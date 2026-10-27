from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import expm

from .basic import X, Z, basis_state, ketbra, packet_blocks
from .circuits import bell_circuit
from .codes import syndrome_projectors
from .dynamics import feshbach_effective, projected_resolvent
from .geometry import causal_volume_hamiltonian, euclidean_transfer
from .symmetry import parity_projectors


def _save(fig: plt.Figure, out: Path, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{stem}.png", dpi=220, bbox_inches="tight")
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def make_visuals(results_path: str | Path, output_dir: str | Path) -> list[str]:
    data = json.loads(Path(results_path).read_text(encoding="utf-8"))
    out = Path(output_dir)
    stems: list[str] = []

    # 1. Common architecture.
    labels = ["seed", "gates", "project", "transfer", "refine", "constrain", "reconstruct"]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10.5, 2.8))
    ax.scatter(x, np.zeros_like(x), s=220)
    for i, label in enumerate(labels):
        ax.text(i, 0.13 if i % 2 == 0 else -0.16, label, ha="center", va="center", fontsize=11)
        if i + 1 < len(labels):
            ax.annotate("", xy=(i + 1 - 0.13, 0), xytext=(i + 0.13, 0), arrowprops={"arrowstyle": "->"})
    ax.set_ylim(-0.35, 0.35)
    ax.axis("off")
    ax.set_title("Quantum realization of the seed calculus")
    _save(fig, out, "01_quantum_seed_architecture")
    stems.append("01_quantum_seed_architecture")

    # 2. Bell state amplitudes.
    _, _, bell = bell_circuit()
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.bar(["00", "01", "10", "11"], np.abs(bell) ** 2)
    ax.set_ylim(0, 0.6)
    ax.set_ylabel("probability")
    ax.set_title("Bell state generated from the seed |00>")
    _save(fig, out, "02_bell_seed_probabilities")
    stems.append("02_bell_seed_probabilities")

    # 3. Parity block Hamiltonian.
    p_even, p_odd = parity_projectors(2)
    h = 0.8 * np.kron(X, X) + 0.35 * (np.kron(Z, np.eye(2)) + np.kron(np.eye(2), Z))
    order = [0, 3, 1, 2]
    block_h = h[np.ix_(order, order)].real
    fig, ax = plt.subplots(figsize=(6.2, 5.3))
    image = ax.imshow(block_h, aspect="equal")
    fig.colorbar(image, ax=ax, label="matrix entry")
    ax.set_xticks(range(4), ["00", "11", "01", "10"])
    ax.set_yticks(range(4), ["00", "11", "01", "10"])
    ax.set_title("Parity-resolved two-qubit Hamiltonian")
    _save(fig, out, "03_parity_block_hamiltonian")
    stems.append("03_parity_block_hamiltonian")

    # 4. Circuit packet paths.
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    layers = [0, 1, 2]
    for layer in layers:
        ax.scatter([layer, layer], [0, 1], s=130)
        ax.text(layer, -0.18, ["seed", "H", "CNOT"][layer], ha="center")
    for layer in [0, 1]:
        for a in [0, 1]:
            for b in [0, 1]:
                ax.plot([layer, layer + 1], [a, b], alpha=0.5)
    ax.text(-0.14, 0, "even", ha="right", va="center")
    ax.text(-0.14, 1, "odd", ha="right", va="center")
    ax.set_xlim(-0.5, 2.4)
    ax.set_ylim(-0.35, 1.25)
    ax.axis("off")
    ax.set_title("Exact circuit reconstruction as a sum over packet paths")
    _save(fig, out, "04_circuit_packet_paths")
    stems.append("04_circuit_packet_paths")

    # 5. Leakage and bound.
    s = data["series"]
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(s["leakage_times"], s["leakage"], label="measured leakage norm")
    ax.plot(s["leakage_times"], s["leakage_bound"], label="commutator bound")
    ax.set_xlabel("time")
    ax.set_ylabel("norm")
    ax.set_title("Symmetry breaking and the leakage bound")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "05_leakage_bound")
    stems.append("05_leakage_bound")

    # 6. Feshbach versus bare truncation.
    vals = [data["effective_dynamics"]["feshbach_resolvent_error"], data["effective_dynamics"]["bare_truncation_error"]]
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    ax.bar(["exact Feshbach", "bare truncation"], vals)
    ax.set_yscale("log")
    ax.set_ylabel("projected-resolvent error")
    ax.set_title("Hidden packets return as a self-energy")
    _save(fig, out, "06_feshbach_vs_truncation")
    stems.append("06_feshbach_vs_truncation")

    # 7. Packet Green function norms.
    green = np.array(data["effective_dynamics"]["packet_green_block_norms"])
    fig, ax = plt.subplots(figsize=(5.8, 5.0))
    image = ax.imshow(green, aspect="equal")
    fig.colorbar(image, ax=ax, label="block Frobenius norm")
    ax.set_xticks([0, 1], ["source even", "source odd"])
    ax.set_yticks([0, 1], ["target even", "target odd"])
    ax.set_title("Packet-resolved Green operator")
    _save(fig, out, "07_packet_green_blocks")
    stems.append("07_packet_green_blocks")

    # 8. Moving-frame correction.
    vals = [data["effective_dynamics"]["moving_frame_error"], data["effective_dynamics"]["omitted_connection_error"]]
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    ax.bar(["with connection", "connection omitted"], vals)
    ax.set_yscale("log")
    ax.set_ylabel("equation residual")
    ax.set_title("A moving coordinate frame requires its connection")
    _save(fig, out, "08_moving_frame_connection")
    stems.append("08_moving_frame_connection")

    # 9. Bloch curvature.
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    ax.plot(s["theta"], s["curvature"], label="finite-difference curvature")
    ax.plot(s["theta"], s["curvature_target"], label=r"$\frac{1}{2}\sin\theta$")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("curvature density")
    ax.set_title("Rank-one Bloch projector curvature")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "09_bloch_curvature")
    stems.append("09_bloch_curvature")

    # 10. Tensor refinement tree.
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    fine_y = np.linspace(0, 1, 8)
    for i, y in enumerate(fine_y):
        ax.scatter(2, y, s=90)
        parity = bin(i).count("1") % 2
        ax.plot([1.05, 1.92], [0.25 if parity == 0 else 0.75, y], alpha=0.65)
        ax.text(2.06, y, format(i, "03b"), va="center", fontsize=9)
    ax.scatter([1, 1], [0.25, 0.75], s=170)
    ax.text(0.82, 0.25, "even", ha="right", va="center")
    ax.text(0.82, 0.75, "odd", ha="right", va="center")
    ax.text(1.5, -0.15, "fine tensor packets refine total parity exactly", ha="center")
    ax.set_xlim(0.3, 2.5)
    ax.set_ylim(-0.25, 1.1)
    ax.axis("off")
    ax.set_title("Tensor/polyphase refinement of three-qubit parity")
    _save(fig, out, "10_tensor_parity_refinement")
    stems.append("10_tensor_parity_refinement")

    # 11. Circle low-mode convergence.
    fig, ax = plt.subplots(figsize=(7.7, 4.8))
    ax.loglog(s["spacing"], s["low_mode_error"], marker="o", label="dispersion error")
    ax.loglog(s["spacing"], s["low_mode_bound"], marker=".", label=r"$k^4h^2/12$")
    ax.set_xlabel("lattice spacing")
    ax.set_ylabel("error")
    ax.set_title("Second-order continuum convergence of the circle Laplacian")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "11_circle_low_mode_convergence")
    stems.append("11_circle_low_mode_convergence")

    # 12. Spectral dimension.
    fig, ax = plt.subplots(figsize=(8.0, 4.9))
    ax.semilogx(s["tau"], s["spectral_dimension_1d"], label="1D cycle")
    ax.semilogx(s["tau"], s["spectral_dimension_2d"], label="2D torus")
    ax.axhline(1, linestyle="--", linewidth=1)
    ax.axhline(2, linestyle="--", linewidth=1)
    ax.set_xlabel(r"diffusion time $\tau$")
    ax.set_ylabel(r"spectral dimension $d_s(\tau)$")
    ax.set_title("Finite spectral-dimension diagnostics")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "12_spectral_dimension")
    stems.append("12_spectral_dimension")

    # 13. Euclidean transfer spectrum.
    hv = causal_volume_hamiltonian(42, kappa=0.8, confinement=0.012)
    tv = euclidean_transfer(hv, 0.35)
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.plot(np.linalg.eigvalsh(tv)[::-1], marker=".", linestyle="none")
    ax.set_yscale("log")
    ax.set_xlabel("ordered mode")
    ax.set_ylabel("transfer eigenvalue")
    ax.set_title("Positive Euclidean transfer spectrum")
    ax.grid(alpha=0.25)
    _save(fig, out, "13_euclidean_transfer_spectrum")
    stems.append("13_euclidean_transfer_spectrum")

    # 14. Causal volume ground state.
    ground = np.array(s["volume_ground_probability"])
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(np.arange(1, len(ground) + 1), ground, marker="o", markersize=3)
    ax.set_xlabel("discrete spatial volume")
    ax.set_ylabel("ground-state probability")
    ax.set_title("Controlled causal-volume transfer toy model")
    ax.grid(alpha=0.25)
    _save(fig, out, "14_causal_volume_ground_state")
    stems.append("14_causal_volume_ground_state")

    # 15. Transfer matrix heatmap.
    fig, ax = plt.subplots(figsize=(6.5, 5.7))
    image = ax.imshow(tv, aspect="auto")
    fig.colorbar(image, ax=ax, label="transfer amplitude")
    ax.set_xlabel("source volume")
    ax.set_ylabel("target volume")
    ax.set_title("Euclidean volume-transfer kernel")
    _save(fig, out, "15_causal_volume_transfer")
    stems.append("15_causal_volume_transfer")

    # 16. Quantum channel damping.
    damped = np.array(data["channels"]["damped_excited_density"], dtype=float)
    fig, ax = plt.subplots(figsize=(5.8, 4.7))
    image = ax.imshow(damped, aspect="equal")
    fig.colorbar(image, ax=ax, label="density entry")
    ax.set_xticks([0, 1], ["0", "1"])
    ax.set_yticks([0, 1], ["0", "1"])
    ax.set_title("Amplitude damping as packet transfer")
    _save(fig, out, "16_amplitude_damping_channel")
    stems.append("16_amplitude_damping_channel")

    # 17. Conjectural continuum tower.
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    levels = np.arange(5)
    widths = [2, 3, 5, 8, 13]
    for level, count in zip(levels, widths, strict=True):
        y = np.linspace(-0.8, 0.8, count)
        ax.scatter(np.full(count, level), y, s=55)
        if level:
            prev = np.linspace(-0.8, 0.8, widths[level - 1])
            for j, yy in enumerate(y):
                parent = int(round(j * (len(prev) - 1) / max(len(y) - 1, 1)))
                ax.plot([level - 1, level], [prev[parent], yy], alpha=0.35)
    ax.set_xlabel("refinement level")
    ax.set_ylabel("geometry packet address")
    ax.set_title("Conjectural projector tower for quantum spacetime")
    ax.set_yticks([])
    ax.grid(axis="x", alpha=0.25)
    _save(fig, out, "17_quantum_spacetime_tower")
    stems.append("17_quantum_spacetime_tower")

    # 18. Proof boundary.
    labels = [
        "finite packets", "circuits", "leakage", "Feshbach", "connections",
        "spectral tests", "constraint closure", "Lorentzian limit", "Einstein limit", "spin-2 pole",
    ]
    status = np.array([[1, 0, 0]] * 6 + [[0, 0, 1]] * 4, dtype=float)
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    ax.imshow(status, aspect="auto")
    ax.set_xticks([0, 1, 2], ["proved here", "classical input", "conjectural"])
    ax.set_yticks(np.arange(len(labels)), labels)
    for i in range(len(labels)):
        for j in range(3):
            if status[i, j]:
                ax.text(j, i, "yes", ha="center", va="center")
    ax.set_title("Proof boundary of the quantum-spacetime program")
    _save(fig, out, "18_proof_boundary")
    stems.append("18_proof_boundary")


    # 19. Error-correction syndrome packets.
    syndromes = syndrome_projectors()
    syndrome_diagonal = np.stack([np.diag(p).real for p in syndromes])
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    image = ax.imshow(syndrome_diagonal, aspect="auto")
    fig.colorbar(image, ax=ax, label="projector diagonal")
    ax.set_yticks(range(4), ["no flip", "flip qubit 1", "flip qubit 2", "flip qubit 3"])
    ax.set_xticks(range(8), [format(i, "03b") for i in range(8)])
    ax.set_title("Orthogonal syndrome packets of the three-qubit bit-flip code")
    _save(fig, out, "19_error_correction_syndromes")
    stems.append("19_error_correction_syndromes")

    return stems
