from __future__ import annotations

from typing import Sequence

import numpy as np


def rank_mod_p(matrix: Sequence[Sequence[int]] | np.ndarray, p: int) -> int:
    a = np.array(matrix, dtype=int) % p
    rows, cols = a.shape
    rank = 0
    col = 0
    while rank < rows and col < cols:
        pivot = next((r for r in range(rank, rows) if a[r, col] % p), None)
        if pivot is None:
            col += 1
            continue
        if pivot != rank:
            a[[rank, pivot]] = a[[pivot, rank]]
        a[rank] = (a[rank] * pow(int(a[rank, col]), -1, p)) % p
        for r in range(rows):
            if r != rank and a[r, col] % p:
                a[r] = (a[r] - a[r, col] * a[rank]) % p
        rank += 1
        col += 1
    return rank


def cohomology_dimensions(differentials: Sequence[np.ndarray], dimensions: Sequence[int], p: int) -> list[int]:
    """H^i dimensions for d_i: C^i -> C^{i+1}."""
    if len(differentials) != len(dimensions) - 1:
        raise ValueError("there must be one fewer differential than spaces")
    ranks = [rank_mod_p(d, p) for d in differentials]
    for i in range(len(differentials) - 1):
        product = (np.asarray(differentials[i + 1], dtype=int) @ np.asarray(differentials[i], dtype=int)) % p
        if np.any(product):
            raise ValueError("differentials do not form a complex")
    out: list[int] = []
    for i, dim in enumerate(dimensions):
        outgoing_rank = ranks[i] if i < len(ranks) else 0
        incoming_rank = ranks[i - 1] if i > 0 else 0
        out.append(int(dim) - outgoing_rank - incoming_rank)
    return out


def packet_cohomology_dimensions(
    packet_differentials: Sequence[Sequence[np.ndarray]],
    packet_dimensions: Sequence[Sequence[int]],
    p: int,
) -> list[list[int]]:
    """Compute cohomology for each invariant packet subcomplex."""
    packet_count = len(packet_dimensions)
    if len(packet_differentials) != packet_count:
        raise ValueError("packet count mismatch")
    return [
        cohomology_dimensions(packet_differentials[j], packet_dimensions[j], p)
        for j in range(packet_count)
    ]
