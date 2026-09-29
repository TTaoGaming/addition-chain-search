---
name: run-evolutionary-search
description: Run a requested evolutionary optimizer on an exact target with a frozen evaluator, bounded resources, traceable generated candidates, and held-out validation. Use for an actual search run, not for a plan or a hand-picked candidate comparison.
---

# Run evolutionary search

First retrieve the existing engine/checkpoint locator for this target. Bind
its source revision, evaluator hash, run command, and access status. Reuse a
reachable prior engine; if it is inaccessible, record `SOURCE_UNAVAILABLE`
instead of claiming the work does not exist or silently rebuilding it. Choose
the engine the user requested. If none was named, choose an available engine
that fits the candidate representation and say which one you chose.
Before launch, freeze the target bytes and hash, incumbent, candidate grammar,
evaluator and its hash, score direction, train and held-out sets, model/provider
route if used, attempt/time/cost limits, output directory, and stopping rule.
Use [the experiment contract](references/experiment-contract.md) as a concise
record; it is not a substitute for the run. For every model-backed route,
including a free or local route, obtain a current admission/availability and
quota or resource-budget receipt before launch. Do not infer that a model name,
installed package, cached model, or old run means the route works now.

Make candidate evaluation independent of the proposer. Prefer data-only
candidates compiled by trusted code. If candidates contain executable code,
require an actual resource-bounded, credential-stripped execution boundary;
do not execute arbitrary generated code in the agent's ordinary workspace.
Keep held-out cases out of prompts, selection, and fitness. A missing safe
evaluator or unverified model route is a stop, not permission to swap in a toy
search while using the engine's name.

Run the engine under the frozen limits. Retain its invocation, version, seed,
model route, every generated candidate or hash, every validity verdict and
score, invalid proposals, and the selected parent/child lineage. Reconcile
trace rows against engine logs and checkpoints; a missing trace row is a
telemetry gap, not evidence that the iteration never produced a candidate.
Append a dated checkpoint before handoff: exact source/evaluator/candidate
hashes, configured versus actual evaluation counts, unique/valid denominators,
negative region, stop reason, and prior checkpoint superseded. Keep generator
source, selected genotype, certificate, and full run trajectory distinct;
recovering any one does not imply recovery of the others.
At least one distinct candidate must be generated and evaluated by the specified engine
for an `ENGINE_RAN` claim. Report `ENGINE_INVOKED` separately from
`DISTINCT_EVALUATED_CHILD`, because a process can run without performing a
useful search step. First use a one-candidate canary: confirm the model
reply reaches the engine's expected content field, its proposal syntax parses,
and the resulting candidate actually differs from the parent. Reject a patch
that matches nothing, a copied generic prompt example, or a child whose
normalized data/code is unchanged. An exit code, iteration counter, dependency
import, dry run, prompt, or manually shuffled variant list does not count.

After selection, replay the selected candidate with a distinct checker on
held-out cases. Compare it with the same-target incumbent under equal
evaluation budgets; record all negative or unchanged outcomes. Separate
arithmetic validity, local fitness, whole-workload speed, native speed,
deployment, and downstream acceptance. Report `ENGINE_NOT_RUN` only if the
engine was never invoked. If it ran but produced no distinct evaluated child,
report `ENGINE_INVOKED=YES`, `DISTINCT_EVALUATED_CHILD=NO`, and the exact failed
gate. Never edit the frozen evaluator to make a candidate pass.
Store the episode as evidence, a cross-episode lesson as a falsifiable claim,
and any reusable procedure as a versioned skill. The system has not learned
operationally until a later independent carrier retrieves the prior artifact,
uses the procedure, and leaves a new verifier/consumer receipt.
