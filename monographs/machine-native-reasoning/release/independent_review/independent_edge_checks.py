"""Independent, finite sanity fixtures; not the universal proof or release gate."""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json


def powerset(xs):
    xs = tuple(xs)
    return tuple(frozenset(s) for k in range(len(xs) + 1) for s in combinations(xs, k))


def check_fixture(name, worlds, cell, target):
    worlds = tuple(worlds)
    candidates = powerset(worlds)
    pairs = frozenset((cell(w), target(w)) for w in worlds)
    cells = frozenset(cell(w) for w in worlds)
    events = tuple(frozenset(w for w in worlds if cell(w) in J) for J in powerset(cells))
    occ = lambda V: frozenset((cell(w), target(w)) for w in V)
    signature = lambda V: tuple(frozenset(target(w) for w in V & E) for E in events)
    assert len({signature(V) for V in candidates}) == 2 ** len(pairs)
    for V in candidates:
        assert frozenset(y for _, y in occ(V)) == frozenset(target(w) for w in V)
        for W in candidates:
            assert (signature(V) == signature(W)) == (occ(V) == occ(W))
        for J, E in zip(powerset(cells), events):
            assert occ(V & E) == frozenset((i, y) for i, y in occ(V) if i in J)
    for S in powerset(pairs):
        realize = frozenset(w for w in worlds if (cell(w), target(w)) in S)
        assert occ(realize) == S
    assert occ(frozenset()) == frozenset()
    return dict(name=name, worlds=len(worlds), attained_pairs=len(pairs),
                candidate_subsets=len(candidates), admitted_events=len(events),
                signature_comparisons=len(candidates)**2,
                occupancy_records=2**len(pairs), passed=True)


fixtures = [
    ("empty extension", [], lambda w: w, lambda w: w),
    ("one world", [0], lambda w: 0, lambda w: 0),
    ("one cell constant target", [0, 1], lambda w: 0, lambda w: 0),
    ("two cells shared target duplicate fibre", [0, 1, 2], lambda w: w // 2, lambda w: 0),
    ("one cell two target values", [0, 1], lambda w: 0, lambda w: w),
    ("two cells each with two target values", list(product((0, 1), repeat=2)), lambda w: w[0], lambda w: w[1]),
    ("source sensor", list(product((0, 1), repeat=3)), lambda w: (w[0], w[1]), lambda w: w[0]),
]
results = [check_fixture(*fixture) for fixture in fixtures]

# Explicit failures of the old classification after changing admissible evidence.
u, v = frozenset([0]), frozenset([1])
constant_target = lambda V: frozenset(0 for _ in V)
old_occupancy = lambda V: frozenset((0, 0) for _ in V)
assert old_occupancy(u) == old_occupancy(v)
assert constant_target(u & u) != constant_target(v & u)
separate_occupancy = lambda V: frozenset((w, 0) for w in V)
assert separate_occupancy(u) != separate_occupancy(v)
reduced_events = [frozenset(), frozenset([0, 1])]
assert tuple(constant_target(u & E) for E in reduced_events) == tuple(constant_target(v & E) for E in reduced_events)

sensor_v = frozenset([(0, 0, 0), (1, 1, 0)])
sensor_w = frozenset([(0, 1, 0), (1, 0, 0)])
assert {w[0] for w in sensor_v} == {w[0] for w in sensor_w} == {0, 1}
assert {w[0] for w in sensor_v if w[1] == 0} == {0}
assert {w[0] for w in sensor_w if w[1] == 0} == {1}
assert 2 not in {0, 1}  # unused value for the Nat-valued two-target fixture
assert 2**4 > 2**3  # necessary cardinal obstruction; no claim to enumerate encoders

out = dict(kind="supplementary independent finite sanity checks", fixtures=results,
           changed_evidence_counterexamples_passed=True,
           source_sensor_collision_passed=True,
           unused_target_value_passed=True,
           four_pairs_three_bits_cardinal_obstruction_passed=True)
here = Path(__file__).resolve().parent
out["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(here / "independent_edge_checks.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
