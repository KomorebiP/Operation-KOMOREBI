"""Standalone figure: a weak intrinsic feedback tap and a growth-order jump.

SF-DISCOVERY-001. Uses only exact formula evaluation and Matplotlib.
The series coefficients use ordinary mpmath arithmetic at 90 decimal digits.
Analytic truncation is bounded separately by an exact rational Cauchy majorant.
"""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import platform
import sys

ROOT = Path(__file__).resolve().parent
DEPS = Path("/workspace/scratch/de82c13900d1/special_work/verification_dependencies")
if DEPS.is_dir():
    sys.path.insert(0, str(DEPS))

import mpmath as mp
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

mp.mp.dps = 90
LAST = 160
PARAMETERS = ("0", "0.001", "0.01", "0.1")
DISPLAY_RADIUS = Fraction(2)
CAUCHY_RADIUS = Fraction(3)
FIG = ROOT / "figures"
EVIDENCE = ROOT / "evidence"
FIG.mkdir(exist_ok=True)
EVIDENCE.mkdir(exist_ok=True)


def cauchy_bound(q, r, radius):
    # Copied, without importing its side effects, from build_figures.py.
    # Coefficient domination gives M(1) <= tan(1) < 2. For larger
    # radii use M(R) <= R[1+M(vR)^2], v=max(q,r).
    v = max(Fraction(str(q)), Fraction(str(r)))
    radius = Fraction(str(radius))
    radii = [radius]
    while radii[-1] > 1:
        radii.append(radii[-1] * v)
    bound = Fraction(2)
    for current in reversed(radii[:-1]):
        bound = current * (1 + bound * bound)
    return bound


def coefficients(epsilon, last=LAST):
    eps = mp.mpf(epsilon)
    q0, q1 = mp.mpf(1) / 4, mp.mpf(3) / 4
    out = [mp.mpf(1)]
    for n in range(1, last + 1):
        weight = (1 - eps) * q0 ** (2 * n) + eps * q1 ** (2 * n)
        out.append(weight * mp.fsum(out[i] * out[n - 1 - i]
                                    for i in range(n)) / (2 * n + 1))
    return out


def exact_coefficients(epsilon, last=8):
    eps = Fraction(epsilon)
    q0, q1 = Fraction(1, 4), Fraction(3, 4)
    out = [Fraction(1)]
    for n in range(1, last + 1):
        weight = (1 - eps) * q0 ** (2 * n) + eps * q1 ** (2 * n)
        out.append(weight * sum(out[i] * out[n - 1 - i]
                                for i in range(n)) / (2 * n + 1))
    return out


def evaluate(coeff, argument):
    z = mp.mpf(str(argument))
    return z * mp.polyval(list(reversed(coeff)), z * z)


