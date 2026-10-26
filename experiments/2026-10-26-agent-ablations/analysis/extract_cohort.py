"""Path-qualified cohort accounting; copied initial work is counted once actual."""
from pathlib import Path
from datetime import datetime,timezone
import csv,json
R=Path(__file__).resolve().parents[1]
BASE=R/"runs/cohort-v1"
def read(p):return json.loads(p.read_text())
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def records(env,round_only=None):
 out=[]
 for p in sorted(env.glob("round-*.candidates.jsonl")):
  if round_only is not None and not p.name.startswith("round-"+str(round_only).zfill(2)+"."):continue
  out += [json.loads(s) for s in p.read_text().splitlines() if s]
 return out
def identity(q):return q["assessment"].get("canonical_schedule_sha256")
def region(q):return canon({"method":q["method"],"knobs":q["knobs"]}) if q["method"]!="explicit" else "explicit:"+str(identity(q))
def receipt(p):return read(p/"RECEIPT.json")
def main():
 rows=[];pairs=[];actual_calls=[];actual_records=[]
 for pair_dir in sorted(BASE.iterdir()):
  if not (pair_dir/"PAIR.json").exists():continue
  info=read(pair_dir/"PAIR.json");done=read(pair_dir/"PAIR_RECEIPT.json")
  task=info["task"];rep=info["replicate"]
  initial_records=[]
  for w in ["A","B"]:
   initial_records+=records(pair_dir/"initial"/w/"environment")
   actual_calls.append(receipt(pair_dir/"initial"/w/"model-round-1"))
  actual_records += initial_records
  initial_regions={region(q) for q in initial_records}
  branch_rows={}
  for arm in ["private","shared"]:
   workers={};second={}
   all_records=[]
   for w in ["A","B"]:
    env=pair_dir/arm/w/"environment"
    workers[w]=records(env);second[w]=records(env,2)
    all_records+=workers[w];actual_records+=second[w]
    actual_calls.append(receipt(pair_dir/arm/w/"model-round-2"))
   valid=[q for q in all_records if q["assessment"].get("valid")]
   best=min(valid,key=lambda q:(q["assessment"]["charged"]["operations"],q["assessment"]["charged"]["M"],identity(q))) if valid else None
   sets={w:{identity(q) for q in workers[w] if q["assessment"].get("valid")} for w in workers}
   secondsets={w:{identity(q) for q in second[w] if q["assessment"].get("valid")} for w in second}
   secondregions={region(q) for w in second for q in second[w]}
   second_calls=[receipt(pair_dir/arm/w/"model-round-2") for w in ["A","B"]]
   initial_calls=[receipt(pair_dir/"initial"/w/"model-round-1") for w in ["A","B"]]
   br=read(pair_dir/arm/"BRANCH_RESULT.json")
   rr={"pair_id":pair_dir.name,"task_id":task["id"],"replicate_id":rep,"arm":arm,"state":br["state"],
    "best_valid_cost":best["assessment"]["charged"]["operations"] if best else None,
    "best_S":best["assessment"]["charged"]["S"] if best else None,
    "best_M":best["assessment"]["charged"]["M"] if best else None,
    "best_identity":identity(best) if best else None,
    "branch_evaluations_including_common_initial":len(all_records),
    "unique_schedules":len(sets["A"]|sets["B"]),
    "duplicate_evaluations":len(valid)-len(sets["A"]|sets["B"]),
    "between_worker_schedule_overlap":len(sets["A"]&sets["B"]),
    "second_worker_schedule_overlap":len(secondsets["A"]&secondsets["B"]),
    "new_second_regions_over_team_initial":len(secondregions-initial_regions),
    "second_action_A":br["second_decisions"]["A"].get("action"),
    "second_action_B":br["second_decisions"]["B"].get("action"),
    "branch_accounted_model_calls":4,
    "branch_input_tokens_including_common_initial":sum(c.get("usage",{}).get("input_tokens",0) for c in initial_calls+second_calls),
    "branch_output_tokens_including_common_initial":sum(c.get("usage",{}).get("output_tokens",0) for c in initial_calls+second_calls)}
   rows.append(rr);branch_rows[arm]=rr
  s=branch_rows["shared"];p=branch_rows["private"]
  pairs.append({"pair_id":pair_dir.name,"task_id":task["id"],"replicate_id":rep,"state":done["state"],"shared_cost":s["best_valid_cost"],"private_cost":p["best_valid_cost"],"cost_shared_minus_private":s["best_valid_cost"]-p["best_valid_cost"] if s["best_valid_cost"] is not None and p["best_valid_cost"] is not None else None,"duplicate_evaluations_shared_minus_private":s["duplicate_evaluations"]-p["duplicate_evaluations"],"worker_overlap_shared_minus_private":s["between_worker_schedule_overlap"]-p["between_worker_schedule_overlap"],"new_second_regions_shared_minus_private":s["new_second_regions_over_team_initial"]-p["new_second_regions_over_team_initial"],"action_A_changed":s["second_action_A"]!=p["second_action_A"],"action_B_changed":s["second_action_B"]!=p["second_action_B"]})
 d={"schema":"paired-cohort-results.v1","created_utc":datetime.now(timezone.utc).isoformat(),"rows":rows,"pairs":pairs,
 "totals":{"pairs":len(pairs),"branches":len(rows),"actual_model_calls":len(actual_calls),"returned_calls":sum(c["state"]=="RETURNED" for c in actual_calls),"actual_candidate_evaluations_initial_once":len(actual_records),"sum_counterfactual_branch_evaluations":sum(r["branch_evaluations_including_common_initial"] for r in rows),"actual_model_input_tokens":sum(c.get("usage",{}).get("input_tokens",0) for c in actual_calls),"actual_model_output_tokens":sum(c.get("usage",{}).get("output_tokens",0) for c in actual_calls),"native_tool_events":sum(c.get("native_tool_events",0) for c in actual_calls)},
 "identity_scope":"Every record/event keyed by pair/arm/worker/path; cloned ordinal event IDs are not globally unique. Initial execution counted once actual; both counterfactual branches include it for their equal4-decision accounting. Schedule identity is not general DAG isomorphism.",
 "validation":"AWAITING_INDEPENDENT_COHORT_AUDIT"}
 (R/"analysis/COHORT_RESULTS.json").write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
 scalar=[k for k,v in rows[0].items() if not isinstance(v,(dict,list))]
 with (R/"analysis/COHORT_RESULTS.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=scalar);w.writeheader();w.writerows({k:r[k] for k in scalar} for r in rows)
 print(json.dumps({"totals":d["totals"],"pairs":pairs},indent=2))
if __name__=="__main__":main()

