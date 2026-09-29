"""OpenEvolve evaluator ABI for a bounded JSON genome, never candidate code."""

from __future__ import annotations

from decoder import GenomeError, MAX_ROWS, from_path


def evaluate(program_path: str) -> dict[str, float]:
    try:
        result = from_path(program_path)
    except (GenomeError, OSError, ValueError, TypeError, RecursionError):
        return {
            "combined_score": 0.0, "valid": 0.0, "operations": 0.0,
            "squarings": 0.0, "multiplications": 0.0, "weight5": 0.0,
            "strict_improvement": 0.0,
        }
    return {
        "combined_score": float(10_000 * (MAX_ROWS - result.operations) + 3_000 - result.weight5),
        "valid": 1.0,
        "operations": float(result.operations),
        "squarings": float(result.squarings),
        "multiplications": float(result.multiplications),
        "weight5": float(result.weight5),
        "strict_improvement": float(result.operations < 421),
    }
