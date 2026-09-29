# Reviewer guide

This page is the fourth part of the [review packet](README.md). Start with one clean checkout:

```sh
git clone https://github.com/TTaoGaming/addition-chain-search.git
cd addition-chain-search
python -B chains/verify_all.py
```

The chain checker exits nonzero on failure and prints JSON with `"status": "PASS_LOCAL_ARITHMETIC_ONLY"` when the included certificates replay. For a second implementation of the Curve25519 279/280 arithmetic, run `node chains/targets/curve25519/frontier/verify.mjs` if Node.js is installed. Python 3 and its standard library are sufficient for the primary check.

| Question | Evidence location |
| --- | --- |
| What are the exact exponents, schedules, and dated baselines? | [Results and checkers](chains/README.md) |
| How were the selected P-384 milestones reached? | [Episodes](search-history/EPISODES.md) and [island map](search-history/ISLAND_MAP.md) |
| Which procedures can another agent try? | [Five MIT skills](skills/README.md) |
| Which claims remain open? | [Limitations and unknowns](LIMITATIONS_AND_UNKNOWN.md) |

The results-package checker covers the headline P-384 421 and Curve25519 279 certificates. The smaller checker bundled with one agent skill has a narrower schema; use the command above for this packet. The [pinned `ring` P-384 source](https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p384.rs) was statically recounted here; it has not been benchmarked against these candidates.

The guide and reconstructed history are public for inspection without a reuse license. The [skills](skills/REUSE_TERMS.md) and original [chain checker material](chains/LICENSE) carry separate terms.
