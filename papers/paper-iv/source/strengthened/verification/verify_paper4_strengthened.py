#!/usr/bin/env python3
from __future__ import annotations

import cmath
import math
import re
import subprocess
from pathlib import Path

import mpmath as mp
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / 'PSC_Paper_IV_Strengthened_Annals_Edition.tex'
BIB = ROOT / 'PSC_Paper_IV_Strengthened_Annals_Edition.bib'
PDF = ROOT / 'PSC_Paper_IV_Strengthened_Annals_Edition.pdf'
LOG = Path(__file__).resolve().parent / 'PSC_Paper_IV_Strengthened_Annals_Edition.log'
RESULT = Path(__file__).resolve().parent / 'STRENGTHENED_RERUN_RESULTS.txt'

mp.mp.dps = 100
results: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = '') -> None:
    results.append((name, bool(condition), detail))
    if not condition:
        raise AssertionError(f'{name}: {detail}')


def reciprocal_polys(N: int, nmax: int) -> list[sp.Expr]:
    w, r = sp.symbols('w r')
    delta = sum(sp.Rational((-1) ** n, math.factorial(N * n)) * w**n for n in range(nmax + 1))
    series = sp.series(sp.exp(-r * sp.log(delta)), w, 0, nmax + 1).removeO().expand()
    return [sp.expand(series.coeff(w, n) * math.factorial(N * n)) for n in range(nmax + 1)]


def kappa_recurrence(N: int, nmax: int) -> list[sp.Rational]:
    a = [sp.Rational((-1) ** n, math.factorial(N * n)) for n in range(nmax + 1)]
    kap = [sp.Rational(0)] * (nmax + 1)
    for m in range(1, nmax + 1):
        kap[m] = -m * a[m] - sum(a[k] * kap[m - k] for k in range(1, m))
    return kap


def D(N: int, z: mp.mpf | mp.mpc) -> mp.mpc:
    return sum(mp.e ** (mp.e ** (mp.j * (2 * k + 1) * mp.pi / N) * z) for k in range(N)) / N


def Dprime(N: int, z: mp.mpf | mp.mpc) -> mp.mpc:
    return sum(
        mp.e ** (mp.j * (2 * k + 1) * mp.pi / N)
        * mp.e ** (mp.e ** (mp.j * (2 * k + 1) * mp.pi / N) * z)
        for k in range(N)
    ) / N


def remainder_R(N: int, z: mp.mpf | mp.mpc) -> mp.mpc:
    a = mp.pi / N
    dom1 = mp.e ** (mp.j * a)
    dom2 = mp.e ** (-mp.j * a)
    total = mp.mpc(0)
    for k in range(N):
        eta = mp.e ** (mp.j * (2 * k + 1) * mp.pi / N)
        if abs(eta - dom1) < mp.mpf('1e-70') or abs(eta - dom2) < mp.mpf('1e-70'):
            continue
        total += mp.e ** ((eta - dom2) * z)
    return total


# A. Root filter and product law
for N in range(2, 8):
    omega = cmath.exp(2j * math.pi / N)
    z0 = 0.17 + 0.09j
    coeff = [((-1) ** m) * (m + 1) / (m + 2) for m in range(20)]
    packets = []
    for j in range(N):
        avg = sum(
            omega ** (-j * ell)
            * sum(coeff[m] * (omega**ell * z0) ** m for m in range(len(coeff)))
            for ell in range(N)
        ) / N
        direct = sum(coeff[m] * z0**m for m in range(len(coeff)) if m % N == j)
        check(f'root filter N={N} j={j}', abs(avg - direct) < 5e-12)
        packets.append(direct)
    full = sum(coeff[m] * z0**m for m in range(len(coeff)))
    check(f'root reconstruction N={N}', abs(sum(packets) - full) < 5e-12)
check('cyclic projection group', True, 'root filters and reconstruction checked')

