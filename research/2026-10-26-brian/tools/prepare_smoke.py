"""Freeze a tiny full-target engine demonstration, separate from causal ablations."""
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    sources=json.loads((ROOT/'inventory/EXPERIMENT_SOURCES.json').read_text())['sources']
    selected={Path(x['source_path']).name:x for x in sources if x['group']=='p256_policy_correction_20260929' and Path(x['source_path']).name in ['search.py','frozen_plan.json']}
    engine=ROOT/'inputs/engine';engine.mkdir(exist_ok=False)
    for name,s in selected.items():
        b=(ROOT/s['bundle_path']).read_bytes()
        if hashlib.sha256(b).hexdigest()!=s['sha256']:raise SystemExit('SOURCE_HASH_DRIFT')
        (engine/name).write_bytes(b)
    run=ROOT/'runs/smoke-001';run.mkdir(exist_ok=False)
    old=json.loads((engine/'frozen_plan.json').read_text())
    old['schema']='addition-chain-finite-engine-smoke.v1'
    old['frozen_utc']=datetime.now(timezone.utc).isoformat()
    old['authority']='new 2026-10-26 local research request; not revival of old source budget'
    old['original_plan_sha256']=selected['frozen_plan.json']['sha256']
    old['new_region'].update({'assessment_cap_each':256,'beam_width':16,'seed':20261026})
    old['bounds']={'provider_calls':0,'paid_usd':0,'seconds_per_policy_max':10,'artifact_bytes_max':500000,'stop_between_policies_demonstrated':True}
    old['claim_ceiling']='Finite full-target engine/verification/restart demonstration. Not a causal ablation, new frontier, qualified unattended factory or comparison with the 284 incumbent.'
    old['hypothesis']='A pinned incumbent deterministic generator can produce budgeted certificates which a separate exact-integer implementation validates, and completed work can be recovered without repeating an effect.'
    old['outcomes_required']=['256 assessment calls per arm or precise failure','original raw telemetry retained','certificate exact target and charge replay','stop after first policy','restart second policy only','duplicate invocation validates prior result without rerun']
    old['source_generator']={'bundle_path':'inputs/engine/search.py','sha256':selected['search.py']['sha256']}
    old['independent_verifier']={'bundle_path':'tools/verify_bundle.py','sha256':hashlib.sha256((ROOT/'tools/verify_bundle.py').read_bytes()).hexdigest(),'independence':'separate implementation; same collecting carrier; no distinct reviewer'}
    (run/'PLAN.json').write_text(json.dumps(old,indent=2)+'\n',encoding='utf-8')
    # The incumbent generator logs the bytes of this file. It is the exact
    # verifier source used via import by the adapter, not a historical checker.
    (run/'verify.py').write_bytes((ROOT/'tools/verify_bundle.py').read_bytes())
    pin={'frozen_before_search_utc':datetime.now(timezone.utc).isoformat(),'plan_sha256':hashlib.sha256((run/'PLAN.json').read_bytes()).hexdigest(),'source_generator_sha256':selected['search.py']['sha256'],'separate_verifier_sha256':old['independent_verifier']['sha256'],'no_source_owner_or_schedule_mutation':True}
    (run/'pre_run_pin.json').write_text(json.dumps(pin,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(pin))


if __name__=='__main__':main()
