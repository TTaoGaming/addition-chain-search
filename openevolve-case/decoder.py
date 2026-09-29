"""Trusted compiler for a compact, data-only P-384 scalar addition-chain genome.

The genome selects four small helper exponents. It never supplies Python code
or the 421-row certificate. All arithmetic and tail optimization live here.
"""

from __future__ import annotations

from array import array
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path


SCHEMA = "p384.scalar.microdict.v1"
ORDER = int(
    "ffffffffffffffffffffffffffffffffffffffffffffffff"
    "c7634d81f4372ddf581a0db248b0a77aecec196accc52973", 16
)
TARGET = ORDER - 2
ANCHOR_BITS = 192
ANCHOR = (1 << ANCHOR_BITS) - 1
LOW = TARGET - (ANCHOR << ANCHOR_BITS)
assert TARGET >> ANCHOR_BITS == ANCHOR and 0 <= LOW < (1 << ANCHOR_BITS)

MAX_GENOME_BYTES = 512
MAX_RANK = 255
MAX_ROWS = 512
INF = 10_000
BASES = (2, 3, 5, 7, 11, ORDER - 1)
BASELINE = (0, (30, 35, 29, 35))


class GenomeError(ValueError):
    """A candidate fails the bounded data or arithmetic contract."""


@dataclass(frozen=True)
class Genome:
    bridge: int
    ranks: tuple[int, int, int, int]


@dataclass(frozen=True)
class Result:
    genome: Genome
    helpers: tuple[int, int, int, int]
    prefix_rows: int
    tail_additions: int
    rows: tuple[tuple[int, int, int], ...]
    squarings: int
    multiplications: int
    certificate: bytes

    @property
    def operations(self) -> int:
        return len(self.rows)

    @property
    def weight5(self) -> int:
        return 4 * self.squarings + 5 * self.multiplications

    @property
    def certificate_sha256(self) -> str:
        return hashlib.sha256(self.certificate).hexdigest()


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise GenomeError("duplicate JSON key")
        result[key] = value
    return result


def _reject_number(_value: str) -> None:
    raise GenomeError("only JSON integers are allowed")


def parse_genome(raw: bytes) -> Genome:
    if len(raw) > MAX_GENOME_BYTES:
        raise GenomeError("genome byte cap")
    try:
        item = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_unique_object,
            parse_float=_reject_number,
            parse_constant=_reject_number,
        )
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise GenomeError("invalid strict JSON") from exc
    if type(item) is not dict or set(item) != {"schema", "bridge", "ranks"}:
        raise GenomeError("genome object shape")
    if item["schema"] != SCHEMA:
        raise GenomeError("genome schema")
    bridge = item["bridge"]
    ranks = item["ranks"]
    if type(bridge) is not int or bridge not in (0, 1):
        raise GenomeError("bridge must be 0 or 1")
    if (type(ranks) is not list or len(ranks) != 4 or
            any(type(rank) is not int or not 0 <= rank <= MAX_RANK for rank in ranks)):
        raise GenomeError("four bounded integer ranks required")
    return Genome(bridge, tuple(ranks))


def genome_bytes(genome: Genome) -> bytes:
    return json.dumps(
        {"schema": SCHEMA, "bridge": genome.bridge, "ranks": list(genome.ranks)},
        separators=(",", ":"), ensure_ascii=True,
    ).encode("ascii") + b"\n"


def _core(bridge: int) -> dict[int, tuple[int, int]]:
    """Fifteen fixed, admissible rows for 2^12-1, with one mutable bridge."""
    rows = {
        2: (1, 1), 3: (2, 1), 6: (3, 3), 12: (6, 6),
        24: (12, 12), 48: (24, 24), 96: (48, 48),
    }
    if bridge == 0:
        rows[192] = (96, 96)
        rows[195] = (192, 3)
    else:
        rows[99] = (96, 3)
        rows[195] = (99, 96)
    rows.update({
        390: (195, 195), 585: (390, 195), 1170: (585, 585),
        1755: (1170, 585), 2925: (1755, 1170), 4095: (2925, 1170),
    })
    return rows


def _pair_sums(values: set[int]) -> dict[int, tuple[int, int]]:
    """Distinct sums with a deterministic parent pair for each output."""
    result: dict[int, tuple[int, int]] = {}
    ordered = sorted(values)
    for i, a in enumerate(ordered):
        for b in ordered[i:]:
            h = a + b
            if h >= 4095 or h in values:
                continue
            pair = (a, b)
            old = result.get(h)
            if old is None or (a != b, pair) < (old[0] != old[1], old):
                result[h] = pair
    return result


def _prefix(genome: Genome) -> tuple[list[tuple[int, int, int]], tuple[int, int, int, int]]:
    core = _core(genome.bridge)
    core_values = {1, *core}
    core_only = sorted(_pair_sums(core_values))
    values = set(core_values)
    aux: dict[int, tuple[int, int]] = {}
    last = 0
    for slot, rank in enumerate(genome.ranks):
        available = _pair_sums(values)
        remaining = 3 - slot
        choices = [h for h in sorted(available) if h > last and
                   sum(z > h for z in core_only) >= remaining]
        if not choices:
            raise GenomeError("helper grammar exhausted")
        h = choices[rank % len(choices)]
        aux[h] = available[h]
        values.add(h)
        last = h
    rows = [(h, *(core | aux)[h]) for h in sorted(core | aux)]
    _validate_rows(rows, expected=4095, require_live=False)
    return rows, tuple(sorted(aux))  # type: ignore[return-value]


