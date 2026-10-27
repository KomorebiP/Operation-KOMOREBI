from __future__ import annotations

import copy
import importlib.util

from rrct_lab.config import DEFAULT_CONFIG
from rrct_lab.experiments.smoke import run
from rrct_lab.registry import EXPERIMENTS


def test_all_family_smoke_matrix() -> None:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["experiment"]["family"] = "smoke_matrix"
    config["runtime"]["device"] = "cpu"
    result = run(config)
    expected_families = set(EXPERIMENTS) - {"smoke_matrix"}
    observed_families = set(result.metadata["family_results"])
    assert observed_families == expected_families
    assert result.metrics["families_total"] == len(expected_families)
    if importlib.util.find_spec("torch") is None:
        expected_missing = {"nested_workspace", "fuzzy_coalitions"}
        assert result.status == "partial"
        assert result.metrics["families_passed"] == len(expected_families) - 2
        assert {
            name
            for name, payload in result.metadata["family_results"].items()
            if payload["status"] == "failed"
        } == expected_missing
        for name in expected_missing:
            assert "DependencyError" in result.metadata["family_results"][name]["error"]
    else:
        assert result.status == "completed"
        assert result.metrics["families_passed"] == result.metrics["families_total"]
