# Reproduce the P-256 review candidate

From the repository root, first run `cd review-candidates/p256-284`. All commands below assume this directory.

## 1. Replay the certificate offline

Python 3.8+; standard library only. From this directory:

```sh
python3 adapter/check_chain_independent.py adapter/candidate.json \
  --sha256 46ba0fb4a02926e02aad7c51cb9c41225952a5549e4c0012964f2de5ad15d148 --modular
python3 adapter/test_adapter.py
```

Expected: `PASS_SCOPED`, 284 operations, 251 squarings and 33 multiplications; then 9 passing generator tests. The checker validates the exact integer exponent, earlier declared parents and full liveness. Row 136 is a legitimate numerical descent: 8415 = 255 + 8160. File order is a dependency order, not a required increasing sequence.

## 2. Build and test the actual ring patch

Use Rust 1.85 or newer, a C toolchain and Perl. The recorded run used Rust 1.98.1 and GCC 14.2.0 on x86_64. Dependency versions are pinned by upstream Cargo.lock.

```sh
git clone https://github.com/briansmith/ring.git ring
git -C ring checkout --detach 840167e18e4fa837eb48de46500454a616a15a6e
git -C ring apply --check ../adapter/ring_p256_284.patch
git -C ring apply ../adapter/ring_p256_284.patch
python3 adapter/add_native_checks.py
cargo test --locked --release -p ring --manifest-path ring/Cargo.toml --test ecdsa_tests
cargo test --locked --release -p ring --manifest-path ring/Cargo.toml --lib
```

`native-tests/` contains the exact oracle fixture and test source used in the recorded run. `add_native_checks.py` recreates them, adds a test-only module, and leaves the production API unchanged. Expected fixture SHA-256: `f36fb66a02f11b979cef9b3bc7b42b0bb5d1937f6a7b6eebd9c50a146d6b993f`.

The oracle uses Python modular inversion, explicit Montgomery encoding and native inverse-product checks. Zero follows ring's existing zero-result convention. The included baseline function comes from the pinned upstream source.

## 3. Check the patch derivation

```sh
python3 adapter/generate_ring.py
```

It requires the exact source blob and certificate, then reproduces the included patch and replacement source. Only single-consumer square runs are fused into existing helpers. The final linear suffix uses the existing accumulator helper. Arithmetic counts are unchanged by code generation.

## 4. Review or repeat the measurements

`receipts/benchmark_summary.json` and the two CSV files contain the results. The complete commands, warmups, alternating order, repeats and caveats are in `TECHNICAL_REPORT.md` and `adapter/BENCHMARK_PLAN.md`.

The inversion benchmark compares both functions in one native binary. Signing compares separately built baseline/candidate ring binaries with the same test key and message. Keep those results separate. Hashes detect file changes; they are not a digital signature or a claim of trusted execution.
