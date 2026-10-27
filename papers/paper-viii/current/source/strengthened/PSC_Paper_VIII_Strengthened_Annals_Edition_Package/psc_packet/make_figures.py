from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Rectangle

from .packet_algorithms import (
    TreeNode,
    compile_tree_budget,
    compile_tree_lagrangian,
    recompress_factors,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
DATA = ROOT / "verification" / "benchmark_results_sanitized.json"

plt.rcParams.update(
    {
        "font.size": 9.5,
        "axes.titlesize": 10.5,
        "axes.labelsize": 9.5,
        "legend.fontsize": 8.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def save(fig: plt.Figure, stem: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def frame() -> pd.DataFrame:
    data = json.loads(DATA.read_text())
    return pd.DataFrame(data["results"])


def architecture() -> None:
    fig, ax = plt.subplots(figsize=(11.2, 2.8))
    labels = [
        "packet coordinates",
        "operator representation",
        "cost and error model",
        "compiler decision",
        "device schedule",
        "declared output",
    ]
    x = np.arange(len(labels))
    for i, label in enumerate(labels):
        box = FancyBboxPatch((i - 0.42, -0.16), 0.84, 0.32, boxstyle="round,pad=0.03", fill=False, linewidth=1.2)
        ax.add_patch(box)
        ax.text(i, 0, label, ha="center", va="center")
        if i < len(labels) - 1:
            ax.annotate("", xy=(i + 0.54, 0), xytext=(i + 0.44, 0), arrowprops={"arrowstyle": "->", "lw": 1.2})
    ax.set_xlim(-0.55, len(labels) - 0.45)
    ax.set_ylim(-0.35, 0.35)
    ax.axis("off")
    ax.set_title("A packet computation is specified before it is scheduled")
    save(fig, "01_packet_compilation_architecture")


def packet_ir() -> None:
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    coords = {0: (0.7, 2.9), 1: (2.7, 3.4), 2: (2.7, 1.6), 3: (5.0, 3.0), 4: (5.2, 1.2), 5: (7.2, 2.2)}
    for v, (x, y) in coords.items():
        box = FancyBboxPatch((x - 0.34, y - 0.22), 0.68, 0.44, boxstyle="round,pad=0.03", fill=False)
        ax.add_patch(box)
        ax.text(x, y, f"packet {v}", ha="center", va="center")
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)]
    for a, b in edges:
        xa, ya = coords[a]
        xb, yb = coords[b]
        ax.annotate("", xy=(xb - 0.38, yb), xytext=(xa + 0.38, ya), arrowprops={"arrowstyle": "->", "lw": 1.1})
    ax.text(4.1, 4.0, "active block addresses", ha="center")
    ax.text(4.1, 0.35, "dimensions, block type, tolerance, and schedule metadata", ha="center")
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    ax.set_title("Packet operator intermediate representation")
    save(fig, "02_packet_ir_graph")


def arithmetic_reduction() -> None:
    ns = np.array([512, 1024, 2048, 4096, 8192, 16384])
    fig, ax = plt.subplots(figsize=(7.6, 4.7))
    for block, rank in [(64, 0), (64, 8), (128, 8), (64, 32)]:
        values = ns / (block + 2 * rank)
        ax.plot(ns, values, marker="o", label=f"block {block}, rank {rank}")
    ax.set_xlabel("dimension")
    ax.set_ylabel("dense work divided by packet work")
    ax.set_title("Ideal arithmetic reduction for equal packets")
    ax.grid(alpha=0.25)
    ax.legend()
    save(fig, "03_ideal_arithmetic_reduction")


def roofline_schematic() -> None:
    intensity = np.logspace(-1, 3, 300)
    bandwidth = 1.0
    peak = 50.0
    attainable = np.minimum(peak, bandwidth * intensity)
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.loglog(intensity, attainable, linewidth=2)
    ax.axhline(peak, linestyle=":")
    ax.axvline(peak / bandwidth, linestyle=":")
    ax.scatter([0.8, 6, 90], [0.8, 6, 50], s=55)
    ax.text(0.9, 0.65, "irregular transfer")
    ax.text(6.6, 4.8, "batched packets")
    ax.text(95, 38, "dense product")
    ax.set_xlabel("arithmetic intensity")
    ax.set_ylabel("attainable work rate in normalized units")
    ax.set_title("Representation changes the roofline location")
    ax.grid(alpha=0.2, which="both")
    save(fig, "04_roofline_schematic")


def bdlr_structure() -> None:
    fig, ax = plt.subplots(figsize=(7.0, 5.4))
    n = 6
    for i in range(n):
        ax.add_patch(Rectangle((i, n - i - 1), 1, 1, fill=False, linewidth=1.3))
    ax.annotate("", xy=(5.6, 5.6), xytext=(0.4, 0.4), arrowprops={"arrowstyle": "->", "lw": 1.4})
    ax.annotate("", xy=(5.6, 0.4), xytext=(0.4, 5.6), arrowprops={"arrowstyle": "->", "lw": 1.4})
    ax.text(3.0, 6.35, "independent diagonal packets")
    ax.text(3.0, -0.45, "global low rank transfer factors")
    ax.set_xlim(-0.2, 6.2)
    ax.set_ylim(-0.7, 6.7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Block diagonal plus low rank representation")
    save(fig, "05_bdlr_structure")


def recompression() -> None:
    rng = np.random.default_rng(11)
    left = rng.normal(size=(90, 18))
    right = rng.normal(size=(80, 18))
    result = recompress_factors(left, right, 8)
    s = result.singular_values
    fig, ax = plt.subplots(figsize=(7.4, 4.7))
    ax.semilogy(np.arange(1, len(s) + 1), s, marker="o")
    ax.axvline(8.5, linestyle=":")
    ax.text(9.0, s[8], "discarded tail")
    ax.set_xlabel("singular value index")
    ax.set_ylabel("small core singular value")
    ax.set_title("Optimal recompression is computed in the factor core")
    ax.grid(alpha=0.25)
    save(fig, "06_recompression_spectrum")


def graph_paths() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.2))
    coords = {0: (0, 1), 1: (1.3, 1.8), 2: (1.3, 0.2), 3: (2.7, 1.0), 4: (4.0, 1.0)}
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
    for ax, title, extra in [(axes[0], "active blocks", []), (axes[1], "support after three compositions", [(0, 3), (1, 4), (2, 4), (0, 4)])]:
        for v, (x, y) in coords.items():
            ax.add_patch(FancyBboxPatch((x - 0.18, y - 0.14), 0.36, 0.28, boxstyle="round,pad=0.02", fill=False))
            ax.text(x, y, str(v), ha="center", va="center")
        for a, b in edges:
            xa, ya = coords[a]
            xb, yb = coords[b]
            ax.annotate("", xy=(xb - 0.2, yb), xytext=(xa + 0.2, ya), arrowprops={"arrowstyle": "->"})
        for a, b in extra:
            xa, ya = coords[a]
            xb, yb = coords[b]
            ax.annotate("", xy=(xb - 0.2, yb + 0.08), xytext=(xa + 0.2, ya + 0.08), arrowprops={"arrowstyle": "->", "linestyle": ":"})
        ax.set_xlim(-0.4, 4.4)
        ax.set_ylim(-0.3, 2.3)
        ax.axis("off")
        ax.set_title(title)
    fig.suptitle("Graph paths predict possible block fill")
    save(fig, "07_path_support")


def triangular_schedule() -> None:
    fig, ax = plt.subplots(figsize=(8.2, 4.3))
    levels = [[0], [1, 2, 3], [4, 5], [6]]
    for j, level in enumerate(levels):
        for k, v in enumerate(level):
            y = k - (len(level) - 1) / 2
            ax.add_patch(FancyBboxPatch((j - 0.27, y - 0.18), 0.54, 0.36, boxstyle="round,pad=0.02", fill=False))
            ax.text(j, y, f"packet {v}", ha="center", va="center")
        if j < len(levels) - 1:
            ax.annotate("", xy=(j + 0.66, 0), xytext=(j + 0.34, 0), arrowprops={"arrowstyle": "->", "lw": 1.2})
    ax.set_xticks(range(len(levels)), [f"stage {j}" for j in range(len(levels))])
    ax.set_yticks([])
    ax.set_xlim(-0.6, 3.6)
    ax.set_ylim(-1.8, 1.8)
    ax.set_title("A block triangular solve advances by topological level")
    for spine in ax.spines.values():
        spine.set_visible(False)
    save(fig, "08_topological_schedule")


def preconditioner() -> None:
    rng = np.random.default_rng(17)
    n = 96
    block = 12
    d = np.zeros((n, n))
    for j in range(0, n, block):
        a = rng.normal(size=(block, block))
        d[j : j + block, j : j + block] = a.T @ a + 5 * np.eye(block)
    k = rng.normal(size=(n, n))
    k = 0.012 * (k + k.T)
    a = d + k
    eig = np.linalg.eigvalsh(a)
    if eig.min() <= 0:
        a += (1 - eig.min()) * np.eye(n)
    b = rng.normal(size=n)

    def cg(matrix, rhs, precondition=None, maxiter=120):
        x = np.zeros_like(rhs)
        r = rhs - matrix @ x
        z = precondition(r) if precondition else r.copy()
        p = z.copy()
        rz = float(r @ z)
        hist = [np.linalg.norm(r)]
        for _ in range(maxiter):
            ap = matrix @ p
            alpha = rz / float(p @ ap)
            x += alpha * p
            r -= alpha * ap
            hist.append(np.linalg.norm(r))
            if hist[-1] < 1e-10:
                break
            z = precondition(r) if precondition else r.copy()
            rz_new = float(r @ z)
            p = z + (rz_new / rz) * p
            rz = rz_new
        return hist

    hist0 = cg(a, b)
    hist1 = cg(a, b, precondition=lambda x: np.linalg.solve(d, x))
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.semilogy(hist0, label="plain conjugate gradient")
    ax.semilogy(hist1, label="packet block Jacobi")
    ax.set_xlabel("iteration")
    ax.set_ylabel("residual norm")
    ax.set_title("Local packet solves reduce weak cross packet coupling")
    ax.grid(alpha=0.25)
    ax.legend()
    save(fig, "09_packet_preconditioner")


def precision() -> None:
    sensitivities = np.array([1.0, 2.0, 7.0, 3.0, 12.0, 4.0, 9.0, 1.5])
    costs = np.array([1.0, 1.2, 1.0, 0.8, 1.5, 1.1, 1.2, 0.9])
    tolerance = 0.035
    eps = tolerance * costs / (sensitivities * costs.sum())
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar(np.arange(len(eps)), eps)
    ax.set_yscale("log")
    ax.set_xlabel("packet edge")
    ax.set_ylabel("allocated relative tolerance")
    ax.set_title("Sensitivity weighted continuous precision allocation")
    save(fig, "10_precision_allocation")


def compiler_tree() -> None:
    root = TreeNode(
        "root",
        12.0,
        0.0,
        0.8,
        (
            TreeNode("left", 4.1, 1.5, 0.3, (TreeNode("left A", 1.1, 0.2), TreeNode("left B", 1.4, 0.15))),
            TreeNode("right", 4.4, 1.2, 0.3, (TreeNode("right A", 1.0, 0.12), TreeNode("right B", 1.3, 0.18))),
        ),
    )
    plan = compile_tree_lagrangian(root, 2.0)
    selected = set(plan.leaves)
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    coords = {
        "root": (4, 4.4),
        "left": (2.2, 3.0),
        "right": (5.8, 3.0),
        "left A": (1.2, 1.4),
        "left B": (3.0, 1.4),
        "right A": (5.0, 1.4),
        "right B": (6.8, 1.4),
    }
    edges = [("root", "left"), ("root", "right"), ("left", "left A"), ("left", "left B"), ("right", "right A"), ("right", "right B")]
    for a, b in edges:
        xa, ya = coords[a]
        xb, yb = coords[b]
        ax.plot([xa, xb], [ya - 0.22, yb + 0.22], linewidth=1.0)
    for name, (x, y) in coords.items():
        lw = 2.2 if name in selected else 1.0
        box = FancyBboxPatch((x - 0.47, y - 0.22), 0.94, 0.44, boxstyle="round,pad=0.03", fill=False, linewidth=lw)
        ax.add_patch(box)
        ax.text(x, y, name, ha="center", va="center")
    ax.text(4, 0.35, "thick boxes form the exact minimum Lagrangian pruning", ha="center")
    ax.set_xlim(0.3, 7.7)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.set_title("Exact dynamic programming on a candidate packet tree")
    save(fig, "11_tree_compiler")


def compiler_frontier() -> None:
    root = TreeNode(
        "root",
        18.0,
        0.02,
        0.5,
        (
            TreeNode("a", 6.0, 0.40, 0.2, (TreeNode("a0", 3.0, 0.05), TreeNode("a1", 3.0, 0.05))),
            TreeNode("b", 5.0, 0.50, 0.2, (TreeNode("b0", 2.7, 0.08), TreeNode("b1", 2.7, 0.08))),
        ),
    )
    points = set()
    for budget in range(0, 51):
        plan = compile_tree_budget(root, budget, scale=0.02)
        if plan is not None:
            points.add((round(plan.error, 12), round(plan.cost, 12)))
    frontier = sorted(points)
    errors = np.array([p[0] for p in frontier])
    costs = np.array([p[1] for p in frontier])
    fig, ax = plt.subplots(figsize=(7.3, 4.6))
    ax.step(errors, costs, where="post", marker="o")
    for error, cost in frontier:
        ax.annotate(f"({error:.2f}, {cost:.1f})", (error, cost), xytext=(4, 5), textcoords="offset points", fontsize=7.5)
    ax.set_xlabel("quantized representation error")
    ax.set_ylabel("minimum compiled cost")
    ax.set_title("Exact cost and error frontier for the quantized tree model")
    ax.grid(alpha=0.25)
    save(fig, "12_budget_compiler_frontier")


def dense_throughput(df: pd.DataFrame) -> None:
    dense = df[(df["suite"] == "dense_gemm") & df["method"].astype(str).str.startswith("gpu_dense")].copy()
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    for method, group in dense.groupby("method"):
        group = group.sort_values("n")
        label = method.replace("gpu_dense_torch_", "").replace("float32_source_", "")
        ax.plot(group["n"], group["gflops_logical"], marker="o", label=label)
    ax.set_xlabel("dimension")
    ax.set_ylabel("logical GFLOP per second")
    ax.set_title("Recorded device resident dense throughput")
    ax.grid(alpha=0.25)
    ax.legend(ncol=2)
    save(fig, "13_dense_gpu_throughput")


def accuracy_frontier(df: pd.DataFrame) -> None:
    dense = df[(df["suite"] == "dense_gemm") & df["method"].astype(str).str.startswith("gpu_dense") & (df["relative_error"].fillna(0) > 0)].copy()
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    for method, group in dense.groupby("method"):
        label = method.replace("gpu_dense_torch_", "").replace("float32_source_", "")
        ax.scatter(group["relative_error"], group["gflops_logical"], s=45, label=label)
    ax.set_xscale("log")
    ax.set_xlabel("relative error")
    ax.set_ylabel("logical GFLOP per second")
    ax.set_title("Recorded dense accuracy and throughput frontier")
    ax.grid(alpha=0.25)
    ax.legend()
    save(fig, "14_accuracy_frontier")


def block_speedup(df: pd.DataFrame) -> None:
    rows = df[(df["suite"] == "block_diagonal_matmat") & (df["method"] == "gpu_packet_torch_bmm")].sort_values("n")
    fig, ax = plt.subplots(figsize=(7.3, 4.6))
    ax.plot(rows["n"], rows["speedup_vs_gpu_dense"], marker="o", label="against GPU dense")
    ax.plot(rows["n"], rows["speedup_vs_cpu_dense"], marker="o", label="against CPU dense")
    ax.set_yscale("log")
    ax.set_xlabel("dimension")
    ax.set_ylabel("measured speedup")
    ax.set_title("Equal block packet application")
    ax.grid(alpha=0.25)
    ax.legend()
    save(fig, "15_block_diagonal_speedup")


def bdlr_timings(df: pd.DataFrame) -> None:
    methods = ["gpu_dense_torch_float32", "gpu_packet_torch", "gpu_packet_cuda_graph", "cpu_packet_bdlr"]
    rows = df[(df["suite"] == "bdlr_matmat") & df["method"].isin(methods)].copy()
    fig, ax = plt.subplots(figsize=(7.7, 4.8))
    for method, group in rows.groupby("method"):
        group = group.sort_values("n")
        label = method.replace("gpu_", "").replace("cpu_", "").replace("_", " ")
        ax.plot(group["n"], group["median_ms"], marker="o", label=label)
    ax.set_yscale("log")
    ax.set_xlabel("dimension")
    ax.set_ylabel("median time in milliseconds")
    ax.set_title("Block diagonal plus low rank application")
    ax.grid(alpha=0.25)
    ax.legend()
    save(fig, "16_bdlr_timings")


def output_contracts(df: pd.DataFrame) -> None:
    rows = df[df["suite"] == "bdlr_product"].copy()
    pivot = rows.pivot_table(index="n", columns="method", values="median_ms", aggfunc="first")
    methods = [m for m in ["gpu_dense_torch_float32", "gpu_packet_compressed_product", "gpu_packet_product_materialized", "cpu_packet_compressed_product"] if m in pivot.columns]
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    x = np.arange(len(pivot.index))
    width = 0.82 / len(methods)
    for j, method in enumerate(methods):
        label = method.replace("gpu_", "").replace("cpu_", "").replace("_", " ")
        ax.bar(x + (j - (len(methods) - 1) / 2) * width, pivot[method], width=width, label=label)
    ax.set_xticks(x, [str(int(v)) for v in pivot.index])
    ax.set_yscale("log")
    ax.set_xlabel("dimension")
    ax.set_ylabel("median time in milliseconds")
    ax.set_title("Compressed factors and explicit matrices are different outputs")
    ax.legend(fontsize=7.4)
    save(fig, "17_output_contract_timings")


def discovery(df: pd.DataFrame) -> None:
    rows = df[(df["suite"] == "hidden_permuted_blocks") & (df["method"] == "cpu_packet_detect_then_apply")].sort_values("n")
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    dense = []
    for cid in rows["case_id"]:
        dense.append(df[(df["case_id"] == cid) & (df["method"] == "cpu_dense_numpy")]["median_ms"].iloc[0])
    ax.plot(rows["n"], rows["structure_discovery_ms"], marker="o", label="one time discovery")
    ax.plot(rows["n"], rows["median_ms"], marker="o", label="packet application")
    ax.plot(rows["n"], dense, marker="o", label="dense application")
    for _, row in rows.iterrows():
        ax.annotate(f"reuse {int(row['reuse_count'])}", (row["n"], row["structure_discovery_ms"]), xytext=(4, 4), textcoords="offset points")
    ax.set_yscale("log")
    ax.set_xlabel("dimension")
    ax.set_ylabel("time in milliseconds")
    ax.set_title("Structure discovery must be amortized")
    ax.grid(alpha=0.25)
    ax.legend()
    save(fig, "18_discovery_amortization")


def transfer_pipeline(df: pd.DataFrame) -> None:
    rows = df[df["suite"] == "transfer_pipeline"].sort_values("median_ms")
    labels = rows["method"].str.replace("gpu_", "", regex=False).str.replace("_", " ", regex=False)
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.barh(labels, rows["median_ms"])
    ax.set_xlabel("median time in milliseconds")
    ax.set_title("Timing scope changes the comparison")
    save(fig, "19_transfer_pipeline")


def negative_controls(df: pd.DataFrame) -> None:
    specs = [
        ("Strassen", "strassen", "cpu_strassen_leaf_128", "cpu_dense_numpy"),
        ("recursive HODLR", "hodlr", "gpu_packet_hodlr", "gpu_dense_torch_float32"),
        ("iterative refinement", "iterative_refinement", "gpu_float32_iterative_refinement", "gpu_dense_solve_float64"),
        ("two stream pipeline", "transfer_pipeline", "gpu_double_buffer_two_gemms", "gpu_serial_two_gemms"),
    ]
    labels, ratios = [], []
    for label, suite, method, baseline_method in specs:
        group = df[(df["suite"] == suite) & (df["method"] == method)]
        row = group.iloc[-1]
        base = df[(df["suite"] == suite) & (df["method"] == baseline_method)]
        if suite in {"strassen", "hodlr"}:
            base = base[base["case_id"] == row["case_id"]]
        baseline = base.iloc[-1]
        labels.append(label)
        ratios.append(row["median_ms"] / baseline["median_ms"])
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.bar(labels, ratios)
    ax.axhline(1.0, linestyle=":")
    ax.set_ylabel("candidate time divided by matched baseline time")
    ax.set_title("Retained negative controls")
    ax.tick_params(axis="x", rotation=18)
    save(fig, "20_negative_controls")


def best_speedups(df: pd.DataFrame) -> None:
    eligible = df[df["speedup_vs_gpu_dense"].notna() & (df["speedup_vs_gpu_dense"] > 0)].copy()
    best = eligible.sort_values("speedup_vs_gpu_dense").groupby("suite", as_index=False).tail(1)
    best = best.sort_values("speedup_vs_gpu_dense", ascending=True).tail(12)
    fig, ax = plt.subplots(figsize=(7.7, 5.5))
    ax.barh(best["suite"].str.replace("_", " ", regex=False), best["speedup_vs_gpu_dense"])
    ax.set_xscale("log")
    ax.set_xlabel("best matched speedup against GPU dense")
    ax.set_title("Measured packet gains vary strongly by representation")
    save(fig, "21_best_gpu_speedups")


def contract_counts(df: pd.DataFrame) -> None:
    counts = df.groupby(["timing_scope", "output_contract"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(8.2, 4.9))
    bottom = np.zeros(len(counts))
    for contract in counts.columns:
        values = counts[contract].to_numpy()
        ax.bar(np.arange(len(counts)), values, bottom=bottom, label=str(contract).replace("_", " "))
        bottom += values
    ax.set_xticks(np.arange(len(counts)), [str(x).replace("_", " ") for x in counts.index], rotation=20, ha="right")
    ax.set_ylabel("recorded rows")
    ax.set_title("The corpus separates timing scope from output contract")
    ax.legend()
    save(fig, "22_benchmark_contracts")


def main() -> None:
    df = frame()
    architecture()
    packet_ir()
    arithmetic_reduction()
    roofline_schematic()
    bdlr_structure()
    recompression()
    graph_paths()
    triangular_schedule()
    preconditioner()
    precision()
    compiler_tree()
    compiler_frontier()
    dense_throughput(df)
    accuracy_frontier(df)
    block_speedup(df)
    bdlr_timings(df)
    output_contracts(df)
    discovery(df)
    transfer_pipeline(df)
    negative_controls(df)
    best_speedups(df)
    contract_counts(df)


if __name__ == "__main__":
    main()
