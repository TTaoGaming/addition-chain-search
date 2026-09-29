# Inversion addition chains: certificates and selected search history

This release separates **scalar-order `n - 2`** schedules from a Curve448
**field-prime `p - 2`** assay. It contains selected exact candidate bytes,
hash-pinned target definitions, and offline checkers. Run the included checks
with Python 3 and its standard library:

```sh
python -B verify_all.py
```

The command exits nonzero on a failed check. Its `PASS_LOCAL_ARITHMETIC_ONLY`
result means that each included schedule reaches the stated exponent through
valid earlier-parent sums with the stated operation count. The scalar checkers
also check live dependencies and modular replay; the Curve448 field checker
replays its arithmetic on seven field vectors. The P-384 frozen checker and
target-family checkers include invalid-input controls. The 279/280 Curve25519
frontier has a second, optional Node.js replay:

```sh
cd targets/curve25519/frontier && node verify.mjs
```

This is an arithmetic result;
it is not a native speed, side-channel, optimality, or deployment result.

## Results in this snapshot

`S` is a squaring and `M` is another multiplication. Published historical
reference counts below come from the 2017 public article *ECC Inversion
Addition Chains*, which credits the earlier secp256k1 scalar work. Those
reference certificates are not bundled or independently replayed here. A
separate static recount of `ring` source at commit
`840167e18e4fa837eb48de46500454a616a15a6e`
provides a more recent comparison for P-256 and P-384. Counts from source are
not native timings.

| Scalar target | Included local candidate | Historical 2017 count | Other comparison / qualification |
| --- | --- | --- | --- |
| P-384 subgroup `n - 2` | **421 = 380S + 41M**; later 421 = 381S + 40M | 433 = 381S + 52M | Pinned `ring` P-384 source (`src/ec/suite_b/ops/p384.rs`) recount: 430 = 382S + 48M. The bundled 421 is arithmetic-replayed, not compiled into `ring`. |
| P-256 subgroup `n - 2` | **291 = 254S + 37M** | 292 = 254S + 38M | Pinned `ring` P-256 source (`src/ec/suite_b/ops/p256.rs`) recount: **289 = 254S + 35M**. The local 291 is worse than that implementation. |
| P-521 subgroup `n - 2` | **582 = 519S + 63M**; other 582 = 518S + 64M | No count in that article | Both local DAGs replay; order from [NIST SP 800-186](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf). No vetted current comparator here. |
| Curve25519 prime subgroup `l - 2` | **279 = 247S + 32M**; 280 = 249S + 31M; earlier 281 = 249S + 32M | 284 = 250S + 34M | Both newer schedules replay in Python and Node.js. A [dated `addchain` result](https://github.com/mmcloughlin/addchain/commit/b52645e520ab79ae83c2dcff2a9e90f59359e6a6) lists 283. This is **not** Curve25519 field `p - 2` or a current-best claim. |
| secp256k1 subgroup `n - 2` | **290 = 253S + 37M** | 290 = 253S + 37M | Local arithmetic DAG replay; **tie**, with no improvement or novelty claim. |

A separate [Curve448 field appendix](FIELD_CURVE448.md) replays a published
**460 = 447S + 13M** baseline and two narrowly declared split variants.
The best is a **tie**, not a lower chain, and its target is `p - 2`.

Newer [P-521 581 and secp256k1 288 review candidates](../review-candidates/README.md)
are outside this frozen `chains/` package and its MIT license. Run their
separate checker; they are not included in `01_addition_chains_r4.zip`.

## Open the certificates

- P-384: [425](p384/certificates/p384_425.txt) →
  [424](p384/certificates/p384_424.txt) →
  [423](p384/certificates/p384_423.txt) →
  [422](p384/certificates/p384_422.txt) →
  [frozen 421](p384/certificates/p384_421.txt), plus a
  [later 421 variant](p384/later_candidate/p384_421_381S40M.txt).
- [P-256 291](targets/p256/candidate.json),
  [P-521 582 519S+63M](targets/p521/candidate.json),
  [P-521 582 518S+64M](targets/p521/candidate_518S64M_source.json),
  [Curve25519 subgroup 283](targets/curve25519/candidate_283.json) →
  [282](targets/curve25519/candidate_282.json) →
  [281](targets/curve25519/candidate.json) →
  [280](targets/curve25519/frontier/curve25519_scalar_280.json) →
  [279](targets/curve25519/frontier/curve25519_scalar_279.json), and
  [secp256k1 subgroup 290](targets/secp256k1/candidate.json).

The P-384 380S + 41M certificate has SHA-256
`844866b0703ef55ca41fc616a7226fe6d8aca3022ead18cdaec1e0911422e02e`.
It has a [separate frozen checker](p384/verify_frozen_421.py) with four
negative controls, in addition to the [progression checker](p384/verify_progression.py).
The later 381S + 40M P-384 variant scores **344.8** rather than **345.0** under
the illustrative `0.8S + M` model; it has narrower local review and no
measured runtime claim.

See [HISTORY.md](HISTORY.md) for selected UTC checkpoints,
[EXPERIMENTS.md](EXPERIMENTS.md) for the PDSA-style search episodes, and
[METHOD.md](METHOD.md) for bounded search regions and unknowns.
[SHA256SUMS.txt](SHA256SUMS.txt) pins every release file except itself.
This is **not an exhaustive export of chat threads or search attempts**. The
original CPU-annealing generator and selected seed-101 genotype for the
frozen P-384 421 result were recovered in a private pinned Git branch, but
are not included here. The full six-seed raw logs were not recovered in this
archive. This repository verifies the *output*, not full reproduction of its
discovery. No result here establishes a shortest
chain, a general learned search policy, a speedup, or cryptographic adoption.
Three source-reference or search-grammar fields were sanitized for this release.
The original bytes and their hashes are retained privately. Arithmetic replay
binds the sanitized release bytes; those three files are not claimed to be
byte-identical to the original recorded evidence.

The original checker code and data authored for this bundle are offered under
the [MIT license](LICENSE). The source-derived Curve448 baseline has a
separate [third-party provenance notice](THIRD_PARTY.md) and included
[BSD-3-Clause terms](THIRD_PARTY_BSD_3_CLAUSE.txt); MIT does not replace them.
