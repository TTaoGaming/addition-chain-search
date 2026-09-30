-- Current generic offline projection; no private schema or live binding.
-- Pure SELECT: these sixteen rows inventory phase/cycle labels, not a serial runtime.
WITH hive(stage_order, stage) AS (
 VALUES (1,'Hindsight'),(2,'Insight'),(3,'Validated_Foresight'),(4,'Evolve')
), pdsa(step_order, step) AS (
 VALUES (1,'Plan'),(2,'Do'),(3,'Study'),(4,'Act')
)
SELECT stage, step FROM hive CROSS JOIN pdsa
ORDER BY stage_order, step_order;
-- Evolve/Evolution spelling remains provisional. Rows grant no authority.
