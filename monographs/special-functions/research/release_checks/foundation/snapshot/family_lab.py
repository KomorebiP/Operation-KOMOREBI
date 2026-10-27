#!/usr/bin/env python3
"""Exact family, sequence, polyphase and finite tap laboratory.

The reusable core needs only Python's standard library. All arrays use ascending
indices and exact rational arithmetic. Finite sequences are zero extended.
Analytic statements require the domain in new_results/sequence_polyphase.md.
"""
from __future__ import annotations
import argparse
import csv
from fractions import Fraction
from math import comb, factorial, lcm
import json
from pathlib import Path

Q = Fraction


def _last(last: int) -> None:
    if not isinstance(last, int) or last < 0:
        raise ValueError("last index must be a nonnegative integer")


def feedback_odd_derivatives(channels, last=12):
    """Return A_n = F^(2n+1)(0); channel tuples are (h,q,r).

    F' = 1 + sum h F(qz) F(rz), F(0)=0. Rational parameters outside
    positive contraction domains are permitted as formal coefficients only.
    """
    _last(last)
    channels = [(Q(h), Q(q), Q(r)) for h, q, r in channels]
    out = [Q(1)]
    for n in range(1, last + 1):
        out.append(sum((h * comb(2*n, 2*i+1) * q**(2*i+1)
                        * r**(2*(n-1-i)+1) * out[i] * out[n-1-i]
                        for h, q, r in channels for i in range(n)), Q(0)))
    return out


def asymmetric_odd_derivatives(q, r, last=12):
    return feedback_odd_derivatives([(1, q, r)], last)


def ordinary_taylor_coefficients(odd_derivatives):
    """Return c_n in sum c_n z^(2n+1), rather than derivative values."""
    return [Q(a, factorial(2*n+1)) for n, a in enumerate(odd_derivatives)]


def full_egf_coefficients(odd_derivatives):
    """Return a_m for F=sum a_m z^m/m!, including its zero even entries."""
    out = [Q(0)] * (2 * len(odd_derivatives))
    for n, a in enumerate(odd_derivatives):
        out[2*n+1] = Q(a)
    return out


def asymmetric_polynomials(last=8):
    """Sparse Z[q,r] for A_n; a key (u,v) means q^u r^v."""
    _last(last)
    out = [{(0, 0): 1}]
    for n in range(1, last + 1):
        p = {}
        for i in range(n):
            j = n - 1 - i
            factor = comb(2*n, 2*i+1)
            for (u, v), a in out[i].items():
                for (s, t), b in out[j].items():
                    key = (u+s+2*i+1, v+t+2*j+1)
                    p[key] = p.get(key, 0) + factor*a*b
        out.append(dict(sorted(p.items())))
    return out


def evaluate_polynomial(p, q, r):
    q, r = Q(q), Q(r)
    return sum((a*q**u*r**v for (u,v), a in p.items()), Q(0))


def section(a, base, residue):
    """EGF/OGF root-filter section, keeping original index positions."""
    if (not isinstance(base, int) or base < 1 or
            not isinstance(residue, int) or not 0 <= residue < base):
        raise ValueError("require integer base >= 1 and 0 <= residue < base")
    return [Q(x) if m % base == residue else Q(0) for m,x in enumerate(a)]


def phase_lanes(a, base):
    """Decimated coefficient arrays x_j[n]=a[base*n+j].

    The exact simple z^j X_j(z^base) reconstruction is an OGF identity.
    EGF reconstruction additionally retains the original factorial weights.
    """
    if not isinstance(base, int) or base < 1:
        raise ValueError("require integer base >= 1")
    return [[Q(x) for x in a[j::base]] for j in range(base)]


def merge_lanes(lanes, length=None):
    if not lanes:
        raise ValueError("at least one phase is required")
    base = len(lanes)
    natural = max((base*(len(lane)-1)+j+1 if lane else 0
                   for j,lane in enumerate(lanes)), default=0)
    if length is None:
        length = natural
    _last(length)
    if length < natural:
        raise ValueError("length would silently discard phase entries")
    out = [Q(0)] * length
    for j,lane in enumerate(lanes):
        for n,x in enumerate(lane):
            out[base*n+j] = Q(x)
    return out


def ordinary_taps(a, taps):
    """Zero-extended ordinary FIR convolution sum_t h_t a_(m-t)."""
    if not a or not taps:
        return []
    out = [Q(0)] * (len(a) + len(taps) - 1)
    for m,x in enumerate(a):
        for t,h in enumerate(taps):
            out[m+t] += Q(x)*Q(h)
    return out


def hurwitz_product(a, b):
    """EGF product: c_m=sum_t binom(m,t) a_t b_(m-t)."""
    if not a or not b:
        return []
    out = [Q(0)] * (len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j] += comb(i+j,i)*Q(x)*Q(y)
    return out


def derivative_shift(a, order=1):
    """EGF derivative coefficient sequence a_(m+order), truncated exactly."""
    _last(order)
    return [Q(x) for x in a[order:]]


def integral_shift(a, order=1):
    """Repeated zero-constant EGF antiderivative: zero-pad the past."""
    _last(order)
    return [Q(0)]*order + [Q(x) for x in a]


def polyphase_tap_matrix(taps, base):
    """Sparse OGF polynomials H[j][l][d] for the exact FIR phase matrix."""
    if not isinstance(base,int) or base < 1:
        raise ValueError("require integer base >= 1")
    mat = [[{} for _ in range(base)] for _ in range(base)]
    for l in range(base):
        for t,h in enumerate(taps):
            j = (t+l) % base
            d = (t+l-j) // base
            if Q(h):
                mat[j][l][d] = mat[j][l].get(d,Q(0)) + Q(h)
    return mat


