from __future__ import annotations

from itertools import product
from typing import Iterable, Sequence

import numpy as np

Array = np.ndarray

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H_GATE = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S_GATE = np.diag([1, 1j]).astype(complex)
T_GATE = np.diag([1, np.exp(1j * np.pi / 4)]).astype(complex)
CNOT = np.array(
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
    dtype=complex,
)


def basis_state(n_qubits: int, index: int) -> Array:
    dim = 2**n_qubits
    if not 0 <= index < dim:
        raise ValueError("basis index out of range")
    out = np.zeros(dim, dtype=complex)
    out[index] = 1.0
    return out


def normalize(v: Array) -> Array:
    v = np.asarray(v, dtype=complex)
    n = np.linalg.norm(v)
    if n == 0:
        raise ValueError("cannot normalize the zero vector")
    return v / n


def ketbra(v: Array, w: Array | None = None) -> Array:
    v = np.asarray(v, dtype=complex)
    w = v if w is None else np.asarray(w, dtype=complex)
    return np.outer(v, np.conjugate(w))


def kron_all(*operators: Array) -> Array:
    if not operators:
        return np.array([[1.0]], dtype=complex)
    out = np.asarray(operators[0], dtype=complex)
    for op in operators[1:]:
        out = np.kron(out, np.asarray(op, dtype=complex))
    return out


def embed_one_qubit(gate: Array, target: int, n_qubits: int) -> Array:
    if not 0 <= target < n_qubits:
        raise ValueError("target out of range")
    ops = [I2] * n_qubits
    ops[target] = np.asarray(gate, dtype=complex)
    return kron_all(*ops)


def embed_two_qubit_adjacent(gate: Array, left: int, n_qubits: int) -> Array:
    if gate.shape != (4, 4):
        raise ValueError("gate must be 4x4")
    if not 0 <= left < n_qubits - 1:
        raise ValueError("adjacent pair out of range")
    ops: list[Array] = []
    i = 0
    while i < n_qubits:
        if i == left:
            ops.append(np.asarray(gate, dtype=complex))
            i += 2
        else:
            ops.append(I2)
            i += 1
    return kron_all(*ops)


def packet_blocks(operator: Array, projectors: Sequence[Array]) -> list[list[Array]]:
    a = np.asarray(operator, dtype=complex)
    return [[pi @ a @ pj for pj in projectors] for pi in projectors]


def reconstruct_blocks(blocks: Sequence[Sequence[Array]]) -> Array:
    first = np.asarray(blocks[0][0], dtype=complex)
    out = np.zeros_like(first)
    for row in blocks:
        for block in row:
            out += block
    return out


def _matrix_rank(columns: list[Array], tol: float = 1e-10) -> int:
    if not columns:
        return 0
    return int(np.linalg.matrix_rank(np.column_stack(columns), tol=tol))


def cyclic_span_rank(operator: Array, seed: Array, max_power: int | None = None, tol: float = 1e-10) -> int:
    a = np.asarray(operator, dtype=complex)
    s = np.asarray(seed, dtype=complex)
    if a.shape[0] != a.shape[1] or a.shape[1] != s.size:
        raise ValueError("incompatible dimensions")
    limit = a.shape[0] if max_power is None else max_power
    columns: list[Array] = []
    v = s.copy()
    for _ in range(limit):
        columns.append(v.copy())
        v = a @ v
    return _matrix_rank(columns, tol=tol)


def reachable_span_rank(generators: Sequence[Array], seed: Array, max_depth: int = 6, tol: float = 1e-10) -> int:
    """Rank of the operator-word orbit up to a fixed depth.

    The routine closes the currently known span under every generator and stops
    early when the rank no longer grows.  It is an exact finite-dimensional
    certificate up to floating-point rank tolerance.
    """
    gens = [np.asarray(g, dtype=complex) for g in generators]
    s = np.asarray(seed, dtype=complex)
    if not gens:
        return 1 if np.linalg.norm(s) else 0
    dim = s.size
    vectors = [s.copy()]
    frontier = [s.copy()]
    rank = _matrix_rank(vectors, tol)
    for _ in range(max_depth):
        candidates = [g @ v for g in gens for v in frontier]
        new_frontier: list[Array] = []
        for v in candidates:
            test_rank = _matrix_rank(vectors + [v], tol)
            if test_rank > rank:
                vectors.append(v)
                new_frontier.append(v)
                rank = test_rank
                if rank == dim:
                    return rank
        if not new_frontier:
            break
        frontier = new_frontier
    return rank
