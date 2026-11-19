"""Exact polynomial-weighted Hankel moments and quasiseparable determinants.

Author: Komorebi P.

Weights are specified in the falling-factorial basis:
P(m) = sum_d a[d] m^(underline d).
Coefficients and derivative parameter c are rational. The underlying
theorems hold over characteristic-zero fields, including complex parameters.
This implementation uses Python's standard-library Fraction throughout.

The Chebyshev moment transform and off-diagonal generator are derived in
research/sequence-closed-forms/POLYNOMIAL_HANKEL_STRUCTURE.md.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb, factorial


def _weights(coefficients):
    if not coefficients:
        raise ValueError("At least one polynomial coefficient is required")
    values = tuple(Fraction(value) for value in coefficients)
    while len(values) > 1 and values[-1] == 0:
        values = values[:-1]
    return values


def power_to_falling(power_coefficients):
    """Convert sum b_k*m^k to sum a_d*m^(underline d), exactly."""
    values = _weights(power_coefficients)
    degree = len(values) - 1
    stirling = [[0] * (degree + 1) for _ in range(degree + 1)]
    stirling[0][0] = 1
    for n in range(1, degree + 1):
        for k in range(1, n + 1):
            stirling[n][k] = stirling[n - 1][k - 1] + k * stirling[n - 1][k]
    return tuple(sum(values[k] * stirling[k][d]
                     for k in range(d, degree + 1))
                 for d in range(degree + 1))


def falling_integer(n, degree):
    value = 1
    for j in range(degree):
        value *= n - j
    return value


def monomial_moment(index, coefficients, c=0):
    """L_(P,c)[x^index], including the empty and odd-moment conventions."""
    if index < 0:
        return Fraction(0)
    a = _weights(coefficients)
    m = index // 2
    original = comb(2 * m, m) * sum(
        coefficient * falling_integer(m, d)
        for d, coefficient in enumerate(a))
    return original if index % 2 == 0 else Fraction(c) * index * original


def _mul_linear_factors(squares):
    """Return ascending coefficients of prod_h (y - squares[h])."""
    polynomial = [Fraction(1)]
    for square in squares:
        nxt = [Fraction(0)] * (len(polynomial) + 1)
        for k, value in enumerate(polynomial):
            nxt[k] -= square * value
            nxt[k + 1] += value
        polynomial = nxt
    return polynomial


@lru_cache(maxsize=None)
def chebyshev_transform_coefficients(coefficients):
    """Odd polynomials U(t) and V(t) as coefficients of t^(2k+1).

    For even n>0, F_P[C_n] = U(n). For odd n>0,
    F_P[C'_n] = V(n). At n=0, F_P[C_0] = 2a_0.
    """
    a = _weights(coefficients)
    degree = len(a) - 1
    u = [Fraction(0) for _ in range(degree)]
    v = [Fraction(0) for _ in range(degree + 1)]
    for d, coefficient in enumerate(a):
        if not coefficient:
            continue
        if d >= 1:
            f = _mul_linear_factors((2*j)**2 for j in range(1, d))
            scale = coefficient / (4**(d - 1) * factorial(d - 1))
            for k, term in enumerate(f):
                u[k] += scale * term
        f = _mul_linear_factors((2*j + 1)**2 for j in range(d))
        scale = coefficient / (4**d * factorial(d))
        for k, term in enumerate(f):
            v[k] += scale * term
    return tuple(u), tuple(v)


def _odd_polynomial(coefficients, index):
    return sum(value * index**(2*k+1)
               for k, value in enumerate(coefficients))


def chebyshev_even_moment(index, coefficients):
    """F_P[C_index] for a nonnegative even Chebyshev index."""
    if index < 0 or index % 2:
        raise ValueError("The Chebyshev index must be even and nonnegative")
    a = _weights(coefficients)
    if index == 0:
        return 2 * a[0]
    return _odd_polynomial(chebyshev_transform_coefficients(a)[0], index)


def chebyshev_derivative_moment(index, coefficients):
    """F_P[C'_index] for a positive odd Chebyshev index."""
    if index <= 0 or index % 2 != 1:
        raise ValueError("The derivative Chebyshev index must be positive and odd")
    a = _weights(coefficients)
    return _odd_polynomial(chebyshev_transform_coefficients(a)[1], index)


def chebyshev_gram_entry(i, j, coefficients, c=0):
    """Exact Gram entry for C_0=2 and C_n=2T_n(x/2), n>0."""
    if i < 0 or j < 0:
        raise ValueError("Gram indices must be nonnegative")
    a = _weights(coefficients)
    if i == j == 0:
        return 4 * a[0]
    u, v = chebyshev_transform_coefficients(a)
    if i == j:
        return 2 * a[0] + _odd_polynomial(u, 2 * i)
    total, gap = i + j, abs(i - j)
    if total % 2 == 0:
        return _odd_polynomial(u, total) + _odd_polynomial(u, gap)
    return Fraction(c) * (
        _odd_polynomial(v, total) + _odd_polynomial(v, gap))


def semiseparable_generators(coefficients, c, size):
    """Return U_i, V_j, diagonal for G_ij=U_i dot V_j whenever i>j.

    The generator has width 2(D+1), with D=degree P, independent of size.
    """
    if size < 0:
        raise ValueError("Matrix size must be nonnegative")
    a = _weights(coefficients)
    c = Fraction(c)
    upoly, vpoly = chebyshev_transform_coefficients(a)
    D = len(a) - 1
    lower_rows, lower_cols, diagonal = [], [], []
    for i in range(size):
        f = [
            2 * sum(upoly[h] * comb(2*h+1, 2*k) *
                    i**(2*h+1-2*k) for h in range(k, D))
            for k in range(D+1)
        ]
        g = [
            2 * sum(vpoly[h] * comb(2*h+1, 2*k) *
                    i**(2*h+1-2*k) for h in range(k, D+1))
            for k in range(D+1)
        ]
        parity = (-1)**i
        row = [(f[k]+c*g[k])/2 for k in range(D+1)]
        row += [parity*(f[k]-c*g[k])/2 for k in range(D+1)]
        col = [Fraction(i**(2*k)) for k in range(D+1)]
        col += [Fraction(parity*i**(2*k)) for k in range(D+1)]
        lower_rows.append(row)
        lower_cols.append(col)
        diagonal.append(
            4*a[0] if i==0 else
            2*a[0] + _odd_polynomial(upoly, 2*i))
    return lower_rows, lower_cols, diagonal


def _inverse_and_det(matrix):
    """Gauss-Jordan inverse and determinant; None if singular."""
    n = len(matrix)
    if not n:
        return Fraction(1), []
    a = [[Fraction(v) for v in row] for row in matrix]
    inverse = [[Fraction(i==j) for j in range(n)] for i in range(n)]
    det = Fraction(1)
    for k in range(n):
        pivot_row = next((i for i in range(k, n) if a[i][k]), None)
        if pivot_row is None:
            return Fraction(0), None
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            inverse[k], inverse[pivot_row] = inverse[pivot_row], inverse[k]
            det = -det
        pivot = a[k][k]
        det *= pivot
        for j in range(n):
            a[k][j] /= pivot
            inverse[k][j] /= pivot
        for i in range(n):
            if i == k or not a[i][k]:
                continue
            factor = a[i][k]
            for j in range(n):
                a[i][j] -= factor*a[k][j]
                inverse[i][j] -= factor*inverse[k][j]
    return det, inverse


def structured_hankel_prefixes(coefficients, c, max_size):
    """Compute every W_N(P,c) for 0<=N<=max_size by exact small-state Schur steps.

    Zero leading minors are retained, with block lookahead to the next
    nonsingular leading prefix. This does not invert a singular Schur pivot.
    No floating point or symbolic roots are used. For scalar nonsingular
    pivots after the initial block, the arithmetic cost is O(N*(D+1)^2);
    lookahead blocks can increase the cost at exceptional parameters.
    """
    if max_size < 0:
        raise ValueError("The maximum Hankel size must be nonnegative")
    a = _weights(coefficients)
    c = Fraction(c)
    result = [Fraction(1)] + [Fraction(0)]*max_size
    if max_size == 0 or not any(a):
        return result

    first = next(d for d, coefficient in enumerate(a) if coefficient)
    first_nonsingular = 2*first + 1
    if max_size < first_nonsingular:
        return result

    u, v, diagonal = semiseparable_generators(a, c, max_size+1)
    width = len(u[0])

    def gram(i, j):
        return (diagonal[i] if i==j else
                chebyshev_gram_entry(i, j, a, c))

    initial = [
        [gram(i, j) for j in range(first_nonsingular)]
        for i in range(first_nonsingular)
    ]
    det, inverse = _inverse_and_det(initial)
    if not det:
        raise ArithmeticError("The theoretically nonsingular initial block vanished")
    result[first_nonsingular] = det / 4

    # K_m = V_m^T (G_m)^(-1) V_m. Its dimension never depends on m.
    K = [
        [sum(v[i][p]*inverse[i][j]*v[j][q]
             for i in range(first_nonsingular)
             for j in range(first_nonsingular))
         for q in range(width)] for p in range(width)
    ]
    m = first_nonsingular
    while m < max_size:
        for length in range(1, max_size-m+1):
            new = list(range(m, m+length))
            Ku = [
                [sum(K[p][q]*u[index][q] for q in range(width))
                 for p in range(width)]
                for index in new
            ]
            schur = [
                [gram(x,y)-sum(u[x][p]*Ku[y-m][p]
                               for p in range(width))
                 for y in new] for x in new
            ]
            block_det, inverse_schur = _inverse_and_det(schur)
            if not block_det:
                continue
            w = [
                [Ku[index-m][p]-v[index][p] for p in range(width)]
                for index in new
            ]
            K = [
                [K[p][q]+sum(w[k][p]*inverse_schur[k][ell]*w[ell][q]
                              for k in range(length) for ell in range(length))
                 for q in range(width)] for p in range(width)
            ]
            det *= block_det
            result[m+length] = det / 4
            m += length
            break
        else:
            # All remaining leading prefixes are singular. Their values
            # were initialized to zero and require no division.
            break
    return result


def initial_nonsingular_formula(coefficients):
    """Return (first size, determinant) for nonzero P, or None for P=0."""
    a = _weights(coefficients)
    if not any(a):
        return None
    first = next(i for i, value in enumerate(a) if value)
    mass = a[first] * factorial(2*first) / factorial(first)
    size = 2*first+1
    return size, (-1)**first * mass**size


if __name__ == "__main__":
    print("Polynomial-weighted Hankel: exact Chebyshev generators and adaptive Schur minors.")
    sample = structured_hankel_prefixes([0,1],1,8)
    print("P(m)=m, c=1:", [str(x) for x in sample])
