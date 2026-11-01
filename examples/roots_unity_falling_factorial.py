#!/usr/bin/env python3
"""Exact roots-of-unity, Newton and falling-factorial projector example.

All computation uses rational arithmetic in the Python standard library.
Roots of unity are handled through the equivalent exact cyclic trace,
not floating-point evaluations. These are classical finite identities.
"""
from __future__ import annotations

import argparse
import csv
import json
from fractions import Fraction
from itertools import product
from math import comb, factorial
from pathlib import Path

Q = Fraction
MAX_DEGREE = 8
ROW_FIVE = (0, 1, 15, 25, 10, 1)
FILES = (
    "newton-stirling.csv",
    "image-histograms.csv",
    "packet-egfs.csv",
    "spectral-projectors.csv",
    "packet-contributions.csv",
    "difference-transfer.csv",
    "refinement.csv",
    "projector-matrix.csv",
    "projection-diagram.svg",
    "function-image-histogram.svg",
    "results.json",
)


def trim(values):
    """Canonical ascending-power coefficient tuple."""
    out = [Q(x) for x in values]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out) if out else (Q(0),)


def add(a, b):
    out = [Q(0)] * max(len(a), len(b))
    for i, x in enumerate(a):
        out[i] += x
    for i, x in enumerate(b):
        out[i] += x
    return trim(out)


def scale(a, c):
    return trim(Q(c) * v for v in a)


def multiply(a, b):
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return trim(out)


def evaluate(a, x):
    value = Q(0)
    for coefficient in reversed(a):
        value = value * x + coefficient
    return value


def power(n):
    if n < 0:
        raise ValueError("Degree must be nonnegative")
    return (Q(0),) * n + (Q(1),)


def falling(k):
    """x_(k)=x(x-1)...(x-k+1), with x_(0)=1."""
    if k < 0:
        raise ValueError("Falling-factorial degree must be nonnegative")
    result = (Q(1),)
    for j in range(k):
        result = multiply(result, (Q(-j), Q(1)))
    return result


def shift(a):
    """Power-basis coefficients of f(x+1)."""
    out = [Q(0)] * len(a)
    for k, coefficient in enumerate(a):
        for j in range(k + 1):
            out[j] += coefficient * comb(k, j)
    return trim(out)


def delta(a):
    """Forward difference, f(x+1)-f(x)."""
    return add(shift(a), scale(a, -1))


def stirling_second(n):
    rows = [(1,)]
    for i in range(1, n + 1):
        prev = rows[-1]
        row = [0] * (i + 1)
        for k in range(1, i + 1):
            row[k] = (prev[k-1] if k-1 < len(prev) else 0) + (
                k * prev[k] if k < len(prev) else 0)
        rows.append(tuple(row))
    return tuple(rows)


def signed_stirling_first(n):
    rows = [(1,)]
    for i in range(1, n + 1):
        prev = rows[-1]
        row = [0] * (i + 1)
        for k in range(i + 1):
            row[k] = ((prev[k-1] if k else 0) -
                      (i - 1) * (prev[k] if k < len(prev) else 0))
        rows.append(tuple(row))
    return tuple(rows)


def from_newton(coefficients):
    """Phi(sum a_k z^k)=sum a_k x_(k). Linear, not multiplicative."""
    out = (Q(0),)
    for k, coefficient in enumerate(coefficients):
        out = add(out, scale(falling(k), coefficient))
    return out


def to_newton(poly):
    """Phi inverse via Newton interpolation at 0,1,...,degree."""
    poly = trim(poly)
    degree = len(poly) - 1
    diffs = [evaluate(poly, j) for j in range(degree + 1)]
    result = []
    for k in range(degree + 1):
        result.append(diffs[0] / factorial(k))
        diffs = [diffs[j+1] - diffs[j] for j in range(len(diffs)-1)]
    return tuple(result)


def project_newton(poly, modulus, residue):
    """Transport a character projector through Phi to polynomial x."""
    if not isinstance(modulus, int) or modulus < 2:
        raise ValueError("Require integer modulus at least two")
    if not isinstance(residue, int) or not 0 <= residue < modulus:
        raise ValueError("Residue must be in 0,...,modulus-1")
    coordinates = to_newton(poly)
    return from_newton(tuple(c if k % modulus == residue else Q(0)
                             for k, c in enumerate(coordinates)))


