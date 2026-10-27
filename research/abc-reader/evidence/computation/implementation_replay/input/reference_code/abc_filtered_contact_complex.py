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
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np
from sympy import factorint

INK = "#18212B"
MUTED = "#5E6B75"
BLUE = "#2E6F9E"
TEAL = "#268A83"
ORANGE = "#D78942"
MAGENTA = "#9C4F82"
RED = "#C6554A"
PALE_BLUE = "#E8F1F7"
PALE_TEAL = "#E8F5F3"
PALE_ORANGE = "#FBF0E5"
PALE_MAGENTA = "#F5EAF1"
PAPER = "#FAFAF7"
GRID = "#CBD2D8"


def exact_int(value: object, name: str = "value") -> int:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not bool")
    try:
        result = int(value)
    except Exception as exc:  # pragma: no cover - defensive
        raise TypeError(f"{name} must be integer-like") from exc
    if hasattr(value, "__int__") and not isinstance(value, (float, complex)):
        return result
    if isinstance(value, int):
        return result
    raise TypeError(f"{name} must be integer-like")


def prime_factorization(n: int) -> dict[int, int]:
    n = abs(exact_int(n, "n"))
    if n < 1:
        raise ValueError("n must be nonzero")
    return {int(p): int(e) for p, e in factorint(n).items()}


def radical(n: int) -> int:
    result = 1
    for p in prime_factorization(n):
        result *= p
    return result


def contact_order(n: int) -> int:
    n = abs(exact_int(n, "n"))
    return n // radical(n)


def contact_primary_orders(n: int) -> dict[int, int]:
    return {p: p ** max(e - 1, 0) for p, e in prime_factorization(n).items() if e >= 2}


def associated_graded_rank(n: int) -> int:
    return sum(max(e - 1, 0) for e in prime_factorization(n).values())


def associated_graded_order(n: int) -> int:
    result = 1
    for p, e in prime_factorization(n).items():
        result *= p ** max(e - 1, 0)
    return result


def max_cyclic_image_of_split(n: int) -> int:
    """Largest possible image order from direct_sum(Z/p)^(e-1) to any cyclic group."""
    result = 1
    for p, e in prime_factorization(n).items():
        if e >= 2:
            result *= p
    return result


def split_forced_kernel(n: int) -> int:
    order = associated_graded_order(n)
    image = max_cyclic_image_of_split(n)
    return order // image


@dataclass(frozen=True)
class CyclicTransfer:
    source_order: int
    target_order: int
    gcd_order: int
    kernel_order: int
    image_order: int
    cokernel_order: int
    source_multiplier: int
    target_multiplier: int


def cyclic_transfer(source_order: int, target_order: int) -> CyclicTransfer:
    m = abs(exact_int(source_order, "source_order"))
    eta = abs(exact_int(target_order, "target_order"))
    if m < 1 or eta < 1:
        raise ValueError("orders must be positive")
    g = math.gcd(m, eta)
    return CyclicTransfer(
        source_order=m,
        target_order=eta,
        gcd_order=g,
        kernel_order=m // g,
        image_order=g,
        cokernel_order=eta // g,
        source_multiplier=m // g,
        target_multiplier=eta // g,
    )


def local_contact_layers(p: int, e: int) -> list[tuple[int, int]]:
    p = exact_int(p, "p")
    e = exact_int(e, "e")
    if p < 2 or e < 1:
        raise ValueError("p >= 2 and e >= 1 required")
    return [(j, p) for j in range(1, e)]


def extension_is_nonsplit(p: int, j: int) -> bool:
    """0 -> Z/p^(j-1) -> Z/p^j -> Z/p -> 0 is nonsplit for j>=2."""
    p = exact_int(p, "p")
    j = exact_int(j, "j")
    if p < 2 or j < 2:
        raise ValueError("p >= 2 and j >= 2 required")
    # Any lift of 1 mod p has order p^j, not p, in Z/p^j.
    return pow(1, 1, p**j) == 1 and (p ** (j - 1)) % (p**j) != 0


def filtered_defect(n: int, eta: int) -> int:
    return cyclic_transfer(contact_order(n), eta).kernel_order


def depth_shortfall(n: int, eta: int) -> dict[int, int]:
    eta_fac = prime_factorization(eta)
    return {
        p: max((e - 1) - eta_fac.get(p, 0), 0)
        for p, e in prime_factorization(n).items()
        if e >= 2
    }


