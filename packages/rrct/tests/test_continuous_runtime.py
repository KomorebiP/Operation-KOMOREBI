from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

import pytest

from rrct_lab.config import DEFAULT_CONFIG
from rrct_lab.exceptions import RRCTLabError
from rrct_lab.runner import run_config


def _base(output_root: Path, name: str) -> dict:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["safety"]["allowed_output_root"] = str(output_root)
    config["run"].update(
        {
            "name": name,
            "seed": 590913,
            "output_root": str(output_root),
            "overwrite": True,
            "make_plots": True,
            "strict_feature_contract": True,
            "fail_on_unused_setting": True,
        }
    )
    config["experiment"].update(
        {
            "family": "continuous_open_set_runtime",
            "agent_count": 4,
            "action_dim": 4,
        }
    )
    config["features"].update(
        {
            "fuzzy_packets": True,
            "dynamic_formation": True,
            "cost_regularization": True,
            "continuous_event_fabric": True,
            "open_set_change_detection": True,
            "dynamic_packet_birth": True,
            "dynamic_packet_death": True,
            "self_model_repair": True,
            "memory_quarantine": True,
        }
    )
    config["workspace"].update(
        {
            "allow_new_packets": True,
            "max_packets": 5,
            "birth_threshold": 0.40,
            "death_threshold": 0.10,
        }
    )
    config["continuous"].update(
        {
            "steps": 8,
            "calibration_steps": 2,
            "event_interval": 4,
            "task_switch_interval": 4,
            "checkpoint_interval": 2,
            "checkpoint_state_rows": 16,
        }
    )
    return config


def _semantic_metrics(summary: dict) -> dict:
    ignored = {"wall_time_seconds", "peak_python_memory_mb"}
    return {key: value for key, value in summary["metrics"].items() if key not in ignored}


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_continuous_resume_matches_uninterrupted_run(tmp_path: Path) -> None:
    staged = _base(tmp_path, "staged")
    staged["continuous"]["invocation_step_limit"] = 4
    first = run_config(staged)[0]
    staged_dir = Path(first["run_directory"])
    assert first["status"] == "interrupted"
    assert first["metrics"]["episodes_completed"] == 4

    resolved = json.loads((staged_dir / "resolved_config.json").read_text(encoding="utf-8"))
    resolved["run"]["resume"] = True
    resumed = run_config(resolved, resume_directory=staged_dir)[0]
    assert resumed["status"] == "completed"
    assert resumed["metadata"]["resumed"] is True
    assert resumed["metadata"]["resume_count"] == 1

    full = _base(tmp_path, "full")
    full["continuous"]["invocation_step_limit"] = 0
    uninterrupted = run_config(full)[0]
    full_dir = Path(uninterrupted["run_directory"])

    assert _semantic_metrics(resumed) == _semantic_metrics(uninterrupted)
    assert resumed["metadata"]["trajectory_digest"] == uninterrupted["metadata"]["trajectory_digest"]
    assert _rows(staged_dir / "rows.csv") == _rows(full_dir / "rows.csv")
    run_state = json.loads((staged_dir / "run_state.json").read_text(encoding="utf-8"))
    assert run_state["status"] == "completed"
    assert run_state["step"] == 8
    assert run_state["resume_count"] == 1


def test_calibration_window_changes_event_schedule(tmp_path: Path) -> None:
    config = _base(tmp_path, "calibration")
    config["continuous"]["steps"] = 12
    config["continuous"]["calibration_steps"] = 5
    config["continuous"]["invocation_step_limit"] = 0
    summary = run_config(config)[0]
    segments = summary["metadata"]["segments"]
    assert segments[0]["start"] == 0
    assert segments[0]["stop"] == 5
    assert segments[0]["event"] == "none"


def test_completed_resume_rejects_changed_configuration(tmp_path: Path) -> None:
    config = _base(tmp_path, "completed_digest")
    completed = run_config(config)[0]
    run_dir = Path(completed["run_directory"])
    assert completed["status"] == "completed"

    changed = json.loads((run_dir / "resolved_config.json").read_text(encoding="utf-8"))
    changed["run"]["resume"] = True
    changed["continuous"]["change_threshold"] = 0.25
    with pytest.raises(RRCTLabError, match="configuration digest"):
        run_config(changed, resume_directory=run_dir)