def naive_power_project(poly, modulus, residue):
    """INCORRECT replacement for transported projector on power coordinates."""
    return trim(v if k % modulus == residue else Q(0)
                for k, v in enumerate(poly))


def trace_character_selector(modulus, k, residue):
    """(1/m)Tr(C^(k-r)) for the regular cyclic permutation representation.

    C has the m eigenvalues of m-th roots of unity; the trace is exactly
    m or 0. This checks Fourier orthogonality using integers only.
    """
    if modulus < 2 or not 0 <= residue < modulus:
        raise ValueError("Invalid cyclic character filter")
    displacement = k - residue
    fixed_points = sum(i == (i + displacement) % modulus
                       for i in range(modulus))
    return Q(fixed_points, modulus)


def star(a, b):
    """Transport ordinary multiplication of Newton-coordinate polynomials."""
    ac, bc = to_newton(a), to_newton(b)
    result = [Q(0)] * (len(ac) + len(bc) - 1)
    for i, x in enumerate(ac):
        for j, y in enumerate(bc):
            result[i+j] += x * y
    return from_newton(result)


def shift_newton_derivative(coordinates):
    """Derivative on z coordinates, corresponding to Delta on x."""
    return tuple(Q(k+1)*coordinates[k+1]
                 for k in range(len(coordinates)-1)) or (Q(0),)



def translate(a, offset):
    """f(x+offset), computed independently by binomial expansion."""
    out = [Q(0)] * len(a)
    for k, coefficient in enumerate(a):
        for j in range(k + 1):
            out[j] += Q(coefficient) * comb(k, j) * Q(offset)**(k-j)
    return trim(out)


def backward_difference(a):
    """Nabla f(x) = f(x) - f(x-1)."""
    return add(a, scale(translate(a, -1), -1))


def newton_degree_operator(poly):
    """Number operator N = x*Nabla: N(x_(k))=k*x_(k)."""
    return multiply(power(1), backward_difference(poly))


def spectral_project_newton(poly, modulus, residue):
    """Exact projector as rational Lagrange polynomial in N on Q[x]_{<=d}."""
    if not isinstance(modulus, int) or modulus < 2:
        raise ValueError("Require integer modulus at least two")
    if not isinstance(residue, int) or not 0 <= residue < modulus:
        raise ValueError("Residue must be in 0,...,modulus-1")
    poly = trim(poly)
    degree = len(poly) - 1
    result = (Q(0),)
    for k in range(degree + 1):
        if k % modulus != residue:
            continue
        candidate = poly
        for j in range(degree + 1):
            if j != k:
                candidate = scale(
                    add(newton_degree_operator(candidate),scale(candidate, -j)),
                    Q(1, k-j))
        result = add(result, candidate)
    return result


def image_count_histogram(n, codomain):
    """Independent exhaustive enumeration of functions [n] -> [codomain].

    For n=0, the empty function is counted once, even for empty codomain.
    No Stirling recurrence, Newton transform or roots of unity is consulted.
    """
    if type(n) is not int or type(codomain) is not int or n < 0 or codomain < 0:
        raise ValueError("n and codomain must be nonnegative integers")
    counts = [0] * (n+1)
    for image in product(range(codomain), repeat=n):
        counts[len(set(image))] += 1
    return tuple(counts)


def series_product_truncated(a, b, degree):
    out = [Q(0)] * (degree + 1)
    for i, value in enumerate(a):
        for j, other in enumerate(b):
            if i + j <= degree:
                out[i+j] += value * other
    return tuple(out)


def packet_egf_coefficients(x, modulus, residue, degree):
    """[t^n] of sum_{k congruent residue} binom(x,k)*(exp(t)-1)^k.

    Formal power series, with rational x; no evaluation at complex roots.
    """
    if not isinstance(modulus, int) or modulus < 2:
        raise ValueError("Require integer modulus at least two")
    if not isinstance(residue, int) or not 0 <= residue < modulus:
        raise ValueError("Residue must be in 0,...,modulus-1")
    if type(degree) is not int or degree < 0:
        raise ValueError("Degree must be a nonnegative integer")
    x = Q(x)
    u = (Q(0),) + tuple(Q(1, factorial(k)) for k in range(1, degree+1))
    power_u = (Q(1),) + (Q(0),)*degree
    result = [Q(0)]*(degree+1)
    for k in range(degree+1):
        if k % modulus == residue:
            weight = evaluate(falling(k), x) / factorial(k)
            for n in range(degree+1):
                result[n] += weight*power_u[n]
        power_u = series_product_truncated(power_u,u,degree)
    return tuple(result)


