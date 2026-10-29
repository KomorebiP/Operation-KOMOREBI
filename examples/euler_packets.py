#!/usr/bin/env python3
"""Exact controls for the extended Euler packet, polynomial and residual case.

Python 3.10+, standard library only. No network, floating arithmetic or model API.
By default this writes only a concise report to stdout. --output DIRECTORY saves
JSON and CSV files there, refusing to replace existing result files.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as F
import hashlib
from itertools import permutations
import json
from math import comb, factorial
from pathlib import Path
import platform


SECANT = (1, 1, 5, 61, 1385, 50521, 2702765, 199360981,
          19391512145, 2404879675441, 370371188237525, 69348874393137901,
          15514534163557086905, 4087072509293123892361,
          1252259641403629865468285, 441543893249023104553682821)
QUARTIC = (1, 1, 69, 33661, 60376809, 288294050521, 3019098162602349,
           60921822444067346581, 2159058013333667522020689,
           125339574046311949415000577841,
           11289082167259099068433198467575829,
           1510335441937894173173702826484473600301)
REFERENCES = {
    'secant': dict(id='A000364', offset=0,
        url='https://oeis.org/A000364/b000364.txt', checked='2026-10-29'),
    'quartic': dict(id='A211212', offset=0,
        url='https://oeis.org/A211212', checked='2026-10-29'),
}


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def trim(a):
    a = list(a)
    while len(a) > 1 and not a[-1]:
        a.pop()
    return a or [F(0)]


def add(a, b, length=None):
    length = max(len(a), len(b)) if length is None else length
    return [F(a[i] if i < len(a) else 0) + F(b[i] if i < len(b) else 0)
            for i in range(length)]


def scale(a, scalar):
    return [F(scalar) * v for v in a]


def mul(a, b, length=None):
    length = len(a)+len(b)-1 if length is None else length
    result = [F(0)] * length
    for i, x in enumerate(a[:length]):
        if x:
            for j, y in enumerate(b[:length-i]):
                if y:
                    result[i+j] += x*y
    return result


def shift(a, amount, length):
    return ([F(0)]*amount + list(a))[:length]


def inverse(a, length):
    if not a or not a[0]:
        raise ValueError('A formal unit needs a nonzero constant coefficient')
    b = [1/F(a[0])]
    for n in range(1, length):
        b.append(-sum(F(a[j])*b[n-j] for j in range(1, min(n+1, len(a))))/a[0])
    return b


def power(a, exponent, length=None):
    if exponent < 0:
        if length is None:
            raise ValueError('Negative powers require a precision')
        return power(inverse(a, length), -exponent, length)
    result = [F(1)]
    for _ in range(exponent):
        result = mul(result, a, length)
    return result


def evaluate(a, value):
    total = F(0)
    for coefficient in reversed(a):
        total = total*value+coefficient
    return total


def translate(a, offset, scalar=1):
    # The polynomial a(offset + scalar*x), by the ordinary binomial theorem.
    result = [F(0)]*len(a)
    for n, value in enumerate(a):
        for j in range(n+1):
            result[j] += value*comb(n,j)*offset**(n-j)*scalar**j
    return trim(result)


def reciprocal_recurrence(spacing, parameter, count):
    """P_N,n(r) from D*F' + r*D'*F = 0, in compressed EGF coordinates."""
    if spacing < 1 or count < 1:
        raise ValueError('Positive spacing and count are required')
    r = F(parameter)
    values = [F(1)]
    for n in range(1, count):
        values.append(sum((-1)**(k+1)*(
            choose(spacing*n-1, spacing*k)
            + r*choose(spacing*n-1, spacing*k-1))*values[n-k]
            for k in range(1,n+1)))
    return values


def reciprocal_binomial(spacing, parameter, count):
    """Independent ordinary Cauchy products for (1+U)^(-r)."""
    u = [F(0)] + [F((-1)**n, factorial(spacing*n)) for n in range(1,count)]
    result = [F(1)]+[F(0)]*(count-1)
    term = [F(1)]+[F(0)]*(count-1)
    coefficient = F(1)
    for k in range(1,count):
        term = mul(term, u, count)
        coefficient *= -F(parameter+k-1)/k
        result = add(result, scale(term, coefficient), count)
    return [result[n]*factorial(spacing*n) for n in range(count)]


def reciprocal_polynomials(spacing, count):
    values = [[F(1)]]
    for n in range(1,count):
        row = [F(0)]*(n+1)
        for k in range(1,n+1):
            weight = [choose(spacing*n-1,spacing*k),
                      choose(spacing*n-1,spacing*k-1)]
            row = add(row,scale(mul(weight,values[n-k]),(-1)**(k+1)),n+1)
        values.append(trim(row))
    return values


def alternating_count(spacing, size):
    """Rank DP: a descent occurs unless the position is divisible by spacing."""
    if size == 0:
        return 1
    row = [1]
    for position in range(1,size):
        if position % spacing == 0:  # preceding value is smaller
            row = [sum(row[:j]) for j in range(position+1)]
        else:
            row = [sum(row[j:]) for j in range(position+1)]
    return sum(row)


def difference_coefficients(values):
    row, result = list(values), []
    while row:
        result.append(row[0])
        row = [y-x for x,y in zip(row,row[1:])]
    return result


def transfer_row(spacing, offset, order):
    unit = [F(comb(spacing,j)) for j in range(spacing+1)]
    unit[0] -= 1
    prefix = [F(comb(offset,j)) for j in range(offset+1)]
    return trim(mul(prefix,power(unit,order)))


def as_integer(value):
    value = F(value)
    if value.denominator != 1:
        raise AssertionError('Expected an integer, got '+str(value))
    return value.numerator


def local_source(chart, degree):
    """Paper IX source, indexed by ordinary even degree."""
    if degree < 0 or degree % 2:
        raise ValueError('An even nonnegative ordinary degree is required')
    if chart == 2:
        return F(3**(degree+2)-1,4*(degree+1)*(degree+2))
    if chart < 1 or chart % 2 == 0:
        raise ValueError('Use the dyadic chart 2 or a positive odd length')
    return F(sum((-1)**a*(2*a+1)**degree for a in range(chart)))


def local_inverse_kernel(chart, count):
    """EGF coefficients of the explicit inverse transfer unit."""
    if chart == 2:
        return [F(2**(4*r+1),(2*r+1)*(2*r+2)) for r in range(count)]
    if chart < 1 or chart % 2 == 0:
        raise ValueError('Use the dyadic chart 2 or a positive odd length')
    return [F(1)]+[F(2**(2*r-1)*chart**(2*r)) for r in range(1,count)]


def local_kernel(chart, count):
    """Invert the explicit unit by ordinary rational Cauchy products."""
    ordinary=[v/factorial(2*r) for r,v in enumerate(local_inverse_kernel(chart,count))]
    return [v*factorial(2*r) for r,v in enumerate(inverse(ordinary,count))]


def local_terms(chart, index):
    """Terms reconstructing E_(2*index), including every factorial weight."""
    return [comb(2*index,2*r)*coefficient*local_source(chart,2*(index-r))
            for r,coefficient in enumerate(local_kernel(chart,index+1))]


def bernoulli_numbers(degree):
    """Independent inversion of (exp(t)-1)/t, with B_1=-1/2."""
    ordinary=inverse([F(1,factorial(j+1)) for j in range(degree+1)],degree+1)
    return [value*factorial(j) for j,value in enumerate(ordinary)]


def valuation(value, prime):
    """Exact rational p-valuation; None denotes the valuation of zero."""
    value=F(value)
    if value == 0:
        return None
    numerator,denominator=abs(value.numerator),value.denominator
    result=0
    while numerator % prime == 0:
        numerator//=prime
        result+=1
    while denominator % prime == 0:
        denominator//=prime
        result-=1
    return result


def rational_residue(value, modulus):
    """Reduce only fractions whose reduced denominator is a unit."""
    value=F(value)
    return value.numerator*pow(value.denominator,-1,modulus) % modulus


def local_row_record(chart, index):
    terms=local_terms(chart,index)
    exact=sum(terms)
    partial=F(0)
    rows=[]
    for depth,term in enumerate(terms):
        partial+=term
        error=exact-partial
        rows.append(dict(depth=depth,term=str(term),partial=str(partial),
                         error=str(error),valuation=valuation(error,chart)))
    return dict(chart=chart,ordinary_degree=2*index,exact=str(exact),rows=rows)


def composition_count(spacing, blocks):
    """Inclusion-exclusion over the cuts between descending blocks."""
    if blocks == 0:
        return 1
    def compositions(total):
        if total == 0:
            yield ()
        else:
            for first in range(1,total+1):
                for rest in compositions(total-first):
                    yield (first,)+rest
    result=0
    for parts in compositions(blocks):
        denominator=1
        for part in parts:
            denominator*=factorial(spacing*part)
        result+=(-1)**(blocks-len(parts))*factorial(spacing*blocks)//denominator
    return result


def compute():
    counts = {}

    def check(group, condition):
        if not condition:
            raise AssertionError('Failed: '+group)
        counts[group] = counts.get(group,0)+1

    # Route A: compressed EGF recurrence versus ordinary rational products.
    parameters = [F(-2), F(-1), F(0), F(1,2), F(1), F(2), F(3)]
    for r in parameters:
        for n,value in enumerate(reciprocal_recurrence(1,r,11)):
            check('spacing_one_boundary',value == r**n)
    for spacing in range(2,7):
        polynomials = reciprocal_polynomials(spacing,11)
        for r in parameters:
            a = reciprocal_recurrence(spacing,r,11)
            b = reciprocal_binomial(spacing,r,11)
            for n in range(11):
                check('reciprocal_routes',a[n] == b[n])
                check('parameter_polynomials',evaluate(polynomials[n],r) == a[n])
        # Compare every coefficient of the two-variable addition identity.
        for n in range(9):
            left, right = {}, {}
            for degree,c in enumerate(polynomials[n]):
                for j in range(degree+1):
                    left[j,degree-j] = left.get((j,degree-j),0)+c*comb(degree,j)
            for k in range(n+1):
                for i,a in enumerate(polynomials[k]):
                    for j,b in enumerate(polynomials[n-k]):
                        right[i,j] = right.get((i,j),0)+comb(spacing*n,spacing*k)*a*b
            clean = lambda x:{k:v for k,v in x.items() if v}
            check('addition_polynomial_identities',clean(left) == clean(right))

    s = reciprocal_recurrence(2,1,41)
    b = reciprocal_recurrence(4,1,21)
    for n,value in enumerate(SECANT):
        check('oeis_secant_prefix',s[n] == value)
    for n,value in enumerate(QUARTIC):
        check('oeis_quartic_prefix',b[n] == value)
    for spacing in range(2,7):
        a = reciprocal_recurrence(spacing,1,9)
        for n in range(9):
            check('rank_dynamic_program',a[n] == alternating_count(spacing,spacing*n))
            check('permutation_composition_formula',a[n] == composition_count(spacing,n))
    # An explicit enumeration checks the rank-DP implementation on small inputs.
    for spacing,size in [(2,0),(2,4),(2,6),(2,8),(4,4),(4,8)]:
        actual = sum(all((p[j-1] < p[j]) == (j % spacing == 0)
                         for j in range(1,size))
                     for p in permutations(range(size)))
        check('permutation_enumeration',actual == alternating_count(spacing,size))

    # Route B: the 0/2 mod 4 transfer matrix and its determinant.
    length = 12
    c = [F(1,factorial(4*n)) for n in range(length)]
    d = [-F(1,factorial(4*n+2)) for n in range(length)]
    g = add(mul(c,c,length),scale(shift(mul(d,d,length),1,length),-1),length)
    expected = [F((-4)**n,factorial(4*n)) for n in range(length)]
    for x,y in zip(g,expected):
        check('quartic_determinant',x == y)
    h = inverse(g,length)
    packet_a = mul(c,h,length)
    packet_b = scale(mul(d,h,length),-1)
    first = add(mul(c,packet_a,length),shift(mul(d,packet_b,length),1,length),length)
    second = add(mul(d,packet_a,length),mul(c,packet_b,length),length)
    for n in range(length):
        check('packet_reconstruction',packet_a[n]*factorial(4*n) == s[2*n])
        check('packet_reconstruction',packet_b[n]*factorial(4*n+2) == s[2*n+1])
        check('packet_product_certificate',first[n] == (n == 0) and second[n] == 0)
    for n in range(41):
        rebuilt = sum(comb(2*n,4*k)*4**k*b[k] for k in range(n//2+1))
        check('quartic_to_secant',rebuilt == s[n])
    recovered=[]
    for n in range(21):
        remainder=s[2*n]-sum(comb(4*n,4*k)*4**k*recovered[k] for k in range(n))
        recovered.append(remainder/4**n)
        check('secant_to_quartic',recovered[n] == b[n])
    naive_a = inverse(c,length)
    check('failure_controls',naive_a[1] == -F(1,24) and packet_a[1] == F(5,24))
    check('failure_controls',mul(d,naive_a,length)[0] == -F(1,2))
    check('failure_controls',packet_a[1]-naive_a[1] == F(1,4))
    check('failure_controls',F(s[2],factorial(2)) != F(s[2],factorial(4)))
    check('failure_controls',add(mul(c,c,2),scale(mul(d,d,2),-1),2)[0] != g[0])

    # Route C: Newton residual squaring in Q[t]/(t^32).
    precision = 32
    cosine = [F(0)]*precision
    for n in range(precision//2):
        cosine[2*n] = F((-1)**n,factorial(2*n))
    exact_inverse = inverse(cosine,precision)
    for n in range(precision//2):
        check('dense_scalar_inverse',exact_inverse[2*n]*factorial(2*n) == s[n])
    current = [F(1)]+[F(0)]*(precision-1)
    residual_orders = []
    for iteration in range(5):
        residual = add([1],scale(mul(cosine,current,precision),-1),precision)
        first_nonzero = next((i for i,value in enumerate(residual) if value),None)
        expected_order = min(2**(iteration+1),precision)
        check('newton_precision',first_nonzero == (expected_order if expected_order < precision else None))
        residual_orders.append(first_nonzero if first_nonzero is not None else 'at least 32')
        check('newton_precision',current[:expected_order] == exact_inverse[:expected_order])
        next_value = mul(current,add([2],scale(mul(cosine,current,precision),-1),precision),precision)
        next_residual = add([1],scale(mul(cosine,next_value,precision),-1),precision)
        check('newton_residual_identity',next_residual == mul(residual,residual,precision))
        current = next_value
    finite_s3 = [F(0)]*10
    for n in range(4):
        finite_s3[2*n] = s[n]/factorial(2*n)
    actual_defect = add([1],scale(mul(cosine,finite_s3,10),-1),10)
    check('truncation_defect',actual_defect[:8] == [0]*8 and actual_defect[8] == F(277,8064))

    # Euler polynomials use a different variable and the signed sech convention.
    size = 13
    denominator = [F(2)]+[F(1,factorial(n)) for n in range(1,size)]
    base = scale(inverse(denominator,size),2)
    euler_polynomials = []
    signed_full = [F(0)]*size
    for n in range(0,size,2):
        signed_full[n] = (-1)**(n//2)*s[n//2]
    for n in range(size):
        poly = [comb(n,j)*base[n-j]*factorial(n-j) for j in range(n+1)]
        euler_polynomials.append(trim(poly))
        centered = [F(0)]*(n+1)
        for k in range(n//2+1):
            piece = translate([F(0)]*(n-2*k)+[F(1)],-F(1,2))
            centered = add(centered,scale(piece,comb(n,2*k)*signed_full[2*k]/2**(2*k)),n+1)
        check('euler_polynomial_centering',trim(poly) == trim(centered))
        target = [F(0)]*n+[F(2)]
        check('euler_polynomial_shift',trim(add(translate(poly,1),poly)) == target)
        check('euler_polynomial_reflection',translate(poly,1,-1) == trim(scale(poly,(-1)**n)))
        if n:
            derivative = [j*poly[j] for j in range(1,len(poly))]
            check('euler_polynomial_derivative',trim(derivative) == trim(scale(euler_polynomials[n-1],n)))
        for length in (0,1,2,3,5,6):
            for start in (-F(1,2),F(0),F(1),F(3,2)):
                direct=sum((-1)**j*(start+j)**n for j in range(length))
                boundary=(evaluate(poly,start)-(-1)**length*evaluate(poly,start+length))/2
                check('alternating_power_telescope',direct == boundary)

    # Paper IX charts: direct windows and rational sources versus formal units.
    local_count=11
    bernoulli=bernoulli_numbers(20)
    signed_egf=[(-1)**n*s[n]/factorial(2*n) for n in range(local_count)]
    for chart in (1,2,3,5,7,9):
        kernel=local_kernel(chart,local_count)
        inverse_coefficients=local_inverse_kernel(chart,local_count)
        ordinary_inverse=[v/factorial(2*r) for r,v in enumerate(inverse_coefficients)]
        source_by_series=mul(ordinary_inverse,signed_egf,local_count)
        for n in range(local_count):
            source=local_source(chart,2*n)
            check('local_source_series',source_by_series[n]*factorial(2*n) == source)
            rebuilt=sum(local_terms(chart,n))
            check('local_euler_reconstruction',rebuilt == (-1)**n*s[n])
            inverse_source=sum(comb(2*n,2*r)*inverse_coefficients[r]*(-1)**(n-r)*s[n-r]
                               for r in range(n+1))
            check('local_inverse_reconstruction',inverse_source == source)
            if chart == 2:
                check('dyadic_source_units',valuation(source,2) == 0)
                if n:
                    check('dyadic_bernoulli_kernel',kernel[n] == -2**(4*n)*(2*n-1)*bernoulli[2*n])
                    check('dyadic_kernel_valuation',valuation(kernel[n],2) == 4*n-1)
            else:
                check('odd_reciprocal_power_kernel',kernel[n] == (-1)**n*chart**(2*n)*reciprocal_recurrence(2,2,n+1)[n])
            terms=local_terms(chart,n)
            for depth in range(n+1):
                error=rebuilt-sum(terms[:depth+1])
                if chart in (2,3,5,7):
                    bound=4*depth+3 if chart == 2 else 2*depth+2
                    actual=valuation(error,chart)
                    check('local_truncation_bound',actual is None or actual >= bound)
                if depth == n:
                    check('full_depth_exact',error == 0)
        if chart == 2:
            for depth in range(10):
                error=sum(local_terms(2,depth+1))-sum(local_terms(2,depth+1)[:depth+1])
                check('dyadic_first_omitted_sharpness',error == kernel[depth+1] and valuation(error,2) == 4*depth+3)
    odd_example=local_row_record(3,4)
    dyadic_example=local_row_record(2,4)
    check('displayed_local_reconstruction',odd_example['exact'] == dyadic_example['exact'] == '1385')
    check('displayed_local_reconstruction',[r['valuation'] for r in dyadic_example['rows']] == [5,8,13,15,None])
    check('displayed_local_reconstruction',[r['term'] for r in dyadic_example['rows']]
          == ['7381/45','-6560/3','163072/15','-204800/9','229376/15'])
    check('displayed_local_reconstruction',rational_residue(F(7381,45),32) == 1385 % 32 == 9)
    try:
        rational_residue(F(5,24),8)
    except ValueError:
        check('failure_controls',True)
    else:
        check('failure_controls',False)
    check('failure_controls',sum((-1)**a for a in range(2)) == 0)

    # The same signed Euler data, now in integer finite-difference coordinates.
    signed = [as_integer((-1)**n*s[n]) for n in range(41)]
    signals = [signed, [n**3-2*n*n+7 for n in range(41)],
               [(-1)**n*(n+1)+n*n for n in range(41)]]
    for signal in signals:
        differences = difference_coefficients(signal)
        for spacing in range(1,6):
            for offset in range(spacing):
                lane = [signal[spacing*q+offset] for q in range(6)]
                direct = difference_coefficients(lane)
                for order in range(6):
                    weights = transfer_row(spacing,offset,order)
                    via_kernel = sum(weight*differences[j] for j,weight in enumerate(weights))
                    check('finite_difference_transfer',direct[order] == via_kernel)
    for m in range(1,5):
        for ell in range(1,5):
            for offset in range(m):
                for branch in range(ell):
                    for order in range(4):
                        outer = transfer_row(ell,branch,order)
                        composed = [F(0)]
                        for j,weight in enumerate(outer):
                            composed = add(composed,scale(transfer_row(m,offset,j),weight))
                        direct = transfer_row(m*ell,offset+m*branch,order)
                        check('refinement_composition',trim(composed) == direct)
    for prime in (2,3,5,7,11):
        residual = [choose(prime,j)-(1 if j in (0,prime) else 0) for j in range(prime+1)]
        check('prime_residual_polynomials',all(value % prime == 0 for value in residual))
        correction = [value//prime for value in residual]
        for signal in signals:
            differences = difference_coefficients(signal[:prime+1])
            check('prime_residual_application',signal[prime]-signal[0]
                  == differences[prime]+prime*sum(correction[j]*differences[j] for j in range(prime+1)))
    c0 = difference_coefficients(signed[:5])
    check('displayed_integer_calculations',c0 == [1,-2,8,-80,1664])
    check('displayed_integer_calculations',2*c0[1]+c0[2] == 4)
    check('displayed_integer_calculations',4*c0[2]+4*c0[3]+c0[4] == 1376)
    check('displayed_integer_calculations',4*c0[1]+6*c0[2]+4*c0[3]+c0[4] == 1384)
    check('displayed_integer_calculations',2*4+1376 == 1384)
    check('failure_controls',c0[2] != signed[2]-signed[0])
    check('failure_controls',(signed[2]-signed[0]) % 8 != c0[2] % 8)
    check('failure_controls',comb(4,2) % 4 != 0)
    first_six=difference_coefficients(signed[:6])
    check('higher_prime_examples',first_six == [1,-2,8,-80,1664,-58112])
    for prime,expected_correction in ((3,18),(5,7590)):
        correction=sum(comb(prime,j)*first_six[j] for j in range(1,prime))
        check('higher_prime_examples',correction == expected_correction)
        check('higher_prime_examples',first_six[prime]+correction == signed[prime]-1)
    alternating=[(-1)**n for n in range(12)]
    constant=[1]*12
    check('sampled_signal_control',alternating[::2] == constant[::2])
    check('sampled_signal_control',alternating[1::2] != constant[1::2])
    check('sampled_signal_control',all(alternating[n+2]-alternating[n] == 0 for n in range(10)))
    # No field-valued quotient or division by a non-unit is used in the modular check.

    polynomials = reciprocal_polynomials(2,6)
    report = dict(status='PASS',arithmetic='exact integers and fractions',
        python=platform.python_version(),randomness=False,checks=counts,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        secant=[as_integer(v) for v in s[:16]],quartic=[as_integer(v) for v in b[:12]],
        signed_euler=signed[:9],difference_coordinates=c0,
        lane_spacing_two=[signed[0],signed[2],signed[4]],
        lane_difference_coordinates=[1,4,1376],refined_first_difference=1384,
        newton_residual_orders=residual_orders,
        reciprocal_power_polynomials=[[str(c) for c in p] for p in polynomials],
        euler_polynomials=[[str(c) for c in p] for p in euler_polynomials[:7]],
        local_reconstructions=[odd_example,dyadic_example],
        references=REFERENCES,
        bounds=dict(reciprocal_spacing=[2,6],reciprocal_index=[0,10],
            reciprocal_parameters=[str(r) for r in parameters],
            addition_spacing=[2,6],addition_index=[0,8],
            quartic_bridge_secant_index=[0,40],quartic_packet_index=[0,11],
            permutation_dp_spacing=[2,6],permutation_dp_block_count=[0,8],
            enumeration_cases=[[2,0],[2,4],[2,6],[2,8],[4,4],[4,8]],
            euler_polynomial_degree=[0,12],newton_precision=32,
            alternating_power_lengths=[0,1,2,3,5,6],alternating_power_starts=['-1/2','0','1','3/2'],
            local_charts=[1,2,3,5,7,9],local_even_degree=[0,20],
            dyadic_sharp_depth=[0,9],bernoulli_degree=[0,20],
            difference_spacing=[1,5],difference_offsets='all 0 <= s < M',difference_order=[0,5],
            composition_spacings=[1,4],composition_offsets='all admitted offsets',composition_order=[0,3],
            primes=[2,3,5,7,11]),
        non_claims=['No novelty or exclusive-method claim.',
            'Finite computations are separate from the written universal algebraic proofs.',
            'No numerical error bound, asymptotic law or complexity advantage is established.',
            'No Lean execution. The local truncation theorems are proved separately; finite checks do not certify broader Euler congruences.'])
    return report


def save_results(directory, report):
    directory.mkdir(parents=True,exist_ok=True)
    paths = [directory/'results.json',directory/'euler-coefficients.csv',directory/'power-polynomials.csv',
             directory/'local-reconstruction.csv']
    if any(p.exists() for p in paths):
        raise FileExistsError('Choose a directory with no existing result files')
    paths[0].write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    with paths[1].open('w',encoding='utf-8',newline='') as stream:
        writer = csv.writer(stream,lineterminator='\n')
        writer.writerow(['compressed_index','ordinary_degree','secant','signed_euler','ordinary_secant_coefficient'])
        for n,s in enumerate(report['secant']):
            writer.writerow([n,2*n,s,(-1)**n*s,str(F(s,factorial(2*n)))])
    with paths[2].open('w',encoding='utf-8',newline='') as stream:
        writer = csv.writer(stream,lineterminator='\n')
        writer.writerow(['spacing','compressed_index','parameter_power','coefficient'])
        for spacing in (2,4):
            for n,p in enumerate(reciprocal_polynomials(spacing,9)):
                for degree,value in enumerate(p):
                    writer.writerow([spacing,n,degree,str(value)])
    with paths[3].open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['chart','ordinary_degree','depth','term','partial','error','error_valuation'])
        for example in report['local_reconstructions']:
            for row in example['rows']:
                writer.writerow([example['chart'],example['ordinary_degree'],row['depth'],row['term'],
                                 row['partial'],row['error'],'infinity' if row['valuation'] is None else row['valuation']])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Save JSON and CSV results in this directory')
    args = parser.parse_args()
    report = compute()
    if args.output:
        save_results(args.output,report)
    print('Secant numbers:', ', '.join(map(str,report['secant'][:7])))
    print('Quartic reciprocal:', ', '.join(map(str,report['quartic'][:5])))
    print('Odd-length and dyadic reconstructions: E_8 = 1385')
    print('Dyadic E_8 tail valuations: 5, 8, 13, 15, exact')
    print('Signed Euler difference coordinates:', ', '.join(map(str,report['difference_coordinates'])))
    print('Spacing-two lane: 1, 5, 1385; differences: 1, 4, 1376')
    print('Refinement: 2*4 + 1376 = 1384')
    print('Prime residual: 2*(-2) + 8 = 4')
    print('Newton residual orders:', ', '.join(map(str,report['newton_residual_orders'])))
    print('PASS: Euler packets, polynomials and residuals')


if __name__ == '__main__':
    main()
