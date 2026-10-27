from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mpmath as mp
import numpy as np
import sympy as sp


PI = math.pi
COLORS = {
    "ink": "#1C2730",
    "blue": "#2E6F9E",
    "teal": "#2A8C82",
    "orange": "#D88745",
    "magenta": "#9B4F83",
    "red": "#C95C54",
    "muted": "#66727C",
    "paper": "#FAFAF7",
    "grid": "#D4D9DD",
}


@dataclass(frozen=True)
class ContactData:
    c: int
    factors: dict[int, int]
    radical: int
    powerful_part: int
    exponent_gcd: int
    global_kernel: int
    global_image: int
    local_kernel_bound: int
    witt_length: int


def exact_int(value: object, name: str = "value") -> int:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not bool")
    try:
        result = int(value)
    except Exception as exc:
        raise TypeError(f"{name} must be integer-like") from exc
    if result != value:
        raise ValueError(f"{name} must be integral")
    return result


def factor_integer(n: int) -> dict[int, int]:
    n = exact_int(n, "n")
    if n <= 0:
        raise ValueError("n must be positive")
    return {int(p): int(e) for p, e in sp.factorint(n).items()}


def radical_from_factors(factors: dict[int, int]) -> int:
    result = 1
    for prime in factors:
        result *= prime
    return result


def vp(n: int, p: int) -> int:
    n = abs(exact_int(n, "n"))
    p = exact_int(p, "p")
    count = 0
    while n and n % p == 0:
        n //= p
        count += 1
    return count


def contact_data(c: int) -> ContactData:
    c = exact_int(c, "c")
    factors = factor_integer(c)
    radical = radical_from_factors(factors)
    powerful = c // radical
    exponents = list(factors.values())
    exponent_gcd = 0
    for exponent in exponents:
        exponent_gcd = math.gcd(exponent_gcd, exponent)
    global_kernel = math.gcd(powerful, exponent_gcd)
    global_image = powerful // global_kernel
    local_kernel_bound = 1
    for prime, exponent in factors.items():
        local_kernel_bound *= prime ** min(vp(exponent, prime), max(exponent - 1, 0))
    witt_length = sum(max(exponent - 1, 0) for exponent in exponents)
    return ContactData(
        c=c,
        factors=factors,
        radical=radical,
        powerful_part=powerful,
        exponent_gcd=exponent_gcd,
        global_kernel=global_kernel,
        global_image=global_image,
        local_kernel_bound=local_kernel_bound,
        witt_length=witt_length,
    )


def kummer_kernel_bruteforce(c: int) -> int:
    data = contact_data(c)
    m = data.powerful_part
    if m == 1:
        return 1
    exponents = list(data.factors.values())
    kernel = 0
    for k in range(m):
        if all((k * exponent) % m == 0 for exponent in exponents):
            kernel += 1
    return kernel


def local_contact_kernel(prime: int, exponent: int) -> int:
    if exponent <= 1:
        return 1
    return prime ** min(vp(exponent, prime), exponent - 1)


def fermat_height_compression(a: int, b: int, c: int) -> dict[str, float | int]:
    if a + b != c:
        raise ValueError("a+b must equal c")
    data = contact_data(c)
    m = data.powerful_part
    log_c = math.log(c)
    if m == 1:
        point_height = log_c
        canonical_scale = 0.0
    else:
        point_height = log_c / m
        canonical_scale = max(m - 3, 0) * point_height
    return {
        "M": m,
        "projective_height": point_height,
        "canonical_plane_curve_scale": canonical_scale,
        "height_ratio": point_height / log_c,
        "canonical_ratio": canonical_scale / log_c,
    }


def fermat_point_residual(a: int, b: int, c: int) -> float:
    data = contact_data(c)
    m = max(data.powerful_part, 1)
    with mp.workdps(100):
        aa = mp.mpf(a) / mp.mpf(c)
        bb = mp.mpf(b) / mp.mpf(c)
        u = mp.e ** (mp.log(aa) / m)
        v = mp.e ** (mp.log(bb) / m)
        return float(abs(u**m + v**m - 1))


