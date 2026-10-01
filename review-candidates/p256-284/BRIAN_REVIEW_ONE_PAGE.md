# P-256 scalar inversion in 284 operations

## Result

An addition chain computes inverses of nonzero scalars modulo the P-256 subgroup order in **284 operations: 251 squarings and 33 other multiplications**. This saves five operations against **254S + 35M** in the [pinned ring implementation](https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p256.rs#L182-L287). S denotes squaring; M denotes other multiplication.

The exponent is the subgroup order minus two:

`E = ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc63254f`

## Method and sources

Only exponent 1 is free. Each operation adds two previously computed exponents; subtraction is excluded. The objective counts every required operation, including helper powers.

The construction combines a structured high-128-bit prefix with a positive low-128-bit digit expansion. Digits may overlap, with carries handled by exact dynamic programming. Beam search and mutation change the prefix and available digits; complete-chain scoring includes their construction costs. Agents designed programs and checked results; numerical search ran without a model call per candidate.

Earlier P-384, secp256k1 and P-521 experiments supplied starting ideas. Literature reviewed included [Cross Window and addition sequences](https://arxiv.org/abs/2207.13276) and [integer-programming synthesis](https://arxiv.org/abs/2306.15002); neither is established as the source of the winning construction.

## Search chronology

Times are UTC, September 29–30, 2026. These are campaign milestones; complete parent-to-child chain ancestry was not recorded.

1. **Correct the baseline.** A local 291-operation chain improved the [older 292-operation result](https://briansmith.org/ecc-inversion-addition-chains-01#p256_scalar_inversion), but ring already used 289. [addchain's generated 294](https://github.com/mmcloughlin/addchain#results) is another separate comparator.

2. **Broaden prefix and window search.** By September 29, 22:28, beam search with dynamic programming reached **288 = 254S + 34M**. The original discovery trajectory remains incomplete.

3. **Change the available digits.** A finite synthesis model reported a 17-operation minimum for the old required digits. Around 05:08–05:10, two routes reached **287 = 254S + 33M**. Overlapping digits used the explicitly constructed helper **315 = 92 + 223** and 18 tail additions. Separately, changing the precomputed powers without reducing their construction cost exposed useful **37**. Twelve of 36 alternatives reached 287, but the first control already contained 37.

4. **Optimize prefix and tail together.** Combining those improvements stayed at 287. Joint mutation then found **286 = 253S + 33M** at 05:28 and **285 = 252S + 33M** at 05:38. The small-power prefix shortened from 13 to 12 operations; helper 47 disappeared. A checkpoint-write failure stopped this run, but certificates survived.

5. **Expand helper construction.** Parallel routes also reached 285, including **E = 51Q + 164** and **E = 771Q + 389**, each with 253S + 32M. Neither is a proven parent of 284. At 06:29:58, a search using enumerated prefixes constructed **8415 = 255 + 8160**, reusing previously computed 8160, and removed unnecessary 183. This gave **284**: 11 prefix operations, 124 further high-part operations, one helper, 128 tail squarings and 20 tail additions.

## Verification and limitations

The [certificate](https://github.com/TTaoGaming/addition-chain-search/blob/c18e65b3a6127446f3fd9c61f4a7ef10627728a5/review-candidates/p256-284/adapter/candidate.json), [independent checker](https://github.com/TTaoGaming/addition-chain-search/blob/c18e65b3a6127446f3fd9c61f4a7ef10627728a5/review-candidates/p256-284/adapter/check_chain_independent.py) and [reproduction instructions](https://github.com/TTaoGaming/addition-chain-search/blob/c18e65b3a6127446f3fd9c61f4a7ef10627728a5/review-candidates/p256-284/REPRODUCE.md) check the exact exponent, all parent references and S/M counts, and confirm every operation contributes to the output. Fresh replay passed 1,034 nonzero inverse bases.

Measured CPU fragments were 426.734 seconds for the 288 campaign, 664.25 for prefix mutation, 126.706 for wider helpers and 3,391.418 for factored targets. These differing scopes do not establish total compute; model calls, tokens, elapsed campaign time and costs remain unknown. Plan–Do–Study–Act logs and search histories are incomplete. No global optimality or algorithmic novelty is claimed; [native speed measurements](https://github.com/TTaoGaming/addition-chain-search/blob/c18e65b3a6127446f3fd9c61f4a7ef10627728a5/review-candidates/p256-284/TECHNICAL_REPORT.md) remain inconclusive.
