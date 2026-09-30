#!/usr/bin/env python3
"""Offline interpreter checks for emitted *Rust text*, not native Rust tests."""
import collections
import hashlib
import json
import re
import unittest
from pathlib import Path
import generate_ring as gen
import check_chain_independent as check

HERE = Path(__file__).parent


def body(source):
    start = source.index('    let _1 = &a;', source.index('fn p256_scalar_inv_to_mont('))
    return source[start:source.index('\n}', start)]


def interpret(rust, base, modulus=None):
    registers = {'a': base}
    squares = muls = 0
    for raw in rust.splitlines():
        line = raw.split('//', 1)[0].strip()
        if not line:
            continue
        if line == 'acc':
            return registers['acc'], squares, muls
        if line == 'let _1 = &a;':
            registers['_1'] = registers['a']
            continue
        m = re.fullmatch(r'let (?:mut )?(\w+) = (sqr|mul|sqr_mul)\((.*?)\);', line)
        a = re.fullmatch(r'sqr_mul_acc\(&mut acc, (.*?), &?(\w+), cpu\);', line)
        if m:
            dest, op, args = m.groups()
            args = [v.strip() for v in args.split(',')]
            assert args[-1] == 'cpu'
            left = registers[args[0].lstrip('&')]
            if op == 'sqr':
                k, right = 1, None
            elif op == 'mul':
                k, right = 0, registers[args[1].lstrip('&')]
            else:
                k = sum(int(x.strip()) for x in args[1].split('+'))
                right = registers[args[2].lstrip('&')]
        elif a:
            dest, op, left = 'acc', 'sqr_mul', registers['acc']
            k = sum(int(x.strip()) for x in a[1].split('+'))
            right = registers[a[2]]
        else:
            raise ValueError(f'unrecognized emitted Rust statement: {line}')
        squares += k
        muls += op != 'sqr'
        if modulus is None:
            value = left << k
            if right is not None:
                value += right
        else:
            value = pow(left, 1 << k, modulus)
            if right is not None:
                value = value * right % modulus
        registers[dest] = value
    raise ValueError('no final acc')


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = check.parse((HERE / 'candidate.json').read_bytes())
        cls.source = (HERE.parent / 'upstream_p256.rs').read_text()
        cls.generated = gen.emit(gen.plan(cls.cert['rows']))

    def test_exact_exponent_and_counts_from_rust_text(self):
        self.assertEqual(interpret(self.generated, 1), (check.TARGET, 251, 33))

    def test_baseline_recount(self):
        self.assertEqual(interpret(body(self.source), 1), (check.TARGET, 254, 35))

    def test_generated_modular_execution(self):
        bases = [0, 1, 2, 3, check.N - 1, check.N // 2]
        bases += [int.from_bytes(hashlib.sha256(f'ring-adapter-v1/{i}'.encode()).digest(), 'big') % check.N for i in range(128)]
        for x in bases:
            actual, s, m = interpret(self.generated, x, check.N)
            self.assertEqual((s, m), (251, 33))
            self.assertEqual(actual, pow(x, check.TARGET, check.N))
            self.assertEqual(actual, interpret(body(self.source), x, check.N)[0])

    def test_only_chain_body_changes(self):
        patched = gen.replace(self.source, self.generated)
        head = self.source[:self.source.index('    let _1 = &a;', self.source.index('fn p256_scalar_inv_to_mont('))]
        self.assertTrue(patched.startswith(head))
        self.assertEqual(patched[patched.index('\nprefixed_extern! {', len(head)):], self.source[self.source.index('\nprefixed_extern! {', len(head)):])

    def test_source_pin_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'upstream blob mismatch'):
            gen.replace(self.source + '\n', self.generated)

    def test_certificate_pin_fails_closed(self):
        with self.assertRaises(check.Rejected):
            check.digest_check((HERE / 'candidate.json').read_bytes() + b'\n', gen.CERT_SHA256)

    def test_late_helper_retained(self):
        self.assertIn('let c136 = mul(&c11, &c16, cpu);', self.generated)
        self.assertEqual(self.generated.count('&c136, cpu'), 2)

    def test_reproducible(self):
        self.assertEqual(self.generated, (HERE / 'generated_body.rs').read_text())

    def test_generated_mutation_detected(self):
        mutant = self.generated.replace('acc, 10, &c136', 'acc, 11, &c136', 1)
        self.assertNotEqual(interpret(mutant, 1)[0], check.TARGET)


if __name__ == '__main__':
    unittest.main(verbosity=2)
