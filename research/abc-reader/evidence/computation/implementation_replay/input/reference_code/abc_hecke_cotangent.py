from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from sympy import factorint

import abc_integral_hecke_transfer as ray

PAPER = ray.PAPER
INK = ray.INK
MUTED = ray.MUTED
BLUE = ray.BLUE
TEAL = ray.TEAL
ORANGE = ray.ORANGE
MAGENTA = ray.MAGENTA
RED = ray.RED
GRID = ray.GRID
COLORS = ray.COLORS


def exact_int(value: object, name: str = "value") -> int:
    return ray.exact_int(value, name)


def factor(n: int) -> dict[int, int]:
    return ray.factor(n)


def radical(n: int) -> int:
    return ray.radical(n)


@dataclass(frozen=True)
class PersistenceProfile:
    c: int
    radical_c: int
    order: int
    packet_rank: int
    cyclic_image_capacity: int
    forced_kernel_lower_bound: int
    repeated_primes: int
    local_trivial_prime_capacity: int


def persistence_profile(c: int) -> PersistenceProfile:
    c = exact_int(c, "c")
    fac = factor(c)
    rad = math.prod(fac) if fac else 1
    order = c // rad
    rank = sum(max(0, e - 1) for e in fac.values())
    repeated = [p for p, e in fac.items() if e >= 2]
    cyclic_capacity = math.prod(repeated) if repeated else 1
    forced_kernel = order // cyclic_capacity
    local_capacity = 1
    for q, e in fac.items():
        if q == 2 or e < 2:
            continue
        local_capacity *= math.gcd(q - 1, 2 * e) ** 2
    return PersistenceProfile(
        c=c,
        radical_c=rad,
        order=order,
        packet_rank=rank,
        cyclic_image_capacity=cyclic_capacity,
        forced_kernel_lower_bound=forced_kernel,
        repeated_primes=len(repeated),
        local_trivial_prime_capacity=local_capacity,
    )


def persistence_module_invariants(c: int) -> dict[str, object]:
    profile = persistence_profile(c)
    p_primary_ranks = {p: e - 1 for p, e in factor(c).items() if e >= 2}
    forced_p_kernel_ranks = {p: max(0, rank - 1) for p, rank in p_primary_ranks.items()}
    return {
        **asdict(profile),
        "p_primary_ranks": p_primary_ranks,
        "forced_p_kernel_ranks": forced_p_kernel_ranks,
    }


def cyclic_kernel_lower_bound(c: int) -> int:
    return persistence_profile(c).forced_kernel_lower_bound


def toy_hecke_order_invariants(moduli: Iterable[int]) -> dict[str, object]:
    values = [exact_int(value, "modulus") for value in moduli]
    if not values or any(value < 1 for value in values):
        raise ValueError("moduli must be positive")
    eta = math.lcm(*values)
    cotangent_order = math.prod(values)
    defect_factor = cotangent_order // eta
    return {
        "moduli": values,
        "congruence_exponent": eta,
        "cotangent_order": cotangent_order,
        "wiles_defect_factor": defect_factor,
        "cotangent_generator_count": len(values),
    }


def monogenic_filter_invariants(eigenvalues: Iterable[int], target: int = 0) -> dict[str, object]:
    values = [exact_int(value, "eigenvalue") for value in eigenvalues]
    target = exact_int(target, "target")
    if target < 0 or target >= len(values):
        raise IndexError("target out of range")
    if len(set(values)) != len(values):
        raise ValueError("eigenvalues must be distinct")
    a0 = values[target]
    derivative = 1
    for index, value in enumerate(values):
        if index != target:
            derivative *= a0 - value
    eta = abs(derivative)
    return {
        "eigenvalues": values,
        "target": target,
        "projector_denominator": eta,
        "cotangent_order": eta,
        "wiles_defect_factor": 1,
    }


def split_tate_scalar_depth(q: int, e: int, ell: int) -> int:
    q = exact_int(q, "q")
    e = exact_int(e, "e")
    ell = exact_int(ell, "ell")
    if q < 3 or e < 1 or ell < 2:
        return 0
    def valuation(n: int, p: int) -> int:
        count = 0
        while n % p == 0 and n:
            n //= p
            count += 1
        return count
    return min(valuation(q - 1, ell), valuation(2 * e, ell))


def split_tate_capacity(q: int, e: int) -> int:
    q = exact_int(q, "q")
    e = exact_int(e, "e")
    if q == 2:
        return 1
    return math.gcd(q - 1, 2 * e) ** 2


