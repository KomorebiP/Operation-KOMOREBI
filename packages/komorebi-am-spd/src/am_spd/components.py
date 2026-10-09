from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import numpy as np
from numpy.typing import NDArray

from . import atlas, final, multiscale, singular
from .api import AMSpdConfig, AMSpdResult, reconstruct

Array = NDArray[np.float64]


@dataclass(frozen=True)
class TreeOptimizationResult:
    lagrange: multiscale.AMResult
    exact: final.ExactTreeResult
    selected_name: str
    reconstruction: Array
    residual: Array
    parameter_count: int
    candidate_rmse: dict[str, float]


@dataclass(frozen=True)
class PixelClosure:
    """Sparse standard-coordinate completion of a finite raster residual."""

    base_reconstruction: Array
    indices: NDArray[np.int64]
    values: Array
    threshold: float

    @classmethod
    def from_result(cls, result: AMSpdResult, threshold: float = 0.0) -> PixelClosure:
        if not np.isfinite(threshold) or threshold < 0:
            raise ValueError("threshold must be finite and nonnegative")
        residual = np.asarray(result.archive_residual, dtype=np.float64)
        magnitude = np.max(np.abs(residual), axis=2)
        indices = np.argwhere(magnitude > threshold).astype(np.int64)
        values = residual[indices[:, 0], indices[:, 1]].copy() if indices.size else np.empty((0, residual.shape[2]))
        return cls(np.asarray(result.reconstruction, dtype=np.float64).copy(), indices, values, float(threshold))

    @property
    def pixel_packet_count(self) -> int:
        return int(len(self.indices))

    @property
    def scalar_coefficient_count(self) -> int:
        return int(self.values.size)

    def residual(self) -> Array:
        value = np.zeros_like(self.base_reconstruction)
        if self.indices.size:
            value[self.indices[:, 0], self.indices[:, 1]] = self.values
        return value

    def decode(self) -> Array:
        return self.base_reconstruction + self.residual()

    def identity_error(self, image: Array) -> float:
        target = atlas.ensure_image(image)
        return float(np.max(np.abs(target - self.decode())))


@dataclass(frozen=True)
class BaselineResult:
    name: str
    reconstruction: Array
    metrics: dict[str, float]
    budget: int | float
    notes: str


def fit_packet_core(image: Array, config: AMSpdConfig | None = None) -> atlas.ReconstructionResult:
    settings = config or AMSpdConfig.quick("core")
    value = atlas.ensure_image(image)
    if value.shape[0] < 8 or value.shape[1] < 8:
        raise ValueError("AM-SPD requires image height and width of at least 8 pixels")
    solver = atlas.InfinitePacketReconstructor(
        value,
        complexity_weight=settings.complexity_weight,
        max_candidates_per_iteration=settings.max_candidates_per_iteration,
        residual_refresh=settings.residual_refresh,
        quadtree_refine_every=settings.quadtree_refine_every,
        random_seed=settings.random_seed,
    )
    return solver.run(max_packets=settings.packet_budget, tolerance=settings.tolerance)


def fit_singular_packets(
    image: Array,
    core_result: atlas.ReconstructionResult | None = None,
    config: AMSpdConfig | None = None,
) -> singular.SingularPacketResult:
    settings = config or AMSpdConfig.quick("spd")
    value = atlas.ensure_image(image)
    core = core_result or fit_packet_core(value, settings)
    return singular.singular_packet_completion(
        value,
        core,
        mode_budget=settings.singular_budget,
        max_depth=max(1, settings.tree_depth + 2),
        max_regions_per_iteration=max(4, settings.max_regions * 2),
        parameter_budget=settings.parameter_budget,
    )


