from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np


@dataclass(frozen=True)
class PrismConfig:
    name: str = "Komorebi PRISM-1"
    clock_ghz: float = 1.5
    compute_chiplets: int = 4
    packet_streaming_multiprocessors_per_chiplet: int = 16
    execution_groups_per_psm: int = 4
    mac_rows: int = 16
    mac_cols: int = 16
    local_sram_kib_per_execution_group: int = 512
    shared_sram_mib_per_chiplet: int = 16
    descriptor_cache_kib_per_psm: int = 128
    transform_engines_per_chiplet: int = 8
    solver_engines_per_chiplet: int = 4
    exact_arithmetic_clusters_per_chiplet: int = 1
    hbm4_stacks: int = 4
    hbm4_capacity_gib_per_stack: int = 36
    hbm4_bandwidth_tbps_per_stack: float = 2.8
    package_network_tbps: float = 16.0
    host_bidirectional_gbps: float = 512.0
    tdp_w: int = 500
    ucie_gtps: int = 64

    @property
    def psms(self) -> int:
        return self.compute_chiplets * self.packet_streaming_multiprocessors_per_chiplet

    @property
    def execution_groups_per_chiplet(self) -> int:
        return self.packet_streaming_multiprocessors_per_chiplet * self.execution_groups_per_psm

    @property
    def execution_groups(self) -> int:
        return self.psms * self.execution_groups_per_psm

    @property
    def tiles(self) -> int:
        return self.execution_groups

    @property
    def total_hbm_gib(self) -> int:
        return self.hbm4_stacks * self.hbm4_capacity_gib_per_stack

    @property
    def total_hbm_tbps(self) -> float:
        return self.hbm4_stacks * self.hbm4_bandwidth_tbps_per_stack

    @property
    def total_sram_mib(self) -> float:
        local = self.execution_groups * self.local_sram_kib_per_execution_group / 1024
        shared = self.compute_chiplets * self.shared_sram_mib_per_chiplet
        return local + shared

    @property
    def fp16_tflops(self) -> float:
        macs = self.execution_groups * self.mac_rows * self.mac_cols
        return macs * 2 * self.clock_ghz * 1e9 / 1e12

    @property
    def fp32_tflops(self) -> float:
        return self.fp16_tflops / 2

    @property
    def fp64_tflops(self) -> float:
        return self.fp16_tflops / 8


@dataclass(frozen=True)
class PacketDescriptor:
    packet_id: int
    parent_id: int
    atlas_id: int
    selector_kind: str
    shape: tuple[int, ...]
    base_address: int
    bytes_per_element: int
    precision: str
    error_budget: float


@dataclass(frozen=True)
class TransferDescriptor:
    edge_id: int
    src_packet: int
    dst_packet: int
    kernel_kind: str
    rows: int
    cols: int
    rank: int
    precision: str
    sensitivity: float
    dependency_token: int


REPRESENTATION_FORMS = (
    "explicit_dense",
    "block_diagonal",
    "block_sparse",
    "low_rank",
    "bdlr",
    "kronecker",
    "sparse_factor_chain",
    "transform_domain",
    "packet_graph",
)

OUTPUT_CONTRACTS = (
    "apply",
    "compressed_operator",
    "factor_graph",
    "transform_plan",
    "explicit_array",
)


@dataclass(frozen=True)
class PlanChoice:
    name: str
    output_form: str
    local_cost: float
    local_error: float = 0.0
    children: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlanResult:
    node: str
    choice: str
    output_form: str
    objective: float
    local_cost: float
    local_error: float
    children: tuple["PlanResult", ...]


@dataclass(frozen=True)
class Estimate:
    workload: str
    flops: float
    bytes_moved: float
    arithmetic_intensity: float
    compute_time_us: float
    memory_time_us: float
    schedule_time_us: float
    total_time_us: float
    energy_mj: float
    notes: str


def packet_slices(sizes: Sequence[int]) -> tuple[slice, ...]:
    out: list[slice] = []
    start = 0
    for size in sizes:
        if size <= 0:
            raise ValueError("packet sizes must be positive")
        out.append(slice(start, start + int(size)))
        start += int(size)
    return tuple(out)


def residue_project(x: np.ndarray, order: int, phase: int) -> np.ndarray:
    arr = np.asarray(x)
    out = np.zeros_like(arr)
    mask = np.arange(arr.size) % order == phase % order
    out[mask] = arr[mask]
    return out


def polyphase_analyze(x: np.ndarray, order: int) -> list[np.ndarray]:
    arr = np.asarray(x)
    return [arr[r::order].copy() for r in range(order)]


def polyphase_synthesize(channels: Sequence[np.ndarray], length: int | None = None) -> np.ndarray:
    order = len(channels)
    if order == 0:
        raise ValueError("channels cannot be empty")
    arrays = [np.asarray(c) for c in channels]
    natural = max(order * len(c) + r for r, c in enumerate(arrays))
    n = natural if length is None else length
    out = np.zeros(n, dtype=np.result_type(*arrays))
    for r, channel in enumerate(arrays):
        positions = np.arange(r, n, order)
        count = min(len(channel), len(positions))
        out[positions[:count]] = channel[:count]
    return out