def character_orthogonality(M: int) -> float:
    M = exact_int(M, "M")
    root = np.exp(2j * np.pi / M)
    maximum = 0.0
    for r in range(M):
        for s in range(M):
            total = sum(root ** ((r - s) * k) for k in range(M)) / M
            expected = 1.0 if r == s else 0.0
            maximum = max(maximum, abs(total - expected))
    return float(maximum)


def character_amplitude_grid(a: int, b: int, c: int, M: int | None = None) -> np.ndarray:
    if M is None:
        M = max(contact_data(c).powerful_part, 2)
    M = exact_int(M, "M")
    r = np.arange(M, dtype=float)[:, None]
    s = np.arange(M, dtype=float)[None, :]
    return np.exp((r * math.log(a / c) + s * math.log(b / c)) / M)


def hecke_depth_distribution(ell: int, steps: int) -> tuple[np.ndarray, np.ndarray]:
    ell = exact_int(ell, "ell")
    steps = exact_int(steps, "steps")
    depths = []
    probabilities = []
    denominator = (ell + 1) ** steps
    for deep_count in range(steps + 1):
        shallow_count = steps - deep_count
        depth = ell ** (deep_count - shallow_count)
        multiplicity = math.comb(steps, deep_count) * ell**shallow_count
        depths.append(float(depth))
        probabilities.append(multiplicity / denominator)
    return np.asarray(depths), np.asarray(probabilities)


def hecke_moments(ell: int, steps: int) -> dict[str, float]:
    depths, probabilities = hecke_depth_distribution(ell, steps)
    mean = float(np.dot(depths, probabilities))
    mean_log = float(np.dot(np.log(depths), probabilities))
    second = float(np.dot(depths**2, probabilities))
    expected_log = -steps * (ell - 1) / (ell + 1) * math.log(ell)
    return {
        "mean": mean,
        "mean_log": mean_log,
        "expected_log": expected_log,
        "second_moment": second,
    }


def witt_carry_polynomials(prime: int) -> tuple[sp.Expr, sp.Expr]:
    p = exact_int(prime, "prime")
    a, b = sp.symbols("a b")
    c = a + b
    first = sp.expand((a**p + b**p - c**p) / p)
    second = sp.expand((a ** (p * p) + b ** (p * p) - c ** (p * p) - p * first**p) / (p * p))
    return sp.factor(first), sp.factor(second)


