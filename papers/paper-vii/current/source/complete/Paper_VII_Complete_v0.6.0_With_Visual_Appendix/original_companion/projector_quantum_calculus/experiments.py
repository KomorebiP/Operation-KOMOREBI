from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm

from .basic import (
    CNOT, H_GATE, I2, X, Z, basis_state, cyclic_span_rank,
    embed_one_qubit, embed_two_qubit_adjacent, ketbra,
    packet_blocks, reachable_span_rank, reconstruct_blocks,
)
from .channels import (
    amplitude_damping_kraus, apply_channel, kraus_completeness_error,
    measurement_probabilities, packet_dephase,
)
from .circuits import bell_circuit, circuit_unitary, packet_path_reconstruction
from .codes import (
    bit_flip_channel, bit_flip_code_projector, bit_flip_errors, bit_flip_recovery,
    encode_logical_state, knill_laflamme_residual, syndrome_projectors,
)
from .dynamics import (
    bloch_curvature, canonical_projector_connection, commutator,
    feshbach_effective, leakage_amplitude, leakage_bound,
    moving_frame_generator, projected_resolvent, unitary_evolution,
)
from .geometry import (
    causal_volume_hamiltonian, cycle_eigenvalues, euclidean_transfer,
    heat_trace, low_mode_error_bound, spectral_dimension, torus_eigenvalues,
)
from .symmetry import (
    coarse_mod_projectors, off_block_norm, parity_operator, parity_projectors,
    sector_populations,
)


def _float(x: complex | float) -> float:
    return float(np.real_if_close(x))


def _json_complex_array(a: np.ndarray) -> list:
    arr = np.asarray(a)
    if np.max(np.abs(arr.imag if np.iscomplexobj(arr) else 0)) < 1e-12:
        return arr.real.tolist()
    return [[[float(z.real), float(z.imag)] for z in row] for row in arr]


