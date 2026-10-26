"""Offline stdlib replay of archived explicit candidates using the frozen oracle.

No model, provider, search, generated code or harness execution occurs. Run from
this public package root with: python -B replay_public.py
"""
import argparse,hashlib,importlib.util,json,zipfile
from collections import Counter
from pathlib import Path


def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,why):
    if not ok:raise ValueError(why)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);parser.add_argument('--source-oracle',type=Path,help='local direct-source validation only; public package defaults to oracle/evaluate.py');args=parser.parse_args();root=args.root
    manifest=json.loads((root/'MANIFEST.v1.json').read_text())
    oracle=args.source_oracle or root/'oracle/evaluate.py'
    oracle_pin=next(x['sha256'] for x in manifest['files'] if x['repo_relative_path'].endswith('/oracle/evaluate.py'))
    require(sha(oracle.read_bytes())==oracle_pin,'frozen oracle source SHA mismatch')
    spec=importlib.util.spec_from_file_location('frozen_public_oracle',oracle);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    candidate_results=[];counts=Counter();valid=Counter();invalid=Counter();clones=0
    for arch in manifest['archives']:
        raw=(root/arch['archive']).read_bytes();require(sha(raw)==arch['sha256'],'archive SHA mismatch: '+arch['archive'])
        with zipfile.ZipFile(root/arch['archive']) as z:
            members=json.loads(z.read('ARCHIVE_MEMBERS.json'))
            for item in members['members']:
                name=item['path'];require(not name.startswith('/') and '..' not in Path(name).parts,'unsafe archive member')
                data=z.read(name);require(len(data)==item['bytes'] and sha(data)==item['sha256'],'member SHA mismatch: '+name)
                if not name.endswith('.candidates.jsonl'):continue
                task_id='synthetic-20-v1' if 'synthetic-20-v1' in arch['job'] else 'synthetic-23-v1'
                for line in data.decode('utf-8').splitlines():
                    if not line.strip():continue
                    row=json.loads(line);result=module.evaluate_payload(row.get('candidate'),task_id);stored=row.get('assessment',{})
                    require(result['arithmetic_valid']==bool(stored.get('valid')),'validity disagreement '+arch['job']+'/'+name)
                    if result['arithmetic_valid']:
                        require(result['charged']==stored['charged'],'charged cost disagreement')
                        require(result['live']==stored['live'],'live cost disagreement')
                        require(result['dead']['operations']==stored['dead']['operations'],'dead count disagreement')
                    group=arch['group'];counts[group+'_materialized']+=1
                    copied=group=='cohort' and item['copied_initial_prefix']
                    if copied:clones+=1
                    else:counts[group+'_actual']+=1
                    (valid if result['arithmetic_valid'] else invalid)[group]+=1
                    candidate_results.append({'group':group,'job':arch['job'],'member':name,'evaluation':row.get('global_evaluation_ordinal'),'copied_initial_prefix':copied,'oracle_state':result['state'],'arithmetic_valid':result['arithmetic_valid'],'charged':result.get('charged')})
    expected=manifest['expected_frozen_counts']
    require(counts['primary_materialized']==expected['primary_materialized_candidate_records'],'primary count mismatch')
    require(counts['cohort_materialized']==expected['cohort_materialized_candidate_records'],'cohort materialized count mismatch')
    require(counts['cohort_actual']==expected['cohort_actual_candidate_evaluations'],'cohort actual count mismatch')
    require(counts['memory_materialized']==expected['memory_candidate_records'],'memory count mismatch')
    require(counts['integration-v1_materialized']==expected['integration_v1_candidate_records'],'v1 integration count mismatch')
    print(json.dumps({'state':'PASS_OFFLINE_ORACLE_REPLAY','oracle_source_sha256':sha(oracle.read_bytes()),'archives_checked':len(manifest['archives']),'all_candidate_records_replayed':len(candidate_results),'counts':dict(counts),'valid_materialized_by_group':dict(valid),'invalid_materialized_by_group':dict(invalid),'cloned_cohort_prefix_records_not_new_actual_evaluations':clones,'scope':'Arithmetic replay and raw member integrity only; no optimum, causal effect, provider independence or cost-control qualification'}))


if __name__=='__main__':main()
