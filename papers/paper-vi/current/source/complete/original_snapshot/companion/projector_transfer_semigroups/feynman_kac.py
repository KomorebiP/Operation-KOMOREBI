from __future__ import annotations

from itertools import product
import numpy as np


def discrete_feynman_kac(
    transition: np.ndarray,
    potential: np.ndarray,
    terminal: np.ndarray,
    steps: int,
) -> np.ndarray:
    """Backward finite-state Feynman-Kac operator.

    K[j,i]=P(X_{r+1}=j | X_r=i), and the current-state weight is exp(-V(i)).
    """
    k = np.asarray(transition, dtype=float)
    v = np.asarray(potential, dtype=float)
    f = np.asarray(terminal, dtype=float)
    transfer = np.diag(np.exp(-v)) @ k.T
    return np.linalg.matrix_power(transfer, steps) @ f


def enumerate_feynman_kac(
    transition: np.ndarray,
    potential: np.ndarray,
    terminal: np.ndarray,
    steps: int,
) -> np.ndarray:
    k = np.asarray(transition, dtype=float)
    v = np.asarray(potential, dtype=float)
    f = np.asarray(terminal, dtype=float)
    n = k.shape[0]
    result = np.zeros(n, dtype=float)
    if steps == 0:
        return f.copy()
    for start in range(n):
        total = 0.0
        for tail in product(range(n), repeat=steps):
            path = (start,) + tail
            probability = 1.0
            weight = 1.0
            for r in range(steps):
                current = path[r]
                nxt = path[r + 1]
                probability *= k[nxt, current]
                weight *= np.exp(-v[current])
            total += probability * weight * f[path[-1]]
        result[start] = total
    return result
