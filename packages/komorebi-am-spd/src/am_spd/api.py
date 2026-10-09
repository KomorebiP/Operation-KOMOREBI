from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field, replace
from numbers import Integral, Real
from pathlib import Path
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from . import atlas, final, multiscale, singular

Array = NDArray[np.float64]
Method = Literal["core", "spd", "tree", "portfolio"]


@dataclass(frozen=True)
class AMSpdConfig:
    """Configuration for the public AM-SPD reconstruction pipeline."""

    method: Method = "portfolio"
    packet_budget: int = 16
    singular_budget: int = 8
    parameter_budget: int | None = None
    tree_depth: int = 2
    max_rank: int = 2
    reopen_fractions: tuple[float, ...] = (0.08, 0.16, 0.24)
    max_actions: int = 5
    max_regions: int = 12
    random_seed: int = 20260731
    complexity_weight: float = 0.035
    max_candidates_per_iteration: int = 170
    residual_refresh: int = 5
    quadtree_refine_every: int = 4
    tolerance: float = 1e-4

    def __post_init__(self) -> None:
        if not isinstance(self.method, str) or self.method not in {"core", "spd", "tree", "portfolio"}:
            raise ValueError(f"unsupported method: {self.method}")
        for name in (
            "packet_budget",
            "singular_budget",
            "tree_depth",
            "max_rank",
            "max_actions",
            "max_regions",
            "max_candidates_per_iteration",
            "residual_refresh",
            "quadtree_refine_every",
            "random_seed",
        ):
            number = getattr(self, name)
            if isinstance(number, (bool, np.bool_)) or not isinstance(number, Integral) or number < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
            object.__setattr__(self, name, int(number))
        if self.packet_budget < 1:
            raise ValueError("packet_budget must be at least 1")
        for name in ("residual_refresh", "quadtree_refine_every"):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} must be at least 1")
        if self.parameter_budget is not None:
            if isinstance(self.parameter_budget, (bool, np.bool_)) or not isinstance(self.parameter_budget, Integral) or self.parameter_budget < 0:
                raise ValueError("parameter_budget must be a nonnegative integer")
            object.__setattr__(self, "parameter_budget", int(self.parameter_budget))
        if not isinstance(self.tolerance, Real) or not math.isfinite(self.tolerance) or not 0.0 <= self.tolerance < 1.0:
            raise ValueError("tolerance must lie in [0, 1)")
        if not isinstance(self.complexity_weight, Real) or not math.isfinite(self.complexity_weight) or self.complexity_weight < 0:
            raise ValueError("complexity_weight must be finite and nonnegative")
        if any(not isinstance(value, Real) or not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in self.reopen_fractions):
            raise ValueError("reopen_fractions must lie in [0, 1]")
        object.__setattr__(self, "reopen_fractions", tuple(float(value) for value in self.reopen_fractions))

    @classmethod
    def quick(cls, method: Method = "portfolio") -> AMSpdConfig:
        return cls(method=method)

    @classmethod
    def paper_scale(cls, method: Method = "portfolio") -> AMSpdConfig:
        """Return the general paper-scale budget profile.

        This is a fresh search with the published 44-packet and 22-mode budget.
        It is distinct from exact historical benchmark replay.
        """

        return cls(
            method=method,
            packet_budget=44,
            singular_budget=22,
            tree_depth=3,
            max_rank=3,
            reopen_fractions=(0.04, 0.08, 0.12, 0.18, 0.25, 0.35),
            max_actions=12,
            max_regions=18,
        )

    @classmethod
    def paper(cls, method: Method = "portfolio") -> AMSpdConfig:
        return cls.paper_scale(method)


