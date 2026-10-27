from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_object(obj: Any) -> str:
    return sha256_bytes(canonical_json_bytes(obj))


def sha256_file(path: str | Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def file_manifest(root: str | Path, exclude: Iterable[str] = ()) -> list[dict[str, Any]]:
    root = Path(root)
    excluded = set(exclude)
    rows: list[dict[str, Any]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        rows.append({"path": rel, "size": path.stat().st_size, "sha256": sha256_file(path)})
    return rows



def sha256_file_set(root: str | Path, relative_paths: Iterable[str]) -> str:
    """Hash an explicit, ordered-independent set of files below ``root``.

    This is used for source-locked model payloads so unrelated cache or legacy
    files cannot alter the receipt. Every declared file must exist.
    """
    base = Path(root)
    rows: list[dict[str, Any]] = []
    for rel in sorted(set(str(item).replace("\\", "/") for item in relative_paths)):
        path = base / Path(rel)
        if not path.is_file():
            raise FileNotFoundError(f"Required payload file is missing: {path}")
        rows.append({"path": rel, "size": path.stat().st_size, "sha256": sha256_file(path)})
    return sha256_object(rows)

def sha256_directory(
    root: str | Path,
    *,
    excluded_directories: Iterable[str] = (".git", ".cache", "__pycache__"),
) -> str:
    """Hash a directory by relative path, size, and file digest.

    Download-client metadata and version-control internals are excluded. The
    resulting digest commits the actual local model/tokenizer payload.
    """
    base = Path(root)
    excluded = set(excluded_directories)
    rows: list[dict[str, Any]] = []
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        rel_path = path.relative_to(base)
        if any(part in excluded for part in rel_path.parts):
            continue
        rows.append({
            "path": rel_path.as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return sha256_object(rows)
