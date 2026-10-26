"""Audit the retained P-521 memory-order control; no new search or source checker."""
import gzip,hashlib,itertools,json
from datetime import datetime,timezone
from pathlib import Path
from verify_bundle import need

ROOT=Path(__file__).resolve().parents[1]


def main():
    sources=[x for x in json.loads((ROOT/'inventory/EXPERIMENT_SOURCES.v2.json').read_text())['sources'] if x['group']=='p521-memory-case-order']
    def get(name):
        s=next(x for x in sources if Path(x['source_path']).name==name);b=(ROOT/s['bundle_path']).read_bytes();need(hashlib.sha256(b).hexdigest()==s['sha256'],'source drift');return s,b
    plan=json.loads(get('frozen_plan.json')[1]);result=json.loads(get('result.json')[1]);arms=[];state_sets={}
    universe=[(prefix,skip) for prefix in range(248,256) for size in range(4) for skip in itertools.combinations(range(3,32,2),size)]
    need(len(universe)==plan['region']['case_count']==4608,'case universe mismatch')
    for arm in result['arms']:
        name=arm['arm'];s,b=get(name+'_attempts.jsonl.gz')
        with gzip.open(ROOT/s['bundle_path'],'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
        need(len(rows)==arm['attempts']==1024,'arm budget mismatch')
        states=[];valid=[];trajectory=[];best=10**9
        for i,row in enumerate(rows,1):
            need(row['ordinal']==i,'ordinal gap');state=(row['prefix'],tuple(row['skips']));need(state in universe,'case outside frozen universe');states.append(state)
            if row['status']=='VALID_DAG':
                need(row['total']==row['squarings']+row['multiplications'],'charge split')
                need(row['weighted_fifths']==4*row['squarings']+5*row['multiplications'],'weighted objective mismatch')
                valid.append(row)
                if row['weighted_fifths']<best:
                    best=row['weighted_fifths'];trajectory.append({'attempt':i,'weighted_fifths':best,'operations':row['total']})
        need(len(set(states))==1024,'duplicate case in arm')
        need(len(valid)==arm['valid_dags'],'valid count mismatch')
        need(len(rows)-len(valid)==arm['unsupported_grammar'],'unsupported count mismatch')
        need(best==arm['best']['weighted_fifths'],'minimum mismatch')
        need(trajectory[-1]['attempt']==arm['best']['first_found_ordinal'],'first best ordinal mismatch')
        # Control order is fully reconstructible from the frozen seed and case IDs.
        order_check='not re-derived; raw source plan and observed order retained'
        if name=='memory_ablated_control':
            seed=plan['arms']['control_seed']
            ordered=sorted(universe,key=lambda x:hashlib.sha256((seed+':'+str(x[0])+':'+','.join(map(str,x[1]))).encode()).hexdigest())
            need(states==ordered[:1024],'control case order mismatch')
            order_check='exact SHA order independently reproduced'
        arms.append({'arm':name,'attempts':len(rows),'unique_cases':len(set(states)),'valid_reported_dags':len(valid),'unsupported_grammar':len(rows)-len(valid),'best_total':arm['best']['total'],'best_S':arm['best']['squarings'],'best_M':arm['best']['multiplications'],'first_best_ordinal':trajectory[-1]['attempt'],'trajectory':trajectory,'source_trace':s,'order_check':order_check,'process_cpu_ns_source':arm['process_cpu_ns'],'wall_ns_source':arm['wall_ns']})
        state_sets[name]=set(states)
    out={'schema':'p521-memory-case-order-current-audit.v1','observed_utc':datetime.now(timezone.utc).isoformat(),'universe_cases':4608,'arms':arms,'shared_cases_between_arms':len(set.intersection(*state_sets.values())),
        'finding':'Control best 586 beats memory-guided best 587 in one fixed ordering comparison. Both exceed the pinned 582 incumbent and current retained 581 witnesses.',
        'independent_certificate_replay':'both original best files included in BUNDLE_INPUTS.v3.json and exact-integer replay',
        'inference_ceiling':'one manually designed history-based order, one region/control seed, different sampled cases/invalid rates; no autonomous memory learning, generalization, serving-family or swarm cooperation effect',
        'not_run':['persona/language/enforcement factorial design','collaboration on/off','adaptive allocation on/off','blinded held-out multi-target replicated memory study']}
    with (ROOT/('verification/P521_MEMORY_AUDIT-'+str(__import__('time').time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({'attempts_audited':sum(x['attempts'] for x in arms),'shared_cases':out['shared_cases_between_arms'],'best_by_arm':{x['arm']:x['best_total'] for x in arms}}))


if __name__=='__main__':main()
