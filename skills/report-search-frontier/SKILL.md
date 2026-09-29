---
name: report-search-frontier
description: Report a bounded search's regions, attempts, negative results, censoring, and certificate provenance without turning one replay into a discovery-history or optimality claim. Use after a search or when reconciling historical results.
---

# Report a search frontier

For each explored region, state its exact target, representation or grammar,
starting incumbent, search algorithm, seed, constraints, evaluation budget,
candidate count, stop reason, and best independently replayed artifact hash.
Keep complete sweeps distinct from time-, memory-, quota-, or error-censored
regions. An exhausted restricted grammar only rules out candidates *inside*
that grammar; it does not prove a global lower bound.

Separate three provenance layers: the generator/run log, the output
certificate, and the independent replay. A certificate that replays with no
recoverable generator still supports the arithmetic result, not reproduction
of its discovery. Retain failed and tied candidates; they bound what was
tried and prevent a selective success narrative.

When comparing a new region with prior work, match target bytes and scoring
rules before declaring progress. Mark unknown search coverage or unavailable
run logs `UNKNOWN`, with the smallest experiment or source needed to resolve
them. Deliver a compact table of complete, censored, and unrun regions, with
exact artifact pointers and UTC observations. Do not treat a planned search,
active agent, or imported optimizer as an executed region.
