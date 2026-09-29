import json,copy
from pathlib import Path
from .checker import check,P,TARGET,Q
ROOT=Path(__file__).resolve().parent

def s(rows,name,ref,k=1): rows.append({'name':name,'op':'S','args':[ref,k]})
def m(rows,name,a,b): rows.append({'name':name,'op':'M','args':[a,b]})
def prefix():
    r=[]
    s(r,'a2','x'); m(r,'a3','x','a2'); s(r,'a6','a3'); m(r,'a7','x','a6')
    s(r,'a7s3','a7',3); m(r,'a63','a7s3','a7')
    s(r,'a63s3','a63',3); m(r,'a511','a63s3','a7')
    s(r,'a511s9','a511',9); m(r,'t18','a511s9','a511')
    s(r,'t19s','t18'); m(r,'t19','t19s','x')
    s(r,'t19s18','t19',18); m(r,'t37','t19s18','t18')
    s(r,'t37s37','t37',37); m(r,'t74','t37s37','t37')
    s(r,'t74s37','t74',37); m(r,'t111','t74s37','t37')
    s(r,'t111s111','t111',111); m(r,'u222','t111s111','t111')
    return r

def candidate(k):
    rows=prefix()
    if k==223:
        s(rows,'v223s','u222'); m(rows,'v223','v223s','x')
        s(rows,'hi','v223',223); m(rows,'q','hi','u222')
    elif k==224:
        m(rows,'v222','u222','x'); s(rows,'v223','v222')
        m(rows,'b224','v223','u222'); s(rows,'hi','u222',224)
        m(rows,'q','hi','b224')
    else: raise ValueError('split outside preregistered set')
    s(rows,'inv1','q'); s(rows,'inv2','inv1'); m(rows,'terminal','inv2','x')
    return {'schema':'curve448.exponent_dag.v1','rows':rows,'terminal':'terminal'}

def replay_all():
    out=[]
    for k in (223,224):
        c=candidate(k); e,sq,mul,vals=check(c)
        if vals['u222']!=(1<<222)-1 or vals['q']!=Q or e!=TARGET: raise AssertionError(f'k={k} exponent mismatch')
        out.append({'k':k,'q_exponent':str(vals['q']),'terminal_exponent':str(e),'S':sq,'M':mul,'total':sq+mul,'accepted_under_460':sq+mul<460})
    return out

if __name__=='__main__': print(json.dumps(replay_all(),sort_keys=True))
