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


def backward_shift(values):
    """The inverse cyclic shift (T^-1 x)[i] = x[(i+1) mod len(x)]."""
    values = exact(values)
    if not values:
        raise ValueError("Signal must be nonempty")
    return values[1:] + values[:1]


def skew_shift(values):
    """(T^-1 - T)x, the finite energy certificate for the FIR."""
    return tuple(left - right for left, right
                 in zip(backward_shift(values), shift(values)))


def zero_extended_fir(values, taps=TAPS):
    """Finite causal convolution with values outside the window set to zero."""
    values = exact(values)
    if not values:
        raise ValueError("Signal must be nonempty")
    return tuple(sum((F(tap) * values[i-j]
                      for j, tap in enumerate(taps) if 0 <= i-j < len(values)),
                     F(0)) for i in range(len(values)))


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


def lifting_decompose(even, odd):
    """Paper V predict/update: difference=odd-even, average=even+difference/2."""
    even, odd = exact(even), exact(odd)
    if len(even) != len(odd):
        raise ValueError("Lifting phases need equal length")
    differences = tuple(o-e for e, o in zip(even, odd))
    averages = tuple(e + difference/2
                     for e, difference in zip(even, differences))
    return averages, differences


def lifting_synthesize(averages, differences):
    """Invert the predict/update map using exactly the stored side channel."""
    averages, differences = exact(averages), exact(differences)
    if len(averages) != len(differences):
        raise ValueError("Lifting phases need equal length")
    even = tuple(a - difference/2
                 for a, difference in zip(averages, differences))
    odd = tuple(e + difference for e, difference in zip(even, differences))
    return join_phases((even, odd))


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


