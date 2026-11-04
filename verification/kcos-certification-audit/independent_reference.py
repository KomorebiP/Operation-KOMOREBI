"""Independent exact-law reference for positive spectra with even multiplicities.

The law is reduced by exact rational partial fractions, not COS inversion.
Decimal arithmetic is outward rounded. exp/log10, documented as correctly
rounded to nearest, are enlarged by one representable neighbor on each side.
This is conditional on CPython Decimal/libmpdec, not a formal implementation proof.
"""
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING, MAX_EMAX, MIN_EMIN
from fractions import Fraction
from math import comb, factorial
from typing import Sequence

@dataclass(frozen=True)
class Box:
    lo: Decimal
    hi: Decimal
    digits: int = 180

    def __post_init__(self):
        if self.lo.is_nan() or self.hi.is_nan() or self.lo > self.hi:
            raise ValueError('Invalid interval')

    @classmethod
    def rational(cls, value: Fraction | int | str, digits: int = 180):
        v = Fraction(value)
        with localcontext() as c:
            c.prec = digits
            c.Emax, c.Emin = MAX_EMAX, MIN_EMIN
            c.rounding = ROUND_FLOOR
            lo = Decimal(v.numerator) / Decimal(v.denominator)
            c.rounding = ROUND_CEILING
            hi = Decimal(v.numerator) / Decimal(v.denominator)
        return cls(lo, hi, digits)

    def __add__(self, other):
        if not isinstance(other, Box):
            other = Box.rational(other, self.digits)
        if other.digits != self.digits:
            raise ValueError('Mixed interval precision')
        with localcontext() as c:
            c.prec = self.digits
            c.Emax, c.Emin = MAX_EMAX, MIN_EMIN
            c.rounding = ROUND_FLOOR
            lo = self.lo + other.lo
            c.rounding = ROUND_CEILING
            hi = self.hi + other.hi
        return Box(lo, hi, self.digits)

    def __mul__(self, other):
        if not isinstance(other, Box):
            other = Box.rational(other, self.digits)
        if other.digits != self.digits:
            raise ValueError('Mixed interval precision')
        with localcontext() as c:
            c.prec = self.digits
            c.Emax, c.Emin = MAX_EMAX, MIN_EMIN
            c.rounding = ROUND_FLOOR
            lo = min(a*b for a in (self.lo, self.hi) for b in (other.lo, other.hi))
            c.rounding = ROUND_CEILING
            hi = max(a*b for a in (self.lo, self.hi) for b in (other.lo, other.hi))
        return Box(lo, hi, self.digits)

    def exp(self):
        with localcontext() as c:
            c.prec = self.digits
            c.Emax, c.Emin = MAX_EMAX, MIN_EMIN
            lo = c.next_minus(c.exp(self.lo))
            hi = c.next_plus(c.exp(self.hi))
        return Box(lo, hi, self.digits)

    def log10(self):
        if self.lo <= 0:
            raise ArithmeticError('Reference precision does not prove positivity')
        with localcontext() as c:
            c.prec = self.digits
            c.Emax, c.Emin = MAX_EMAX, MIN_EMIN
            lo = c.next_minus(c.log10(self.lo))
            hi = c.next_plus(c.log10(self.hi))
        return Box(lo, hi, self.digits)

    def strings(self):
        return [str(self.lo), str(self.hi)]


