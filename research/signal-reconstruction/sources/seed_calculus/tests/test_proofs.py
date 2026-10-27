from __future__ import annotations

import sympy as sp

from proof_atlas import arithmetic, bayes, linear, nonlinear_geometry, physics, quantum, signal


def matrix_zero(M: sp.Matrix) -> bool:
    return all(sp.simplify(sp.expand_complex(v)) == 0 for v in M)


def test_linear_certificate() -> None:
    c = linear.build_certificate()
    assert matrix_zero(c.object_residual)
    assert matrix_zero(c.operator_residual)
    assert matrix_zero(c.product_residual)
    assert matrix_zero(c.refinement_residual)


def test_signal_certificate() -> None:
    c = signal.build_certificate()
    assert matrix_zero(c.polyphase_residual)
    assert all(matrix_zero(x) for x in c.refinement_residuals)
    assert matrix_zero(c.haar_residual)
    assert matrix_zero(c.fourier_residual)
    assert matrix_zero(c.fourier_projector_residual)
    assert all(matrix_zero(x) for x in c.fourier_idempotence_residuals)


def test_quantum_certificate() -> None:
    c = quantum.build_certificate()
    assert matrix_zero(c.path_residual)
    assert matrix_zero(c.odd_component)
    assert sp.simplify(c.norm_residual) == 0
    assert matrix_zero(c.reduced_density_residual)


def test_bayes_certificate() -> None:
    c = bayes.build_certificate()
    assert matrix_zero(c.expectation_idempotence_residual)
    assert matrix_zero(c.weighted_adjoint_residual)
    assert matrix_zero(c.sufficient_residual)
    assert matrix_zero(c.factorization_residual)
    assert c.nonsufficient_exact_coarse == sp.Matrix([sp.Rational(7,29), sp.Rational(22,29)])
    assert c.nonsufficient_nominal_coarse == sp.Matrix([sp.Rational(2,9), sp.Rational(7,9)])


def test_arithmetic_certificate() -> None:
    c = arithmetic.build_certificate(12)
    assert c.sequence[:6] == (1, 2, 754, 3009008, 58105670266, 3690819041733782)
    assert all(x == 0 for x in c.recurrence_residuals)
    assert c.series_residual == 0
    assert c.hypergeometric_residual == 0
    assert all(x == 0 for x in c.composition_formula_residuals)


def test_physics_certificate() -> None:
    c = physics.build_certificate()
    assert matrix_zero(c.ode_residual)
    assert sp.simplify(c.total_energy - 1) == 0
    assert sp.simplify(c.symmetric_energy - sp.Rational(1,4)) == 0
    assert sp.simplify(c.antisymmetric_energy - sp.Rational(3,4)) == 0
    assert sp.simplify(c.energy_partition_residual) == 0


def test_nonlinear_geometry_certificate() -> None:
    c = nonlinear_geometry.build_certificate()
    assert matrix_zero(c.nonlinear_residual)
    assert matrix_zero(c.flat_holonomy_residual)
    assert sp.simplify(c.obstruction_norm_squared - sp.Rational(8,5)) == 0
