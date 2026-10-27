from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from . import arithmetic, bayes, linear, nonlinear_geometry, physics, quantum, signal


@dataclass(frozen=True)
class DetailedCertificate:
    linear_contributions: tuple[tuple[sp.Matrix, ...], ...]
    linear_row_residuals: tuple[sp.Matrix, ...]
    fourier_band_packets: tuple[sp.Matrix, ...]
    fourier_band_residual: sp.Matrix
    quantum_path_table: tuple[tuple[str, sp.Matrix], ...]
    quantum_measurement_probabilities: tuple[sp.Expr, ...]
    bayes_witness_coarse_prior: sp.Matrix
    bayes_witness_posterior_1: sp.Matrix
    bayes_witness_posterior_2: sp.Matrix
    bayes_witness_difference: sp.Matrix
    recurrence_contributions: tuple[tuple[sp.Integer, sp.Integer, sp.Integer], ...]
    mode_shapes: tuple[sp.Matrix, sp.Matrix]
    nonlinear_even: sp.Matrix
    nonlinear_odd: sp.Matrix
    nonlinear_even_output: sp.Matrix
    nonlinear_odd_output: sp.Matrix
    holonomy_edges: tuple[sp.Matrix, ...]


def _coarsen(v: sp.Matrix) -> sp.Matrix:
    return sp.Matrix([v[0] + v[1], v[2] + v[3]])


def _bayes(prior: sp.Matrix, likelihood: sp.Matrix) -> sp.Matrix:
    w = prior.multiply_elementwise(likelihood)
    return sp.simplify(w / sum(w))


