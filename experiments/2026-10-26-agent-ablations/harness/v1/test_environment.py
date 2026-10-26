"""Meaningful bounded controls; no oracle key or nonpublic oracle file is read."""
import hashlib
import importlib.util
import json
import time
from pathlib import Path
from ac_environment import Environment,Refusal,binary_candidate,window_candidate,dictionary_candidate,evaluate_candidate,proposals,public_tasks

HERE=Path(__file__).resolve().parent


def check(ok,message):
    if not ok:raise AssertionError(message)


def main():
    stamp=str(time.time_ns());out=HERE/'test-artifacts'/stamp;out.mkdir(parents=True,exist_ok=False);checks=[]
    def record(name,value=True):check(value,name);checks.append({'control':name,'state':'PASS'})
    tasks,_=public_tasks();target=int(tasks['synthetic-20-v1']['target_decimal'])
    binary=binary_candidate(target);score=evaluate_candidate(binary,target)
    record('positive_exact_binary_endpoint',score['valid'] and score['charged']=={'operations':28,'S':19,'M':9} and score['dead']['operations']==0)
    bad={'steps':[list(x) for x in binary['steps']],'output_index':binary['output_index']};bad['steps'][0]=[1,0]
    record('future_reference_rejected',not evaluate_candidate(bad,target)['valid'])
    bad={'steps':[list(x) for x in binary['steps']],'output_index':binary['output_index']};bad['steps'][0]=[True,0]
    record('boolean_index_rejected',not evaluate_candidate(bad,target)['valid'])
    record('wrong_endpoint_rejected',not evaluate_candidate(binary,target+1)['valid'])
    record('base_output_rejected',not evaluate_candidate({'steps':binary['steps'],'output_index':0},target)['valid'])
    record('row_cap_rejected',not evaluate_candidate({'steps':[[0,0]]*257,'output_index':1},2)['valid'])
    dead={'steps':binary['steps']+[[0,0]],'output_index':binary['output_index']};deadscore=evaluate_candidate(dead,target)
    record('dead_row_allowed_and_fully_charged',deadscore['valid'] and deadscore['charged']['operations']==29 and deadscore['live']['operations']==28 and deadscore['dead']['operations']==1)
    dup=evaluate_candidate({'steps':[[0,0],[0,0],[1,2]],'output_index':3},4)
    record('duplicate_exponents_allowed_indices_charged',dup['valid'] and dup['charged']=={'operations':3,'S':2,'M':1})
    changed={'steps':[list(x) for x in binary['steps']],'output_index':binary['output_index']}
    for row in changed['steps']:
        if row[0]!=row[1]:row.reverse();break
    altered=evaluate_candidate(changed,target)
    record('commutative_duplicate_identity',altered['valid'] and altered['canonical_schedule_sha256']==score['canonical_schedule_sha256'] and altered['raw_candidate_sha256']!=score['raw_candidate_sha256'])
    for task in tasks.values():
        t=int(task['target_decimal'])
        for width in range(1,7):
            for variant in ['fixed','sliding']:
                current=evaluate_candidate(window_candidate(t,width,variant),t)
                record(task['task_id']+'-'+variant+'-w'+str(width),current['valid'] and current['dead']['operations']==0)
        d=evaluate_candidate(dictionary_candidate(t,[1,3,5,7,15],4),t)
        record(task['task_id']+'-dictionary',d['valid'] and d['dead']['operations']==0)
    actions,configured=proposals({'type':'search','method':'dictionary','knobs':{'base_digits':[1],'candidate_digits':list(range(2,18)),'max_added_digits':2,'max_window_bits':5},'max_evaluations':64})
    record('configured137_capped64',configured==137 and len(actions)==64)
    enabled=Environment.create(out/'tools-on','synthetic-20-v1',True,True)
    feedback=enabled.act({'type':'search','method':'window','knobs':{'widths':[1,2,3,4,5,6],'variants':['fixed','sliding']},'max_evaluations':64})
    record('feedback_on_exact_cost',feedback['status']=='COMPLETE' and len(feedback['evaluations'])==12 and feedback['best_so_far']['charged']['operations']>0)
    enabled=Environment.load(out/'tools-on');enabled.act({'type':'construct','method':'binary','knobs':{}});enabled=Environment.load(out/'tools-on');enabled.act({'type':'submit_chain',**binary})
    record('restart_round_accounting',enabled.trusted_export()['rounds_used']==3)
    try:enabled.act({'type':'construct','method':'binary','knobs':{}});record('round4_refused',False)
    except Refusal:record('round4_refused')
    off=Environment.create(out/'tools-off','synthetic-20-v1',False,True)
    denied=off.act({'type':'construct','method':'binary','knobs':{}})
    record('tools_off_refuses_search_no_evaluation',denied['status']=='REFUSED' and denied['reason']=='TOOLS_DISABLED' and off.state['candidate_evaluations']==0)
    accepted=off.act({'type':'submit_chain',**binary})
    record('tools_off_explicit_chain_available',accepted['evaluations'][0]['valid'])
    hidden=Environment.create(out/'feedback-off','synthetic-20-v1',True,False)
    ack=hidden.act({'type':'construct','method':'binary','knobs':{}})
    record('feedback_off_only_ack',set(ack)=={'status','receipt_id','round','rounds_remaining'} and ack['status']=='ACK')
    ack2=hidden.act('{malformed JSON')
    record('feedback_off_invalid_action_same_shape',set(ack2)==set(ack) and ack2['status']=='ACK')
    hidden.act({'type':'submit_chain',**dead})
    record('hidden_final_aggregation_retains_lower_charged_binary',hidden.trusted_export()['best_local_assessment']['charged']['operations']==28)
    duplicate=Environment.create(out/'duplicate','synthetic-20-v1',True,True);duplicate.act({'type':'submit_chain',**binary});f=duplicate.act({'type':'submit_chain',**changed})
    record('duplicate_recorded_not_new_credit',f['evaluations'][0]['duplicate'] and duplicate.trusted_export()['unique_canonical_schedules']==1)
    tagged=Environment.create(out/'tagged','synthetic-20-v1',True,True)
    tag_result=tagged.act({'type':'submit_chain','task_id':'synthetic-20-v1',**binary})
    record('public_oracle_action_task_id_accepted',tag_result['evaluations'][0]['valid'])
    wrong_tag=tagged.act({'type':'submit_chain','task_id':'synthetic-23-v1',**binary})
    record('wrong_task_id_refused',wrong_tag['status']=='REFUSED' and wrong_tag['reason']=='TASK_ID_MISMATCH')
    try:Environment.create(HERE/'..'/'..'/'oracle-bypass','synthetic-20-v1',True,True);record('path_traversal_refused',False)
    except Refusal:record('path_traversal_refused')
    result={'schema':'bounded-addition-chain-harness-controls.v1','state':'PASS','controls':checks,'control_count':len(checks),'source_sha256':hashlib.sha256((HERE/'ac_environment.py').read_bytes()).hexdigest(),'public_tasks_sha256':hashlib.sha256((HERE/'PUBLIC_TASKS.json').read_bytes()).hexdigest(),'oracle_private_files_read':False,'artifact_directory':str(out)}
    dest=out/'TEST_RESULT.json';dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'state':'PASS','controls':len(checks),'receipt':str(dest),'harness_sha256':result['source_sha256']}))


if __name__=='__main__':main()
