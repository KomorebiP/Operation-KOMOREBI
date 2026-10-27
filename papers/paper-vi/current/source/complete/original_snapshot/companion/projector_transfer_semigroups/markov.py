from __future__ import annotations

from math import comb
from collections.abc import Sequence
import numpy as np
from scipy.linalg import expm


def symmetric_random_walk(steps: int) -> tuple[np.ndarray, np.ndarray]:
    """Positions and probabilities after `steps` fair +/-1 increments."""
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    positions = np.arange(-steps, steps + 1, 2, dtype=int)
    probabilities = np.array([comb(steps, (steps + int(k)) // 2) / 2**steps for k in positions], dtype=float)
    return positions, probabilities


def evolve_markov(kernel: np.ndarray, initial: np.ndarray, steps: int) -> np.ndarray:
    k = np.asarray(kernel, dtype=float)
    p = np.asarray(initial, dtype=float)
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    return np.linalg.matrix_power(k, steps) @ p


def exact_lumped_chain() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return a column-stochastic fine chain K, coarsener C, and exact lumped chain Kbar."""
    k = np.array(
        [
            [0.50, 0.10, 0.15, 0.05],
            [0.20, 0.60, 0.05, 0.15],
            [0.20, 0.05, 0.50, 0.20],
            [0.10, 0.25, 0.30, 0.60],
        ],
        dtype=float,
    )
    c = np.array([[1, 1, 0, 0], [0, 0, 1, 1]], dtype=float)
    kbar = np.array([[0.70, 0.20], [0.30, 0.80]], dtype=float)
    return k, c, kbar


def lumping_defect(kernel: np.ndarray, coarsener: np.ndarray, coarse_kernel: np.ndarray) -> np.ndarray:
    return coarsener @ kernel - coarse_kernel @ coarsener


def finite_horizon_lumping_error(
    kernel: np.ndarray,
    coarsener: np.ndarray,
    coarse_kernel: np.ndarray,
    steps: int,
) -> np.ndarray:
    return coarsener @ np.linalg.matrix_power(kernel, steps) - np.linalg.matrix_power(coarse_kernel, steps) @ coarsener


def survival_curve(generator: np.ndarray, initial: np.ndarray, times: Sequence[float]) -> dict[str, np.ndarray]:
    """Transient-state survival, density, and hazard for dp/dt=A p."""
    a = np.asarray(generator, dtype=float)
    p0 = np.asarray(initial, dtype=float)
    ones = np.ones(a.shape[0])
    survival: list[float] = []
    density: list[float] = []
    hazard: list[float] = []
    absorption_rates = -ones @ a
    for t in times:
        p = expm(float(t) * a) @ p0
        s = float(ones @ p)
        f = float(absorption_rates @ p)
        survival.append(s)
        density.append(f)
        hazard.append(f / s if s > 0 else np.nan)
    return {
        "time": np.asarray(times, dtype=float),
        "survival": np.asarray(survival),
        "density": np.asarray(density),
        "hazard": np.asarray(hazard),
    }
