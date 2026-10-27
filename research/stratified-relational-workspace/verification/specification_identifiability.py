from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

RESULTS_DIR = Path(__file__).with_name("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT = RESULTS_DIR / "specification_identifiability.json"


def assert_close(a: float, b: float, tol: float = 1e-12) -> None:
    if not math.isclose(a, b, rel_tol=tol, abs_tol=tol):
        raise AssertionError(f'{a!r} != {b!r}')


def specification_transport_check() -> dict[str, Any]:
    margins = [0.42, 0.31, 0.27]
    lipschitz = [0.80, 0.50, 0.40]
    max_distance = 0.20
    mismatch = [0.03, 0.01, 0.02]
    budgets = [l * max_distance + b for l, b in zip(lipschitz, mismatch)]
    transported_lower_bounds = [m - b for m, b in zip(margins, budgets)]
    robust = all(x > 0.0 for x in transported_lower_bounds)
    radius_lower_bound_zero_mismatch = min(
        m / l for m, l in zip(margins, lipschitz) if l > 0.0
    )
    if not robust:
        raise AssertionError('Specification-transport condition should pass.')
    if radius_lower_bound_zero_mismatch <= max_distance:
        raise AssertionError('Radius lower bound should cover the audited family.')
    return {
        'reference_margins': margins,
        'transport_budgets': budgets,
        'transported_lower_bounds': transported_lower_bounds,
        'robust_across_family': robust,
        'zero_mismatch_radius_lower_bound': radius_lower_bound_zero_mismatch,
        'audited_family_radius': max_distance,
    }


def nonidentifiability_check() -> dict[str, Any]:
    probability_rule_outputs_one = 0.37
    error_if_true_certificate_zero = probability_rule_outputs_one
    error_if_true_certificate_one = 1.0 - probability_rule_outputs_one
    error_sum = error_if_true_certificate_zero + error_if_true_certificate_one
    worst_case_error = max(
        error_if_true_certificate_zero, error_if_true_certificate_one
    )
    minimax_error = 0.5
    assert_close(error_sum, 1.0)
    if worst_case_error < minimax_error:
        raise AssertionError('Two-point indistinguishability lower bound failed.')
    return {
        'experimentally_equivalent_realizations': True,
        'certificate_values': [0, 1],
        'rule_probability_output_one': probability_rule_outputs_one,
        'error_probabilities': [
            error_if_true_certificate_zero,
            error_if_true_certificate_one,
        ],
        'error_sum': error_sum,
        'worst_case_error': worst_case_error,
        'minimax_lower_bound': minimax_error,
    }


def identified_set_check() -> dict[str, Any]:
    mixed_margins = [0.14, 0.06, -0.02, 0.11]
    pass_margins = [0.04, 0.08, 0.06]
    fail_margins = [-0.03, -0.09, -0.01]

    def classify(values: list[float]) -> str:
        lower = min(values)
        upper = max(values)
        if lower > 0.0:
            return 'identified_pass'
        if upper <= 0.0:
            return 'identified_fail'
        return 'not_identified'

    mixed_status = classify(mixed_margins)
    pass_status = classify(pass_margins)
    fail_status = classify(fail_margins)
    if mixed_status != 'not_identified':
        raise AssertionError('Mixed identified set should be unresolved.')
    if pass_status != 'identified_pass' or fail_status != 'identified_fail':
        raise AssertionError('Point-sign identification classification failed.')
    return {
        'mixed_margin_set': mixed_margins,
        'mixed_bounds': [min(mixed_margins), max(mixed_margins)],
        'mixed_status': mixed_status,
        'positive_set_status': pass_status,
        'nonpositive_set_status': fail_status,
    }


def finite_sample_check() -> dict[str, Any]:
    n = 2500
    gates = 12
    specifications = 30
    delta = 0.05
    epsilon = math.sqrt(
        math.log(2.0 * gates * specifications / delta) / (2.0 * n)
    )
    empirical_lower_envelope = 0.09
    adjusted_lower_envelope = empirical_lower_envelope - epsilon
    robust_pass = adjusted_lower_envelope > 0.0
    if not robust_pass:
        raise AssertionError('Chosen finite-grid example should certify.')

    eta = 0.04
    covering_number = 80
    lipschitz = 0.30
    continuous_epsilon = math.sqrt(
        math.log(2.0 * gates * covering_number / delta) / (2.0 * n)
    ) + 2.0 * lipschitz * eta

    return {
        'sample_size': n,
        'gate_count': gates,
        'specification_count': specifications,
        'delta': delta,
        'finite_grid_uniform_radius': epsilon,
        'empirical_lower_envelope': empirical_lower_envelope,
        'adjusted_lower_envelope': adjusted_lower_envelope,
        'robust_pass': robust_pass,
        'continuous_family': {
            'eta': eta,
            'covering_number': covering_number,
            'lipschitz_constant': lipschitz,
            'uniform_radius': continuous_epsilon,
        },
    }


def selection_check() -> dict[str, Any]:
    alpha = 0.05
    candidate_specifications = 20
    familywise_false_pass = 1.0 - (1.0 - alpha) ** candidate_specifications
    independent_split_bound = alpha
    if familywise_false_pass <= alpha:
        raise AssertionError('Adaptive search should inflate the false-pass rate.')
    return {
        'pointwise_alpha': alpha,
        'candidate_specifications': candidate_specifications,
        'same_data_search_false_pass_probability': familywise_false_pass,
        'independent_selection_certification_bound': independent_split_bound,
        'inflation_factor': familywise_false_pass / alpha,
    }


def main() -> None:
    results = {
        'specification_transport': specification_transport_check(),
        'experimental_nonidentifiability': nonidentifiability_check(),
        'partial_identification': identified_set_check(),
        'uniform_finite_sample_certification': finite_sample_check(),
        'adaptive_specification_selection': selection_check(),
        'all_checks_passed': True,
    }
    OUTPUT.write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
