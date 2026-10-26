from pathlib import Path
import hashlib,json,datetime
R=Path(__file__).resolve().parents[1]
source=(R/"control/run_cohort_v1.py").read_text()
guard=' if datetime.now(timezone.utc)>=adapter.STOP:\n  return {"state":"HORIZON_REFUSED_BEFORE_INVOKE","receipt":{"state":"HORIZON_REFUSED_BEFORE_INVOKE","wall_s":0,"usage":{},"native_tool_events":0}}\n'
source=source.replace('def call(worker,task,folder,own,peers,index):\n','def call(worker,task,folder,own,peers,index):\n'+guard)
source=source.replace(' proposal,receipt=adapter.invoke(MODELS[worker],prompt,folder/("model-round-"+str(index)))\n',guard+' proposal,receipt=adapter.invoke(MODELS[worker],prompt,folder/("model-round-"+str(index)))\n')
p=R/"control/run_cohort_v2.py"
assert not p.exists()
p.write_text(source,encoding="utf-8")
receipt={"schema":"cohort-prelaunch-amendment.v2","utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"prior_cohort_calls":0,"selected_runner":"control/run_cohort_v2.py","sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"change":"Per-call horizon refusals before prompt preparation and immediately before invoke; no call after19:24:08Z.","event_identity_scope":"Key by pair/arm/worker/path plus event_id. Cloned initial work counted once actual; ordinal event IDs can collide across branches. Never deduplicate actual inference by bare event_id.","harness_oracle_schema_changed":False}
(R/"control/COHORT_AMENDMENT.v2.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
print(json.dumps(receipt))

