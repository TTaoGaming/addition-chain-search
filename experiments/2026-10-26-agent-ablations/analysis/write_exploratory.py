import json
from pathlib import Path
from extract_primary import pair
R=Path(__file__).resolve().parents[1]
d=json.loads((R/"analysis/PRIMARY_RESULTS.json").read_text())
x=pair(d["rows"],"exploratory_relevant_memory_minus_none","M","B")
x["status"]="PREREGISTERED_EXPLORATORY_DERIVED_FROM_AUDITED_ROWS"
x["primary_rows_sha256"]="5d884748187c90fb7413a9ba17e65103955ea736ad142da26826945c93f75ac8"
(R/"analysis/EXPLORATORY_M_MINUS_B.json").write_text(json.dumps(x,indent=2)+"\n",encoding="utf-8")
print(json.dumps([p["cost_delta_treatment_minus_control"] for p in x["pairs"]]))

