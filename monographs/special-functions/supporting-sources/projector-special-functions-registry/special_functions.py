from __future__ import annotations

from dataclasses import dataclass, asdict
from fractions import Fraction
from math import comb, factorial, pi
from pathlib import Path
from typing import Iterable, Sequence
import cmath
import csv
import json

import mpmath as mp
import numpy as np
import sympy as sp


def root_filter_value(coefficients: Sequence[complex], N: int, j: int, z: complex) -> complex:
    """Evaluate the j-th residue section of a finite exponential series.

    ``coefficients[m]`` is the EGF coefficient a_m in sum a_m z^m/m!.
    """
    return sum(
        coefficients[m] * z**m / factorial(m)
        for m in range(j, len(coefficients), N)
    )


def root_filter_average(function, N: int, j: int, z: complex) -> complex:
    omega = cmath.exp(2j * cmath.pi / N)
    return sum(omega ** (-j * ell) * function(omega**ell * z) for ell in range(N)) / N


def transfer_exponential(N: int, j: int, z: complex, lam: complex = 1, terms: int = 80) -> complex:
    """Stable evaluation of the j-th exponential residue section.

    Terms are advanced by the factorial ratio between successive residue
    exponents.  Mpmath inputs retain the active arbitrary precision; ordinary
    numeric inputs use native complex arithmetic.
    """
    if N < 1 or not 0 <= j < N:
        raise ValueError("require N >= 1 and 0 <= j < N")
    if terms < 1:
        return 0.0 + 0.0j
    high_precision = isinstance(z, (mp.mpf, mp.mpc)) or isinstance(lam, (mp.mpf, mp.mpc))
    x = mp.mpc(lam) * mp.mpc(z) if high_precision else complex(lam) * complex(z)
    term = x**j / factorial(j)
    total = term
    degree = j
    for _ in range(1, terms):
        denominator = 1
        for k in range(1, N + 1):
            denominator *= degree + k
        term *= x**N / denominator
        total += term
        degree += N
    return total


def transfer_exponential_hypergeom(N: int, j: int, z: complex, lam: complex = 1) -> complex:
    params = [mp.mpf(j + 1 + q) / N for q in range(N)]
    removed = False
    filtered = []
    for p in params:
        if not removed and abs(p - 1) < mp.mpf("1e-30"):
            removed = True
        else:
            filtered.append(p)
    return (lam * z) ** j / factorial(j) * mp.hyper([], filtered, (lam * z) ** N / N**N)


def D_value(N: int, z: complex, terms: int = 80) -> complex:
    """Stable evaluation of D_N(z)=sum (-1)^n z^(Nn)/(Nn)!."""
    if N < 1:
        raise ValueError("N must be positive")
    if terms < 1:
        return 0.0 + 0.0j
    high_precision = isinstance(z, (mp.mpf, mp.mpc))
    zc = mp.mpc(z) if high_precision else complex(z)
    term = mp.mpc(1) if high_precision else 1.0 + 0.0j
    total = term
    degree = 0
    for _ in range(1, terms):
        denominator = 1
        for k in range(1, N + 1):
            denominator *= degree + k
        term *= -(zc**N) / denominator
        total += term
        degree += N
    return total


def D_root_average(N: int, z: complex) -> complex:
    roots = [cmath.exp(1j * (2 * k + 1) * pi / N) for k in range(N)]
    return sum(cmath.exp(root * z) for root in roots) / N


def block_product(a: Sequence[Fraction], b: Sequence[Fraction], N: int, nmax: int | None = None) -> list[Fraction]:
    """Product for series sum a_n z^(Nn)/(Nn)! and sum b_n z^(Nn)/(Nn)!."""
    if nmax is None:
        nmax = min(len(a), len(b)) - 1
    out = [Fraction(0) for _ in range(nmax + 1)]
    for n in range(nmax + 1):
        out[n] = sum(
            Fraction(comb(N * n, N * k)) * a[k] * b[n - k]
            for k in range(n + 1)
            if k < len(a) and n - k < len(b)
        )
    return out


def reciprocal_block_coefficients(denominator: Sequence[Fraction], N: int, nmax: int) -> list[Fraction]:
    if not denominator or denominator[0] == 0:
        raise ValueError("denominator must have nonzero constant term")
    out = [Fraction(0) for _ in range(nmax + 1)]
    out[0] = Fraction(1, 1) / denominator[0]
    for n in range(1, nmax + 1):
        total = sum(
            Fraction(comb(N * n, N * k)) * denominator[k] * out[n - k]
            for k in range(1, min(n, len(denominator) - 1) + 1)
        )
        out[n] = -total / denominator[0]
    return out


