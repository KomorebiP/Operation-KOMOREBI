#!/usr/bin/env python3
"""Finite numerical checks for arithmetic prime-sieve packet polynomials.

No finite check is a proof of positivity, a global asymptotic, or novelty.
The route note supplies the exact proofs.  Run with mpmath installed, e.g.
PYTHONPATH=/workspace/scratch/de82c13900d1/special_work/verification_dependencies python checks/arithmetic_polynomials.py
"""
from pathlib import Path
import json
import mpmath as mp

mp.mp.dps = 160
OUT = Path(__file__).resolve().parents[1] / "evidence" / "arithmetic_polynomial_checks.json"


def moments(count, prime=2, strength=0, depth=0):
    strength = mp.mpf(str(strength))
    return [sum((-1)**j * mp.binomial(2*(i+depth), j)
                * mp.zeta(4+2*j)/mp.zeta(8+4*j)
                * (1+strength/(mp.mpf(prime)**(4+2*j)+1))
                for j in range(2*(i+depth)+1)) for i in range(count)]


def inner(a, b, mu, shift=0):
    return sum(ai*bj*mu[i+j+shift] for i, ai in enumerate(a)
               for j, bj in enumerate(b))


def polynomial(n, mu):
    if not n:
        return [mp.mpf(1)]
    H = mp.matrix([[mu[i+j] for j in range(n)] for i in range(n)])
    c = mp.lu_solve(H, mp.matrix([-mu[n+i] for i in range(n)]))
    return list(c) + [mp.mpf(1)]


def kernel(n, mu, x=0):
    value = mp.mpf(0)
    for i in range(n+1):
        pi = polynomial(i, mu)
        value += mp.polyval(list(reversed(pi)), x)**2/inner(pi, pi, mu)
    return value


def s(x):
    return mp.nstr(x, 102)


checks = []
samples = []
maximum_orthogonality_error = mp.mpf(0)
for p in [2, 3, 5]:
    for lam in [-1, -.5, 0, 1, 10]:
        for k in [0, 1, 3, 10]:
            mu = moments(15, p, lam, k)
            ps = [polynomial(n, mu) for n in range(7)]
            hs = [inner(q, q, mu) for q in ps]
            assert all(h > 0 for h in hs)
            for n in range(1, 7):
                for j in range(n):
                    err = abs(inner(ps[n], [mp.mpf(0)]*j+[mp.mpf(1)], mu))
                    maximum_orthogonality_error = max(maximum_orthogonality_error, err)
                    assert err < mp.mpf('1e-115')
                a = inner(ps[n], ps[n], mu, 1)/hs[n]
                assert 0 < a < 1
                assert hs[n]/hs[n-1] > 0
            checks.append({"prime": p, "strength": lam, "depth": k,
                           "degrees": [0, 6], "positive_norms": True})
            if p == 2 and k == 0 and lam in [-1, 0, 1]:
                samples.append({"prime": p, "strength": lam,
                                "moments_0_to_4": list(map(s, mu[:5])),
                                "p1_coefficients_ascending": list(map(s, ps[1])),
                                "p2_coefficients_ascending": list(map(s, ps[2])),
                                "a0": s(inner(ps[0], ps[0], mu, 1)/hs[0]),
                                "a1": s(inner(ps[1], ps[1], mu, 1)/hs[1]),
                                "b1_monic": s(hs[1]/hs[0])})

# Hankel singular strengths from a symmetric definite matrix pencil.
exceptional_strengths = []
sieve_margin_bounds = []
for p in [2, 3, 5]:
    full = moments(9, p, 0)
    without = moments(9, p, -1)
    for n in range(1, 5):
        A = mp.matrix([[without[i+j] for j in range(n)] for i in range(n)])
        B = mp.matrix([[full[i+j]-without[i+j] for j in range(n)] for i in range(n)])
        L = mp.cholesky(A)
        Linv = L**-1
        C = Linv*B*Linv.T
        eigenvalues, _ = mp.eigsy(C)
        roots = [-1-1/e for e in eigenvalues]
        assert all(r < -1 for r in roots)
        for r in roots:
            # Relative determinant residual: large negative roots can make
            # entries huge, so an absolute determinant criterion is invalid.
            matrix = A+(1+r)*B
            scale = max(mp.mpf(1), max(abs(v) for v in matrix))
            err = abs(mp.det(matrix))/scale**n
            assert err < mp.mpf('1e-120')
        exceptional_strengths.append({"prime": p, "hankel_order": n,
                                       "lambda_roots": list(map(s, roots))})
        if p == 2 and n >= 2:
            delta = -1-max(roots)
            upper = mp.mpf(4096)/81*(mp.mpf(16)/17*full[0]-1)*(mp.mpf(272)/567)**(2*(n-2))
            assert 0 < delta <= upper
            sieve_margin_bounds.append({"hankel_order": n, "delta": s(delta),
                                        "proven_upper_bound": s(upper)})

