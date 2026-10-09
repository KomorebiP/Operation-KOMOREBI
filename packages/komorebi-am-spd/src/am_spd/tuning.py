from __future__ import annotations

import csv
import json
import math
import time
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, replace
from numbers import Integral, Real
from pathlib import Path
from typing import Literal

import numpy as np

from . import atlas
from .api import AMSpdConfig, AMSpdResult, reconstruct_from_core
from .components import fit_packet_core

Objective = Literal["rate-distortion", "ssim-rate", "rmse", "target-rmse"]


@dataclass(frozen=True)
class TuningRecord:
    index: int
    method: str
    packet_budget: int
    singular_budget: int
    tree_depth: int
    max_rank: int
    runtime_seconds: float
    selected_method: str
    packet_count: int
    parameter_count: int
    parameter_density: float
    rmse: float
    ssim: float
    score: float
    feasible: bool
    core_cache_hit: bool


@dataclass
class AutoTuneResult:
    best_result: AMSpdResult
    best_config: AMSpdConfig
    records: list[TuningRecord]
    objective: Objective
    rate_weight: float
    target_rmse: float | None
    max_parameters: int | None

    def summary(self) -> dict[str, object]:
        records = [asdict(record) for record in self.records]
        for record in records:
            if not math.isfinite(record["score"]):
                record["score"] = None
        best_summary = self.best_result.summary()
        metadata = best_summary["run_metadata"]
        if "score" in metadata and not math.isfinite(metadata["score"]):
            metadata["score"] = None
        return {
            "operation": "automatic-budget-selection",
            "objective": self.objective,
            "rate_weight": self.rate_weight,
            "target_rmse": self.target_rmse,
            "max_parameters": self.max_parameters,
            "best_config": asdict(self.best_config),
            "best_result": best_summary,
            "records": records,
        }

    def save_report(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.summary(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return destination

    def save_csv(self, path: str | Path) -> Path:
        """Write one row per evaluated configuration."""

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(TuningRecord.__dataclass_fields__)
        with destination.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(asdict(record) for record in self.records)
        return destination


def _integer_grid(values: Iterable[int], name: str, minimum: int = 0) -> tuple[int, ...]:
    declared = tuple(values)
    if not declared:
        raise ValueError(f"{name} must contain at least one value")
    if any(isinstance(value, bool) or not isinstance(value, Integral) or value < minimum for value in declared):
        raise ValueError(f"{name} must contain integers at least {minimum}")
    return tuple(dict.fromkeys(int(value) for value in declared))


def tuning_candidates(
    base: AMSpdConfig | None = None,
    *,
    methods: Iterable[str] = ("core", "spd", "tree", "portfolio"),
    packet_budgets: Sequence[int] = (8, 12, 16),
    singular_budgets: Sequence[int] | None = None,
    tree_depths: Sequence[int] | None = None,
    max_ranks: Sequence[int] | None = None,
) -> list[AMSpdConfig]:
    """Construct a bounded configuration grid suitable for local tuning.

    When singular budgets, tree depths, or ranks are omitted, each packet budget
    receives one proportionate setting. Supplying explicit sequences creates a
    Cartesian grid over those values.
    """

    template = base or AMSpdConfig.quick()
    method_values = tuple(dict.fromkeys(str(method) for method in methods))
    if not method_values:
        raise ValueError("at least one method is required")
    if any(method not in {"core", "spd", "tree", "portfolio"} for method in method_values):
        raise ValueError("methods must be core, spd, tree, or portfolio")
    packets = _integer_grid(packet_budgets, "packet budgets", minimum=1)
    singular_grid = _integer_grid(singular_budgets, "singular budgets") if singular_budgets is not None else None
    depth_grid = _integer_grid(tree_depths, "tree depths") if tree_depths is not None else None
    rank_grid = _integer_grid(max_ranks, "max ranks") if max_ranks is not None else None

    candidates: list[AMSpdConfig] = []
    for packet_budget in packets:
        singular_values = singular_grid if singular_grid is not None else (max(1, packet_budget // 2),)
        depth_values = depth_grid if depth_grid is not None else (template.tree_depth,)
        rank_values = rank_grid if rank_grid is not None else (template.max_rank,)
        for method in method_values:
            for singular_budget in singular_values:
                for tree_depth in depth_values:
                    for max_rank in rank_values:
                        candidates.append(
                            replace(
                                template,
                                method=method,  # type: ignore[arg-type]
                                packet_budget=packet_budget,
                                singular_budget=singular_budget,
                                tree_depth=tree_depth,
                                max_rank=max_rank,
                            )
                        )
    # Preserve declaration order while removing duplicate dataclass values.
    return list(dict.fromkeys(candidates))


def _score(
    result: AMSpdResult,
    *,
    objective: Objective,
    rate_weight: float,
    scalar_count: int,
    target_rmse: float | None,
    max_parameters: int | None,
) -> tuple[float, bool]:
    rmse = float(result.metrics["rmse"])
    ssim = float(result.metrics["ssim"])
    density = result.parameter_count / max(scalar_count, 1)
    feasible = max_parameters is None or result.parameter_count <= max_parameters
    if objective == "target-rmse":
        if target_rmse is None:
            raise ValueError("target-rmse objective requires target_rmse")
        feasible = feasible and rmse <= target_rmse
        # Feasible candidates are ordered by storage, then error. Infeasible
        # candidates retain a finite diagnostic score for the report.
        return (density if feasible else 1e6 + rmse), feasible
    if not feasible:
        return float("inf"), False
    if objective == "rmse":
        return rmse, True
    if objective == "ssim-rate":
        return (1.0 - ssim) + rate_weight * density, True
    if objective == "rate-distortion":
        return rmse * rmse + rate_weight * density, True
    raise ValueError(f"unsupported tuning objective: {objective}")


def auto_tune(
    image,
    candidates: Sequence[AMSpdConfig] | None = None,
    *,
    objective: Objective = "rate-distortion",
    rate_weight: float = 0.01,
    target_rmse: float | None = None,
    max_parameters: int | None = None,
) -> AutoTuneResult:
    """Evaluate a finite AM-SPD configuration set and select one deterministically."""

    if objective not in {"rate-distortion", "ssim-rate", "rmse", "target-rmse"}:
        raise ValueError(f"unsupported tuning objective: {objective}")
    if (
        isinstance(rate_weight, bool)
        or not isinstance(rate_weight, Real)
        or not math.isfinite(rate_weight)
        or rate_weight < 0
    ):
        raise ValueError("rate_weight must be finite and nonnegative")
    if target_rmse is not None and (
        isinstance(target_rmse, bool)
        or not isinstance(target_rmse, Real)
        or not math.isfinite(target_rmse)
        or target_rmse < 0
    ):
        raise ValueError("target_rmse must be finite and nonnegative")
    if objective == "target-rmse" and target_rmse is None:
        raise ValueError("target-rmse objective requires target_rmse")
    if max_parameters is not None and (
        isinstance(max_parameters, bool) or not isinstance(max_parameters, Integral) or max_parameters < 0
    ):
        raise ValueError("max_parameters must be a nonnegative integer")
    rate_weight = float(rate_weight)
    target_rmse = float(target_rmse) if target_rmse is not None else None
    max_parameters = int(max_parameters) if max_parameters is not None else None
    value = atlas.ensure_image(image)
    search = list(tuning_candidates() if candidates is None else candidates)
    if not search:
        raise ValueError("at least one tuning candidate is required")
    if any(not isinstance(config, AMSpdConfig) for config in search):
        raise TypeError("each tuning candidate must be an AMSpdConfig")

    records: list[TuningRecord] = []
    results: list[AMSpdResult] = []
    scalar_count = int(np.prod(value.shape))
    core_cache: dict[tuple[object, ...], object] = {}
    for index, config in enumerate(search):
        started = time.perf_counter()
        core_key = (
            config.packet_budget,
            config.random_seed,
            config.complexity_weight,
            config.max_candidates_per_iteration,
            config.residual_refresh,
            config.quadtree_refine_every,
            config.tolerance,
        )
        core_cache_hit = core_key in core_cache
        core = core_cache.get(core_key)
        if core is None:
            core = fit_packet_core(value, config)
            core_cache[core_key] = core
        result = reconstruct_from_core(
            value,
            core,
            config,
            run_metadata={
                "operation": "automatic-budget-selection-candidate",
                "candidate_index": index,
                "core_cache_hit": core_cache_hit,
            },
        )
        runtime = time.perf_counter() - started
        score, feasible = _score(
            result,
            objective=objective,
            rate_weight=rate_weight,
            scalar_count=scalar_count,
            target_rmse=target_rmse,
            max_parameters=max_parameters,
        )
        result.run_metadata.update(
            {
                "operation": "automatic-budget-selection-candidate",
                "candidate_index": index,
                "core_cache_hit": core_cache_hit,
                "objective": objective,
                "score": score,
                "feasible": feasible,
            }
        )
        records.append(
            TuningRecord(
                index=index,
                method=config.method,
                packet_budget=config.packet_budget,
                singular_budget=config.singular_budget,
                tree_depth=config.tree_depth,
                max_rank=config.max_rank,
                runtime_seconds=runtime,
                selected_method=result.selected_method,
                packet_count=result.packet_count,
                parameter_count=result.parameter_count,
                parameter_density=result.parameter_count / max(scalar_count, 1),
                rmse=float(result.metrics["rmse"]),
                ssim=float(result.metrics["ssim"]),
                score=float(score),
                feasible=feasible,
                core_cache_hit=core_cache_hit,
            )
        )
        results.append(result)

    feasible_indices = [index for index, record in enumerate(records) if record.feasible]
    if feasible_indices:
        selected_index = min(
            feasible_indices,
            key=lambda index: (
                records[index].score,
                records[index].parameter_count,
                records[index].rmse,
                records[index].index,
            ),
        )
    else:
        # No candidate met the declared constraint. Return the least-distorted
        # result while preserving the infeasible ledger rather than failing
        # after all expensive runs have completed.
        selected_index = min(
            range(len(records)),
            key=lambda index: (
                records[index].rmse,
                records[index].parameter_count,
                records[index].index,
            ),
        )
    best = results[selected_index]
    best.run_metadata.update(
        {
            "operation": "automatic-budget-selection",
            "selected_candidate_index": selected_index,
            "objective": objective,
            "rate_weight": rate_weight,
            "target_rmse": target_rmse,
            "max_parameters": max_parameters,
            "candidate_count": len(records),
            "constraint_satisfied": records[selected_index].feasible,
        }
    )
    return AutoTuneResult(
        best_result=best,
        best_config=search[selected_index],
        records=records,
        objective=objective,
        rate_weight=float(rate_weight),
        target_rmse=target_rmse,
        max_parameters=max_parameters,
    )
