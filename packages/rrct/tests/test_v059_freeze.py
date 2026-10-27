from __future__ import annotations

import copy

from rrct_lab.config import DEFAULT_CONFIG
from rrct_lab.freeze import create_freeze, verify_freeze


def test_freeze_round_trip(tmp_path) -> None:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["experiment"]["family"] = "single_agent_closure"
    path = tmp_path / "freeze.json"
    payload = create_freeze(config, path)
    assert payload["source_file_count"] > 0
    verification = verify_freeze(path)
    assert verification["all_checks_pass"] is True
