# Primary addition-chain behavior pilot

This is a controlled pilot on two synthetic integer targets, not a claim about global optimality, cryptographic performance or a deployed Apex swarm.

## What actually ran

The frozen plan had40 trajectories: nine treatments on each of two targets with two replicate IDs using gpt-6.1-sol, plus four matched gpt-6-luna baselines. Each trajectory allowed three structured decisions and at most64 deterministic evaluations per search action. All native CLI tools, stored memories and delegation were disabled; the runner supplied the experimental search interface and feedback.

39 trajectories completed. One tools-off trajectory timed out on decision2 after retaining a valid24-operation incumbent. There were119 attempted model calls,118 returned calls and3,098 recorded candidate evaluations. All3,098 candidates and all40 final selections agree with a separately authored, pre-frozen exact-integer evaluator. No native-tool events occurred. Returned-call usage records total1,914,920 input tokens and77,704 output tokens; the timed-out call's usage is unknown.

The targets are750339 (binary baseline28) and7162463 (binary baseline35). Replicate IDs are not controlled model RNG seeds. The principal task count is two, not40 independent tasks.

## Observed quality differences

Deltas below are treatment minus control in the fixed order target20/rep1, target20/rep2, target23/rep1, target23/rep2. Negative means fewer charged operations.

| Treatment / control | Cost deltas | Interpretation within this pilot |
|---|---|---|
| Name-only Apex Nidhoggr / neutral |0,0,-1,-1| Two one-operation improvements on the23-bit task; no general persona or durable-agent advantage established. |
| Operative skill packet / baseline |0,0,0,0| All four final costs tied even though action details and duplicate counts changed. |
| Relevant training memory / irrelevant memory |0,0,+1,0| No quality win; one worse count. This tests a static15/31 training-example packet, not autonomous memory. |
| Reordered same facts / original order |0,0,0,0| Allocation details changed; final costs tied. |
| Search tools absent / available |0,0,-2,-2| Direct construction reached29 on the23-bit target versus baseline31. One20-bit run timed out with a valid partial24; keep its TIMEOUT flag. |
| All evaluator feedback withheld / supplied |+1,0,0,0| One worse count, three ties. Validity, cost and incumbent feedback were withheld together. |
| Combined name+skill+memory / baseline |0,+1,0,0| Exploratory bundle; cannot attribute the result to one component. |
| gpt-6-luna / gpt-6.1-sol baseline |+1,+1,0,+1| Sol returned lower costs in three pairs; Luna used fewer evaluations. This compares requested included model routes, not different vendors. |

The preregistered exploratory relevant-memory/no-memory contrast is0,0,0,-1, reported separately from the eight primary table contrasts.

## Behavior changed more often than yield

Exact action/parameter sequences differed in all four pairs of every reported contrast. That is not by itself evidence that each treatment caused a reliable improvement: repeated baselines also changed their full action sequences despite identical supplied first prompts. The two Sol baseline repetitions retained the same cost on each target; Luna differed by one operation on one target.

The useful distinction is between choosing different regions, spending different effort and finding a lower-cost valid witness. The skill packet changed parameters/duplicates without changing the four best costs. Static memory changed allocation with mixed quality. Name-only framing and model-route differences need broader task replication before a general conclusion.

The tools-off result is a useful counterexample to “more tools automatically means better search.” Tools-on still allowed direct chain submissions; those controllers chose the offered window/dictionary search interface. Tools-off forced direct construction and used more model work, including one timeout. The offered engine is bounded and does not cover every construction family. This does not show that tools in general are harmful.

All recorded candidates were valid in both feedback conditions. The study therefore does not establish that verifier feedback improved validity. It does show a small quality/allocation difference for the combined evaluator-feedback package. The independent final verifier is what establishes our knowledge that the returned chains are valid; that role remains separate.

## Evidence and limitations

- Raw table: PRIMARY_RESULTS.json and PRIMARY_RESULTS.csv.
- Independent audit: oracle/PRIMARY_AUDIT.v1.json, SHA46cffc7c2c8a988446ac5c35ccd4e9a3289246a20f0504c08f17139a024ac7af.
- Frozen primary table SHA5d884748187c90fb7413a9ba17e65103955ea736ad142da26826945c93f75ac8.
- The first integration run and prelaunch grammar/scope corrections remain separate; no silent pooling or deletion.
- Skill adds instruction length. Training-memory controls have96 words each but are not tokenizer-equivalent. API model randomness is not controlled. Matched decision/evaluation ceilings are not matched realized compute.
- Index-schedule identity preserves row order, multiplicity and output and normalizes parent commutation. It is not general graph-isomorphism canonicalization; a new hash alone is not a new mathematical discovery.

The separately preregistered shared-blackboard and recorded-episode memory experiments follow this pilot. Raw private emails and credential values are excluded from the research export.
