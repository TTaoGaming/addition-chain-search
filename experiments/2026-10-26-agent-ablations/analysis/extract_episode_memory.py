"""Extract all planned primary cells, including failures/missingness. No inference."""
import argparse,csv,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
OUT=R/"analysis"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def row(job):
 p=R/"runs/memory-v1"/job["id"]
 rec=read(p/"RUN_RECEIPT.json") if (p/"RUN_RECEIPT.json").exists() else {}
 final=read(p/"TRUSTED_FINAL.json") if (p/"TRUSTED_FINAL.json").exists() else {}
 records=[]
 for f in sorted((p/"environment").glob("round-*.candidates.jsonl")):
  records += [json.loads(line) for line in f.read_text().splitlines() if line]
 events=final.get("events",[])
 rounds=rec.get("rounds",[])
 best=final.get("best_local_assessment")
 actions=[e.get("parsed_action") for e in events]
 region_ids=[]
 for e in records:
  region_ids.append(canonical({"method":e["method"],"knobs":e["knobs"]}) if e["method"]!="explicit" else "explicit:"+str(e["assessment"].get("canonical_schedule_sha256")))
 costs=[x["assessment"]["charged"]["operations"] for x in records if x["assessment"].get("valid")]
 jobcell=job["cell"]
 state=rec.get("state","RUNNING_NO_FINAL_RECEIPT" if p.exists() else "NOT_STARTED")
 result={
 "trajectory_id":job["id"],"task_id":job["task"]["id"],"target":job["task"]["target"],
 "replicate_id":job["replicate"],"cell_id":jobcell["id"],"cell_name":jobcell["name"],
 "model":job["model"],"state":state,"failure_or_censor_reason":rec.get("error"),
 "tools":jobcell["tools"],"feedback":jobcell["feedback"],"skill":jobcell["skill"],"memory":jobcell["memory"],
 "public_baseline":job["task"]["binary_baseline"],
 "best_valid_cost":best["charged"]["operations"] if best and best.get("valid") else None,
 "best_S":best["charged"]["S"] if best and best.get("valid") else None,
 "best_M":best["charged"]["M"] if best and best.get("valid") else None,
 "best_identity":best.get("canonical_schedule_sha256") if best else None,
 "best_live":best.get("live",{}).get("operations") if best else None,
 "best_dead":best.get("dead",{}).get("operations") if best else None,
 "attempted_rounds":len(rounds),"returned_rounds":sum(q["state"]=="RETURNED" for q in rounds),
 "environment_rounds":len(events),"action_sequence":actions,
 "action_family_sequence":[(a.get("type")+":"+str(a.get("method","explicit"))) if isinstance(a,dict) else None for a in actions],
 "region_sequence":region_ids,"realized_evaluations":len(records),
 "unique_regions":len(set(region_ids)),
 "valid_candidates":sum(bool(x["assessment"].get("valid")) for x in records),
 "invalid_candidates":sum(not x["assessment"].get("valid") for x in records),
 "refused_actions":sum(e.get("status")=="REFUSED" for e in events),
 "unique_schedule_count":len({x["assessment"].get("canonical_schedule_sha256") for x in records if x["assessment"].get("valid")}),
 "duplicate_candidates":sum(bool(x.get("canonical_schedule_duplicate")) for x in records),
 "native_tool_events":sum(x.get("native_tool_events",0) for x in rounds),
 "model_input_tokens":sum(x.get("usage",{}).get("input_tokens",0) for x in rounds),
 "model_cached_input_tokens":sum(x.get("usage",{}).get("cached_input_tokens",0) for x in rounds),
 "model_output_tokens":sum(x.get("usage",{}).get("output_tokens",0) for x in rounds),
 "model_reasoning_output_tokens":sum(x.get("usage",{}).get("reasoning_output_tokens",0) for x in rounds),
 "model_wall_s":sum(x.get("wall_s",0) for x in rounds),
 "search_cpu_s":sum(x.get("process_cpu_seconds",0) for x in events),
 "started_utc":rec.get("started_utc"),"ended_utc":rec.get("ended_utc"),
 "independent_validation":"AWAITING_FULL_ORACLE_AUDIT"
 }
 result["improvement_over_binary"]=result["public_baseline"]-result["best_valid_cost"] if result["best_valid_cost"] is not None else None
 result["duplicate_fraction"]=result["duplicate_candidates"]/len(records) if records else None
 result["aggregation_min_matches_records"]=(result["best_valid_cost"]==min(costs)) if costs else result["best_valid_cost"] is None
 return result
