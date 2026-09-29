#!/usr/bin/env python3
"""Independently replay the retained P-521 518S+64M source DAG."""

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ORDER = int(json.loads((ROOT / "manifest.json").read_text())["order_hex"], 16)
TARGET = ORDER - 2


def check(candidate):
    if candidate.get("schema") != "hfo.addition_chain_dag.v0":
        raise ValueError("schema")
    if int(candidate["n_hex"], 16) != ORDER or int(candidate["target_hex"], 16) != TARGET:
        raise ValueError("target")
    rows = candidate.get("rows")
    if not isinstance(rows, list) or len(rows) > 2000:
        raise ValueError("row count")
    parents = {1: None}
    squares = multiplies = 0
    for row in rows:
        if not isinstance(row, list) or len(row) != 3 or any(type(x) is not int for x in row):
            raise ValueError("row shape")
        value, left, right = row
        if value in parents or left not in parents or right not in parents or value != left + right:
            raise ValueError("invalid earlier-parent sum")
        if value <= max(parents):
            raise ValueError("nonmonotone row")
        parents[value] = (left, right)
        squares += left == right
        multiplies += left != right
    if rows[-1][0] != TARGET:
        raise ValueError("wrong terminal")
    needed = {TARGET}
    pending = [TARGET]
    while pending:
        value = pending.pop()
        if value == 1:
            continue
        for parent in parents[value]:
            if parent not in needed:
                needed.add(parent)
                pending.append(parent)
    if len(needed) != len(parents):
        raise ValueError("dead rows")
    for base in (2, 3, 5, 42, ORDER - 1):
        vals = {1: base}
        for value, left, right in rows:
            vals[value] = vals[left] * vals[right] % ORDER
        if vals[TARGET] != pow(base, TARGET, ORDER):
            raise ValueError("modular replay")
    return {"status": "PASS_LOCAL_ARITHMETIC_ONLY", "rows": len(rows),
            "squarings": squares, "multiplications": multiplies}


if __name__ == "__main__":
    candidate = json.loads((ROOT / "candidate_518S64M_source.json").read_text())
    result = check(candidate)
    if (result["rows"], result["squarings"], result["multiplications"]) != (582, 518, 64):
        raise ValueError("unexpected P-521 counts")
    damaged = copy.deepcopy(candidate)
    damaged["rows"][-1][0] += 1
    try:
        check(damaged)
    except ValueError:
        result["terminal_mutation_rejected"] = True
    else:
        raise ValueError("terminal mutation accepted")
    print(json.dumps(result, sort_keys=True))
