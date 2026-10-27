#!/usr/bin/env python3
"""SF-DISCOVERY-100: finite arithmetic inverse checks and recovery examples.

The infinite identifiability and instability theorems have local proofs in
new_results/arithmetic_inverse.md.  Rational Prony checks use explicitly FINITE
atomic surrogates, not a claim that the infinite family has finite Hankel rank.
High-precision evaluations are not interval/ball arithmetic certificates.
"""
from fractions import Fraction
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

DEPENDENCIES = Path('/workspace/scratch/de82c13900d1/special_work/verification_dependencies')
if DEPENDENCIES.is_dir():
    sys.path.insert(0, str(DEPENDENCIES))
import mpmath as mp

ROOT = Path(__file__).resolve().parents[1]


def squarefree_flags(nmax):
    flags = bytearray(b'\x01') * (nmax + 1)
    flags[0] = 0
    for d in range(2, math.isqrt(nmax) + 1):
        dd = d * d
        for n in range(dd, nmax + 1, dd):
            flags[n] = 0
    return flags


def support_up_to(q, nmax, flags=None):
    if flags is None:
        flags = squarefree_flags(nmax)
    return [n for n in range(2, nmax + 1) if flags[n] and math.gcd(n, q) == 1]


def prime_divisors(q):
    result = []
    d = 2
    while d * d <= q:
        if q % d == 0:
            result.append(d)
            while q % d == 0:
                q //= d
        d += 1
    if q > 1:
        result.append(q)
    return result


def density(q):
    return mp.fprod(mp.mpf(p)/(p + 1) for p in prime_divisors(q)) / mp.zeta(2)


def zeta_ratio(v, q):
    return mp.zeta(v)/mp.zeta(2*v) * mp.fprod(
        1/(1+mp.power(p, -v)) for p in prime_divisors(q))


def frequency(n, beta):
    return -2 * mp.log1p(-mp.power(n, -beta))


def determinant(matrix):
    a = [list(row) for row in matrix]
    value = Fraction(1)
    for j in range(len(a)):
        pivot_row = next(k for k in range(j, len(a)) if a[k][j])
        if pivot_row != j:
            a[j], a[pivot_row] = a[pivot_row], a[j]
            value = -value
        pivot = a[j][j]
        value *= pivot
        for k in range(j+1, len(a)):
            factor = a[k][j]/pivot
            for ell in range(j+1, len(a)):
                a[k][ell] -= factor*a[j][ell]
    return value


def solve(matrix, vector):
    a = [list(row) + [entry] for row, entry in zip(matrix, vector)]
    d = len(a)
    for j in range(d):
        pivot_row = next(k for k in range(j, d) if a[k][j])
        a[j], a[pivot_row] = a[pivot_row], a[j]
        pivot = a[j][j]
        a[j] = [entry/pivot for entry in a[j]]
        for k in range(d):
            if k != j:
                factor = a[k][j]
                a[k] = [a[k][ell]-factor*a[j][ell] for ell in range(d+1)]
    return [row[-1] for row in a]


def polynomial_from_roots(roots):
    c = [Fraction(1)]
    for x in roots:
        nxt = [Fraction(0)] * (len(c)+1)
        for j, value in enumerate(c):
            nxt[j] -= x*value
            nxt[j+1] += value
        c = nxt
    return c


def integer_root_exact(n, degree):
    lo, hi = 0, n+1
    while hi-lo > 1:
        mid = (lo+hi)//2
        if mid**degree <= n:
            lo = mid
        else:
            hi = mid
    assert lo**degree == n
    return lo


def finite_prony_checks():
    checks = 0
    models = []
    for q in (1, 2, 6, 30):
        ns = support_up_to(q, 100)[:5]
        for beta in (1, 2, 3):
            for d in range(1, 6):
                nodes = [(1-Fraction(1, n**beta))**2 for n in ns[:d]]
                weights = [Fraction(1, n**4) for n in ns[:d]]
                moments = [sum((w*x**k for w, x in zip(weights, nodes)), Fraction())
                           for k in range(2*d+4)]
                hankel = [[moments[i+j] for j in range(d)] for i in range(d)]
                c = solve(hankel, [-moments[i+d] for i in range(d)]) + [Fraction(1)]
                assert c == polynomial_from_roots(nodes)
                checks += 1
                expected_det = math.prod(weights) * math.prod(
                    (nodes[j]-nodes[i])**2 for i in range(d) for j in range(i+1, d))
                assert determinant(hankel) == expected_det > 0
                checks += 1
                recovered_weights = solve([[x**k for x in nodes] for k in range(d)], moments[:d])
                assert recovered_weights == weights
                checks += 1
                recovered_ns = []
                for x in nodes:
                    root_x = Fraction(math.isqrt(x.numerator), math.isqrt(x.denominator))
                    assert root_x**2 == x
                    inverse_power = 1/(1-root_x)
                    assert inverse_power.denominator == 1
                    recovered_ns.append(integer_root_exact(inverse_power.numerator, beta))
                assert recovered_ns == ns[:d]
                checks += 1
                assert [sum((c[j]*moments[k+j] for j in range(d+1)), Fraction())
                        for k in range(d+4)] == [0]*(d+4)
                checks += 1
                models.append({'q':q, 'beta':beta, 'atoms':d,
                               'support':ns[:d], 'positive_hankel_determinant':True})
    for q, qpow in ((2,8), (6,72), (30,900), (210,44100)):
        assert support_up_to(q, 10000) == support_up_to(qpow, 10000)
        checks += 1
    return checks, models


