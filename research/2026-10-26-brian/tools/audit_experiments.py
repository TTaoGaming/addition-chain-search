"""Read pinned historical runs; never launch search, solver, provider or source checker."""
import gzip
import hashlib
import json
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from verify_bundle import need, integer

ROOT=Path(__file__).resolve().parents[1]


def main():
    index=json.loads((ROOT/"inventory/EXPERIMENT_SOURCES.json").read_text())
    sources=index["sources"]
    def source(group,name):
        found=[s for s in sources if s['group']==group and Path(s['source_path']).name==name]
        need(len(found)==1,"source locator ambiguous: "+group+" "+name)
        s=found[0];b=(ROOT/s['bundle_path']).read_bytes()
        need(hashlib.sha256(b).hexdigest()==s['sha256'],"experiment source hash drift")
        return s,b
    def doc(group,name):return json.loads(source(group,name)[1])

    def dp_score(values,parents,target,width,corrected):
        # Independently forward-propagate all legal bit windows. This is a
        # deterministic score spot-check, not a second historical search run.
        bits=bin(target)[2:];n=len(bits);allowed=set(values);dist=[None]*(n+1)
        def key(t):return (sum(t),t[1],t[0]) if corrected else (sum(t),t[0],t[1])
        def update(i,v):
            if dist[i] is None or key(v)<key(dist[i]):dist[i]=v
        for w in range(1,min(width,n)+1):
            if int(bits[:w],2) in allowed:update(w,(0,0))
        for i in range(1,n):
            if dist[i] is None:continue
            for w in range(1,min(width,n-i)+1):
                digit=int(bits[i:i+w],2)
                if digit==0 or digit in allowed:
                    update(i+w,(dist[i][0]+w,dist[i][1]+int(digit!=0)))
        need(dist[n] is not None,"DP target unreachable")
        ps=sum(a==b for a,b in parents);pm=len(parents)-ps
        sq,mu=dist[n][0]+ps,dist[n][1]+pm
        return [sq+mu,sq,mu]

    traces={};results=[]
    for group,corrected in [("p256_memory_transfer_20260929",False),("p256_policy_correction_20260929",True)]:
        plan=doc(group,"frozen_plan.json");target=int(plan["target_hex"],16);width=plan["new_region"]["max_window_bits"]
        for policy in ["score_guided","hash_control"]:
            s,b=source(group,policy+".assessments.jsonl.gz")
            rows=[]
            with gzip.open(ROOT/s['bundle_path'],"rt",encoding="utf-8") as f:
                for line in f:
                    need(len(rows)<100000,"trace row cap")
                    rows.append(json.loads(line))
            result=doc(group,policy+".result.json")
            need(len(rows)==result['counters']['assessments']==24000,"assessment count mismatch")
            unique=set();value_sets=set();best=10**9;trajectory=[];sample_count=0
            observed_bins=Counter();state_invalid=0
            for i,row in enumerate(rows,1):
                need(row['ordinal']==i,"trace ordinal gap")
                values=row['values'];parents=row['parents']
                need(len(values)==len(parents)+1 and values[0]==1,"precompute shape")
                for j,(a,c) in enumerate(parents,1):
                    need(type(a) is int and type(c) is int and 0<=a<j and 0<=c<j,"precompute future reference")
                    need(values[j]==values[a]+values[c],"precompute parent identity")
                need(all(values[j]>values[j-1] for j in range(1,len(values))),"precompute grammar monotonicity")
                state=(tuple(values),tuple(map(tuple,parents)));unique.add(state);value_sets.add(tuple(values))
                score=row['score'];need(type(score) is list and len(score)==3 and score[0]==score[1]+score[2],"score split mismatch")
                observed_bins['below_291' if score[0]<291 else 'equal_291' if score[0]==291 else 'above_291']+=1
                if score[0]<best:
                    best=score[0];trajectory.append({"assessment":i,"operations":best,"S":score[1],"M":score[2],"depth":row['depth']})
                if i in [1,len(rows)] or i%251==0:
                    need(dp_score(values,parents,target,width,corrected)==score,"independent forward-window score mismatch at "+str(i));sample_count+=1
            for k in ['below_291','equal_291','above_291']:
                need(observed_bins[k]==result['counters'][k],"score histogram mismatch")
            need(best==result['best']['operations'],"reported minimum mismatch")
            bydepth=defaultdict(lambda: {'beam':[],'child':[]})
            for row in rows:bydepth[row['depth']][row['origin']].append(row)
            selection_checks=[];seed=plan['new_region']['seed'];bw=plan['new_region']['beam_width']
            def tie(values,lane):return hashlib.sha256((str(seed)+':'+lane+':'+','.join(map(str,values))).encode()).hexdigest()
            for depth,partition in sorted(bydepth.items()):
                children=partition['child'];beam=partition['beam']
                if not children or not beam:continue
                ordered=sorted(children,key=(lambda r:(r['score'][0],r['score'][2],tie(r['values'],policy))) if policy=='score_guided' else (lambda r:tie(r['values'],policy)))
                expected=[(r['values'],r['parents']) for r in ordered[:bw]]
                actual=[(r['values'],r['parents']) for r in beam]
                need(actual==expected[:len(actual)],"recorded beam is inconsistent with selection policy")
                selection_checks.append({'depth':depth,'observed_beam_rows':len(actual),'consistent':True})
            results.append({'group':group,'policy':policy,'plan_source':source(group,'frozen_plan.json')[0], 'trace_source':s,
                'assessments':len(rows),'unique_precompute_states':len(unique),'unique_precompute_value_sets':len(value_sets),
                'repeated_precompute_assessments':len(rows)-len(unique),'exact_forward_DP_spot_checks':sample_count,
                'all_precompute_reference_and_sum_checks':'PASS','reported_score_bins_recomputed':dict(observed_bins),
                'selection_checks':selection_checks,'best_operations':best,'best_S':result['best']['squarings'],'best_M':result['best']['multiplications'],
                'wall_ns_reported':result['wall_ns'],'process_cpu_ns_reported':result['process_cpu_ns'],'dp_transitions_reported':result['counters']['dp_transitions'],
                'trajectory':trajectory,'stop_class':'ASSESSMENT_CAP','full_DAG_invalid_proposals':'UNKNOWN; only final certificates and precompute states audited',
                'claim_ceiling':'one seed; matched assessment count, unequal realized compute; deterministic heuristic selection, no collaboration/memory causal experiment'})
            traces[(group,policy)]=rows
    corrections=[]
    for policy in ['score_guided','hash_control']:
        a=traces[('p256_memory_transfer_20260929',policy)];b=traces[('p256_policy_correction_20260929',policy)]
        changed_states=sum((x['values'],x['parents'])!=(y['values'],y['parents']) for x,y in zip(a,b))
        changed_scores=sum(x['score']!=y['score'] for x,y in zip(a,b))
        corrections.append({'policy':policy,'paired_ordinals':len(a),'changed_state_ordinals':changed_states,'changed_score_ordinals':changed_scores,'interpretation':'no observed search-state or score effect in this region; not a general no-effect proof'})

    evo=[]
    for run in ['run_001','run_002','run_003']:
        s,b=source('compact-openevolve-'+run,'evolution_trace.jsonl')
        rows=[json.loads(x) for x in b.decode().splitlines() if x.strip()]
        def canonical(code):
            try:return json.dumps(json.loads(code),sort_keys=True,separators=(',',':'))
            except ValueError:return 'NON_JSON:'+code
        items=[{'iteration':x['iteration'],'timestamp_raw':x['timestamp'],'timestamp_utc':datetime.fromtimestamp(x['timestamp'],timezone.utc).isoformat(),
                'child_id':x['child_id'],'parent_id':x['parent_id'],'child_metrics_reported':x['child_metrics'],
                'parent_identical':canonical(x['child_code'])==canonical(x['parent_code']),
                'canonical_genome_sha256':hashlib.sha256(canonical(x['child_code']).encode()).hexdigest()} for x in rows]
        expected=1 if run=='run_001' else 8
        evo.append({'run':run,'trace_source':s,'trace_rows':len(rows),'expected_iterations_from_receipt':expected,'missing_iteration_rows':sorted(set(range(1,expected+1))-{x['iteration'] for x in rows}),
            'unique_child_genomes_in_trace':len({x['canonical_genome_sha256'] for x in items}),'parent_identical_rows':sum(x['parent_identical'] for x in items),
            'strict_improvement_rows_reported':sum(x['child_metrics'].get('strict_improvement',0)>0 for x in rows),'items':items,
            'ceiling':'raw engine trace and reported metrics; genome counts are not independently replayed arithmetic DAG counts'})
    missing=doc('compact-openevolve-missing-trace-row','f135a2b8-49b3-4978-843f-ef5d132c5e5d.json')

    episodes=[]
    for arm in ['contiguous_guided','contiguous_random','split_guided','split_random']:
        group='p256-episodes-'+arm
        rows=[doc(group,'EPISODE_'+str(i).zfill(2)+'.json') for i in range(12)]
        episodes.append({'arm':arm,'outcomes':len(rows),'solver_status_counts':dict(Counter(x['solver']['status'] for x in rows)),
            'minimum_emitted_candidate':min((x['count']['operations'] for x in rows if x.get('count')),default=None),
            'candidate_cases':sum(bool(x.get('candidate')) for x in rows),'solver_scope':'THIS_FINITE_MODEL_ONLY',
            'source_result':source(group,'RESULT.json')[0], 'result':doc(group,'RESULT.json')})
    correction=doc('p256-episodes','RESOURCE_DENOMINATOR_CORRECTION.json')
    replay=json.loads(sorted((ROOT/'verification').glob('replay-*.json'))[-1].read_text())
    graph_by_hash={w['sha256']:next(x for x in replay['results'] if x['id']==w['id'])['arithmetic_graph_sha256'] for w in json.loads((ROOT/'inventory/BUNDLE_INPUTS.final.json').read_text())['witnesses']}
    candidates=correction['cases'];graphs=[graph_by_hash[x['file']['sha256']] for x in candidates]
    seed=graph_by_hash['cf2f652a6fe1b240cfbeb0ffdf718feeaec2a7ae07875445357035c83ca0eeac']
    need(all(g==seed for g in graphs),'source-equivalence correction does not match independent graph fingerprints')
    output={'schema':'addition-chain-historical-ablation-audit.v1','observed_utc':datetime.now(timezone.utc).isoformat(),'p256_matched_assessment_runs':results,'correction_comparison':corrections,
        'compact_openevolve':evo,'missing_trace_checkpoint':{'id':missing['id'],'iteration_found':missing.get('iteration_found'),'metrics_reported':missing['metrics'],'source':source('compact-openevolve-missing-trace-row','f135a2b8-49b3-4978-843f-ef5d132c5e5d.json')[0]},
        'p256_scaffold_episodes':episodes,'independent_duplicate_audit':{'candidate_file_cases':len(candidates),'distinct_raw_hashes':len({x['file']['sha256'] for x in candidates}),'distinct_arithmetic_graphs':len(set(graphs)),'all_equal_to_existing_285_source':all(g==seed for g in graphs),'new_graphs':0},
        'proposed_causal_swarm_ablation':'NOT_RUN: collaboration, adaptive allocation, memory on/off, irrelevant memory, held-out targets and paired multi-seed budgets are not present in these runs',
        'historical_resource_observations':'source-reported times are retained; this audit does not turn them into current timing measurements or equal CPU budgets'}
    with (ROOT/('verification/ABLATION_AUDIT-'+str(__import__('time').time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(output,f,indent=2);f.write('\n')
    print(json.dumps({'trace_assessments_audited':sum(x['assessments'] for x in results),'independent_score_spot_checks':sum(x['exact_forward_DP_spot_checks'] for x in results),'corrections':corrections,'scaffold_outcomes':sum(x['outcomes'] for x in episodes),'duplicate_audit':output['independent_duplicate_audit'],'openevolve_trace_rows':[x['trace_rows'] for x in evo]}))


if __name__=='__main__':main()
