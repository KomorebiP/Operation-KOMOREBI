"""Static D0 protocol checks that do not execute the v0.36 campaign."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "validation" / "V0_36_DEVELOPMENT_PROTOCOL.md"
REGISTRY = ROOT / "validation" / "V0_36_LINEAGE_AND_SEED_REGISTRY.json"
RUNTIME = ROOT / "src" / "rrct" / "unified_causal_loop.py"


def test_v036_seed_registry_matches_d0_protocol() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    cohorts = registry["v036_reserved_cohorts"]
    assert cohorts["pilot_seeds"] == [6451, 6457, 6463, 6469]
    assert cohorts["development_seeds"] == [6501, 6507, 6513, 6519]
    assert cohorts["status"] == "reserved_unrun"
    assert set(cohorts["pilot_seeds"]).isdisjoint(cohorts["development_seeds"])

    protocol = PROTOCOL.read_text(encoding="utf-8")
    for seed in cohorts["pilot_seeds"] + cohorts["development_seeds"]:
        assert f"`{seed}`" in protocol
    assert "confirmatory or official seeds: none" in protocol


def test_v036_d0_schedule_and_endpoints_are_closed() -> None:
    protocol = PROTOCOL.read_text(encoding="utf-8")
    phases = re.findall(r"^### P([0-4])\.", protocol, flags=re.MULTILINE)
    assert phases == ["0", "1", "2", "3", "4"]
    assert "exact total is 4,800 transitions" in protocol

    endpoints = re.findall(r"^\| E(\d{2}) \|", protocol, flags=re.MULTILINE)
    assert endpoints == [f"{index:02d}" for index in range(1, 9)]
    assert "| E09 |" not in protocol
    assert "Campaign status: **unrun when this D0 text was written**" in protocol


def test_v036_d0_excludes_later_reflective_claims() -> None:
    protocol = PROTOCOL.read_text(encoding="utf-8")
    required_future_gaps = (
        "paired-sentinel lane",
        "causal-continuity planning",
        "learned continuity value",
        "Reflective value revision",
        "meta-criterion audit",
        "phenomenal",
    )
    for phrase in required_future_gaps:
        assert phrase.lower() in protocol.lower()
    assert "does not define a consciousness percentage" in protocol


def test_unified_runtime_has_no_private_world_import_or_name() -> None:
    tree = ast.parse(RUNTIME.read_text(encoding="utf-8"), filename=str(RUNTIME))
    imports: list[str] = []
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)

    assert not any(name.endswith("unified_causal_loop_experiment") for name in imports)
    assert names.isdisjoint(
        {
            "_hidden_interface",
            "_hidden_structure",
            "_true_focal_quality",
            "true_projector",
            "true_pair",
            "true_rank",
        }
    )
