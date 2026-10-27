from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SELECTOR_PATH = PROJECT_ROOT / "validation/select_v0411_seeds.py"


def _load_selector() -> ModuleType:
    specification = importlib.util.spec_from_file_location(
        "test_select_v0411_seeds", SELECTOR_PATH
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


selector = _load_selector()


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / "validation").mkdir(parents=True)
    shutil.copyfile(SELECTOR_PATH, root / selector.SELECTOR_RELATIVE_PATH)
    (root / "src").mkdir()
    (root / "src/model.py").write_text("model = 'fixture'\n", encoding="utf-8")
    (root / ".venv").mkdir()
    (root / ".venv/ignored.txt").write_text("100000002\n", encoding="utf-8")
    (root / "src/__pycache__").mkdir()
    (root / "src/__pycache__/ignored.pyc").write_bytes(b"100000004")
    return root


def _draws(monkeypatch: pytest.MonkeyPatch, values: list[int]) -> list[int]:
    remaining = [value - selector.CANDIDATE_FLOOR for value in values]
    calls: list[int] = []

    def fake_randbelow(span: int) -> int:
        assert span == selector.CANDIDATE_SPAN
        value = remaining.pop(0)
        calls.append(value)
        return value

    monkeypatch.setattr(selector.secrets, "randbelow", fake_randbelow)
    return calls


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _outputs(root: Path) -> tuple[Path, Path, Path]:
    validation = root / "validation"
    return (
        validation / selector.SCAN_NAME,
        validation / selector.RECEIPT_NAME,
        validation / selector.REGISTRY_NAME,
    )


def test_selects_first_four_clean_candidates_and_seals_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _project(tmp_path)
    candidates = [100000000 + index for index in range(1, 13)]
    # Candidate 1 occurs once. Candidate 3 occurs twice. Candidate 2 appears
    # only as a substring adjacent to another digit and must remain clean.
    (root / "evidence.txt").write_text(
        "100000001 91000000020 100000003 x100000003y\n", encoding="utf-8"
    )
    calls = _draws(monkeypatch, [candidates[0], candidates[0], *candidates[1:]])

    result = selector.select_seeds(root)

    scan_path, receipt_path, registry_path = _outputs(root)
    assert all(path.is_file() for path in (scan_path, receipt_path, registry_path))
    scan = json.loads(scan_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    expected = [candidates[1], candidates[3], candidates[4], candidates[5]]
    assert registry["fresh_pilot_seeds"] == expected
    assert receipt["selected_fresh_pilot_seeds"] == expected
    assert receipt["candidate_generation_order"] == candidates
    assert receipt["randbelow_call_count"] == 13
    assert receipt["duplicate_draw_count"] == 1
    assert len(calls) == 13
    records = {row["candidate"]: row for row in receipt["candidate_scan_records"]}
    assert records[candidates[0]]["standalone_decimal_occurrence_count"] == 1
    assert records[candidates[1]]["standalone_decimal_occurrence_count"] == 0
    assert records[candidates[2]]["standalone_decimal_occurrence_count"] == 2

    file_paths = [record["relative_path"] for record in scan["files"]]
    assert file_paths == sorted(file_paths)
    assert "validation/select_v0411_seeds.py" in file_paths
    assert "evidence.txt" in file_paths
    assert not any(".venv" in path or "__pycache__" in path for path in file_paths)
    assert scan["scan_surface_sha256"] == selector._canonical_sha256(scan["files"])
    assert receipt["scan_manifest"]["sha256"] == _sha256(scan_path)
    assert receipt["seed_registry"]["sha256"] == _sha256(registry_path)
    assert receipt["selector"]["sha256"] == _sha256(
        root / selector.SELECTOR_RELATIVE_PATH
    )
    assert result["selected_seed_count"] == 4
    assert not (root / "validation" / selector.TRANSACTION_DIRECTORY_NAME).exists()


def test_fewer_than_four_clean_candidates_never_publishes_or_redraws(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _project(tmp_path)
    candidates = [200000000 + index for index in range(1, 13)]
    (root / "evidence.txt").write_text(
        " ".join(str(candidate) for candidate in candidates[:9]) + "\n",
        encoding="utf-8",
    )
    calls = _draws(monkeypatch, candidates)

    with pytest.raises(selector.SeedSelectionError, match="no redraw"):
        selector.select_seeds(root)

    assert len(calls) == 12
    assert not any(path.exists() for path in _outputs(root))
    assert not (root / "validation" / selector.TRANSACTION_DIRECTORY_NAME).exists()


def test_existing_selection_is_exclusive_and_checked_before_new_draw(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _project(tmp_path)
    candidates = [300000000 + index for index in range(1, 13)]
    first_calls = _draws(monkeypatch, candidates)
    selector.select_seeds(root)
    before = {path.name: path.read_bytes() for path in _outputs(root)}

    def forbidden_draw(_span: int) -> int:
        raise AssertionError("a consumed selector must not draw again")

    monkeypatch.setattr(selector.secrets, "randbelow", forbidden_draw)
    with pytest.raises(FileExistsError, match="already consumed"):
        selector.select_seeds(root)

    assert len(first_calls) == 12
    assert {path.name: path.read_bytes() for path in _outputs(root)} == before


@pytest.mark.parametrize(
    "late_path",
    [
        "validation/V0_41_1_PREOUTCOME_FREEZE.json",
        f"validation/{selector.CAMPAIGN_DIRECTORY_NAME}/campaign_receipt.json",
    ],
)
def test_freeze_or_campaign_artifact_blocks_late_selection_before_draw(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    late_path: str,
) -> None:
    root = _project(tmp_path)
    path = root / late_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("late\n", encoding="utf-8")

    def forbidden_draw(_span: int) -> int:
        raise AssertionError("late selection must fail before RNG")

    monkeypatch.setattr(selector.secrets, "randbelow", forbidden_draw)
    with pytest.raises(FileExistsError, match="too late"):
        selector.select_seeds(root)

    assert not any(output.exists() for output in _outputs(root))


def test_publication_failure_cleans_every_final_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _project(tmp_path)
    candidates = [400000000 + index for index in range(1, 13)]
    _draws(monkeypatch, candidates)
    original_link = selector.os.link
    calls = 0

    def fail_second_link(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected transaction publication failure")
        original_link(source, destination)

    monkeypatch.setattr(selector.os, "link", fail_second_link)
    with pytest.raises(OSError, match="injected"):
        selector.select_seeds(root)

    assert not any(path.exists() for path in _outputs(root))
    assert not (root / "validation" / selector.TRANSACTION_DIRECTORY_NAME).exists()