def best_detail_budget(levels):
    """Optimal fixed Haar-coordinate budget with the mean always retained.

    The detail synthesis vectors are orthogonal with squared norm 2**level.
    Sort exact weighted energies; ties use (level,index) to be deterministic.
    Returns (retained_count, retained_energy, residual_energy) for each budget.
    This is not an adaptive best-packet-tree algorithm.
    """
    entries = sorted(
        ((2**j * F(d)**2, j, k)
         for j, (_, details) in enumerate(levels, 1)
         for k, d in enumerate(details) if d != 0),
        key=lambda item: (-item[0], item[1], item[2]))
    residual = sum((item[0] for item in entries), F(0))
    records = [(0, F(0), residual)]
    retained = F(0)
    for budget, (contribution, _, _) in enumerate(entries, 1):
        retained += contribution
        residual -= contribution
        records.append((budget, retained, residual))
    return tuple(records)


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
    boundary = zero_extended_fir(x)
    return dict(x=x, mean=mean, levels=levels, coarse=coarse, residual=residual,
                filtered=filtered, wrong=wrong, boundary=boundary,
                boundary_residual=tuple(u - v for u, v in zip(filtered, boundary)),
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

    # The independent Paper V lifting factorization uses d_L = odd-even.
    a, d = haar_pair(*split_phases(x))
    lifted_a, lifted_difference = lifting_decompose(*split_phases(x))
    require(lifted_a == a and lifted_difference == tuple(-2*v for v in d),
            "reference", "lifting equals Haar after declared rescaling")
    require(lifting_synthesize(lifted_a, lifted_difference) == x,
            "reference", "exact predict/update synthesis")
    skew = skew_shift(x)
    require(energy(skew) == 624 and
            energy(case["filtered"]) == 4*energy(x) + energy(skew),
            "reference", "sharp FIR energy identity")
    require(4*energy(x) <= energy(case["filtered"]) <= 8*energy(x),
            "reference", "finite stability interval")
    require(energy(case["filter_error"]) == energy(skew),
            "reference", "off-diagonal error equals FIR energy surplus")
    require(case["boundary_residual"] == exact((4,-4)+(0,)*14)
            and energy(case["boundary_residual"]) == 32,
            "reference", "two-site boundary correction")
    require(tuple(record[2] for record in best_detail_budget(levels))
            == tuple(map(F, (272,144,80,48,16,0))),
            "reference", "optimal fixed-basis detail budget")
    contrast = exact((2,)*8 + (-2,-2,1,-5,-2,-2,-2,-2))
    contrast_mean, contrast_levels = analyze(contrast)
    require(contrast_mean == 0 and energy(contrast) == 82
            and best_detail_budget(contrast_levels)[1] == (1,F(64),F(18)),
            "reference", "weighted selection beats largest raw magnitude")
    flat, quarter = exact((1,)*16), exact((1,0,-1,0)*4)
    require(energy(fir(flat)) == 4*energy(flat) and
            energy(fir(quarter)) == 8*energy(quarter),
            "reference", "both finite operator norm bounds are sharp")

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
        lifted_a, lifted_d = lifting_decompose(e, o)
        require(lifted_a == a and lifted_d == tuple(-2*v for v in d)
                and lifting_synthesize(lifted_a, lifted_d) == basis,
                "basis", "lifting operator basis "+str(k))
        require(energy(direct) == 4*energy(basis)+energy(skew_shift(basis)),
                "basis", "FIR adjoint energy basis "+str(k))
        require(energy(tuple(u-v for u,v in zip(direct, diagonal_only(a,d))))
                == energy(skew_shift(basis)),
                "basis", "omitted cross phase error basis "+str(k))
        residue = tuple(u-v for u,v in zip(direct, zero_extended_fir(basis)))
        require(residue == (2*basis[-1]-basis[-2], -basis[-1])
                + (F(0),)*(len(basis)-2),
                "basis", "boundary correction basis "+str(k))

    # Exhaustive small-integer 4-vectors and deterministic longer controls.
    for numbers in product((-2, -1, 0, 1, 2), repeat=4):
        s = exact(numbers)
        m, stages = analyze(s)
        require(synthesize(m, stages) == s, "exhaustive", "four-sample inverse")
        require(coefficient_energy(m, stages) == energy(s),
                "exhaustive", "four-sample energy")
        require(join_phases(transfer_polyphase(*split_phases(s))) == fir(s),
                "exhaustive", "four-sample polyphase FIR")
        even, odd = split_phases(s)
        a, d = haar_pair(even, odd)
        lifted_a, lifted_d = lifting_decompose(even, odd)
        require(lifted_a == a and lifted_d == tuple(-2*v for v in d)
                and lifting_synthesize(lifted_a, lifted_d) == s,
                "exhaustive", "four-sample lifting inverse")
        direct = fir(s)
        require(energy(direct) == 4*energy(s) + energy(skew_shift(s)),
                "exhaustive", "four-sample FIR energy")
        require(energy(tuple(u-v for u,v in zip(direct, diagonal_only(a,d))))
                == energy(skew_shift(s)),
                "exhaustive", "four-sample omitted cross blocks")
        boundary_difference = tuple(u-v for u,v in zip(direct, zero_extended_fir(s)))
        require(boundary_difference == (2*s[-1]-s[-2], -s[-1])
                + (F(0),)*(len(s)-2),
                "exhaustive", "four-sample edge correction")
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
            even, odd = split_phases(s)
            a, d = haar_pair(even, odd)
            lifted_a, lifted_d = lifting_decompose(even, odd)
            require(lifted_a == a and lifted_d == tuple(-2*v for v in d)
                    and lifting_synthesize(lifted_a, lifted_d) == s,
                    "random", "predict update lifting")
            direct = fir(s)
            require(energy(direct) == 4*energy(s) + energy(skew_shift(s)),
                    "random", "sharp finite filter energy")
            require(energy(tuple(u-v for u,v in zip(direct, diagonal_only(a,d))))
                    == energy(skew_shift(s)),
                    "random", "cross channel energy identity")
            boundary_difference = tuple(u-v for u,v in zip(direct, zero_extended_fir(s)))
            require(boundary_difference == (2*s[-1]-s[-2], -s[-1])
                    + (F(0),)*(len(s)-2),
                    "random", "cyclic versus zero edge packet")
    return counts


def figure_svg(case):
    """A small, accessible SVG generated from exact sample data."""
    width, height = 1020, 520
    colors = ("#205e54", "#287d89", "#b96b35")
    panels = ((case["x"], "Original x", colors[0]),
              (case["coarse"], "Coarse reconstruction (finest details removed)", colors[1]),
              (case["residual"], "Residual x - reconstruction", colors[2]))
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1020" height="520" viewBox="0 0 1020 520" role="img" aria-labelledby="title description">',
        '<title id="title">Haar reconstruction and exact residual</title>',
        '<desc id="description">Three aligned sixteen-sample stem plots: the input signal, its lowpass reconstruction, and the missing finest detail. The residual has values eight and negative eight only at positions ten and eleven.</desc>',
        '<rect width="1020" height="520" fill="#ffffff"/>',
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
        '<text x="977" y="504" text-anchor="end" font-family="sans-serif" font-size="11" fill="#526966">Sample addresses 0–15 · linear amplitude scale in every panel</text>',
        '</svg>'))
    return "\n".join(pieces) + "\n"


