#!/usr/bin/env python3
"""Read-only replay of the Curve448 field baseline and two declared splits."""

import copy
import json
from pathlib import Path

from checker import P, TARGET, parse
from r2.checker import Q, check
from r2.replay import candidate


ROOT = Path(__file__).resolve().parent
VECTORS = json.loads((ROOT / "vectors.json").read_text())["vectors"]


def evaluate(candidate, x):
    values = {"x": x}
    for row in candidate["rows"]:
        left, right = row["args"]
        if row["op"] == "S":
            values[row["name"]] = pow(values[left], 1 << right, P)
        elif row["op"] == "M":
            values[row["name"]] = values[left] * values[right] % P
        else:
            raise ValueError("unsupported operation")
    return values[candidate["terminal"]]


def check_vectors(candidate, exponent):
    for vector in VECTORS:
        x, inverse = int(vector["x"]), int(vector["inverse"])
        if (not 1 <= x < P or evaluate(candidate, x) != inverse
                or pow(x, exponent, P) != inverse or x * inverse % P != 1):
            raise ValueError("field vector")


def main():
    baseline = json.loads((ROOT / "baseline.json").read_text())
    exponent, squares, multiplies, _ = parse(baseline)
    if (exponent, squares, multiplies) != (TARGET, 447, 13):
        raise ValueError("baseline")
    check_vectors(baseline, exponent)
    bad = copy.deepcopy(baseline)
    bad["rows"][0]["args"][0] = "missing"
    try:
        parse(bad)
    except ValueError:
        pass
    else:
        raise ValueError("bad-row mutation accepted")
    bad = copy.deepcopy(baseline)
    bad["terminal"] = "x"
    if parse(bad)[0] == TARGET:
        raise ValueError("bad-terminal mutation accepted")

    splits = []
    for k, expected in ((223, (447, 13)), (224, (448, 14))):
        split_candidate = candidate(k)
        exp, sq, mul, values = check(split_candidate)
        if exp != TARGET or values["q"] != Q or (sq, mul) != expected:
            raise ValueError("split replay")
        check_vectors(split_candidate, exp)
        splits.append({"k": k, "squarings": sq, "multiplications": mul})
    return {"status": "PASS_LOCAL_ARITHMETIC_ONLY", "target": "Curve448 field p-2",
            "baseline": {"squarings": squares, "multiplications": multiplies},
            "splits": splits, "vectors_per_candidate": len(VECTORS)}


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True))
