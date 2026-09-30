# Reviewer guide

This is the short verification path for the [project](README.md). Start with one clean checkout:

```sh
git clone https://github.com/TTaoGaming/addition-chain-search.git
cd addition-chain-search
python -B chains/verify_all.py
python -B review-candidates/verify.py
python3 -B review-candidates/p256-284/verify.py
```

The frozen chain checker exits nonzero on failure and prints JSON with `"status": "PASS_LOCAL_ARITHMETIC_ONLY"` when its included certificates replay. The separate review-candidate checker ends with `PASS_LOCAL_ARITHMETIC_ONLY` after replaying its three P-521/secp256k1 certificates and rejecting mutations. For a second implementation of the Curve25519 279/280 arithmetic, run `node chains/targets/curve25519/frontier/verify.mjs` if Node.js is installed. Python 3.8+ and its standard library are sufficient for all three offline checks. The P-256 review checker ends with `PASS_P256_REVIEW`; it also verifies patch generation. For native ring tests, use the [P-256 reproduction guide](review-candidates/p256-284/REPRODUCE.md).

| Question | Evidence location |
| --- | --- |
| What are the exact exponents, schedules, and dated baselines? | [Results and checkers](chains/README.md) |
| What is the tested P-256 scalar result? | [284-operation ring review](review-candidates/p256-284/README.md), with native test and benchmark evidence |
| What are the newer P-521 and secp256k1 arithmetic leads? | [Review-only candidates](review-candidates/README.md) and their separate checker |
| How did the search proceed and where were resources spent? | [Dated episodes](search-history/EPISODES.md), [island and resource map](search-history/ISLAND_MAP.md), and [bounded methods](search-history/METHODS_AND_LIMITS.md) |
| Which procedures can another agent try? | [Five MIT skills](skills/README.md) |
| Which claims remain open? | [Limitations and unknowns](LIMITATIONS_AND_UNKNOWN.md) |

The results-package checker covers the headline P-384 421 and Curve25519 279 certificates. The smaller checker bundled with one agent skill has a narrower schema; use the command above for this packet. The [pinned `ring` P-384 source](https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p384.rs) was statically recounted here; it has not been benchmarked against these candidates.

The guide and reconstructed history are public for inspection without a reuse license. The [skills](skills/REUSE_TERMS.md) and original [chain checker material](chains/LICENSE) carry separate terms. The [new review-candidate materials](review-candidates/SOURCE_NOTICE.md) grant no new project reuse license; copied ring source retains its upstream notices. They are outside `chains/` and its frozen ZIP.
