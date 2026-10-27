from __future__ import annotations

import json
from pathlib import Path

import pytest

from komorebi_arc3_offline.suite import (
    SUITE_PROFILES,
    audit_suite,
    discover_suite,
    order_suite,
    write_suite_plan,
)

pytestmark = pytest.mark.local_suite


def _environment_root() -> Path:
    root = Path(__file__).resolve().parents[1] / "environment_files"
    if len(list(root.rglob("metadata.json"))) != 25:
        pytest.skip("optional 25-environment ARC fixture archive is not installed")
    return root


def test_uploaded_environment_tree_is_complete_and_offline_safe() -> None:
    report = audit_suite(_environment_root())
    assert report["game_count"] == 25
    assert report["all_ok"] is True
    assert all(row["ok"] for row in report["games"])
    assert len({row["game_id"] for row in report["games"]}) == 25


def test_suite_discovery_and_ordering() -> None:
    games = discover_suite(_environment_root())
    assert len(games) == 25
    easy = order_suite(games, "easy")
    hard = order_suite(games, "hard")
    assert easy[0].baseline_total <= easy[-1].baseline_total
    assert hard[0].baseline_total >= hard[-1].baseline_total
    assert order_suite(games, "id") == sorted(games, key=lambda row: row.game_id)


def test_profiles_create_distinct_whole_game_budgets() -> None:
    game = order_suite(discover_suite(_environment_root()), "easy")[0]
    quick = SUITE_PROFILES["quick"].actions_for(game)
    balanced = SUITE_PROFILES["balanced"].actions_for(game)
    thorough = SUITE_PROFILES["thorough"].actions_for(game)
    assert quick <= balanced <= thorough
    assert quick >= SUITE_PROFILES["quick"].minimum_actions


def test_suite_plan_round_trip(tmp_path: Path) -> None:
    games = order_suite(discover_suite(_environment_root()), "easy")[:3]
    paths = write_suite_plan(games, tmp_path, profile="balanced")
    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["game_count"] == 3
    assert payload["games"][0]["game_id"] == games[0].game_id
    assert payload["games"][0]["action_budget"] > 0
    assert paths["csv"].exists()