def example_row():
    row = stirling_second(5)[5]
    polynomial = power(5)
    pieces = tuple(project_newton(polynomial, 3, r) for r in range(3))
    return row, polynomial, pieces


def check():
    counts = {}

    def verify(cond, category, reason):
        if not cond:
            raise AssertionError(category + ": " + reason)
        counts[category] = counts.get(category, 0) + 1

    row, p, packets = example_row()
    verify(row == ROW_FIVE, "anchor", "Stirling fifth row")
    verify(to_newton(p) == tuple(map(Q, ROW_FIVE)), "anchor", "Newton fifth row")
    verify(from_newton(ROW_FIVE) == p, "anchor", "recover x^5")
    verify(tuple(evaluate(a, 4) for a in packets) == (600, 244, 180),
           "anchor", "three exact packet values")
    verify(sum(evaluate(a, 4) for a in packets) == 1024,
           "anchor", "600+244+180=4^5")
    verify(tuple(evaluate(delta(a), 4) for a in packets) == (900, 961, 240),
           "anchor", "difference packet values")
    verify(sum(evaluate(delta(a), 4) for a in packets) == 2101,
           "anchor", "5^5-4^5")
    verify(evaluate(naive_power_project(p, 3, 2), 4) == 1024,
           "anchor", "incorrect raw-degree filter")
    verify(evaluate(packets[2], 4) == 180, "anchor", "correct transferred filter")
    verify(star(power(1), power(1)) == falling(2),
           "anchor", "star multiplication on first-order coordinates")
    verify(multiply(power(1), power(1)) != star(power(1), power(1)),
           "anchor", "Phi does not preserve ordinary products")
    verify(delta(power(2)) == (Q(1), Q(2)),
           "anchor", "finite-difference Leibniz obstruction")

    second, first = stirling_second(MAX_DEGREE), signed_stirling_first(MAX_DEGREE)
    for n in range(MAX_DEGREE + 1):
        recovered = to_newton(power(n))
        for k in range(n+1):
            verify(recovered[k] == second[n][k], "stirling",
                   f"independent difference triangle n={n},k={k}")
            verify(falling(k)[0] == int(k == 0), "stirling",
                   f"falling zero coefficient k={k}")
        for k in range(n+1):
            verify(sum(first[n][j] * second[j][k] for j in range(k, n+1))
                   == int(n == k), "stirling", f"inverse first*second {n},{k}")
            verify(sum(second[n][j] * first[j][k] for j in range(k, n+1))
                   == int(n == k), "stirling", f"inverse second*first {n},{k}")
        verify(from_newton(recovered) == power(n), "stirling",
               f"Newton roundtrip x^{n}")
        verify(falling(n) == tuple(map(Q, first[n])), "stirling",
               f"signed first-kind polynomial n={n}")

    sample_polys = [power(i) for i in range(MAX_DEGREE+1)]
    sample_polys += [(Q(2),Q(-3),Q(0),Q(5)), (Q(1,2),Q(0),Q(-4),Q(1),Q(2))]
    for poly in sample_polys:
        verify(from_newton(to_newton(poly)) == trim(poly),
               "roundtrip", "polynomial Newton roundtrip")
        for modulus in range(2,7):
            pieces = [project_newton(poly, modulus, r) for r in range(modulus)]
            whole = (Q(0),)
            for part in pieces:
                whole = add(whole, part)
            verify(whole == trim(poly), "projection", "complete residue family")
            for r in range(modulus):
                verify(project_newton(pieces[r], modulus, r) == pieces[r],
                       "projection", "idempotent")
                verify(project_newton(delta(pieces[r]), modulus,(r-1)%modulus)
                       == delta(pieces[r]), "difference",
                       "Delta Q_r = Q_(r-1) Delta")
                verify(delta(pieces[r]) ==
                       project_newton(delta(poly), modulus,(r-1)%modulus),
                       "difference", "strong differential transfer")
                for j in range(modulus):
                    if r != j:
                        verify(project_newton(pieces[r], modulus, j) == (Q(0),),
                               "projection", "pairwise annihilation")
                verify(trace_character_selector(modulus,r,r)==1,
                       "fourier", "character self-sum")
            verify(delta(poly) ==
                   from_newton(shift_newton_derivative(to_newton(poly))),
                   "difference", "Delta = Phi D Phi inverse")
            for k in range(len(poly)):
                for r in range(modulus):
                    verify(trace_character_selector(modulus,k,r) ==
                           int(k % modulus == r), "fourier",
                           "cyclic trace equals roots-of-unity average")
            for factor in (2,3):
                refined=modulus*factor
                for r in range(modulus):
                    children=(Q(0),)
                    for q in range(factor):
                        children=add(children,project_newton(poly,refined,r+modulus*q))
                    verify(children==pieces[r],"refinement",
                           "parent equals disjoint residue children")
    # A second, *independent* interpretation: count actual functions by
    # the number of different labels in their image, without using S(n,k).
    verify(image_count_histogram(5,4)==(0,4,180,600,240,0),
           "enumeration","all 1,024 functions [5] -> [4] by image size")
    for codomain in range(5):
        for n in range(7):
            observed=image_count_histogram(n,codomain)
            verify(sum(observed)==codomain**n,"enumeration",
                   "all functions counted, including the empty function")
            for k in range(n+1):
                expected=second[n][k]*evaluate(falling(k),codomain)
                verify(observed[k]==expected,"enumeration",
                       "independent image enumeration vs falling Stirling count")

    # The finite-difference number operator N=x*(I-E^{-1}) has eigenvectors
    # (x)_(k) with eigenvalues k. A finite degree cutoff makes its spectral
    # projectors rational Lagrange polynomials in N, no roots needed.
    for k in range(MAX_DEGREE+1):
        verify(newton_degree_operator(falling(k))==scale(falling(k),k),
               "spectral","falling factorial eigenvalue")
    verify(newton_degree_operator(power(2))==(Q(0),Q(-1),Q(2)),
           "spectral","N x^2=2x^2-x, not ordinary Euler derivative")
    for polynomial in sample_polys:
        verify(add(newton_degree_operator(delta(polynomial)),
                   scale(delta(newton_degree_operator(polynomial)),-1))
                   ==scale(delta(polynomial),-1),"spectral",
               "[N,Delta] = -Delta")
    for n in range(7):
        for modulus in (2,3,4,5):
            for r in range(modulus):
                verify(spectral_project_newton(power(n),modulus,r)
                       ==project_newton(power(n),modulus,r),
                       "spectral","spectral Lagrange projector equals conjugation")

    # A third independent route via the EGF of functions with image size
    # in a specified residue class. Compare all formal t coefficients.
    for x in (Q(0),Q(1),Q(4),Q(1,2),Q(-3,2)):
        for modulus in (2,3,4):
            egfs=[packet_egf_coefficients(x,modulus,r,MAX_DEGREE)
                  for r in range(modulus)]
            for n in range(MAX_DEGREE+1):
                verify(sum(egfs[r][n] for r in range(modulus)) ==
                       Q(x**n,factorial(n)),"packet_egf",
                       "sum of filtered EGFs is exp(x*t)")
                for r in range(modulus):
                    verify(egfs[r][n] ==
                           Q(evaluate(project_newton(power(n),modulus,r),x),
                             factorial(n)),"packet_egf",
                           "EGF coefficients reproduce transported projection")
    verify(tuple(packet_egf_coefficients(4,3,r,5)[5]*factorial(5)
                 for r in range(3))==(600,244,180),
           "packet_egf","fifth EGF coefficient matches image partition")

    # All entries of Q in the ordinary-power basis, computed independently
    # from signed Stirling and the second-kind triangle.
    for degree in range(0,7):
        for modulus in (2,3,4,5):
            for r in range(modulus):
                for j in range(degree+1):
                    projected=project_newton(power(j),modulus,r)
                    for i in range(degree+1):
                        actual=projected[i] if i<len(projected) else Q(0)
                        expected=sum(first[k][i]*second[j][k]
                                     for k in range(i,j+1) if k%modulus==r)
                        verify(actual==expected,"matrix",
                               "Q=M diag_r M^-1 in monomial coordinates")

    examples=[
        (power(1),power(1)),
        ((Q(1),Q(2),Q(1)),(Q(3),Q(-1),Q(0),Q(1))),
        ((Q(-2),Q(1),Q(0),Q(3)),(Q(2),Q(1),Q(-1))),
    ]
    for f,g in examples:
        verify(to_newton(star(f,g)) ==
               trim(tuple(sum(
                    to_newton(f)[i]*to_newton(g)[k-i]
                    for i in range(len(to_newton(f)))
                    if 0<=k-i<len(to_newton(g)))
                    for k in range(len(to_newton(f))+len(to_newton(g))-1))),
               "star","Newton multiplication law")
        verify(delta(star(f,g)) ==
               add(star(delta(f),g),star(f,delta(g))),
               "star","Delta is star derivation")
        # The ordinary discrete Leibniz rule has a shifted first factor.
        verify(delta(multiply(f,g)) ==
               add(multiply(delta(f),g),
                   multiply(shift(f),delta(g))),
               "star","correct shifted ordinary Leibniz rule")
        for m in (2,3,4):
            for r in range(m):
                right=(Q(0),)
                for a in range(m):
                    right=add(right,star(project_newton(f,m,a),
                        project_newton(g,m,(r-a)%m)))
                verify(project_newton(star(f,g),m,r)==right,
                       "star","cyclic packet multiplication")
    for bad in (0,1,-2,2.5):
        try:
            project_newton(p,bad,0)
        except ValueError:
            verify(True,"boundaries","reject invalid modulus")
        else:
            verify(False,"boundaries","invalid modulus accepted")
    for bad in (-1,3,1.5):
        try:
            project_newton(p,3,bad)
        except ValueError:
            verify(True,"boundaries","reject invalid residue")
        else:
            verify(False,"boundaries","invalid residue accepted")
    return counts