# B. Finite algebra and signed companion matrix
for N in range(1, 9):
    J = sp.zeros(N)
    for j in range(N - 1):
        J[j + 1, j] = 1
    J[0, N - 1] = -1
    check(f'signed shift power N={N}', J**N == -sp.eye(N))
    x = sp.symbols('x')
    trunc = sp.zeros(N)
    for m in range(0, 5 * N):
        trunc += x**m / sp.factorial(m) * (J**m)
    first = trunc[:, 0]
    for j in range(N):
        target = sum((-1) ** n * x ** (N * n + j) / sp.factorial(N * n + j) for n in range(5) if N*n+j < 5*N)
        check(f'companion first column N={N} j={j}', sp.expand(first[j] - target) == 0)
    for pidx in range(N):
        for qidx in range(N):
            d = (pidx - qidx) % N
            eps = 1 if pidx >= qidx else -1
            target = eps * sum(
                (-1) ** n * x ** (N * n + d) / sp.factorial(N * n + d)
                for n in range(6) if N*n+d < 5*N
            )
            check(
                f'companion full entry N={N} p={pidx} q={qidx}',
                sp.expand(trunc[pidx, qidx] - target) == 0,
            )
    char = sp.factor(J.charpoly().as_expr())
    check(f'companion characteristic N={N}', sp.expand(char - (sp.Symbol('lambda')**N + 1)) == 0, str(char))
check('finite algebra and matrix model', True, 'signed shift identities checked symbolically')

# C. Differential cycles, Wronskians, and addition laws
z, lam, w = sp.symbols('z lam w')
for N in range(2, 7):
    M = 6
    E = [sum((lam * z) ** (N * n + j) / sp.factorial(N * n + j) for n in range(M)) for j in range(N)]
    Ds = [sum((-1) ** n * z ** (N * n + j) / sp.factorial(N * n + j) for n in range(M)) for j in range(N)]
    for j in range(1, N):
        check(f'transfer derivative N={N} j={j}', sp.series(sp.diff(E[j], z) - lam * E[j-1], z, 0, N*(M-1)).removeO() == 0)
        check(f'signed derivative N={N} j={j}', sp.series(sp.diff(Ds[j], z) - Ds[j-1], z, 0, N*(M-1)).removeO() == 0)
    check(f'transfer wrap N={N}', sp.series(sp.diff(E[0], z) - lam * E[N-1], z, 0, N*(M-1)).removeO() == 0)
    check(f'signed wrap N={N}', sp.series(sp.diff(Ds[0], z) + Ds[N-1], z, 0, N*(M-1)).removeO() == 0)
check('differential systems', True, 'transfer and signed cycles checked')

# D. Reciprocal Bell, denominator recurrence, logarithmic recurrence, determinant, and explicit first values
r, s = sp.symbols('r s')
for N in range(1, 7):
    nmax = 6
    P = reciprocal_polys(N, nmax)
    kap = kappa_recurrence(N, nmax)
    for n in range(1, nmax + 1):
        # Bell formula
        u = sp.symbols('u')
        exponent = sum(r * kap[m] * u**m / m for m in range(1, n + 1))
        bell = sp.expand(sp.series(sp.exp(exponent), u, 0, n + 1).removeO().coeff(u, n) * sp.factorial(N*n))
        check(f'Bell formula N={N} n={n}', sp.simplify(P[n] - bell) == 0)
        # Original recurrence
        rec = -sum((-1)**k * sp.binomial(N*n-1, N*k) * P[n-k] for k in range(1, n))
        rec -= r * sum((-1)**k * sp.binomial(N*n-1, N*k-1) * P[n-k] for k in range(1, n+1))
        check(f'parameter recurrence N={N} n={n}', sp.simplify(P[n] - rec) == 0)
        # Logarithmic recurrence
        logrec = r * sum(sp.factorial(N*n) * kap[k] * P[n-k] / sp.factorial(N*(n-k)) for k in range(1, n+1)) / n
        check(f'logarithmic recurrence N={N} n={n}', sp.simplify(P[n] - logrec) == 0)
        # Hessenberg determinant
        p = [None] + [r * kap[k] for k in range(1, n+1)]
        Mx = sp.zeros(n)
        for i in range(n):
            for j in range(n):
                if j <= i:
                    Mx[i, j] = p[i-j+1]
                elif j == i + 1:
                    Mx[i, j] = -(i+1)
        detb = sp.expand(Mx.det() / sp.factorial(n) * sp.factorial(N*n))
        check(f'Hessenberg determinant N={N} n={n}', sp.simplify(P[n] - detb) == 0)
        # Semigroup
        conv = sum(sp.binomial(N*n, N*q) * P[q] * P[n-q].subs(r, s) for q in range(n+1))
        check(f'reciprocal semigroup N={N} n={n}', sp.simplify(P[n].subs(r, r+s) - conv) == 0)
    p2 = r * (sp.binomial(2*N, N) * (r+1) / 2 - 1)
    p3 = r * (sp.factorial(3*N) * (r+1)*(r+2)/(6*sp.factorial(N)**3) - sp.binomial(3*N, N)*(r+1) + 1)
    check(f'explicit P1 N={N}', sp.simplify(P[1] - r) == 0)
    check(f'explicit P2 N={N}', sp.simplify(P[2] - p2) == 0)
    check(f'explicit P3 N={N}', sp.simplify(P[3] - p3) == 0)
