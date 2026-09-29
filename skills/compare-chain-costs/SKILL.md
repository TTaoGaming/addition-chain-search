---
name: compare-chain-costs
description: Compare exact addition-chain candidates with published or implementation baselines using matching exponents, pinned source versions, squaring/multiplication counts, and separately measured native timing. Use for ranking or novelty claims.
---

# Compare chain costs

First establish that both candidates compute the same field or subgroup
exponent, using exact target definitions. Pin the comparator's article or
implementation revision and observation date. Recount its operations from
source when possible; label a count copied from prose as reported, not
independently verified.

Show `S` and `M` separately. If one candidate has fewer `S` but more `M`,
present the Pareto tradeoff and any explicitly chosen weighted model. A lower
sum of operations does not itself establish a native speedup. For a speed
claim, benchmark both implementations in the intended library/hardware with
the same setup, whole workload, repeated controls, and uncertainty; keep
microbenchmarks separate.

Report ties and regressions plainly. A valid candidate worse than the pinned
implementation is a negative result, not an improvement over an older article.
If the comparator is missing or current-best status is unknown, say so.
Credit the source lineage rather than claiming a tied historical chain as new.
