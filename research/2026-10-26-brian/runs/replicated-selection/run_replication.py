"""Finite preregistered selection-package replication, no provider or model calls.

The incumbent engine is imported unchanged. Only its documented input globals
are rebound to isolated per-seed files; no incumbent source or checker is edited.
"""
import gzip
import hashlib
import importlib.util
import json
import statistics
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(__file__).resolve().parent
ENGINE = ROOT / "inputs/engine/search.py"
EXPECTED_ENGINE = "4357f20b2555ce6344f44af140da879c0a6e25b29b560f9566f54a2d3b71cb67"
VERIFIER = ROOT / "tools/verify_bundle.py"
SEEDS = [2026102601,2026102602,2026102603,2026102604,2026102605,2026102606,2026102607,2026102608]


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha(path):
    return sha_bytes(path.read_bytes())


def put(path, data):
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2); f.write("\n")


def frozen_plan():
    return {
        "schema":"addition-chain-replicated-selection-preregistration.v1",
        "frozen_utc":datetime.now(timezone.utc).isoformat(),
        "question":"In this tiny full-target region, how does the existing score-guided selection package compare with seeded SHA selection under matched assessment caps?",
        "hypothesis":"Score-guided selection may reduce best charged operations at the same 256-assessment cap. The paired difference control-minus-guided is reported regardless of sign.",
        "target_id":"P-256 scalar order n-2",
        "modulus_decimal":"115792089210356248762697446949407573529996955224135760342422259061068512044369",
        "target_hex":"ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc63254f",
        "current_retained_best_operations":284,
        "engine_sha256":EXPECTED_ENGINE,
        "verifier_sha256":sha(VERIFIER),
        "seeds":SEEDS,
        "policies":["score_guided","hash_control"],
        "arm_order":"guided first for even zero-based seed position, hash first for odd; no adaptive reassignment",
        "grammar":{"max_precompute_exponent":127,"max_window_bits":8,"max_precompute_operations":14,"beam_width":16},
        "budgets":{"assessments_each_arm":256,"total_configured_assessments":4096,"process_CPU_seconds_total_max":30,"wall_seconds_total_max":60,"provider_calls":0,"paid_usd":0,"model_tokens":0,"new_output_bytes_max":1000000},
        "primary_endpoint":"Paired control-minus-guided best charged-operation difference across the eight fixed seeds; report raw pairs and median, with ties retained.",
        "secondary_endpoints":["best S/M separately","valid emitted final certificates","assessment ordinal of final best","unique and repeated precompute states","DP transitions","source-meter CPU/wall including telemetry","observed selected beam difference"],
        "stop_rules":["Any input/verifier drift -> stop without rerun","Any failed exact certificate -> retain failure and stop","At CPU/wall/output bound -> retain completed/censored arms, no extrapolation","No frontier claim without exact certificate strictly below284","No post-result seed or grammar changes"],
        "effect_scope":"New local isolated run files only; no source writes, scheduler, provider, network, reviewer wake, or consumer acceptance",
        "inference_ceiling":"A deterministic selection-package comparison on one historically exposed target at a tiny budget. Policy-specific hash tie salts differ too. Not an agent-skill, collaboration, autonomous-memory, serving-family, held-out-target or generalization test.",
        "failure_policy":"Never overwrite a previous run or silently retry a partial arm. New invocation on populated output is refused."
    }


