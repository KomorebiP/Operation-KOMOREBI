from __future__ import annotations

import numpy as np


def dirichlet_laplacian_1d(interior_points: int) -> tuple[np.ndarray, np.ndarray, float]:
    if interior_points < 1:
        raise ValueError("at least one interior point required")
    n = interior_points
    h = 1.0 / (n + 1)
    lap = (2.0 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)) / h**2
    grid = np.arange(1, n + 1, dtype=float) * h
    return lap, grid, h


def continuous_dirichlet_green(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    xx = np.asarray(x, dtype=float)[:, None]
    yy = np.asarray(y, dtype=float)[None, :]
    return np.minimum(xx, yy) - xx * yy


def discrete_green_scaled(interior_points: int) -> tuple[np.ndarray, np.ndarray, float]:
    lap, grid, h = dirichlet_laplacian_1d(interior_points)
    return np.linalg.inv(lap) / h, grid, h


def low_mode_eigenvalue_error(interior_points: int, mode: int) -> float:
    if not 1 <= mode <= interior_points:
        raise ValueError("valid mode required")
    h = 1.0 / (interior_points + 1)
    discrete = 4.0 / h**2 * np.sin(mode * np.pi * h / 2.0) ** 2
    exact = (mode * np.pi) ** 2
    return abs(discrete - exact)
