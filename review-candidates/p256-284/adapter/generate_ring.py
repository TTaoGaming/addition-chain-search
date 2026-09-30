#!/usr/bin/env python3
"""Pinned P-256 scalar certificate -> actual ring function-body patch.

No search; no invented arithmetic backend. Preserve ring's helpers and ABI.
Only fuse single-consumer square runs into ring's existing sqr_mul helpers.
"""
import argparse
import collections
import difflib
import hashlib
import json
from pathlib import Path

import check_chain_independent as check

CERT_SHA256 = '46ba0fb4a02926e02aad7c51cb9c41225952a5549e4c0012964f2de5ad15d148'
RING_COMMIT = '840167e18e4fa837eb48de46500454a616a15a6e'
RING_BLOB = 'edd3548309824ea8f685480d660f5d7591184a1d'
PATH = 'src/ec/suite_b/ops/p256.rs'


def plan(rows):
    parents = {out: (left, right, i) for i, (out, left, right) in enumerate(rows)}
    users = collections.defaultdict(set)
    for i, (_, left, right) in enumerate(rows):
        users[left].add(i)
        users[right].add(i)
    absorbed, fused = set(), {}
    for i, (out, left, right) in enumerate(rows):
        if left == right:
            continue
        alternatives = []
        for first, second in ((left, right), (right, left)):
            node, consumer, removed = first, i, []
            while node in parents:
                a, b, producer = parents[node]
                if a != b or users[node] != {consumer}:
                    break
                removed.append(producer)
                node, consumer = a, producer
            alternatives.append((len(removed), node, second, removed))
        count, base, other, removed = max(alternatives, key=lambda x: x[0])
        if count:
            fused[i] = (base, other, count)
            absorbed.update(removed)
    result = []
    for i, (out, left, right) in enumerate(rows):
        if i in absorbed:
            continue
        if i in fused:
            left, right, count = fused[i]
            kind = 'sqr_mul'
        else:
            kind, count = ('sqr', 1) if left == right else ('mul', 0)
        result.append(dict(index=i + 1, out=out, left=left, right=right, squares=count, kind=kind))
    # Exact replay of emitted primitive semantics, separate from the input validator.
    values, squares, multiplies = {1: 1}, 0, 0
    for p in result:
        if p['kind'] == 'sqr':
            out = 2 * values[p['left']]
        elif p['kind'] == 'mul':
            out = values[p['left']] + values[p['right']]
        else:
            out = (values[p['left']] << p['squares']) + values[p['right']]
        if out != p['out']:
            raise ValueError('emission-plan exponent mismatch')
        values[out] = out
        squares += p['squares']
        multiplies += p['kind'] != 'sqr'
    if (squares, multiplies, result[-1]['out']) != (251, 33, check.TARGET):
        raise ValueError('emission-plan target/count mismatch')
    return result


def emit(ops):
    names = {1: 'a', **{p['out']: f"c{p['index']}" for p in ops}}
    tail = len(ops) - 1
    while tail > 0:
        prev, op = ops[tail - 1], ops[tail]
        # Only the linear suffix is accumulated; the rhs must survive separately.
        if op['left'] != prev['out'] or op['right'] == prev['out']:
            break
        if any(q['right'] == prev['out'] for q in ops[tail + 1:]):
            break
        tail -= 1
    lines = [f'    // Generated from certificate SHA-256 {CERT_SHA256}.',
             '    // Exact scalar exponent n-2: 284 = 251 squarings + 33 multiplications.',
             '    // Public, fixed schedule; existing ring Montgomery helpers unchanged.']
    for j, p in enumerate(ops):
        left, right = names[p['left']], names[p['right']]
        if j > tail:
            if p['kind'] == 'sqr_mul':
                code = f"sqr_mul_acc(&mut acc, {p['squares']}, &{right}, cpu);"
            elif p['kind'] == 'mul':
                code = f'acc = mul(&acc, &{right}, cpu);'
            else:
                code = 'acc = sqr(&acc, cpu);'
        else:
            kind = p['kind']
            args = f'&{left}, cpu' if kind == 'sqr' else (
                f'&{left}, &{right}, cpu' if kind == 'mul' else f"&{left}, {p['squares']}, &{right}, cpu")
            dest = 'mut acc' if j == tail else names[p['out']]
            code = f'let {dest} = {kind}({args});'
        lines.append(f"    {code} // certificate row {p['index']}")
    return '\n'.join(lines) + '\n\n    acc\n'


def replace(source, generated):
    encoded = source.encode()
    blob = hashlib.sha1(f'blob {len(encoded)}\0'.encode() + encoded).hexdigest()
    if blob != RING_BLOB:
        raise ValueError(f'upstream blob mismatch: expected {RING_BLOB}, got {blob}')
    fn = source.index('fn p256_scalar_inv_to_mont(')
    start = source.index('    let _1 = &a;', fn)
    end = source.index('\n}\n', start)
    return source[:start] + generated + source[end:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).parent.parent / 'upstream_p256.rs')
    parser.add_argument('--certificate', type=Path, default=Path(__file__).with_name('candidate.json'))
    parser.add_argument('--out', type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    raw = args.certificate.read_bytes()
    check.digest_check(raw, CERT_SHA256)
    obj = check.parse(raw)
    certificate = check.verify(obj)
    ops = plan(obj['rows'])
    source = args.source.read_text()
    generated = emit(ops)
    patched = replace(source, generated)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'p256_candidate.rs').write_text(patched)
    (args.out / 'generated_body.rs').write_text(generated)
    (args.out / 'ring_p256_284.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True), patched.splitlines(True), 'a/' + PATH, 'b/' + PATH)))
    (args.out / 'emission_plan.json').write_text(json.dumps(ops, indent=2) + '\n')
    result = {'ring_commit': RING_COMMIT, 'ring_source_blob': RING_BLOB,
              'certificate_sha256': CERT_SHA256, 'certificate': certificate,
              'emitted_calls': len(ops), 'fused_square_rows': len(obj['rows']) - len(ops),
              'generated_source_sha256': hashlib.sha256(patched.encode()).hexdigest()}
    (args.out / 'generation_result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
