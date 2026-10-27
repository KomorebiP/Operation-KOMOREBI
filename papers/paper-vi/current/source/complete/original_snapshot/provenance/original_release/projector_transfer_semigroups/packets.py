from __future__ import annotations

from collections.abc import Sequence
import numpy as np


def coordinate_projectors(groups: Sequence[Sequence[int]], dimension: int) -> list[np.ndarray]:
    """Orthogonal coordinate projectors associated with a disjoint partition."""
    seen: set[int] = set()
    projectors: list[np.ndarray] = []
    for group in groups:
        p = np.zeros((dimension, dimension), dtype=float)
        for i in group:
            if not 0 <= i < dimension:
                raise ValueError("packet index out of range")
            if i in seen:
                raise ValueError("groups must be disjoint")
            seen.add(i)
            p[i, i] = 1.0
        projectors.append(p)
    if seen != set(range(dimension)):
        raise ValueError("groups must cover every coordinate")
    return projectors


def validate_projectors(projectors: Sequence[np.ndarray], tol: float = 1e-12) -> bool:
    if not projectors:
        return False
    n = projectors[0].shape[0]
    total = np.zeros((n, n), dtype=complex)
    for i, p in enumerate(projectors):
        if p.shape != (n, n):
            return False
        if np.linalg.norm(p @ p - p) > tol:
            return False
        total += p
        for j, q in enumerate(projectors):
            if i != j and np.linalg.norm(p @ q) > tol:
                return False
    return np.linalg.norm(total - np.eye(n)) <= tol


def packet_blocks(operator: np.ndarray, projectors: Sequence[np.ndarray]) -> list[list[np.ndarray]]:
    """Return blocks B[beta][alpha] = P_beta A P_alpha."""
    return [[pb @ operator @ pa for pa in projectors] for pb in projectors]


def reconstruct_from_blocks(blocks: Sequence[Sequence[np.ndarray]]) -> np.ndarray:
    if not blocks or not blocks[0]:
        raise ValueError("nonempty block matrix required")
    out = np.zeros_like(np.asarray(blocks[0][0]), dtype=complex)
    for row in blocks:
        for block in row:
            out = out + block
    return out


def block_composition(
    left: Sequence[Sequence[np.ndarray]],
    right: Sequence[Sequence[np.ndarray]],
) -> list[list[np.ndarray]]:
    """Matrix multiplication in packet-block coordinates."""
    n = len(left)
    if n == 0 or len(right) != n:
        raise ValueError("square block systems required")
    result: list[list[np.ndarray]] = []
    for beta in range(n):
        row: list[np.ndarray] = []
        for alpha in range(n):
            value = np.zeros_like(np.asarray(left[beta][0]), dtype=complex)
            for gamma in range(n):
                value = value + left[beta][gamma] @ right[gamma][alpha]
            row.append(value)
        result.append(row)
    return result
