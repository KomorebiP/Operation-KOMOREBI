#!/usr/bin/env python3
"""Exact packet, motif, and Green-kernel tests for the six-wire F_2 circuit threshold.

Run after circuit_census_f2 so that circuit_census_f2.out is present.
No internet access or nonstandard Python packages are required.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
import json
import re
from pathlib import Path

N = 6


def ident(n: int = N) -> tuple[int, ...]:
    return tuple(1 << i for i in range(n))


def gate(rows: tuple[int, ...], source: int, target: int) -> tuple[int, ...]:
    out = list(rows)
    out[target] ^= out[source]
    return tuple(out)


def run(gates, n: int = N) -> tuple[int, ...]:
    state = ident(n)
    for source, target in gates:
        state = gate(state, source, target)
    return state


def multiply(A: tuple[int, ...], B: tuple[int, ...]) -> tuple[int, ...]:
    out = []
    for row in A:
        value = 0
        for k in range(N):
            if (row >> k) & 1:
                value ^= B[k]
        out.append(value)
    return tuple(out)


def inverse(A: tuple[int, ...]) -> tuple[int, ...]:
    left = list(A)
    right = [1 << i for i in range(N)]
    for column in range(N):
        pivot = next(i for i in range(column, N) if (left[i] >> column) & 1)
        left[column], left[pivot] = left[pivot], left[column]
        right[column], right[pivot] = right[pivot], right[column]
        for i in range(N):
            if i != column and ((left[i] >> column) & 1):
                left[i] ^= left[column]
                right[i] ^= right[column]
    return tuple(right)


def exact_word_layers(start, generators, depth):
    layers = [{start: 1}]
    current = {start: 1}
    for _ in range(depth):
        nxt = defaultdict(int)
        for state, count in current.items():
            for source, target in generators:
                nxt[gate(state, source, target)] += count
        current = dict(nxt)
        layers.append(current)
    return layers


def parse_defects(path: Path):
    defects = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("code "):
            match = re.search(r"rows(.*)$", line)
            assert match
            defects.add(tuple(int(x) for x in match.group(1).split()))
    return defects


def generate_three_cross_one_phase_motifs():
    """Generate every irreducible six-role one-catalyst motif.

    The central pair p<q is adjacent.  There are four auxiliary rows.  One is
    a phase leaf; the other three are cross leaves.  The opposite-side cross
    leaves are divided nontrivially before/after the phase.
    """
    motifs = {}
    for p in range(1, 4):
        q = p + 1
        left = list(range(p))
        right = list(range(q + 1, N))

        # Left phase x -> p.  Other left leaves update q.  Right reads of p
        # are split nontrivially around the phase.
        for phase in left:
            cross_left = [x for x in left if x != phase]
            for mask in range(1, (1 << len(right)) - 1):
                before = [right[i] for i in range(len(right)) if (mask >> i) & 1]
                after = [y for y in right if y not in before]
                word = ([(q, p)] + [(x, q) for x in cross_left]
                        + [(p, y) for y in before] + [(phase, p)]
                        + [(p, y) for y in after] + [(q, p)])
                motifs[run(word)] = {
                    "orientation": "left_phase", "p": p, "q": q,
                    "phase": phase, "before": before, "word": word,
                }

        # Right phase q -> y.  Left updates of q are split nontrivially
        # around the phase.  Other right leaves read p.
        for phase in right:
            cross_right = [y for y in right if y != phase]
            for mask in range(1, (1 << len(left)) - 1):
                before = [left[i] for i in range(len(left)) if (mask >> i) & 1]
                after = [x for x in left if x not in before]
                word = ([(q, p)] + [(x, q) for x in before] + [(q, phase)]
                        + [(x, q) for x in after]
                        + [(p, y) for y in cross_right] + [(q, p)])
                motifs[run(word)] = {
                    "orientation": "right_phase", "p": p, "q": q,
                    "phase": phase, "before": before, "word": word,
                }
    return motifs


def projective_pasch_test():
    # Nonzero points in span{x,p,q}=F_2^3, represented in ambient coordinates.
    x, p, q = 1 << 0, 1 << 1, 1 << 2
    points = {x, p, q, p ^ q, p ^ q ^ x, p ^ x}
    missing = (x ^ q)
    all_lines = []
    for triple in combinations(sorted(points), 3):
        if triple[0] ^ triple[1] ^ triple[2] == 0:
            all_lines.append(triple)
    degrees = Counter(v for line in all_lines for v in line)
    assert len(points) == 6 and missing not in points
    assert len(all_lines) == 4
    assert set(degrees.values()) == {2}
    return {
        "points": sorted(points), "missing_fano_point": missing,
        "lines": [list(line) for line in all_lines],
        "line_degree_multiset": sorted(degrees.values()),
    }


def main():
    census_path = Path("circuit_census_f2.out")
    if not census_path.exists():
        raise SystemExit("Run circuit_census_f2 first.")
    defects = parse_defects(census_path)
    motifs = generate_three_cross_one_phase_motifs()
    assert len(defects) == 20
    assert len(motifs) == 20
    assert set(motifs) == defects

    low_generators = [(s, t) for s in range(N) for t in range(N) if s < t]
    all_generators = [(s, t) for s in range(N) for t in range(N) if s != t]
    I = ident()
    canonical_word = [(2, 1), (1, 3), (0, 1), (1, 4), (1, 5), (2, 1)]
    canonical = run(canonical_word)
    assert canonical in defects

    low_layers = exact_word_layers(I, low_generators, 10)
    ambient_layers = exact_word_layers(I, all_generators, 4)
    inverse_cache = {state: inverse(state) for layer in ambient_layers for state in layer}

    def ambient_counts(target):
        out = []
        for k in range(9):
            a = k // 2; b = k - a
            value = 0
            for state, count in ambient_layers[a].items():
                endpoint = multiply(target, inverse_cache[state])
                value += count * ambient_layers[b].get(endpoint, 0)
            out.append(value)
        return out

    canonical_low = [layer.get(canonical, 0) for layer in low_layers]
    canonical_all = ambient_counts(canonical)
    assert canonical_low[:7] == [0] * 7 and canonical_low[7] == 543
    assert canonical_all[:6] == [0] * 6 and canonical_all[6] == 2

    signatures = Counter()
    for target in sorted(defects):
        low_signature = tuple(layer.get(target, 0) for layer in low_layers[7:11])
        all_signature = tuple(ambient_counts(target)[6:9])
        signatures[(low_signature, all_signature)] += 1
    assert len(signatures) == 5
    assert set(signatures.values()) == {4}

    output = {
        "defect_targets": 20,
        "analytic_motifs": 20,
        "motif_set_equals_exact_census": True,
        "canonical_target_rows": list(canonical),
        "canonical_restricted_green_coefficients_k0_to_k10": canonical_low,
        "canonical_ambient_green_coefficients_k0_to_k8": canonical_all,
        "endpoint_green_signature_packets": [
            {
                "restricted_k7_to_k10": list(key[0]),
                "ambient_k6_to_k8": list(key[1]),
                "target_count": multiplicity,
            }
            for key, multiplicity in sorted(signatures.items())
        ],
        "flagged_pasch": projective_pasch_test(),
    }
    Path("circuit_packet_results.json").write_text(json.dumps(output, indent=2), encoding="utf-8")

    print("Exact six-dimensional defects:", len(defects))
    print("Three-cross/one-phase motifs:", len(motifs))
    print("Motif set equals exact defect census: True")
    print("Canonical restricted Green coefficients k=0..10:", canonical_low)
    print("Canonical ambient Green coefficients k=0..8:", canonical_all)
    print("Endpoint Green-signature packets:", len(signatures), "of multiplicity 4 each")
    print("Circuit projective motif: Fano plane minus one point (four-line Pasch)")
    print("Wrote circuit_packet_results.json")


if __name__ == "__main__":
    main()
