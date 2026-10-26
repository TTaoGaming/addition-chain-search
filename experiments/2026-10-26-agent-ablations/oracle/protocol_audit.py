"""Pre-outcome protocol/stimulus audit; no harness source or outcome access."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROTOCOL_SHA = '3912d9a4b3c9eab980731a57cab30683a2e9f7ee567d4959121f6b10d9493498'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    protocol_path = ROOT / 'PROTOCOL.v1.json'
    assert sha(protocol_path) == PROTOCOL_SHA
    protocol = json.loads(protocol_path.read_text())
    manifest = json.loads((ROOT / 'stimuli/MANIFEST.json').read_text())
    pins = []
    for pin in manifest['pins']:
        path = ROOT / pin['path']
        assert sha(path) == pin['sha256'] and path.stat().st_size == pin['bytes']
        pins.append({'path': pin['path'], 'sha256': sha(path), 'bytes': path.stat().st_size})
    texts = {name: (ROOT / 'stimuli' / (name + '.txt')).read_text()
             for name in ('relevant', 'reordered', 'irrelevant', 'skill')}
    counts = {name: len(texts[name].split()) for name in ('relevant', 'reordered', 'irrelevant')}
    assert counts == {'relevant': 96, 'reordered': 96, 'irrelevant': 96}
    paragraphs = texts['relevant'].strip().split('\n\n')
    assert len(paragraphs) == 3
    assert '\n\n'.join(reversed(paragraphs)) == texts['reordered'].strip()
    run_order = json.loads((ROOT / 'stimuli/RUN_ORDER.json').read_text())
    tasks = {t['id']: t for t in protocol['tasks']}
    cells = {c['id']: c for c in protocol['cells']}
    expected = {(t, r, c, protocol['models']['primary'])
                for t in tasks for r in protocol['replicate_ids'] for c in cells}
    expected |= {(t, r, 'B', protocol['models']['backend_contrast'])
                 for t in tasks for r in protocol['replicate_ids']}
    actual = []
    for entry in run_order:
        assert entry['task'] == tasks[entry['task']['id']]
        assert entry['cell'] == cells[entry['cell']['id']]
        actual.append((entry['task']['id'], entry['replicate'], entry['cell']['id'], entry['model']))
    assert len(actual) == len(set(actual)) == 40 and set(actual) == expected
    assert len({entry['id'] for entry in run_order}) == 40
    assert len(actual) * protocol['rounds'] == 120
    assert protocol['task_public_manifest_sha256'] == sha(HERE / 'PUBLIC_TASKS.json')
    freeze = json.loads((HERE / 'CORE_FREEZE.json').read_text(encoding='utf-8-sig'))
    assert sha(HERE / 'evaluate.py') == next(p['sha256'] for p in freeze['code'] if p['name'] == 'evaluate.py')
    findings = [
        {'id': 'STIMULUS-1', 'severity': 'LIMITATION',
         'finding': 'M-I is word-count matched, not byte/token matched; relevant packet has three paragraphs while irrelevant packet is a single paragraph ending mid-clause.',
         'recommendation': 'If retaining frozen stimuli, describe the content-packet contrast and disclose prose completeness/format as possible confounds; do not claim pure semantic relevance isolation.'},
        {'id': 'BLINDING-1', 'severity': 'IMPLEMENTATION_GUARD_TO_VERIFY',
         'finding': 'Run IDs contain treatment labels. memory_kind must be provided for all nonempty packets, and assignment IDs must not leak through visible feedback/history/receipt identifiers.',
         'recommendation': 'Inspect actual rendered prompts and visible results once runner/harness are frozen.'},
        {'id': 'FEEDBACK-1', 'severity': 'IMPLEMENTATION_GUARD_TO_VERIFY',
         'finding': 'Verifier-withheld cell requires all visible result paths to respect the frozen feedback mask.',
         'recommendation': 'Check costs, validity, incumbents, candidate schedules and receipt metadata for unintended feedback before interpreting V-B.'},
    ]
    output = {'schema': 'pre-outcome-independent-protocol-audit.v1',
              'observed_utc': datetime.now(timezone.utc).isoformat(),
              'protocol_sha256': PROTOCOL_SHA,
              'stimuli_manifest_sha256': sha(ROOT / 'stimuli/MANIFEST.json'),
              'source_sha256': sha(Path(__file__)), 'pins': pins,
              'memory_word_counts': counts,
              'memory_bytes': {name: len(texts[name].encode()) for name in counts},
              'reordered_is_exact_paragraph_reversal': True,
              'trajectory_count': len(actual), 'decision_count': len(actual) * protocol['rounds'],
              'cell_model_counts': {str(k): v for k, v in Counter((e[2], e[3]) for e in actual).items()},
              'frozen_arithmetic_core_unchanged': True,
              'harness_or_runner_implementation_read': False, 'experimental_outcomes_read': False,
              'findings': findings,
              'verdict': 'PASS_SCOPED_PREREGISTRATION_WITH_STIMULUS_LIMITATION_AND_PENDING_IMPLEMENTATION_GUARDS',
              'ceiling': 'protocol/stimulus consistency; no inference outcome, implementation, OS isolation, family independence or Apex admission claim'}
    destination = HERE / 'PROTOCOL_AUDIT.v1.json'
    destination.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'verdict': output['verdict'], 'trajectories': len(actual),
                      'decisions': len(actual) * protocol['rounds'], 'memory_word_counts': counts,
                      'receipt_sha256': sha(destination)}))


if __name__ == '__main__':
    main()
