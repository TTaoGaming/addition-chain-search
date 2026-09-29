# Search process, negative results, and limits

## What the swarm actually did

- A human directed the target and larger search pivots. Agents built, checked, and recorded bounded search tools and certificates. The successful September 24 inner loop was a CPU annealer, **not an LLM generating every candidate**. It altered constructible prefix/intermediate exponents; a digit dynamic program evaluated tail constructions. A frozen arithmetic judge, not agent prose, selected candidates.
- Structured private checkpoints recorded target, method, seed/budget, selected certificate SHA-256, verifier state, and stalls. The recipient archives carry selected certificate bytes, not raw private discussion. `P384_CHECKPOINTS.md` marks reconstructed versus preserved bytes and distinguishes the historical discovery time from a later commit time.
- We tested restricted search neighborhoods and retained negative results. A fixed-prefix helper sweep was capped mid-region; later R10–R13 completed a different pinned-prefix one-helper region (20,488,942 states), R15 completed 16 selected two-helper pairs (9,429,312 states), and prefix-surgery enumeration also failed to yield a 420 in its defined region. These are not a global lower bound; details and caveats are in this history package's `METHODS_AND_LIMITS.md`.

## The decisions between the milestones

| Question or obstacle | Test and observation | Why the next move changed |
| --- | --- | --- |
| Can a cheap exact score replace subjective champion selection? | The 425 certificate was parsed against exact `n−2`; the inner score was validity, operation count and an illustrative `0.8S+M` weight. Heavier Python/Node/C++ checks were reserved for champions. A 1,828-dictionary small-prefix screen had no survivor at that point. | Keep the arithmetic judge fixed; search the low-192-bit tail and constructible digit dictionary together. |
| Can one extra helper buy a shorter tail? | A reported 424 used helper 301 and a 29-add tail. Its provisional row ordering was corrected for strict monotonicity without changing the 424 count. Same-count 424 variants then traded squarings against multiplications; exact bytes for those variants are absent from this release. | A lower weighted cost can matter even when total operations tie, but it must remain a separate, qualified claim. |
| Are small local helper changes enough for 423? | The logged local neighborhoods failed; one search enumerated 103,193 length-10-to-63 chains and screened helper neighborhoods without reaching the required tail threshold. This was a bounded negative, not a proof of impossibility. | Tao directed a nonlocal representation search instead of repeating the same island. |
| What changed at 423 and 422? | The 423 search enumerated exact 15-operation star prefixes to 4095 and scored them with downstream carry-DP. The 422 search used a different prefix and two helpers, reaching a 28-add low-192 tail. After 422, extra helpers improved tail counts but paid for themselves, leaving the total at 422 in the tested region. | Freeze the 422 certificate and vary the prefix dictionary jointly rather than assuming another local helper would pay off. |
| Can a CPU inner loop cross the 422 plateau? | A frozen judge and six-seed annealer found the selected 421 at seed 101, iteration 114144. The reported 210 valid 421 certificates formed two `(S,M)` families; none was ≤420. Original per-seed logs are missing from this packet. | The local prefix-dictionary move set appeared saturated; wider representation and independent verification became the next questions. |
| Does more annealing in the same family reach 420? | A later wider run reported about 240k evaluations and no 420. Two mis-tuned hot-temperature seeds drifted badly and were stopped, wasting about 40 core-minutes. | Preserve the failed budget and switch construction family instead of treating more compute as a plan. |

These rows synthesize dated private checkpoints. The recipient can replay the **included certificates**, but not the omitted raw historical search logs or unbundled same-count 424 variants.

## What we cannot honestly reconstruct yet

The six original September 24 CPU `anneal_seed{101..106}.jsonl` logs were not found in a bounded local search. They may exist in the original private WSL or container run directory. We retain the selected source, genotype, certificate, dated private checkpoints, and six-seed reported tally, but not every trial, exact evaluated denominator, or a complete historical trajectory. The 424/423 exact certificates are reconstructed by hash-matched recipes, not recovered original run logs. Do not infer equal compute budgets or a direct parent-child mutation chain from the 425→421 milestones.

The next technical test is a preregistered search region with an immutable judge, retained raw run logs, and independent replay. See [limitations](../LIMITATIONS_AND_UNKNOWN.md) for claim boundaries.
