# Search islands, coverage, and resource ledger

Reconciled 2026-09-29 19:10 UTC from selected private receipts and the public
certificates. Each row names a **region of a search**, not an exhaustive
region of all possible addition chains. Times are UTC. `S` is a squaring and
`M` is another multiplication. Different scalar targets are separate problems;
the Curve448 field assay is separate again. The [exact candidate checks](../chains/README.md)
and [search episodes](EPISODES.md) give the detailed evidence boundaries. A
private Slack checkpoint is a reported search observation; a bundled
certificate with an offline checker is stronger evidence of the final math.

## Candidate frontier in this public snapshot

| Exact target | Locally replayed candidate | Dated comparison | Claim ceiling |
| --- | --- | --- | --- |
| P-384 subgroup scalar `n - 2` | [421 = 380S + 41M](../chains/p384/certificates/p384_421.txt); later [421 = 381S + 40M](../chains/p384/later_candidate/p384_421_381S40M.txt) | [Brian Smith's 2017 article](https://briansmith.org/ecc-inversion-addition-chains-01): 433; pinned `ring` source recount: 430 | Locally replayed count improvement against those pinned references; no verified 420, current-best, or native-speed claim. |
| Curve25519 subgroup scalar `l - 2` | [279 = 247S + 32M](../chains/targets/curve25519/frontier/curve25519_scalar_279.json); 280 is another S/M tradeoff | [2017 article](https://briansmith.org/ecc-inversion-addition-chains-01): 284; [dated `addchain` result](https://github.com/mmcloughlin/addchain/commit/b52645e520ab79ae83c2dcff2a9e90f59359e6a6): 283 | Locally replayed below those dated counts; current rank and speed unknown. |
| P-256 subgroup scalar `n - 2` | [291 = 254S + 37M](../chains/targets/p256/candidate.json) | 2017 article: 292; pinned `ring` recount: **289** | Below the dated article but worse than the pinned implementation count. |
| P-521 subgroup scalar `n - 2` | [581 = 517S + 64M or 516S + 65M](../review-candidates/README.md) | Our earlier local 582; external current comparator **unknown** | Review-only arithmetic certificates; one-operation local improvement, not a public-best claim. |
| secp256k1 subgroup scalar `n - 2` | [288 = 253S + 35M](../review-candidates/README.md) | Brian's dated 2017 290 = 253S + 37M | Review-only arithmetic certificate two multiplications below that dated count; no current-rank or native-speed claim. |
| Curve448 **field** `p - 2` | [460 = 447S + 13M](../chains/FIELD_CURVE448.md) | Source-derived 460 | Tie, not a new count improvement; separate field target. |

The older `chains/` ZIP still contains local P-521 582 and secp256k1 290;
the newer 581/288 files and their checker are in the separate review-only
directory. These are not one cross-curve leaderboard. A replayed schedule is
not a software speedup, security review, priority claim, or optimality proof.

## Explored islands

| Region and search grammar | UTC observation | Measured or configured resources | Outcome and coverage |
| --- | --- | --- | --- |
| P-384 early prefix/tail probes, corrected dictionary, then joint dictionary/tail MILP and reverse exponent DAG | Sep 10 13:42–by 15:25 | Four distinct reported runs: 55 evaluations/0.130 s; 761/1.019 s; MILP 1,720 binaries, 2,622 constraints, nine nodes/6.946 s; 89 parent proposals, 61 values/15.826 s | Reported 432 → 429 → 426 → 425. Early outputs are not bundled or byte-bound to the later public 425. One early loop bug narrowed its region. [Episodes](EPISODES.md) |
| P-384 structural checkpoints: helper combinations, a 15-operation star prefix, and lower-192-bit carry/digit dynamic-programming tails | 425 by Sep 10 15:25; 424 Sep 23 01:31; 423 Sep 23 13:25; 422 Sep 23 13:38 | Comparable runtime, CPU-hours, model calls, cost, and operator minutes **unknown** | Exact included 425, 424, 423, and 422 schedules replay. They were selected best checkpoints from **different episodes**, not a parent-child mutation trail. The 425 is a live exponentiation DAG with one decreasing row. [Episodes](EPISODES.md) |
| P-384 424→423→422 prefix/dictionary pivot | Sep 23 checkpoints | A 424 follow-up reported 91 one-helper values, 136 selected pairs, and 438 random dependent two-helper genotypes without 423. The later campaign reported 103,193 ten-operation chains to 63, then 748 exact 15-operation star chains to 4095, 3,622 insertion mutants, and 12 raw-tail-32 survivors | These are separate bounded screens; one helper reached a 423 class and a different two-helper composition reached the bundled 422. The headline 423 certificate is not a demonstrated parent of 422. [Episodes](EPISODES.md) |
| P-384 fixed-scaffold CPU annealing with frozen arithmetic judge | Launched Sep 24 12:07:40; 421 reported Sep 24 12:50:43 | About 43 minutes from launch to reported result; seed 101, iteration 114144. Six seeds × 200,000 iterations were **configured**, not proven actual evaluations. Full raw run logs, CPU-hours, model-token use, spend, and operator minutes **unknown** | Frozen 421 certificate and separate checker replay. Six-seed checkpoint reports two seeds reaching 421, four best at 422, 210 distinct judge-valid 421 certificates, and none at 420 or below. Aggregate is not independently reconstructed from all raw logs. [Episodes](EPISODES.md) |
| P-384 one-helper sweep under one fixed prefix and tail grammar | Later checkpoint; exact UTC and elapsed time **unknown** | 27,160,037 digit evaluations across the completed no-helper baseline and three of 33 helpers; the next helper hit a 30,000,001-evaluation cap and was interrupted | **CENSORED.** No lower `0.8S + M` result in completed cases. The remaining helper cases were not exhausted. [Methods](METHODS_AND_LIMITS.md) |
| P-384 R7-pinned prefix, restricted 192-squaring tail: one-helper and selected two-helper regions | Later R10–R15 checkpoints; exact UTC and elapsed time **unknown** | 33/33 declared one-helper values, 20,488,942 states; 16 selected two-helper pairs, 9,429,312 states | **COMPLETED WITHIN DECLARED REGIONS.** The one-helper cases yielded no improving candidate; the selected two-helper pairs yielded no 420. Other prefixes, helpers, and tail grammars remain open. [Methods](METHODS_AND_LIMITS.md) |
| P-384 local prefix surgery from the *other* 421 = 381S + 40M schedule | Later checkpoint; exact UTC and elapsed time **unknown** | 9 eligible single-row deletions, 36 double-deletion pairs, 41,040 helper-parent proposals over 648 insertion gaps | **COMPLETED WITHIN DECLARED REGION.** No feasible 420; a second implementation agreed on enumeration and negative result. [Methods](METHODS_AND_LIMITS.md) |
| Curve25519 subgroup scalar window/helper searches | 280 reported by Sep 29 01:06; 279 observed by 08:19; exact 279 launch and elapsed times **unknown** | 203,424 assessments produced 280 with reported 96.109 s producer wall/92.969 s CPU; another region assessed 291,558 without below-280; the prior packet reports 209,748 assessments for the 9-bit region that produced 279 | The included 280 and 279 schedules pass Python and Node.js arithmetic replay. The 279 proposal log is not included; assessment totals are region-specific. [Episodes](EPISODES.md) and [methods](METHODS_AND_LIMITS.md) |
| P-256 scalar guided and control probes | Sep 29 00:18; comparator correction 08:24 | 24,000 assessments per arm, then 169,271 in another region; 116.078 s reported Python CPU covers the wider P-256/P-521 wave, not this row alone | Guided 301 versus control 305; later 296, still behind local 291. Pinned `ring` recount is 289, so improvement against dated 292 is not a current-source win. [Episodes](EPISODES.md) |
| P-521 scalar sparse helper regions, then deletion/repair | Sep 29 03:24, 04:37, 08:19 | Width-7 385/385 and width-8 637/637, each best 583; then deletion of exponent 30 and rebuilding 60. A later 64-case one-step portal region was negative, with about 355.81 s reported wall | The representation pivot produced two replayable 581 cost variants below our local 582. No vetted external P-521 comparator or global 580 lower bound. [Review certificates](../review-candidates/README.md) |
| secp256k1 scalar overlapping positive tail digits and carries | Sep 29 12:10–13:11 recovery segment | 120,300 candidate checks across R4/R5/R7/R8 **including duplicates**. R8 had 7,942 fresh digit-set solves and 19,382 cache reuses; retrospective lookups are not new evaluations | Review-only 288 certificate replays. Full source trajectory, comparable token/cost, and native benchmark are not bundled. [Review certificate](../review-candidates/README.md) |

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
| Other representation families and broader non-tail-focused decompositions | **NOT SYSTEMATICALLY MAPPED**. One local prefix-surgery region is documented above | Compare explicitly different grammars under matched budgets and the same arithmetic judge. |
| Current published and implementation frontier for each exact target | **UNKNOWN** beyond the dated/pinned comparisons above | Pin source revisions and recount the same exponent and operation metric before calling a candidate a current champion. |
| P-521 current scalar comparator and secp256k1 288 discovery trajectory | **PARTIAL**: exact review certificates replay, but P-521 lacks a vetted external comparator and the complete secp search trace was not independently inspected | Freeze source/target revisions and retain raw proposal/cache traces; keep cache hits separate from fresh solves and obtain a distinct trajectory review. |
| Native speed, constant-time behavior, and integration | **NOT TESTED** for these candidates | Implement separately and benchmark with fixed hardware, build, vectors, and side-channel criteria. |
| Transfer of the five agent skills across targets and model families | **HYPOTHESIS** | Run held-out tasks with and without each skill; measure valid outputs, repeats, operator corrections, time, and cost. |

## Why these regions were chosen

Tommy's 2026-09-29 retrospective account uses a blacksmith refining a candidate:
the published construction looked strong in its regular section, while an
irregular tail appeared to offer nearby changes. That led the operator to
spend early effort on helpers, suffix representations, and bounded islands
before revisiting the prefix. This is an **analogy for search allocation**, not
a mathematical decomposition or evidence that a prefix is optimal. The
380/381 squarings above count whole schedules, not a frozen prefix.

In that same retrospective account, as the best recorded P-384 count moved
from selected 425 to 421 checkpoints, "420" was shorthand for **any result
below 421**, not a claim that 420 was the unique right target. The operator
directed major pivots and agents proposed or built parts of the search; this
archive does not assign every
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
