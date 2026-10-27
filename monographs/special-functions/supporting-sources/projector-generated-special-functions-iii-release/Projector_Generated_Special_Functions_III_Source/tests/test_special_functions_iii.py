from __future__ import annotations

import math
from pathlib import Path

import mpmath as mp
import numpy as np
from scipy.special import gamma as gamma_fn, roots_genlaguerre

import projector_generated_special_functions_iii as sf

ROOT = Path(__file__).resolve().parents[1]


def small_measure() -> sf.PacketMeasure:
    return sf.build_measure(sf.PacketParameters(a=2.0, beta=2.0, conductor=1), nmax=300_000)


def test_energy_matches_zeta_ratio_at_low_order() -> None:
    measure = small_measure()
    for k in range(5):
        exact = float(sf.exact_energy_zeta_ratio(k, dps=90))
        assert abs(measure.energy(k) - exact) < 2e-10


def test_operator_moment_identity() -> None:
    measure = small_measure()
    seed = np.sqrt(measure.w)
    for k in (0, 1, 4, 9):
        direct = float(np.dot(seed, (measure.x**k) * seed))
        assert abs(direct - measure.energy(k)) < 1e-13


def test_complete_monotonicity_finite_window() -> None:
    measure = small_measure()
    values = measure.energies(range(30))
    current = values
    for order in range(7):
        if order:
            current = np.diff(current)
        assert np.min(((-1) ** order) * current) > -1e-13


def test_hankel_positive_definite() -> None:
    measure = small_measure()
    moments = measure.energies(range(12))
    for degree in range(1, 5):
        matrix = sf.hankel_matrix(moments, degree)
        assert np.min(np.linalg.eigvalsh(matrix)) > 0


def test_selected_generalized_minors_are_positive() -> None:
    specs = [
        ((0, 1), (0, 2)),
        ((0, 2), (1, 4)),
        ((0, 1, 3), (0, 2, 4)),
    ]
    for rows, cols in specs:
        assert sf.generalized_hankel_minor(rows, cols, dps=90) > 0


def test_jacobi_nodes_and_weights() -> None:
    measure = small_measure()
    result = sf.global_lanczos(measure, 8)
    nodes, weights = sf.gauss_quadrature(result)
    assert np.all(nodes >= -1e-12)
    assert np.all(nodes < 1)
    assert np.all(weights > 0)
    assert abs(np.sum(weights) - 1) < 1e-13


def test_lanczos_moment_exactness() -> None:
    measure = small_measure()
    for steps in (2, 4, 6):
        result = sf.global_lanczos(measure, steps)
        errors = sf.moment_matching_error(measure, result, 2 * steps - 1)
        assert np.max(errors) < 2e-12


def test_reduced_resolvent_accuracy() -> None:
    measure = small_measure()
    result = sf.global_lanczos(measure, 8)
    for z in (-4.0, -1.0, -0.25, 0.5):
        assert abs(sf.exact_resolvent(measure, z) - sf.reduced_resolvent(measure, result, z)) < 2e-8


def test_resolvent_has_nonzero_imaginary_part_off_real_axis() -> None:
    measure = small_measure()
    for z in (0.4 + 0.6j, -1.2 + 0.4j, 1.1 + 0.3j):
        value = sf.exact_resolvent(measure, z)
        assert abs(value) > 1e-8
        assert abs(value.imag) > 1e-8


def test_gamma_tilt_first_moments() -> None:
    measure = small_measure()
    k = 1_000_000
    moments = sf.tilted_moments(measure, k, 3)
    target = np.array([float(mp.rf(measure.params.alpha, r)) for r in range(4)])
    relative = np.max(np.abs(moments - target) / np.maximum(1.0, target))
    assert relative < 0.02


def test_laguerre_recurrence_limit() -> None:
    measure = small_measure()
    result = sf.tilted_lanczos(measure, 10_000_000, 5)
    alpha = measure.params.alpha
    diagonal = np.array([2 * m + alpha for m in range(5)])
    off = np.array([math.sqrt((m + 1) * (m + alpha)) for m in range(4)])
    assert np.max(np.abs(result.diagonal - diagonal)) < 0.06
    assert np.max(np.abs(result.off_diagonal - off)) < 0.04


def test_monic_laguerre_coefficients() -> None:
    alpha = 1.5
    for degree in range(5):
        coeff = sf.monic_laguerre_coefficients(degree, alpha)
        assert abs(coeff[-1] - 1) < 1e-10


def test_hankel_gamma_limit() -> None:
    measure = small_measure()
    for degree in (1, 2, 3):
        ratio = sf.hankel_asymptotic_ratio(measure, 1_000_000, degree)
        assert abs(ratio - 1) < 0.08


def test_gauss_laguerre_limit() -> None:
    measure = small_measure()
    degree = 5
    result = sf.tilted_lanczos(measure, 10_000_000, degree)
    nodes, weights = sf.gauss_quadrature(result)
    target_nodes, target_weights = roots_genlaguerre(degree, measure.params.alpha - 1)
    target_weights = target_weights / gamma_fn(measure.params.alpha)
    assert np.max(np.abs(nodes - target_nodes)) < 0.05
    assert np.max(np.abs(weights - target_weights)) < 0.01


def test_energy_asymptotic_constant() -> None:
    measure = small_measure()
    k = 100_000
    ratio = measure.energy(k) / (measure.params.energy_constant * k ** (-measure.params.alpha))
    assert abs(ratio - 1) < 0.03


def test_edge_cusp_constant() -> None:
    measure = small_measure()
    z = 1 - 1e-5
    observed = (sf.exact_resolvent(measure, 1).real - sf.exact_resolvent(measure, z).real) / math.sqrt(1 - z)
    expected = 3 / (2 ** 1.5 * math.pi)
    assert abs(observed / expected - 1) < 0.04


def test_parameter_alpha_and_density() -> None:
    params = sf.PacketParameters(a=2.0, beta=2.0, conductor=5)
    assert params.alpha == 1.5
    expected = 1 / float(mp.zeta(2)) * 5 / 6
    assert abs(params.density - expected) < 1e-15


def test_required_figure_pairs_exist() -> None:
    pdfs = sorted((ROOT / "figures").glob("*.pdf"))
    pngs = sorted((ROOT / "figures").glob("*.png"))
    assert len(pdfs) == len(pngs) == 22
    assert {p.stem for p in pdfs} == {p.stem for p in pngs}


def test_result_ledger_reports_all_checks_passed() -> None:
    import json
    data = json.loads((ROOT / "results" / "results.json").read_text())
    assert data["passed"] == data["checks"] == 34
    assert data["figure_pairs"] == 22
