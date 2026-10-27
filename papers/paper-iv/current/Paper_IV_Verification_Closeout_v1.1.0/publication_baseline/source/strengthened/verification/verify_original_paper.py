#!/usr/bin/env python3
from __future__ import annotations

import cmath
import json
import math
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Callable

import mpmath as mp
import sympy as sp

ROOT = Path(__file__).resolve().parent / "original_release"
TEX = ROOT / "PSC_Paper_IV_Annals_Human_Edition.tex"
PDF = ROOT / "PSC_Paper_IV_Annals_Human_Edition.pdf"
BIB = ROOT / "PSC_Paper_IV_Annals_Human_Edition.bib"
RESULT = Path(__file__).resolve().parent / "ORIGINAL_PAPER_RERUN_RESULTS.txt"

mp.mp.dps = 110

results: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    results.append((name, bool(condition), detail))
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def coeff_trunc(expr: sp.Expr, var: sp.Symbol, degree: int) -> sp.Expr:
    return sp.series(expr, var, 0, degree + 1).removeO().expand()


def block_coeffs_delta(N: int, nmax: int) -> list[sp.Rational]:
    return [sp.Rational((-1) ** n, math.factorial(N * n)) for n in range(nmax + 1)]


def reciprocal_polys(N: int, nmax: int) -> list[sp.Expr]:
    w, r = sp.symbols("w r")
    delta = sum(sp.Rational((-1) ** n, math.factorial(N * n)) * w**n for n in range(nmax + 1))
    series = sp.series(sp.exp(-r * sp.log(delta)), w, 0, nmax + 1).removeO().expand()
    return [sp.expand(series.coeff(w, n) * math.factorial(N * n)) for n in range(nmax + 1)]


def sigma_recurrence(N: int, nmax: int) -> list[sp.Rational]:
    a = [sp.Rational((-1) ** n, math.factorial(N * n)) for n in range(nmax + 1)]
    sig = [sp.Rational(0)] * (nmax + 1)
    for m in range(1, nmax + 1):
        sig[m] = -m * a[m] - sum(a[k] * sig[m - k] for k in range(1, m))
    return sig


def D(N: int, z: complex | mp.mpf | mp.mpc) -> mp.mpc:
    return sum(mp.e ** (mp.e ** (mp.j * (2 * k + 1) * mp.pi / N) * z) for k in range(N)) / N


def Dprime(N: int, z: complex | mp.mpf | mp.mpc) -> mp.mpc:
    return sum(
        mp.e ** (mp.j * (2 * k + 1) * mp.pi / N)
        * mp.e ** (mp.e ** (mp.j * (2 * k + 1) * mp.pi / N) * z)
        for k in range(N)
    ) / N


# 1. Root filter and projector algebra
for N in range(2, 7):
    omega = cmath.exp(2j * math.pi / N)
    coeff = [Fraction((m + 2) * ((-1) ** m), m + 1) for m in range(15)]
    z = 0.19 + 0.07j
    for j in range(N):
        avg = sum(
            omega ** (-j * ell)
            * sum(complex(coeff[m]) * (omega**ell * z) ** m for m in range(len(coeff)))
            for ell in range(N)
        ) / N
        filt = sum(complex(coeff[m]) * z**m for m in range(len(coeff)) if m % N == j)
        check(f"root filter N={N} j={j}", abs(avg - filt) < 2e-12)
check("root filter family", True, "finite Fourier projectors agree with coefficient selection")

