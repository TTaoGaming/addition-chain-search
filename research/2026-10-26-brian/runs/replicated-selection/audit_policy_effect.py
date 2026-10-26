"""Audit selection changes and semantic duplication from already saved raw traces."""
import csv,gzip,json,hashlib
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=Path(__file__).resolve().parent


def key(row):return tuple(row['values']),tuple(map(tuple,row['parents']))


def main():
    result=json.loads((RUN/'RESULT.json').read_text())
    rows=[]
    for pair in result['pairs']:
        folder=RUN/('seed-'+str(pair['seed']))
        traces={}
        for policy in ['score_guided','hash_control']:
            with gzip.open(folder/(policy+'.assessments.jsonl.gz'),'rt') as f:traces[policy]=[json.loads(x) for x in f]
        g=traces['score_guided'];h=traces['hash_control'];gs=set(map(key,g));hs=set(map(key,h))
        changed=[i for i,(a,b) in enumerate(zip(g,h),1) if key(a)!=key(b)]
        beam=defaultdict(dict)
        for policy,trace in traces.items():
            for depth in sorted({x['depth'] for x in trace}):beam[depth][policy]=set(key(x) for x in trace if x['depth']==depth and x['origin']=='beam')
        comparisons=[{'depth':depth,'guided_observed_beam':len(v.get('score_guided',set())),'hash_observed_beam':len(v.get('hash_control',set())),
            'shared_observed_beam_states':len(v.get('score_guided',set())&v.get('hash_control',set()))} for depth,v in sorted(beam.items()) if v.get('score_guided') or v.get('hash_control')]
        rows.append({'seed':pair['seed'],'changed_state_ordinals':len(changed),'first_changed_state_ordinal':changed[0] if changed else None,'unique_states_shared_between_policies':len(gs&hs),'guided_unique_states':len(gs),'hash_unique_states':len(hs),'observed_beam_comparison':comparisons})
    graphs={policy:len({x['arithmetic_graph_sha256'] for x in result['records'] if x['policy']==policy}) for policy in ['score_guided','hash_control']}
    out={'schema':'addition-chain-selection-effect-audit.v1','source_result_sha256':hashlib.sha256((RUN/'RESULT.json').read_bytes()).hexdigest(),
        'paired_rows':rows,'distinct_final_arithmetic_graphs_by_policy':graphs,'all_distinct_final_arithmetic_graphs':len({x['arithmetic_graph_sha256'] for x in result['records']}),
        'conclusion':'Selection packages changed evaluated state populations. Terminal certificate counts differ for five seeds and tie for three. This is one exposed target; state and certificate duplicates are retained.',
        'ceiling':'Precompute-state diversity and final certificate graph identity only; not full proposal-DAG diversity or an agent learning claim.'}
    with (RUN/'POLICY_EFFECT_AUDIT.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    with (RUN/'PAIRED_RESULTS.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(result['pairs'][0]));writer.writeheader();writer.writerows(result['pairs'])
    size=sum(p.stat().st_size for p in RUN.rglob('*') if p.is_file())
    if size>1000000:raise SystemExit('OUTPUT_CAP_EXCEEDED_PRESERVED')
    print(json.dumps({'distinct_graphs':graphs,'all_distinct_graphs':out['all_distinct_final_arithmetic_graphs'],'first_changed_ordinals':[x['first_changed_state_ordinal'] for x in rows],'artifact_bytes':size}))


if __name__=='__main__':main()