def haar_analyze(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(x, dtype=float)
    if arr.size % 2:
        raise ValueError("Haar analysis requires even length")
    s = math.sqrt(2.0)
    return (arr[0::2] + arr[1::2]) / s, (arr[0::2] - arr[1::2]) / s


def haar_synthesize(low: np.ndarray, high: np.ndarray) -> np.ndarray:
    low = np.asarray(low, dtype=float)
    high = np.asarray(high, dtype=float)
    if low.shape != high.shape:
        raise ValueError("Haar channels must match")
    s = math.sqrt(2.0)
    out = np.empty(low.size * 2)
    out[0::2] = (low + high) / s
    out[1::2] = (low - high) / s
    return out


def block_diagonal_apply(blocks: Sequence[np.ndarray], x: np.ndarray) -> np.ndarray:
    sizes = [b.shape[0] for b in blocks]
    slices = packet_slices(sizes)
    x = np.asarray(x)
    out = np.empty_like(x, dtype=np.result_type(x, *blocks))
    for slc, block in zip(slices, blocks, strict=True):
        out[slc] = block @ x[slc]
    return out


def bdlr_apply(blocks: Sequence[np.ndarray], u: np.ndarray, v: np.ndarray, x: np.ndarray) -> np.ndarray:
    return block_diagonal_apply(blocks, x) + u @ (v.T.conj() @ x)


def materialize_bdlr(blocks: Sequence[np.ndarray], u: np.ndarray, v: np.ndarray) -> np.ndarray:
    sizes = [b.shape[0] for b in blocks]
    total = sum(sizes)
    out = np.zeros((total, total), dtype=np.result_type(*blocks, u, v))
    for slc, block in zip(packet_slices(sizes), blocks, strict=True):
        out[slc, slc] = block
    return out + u @ v.T.conj()


def output_contract_allows(output_form: str, contract: str) -> bool:
    if output_form not in REPRESENTATION_FORMS:
        raise ValueError(f"unknown output form {output_form}")
    if contract not in OUTPUT_CONTRACTS:
        raise ValueError(f"unknown output contract {contract}")
    if contract == "apply":
        return True
    if contract == "explicit_array":
        return output_form == "explicit_dense"
    if contract == "transform_plan":
        return output_form in {"transform_domain", "sparse_factor_chain", "packet_graph"}
    if contract == "factor_graph":
        return output_form in {
            "block_diagonal",
            "block_sparse",
            "low_rank",
            "bdlr",
            "kronecker",
            "sparse_factor_chain",
            "transform_domain",
            "packet_graph",
        }
    return True


def pmr_plan(
    root: str,
    options: dict[str, tuple[PlanChoice, ...]],
    error_weight: float,
    output_contract: str,
) -> PlanResult:
    """Bellman planner on a finite mixed-representation tree."""
    if error_weight < 0:
        raise ValueError("error weight must be nonnegative")
    memo: dict[tuple[str, bool], PlanResult] = {}
    active: set[str] = set()

    def solve(node: str, is_root: bool) -> PlanResult:
        key = (node, is_root)
        if key in memo:
            return memo[key]
        if node in active:
            raise ValueError("candidate plan graph must be acyclic")
        if node not in options or not options[node]:
            raise ValueError(f"no candidate representations for {node}")
        active.add(node)
        candidates: list[PlanResult] = []
        for choice in options[node]:
            if choice.output_form not in REPRESENTATION_FORMS:
                raise ValueError(f"unknown representation {choice.output_form}")
            if is_root and not output_contract_allows(choice.output_form, output_contract):
                continue
            child_results = tuple(solve(child, False) for child in choice.children)
            objective = (
                choice.local_cost
                + error_weight * choice.local_error * choice.local_error
                + sum(child.objective for child in child_results)
            )
            candidates.append(
                PlanResult(
                    node=node,
                    choice=choice.name,
                    output_form=choice.output_form,
                    objective=float(objective),
                    local_cost=float(choice.local_cost),
                    local_error=float(choice.local_error),
                    children=child_results,
                )
            )
        active.remove(node)
        if not candidates:
            raise ValueError(f"no representation satisfies output contract {output_contract}")
        best = min(candidates, key=lambda result: (result.objective, result.choice))
        memo[key] = best
        return best

    return solve(root, True)


def measured_cuda_baselines() -> dict[str, float | str]:
    """Measured structured CUDA rows imported from the prior packet-GPU study."""
    return {
        "hardware": "NVIDIA GeForce RTX 3070 Ti Laptop GPU",
        "equal_block_packet_ms": 0.046032,
        "equal_block_speedup_vs_gpu_dense": 14.8919,
        "equal_block_speedup_vs_cpu_dense": 235.7404,
        "bdlr_standard_packet_ms": 0.097280,
        "bdlr_graph_packet_ms": 0.079872,
        "bdlr_speedup_vs_gpu_dense": 10.9355,
        "bdlr_speedup_vs_cpu_dense": 153.6527,
        "bdlr_graph_replay_gain": 0.097280 / 0.079872,
        "compressed_product_ms": 0.1582,
        "materialized_product_ms": 0.5073,
        "compressed_output_gain": 0.5073 / 0.1582,
        "measured_rows": 154.0,
    }


def gain_decomposition() -> dict[str, float | str]:
    cuda = measured_cuda_baselines()
    return {
        "representation_reduction_bdlr": 102.4,
        "measured_packet_gpu_gain_vs_dense_gpu": float(cuda["bdlr_speedup_vs_gpu_dense"]),
        "measured_cuda_graph_gain_same_representation": float(cuda["bdlr_graph_replay_gain"]),
        "measured_compressed_output_gain": float(cuda["compressed_output_gain"]),
        "note": "Factors are reported separately and are not multiplied unless timing scope and output contract match.",
    }


def topological_order(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> tuple[str, ...]:
    nodes = tuple(sorted(set(nodes)))
    edge_list = tuple(edges)
    indegree = {n: 0 for n in nodes}
    outgoing = {n: [] for n in nodes}
    for a, b in edge_list:
        indegree[b] += 1
        outgoing[a].append(b)
    ready = sorted(n for n, d in indegree.items() if d == 0)
    order: list[str] = []
    while ready:
        n = ready.pop(0)
        order.append(n)
        for b in sorted(outgoing[n]):
            indegree[b] -= 1
            if indegree[b] == 0:
                ready.append(b)
                ready.sort()
    if len(order) != len(nodes):
        raise ValueError("graph is cyclic")
    return tuple(order)


def substitute_task(
    nodes: set[str],
    edges: set[tuple[str, str]],
    vertex: str,
    local_nodes: set[str],
    local_edges: set[tuple[str, str]],
    entries: set[str],
    exits: set[str],
) -> tuple[set[str], set[tuple[str, str]], tuple[str, ...]]:
    old_order = topological_order(nodes, edges)
    local_order = topological_order(local_nodes, local_edges)
    preds = {a for a, b in edges if b == vertex}
    succs = {b for a, b in edges if a == vertex}
    context_edges = {e for e in edges if vertex not in e}
    new_edges = set(context_edges) | set(local_edges)
    new_edges |= {(p, e) for p in preds for e in entries}
    new_edges |= {(x, s) for x in exits for s in succs}
    new_nodes = (set(nodes) - {vertex}) | set(local_nodes)
    idx = old_order.index(vertex)
    spliced = old_order[:idx] + local_order + old_order[idx + 1 :]
    if tuple(n for n in spliced if n in nodes - {vertex}) != tuple(n for n in old_order if n != vertex):
        raise RuntimeError("remote order changed")
    if set(spliced) != new_nodes:
        raise RuntimeError("spliced order has wrong nodes")
    positions = {n: i for i, n in enumerate(spliced)}
    if not all(positions[a] < positions[b] for a, b in new_edges):
        raise RuntimeError("spliced order is not topological")
    return new_nodes, new_edges, spliced


def peak_flops(config: PrismConfig, precision: str) -> float:
    p = precision.lower()
    if p in {"fp16", "bf16"}:
        return config.fp16_tflops * 1e12
    if p in {"fp32", "tf32"}:
        return config.fp32_tflops * 1e12
    if p == "fp64":
        return config.fp64_tflops * 1e12
    raise ValueError(f"unsupported precision {precision}")


def roofline_estimate(
    config: PrismConfig,
    workload: str,
    flops: float,
    bytes_moved: float,
    precision: str = "fp32",
    graph_regions: int = 1,
    power_w: float | None = None,
    notes: str = "",
    use_sram: bool = False,
) -> Estimate:
    peak = peak_flops(config, precision)
    bandwidth = (config.package_network_tbps if use_sram else config.total_hbm_tbps) * 1e12
    efficiency_compute = 0.72 if use_sram else 0.62
    efficiency_bw = 0.72 if use_sram else 0.74
    compute_s = flops / (peak * efficiency_compute)
    memory_s = bytes_moved / (bandwidth * efficiency_bw)
    schedule_s = graph_regions * 0.32e-6
    total_s = max(compute_s, memory_s) + schedule_s
    watts = float(config.tdp_w if power_w is None else power_w)
    return Estimate(
        workload=workload,
        flops=flops,
        bytes_moved=bytes_moved,
        arithmetic_intensity=flops / max(bytes_moved, 1.0),
        compute_time_us=compute_s * 1e6,
        memory_time_us=memory_s * 1e6,
        schedule_time_us=schedule_s * 1e6,
        total_time_us=total_s * 1e6,
        energy_mj=watts * total_s * 1e3,
        notes=notes,
    )


def dense_apply_estimate(config: PrismConfig, n: int, q: int, itemsize: int = 4) -> Estimate:
    flops = 2.0 * n * n * q
    bytes_moved = itemsize * (n * n + 2 * n * q)
    return roofline_estimate(
        config,
        "Dense apply baseline",
        flops,
        bytes_moved,
        precision="fp32",
        graph_regions=1,
        notes="Dense matrix is materialized and read once",
    )


def bdlr_estimate(config: PrismConfig, n: int, b: int, r: int, q: int, itemsize: int = 4) -> Estimate:
    flops = 2.0 * q * n * (b + 2 * r)
    bytes_moved = itemsize * (n * (b + 2 * r) + 3 * n * q + 2 * r * q)
    return roofline_estimate(
        config,
        "Packet BDLR apply",
        flops,
        bytes_moved,
        precision="fp32",
        graph_regions=4,
        notes="Factor-first execution with block diagonal and two low-rank contractions",
        use_sram=True,
    )


def block_sparse_estimate(config: PrismConfig, blocks: int, b: int, degree: int, q: int, itemsize: int = 4) -> Estimate:
    n = blocks * b
    edge_count = blocks * degree
    flops = 2.0 * edge_count * b * b * q
    bytes_moved = itemsize * (edge_count * b * b + 2 * n * q)
    return roofline_estimate(
        config,
        "Regular block-sparse transfer",
        flops,
        bytes_moved,
        precision="fp32",
        graph_regions=max(1, degree),
        notes="Edges are grouped by equal shape and scheduled as batches",
        use_sram=True,
    )


def multi_atlas_estimate(config: PrismConfig, pixels: int, atlases: int = 5, itemsize: int = 4) -> tuple[Estimate, Estimate]:
    logn = math.log2(pixels)
    transform_flops = 5.0 * pixels * logn + 8.0 * pixels
    total_flops = atlases * transform_flops
    baseline_passes = 3 * atlases + 2
    prism_passes = 4
    baseline_bytes = baseline_passes * pixels * itemsize
    prism_bytes = prism_passes * pixels * itemsize
    baseline = roofline_estimate(
        config,
        "Separate multi-atlas kernels",
        total_flops,
        baseline_bytes,
        precision="fp32",
        graph_regions=baseline_passes,
        notes="Each atlas writes an intermediate array to HBM",
    )
    prism = roofline_estimate(
        config,
        "Fused multi-atlas pipeline",
        total_flops,
        prism_bytes,
        precision="fp32",
        graph_regions=3,
        notes="Analysis, packet selection, feature reduction, and synthesis are fused",
        use_sram=True,
    )
    return baseline, prism


def edge_recovery_estimate(config: PrismConfig, samples: int, max_jumps: int, itemsize: int = 8) -> tuple[Estimate, Estimate]:
    fft_flops = 5.0 * samples * math.log2(samples)
    hankel = max_jumps + 1
    svd_flops = 20.0 * hankel**3
    vandermonde_flops = 4.0 * max_jumps**3
    root_flops = 250.0 * max_jumps**2
    flops = fft_flops + svd_flops + vandermonde_flops + root_flops
    baseline_bytes = itemsize * (10 * samples + 8 * hankel**2)
    prism_bytes = itemsize * (3 * samples + 4 * hankel**2)
    baseline = roofline_estimate(
        config,
        "General accelerator edge recovery",
        flops,
        baseline_bytes,
        precision="fp64",
        graph_regions=12,
        power_w=420,
        notes="FFT and small solvers run as separate kernels",
    )
    prism = roofline_estimate(
        config,
        "PRISM polyphase edge recovery",
        flops,
        prism_bytes,
        precision="fp64",
        graph_regions=4,
        power_w=260,
        notes="Streaming Hankel construction and resident small-solver cluster",
        use_sram=True,
    )
    return baseline, prism


def bayes_estimate(config: PrismConfig, models: int, samples: int, features: int, outputs: int, itemsize: int = 4) -> tuple[Estimate, Estimate]:
    flops_per_model = 2.0 * samples * features * features + (2.0 / 3.0) * features**3 + 2.0 * samples * features * outputs
    flops = models * flops_per_model
    baseline_bytes = itemsize * models * (samples * features + features * features + features * outputs)
    prism_bytes = itemsize * (samples * features + models * (features * features + features * outputs))
    baseline = roofline_estimate(
        config,
        "Independent Bayesian model kernels",
        flops,
        baseline_bytes,
        precision="fp32",
        graph_regions=models,
        notes="Each model reloads the shared state matrix",
    )
    prism = roofline_estimate(
        config,
        "Shape-batched Bayesian posterior",
        flops,
        prism_bytes,
        precision="fp32",
        graph_regions=8,
        notes="Shared design matrices remain resident and models are grouped by shape",
        use_sram=True,
    )
    return baseline, prism


def _save(fig: plt.Figure, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{name}.pdf", bbox_inches="tight", pad_inches=0.08)
    fig.savefig(out_dir / f"{name}.png", dpi=190, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def _box(ax: plt.Axes, x: float, y: float, w: float, h: float, text: str, face: str = "white", fontsize: float = 10.5) -> None:
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.02", facecolor=face, edgecolor="black", linewidth=1.2)
    ax.add_patch(patch)
    label = ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, multialignment="center")
    fig = ax.figure
    for _ in range(12):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        bb = label.get_window_extent(renderer=renderer)
        p0 = ax.transData.transform((x, y))
        p1 = ax.transData.transform((x + w, y + h))
        if bb.width <= abs(p1[0] - p0[0]) * 0.86 and bb.height <= abs(p1[1] - p0[1]) * 0.80:
            break
        label.set_fontsize(max(6.8, label.get_fontsize() * 0.90))


def _arrow(ax: plt.Axes, a: tuple[float, float], b: tuple[float, float], text: str | None = None, rad: float = 0.0) -> None:
    arrow = FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=12, linewidth=1.3, color="black", connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(arrow)
    if text:
        mx = (a[0] + b[0]) / 2
        my = (a[1] + b[1]) / 2
        ax.text(mx, my + 0.025, text, ha="center", va="bottom", fontsize=8.5, bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.0})


def fig_package(config: PrismConfig, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.96, "Komorebi PRISM-1 chiplet package", ha="center", va="top", fontsize=21, weight="bold")
    ax.add_patch(Rectangle((0.06, 0.10), 0.88, 0.78, facecolor="#f2f2f2", edgecolor="black", linewidth=1.4))
    positions = [(0.18, 0.58), (0.58, 0.58), (0.18, 0.22), (0.58, 0.22)]
    for i, (x, y) in enumerate(positions):
        _box(ax, x, y, 0.24, 0.20, f"Compute chiplet C{i}\n16 packet SMs\n64 execution groups\n8 transform engines\n4 solver engines", face="#dbeafe", fontsize=11)
    _box(ax, 0.42, 0.40, 0.16, 0.20, "I/O and control die\nRISC-V control\nglobal scheduler\nPCIe and CXL", face="#fef3c7", fontsize=9.2)
    hbm_pos = [(0.075, 0.69), (0.815, 0.69), (0.075, 0.20), (0.815, 0.20)]
    for i, (x, y) in enumerate(hbm_pos):
        _box(ax, x, y, 0.10, 0.15, f"HBM4 {i}\n36 GiB\n>2.8 TB/s", face="#dcfce7", fontsize=9.2)
    package_links = [
        ((0.42, 0.68), (0.435, 0.57)),
        ((0.58, 0.68), (0.565, 0.57)),
        ((0.42, 0.32), (0.435, 0.43)),
        ((0.58, 0.32), (0.565, 0.43)),
    ]
    for start, end in package_links:
        _arrow(ax, start, end)
    ax.text(0.5, 0.12, f"{config.total_hbm_gib} GiB HBM4   {config.total_hbm_tbps:.1f} TB/s aggregate   UCIe {config.ucie_gtps} GT/s package links", ha="center", fontsize=12, weight="bold")
    _save(fig, out, "01_package_architecture")


def fig_tile(config: PrismConfig, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.96, "One execution group and shared PSM paths", ha="center", va="top", fontsize=20, weight="bold")
    boxes = [
        (0.05, 0.64, 0.20, 0.18, "Descriptor front end\npacket and transfer tables", "#fef3c7"),
        (0.30, 0.64, 0.20, 0.18, "Projector DMA\nmask, gather, scatter\npolyphase permutation", "#ede9fe"),
        (0.55, 0.64, 0.20, 0.18, "1024-bit vector lane\nselectors and reductions", "#e0f2fe"),
        (0.78, 0.64, 0.17, 0.18, "Certificate unit\nFP64 and exact accumulators", "#fee2e2"),
        (0.18, 0.34, 0.28, 0.22, "one 16 x 16 matrix array\nblock transfer and low rank\nFP16 BF16 FP32 FP64\ncomplex pairs", "#dbeafe"),
        (0.54, 0.34, 0.28, 0.22, "Nonlinear and memory unit\nquadratic interactions\ndelay and Volterra kernels", "#dcfce7"),
        (0.18, 0.10, 0.28, 0.16, f"PSM scratchpad\n{config.execution_groups_per_psm * config.local_sram_kib_per_execution_group // 1024} MiB across four banks", "#f3f4f6"),
        (0.54, 0.10, 0.28, 0.16, "Mesh router\nmulticast and reduction", "#f3f4f6"),
    ]
    for x, y, w, h, text, face in boxes:
        _box(ax, x, y, w, h, text, face=face, fontsize=10.5)
    _arrow(ax, (0.25, 0.73), (0.30, 0.73))
    _arrow(ax, (0.50, 0.73), (0.55, 0.73))
    _arrow(ax, (0.75, 0.73), (0.78, 0.73))
    _arrow(ax, (0.40, 0.64), (0.32, 0.56))
    _arrow(ax, (0.65, 0.64), (0.68, 0.56))
    _arrow(ax, (0.32, 0.34), (0.32, 0.26))
    _arrow(ax, (0.68, 0.34), (0.68, 0.26))
    _arrow(ax, (0.46, 0.18), (0.54, 0.18))
    _save(fig, out, "02_packet_compute_tile")


def fig_calculus_pipeline(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 5.7))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.92, "The calculus maps directly to a hardware pipeline", ha="center", fontsize=20, weight="bold")
    labels = [
        ("seed", "load object and grammar"),
        ("address", "packet descriptor"),
        ("project", "analysis or selector"),
        ("transfer", "block or low-rank edge"),
        ("refine", "local child graph"),
        ("synthesize", "exact reconstruction"),
        ("certify", "residual and bound"),
    ]
    xs = np.linspace(0.025, 0.84, len(labels))
    for i, (x, (title, sub)) in enumerate(zip(xs, labels, strict=True)):
        _box(ax, x, 0.43, 0.13, 0.22, f"{title}\n{sub}", face="#f8fafc", fontsize=10.2)
        if i < len(labels) - 1:
            _arrow(ax, (x + 0.13, 0.54), (xs[i + 1], 0.54))
    _arrow(ax, (0.91, 0.40), (0.08, 0.40), text="certificate feeds residual-driven refinement", rad=-0.18)
    ax.text(0.5, 0.15, "Every command keeps the packet identity, atlas, precision tag, parent relation, and error budget attached to the data.", ha="center", fontsize=11.5)
    _save(fig, out, "03_calculus_pipeline")