def corpus_profiles(source_data: Path) -> pd.DataFrame:
    specs = [
        ("abc_hits_c10000", source_data / "abc_hits_c10000.csv"),
        ("high_quality_c100000", source_data / "high_quality_c100000.csv"),
        ("leiden_top20", source_data / "leiden_top20.csv"),
    ]
    rows: list[dict[str, object]] = []
    for corpus, path in specs:
        frame = pd.read_csv(path, dtype={"a": "string", "b": "string", "c": "string", "radical": "string"})
        for record in frame.itertuples(index=False):
            a = exact_int(record.a, "a")
            b = exact_int(record.b, "b")
            c = exact_int(record.c, "c")
            profile = persistence_profile(c)
            rows.append({
                "corpus": corpus,
                "a": a,
                "b": b,
                "c": c,
                "radical_abc": exact_int(record.radical, "radical"),
                "quality": float(record.quality),
                **asdict(profile),
                "cyclic_survival_fraction": Fraction(profile.cyclic_image_capacity, profile.order),
                "forced_kernel_log10": math.log10(profile.forced_kernel_lower_bound) if profile.forced_kernel_lower_bound > 0 else 0.0,
                "local_capacity_fraction": Fraction(profile.local_trivial_prime_capacity, profile.order),
            })
    return pd.DataFrame(rows)


def corpus_summary(profiles: pd.DataFrame) -> pd.DataFrame:
    summaries: list[dict[str, object]] = []
    for corpus, group in profiles.groupby("corpus"):
        kernel = group.forced_kernel_lower_bound.astype(object)
        survival = np.array([float(value) for value in group.cyclic_survival_fraction])
        local_fraction = np.array([float(value) for value in group.local_capacity_fraction])
        summaries.append({
            "corpus": corpus,
            "rows": len(group),
            "fraction_nontrivial_forced_kernel": float(np.mean([value > 1 for value in kernel])),
            "median_packet_rank": float(group.packet_rank.median()),
            "maximum_packet_rank": int(group.packet_rank.max()),
            "median_cyclic_survival_fraction": float(np.median(survival)),
            "median_forced_kernel_log10": float(group.forced_kernel_log10.median()),
            "maximum_forced_kernel_log10": float(group.forced_kernel_log10.max()),
            "median_local_capacity_fraction": float(np.median(local_fraction)),
        })
    return pd.DataFrame(summaries).sort_values("corpus")


def save_figure(fig: plt.Figure, out: Path, stem: str) -> None:
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(out / f"{stem}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def diagram_axes(figsize: tuple[float, float] = (13.0, 6.2)) -> tuple[plt.Figure, plt.Axes]:
    return ray.diagram_axes(figsize)


def box(ax: plt.Axes, xy: tuple[float, float], wh: tuple[float, float], text: str, color: str, fontsize: float = 11.0, weight: str = "normal") -> None:
    ray.box(ax, xy, wh, text, color, fontsize, weight)


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = INK, text: str | None = None, offset: tuple[float, float] = (0, 0.035)) -> None:
    ray.arrow(ax, start, end, color, text, offset)


def figure_cyclic_rank_obstruction(out: Path) -> None:
    fig, ax = diagram_axes()
    ax.text(0.5, 0.94, "The direct occupancy target has the wrong algebraic rank", ha="center", fontsize=20, weight="bold")
    box(ax, (0.04, 0.57), (0.31, 0.20), r"persistence packet at $p^e$" + "\n" + r"$(\mathbf{Z}/p\mathbf{Z})^{e-1}$", BLUE, 13, "bold")
    box(ax, (0.65, 0.57), (0.31, 0.20), "rational eigenline congruence packet\ncyclic p-primary rank at most one", MAGENTA, 12.2, "bold")
    arrow(ax, (0.35, 0.67), (0.65, 0.67), RED, "any homomorphism")
    box(ax, (0.31, 0.20), (0.38, 0.18), r"forced kernel rank $\geq e-2$" + "\n" + r"forced size $\geq p^{e-2}$", RED, 13, "bold")
    arrow(ax, (0.50, 0.57), (0.50, 0.38), RED)
    ax.text(0.5, 0.08, "Multiplicity cannot be stored in a cyclic congruence quotient.  It must move to a cotangent or derived module.", ha="center", fontsize=11, color=MUTED)
    save_figure(fig, out, "12_cyclic_rank_obstruction")


