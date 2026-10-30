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


def toeplitz_matrix(coefficients, size):
    """Leading block of multiplication in ordinary coefficient coordinates."""
    return [[F(coefficients[n-j]) if j <= n else F(0)
             for j in range(size)] for n in range(size)]


def coefficient_matrix(kernel, size):
    """Leading block in even exponential coefficient coordinates."""
    return [[F(comb(2*n,2*j))*kernel[n-j] if j <= n else F(0)
             for j in range(size)] for n in range(size)]


def matrix_product(a, b):
    if not a or not b or any(len(row) != len(b) for row in a):
        raise ValueError('Compatible nonempty matrices are required')
    if any(len(row) != len(b[0]) for row in b):
        raise ValueError('The right matrix must be rectangular')
    return [[sum((x*y for x,y in zip(row,column)),F(0))
             for column in zip(*b)] for row in a]


def matrix_vector(a, vector):
    if any(len(row) != len(vector) for row in a):
        raise ValueError('Matrix and vector dimensions differ')
    return [sum((x*y for x,y in zip(row,vector)),F(0)) for row in a]


def pascal_matrix(size, inverse=False):
    return [[F(choose(n,j)*((-1)**(n-j) if inverse and j <= n else 1))
             for j in range(size)] for n in range(size)]


def congruential_packet(spacing, address, count):
    """Normalized positive-section Euler coefficients C_(N,j)(n)."""
    if spacing < 1 or not 0 <= address < spacing:
        raise ValueError('Require N>=1 and 0<=address<N')
    denominator=[F(factorial(address),factorial(spacing*n+address)) for n in range(count)]
    return [value*factorial(spacing*n) for n,value in enumerate(inverse(denominator,count))]


def fibonacci_polynomials(count):
    """B_k=F_(k+1), ascending ordinary polynomial coefficients."""
    basis=[]
    previous,current=[F(0)],[F(1)]
    for _ in range(count):
        basis.append(current)
        previous,current=current,trim(add([F(0)]+current,previous))
    return basis


def monic_coordinates(polynomial, basis):
    """Descending elimination, independent of the ballot coefficient formula."""
    remainder=list(polynomial)+[F(0)]*(len(basis)-len(polynomial))
    coordinates=[F(0)]*len(basis)
    for k in reversed(range(len(basis))):
        coordinates[k]=remainder[k]
        for j,value in enumerate(basis[k]):
            remainder[j]-=coordinates[k]*value
    assert not any(remainder)
    return coordinates


