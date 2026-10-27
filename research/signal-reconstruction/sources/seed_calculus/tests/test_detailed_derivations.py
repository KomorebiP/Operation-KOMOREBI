from __future__ import annotations

import sympy as sp
from functools import lru_cache
import gc

from proof_atlas import details


def zero_matrix(M: sp.Matrix) -> bool:
    return all(sp.simplify(sp.expand_complex(v)) == 0 for v in M)


@lru_cache(maxsize=1)
def get_certificate():
    return details.build_detailed_certificate()


def test_linear_contribution_rows_reconstruct_output_packets() -> None:
    c = get_certificate()
    assert all(zero_matrix(r) for r in c.linear_row_residuals)


def test_fourier_band_signals_reconstruct_original_signal() -> None:
    c = get_certificate()
    assert zero_matrix(c.fourier_band_residual)


def test_quantum_all_parity_paths_are_accounted_for() -> None:
    c = get_certificate()
    assert c.quantum_path_table[0][1] == sp.Matrix([sp.sqrt(2)/2, 0, 0, 0])
    assert c.quantum_path_table[1][1] == sp.Matrix([0, 0, 0, sp.sqrt(2)/2])
    assert c.quantum_path_table[2][1] == sp.zeros(4, 1)
    assert c.quantum_path_table[3][1] == sp.zeros(4, 1)
    assert c.quantum_measurement_probabilities == (sp.Rational(1,2), 0, 0, sp.Rational(1,2))


def test_bayesian_same_coarse_prior_can_have_different_coarse_posterior() -> None:
    c = get_certificate()
    assert c.bayes_witness_coarse_prior == sp.Matrix([sp.Rational(3,10), sp.Rational(7,10)])
    assert c.bayes_witness_posterior_1 == sp.Matrix([sp.Rational(7,29), sp.Rational(22,29)])
    assert c.bayes_witness_posterior_2 == sp.Matrix([sp.Rational(1,5), sp.Rational(4,5)])
    assert c.bayes_witness_difference == sp.Matrix([sp.Rational(6,145), -sp.Rational(6,145)])


def test_arithmetic_recurrence_contributions_sum_exactly() -> None:
    c = get_certificate()
    expected = (
        (0, 2, 2),
        (252, 502, 754),
        (1507506, 1501502, 3009008),
        (34919099764, 23186570502, 58105670266),
    )
    assert c.recurrence_contributions == expected


def test_physics_mode_shapes_are_normalized_and_orthogonal() -> None:
    c = get_certificate()
    es, ea = c.mode_shapes
    assert sp.simplify((es.T*es)[0]-1) == 0
    assert sp.simplify((ea.T*ea)[0]-1) == 0
    assert sp.simplify((es.T*ea)[0]) == 0


def test_nonlinear_channels_and_holonomy_edges() -> None:
    c = get_certificate()
    assert c.nonlinear_even == sp.Matrix([1,0,3,-2])
    assert c.nonlinear_odd == sp.Matrix([2,-1,1,2])
    assert c.nonlinear_even_output == sp.Matrix([3,2,sp.Rational(7,2),-sp.Rational(3,2)])
    assert c.nonlinear_odd_output == sp.Matrix([sp.Rational(5,2),-1,sp.Rational(11,2),4])
    product = c.holonomy_edges[3]*c.holonomy_edges[2]*c.holonomy_edges[1]*c.holonomy_edges[0]
    assert zero_matrix(sp.simplify(product-sp.eye(2)))


def teardown_module() -> None:
    get_certificate.cache_clear()
    sp.core.cache.clear_cache()
    gc.collect()
