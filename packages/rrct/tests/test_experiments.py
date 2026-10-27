from __future__ import annotations

import copy

from rrct_lab.config import DEFAULT_CONFIG
from rrct_lab.experiments import (
    continuous,
    distributed,
    formation,
    identity,
    single_agent,
    synergy,
)


def base(family: str) -> dict:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["experiment"]["family"] = family
    config["experiment"]["episodes"] = 128
    config["experiment"]["calibration_episodes"] = 128
    config["experiment"]["holdout_episodes"] = 128
    config["run"]["save_rows"] = False
    return config


def test_fast_experiment_families() -> None:
    configs = [
        (single_agent.run, base("single_agent_closure")),
        (identity.run, base("transformational_identity")),
        (distributed.run, base("distributed_workspace")),
        (synergy.run, base("synergistic_channel")),
        (formation.run, base("formation_routing")),
        (continuous.run, base("continuous_open_set_runtime")),
    ]
    configs[2][1]["features"]["distributed_workspace"] = True
    configs[2][1]["features"]["pair_memory"] = True
    configs[4][1]["features"]["dynamic_formation"] = True
    configs[4][1]["features"]["cost_regularization"] = True
    configs[5][1]["continuous"]["steps"] = 24
    configs[5][1]["features"]["continuous_event_fabric"] = True
    configs[5][1]["features"]["dynamic_formation"] = True
    configs[5][1]["features"]["fuzzy_packets"] = True
    for runner, config in configs:
        result = runner(config)
        assert result.status == "completed"
        assert result.metrics
