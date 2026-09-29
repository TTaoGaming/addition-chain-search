# What worked, failed, and remains unknown

This is selected research evidence, not an exhaustive experiment log. The
separate `01_addition_chains_r4.zip` (SHA-256
`e850af310dc732eba5329692987e6ce43fcc15e8186c1c691cf47f9c1fd0ac4e`)
has the exact certificates, verifiers, dated history, and source citations.

| Observation | Status | Lesson for an agent |
| --- | --- | --- |
| P-384 scalar `n−2` certificates progressed 425 → 424 → 423 → 422 → 421 operations; the frozen 421 arithmetic replay and mutation controls pass | Verified locally | Preserve each exact certificate and verifier. The private CPU annealing source and selected seed-101 genotype were recovered; the full six-seed raw trajectory is not in this packet. Output replay is not full discovery reproduction. |
| Six-seed P-384 CPU anneal: two seeds reached 421, four best at 422; 210 distinct judge-valid 421 certificates and no ≤420 were reported | Private Slack aggregate, not raw-log replay in this packet | State configured iterations and actual evaluations separately. A bounded negative is not a shortest-chain proof. |
| A later agent rebuilt a searcher because the earlier private engine was unreachable | Private STRIFE checkpoint | Require an engine locator and cite-or-gap on intake. If access fails, record `SOURCE_UNAVAILABLE`, not “no prior engine.” A skill must be tested by a later carrier before claiming system-level learning. |
| Curve25519 prime-subgroup `l−2` has locally replayed 279 = 247S+32M and 280 = 249S+31M schedules | Verified locally | Keep both Pareto points; a lower operation count does not alone settle weighted hardware cost. Do not confuse the scalar subgroup with the field-prime `p−2` target. |
| P-256 scalar 291 is valid, but a pinned `ring` source recount is 289 | Verified local arithmetic and dated source comparison | A valid new candidate can be worse than an existing implementation. Negative comparisons belong in the report. |
| secp256k1 scalar 290 ties the historical published count | Verified local arithmetic | Credit the prior Wuille → Dettman → Brian Smith lineage; do not claim novelty for a tie. |
| A five-candidate fixed-grammar checker pilot passed correctness and held-out cases, but selected different winners on local reruns; subsequent whole-process speed confirmation did not pass | Local pilot, speed gain held | A small scripted sweep is not a named evolutionary-engine run. In-process timing is not end-to-end throughput. |
| Native cryptographic speedup, shortest-chain proof, and adoption into a library | Unknown / not established by this packet | Require native measurements, an appropriate optimality proof, and downstream acceptance respectively. |

The public comparison source is [Brian Smith's 2017 addition-chain
article](https://briansmith.org/ecc-inversion-addition-chains-01). Its
secp256k1 scalar section describes the earlier Wuille and Dettman work and
Smith's subsequent four-bit-window 290 construction. The chain package's
`THIRD_PARTY.md` records other provenance and licensing boundaries.
