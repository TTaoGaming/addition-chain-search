"""Recheck saved inputs, all score assessments and final certificates without search."""
import gzip,hashlib,importlib.util,json,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def require(ok,why):
    if not ok:raise ValueError(why)


def independent_forward_score(values,parents,target,width=8):
    bits=bin(target)[2:];n=len(bits);allowed=set(values);dp=[None]*(n+1)
    def rank(t):return (t[0]+t[1],t[1],t[0])
    def put(i,v):
        if dp[i] is None or rank(v)<rank(dp[i]):dp[i]=v
    for w in range(1,min(width,n)+1):
        if int(bits[:w],2) in allowed:put(w,(0,0))
    for i in range(1,n):
        if dp[i] is None:continue
        for w in range(1,min(width,n-i)+1):
            d=int(bits[i:i+w],2)
            if not d or d in allowed:put(i+w,(dp[i][0]+w,dp[i][1]+bool(d)))
    require(dp[n] is not None,'target unreachable in window grammar')
    ps=sum(a==b for a,b in parents);pm=len(parents)-ps
    s,m=dp[n][0]+ps,dp[n][1]+pm
    return [s+m,s,m]


def main():
    before=time.process_time();result=json.loads((RUN/'RESULT.json').read_text());pin=json.loads((RUN/'PRE_RUN_PIN.json').read_text());plan=json.loads((RUN/'PREREGISTRATION.json').read_text())
    require(sha(RUN/'PREREGISTRATION.json')==pin['preregistration_sha256']==result['preregistration_sha256'],'preregistration drift')
    require(sha(RUN/'run_replication.py')==pin['runner_sha256'],'original runner drift')
    require(sha(ROOT/'inputs/engine/search.py')==pin['engine_sha256']==result['engine_sha256'],'engine drift')
    frozen_verifier=RUN/('seed-'+str(plan['seeds'][0]))/'verify.py'
    require(sha(frozen_verifier)==pin['verifier_sha256']==result['verifier_sha256'],'frozen verifier drift')
    spec=importlib.util.spec_from_file_location('replication_frozen_verifier',frozen_verifier);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    target=int(plan['target_hex'],16);modulus=int(plan['modulus_decimal']);count=0;certs=0
    for rec in result['records']:
        folder=ROOT/rec['artifact_directory'];policy=rec['policy']
        require(sha(folder/(policy+'.result.json'))==rec['result_sha256'],'result drift')
        require(sha(folder/(policy+'.certificate.json'))==rec['certificate_sha256'],'certificate drift')
        require(sha(folder/(policy+'.assessments.jsonl.gz'))==rec['trace_sha256'],'trace drift')
        check=v.verify((folder/(policy+'.certificate.json')).read_bytes(),'json',target,modulus)
        require(check['charged']==rec['best'] and check['dead']['operations']==0,'final certificate replay disagreement');certs+=1
        with gzip.open(folder/(policy+'.assessments.jsonl.gz'),'rt') as f:rows=[json.loads(line) for line in f]
        require(len(rows)==256,'assessment cap mismatch')
        for ordinal,row in enumerate(rows,1):
            require(row['ordinal']==ordinal,'ordinal gap');vals=row['values'];parents=row['parents']
            require(vals[0]==1 and len(vals)==len(parents)+1,'precompute shape')
            for j,(a,b) in enumerate(parents,1):
                require(type(a) is int and type(b) is int and 0<=a<j and 0<=b<j,'precompute reference')
                require(type(vals[j]) is int and vals[j]==vals[a]+vals[b] and vals[j]>vals[j-1] and vals[j]<=127,'precompute identity/grammar')
            require(row['score']==independent_forward_score(vals,parents,target),'independent forward score disagreement')
            count+=1
    out={'schema':'replicated-selection-saved-run-validation.v1','state':'PASS_SAVED_RUN','exact_forward_DP_scores_checked':count,'final_certificates_replayed':certs,'source_pin_checks':'PASS','current_process_cpu_seconds_for_this_audit':time.process_time()-before,
        'measurement_boundary':'This audit only; excludes original run and report preparation','independence':'Forward DP is separate from producer backward DP; final exact-integer replay uses frozen separate verifier implementation. Same configured model family, no distinct serving-family claim.'}
    dest=RUN/('SAVED_RUN_VALIDATION-'+str(time.time_ns())+'.json')
    with dest.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    size=sum(p.stat().st_size for p in RUN.rglob('*') if p.is_file());require(size<=1000000,'run output cap')
    print(json.dumps({'receipt':str(dest),'state':out['state'],'scores_checked':count,'certificates':certs,'audit_CPU_seconds':out['current_process_cpu_seconds_for_this_audit'],'artifact_bytes':size}))


if __name__=='__main__':main()
