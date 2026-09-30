# P-256 scalar inversion: a tested ring candidate

## Result

The existing 284-operation certificate is now implemented in the actual ring P-256 subgroup scalar n−2 inversion function. The production patch changes only the straight-line chain body. Existing Montgomery helpers, domain conversion, ABI and dispatch are retained. This is a local review candidate.

Pinned baseline: briansmith/ring commit `840167e18e4fa837eb48de46500454a616a15a6e`, `src/ec/suite_b/ops/p256.rs` blob `edd3548309824ea8f685480d660f5d7591184a1d`.

[Exact upstream source](https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p256.rs)

- Baseline: 289 = 254 squarings + 35 other multiplications
- Candidate: 284 = 251 squarings + 33 other multiplications
- The generator fuses single-consumer square runs into 40 existing-helper calls and uses ring's accumulator helper for the linear suffix
- Exact candidate SHA-256: `46ba0fb4a02926e02aad7c51cb9c41225952a5549e4c0012964f2de5ad15d148`
- Target: P-256 subgroup order n−2, not the field exponent or the separate field inverse-squared function

## Observed performance

One x86_64 shared-cloud-host run: AMD EPYC 9V74, process affinity CPU 0, Rust 1.98.1, GCC 14.2.0, and ring's release profile. No frequency/turbo isolation.

Scalar inversion: 41 paired batches of 16,384 inversions, four warmup batches per implementation, 64 precomputed full-width nonzero inputs, alternating execution order. Median paired candidate/baseline latency ratio: 0.98734, or 1.27% lower latency. Sample-bootstrap median-ratio interval: 0.98091–0.99553. Candidate was faster in 30/41 pairs. Individual-pair p10–p90 ratio: 0.94532–1.03587.

End-to-end ECDSA P-256 signing: 31 paired batches of 2,000 signatures, 1,000 warmups per child process, identical fixed key/message and RNG API, alternating order. Median paired ratio: 1.00759, or 0.76% higher latency. Sample-bootstrap interval: 0.98258–1.02496. This result is inconclusive; no signing speedup is established.

Separate implementation medians were 5,817 ns vs 5,757 ns per inversion and 18,243 ns vs 18,311 ns per signature. The median of paired ratios differs from the ratio of these medians; the paired statistic is the comparison.

All observations, including outliers, are retained. The analysis uses 20,000 deterministic bootstrap resamples of paired ratios. Its intervals summarize these samples only. Shared-host scheduling, temporal dependence, code placement and execution order remain caveats. No application-throughput, energy, cross-platform or side-channel claim follows.

## Tests actually run

- Unchanged native baseline: 7/7 ECDSA integration tests
- Patched native ring: 7/7 ECDSA integration tests and 14/14 focused P-256 unit tests
- 1,792 native oracle vectors: zero, endpoints, all powers-of-two and neighbors, and 1,024 deterministic full-width scalars. Python `pow(x, -1, n)` supplies expected inverses with explicit Montgomery encoding. Both native baseline and candidate match, and native inverse-product checks pass
- Full patched library: 95 passed, 0 failed, 1 ignored timing benchmark. The timing benchmark subsequently ran explicitly and passed
- 9 offline generator tests: exact replay of emitted Rust text, 134 modular bases compared with Python and baseline, source/certificate pin failures, and a generated-code mutation control

Zero preserves ring's return-zero convention. Offline Python checks are not counted as native tests.

## Reproduce from source

First `cd review-candidates/p256-284` from the repository root.

Requires Python 3.8+, Rust meeting ring's MSRV 1.85, C compiler, Perl, Git and network access for official dependencies. This bundle installs nothing automatically. From the extracted directory:

```sh
git clone https://github.com/briansmith/ring.git ring
git -C ring checkout --detach 840167e18e4fa837eb48de46500454a616a15a6e
python3 adapter/generate_ring.py
python3 adapter/test_adapter.py
git -C ring apply ../adapter/ring_p256_284.patch
python3 adapter/add_native_checks.py
cargo test --locked --release -p ring --manifest-path ring/Cargo.toml --test ecdsa_tests
cargo test --locked --release -p ring --manifest-path ring/Cargo.toml --lib
```

The generator pins the bundled upstream source and certificate, rejecting hash drift. The production-only patch can be reviewed separately from the test harness. Test/benchmark support is under `cfg(test)` and adds no production exports.

Microbenchmark, choosing an allowed CPU number:

```sh
taskset -c 0 cargo test --locked --release -p ring --manifest-path ring/Cargo.toml --lib p256_chain284_paired_microbenchmark -- --ignored --nocapture --test-threads=1
```

End-to-end comparison:

```sh
git -C ring worktree add --detach ../ring_baseline 840167e18e4fa837eb48de46500454a616a15a6e
mkdir -p ring/examples ring_baseline/examples
cp adapter/chain284_sign_bench.rs ring/examples/
cp adapter/chain284_sign_bench.rs ring_baseline/examples/
cargo build --locked --release -p ring --manifest-path ring/Cargo.toml --example chain284_sign_bench
cargo build --locked --release -p ring --manifest-path ring_baseline/Cargo.toml --example chain284_sign_bench
taskset -c 0 python3 adapter/run_paired_sign.py ring_baseline/target/release/examples/chain284_sign_bench ring/target/release/examples/chain284_sign_bench
```

Save new stdout separately from the preserved run. `adapter/analyze_benchmarks.py` reproduces the exact analysis from the retained raw files. Executable hashes are recorded in `receipts/benchmark_binaries.json`; executable snapshots are not distributed here. Rebuild from the included source.

## Limited source inspection

The generated production body introduces no conditional branches, loops, table indices or secret-dependent selection. Operand references and squaring counts are fixed by the public certificate. Existing helpers, representation and backend calls are byte-preserved. This is a limited source inspection, not a constant-time proof, compiler/assembly audit or inherited-backend review.

No global optimality, new algorithmic technique, maintainers' acceptance, other-architecture result or production suitability is established. Upstream ring licensing applies; the copied source notice is included in `LICENSE-ring-source.txt`. This directory is published for technical review. No new reuse license is granted; upstream terms for copied ring code remain intact. See SOURCE_NOTICE.md.

## Contents

- `adapter/ring_p256_284.patch`: production-only patch
- `adapter/generate_ring.py`: pinned code generator
- `adapter/candidate.json`: unchanged existing certificate
- `adapter/add_native_checks.py`: recreate native oracle tests and saved baseline
- `adapter/native_benchmark.rs`, `adapter/chain284_sign_bench.rs`, `adapter/run_paired_sign.py`: benchmark harnesses
- `receipts/`: raw logs, observations, host/binary metadata
- Measured executable snapshots are omitted from this compact source-only packet

Native test logs and raw timing data are included. Build-directory prefixes in selected logs were replaced with `<BUILD_ROOT>` for publication; test names, outcomes and timings are unchanged. See `PUBLICATION_NOTES.md`.
