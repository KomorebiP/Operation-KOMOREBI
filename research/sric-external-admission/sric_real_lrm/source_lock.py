from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .hashing import sha256_object


class SourceLockError(RuntimeError):
    pass


def load_source_lock(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != "sric.real-lrm.external-source-lock.v2":
        raise SourceLockError("Unsupported external source lock schema")
    return data


def _git(repo: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except Exception as exc:
        raise SourceLockError(f"Git source-lock check failed for {repo}: {args}") from exc


def verify_external_repository(
    repo: str | Path,
    lock: Mapping[str, Any],
    *,
    dataset_key: str = "prontoqa_test",
) -> dict[str, Any]:
    root = Path(repo).resolve()
    expected = dict(lock["external_repository"])
    commit = _git(root, "rev-parse", "HEAD")
    if commit != expected["commit"]:
        raise SourceLockError(f"External commit {commit} does not match {expected['commit']}")
    status = _git(root, "status", "--porcelain")
    if status:
        raise SourceLockError("External repository is dirty")
    required_names = {"model_wrapper", "latent_runtime", "requirements", dataset_key}
    files = dict(expected["files"])
    missing = sorted(required_names - set(files))
    if missing:
        raise SourceLockError(f"Source lock omits required objects: {missing}")
    verified: list[dict[str, str]] = []
    for name in sorted(required_names):
        item = dict(files[name])
        actual = _git(root, "rev-parse", f"HEAD:{item['path']}")
        if actual != item["git_blob_sha"]:
            raise SourceLockError(f"Blob mismatch for {item['path']}: {actual}")
        verified.append({"name": name, "path": item["path"], "git_blob_sha": actual})
    payload = {
        "schema": "sric.real-lrm.external-source-verification.v1",
        "repository": expected["name"],
        "commit": commit,
        "clean": True,
        "dataset_key": dataset_key,
        "verified_objects": verified,
    }
    return {**payload, "verification_sha256": sha256_object(payload)}
