// Read-only Node.js replay, independent of the Python checker and search code.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const order = (1n << 252n) + 27742317777372353535851937790883648493n;
const target = order - 2n;
const cases = [
  ['curve25519_scalar_279.json', '3948e3c1692f1d863aa2d7d37246217ed4a2328b5fbec034d8f5f8e6aa6cb0b1', 'e653c99395b406db0461513090024cd0819e5c0a423b237d369f7ebd4ccc0883', 279, 247, 32],
  ['curve25519_scalar_280.json', 'a3a1897b9eeb496cd4b8ac164b653e0c272afd16c8d4e6ad5ca9f402cfe9ca2a', '69576686cf4c14dcd0b811fab610dbb2b764fd3e497ac48e0cfb343be930157f', 280, 249, 31],
];
function requireThat(condition, reason) {
  if (!condition) throw new Error(reason);
}
function power(base, exponent, modulus) {
  let result = 1n;
  let x = base % modulus;
  let k = exponent;
  while (k > 0n) {
    if (k & 1n) result = result * x % modulus;
    x = x * x % modulus;
    k >>= 1n;
  }
  return result;
}
function replay(cert, planHash, wanted) {
  requireThat(cert.source_plan_sha256 === planHash, 'plan binding');
  requireThat(BigInt('0x' + cert.target_hex) === target, 'target exponent');
  requireThat(Array.isArray(cert.operations) && cert.operations.length === cert.operation_count, 'row count');
  const exponents = [1n];
  const parents = [[]];
  let squares = 0, multiplies = 0, accumulating = false, precomputeCount = 0;
  for (const row of cert.operations) {
    requireThat(Object.keys(row).sort().join(',') === 'left,phase,right', 'row shape');
    const {left, right, phase} = row;
    requireThat(Number.isInteger(left) && Number.isInteger(right) && left >= 0 && right >= 0 && left < exponents.length && right < exponents.length, 'parent index');
    requireThat(phase === 'precompute' || phase === 'accumulate', 'phase');
    if (phase === 'accumulate') accumulating = true;
    else { requireThat(!accumulating, 'phase order'); precomputeCount++; }
    exponents.push(exponents[left] + exponents[right]);
    requireThat(exponents.at(-1) > exponents.at(-2), 'nonincreasing chain');
    parents.push([left, right]);
    if (left === right) squares++; else multiplies++;
  }
  requireThat(exponents.at(-1) === target, 'terminal exponent');
  requireThat(JSON.stringify(cert.precompute_values) === JSON.stringify(exponents.slice(0, precomputeCount + 1).map(Number)), 'precompute metadata');
  requireThat(cert.precompute_values.includes(cert.first_window.exponent) && cert.first_window.bits === BigInt(cert.first_window.exponent).toString(2).length, 'first-window metadata');
  requireThat(cert.operation_count === wanted[0] && squares === wanted[1] && multiplies === wanted[2], 'expected cost');
  requireThat(cert.squarings === squares && cert.multiplications === multiplies, 'certificate cost');
  const live = new Set([parents.length - 1]);
  for (let i = parents.length - 1; i >= 1; i--) if (live.has(i)) for (const p of parents[i]) live.add(p);
  requireThat(live.size === parents.length, 'dead operation');
  for (const base of [2n, 3n, 5n, 7n, 11n, order - 1n]) {
    const values = [base % order];
    for (const row of cert.operations) values.push(values[row.left] * values[row.right] % order);
    requireThat(values.at(-1) === power(base, target, order), 'modular replay');
    requireThat(values.at(-1) * base % order === 1n, 'inverse identity');
  }
  return {operations: wanted[0], squarings: squares, other_multiplications: multiplies};
}
const results = [];
for (const [name, expectedSha, planHash, n, s, m] of cases) {
  const raw = fs.readFileSync(path.join(root, name));
  requireThat(crypto.createHash('sha256').update(raw).digest('hex') === expectedSha, 'certificate bytes');
  const cert = JSON.parse(raw.toString('utf8'));
  const result = replay(cert, planHash, [n, s, m]);
  const broken = structuredClone(cert);
  broken.operations.at(-1).left = 0;
  let rejected = false;
  try { replay(broken, planHash, [n, s, m]); } catch { rejected = true; }
  requireThat(rejected, 'corruption not rejected');
  results.push({file: name, sha256: expectedSha, ...result, mutation_rejected: true});
}
process.stdout.write(JSON.stringify({verdict: 'PASS_LOCAL_ARITHMETIC_ONLY', target: 'Curve25519 subgroup scalar l-2', cases: results}) + '\n');
