from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from .edges import (
    boundary_band,
    estimated_edge_reconstruct_1d,
    estimated_edge_reconstruct_2d,
    exact_edge_reconstruct_1d,
    exact_edge_reconstruct_2d,
    fft_lowpass_1d,
    fft_lowpass_2d,
    mask_iou,
    rmse,
)
from .filterbanks import (
    haar_analyze,
    haar_packet_analyze,
    haar_packet_synthesize,
    haar_synthesize,
    lifting_analyze,
    lifting_synthesize,
    packet_energy,
)
from .nonlinear import coefficient_packets, nonlinear_packet_reconstruct, nonlinear_shift_filter, packet_product
from .polyphase import polyphase_analyze, polyphase_convolution, polyphase_synthesize, verify_refinement
from .adaptive import (
    all_haar_packet_nodes,
    best_pruning,
    enumerate_prunings,
    optimum_gap,
    packet_tree_costs,
    perturbation_envelope,
    pruning_cost,
    stable_by_gap,
    synthesize_pruning,
)
from .smith import (
    admittance_from_gamma,
    constant_reactance_arc,
    constant_resistance_circle,
    gamma_from_z,
    phase_mobius,
    rotate_gamma,
    smith_sensitivity,
    z_from_gamma,
)


def make_signal_1d(n: int = 1024) -> dict[str, np.ndarray]:
    t = np.linspace(-1.0, 1.0, n, endpoint=False)
    smooth = (
        0.18
        + 0.11 * np.cos(2 * np.pi * t)
        + 0.05 * np.exp(-((t + 0.55) ** 2) / 0.07)
        + 0.035 * np.exp(-((t - 0.52) ** 2) / 0.04)
    )
    mask = np.abs(t) <= 0.34
    edge = 0.72 * mask.astype(float)
    return {"t": t, "smooth": smooth, "mask": mask, "edge": edge, "signal": smooth + edge}


def make_disk_2d(n: int = 192) -> dict[str, np.ndarray]:
    x = np.linspace(-1.0, 1.0, n, endpoint=False)
    X, Y = np.meshgrid(x, x)
    smooth = (
        0.18
        + 0.16 * np.exp(-((X + 0.40) ** 2 + (Y + 0.28) ** 2) / 0.09)
        + 0.10 * np.exp(-((X - 0.38) ** 2 + (Y - 0.30) ** 2) / 0.07)
        + 0.04 * np.cos(np.pi * X) * np.cos(np.pi * Y)
    )
    mask = X**2 + Y**2 <= 0.40**2
    edge = 0.64 * mask.astype(float)
    return {"x": x, "X": X, "Y": Y, "smooth": smooth, "mask": mask, "edge": edge, "image": smooth + edge}


def make_multiedge_2d(n: int = 192) -> dict[str, np.ndarray]:
    x = np.linspace(-1.0, 1.0, n, endpoint=False)
    X, Y = np.meshgrid(x, x)
    smooth = 0.16 + 0.10 * np.cos(np.pi * X) * np.cos(np.pi * Y) + 0.03 * np.cos(2 * np.pi * X) + 0.045 * np.exp(-((X - 0.08) ** 2 + (Y + 0.04) ** 2) / 0.11)
    disk = (X + 0.38) ** 2 + (Y - 0.15) ** 2 <= 0.27**2
    square = (np.abs(X - 0.35) <= 0.25) & (np.abs(Y + 0.28) <= 0.19)
    diamond = np.abs(X + 0.02) + np.abs(Y + 0.50) <= 0.18
    edge = 0.55 * disk.astype(float) + 0.42 * square.astype(float) + 0.33 * diamond.astype(float)
    mask = disk | square | diamond
    return {"x": x, "X": X, "Y": Y, "smooth": smooth, "mask": mask, "edge": edge, "image": smooth + edge}


