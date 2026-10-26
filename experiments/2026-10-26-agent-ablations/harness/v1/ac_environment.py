"""Bounded data-only addition-chain environment, release candidate v1.

CLI stdout is the candidate-visible response for init/act. Export is trusted
runner-only. No candidate code is compiled, evaluated or executed.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
MAX_ROWS=256
MAX_ACTION_BYTES=65536
MAX_ROUNDS=3
MAX_EVALS=64
MAX_TRAJECTORY_BYTES=2000000


class Refusal(ValueError):
    pass


def require(ok,code):
    if not ok:raise Refusal(code)


def integer(x,lo=0,hi=10**9):
    require(type(x) is int and lo<=x<=hi,'STRICT_INTEGER_OR_RANGE')
    return x


def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('utf-8')
def digest(data):return hashlib.sha256(data).hexdigest()
def utc():return datetime.now(timezone.utc).isoformat()


def put(path,obj):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,indent=2);f.write('\n')


def safe_directory(path,create=False):
    path=Path(path).absolute()
    require('..' not in path.parts,'PARENT_TRAVERSAL_OUTPUT_REFUSED')
    require(path.is_relative_to(PROJECT),'OUTPUT_OUTSIDE_AUTHORIZED_PROJECT')
    require(path.is_relative_to(PROJECT/'runs') or path.is_relative_to(PROJECT/'harness'),'OUTPUT_SCOPE_NOT_RUNS_OR_HARNESS')
    for p in [path,*path.parents]:
        if p==PROJECT.parent:break
        if p.exists():require(not (getattr(p.lstat(),'st_file_attributes',0)&0x400),'REPARSE_OUTPUT_REFUSED')
    if create:path.mkdir(parents=True,exist_ok=False)
    else:require(path.is_dir(),'ENVIRONMENT_ABSENT')
    return path


def evaluate_candidate(candidate,target):
    """Exact public mathematical contract; no hidden optimum or oracle key.

    Repeated values and dead rows are legal. Every serialized row is charged.
    Canonical duplicate identity normalizes parent order but retains indices,
    row order and declared output. It is not full graph-isomorphism identity.
    """
    raw=canonical(candidate)
    base={'raw_candidate_sha256':digest(raw),'raw_candidate_bytes':len(raw),'valid':False}
    try:
        require(len(raw)<=MAX_ACTION_BYTES,'CANDIDATE_BYTE_CAP')
        require(type(candidate) is dict and set(candidate)<= {'steps','output_index'},'CANDIDATE_FIELDS')
        steps=candidate.get('steps');require(type(steps) is list and 1<=len(steps)<=MAX_ROWS,'ROW_COUNT_CAP_OR_SHAPE')
        target=integer(target,2,1<<256)
        values=[1];parents=[]
        for i,row in enumerate(steps):
            require(type(row) is list and len(row)==2,'INDEX_PAIR_SHAPE')
            a,b=[integer(x,0,i) for x in row]
            values.append(values[a]+values[b]);parents.append((a,b))
        output=integer(candidate.get('output_index',len(steps)),1,len(steps))
        require(values[output]==target,'WRONG_ENDPOINT')
        live={output};todo=[output]
        while todo:
            node=todo.pop()
            if node:
                for p in parents[node-1]:
                    if p not in live:live.add(p);todo.append(p)
        s=sum(a==b for a,b in parents);m=len(parents)-s
        ls=sum(i in live and a==b for i,(a,b) in enumerate(parents,1));lm=sum(i in live and a!=b for i,(a,b) in enumerate(parents,1))
        schedule={'target':str(target),'steps':[sorted(p) for p in parents],'output_index':output}
        base.update({'valid':True,'reason':None,'charged':{'operations':len(parents),'S':s,'M':m},'live':{'operations':ls+lm,'S':ls,'M':lm},
            'dead':{'operations':len(parents)-ls-lm,'row_indices':sorted(set(range(1,len(values)))-live)},'output_index':output,'endpoint_decimal':str(values[output]),
            'canonical_schedule_sha256':digest(canonical(schedule)),'canonical_scope':'commutative index schedule, row multiplicity/order and output retained; not graph-isomorphism canonicalization'})
    except (Refusal,ValueError,TypeError) as error:base['reason']=str(error)
    return base


class Builder:
    def __init__(self):self.steps=[];self.values=[1];self.byvalue={1:0}
    def add(self,a,b):
        value=self.values[a]+self.values[b]
        if value in self.byvalue:return self.byvalue[value]
        require(len(self.steps)<MAX_ROWS,'CONSTRUCTOR_ROW_CAP')
        self.steps.append([a,b]);self.values.append(value);self.byvalue[value]=len(self.steps)
        return len(self.steps)
    def ensure(self,value):
        if value in self.byvalue:return self.byvalue[value]
        half=self.ensure(value//2);result=self.add(half,half)
        if value%2:result=self.add(result,0)
        return result
    def finish(self,output):
        # This is compilation of the tool's own construction, never a repair
        # or pruning operation on a submitted candidate.
        live={output};todo=[output]
        while todo:
            node=todo.pop()
            if node:
                for p in self.steps[node-1]:
                    if p not in live:live.add(p);todo.append(p)
        mapping={0:0};steps=[]
        for i,(a,b) in enumerate(self.steps,1):
            if i in live:steps.append([mapping[a],mapping[b]]);mapping[i]=len(steps)
        return {'steps':steps,'output_index':mapping[output]}


def binary_candidate(target):
    b=Builder();acc=0
    for digit in bin(target)[3:]:
        acc=b.add(acc,acc)
        if digit=='1':acc=b.add(acc,0)
    return b.finish(acc)


def segments_for_window(target,width,variant):
    bits=bin(target)[2:];segments=[]
    if variant=='fixed':
        first=len(bits)%width or width;pos=0
        while pos<len(bits):
            w=first if pos==0 else min(width,len(bits)-pos)
            segments.append((w,int(bits[pos:pos+w],2)));pos+=w
    else:
        pos=0
        while pos<len(bits):
            if bits[pos]=='0':segments.append((1,0));pos+=1;continue
            end=min(len(bits),pos+width)
            while bits[end-1]=='0':end-=1
            segments.append((end-pos,int(bits[pos:end],2)));pos=end
    return segments


def compile_segments(target,segments,digits):
    b=Builder();indices={d:b.ensure(d) for d in sorted(set(digits)|{1})}
    first_width,first_digit=segments[0];require(first_digit in indices,'LEADING_DIGIT_NOT_PRECOMPUTED');acc=indices[first_digit]
    for width,digit in segments[1:]:
        for _ in range(width):acc=b.add(acc,acc)
        if digit:acc=b.add(acc,indices[digit])
    require(b.values[acc]==target,'CONSTRUCTOR_ENDPOINT_BUG')
    return b.finish(acc)


def window_candidate(target,width,variant):
    width=integer(width,1,6);require(variant in ['fixed','sliding'],'WINDOW_VARIANT')
    segments=segments_for_window(target,width,variant)
    return compile_segments(target,segments,[d for _,d in segments if d])


def digit_list(value,max_items=64):
    require(type(value) is list and 1<=len(value)<=max_items,'DIGIT_LIST_SHAPE')
    digits=[integer(x,1,63) for x in value]
    require(len(set(digits))==len(digits),'DUPLICATE_DIGIT_KNOB')
    return sorted(digits)


def dictionary_candidate(target,digits,width):
    digits=digit_list(digits);width=integer(width,1,6)
    require(1 in digits and all(d<(1<<width) for d in digits),'DICTIONARY_DIGIT_OR_WIDTH')
    allowed=set(digits);bits=bin(target)[2:];n=len(bits);dp=[None]*(n+1);choice=[None]*(n+1);dp[n]=(0,0,0)
    for i in range(n-1,0,-1):
        for w in range(1,min(width,n-i)+1):
            d=int(bits[i:i+w],2)
            if (not d or d in allowed) and dp[i+w] is not None:
                tail=dp[i+w];score=(tail[0]+w+bool(d),tail[1]+w,tail[2]+bool(d))
                if dp[i] is None or (score[0],score[2],score[1])<(dp[i][0],dp[i][2],dp[i][1]):dp[i]=score;choice[i]=(w,d)
    first=None;best=None
    for w in range(1,min(width,n)+1):
        d=int(bits[:w],2)
        if d in allowed and dp[w] is not None:
            score=dp[w]
            if best is None or (score[0],score[2],score[1])<(best[0],best[2],best[1]):best=score;first=(w,d)
    require(first is not None,'DICTIONARY_UNREACHABLE')
    segments=[first];pos=first[0]
    while pos<n:
        require(choice[pos] is not None,'DICTIONARY_PATH_BUG');segments.append(choice[pos]);pos+=choice[pos][0]
    return compile_segments(target,segments,digits)


def proposals(action):
    """Return bounded deterministic genotype definitions, never executable code."""
    require(type(action) is dict,'ACTION_OBJECT')
    kind=action.get('type')
    if kind=='submit_chain':
        require(set(action)<={'type','task_id','steps','output_index'},'ACTION_FIELDS')
        candidate={'steps':action.get('steps')}
        if 'output_index' in action:candidate['output_index']=action['output_index']
        return [('explicit',candidate)],1
    require(kind in ['construct','search'],'ACTION_TYPE')
    require(set(action)<={'type','task_id','method','knobs','max_evaluations'},'ACTION_FIELDS')
    method=action.get('method');knobs=action.get('knobs',{});require(type(knobs) is dict,'KNOBS_OBJECT')
    cap=integer(action.get('max_evaluations',64),1,64)
    if kind=='construct':
        if method=='binary':require(not knobs,'BINARY_KNOBS');return [('binary',{})],1
        if method=='window':
            require(set(knobs)<={'width','variant'},'WINDOW_KNOBS');width=integer(knobs.get('width',4),1,6);variant=knobs.get('variant','sliding');require(variant in ['fixed','sliding'],'WINDOW_VARIANT')
            return [('window',{'width':width,'variant':variant})],1
        if method=='dictionary':
            require(set(knobs)<={'digits','max_window_bits'},'DICTIONARY_KNOBS');digits=digit_list(knobs.get('digits',[1,3,5,7,15]));width=integer(knobs.get('max_window_bits',4),1,6)
            return [('dictionary',{'digits':digits,'max_window_bits':width})],1
        raise Refusal('CONSTRUCT_METHOD')
    if method=='window':
        require(set(knobs)<={'widths','variants'},'WINDOW_SEARCH_KNOBS');widths=knobs.get('widths',[1,2,3,4,5,6]);variants=knobs.get('variants',['fixed','sliding'])
        require(type(widths) is list and 1<=len(widths)<=6 and len(set(widths))==len(widths),'WINDOW_WIDTH_LIST');widths=sorted(integer(x,1,6) for x in widths)
        require(type(variants) is list and 1<=len(variants)<=2 and all(x in ['fixed','sliding'] for x in variants) and len(set(variants))==len(variants),'WINDOW_VARIANT_LIST')
        definitions=[('window',{'width':w,'variant':v}) for w in widths for v in sorted(variants)]
        return definitions[:cap],len(definitions)
    if method=='dictionary':
        require(set(knobs)<={'base_digits','candidate_digits','max_added_digits','max_window_bits'},'DICTIONARY_SEARCH_KNOBS')
        base=digit_list(knobs.get('base_digits',[1,3,5]));require(1 in base,'DICTIONARY_BASE_ONE_REQUIRED')
        extras=knobs.get('candidate_digits',[7,9,11,15,31]);require(type(extras) is list and len(extras)<=16,'EXTRA_DIGIT_LIST');extras=[] if not extras else digit_list(extras,16)
        extras=[d for d in extras if d not in base];maximum=integer(knobs.get('max_added_digits',1),0,2);width=integer(knobs.get('max_window_bits',5),1,6)
        total=sum(math.comb(len(extras),k) for k in range(maximum+1) if k<=len(extras));definitions=[]
        for k in range(maximum+1):
            for combo in itertools.combinations(extras,k):
                if len(definitions)<cap:definitions.append(('dictionary',{'digits':sorted(base+list(combo)),'max_window_bits':width}))
        return definitions,total
    raise Refusal('SEARCH_METHOD')


def public_tasks():
    path=HERE/'PUBLIC_TASKS.json';b=path.read_bytes();d=json.loads(b)
    return {t['task_id']:t for t in d['tasks']},digest(b)


class Environment:
    @classmethod
    def create(cls,output,task_id,tools_enabled=True,feedback_enabled=True,max_rounds=3):
        require(type(tools_enabled) is bool and type(feedback_enabled) is bool,'TREATMENT_BOOLEAN')
        maximum=integer(max_rounds,1,MAX_ROUNDS);tasks,task_hash=public_tasks();require(task_id in tasks,'UNKNOWN_PUBLIC_TASK')
        t=tasks[task_id];target=integer(int(t['target_decimal']),1<<15,(1<<24)-1)
        folder=safe_directory(output,create=True)
        state={'schema':'bounded-addition-chain-environment-state.v1','environment_id':str(uuid.uuid4()),'created_utc':utc(),'task_id':task_id,'target':target,'public_tasks_sha256':task_hash,'harness_sha256':digest(Path(__file__).read_bytes()),
            'tools_enabled':tools_enabled,'feedback_enabled':feedback_enabled,'max_rounds':maximum,'rounds_used':0,'candidate_evaluations':0,'best':None,'seen_raw':[],'seen_canonical':[],'previous_state_sha256':None}
        put(folder/'STATE-000.json',state)
        return cls(folder,state)
    @classmethod
    def load(cls,output):
        folder=safe_directory(output);files=sorted(folder.glob('STATE-[0-9][0-9][0-9].json'));require(bool(files),'STATE_MISSING')
        prior=None
        for path in files:
            b=path.read_bytes();state=json.loads(b);require(state['previous_state_sha256']==prior,'STATE_CHAIN_DRIFT');prior=digest(b)
        require(state['harness_sha256']==digest(Path(__file__).read_bytes()),'HARNESS_RELEASE_DRIFT')
        require(state['public_tasks_sha256']==public_tasks()[1],'PUBLIC_TASK_DRIFT')
        return cls(folder,state)
    def __init__(self,folder,state):self.folder=folder;self.state=state
    def public_init(self):
        return {'status':'READY','environment_id':self.state['environment_id'],'task_id':self.state['task_id'],'target_decimal':str(self.state['target']),'tools_enabled':self.state['tools_enabled'],'feedback_enabled':self.state['feedback_enabled'],'max_rounds':self.state['max_rounds'],'max_evaluations_per_search':64,'max_rows':256}
    def act(self,raw):
        require(type(raw) in [bytes,str,dict],'RAW_ACTION_TYPE')
        original=canonical(raw) if type(raw) is dict else raw.encode('utf-8') if type(raw) is str else raw
        require(self.state['rounds_used']<self.state['max_rounds'],'ROUND_LIMIT')
        require(sum(p.stat().st_size for p in self.folder.iterdir() if p.is_file())<MAX_TRAJECTORY_BYTES-800000,'TRAJECTORY_ARTIFACT_CAP')
        round_no=self.state['rounds_used']+1;stem='round-'+str(round_no).zfill(2);receipt_id=str(uuid.uuid4());started=utc();wall=time.perf_counter();cpu=time.process_time()
        require(not (self.folder/(stem+'.event.json')).exists(),'PARTIAL_OR_DUPLICATE_ROUND_HOLD')
        action=None;status='COMPLETE';reason=None;definitions=[];configured=0;records=[];visible=[]
        try:
            require(len(original)<=MAX_ACTION_BYTES,'ACTION_BYTE_CAP')
            action=json.loads(original.decode('utf-8'))
            if type(action) is dict and 'task_id' in action:require(action['task_id']==self.state['task_id'],'TASK_ID_MISMATCH')
            definitions,configured=proposals(action)
            if action.get('type')!='submit_chain':require(self.state['tools_enabled'],'TOOLS_DISABLED')
            for local_index,(method,knobs) in enumerate(definitions,1):
                require(local_index<=64,'EVALUATION_CAP')
                try:
                    candidate=knobs if method=='explicit' else binary_candidate(self.state['target']) if method=='binary' else window_candidate(self.state['target'],knobs['width'],knobs['variant']) if method=='window' else dictionary_candidate(self.state['target'],knobs['digits'],knobs['max_window_bits'])
                    assessment=evaluate_candidate(candidate,self.state['target'])
                except (Refusal,ValueError,KeyError,TypeError) as error:
                    candidate=None;assessment={'valid':False,'reason':'CONSTRUCTION_REFUSED:'+str(error),'raw_candidate_sha256':None}
                ordinal=self.state['candidate_evaluations']+1;candidate_id=stem+'-candidate-'+str(local_index).zfill(2)
                rawhash=assessment.get('raw_candidate_sha256');canonhash=assessment.get('canonical_schedule_sha256')
                rawdup=bool(rawhash and rawhash in self.state['seen_raw']);canonicaldup=bool(canonhash and canonhash in self.state['seen_canonical'])
                if rawhash:self.state['seen_raw'].append(rawhash)
                if canonhash:self.state['seen_canonical'].append(canonhash)
                record={'schema':'bounded-addition-chain-evaluation.v1','environment_id':self.state['environment_id'],'event_id':self.state['environment_id']+':evaluation:'+str(ordinal),'action_id':receipt_id,'candidate_id':candidate_id,'global_evaluation_ordinal':ordinal,'round':round_no,'method':method,'knobs':knobs if method!='explicit' else None,'candidate':candidate,'assessment':assessment,'raw_duplicate':rawdup,'canonical_schedule_duplicate':canonicaldup,'source_action_sha256':digest(original)}
                records.append(record);self.state['candidate_evaluations']=ordinal
                if assessment['valid']:
                    rank=(assessment['charged']['operations'],assessment['charged']['M'],canonhash)
                    current=self.state['best']
                    if current is None or rank<tuple(current['rank']):self.state['best']={'candidate_id':candidate_id,'candidate':candidate,'assessment':assessment,'rank':list(rank)}
                visible.append({'candidate_id':candidate_id,'valid':assessment['valid'],'reason':assessment.get('reason'),'charged':assessment.get('charged'),'live':assessment.get('live'),'dead':assessment.get('dead'),'duplicate':canonicaldup})
        except (Refusal,ValueError,UnicodeError,TypeError) as error:status='REFUSED';reason=str(error)
        # Raw action is preserved as bytes; oversize actions retain bounded prefix
        # and explicit capture scope. The runner retains original model output.
        with (self.folder/(stem+'.action.bin')).open('xb') as f:f.write(original[:MAX_ACTION_BYTES+1])
        with (self.folder/(stem+'.candidates.jsonl')).open('x',encoding='utf-8') as f:
            for record in records:f.write(json.dumps(record,sort_keys=True,separators=(',',':'))+'\n')
        event={'schema':'bounded-addition-chain-action-event.v1','environment_id':self.state['environment_id'],'event_id':receipt_id,'action_id':receipt_id,'receipt_id':receipt_id,'round':round_no,'started_utc':started,'ended_utc':utc(),'action_sha256':digest(original),'action_sha256_scope':'complete_original' if len(original)<=MAX_ACTION_BYTES else 'captured_prefix_only','captured_action_bytes':len(original),'raw_capture':'complete' if len(original)<=MAX_ACTION_BYTES else 'prefix_only_original_retained_by_runner','parsed_action':action,'status':status,'reason':reason,'configured_candidates':configured,'evaluated_candidates':len(records),'censored_candidates':max(0,configured-len(records)) if status=='COMPLETE' else configured,'invalid_candidates':sum(not r['assessment']['valid'] for r in records),'raw_duplicate_candidates':sum(r['raw_duplicate'] for r in records),'canonical_duplicate_candidates':sum(r['canonical_schedule_duplicate'] for r in records),'wall_seconds':time.perf_counter()-wall,'process_cpu_seconds':time.process_time()-cpu,'harness_sha256':self.state['harness_sha256']}
        put(self.folder/(stem+'.event.json'),event)
        self.state['rounds_used']=round_no
        prior=self.folder/('STATE-'+str(round_no-1).zfill(3)+'.json');self.state['previous_state_sha256']=digest(prior.read_bytes())
        put(self.folder/('STATE-'+str(round_no).zfill(3)+'.json'),self.state)
        if self.state['feedback_enabled']:
            best=self.state['best'];feedback={'status':status,'reason':reason,'receipt_id':receipt_id,'round':round_no,'rounds_remaining':self.state['max_rounds']-round_no,'evaluations':visible,'censored_candidates':event['censored_candidates'],'best_so_far':None if best is None else {'candidate_id':best['candidate_id'],'candidate':best['candidate'],'charged':best['assessment']['charged'],'live':best['assessment']['live'],'dead':best['assessment']['dead']}}
        else:feedback={'status':'ACK','receipt_id':receipt_id,'round':round_no,'rounds_remaining':self.state['max_rounds']-round_no}
        put(self.folder/(stem+'.feedback.json'),feedback)
        return feedback
    def trusted_export(self):
        events=[json.loads(p.read_text()) for p in sorted(self.folder.glob('round-*.event.json'))]
        return {'schema':'bounded-addition-chain-trusted-export.v1','environment_id':self.state['environment_id'],'task_id':self.state['task_id'],'target_decimal':str(self.state['target']),'rounds_used':self.state['rounds_used'],'max_rounds':self.state['max_rounds'],'complete':self.state['rounds_used']==self.state['max_rounds'],'tools_enabled':self.state['tools_enabled'],'feedback_enabled':self.state['feedback_enabled'],'candidate_evaluations':self.state['candidate_evaluations'],'best_candidate':None if self.state['best'] is None else self.state['best']['candidate'],'best_local_assessment':None if self.state['best'] is None else self.state['best']['assessment'],'unique_raw_candidate_hashes':len(set(self.state['seen_raw'])),'unique_canonical_schedules':len(set(self.state['seen_canonical'])),'events':events,'final_aggregation':'lowest charged total, then M, then canonical index-schedule hash; identical across treatments','evidence_ceiling':'local harness assessment; independent oracle separately evaluates final explicit candidate'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='operation',required=True)
    create=sub.add_parser('init');create.add_argument('--output',required=True);create.add_argument('--task-id',required=True);create.add_argument('--tools',choices=['on','off'],required=True);create.add_argument('--feedback',choices=['on','off'],required=True);create.add_argument('--max-rounds',type=int,default=3)
    act=sub.add_parser('act');act.add_argument('--output',required=True);act.add_argument('--action-file',required=True)
    export=sub.add_parser('export');export.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        if args.operation=='init':result=Environment.create(args.output,args.task_id,args.tools=='on',args.feedback=='on',args.max_rounds).public_init()
        elif args.operation=='act':
            with Path(args.action_file).open('rb') as f:raw=f.read(MAX_ACTION_BYTES+1)
            result=Environment.load(args.output).act(raw)
        else:result=Environment.load(args.output).trusted_export()
        print(json.dumps(result,separators=(',',':')))
    except (Refusal,ValueError,OSError,KeyError,TypeError) as error:
        print(json.dumps({'status':'INTERFACE_REFUSED','reason':type(error).__name__+':'+str(error)}));return 2
    return 0


if __name__=='__main__':sys.exit(main())