def density_partial_fractions(eigenvalues: Sequence[str]):
    """Return (rate, pole order, exact rational coefficient) of Laplace density."""
    counts = Counter(Fraction(x) for x in eigenvalues)
    if not counts or any(x <= 0 or n % 2 for x, n in counts.items()):
        raise ValueError('Reference requires positive eigenvalues of even multiplicity')
    rates = {Fraction(1, 2)/lam: n//2 for lam, n in counts.items()}
    result = []
    for rate, multiplicity in rates.items():
        coeff = [rate**multiplicity] + [Fraction(0)]*(multiplicity-1)
        for other_rate, other_multiplicity in rates.items():
            if other_rate == rate:
                continue
            delta = other_rate-rate
            terms = [(other_rate/delta)**other_multiplicity * (-1)**j *
                     comb(other_multiplicity+j-1, j) / delta**j
                     for j in range(multiplicity)]
            coeff = [sum((coeff[j]*terms[k-j] for j in range(k+1)), Fraction(0))
                     for k in range(multiplicity)]
        result.extend((rate, k, coeff[multiplicity-k]) for k in range(1, multiplicity+1))
    assert sum((c/r**k for r,k,c in result), Fraction(0)) == 1
    for s in (Fraction(1, 3), Fraction(1), Fraction(7, 2)):
        expected = Fraction(1)
        for r,m in rates.items():
            expected *= (r/(s+r))**m
        assert sum((c/(s+r)**k for r,k,c in result), Fraction(0)) == expected
    return result


def exact_law_tail(q_decimal: str, eigenvalues: Sequence[str], digits: int = 180):
    """Enclose the finite exponential-polynomial survival formula independently."""
    q = Fraction(q_decimal)
    poles = density_partial_fractions(eigenvalues)
    if q <= 0:
        return {'probability': ['1', '1'], 'log10': ['0', '0'], 'decimal_digits': digits}
    weights = {}
    for rate, order, coefficient in poles:
        x = rate*q
        polynomial = sum((x**j/factorial(j) for j in range(order)), Fraction(0))
        weights[rate] = weights.get(rate, Fraction(0)) + coefficient/rate**order*polynomial
    tail = Box.rational(0, digits)
    for rate, coefficient in weights.items():
        tail = tail + Box.rational(coefficient, digits)*Box.rational(-rate*q, digits).exp()
    if tail.hi <= 0 or tail.lo > 1:
        raise ArithmeticError('Invalid reference probability')
    tail = Box(max(Decimal(0), tail.lo), min(Decimal(1), tail.hi), digits)
    logarithm = tail.log10()
    return {'probability': tail.strings(), 'log10': logarithm.strings(),
            'decimal_digits': digits, 'distinct_rates': len(weights),
            'reference': 'exact rational partial fractions + outward Decimal exp/log10'}


def imhof_quad(q_decimal: str, eigenvalues: Sequence[str], absolute_accuracy: float = 1e-10):
    """Independent binary64 Imhof/Gil-Pelaez quadrature; NOT a directed enclosure."""
    import math
    import warnings
    import numpy as np
    from scipy.integrate import quad, IntegrationWarning
    lam = np.asarray([float(x) for x in eigenvalues], dtype=float)
    scale = float(np.max(lam))
    lam = lam/scale
    q = float(Fraction(q_decimal)/Fraction(str(scale)))
    def f(t):
        if t == 0:
            return float(lam.sum())-q
        z = 2*lam*t
        phase = .5*float(np.arctan(z).sum())-q*t
        logmag = -.25*float(np.log1p(z*z).sum())
        return math.sin(phase)*math.exp(logmag)/t
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always', IntegrationWarning)
        integral, error = quad(f, 0, np.inf, epsabs=math.pi*absolute_accuracy,
                               epsrel=1e-11, limit=1500)
    return {'probability': .5+integral/math.pi, 'estimated_absolute_error': error/math.pi,
            'requested_absolute_accuracy': absolute_accuracy,
            'warnings': [str(w.message) for w in caught],
            'semantics': 'QUADPACK error estimate, not a rigorous interval'}


def imhof_weighted(q_decimal: str, eigenvalues: Sequence[str], absolute_accuracy: float = 1e-10):
    """Imhof formula with oscillatory QUADPACK weights and an analytic subtraction.

    Split Im(exp(-iqt) phi(t))/t into cosine and sine integrals. Subtract
    exp(-t)/t from the sine amplitude to remove the removable singularity,
    and restore its known integral atan(q). Error estimates remain non-rigorous.
    This is an audit implementation of the formula, not CompQuadForm's R imhof.
    """
    import math, warnings
    import numpy as np
    from scipy.integrate import quad, IntegrationWarning
    scale = max(Fraction(x) for x in eigenvalues)
    lam = np.asarray([float(Fraction(x)/scale) for x in eigenvalues])
    q = float(Fraction(q_decimal)/scale)
    if q <= 0:
        raise ValueError('This comparison requires a positive threshold')
    def components(t):
        z=2*lam*t
        logmag=-.25*float(np.log1p(z*z).sum())
        phase=.5*float(np.arctan(z).sum())
        return logmag,phase
    def cosine_amplitude(t):
        if t==0:return float(lam.sum())
        lm,ph=components(t)
        return math.exp(lm)*math.sin(ph)/t
    def sine_amplitude(t):
        if t==0:return 1.0
        lm,ph=components(t)
        return (math.expm1(lm)-2*math.exp(lm)*math.sin(ph/2)**2-math.expm1(-t))/t
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always',IntegrationWarning)
        cosine,ec=quad(cosine_amplitude,0,np.inf,weight='cos',wvar=q,
                       epsabs=math.pi*absolute_accuracy/4,limlst=500,limit=500)
        sine,es=quad(sine_amplitude,0,np.inf,weight='sin',wvar=q,
                     epsabs=math.pi*absolute_accuracy/4,limlst=500,limit=500)
    return {'probability':.5+(cosine-sine-math.atan(q))/math.pi,
            'estimated_absolute_error':(ec+es)/math.pi,
            'requested_absolute_accuracy':absolute_accuracy,
            'warnings':[str(w.message) for w in caught],
            'semantics':'Independent Imhof formula, oscillatory QUADPACK error estimates, not a directed enclosure'}

if __name__ == '__main__':
    print(exact_law_tail('40', ['1','1','2','2']))
