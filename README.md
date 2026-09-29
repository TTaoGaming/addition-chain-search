# Addition-chain search: four-part review packet

Tommy Tai's AI-assisted research follows [Brian Smith's public 2017
article](https://briansmith.org/ecc-inversion-addition-chains-01). No
endorsement from Brian is claimed. **One link to share is this page**;
each part below can be read separately. This is a selected public snapshot
as of 2026-09-29 17:03 UTC, not a census of unpublished candidates or the
current global best.

| Part | Plain-language use | Open |
| --- | --- | --- |
| **1. Checkable candidates and dated baselines** | Inspect exact scalar targets and run the arithmetic checks. P-384 421 and Curve25519 subgroup 279 beat **dated operation-count references**, with native speed and current-best status untested. | [Read](chains/README.md) · [ZIP](01_addition_chains_r4.zip) |
| **2. Search episodes and island map** | See the selected 425→421 checkpoints, tested and untested regions, UTC/resource evidence, bounded failures, and missing raw logs. The checkpoints came from different episodes. | [Read](search-history/README.md) · [ZIP](02_search_history_reconstruction_r2.zip) |
| **3. Agent skills** | Inspect five MIT-licensed procedures: three general research skills and two addition-chain checks. Transfer across models remains a behavioral-test hypothesis. | [Read](skills/README.md) · [ZIP](03_agent_skills_r9_mit_public.zip) |
| **4. Reviewer guide and open questions** | Run the shortest independent check, follow each claim to its evidence, and see what would need testing next. | [Read](REVIEWER_GUIDE.md) |

For a quick check, run `python -B chains/verify_all.py` in a fresh checkout;
it should report `PASS_LOCAL_ARITHMETIC_ONLY`. This verifies the **included
certificates**, not how the search discovered them or how fast a native
implementation would run. The [reviewer guide](REVIEWER_GUIDE.md) explains
that boundary.

The separate [OpenEvolve P-384 case](openevolve-case/README.md)
([ZIP](04_openevolve_p384_case_r3_public.zip)) is an optional negative-result
appendix under part 4. It did not improve its different 421 seed. The case,
reconstructed history, and reviewer guide are public for inspection without
reuse licenses; the agent skills are MIT licensed. See [reuse terms](skills/REUSE_TERMS.md),
[limitations](LIMITATIONS_AND_UNKNOWN.md), and [release hashes](PUBLIC_SHA256SUMS.txt).
