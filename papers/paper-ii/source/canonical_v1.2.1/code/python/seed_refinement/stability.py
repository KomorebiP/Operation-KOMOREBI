from __future__ import annotations

from numbers import Integral
from typing import Tuple

import numpy as np


def _validate_tower_shapes(
    coarsen: np.ndarray,
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    C = np.asarray(coarsen)
    T_f = np.asarray(fine_operator)
    T_c = np.asarray(coarse_operator)
    if C.ndim != 2 or T_f.ndim != 2 or T_c.ndim != 2:
        raise ValueError("coarsen and both operators must be matrices")
    coarse_size, fine_size = C.shape
    if T_f.shape != (fine_size, fine_size):
        raise ValueError("fine_operator shape must match the fine dimension of coarsen")
    if T_c.shape != (coarse_size, coarse_size):
        raise ValueError("coarse_operator shape must match the coarse dimension of coarsen")
    return C, T_f, T_c


def _require_power(power: int) -> int:
    if isinstance(power, bool) or not isinstance(power, Integral) or power < 1:
        raise ValueError("power must be a positive integer")
    return int(power)


def power_defect(coarsen: np.ndarray, fine_operator: np.ndarray, coarse_operator: np.ndarray) -> np.ndarray:
    C, T_f, T_c = _validate_tower_shapes(coarsen, fine_operator, coarse_operator)
    return C @ T_f - T_c @ C


def power_defect_expansion(
    coarsen: np.ndarray,
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
    power: int,
) -> np.ndarray:
    power = _require_power(power)
    coarsen, fine_operator, coarse_operator = _validate_tower_shapes(
        coarsen, fine_operator, coarse_operator
    )
    defect = power_defect(coarsen, fine_operator, coarse_operator)
    out = np.zeros((coarse_operator.shape[0], fine_operator.shape[0]), dtype=np.result_type(coarsen, fine_operator, coarse_operator))
    for k in range(power):
        out += np.linalg.matrix_power(coarse_operator, power - 1 - k) @ defect @ np.linalg.matrix_power(fine_operator, k)
    return out


def resolvent_defect(
    coarsen: np.ndarray,
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
    spectral_parameter: complex,
) -> tuple[np.ndarray, np.ndarray]:
    coarsen, fine_operator, coarse_operator = _validate_tower_shapes(
        coarsen, fine_operator, coarse_operator
    )
    fine_resolvent = np.linalg.inv(spectral_parameter * np.eye(fine_operator.shape[0]) - fine_operator)
    coarse_resolvent = np.linalg.inv(spectral_parameter * np.eye(coarse_operator.shape[0]) - coarse_operator)
    lhs = coarsen @ fine_resolvent - coarse_resolvent @ coarsen
    rhs = coarse_resolvent @ power_defect(coarsen, fine_operator, coarse_operator) @ fine_resolvent
    return lhs, rhs


def compatible_replication_tower(coarse_values: np.ndarray, children: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Create E,C,T_f,T_c with C E=I and C T_f=T_c C.

    Each coarse coordinate is repeated across `children` fine coordinates.  E is
    replication and C is averaging.  T_f repeats the coarse diagonal value on each
    child packet.
    """
    raw_values = np.asarray(coarse_values)
    if raw_values.ndim != 1 or raw_values.size == 0:
        raise ValueError("coarse_values must be a nonempty one-dimensional array")
    values = np.asarray(coarse_values, dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("coarse_values must be finite")
    if isinstance(children, bool) or not isinstance(children, Integral) or children < 1:
        raise ValueError("children must be a positive integer")
    children = int(children)
    m = len(values)
    E = np.zeros((m * children, m), dtype=float)
    C = np.zeros((m, m * children), dtype=float)
    for i in range(m):
        E[i * children:(i + 1) * children, i] = 1.0
        C[i, i * children:(i + 1) * children] = 1.0 / children
    T_c = np.diag(values)
    T_f = np.diag(np.repeat(values, children))
    return E, C, T_f, T_c


def defect_norm_bound(
    coarsen: np.ndarray,
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
    power: int,
) -> tuple[float, float]:
    power = _require_power(power)
    coarsen, fine_operator, coarse_operator = _validate_tower_shapes(
        coarsen, fine_operator, coarse_operator
    )
    actual = np.linalg.norm(coarsen @ np.linalg.matrix_power(fine_operator, power) - np.linalg.matrix_power(coarse_operator, power) @ coarsen, 2)
    defect = np.linalg.norm(power_defect(coarsen, fine_operator, coarse_operator), 2)
    nf = np.linalg.norm(fine_operator, 2)
    nc = np.linalg.norm(coarse_operator, 2)
    bound = defect * sum((nc ** (power - 1 - k)) * (nf**k) for k in range(power))
    return float(actual), float(bound)
