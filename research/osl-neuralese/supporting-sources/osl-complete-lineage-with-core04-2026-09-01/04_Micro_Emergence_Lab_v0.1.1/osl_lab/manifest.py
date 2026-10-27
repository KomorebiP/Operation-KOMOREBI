from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping

from .utils import save_json, sha256_file


DEFAULT_EXCLUDES = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "dist",
    "results",
    "runs",
}


def iter_files(root: str | Path, excludes: Iterable[str] = DEFAULT_EXCLUDES):
    base = Path(root)
    blocked = set(excludes)
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(base)
        if any(part in blocked for part in relative.parts):
            continue
        if path.name in {"MANIFEST.json", "SHA256SUMS.txt"}:
            continue
        yield path, relative


def build_manifest(root: str | Path, output: str | Path | None = None) -> dict[str, Any]:
    base = Path(root).resolve()
    entries = []
    for path, relative in iter_files(base):
        entries.append(
            {
                "path": relative.as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    payload = {
        "schema": "osl.micro-emergence.manifest.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(entries),
        "files": entries,
    }
    target = Path(output) if output else base / "MANIFEST.json"
    save_json(target, payload)
    sums = target.with_name("SHA256SUMS.txt")
    sums.write_text(
        "".join(f"{item['sha256']}  {item['path']}\n" for item in entries),
        encoding="utf-8",
        newline="\n",
    )
    return payload


def verify_manifest(root: str | Path, manifest_path: str | Path | None = None) -> dict[str, Any]:
    base = Path(root).resolve()
    source = Path(manifest_path) if manifest_path else base / "MANIFEST.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    failures: list[dict[str, str]] = []
    checked = 0
    if not isinstance(payload, Mapping):
        return {
            "schema": "osl.micro-emergence.manifest-verification.v1",
            "status": "FAIL",
            "checked": 0,
            "expected": 0,
            "unexpected": [],
            "failures": [{"path": "MANIFEST.json", "reason": "manifest root must be an object"}],
        }
    if payload.get("schema") != "osl.micro-emergence.manifest.v1":
        failures.append({"path": "MANIFEST.json", "reason": "unsupported manifest schema"})
    raw_entries = payload.get("files", [])
    if not isinstance(raw_entries, list):
        return {
            "schema": "osl.micro-emergence.manifest-verification.v1",
            "status": "FAIL",
            "checked": 0,
            "expected": 0,
            "unexpected": [],
            "failures": [{"path": "MANIFEST.json", "reason": "files must be a list"}],
        }
    declared_paths: set[str] = set()
    valid_entries: list[tuple[Mapping[str, Any], str, Path]] = []
    for item in raw_entries:
        if not isinstance(item, Mapping) or not isinstance(item.get("path"), str):
            failures.append({"path": "MANIFEST.json", "reason": "invalid file entry"})
            continue
        raw_path = str(item["path"])
        relative = PurePosixPath(raw_path)
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            failures.append({"path": raw_path, "reason": "unsafe manifest path"})
            continue
        normalized = relative.as_posix()
        if normalized in declared_paths:
            failures.append({"path": normalized, "reason": "duplicate manifest path"})
            continue
        declared_paths.add(normalized)
        path = (base / Path(*relative.parts)).resolve()
        if not path.is_relative_to(base):
            failures.append({"path": normalized, "reason": "manifest path escapes project root"})
            continue
        valid_entries.append((item, normalized, path))

    declared_count = payload.get("file_count")
    if declared_count != len(raw_entries):
        failures.append(
            {
                "path": "MANIFEST.json",
                "reason": f"file_count {declared_count!r} != {len(raw_entries)} entries",
            }
        )

    actual_paths = {relative.as_posix() for _, relative in iter_files(base)}
    unexpected = sorted(actual_paths - declared_paths)
    for relative in unexpected:
        failures.append({"path": relative, "reason": "unexpected unmanifested file"})

    sums_path = base / "SHA256SUMS.txt"
    try:
        expected_sums = "".join(
            f"{str(item['sha256'])}  {normalized}\n"
            for item, normalized, _ in valid_entries
        )
    except KeyError:
        expected_sums = ""
        failures.append({"path": "MANIFEST.json", "reason": "file entry lacks sha256"})
    if not sums_path.is_file():
        failures.append({"path": "SHA256SUMS.txt", "reason": "missing"})
    elif sums_path.read_text(encoding="utf-8") != expected_sums:
        failures.append({"path": "SHA256SUMS.txt", "reason": "content does not match manifest"})

    for item, normalized, path in valid_entries:
        if not path.is_file():
            failures.append({"path": normalized, "reason": "missing"})
            continue
        checked += 1
        actual_size = path.stat().st_size
        try:
            expected_size = int(item["size_bytes"])
            expected_hash = str(item["sha256"])
        except (KeyError, TypeError, ValueError):
            failures.append({"path": normalized, "reason": "invalid size/hash descriptor"})
            continue
        if actual_size != expected_size:
            failures.append(
                {
                    "path": normalized,
                    "reason": f"size {actual_size} != {expected_size}",
                }
            )
            continue
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            failures.append({"path": normalized, "reason": "sha256 mismatch"})
    return {
        "schema": "osl.micro-emergence.manifest-verification.v1",
        "status": "PASS" if not failures else "FAIL",
        "checked": checked,
        "expected": len(raw_entries),
        "unexpected": unexpected,
        "failures": failures,
    }
