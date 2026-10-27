from __future__ import annotations

import importlib.util
import json
import platform
import sys
from pathlib import Path
from typing import Any

from .source_lock import sha256_file, verify_source_lock


def run_preflight(
    repo_dir: str | Path | None,
    checkpoint: str | Path | None,
    source_lock: str | Path,
) -> dict[str, Any]:
    repo = Path(repo_dir).expanduser().resolve() if repo_dir else None
    ckpt = Path(checkpoint).expanduser().resolve() if checkpoint else None
    transformers_available = importlib.util.find_spec("transformers") is not None
    torch_available = importlib.util.find_spec("torch") is not None
    cuda_available = False
    torch_version = None
    if torch_available:
        import torch
        torch_version = torch.__version__
        cuda_available = bool(torch.cuda.is_available())
    lock_result = verify_source_lock(repo, source_lock) if repo else {"passed": False, "repository_exists": False}
    blockers: list[str] = []
    if not transformers_available:
        blockers.append("transformers_missing")
    if not torch_available:
        blockers.append("torch_missing")
    if repo is None or not repo.is_dir():
        blockers.append("repository_checkout_missing")
    elif not lock_result.get("passed", False):
        blockers.append("repository_source_lock_mismatch")
    if ckpt is None or not ckpt.is_file():
        blockers.append("checkpoint_missing")
    if not cuda_available:
        blockers.append("cuda_unavailable")

    if not blockers:
        status = "READY_FOR_REAL_CHECKPOINT_AUDIT"
    elif set(blockers) <= {"cuda_unavailable"}:
        status = "READY_CPU_ONLY"
    else:
        status = "ADAPTER_VALIDATED_REAL_EXECUTION_BLOCKED"
    return {
        "schema": "sric.block23.external-preflight.v1",
        "status": status,
        "real_checkpoint_executed": False,
        "blockers": blockers,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "torch": torch_version,
            "transformers_available": transformers_available,
            "cuda_available": cuda_available,
        },
        "repository": str(repo) if repo else None,
        "source_lock": lock_result,
        "checkpoint": {
            "path": str(ckpt) if ckpt else None,
            "exists": bool(ckpt and ckpt.is_file()),
            "size_bytes": ckpt.stat().st_size if ckpt and ckpt.is_file() else None,
            "sha256": sha256_file(ckpt) if ckpt and ckpt.is_file() else None,
        },
    }


def write_preflight(path: str | Path, **kwargs: Any) -> dict[str, Any]:
    result = run_preflight(**kwargs)
    Path(path).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result