@dataclass
class AMSpdResult:
    """Finite AM-SPD result with exact residual accounting."""

    input_image: Array
    reconstruction: Array
    archive_residual: Array
    selected_method: str
    parameter_count: int
    packet_count: int
    metrics: dict[str, float]
    config: AMSpdConfig
    candidate_rmse: dict[str, float] = field(default_factory=dict)
    core_result: atlas.ReconstructionResult | None = field(default=None, repr=False)
    singular_result: singular.SingularPacketResult | None = field(default=None, repr=False)
    lagrange_tree_result: multiscale.AMResult | None = field(default=None, repr=False)
    exact_tree_result: final.ExactTreeResult | None = field(default=None, repr=False)
    portfolios: list[final.FinalPortfolio] = field(default_factory=list, repr=False)
    run_metadata: dict[str, object] = field(default_factory=dict)

    @property
    def residual(self) -> Array:
        return self.archive_residual

    @property
    def exact_identity_error(self) -> float:
        recovered = self.reconstruction + self.archive_residual
        return float(np.max(np.abs(self.input_image - recovered)))

    def bounded_reconstruction(self) -> Array:
        return atlas.bounded_synthesis(self.reconstruction)

    def exact_reconstruction(self) -> Array:
        return self.reconstruction + self.archive_residual

    def summary(self) -> dict[str, object]:
        return {
            "selected_method": self.selected_method,
            "shape": list(self.input_image.shape),
            "parameter_count": self.parameter_count,
            "packet_count": self.packet_count,
            "exact_identity_error": self.exact_identity_error,
            "metrics": {key: float(value) for key, value in self.metrics.items()},
            "candidate_rmse": {key: float(value) for key, value in self.candidate_rmse.items()},
            "config": asdict(self.config),
            "run_metadata": dict(self.run_metadata),
        }

    def save_archive(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            destination,
            input_image=self.input_image,
            reconstruction=self.reconstruction,
            archive_residual=self.archive_residual,
            summary_json=np.array(json.dumps(self.summary(), sort_keys=True)),
        )
        return destination

    def to_model(
        self,
        *,
        residual_storage: str = "dense",
        residual_threshold: float = 0.0,
        include_input: bool = False,
        include_atoms: bool = True,
        include_directions: bool = True,
        provenance: dict[str, object] | None = None,
    ):
        from .model import AMSpdModel

        return AMSpdModel.from_result(
            self,
            residual_storage=residual_storage,
            residual_threshold=residual_threshold,
            include_input=include_input,
            include_atoms=include_atoms,
            include_directions=include_directions,
            provenance=provenance,
        )

    def save_model(
        self,
        path: str | Path,
        *,
        residual_storage: str = "dense",
        residual_threshold: float = 0.0,
        include_input: bool = False,
        include_atoms: bool = True,
        include_directions: bool = True,
        provenance: dict[str, object] | None = None,
    ) -> Path:
        return self.to_model(
            residual_storage=residual_storage,
            residual_threshold=residual_threshold,
            include_input=include_input,
            include_atoms=include_atoms,
            include_directions=include_directions,
            provenance=provenance,
        ).save(path)


def _validate_image(image: Array) -> Array:
    value = atlas.ensure_image(image)
    if value.shape[0] < 8 or value.shape[1] < 8:
        raise ValueError("AM-SPD requires image height and width of at least 8 pixels")
    return value


def _make_core(image: Array, config: AMSpdConfig) -> atlas.ReconstructionResult:
    solver = atlas.InfinitePacketReconstructor(
        image,
        complexity_weight=config.complexity_weight,
        max_candidates_per_iteration=config.max_candidates_per_iteration,
        residual_refresh=config.residual_refresh,
        quadtree_refine_every=config.quadtree_refine_every,
        random_seed=config.random_seed,
    )
    return solver.run(max_packets=config.packet_budget, tolerance=config.tolerance)


def _result(
    image: Array,
    reconstruction: Array,
    selected_method: str,
    parameter_count: int,
    config: AMSpdConfig,
    core_result: atlas.ReconstructionResult,
    *,
    singular_result: singular.SingularPacketResult | None = None,
    lagrange_tree_result: multiscale.AMResult | None = None,
    exact_tree_result: final.ExactTreeResult | None = None,
    portfolios: list[final.FinalPortfolio] | None = None,
    candidate_rmse: dict[str, float] | None = None,
    run_metadata: dict[str, object] | None = None,
) -> AMSpdResult:
    raw = np.asarray(reconstruction, dtype=np.float64)
    residual = image - raw
    return AMSpdResult(
        input_image=image,
        reconstruction=raw,
        archive_residual=residual,
        selected_method=selected_method,
        parameter_count=int(parameter_count),
        packet_count=len(core_result.active_specs),
        metrics=atlas.image_metrics(image, atlas.bounded_synthesis(raw)),
        config=config,
        candidate_rmse=candidate_rmse or {selected_method: final.exact_rmse(image, raw)},
        core_result=core_result,
        singular_result=singular_result,
        lagrange_tree_result=lagrange_tree_result,
        exact_tree_result=exact_tree_result,
        portfolios=portfolios or [],
        run_metadata=run_metadata or {},
    )