def svg_diagram():
    """Accessible, vector-only illustration generated from the same exact data."""
    row, poly, packets = example_row()
    values = [int(evaluate(p,4)) for p in packets]
    pieces = ["25(x)_3", "(x)_1 + 10(x)_4", "15(x)_2 + (x)_5"]
    fills = ["#d4f1e8","#e0e9ff","#fff0d9"]
    strokes = ["#156b5b","#365d9d","#9c5816"]
    out=[
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="580" viewBox="0 0 1080 580" role="img" aria-labelledby="title desc">',
        '<title id="title">Root of unity projection transported into falling factorial coordinates</title>',
        '<desc id="desc">The fifth Touchard polynomial with coefficients 1,15,25,10,1 is projected by degree modulo three. After falling factorial transport, packet values at x=4 are 600, 244 and 180. They sum exactly to 1024. A degree-five raw-power filter alone gives a different, incorrect packet assignment.</desc>',
        '<rect width="1080" height="580" fill="#fff"/>',
        '<text x="40" y="51" font-family="sans-serif" font-size="27" font-weight="700" fill="#16382f">One polynomial, three residue packets, exact recovery</text>',
        '<text x="40" y="84" font-family="sans-serif" font-size="17" fill="#52665e">T5(z) = z + 15z^2 + 25z^3 + 10z^4 + z^5  |  project degrees modulo 3</text>',
        '<rect x="40" y="113" width="1000" height="67" rx="12" fill="#f1f5f4"/>',
        '<text x="60" y="143" font-family="sans-serif" font-size="17" font-weight="600" fill="#16382f">Linear coordinate transport</text>',
        '<text x="60" y="164" font-family="sans-serif" font-size="16" fill="#3b5a50">Phi(z^k) = x(x-1)...(x-k+1)   |   Q_r = Phi P_r Phi inverse</text>',
    ]
    for r in range(3):
        x=40+340*r
        out.extend([
            f'<rect x="{x}" y="214" width="320" height="221" rx="14" fill="{fills[r]}" stroke="{strokes[r]}" stroke-width="1.3"/>',
            f'<text x="{x+20}" y="251" font-family="sans-serif" font-size="18" font-weight="700" fill="{strokes[r]}">Residue {r} (mod 3)</text>',
            f'<text x="{x+20}" y="290" font-family="sans-serif" font-size="18" fill="#203a32">{pieces[r]}</text>',
            f'<text x="{x+20}" y="332" font-family="sans-serif" font-size="15" fill="#486259">At x = 4</text>',
            f'<text x="{x+20}" y="393" font-family="sans-serif" font-size="49" font-weight="700" fill="{strokes[r]}">{values[r]}</text>',
        ])
    out.extend([
        '<rect x="40" y="462" width="1000" height="80" rx="12" fill="#153f34"/>',
        '<text x="66" y="496" font-family="sans-serif" font-size="17" fill="#deefeb">Sum of all three transported packets</text>',
        '<text x="66" y="527" font-family="sans-serif" font-size="30" font-weight="700" fill="#fff">600 + 244 + 180 = 1024 = 4^5</text>',
        '</svg>'
    ])
    return "\n".join(out)+"\n"



