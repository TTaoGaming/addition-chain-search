"""Trusted browser action transport; candidate outputs are data only."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,importlib.util,json,hashlib
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("fixed_adapter",R/"control/run_codex_v3.py")
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
BASE=R/"runs/browser-v1"
DEADLINE=datetime(2026,10,26,18,36,tzinfo=timezone.utc)
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+"\n",encoding="utf-8")
def main():
 p=argparse.ArgumentParser();p.add_argument("op",choices=["init","prompt","record","export"])
 p.add_argument("--cell",choices=["B","V"],required=True);p.add_argument("--round",type=int,choices=[1,2,3]);p.add_argument("--response-file");p.add_argument("--metadata-file")
 x=p.parse_args();f=BASE/("synthetic-20-v1__r1__"+x.cell+"__freebrowser")
 if x.op=="init":
  if f.exists():raise SystemExit("EXISTING_NO_RETRY")
  task=json.loads((R/"PROTOCOL.v1.json").read_text())["tasks"][0]
  job={"id":f.name,"task":task,"replicate":1,"cell":{"id":x.cell,"label":"neutral","skill":False,"memory":"none","tools":True,"feedback":x.cell=="B"},"model":"free-browser-record-per-call"}
  init=a.environment(["init","--output",str(f/"environment"),"--task-id",task["id"],"--tools","on","--feedback","on" if x.cell=="B" else "off"])
  dump(f/"JOB.json",job);dump(f/"HISTORY.json",[]);dump(f/"INIT_RECEIPT.json",init)
  print(json.dumps({"state":"READY","folder":str(f)}));return
 if x.op=="export":
  final=a.environment(["export","--output",str(f/"environment")]);dump(f/"TRUSTED_FINAL.json",final);print(json.dumps({"state":"EXPORTED","rounds":final["rounds_used"]}));return
 job=json.loads((f/"JOB.json").read_text());history=json.loads((f/"HISTORY.json").read_text())
 if x.round!=len(history)+1:raise SystemExit("NONCONTIGUOUS_ROUND")
 folder=f/("round-"+str(x.round));folder.mkdir(exist_ok=True)
 if x.op=="prompt":
  if datetime.now(timezone.utc)>=DEADLINE:raise SystemExit("BROWSER_HORIZON_NO_NEW_CALL")
  prompt=a.TEMPLATE.format(label="neutral",target=job["task"]["target"],baseline=job["task"]["binary_baseline"],tools="on",feedback="on" if x.cell=="B" else "off",skill="",memory_kind="absent",memory="(none)",round=x.round,history=json.dumps(history,separators=(",",":")))
  prompt+="\nRequired JSON response schema (return only the object, no other text):\n"+a.SCHEMA.read_text()
  path=folder/"prompt.txt"
  if path.exists():raise SystemExit("PROMPT_ALREADY_PREPARED_NO_RESEND")
  path.write_text(prompt,encoding="utf-8");dump(folder/"REQUEST.json",{"utc":datetime.now(timezone.utc).isoformat(),"prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),"automatic_retries":0})
  print(json.dumps({"state":"PROMPT_READY","path":str(path),"chars":len(prompt)}));return
 raw=Path(x.response_file).read_bytes();capture=folder/"response.txt"
 if capture.exists():raise SystemExit("RESPONSE_ALREADY_CAPTURED")
 capture.write_bytes(raw)
 if x.metadata_file:dump(folder/"UI_METADATA.json",json.loads(Path(x.metadata_file).read_text()))
 text=raw.decode("utf-8").strip();parse_mode="exact_JSON";fence=chr(96)*3
 if text.startswith(fence) and text.endswith(fence):
  lines=text.splitlines();text="\n".join(lines[1:-1]);parse_mode="single_outer_fence_removed"
 try:
  proposal=json.loads(text);needed=set(json.loads(a.SCHEMA.read_text())["required"])
  if not isinstance(proposal,dict) or set(proposal)!=needed:raise ValueError("required/common fields mismatch")
  action=a.transform(proposal)
 except (ValueError,KeyError,TypeError) as error:
  dump(folder/"RECEIPT.json",{"state":"FORMAT_FAILURE_NO_RETRY","reason":str(error),"response_sha256":hashlib.sha256(raw).hexdigest(),"parse_mode":parse_mode})
  print(json.dumps({"state":"FORMAT_FAILURE_NO_RETRY","reason":str(error)}));return
 action_file=f/("action-"+str(x.round)+".json");dump(action_file,action)
 feedback=a.environment(["act","--output",str(f/"environment"),"--action-file",str(action_file)])
 dump(f/("feedback-"+str(x.round)+".json"),feedback)
 history.append({"action":action,"visible_feedback":feedback});dump(f/"HISTORY.json",history)
 dump(folder/"RECEIPT.json",{"state":"RECORDED","utc":datetime.now(timezone.utc).isoformat(),"response_sha256":hashlib.sha256(raw).hexdigest(),"parse_mode":parse_mode})
 print(json.dumps({"state":"RECORDED","round":x.round,"visible_feedback":feedback}))
if __name__=="__main__":main()

