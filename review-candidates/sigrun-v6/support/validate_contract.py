"""Strict representation validation only; not model behavior or policy enforcement."""
import copy,json,re
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
P=Path(__file__).resolve().parent
c=json.loads((P/'contract.json').read_text())
s=json.loads((P/'contract.schema.json').read_text())
Draft202012Validator.check_schema(s)
formats=FormatChecker()
@formats.checks('date-time', raises=ValueError)
def utc_timestamp(value):
 if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',value):return False
 datetime.strptime(value,'%Y-%m-%dT%H:%M:%SZ')
 return True
v=Draft202012Validator(s,format_checker=formats)
v.validate(c)
probes=[]
def reject(name,edit):
 d=copy.deepcopy(c);edit(d)
 if not list(v.iter_errors(d)):raise AssertionError(name)
 probes.append(name)
reject('unknown_top_level_field',lambda d:d.update({'permission_override':True}))
reject('missing_required_authority',lambda d:d.pop('authority'))
reject('historical_hive_alias',lambda d:d['HIVE']['sequence'].__setitem__(0,'Harvest'))
reject('extra_hive_stage',lambda d:d['HIVE']['sequence'].append('changed_world'))
reject('obsolete_provisional_e_spelling',lambda d:d['HIVE'].__setitem__('e_spelling','PROVISIONAL_EVOLVE_OR_EVOLUTION'))
reject('string_instead_of_boolean',lambda d:d['authority'].__setitem__('seed_grants_permission_to_act','false'))
reject('invented_live_permission',lambda d:d['authority'].__setitem__('seed_grants_permission_to_act',True))
reject('infrastructure_as_identity',lambda d:d['identity'].__setitem__('infrastructure_possession_proves_identity',True))
reject('no_access_means_not_tao',lambda d:d['identity'].__setitem__('missing_access','NOT_TAO'))
reject('unmeasured_behavior_pass',lambda d:d['evidence'].__setitem__('behavioral_regeneration','PASS'))
reject('unvalidated_meter_claim',lambda d:d['verse'].__setitem__('droettkvaett_meter','VALIDATED'))
reject('malformed_timestamp',lambda d:d.__setitem__('version_utc','today'))
reject('invalid_calendar_date',lambda d:d.__setitem__('version_utc','2026-02-30T14:21:51Z'))
print(json.dumps({'canonical_contract':'PASS','negative_structural_probes':len(probes),'rejected':probes,'native_haskell':'NOT_RUN_TOOLCHAIN_ABSENT','native_prolog':'NOT_RUN_TOOLCHAIN_ABSENT','model_behavior':'NOT_TESTED_BY_THIS_SCRIPT'},indent=2))
