from __future__ import annotations

import copy

import pytest

from rrct_lab.config import DEFAULT_CONFIG
from rrct_lab.contracts import audit_config, enforce_contract
from rrct_lab.exceptions import ConfigError
from rrct_lab.registry import get_experiment


def test_strict_contract_rejects_unused_nondefault_setting() -> None:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["experiment"]["family"] = "single_agent_closure"
    config["features"]["fuzzy_packets"] = True
    with pytest.raises(ConfigError):
        enforce_contract(config)


def test_continuous_contract_accepts_dynamic_runtime_controls() -> None:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["experiment"]["family"] = "continuous_open_set_runtime"
    config["features"]["continuous_event_fabric"] = True
    config["features"]["dynamic_packet_birth"] = True
    config["features"]["dynamic_packet_death"] = True
    config["features"]["self_model_repair"] = True
    config["workspace"]["allow_new_packets"] = True
    config["continuous"]["checkpoint_interval"] = 4
    report = audit_config(config)
    assert report["unknown_keys"] == []
    assert report["unsupported_nondefault"] == []


def test_continuous_runtime_ownership_comes_from_registry() -> None:
    spec = get_experiment("continuous_open_set_runtime")
    assert spec.checkpoint_interval_key == "continuous.checkpoint_interval"
    assert set(spec.runtime_owned_keys) == {
        "runtime.memory_limit_mb",
        "runtime.timeout_seconds",
        "run.save_rows",
    }

    config = copy.deepcopy(DEFAULT_CONFIG)
    config["experiment"]["family"] = spec.key
    config["continuous"]["checkpoint_interval"] = 4
    config["runtime"]["memory_limit_mb"] = 64
    config["runtime"]["timeout_seconds"] = 10
    config["run"]["save_rows"] = False
    report = audit_config(config)
    assert report["unsupported_nondefault"] == []
    assert {
        "continuous.checkpoint_interval",
        "runtime.memory_limit_mb",
        "runtime.timeout_seconds",
        "run.save_rows",
    }.issubset(report["implemented_nondefault"])


def test_atomic_result_writes_cannot_be_disabled() -> None:
    import copy

    from rrct_lab.config import DEFAULT_CONFIG, validate_config
    from rrct_lab.exceptions import ConfigError

    config = copy.deepcopy(DEFAULT_CONFIG)
    config["run"]["atomic_results"] = False
    with pytest.raises(ConfigError):
        validate_config(config)
