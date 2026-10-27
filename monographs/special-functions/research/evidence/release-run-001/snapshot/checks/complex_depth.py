#!/usr/bin/env python3
"""Exact finite checks and bounded high-precision examples for SF-DISCOVERY-001.

Finite checks do not certify entire-function non-D-finiteness or an asymptotic
theorem. Those claims have separate arguments in routes/complex_depth.md.
"""
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys

DEPENDENCIES = Path('/workspace/scratch/de82c13900d1/special_work/verification_dependencies')
if DEPENDENCIES.is_dir():
    sys.path.insert(0, str(DEPENDENCIES))
import mpmath as mp


def squarefree(n):
    return all(n % (d*d) for d in range(2, math.isqrt(n)+1))


def exact_sum(twice_a, beta, q, s, nmax=30):
    return sum((Fraction(1, n**twice_a) *
                (1-Fraction(1, n**beta))**(2*s)
                for n in range(2, nmax+1)
                if math.gcd(n, q) == 1 and squarefree(n)), Fraction())


def determinant(matrix):
    a = [list(row) for row in matrix]
    result = Fraction(1)
    for j in range(len(a)):
        k = next(k for k in range(j, len(a)) if a[k][j])
        if k != j:
            a[j], a[k] = a[k], a[j]
            result = -result
        pivot = a[j][j]
        result *= pivot
        for k in range(j+1, len(a)):
            factor = a[k][j]/pivot
            for ell in range(j+1, len(a)):
                a[k][ell] -= factor*a[j][ell]
    return result


def zeta_ratio(v, q):
    ans = mp.zeta(v)/mp.zeta(2*v)
    for p in range(2, q+1):
        if q % p == 0 and all(p % d for d in range(2, math.isqrt(p)+1)):
            ans /= 1+mp.power(p, -v)
    return ans


def direct_sum(a, beta, q, s, nmax):
    return mp.fsum(mp.power(n, -2*a)*mp.exp(2*s*mp.log1p(-mp.power(n, -beta)))
                   for n in range(2, nmax+1)
                   if math.gcd(n, q) == 1 and squarefree(n))


def newton_sum(a, beta, q, s, kmax):
    return mp.fsum((-1)**k * mp.binomial(2*s, k) *
                   (zeta_ratio(2*a+beta*k, q)-1)
                   for k in range(kmax+1))


def main():
    exact_checks = 0
    for twice_a in (2, 3, 4):
        for beta in (1, 2, 3):
            for q in (1, 2, 6, 30):
                for s in range(-2, 6):
                    left = exact_sum(twice_a, beta, q, s+1)
                    right = (exact_sum(twice_a, beta, q, s)
                             - 2*exact_sum(twice_a+beta, beta, q, s)
                             + exact_sum(twice_a+2*beta, beta, q, s))
                    assert left == right
                    exact_checks += 1
    for s in range(-2, 6):
        assert exact_sum(4, 2, 6, s) == exact_sum(4, 2, 12, s)
        exact_checks += 1
    assert exact_sum(4, 2, 1, 0, nmax=3) == Fraction(1,16)+Fraction(1,81)
    exact_checks += 1
    gram_determinants = []
    for size in range(1, 5):
        gram = [[exact_sum(4, 2, 1, i+j, nmax=15)
                 for j in range(size)] for i in range(size)]
        det = determinant(gram)
        assert det > 0
        exact_checks += 1
        gram_determinants.append({'size': size, 'sign': 1,
                                 'numerator_digits': len(str(det.numerator)),
                                 'denominator_digits': len(str(det.denominator))})
    mp.mp.dps = 80
    examples = []
    nmax, kmax = 2000, 90
    for q, s in ((1, mp.mpc('0.5','0.25')),
                 (2, mp.mpc('-0.5','0.75')),
                 (6, mp.mpc('2','1'))):
        a, beta = mp.mpf(2), mp.mpf(2)
        positive = direct_sum(a, beta, q, s, nmax)
        newton = newton_sum(a, beta, q, s, kmax)
        omitted_tail_bound = mp.power(nmax,1-2*a)/(2*a-1)
        if mp.re(s) < 0:
            omitted_tail_bound *= mp.power(1-mp.power(nmax+1,-beta), 2*mp.re(s))
        discrepancy = abs(positive-newton)
        # Newton truncation and rounding at these specific parameters are far
        # below this direct-tail envelope. No certified ball arithmetic claim.
        assert discrepancy < omitted_tail_bound
        examples.append({'q':q, 's':[str(mp.re(s)), str(mp.im(s))],
                         'newton_value':[mp.nstr(mp.re(newton),22),mp.nstr(mp.im(newton),22)],
                         'direct_newton_discrepancy':mp.nstr(discrepancy,8),
                         'direct_tail_bound':mp.nstr(omitted_tail_bound,8)})
    types = []
    for q in (1,2,6,30):
        m = next(n for n in range(2,50) if math.gcd(n,q)==1 and squarefree(n))
        types.append({'q':q,'least_support_integer':m,
                      'type_beta2':mp.nstr(-2*mp.log1p(-mp.mpf(m)**-2),22)})
    print(json.dumps({'status':'PASS', 'checkpoint':'SF-DISCOVERY-001',
                      'exact_checks':exact_checks,'bounds':{'nmax_exact':30,
                      'twice_a':[2,3,4],'beta':[1,2,3], 'q':[1,2,6,30],
                      'integer_depth':[-2,5], 'gram_sizes':[1,2,3,4],
                      'nmax_complex':nmax,'kmax_newton':kmax,'decimal_precision':mp.mp.dps},
                      'gram_determinants':gram_determinants,'complex_examples':examples,
                      'types':types,'software':{'python':sys.version.split()[0],
                      'mpmath':mp.__version__},'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'non_claims':['Finite checks do not prove non-D-finiteness.',
                                    'High precision examples are not ball-arithmetic certificates.',
                                    'No historical novelty or RH claim.']},indent=2))


if __name__ == '__main__':
    main()
