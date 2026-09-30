#!/usr/bin/env python3
"""Add test-only independent-oracle vectors and saved baseline to local ring tree."""
import hashlib
from pathlib import Path
import check_chain_independent as check

ROOT = Path(__file__).resolve().parent.parent
P256 = ROOT / 'ring/src/ec/suite_b/ops/p256.rs'
source = (ROOT / 'upstream_p256.rs').read_text()
start = source.index('fn p256_scalar_inv_to_mont(')
end = source.index('\n}\n', source.index('    let _1 = &a;', start)) + 3
baseline = source[start:end].replace('fn p256_scalar_inv_to_mont(', 'fn baseline_scalar_inv_to_mont(', 1)
module = '''// Local validation only. Not part of the production patch.
use super::*;

''' + baseline + '''
fn scalar(hex: &str) -> Scalar<Unencoded> {
    Scalar::from(&PublicScalar::<Unencoded>::from_hex(hex))
}

fn montgomery(hex: &str) -> Scalar<R> {
    Scalar::from(&PublicScalar::<R>::from_hex(hex))
}

#[test]
fn p256_chain284_independent_oracle() {
    let cpu = cpu::features();
    let mut count = 0;
    for line in include_str!("p256_chain284_vectors.txt").lines() {
        let mut fields = line.split_whitespace();
        let plain = scalar(fields.next().unwrap());
        let input = montgomery(fields.next().unwrap());
        let expected = montgomery(fields.next().unwrap());
        assert!(fields.next().is_none());
        let candidate = p256_scalar_inv_to_mont(input, cpu);
        let baseline = baseline_scalar_inv_to_mont(input, cpu);
        assert_eq!(candidate.limbs, expected.limbs, "candidate vector {count}");
        assert_eq!(baseline.limbs, expected.limbs, "baseline vector {count}");
        let product = SCALAR_OPS.scalar_product(&plain, &candidate, cpu);
        let product_expected = if count == 0 { Scalar::zero() } else { Scalar::one() };
        assert_eq!(product.limbs, product_expected.limbs, "inverse product {count}");
        count += 1;
    }
    assert_eq!(count, 1792);
}
'''
# Cover zero, endpoints, powers of two, neighbors, and deterministic full-width inputs.
bases = [0, 1, 2, 3, check.N-1, check.N-2, check.N//2]
for k in range(1, 256):
    for x in ((1 << k)-1, 1 << k, (1 << k)+1):
        if x < check.N:
            bases.append(x)
bases.extend(1 + int.from_bytes(hashlib.sha256(f'ring-native-oracle-v1/{i}'.encode()).digest(), 'big') % (check.N-1) for i in range(1024))
bases = list(dict.fromkeys(bases))
module = module.replace('assert_eq!(count, 1792);', f'assert_eq!(count, {len(bases)});')
R = pow(2, 256, check.N)
lines = []
for x in bases:
    inverse = pow(x, -1, check.N) if x else 0
    assert x == 0 or inverse * x % check.N == 1
    lines.append(f'{x:064x} {x * R % check.N:064x} {inverse * R % check.N:064x}')
fixture = '\n'.join(lines) + '\n'
module += (ROOT / 'adapter/native_benchmark.rs').read_text()
(P256.parent/'p256_chain284_tests.rs').write_text(module)
(P256.parent/'p256_chain284_vectors.txt').write_text(fixture)
current = P256.read_text()
marker = '\n#[cfg(test)]\n#[path = "p256_chain284_tests.rs"]\nmod chain284_validation;\n'
if marker not in current:
    P256.write_text(current + marker)
print(f'{len(bases)} independent oracle vectors; fixture sha256={hashlib.sha256(fixture.encode()).hexdigest()}')