def apply_polyphase_matrix(lanes, matrix, output_length):
    """Return output phases with the specified original-sequence length."""
    _last(output_length)
    base = len(lanes)
    if base < 1:
        raise ValueError("at least one phase is required")
    if len(matrix) != base or any(len(row) != base for row in matrix):
        raise ValueError("phase matrix dimensions disagree")
    out = [[Q(0)]*len(range(j,output_length,base)) for j in range(base)]
    for j in range(base):
        for l in range(base):
            for d,h in matrix[j][l].items():
                if not isinstance(d,int) or d < 0:
                    raise ValueError("phase polynomial exponents must be nonnegative integers")
                for n,x in enumerate(lanes[l]):
                    if n+d < len(out[j]):
                        out[j][n+d] += Q(h)*Q(x)
                    elif h*x:
                        raise ValueError("output length would discard a nonzero coefficient")
    return out


def catalog(last=12):
    """Explicit formulas, exact samples and scope; no OEIS priority claim."""
    pairs = [
        ("tangent", "1", "1", "Known tan(z); positive-contraction theorem does not apply."),
        ("linear", "0", "1", "Known z, a degenerate boundary."),
        ("hyperbolic_tangent", "1", "-1", "Known tanh(z), formal signed boundary."),
        *[(f"formal_{q}_{r}",str(q),str(r),"Positive integer formal specialization; radius of convergence zero.")
          for q,r in [(1,2),(1,3),(1,4),(2,2),(2,3),(2,4),(3,3),(3,4)]],
        ("scaled_sinh", "1/2", "1/2", "Known sqrt(2)*sinh(z/sqrt(2)); entire."),
        ("asym_1_4_3_4", "1/4", "3/4", "Positive contractions; entire, order 1."),
        ("asym_1_3_2_3", "1/3", "2/3", "Positive contractions; entire, order 1."),
        ("asym_1_3_1_2", "1/3", "1/2", "Positive contractions; entire; 3^(-rho)+2^(-rho)=1."),
        ("entire_infinite_order_boundary", "1/2", "1", "Positive edge case; entire of infinite order; linear ODE bootstrap."),
    ]
    rows = []
    for name,q,r,scope in pairs:
        channels = [(Q(1),Q(q),Q(r))]
        rows.append(_catalog_row(name, channels, last, scope))
    rows.append(_catalog_row("bank_equal_weak_fast",
        [(Q(1,2),Q(1,4),Q(1,4)),(Q(1,2),Q(3,4),Q(3,4))],last,
        "Positive normalized feedback bank; entire; order log(2)/log(4/3)."))
    rows.append(_catalog_row("bank_equal_asymmetric",
        [(Q(1,2),Q(1,3),Q(2,3)),(Q(1,2),Q(1,4),Q(3,4))],last,
        "Positive normalized feedback bank; entire; order 1."))
    return {"contract":"SF-DISCOVERY-100", "normalization":"A_n=F^(2n+1)(0), n starts at 0",
            "last_index":last, "catalog_count":len(rows),
            "oeis_status":"Exact sequence candidates for lookup; no search, accession or novelty asserted by this file.",
            "rows":rows}


def _catalog_row(name, channels, last, scope):
    a = feedback_odd_derivatives(channels,last)
    scale = lcm(*(x.denominator for row in channels for x in row[1:]))
    weight_scale = lcm(*(row[0].denominator for row in channels))
    multipliers = [weight_scale**n * scale**(n*(n+1)) for n in range(last+1)]
    cleared = [x*d for x,d in zip(a,multipliers)]
    return {"id":name,"channels":[[str(x) for x in row] for row in channels],
            "scope":scope, "A_n":[str(x) for x in a],
            "c_n":[str(x) for x in ordinary_taylor_coefficients(a)],
            "integer_samples":all(x.denominator == 1 for x in a),
            "clearing_scales":{"contractions_D":scale,"weights_H":weight_scale},
            "denominator_multiplier":[str(x) for x in multipliers],
            "cleared_A_n":[str(x) for x in cleared],
            "clearing_note":"H^n D^(n(n+1)) A_n is an integer by the degree bound; this normalization is not minimal."}


def export_catalog(outdir,last=12):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    data=catalog(last)
    (outdir/"sequence_catalog.json").write_text(json.dumps(data,indent=2)+"\n")
    with (outdir/"sequence_catalog.csv").open("w",newline="") as f:
        writer=csv.writer(f);writer.writerow(["id","n","derivative_index","A_n","c_n","denominator_multiplier","cleared_A_n","scope"])
        for row in data["rows"]:
            for n,(a,c) in enumerate(zip(row["A_n"],row["c_n"])):
                writer.writerow([row["id"],n,2*n+1,a,c,row["denominator_multiplier"][n],row["cleared_A_n"][n],row["scope"]])
    return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest="command",required=True)
    cat=commands.add_parser("catalog");cat.add_argument("--n",type=int,default=12)
    cat.add_argument("--output-dir",default="examples")
    seq=commands.add_parser("coefficients");seq.add_argument("--q",required=True)
    seq.add_argument("--r",required=True);seq.add_argument("--n",type=int,default=8)
    args=parser.parse_args()
    if args.command == "catalog":
        d=export_catalog(args.output_dir,args.n)
        print(json.dumps({"catalog_count":d["catalog_count"],"last_index":d["last_index"]}))
    else:
        a=asymmetric_odd_derivatives(args.q,args.r,args.n)
        print(json.dumps({"A_n":[str(x) for x in a],
                          "c_n":[str(x) for x in ordinary_taylor_coefficients(a)]},indent=2))


if __name__ == "__main__":
    main()
