from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np

SQRT2 = np.sqrt(2.0)


def _require_even(x: np.ndarray) -> None:
    if x.ndim != 1 or len(x) % 2:
        raise ValueError("the transform requires a one-dimensional even-length signal")


def haar_analyze(x: Sequence[complex]) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(x)
    _require_even(arr)
    even, odd = arr[0::2], arr[1::2]
    return (even + odd) / SQRT2, (even - odd) / SQRT2


def haar_synthesize(low: Sequence[complex], high: Sequence[complex]) -> np.ndarray:
    low_arr, high_arr = np.asarray(low), np.asarray(high)
    if low_arr.shape != high_arr.shape:
        raise ValueError("low and high channels must have the same shape")
    out = np.empty(2 * len(low_arr), dtype=np.result_type(low_arr, high_arr, float))
    out[0::2] = (low_arr + high_arr) / SQRT2
    out[1::2] = (low_arr - high_arr) / SQRT2
    return out


def haar_packet_analyze(x: Sequence[complex], depth: int) -> dict[str, np.ndarray]:
    if depth < 0:
        raise ValueError("depth must be nonnegative")
    packets: dict[str, np.ndarray] = {"": np.asarray(x).copy()}
    for _ in range(depth):
        refined: dict[str, np.ndarray] = {}
        for path, packet in packets.items():
            low, high = haar_analyze(packet)
            refined[path + "0"] = low
            refined[path + "1"] = high
        packets = refined
    return packets


def haar_packet_synthesize(packets: Mapping[str, Sequence[complex]]) -> np.ndarray:
    if not packets:
        raise ValueError("packets cannot be empty")
    depth = len(next(iter(packets)))
    if any(len(path) != depth for path in packets):
        raise ValueError("all packet paths must have the same depth")
    current = {path: np.asarray(value) for path, value in packets.items()}
    for _ in range(depth, 0, -1):
        parents = sorted({path[:-1] for path in current})
        next_level: dict[str, np.ndarray] = {}
        for parent in parents:
            low_key, high_key = parent + "0", parent + "1"
            if low_key not in current or high_key not in current:
                raise ValueError("packet tree is incomplete")
            next_level[parent] = haar_synthesize(current[low_key], current[high_key])
        current = next_level
    return current[""]


def lifting_analyze(x: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(x, dtype=float)
    _require_even(arr)
    even, odd = arr[0::2].copy(), arr[1::2].copy()
    detail = odd - even
    smooth = even + 0.5 * detail
    return smooth, detail


def lifting_synthesize(smooth: Sequence[float], detail: Sequence[float]) -> np.ndarray:
    smooth_arr, detail_arr = np.asarray(smooth, dtype=float), np.asarray(detail, dtype=float)
    if smooth_arr.shape != detail_arr.shape:
        raise ValueError("smooth and detail channels must have the same shape")
    even = smooth_arr - 0.5 * detail_arr
    odd = detail_arr + even
    out = np.empty(2 * len(even), dtype=float)
    out[0::2], out[1::2] = even, odd
    return out


def packet_energy(packets: Mapping[str, Sequence[complex]]) -> float:
    return float(sum(np.vdot(np.asarray(v), np.asarray(v)).real for v in packets.values()))