def load_triples(paths: Iterable[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[tuple[int, int, int]] = set()
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                a = int(row["a"])
                b = int(row["b"])
                c = int(row["c"])
                key = (a, b, c)
                if key in seen:
                    continue
                seen.add(key)
                rows.append({
                    "a": a,
                    "b": b,
                    "c": c,
                    "radical": int(row["radical"]),
                    "quality": float(row["quality"]),
                    "source": path.name,
                })
    return rows


def enrich_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    enriched: list[dict[str, object]] = []
    for row in rows:
        a = int(row["a"])
        b = int(row["b"])
        c = int(row["c"])
        data = contact_data(c)
        height = fermat_height_compression(a, b, c)
        record = dict(row)
        record.update({
            "c_radical": data.radical,
            "powerful_part_M": data.powerful_part,
            "exponent_gcd": data.exponent_gcd,
            "kummer_kernel": data.global_kernel,
            "kummer_image": data.global_image,
            "local_kernel_bound": data.local_kernel_bound,
            "witt_length": data.witt_length,
            "kernel_over_log2c": data.global_kernel / max(math.log2(c), 1.0),
            "occupancy_fraction": data.global_image / max(data.powerful_part, 1),
            "fermat_height": height["projective_height"],
            "fermat_height_ratio": height["height_ratio"],
            "canonical_ratio": height["canonical_ratio"],
            "fermat_residual": fermat_point_residual(a, b, c),
            "factorization_c": " ".join(f"{p}^{e}" for p, e in sorted(data.factors.items())),
        })
        enriched.append(record)
    return enriched


def save_csv(rows: list[dict[str, object]], path: Path) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def save_figure(fig: plt.Figure, output: Path, stem: str) -> None:
    fig.savefig(output / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(output / f"{stem}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def make_figures(rows: list[dict[str, object]], output: Path) -> list[str]:
    output.mkdir(parents=True, exist_ok=True)
    stems: list[str] = []

    fig, ax = plt.subplots(figsize=(12.5, 6.0))
    ax.axis("off")
    boxes = [
        (0.02, 0.58, 0.15, 0.22, "filtered contact\nJ_c", COLORS["blue"]),
        (0.22, 0.58, 0.15, 0.22, "Witt crystal\nW_{e_p-1}(F_p)", COLORS["teal"]),
        (0.42, 0.58, 0.15, 0.22, "Kummer packet\n[c]", COLORS["orange"]),
        (0.62, 0.58, 0.15, 0.22, "Fermat lift\n$u^M+v^M=1$", COLORS["magenta"]),
        (0.82, 0.58, 0.15, 0.22, "Jacobi bank\nP_{r,s}", COLORS["red"]),
    ]
    for x, y, w, h, label, color in boxes:
        patch = plt.Rectangle((x, y), w, h, transform=ax.transAxes, facecolor=color + "22", edgecolor=color, linewidth=2)
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, label, transform=ax.transAxes, ha="center", va="center", fontsize=10.5, weight="bold")
    for left, right in zip(boxes[:-1], boxes[1:]):
        ax.annotate("", xy=(right[0], 0.69), xytext=(left[0] + left[2], 0.69), xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->", lw=2, color=COLORS["ink"]))
    ax.text(0.5, 0.38, "The first three arrows are exact and nearly lossless.", transform=ax.transAxes, ha="center", fontsize=15, weight="bold")
    ax.text(0.5, 0.24, "The unresolved step is compressing the Fermat character bank into a low-complexity global channel without paying the height back.", transform=ax.transAxes, ha="center", fontsize=12, color=COLORS["muted"], wrap=True)
    ax.set_title("The carry-preserving route after Attack VIII", fontsize=20, weight="bold", pad=12)
    save_figure(fig, output, "01_witt_kummer_architecture")
    stems.append("01_witt_kummer_architecture")

    x = np.asarray([math.log10(max(int(r["powerful_part_M"]), 1)) for r in rows])
    y = np.asarray([math.log10(max(int(r["kummer_kernel"]), 1)) for r in rows])
    q = np.asarray([float(r["quality"]) for r in rows])
    fig, ax = plt.subplots(figsize=(11.5, 6.0))
    scatter = ax.scatter(x, y, c=q, cmap="viridis", s=24, alpha=0.75)
    ax.plot([0, max(x.max(), 1)], [0, max(x.max(), 1)], linestyle="--", color=COLORS["red"], label="kernel = source size")
    ax.set_xlabel(r"$\log_{10}(c/\operatorname{rad}(c))$")
    ax.set_ylabel(r"$\log_{10}|\ker \,\kappa_c|$")
    ax.set_title("Global Kummer occupancy loses only the common exponent divisor", weight="bold")
    ax.grid(alpha=0.18)
    ax.legend()
    fig.colorbar(scatter, ax=ax, label="abc quality")
    save_figure(fig, output, "02_kummer_kernel_corpus")
    stems.append("02_kummer_kernel_corpus")

    fractions = np.asarray([float(r["occupancy_fraction"]) for r in rows])
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    ax.hist(fractions, bins=np.linspace(0, 1, 41), color=COLORS["blue"], edgecolor=COLORS["ink"], alpha=0.85)
    ax.set_xlabel("fraction of the filtered contact packet retained")
    ax.set_ylabel("number of triples")
    ax.set_title("Near-injective global Kummer occupancy", weight="bold")
    ax.grid(axis="y", alpha=0.18)
    save_figure(fig, output, "03_occupancy_fraction")
    stems.append("03_occupancy_fraction")

    top = sorted(rows, key=lambda r: float(r["quality"]), reverse=True)[:20]
    labels = [str(int(r["c"])) for r in top]
    M = np.asarray([max(int(r["powerful_part_M"]), 1) for r in top], dtype=float)
    height_ratio = 1.0 / M
    canonical_ratio = np.asarray([float(r["canonical_ratio"]) for r in top])
    fig, ax = plt.subplots(figsize=(12.5, 6.0))
    positions = np.arange(len(top))
    ax.semilogy(positions, height_ratio, marker="o", color=COLORS["teal"], label="projective height after $M$th roots")
    ax.plot(positions, np.maximum(canonical_ratio, 1e-18), marker="s", color=COLORS["orange"], label="canonical plane-curve scale")
    ax.set_xticks(positions, labels, rotation=70, ha="right", fontsize=8)
    ax.set_ylabel("ratio to $\\log c$")
    ax.set_title("Root extraction compresses coordinates but the Fermat canonical degree restores the scale", weight="bold")
    ax.grid(alpha=0.18)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, output, "04_height_compression_payback")
    stems.append("04_height_compression_payback")

    example = next((r for r in rows if int(r["a"]) == 3 and int(r["c"]) == 128), None)
    if example is None:
        example = {"a": 3, "b": 125, "c": 128}
    a = int(example["a"])
    b = int(example["b"])
    c = int(example["c"])
    M_example = contact_data(c).powerful_part
    grid = character_amplitude_grid(a, b, c, M=M_example)
    fig, ax = plt.subplots(figsize=(8.3, 7.0))
    image = ax.imshow(np.log10(np.maximum(grid, 1e-300)), origin="lower", cmap="magma", aspect="auto")
    ax.set_xlabel("character index $s$")
    ax.set_ylabel("character index $r$")
    ax.set_title(f"Fermat character amplitudes for {a}+{b}={c}, M={M_example}", weight="bold")
    fig.colorbar(image, ax=ax, label=r"$\log_{10}|u^r v^s|$")
    save_figure(fig, output, "05_fermat_character_grid")
    stems.append("05_fermat_character_grid")

    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.7))
    for ax, ell in zip(axes, [2, 3, 5], strict=True):
        depths, probabilities = hecke_depth_distribution(ell, 7)
        ax.stem(np.log(depths) / math.log(ell), probabilities, basefmt=" ")
        ax.axvline(0, color=COLORS["muted"], lw=1)
        moments = hecke_moments(ell, 7)
        ax.set_title(f"$\\ell={ell}$, mean depth {moments['mean']:.3f}", weight="bold", fontsize=11)
        ax.set_xlabel(r"$\log_\ell(E_7/E_0)$")
        ax.grid(alpha=0.16)
    axes[0].set_ylabel("packet probability")
    fig.suptitle("Prime-to-contact Hecke refinement is a mean-preserving multiplicative cascade", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, output, "06_hecke_contact_cascade")
    stems.append("06_hecke_contact_cascade")

    steps = np.arange(1, 13)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0))
    for ell, color in zip([2, 3, 5], [COLORS["blue"], COLORS["teal"], COLORS["magenta"]], strict=True):
        means = [hecke_moments(ell, int(step))["mean"] for step in steps]
        logs = [hecke_moments(ell, int(step))["mean_log"] for step in steps]
        axes[0].plot(steps, means, marker="o", color=color, label=f"ell={ell}")
        axes[1].plot(steps, logs, marker="o", color=color, label=f"ell={ell}")
    axes[0].axhline(1, color=COLORS["ink"], linestyle="--")
    axes[0].set_title("linear contact mean is conserved", weight="bold")
    axes[0].set_ylabel("normalized mean depth")
    axes[1].set_title("typical log-depth drifts downward", weight="bold")
    axes[1].set_ylabel("mean log-depth")
    for ax in axes:
        ax.set_xlabel("Hecke refinement steps")
        ax.grid(alpha=0.18)
        ax.legend()
    fig.tight_layout()
    save_figure(fig, output, "07_hecke_mean_and_entropy")
    stems.append("07_hecke_mean_and_entropy")

    first2, second2 = witt_carry_polynomials(2)
    first3, second3 = witt_carry_polynomials(3)
    fig, ax = plt.subplots(figsize=(12.5, 5.8))
    ax.axis("off")
    text = (
        r"$p=2:$" + "\n" +
        rf"$C_1={sp.latex(first2)}$" + "\n" +
        rf"$C_2={sp.latex(second2)}$" + "\n\n" +
        r"$p=3:$" + "\n" +
        rf"$C_1={sp.latex(first3)}$" + "\n" +
        rf"$C_2={sp.latex(second3)}$"
    )
    ax.text(0.5, 0.55, text, ha="center", va="center", fontsize=18, color=COLORS["ink"])
    ax.text(0.5, 0.12, "The carry spectrum preserves the additive relation in higher Witt coordinates, but degree-normalized size remains at the original height scale.", ha="center", va="center", fontsize=12, color=COLORS["muted"], wrap=True)
    ax.set_title("First p-typical Witt carry packets", fontsize=20, weight="bold")
    save_figure(fig, output, "08_witt_carry_packets")
    stems.append("08_witt_carry_packets")

    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.axis("off")
    items = [
        (0.04, 0.62, 0.21, 0.22, "Solved", "global Kummer occupancy\nloss at most log2(c)", COLORS["teal"]),
        (0.30, 0.62, 0.21, 0.22, "Exact", "Fermat root lift\nheight divided by M", COLORS["blue"]),
        (0.56, 0.62, 0.18, 0.22, "Exact", "character DFT\nM^2 channels", COLORS["orange"]),
        (0.79, 0.62, 0.17, 0.22, "Open", "sparse Jacobi quotient\nlow synthesis cost", COLORS["red"]),
    ]
    for x, y, w, h, head, body, color in items:
        patch = plt.Rectangle((x, y), w, h, transform=ax.transAxes, facecolor=color + "20", edgecolor=color, linewidth=2)
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h * 0.72, head, transform=ax.transAxes, ha="center", va="center", fontsize=14, weight="bold", color=color)
        ax.text(x + w / 2, y + h * 0.36, body, transform=ax.transAxes, ha="center", va="center", fontsize=9.4)
    for left, right in zip(items[:-1], items[1:]):
        ax.annotate("", xy=(right[0], 0.73), xytext=(left[0] + left[2], 0.73), xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->", lw=2, color=COLORS["ink"]))
    ax.text(0.5, 0.37, "The full Fermat cover pays the height compression back through canonical degree.", transform=ax.transAxes, ha="center", fontsize=14, weight="bold")
    ax.text(0.5, 0.23, "The remaining escape requires a character quotient that retains the Kummer contact packet but has conductor, degree, and archimedean norm controlled by the radical.", transform=ax.transAxes, ha="center", fontsize=12, color=COLORS["muted"], wrap=True)
    ax.set_title("The corrected final barrier", fontsize=21, weight="bold")
    save_figure(fig, output, "09_final_barrier")
    stems.append("09_final_barrier")

    return stems


def build_results(rows: list[dict[str, object]]) -> dict[str, object]:
    kernels = [int(row["kummer_kernel"]) for row in rows]
    fractions = [float(row["occupancy_fraction"]) for row in rows]
    residuals = [float(row["fermat_residual"]) for row in rows]
    top = sorted(rows, key=lambda row: float(row["quality"]), reverse=True)[:20]
    return {
        "triple_count": len(rows),
        "max_kummer_kernel": max(kernels),
        "median_kummer_kernel": float(np.median(kernels)),
        "min_occupancy_fraction": min(fractions),
        "median_occupancy_fraction": float(np.median(fractions)),
        "max_fermat_identity_residual": max(residuals),
        "top20": [
            {
                "a": int(row["a"]),
                "b": int(row["b"]),
                "c": int(row["c"]),
                "quality": float(row["quality"]),
                "M": int(row["powerful_part_M"]),
                "kernel": int(row["kummer_kernel"]),
                "image": int(row["kummer_image"]),
                "height_ratio": float(row["fermat_height_ratio"]),
                "canonical_ratio": float(row["canonical_ratio"]),
            }
            for row in top
        ],
        "hecke_checks": {
            str(ell): {str(step): hecke_moments(ell, step) for step in [1, 2, 4, 8]}
            for ell in [2, 3, 5]
        },
        "character_orthogonality": {str(M): character_orthogonality(M) for M in range(2, 11)},
        "witt_carries": {
            "2": [str(expr) for expr in witt_carry_polynomials(2)],
            "3": [str(expr) for expr in witt_carry_polynomials(3)],
        },
    }


def run_tests(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    tests: list[dict[str, object]] = []

    def record(name: str, condition: bool, detail: object) -> None:
        tests.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    for c in [8, 9, 16, 27, 32, 64, 128, 625, 6561, 4375]:
        data = contact_data(c)
        if data.powerful_part <= 10000:
            brute = kummer_kernel_bruteforce(c)
            record(f"global-kernel-{c}", brute == data.global_kernel, {"formula": data.global_kernel, "brute": brute})

    for c in [128, 729, 4375, 6561, 59049]:
        data = contact_data(c)
        record(f"kernel-log-bound-{c}", data.global_kernel <= max(math.log2(c), 1), data.global_kernel)

    for M in range(2, 11):
        error = character_orthogonality(M)
        record(f"character-orthogonality-{M}", error < 1e-11, error)

    for ell in [2, 3, 5, 7]:
        for step in [1, 2, 5, 8]:
            moments = hecke_moments(ell, step)
            record(f"hecke-mean-{ell}-{step}", abs(moments["mean"] - 1.0) < 1e-12, moments["mean"])
            record(f"hecke-log-{ell}-{step}", abs(moments["mean_log"] - moments["expected_log"]) < 1e-12, moments)

    first2, second2 = witt_carry_polynomials(2)
    first3, second3 = witt_carry_polynomials(3)
    a, b = sp.symbols("a b")
    record("witt-carry-p2-first", sp.expand(first2 + a * b) == 0, first2)
    record("witt-carry-p2-second", sp.expand(second2 + a * b * (a + b) ** 2) == 0, second2)
    record("witt-carry-p3-first", sp.expand(first3 + a * b * (a + b)) == 0, first3)
    record("witt-carry-p3-second", sp.expand(second3 + a * b * (a + b) * (a * a + a * b + b * b) ** 3) == 0, second3)

    maximum_residual = max(float(row["fermat_residual"]) for row in rows)
    record("fermat-identities", maximum_residual < 2e-11, maximum_residual)
    record("all-global-kernels-sublog", all(int(row["kummer_kernel"]) <= max(math.log2(int(row["c"])), 1) for row in rows), max(int(row["kummer_kernel"]) for row in rows))
    record("occupancy-fraction-positive", all(float(row["occupancy_fraction"]) > 0 for row in rows), min(float(row["occupancy_fraction"]) for row in rows))
    return tests


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    base = args.base.resolve()
    source_data = base / "source_data"
    figures = base / "figures"
    tables = base / "tables"
    results_dir = base / "results"
    tables.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    paths = [source_data / "abc_hits_c10000.csv", source_data / "high_quality_c100000.csv", source_data / "leiden_top20.csv"]
    rows = enrich_rows(load_triples(paths))
    save_csv(rows, tables / "witt_kummer_corpus.csv")
    stems = make_figures(rows, figures)
    tests = run_tests(rows)
    results = build_results(rows)
    results["tests"] = tests
    results["tests_passed"] = sum(1 for test in tests if test["passed"])
    results["tests_total"] = len(tests)
    results["figure_pairs"] = len(stems)
    (results_dir / "attack_ix_results.json").write_text(json.dumps(results, indent=2, default=str) + "\n", encoding="utf-8")
    (results_dir / "tests.json").write_text(json.dumps(tests, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({
        "triples": len(rows),
        "tests": f"{results['tests_passed']}/{results['tests_total']}",
        "figure_pairs": len(stems),
        "max_kernel": results["max_kummer_kernel"],
        "median_occupancy_fraction": results["median_occupancy_fraction"],
    }, indent=2))


if __name__ == "__main__":
    main()
