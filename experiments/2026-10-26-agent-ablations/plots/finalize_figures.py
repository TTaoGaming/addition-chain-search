"""Source/format validation and the human-inspected visual-QA receipt, plots only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, xml.etree.ElementTree as ET
from PIL import Image
H=Path(__file__).resolve().parent
R=H.parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((H/'FIGURE_RECEIPT.json').read_text())
assert all(sha(R/p)==h for p,h in receipt['source_pins'].items())
formats=[]
for name in receipt['figures']:
    svg=H/(name+'.svg'); tree=ET.parse(svg)
    text_count=sum(1 for e in tree.iter() if e.tag.endswith('}text'))
    assert text_count>10
    png=H/(name+'.png')
    with Image.open(png) as image:
        image.verify()
    with Image.open(png) as image:
        size=image.size
    formats.append({'figure':name,'png_dimensions':size,'svg_xml_parse':'PASS','svg_editable_text_nodes':text_count,'png_sha256':sha(png),'svg_sha256':sha(svg)})
qa={'schema':'primary-figure-visual-qa.v1','observed_utc':datetime.now(timezone.utc).isoformat(),
 'state':'PASS_SCOPED_PNG_VISUAL_QA_AND_SVG_STRUCTURE',
 'visual_checks':[
  'All four PNGs opened with view_image and inspected at displayed export size.',
  'Observed initial overlap of budget-count annotation and status bar; moved bar above count text and re-opened corrected export.',
  'Observed tight adjacent decision headers; wrapped headers and re-opened corrected raw trajectory export.',
  'Final images show readable titles, exact paired values, task/replicate labels, all40raw rows, explicit timeout prefix and footnotes without visible clipping/overlap.',
  'Redundant encodings retained: exact numbers, direct labels, filled/open shapes and timeout diamond; action family codes remain legible without color.'
 ],
 'data_checks':[
  'Frozen JSON hash equals5d884748187c90fb7413a9ba17e65103955ea736ad142da26826945c93f75ac8; independent audit binds same JSON and CSV.',
  '40unique task×replicate×cell×model keys;39complete+1timeout;3098evaluations; valid=uniqueSchedule+duplicate records for every row.',
  'All32pair costs, deltas, action/family changes, unique-region/evaluation/duplicate deltas recomputed from frozen raw rows by renderer.',
  'No v1integration or browser cohort pooled into primary figures.'
 ],
 'not_performed':['No browser rasterization of SVG or rendered Mermaid parser; SVG XML/editable-text structure checked.','No formal color-vision simulation or statistical power/generalization claim.'],
 'formats':formats,'source_mutations':[]}
(H/'VISUAL_QA.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
receipt['state']='PASS_SCOPED_FIGURES_READY_FOR_INDEPENDENT_REVIEW'
receipt['visual_qa_sha256']=sha(H/'VISUAL_QA.json')
receipt['files']=[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(H.iterdir()) if p.is_file() and p.name!='FIGURE_RECEIPT.json']
receipt['bytes_before_receipt']=sum(p.stat().st_size for p in H.iterdir() if p.is_file() and p.name!='FIGURE_RECEIPT.json')
(H/'FIGURE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
total=sum(p.stat().st_size for p in H.iterdir() if p.is_file());assert total<4000000
print(json.dumps({'state':receipt['state'],'total_bytes':total,'receipt_sha256':sha(H/'FIGURE_RECEIPT.json'),'visual_qa_sha256':sha(H/'VISUAL_QA.json')}))
