from __future__ import annotations

import csv
import json
import math
import sys
from dataclasses import asdict
from itertools import product
from pathlib import Path
from typing import Any, Callable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.ticker import LogFormatterMathtext, LogLocator, MaxNLocator

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from priq import (  # noqa: E402
    aggregate_output_coefficients,
    averaging_section,
    bayes_commutation_residual,
    bayes_update,
    best_k_residuals,
    block_sum_matrix,
    exact_lift_tensor,
    hidden_exchange_fields,
    hyperedge_energy_statistics,
    integrate_rk4,
    kernel_basis,
    normalization_perturbation_bound,
    posterior_error_certificate,
    quotient_defect,
    recover_coarse_tensor,
    simulate_prediction_update_filter,
    slot_kernel_residual,
    symmetrize_inputs,
    transform_tensor,
)

FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"
RESULTS = ROOT / "results"
BUILD = ROOT / "build"
for directory in (FIGURES, TABLES, RESULTS, BUILD):
    directory.mkdir(parents=True, exist_ok=True)

TOL = 1e-10

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 11,
        "axes.labelsize": 11,
        "legend.fontsize": 9.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.9,
        "lines.markersize": 5.0,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "mathtext.fontset": "cm",
    }
)


def clean_plot_axes(ax: plt.Axes, *, grid: bool = True) -> None:
    if grid:
        ax.grid(True, alpha=0.18)
    ax.tick_params(length=4)


class Ledger:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(
        self,
        check_id: str,
        statement: str,
        value: float,
        tolerance: float,
        *,
        comparator: str = "<=",
    ) -> bool:
        value = float(value)
        tolerance = float(tolerance)
        if comparator == "<=":
            passed = bool(value <= tolerance)
        elif comparator == ">=":
            passed = bool(value >= tolerance)
        else:
            raise ValueError(f"unsupported comparator {comparator!r}")
        self.rows.append(
            {
                "id": check_id,
                "statement": statement,
                "value": value,
                "tolerance": tolerance,
                "comparator": comparator,
                "status": "PASS" if passed else "FAIL",
            }
        )
        return passed

    @property
    def passed(self) -> int:
        return sum(row["status"] == "PASS" for row in self.rows)

    @property
    def failed(self) -> int:
        return sum(row["status"] == "FAIL" for row in self.rows)


def tex_number(value: float, digits: int = 3) -> str:
    if value == 0:
        return "0"
    exponent = int(math.floor(math.log10(abs(value))))
    if -2 <= exponent <= 2:
        return f"{value:.{digits}g}"
    mantissa = value / (10.0**exponent)
    return rf"{mantissa:.{digits}g}\times 10^{{{exponent}}}"


def tex_threshold(value: float, digits: int = 3) -> str:
    if value == 0:
        return "0"
    exponent = int(math.floor(math.log10(abs(value))))
    mantissa = value / (10.0**exponent)
    if abs(mantissa - 1.0) < 1e-12:
        return rf"10^{{{exponent}}}"
    if -2 <= exponent <= 2:
        return f"{value:.{digits}g}"
    return rf"{mantissa:.{digits}g}\times 10^{{{exponent}}}"


