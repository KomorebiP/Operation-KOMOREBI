from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from g1d.integrity import sha256_file
from g1d.integrity import (
    FIXED_SOURCE_CHECKPOINT_SHA256,
    FIXED_SOURCE_CLAIM,
    FIXED_SOURCE_CONFIG_DIGEST,
    FIXED_SOURCE_INVENTORY_SHA256,
    FIXED_SOURCE_SEED,
)


STATIC_FILES = {
    "static_analysis.json",
    "diagnostic_report.md",
    "diagnostic_preflight.json",
}
FULL_FILES = STATIC_FILES | {
    "checkpoint_spectrum.json",
    "state_geometry.json",
    "probe_results.json",
    "recurrence_results.json",
    "bridge_results.json",
    "dynamic_replay.json",
    "diagnostic_verdict.json",
    "intervention_predictions.jsonl",
    "feature_bank.pt",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Neuralese G1-D1 artifacts")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path.name}")
    return value


def main() -> int:
    args = parse_args()
    root = Path(args.output).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"diagnostic output not found: {root}")
    manifest_path = root / "artifact_manifest.json"
    verification_path = root / "verification.json"
    if not manifest_path.is_file() or not verification_path.is_file():
        raise RuntimeError("diagnostic manifest or verification is missing")
    manifest = read_json(manifest_path)
    if (
        manifest.get("schema") != "komorebi.neuralese.g1d.artifact_manifest.v1"
        or manifest.get("entry_count") != len(manifest.get("entries", []))
    ):
        raise RuntimeError("diagnostic artifact manifest is malformed")
    entries = manifest["entries"]
    expected_names = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "size", "sha256"}:
            raise RuntimeError("malformed diagnostic artifact entry")
        name = entry["path"]
        if (
            not isinstance(name, str)
            or not name
            or "/" in name
            or "\\" in name
            or name in expected_names
        ):
            raise RuntimeError(f"invalid diagnostic artifact name: {name!r}")
        expected_names.append(name)
        path = root / name
        if (
            not path.is_file()
            or path.stat().st_size != entry["size"]
            or sha256_file(path) != entry["sha256"]
        ):
            raise RuntimeError(f"diagnostic artifact byte mismatch: {name}")
    if expected_names != sorted(expected_names):
        raise RuntimeError("diagnostic artifact entries are not sorted")
    preflight = read_json(root / "diagnostic_preflight.json")
    scope = preflight.get("scope")
    if scope not in {"STATIC_ONLY", "FULL_DIAGNOSTIC"}:
        raise RuntimeError("unknown diagnostic scope")
    expected_set = STATIC_FILES if scope == "STATIC_ONLY" else FULL_FILES
    if set(expected_names) != expected_set:
        raise RuntimeError("diagnostic artifact set does not match its declared scope")
    observed_files = {
        path.name
        for path in root.iterdir()
        if path.is_file() and path.name != ".g1d.lock"
    }
    if observed_files != expected_set | {"artifact_manifest.json", "verification.json"}:
        raise RuntimeError("diagnostic output contains missing or unexpected files")
    static = read_json(root / "static_analysis.json")
    if static.get("schema") != "komorebi.neuralese.g1d.static_analysis.v1":
        raise RuntimeError("static-analysis schema mismatch")
    if static.get("source_run", {}).get("claim") != FIXED_SOURCE_CLAIM:
        raise RuntimeError("static analysis source claim mismatch")
    source = preflight.get("source_run_verification", {})
    cross_file = source.get("cross_file_verification", {})
    if (
        source.get("schema") != "komorebi.neuralese.g1d.fixed_source.v1"
        or source.get("status") != "PASS"
        or source.get("seed") != FIXED_SOURCE_SEED
        or source.get("claim") != FIXED_SOURCE_CLAIM
        or source.get("config_digest") != FIXED_SOURCE_CONFIG_DIGEST
        or source.get("checkpoint_sha256") != FIXED_SOURCE_CHECKPOINT_SHA256
        or source.get("source_inventory_sha256")
        != FIXED_SOURCE_INVENTORY_SHA256
        or cross_file.get("status") != "PASS"
        or cross_file.get("seed") != FIXED_SOURCE_SEED
        or cross_file.get("config_digest") != FIXED_SOURCE_CONFIG_DIGEST
        or cross_file.get("checkpoint_validated")
        is not (scope == "FULL_DIAGNOSTIC")
    ):
        raise RuntimeError("fixed source-run verification mismatch")
    verification = read_json(verification_path)
    if (
        verification.get("schema") != "komorebi.neuralese.g1d.verification.v1"
        or verification.get("status") != "PASS"
        or verification.get("claim") != "DIAGNOSTIC_ONLY"
        or verification.get("scope") != scope
        or verification.get("artifact_manifest_sha256") != sha256_file(manifest_path)
        or verification.get("artifact_count") != len(entries)
        or verification.get("source_run_immutable") is not True
    ):
        raise RuntimeError("diagnostic verification record mismatch")
    if scope == "FULL_DIAGNOSTIC":
        verdict = read_json(root / "diagnostic_verdict.json")
        replay = read_json(root / "dynamic_replay.json")
        if verdict.get("claim") != "DIAGNOSTIC_ONLY" or verdict.get(
            "g1_scientific_claim_changed"
        ) is not False:
            raise RuntimeError("diagnostic claim boundary mismatch")
        if not replay or not all(value.get("exact") is True for value in replay.values()):
            raise RuntimeError("saved predictions were not exactly replayed")
        if verification.get("dynamic_replay_exact") is not True:
            raise RuntimeError("verification omits exact dynamic replay")
        try:
            import torch
        except ImportError as error:
            raise RuntimeError("PyTorch is required to verify the feature bank") from error
        feature_bank = torch.load(
            root / "feature_bank.pt", map_location="cpu", weights_only=True
        )
        if (
            not isinstance(feature_bank, dict)
            or feature_bank.get("schema") != "komorebi.neuralese.g1d.feature_bank.v1"
            or feature_bank.get("source_run_config_digest")
            != FIXED_SOURCE_CONFIG_DIGEST
            or feature_bank.get("selection")
            != preflight.get("diagnostic_selection")
        ):
            raise RuntimeError("feature-bank schema mismatch")
        tensors = []

        def collect(value):
            if torch.is_tensor(value):
                tensors.append(value)
            elif isinstance(value, dict):
                for child in value.values():
                    collect(child)
            elif isinstance(value, (list, tuple)):
                for child in value:
                    collect(child)

        collect(feature_bank)
        if not tensors or any(not bool(torch.isfinite(value).all().item()) for value in tensors):
            raise RuntimeError("feature bank is empty or nonfinite")
    print(
        f"G1D_OUTPUT_VALID scope={scope} artifacts={len(entries)} "
        f"claim={verification['claim']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"G1D_OUTPUT_INVALID: {error}", file=sys.stderr)
        raise SystemExit(1)
