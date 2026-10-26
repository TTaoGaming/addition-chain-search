import json
from pathlib import Path
p=Path(__file__).resolve().parent/"PRIMARY_RESULTS.json"
d=json.loads(p.read_text())
out={"totals":d["totals"],"contrasts":[],"baseline_repeats":d["baseline_repeat_diagnostic"]}
for c in d["contrasts"]:
 pairs=c["pairs"]
 out["contrasts"].append({"contrast":c["contrast"],"cost_deltas":[p["cost_delta_treatment_minus_control"] for p in pairs],"cost_pairs":[[p["cost_treatment"],p["cost_control"]] for p in pairs],"action_changes":sum(p["action_sequence_changed"] for p in pairs),"family_changes":sum(p["action_families_changed"] for p in pairs),"states":[[p["treatment_state"],p["control_state"]] for p in pairs],"evaluation_deltas":[p["evaluations_delta"] for p in pairs],"duplicate_deltas":[p["duplicates_delta"] for p in pairs]})
print(json.dumps(out,indent=2))

