# Reviewer guide

This is the short verification path for the [project](README.md). Start with one clean checkout:

```sh
git clone https://github.com/TTaoGaming/addition-chain-search.git
cd addition-chain-search
python -B chains/verify_all.py
python -B review-candidates/verify.py
```

The frozen chain checker exits nonzero on failure and prints JSON with `"status": "PASS_LOCAL_ARITHMETIC_ONLY"` when its included certificates replay. The separate review-candidate checker ends with `PASS_LOCAL_ARITHMETIC_ONLY` after replaying the three new certificates and rejecting mutations. For a second implementation of the Curve25519 279/280 arithmetic, run `node chains/targets/curve25519/frontier/verify.mjs` if Node.js is installed. Python 3 and its standard library are sufficient for the two primary checks.

| Question | Evidence location |
| --- | --- |
| What are the exact exponents, schedules, and dated baselines? | [Results and checkers](chains/README.md) |
| What are the newer P-521 and secp256k1 arithmetic leads? | [Review-only candidates](review-candidates/README.md) and their separate checker |
| How did the search proceed and where were resources spent? | [Dated episodes](search-history/EPISODES.md), [island and resource map](search-history/ISLAND_MAP.md), and [bounded methods](search-history/METHODS_AND_LIMITS.md) |
| Which procedures can another agent try? | [Five MIT skills](skills/README.md) |
| Which claims remain open? | [Limitations and unknowns](LIMITATIONS_AND_UNKNOWN.md) |

The results-package checker covers the headline P-384 421 and Curve25519 279 certificates. The smaller checker bundled with one agent skill has a narrower schema; use the command above for this packet. The [pinned `ring` P-384 source](https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p384.rs) was statically recounted here; it has not been benchmarked against these candidates.

The guide and reconstructed history are public for inspection without a reuse license. The [skills](skills/REUSE_TERMS.md) and original [chain checker material](chains/LICENSE) carry separate terms. The [new review-candidate materials](review-candidates/SOURCE_NOTICE.md) have no reuse license; they are outside `chains/` and its frozen ZIP.
