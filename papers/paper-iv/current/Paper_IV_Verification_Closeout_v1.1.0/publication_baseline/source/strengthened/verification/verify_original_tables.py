#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import sympy as sp

ROOT = Path(__file__).resolve().parent / "original_release"
DATA = Path(__file__).resolve().parent / "original_data"
OUT = Path(__file__).resolve().parent / "ORIGINAL_TABLE_RERUN_RESULTS.txt"

r, u, x, w = sp.symbols("r u x w")


def P_polys(N: int, nmax: int) -> list[sp.Expr]:
    P = [sp.Integer(1)]
    for n in range(1, nmax + 1):
        value = -sum(
            (-1) ** k * sp.binomial(N * n - 1, N * k) * P[n - k]
            for k in range(1, n)
        ) - r * sum(
            (-1) ** k * sp.binomial(N * n - 1, N * k - 1) * P[n - k]
            for k in range(1, n + 1)
        )
        P.append(sp.expand(value))
    return P


def tangent(N: int, nmax: int) -> list[sp.Expr]:
    T = [sp.Integer(1)]
    for n in range(1, nmax + 1):
        value = (-1) ** n - sum(
            (-1) ** k * sp.binomial(N * n + N - 1, N * k) * T[n - k]
            for k in range(1, n + 1)
        )
        T.append(sp.expand(value))
    return T


def congruential_power(N: int, j: int, rr: int, nmax: int) -> list[sp.Expr]:
    phi = sum(sp.factorial(j) * w**n / sp.factorial(N * n + j) for n in range(nmax + 1))
    power = sp.series(phi ** (-rr), w, 0, nmax + 1).removeO().expand()
    return [sp.expand(power.coeff(w, n) * sp.factorial(N * n)) for n in range(nmax + 1)]


def theta_polys(N: int, nmax: int, P: list[sp.Expr]) -> list[sp.Expr]:
    vals = []
    for n in range(nmax + 1):
        val = (-1) ** n * sum(
            sp.binomial(N * n, N * q)
            * P[q].subs(r, 1)
            * u ** (N * q)
            * P[n - q].subs(r, u)
            for q in range(n + 1)
        )
        vals.append(sp.factor(sp.expand(val)))
    return vals

checks = []

sec = pd.read_csv(DATA / "transfer_secant_coefficients.csv")
for N, group in sec.groupby("N"):
    P = P_polys(int(N), int(group.n.max()))
    for row in group.itertuples(index=False):
        expected = sp.sympify(str(row.coefficient))
        actual = sp.expand(P[row.n].subs(r, row.r))
        checks.append(("transfer secant", actual == expected, (row.N, row.r, row.n)))

tan = pd.read_csv(DATA / "transfer_tangent_coefficients.csv")
for N, group in tan.groupby("N"):
    T = tangent(int(N), int(group.n.max()))
    for row in group.itertuples(index=False):
        checks.append(("transfer tangent", sp.sympify(str(row.coefficient)) == T[row.n], (row.N, row.n)))

param = pd.read_csv(DATA / "secancy_parameter_polynomials.csv")
for N, group in param.groupby("N"):
    P = P_polys(int(N), int(group.n.max()))
    for row in group.itertuples(index=False):
        expected = sp.sympify(str(row.polynomial), locals={"r": r})
        checks.append(("parameter polynomial", sp.expand(P[row.n] - expected) == 0, (row.N, row.n)))

cong = pd.read_csv(DATA / "congruential_euler_coefficients.csv")
for (N, j, rr), group in cong.groupby(["N", "j", "r"]):
    C = congruential_power(int(N), int(j), int(rr), int(group.n.max()))
    for row in group.itertuples(index=False):
        expected = sp.sympify(str(row.coefficient))
        checks.append(("congruential coefficient", sp.expand(C[row.n] - expected) == 0, (row.N, row.j, row.r, row.n)))

app = pd.read_csv(DATA / "block_appell_polynomials.csv")
for (N, j, rr), group in app.groupby(["N", "j", "r"]):
    maxblock = int(group.degree.max()) // int(N)
    C = congruential_power(int(N), int(j), int(rr), maxblock)
    for row in group.itertuples(index=False):
        actual = sum(
            sp.binomial(row.degree, N * n) * C[n] * x ** (row.degree - N * n)
            for n in range(row.degree // N + 1)
        )
        expected = sp.sympify(str(row.polynomial), locals={"x": x})
        checks.append(("Appell polynomial", sp.expand(actual - expected) == 0, (row.N, row.j, row.r, row.degree)))

theta = pd.read_csv(DATA / "transfer_theta_polynomials.csv")
for N, group in theta.groupby("N"):
    P = P_polys(int(N), int(group.n.max()))
    vals = theta_polys(int(N), int(group.n.max()), P)
    for row in group.itertuples(index=False):
        expected = sp.sympify(str(row.polynomial), locals={"u": u})
        checks.append(("theta polynomial", sp.expand(vals[row.n] - expected) == 0, (row.N, row.n)))

failed = [item for item in checks if not item[1]]
lines = [f"Original Paper IV tables: {len(checks) - len(failed)}/{len(checks)} rows verified", ""]
from collections import Counter
counts = Counter(name for name, ok, key in checks)
for name in sorted(counts):
    bad = sum(1 for n, ok, key in checks if n == name and not ok)
    lines.append(f"{'PASS' if bad == 0 else 'FAIL'} | {name} | {counts[name] - bad}/{counts[name]}")
if failed:
    lines += ["", "Failures:"] + [f"{name} {key}" for name, ok, key in failed[:50]]
OUT.write_text("\n".join(lines) + "\n", encoding="utf8")
print(lines[0])
if failed:
    raise SystemExit(1)
