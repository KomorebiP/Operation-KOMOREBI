from __future__ import annotations

from functools import lru_cache

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class PhysicsCertificate:
    stiffness: sp.Matrix
    symmetric_projector: sp.Matrix
    antisymmetric_projector: sp.Matrix
    q: sp.Matrix
    v: sp.Matrix
    ode_residual: sp.Matrix
    total_energy: sp.Expr
    symmetric_energy: sp.Expr
    antisymmetric_energy: sp.Expr
    energy_partition_residual: sp.Expr


def matrix_is_zero(M: sp.Matrix) -> bool:
    return all(sp.simplify(v) == 0 for v in M)


@lru_cache(maxsize=None)
def build_certificate() -> PhysicsCertificate:
    t = sp.symbols("t", real=True)
    K = sp.Matrix([[2, -1], [-1, 2]])
    Ps = sp.Matrix([[1, 1], [1, 1]]) / 2
    Pa = sp.Matrix([[1, -1], [-1, 1]]) / 2
    q0 = sp.Matrix([1, 0])
    v0 = sp.Matrix([0, 0])

    q = sp.simplify(
        sp.cos(t) * Ps * q0
        + sp.sin(t) * Ps * v0
        + sp.cos(sp.sqrt(3) * t) * Pa * q0
        + sp.sin(sp.sqrt(3) * t) / sp.sqrt(3) * Pa * v0
    )
    v = sp.simplify(q.diff(t))
    ode_residual = sp.simplify(q.diff(t, 2) + K * q)

    total_energy = sp.simplify((v.T * v)[0] / 2 + (q.T * K * q)[0] / 2)
    qs, qa = sp.simplify(Ps * q), sp.simplify(Pa * q)
    vs, va = sp.simplify(Ps * v), sp.simplify(Pa * v)
    Es = sp.simplify((vs.T * vs)[0] / 2 + (qs.T * qs)[0] / 2)
    Ea = sp.simplify((va.T * va)[0] / 2 + 3 * (qa.T * qa)[0] / 2)
    energy_partition_residual = sp.simplify(total_energy - Es - Ea)

    assert matrix_is_zero(Ps * Ps - Ps)
    assert matrix_is_zero(Pa * Pa - Pa)
    assert matrix_is_zero(Ps * Pa)
    assert matrix_is_zero(Ps + Pa - sp.eye(2))
    assert matrix_is_zero(K - Ps - 3 * Pa)
    assert matrix_is_zero(ode_residual)
    assert sp.simplify(total_energy - 1) == 0
    assert sp.simplify(Es - sp.Rational(1, 4)) == 0
    assert sp.simplify(Ea - sp.Rational(3, 4)) == 0
    assert energy_partition_residual == 0

    return PhysicsCertificate(
        stiffness=K,
        symmetric_projector=Ps,
        antisymmetric_projector=Pa,
        q=q,
        v=v,
        ode_residual=ode_residual,
        total_energy=total_energy,
        symmetric_energy=Es,
        antisymmetric_energy=Ea,
        energy_partition_residual=energy_partition_residual,
    )
