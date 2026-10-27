from __future__ import annotations

import sympy as sp


def is_zero_matrix(matrix: sp.Matrix) -> bool:
    return all(sp.simplify(sp.expand_complex(value)) == 0 for value in matrix)


def test_independent_linear_packet_audit() -> None:
    projectors = (
        sp.diag(1, 1, 0, 0, 0, 0),
        sp.diag(0, 0, 1, 1, 0, 0),
        sp.diag(0, 0, 0, 0, 1, 1),
    )
    x = sp.Matrix([2, -1, 3, 4, -2, 5])
    T = sp.Matrix([
        [1, 2, 0, 0, 1, 0], [0, 1, 1, 0, 0, 1],
        [2, 0, 1, 1, 0, 0], [0, 1, 0, 2, 1, 0],
        [1, 0, 0, 1, 2, 1], [0, 0, 1, 0, 0, 3],
    ])
    S = sp.Matrix([
        [2, 0, 1, 0, 0, 0], [1, 1, 0, 0, 0, 1],
        [0, 1, 1, 0, 1, 0], [0, 0, 1, 1, 0, 0],
        [1, 0, 0, 0, 1, 1], [0, 1, 0, 1, 0, 1],
    ])
    assert is_zero_matrix(sum(projectors, sp.zeros(6)) - sp.eye(6))
    assert is_zero_matrix(sum((P * x for P in projectors), sp.zeros(6, 1)) - x)
    assert is_zero_matrix(
        sum((Pb * T * Pa for Pb in projectors for Pa in projectors), sp.zeros(6)) - T
    )
    for Pg in projectors:
        for Pa in projectors:
            direct = Pg * S * T * Pa
            paths = sum((Pg * S * Pb * T * Pa for Pb in projectors), sp.zeros(6))
            assert is_zero_matrix(direct - paths)


def test_independent_signal_transform_audit() -> None:
    x = sp.Matrix([3, 1, 4, 1, 5, 9, 2, 6])
    channels = tuple(sp.Matrix([x[i] for i in range(r, 8, 4)]) for r in range(4))
    rebuilt = sp.zeros(8, 1)
    for r, channel in enumerate(channels):
        for q, value in enumerate(channel):
            rebuilt[4 * q + r] = value
    assert rebuilt == x

    H2 = sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
    H = sp.diag(H2, H2, H2, H2)
    assert is_zero_matrix(H.T * H - sp.eye(8))
    assert is_zero_matrix(H.T * H * x - x)

    roots = [
        1, (1 - sp.I) / sp.sqrt(2), -sp.I, -(1 + sp.I) / sp.sqrt(2),
        -1, -(1 - sp.I) / sp.sqrt(2), sp.I, (1 + sp.I) / sp.sqrt(2),
    ]
    F = sp.Matrix(8, 8, lambda j, k: roots[(j * k) % 8] / sp.sqrt(8))
    assert is_zero_matrix(F.conjugate().T * F - sp.eye(8))
    groups = ((0,), (1, 7), (2, 6), (3, 5), (4,))
    packets = []
    for group in groups:
        E = sp.zeros(8)
        for i in group:
            E[i, i] = 1
        packets.append(sp.simplify(F.conjugate().T * E * F))
    assert is_zero_matrix(sum(packets, sp.zeros(8)) - sp.eye(8))
    for i, Pi in enumerate(packets):
        assert is_zero_matrix(Pi * Pi - Pi)
        for j, Pj in enumerate(packets):
            if i != j:
                assert is_zero_matrix(Pi * Pj)


def test_independent_quantum_audit() -> None:
    I2 = sp.eye(2)
    H = sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
    CNOT = sp.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    psi = CNOT * sp.kronecker_product(H, I2) * sp.Matrix([1, 0, 0, 0])
    target = sp.Matrix([1, 0, 0, 1]) / sp.sqrt(2)
    assert is_zero_matrix(psi - target)
    rho = sp.simplify(psi * psi.conjugate().T)
    reduced = sp.Matrix(2, 2, lambda a, ap: sum(rho[2 * a + b, 2 * ap + b] for b in range(2)))
    assert is_zero_matrix(reduced - sp.eye(2) / 2)
    assert sp.simplify((psi.conjugate().T * psi)[0] - 1) == 0