def denominator_coefficients(N: int, nmax: int) -> list[Fraction]:
    return [Fraction((-1) ** n) for n in range(nmax + 1)]


def secant_coefficients(N: int, order: int, nmax: int) -> list[Fraction]:
    if order < 0:
        raise ValueError("order must be nonnegative")
    base = reciprocal_block_coefficients(denominator_coefficients(N, nmax), N, nmax)
    out = [Fraction(1)] + [Fraction(0) for _ in range(nmax)]
    for _ in range(order):
        out = block_product(out, base, N, nmax)
    return out


def secant_value(N: int, order: int, z: complex, terms: int = 80) -> complex:
    return D_value(N, z, terms) ** (-order)


def transfer_tangent_value(N: int, z: complex, terms: int = 80) -> complex:
    """Evaluate -D_N'(z)/D_N(z) using stable factorial-ratio series."""
    if N < 1:
        raise ValueError("N must be positive")
    high_precision = isinstance(z, (mp.mpf, mp.mpc))
    zc = mp.mpc(z) if high_precision else complex(z)
    d = D_value(N, zc, terms)
    if abs(d) == 0:
        raise ZeroDivisionError("z is a zero of D_N")
    if zc == 0:
        one = mp.mpc(1) if high_precision else 1.0 + 0.0j
        zero = mp.mpc(0) if high_precision else 0.0 + 0.0j
        return one if N == 1 else zero
    term = -(zc ** (N - 1)) / factorial(N - 1)
    dp = term
    degree = N - 1
    for _ in range(2, terms):
        denominator = 1
        for k in range(1, N + 1):
            denominator *= degree + k
        term *= -(zc**N) / denominator
        dp += term
        degree += N
    return -dp / d


def transfer_tangent_coefficients(N: int, nmax: int) -> list[Fraction]:
    """Coefficients T_n in Tan_N(z)=sum T_n z^(Nn+N-1)/(Nn+N-1)!."""
    out = [Fraction(0) for _ in range(nmax + 1)]
    for m in range(nmax + 1):
        rhs = Fraction((-1) ** m)
        earlier = sum(
            Fraction((-1) ** k * comb(N * m + N - 1, N * k)) * out[m - k]
            for k in range(1, m + 1)
        )
        out[m] = rhs - earlier
    return out


def section_value(N: int, j: int, z: complex, terms: int = 80) -> complex:
    return transfer_exponential(N, j, z, 1, terms)


def congruential_euler_value(N: int, j: int, z: complex, terms: int = 80) -> complex:
    if z == 0:
        return 1.0 + 0j
    return (z**j / factorial(j)) / section_value(N, j, z, terms)


def congruential_euler_coefficients(N: int, j: int, nmax: int) -> list[Fraction]:
    out = [Fraction(0) for _ in range(nmax + 1)]
    out[0] = Fraction(1)
    for n in range(1, nmax + 1):
        numerator = sum(Fraction(comb(N * n + j, N * q)) * out[q] for q in range(n))
        out[n] = -numerator / Fraction(comb(N * n + j, N * n))
    return out


def congruential_power_coefficients(N: int, j: int, order: int, nmax: int) -> list[Fraction]:
    base = congruential_euler_coefficients(N, j, nmax)
    out = [Fraction(1)] + [Fraction(0) for _ in range(nmax)]
    for _ in range(order):
        out = block_product(out, base, N, nmax)
    return out


def full_egf_coefficients_from_block(block: Sequence[Fraction], N: int, max_degree: int) -> list[Fraction]:
    out = [Fraction(0) for _ in range(max_degree + 1)]
    for n, value in enumerate(block):
        if N * n <= max_degree:
            out[N * n] = value
    return out


