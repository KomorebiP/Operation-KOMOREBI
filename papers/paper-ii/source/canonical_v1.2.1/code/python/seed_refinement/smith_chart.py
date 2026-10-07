from __future__ import annotations

import cmath
from numbers import Integral
from typing import Iterable

import numpy as np


def _require_order(order: int) -> int:
    if isinstance(order, bool) or not isinstance(order, Integral) or order < 1:
        raise ValueError("order must be a positive integer")
    return int(order)


def gamma_from_impedance(z: complex) -> complex:
    if z == -1:
        raise ZeroDivisionError("z=-1 maps to the point at infinity")
    return (z - 1) / (z + 1)


def impedance_from_gamma(gamma: complex) -> complex:
    if gamma == 1:
        raise ZeroDivisionError("gamma=1 is the open-circuit point")
    return (1 + gamma) / (1 - gamma)


def phase_transform(z: complex, order: int, phase: int) -> complex:
    order = _require_order(order)
    if isinstance(phase, bool) or not isinstance(phase, Integral):
        raise ValueError("phase must be an integer")
    omega = cmath.exp(2j * cmath.pi / order)
    return impedance_from_gamma((omega**phase) * gamma_from_impedance(z))


def polyphase_orbit(radius: float, order: int) -> np.ndarray:
    order = _require_order(order)
    if not (0 <= radius < 1):
        raise ValueError("radius must lie in [0,1)")
    omega = np.exp(2j * np.pi / order)
    return np.array([impedance_from_gamma(radius * omega**k) for k in range(order)])


def smith_weight(gamma: complex) -> float:
    if gamma in (1, -1):
        return float("inf")
    return 1.0 / abs(1 - gamma) ** 2 + 1.0 / abs(1 + gamma) ** 2
