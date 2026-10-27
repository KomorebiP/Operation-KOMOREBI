from __future__ import annotations

from functools import lru_cache

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class QuantumCertificate:
    psi0: sp.Matrix
    psi1: sp.Matrix
    bell: sp.Matrix
    even_component: sp.Matrix
    odd_component: sp.Matrix
    path_even: sp.Matrix
    path_odd: sp.Matrix
    path_residual: sp.Matrix
    norm_residual: sp.Expr
    reduced_density: sp.Matrix
    reduced_density_residual: sp.Matrix


def kron(A: sp.Matrix, B: sp.Matrix) -> sp.Matrix:
    return sp.kronecker_product(A, B)


def partial_trace_second_qubit(rho: sp.Matrix) -> sp.Matrix:
    out = sp.zeros(2)
    for a in range(2):
        for ap in range(2):
            out[a, ap] = sum(rho[2 * a + b, 2 * ap + b] for b in range(2))
    return sp.simplify(out)


def matrix_is_zero(M: sp.Matrix) -> bool:
    return all(sp.simplify(v) == 0 for v in M)


@lru_cache(maxsize=None)
def build_certificate() -> QuantumCertificate:
    I2 = sp.eye(2)
    H = sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
    H1 = kron(H, I2)
    CNOT = sp.Matrix(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
        ]
    )
    psi0 = sp.Matrix([1, 0, 0, 0])
    psi1 = sp.simplify(H1 * psi0)
    bell = sp.simplify(CNOT * psi1)

    Pe = sp.diag(1, 0, 0, 1)
    Po = sp.diag(0, 1, 1, 0)
    even_component = Pe * bell
    odd_component = Po * bell

    path_even = sp.simplify(Pe * CNOT * Pe * H1 * Pe * psi0)
    path_odd = sp.simplify(Pe * CNOT * Po * H1 * Pe * psi0)
    path_residual = sp.simplify(path_even + path_odd - bell)

    norm_residual = sp.simplify((bell.conjugate().T * bell)[0] - 1)
    rho = sp.simplify(bell * bell.conjugate().T)
    rho_A = partial_trace_second_qubit(rho)
    reduced_density_residual = sp.simplify(rho_A - sp.eye(2) / 2)

    assert matrix_is_zero(path_residual)
    assert matrix_is_zero(odd_component)
    assert sp.simplify(norm_residual) == 0
    assert matrix_is_zero(reduced_density_residual)

    return QuantumCertificate(
        psi0=psi0,
        psi1=psi1,
        bell=bell,
        even_component=even_component,
        odd_component=odd_component,
        path_even=path_even,
        path_odd=path_odd,
        path_residual=path_residual,
        norm_residual=norm_residual,
        reduced_density=rho_A,
        reduced_density_residual=reduced_density_residual,
    )
