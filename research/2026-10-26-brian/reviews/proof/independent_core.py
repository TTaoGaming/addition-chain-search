"""Exact exponent-triple replay, authored before reading the bundle verifier.

Definition: exponent 1 is free. Each ordered [v, a, b] operation must
consume two earlier positive integer exponents with v = a + b. Every row
is charged; a == b is S, otherwise M. The terminal exponent must be target.
No arithmetic is performed modulo a field or scalar order.
"""


class InvalidWitness(ValueError):
    pass


def exact_integer(value):
    # bool and float are intentionally not mathematical integer encodings.
    if type(value) is not int:
        raise InvalidWitness("exponents must be JSON/Python integers")
    if value <= 0:
        raise InvalidWitness("exponents must be positive")
    return value


def check(rows, target):
    exact_integer(target)
    if type(rows) is not list or not rows:
        raise InvalidWitness("nonempty operation list required")
    available = {1: -1}
    dependencies = []
    squarings = 0
    duplicate_outputs = []
    increasing = True
    previous = 1
    for index, row in enumerate(rows):
        if type(row) is not list or len(row) != 3:
            raise InvalidWitness(f"row {index}: expected [v,a,b]")
        v, a, b = [exact_integer(x) for x in row]
        if a not in available or b not in available:
            raise InvalidWitness(f"row {index}: unavailable parent")
        if v != a + b:
            raise InvalidWitness(f"row {index}: incorrect integer sum")
        dependencies.append((available[a], available[b]))
        if v in available:
            duplicate_outputs.append(index)
        available[v] = index
        squarings += int(a == b)
        increasing = increasing and (v > previous)
        previous = v
    if rows[-1][0] != target:
        raise InvalidWitness("wrong terminal target")
    # Positive sums plus earlier-parent checks give inductive ancestry to 1.
    # When a value repeats, parent references resolve to its latest occurrence.
    live = set()
    frontier = [len(rows) - 1]
    while frontier:
        index = frontier.pop()
        if index == -1 or index in live:
            continue
        live.add(index)
        frontier.extend(dependencies[index])
    dead = sorted(set(range(len(rows))) - live)
    return {
        "target_decimal": str(target),
        "charged": {"operations": len(rows), "S": squarings,
                    "M": len(rows) - squarings},
        "live_operations": len(live),
        "dead_indices_zero_based": dead,
        "duplicate_output_indices_zero_based": duplicate_outputs,
        "strictly_increasing": increasing,
        "ancestry": "all parents inductively derive from exponent 1",
        "duplicate_resolution": "latest prior occurrence; all rows charged",
    }
