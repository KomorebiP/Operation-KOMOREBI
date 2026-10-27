from __future__ import annotations

import copy
import json

from rrct_lab.config import DEFAULT_CONFIG
from rrct_lab.contracts import audit_config, enforce_contract
from rrct_lab.experiments.continuous import run as run_continuous
from rrct_lab.orchestration import RunContext


def continuous_config() -> dict:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["experiment"]["family"] = "continuous_open_set_runtime"
    config["experiment"]["agent_count"] = 4
    config["run"]["save_rows"] = True
    config["run"]["make_plots"] = False
    config["continuous"]["steps"] = 24
    config["continuous"]["calibration_steps"] = 3
    config["continuous"]["event_interval"] = 4
    config["continuous"]["checkpoint_interval"] = 4
    config["continuous"]["checkpoint_state_rows"] = 32
    config["workspace"]["allow_new_packets"] = True
    for key in (
        "fuzzy_packets",
        "dynamic_formation",
        "continuous_event_fabric",
        "open_set_change_detection",
        "dynamic_packet_birth",
        "dynamic_packet_death",
        "self_model_repair",
        "memory_quarantine",
    ):
        config["features"][key] = True
    return config


def test_continuous_contract_has_no_unsupported_nondefault() -> None:
    config = continuous_config()
    report = audit_config(config)
    assert report["unknown_keys"] == []
    assert report["unsupported_nondefault"] == []
    enforce_contract(config)


def test_continuous_runtime_is_finite_and_complete() -> None:
    result = run_continuous(continuous_config())
    assert result.status == "completed"
    assert result.metrics["episodes_completed"] == 24
    assert result.metrics["run_complete"] is True
    assert all(
        not isinstance(value, float) or value == value
        for value in result.metrics.values()
    )


def test_checkpoint_resume_matches_uninterrupted(tmp_path) -> None:
    interrupted = continuous_config()
    interrupted["continuous"]["invocation_step_limit"] = 12
    run_dir = tmp_path / "resumed"
    context_1 = RunContext.create(run_dir, interrupted)
    first = run_continuous(interrupted, context=context_1)
    assert first.status == "interrupted"

    resumed = copy.deepcopy(interrupted)
    resumed["run"]["resume"] = True
    context_2 = RunContext.create(run_dir, resumed)
    second = run_continuous(resumed, context=context_2)
    assert second.status == "completed"

    complete = continuous_config()
    full_dir = tmp_path / "full"
    context_3 = RunContext.create(full_dir, complete)
    third = run_continuous(complete, context=context_3)
    assert third.status == "completed"

    assert second.metrics == third.metrics
    assert second.rows == third.rows
    resumed_state = json.loads((run_dir / "checkpoints/latest.json").read_text())["state"]
    full_state = json.loads((full_dir / "checkpoints/latest.json").read_text())["state"]
    assert resumed_state == full_state
