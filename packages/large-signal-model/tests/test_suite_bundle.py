from __future__ import annotations

import json
from pathlib import Path

import pytest

from komorebi_arc3_offline.suite import (
    SUITE_PROFILES,
    audit_suite,
    discover_suite,
    write_suite_manifest,
)

pytestmark = pytest.mark.local_suite


def _environment_root() -> Path:
    root = Path(__file__).resolve().parents[1] / "environment_files"
    if len(list(root.rglob("metadata.json"))) != 25:
        pytest.skip("optional 25-environment ARC fixture archive is not installed")
    return root


def test_bundled_suite_has_25_complete_environments() -> None:
    root = _environment_root()
    games = discover_suite(root)
    assert len(games) == 25
    assert len({game.game_id for game in games}) == 25
    assert all(game.level_count >= 1 for game in games)
    assert all(game.baseline_total > 0 for game in games)
    assert all((root / game.metadata_path).exists() for game in games)
    assert all((root / game.source_path).exists() for game in games)


def test_static_suite_audit_passes() -> None:
    report = audit_suite(_environment_root())
    assert report["game_count"] == 25
    assert report["all_ok"] is True
    assert all(row["ok"] for row in report["games"])


def test_profiles_generate_ordered_bounded_budgets() -> None:
    games = discover_suite(_environment_root())
    for game in games:
        quick = SUITE_PROFILES["quick"].actions_for(game)
        balanced = SUITE_PROFILES["balanced"].actions_for(game)
        thorough = SUITE_PROFILES["thorough"].actions_for(game)
        assert 1 <= quick <= balanced <= thorough
        assert quick <= SUITE_PROFILES["quick"].maximum_actions
        assert thorough <= SUITE_PROFILES["thorough"].maximum_actions


def test_manifest_records_all_games(tmp_path: Path) -> None:
    path = write_suite_manifest(_environment_root(), tmp_path / "manifest.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["game_count"] == 25
    assert len(payload["games"]) == 25
    assert all(row["balanced_budget"] >= row["quick_budget"] for row in payload["games"])
