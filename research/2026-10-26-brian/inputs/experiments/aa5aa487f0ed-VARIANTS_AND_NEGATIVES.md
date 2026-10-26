# P-384 side frontier and bounded negative regions (private)

These are separate from the five exact milestone certificates in `manifest.json`. A named hash or a search count is not, by itself, a full certificate or an optimality proof. Search statements below are historical reports in [Gen143 issue #169](https://github.com/TTaoGaming/hfo-gen-143/issues/169); this bundle did not rerun those searches.

## Same-length and later variants

| Candidate | `0.8S+M` | Exact SHA-256 or status | Source and present ceiling |
| --- | ---: | --- | --- |
| Initial 424 = 380S+44M | 348.0 | `88c3ff1cb882db81e8cee4d48a62c1ac41b7f57a1f52dfa5473242b1fc54b1be` | [Issue comment](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5787410277); exact certificate included and replayed here. Earlier `97b24e...` ordering was superseded because it was not strictly increasing. |
| 424 = 381S+43M | 347.8 | `4160d226392689d73c833725fe5acdc733b78f0d0295e082b30a653b4d191014` | [Issue comment](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5788078574); recipe and historical three-language checks reported, exact bytes not included here. |
| 424 = 382S+42M | 347.6 | `4ee56bbf2a2ec6e3f66961086257d4cf1268476f881d5da151bbd2a342ad08cb` | [Issue comment](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5788096860); weighted frontier improved, exact bytes not included here. |
| Another 424 = 382S+42M | 347.6 | `aa998bdb0041f26715bf76d645e90cb8671009806a1a0fcd5db9c4b9d1f9960e` | [Independent reconstruction report](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5788235126); same fitness class, different bytes; no byte-for-byte corroboration of `4ee56...`. |
| 423 = 381S+42M | 346.8 | `179c160b79f4c953b1d4822e6ce922213db26993c604c6c79544efdb4acdf6f2` | [Issue comment](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5795669973); exact certificate included and replayed here. |
| 423 = 382S+41M | 346.6 | Hash not located in scoped sources | [Gen5 terminal report](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5795965874) calls this a one-helper parent of 422. No full bytes or distinct replay in this bundle; **UNKNOWN**. |
| 422 = 382S+40M | 345.6 | `5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70` | Public PR3 and [issue comment](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5795874748); included and replayed here. |
| Public 421 = 380S+41M | 345.0 | `844866b0703ef55ca41fc616a7226fe6d8aca3022ead18cdaec1e0911422e02e` | Public PR5; included and replayed here. |
| Later private 421 = 381S+40M | 344.8 | `0a8c5bb288aefb494e64dfa793e9e9b8ca1e162dcbc6c79ae6a6015ee089b518` | [Private lineage checkpoint](../competition_packet_01a09bde/BRIAN_LINEAGE_PRIVATE_CHECKPOINT_20260928T183606Z.md) reports local replay on 28 Sep 11:38 UTC. Full bytes not included; do not replace public PR5. |

## What the failed islands actually tested

- **424 stage:** [Gen2 checkpoint](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5787462248) reports 91 direct one-helper sums, 136 pairs from 17 strongest mutants, 438 random two-step genotypes, and a 20,000-prefix probe. None produced 423 in those regions.
- **Fixed 63/4095 neighborhood:** [Gen3 report](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5788029768) reports 103,193 ten-operation chains to 63 and bounded helper/retained-ancestor tests, including all 24 length-10 chains to 255. This constrained topology became stiff; the result did not rule out other decompositions.
- **Weighted 424 neighborhood:** [Gen3 terminal report](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5788180428) reports 20,451 higher-doubling seeds, 20,000 optimal-tail backtracks yielding 1,985 unique tails, and helper/motif tests. None yielded 423 in those tested islands.
- **Independent 424 lineage:** [Gen4 report](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5788235126) reports 2,410 seeds, 4,279 direct-sum helper genotypes, 1,704 doubling-helper trials, 159 second helpers, and 142 one-helper sums; no improvement over its 424 frontier. [Short-seed report](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5788290218) reports 3,757 nine-operation and 87 eight-operation chains to 63, with bounded helper follow-up; none crossed its 423 boundary.
- **Nonlocal breakthrough:** [Gen5 report](https://github.com/TTaoGaming/hfo-gen-143/issues/169#issuecomment-5795965874) changed the representation, scored 748 exact 15-step star chains to 4095 and 3,622 valid 16-step insertion mutants by downstream tail cost, then found 423 and 422 through helper co-evolution. Third/fourth helper additions to the 422 winner were neutral; tested local stress bands yielded no 421. The later public 421 came from a different CPU search episode.

These are scoped search receipts, not a complete run-by-run log of every candidate, wall time, seed, CPU, or model call. The full search trajectory and equal-budget brute-force comparison remain **UNKNOWN** here.