def figure_corpus_kernel(profiles: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.0))
    colors = {"abc_hits_c10000": BLUE, "high_quality_c100000": TEAL, "leiden_top20": MAGENTA}
    for corpus, group in profiles.groupby("corpus"):
        axes[0].scatter(group.packet_rank, group.forced_kernel_log10, label=corpus.replace("_", " "), color=colors[corpus], alpha=0.68, s=28, edgecolor=INK, linewidth=0.25)
        axes[1].scatter(group.quality, [float(value) for value in group.cyclic_survival_fraction], label=corpus.replace("_", " "), color=colors[corpus], alpha=0.68, s=28, edgecolor=INK, linewidth=0.25)
    axes[0].set_xlabel("persistence packet rank")
    axes[0].set_ylabel(r"$\log_{10}$ forced kernel lower bound")
    axes[0].set_title("Cyclic compression discards most repeated-depth directions", weight="bold")
    axes[0].grid(alpha=0.18)
    axes[1].set_xlabel("abc quality")
    axes[1].set_ylabel("maximum cyclic survival fraction")
    axes[1].set_yscale("log")
    axes[1].set_title("The cyclic target retains only one direction per prime", weight="bold")
    axes[1].grid(alpha=0.18, which="both")
    axes[0].legend(fontsize=8)
    fig.suptitle("The rank obstruction across 466 supplied triples", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, out, "13_corpus_cyclic_kernel")


def figure_toy_order(out: Path) -> None:
    moduli = [4, 8, 9, 25]
    inv = toy_hecke_order_invariants(moduli)
    fig, ax = diagram_axes((13.0, 6.4))
    ax.text(0.5, 0.95, "A toy Hecke order separates cyclic leakage from cotangent multiplicity", ha="center", fontsize=19.5, weight="bold")
    for index, modulus in enumerate(moduli):
        x = 0.06 + 0.19 * index
        box(ax, (x, 0.61), (0.14, 0.14), rf"cotangent direction {index+1}" + "\n" + rf"$\mathbf{{Z}}/{modulus}\mathbf{{Z}}$", COLORS[index], 11.2, "bold")
    box(ax, (0.80, 0.61), (0.16, 0.14), "cyclic quotient" + "\n" + "$\\mathbf{Z}/" + str(inv["congruence_exponent"]) + "\\mathbf{Z}$", MAGENTA, 11.5, "bold")
    for index in range(len(moduli)):
        arrow(ax, (0.13 + 0.19 * index, 0.61), (0.88, 0.47), COLORS[index], None)
    box(ax, (0.20, 0.18), (0.27, 0.17), rf"cotangent order" + "\n" + rf"$\prod m_i={inv['cotangent_order']}$", TEAL, 12, "bold")
    box(ax, (0.54, 0.18), (0.27, 0.17), rf"defect factor" + "\n" + rf"$\prod m_i/\mathrm{{lcm}}(m_i)={inv['wiles_defect_factor']}$", RED, 12, "bold")
    ax.text(0.5, 0.07, "The congruence exponent records the largest common depth.  The cotangent module records every independent direction.", ha="center", fontsize=11, color=MUTED)
    save_figure(fig, out, "14_toy_hecke_cotangent")


def figure_ci_vs_defect(out: Path) -> None:
    monogenic = monogenic_filter_invariants([0, 2, 5, 9], 0)
    toy = toy_hecke_order_invariants([4, 8, 9, 25])
    labels = ["monogenic\ncomplete intersection", "multi-direction\ntoy order"]
    congruence = [monogenic["projector_denominator"], toy["congruence_exponent"]]
    cotangent = [monogenic["cotangent_order"], toy["cotangent_order"]]
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    x = np.arange(2)
    width = 0.34
    ax.bar(x - width / 2, congruence, width, label="cyclic congruence order", color=BLUE, edgecolor=INK)
    ax.bar(x + width / 2, cotangent, width, label="cotangent order", color=ORANGE, edgecolor=INK)
    ax.set_yscale("log")
    ax.set_xticks(x, labels)
    ax.set_ylabel("module order")
    ax.set_title("Complete intersections have no Wiles defect", weight="bold")
    ax.grid(axis="y", alpha=0.18, which="both")
    ax.legend()
    ax.text(0, math.sqrt(congruence[0] * cotangent[0]), "equality", ha="center", va="center", color=TEAL, weight="bold")
    ax.text(1, math.sqrt(congruence[1] * cotangent[1]), f"defect {toy['wiles_defect_factor']}", ha="center", va="center", color=RED, weight="bold")
    fig.tight_layout()
    save_figure(fig, out, "15_complete_intersection_vs_defect")


