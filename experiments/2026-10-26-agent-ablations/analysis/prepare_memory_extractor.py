from pathlib import Path
R=Path(__file__).resolve().parents[1]
prefix=(R/"analysis/extract_primary.py").read_text().split("def main():",1)[0].replace('R/"runs/v2"','R/"runs/memory-v1"')
body=r'''
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
   exact_copies_of_supplied_retained=sum(normalized_candidate(q.get("candidate"))==normalized_candidate(packet["retained_best_candidate"]) for q in records) if packet else 0,
   valid_overlap_with_supplied_episode=sum(q["assessment"]["canonical_schedule_sha256"] in set(supplied["all_source_candidate_schedule_hashes"]) for q in valid) if supplied else 0)
 contrasts=[pair(rows,"same_target_minus_other_target","W","U"),pair(rows,"same_target_minus_cold","W","C"),pair(rows,"other_target_minus_cold","U","C")]
 d={"schema":"episode-memory-results.v1","created_utc":datetime.now(timezone.utc).isoformat(),"rows":rows,"contrasts":contrasts,
  "totals":{"trajectories":len(rows),"completed":sum(r["state"]=="COMPLETED" for r in rows),"attempted_rounds":sum(r["attempted_rounds"] for r in rows),"returned_rounds":sum(r["returned_rounds"] for r in rows),"candidate_evaluations":sum(r["realized_evaluations"] for r in rows),"native_tool_events":sum(r["native_tool_events"] for r in rows),"model_input_tokens":sum(r["model_input_tokens"] for r in rows),"model_output_tokens":sum(r["model_output_tokens"] for r in rows),"strict_source_improvement_trajectories":sum(bool(r["strict_cost_improvement_over_current_source"]) for r in rows),"strict_full_primary_improvement_trajectories":sum(bool(r["strict_cost_improvement_over_full_primary"]) for r in rows)},
  "denominators":"All W/U/C for a task use same current-target source pool/incumbent. Supplied-packet copies are separate. New index-schedule hashes alone are not new mathematical graphs. Full primary best24/29 also reported; no global novelty claim.",
  "validation":"AWAITING_INDEPENDENT_MEMORY_AUDIT"}
 (R/"analysis/EPISODE_MEMORY_RESULTS.json").write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
 scalar=[k for k,v in rows[0].items() if not isinstance(v,(list,dict))]
 with (R/"analysis/EPISODE_MEMORY_RESULTS.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=scalar);w.writeheader();w.writerows({k:r[k] for k in scalar} for r in rows)
 print(json.dumps({"totals":d["totals"],"contrasts":[{"contrast":c["contrast"],"cost_deltas":[p["cost_delta_treatment_minus_control"] for p in c["pairs"]]} for c in contrasts],"by_condition":[{"condition":c,"costs":[r["best_valid_cost"] for r in rows if r["cell_id"]==c],"evaluations":[r["realized_evaluations"] for r in rows if r["cell_id"]==c],"supplied_copies":[r["exact_copies_of_supplied_retained"] for r in rows if r["cell_id"]==c]} for c in ["W","U","C"]]},indent=2))
if __name__=="__main__":main()
'''
p=R/"analysis/extract_episode_memory.py"
assert not p.exists()
p.write_text(prefix+body,encoding="utf-8")
print(str(p))

