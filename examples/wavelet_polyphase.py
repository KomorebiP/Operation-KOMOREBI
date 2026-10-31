#!/usr/bin/env python3
"""Exact finite Haar and polyphase FIR transfer, with reproducible source data.

All arithmetic uses Fraction. The FIR filter is circular on a declared finite
window; no infinite-signal or zero-extension claim is made.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
from random import Random

DEFAULT = (2, 2, 2, 2, 6, 6, 6, 6, -4, -4, 12, -4, 4, 4, 4, 4)
TAPS = (1, 2, -1)


def exact(values):
    return tuple(F(v) for v in values)


def split_phases(values, modulus=2):
    values = exact(values)
    if modulus < 1 or not values or len(values) % modulus:
        raise ValueError("The nonempty signal length must be divisible by the phase count")
    return tuple(values[r::modulus] for r in range(modulus))


def join_phases(phases):
    phases = tuple(exact(row) for row in phases)
    if not phases or not phases[0] or any(len(row) != len(phases[0]) for row in phases):
        raise ValueError("Phase rows must be nonempty and equally long")
    return tuple(phases[r][k] for k in range(len(phases[0])) for r in range(len(phases)))


def shift(values):
    """The periodic right shift (T x)[i] = x[(i-1) mod len(x)]."""
    values = exact(values)
    if not values:
        raise ValueError("Signal must be nonempty")
    return values[-1:] + values[:-1]


def fir(values, taps=TAPS):
    """Circular FIR: H = sum_j taps[j] T^j."""
    values = exact(values)
    if not values:
        raise ValueError("Signal must be nonempty")
    out = (F(0),) * len(values)
    shifted = values
    for coefficient in taps:
        out = tuple(a + F(coefficient) * b for a, b in zip(out, shifted))
        shifted = shift(shifted)
    return out


def haar_pair(even, odd):
    even, odd = exact(even), exact(odd)
    if len(even) != len(odd):
        raise ValueError("Haar phases need equal length")
    return (tuple((u + v) / 2 for u, v in zip(even, odd)),
            tuple((u - v) / 2 for u, v in zip(even, odd)))


def inverse_haar_pair(averages, details):
    averages, details = exact(averages), exact(details)
    if len(averages) != len(details):
        raise ValueError("Haar phases need equal length")
    return join_phases((tuple(a + d for a, d in zip(averages, details)),
                        tuple(a - d for a, d in zip(averages, details))))


def analyze(values):
    """Return final mean and all (averages, details), fine to coarse."""
    values = exact(values)
    if len(values) < 2 or len(values) & (len(values) - 1):
        raise ValueError("Haar analysis needs a power-of-two length >= 2")
    current, levels = values, []
    while len(current) > 1:
        averages, details = haar_pair(*split_phases(current))
        levels.append((averages, details))
        current = averages
    return current[0], tuple(levels)


def synthesize(mean, levels, omit=frozenset()):
    """Reconstruct. An omitted detail (level, index) is replaced by zero."""
    current = (F(mean),)
    for j in range(len(levels), 0, -1):
        details = levels[j - 1][1]
        if len(current) != len(details):
            raise ValueError("Inconsistent Haar level lengths")
        saved = tuple(F(0) if (j, k) in omit else d for k, d in enumerate(details))
        current = inverse_haar_pair(current, saved)
    return current


def energy(values):
    return sum((F(v) ** 2 for v in values), F(0))


def coefficient_energy(mean, levels):
    length = 2 ** len(levels)
    return length * F(mean) ** 2 + sum(
        (2 ** j * energy(pair[1]) for j, pair in enumerate(levels, 1)), F(0))


def transfer_polyphase(even, odd):
    """(E',O') = ((I-Z)E+2ZO, 2E+(I-Z)O), Z a circular half-rate shift."""
    even, odd = exact(even), exact(odd)
    if len(even) != len(odd) or not even:
        raise ValueError("Equal nonempty phase rows required")
    ze, zo = shift(even), shift(odd)
    return (tuple(e - ep + 2 * op for e, ep, op in zip(even, ze, zo)),
            tuple(2 * e + o - op for e, o, op in zip(even, odd, zo)))


def transfer_haar(averages, details):
    """(A',D') = (2A+(I-Z)D, (Z-I)A-2ZD)."""
    averages, details = exact(averages), exact(details)
    if len(averages) != len(details) or not averages:
        raise ValueError("Equal nonempty coefficient rows required")
    za, zd = shift(averages), shift(details)
    return (tuple(2*a + d - prev for a, d, prev in zip(averages, details, zd)),
            tuple(prev - a - 2*old for a, prev, old in zip(averages, za, zd)))


def diagonal_only(averages, details):
    """Deliberately invalid shortcut: erase the two off-diagonal transfers."""
    a, d = exact(averages), exact(details)
    return inverse_haar_pair(tuple(2*x for x in a), tuple(-2*x for x in shift(d)))


def default_case():
    x = exact(DEFAULT)
    mean, levels = analyze(x)
    omit = frozenset((1, k) for k in range(len(levels[0][1])))
    coarse = synthesize(mean, levels, omit)
    residual = tuple(u - v for u, v in zip(x, coarse))
    filtered = fir(x)
    even, odd = split_phases(x)
    a, d = haar_pair(even, odd)
    wrong = diagonal_only(a, d)
    return dict(x=x, mean=mean, levels=levels, coarse=coarse, residual=residual,
                filtered=filtered, wrong=wrong,
                filter_error=tuple(u - v for u, v in zip(filtered, wrong)))


def check():
    counts = {}
    def require(condition, group, message):
        if not condition:
            raise AssertionError(group + ": " + message)
        counts[group] = counts.get(group, 0) + 1

    case = default_case()
    x, mean, levels = case["x"], case["mean"], case["levels"]
    require(mean == 3, "reference", "global mean")
    for j, expected in enumerate((
        (0, 0, 0, 0, 0, 8, 0, 0),
        (0, 0, -4, 0),
        (-2, -2),
        (1,)), 1):
        require(levels[j-1][1] == exact(expected), "reference", "detail level "+str(j))
    require(synthesize(mean, levels) == x, "reference", "full inverse")
    require(energy(x) == coefficient_energy(mean, levels) == 416,
            "reference", "weighted energy")
    require(case["coarse"] == exact((2,2,2,2,6,6,6,6,-4,-4,4,4,4,4,4,4)),
            "reference", "coarse sample sequence")
    require(case["residual"] == exact((0,0,0,0,0,0,0,0,0,0,8,-8,0,0,0,0)),
            "reference", "missing spike detail")
    require(energy(case["coarse"]) == 288 and energy(case["residual"]) == 128
            and energy(x) == energy(case["coarse"]) + energy(case["residual"]),
            "reference", "exact Pythagorean split")
    require(case["filtered"] == exact((6,2,4,4,8,16,12,12,2,-18,8,24,-16,16,8,8)),
            "reference", "circular FIR samples")
    require(energy(case["filtered"]) == 2288, "reference", "filtered energy")
    require(energy(case["filter_error"]) == 624, "reference", "off-diagonal omission")
    require(fir(x)[0] == x[0] + 2*x[-1] - x[-2] == 6,
            "reference", "periodic boundary")
    require(split_phases(x, 4) == (
        exact((2,6,-4,4)),exact((2,6,-4,4)),
        exact((2,6,12,4)),exact((2,6,-4,4))),
        "reference", "four-address refinement")
    require(join_phases(split_phases(x, 2)) == join_phases(split_phases(x, 4)) == x,
            "reference", "two and four address synthesis")
    require(haar_pair(*split_phases(case["filtered"])) ==
            transfer_haar(*haar_pair(*split_phases(x))),
            "reference", "transferred Haar coefficients")
    require(join_phases(transfer_polyphase(*split_phases(x))) == case["filtered"],
            "reference", "polyphase transfer")
    require(diagonal_only(*haar_pair(*split_phases(x))) != case["filtered"],
            "obstructions", "cross phase interactions cannot be discarded")
    require(haar_pair(*split_phases(case["coarse"]))[0] ==
            haar_pair(*split_phases(x))[0], "obstructions", "lowpass collision")
    require(case["coarse"] != x, "obstructions", "different signals same lowpass")
    require(synthesize(*analyze(case["coarse"])) == case["coarse"],
            "obstructions", "coarsened signal is valid")
    even, odd = split_phases(x)
    require(join_phases((even, (F(0),)*len(odd))) != x,
            "obstructions", "missing odd phase")
    require(x[10] == 12 and x[11] == -4 and
            case["filtered"][10] == 8 and case["filtered"][11] == 24,
            "reference", "local boundary-crossing calculation")

    # Linearity plus equality on every coordinate basis vector gives an
    # exact 16-dimensional operator identity, not merely a sample agreement.
    for k in range(16):
        basis = tuple(F(i == k) for i in range(16))
        e, o = split_phases(basis)
        a, d = haar_pair(e, o)
        direct = fir(basis)
        require(join_phases(transfer_polyphase(e, o)) == direct,
                "basis", "polyphase FIR basis "+str(k))
        require(haar_pair(*split_phases(direct)) == transfer_haar(a, d),
                "basis", "Haar conjugacy basis "+str(k))
        require(synthesize(*analyze(basis)) == basis, "basis", "wavelet basis "+str(k))

    # Exhaustive small-integer 4-vectors and deterministic longer controls.
    for numbers in product((-2, -1, 0, 1, 2), repeat=4):
        s = exact(numbers)
        m, stages = analyze(s)
        require(synthesize(m, stages) == s, "exhaustive", "four-sample inverse")
        require(coefficient_energy(m, stages) == energy(s),
                "exhaustive", "four-sample energy")
        require(join_phases(transfer_polyphase(*split_phases(s))) == fir(s),
                "exhaustive", "four-sample polyphase FIR")
    rng = Random(20261030)
    for length in (8, 16, 32):
        for _ in range(32):
            s = exact(rng.randrange(-12, 13) for _ in range(length))
            m, stages = analyze(s)
            require(synthesize(m, stages) == s, "random", "multilevel synthesis")
            require(coefficient_energy(m, stages) == energy(s),
                    "random", "weighted Parseval identity")
            require(join_phases(split_phases(s, 2)) == s, "random", "phase inverse")
            require(join_phases(transfer_polyphase(*split_phases(s))) == fir(s),
                    "random", "circular FIR polyphase transfer")
            require(haar_pair(*split_phases(fir(s))) ==
                    transfer_haar(*haar_pair(*split_phases(s))),
                    "random", "Haar coordinate transfer")
    return counts


def figure_svg(case):
    """A small, accessible SVG generated from exact sample data."""
    width, height = 1020, 490
    colors = ("#205e54", "#287d89", "#b96b35")
    panels = ((case["x"], "Original x", colors[0]),
              (case["coarse"], "Coarse reconstruction (finest details removed)", colors[1]),
              (case["residual"], "Residual x - reconstruction", colors[2]))
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1020" height="490" viewBox="0 0 1020 490" role="img" aria-labelledby="title description">',
        '<title id="title">Haar reconstruction and exact residual</title>',
        '<desc id="description">Three aligned sixteen-sample stem plots: the input signal, its lowpass reconstruction, and the missing finest detail. The residual has values eight and negative eight only at positions ten and eleven.</desc>',
        '<rect width="1020" height="490" fill="#ffffff"/>',
        '<text x="35" y="30" font-family="sans-serif" font-size="20" font-weight="600" fill="#193b36">One signal · full, coarse and residual coordinates</text>',
    ]
    def fmt(v):
        return format(float(v), ".2f")
    for index, (data, name, color) in enumerate(panels):
        top = 48 + index * 146
        baseline = top + 88
        pieces.extend((
            f'<text x="36" y="{top+15}" font-family="sans-serif" font-size="15" font-weight="600" fill="#203c39">{name}</text>',
            f'<line x1="41" y1="{baseline}" x2="972" y2="{baseline}" stroke="#9eb3af" stroke-width="1.2"/>',
            f'<rect x="30" y="{top+23}" width="950" height="114" rx="6" fill="none" stroke="#e3eeeb"/>',
        ))
        for k, value in enumerate(data):
            px = 60 + 58*k
            py = baseline - 4.8*float(value)
            pieces.append(f'<line x1="{px}" y1="{baseline}" x2="{px}" y2="{fmt(py)}" stroke="{color}" stroke-width="3"/>')
            pieces.append(f'<circle cx="{px}" cy="{fmt(py)}" r="4" fill="{color}"/>')
            if k in (0, 4, 8, 12, 15):
                pieces.append(f'<text x="{px}" y="{top+130}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#526966">{k}</text>')
    pieces.extend((
        '<text x="977" y="473" text-anchor="end" font-family="sans-serif" font-size="11" fill="#526966">Sample addresses 0–15 · linear amplitude scale in every panel</text>',
        '</svg>'))
    return "\n".join(pieces) + "\n"


def save(folder, counts):
    folder.mkdir(parents=True, exist_ok=True)
    case = default_case()
    x, levels = case["x"], case["levels"]
    with (folder/"phase-transfer.csv").open("w", encoding="utf-8", newline="") as stream:
        w = csv.writer(stream, lineterminator="\n")
        w.writerow(("index", "original", "coarse", "residual", "circular_fir",
                    "incorrect_diagonal_only", "transfer_error"))
        for i in range(len(x)):
            w.writerow((i, *(str(v[i]) for v in (
                x, case["coarse"], case["residual"], case["filtered"],
                case["wrong"], case["filter_error"]))))
    with (folder/"haar-coefficients.csv").open("w", encoding="utf-8", newline="") as stream:
        w = csv.writer(stream, lineterminator="\n")
        w.writerow(("kind", "level", "index", "value", "energy_weight", "weighted_energy"))
        w.writerow(("mean", 4, 0, str(case["mean"]), 16, str(16*case["mean"]**2)))
        for j in range(len(levels), 0, -1):
            for k, d in enumerate(levels[j-1][1]):
                w.writerow(("detail", j, k, str(d), 2**j, str(2**j*d*d)))
    (folder/"signal-comparison.svg").write_text(figure_svg(case), encoding="utf-8", newline="\n")
    record = {
        "case": "Haar averaging / cyclic FIR (1, 2, -1)",
        "signal": list(DEFAULT),
        "filtered": [int(v) for v in case["filtered"]],
        "coarse": [int(v) for v in case["coarse"]],
        "energies": {"original": 416, "coarse": 288, "residual": 128,
                     "filtered": 2288, "missing_transfer_blocks": 624},
        "assertions_by_group": counts,
        "total_assertions": sum(counts.values()),
        "scope": "Exact finite models; no infinite-domain or cross-boundary filter claim."
    }
    (folder/"results.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n",
                                       encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write reproducible CSV, SVG, and JSON records")
    args = parser.parse_args()
    counts = check()
    case = default_case()
    print("WAVELET POLYPHASE | 16 samples | circular FIR (1,2,-1)")
    print("Original energy 416 = coarse 288 + residual 128")
    print("Direct FIR equals both transported polyphase and Haar operators")
    print("Omitting two transfer blocks gives squared error 624")
    print("PASS: " + str(sum(counts.values())) + " exact assertions")
    if args.output:
        save(args.output, counts)
        print("Exact tables and diagram written to " + str(args.output))


if __name__ == "__main__":
    main()
