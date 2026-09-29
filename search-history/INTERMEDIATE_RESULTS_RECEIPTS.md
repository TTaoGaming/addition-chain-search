# Intermediate results and receipts

All P-384 rows below target the curve's subgroup-order **scalar** inverse exponent `n−2`, not the field-prime `p−2`. `S` is squaring and `M` is another multiplication. The receipt that a recipient can check is the bundled certificate plus its exact SHA-256 and an independent arithmetic replay; the dated discovery account is a separate historical claim.

| Selected result | S + M | Certificate SHA-256 | Historical checkpoint UTC | What is verifiable here |
| --- | --- | --- | --- | --- |
| 425 | 380S + 45M | `14da9fd3bfa7e3e615c78c5d6cf73dc0262ea3ff65eb29553be502de37f0df05` | Reported by Sep 10 15:25 | Valid live exponentiation DAG; not strictly increasing |
| 424 | 380S + 44M | `88c3ff1cb882db81e8cee4d48a62c1ac41b7f57a1f52dfa5473242b1fc54b1be` | Sep 23 01:31:01 | Strictly increasing; bytes reconstructed from recorded recipe and matched to historical hash |
| 423 | 381S + 42M | `179c160b79f4c953b1d4822e6ce922213db26993c604c6c79544efdb4acdf6f2` | Sep 23 13:25:29 | Strictly increasing; reconstructed bytes matched to historical hash |
| 422 | 382S + 40M | `5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70` | Sep 23 13:38:34 | Preserved exact certificate; strictly increasing |
| 421 | 380S + 41M | `844866b0703ef55ca41fc616a7226fe6d8aca3022ead18cdaec1e0911422e02e` | Sep 24 12:50:43 | Frozen exact certificate, separate checker, negative controls; selected genotype/source are retained privately |

For all five, extract `01_addition_chains_r4.zip` and run `python -B verify_all.py`; the `p384_history` and `p384_frozen_421` fields are the machine-readable replay. The selected 421 was reported from CPU annealing seed 101 at iteration 114144. The six-seed aggregate reported two seeds at 421, four at 422, 210 distinct valid 421 certificates and no ≤420. Those counts are **reported**, not reconstructible from the six original per-seed JSONL files in this packet. The selected genotype and frozen certificate survive; full run trajectories do not.

The headline progression omits two useful **same-count** search checkpoints. After the bundled 424 = 380S+44M, private receipts reported 424 = 381S+43M (SHA-256 `4160d226392689d73c833725fe5acdc733b78f0d0295e082b30a653b4d191014`) and then 424 = 382S+42M (SHA-256 `4ee56bbf2a2ec6e3f66961086257d4cf1268476f881d5da151bbd2a342ad08cb`). At an illustrative squaring cost of 0.8 multiplication, their costs are 347.8 and 347.6, versus 348.0 for the bundled 424. Their exact bytes are **not** in this archive, so those two rows are reported historical receipts, not recipient-replayable certificates. The subsequent 423 checkpoint used the 382S+42M frontier as its comparison. An earlier provisional 424 hash was corrected when a helper row had to be moved to make the chain strictly increasing; the bundled 424 hash above is the corrected one.

Other target experiments are in `01_addition_chains_r4.zip` in this history package under `METHODS_AND_LIMITS.md` and `EPISODES.md`. They have separate comparison domains: local P-256 291 is below the 2017 article's 292 but worse than the pinned `ring` 289 recount; secp256k1 290 ties the article; Curve448 **field** inversion ties its 460 baseline. P-521 and Curve25519 scalar candidates and bounded negative searches are included with their own checks. No blanket multi-chain improvement is claimed.

The separate `04_openevolve_p384_case_r3_public.zip` replays a **later** compact-genotype experiment: 17 reported children, nine distinct generated certificates, best generated 425, while the different 421-operation seed remained best. Run `python -B replay_ledger.py --selftest`; it checks ledger arithmetic, parent pointers, hashes, and tamper rejection. It does not authenticate omitted model responses or engine logs. One trace row is missing and explicitly labeled in that case study.

The chain archive also includes a later **different** 421 = 381S+40M certificate, SHA-256 `0a8c5bb288aefb494e64dfa793e9e9b8ca1e162dcbc6c79ae6a6015ee089b518`. Its illustrative 0.8S+M cost is 344.8 versus 345.0 for the frozen CPU-annealed 380S+41M certificate. Equal operation count does not imply equal runtime; no native timing claim follows from that weighting.

Public comparison: [Brian Smith, *ECC Inversion Addition Chains* (2017)](https://briansmith.org/ecc-inversion-addition-chains-01), P-384 scalar 433 = 381S + 52M. The included 421 is 12 fewer operations under the same arithmetic count convention. This is a certificate/count comparison, not a measured implementation speedup, optimality proof, or claim that Brian has reviewed it.
