# Reviewer guide: check the result, then the search account

This is the fourth part of the [four-part project](README.md), observed
2026-09-29 17:03 UTC. It gives an independent reader a short route through
the evidence. No endorsement from Brian Smith is claimed.

## First check: exact arithmetic

With Python 3 and Git, from a fresh checkout:

```sh
git clone https://github.com/TTaoGaming/addition-chain-search.git
cd addition-chain-search
python -B chains/verify_all.py
```

The command should exit 0 and print JSON with
`"status": "PASS_LOCAL_ARITHMETIC_ONLY"`. It checks the bundled file hashes,
target exponents, parent sums, operation counts, live dependencies, modular
replay, and negative controls. In particular, the frozen P-384 scalar
`n - 2` certificate is 421 = 380S + 41M; the Curve25519 subgroup scalar
`l - 2` candidate is 279 = 247S + 32M. The optional
[Node.js replay](chains/targets/curve25519/frontier/README.md) checks the
279/280 pair in a second implementation. A reader can also use the
[results ZIP](01_addition_chains_r4.zip) without cloning.

| Question | What this release establishes | Where to look |
| --- | --- | --- |
| Do the included schedules reach the exact target in the stated operations? | **Local arithmetic replay passes**; the checkers and certificates are included. | [Results and checkers](chains/README.md) |
| Are the counts below relevant published examples? | P-384 421 is below the [2017 P-384 scalar 433](https://briansmith.org/ecc-inversion-addition-chains-01); Curve25519 scalar 279 is below the [dated `addchain` 283](https://github.com/mmcloughlin/addchain/commit/b52645e520ab79ae83c2dcff2a9e90f59359e6a6). These are **dated comparisons**, not a current-best survey. | [Exact-target comparison table](chains/README.md) |
| Can the historical discovery be replayed from this release? | **Partly.** Selected certificates, checkpoints, and bounded negative regions survive; full six-seed CPU logs and equal-budget island comparisons do not. | [Episodes](search-history/EPISODES.md) and [island/resource map](search-history/ISLAND_MAP.md) |
| Do the skills transfer between agents or model families? | **Not measured.** Five MIT skills encode procedures; loading them and improving held-out behavior are separate tests. | [Skills](skills/README.md) |
| Did an evolutionary engine improve the frozen P-384 421? | The later, bounded [OpenEvolve case](openevolve-case/README.md) used a different 421 seed and produced no improvement. Its ledger replays, with one missing trace row and no raw model responses here. | [Case and limits](openevolve-case/RESULTS.md) |

The [pinned `ring` P-384 source](https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p384.rs)
has a separately recorded static recount of 430 operations in this packet.
That is a source-count comparison, not a runtime benchmark.

The small checker bundled with the agent skills does not parse the headline
P-384 421 or Curve25519 279/280 schedules; use the **results-package command
above** for those claims. Installing a skill is not evidence that an agent
used it.

## What remains open

The release does **not** show a native speedup, constant-time behavior,
shortest-chain optimality, a current global champion, library adoption, or
a learned transferable search policy. The next discriminating checks are a
pinned-source current-frontier census for each *same exact target*, a native
benchmark under fixed build/hardware conditions, and held-out skill tests
with and without each procedure. A new search should retain raw run logs,
start/end UTC, CPU and model use, cost, and operator touches; the historical
gaps in the [island map](search-history/ISLAND_MAP.md) cannot be filled by
guessing. See [limits and unknowns](LIMITATIONS_AND_UNKNOWN.md) and the
[release hashes](PUBLIC_SHA256SUMS.txt).

This guide is public for inspection; no reuse license for its prose is
granted. The [five agent skills](skills/README.md) and original checker code
have separate license terms.
