# Search-history reconstruction

This package reconstructs **selected** search decisions and checkpoints. It is
separate from the [certificate and checker package](../chains/README.md):
replaying a final certificate checks its arithmetic, not the path that found it.

1. [P-384 checkpoints](P384_CHECKPOINTS.md) — preserved versus hash-matched
   reconstructed certificate bytes and reported UTC events.
2. [Search episodes](EPISODES.md) and [methods and bounded negatives](METHODS_AND_LIMITS.md)
   — regions tested, censored searches, and what the negatives do not prove.
3. [Intermediate results and receipts](INTERMEDIATE_RESULTS_RECEIPTS.md) and
   [decisions and failures](RESEARCH_METHOD_AND_FAILURES.md) — selected evidence
   and why the search direction changed.
4. [Search island map and resource ledger](ISLAND_MAP.md) — explored and open
   regions, observed UTC, measured or missing compute, and the operator's
   retrospective reason for starting with the tail.

**Evidence key:** included certificates pass local arithmetic replay; 424 and
423 bytes were reconstructed from recipes and matched to recorded hashes;
six-seed annealing totals are reported aggregates because the original raw
per-seed logs are absent here. The 425→421 rows came from different episodes,
not a proven direct mutation lineage. The frozen 421 came from CPU annealing,
not the later OpenEvolve case. No native speed, shortest-chain proof, complete
trajectory, or Brian endorsement follows from this reconstruction.

For offline browsing, extract `01_addition_chains_r4.zip` into a `chains/`
directory and `02_search_history_reconstruction_r2.zip` into a sibling
`search-history/` directory. Then the relative certificate links work; run the
checker from `chains/`. [Reuse terms](REUSE_TERMS.md): this reconstructed prose is
public for inspection only, with no reuse license granted. Private logs and
correspondence are not included.
