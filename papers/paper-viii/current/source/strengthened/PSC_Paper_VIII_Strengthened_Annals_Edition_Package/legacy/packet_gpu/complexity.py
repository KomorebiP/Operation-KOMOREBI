from __future__ import annotations

from math import ceil
from typing import Iterable, Sequence


def dense_apply_flops(n: int, rhs: int = 1) -> int:
    if n <= 0 or rhs <= 0:
        raise ValueError("n and rhs must be positive")
    return 2 * n * n * rhs


def block_apply_flops(sizes: Sequence[int], rhs: int = 1) -> int:
    if rhs <= 0 or any(size <= 0 for size in sizes):
        raise ValueError("packet sizes and rhs must be positive")
    return 2 * rhs * sum(int(size) ** 2 for size in sizes)


def bdlr_apply_flops(sizes: Sequence[int], rank: int, rhs: int = 1) -> int:
    if rank < 0:
        raise ValueError("rank cannot be negative")
    n = sum(sizes)
    return block_apply_flops(sizes, rhs) + 4 * n * rank * rhs


def sparse_packet_apply_flops(sizes: Sequence[int], edges: Iterable[tuple[int, int]], rhs: int = 1) -> int:
    sizes = tuple(int(s) for s in sizes)
    return 2 * rhs * sum(sizes[beta] * sizes[alpha] for beta, alpha in edges)


def dense_storage(n: int, itemsize: int = 8) -> int:
    return n * n * itemsize


def block_storage(sizes: Sequence[int], itemsize: int = 8) -> int:
    return sum(int(size) ** 2 for size in sizes) * itemsize


def bdlr_storage(sizes: Sequence[int], rank: int, itemsize: int = 8) -> int:
    n = sum(sizes)
    return (sum(int(size) ** 2 for size in sizes) + 2 * n * rank) * itemsize


def equal_packet_sizes(n: int, block_size: int) -> tuple[int, ...]:
    if n <= 0 or block_size <= 0 or n % block_size:
        raise ValueError("block_size must divide n")
    return (block_size,) * (n // block_size)


def ideal_bdlr_speedup(n: int, block_size: int, rank: int) -> float:
    """Ideal arithmetic reduction for equal packets and explicit RHS application."""
    if min(n, block_size) <= 0 or rank < 0 or n % block_size:
        raise ValueError("invalid dimensions")
    denominator = n * block_size + 2 * n * rank
    return n * n / denominator


def representation_reduction(n: int, block_size: int, rank: int) -> float:
    return ideal_bdlr_speedup(n, block_size, rank)


def amortized_break_even(setup_time: float, dense_time: float, packet_time: float) -> int | None:
    """Smallest integer reuse count R for setup+R*packet < R*dense."""
    if setup_time < 0 or dense_time < 0 or packet_time < 0:
        raise ValueError("times cannot be negative")
    gain = dense_time - packet_time
    if gain <= 0:
        return None
    return max(1, int(setup_time // gain) + 1)


def graph_break_even(capture_time: float, ordinary_time: float, replay_time: float) -> int | None:
    return amortized_break_even(capture_time, ordinary_time, replay_time)


def transfer_break_even(transfer_time: float, cpu_time: float, gpu_time: float) -> int | None:
    return amortized_break_even(transfer_time, cpu_time, gpu_time)


def arithmetic_intensity(flops: float, bytes_moved: float) -> float:
    if bytes_moved <= 0:
        raise ValueError("bytes_moved must be positive")
    return float(flops) / float(bytes_moved)


def equal_block_launch_count(n: int, block_size: int, grouping: bool = True) -> int:
    if n % block_size:
        raise ValueError("block_size must divide n")
    return 1 if grouping else n // block_size
