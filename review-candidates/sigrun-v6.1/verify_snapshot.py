"""Offline file/source-coverage checks, not whole-system recovery validation."""
from pathlib import Path
import json,hashlib
from embedded_seed import validate_embedded
P=Path(__file__).resolve().parent
for name,want in json.loads((P/'SHA256SUMS.json').read_text()).items():
 f=(P/name).resolve();assert f.is_relative_to(P);assert hashlib.sha256(f.read_bytes()).hexdigest()==want,name
a=json.loads((P/'ASSESSMENT.json').read_text());text=(P/'SEED.md').read_text()
inline=validate_embedded(text,json.loads((P/'EMBEDDED_CONTENT.json').read_text()))
assert a['current_hive']==['Hindsight','Insight','Validated Foresight','Evolution']
assert 'not16serialglobalsteps' in a['geometry']
for name in ['Gleipnir_heritage.hs','Grimoire_heritage.hs','Sigrun_card_heritage.hs','runtime_type_fragments.py']:assert (P/'heritage'/name).read_text() in text
for x in json.loads((P/'models/formal_architecture_excerpts.json').read_text())['excerpts']:assert x['text'] in text
model=json.loads((P/'models/compound_actor_model.json').read_text());assert len(model['state_candidate']['terms'])==11 and len(model['compound_layers'])==7
assert len(model['obsidian_matrix_8x8'])==8 and all(len(x)==8 for x in model['obsidian_matrix_8x8'])
r=json.loads((P/'receipts/HERITAGE_COMPILE_RESULTS.json').read_text());assert [x['compile_exit'] for x in r]==[0,1,1]
assert 'ratchet_overflow_counterexample",True' in (P/'receipts/counterexamples-run.log').read_text()
print(json.dumps({'inline_content':inline,'file_hashes':'PASS','embedded_source_fragments':'PASS','actor_state_fields':11,'compound_layers':7,'role_matrix':'8x8','native_receipt_exits':[0,1,1],'whole_system_recovery':'NOT_ESTABLISHED'},indent=2))
