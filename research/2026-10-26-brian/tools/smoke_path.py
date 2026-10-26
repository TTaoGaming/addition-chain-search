"""Finite incumbent-engine adapter, not a scheduler, queue, service or factory controller.

One fixed two-policy plan. Append-only policy checkpoints support an intentional
process exit and restart. All effects are confined to runs/smoke-001.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime,timezone
from pathlib import Path
from verify_bundle import need,verify

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/smoke-001'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def readplan():
    p=RUN/'PLAN.json';pin=json.loads((RUN/'pre_run_pin.json').read_text());plan=json.loads(p.read_text())
    need(sha(p)==pin['plan_sha256'],'SMOKE_PLAN_HASH_DRIFT')
    need(sha(ROOT/plan['source_generator']['bundle_path'])==plan['source_generator']['sha256'],'ENGINE_HASH_DRIFT')
    need(sha(ROOT/plan['independent_verifier']['bundle_path'])==plan['independent_verifier']['sha256']==sha(RUN/'verify.py'),'VERIFIER_HASH_DRIFT')
    need(plan['new_region']['assessment_cap_each']==256 and plan['new_region']['policies']==['score_guided','hash_control'],'SMOKE_BOUND_DRIFT')
    return plan


def verify_completed(policy,plan):
    checkpoint=RUN/('checkpoint-'+policy+'.json');cp=json.loads(checkpoint.read_text())
    need(cp['plan_sha256']==sha(RUN/'PLAN.json'),'checkpoint-plan mismatch')
    for name,h in cp['artifact_sha256'].items():need(sha(RUN/name)==h,'completed artifact drift')
    result=json.loads((RUN/(policy+'.result.json')).read_text())
    need(result['counters']['assessments']==256,'completed assessment count mismatch')
    target=int(plan['target_hex'],16)
    v=verify((RUN/(policy+'.certificate.json')).read_bytes(),'json',target,target+2)
    need(v['dead']['operations']==0,'smoke generator returned dead rows')
    return v


def child(policy):
    plan=readplan();enginepath=ROOT/plan['source_generator']['bundle_path']
    spec=importlib.util.spec_from_file_location('frozen_incumbent_engine',enginepath)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    # Configure only existing engine input globals. The source file is unchanged.
    mod.HERE=RUN;mod.PLAN_PATH=RUN/'PLAN.json';mod.PLAN_BYTES=mod.PLAN_PATH.read_bytes();mod.PLAN=plan;mod.REGION=plan['new_region']
    need(mod.TARGET==int(plan['target_hex'],16),'engine target mismatch')
    result=mod.run_policy(policy)
    target=int(plan['target_hex'],16)
    validation=verify((RUN/(policy+'.certificate.json')).read_bytes(),'json',target,target+2)
    need(validation['dead']['operations']==0,'generated dead rows')
    need(result['counters']['assessments']==256,'engine did not meet exact tiny assessment cap')
    names=[policy+'.result.json',policy+'.certificate.json',policy+'.assessments.jsonl.gz']
    checkpoint={'state':'POLICY_COMPLETE_VERIFIED','observed_utc':datetime.now(timezone.utc).isoformat(),'policy':policy,'plan_sha256':sha(RUN/'PLAN.json'),'artifact_sha256':{n:sha(RUN/n) for n in names},'separate_verifier_result':validation,'generator_is_pinned_original':True,'claim_ceiling':plan['claim_ceiling']}
    with (RUN/('checkpoint-'+policy+'.json')).open('x',encoding='utf-8') as f:json.dump(checkpoint,f,indent=2);f.write('\n')
    print(json.dumps({'policy':policy,'best':result['best'],'assessments':256,'validation':validation['state']}))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stop-after',type=int);p.add_argument('--child',choices=['score_guided','hash_control']);args=p.parse_args()
    if args.child:child(args.child);return
    plan=readplan();completed_before=[];executed=[];failures=[];stamp=str(time.time_ns())
    for policy in plan['new_region']['policies']:
        checkpoint=RUN/('checkpoint-'+policy+'.json')
        if checkpoint.exists():verify_completed(policy,plan);completed_before.append(policy);continue
        # A failed or interrupted child is never silently overwritten/retried.
        need(not any((RUN/(policy+suffix)).exists() for suffix in ['.result.json','.certificate.json','.assessments.jsonl.gz']), 'PARTIAL_PRIOR_ATTEMPT_HOLD')
        start=time.perf_counter()
        try:
            proc=subprocess.run([sys.executable,'-B',str(Path(__file__)),'--child',policy],cwd=ROOT,capture_output=True,timeout=10)
            code=proc.returncode;stdout=proc.stdout;stderr=proc.stderr
        except subprocess.TimeoutExpired as e:
            code='TIMEOUT';stdout=e.stdout or b'';stderr=e.stderr or b''
        (RUN/(stamp+'-'+policy+'.stdout.txt')).write_bytes(stdout)
        (RUN/(stamp+'-'+policy+'.stderr.txt')).write_bytes(stderr)
        if code!=0:
            failures.append({'policy':policy,'exit_code':code});break
        verify_completed(policy,plan);executed.append(policy)
        if args.stop_after and len(executed)>=args.stop_after:break
    done=[policy for policy in plan['new_region']['policies'] if (RUN/('checkpoint-'+policy+'.json')).exists()]
    state='FAILED_PRESERVED_HOLD' if failures else 'DUPLICATE_ALREADY_COMPLETE_NO_RERUN' if len(completed_before)==2 else 'COMPLETE_BOUNDED_DEMONSTRATION' if len(done)==2 else 'STOPPED_AT_DURABLE_CHECKPOINT'
    receipt={'schema':'addition-chain-smoke-invocation.v1','observed_utc':datetime.now(timezone.utc).isoformat(),'state':state,'completed_before':completed_before,'policies_executed_this_invocation':executed,'completed_after':done,'failures':failures,'plan_sha256':sha(RUN/'PLAN.json'),'effect_scope':'local finite demonstration; no provider call, lease transfer, scheduler, production history integration or consumer acceptance'}
    with (RUN/('invocation-'+stamp+'.json')).open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(receipt))
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
