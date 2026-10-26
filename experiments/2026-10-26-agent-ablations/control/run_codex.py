"""Included-Codex structured-proposal runner. Owns only runs/ and control receipts."""
import argparse,concurrent.futures,hashlib,json,os,subprocess,sys,time,threading
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STOP=datetime(2026,10,26,19,24,8,tzinfo=timezone.utc)
LAST_NEW=datetime(2026,10,26,19,12,tzinfo=timezone.utc)
PROFILE=json.loads((ROOT/"control/CODEX_PROFILE.json").read_text())
TEMPLATE=(ROOT/"stimuli/PROMPT_TEMPLATE.txt").read_text()
SCHEMA=ROOT/"stimuli/action.schema.json"
ENVIRONMENT=ROOT/"harness/v1/ac_environment.py"
LOCK=threading.Lock()
def now():return datetime.now(timezone.utc).isoformat()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
def progress(data):
 with LOCK:
  with (ROOT/"runs/PROGRESS.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps({"utc":now(),**data})+"\n")
def environment(args):
 r=subprocess.run([sys.executable,"-B",str(ENVIRONMENT),*args],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",timeout=30)
 if r.returncode:raise RuntimeError("environment failure: "+r.stderr[:1500]+" stdout:"+r.stdout[:1500])
 return json.loads(r.stdout)
def transform(p):
 typ=p["type"]
 if typ=="submit_chain":return {"type":typ,"steps":p["steps"],"output_index":p["output_index"]}
 if p["method"]=="binary":knobs={}
 elif p["method"]=="window":
  knobs={"widths":p["widths"],"variants":["fixed","sliding"]} if typ=="search" else {"width":p["width"],"variant":p["variant"]}
 else:
  knobs={"max_window_bits":p["max_window_bits"]}
  if typ=="search":knobs.update(base_digits=p["digits"],candidate_digits=p["candidate_digits"],max_added_digits=p["max_added_digits"])
  else:knobs["digits"]=p["digits"]
 a={"type":typ,"method":p["method"],"knobs":knobs}
 if typ=="search":a["max_evaluations"]=p["max_evaluations"]
 return a
def invoke(model,prompt,out):
 out.mkdir(exist_ok=False)
 (out/"prompt.txt").write_text(prompt,encoding="utf-8")
 args=[PROFILE["executable"],"exec","--ignore-user-config","--model",model,"--skip-git-repo-check","--ephemeral","--sandbox","read-only"]
 for flag in PROFILE["disabled_features"]:args.extend(["--disable",flag])
 for c in PROFILE["configs"]:args.extend(["-c",c])
 args.extend(["--json","--output-schema",str(SCHEMA),"-o",str(out/"answer.json"),"-"])
 dump(out/"REQUEST.json",{"model":model,"effort":PROFILE["reasoning_effort"],"started_utc":now(),"prompt_sha256":sha(prompt.encode()),"profile_sha256":sha((ROOT/"control/CODEX_PROFILE.json").read_bytes()),"schema_sha256":sha(SCHEMA.read_bytes()),"timeout_s":120,"automatic_retries":0})
 t=time.perf_counter()
 with (out/"events.jsonl").open("w",encoding="utf-8") as stdout,(out/"stderr.txt").open("w",encoding="utf-8") as stderr:
  proc=subprocess.Popen(args,cwd=ROOT,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,text=True,encoding="utf-8")
  try:proc.communicate(prompt,timeout=min(120,max(1,(STOP-datetime.now(timezone.utc)).total_seconds())))
  except subprocess.TimeoutExpired:
   proc.kill();proc.communicate()
   receipt={"state":"TIMEOUT","returncode":proc.returncode,"wall_s":time.perf_counter()-t,"ended_utc":now()}
   dump(out/"RECEIPT.json",receipt);return None,receipt
 events=[]
 for line in (out/"events.jsonl").read_text(encoding="utf-8").splitlines():
  try:events.append(json.loads(line))
  except json.JSONDecodeError:pass
 tools=[e["item"] for e in events if isinstance(e.get("item"),dict) and e["item"].get("type") not in ("agent_message","reasoning")]
 usage=next((e.get("usage",{}) for e in reversed(events) if e.get("type")=="turn.completed"),{})
 receipt={"state":"RETURNED","returncode":proc.returncode,"wall_s":time.perf_counter()-t,"ended_utc":now(),"usage":usage,"native_tool_events":len(tools)}
 if proc.returncode!=0:receipt["state"]="MODEL_FAILURE"
 elif tools:receipt["state"]="CONTAMINATED_NATIVE_TOOL_EVENT"
 elif not (out/"answer.json").exists():receipt["state"]="NO_ANSWER"
 else:
  try:
   raw=(out/"answer.json").read_bytes()
   answer=json.loads(raw)
   receipt["answer_sha256"]=sha(raw)
  except (ValueError,OSError):receipt["state"]="ANSWER_PARSE_FAILURE"
 dump(out/"RECEIPT.json",receipt)
 return (answer if receipt["state"]=="RETURNED" else None),receipt
def run(job):
 dest=ROOT/"runs"/job["id"]
 if dest.exists():
  return {"id":job["id"],"state":"EXISTING_SKIPPED_NO_RETRY"}
 if datetime.now(timezone.utc)>=LAST_NEW:return {"id":job["id"],"state":"HORIZON_NOT_STARTED"}
 dest.mkdir(parents=True)
 dump(dest/"JOB.json",job)
 progress({"id":job["id"],"state":"STARTED"})
 history=[]
 report={"id":job["id"],"state":"IN_PROGRESS","started_utc":now(),"rounds":[]}
 try:
  c=job["cell"]
  init=environment(["init","--output",str(dest/"environment"),"--task-id",job["task"]["id"],"--tools","on" if c["tools"] else "off","--feedback","on" if c["feedback"] else "off"])
  # Initial environment response is retained by root, not exposed as a hidden side channel.
  dump(dest/"INIT_RECEIPT.json",init)
  for index in range(1,4):
   if datetime.now(timezone.utc)>=STOP:
    report["state"]="HORIZON_PARTIAL";break
   memory_name="irrelevant.v2.txt" if c["memory"]=="irrelevant" else c["memory"]+".txt"
   memory=(ROOT/"stimuli"/memory_name).read_text() if c["memory"]!="none" else "(none)"
   prompt=TEMPLATE.format(label=c["label"],target=job["task"]["target"],baseline=job["task"]["binary_baseline"],tools="on" if c["tools"] else "off",feedback="on" if c["feedback"] else "off",skill=(ROOT/"stimuli/skill.txt").read_text() if c["skill"] else "",memory_kind="provided" if c["memory"]!="none" else "absent",memory=memory,round=index,history=json.dumps(history,separators=(",",":")))
   proposal,rec=invoke(job["model"],prompt,dest/("round-"+str(index)))
   report["rounds"].append(rec)
   if proposal is None:
    report["state"]=rec["state"];break
   action=transform(proposal)
   ap=dest/("action-"+str(index)+".json");dump(ap,action)
   feedback=environment(["act","--output",str(dest/"environment"),"--action-file",str(ap)])
   dump(dest/("feedback-"+str(index)+".json"),feedback)
   history.append({"action":action,"visible_feedback":feedback})
   dump(dest/"RUN_RECEIPT.json",report)
  else:report["state"]="COMPLETED"
  final=environment(["export","--output",str(dest/"environment")])
  dump(dest/"TRUSTED_FINAL.json",final)
 except Exception as e:
  report["state"]="RUNNER_OR_ENVIRONMENT_FAILURE";report["error"]=str(e)
 report["ended_utc"]=now()
 dump(dest/"RUN_RECEIPT.json",report)
 progress({"id":job["id"],"state":report["state"],"rounds_returned":sum(r["state"]=="RETURNED" for r in report["rounds"])})
 return {"id":job["id"],"state":report["state"]}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--limit",type=int,default=40)
 p.add_argument("--workers",type=int,choices=[1,2],default=1)
 p.add_argument("--model",choices=["gpt-6.1-sol","gpt-6-luna"])
 a=p.parse_args()
 if not ENVIRONMENT.exists():raise SystemExit("FROZEN_ENVIRONMENT_NOT_READY")
 jobs=json.loads((ROOT/"stimuli/RUN_ORDER.json").read_text())
 if a.model:jobs=[j for j in jobs if j["model"]==a.model]
 jobs=[j for j in jobs if not (ROOT/"runs"/j["id"]).exists()][:a.limit]
 (ROOT/"runs").mkdir(exist_ok=True)
 dump(ROOT/"control"/("LAUNCH-"+str(time.time_ns())+".json"),{"utc":now(),"job_ids":[j["id"] for j in jobs],"workers":a.workers,"runner_sha256":sha(Path(__file__).read_bytes()),"protocol_sha256":sha((ROOT/"PROTOCOL.v1.json").read_bytes())})
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
  for r in ex.map(run,jobs):print(json.dumps(r),flush=True)
if __name__=="__main__":main()

