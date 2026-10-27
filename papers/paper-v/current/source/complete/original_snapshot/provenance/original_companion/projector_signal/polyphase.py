from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


def residue_project(x: Sequence[complex], order: int, phase: int) -> np.ndarray:
    if order < 1:
        raise ValueError("order must be positive")
    arr = np.asarray(x)
    idx = np.arange(arr.size)
    out = np.zeros_like(arr)
    mask = idx % order == phase % order
    out[mask] = arr[mask]
    return out


def polyphase_analyze(x: Sequence[complex], order: int) -> list[np.ndarray]:
    if order < 1:
        raise ValueError("order must be positive")
    arr = np.asarray(x)
    return [arr[r::order].copy() for r in range(order)]


def polyphase_synthesize(
    channels: Sequence[Sequence[complex]],
    order: int | None = None,
    length: int | None = None,
) -> np.ndarray:
    nphase = order if order is not None else len(channels)
    if nphase < 1 or len(channels) != nphase:
        raise ValueError("number of channels must equal order")
    arrays = [np.asarray(channel) for channel in channels]
    natural_length = max((nphase * len(a) + r for r, a in enumerate(arrays)), default=0)
    out_length = natural_length if length is None else length
    dtype = np.result_type(*[a.dtype for a in arrays]) if arrays else float
    out = np.zeros(out_length, dtype=dtype)
    for r, channel in enumerate(arrays):
        positions = np.arange(r, out_length, nphase)
        count = min(len(channel), len(positions))
        out[positions[:count]] = channel[:count]
    return out


def refinement_children(coarse_order: int, fine_order: int, phase: int) -> tuple[int, ...]:
    if coarse_order < 1 or fine_order < 1:
        raise ValueError("orders must be positive")
    if fine_order % coarse_order:
        raise ValueError("fine order must be divisible by coarse order")
    return tuple(s for s in range(fine_order) if s % coarse_order == phase % coarse_order)


def verify_refinement(x: Sequence[complex], coarse_order: int, fine_order: int) -> float:
    arr = np.asarray(x)
    residual = 0.0
    for r in range(coarse_order):
        coarse = residue_project(arr, coarse_order, r)
        fine_sum = sum(
            (residue_project(arr, fine_order, s) for s in refinement_children(coarse_order, fine_order, r)),
            np.zeros_like(arr),
        )
        residual = max(residual, float(np.max(np.abs(coarse - fine_sum))))
    return residual


@dataclass(frozen=True)
class PolyphaseKernel:
    output_phase: int
    input_phase: int
    delays: tuple[int, ...]
    coefficients: tuple[complex, ...]


def polyphase_filter_kernels(h: Sequence[complex], order: int) -> list[list[PolyphaseKernel]]:
    taps = np.asarray(h)
    result: list[list[PolyphaseKernel]] = []
    for k in range(order):
        row: list[PolyphaseKernel] = []
        for s in range(order):
            entries: list[tuple[int, complex]] = []
            m_min = int(np.floor((-(k - s)) / order)) - 1
            m_max = int(np.ceil((len(taps) - 1 - (k - s)) / order)) + 1
            for m in range(m_min, m_max + 1):
                idx = order * m + k - s
                if 0 <= idx < len(taps) and taps[idx] != 0:
                    entries.append((m, complex(taps[idx])))
            row.append(
                PolyphaseKernel(
                    output_phase=k,
                    input_phase=s,
                    delays=tuple(m for m, _ in entries),
                    coefficients=tuple(c for _, c in entries),
                )
            )
        result.append(row)
    return result


def polyphase_convolution(x: Sequence[complex], h: Sequence[complex], order: int) -> np.ndarray:
    x_arr = np.asarray(x)
    h_arr = np.asarray(h)
    y_len = len(x_arr) + len(h_arr) - 1
    x_channels = polyphase_analyze(x_arr, order)
    kernels = polyphase_filter_kernels(h_arr, order)
    y_channels: list[np.ndarray] = []
    for k in range(order):
        yk_len = len(np.arange(k, y_len, order))
        yk = np.zeros(yk_len, dtype=np.result_type(x_arr, h_arr, complex))
        for s in range(order):
            xs = x_channels[s]
            kernel = kernels[k][s]
            for delay, coefficient in zip(kernel.delays, kernel.coefficients, strict=True):
                for n in range(yk_len):
                    q = n - delay
                    if 0 <= q < len(xs):
                        yk[n] += coefficient * xs[q]
        y_channels.append(yk)
    return np.real_if_close(polyphase_synthesize(y_channels, order=order, length=y_len), tol=1000)
