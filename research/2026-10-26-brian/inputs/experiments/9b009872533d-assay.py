"""Matched P-521 scalar n-2 helper-case ordering assay; local CPU only."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import itertools
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN_PATH = HERE / "frozen_plan.json"
PLAN = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
SOURCE = Path(PLAN["generator_source"])
INCUMBENT = Path(PLAN["incumbent_certificate"])


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def cases() -> list[tuple[int, tuple[int, ...]]]:
    odds = tuple(range(3, 32, 2))
    return [(prefix, skips)
            for prefix in range(PLAN["region"]["prefixes_inclusive"][0],
                                PLAN["region"]["prefixes_inclusive"][1] + 1)
            for size in range(4)
            for skips in itertools.combinations(odds, size)]


def memory_key(case: tuple[int, tuple[int, ...]]):
    prefix, skips = case
    return (256 - prefix, 0 if 11 in skips else 1, len(skips), skips)


def control_key(case: tuple[int, tuple[int, ...]]):
    prefix, skips = case
    key = f"{PLAN['arms']['control_seed']}:{prefix}:{','.join(map(str, skips))}".encode("ascii")
    return hashlib.sha256(key).digest()


def run_arm(name: str, order: list, module) -> dict:
    attempted = valid = invalid = 0
    best = None
    best_key = None
    best_ordinal = None
    best_case = None
    start_utc = utc()
    start_wall = time.perf_counter_ns()
    start_cpu = time.process_time_ns()
    trace_path = HERE / f"{name}_attempts.jsonl.gz"
    with gzip.open(trace_path, "wt", encoding="utf-8", compresslevel=3) as trace:
        for prefix, skips in order[:PLAN["arms"]["attempts_each"]]:
            attempted += 1
            if (time.perf_counter_ns() - start_wall) > PLAN["limits"]["wall_seconds"] * 1_000_000_000:
                break
            try:
                _, windows = module.optimal_windows(module.BITS[prefix:], frozenset(skips))
                dag, dead = module.remove_dead_rows(module.construct(prefix, windows, frozenset(skips)))
                if dead and any(row[0] in dead for row in dag["rows"]):
                    raise AssertionError("liveness pruning failed")
                if dag["rows"][-1][0] != module.TARGET:
                    raise AssertionError("target mismatch")
            except ValueError as exc:
                invalid += 1
                trace.write(json.dumps({"ordinal": attempted, "prefix": prefix, "skips": skips,
                                        "status": "UNSUPPORTED_GRAMMAR", "reason": str(exc)},
                                       separators=(",", ":")) + "\n")
                continue
            valid += 1
            score = (4 * dag["squarings"] + 5 * dag["multiplications"], dag["total"], dag["multiplications"])
            if best_key is None or score < best_key:
                best = dag
                best_key = score
                best_ordinal = attempted
                best_case = {"prefix": prefix, "skips": list(skips)}
            trace.write(json.dumps({"ordinal": attempted, "prefix": prefix, "skips": skips,
                                    "status": "VALID_DAG", "squarings": dag["squarings"],
                                    "multiplications": dag["multiplications"], "total": dag["total"],
                                    "weighted_fifths": score[0]}, separators=(",", ":")) + "\n")
    wall_ns = time.perf_counter_ns() - start_wall
    cpu_ns = time.process_time_ns() - start_cpu
    best_path = HERE / f"{name}_best.json"
    if best is not None:
        best_payload = {k: best[k] for k in ("schema", "n_hex", "target_hex", "rows")}
        best_path.write_text(json.dumps(best_payload, separators=(",", ":")) + "\n", encoding="ascii")
    return {
        "arm": name, "start_utc": start_utc, "end_utc": utc(),
        "wall_ns": wall_ns, "process_cpu_ns": cpu_ns,
        "attempts": attempted, "valid_dags": valid, "unsupported_grammar": invalid,
        "full_budget_completed": attempted == PLAN["arms"]["attempts_each"],
        "best": {"squarings": best["squarings"], "multiplications": best["multiplications"],
                 "total": best["total"], "weighted_fifths": best_key[0],
                 "weighted_0_8": best_key[0] / 5,
                 "first_found_ordinal": best_ordinal, "case": best_case,
                 "certificate_sha256": sha(best_path)} if best else None,
        "trace_sha256": sha(trace_path),
        "measurement_boundary": "arm order evaluation through compressed trace close; excludes plan pin and final summary write"
    }


def main() -> None:
    assert sha(SOURCE) == PLAN["generator_sha256"], "generator drift"
    assert sha(INCUMBENT) == PLAN["incumbent_sha256"], "incumbent drift"
    all_cases = cases()
    assert len(all_cases) == PLAN["region"]["case_count"]
    source_spec = importlib.util.spec_from_file_location("p521_prior_generator", SOURCE)
    assert source_spec and source_spec.loader
    module = importlib.util.module_from_spec(source_spec)
    source_spec.loader.exec_module(module)
    assert module.TARGET == module.N - 2
    pin = {"schema": "hfo.p521_transfer_pre_run_pin.v1", "observed_utc": utc(),
           "plan_sha256": sha(PLAN_PATH), "assay_sha256": sha(Path(__file__)),
           "generator_sha256": sha(SOURCE), "incumbent_sha256": sha(INCUMBENT),
           "pid": os.getpid(), "written_before_first_case": True}
    (HERE / "pre_run_pin.json").write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")
    memory_order = sorted(all_cases, key=memory_key)
    control_order = sorted(all_cases, key=control_key)
    arms = [run_arm("memory_guided", memory_order, module),
            run_arm("memory_ablated_control", control_order, module)]
    summary = {"schema": "hfo.p521_scalar_memory_transfer_result.v1",
               "observed_utc": utc(), "plan_sha256": sha(PLAN_PATH),
               "assay_sha256": sha(Path(__file__)), "pre_run_pin_sha256": sha(HERE / "pre_run_pin.json"),
               "target_hex": format(module.TARGET, "x"), "arms": arms,
               "provider_calls": 0, "paid_usd": 0,
               "caveat": "Historical P-521 local winner informed the memory ordering; no autonomous learning claim."}
    (HERE / "result.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"arms": arms, "plan_sha256": summary["plan_sha256"]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
