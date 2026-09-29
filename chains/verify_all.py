#!/usr/bin/env python3
"""Run the frozen, local arithmetic checks in this release; no network access."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGETS = (
    ("p256", "candidate.json", "47c5dd4cd01aa5af55271e18ba9c85938348eb55cbddb6ff72acc521153c5a74", "456b0cca65cf82efb3b6ddce2926148cb72633d043e2451c42ad59c58bb8ec35", 291, 254, 37),
    ("p521", "candidate.json", "11ac48a8ec2fbc34b8be9a9c0d25c97c9450ea1d8f23f05aa4c7215ffdddeb7c", "c05538403e66df9e9ffbf6627ee2fa0e53d9e4a3cfccbe939527bd67fda879c6", 582, 519, 63),
    ("curve25519", "candidate.json", "014e8fa7513f19a135c76385f75544d655dc262985d9ab1ae5e4cf6eee4ec461", "832b72b0f03ca643607319ef44910618fc7fe9aad171f5f24df0290ea5c09fd8", 281, 249, 32),
    ("curve25519", "candidate_282.json", "014e8fa7513f19a135c76385f75544d655dc262985d9ab1ae5e4cf6eee4ec461", "1a889f6fea716915170f7b70be48d8fe92f733f113825cc94f41d8fec0c36359", 282, 250, 32),
    ("curve25519", "candidate_283.json", "014e8fa7513f19a135c76385f75544d655dc262985d9ab1ae5e4cf6eee4ec461", "e7395e8ecd817f7cd3fa7e599c80a0b67056175271e10ce45be714bdf3d660b7", 283, 250, 33),
    ("secp256k1", "candidate.json", "a7e65cbb8fd4e6b71c9bb35403e16d2fa22f1f6f0d68b83a984c1d393ffa7f01", "904518c4f165a168f0412164a23babe91b66d70820a0fad76686e5a84bf77e5a", 290, 253, 37),
)


def check_release_hashes() -> None:
    expected = {}
    for line in (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_./-]+)", line)
        if match is None or ".." in Path(match[2]).parts or match[2].startswith("/"):
            raise ValueError("invalid SHA256SUMS entry")
        if match[2] in expected:
            raise ValueError("duplicate SHA256SUMS entry")
        expected[match[2]] = match[1]
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS.txt"
        and path.relative_to(ROOT).parts[0] != ".git"
    }
    if actual != set(expected):
        raise ValueError("release file inventory differs from SHA256SUMS")
    for relative, digest in expected.items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
            raise ValueError(f"release hash mismatch: {relative}")


def run(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "-B", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"checker failed: {' '.join(args)}\n{completed.stderr}")
    return json.loads(completed.stdout)


def main() -> None:
    check_release_hashes()
    progression = run(str(ROOT / "p384/verify_progression.py"))
    if progression["status"] != "PASS_LOCAL_CERTIFICATE_REPLAY" or len(progression["cases"]) != 6:
        raise ValueError("P-384 progression result mismatch")
    if progression.get("same_math_byte_mutation_rejected") is not True:
        raise ValueError("P-384 byte mutation was not rejected")
    if [case.get("strictly_increasing") for case in progression["cases"]] != [False, True, True, True, True, True]:
        raise ValueError("P-384 chain shape mismatch")
    if any(case.get("unused_rows") != 0 for case in progression["cases"]):
        raise ValueError("P-384 liveness mismatch")
    frozen = run(str(ROOT / "p384/verify_frozen_421.py"), str(ROOT / "p384/certificates/p384_421.txt"))
    if frozen.get("valid") is not True or frozen.get("rejected_mutations") != [
        "wrong_sum", "missing_row", "wrong_target", "changed_bytes_same_math"
    ]:
        raise ValueError("frozen P-384 checker result mismatch")

    target_results = []
    for name, filename, manifest_sha, candidate_sha, rows, squares, multiplies in TARGETS:
        base = ROOT / "targets" / name
        result = run(
            str(ROOT / "targets/verify_dag.py"),
            "--manifest", str(base / "manifest.json"),
            "--manifest-sha256", manifest_sha,
            "--candidate", str(base / filename),
            "--candidate-sha256", candidate_sha,
        )
        if (result.get("verdict"), result.get("rows"), result.get("squarings"),
                result.get("multiplications"), result.get("effect_ceiling")) != (
                    "PASS_LOCAL_ARITHMETIC", rows, squares, multiplies,
                    "LOCAL_ARITHMETIC_ONLY"):
            raise ValueError(f"{name}: declared counts or ceiling mismatch")
        target_results.append(result)
    p521_variant = run(str(ROOT / "targets/p521/verify_variant.py"))
    if (p521_variant.get("status"), p521_variant.get("rows"),
            p521_variant.get("squarings"), p521_variant.get("multiplications"),
            p521_variant.get("terminal_mutation_rejected")) != (
                "PASS_LOCAL_ARITHMETIC_ONLY", 582, 518, 64, True):
        raise ValueError("P-521 variant mismatch")
    curve25519_frontier = run(str(ROOT / "targets/curve25519/frontier/verify.py"))
    if curve25519_frontier.get("verdict") != "PASS_LOCAL_ARITHMETIC_ONLY":
        raise ValueError("Curve25519 279/280 frontier verdict mismatch")
    frontier_cases = [
        (case.get("file"), case.get("sha256"), case.get("operations"),
         case.get("squarings"), case.get("other_multiplications"),
         case.get("mutation_rejected"))
        for case in curve25519_frontier.get("cases", [])
    ]
    if frontier_cases != [
        ("curve25519_scalar_279.json", "3948e3c1692f1d863aa2d7d37246217ed4a2328b5fbec034d8f5f8e6aa6cb0b1", 279, 247, 32, True),
        ("curve25519_scalar_280.json", "a3a1897b9eeb496cd4b8ac164b653e0c272afd16c8d4e6ad5ca9f402cfe9ca2a", 280, 249, 31, True),
    ]:
        raise ValueError("Curve25519 279/280 frontier case mismatch")
    field_curve448 = run(str(ROOT / "field/curve448/verify_field.py"))
    if (field_curve448.get("status"), field_curve448.get("target"),
            field_curve448.get("vectors_per_candidate")) != (
                "PASS_LOCAL_ARITHMETIC_ONLY", "Curve448 field p-2", 7):
        raise ValueError("Curve448 field assay mismatch")
    print(json.dumps({
        "status": "PASS_LOCAL_ARITHMETIC_ONLY",
        "p384_history": progression,
        "p384_frozen_421": frozen,
        "other_targets": target_results,
        "p521_variant": p521_variant,
        "curve25519_frontier": curve25519_frontier,
        "curve448_field_assay": field_curve448,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
