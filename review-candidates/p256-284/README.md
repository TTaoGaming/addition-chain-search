# P-256 scalar inversion with 284 operations

This review candidate implements **284 = 251 squarings + 33 other multiplications** in ring's actual P-256 scalar inversion function. It replaces the pinned **289 = 254S + 35M** chain, saving three squarings and two multiplications while retaining ring's arithmetic backend and API.

The chain and patch have passed exact replay and native correctness tests. One shared-host benchmark showed **1.27% lower paired median inversion latency**; end-to-end ECDSA signing was **inconclusive**. This is a review candidate, not a global-record, constant-time-proof or production-readiness claim.

## Review in three steps

1. **Check the result:** [certificate](adapter/candidate.json), [production-only ring patch](adapter/ring_p256_284.patch), and [short reproduction guide](REPRODUCE.md)
2. **Inspect the evidence:** [native tests and paired measurements](TECHNICAL_REPORT.md), [raw timings](receipts/benchmark_summary.json), and [public comparisons](PUBLIC_COMPARISON.md)
3. **Understand the search:** [milestones, explored regions and next questions](SEARCH_HISTORY.md), with two independently replayable alternative 285-operation certificates

From the repository root, Python 3.8+ with no third-party packages:

```sh
python3 -B review-candidates/p256-284/verify.py
```

Expected final line: `PASS_P256_REVIEW`. This checks file hashes, the exact target and charged operations, 1,034 modular bases, both alternative certificates, nine generator tests, and byte-for-byte patch generation. Native reproduction needs Rust, a C toolchain, Perl and the pinned ring checkout; see [REPRODUCE.md](REPRODUCE.md).

## Exact scope

- Target: the P-256 subgroup **scalar order n−2**, not the field prime or a square-root exponent
- Certificate SHA-256: `46ba0fb4a02926e02aad7c51cb9c41225952a5549e4c0012964f2de5ad15d148`
- ring base: `840167e18e4fa837eb48de46500454a616a15a6e`
- Native checks: 7 ECDSA integration tests, 14 focused P-256 tests, 1,792 direct oracle vectors, and 95 full-library tests passed
- Source review dated September 30, 2026; the exact candidate is unchanged from the measured run

Prepared as part of Tommy Tai's AI-assisted addition-chain research. The search history distinguishes reconstructed reports from certificates that can be checked here. New materials are review-only under the existing repository policy; included ring source retains its upstream notices. See [source and rights](SOURCE_NOTICE.md). The earlier [291 certificate](../../chains/targets/p256/candidate.json) and other targets remain unchanged.
