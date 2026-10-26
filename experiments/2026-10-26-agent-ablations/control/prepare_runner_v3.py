from pathlib import Path
import json,hashlib,datetime
r=Path(__file__).resolve().parents[1]
p=r/'control/run_codex_v3.py'
assert not p.exists()
text=(r/'control/run_codex_v2.py').read_text().replace('ROOT/"runs-v2"','ROOT/"runs"/"v2"')
p.write_text(text,encoding='utf-8')
b=p.read_bytes()
amendment={
 'schema':'prelaunch-runner-scope-amendment.v3',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'prior_runner_v2_inference_calls':0,
 'first_failure':'Independent prelaunch review caught runner output path runs-v2 outside frozen harness allowlist; no v2 model call was executed.',
 'selected_runner':'control/run_codex_v3.py',
 'runner_sha256':hashlib.sha256(b).hexdigest(),
 'selected_analysis_partition':'runs/v2',
 'change':'Move versioned analysis partition inside admitted runs subtree. Preserve v1 data and unlaunched v2 runner. Prompt/schema interfacev2 unchanged. Harness/oracle unchanged.',
 'shell_first_failure':'An earlier python -c preparation command failed syntax due to PowerShell quoting and wrote no runner; preserved in root tool receipt. Replaced with this saved source file.',
 'integration_smoke':'runs/v2/integration-smoke environment init passed without model calls; excluded from experimental assignments.'
}
(r/'control/RUNNER_SCOPE_AMENDMENT.v3.json').write_text(json.dumps(amendment,indent=2)+'\n',encoding='utf-8')
print(json.dumps(amendment))