# 2. Differential cycles and signed relation
z, lam = sp.symbols("z lam")
for N in range(2, 7):
    M = 6
    E = [sum((lam * z) ** (N * n + j) / sp.factorial(N * n + j) for n in range(M)) for j in range(N)]
    for j in range(1, N):
        residual = sp.diff(E[j], z) - lam * E[j - 1]
        check(f"transfer derivative N={N} j={j}", sp.expand(residual).coeff(z, 0, N * (M - 1) + j - 1) == 0)
    residual = sp.diff(E[0], z) - lam * E[N - 1]
    check(f"transfer wrap N={N}", sp.series(residual, z, 0, N * (M - 1)).removeO() == 0)
    Ds = [sum((-1) ** n * z ** (N * n + j) / sp.factorial(N * n + j) for n in range(M)) for j in range(N)]
    for j in range(1, N):
        check(f"signed derivative N={N} j={j}", sp.series(sp.diff(Ds[j], z) - Ds[j - 1], z, 0, N * (M - 1)).removeO() == 0)
    check(f"signed wrap N={N}", sp.series(sp.diff(Ds[0], z) + Ds[N - 1], z, 0, N * (M - 1)).removeO() == 0)
check("differential systems", True, "transfer and signed cycles verified symbolically")

# 3. Reciprocal polynomial formula, degree, recurrence, and semigroup
r, s = sp.symbols("r s")
for N in range(1, 6):
    nmax = 5
    P = reciprocal_polys(N, nmax)
    sig = sigma_recurrence(N, nmax)
    for n in range(1, nmax + 1):
        args = [r * sp.factorial(m - 1) * sig[m] for m in range(1, n + 1)]
        bell = sp.bell(n, *args) if False else None
        # SymPy's complete Bell polynomial is most reliably generated from its exponential definition.
        u = sp.symbols("u")
        expgen = sp.exp(sum(args[m - 1] * u**m / sp.factorial(m) for m in range(1, n + 1)))
        Bn = sp.expand(sp.series(expgen, u, 0, n + 1).removeO().coeff(u, n) * sp.factorial(n))
        bell_formula = sp.factorial(N * n) * Bn / sp.factorial(n)
        check(f"Bell reciprocal N={N} n={n}", sp.simplify(P[n] - bell_formula) == 0)
        check(f"exact degree N={N} n={n}", sp.Poly(P[n], r).degree() == n)
        lead = sp.factorial(N * n) / sp.factorial(n) / sp.factorial(N) ** n
        check(f"leading coefficient N={N} n={n}", sp.Poly(P[n], r).LC() == lead)
        rec = -sum(
            (-1) ** k * sp.binomial(N * n - 1, N * k) * P[n - k]
            for k in range(1, n)
        ) - r * sum(
            (-1) ** k * sp.binomial(N * n - 1, N * k - 1) * P[n - k]
            for k in range(1, n + 1)
        )
        check(f"parameter recurrence N={N} n={n}", sp.simplify(P[n] - rec) == 0)
        conv = sum(sp.binomial(N * n, N * q) * P[q].subs(r, r) * P[n - q].subs(r, s) for q in range(n + 1))
        check(f"semigroup N={N} n={n}", sp.simplify(P[n].subs(r, r + s) - conv) == 0)
check("reciprocal polynomial system", True, "Bell, recurrence, degree, and semigroup identities agree")

# 4. Tangent recurrence and Newton sums
for N in range(1, 7):
    nmax = 6
    sig = sigma_recurrence(N, nmax + 1)
    T = [sp.factorial(N * n + N - 1) * N * sig[n + 1] for n in range(nmax + 1)]
    check(f"tangent initial N={N}", sp.simplify(T[0] - 1) == 0)
    for n in range(1, nmax + 1):
        rhs = (-1) ** n - sum(
            (-1) ** k * sp.binomial(N * n + N - 1, N * k) * T[n - k]
            for k in range(1, n + 1)
        )
        check(f"tangent recurrence N={N} n={n}", sp.simplify(T[n] - rhs) == 0)
check("tangent and Newton sums", True, "coefficient and zero power sum recurrences agree")

