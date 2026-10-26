# Primary behavior-ablation figures

These standalone figures use the frozen [primary JSON](../analysis/PRIMARY_RESULTS.json), [CSV](../analysis/PRIMARY_RESULTS.csv), and [independent audit](../oracle/PRIMARY_AUDIT.v1.json). They cover `runs/v2` only. The earlier integration trajectory and exploratory browser transport attempts are excluded. Every plotted value is retained in [PLOT_DATA.json](PLOT_DATA.json); [render_primary.py](render_primary.py) exports PNG and editable-text SVG. Run `python -B plots/render_primary.py --render` from the project root. No installation or network is needed.

| Figure | Purpose and suggested caption |
|---|---|
| [Paired costs](primary_paired_costs.svg) · [PNG](primary_paired_costs.png) | **Best valid charged operation counts for all four task × replicate pairs in each contrast.** Negative differences are lower counts. Pair labels show exact control → treatment values; the open diamond retains the best valid prefix of a timed-out trajectory. Name-only framing and actual configured backend are separate contrasts. Relevant-versus-irrelevant memory (M−I) and order of the same facts (O−M) answer different questions. |
| [Paired behavior](primary_paired_behavior.svg) · [PNG](primary_paired_behavior.png) | **Action changes do not imply cost changes.** The panels show exact-action/coarse-family changes, and signed changes in unique generator regions, duplicate candidate records, and realized exact evaluations for the same four pairs. Every exact action sequence changed, while many final costs tied. Color intensity has a separate scale in each count panel; printed values control the comparison. |
| [All raw trajectories](primary_raw_trajectories.svg) · [PNG](primary_raw_trajectories.png) | **All 40 planned trajectories, separated by task.** Each row shows the three decision positions, best valid charged cost, actual evaluation count, unique generator-region count, and duplicate/valid candidate numerator and denominator. The single timeout retains its valid first submission and marks the later unstarted decision. This is the main audit view when a summary sounds too broad. |
| [Completion and work](primary_budget_completion.svg) · [PNG](primary_budget_completion.png) | **The shared decision cap did not equalize realized search work.** Of 40 trajectories, 39 completed and one timed out; 119 decisions were attempted and 118 returned. All 3,098 evaluated candidate records were valid under the independent audit. Every task × replicate workload and duplication fraction is shown. The 192-evaluation line is only an upper bound of three decisions ×64 candidates, not a required workload. |

## Scope and definitions

The two exposed synthetic targets are 750339 (20 bits; binary baseline 28) and 7162463 (23 bits; baseline 35). The integer exponent base is 1, each addition is charged, and dead rows remain charged. A lower valid count in this pilot does not establish global optimality or improve a historical curve-domain witness.

`r1` and `r2` are repeat/order identifiers, not controlled model RNG seeds. There are **two tasks**, not 40 independent tasks. Identical baseline first prompts were supplied within each task/model repeat pair; all four whole action sequences nevertheless differed between repeats. Therefore the plots report descriptive paired observations without confidence intervals, significance tests, or general causal claims about learning.

| Cell | Actual condition |
|---|---|
| B | Neutral baseline; deterministic construction/search actions and candidate-visible verifier feedback available. |
| N | B with the identity-framing string `Apex Nidhoggr`. This does not make the controller an admitted Apex actor or establish participation by that actor. |
| S | B with a static operative skill packet. Additional instruction length is part of this treatment. |
| I | B with irrelevant memory prose. |
| M | B with relevant static memory. M and I have 96 words each; tokenizer-equivalent length is not claimed. |
| O | Same memory facts as M in a different paragraph order. |
| T | Construction/search tools absent; explicit chain submission remains available. |
| V | Candidate-visible verifier feedback withheld. The final exact evaluator remains the same; actions receive masked acknowledgment. |
| A | Exploratory bundle of name framing, skill and relevant memory. |
| Luna | Separate baseline configured as `gpt-6-luna`; other cells use `gpt-6.1-sol`. This is an actual backend setting, distinct from N's name string. |

