# Addition-chain search: results, history, and tools

Tommy Tai's AI-assisted research follows [Brian Smith's public 2017 addition-chain
article](https://briansmith.org/ecc-inversion-addition-chains-01). Brian has not
reviewed or endorsed this project.

## Start with one of three packages

| Package | Plain-language use | Download |
| --- | --- | --- |
| [1. Addition-chain results and checkers](chains/README.md) | Check the exact candidate chains, including P-384 scalar `n−2` at **421 = 380S + 41M**. | [ZIP](01_addition_chains_r4.zip) |
| [2. Search-history reconstruction](search-history/README.md) | See selected 425→421 checkpoints, an [island and resource map](search-history/ISLAND_MAP.md), failed regions, and missing records. | [ZIP](02_search_history_reconstruction_r2.zip) |
| [3. Agent skills](skills/README.md) | Reuse five MIT-licensed procedures, grouped into general search and addition-chain-specific checks. | [ZIP](03_agent_skills_r9_mit_public.zip) |

The search-history reconstruction is public for inspection only; its
[reuse terms](search-history/REUSE_TERMS.md) are distinct from the skills' MIT grant.

Optional fourth appendix: [a later OpenEvolve P-384 case](openevolve-case/README.md)
([ZIP](04_openevolve_p384_case_r3_public.zip)). It generated no improvement over
its different 421 seed and is public for inspection only, without a reuse grant.

The 421 certificate passes local arithmetic replay. These files do not establish
native speed, a shortest chain, a full raw search trajectory, or adoption in a
cryptographic library. Read the [limitations](LIMITATIONS_AND_UNKNOWN.md) and
the [release hashes](PUBLIC_SHA256SUMS.txt) before relying on a result.