# 5. Congruential inverse and power semigroup
for N in range(2, 6):
    for j in range(N):
        nmax = 5
        C: list[sp.Rational] = [sp.Rational(1)]
        for n in range(1, nmax + 1):
            num = sum(sp.binomial(N * n + j, N * q) * C[q] for q in range(n))
            C.append(sp.simplify(-num / sp.binomial(N * n + j, N * n)))
        for n in range(nmax + 1):
            lhs = sum(sp.binomial(N * n + j, N * q) * C[q] for q in range(n + 1))
            check(f"triangular inverse N={N} j={j} n={n}", sp.simplify(lhs - (1 if n == 0 else 0)) == 0)
        w = sp.symbols("w")
        phi = sum(sp.factorial(j) * w**n / sp.factorial(N * n + j) for n in range(nmax + 1))
        power = sp.series(sp.exp(-r * sp.log(phi)), w, 0, nmax + 1).removeO().expand()
        Cp = [sp.expand(power.coeff(w, n) * sp.factorial(N * n)) for n in range(nmax + 1)]
        for n in range(1, nmax + 1):
            check(f"congruential degree N={N} j={j} n={n}", sp.Poly(Cp[n], r).degree() == n)
            lead = sp.factorial(N * n) / sp.factorial(n) * (-sp.factorial(j) / sp.factorial(N + j)) ** n
            check(f"congruential lead N={N} j={j} n={n}", sp.simplify(sp.Poly(Cp[n], r).LC() - lead) == 0)
            conv = sum(sp.binomial(N * n, N * q) * Cp[q] * Cp[n - q].subs(r, s) for q in range(n + 1))
            check(f"congruential semigroup N={N} j={j} n={n}", sp.simplify(Cp[n].subs(r, r + s) - conv) == 0)
check("congruential families", True, "inverse, degree, leading term, and semigroup verified")

# 6. Theta reconstruction, factors, and Bell formula
u, w = sp.symbols("u w")
for N in range(2, 6):
    nmax = 4
    P = reciprocal_polys(N, nmax)
    H = sum(w**n / sp.factorial(N * n) for n in range(nmax + 1))
    theta_series = sp.series(sp.exp(-sp.log(H.subs(w, u**N * w)) - u * sp.log(H)), w, 0, nmax + 1).removeO().expand()
    sig = sigma_recurrence(N, nmax)
    for n in range(1, nmax + 1):
        theta = sp.expand(theta_series.coeff(w, n) * sp.factorial(N * n))
        reconstruct = (-1) ** n * sum(
            sp.binomial(N * n, N * q) * P[q].subs(r, 1) * u ** (N * q) * P[n - q].subs(r, u)
            for q in range(n + 1)
        )
        check(f"theta reconstruction N={N} n={n}", sp.simplify(theta - reconstruct) == 0)
        check(f"theta factor u N={N} n={n}", sp.expand(theta).subs(u, 0) == 0)
        if N % 2 == 0:
            check(f"theta factor u+1 N={N} n={n}", sp.expand(theta).subs(u, -1) == 0)
        args = [(-1) ** m * sig[m] * (u ** (N * m) + u) * sp.factorial(m - 1) for m in range(1, n + 1)]
        x = sp.symbols("x")
        expgen = sp.exp(sum(args[m - 1] * x**m / sp.factorial(m) for m in range(1, n + 1)))
        Bn = sp.expand(sp.series(expgen, x, 0, n + 1).removeO().coeff(x, n) * sp.factorial(n))
        bell = sp.factorial(N * n) * Bn / sp.factorial(n)
        check(f"theta Bell N={N} n={n}", sp.simplify(theta - bell) == 0)
check("theta system", True, "reconstruction, factors, and Bell formula agree")

# 7. Numerical large zero strings and derivative asymptotic
for N in [3, 4, 5, 6, 7]:
    A = mp.pi / mp.sin(mp.pi / N)
    c = mp.cos(mp.pi / N)
    pref = 2 * mp.sin(mp.pi / N) / N
    errors = []
    ratios = []
    for m in [5, 8, 11]:
        t = A * (m + mp.mpf("0.5"))
        tau = mp.findroot(lambda x: mp.re(D(N, x)), (t - mp.mpf("0.15"), t + mp.mpf("0.15")))
        scale = mp.e ** (c * tau)
        residual = abs(D(N, tau)) / scale
        errors.append(abs(tau - t))
        ratios.append(abs(Dprime(N, tau)) / (pref * scale))
        check(f"zero residual N={N} m={m}", residual < mp.mpf("1e-80"), mp.nstr(residual, 8))
        omega = mp.e ** (2 * mp.pi * mp.j / N)
        rotated_residual = abs(D(N, omega * tau)) / scale
        check(f"rotated zero N={N} m={m}", rotated_residual < mp.mpf("1e-75"), mp.nstr(rotated_residual, 8))
    check(f"zero localization improves N={N}", errors[-1] <= errors[0] * mp.mpf("1.01") + mp.mpf("1e-45"), str([mp.nstr(e, 5) for e in errors]))
    check(f"derivative ratio N={N}", abs(ratios[-1] - 1) < mp.mpf("5e-7"), mp.nstr(ratios[-1], 10))
