"""Seed-independent replay of a decimal P-384 scalar n-2 certificate.

This module deliberately does not import the genome compiler or evaluator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ORDER = int(
    "ffffffffffffffffffffffffffffffffffffffffffffffff"
    "c7634d81f4372ddf581a0db248b0a77aecec196accc52973", 16
)
TARGET = ORDER - 2
BASES = (2, 3, 5, 7, 17, ORDER - 1)
MAX_BYTES = 160_000
MAX_ROWS = 512


def replay(raw: bytes) -> dict[str, object]:
    if not 0 < len(raw) <= MAX_BYTES or not raw.endswith(b"\n"):
        raise ValueError("certificate size or terminator")
    lines = raw.decode("ascii").splitlines()
    if not 1 <= len(lines) <= MAX_ROWS:
        raise ValueError("certificate row count")
    rows: list[tuple[int, int, int]] = []
    known = {1}
    previous = 1
    squares = 0
    for line in lines:
        fields = line.split()
        if len(fields) != 3 or any(not part.isdecimal() for part in fields):
            raise ValueError("certificate row syntax")
        h, a, b = (int(part) for part in fields)
        if h <= previous or h != a + b or a not in known or b not in known:
            raise ValueError("certificate arithmetic or dependency")
        rows.append((h, a, b))
        known.add(h)
        previous = h
        squares += a == b
    if previous != TARGET:
        raise ValueError("wrong scalar n-2 target")
    needed = {TARGET}
    for h, a, b in reversed(rows):
        if h not in needed:
            raise ValueError("dead certificate row")
        needed.update((a, b))
    for base in BASES:
        values = {1: base % ORDER}
        for h, a, b in rows:
            values[h] = values[a] * values[b] % ORDER
        oracle = pow(base, TARGET, ORDER)
        if values[TARGET] != oracle or values[TARGET] * base % ORDER != 1:
            raise ValueError("modular replay mismatch")
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "operations": len(rows),
        "squarings": squares,
        "multiplications": len(rows) - squares,
        "weight5": 4 * squares + 5 * (len(rows) - squares),
        "bases": [format(base, "x") for base in BASES],
        "status": "PASS_LOCAL_INDEPENDENT_REPLAY",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    with open(args.certificate, "rb") as source:
        raw = source.read(MAX_BYTES + 1)
    print(json.dumps(replay(raw), sort_keys=True))


if __name__ == "__main__":
    main()
