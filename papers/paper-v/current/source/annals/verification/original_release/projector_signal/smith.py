from __future__ import annotations

from typing import Callable, Sequence

import numpy as np

ArrayLike = np.ndarray | Sequence[complex] | complex


def gamma_from_z(z: ArrayLike) -> np.ndarray:
    z_arr = np.asarray(z, dtype=complex)
    if np.any(np.isclose(z_arr + 1.0, 0.0)):
        raise ZeroDivisionError("z=-1 is the pole of the Cayley transform")
    return (z_arr - 1.0) / (z_arr + 1.0)


def z_from_gamma(gamma: ArrayLike) -> np.ndarray:
    g_arr = np.asarray(gamma, dtype=complex)
    if np.any(np.isclose(1.0 - g_arr, 0.0)):
        raise ZeroDivisionError("Gamma=1 is the open-circuit point")
    return (1.0 + g_arr) / (1.0 - g_arr)


def admittance_from_gamma(gamma: ArrayLike) -> np.ndarray:
    g_arr = np.asarray(gamma, dtype=complex)
    if np.any(np.isclose(1.0 + g_arr, 0.0)):
        raise ZeroDivisionError("Gamma=-1 is the short-circuit point")
    return (1.0 - g_arr) / (1.0 + g_arr)


def root_of_unity(order: int, phase: int = 1) -> complex:
    if order < 1:
        raise ValueError("order must be positive")
    return np.exp(2j * np.pi * (phase % order) / order)


def rotate_gamma(gamma: ArrayLike, order: int, phase: int) -> np.ndarray:
    return root_of_unity(order, phase) * np.asarray(gamma, dtype=complex)


def phase_mobius(z: ArrayLike, order: int, phase: int) -> np.ndarray:
    w = root_of_unity(order, phase)
    z_arr = np.asarray(z, dtype=complex)
    numerator = (1 + w) * z_arr + (1 - w)
    denominator = (1 - w) * z_arr + (1 + w)
    if np.any(np.isclose(denominator, 0.0)):
        raise ZeroDivisionError("phase Mobius transform has a pole")
    return numerator / denominator


def constant_resistance_circle(r: float, samples: int = 1000) -> np.ndarray:
    angle = np.linspace(0, 2 * np.pi, samples)
    return r / (1 + r) + np.exp(1j * angle) / (1 + r)


def constant_reactance_arc(x: float, samples: int = 1200) -> np.ndarray:
    r = np.geomspace(1e-5, 1e3, samples)
    return gamma_from_z(r + 1j * x)


def smith_sensitivity(gamma: ArrayLike, epsilon: float = 0.0) -> np.ndarray:
    g = np.asarray(gamma, dtype=complex)
    return 1 / (np.abs(1 - g) ** 2 + epsilon) + 1 / (np.abs(1 + g) ** 2 + epsilon)


def project_coefficients(coefficients: Sequence[complex], order: int, phase: int) -> np.ndarray:
    coeffs = np.asarray(coefficients, dtype=complex)
    idx = np.arange(len(coeffs))
    return np.where(idx % order == phase % order, coeffs, 0.0)


def root_filter_project(
    function: Callable[[np.ndarray], np.ndarray], gamma: ArrayLike, order: int, phase: int
) -> np.ndarray:
    g = np.asarray(gamma, dtype=complex)
    total = np.zeros_like(g, dtype=complex)
    omega = root_of_unity(order)
    for k in range(order):
        total += omega ** (-phase * k) * function(omega**k * g)
    return total / order
