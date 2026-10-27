from __future__ import annotations

import copy
from pathlib import Path

from rrct_lab.config import DEFAULT_CONFIG
from rrct_lab.freeze import create_freeze, verify_freeze


def test_source_and_configuration_freeze_verifies(tmp_path: Path) -> None:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["experiment"]["family"] = "continuous_open_set_runtime"
    path = tmp_path / "freeze.json"
    payload = create_freeze(config, path)
    verification = verify_freeze(path)
    assert payload["source_file_count"] > 0
    assert verification["all_checks_pass"] is True
    assert verification["failed_checks"] == []
