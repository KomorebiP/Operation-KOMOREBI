"""Rational kernels, sharp rank and finite-state differential Hankel tails.

Author: Komorebi P. Exact Fraction arithmetic; standard library only.
Extends the existing differential Hankel implementation in this source tree.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import comb, factorial, gcd, lcm, prod
from sequence_polynomial_hankel import _weights
from sequence_differential_hankel import (
    algebraic_moment_generating_function, chebyshev_jet_polynomials,
    chebyshev_jet_gram_entry,
)


def parameters(weights, differential):
    a, c = _weights(weights), _weights(differential)
    return a, c, len(a)-1+len(c)-1


def _trim(values):
    values = list(values)
    while len(values)>1 and not values[-1]:
        values.pop()
    return tuple(values)


def evaluate(poly, x):
    value = F(0)
    for coefficient in reversed(poly):
        value = value*x+coefficient
    return value


def _multiply(left, right):
    result = [F(0)]*(len(left)+len(right)-1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            result[i+j] += x*y
    return _trim(result)


def linear_hankel_generating_function(a, b):
    """Numerator and denominator for P(m)=a+b*m, operator identity.

    Ascending coefficients, exact rational parameters. The constant term of
    the denominator is one at every specialization, including a=b=0.
    The displayed order-nine annihilator need not be minimal at special values.
    """
    a, b = F(a), F(b)
    numerator = (
        F(1), -17*a+12*b, 2*(64*a*a-77*a*b+24*b*b),
        -8*(70*a**3-105*a*a*b+51*a*b*b-7*b**3),
        8*a*(196*a**3-315*a*a*b+168*a*b*b-30*b**3),
        -32*a*(91*a**4-140*a**3*b+66*a*a*b*b-8*a*b**3-2*b**4),
        32*a**3*(112*a**3-147*a*a*b+48*a*b*b+2*b**3),
        -128*a**4*(2*a-b)*(11*a*a-5*a*b-b*b),
        640*a**7*(2*a-b), -256*a**9,
    )
    factor = _multiply((1, -2*a), (1, -4*(a-b), 4*a*a))
    denominator = _multiply(_multiply(factor, factor), factor)
    return _trim(numerator), denominator


def linear_hankel_determinants(a, b, max_size):
    """W_0,...,W_max_size from the uniform rational OGF, without pivot division."""
    if not isinstance(max_size, int) or max_size<0:
        raise ValueError('max_size must be a nonnegative integer')
    numerator, denominator = linear_hankel_generating_function(a, b)
    values = []
    for n in range(max_size+1):
        values.append((numerator[n] if n<len(numerator) else F(0))-
                      sum(denominator[j]*values[n-j]
                          for j in range(1, min(n, len(denominator)-1)+1)))
    return values


def branch_numerator_values(weights, differential):
    """Actual R(-1/2), R(1/2), and the predicted nonzero endpoint values."""
    a, c, M = parameters(weights, differential)
    R, _ = algebraic_moment_generating_function(a, c)
    top = a[-1]*c[-1]
    for j in range(M):
        top *= F(2*j+1, 2)
    return (evaluate(R, -F(1, 2)), evaluate(R, F(1, 2)),
            (-1)**(len(c)-1)*top, top)


def separated_minor_formula(rows, columns, weights, differential):
    """Exact 2M-square separated minor, depending only on top a_D*c_r.

    Each increasing index set must contain M even and M odd indices.
    Rows lie strictly above columns. No determinant algorithm is used.
    """
    a, c, M = parameters(weights, differential)
    rows, columns = tuple(rows), tuple(columns)
    if (not any(a) or not any(c) or M<1 or len(rows)!=2*M
            or len(columns)!=2*M or min(rows)<=max(columns)
            or min(columns)<0 or tuple(sorted(set(rows)))!=rows
            or tuple(sorted(set(columns)))!=columns
            or sum(i%2==0 for i in rows)!=M
            or sum(j%2==0 for j in columns)!=M):
        raise ValueError('requires nonzero inputs and separated parity-balanced 2M-square indices')

    def parity_sign(indices):
        return (-1)**sum(i%2 and j%2==0
                         for k, i in enumerate(indices) for j in indices[k+1:])

    def vandermonde(indices):
        return prod(j*j-i*i for k, i in enumerate(indices) for j in indices[k+1:])

    b = a[-1]*c[-1]/(4**(M-1)*factorial(M-1))
    binomials = prod(comb(2*M-1, 2*k) for k in range(M))
    value = ((-1)**((len(c)-1)*M)*4**M*parity_sign(rows)*parity_sign(columns)
             *b**(2*M)*binomials**2*prod(rows))
    for indices in (rows, columns):
        for parity in (0, 1):
            value *= vandermonde([i for i in indices if i%2==parity])
    return value


def canonical_kernel(weights, differential):
    """(H, p) with A(t)=H(t)/(1-t^2)^p, Phi(t)=1+t^2.

    L[x^n]=[t^n] A(t)*Phi(t)^n for every n>=0.
    For nonzero inputs p=2*(D+r) is the exact pole order at both +/-1.
    Zero inputs have H=0,p=0; constant inputs give constant A.
    """
    a, c, M = parameters(weights, differential)
    if not any(a) or not any(c):
        return (F(0),), 0
    R, _ = algebraic_moment_generating_function(a, c)
    H = [F(0)]*(4*M+1)
    for j, coefficient in enumerate(R):
        for k in range(2*M-j+1):
            H[j+2*k] += coefficient*comb(2*M-j, k)
    return _trim(H), 2*M


def kernel_moment(n, weights, differential):
    """Independent rational-kernel coefficient extraction; no moment recurrence."""
    if not isinstance(n, int) or n<0:
        raise ValueError('n must be a nonnegative integer')
    H, p = canonical_kernel(weights, differential)
    value = F(0)
    for j, coefficient in enumerate(H[:n+1]):
        if not coefficient or (n-j)%2:
            continue
        q = (n-j)//2
        if p:
            factor = sum(comb(n, k)*comb(p+q-k-1, q-k)
                         for k in range(min(n, q)+1))
        else:
            factor = comb(n, q) if q<=n else 0
        value += coefficient*factor
    return value


def difference_stencil(M):
    """Lower triangular Q=(1-E^2)^(2M), degree w=4M in the backward shift."""
    if not isinstance(M, int) or M<0:
        raise ValueError('M must be a nonnegative integer')
    return tuple((2*j, F((-1)**j*comb(2*M, j))) for j in range(2*M+1))


@lru_cache(maxsize=None)
def band_entry(i, j, weights, differential):
    """Entry of Q G Q^T, including all boundary rows and C_0=2."""
    a, c, M = parameters(weights, differential)
    if i<0 or j<0:
        return F(0)
    return sum(x*y*chebyshev_jet_gram_entry(i-p, j-q, a, c)
               for p, x in difference_stencil(M) if p<=i
               for q, y in difference_stencil(M) if q<=j)


@lru_cache(maxsize=None)
def stationary_diagonal(d, weights, differential):
    """Toeplitz tail value at offset i-j=d, calculated without large indices."""
    a, c, M = parameters(weights, differential)
    even, odd = chebyshev_jet_polynomials(a, c)

    def tau(n):
        n = abs(n)
        if not n:
            return 2*a[0]*c[0]
        poly = odd if n%2 else even
        return sum(value*n**(2*h+1) for h, value in enumerate(poly))

    return sum(x*y*tau(d-p+q)
               for p, x in difference_stencil(M)
               for q, y in difference_stencil(M))


@lru_cache(maxsize=None)
def _choices(w, state):
    occupied = set(state)
    choices = []
    for k in range(2*w+1):
        if k in occupied or (0 not in occupied and k!=0):
            continue
        target = tuple(j-1 for j in sorted(occupied | {k}) if j)
        sign = (-1)**sum(j>k for j in occupied)
        choices.append((k, target, sign))
    return tuple(choices)


def _step(vector, w, diagonal):
    result = {}
    for state, value in vector.items():
        for k, target, sign in _choices(w, state):
            coefficient = diagonal[k]
            if coefficient:
                result[target] = result.get(target, F(0))+sign*coefficient*value
    return {state: value for state, value in result.items() if value}


def transfer_metadata(weights, differential, max_states=20000):
    a, c, M = parameters(weights, differential)
    w = 4*M
    count = comb(2*w, w)
    if count>max_states:
        raise ValueError(f'transfer has {count} states; explicit cap is {max_states}')
    return a, c, M, w, count, 2*w+1, tuple(range(w))


def stationary_start(weights, differential, max_states=20000):
    a, c, M, w, count, start, initial = transfer_metadata(
        weights, differential, max_states)
    vector = {initial: F(1)}
    for i in range(start):
        diagonal = [band_entry(i, i-w+k, a, c) for k in range(2*w+1)]
        vector = _step(vector, w, diagonal)
    diagonal = [stationary_diagonal(w-k, a, c) for k in range(2*w+1)]
    return vector, diagonal


def transfer_determinants(weights, differential, max_size, max_states=20000):
    """Exact W_0,...,W_max_size via signed matching states, including all zeros."""
    if not isinstance(max_size, int) or max_size<0:
        raise ValueError('max_size must be a nonnegative integer')
    a, c, M = parameters(weights, differential)
    if not any(a) or not any(c):
        return [F(1)]+[F(0)]*max_size
    if M==0:
        mass = a[0]*c[0]
        return [F(1)]+[mass*(2*mass)**(n-1) for n in range(1, max_size+1)]
    a, c, M, w, count, start, initial = transfer_metadata(a, c, max_states)
    vector = {initial: F(1)}
    result = [F(1)]
    stationary = [stationary_diagonal(w-k, a, c) for k in range(2*w+1)]
    for i in range(max_size):
        diagonal = stationary if i>=start else [
            band_entry(i, i-w+k, a, c) for k in range(2*w+1)]
        vector = _step(vector, w, diagonal)
        result.append(vector.get(initial, F(0))/4)
    return result


def _add_scaled(target, source, coefficient):
    for key, value in source.items():
        updated = target.get(key, F(0))+coefficient*value
        if updated:
            target[key] = updated
        else:
            target.pop(key, None)


def _integer_relation(relation, degree):
    values = [relation.get(j, F(0)) for j in range(degree+1)]
    denominator = lcm(*(value.denominator for value in values))
    values = [int(value*denominator) for value in values]
    common = gcd(*values)
    values = [value//common for value in values]
    if values[-1]<0:
        values = [-value for value in values]
    return tuple(values)


def krylov_certificate(weights, differential, max_order=80, max_states=20000):
    """Prove an eventual recurrence by an exact FULL STATE vector identity.

    It never promotes a fitted scalar prefix to a certificate. The order is
    an annihilator order, not a claim of minimal scalar recurrence order.
    """
    a, c, M, w, count, start, initial = transfer_metadata(
        weights, differential, max_states)
    if not any(a) or not any(c) or M==0:
        raise ValueError('use the explicit zero or constant-input formula')
    vector, diagonal = stationary_start(a, c, max_states)
    echelon = {}
    for j in range(min(max_order, count)+1):
        reduced, relation = dict(vector), {j: F(1)}
        for pivot in sorted(echelon):
            coefficient = reduced.get(pivot, F(0))
            if coefficient:
                basis, representation = echelon[pivot]
                _add_scaled(reduced, basis, -coefficient)
                _add_scaled(relation, representation, -coefficient)
        if not reduced:
            coefficients = _integer_relation(relation, j)
            return {'start': start, 'coefficients': coefficients,
                    'order': j, 'states': count,
                    'vector_identity': 'sum_j coefficients[j] T^j v = 0'}
        pivot = min(reduced)
        scale = reduced[pivot]
        echelon[pivot] = ({key: value/scale for key, value in reduced.items()},
                          {key: value/scale for key, value in relation.items()})
        vector = _step(vector, w, diagonal)
    raise ValueError(f'no full-state relation found by the explicit order cap {max_order}')


def verify_certificate(weights, differential, certificate, max_states=20000):
    """Recompute the full transfer-vector residual from a supplied relation."""
    a, c, M, w, count, start, initial = transfer_metadata(
        weights, differential, max_states)
    try:
        coefficients = tuple(F(value) for value in certificate['coefficients'])
        valid_shape = (coefficients and coefficients[-1]!=0
                       and certificate['order']==len(coefficients)-1
                       and certificate['start']==start
                       and certificate['states']==count)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False
    if not valid_shape:
        return False
    vector, diagonal = stationary_start(a, c, max_states)
    residual = {}
    for coefficient in coefficients:
        _add_scaled(residual, vector, F(coefficient))
        vector = _step(vector, w, diagonal)
    return not residual


def certified_rational_ogf(weights, differential, certificate):
    """Exact numerator/denominator; the supplied full-state relation is checked."""
    if not verify_certificate(weights, differential, certificate):
        raise ValueError('invalid full-state recurrence certificate')
    coefficients = certificate['coefficients']
    order, start = len(coefficients)-1, certificate['start']
    denominator = tuple(F(value, coefficients[-1])
                        for value in reversed(coefficients))
    values = transfer_determinants(weights, differential, start+order-1)
    numerator = [sum(denominator[j]*values[n-j]
                     for j in range(min(n, order)+1))
                 for n in range(start+order)]
    return _trim(numerator), _trim(denominator)