def block_appell_polynomials(N: int, j: int, order: int, max_degree: int) -> list[sp.Expr]:
    x = sp.Symbol("x")
    block = congruential_power_coefficients(N, j, order, max_degree // N)
    g = full_egf_coefficients_from_block(block, N, max_degree)
    polys: list[sp.Expr] = []
    for m in range(max_degree + 1):
        poly = sum(sp.binomial(m, k) * sp.Rational(g[k].numerator, g[k].denominator) * x ** (m - k) for k in range(m + 1))
        polys.append(sp.expand(poly))
    return polys


def secant_parameter_polynomial(N: int, n: int) -> sp.Expr:
    """Polynomial in r whose integer values give coefficients of D_N(z)^(-r)."""
    r = sp.Symbol("r")
    if n == 0:
        return sp.Integer(1)
    total = sp.Integer(0)

    def recurse(remaining: int, max_i: int, counts: dict[int, int]) -> None:
        nonlocal total
        if remaining == 0:
            M = sum(counts.values())
            term = (-1) ** (n + M) * sp.rf(r, M)
            for i, mi in counts.items():
                term /= sp.factorial(mi) * sp.factorial(N * i) ** mi
            total += sp.factorial(N * n) * term
            return
        if max_i == 0:
            return
        max_count = remaining // max_i
        for c in range(max_count + 1):
            if c:
                counts[max_i] = c
            recurse(remaining - c * max_i, max_i - 1, counts)
            counts.pop(max_i, None)

    recurse(n, n, {})
    return sp.factor(sp.expand(total))


def theta_polynomials(max_m: int) -> list[sp.Expr]:
    x, z = sp.symbols("x z")
    # exp(x log(sech z)) avoids ambiguous symbolic noninteger powers.
    expr = sp.sech(x * z) * sp.exp(x * sp.log(sp.sech(z)))
    series = sp.series(expr, z, 0, 2 * max_m + 2).removeO().expand()
    return [sp.factor(sp.expand(series.coeff(z, 2 * m) * sp.factorial(2 * m))) for m in range(max_m + 1)]


def spectral_zeta_N2_positive(s: complex) -> complex:
    return mp.pi ** (-s) * mp.zeta(s, mp.mpf("0.5"))


def spectral_zeta_N2_partial(s: complex, terms: int) -> complex:
    return sum(((k + mp.mpf("0.5")) * mp.pi) ** (-s) for k in range(terms))


def amice_transform_coefficients(egf_coeffs: Sequence[Fraction], degree: int) -> list[Fraction]:
    """Coefficients of A(log(1+T)) through T^degree for an EGF A."""
    T = sp.Symbol("T")
    log_series = sp.series(sp.log(1 + T), T, 0, degree + 1).removeO()
    expr = sp.Integer(0)
    for n, a in enumerate(egf_coeffs):
        if n > degree:
            break
        expr += sp.Rational(a.numerator, a.denominator) * log_series**n / sp.factorial(n)
    expr = sp.series(expr, T, 0, degree + 1).removeO().expand()
    return [Fraction(int(sp.numer(expr.coeff(T, k))), int(sp.denom(expr.coeff(T, k)))) for k in range(degree + 1)]


@dataclass(frozen=True)
class RegistryEntry:
    family: str
    symbol: str
    definition: str
    object_type: str
    status: str
    classical_boundary: str
    core_property: str


def registry_entries() -> list[RegistryEntry]:
    return [
        RegistryEntry(
            "Transfer-block sections",
            r"\\mathcal B_{N,j}F",
            r"N^{-1}\\sum_{\\ell=0}^{N-1}\\omega^{-j\\ell}F(\\omega^\\ell z)",
            "construction schema",
            "proved operator construction",
            "classical multisection/root-of-unity filter",
            "exact projection and reconstruction",
        ),
        RegistryEntry(
            "Transfer exponentials",
            r"\\mathsf E_{N,j}(\\lambda z)",
            r"\\sum_{n\\ge0}(\\lambda z)^{Nn+j}/(Nn+j)!",
            "entire scalar function",
            "explicit; classical boundary",
            r"generalized hyperbolic/Olivier-type section; ${}_0F_{N-1}$",
            r"D^N f=\\lambda^N f and cyclic derivative law",
        ),
        RegistryEntry(
            "Universal transfer denominator",
            r"D_N(z)",
            r"\\sum_{n\\ge0}(-1)^n z^{Nn}/(Nn)!",
            "entire scalar function",
            "explicit; classical boundary",
            "rotated transfer exponential / exponential polynomial",
            r"D_N^{(N)}=-D_N",
        ),
        RegistryEntry(
            "Transfer secants",
            r"\\mathsf{Sec}_N^{[r]}(z)",
            r"D_N(z)^{-r}",
            "meromorphic scalar family",
            "core candidate-new family",
            r"contains $\\sec z$ at $(N,r)=(2,1)$",
            "reciprocal-power semigroup and block convolution",
        ),
        RegistryEntry(
            "Transfer tangents",
            r"\\mathsf{Tan}_N(z)",
            r"-D_N'(z)/D_N(z)",
            "meromorphic scalar function",
            "derived and computationally verified",
            r"contains $\\tan z$ at $N=2$",
            r"(\\mathsf{Sec}_N^{[r]})'=r\\mathsf{Tan}_N\\mathsf{Sec}_N^{[r]}",
        ),
        RegistryEntry(
            "Congruential Euler blocks",
            r"\\mathsf{CE}_{N,j}(z)",
            r"(z^j/j!)/\\mathsf E_{N,j}(z)",
            "meromorphic scalar family",
            "explicit; overlaps recent congruential Euler literature",
            r"reciprocal of a ${}_0F_{N-1}$ section",
            "triangular inverse system and p-adic packet arithmetic",
        ),
        RegistryEntry(
            "Higher congruential Euler powers",
            r"\\mathsf{CE}_{N,j}^{[r]}(z)",
            r"\\mathsf{CE}_{N,j}(z)^r",
            "meromorphic scalar family",
            "natural extension",
            "higher-order Euler/Appell boundary",
            "binomial block convolution in r",
        ),
        RegistryEntry(
            "Block-Appell polynomials",
            r"E_m^{(N,j;r)}(x)",
            r"\\mathsf{CE}_{N,j}(z)^r e^{xz}=\\sum_mE_m^{(N,j;r)}(x)z^m/m!",
            "polynomial sequence",
            "explicit derived family",
            "Appell/Sheffer theory",
            r"\\partial_xE_m=mE_{m-1}",
        ),
        RegistryEntry(
            "Transfer-secancy parameter polynomials",
            r"P_{N,n}(r)",
            r"[z^{Nn}/(Nn)!]D_N(z)^{-r}",
            "polynomial in the order parameter",
            "explicit derived family",
            "Bell/partition polynomial boundary",
            "rising-factorial partition formula",
        ),
        RegistryEntry(
            "Euler-transfer theta polynomials",
            r"\\Theta_{2m}(x)",
            r"\\sech(xz)\\sech^x z=\\sum_m\\Theta_{2m}(x)z^{2m}/(2m)!",
            "polynomial sequence",
            "explicit in Euler transfer branch",
            "higher-order Euler boundary",
            "integer coefficients and exact inverse kernel",
        ),
        RegistryEntry(
            "Spectral block zeta",
            r"\\mathfrak Z_N(s)",
            r"\\sum_{D_N(\\rho)=0}\\rho^{-s}",
            "zeta-type function",
            "candidate-new; analytic completion required",
            "spectral zeta / zero zeta tradition",
            "encodes pole spectrum and coefficient asymptotics",
        ),
        RegistryEntry(
            "Residue-weighted block zeta",
            r"\\mathfrak Z_N^{[r]}(s)",
            r"\\sum_{D_N(\\rho)=0}D_N'(\\rho)^{-r}\\rho^{-s}",
            "zeta-type function",
            "candidate-new; regularization required",
            "Mittag-Leffler and spectral determinant boundary",
            "directly weights reciprocal-pole residues",
        ),
        RegistryEntry(
            "p-adic transfer avatars",
            r"\\widehat F(T)=F(\\log(1+T))",
            "Amice-Mahler transform of each admissible family",
            "p-adic analytic/formal family",
            "conditional on bounded or weighted admissibility",
            "Amice and Mahler theory",
            "mixed Kummer and finite-difference bounds",
        ),
        RegistryEntry(
            "Packet resolvent functions",
            r"R_{ij}(z)=P_i(T-zI)^{-1}P_j",
            "projected resolvent",
            "operator-valued special function",
            "proved operator construction",
            "classical resolvent/Riesz calculus",
            "mixed-chart resolvent identity",
        ),
        RegistryEntry(
            "Nonlinear packet-tree functions",
            r"\\mathcal J_{i;j_1\\ldots j_m}^{(m)}",
            "projected derivatives and rooted-tree compositions",
            "multilinear/operator family",
            "proved calculus; not yet one canonical scalar family",
            "Faà di Bruno and operad theory",
            "exact nonlinear refinement and composition",
        ),
    ]


def write_registry(output_dir: str | Path) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    entries = registry_entries()
    (output / "special_function_registry.json").write_text(
        json.dumps([asdict(e) for e in entries], indent=2), encoding="utf-8"
    )
    with (output / "special_function_registry.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(entries[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(e) for e in entries)


if __name__ == "__main__":
    write_registry(Path(__file__).resolve().parent / "results")
