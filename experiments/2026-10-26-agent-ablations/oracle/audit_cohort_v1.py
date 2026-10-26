"""Independent data-only cohort audit; browser late body is parsed, never applied."""
import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import evaluate
from integration_audit_v1 import transform

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PINS=[]; CALLS=[]; CANDIDATES=[]; CONTEXT={}

def need(ok,why):
    if not ok: raise AssertionError(why)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def read(p):
    raw=p.read_bytes();PINS.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    return json.loads(raw.decode('utf-8-sig'))
def rows(p):
    raw=p.read_bytes();PINS.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    return [json.loads(x) for x in raw.decode().splitlines() if x.strip()]
def identity(c,target):
    return hashlib.sha256(canon({'target':str(target),'steps':[sorted(x) for x in c['steps']],'output_index':c.get('output_index',len(c['steps']))}).encode()).hexdigest()
def region(r):
    return canon({'method':r['method'],'knobs':r['knobs']}) if r['method']!='explicit' else 'explicit:'+str(r['assessment'].get('canonical_schedule_sha256'))

def environment(folder,task,namespace,round_count,actual_rounds):
    allrows=[];events=[];best=None;rank=None;seenraw=set();seencanon=set()
    for n in range(1,round_count+1):
        event=read(folder/f'environment/round-{n:02d}.event.json');child=rows(folder/f'environment/round-{n:02d}.candidates.jsonl')
        need(event['evaluated_candidates']==len(child)<=64,'EVALUATION_CAP_OR_COUNT')
        need(event['action_sha256']==sha(folder/f'environment/round-{n:02d}.action.bin'),'ACTION_HASH')
        visible=[]
        for record in child:
            CONTEXT.update(namespace=namespace,round=n,candidate=record['candidate_id'])
            need(record['action_id']==event['event_id'] and record['source_action_sha256']==event['action_sha256'],'ACTION_PROVENANCE')
            need(record['global_evaluation_ordinal']==len(allrows)+1,'EVALUATION_ORDINAL')
            c=record['candidate'];a=record['assessment'];v=evaluate.evaluate_payload(c,task['id'])
            need(v['arithmetic_valid']==a['valid'],'VALIDITY')
            rawhash=hashlib.sha256(canon(c).encode()).hexdigest() if c is not None else None
            h=identity(c,task['target']) if v['arithmetic_valid'] else None
            need(rawhash==a.get('raw_candidate_sha256'),'RAW_CANDIDATE_HASH')
            need(record['raw_duplicate']==bool(rawhash and rawhash in seenraw),'RAW_DUPLICATE')
            need(record['canonical_schedule_duplicate']==bool(h and h in seencanon),'SCHEDULE_DUPLICATE')
            if rawhash:seenraw.add(rawhash)
            if h:seencanon.add(h)
            if v['arithmetic_valid']:
                need(v['charged']==a['charged'] and v['live']==a['live'],'CHARGED_OR_LIVE')
                need(v['dead']['operations']==a['dead']['operations'] and v['dead']['node_indices']==a['dead']['row_indices'],'DEAD_ROWS')
                need(h==a['canonical_schedule_sha256'],'INDEX_IDENTITY')
                r=(v['charged']['operations'],v['charged']['M'],h)
                if rank is None or r<rank:rank,best=r,record
            qualified=namespace+f'/round-{n:02d}/'+record['event_id']
            CANDIDATES.append({'qualified_id':qualified,'actual_execution':n in actual_rounds,'valid':v['arithmetic_valid'],
                               'cost':v.get('charged',{}).get('operations'),'S':v.get('charged',{}).get('S'),
                               'M':v.get('charged',{}).get('M'),'live':v.get('live',{}).get('operations'),
                               'dead':v.get('dead',{}).get('operations'),'schedule_sha256':h})
            visible.append({'candidate_id':record['candidate_id'],'valid':a['valid'],'reason':a.get('reason'),
                            'charged':a.get('charged'),'live':a.get('live'),'dead':a.get('dead'),'duplicate':record['canonical_schedule_duplicate']})
            allrows.append(record)
        wanted={'status':event['status'],'reason':event['reason'],'receipt_id':event['event_id'],'round':n,'rounds_remaining':2-n,
                'evaluations':visible,'censored_candidates':event['censored_candidates'],
                'best_so_far':None if best is None else {'candidate_id':best['candidate_id'],'candidate':best['candidate'],
                    'charged':best['assessment']['charged'],'live':best['assessment']['live'],'dead':best['assessment']['dead']}}
        need(read(folder/f'environment/round-{n:02d}.feedback.json')==wanted,'VISIBLE_FEEDBACK_OR_AGGREGATE')
        events.append(event)
    previous=None
    for n in range(round_count+1):
        p=folder/f'environment/STATE-{n:03d}.json';s=read(p)
        need(s['previous_state_sha256']==previous and s['rounds_used']==n and s['max_rounds']==2,'STATE_CHAIN')
        need(s['target']==task['target'] and s['task_id']==task['id'] and s['tools_enabled'] and s['feedback_enabled'],'STATE_TREATMENT')
        previous=sha(p)
    need(s['candidate_evaluations']==len(allrows),'STATE_EVALUATION_TOTAL')
    need(s['best']['candidate']==best['candidate'],'STATE_BEST')
    return {'records':allrows,'events':events,'rank':rank,'best':best}

