from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from am_spd import (
    AMSpdConfig,
    TiledAMSpdModel,
    TiledConfig,
    compare_model_archives,
    load_model_archive,
    resume_tiled_model,
    tiled_reconstruct,
)


def config() -> AMSpdConfig:
    return AMSpdConfig(
        method="core",
        packet_budget=3,
        singular_budget=1,
        tree_depth=1,
        max_rank=1,
        max_actions=1,
        max_regions=3,
        max_candidates_per_iteration=28,
        tolerance=0.0,
    )


def test_tiled_reconstruction_and_model_roundtrip(tmp_path: Path) -> None:
    rng = np.random.default_rng(20260819)
    image = rng.random((18, 22, 3))
    result = tiled_reconstruct(image, config(), TiledConfig(tile_size=12, overlap=4, workers=2))

    assert len(result.regions) > 1
    assert result.reconstruction.shape == image.shape
    assert result.exact_identity_error <= 1e-12

    path = result.save_model(
        tmp_path / "image.amspdt",
        residual_storage="sparse",
        include_input=True,
        include_tile_models=True,
    )
    loaded = load_model_archive(path)
    assert isinstance(loaded, TiledAMSpdModel)
    assert loaded.verify()["passed"] is True
    assert len(loaded.tile_models) == len(result.regions)
    assert loaded.resume_state_quality == "exact"
    assert all(model.input_image is not None for model in loaded.tile_models)
    np.testing.assert_allclose(loaded.decode("exact"), image, atol=1e-12, rtol=0.0)


def test_model_comparison_reports_pairwise_deltas(tmp_path: Path) -> None:
    rng = np.random.default_rng(17)
    image = rng.random((12, 14, 1))
    first = tiled_reconstruct(image, config(), TiledConfig(tile_size=10, overlap=2))
    second = tiled_reconstruct(image, config(), TiledConfig(tile_size=12, overlap=2))
    first_path = first.save_model(tmp_path / "first.amspdt", include_input=True)
    second_path = second.save_model(tmp_path / "second.amspdt", include_input=True)

    comparison = compare_model_archives([first_path, second_path])
    assert len(comparison["models"]) == 2
    assert comparison["pairwise"][0]["same_shape"] is True
    assert comparison["pairwise"][0]["exact_rmse"] <= 1e-12


@pytest.mark.parametrize("include_input", [False, True])
def test_tiled_checkpoint_resume_matches_uninterrupted_tiles(tmp_path: Path, include_input: bool) -> None:
    rng = np.random.default_rng(314159)
    image = rng.random((14, 16, 1))
    tiles = TiledConfig(tile_size=10, overlap=2, workers=2)
    initial = tiled_reconstruct(image, config(), tiles)
    model = load_model_archive(
        initial.save_model(
            tmp_path / "checkpoint.amspdt",
            residual_storage="sparse",
            include_tile_models=True,
            include_input=include_input,
        )
    )
    assert isinstance(model, TiledAMSpdModel)
    assert model.supports_resume is True
    assert model.resume_state_quality == ("exact" if include_input else "frontier-exact")

    resumed = resume_tiled_model(model, target_packet_budget=4, workers=2)
    uninterrupted = tiled_reconstruct(image, replace(config(), packet_budget=4), tiles)
    if include_input:
        np.testing.assert_array_equal(resumed.reconstruction, uninterrupted.reconstruction)
    else:
        np.testing.assert_allclose(resumed.reconstruction, uninterrupted.reconstruction, atol=1e-14, rtol=0.0)
    assert resumed.exact_identity_error <= 1e-12


def test_tiled_validation_rejects_inconsistent_totals(tmp_path: Path) -> None:
    image = np.random.default_rng(123).random((16, 16, 1))
    result = tiled_reconstruct(image, config(), TiledConfig(tile_size=10, overlap=2))
    model = result.to_model(include_input=True, include_tile_models=True)

    model.parameter_count += 1
    verification = model.verify()
    assert not verification["passed"]
    assert any("parameter_count" in error for error in verification["errors"])


def test_tiled_validation_rejects_negative_residual_threshold() -> None:
    image = np.random.default_rng(456).random((16, 16, 1))
    result = tiled_reconstruct(image, config(), TiledConfig(tile_size=10, overlap=2))
    model = result.to_model(include_input=True, include_tile_models=False)
    model.residual_threshold = -1.0
    verification = model.verify()
    assert not verification["passed"]
    assert any("residual_threshold" in error for error in verification["errors"])