def rank_examples(flags):
    output = []
    for q in (1, 2, 6, 30):
        ns = support_up_to(q, 100000, flags)
        delta = density(q)
        for beta in (mp.mpf(1), mp.mpf(2), mp.mpf('0.75')):
            for j in (100, 1000, 10000):
                nj, n2j = ns[j-1], ns[2*j-1]
                estimate = -mp.log(frequency(n2j,beta)/frequency(nj,beta))/mp.log(2)
                output.append({'q':q, 'beta':str(beta), 'rank_j':j,
                               'n_j':nj, 'n_2j':n2j,
                               'beta_rank_ratio_estimate':mp.nstr(estimate,24),
                               'relative_density_position':mp.nstr(delta*nj/j,24)})
    return output


def peeling_examples(flags):
    output = []
    checks = 0
    nmax, h = 5000, mp.mpf(4)
    for q in (1, 2, 6, 30):
        ns = support_up_to(q, nmax, flags)
        lambdas = [frequency(n,2) for n in ns]
        weights = [mp.mpf(1)/n**4 for n in ns]
        total = zeta_ratio(4,q)-1
        for j in range(3):
            lead_lambda, lead_weight = lambdas[j], weights[j]
            tail_mass = total-mp.fsum(weights[:j+1])
            gap = lambdas[j]-lambdas[j+1]
            for t in (20,100,500):
                values = [mp.fsum(weights[k]*mp.exp(lambdas[k]*depth)
                                 for k in range(j,len(ns))) for depth in (t,t+h)]
                slope = mp.log(values[1]/values[0])/h
                slope_error_bound = mp.log1p(tail_mass/lead_weight*mp.exp(-gap*t))/h
                assert lead_lambda-slope_error_bound-mp.mpf('1e-160') <= slope <= lead_lambda+mp.mpf('1e-160')
                checks += 1
                amplitude = values[0]*mp.exp(-lead_lambda*t)
                amp_error_bound = tail_mass*mp.exp(-gap*t)
                assert lead_weight-mp.mpf('1e-160') <= amplitude <= lead_weight+amp_error_bound+mp.mpf('1e-160')
                checks += 1
                # This true infinite-sum tail envelope is a proved analytic bound;
                # the displayed mpmath arithmetic itself has no directed rounding.
                omitted = [mp.exp(depth*frequency(nmax+1,2))/(3*mp.mpf(nmax)**3)
                           for depth in (t,t+h)]
                slope_interval = [mp.log(values[1]/(values[0]+omitted[0]))/h,
                                  mp.log((values[1]+omitted[1])/values[0])/h]
                a_value = mp.fsum(weights[k]*mp.exp(lambdas[k]*t) for k in range(len(ns)))
                kappa = a_value/values[0]
                n_estimate = (1-mp.exp(-slope/2))**(-mp.mpf('0.5'))
                if j == 0 and t == 500:
                    assert int(mp.nint(n_estimate)) == ns[j]
                    checks += 1
                output.append({'q':q, 'atom_index':j+1, 'n':ns[j], 't':t, 'h':str(h),
                               'lambda':mp.nstr(lead_lambda,24),
                               'lambda_secant_estimate':mp.nstr(slope,24),
                               'secant_error':mp.nstr(lead_lambda-slope,12),
                               'proved_secant_error_envelope':mp.nstr(slope_error_bound,12),
                               'true_secant_truncation_interval': [mp.nstr(x,24) for x in slope_interval],
                               'weight':mp.nstr(lead_weight,24),
                               'normalized_amplitude_estimate':mp.nstr(amplitude,24),
                               'proved_amplitude_error_envelope':mp.nstr(amp_error_bound,12),
                               'support_integer_estimate_known_beta':mp.nstr(n_estimate,24),
                               'log10_subtraction_condition_factor':mp.nstr(mp.log10(kappa),12),
                               'truncated_sum_nmax':nmax,
                               'residual_convention':'Previous atoms removed exactly; residual evaluated as a positive sum.'})
    return checks, output