def fig_descriptor(out: Path) -> None:
    fields = [
        ("packet_id", 12),
        ("parent_id", 12),
        ("atlas_id", 8),
        ("selector", 8),
        ("precision", 4),
        ("shape", 24),
        ("base_address", 64),
        ("error_budget", 32),
        ("flags", 12),
    ]
    total = sum(bits for _, bits in fields)
    fig, ax = plt.subplots(figsize=(13.0, 4.3))
    ax.set_xlim(0, total)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(total / 2, 0.92, "Packet descriptor entry", ha="center", fontsize=20, weight="bold")
    x = 0
    for name, bits in fields:
        ax.add_patch(Rectangle((x, 0.35), bits, 0.30, facecolor="#e5e7eb", edgecolor="black"))
        ax.text(x + bits / 2, 0.50, f"{name}\n{bits} bits", ha="center", va="center", fontsize=8.5)
        x += bits
    ax.text(total / 2, 0.14, "Selectors may be contiguous ranges, residue classes, bit masks, transform-domain bands, basis projectors, or packet-tree nodes.", ha="center", fontsize=11)
    _save(fig, out, "04_packet_descriptor")


def fig_transfer_descriptor(out: Path) -> None:
    fields = [
        ("edge_id", 12),
        ("src", 12),
        ("dst", 12),
        ("kernel", 8),
        ("rows", 16),
        ("cols", 16),
        ("rank", 8),
        ("precision", 4),
        ("sensitivity", 32),
        ("payload", 64),
        ("token", 16),
    ]
    total = sum(bits for _, bits in fields)
    fig, ax = plt.subplots(figsize=(13.0, 4.5))
    ax.set_xlim(0, total)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(total / 2, 0.92, "Transfer edge descriptor", ha="center", fontsize=20, weight="bold")
    x = 0
    for name, bits in fields:
        ax.add_patch(Rectangle((x, 0.35), bits, 0.30, facecolor="#dbeafe", edgecolor="black"))
        ax.text(x + bits / 2, 0.50, f"{name}\n{bits}", ha="center", va="center", fontsize=8.2)
        x += bits
    ax.text(total / 2, 0.14, "The edge descriptor is the hardware form of P_beta T P_alpha. It carries the operator class and its certificate weight.", ha="center", fontsize=11)
    _save(fig, out, "05_transfer_descriptor")


def fig_memory(config: PrismConfig, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 6.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "Factor-first packet memory hierarchy", ha="center", fontsize=20, weight="bold")
    levels = [
        (0.08, 0.72, 0.84, 0.14, f"HBM4 exact archive and cold factors\n{config.total_hbm_gib} GiB   {config.total_hbm_tbps:.1f} TB/s aggregate", "#dcfce7"),
        (0.16, 0.52, 0.68, 0.14, f"Shared packet cache and graph store\n{config.compute_chiplets * config.shared_sram_mib_per_chiplet} MiB", "#dbeafe"),
        (0.24, 0.32, 0.52, 0.14, f"Distributed PSM scratchpads\n{config.execution_groups * config.local_sram_kib_per_execution_group / 1024:.0f} MiB", "#ede9fe"),
        (0.34, 0.12, 0.32, 0.14, "Registers and exact accumulators\nactive blocks, low-rank panels, residuals", "#fef3c7"),
    ]
    for x, y, w, h, text, face in levels:
        _box(ax, x, y, w, h, text, face=face, fontsize=11)
    for i in range(len(levels) - 1):
        x0, y0, w0, h0, _, _ = levels[i]
        x1, y1, w1, h1, _, _ = levels[i + 1]
        _arrow(ax, (0.50, y0), (0.50, y1 + h1))
    ax.text(0.5, 0.03, "No dense array is required. Explicit materialization is only one optional output contract.", ha="center", fontsize=11.5, weight="bold")
    _save(fig, out, "06_memory_hierarchy")


def fig_bdlr(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 5.7))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.92, "BDLR execution dataflow", ha="center", fontsize=20, weight="bold")
    _box(ax, 0.05, 0.39, 0.12, 0.20, "input X", face="#f8fafc", fontsize=13)
    _box(ax, 0.25, 0.60, 0.18, 0.18, "block engines\nD X", face="#dbeafe", fontsize=12)
    _box(ax, 0.25, 0.20, 0.18, 0.18, "reduction engine\nV* X", face="#ede9fe", fontsize=12)
    _box(ax, 0.52, 0.20, 0.18, 0.18, "low-rank engine\nU (V* X)", face="#dcfce7", fontsize=12)
    _box(ax, 0.78, 0.39, 0.16, 0.20, "packet sum\nD X + U(V*X)", face="#fef3c7", fontsize=12)
    _arrow(ax, (0.17, 0.49), (0.25, 0.69))
    _arrow(ax, (0.17, 0.49), (0.25, 0.29))
    _arrow(ax, (0.43, 0.29), (0.52, 0.29))
    _arrow(ax, (0.43, 0.69), (0.78, 0.52))
    _arrow(ax, (0.70, 0.29), (0.78, 0.46))
    ax.text(0.5, 0.07, "The factors remain compressed through the pipeline. Materialization is a separate command.", ha="center", fontsize=11.5)
    _save(fig, out, "07_bdlr_dataflow")


def fig_transform(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.94, "Unified transform fabric", ha="center", fontsize=20, weight="bold")
    _box(ax, 0.05, 0.40, 0.14, 0.20, "input packet\nstream", face="#f8fafc", fontsize=12)
    units = [
        (0.27, 0.70, "FFT and DCT\nbutterflies"),
        (0.27, 0.46, "wavelet lifting\npredict and update"),
        (0.27, 0.22, "polyphase\npermute and interleave"),
    ]
    for x, y, text in units:
        _box(ax, x, y, 0.20, 0.15, text, face="#dbeafe", fontsize=11)
        _arrow(ax, (0.19, 0.50), (x, y + 0.075))
    _box(ax, 0.57, 0.37, 0.18, 0.26, "selector bank\nfrequency bands\npacket-tree nodes\nphase channels", face="#ede9fe", fontsize=11)
    for x, y, _ in units:
        _arrow(ax, (x + 0.20, y + 0.075), (0.57, 0.50))
    _box(ax, 0.82, 0.40, 0.14, 0.20, "analysis output\nor synthesis", face="#dcfce7", fontsize=12)
    _arrow(ax, (0.75, 0.50), (0.82, 0.50))
    ax.text(0.5, 0.07, "One configurable butterfly, permutation, and selector fabric replaces separate fixed-function data paths.", ha="center", fontsize=11.3)
    _save(fig, out, "08_transform_fabric")


def fig_edge_pipeline(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 6.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.93, "Self-calibrating edge recovery pipeline", ha="center", fontsize=20, weight="bold")
    stages = [
        ("spectral packet", "high-frequency coefficients"),
        ("polyphase", "decimated channels"),
        ("Hankel", "streaming matrix build"),
        ("small solver", "rank and annihilator"),
        ("phase recovery", "physical roots"),
        ("edge synthesis", "native singular packet"),
        ("certificate", "residual and branch margin"),
    ]
    xs = np.linspace(0.025, 0.84, len(stages))
    for i, (x, (a, b)) in enumerate(zip(xs, stages, strict=True)):
        _box(ax, x, 0.40, 0.13, 0.22, f"{a}\n{b}", face="#f8fafc", fontsize=9.7)
        if i < len(stages) - 1:
            _arrow(ax, (x + 0.13, 0.51), (xs[i + 1], 0.51))
    ax.text(0.5, 0.17, "The small Hankel, QR, SVD, root, and Vandermonde operations remain on one resident solver cluster.", ha="center", fontsize=11.2)
    _save(fig, out, "09_edge_recovery_pipeline")


def fig_bayes(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 6.1))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.94, "Typed Bayesian operator posterior", ha="center", fontsize=20, weight="bold")
    _box(ax, 0.05, 0.39, 0.16, 0.22, "resident state matrix\nmacro meso micro", face="#dbeafe", fontsize=11.5)
    _box(ax, 0.29, 0.66, 0.18, 0.16, "linear models", face="#f8fafc", fontsize=11)
    _box(ax, 0.29, 0.43, 0.18, 0.16, "quadratic and hybrid", face="#f8fafc", fontsize=11)
    _box(ax, 0.29, 0.20, 0.18, 0.16, "delay and memory", face="#f8fafc", fontsize=11)
    for y in (0.74, 0.51, 0.28):
        _arrow(ax, (0.21, 0.50), (0.29, y))
    _box(ax, 0.56, 0.37, 0.18, 0.26, "shape-batched solver\nGram matrices\nCholesky or QR\npredictive score", face="#ede9fe", fontsize=11)
    for y in (0.74, 0.51, 0.28):
        _arrow(ax, (0.47, y), (0.56, 0.50))
    _box(ax, 0.82, 0.39, 0.14, 0.22, "posterior mixture\nand disagreement", face="#dcfce7", fontsize=11)
    _arrow(ax, (0.74, 0.50), (0.82, 0.50))
    ax.text(0.5, 0.08, "Shared design matrices are loaded once. Candidate programs are grouped by feature shape and precision.", ha="center", fontsize=11.2)
    _save(fig, out, "10_bayesian_pipeline")


