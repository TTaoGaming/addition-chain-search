"""Read-only offline calibration and 100 distinct one-gene mutation assays."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

from decoder import Genome, GenomeError, compile_genome, from_bytes, genome_bytes
from independent_verify import replay


ROOT = Path(__file__).resolve().parent
BASELINE = Genome(0, (30, 35, 29, 35))
LAB_VARIANT = Genome(1, (34, 30, 29, 35))


def rejected(raw: bytes) -> bool:
    try:
        from_bytes(raw)
    except GenomeError:
        return True
    return False


def main() -> None:
    seed = (ROOT / "seed.json").read_bytes()
    if seed != genome_bytes(BASELINE):
        raise AssertionError("seed bytes are not canonical")
    base = from_bytes(seed)
    lab = compile_genome(LAB_VARIANT)
    for name, result, expected in (
        ("portable", base, (421, 381, 40, 26)),
        ("lab", lab, (421, 380, 41, 26)),
    ):
        observed = (result.operations, result.squarings,
                    result.multiplications, result.tail_additions)
        if observed != expected:
            raise AssertionError(f"{name} calibration: {observed} != {expected}")
        if result.helpers != (197, 609, 1756, 3122):
            raise AssertionError(f"{name} helper calibration")
        check = replay(result.certificate)
        if check["operations"] != result.operations or check["weight5"] != result.weight5:
            raise AssertionError(f"{name} independent replay mismatch")

    # Mutate exactly one rank relative to the portable seed. Values are sampled
    # in round-robin order; aliases and repeated certificates are not counted.
    accepted: list[dict[str, object]] = []
    cert_hashes: set[str] = {base.certificate_sha256}
    attempted = 0
    no_op_rejections = 0
    duplicate_certificates = 0
    for value in range(256):
        for slot in range(4):
            if value == BASELINE.ranks[slot]:
                continue
            changed = list(BASELINE.ranks)
            changed[slot] = value
            candidate = Genome(BASELINE.bridge, tuple(changed))
            attempted += 1
            try:
                result = from_bytes(genome_bytes(candidate))
            except GenomeError as exc:
                if str(exc) != "no-op phenotype":
                    raise
                no_op_rejections += 1
                continue
            if result.certificate_sha256 in cert_hashes:
                duplicate_certificates += 1
                continue
            check = replay(result.certificate)
            if (check["sha256"] != result.certificate_sha256 or
                    check["operations"] != result.operations or
                    check["weight5"] != result.weight5):
                raise AssertionError("mutant independent replay mismatch")
            cert_hashes.add(result.certificate_sha256)
            accepted.append({
                "slot": slot, "rank": value, "operations": result.operations,
                "squarings": result.squarings,
                "multiplications": result.multiplications,
                "certificate_sha256": result.certificate_sha256,
            })
            if len(accepted) == 100:
                break
        if len(accepted) == 100:
            break
    if len(accepted) != 100:
        raise AssertionError("fewer than 100 distinct valid one-gene mutations")
    levels = Counter(str(item["operations"]) for item in accepted)
    if len(levels) < 3:
        raise AssertionError("insufficient operation-score diversity")

    bad_json = [
        b'{"schema":"p384.scalar.microdict.v1","bridge":0,"bridge":1,"ranks":[30,35,29,35]}',
        b'{"schema":"p384.scalar.microdict.v1","bridge":true,"ranks":[30,35,29,35]}',
        b'{"schema":"p384.scalar.microdict.v1","bridge":0,"ranks":[30.0,35,29,35]}',
        b'{"schema":"p384.scalar.microdict.v1","bridge":0,"ranks":[30,35,29,35],"code":"x"}',
        b'{"schema":"p384.scalar.microdict.v1","bridge":0,"ranks":[256,35,29,35]}',
        b'{"schema":"p384.scalar.microdict.v1","bridge":0,"ranks":[30,35,29]}',
        b"x" * 513,
    ]
    if not all(rejected(raw) for raw in bad_json):
        raise AssertionError("bad genome accepted")

    # A different rank encoding that selects the same first helper must not
    # pass as an evolutionary change. The initial seed itself remains valid.
    alias = Genome(0, (BASELINE.ranks[0] + 95, *BASELINE.ranks[1:]))
    if not rejected(genome_bytes(alias)):
        raise AssertionError("no-op alias accepted")
    lines = base.certificate.splitlines()
    fields = lines[-1].split()
    fields[0] = str(int(fields[0]) + 2).encode("ascii")
    lines[-1] = b" ".join(fields)
    try:
        replay(b"\n".join(lines) + b"\n")
    except ValueError:
        mutation_rejected = True
    else:
        raise AssertionError("independent verifier accepted tampered terminal")

    output = {
        "status": "PASS_OFFLINE_GENOTYPE_FEASIBILITY",
        "seed_sha256": hashlib.sha256(seed).hexdigest(),
        "seed_certificate_sha256": base.certificate_sha256,
        "seed_operations": base.operations,
        "seed_squarings": base.squarings,
        "seed_multiplications": base.multiplications,
        "seed_tail_additions": base.tail_additions,
        "lab_certificate_sha256": lab.certificate_sha256,
        "one_gene_attempts": attempted,
        "one_gene_distinct_valid_certificates": len(accepted),
        "one_gene_no_op_rejections": no_op_rejections,
        "one_gene_duplicate_certificates_skipped": duplicate_certificates,
        "one_gene_operations_histogram": dict(sorted(levels.items())),
        "best_one_gene_operations": min(item["operations"] for item in accepted),
        "bad_genomes_rejected": len(bad_json),
        "alias_rejected": True,
        "tampered_terminal_rejected": mutation_rejected,
        "evidence_ceiling": "Local deterministic generated-chain and independent replay only; no model candidate, native speed, or public acceptance.",
    }
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