def run_experiments(output: str | Path | None = None, table: str | Path | None = None) -> dict:
    rng = np.random.default_rng(20260727)

    # Bell seed and circuit.
    bell_seed, bell_gates, bell = bell_circuit()
    bell_target = (basis_state(2, 0) + basis_state(2, 3)) / np.sqrt(2)
    bell_error = float(np.linalg.norm(bell - bell_target))

    # Reachability from one quantum seed.
    generators = [embed_one_qubit(X, 0, 3), embed_one_qubit(X, 1, 3), embed_one_qubit(X, 2, 3)]
    reachable_rank = reachable_span_rank(generators, basis_state(3, 0), max_depth=5)

    # Parity-resolved Hamiltonian.
    j, hfield = 0.8, 0.35
    xx = np.kron(X, X)
    z1 = np.kron(Z, I2)
    z2 = np.kron(I2, Z)
    h_sym = j * xx + hfield * (z1 + z2)
    p_even, p_odd = parity_projectors(2)
    parity_off = off_block_norm(h_sym, [p_even, p_odd])
    parity_eigs = {
        "full": np.linalg.eigvalsh(h_sym).tolist(),
        "even": np.linalg.eigvalsh(np.array([[2*hfield, j], [j, -2*hfield]], dtype=float)).tolist(),
        "odd": np.linalg.eigvalsh(np.array([[0, j], [j, 0]], dtype=float)).tolist(),
    }

    # Circuit path reconstruction.
    path_recon = packet_path_reconstruction(bell_gates, [p_even, p_odd])
    circuit_u = circuit_unitary(bell_gates)
    circuit_path_error = float(np.linalg.norm(path_recon - circuit_u))

    # Symmetry breaking and leakage.
    perturbation = 0.22 * np.kron(X, I2)
    h_broken = h_sym + perturbation
    times = np.linspace(0, 5, 101)
    leakage = np.array([leakage_amplitude(h_broken, p_even, t) for t in times])
    bounds = np.array([leakage_bound(h_broken, p_even, t) for t in times])
    max_bound_violation = float(np.max(leakage - bounds))
    exact_symmetry_leakage = float(max(leakage_amplitude(h_sym, p_even, t) for t in times))

    # Feshbach projected resolvent.
    a = rng.standard_normal((6, 6)) + 1j * rng.standard_normal((6, 6))
    h_random = (a + a.conj().T) / 2
    p = np.diag([1, 1, 1, 0, 0, 0]).astype(complex)
    z = 7.5 + 0.4j
    exact_res = projected_resolvent(h_random, p, z)
    heff = feshbach_effective(h_random, p, z)
    fesh_res = np.linalg.inv(z * np.eye(3) - heff)
    feshbach_error = float(np.linalg.norm(exact_res - fesh_res))
    bare = np.linalg.inv(z * np.eye(3) - h_random[:3, :3])
    bare_error = float(np.linalg.norm(exact_res - bare))

    # Moving frame and canonical connection.
    k = np.array([[0, -0.7], [0.7, 0]], dtype=complex)
    t0 = 0.41
    u = expm(t0 * k)
    du = k @ u
    h2 = np.array([[1.2, 0.3 - 0.2j], [0.3 + 0.2j, -0.4]], dtype=complex)
    moving_h = moving_frame_generator(h2, u, du)
    psi = np.array([0.6 + 0.1j, -0.3 + 0.7j], dtype=complex)
    psi = psi / np.linalg.norm(psi)
    y = u.conj().T @ psi
    dt = 1e-6
    up = expm((t0 + dt) * k)
    um = expm((t0 - dt) * k)
    psi_p = unitary_evolution(h2, dt) @ psi
    psi_m = unitary_evolution(h2, -dt) @ psi
    y_p = up.conj().T @ psi_p
    y_m = um.conj().T @ psi_m
    numerical_ydot = (y_p - y_m) / (2 * dt)
    predicted_ydot = -1j * moving_h @ y
    moving_frame_error = float(np.linalg.norm(numerical_ydot - predicted_ydot))
    omission_ydot = -1j * (u.conj().T @ h2 @ u) @ y
    omission_error = float(np.linalg.norm(numerical_ydot - omission_ydot))

    fixed = [np.diag([1, 0]).astype(complex), np.diag([0, 1]).astype(complex)]
    moving_p = [u @ q @ u.conj().T for q in fixed]
    derivatives = [commutator(k, q) for q in moving_p]
    connection = canonical_projector_connection(moving_p, derivatives)
    connection_error = float(max(np.linalg.norm(commutator(connection, q) - dq) for q, dq in zip(moving_p, derivatives, strict=True)))

    # Bloch curvature.
    theta_values = np.linspace(0.15, np.pi - 0.15, 31)
    curvature = np.array([bloch_curvature(theta, 0.7) for theta in theta_values])
    curvature_target = 0.5 * np.sin(theta_values)
    curvature_error = float(np.max(np.abs(curvature - curvature_target)))

    # Measurement and dephasing.
    rho_bell = ketbra(bell)
    effects = [ketbra(basis_state(2, i)) for i in range(4)]
    probs = measurement_probabilities(rho_bell, effects)
    rho_dephased = packet_dephase(rho_bell, [p_even, p_odd])
    dephase_measurement_error = float(np.linalg.norm(probs - measurement_probabilities(rho_dephased, effects)))

    # Amplitude damping channel.
    kraus = amplitude_damping_kraus(0.23)
    channel_tp_error = kraus_completeness_error(kraus)
    rho_excited = ketbra(basis_state(1, 1))
    damped = apply_channel(rho_excited, kraus)
    trace_error = float(abs(np.trace(damped) - 1))


    # Three-qubit bit-flip error correction.
    code_projector = bit_flip_code_projector()
    code_errors = bit_flip_errors()
    _, kl_residual = knill_laflamme_residual(code_projector, code_errors)
    logical_state = encode_logical_state(np.sqrt(0.37), np.sqrt(0.63) * np.exp(0.41j))
    logical_density = ketbra(logical_state)
    corrupted_density = bit_flip_channel(logical_density, [0.70, 0.08, 0.11, 0.11])
    recovered_density = bit_flip_recovery(corrupted_density)
    recovery_error = float(np.linalg.norm(recovered_density - logical_density))
    syndrome_completeness = float(np.linalg.norm(sum(syndrome_projectors()) - np.eye(8)))

    # Tensor/polyphase refinement: local computational packets refine total parity.
    local = [[np.diag([1, 0]).astype(complex), np.diag([0, 1]).astype(complex)] for _ in range(3)]
    coarse = coarse_mod_projectors(local, 2)
    p3 = parity_projectors(3)
    tensor_refinement_error = float(max(np.linalg.norm(coarse[i] - p3[i]) for i in range(2)))

    # Circle low-mode convergence.
    sizes = np.array([32, 48, 64, 96, 128, 192])
    errors = []
    bounds_low = []
    for n in sizes:
        hspace = 2 * np.pi / n
        err, bnd = low_mode_error_bound(1, hspace)
        errors.append(err)
        bounds_low.append(bnd)
    errors = np.array(errors)
    observed_order = float(np.polyfit(np.log(2 * np.pi / sizes), np.log(errors), 1)[0])
    max_lowmode_bound_violation = float(np.max(errors - np.array(bounds_low)))

    # Spectral dimension on 1D and 2D tori.
    taus = np.logspace(-3.2, 1.0, 180)
    eig1 = cycle_eigenvalues(256)
    eig2 = torus_eigenvalues(48, 2)
    ds1 = spectral_dimension(eig1, taus)
    ds2 = spectral_dimension(eig2, taus)
    mask = (taus > 0.03) & (taus < 0.5)
    ds1_plateau = float(np.median(ds1[mask]))
    ds2_plateau = float(np.median(ds2[mask]))

    # Euclidean transfer and causal-volume toy.
    hv = causal_volume_hamiltonian(42, kappa=0.8, confinement=0.012)
    tv = euclidean_transfer(hv, 0.35)
    transfer_min_eigenvalue = float(np.min(np.linalg.eigvalsh(tv)))
    transfer_semigroup_error = float(np.linalg.norm(tv @ tv - euclidean_transfer(hv, 0.70)))
    evals, evecs = np.linalg.eigh(hv)
    ground = np.abs(evecs[:, 0]) ** 2
    ground /= ground.sum()
    volume_mean = float(np.dot(np.arange(1, 43), ground))
    volume_variance = float(np.dot((np.arange(1, 43) - volume_mean) ** 2, ground))
    volume_packets = [np.diag([(1 if (i + 1) % 4 == r else 0) for i in range(42)]).astype(complex) for r in range(4)]
    transfer_block_reconstruction = float(np.linalg.norm(reconstruct_blocks(packet_blocks(tv, volume_packets)) - tv))

    # Packet Green function heatmap data.
    green_blocks = packet_blocks(np.linalg.inv((2.7 + 0.2j) * np.eye(4) - h_broken), [p_even, p_odd])
    green_norms = np.array([[np.linalg.norm(b) for b in row] for row in green_blocks])

    results = {
        "author": "Komorebi P.",
        "execution": {"device": "CPU", "gpu_used": False},
        "bell": {
            "state_error": bell_error,
            "probabilities": probs.tolist(),
            "reachable_rank_three_qubit_x_generators": reachable_rank,
        },
        "symmetry": {
            "parity_off_block_norm": parity_off,
            "eigenvalues": parity_eigs,
            "circuit_path_reconstruction_error": circuit_path_error,
            "exact_symmetry_max_leakage": exact_symmetry_leakage,
            "broken_symmetry_max_leakage": float(np.max(leakage)),
            "maximum_leakage_bound_violation": max_bound_violation,
            "tensor_refinement_error": tensor_refinement_error,
        },
        "effective_dynamics": {
            "feshbach_resolvent_error": feshbach_error,
            "bare_truncation_error": bare_error,
            "moving_frame_error": moving_frame_error,
            "omitted_connection_error": omission_error,
            "canonical_connection_error": connection_error,
            "bloch_curvature_error": curvature_error,
            "packet_green_block_norms": green_norms.tolist(),
        },
        "channels": {
            "dephased_measurement_error": dephase_measurement_error,
            "kraus_completeness_error": channel_tp_error,
            "output_trace_error": trace_error,
            "damped_excited_density": _json_complex_array(damped),
        },
        "error_correction": {
            "knill_laflamme_residual": kl_residual,
            "recovery_error": recovery_error,
            "syndrome_completeness_error": syndrome_completeness,
        },
        "geometry": {
            "circle_observed_order": observed_order,
            "maximum_low_mode_bound_violation": max_lowmode_bound_violation,
            "spectral_dimension_1d_plateau": ds1_plateau,
            "spectral_dimension_2d_plateau": ds2_plateau,
            "minimum_transfer_eigenvalue": transfer_min_eigenvalue,
            "transfer_semigroup_error": transfer_semigroup_error,
            "volume_ground_mean": volume_mean,
            "volume_ground_variance": volume_variance,
            "volume_packet_reconstruction_error": transfer_block_reconstruction,
        },
        "series": {
            "leakage_times": times.tolist(),
            "leakage": leakage.tolist(),
            "leakage_bound": bounds.tolist(),
            "theta": theta_values.tolist(),
            "curvature": curvature.tolist(),
            "curvature_target": curvature_target.tolist(),
            "spacing": (2 * np.pi / sizes).tolist(),
            "low_mode_error": errors.tolist(),
            "low_mode_bound": np.asarray(bounds_low).tolist(),
            "tau": taus.tolist(),
            "spectral_dimension_1d": ds1.tolist(),
            "spectral_dimension_2d": ds2.tolist(),
            "volume_ground_probability": ground.tolist(),
        },
    }

    if output is not None:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")

    if table is not None:
        rows = [
            ("Bell-state error", bell_error),
            ("Three-qubit reachable rank", reachable_rank),
            ("Parity off-block norm", parity_off),
            ("Circuit path reconstruction", circuit_path_error),
            ("Exact symmetry max leakage", exact_symmetry_leakage),
            ("Maximum leakage-bound violation", max_bound_violation),
            ("Feshbach resolvent error", feshbach_error),
            ("Bare truncation error", bare_error),
            ("Moving-frame error", moving_frame_error),
            ("Omitted-connection error", omission_error),
            ("Canonical connection error", connection_error),
            ("Bloch-curvature error", curvature_error),
            ("Knill-Laflamme residual", kl_residual),
            ("Bit-flip recovery error", recovery_error),
            ("Syndrome completeness error", syndrome_completeness),
            ("Tensor refinement error", tensor_refinement_error),
            ("Circle convergence order", observed_order),
            ("1D spectral-dimension plateau", ds1_plateau),
            ("2D spectral-dimension plateau", ds2_plateau),
            ("Minimum Euclidean-transfer eigenvalue", transfer_min_eigenvalue),
            ("Transfer semigroup error", transfer_semigroup_error),
            ("Volume packet reconstruction", transfer_block_reconstruction),
        ]
        path = Path(table)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["certificate", "value"])
            writer.writerows(rows)

    return results