def svg_image_histogram():
    """Standalone accessible SVG using independently enumerated exact counts."""
    hist = image_count_histogram(5,4)
    fills = ("#1d6855","#3b68a2","#b87321")
    result = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1020" height="550" viewBox="0 0 1020 550" role="img" aria-labelledby="title desc">',
        '<title id="title">Exact image-size histogram for functions from five inputs to four labels</title>',
        '<desc id="desc">Enumerating all 1024 functions from a five-element set to a four-element set gives 0, 4, 180, 600, 240 and 0 functions using k=0 through k=5 different labels. Grouping k modulo three gives 600, 244 and 180.</desc>',
        '<rect width="1020" height="550" fill="#fff"/>',
        '<text x="42" y="49" font-family="sans-serif" font-size="26" font-weight="700" fill="#173e32">Count actual functions by their image size</text>',
        '<text x="42" y="82" font-family="sans-serif" font-size="16" fill="#48645d">Every map from 5 inputs to 4 labels, grouped by how many distinct labels occur</text>',
        '<line x1="74" y1="421" x2="949" y2="421" stroke="#637870" stroke-width="2"/>',
    ]
    for k,value in enumerate(hist):
        x=91+k*145
        height=round(value*274/600)
        display_height=max(3,height) if value else 0
        y=421-display_height
        result.append(
            f'<rect x="{x}" y="{y}" width="84" height="{display_height}" rx="4" fill="{fills[k%3]}"/>')
        result.append(
            f'<text x="{x+42}" y="{max(115,y-12)}" text-anchor="middle" font-family="sans-serif" font-size="21" font-weight="700" fill="#203e34">{value}</text>')
        result.append(
            f'<text x="{x+42}" y="452" text-anchor="middle" font-family="sans-serif" font-size="16" fill="#48645d">k = {k}</text>')
    result.extend([
        '<text x="43" y="493" font-family="sans-serif" font-size="16" fill="#42675a">Residue 0: 600</text>',
        '<text x="375" y="493" font-family="sans-serif" font-size="16" fill="#365d91">Residue 1: 244</text>',
        '<text x="708" y="493" font-family="sans-serif" font-size="16" fill="#955c20">Residue 2: 180</text>',
        '<text x="43" y="527" font-family="sans-serif" font-size="17" font-weight="700" fill="#173e32">600 + 244 + 180 = 1024 functions</text>',
        '</svg>'
    ])
    return "\n".join(result)+"\n"


