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



def series_compose(outer, inner):
    """Exact truncated formal composition; inner must vanish at zero."""
    if len(outer)!=len(inner) or not inner or inner[0]!=0:
        raise ValueError("Formal composition requires equal degree and zero inner constant")
    degree=len(outer)-1
    result=[Q(0)]*(degree+1)
    power=(Q(1),)+(Q(0),)*degree
    for k,coefficient in enumerate(outer):
        for n in range(degree+1):
            result[n]+=Q(coefficient)*power[n]
        power=series_product(power,inner)
    return tuple(result)


def formal_log_one_plus(degree):
    """Coefficients of log(1+t), exactly to the requested degree."""
    return (Q(0),)+tuple(Q((-1)**(j+1),j) for j in range(1,degree+1))


def stirling_transform_egf(degree, weights):
    """EGF of S*weights = A(exp(t)-1), A(u)=sum weights[k]u**k/k!."""
    weights=tuple(weights)
    if len(weights)<degree+1:
        raise ValueError("Need every input coordinate through declared degree")
    input_egf=tuple(Q(weights[k],factorial(k)) for k in range(degree+1))
    expm1=(Q(0),)+tuple(Q(1,factorial(k)) for k in range(1,degree+1))
    return series_compose(input_egf,expm1)


def series_reciprocal(a):
    if not a or a[0] != 1:
        raise ValueError("Reciprocal series requires constant term exactly one")
    out = [Q(1)]
    for n in range(1, len(a)):
        out.append(-sum((a[j]*out[n-j] for j in range(1,n+1)), Q(0)))
    return tuple(out)


def egf_coefficients(values):
    return tuple(Q(v, factorial(n)) for n, v in enumerate(values))


def exponential_series_of_expm1(degree, z=1):
    """Formal exp(z*(exp(t)-1)) in exact rational arithmetic."""
    z=Q(z)
    unit = (Q(1),) + (Q(0),)*degree
    u = (Q(0),) + tuple(Q(1, factorial(j)) for j in range(1, degree+1))
    result = [Q(0)] * (degree+1)
    power = unit
    for k in range(degree+1):
        for n in range(degree+1):
            result[n] += power[n]*z**k/factorial(k)
        power = series_product(power, u)
    return tuple(result)


def ordered_reciprocal_series(degree):
    """1 / (2-exp(t)) as a formal power series about t=0."""
    denominator = (Q(1),) + tuple(-Q(1,factorial(n))
                                  for n in range(1,degree+1))
    return series_reciprocal(denominator)



def touchard_value(row, z):
    """Evaluate the exact row polynomial sum S(n,k)*z**k."""
    z=Q(z)
    return sum((value*z**k for k,value in enumerate(row)),Q(0))


def exponential_moment_value(row, scale):
    """Gamma moment of T_n(scale*u); E[u**k]=k!, u~Exp(1)."""
    scale=Q(scale)
    return sum((value*factorial(k)*scale**k for k,value in enumerate(row)),Q(0))


def geometric_falling_moment(order, mean):
    """Exact falling-factorial moment of a geometric variable with given mean."""
    if order<0:
        raise ValueError("Moment order must be nonnegative")
    mean=Q(mean)
    if mean<0:
        raise ValueError("Geometric mean must be nonnegative")
    q=mean/(1+mean)
    return Q(factorial(order))*q**order/((1+mean)*(1-q)**(order+1))


def geometric_moment_value(row, mean):
    """Compute the polynomial's geometric raw moment in the falling basis."""
    return sum((value*geometric_falling_moment(k,mean)
                for k,value in enumerate(row)),Q(0))



def interpolate_integer_samples(samples):
    """Recover monomial coefficients from P(0),...,P(n) by Newton differences."""
    if not samples:
        raise ValueError("At least one polynomial sample is required")
    degree=len(samples)-1
    differences=[Q(v) for v in samples]
    result=[Q(0)]*(degree+1)
    falling=[Q(1)]
    for j in range(degree+1):
        scale=differences[0]/factorial(j)
        for k,value in enumerate(falling):
            result[k]+=scale*value
        differences=[differences[i+1]-differences[i]
                     for i in range(len(differences)-1)]
        next_falling=[Q(0)]*(len(falling)+1)
        for k,value in enumerate(falling):
            next_falling[k]-=j*value
            next_falling[k+1]+=value
        falling=next_falling
    return tuple(result)