def _tail_digits(prefix: list[tuple[int, int, int]]) -> tuple[list[int], int]:
    """Exact min-add carry DP for LOW = sum(d[p] * 2^p), d[p] in prefix."""
    digits = sorted({0, 1, *(h for h, _, _ in prefix)})
    even = [d for d in digits if d & 1 == 0]
    odd = [d for d in digits if d & 1]
    costs = array("H", [INF]) * 4096
    costs[0] = 0
    back_q: list[array] = []
    back_digit: list[array] = []
    for p in range(ANCHOR_BITS):
        bit = (LOW >> p) & 1
        next_costs = array("H", [INF]) * 4096
        parents = array("H", [0]) * 4096
        selected = array("H", [0]) * 4096
        for q, old_cost in enumerate(costs):
            if old_cost == INF:
                continue
            for digit in odd if (bit - q) & 1 else even:
                numerator = q + digit - bit
                if numerator < 0:
                    continue
                q2 = numerator >> 1
                new_cost = old_cost + (digit != 0)
                if new_cost < next_costs[q2]:
                    next_costs[q2] = new_cost
                    parents[q2] = q
                    selected[q2] = digit
        costs = next_costs
        back_q.append(parents)
        back_digit.append(selected)
    minimum = costs[0]
    if minimum == INF:
        raise GenomeError("tail representation missing")
    choices = [0] * ANCHOR_BITS
    q = 0
    for p in range(ANCHOR_BITS - 1, -1, -1):
        choices[p] = back_digit[p][q]
        q = back_q[p][q]
    if q != 0 or sum(d << p for p, d in enumerate(choices)) != LOW:
        raise GenomeError("tail traceback mismatch")
    return choices, minimum


def _prune_dead(rows: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    needed = {TARGET}
    kept: list[tuple[int, int, int]] = []
    for row in reversed(rows):
        h, a, b = row
        if h in needed:
            kept.append(row)
            needed.update((a, b))
    kept.reverse()
    return kept


def _validate_rows(rows: list[tuple[int, int, int]], *, expected: int,
                   require_live: bool) -> tuple[int, int]:
    if not 1 <= len(rows) <= MAX_ROWS:
        raise GenomeError("row count")
    known = {1}
    previous = 1
    squares = multiples = 0
    for h, a, b in rows:
        if h <= previous or h != a + b or a not in known or b not in known:
            raise GenomeError("invalid addition DAG")
        known.add(h)
        previous = h
        squares += a == b
        multiples += a != b
    if previous != expected:
        raise GenomeError("wrong terminal exponent")
    if require_live:
        needed = {expected}
        for h, a, b in reversed(rows):
            if h not in needed:
                raise GenomeError("dead row")
            needed.update((a, b))
    return squares, multiples


@lru_cache(maxsize=512)
def compile_genome(genome: Genome) -> Result:
    prefix, helpers = _prefix(genome)
    choices, tail_additions = _tail_digits(prefix)
    rows = prefix.copy()
    current = 4095
    width = 12
    for _ in range(4):
        old_anchor = current
        for _ in range(width):
            doubled = current + current
            rows.append((doubled, current, current))
            current = doubled
        next_anchor = current + old_anchor
        rows.append((next_anchor, current, old_anchor))
        current = next_anchor
        width *= 2
    if current != ANCHOR:
        raise GenomeError("anchor construction")
    for p in range(ANCHOR_BITS - 1, -1, -1):
        doubled = current + current
        rows.append((doubled, current, current))
        current = doubled
        digit = choices[p]
        if digit:
            next_value = current + digit
            rows.append((next_value, current, digit))
            current = next_value
    rows = _prune_dead(rows)
    squares, multiples = _validate_rows(rows, expected=TARGET, require_live=True)
    if squares + multiples != len(rows):
        raise GenomeError("count mismatch")
    for base in BASES:
        powers = {1: base % ORDER}
        for h, a, b in rows:
            powers[h] = powers[a] * powers[b] % ORDER
        if powers[TARGET] != pow(base, TARGET, ORDER):
            raise GenomeError("modular replay")
    certificate = b"".join(f"{h} {a} {b}\n".encode("ascii") for h, a, b in rows)
    live_prefix_rows = sum(h <= 4095 for h, _, _ in rows)
    return Result(genome, helpers, live_prefix_rows, tail_additions, tuple(rows),
                  squares, multiples, certificate)


def from_bytes(raw: bytes) -> Result:
    genome = parse_genome(raw)
    result = compile_genome(genome)
    if (genome.bridge, genome.ranks) != BASELINE:
        baseline = compile_genome(Genome(*BASELINE))
        if result.certificate == baseline.certificate:
            raise GenomeError("no-op phenotype")
    return result


def from_path(path: str | Path) -> Result:
    with open(path, "rb") as source:
        raw = source.read(MAX_GENOME_BYTES + 1)
    return from_bytes(raw)