def fig_scheduler(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 6.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "Local refinement without global recompilation", ha="center", fontsize=20, weight="bold")
    old = [(0.08, 0.58, "A"), (0.25, 0.58, "B"), (0.42, 0.58, "packet v"), (0.59, 0.58, "C"), (0.76, 0.58, "D")]
    for x, y, label in old:
        _box(ax, x, y, 0.12, 0.14, label, face="#f8fafc", fontsize=12)
    for i in range(len(old) - 1):
        _arrow(ax, (old[i][0] + 0.12, 0.65), (old[i + 1][0], 0.65))
    children = [(0.35, 0.23, "v0"), (0.48, 0.23, "v1"), (0.61, 0.23, "v2")]
    for x, y, label in children:
        _box(ax, x, y, 0.10, 0.13, label, face="#dbeafe", fontsize=11)
    _arrow(ax, (0.20, 0.65), (0.35, 0.30))
    _arrow(ax, (0.45, 0.295), (0.48, 0.295))
    _arrow(ax, (0.58, 0.295), (0.61, 0.295))
    _arrow(ax, (0.71, 0.30), (0.76, 0.65))
    ax.text(0.14, 0.18, "A and B keep their descriptors", ha="center", fontsize=10.5)
    ax.text(0.82, 0.18, "C and D keep their descriptors", ha="center", fontsize=10.5)
    ax.text(0.50, 0.08, "Only the child module and the edges incident to the parent packet are regenerated.", ha="center", fontsize=11.5, weight="bold")
    _save(fig, out, "11_refinement_local_schedule")


def fig_compiler(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.94, "PRISM packet compiler", ha="center", fontsize=20, weight="bold")
    stages = [
        ("calculus IR", "atlases, packets, edges"),
        ("canonicalize", "prove shape and parent relations"),
        ("choose form", "block sparse, BDLR, transform"),
        ("allocate precision", "sensitivity and error budget"),
        ("place", "tile and memory locality"),
        ("schedule", "dependency tokens and replay"),
        ("emit", "descriptors and certificates"),
    ]
    xs = np.linspace(0.02, 0.85, len(stages))
    for i, (x, (a, b)) in enumerate(zip(xs, stages, strict=True)):
        _box(ax, x, 0.42, 0.125, 0.21, f"{a}\n{b}", face="#f8fafc", fontsize=9.5)
        if i < len(stages) - 1:
            _arrow(ax, (x + 0.125, 0.525), (xs[i + 1], 0.525))
    ax.text(0.5, 0.18, "The compiler is allowed to change the representation only when the exact output contract and certificate are preserved.", ha="center", fontsize=11.2)
    _save(fig, out, "12_compiler_pipeline")


def fig_workload_map(out: Path) -> None:
    labels = ["polyphase", "Fourier", "wavelet", "BDLR", "block sparse", "Bayesian", "Prony", "Volterra", "exact modular"]
    engines = ["projector DMA", "transform", "transform", "matrix + low rank", "matrix + router", "solver", "solver + transform", "memory unit", "exact arithmetic"]
    fig, ax = plt.subplots(figsize=(12.8, 6.5))
    ax.axis("off")
    ax.text(0.5, 0.95, "Calculus operations and hardware engines", ha="center", fontsize=20, weight="bold", transform=ax.transAxes)
    y = 0.84
    for i, (op, engine) in enumerate(zip(labels, engines, strict=True)):
        face = "#f8fafc" if i % 2 == 0 else "#eef2ff"
        ax.add_patch(Rectangle((0.08, y - 0.035), 0.84, 0.065, facecolor=face, edgecolor="none", transform=ax.transAxes))
        ax.text(0.12, y, op, ha="left", va="center", fontsize=11.5, weight="bold", transform=ax.transAxes)
        ax.text(0.52, y, engine, ha="left", va="center", fontsize=11.5, transform=ax.transAxes)
        y -= 0.083
    _save(fig, out, "13_workload_engine_map")


def fig_roofline(config: PrismConfig, estimates: Sequence[Estimate], out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.8, 6.5))
    intensity = np.logspace(-2, 4, 400)
    peak = config.fp32_tflops
    bw = config.total_hbm_tbps
    roof = np.minimum(peak, intensity * bw)
    ax.loglog(intensity, roof, linewidth=2.2, label="PRISM FP32 roofline")
    for est in estimates:
        perf = est.flops / (est.total_time_us * 1e-6) / 1e12
        ax.scatter(est.arithmetic_intensity, perf, s=55)
        ax.annotate(est.workload, (est.arithmetic_intensity, perf), xytext=(5, 5), textcoords="offset points", fontsize=8.5)
    ax.set_xlabel("Arithmetic intensity in operations per byte")
    ax.set_ylabel("Modeled throughput in TFLOP/s")
    ax.set_title("PRISM roofline and representative packet workloads", weight="bold")
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    _save(fig, out, "14_roofline")


def fig_performance(pairs: Sequence[tuple[Estimate, Estimate]], out: Path) -> None:
    names = [p[1].workload.replace("PRISM ", "") for p in pairs]
    speedups = [p[0].total_time_us / p[1].total_time_us for p in pairs]
    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    ax.bar(np.arange(len(names)), speedups)
    ax.set_xticks(np.arange(len(names)), names, rotation=22, ha="right")
    ax.set_ylabel("Modeled speedup over matched generic execution")
    ax.set_title("Architecture-model speedups from structure and kernel fusion", weight="bold")
    ax.grid(alpha=0.22, axis="y")
    for i, value in enumerate(speedups):
        ax.text(i, value, f"{value:.1f}x", ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    _save(fig, out, "15_modeled_speedups")


def fig_memory_reduction(out: Path) -> None:
    n, b, r = 8192, 64, 8
    dense = n * n * 4 / 2**20
    bdlr = n * (b + 2 * r) * 4 / 2**20
    block = n * b * 4 / 2**20
    labels = ["dense", "block diagonal", "BDLR"]
    values = [dense, block, bdlr]
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.bar(labels, values)
    ax.set_yscale("log")
    ax.set_ylabel("Stored representation in MiB")
    ax.set_title("Representation memory for n=8192, b=64, r=8", weight="bold")
    ax.grid(alpha=0.22, axis="y", which="both")
    for i, value in enumerate(values):
        ax.text(i, value, f"{value:.2f}", ha="center", va="bottom", fontsize=10)
    _save(fig, out, "16_representation_memory")


def fig_power(config: PrismConfig, out: Path) -> None:
    labels = ["execution groups", "SRAM", "packet network", "HBM PHY", "transform and solver", "I/O and control", "clock and margin"]
    values = [175, 80, 65, 70, 40, 30, 40]
    if sum(values) != config.tdp_w:
        raise RuntimeError("power budget must equal TDP")
    fig, ax = plt.subplots(figsize=(9.0, 6.2))
    ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=90)
    ax.set_title(f"Reference power budget at {config.tdp_w} W", weight="bold")
    _save(fig, out, "17_power_budget")


def fig_area(out: Path) -> None:
    labels = ["distributed SRAM", "matrix and vector lanes", "network and DMA", "transform and solver", "control and DFx"]
    values = [35, 30, 15, 12, 8]
    fig, ax = plt.subplots(figsize=(9.0, 6.2))
    ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=90)
    ax.set_title("Target compute-chiplet area allocation", weight="bold")
    _save(fig, out, "18_area_allocation")


def fig_precision(out: Path) -> None:
    sensitivity = np.array([0.10, 0.18, 0.30, 0.52, 0.80, 1.20, 2.0, 3.2])
    cost = np.ones_like(sensitivity)
    tau = 0.02
    eps = tau * cost / (sensitivity * cost.sum())
    bits = np.clip(np.ceil(-np.log2(eps)), 8, 64)
    fig, ax = plt.subplots(figsize=(10.2, 5.8))
    ax.plot(sensitivity, bits, marker="o")
    ax.set_xlabel("Packet sensitivity weight")
    ax.set_ylabel("Allocated mantissa target in bits")
    ax.set_title("Sensitivity-driven precision tags", weight="bold")
    ax.grid(alpha=0.25)
    _save(fig, out, "19_precision_allocation")


def fig_network(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.8, 7.0))
    ax.set_xlim(-0.5, 7.5)
    ax.set_ylim(-0.85, 7.5)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("One 8 x 8 compute-chiplet packet mesh", fontsize=18, weight="bold")
    for i in range(8):
        for j in range(8):
            ax.add_patch(Rectangle((i - 0.28, j - 0.28), 0.56, 0.56, facecolor="#e5e7eb", edgecolor="black", linewidth=0.7))
            if i < 7:
                ax.plot([i + 0.28, i + 0.72], [j, j], color="black", linewidth=0.7)
            if j < 7:
                ax.plot([i, i], [j + 0.28, j + 0.72], color="black", linewidth=0.7)
    ax.text(3.5, -0.58, "Routers support unicast, packet multicast, and tree reduction", ha="center", va="top", fontsize=10.5)
    _save(fig, out, "20_packet_mesh")


def fig_isa(out: Path) -> None:
    groups = {
        "packet": ["PLOAD", "PSELECT", "PSPLIT", "PCOARSEN"],
        "transform": ["FFT", "WAVELET", "POLYPHASE", "SYNTH"],
        "transfer": ["BLK_GEMM", "BDLR", "SPARSE", "WOODBURY"],
        "solver": ["CHOLESKY", "QR", "SVD", "ROOT"],
        "logic": ["NONLINEAR", "MEMORY", "BAYES", "GRAPH"],
        "certificate": ["RESIDUAL", "BOUND", "TRACE", "COMMIT"],
    }
    fig, ax = plt.subplots(figsize=(12.0, 6.3))
    ax.axis("off")
    ax.text(0.5, 0.95, "Packet Seed Command groups", ha="center", fontsize=20, weight="bold", transform=ax.transAxes)
    y = 0.82
    for group, ops in groups.items():
        ax.text(0.08, y, group, ha="left", va="center", fontsize=12, weight="bold", transform=ax.transAxes)
        for j, op in enumerate(ops):
            x = 0.28 + j * 0.17
            ax.add_patch(FancyBboxPatch((x, y - 0.035), 0.13, 0.07, boxstyle="round,pad=0.01", facecolor="#eef2ff", edgecolor="black", transform=ax.transAxes))
            ax.text(x + 0.065, y, op, ha="center", va="center", fontsize=9.5, transform=ax.transAxes)
        y -= 0.125
    _save(fig, out, "21_command_groups")


def fig_prototype(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 5.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.93, "Implementation path", ha="center", fontsize=20, weight="bold")
    stages = [
        ("software and CUDA", "shared Packet IR\nmeasured structured kernels"),
        ("trace comparison", "matched CUDA and PRISM\nbackend records"),
        ("FPGA PSM", "one multiprocessor\nexternal memory"),
        ("chiplet and package", "measured PSM scaling\nthen HBM4 and UCIe"),
    ]
    xs = [0.05, 0.29, 0.53, 0.77]
    for i, (x, (a, b)) in enumerate(zip(xs, stages, strict=True)):
        _box(ax, x, 0.38, 0.18, 0.24, f"{a}\n{b}", face="#f8fafc", fontsize=11)
        if i < len(stages) - 1:
            _arrow(ax, (x + 0.18, 0.50), (xs[i + 1], 0.50))
    ax.text(0.5, 0.14, "Each stage preserves the same descriptor format, operator contracts, and certificate semantics.", ha="center", fontsize=11.5)
    _save(fig, out, "22_implementation_path")