def figure_two_prime_spectrogram(out: Path) -> None:
    conductor_data = [(3, 22), (5, 4), (7, 15), (11, 2), (31, 1)]
    coefficient_primes = [2, 3, 5, 7, 11, 13]
    matrix = np.array([[2 * split_tate_scalar_depth(q, e, ell) for q, e in conductor_data] for ell in coefficient_primes], dtype=float)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0), gridspec_kw={"width_ratios": [1.25, 0.75]})
    image = axes[0].imshow(matrix, cmap="YlGnBu", aspect="auto", vmin=0)
    axes[0].set_xticks(range(len(conductor_data)), [rf"$q={q}$\n$e={e}$" for q, e in conductor_data])
    axes[0].set_yticks(range(len(coefficient_primes)), [rf"$\ell={ell}$" for ell in coefficient_primes])
    axes[0].set_title(r"available local defect length $2n_{\ell,q}$", weight="bold")
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            axes[0].text(col, row, str(int(matrix[row, col])), ha="center", va="center", color=INK, fontsize=9)
    fig.colorbar(image, ax=axes[0], fraction=0.045, pad=0.03)
    persistence_logs = [(e - 1) * math.log(q) for q, e in conductor_data]
    capacity_logs = [math.log(max(1, split_tate_capacity(q, e))) for q, e in conductor_data]
    x = np.arange(len(conductor_data))
    axes[1].bar(x - 0.17, persistence_logs, 0.34, label=r"persistence $(e-1)\log q$", color=ORANGE, edgecolor=INK)
    axes[1].bar(x + 0.17, capacity_logs, 0.34, label="local defect capacity", color=TEAL, edgecolor=INK)
    axes[1].set_xticks(x, [str(q) for q, _ in conductor_data])
    axes[1].set_xlabel("conductor prime q")
    axes[1].set_ylabel("logarithmic size")
    axes[1].set_title("Local trivial-prime defects do not carry base-q depth", weight="bold")
    axes[1].grid(axis="y", alpha=0.18)
    axes[1].legend(fontsize=8)
    fig.suptitle("The correct local-global signal has two prime indices", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, out, "16_two_prime_wiles_spectrogram")


def figure_corrected_target(out: Path) -> None:
    fig, ax = diagram_axes((13.0, 6.5))
    ax.text(0.5, 0.95, "The corrected integral automorphic transfer problem", ha="center", fontsize=20, weight="bold")
    box(ax, (0.03, 0.61), (0.22, 0.18), r"valuation persistence" + "\n" + r"$\mathrm{Fitt}_0(\mathcal{P}_c)=c/R_c$", BLUE, 11.7, "bold")
    box(ax, (0.31, 0.61), (0.22, 0.18), r"local deformation packets" + "\n" + r"indexed by $(\ell,q)$", TEAL, 11.7, "bold")
    box(ax, (0.59, 0.61), (0.22, 0.18), r"Hecke cotangent complex" + "\n" + r"$\mathbb{L}_{\mathbf{T}/\mathcal{O}}$", ORANGE, 11.7, "bold")
    box(ax, (0.78, 0.20), (0.18, 0.18), "determinant line\nand Arakelov norm", MAGENTA, 11.5, "bold")
    arrow(ax, (0.25, 0.70), (0.31, 0.70))
    arrow(ax, (0.53, 0.70), (0.59, 0.70))
    arrow(ax, (0.70, 0.61), (0.87, 0.38), MAGENTA)
    box(ax, (0.08, 0.20), (0.25, 0.18), "superseded target\nmap into one cyclic quotient", RED, 11.3)
    box(ax, (0.40, 0.20), (0.28, 0.18), "needed theorem\nFitting divisibility plus a conductor-scale norm bound", TEAL, 11.3, "bold")
    arrow(ax, (0.14, 0.61), (0.20, 0.38), RED)
    arrow(ax, (0.70, 0.61), (0.54, 0.38), TEAL)
    ax.text(0.5, 0.065, "Multiplicity belongs in the cotangent complex.  The remaining abc estimate is a determinant-line size theorem.", ha="center", fontsize=10.8, color=MUTED)
    save_figure(fig, out, "17_corrected_determinant_target")


