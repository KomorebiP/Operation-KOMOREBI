#!/usr/bin/env python3
"""Seven exact finite groups for the operator-cutoff study.

Contract: rational monomial matrices at N=0,...,6; all 63 words in D,M of
length 0,...,5 at N=0,...,5, compared on each basis vector (1323 controls);
the displayed N=3 witnesses and falling-basis transport; primes 2,3,5,7
at N=p-1, all 87 quotient basis-product pairs, and one negative field control.
All arithmetic is exact Fraction or integer modular arithmetic. General
padding and characteristic arguments are supplied separately in the text.

Run: python -B examples/operator_cutoffs.py
Standard library plus sibling guide helpers. Prints JSON; writes no files.
"""
from fractions import Fraction as F
from itertools import product
from math import comb
import json

from operator_guide import M, v, eye, mm, sub, scale, norm_inf, rank


C = M([[1, 0, 0, 0], [0, 1, -1, 2], [0, 0, 1, -3], [0, 0, 0, 1]])
CI = M([[1, 0, 0, 0], [0, 1, 1, 1], [0, 0, 1, 3], [0, 0, 0, 1]])


def matrices(cutoff):
    size = cutoff+1
    derivative = M([[j if i == j-1 else 0 for j in range(size)] for i in range(size)])
    multiply = M([[int(i == j+1) for j in range(size)] for i in range(size)])
    top = M([[int(i == j == cutoff) for j in range(size)] for i in range(size)])
    return derivative, multiply, top


def trace(a):
    return sum(a[i][i] for i in range(len(a)))


def values(column):
    return tuple(row[0] for row in column)


def padding(word):
    change = peak = 0
    for symbol in reversed(word):
        change += 1 if symbol == 'M' else -1
        peak = max(peak, change)
    return peak


def word_matrix(word, cutoff):
    derivative, multiply, _ = matrices(cutoff)
    result = eye(cutoff+1)
    for symbol in reversed(word):
        result = mm(derivative if symbol == 'D' else multiply, result)
    return result


def full_polynomial_word(word, coefficients):
    """Operate on a growing coefficient list, with no intermediate cutoff."""
    coefficients = list(map(F, coefficients))
    for symbol in reversed(word):
        if symbol == 'M':
            coefficients = [F(0)]+coefficients
        else:
            coefficients = [j*coefficients[j] for j in range(1, len(coefficients))] or [F(0)]
    return tuple(coefficients)


def cropped(coefficients, cutoff):
    return tuple(coefficients[i] if i < len(coefficients) else F(0) for i in range(cutoff+1))


def mod_matrix(a, prime):
    assert all(x.denominator == 1 for row in a for x in row)
    return tuple(tuple(int(x) % prime for x in row) for row in a)


def quotient_product(a, b, prime):
    return tuple(sum(a[j]*b[k-j] for j in range(k+1)) % prime for k in range(prime))


def quotient_derivative(a, prime):
    return tuple(((k+1)*a[k+1]) % prime if k+1 < prime else 0 for k in range(prime))


