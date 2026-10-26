"""Frozen P-256 scalar precompute/window search with bounded two-policy assay."""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN_PATH = HERE / "frozen_plan.json"
PLAN_BYTES = PLAN_PATH.read_bytes()
PLAN = json.loads(PLAN_BYTES)
N = 115792089210356248762697446949407573529996955224135760342422259061068512044369
TARGET = N - 2
assert TARGET == int(PLAN["target_hex"], 16)
BITS = bin(TARGET)[2:]
REGION = PLAN["new_region"]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tie_key(values: tuple[int, ...], policy: str) -> str:
    return hashlib.sha256((str(REGION["seed"]) + ":" + policy + ":" + ",".join(map(str, values))).encode()).hexdigest()


def window_dp(values: tuple[int, ...]):
    allowed = set(values)
    length = len(BITS)
    infinity = (10**9, 10**9, 10**9)
    dp = [infinity] * (length + 1)
    choice = [None] * (length + 1)
    dp[length] = (0, 0, 0)
    transitions = 0
    for i in range(length - 1, 0, -1):
        v = 0
        for width in range(1, min(REGION["max_window_bits"], length - i) + 1):
            v = (v << 1) | int(BITS[i + width - 1])
            if v and v not in allowed:
                continue
            transitions += 1
            tail = dp[i + width]
            score = (tail[0] + width + int(v != 0), tail[1] + width, tail[2] + int(v != 0))
            if (score[0], score[2], score[1]) < (dp[i][0], dp[i][2], dp[i][1]):
                dp[i] = score
                choice[i] = (width, v)
    first = None
    first_score = infinity
    v = 0
    for width in range(1, min(REGION["max_window_bits"], length) + 1):
        v = (v << 1) | int(BITS[width - 1])
        if v in allowed:
            transitions += 1
            if (dp[width][0], dp[width][2], dp[width][1]) < (first_score[0], first_score[2], first_score[1]):
                first_score = dp[width]
                first = (width, v)
    assert first is not None
    return first_score, first, choice, transitions


def assess(state):
    values, parents = state
    main, first, choices, transitions = window_dp(values)
    sq = sum(a == b for a, b in parents)
    mul = len(parents) - sq
    score = (main[0] + len(parents), main[1] + sq, main[2] + mul)
    return score, first, choices, transitions


def certificate(state, first, choices):
    values, parents = state
    ops = [{"left": a, "right": b, "phase": "precompute"} for a, b in parents]
    exps = list(values)
    indices = {v: i for i, v in enumerate(values)}
    width, digit = first
    acc = indices[digit]
    position = width
    while position < len(BITS):
        shift, digit = choices[position]
        for _ in range(shift):
            ops.append({"left": acc, "right": acc, "phase": "accumulate"})
            exps.append(2 * exps[acc])
            acc = len(exps) - 1
        if digit:
            ops.append({"left": acc, "right": indices[digit], "phase": "accumulate"})
            exps.append(exps[acc] + digit)
            acc = len(exps) - 1
        position += shift
    assert exps[acc] == TARGET
    return {"schema": "hfo.p256_scalar_transfer_certificate.v1", "target_hex": format(TARGET, "x"),
            "source_plan_sha256": hashlib.sha256(PLAN_BYTES).hexdigest(), "precompute_values": list(values),
            "first_window": {"bits": width, "exponent": first[1]}, "operations": ops,
            "operation_count": len(ops), "squarings": sum(x["left"] == x["right"] for x in ops),
            "multiplications": sum(x["left"] != x["right"] for x in ops)}