def save(folder, counts):
    folder.mkdir(parents=True, exist_ok=True)
    case = default_case()
    x, levels = case["x"], case["levels"]
    with (folder/"phase-transfer.csv").open("w", encoding="utf-8", newline="") as stream:
        w = csv.writer(stream, lineterminator="\n")
        w.writerow(("index", "original", "coarse", "residual", "circular_fir",
                    "incorrect_diagonal_only", "transfer_error",
                    "zero_extended_fir", "cyclic_minus_zero_boundary"))
        for i in range(len(x)):
            w.writerow((i, *(str(v[i]) for v in (
                x, case["coarse"], case["residual"], case["filtered"],
                case["wrong"], case["filter_error"], case["boundary"],
                case["boundary_residual"]))))
    with (folder/"haar-coefficients.csv").open("w", encoding="utf-8", newline="") as stream:
        w = csv.writer(stream, lineterminator="\n")
        w.writerow(("kind", "level", "index", "value", "energy_weight", "weighted_energy"))
        w.writerow(("mean", 4, 0, str(case["mean"]), 16, str(16*case["mean"]**2)))
        for j in range(len(levels), 0, -1):
            for k, d in enumerate(levels[j-1][1]):
                w.writerow(("detail", j, k, str(d), 2**j, str(2**j*d*d)))
    with (folder/"weighted-budget.csv").open("w", encoding="utf-8", newline="") as stream:
        w = csv.writer(stream, lineterminator="\n")
        w.writerow(("retained_details", "retained_detail_energy", "squared_residual_error"))
        for budget, retained, residual in best_detail_budget(levels):
            w.writerow((budget, str(retained), str(residual)))
    (folder/"signal-comparison.svg").write_text(figure_svg(case), encoding="utf-8", newline="\n")
    record = {
        "case": "Haar averaging / cyclic FIR (1, 2, -1)",
        "signal": list(DEFAULT),
        "filtered": [int(v) for v in case["filtered"]],
        "coarse": [int(v) for v in case["coarse"]],
        "energies": {"original": 416, "coarse": 288, "residual": 128,
                     "filtered": 2288, "missing_transfer_blocks": 624},
        "stability": {
            "fourfold_input": 1664,
            "skew_shift_energy": int(energy(skew_shift(x))),
            "filtered": int(energy(case["filtered"])),
            "eightfold_input": 3328,
            "omitted_transfer_error": int(energy(case["filter_error"])),
            "boundary_correction_energy": int(energy(case["boundary_residual"]))
        },
        "weighted_selection_control": {
            "coarse_detail_amplitude": 2,
            "fine_detail_amplitude": 3,
            "coarse_weighted_energy": 64,
            "fine_weighted_energy": 18,
            "raw_magnitude_selection_error": 64,
            "weighted_selection_error": 18
        },
        "budget_residual_energies": [int(row[2]) for row in best_detail_budget(levels)],
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
    print("FIR energy 2288 = 4 * 416 + 624; two omitted transfers also cost 624")
    print("Zero-extension boundary correction: (4,-4), squared energy 32")
    print("Best-detail budget errors: 272, 144, 80, 48, 16, 0")
    print("PASS: " + str(sum(counts.values())) + " exact assertions")
    if args.output:
        save(args.output, counts)
        print("Exact tables and diagram written to " + str(args.output))


if __name__ == "__main__":
    main()
