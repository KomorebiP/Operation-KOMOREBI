#!/usr/bin/env python
"""Run the ground-truth recurrent-depth / Komorebi acceptance suite."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from krd_lab.analysis import (  # noqa: E402
    block_transport_certificate,
    contraction_certificate,
    coordinate_projectors,
    detect_slider,
    last_write_selector,
    linear_operator_fit,
    modulo_cache_profile,
    path_independence,
)
from krd_lab.komorebi_bridge import verify_with_komorebi  # noqa: E402
from krd_lab.synthetic import (  # noqa: E402
    contraction_system,
    generate_trajectories,
    mixed_system,
    rotation_system,
    slider_system,
)


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return [[float(x.real), float(x.imag)] for x in value.reshape(-1)]
        return value.tolist()
    if isinstance(value, (np.floating, np.integer, np.bool_)):
        return value.item()
    if isinstance(value, complex):
        return [float(value.real), float(value.imag)]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


class Gates:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(
        self,
        name: str,
        passed: bool,
        *,
        kind: str,
        required: bool = True,
        skipped: bool = False,
        **metrics: Any,
    ) -> None:
        self.rows.append(
            {
                "name": name,
                "passed": bool(passed),
                "kind": kind,
                "required": bool(required),
                "skipped": bool(skipped),
                "metrics": _jsonable(metrics),
            }
        )

    @property
    def required_passed(self) -> bool:
        return all(row["passed"] for row in self.rows if row["required"])


def _column_pairs(trajectories: list[np.ndarray], feature=None) -> tuple[np.ndarray, np.ndarray]:
    source_rows: list[np.ndarray] = []
    target_rows: list[np.ndarray] = []
    transform = (lambda x: x) if feature is None else feature
    for trajectory in trajectories:
        source_rows.extend(transform(state) for state in trajectory[:-1])
        target_rows.extend(transform(state) for state in trajectory[1:])
    return np.asarray(source_rows, dtype=float).T, np.asarray(target_rows, dtype=float).T


def _relative_residual(operator: np.ndarray, source: np.ndarray, target: np.ndarray) -> float:
    denominator = max(float(np.linalg.norm(target)), np.finfo(float).eps)
    return float(np.linalg.norm(target - operator @ source) / denominator)


def run_suite(komorebi_src: str | None = None) -> dict[str, Any]:
    gates = Gates()

    # Fixed point and exact affine Koopman lift.
    contraction, fixed_point = contraction_system()
    trajectory = contraction.trajectory(np.array([8.0, -5.0]), 80)
    initial_error = float(np.linalg.norm(trajectory[0] - fixed_point))
    final_error = float(np.linalg.norm(trajectory[-1] - fixed_point))
    kappa = float(np.linalg.norm(contraction.operator, ord=2))
    gates.add(
        "fixed_point_contraction",
        np.allclose(contraction.step(fixed_point), fixed_point, atol=1e-13)
        and final_error <= kappa**80 * initial_error + 5e-12,
        kind="exact_ground_truth",
        kappa=kappa,
        initial_error=initial_error,
        final_error=final_error,
    )
    rng = np.random.default_rng(202502)
    contraction_trajectories = generate_trajectories(
        contraction, [rng.normal(size=2) for _ in range(12)], 12
    )
    homogeneous = lambda state: np.r_[state, 1.0]
    source, target = _column_pairs(contraction_trajectories, homogeneous)
    contraction_fit = linear_operator_fit(source, target)
    expected_homogeneous = np.block(
        [
            [contraction.operator, contraction.offset[:, None]],
            [np.zeros((1, 2)), np.ones((1, 1))],
        ]
    )
    gates.add(
        "affine_homogeneous_koopman_recovery",
        contraction_fit.fully_excited
        and np.linalg.norm(contraction_fit.operator - expected_homogeneous) < 1e-10
        and contraction_fit.relative_residual < 1e-11,
        kind="finite_exact_recovery",
        effective_rank=contraction_fit.effective_rank,
        operator_error=float(np.linalg.norm(contraction_fit.operator - expected_homogeneous)),
        fit_residual=contraction_fit.relative_residual,
    )

    # Period seven orbit. This is checked in full state space, not from PCA.
    q = 7
    orbit = rotation_system(theta=2.0 * np.pi / q)
    orbit_initial = np.array([1.0, 0.2])
    orbit_states = orbit.trajectory(orbit_initial, q)
    preperiod_returns = [float(np.linalg.norm(orbit_states[j] - orbit_initial)) for j in range(1, q)]
    gates.add(
        "period_7_full_space_orbit",
        np.linalg.norm(orbit_states[-1] - orbit_initial) < 3e-12
        and min(preperiod_returns) > 1e-3
        and np.max(np.abs(np.linalg.norm(orbit_states, axis=1) - np.linalg.norm(orbit_initial))) < 3e-12,
        kind="exact_ground_truth",
        return_error=float(np.linalg.norm(orbit_states[-1] - orbit_initial)),
        nearest_early_return=min(preperiod_returns),
    )
    orbit_fit = linear_operator_fit(orbit_states[:-1].T, orbit_states[1:].T)
    gates.add(
        "rotation_dmd_recovery",
        orbit_fit.fully_excited
        and np.linalg.norm(orbit_fit.operator - orbit.operator) < 1e-10,
        kind="finite_exact_recovery",
        effective_rank=orbit_fit.effective_rank,
        operator_error=float(np.linalg.norm(orbit_fit.operator - orbit.operator)),
        eigenvalues=np.linalg.eigvals(orbit_fit.operator),
    )

    # Unit-eigenvalue Jordan chain / slider.
    slider = slider_system()
    slider_states = slider.trajectory(np.array([-1.0, 0.25]), 24)
    slider_result = detect_slider(slider_states)
    nilpotent = slider.operator - np.eye(2)
    gates.add(
        "jordan_slider",
        slider_result.detected
        and np.linalg.norm(np.diff(slider_states, n=2, axis=0)) < 1e-12
        and np.linalg.matrix_rank(nilpotent, tol=1e-12) == 1
        and np.linalg.norm(nilpotent @ nilpotent) < 1e-12,
        kind="exact_ground_truth",
        slider=slider_result,
        nilpotent_norm=float(np.linalg.norm(nilpotent)),
    )

    # Exact packet algebra and directed C -> O -> S transport.
    mixed, groups = mixed_system()
    packets = coordinate_projectors(5, groups)
    block_certificate = block_transport_certificate(mixed.operator, packets, exponent=5)
    contract, orbit_packet, slider_packet = packets
    two_step = slider_packet @ np.linalg.matrix_power(mixed.operator, 2) @ contract
    via_orbit = (
        slider_packet @ mixed.operator @ orbit_packet
    ) @ (
        orbit_packet @ mixed.operator @ contract
    )
    direct_contract_to_slider = slider_packet @ mixed.operator @ contract
    gates.add(
        "packet_path_reconstruction",
        block_certificate.valid
        and np.linalg.norm(two_step - via_orbit) < 1e-12
        and np.linalg.norm(via_orbit) > 0
        and np.linalg.norm(direct_contract_to_slider) < 1e-12,
        kind="exact_algebra",
        certificate=block_certificate,
        two_step_identity_residual=float(np.linalg.norm(two_step - via_orbit)),
        induced_transport_norm=float(np.linalg.norm(via_orbit)),
    )

    # Initialization endpoint collapse and a neutral negative control.
    many_initials = [rng.normal(size=2) * 8.0 for _ in range(64)]
    long_trajectories = generate_trajectories(contraction, many_initials, 100)
    collapse = path_independence(long_trajectories)
    gates.add(
        "initialization_endpoint_collapse",
        collapse.final_pairwise_max < 1e-8,
        kind="measured_property_not_holonomy",
        result=collapse,
    )
    point_a, point_b = np.array([1.0, -0.4]), np.array([-0.2, 0.7])
    before = float(np.linalg.norm(point_a - point_b))
    after = float(np.linalg.norm(orbit.step(point_a) - orbit.step(point_b)))
    gates.add(
        "rotation_rejects_endpoint_collapse",
        abs(before - after) < 1e-12,
        kind="negative_control",
        distance_before=before,
        distance_after=after,
    )

    # Cyclic cache is a last-write selector, not a residue sum.
    step_count, modulus = 10, 3
    profile = modulo_cache_profile(step_count, modulus)
    selector = last_write_selector(step_count, modulus)
    values = np.arange(step_count, dtype=float)
    final_cache = selector @ values
    mutated_overwritten = values.copy()
    mutated_overwritten[0] += 1000.0
    mutated_survivor = values.copy()
    mutated_survivor[9] += 1000.0
    gates.add(
        "modulo_cache_last_write_quotient",
        profile["retained_last_step"] == {"0": 9, "1": 7, "2": 8}
        and profile["collision_count"] == 7
        and np.linalg.matrix_rank(selector) == 3
        and np.allclose(selector @ mutated_overwritten, final_cache)
        and not np.allclose(selector @ mutated_survivor, final_cache),
        kind="exact_algebra",
        profile=profile,
        selector_rank=int(np.linalg.matrix_rank(selector)),
        final_cache=final_cache,
    )

    # Exact polynomial observable closure for an affine scalar recurrence.
    a, b = 0.6, -0.2
    phi = lambda x: np.array([1.0, float(x), float(x) ** 2])
    train_x = np.linspace(-2.0, 2.0, 81)
    poly_source = np.column_stack([phi(x) for x in train_x])
    poly_target = np.column_stack([phi(a * x + b) for x in train_x])
    poly_fit = linear_operator_fit(poly_source, poly_target)
    expected_poly = np.array(
        [[1.0, 0.0, 0.0], [b, a, 0.0], [b * b, 2.0 * a * b, a * a]]
    )
    heldout_x = rng.uniform(-2.1, 2.1, size=103)
    heldout_source = np.column_stack([phi(x) for x in heldout_x])
    heldout_target = np.column_stack([phi(a * x + b) for x in heldout_x])
    heldout_residual = _relative_residual(poly_fit.operator, heldout_source, heldout_target)
    gates.add(
        "polynomial_koopman_closure",
        poly_fit.fully_excited
        and np.linalg.norm(poly_fit.operator - expected_poly) < 1e-10
        and heldout_residual < 1e-10,
        kind="finite_exact_recovery",
        operator_error=float(np.linalg.norm(poly_fit.operator - expected_poly)),
        heldout_residual=heldout_residual,
        eigenvalues=np.linalg.eigvals(poly_fit.operator),
    )

    # Missing x^2 observable produces held-out leakage.
    low_phi = lambda x: np.array([1.0, float(x)])
    nonlinear = lambda x: 0.5 * x + 0.2 * x * x
    leak_train = np.linspace(-1.0, 1.0, 101)
    leak_source = np.column_stack([low_phi(x) for x in leak_train])
    leak_target = np.column_stack([low_phi(nonlinear(x)) for x in leak_train])
    leak_fit = linear_operator_fit(leak_source, leak_target)
    leak_test = np.linspace(-0.987, 0.993, 137)
    leak_test_source = np.column_stack([low_phi(x) for x in leak_test])
    leak_test_target = np.column_stack([low_phi(nonlinear(x)) for x in leak_test])
    leakage = _relative_residual(leak_fit.operator, leak_test_source, leak_test_target)
    gates.add(
        "omitted_observable_leakage",
        leakage > 1e-2,
        kind="negative_control",
        heldout_relative_residual=leakage,
        train_relative_residual=leak_fit.relative_residual,
    )

    # A trajectory confined to one eigendirection cannot identify the other.
    rank_operator = np.diag([0.4, 0.8])
    rank_states = [np.array([1.0, 0.0])]
    for _ in range(12):
        rank_states.append(rank_operator @ rank_states[-1])
    rank_states_array = np.vstack(rank_states)
    rank_fit = linear_operator_fit(rank_states_array[:-1].T, rank_states_array[1:].T)
    unseen = np.array([0.0, 1.0])
    unseen_error = float(np.linalg.norm(rank_fit.operator @ unseen - rank_operator @ unseen))
    gates.add(
        "rank_deficient_excitation_fails_closed",
        rank_fit.effective_rank == 1 and not rank_fit.fully_excited and unseen_error > 0.1,
        kind="negative_control",
        effective_rank=rank_fit.effective_rank,
        unseen_lane_error=unseen_error,
    )

    # Certified stopping and false-convergence controls.
    scalar_states = [np.array([0.0])]
    for _ in range(25):
        scalar_states.append(0.7 * scalar_states[-1] + 0.3)
    scalar_states_array = np.vstack(scalar_states)
    stop_certificate = contraction_certificate(
        scalar_states_array, kappa=0.7, fixed_point=np.array([1.0])
    )
    gates.add(
        "contraction_stopping_certificate",
        stop_certificate.bound_holds is True
        and abs(
            float(stop_certificate.fixed_point_error_bound)
            - float(stop_certificate.observed_final_error)
        )
        < 1e-12,
        kind="rigorous_given_kappa",
        certificate=stop_certificate,
    )
    slow_previous, slow_current = 1.0, 0.99
    naive_threshold = 0.02
    slow_bound = 0.99 / (1.0 - 0.99) * abs(slow_current - slow_previous)
    nonnormal = np.array([[0.5, 10.0], [0.0, 0.5]])
    gates.add(
        "false_convergence_controls",
        abs(slow_current - slow_previous) < naive_threshold
        and slow_bound > naive_threshold
        and max(abs(np.linalg.eigvals(nonnormal))) < 1.0
        and np.linalg.norm(nonnormal, ord=2) > 1.0,
        kind="negative_control",
        slow_actual_error=slow_current,
        slow_certificate_bound=slow_bound,
        nonnormal_spectral_radius=float(max(abs(np.linalg.eigvals(nonnormal)))),
        nonnormal_operator_norm=float(np.linalg.norm(nonnormal, ord=2)),
    )

    # Optional cross-check against the user's existing Komorebi Math core.
    bridge = verify_with_komorebi(
        mixed.operator,
        packets,
        ["contract", "orbit", "slider"],
        komorebi_src=komorebi_src,
        exponent=5,
    )
    gates.add(
        "existing_komorebi_math_bridge",
        (not bridge.get("available", False))
        or (
            bridge.get("packet_certificate_valid", False)
            and bridge.get("operator_certificate_valid", False)
            and bridge.get("path_power_residual", 1.0) < 1e-10
        ),
        kind="optional_cross_check",
        required=False,
        skipped=not bridge.get("available", False),
        bridge=bridge,
    )

    return {
        "schema_version": "1.0",
        "lab_version": "0.1.1",
        "precision": "float64",
        "required_passed": gates.required_passed,
        "gate_count": len(gates.rows),
        "required_failures": [
            row["name"] for row in gates.rows if row["required"] and not row["passed"]
        ],
        "gates": gates.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "synthetic_summary.json",
        help="JSON report path",
    )
    parser.add_argument(
        "--komorebi-src",
        default=None,
        help="Optional path to the existing komorebi-math src directory",
    )
    args = parser.parse_args()
    report = run_suite(args.komorebi_src)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for row in report["gates"]:
        marker = "SKIP" if row.get("skipped", False) else ("PASS" if row["passed"] else "FAIL")
        optional = " (optional)" if not row["required"] else ""
        print(f"[{marker}] {row['name']}{optional}")
    print(f"\nReport: {args.output.resolve()}")
    return 0 if report["required_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
