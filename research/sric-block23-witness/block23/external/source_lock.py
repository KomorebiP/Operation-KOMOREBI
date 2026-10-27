from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while data := f.read(chunk):
            h.update(data)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def verify_source_lock(repo_dir: str | Path, lock_path: str | Path) -> dict[str, Any]:
    repo = Path(repo_dir)
    lock = json.loads(Path(lock_path).read_text(encoding="utf-8"))
    result: dict[str, Any] = {"repository_exists": repo.is_dir(), "files": {}, "commit": None, "passed": False}
    if not repo.is_dir():
        return result
    try:
        result["commit"] = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        result["commit"] = None
    for rel, expected in lock["files"].items():
        path = repo / rel
        actual = git_blob_sha(path) if path.is_file() else None
        result["files"][rel] = {"expected_git_blob": expected, "actual_git_blob": actual, "match": actual == expected}
    result["passed"] = (
        result["commit"] == lock["commit"]
        and all(v["match"] for v in result["files"].values())
    )
    return result