def fibonacci_examples(euler_polynomials, signed, check):
    size=len(euler_polynomials)
    basis=fibonacci_polynomials(size+1)
    columns=[monic_coordinates(poly,basis[:size]) for poly in euler_polynomials]
    connection=[list(row) for row in zip(*columns)]
    for n in range(size):
        for k in range(size):
            closed=sum((euler_polynomials[n][k+2*r]*(-1)**r
                        *(choose(k+2*r,r)-choose(k+2*r,r-1))
                        for r in range(max(0,(n-k)//2+1))),F(0))
            check('fibonacci_connection_formula',connection[k][n]==closed)
        recovered=[F(0)]*size
        for k in range(size):
            recovered=add(recovered,scale(basis[k],connection[k][n]),size)
        check('fibonacci_polynomial_reconstruction',trim(recovered)==euler_polynomials[n])
        recovered_euler=2**n*sum(connection[k][n]*evaluate(basis[k],F(1,2)) for k in range(size))
        expected=0 if n%2 else signed[n//2]
        check('fibonacci_centered_euler_recovery',recovered_euler==expected)
    reverse_columns=[monic_coordinates(poly,euler_polynomials) for poly in basis[:size]]
    reverse=[list(row) for row in zip(*reverse_columns)]
    identity=[[F(i==j) for j in range(size)] for i in range(size)]
    check('fibonacci_connection_inverse',matrix_product(connection,reverse)==identity)
    check('fibonacci_connection_inverse',matrix_product(reverse,connection)==identity)
    displayed=[[1,F(-1,2),-1,F(7,4),2],[0,1,-1,-2,5],
               [0,0,1,F(-3,2),-3],[0,0,0,1,-2],[0,0,0,0,1]]
    check('fibonacci_display', [row[:5] for row in connection[:5]]==displayed)
    check('fibonacci_failure_controls',matrix_vector(displayed,[1,0,0,0,0])
          != matrix_vector(list(map(list,zip(*displayed))),[1,0,0,0,0]))
    # Direct polynomial matrix iteration versus the Fibonacci recurrence.
    polynomial_powers=[]
    state=[[[F(1)],[F(0)]],[[F(0)],[F(1)]]]
    for n in range(size):
        polynomial_powers.append(state)
        if n:
            expected=[[basis[n],basis[n-1]],
                      [basis[n-1],basis[n-2] if n>=2 else [F(0)]]]
            check('fibonacci_polynomial_companion',state==expected)
        state=[[trim(add([F(0)]+state[i][0],state[i][1])),state[i][0]] for i in range(2)]

    count=16
    a=[F(value) for value in signed[:count]]
    fib=[0,1]
    for _ in range(count+1):
        fib.append(fib[-1]+fib[-2])
    analysis=[[F(i==j) if i<2 else F(j==i)-F(j==i-1)-F(j==i-2)
               for j in range(count)] for i in range(count)]
    synthesis=[]
    for i in range(count):
        synthesis.append([F(1 if i==0 else fib[i-1]) if j==0 else
                          F(fib[i]) if j==1 else F(fib[i-j+1]) if j<=i else F(0)
                          for j in range(count)])
    identity=[[F(i==j) for j in range(count)] for i in range(count)]
    check('fibonacci_defect_inverse',matrix_product(analysis,synthesis)==identity)
    check('fibonacci_defect_inverse',matrix_product(synthesis,analysis)==identity)
    coordinates=matrix_vector(analysis,a)
    check('fibonacci_defect_reconstruction',matrix_vector(synthesis,coordinates)==a)
    defects=coordinates[2:]
    check('fibonacci_display',defects[:4]==[5,-65,1441,-51845])
    companion=[[F(0),F(1)],[F(1),F(1)]]
    inverse_companion=[[F(-1),F(1)],[F(1),F(0)]]
    forward=backward=[[F(1),F(0)],[F(0),F(1)]]
    moving=[]
    for n in range(count-1):
        state=a[n:n+2]
        z=matrix_vector(backward,state)
        moving.append(z)
        check('fibonacci_moving_state',matrix_vector(forward,z)==state)
        green=matrix_vector(forward,a[:2])
        for j in range(n):
            green=add(green,[F(fib[n-1-j]*defects[j]),F(fib[n-j]*defects[j])],2)
        check('fibonacci_green_reconstruction',green==state)
        if n<count-2:
            next_state=add(matrix_vector(companion,state),[0,defects[n]],2)
            check('fibonacci_forced_companion',next_state==a[n+1:n+3])
            next_backward=matrix_product(inverse_companion,backward)
            increment=matrix_vector(next_backward,[0,defects[n]])
            check('fibonacci_moving_increment',add(z,increment)==matrix_vector(next_backward,next_state))
        forward=matrix_product(companion,forward)
        backward=matrix_product(inverse_companion,backward)
    check('fibonacci_display',moving[:4]==[[1,-1],[6,-1],[71,-66],[2953,-1507]])
    check('fibonacci_failure_controls',defects[0]!=0)

    residual=mul(a,[F(1),F(-1),F(-1)],count)
    kernel=inverse(residual,count)
    transfer=toeplitz_matrix(kernel,count)
    inverse_transfer=toeplitz_matrix(residual,count)
    target=[F(fib[n+1]) for n in range(count)]
    check('fibonacci_sequence_transfer',matrix_vector(transfer,a)==target)
    check('fibonacci_sequence_transfer',matrix_vector(inverse_transfer,target)==a)
    check('fibonacci_toeplitz_inverse',matrix_product(transfer,inverse_transfer)==identity)
    check('fibonacci_toeplitz_inverse',matrix_product(inverse_transfer,transfer)==identity)
    check('fibonacci_display',residual[:6]==[1,-2,5,-65,1441,-51845])
    check('fibonacci_display',kernel[:6]==[1,2,-1,53,-1200,46233])
    # Complete rows of S L(H)-L(H) S: an infinite rank-one boundary term.
    for n in range(count-1):
        for j in range(count):
            first=kernel[n+1-j] if j<=n+1 else 0
            second=kernel[n-j+1] if 1<=j<=n+1 else 0
            check('fibonacci_shift_commutator',first-second==(kernel[n+1] if j==0 else 0))
    return dict(polynomial_connection=[[str(c) for c in row] for row in connection],
        polynomial_inverse=[[str(c) for c in row] for row in reverse],
        polynomial_basis=[[str(c) for c in poly] for poly in basis[:size]],
        polynomial_companion_powers=[[[[str(c) for c in poly] for poly in row] for row in mat] for mat in polynomial_powers],
        recurrence_analysis=[[str(c) for c in row] for row in analysis],
        recurrence_synthesis=[[str(c) for c in row] for row in synthesis],
        defects=[str(c) for c in defects],moving_states=[[str(c) for c in row] for row in moving],
        ordinary_residual=[str(c) for c in residual],ordinary_kernel=[str(c) for c in kernel],
        sequence_transfer=[[str(c) for c in row] for row in transfer],
        sequence_inverse=[[str(c) for c in row] for row in inverse_transfer],
        target=[int(c) for c in target])


def matrix_power(matrix, exponent):
    result=[[F(i==j) for j in range(len(matrix))] for i in range(len(matrix))]
    base=matrix
    while exponent:
        if exponent%2:
            result=matrix_product(result,base)
        base=matrix_product(base,base)
        exponent//=2
    return result


def literature_examples(euler_polynomials, check):
    fib=[0,1]
    for _ in range(1400):
        fib.append(fib[-1]+fib[-2])
    lucas=[2,1]
    for _ in range(12):
        lucas.append(lucas[-1]+lucas[-2])
    companion=[[F(1),F(1)],[F(1),F(0)]]
    identity=[[F(1),F(0)],[F(0),F(1)]]
    jumps=[]
    for step in range(13):
        jump=matrix_power(companion,step)
        jumps.append([[int(c) for c in row] for row in jump])
        check('literature_lucas_trace',jump[0][0]+jump[1][1]==lucas[step])
        check('literature_determinant_parity',jump[0][0]*jump[1][1]-jump[0][1]*jump[1][0]==(-1)**step)
        char=matrix_product(jump,jump)
        check('literature_jump_characteristic',all(char[i][j]-lucas[step]*jump[i][j]+(-1)**step*identity[i][j]==0
                                                 for i in range(2) for j in range(2)))
        for address in range(6):
            for k in range(9):
                check('literature_sampled_recurrence',fib[step*(k+2)+address]
                      ==lucas[step]*fib[step*(k+1)+address]-(-1)**step*fib[step*k+address])
    check('literature_parity_control',fib[5]!=3*fib[3]+fib[1])
    check('literature_jump_control',matrix_power(companion,2)!=companion)

    precision=[]
    ladder=[]
    for refinement in range(5):
        step=12*2**refinement
        jump=matrix_power(companion,step)
        divisor=2**(refinement+3)
        factor=[[ (jump[i][j]-identity[i][j])/divisor for j in range(2)] for i in range(2)]
        check('literature_dyadic_refinement',all(c.denominator==1 for row in factor for c in row))
        check('literature_dyadic_factor_parity',all(int(factor[i][j])%2==int(i==j) for i in range(2) for j in range(2)))
        for n in range(7):
            for order in range(6):
                direct=sum((-1)**(order-j)*comb(order,j)*fib[n+step*j] for j in range(order+1))
                projected=matrix_vector(matrix_product(matrix_power(companion,n),matrix_power(factor,order)),[1,0])[1]
                check('literature_matrix_difference',direct==divisor**order*projected)
                check('literature_dyadic_divisibility',direct%(divisor**order)==0)
                if n==1:
                    check('literature_dyadic_sharpness',valuation(direct,2)==(refinement+3)*order)
        for address in range(4):
            for coarse in range(7):
                terms=[]
                for order in range(coarse+1):
                    projected=matrix_vector(matrix_product(matrix_power(companion,address),matrix_power(factor,order)),[1,0])[1]
                    terms.append(comb(coarse,order)*divisor**order*projected)
                check('literature_packet_binomial',sum(terms)==fib[step*coarse+address])
                for depth in range(coarse+2):
                    partial=sum(terms[:depth])
                    error=fib[step*coarse+address]-partial
                    check('literature_packet_precision',error%(divisor**depth)==0)
                    if address==1 and coarse==3:
                        precision.append(dict(step=step,refinement=refinement,depth=depth,
                            target=fib[step*coarse+address],partial=int(partial),error=int(error),
                            modulus=divisor**depth,valuation=valuation(error,2)))
        ladder.append(dict(step=step,power=refinement,divisor=divisor,
                           factor=[[int(c) for c in row] for row in factor]))
    check('literature_display',ladder[0]['factor']==[[29,18],[18,11]])
    jump24=matrix_power(companion,24)
    factor144=[[(jump24[i][j]-identity[i][j])/144 for j in range(2)] for i in range(2)]
    check('literature_simultaneous_factor',factor144==[[521,322],[322,199]])
    for n in range(7):
        for order in range(6):
            direct=sum((-1)**(order-j)*comb(order,j)*fib[n+24*j] for j in range(order+1))
            projected=matrix_vector(matrix_product(matrix_power(companion,n),matrix_power(factor144,order)),[1,0])[1]
            check('literature_simultaneous_differences',direct==144**order*projected)
            check('literature_simultaneous_moduli',direct%(144**order)==0 and direct%(24**order)==0)
    check('literature_display',sum((-1)**(2-j)*comb(2,j)*fib[1+24*j] for j in range(3))==7778592000)
    # Actual composition of the existing ordinary Euler transfer with a selector.
    a=[(-1)**n*v for n,v in enumerate(reciprocal_recurrence(2,1,16))]
    kernel=inverse(mul(a,[1,-1,-1],16),16)
    selector_rows=[toeplitz_matrix(kernel,16)[2*k] for k in range(8)]
    check('literature_euler_packet_composition',matrix_vector(selector_rows,a)==[fib[2*k+1] for k in range(8)])

    calculus={}
    for degree in range(9):
        source=fibonacci_polynomials(degree+1)
        target=fibonacci_polynomials(degree+2)
        primitives=[[F(0)]+[value/F(i+1) for i,value in enumerate(poly)] for poly in source]
        integral=list(map(list,zip(*(monic_coordinates(poly,target) for poly in primitives))))
        derivative=list(map(list,zip(*(monic_coordinates([F(j)*poly[j] for j in range(1,len(poly))] or [F(0)],source)
                                       for poly in target))))
        c=list(map(list,zip(*(monic_coordinates(poly,source) for poly in euler_polynomials[:degree+1]))))
        c_inverse=list(map(list,zip(*(monic_coordinates(poly,euler_polynomials[:degree+2]) for poly in target))))
        d_euler=[[F(j) if i==j-1 else F(0) for j in range(degree+2)] for i in range(degree+1)]
        conjugate=matrix_product(matrix_product(c,d_euler),c_inverse)
        check('literature_derivative_conjugacy',conjugate==derivative)
        combined=matrix_product(conjugate,integral)
        check('literature_calculus_round_trip',combined==[[F(i==j) for j in range(degree+1)] for i in range(degree+1)])
        reverse=matrix_product(integral,derivative)
        evaluation=[poly[0] for poly in target]
        check('literature_calculus_boundary',reverse==[[F(i==j)-(evaluation[j] if i==0 else 0)
                                                       for j in range(degree+2)] for i in range(degree+2)])
        moment=lambda poly:sum(value/F(i+1) for i,value in enumerate(poly))
        fib_moments=[moment(poly) for poly in source]
        euler_moments=[moment(poly) for poly in euler_polynomials[:degree+1]]
        check('literature_integral_covector',matrix_product([fib_moments],c)==[euler_moments])
        calculus[str(degree)]=dict(integral=integral,derivative=derivative,
            euler_derivative=d_euler,connection=c,inverse_connection=c_inverse,
            fib_moments=fib_moments,euler_moments=euler_moments)
    display=calculus['3']
    v0=[F(0),F(0),F(0),F(1)]
    v1=matrix_vector(display['integral'],v0)
    v2=matrix_vector(display['inverse_connection'],v1)
    v3=matrix_vector(display['euler_derivative'],v2)
    v4=matrix_vector(display['connection'],v3)
    check('literature_display',v1==[F(-1,2),0,F(1,4),0,F(1,4)])
    check('literature_display',v2==[F(5,8),F(3,2),F(7,4),F(1,2),F(1,4)])
    check('literature_display',v3==[F(3,2),F(7,2),F(3,2),1] and v4==v0)
    check('literature_display',sum(x*y for x,y in zip(display['fib_moments'],v4))==F(5,4))
    check('literature_wrong_operator_control',matrix_vector(display['euler_derivative'],[0,0,0,1,0])
          !=matrix_vector(display['derivative'],[0,0,0,1,0]))
    def strings(obj):
        if isinstance(obj,F):return str(obj)
        if isinstance(obj,list):return [strings(x) for x in obj]
        if isinstance(obj,dict):return {k:strings(v) for k,v in obj.items()}
        return obj
    return dict(jumps=jumps,lucas=lucas[:13],packet_three=[[fib[3*k+j] for k in range(6)] for j in range(3)],
        dyadic_factors=ladder,precision=precision,simultaneous_factor=[[int(c) for c in row] for row in factor144],
        calculus=strings(calculus),calculus_vectors=strings([v0,v1,v2,v3,v4]))


def compose_series(outer, inner, count):
    result=[F(0)]*count
    term=[F(1)]+[F(0)]*(count-1)
    for coefficient in outer[:count]:
        result=add(result,scale(term,coefficient),count)
        term=mul(term,inner,count)
    return result


def stirling_tables(size):
    first=[[0]*size for _ in range(size)]
    second=[[0]*size for _ in range(size)]
    first[0][0]=second[0][0]=1
    for n in range(1,size):
        for k in range(1,n+1):
            first[n][k]=first[n-1][k-1]-(n-1)*first[n-1][k]
            second[n][k]=second[n-1][k-1]+k*second[n-1][k]
    return first,second


def cyclic_product(a,b,prime):
    return [sum(a[j]*b[(i-j)%prime] for j in range(prime))%prime for i in range(prime)]


def atlas_examples(check):
    gains=[1,1,4,2]
    original_gains=[1,1,5,3]
    packets=[]
    for address in range(4):
        values=congruential_packet(4,address,48)
        triangular=[F(1)]
        for n in range(1,48):
            triangular.append(-sum(comb(4*n+address,4*k)*triangular[k] for k in range(n))
                              /F(comb(4*n+address,4*n)))
        check('atlas_quartic_recurrence',triangular==values)
        check('atlas_quartic_integrality',all(v.denominator%2 for v in values))
        for n in range(7):
            for step in range(1,9):
                for order in range(6):
                    difference=sum((-1)**(order-k)*comb(order,k)*values[n+step*k] for k in range(order+1))
                    weight=valuation(difference,2)
                    check('atlas_all_row_bounds',weight is None or weight>=order*(1+valuation(step,2)))
        for n in range(9):
            for step in range(1,17):
                difference=values[n+step]-values[n]
                check('atlas_exact_displacement',valuation(difference,2)==valuation(step,2)+gains[address])
        packets.append(values)
    newton=[difference_coefficients(values[:13]) for values in packets]
    for address,orders,expected in [(0,[2],[3]),(1,[2],[3]),(2,[2,3,4,5,6],[6,9,13,16,22]),(3,[2,3,4],[8,8,15])]:
        check('atlas_newton_prefix',[valuation(newton[address][k],2) for k in orders]==expected)
    check('atlas_display',[newton[j][1] for j in range(4)]==[F(-2),F(-6,5),F(-16,15),F(-36,35)])

    # All source diagonals are odd, so modular recurrence needs no rational division.
    modulus=8192
    binomial=[[comb(4*n,4*k)%modulus for k in range(n+1)] for n in range(256)]
    modular=[]
    permutations=[]
    phi_tables=[]
    periods=[]
    for address in range(4):
        g=[pow(comb(4*k+address,address),-1,modulus) for k in range(256)]
        values=[1]
        for n in range(1,256):
            values.append(-sum(binomial[n][k]*g[k]*values[n-k] for k in range(1,n+1))%modulus)
        modular.append(values)
        for n,exact in enumerate(packets[address]):
            check('atlas_exact_modular_agreement',values[n]==exact.numerator*pow(exact.denominator,-1,modulus)%modulus)
        factor=factorial(address)
        d=original_gains[address]
        original=[factor*v%modulus for v in values]
        check('atlas_affine_image_residue',all((v-factor)%2**d==0 for v in original))
        phi=[((v-factor)//2**d)%256 for v in original]
        phi_tables.append(phi)
        for bits in range(1,9):
            precision=2**bits
            residues=[value%precision for value in phi[:precision]]
            check('atlas_residue_permutation',sorted(residues)==list(range(precision)))
            permutations.append(dict(address=address,bits=bits,size=precision,bijection=True))
        for n in range(32):
            for m in range(n):
                check('atlas_finite_isometry',valuation(phi[n]-phi[m],2)==valuation(n-m,2))
        for bits in range(9):
            period=2**max(0,bits-d)
            periods.append(dict(address=address,bits=bits,least_period=period))
            for n in range(9):
                check('atlas_least_period',original[n+period]%(2**bits)==original[n]%(2**bits))
                for step in range(1,17):
                    actual=(original[n+step]-original[n])%(2**bits)==0
                    check('atlas_period_classification',actual==(step%period==0))
            if period>1:
                check('atlas_half_period_control',(original[period//2]-original[0])%(2**bits)!=0)
    trace=[]
    address,target,index=2,13,0
    phi=phi_tables[address]
    for bits in range(6):
        low=index
        high=index+2**bits
        mod=2**(bits+1)
        candidates=[value for value in (low,high) if phi[value]%mod==target%mod]
        check('atlas_binary_lifting',len(candidates)==1)
        index=candidates[0]
        trace.append(dict(bits=bits+1,modulus=mod,low=low,low_image=phi[low]%mod,
            high=high,high_image=phi[high]%mod,target=target%mod,chosen=index))
    check('atlas_inverse_search',[n for n in range(64) if phi[n]%64==13]==[index])
    row_modulus=2048
    diagonal=comb(4*index+address,4*index)
    summands=[comb(4*index+address,4*k)*modular[address][k]%row_modulus for k in range(index)]
    row_sum=sum(summands)%row_modulus
    recovered_c=-row_sum*pow(diagonal,-1,row_modulus)%row_modulus
    recovered_u=factorial(address)*recovered_c%row_modulus
    check('atlas_inverse_row_witness',recovered_c==modular[address][index]%row_modulus)
    check('atlas_inverse_row_witness',recovered_u==418)
    row_witness=dict(index=index,address=address,modulus=row_modulus,diagonal=diagonal,
        inverse_diagonal=pow(diagonal,-1,row_modulus),summands=summands,
        sum=row_sum,normalized=recovered_c,original=recovered_u)

    signed_even=[(-1)**n*v for n,v in enumerate(reciprocal_recurrence(2,1,13))]
    full=[int(signed_even[n//2]) if n%2==0 else 0 for n in range(25)]
    modes=[]
    for prime in (3,5,7):
        unit=[1]+[0]*(prime-1)
        source=[0]*prime
        source[1]=source[-1]=pow(2,-1,prime)
        nilpotent=[(x-y)%prime for x,y in zip(source,unit)]
        term=unit
        inverse_weights=[0]*prime
        for r in range(prime):
            inverse_weights=[(a+(-1)**r*b)%prime for a,b in zip(inverse_weights,term)]
            term=cyclic_product(term,nilpotent,prime)
        check('atlas_mode_nilpotence',term==[0]*prime)
        check('atlas_mode_inverse',cyclic_product(source,inverse_weights,prime)==unit)
        check('atlas_mode_inverse',cyclic_product(inverse_weights,source,prime)==unit)
        values=[sum(weight*pow(u,n,prime) for u,weight in enumerate(inverse_weights))%prime for n in range(25)]
        check('atlas_modes_euler_values',values==[v%prime for v in full])
        q=[(1+(-1)**n)*pow(2,-1,prime)%prime for n in range(25)]
        for n in range(25):
            product=sum(comb(n,k)*q[k]*values[n-k] for k in range(n+1))%prime
            check('atlas_modes_hurwitz_product',product==int(n==0))
        modes.append(dict(prime=prime,source=source,weights=inverse_weights,values=values))
    check('atlas_display',modes[1]['weights']==[1,1,4,4,1])
    check('atlas_positive_tail_control',full[0]%5!=full[4]%5)
    check('atlas_factorial_nonunit',factorial(5)%5==0)

    size=17
    first,second=stirling_tables(size)
    identity=[[int(i==j) for j in range(size)] for i in range(size)]
    check('atlas_stirling_inverse',matrix_product(first,second)==identity)
    check('atlas_stirling_inverse',matrix_product(second,first)==identity)
    log=[F(0)]+[F((-1)**(n+1),n) for n in range(1,size)]
    exponential=[F(0)]+[F(1,factorial(n)) for n in range(1,size)]
    identity_series=[F(0),F(1)]+[F(0)]*(size-2)
    check('atlas_log_exp_inverse',compose_series(log,exponential,size)==identity_series)
    check('atlas_log_exp_inverse',compose_series(exponential,log,size)==identity_series)
    egf=[F(full[n],factorial(n)) for n in range(size)]
    logarithmic=compose_series(egf,log,size)
    transformed=matrix_vector(first,full[:size])
    check('atlas_log_stirling',transformed==[logarithmic[n]*factorial(n) for n in range(size)])
    check('atlas_stirling_recovery',matrix_vector(second,transformed)==full[:size])
    rational=mul([1,1],inverse([1,1,F(1,2)],size),size)
    check('atlas_log_rational_form',logarithmic==rational)
    shift=compose_series([F(full[n+1],factorial(n)) for n in range(size)],log,size)
    extra_log=log+[F((-1)**(size+1),size)]
    extra_composed=compose_series([F(full[n],factorial(n)) for n in range(size+1)],extra_log,size+1)
    extra_rational=mul([1,1],inverse([1,1,F(1,2)],size+1),size+1)
    check('atlas_log_extra_degree',extra_composed[-1]==extra_rational[-1])
    extended=transformed+[extra_rational[-1]*factorial(size)]
    theta=[extended[n+1]+n*transformed[n] for n in range(size)]
    check('atlas_transported_derivative',theta==[shift[n]*factorial(n) for n in range(size)])
    for n in range(2,size):
        check('atlas_log_integer_recurrence',transformed[n]==-n*transformed[n-1]-comb(n,2)*transformed[n-2])
    check('atlas_display',transformed[:9]==[1,0,-1,3,-6,0,90,-630,2520])
    return dict(quartic=[[str(c) for c in values] for values in packets],newton_prefix=[[str(c) for c in row] for row in newton],
        gains=gains,original_gains=original_gains,modular_coefficients=modular,modulus=modulus,
        phi_residues=phi_tables,permutations=permutations,periods=periods,inverse_trace=trace,
        inverse_address=2,inverse_target=13,inverse_bits=6,inverse_index=index,modes=modes,
        inverse_row_witness=row_witness,
        stirling_first=first,stirling_second=second,full_euler=full,logarithmic_euler=[int(v) for v in transformed],
        logarithmic_ordinary=[str(v) for v in logarithmic],derivative_pullback=[str(v) for v in shift])


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

    # Infinite transforms tested through their declared, exact finite blocks.
    matrix_size=12
    identity=[[F(n == j) for j in range(matrix_size)] for n in range(matrix_size)]
    matrices={}
    for chart in (2,3,5,7):
        kernel=local_kernel(chart,matrix_size)
        inverse_coefficients=local_inverse_kernel(chart,matrix_size)
        forward=coefficient_matrix(kernel,matrix_size)
        backward=coefficient_matrix(inverse_coefficients,matrix_size)
        matrices[chart]=forward
        for product in (matrix_product(forward,backward),matrix_product(backward,forward)):
            for n in range(matrix_size):
                for j in range(matrix_size):
                    check('local_matrix_inverse_entries',product[n][j] == identity[n][j])
        source=[local_source(chart,2*n) for n in range(matrix_size)]
        target=[(-1)**n*s[n] for n in range(matrix_size)]
        for actual,expected_value in zip(matrix_vector(forward,source),target):
            check('local_matrix_reconstruction',actual == expected_value)
        for actual,expected_value in zip(matrix_vector(backward,target),source):
            check('local_matrix_inverse_reconstruction',actual == expected_value)
        ordinary=toeplitz_matrix([v/factorial(2*n) for n,v in enumerate(kernel)],matrix_size)
        for n in range(matrix_size):
            for j in range(matrix_size):
                check('factorial_matrix_conjugation',forward[n][j]
                      == F(factorial(2*n),factorial(2*j))*ordinary[n][j])
        for length in range(1,matrix_size+1):
            block=lambda a:[row[:length] for row in a[:length]]
            check('stable_triangular_prefixes',matrix_product(block(forward),block(backward)) == block(identity))
    for left,right in ((2,3),(3,5),(5,2)):
        a,b_kernel=local_kernel(left,matrix_size),local_kernel(right,matrix_size)
        convolution=[sum(comb(2*n,2*r)*a[r]*b_kernel[n-r] for r in range(n+1))
                     for n in range(matrix_size)]
        product=matrix_product(matrices[left],matrices[right])
        combined=coefficient_matrix(convolution,matrix_size)
        for n in range(matrix_size):
            for j in range(matrix_size):
                check('coefficient_matrix_composition',product[n][j] == combined[n][j])
    p,q=pascal_matrix(matrix_size),pascal_matrix(matrix_size,inverse=True)
    product=matrix_product(p,q)
    for n in range(matrix_size):
        for j in range(matrix_size):
            check('pascal_inverse_entries',product[n][j] == identity[n][j])
    euler_vector=[as_integer((-1)**n*s[n]) for n in range(matrix_size)]
    differences=difference_coefficients(euler_vector)
    for actual,expected_value in zip(matrix_vector(q,euler_vector),differences):
        check('pascal_coefficient_coordinates',actual == expected_value)
    for actual,expected_value in zip(matrix_vector(p,differences),euler_vector):
        check('pascal_coefficient_coordinates',actual == expected_value)
    for spacing in range(1,4):
        for offset in range(spacing):
            count=3*spacing+offset+1
            selector=[[F(j == spacing*k+offset) for j in range(count)] for k in range(4)]
            conjugated=matrix_product(matrix_product(pascal_matrix(4,inverse=True),selector),pascal_matrix(count))
            for k in range(4):
                weights=transfer_row(spacing,offset,k)
                expected_row=list(weights)+[F(0)]*(count-len(weights))
                for actual,expected_value in zip(conjugated[k],expected_row):
                    check('sampling_pascal_conjugation',actual == expected_value)
            lane=[euler_vector[spacing*k+offset] for k in range(4)]
            direct=difference_coefficients(lane)
            for actual,expected_value in zip(matrix_vector(conjugated,differences[:count]),direct):
                check('sampling_matrix_application',actual == expected_value)
    sampling=[list(transfer_row(2,0,k))+[F(0)]*(5-len(transfer_row(2,0,k))) for k in range(3)]
    correct_cutoff=matrix_vector(sampling,differences[:5])
    wrong_cutoff=matrix_vector([row[:3] for row in sampling],differences[:3])
    check('sampling_cutoff_counterexample',correct_cutoff == [1,4,1376] and wrong_cutoff == [1,4,32])
    wrong_ordinary=toeplitz_matrix([v/factorial(2*r) for r,v in enumerate(local_kernel(3,2))],2)
    check('matrix_normalization_counterexample',matrix_vector(wrong_ordinary,[1,17]) == [1,8])

    # Regroup a scalar infinite Toeplitz operator into two packet blocks.
    packet_size=6
    cosine_coefficients=[F((-1)**n,factorial(2*n)) for n in range(2*packet_size)]
    scalar_operator=toeplitz_matrix(cosine_coefficients,2*packet_size)
    permutation=list(range(0,2*packet_size,2))+list(range(1,2*packet_size,2))
    regrouped=[[scalar_operator[n][j] for j in permutation] for n in permutation]
    packet_c=[F(1,factorial(4*n)) for n in range(packet_size)]
    packet_d=[-F(1,factorial(4*n+2)) for n in range(packet_size)]
    cc=toeplitz_matrix(packet_c,packet_size)
    dd=toeplitz_matrix(packet_d,packet_size)
    ud=toeplitz_matrix([F(0)]+packet_d[:-1],packet_size)
    block_operator=[cc[n]+ud[n] for n in range(packet_size)]+[dd[n]+cc[n] for n in range(packet_size)]
    for n in range(2*packet_size):
        for j in range(2*packet_size):
            check('infinite_packet_block_entries',regrouped[n][j] == block_operator[n][j])
    original=[s[n]/factorial(2*n) for n in range(2*packet_size)]
    packet_vector=[original[n] for n in permutation]
    for n,value in enumerate(matrix_vector(block_operator,packet_vector)):
        check('packet_block_inverse_application',value == (n == 0))
    matrix_examples=dict(local_size=matrix_size,
        odd_three=[[str(v) for v in row[:5]] for row in matrices[3][:5]],
        dyadic=[[str(v) for v in row[:5]] for row in matrices[2][:5]],
        odd_three_inverse=[[str(v) for v in row[:5]] for row in coefficient_matrix(local_inverse_kernel(3,matrix_size),matrix_size)[:5]],
        sampling_two=[[str(v) for v in row] for row in sampling],
        correct_sampling_cutoff=[str(v) for v in correct_cutoff],wrong_sampling_cutoff=[str(v) for v in wrong_cutoff])

    # Exact base changes between local source coordinates, before modular reduction.
    base_size=8
    charts=(2,3,5,7)
    base_changes={}
    for source_chart in charts:
        for target_chart in charts:
            inverse_target=coefficient_matrix(local_inverse_kernel(target_chart,base_size),base_size)
            forward_source=[row[:base_size] for row in matrices[source_chart][:base_size]]
            change=matrix_product(inverse_target,forward_source)
            base_changes[source_chart,target_chart]=change
            source_vector=[local_source(source_chart,2*n) for n in range(base_size)]
            target_vector=[local_source(target_chart,2*n) for n in range(base_size)]
            for actual,expected_value in zip(matrix_vector(change,source_vector),target_vector):
                check('local_base_change_values',actual == expected_value)
            for row in change:
                for value in row:
                    check('dyadic_integral_base_change',value.denominator % 2 == 1)
                    if source_chart != 2 and target_chart != 2:
                        check('odd_integral_base_change',value.denominator == 1)
    for source_chart in charts:
        for intermediate in charts:
            for target_chart in charts:
                composed=matrix_product(base_changes[intermediate,target_chart],base_changes[source_chart,intermediate])
                direct=base_changes[source_chart,target_chart]
                for n in range(base_size):
                    for j in range(base_size):
                        check('base_change_cocycle_entries',composed[n][j] == direct[n][j])
    loss_entry=base_changes[3,2][4][2]
    perturbation=[F(0)]*base_size
    perturbation[2]=9
    output_error=matrix_vector(base_changes[3,2],perturbation)[4]
    check('base_change_precision_loss',loss_entry == F(215264,3))
    check('base_change_precision_loss',output_error == 645792 and valuation(output_error,3) == 1)
    check('base_change_precision_loss',valuation(loss_entry,3) == -1 and valuation(loss_entry,2) == 5)
    ladders=[]
    for chart in (2,3):
        rows=local_row_record(chart,4)['rows']
        for depth in range(4):
            modulus=chart**(4*depth+3 if chart==2 else 2*depth+2)
            partial=F(rows[depth]['partial'])
            residue=rational_residue(partial,modulus)
            check('displayed_supercongruence_ladders',residue == 1385 % modulus)
            ladders.append(dict(chart=chart,depth=depth,modulus=modulus,partial=str(partial),
                                residue=residue,error=rows[depth]['error'],valuation=rows[depth]['valuation']))
    odd_source=[local_source(3,2*n) for n in range(5)]
    changed=matrix_vector([row[:5] for row in base_changes[3,5][:5]],odd_source)
    check('odd_chart_modulus_transport',rational_residue(changed[2],81) == 7)
    check('odd_chart_modulus_transport',F(896)+192*17+545 == changed[2] == 4705)
    check('modulus_change_counterexample',1 % 81 == 82 % 81 and 1 % 25 != 82 % 25)
    crt_residue=9+32*((8-9)*pow(32,-1,81) % 81)
    check('coprime_supercongruence_combination',32*38-81*15 == 1)
    check('coprime_supercongruence_combination',crt_residue == 1385 and crt_residue % 81 == 8 and crt_residue % 32 == 9)
    for spacing in range(1,7):
        for address in range(spacing):
            packet=congruential_packet(spacing,address,9)
            triangular=[F(1)]
            clearing=1
            for n in range(9):
                if n:
                    diagonal=comb(spacing*n+address,spacing*n)
                    triangular.append(-sum(comb(spacing*n+address,spacing*j)*triangular[j] for j in range(n))/F(diagonal))
                    clearing*=diagonal
                check('congruential_family_routes',packet[n] == triangular[n])
                check('congruential_denominator_clearing',(clearing*packet[n]).denominator == 1)
    family_four=congruential_packet(4,0,9)
    family_two=congruential_packet(2,0,9)
    family_boundary=congruential_packet(2,1,9)
    for n in range(9):
        check('congruential_family_specializations',family_four[n] == (-1)**n*b[n])
        check('congruential_family_specializations',family_two[n] == (-1)**n*s[n])
        check('congruential_family_specializations',family_boundary[n] == (2-2**(2*n))*bernoulli[2*n])
    base_change_examples=dict(size=base_size,
        three_to_five=[[str(v) for v in row[:5]] for row in base_changes[3,5][:5]],
        three_to_two=[[str(v) for v in row[:5]] for row in base_changes[3,2][:5]],
        three_adic_loss_entry=str(loss_entry),input_error=9,output_error=str(output_error),
        congruence_ladders=ladders,crt=dict(moduli=[81,32],residues=[8,9],residue=crt_residue,modulus=81*32),
        family_four=[str(v) for v in family_four[:5]])

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

    fibonacci=fibonacci_examples(euler_polynomials,signed,check)
    literature=literature_examples(euler_polynomials,check)
    atlas=atlas_examples(check)
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
        matrix_examples=matrix_examples,
        base_change_examples=base_change_examples,
        fibonacci=fibonacci,
        literature=literature,
        atlas=atlas,
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
            local_matrix_size=12,packet_block_size=6,pascal_matrix_size=12,
            sampling_matrix_spacings=[1,3],sampling_matrix_orders=[0,3],
            base_change_charts=[2,3,5,7],base_change_matrix_size=8,base_change_all_triples=True,
            congruential_family_spacing=[1,6],congruential_addresses='every 0<=j<N',congruential_index=[0,8],
            fibonacci_polynomial_degree=[0,12],fibonacci_sequence_length=16,
            fibonacci_companion_power=[0,12],fibonacci_state_index=[0,14],
            literature_packet_step=[0,12],literature_packet_address=[0,5],literature_packet_index=[0,8],
            literature_dyadic_refinement=[0,4],literature_difference_base=[0,6],literature_difference_order=[0,5],
            literature_binomial_address=[0,3],literature_binomial_index=[0,6],literature_calculus_degree=[0,8],
            quartic_exact_index=[0,47],quartic_difference_base=[0,6],quartic_difference_step=[1,8],quartic_difference_order=[0,5],
            quartic_displacement_base=[0,8],quartic_displacement_step=[1,16],quartic_modular_index=[0,255],quartic_modulus=8192,
            residue_permutation_bits=[1,8],isometry_pair_indices=[0,31],period_precision=[0,8],inverse_bits=6,
            mode_primes=[3,5,7],mode_full_degree=[0,24],stirling_degree=16,log_derivative_input_degree=17,
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
             directory/'local-reconstruction.csv',directory/'coefficient-matrices.csv',directory/'congruence-ladders.csv',
             directory/'fibonacci-transfer.csv',directory/'fibonacci-precision.csv',directory/'polynomial-calculus.csv',
             directory/'quartic-addresses.csv',directory/'dyadic-inverse.csv',directory/'euler-coordinate-atlas.csv']
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
    with paths[4].open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['transform','chart','row','column','value','coordinates'])
        def write_matrix(name,chart,matrix,coordinates):
            for n,row in enumerate(matrix):
                for j,value in enumerate(row):
                    writer.writerow([name,chart,n,j,str(value),coordinates])
        for chart in (2,3,5,7):
            for name,kernel in [('local_forward',local_kernel(chart,12)),
                                ('local_inverse',local_inverse_kernel(chart,12))]:
                write_matrix(name,chart,coefficient_matrix(kernel,12),'even EGF numerators')
        write_matrix('pascal_reconstruction','',pascal_matrix(12),'sequence from differences')
        write_matrix('pascal_difference','',pascal_matrix(12,inverse=True),'differences from sequence')
        write_matrix('sampling_M2_s0','',report['matrix_examples']['sampling_two'],'Newton differences')
        write_matrix('source_base_change','3_to_5',report['base_change_examples']['three_to_five'],'even EGF source numerators')
        write_matrix('source_base_change','3_to_2',report['base_change_examples']['three_to_two'],'even EGF source numerators')
    with paths[5].open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['chart','depth','proved_modulus','partial','residue','error','exact_error_valuation'])
        for row in report['base_change_examples']['congruence_ladders']:
            writer.writerow([row[key] for key in ('chart','depth','modulus','partial','residue','error','valuation')])
    with paths[6].open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['transform','row','column','value'])
        for name in ('polynomial_connection','polynomial_inverse','recurrence_analysis',
                     'recurrence_synthesis','sequence_transfer','sequence_inverse'):
            for i,row in enumerate(report['fibonacci'][name]):
                for j,value in enumerate(row):
                    writer.writerow([name,i,j,value])
    with paths[7].open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        keys=['step','refinement','depth','target','partial','error','modulus','valuation']
        writer.writerow(keys)
        for row in report['literature']['precision']:
            writer.writerow(['infinity' if row[key] is None else row[key] for key in keys])
    with paths[8].open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['source_degree','operator','row','column','value'])
        for degree,record in report['literature']['calculus'].items():
            for name in ('integral','derivative','euler_derivative','connection','inverse_connection'):
                for i,row in enumerate(record[name]):
                    for j,value in enumerate(row):
                        writer.writerow([degree,name,i,j,value])
    with paths[9].open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['address','index','normalized_C','original_U','newton_coefficient','modulus','modular_C','phi_mod_256'])
        atlas=report['atlas']
        for address in range(4):
            for n in range(256):
                exact=atlas['quartic'][address][n] if n<48 else ''
                original=str(factorial(address)*F(exact)) if exact else ''
                newton=atlas['newton_prefix'][address][n] if n<13 else ''
                writer.writerow([address,n,exact,original,newton,8192,atlas['modular_coefficients'][address][n],atlas['phi_residues'][address][n]])
    with paths[10].open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['bits','modulus','low','low_image','high','high_image','target','chosen'],lineterminator='\n')
        writer.writeheader()
        writer.writerows(report['atlas']['inverse_trace'])
    with paths[11].open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['full_degree','signed_euler','logarithmic_hurwitz','logarithmic_ordinary','mod_3','mod_5','mod_7'])
        for n in range(25):
            writer.writerow([n,report['atlas']['full_euler'][n],
                report['atlas']['logarithmic_euler'][n] if n<17 else '',
                report['atlas']['logarithmic_ordinary'][n] if n<17 else '',
                *[row['values'][n] for row in report['atlas']['modes']]])


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
    print('Matrix checks: inverse, composition, factorial normalization, packets, Pascal sampling')
    print('Sampling cutoff control: 3 columns give 32; 5 columns give 1376')
    print('Base changes: exact cocycle; prime-dependent precision checked')
    print('Supercongruence combination: 8 mod 81 and 9 mod 32 give 1385 mod 2592')
    print('Fibonacci polynomial coordinates: E_4(x) = 2 B_0 + 5 B_1 - 3 B_2 - 2 B_3 + B_4')
    print('Fibonacci recurrence defects: 5, -65, 1441, -51845')
    print('Reversible sequence transfer: 1, -1, 5, -61, 1385 -> 1, 1, 2, 3, 5')
    print('Paper IX Fibonacci packets: step 3 gives u[k+2] = 4*u[k+1] + u[k]')
    print('Fibonacci precision ladder: F_37 = 24157817; tail valuations 3, 6, 9, exact')
    print('Euler/Fibonacci calculus: full round trip is I_4; integral = 5/4')
    print('Quartic address gains: normalized 1, 1, 4, 2; original 1, 1, 5, 3')
    print('Dyadic inverse: address 2, target 13 mod 64 -> index',report['atlas']['inverse_index'])
    print('Finite mode inverse mod 5: weights 1, 1, -1, -1, 1')
    print('Logarithmic Euler coordinates: 1, 0, -1, 3, -6, 0, 90, -630, 2520')
    print('Signed Euler difference coordinates:', ', '.join(map(str,report['difference_coordinates'])))
    print('Spacing-two lane: 1, 5, 1385; differences: 1, 4, 1376')
    print('Refinement: 2*4 + 1376 = 1384')
    print('Prime residual: 2*(-2) + 8 = 4')
    print('Newton residual orders:', ', '.join(map(str,report['newton_residual_orders'])))
    print('PASS: Euler packets, polynomials and residuals')


if __name__ == '__main__':
    main()
