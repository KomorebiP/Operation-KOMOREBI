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


def wavelet_analysis(values):
    """All lowpass-branch Haar coordinates: mean, then coarse-to-fine details."""
    mean, levels = analyze(values)
    return (mean,) + tuple(d for _, details in reversed(levels) for d in details)


def wavelet_synthesis(coordinates):
    """Inverse transform using only the declared coarse-to-fine coordinates."""
    coordinates = exact(coordinates)
    n = len(coordinates)
    if n < 2 or n & (n-1):
        raise ValueError("Wavelet coordinates need a power-of-two length >= 2")
    current = (coordinates[0],)
    offset = 1
    while len(current) < n:
        count = len(current)
        current = inverse_haar_pair(current, coordinates[offset:offset+count])
        offset += count
    if offset != n:
        raise AssertionError("Wavelet coordinate partition did not close")
    return current


def wavelet_labels(length):
    if length < 2 or length & (length - 1):
        raise ValueError("Wavelet coordinate labels require a dyadic length")
    depth = length.bit_length()-1
    return ("m",) + tuple(f"L{j}.{k}" for j in range(depth,0,-1)
                           for k in range(length//(2**j)))


def wavelet_energy_levels(coordinates):
    """Five weighted bands for length 16; generalized to any dyadic length."""
    coordinates = exact(coordinates)
    labels = wavelet_labels(len(coordinates))
    depth = len(coordinates).bit_length()-1
    result = [("mean", len(coordinates)*coordinates[0]**2,
               int(coordinates[0] != 0))]
    offset = 1
    for j in range(depth,0,-1):
        width = len(coordinates)//(2**j)
        values = coordinates[offset:offset+width]
        result.append((f"level_{j}", (2**j)*energy(values),
                       sum(int(value != 0) for value in values)))
        offset += width
    if len(labels) != offset:
        raise AssertionError("The scale labels do not match the input")
    return tuple(result)


def full_wavelet_transfer(length=16):
    """Exact W H W^-1 matrix, columns obtained from wavelet coordinate impulses."""
    wavelet_labels(length)
    columns = []
    for j in range(length):
        e = tuple(F(k == j) for k in range(length))
        columns.append(wavelet_analysis(fir(wavelet_synthesis(e))))
    return tuple(tuple(columns[j][i] for j in range(length))
                 for i in range(length))


def apply_matrix(matrix, values):
    values = exact(values)
    if len(matrix) != len(values) or any(len(row) != len(values) for row in matrix):
        raise ValueError("Transfer matrix and coordinate length differ")
    return tuple(sum((F(a)*b for a,b in zip(row,values)),F(0)) for row in matrix)


def coarsen_first_level(values):
    """Project onto first-level Haar averages, duplicating every pair mean."""
    values = exact(values)
    if len(values)<2 or len(values)%2:
        raise ValueError("First-level coarsening needs a positive even length")
    return inverse_haar_pair(haar_pair(*split_phases(values))[0],
                             (F(0),)*(len(values)//2))


def operation_commutator(values):
    """(P H - H P)x, where P is the averaging projection."""
    values = exact(values)
    ph = coarsen_first_level(fir(values))
    hp = fir(coarsen_first_level(values))
    return tuple(a-b for a,b in zip(ph,hp))


def multiscale_transfer_svg(matrix):
    """Python-generated signed rational heatmap with matching coordinate labels."""
    n = len(matrix)
    labels = wavelet_labels(n)
    if len(matrix)!=n or any(len(row)!=n for row in matrix):
        raise ValueError("Heatmap requires a square wavelet matrix")
    cell = 34
    left, top = 138, 112
    width, height = 822, 774
    nnz=sum(int(coefficient != 0) for row in matrix for coefficient in row)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="822" height="774" viewBox="0 0 822 774" role="img" aria-labelledby="title description">',
        '<title id="title">Exact four-level Haar transfer matrix</title>',
        '<desc id="description">A 16 by 16 matrix for W H W inverse. Rows are output wavelet coordinates, columns are input wavelet coordinates, ordered global mean then levels four through one. Teal is positive, ochre negative, grey zero. Each nonzero cell is labeled with its exact rational value.</desc>',
        '<rect width="822" height="774" fill="#fff"/>',
        '<text x="36" y="34" font-family="sans-serif" font-size="21" font-weight="600" fill="#173f3a">FIR transfer in four-level Haar coordinates</text>',
        f'<text x="36" y="60" font-family="sans-serif" font-size="14" fill="#425852">{n} × {n} exact coefficients · {nnz} nonzero · W H W⁻¹</text>',
        '<text x="140" y="85" font-family="sans-serif" font-size="12" fill="#536b66">Input wavelet coordinates (columns)</text>',
        '<text x="12" y="107" font-family="sans-serif" font-size="12" fill="#536b66">Output rows</text>'
    ]
    for j, label in enumerate(labels):
        cx = left + j*cell + cell//2
        parts.append(f'<text x="{cx}" y="104" text-anchor="middle" font-family="monospace" font-size="10" fill="#445f59">{label}</text>')
    for i, row in enumerate(matrix):
        y = top+i*cell
        parts.append(f'<text x="{left-10}" y="{y+22}" text-anchor="end" font-family="monospace" font-size="11" fill="#334e49">{labels[i]}</text>')
        for j, value in enumerate(row):
            x = left+j*cell
            fill="#edf1f0" if value==0 else ("#28786d" if value>0 else "#b57442")
            parts.append(f'<rect x="{x}" y="{y}" width="{cell-1}" height="{cell-1}" rx="2" fill="{fill}"/>')
            if value:
                foreground="#ffffff"
                parts.append(f'<text x="{x+cell//2}" y="{y+21}" text-anchor="middle" font-family="monospace" font-size="10" font-weight="600" fill="{foreground}">{value}</text>')
    parts.extend((
        '<rect x="140" y="686" width="16" height="16" fill="#28786d"/>',
        '<text x="165" y="699" font-family="sans-serif" font-size="13" fill="#334e49">positive</text>',
        '<rect x="258" y="686" width="16" height="16" fill="#b57442"/>',
        '<text x="283" y="699" font-family="sans-serif" font-size="13" fill="#334e49">negative</text>',
        '<rect x="382" y="686" width="16" height="16" fill="#edf1f0"/>',
        '<text x="407" y="699" font-family="sans-serif" font-size="13" fill="#334e49">zero</text>',
        '<text x="140" y="740" font-family="sans-serif" font-size="13" fill="#536b66">Averaging-normalized Haar basis · no approximation · finite circular boundary</text>',
        '</svg>'
    ))
    return "\n".join(parts) + "\n"


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

    # Full four-level operator transfer, not merely one Haar pair.
    wx = wavelet_analysis(x)
    wy = wavelet_analysis(case["filtered"])
    matrix16 = full_wavelet_transfer(16)
    project = coarsen_first_level
    ph = project(case["filtered"])
    hp = fir(project(x))
    commutator = operation_commutator(x)
    require(wx == exact((3,1,-2,-2,0,0,-4,0,0,0,0,0,0,8,0,0)),
            "multiscale", "full input coefficient ordering")
    require(wy == exact((6,2,-4,0,0,0,-12,-4,2,0,-4,0,10,-8,-16,0)),
            "multiscale", "full filtered coefficient ordering")
    require(wavelet_synthesis(wx) == x,
            "multiscale", "wavelet analysis-synthesis inverse")
    require(wavelet_synthesis(wy) == case["filtered"],
            "multiscale", "filtered wavelet analysis-synthesis")
    require(tuple(value for _,value,_ in wavelet_energy_levels(wx))
            == exact((144,16,64,64,128)),
            "multiscale", "five original weighted energy bands")
    require(tuple(value for _,value,_ in wavelet_energy_levels(wy))
            == exact((576,64,128,640,880)),
            "multiscale", "five filtered weighted energy bands")
    require(sum(int(t!=0) for t in wx) == 6,
            "multiscale", "original wavelet support size")
    require(sum(int(t!=0) for t in wy) == 10,
            "multiscale", "filtered wavelet support size")
    require(len(matrix16) == 16 and all(len(row)==16 for row in matrix16),
            "multiscale", "full square transfer matrix shape")
    require(sum(t!=0 for row in matrix16 for t in row) == 56,
            "multiscale", "exact transfer matrix sparsity")
    require(apply_matrix(matrix16, wx) == wy,
            "multiscale", "full four-level operator transfer on the signal")
    require(matrix16[0] == exact((2,)+(0,)*15),
            "multiscale", "the global mean scales exactly by two")
    require(project(x) == case["coarse"],
            "multiscale", "coarsening equals dropping finest details")
    require(project(project(x)) == project(x),
            "multiscale", "coarsening is idempotent")
    require(energy(commutator) == 624,
            "multiscale", "noncommutation witness energy")
    require(energy(tuple(case["filtered"][i]-hp[i] for i in range(16))) == 768
            and energy(tuple(case["filtered"][i]-ph[i] for i in range(16))) == 880,
            "multiscale", "distinct orders have distinct projection errors")
    require(energy(commutator) == energy(case["filter_error"]),
            "multiscale", "commutator norm equals omitted-transfer energy")
    require(commutator == exact((-2,2,0,0,4,-4,0,0,-10,10,16,0,-8,-8,0,0)),
            "multiscale", "exact commutator coordinate witness")
    require(commutator != (F(0),)*16,
            "multiscale", "filter and coarse projection do not commute")

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
        waves = wavelet_analysis(basis)
        require(wavelet_synthesis(waves) == basis,
                "multiscale", "four-level inverse on coordinate impulse")
        require(apply_matrix(matrix16, waves) == wavelet_analysis(direct),
                "multiscale", "whole wavelet matrix on coordinate impulse")
        require(energy(operation_commutator(basis))
                == energy(skew_shift(basis)),
                "multiscale", "whole commutator on sample impulse")
        require(energy(basis) == sum(v for _,v,_ in wavelet_energy_levels(waves)),
                "multiscale", "wavelet energy on sample impulse")

    # Exhaustive small-integer 4-vectors and deterministic longer controls.
    matrix4=full_wavelet_transfer(4)
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
        require(apply_matrix(matrix4, wavelet_analysis(s)) == wavelet_analysis(direct),
                "multiscale", "exhaustive 4-point whole wavelet transfer")
        require(energy(operation_commutator(s)) == energy(skew_shift(s)),
                "multiscale", "exhaustive 4-point noncommutation certificate")
    rng = Random(20261030)
    wavelet_matrices = {8:full_wavelet_transfer(8),16:matrix16,32:full_wavelet_transfer(32)}
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
            require(apply_matrix(wavelet_matrices[length], wavelet_analysis(s))
                    == wavelet_analysis(direct),
                    "multiscale", "whole wavelet transfer for seeded signal")
            require(energy(operation_commutator(s)) == energy(skew_shift(s)),
                    "multiscale", "noncommutation for seeded signal")
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
    input_waves = wavelet_analysis(x)
    output_waves = wavelet_analysis(case["filtered"])
    matrix = full_wavelet_transfer(len(x))
    labels = wavelet_labels(len(x))
    with (folder/"full-wavelet-transfer.csv").open("w", encoding="utf-8", newline="") as stream:
        w = csv.writer(stream, lineterminator="\n")
        w.writerow(("output_index","output_coordinate","input_index","input_coordinate","coefficient"))
        for i, row in enumerate(matrix):
            for j, coefficient in enumerate(row):
                if coefficient:
                    w.writerow((i, labels[i], j, labels[j], str(coefficient)))
    input_bands = wavelet_energy_levels(input_waves)
    output_bands = wavelet_energy_levels(output_waves)
    with (folder/"multiscale-energy.csv").open("w", encoding="utf-8", newline="") as stream:
        w = csv.writer(stream, lineterminator="\n")
        w.writerow(("band","original_energy","filtered_energy","original_nonzero","filtered_nonzero"))
        for (name, en0, count0), (_, en1, count1) in zip(input_bands,output_bands):
            w.writerow((name, str(en0), str(en1), count0, count1))
    ph=coarsen_first_level(case["filtered"])
    hp=fir(coarsen_first_level(x))
    with (folder/"operation-order.csv").open("w", encoding="utf-8", newline="") as stream:
        w=csv.writer(stream, lineterminator="\n")
        w.writerow(("index","original","filtered","coarse_original","filter_coarse",
                    "coarse_filtered","commutator","filtered_minus_filter_coarse",
                    "filtered_minus_coarse_filtered"))
        for k in range(len(x)):
            w.writerow((k,str(x[k]),str(case["filtered"][k]),str(case["coarse"][k]),
                        str(hp[k]),str(ph[k]),str(ph[k]-hp[k]),
                        str(case["filtered"][k]-hp[k]),
                        str(case["filtered"][k]-ph[k])))
    (folder/"full-wavelet-transfer.svg").write_text(
        multiscale_transfer_svg(matrix), encoding="utf-8", newline="\n")
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
        "multiscale": {
            "matrix_order": len(matrix),
            "matrix_nonzero": sum(int(value != 0) for row in matrix for value in row),
            "input_wavelet_nonzero": sum(int(value != 0) for value in input_waves),
            "filtered_wavelet_nonzero": sum(int(value != 0) for value in output_waves),
            "input_band_energies": [int(v) for _, v, _ in input_bands],
            "filtered_band_energies": [int(v) for _, v, _ in output_bands],
            "commutator_energy": int(energy(operation_commutator(x))),
            "error_filter_coarse": int(energy(tuple(y-v for y,v in zip(case["filtered"],hp)))),
            "error_coarse_filtered": int(energy(tuple(y-v for y,v in zip(case["filtered"],ph)))),
        },
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
    print("Full Haar transfer: 16 x 16 rational matrix, 56 nonzero entries")
    print("Commutator energy 624; H(Px) error 768; P(Hx) error 880")
    print("PASS: " + str(sum(counts.values())) + " exact assertions")
    if args.output:
        save(args.output, counts)
        print("Exact tables and diagram written to " + str(args.output))


if __name__ == "__main__":
    main()
