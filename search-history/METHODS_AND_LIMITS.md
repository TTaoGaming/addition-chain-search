# Search methods and evidence limits

The proof checkers consume frozen certificates; they do not execute any search.
The following search details come from selected local run receipts and are
reported provenance, not independently reproduced searches in this release.
Source-hash fields in several candidate JSON files are opaque historical
pointers to source candidates that are not bundled here. The public verifier
checks the included file hashes and arithmetic, not those pointers.

The early P-384 receipts form a sequence of **search changes**, not a single
comparable run: an alternate-prefix and helper-27 tail DP reported 432 after
55 evaluations (its loop bug narrowed the region); a corrected helper-59 run
reported 429 after 761 evaluations; a joint dictionary/tail MILP reported 426
with 1,720 binary variables, 2,622 constraints, and nine solver nodes; and a
reverse exact-exponent DAG reported 425 after 89 parent proposals. The exact
432, 429, and 426 outputs are absent. The early 425 source stream is not
byte-bound to the later bundled 425 certificate. See the dated
[episodes](EPISODES.md) for the observed UTC and reported wall times.

| Target | Recorded search scope | What the included certificate proves |
| --- | --- | --- |
| P-384 421 = 380S + 41M | Custom CPU simulated annealing added, dropped, or replaced constructible intermediate exponents. A digit dynamic program scored a fixed dictionary within a restricted positive-digit representation with carries. Reported discovery point: seed 101, iteration 114144. | Exact 421-row arithmetic schedule for scalar `n - 2`; search source and full run log are absent here. |
| P-256 291 | Fixed prefix and restricted suffix search tested 270 helper cases: 1 improved, 11 tied, 258 worsened relative to that run's incumbent. | Exact 291-row normalized DAG with 254S + 37M. |
| P-521 582 | A run receipt reports 1,834 prefix/width grid cases and 4,032 omission cases. A prior 584-row trace was superseded after liveness checking found dead rows. | Exact 582-row DAG with 519S + 63M. |
| Curve25519 subgroup 283 → 282 → 281 | A dictionary search reached 283 = 250S+33M; a separate carrier and later widened search reached 282 = 250S+32M. A further run receipt reports 4,266 states and 5,049,759 dynamic-program transitions in 10.41 seconds for 281. | All three included arithmetic DAGs replay. The final 281 has 249S + 32M. The original 283 row order was nonmonotone; its bundled normalized version sorts the same parent pairs by exponent. |
| Curve25519 subgroup 280 and 279 | One 8-bit region assessed 203,424 candidates and produced 280 = 249S+31M. A later wider helper-cap region assessed 291,558 without a result below 280. A 9-bit window/helper region assessed 209,748 and produced 279 = 247S+32M. | The two exact included schedules replay in separate Python and Node.js checkers. The raw 279 search output had stale helper metadata after dead-row pruning; the included 279 certificate is the normalized version. Full proposal traces and search source are not bundled. |
| secp256k1 subgroup 290 | A local transfer normalized an existing certificate and a second implementation checked 22 samples; the shared checker replays six bases. | Exact 290-row DAG with 253S + 37M, **tying** the 2017 published count. This is not a lower or novel result. |
| P-521 second 582 variant | Reachability-prune conversion removed two unused rows from an earlier 584-row source trace. | Exact 582-row DAG with 518S + 64M; its local verifier checks parent sums, liveness, and five modular bases. The 519S + 63M variant has lower illustrative `0.8S + M` cost (478.2 vs 478.4). |

The September 23 P-384 campaign covered 748 exact 15-operation star chains to
4095 and 3,622 valid insertion mutants; 12 met that campaign's raw-tail-32
screen. A one-helper route reached a 423 class, while a different two-helper
route yielded the bundled 422. These are campaign counts, not 4,095 tested
prefixes or a proven parent-child path between the two bundled certificates.
Third and fourth helpers were neutral in the tested family. A separate earlier
helper neighborhood and 103,193 ten-operation chains ending at 63 also failed
to improve under their respective screens; neither negative exhausts other
representations.

Two September 29 arithmetic certificates are in a separate
[review-only section](../review-candidates/README.md), after the frozen chain
archive: P-521 581 = 517S + 64M and 516S + 65M, found by deleting exponent 30
from a local 582 and rebuilding exponent 60 as `29 + 31`; and secp256k1 288 =
253S + 35M, found after allowing overlapping positive tail digits and carries
under a fixed scaffold. The P-521 sparse-width regions separately tested
385 and 637 cases with best 583. The secp terminal receipt reports 120,300
candidate checks across four runs **including duplicates**; its final run
separates 7,942 fresh solves from 19,382 cache reuses. Neither review-only
certificate establishes current public-best status, native speed, or complete
search provenance.

One later P-384 fixed-prefix, low-192-bit digit-DP sweep declared 33 helper
candidates plus a no-helper baseline. The baseline and three helpers completed
27,160,037 digit evaluations without a lower `0.8S + M` result. The next
helper was interrupted by the 30,000,001-evaluation cap; the remaining 30
helper cases were not tested to completion. This is a bounded negative for
four completed cases in that run, not evidence that its full helper region was
exhausted at the time.

Later R10–R13 runs used a **different, pinned R7 prefix** and completed all 33
declared one-helper values under its fixed 192-squaring, at-most-one-positive-
digit-per-bit tail representation: 5 + 5 + 20 + 3 disjoint cases, totaling
20,488,942 states. None produced an improving candidate in those declared
regions. R15 completed 16 selected two-helper pairs under the same R7 prefix
and tail grammar (9,429,312 states) without a 420-row candidate. Pair selection
followed a frozen parent-disjointness rule; it was not a learned policy. These
results do not exhaust other prefix dictionaries, helper constructions, or
tail representations.

A separate fixed-output prefix-surgery search started from the later
P-384 421 = 381S + 40M variant. It checked 9 eligible single-row deletions,
36 double-deletion pairs, and 41,040 helper-parent proposals across 648
insertion gaps. No feasible 420 appeared in that declared region. A second
implementation agreed on the enumeration and negative result. This does not
rule out 420 in a different representation or search region.

The search counts describe different regions and budgets. They cannot be
compared as an equal-compute contest. Human-directed pivots and agent-written
tools used deterministic inner scoring; no learned helper-selection policy is
established. There is no shortest-chain proof, general transfer result, native
timing, side-channel assessment, or production adoption in this snapshot.
There is no verified 420-operation P-384 certificate here. Agent assistance in
building search tools does not turn arithmetic replay into human or external
cryptographic acceptance.

The separate [Curve448 field assay](../chains/FIELD_CURVE448.md) targets `p - 2`,
not scalar `n - 2`. Its source-derived 460 baseline is a tie with published
implementations; an iteration-censored local mutation run and a complete
two-value split test found no lower candidate in their respective declared
regions. It must not be combined with the scalar result counts.

The P-256 291 result only improves on the 2017 article's 292. A static
recount of pinned `ring` source at commit
`840167e18e4fa837eb48de46500454a616a15a6e` (`src/ec/suite_b/ops/p256.rs`)
gives 289 = 254S + 35M. No current-best P-256 claim is made.

The reference comparisons for P-384, P-256, and Curve25519 subgroup scalar
inversion are from the public 2017 article *ECC Inversion Addition Chains*.
The P-521 subgroup order is specified in [NIST SP 800-186](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf).
For this sanitized release, two target-manifest source strings and one
search-grammar phrase differ from the privately retained originals. Numerical
target fields and candidate rows are unchanged. The release checker pins and
replays the sanitized bytes; it does not establish byte identity with the
original evidence or reproduce the underlying search.
