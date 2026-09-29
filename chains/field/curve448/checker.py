import json, hashlib, sys
from pathlib import Path

P=(1<<448)-(1<<224)-1
TARGET=P-2

def parse(obj):
    if not isinstance(obj,dict) or obj.get('schema')!='curve448.exponent_dag.v1': raise ValueError('schema')
    vals={'x':1}; rows=obj.get('rows')
    if not isinstance(rows,list): raise ValueError('rows')
    s=m=0
    for i,row in enumerate(rows):
        if not isinstance(row,dict): raise ValueError(f'row {i}: not object')
        name=row.get('name'); op=row.get('op'); args=row.get('args')
        if not isinstance(name,str) or not name or name in vals: raise ValueError(f'row {i}: bad/duplicate name')
        if not isinstance(args,list): raise ValueError(f'row {i}: args')
        if op=='S':
            if len(args)!=2 or args[0] not in vals or type(args[1]) is not int or args[1]<1: raise ValueError(f'row {i}: bad square')
            vals[name]=vals[args[0]] << args[1]; s+=args[1]
        elif op=='M':
            if len(args)!=2 or any(x not in vals for x in args): raise ValueError(f'row {i}: bad multiply reference')
            vals[name]=vals[args[0]]+vals[args[1]]; m+=1
        else: raise ValueError(f'row {i}: unsupported op')
    term=obj.get('terminal')
    if term not in vals: raise ValueError('terminal reference')
    return vals[term],s,m,vals

def pruned(obj):
    rows=obj['rows']; needed={obj['terminal']}; by={r['name']:r for r in rows}
    pending=[obj['terminal']]
    while pending:
        n=pending.pop()
        if n=='x': continue
        if n not in by: raise ValueError('dead-code reference')
        r=by[n]
        deps=r['args'][:1] if r['op']=='S' else r['args']
        for dep in deps:
            if dep not in needed: needed.add(dep); pending.append(dep)
    return {'schema':obj['schema'],'rows':[r for r in rows if r['name'] in needed],'terminal':obj['terminal']}

def main(path):
    obj=json.loads(Path(path).read_text(encoding='utf-8'))
    e,s,m,_=parse(obj)
    if e!=TARGET: raise ValueError('terminal exponent mismatch')
    return {'terminal_exponent':str(e),'target_exponent':str(TARGET),'S':s,'M':m,'total':s+m}
if __name__=='__main__':
    try: print(json.dumps(main(sys.argv[1]),sort_keys=True))
    except Exception as e: print(json.dumps({'accepted':False,'error':str(e)},sort_keys=True)); sys.exit(1)