def run_audit():
    groups = {}
    commutators = []
    for cutoff in range(7):
        derivative, multiply, top = matrices(cutoff)
        commutator = sub(mm(derivative, multiply), mm(multiply, derivative))
        assert commutator == sub(eye(cutoff+1), scale(cutoff+1, top))
        assert trace(commutator) == 0
        commutators.append(tuple(commutator[i][i] for i in range(cutoff+1)))
    groups['finite-commutators'] = {'cutoffs': list(range(7)), 'diagonals': commutators}

    derivative, multiply, top = matrices(3)
    fixture = v(1, 2, 3, 4)
    dm = mm(derivative, multiply)
    md = mm(multiply, derivative)
    commutator = sub(dm, md)
    defect = sub(commutator, eye(4))
    padded_dm = tuple(row[:4] for row in word_matrix('DM', 4)[:4])
    assert sub(padded_dm, md) == eye(4)
    groups['boundary-witness'] = {'D3': derivative, 'M3': multiply,
        'DM_f': values(mm(dm, fixture)), 'MD_f': values(mm(md, fixture)),
        'commutator_f': values(mm(commutator, fixture)), 'defect_f': values(mm(defect, fixture)),
        'padded_DM_diagonal': tuple(padded_dm[i][i] for i in range(4))}

    words = [''.join(letters) for length in range(6) for letters in product('DM', repeat=length)]
    assert len(words) == 63
    combinations = basis_controls = 0
    for cutoff in range(6):
        for word in words:
            matrix = word_matrix(word, cutoff+padding(word))
            for basis_index in range(cutoff+1):
                coefficients = tuple(int(j == basis_index) for j in range(cutoff+1))
                expected = cropped(full_polynomial_word(word, coefficients), cutoff)
                actual = tuple(matrix[row][basis_index] for row in range(cutoff+1))
                assert actual == expected, (cutoff, word, basis_index)
                basis_controls += 1
            combinations += 1
    assert combinations == 378 and basis_controls == 1323
    groups['safe-padding'] = {'cutoffs': [0, 5], 'word_lengths': [0, 5], 'word_count': len(words),
        'word_cutoff_combinations': combinations, 'basis_controls': basis_controls,
        'example_padding': {word: padding(word) for word in ('DM', 'MD', 'DDMM', 'MDMD', 'DDDMM')}}

    full_long = tuple(row[:4] for row in word_matrix('DDMM', 5)[:4])
    short_long = word_matrix('DDMM', 3)
    one_extra = tuple(row[:4] for row in word_matrix('DDMM', 4)[:4])
    assert tuple(full_long[i][i] for i in range(4)) == (2, 6, 12, 20)
    assert one_extra != full_long and short_long != full_long
    groups['longer-word'] = {'full_diagonal': tuple(full_long[i][i] for i in range(4)),
        'unpadded_diagonal': tuple(short_long[i][i] for i in range(4)),
        'one_extra_diagonal': tuple(one_extra[i][i] for i in range(4)),
        'full_f': values(mm(full_long, fixture)), 'unpadded_f': values(mm(short_long, fixture)),
        'error_norm': norm_inf(sub(short_long, full_long))}

    assert mm(C, CI) == mm(CI, C) == eye(4)
    transported_d = mm(mm(C, derivative), CI)
    direct_difference = M([[comb(j, i) if j > i else 0 for j in range(4)] for i in range(4)])
    assert transported_d == direct_difference
    transported_m = mm(mm(C, multiply), CI)
    transported_top = mm(mm(C, top), CI)
    transported_commutator = sub(mm(transported_d, transported_m), mm(transported_m, transported_d))
    assert transported_commutator == sub(eye(4), scale(4, transported_top))
    assert rank(transported_top) == 1
    cube = v(0, 0, 0, 1)
    assert mm(transported_top, cube) == v(0, 2, -3, 1)
    # Full raising of x^3 is x(x-1)^3; remove b4 for the transported cutoff.
    full_raise = (F(0), F(-1), F(3), F(-3), F(1))
    b4 = (F(0), F(-6), F(11), F(-6), F(1))
    transported_raise = tuple(a-b for a, b in zip(full_raise, b4))[:4]
    assert values(mm(transported_m, cube)) == transported_raise
    groups['transported-cutoff'] = {'C': C, 'C_inverse': CI, 'top_packet': transported_top,
        'forward_difference': transported_d, 'raised_cube': transported_raise,
        'ordinary_cutoff_raised_cube': full_raise[:4],
        'boundary_on_cube': values(mm(scale(-4, transported_top), cube))}

    norms = []
    for cutoff in range(7):
        d, m, _ = matrices(cutoff)
        error = sub(sub(mm(d, m), mm(m, d)), eye(cutoff+1))
        assert norm_inf(error) == cutoff+1
        norms.append(norm_inf(error))
    transported_error = scale(-4, transported_top)
    assert norm_inf(transported_error) == 12
    assert max(abs(x) for x in values(mm(transported_error, cube))) == 12
    # The fixed cubic is eventually interior, while each top basis input detects the edge.
    for cutoff in range(4, 7):
        d, m, _ = matrices(cutoff)
        error = sub(sub(mm(d, m), mm(m, d)), eye(cutoff+1))
        assert mm(error, v(*cropped((1, 2, 3, 4), cutoff))) == v(*([0]*(cutoff+1)))
    groups['coefficient-norms'] = {'cutoffs': list(range(7)), 'defect_norms': norms,
        'transported_norm': norm_inf(transported_error), 'fixed_cubic_interior_cutoffs': [4, 5, 6]}

    primes = (2, 3, 5, 7)
    pair_count = 0
    for prime in primes:
        d, m, _ = matrices(prime-1)
        assert mod_matrix(sub(mm(d, m), mm(m, d)), prime) == mod_matrix(eye(prime), prime)
        assert int(trace(eye(prime))) % prime == 0
        basis = [tuple(int(i == j) for i in range(prime)) for j in range(prime)]
        for a, b in product(basis, repeat=2):
            left = quotient_derivative(quotient_product(a, b, prime), prime)
            first = quotient_product(quotient_derivative(a, prime), b, prime)
            second = quotient_product(a, quotient_derivative(b, prime), prime)
            assert left == tuple((x+y) % prime for x, y in zip(first, second))
            pair_count += 1
    assert pair_count == 87
    d, m, _ = matrices(3)
    negative = mod_matrix(sub(mm(d, m), mm(m, d)), 3)
    assert negative != mod_matrix(eye(4), 3)
    assert cropped(full_polynomial_word('D', (0, 0, 0, 0, 1)), 3) == (0, 0, 0, 4)
    groups['finite-field-controls'] = {'primes': primes, 'quotient_basis_product_pairs': pair_count,
        'F3_cutoff3_commutator_diagonal': tuple(negative[i][i] for i in range(4)),
        'rational_quotient_representative_derivatives': (0, 4)}
    assert len(groups) == 7
    return {'status': 'PASS', 'finite_example_groups': len(groups), 'groups': groups}


if __name__ == '__main__':
    print(json.dumps(run_audit(), default=str, indent=2))
