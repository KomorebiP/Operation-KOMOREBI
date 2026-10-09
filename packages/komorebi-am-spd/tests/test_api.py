from __future__ import annotations

import numpy as np
import pytest

from am_spd import AMSpdConfig, reconstruct
from am_spd.atlas import synthetic_geometry


def tiny_config(method: str) -> AMSpdConfig:
    return AMSpdConfig(
        method=method,
        packet_budget=4,
        singular_budget=2,
        tree_depth=1,
        max_rank=1,
        reopen_fractions=(0.2,),
        max_actions=1,
        max_regions=4,
        max_candidates_per_iteration=36,
    )


def test_core_preserves_shape_and_exact_archive_identity() -> None:
    image = synthetic_geometry(12)
    result = reconstruct(image, tiny_config("core"))
    assert result.reconstruction.shape == image.shape
    assert result.packet_count <= 4
    assert result.exact_identity_error <= 1e-12
    np.testing.assert_allclose(result.exact_reconstruction(), image, atol=1e-12, rtol=0.0)


def test_spd_does_not_increase_raw_residual_norm() -> None:
    image = synthetic_geometry(12)
    result = reconstruct(image, tiny_config("spd"))
    assert result.core_result is not None
    assert result.singular_result is not None
    assert np.linalg.norm(result.archive_residual) <= np.linalg.norm(result.core_result.residual) + 1e-10
    assert result.exact_identity_error <= 1e-12


def test_tree_selects_a_finite_candidate() -> None:
    image = synthetic_geometry(12)
    result = reconstruct(image, tiny_config("tree"))
    assert result.selected_method in {"lagrange_tree", "exact_budget_tree"}
    assert result.lagrange_tree_result is not None
    assert result.exact_tree_result is not None
    assert set(result.candidate_rmse) == {"lagrange_tree", "exact_budget_tree"}
    assert np.isfinite(result.reconstruction).all()


@pytest.mark.slow
def test_portfolio_smoke() -> None:
    image = synthetic_geometry(12)
    result = reconstruct(image, tiny_config("portfolio"))
    assert result.selected_method.startswith("portfolio:")
    assert len(result.portfolios) == 3
    assert result.exact_identity_error <= 1e-12
    assert np.isfinite(result.metrics["rmse"])


def test_invalid_small_image_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least 8"):
        reconstruct(np.zeros((4, 4)), tiny_config("core"))
