from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np

Array = np.ndarray


def _sizes_from_blocks(blocks: Sequence[Array]) -> tuple[int, ...]:
    sizes: list[int] = []
    for block in blocks:
        if block.ndim != 2 or block.shape[0] != block.shape[1]:
            raise ValueError("every diagonal packet must be square")
        sizes.append(int(block.shape[0]))
    if not sizes:
        raise ValueError("at least one packet is required")
    return tuple(sizes)


def packet_slices(sizes: Sequence[int]) -> tuple[slice, ...]:
    start = 0
    result: list[slice] = []
    for size in sizes:
        if size <= 0:
            raise ValueError("packet sizes must be positive")
        result.append(slice(start, start + int(size)))
        start += int(size)
    return tuple(result)


def materialize_blocks(blocks: Sequence[Array]) -> Array:
    sizes = _sizes_from_blocks(blocks)
    dtype = np.result_type(*[block.dtype for block in blocks])
    total = sum(sizes)
    out = np.zeros((total, total), dtype=dtype)
    for slc, block in zip(packet_slices(sizes), blocks, strict=True):
        out[slc, slc] = block
    return out


def packet_blocks(matrix: Array, sizes: Sequence[int]) -> dict[tuple[int, int], Array]:
    matrix = np.asarray(matrix)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("matrix must be square")
    if sum(sizes) != matrix.shape[0]:
        raise ValueError("packet sizes do not match matrix dimension")
    slices = packet_slices(sizes)
    return {
        (beta, alpha): matrix[slices[beta], slices[alpha]].copy()
        for beta in range(len(sizes))
        for alpha in range(len(sizes))
    }


@dataclass(frozen=True)
class BlockDiagonal:
    blocks: tuple[Array, ...]

    def __post_init__(self) -> None:
        sizes = _sizes_from_blocks(self.blocks)
        object.__setattr__(self, "sizes", sizes)
        object.__setattr__(self, "slices", packet_slices(sizes))
        object.__setattr__(self, "n", sum(sizes))

    @classmethod
    def from_sequence(cls, blocks: Sequence[Array]) -> "BlockDiagonal":
        return cls(tuple(np.asarray(block) for block in blocks))

    def materialize(self) -> Array:
        return materialize_blocks(self.blocks)

    def apply(self, x: Array) -> Array:
        x = np.asarray(x)
        vector = x.ndim == 1
        if vector:
            x = x[:, None]
        if x.ndim != 2 or x.shape[0] != self.n:
            raise ValueError("right-hand side has incompatible shape")
        out = np.empty((self.n, x.shape[1]), dtype=np.result_type(x.dtype, *[b.dtype for b in self.blocks]))
        for slc, block in zip(self.slices, self.blocks, strict=True):
            out[slc] = block @ x[slc]
        return out[:, 0] if vector else out

    def solve(self, b: Array) -> Array:
        b = np.asarray(b)
        vector = b.ndim == 1
        if vector:
            b = b[:, None]
        if b.shape[0] != self.n:
            raise ValueError("right-hand side has incompatible shape")
        out = np.empty_like(b, dtype=np.result_type(b.dtype, *[block.dtype for block in self.blocks]))
        for slc, block in zip(self.slices, self.blocks, strict=True):
            out[slc] = np.linalg.solve(block, b[slc])
        return out[:, 0] if vector else out

    def transpose_apply(self, x: Array) -> Array:
        return BlockDiagonal.from_sequence([b.T.conj() for b in self.blocks]).apply(x)


