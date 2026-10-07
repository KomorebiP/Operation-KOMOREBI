from __future__ import annotations

from typing import Tuple

import numpy as np


def power_defect(coarsen: np.ndarray, fine_operator: np.ndarray, coarse_operator: np.ndarray) -> np.ndarray:
    return coarsen @ fine_operator - coarse_operator @ coarsen


def power_defect_expansion(
    coarsen: np.ndarray,
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
    power: int,
) -> np.ndarray:
    if power < 1:
        raise ValueError("power must be positive")
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
    values = np.asarray(coarse_values, dtype=float)
    if children < 1:
        raise ValueError("children must be positive")
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
    actual = np.linalg.norm(coarsen @ np.linalg.matrix_power(fine_operator, power) - np.linalg.matrix_power(coarse_operator, power) @ coarsen, 2)
    defect = np.linalg.norm(power_defect(coarsen, fine_operator, coarse_operator), 2)
    nf = np.linalg.norm(fine_operator, 2)
    nc = np.linalg.norm(coarse_operator, 2)
    bound = defect * sum((nc ** (power - 1 - k)) * (nf**k) for k in range(power))
    return float(actual), float(bound)
