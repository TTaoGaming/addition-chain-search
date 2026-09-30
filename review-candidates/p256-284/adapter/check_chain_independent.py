#!/usr/bin/env python3
"""One-shot, standard-library-only exact checker, written for this replay.

No producer or existing verifier code is imported. Exponent arithmetic uses
Python arbitrary-precision integers. This is not a constant-time implementation.
The only free exponent is 1. Every row is one charged sum of earlier exponents.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
TARGET = N - 2
SCHEMA = "hfo.addition_chain_dag.v0"


class Rejected(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def require(condition, code, message):
    if not condition:
        raise Rejected(code, message)


def unique_keys(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "DUPLICATE_JSON_KEY", f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def parse(raw):
    require(len(raw) <= 2_000_000, "INPUT_SIZE", "certificate exceeds 2 MB bound")
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Rejected("JSON", str(exc)) from exc
    require(type(obj) is dict, "OBJECT", "certificate must be a JSON object")
    return obj


def hex_integer(obj, field):
    value = obj.get(field)
    require(type(value) is str and re.fullmatch(r"[0-9a-fA-F]+", value) is not None,
            "HEX", f"{field} must be an unprefixed hexadecimal string")
    return int(value, 16)


def digest_check(raw, expected):
    actual = hashlib.sha256(raw).hexdigest()
    require(actual == expected, "RAW_SHA256", f"expected {expected}, got {actual}")
    return actual


def verify(obj):
    require(obj.get("schema") == SCHEMA, "SCHEMA", "unexpected certificate schema")
    require(hex_integer(obj, "n_hex") == N, "MODULUS", "modulus is not the pinned P-256 scalar order")
    require(hex_integer(obj, "target_hex") == TARGET, "TARGET", "target is not the exact integer n-2")
    rows = obj.get("rows")
    require(type(rows) is list and 0 < len(rows) <= 4096, "ROWS", "rows must be a nonempty bounded array")
    for field in ("operations", "squarings", "multiplications"):
        require(type(obj.get(field)) is int and obj[field] >= 0, "COUNT_TYPE", f"{field} must be a nonnegative integer")
    require(obj["operations"] == len(rows), "OPERATION_COUNT", "declared total differs from rows length")
    require(obj.get("all_rows_live") is True, "LIVE_DECLARATION", "all_rows_live must be true")

    # First path: exact value-DAG replay in original declared row order.
    producers = {1: -1}
    parents = []
    outputs = []
    squarings = 0
    descents = []
    for index, row in enumerate(rows):
        require(type(row) is list and len(row) == 3, "ROW_SHAPE", f"row {index+1} must have three entries")
        require(all(type(v) is int for v in row), "INTEGER_TYPE", f"row {index+1} contains a non-integer, float, or bool")
        out, left, right = row
        require(min(row) > 0, "POSITIVITY", f"row {index+1} contains a nonpositive value")
        require(left in producers and right in producers, "EARLIER_PARENT", f"row {index+1} uses an unavailable earlier parent")
        require(out not in producers, "DUPLICATE_OUTPUT", f"row {index+1} repeats exponent {out}")
        require(left + right == out, "EXACT_SUM", f"row {index+1} does not equal the sum of its declared parents")
        if outputs and out < outputs[-1]:
            descents.append(index+1)
        parents.append((producers[left], producers[right]))
        producers[out] = index
        outputs.append(out)
        squarings += int(left == right)
    require(outputs[-1] == TARGET, "FINAL_TARGET", "final exponent is not n-2")
    require(squarings == obj["squarings"], "SQUARING_COUNT", "declared squaring count differs")
    multiplications = len(rows) - squarings
    require(multiplications == obj["multiplications"], "MULTIPLICATION_COUNT", "declared multiplication count differs")

    # Reverse reachability means charged but unused helpers cannot hide in rows.
    live = set()
    work = [len(rows)-1]
    while work:
        index = work.pop()
        if index < 0 or index in live:
            continue
        live.add(index)
        work.extend(parents[index])
    require(len(live) == len(rows), "DEAD_ROW", f"dead rows: {[i+1 for i in range(len(rows)) if i not in live]}")

    # Second path: an index-register machine recomputes exponents from 1,
    # without trusting row outputs as the register's stored arithmetic value.
    registers = [1]
    index_squarings = 0
    for index, (left, right) in enumerate(parents):
        value = registers[left+1] + registers[right+1]
        require(value == outputs[index], "INDEX_REPLAY", f"index replay mismatch at row {index+1}")
        registers.append(value)
        index_squarings += int(left == right)
    require(registers[-1] == TARGET and index_squarings == squarings,
            "INDEX_REPLAY", "index result/count does not agree")

    # Independent sorted-value existence test; it may find different parents.
    # Its chosen parent counts are deliberately NOT substituted for declared ones.
    sorted_values = [1] + sorted(outputs)
    for i in range(1, len(sorted_values)):
        left, right = 0, i-1
        goal = sorted_values[i]
        while left <= right:
            total = sorted_values[left] + sorted_values[right]
            if total == goal:
                break
            if total < goal:
                left += 1
            else:
                right -= 1
        require(left <= right, "SORTED_VALUE_SUM", f"exponent {goal} has no earlier pair in sorted sequence")
    require(sorted_values[-1] == TARGET, "SORTED_FINAL", "sorted last exponent is not n-2")
    return {
        "operations": len(rows), "squarings": squarings,
        "multiplications": multiplications, "all_rows_live": True,
        "earlier_declared_parents": True, "exact_integer_target": True,
        "index_register_replay": True, "sorted_value_sequence": True,
        "file_order_descent_rows_1_based": descents,
        "target_hex": format(TARGET, "x"),
    }


def modular_replay(obj, count=1024):
    # Fixed points plus deterministic hash-derived nonzero bases, reproducible
    # without PRNG-library version assumptions. These tests supplement exact proof.
    fixed = [1, 2, 3, 5, 7, 11, 17, 255, N//2, N-1]
    derived = [1 + int.from_bytes(hashlib.sha256(b"dot-chain284-replay-v1/" + i.to_bytes(4, "big")).digest(), "big") % (N-1)
               for i in range(count)]
    bases = fixed + derived
    for base in bases:
        residues = {1: base}
        for out, left, right in obj["rows"]:
            residues[out] = (residues[left] * residues[right]) % N
        actual = residues[TARGET]
        require(actual == pow(base, TARGET, N), "MODULAR_POW", f"modular exponent mismatch at base {base}")
        require(actual == pow(base, -1, N), "MODULAR_INVERSE", f"inverse mismatch at base {base}")
        require(actual * base % N == 1, "INVERSE_PRODUCT", f"inverse product mismatch at base {base}")
    return {"fixed_bases": len(fixed), "hash_derived_bases": count,
            "unique_bases": len(set(bases)), "nonzero_bases": len(bases),
            "modular_pow_inverse_product": "PASS"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--sha256", help="require exact raw-file digest before semantic replay")
    parser.add_argument("--modular", action="store_true", help="also test 10 fixed plus 1024 deterministic nonzero bases")
    args = parser.parse_args()
    try:
        raw = args.certificate.read_bytes()
        if args.sha256:
            digest_check(raw, args.sha256)
        obj = parse(raw)
        result = verify(obj)
        result.update(verdict="PASS_SCOPED", raw_bytes=len(raw), raw_sha256=hashlib.sha256(raw).hexdigest())
        if args.modular:
            result["modular_replay"] = modular_replay(obj)
    except (Rejected, OSError) as exc:
        print(json.dumps({"verdict": "FAIL", "reason": getattr(exc, "code", "IO"), "detail": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