def compact_instability_examples():
    output = []
    checks = 0
    radius = mp.mpf(5)
    for p in (101,1009,10007):
        mass = zeta_ratio(4,1)/(mp.mpf(p)**4+1)
        bound = mp.exp(radius*frequency(p,2))*mass
        values = []
        for s in (mp.mpf(0), mp.mpf(4), mp.mpc('0.5','0.25')):
            difference = mp.fsum((-1)**k*mp.binomial(2*s,k)*zeta_ratio(4+2*k,1)/
                                 (mp.mpf(p)**(4+2*k)+1) for k in range(51))
            assert abs(difference) <= bound+mp.mpf('1e-160')
            checks += 1
            if s == 0:
                assert abs(difference-mass) < mp.mpf('1e-160')
                checks += 1
            values.append({'s':[str(mp.re(s)),str(mp.im(s))],
                           'difference_value':[mp.nstr(mp.re(difference),24),mp.nstr(mp.im(difference),24)]})
        output.append({'q':1,'newly_excluded_prime':p,'a':2,'beta':2,
                       'radius':str(radius),'exact_mass_formula':'Z_1(4)/(p^4+1)',
                       'removed_mass':mp.nstr(mass,24),
                       'proved_compact_difference_envelope':mp.nstr(bound,24),
                       'derivative_envelopes_k_0_to_4':[mp.nstr(bound*frequency(p,2)**k,24) for k in range(5)],
                       'examples':values})
    return checks, output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path,
                        default=ROOT/'evidence'/'arithmetic_inverse_checks.json')
    args = parser.parse_args()
    started = time.monotonic()
    mp.mp.dps = 180
    exact_checks, models = finite_prony_checks()
    flags = squarefree_flags(100000)
    ranks = rank_examples(flags)
    numerical_checks, peeling = peeling_examples(flags)
    more_checks, compact = compact_instability_examples()
    proof = ROOT/'new_results'/'arithmetic_inverse.md'
    result = {'status':'PASS','checkpoint':'SF-DISCOVERY-100',
              'exact_checks':exact_checks,'high_precision_checks':numerical_checks+more_checks,
              'contract':{'claim':'Exact infinite-family identifiability modulo radical and finite gap-based peeling bounds.',
                          'exact_surrogate':'Finite atomic moment/Prony reconstruction with rational nodes and weights.',
                          'exact_parameters':{'twice_a':4,'beta':[1,2,3],'q':[1,2,6,30],
                                              'atom_counts':[1,2,3,4,5]},
                          'numeric_parameters':{'twice_a':4,'beta_peeling':2,'q':[1,2,6,30],
                                                'atom_indices':[1,2,3],'negative_depth_t':[20,100,500],
                                                'secant_h':4,'direct_sum_nmax':5000,
                                                'rank_count_nmax':100000,'rank_beta':[1,2,0.75],
                                                'ranks':[100,1000,10000],'instability_primes':[101,1009,10007]},
                          'arithmetic':'fractions.Fraction exact and mpmath 180 decimal digits',
                          'pass_meaning':'Exact surrogate identities verified; numerical examples within analytic envelopes.',
                          'failure_meaning':'A violated finite assertion requires implementation or bound review; it is not automatically a counterexample to the infinite theorem.',
                          'resource_bounds':'Finite support enumeration up to 100000; no adaptive or unbounded search.'},
              'finite_prony_models':models,'rank_recovery_examples':ranks,
              'negative_depth_peeling_examples':peeling,'compact_instability_examples':compact,
              'software':{'python':sys.version.split()[0],'mpmath':mp.__version__,'platform':platform.platform()},
              'runtime_seconds':round(time.monotonic()-started,6),
              'command':'python checks/arithmetic_inverse.py',
              'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'proof_sha256':hashlib.sha256(proof.read_bytes()).hexdigest() if proof.exists() else None,
              'run_history':[{'event':'Primary de Gruyter chapter webpage retrieval failed with Internal Error; the publisher-distributed 2010 book preview authenticated Proposition 1.2 and Theorem 1.4 instead.',
                              'category':'source-retrieval failure','mathematical_impact':'None: inverse proof is local and the preview verifies the classical comparison.'}],
              'non_claims':['Finite Prony checks concern finite surrogate measures only.',
                            'Rank examples do not prove the asymptotic limit.',
                            'High precision is not interval/ball arithmetic.',
                            'Exact identifiability is not uniform finite-data stability.',
                            'No global historical novelty claim.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