@dataclass(frozen=True)
class BDLRMatrix:
    diagonal: BlockDiagonal
    u: Array
    v: Array

    def __post_init__(self) -> None:
        u = np.asarray(self.u)
        v = np.asarray(self.v)
        if u.ndim != 2 or v.ndim != 2 or u.shape != v.shape:
            raise ValueError("u and v must have the same two-dimensional shape")
        if u.shape[0] != self.diagonal.n:
            raise ValueError("low-rank factors must match the diagonal dimension")
        object.__setattr__(self, "u", u)
        object.__setattr__(self, "v", v)
        object.__setattr__(self, "n", self.diagonal.n)
        object.__setattr__(self, "rank", u.shape[1])

    def materialize(self) -> Array:
        return self.diagonal.materialize() + self.u @ self.v.T.conj()

    def apply(self, x: Array) -> Array:
        x = np.asarray(x)
        return self.diagonal.apply(x) + self.u @ (self.v.T.conj() @ x)

    def solve(self, b: Array) -> Array:
        """Apply the exact Woodbury formula, assuming all required inverses exist."""
        dinv_b = self.diagonal.solve(b)
        dinv_u = self.diagonal.solve(self.u)
        middle = np.eye(self.rank, dtype=np.result_type(dinv_u, self.v)) + self.v.T.conj() @ dinv_u
        correction = dinv_u @ np.linalg.solve(middle, self.v.T.conj() @ dinv_b)
        return dinv_b - correction

    def compressed_product(self, other: "BDLRMatrix") -> "BDLRMatrix":
        """Return an exact BDLR representation of self @ other.

        The resulting rank is at most rank(self)+rank(other), before optional
        numerical recompression.
        """
        if self.diagonal.sizes != other.diagonal.sizes:
            raise ValueError("packet structures must agree")
        d_blocks = tuple(a @ b for a, b in zip(self.diagonal.blocks, other.diagonal.blocks, strict=True))
        d_product = BlockDiagonal(d_blocks)
        d_a_u_b = self.diagonal.apply(other.u)
        interaction = self.v.T.conj() @ other.u
        left_1 = d_a_u_b + self.u @ interaction
        right_1 = other.v
        left_2 = self.u
        right_2 = other.diagonal.transpose_apply(self.v)
        u = np.concatenate([left_1, left_2], axis=1)
        v = np.concatenate([right_1, right_2], axis=1)
        return BDLRMatrix(d_product, u, v)


@dataclass(frozen=True)
class BlockSparseMatrix:
    sizes: tuple[int, ...]
    edges: Mapping[tuple[int, int], Array]

    def __post_init__(self) -> None:
        slices = packet_slices(self.sizes)
        checked: dict[tuple[int, int], Array] = {}
        for (beta, alpha), block in self.edges.items():
            if not (0 <= alpha < len(self.sizes) and 0 <= beta < len(self.sizes)):
                raise ValueError("edge index is outside packet range")
            block = np.asarray(block)
            expected = (self.sizes[beta], self.sizes[alpha])
            if block.shape != expected:
                raise ValueError(f"edge {(beta, alpha)} has shape {block.shape}, expected {expected}")
            checked[(beta, alpha)] = block
        object.__setattr__(self, "edges", checked)
        object.__setattr__(self, "slices", slices)
        object.__setattr__(self, "n", sum(self.sizes))

    def materialize(self) -> Array:
        dtype = np.result_type(*[block.dtype for block in self.edges.values()]) if self.edges else float
        out = np.zeros((self.n, self.n), dtype=dtype)
        for (beta, alpha), block in self.edges.items():
            out[self.slices[beta], self.slices[alpha]] += block
        return out

    def apply(self, x: Array) -> Array:
        x = np.asarray(x)
        vector = x.ndim == 1
        if vector:
            x = x[:, None]
        if x.ndim != 2 or x.shape[0] != self.n:
            raise ValueError("right-hand side has incompatible shape")
        dtype = np.result_type(x.dtype, *[block.dtype for block in self.edges.values()]) if self.edges else x.dtype
        out = np.zeros((self.n, x.shape[1]), dtype=dtype)
        for (beta, alpha), block in self.edges.items():
            out[self.slices[beta]] += block @ x[self.slices[alpha]]
        return out[:, 0] if vector else out

    @property
    def stored_entries(self) -> int:
        return sum(block.size for block in self.edges.values())
