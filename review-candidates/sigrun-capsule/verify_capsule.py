"""Offline integrity and explicit local serialization checks. No network or effects."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
manifest=json.loads((P/'SHA256SUMS.json').read_text())
for name,digest in manifest.items():
 p=(P/name).resolve()
 assert p.parent==P, 'unexpected path'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
c=json.loads((P/'capsule.json').read_text());old=json.loads((P/'source-chain.json').read_text())
assert len(old['s_chain'])==19 and old['s_chain'][0]=='SIGRUN'
assert c['s_chain']==old['s_chain']+['SLIVER'] and len(set(c['s_chain']))==20
canon=lambda o:json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
assert canon(json.loads(canon(c)))==canon(c)
assert c['status']=='REVIEW_CANDIDATE'
seed=(P/'SEED.txt').read_text()
assert c['version_utc'] in seed
assert ' '.join(c['s_chain']) in seed
assert all(f['expression'] in seed for f in c['formulas'])
print(json.dumps({'files_checked':len(manifest),'original_terms':19,'current_terms':20,'serialization_roundtrip':'PASS','capsule_canonical_sha256':hashlib.sha256(canon(c)).hexdigest(),'literal_quine':'NOT_TESTED','behavioral_regeneration':'NOT_ESTABLISHED','authority_granted':False},indent=2))