def optimize_trees(
    image: Array,
    core_result: atlas.ReconstructionResult | None = None,
    singular_result: singular.SingularPacketResult | None = None,
    config: AMSpdConfig | None = None,
) -> TreeOptimizationResult:
    settings = config or AMSpdConfig.quick("tree")
    value = atlas.ensure_image(image)
    core = core_result or fit_packet_core(value, settings)
    spd_result = singular_result or fit_singular_packets(value, core, settings)
    spd_parameters = int(spd_result.parameter_counts[-1]) if spd_result.parameter_counts else 0
    parameter_budget = settings.parameter_budget if settings.parameter_budget is not None else spd_parameters
    lagrange = multiscale.tree_result(
        value,
        core,
        parameter_budget,
        max_depth=settings.tree_depth,
        max_rank=settings.max_rank,
    )
    exact = final.exact_budget_tree_result(
        value,
        core,
        parameter_budget,
        max_depth=settings.tree_depth,
        max_rank=settings.max_rank,
    )
    candidate_rmse = {
        "lagrange_tree": final.exact_rmse(value, lagrange.reconstruction),
        "exact_budget_tree": final.exact_rmse(value, exact.reconstruction),
    }
    if candidate_rmse["exact_budget_tree"] <= candidate_rmse["lagrange_tree"]:
        return TreeOptimizationResult(
            lagrange,
            exact,
            "exact_budget_tree",
            exact.reconstruction,
            exact.residual,
            exact.parameter_count,
            candidate_rmse,
        )
    return TreeOptimizationResult(
        lagrange,
        exact,
        "lagrange_tree",
        lagrange.reconstruction,
        lagrange.residual,
        lagrange.parameter_count,
        candidate_rmse,
    )


def fit_portfolio(image: Array, config: AMSpdConfig | None = None) -> AMSpdResult:
    settings = config or AMSpdConfig.quick("portfolio")
    if settings.method != "portfolio":
        settings = replace(settings, method="portfolio")
    return reconstruct(image, settings)


def complete_with_pixels(result: AMSpdResult, threshold: float = 0.0) -> PixelClosure:
    """Complete an AM-SPD approximation in the finite pixel-coordinate basis.

    Unlike the archival dense refit helper, this representation stores only the
    unresolved pixel-channel coefficients. It is exact for ``threshold=0`` and
    avoids constructing a dense pixel-basis least-squares matrix.
    """

    return PixelClosure.from_result(result, threshold=threshold)


def compare_baselines(
    image: Array,
    *,
    coefficient_budget: int = 64,
    svd_rank: int = 4,
    quadtree_leaves: int = 32,
    tv_weight: float = 0.07,
) -> dict[str, BaselineResult]:
    value = atlas.ensure_image(image)
    reconstructions: dict[str, tuple[Array, int | float, str]] = {
        "fourier_lowpass": (
            atlas.fourier_lowpass_reconstruction(value, coefficient_budget),
            coefficient_budget,
            "Centered square Fourier low-pass support.",
        ),
        "dct": (
            atlas.dct_reconstruction(value, coefficient_budget),
            coefficient_budget,
            "Largest-energy shared spatial DCT coordinates.",
        ),
        "global_svd": (
            singular.joint_svd_reconstruction(value, svd_rank),
            svd_rank,
            "Joint global matrix SVD at the declared rank.",
        ),
        "quadtree": (
            atlas.adaptive_quadtree_reconstruction(value, quadtree_leaves),
            quadtree_leaves,
            "Adaptive piecewise-constant quadtree.",
        ),
        "tv": (
            atlas.tv_reconstruction(value, weight=tv_weight),
            tv_weight,
            "Total-variation denoising baseline; not parameter matched.",
        ),
    }
    return {
        name: BaselineResult(
            name=name,
            reconstruction=np.asarray(reconstruction, dtype=np.float64),
            metrics=atlas.image_metrics(value, atlas.bounded_synthesis(reconstruction)),
            budget=budget,
            notes=notes,
        )
        for name, (reconstruction, budget, notes) in reconstructions.items()
    }


def component_summary(result: AMSpdResult) -> dict[str, Any]:
    return {
        "selected_method": result.selected_method,
        "packets": len(result.core_result.active_specs) if result.core_result is not None else 0,
        "singular_modes": len(result.singular_result.modes) if result.singular_result is not None else 0,
        "lagrange_tree_selections": len(result.lagrange_tree_result.tree_selections) if result.lagrange_tree_result is not None else 0,
        "exact_tree_selections": len(result.exact_tree_result.selections) if result.exact_tree_result is not None else 0,
        "exact_frontier_states": len(result.exact_tree_result.frontier) if result.exact_tree_result is not None else 0,
        "portfolio_trials": sum(len(portfolio.trials) for portfolio in result.portfolios),
    }
