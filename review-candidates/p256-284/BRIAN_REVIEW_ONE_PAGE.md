# P-256 scalar inversion search episodes

**Result: 284 operations = 251 squarings + 33 other multiplications**, five fewer than **289 = 254S + 35M** in the [pinned ring implementation](https://github.com/briansmith/ring/blob/840167e18e4fa837eb48de46500454a616a15a6e/src/ec/suite_b/ops/p256.rs#L182-L287). The target is the scalar subgroup order minus two:

`E = ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc63254f`

Only exponent 1 is free. Every operation adds two earlier exponents; equal parents cost S, unequal parents M. The objective is S+M over the entire live dependency DAG, including helpers. Subtraction is excluded.

## Origins and working method

The initial menu reused earlier P-384 prefix/dictionary-plus-tail-DP work, secp256k1 positive carry recoding, and P-521 deletion/repair experiments. Literature intake compared [Cross Window and addition-sequence methods](https://arxiv.org/abs/2207.13276) and [ILP addition-sequence synthesis](https://arxiv.org/abs/2306.15002); it does not establish that either paper caused the winning construction. Agents proposed representations, implemented bounded programs and reviewed certificates. Numerical search used beam search, prefix-DAG mutation and exact carry DP, without a model call per candidate. The main family builds a structured high 128-bit scaffold and a positive, possibly overlapping low-128-bit digit expansion.

## Episodes and pivot triggers

Times are UTC. This is campaign chronology, **not established certificate-by-certificate ancestry**.

1. **Correct the comparator.** Local **291 = 254S+37M**, using helper 66, improved Smith's dated [292 = 254S+38M](https://briansmith.org/ecc-inversion-addition-chains-01#p256_scalar_inversion), but lost to ring's 289. The [addchain table's generated 294](https://github.com/mmcloughlin/addchain#results) is another separate comparator. The target became below 289.

2. **Broaden the prefix/window search.** By **September 29, 22:28**, a beam/DP campaign had **288 = 254S+34M**; distinct replay followed. Its reported 3,134,149 assessments include controls and repeats, not unique DAGs. The complete discovery trajectory is missing.

3. **Change resources without demanding a cheaper dictionary.** On **September 30, 05:00–05:10**, fixed-demand synthesis reported a 17-row minimum. Carry-aware overlap then reached **287 = 254S+33M**, paying for **315 = 92+223** and using 18 tail additions. Independently, whole-chain rescoring of equal-cost dictionaries exposed useful **37**: 12 of 36 ties reached 287. The first control already contained 37; exhaustive enumeration was not shown necessary.

4. **Optimize dictionary and tail jointly.** Simple 37/315 crossover and transferred dictionaries remained 287. Prefix-DAG mutation with carry-tail scoring found **286 = 253S+33M at 05:28**, evaluation 42,486: a 13-row prefix to 255, paid 47 and 20 tail additions. The same run found **285 = 252S+33M at 05:38**, evaluation 238,703: 12 prefix rows, no extra helper, 21 tail additions. A checkpoint-write error ended the run at 260,010 evaluations; saved certificates survived. A diversity audit found 256 elite encodings represented only two DAGs, prompting canonical-DAG retention.

5. **Test other representations.** Parallel ancestry-activation and exact-prefix routes produced other 285s. Factoring **E = 51Q+164** or **771Q+389** produced **285 = 253S+32M**. Finite recombination regions failed to improve; larger timed-out regions remained unknown. These families are not established parents of 284.

6. **Widen paid scaffold bridges.** At **06:29:58**, the exact-prefix bank with adapted carry DP found **8415 = 255+8160**, reusing already-charged 8160. Exact ancestry activation dropped optional 183. The resulting **284 = 251S+33M** comprises 11 prefix rows + 124 other scaffold rows + one helper + 128 tail squarings + 20 tail additions.

## Checks, compute and limits

Recovered Plan–Do–Study–Act checkpoints document scoped questions, budgets, solver checks against tiny oracles, malformed-certificate tests, and changes of search region after bounded failures. The [exact certificate](https://github.com/TTaoGaming/addition-chain-search/blob/c18e65b3a6127446f3fd9c61f4a7ef10627728a5/review-candidates/p256-284/adapter/candidate.json) and [checker](https://github.com/TTaoGaming/addition-chain-search/blob/c18e65b3a6127446f3fd9c61f4a7ef10627728a5/review-candidates/p256-284/adapter/check_chain_independent.py) verify exact E, earlier declared parents, full liveness and S/M counts; [reproduction instructions](https://github.com/TTaoGaming/addition-chain-search/blob/c18e65b3a6127446f3fd9c61f4a7ef10627728a5/review-candidates/p256-284/REPRODUCE.md) are included. Separate-code and different-model-family arithmetic replays followed; fresh replay passed 1,034 nonzero inverse bases. Certificate SHA-256: `46ba0fb4a02926e02aad7c51cb9c41225952a5549e4c0012964f2de5ad15d148`.

Measured CPU fragments: 288 wave **426.734 s**; 286/285 mutation run **664.25 s**; wide-helper assay **126.706 s**; factored-target campaign **3,391.418 s**. Accounting scopes differ; these are not an end-to-end total. Total agents, model calls/tokens, model compute, elapsed campaign time and monetary cost remain unknown.

A complete four-phase checkpoint sequence for every agent is not recovered. Full trajectories, neutral-287 bytes and the bridge between two recorded 288 hashes remain incomplete. Tested follow-ons found no sub-284 witness. No global optimum, algorithmic novelty or native-speed gain is established; [native signing measurements remain inconclusive](https://github.com/TTaoGaming/addition-chain-search/blob/c18e65b3a6127446f3fd9c61f4a7ef10627728a5/review-candidates/p256-284/TECHNICAL_REPORT.md).

