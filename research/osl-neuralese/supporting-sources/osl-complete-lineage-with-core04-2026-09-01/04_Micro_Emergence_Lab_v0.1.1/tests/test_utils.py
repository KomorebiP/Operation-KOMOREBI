from pathlib import Path

from osl_lab.manifest import build_manifest, verify_manifest
from osl_lab.utils import iter_jsonl, write_jsonl


def test_jsonl_roundtrip(tmp_path: Path):
    records = [{"x": 1}, {"x": 2}]
    path, count = write_jsonl(tmp_path / "records.jsonl", records)
    assert count == 2
    assert list(iter_jsonl(path)) == records


def test_manifest_roundtrip(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    payload = build_manifest(tmp_path)
    assert payload["file_count"] == 1
    result = verify_manifest(tmp_path)
    assert result["status"] == "PASS"


def test_manifest_rejects_unexpected_unlisted_file(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    build_manifest(tmp_path)
    (tmp_path / "injected.txt").write_text("unexpected", encoding="utf-8")

    result = verify_manifest(tmp_path)

    assert result["status"] == "FAIL"
    assert result["unexpected"] == ["injected.txt"]


def test_manifest_rejects_stale_checksum_companion(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    build_manifest(tmp_path)
    (tmp_path / "SHA256SUMS.txt").write_text("stale\n", encoding="utf-8")

    result = verify_manifest(tmp_path)

    assert result["status"] == "FAIL"
    assert {item["path"] for item in result["failures"]} == {"SHA256SUMS.txt"}