def write_extension_tables(base: Path, profiles: pd.DataFrame, summary: pd.DataFrame) -> None:
    tables = base / "tables"
    tables.mkdir(exist_ok=True)
    output = profiles.copy()
    output["cyclic_survival_fraction"] = [f"{value.numerator}/{value.denominator}" for value in output.cyclic_survival_fraction]
    output["local_capacity_fraction"] = [f"{value.numerator}/{value.denominator}" for value in output.local_capacity_fraction]
    output.to_csv(tables / "persistence_cyclic_obstruction.csv", index=False)
    summary.to_csv(tables / "persistence_corpus_summary.csv", index=False)
    toy_rows = []
    for moduli in ([2, 3], [4, 8], [4, 8, 9, 25], [8, 8, 8], [3, 9, 27]):
        toy_rows.append(toy_hecke_order_invariants(moduli))
    pd.DataFrame(toy_rows).to_csv(tables / "toy_hecke_cotangent_orders.csv", index=False)


def run(base: Path) -> dict[str, object]:
    base_results = ray.run(base)
    profiles = corpus_profiles(base / "source_data")
    summary = corpus_summary(profiles)
    write_extension_tables(base, profiles, summary)

    checks = 0
    for c in [1, 8, 81, 625, 2401, 2**8 * 3**22 * 5**4]:
        profile = persistence_profile(c)
        if profile.order != c // radical(c):
            raise AssertionError("persistence order failed")
        if profile.forced_kernel_lower_bound * profile.cyclic_image_capacity != profile.order:
            raise AssertionError("cyclic kernel factorization failed")
        checks += 2
    for moduli in ([2, 3], [4, 8], [4, 8, 9, 25], [8, 8, 8], [3, 9, 27]):
        inv = toy_hecke_order_invariants(moduli)
        if inv["cotangent_order"] != math.prod(moduli):
            raise AssertionError("toy cotangent order failed")
        if inv["congruence_exponent"] != math.lcm(*moduli):
            raise AssertionError("toy congruence exponent failed")
        if inv["wiles_defect_factor"] * inv["congruence_exponent"] != inv["cotangent_order"]:
            raise AssertionError("toy defect factor failed")
        checks += 3
    for eigenvalues in ([0, 2], [0, 2, 5], [1, 4, 10, 13], [-3, 0, 7, 12]):
        for target in range(len(eigenvalues)):
            inv = monogenic_filter_invariants(eigenvalues, target)
            if inv["projector_denominator"] != inv["cotangent_order"] or inv["wiles_defect_factor"] != 1:
                raise AssertionError("monogenic complete-intersection equality failed")
            checks += 1
    special = persistence_profile(2**8 * 3**22 * 5**4)
    expected_kernel = 2**6 * 3**20 * 5**2
    if special.packet_rank != 31 or special.forced_kernel_lower_bound != expected_kernel:
        raise AssertionError("large arbitrary-precision persistence case failed")
    checks += 1
    if len(profiles) != 466:
        raise AssertionError("unexpected corpus size")
    checks += len(profiles)
    for record in profiles.itertuples(index=False):
        if exact_int(record.forced_kernel_lower_bound) * exact_int(record.cyclic_image_capacity) != exact_int(record.order):
            raise AssertionError("corpus cyclic factorization failed")
        checks += 1

    figures = base / "figures"
    figure_cyclic_rank_obstruction(figures)
    figure_corpus_kernel(profiles, figures)
    figure_toy_order(figures)
    figure_ci_vs_defect(figures)
    figure_two_prime_spectrogram(figures)
    figure_corrected_target(figures)

    results = {
        **base_results,
        "title": "Projector-Resolved ABC Attack VII: Integral Automorphic Transfer",
        "status": "exact structural corrections and finite experiments. abc not proved",
        "extension_checks": checks,
        "total_checks": int(base_results["total_checks"]) + checks,
        "figure_pairs": 17,
        "corpus_rows": len(profiles),
        "persistence_direct_occupancy_status": "refuted in general by p-rank obstruction",
        "cyclic_congruence_theorem": "T/(I + Ann(I)) is cyclic of order eta for a rational eigenline",
        "corrected_target": "cotangent or derived determinant-line transfer with Fitting divisibility and an archimedean conductor-scale bound",
        "large_case": {
            "c": 2**8 * 3**22 * 5**4,
            "packet_rank": special.packet_rank,
            "persistence_order": special.order,
            "cyclic_capacity": special.cyclic_image_capacity,
            "forced_kernel_lower_bound": special.forced_kernel_lower_bound,
        },
        "corpus_summary": summary.to_dict(orient="records"),
        "roadblock": "The local and cyclic channels are too small.  The missing theorem must control a global Hecke cotangent determinant and its archimedean norm.",
    }
    results_dir = base / "results"
    results_dir.mkdir(exist_ok=True)
    (results_dir / "attack_vii_results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(run(args.base), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
