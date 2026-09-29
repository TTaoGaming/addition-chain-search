#!/usr/bin/env python3
"""Check the exact bytes and arithmetic of the selected P-384 scalar chains.

This checker reads certificates only. It does not import or run any search code.
"""

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ORDER = int(
    "ffffffffffffffffffffffffffffffffffffffffffffffff"
    "c7634d81f4372ddf581a0db248b0a77aecec196accc52973", 16
)
TARGET = ORDER - 2
ROW = re.compile(r"[1-9][0-9]* [1-9][0-9]* [1-9][0-9]*\Z")

# (relative path, operations, squarings, other multiplications, SHA-256)
CASES = (
    ("certificates/p384_425.txt", 425, 380, 45, "14da9fd3bfa7e3e615c78c5d6cf73dc0262ea3ff65eb29553be502de37f0df05"),
    ("certificates/p384_424.txt", 424, 380, 44, "88c3ff1cb882db81e8cee4d48a62c1ac41b7f57a1f52dfa5473242b1fc54b1be"),
    ("certificates/p384_423.txt", 423, 381, 42, "179c160b79f4c953b1d4822e6ce922213db26993c604c6c79544efdb4acdf6f2"),
    ("certificates/p384_422.txt", 422, 382, 40, "5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70"),
    ("certificates/p384_421.txt", 421, 380, 41, "844866b0703ef55ca41fc616a7226fe6d8aca3022ead18cdaec1e0911422e02e"),
    ("later_candidate/p384_421_381S40M.txt", 421, 381, 40, "0a8c5bb288aefb494e64dfa793e9e9b8ca1e162dcbc6c79ae6a6015ee089b518"),
)


def verify(raw: bytes, expected: tuple) -> dict:
    name, operations, expected_s, expected_m, expected_sha = expected
    if not raw or len(raw) > 200_000 or b"\r" in raw or not raw.endswith(b"\n"):
        raise ValueError(f"{name}: expected bounded ASCII with LF line endings")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha:
        raise ValueError(f"{name}: exact certificate SHA-256 mismatch")
    try:
        lines = raw.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError(f"{name}: non-ASCII certificate") from exc
    if len(lines) != operations:
        raise ValueError(f"{name}: expected {operations} rows, got {len(lines)}")

    seen = {1}
    rows = []
    squarings = 0
    previous = 1
    strictly_increasing = True
    for number, line in enumerate(lines, 1):
        if ROW.fullmatch(line) is None:
            raise ValueError(f"{name}: malformed row {number}")
        output, left, right = map(int, line.split(" "))
        if left not in seen or right not in seen:
            raise ValueError(f"{name}: missing prior parent at row {number}")
        if output != left + right or output in seen:
            raise ValueError(f"{name}: invalid or repeated sum at row {number}")
        if output <= previous:
            strictly_increasing = False
        seen.add(output)
        rows.append((output, left, right))
        squarings += left == right
        previous = output
    if rows[0] != (2, 1, 1) or rows[-1][0] != TARGET:
        raise ValueError(f"{name}: wrong start or target")
    multiplications = operations - squarings
    if (squarings, multiplications) != (expected_s, expected_m):
        raise ValueError(f"{name}: wrong operation counts")

    live = {TARGET}
    for output, left, right in reversed(rows):
        if output in live:
            live.update((left, right))
    unused_rows = sum(output not in live for output, _, _ in rows)
    if unused_rows:
        raise ValueError(f"{name}: {unused_rows} unused rows")

    for base in (2, 7, ORDER - 1):
        values = {1: base % ORDER}
        for output, left, right in rows:
            values[output] = values[left] * values[right] % ORDER
        if values[TARGET] != pow(base, TARGET, ORDER) or base * values[TARGET] % ORDER != 1:
            raise ValueError(f"{name}: modular replay failed for base {base}")
    return {
        "file": name,
        "sha256": digest,
        "operations": operations,
        "squarings": squarings,
        "other_multiplications": multiplications,
        "weighted_0_8S_plus_M": (4 * squarings + 5 * multiplications) / 5,
        "strictly_increasing": strictly_increasing,
        "unused_rows": unused_rows,
    }


def main() -> None:
    results = [verify((ROOT / case[0]).read_bytes(), case) for case in CASES]
    # A same-length, math-valid candidate must fail the frozen byte check.
    raw = (ROOT / CASES[3][0]).read_bytes()
    changed = raw.replace(b"3 2 1\n", b"3 1 2\n", 1)
    if changed == raw or len(changed) != len(raw):
        raise ValueError("failed to construct same-length mutation")
    try:
        verify(changed, CASES[3])
    except ValueError:
        mutation_rejected = True
    else:
        raise ValueError("mutated certificate was accepted")
    print(json.dumps({"status": "PASS_LOCAL_CERTIFICATE_REPLAY", "cases": results,
                      "same_math_byte_mutation_rejected": mutation_rejected}, sort_keys=True))


if __name__ == "__main__":
    main()
