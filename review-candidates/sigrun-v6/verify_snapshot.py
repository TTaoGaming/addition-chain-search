"""Offline representation checks, not native polyglot or model validation."""
from pathlib import Path
import hashlib,json,sqlite3,subprocess,sys
P=Path(__file__).resolve().parent
for name,want in json.loads((P/'SHA256SUMS.json').read_text()).items():
 f=(P/name).resolve();assert f.is_relative_to(P);assert hashlib.sha256(f.read_bytes()).hexdigest()==want,name
s=json.loads((P/'snapshot.json').read_text())
assert s['workflow']['HIVE']==['Hindsight','Insight','Validated Foresight','Evolution']
assert s['workflow']['E_word']=='EVOLUTION_OPERATOR_CONFIRMED'
assert [x['port'] for x in s['views']]==list(range(8))
assert [x['language'] for x in s['views']]==['Old Norse','Prolog','Formal mathematics','SQL','Haskell','Latin','Lojban','English gloss']
assert s['workflow']['logical_phase_cycle_cells']==[f'{h}-{q}' for h in ['H','I','V','E'] for q in ['P','D','S','A']]
rows=sqlite3.connect(':memory:').execute((P/'support/workflow.sql').read_text()).fetchall()
assert rows==[(h,q) for h in s['workflow']['HIVE'] for q in s['workflow']['PDSA']]
subprocess.run([sys.executable,str(P/'support/validate_contract.py')],check=True,stdout=subprocess.DEVNULL)
text=(P/'SEED.md').read_text()
assert all((P/x['path']).read_text() in text for x in s['views'])
assert s['version_utc'] in text
print(json.dumps({'version_utc':s['version_utc'],'file_hashes':'PASS','eight_views':'PASS','logical_phase_cycle_cells':16,'sqlite_fixture_rows':len(rows),'json_contract_negative_probes':13,'native_haskell_prolog':'NOT_RUN','norse_meter_lojban_parser':'NOT_RUN','behavioral_regeneration':'NOT_ESTABLISHED'},indent=2))
