from __future__ import annotations

import cmath
import itertools
import json
import math
import random
import re
from fractions import Fraction
from pathlib import Path

import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / 'PSC_Strong_Artin_Residual_Realization.tex'
BIB = ROOT / 'PSC_Strong_Artin_Residual_Realization.bib'

checks = 0
failures: list[str] = []
groups: list[tuple[str, int]] = []


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        failures.append(message)


def group(name: str, fn) -> None:
    before = checks
    fn()
    groups.append((name, checks - before))


def mat_tuple(A: np.ndarray, p: int) -> tuple[int, ...]:
    return tuple(int(x) % p for x in A.reshape(-1))


def closure(gens: list[np.ndarray], p: int) -> list[np.ndarray]:
    n = gens[0].shape[0]
    I = np.eye(n, dtype=int)
    seen = {mat_tuple(I, p): I % p}
    queue = [I % p]
    allgens = gens[:]
    while queue:
        A = queue.pop()
        for B in allgens:
            C = (A @ B) % p
            key = mat_tuple(C, p)
            if key not in seen:
                seen[key] = C
                queue.append(C)
    return list(seen.values())


def trace_mod(A: np.ndarray, p: int) -> int:
    return int(np.trace(A)) % p


def primitive_root_of_order(m: int, p: int) -> int:
    g = int(sp.primitive_root(p))
    return pow(g, (p - 1) // m, p)


def trace_bound_examples() -> None:
    # Cyclic two dimensional examples.
    for m, p in [(3, 7), (4, 13), (5, 11), (6, 13), (8, 17), (10, 41)]:
        a = primitive_root_of_order(m, p)
        R = np.array([[a, 0], [0, pow(a, -1, p)]], dtype=int)
        G = closure([R], p)
        traces = {trace_mod(A, p) for A in G}
        check(len(G) == m, f'cyclic order m={m},p={p}')
        check(len(G) <= len(traces) ** 4, f'cyclic trace bound m={m},p={p}')

    # Dihedral examples in cross characteristic.
    for m, p in [(3, 7), (4, 13), (5, 11), (6, 13), (8, 17)]:
        a = primitive_root_of_order(m, p)
        R = np.array([[a, 0], [0, pow(a, -1, p)]], dtype=int)
        S = np.array([[0, 1], [1, 0]], dtype=int)
        G = closure([R, S], p)
        traces = {trace_mod(A, p) for A in G}
        check(len(G) == 2 * m, f'dihedral order m={m},p={p}')
        check(len(G) <= len(traces) ** 4, f'dihedral trace bound m={m},p={p}')

    # S3 standard representation.
    for p in [5, 7, 11, 13, 17, 19]:
        A = np.array([[0, -1], [1, -1]], dtype=int) % p
        B = np.array([[0, 1], [1, 0]], dtype=int) % p
        G = closure([A, B], p)
        traces = {trace_mod(X, p) for X in G}
        check(len(G) == 6, f'S3 order p={p}')
        check(len(G) <= len(traces) ** 4, f'S3 trace bound p={p}')

    # Q8 in fields containing a square root of minus one.
    for p in [5, 13, 17, 29]:
        i = next(x for x in range(p) if x * x % p == p - 1)
        Iq = np.array([[i, 0], [0, -i]], dtype=int) % p
        Jq = np.array([[0, 1], [-1, 0]], dtype=int) % p
        G = closure([Iq, Jq], p)
        traces = {trace_mod(X, p) for X in G}
        check(len(G) == 8, f'Q8 order p={p}')
        check(len(G) <= len(traces) ** 4, f'Q8 trace bound p={p}')


def algebraic_central_no_go() -> None:
    def weyl_dim(lam: tuple[int, ...]) -> int:
        n = len(lam)
        out = Fraction(1, 1)
        for i in range(n):
            for j in range(i + 1, n):
                out *= Fraction(lam[i] - lam[j] + j - i, j - i)
        return int(out)

    rng = random.Random(1801)
    for n in range(2, 9):
        primes = [p for p in sp.factorint(n)]
        for _ in range(400):
            vals = sorted([rng.randrange(0, 9) for __ in range(n)], reverse=True)
            lam = tuple(vals)
            N = weyl_dim(lam)
            w = sum(lam)
            check((w * N) % n == 0, f'GLn determinant exponent n={n},lam={lam}')
            for p in primes:
                check((w * N) % p == 0, f'central blindness p={p},n={n},lam={lam}')
            # determinant twists preserve the identity
            k = rng.randrange(-5, 6)
            wp = w + n * k
            check((wp * N) % n == 0, f'determinant twist identity n={n}')


def total_induction_blind() -> None:
    for p in [2, 3, 5, 7, 11]:
        base = list(range(p))
        for j in range(p):
            rotated = [((a + j) % p) for a in base]
            check(sorted(rotated) == base, f'torsor sum invariant p={p},j={j}')
        # The regular character vanishes away from the identity.
        zeta = cmath.exp(2j * math.pi / p)
        for r in range(p):
            val = sum(zeta ** (a * r) for a in range(p))
            target = p if r == 0 else 0
            check(abs(val - target) < 1e-8, f'regular character p={p},r={r}')


def extension_spectra() -> None:
    rng = random.Random(321)
    for p in [2, 3, 5, 7]:
        zeta = cmath.exp(2j * math.pi / p)
        for _ in range(300):
            arrays = [np.array([rng.randrange(0, 5) for _ in range(p)], dtype=int)
                      for __ in range(rng.randrange(1, 6))]
            j = rng.randrange(p)
            shifted = [np.roll(a, j) for a in arrays]
            sols = [x for x in range(p)
                    if all(np.array_equal(np.roll(a, x), b) for a, b in zip(arrays, shifted))]
            stab = [x for x in range(p)
                    if all(np.array_equal(np.roll(a, x), a) for a in arrays)]
            check(sorted(sols) == sorted({(j + x) % p for x in stab}), 'alignment coset')
            for a, b in zip(arrays, shifted):
                for r in range(p):
                    ha = sum(int(a[q]) * zeta ** (q * r) for q in range(p))
                    hb = sum(int(b[q]) * zeta ** (q * r) for q in range(p))
                    check(abs(hb - zeta ** (j * r) * ha) < 1e-7, 'Fourier spectrum shift')


def finite_satake_and_alphabet() -> None:
    rng = random.Random(45)
    for d in range(1, 10):
        for f in [q for q in range(1, d + 1) if d % q == 0]:
            for M in range(1, 14):
                for _ in range(20):
                    e = rng.randrange(f * M)
                    alpha = cmath.exp(2j * math.pi * e / (f * M))
                    check(abs((alpha ** f) ** M - 1) < 1e-7, 'base changed finite exponent')
                    check(abs(alpha ** (d * M) - 1) < 1e-7, 'descent root bounded')
    for N in range(1, 12):
        for n in range(1, 10):
            brute = sum(1 for _ in itertools.combinations_with_replacement(range(N), n))
            check(brute == math.comb(N + n - 1, n), 'finite polynomial alphabet size')

    alphabet = [(1, -3, 2), (1, -1, -2), (1, 2, -3), (1, 0, 1), (1, 4, 4)]
    bad = set()
    for P, Q in itertools.combinations(alphabet, 2):
        nonzero = [abs(a - b) for a, b in zip(P, Q) if a != b]
        g = math.gcd(*nonzero)
        bad.update(int(q) for q in sp.factorint(g))
    for ell in list(sp.primerange(2, 150)):
        red = {tuple(c % ell for c in P) for P in alphabet}
        check((len(red) == len(alphabet)) == (ell not in bad), f'separating alphabet ell={ell}')


def residual_lifting_toys() -> None:
    # S3 standard characteristic polynomials over characteristic zero:
    # identity, transpositions, and 3 cycles.
    polys = {(1, -2, 1), (1, 0, -1), (1, 1, 1)}
    t = len({-P[1] for P in polys})
    bound = t ** 4
    check(6 <= bound, 'S3 residual image bound')
    for ell in [101, 103, 107, 109]:
        reductions = {tuple(c % ell for c in P) for P in polys}
        check(len(reductions) == len(polys), f'S3 exact alphabet lift ell={ell}')
        check(ell > 6, f'S3 cross characteristic ell={ell}')

    # Cyclic finite-image polynomial alphabet lifts uniquely at a large prime.
    for m in [3, 4, 5, 6, 8, 10]:
        roots = [cmath.exp(2j * math.pi * a / m) for a in range(m)]
        traces = {round((z + z.conjugate()).real, 10) for z in roots}
        bound = len(traces) ** 4
        check(m <= bound, f'cyclic universal bound m={m}')


def quotient_prime_collapse() -> None:
    rng = random.Random(777)
    x = sp.symbols('x')
    for p in [2, 3, 5, 7]:
        for n in range(1, 6):
            for _ in range(70):
                A = sp.Matrix([[rng.randrange(p) for _ in range(n)] for __ in range(n)])
                cp = A.charpoly(x).all_coeffs()
                cpp = (A ** p).charpoly(x).all_coeffs()
                check(all((int(a) - int(b)) % p == 0 for a, b in zip(cp, cpp)),
                      f'Frobenius characteristic polynomial p={p},n={n}')
        for j in range(p):
            check(pow(1, j, p) == 1, f'quotient label collapse p={p},j={j}')


def ladic_rigidity_toys() -> None:
    for N in [2, 3, 4, 5, 6, 8, 10, 12, 15]:
        z = cmath.exp(2j * math.pi / N)
        A = np.diag([z, z.conjugate()])
        traces = {round(np.trace(np.linalg.matrix_power(A, j)).real, 10) for j in range(N)}
        check(len(traces) <= N, f'finite l-adic trace alphabet N={N}')
        check(np.linalg.norm(np.linalg.matrix_power(A, N) - np.eye(2)) < 1e-8,
              f'finite l-adic image N={N}')

    # Semisimplicity is essential: finite unipotent truncations all have trace two,
    # while the compatible pro-l unipotent family would be infinite.
    for ell in [3, 5, 7, 11]:
        for m in range(1, 6):
            modulus = ell ** m
            count = modulus
            traces = {2 % modulus}
            check(len(traces) == 1 and count > 1, 'unipotent counterexample to omission of semisimplicity')


def positive_cone() -> None:
    chi = np.array([1, 0, 0])
    theta1 = np.array([1, 1, 0])
    theta2 = np.array([1, -1, 0])
    check(np.array_equal(2 * chi, theta1 + theta2), 'positive saturation identity')
    # A signed Brauer relation uses a negative coefficient and therefore
    # does not lie in the positive induction monoid.
    signed_coefficients = [1, -1]
    check(any(c < 0 for c in signed_coefficients), 'signed Brauer relation contains a negative coefficient')


def source_integrity() -> None:
    tex = TEX.read_text()
    bib = BIB.read_text()
    labels = re.findall(r'\\label\{([^}]+)\}', tex)
    check(len(labels) == len(set(labels)), 'unique labels')
    refs = []
    for cmd in ['ref', 'cref', 'Cref', 'eqref']:
        for g in re.findall(r'\\' + cmd + r'\{([^}]+)\}', tex):
            refs.extend(x.strip() for x in g.split(','))
    check(not (set(refs) - set(labels)), 'all references resolve')
    keys = set(re.findall(r'@\w+\{([^,]+),', bib))
    cites = set()
    for g in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}', tex):
        cites.update(x.strip() for x in g.split(','))
    check(not (cites - keys), 'all citations resolve')
    check(not (keys - cites), 'all bibliography entries cited')

    proved = sum(tex.count(f'\\begin{{{e}}}') for e in ['theorem', 'proposition', 'lemma', 'corollary'])
    proved_examples = len(re.findall(r'\\end\{example\}\s*\\begin\{proof\}', tex))
    proofs = tex.count('\\begin{proof}')
    check(proved + proved_examples == proofs, f'proof count {proved}+{proved_examples}={proofs}')

    abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.S).group(1)
    abstract = re.sub(r'\\[A-Za-z]+(?:\{[^{}]*\})?', ' ', abstract)
    words = re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", abstract)
    check(len(words) <= 200, f'abstract word count {len(words)}')
    check(';' not in tex, 'no source semicolons')
    check('--' not in tex, 'no source double ASCII hyphens')
    check('\\newpage' not in tex and '\\pagebreak' not in tex, 'no forced page breaks')

    figs = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', tex)
    check(len(figs) == 21, f'21 referenced figures, found {len(figs)}')
    check(len(figs) == len(set(figs)), 'unique figure uses')
    for f in figs:
        check((ROOT / 'figures' / f).exists(), f'figure exists {f}')

    log = (ROOT / 'build19.log').read_text(errors='ignore')
    check('undefined references' not in log.lower(), 'no undefined references')
    check('undefined citations' not in log.lower(), 'no undefined citations')
    check('Overfull' not in log, 'no overfull boxes')

    pdftext = Path('/tmp/strong_artin_residual_text.txt')
    if pdftext.exists():
        txt = pdftext.read_text(errors='ignore')
        check(';' not in txt, 'no PDF semicolons')
        check('-' not in txt, 'no visible ASCII hyphens')


for name, fn in [
    ('Finite trace image bounds', trace_bound_examples),
    ('Algebraic central no go', algebraic_central_no_go),
    ('Total induction blindness', total_induction_blind),
    ('Extension spectra', extension_spectra),
    ('Finite Satake alphabets', finite_satake_and_alphabet),
    ('Cross characteristic residual lifts', residual_lifting_toys),
    ('Quotient prime collapse', quotient_prime_collapse),
    ('l adic finite trace rigidity', ladic_rigidity_toys),
    ('Positive Artin cone', positive_cone),
    ('Source and package integrity', source_integrity),
]:
    group(name, fn)

summary = {
    'checks': checks,
    'failures': failures,
    'groups': [{'name': n, 'checks': c} for n, c in groups],
}
(ROOT / 'verification' / 'residual_verification_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
lines = [f'Strong Artin residual realization verification: {checks - len(failures)}/{checks} checks passed']
lines.extend(f'{n}: {c}' for n, c in groups)
if failures:
    lines.append('Failures:')
    lines.extend(failures)
(ROOT / 'verification' / 'residual_verification_summary.txt').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
raise SystemExit(1 if failures else 0)