def build_detailed_certificate() -> DetailedCertificate:
    lc = linear.build_certificate()
    signal_x = sp.Matrix([3, 1, 4, 1, 5, 9, 2, 6])
    F = signal.dft8_matrix()
    fourier_coefficients = signal.matrix_simplify(F * signal_x)
    qc = quantum.build_certificate()
    ac = arithmetic.build_certificate(6)
    pc = physics.build_certificate()
    ng = nonlinear_geometry.build_certificate()

    linear_contributions = tuple(
        tuple(sp.simplify(lc.blocks[b][a] * lc.x) for a in range(3))
        for b in range(3)
    )
    Tx = sp.simplify(lc.operator * lc.x)
    linear_row_residuals = tuple(
        sp.simplify(sum(linear_contributions[b], sp.zeros(6, 1)) - lc.projectors[b] * Tx)
        for b in range(3)
    )

    groups = ((0,), (1, 7), (2, 6), (3, 5), (4,))
    band_packets = []
    for group in groups:
        selected = sp.zeros(8, 1)
        for k in group:
            selected[k] = fourier_coefficients[k]
        band_packets.append(signal.matrix_simplify(F.conjugate().T * selected))
    fourier_band_packets = tuple(band_packets)
    fourier_band_residual = signal.matrix_simplify(sum(fourier_band_packets, sp.zeros(8, 1)) - signal_x)

    I2 = sp.eye(2)
    H = sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
    H1 = sp.kronecker_product(H, I2)
    CNOT = sp.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    Pe = sp.diag(1, 0, 0, 1)
    Po = sp.diag(0, 1, 1, 0)
    psi0 = sp.Matrix([1, 0, 0, 0])
    path_table = (
        ("e->e", sp.simplify(Pe * CNOT * Pe * H1 * Pe * psi0)),
        ("o->e", sp.simplify(Pe * CNOT * Po * H1 * Pe * psi0)),
        ("e->o", sp.simplify(Po * CNOT * Pe * H1 * Pe * psi0)),
        ("o->o", sp.simplify(Po * CNOT * Po * H1 * Pe * psi0)),
    )
    probs = tuple(sp.simplify(sp.conjugate(qc.bell[i]) * qc.bell[i]) for i in range(4))

    lam = sp.Matrix([1, 3, 2, 4])
    p1 = sp.Matrix([sp.Rational(1, 10), sp.Rational(2, 10), sp.Rational(3, 10), sp.Rational(4, 10)])
    p2 = sp.Matrix([sp.Rational(2, 10), sp.Rational(1, 10), sp.Rational(4, 10), sp.Rational(3, 10)])
    coarse_prior = _coarsen(p1)
    assert coarse_prior == _coarsen(p2)
    post1 = _coarsen(_bayes(p1, lam))
    post2 = _coarsen(_bayes(p2, lam))
    post_diff = sp.simplify(post1 - post2)

    recurrence_contributions: list[tuple[sp.Integer, sp.Integer, sp.Integer]] = []
    seq = ac.sequence
    for n in range(1, 5):
        term_a = -sum(
            (-1) ** k * sp.binomial(5 * n - 1, 5 * k) * seq[n - k]
            for k in range(1, n)
        )
        term_b = -2 * sum(
            (-1) ** k * sp.binomial(5 * n - 1, 5 * k - 1) * seq[n - k]
            for k in range(1, n + 1)
        )
        recurrence_contributions.append((sp.Integer(term_a), sp.Integer(term_b), sp.Integer(seq[n])))
        assert sp.simplify(term_a + term_b - seq[n]) == 0

    es = sp.Matrix([1, 1]) / sp.sqrt(2)
    ea = sp.Matrix([1, -1]) / sp.sqrt(2)
    assert sp.simplify(pc.stiffness * es - es) == sp.zeros(2, 1)
    assert sp.simplify(pc.stiffness * ea - 3 * ea) == sp.zeros(2, 1)

    e = sp.Matrix([ng.signal[i] for i in range(0, ng.signal.rows, 2)])
    o = sp.Matrix([ng.signal[i] for i in range(1, ng.signal.rows, 2)])
    alpha = sp.Rational(1, 2)
    ye = sp.Matrix([e[k] + alpha * o[(k - 1) % e.rows] ** 2 for k in range(e.rows)])
    yo = sp.Matrix([o[k] + alpha * e[k] ** 2 for k in range(e.rows)])

    U = [
        sp.eye(2),
        nonlinear_geometry.rotation(sp.Rational(3, 5), sp.Rational(4, 5)),
        nonlinear_geometry.rotation(sp.Rational(5, 13), sp.Rational(12, 13)),
        nonlinear_geometry.rotation(sp.Rational(7, 25), sp.Rational(24, 25)),
    ]
    edges = (
        sp.simplify(U[1] * U[0].inv()),
        sp.simplify(U[2] * U[1].inv()),
        sp.simplify(U[3] * U[2].inv()),
        sp.simplify(U[0] * U[3].inv()),
    )
    assert sp.simplify(edges[3] * edges[2] * edges[1] * edges[0] - sp.eye(2)) == sp.zeros(2)

    assert all(all(sp.simplify(v) == 0 for v in r) for r in linear_row_residuals)
    assert all(sp.simplify(v) == 0 for v in fourier_band_residual)
    assert path_table[2][1] == sp.zeros(4, 1)
    assert path_table[3][1] == sp.zeros(4, 1)
    assert probs == (sp.Rational(1, 2), 0, 0, sp.Rational(1, 2))
    assert post_diff == sp.Matrix([sp.Rational(6, 145), -sp.Rational(6, 145)])
    assert sp.Matrix([v for pair in zip(ye, yo) for v in pair]) == ng.direct_output

    return DetailedCertificate(
        linear_contributions=linear_contributions,
        linear_row_residuals=linear_row_residuals,
        fourier_band_packets=fourier_band_packets,
        fourier_band_residual=fourier_band_residual,
        quantum_path_table=path_table,
        quantum_measurement_probabilities=probs,
        bayes_witness_coarse_prior=coarse_prior,
        bayes_witness_posterior_1=post1,
        bayes_witness_posterior_2=post2,
        bayes_witness_difference=post_diff,
        recurrence_contributions=tuple(recurrence_contributions),
        mode_shapes=(es, ea),
        nonlinear_even=e,
        nonlinear_odd=o,
        nonlinear_even_output=ye,
        nonlinear_odd_output=yo,
        holonomy_edges=edges,
    )
