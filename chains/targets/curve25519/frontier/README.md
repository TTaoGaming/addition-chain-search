# Curve25519 prime-subgroup scalar frontier

These schedules compute `l - 2` for the Curve25519 prime-subgroup order.
They do not compute field-prime `p - 2`. `S` counts squares and `M` counts
other multiplications.

| Certificate | S | M | Total | Illustrative `0.8S + M` |
| --- | ---: | ---: | ---: | ---: |
| [279](curve25519_scalar_279.json) | 247 | 32 | 279 | 229.6 |
| [280](curve25519_scalar_280.json) | 249 | 31 | 280 | 230.2 |

The two schedules trade squares against other multiplications. They tie at
square weight `0.5`; 279 scores lower for weights above `0.5`. This cost
model is illustrative, not a measured hardware ratio. The public 2017
article *ECC Inversion Addition Chains* reports 284 for this exponent, and a
[dated `addchain` result](https://github.com/mmcloughlin/addchain/commit/b52645e520ab79ae83c2dcff2a9e90f59359e6a6)
lists 283. These are dated symbolic comparisons, not a current-best or native
speed claim.

From this folder, run both independent, read-only replayers:

```sh
python -B verify.py
node verify.mjs
```

They bind exact certificate hashes, source-plan hash strings, target exponent,
prior-parent arithmetic, strict increase, liveness, helper metadata, S/M
counts, modular inversion checks, and a corrupted-row negative control.
The included 279 is normalized from a mathematically valid raw search output
whose helper metadata still named one pruned row. The normalized certificate
has SHA-256 `3948e3c1692f1d863aa2d7d37246217ed4a2328b5fbec034d8f5f8e6aa6cb0b1`;
280 has SHA-256 `a3a1897b9eeb496cd4b8ac164b653e0c272afd16c8d4e6ad5ca9f402cfe9ca2a`.

The 280 region made 203,424 assessments in 92.969 process CPU seconds. A
different widened region made 291,558 assessments in 136.453 process CPU
seconds with no result below 280. The 279 region made 209,748 assessments
in 103.688 process CPU seconds. These are bounded search receipts;
proposal traces and generator source are not bundled. This folder proves
local arithmetic for the included exact certificates, not the process that
found them, global optimality, implementation speed, or adoption.
