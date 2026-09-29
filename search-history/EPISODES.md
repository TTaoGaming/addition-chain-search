# Selected search cycles and evidence boundaries

The records below are selected **Plan → Do → Study → Act** episodes recovered
from local receipts, private Slack checkpoints, and source-bound GitHub work.
Times are UTC. A checkpoint time
is when a result was reported or observed, not necessarily the moment its
first candidate was generated. The original proposal streams, full chat
histories, comparable compute budgets, model-token costs, and operator time
are not bundled. A certificate link means its final arithmetic can be
replayed now; it does not replay how the search discovered it.

## Earlier P-384 exploration: reported source episodes

These September 10 receipts explain how the search moved before the five
bundled checkpoints. The exact early 432, 429, and 426 outputs are not in this
release. Their reported work counts and wall times come from the original run
receipts; they are not a same-budget comparison or a reconstructed continuous
mutation path.

| Observed UTC | Reported result | Search change | Reported work and observation |
| --- | --- | --- | --- |
| 2026-09-10 13:42 | 432 | Alternate prefix, paid helper 27, exact tail dynamic program. | 55 evaluations in 0.12955 s. A loop bug narrowed the tested neighborhood; the result was not an exhaustive search. |
| 2026-09-10 13:42–13:43 | 429 | Correct the loop and try paid helper 59. | 761 single-addition evaluations in 1.01867 s; Python and separate C++ arithmetic replay were reported. |
| 2026-09-10 15:08 | 426 | Joint dictionary-DAG and tail mixed-integer search. | 1,720 binary variables, 2,622 constraints, nine solver nodes, 6.946 s reported wall. |
| By 2026-09-10 15:25 | 425 | Reverse exact-exponent DAG allowing overlapping positive digits, with paid helper `71 = 22 + 49`. | 89 parent proposals, 61 values, 15.826 s reported wall. This source stream is **not byte-bound** to the later bundled 425 certificate. |

The wall figures measure different small runs, not total project time. The
public 425 certificate below is a later retained artifact; its check does not
retroactively verify every early search receipt.

| When (UTC) | Plan / change | Observed result | Study / next action |
| --- | --- | --- | --- |
| By 2026-09-10 15:25 | Explore a P-384 scalar schedule below the published 433. | A 425 = 380S+45M **count** was reported; the [later bundled 425](../chains/p384/certificates/p384_425.txt) has the same count. | The early source stream and bundled certificate are not byte-bound. The bundled file replays as a live exponentiation DAG but has one decreasing row. Its 2026-09-21 21:13:57 commit author time is not the early discovery time. |
| 2026-09-23 01:31:01 | Combine helpers with a lower-192-bit digit dynamic program. | [424 = 380S+44M](../chains/p384/certificates/p384_424.txt). | Correct an earlier out-of-order helper placement, match the recorded certificate hash, and continue varying structure. |
| 2026-09-23 02:45–02:47 | Trade S against M at the same total. | Other 424 variants reported as 381S+43M and 382S+42M. | Illustrative `0.8S + M` cost improved; the exact variant files are **not** included here, so these are reported-only history. |
| 2026-09-23 13:25:29 | Enumerate a 15-operation star prefix, then score downstream carry-DP tails. | [423 = 381S+42M](../chains/p384/certificates/p384_423.txt). | Replay exact certificate and try a different prefix/helper composition. |
| 2026-09-23 13:38:34 | Change prefix, add two helpers, and rescore a 192-bit tail. | [422 = 382S+40M](../chains/p384/certificates/p384_422.txt). | Replay exact certificate and search a different fixed scaffold. |
| 2026-09-24 12:07:40 → 12:50:43 | Launch a fixed-scaffold CPU annealing lane under a frozen arithmetic judge. | [421 = 380S+41M](../chains/p384/certificates/p384_421.txt), reported at seed 101, iteration 114144. | Freeze certificate SHA-256 `844866b0703ef55ca41fc616a7226fe6d8aca3022ead18cdaec1e0911422e02e` and replay with a separate checker. A private pinned branch retains the generator, evaluator, and selected genotype; raw run logs are not in this archive. No LLM was in the candidate loop. |
| 2026-09-24 13:35:59 | Complete six-seed CPU anneal tally: seeds 101–106, 200,000 configured iterations each. | Private checkpoints report two seeds reaching 421, four best at 422, 210 distinct judge-valid 421 certificates, and none at ≤420. | Reported aggregate, not independently replayed from all six raw logs here. This is not a global lower bound or a retained 1.2-million-row trace. |
| 2026-09-25 | Probe further bounded P-384 neighborhoods. | Private checkpoints report two mis-tuned seeds stopped, later carry-aware seeds with best 421, and one-row/one-helper tests without ≤420. | Negative only within those regions and budgets; raw logs and distinct verification are not bundled. |
| By 2026-09-28 | Explore a different P-384 421 S/M balance. | [421 = 381S+40M](../chains/p384/later_candidate/p384_421_381S40M.txt). | Local arithmetic replay; exact discovery time is unknown. The illustrative `0.8S + M` score is 344.8 versus 345.0 for 380S+41M. |
| By 2026-09-29 01:06 | Widen a Curve25519 scalar helper/window region after the included 281 result. | [280 = 249S+31M](../chains/targets/curve25519/frontier/curve25519_scalar_280.json), from 203,424 score assessments. | A later widened helper-cap region assessed 291,558 cases without a chain below 280. Keep this negative scoped to that region. |
| By 2026-09-29 08:19 | Test another Curve25519 scalar 9-bit window/helper region. | [279 = 247S+32M](../chains/targets/curve25519/frontier/curve25519_scalar_279.json). The prior packet reports 209,748 assessments; the original proposal log is not included here. | Normalize stale helper metadata after dead-row pruning; exact certificate passes separate Python and Node.js replay. It uses one more general multiplication than 280, so native cost remains unknown. |

