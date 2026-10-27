from __future__ import annotations

import copy

import pytest

from rrct_lab.config import DEFAULT_CONFIG, validate_config
from rrct_lab.exceptions import ConfigError, SafetyBoundaryError
from rrct_lab.runner import run_config


def test_default_config_is_valid() -> None:
    validate_config(copy.deepcopy(DEFAULT_CONFIG))


def test_safety_boundary_blocks_network_access() -> None:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["safety"]["network_access"] = True
    with pytest.raises(SafetyBoundaryError):
        validate_config(config)


def test_runner_validates_direct_config_mappings() -> None:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["run"]["atomic_results"] = False
    with pytest.raises(ConfigError, match="atomic_results"):
        run_config(config)


def test_synthetic_jspace_rank_above_head_count_is_rejected() -> None:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["experiment"]["family"] = "persistent_fuzzy_j_workspace"
    config["jspace"]["residual_dimension"] = 32
    config["jspace"]["frame_rank"] = 5
    with pytest.raises(ConfigError, match="four-head synthetic bridge"):
        validate_config(config)


def test_jspace_active_directions_cannot_exceed_rank() -> None:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["experiment"]["family"] = "persistent_fuzzy_j_workspace"
    config["jspace"]["frame_rank"] = 2
    config["jspace"]["active_directions"] = 3
    with pytest.raises(ConfigError, match="active_directions"):
        validate_config(config)
