import json
P=(1<<448)-(1<<224)-1
TARGET=P-2
Q=(1<<446)-(1<<222)-1

def check(obj):
    if obj.get('schema')!='curve448.exponent_dag.v1' or not isinstance(obj.get('rows'),list): raise ValueError('schema/rows')
    values={'x':1}; s=m=0
    for i,r in enumerate(obj['rows']):
        name=r.get('name'); op=r.get('op'); a=r.get('args')
        if not isinstance(name,str) or not name or name in values or not isinstance(a,list): raise ValueError(f'row {i}: invalid name/args')
        if op=='S':
            if len(a)!=2 or a[0] not in values or type(a[1]) is not int or a[1]<1: raise ValueError(f'row {i}: bad square')
            values[name]=values[a[0]]<<a[1]; s+=a[1]
        elif op=='M':
            if len(a)!=2 or any(x not in values for x in a): raise ValueError(f'row {i}: bad multiply')
            values[name]=values[a[0]]+values[a[1]]; m+=1
        else: raise ValueError(f'row {i}: op')
    t=obj.get('terminal')
    if t not in values: raise ValueError('terminal ref')
    return values[t],s,m,values
