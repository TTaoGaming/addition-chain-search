# Bounded search result and limits

Observed 2026-09-29 UTC. Separate private local run records report that three compact-genotype runs used OpenEvolve 0.3.2,
one worker, local Ollama `qwen3.5:2b-q4_K_M`, and a five-minute wall limit per
run. The engine/model are not bundled. The target was the P-384 scalar-order
`n−2` addition chain; the exact 421-operation seed (381S+40M) remains best.

Separate private local receipts, not bundled in this archive, recorded an
earlier attempt to evolve the full 421-row JSON certificate. Eight model
responses had no parseable diff because content was empty; a retry copied
the engine's generic Python example and changed zero chain bytes. This is
historical integration context, not independently reproducible from the
files in this ZIP. The compact genome was introduced so a model can propose
small, strict data and a trusted decoder can produce exact-target
certificates.

Offline, the compact seed reproduced 421 operations. From 109 deterministic
one-gene attempts, 100 distinct exact-target certificates independently
replayed at 422–428 operations. These are decoder feasibility controls, not
engine-generated improvements.

| Reported engine run | Budget | Distinct valid generated certificates in the sanitized ledger | Best generated count | Best overall |
| --- | ---: | ---: | ---: | ---: |
| `run_001` compact canary | 1 iteration | 1 | 426 | seed 421 |
| `run_002` original prompt | 8 iterations | 1, repeated eight times | 426 | seed 421 |
| `run_003` adjusted prompt | 8 iterations | 8 | 425 | seed 421 |

The [sanitized ledger](candidate_ledger.jsonl) gives every reported child in
all three runs, including the repeated all-255 genomes and parent pointers.
`python -B replay_ledger.py --selftest` independently replays each certificate,
checks the recorded count/hash, derives the nine-distinct total, and rejects
a tampered hash. The raw engine trace and checkpoint are not bundled, so this
is not independent proof that the engine generated those 17 rows. In
`run_003` the eight child genomes, in iteration order, were:

| Iteration | `bridge` | `ranks` | Operations | Certificate SHA-256 |
| ---: | ---: | --- | ---: | --- |
| 1 | 0 | `[30,31,29,33]` | 425 | `e5233b5427b09e8b854ca700316e066be2c7c7fa4c7a520777abb0aa4808cfc3` |
| 2 | 0 | `[63,62,61,60]` | 427 | `0e3f90103d0472325a69d0e47bc90ef383ae6f1f6ecf3f3c1ff65e82f44aa058` |
| 3 | 0 | `[15,63,9,63]` | 427 | `43cb17d8ae905f2fa79a5d748c5db1c114f9aecf187085206d6c20516814e961` |
| 4 | 0 | `[17,63,31,19]` | 426 | `025939d48468fa24c7c98c55e615e684c2c1eac8e66f1adc4c01ec54a1a6e184` |
| 5 | 0 | `[63,32,0,32]` | 426 | `a72ca7a861c30b4e9aa25bdcc30e4251286321c8b97798d8cb16b87b3687f5dd` |
| 6 | 0 | `[63,61,63,62]` | 426 | `7cb994deb42bfeb45500ac99ec91a99068d5b02825e5414a9bccc622abdc8e15` |
| 7 | 0 | `[63,63,63,63]` | 426 | `cc35319aabb1cce5dc6b340f395dccf71a91799913a8b40da7a68d04b6247ee6` |
| 8 | 1 | `[0,63,30,18]` | 426 | `2cc002cc923b27ea2fa9a96377936dcef98b1da14166a1ffa66c4c22aa11e65e` |

All eight were different from their parents, passed the exact-target decoder
and the separate certificate verifier, and were worse than the seed. The
adjusted prompt's diversity success is real, but its frozen telemetry gate
required eight trace rows and got only seven. Iteration 6 is present in the
engine log and final checkpoint, and its preserved program was independently
replayed. This is an explicit trace/checkpoint inconsistency, not an erased
or invented candidate. No native cryptographic benchmark or library adoption
was performed.

The private original run receipts, not included here, bind frozen inputs and raw trace hashes:
`run_001` trace `b34a072fb8035f085d9eba958fc79fdc353ff2912116279ef0ffd2ae5fd8ec1e`,
`run_002` trace `bcac67e397b647bc35d9daa3165ad5a00605bc48e1574861a1ab2d73ea426b76`,
`run_003` trace `a8b79094567dbb64af36a9746ea088117aa9ea1e5b57d2a11f4aeaefc192a5d8`.
Those raw logs are not in this recipient candidate. The local source files in
this package can reproduce the candidate arithmetic, but these text hashes
alone are not an independently verifiable public run log.

Verdict: named engine invoked; distinct candidates evaluated and independently
replayed; no improvement over 421; trace completeness held; speed,
optimality, and recipient use unknown.
