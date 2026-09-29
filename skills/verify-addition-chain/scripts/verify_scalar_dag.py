"""Target-independent, read-only replay of a fixed-exponent addition-chain DAG.

The target manifest is supplied separately from the candidate. Search programs
may produce candidates but are not imported or executed by this verifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_manifest(path: Path) -> tuple[dict, bytes, int, int]:
    raw = path.read_bytes()
    if len(raw) > 16384:
        raise ValueError("manifest too large")
    manifest = json.loads(raw)
    if manifest.get("schema") != "hfo.chain_target.v0":
        raise ValueError("unknown manifest schema")
    if manifest.get("target_rule") != "scalar_n_minus_2":
        raise ValueError("unsupported target rule")
    for key, ceiling in (("max_candidate_bytes", 2_000_000), ("max_rows", 5000)):
        value = manifest.get(key)
        if type(value) is not int or not 0 < value <= ceiling:
            raise ValueError(f"invalid {key}")
    order = int(manifest["order_hex"], 16)
    if not 3 < order.bit_length() <= 4096 or order % 2 != 1:
        raise ValueError("invalid order size or parity")
    target = order - 2
    if manifest.get("target_hex") != format(target, "x"):
        raise ValueError("manifest target does not equal order minus two")
    return manifest, raw, order, target


def load_rows(path: Path, limit: int, order: int, target: int) -> tuple[list[tuple[int, int, int]], bytes]:
    raw = path.read_bytes()
    if len(raw) > limit:
        raise ValueError("candidate exceeds byte limit")
    json_candidate = path.suffix.lower() == ".json"
    if json_candidate:
        candidate = json.loads(raw)
        if not isinstance(candidate, dict) or candidate.get("schema") != "hfo.exponent_dag.v1":
            raise ValueError("unknown candidate schema")
        if type(candidate.get("n_hex")) is not str or int(candidate["n_hex"], 16) != order:
            raise ValueError("candidate order differs from manifest")
        if type(candidate.get("target_hex")) is not str or int(candidate["target_hex"], 16) != target:
            raise ValueError("candidate target differs from manifest")
        rows = candidate["rows"]
    else:
        rows = [line.split() for line in raw.decode("ascii").splitlines() if line.strip()]
    parsed: list[tuple[int, int, int]] = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, (list, tuple)) or len(row) != 3:
            raise ValueError(f"row {index}: expected three integers")
        if json_candidate:
            if any(type(value) is not int for value in row):
                raise ValueError(f"row {index}: noninteger JSON value")
        elif any(not re.fullmatch(r"[0-9]+", value) for value in row):
            raise ValueError(f"row {index}: nondecimal text value")
        parsed.append(tuple(int(value) for value in row))
    return parsed, raw


def replay(rows: list[tuple[int, int, int]], order: int, target: int, max_rows: int) -> tuple[int, int, int]:
    if not 0 < len(rows) <= max_rows:
        raise ValueError("row limit or empty candidate")
    seen = {1}
    last = 1
    squares = multiplies = 0
    for index, (out, left, right) in enumerate(rows, 1):
        if out <= last or out != left + right:
            raise ValueError(f"row {index}: nonincreasing or wrong sum")
        if left not in seen or right not in seen:
            raise ValueError(f"row {index}: missing parent")
        if out > target:
            raise ValueError(f"row {index}: exceeds target")
        seen.add(out)
        last = out
        squares += left == right
        multiplies += left != right
    if last != target:
        raise ValueError("terminal exponent differs from target")
    live = {target}
    dead = []
    for out, left, right in reversed(rows):
        if out in live:
            live.add(left)
            live.add(right)
        else:
            dead.append(out)
    if dead:
        raise ValueError(f"{len(dead)} dead rows; first exponents: {dead[:8]}")
    bases = (2, 3, 5, 7, 17, order - 1)
    for base in bases:
        powers = {1: base % order}
        for out, left, right in rows:
            powers[out] = powers[left] * powers[right] % order
        if powers[target] != pow(base, target, order):
            raise ValueError("modular replay disagrees with pow")
        if powers[target] * base % order != 1:
            raise ValueError("inverse identity failed")
    altered = list(rows)
    out, left, right = altered[-1]
    altered[-1] = (out + 1, left, right)
    try:
        replay_structure_only(altered, target)
    except ValueError:
        pass
    else:
        raise ValueError("damaged final row was accepted")
    return squares, multiplies, len(bases)


def replay_structure_only(rows: list[tuple[int, int, int]], target: int) -> None:
    seen = {1}
    last = 1
    for out, left, right in rows:
        if out <= last or out != left + right or left not in seen or right not in seen:
            raise ValueError("invalid row")
        seen.add(out)
        last = out
    if last != target:
        raise ValueError("wrong terminal exponent")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--candidate-sha256", required=True)
    args = parser.parse_args()
    start = time.perf_counter_ns()
    manifest, manifest_raw, order, target = load_manifest(args.manifest)
    if sha(manifest_raw) != args.manifest_sha256.lower():
        raise ValueError("manifest hash mismatch")
    rows, candidate_raw = load_rows(
        args.candidate, manifest["max_candidate_bytes"], order, target
    )
    digest = sha(candidate_raw)
    if digest.lower() != args.candidate_sha256.lower():
        raise ValueError("candidate hash mismatch")
    squares, multiplies, bases = replay(rows, order, target, manifest["max_rows"])
    print(json.dumps({
        "verdict": "PASS_LOCAL_ARITHMETIC",
        "target_id": manifest["target_id"],
        "manifest_sha256": sha(manifest_raw),
        "candidate_sha256": digest,
        "target_hex": format(target, "x"),
        "rows": len(rows),
        "squarings": squares,
        "multiplications": multiplies,
        "operations": squares + multiplies,
        "modular_bases_checked": bases,
        "last_row_mutation_rejected": True,
        "elapsed_ms": (time.perf_counter_ns() - start) / 1_000_000,
        "effect_ceiling": "LOCAL_ARITHMETIC_ONLY",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
