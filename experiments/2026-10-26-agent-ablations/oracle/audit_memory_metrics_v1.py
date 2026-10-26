"""Compare memory summaries with independently audited raw records and fixed pools."""
import csv,hashlib,json,math
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def need(ok,why):
    if not ok:raise AssertionError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ident(c,target):
    x={'target':str(target),'steps':[sorted(p) for p in c['steps']],'output_index':c.get('output_index',len(c['steps']))}
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
    raw_path=HERE/'MEMORY_RAW_AUDIT.v1.json';raw=read(raw_path)
    need(sha(HERE/'PRIMARY_CANDIDATE_AUDIT.v1.csv')=='def716ed97fa546a7e8a46b169e1dd71936b4a5d25fa3ad9ebbcf9cafd913d58','PRIMARY_POOL_DRIFT')
    primary_sets={};frontier={}
    with (HERE/'PRIMARY_CANDIDATE_AUDIT.v1.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            if r['valid']!='True':continue
            task=r['trajectory_id'].split('__')[0];primary_sets.setdefault(task,set()).add(r['schedule_sha256'])
            frontier[task]=min(frontier.get(task,10**9),int(r['cost']))
    need(frontier=={'synthetic-20-v1':24,'synthetic-23-v1':29},'PRIMARY_FRONTIER')
    dpath=ROOT/'control/EPISODE_SOURCE_DENOMINATORS.json';need(sha(dpath)=='82616dcd2311dfe9c90952a935cd26ef936b7699d1206664a2630c10d0891e6f','FIXED_SOURCE_POOL_DRIFT')
    den={d['task_id']:d for d in read(dpath)}
    freeze=read(ROOT/'control/EPISODE_MEMORY_FREEZE.v1.json')
    for pin in freeze['pins']:need(sha(ROOT/pin['path'])==pin['sha256'],'MEMORY_FREEZE_PIN_DRIFT')
    producer_path=ROOT/'analysis/EPISODE_MEMORY_RESULTS.json';producer=read(producer_path)
    rows=[];packet_mapping=[]
    for base in raw['rows']:
        task=base['task_id'];cell=base['cell_id'];folder=ROOT/'runs/memory-v1'/base['trajectory_id']
        job=read(folder/'JOB.json');packet=None;packet_task=None;packet_bytes=packet_words=0
        if cell!='C':
            path=ROOT/('stimuli/'+job['cell']['memory']+'.txt');packet=read(path);packet_task=packet['source_task']
            packet_bytes=path.stat().st_size;packet_words=len(path.read_text().split())
            need((packet_task==task)==(cell=='W'),'PACKET_TARGET_CONDITION_MAPPING')
        else:need(job['cell']['memory']=='none','COLD_PACKET_MAPPING')
        records=[]
        for p in sorted((folder/'environment').glob('round-*.candidates.jsonl')):
            records.extend(json.loads(line) for line in p.read_text().splitlines() if line.strip())
        valid=[r for r in records if r['assessment']['valid']]
        hashes=[ident(r['candidate'],base['target']) for r in valid];unique=set(hashes);source=set(den[task]['all_source_candidate_schedule_hashes'])
        provided=set(den[packet_task]['all_source_candidate_schedule_hashes']) if packet else set()
        retained=ident(packet['retained_best_candidate'],packet['exact_source_target']) if packet else None
        matching=sum(h==retained for h in hashes) if retained else 0
        direct=sum(r['method']=='explicit' and ident(r['candidate'],base['target'])==retained for r in valid) if retained else 0
        extra={'current_target_source_incumbent':den[task]['source_episode_best_cost'],'full_primary_incumbent':frontier[task],
               'source_pool_schedule_count':len(source),
               'strict_cost_improvement_over_current_source':base['best_valid_cost']<den[task]['source_episode_best_cost'],
               'strict_cost_improvement_over_full_primary':base['best_valid_cost']<frontier[task],
               'current_source_schedule_overlap_evaluations':sum(h in source for h in hashes),
               'current_source_unique_schedule_overlap':len(unique&source),
               'distinct_schedules_outside_current_source':len(unique-source),
               'distinct_schedules_outside_full_primary':len(unique-primary_sets[task]),
               'best_is_current_source_schedule':base['best_identity'] in source,
               'supplied_packet_source_task':packet_task,'supplied_packet_words':packet_words,'supplied_packet_bytes':packet_bytes,
               'evaluations_matching_supplied_retained_schedule':matching,
               'direct_submissions_matching_supplied_retained':direct,
               'valid_overlap_with_supplied_episode':sum(h in provided for h in hashes)}
        row={**base,**extra};claim=next(r for r in producer['rows'] if r['trajectory_id']==base['trajectory_id'])
        for k,v in row.items():
            if k=='independent_validation':continue
            need((math.isclose(v,claim[k],rel_tol=1e-12,abs_tol=1e-9) if type(v)is float else v==claim[k]),'MEMORY_ROW_FIELD:'+k)
        need(set(claim)==set(row),'UNVERIFIED_MEMORY_ROW_FIELDS')
        rows.append(row);packet_mapping.append({'trajectory_id':base['trajectory_id'],'packet_task':packet_task,'words':packet_words,'bytes':packet_bytes,'retained_schedule_matches':matching,'direct_submission_matches':direct})
    lookup={(r['task_id'],r['replicate_id'],r['cell_id']):r for r in rows};contrasts=[]
    expected_contrasts=[('same_target_minus_other_target','W','U'),('same_target_minus_cold','W','C'),('other_target_minus_cold','U','C')]
    need([(c['contrast'],c['treatment'],c['control']) for c in producer['contrasts']]==expected_contrasts,'MEMORY_CONTRAST_MAPPING')
    for contrast in producer['contrasts']:
        computed=[]
        for task in ('synthetic-20-v1','synthetic-23-v1'):
            for rep in (1,2):
                t=lookup[(task,rep,contrast['treatment'])];c=lookup[(task,rep,contrast['control'])]
                computed.append({'task_id':task,'replicate_id':rep,'treatment_id':t['trajectory_id'],'control_id':c['trajectory_id'],
                    'treatment_state':t['state'],'control_state':c['state'],'cost_treatment':t['best_valid_cost'],'cost_control':c['best_valid_cost'],
                    'cost_delta_treatment_minus_control':t['best_valid_cost']-c['best_valid_cost'],
                    'action_sequence_changed':t['action_sequence']!=c['action_sequence'],'action_families_changed':t['action_family_sequence']!=c['action_family_sequence'],
                    'final_identity_changed':t['best_identity']!=c['best_identity'],'unique_regions_delta':t['unique_regions']-c['unique_regions'],
                    'evaluations_delta':t['realized_evaluations']-c['realized_evaluations'],'duplicates_delta':t['duplicate_candidates']-c['duplicate_candidates'],
                    'invalid_delta':t['invalid_candidates']-c['invalid_candidates']})
        need(computed==contrast['pairs'],'MEMORY_CONTRAST_FIELDS')
        contrasts.append({'contrast':contrast['contrast'],'cost_deltas':[p['cost_delta_treatment_minus_control'] for p in computed]})
    totals={'trajectories':12,'completed':12,'attempted_rounds':sum(r['attempted_rounds'] for r in rows),'returned_rounds':sum(r['returned_rounds'] for r in rows),
            'candidate_evaluations':sum(r['realized_evaluations'] for r in rows),'native_tool_events':0,
            'model_input_tokens':sum(r['model_input_tokens'] for r in rows),'model_output_tokens':sum(r['model_output_tokens'] for r in rows),
            'strict_source_improvement_trajectories':sum(r['strict_cost_improvement_over_current_source'] for r in rows),
            'strict_full_primary_improvement_trajectories':sum(r['strict_cost_improvement_over_full_primary'] for r in rows)}
    need(totals==producer['totals'],'MEMORY_TOTALS')
    csvpath=ROOT/'analysis/EPISODE_MEMORY_RESULTS.csv'
    with csvpath.open(newline='',encoding='utf-8-sig') as f:table=list(csv.DictReader(f))
    need(len(table)==12,'MEMORY_CSV_DENOMINATOR')
    for c,row in zip(table,rows,strict=True):
        for k,v in c.items():
            if k=='independent_validation':continue
            need(v==('' if row[k]is None else str(row[k])),'MEMORY_CSV_FIELD:'+k)
    clarification=read(ROOT/'control/MEMORY_ANALYSIS_CLARIFICATION.v1.json')
    first=min(datetime.fromisoformat(read(p)['started_utc']) for p in (ROOT/'runs/memory-v1').rglob('REQUEST.json'))
    need(datetime.strptime(clarification['observed_utc'],'%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)<first,'CLARIFICATION_NOT_PRECALL')
    warm=[r for r in rows if r['cell_id']=='W']
    report={'schema':'full-independent-memory-and-logical-audit.v1','observed_utc':datetime.now(timezone.utc).isoformat(),
       'verdict':'VERIFICATION_PASS_MEMORY_AND_COMBINED_LOGICAL_CLAIMS_WITH_SCOPED_LIMITS',
       'audit_code_sha256':sha(Path(__file__)),'raw_memory_audit_sha256':sha(raw_path),'producer_result_sha256':sha(producer_path),'producer_csv_sha256':sha(csvpath),
       'source_denominator_sha256':sha(dpath),'analysis_clarification_sha256':sha(ROOT/'control/MEMORY_ANALYSIS_CLARIFICATION.v1.json'),
       'totals':totals,'contrast_summaries':contrasts,'all12_packet_mappings_and_extended_fields_match':True,
       'packet_mapping':packet_mapping,'warm_matching_evaluations':sum(r['evaluations_matching_supplied_retained_schedule'] for r in warm),
       'warm_direct_submission_matches':sum(r['direct_submissions_matching_supplied_retained'] for r in warm),
       'warm_direct_matches_task_replicate_order':[lookup[(t,r,'W')]['direct_submissions_matching_supplied_retained'] for t in ('synthetic-20-v1','synthetic-23-v1') for r in (1,2)],
       'current_target_incumbents_fixed_for_all_WUC':{'synthetic-20-v1':24,'synthetic-23-v1':31},'full_primary_frontier':frontier,
       'combined_actual_counts':{'primary_calls':119,'cohort_calls':24,'memory_calls':36,'included_actual_calls':179,'returned_calls':178,
          'primary_candidate_records':3098,'cohort_actual_records':908,'memory_records':939,'actual_candidate_records_total':4945,
          'excluded_browser_substantive_attempts':2,'accepted_browser_actions':0},
       'logical_limits':['Warm matching counts are observed schedule identity, not evidence of a copying mechanism; direct submissions reported separately.',
          'Three source-relative cost improvements do not beat full-primary frontier24/29. New index schedules do not prove new mathematical graphs or global novelty.',
          'Primary TIMEOUT retains valid partial24-cost; completion and valid-candidate rates remain separate and timeout token usage is unknown.',
          'Cohort cost deltas allzero, mixed duplication/region effects; static peer snapshot, not persistent autonomous cooperation.',
          'Memory packets are unequal in size and expose known target-specific certificates. Four paired observations/two exposed tasks do not establish general memory benefits.',
          'Browser B late body parsed only, timing UNKNOWN. V131.504s send-to-stop-request violates120s bound; no controlled browser B/V math comparison.'],
       'independence_ceiling':'same configured reviewer model family; separate arithmetic code frozen before harness; no OS ACL isolation, optimality or Apex/runtime admission'}
    out=HERE/'MEMORY_AUDIT.v1.json';out.write_text(json.dumps(report,indent=2)+'\n')
    used=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());need(used<4000000,'ORACLE_ARTIFACT_CAP')
    print(json.dumps({'verdict':report['verdict'],'totals':totals,'warm_matches':report['warm_matching_evaluations'],
        'warm_direct_matches':report['warm_direct_submission_matches'],'contrasts':contrasts,'receipt_sha256':sha(out),'oracle_bytes':used}))

if __name__=='__main__':
    try:main()
    except Exception as exc:
        p=HERE/('MEMORY_METRICS_FIRST_FAILURE-'+datetime.now(timezone.utc).strftime('%H%M%S')+'.json')
        p.write_text(json.dumps({'state':'VERIFICATION_FAIL_PRESERVED','reason':str(exc)},indent=2)+'\n')
        print(json.dumps({'state':'VERIFICATION_FAIL_PRESERVED','reason':str(exc),'receipt':str(p)}));raise
