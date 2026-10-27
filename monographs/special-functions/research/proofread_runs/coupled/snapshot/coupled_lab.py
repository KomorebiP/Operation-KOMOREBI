#!/usr/bin/env python3
"""Exact coupled feedback laboratory (Python standard library only).

U'=1+U(qz)V(rz), V'=1+U(az)V(bz), U(0)=V(0)=0.
Arrays A_n, B_n are derivatives of order 2n+1, beginning with A_0=B_0=1.
Coefficient generation is formal for arbitrary rational scales. Analytic
evaluation certificates require all four scales strictly between zero and one.
"""
from __future__ import annotations
import argparse
import csv
from fractions import Fraction as Q
import json
from math import comb, factorial, isfinite, lcm, sqrt
from pathlib import Path
from family_lab import (ordinary_taylor_coefficients, full_egf_coefficients,
                        phase_lanes, merge_lanes, polyphase_tap_matrix,
                        apply_polyphase_matrix, ordinary_taps)


def _index(n):
    if type(n) is not int or n < 0:
        raise ValueError("last index must be a nonnegative integer")


def scales(q, r, a, b, *, contraction=False):
    p = tuple(Q(x) for x in (q, r, a, b))
    if contraction and not all(0 < x < 1 for x in p):
        raise ValueError("analytic certificates require 0 < q,r,a,b < 1")
    return p


def coupled_odd_derivatives(q, r, a, b, last=12):
    """Return exact rational arrays (A_n,B_n), n=0,...,last."""
    _index(last)
    q, r, a, b = scales(q, r, a, b)
    u, v = [Q(1)], [Q(1)]
    for n in range(1, last+1):
        products = [(comb(2*n, 2*i+1)*u[i]*v[n-1-i], 2*i+1,
                     2*(n-1-i)+1) for i in range(n)]
        u.append(sum((c*q**i*r**j for c,i,j in products), Q(0)))
        v.append(sum((c*a**i*b**j for c,i,j in products), Q(0)))
    return u, v


def cleared_derivatives(q, r, a, b, last=12):
    """D^(n(n+1)) clears both derivative arrays; not a minimal clearing."""
    p = scales(q, r, a, b)
    u, v = coupled_odd_derivatives(*p, last=last)
    d = lcm(*(x.denominator for x in p))
    multipliers = [d**(n*(n+1)) for n in range(last+1)]
    return d, multipliers, ([x*m for x,m in zip(u,multipliers)],
                           [x*m for x,m in zip(v,multipliers)])


def disk_majorant(q, r, a, b, radius, *, max_steps=20, max_bits=2_000_000):
    """An exact upper bound for max(|U|,|V|) on |z|<=radius.

    For x<1, positive coefficient domination by z/(1-z^2) gives B(x).
    Then M(x)<=x*(1+M(Qmax*x)^2) bootstraps the disk bound. Integer
    resource guards raise explicitly instead of weakening the certificate.
    """
    p = scales(q, r, a, b, contraction=True)
    radius = Q(radius)
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    if radius == 0:
        return Q(0)
    _index(max_steps)
    if type(max_bits) is not int or max_bits < 1:
        raise ValueError("max_bits must be a positive integer")
    largest = max(p)
    ladder, x = [], radius
    while x >= 1:
        if len(ladder) >= max_steps:
            raise ValueError("majorant recursion exceeds max_steps")
        ladder.append(x)
        x *= largest
    bound = x/(1-x*x)
    for x in reversed(ladder):
        bound = x*(1+bound*bound)
        if max(bound.numerator.bit_length(), bound.denominator.bit_length()) > max_bits:
            raise ValueError("majorant exact rational exceeds max_bits")
    return bound


def certified_evaluation(q, r, a, b, x, last=24, outer_radius=None):
    """Exact interval endpoints for U(x),V(x) at rational x>=0.

    The error also bounds the truncated odd series throughout |z|<=x.
    Tail <= B(S)*(x/S)^(2*last+3), where S>x and B(S) is disk_majorant.
    This is an enclosure, not a floating point interval implementation.
    """
    _index(last)
    p = scales(q, r, a, b, contraction=True)
    x = Q(x)
    if x < 0:
        raise ValueError("certified real evaluation requires x>=0")
    s = Q(outer_radius) if outer_radius is not None else max(Q(1),2*x)
    if s <= x:
        raise ValueError("outer radius must be strictly greater than x")
    derivatives = coupled_odd_derivatives(*p,last=last)
    partial = [sum((c*x**(2*n+1) for n,c in enumerate(
        ordinary_taylor_coefficients(row))), Q(0)) for row in derivatives]
    majorant = disk_majorant(*p,s)
    tail = majorant*(x/s)**(2*last+3)
    return {"x":x,"last_index":last,"outer_radius":s,"majorant":majorant,
            "tail_bound":tail,"U":(partial[0],partial[0]+tail),
            "V":(partial[1],partial[1]+tail)}


