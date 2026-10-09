from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from am_spd import AMSpdConfig, TiledConfig, auto_tune, batch, run_batch, tuning, tuning_candidates
from am_spd.io import save_image


def small_config() -> AMSpdConfig:
    return AMSpdConfig(method="core", packet_budget=1, max_candidates_per_iteration=8, tolerance=0.0)


def make_input(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "inputs"
    source.mkdir()
    save_image(source / "one.png", np.linspace(0.0, 1.0, 64).reshape(8, 8, 1))
    return source, tmp_path / "outputs"


def test_same_stem_batch_inputs_fail_before_writing(tmp_path: Path) -> None:
    source, output = make_input(tmp_path)
    save_image(source / "one.jpg", np.ones((8, 8, 1)))
    with pytest.raises(ValueError, match="collision"):
        run_batch(source, output, small_config(), workers=2)
    assert not output.exists()


def test_nested_batch_output_is_excluded_from_recursive_restarts(tmp_path: Path) -> None:
    source, _ = make_input(tmp_path)
    output = source / "results"
    first = run_batch(source, output, small_config())
    second = run_batch(source, output, small_config(), skip_existing=True)
    assert len(first.records) == len(second.records) == 1
    assert second.records[0].status == "skipped"


def test_batch_directory_output_must_differ_from_source(tmp_path: Path) -> None:
    source, _ = make_input(tmp_path)
    with pytest.raises(ValueError, match="differ"):
        run_batch(source, source, small_config())


@pytest.mark.parametrize("tiled", [False, True])
def test_batch_restart_rebuilds_missing_requested_model(tmp_path: Path, tiled: bool) -> None:
    source, output = make_input(tmp_path)
    options = {"tile_config": TiledConfig(tile_size=8, overlap=0)} if tiled else {}
    first = run_batch(source, output, small_config(), save_models=True, **options)
    Path(first.records[0].model).unlink()
    second = run_batch(source, output, small_config(), save_models=True, skip_existing=True, **options)
    assert second.records[0].status == "completed"
    assert Path(second.records[0].model).is_file()


def test_batch_restart_fingerprint_includes_library_version(tmp_path: Path, monkeypatch) -> None:
    source, output = make_input(tmp_path)
    first = run_batch(source, output, small_config())
    monkeypatch.setattr(batch, "__version__", "next-release", raising=False)
    second = run_batch(source, output, small_config(), skip_existing=True)
    assert second.run_fingerprint != first.run_fingerprint
    assert second.records[0].status == "completed"


def test_batch_restart_does_not_report_an_unrequested_stale_model(tmp_path: Path) -> None:
    source, output = make_input(tmp_path)
    run_batch(source, output, small_config(), save_models=True)
    run_batch(source, output, small_config())
    resumed = run_batch(source, output, small_config(), skip_existing=True)
    assert resumed.records[0].status == "skipped"
    assert resumed.records[0].model is None


def test_batch_source_read_failure_is_recorded(tmp_path: Path, monkeypatch) -> None:
    source, output = make_input(tmp_path)

    def cannot_read(path):
        raise OSError("source became unreadable")

    monkeypatch.setattr(batch, "_sha256_file", cannot_read)
    result = run_batch(source, output, small_config())
    assert result.passed is False
    assert result.records[0].status == "failed"
    assert "source became unreadable" in result.records[0].error


def test_batch_restart_rebuilds_malformed_summary_mode(tmp_path: Path) -> None:
    source, output = make_input(tmp_path)
    first = run_batch(source, output, small_config())
    summary_path = Path(first.records[0].summary)
    summary = json.loads(summary_path.read_text())
    summary["batch"]["mode"] = []
    summary_path.write_text(json.dumps(summary))
    resumed = run_batch(source, output, small_config(), skip_existing=True)
    assert resumed.records[0].status == "completed"


@pytest.mark.parametrize("field,value", [("workers", 1.5), ("workers", True), ("tiled_above", 8.5)])
def test_batch_rejects_fractional_integer_controls(tmp_path: Path, field: str, value) -> None:
    source, output = make_input(tmp_path)
    with pytest.raises(ValueError, match="integer"):
        run_batch(source, output, small_config(), **{field: value})


@pytest.mark.parametrize("field", ["packet_budgets", "singular_budgets", "tree_depths", "max_ranks"])
def test_tuning_grid_rejects_fractional_values(field: str) -> None:
    with pytest.raises(ValueError, match="integers"):
        tuning_candidates(small_config(), methods=("core",), **{field: (1.5,)})


@pytest.mark.parametrize("field", ["packet_budgets", "singular_budgets", "tree_depths", "max_ranks"])
def test_tuning_grid_rejects_empty_dimensions(field: str) -> None:
    with pytest.raises(ValueError, match="at least one"):
        tuning_candidates(small_config(), methods=("core",), **{field: ()})


@pytest.mark.parametrize("field", ["rate_weight", "target_rmse"])
@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_tuning_rejects_nonfinite_objective_parameters(field: str, value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        auto_tune(np.ones((8, 8, 1)), [small_config()], **{field: value})


def test_empty_tuning_candidates_do_not_trigger_a_default_search(monkeypatch) -> None:
    def unexpected_default_search():
        raise AssertionError("explicitly empty candidates must remain empty")

    monkeypatch.setattr(tuning, "tuning_candidates", unexpected_default_search)
    with pytest.raises(ValueError, match="at least one"):
        auto_tune(np.ones((8, 8, 1)), [])


def test_tuning_uses_candidate_order_for_exact_ties() -> None:
    config = small_config()
    tuned = auto_tune(np.ones((8, 8, 1)), [config, config], objective="rmse")
    assert tuned.records[0].rmse == tuned.records[1].rmse
    assert tuned.best_result.run_metadata["selected_candidate_index"] == 0


def test_target_rmse_score_orders_storage_before_error() -> None:
    cheaper = SimpleNamespace(metrics={"rmse": 0.9, "ssim": 0.0}, parameter_count=10)
    dearer = SimpleNamespace(metrics={"rmse": 0.0, "ssim": 1.0}, parameter_count=11)
    options = dict(objective="target-rmse", rate_weight=0.01, scalar_count=100000, target_rmse=1.0, max_parameters=None)
    assert tuning._score(cheaper, **options)[0] < tuning._score(dearer, **options)[0]


def test_infeasible_tuning_scores_are_null_in_json_report(tmp_path: Path) -> None:
    tuned = auto_tune(np.ones((8, 8, 1)), [replace(small_config(), packet_budget=2)], max_parameters=0)
    assert tuned.records[0].score == float("inf")
    report = tuned.save_report(tmp_path / "tuning.json")
    summary = json.loads(report.read_text())
    assert summary["records"][0]["score"] is None
    assert summary["best_result"]["run_metadata"]["score"] is None
    assert summary["records"][0]["feasible"] is False
