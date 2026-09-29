# Addition-chain search: reviewer packet v7

Tommy Tai's AI-assisted research builds on [Brian Smith's public 2017 article](https://briansmith.org/ecc-inversion-addition-chains-01). This selected snapshot was prepared 2026-09-29 UTC. It presents exact certificates and a reconstructed account of the search.

| Part | What to use it for | Open |
| --- | --- | --- |
| **1. Chain results** | Check the exact exponents, schedules, and dated comparisons. | [Results](chains/README.md) · [ZIP](01_addition_chains_r4.zip) |
| **2. Search history** | See the selected 425→421 episodes, explored islands, resource records, and gaps. | [History](search-history/README.md) · [ZIP](02_search_history_reconstruction_r3.zip) |
| **3. Agent skills** | Reuse five MIT-licensed procedures: three general research skills and two chain-specific checks. | [Skills](skills/README.md) · [ZIP](03_agent_skills_r10_mit_public.zip) |
| **4. Reviewer guide** | Run the shortest checks and trace each claim to its source. | [Guide](REVIEWER_GUIDE.md) |

| Exact target | Included candidate | Dated comparison | Evidence here |
| --- | --- | --- | --- |
| P-384 subgroup scalar `n−2` | **421 = 380S + 41M** | Brian's 2017 433; pinned `ring` source recount 430 | [Frozen certificate and checker](chains/p384/verify_frozen_421.py) |
| Curve25519 prime-subgroup scalar `l−2` | **279 = 247S + 32M** | 2017 284; dated `addchain` 283 | [Certificate and two replayers](chains/targets/curve25519/frontier/README.md) |

`S` means squaring; `M` means another multiplication. These comparisons use abstract operation counts for the **same target**, not native timing. Run `python -B chains/verify_all.py` after cloning; it returns `PASS_LOCAL_ARITHMETIC_ONLY`. The [reviewer guide](REVIEWER_GUIDE.md) gives the commands, and [limitations](LIMITATIONS_AND_UNKNOWN.md) states the claim boundaries once. [Release hashes](PUBLIC_SHA256SUMS.txt) and [changes](CHANGELOG.md) identify these exact files.