def fig_negative_controls(out: Path) -> None:
    labels = ["regular BDLR", "regular block sparse", "multi-atlas fusion", "small one-off FFT", "dense unstructured GEMM", "irregular no-reuse graph"]
    suitability = [0.95, 0.88, 0.82, 0.28, 0.22, 0.18]
    fig, ax = plt.subplots(figsize=(11.0, 6.0))
    ax.barh(np.arange(len(labels)), suitability)
    ax.set_yticks(np.arange(len(labels)), labels)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Expected architectural fit")
    ax.set_title("Workloads the chip should accelerate and workloads it should reject", weight="bold")
    ax.grid(alpha=0.22, axis="x")
    _save(fig, out, "23_workload_fit")



def precision_allocation(sensitivity: np.ndarray, cost: np.ndarray, tau: float) -> np.ndarray:
    """Allocate a continuous packet error budget under the logarithmic cost model."""
    s = np.asarray(sensitivity, dtype=float)
    c = np.asarray(cost, dtype=float)
    if s.shape != c.shape or s.ndim != 1:
        raise ValueError("sensitivity and cost must be matching one-dimensional arrays")
    if np.any(s <= 0) or np.any(c <= 0) or tau <= 0:
        raise ValueError("sensitivities, costs, and tau must be positive")
    return tau * c / (s * np.sum(c))


def certificate_commit_allowed(
    dependency_ready: bool,
    kernel_complete: bool,
    residual: float,
    error_budget: float,
) -> bool:
    """Return true only when execution and its required numerical certificate both pass."""
    return bool(
        dependency_ready
        and kernel_complete
        and error_budget >= 0
        and residual >= 0
        and residual <= error_budget
    )


def local_refinement_descriptor_bound(
    child_nodes: int,
    child_edges: int,
    parent_indegree: int,
    parent_outdegree: int,
    entry_count: int,
    exit_count: int,
) -> int:
    """Worst-case descriptor regeneration bound for one local refinement."""
    values = [child_nodes, child_edges, parent_indegree, parent_outdegree, entry_count, exit_count]
    if any(v < 0 for v in values):
        raise ValueError("descriptor counts must be nonnegative")
    return (
        child_nodes
        + child_edges
        + parent_indegree * entry_count
        + parent_outdegree * exit_count
    )


def route_workload(
    operator_kind: str,
    representation_reduction: float,
    reuse_count: int,
    graph_nodes: int,
) -> str:
    """Simple reference routing rule used by the compiler examples and tests."""
    if reuse_count < 1 or graph_nodes < 1 or representation_reduction <= 0:
        raise ValueError("invalid workload description")
    kind = operator_kind.lower()
    if kind in {"bdlr", "block_sparse", "transform", "small_solver", "packet_graph"}:
        if representation_reduction >= 1.25 and (reuse_count >= 2 or graph_nodes >= 8):
            return "prism"
    if kind == "dense" and representation_reduction < 1.25:
        return "dense_path"
    if graph_nodes <= 3 and reuse_count == 1:
        return "host_or_general_device"
    return "profile_before_routing"


def bdlr_sensitivity_tables(config: PrismConfig, n: int = 8192, q: int = 32) -> dict[str, object]:
    block_sizes = np.array([16, 32, 64, 128, 256], dtype=int)
    ranks = np.array([2, 4, 8, 16, 32], dtype=int)
    dense = dense_apply_estimate(config, n, q)
    speedups = np.zeros((len(ranks), len(block_sizes)))
    storage = np.zeros_like(speedups)
    for i, rank in enumerate(ranks):
        for j, block in enumerate(block_sizes):
            packet = bdlr_estimate(config, n, int(block), int(rank), q)
            speedups[i, j] = dense.total_time_us / packet.total_time_us
            storage[i, j] = n / (block + 2 * rank)
    return {
        "block_sizes": block_sizes.tolist(),
        "ranks": ranks.tolist(),
        "modeled_speedups": speedups.tolist(),
        "storage_reduction": storage.tolist(),
    }


def fig_packet_lifecycle(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.94, "Life of one packet command", ha="center", fontsize=21, weight="bold")
    labels = [
        ("archive", "packet data and descriptor", "#e0f2fe"),
        ("ready", "dependencies and storage valid", "#ede9fe"),
        ("execute", "selected engine runs local map", "#dcfce7"),
        ("provisional", "result held before commit", "#fef3c7"),
        ("certify", "residual or bound checked", "#fee2e2"),
        ("commit", "result becomes visible", "#dbeafe"),
    ]
    xs = np.linspace(0.03, 0.82, len(labels))
    for i, (x, (title, sub, face)) in enumerate(zip(xs, labels, strict=True)):
        _box(ax, x, 0.45, 0.145, 0.20, f"{title}\n{sub}", face=face, fontsize=10.2)
        if i < len(labels) - 1:
            _arrow(ax, (x + 0.145, 0.55), (xs[i + 1], 0.55))
    _arrow(ax, (0.89, 0.43), (0.57, 0.35), text="failed certificate returns the region for replay", rad=-0.20)
    ax.text(
        0.5,
        0.16,
        "The result remains provisional until the declared certificate passes. A failed check does not silently publish data.",
        ha="center",
        fontsize=11.3,
    )
    _save(fig, out, "24_packet_lifecycle")


def fig_workload_router(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.5, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "Compiler routing decision", ha="center", fontsize=21, weight="bold")
    _box(ax, 0.39, 0.79, 0.22, 0.10, "Is useful packet structure proved?", face="#fef3c7", fontsize=11)
    _box(ax, 0.08, 0.58, 0.22, 0.12, "No\nuse the dense path or another device", face="#fee2e2", fontsize=11)
    _box(ax, 0.39, 0.58, 0.22, 0.12, "Yes\ndoes it reduce bytes or arithmetic?", face="#e0f2fe", fontsize=10.5)
    _box(ax, 0.70, 0.58, 0.22, 0.12, "Unclear\nprofile both representations", face="#f3f4f6", fontsize=10.5)
    _box(ax, 0.23, 0.34, 0.22, 0.12, "No\nretain the simpler route", face="#fee2e2", fontsize=11)
    _box(ax, 0.55, 0.34, 0.22, 0.12, "Yes\nis reuse large enough to amortize setup?", face="#dcfce7", fontsize=10.2)
    _box(ax, 0.41, 0.10, 0.22, 0.12, "Route to PRISM\nattach certificate plan", face="#dbeafe", fontsize=11)
    _arrow(ax, (0.44, 0.79), (0.25, 0.70), text="no")
    _arrow(ax, (0.50, 0.79), (0.50, 0.70), text="yes")
    _arrow(ax, (0.56, 0.79), (0.81, 0.70), text="unknown")
    _arrow(ax, (0.45, 0.58), (0.34, 0.46), text="no")
    _arrow(ax, (0.55, 0.58), (0.66, 0.46), text="yes")
    _arrow(ax, (0.66, 0.34), (0.52, 0.22), text="yes")
    ax.text(0.72, 0.23, "A small one-off graph may still be routed away", ha="center", fontsize=10.5)
    _save(fig, out, "25_workload_router")


def fig_chiplet_floorplan(config: PrismConfig, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.2, 7.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Reference compute-chiplet floorplan", fontsize=20, weight="bold", pad=10)
    ax.add_patch(Rectangle((0.4, 0.4), 9.2, 9.2, facecolor="#f8fafc", edgecolor="black", linewidth=1.5))
    for i in range(8):
        for j in range(8):
            ax.add_patch(Rectangle((1.2 + i * 0.9, 1.2 + j * 0.9), 0.68, 0.68, facecolor="#dbeafe", edgecolor="#334155", linewidth=0.45))
    for y in [1.25, 3.25, 5.25, 7.25]:
        ax.add_patch(Rectangle((8.55, y), 0.55, 1.3, facecolor="#dcfce7", edgecolor="black", linewidth=0.8))
        ax.text(8.825, y + 0.65, "solver", ha="center", va="center", rotation=90, fontsize=8)
    for x in [1.2, 3.0, 4.8, 6.6]:
        ax.add_patch(Rectangle((x, 8.55), 1.25, 0.55, facecolor="#ede9fe", edgecolor="black", linewidth=0.8))
        ax.text(x + 0.625, 8.825, "transform", ha="center", va="center", fontsize=8)
    ax.add_patch(Rectangle((0.55, 1.2), 0.42, 7.2, facecolor="#fef3c7", edgecolor="black", linewidth=0.8))
    ax.text(0.76, 4.8, "shared SRAM banks", ha="center", va="center", rotation=90, fontsize=9)
    ax.add_patch(Rectangle((1.2, 0.55), 6.8, 0.42, facecolor="#fee2e2", edgecolor="black", linewidth=0.8))
    ax.text(4.6, 0.76, "UCIe and package router edge", ha="center", va="center", fontsize=9)
    ax.add_patch(Rectangle((8.55, 8.55), 0.55, 0.55, facecolor="#fecaca", edgecolor="black", linewidth=0.8))
    ax.text(8.825, 8.825, "exact", ha="center", va="center", fontsize=7.5)
    _save(fig, out, "26_chiplet_floorplan")


def fig_bandwidth_budget(config: PrismConfig, out: Path) -> None:
    labels = ["PCIe x16 host", "HBM4 aggregate", "package fabric"]
    values = [config.host_bidirectional_gbps / 1000.0, config.total_hbm_tbps, config.package_network_tbps]
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    bars = ax.bar(labels, values, edgecolor="black")
    ax.set_ylabel("Reference bidirectional or aggregate bandwidth in TB/s")
    ax.set_title("Bandwidth levels in the reference package", weight="bold")
    ax.grid(alpha=0.22, axis="y")
    for bar, value in zip(bars, values, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.3g}", ha="center", va="bottom", fontsize=10.5)
    ax.text(
        0.5,
        -0.18,
        "The host link is not the steady-state data path. Reusable packet graphs and factors are expected to remain on the package.",
        ha="center",
        transform=ax.transAxes,
        fontsize=10.5,
    )
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    _save(fig, out, "27_bandwidth_budget")


def fig_command_state_machine(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.5, 6.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.94, "Command and certificate state machine", ha="center", fontsize=21, weight="bold")
    states = {
        "queued": (0.08, 0.54, "#e0f2fe"),
        "ready": (0.26, 0.54, "#ede9fe"),
        "running": (0.44, 0.54, "#dcfce7"),
        "provisional": (0.62, 0.54, "#fef3c7"),
        "committed": (0.82, 0.72, "#dbeafe"),
        "replay": (0.82, 0.36, "#fee2e2"),
    }
    for name, (x, y, face) in states.items():
        _box(ax, x, y, 0.12, 0.11, name, face=face, fontsize=11)
    _arrow(ax, (0.20, 0.595), (0.26, 0.595), text="tokens ready")
    _arrow(ax, (0.38, 0.595), (0.44, 0.595), text="resources granted")
    _arrow(ax, (0.56, 0.595), (0.62, 0.595), text="kernel done")
    _arrow(ax, (0.74, 0.61), (0.82, 0.74), text="certificate passes")
    _arrow(ax, (0.74, 0.56), (0.82, 0.42), text="certificate fails")
    _arrow(ax, (0.88, 0.36), (0.50, 0.49), text="reissue local region", rad=-0.18)
    ax.text(0.5, 0.16, "Only committed results can satisfy downstream completion tokens.", ha="center", fontsize=11.5)
    _save(fig, out, "28_command_state_machine")


def fig_bdlr_sensitivity(config: PrismConfig, out: Path) -> None:
    table = bdlr_sensitivity_tables(config)
    blocks = table["block_sizes"]
    ranks = table["ranks"]
    speedups = np.array(table["modeled_speedups"])
    fig, ax = plt.subplots(figsize=(9.8, 6.4))
    im = ax.imshow(speedups, origin="lower", aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(blocks)), blocks)
    ax.set_yticks(range(len(ranks)), ranks)
    ax.set_xlabel("Packet block width b")
    ax.set_ylabel("Low-rank correction r")
    ax.set_title("Modeled BDLR speedup sensitivity for n=8192 and q=32", weight="bold")
    for i in range(len(ranks)):
        for j in range(len(blocks)):
            ax.text(j, i, f"{speedups[i, j]:.1f}x", ha="center", va="center", fontsize=9, color="white" if speedups[i, j] < speedups.max() * 0.55 else "black")
    fig.colorbar(im, ax=ax, label="Modeled speedup")
    fig.tight_layout()
    _save(fig, out, "29_bdlr_speedup_sensitivity")