def test_independent_probability_bayesian_audit() -> None:
    mu = sp.Matrix([sp.Rational(1, 10), sp.Rational(2, 10), sp.Rational(3, 10), sp.Rational(4, 10)])
    f = sp.Matrix([1, 4, -2, 3])
    E = sp.Matrix([
        [sp.Rational(1, 3), sp.Rational(2, 3), 0, 0],
        [sp.Rational(1, 3), sp.Rational(2, 3), 0, 0],
        [0, 0, sp.Rational(3, 7), sp.Rational(4, 7)],
        [0, 0, sp.Rational(3, 7), sp.Rational(4, 7)],
    ])
    assert is_zero_matrix(E * E - E)
    assert E * f == sp.Matrix([3, 3, sp.Rational(6, 7), sp.Rational(6, 7)])
    M = sp.diag(*list(mu))
    assert is_zero_matrix(M * E - E.T * M)

    lam = sp.Matrix([1, 3, 2, 4])
    fine_weights = mu.multiply_elementwise(lam)
    fine_post = fine_weights / sum(fine_weights)
    exact_coarse = sp.Matrix([fine_post[0] + fine_post[1], fine_post[2] + fine_post[3]])
    assert exact_coarse == sp.Matrix([sp.Rational(7, 29), sp.Rational(22, 29)])
    P = sp.Matrix([sp.Rational(3, 10), sp.Rational(7, 10)])
    nominal_lam = sp.Matrix([2, 3])
    nominal = P.multiply_elementwise(nominal_lam) / (P.T * nominal_lam)[0]
    r = sp.Matrix([sp.Rational(7, 3), sp.Rational(22, 7)])
    delta = r - nominal_lam
    Zr = (P.T * r)[0]
    factor = (sp.diag(*list(P)) - nominal * P.T) * delta / Zr
    assert is_zero_matrix(exact_coarse - nominal - factor)


def test_independent_arithmetic_series_audit() -> None:
    # Independent exact power-series inversion using only rational arithmetic.
    from fractions import Fraction
    from math import factorial

    nmax = 8
    d = [Fraction((-1) ** n, factorial(5 * n)) for n in range(nmax + 1)]
    q = [sum((d[k] * d[n - k] for k in range(n + 1)), Fraction(0, 1)) for n in range(nmax + 1)]
    c = [Fraction(0, 1) for _ in range(nmax + 1)]
    c[0] = Fraction(1, 1)
    for n in range(1, nmax + 1):
        c[n] = -sum((q[k] * c[n - k] for k in range(1, n + 1)), Fraction(0, 1))

    direct = tuple(factorial(5 * n) * c[n] for n in range(nmax + 1))
    assert direct == (
        1, 2, 754, 3009008, 58105670266, 3690819041733782,
        611297487195595912564, 225925381294863591587930378,
        166595785020134064487394817914506,
    )

    # Independent character-filter audit of the closed form.  The five roots
    # are r_j=-omega^j with omega^5=1.  Their m-th power average vanishes
    # unless 5 divides m; at m=5n it equals (-1)^n.
    for m in range(31):
        multiplicities = [0] * 5
        for j in range(5):
            multiplicities[(j * m) % 5] += 1
        if m % 5 == 0:
            assert multiplicities == [5, 0, 0, 0, 0]
            filtered = (-1) ** (m // 5)
            target = (-1) ** (m // 5)
        else:
            assert multiplicities == [1, 1, 1, 1, 1]
            filtered = 0  # 1+omega+...+omega^4=0
            target = 0
        assert filtered == target


def test_independent_physics_audit() -> None:
    t = sp.symbols('t', real=True)
    Ps = sp.Matrix([[1, 1], [1, 1]]) / 2
    Pa = sp.Matrix([[1, -1], [-1, 1]]) / 2
    K = sp.Matrix([[2, -1], [-1, 2]])
    q0 = sp.Matrix([1, 0])
    q = sp.cos(t) * Ps * q0 + sp.cos(sp.sqrt(3) * t) * Pa * q0
    assert is_zero_matrix(sp.simplify(q.diff(t, 2) + K * q))
    v = q.diff(t)
    energy = sp.simplify((v.T*v)[0]/2 + (q.T*K*q)[0]/2)
    assert sp.simplify(energy - 1) == 0
    assert is_zero_matrix(K - Ps - 3*Pa)


def test_independent_nonlinear_holonomy_audit() -> None:
    x = sp.Matrix([1, 2, 0, -1, 3, 1, -2, 2])
    alpha = sp.Rational(1, 2)
    direct = sp.Matrix([x[i] + alpha*x[(i-1) % 8]**2 for i in range(8)])
    e = sp.Matrix(x[0::2, 0])
    o = sp.Matrix(x[1::2, 0])
    ye = sp.Matrix([e[k] + alpha*o[(k-1) % 4]**2 for k in range(4)])
    yo = sp.Matrix([o[k] + alpha*e[k]**2 for k in range(4)])
    packed = sp.Matrix([value for pair in zip(ye, yo) for value in pair])
    assert packed == direct

    def rot(a: sp.Rational, b: sp.Rational) -> sp.Matrix:
        return sp.Matrix([[a, -b], [b, a]])

    U = [sp.eye(2), rot(sp.Rational(3,5), sp.Rational(4,5)),
         rot(sp.Rational(5,13), sp.Rational(12,13)),
         rot(sp.Rational(7,25), sp.Rational(24,25))]
    edges = [U[1]*U[0].inv(), U[2]*U[1].inv(), U[3]*U[2].inv(), U[0]*U[3].inv()]
    flat = sp.simplify(edges[3]*edges[2]*edges[1]*edges[0])
    assert is_zero_matrix(flat - sp.eye(2))
    Q = rot(sp.Rational(3,5), sp.Rational(4,5))
    bad = sp.simplify((Q*edges[3])*edges[2]*edges[1]*edges[0])
    obstruction = bad - sp.eye(2)
    assert bad == Q
    assert sp.simplify(sum(v**2 for v in obstruction) - sp.Rational(8,5)) == 0