The 424 helper-301 route kept the existing route to `2^192−1`, removed two
helpers, paid for `301 = 49 + 252`, and reduced the low-192 tail to 29
additions. A later bounded follow-up tried 91 one-helper values, 136 pairs
among 17 stronger one-helper choices, and 438 random dependent two-helper
genotypes without a 423 in those regions. Another screen enumerated 103,193
distinct ten-operation chains ending at 63. Those negatives helped motivate a
different prefix/dictionary representation; they did not rule out other
helpers or prefixes.

The later 423→422 campaign reports 748 exact 15-operation star chains ending
at 4095, 3,622 valid insertion mutants, and 12 reaching its raw-tail-32
threshold. One helper reached a 423 class; a different two-helper composition
reached the bundled 422. The headline bundled 423 certificate is not a
demonstrated direct parent of that 422. Third and fourth helpers were neutral
at 422 in the tested family. A separate later source replay reproduced the 422 certificate. These
are **campaign-specific counts**, not 4,095 prefixes tested and not a claim
that the prefix is optimal.

Subsequent fixed-region searches described in [METHODS_AND_LIMITS.md](METHODS_AND_LIMITS.md)
returned bounded negatives, including completed one-helper and selected
two-helper sweeps under a pinned prefix. None produced a bundled 420
certificate. Those negative results do **not** establish a global lower bound.

## Other target episodes and pivots

| Observed UTC | Target and bounded region | Result and next decision |
| --- | --- | --- |
| 2026-09-29 00:18 | P-256 scalar: guided and control arms assessed 24,000 candidates each; a further 169,271 assessments tested another region. | The arms scored 301 and 305; the later region reached 296, still behind the bundled local [291](../chains/targets/p256/candidate.json). The 116.078 s Python CPU report covers the wider P-256/P-521 wave, not this P-256 arm alone. A pinned `ring` source recount of 289 later corrected the dated-292 comparison: our 291 is not the best count against that source. |
| 2026-09-29 03:24 and 04:37 | P-521 scalar: sparse width-7 (385/385) and disjoint width-8 (637/637) regions. | Each region's best was 583, worse than the bundled local [582](../chains/targets/p521/candidate.json). The next improvement came from a different deletion/repair grammar, not from extending either sparse-helper sweep. |
| By 2026-09-29 08:19 | P-521 scalar: remove exponent 30 from a local 582 schedule and rebuild exponent 60 as `29 + 31`. | Two alternative [581 schedules](../review-candidates/README.md) now replay at 517S+64M and 516S+65M. Subsequent single-deletion and 64 one-step portal tests found no 580 in their declared regions; they are not a lower bound for P-521. |
| 2026-09-29 12:10–13:11 | secp256k1 scalar: allow overlapping positive tail digits and carries under a fixed scaffold. | A recovered 289 led to a [288 = 253S+35M certificate](../review-candidates/README.md). The terminal receipt reports 120,300 candidate checks across four named runs **including duplicates**; in the final run, 7,942 were fresh digit-set solves and 19,382 were cached reuses. Search provenance is partial; the certificate has separate arithmetic replay. |
| Exact episode UTC unknown | Curve448 **field** `p−2`: source-derived baseline and narrowly bounded split variants. | The [460 = 447S+13M assay](../chains/FIELD_CURVE448.md) ties its source comparison. It is not a scalar result or a shorter-chain claim. |

Curve25519 subgroup scalar work also included the replayed 283 → 282 → 281 →
280 → 279 steps. The 283
candidate was reordered by exponent from an earlier live DAG while preserving
every parent pair; its source SHA-256 is recorded in the normalized
file. A search-grammar metadata phrase in this 283 release file was sanitized;
the original file and its SHA-256 are held privately. The separate
[Curve448 field assay](../chains/FIELD_CURVE448.md) records a two-value split
test. These target families have different exponents and search scopes; their
counts are not a single optimization race. The older chain ZIP still contains
P-521 582 and secp256k1 290; the newer 581 and 288 certificates are in the
separate review-only section.

The observed loop was to change a representation or search region, test it,
replay a candidate's exact arithmetic, study failures, and choose another
region. The private generator and selected genotype were recovered after an
earlier packet mistakenly said the generator was missing; the raw six-seed
trajectory still is not included. This does not show that the agent ecology
learned a transferable helper-selection policy. The public evidence is strongest for the
included final arithmetic certificates and weakest for unbundled search
trajectories and resource costs.
