"""Independent exact-integer addition-chain oracle. No candidate code execution.

Authored from the mathematical task rules before reading harness code.
The evaluator and its controls must not be included in candidate prompts.
"""
import argparse
import hashlib
import json
from pathlib import Path

MAX_ROWS = 256
MAX_CANDIDATE_BYTES = 65536
TASKS = {'synthetic-20-v1': 750339, 'synthetic-23-v1': 7162463}


class Rejected(ValueError):
    def __init__(self, code, detail):
        self.code, self.detail = code, detail
        super().__init__(detail)


def require(condition, code, detail):
    if not condition:
        raise Rejected(code, detail)


def digest_object(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def inspect_chain(steps, output_index, target):
    """Inspect explicit arithmetic; target is an exact positive integer.

    Index0 is the free exponent1. Row k creates node k+1. An S requires
    equal parent INDICES. All rows are charged, including dead/repeated work.
    """
    require(type(target) is int and target > 1, 'INVALID_TARGET', 'positive target greater than1 required')
    require(type(steps) is list and 0 < len(steps) <= MAX_ROWS,
            'INVALID_ROWS', 'one to256 parent-index rows required')
    values = [1]
    parents = []
    for row_number, pair in enumerate(steps):
        require(type(pair) is list and len(pair) == 2, 'INVALID_PAIR', f'row{row_number}: two indices required')
        a, b = pair
        require(type(a) is int and type(b) is int, 'INVALID_INDEX_TYPE', f'row{row_number}: exact integer indices required')
        require(0 <= a < len(values) and 0 <= b < len(values),
                'INVALID_INDEX', f'row{row_number}: parents must already exist')
        values.append(values[a] + values[b])
        parents.append((a, b))
    require(type(output_index) is int and 0 < output_index < len(values),
            'INVALID_OUTPUT_INDEX', 'output must name a computed non-base node')
    require(values[output_index] == target, 'WRONG_ENDPOINT', 'computed endpoint differs from the exact task integer')
    live = set()
    frontier = [output_index]
    while frontier:
        node = frontier.pop()
        if node == 0 or node in live:
            continue
        live.add(node)
        frontier.extend(parents[node - 1])
    dead = sorted(set(range(1, len(values))) - live)
    squarings = sum(a == b for a, b in parents)
    live_s = sum(node in live and a == b for node, (a, b) in enumerate(parents, 1))
    live_m = len(live) - live_s
    occurrences = {}
    for node, value in enumerate(values):
        occurrences.setdefault(value, []).append(node)
    repeated = [{'exponent_decimal': str(value), 'node_indices': nodes}
                for value, nodes in sorted(occurrences.items()) if len(nodes) > 1]
    equations = sorted((values[node], min(values[a], values[b]), max(values[a], values[b]))
                       for node, (a, b) in enumerate(parents, 1))
    literal_schedule = {'steps': steps, 'output_index': output_index, 'target_decimal': str(target)}
    commutative_schedule = {'steps': [sorted(pair) for pair in steps],
                            'output_index': output_index, 'target_decimal': str(target)}
    return {
        'state': 'VALID_EXACT' if not dead else 'VALID_EXACT_WITH_DEAD_ROWS',
        'arithmetic_valid': True,
        'target_decimal': str(target), 'computed_output_decimal': str(values[output_index]),
        'output_index': output_index,
        'charged': {'operations': len(steps), 'S': squarings, 'M': len(steps) - squarings},
        'live': {'operations': len(live), 'S': live_s, 'M': live_m},
        'dead': {'operations': len(dead), 'node_indices': dead},
        'repeated_exponent_values': repeated,
        'all_node_exponents_decimal': [str(value) for value in values],
        'index_schedule_sha256': digest_object(literal_schedule),
        'commutative_index_schedule_sha256': digest_object(commutative_schedule),
        'index_identity_scope': 'topological index schedule plus output and target; commutative variant sorts each parent pair; neither canonicalizes graph isomorphism',
        'exponent_equation_signature_sha256': digest_object(equations),
        'equation_signature_scope': 'exponent-equation multiset only; loses repeated-node reference identity',
        'ceiling': 'exact integer construction/counts/ancestry; no global optimum, timing or learning claim',
    }


def evaluate_payload(payload, task_id):
    """Public integration API; receives JSON data, never executable code."""
    try:
        require(task_id in TASKS, 'UNKNOWN_TASK', 'task identifier is not admitted')
        require(type(payload) is dict, 'INVALID_CANDIDATE', 'candidate JSON object required')
        if 'task_id' in payload:
            require(payload['task_id'] == task_id, 'TASK_MISMATCH', 'candidate task binding disagrees')
        if 'type' in payload:
            require(payload['type'] == 'submit_chain', 'INVALID_ACTION', 'oracle accepts explicit submit_chain data only')
        steps = payload.get('steps')
        output_index = payload.get('output_index', len(steps) if type(steps) is list else None)
        result = inspect_chain(steps, output_index, TASKS[task_id])
        claims = payload.get('claims')
        if claims is not None:
            require(type(claims) is dict, 'INVALID_CLAIMS', 'claims must be an object')
            for field in ('operations', 'S', 'M'):
                if field in claims:
                    require(type(claims[field]) is int and claims[field] == result['charged'][field],
                            'FALSE_COUNT_CLAIM', field + ' disagrees with all serialized rows')
            if 'values' in claims:
                require(type(claims['values']) is list and all(type(v) is int for v in claims['values']) and
                        [str(v) for v in claims['values']] == result['all_node_exponents_decimal'],
                        'FALSE_VALUE_CLAIM', 'declared exponents disagree with exact parent sums')
        result['task_id'] = task_id
        return result
    except Rejected as exc:
        return {'state': exc.code, 'arithmetic_valid': False, 'reason': exc.detail, 'task_id': task_id}


def evaluate_bytes(raw, task_id):
    if type(raw) is not bytes or len(raw) > MAX_CANDIDATE_BYTES:
        return {'state': 'CANDIDATE_BYTE_CAP', 'arithmetic_valid': False, 'task_id': task_id}
    raw_sha = hashlib.sha256(raw).hexdigest()
    def unique_object(pairs):
        obj = {}
        for key, value in pairs:
            require(key not in obj, 'DUPLICATE_JSON_KEY', 'duplicate object field')
            obj[key] = value
        return obj
    try:
        payload = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique_object)
    except (ValueError, UnicodeError):
        return {'state': 'INVALID_JSON', 'arithmetic_valid': False,
                'task_id': task_id, 'candidate_raw_sha256': raw_sha}
    result = evaluate_payload(payload, task_id)
    result['candidate_raw_sha256'] = raw_sha
    result['evaluator_source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


def audit_budget_counts(actual_events, limits):
    """Audit normalized counters. Raw-log normalization must be separately reviewed.

    Caller supplies one event per ACTUAL occurrence. It must not feed planned
    counts or cached summary counters. This function never proves model behavior.
    """
    counters = {'model_rounds': 0, 'construct_actions': 0, 'submit_actions': 0,
                'candidate_evaluations': 0, 'provider_calls': 0, 'usd': 0}
    evaluations_by_action = {}
    seen_ids = set()
    earlier_actions = set()
    errors = []
    if type(actual_events) is not list or len(actual_events) > 10000 or type(limits) is not dict:
        return {'state': 'HOLD_INVALID_BUDGET_INPUT', 'errors': ['bounded events and limits required']}
    required_limits = ('model_rounds', 'construct_actions', 'submit_actions',
                       'candidate_evaluations', 'provider_calls', 'candidate_evaluations_per_action')
    if any(type(limits.get(field)) is not int or limits[field] < 0 for field in required_limits) or type(limits.get('usd')) is not int or limits['usd'] != 0:
        return {'state': 'HOLD_INVALID_BUDGET_INPUT', 'errors': ['explicit nonnegative integer limits and integer usd=0 required']}
    for position, event in enumerate(actual_events):
        if type(event) is not dict or type(event.get('seq')) is not int or event['seq'] != position:
            errors.append('noncontiguous sequence at event' + str(position)); continue
        event_id = event.get('event_id')
        if type(event_id) is not str or event_id in seen_ids:
            errors.append('missing/duplicate event identity'); continue
        seen_ids.add(event_id)
        kind = event.get('kind')
        if kind in ('model_round', 'construct_action', 'submit_action', 'candidate_evaluation', 'provider_call'):
            field = {'model_round': 'model_rounds', 'construct_action': 'construct_actions',
                     'submit_action': 'submit_actions', 'candidate_evaluation': 'candidate_evaluations',
                     'provider_call': 'provider_calls'}[kind]
            counters[field] += 1
        else:
            errors.append('unknown event kind'); continue
        if kind == 'candidate_evaluation':
            parent = event.get('action_id')
            if type(parent) is not str or parent not in earlier_actions:
                errors.append('evaluation missing earlier action identity')
            else:
                evaluations_by_action[parent] = evaluations_by_action.get(parent, 0) + 1
        if kind in ('construct_action', 'submit_action'):
            earlier_actions.add(event_id)
        usd = event.get('usd', 0)
        if type(usd) not in (int, float) or usd != 0:
            errors.append('nonzero or invalid spend field')
        for field, bound in limits.items():
            if field in counters and field != 'usd' and type(bound) is int and counters[field] > bound:
                errors.append(field + ' exceeded')
    per_action_cap = limits.get('candidate_evaluations_per_action')
    if type(per_action_cap) is int and any(n > per_action_cap for n in evaluations_by_action.values()):
        errors.append('per-action candidate evaluation cap exceeded')
    if limits.get('usd') != 0:
        errors.append('zero-spend limit is required')
    return {'state': 'PASS_NORMALIZED_BUDGET' if not errors else 'HOLD_BUDGET_LOG',
            'actual_counters': counters, 'evaluations_by_action': evaluations_by_action,
            'errors': sorted(set(errors)),
            'ceiling': 'normalized event counts only; compare to raw actions/provider receipts separately'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', required=True, choices=sorted(TASKS))
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--output')
    args = parser.parse_args()
    path = Path(args.candidate)
    with path.open('rb') as source:
        raw = source.read(MAX_CANDIDATE_BYTES + 1)
    result = evaluate_bytes(raw, args.task)
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        destination = Path(args.output).resolve()
        allowed = Path(__file__).resolve().parent
        require(destination.is_relative_to(allowed), 'ORACLE_WRITE_SCOPE', 'output must remain under oracle/')
        with destination.open('x', encoding='utf-8') as stream:
            stream.write(encoded)
    else:
        print(encoded, end='')
    return 0 if result['arithmetic_valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
