"""Finalize only an inspected supplement; never rewrite primary receipt/figures."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,xml.etree.ElementTree as ET
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('name',choices=['COHORT','MEMORY']);a=p.parse_args()
path=H/('SUPPLEMENT_'+a.name+'_RECEIPT.json');d=json.loads(path.read_text())
assert all(sha(R/p)==h for p,h in d['source_pins'].items())
assert all(sha(H/p)==h for p,h in d['preserved_primary_pins'].items())
png=next(H/f['path'] for f in d['files'] if f['path'].endswith('.png'));svg=png.with_suffix('.svg')
with Image.open(png) as im:im.verify()
text_nodes=sum(1 for e in ET.parse(svg).iter() if e.tag.endswith('}text'));assert text_nodes>20
qa={'observed_utc':datetime.now(timezone.utc).isoformat(),'state':'PASS_SCOPED_PNG_VISUAL_QA_AND_SVG_STRUCTURE',
 'checks':['Opened final PNG with view_image; checked readable paired labels, exact values, legends and source-scope caveats without visible clipping or overlap.','All source pins and accepted primary pins unchanged. SVG XML parses and retains editable text.','Actual execution, copied state accounting and mathematical outcomes are explicitly distinct.'],
 'limits':['SVG not browser-rasterized; no formal color-vision simulation.','Descriptive small exposed-task study; no inferential confidence intervals or autonomous-learning claim.'],
 'svg_editable_text_nodes':text_nodes,'png_sha256':sha(png),'svg_sha256':sha(svg)}
qa_name='SUPPLEMENT_'+a.name+'_QA.json';(H/qa_name).write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
d['state']='PASS_SCOPED_SUPPLEMENT_READY_FOR_INDEPENDENT_REVIEW';d['qa']={'path':qa_name,'sha256':sha(H/qa_name)}
caption=H/('COHORT_CAPTION.md' if a.name=='COHORT' else 'MEMORY_CAPTION.md')
d['caption']={'path':caption.name,'sha256':sha(caption)};d['finalizer_sha256']=sha(Path(__file__))
d['plots_total_bytes']=sum(f.stat().st_size for f in H.iterdir() if f.is_file());assert d['plots_total_bytes']<4000000
path.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'state':d['state'],'receipt':path.name,'sha256':sha(path),'plots_total_bytes':d['plots_total_bytes']}))