def call(folder,n,worker,task,own,peers,template):
    model=folder/f'model-round-{n}';request=read(model/'REQUEST.json');receipt=read(model/'RECEIPT.json')
    need(request['model']=={'A':'gpt-6.1-sol','B':'gpt-6-luna'}[worker] and request['effort']=='medium' and request['automatic_retries']==0,'MODEL_OR_RETRY')
    need(request['profile_sha256']==sha(ROOT/'control/CODEX_PROFILE.json') and request['schema_sha256']==sha(ROOT/'stimuli/action.v2.schema.json'),'CALL_PROFILE')
    prompt=(model/'prompt.txt').read_text();wanted=template.format(worker=worker,target=task['target'],baseline=task['binary_baseline'],
        skill=(ROOT/'stimuli/skill.txt').read_text(),round=n,own=json.dumps(own,separators=(',',':')),peers=json.dumps(peers,separators=(',',':')))
    need(prompt==wanted and hashlib.sha256(prompt.encode()).hexdigest()==request['prompt_sha256'],'PROMPT_OR_PEER_MASK')
    need('oracle/' not in prompt.lower() and 'oracle\\' not in prompt.lower() and '__r' not in prompt,'PROMPT_PATH_LEAK')
    stream=rows(model/'events.jsonl');native=[e['item'] for e in stream if isinstance(e.get('item'),dict) and e['item'].get('type') not in ('agent_message','reasoning')]
    need(not native and receipt['native_tool_events']==0 and receipt['state']=='RETURNED' and receipt['returncode']==0,'CALL_OR_NATIVE_EVENT')
    done=[e for e in stream if e.get('type')=='turn.completed'];need(len(done)==1 and done[0].get('usage',{})==receipt['usage'],'CALL_USAGE')
    proposal=read(model/'answer.json');action=read(folder/f'action-{n}.json');feedback=read(folder/f'feedback-{n}.json')
    need(sha(model/'answer.json')==receipt['answer_sha256'] and transform(proposal)==action,'TRANSFORM')
    need(action==read(folder/f'environment/round-{n:02d}.event.json')['parsed_action'],'ACTION_EVENT')
    need(feedback==read(folder/f'environment/round-{n:02d}.feedback.json'),'FEEDBACK_COPY')
    need(sha(folder/f'action-{n}.json')==sha(folder/f'environment/round-{n:02d}.action.bin'),'ACTION_CAPTURE')
    start=datetime.fromisoformat(request['started_utc']);end=datetime.fromisoformat(receipt['ended_utc'])
    need(start<=end and start<datetime(2026,10,26,19,24,8,tzinfo=timezone.utc),'CALL_HORIZON')
    CALLS.append({'namespace':str(folder.relative_to(ROOT)),'round':n,'start':request['started_utc'],'end':receipt['ended_utc'],'usage':receipt['usage']})
    return {'state':'RETURNED','receipt':receipt,'action':action,'visible_feedback':feedback}

