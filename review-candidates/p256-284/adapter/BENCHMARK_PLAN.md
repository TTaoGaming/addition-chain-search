# Paired native benchmark plan

Do not infer speed from operation counts. Both implementations use the same pinned ring commit, optimized Rust1.98.1/GCC14.2.0 toolchain, x86_64 host and inputs.

## Scalar inversion microbenchmark

Test-only module contains the unchanged baseline and the candidate side-by-side in one release binary. Measure actual ring Montgomery backend calls, input/output behind std::hint::black_box and function pointer behind black_box. Precompute64 nonzero full-width Montgomery inputs outside timing. Warm each implementation for four16,384-operation batches. Then record41 paired16,384-operation batches, alternating baseline-first and candidate-first. Run one test thread and pin process affinity to one available CPU if supported. The file reports raw nanoseconds per batch and iterations; analyse paired candidate/baseline ratios, spread and uncertainty. This measures inversion alone, excluding conversion into Montgomery form, signing, and Python.

## End-to-end ECDSA P-256 signing

Identical local example compiled separately against unchanged baseline and patched ring. Fixed test key and32-byte message. Same SystemRandom source used in both implementations. Each process constructs key and warms1,000 signatures outside timed interval; then times2,000 signatures.31 paired processes alternate baseline/candidate order. Driver and child affinity inherited from one available CPU. Keep signing results distinct from inversion-only results. Runtime randomness, shared-host scheduling, frequency changes, and code layout remain potential noise/confounders; no cross-platform conclusion.

## Reporting

Save raw observations, executable/source hashes, versions, commit, CPU identity/affinity, timestamp, and analysis. Report regressions or inconclusive results as such. No claim of production readiness, side-channel proof, global optimality, external approval or throughput on other architectures. Full tests run separately and are not benchmark samples.
