"""Independent full primary audit: read raw data; execute no candidate/harness code."""
import csv
import hashlib
import io
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import evaluate
from integration_audit_v1 import transform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULT = ROOT / 'analysis/PRIMARY_RESULTS.json'
TABLE = ROOT / 'analysis/PRIMARY_RESULTS.csv'
EXPECTED_RESULT = '5d884748187c90fb7413a9ba17e65103955ea736ad142da26826945c93f75ac8'
EXPECTED_TABLE = '0cddea566120c3468b165dd782a6ecd11c4db1f9fc6d1b46ac1783ed0271f2bf'
PINS = []
CONTEXT = {}


def need(ok, code):
    if not ok:
        raise AssertionError(code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    raw = path.read_bytes()
    PINS.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(raw), 'bytes': len(raw)})
    return json.loads(raw.decode('utf-8-sig'))


def lines(path):
    raw = path.read_bytes()
    PINS.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(raw), 'bytes': len(raw)})
    return [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]


def canon(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def schedule_hash(candidate, target):
    return digest(canon({'target': str(target), 'steps': [sorted(p) for p in candidate['steps']],
                         'output_index': candidate.get('output_index', len(candidate['steps']))}).encode())


def matches(actual, expected):
    if type(actual) is float and type(expected) is float:
        return math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-9)
    return actual == expected


