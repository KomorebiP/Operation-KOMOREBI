from __future__ import annotations

import json
from pathlib import Path
import numpy as np
from scipy.linalg import expm

from .packets import coordinate_projectors, packet_blocks, reconstruct_from_blocks, block_composition
from .semigroup import (
    feshbach_effective_operator,
    projected_resolvent,
    memory_kernel_laplace,
    numerical_memory_laplace,
    generator_refinement_defect,
    semigroup_refinement_residual,
    duhamel_defect_integral,
)
from .markov import (
    symmetric_random_walk,
    exact_lumped_chain,
    lumping_defect,
    finite_horizon_lumping_error,
    survival_curve,
)
from .bayes import (
    bayes_update,
    packet_bayes_update,
    beta_binomial_posterior,
    bayesian_flow,
    bayesian_flow_generator,
    hmm_filter,
    coarsen_probability,
    bayesian_coarsening_defect,
    bayesian_sufficient_partition,
    canonical_bayesian_partition,
)
from .conditional import weighted_conditional_expectation, martingale_differences, gaussian_hermite_gram
from .fractional import (
    fractional_semigroup,
    scalar_square_root_subordination,
    generator_intertwining_defect,
    fractional_intertwining_defect,
    fractional_holder_bound,
    fractional_gap_bound,
    fractional_semigroup_intertwining_defect,
    fractional_semigroup_bound,
)
from .pde import discrete_green_scaled, continuous_dirichlet_green, low_mode_eigenvalue_error, dirichlet_laplacian_1d
from .feynman_kac import discrete_feynman_kac, enumerate_feynman_kac


def _max_abs(a: np.ndarray) -> float:
    return float(np.max(np.abs(a)))


