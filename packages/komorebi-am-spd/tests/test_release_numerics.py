from __future__ import annotations

import itertools

import numpy as np
import pytest

from am_spd import AMSpdConfig, atlas, exact, final, multiscale, reconstruct
from am_spd.api import reconstruct_from_core, resume_model


@pytest.mark.parametrize("name", ["packet_budget", "singular_budget", "parameter_budget", "tree_depth", "max_rank", "max_actions", "max_regions", "max_candidates_per_iteration", "residual_refresh", "quadtree_refine_every", "random_seed"])
@pytest.mark.parametrize("value", [1.5, True, -1])
def test_discrete_configuration_rejects_invalid_values(name: str, value: object) -> None:
    with pytest.raises(ValueError, match=name):
        AMSpdConfig(**{name: value})


@pytest.mark.parametrize("name", ["residual_refresh", "quadtree_refine_every"])
def test_refresh_intervals_cannot_be_zero(name: str) -> None:
    with pytest.raises(ValueError, match=name):
        AMSpdConfig(**{name: 0})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.01])
def test_complexity_weight_must_be_finite_and_nonnegative(value: float) -> None:
    with pytest.raises(ValueError, match="complexity_weight"):
        AMSpdConfig(complexity_weight=value)


def test_integer_brightness_uses_dtype_range() -> None:
    for dtype, intensity in [(np.uint8, 128), (np.uint16, 30000), (np.int16, 12000)]:
        image = np.full((8, 9), intensity, dtype=dtype)
        normalized = atlas.ensure_image(image)
        np.testing.assert_allclose(normalized, intensity / np.iinfo(dtype).max, rtol=0, atol=0)
    image = np.array([[100, 200]], dtype=np.uint8)
    np.testing.assert_allclose(atlas.ensure_image(image)[..., 0], image / 255.0)


@pytest.mark.parametrize("image", [np.zeros((8, 8, 0)), np.zeros((0, 8)), np.full((8, 8), 7.5), np.full((8, 8), -1.0), np.ones((8, 8), dtype=complex), np.full((8, 8), -1, dtype=np.int16)])
def test_invalid_source_arrays_fail_clearly(image: np.ndarray) -> None:
    with pytest.raises(ValueError):
        atlas.ensure_image(image)


@pytest.mark.parametrize("method", ["core", "spd", "tree", "portfolio"])
def test_two_channel_images_are_supported(method: str) -> None:
    image = np.random.default_rng(140).uniform(size=(8, 9, 2))
    result = reconstruct(image, AMSpdConfig(method=method, packet_budget=2, singular_budget=1, tree_depth=1, max_rank=1, max_actions=1, max_regions=2, reopen_fractions=(0.25,), max_candidates_per_iteration=24))
    assert result.reconstruction.shape == image.shape
    assert result.exact_identity_error < 1e-14
    assert all(np.isfinite(result.metrics[name]) for name in ("rmse", "ssim", "edge_rmse"))


@pytest.mark.parametrize("module", [exact, multiscale])
def test_duplicate_direction_does_not_create_rounding_leakage(module: object) -> None:
    basis, _ = np.linalg.qr(np.random.default_rng(41).normal(size=(90, 3)))
    complement = module.complement_basis([basis[:, 0]], basis)
    assert complement.shape == (90, 0)
    # A distinct direction must produce an orthogonal projector with the
    # expected independent least-squares energy reduction.
    raw = np.random.default_rng(44).normal(size=90)
    complement = module.complement_basis([basis[:, 0], raw], basis)
    assert complement.shape == (90, 1)
    np.testing.assert_allclose(basis.T @ complement, 0, atol=1e-13)
    target = np.random.default_rng(45).normal(size=(9, 10, 1))
    _, old_residual = module.project_target(target, basis)
    completed = np.column_stack((basis, complement))
    reconstruction, new_residual = module.project_target(target, completed)
    independent = completed @ np.linalg.lstsq(completed, target.reshape(-1), rcond=None)[0]
    np.testing.assert_allclose(reconstruction.reshape(-1), independent, atol=1e-13)
    expected_gain = np.sum((complement.T @ old_residual.reshape(-1)) ** 2)
    np.testing.assert_allclose(np.sum(old_residual**2) - np.sum(new_residual**2), expected_gain, atol=1e-12)


