# Public P-256 scalar chain comparison

Checked September 30, 2026, through 12:02:38 UTC. The exact target is the P-256 subgroup order minus two, `ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc63254f`. A squaring counts as one operation, as does another multiplication. Representation conversions and the cost of the backend are outside this addition-chain count.

## Result

The shortest external same-target chain directly verified in the sources checked is the pinned **ring chain at 289 = 254S + 35M**. The included **284 = 251S + 33M** certificate is five operations shorter. It is eight operations shorter than the 292-operation chain in the historical article and the pinned Go implementation. The included candidate is a project review result; this limited comparison does not establish a globally shortest chain or a public-record claim.

## Primary comparisons

- **ring: 289 = 254S + 35M.** [Pinned production source, lines 182–287](https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p256.rs#L182-L287). Recounted directly from the body: 6 standalone squarings plus 248 fused squarings; 12 standalone multiplications plus 23 fused multiplications. Source Git blob: `edd3548309824ea8f685480d660f5d7591184a1d`. This is the baseline that was actually built and benchmarked in this packet.
- **Brian Smith's 2017 article: 292 = 254S + 38M.** [P-256 scalar inversion section](https://briansmith.org/ecc-inversion-addition-chains-01#p256_scalar_inversion). The article explicitly reports this count; its title and historical best-known label are not a current record registry.
- **addchain: 294 generated; 292 listed as best-known hand-optimized.** [Project results table](https://github.com/mmcloughlin/addchain#results). Read on the date above; README Git blob `3b9e878344b5da49e97ee4a2d6bc4109988f228a`. This reports the project's published table, not a new run or an exhaustive capability bound. Its adjacent Curve25519 283/284 row is a different target.
- **Go: 292 = 254S + 38M at the checked revision.** [Pinned P256OrdInverse source](https://github.com/golang/go/blob/e4e6887ceefdd516fae86aa43b3410a2a0398394/src/crypto/internal/fips140/nistec/p256_ordinv.go#L9-L74). The source explicitly gives 38 multiplications and 254 squarings and attributes the chain to Smith's article. Git blob: `d1e58b202be003367bfc78236c98283fe66ca2d3`.

## Scope and limits

The web sweep used same-target phrases with 284, 283 and 289, plus the full hexadecimal exponent, and inspected the primary sources above. It did not recover a competing public certificate shorter than 284. Search coverage is limited: unindexed, unpublished, private, local-only or later results may exist. The strongest supported statement is that this verified 284 candidate improves on the inspected 289-operation ring implementation.

These counts do not rank all modular-inversion algorithms or predict signing speed. The actual ring tests and paired measurements are in `TECHNICAL_REPORT.md`: scalar inversion improved modestly in the recorded run; end-to-end signing remained inconclusive. The code, certificates, native test evidence, raw benchmarks and search history were unchanged for this comparison update. Private correspondence is not included.
