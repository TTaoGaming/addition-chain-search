-- Current generic offline projection; no private schema or live binding.
-- Pure SELECT: these sixteen rows inventory phase/cycle labels, not a serial runtime.
WITH hive(stage_order, stage) AS (
 VALUES (1,'Hindsight'),(2,'Insight'),(3,'Validated Foresight'),(4,'Evolution')
), pdsa(step_order, step) AS (
 VALUES (1,'Plan'),(2,'Do'),(3,'Study'),(4,'Act')
)
SELECT stage, step FROM hive CROSS JOIN pdsa
ORDER BY stage_order, step_order;
-- Evolution is the confirmed current phase name. Rows grant no authority.
