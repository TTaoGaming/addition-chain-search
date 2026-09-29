---
name: verify-addition-chain
description: Check an exact exponentiation addition-chain certificate for scalar or field inversion, including target identity, dependency arithmetic, operation counts, replay, and negative controls. Use when given a proposed chain, not as proof of speed or optimality.
---

# Verify an addition chain

Obtain the expected target/order and certificate digest from a trusted release
or independently pinned source; a candidate-supplied manifest is only a claim.
Bind the exact certificate bytes and SHA-256 before interpreting its claimed
count. Identify the curve, algebraic domain, modulus/order, and exponent:
`n−2` or `l−2` for a subgroup scalar, versus `p−2` for a field element.
Do not compare chains from different targets. See
[target and count terms](references/targets-and-counts.md) when terminology
is ambiguous.

Parse the certificate without executing untrusted code. Recompute every row
from previously defined parents, reject missing or forward references, and
check that the terminal exponent is the exact requested target. Trace live
dependencies so unused rows cannot silently improve the claimed cost.
Recount squarings (`S`, doubling an exponent) and other multiplications (`M`),
including declared precomputation. Replay modular exponentiation for several
fixed bases and compare with the trusted power operation where applicable.

Run at least one negative control that changes an edge or terminal target and
must fail; preserve its failure result. Return the target hash, certificate
hash, row count, `S/M` count, replay and mutation-control verdicts. This proves
bounded arithmetic validity only. Shortest-chain optimality, constant-time
behavior, native speed, and library integration need separate evidence.

For the adjacent chain release's `hfo.exponent_dag.v1` scalar JSON format,
`scripts/verify_scalar_dag.py` is an optional standard-library checker copied
byte-for-byte from that release (SHA-256
`af7b242af9fef34552f67c32df5f6c27c4bf258cce7ce632cdaa556964978d21`;
see this folder's `LICENSE`). It requires the exact manifest and candidate
SHA-256 on the command line. It does **not** parse the headline Curve25519
279/280 certificates, whose schema is
`curve25519.scalar_addition_chain.certificate.v1`; use the adjacent chain
release's `targets/curve25519/frontier/verify.py` for those. The P-384 425
history certificate also needs that release's `p384/verify_progression.py`
because its valid DAG is nonmonotone; do not force it through this checker.
The optional checker does not accept field `p−2` chains either. Its
`PASS_LOCAL_ARITHMETIC` output is conditional on
the supplied manifest and does not independently authenticate the curve,
order, release, or author.
