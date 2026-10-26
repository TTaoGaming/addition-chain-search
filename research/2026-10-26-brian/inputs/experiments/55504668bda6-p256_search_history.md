# P-256 search history and remaining questions

The selected certificate has 284 operations. This page explains the route to it and the limits of the follow-on search. It is a condensed reconstruction, not a complete raw trajectory or proof that every checkpoint directly descended from the preceding one.

## Milestones

1. **291 = 254S + 37M:** the earlier public project certificate improved the dated 292 article, but did not beat ring's stronger 289. That distinction corrected the search baseline. The [earlier certificate](../../chains/targets/p256/candidate.json) remains available.
2. **288, then two routes to 287:** reconstructed experiments used positive overlapping-digit recoding with a paid helper 315 = 92 + 223, and equal-cost dictionary rewrites that exposed helper 37. The first positive-control dictionary already contained 37, so enumeration was not shown necessary to discover that improvement.
3. **286 then 285:** a combined positive-prefix mutation and carry-tail scorer reported improvements at evaluations 42,486 and 238,703. A later diversity check found 256 elite encodings represented just two arithmetic DAGs. Encodings should therefore not be counted as independent structural diversity.
4. **Alternative 285 families:** factor targets E = 51Q + 164 and E = 771Q + 389 gave **285 = 253S + 32M**. Both exact certificates are [included](history/alternative_certificates/) and replayed by `verify.py`. They use one fewer multiplication than the 284, but two more squarings; runtime ranking can depend on the backend.
5. **284 using a paid scaffold value:** the selected construction builds 8415 = 255 + 8160, reusing 8160 from the already charged scaffold. It has an 11-row prefix to 255, one additional paid helper, and 20 tail additions. Row 136 is numerically smaller than the previous row but uses earlier parents; a legal topological schedule need not be monotonically increasing.

The 288–286 checkpoints and discovery-process budgets above are reconstructed historical reports. Their complete trajectories are not bundled here. The stronger, independently reproducible evidence in this directory is the terminal 284 certificate, two alternative 285 certificates, generated ring patch and direct tests. This account does not establish which search decision was causally necessary.

## Three bounded searches starting from 284

The follow-on runs held the high scaffold fixed and used paid helper mutations with carry-DP tail scoring. They tested **420 helper genomes**, representing **397 distinct canonical DAGs** across all rounds; every emitted certificate was exactly checked. The best remained 284, with no chain of 283 or fewer found.

| Round | Genomes | Distinct DAGs in round | Search wall seconds | Best |
| --- | ---: | ---: | ---: | ---: |
| 1 | 17 | 17 | 2.074 | 284 |
| 2 | 257 | 256 | 30.280 | 284 |
| 3 | 146 | 146 | 33.788 | 284 |

Total search wall time was 66.143 seconds, child-process CPU 63.565 seconds and Python CPU 2.567 seconds. These exclude setup, source recovery, coding, compilation and reporting. Per-round distinct counts overlap; they must not be summed as the across-round count. The compact [run summary](search_summary.json) preserves budgets and outcomes. Full candidate populations and search programs are not in this minimal review page, so these search counts are reported observations rather than independently rerunnable experiments here.

Neutral variants paid for 8925 = 8415 + 510 and reduced tail additions from 20 to 19; further helpers 16575 or 8927 reduced them to 18. Their construction cost canceled those tail savings. They do not improve the operation-count record.

## Explored regions and limits

- Earlier finite dictionary and value-union searches only closed their frozen value sets, parent choices and depth bounds. They do not rule out new helpers or scaffolds.
- Carry DP is exact for its fixed dictionary's tail objective. Choosing a single tied tail trace is not an exact optimization of the total shared helper ancestry.
- Larger helper universes and a partially processed unrestricted-prefix search did not have recovered complete terminal evidence. Those questions remain open.
- Native scheduling, register pressure and backend costs can change the ranking of equal-count chains. The present patch uses the original 284 throughout its paired comparison.

## Useful next experiments

1. Jointly optimize helper ancestry and all nondominated carry-tail states on a small new bank.
2. Freeze a value union containing the 284 and both different 285 families before an exact bounded minimum-DAG query. Treat timeouts as unknown.
3. Explore coordinated prefix, helper and scaffold changes while measuring canonical DAG diversity, rather than repeating equivalent encodings.
4. Benchmark the different 285 cost points and neutral 284 schedules against the present native baseline before selecting by weighted operation count.

This search history supports these specific next experiments. It proves neither a global optimum nor an untried region in every other researcher's search.
