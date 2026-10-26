"""Freeze fixed-source episode packets and matched memory assignments; no inference."""
from pathlib import Path
import json,hashlib,random,datetime
R=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def write(rel,data):
 p=R/rel
 if p.exists():raise SystemExit("refuse overwrite "+rel)
 p.parent.mkdir(parents=True,exist_ok=True)
 text=data if isinstance(data,str) else json.dumps(data,indent=2)+"\n"
 p.write_text(text,encoding="utf-8")
 b=p.read_bytes()
 return {"path":rel,"sha256":sha(b),"bytes":len(b),"words":len(text.split())}
protocol=json.loads((R/"PROTOCOL.v1.json").read_text())
pins=[];source_records=[]
for task in protocol["tasks"]:
 source_id=task["id"]+"__r1__B__sol"
 source=R/"runs/v2"/source_id
 rec=json.loads((source/"RUN_RECEIPT.json").read_text())
 assert rec["state"]=="COMPLETED"
 final=json.loads((source/"TRUSTED_FINAL.json").read_text())
 records=[]
 for p in sorted((source/"environment").glob("round-*.candidates.jsonl")):
  records += [json.loads(line) for line in p.read_text().splitlines() if line]
 summaries=[]
 for event in final["events"]:
  rs=[r for r in records if r["round"]==event["round"]]
  costs=[r["assessment"]["charged"]["operations"] for r in rs if r["assessment"].get("valid")]
  summaries.append({"action":event["parsed_action"],"status":event["status"],"refusal_reason":event["reason"],"evaluated_candidates":len(rs),"valid_candidates":len(costs),"best_charged_cost":min(costs) if costs else None})
 packet={"kind":"recorded_completed_search_episode","source_run":source_id,"exact_source_target":task["target"],"source_task":task["id"],"source_model":"gpt-6.1-sol","actions_and_summaries":summaries,"retained_best_candidate":final["best_candidate"],"retained_best_cost":final["best_local_assessment"]["charged"],"scope":"This is prior known work, not a new discovery. The source target is explicitly labeled; compare it with the current task before using the certificate."}
 pins.append(write("stimuli/episode-"+task["id"]+".txt",json.dumps(packet,indent=2)+"\n"))
 source_records.append({"task_id":task["id"],"source_run":source_id,"source_final_sha256":sha((source/"TRUSTED_FINAL.json").read_bytes()),"source_job_sha256":sha((source/"JOB.json").read_bytes()),"source_episode_best_cost":final["best_local_assessment"]["charged"]["operations"],"all_source_candidate_schedule_hashes":sorted({r["assessment"].get("canonical_schedule_sha256") for r in records if r["assessment"].get("valid")})})
pins.append(write("control/EPISODE_SOURCE_DENOMINATORS.json",source_records))
jobs=[]
for task in protocol["tasks"]:
 other=next(t for t in protocol["tasks"] if t["id"]!=task["id"])
 for rep in [1,2]:
  for cid,name,mem in [("W","same_target_episode","episode-"+task["id"]),("U","other_target_episode","episode-"+other["id"]),("C","cold_no_episode","none")]:
   cell={"id":cid,"name":name,"label":"neutral","skill":True,"memory":mem,"tools":True,"feedback":True}
   jobs.append({"id":task["id"]+"__r"+str(rep)+"__"+cid+"__sol","task":task,"replicate":rep,"cell":cell,"model":"gpt-6.1-sol"})
random.Random(202610261804).shuffle(jobs)
pins.append(write("control/MEMORY_RUN_ORDER.json",jobs))
runner=(R/"control/run_codex_v3.py").read_text().replace('ROOT/"runs"/"v2"','ROOT/"runs"/"memory-v1"').replace('stimuli/RUN_ORDER.json','control/MEMORY_RUN_ORDER.json')
guard=' if datetime.now(timezone.utc)>=STOP:\n  return None,{"state":"HORIZON_REFUSED_BEFORE_INVOKE","wall_s":0,"usage":{},"native_tool_events":0}\n'
runner=runner.replace('def invoke(model,prompt,out):\n','def invoke(model,prompt,out):\n'+guard)
runner=runner.replace(' with (out/"events.jsonl").open("w",encoding="utf-8") as stdout,',guard+' with (out/"events.jsonl").open("w",encoding="utf-8") as stdout,')
pins.append(write("control/run_episode_memory_v1.py",runner))
manifest={"schema":"recorded-episode-memory-freeze.v1","utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"before_live_calls":not (R/"runs/memory-v1").exists(),"fixed_source_selection":"Primary v2 Sol baseline replicate1 for each task; all3 action records; no source selected by score.","source_validation":"Await full independent primary audit before memory launch.","pins":pins,"planned_trajectories":len(jobs),"planned_model_decisions":36,"novelty_denominator":"Every valid canonical index-schedule hash from each full source episode, not just visible retained-best file."}
write("control/EPISODE_MEMORY_FREEZE.v1.json",manifest)
print(json.dumps(manifest))

