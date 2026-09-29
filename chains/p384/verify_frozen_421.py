#!/usr/bin/env python3
"""Check the frozen P-384 scalar-inversion chain with Python's standard library."""

import hashlib
import json
import re
import sys
from pathlib import Path

N = 39402006196394479212279040100143613805079739270465446667946905279627659399113263569398956308152294913554433653942643
SHA256 = "844866b0703ef55ca41fc616a7226fe6d8aca3022ead18cdaec1e0911422e02e"
ROW = re.compile(r"[1-9][0-9]* [1-9][0-9]* [1-9][0-9]*\Z")


def check(raw: bytes, *, exact_bytes: bool) -> dict:
    if not raw or len(raw) > 200_000 or not raw.endswith(b"\n") or b"\r" in raw:
        raise ValueError("certificate must be bounded ASCII with LF line endings")
    try:
        lines = raw.decode("ascii").split("\n")[:-1]
    except UnicodeError as exc:
        raise ValueError("certificate is not ASCII") from exc
    if len(lines) != 421:
        raise ValueError(f"expected 421 operations; got {len(lines)}")

    known = {1}
    previous = 1
    steps = []
    squarings = 0
    for number, line in enumerate(lines, 1):
        if not ROW.fullmatch(line):
            raise ValueError(f"invalid row syntax at {number}")
        output, left, right = map(int, line.split(" "))
        if left not in known or right not in known:
            raise ValueError(f"parent not previously available at {number}")
        if output != left + right or output <= previous:
            raise ValueError(f"invalid or unordered sum at {number}")
        known.add(output)
        previous = output
        steps.append((output, left, right))
        squarings += left == right

    if previous != N - 2:
        raise ValueError("terminal exponent is not P-384 subgroup order minus two")
    multiplications = len(steps) - squarings
    if (squarings, multiplications) != (380, 41):
        raise ValueError("operation counts are not 380S + 41M")

    digest = hashlib.sha256(raw).hexdigest()
    if exact_bytes and digest != SHA256:
        raise ValueError("frozen certificate SHA-256 mismatch")

    # Re-evaluate the same dependency graph in modular arithmetic, then
    # compare to Python's independent modular exponentiation implementation.
    for base in (2, 3, 5, 17):
        values = {1: base}
        for output, left, right in steps:
            values[output] = values[left] * values[right] % N
        if values[previous] != pow(base, N - 2, N) or base * values[previous] % N != 1:
            raise ValueError(f"modular inversion check failed for base {base}")

    return {
        "sha256": digest,
        "operations": len(steps),
        "squarings": squarings,
        "other_multiplications": multiplications,
        "weighted_0_8S_plus_M": "345.0",
        "target_hex": hex(previous),
        "modular_bases": [2, 3, 5, 17],
    }


def negative_controls(raw: bytes) -> list[str]:
    lines = raw.splitlines(keepends=True)
    controls = {}
    bad_sum = lines.copy()
    parts = bad_sum[199].decode("ascii").split()
    parts[0] = str(int(parts[0]) + 1)
    bad_sum[199] = (" ".join(parts) + "\n").encode("ascii")
    controls["wrong_sum"] = (b"".join(bad_sum), False)
    controls["missing_row"] = (b"".join(lines[:199] + lines[200:]), False)
    wrong_target = lines.copy()
    parts = wrong_target[-1].decode("ascii").split()
    parts[0] = str(int(parts[0]) + 1)
    wrong_target[-1] = (" ".join(parts) + "\n").encode("ascii")
    controls["wrong_target"] = (b"".join(wrong_target), False)
    same_math = lines.copy()
    parts = same_math[7].decode("ascii").split()
    same_math[7] = f"{parts[0]} {parts[2]} {parts[1]}\n".encode("ascii")
    controls["changed_bytes_same_math"] = (b"".join(same_math), True)
    for name, (mutant, exact_bytes) in controls.items():
        try:
            check(mutant, exact_bytes=exact_bytes)
        except ValueError:
            continue
        raise ValueError(f"negative control accepted: {name}")
    return list(controls)


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).parent / "certificates" / "p384_421.txt"
    if len(sys.argv) > 2:
        raise ValueError("usage: python -B p384/verify_frozen_421.py [certificate path]")
    raw = path.read_bytes()
    result = check(raw, exact_bytes=True)
    result["rejected_mutations"] = negative_controls(raw)
    result["valid"] = True
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1) from None
