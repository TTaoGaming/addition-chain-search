# Addition-chain search: checkable results and methods

This project is a small, inspectable record of Tommy Tai's AI-assisted search following [Brian Smith's public 2017 P-384 addition-chain article](https://briansmith.org/ecc-inversion-addition-chains-01). Brian has not reviewed or endorsed these results.

## Two-minute read

1. **Check the strongest result.** The frozen P-384 scalar `n−2` certificate has **421 operations: 380 squarings and 41 other multiplications**. It is 12 below the article's 433 count and nine below a pinned-source `ring` recount of 430. Run `cd chains && python -B verify_all.py` to replay the arithmetic and negative controls. This is an operation-count result, not measured native speed or a proof of the shortest possible chain.
2. **See how the search was recorded.** [HISTORY](chains/HISTORY.md), [EXPERIMENTS](chains/EXPERIMENTS.md), and [METHOD](chains/METHOD.md) explain selected 425→421 checkpoints, different constructions, and bounded negative searches. The September 24 CPU annealing run produced the frozen 421. Its selected source and genotype survive privately, but the six original per-seed logs are missing from this project. These checkpoints are not one proven mutation lineage.
3. **Inspect the later evolutionary case separately.** [The OpenEvolve case](openevolve-case/README.md) starts from a *different* 421 certificate, 381S+40M. Run `cd openevolve-case && python -B replay_ledger.py --selftest`. Its 17 reported children yielded nine distinct certificates; the best generated child was 425, so the seed remained best. This local ledger replay does not authenticate omitted model traces or show that OpenEvolve discovered the frozen CPU-annealed 421.

The [five MIT-licensed portable agent skills](skills/README.md) describe the verification, search, cost, frontier-reporting, and packaging workflow. Their [reuse terms](skills/REUSE_TERMS.md) are separate from the chain archive's MIT and third-party notices. The OpenEvolve case is available for review only. Read [limitations](LIMITATIONS_AND_UNKNOWN.md) before reusing any result.

For deeper context, see [intermediate results and receipts](INTERMEDIATE_RESULTS_RECEIPTS.md) and [search process and failures](RESEARCH_METHOD_AND_FAILURES.md). Those notes distinguish replayable certificates, reported aggregates, bounded negative searches, and unknowns.

Tommy chose targets, search direction, and timeboxes; agents implemented and ran many experiments. The durable record and automatic resource allocation are still incomplete. Neither a model suggestion nor a scheduled wake counts as a verified improvement without a checker and a bound receipt.