@pytest.mark.parametrize("method", ["spd", "tree", "portfolio"])
@pytest.mark.parametrize("budget", [0, 1, 30, 70])
def test_explicit_downstream_budget_is_respected(method: str, budget: int) -> None:
    image = np.random.default_rng(66).uniform(size=(8, 9))
    result = reconstruct(image, AMSpdConfig(method=method, packet_budget=2, singular_budget=3, parameter_budget=budget, tree_depth=1, max_rank=1, max_actions=1, max_regions=2, reopen_fractions=(0.25,), max_candidates_per_iteration=24))
    assert result.parameter_count <= budget
    assert result.run_metadata["parameter_budget_scope"] == "downstream_scalar_proxy"
    assert result.run_metadata["core_coefficient_count"] == result.packet_count
    assert np.linalg.norm(result.archive_residual) <= np.linalg.norm(result.core_result.residual) + 1e-12
    if method == "portfolio":
        for portfolio in result.portfolios:
            assert all(trial.parameter_count <= budget for trial in portfolio.trials)
            assert final.exact_rmse(result.input_image, portfolio.reconstruction) <= portfolio.trials[0].exact_rmse + 1e-13
    if budget == 0:
        assert result.parameter_count == 0


def test_small_exact_tree_matches_exhaustive_prunings() -> None:
    residual = np.random.default_rng(172).normal(size=(4, 4, 2))
    root = exact.build_tree(4, 4, max_depth=1)
    exact.fill_tree_models(root, residual, max_rank=1)
    possibilities = [(model.parameter_count, model.error_squared) for model in root.models]
    for combination in itertools.product(*(child.models for child in root.children)):
        possibilities.append((sum(model.parameter_count for model in combination), sum(model.error_squared for model in combination)))
    for budget in range(101):
        optimum = min((error, cost) for cost, error in possibilities if cost <= budget)
        selected = exact.best_budget_state(exact.exact_tree_frontier(root, budget), budget)
        assert selected is not None
        np.testing.assert_allclose(selected.error_squared, optimum[0], atol=1e-12)
        assert selected.parameter_count == optimum[1]


def test_metric_range_violation_is_measured_before_clipping() -> None:
    source = np.random.default_rng(201).uniform(size=(8, 9, 1))
    estimate = source.copy()
    estimate[0, 0, 0] = -0.2
    estimate[0, 1, 0] = 1.3
    metrics = atlas.image_metrics(source, estimate)
    np.testing.assert_allclose(metrics["range_violation"], 0.5)
    np.testing.assert_allclose(metrics["rmse"], np.sqrt(np.mean((source - np.clip(estimate, 0, 1)) ** 2)))


@pytest.mark.parametrize("name", ["additional_packets", "target_packet_budget"])
@pytest.mark.parametrize("value", [2.5, True, -1])
def test_resume_budget_requires_integers(name: str, value: object) -> None:
    source = np.random.default_rng(210).uniform(size=(8, 9, 1))
    model = reconstruct(source, AMSpdConfig(method="core", packet_budget=1)).to_model(include_input=True)
    with pytest.raises(ValueError, match=name):
        resume_model(model, **{name: value})


def test_core_cannot_be_reused_for_another_same_shape_source() -> None:
    source = np.random.default_rng(220).uniform(size=(8, 9, 1))
    settings = AMSpdConfig(method="core", packet_budget=1)
    core = reconstruct(source, settings).core_result
    with pytest.raises(ValueError, match="different source"):
        reconstruct_from_core(1 - source, core, settings)
    core.active_atoms[0][0, 0] = float("nan")
    with pytest.raises(ValueError, match="finite real"):
        reconstruct_from_core(source, core, settings)


def test_tiny_nonzero_local_residual_keeps_its_error_accounting() -> None:
    residual = np.full((4, 4, 1), 1e-10)
    model = exact.local_models(residual, exact.Region(0, 0, 4, 4))[0]
    assert model.rank == 0
    assert model.error_squared == np.sum(residual**2)
