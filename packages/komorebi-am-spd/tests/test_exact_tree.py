from __future__ import annotations

import numpy as np

from am_spd import exact


def test_exact_frontier_is_nondominated() -> None:
    rng = np.random.default_rng(17)
    residual = rng.normal(size=(8, 8, 1))
    root = exact.build_tree(8, 8, max_depth=1)
    exact.fill_tree_models(root, residual, max_rank=1)
    frontier = exact.exact_tree_frontier(root, parameter_budget=100)

    assert frontier
    costs = [state.parameter_count for state in frontier]
    errors = [state.error_squared for state in frontier]
    assert all(left < right for left, right in zip(costs, costs[1:], strict=False))
    assert all(left > right for left, right in zip(errors, errors[1:], strict=False))


def test_patch_matrix_roundtrip() -> None:
    rng = np.random.default_rng(23)
    patch = rng.normal(size=(5, 7, 3))
    for orientation in ("row", "column", "channel"):
        matrix = exact.patch_matrix(patch, orientation)
        recovered = exact.component_from_matrix(matrix, patch.shape, orientation)
        np.testing.assert_allclose(recovered, patch)