def fig_bdlr_storage_sensitivity(config: PrismConfig, out: Path) -> None:
    table = bdlr_sensitivity_tables(config)
    blocks = table["block_sizes"]
    ranks = table["ranks"]
    reduction = np.array(table["storage_reduction"])
    fig, ax = plt.subplots(figsize=(9.8, 6.4))
    im = ax.imshow(reduction, origin="lower", aspect="auto", cmap="magma")
    ax.set_xticks(range(len(blocks)), blocks)
    ax.set_yticks(range(len(ranks)), ranks)
    ax.set_xlabel("Packet block width b")
    ax.set_ylabel("Low-rank correction r")
    ax.set_title("Dense-to-factor storage reduction", weight="bold")
    for i in range(len(ranks)):
        for j in range(len(blocks)):
            ax.text(j, i, f"{reduction[i, j]:.1f}x", ha="center", va="center", fontsize=9, color="white" if reduction[i, j] < reduction.max() * 0.50 else "black")
    fig.colorbar(im, ax=ax, label="Storage reduction")
    fig.tight_layout()
    _save(fig, out, "30_bdlr_storage_sensitivity")


def fig_solver_pipeline(out: Path) -> None:
    stages = [
        ("FFT packet", 0.0, 3.0, "#dbeafe"),
        ("polyphase", 2.3, 1.3, "#ede9fe"),
        ("Hankel build", 3.1, 1.0, "#dcfce7"),
        ("rank and SVD", 4.0, 1.5, "#fef3c7"),
        ("roots and phase", 5.3, 1.5, "#fee2e2"),
        ("Vandermonde", 6.5, 1.2, "#cffafe"),
        ("native synthesis", 7.4, 1.5, "#bfdbfe"),
        ("certificate", 8.5, 1.0, "#fecaca"),
    ]
    fig, ax = plt.subplots(figsize=(12.0, 6.0))
    y = np.arange(len(stages))
    for i, (name, start, width, color) in enumerate(stages):
        ax.barh(i, width, left=start, color=color, edgecolor="black")
        ax.text(start + width / 2, i, name, ha="center", va="center", fontsize=9.5)
    ax.set_yticks([])
    ax.set_xlabel("Illustrative normalized time")
    ax.set_title("Resident small-solver pipeline for unknown-edge recovery", weight="bold")
    ax.set_xlim(0, 10)
    ax.grid(alpha=0.18, axis="x")
    ax.invert_yaxis()
    fig.tight_layout()
    _save(fig, out, "31_solver_pipeline")


def fig_pr_lasm_state_map(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "PR-LASM data that remains resident on PRISM", ha="center", fontsize=20, weight="bold")
    _box(ax, 0.05, 0.58, 0.25, 0.22, "exact archive\nspatial, Fourier, wavelet, polyphase\nreconstructible signal object", face="#e0f2fe", fontsize=10.8)
    _box(ax, 0.38, 0.67, 0.18, 0.12, "macro state\n48 values", face="#dcfce7", fontsize=11)
    _box(ax, 0.38, 0.49, 0.18, 0.12, "meso state\n96 values", face="#dcfce7", fontsize=11)
    _box(ax, 0.38, 0.31, 0.18, 0.12, "micro state\n192 values", face="#dcfce7", fontsize=11)
    _box(ax, 0.66, 0.58, 0.27, 0.22, "typed program portfolio\nlinear, nonlinear, memory, Bayesian\nshared resident design matrices", face="#fef3c7", fontsize=10.8)
    _box(ax, 0.66, 0.23, 0.27, 0.17, "transition graph and planner\nexact replay edges kept separate\nfrom probabilistic predictions", face="#ede9fe", fontsize=10.5)
    _arrow(ax, (0.30, 0.69), (0.38, 0.73))
    _arrow(ax, (0.30, 0.69), (0.38, 0.55))
    _arrow(ax, (0.30, 0.69), (0.38, 0.37))
    _arrow(ax, (0.56, 0.73), (0.66, 0.69))
    _arrow(ax, (0.56, 0.55), (0.66, 0.66))
    _arrow(ax, (0.56, 0.37), (0.66, 0.63))
    _arrow(ax, (0.80, 0.58), (0.80, 0.40))
    _arrow(ax, (0.70, 0.23), (0.28, 0.56), text="residual-driven refinement", rad=-0.16)
    ax.text(0.5, 0.10, "Compact prediction state never replaces the exact archive.", ha="center", fontsize=11.5)
    _save(fig, out, "32_pr_lasm_state_map")


def fig_verification_pyramid(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.0, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "Verification ladder", ha="center", fontsize=21, weight="bold")
    levels = [
        (0.08, 0.14, 0.84, "mathematical operator contracts", "#dbeafe"),
        (0.14, 0.27, 0.72, "behavioral and performance model", "#e0f2fe"),
        (0.20, 0.40, 0.60, "bit-accurate kernels and compiler conformance", "#dcfce7"),
        (0.26, 0.53, 0.48, "RTL simulation and formal properties", "#fef3c7"),
        (0.32, 0.66, 0.36, "FPGA overlay and measured data movement", "#fee2e2"),
        (0.38, 0.79, 0.24, "single-chiplet silicon", "#fecaca"),
    ]
    for x, y, w, label, color in levels:
        ax.add_patch(Rectangle((x, y), w, 0.09, facecolor=color, edgecolor="black", linewidth=1.0))
        ax.text(x + w / 2, y + 0.045, label, ha="center", va="center", fontsize=10.5)
    ax.text(0.5, 0.06, "The present work covers the first two levels and defines the interfaces needed by the remaining levels.", ha="center", fontsize=10.7)
    _save(fig, out, "33_verification_pyramid")


def fig_fpga_overlay(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.6, 6.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.94, "Recommended FPGA overlay", ha="center", fontsize=21, weight="bold")
    _box(ax, 0.04, 0.40, 0.15, 0.20, "host and runtime\nPCIe DMA\ncommand ring", face="#fef3c7", fontsize=10.5)
    _box(ax, 0.25, 0.62, 0.17, 0.16, "packet directory\nand token scoreboard", face="#e0f2fe", fontsize=10.5)
    _box(ax, 0.25, 0.28, 0.17, 0.16, "projector DMA\nand packet SRAM", face="#ede9fe", fontsize=10.5)
    _box(ax, 0.49, 0.62, 0.17, 0.16, "transform engine\nFFT and lifting", face="#dcfce7", fontsize=10.5)
    _box(ax, 0.49, 0.28, 0.17, 0.16, "matrix and low-rank\nengine", face="#dbeafe", fontsize=10.5)
    _box(ax, 0.73, 0.62, 0.17, 0.16, "small solver\nQR, SVD, roots", face="#fef3c7", fontsize=10.5)
    _box(ax, 0.73, 0.28, 0.17, 0.16, "certificate unit\nand commit controller", face="#fee2e2", fontsize=10.5)
    _arrow(ax, (0.19, 0.50), (0.25, 0.70))
    _arrow(ax, (0.19, 0.50), (0.25, 0.36))
    _arrow(ax, (0.42, 0.70), (0.49, 0.70))
    _arrow(ax, (0.42, 0.36), (0.49, 0.36))
    _arrow(ax, (0.66, 0.70), (0.73, 0.70))
    _arrow(ax, (0.66, 0.36), (0.73, 0.36))
    _arrow(ax, (0.82, 0.62), (0.82, 0.44))
    _arrow(ax, (0.73, 0.34), (0.66, 0.34), text="replay on failure", rad=-0.18)
    ax.text(0.5, 0.12, "The overlay should preserve the final descriptor format so software can move to a later ASIC without changing its graph model.", ha="center", fontsize=10.8)
    _save(fig, out, "34_fpga_overlay")


def fig_risk_matrix(out: Path) -> None:
    risks = [
        (4, 4, "HBM and package power"),
        (3, 4, "small-solver latency"),
        (3, 3, "NoC congestion"),
        (2, 5, "compiler misclassification"),
        (3, 2, "descriptor overhead"),
        (2, 4, "certificate false pass"),
        (2, 3, "exact-arithmetic timing"),
    ]
    fig, ax = plt.subplots(figsize=(9.2, 6.8))
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xlabel("Likelihood before mitigation")
    ax.set_ylabel("Impact")
    ax.set_title("Development risk map", weight="bold")
    for x in range(1, 6):
        for y in range(1, 6):
            score = x * y
            color = "#dcfce7" if score <= 6 else "#fef3c7" if score <= 12 else "#fee2e2"
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor=color, edgecolor="white"))
    for x, y, label in risks:
        ax.scatter([x], [y], s=70, edgecolor="black", zorder=3)
        ax.text(x + 0.08, y + 0.08, label, fontsize=8.5, va="bottom")
    ax.grid(color="white", linewidth=1.2)
    fig.tight_layout()
    _save(fig, out, "35_risk_matrix")


def fig_compiler_trace(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.94, "Worked compiler trace for one BDLR operator", ha="center", fontsize=20, weight="bold")
    stages = [
        (0.03, "typed operator\n$A=D+UV^*$"),
        (0.20, "legality\nshape and output contract"),
        (0.37, "representation\nkeep factors"),
        (0.54, "placement\nco-locate blocks and factor rows"),
        (0.71, "precision\nallocate edge budgets"),
        (0.86, "schedule\nreduce and broadcast"),
    ]
    for i, (x, text) in enumerate(stages):
        _box(ax, x, 0.48, 0.12, 0.19, text, face="#f8fafc", fontsize=9.8)
        if i < len(stages) - 1:
            _arrow(ax, (x + 0.12, 0.575), (stages[i + 1][0], 0.575))
    ax.text(0.5, 0.29, "Explicit array never created", ha="center", fontsize=13, weight="bold")
    ax.text(0.5, 0.20, "Stored scalars fall from $n^2$ to $n(b+2r)$ while the external operator contract remains unchanged.", ha="center", fontsize=11)
    _save(fig, out, "36_compiler_trace")