def run_policy(policy: str):
    assert policy in REGION["policies"]
    budget = REGION["assessment_cap_each"]
    beam = [((1,), ())]
    best = None
    best_score = (10**9, 10**9, 10**9)
    counters = {"assessments": 0, "below_291": 0, "equal_291": 0, "above_291": 0,
                "raw_children": 0, "unique_children": 0, "unscored_due_cap": 0,
                "scored_not_selected": 0, "dp_transitions": 0}
    by_depth = []
    start_utc = utc()
    wall0 = time.perf_counter_ns()
    cpu0 = time.process_time_ns()
    trace_path = HERE / f"{policy}.assessments.jsonl.gz"
    with gzip.open(trace_path, "wt", encoding="utf-8", compresslevel=3) as trace:
        def logged(state, depth, origin):
            nonlocal best, best_score
            score, first, choices, transitions = assess(state)
            counters["assessments"] += 1
            counters["dp_transitions"] += transitions
            relation = "below_291" if score[0] < 291 else "equal_291" if score[0] == 291 else "above_291"
            counters[relation] += 1
            trace.write(json.dumps({"ordinal": counters["assessments"], "depth": depth, "origin": origin,
                                    "values": state[0], "parents": state[1], "score": score,
                                    "dp_transitions": transitions}, separators=(",", ":")) + "\n")
            if (score[0], score[2], score[1]) < (best_score[0], best_score[2], best_score[1]):
                best_score = score
                best = (state, first, choices)
            return score

        for depth in range(REGION["max_precompute_operations"] + 1):
            observed_beam = []
            for state in beam:
                if counters["assessments"] >= budget:
                    break
                observed_beam.append((state, logged(state, depth, "beam")))
            item = {"depth": depth, "beam_scored": len(observed_beam), "best_so_far": best_score[0]}
            if depth == REGION["max_precompute_operations"] or counters["assessments"] >= budget:
                by_depth.append(item)
                break
            candidates = {}
            raw = 0
            for (values, parents), _ in observed_beam:
                bound = values[-1]
                for i in range(len(values)):
                    for j in range(i, len(values)):
                        v = values[i] + values[j]
                        if not (bound < v <= REGION["max_precompute_exponent"]):
                            continue
                        raw += 1
                        key = values + (v,)
                        proposed = parents + ((i, j),)
                        old = candidates.get(key)
                        if old is None or sum(a != b for a, b in proposed) < sum(a != b for a, b in old[1]):
                            candidates[key] = (key, proposed)
            counters["raw_children"] += raw
            counters["unique_children"] += len(candidates)
            remaining = budget - counters["assessments"]
            ordered = sorted(candidates.values(), key=lambda state: tie_key(state[0], "sample"))
            chosen = ordered[:remaining]
            counters["unscored_due_cap"] += len(ordered) - len(chosen)
            rows = [(state, logged(state, depth + 1, "child")) for state in chosen]
            if policy == "score_guided":
                rows.sort(key=lambda row: (row[1][0], row[1][2], tie_key(row[0][0], policy)))
            else:
                rows.sort(key=lambda row: tie_key(row[0][0], policy))
            beam = [row[0] for row in rows[:REGION["beam_width"]]]
            counters["scored_not_selected"] += max(0, len(rows) - len(beam))
            item.update({"raw_children": raw, "unique_children": len(candidates), "children_scored": len(rows),
                         "children_selected": len(beam), "best_so_far": best_score[0]})
            by_depth.append(item)
            if not beam or counters["assessments"] >= budget:
                break
    wall_ns = time.perf_counter_ns() - wall0
    cpu_ns = time.process_time_ns() - cpu0
    cert = certificate(*best)
    cert_path = HERE / f"{policy}.certificate.json"
    cert_path.write_text(json.dumps(cert, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    out = {"schema": "hfo.p256_scalar_transfer_run.v1", "policy": policy, "start_utc": start_utc,
           "end_utc": utc(), "wall_ns": wall_ns, "process_cpu_ns": cpu_ns,
           "measurement_boundary": "search including trace write/close; excludes result assembly and verifier",
           "pid": os.getpid(), "plan_sha256": digest(PLAN_PATH), "generator_sha256": digest(Path(__file__)),
           "verifier_sha256": digest(HERE / "verify.py"), "pre_run_pin_sha256": digest(HERE / "pre_run_pin.json"),
           "trace_sha256": digest(trace_path), "certificate_sha256": digest(cert_path),
           "counters": counters, "by_depth": by_depth,
           "best": {"operations": cert["operation_count"], "squarings": cert["squarings"],
                    "multiplications": cert["multiplications"]},
           "provider_calls": 0, "paid_usd": 0, "model_tokens": None, "tao_review_minutes": None,
           "claim_ceiling": PLAN["claim_ceiling"]}
    (HERE / f"{policy}.result.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def main():
    assert digest(Path(PLAN["incumbent"]["source_path"])) == PLAN["incumbent"]["sha256"]
    assert digest(Path(PLAN["donor"]["source_path"])) == PLAN["donor"]["sha256"]
    pin = {"schema": "hfo.search_pre_run_pin.v1", "utc": utc(), "plan_sha256": digest(PLAN_PATH),
           "generator_sha256": digest(Path(__file__)), "verifier_sha256": digest(HERE / "verify.py"),
           "incumbent_sha256": PLAN["incumbent"]["sha256"], "donor_sha256": PLAN["donor"]["sha256"],
           "timing": "written before either policy search"}
    (HERE / "pre_run_pin.json").write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")
    for policy in REGION["policies"]:
        out = run_policy(policy)
        print(json.dumps({"policy": policy, "best": out["best"], "assessments": out["counters"]["assessments"],
                          "wall_ns": out["wall_ns"], "process_cpu_ns": out["process_cpu_ns"]}))


if __name__ == "__main__":
    main()