def save(directory: Path, counts):
    directory.mkdir(parents=True,exist_ok=True)
    for name in FILES:
        if (directory/name).exists():
            raise FileExistsError("Refusing to overwrite "+str(directory/name))
    second=stirling_second(MAX_DEGREE)
    with (directory/"newton-stirling.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(("n","k","stirling_second","newton_delta_k_at_zero_over_k_factorial"))
        for n in range(MAX_DEGREE+1):
            c=to_newton(power(n))
            for k in range(n+1):
                w.writerow((n,k,second[n][k],str(c[k])))
    with (directory/"image-histograms.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(("domain_size","codomain_size","distinct_image_size",
                    "enumerated_functions","stirling_falling_formula"))
        for codomain in range(5):
            for n in range(7):
                hist=image_count_histogram(n,codomain)
                for k in range(n+1):
                    w.writerow((n,codomain,k,hist[k],
                                str(second[n][k]*evaluate(falling(k),codomain))))
    with (directory/"packet-egfs.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(("codomain_parameter","modulus","residue","degree",
                    "ordinary_egf_coefficient","weighted_exact_count"))
        for r in range(3):
            series=packet_egf_coefficients(4,3,r,MAX_DEGREE)
            for n in range(MAX_DEGREE+1):
                w.writerow((4,3,r,n,str(series[n]),
                            str(series[n]*factorial(n))))
    with (directory/"spectral-projectors.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(("power_degree","modulus","residue",
                    "spectral_power_coefficients","conjugated_power_coefficients"))
        for n in range(7):
            for r in range(3):
                spectral=spectral_project_newton(power(n),3,r)
                conjugated=project_newton(power(n),3,r)
                w.writerow((n,3,r,";".join(map(str,spectral)),
                            ";".join(map(str,conjugated))))
    row,p,packets=example_row()
    with (directory/"packet-contributions.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(("residue","k","stirling_count","falling_4_k","contribution","character_trace"))
        for r in range(3):
            for k,c in enumerate(row):
                if k%3==r:
                    vk=evaluate(falling(k),4)
                    w.writerow((r,k,c,str(vk),str(c*vk),
                                str(trace_character_selector(3,k,r))))
    with (directory/"difference-transfer.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(("residue","packet_value_x4","delta_packet_x4",
                    "projected_delta_in_predecessor_packet_x4"))
        for r in range(3):
            w.writerow((r,str(evaluate(packets[r],4)),
                        str(evaluate(delta(packets[r]),4)),
                        str(evaluate(project_newton(delta(p),3,(r-1)%3),4))))
    with (directory/"refinement.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(("parent_modulus","parent_residue","child_modulus",
                    "child_residue","child_value_x4","parent_value_x4"))
        for r in range(3):
            for q in range(2):
                w.writerow((3,r,6,r+3*q,
                            str(evaluate(project_newton(p,6,r+3*q),4)),
                            str(evaluate(packets[r],4))))
    with (directory/"projector-matrix.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(("residue","row_monomial_degree","column_input_power",
                    "matrix_coefficient"))
        for r in range(3):
            for col in range(6):
                proj=project_newton(power(col),3,r)
                for row_number in range(6):
                    w.writerow((r,row_number,col,str(
                        proj[row_number] if row_number<len(proj) else Q(0))))
    (directory/"projection-diagram.svg").write_text(svg_diagram(),encoding="utf-8")
    (directory/"function-image-histogram.svg").write_text(svg_image_histogram(),encoding="utf-8")
    summary={
        "arithmetic":"exact integer and Fraction",
        "scope":"Polynomials over Q; finite degree and m>=2; no analytic or p-adic convergence",
        "row5":list(row),
        "newton_polynomial":"z + 15z^2 + 25z^3 + 10z^4 + z^5",
        "packet_polynomials_power_basis":[list(map(str,part)) for part in packets],
        "packet_values_at_x4":[str(evaluate(v,4)) for v in packets],
        "image_count_histogram_n5_x4":list(image_count_histogram(5,4)),
        "number_operator_on_x_squared":list(map(str,newton_degree_operator(power(2)))),
        "packet_egf_n5_x4":[str(packet_egf_coefficients(4,3,r,5)[5]*120)
                            for r in range(3)],
        "difference_values_at_x4":[str(evaluate(delta(v),4)) for v in packets],
        "reconstructed_value_at_x4":str(evaluate(p,4)),
        "naive_residue2_at_x4":str(evaluate(naive_power_project(p,3,2),4)),
        "correct_residue2_at_x4":str(evaluate(packets[2],4)),
        "star_x_x_coefficients":list(map(str,star(power(1),power(1)))),
        "checks_by_group":counts,
        "total_assertions":sum(counts.values())
    }
    (directory/"results.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,help="New destination for exact CSV, SVG and JSON")
    args=parser.parse_args()
    counts=check()
    print("Stirling row five:",ROW_FIVE)
    print("Root-of-unity packets at x=4: 600 + 244 + 180 = 1024")
    print("Finite-difference packets at x=4: 900 + 961 + 240 = 2101")
    print("Independent function-image counts: 0, 4, 180, 600, 240, 0")
    print("Spectral number operator: N=x*(I-backshift), N(x^2)=2x^2-x")
    print("Transferred projector != raw power-degree filter (180 != 1024)")
    print("PASS:",sum(counts.values()),"exact assertions")
    if args.output:
        save(args.output,counts)
        print("Exact artifacts:",args.output)


if __name__=="__main__":
    main()
