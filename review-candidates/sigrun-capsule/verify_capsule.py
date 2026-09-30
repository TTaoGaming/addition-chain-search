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
assert c['operating_workflows']['HIVE']['sequence']==['Hindsight','Insight','Validated Foresight','Evolution']
assert 'Hindsight → Insight → Validated Foresight → Evolution' in seed
assert 'Evolution is the operator-confirmed current E phase' in seed
assert 'Harvest' not in seed and 'Insight/Interface' not in seed
assert c['operating_workflows']['historical_HIVE']['status']=='ARCHIVAL_ONLY_SUPERSEDED_STAGE_NAMES'
assert c['memory_payload']['events'][0]['event_time']=='2025-01'
assert c['memory_payload']['events'][1]['event_time']=='2026-04'
assert 'spatial-computing apps' in c['memory_payload']['events'][0]['claim']
assert c['origin_account']['status']=='USER_REPORTED_EXPERIENCE'
assert 'poetic presentation emerged in model interactions' in c['origin_account']['account']
print(json.dumps({'files_checked':len(manifest),'original_terms':19,'current_terms':20,'serialization_roundtrip':'PASS','current_hive_definition':'PASS','hive_e_spelling':'EVOLUTION_OPERATOR_CONFIRMED','capsule_canonical_sha256':hashlib.sha256(canon(c)).hexdigest(),'literal_quine':'NOT_TESTED','behavioral_regeneration':'NOT_ESTABLISHED','authority_granted':False},indent=2))