def main():
    need(sha(HERE/'evaluate.py')=='826aff70f4a60f6527c2d2e3f4aa6181d009a60fb26c32f43743b0da03dc046d','ORACLE_DRIFT')
    need(sha(ROOT/'control/run_cohort_v2.py')=='bbfc713cc74d72d73b12280fb95812c449a6a32d5e38d16db25f53d8f2c0ea38','COHORT_RUNNER_DRIFT')
    order=read(ROOT/'control/COHORT_RUN_ORDER.json');template=(ROOT/'stimuli/COHORT_TEMPLATE.v1.txt').read_text()
    computed=[];paired=[];actual_evals=0;initial_evals=0
    for job in order:
        task=job['task'];pair_id=task['id']+'__r'+str(job['replicate']);base=ROOT/'runs/cohort-v1'/pair_id
        CONTEXT.clear();CONTEXT.update(pair=pair_id)
        pair=read(base/'PAIR_RECEIPT.json');initial=read(base/'INITIAL_RESULTS.json')
        need(pair['state']=='COMPLETED' and pair['branch_order']==job['arms'],'PAIR_STATUS_OR_ORDER')
        initial_data={};initial_tokens={};initial_regions=set()
        for w in ('A','B'):
            f=base/'initial'/w;observed=call(f,1,w,task,[],[],template);need(observed==initial[w],'INITIAL_RESULT_COPY')
            expected=pair['initial_state_file_pins'][w]
            actual={str(p.relative_to(f/'environment')).replace('\\','/'):sha(p) for p in (f/'environment').rglob('*') if p.is_file()}
            need(actual==expected,'INITIAL_FILE_MAP')
            data=environment(f,task,pair_id+'/initial/'+w,1,{1});initial_data[w]=data
            actual_evals+=len(data['records']);initial_evals+=len(data['records']);initial_regions|={region(r) for r in data['records']}
        arm_rows={}
        for arm in ('private','shared'):
            result=read(base/arm/'BRANCH_RESULT.json');need(result['state']=='COMPLETED','BRANCH_STATUS')
            datasets={};secondsets={};secondregions=set();tokens_in=tokens_out=0
            for w in ('A','B'):
                folder=base/arm/w
                for rel,h in pair['initial_state_file_pins'][w].items():need(sha(folder/'environment'/rel)==h,'CLONE_PREFIX_BYTE_DRIFT')
                peer='B' if w=='A' else 'A';own=[{'action':initial[w]['action'],'visible_feedback':initial[w]['visible_feedback']}]
                peers=[{'worker':peer,'action':initial[peer]['action'],'visible_feedback':initial[peer]['visible_feedback']}] if arm=='shared' else []
                observed=call(folder,2,w,task,own,peers,template);need(observed==result['second_decisions'][w],'SECOND_RESULT_COPY')
                data=environment(folder,task,pair_id+'/'+arm+'/'+w,2,{2});datasets[w]=data
                final=result['worker_finals'][w]
                need(final['events']==data['events'] and final['candidate_evaluations']==len(data['records']) and final['complete'],'WORKER_FINAL_DENOMINATOR')
                need(final['best_candidate']==data['best']['candidate'] and final['best_local_assessment']==data['best']['assessment'],'WORKER_FINAL_MINIMUM')
                second=[r for r in data['records'] if r['round']==2];actual_evals+=len(second)
                secondsets[w]={r['assessment']['canonical_schedule_sha256'] for r in second if r['assessment']['valid']}
                secondregions|={region(r) for r in second}
                for receipt in (initial[w]['receipt'],observed['receipt']):tokens_in+=receipt['usage'].get('input_tokens',0);tokens_out+=receipt['usage'].get('output_tokens',0)
            allrecords=datasets['A']['records']+datasets['B']['records'];valid=[r for r in allrecords if r['assessment']['valid']]
            need(len(valid)==len(allrecords),'UNEXPECTED_INVALID_REQUIRES_SEPARATE_DUPLICATE_DEFINITION')
            best=min(valid,key=lambda r:(r['assessment']['charged']['operations'],r['assessment']['charged']['M'],r['assessment']['canonical_schedule_sha256']))
            sets={w:{r['assessment']['canonical_schedule_sha256'] for r in datasets[w]['records'] if r['assessment']['valid']} for w in ('A','B')}
            allhashes=sets['A']|sets['B'];a=best['assessment']
            row={'pair_id':pair_id,'task_id':task['id'],'replicate_id':job['replicate'],'arm':arm,'state':'COMPLETED',
                 'best_valid_cost':a['charged']['operations'],'best_S':a['charged']['S'],'best_M':a['charged']['M'],'best_identity':a['canonical_schedule_sha256'],
                 'branch_evaluations_including_common_initial':len(allrecords),'unique_schedules':len(allhashes),'duplicate_evaluations':len(valid)-len(allhashes),
                 'between_worker_schedule_overlap':len(sets['A']&sets['B']),'second_worker_schedule_overlap':len(secondsets['A']&secondsets['B']),
                 'new_second_regions_over_team_initial':len(secondregions-initial_regions),'second_action_A':result['second_decisions']['A']['action'],
                 'second_action_B':result['second_decisions']['B']['action'],'branch_accounted_model_calls':4,
                 'branch_input_tokens_including_common_initial':tokens_in,'branch_output_tokens_including_common_initial':tokens_out}
            computed.append(row);arm_rows[arm]=row
        s,p=arm_rows['shared'],arm_rows['private']
        paired.append({'pair_id':pair_id,'task_id':task['id'],'replicate_id':job['replicate'],'state':'COMPLETED','shared_cost':s['best_valid_cost'],'private_cost':p['best_valid_cost'],
                       'cost_shared_minus_private':s['best_valid_cost']-p['best_valid_cost'],
                       'duplicate_evaluations_shared_minus_private':s['duplicate_evaluations']-p['duplicate_evaluations'],
                       'worker_overlap_shared_minus_private':s['between_worker_schedule_overlap']-p['between_worker_schedule_overlap'],
                       'new_second_regions_shared_minus_private':s['new_second_regions_over_team_initial']-p['new_second_regions_over_team_initial'],
                       'action_A_changed':s['second_action_A']!=p['second_action_A'],'action_B_changed':s['second_action_B']!=p['second_action_B']})
    need(len(CALLS)==24 and len({(c['namespace'],c['round']) for c in CALLS})==24,'ACTUAL_CALL_DENOMINATOR')
    need(len({r['qualified_id'] for r in CANDIDATES})==len(CANDIDATES),'PATH_QUALIFIED_ID_COLLISION')
    need(sum(r['actual_execution'] for r in CANDIDATES)==actual_evals,'ACTUAL_VS_CLONED_ACCOUNTING')
    sweep=sorted([(datetime.fromisoformat(c['start']),1) for c in CALLS]+[(datetime.fromisoformat(c['end']),-1) for c in CALLS],key=lambda x:(x[0],x[1]))
    active=maximum=0
    for _,delta in sweep:active+=delta;maximum=max(maximum,active)
    need(active==0 and maximum<=2,'COHORT_CONCURRENCY')
    totals={'pairs':4,'branches':8,'actual_model_calls':24,'returned_calls':24,'actual_candidate_evaluations_initial_once':actual_evals,
            'sum_counterfactual_branch_evaluations':sum(r['branch_evaluations_including_common_initial'] for r in computed),
            'actual_model_input_tokens':sum(c['usage'].get('input_tokens',0) for c in CALLS),
            'actual_model_output_tokens':sum(c['usage'].get('output_tokens',0) for c in CALLS),'native_tool_events':0}
    producer_path=ROOT/'analysis/COHORT_RESULTS.json';producer=read(producer_path)
    need(computed==producer['rows'] and paired==producer['pairs'] and totals==producer['totals'],'PRODUCER_COHORT_ROW_OR_METRIC_MISMATCH')
    primary=read(ROOT/'analysis/PRIMARY_RESULTS.json');need(sha(ROOT/'analysis/PRIMARY_RESULTS.json')=='5d884748187c90fb7413a9ba17e65103955ea736ad142da26826945c93f75ac8','PRIMARY_APPEND_SOURCE_DRIFT')
    appendix=read(ROOT/'analysis/EXPLORATORY_M_MINUS_B.json');lookup={(r['task_id'],r['replicate_id'],r['cell_id'],r['model']):r for r in primary['rows']}
    for entry in appendix['pairs']:
        t=lookup[(entry['task_id'],entry['replicate_id'],'M','gpt-6.1-sol')];c=lookup[(entry['task_id'],entry['replicate_id'],'B','gpt-6.1-sol')]
        need(entry['cost_delta_treatment_minus_control']==t['best_valid_cost']-c['best_valid_cost'],'M_MINUS_B_APPENDIX')
    browser=read(ROOT/'runs/browser-v1/RECONCILIATION_RECEIPT.json');late=ROOT/'runs/browser-v1'/browser['B']['late_body_file'];raw=late.read_bytes()
    need(sha(late)==browser['B']['late_body_sha256'] and len(raw)==browser['B']['late_body_bytes']==723,'LATE_BODY_PIN')
    parsed=json.loads(raw);need(type(parsed)is dict and parsed.get('type')=='submit_chain','LATE_BODY_JSON_PARSE')
    for arm in ('B','V'):
        b=ROOT/f'runs/browser-v1/synthetic-20-v1__r1__{arm}__freebrowser';need((b/'round-1/response.txt').stat().st_size==0 and (b/'round-1/raw_capture.txt').stat().st_size==0,'ORIGINAL_BROWSER_CAPTURE_CHANGED')
        final=read(b/'TRUSTED_FINAL.json');need(final['candidate_evaluations']==0 and final['rounds_used']==0,'EXCLUDED_BROWSER_ACTION_ACCEPTED')
    delay=(datetime.fromisoformat(browser['V']['stop_request_utc'].replace('Z','+00:00'))-datetime.fromisoformat(browser['V']['send_utc'].replace('Z','+00:00'))).total_seconds()
    need(abs(delay-131.504)<1e-9 and browser['V']['strict_120s_stop_bound']=='FAILED','BROWSER_STOP_RECONCILIATION')
    candidate_path=HERE/'COHORT_CANDIDATE_AUDIT.v1.csv'
    with candidate_path.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(CANDIDATES[0]));writer.writeheader();writer.writerows(CANDIDATES)
    report={'schema':'independent-full-cohort-audit.v1','observed_utc':datetime.now(timezone.utc).isoformat(),
            'verdict':'VERIFICATION_PASS_COHORT_WITH_BROWSER_EXCLUSION_CONFIRMED','audit_code_sha256':sha(Path(__file__)),
            'oracle_sha256':sha(HERE/'evaluate.py'),'producer_result_sha256':sha(producer_path),'candidate_audit_sha256':sha(candidate_path),
            'totals':totals,'initial_actual_evaluation_records':initial_evals,'materialized_records_replayed_including_clones':len(CANDIDATES),
            'maximum_observed_cohort_cli_overlap':maximum,'all_cloned_prefixes_byte_identical':True,'all_runtime_prompts_match_declared_own_peer_masks':True,
            'path_qualified_ids_unique':True,'rows':computed,'pairs':paired,'calls':CALLS,
            'M_minus_B_appendix_cost_deltas_verified':[p['cost_delta_treatment_minus_control'] for p in appendix['pairs']],
            'browser_review':{'reconciliation_sha256':sha(ROOT/'runs/browser-v1/RECONCILIATION_RECEIPT.json'),'late_body_sha256':sha(late),
               'JSON_parse':'PASS_DATA_ONLY','late_action_applied':False,'late_candidate_arithmetic_evaluated':False,'accepted_browser_actions':0,
               'B_120s_compliance':'UNKNOWN','V_stop_seconds':delay,'V_overrun_seconds':delay-120,'controlled_B_V_comparison':'NOT_AVAILABLE'},
            'raw_input_pins':list({p['path']:p for p in PINS}.values()),
            'scope':'24 actual calls; initial work counted once. Four pairs/two exposed tasks; no cost gain observed, mixed duplicate/region effects. Same configured reviewer model family; no global optimum, autonomous memory or Apex admission.'}
    out=HERE/'COHORT_AUDIT.v1.json';out.write_text(json.dumps(report,indent=2)+'\n')
    used=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());need(used<4000000,'ORACLE_ARTIFACT_CAP')
    print(json.dumps({'verdict':report['verdict'],'totals':totals,'materialized_records':len(CANDIDATES),'max_cli_overlap':maximum,
        'cost_deltas':[p['cost_shared_minus_private'] for p in paired],'receipt_sha256':sha(out),'oracle_bytes':used}))

if __name__=='__main__':
    try:main()
    except Exception as exc:
        p=HERE/('COHORT_AUDIT_FIRST_FAILURE-'+datetime.now(timezone.utc).strftime('%H%M%S')+'.json')
        p.write_text(json.dumps({'state':'VERIFICATION_FAIL_PRESERVED','context':CONTEXT,'reason':str(exc),'input_pins':PINS},indent=2)+'\n')
        print(json.dumps({'state':'VERIFICATION_FAIL_PRESERVED','reason':str(exc),'context':CONTEXT,'receipt':str(p)}));raise
