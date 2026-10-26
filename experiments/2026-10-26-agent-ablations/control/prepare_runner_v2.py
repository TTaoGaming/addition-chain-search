import hashlib,json,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
schema=json.loads((R/'stimuli/action.schema.json').read_text())
schema['properties']['max_added_digits']['maximum']=2
template=(R/'stimuli/PROMPT_TEMPLATE.txt').read_text().replace('positive odd digits','unique positive integer digits including1').replace('max_added_digits0..3','max_added_digits0..2').replace('widths list, variants','nonempty unique widths list, variants')
runner=(R/'control/run_codex.py').read_text().replace('stimuli/PROMPT_TEMPLATE.txt','stimuli/PROMPT_TEMPLATE.v2.txt').replace('stimuli/action.schema.json','stimuli/action.v2.schema.json').replace('ROOT/"runs"','ROOT/"runs-v2"')
files={'stimuli/action.v2.schema.json':json.dumps(schema,indent=2)+'\n','stimuli/PROMPT_TEMPLATE.v2.txt':template,'control/run_codex_v2.py':runner}
pins=[]
for rel,text in files.items():
 p=R/rel
 if p.exists():raise SystemExit('refuse overwrite '+rel)
 p.write_text(text,encoding='utf-8')
 b=p.read_bytes();pins.append({'path':rel,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
amend={'schema':'prebatch-interface-amendment.v2','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_first_v2_trajectory':not (R/'runs-v2').exists(),'prior_experimental_run':'runs/synthetic-20-v1__r2__B__luna','prior_result_retained':'25-operation valid witness,11 evaluated candidates, dictionary request max_added3 refused by unchanged harness','first_failure':'Root prompt/schema advertised max_added_digits0..3 while frozen harness accepts0..2. Independent reviewer and root detected before remaining39 jobs. Root also clarifies unique positive integer dictionary digits rather than odd-only.','change':'Versioned runner/schema/template advertise the implemented grammar. Harness and oracle unchanged. Original code,prompt,schema,logs and failed action retained.','analysis_set':'All40 primary v2 assignments use one consistent v2 interface and original frozen randomized order. First v1 trajectory reported separately; no pooling or silent deletion. Same hypotheses/cells/targets/limits; no outcome-driven tool tuning.','selected_irrelevant_control':'stimuli/irrelevant.v2.txt','pins':pins}
p=R/'control/INTERFACE_AMENDMENT.v2.json';p.write_text(json.dumps(amend,indent=2)+'\n',encoding='utf-8')
print(json.dumps(amend))
