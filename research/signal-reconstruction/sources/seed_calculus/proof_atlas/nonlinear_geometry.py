from __future__ import annotations

from functools import lru_cache

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class NonlinearGeometryCertificate:
    signal: sp.Matrix
    direct_output: sp.Matrix
    packet_output: sp.Matrix
    nonlinear_residual: sp.Matrix
    flat_holonomy: sp.Matrix
    flat_holonomy_residual: sp.Matrix
    perturbed_holonomy: sp.Matrix
    obstruction_matrix: sp.Matrix
    obstruction_norm_squared: sp.Expr


def nonlinear_filter(x: sp.Matrix, alpha: sp.Rational) -> sp.Matrix:
    n = x.rows
    return sp.Matrix([x[i] + alpha * x[(i - 1) % n] ** 2 for i in range(n)])


def packet_nonlinear_filter(x: sp.Matrix, alpha: sp.Rational) -> sp.Matrix:
    e = sp.Matrix([x[i] for i in range(0, x.rows, 2)])
    o = sp.Matrix([x[i] for i in range(1, x.rows, 2)])
    m = e.rows
    ye = sp.Matrix([e[k] + alpha * o[(k - 1) % m] ** 2 for k in range(m)])
    yo = sp.Matrix([o[k] + alpha * e[k] ** 2 for k in range(m)])
    out = sp.zeros(x.rows, 1)
    for k in range(m):
        out[2 * k] = ye[k]
        out[2 * k + 1] = yo[k]
    return out


def rotation(a: sp.Rational, b: sp.Rational) -> sp.Matrix:
    if sp.simplify(a * a + b * b - 1) != 0:
        raise ValueError("a^2+b^2 must equal 1")
    return sp.Matrix([[a, -b], [b, a]])


def matrix_is_zero(M: sp.Matrix) -> bool:
    return all(sp.simplify(v) == 0 for v in M)


@lru_cache(maxsize=None)
def build_certificate() -> NonlinearGeometryCertificate:
    x = sp.Matrix([1, 2, 0, -1, 3, 1, -2, 2])
    alpha = sp.Rational(1, 2)
    direct = nonlinear_filter(x, alpha)
    packet = packet_nonlinear_filter(x, alpha)
    nonlinear_residual = sp.simplify(packet - direct)

    U = [
        sp.eye(2),
        rotation(sp.Rational(3, 5), sp.Rational(4, 5)),
        rotation(sp.Rational(5, 13), sp.Rational(12, 13)),
        rotation(sp.Rational(7, 25), sp.Rational(24, 25)),
    ]
    # Directed cycle 0->1->2->3->0. A-edges are identity; B_{v,u}=U_v U_u^{-1}.
    B10 = sp.simplify(U[1] * U[0].inv())
    B21 = sp.simplify(U[2] * U[1].inv())
    B32 = sp.simplify(U[3] * U[2].inv())
    B03 = sp.simplify(U[0] * U[3].inv())
    flat_holonomy = sp.simplify(B03 * B32 * B21 * B10)
    flat_residual = sp.simplify(flat_holonomy - sp.eye(2))

    Q = rotation(sp.Rational(3, 5), sp.Rational(4, 5))
    B03_bad = sp.simplify(Q * B03)
    bad_holonomy = sp.simplify(B03_bad * B32 * B21 * B10)
    obstruction = sp.simplify(bad_holonomy - sp.eye(2))
    obstruction_norm_squared = sp.simplify(sum(v * v for v in obstruction))

    assert matrix_is_zero(nonlinear_residual)
    assert matrix_is_zero(flat_residual)
    assert bad_holonomy == Q
    assert obstruction_norm_squared == sp.Rational(8, 5)

    return NonlinearGeometryCertificate(
        signal=x,
        direct_output=direct,
        packet_output=packet,
        nonlinear_residual=nonlinear_residual,
        flat_holonomy=flat_holonomy,
        flat_holonomy_residual=flat_residual,
        perturbed_holonomy=bad_holonomy,
        obstruction_matrix=obstruction,
        obstruction_norm_squared=obstruction_norm_squared,
    )
