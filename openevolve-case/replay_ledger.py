"""Arithmetic replay of a sanitized, source-reported search ledger.

This proves the listed genotypes compile to independently valid certificates.
It does not authenticate the omitted engine logs, model replies, or timing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from decoder import SCHEMA, from_bytes
from independent_verify import replay


HERE = Path(__file__).resolve().parent
FIELDS = {
    "run", "iteration", "parent", "bridge", "ranks", "operations",
    "squarings", "multiplications", "certificate_sha256", "reported_source",
}
RUN_SIZES = {"run_001": 1, "run_002": 8, "run_003": 8}
MAX_LEDGER_BYTES = 32768
SEED_SHA256 = "1cb02c61d877caeb08e61b183369b8d5ba370ce354960f6371a6600fee99473a"


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate ledger key")
        result[key] = value
    return result


def reject_number(_value: str) -> None:
    raise ValueError("non-integer ledger number")


def check(rows: list[dict[str, object]]) -> dict[str, object]:
    if len(rows) != sum(RUN_SIZES.values()):
        raise ValueError("ledger row count")
    seed_genome = json.loads((HERE / "seed.json").read_bytes())
    seed = from_bytes((HERE / "seed.json").read_bytes())
    seed_check = replay(seed.certificate)
    if (seed_check["sha256"] != SEED_SHA256 or
            (seed_check["operations"], seed_check["squarings"], seed_check["multiplications"]) != (421, 381, 40)):
        raise ValueError("seed arithmetic or hash")
    seen: dict[str, dict[str, object]] = {"seed": seed_genome}
    counts = {run: 0 for run in RUN_SIZES}
    distinct: dict[str, set[str]] = {run: set() for run in RUN_SIZES}
    all_hashes: set[str] = set()
    parent_identical = 0
    best_generated = 10**9
    expected_order = [run for run, size in RUN_SIZES.items() for _ in range(size)]
    for index, item in enumerate(rows):
        if type(item) is not dict or set(item) != FIELDS:
            raise ValueError("ledger shape")
        run = item["run"]
        if type(run) is not str or run != expected_order[index]:
            raise ValueError("ledger run order")
        counts[run] += 1
        iteration = item["iteration"]
        if type(iteration) is not int or iteration != counts[run]:
            raise ValueError("ledger iteration order")
        source = item["reported_source"]
        expected_source = ("private_engine_log_and_checkpoint_no_trace_row"
                           if run == "run_003" and iteration == 6 else "private_trace")
        if source != expected_source:
            raise ValueError("reported source label")
        parent = item["parent"]
        if type(parent) is not str or parent not in seen:
            raise ValueError("unknown or future parent")
        if parent != "seed" and not parent.startswith(run + "_"):
            raise ValueError("cross-run parent")
        genome = {"schema": SCHEMA, "bridge": item["bridge"], "ranks": item["ranks"]}
        raw = json.dumps(genome, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"
        result = from_bytes(raw)
        independent = replay(result.certificate)
        for field in ("operations", "squarings", "multiplications"):
            if type(item[field]) is not int or item[field] != independent[field]:
                raise ValueError("certificate count mismatch")
        if (type(item["certificate_sha256"]) is not str or
                item["certificate_sha256"] != independent["sha256"]):
            raise ValueError("certificate hash mismatch")
        if genome == seen[parent]:
            parent_identical += 1
        identity = f"{run}_{iteration}"
        seen[identity] = genome
        distinct[run].add(independent["sha256"])
        all_hashes.add(independent["sha256"])
        best_generated = min(best_generated, independent["operations"])
    return {
        "status": "PASS_LOCAL_LEDGER_REPLAY",
        "evidence_ceiling": "ARITHMETIC_AND_SANITIZED_PROJECTION_NOT_ENGINE_AUTHENTICATION",
        "seed_operations": seed_check["operations"],
        "generated_rows": len(rows),
        "distinct_generated_certificates": len(all_hashes),
        "distinct_by_run": {run: len(values) for run, values in distinct.items()},
        "parent_identical_genomes": parent_identical,
        "best_generated_operations": best_generated,
    }


def load(path: Path) -> list[dict[str, object]]:
    raw = path.read_bytes()
    if not 0 < len(raw) <= MAX_LEDGER_BYTES or not raw.endswith(b"\n"):
        raise ValueError("ledger size or terminator")
    return [json.loads(line, object_pairs_hook=unique_object,
                       parse_float=reject_number, parse_constant=reject_number)
            for line in raw.decode("ascii").splitlines()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true",
                        help="also prove that a tampered certificate hash is rejected")
    args = parser.parse_args()
    rows = load(HERE / "candidate_ledger.jsonl")
    result = check(rows)
    if args.selftest:
        altered = [dict(row) for row in rows]
        altered[0]["certificate_sha256"] = "0" * 64
        try:
            check(altered)
        except ValueError as exc:
            if str(exc) != "certificate hash mismatch":
                raise
        else:
            raise AssertionError("tampered hash was accepted")
        result["tampered_hash_rejected"] = True
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