def main():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.15,
        "pdf.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })
    bound = cauchy_bound("0.75", "0.75", CAUCHY_RADIUS)
    ratio = DISPLAY_RADIUS / CAUCHY_RADIUS
    first_omitted_power = 2 * (LAST + 1) + 1
    tail = bound * ratio ** first_omitted_power / (1 - ratio)
    assert tail < Fraction(1, 10 ** 40)

    argument_grid = np.linspace(0, 2, 241)
    colors = ("#475569", "#0f75bc", "#0d9488", "#d95f35")
    styles = ("-", "--", "-.", "-")
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.9))
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.21, top=0.77, wspace=0.30)
    fig.suptitle("A weak feedback tap changes global growth", y=0.97,
                 fontsize=16, fontweight="bold")
    fig.text(0.5, 0.87,
             r"$F_\varepsilon'=1+(1-\varepsilon)F_\varepsilon(z/4)^2"
             r"+\varepsilon F_\varepsilon(3z/4)^2,\quad F_\varepsilon(0)=0,"
             r"\quad 0\leq\varepsilon\leq1$",
             ha="center", fontsize=12.5)
    checks = 0
    curves = []
    for eps, color, style in zip(PARAMETERS, colors, styles):
        coeff = coefficients(eps)
        exact = exact_coefficients(eps)
        errors = []
        for actual, target in zip(coeff, exact):
            target_mp = mp.mpf(target.numerator) / target.denominator
            error = abs(actual - target_mp)
            assert error < mp.mpf("1e-85")
            errors.append(error)
            checks += 1
        values = [float(evaluate(coeff, z)) for z in argument_grid]
        axes[0].plot(argument_grid, values, color=color, ls=style, lw=2.1,
                     label=rf"$\varepsilon={eps}$")
        value_at_two = evaluate(coeff, 2)
        curves.append({
            "epsilon": eps,
            "last_n": LAST,
            "highest_included_power": 2 * LAST + 1,
            "sample_count": len(argument_grid),
            "display_argument": [0, 2],
            "coefficient_precision_decimal_digits": mp.mp.dps,
            "exact_crosscheck_coefficients_n": [0, 8],
            "max_exact_crosscheck_abs_error": mp.nstr(max(errors), 30),
            "f_at_two_numerical": mp.nstr(value_at_two, 45),
            "coefficient_text_sha256": hashlib.sha256(
                "|".join(mp.nstr(c, 90) for c in coeff).encode()).hexdigest(),
        })
    axes[0].set(xlabel="Real argument z", ylabel=r"$F_\varepsilon(z)$",
                title="Curves stay close on a bounded interval")
    axes[0].set_xlim(0, 2)
    axes[0].legend(title="Weak tap weight", fontsize=10, title_fontsize=10,
                   loc="upper left", frameon=False)

    order_zero = 0.5
    order_positive = float(mp.log(2) / mp.log(mp.mpf(4) / 3))
    axes[1].plot([0, 0.1], [order_positive, order_positive], color="#0f75bc",
                 lw=2.5, solid_capstyle="butt")
    axes[1].plot(0, order_positive, marker="o", ms=9, mfc="white",
                 mec="#0f75bc", mew=2, clip_on=False, zorder=4)
    axes[1].plot(0, order_zero, marker="o", ms=9, color="#d95f35",
                 clip_on=False, zorder=4)
    axes[1].annotate(r"$\log 2/\log(4/3)$ for every $\varepsilon>0$",
                     xy=(0.050, order_positive), xytext=(0.011, 2.70),
                     fontsize=10, color="#075985")
    axes[1].annotate(r"$1/2$ when the tap is removed",
                     xy=(0, order_zero), xytext=(0.011, 0.77),
                     fontsize=10, color="#9a3412",
                     arrowprops={"arrowstyle": "-", "color": "#d95f35", "lw": 1.1})
    axes[1].set(xlabel=r"Weak tap weight $\varepsilon$",
                ylabel="Entire growth order",
                title="The order jumps at tap removal",
                xlim=(0, 0.1), ylim=(0.25, 3.0))
    axes[1].set_xticks([0, 0.025, 0.05, 0.075, 0.1])
    axes[1].set_xticklabels(["0", "0.025", "0.05", "0.075", "0.1"])
    fig.text(0.075, 0.087,
             "Left: 90-digit series calculations, with an exact analytic truncation bound.",
             fontsize=9.5)
    fig.text(0.075, 0.043,
             "Right: the proved growth order. Compact convergence does not preserve this global invariant.",
             fontsize=9.5)
    for extension in ("pdf", "png"):
        kwargs = {"dpi": 200} if extension == "png" else {}
        fig.savefig(FIG / f"07_weak_tap.{extension}", bbox_inches="tight", **kwargs)
    plt.close(fig)

    record = {
        "checkpoint": "SF-DISCOVERY-001",
        "figure": "07_weak_tap",
        "contract": "Numerical display of weak-tap family on z in [0,2], with separately exact analytic tail bound and theoretical growth-order discontinuity.",
        "software": {
            "python": platform.python_version(), "mpmath": mp.__version__,
            "numpy": np.__version__, "matplotlib": matplotlib.__version__,
        },
        "arithmetic": "mpmath ordinary 90-digit arithmetic; fractions.Fraction exact Cauchy bound; not certified balls",
        "majorant": {
            "function": "f_(3/4), the known single-dilation family",
            "reason": "Coefficientwise domination of both positive feedback channels and their normalized mixtures.",
            "base_radius": "1", "base_M_upper": "2",
            "base_justification": "f_(3/4)(1)<=tan(1)<2; cos(1)>1/2 and sin(1)<1.",
            "recurrence": "M(R)<=R*(1+M((3/4)*R)^2)",
            "cauchy_radius": str(CAUCHY_RADIUS),
            "display_radius": str(DISPLAY_RADIUS),
            "Cauchy_M_upper_exact": str(bound),
            "Cauchy_M_upper_float": float(bound),
            "first_omitted_power": first_omitted_power,
            "analytic_tail_bound_exact": str(tail),
            "analytic_tail_bound_float": float(tail),
        },
        "ordinary_precision_crosschecks": checks,
        "curves": curves,
        "theoretical_order": {
            "parameter_domain": "0<=epsilon<=1",
            "epsilon_zero": "1/2",
            "epsilon_positive": "log(2)/log(4/3)",
            "epsilon_positive_decimal": mp.nstr(mp.log(2) / mp.log(mp.mpf(4) / 3), 45),
            "argument": "Maximum active channel order; zero-weight channel is removed.",
            "positive_weights_required": True,
        },
        "non_claims": [
            "The analytic truncation bound does not certify floating arithmetic roundoff.",
            "The plotted finite-argument curves do not measure or prove the asymptotic order.",
            "The order step is a theorem display, not a fitted empirical curve.",
            "No historical priority claim.",
        ],
    }
    for extension in ("pdf", "png"):
        path = FIG / f"07_weak_tap.{extension}"
        record.setdefault("output_sha256", {})[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (EVIDENCE / "tap_figure_computation.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({
        "figure": "07_weak_tap", "precision": mp.mp.dps,
        "analytic_tail_bound_float": float(tail),
        "ordinary_precision_crosschecks": checks,
        "f_at_2": {item["epsilon"]: item["f_at_two_numerical"] for item in curves},
        "positive_tap_order": record["theoretical_order"]["epsilon_positive_decimal"],
    }, indent=2))


if __name__ == "__main__":
    main()
