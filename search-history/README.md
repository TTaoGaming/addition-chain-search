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
per-seed logs are absent here. The 432, 429, and 426 source episodes are
reported history with no bundled certificates. The 425→421 rows came from
different episodes, not a proven direct mutation lineage. The frozen 421 came
from CPU annealing. Newer [P-521 581 and secp256k1 288 review candidates](../review-candidates/README.md)
sit outside the frozen chain ZIP and use a separate checker. See
[limitations](../LIMITATIONS_AND_UNKNOWN.md) for the evidence boundary.

For complete offline navigation, clone or download the **whole repository**;
from its root run `python -B chains/verify_all.py` and, separately,
`python -B review-candidates/verify.py`. The standalone history ZIP has only
the narrative, so links into `chains/`, `review-candidates/`, and root-level
documents need the full checkout. The frozen chains ZIP is independently
runnable; its current archive link is in the [project README](../README.md).
[Reuse terms](REUSE_TERMS.md): this reconstructed prose is public for
inspection only, with no reuse license granted. Private logs and
correspondence are not included.