def parameterized_reciprocal_series(degree, scale):
    """Formal 1/(1-scale*(exp(t)-1)); no floating-point operations."""
    scale=Q(scale)
    denominator=(Q(1),)+tuple(-scale*Q(1,factorial(n))
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

    # Same Stirling row, two different functionals: evaluation and gamma moment.
    # Check each parameter through a second formal generating-function route.
    for z in (Q(0),Q(1,2),Q(1),Q(2)):
        ts=tuple(touchard_value(row,z) for row in S)
        fs=tuple(exponential_moment_value(row,z) for row in S)
        t_egf=exponential_series_of_expm1(DEGREE,z)
        f_egf=parameterized_reciprocal_series(DEGREE,z)
        for n in range(DEGREE+1):
            verify(t_egf[n]==Q(ts[n],factorial(n)),
                   "moments","Touchard EGF at parameter "+str(z))
            verify(f_egf[n]==Q(fs[n],factorial(n)),
                   "moments","Parameterized Fubini EGF at "+str(z))
            verify(sum(s[n][j]*fs[j] for j in range(n+1))
                   == factorial(n)*z**n,
                   "moments","Signed inverse recovers scaled gamma moments")
            verify(geometric_moment_value(S[n],z)==fs[n],
                   "moments","Independent geometric moment of Touchard polynomial")
            verify(geometric_falling_moment(n,z)==factorial(n)*z**n,
                   "moments","Geometric falling factorial identity")
        for n in range(DEGREE):
            verify(ts[n+1] == z*sum(comb(n,j)*ts[j] for j in range(n+1)),
                   "moments","Touchard binomial recurrence")
        for n in range(1,DEGREE+1):
            verify(fs[n] == z*sum(comb(n,j)*fs[n-j] for j in range(1,n+1)),
                   "moments","Parameterized reciprocal recurrence")
    verify(touchard_value(S[5],Q(1,2))==Q(257,32),
           "reference","Touchard half evaluation")
    verify(exponential_moment_value(S[5],Q(1,2))==Q(91,2),
           "reference","Half-scaled gamma moment")
    verify(touchard_value(S[5],Q(2))==454,
           "reference","Touchard evaluation at two")
    verify(exponential_moment_value(S[5],Q(2))==9002,
           "reference","Double-scaled gamma moment")
    verify(touchard_value(S[5],1)==bell[5],
           "reference","Touchard evaluation recovers Bell")
    verify(exponential_moment_value(S[5],1)==ordered[5],
           "reference","Gamma moment recovers Fubini")
    verify(parameterized_reciprocal_series(DEGREE,1)==rf,
           "reference","Parameter one recovers original reciprocal")
    verify(touchard_value(S[0],0)==exponential_moment_value(S[0],0)==1,
           "reference","Empty-set boundary for zero parameter")

    # General coefficient grammar: composition and its formal logarithmic inverse.
    weight_families=(
        (1,)*(DEGREE+1),
        tuple(factorial(k) for k in range(DEGREE+1)),
        tuple(Q((-1)**k*(k+1),3) for k in range(DEGREE+1)),
        tuple(Q(k*k+1,k+1) for k in range(DEGREE+1)),
    )
    log= formal_log_one_plus(DEGREE)
    for weights in weight_families:
        outputs=lower_apply(S,weights)
        generated=stirling_transform_egf(DEGREE,weights)
        recovered=series_compose(generated,log)
        for n in range(DEGREE+1):
            verify(generated[n]==Q(outputs[n],factorial(n)),
                   "composition","General Stirling formal substitution")
            verify(recovered[n]==Q(weights[n],factorial(n)),
                   "composition","Formal logarithm recovers original weight")

    # Touchard polynomial calculus and the exact binomial-type addition law.
    for z in (Q(0),Q(1,2),Q(1),Q(2),Q(-1)):
        for n in range(DEGREE):
            derivative=sum(k*S[n][k]*z**(k-1) for k in range(1,n+1))
            verify(touchard_value(S[n+1],z)
                   ==z*(touchard_value(S[n],z)+derivative),
                   "touchard","Touchard differential recurrence")
    for x,y in ((Q(0),Q(1)),(Q(1),Q(1)),(Q(1,2),Q(2)),(Q(-1),Q(2))):
        for n in range(DEGREE+1):
            verify(touchard_value(S[n],x+y)==sum(
                comb(n,j)*touchard_value(S[j],x)
                *touchard_value(S[n-j],y) for j in range(n+1)),
                "touchard","Touchard binomial addition law")

    # Full parameter polynomial is reversible; one or two scalar summaries are not.
    for n,row in enumerate(S):
        touchard_samples=tuple(touchard_value(row,j) for j in range(n+1))
        ordered_samples=tuple(exponential_moment_value(row,j) for j in range(n+1))
        verify(interpolate_integer_samples(touchard_samples)==tuple(row),
               "reconstruction","Touchard interpolation recovers the row")
        ordered_coefficients=interpolate_integer_samples(ordered_samples)
        verify(tuple(ordered_coefficients[k]/factorial(k)
                     for k in range(n+1))==tuple(row),
               "reconstruction","Ordered polynomial recovers factorial-scaled row")
    original,candidate=S[4],ALTERNATIVE_ROW_4
    verify(touchard_value(original,2)==94
           and touchard_value(candidate,2)==90,
           "reconstruction","Another evaluation separates the two profiles")
    verify(exponential_moment_value(original,2)==730
           and exponential_moment_value(candidate,2)==746,
           "reconstruction","Another moment separates the two profiles")
    verify(interpolate_integer_samples(tuple(
        touchard_value(candidate,j) for j in range(5)))==candidate,
        "reconstruction","Interpolate the alternative candidate itself")
    verify(interpolate_integer_samples(tuple(
        exponential_moment_value(candidate,j) for j in range(5)))
        ==tuple(candidate[k]*factorial(k) for k in range(5)),
        "reconstruction","Recover candidate factorial-weighted coefficients")

    # The mod-m filters satisfy an entire coupled transfer, not just reconstruction.
    for modulus in range(2,6):
        for residue in range(modulus):
            expected=packet(fe,modulus,residue)
            generated=[Q(int(residue==0))]+[Q(0)]*DEGREE
            for tap in range(modulus):
                contribution=series_product(packet(u,modulus,tap),
                    packet(fe,modulus,(residue-tap)%modulus))
                generated=[generated[n]+contribution[n]
                           for n in range(DEGREE+1)]
            for n in range(DEGREE+1):
                verify(expected[n]==generated[n],"packet_transfer",
                       "Coupled residue transfer at modulus "+str(modulus))
    for residue,expected in enumerate((30,380,131)):
        verify(sum(comb(5,j)*ordered[5-j] for j in range(1,6)
                   if j%3==residue)==expected,
               "packet_transfer","Three-residue tap contributions at n=5")
    verify(30+380+131==ordered[5],"packet_transfer",
           "All three taps reconstruct Fubini n=5")

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
    with (folder/"moment-bridge.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream,lineterminator="\n")
        writer.writerow(("parameter","n","touchard_evaluation","exponential_moment",
                         "geometric_moment","touchard_egf_coefficient","moment_egf_coefficient",
                         "signed_inverse_recovered_weight"))
        for scale in (Q(0),Q(1,2),Q(1),Q(2)):
            values=tuple(exponential_moment_value(row,scale) for row in S)
            for n,row in enumerate(S):
                writer.writerow((str(scale),n,str(touchard_value(row,scale)),
                                 str(values[n]),str(geometric_moment_value(row,scale)),
                                 str(touchard_value(row,scale)/factorial(n)),
                                 str(values[n]/factorial(n)),
                                 str(sum(first[n][j]*values[j]
                                         for j in range(n+1)))))
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
    original=S[4]
    with (folder/"reconstruction.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream,lineterminator="\n")
        writer.writerow(("parameter","true_touchard","candidate_touchard",
                         "true_ordered_polynomial","candidate_ordered_polynomial"))
        for z in range(5):
            writer.writerow((z,touchard_value(original,z),
                             touchard_value(ALTERNATIVE_ROW_4,z),
                             exponential_moment_value(original,z),
                             exponential_moment_value(ALTERNATIVE_ROW_4,z)))
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
        moment_bridge_n5={
            str(scale):dict(touchard=str(touchard_value(S[5],scale)),
                            exponential_moment=str(exponential_moment_value(S[5],scale)))
            for scale in (Q(0),Q(1,2),Q(1),Q(2))
        },
        witness_n4=dict(true_row=list(S[4]),alternative_row=list(ALTERNATIVE_ROW_4),
                        bell=bell[4],fubini=ordered[4],
                        difference=[ALTERNATIVE_ROW_4[k]-S[4][k] for k in range(5)]),
        packet_split_n5=dict(even_degree_tap_contribution=135,
                             odd_degree_tap_contribution=406),
        packet_split_n5_mod3=dict(residue_0=30,residue_1=380,residue_2=131),
        reconstruction_n4=dict(
            true_ordered_samples=[str(exponential_moment_value(S[4],z))
                                  for z in range(5)],
            candidate_ordered_samples=[str(exponential_moment_value(
                ALTERNATIVE_ROW_4,z)) for z in range(5)],
            true_touchard_at_2=94,candidate_touchard_at_2=90,
            recovered_stirling_row=[int(v) for v in interpolate_integer_samples(tuple(
                touchard_value(S[4],z) for z in range(5)))]),
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
    print("General EGF substitution and exact polynomial interpolation checked")
    print("Three residue tap paths at n=5: 30 + 380 + 131 = 541")
    print("Touchard T5(2)=454; gamma moment F5(2)=9002")
    print("Reciprocal parity packets at degree five: 135 + 406 = 541")
    print("n=4: distinct nonnegative rows can share Bell=15 and Fubini=75")
    print(f"PASS: {sum(checks.values())} exact assertions")
    if args.output:
        save(args.output,checks)
        print("Exact tables and diagram written to "+str(args.output))


if __name__=="__main__":
    main()
