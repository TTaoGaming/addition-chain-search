#!/usr/bin/env python3
"""Read-only, search-independent replay of two fixed Curve25519 scalar DAGs."""

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ORDER = (1 << 252) + 27742317777372353535851937790883648493
TARGET = ORDER - 2
CASES = {
    "curve25519_scalar_279.json": (
        "3948e3c1692f1d863aa2d7d37246217ed4a2328b5fbec034d8f5f8e6aa6cb0b1",
        "e653c99395b406db0461513090024cd0819e5c0a423b237d369f7ebd4ccc0883",
        (279, 247, 32),
    ),
    "curve25519_scalar_280.json": (
        "a3a1897b9eeb496cd4b8ac164b653e0c272afd16c8d4e6ad5ca9f402cfe9ca2a",
        "69576686cf4c14dcd0b811fab610dbb2b764fd3e497ac48e0cfb343be930157f",
        (280, 249, 31),
    ),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def replay(cert, expected_plan, expected_counts):
    require(cert["source_plan_sha256"] == expected_plan, "plan binding")
    require(int(cert["target_hex"], 16) == TARGET, "target exponent")
    ops = cert["operations"]
    require(len(ops) == cert["operation_count"], "row count")
    exponents = [1]
    parents = [()]
    squares = multiplies = 0
    accumulating = False
    precompute_count = 0
    for row in ops:
        require(set(row) == {"left", "right", "phase"}, "row shape")
        a, b = row["left"], row["right"]
        require(type(a) is int and type(b) is int, "parent type")
        require(0 <= a < len(exponents) and 0 <= b < len(exponents), "parent index")
        require(row["phase"] in ("precompute", "accumulate"), "phase")
        if row["phase"] == "accumulate":
            accumulating = True
        else:
            require(not accumulating, "phase order")
            precompute_count += 1
        exponents.append(exponents[a] + exponents[b])
        require(exponents[-1] > exponents[-2], "nonincreasing chain")
        parents.append((a, b))
        squares += a == b
        multiplies += a != b
    require(exponents[-1] == TARGET, "terminal exponent")
    require(cert["precompute_values"] == exponents[:precompute_count + 1], "precompute metadata")
    first = cert["first_window"]
    require(first["exponent"] in cert["precompute_values"] and first["bits"] == first["exponent"].bit_length(), "first-window metadata")
    require((len(ops), squares, multiplies) == expected_counts, "declared cost")
    require((squares, multiplies) == (cert["squarings"], cert["multiplications"]), "certificate cost")
    live = {len(exponents) - 1}
    for i in range(len(exponents) - 1, 0, -1):
        if i in live:
            live.update(parents[i])
    require(len(live) == len(exponents), "dead operation")
    for base in (2, 3, 5, 7, 11, ORDER - 1):
        values = [base % ORDER]
        for row in ops:
            values.append(values[row["left"]] * values[row["right"]] % ORDER)
        require(values[-1] == pow(base, TARGET, ORDER), "modular replay")
        require(values[-1] * base % ORDER == 1, "inverse identity")
    return {"operations": len(ops), "squarings": squares, "other_multiplications": multiplies}


def main():
    results = []
    for filename, (expected_sha, plan_sha, counts) in CASES.items():
        raw = (ROOT / filename).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected_sha, "certificate bytes")
        cert = json.loads(raw)
        result = replay(cert, plan_sha, counts)
        broken = copy.deepcopy(cert)
        broken["operations"][-1]["left"] = 0
        try:
            replay(broken, plan_sha, counts)
        except ValueError:
            pass
        else:
            raise ValueError("corruption not rejected")
        results.append({"file": filename, "sha256": expected_sha, **result, "mutation_rejected": True})
    print(json.dumps({"verdict": "PASS_LOCAL_ARITHMETIC_ONLY", "target": "Curve25519 subgroup scalar l-2", "cases": results}, sort_keys=True))


if __name__ == "__main__":
    main()
