from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

from sric_real_lrm.hashing import sha256_file, sha256_file_set, sha256_object
from sric_real_lrm.source_lock import load_source_lock


DEFAULT_BASE_FILES = (
    "config.json",
    "generation_config.json",
    "model.safetensors",
    "merges.txt",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
)


def build_asset_plan(lock: Mapping[str, Any], runtime_root: str | Path) -> dict[str, Any]:
    root = Path(runtime_root).resolve()
    checkpoint = dict(lock["checkpoints"]["prontoqa_primary"])
    base = dict(lock["base_model"])
    required = tuple(base.get("required_files", DEFAULT_BASE_FILES))
    return {
        "runtime_root": str(root),
        "checkpoint_repository": str(checkpoint["repository"]),
        "checkpoint_revision": str(checkpoint["revision"]),
        "checkpoint_filename": str(checkpoint["filename"]),
        "checkpoint_dir": str(root / "checkpoints" / "gpt2_prontoqa_multimode"),
        "base_model_repository": str(base["repository"]),
        "base_model_revision": str(base["revision"]),
        "base_model_required_files": list(required),
        "base_model_dir": str(root / "models" / "gpt2"),
    }


def _require_python() -> None:
    if sys.version_info[:2] not in {(3, 10), (3, 11), (3, 12)}:
        raise SystemExit(
            "Use Python 3.10-3.12 for the pinned external runtime; "
            f"current={sys.version.split()[0]}"
        )


def _verify_required_files(root: Path, names: list[str]) -> None:
    missing = [name for name in names if not (root / name).is_file()]
    if missing:
        raise RuntimeError(f"Base-model snapshot is incomplete: missing={missing}")


def download_assets(
    *,
    lock_path: str | Path,
    runtime_root: str | Path,
    external_repo: str | Path,
    local_files_only: bool = False,
) -> dict[str, Any]:
    # Import only after the caller has had an opportunity to set
    # HF_HUB_DISABLE_XET. huggingface_hub reads that switch at import time.
    from huggingface_hub import hf_hub_download, snapshot_download

    lock = load_source_lock(lock_path)
    plan = build_asset_plan(lock, runtime_root)
    root = Path(plan["runtime_root"])
    root.mkdir(parents=True, exist_ok=True)

    checkpoint_dir = Path(plan["checkpoint_dir"])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = Path(
        hf_hub_download(
            repo_id=plan["checkpoint_repository"],
            filename=plan["checkpoint_filename"],
            revision=plan["checkpoint_revision"],
            local_dir=checkpoint_dir,
            local_files_only=local_files_only,
        )
    ).resolve()

    base_dir = Path(
        snapshot_download(
            repo_id=plan["base_model_repository"],
            revision=plan["base_model_revision"],
            local_dir=plan["base_model_dir"],
            allow_patterns=plan["base_model_required_files"],
            local_files_only=local_files_only,
        )
    ).resolve()
    _verify_required_files(base_dir, plan["base_model_required_files"])

    external_root = Path(external_repo).resolve()
    data_path = external_root / "data" / "prontoqa_test.json"
    if not data_path.is_file():
        raise FileNotFoundError(f"Source-locked PrOntoQA test file is missing: {data_path}")

    payload = {
        "schema": "sric.block24.runtime-paths.v3",
        "python": str(Path(sys.executable).resolve()),
        "external_repo": str(external_root),
        "external_commit": str(lock["external_repository"]["commit"]),
        "checkpoint": str(checkpoint_path),
        "checkpoint_repository": plan["checkpoint_repository"],
        "checkpoint_revision": plan["checkpoint_revision"],
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "checkpoint_size": checkpoint_path.stat().st_size,
        "base_model": str(base_dir),
        "base_model_repository": plan["base_model_repository"],
        "base_model_revision": plan["base_model_revision"],
        "base_model_required_files": plan["base_model_required_files"],
        "base_model_tree_sha256": sha256_file_set(base_dir, plan["base_model_required_files"]),
        "data": str(data_path),
        "download_transport": {
            "hf_hub_disable_xet": os.getenv("HF_HUB_DISABLE_XET", "0"),
            "local_files_only": bool(local_files_only),
        },
    }
    payload["asset_receipt_sha256"] = sha256_object(payload)
    output = root / "runtime_paths.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and hash the exact Block 24 checkpoint and minimal GPT-2 snapshot"
    )
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--external-repo", required=True)
    parser.add_argument("--source-lock", default="external_source_lock.json")
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument(
        "--disable-xet",
        action="store_true",
        help="Force the standard HTTP/LFS path when the local Xet transport is unavailable",
    )
    args = parser.parse_args()
    _require_python()
    if args.disable_xet:
        os.environ["HF_HUB_DISABLE_XET"] = "1"
    receipt = download_assets(
        lock_path=args.source_lock,
        runtime_root=args.runtime_root,
        external_repo=args.external_repo,
        local_files_only=args.local_files_only,
    )
    print("SRIC_BLOCK24_ASSET_DOWNLOAD=PASS")
    print(f"checkpoint_sha256={receipt['checkpoint_sha256']}")
    print(f"checkpoint_size={receipt['checkpoint_size']}")
    print(f"base_model_tree_sha256={receipt['base_model_tree_sha256']}")
    print(f"asset_receipt_sha256={receipt['asset_receipt_sha256']}")
    print(f"runtime_paths={Path(args.runtime_root).resolve() / 'runtime_paths.json'}")


if __name__ == "__main__":
    main()
