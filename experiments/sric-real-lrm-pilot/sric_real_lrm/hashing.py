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