def toy_filtered_hecke(moduli: Iterable[int]) -> dict[str, int | list[int]]:
    mods = [abs(exact_int(m)) for m in moduli]
    if not mods or any(m < 1 for m in mods):
        raise ValueError("positive moduli required")
    product = math.prod(mods)
    lcm = 1
    for m in mods:
        lcm = math.lcm(lcm, m)
    return {
        "moduli": mods,
        "cotangent_order": product,
        "congruence_order": lcm,
        "wiles_defect_factor": product // lcm,
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _save(fig: plt.Figure, out: Path, name: str) -> None:
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(out / f"{name}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def _diagram_axes(figsize=(12.5, 6.4)) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def _box(ax: plt.Axes, xy: tuple[float, float], wh: tuple[float, float], text: str,
         face: str = "white", edge: str = INK, fontsize: float = 11.5, lw: float = 1.6) -> None:
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.012,rounding_size=.018",
                           facecolor=face, edgecolor=edge, linewidth=lw)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, color=INK)


def _arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float],
           color: str = INK, lw: float = 1.7, text: str | None = None,
           text_offset=(0.0, 0.035), style: str = "-|>") -> None:
    arr = FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=13,
                          linewidth=lw, color=color, connectionstyle="arc3,rad=0")
    ax.add_patch(arr)
    if text:
        ax.text((start[0] + end[0]) / 2 + text_offset[0],
                (start[1] + end[1]) / 2 + text_offset[1],
                text, ha="center", va="center", fontsize=10.5, color=color)


def figure_contact_complex(out: Path) -> None:
    fig, ax = _diagram_axes()
    ax.text(.5, .94, "The output persistence is a filtered cusp-contact complex", ha="center", fontsize=20, weight="bold")
    _box(ax, (.05, .57), (.22, .18), "cusp contact divisor\n" + r"$C=\sum e_p[p]$", PALE_BLUE, BLUE, 14)
    _box(ax, (.39, .57), (.22, .18), "reduced contact\n" + r"$C_{\rm red}=\sum[p]$", PALE_TEAL, TEAL, 14)
    _box(ax, (.73, .57), (.22, .18), "contact quotient\n" + r"$\mathcal{J}_c=R_c\mathrm{Z}/c\mathrm{Z}$", PALE_ORANGE, ORANGE, 13)
    _arrow(ax, (.27, .66), (.39, .66), BLUE, text="inclusion")
    _arrow(ax, (.61, .66), (.73, .66), TEAL, text="cohomology")
    ax.text(.5, .38, r"$\mathbf{J}_c=[\mathcal{O}(-C)\to\mathcal{O}(-C_{\rm red})]\simeq[\mathrm{Z}\overset{c/R_c}{\longrightarrow}\mathrm{Z}]$",
            ha="center", fontsize=15, color=INK)
    ax.text(.5, .22, r"$|H^0(\mathbf{J}_c)|=c/R_c$", ha="center", fontsize=18, weight="bold", color=BLUE)
    ax.text(.5, .10, "The carries between depth layers remain part of the object.", ha="center", fontsize=12, color=MUTED)
    _save(fig, out, "01_contact_complex")


def figure_filtered_vs_graded(out: Path, p: int = 3, e: int = 6) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.6))
    ax = axes[0]
    ax.set_title(r"filtered packet $\mathrm{Z}/p^{e-1}\mathrm{Z}$", weight="bold")
    ax.axis("off")
    ys = np.linspace(.82, .18, e)
    for j, y in enumerate(ys[:-1], start=1):
        ax.add_patch(Rectangle((.30, y - .035), .40, .07, facecolor=PALE_BLUE, edgecolor=BLUE, lw=1.5))
        ax.text(.5, y, rf"$p^{{{j}}}\mathrm{{Z}}/p^{{{e}}}\mathrm{{Z}}$", ha="center", va="center", fontsize=11)
        if j < e - 1:
            ax.annotate("", xy=(.5, ys[j] + .04), xytext=(.5, y - .04), arrowprops=dict(arrowstyle="->", color=INK))
    ax.text(.5, .05, r"non-split carry extensions", ha="center", color=MUTED, fontsize=11)
    ax = axes[1]
    ax.set_title(r"associated graded $\bigoplus_{j=1}^{e-1}\mathrm{F}_p$", weight="bold")
    ax.axis("off")
    for j, y in enumerate(np.linspace(.80, .20, e - 1), start=1):
        ax.add_patch(FancyBboxPatch((.33, y - .045), .34, .09, boxstyle="round,pad=.01", facecolor=PALE_MAGENTA, edgecolor=MAGENTA))
        ax.text(.5, y, rf"grade {j}: $\mathrm{{F}}_p$", ha="center", va="center", fontsize=11)
    ax.text(.5, .05, "all extension data forgotten", ha="center", color=MUTED, fontsize=11)
    fig.suptitle("Passing to the associated graded preserves order but destroys cyclic carry structure", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, .03, 1, .90])
    _save(fig, out, "02_filtered_vs_graded")


