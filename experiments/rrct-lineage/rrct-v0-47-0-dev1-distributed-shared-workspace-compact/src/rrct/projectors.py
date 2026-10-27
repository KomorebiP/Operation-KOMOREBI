"""Nested orthogonal resolution projectors.

The :class:`NestedOrthogonalProjectors` class supplies the finite-dimensional
resolution lattice used by the prototype.  A single orthonormal basis is
truncated at increasing ranks, which makes nesting exact up to floating-point
roundoff::

    P_i P_j = P_min(i, j)

The implementation accepts either individual vectors or arrays whose final
axis is the represented state space.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]


def _default_ranks(dimension: int, n_levels: int) -> tuple[int, ...]:
    """Return approximately evenly spaced, strictly increasing ranks."""

    if n_levels <= 0:
        raise ValueError("n_levels must be positive")
    count = min(dimension, n_levels)
    raw = np.rint(np.linspace(1, dimension, count)).astype(int)
    ranks = tuple(sorted(set(int(rank) for rank in raw)))
    if ranks[-1] != dimension:
        ranks = (*ranks, dimension)
    return ranks


class NestedOrthogonalProjectors:
    """A finite exact filtration of orthogonal projectors.

    Parameters
    ----------
    dimension:
        Dimension of the represented state space.
    ranks:
        Strictly increasing projector ranks.  The final rank must equal
        ``dimension`` so the last projector is the identity.  If omitted,
        approximately uniform ranks are generated from ``n_levels``.
    n_levels:
        Requested number of automatically generated levels.
    basis:
        Optional orthonormal basis stored column-wise.  Supplying a basis is
        useful when semantic coarse coordinates are known in advance.
    seed:
        Seed used to generate a deterministic random orthonormal basis when
        ``basis`` is omitted.
    """

    def __init__(
        self,
        dimension: int,
        *,
        ranks: Sequence[int] | None = None,
        n_levels: int = 4,
        basis: ArrayLike | None = None,
        seed: int | np.random.SeedSequence | None = 0,
    ) -> None:
        if int(dimension) != dimension or dimension <= 0:
            raise ValueError("dimension must be a positive integer")
        self.dimension = int(dimension)

        if ranks is None:
            parsed_ranks = _default_ranks(self.dimension, n_levels)
        else:
            parsed_ranks = tuple(int(rank) for rank in ranks)
            if not parsed_ranks:
                raise ValueError("ranks cannot be empty")
            if any(rank <= 0 or rank > self.dimension for rank in parsed_ranks):
                raise ValueError("every rank must lie in [1, dimension]")
            if any(left >= right for left, right in zip(parsed_ranks, parsed_ranks[1:])):
                raise ValueError("ranks must be strictly increasing")
            if parsed_ranks[-1] != self.dimension:
                raise ValueError("the final rank must equal dimension")
        self.ranks = parsed_ranks

        if basis is None:
            rng = np.random.default_rng(seed)
            matrix = rng.normal(size=(self.dimension, self.dimension))
            q, r = np.linalg.qr(matrix)
            # Fix QR sign ambiguity to make results reproducible across calls.
            signs = np.sign(np.diag(r))
            signs[signs == 0.0] = 1.0
            parsed_basis = q * signs
        else:
            parsed_basis = np.asarray(basis, dtype=np.float64)
            if parsed_basis.shape != (self.dimension, self.dimension):
                raise ValueError(
                    "basis must have shape "
                    f"({self.dimension}, {self.dimension})"
                )
            gram = parsed_basis.T @ parsed_basis
            if not np.allclose(gram, np.eye(self.dimension), atol=1e-10, rtol=1e-10):
                raise ValueError("basis columns must be orthonormal")

        self.basis: FloatArray = np.array(parsed_basis, dtype=np.float64, copy=True)
        self.basis.setflags(write=False)
        self._matrices: tuple[FloatArray, ...] = tuple(
            self._make_projector(rank) for rank in self.ranks
        )
        self._details: tuple[FloatArray, ...] = self._make_detail_matrices()

    def _make_projector(self, rank: int) -> FloatArray:
        leading = self.basis[:, :rank]
        matrix = np.asarray(leading @ leading.T, dtype=np.float64)
        matrix.setflags(write=False)
        return matrix

    def _make_detail_matrices(self) -> tuple[FloatArray, ...]:
        matrices: list[FloatArray] = []
        previous = np.zeros((self.dimension, self.dimension), dtype=np.float64)
        for projector in self._matrices:
            detail = np.asarray(projector - previous, dtype=np.float64)
            detail.setflags(write=False)
            matrices.append(detail)
            previous = projector
        return tuple(matrices)

    def __len__(self) -> int:
        """Return the number of resolution levels."""

        return len(self.ranks)

    def _level_index(self, level: int) -> int:
        index = int(level)
        if index != level or not 0 <= index < len(self):
            raise IndexError(f"level must lie in [0, {len(self) - 1}]")
        return index

    def matrix(self, level: int, *, copy: bool = True) -> FloatArray:
        """Return the orthogonal-projector matrix for ``level``."""

        matrix = self._matrices[self._level_index(level)]
        return matrix.copy() if copy else matrix

    def detail_matrix(self, level: int, *, copy: bool = True) -> FloatArray:
        """Return ``D_0=P_0`` or ``D_l=P_l-P_(l-1)`` for ``level``."""

        matrix = self._details[self._level_index(level)]
        return matrix.copy() if copy else matrix

    def project(self, values: ArrayLike, level: int) -> FloatArray:
        """Project ``values`` at a chosen resolution.

        The final axis of ``values`` must equal :attr:`dimension`.
        """

        array = np.asarray(values, dtype=np.float64)
        if array.ndim == 0 or array.shape[-1] != self.dimension:
            raise ValueError(
                f"values must have final dimension {self.dimension}, got {array.shape}"
            )
        projector = self._matrices[self._level_index(level)]
        return np.asarray(array @ projector, dtype=np.float64)

    def detail(self, values: ArrayLike, level: int) -> FloatArray:
        """Apply one orthogonal detail projector to ``values``."""

        array = np.asarray(values, dtype=np.float64)
        if array.ndim == 0 or array.shape[-1] != self.dimension:
            raise ValueError(
                f"values must have final dimension {self.dimension}, got {array.shape}"
            )
        detail = self._details[self._level_index(level)]
        return np.asarray(array @ detail, dtype=np.float64)

    def decompose(self, values: ArrayLike) -> tuple[FloatArray, ...]:
        """Return the mutually orthogonal resolution-detail components."""

        return tuple(self.detail(values, level) for level in range(len(self)))

    def reconstruct(self, details: Sequence[ArrayLike]) -> FloatArray:
        """Reconstruct a state by summing one component per detail level."""

        if len(details) != len(self):
            raise ValueError(f"expected {len(self)} detail components")
        arrays = [np.asarray(component, dtype=np.float64) for component in details]
        if any(array.ndim == 0 or array.shape[-1] != self.dimension for array in arrays):
            raise ValueError(
                f"every detail component must have final dimension {self.dimension}"
            )
        if any(array.shape != arrays[0].shape for array in arrays[1:]):
            raise ValueError("all detail components must have the same shape")
        return np.asarray(np.sum(np.stack(arrays, axis=0), axis=0), dtype=np.float64)

    def residual_norms(self, values: ArrayLike) -> FloatArray:
        """Return relative unresolved norm at every resolution level."""

        array = np.asarray(values, dtype=np.float64)
        if array.ndim != 1 or array.shape[0] != self.dimension:
            raise ValueError(f"values must be a vector of length {self.dimension}")
        scale = max(float(np.linalg.norm(array)), np.finfo(np.float64).eps)
        return np.asarray(
            [np.linalg.norm(array - self.project(array, level)) / scale for level in range(len(self))],
            dtype=np.float64,
        )

    def validate(self, *, atol: float = 1e-10) -> dict[str, float | bool]:
        """Numerically audit orthogonality, nesting, and exact reconstruction."""

        identity = np.eye(self.dimension)
        idempotence = max(
            float(np.linalg.norm(projector @ projector - projector, ord=2))
            for projector in self._matrices
        )
        symmetry = max(
            float(np.linalg.norm(projector.T - projector, ord=2))
            for projector in self._matrices
        )
        nesting = 0.0
        for left, p_left in enumerate(self._matrices):
            for right, p_right in enumerate(self._matrices):
                expected = self._matrices[min(left, right)]
                nesting = max(
                    nesting,
                    float(np.linalg.norm(p_left @ p_right - expected, ord=2)),
                )
        detail_orthogonality = 0.0
        for left, d_left in enumerate(self._details):
            for right, d_right in enumerate(self._details):
                if left != right:
                    detail_orthogonality = max(
                        detail_orthogonality,
                        float(np.linalg.norm(d_left @ d_right, ord=2)),
                    )
        completeness = float(np.linalg.norm(sum(self._details) - identity, ord=2))
        worst = max(
            idempotence,
            symmetry,
            nesting,
            detail_orthogonality,
            completeness,
        )
        return {
            "valid": worst <= atol,
            "idempotence_error": idempotence,
            "symmetry_error": symmetry,
            "nesting_error": nesting,
            "detail_orthogonality_error": detail_orthogonality,
            "completeness_error": completeness,
            "worst_error": worst,
        }


__all__ = ["FloatArray", "NestedOrthogonalProjectors"]
