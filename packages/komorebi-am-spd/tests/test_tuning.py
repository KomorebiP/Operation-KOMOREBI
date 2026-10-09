from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path

from am_spd import AMSpdConfig, auto_tune, tuning_candidates
from am_spd.atlas import synthetic_geometry


def base() -> AMSpdConfig:
    return AMSpdConfig(
        method="core",
        packet_budget=2,
        singular_budget=1,
        tree_depth=1,
        max_rank=1,
        max_actions=1,
        max_regions=3,
        max_candidates_per_iteration=24,
        tolerance=0.0,
    )


def test_finite_budget_tuning_selects_declared_candidate(tmp_path: Path) -> None:
    image = synthetic_geometry(10)
    candidates = tuning_candidates(
        base(),
        methods=("core",),
        packet_budgets=(2, 3, 4),
        singular_budgets=(1,),
        tree_depths=(1,),
        max_ranks=(1,),
    )
    tuned = auto_tune(image, candidates, objective="rmse")

    assert len(tuned.records) == 3
    assert tuned.best_config in candidates
    assert tuned.best_result.exact_identity_error <= 1e-12
    assert min(record.score for record in tuned.records) == next(
        record.score for record in tuned.records if record.index == tuned.best_result.run_metadata["selected_candidate_index"]
    )

    report = tuned.save_report(tmp_path / "tuning.json")
    ledger = tuned.save_csv(tmp_path / "tuning.csv")
    assert json.loads(report.read_text())["records"]
    with ledger.open(newline="", encoding="utf-8") as handle:
        assert len(list(csv.DictReader(handle))) == 3


def test_target_rmse_constraint_records_infeasible_search() -> None:
    image = synthetic_geometry(10)
    candidates = [replace(base(), packet_budget=2), replace(base(), packet_budget=3)]
    tuned = auto_tune(image, candidates, objective="target-rmse", target_rmse=0.0)
    assert tuned.best_result.run_metadata["constraint_satisfied"] is False
    assert all(record.feasible is False for record in tuned.records)


def test_tuning_reuses_packet_core_across_downstream_methods() -> None:
    image = synthetic_geometry(10)
    candidates = tuning_candidates(
        base(),
        methods=("core", "spd"),
        packet_budgets=(3,),
        singular_budgets=(1,),
        tree_depths=(1,),
        max_ranks=(1,),
    )
    tuned = auto_tune(image, candidates, objective="rmse")
    assert tuned.records[0].core_cache_hit is False
    assert tuned.records[1].core_cache_hit is True