check('reciprocal coefficient system', True, 'all reciprocal formulas agree')

# E. Tangent recurrence and Riccati low orders
for N in range(1, 8):
    kap = kappa_recurrence(N, 8)
    T = [N * sp.factorial(N*n+N-1) * kap[n+1] for n in range(7)]
    check(f'tangent initial N={N}', T[0] == 1)
    for n in range(1, 7):
        rhs = (-1)**n - sum((-1)**k * sp.binomial(N*n+N-1, N*k) * T[n-k] for k in range(1, n+1))
        check(f'tangent recurrence N={N} n={n}', sp.simplify(T[n] - rhs) == 0)
check('tangent system', True, 'tangent coefficients checked')

# F. Congruential reciprocal and Appell laws
x, y = sp.symbols('x y')
for N in range(2, 6):
    for j in range(N):
        nmax = 5
        phi = sum(sp.factorial(j) * w**n / sp.factorial(N*n+j) for n in range(nmax+1))
        Cseries = sp.series(sp.exp(-r * sp.log(phi)), w, 0, nmax+1).removeO().expand()
        Cp = [sp.expand(Cseries.coeff(w, n) * sp.factorial(N*n)) for n in range(nmax+1)]
        # triangular inverse at r=1
        C1 = [sp.expand(v.subs(r, 1)) for v in Cp]
        for n in range(nmax+1):
            lhs = sum(sp.binomial(N*n+j, N*q) * C1[q] for q in range(n+1))
            check(f'congruential inverse N={N} j={j} n={n}', sp.simplify(lhs - (1 if n == 0 else 0)) == 0)
        # Appell polynomials
        mmax = 7
        Er = []
        Es = []
        Ers = []
        for m in range(mmax+1):
            Er.append(sp.expand(sum(sp.binomial(m, N*n) * Cp[n] * x**(m-N*n) for n in range(0, min(nmax, m//N)+1))))
            Es.append(sp.expand(sum(sp.binomial(m, N*n) * Cp[n].subs(r, s) * y**(m-N*n) for n in range(0, min(nmax, m//N)+1))))
            Ers.append(sp.expand(sum(sp.binomial(m, N*n) * Cp[n].subs(r, r+s) * (x+y)**(m-N*n) for n in range(0, min(nmax, m//N)+1))))
        for m in range(mmax+1):
            conv = sum(sp.binomial(m, q) * Er[q] * Es[m-q] for q in range(m+1))
            check(f'Appell two parameter N={N} j={j} m={m}', sp.simplify(Ers[m] - conv) == 0)
            if m > 0:
                check(f'Appell derivative N={N} j={j} m={m}', sp.simplify(sp.diff(Er[m], x) - m*Er[m-1]) == 0)
check('congruential and Appell system', True, 'inverse, derivative, and two parameter laws checked')

# Classical Euler relation for the normalized secant Appell system
for m in range(0, 10):
    lhs = sp.expand(sum(
        sp.binomial(m, 2*n)
        * (-1)**n * reciprocal_polys(2, m//2)[n].subs(r, 1)
        * x**(m-2*n)
        for n in range(m//2 + 1)
    ))
    rhs = sp.expand(2**m * sp.euler(m, (x+1)/2))
    check(f'Euler scaling m={m}', sp.simplify(lhs-rhs) == 0)
check('classical Euler scaling', True, 'scaled and translated Euler identity checked')

# G. Theta reconstruction and Newton recurrence
u = sp.symbols('u')
for N in range(2, 7):
    nmax = 5
    kap = kappa_recurrence(N, nmax)
    H = sum(w**n / sp.factorial(N*n) for n in range(nmax+1))
    theta_series = sp.series(sp.exp(-sp.log(H.subs(w, u**N*w)) - u*sp.log(H)), w, 0, nmax+1).removeO().expand()
    theta = [sp.expand(theta_series.coeff(w,n)*sp.factorial(N*n)) for n in range(nmax+1)]
    P = reciprocal_polys(N, nmax)
    for n in range(1, nmax+1):
        reconstruct = (-1)**n * sum(sp.binomial(N*n, N*q) * P[q].subs(r,1) * u**(N*q) * P[n-q].subs(r,u) for q in range(n+1))
        check(f'theta reconstruction N={N} n={n}', sp.simplify(theta[n] - reconstruct) == 0)
        lhs = n * theta[n] / sp.factorial(N*n)
        rhs = sum((-1)**m * kap[m] * (u**(N*m)+u) * theta[n-m]/sp.factorial(N*(n-m)) for m in range(1,n+1))
        check(f'theta Newton N={N} n={n}', sp.simplify(lhs-rhs) == 0)
        check(f'theta factor u N={N} n={n}', theta[n].subs(u,0) == 0)
        if N % 2 == 0:
            check(f'theta factor u+1 N={N} n={n}', theta[n].subs(u,-1) == 0)
    check(f'theta first value N={N}', sp.simplify(theta[1] + u**N + u) == 0)
check('theta system', True, 'reconstruction and Newton recurrence checked')

# H. Indicator dominance away from tie directions
for N in range(3, 10):
    a = mp.pi/N
    # choose offsets strictly between tie directions
    for frac in [mp.mpf('0.22'), mp.mpf('0.41')]:
        theta = frac * 2*mp.pi/N
        projections = []
        roots = []
        for k in range(N):
            eta = mp.e ** (mp.j*(2*k+1)*mp.pi/N)
            roots.append(eta)
            projections.append(mp.re(eta * mp.e**(mp.j*theta)))
        idx = max(range(N), key=lambda k: projections[k])
        eta = roots[idx]
        ratios = []
        for rad in [12, 20, 28]:
            zc = rad * mp.e**(mp.j*theta)
            ratio = N*D(N,zc)/mp.e**(eta*zc)
            ratios.append(abs(ratio-1))
        check(f'indicator dominance N={N} frac={frac}', ratios[-1] < ratios[0], str([mp.nstr(v,5) for v in ratios]))
check('indicator polygon', True, 'dominant exponential convergence checked away from ties')

# I. Large zeros, first correction, derivative sign, and rotations
for N in range(3, 11):
    a = mp.pi/N
    sN = mp.sin(a)
    cN = mp.cos(a)
    gamma = cN - mp.cos(3*a)
    A = mp.pi/sN
    for m in [4, 6, 8]:
        t = A*(m+mp.mpf('0.5'))
        tau = mp.findroot(lambda xx: mp.re(D(N,xx)), (t-mp.mpf('0.15'), t+mp.mpf('0.15')))
        corr = remainder_R(N,t)/(2j*sN)
        # correction should be real to high precision
        check(f'correction real N={N} m={m}', abs(mp.im(corr)) < mp.mpf('1e-70'), mp.nstr(corr,8))
        err0 = abs(tau-t)
        err1 = abs(tau-t-mp.re(corr))
        check(f'first correction improves N={N} m={m}', err1 <= err0 + mp.mpf('1e-70'), f'{mp.nstr(err0,6)} to {mp.nstr(err1,6)}')
        # scaled second order error, allowing exact cancellations
        boundscale = mp.e**(-2*gamma*t)
        check(f'first correction scale N={N} m={m}', err1 < max(mp.mpf('1e4')*boundscale, mp.mpf('1e-70')), mp.nstr(err1/boundscale if boundscale else err1,8))
        dval = mp.re(Dprime(N,tau))
        model = ((-1)**(m+1))*2*sN/N*mp.e**(cN*tau)
        check(f'derivative sign N={N} m={m}', dval*model > 0)
        check(f'derivative ratio N={N} m={m}', abs(dval/model-1) < mp.mpf('2e-4'), mp.nstr(dval/model,10))
        omega = mp.e**(2*mp.pi*mp.j/N)
        check(f'rotated zero N={N} m={m}', abs(D(N,omega*tau))/mp.e**(cN*tau) < mp.mpf('1e-70'))
check('large zero and first correction', True, 'N=3 through 10 checked at high precision')

# J. Exact low order models and trace sums
for z0 in [mp.mpf('0.2'), mp.mpf('1.1'), mp.mpc('0.4','0.2')]:
    d3 = (mp.e**(-z0) + 2*mp.e**(z0/2)*mp.cos(mp.sqrt(3)*z0/2))/3
    d4 = mp.cos(z0/mp.sqrt(2))*mp.cosh(z0/mp.sqrt(2))
    check('N=3 closed form', abs(D(3,z0)-d3) < mp.mpf('1e-70'))
    check('N=4 closed form', abs(D(4,z0)-d4) < mp.mpf('1e-70'))
# sigma_1 exact from the zero strings for N=2 and N=4
sigma2 = mp.nsum(lambda m: 1/(mp.pi**2*(m+mp.mpf('0.5'))**2), [0, mp.inf])
sigma4 = mp.nsum(lambda m: 1/(4*mp.pi**4*(m+mp.mpf('0.5'))**4), [0, mp.inf])
check('trace sum N=2', abs(sigma2-mp.mpf(1)/2) < mp.mpf('1e-70'))
check('trace sum N=4', abs(sigma4-mp.mpf(1)/24) < mp.mpf('1e-70'))
check('exact low order and trace models', True, 'N=3 and N=4 formulas checked')

# Exact zero zeta models in orders two and four
for sval in [mp.mpf('0.8'), mp.mpf('1.3'), mp.mpc('1.1','0.4')]:
    Mtail = 40
    if mp.re(sval) > mp.mpf('0.5'):
        z2red_sum = sum((mp.pi**2*(m+mp.mpf('0.5'))**2)**(-sval) for m in range(Mtail))
        z2red_sum += mp.pi**(-2*sval)*mp.zeta(2*sval, Mtail+mp.mpf('0.5'))
        z2red_model = mp.pi**(-2*sval)*mp.zeta(2*sval, mp.mpf('0.5'))
        check(f'exact zeta N=2 red s={sval}', abs(z2red_sum-z2red_model) < mp.mpf('1e-80'))
    if mp.re(sval) > mp.mpf('0.25'):
        A4 = mp.sqrt(2)*mp.pi
        z4red_sum = sum((A4**4*(m+mp.mpf('0.5'))**4)**(-sval) for m in range(Mtail))
        z4red_sum += A4**(-4*sval)*mp.zeta(4*sval, Mtail+mp.mpf('0.5'))
        z4red_model = A4**(-4*sval)*mp.zeta(4*sval, mp.mpf('0.5'))
        check(f'exact zeta N=4 red s={sval}', abs(z4red_sum-z4red_model) < mp.mpf('1e-80'))
check('exact zeta models', True, 'orders two and four checked numerically')

# K. Orbit invariance in coefficient asymptotics
for N in range(2, 9):
    omega = mp.e**(2*mp.pi*mp.j/N)
    tau = mp.mpf('1.234')
    # identities are algebraic in any point, not only zeros, for derivative rotation
    for k in range(N):
        rho = omega**k*tau
        lhs = rho * Dprime(N,rho)
        rhs = tau * Dprime(N,tau)
        check(f'orbit derivative invariant N={N} k={k}', abs(lhs-rhs) < mp.mpf('1e-70'))
        check(f'orbit monomial invariant N={N} k={k}', abs(rho**(-N*4)-tau**(-N*4)) < mp.mpf('1e-70'))
check('orbit reduction identities', True, 'rotational invariants checked')

# L. Source, proof, citation, and PDF integrity
source = TEX.read_text(encoding='utf8')
bib = BIB.read_text(encoding='utf8')
labels = re.findall(r'\\label\{([^}]+)\}', source)
refs = re.findall(r'\\(?:c|C)?ref\{([^}]+)\}', source)
ref_items = [item.strip() for group in refs for item in group.split(',')]
keys = set(re.findall(r'@\w+\{([^,]+),', bib))
cites = set(item.strip() for group in re.findall(r'\\cite\{([^}]+)\}', source) for item in group.split(','))
check('unique labels', len(labels) == len(set(labels)), f'{len(labels)} labels')
check('all internal references', not sorted(set(ref_items)-set(labels)), str(sorted(set(ref_items)-set(labels))))
check('all citations resolve', not sorted(cites-keys), str(sorted(cites-keys)))
check('all bibliography entries cited', not sorted(keys-cites), str(sorted(keys-cites)))
check('no semicolons in source', ';' not in source)
check('no source double hyphens', '--' not in source)
check('no forced page breaks', not re.search(r'\\(?:newpage|pagebreak|clearpage)\b', source))
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', source, re.S).group(1)
abstract_words = len(re.findall(r"\b[\w']+\b", re.sub(r'\\\[.*?\\\]', ' ', abstract, flags=re.S)))
check('abstract under 200 words', abstract_words <= 200, str(abstract_words))
# theorem proof count
result_envs = re.findall(r'\\begin\{(theorem|proposition|lemma|corollary)\}', source)
proofs = re.findall(r'\\begin\{proof\}', source)
check('proof count matches results', len(result_envs) == len(proofs), f'{len(result_envs)} results and {len(proofs)} proofs')
# No unresolved items in log
log = LOG.read_text(encoding='utf8', errors='ignore')
check('no unresolved references in log', 'undefined references' not in log.lower() and 'citation' not in '\n'.join(line for line in log.splitlines() if 'undefined' in line.lower()).lower())
check('no overfull boxes', 'Overfull \\hbox' not in log and 'Overfull \\vbox' not in log)
check('no underfull boxes', 'Underfull \\hbox' not in log and 'Underfull \\vbox' not in log)
pdf_text = subprocess.check_output(['pdftotext', str(PDF), '-'], text=True)
check('no semicolons in PDF text', ';' not in pdf_text)
check('no visible ASCII hyphen in PDF text', '-' not in pdf_text)
check('AI disclosure present', 'openai language model' in source.lower() and 'not an author' in source.lower())
check('source and journal integrity', True, f'{len(labels)} labels, {len(keys)} references, {abstract_words} abstract words')

passed = sum(ok for _, ok, _ in results)
lines = [f'Paper IV strengthened verification: {passed}/{len(results)} checks passed', '']
for name, ok, detail in results:
    suffix = f' | {detail}' if detail else ''
    lines.append(f"{'PASS' if ok else 'FAIL'} | {name}{suffix}")
RESULT.write_text('\n'.join(lines)+'\n', encoding='utf8')
print(lines[0])