def reconstruct_from_core(
    image: Array,
    core_result: atlas.ReconstructionResult,
    config: AMSpdConfig | None = None,
    *,
    run_metadata: dict[str, object] | None = None,
) -> AMSpdResult:
    """Run the selected downstream stages from an existing packet core."""

    settings = config or AMSpdConfig()
    value = _validate_image(image)
    if core_result.reconstruction.shape != value.shape or core_result.residual.shape != value.shape:
        raise ValueError("packet core must match the source image shape")
    for component in (core_result.reconstruction, core_result.residual, core_result.coefficients, *core_result.active_atoms):
        if np.iscomplexobj(component) or not np.isfinite(component).all():
            raise ValueError("packet core arrays must contain finite real values")
    if not np.allclose(core_result.reconstruction + core_result.residual, value, atol=1e-10, rtol=0.0):
        raise ValueError("packet core belongs to a different source image")
    if len(core_result.active_specs) != len(core_result.active_atoms):
        raise ValueError("packet core specification and atom counts differ")
    if not core_result.active_atoms:
        raise ValueError("packet core must contain at least one atom")
    if any(np.asarray(atom).shape != value.shape[:2] for atom in core_result.active_atoms):
        raise ValueError("packet core atom has the wrong spatial shape")
    if np.asarray(core_result.coefficients).shape != (len(core_result.active_atoms), value.shape[2]):
        raise ValueError("packet core coefficient shape does not match atoms and channels")

    metadata = dict(run_metadata or {})
    metadata.setdefault("core_packet_count", len(core_result.active_specs))
    metadata.setdefault("core_coefficient_count", len(core_result.active_specs) * value.shape[2])
    metadata.setdefault("parameter_budget_scope", "core_coefficients" if settings.method == "core" else "downstream_scalar_proxy")

    if settings.method == "core":
        return _result(
            value,
            core_result.reconstruction,
            "core",
            len(core_result.active_specs) * value.shape[2],
            settings,
            core_result,
            run_metadata=metadata,
        )

    spd_result = singular.singular_packet_completion(
        value,
        core_result,
        mode_budget=settings.singular_budget,
        max_depth=max(1, settings.tree_depth + 2),
        max_regions_per_iteration=max(4, settings.max_regions * 2),
        parameter_budget=settings.parameter_budget,
    )
    spd_parameters = int(spd_result.parameter_counts[-1]) if spd_result.parameter_counts else 0
    if settings.method == "spd":
        return _result(
            value,
            spd_result.reconstruction,
            "spd",
            spd_parameters,
            settings,
            core_result,
            singular_result=spd_result,
            run_metadata=metadata,
        )

    parameter_budget = settings.parameter_budget if settings.parameter_budget is not None else spd_parameters
    lagrange_tree = multiscale.tree_result(
        value,
        core_result,
        parameter_budget,
        max_depth=settings.tree_depth,
        max_rank=settings.max_rank,
    )
    exact_tree = final.exact_budget_tree_result(
        value,
        core_result,
        parameter_budget,
        max_depth=settings.tree_depth,
        max_rank=settings.max_rank,
    )
    tree_candidates = {
        "lagrange_tree": final.exact_rmse(value, lagrange_tree.reconstruction),
        "exact_budget_tree": final.exact_rmse(value, exact_tree.reconstruction),
    }
    if settings.method == "tree":
        if tree_candidates["exact_budget_tree"] <= tree_candidates["lagrange_tree"]:
            reconstruction = exact_tree.reconstruction
            selected = "exact_budget_tree"
            parameters = exact_tree.parameter_count
        else:
            reconstruction = lagrange_tree.reconstruction
            selected = "lagrange_tree"
            parameters = lagrange_tree.parameter_count
        return _result(
            value,
            reconstruction,
            selected,
            parameters,
            settings,
            core_result,
            singular_result=spd_result,
            lagrange_tree_result=lagrange_tree,
            exact_tree_result=exact_tree,
            candidate_rmse=tree_candidates,
            run_metadata=metadata,
        )

    seeds: list[tuple[str, Array, list[Array], list[float]]] = [
        (
            "greedy_spd",
            spd_result.reconstruction,
            list(spd_result.directions),
            [float(mode.parameter_count) for mode in spd_result.modes],
        )
    ]
    lagrange_unit_cost = lagrange_tree.parameter_count / max(len(lagrange_tree.directions), 1)
    seeds.append(
        (
            "lagrange_tree",
            lagrange_tree.reconstruction,
            list(lagrange_tree.directions),
            [float(lagrange_unit_cost)] * len(lagrange_tree.directions),
        )
    )
    exact_unit_cost = exact_tree.parameter_count / max(len(exact_tree.directions), 1)
    seeds.append(
        (
            "exact_budget_tree",
            exact_tree.reconstruction,
            list(exact_tree.directions),
            [float(exact_unit_cost)] * len(exact_tree.directions),
        )
    )

    portfolios = [
        final.seed_portfolio(
            "input",
            value,
            core_result,
            seed_name,
            seed_reconstruction,
            seed_directions,
            seed_costs,
            parameter_budget,
            settings.reopen_fractions,
            settings.max_actions,
            settings.max_rank,
            settings.max_regions,
        )
        for seed_name, seed_reconstruction, seed_directions, seed_costs in seeds
    ]
    best = min(
        portfolios,
        key=lambda portfolio: (final.exact_rmse(value, portfolio.reconstruction), portfolio.parameter_count),
    )
    for trial in best.trials:
        if trial.selected_within_seed:
            trial.selected_final = True
    return _result(
        value,
        best.reconstruction,
        f"portfolio:{best.seed}",
        best.parameter_count,
        settings,
        core_result,
        singular_result=spd_result,
        lagrange_tree_result=lagrange_tree,
        exact_tree_result=exact_tree,
        portfolios=portfolios,
        candidate_rmse={
            portfolio.seed: final.exact_rmse(value, portfolio.reconstruction) for portfolio in portfolios
        },
        run_metadata=metadata,
    )


