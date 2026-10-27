from __future__ import annotations

from collections.abc import Sequence
import numpy as np
from scipy.special import eval_hermitenorm, roots_hermitenorm


def weighted_conditional_expectation(
    groups: Sequence[Sequence[int]],
    probabilities: np.ndarray,
) -> np.ndarray:
    """Matrix of E[. | partition] on a finite probability space."""
    pi = np.asarray(probabilities, dtype=float)
    if np.any(pi <= 0) or abs(float(pi.sum()) - 1.0) > 1e-12:
        raise ValueError("strictly positive probability vector summing to one required")
    n = len(pi)
    p = np.zeros((n, n), dtype=float)
    seen: set[int] = set()
    for group in groups:
        mass = float(sum(pi[i] for i in group))
        if mass <= 0:
            raise ValueError("nonempty positive-mass groups required")
        for i in group:
            if i in seen:
                raise ValueError("groups must be disjoint")
            seen.add(i)
            for j in group:
                p[i, j] = pi[j] / mass
    if seen != set(range(n)):
        raise ValueError("groups must cover the space")
    return p


def weighted_inner(x: np.ndarray, y: np.ndarray, probabilities: np.ndarray) -> float:
    return float(np.asarray(x) @ (np.asarray(probabilities) * np.asarray(y)))


def martingale_differences(projectors: Sequence[np.ndarray]) -> list[np.ndarray]:
    if not projectors:
        return []
    differences = [np.asarray(projectors[0], dtype=float)]
    for j in range(1, len(projectors)):
        differences.append(np.asarray(projectors[j]) - np.asarray(projectors[j - 1]))
    return differences


def gaussian_hermite_gram(max_degree: int, quadrature_order: int = 80) -> np.ndarray:
    """Gram matrix of normalized probabilists' Hermite polynomials under N(0,1)."""
    nodes, weights = roots_hermitenorm(quadrature_order)
    weights = weights / np.sqrt(2 * np.pi)
    values = []
    import math
    for n in range(max_degree + 1):
        values.append(eval_hermitenorm(n, nodes) / np.sqrt(math.factorial(n)))
    v = np.asarray(values)
    return (v * weights) @ v.T


def ornstein_uhlenbeck_eigenvalues(max_degree: int, time: float) -> np.ndarray:
    return np.exp(-float(time) * np.arange(max_degree + 1, dtype=float))