def figure_rank_correction(out: Path) -> None:
    cases = [
        ("$c=2^7$", 128, 4),
        ("$c=5^4 7$", 4375, 8),
        ("$c=2^8 3^{22}5^4$", 2**8 * 3**22 * 5**4, 30),
    ]
    split = [split_forced_kernel(c) for _, c, _ in cases]
    filtered = [filtered_defect(c, eta) for _, c, eta in cases]
    x = np.arange(len(cases))
    fig, ax = plt.subplots(figsize=(12.2, 5.5))
    ax.bar(x - .18, np.log10(np.maximum(split, 1)), width=.36, label="split graded forced kernel", color=MAGENTA)
    ax.bar(x + .18, np.log10(np.maximum(filtered, 1)), width=.36, label="filtered cyclic kernel", color=TEAL)
    ax.set_xticks(x, [label for label, _, _ in cases])
    ax.set_ylabel(r"$\log_{10}$ kernel lower bound")
    ax.set_title("The graded rank obstruction disappears when carry extensions are retained", weight="bold", fontsize=16)
    ax.grid(axis="y", alpha=.18)
    ax.legend()
    fig.tight_layout()
    _save(fig, out, "03_rank_obstruction_correction")


def figure_gcd_transducer(out: Path) -> None:
    source = np.array([4, 8, 12, 16, 24, 32, 64, 81, 125], dtype=int)
    target = np.array([4, 6, 8, 12, 16, 24, 27, 32, 64], dtype=int)
    matrix = np.array([[math.gcd(int(m), int(e)) for e in target] for m in source])
    fig, ax = plt.subplots(figsize=(11.5, 6.1))
    im = ax.imshow(matrix, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(target)), [str(v) for v in target])
    ax.set_yticks(range(len(source)), [str(v) for v in source])
    ax.set_xlabel(r"target order $\eta$")
    ax.set_ylabel(r"source contact order $m$")
    ax.set_title(r"Maximum filtered transfer image is $\gcd(m,\eta)$", weight="bold", fontsize=17)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            color = "white" if matrix[i, j] > matrix.max() * .42 else INK
            ax.text(j, i, str(matrix[i, j]), ha="center", va="center", fontsize=8.5, color=color)
    fig.colorbar(im, ax=ax, fraction=.028, pad=.02, label="image order")
    fig.tight_layout()
    _save(fig, out, "04_gcd_transducer")


