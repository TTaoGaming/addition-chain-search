# Third-party provenance

The Curve448 [baseline DAG](field/curve448/baseline.json) is an arithmetic
transcription of the `invert` function in
[ed448-goldilocks version 0.9.0](https://docs.rs/ed448-goldilocks/0.9.0/src/ed448_goldilocks/field/mod.rs.html#36-59).
The package metadata names Kevaundray Wedderburn as an author and declares
[`BSD-3-Clause`](https://docs.rs/crate/ed448-goldilocks/0.9.0/source/Cargo.toml).
The upstream Rust function is not copied into this release. The transcription
retains that attribution and license provenance; our MIT license does not
relicense the upstream implementation. The [BSD-3-Clause terms](THIRD_PARTY_BSD_3_CLAUSE.txt)
apply to the upstream work. We found no separate copyright notice in the
version 0.9.0 source listing and have not invented a holder or year.
The function's own comment credits
[mmcloughlin/addchain](https://github.com/mmcloughlin/addchain) for the
addition-chain construction; that contribution is also acknowledged here.

The [public 2017 article *ECC Inversion Addition Chains*](https://briansmith.org/ecc-inversion-addition-chains-01)
explains the secp256k1 scalar lineage: Pieter Wuille implemented an earlier
chain, Peter Dettman improved it with additional windows, and Brian Smith
then used further four-bit windows to obtain the published 290-operation
construction. The local certificate in this release ties that published
count; it does not claim novelty or ownership of that construction. The
other historical reference counts are also attributed to that article. No
upstream code from `ring`, Nettle, or the cited papers is included.
