# Public arithmetic task interface

Only this file and PUBLIC_TASKS.json are public candidate material. Evaluator source, private controls, outcomes and audit receipts stay outside candidate prompts and workspaces.

The tasks are synthetic-20-v1, exact target750339 (0xb7303), and synthetic-23-v1, exact target7162463 (0x6d4a5f). Public binary baselines are28=19S+9M and35=22S+13M respectively. The target-generation recipe and full binary schedules are in PUBLIC_TASKS.json. These are session-generated tasks, with no claim of global optimality or absence from model pretraining.

Submit JSON data: `{"type":"submit_chain","task_id":"synthetic-20-v1","steps":[[0,0],...],"output_index":N}`. The illustrative ellipsis is not literal JSON.

Exponent e[0]=1 is free. Row k creates e[k+1]=e[a]+e[b] using indices0 through k. Parent indices must be exact nonnegative JSON integers; booleans/floats are invalid. Each row charges one operation: S iff a==b, otherwise M. Repeated exponent values are allowed, and equal exponent values at different indices still charge M when those two different indices are used together. All serialized rows are charged. Dead rows and rows after the selected output remain charged and are reported separately. The output index names any computed non-base node; if omitted it defaults to the last node.

Limits:1 to256 rows; candidate encoding at most65536 bytes. The selected node must equal the exact target integer, without modular reduction. Minimize total charged operations; S and M are retained separately.

The independent integration API is `evaluate_payload(payload, task_id)` or `evaluate_bytes(raw_bytes, task_id)` in the oracle evaluator. It returns state/arithmetic_valid, charged/live/dead counts, duplicate-value node indices, and exact schedule/signature hashes. It never executes candidate code. Construct actions belong to the harness and must yield explicit parent-index data before evaluation. Feedback policy controls which result fields candidates see.

Normalized budget-audit events have contiguous seq, unique event_id, kind (`model_round`, `construct_action`, `submit_action`, `candidate_evaluation`, `provider_call`), optional zero usd, and action_id on evaluations referencing an earlier action. Audit limits cover the corresponding plural counters, candidate_evaluations_per_action and usd=0. Normalization from the frozen raw harness log requires separate review; planned counts are not actual-event evidence.

Blinding is a prompt/tool-disabled boundary on a shared filesystem, not an OS access-control claim. Candidate processes must not receive oracle paths/source/controls or a filesystem tool. A tool-enabled candidate able to inspect oracle material requires an explicit contamination/blocker report.