def tex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def save_figure(fig: plt.Figure, stem: str) -> None:
    pdf_metadata = {
        "Creator": "PRIQ 0.1.4",
        "Producer": "Matplotlib",
        "CreationDate": None,
        "ModDate": None,
    }
    fig.savefig(
        FIGURES / f"{stem}.pdf",
        bbox_inches="tight",
        metadata=pdf_metadata,
    )
    fig.savefig(FIGURES / f"{stem}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def tensor_defect_general(Af: np.ndarray, Ac: np.ndarray, C: np.ndarray) -> np.ndarray:
    order = Af.ndim - 1
    left = transform_tensor(Af, C, [np.eye(Af.shape[1])] * order)
    right = transform_tensor(Ac, np.eye(Ac.shape[0]), [C] * order)
    return left - right


def exact_tensor_certificates(ledger: Ledger, rng: np.random.Generator) -> dict[str, Any]:
    pi = np.asarray([0, 0, 1, 1], dtype=int)
    C = block_sum_matrix(pi)
    E = averaging_section(pi)
    exact_data: dict[str, Any] = {"C": C, "E": E, "pi": pi}

    for order in (1, 2, 3):
        coarse = rng.normal(size=(2, *([2] * order)))
        if order > 1:
            coarse = symmetrize_inputs(coarse)
        hidden_raw = rng.normal(size=(4, *([4] * order)))
        fine = exact_lift_tensor(coarse, C, E, hidden_tensor=hidden_raw)
        defect = float(np.linalg.norm(quotient_defect(fine, coarse, C)))
        slot = float(slot_kernel_residual(fine, C))
        recovery = recover_coarse_tensor(fine, pi)
        recovery_error = float(np.max(np.abs(recovery.coarse_tensor - coarse)))
        fiber_variation = float(recovery.max_fiber_variation)
        ledger.add(f"Q{order}D", f"order {order} quotient defect", defect, TOL)
        ledger.add(f"Q{order}K", f"order {order} hidden input residual", slot, TOL)
        ledger.add(f"Q{order}R", f"order {order} coarse tensor recovery", recovery_error, TOL)
        exact_data[f"order_{order}"] = {
            "coarse": coarse,
            "fine": fine,
            "defect": defect,
            "slot_kernel": slot,
            "recovery_error": recovery_error,
            "fiber_variation": fiber_variation,
        }

    fine2 = exact_data["order_2"]["fine"].copy()
    fine2[0, 0, 0] += 0.125
    negative = recover_coarse_tensor(fine2, pi)
    ledger.add(
        "QNEG",
        "a perturbation of one coefficient violates fiber constancy",
        negative.max_fiber_variation,
        0.1,
        comparator=">=",
    )

    coarse_sym = symmetrize_inputs(rng.normal(size=(2, 2, 2)))
    fine_sym = exact_lift_tensor(coarse_sym, C, E)
    symmetry_error = float(np.linalg.norm(fine_sym - np.swapaxes(fine_sym, 1, 2)))
    ledger.add("QSYM", "symmetric interaction remains symmetric after exact lift", symmetry_error, TOL)

    hidden = rng.normal(size=(4, 4, 4))
    Q = np.eye(4) - E @ C
    hidden_projected = transform_tensor(hidden, Q, [np.eye(4), np.eye(4)])
    hidden_output = transform_tensor(hidden_projected, C, [np.eye(4), np.eye(4)])
    ledger.add("QHID", "projected hidden tensor has zero coarse output", np.linalg.norm(hidden_output), TOL)
    return exact_data


def multilevel_certificates(ledger: Ledger, rng: np.random.Generator) -> dict[str, float]:
    C21 = np.asarray([[1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)
    C10 = np.asarray([[1, 1, 0], [0, 0, 1]], dtype=float)
    C20 = C10 @ C21
    order = 2

    E21 = np.asarray(
        [[0.5, 0, 0], [0.5, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float
    )
    E10 = np.asarray([[0.5, 0], [0.5, 0], [0, 1]], dtype=float)
    A0 = rng.normal(size=(2, 2, 2))
    A1 = exact_lift_tensor(A0, C10, E10, hidden_tensor=rng.normal(size=(3, 3, 3)))
    A2 = exact_lift_tensor(A1, C21, E21, hidden_tensor=rng.normal(size=(4, 4, 4)))
    transitive = float(np.linalg.norm(tensor_defect_general(A2, A0, C20)))
    ledger.add("QTRN", "exact quotient transitivity across two aggregation levels", transitive, TOL)

    B2 = rng.normal(size=(4, 4, 4))
    B1 = rng.normal(size=(3, 3, 3))
    B0 = rng.normal(size=(2, 2, 2))
    d21 = tensor_defect_general(B2, B1, C21)
    d10 = tensor_defect_general(B1, B0, C10)
    d20 = tensor_defect_general(B2, B0, C20)
    rhs = transform_tensor(d21, C10, [np.eye(4)] * order) + transform_tensor(
        d10, np.eye(2), [C21] * order
    )
    identity_residual = float(np.linalg.norm(d20 - rhs))
    ledger.add("QMLT", "interaction defect identity across two levels", identity_residual, TOL)
    return {"transitivity_residual": transitive, "defect_identity_residual": identity_residual}


def exact_model_certificates(ledger: Ledger, rng: np.random.Generator) -> dict[str, Any]:
    fine, coarse, C = hidden_exchange_fields()
    x0 = np.asarray([0.31, 0.19, 0.17, 0.33], dtype=float)

    point_residuals = []
    for _ in range(200):
        x = rng.dirichlet(np.ones(4))
        point_residuals.append(float(np.linalg.norm(C @ fine(x) - coarse(C @ x), ord=1)))
    field_point_residual = max(point_residuals)
    ledger.add("QFLD", "fine vector field factors through the coarse field", field_point_residual, TOL)

    coarse_likelihoods = [
        np.asarray([1.40, 0.75]),
        np.asarray([0.80, 1.50]),
        np.asarray([1.25, 0.90]),
        np.asarray([0.70, 1.35]),
        np.asarray([1.10, 0.85]),
    ]
    fine_likelihoods = [C.T @ lam for lam in coarse_likelihoods]
    durations = [0.4, 0.6, 0.5, 0.7, 0.45]
    trace = simulate_prediction_update_filter(
        x0,
        C @ x0,
        fine,
        coarse,
        fine_likelihoods,
        coarse_likelihoods,
        durations,
        max_step=1e-3,
    )
    prediction_residual = max(
        float(np.linalg.norm(C @ xf - xc, ord=1))
        for xf, xc in zip(trace.fine_predictions, trace.coarse_predictions, strict=True)
    )
    posterior_residual = max(
        float(np.linalg.norm(C @ xf - xc, ord=1))
        for xf, xc in zip(trace.fine_posteriors, trace.coarse_posteriors, strict=True)
    )
    evidence_residual = float(np.max(np.abs(trace.fine_evidence - trace.coarse_evidence)))
    ledger.add("QPRD", "exact aggregate prediction commutation", prediction_residual, 5e-10)
    ledger.add("QCOC", "exact commutation of the prediction and update cocycle", posterior_residual, 5e-10)
    ledger.add("QEVD", "exact evidence aggregation at one step", evidence_residual, 5e-10)

    # Mass and positivity are checked over a sampled trajectory, not just at the endpoint.
    states = [x0.copy()]
    state = x0.copy()
    for _ in range(400):
        state = integrate_rk4(fine, state, 0.005, max_step=0.005)
        states.append(state.copy())
    states_arr = np.asarray(states)
    mass_residual = float(np.max(np.abs(states_arr.sum(axis=1) - 1.0)))
    positivity_violation = float(max(0.0, -states_arr.min()))
    ledger.add("QMAS", "fine nonlinear trajectory preserves total mass", mass_residual, 5e-10)
    ledger.add("QPOS", "fine nonlinear trajectory preserves nonnegativity", positivity_violation, 5e-12)

    bayes_residuals = []
    evidence_residuals = []
    for _ in range(100):
        mu = rng.dirichlet(np.ones(4))
        lamc = rng.uniform(0.4, 1.8, size=2)
        lamf = C.T @ lamc
        bayes_residuals.append(bayes_commutation_residual(mu, lamf, lamc, C))
        evidence_residuals.append(abs(float(lamf @ mu) - float(lamc @ (C @ mu))))
    ledger.add("QBAY", "a likelihood constant within each fiber gives exact Bayesian refinement", max(bayes_residuals), TOL)
    ledger.add("QBEV", "a likelihood constant within each fiber preserves evidence", max(evidence_residuals), TOL)

    mu = rng.dirichlet(np.ones(4))
    lam = rng.uniform(0.3, 2.0, size=4)
    scale_residual = float(np.linalg.norm(bayes_update(mu, 3.7 * lam) - bayes_update(mu, lam), ord=1))
    ledger.add("QSCL", "Bayesian update is invariant under global likelihood scale", scale_residual, TOL)

    return {
        "fine_field": fine,
        "coarse_field": coarse,
        "C": C,
        "x0": x0,
        "coarse_likelihoods": coarse_likelihoods,
        "fine_likelihoods": fine_likelihoods,
        "durations": durations,
        "trace": trace,
        "prediction_residual": prediction_residual,
        "posterior_residual": posterior_residual,
        "evidence_residual": evidence_residual,
        "mass_residual": mass_residual,
        "positivity_violation": positivity_violation,
    }


def perturbation_certificates(ledger: Ledger, exact: dict[str, Any]) -> dict[str, Any]:
    C = exact["C"]
    x0 = exact["x0"]
    coarse_likelihoods = exact["coarse_likelihoods"]
    durations = exact["durations"]

    eps_values = np.logspace(-6, -1, 10)
    flow_actual = []
    flow_bound = []
    duration = 0.8
    _, coarse, _ = hidden_exchange_fields()
    coarse_endpoint = integrate_rk4(coarse, C @ x0, duration, max_step=5e-4)
    for eps in eps_values:
        fine_eps, _, _ = hidden_exchange_fields(epsilon=float(eps))
        fine_endpoint = integrate_rk4(fine_eps, x0, duration, max_step=5e-4)
        actual = float(np.linalg.norm(C @ fine_endpoint - coarse_endpoint, ord=1))
        bound = float(2.0 * eps * duration)
        flow_actual.append(actual)
        flow_bound.append(bound)
    flow_actual_arr = np.asarray(flow_actual)
    flow_bound_arr = np.asarray(flow_bound)
    flow_violation = float(np.max(flow_actual_arr - flow_bound_arr))
    ledger.add("QFDB", "controlled dynamical perturbation respects the flow certificate", max(0.0, flow_violation), 2e-9)
    flow_slope = float(np.polyfit(np.log(eps_values[-7:]), np.log(flow_actual_arr[-7:]), 1)[0])
    ledger.add("QFSL", "flow discrepancy has first order perturbation scaling", abs(flow_slope - 1.0), 0.08)

    eta = 0.03
    lamc = np.asarray([1.3, 0.8])
    lamf = C.T @ lamc + eta * np.asarray([1.0, -1.0, 0.0, 0.0])
    ledger.add(
        "QLPS",
        "perturbed likelihood remains strictly positive",
        float(lamf.min()),
        1e-12,
        comparator=">=",
    )
    obs_violations = []
    for mu_seed in range(40):
        rng = np.random.default_rng(1000 + mu_seed)
        mu = rng.dirichlet(np.ones(4))
        actual = bayes_commutation_residual(mu, lamf, lamc, C)
        zstar = min(float(lamf.min()), float(lamc.min()))
        bound = 2.0 * eta / zstar
        obs_violations.append(actual - bound)
    ledger.add("QOBB", "variation of the likelihood within a fiber respects the Bayesian bound", max(0.0, max(obs_violations)), 1e-12)

    eta_values = np.logspace(-6, math.log10(0.30), 10)
    bayes_actual: list[float] = []
    bayes_bound: list[float] = []
    direction = np.asarray([1.0, -1.0, 0.0, 0.0])
    prior = x0.copy()
    for eta_value in eta_values:
        fine_likelihood = C.T @ lamc + float(eta_value) * direction
        actual = bayes_commutation_residual(prior, fine_likelihood, lamc, C)
        fine_evidence = float(fine_likelihood @ prior)
        coarse_evidence = float(lamc @ (C @ prior))
        numerator = float(np.sum(prior * np.abs(float(eta_value) * direction)))
        bound = 2.0 * numerator / min(fine_evidence, coarse_evidence)
        bayes_actual.append(actual)
        bayes_bound.append(bound)
    bayes_actual_arr = np.asarray(bayes_actual)
    bayes_bound_arr = np.asarray(bayes_bound)
    ledger.add(
        "QBSC",
        "the Bayesian perturbation sweep remains below the likelihood certificate",
        max(0.0, float(np.max(bayes_actual_arr - bayes_bound_arr))),
        1e-12,
    )
    bayes_slope = float(
        np.polyfit(np.log(eta_values[:7]), np.log(bayes_actual_arr[:7]), 1)[0]
    )
    ledger.add(
        "QBSL",
        "Bayesian discrepancy has first order scaling for small fiber mismatch",
        abs(bayes_slope - 1.0),
        0.08,
    )

    normalization_violations = []
    for norm_seed in range(100):
        rng = np.random.default_rng(2000 + norm_seed)
        u = rng.uniform(0.05, 2.0, size=7)
        v = rng.uniform(0.05, 2.0, size=7)
        actual = float(np.linalg.norm(u / u.sum() - v / v.sum(), ord=1))
        bound = normalization_perturbation_bound(u, v)
        normalization_violations.append(actual - bound)
    ledger.add(
        "QNMB",
        "symmetric normalization bound uses the larger positive mass",
        max(0.0, max(normalization_violations)),
        1e-12,
    )

    joint_values = np.logspace(-6, -2, 9)
    posterior_actual: list[float] = []
    posterior_bound: list[float] = []
    evidence_actual: list[float] = []
    evidence_bound: list[float] = []

    for rho in joint_values:
        fine_rho, coarse_rho, _ = hidden_exchange_fields(epsilon=float(rho))
        fine_likelihoods = [
            C.T @ lam + rho * np.asarray([1.0, -1.0, 0.0, 0.0])
            for lam in coarse_likelihoods
        ]
        if any(np.any(lam <= 0) for lam in fine_likelihoods):
            raise RuntimeError("joint likelihood perturbation left the strictly positive regime")
        trace = simulate_prediction_update_filter(
            x0,
            C @ x0,
            fine_rho,
            coarse_rho,
            fine_likelihoods,
            coarse_likelihoods,
            durations,
            max_step=1e-3,
        )
        actual_post = float(np.linalg.norm(C @ trace.fine_posteriors[-1] - trace.coarse_posteriors[-1], ord=1))

        flow_L = np.ones(len(durations))
        bayes_L = []
        flow_d = []
        bayes_d = []
        for lamc, lamf, T in zip(coarse_likelihoods, fine_likelihoods, durations, strict=True):
            zstar = min(float(lamc.min()), float(lamf.min()))
            bayes_L.append(2.0 * float(lamc.max()) / float(lamc.min()))
            flow_d.append(2.0 * float(rho) * float(T))
            bayes_d.append(2.0 * float(rho) / zstar)
        bound_post, _, _ = posterior_error_certificate(0.0, flow_L, bayes_L, flow_d, bayes_d)
        posterior_actual.append(actual_post)
        posterior_bound.append(bound_post)

        step_actual = np.abs(trace.fine_evidence - trace.coarse_evidence)
        step_bounds = []
        for k, (lamc, pred_f, pred_c) in enumerate(
            zip(coarse_likelihoods, trace.fine_predictions, trace.coarse_predictions, strict=True)
        ):
            e_minus = float(np.linalg.norm(C @ pred_f - pred_c, ord=1))
            step_bounds.append(float(lamc.max()) * e_minus + float(rho))
        evidence_actual.append(float(step_actual.sum()))
        evidence_bound.append(float(np.sum(step_bounds)))

    posterior_actual_arr = np.asarray(posterior_actual)
    posterior_bound_arr = np.asarray(posterior_bound)
    evidence_actual_arr = np.asarray(evidence_actual)
    evidence_bound_arr = np.asarray(evidence_bound)

    ledger.add(
        "QPST",
        "recursive posterior certificate dominates every joint perturbation run",
        max(0.0, float(np.max(posterior_actual_arr - posterior_bound_arr))),
        1e-10,
    )
    posterior_slope = float(np.polyfit(np.log(joint_values[:6]), np.log(posterior_actual_arr[:6]), 1)[0])
    ledger.add("QPSL", "joint posterior discrepancy has first order scaling for small perturbations", abs(posterior_slope - 1.0), 0.12)
    ledger.add(
        "QLEV",
        "the evidence certificate at each step dominates the accumulated discrepancy",
        max(0.0, float(np.max(evidence_actual_arr - evidence_bound_arr))),
        1e-10,
    )

    return {
        "eps_values": eps_values,
        "flow_actual": flow_actual_arr,
        "flow_bound": flow_bound_arr,
        "flow_slope": flow_slope,
        "eta_values": eta_values,
        "bayes_actual": bayes_actual_arr,
        "bayes_bound": bayes_bound_arr,
        "bayes_slope": bayes_slope,
        "joint_values": joint_values,
        "posterior_actual": posterior_actual_arr,
        "posterior_bound": posterior_bound_arr,
        "posterior_slope": posterior_slope,
        "evidence_actual": evidence_actual_arr,
        "evidence_bound": evidence_bound_arr,
    }


def pruning_certificates(ledger: Ledger) -> dict[str, Any]:
    coefficients = np.geomspace(1.0, 1e-3, 36)
    probabilities, entropy, effective = hyperedge_energy_statistics(coefficients)
    residuals = best_k_residuals(coefficients)
    parseval_residual = abs(float(np.dot(coefficients, coefficients)) - float(np.sum(coefficients**2)))
    ledger.add("QPAR", "hyperedge energy satisfies the scalar Parseval identity", parseval_residual, TOL)
    monotonic_violation = max(0.0, float(np.max(np.diff(residuals))))
    terminal_residual = float(residuals[-1])
    ledger.add("QBST", "the residual from retaining the largest energy hyperedges decreases to zero", max(monotonic_violation, terminal_residual), TOL)
    return {
        "coefficients": coefficients,
        "probabilities": probabilities,
        "entropy": entropy,
        "effective_count": effective,
        "residuals": residuals,
    }


def make_hypergraph_figure() -> None:
    """Draw the fine hypergraph and its coarse quotient."""

    fig, ax = plt.subplots(figsize=(5.0, 3.2), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.text(2.35, 5.45, "Fine interaction fibers", ha="center", fontsize=9.8)
    ax.text(8.0, 5.45, "Coarse quotient", ha="center", fontsize=9.8)

    fine_inputs = [
        (0.65, 4.15, "$j$"),
        (0.65, 2.15, "$j'$"),
        (1.95, 4.15, "$k$"),
        (1.95, 2.15, "$k'$"),
    ]
    for x, y, label in fine_inputs:
        ax.add_patch(Circle((x, y), 0.28, fill=False, linewidth=1.15))
        ax.text(x, y, label, ha="center", va="center")
    ax.text(0.65, 1.35, "fiber $b$", ha="center", fontsize=7.6)
    ax.text(1.95, 1.35, "fiber $c$", ha="center", fontsize=7.6)

    junctions = [(3.25, 3.75), (3.25, 1.75)]
    outputs = [(4.35, 3.75, "$i$"), (4.35, 1.75, "$i'$ ")]
    for x, y in junctions:
        ax.add_patch(Circle((x, y), 0.12, fill=False, linewidth=1.05))
    for x, y, label in outputs:
        ax.add_patch(Circle((x, y), 0.28, fill=False, linewidth=1.15))
        ax.text(x, y, label.strip(), ha="center", va="center")
    ax.text(4.35, 1.05, "output fiber $a$", ha="center", fontsize=7.6)

    for start_point in [(0.65, 4.15), (1.95, 4.15)]:
        ax.add_patch(FancyArrowPatch(start_point, junctions[0], arrowstyle="->", mutation_scale=11, shrinkA=18, shrinkB=7))
    for start_point in [(0.65, 2.15), (1.95, 2.15)]:
        ax.add_patch(FancyArrowPatch(start_point, junctions[1], arrowstyle="->", mutation_scale=11, shrinkA=18, shrinkB=7))
    for junction, output in zip(junctions, outputs, strict=True):
        ax.add_patch(FancyArrowPatch(junction, output[:2], arrowstyle="->", mutation_scale=11, shrinkA=7, shrinkB=18))

    ax.text(2.45, 4.77, r"$g_{a;j,k}=g_{a;j',k'}$ on one product fiber", ha="center", fontsize=7.8)
    ax.add_patch(FancyArrowPatch((4.9, 3.0), (6.15, 3.0), arrowstyle="-|>", mutation_scale=16))
    ax.text(5.52, 3.35, r"$\pi_*$", ha="center")

    coarse_inputs = [(6.8, 3.9, "$b$"), (6.8, 2.1, "$c$")]
    for x, y, label in coarse_inputs:
        ax.add_patch(Circle((x, y), 0.34, fill=False, linewidth=1.15))
        ax.text(x, y, label, ha="center", va="center")
    coarse_junction = (8.2, 3.0)
    coarse_output = (9.35, 3.0)
    ax.add_patch(Circle(coarse_junction, 0.14, fill=False, linewidth=1.05))
    ax.add_patch(Circle(coarse_output, 0.34, fill=False, linewidth=1.15))
    ax.text(*coarse_output, "$a$", ha="center", va="center")
    for start_point in [(6.8, 3.9), (6.8, 2.1)]:
        ax.add_patch(FancyArrowPatch(start_point, coarse_junction, arrowstyle="->", mutation_scale=11, shrinkA=22, shrinkB=8))
    ax.add_patch(FancyArrowPatch(coarse_junction, coarse_output, arrowstyle="->", mutation_scale=11, shrinkA=8, shrinkB=22))
    ax.text(8.05, 0.85, r"one descended hyperedge $(b,c)\to a$", ha="center", fontsize=7.8)
    save_figure(fig, "hypergraph_quotient")


def make_fiber_constancy_figure(exact_tensors: dict[str, Any]) -> None:
    """Visualize the block constancy required by the quadratic quotient test."""

    fine = exact_tensors["order_2"]["fine"]
    C = exact_tensors["C"]
    aggregated = aggregate_output_coefficients(fine, C)[0]
    variation = exact_tensors["order_2"]["fiber_variation"]

    fig, ax = plt.subplots(figsize=(3.6, 3.15), constrained_layout=True)
    image = ax.imshow(aggregated, origin="lower", aspect="equal")
    ax.axvline(1.5, linestyle="--", linewidth=1.0)
    ax.axhline(1.5, linestyle="--", linewidth=1.0)
    ax.set_xticks(range(4), labels=["1", "2", "3", "4"])
    ax.set_yticks(range(4), labels=["1", "2", "3", "4"])
    ax.set_xlabel("Fine input index in slot 2", fontsize=9)
    ax.set_ylabel("Fine input index in slot 1", fontsize=9)
    colorbar = fig.colorbar(image, ax=ax, pad=0.03)
    colorbar.set_label("Aggregated coefficient", fontsize=8)
    ax.tick_params(labelsize=8)
    colorbar.ax.tick_params(labelsize=8)
    save_figure(fig, "fiber_constancy_map")


def _trajectory(field: Callable[[np.ndarray], np.ndarray], initial: np.ndarray, duration: float, step: float) -> tuple[np.ndarray, np.ndarray]:
    steps = max(1, int(round(duration / step)))
    times = np.linspace(0.0, duration, steps + 1)
    state = initial.copy()
    states = [state.copy()]
    for _ in range(steps):
        state = integrate_rk4(field, state, step, max_step=step)
        states.append(state.copy())
    return times, np.asarray(states)


def make_exact_quotient_flow_figure(exact: dict[str, Any]) -> None:
    """Show hidden fine motion and exact agreement of the aggregate flow."""

    C = exact["C"]
    times, fine_states = _trajectory(exact["fine_field"], exact["x0"], 4.0, 0.01)
    _, coarse_states = _trajectory(exact["coarse_field"], C @ exact["x0"], 4.0, 0.01)
    aggregate = np.asarray([C @ state for state in fine_states])
    residual = float(np.max(np.linalg.norm(aggregate - coarse_states, ord=1, axis=1)))

    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.plot(times, fine_states[:, 0], linestyle=":", label=r"fine state $x_1$")
    ax.plot(times, fine_states[:, 1], linestyle="-.", label=r"fine state $x_2$")
    ax.plot(times, aggregate[:, 0], linewidth=2.3, label=r"aggregate $x_1+x_2$")
    ax.plot(times, coarse_states[:, 0], linestyle="--", marker="o", markevery=40, label=r"coarse state $z_1$")
    ax.set_xlabel("Time")
    ax.set_ylabel("Mass in the first coarse packet")
    ax.legend(frameon=False, ncols=2)
    ax.text(
        0.985,
        0.95,
        f"maximum aggregate residual = {residual:.2e}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9.2,
        bbox={"boxstyle": "round,pad=0.18", "alpha": 0.10},
    )
    clean_plot_axes(ax)
    save_figure(fig, "exact_quotient_flow")


def make_exact_filter_residual_figure(exact: dict[str, Any]) -> None:
    """Plot exact filter commutation residuals at floating point scale."""

    trace = exact["trace"]
    C = exact["C"]
    residuals = np.asarray(
        [
            np.linalg.norm(C @ fine - coarse, ord=1)
            for fine, coarse in zip(trace.fine_posteriors, trace.coarse_posteriors, strict=True)
        ]
    )
    steps = np.arange(residuals.size)
    floor = 1e-18
    epsilon = np.finfo(float).eps

    fig, ax = plt.subplots(figsize=(7.0, 4.2), constrained_layout=True)
    ax.semilogy(steps, np.maximum(residuals, floor), marker="o", label="posterior residual")
    ax.semilogy(steps, np.full_like(steps, epsilon, dtype=float), linestyle="--", label="double precision epsilon")
    ax.set_xlabel("Prediction and update step")
    ax.set_ylabel(r"Aggregate discrepancy in $\ell^1$")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.legend(frameon=False)
    ax.text(0.985, 0.95, f"maximum residual = {residuals.max():.2e}", transform=ax.transAxes, ha="right", va="top", fontsize=9.2)
    clean_plot_axes(ax)
    save_figure(fig, "exact_filtering_residual")


def make_flow_bound_figure(perturb: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.3), constrained_layout=True)
    ax.loglog(perturb["eps_values"], perturb["flow_actual"], marker="o", label="observed flow error")
    ax.loglog(perturb["eps_values"], perturb["flow_bound"], linestyle="--", marker="s", label=r"certificate $2\varepsilon T$")
    ax.set_xlabel(r"Dynamical perturbation $\varepsilon$")
    ax.set_ylabel(r"Flow discrepancy in $\ell^1$")
    ax.xaxis.set_major_locator(LogLocator(base=10))
    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.legend(frameon=False)
    ax.text(0.985, 0.04, f"fitted slope = {perturb['flow_slope']:.3f}", transform=ax.transAxes, ha="right", va="bottom", fontsize=9.2)
    clean_plot_axes(ax)
    save_figure(fig, "flow_perturbation_scaling")


def make_bayesian_bound_figure(perturb: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.3), constrained_layout=True)
    ax.loglog(perturb["eta_values"], perturb["bayes_actual"], marker="o", label="observed update error")
    ax.loglog(perturb["eta_values"], perturb["bayes_bound"], linestyle="--", marker="s", label="normalization certificate")
    ax.set_xlabel(r"Likelihood fiber mismatch $\eta$")
    ax.set_ylabel(r"Update discrepancy in $\ell^1$")
    ax.xaxis.set_major_locator(LogLocator(base=10))
    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.legend(frameon=False)
    ax.text(0.985, 0.04, f"fitted slope = {perturb['bayes_slope']:.3f}", transform=ax.transAxes, ha="right", va="bottom", fontsize=9.2)
    clean_plot_axes(ax)
    save_figure(fig, "bayesian_perturbation_scaling")


def make_posterior_figure(perturb: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.3), constrained_layout=True)
    ax.loglog(perturb["joint_values"], perturb["posterior_actual"], marker="o", label="observed final error")
    ax.loglog(perturb["joint_values"], perturb["posterior_bound"], linestyle="--", marker="s", label="recursive certificate")
    ax.set_xlabel(r"Joint perturbation $\rho$, with $\varepsilon=\eta=\rho$")
    ax.set_ylabel(r"Final posterior discrepancy in $\ell^1$")
    ax.xaxis.set_major_locator(LogLocator(base=10))
    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.legend(frameon=False)
    ax.text(0.985, 0.04, f"fitted slope = {perturb['posterior_slope']:.3f}", transform=ax.transAxes, ha="right", va="bottom", fontsize=9.2)
    clean_plot_axes(ax)
    save_figure(fig, "posterior_error_certificate")


def make_hyperedge_energy_figure(pruning: dict[str, Any]) -> None:
    energy = np.sort(pruning["probabilities"])[::-1]
    ranks = np.arange(1, energy.size + 1)
    fig, ax = plt.subplots(figsize=(3.75, 3.15), constrained_layout=True)
    ax.semilogy(ranks, energy, marker="o")
    ax.set_xlabel("Hyperedge rank", fontsize=9)
    ax.set_ylabel("Normalized squared energy", fontsize=9)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.text(0.985, 0.95, f"entropy = {pruning['entropy']:.3f}\neffective count = {pruning['effective_count']:.2f}", transform=ax.transAxes, ha="right", va="top", fontsize=7.8)
    ax.tick_params(labelsize=8)
    clean_plot_axes(ax)
    save_figure(fig, "hyperedge_energy_spectrum")


def make_pruning_figure(pruning: dict[str, Any]) -> None:
    residuals = pruning["residuals"]
    fig, ax = plt.subplots(figsize=(3.75, 3.15), constrained_layout=True)
    ax.semilogy(np.arange(residuals.size), np.maximum(residuals, 1e-16), marker="o")
    ax.set_xlabel(r"Retained hyperedge count $k$", fontsize=9)
    ax.set_ylabel("Hilbert Schmidt residual", fontsize=9)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.tick_params(labelsize=8)
    clean_plot_axes(ax)
    save_figure(fig, "hyperedge_pruning")


def write_tables(ledger: Ledger, exact: dict[str, Any], perturb: dict[str, Any], pruning: dict[str, Any]) -> None:
    with (TABLES / "test_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "statement", "value", "tolerance", "comparator", "status"])
        writer.writeheader()
        writer.writerows(ledger.rows)

    macros = rf"""% Generated by examples/run_certificates.py
\newcommand{{\VerificationPassCount}}{{{ledger.passed}}}
\newcommand{{\VerificationFailCount}}{{{ledger.failed}}}
\newcommand{{\ExactPredictionResidual}}{{\ensuremath{{{tex_number(exact['prediction_residual'])}}}}}
\newcommand{{\ExactPosteriorResidual}}{{\ensuremath{{{tex_number(exact['posterior_residual'])}}}}}
\newcommand{{\ExactEvidenceResidual}}{{\ensuremath{{{tex_number(exact['evidence_residual'])}}}}}
\newcommand{{\PerturbationSlope}}{{\ensuremath{{{perturb['posterior_slope']:.4f}}}}}
\newcommand{{\HyperedgeEntropyValue}}{{\ensuremath{{{pruning['entropy']:.4f}}}}}
\newcommand{{\EffectiveHyperedgeCount}}{{\ensuremath{{{pruning['effective_count']:.3f}}}}}
"""
    (TABLES / "verification_macros.tex").write_text(macros, encoding="utf-8")

    lines = [
        r"\begin{longtable}{@{}p{0.08\linewidth}p{0.43\linewidth}p{0.12\linewidth}p{0.12\linewidth}p{0.08\linewidth}@{}}",
        r"\caption{Executed deterministic finite certificate ledger.}\label{tab:executed-ledger}\\",
        r"\toprule",
        r"ID & Check & Value & Threshold & Status\\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"ID & Check & Value & Threshold & Status\\",
        r"\midrule",
        r"\endhead",
    ]
    for row in ledger.rows:
        comparator = r"\leq" if row["comparator"] == "<=" else r"\geq"
        threshold = f"${comparator} {tex_threshold(row['tolerance'])}$"
        lines.append(
            f"{tex_escape(row['id'])} & {tex_escape(row['statement'])} & "
            f"${tex_number(row['value'])}$ & {threshold} & {row['status']}\\\\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}"])
    (TABLES / "test_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_results(
    ledger: Ledger,
    exact_tensors: dict[str, Any],
    multilevel: dict[str, float],
    exact_model: dict[str, Any],
    perturb: dict[str, Any],
    pruning: dict[str, Any],
) -> None:
    payload = {
        "schema": "priq.verification.v1",
        "version": "0.1.4",
        "deterministic_seed": 20260902,
        "pass_count": ledger.passed,
        "fail_count": ledger.failed,
        "checks": ledger.rows,
        "summary": {
            "exact_prediction_residual": exact_model["prediction_residual"],
            "exact_posterior_residual": exact_model["posterior_residual"],
            "exact_evidence_residual": exact_model["evidence_residual"],
            "flow_perturbation_slope": perturb["flow_slope"],
            "posterior_perturbation_slope": perturb["posterior_slope"],
            "bayesian_perturbation_slope": perturb["bayes_slope"],
            "quadratic_fiber_variation": exact_tensors["order_2"]["fiber_variation"],
            "hyperedge_entropy": pruning["entropy"],
            "effective_hyperedge_count": pruning["effective_count"],
            **multilevel,
        },
        "arrays": {
            "flow_eps": perturb["eps_values"].tolist(),
            "flow_actual": perturb["flow_actual"].tolist(),
            "flow_bound": perturb["flow_bound"].tolist(),
            "bayes_eta": perturb["eta_values"].tolist(),
            "bayes_actual": perturb["bayes_actual"].tolist(),
            "bayes_bound": perturb["bayes_bound"].tolist(),
            "joint_perturbation": perturb["joint_values"].tolist(),
            "posterior_actual": perturb["posterior_actual"].tolist(),
            "posterior_bound": perturb["posterior_bound"].tolist(),
            "evidence_actual": perturb["evidence_actual"].tolist(),
            "evidence_bound": perturb["evidence_bound"].tolist(),
            "hyperedge_energy_probability": pruning["probabilities"].tolist(),
            "hyperedge_best_k_residual": pruning["residuals"].tolist(),
        },
    }
    (RESULTS / "verification.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (RESULTS / "summary.json").write_text(json.dumps(payload["summary"], indent=2) + "\n", encoding="utf-8")


def main() -> int:
    rng = np.random.default_rng(20260902)
    ledger = Ledger()
    exact_tensors = exact_tensor_certificates(ledger, rng)
    multilevel = multilevel_certificates(ledger, rng)
    exact_model = exact_model_certificates(ledger, rng)
    perturb = perturbation_certificates(ledger, exact_model)
    pruning = pruning_certificates(ledger)

    make_hypergraph_figure()
    make_fiber_constancy_figure(exact_tensors)
    make_exact_quotient_flow_figure(exact_model)
    make_exact_filter_residual_figure(exact_model)
    make_flow_bound_figure(perturb)
    make_bayesian_bound_figure(perturb)
    make_posterior_figure(perturb)
    make_hyperedge_energy_figure(pruning)
    make_pruning_figure(pruning)
    write_tables(ledger, exact_model, perturb, pruning)
    write_results(ledger, exact_tensors, multilevel, exact_model, perturb, pruning)

    print(json.dumps({"pass_count": ledger.passed, "fail_count": ledger.failed}, indent=2))
    if ledger.failed:
        for row in ledger.rows:
            if row["status"] == "FAIL":
                print(row)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
