# Search islands, coverage, and resource ledger

Snapshot observed 2026-09-29 16:41 UTC. This map is a reconstruction from
selected receipts. Each row names a **region of a search**, not an exhaustive
region of all possible addition chains. Times are UTC. `S` is a squaring and
`M` is another multiplication. Different scalar targets are separate problems;
the Curve448 field assay is separate again. The [exact candidate checks](../chains/README.md)
and [search episodes](EPISODES.md) give the detailed evidence boundaries.

## Candidate frontier in this public snapshot

| Exact target | Locally replayed candidate | Dated comparison | Claim ceiling |
| --- | --- | --- | --- |
| P-384 subgroup scalar `n - 2` | 421 = 380S + 41M | [Brian Smith's 2017 article](https://briansmith.org/ecc-inversion-addition-chains-01): 433 = 381S + 52M; pinned `ring` source recount: 430 = 382S + 48M | 12 or 9 fewer abstract operations against those dated references. No present-best or native-speed claim. |
| Curve25519 subgroup scalar `l - 2` | 279 = 247S + 32M | [2017 article](https://briansmith.org/ecc-inversion-addition-chains-01): 284; [dated `addchain` result](https://github.com/mmcloughlin/addchain/commit/b52645e520ab79ae83c2dcff2a9e90f59359e6a6): 283 | Five or four fewer abstract operations against those dated references. No present-best or native-speed claim. |

The P-256 candidate 291 beats the 2017 article's 292 but loses to the pinned
`ring` source recount of 289. The included secp256k1 scalar 290 and Curve448
field 460 tie their respective references. P-521 582 has no vetted current
comparator in this release. See the [results table](../chains/README.md) for
the exact targets and qualifications. A replayed arithmetic schedule is not a
software speedup, security review, priority claim, or proof of optimality.

## Explored islands

| Region and search grammar | UTC observation | Measured or configured resources | Outcome and coverage |
| --- | --- | --- | --- |
| P-384 structural checkpoints: helper combinations, a 15-operation star prefix, and lower-192-bit carry/digit dynamic-programming tails | 425 by Sep 10 15:25; 424 Sep 23 01:31; 423 Sep 23 13:25; 422 Sep 23 13:38 | Comparable runtime, CPU-hours, model calls, cost, and operator minutes **unknown** | Exact included 425, 424, 423, and 422 schedules replay. They were selected best checkpoints from **different episodes**, not a parent-child mutation trail. The 425 is a live exponentiation DAG with one decreasing row. [Episodes](EPISODES.md) |
| P-384 fixed-scaffold CPU annealing with frozen arithmetic judge | Launched Sep 24 12:07:40; 421 reported Sep 24 12:50:43 | About 43 minutes from launch to reported result; seed 101, iteration 114144. Six seeds × 200,000 iterations were **configured**, not proven actual evaluations. Full raw run logs, CPU-hours, model-token use, spend, and operator minutes **unknown** | Frozen 421 certificate and separate checker replay. Six-seed checkpoint reports two seeds reaching 421, four best at 422, 210 distinct judge-valid 421 certificates, and none at 420 or below. Aggregate is not independently reconstructed from all raw logs. [Episodes](EPISODES.md) |
| P-384 one-helper sweep under one fixed prefix and tail grammar | Later checkpoint; exact UTC and elapsed time **unknown** | 27,160,037 digit evaluations across the completed no-helper baseline and three of 33 helpers; the next helper hit a 30,000,001-evaluation cap and was interrupted | **CENSORED.** No lower `0.8S + M` result in completed cases. The remaining helper cases were not exhausted. [Methods](METHODS_AND_LIMITS.md) |
| P-384 R7-pinned prefix, restricted 192-squaring tail: one-helper and selected two-helper regions | Later R10–R15 checkpoints; exact UTC and elapsed time **unknown** | 33/33 declared one-helper values, 20,488,942 states; 16 selected two-helper pairs, 9,429,312 states | **COMPLETED WITHIN DECLARED REGIONS.** The one-helper cases yielded no improving candidate; the selected two-helper pairs yielded no 420. Other prefixes, helpers, and tail grammars remain open. [Methods](METHODS_AND_LIMITS.md) |
| P-384 local prefix surgery from the *other* 421 = 381S + 40M schedule | Later checkpoint; exact UTC and elapsed time **unknown** | 9 eligible single-row deletions, 36 double-deletion pairs, 41,040 helper-parent proposals over 648 insertion gaps | **COMPLETED WITHIN DECLARED REGION.** No feasible 420; a second implementation agreed on enumeration and negative result. [Methods](METHODS_AND_LIMITS.md) |
| Curve25519 subgroup scalar window/helper searches | By Sep 29 01:06; exact launch and elapsed times **unknown** | 203,424 assessments produced 280; another region assessed 291,558 without a result below 280; a 9-bit region assessed 209,748 and produced 279 | The included 280 and 279 schedules pass Python and Node.js arithmetic replay. Assessment totals are region-specific, not comparable wall-time or token budgets. [Episodes](EPISODES.md) and [methods](METHODS_AND_LIMITS.md) |
| Later P-384 OpenEvolve case using a *different* 421 seed | By Sep 29; exact elapsed time and model spend **unknown** | 17 generated children reported, nine distinct certificates; one trace row missing | Best generated child was 425; the input seed remained 421. This is a bounded negative and does not explain discovery of the earlier frozen 421. [Case](../openevolve-case/README.md) |

These rows mix elapsed time, configured iterations, judge evaluations, search
states, and generated children. Those units are **not interchangeable**. Most
historical GPU use (if any), CPU-hours, model calls/tokens, dollar cost, and Tao's
operator minutes were not retained. We mark them unknown instead of treating
missing records as zero. The methods page records other bounded searches.

## Open islands and next discriminating tests

| Region | Current coverage | Useful next test |
| --- | --- | --- |
| Alternative prefix and window choices outside the declared subsets | **NOT EXHAUSTED** | Freeze an exact prefix/window set and tail grammar, then count unique candidates, wall time, and verifier passes. |
| Wider two-helper and multi-helper combinations | **PARTIAL**: 16 selected pairs under one prefix and tail grammar | Change one dimension at a time against a frozen baseline; do not turn one region's negative into a global lower bound. |
| Other representation families and broader non-tail-focused decompositions | **NOT SYSTEMATICALLY MAPPED**. One local prefix-surgery region and one compact-genotype case are documented above | Compare explicitly different grammars under matched budgets and the same arithmetic judge. |
| Current published and implementation frontier for each exact target | **UNKNOWN** beyond the dated/pinned comparisons above | Pin source revisions and recount the same exponent and operation metric before calling a candidate a current champion. |
| Native speed, constant-time behavior, and integration | **NOT TESTED** for these candidates | Implement separately and benchmark with fixed hardware, build, vectors, and side-channel criteria. |
| Transfer of the five agent skills across targets and model families | **HYPOTHESIS** | Run held-out tasks with and without each skill; measure valid outputs, repeats, operator corrections, time, and cost. |

## Why these regions were chosen

Tommy's 2026-09-29 retrospective account uses a blacksmith refining a candidate:
the
published construction looked strong in its regular section, while an
irregular tail appeared to offer nearby changes. That led the operator to
spend early effort on helpers, suffix representations, and bounded islands
before revisiting the prefix. This is an **analogy for search allocation**, not
a mathematical decomposition or evidence that a prefix is optimal. The
380/381 squarings above count whole schedules, not a frozen prefix.

In that same retrospective account, as the best recorded P-384 count moved
from selected 425 to 421 checkpoints, "420" was shorthand for **any result
below 421**, not a claim that 420 was the unique right target. The operator directed major pivots and agents
proposed or built parts of the search; this archive does not assign every
idea to a person or model. Preserved records of earlier trials may inform
later island selection, but this release has no equal-compute comparison or held-out
test proving a learned, transferable search policy. A narrower region was
chosen for tractable progress, not because other regions were ruled out.

The [methods and limits](METHODS_AND_LIMITS.md) specify what the bounded
negatives actually cover. New experiments should log target/exponent,
representation, frozen evaluator, input hash, proposal family, unique
candidate count, start and end UTC, wall and CPU time, model/API usage,
operator touches, cost, best valid certificate, independent replay, and
the region left unexplored.