# Exact Christoffel and shifted determinant identities, evaluated numerically.
depth_transport_cases = 0
tau_identity_cases = 0
for lam in [-1, 0, 1]:
    for k in range(4):
        mu = moments(15, 2, lam, k)
        for n in range(1, 6):
            p, pnext = polynomial(n, mu), polynomial(n+1, mu)
            factor = pnext[0]/p[0]
            numerator = pnext.copy()
            for i, coefficient in enumerate(p):
                numerator[i] -= factor*coefficient
            actual = polynomial(n, mu[1:])
            assert max(abs(a-b) for a, b in zip(numerator[1:], actual)) < mp.mpf('1e-110')
            depth_transport_cases += 1
        def tau(n, shift):
            return mp.mpf(1) if n == 0 else mp.det(mp.matrix([[mu[i+j+shift] for j in range(n)] for i in range(n)]))
        for n in range(1, 5):
            lhs = tau(n, 0)*tau(n, 2)-tau(n, 1)**2
            rhs = tau(n+1, 0)*tau(n-1, 2)
            assert lhs > 0 and rhs > 0
            assert abs(lhs-rhs) < mp.mpf('1e-140')
            tau_identity_cases += 1

# Uvarov formula, including exact removal of the existing zero atom.
mu = moments(15)
uvarov_cases = 0
for theta in [-1, -.5, 1, 10]:
    modified = mu.copy()
    modified[0] += theta
    for n in range(1, 7):
        p = polynomial(n, mu)
        K = [mp.mpf(0)]*n
        for j in range(n):
            q = polynomial(j, mu)
            factor = q[0]/inner(q, q, mu)
            for i in range(j+1):
                K[i] += factor*q[i]
        factor = mp.mpf(theta)*p[0]/(1+theta*K[0])
        formula = p.copy()
        for i in range(n):
            formula[i] -= factor*K[i]
        actual = polynomial(n, modified)
        assert max(abs(a-b) for a, b in zip(formula, actual)) < mp.mpf('1e-115')
        uvarov_cases += 1

mass_recovery = []
for n in range(7):
    K = kernel(n, mu)
    upper = 1+(mu[0]-1)*mp.mpf(7)**(2*n)/mp.mpf(16)**(2*n)
    assert 1 <= 1/K <= upper + mp.mpf('1e-140')
    mass_recovery.append({"degree": n, "inverse_kernel": s(1/K),
                          "proven_upper_bound": s(upper)})

# Differential measure-flow identity for the prime-sieve strength.
p, lam, n = 2, mp.mpf('.25'), 3
step = mp.mpf('1e-45')
mu = moments(11, p, lam)
pm = polynomial(n, mu)
prime_mu = [a-b for a, b in zip(moments(11, p, 1), moments(11, p, 0))]
formula = [mp.mpf(0)]*n
for j in range(n):
    q = polynomial(j, mu)
    factor = -inner(pm, q, prime_mu)/inner(q, q, mu)
    for i in range(j+1):
        formula[i] += factor*q[i]
plus, minus = polynomial(n, moments(11, p, lam+step)), polynomial(n, moments(11, p, lam-step))
derivative_error = max(abs((plus[i]-minus[i])/(2*step)-formula[i]) for i in range(n))
assert derivative_error < mp.mpf('1e-80')

report = {"precision_decimal_digits": mp.mp.dps,
          "scope": "Finite checks only. Exact proofs and novelty boundaries are in routes/arithmetic_polynomials.md.",
          "parameter_cases": len(checks), "checked_degrees": [0, 6],
          "orthogonality_tests": len(checks)*21,
          "maximum_absolute_orthogonality_error": s(maximum_orthogonality_error),
          "uvarov_formula_cases": uvarov_cases,
          "prime_flow_derivative_error": s(derivative_error),
          "parameter_grid": checks,
          "sample_polynomials": samples,
          "hankel_exceptional_strengths": exceptional_strengths,
          "sieve_margin_bounds": sieve_margin_bounds,
          "depth_transport_cases": depth_transport_cases,
          "tau_identity_cases": tau_identity_cases,
          "mass_recovery": mass_recovery,
          "run_history": [
              {"run": 1, "status": "failed",
               "failed_check": "abs(det(A+(1+lambda)*B)) < 1e-120",
               "observed_error": "AssertionError at the absolute determinant residual assertion, after the parameter grid passed.",
               "interpretation": "Scale-dependent test criterion: very large negative lambda roots produce large matrix entries. No exact theorem was refuted."},
              {"run": 2, "status": "passed",
               "correction": "Use abs(det(matrix))/max(1,max(abs(matrix entries)))**order < 1e-120.",
               "limitation": "Numerical residual only; no interval root certification."}
          ],
          "status": "passed"}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps({k: report[k] for k in ["status", "parameter_cases", "orthogonality_tests", "uvarov_formula_cases", "maximum_absolute_orthogonality_error"]}, indent=2))