def main():
    if sha(ENGINE) != EXPECTED_ENGINE:
        raise SystemExit("ENGINE_HASH_DRIFT")
    plan_path = RUN / "PREREGISTRATION.json"
    if plan_path.exists():
        raise SystemExit("ALREADY_FROZEN_OR_RUN: no automatic overwrite/retry")
    plan=frozen_plan(); put(plan_path,plan)
    put(RUN / "PRE_RUN_PIN.json", {"observed_utc":datetime.now(timezone.utc).isoformat(),"preregistration_sha256":sha(plan_path),"engine_sha256":sha(ENGINE),"verifier_sha256":sha(VERIFIER),"runner_sha256":sha(Path(__file__)),"written_before_any_arm":True})
    sys.path.insert(0,str(ROOT / "tools"))
    from verify_bundle import verify
    spec=importlib.util.spec_from_file_location("pinned_corrected_engine", ENGINE)
    engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    before_wall=time.perf_counter(); before_cpu=time.process_time()
    records=[]; failures=[]; stopped=None
    old=json.loads((ROOT / "inputs/engine/frozen_plan.json").read_text())
    for index,seed in enumerate(SEEDS):
        folder=RUN / ("seed-"+str(seed)); folder.mkdir(exist_ok=False)
        local_plan=json.loads(json.dumps(old))
        local_plan['schema']='addition-chain-replicated-selection-seed.v1'
        local_plan['replication_preregistration_sha256']=sha(plan_path)
        local_plan['new_region'].update(plan['grammar'])
        local_plan['new_region'].update({'assessment_cap_each':256,'seed':seed,'policies':['score_guided','hash_control']})
        local_plan['bounds']={'provider_calls':0,'paid_usd':0,'new_scope':'new20261026 replication; old historical deadline not revived'}
        local_plan['claim_ceiling']=plan['inference_ceiling']
        put(folder / 'frozen_plan.json',local_plan)
        (folder / 'verify.py').write_bytes(VERIFIER.read_bytes())
        put(folder / 'pre_run_pin.json',{'utc':datetime.now(timezone.utc).isoformat(),'plan_sha256':sha(folder/'frozen_plan.json'),'generator_sha256':sha(ENGINE),'verifier_sha256':sha(VERIFIER),'preregistration_sha256':sha(plan_path)})
        order=['score_guided','hash_control'] if index%2==0 else ['hash_control','score_guided']
        for policy in order:
            if time.process_time()-before_cpu>=30 or time.perf_counter()-before_wall>=60:
                stopped='CPU_OR_WALL_BOUND';break
            engine.HERE=folder;engine.PLAN_PATH=folder/'frozen_plan.json';engine.PLAN_BYTES=engine.PLAN_PATH.read_bytes();engine.PLAN=local_plan;engine.REGION=local_plan['new_region']
            try:
                if sha(ENGINE)!=EXPECTED_ENGINE or sha(VERIFIER)!=plan['verifier_sha256']:
                    raise ValueError('INPUT_HASH_DRIFT')
                result=engine.run_policy(policy)
                cert_path=folder/(policy+'.certificate.json')
                target=int(plan['target_hex'],16);modulus=int(plan['modulus_decimal'])
                checked=verify(cert_path.read_bytes(),'json',target,modulus)
                if checked['dead']['operations'] or checked['charged']['operations']!=result['best']['operations']:
                    raise ValueError('CERTIFICATE_REPLAY_OR_LIVENESS_FAILED')
                trace_path=folder/(policy+'.assessments.jsonl.gz')
                with gzip.open(trace_path,'rt',encoding='utf-8') as f:trace=[json.loads(x) for x in f]
                if len(trace)!=256 or any(x['ordinal']!=i for i,x in enumerate(trace,1)):
                    raise ValueError('TRACE_BUDGET_OR_ORDINAL_MISMATCH')
                keys=[(tuple(x['values']),tuple(map(tuple,x['parents']))) for x in trace]
                minimum=min(x['score'][0] for x in trace)
                if minimum!=checked['charged']['operations']:raise ValueError('TRACE_BEST_MISMATCH')
                record={'seed':seed,'policy':policy,'order_position':order.index(policy)+1,'state':'COMPLETE_VERIFIED','best':checked['charged'],'arithmetic_graph_sha256':checked['arithmetic_graph_sha256'],
                    'assessments':len(trace),'unique_precompute_states':len(set(keys)),'repeated_precompute_assessments':len(keys)-len(set(keys)),
                    'first_final_best_ordinal':next(x['ordinal'] for x in trace if x['score'][0]==minimum),'DP_transitions':result['counters']['dp_transitions'],
                    'process_cpu_ns_search_including_trace':result['process_cpu_ns'],'wall_ns_search_including_trace':result['wall_ns'],
                    'certificate_sha256':sha(cert_path),'trace_sha256':sha(trace_path),'result_sha256':sha(folder/(policy+'.result.json')),'separate_exact_replay':checked,
                    'artifact_directory':str(folder.relative_to(ROOT)).replace('\\','/'),'beats_current284':checked['charged']['operations']<284}
                put(folder/(policy+'.CURRENT_REPLAY.json'),record);records.append(record)
            except Exception as error:
                failures.append({'seed':seed,'policy':policy,'state':'FAILED_PRESERVED','error':type(error).__name__+': '+str(error)})
                stopped='FIRST_FAILED_ARM';break
        if stopped:break
    pairs=[]
    for seed in SEEDS:
        rs={r['policy']:r for r in records if r['seed']==seed}
        if len(rs)==2:
            g=rs['score_guided'];c=rs['hash_control']
            pairs.append({'seed':seed,'guided_operations':g['best']['operations'],'hash_operations':c['best']['operations'],'control_minus_guided':c['best']['operations']-g['best']['operations'],
                'guided_unique_precompute_states':g['unique_precompute_states'],'hash_unique_precompute_states':c['unique_precompute_states'],'guided_cpu_ns':g['process_cpu_ns_search_including_trace'],'hash_cpu_ns':c['process_cpu_ns_search_including_trace']})
    delta=[p['control_minus_guided'] for p in pairs]
    output={'schema':'addition-chain-replicated-selection-result.v1','observed_utc':datetime.now(timezone.utc).isoformat(),'preregistration_sha256':sha(plan_path),'engine_sha256':sha(ENGINE),'verifier_sha256':sha(VERIFIER),
        'status':'COMPLETE_BOUND' if len(records)==16 and not failures else 'PARTIAL_PRESERVED','completed_arms':len(records),'configured_arms':16,'completed_assessments':sum(r['assessments'] for r in records),
        'failures':failures,'stop':stopped,'records':records,'pairs':pairs,
        'paired_summary':{'complete_pairs':len(pairs),'guided_wins':sum(d>0 for d in delta),'ties':sum(d==0 for d in delta),'guided_losses':sum(d<0 for d in delta),'median_control_minus_guided':statistics.median(delta) if delta else None,'mean_control_minus_guided':statistics.mean(delta) if delta else None},
        'total_process_cpu_seconds_including_verification_and_audit':time.process_time()-before_cpu,'total_wall_seconds_including_verification_and_audit':time.perf_counter()-before_wall,
        'minimum_emitted_operations':min((r['best']['operations'] for r in records),default=None),'frontier_improvements':sum(r['beats_current284'] for r in records),
        'inference_ceiling':plan['inference_ceiling'],'raw_trace_row_unit':'Assessment calls, including beam states assessed again; not unique full DAG proposals.'}
    put(RUN/'RESULT.json',output)
    files=[p for p in RUN.rglob('*') if p.is_file()]
    manifest={'schema':'addition-chain-replication-file-manifest.v1','files':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)],'scope':'all prior files in this new run folder; excludes this self-referential manifest'}
    put(RUN/'FILE_MANIFEST.json',manifest)
    size=sum(p.stat().st_size for p in RUN.rglob('*') if p.is_file())
    if size>1000000:raise SystemExit('ARTIFACT_BOUND_EXCEEDED_PRESERVED')
    print(json.dumps({'status':output['status'],'completed_arms':len(records),'assessments':output['completed_assessments'],'pairs':pairs,'paired_summary':output['paired_summary'],'CPU_seconds':output['total_process_cpu_seconds_including_verification_and_audit'],'artifact_bytes':size}))


if __name__=='__main__':main()
