"""Two-worker paired peer-observation pilot; candidates receive no branch labels."""
import concurrent.futures,hashlib,importlib.util,json,random,shutil,time
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("proposal_adapter",R/"control/run_codex_v3.py")
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
BASE=R/"runs/cohort-v1"
MODELS={"A":"gpt-6.1-sol","B":"gpt-6-luna"}
TEMPLATE="""You are one of two bounded addition-chain proposal controllers working toward the same team objective. Your stable worker label is {worker}. Native CLI tools are unavailable. Return only requested JSON data; do not read files, browse, execute code, delegate, or seek hidden evaluation material.
Task: exact integer target {target}, free e[0]=1, public binary baseline {baseline} charged operations. Every row [a,b] adds earlier nodes. S iff a==b, otherwise M. Charge every serialized row, including dead rows; repeated values are allowed. output_index selects a computed non-base node. Max256rows/65536bytes.
The team objective is the lowest exact valid charged cost over both workers' candidates. You have two decisions total. Search tools and exact validity/cost feedback are on. Each search request evaluates at most64 deterministic candidates. Every attempted action consumes a decision.
The same operative skill is supplied to every worker:
{skill}
Action grammar: submit_chain explicit steps/output_index; construct binary; construct window width1..6 variantfixed/sliding; construct dictionary unique integer digits1..63 including1 and max_window_bits1..6; search window nonempty unique widths1..6 with bothvariants; search dictionary unique base digits including1, candidate_digits1..63, max_added_digits0..2, max_window_bits1..6, max_evaluations1..64.
Use the common schema. Unused fields may take simple defaults (methodnone,width1,variantsliding,emptyarrays,max_added0,max_window_bits1,max_evaluations1,output_index0). Keep rationale under100words; rationale is not a candidate.
Decision {round} of2.
Your own prior action and candidate-visible feedback:
{own}
Other workers' observations supplied to you:
{peers}
Return one JSON action now.
"""
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+"\n",encoding="utf-8")
def pinfiles(folder):
 return {str(p.relative_to(folder)).replace("\\","/"):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob("*")) if p.is_file()}
def call(worker,task,folder,own,peers,index):
 if datetime.now(timezone.utc)>=adapter.STOP:
  return {"state":"HORIZON_REFUSED_BEFORE_INVOKE","receipt":{"state":"HORIZON_REFUSED_BEFORE_INVOKE","wall_s":0,"usage":{},"native_tool_events":0}}
 prompt=TEMPLATE.format(worker=worker,target=task["target"],baseline=task["binary_baseline"],skill=(R/"stimuli/skill.txt").read_text(),round=index,own=json.dumps(own,separators=(",",":")),peers=json.dumps(peers,separators=(",",":")))
 if datetime.now(timezone.utc)>=adapter.STOP:
  return {"state":"HORIZON_REFUSED_BEFORE_INVOKE","receipt":{"state":"HORIZON_REFUSED_BEFORE_INVOKE","wall_s":0,"usage":{},"native_tool_events":0}}
 proposal,receipt=adapter.invoke(MODELS[worker],prompt,folder/("model-round-"+str(index)))
 if proposal is None:return {"state":receipt["state"],"receipt":receipt}
 action=adapter.transform(proposal)
 ap=folder/("action-"+str(index)+".json");dump(ap,action)
 feedback=adapter.environment(["act","--output",str(folder/"environment"),"--action-file",str(ap)])
 dump(folder/("feedback-"+str(index)+".json"),feedback)
 return {"state":"RETURNED","receipt":receipt,"action":action,"visible_feedback":feedback}
