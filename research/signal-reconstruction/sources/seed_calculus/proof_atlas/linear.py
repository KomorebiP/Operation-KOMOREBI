from __future__ import annotations

from functools import lru_cache

from dataclasses import dataclass
from typing import Iterable

import sympy as sp


@dataclass(frozen=True)
class LinearCertificate:
    x: sp.Matrix
    operator: sp.Matrix
    projectors: tuple[sp.Matrix, ...]
    packets: tuple[sp.Matrix, ...]
    blocks: tuple[tuple[sp.Matrix, ...], ...]
    object_residual: sp.Matrix
    operator_residual: sp.Matrix
    product_residual: sp.Matrix
    refinement_residual: sp.Matrix


def coordinate_projectors(block_sizes: Iterable[int]) -> tuple[sp.Matrix, ...]:
    sizes = tuple(int(s) for s in block_sizes)
    if not sizes or any(s <= 0 for s in sizes):
        raise ValueError("block sizes must be positive")
    n = sum(sizes)
    out: list[sp.Matrix] = []
    start = 0
    for size in sizes:
        P = sp.zeros(n)
        for i in range(start, start + size):
            P[i, i] = 1
        out.append(P)
        start += size
    return tuple(out)


def transfer_blocks(T: sp.Matrix, projectors: tuple[sp.Matrix, ...]) -> tuple[tuple[sp.Matrix, ...], ...]:
    return tuple(
        tuple(Pb * T * Pa for Pa in projectors)
        for Pb in projectors
    )


def reconstruct_operator(blocks: tuple[tuple[sp.Matrix, ...], ...]) -> sp.Matrix:
    if not blocks or not blocks[0]:
        raise ValueError("blocks cannot be empty")
    n = blocks[0][0].rows
    return sum((B for row in blocks for B in row), sp.zeros(n))


def matrix_is_zero(M: sp.Matrix) -> bool:
    return all(sp.simplify(v) == 0 for v in M)


@lru_cache(maxsize=None)
def build_certificate() -> LinearCertificate:
    P = coordinate_projectors((2, 2, 2))
    x = sp.Matrix([2, -1, 3, 4, -2, 5])
    T = sp.Matrix(
        [
            [1, 2, 0, 0, 1, 0],
            [0, 1, 1, 0, 0, 1],
            [2, 0, 1, 1, 0, 0],
            [0, 1, 0, 2, 1, 0],
            [1, 0, 0, 1, 2, 1],
            [0, 0, 1, 0, 0, 3],
        ]
    )
    S = sp.Matrix(
        [
            [2, 0, 1, 0, 0, 0],
            [1, 1, 0, 0, 0, 1],
            [0, 1, 1, 0, 1, 0],
            [0, 0, 1, 1, 0, 0],
            [1, 0, 0, 0, 1, 1],
            [0, 1, 0, 1, 0, 1],
        ]
    )

    packets = tuple(Pa * x for Pa in P)
    object_residual = sum(packets, sp.zeros(6, 1)) - x

    blocks_T = transfer_blocks(T, P)
    operator_residual = reconstruct_operator(blocks_T) - T

    blocks_S = transfer_blocks(S, P)
    blocks_ST = transfer_blocks(S * T, P)
    product_rebuilt = tuple(
        tuple(
            sum((blocks_S[g][b] * blocks_T[b][a] for b in range(len(P))), sp.zeros(6))
            for a in range(len(P))
        )
        for g in range(len(P))
    )
    # Preserve every block residual separately in one block matrix.  A plain
    # sum could conceal cancellation between distinct packet paths.
    difference_rows = tuple(
        tuple(blocks_ST[g][a] - product_rebuilt[g][a] for a in range(len(P)))
        for g in range(len(P))
    )
    product_residual = sp.Matrix.vstack(
        *(sp.Matrix.hstack(*row) for row in difference_rows)
    )

    # Refine the first 2D packet into its two coordinate children.
    Q0 = sp.diag(1, 0, 0, 0, 0, 0)
    Q1 = sp.diag(0, 1, 0, 0, 0, 0)
    refinement_residual = P[0] - Q0 - Q1

    assert matrix_is_zero(object_residual)
    assert matrix_is_zero(operator_residual)
    assert matrix_is_zero(product_residual)
    assert matrix_is_zero(refinement_residual)

    return LinearCertificate(
        x=x,
        operator=T,
        projectors=P,
        packets=packets,
        blocks=blocks_T,
        object_residual=object_residual,
        operator_residual=operator_residual,
        product_residual=product_residual,
        refinement_residual=refinement_residual,
    )
