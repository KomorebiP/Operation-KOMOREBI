from __future__ import annotations

import copy
import csv
import json
import math
from pathlib import Path

import pytest

from rrct_lab.config import DEFAULT_CONFIG
from rrct_lab.experiments import fuzzy_j
from rrct_lab.runner import run_config


def _config(
    *,
    seed: int = 601001,
    steps: int = 32,
    calibration_steps: int = 12,
) -> dict:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["run"].update(
        {
            "name": "fuzzy_j_test",
            "seed": seed,
            "save_rows": True,
            "overwrite": True,
            "strict_feature_contract": True,
            "fail_on_unused_setting": True,
        }
    )
    config["runtime"]["device"] = "cpu"
    config["experiment"]["family"] = "persistent_fuzzy_j_workspace"
    config["features"].update(
        {
            "fuzzy_packets": True,
            "dynamic_formation": True,
            "cost_regularization": True,
            "jacobian_workspace": True,
            "moving_j_lens": True,
            "sparse_cone": True,
        }
    )
    config["jspace"].update(
        {
            "residual_dimension": 8,
            "frame_rank": 4,
            "active_directions": 2,
            "steps": steps,
            "calibration_steps": calibration_steps,
            "event_interval": 4,
            "moving_rate": 0.20,
            "gate_learning_rate": 0.08,
            "readout_learning_rate": 0.05,
            "ridge": 0.001,
            "spectral_ratio": 0.0001,
            "ignition_threshold": 0.05,
            "access_hysteresis": 0.02,
            "random_baselines": 2,
            "checkpoint_interval": 4,
            "invocation_step_limit": 0,
        }
    )
    return config


def _semantic_metrics(summary: dict) -> dict:
    ignored = {"wall_time_seconds", "peak_python_memory_mb"}
    return {
        key: value
        for key, value in summary["metrics"].items()
        if key not in ignored
    }


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_fuzzy_j_completion_and_geometric_invariants() -> None:
    result = fuzzy_j.run(_config())
    assert result.status == "completed"
    assert result.family == "persistent_fuzzy_j_workspace"
    assert result.metrics["episodes_completed"] == 32
    assert result.metrics["run_complete"] is True
    assert result.metrics["jspace_rank"] == 4
    assert result.metrics["mean_active_directions"] <= 2.0
    assert 0.0 <= result.metrics["jspace_jacobian_energy_capture"] <= 1.0
    assert 0.0 <= result.metrics["jspace_activation_variance_fraction"] <= 1.0
    assert result.metrics["jspace_projector_idempotence_defect"] < 1e-10
    assert result.metrics["task_event_dependence"] == 0.0
    assert isinstance(result.metrics["longest_supported_prefix"], str)
    assert 0 <= result.metrics["supported_prefix_length"] <= 5
    assert result.metadata["controller_hidden_truth_access"] is False
    assert "terminal consumer loss" in result.metadata["membership_supervision"]
    assert result.warnings
    for value in result.metrics.values():
        if isinstance(value, float):
            assert math.isfinite(value)


def test_fuzzy_j_is_deterministic() -> None:
    first = fuzzy_j.run(_config(seed=601137))
    second = fuzzy_j.run(_config(seed=601137))
    assert first.metrics == second.metrics
    assert first.rows == second.rows
    assert (
        first.metadata["trajectory_digest"]
        == second.metadata["trajectory_digest"]
    )


def test_fuzzy_j_exact_resume_matches_uninterrupted(
    tmp_path: Path,
) -> None:
    staged = _config(seed=601211, steps=24, calibration_steps=8)
    staged["safety"]["allowed_output_root"] = str(tmp_path)
    staged["run"].update(
        {
            "name": "fuzzy_j_staged",
            "output_root": str(tmp_path),
        }
    )
    staged["jspace"]["invocation_step_limit"] = 12
    first = run_config(staged)[0]
    staged_dir = Path(first["run_directory"])
    assert first["status"] == "interrupted"
    assert first["metrics"]["episodes_completed"] == 12

    resolved = json.loads(
        (staged_dir / "resolved_config.json").read_text(encoding="utf-8")
    )
    resolved["run"]["resume"] = True
    resumed = run_config(resolved, resume_directory=staged_dir)[0]
    assert resumed["status"] == "completed"
    assert resumed["metadata"]["resumed"] is True

    full = _config(seed=601211, steps=24, calibration_steps=8)
    full["safety"]["allowed_output_root"] = str(tmp_path)
    full["run"].update(
        {
            "name": "fuzzy_j_full",
            "output_root": str(tmp_path),
        }
    )
    uninterrupted = run_config(full)[0]
    full_dir = Path(uninterrupted["run_directory"])

    assert _semantic_metrics(resumed) == _semantic_metrics(uninterrupted)
    assert (
        resumed["metadata"]["trajectory_digest"]
        == uninterrupted["metadata"]["trajectory_digest"]
    )
    assert _rows(staged_dir / "rows.csv") == _rows(full_dir / "rows.csv")
    staged_state = json.loads(
        (staged_dir / "checkpoints" / "latest.json").read_text(
            encoding="utf-8"
        )
    )["state"]
    full_state = json.loads(
        (full_dir / "checkpoints" / "latest.json").read_text(
            encoding="utf-8"
        )
    )["state"]
    assert staged_state == full_state


def test_fuzzy_j_causal_ladder_raw_signs() -> None:
    intact_config = _config(steps=48, calibration_steps=24)
    intact = fuzzy_j.run(intact_config)
    metrics = intact.metrics
    assert metrics["jspace_ablation_drop"] > 0.0
    assert metrics["provenance_plan_drop"] > 0.0
    assert metrics["routine_preservation_under_jspace_cut"] == pytest.approx(1.0)
    assert metrics["code_preservation_under_broadcast_cut"] == pytest.approx(1.0)
    assert metrics["report_preservation_under_provenance_cut"] == pytest.approx(1.0)
    assert metrics["feedback_cut_first_pass_preservation"] == pytest.approx(1.0)

    jcut_config = copy.deepcopy(intact_config)
    jcut_config["interventions"]["jspace_cut"] = True
    jcut = fuzzy_j.run(jcut_config)
    assert jcut.metrics["mean_jspace_code_norm"] > 0.0
    assert jcut.metrics["mean_effective_jspace_code_norm"] == 0.0
    assert jcut.metrics["membership_upstream_preservation"] == pytest.approx(1.0)
    assert jcut.metrics["jspace_upstream_preservation"] == pytest.approx(0.0)

    broadcast_config = copy.deepcopy(intact_config)
    broadcast_config["interventions"]["broadcast_cut"] = True
    broadcast = fuzzy_j.run(broadcast_config)
    assert broadcast.metrics["mean_effective_jspace_code_norm"] > 0.0
    assert broadcast.metrics["jspace_upstream_preservation"] == pytest.approx(1.0)
    assert broadcast.metrics["workspace_decodability"] < metrics["workspace_decodability"]

    feedback_config = copy.deepcopy(intact_config)
    feedback_config["interventions"]["feedback_cut"] = True
    feedback = fuzzy_j.run(feedback_config)
    assert feedback.metrics["feedback_cut_first_pass_preservation"] == pytest.approx(1.0)
    assert feedback.metrics["recurrence_reopen_rate"] < metrics["recurrence_reopen_rate"]

    shuffled_config = copy.deepcopy(intact_config)
    shuffled_config["interventions"]["membership_shuffle"] = True
    shuffled = fuzzy_j.run(shuffled_config)
    assert shuffled.metrics["membership_upstream_preservation"] < 1.0