def run_experiments(output: str | Path | None = None) -> dict[str, object]:
    rng = np.random.default_rng(20260727)

    # Packet semigroup law.
    a = rng.normal(size=(6, 6))
    generator = -0.4 * (a.T @ a)
    projectors = coordinate_projectors([[0, 1], [2, 3], [4, 5]], 6)
    t, s = 0.31, 0.47
    left_blocks = packet_blocks(expm(t * generator), projectors)
    right_blocks = packet_blocks(expm(s * generator), projectors)
    composed = block_composition(left_blocks, right_blocks)
    target = packet_blocks(expm((t + s) * generator), projectors)
    semigroup_block_residual = max(
        _max_abs(composed[i][j] - target[i][j]) for i in range(3) for j in range(3)
    )
    reconstruction_residual = _max_abs(reconstruct_from_blocks(target) - expm((t + s) * generator))

    # Markov and lumping.
    positions, probabilities = symmetric_random_walk(20)
    random_walk_mass_error = abs(float(probabilities.sum()) - 1.0)
    random_walk_mean = float(positions @ probabilities)
    random_walk_variance = float((positions**2) @ probabilities - random_walk_mean**2)
    k, c, kbar = exact_lumped_chain()
    exact_lumping_defect = _max_abs(lumping_defect(k, c, kbar))
    exact_horizon_error = _max_abs(finite_horizon_lumping_error(k, c, kbar, 12))
    perturbed = k.copy()
    perturbed[:, 0] += np.array([0.01, 0.0, -0.01, 0.0])
    defect = lumping_defect(perturbed, c, kbar)
    eps = float(np.linalg.norm(defect, 1))
    horizon = 10
    actual = float(np.linalg.norm(finite_horizon_lumping_error(perturbed, c, kbar, horizon), 1))
    bound = horizon * eps

    # Bayesian identities.
    prior = np.array([0.12, 0.18, 0.30, 0.40])
    l1 = np.array([0.2, 0.8, 0.6, 0.3])
    l2 = np.array([0.9, 0.4, 0.7, 0.5])
    bayes_composition = _max_abs(bayes_update(bayes_update(prior, l1), l2) - bayes_update(prior, l1 * l2))
    packet = packet_bayes_update(prior, l1, [[0, 1], [2, 3]])
    packet_bayes_residual = _max_abs(packet["posterior"] - packet["reconstructed"])
    posterior = beta_binomial_posterior(2.0, 3.0, 7, 10)
    score = np.array([-0.4, 0.1, 0.8, 1.2])
    flow_t = 0.73
    dt = 1e-6
    numerical_derivative = (bayesian_flow(prior, score, flow_t + dt) - bayesian_flow(prior, score, flow_t - dt)) / (2 * dt)
    flow_generator = bayesian_flow_generator(bayesian_flow(prior, score, flow_t), score)
    bayes_flow_residual = _max_abs(numerical_derivative - flow_generator)
    bayes_semigroup_residual = _max_abs(
        bayesian_flow(bayesian_flow(prior, score, 0.4), score, 0.7) - bayesian_flow(prior, score, 1.1)
    )

    # Exact Bayesian refinement and information-loss factorization.
    refinement_groups = ((0, 1), (2, 3))
    sufficient_likelihood = np.array([0.4, 0.4, 1.7, 1.7])
    _, coarse_sufficient = bayesian_sufficient_partition(
        sufficient_likelihood, refinement_groups
    )
    fine_then_coarse = coarsen_probability(
        bayes_update(prior, sufficient_likelihood), refinement_groups
    )
    coarse_then_update = bayes_update(
        coarsen_probability(prior, refinement_groups), coarse_sufficient
    )
    bayesian_refinement_residual = _max_abs(fine_then_coarse - coarse_then_update)

    nonsufficient_likelihood = np.array([0.2, 0.9, 1.4, 0.8])
    declared_coarse_likelihood = np.array([0.55, 1.10])
    bayes_defect_record = bayesian_coarsening_defect(
        prior, nonsufficient_likelihood, refinement_groups, declared_coarse_likelihood
    )
    bayesian_defect_factorization_residual = _max_abs(
        bayes_defect_record["defect"] - bayes_defect_record["factored_defect"]
    )
    bayesian_defect_l1 = float(np.linalg.norm(bayes_defect_record["defect"], 1))
    bayesian_defect_bound = float(bayes_defect_record["l1_bound"])

    same_coarse_a = np.array([0.25, 0.05, 0.35, 0.35])
    same_coarse_b = np.array([0.05, 0.25, 0.35, 0.35])
    necessity_witness = _max_abs(
        coarsen_probability(
            bayes_update(same_coarse_a, nonsufficient_likelihood), refinement_groups
        )
        - coarsen_probability(
            bayes_update(same_coarse_b, nonsufficient_likelihood), refinement_groups
        )
    )
    canonical_partition = canonical_bayesian_partition(
        [
            np.array([0.2, 0.2, 0.7, 0.7, 1.1]),
            np.array([0.8, 0.8, 0.1, 0.1, 0.5]),
        ]
    )

    # Conditional expectation / martingale.
    pi = np.ones(8) / 8
    p0 = weighted_conditional_expectation([list(range(8))], pi)
    p1 = weighted_conditional_expectation([list(range(4)), list(range(4, 8))], pi)
    p2 = weighted_conditional_expectation([[0, 1], [2, 3], [4, 5], [6, 7]], pi)
    p3 = np.eye(8)
    tower_residual = _max_abs(p1 @ p2 - p1)
    ds = martingale_differences([p0, p1, p2, p3])
    martingale_orthogonality = max(_max_abs(ds[i] @ ds[j]) for i in range(4) for j in range(4) if i != j)
    hermite_gram_error = _max_abs(gaussian_hermite_gram(8, 80) - np.eye(9))

    # Fractional semigroups and subordination.
    lap_small, _, _ = dirichlet_laplacian_1d(18)
    frac_a = fractional_semigroup(lap_small, 0.5, 0.31)
    frac_b = fractional_semigroup(lap_small, 0.5, 0.47)
    frac_c = fractional_semigroup(lap_small, 0.5, 0.78)
    fractional_semigroup_residual = _max_abs(frac_a @ frac_b - frac_c)
    subordination_errors = {
        str(lam): abs(scalar_square_root_subordination(lam, 0.7) - np.exp(-0.7 * np.sqrt(lam)))
        for lam in (0.25, 1.0, 4.0, 9.0)
    }

    # Fractional naturality and resolvent-defect transfer.
    fine_frac = np.diag([0.45, 0.9, 1.8, 3.2])
    coarse_frac = np.array([[0.6, -0.08], [-0.08, 1.4]])
    coarsener_frac = np.array([[0.8, 0.1, 0.0, 0.2], [0.0, 0.25, 0.5, 0.55]])
    alpha_frac = 0.58
    time_frac = 0.75
    generator_frac_defect = generator_intertwining_defect(
        fine_frac, coarse_frac, coarsener_frac
    )
    fractional_frac_defect = fractional_intertwining_defect(
        fine_frac, coarse_frac, coarsener_frac, alpha_frac
    )
    fractional_defect_norm = float(np.linalg.norm(fractional_frac_defect, 2))
    fractional_holder_certificate = fractional_holder_bound(
        fine_frac, coarse_frac, coarsener_frac, alpha_frac
    )
    fractional_gap_certificate = fractional_gap_bound(
        fine_frac, coarse_frac, coarsener_frac, alpha_frac
    )
    fractional_semigroup_defect = fractional_semigroup_intertwining_defect(
        fine_frac, coarse_frac, coarsener_frac, alpha_frac, time_frac
    )
    fractional_semigroup_defect_norm = float(np.linalg.norm(fractional_semigroup_defect, 2))
    fractional_semigroup_certificate = fractional_semigroup_bound(
        fine_frac, coarse_frac, coarsener_frac, alpha_frac, time_frac, use_gap=True
    )
    exact_fine_frac = np.diag([0.0, 1.0, 2.0, 4.0])
    exact_coarse_frac = np.diag([0.0, 2.0])
    exact_coarsener_frac = np.array(
        [[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]]
    )
    exact_fractional_naturality_residual = float(
        np.linalg.norm(
            fractional_intertwining_defect(
                exact_fine_frac, exact_coarse_frac, exact_coarsener_frac, alpha_frac
            ),
            2,
        )
    )

    # PDE Green and eigenvalue convergence.
    green_errors = {}
    eigen_errors = {}
    for n in (15, 31, 63, 127):
        discrete, grid, _ = discrete_green_scaled(n)
        exact = continuous_dirichlet_green(grid, grid)
        green_errors[str(n)] = _max_abs(discrete - exact)
        eigen_errors[str(n)] = low_mode_eigenvalue_error(n, 1)
    ns = np.array([31, 63, 127, 255], dtype=float)
    hs = 1.0 / (ns + 1.0)
    errs = np.array([low_mode_eigenvalue_error(int(n), 1) for n in ns])
    pde_order = float(np.polyfit(np.log(hs), np.log(errs), 1)[0])

    # Feynman-Kac exact enumeration.
    fk_kernel = np.array([[0.75, 0.25], [0.25, 0.75]], dtype=float)
    potential = np.array([0.15, 0.7])
    terminal = np.array([1.0, 2.0])
    fk_matrix = discrete_feynman_kac(fk_kernel, potential, terminal, 6)
    fk_enum = enumerate_feynman_kac(fk_kernel, potential, terminal, 6)
    feynman_kac_residual = _max_abs(fk_matrix - fk_enum)

    # Exact latent-state elimination and memory kernel.
    latent_operator = np.array(
        [
            [-1.2, 0.3, 0.4, 0.0],
            [0.2, -0.9, 0.0, 0.25],
            [0.35, 0.0, -1.7, 0.5],
            [0.0, 0.4, 0.2, -1.4],
        ],
        dtype=float,
    )
    z = 2.3
    effective = feshbach_effective_operator(latent_operator, [0, 1], z)
    feshbach_residual = _max_abs(np.linalg.inv(effective) - projected_resolvent(latent_operator, [0, 1], z))
    memory_exact = memory_kernel_laplace(latent_operator, [0, 1], z)
    memory_numeric = numerical_memory_laplace(latent_operator, [0, 1], z, upper=45.0)
    memory_laplace_residual = _max_abs(memory_exact - memory_numeric)

    # Refinement intertwining and Duhamel identity.
    coarse = np.array([[-0.4, 0.2], [0.4, -0.2]], dtype=float)
    coarsener = np.array([[0.5, 0.5, 0.0, 0.0], [0.0, 0.0, 0.5, 0.5]], dtype=float)
    embedder = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]], dtype=float)
    micro = np.array(
        [
            [-1.0, 1.0, 0.0, 0.0],
            [1.0, -1.0, 0.0, 0.0],
            [0.0, 0.0, -1.3, 1.3],
            [0.0, 0.0, 1.3, -1.3],
        ]
    )
    fine_exact = embedder @ coarse @ coarsener + micro
    exact_generator_defect = _max_abs(generator_refinement_defect(coarsener, fine_exact, coarse))
    exact_semigroup_defect = _max_abs(semigroup_refinement_residual(coarsener, fine_exact, coarse, 1.1))
    perturbation = np.array(
        [[0.02, 0.0, -0.01, 0.0], [0.0, -0.02, 0.0, 0.01], [-0.02, 0.0, 0.01, 0.0], [0.0, 0.02, 0.0, -0.01]]
    )
    fine_perturbed = fine_exact + perturbation
    time = 0.85
    semigroup_defect_matrix = semigroup_refinement_residual(coarsener, fine_perturbed, coarse, time)
    duhamel_matrix = duhamel_defect_integral(coarsener, fine_perturbed, coarse, time)
    duhamel_residual = _max_abs(semigroup_defect_matrix - duhamel_matrix)

    # HMM and survival.
    likelihoods = [np.array([0.85, 0.25]), np.array([0.35, 0.8]), np.array([0.9, 0.2])]
    hmm_states = hmm_filter(fk_kernel, np.array([0.6, 0.4]), likelihoods)
    hmm_mass_error = max(abs(float(p.sum()) - 1.0) for p in hmm_states)
    transient = np.array([[-0.45, 0.12, 0.0], [0.30, -0.52, 0.18], [0.0, 0.28, -0.60]], dtype=float)
    survival = survival_curve(transient, np.array([1.0, 0.0, 0.0]), np.linspace(0, 12, 241))
    survival_monotonic_violation = float(np.max(np.maximum(np.diff(survival["survival"]), 0.0)))
    minimum_hazard = float(np.min(survival["hazard"]))

    results: dict[str, object] = {
        "author": "Komorebi P.",
        "profile": "cpu_exact_and_numerical",
        "packet_semigroup": {
            "block_composition_residual": semigroup_block_residual,
            "operator_reconstruction_residual": reconstruction_residual,
        },
        "random_walk": {
            "steps": 20,
            "mass_error": random_walk_mass_error,
            "mean": random_walk_mean,
            "variance": random_walk_variance,
        },
        "markov_lumping": {
            "exact_generator_defect": exact_lumping_defect,
            "exact_horizon_error": exact_horizon_error,
            "perturbed_one_step_defect_norm_1": eps,
            "perturbed_horizon": horizon,
            "perturbed_actual_error_norm_1": actual,
            "linear_bound": bound,
        },
        "bayesian": {
            "composition_residual": bayes_composition,
            "packet_reconstruction_residual": packet_bayes_residual,
            "flow_generator_residual": bayes_flow_residual,
            "flow_semigroup_residual": bayes_semigroup_residual,
            "beta_binomial_posterior": posterior,
            "refinement_commutation_residual": bayesian_refinement_residual,
            "defect_factorization_residual": bayesian_defect_factorization_residual,
            "defect_l1": bayesian_defect_l1,
            "defect_l1_bound": bayesian_defect_bound,
            "necessity_witness_difference": necessity_witness,
            "canonical_sufficient_partition": [list(group) for group in canonical_partition],
            "effective_coarse_likelihood": bayes_defect_record["effective_likelihood"].tolist(),
            "information_loss_packet": bayes_defect_record["information_loss_packet"].tolist(),
        },
        "conditional_expectation": {
            "tower_residual": tower_residual,
            "martingale_difference_orthogonality": martingale_orthogonality,
            "hermite_gram_residual": hermite_gram_error,
        },
        "fractional": {
            "semigroup_residual": fractional_semigroup_residual,
            "subordination_errors": subordination_errors,
            "generator_refinement_defect_norm": float(np.linalg.norm(generator_frac_defect, 2)),
            "fractional_refinement_defect_norm": fractional_defect_norm,
            "holder_certificate": fractional_holder_certificate,
            "gap_certificate": fractional_gap_certificate,
            "fractional_semigroup_defect_norm": fractional_semigroup_defect_norm,
            "fractional_semigroup_certificate": fractional_semigroup_certificate,
            "exact_naturality_residual": exact_fractional_naturality_residual,
            "alpha": alpha_frac,
            "time": time_frac,
        },
        "pde": {
            "green_max_errors": green_errors,
            "first_eigenvalue_errors": eigen_errors,
            "observed_order": pde_order,
        },
        "feynman_kac": {"enumeration_residual": feynman_kac_residual},
        "latent_elimination": {
            "feshbach_resolvent_residual": feshbach_residual,
            "memory_laplace_residual": memory_laplace_residual,
        },
        "refinement": {
            "exact_generator_defect": exact_generator_defect,
            "exact_semigroup_defect": exact_semigroup_defect,
            "duhamel_identity_residual": duhamel_residual,
        },
        "hmm": {"normalization_error": hmm_mass_error, "filtered_states": [p.tolist() for p in hmm_states]},
        "survival": {
            "monotonicity_violation": survival_monotonic_violation,
            "minimum_hazard": minimum_hazard,
            "final_survival": float(survival["survival"][-1]),
        },
    }

    if output is not None:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    return results
