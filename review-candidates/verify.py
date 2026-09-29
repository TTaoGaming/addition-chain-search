#!/usr/bin/env python3
"""Read-only arithmetic replay of the three bundled scalar-chain certificates."""

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
P521_N = int(
    "1ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    "fa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409",
    16,
)
SECP256K1_N = int(
    "fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141", 16
)
FILES = {
    "p521_581_517S64M.json": "8f4701f3aa811d41606bda06cd1faf441243ed58f051a4e6305e7160c25d69cf",
    "p521_581_516S65M.json": "35e0862c40b159875aec071065a77f390d27114ade2c0b5a33578e0766963b2d",
    "secp256k1_288.json": "4f8fc44ad666a60717c4f9f0add36f7cc0156c3794dc76af66119054cef0f8f8",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_pinned(name):
    raw = (ROOT / "certificates" / name).read_bytes()
    require(len(raw) <= 500_000, "oversized certificate")
    require(hashlib.sha256(raw).hexdigest() == FILES[name], "certificate hash drift")
    return json.loads(raw)


def check_p521(cert):
    require(type(cert) is dict and set(cert) == {"target", "modulus", "rows"}, "P-521 shape")
    require(type(cert["target"]) is str and cert["target"].isdigit(), "P-521 target encoding")
    require(type(cert["modulus"]) is str and cert["modulus"].isdigit(), "P-521 order encoding")
    require(int(cert["modulus"]) == P521_N, "P-521 scalar order mismatch")
    require(int(cert["target"]) == P521_N - 2, "P-521 scalar target mismatch")
    rows = cert["rows"]
    require(type(rows) is list and 0 < len(rows) <= 1_000, "P-521 row count")
    seen = {1}
    parents = {}
    previous = 1
    squares = multiplies = 0
    powers = {base: {1: base % P521_N} for base in (2, 3, 5, 42, P521_N - 1)}
    for row in rows:
        require(type(row) is list and len(row) == 4, "P-521 row shape")
        value, left, right, kind = row
        require(all(type(x) is int for x in (value, left, right)) and kind == "chain", "P-521 row type")
        require(left in seen and right in seen and value == left + right, "P-521 parent sum")
        require(value > previous and value <= P521_N - 2, "P-521 row order")
        seen.add(value)
        parents[value] = (left, right)
        previous = value
        squares += left == right
        multiplies += left != right
        for vals in powers.values():
            vals[value] = vals[left] * vals[right] % P521_N
    require(previous == P521_N - 2, "P-521 terminal")
    needed = {1}
    pending = [P521_N - 2]
    while pending:
        value = pending.pop()
        if value in needed:
            continue
        needed.add(value)
        pending.extend(parents[value])
    require(needed == seen, "P-521 dead row")
    for base, vals in powers.items():
        require(vals[P521_N - 2] == pow(base, P521_N - 2, P521_N), "P-521 modular replay")
        require(vals[P521_N - 2] * base % P521_N == 1, "P-521 inversion replay")
    return len(rows), squares, multiplies


def check_secp256k1(cert):
    require(type(cert) is dict and set(cert) == {"target_hex", "steps"}, "secp256k1 shape")
    require(cert["target_hex"] == format(SECP256K1_N - 2, "x"), "secp256k1 scalar target")
    steps = cert["steps"]
    require(type(steps) is list and 0 < len(steps) <= 1_000, "secp256k1 step count")
    values = [1]
    powers = {base: [base % SECP256K1_N] for base in (2, 3, 5, 42, SECP256K1_N - 1)}
    squares = multiplies = 0
    for pair in steps:
        require(type(pair) is list and len(pair) == 2, "secp256k1 step shape")
        left, right = pair
        require(type(left) is int and type(right) is int, "secp256k1 parent type")
        require(0 <= left < len(values) and 0 <= right < len(values), "secp256k1 forward parent")
        value = values[left] + values[right]
        require(values[-1] < value <= SECP256K1_N - 2, "secp256k1 sum/order")
        values.append(value)
        squares += left == right
        multiplies += left != right
        for vals in powers.values():
            vals.append(vals[left] * vals[right] % SECP256K1_N)
    require(values[-1] == SECP256K1_N - 2, "secp256k1 terminal")
    needed = {0}
    pending = [len(steps)]
    while pending:
        index = pending.pop()
        if index in needed:
            continue
        needed.add(index)
        pending.extend(steps[index - 1])
    require(len(needed) == len(values), "secp256k1 dead step")
    for base, vals in powers.items():
        require(vals[-1] == pow(base, SECP256K1_N - 2, SECP256K1_N), "secp256k1 modular replay")
        require(vals[-1] * base % SECP256K1_N == 1, "secp256k1 inversion replay")
    return len(steps), squares, multiplies


def rejects(checker, damaged):
    try:
        checker(damaged)
    except (ValueError, KeyError, IndexError):
        return True
    return False


def main():
    expected = {
        "p521_581_517S64M.json": (581, 517, 64),
        "p521_581_516S65M.json": (581, 516, 65),
        "secp256k1_288.json": (288, 253, 35),
    }
    for name, count in expected.items():
        cert = load_pinned(name)
        checker = check_secp256k1 if name.startswith("secp") else check_p521
        actual = checker(cert)
        require(actual == count, "unexpected operation count")
        bad_target = copy.deepcopy(cert)
        if checker is check_p521:
            bad_target["target"] = str(P521_N - 3)
        else:
            bad_target["target_hex"] = format(SECP256K1_N - 3, "x")
        require(rejects(checker, bad_target), "wrong-target mutation accepted")
        bad_parent = copy.deepcopy(cert)
        if checker is check_p521:
            bad_parent["rows"][-1][1] = 0
        else:
            bad_parent["steps"][-1][0] = len(cert["steps"]) + 1
        require(rejects(checker, bad_parent), "bad-parent mutation accepted")
        print(f"PASS {name} operations={actual[0]} S={actual[1]} M={actual[2]} mutants_rejected=2")
    print("PASS_LOCAL_ARITHMETIC_ONLY")


if __name__ == "__main__":
    main()
