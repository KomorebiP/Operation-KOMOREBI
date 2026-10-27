from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .benchmark_data import best_speedups, load_benchmark, rows_frame
from .complexity import ideal_bdlr_speedup, representation_reduction
from .experiments import run_finite_experiments
from .operators import BDLRMatrix, BlockDiagonal


def _save(fig: plt.Figure, out: Path, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{stem}.png", dpi=220, bbox_inches="tight")
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def make_visuals(benchmark_path: str | Path, output_dir: str | Path) -> list[str]:
    out = Path(output_dir)
    data = load_benchmark(benchmark_path)
    frame = rows_frame(data)
    stems: list[str] = []

    # 1. Common architecture.
    fig, ax = plt.subplots(figsize=(11.0, 3.0))
    labels = ["seed / data", "packet projectors", "structured operator", "GPU schedule", "error certificate", "reconstruction"]
    x = np.arange(len(labels))
    ax.scatter(x, np.zeros_like(x), s=260)
    for i, label in enumerate(labels):
        ax.text(i, 0.17 if i % 2 == 0 else -0.20, label, ha="center", va="center", fontsize=11)
        if i + 1 < len(labels):
            ax.annotate("", xy=(i + 1 - 0.13, 0), xytext=(i + 0.13, 0), arrowprops={"arrowstyle": "->"})
    ax.set_xlim(-0.45, len(labels) - 0.55)
    ax.set_ylim(-0.38, 0.38)
    ax.axis("off")
    ax.set_title("Packet algorithm realization of the common seed-calculus chain")
    _save(fig, out, "01_packet_gpu_architecture")
    stems.append("01_packet_gpu_architecture")

    # 2. Matrix packet structure.
    rng = np.random.default_rng(4)
    sizes = (12, 12, 12, 12, 12)
    blocks = tuple(rng.normal(size=(s, s)) for s in sizes)
    diagonal = BlockDiagonal(blocks)
    u = rng.normal(size=(sum(sizes), 3)) * 0.3
    v = rng.normal(size=(sum(sizes), 3)) * 0.3
    matrix = BDLRMatrix(diagonal, u, v).materialize()
    fig, ax = plt.subplots(figsize=(6.6, 5.8))
    image = ax.imshow(matrix, aspect="equal")
    fig.colorbar(image, ax=ax, label="entry")
    ax.set_title("Block-diagonal packets plus a global low-rank transfer")
    ax.set_xlabel("input coordinate")
    ax.set_ylabel("output coordinate")
    _save(fig, out, "02_bdlr_structure")
    stems.append("02_bdlr_structure")

    # 3. Ideal arithmetic speedup.
    ns = np.array([512, 1024, 2048, 4096, 8192, 16384])
    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    for block, rank in [(64, 0), (64, 8), (128, 8), (64, 32)]:
        ax.plot(ns, [ideal_bdlr_speedup(int(n), block, rank) for n in ns], marker="o", label=f"b={block}, r={rank}")
    ax.set_xlabel("matrix dimension n")
    ax.set_ylabel("ideal dense / packet arithmetic ratio")
    ax.set_title("Arithmetic removed by packet structure")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "03_ideal_packet_speedup")
    stems.append("03_ideal_packet_speedup")

    # 4. Representation memory reduction.
    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    for block, rank in [(64, 8), (128, 8), (64, 32)]:
        ax.plot(ns, [representation_reduction(int(n), block, rank) for n in ns], marker="o", label=f"b={block}, r={rank}")
    ax.set_xlabel("matrix dimension n")
    ax.set_ylabel("dense / BDLR stored entries")
    ax.set_title("Representation-memory reduction")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "04_representation_memory_reduction")
    stems.append("04_representation_memory_reduction")

    # 5. Dense GPU throughput.
    dense = frame[(frame["suite"] == "dense_gemm") & frame["method"].astype(str).str.startswith("gpu_dense")].copy()
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    for method, group in dense.groupby("method"):
        group = group.sort_values("n")
        ax.plot(group["n"], group["gflops_logical"], marker="o", label=method.replace("gpu_dense_torch_", ""))
    ax.set_xlabel("n")
    ax.set_ylabel("logical GFLOP/s")
    ax.set_title("Measured device-resident dense throughput")
    ax.legend(ncol=2)
    ax.grid(alpha=0.25)
    _save(fig, out, "05_dense_gpu_throughput")
    stems.append("05_dense_gpu_throughput")

    # 6. Accuracy-performance frontier for dense source float32 cases.
    frontier = dense[(dense["relative_error"].notna()) & (dense["relative_error"] > 0)].copy()
    fig, ax = plt.subplots(figsize=(7.6, 5.2))
    for method, group in frontier.groupby("method"):
        ax.scatter(group["relative_error"], group["gflops_logical"], s=60, label=method.replace("gpu_dense_torch_", ""))
    ax.set_xscale("log")
    ax.set_xlabel("relative error")
    ax.set_ylabel("logical GFLOP/s")
    ax.set_title("Measured dense accuracy-performance frontier")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "06_accuracy_performance_frontier")
    stems.append("06_accuracy_performance_frontier")

    # 7. Block diagonal measured speedup.
    bd = frame[(frame["suite"] == "block_diagonal_matmat") & (frame["method"] == "gpu_packet_torch_bmm")].sort_values("n")
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.plot(bd["n"], bd["speedup_vs_gpu_dense"], marker="o", label="vs GPU dense")
    ax.plot(bd["n"], bd["speedup_vs_cpu_dense"], marker="o", label="vs CPU dense")
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("measured speedup")
    ax.set_title("Equal-block packet multiplication")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "07_block_diagonal_speedup")
    stems.append("07_block_diagonal_speedup")

    # 8. BDLR implementations.
    bdlr = frame[(frame["suite"] == "bdlr_matmat") & frame["method"].isin(["gpu_dense_torch_float32", "gpu_packet_torch", "gpu_packet_cuda_graph", "cpu_packet_bdlr"])].copy()
    fig, ax = plt.subplots(figsize=(8.2, 5.1))
    for method, group in bdlr.groupby("method"):
        group = group.sort_values("n")
        ax.plot(group["n"], group["median_ms"], marker="o", label=method.replace("gpu_", "").replace("cpu_", ""))
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("median time (ms)")
    ax.set_title("BDLR application: representation and launch strategy")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "08_bdlr_timings")
    stems.append("08_bdlr_timings")

    # 9. Compressed vs materialized BDLR product.
    prod = frame[frame["suite"] == "bdlr_product"].copy()
    pivot = prod.pivot_table(index="n", columns="method", values="median_ms", aggfunc="first")
    fig, ax = plt.subplots(figsize=(8.4, 5.1))
    methods = [m for m in ["gpu_dense_torch_float32", "gpu_packet_compressed_product", "gpu_packet_product_materialized", "cpu_packet_compressed_product"] if m in pivot.columns]
    x = np.arange(len(pivot.index))
    width = 0.8 / max(1, len(methods))
    for j, method in enumerate(methods):
        ax.bar(x + (j - (len(methods)-1)/2)*width, pivot[method], width=width, label=method.replace("gpu_", "").replace("cpu_", ""))
    ax.set_xticks(x, [str(v) for v in pivot.index])
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("median time (ms)")
    ax.set_title("Output contract changes the correct comparison")
    ax.legend(fontsize=8)
    _save(fig, out, "09_compressed_vs_materialized")
    stems.append("09_compressed_vs_materialized")

    # 10. Structure discovery amortization.
    hidden = frame[(frame["suite"] == "hidden_permuted_blocks") & (frame["method"] == "cpu_packet_detect_then_apply")].sort_values("n")
    fig, ax = plt.subplots(figsize=(7.8, 4.9))
    ax.plot(hidden["n"], hidden["structure_discovery_ms"], marker="o", label="one-time discovery")
    ax.plot(hidden["n"], hidden["median_ms"], marker="o", label="packet apply")
    ax.plot(hidden["n"], [frame[(frame["case_id"] == cid) & (frame["method"] == "cpu_dense_numpy")]["median_ms"].iloc[0] for cid in hidden["case_id"]], marker="o", label="dense apply")
    for _, row in hidden.iterrows():
        ax.annotate(f"R={int(row['reuse_count'])}", (row["n"], row["structure_discovery_ms"]), xytext=(4, 4), textcoords="offset points")
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("time (ms)")
    ax.set_title("Discovery cost and measured reuse threshold")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "10_structure_discovery_amortization")
    stems.append("10_structure_discovery_amortization")

    # 11. Transform crossover.
    fwht = frame[frame["suite"] == "walsh_hadamard"].copy()
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    for method, group in fwht.groupby("method"):
        group = group.sort_values("n")
        ax.plot(group["n"], group["median_ms"], marker="o", label=method.replace("_packet_fwht", ""))
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("transform length")
    ax.set_ylabel("median time (ms)")
    ax.set_title("The GPU becomes favorable only after the transform is large enough")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "11_fwht_crossover")
    stems.append("11_fwht_crossover")

    # 12. Negative controls.
    negative_rows = []
    for suite, methods in {
        "strassen": ["cpu_strassen_leaf_128"],
        "hodlr": ["gpu_packet_hodlr"],
        "iterative_refinement": ["gpu_float32_iterative_refinement"],
        "transfer_pipeline": ["gpu_double_buffer_two_gemms"],
    }.items():
        for method in methods:
            group = frame[(frame["suite"] == suite) & (frame["method"] == method)]
            if group.empty:
                continue
            row = group.iloc[-1]
            if suite == "transfer_pipeline":
                baseline = frame[(frame["suite"] == suite) & (frame["method"] == "gpu_serial_two_gemms")].iloc[0]
            elif suite == "iterative_refinement":
                baseline = frame[(frame["suite"] == suite) & (frame["method"] == "gpu_dense_solve_float64")].iloc[0]
            elif suite == "hodlr":
                baseline = frame[(frame["case_id"] == row["case_id"]) & (frame["method"] == "gpu_dense_torch_float32")].iloc[0]
            else:
                baseline = frame[(frame["case_id"] == row["case_id"]) & (frame["method"] == "cpu_dense_numpy")].iloc[0]
            negative_rows.append((suite, row["median_ms"] / baseline["median_ms"]))
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    labels = [x[0] for x in negative_rows]
    ratios = [x[1] for x in negative_rows]
    ax.bar(labels, ratios)
    ax.axhline(1.0, linestyle="--")
    ax.set_ylabel("candidate time / matched baseline time")
    ax.set_title("Retained negative controls")
    ax.tick_params(axis="x", rotation=20)
    _save(fig, out, "12_negative_controls")
    stems.append("12_negative_controls")

    # 13. Transfer pipeline.
    pipe = frame[frame["suite"] == "transfer_pipeline"].sort_values("median_ms")
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    labels = pipe["method"].str.replace("gpu_", "", regex=False)
    ax.barh(labels, pipe["median_ms"])
    ax.set_xlabel("median time (ms)")
    ax.set_title("Device residency, graph replay, and end-to-end transfer")
    _save(fig, out, "13_transfer_pipeline")
    stems.append("13_transfer_pipeline")

    # 14-15. Best packet speedups by suite.
    for baseline, stem, title in [
        ("gpu_dense", "14_best_packet_speedup_gpu", "Best matched packet speedup versus GPU dense"),
        ("cpu_dense", "15_best_packet_speedup_cpu", "Best matched packet speedup versus CPU dense"),
    ]:
        best = best_speedups(frame, baseline).head(12).sort_values(f"speedup_vs_{baseline}")
        fig, ax = plt.subplots(figsize=(8.8, 6.0))
        ax.barh(best["suite"], best[f"speedup_vs_{baseline}"])
        ax.set_xscale("log")
        ax.set_xlabel("measured speedup")
        ax.set_title(title)
        for y, value in enumerate(best[f"speedup_vs_{baseline}"]):
            ax.text(value, y, f" {value:.2f}x", va="center", fontsize=9)
        _save(fig, out, stem)
        stems.append(stem)

    # 16. Precision allocation model.
    finite = run_finite_experiments()
    tolerances = np.array(finite["finite_certificates"]["optimal_tolerances"])
    fig, ax = plt.subplots(figsize=(7.7, 4.8))
    ax.bar(np.arange(len(tolerances)), tolerances)
    ax.set_yscale("log")
    ax.set_xlabel("packet")
    ax.set_ylabel("allocated relative tolerance")
    ax.set_title("Sensitivity-weighted precision allocation")
    _save(fig, out, "16_precision_allocation")
    stems.append("16_precision_allocation")

    # 17. Preconditioned CG convergence.
    rng = np.random.default_rng(11)
    blocks = []
    for _ in range(8):
        a = rng.normal(size=(12, 12))
        blocks.append(a.T @ a + 4 * np.eye(12))
    d = BlockDiagonal(tuple(blocks))
    n = d.n
    coupling = rng.normal(size=(n, n))
    coupling = 0.015 * (coupling + coupling.T)
    a = d.materialize() + coupling
    min_eig = np.linalg.eigvalsh(a).min()
    if min_eig <= 0:
        a += (1 - min_eig) * np.eye(n)
    b = rng.normal(size=n)
    from .krylov import conjugate_gradient
    plain = conjugate_gradient(lambda x: a @ x, b, tol=1e-10, maxiter=300)
    packet = conjugate_gradient(lambda x: a @ x, b, precondition=d.solve, tol=1e-10, maxiter=300)
    fig, ax = plt.subplots(figsize=(7.7, 4.8))
    ax.semilogy(plain.residual_norms, label="unpreconditioned")
    ax.semilogy(packet.residual_norms, label="packet block-Jacobi")
    ax.set_xlabel("iteration")
    ax.set_ylabel("residual norm")
    ax.set_title("Packet preconditioning of a weakly coupled system")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "17_packet_preconditioner")
    stems.append("17_packet_preconditioner")

    # 18. Benchmark contract matrix.
    contract_counts = frame.groupby(["timing_scope", "output_contract"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(9.0, 5.8))
    image = ax.imshow(contract_counts.values, aspect="auto")
    fig.colorbar(image, ax=ax, label="row count")
    ax.set_xticks(np.arange(len(contract_counts.columns)), contract_counts.columns, rotation=35, ha="right")
    ax.set_yticks(np.arange(len(contract_counts.index)), contract_counts.index)
    ax.set_title("Timing scope and output contract are part of the mathematical comparison")
    _save(fig, out, "18_benchmark_contracts")
    stems.append("18_benchmark_contracts")

    return stems
