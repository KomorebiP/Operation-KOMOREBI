from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np


def packet_error_bound(
    block_norms: Sequence[float],
    relative_errors: Sequence[float],
    input_packet_norms: Sequence[float],
) -> float:
    """Triangle-inequality certificate for a block-diagonal packet application."""
    if not (len(block_norms) == len(relative_errors) == len(input_packet_norms)):
        raise ValueError("all packet sequences must have the same length")
    if any(value < 0 for value in (*block_norms, *relative_errors, *input_packet_norms)):
        raise ValueError("norms and tolerances must be nonnegative")
    return float(sum(a * eps * x for a, eps, x in zip(block_norms, relative_errors, input_packet_norms, strict=True)))


def transfer_error_bound(
    edge_norms: Sequence[float],
    relative_errors: Sequence[float],
    source_norms: Sequence[float],
) -> float:
    return packet_error_bound(edge_norms, relative_errors, source_norms)


def optimal_precision_tolerances(
    sensitivities: Sequence[float],
    costs: Sequence[float],
    total_tolerance: float,
) -> np.ndarray:
    """Solve a continuous packet-precision allocation model.

    The model minimizes sum c_e log(1/eps_e) subject to
    sum s_e eps_e = total_tolerance. The exact optimizer is
    eps_e = total_tolerance*c_e/(s_e*sum c).
    """
    s = np.asarray(sensitivities, dtype=float)
    c = np.asarray(costs, dtype=float)
    if s.ndim != 1 or c.ndim != 1 or s.size != c.size or s.size == 0:
        raise ValueError("sensitivities and costs must be nonempty one-dimensional arrays of equal size")
    if np.any(s <= 0) or np.any(c <= 0) or total_tolerance <= 0:
        raise ValueError("all sensitivities, costs, and total_tolerance must be positive")
    return total_tolerance * c / (s * c.sum())


def _dtype_for_bits(bits: int):
    if bits <= 16:
        return np.float16
    if bits <= 32:
        return np.float32
    return np.float64


def quantize_by_packet(blocks: Sequence[np.ndarray], bits: Sequence[int]) -> tuple[np.ndarray, ...]:
    if len(blocks) != len(bits):
        raise ValueError("blocks and bits must have equal length")
    result = []
    for block, bit_count in zip(blocks, bits, strict=True):
        dtype = _dtype_for_bits(int(bit_count))
        result.append(np.asarray(block, dtype=dtype).astype(np.float64))
    return tuple(result)


def actual_block_diagonal_error(
    exact_blocks: Sequence[np.ndarray],
    approximate_blocks: Sequence[np.ndarray],
    packet_inputs: Sequence[np.ndarray],
) -> float:
    if not (len(exact_blocks) == len(approximate_blocks) == len(packet_inputs)):
        raise ValueError("packet sequences must agree")
    errors = [
        (np.asarray(approx) - np.asarray(exact)) @ np.asarray(x)
        for exact, approx, x in zip(exact_blocks, approximate_blocks, packet_inputs, strict=True)
    ]
    return float(np.linalg.norm(np.concatenate([e.reshape(-1) for e in errors])))