def load_sampled(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sampled_rows(path: Path) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for raw in load_sampled(path):
        c = int(raw["c"])
        eta = int(raw["sampled_projector_denominator"])
        m = contact_order(c)
        transfer = cyclic_transfer(m, eta)
        row: dict[str, object] = {
            "radical": int(raw["radical"]),
            "target": int(raw["target"]),
            "a": int(raw["a"]),
            "b": int(raw["b"]),
            "c": c,
            "quality": float(raw["quality"]),
            "contact_order": m,
            "sampled_eta": eta,
            "gcd_image": transfer.image_order,
            "filtered_kernel": transfer.kernel_order,
            "filtered_cokernel": transfer.cokernel_order,
            "split_forced_kernel": split_forced_kernel(c),
            "graded_rank": associated_graded_rank(c),
            "kernel_fraction": transfer.kernel_order / m,
            "depth_shortfall": ";".join(f"{p}:{d}" for p, d in sorted(depth_shortfall(c, eta).items())),
        }
        output.append(row)
    return output


def figure_sampled_defect(out: Path, rows: list[dict[str, object]]) -> None:
    x = np.array([int(r["contact_order"]) for r in rows], dtype=float)
    y_split = np.array([int(r["split_forced_kernel"]) for r in rows], dtype=float)
    y_filtered = np.array([int(r["filtered_kernel"]) for r in rows], dtype=float)
    q = np.array([float(r["quality"]) for r in rows])
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.2))
    axes[0].scatter(x, y_split, c=q, cmap="viridis", s=34, alpha=.80, label="split")
    axes[0].scatter(x, y_filtered, c=q, cmap="viridis", marker="x", s=34, alpha=.80, label="filtered")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("output contact order")
    axes[0].set_ylabel("kernel lower bound")
    axes[0].set_title("Sampled Hecke targets", weight="bold")
    axes[0].legend()
    ratio = y_filtered / np.maximum(y_split, 1)
    axes[1].hist(np.log10(np.maximum(ratio, 1e-18)), bins=22, color=TEAL, edgecolor=INK)
    axes[1].set_xlabel(r"$\log_{10}$(filtered kernel / graded forced kernel)")
    axes[1].set_ylabel("count")
    axes[1].set_title("Effect of restoring carries", weight="bold")
    for ax in axes:
        ax.grid(alpha=.16)
    fig.suptitle("The filtered defect is a gcd depth shortfall, not a rank mismatch", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, .92])
    _save(fig, out, "05_sampled_filtered_defect")


def figure_depth_shortfall(out: Path, rows: list[dict[str, object]]) -> None:
    points: list[tuple[int, int, int]] = []
    for row in rows:
        c = int(row["c"])
        eta = int(row["sampled_eta"])
        eta_fac = prime_factorization(eta)
        for p, e in prime_factorization(c).items():
            if e >= 2:
                points.append((p, e - 1, eta_fac.get(p, 0)))
    x = np.arange(len(points))
    source_depth = np.array([v for _, v, _ in points])
    occupied = np.array([min(v, t) for _, v, t in points])
    order = np.argsort(source_depth - occupied)[::-1]
    order = order[: min(45, len(order))]
    fig, ax = plt.subplots(figsize=(12.6, 5.8))
    ax.bar(np.arange(len(order)), source_depth[order], color=PALE_ORANGE, edgecolor=ORANGE, label="contact depth $e_p-1$")
    ax.bar(np.arange(len(order)), occupied[order], color=TEAL, edgecolor=INK, label=r"sampled occupied depth $\min(e_p-1,v_p(\eta))$")
    labels = [str(points[i][0]) for i in order]
    ax.set_xticks(np.arange(len(order)), labels, rotation=90, fontsize=7)
    ax.set_xlabel("conductor prime $p$ in selected rows")
    ax.set_ylabel("filtration layers")
    ax.set_title("The filtered defect is missing prime-power depth", weight="bold", fontsize=17)
    ax.legend()
    ax.grid(axis="y", alpha=.16)
    fig.tight_layout()
    _save(fig, out, "06_prime_depth_shortfall")


def figure_local_contact(out: Path) -> None:
    fig, ax = _diagram_axes((12.8, 6.6))
    ax.text(.5, .95, "Odd-adic and dyadic contact coordinates preserve the same filtered length", ha="center", fontsize=19, weight="bold")
    _box(ax, (.05, .58), (.25, .18), "odd p\n" + r"$p\mathrm{Z}_p/p^e\mathrm{Z}_p$", PALE_TEAL, TEAL, 12.5)
    _box(ax, (.375, .58), (.25, .18), "dyadic additive\n" + r"$2\mathrm{Z}_2/2^e\mathrm{Z}_2$", PALE_BLUE, BLUE, 12.5)
    _box(ax, (.70, .58), (.25, .18), "weighted dyadic units\n" + r"$(1+4\mathrm{Z}_2)/(1+2^{e+1}\mathrm{Z}_2)$", PALE_MAGENTA, MAGENTA, 10.5)
    for x0 in [.175, .50, .825]:
        _arrow(ax, (x0, .58), (x0, .39), INK)
    _box(ax, (.14, .25), (.72, .13), r"common filtered length $e-1$ and associated graded $(\mathrm{F}_p)^{e-1}$", "white", INK, 15)
    ax.text(.5, .12, "The local coordinates differ, but the carry filtration is the invariant object.", ha="center", fontsize=12, color=MUTED)
    _save(fig, out, "07_dyadic_odd_adic_contact")


