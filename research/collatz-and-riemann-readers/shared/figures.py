#!/usr/bin/env python3
"""Reproduce the finite diagnostics and schematic figures for the conjecture set.

Run with Python 3.12 and the versions in figures/requirements.txt. No network
access, random inputs, symbolic algebra package, or external data is required.
The historical Collatz coverage counts are declared inputs, not recomputed.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import mpmath as mp
import numpy as np


CHARCOAL = "#29333A"
BLUE = "#245B78"
TEAL = "#377C78"
COPPER = "#AE6749"
GRAY = "#858B90"
LIGHT = "#E8EBEC"


def v2(n: int) -> int:
    if n <= 0:
        raise ValueError("v2 requires a positive integer")
    return (n & -n).bit_length() - 1


def odd_step(n: int) -> tuple[int, int]:
    if n <= 0 or n % 2 != 1:
        raise ValueError("the accelerated map requires a positive odd integer")
    valuation = v2(3 * n + 1)
    return (3 * n + 1) >> valuation, valuation


def orbit(n: int, max_steps: int = 512) -> list[dict]:
    initial = n
    rows = [{"k": 0, "x": n, "r": None, "S": 0, "C": 0, "p": 1}]
    power, offset, exponent = 1, 0, 0
    for k in range(1, max_steps + 1):
        if n == 1:
            break
        n, valuation = odd_step(n)
        offset = 3 * offset + (1 << exponent)
        power *= 3
        exponent += valuation
        assert power * initial + offset == n * (1 << exponent)
        rows.append({"k": k, "x": n, "r": valuation, "S": exponent,
                     "C": offset, "p": power})
    if rows[-1]["x"] != 1:
        raise RuntimeError(f"orbit {initial} exceeds the declared {max_steps} step cap")
    return rows


def word_affine(word: tuple[int, ...]) -> tuple[int, int, int]:
    power, offset, exponent = 1, 0, 0
    for valuation in word:
        offset = 3 * offset + (1 << exponent)
        power *= 3
        exponent += valuation
    return power, offset, exponent


def word_residue(word: tuple[int, ...]) -> tuple[int, int]:
    power, offset, exponent = word_affine(word)
    modulus = 1 << (exponent + 1)
    residue = ((1 << exponent) - offset) * pow(power, -1, modulus) % modulus
    return residue, modulus


def xi(s):
    # This evaluation is only called away from s=0 and s=1.
    return s * (s - 1) * mp.power(mp.pi, -s / 2) * mp.gamma(s / 2) * mp.zeta(s) / 2


def xi_real_alternative(t):
    # Orthogonal evaluation using the real Hardy Z function on the critical line.
    return -(mp.mpf(".25") + t * t) * mp.power(mp.pi, -mp.mpf(".25")) * abs(
        mp.gamma(mp.mpf(".25") + 0.5j * t)) * mp.siegelz(t) / 2


def fraction_text(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def configure_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
        "mathtext.fontset": "dejavuserif",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "axes.edgecolor": CHARCOAL,
        "axes.labelcolor": CHARCOAL,
        "text.color": CHARCOAL,
        "xtick.color": CHARCOAL,
        "ytick.color": CHARCOAL,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.65,
        "xtick.major.width": 0.65,
        "ytick.major.width": 0.65,
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def style_axes(ax, grid=True):
    if grid:
        ax.grid(axis="y", color=LIGHT, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=9, length=3)


def save_figure(fig, output_dir: Path, key: str):
    fig.savefig(output_dir / f"{key}.pdf", bbox_inches="tight", pad_inches=0.08,
                metadata={"Creator": "Komorebi reproducible figures.py",
                          "CreationDate": None, "ModDate": None})
    fig.savefig(output_dir / f"{key}.png", dpi=220, bbox_inches="tight", pad_inches=0.08,
                metadata={"Software": "Komorebi reproducible figures.py"})
    plt.close(fig)


def build_collatz_data() -> tuple[dict, list[dict], list[str]]:
    rows = orbit(27)
    first = next(row for row in rows[1:] if row["x"] < 27)
    assert (first["k"], first["x"], first["S"], first["C"]) == (
        37, 23, 59, 1100931843921811423)
    assert rows[2]["x"] == 31 and rows[1]["x"] == 41
    identity_checks = 0
    first_descent_examples = []
    for initial in (3, 7, 27, 41, 63, 127):
        sample = orbit(initial)
        for row in sample:
            ratio = Fraction(row["x"], initial)
            assert ratio == Fraction(row["p"], 1 << row["S"]) + Fraction(
                row["C"], (1 << row["S"]) * initial)
            inequality = row["C"] < ((1 << row["S"]) - row["p"]) * initial
            assert inequality == (row["x"] < initial)
            identity_checks += 1
        found = next(row for row in sample[1:] if row["x"] < initial)
        first_descent_examples.append({"initial": initial, **found})
    word_checks, cylinder_rows = 0, []
    for length in range(1, 5):
        for word in itertools.product(range(1, 4), repeat=length):
            residue, modulus = word_residue(word)
            members = 0
            for n in range(1, 4096, 2):
                x, actual = n, []
                for _ in word:
                    x, valuation = odd_step(x)
                    actual.append(valuation)
                present = tuple(actual) == word
                assert present == (n % modulus == residue)
                if present:
                    power, offset, exponent = word_affine(word)
                    assert power * n + offset == x * (1 << exponent)
                    members += 1
                word_checks += 1
            cylinder_rows.append({"word": list(word), "residue": residue,
                                  "modulus": modulus, "tested_members": members})
    tree = []
    for second in (1, 2, 3):
        residue, modulus = word_residue((1, second))
        tree.append({"second_exponent": second, "residue": residue, "modulus": modulus})
    tail_residue, tail_modulus = 3, 32
    for n in range(3, 4096, 4):
        x, first_r = odd_step(n)
        _, second_r = odd_step(x)
        assert first_r == 1
        assert (second_r >= 4) == (n % tail_modulus == tail_residue)
    for row in rows:
        row["multiplicative_ratio"] = fraction_text(Fraction(row["p"], 1 << row["S"]))
        row["additive_ratio"] = fraction_text(Fraction(row["C"], (1 << row["S"]) * 27))
        row["total_ratio"] = fraction_text(Fraction(row["x"], 27))
    return ({"convention": "A(n)=(3n+1)/2^v2(3n+1), n positive odd",
             "orbit27": rows, "first_descent27": first,
             "first_descent_examples": first_descent_examples,
             "exact_affine_checks": identity_checks,
             "cylinder_checks": word_checks, "cylinders": cylinder_rows,
             "tree": tree,
             "historical_coverage": {"modulus": 4096, "odd_classes": 2048,
                                      "covered": 1804, "unresolved": 244,
                                      "provenance": "Saved release count supplied by manuscript team; not replayed by this script"}},
            rows, [f"{identity_checks} exact iterate and descent-inequality checks passed",
                   f"{word_checks} exact word/cylinder membership checks passed",
                   "n=27: first source descent at odd step 37, x=23, S=59; intermediate 31 follows 41 but exceeds 27",
                   "The r2>=4 tail of the r1=1 branch was checked on every representative n<=4095"])


def plot_collatz(output_dir, rows, data):
    k = [row["k"] for row in rows]
    values = [row["x"] for row in rows]
    first = data["first_descent27"]
    fig, ax = plt.subplots(figsize=(6.7, 3.35), layout="constrained")
    ax.plot(k, values, color=BLUE, linewidth=1.6, marker="o", markersize=2.8)
    ax.axhline(27, color=GRAY, linewidth=0.9, linestyle="--", label="Initial value 27")
    ax.scatter([first["k"]], [first["x"]], color=COPPER, s=38, zorder=4,
               label="First descent below 27")
    ax.annotate("Step 37: 23 < 27", (first["k"], first["x"]),
                xytext=(23, 4.4), textcoords="data",
                arrowprops={"arrowstyle": "-", "color": COPPER, "lw": .8},
                color=COPPER, fontsize=9)
    ax.set(yscale="log", xlabel="Accelerated odd step k", ylabel=r"$A^k(27)$ (log scale)",
           title="The odd orbit of 27")
    ax.set_xlim(-.8, k[-1] + .8)
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    style_axes(ax)
    save_figure(fig, output_dir, "collatz_orbit27")

    multiplier = [float(Fraction(row["multiplicative_ratio"])) for row in rows]
    offset = [float(Fraction(row["additive_ratio"])) if row["k"] else np.nan for row in rows]
    total = [row["x"] / 27 for row in rows]
    fig, ax = plt.subplots(figsize=(6.7, 3.65), layout="constrained")
    ax.plot(k, total, color=CHARCOAL, linewidth=1.5, label=r"Total $A^k(27)/27$")
    ax.plot(k, multiplier, color=BLUE, linewidth=1.3, label=r"Multiplicative term $3^k/2^{S_k}$")
    ax.plot(k, offset, color=COPPER, linewidth=1.3, label=r"Additive term $C_k/(27\cdot2^{S_k})$")
    ax.axhline(1, color=GRAY, linewidth=1, linestyle="--")
    ax.axvline(first["k"], color=TEAL, linewidth=.9, linestyle=":")
    ax.text(first["k"] - .7, .0014, "First source descent", rotation=90,
            va="bottom", ha="right", color=TEAL, fontsize=8)
    ax.set(yscale="log", xlabel="Accelerated odd step k", ylabel="Contribution relative to 27 (log scale)",
           title="The two contributions to the affine orbit")
    ax.set_xlim(-.8, k[-1] + .8)
    ax.set_ylim(.001, max(total) * 2)
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    style_axes(ax)
    save_figure(fig, output_dir, "collatz_affine27")

    fig, ax = plt.subplots(figsize=(6.7, 2.25), layout="constrained")
    ax.barh([.55], [1804], height=.28, color=BLUE)
    ax.barh([.55], [244], left=[1804], height=.28, color=COPPER)
    ax.text(902, .55, "1,804 covered", ha="center", va="center", color="white", fontsize=11)
    ax.annotate("244 unresolved", xy=(1926, .7), xytext=(2048, 1.03),
                ha="right", va="center", color=COPPER, fontsize=10,
                arrowprops={"arrowstyle": "-", "color": COPPER, "lw": .8})
    ax.text(0, .06, "2,048 odd residue classes modulo 4,096", fontsize=10, va="bottom")
    ax.text(0, -.20, "Historical release counts. The underlying certificate is not replayed here.",
            fontsize=8, color=GRAY, va="bottom")
    ax.set_title("The recorded finite certificate coverage", loc="left", pad=9)
    ax.set(xlim=(0, 2048), ylim=(-.25, 1.15))
    ax.axis("off")
    save_figure(fig, output_dir, "collatz_coverage")

    fig, ax = plt.subplots(figsize=(6.7, 3.6), layout="constrained")
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    ax.set_title("Refining one exact valuation cylinder", loc="left", pad=10)
    nodes = [(0.51, .87, "$r_2=1$", r"$n\equiv7\ (\mathrm{mod}\ 8)$"),
             (0.51, .65, "$r_2=2$", r"$n\equiv11\ (\mathrm{mod}\ 16)$"),
             (0.51, .43, "$r_2=3$", r"$n\equiv19\ (\mathrm{mod}\ 32)$"),
             (0.51, .21, r"$r_2\geq4$", r"$n\equiv3\ (\mathrm{mod}\ 32)$")]
    root_box = FancyBboxPatch((.025, .43), .28, .24, boxstyle="round,pad=.012",
                             linewidth=.8, edgecolor=BLUE, facecolor="#F2F6F8")
    ax.add_patch(root_box)
    ax.text(.165, .59, "$r_1=1$", ha="center", va="center", color=BLUE)
    ax.text(.165, .50, r"$n\equiv3\ (\mathrm{mod}\ 4)$", ha="center", va="center", color=BLUE)
    for x, y, exponent_text, residue_text in nodes:
        ax.add_patch(FancyArrowPatch((.32, .55), (x - .018, y), arrowstyle="->",
                                    mutation_scale=8, lw=.8, color=GRAY,
                                    connectionstyle="arc3,rad=0"))
        ax.add_patch(FancyBboxPatch((x, y - .074), .43, .15, boxstyle="round,pad=.012",
                                   linewidth=.65, edgecolor=TEAL, facecolor="#F3F7F6"))
        ax.text(x + .10, y, exponent_text, ha="center", va="center", fontsize=10)
        ax.text(x + .29, y, residue_text, ha="center", va="center", fontsize=10)
    ax.text(.025, .027, "One branch only. The tail records a larger valuation, not unresolved dynamics.",
            fontsize=8, color=GRAY, va="bottom")
    save_figure(fig, output_dir, "collatz_residue_tree")


def build_rh_data():
    mp.mp.dps = 50
    denominator = xi(mp.mpf(".5"))
    t_values = [mp.mpf(k) / 20 for k in range(701)]
    values = [xi(mp.mpf(".5") + 1j * t) / denominator for t in t_values]
    assert max(abs(mp.im(value)) for value in values) < mp.mpf("1e-45")
    # The direct formula agrees with a real Hardy-Z evaluation at selected points.
    benchmark_t = [mp.mpf(str(t)) for t in (0, .5, 5, 10, 14.1, 14.2, 20, 30, 35)]
    alternate_errors = [abs(xi(mp.mpf(".5") + 1j * t) - xi_real_alternative(t)) for t in benchmark_t]
    assert max(alternate_errors) < mp.mpf("1e-45")
    base_values = [xi(mp.mpf(".5") + 1j * t) for t in benchmark_t]
    with mp.workdps(75):
        refined_errors = [abs(base - xi(mp.mpf(".5") + 1j * t))
                          for base, t in zip(base_values, benchmark_t)]
        assert max(refined_errors) < mp.mpf("1e-45")
        symmetry_errors = [abs(xi(s) - xi(1 - s)) for s in
                           (mp.mpf(".25") + 3j, mp.mpf(".7") + 10j, mp.mpf(".5") + 30j)]
        assert max(symmetry_errors) < mp.mpf("1e-65")
    x = np.linspace(-10, 10, 8001)
    basis = []
    for k in range(4):
        coefficients = np.zeros(k + 1)
        coefficients[k] = 1
        basis.append(np.polynomial.hermite.hermval(x, coefficients) * np.exp(-x * x / 2) /
                     math.sqrt((2 ** k) * math.factorial(k) * math.sqrt(math.pi)))
    gram = [[float(np.trapezoid(left * right, x)) for right in basis] for left in basis]
    gram_error = float(np.max(np.abs(np.array(gram) - np.eye(4))))
    assert gram_error < 1e-12
    return {"xi": {"definition": "xi(s)=s(s-1)*pi^(-s/2)*Gamma(s/2)*zeta(s)/2",
                   "normalization": mp.nstr(denominator, 50),
                   "lower_panel_compensation": "exp(pi*t/4), evaluated in binary64 from the same normalized xi samples",
                   "t_grid": [float(t) for t in t_values],
                   "normalized_values": [mp.nstr(mp.re(z), 50) for z in values],
                   "decimal_precision": 50, "refined_decimal_precision": 75,
                   "control_points": [float(t) for t in benchmark_t],
                   "max_hardy_z_absolute_discrepancy": mp.nstr(max(alternate_errors), 12),
                   "max_precision_absolute_discrepancy": mp.nstr(max(refined_errors), 12),
                   "max_functional_equation_absolute_discrepancy": mp.nstr(max(symmetry_errors), 12)},
            "barrier": {"definition": "M^(-1) and M^(-3/2), with common arbitrary unit normalization",
                        "bounds": [1, 1000000], "kind": "schematic, no Mobius data"},
            "heatfront": {"definition": "exp(delta*u), omitting the fixed exp(t*z^2) multiplier",
                          "deltas": [0, .1, .25], "u_bounds": [0, 20],
                          "kind": "hypothetical isolated-mode envelope, no sampled off-line zero"},
            "hermite": {"definition": "H_k(x)*exp(-x^2/2)/sqrt(2^k*k!*sqrt(pi)), physicists' H_k",
                        "orders": [0, 1, 2, 3], "plot_x_bounds": [-4, 4],
                        "gram_check_bounds": [-10, 10], "gram_check_grid_points": 8001,
                        "finite_trapezoid_gram": gram, "max_gram_error": gram_error,
                        "kind": "example normalized basis, no claim of heat-packet compression"}}, [
            "701 critical-line xi evaluations passed the realness tolerance 1e-45 at 50 decimal digits",
            "Nine Hardy-Z cross-checks and nine 75-digit recomputations passed absolute tolerance 1e-45",
            "Three functional-equation controls passed absolute tolerance 1e-65 at 75 decimal digits",
            "First four Hermite functions passed a finite trapezoid Gram check to 1e-12 on 8,001 points"]


def plot_rh(output_dir, data):
    t = np.array(data["xi"]["t_grid"])
    y = np.array([float(value) for value in data["xi"]["normalized_values"]])
    fig, axes = plt.subplots(2, 1, figsize=(6.7, 4.5), layout="constrained",
                             gridspec_kw={"height_ratios": [1, 1.2]})
    axes[0].plot(t[t <= 12], y[t <= 12], color=BLUE, lw=1.6)
    axes[0].set(xlabel="Height t", ylabel=r"$\xi(\frac{1}{2}+it)/\xi(\frac{1}{2})$",
                title="A finite view of the completed zeta function", xlim=(0, 12), ylim=(-.02, 1.03))
    compensation = np.exp(np.pi * t / 4)
    axes[1].plot(t, compensation * y, color=TEAL, lw=1.4)
    axes[1].axhline(0, color=GRAY, lw=.7)
    axes[1].set(xlabel="Height t", ylabel=r"$e^{\pi t/4}\xi(\frac{1}{2}+it)/\xi(\frac{1}{2})$", xlim=(0, 35))
    axes[1].set_title("Exponential compensation exposes the finite oscillations",
                      loc="left", fontsize=9, color=GRAY, pad=6)
    for ax in axes:
        style_axes(ax)
    save_figure(fig, output_dir, "rh_xi")

    m = np.logspace(0, 6, 301)
    fig, ax = plt.subplots(figsize=(6.7, 3.35), layout="constrained")
    ax.loglog(m, m ** -1, color=BLUE, lw=1.6, label=r"Barrier-rate model $M^{-1}$")
    ax.loglog(m, m ** -1.5, color=COPPER, lw=1.6, label=r"Target-rate model $M^{-3/2}$")
    ax.set(xlabel="Index M (log scale)", ylabel="Schematic magnitude (log scale)",
           title="Two rates separated by the parity barrier")
    ax.text(.03, .045, "Schematic curves with a common unit normalization. No Möbius measurements.",
            transform=ax.transAxes, color=GRAY, fontsize=8)
    ax.legend(frameon=False, fontsize=9)
    style_axes(ax)
    save_figure(fig, output_dir, "rh_barrier")

    u = np.linspace(0, 20, 401)
    fig, ax = plt.subplots(figsize=(6.7, 3.35), layout="constrained")
    for delta, color in ((0, CHARCOAL), (.1, TEAL), (.25, COPPER)):
        ax.plot(u, np.exp(delta * u), color=color, lw=1.6,
                label=rf"$\delta={delta:g}$")
    ax.set(yscale="log", xlabel="Front coordinate u", ylabel=r"Amplitude envelope $e^{\delta u}$ (log scale)",
           title="Hypothetical displacement from the critical line")
    ax.text(.03, .94, r"$\delta=\operatorname{Re}(\rho)-\frac{1}{2}$; fixed heat multiplier omitted",
            transform=ax.transAxes, va="top", color=GRAY, fontsize=8)
    ax.text(0, -.27, "Isolated-mode models. These curves are not observed zero packets.",
            transform=ax.transAxes, color=GRAY, fontsize=8)
    ax.legend(frameon=False, loc="center right", fontsize=9)
    style_axes(ax)
    save_figure(fig, output_dir, "rh_heatfront")

    x = np.linspace(-4, 4, 801)
    fig, ax = plt.subplots(figsize=(6.7, 3.55), layout="constrained")
    for k, color in enumerate((CHARCOAL, BLUE, TEAL, COPPER)):
        coefficients = np.zeros(k + 1)
        coefficients[k] = 1
        function = (np.polynomial.hermite.hermval(x, coefficients) * np.exp(-x * x / 2) /
                    math.sqrt((2 ** k) * math.factorial(k) * math.sqrt(math.pi)))
        ax.plot(x, function, color=color, lw=1.5, label=rf"$h_{k}$")
    ax.axhline(0, color=GRAY, linewidth=.7)
    ax.set(xlabel="Normalized coordinate x", ylabel=r"$h_k(x)$",
           title="The first four normalized Hermite functions", xlim=(-4, 4), ylim=(-.75, .95))
    ax.text(0, -.27, "An example orthonormal basis. No packet approximation is asserted.",
            transform=ax.transAxes, color=GRAY, fontsize=8)
    ax.legend(frameon=False, fontsize=9, ncols=4, loc="upper right")
    style_axes(ax)
    save_figure(fig, output_dir, "rh_hermite")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "figures")
    parser.add_argument("--environment-note", default="")
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    clock = time.perf_counter()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_style()
    collatz, rows, collatz_checks = build_collatz_data()
    rh, rh_checks = build_rh_data()
    plot_collatz(output_dir, rows, collatz)
    plot_rh(output_dir, rh)
    data = {"collatz": collatz, "riemann": rh}
    (output_dir / "data.json").write_text(json.dumps(data, indent=2) + "\n")
    (output_dir / "requirements.txt").write_text(
        "# Exact versions used for this reproduction\n"
        f"numpy=={np.__version__}\nmatplotlib=={matplotlib.__version__}\nmpmath=={mp.__version__}\n")
    keys = ["collatz_orbit27", "collatz_affine27", "collatz_coverage", "collatz_residue_tree",
            "rh_xi", "rh_barrier", "rh_heatfront", "rh_hermite"]
    all_checks = collatz_checks + rh_checks
    duration = time.perf_counter() - clock
    report_dir = Path(__file__).resolve().parent
    project_root = report_dir.parent
    report = {
        "schema_version": 1,
        "claim_id": "KOMOREBI-CONJECTURE-FIGURES-2026-10-08",
        "repository": {"commit": "unversioned publication working directory", "dirty": True},
        "command": " ".join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
        "environment": {"software": [{"name": "Python", "version": platform.python_version()},
                                        {"name": "NumPy", "version": np.__version__},
                                        {"name": "Matplotlib", "version": matplotlib.__version__},
                                        {"name": "mpmath", "version": mp.__version__}],
                        "hardware": f"{platform.machine()} / {platform.platform()}",
                        "mpmath_module": str(Path(mp.__file__).resolve()),
                        "environment_note": args.environment_note},
        "mathematics": {
            "assertion_tested": "Finite Collatz iterate/cylinder identities and numerical xi/Hermite consistency controls",
            "coefficient_domain": "Exact Python integers and Fraction for Collatz; mpmath 50/75 decimal floating arithmetic for xi; binary64 for plotting and Hermite quadrature",
            "conventions": "Accelerated odd map A; S cumulative 2-adic valuation; C affine offset; standard xi and physicists' Hermite polynomials",
            "inputs": ["shared/figures.py", "Historical declared coverage counts1804/244, not replayed"],
            "bounds": {"orbit_seeds": [3, 7, 27, 41, 63, 127], "orbit_max_steps": 512,
                       "cylinder_word_lengths": [1, 4], "cylinder_letters": [1, 3],
                       "cylinder_odd_inputs": [1, 4095], "xi_t_bounds": [0, 35],
                       "xi_grid_points": 701, "xi_control_points": 9,
                       "hermite_orders": [0, 3], "hermite_gram_grid_points": 8001,
                       "hermite_gram_bounds": [-10, 10]},
            "non_claims": ["No universal Collatz descent or complete arithmetic progression cover is proved",
                           "Historical coverage counts are not independently replayed here",
                           "No proof of RH, exhaustive zero test, or certified interval evaluation is asserted",
                           "Barrier and heat-front panels are schematic models, not arithmetic observations",
                           "Hermite basis illustration does not verify any heat-packet compression"]},
        "randomness": {"used": False, "generator": "none", "seed": None},
        "run": {"started_at": started, "runtime_seconds": round(duration, 3), "exit_status": 0},
        "checks": all_checks,
        "result": "Exact finite Collatz assertions passed; numerical controls passed at the stated tolerances; eight figures generated",
        "residual_risks": ["mpmath numerical evaluations are not rigorous interval bounds",
                           "Finite tests and numerical controls do not establish universal conjectures",
                           "Historical certificate replay belongs to the source archive audit",
                           "Pixel and PDF reproduction can differ with library/font versions"],
        "execution_input_sha256": sha256(Path(__file__).resolve()),
        "figure_keys": keys,
        "outputs": []}
    md = "# Computation and figure report\n\n" + (
        "The exact Collatz computations verify the accelerated orbit examples and bounded cylinder checks. "
        "The xi and Hermite computations pass numerical consistency controls. Two RH panels are schematic.\n\n")
    md += "## Contract\n\n"
    md += "* Collatz: six odd starting values, a 512-step cap, exact integer/Fraction arithmetic.\n"
    md += "* Cylinder check: all 120 words of length 1–4 over exponents 1–3, tested against every odd n from 1 to 4,095.\n"
    md += "* Xi: 701 points from t=0 to 35 at 50 decimal digits, with nine 75-digit and Hardy-Z controls.\n"
    md += "* Hermite: orders 0–3, finite trapezoid Gram check on 8,001 points in [-10,10].\n"
    md += "* Saved coverage input: 1,804 covered and 244 unresolved among 2,048 odd classes modulo 4,096. This count was not replayed.\n\n"
    md += "## Results\n\n" + "\n".join(f"* {item}." for item in all_checks) + "\n\n"
    md += "The first descent of 27 occurs at accelerated step 37, with x=23, S=59, and C=1100931843921811423. "
    md += "At step 2, 31 is below the preceding 41 but above the source 27.\n\n"
    md += "## Reproduction\n\n"
    md += "Install the exact versions in figures/requirements.txt, then run:\n\n```bash\npython shared/figures.py\n```\n\n"
    md += f"Tested interpreter: Python {platform.python_version()}. Matplotlib {matplotlib.__version__}, NumPy {np.__version__}, mpmath {mp.__version__}.\n\n"
    if args.environment_note:
        md += f"Execution environment note: {args.environment_note}\n\n"
    md += "Numerical xi values are not interval certificates. The finite Collatz checks do not establish universal descent. "
    md += "The barrier-rate curves use a common unit normalization. The heat-front curves model isolated amplitude envelopes "
    md += "exp(delta*u), omitting the fixed heat multiplier, and do not represent observed off-line zeros. "
    md += "The Hermite functions illustrate a basis only.\n\n"
    md += f"Generated eight vector PDF figures and eight 220-dpi PNG counterparts in {duration:.2f} seconds. "
    md += "Exact rational orbit data, numerical xi samples, and control outputs are in figures/data.json.\n"
    md_path = report_dir / "COMPUTATION_REPORT.md"
    md_path.write_text(md)
    files = [output_dir / f"{key}.{extension}" for key in keys for extension in ("pdf", "png")]
    files.extend([output_dir / "data.json", output_dir / "requirements.txt", md_path])
    report["outputs"] = [{"path": str(path.relative_to(project_root)), "sha256": sha256(path)} for path in files]
    (report_dir / "COMPUTATION_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "passed", "figures": len(keys), "plot_files": 2 * len(keys),
                      "data": str(output_dir / "data.json"), "runtime_seconds": round(duration, 3)}))


if __name__ == "__main__":
    main()