def pf_spectral_radius(q, r, a, b, exponent):
    """Floating point Perron eigenvalue of [[q^t,r^t],[a^t,b^t]]."""
    p = tuple(float(x) for x in (q,r,a,b))
    t = float(exponent)
    if not all(isfinite(x) and 0 < x < 1 for x in p):
        raise ValueError("PF calculation requires finite strict contractions")
    if not isfinite(t) or t < 0:
        raise ValueError("exponent must be finite and nonnegative")
    q,r,a,b = (x**t for x in p)
    return (q+b+sqrt((q-b)**2+4*r*a))/2


def pf_order(q, r, a, b, tolerance=1e-12):
    """Numerical root bracket for spectral radius = 1; no interval proof."""
    if not isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance must be finite and positive")
    p = tuple(float(x) for x in (q,r,a,b))
    pf_spectral_radius(*p,0)
    low, high = 0.0, 1.0
    while pf_spectral_radius(*p,high) > 1:
        high *= 2
        if not isfinite(high):
            raise ValueError("floating point exponent bracket overflow")
    for _ in range(200):
        if high-low <= tolerance*max(1.0,high):
            break
        mid = (low+high)/2
        if pf_spectral_radius(*p,mid) > 1:
            low=mid
        else:
            high=mid
    return {"rho":(low+high)/2,"bracket":[low,high],
            "spectral_residual":pf_spectral_radius(*p,(low+high)/2)-1,
            "arithmetic":"IEEE 754 double, not a rigorous interval bracket"}


def catalog(last=10):
    rows=[]
    cases=[("unequal_weights_order_one",("1/5","2/5","3/5","7/10"),
            "Positive contractions. Exact order-one PF identity has right vector (1/2,1)."),
           ("generic_contractions",("1/3","2/3","1/2","3/4"),
            "Positive contractions. PF root is computed numerically."),
           ("scalar_sinh",("1/2",)*4,
            "Known U=V=sqrt(2)*sinh(z/sqrt(2))."),
           ("scalar_asymmetric",("1/3","2/3","1/3","2/3"),
            "Identical equations force U=V=T_(1/3,2/3)."),
           ("formal_integer_1_2_2_3",("1","2","2","3"),
            "Formal integer specialization outside the analytic contraction domain. No convergence claim."),
           ("formal_signed",("-1","2","1","-2"),
            "Formal signed specialization. Positivity and contraction theorems do not apply."),
           ("tangent_anchor",("1",)*4,
            "Known U=V=tan(z), meromorphic, outside the contraction domain.")]
    for name,p,scope in cases:
        u,v=coupled_odd_derivatives(*p,last=last)
        d,m,cleared=cleared_derivatives(*p,last=last)
        rows.append({"id":name,"scales":list(p),"scope":scope,
                     "U_derivatives":[str(x) for x in u],
                     "V_derivatives":[str(x) for x in v],
                     "denominator_D":d,"multipliers":[str(x) for x in m],
                     "cleared_U":[str(x) for x in cleared[0]],
                     "cleared_V":[str(x) for x in cleared[1]]})
    return {"checkpoint":"SF-DISCOVERY-110","normalization":"A_n=U^(2n+1)(0), B_n=V^(2n+1)(0)",
            "last_index":last,"rows":rows,
            "oeis_status":"No accession or historical novelty asserted."}


def export_catalog(output_dir,last=10):
    target=Path(output_dir);target.mkdir(parents=True,exist_ok=True)
    data=catalog(last)
    (target/"coupled_catalog.json").write_text(json.dumps(data,indent=2)+"\n")
    with (target/"coupled_catalog.csv").open("w",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(["id","n","U_derivative","V_derivative","cleared_U","cleared_V","scope"])
        for row in data["rows"]:
            for n in range(last+1):
                writer.writerow([row["id"],n,row["U_derivatives"][n],row["V_derivatives"][n],
                                 row["cleared_U"][n],row["cleared_V"][n],row["scope"]])
    return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest="command",required=True)
    cat=commands.add_parser("catalog");cat.add_argument("--n",type=int,default=10)
    cat.add_argument("--output-dir",default="examples")
    coefficients=commands.add_parser("coefficients")
    for name in ("q","r","a","b"):coefficients.add_argument("--"+name,required=True)
    coefficients.add_argument("--n",type=int,default=8)
    args=parser.parse_args()
    if args.command=="catalog":
        data=export_catalog(args.output_dir,args.n)
        print(json.dumps({"catalog_rows":len(data["rows"]),"last_index":args.n}))
    else:
        u,v=coupled_odd_derivatives(args.q,args.r,args.a,args.b,args.n)
        print(json.dumps({"U_derivatives":[str(x) for x in u],"V_derivatives":[str(x) for x in v]},indent=2))


if __name__=="__main__":main()
