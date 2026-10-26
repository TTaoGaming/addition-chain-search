# Current replay findings

| Exact target | Original files | Exponent-equation signatures | Smallest retained count | S/M splits at that count |
|---|---:|---:|---:|---|
| p384 (subgroup scalar order) | 7 | 7 | 421 | 380S+41M, 381S+40M |
| curve25519 (subgroup scalar order) | 15 | 8 | 279 | 247S+32M |
| p521 (subgroup scalar order) | 11 | 8 | 581 | 516S+65M, 517S+64M |
| secp256k1 (subgroup scalar order) | 4 | 4 | 288 | 253S+35M |
| p256 (subgroup scalar order) | 83 | 28 | 284 | 251S+33M |
| curve448-field (field prime) | 1 | 1 | 460 | 447S+13M |

This is a collection minimum, not a shortest-chain proof or current-world-best census. Signatures normalize exponent equations and commutative parent order; raw bytes, topological schedules and resource identities remain separate.

The frozen manifest contains 121 files, 211 source-file aliases, and 56 distinct equation signatures. Two P-521 files retain two dead rows each. Every serialized row remains charged; no witness was repaired.

The two421 witnesses compute exactly the same P-384 scalar-order exponent. They use different DAGs and S/M compositions:380S+41M versus381S+40M. Function equivalence follows under the verified exponent-addition model; schedule identity, native speed and adoption do not follow.

Current primary replay: `verification/replay-20261026T153224-425600300.json`. Later versioned verification and distinct review must be read with their own receipts.