def fig_packet_streaming_multiprocessor(config: PrismConfig, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 7.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.96, "Packet Streaming Multiprocessor", ha="center", va="top", fontsize=21, weight="bold")
    _box(ax, 0.05, 0.69, 0.19, 0.16, "front end\npacket warps\ndependency tokens", face="#fef3c7", fontsize=10.5)
    _box(ax, 0.29, 0.69, 0.19, 0.16, "representation router\nblock, factors, transform\nsmall solver, dense leaf", face="#ede9fe", fontsize=10.0)
    _box(ax, 0.53, 0.69, 0.19, 0.16, "descriptor and atlas cache\nparent, precision, output contract", face="#e0f2fe", fontsize=9.8)
    _box(ax, 0.77, 0.69, 0.18, 0.16, "certificate and commit\nresidual, bound, replay", face="#fee2e2", fontsize=10.2)
    for i in range(3):
        starts = [0.24, 0.48, 0.72]
        ends = [0.29, 0.53, 0.77]
        _arrow(ax, (starts[i], 0.77), (ends[i], 0.77))
    xs = [0.06, 0.29, 0.52, 0.75]
    colors = ["#dbeafe", "#dcfce7", "#fef3c7", "#ede9fe"]
    labels = [
        "execution group 0\n16 x 16 matrix\nvector lanes",
        "execution group 1\n16 x 16 matrix\nvector lanes",
        "execution group 2\n16 x 16 matrix\nvector lanes",
        "execution group 3\n16 x 16 matrix\nvector lanes",
    ]
    for x, face, label in zip(xs, colors, labels, strict=True):
        _box(ax, x, 0.36, 0.19, 0.22, label, face=face, fontsize=10.4)
        _arrow(ax, (0.385, 0.69), (x + 0.095, 0.58))
    _box(ax, 0.12, 0.10, 0.34, 0.16, f"PSM packet scratchpad\n{config.execution_groups_per_psm * config.local_sram_kib_per_execution_group // 1024} MiB, four independently banked regions", face="#f3f4f6", fontsize=11)
    _box(ax, 0.54, 0.10, 0.34, 0.16, "asynchronous packet DMA and mesh port\ngather, scatter, multicast, reduction", face="#f3f4f6", fontsize=11)
    for x in xs:
        _arrow(ax, (x + 0.095, 0.36), (0.29, 0.26))
        _arrow(ax, (x + 0.095, 0.36), (0.71, 0.26))
    ax.text(0.5, 0.03, "A packet warp may invoke several execution forms without converting the operator into one dense array.", ha="center", fontsize=11.4, weight="bold")
    _save(fig, out, "37_packet_streaming_multiprocessor")


def fig_mixed_representation_space(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 6.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "One operator, several executable representations", ha="center", fontsize=21, weight="bold")
    _box(ax, 0.39, 0.72, 0.22, 0.14, "typed operator\noutput contract and tolerance", face="#fef3c7", fontsize=11.5)
    forms = [
        (0.04, 0.43, "block and\nblock sparse", "#dbeafe"),
        (0.23, 0.43, "low rank and\nBDLR factors", "#dcfce7"),
        (0.42, 0.43, "Kronecker and\ntensor factors", "#ede9fe"),
        (0.61, 0.43, "sparse chain and\nbutterfly", "#e0f2fe"),
        (0.80, 0.43, "transform and\npacket graph", "#fef3c7"),
    ]
    for x, y, label, face in forms:
        _box(ax, x, y, 0.16, 0.15, label, face=face, fontsize=10.5)
        _arrow(ax, (0.50, 0.72), (x + 0.08, y + 0.15))
    _box(ax, 0.38, 0.14, 0.24, 0.14, "explicit full array\noptional fallback or requested output", face="#fee2e2", fontsize=11.0)
    for x, y, _, _ in forms:
        _arrow(ax, (x + 0.08, y), (0.50, 0.28), rad=0.04 if x < 0.5 else -0.04)
    ax.text(0.5, 0.05, "The dense representation is one candidate leaf. It is not the machine state that every path must preserve.", ha="center", fontsize=11.5, weight="bold")
    _save(fig, out, "38_mixed_representation_space")


def fig_pmr_gemm_planner(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.96, "PMR-GEMM mixed-representation planning", ha="center", fontsize=21, weight="bold")
    _box(ax, 0.39, 0.78, 0.22, 0.12, "product node\nA B", face="#fef3c7", fontsize=13)
    choices = [
        (0.04, 0.54, "generic dense leaf"),
        (0.21, 0.54, "low-rank\ncontraction"),
        (0.38, 0.54, "Kronecker\nidentity"),
        (0.55, 0.54, "transform-domain\nrule"),
        (0.72, 0.54, "sparse factor\nchain"),
        (0.87, 0.54, "split and\nrecurse"),
    ]
    for x, y, label in choices:
        w = 0.12 if x < 0.85 else 0.10
        _box(ax, x, y, w, 0.14, label, face="#f8fafc", fontsize=9.7)
        _arrow(ax, (0.50, 0.78), (x + w / 2, y + 0.14))
    _box(ax, 0.24, 0.25, 0.22, 0.13, "Bellman objective\nlocal cost + error + child plans", face="#dbeafe", fontsize=10.8)
    _box(ax, 0.54, 0.25, 0.22, 0.13, "output contract\napply, factors, transform plan, array", face="#dcfce7", fontsize=10.5)
    _arrow(ax, (0.92, 0.54), (0.35, 0.38))
    _arrow(ax, (0.50, 0.54), (0.65, 0.38))
    _box(ax, 0.39, 0.06, 0.22, 0.12, "least-cost certified plan", face="#ede9fe", fontsize=12)
    _arrow(ax, (0.35, 0.25), (0.48, 0.18))
    _arrow(ax, (0.65, 0.25), (0.52, 0.18))
    ax.text(0.5, 0.01, "The generic leaf remains available, but structured leaves are not converted back to dense form unless the output contract asks for it.", ha="center", fontsize=10.8)
    _save(fig, out, "39_pmr_gemm_planner")


def fig_shared_packet_ir(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 6.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "One Packet IR, two execution backends", ha="center", fontsize=21, weight="bold")
    _box(ax, 0.37, 0.73, 0.26, 0.13, "calculus front end\npackets, atlases, transfer graph", face="#fef3c7", fontsize=11.2)
    _box(ax, 0.37, 0.52, 0.26, 0.13, "Packet IR\nrepresentation, schedule, precision, certificate", face="#ede9fe", fontsize=10.8)
    _arrow(ax, (0.50, 0.73), (0.50, 0.65))
    _box(ax, 0.08, 0.20, 0.34, 0.22, "CUDA compatibility backend\nCUDA Graphs\nasynchronous copies\ngrouped GEMM, cuFFT, cuSPARSE, CUB", face="#dbeafe", fontsize=10.8)
    _box(ax, 0.58, 0.20, 0.34, 0.22, "PRISM backend\nPacket Streaming Multiprocessors\nresident factors and small solvers\nlocal refinement and certified commit", face="#dcfce7", fontsize=10.8)
    _arrow(ax, (0.43, 0.52), (0.25, 0.42))
    _arrow(ax, (0.57, 0.52), (0.75, 0.42))
    ax.text(0.5, 0.08, "The CUDA path is the software foundation and the matched baseline. PRISM accelerates the same Packet IR rather than replacing it with a different mathematics.", ha="center", fontsize=11.2, weight="bold")
    _save(fig, out, "40_shared_packet_ir")


def fig_gain_decomposition(out: Path) -> None:
    data = gain_decomposition()
    labels = ["representation\nreduction", "measured packet CUDA\nvs dense CUDA", "CUDA Graph gain\nsame representation", "compressed output\nvs materialization"]
    values = [float(data["representation_reduction_bdlr"]), float(data["measured_packet_gpu_gain_vs_dense_gpu"]), float(data["measured_cuda_graph_gain_same_representation"]), float(data["measured_compressed_output_gain"])]
    fig, ax = plt.subplots(figsize=(12.2, 6.3))
    bars = ax.bar(np.arange(len(values)), values)
    ax.set_yscale("log")
    ax.set_xticks(np.arange(len(values)), labels)
    ax.set_ylabel("Gain or reduction factor, logarithmic scale")
    ax.set_title("Separate the source of each gain", weight="bold")
    ax.grid(alpha=0.22, axis="y", which="both")
    for bar, value in zip(bars, values, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, value * 1.08, f"{value:.2f}x", ha="center", va="bottom", fontsize=10.5)
    fig.text(0.5, 0.01, "These factors answer different questions. They are not multiplied unless the timing scope, representation, and output contract match.", ha="center", fontsize=10.5)
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    _save(fig, out, "41_gain_decomposition")


def fig_output_contracts(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 6.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "Output contracts determine whether materialization is needed", ha="center", fontsize=21, weight="bold")
    _box(ax, 0.06, 0.42, 0.18, 0.20, "operator plan\npacket graph or factors", face="#fef3c7", fontsize=11.5)
    contracts = [
        (0.31, 0.70, "apply to vectors\nreturn Y"),
        (0.31, 0.49, "compressed operator\nreturn factors"),
        (0.31, 0.28, "transform plan\nreturn chain"),
        (0.31, 0.07, "explicit array\nreturn every entry"),
    ]
    outputs = [
        (0.68, 0.70, "streamed application\nno matrix object"),
        (0.68, 0.49, "BDLR, Kronecker, sparse chain\nno full array"),
        (0.68, 0.28, "FFT, wavelet, butterfly\nno full array"),
        (0.68, 0.07, "materialization command\nonly for this contract"),
    ]
    for (x, y, label), (_, _, output) in zip(contracts, outputs, strict=True):
        _box(ax, x, y, 0.23, 0.14, label, face="#f8fafc", fontsize=10.5)
        _box(ax, 0.68, y, 0.25, 0.14, output, face="#dbeafe" if y > 0.1 else "#fee2e2", fontsize=10.2)
        _arrow(ax, (0.24, 0.52), (x, y + 0.07), rad=0.04)
        _arrow(ax, (x + 0.23, y + 0.07), (0.68, y + 0.07))
    ax.text(0.5, 0.02, "The architecture preserves the requested mathematical result, not an unnecessary intermediate representation.", ha="center", fontsize=11.3, weight="bold")
    _save(fig, out, "42_output_contracts")


def fig_cuda_measured_baselines(out: Path) -> None:
    data = measured_cuda_baselines()
    labels = ["equal block\npacket", "BDLR standard\npacket", "BDLR graph\npacket", "compressed\nproduct", "materialized\nproduct"]
    values = [
        float(data["equal_block_packet_ms"]),
        float(data["bdlr_standard_packet_ms"]),
        float(data["bdlr_graph_packet_ms"]),
        float(data["compressed_product_ms"]),
        float(data["materialized_product_ms"]),
    ]
    fig, ax = plt.subplots(figsize=(12.4, 6.2))
    bars = ax.bar(np.arange(len(values)), values)
    ax.set_xticks(np.arange(len(values)), labels)
    ax.set_ylabel("Measured time in milliseconds")
    ax.set_title("Existing CUDA packet algorithms provide the software foundation", weight="bold")
    ax.grid(alpha=0.22, axis="y")
    for bar, value in zip(bars, values, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, value + max(values) * 0.025, f"{value:.4f}", ha="center", va="bottom", fontsize=10)
    fig.text(0.5, 0.01, "Prior measurements on an RTX 3070 Ti Laptop GPU. Compressed and materialized product rows have different output contracts.", ha="center", fontsize=10.4)
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    _save(fig, out, "43_cuda_measured_baselines")


