# Selected search cycles and evidence boundaries

The records below are selected **Plan → Do → Study → Act** episodes recovered
from local receipts and collaboration logs. Times are UTC. A checkpoint time
is when a result was reported or observed, not necessarily the moment its
first candidate was generated. The original proposal streams, full chat
histories, comparable compute budgets, model-token costs, and operator time
are not bundled. A certificate link means its final arithmetic can be
replayed now; it does not replay how the search discovered it.

| When (UTC) | Plan / change | Observed result | Study / next action |
| --- | --- | --- | --- |
| By 2026-09-10 15:25 | Explore P-384 scalar schedule below the published 433. | [425 = 380S+45M](../chains/p384/certificates/p384_425.txt) reported. | Replayed as a live exponentiation DAG. One output row decreases, so it is not a strictly increasing chain. Later exact file is preserved; its 2026-09-21 21:13:57 commit author time is not the discovery time. |
| 2026-09-23 01:31:01 | Combine helpers with a lower-192-bit digit dynamic program. | [424 = 380S+44M](../chains/p384/certificates/p384_424.txt). | Correct an earlier out-of-order helper placement, match the recorded certificate hash, and continue varying structure. |
| 2026-09-23 02:45–02:47 | Trade S against M at the same total. | Other 424 variants reported as 381S+43M and 382S+42M. | Illustrative `0.8S + M` cost improved; the exact variant files are **not** included here, so these are reported-only history. |
| 2026-09-23 13:25:29 | Enumerate a 15-operation star prefix, then score downstream carry-DP tails. | [423 = 381S+42M](../chains/p384/certificates/p384_423.txt). | Replay exact certificate and try a different prefix/helper composition. |
| 2026-09-23 13:38:34 | Change prefix, add two helpers, and rescore a 192-bit tail. | [422 = 382S+40M](../chains/p384/certificates/p384_422.txt). | Replay exact certificate and search a different fixed scaffold. |
| 2026-09-24 12:07:40 → 12:50:43 | Launch a fixed-scaffold CPU annealing lane under a frozen arithmetic judge. | [421 = 380S+41M](../chains/p384/certificates/p384_421.txt), reported at seed 101, iteration 114144. | Freeze certificate SHA-256 `844866b0703ef55ca41fc616a7226fe6d8aca3022ead18cdaec1e0911422e02e` and replay with a separate checker. A private pinned branch retains the generator, evaluator, and selected genotype; raw run logs are not in this archive. No LLM was in the candidate loop. |
| 2026-09-24 13:35:59 | Complete six-seed CPU anneal tally: seeds 101–106, 200,000 configured iterations each. | Private checkpoints report two seeds reaching 421, four best at 422, 210 distinct judge-valid 421 certificates, and none at ≤420. | Reported aggregate, not independently replayed from all six raw logs here. This is not a global lower bound or a retained 1.2-million-row trace. |
| 2026-09-25 | Probe further bounded P-384 neighborhoods. | Private checkpoints report two mis-tuned seeds stopped, later carry-aware seeds with best 421, and one-row/one-helper tests without ≤420. | Negative only within those regions and budgets; raw logs and distinct verification are not bundled. |
| By 2026-09-28 | Explore a different P-384 421 S/M balance. | [421 = 381S+40M](../chains/p384/later_candidate/p384_421_381S40M.txt). | Local arithmetic replay; exact discovery time is unknown. The illustrative `0.8S + M` score is 344.8 versus 345.0 for 380S+41M. |
| By 2026-09-29 01:06 | Widen a Curve25519 scalar helper/window region after the included 281 result. | [280 = 249S+31M](../chains/targets/curve25519/frontier/curve25519_scalar_280.json), from 203,424 score assessments. | A later widened helper-cap region assessed 291,558 cases without a chain below 280. Keep this negative scoped to that region. |
| By 2026-09-29 01:06 | Test another Curve25519 scalar 9-bit window/helper region. | [279 = 247S+32M](../chains/targets/curve25519/frontier/curve25519_scalar_279.json), from 209,748 assessments. | Normalize stale helper metadata after dead-row pruning; exact certificate passes separate Python and Node.js replay. It uses one more general multiplication than 280, so native cost remains unknown. |

Subsequent fixed-region searches described in [METHODS_AND_LIMITS.md](METHODS_AND_LIMITS.md)
returned bounded negatives, including completed one-helper and selected
two-helper sweeps under a pinned prefix. None produced a bundled 420
certificate. Those negative results do **not** establish a global lower bound.

Other target work in this snapshot includes replayed P-256 291, P-521 582,
Curve25519 subgroup 283 → 282 → 281 → 280 → 279, and a secp256k1 290 tie. The 283
candidate was reordered by exponent from an earlier live DAG while preserving
every parent pair; its source SHA-256 is recorded in the normalized
file. A search-grammar metadata phrase in this 283 release file was sanitized;
the original file and its SHA-256 are held privately. The separate
[Curve448 field assay](../chains/FIELD_CURVE448.md) records a 460 tie and an exhausted
two-value split test. These target families have different exponents and
search scopes; their counts are not a single optimization race.

The observed loop was to change a representation or search region, test it,
replay a candidate's exact arithmetic, study failures, and choose another
region. The private generator and selected genotype were recovered after an
earlier packet mistakenly said the generator was missing; the raw six-seed
trajectory still is not included. This does not show that the agent ecology
learned a transferable helper-selection policy. The public evidence here is strongest for the
included final arithmetic certificates and weakest for unbundled search
trajectories and resource costs.