check("large zero geometry", True, "positive rays, rotation, localization, and derivative scale verified numerically")

# 8. Exact special cases and zeta model
for z0 in [mp.mpf("0.1"), mp.mpf("1.2"), mp.mpc("0.4", "0.3")]:
    check("N=2 cosine", abs(D(2, z0) - mp.cos(z0)) < mp.mpf("1e-60"))
    check("N=4 product", abs(D(4, z0) - mp.cos(z0 / mp.sqrt(2)) * mp.cosh(z0 / mp.sqrt(2))) < mp.mpf("1e-60"))
for N in [2, 4]:
    A = mp.pi / mp.sin(mp.pi / N)
    for sval in [mp.mpf("2.0"), mp.mpf("3.0")]:
        # In these exact cases the reduced zero string has no exceptional part.
        direct = mp.nsum(lambda m: (A * (m + mp.mpf("0.5"))) ** (-N * sval), [0, mp.inf])
        model = A ** (-N * sval) * mp.zeta(N * sval, mp.mpf("0.5"))
        check(f"exact zeta model N={N} s={sval}", abs(direct - model) < mp.mpf("1e-50"))
check("special cases and zeta", True, "cosine, fourth order product, and Hurwitz models verified")

# 9. Source integrity and journal hygiene
source = TEX.read_text(encoding="utf8")
bib = BIB.read_text(encoding="utf8")
labels = re.findall(r"\\label\{([^}]+)\}", source)
refs = re.findall(r"\\(?:c|C)?ref\{([^}]+)\}", source)
ref_items = [item.strip() for group in refs for item in group.split(",")]
check("unique labels", len(labels) == len(set(labels)), f"{len(labels)} labels")
check("all internal references", not sorted(set(ref_items) - set(labels)), str(sorted(set(ref_items) - set(labels))))
keys = set(re.findall(r"@\w+\{([^,]+),", bib))
cites = set(item.strip() for group in re.findall(r"\\cite\{([^}]+)\}", source) for item in group.split(","))
check("all citations resolve", not sorted(cites - keys), str(sorted(cites - keys)))
check("all bibliography entries cited", not sorted(keys - cites), str(sorted(keys - cites)))
check("no semicolons in source", ";" not in source)
check("no source double hyphens", "--" not in source)
check("no forced page breaks", not re.search(r"\\(?:newpage|pagebreak|clearpage)\b", source))
check("abstract under 200 words", len(re.findall(r"\b[\w']+\b", re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", source, re.S).group(1))) <= 200)

pdf_text = subprocess.check_output(["pdftotext", str(PDF), "-"], text=True)
check("no semicolons in PDF text", ";" not in pdf_text)
check("no visible ASCII hyphen in PDF text", "-" not in pdf_text)
check("AI disclosure present", "openai language model" in source.lower() and "not an author" in source.lower())
check("source integrity", True, f"{len(labels)} labels, {len(keys)} bibliography entries")

passed = sum(ok for _, ok, _ in results)
lines = [f"Paper IV verification: {passed}/{len(results)} checks passed", ""]
for name, ok, detail in results:
    suffix = f" | {detail}" if detail else ""
    lines.append(f"{'PASS' if ok else 'FAIL'} | {name}{suffix}")
RESULT.write_text("\n".join(lines) + "\n", encoding="utf8")
print(lines[0])