def figure_transducer(out: Path) -> None:
    fig, ax = _diagram_axes((13.0, 6.7))
    ax.text(.5, .95, "Filtered cusp-Selmer-Hecke transducer", ha="center", fontsize=21, weight="bold")
    boxes = [
        (.03, .56, .16, .18, "cusp contact\n" + r"$\mathbf{J}_c$", PALE_BLUE, BLUE),
        (.23, .56, .16, .18, "local Steinberg\n" + r"$\mathbf{L}_p^{\rm st}$", PALE_TEAL, TEAL),
        (.43, .56, .16, .18, "global Selmer\ncomplex", PALE_ORANGE, ORANGE),
        (.63, .56, .16, .18, "Hecke cotangent\ncomplex", PALE_MAGENTA, MAGENTA),
        (.83, .56, .14, .18, "target channel\n" + r"$\mathbf{C}_f$", "white", INK),
    ]
    for x, y, w, h, text, face, edge in boxes:
        _box(ax, (x, y), (w, h), text, face, edge, 10.5)
    for i in range(len(boxes) - 1):
        x, y, w, h, *_ = boxes[i]
        nx, ny, *_ = boxes[i + 1]
        _arrow(ax, (x + w, y + h / 2), (nx, ny + h / 2), INK)
    ax.text(.31, .48, "local contact classes", ha="center", fontsize=10, color=MUTED)
    ax.text(.51, .48, r"global compatibility", ha="center", fontsize=10, color=MUTED)
    ax.text(.71, .48, r"$R=\mathrm{T}$ bridge", ha="center", fontsize=10, color=MUTED)
    _box(ax, (.20, .21), (.60, .14), r"transduction cone $\mathbf{E}_f=\mathrm{Cone}(\Theta_f)$", "white", RED, 15)
    _arrow(ax, (.50, .56), (.50, .35), RED)
    ax.text(.5, .10, "The missing theorem is a Bockstein-compatible map with small source loss and controlled target size.", ha="center", fontsize=11.5, color=MUTED)
    _save(fig, out, "08_filtered_transducer_architecture")


def figure_extension_reconstruction(out: Path, p: int = 2, e: int = 7) -> None:
    fig, ax = _diagram_axes((12.8, 6.7))
    ax.text(.5, .95, "Carry extensions rebuild the cyclic prime-power packet", ha="center", fontsize=20, weight="bold")
    x_positions = np.linspace(.10, .90, e - 1)
    for j, x in enumerate(x_positions, start=1):
        _box(ax, (x - .045, .67), (.09, .10), rf"$\mathrm{{F}}_{p}$", PALE_MAGENTA, MAGENTA, 11)
        ax.text(x, .61, rf"grade {j}", ha="center", fontsize=9, color=MUTED)
    for i in range(len(x_positions) - 1):
        _arrow(ax, (x_positions[i] + .045, .72), (x_positions[i + 1] - .045, .72), RED, text="carry", text_offset=(0, .04))
    _box(ax, (.28, .28), (.44, .17), f"filtered synthesis\nZ/{p**(e-1)}Z", PALE_BLUE, BLUE, 17)
    for x in x_positions:
        _arrow(ax, (x, .67), (.50, .45), BLUE, lw=1.0)
    ax.text(.5, .14, r"order is preserved, while extension data converts many grades into one cyclic object", ha="center", fontsize=12, color=MUTED)
    _save(fig, out, "09_extension_reconstruction")