The action grid uses SW=search window, SD=search dictionary, EX=explicit chain submission, CB=binary construction. The renderer does not reconstruct unseen decisions. The T/20b/r2 row has a valid 24-operation first submission, a decision 2 timeout, and unstarted decision 3. The timeout is included in raw pairs as a censored prefix, not silently counted as a completed three-decision result.

A region is exact generator method plus normalized knobs; explicit submissions are keyed by schedule identity. Candidate identity is a commutative parent-index schedule preserving row order, multiplicity and output node, **not** general DAG isomorphism. A duplicate is another valid record with an already-seen schedule identity inside its trajectory. Denominators are candidate records, not independent discoveries. No-candidate duplicate fractions would be undefined; every primary row has at least one valid record.

## What these figures support in Tao's own write-up

- Separate **observed behavior**, **valid arithmetic outcome**, and **proposed architecture**. This pilot is one proposal controller with deterministic inner search; it does not test a deployed eight-Apex system, persistent learning, or blackboard coordination.
- Say the skill and memory-order contrasts had four observed cost ties while their duplicate/region behavior changed. Avoid saying those components never matter: the sample is small and the model randomness is unmatched.
- The name-only contrast was lower by one addition on the23-bit task in both repeat positions and tied on the20-bit task. Because N is a prompt string and the baseline itself varies in actions, this is an observation to replicate, not evidence that an Apex persona caused a gain.
- Relevant versus irrelevant memory had three cost ties and one cost increase of one. That differs from testing memory presence versus absence; O−M tests only order of identical facts.
- Removing search/construction actions produced direct submissions with lower observed costs on the23-bit task while using far fewer evaluations. The20-bit pair includes a timeout. This exposes a useful mismatch between inner-search coverage and proposal quality, not a general verdict that tools harm search.
- Withholding feedback produced one worse20-bit result and three ties. The actual backend contrast had three results one operation higher for Luna and one tie; do not turn this into a general model ranking.
- Include the incomplete external attempt honestly: [browser lane receipt](../runs/browser-v1/BROWSER_LANE_RECEIPT.json) preserves the first captures, while the later [reconciliation receipt](../runs/browser-v1/RECONCILIATION_RECEIPT.json) corrects their interpretation. There were two substantive free-router sends and zero accepted controlled JSON actions. B's first Copy returned zero characters, but a late JSON body appeared during readback outside the browser horizon; provider-final emptiness was not established. V was stopped after 131.504 seconds, exceeding the strict120-second bound by11.504 seconds. Neither latest room showed active generation. No late body is pooled into the controlled results. This is transport/capture evidence, not a completed B/V math contrast, and is excluded from every primary plot.

The suggested captions are technical report support, not an email draft. No private correspondence is included.

## Frozen source pins and time meaning

The primary result was extracted at 2026-10-26T18:16:26Z; the independent audit observed at 18:21:42Z. These are extraction/audit clocks, not individual model execution times. Per-trajectory start/end clocks remain in PLOT_DATA. The rendering receipt has its own creation time. The protocol and amendments predate primary launch; the v1 interface mismatch remains excluded rather than repaired into v2.

| Source | SHA-256 |
|---|---|
| `analysis/PRIMARY_RESULTS.json` | `5d884748187c90fb7413a9ba17e65103955ea736ad142da26826945c93f75ac8` |
| `analysis/PRIMARY_RESULTS.csv` | `0cddea566120c3468b165dd782a6ecd11c4db1f9fc6d1b46ac1783ed0271f2bf` |
| `oracle/PRIMARY_AUDIT.v1.json` | `46cffc7c2c8a988446ac5c35ccd4e9a3289246a20f0504c08f17139a024ac7af` |

[FIGURE_RECEIPT.json](FIGURE_RECEIPT.json) pins the protocol, execution freeze, stimulus/interface/scope amendments, renderer, editable plot data and final outputs. [VISUAL_QA.json](VISUAL_QA.json) records the actual visual checks and remaining limits.
