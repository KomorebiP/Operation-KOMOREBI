#!/usr/bin/env python3
"""Stirling, Bell and Fubini numbers: exact triangular and reciprocal transfers.

The calculations use Python's standard library and exact integer/Fraction
arithmetic. The published examples are classical identities, not new theorems.
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
DEGREE = 10
REFERENCE_ROW = (0, 1, 15, 25, 10, 1)
ALTERNATIVE_ROW_4 = (0, 5, 2, 7, 1)


def stirling_second(max_n):
    rows = [(1,)]
    for n in range(1, max_n + 1):
        prev = rows[-1]
        rows.append(tuple((prev[k-1] if 0 <= k-1 < n else 0)
                          + k*(prev[k] if k < n else 0)
                          for k in range(n+1)))
    return tuple(rows)


def signed_stirling_first(max_n):
    """Coefficients of x(x-1)...(x-n+1), in ascending powers of x."""
    rows = [(1,)]
    for n in range(1, max_n + 1):
        prev = rows[-1]
        rows.append(tuple((prev[k-1] if 0 <= k-1 < n else 0)
                          - (n-1)*(prev[k] if k < n else 0)
                          for k in range(n+1)))
    return tuple(rows)


def lower_apply(rows, weights):
    weights = tuple(weights)
    return tuple(sum(row[k]*weights[k] for k in range(n+1))
                 for n, row in enumerate(rows))


def bell_fubini(rows):
    length = len(rows)
    bell = lower_apply(rows, (1,)*length)
    ordered = lower_apply(rows, tuple(factorial(k) for k in range(length)))
    return bell, ordered


def series_product(a, b):
    if len(a) != len(b):
        raise ValueError("Truncated series require equal declared degree")
    return tuple(sum((a[j]*b[n-j] for j in range(n+1)), Q(0))
                 for n in range(len(a)))


def series_reciprocal(a):
    if not a or a[0] != 1:
        raise ValueError("Reciprocal series requires constant term exactly one")
    out = [Q(1)]
    for n in range(1, len(a)):
        out.append(-sum((a[j]*out[n-j] for j in range(1,n+1)), Q(0)))
    return tuple(out)


def egf_coefficients(values):
    return tuple(Q(v, factorial(n)) for n, v in enumerate(values))


def exponential_series_of_expm1(degree):
    """Formal exp(exp(t)-1) as sum_{k=0}^N (exp(t)-1)^k/k!."""
    unit = (Q(1),) + (Q(0),)*degree
    u = (Q(0),) + tuple(Q(1, factorial(j)) for j in range(1, degree+1))
    result = [Q(0)] * (degree+1)
    power = unit
    for k in range(degree+1):
        for n in range(degree+1):
            result[n] += power[n]/factorial(k)
        power = series_product(power, u)
    return tuple(result)


def ordered_reciprocal_series(degree):
    """1 / (2-exp(t)) as a formal power series about t=0."""
    denominator = (Q(1),) + tuple(-Q(1,factorial(n))
                                  for n in range(1,degree+1))
    return series_reciprocal(denominator)


def packet(values, modulus, residue):
    if modulus < 1 or not 0 <= residue < modulus:
        raise ValueError("Invalid residue packet")
    return tuple(v if n%modulus == residue else Q(0)
                 for n,v in enumerate(values))


def bell_recurrence(degree):
    out = [1]
    for n in range(degree):
        out.append(sum(comb(n,k)*out[k] for k in range(n+1)))
    return tuple(out)


def fubini_recurrence(degree):
    out=[1]
    for n in range(1,degree+1):
        out.append(sum(comb(n,j)*out[n-j] for j in range(1,n+1)))
    return tuple(out)


def direct_set_partition_histogram(n):
    """Independent restricted-growth-string enumeration (small n only)."""
    if n==0:
        return (1,)
    totals=[0]*(n+1)
    def visit(length, highest):
        if length==n:
            totals[highest+1]+=1
            return
        for label in range(highest+2):
            visit(length+1, max(highest,label))
    visit(0,-1)
    return tuple(totals)


def surjection_count(n,k):
    """Independent inclusion-exclusion count of maps onto k labelled blocks."""
    return sum((-1)**j * comb(k,j) * (k-j)**n for j in range(k+1))


def weighted_sum(row):
    return sum(factorial(k)*c for k,c in enumerate(row))


def test_cases():
    counters={}
    def verify(condition, group, explanation):
        if not condition:
            raise AssertionError(f"{group}: {explanation}")
        counters[group]=counters.get(group,0)+1

    S=stirling_second(DEGREE)
    s=signed_stirling_first(DEGREE)
    bell,ordered=bell_fubini(S)
    verify(S[5] == REFERENCE_ROW,"reference","Stirling row at n=5")
    verify(tuple(factorial(k)*S[5][k] for k in range(6))
           == (0,1,30,150,240,120),"reference","Factorial-weighted row")
    verify(bell[5]==52 and ordered[5]==541,"reference","Two row sums")
    verify(bell[4]==15 and ordered[4]==75,"reference","n=4 Bell/Fubini values")
    verify(s[5]==(0,24,-50,35,-10,1),"reference","Signed inverse row")
    verify(sum(s[5][k]*ordered[k] for k in range(6))==120,
           "reference","Inverted Fubini family yields 5!")
    verify(sum(s[5][k]*bell[k] for k in range(6))==1,
           "reference","Inverted Bell family yields a constant input")
    verify(bell[:9]==(1,1,2,5,15,52,203,877,4140),
           "reference","First nine Bell numbers")
    verify(ordered[:9]==(1,1,3,13,75,541,4683,47293,545835),
           "reference","First nine ordered Bell numbers")
    verify(tuple(sum(S[4]) for _ in range(1))==(15,),
           "reference","Original fourth row count")
    verify(tuple(S[4])==(0,1,7,6,1),"reference","Original n=4 coordinates")
    verify(sum(ALTERNATIVE_ROW_4)==bell[4]
           and weighted_sum(ALTERNATIVE_ROW_4)==ordered[4],
           "reference","Both observed summaries agree at n=4")
    verify(ALTERNATIVE_ROW_4!=S[4] and
           all(v>=0 for v in ALTERNATIVE_ROW_4),
           "reference","Different nonnegative integral coordinate profiles")
    verify(ordered[5]==375+130+30+5+1,"reference","Ordered Bell binomial recurrence n=5")

    # Independent finite combinatorial enumeration does not call S recurrence.
    for n in range(0,9):
        histogram=direct_set_partition_histogram(n)
        for k in range(n+1):
            verify(histogram[k]==S[n][k],
                   "partitions",f"Enumerated partitions n={n}, k={k}")
    # Labelled surjections: onto maps are not the same as unordered partitions.
    for n in range(0,8):
        for k in range(n+1):
            verify(surjection_count(n,k)==factorial(k)*S[n][k],
                   "surjections",f"Inclusion-exclusion n={n}, k={k}")

    for n in range(0,DEGREE+1):
        verify(S[n][n]==1 and s[n][n]==1,"triangular","Unit diagonal")
        verify(sum(s[n][k]*bell[k] for k in range(n+1))==1,
               "triangular","Bell-to-constant exact inverse")
        verify(sum(s[n][k]*ordered[k] for k in range(n+1))==factorial(n),
               "triangular","Fubini-to-factorial exact inverse")
        for k in range(n+1):
            verify(sum(s[n][j]*S[j][k] for j in range(k,n+1))
                   == int(n==k),"triangular","Exact product s*S=I")
            verify(sum(S[n][j]*s[j][k] for j in range(k,n+1))
                   == int(n==k),"triangular","Exact product S*s=I")

    be=egf_coefficients(bell)
    fe=egf_coefficients(ordered)
    eb=exponential_series_of_expm1(DEGREE)
    rf=ordered_reciprocal_series(DEGREE)
    u=(Q(0),)+tuple(Q(1,factorial(j)) for j in range(1,DEGREE+1))
    for n in range(DEGREE+1):
        verify(be[n]==eb[n],"generating","exp(exp(t)-1) coefficient")
        verify(fe[n]==rf[n],"generating","1/(2-exp(t)) coefficient")
        verify(bell[n]==bell_recurrence(DEGREE)[n],
               "generating","Independent Bell recurrence")
        verify(ordered[n]==fubini_recurrence(DEGREE)[n],
               "generating","Independent ordered Bell recurrence")
    for k in range(DEGREE+1):
        power=(Q(1),)+(Q(0),)*DEGREE
        for _ in range(k):
            power=series_product(power,u)
        for n in range(k,DEGREE+1):
            verify(power[n]/factorial(k)==Q(S[n][k],factorial(n)),
                   "generating","Fixed k partition EGF")

    # Even/odd packets of F and U obey an exact 2x2 convolutional transfer.
    ue,uo=packet(u,2,0),packet(u,2,1)
    even,odd=packet(fe,2,0),packet(fe,2,1)
    lhs_even=series_product(ue,even)
    cross_even=series_product(uo,odd)
    lhs_odd=series_product(ue,odd)
    cross_odd=series_product(uo,even)
    for n in range(DEGREE+1):
        verify(even[n] == (int(n==0)+lhs_even[n]+cross_even[n]),
               "packets","Even reciprocal packet transfer")
        verify(odd[n] == lhs_odd[n]+cross_odd[n],
               "packets","Odd reciprocal packet transfer")
        verify(even[n]+odd[n]==fe[n],"packets","Two packets reconstruct")
        verify(sum(packet(fe,3,r)[n] for r in range(3))==fe[n],
               "packets","Three packets reconstruct")
    verify(sum(comb(5,j)*ordered[5-j] for j in (2,4))==135,
           "reference","Even tap-to-odd output contributions")
    verify(sum(comb(5,j)*ordered[5-j] for j in (1,3,5))==406,
           "reference","Odd tap-to-even output contributions")
    verify(135+406==ordered[5],"reference","Two blocks yield F5")
    return counters


def panel_svg():
    """Two exact triangular charts with cell contents from integer recurrence."""
    S=stirling_second(7)
    top=112
    cell=52
    lefts=(68,570)
    pieces=[
        '<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="650" viewBox="0 0 1050 650" role="img" aria-labelledby="title desc">',
        '<title id="title">Stirling partitions and factorial-weighted ordered partitions</title>',
        '<desc id="desc">Two triangular charts indexed by set size n in rows zero through seven and block count k in columns zero through seven. Left cells are Stirling counts S(n,k); right cells are k factorial times S(n,k). Cells outside k less than or equal to n are left blank. Exact integer values are printed in every valid cell.</desc>',
        '<rect width="1050" height="650" fill="#ffffff"/>',
        '<text x="42" y="37" font-family="sans-serif" font-size="23" font-weight="600" fill="#173b39">One triangular kernel · two counting families</text>',
        '<text x="42" y="63" font-family="sans-serif" font-size="14" fill="#475c59">Unordered partitions become ordered partitions by multiplying each k-block coordinate by k!</text>',
    ]
    for chart,left in enumerate(lefts):
        label=("S(n,k): partitions","k! S(n,k): ordered blocks")[chart]
        pieces.append(f'<text x="{left}" y="95" font-family="sans-serif" font-size="17" font-weight="600" fill="#235a54">{label}</text>')
        for k in range(8):
            xx=left+k*cell+cell//2
            pieces.append(f'<text x="{xx}" y="126" text-anchor="middle" font-family="monospace" font-size="12" fill="#355751">{k}</text>')
        for n,row in enumerate(S):
            yy=top+21+n*cell
            pieces.append(f'<text x="{left-16}" y="{yy+31}" text-anchor="end" font-family="monospace" font-size="12" fill="#355751">{n}</text>')
            for k,value in enumerate(row):
                number=value*factorial(k) if chart else value
                xx=left+k*cell
                # Integer bit-length yields a deterministic graduated scale without floating-point logs.
                shade=min(6,(number.bit_length()-1)//3) if number else 0
                palette=("#edf4f2","#dcece7","#c2e0d6","#9acbb9",
                         "#6caf9c","#438a7c","#216859")
                fill=palette[shade]
                pieces.append(f'<rect x="{xx}" y="{yy}" width="{cell-2}" height="{cell-2}" rx="3" fill="{fill}"/>')
                pieces.append(f'<text x="{xx+cell//2}" y="{yy+29}" text-anchor="middle" font-family="monospace" font-size="12" font-weight="600" fill="#112d29">{number}</text>')
    pieces.extend([
        '<text x="69" y="593" font-family="sans-serif" font-size="15" fill="#334e48">Row n=5: 0 + 1 + 15 + 25 + 10 + 1 = 52</text>',
        '<text x="570" y="593" font-family="sans-serif" font-size="15" fill="#334e48">Row n=5: 0 + 1 + 30 + 150 + 240 + 120 = 541</text>',
        '<text x="68" y="624" font-family="sans-serif" font-size="12" fill="#60716e">All displayed values are exact integers. White space above the triangles is outside k ≤ n.</text>',
        '</svg>'
    ])
    return "\n".join(pieces)+"\n"


def save(folder, checks):
    folder.mkdir(parents=True,exist_ok=True)
    S=stirling_second(DEGREE)
    first=signed_stirling_first(DEGREE)
    bell,ordered=bell_fubini(S)
    with (folder/"stirling-rows.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream,lineterminator="\n")
        writer.writerow(("n","k","partitions","block_order_factorial","ordered_partitions"))
        for n,row in enumerate(S):
            for k,value in enumerate(row):
                writer.writerow((n,k,value,factorial(k),value*factorial(k)))
    with (folder/"sequence-checks.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream,lineterminator="\n")
        writer.writerow(("n","bell","fubini","independent_bell","independent_fubini","stirling_inverse_bell","stirling_inverse_fubini","fubini_phase_mod2","fubini_phase_mod3"))
        bb=bell_recurrence(DEGREE)
        ff=fubini_recurrence(DEGREE)
        for n in range(DEGREE+1):
            writer.writerow((n,bell[n],ordered[n],bb[n],ff[n],
                             sum(first[n][j]*bell[j] for j in range(n+1)),
                             sum(first[n][j]*ordered[j] for j in range(n+1)),
                             n%2,n%3))
    with (folder/"signed-transfer.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream,lineterminator="\n")
        writer.writerow(("n","k","stirling_second","signed_stirling_first","inverse_product"))
        for n in range(DEGREE+1):
            for k in range(n+1):
                product_value=sum(first[n][j]*S[j][k] for j in range(k,n+1))
                writer.writerow((n,k,S[n][k],first[n][k],product_value))
    witness=S[4]
    with (folder/"obstruction.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream,lineterminator="\n")
        writer.writerow(("k","true_stirling_row","alternative_candidate","difference","factorial","weighted_difference"))
        for k in range(5):
            delta=ALTERNATIVE_ROW_4[k]-witness[k]
            writer.writerow((k,witness[k],ALTERNATIVE_ROW_4[k],delta,factorial(k),factorial(k)*delta))
    with (folder/"reciprocal-packets.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream,lineterminator="\n")
        writer.writerow(("n","bell","fubini","egf_bell","egf_fubini","even_packet","odd_packet","mod3_residue","mod3_packet"))
        be=egf_coefficients(bell)
        fe=egf_coefficients(ordered)
        for n in range(DEGREE+1):
            writer.writerow((n,bell[n],ordered[n],str(be[n]),str(fe[n]),
                            str(packet(fe,2,0)[n]),str(packet(fe,2,1)[n]),
                            n%3,str(packet(fe,3,n%3)[n])))
    (folder/"stirling-transform.svg").write_text(panel_svg(),encoding="utf-8",newline="\n")
    record=dict(
        case="Stirling rows, Bell/Fubini triangular transfers and reciprocal parity packets",
        degree=DEGREE,
        bell5=bell[5],
        fubini5=ordered[5],
        row5=list(S[5]),
        weighted_row5=[factorial(k)*S[5][k] for k in range(6)],
        witness_n4=dict(true_row=list(S[4]),alternative_row=list(ALTERNATIVE_ROW_4),
                        bell=bell[4],fubini=ordered[4],
                        difference=[ALTERNATIVE_ROW_4[k]-S[4][k] for k in range(5)]),
        packet_split_n5=dict(even_degree_tap_contribution=135,
                             odd_degree_tap_contribution=406),
        checks_by_group=checks,
        total_assertions=sum(checks.values()),
        scope="Exact classical finite combinatorics and formal-series identities; no new Lean replay or universal recovery theorem."
    )
    (folder/"results.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",
                                       encoding="utf-8",newline="\n")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,help="Generate exact CSV, JSON and SVG tables")
    args=parser.parse_args()
    checks=test_cases()
    print("STIRLING / BELL / FUBINI | exact integer and rational arithmetic")
    print("n=5: S=(0,1,15,25,10,1); Bell=52; Fubini=541")
    print("Inverse Stirling transform recovers 1 and k! input families")
    print("Reciprocal parity packets at degree five: 135 + 406 = 541")
    print("n=4: distinct nonnegative rows can share Bell=15 and Fubini=75")
    print(f"PASS: {sum(checks.values())} exact assertions")
    if args.output:
        save(args.output,checks)
        print("Exact tables and diagram written to "+str(args.output))


if __name__=="__main__":
    main()