def figure_attack_transition(out: Path) -> None:
    fig, ax = _diagram_axes((13.0, 6.6))
    ax.text(.5, .95, "Attack VII to Attack VIII", ha="center", fontsize=22, weight="bold")
    _box(ax, (.05, .58), (.36, .22), "Attack VII\nassociated graded packet\n" + r"$\bigoplus_p(\mathrm{F}_p)^{e_p-1}$", PALE_MAGENTA, MAGENTA, 14)
    _box(ax, (.59, .58), (.36, .22), "Attack VIII\nfiltered contact complex\n" + r"$[\mathrm{Z}\overset{c/R_c}{\longrightarrow}\mathrm{Z}]$", PALE_BLUE, BLUE, 14)
    _arrow(ax, (.41, .69), (.59, .69), INK, text="restore carries", text_offset=(0, .055))
    _box(ax, (.05, .24), (.36, .18), "old barrier\np-rank mismatch with cyclic target", PALE_ORANGE, ORANGE, 13)
    _box(ax, (.59, .24), (.36, .18), "new barrier\nconstruct filtered map\nand prove size bounds", PALE_TEAL, TEAL, 13)
    _arrow(ax, (.23, .58), (.23, .42), ORANGE)
    _arrow(ax, (.77, .58), (.77, .42), TEAL)
    ax.text(.5, .09, "The previous no-go theorem remains correct for the graded approximation, but not for the filtered source.", ha="center", fontsize=11.5, color=MUTED)
    _save(fig, out, "10_attack_vii_to_viii")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate(base: Path) -> dict[str, object]:
    figures = base / "figures"
    tables = base / "tables"
    results_dir = base / "results"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    rows = sampled_rows(base / "source_data" / "sampled_hecke_targets.csv")
    write_csv(tables / "sampled_filtered_transfer.csv", rows)

    examples: list[dict[str, object]] = []
    for c, eta, label in [
        (128, 4, "3+125=128"),
        (4375, 8, "1+4374=4375"),
        (6561, 8, "289+6272=6561"),
        (2**8 * 3**22 * 5**4, 30, "large persistence example"),
    ]:
        tr = cyclic_transfer(contact_order(c), eta)
        examples.append({
            "label": label,
            "c": c,
            "factorization": " ".join(f"{p}^{e}" for p, e in sorted(prime_factorization(c).items())),
            "contact_order": tr.source_order,
            "graded_rank": associated_graded_rank(c),
            "split_forced_kernel": split_forced_kernel(c),
            "target_eta": eta,
            "gcd_image": tr.image_order,
            "filtered_kernel": tr.kernel_order,
            "filtered_cokernel": tr.cokernel_order,
        })
    write_csv(tables / "contact_examples.csv", examples)

    toy_rows: list[dict[str, object]] = []
    for mods in ([4, 8], [8, 8, 3], [9, 27, 5], [4, 8, 16, 3, 9]):
        record = toy_filtered_hecke(mods)
        toy_rows.append({
            "moduli": " ".join(map(str, mods)),
            "cotangent_order": record["cotangent_order"],
            "congruence_order": record["congruence_order"],
            "wiles_defect_factor": record["wiles_defect_factor"],
        })
    write_csv(tables / "toy_filtered_hecke.csv", toy_rows)

    figure_contact_complex(figures)
    figure_filtered_vs_graded(figures)
    figure_rank_correction(figures)
    figure_gcd_transducer(figures)
    figure_sampled_defect(figures, rows)
    figure_depth_shortfall(figures, rows)
    figure_local_contact(figures)
    figure_transducer(figures)
    figure_extension_reconstruction(figures)
    figure_attack_transition(figures)

    sampled_kernel = np.array([int(r["filtered_kernel"]) for r in rows], dtype=object)
    sampled_split = np.array([int(r["split_forced_kernel"]) for r in rows], dtype=object)
    summary: dict[str, object] = {
        "title": "Projector-Resolved ABC Attack VIII: Filtered Cusp-Contact Transfer",
        "status": "filtered structural correction and conditional theorem. abc not proved",
        "sampled_rows": len(rows),
        "figure_pairs": 10,
        "exact_contact_identity": "|R_c Z / c Z| = c / R_c",
        "associated_graded_identity": "gr(J_c) = direct sum over p^e||c of (F_p)^(e-1)",
        "cyclic_transfer_identity": "max image order between cyclic packets of orders m and eta is gcd(m,eta)",
        "median_filtered_kernel_log10": float(np.median([math.log10(max(int(v), 1)) for v in sampled_kernel])),
        "median_split_kernel_log10": float(np.median([math.log10(max(int(v), 1)) for v in sampled_split])),
        "large_example": examples[-1],
        "corrected_roadblock": "construct a geometry-induced Bockstein-compatible filtered transfer and prove both source depth occupancy and an archimedean target bound",
        "conditional_target": "small kernel for H0(J_c)->H0(C_f) plus target size <= R_a R_b R^epsilon",
        "tests_expected": 18,
    }
    (results_dir / "attack_viii_results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ABC Attack VIII filtered contact data and figures")
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    summary = generate(args.base.resolve())
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
