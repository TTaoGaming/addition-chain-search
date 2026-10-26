"""Reproduce target integers and public binary baselines; no search/model call."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 'brian-agent-ablation-20261026-v1'


def generate(bits):
    material = (SEED + '|bits=' + str(bits)).encode('ascii')
    digest = hashlib.sha256(material).hexdigest()
    target = (int(digest, 16) & ((1 << bits) - 1)) | (1 << (bits - 1)) | 1
    values = [1]
    steps = []
    current = 0
    for bit in bin(target)[3:]:
        steps.append([current, current])
        values.append(values[current] + values[current])
        current = len(steps)
        if bit == '1':
            steps.append([current, 0])
            values.append(values[current] + 1)
            current = len(steps)
    assert values[current] == target
    squarings = sum(a == b for a, b in steps)
    return {'task_id': f'synthetic-{bits}-v1', 'target_decimal': str(target),
            'target_hex': format(target, 'x'), 'target_bits': bits,
            'popcount': target.bit_count(), 'steps': steps, 'output_index': current,
            'operations': len(steps), 'S': squarings, 'M': len(steps) - squarings,
            'material_ascii': material.decode(), 'material_sha256': digest}


def main():
    public_path = HERE / 'PUBLIC_TASKS.json'
    public = json.loads(public_path.read_text())
    generated = [generate(20), generate(23)]
    for actual, expected in zip(public['tasks'], generated, strict=True):
        for key in ('task_id', 'target_decimal', 'target_hex', 'target_bits', 'popcount'):
            assert actual[key] == expected[key]
        for key in ('steps', 'output_index', 'operations', 'S', 'M'):
            assert actual['binary_baseline'][key] == expected[key]
        assert actual['generation']['sha256'] == expected['material_sha256']
    receipt = {'schema': 'synthetic-task-generation-receipt.v1',
               'observed_utc': datetime.now(timezone.utc).isoformat(),
               'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'public_tasks_sha256': hashlib.sha256(public_path.read_bytes()).hexdigest(),
               'seed': SEED, 'formula': 'SHA256 low bits with high and low bits forced1',
               'generated': generated,
               'determinism_scope': 'target integers and baseline schedules; wall-clock receipt metadata is not deterministic',
               'ceiling': 'new session-selected synthetic task definitions; no novelty, pretraining absence, difficulty or optimum certification'}
    out = HERE / 'GENERATION_RECEIPT.json'
    out.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'state': 'PASS_DETERMINISTIC_REGENERATION',
                      'source_sha256': receipt['source_sha256'],
                      'public_tasks_sha256': receipt['public_tasks_sha256'],
                      'receipt_sha256': hashlib.sha256(out.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
