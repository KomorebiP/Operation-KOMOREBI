from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from rrct_lab.config import DEFAULT_CONFIG
from rrct_lab.exceptions import ConfigError
from rrct_lab.sweep import (
    _base_config_digest,
    _cell_name,
    expand_grid,
    run_sweep,
)


def test_grid_expansion() -> None:
    rows = expand_grid({"a": [1, 2], "b": [3, 4, 5]})
    assert len(rows) == 6
    assert {tuple(sorted(row.items())) for row in rows}


def _nonexecuting_sweep(output_root: Path) -> dict:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["run"].update(
        {
            "name": "digest_bound",
            "output_root": str(output_root),
            "overwrite": True,
        }
    )
    config["safety"]["allowed_output_root"] = str(output_root)
    config["sweep"].update(
        {
            "enabled": True,
            "execute": False,
            "resume": True,
            "grid": {"experiment.noise_std": [0.01, 0.02]},
        }
    )
    return config


def test_cell_identity_binds_base_configuration() -> None:
    first = copy.deepcopy(DEFAULT_CONFIG)
    second = copy.deepcopy(DEFAULT_CONFIG)
    second["experiment"]["noise_std"] = 0.25
    overrides = {"training.steps": 10}
    first_id = _cell_name(0, overrides, _base_config_digest(first))
    second_id = _cell_name(0, overrides, _base_config_digest(second))
    assert first_id != second_id


def test_sweep_resume_rejects_changed_base_configuration(tmp_path: Path) -> None:
    config = _nonexecuting_sweep(tmp_path)
    first = run_sweep(config)
    state_path = Path(first["sweep_directory"]) / "sweep_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["base_config_digest"] == _base_config_digest(config)

    changed = copy.deepcopy(config)
    changed["experiment"]["noise_std"] = 0.25
    with pytest.raises(ConfigError, match="base configuration digest"):
        run_sweep(changed)