def main():
    need(digest((HERE / 'evaluate.py').read_bytes()) == '826aff70f4a60f6527c2d2e3f4aa6181d009a60fb26c32f43743b0da03dc046d', 'ORACLE_DRIFT')
    need(digest((ROOT / 'control/run_episode_memory_v1.py').read_bytes()) == '058d52ab821f33831d25c931e537ca065604fe7458408819c3b055f871da81f1', 'RUNNER_DRIFT')
    need(digest((ROOT / 'harness/v1/ac_environment.py').read_bytes()) == 'd9dceb2fc3c967e83277bbcc20be4115fd62ea30ede62f4b980be6c178fac723', 'HARNESS_DRIFT')
    jobs = load(ROOT / 'control/MEMORY_RUN_ORDER.json')
    profile = load(ROOT / 'control/CODEX_PROFILE.json')
    profile_sha = digest((ROOT / 'control/CODEX_PROFILE.json').read_bytes())
    schema_sha = digest((ROOT / 'stimuli/action.v2.schema.json').read_bytes())
    template = (ROOT / 'stimuli/PROMPT_TEMPLATE.v2.txt').read_text()
    skill = (ROOT / 'stimuli/skill.txt').read_text()
    need(len(jobs) == len({j['id'] for j in jobs}) == 12, 'ASSIGNMENT_DENOMINATOR')
    independent_rows, candidate_rows, checks, intervals, missing_usage = [], [], [], [], []
    global_evaluation_ids, global_action_ids, environment_ids = set(), set(), set()
    for job in jobs:
        CONTEXT.clear(); CONTEXT.update(trajectory=job['id'])
        path = ROOT / 'runs/memory-v1' / job['id']
        need(load(path / 'JOB.json') == job, 'JOB_ASSIGNMENT_DRIFT')
        report = load(path / 'RUN_RECEIPT.json')
        final = load(path / 'TRUSTED_FINAL.json')
        cell, task = job['cell'], job['task']
        need(task['target'] == evaluate.TASKS[task['id']], 'TASK_INTEGER_DRIFT')
        need(report['state'] in ('COMPLETED', 'TIMEOUT'), 'UNRECOGNIZED_TERMINAL_STATE')
        need(final['task_id'] == task['id'] and int(final['target_decimal']) == task['target'], 'FINAL_TASK_DRIFT')
        need(final['tools_enabled'] == cell['tools'] and final['feedback_enabled'] == cell['feedback'], 'FINAL_TREATMENT_DRIFT')
        need(final['environment_id'] not in environment_ids, 'GLOBAL_ENVIRONMENT_ID_COLLISION')
        environment_ids.add(final['environment_id'])
        rounds = report['rounds']
        need(1 <= len(rounds) <= 3, 'DECISION_CAP')
        model_events = []
        history, raw_events, records, regions, actions = [], [], [], [], []
        seen_raw, seen_schedule, best_rank, best_record = set(), set(), None, None
        valid_count = invalid_count = duplicates = dead_records = repeated_value_records = 0
        ordinal = 0
        for round_no, model_receipt in enumerate(rounds, 1):
            CONTEXT.update(round=round_no)
            folder = path / f'round-{round_no}'
            request = load(folder / 'REQUEST.json')
            receipt = load(folder / 'RECEIPT.json')
            need(receipt == model_receipt, 'MODEL_RECEIPT_COPY_DRIFT')
            need(request['model'] == job['model'] and request['effort'] == 'medium' and request['automatic_retries'] == 0, 'MODEL_ROUTE_OR_RETRY_DRIFT')
            need(request['profile_sha256'] == profile_sha and request['schema_sha256'] == schema_sha, 'MODEL_PROFILE_SCHEMA_DRIFT')
            prompt_path = folder / 'prompt.txt'
            prompt_raw = prompt_path.read_bytes()
            PINS.append({'path': str(prompt_path.relative_to(ROOT)), 'sha256': digest(prompt_raw), 'bytes': len(prompt_raw)})
            prompt = prompt_path.read_text()
            memory_name = 'irrelevant.v2.txt' if cell['memory'] == 'irrelevant' else cell['memory'] + '.txt'
            memory = (ROOT / 'stimuli' / memory_name).read_text() if cell['memory'] != 'none' else '(none)'
            expected_prompt = template.format(label=cell['label'], target=task['target'], baseline=task['binary_baseline'],
                                              tools='on' if cell['tools'] else 'off', feedback='on' if cell['feedback'] else 'off',
                                              skill=skill if cell['skill'] else '', memory_kind='provided' if cell['memory'] != 'none' else 'absent',
                                              memory=memory, round=round_no, history=json.dumps(history, separators=(',', ':')))
            need(prompt == expected_prompt and digest(prompt.encode()) == request['prompt_sha256'], 'PROMPT_OR_HISTORY_DRIFT')
            need(job['id'] not in prompt and 'oracle/' not in prompt.lower() and 'oracle\\' not in prompt.lower(), 'ASSIGNMENT_OR_ORACLE_PATH_LEAK')
            stream = lines(folder / 'events.jsonl')
            native = [e['item'] for e in stream if isinstance(e.get('item'), dict) and e['item'].get('type') not in ('agent_message', 'reasoning')]
            need(not native, 'NATIVE_TOOL_CONTAMINATION')
            if 'native_tool_events' in receipt:
                need(receipt['native_tool_events'] == 0, 'NATIVE_TOOL_COUNTER_DRIFT')
            start = datetime.fromisoformat(request['started_utc'])
            end = datetime.fromisoformat(receipt['ended_utc'])
            need(start <= end and start < datetime(2026, 10, 26, 19, 24, 8, tzinfo=timezone.utc), 'CALL_HORIZON_OR_CLOCK')
            intervals.append((start, end, job['id'], round_no))
            model_events.extend([{'event_id': f'model-{round_no}', 'kind': 'model_round'},
                                 {'event_id': f'provider-{round_no}', 'kind': 'provider_call'}])
            if receipt['state'] == 'TIMEOUT':
                need(report['state'] == 'TIMEOUT' and round_no == len(rounds), 'TIMEOUT_RETRY_OR_STATE')
                need(not (path / f'action-{round_no}.json').exists(), 'ACTION_AFTER_TIMEOUT')
                missing_usage.append({'trajectory_id': job['id'], 'round': round_no, 'state': 'TIMEOUT_USAGE_UNKNOWN'})
                continue
            need(receipt['state'] == 'RETURNED' and receipt['returncode'] == 0, 'UNEXPECTED_MODEL_RECEIPT')
            completed = [e for e in stream if e.get('type') == 'turn.completed']
            need(len(completed) == 1 and completed[0].get('usage', {}) == receipt.get('usage', {}), 'STREAM_USAGE_MISMATCH')
            proposal = load(folder / 'answer.json')
            need(receipt['answer_sha256'] == digest((folder / 'answer.json').read_bytes()), 'ANSWER_BYTE_DRIFT')
            action_path = path / f'action-{round_no}.json'
            action = load(action_path)
            need(transform(proposal) == action, 'PROPOSAL_TRANSFORMATION_DRIFT')
            event = load(path / f'environment/round-{round_no:02d}.event.json')
            need(event['round'] == round_no and event['parsed_action'] == action, 'RAW_ACTION_EVENT_DRIFT')
            need(event['event_id'] == event['action_id'] == event['receipt_id'] and event['event_id'] not in global_action_ids, 'ACTION_IDENTITY_COLLISION')
            global_action_ids.add(event['event_id'])
            need(event['action_sha256'] == digest(action_path.read_bytes()), 'ACTION_BYTE_PIN_MISMATCH')
            need((path / f'environment/round-{round_no:02d}.action.bin').read_bytes() == action_path.read_bytes(), 'ACTION_CAPTURE_MISMATCH')
            if not cell['tools']:
                need(action['type'] == 'submit_chain' or event['status'] == 'REFUSED', 'TOOLS_OFF_BYPASS')
            child_rows = lines(path / f'environment/round-{round_no:02d}.candidates.jsonl')
            need(event['evaluated_candidates'] == len(child_rows) <= 64, 'ACTUAL_EVALUATION_COUNTER')
            need(event['censored_candidates'] == (max(0, event['configured_candidates'] - len(child_rows)) if event['status'] == 'COMPLETE' else event['configured_candidates']), 'CENSOR_COUNTER')
            need(event['status'] != 'REFUSED' or not child_rows, 'REFUSED_ACTION_EVALUATED')
            visible = []
            model_events.append({'event_id': event['event_id'], 'kind': 'submit_action' if action['type'] == 'submit_chain' else 'construct_action'})
            for record in child_rows:
                ordinal += 1
                CONTEXT.update(candidate=record['candidate_id'])
                need(record['global_evaluation_ordinal'] == ordinal and record['event_id'] not in global_evaluation_ids, 'EVALUATION_ID_OR_ORDINAL')
                global_evaluation_ids.add(record['event_id'])
                need(record['action_id'] == event['event_id'] and record['source_action_sha256'] == event['action_sha256'], 'CANDIDATE_ACTION_PROVENANCE')
                candidate, assessment = record['candidate'], record['assessment']
                replay = evaluate.evaluate_payload(candidate, task['id'])
                need(replay['arithmetic_valid'] == assessment['valid'], 'CANDIDATE_VALIDITY_MISMATCH')
                raw_hash = digest(canon(candidate).encode()) if candidate is not None else None
                identity = schedule_hash(candidate, task['target']) if replay['arithmetic_valid'] else None
                need(raw_hash == assessment.get('raw_candidate_sha256'), 'CANONICAL_CANDIDATE_BYTE_HASH')
                need(record['raw_duplicate'] == bool(raw_hash and raw_hash in seen_raw), 'RAW_DUPLICATE_COUNTER')
                need(record['canonical_schedule_duplicate'] == bool(identity and identity in seen_schedule), 'INDEX_DUPLICATE_COUNTER')
                if raw_hash: seen_raw.add(raw_hash)
                if identity: seen_schedule.add(identity)
                duplicates += int(record['canonical_schedule_duplicate'])
                if replay['arithmetic_valid']:
                    valid_count += 1
                    need(replay['charged'] == assessment['charged'] and replay['live'] == assessment['live'], 'S_M_OR_LIVENESS_MISMATCH')
                    need(replay['dead']['operations'] == assessment['dead']['operations'] and replay['dead']['node_indices'] == assessment['dead']['row_indices'], 'DEAD_ROW_MISMATCH')
                    need(identity == assessment['canonical_schedule_sha256'], 'SCHEDULE_IDENTITY_MISMATCH')
                    rank = (replay['charged']['operations'], replay['charged']['M'], identity)
                    if best_rank is None or rank < best_rank:
                        best_rank, best_record = rank, record
                    dead_records += int(bool(replay['dead']['operations']))
                    repeated_value_records += int(bool(replay['repeated_exponent_values']))
                else:
                    invalid_count += 1
                region = canon({'method': record['method'], 'knobs': record['knobs']}) if record['method'] != 'explicit' else 'explicit:' + str(identity)
                regions.append(region)
                visible.append({'candidate_id': record['candidate_id'], 'valid': assessment['valid'], 'reason': assessment.get('reason'),
                                'charged': assessment.get('charged'), 'live': assessment.get('live'), 'dead': assessment.get('dead'),
                                'duplicate': record['canonical_schedule_duplicate']})
                candidate_rows.append({'trajectory_id': job['id'], 'ordinal': ordinal, 'candidate_id': record['candidate_id'],
                                       'valid': replay['arithmetic_valid'], 'cost': replay.get('charged', {}).get('operations'),
                                       'S': replay.get('charged', {}).get('S'), 'M': replay.get('charged', {}).get('M'),
                                       'live': replay.get('live', {}).get('operations'), 'dead': replay.get('dead', {}).get('operations'),
                                       'schedule_sha256': identity, 'duplicate': record['canonical_schedule_duplicate']})
                model_events.append({'event_id': record['event_id'], 'kind': 'candidate_evaluation', 'action_id': event['event_id']})
            need(event['invalid_candidates'] == sum(not r['assessment']['valid'] for r in child_rows), 'INVALID_COUNTER')
            need(event['canonical_duplicate_candidates'] == sum(r['canonical_schedule_duplicate'] for r in child_rows), 'DUPLICATE_EVENT_COUNTER')
            feedback = load(path / f'feedback-{round_no}.json')
            need(feedback == load(path / f'environment/round-{round_no:02d}.feedback.json'), 'VISIBLE_FEEDBACK_COPY_DRIFT')
            if cell['feedback']:
                best = best_record
                public_best = None if best is None else {'candidate_id': best['candidate_id'], 'candidate': best['candidate'],
                                                        'charged': best['assessment']['charged'], 'live': best['assessment']['live'], 'dead': best['assessment']['dead']}
                expected_feedback = {'status': event['status'], 'reason': event['reason'], 'receipt_id': event['event_id'],
                                     'round': round_no, 'rounds_remaining': 3 - round_no, 'evaluations': visible,
                                     'censored_candidates': event['censored_candidates'], 'best_so_far': public_best}
            else:
                expected_feedback = {'status': 'ACK', 'receipt_id': event['event_id'], 'round': round_no, 'rounds_remaining': 3 - round_no}
            need(feedback == expected_feedback, 'FEEDBACK_MASK_OR_VALUE_DRIFT')
            history.append({'action': action, 'visible_feedback': feedback})
            records.extend(child_rows); raw_events.append(event); actions.append(action)
        need(final['events'] == raw_events and final['candidate_evaluations'] == ordinal, 'FINAL_RAW_DENOMINATOR')
        need(final['rounds_used'] == len(raw_events) and final['complete'] == (len(raw_events) == 3), 'ENVIRONMENT_COMPLETION_COUNTER')
        expected_best = None if best_record is None else best_record['candidate']
        need(final['best_candidate'] == expected_best, 'FINAL_MINIMUM_RANK_AGGREGATION')
        best = None if expected_best is None else evaluate.evaluate_payload(expected_best, task['id'])
        if best:
            need(final['best_local_assessment'] == best_record['assessment'], 'FINAL_BEST_ASSESSMENT_COPY')
        previous_state_sha = None
        state_files = sorted((path / 'environment').glob('STATE-[0-9][0-9][0-9].json'))
        need(len(state_files) == len(raw_events) + 1, 'STATE_CHAIN_LENGTH')
        for state_no, state_path in enumerate(state_files):
            state = load(state_path)
            need(state['previous_state_sha256'] == previous_state_sha and state['rounds_used'] == state_no, 'STATE_CHAIN_DRIFT')
            need(state['environment_id'] == final['environment_id'] and state['target'] == task['target'], 'STATE_IDENTITY_DRIFT')
            previous_state_sha = digest(state_path.read_bytes())
        for seq, event in enumerate(model_events): event.update(seq=seq, usd=0)
        budget = evaluate.audit_budget_counts(model_events, {'model_rounds': 3, 'construct_actions': 3, 'submit_actions': 3,
                                                           'candidate_evaluations': 195, 'provider_calls': 3,
                                                           'candidate_evaluations_per_action': 64, 'usd': 0})
        need(budget['state'] == 'PASS_NORMALIZED_BUDGET', 'BUDGET_LOG_HOLD')
        row = {'trajectory_id': job['id'], 'task_id': task['id'], 'target': task['target'], 'replicate_id': job['replicate'],
               'cell_id': cell['id'], 'cell_name': cell['name'], 'model': job['model'], 'state': report['state'],
               'failure_or_censor_reason': report.get('error'), 'tools': cell['tools'], 'feedback': cell['feedback'],
               'skill': cell['skill'], 'memory': cell['memory'], 'public_baseline': task['binary_baseline'],
               'best_valid_cost': best['charged']['operations'] if best else None,
               'best_S': best['charged']['S'] if best else None, 'best_M': best['charged']['M'] if best else None,
               'best_identity': best_rank[2] if best_rank else None, 'best_live': best['live']['operations'] if best else None,
               'best_dead': best['dead']['operations'] if best else None,
               'attempted_rounds': len(rounds), 'returned_rounds': sum(r['state'] == 'RETURNED' for r in rounds),
               'environment_rounds': len(raw_events), 'action_sequence': actions,
               'action_family_sequence': [a['type'] + ':' + str(a.get('method', 'explicit')) for a in actions],
               'region_sequence': regions, 'realized_evaluations': ordinal, 'unique_regions': len(set(regions)),
               'valid_candidates': valid_count, 'invalid_candidates': invalid_count,
               'refused_actions': sum(e['status'] == 'REFUSED' for e in raw_events),
               'unique_schedule_count': len(seen_schedule), 'duplicate_candidates': duplicates,
               'native_tool_events': 0,
               'model_input_tokens': sum(r.get('usage', {}).get('input_tokens', 0) for r in rounds),
               'model_cached_input_tokens': sum(r.get('usage', {}).get('cached_input_tokens', 0) for r in rounds),
               'model_output_tokens': sum(r.get('usage', {}).get('output_tokens', 0) for r in rounds),
               'model_reasoning_output_tokens': sum(r.get('usage', {}).get('reasoning_output_tokens', 0) for r in rounds),
               'model_wall_s': sum(r.get('wall_s', 0) for r in rounds),
               'search_cpu_s': sum(e['process_cpu_seconds'] for e in raw_events),
               'started_utc': report.get('started_utc'), 'ended_utc': report.get('ended_utc'),
               'independent_validation': 'AWAITING_FULL_ORACLE_AUDIT'}
        row.update(improvement_over_binary=task['binary_baseline'] - row['best_valid_cost'] if best else None,
                   duplicate_fraction=duplicates / ordinal if ordinal else None,
                   aggregation_min_matches_records=True)
        independent_rows.append(row)
        checks.append({'trajectory_id': job['id'], 'state': report['state'], 'candidates': ordinal,
                       'charged_best': best.get('charged') if best else None, 'budget': budget,
                       'dead_candidate_records': dead_records, 'repeated_value_candidate_records': repeated_value_records,
                       'prompt_transform_feedback_state_rank_checks': 'PASS'})
    need(len(independent_rows)==12 and all(r['state']=='COMPLETED' for r in independent_rows),'MEMORY_COMPLETION_DENOMINATOR')
    need(len(intervals)==36 and not missing_usage,'MEMORY_CALL_DENOMINATOR')
    requests=list((ROOT/'runs/memory-v1').rglob('REQUEST.json'))
    need(len(requests)==36,'MEMORY_PHYSICAL_REQUEST_COUNT')
    sweep=sorted([(a,1) for a,b,t,n in intervals]+[(b,-1) for a,b,t,n in intervals],key=lambda x:(x[0],x[1]))
    active=maximum=0
    for _,delta in sweep:active+=delta;maximum=max(maximum,active)
    need(active==0 and maximum<=2,'MEMORY_CONCURRENCY')
    candidate_path=HERE/'MEMORY_CANDIDATE_AUDIT.v1.csv'
    with candidate_path.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(candidate_rows[0]));writer.writeheader();writer.writerows(candidate_rows)
    totals={'trajectories':12,'completed':12,'actual_calls':36,'returned_calls':36,'actual_candidate_records':len(candidate_rows),'valid_candidate_records':sum(r['valid_candidates'] for r in independent_rows),'invalid_candidate_records':sum(r['invalid_candidates'] for r in independent_rows),'native_tool_events':0,'model_input_tokens':sum(r['model_input_tokens'] for r in independent_rows),'model_output_tokens':sum(r['model_output_tokens'] for r in independent_rows),'max_cli_overlap':maximum}
    out=HERE/'MEMORY_RAW_AUDIT.v1.json'
    receipt={'schema':'independent-memory-raw-audit.v1','observed_utc':datetime.now(timezone.utc).isoformat(),'verdict':'VERIFICATION_PASS_RAW_MEMORY_PENDING_PRODUCER_METRIC_COMPARISON','source_sha256':digest(Path(__file__).read_bytes()),'oracle_sha256':digest((HERE/'evaluate.py').read_bytes()),'candidate_audit_sha256':digest(candidate_path.read_bytes()),'totals':totals,'rows':independent_rows,'trajectory_checks':checks,'raw_input_pins':list({p['path']:p for p in PINS}.values()),'scope':'All raw data verified. Current-target source, supplied packet, wider primary pool and producer contrasts compared separately. No inference or candidate code execution.'}
    out.write_text(json.dumps(receipt,indent=2)+'\n')
    used=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());need(used<4000000,'ORACLE_ARTIFACT_CAP')
    print(json.dumps({'verdict':receipt['verdict'],'totals':totals,'receipt_sha256':digest(out.read_bytes()),'oracle_bytes':used}))

if __name__=='__main__':
    try:main()
    except Exception as exc:
        p=HERE/('MEMORY_AUDIT_FIRST_FAILURE-'+datetime.now(timezone.utc).strftime('%H%M%S')+'.json')
        p.write_text(json.dumps({'state':'VERIFICATION_FAIL_PRESERVED','context':CONTEXT,'reason':str(exc),'input_pins':PINS},indent=2)+'\n')
        print(json.dumps({'state':'VERIFICATION_FAIL_PRESERVED','reason':str(exc),'context':CONTEXT,'receipt':str(p)}));raise
