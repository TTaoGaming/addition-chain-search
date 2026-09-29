# Addition-chain search

Tommy Tai's AI-assisted research builds on [Brian Smith's public 2017 article](https://briansmith.org/ecc-inversion-addition-chains-01). This 2026-09-29 UTC snapshot publishes arithmetic certificates, a selected reconstruction of the search, and agent skills. Clone the project and run `python -B chains/verify_all.py` to replay the included chains.

| Project area | What it contains | Open |
| --- | --- | --- |
| **1. Published chain candidates** | Exact exponents, schedules, checkers, and dated comparisons. | [Results](chains/README.md) · [ZIP](01_addition_chains_r4.zip) |
| **2. Search history** | Selected 425→421 episodes, explored islands, resource records, and gaps. | [History](search-history/README.md) · [ZIP](02_search_history_reconstruction_r3.zip) |
| **3. Agent skills** | Five MIT-licensed procedures that may transfer to other agents and targets; behavioral transfer has not been tested. | [Skills](skills/README.md) · [ZIP](03_agent_skills_r10_mit_public.zip) |

The [verification guide](REVIEWER_GUIDE.md) gives the shortest commands and maps each claim to its source.

## Published candidates

| Exact target | Locally replayed candidate | Dated comparison | Evidence here |
| --- | --- | --- | --- |
| P-384 subgroup scalar `n−2` | **421 = 380S + 41M** | Brian's 2017 433; pinned `ring` source recount 430 | [Frozen certificate and checker](chains/p384/verify_frozen_421.py) |
| Curve25519 prime-subgroup scalar `l−2` | **279 = 247S + 32M** | 2017 284; dated `addchain` 283 | [Certificate and two replayers](chains/targets/curve25519/frontier/README.md) |

`S` means squaring; `M` means another multiplication. These are abstract operation counts for the **same target**, not native timings or claims of current global best. Additional internal leads are under review and are outside this release. The verifier returns `PASS_LOCAL_ARITHMETIC_ONLY`; [limitations](LIMITATIONS_AND_UNKNOWN.md) states the open questions once. [Release hashes](PUBLIC_SHA256SUMS.txt) and [changes](CHANGELOG.md) identify these exact files.
