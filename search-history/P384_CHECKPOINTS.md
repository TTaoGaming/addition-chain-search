# Selected P-384 scalar checkpoints

All rows target the P-384 **subgroup order `n - 2`**. Each included file is
replayed by `p384/verify_progression.py`; the frozen 380S + 41M 421 certificate
also has `p384/verify_frozen_421.py`. `S` means squaring and `M` means another
multiplication.

| Result | Arithmetic | Reported event or checkpoint (UTC) | Source and byte provenance | Verification and qualification |
| --- | --- | --- | --- | --- |
| [425](../chains/p384/certificates/p384_425.txt) | 380S + 45M | Replay reported **by** 2026-09-10 15:25 | Exact certificate present in a later Git commit authored 2026-09-21 21:13:57 UTC | Valid live exponentiation DAG; rows decrease, so this is not a strictly increasing addition chain |
| [424](../chains/p384/certificates/p384_424.txt) | 380S + 44M | Checkpoint reported 2026-09-23 01:31:01 | Exact bytes reconstructed from a recorded recipe and matched to its historical SHA-256 | Strictly increasing, local replay |
| [423](../chains/p384/certificates/p384_423.txt) | 381S + 42M | Checkpoint reported 2026-09-23 13:25:29 | Exact bytes reconstructed from a recorded recipe and matched to its historical SHA-256 | Strictly increasing, local replay |
| [422](../chains/p384/certificates/p384_422.txt) | 382S + 40M | Checkpoint reported 2026-09-23 13:38:34 | Exact certificate preserved | Strictly increasing, local replay |
| [421](../chains/p384/certificates/p384_421.txt) | 380S + 41M | Checkpoint reported 2026-09-24 12:50:43 | Frozen certificate preserved | Strictly increasing; separate frozen checker and negative controls |
| [421 variant](../chains/p384/later_candidate/p384_421_381S40M.txt) | 381S + 40M | Exact discovery time unknown in this snapshot; local replay observed 2026-09-28 | Exact certificate preserved | Strictly increasing; lower illustrative `0.8S + M` score, narrower review |

Other reported frontiers are **not certificate-replayable from this release**.
A predecessor 426 = 380S + 46M is recorded with candidate SHA-256
`565353709cba96a918ed307ba426da62dc4ee1dd962a3d41e5d536483ad5b83d`,
but its exact bytes are absent here. Two later same-count 424 variants were
reported at 381S + 43M (hash
`4160d226392689d73c833725fe5acdc733b78f0d0295e082b30a653b4d191014`)
and 382S + 42M (hash
`4ee56bbf2a2ec6e3f66961086257d4cf1268476f881d5da151bbd2a342ad08cb`).
Their illustrative `0.8S + M` scores are 347.8 and 347.6 versus 348.0
for the bundled 380S + 44M certificate. These figures come from historical
receipts; the verifier here does not validate the absent bytes or their
discovery times. An earlier 429 is mentioned in private context, but no
byte-bound certificate or trustworthy event time has been recovered into
this snapshot.

These are selected best-result checkpoints from different search episodes and
representations. They do **not** establish a complete candidate trajectory,
equal search budgets, or that each row descended by one mutation from the
previous row. The 425 reported replay time and the later exact-certificate
commit's author timestamp are different events. The 424/423 reconstruction is validated by
matching exact recorded hashes and a fresh arithmetic replay, not by a full
reproduction of the original search.

The published 2017 P-384 scalar reference is **433 = 381S + 52M** in
the public article *ECC Inversion Addition Chains*.
The included 421 = 380S + 41M schedule uses 12 fewer arithmetic operations;
the pinned `ring` implementation source at commit
`840167e18e4fa837eb48de46500454a616a15a6e` (`src/ec/suite_b/ops/p384.rs`)
recounts as 430 = 382S + 48M, a nine-operation comparison. Neither
comparison is a measured speedup or a claim of global optimality.