def generate_all(root: Path) -> dict[str, object]:
    config = PrismConfig()
    figures = root / "figures"
    results_dir = root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    dense = dense_apply_estimate(config, 8192, 32)
    bdlr = bdlr_estimate(config, 8192, 64, 8, 32)
    sparse = block_sparse_estimate(config, 128, 64, 5, 32)
    atlas_base, atlas_prism = multi_atlas_estimate(config, 1024 * 1024, 5)
    edge_base, edge_prism = edge_recovery_estimate(config, 16384, 12)
    bayes_base, bayes_prism = bayes_estimate(config, 256, 4096, 96, 8)

    estimates = [dense, bdlr, sparse, atlas_base, atlas_prism, edge_base, edge_prism, bayes_base, bayes_prism]
    pairs = [(dense, bdlr), (atlas_base, atlas_prism), (edge_base, edge_prism), (bayes_base, bayes_prism)]

    fig_package(config, figures)
    fig_tile(config, figures)
    fig_calculus_pipeline(figures)
    fig_descriptor(figures)
    fig_transfer_descriptor(figures)
    fig_memory(config, figures)
    fig_bdlr(figures)
    fig_transform(figures)
    fig_edge_pipeline(figures)
    fig_bayes(figures)
    fig_scheduler(figures)
    fig_compiler(figures)
    fig_workload_map(figures)
    fig_roofline(config, [bdlr, sparse, atlas_prism, edge_prism, bayes_prism], figures)
    fig_performance(pairs, figures)
    fig_memory_reduction(figures)
    fig_power(config, figures)
    fig_area(figures)
    fig_precision(figures)
    fig_network(figures)
    fig_isa(figures)
    fig_prototype(figures)
    fig_negative_controls(figures)
    fig_packet_lifecycle(figures)
    fig_workload_router(figures)
    fig_chiplet_floorplan(config, figures)
    fig_bandwidth_budget(config, figures)
    fig_command_state_machine(figures)
    fig_bdlr_sensitivity(config, figures)
    fig_bdlr_storage_sensitivity(config, figures)
    fig_solver_pipeline(figures)
    fig_pr_lasm_state_map(figures)
    fig_verification_pyramid(figures)
    fig_fpga_overlay(figures)
    fig_risk_matrix(figures)
    fig_compiler_trace(figures)
    fig_packet_streaming_multiprocessor(config, figures)
    fig_mixed_representation_space(figures)
    fig_pmr_gemm_planner(figures)
    fig_shared_packet_ir(figures)
    fig_gain_decomposition(figures)
    fig_output_contracts(figures)
    fig_cuda_measured_baselines(figures)

    tests = run_self_tests()
    result = {
        "config": asdict(config),
        "derived": {
            "packet_streaming_multiprocessors": config.psms,
            "execution_groups": config.execution_groups,
            "tiles": config.tiles,
            "packet_streaming_multiprocessors_per_chiplet": config.packet_streaming_multiprocessors_per_chiplet,
            "execution_groups_per_psm": config.execution_groups_per_psm,
            "fp16_tflops": config.fp16_tflops,
            "fp32_tflops": config.fp32_tflops,
            "fp64_tflops": config.fp64_tflops,
            "total_hbm_gib": config.total_hbm_gib,
            "total_hbm_tbps": config.total_hbm_tbps,
            "total_sram_mib": config.total_sram_mib,
        },
        "estimates": [asdict(e) for e in estimates],
        "modeled_speedups": {
            p[1].workload: p[0].total_time_us / p[1].total_time_us for p in pairs
        },
        "self_tests": tests,
        "bdlr_sensitivity": bdlr_sensitivity_tables(config),
        "measured_cuda_baselines": measured_cuda_baselines(),
        "gain_decomposition": gain_decomposition(),
        "representation_forms": list(REPRESENTATION_FORMS),
        "output_contracts": list(OUTPUT_CONTRACTS),
        "bandwidth_budget_tbps": {
            "host": config.host_bidirectional_gbps / 1000.0,
            "hbm": config.total_hbm_tbps,
            "package": config.package_network_tbps,
        },
        "figure_pairs": 43,
    }
    (results_dir / "prism_chip_results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def run_self_tests() -> dict[str, float | int | bool]:
    rng = np.random.default_rng(20260730)

    x = rng.normal(size=64)
    packets = [residue_project(x, 4, r) for r in range(4)]
    packet_residual = float(np.max(np.abs(sum(packets, np.zeros_like(x)) - x)))

    channels = polyphase_analyze(x, 4)
    polyphase_residual = float(np.max(np.abs(polyphase_synthesize(channels, length=x.size) - x)))

    low, high = haar_analyze(x)
    haar_residual = float(np.max(np.abs(haar_synthesize(low, high) - x)))

    blocks = [rng.normal(size=(8, 8)) for _ in range(8)]
    u = rng.normal(size=(64, 4))
    v = rng.normal(size=(64, 4))
    y_structured = bdlr_apply(blocks, u, v, x)
    y_dense = materialize_bdlr(blocks, u, v) @ x
    bdlr_residual = float(np.max(np.abs(y_structured - y_dense)))

    nodes = {"A", "B", "v", "C", "D"}
    edges = {("A", "B"), ("B", "v"), ("v", "C"), ("C", "D")}
    local_nodes = {"v0", "v1", "v2"}
    local_edges = {("v0", "v1"), ("v1", "v2")}
    new_nodes, new_edges, order = substitute_task(nodes, edges, "v", local_nodes, local_edges, {"v0"}, {"v2"})
    schedule_ok = set(order) == new_nodes and all(order.index(a) < order.index(b) for a, b in new_edges)

    config = PrismConfig()
    derived_ok = (
        config.psms == 64
        and config.execution_groups == 256
        and config.tiles == 256
        and abs(config.total_hbm_tbps - 11.2) < 1e-12
        and abs(config.total_sram_mib - 192.0) < 1e-12
    )

    descriptor = PacketDescriptor(1, 0, 2, "residue", (64,), 0x1000, 4, "fp32", 1e-5)
    edge = TransferDescriptor(1, 1, 2, "bdlr", 64, 64, 4, "fp32", 0.3, 9)
    descriptor_ok = descriptor.packet_id == edge.src_packet and descriptor.bytes_per_element == 4

    sensitivities = np.array([0.2, 0.5, 1.0, 2.0])
    costs = np.array([1.0, 2.0, 1.0, 3.0])
    tau = 0.025
    eps = precision_allocation(sensitivities, costs, tau)
    precision_budget_ok = abs(float(np.dot(sensitivities, eps)) - tau) < 1e-14

    commit_ok = certificate_commit_allowed(True, True, 8e-6, 1e-5)
    commit_rejects = not certificate_commit_allowed(True, True, 2e-5, 1e-5)

    refinement_bound_ok = local_refinement_descriptor_bound(3, 2, 1, 1, 1, 1) == 7

    routing_ok = (
        route_workload("bdlr", 12.0, 8, 32) == "prism"
        and route_workload("dense", 1.0, 1, 1) == "dense_path"
        and route_workload("transform", 1.1, 1, 2) == "host_or_general_device"
    )

    table = bdlr_sensitivity_tables(config)
    sensitivity_ok = (
        len(table["block_sizes"]) == 5
        and len(table["ranks"]) == 5
        and np.all(np.asarray(table["modeled_speedups"]) > 1.0)
        and np.all(np.asarray(table["storage_reduction"]) > 1.0)
    )

    bandwidth_ok = (
        config.package_network_tbps > config.total_hbm_tbps
        and config.total_hbm_tbps > config.host_bidirectional_gbps / 1000.0
    )

    options = {
        "root": (
            PlanChoice("dense", "explicit_dense", 100.0),
            PlanChoice("transform", "transform_domain", 8.0),
            PlanChoice("split", "packet_graph", 1.0, children=("left", "right")),
        ),
        "left": (
            PlanChoice("left_block", "block_diagonal", 2.0),
            PlanChoice("left_dense", "explicit_dense", 20.0),
        ),
        "right": (
            PlanChoice("right_low_rank", "low_rank", 2.5, local_error=0.01),
            PlanChoice("right_dense", "explicit_dense", 18.0),
        ),
    }
    compressed_plan = pmr_plan("root", options, error_weight=10.0, output_contract="factor_graph")
    explicit_plan = pmr_plan("root", options, error_weight=10.0, output_contract="explicit_array")
    pmr_optimal_ok = compressed_plan.choice == "split" and explicit_plan.choice == "dense"

    contract_ok = (
        output_contract_allows("bdlr", "apply")
        and output_contract_allows("bdlr", "factor_graph")
        and not output_contract_allows("bdlr", "explicit_array")
        and output_contract_allows("explicit_dense", "explicit_array")
    )

    cuda = measured_cuda_baselines()
    cuda_rows_ok = (
        abs(float(cuda["bdlr_graph_replay_gain"]) - (0.097280 / 0.079872)) < 1e-12
        and float(cuda["bdlr_speedup_vs_gpu_dense"]) > 1.0
        and float(cuda["compressed_output_gain"]) > 1.0
    )

    decomposition = gain_decomposition()
    gain_decomposition_ok = (
        float(decomposition["representation_reduction_bdlr"]) == 102.4
        and float(decomposition["measured_packet_gpu_gain_vs_dense_gpu"]) > 1.0
    )

    representation_registry_ok = (
        len(REPRESENTATION_FORMS) == 9
        and len(OUTPUT_CONTRACTS) == 5
        and "explicit_dense" in REPRESENTATION_FORMS
        and "packet_graph" in REPRESENTATION_FORMS
    )

    result = {
        "packet_reconstruction_residual": packet_residual,
        "polyphase_residual": polyphase_residual,
        "haar_residual": haar_residual,
        "bdlr_residual": bdlr_residual,
        "local_schedule_valid": bool(schedule_ok),
        "derived_configuration_valid": bool(derived_ok),
        "descriptor_contract_valid": bool(descriptor_ok),
        "precision_budget_valid": bool(precision_budget_ok),
        "commit_protocol_valid": bool(commit_ok and commit_rejects),
        "local_refinement_bound_valid": bool(refinement_bound_ok),
        "routing_policy_valid": bool(routing_ok),
        "sensitivity_tables_valid": bool(sensitivity_ok),
        "bandwidth_hierarchy_valid": bool(bandwidth_ok),
        "pmr_planner_valid": bool(pmr_optimal_ok),
        "output_contracts_valid": bool(contract_ok),
        "cuda_baseline_registry_valid": bool(cuda_rows_ok),
        "gain_decomposition_valid": bool(gain_decomposition_ok),
        "representation_registry_valid": bool(representation_registry_ok),
        "tests_passed": int(packet_residual < 1e-12)
        + int(polyphase_residual < 1e-12)
        + int(haar_residual < 1e-12)
        + int(bdlr_residual < 1e-11)
        + int(schedule_ok)
        + int(derived_ok)
        + int(descriptor_ok)
        + int(precision_budget_ok)
        + int(commit_ok and commit_rejects)
        + int(refinement_bound_ok)
        + int(routing_ok)
        + int(sensitivity_ok)
        + int(bandwidth_ok)
        + int(pmr_optimal_ok)
        + int(contract_ok)
        + int(cuda_rows_ok)
        + int(gain_decomposition_ok)
        + int(representation_registry_ok),
        "tests_total": 18,
    }
    if result["tests_passed"] != result["tests_total"]:
        raise RuntimeError(f"self tests failed: {result}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the Komorebi PRISM-1 architecture model and figures")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    result = generate_all(args.root)
    print(json.dumps({"status": "ok", "tests": result["self_tests"], "figure_pairs": result["figure_pairs"]}, indent=2))


if __name__ == "__main__":
    main()
