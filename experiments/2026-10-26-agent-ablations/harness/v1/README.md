# Bounded addition-chain environment v1

Pure Python, standard library only. Candidate actions are JSON data. No model,
network, subprocess, generated-code execution or hidden-oracle read occurs here.
The independently supplied public targets are copied in `PUBLIC_TASKS.json`;
no other oracle file was copied.

The trusted runner creates one fresh environment per trajectory. All three
attempted actions, including refusals, consume decision rounds. Each explicit
submission evaluates one candidate; a construction/search action evaluates at
most64 candidates. Tool-generated candidate definitions and every actual
evaluation are saved. Invalid and duplicate candidates still count. Untested
configured definitions are recorded as censored, not evaluated.

## Python interface

```python
from ac_environment import Environment
env = Environment.create(output_dir, 'synthetic-20-v1',
                         tools_enabled=True, feedback_enabled=False)
feedback = env.act({'type':'construct', 'method':'binary', 'knobs':{}})
env = Environment.load(output_dir)  # a separate process may resume
trusted = env.trusted_export()      # runner only; never feed to candidate
```

`act` accepts original UTF-8 bytes, text, or a JSON-compatible dictionary.
Dictionary actions are canonically encoded. Full original model output remains
the root runner's responsibility; oversize actions preserve a bounded captured
prefix with a clearly scoped digest. `ACTION_CONTRACT.json` contains complete
examples. Optional `task_id` must match the environment.

## CLI interface

From the experiment root:

```text
python -B harness/v1/ac_environment.py init --output RUN_DIR --task-id synthetic-20-v1 --tools on --feedback off
python -B harness/v1/ac_environment.py act --output RUN_DIR --action-file ACTION_JSON
python -B harness/v1/ac_environment.py export --output RUN_DIR
```

`init` and `act` print one JSON candidate-visible response. In feedback-off
mode, `act` returns only `ACK`, opaque receipt ID, round and rounds remaining,
even for malformed/refused actions. Exact validity, costs, selected candidates,
file paths and timing are absent from that response. Tools-off refuses
construct/search; explicit submissions remain available. The root candidate
profile must have no filesystem/native-tool access. This is an I/O blinding
boundary on a shared filesystem, not an OS access-control claim.

`export` is privileged runner evidence. It provides the final explicit
`best_candidate` for the separate oracle, local assessment and action events.
Use the same independent final evaluation across all feedback conditions.
Final aggregation is identical in every cell: lowest total charged operations,
then M, then canonical index-schedule digest. It is harness selection, not an
agent inference. A trajectory without a valid candidate exports null.

## Arithmetic and tools

Base exponent1 is free. Parent-index pairs append exact positive sums. All
serialized rows are charged, including dead rows and rows after the declared
output. Repeated values are legal; equal values at different indices charge M
when different indices are used together. Submitted chains are never repaired
or pruned. Constructors compile only their own output ancestry and log the
resulting explicit schedule.

Binary uses left-to-right binary construction. Window tools support fixed or
sliding windows of widths1..6. Dictionary tools use explicitly chosen positive
digits1..63 and a bounded bit-window dynamic program; dictionary search varies
up to two additions to the digit set. These are bounded construction/search
heuristics, not minimum-chain solvers. Duplicate identity sorts commutative
index pairs and preserves row order, multiplicity and output; it is not full
graph-isomorphism canonicalization.

Raw events and candidate JSONL records are described in `RAW_EVENT_SCHEMA.json`.
The independent reviewer owns normalization into the budget oracle's event
format. Configured candidates, actual evaluations, model calls and provider
calls remain separate counts. Snapshot files and raw action/evaluation files
are append-only; release drift or a partial prior round holds resumption.

Run `python -B harness/v1/test_environment.py` for fresh controlled test
artifacts. Existing first results are preserved. The release receipt pins the
source and public task inputs before the experimental launch.