def reconstruct(image: Array, config: AMSpdConfig | None = None) -> AMSpdResult:
    settings = config or AMSpdConfig()
    value = _validate_image(image)
    return reconstruct_from_core(value, _make_core(value, settings), settings)


def config_from_mapping(mapping: dict[str, object], *, method: Method | None = None) -> AMSpdConfig:
    """Create a validated configuration from model metadata."""

    allowed = {
        "method",
        "packet_budget",
        "singular_budget",
        "parameter_budget",
        "tree_depth",
        "max_rank",
        "reopen_fractions",
        "max_actions",
        "max_regions",
        "random_seed",
        "complexity_weight",
        "max_candidates_per_iteration",
        "residual_refresh",
        "quadtree_refine_every",
        "tolerance",
    }
    values: dict[str, Any] = {key: value for key, value in mapping.items() if key in allowed}
    if "reopen_fractions" in values:
        values["reopen_fractions"] = tuple(float(value) for value in values["reopen_fractions"])
    if method is not None:
        values["method"] = method
    return AMSpdConfig(**values)


def resume_model(
    model: object,
    config: AMSpdConfig | None = None,
    *,
    additional_packets: int = 8,
    target_packet_budget: int | None = None,
    method: Method | None = None,
) -> AMSpdResult:
    """Continue a saved packet search and rerun its downstream stages."""

    from .model import AMSpdModel

    loaded = AMSpdModel.load(model) if isinstance(model, (str, Path)) else model
    if not isinstance(loaded, AMSpdModel):
        raise TypeError("model must be an AMSpdModel or a path to one")
    if not loaded.supports_resume:
        raise ValueError("model cannot be resumed; retain core atoms and exact source data when saving")
    for name, number in (("additional_packets", additional_packets), ("target_packet_budget", target_packet_budget)):
        if number is not None and (isinstance(number, (bool, np.bool_)) or not isinstance(number, Integral) or number < 0):
            raise ValueError(f"{name} must be a nonnegative integer")
    if target_packet_budget is None and additional_packets < 1:
        raise ValueError("additional_packets must be at least 1 when no target packet budget is supplied")

    value = _validate_image(loaded.source_image())
    original_settings = config_from_mapping(loaded.config)
    settings = config or original_settings
    if method is not None:
        settings = replace(settings, method=method)
    changed_search_settings = any(
        getattr(settings, name) != getattr(original_settings, name)
        for name in (
            "complexity_weight",
            "max_candidates_per_iteration",
            "residual_refresh",
            "quadtree_refine_every",
            "random_seed",
            "tolerance",
        )
    )
    current_packets = len(loaded.packet_specs)
    target = target_packet_budget if target_packet_budget is not None else current_packets + additional_packets
    if target <= current_packets:
        raise ValueError(f"target packet budget must exceed the saved count ({current_packets})")
    settings = replace(settings, packet_budget=int(target))

    solver = atlas.InfinitePacketReconstructor.from_reconstruction_result(
        value,
        loaded.to_core_result(value),
        complexity_weight=settings.complexity_weight,
        max_candidates_per_iteration=settings.max_candidates_per_iteration,
        residual_refresh=settings.residual_refresh,
        quadtree_refine_every=settings.quadtree_refine_every,
        random_seed=settings.random_seed,
    )
    continued_core = solver.run(max_packets=settings.packet_budget, tolerance=settings.tolerance)
    return reconstruct_from_core(
        value,
        continued_core,
        settings,
        run_metadata={
            "operation": "resume",
            "source_schema_version": loaded.schema_version,
            "resume_state_quality": loaded.resume_state_quality,
            "saved_packet_count": current_packets,
            "target_packet_budget": settings.packet_budget,
            "packets_added": len(continued_core.active_specs) - current_packets,
            "search_parameters_overridden": changed_search_settings,
            "uninterrupted_equivalence_expected": (
                loaded.resume_state_quality == "exact" and not changed_search_settings
            ),
        },
    )
