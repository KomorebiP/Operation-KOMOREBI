from __future__ import annotations

import numpy as np

from am_spd import (
    AMSpdConfig,
    compare_baselines,
    complete_with_pixels,
    fit_packet_core,
    fit_singular_packets,
    optimize_trees,
    reconstruct,
)
from am_spd.atlas import synthetic_geometry


def config(method: str) -> AMSpdConfig:
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


def test_public_component_pipeline() -> None:
    image = synthetic_geometry(12)
    core = fit_packet_core(image, config("core"))
    spd = fit_singular_packets(image, core, config("spd"))
    trees = optimize_trees(image, core, spd, config("tree"))

    assert len(core.active_specs) <= 4
    assert len(spd.modes) <= 2
    assert trees.selected_name in {"lagrange_tree", "exact_budget_tree"}
    assert np.isfinite(trees.reconstruction).all()


def test_sparse_pixel_coordinate_completion_is_exact() -> None:
    image = synthetic_geometry(12)
    result = reconstruct(image, config("core"))
    closure = complete_with_pixels(result)
    assert closure.pixel_packet_count > 0
    assert closure.identity_error(image) <= 1e-12
    np.testing.assert_allclose(closure.decode(), image, atol=1e-12, rtol=0.0)


def test_baseline_suite_returns_finite_metrics() -> None:
    image = synthetic_geometry(12)
    results = compare_baselines(image, coefficient_budget=8, svd_rank=1, quadtree_leaves=4)
    assert set(results) == {"fourier_lowpass", "dct", "global_svd", "quadtree", "tv"}
    assert all(np.isfinite(result.reconstruction).all() for result in results.values())
    assert all(np.isfinite(result.metrics["rmse"]) for result in results.values())