def pair(rows,code,treat,control,treat_model="gpt-6.1-sol",control_model="gpt-6.1-sol"):
 lookup={(r["task_id"],r["replicate_id"],r["cell_id"],r["model"]):r for r in rows}
 pairs=[]
 for task in ["synthetic-20-v1","synthetic-23-v1"]:
  for rep in [1,2]:
   t=lookup[(task,rep,treat,treat_model)];c=lookup[(task,rep,control,control_model)]
   usable=t["best_valid_cost"] is not None and c["best_valid_cost"] is not None
   pairs.append({"task_id":task,"replicate_id":rep,"treatment_id":t["trajectory_id"],"control_id":c["trajectory_id"],
    "treatment_state":t["state"],"control_state":c["state"],
    "cost_treatment":t["best_valid_cost"],"cost_control":c["best_valid_cost"],
    "cost_delta_treatment_minus_control":t["best_valid_cost"]-c["best_valid_cost"] if usable else None,
    "action_sequence_changed":t["action_sequence"]!=c["action_sequence"],
    "action_families_changed":t["action_family_sequence"]!=c["action_family_sequence"],
    "final_identity_changed":t["best_identity"]!=c["best_identity"] if usable else None,
    "unique_regions_delta":t["unique_regions"]-c["unique_regions"],
    "evaluations_delta":t["realized_evaluations"]-c["realized_evaluations"],
    "duplicates_delta":t["duplicate_candidates"]-c["duplicate_candidates"],
    "invalid_delta":t["invalid_candidates"]-c["invalid_candidates"]})
 return {"contrast":code,"treatment":treat,"control":control,"treatment_model":treat_model,"control_model":control_model,"pairs":pairs}

def normalized_candidate(c):
 if not isinstance(c,dict) or not isinstance(c.get("steps"),list):return None
 return canonical({"steps":[sorted(p) for p in c["steps"]],"output_index":c.get("output_index",len(c["steps"]))})