def sparse_haar_packet_reconstruction(signal: np.ndarray, depth: int, keep: int) -> tuple[np.ndarray, int]:
    packets = haar_packet_analyze(signal, depth)
    entries: list[tuple[float, str, int]] = []
    for path, values in packets.items():
        for idx, value in enumerate(values):
            entries.append((abs(complex(value)), path, idx))
    entries.sort(reverse=True, key=lambda row: row[0])
    selected = {(path, idx) for _, path, idx in entries[:keep]}
    truncated = {
        path: np.array([value if (path, idx) in selected else 0 for idx, value in enumerate(values)])
        for path, values in packets.items()
    }
    return haar_packet_synthesize(truncated), len(selected)


def run_experiments(root: str | Path) -> dict:
    root = Path(root)
    (root / "results").mkdir(parents=True, exist_ok=True)
    (root / "tables").mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260727)

    # Exact residue and filtering checks.
    x = rng.normal(size=257)
    h = np.array([0.15, -0.2, 0.45, 0.8, 0.45, -0.2, 0.15])
    polyphase_reconstruction = float(
        np.max(np.abs(polyphase_synthesize(polyphase_analyze(x, 5), 5, len(x)) - x))
    )
    refinement_residual = verify_refinement(x, 4, 16)
    convolution_residual = float(np.max(np.abs(np.convolve(x, h) - polyphase_convolution(x, h, 4))))

    # Haar and lifting checks.
    xh = rng.normal(size=512)
    low, high = haar_analyze(xh)
    haar_reconstruction = float(np.max(np.abs(haar_synthesize(low, high) - xh)))
    haar_energy = float(abs(np.vdot(xh, xh).real - np.vdot(low, low).real - np.vdot(high, high).real))
    packets = haar_packet_analyze(xh, 4)
    packet_reconstruction = float(np.max(np.abs(haar_packet_synthesize(packets) - xh)))
    packet_energy_residual = float(abs(np.vdot(xh, xh).real - packet_energy(packets)))
    smooth_lift, detail_lift = lifting_analyze(xh)
    lifting_reconstruction = float(np.max(np.abs(lifting_synthesize(smooth_lift, detail_lift) - xh)))

    # One-dimensional edge study.
    case1 = make_signal_1d()
    modes = 18
    global1 = fft_lowpass_1d(case1["signal"], modes)
    known1 = exact_edge_reconstruct_1d(case1["smooth"], case1["edge"], modes)
    estimated1, mask1, amplitude1 = estimated_edge_reconstruct_1d(case1["signal"], modes)
    one_d = {
        "global_rmse": rmse(case1["signal"], global1),
        "known_packet_rmse": rmse(case1["signal"], known1),
        "estimated_packet_rmse": rmse(case1["signal"], estimated1),
        "estimated_mask_iou": mask_iou(case1["mask"], mask1),
        "estimated_amplitude": amplitude1,
        "global_max_error": float(np.max(np.abs(case1["signal"] - global1))),
        "known_packet_max_error": float(np.max(np.abs(case1["signal"] - known1))),
        "estimated_packet_max_error": float(np.max(np.abs(case1["signal"] - estimated1))),
    }

    # Two-dimensional edge study.
    case2 = make_disk_2d()
    cutoff = 16
    global2 = fft_lowpass_2d(case2["image"], cutoff)
    known2 = exact_edge_reconstruct_2d(case2["smooth"], case2["edge"], cutoff)
    estimated2, mask2, amplitude2 = estimated_edge_reconstruct_2d(case2["image"], cutoff)
    band = boundary_band(case2["mask"], 3)
    two_d = {
        "global_rmse": rmse(case2["image"], global2),
        "known_packet_rmse": rmse(case2["image"], known2),
        "estimated_packet_rmse": rmse(case2["image"], estimated2),
        "estimated_mask_iou": mask_iou(case2["mask"], mask2),
        "estimated_amplitude": amplitude2,
        "global_boundary_rmse": rmse(case2["image"][band], global2[band]),
        "known_packet_boundary_rmse": rmse(case2["image"][band], known2[band]),
        "estimated_packet_boundary_rmse": rmse(case2["image"][band], estimated2[band]),
    }

    # Multi-edge known-packet stress test.
    multi = make_multiedge_2d()
    global_multi = fft_lowpass_2d(multi["image"], 18)
    known_multi = exact_edge_reconstruct_2d(multi["smooth"], multi["edge"], 18)
    multi_d = {
        "global_rmse": rmse(multi["image"], global_multi),
        "known_packet_rmse": rmse(multi["image"], known_multi),
        "global_max_error": float(np.max(np.abs(multi["image"] - global_multi))),
        "known_packet_max_error": float(np.max(np.abs(multi["image"] - known_multi))),
    }

    # Sparse representation comparison.
    sparse_signal = case1["signal"] - np.mean(case1["signal"])
    sparse_rows = []
    for keep in (16, 32, 64, 128, 256):
        wavelet, count = sparse_haar_packet_reconstruction(sparse_signal, depth=5, keep=keep)
        spectrum = np.fft.fft(sparse_signal)
        order = np.argsort(np.abs(spectrum))[::-1]
        kept = np.zeros_like(spectrum)
        kept[order[:keep]] = spectrum[order[:keep]]
        fourier = np.real(np.fft.ifft(kept))
        sparse_rows.append(
            {
                "kept_coefficients": count,
                "wavelet_packet_rmse": rmse(sparse_signal, wavelet),
                "best_magnitude_fourier_rmse": rmse(sparse_signal, fourier),
            }
        )

    # Globally optimal adaptive packet tree with an exact synthesis certificate.
    ta = np.linspace(0.0, 1.0, 128, endpoint=False)
    adaptive_signal = (
        np.sin(2 * np.pi * 5 * ta)
        + 0.35 * np.sin(2 * np.pi * 17 * ta) * (ta < 0.5)
        + 0.80 * ((ta > 0.62) & (ta < 0.78)).astype(float)
    )
    adaptive_depth = 5
    adaptive_nodes = all_haar_packet_nodes(adaptive_signal, adaptive_depth)
    adaptive_cost = packet_tree_costs(
        adaptive_nodes, adaptive_depth, complexity_per_node=0.002
    )
    adaptive_optimum = best_pruning(adaptive_cost, adaptive_depth)
    adaptive_reconstructed = synthesize_pruning(
        adaptive_nodes, adaptive_optimum.nodes, adaptive_depth
    )
    adaptive_gap = optimum_gap(adaptive_cost, adaptive_depth)
    local_noise_bound = {path: 1.0e-6 for path in adaptive_cost}
    adaptive_envelope = perturbation_envelope(local_noise_bound, adaptive_depth)
    brute_cost = min(
        pruning_cost(pruning, adaptive_cost)
        for pruning in enumerate_prunings(adaptive_depth)
    )
    adaptive_tree = {
        "maximum_depth": adaptive_depth,
        "pruning_count": len(enumerate_prunings(adaptive_depth)),
        "selected_nodes": list(adaptive_optimum.nodes),
        "selected_node_count": len(adaptive_optimum.nodes),
        "dynamic_programming_cost": adaptive_optimum.cost,
        "brute_force_cost": brute_cost,
        "optimality_residual": abs(adaptive_optimum.cost - brute_cost),
        "mixed_depth_reconstruction_residual": float(
            np.max(np.abs(adaptive_reconstructed - adaptive_signal))
        ),
        "global_optimum_gap": adaptive_gap,
        "cost_perturbation_envelope": adaptive_envelope,
        "stability_certificate": stable_by_gap(adaptive_gap, adaptive_envelope),
    }

    # Smith coordinate certificates.
    z = np.array([0.25 + 0.5j, 1.5 - 0.25j, 4.0 + 3.0j])
    smith_roundtrip = float(np.max(np.abs(z_from_gamma(gamma_from_z(z)) - z)))
    smith_rotation = float(
        max(
            np.max(np.abs(gamma_from_z(phase_mobius(z, N, k)) - rotate_gamma(gamma_from_z(z), N, k)))
            for N in (2, 3, 4, 8, 16)
            for k in range(N)
        )
    )
    smith_n2 = float(np.max(np.abs(phase_mobius(z, 2, 1) - 1 / z)))
    smith_duality = float(
        np.max(np.abs(admittance_from_gamma(gamma_from_z(z)) - z_from_gamma(-gamma_from_z(z))))
    )
    circle_residual = 0.0
    for resistance in (0.0, 0.2, 0.5, 1, 2, 5):
        gamma = constant_resistance_circle(resistance, 600)
        residual = (gamma.real - resistance / (1 + resistance)) ** 2 + gamma.imag**2 - 1 / (1 + resistance) ** 2
        circle_residual = max(circle_residual, float(np.max(np.abs(residual))))
    for reactance in (-5, -1, -0.2, 0.2, 1, 5):
        gamma = constant_reactance_arc(reactance, 800)
        residual = (gamma.real - 1) ** 2 + (gamma.imag - 1 / reactance) ** 2 - 1 / reactance**2
        circle_residual = max(circle_residual, float(np.max(np.abs(residual))))
    gamma_probe = np.array([0.2 + 0.3j, -0.4 + 0.1j, 0.7 - 0.2j])
    sensitivity_symmetry = float(np.max(np.abs(smith_sensitivity(gamma_probe) - smith_sensitivity(-gamma_probe))))

    # Nonlinear packet interactions.
    a = rng.normal(size=17)
    b = rng.normal(size=13)
    direct_product = np.convolve(a, b)
    product_packets = packet_product(a, b, 5)
    product_residual = float(np.max(np.abs(sum(product_packets, np.zeros_like(direct_product)) - direct_product)))
    nonlinear_direct = nonlinear_shift_filter(x, 0.35)
    nonlinear_residual = float(np.max(np.abs(nonlinear_packet_reconstruct(x, 7, 0.35) - nonlinear_direct)))

    results = {
        "author": "Komorebi P.",
        "paper": "Projector-Resolved Seed Calculus V",
        "computational_scope": "CPU finite and numerical certificates; no GPU claim",
        "exact_certificates": {
            "polyphase_reconstruction_residual": polyphase_reconstruction,
            "nested_refinement_residual": refinement_residual,
            "polyphase_convolution_residual": convolution_residual,
            "haar_reconstruction_residual": haar_reconstruction,
            "haar_energy_residual": haar_energy,
            "wavelet_packet_reconstruction_residual": packet_reconstruction,
            "wavelet_packet_energy_residual": packet_energy_residual,
            "lifting_reconstruction_residual": lifting_reconstruction,
            "smith_roundtrip_residual": smith_roundtrip,
            "smith_rotation_residual": smith_rotation,
            "smith_n2_inversion_residual": smith_n2,
            "smith_admittance_duality_residual": smith_duality,
            "smith_circle_residual": circle_residual,
            "smith_sensitivity_symmetry_residual": sensitivity_symmetry,
            "nonlinear_product_packet_residual": product_residual,
            "nonlinear_filter_reconstruction_residual": nonlinear_residual,
        },
        "one_dimensional_edge_study": one_d,
        "two_dimensional_edge_study": two_d,
        "multi_edge_study": multi_d,
        "sparse_representation_study": sparse_rows,
        "adaptive_packet_tree": adaptive_tree,
    }
    (root / "results" / "numerical_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    summary_rows: list[tuple[str, float | str]] = []
    for key, value in results["exact_certificates"].items():
        summary_rows.append((key, float(value)))
    for prefix, mapping in (("edge_1d", one_d), ("edge_2d", two_d), ("multi_edge", multi_d)):
        for key, value in mapping.items():
            summary_rows.append((f"{prefix}_{key}", float(value)))
    with (root / "tables" / "numerical_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerows(summary_rows)
    with (root / "tables" / "sparse_representation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sparse_rows[0]))
        writer.writeheader()
        writer.writerows(sparse_rows)
    with (root / "tables" / "adaptive_packet_tree.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value"])
        for key, value in adaptive_tree.items():
            writer.writerow([key, "|".join(value) if isinstance(value, list) else value])
    return results