def run_pair(task,rep,arms):
 pair=BASE/(task["id"]+"__r"+str(rep))
 if pair.exists():return {"pair":pair.name,"state":"EXISTING_SKIPPED_NO_RETRY"}
 pair.mkdir(parents=True)
 dump(pair/"PAIR.json",{"task":task,"replicate":rep,"arm_order":arms,"models":MODELS,"started_utc":datetime.now(timezone.utc).isoformat()})
 initial={}
 for worker in MODELS:
  f=pair/"initial"/worker
  init=adapter.environment(["init","--output",str(f/"environment"),"--task-id",task["id"],"--tools","on","--feedback","on","--max-rounds","2"])
  dump(f/"INIT.json",init)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
  futures={w:ex.submit(call,w,task,pair/"initial"/w,[],[],1) for w in MODELS}
  initial={w:f.result() for w,f in futures.items()}
 dump(pair/"INITIAL_RESULTS.json",initial)
 if any(x["state"]!="RETURNED" for x in initial.values()):
  result={"pair":pair.name,"state":"INITIAL_FAILURE_NO_RETRY","initial":initial};dump(pair/"PAIR_RECEIPT.json",result);return result
 state_pins={w:pinfiles(pair/"initial"/w/"environment") for w in MODELS}
 branches={}
 for arm in arms:
  if datetime.now(timezone.utc)>=adapter.STOP:
   branches[arm]={"state":"HORIZON_NOT_STARTED"};continue
  for worker in MODELS:
   source=(pair/"initial"/worker/"environment").resolve()
   dest=(pair/arm/worker/"environment").resolve()
   if not source.is_relative_to(R.resolve()) or not dest.is_relative_to((R/"runs").resolve()):raise RuntimeError("CLONE_SCOPE")
   if any(p.is_symlink() for p in source.rglob("*")):raise RuntimeError("CLONE_LINK_HOLD")
   dest.parent.mkdir(parents=True,exist_ok=True)
   shutil.copytree(source,dest)
   if pinfiles(dest)!=state_pins[worker]:raise RuntimeError("CLONE_BYTE_DRIFT")
  def branch_call(worker):
   peer="B" if worker=="A" else "A"
   own=[{"action":initial[worker]["action"],"visible_feedback":initial[worker]["visible_feedback"]}]
   peers=[{"worker":peer,"action":initial[peer]["action"],"visible_feedback":initial[peer]["visible_feedback"]}] if arm=="shared" else []
   return call(worker,task,pair/arm/worker,own,peers,2)
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
   futures={w:ex.submit(branch_call,w) for w in MODELS}
   results={w:f.result() for w,f in futures.items()}
  finals={w:adapter.environment(["export","--output",str(pair/arm/w/"environment")]) for w in MODELS}
  branches[arm]={"state":"COMPLETED" if all(v["state"]=="RETURNED" for v in results.values()) else "MODEL_FAILURE","second_decisions":results,"worker_finals":finals}
  dump(pair/arm/"BRANCH_RESULT.json",branches[arm])
 result={"schema":"two-worker-paired-pilot-receipt.v1","pair":pair.name,"state":"COMPLETED" if all(b["state"]=="COMPLETED" for b in branches.values()) else "PARTIAL","initial_state_file_pins":state_pins,"initial_calls_executed_once":2,"branch_order":arms,"branches":{k:{"state":v["state"]} for k,v in branches.items()},"ended_utc":datetime.now(timezone.utc).isoformat()}
 dump(pair/"PAIR_RECEIPT.json",result);return result
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument("--limit",type=int,default=4);p.add_argument("--dry-prepare",action="store_true");a=p.parse_args()
 tasks=json.loads((R/"PROTOCOL.v1.json").read_text())["tasks"]
 rng=random.Random(202610261753)
 jobs=[]
 for task in tasks:
  for rep in [1,2]:
   arms=["private","shared"];rng.shuffle(arms);jobs.append((task,rep,arms))
 if a.dry_prepare:
  dump(R/"control/COHORT_RUN_ORDER.json",[{"task":t,"replicate":rep,"arms":arms} for t,rep,arms in jobs])
  (R/"stimuli/COHORT_TEMPLATE.v1.txt").write_text(TEMPLATE,encoding="utf-8")
  print(json.dumps({"state":"PREPARED_NO_INFERENCE","pairs":len(jobs)}));return
 BASE.mkdir(parents=True,exist_ok=True)
 for task,rep,arms in jobs[:a.limit]:
  if datetime.now(timezone.utc)>=adapter.LAST_NEW:print(json.dumps({"state":"HORIZON_NO_NEW_PAIR"}));break
  try:print(json.dumps(run_pair(task,rep,arms)),flush=True)
  except Exception as e:
   result={"state":"RUNNER_FAILURE_NO_RETRY","task":task["id"],"replicate":rep,"error":str(e)}
   dump(BASE/(task["id"]+"__r"+str(rep))/"FAILURE.json",result);print(json.dumps(result),flush=True)
if __name__=="__main__":main()