def main():
 jobs=read(R/"control/MEMORY_RUN_ORDER.json")
 rows=[row(j) for j in jobs]
 assert all(r["state"]=="COMPLETED" for r in rows),"MEMORY_NOT_ALL_COMPLETE"
 source={x["task_id"]:x for x in read(R/"control/EPISODE_SOURCE_DENOMINATORS.json")}
 primary=read(R/"analysis/PRIMARY_RESULTS.json")
 primary_best={task:min(r["best_valid_cost"] for r in primary["rows"] if r["task_id"]==task and r["best_valid_cost"] is not None) for task in source}
 primary_pools={task:set() for task in source}
 for job in read(R/"stimuli/RUN_ORDER.json"):
  for f in (R/"runs/v2"/job["id"]/"environment").glob("round-*.candidates.jsonl"):
   for line in f.read_text().splitlines():
    if line:
     q=json.loads(line)
     if q["assessment"].get("valid"):primary_pools[job["task"]["id"]].add(q["assessment"]["canonical_schedule_sha256"])
 for rr,job in zip(rows,jobs):
  current=source[rr["task_id"]];current_pool=set(current["all_source_candidate_schedule_hashes"])
  mem=job["cell"]["memory"];packet=None;supplied=None
  if mem!="none":
   packet=read(R/"stimuli"/(mem+".txt"));supplied=source[packet["source_task"]]
  records=[]
  for f in (R/"runs/memory-v1"/job["id"]/"environment").glob("round-*.candidates.jsonl"):
   records += [json.loads(l) for l in f.read_text().splitlines() if l]
  valid=[q for q in records if q["assessment"].get("valid")]
  hashes={q["assessment"]["canonical_schedule_sha256"] for q in valid}
  rr.update(current_target_source_incumbent=current["source_episode_best_cost"],
   full_primary_incumbent=primary_best[rr["task_id"]],
   source_pool_schedule_count=len(current_pool),
   strict_cost_improvement_over_current_source=rr["best_valid_cost"]<current["source_episode_best_cost"] if rr["best_valid_cost"] is not None else None,
   strict_cost_improvement_over_full_primary=rr["best_valid_cost"]<primary_best[rr["task_id"]] if rr["best_valid_cost"] is not None else None,
   current_source_schedule_overlap_evaluations=sum(q["assessment"]["canonical_schedule_sha256"] in current_pool for q in valid),
   current_source_unique_schedule_overlap=len(hashes&current_pool),
   distinct_schedules_outside_current_source=len(hashes-current_pool),
   distinct_schedules_outside_full_primary=len(hashes-primary_pools[rr["task_id"]]),
   best_is_current_source_schedule=rr["best_identity"] in current_pool if rr["best_identity"] else None,
   supplied_packet_source_task=packet["source_task"] if packet else None,
   supplied_packet_words=len((R/"stimuli"/(mem+".txt")).read_text().split()) if packet else 0,
   supplied_packet_bytes=(R/"stimuli"/(mem+".txt")).stat().st_size if packet else 0,
   evaluations_matching_supplied_retained_schedule=sum(normalized_candidate(q.get("candidate"))==normalized_candidate(packet["retained_best_candidate"]) for q in records) if packet else 0,
   direct_submissions_matching_supplied_retained=sum(q.get("method")=="explicit" and normalized_candidate(q.get("candidate"))==normalized_candidate(packet["retained_best_candidate"]) for q in records) if packet else 0,
   valid_overlap_with_supplied_episode=sum(q["assessment"]["canonical_schedule_sha256"] in set(supplied["all_source_candidate_schedule_hashes"]) for q in valid) if supplied else 0)
 contrasts=[pair(rows,"same_target_minus_other_target","W","U"),pair(rows,"same_target_minus_cold","W","C"),pair(rows,"other_target_minus_cold","U","C")]
 d={"schema":"episode-memory-results.v1","created_utc":datetime.now(timezone.utc).isoformat(),"rows":rows,"contrasts":contrasts,
  "totals":{"trajectories":len(rows),"completed":sum(r["state"]=="COMPLETED" for r in rows),"attempted_rounds":sum(r["attempted_rounds"] for r in rows),"returned_rounds":sum(r["returned_rounds"] for r in rows),"candidate_evaluations":sum(r["realized_evaluations"] for r in rows),"native_tool_events":sum(r["native_tool_events"] for r in rows),"model_input_tokens":sum(r["model_input_tokens"] for r in rows),"model_output_tokens":sum(r["model_output_tokens"] for r in rows),"strict_source_improvement_trajectories":sum(bool(r["strict_cost_improvement_over_current_source"]) for r in rows),"strict_full_primary_improvement_trajectories":sum(bool(r["strict_cost_improvement_over_full_primary"]) for r in rows)},
  "denominators":"All W/U/C for a task use same current-target source pool/incumbent. Supplied-packet copies are separate. New index-schedule hashes alone are not new mathematical graphs. Full primary best24/29 also reported; no global novelty claim.",
  "validation":"AWAITING_INDEPENDENT_MEMORY_AUDIT"}
 d["copy_semantics"]="Matching evaluations include deterministic-tool rediscovery; only the direct-submission field counts explicit submissions. Neither alone proves a model's copying mechanism or mathematical novelty. Provisional v1 broad-copy field was renamed before final audit."
 (R/"analysis/EPISODE_MEMORY_RESULTS.json").write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
 scalar=[k for k,v in rows[0].items() if not isinstance(v,(list,dict))]
 with (R/"analysis/EPISODE_MEMORY_RESULTS.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=scalar);w.writeheader();w.writerows({k:r[k] for k in scalar} for r in rows)
 print(json.dumps({"totals":d["totals"],"contrasts":[{"contrast":c["contrast"],"cost_deltas":[p["cost_delta_treatment_minus_control"] for p in c["pairs"]]} for c in contrasts],"by_condition":[{"condition":c,"costs":[r["best_valid_cost"] for r in rows if r["cell_id"]==c],"evaluations":[r["realized_evaluations"] for r in rows if r["cell_id"]==c],"matching_evaluations":[r["evaluations_matching_supplied_retained_schedule"] for r in rows if r["cell_id"]==c],"direct_submissions":[r["direct_submissions_matching_supplied_retained"] for r in rows if r["cell_id"]==c]} for c in ["W","U","C"]]},indent=2))
if __name__=="__main__":main()
