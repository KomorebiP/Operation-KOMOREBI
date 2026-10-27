from __future__ import annotations

from typing import Sequence

import numpy as np


def coefficient_packets(coefficients: Sequence[complex], order: int) -> list[np.ndarray]:
    coeffs = np.asarray(coefficients)
    idx = np.arange(len(coeffs))
    return [np.where(idx % order == r, coeffs, 0) for r in range(order)]


def packet_product(a: Sequence[complex], b: Sequence[complex], order: int) -> list[np.ndarray]:
    a_packets, b_packets = coefficient_packets(a, order), coefficient_packets(b, order)
    length = len(a) + len(b) - 1
    out = [np.zeros(length, dtype=np.result_type(a, b, complex)) for _ in range(order)]
    for i in range(order):
        for j in range(order):
            out[(i + j) % order] += np.convolve(a_packets[i], b_packets[j])
    return [np.real_if_close(packet) for packet in out]


def nonlinear_shift_filter(x: Sequence[float], alpha: float = 0.25) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    return arr + alpha * arr * np.roll(arr, 1)


def nonlinear_packet_reconstruct(x: Sequence[float], order: int, alpha: float = 0.25) -> np.ndarray:
    y = nonlinear_shift_filter(x, alpha)
    idx = np.arange(len(y))
    packets = [np.where(idx % order == r, y, 0) for r in range(order)]
    return sum(packets, np.zeros_like(y))
