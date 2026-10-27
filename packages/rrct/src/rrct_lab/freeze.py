from __future__ import annotations

import datetime as dt
import json
import pathlib
from typing import Any

from .config import validate_config
from .dependencies import doctor
from .contracts import enforce_contract
from .orchestration import stable_checkpoint_digest
from .runner import project_root, run_config
from .utils import atomic_write_json, digest_object, sha256_file


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def source_manifest(root: pathlib.Path) -> list[dict[str, Any]]:
    included: list[pathlib.Path] = []
    for pattern in (
        "src/**/*.py",
        "tests/**/*.py",
        "vendor/wheels/*.whl",
        "pyproject.toml",
        "requirements-local.txt",
    ):
        included.extend(root.glob(pattern))
    rows = []
    for path in sorted({item.resolve() for item in included if item.is_file()}):
        rows.append(
            {
                "relative_path": path.relative_to(root.resolve()).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return rows


def create_freeze(config: dict[str, Any], output: pathlib.Path) -> dict[str, Any]:
    validate_config(config)
    contract = enforce_contract(config)
    root = project_root()
    manifest = source_manifest(root)
    payload = {
        "schema": "rrct.lab.freeze.v2",
        "created_at_utc": _utc_now(),
        "config": config,
        "config_digest": digest_object(config),
        "stable_checkpoint_digest": stable_checkpoint_digest(config),
        "feature_contract": contract,
        "source_file_count": len(manifest),
        "source_manifest": manifest,
        "source_manifest_digest": digest_object(manifest),
        "environment": doctor(),
        "seed_policy": {
            "base_seed": int(config["run"]["seed"]),
            "repetitions": int(config["run"].get("repetitions", 1)),
        },
    }
    payload["freeze_content_digest"] = digest_object(payload)
    atomic_write_json(output, payload)
    return payload


def verify_freeze(path: pathlib.Path) -> dict[str, Any]:
    root = project_root()
    payload = json.loads(path.read_text(encoding="utf-8"))
    failures: list[str] = []
    stored_content_digest = payload.get("freeze_content_digest")
    unsigned_payload = dict(payload)
    unsigned_payload.pop("freeze_content_digest", None)
    if stored_content_digest != digest_object(unsigned_payload):
        failures.append("freeze_content_digest")
    if digest_object(payload["source_manifest"]) != payload.get("source_manifest_digest"):
        failures.append("source_manifest_digest")
    if digest_object(payload["config"]) != payload["config_digest"]:
        failures.append("config_digest")
    if stable_checkpoint_digest(payload["config"]) != payload["stable_checkpoint_digest"]:
        failures.append("stable_checkpoint_digest")
    current_manifest = source_manifest(root)
    expected_paths = {entry["relative_path"] for entry in payload["source_manifest"]}
    current_paths = {entry["relative_path"] for entry in current_manifest}
    for relative in sorted(expected_paths - current_paths):
        failures.append(f"missing::{relative}")
    for relative in sorted(current_paths - expected_paths):
        failures.append(f"unexpected::{relative}")
    for entry in payload["source_manifest"]:
        candidate = root / entry["relative_path"]
        if not candidate.is_file():
            failures.append(f"missing::{entry['relative_path']}")
            continue
        if candidate.stat().st_size != entry["size_bytes"]:
            failures.append(f"size::{entry['relative_path']}")
        if sha256_file(candidate) != entry["sha256"]:
            failures.append(f"sha256::{entry['relative_path']}")
    return {
        "schema": "rrct.lab.freeze_verification.v2",
        "freeze": str(path),
        "source_file_count": len(payload["source_manifest"]),
        "failed_checks": failures,
        "all_checks_pass": not failures,
        "payload": payload,
    }


def run_frozen(path: pathlib.Path) -> list[dict[str, Any]]:
    verification = verify_freeze(path)
    if not verification["all_checks_pass"]:
        raise RuntimeError(
            "freeze verification failed: " + ", ".join(verification["failed_checks"])
        )
    return run_config(verification["payload"]["config"])


def audit_run(run_dir: pathlib.Path) -> dict[str, Any]:
    failures: list[str] = []
    resolved_path = run_dir / "resolved_config.json"
    summary_path = run_dir / "summary.json"
    state_path = run_dir / "run_state.json"
    for path in (resolved_path, summary_path, state_path):
        if not path.is_file():
            failures.append(f"missing::{path.name}")
    if failures:
        return {
            "schema": "rrct.lab.run_audit.v1",
            "run_directory": str(run_dir),
            "failed_checks": failures,
            "all_checks_pass": False,
        }
    config = json.loads(resolved_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    stable_digest = stable_checkpoint_digest(config)
    if state.get("config_digest") != stable_digest:
        failures.append("state_config_digest")
    if summary.get("status") == "completed" and state.get("status") != "completed":
        failures.append("completed_summary_without_completed_state")
    checkpoint_path = run_dir / "checkpoints/latest.json"
    checkpoint = None
    if checkpoint_path.is_file():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if checkpoint.get("config_digest") != stable_digest:
            failures.append("checkpoint_config_digest")
        if checkpoint.get("state_digest") != digest_object(checkpoint.get("state", {})):
            failures.append("checkpoint_state_digest")
    contract_path = run_dir / "feature_contract.json"
    if not contract_path.is_file():
        failures.append("missing::feature_contract.json")
    return {
        "schema": "rrct.lab.run_audit.v1",
        "run_directory": str(run_dir),
        "family": summary.get("family"),
        "summary_status": summary.get("status"),
        "run_state_status": state.get("status"),
        "checkpoint_present": checkpoint is not None,
        "resume_count": state.get("resume_count", 0),
        "failed_checks": failures,
        "all_checks_pass": not failures,
    }
