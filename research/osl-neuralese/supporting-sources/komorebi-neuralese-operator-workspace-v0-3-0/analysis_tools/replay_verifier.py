#!/usr/bin/env python3
"""Fail-closed, single-cell reproducibility replay for the v0.3 runner.

The replay protocol preserves the primary training and evaluation configuration,
but selects exactly one arm and one seed.  The verifier then compares the
original and replayed scientific records and checkpoint tensor payloads.

Raw ``torch.save`` file hashes are reported but are not expected to match: the
replay checkpoint intentionally contains a different protocol identifier and
protocol digest.  A canonical checkpoint hash removes only those explicitly
listed provenance fields and hashes every state-dict tensor byte, so it is the
appropriate exact checkpoint comparison for a single-cell replay protocol.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import torch


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "run_experiment.py"

RECORD_EXCLUDED_PATHS: tuple[tuple[str, ...], ...] = (
    ("analysis_status",),
    ("protocol_id",),
    ("protocol_digest",),
    ("training", "elapsed_seconds"),
    ("started_at",),
    ("created_at",),
    ("completed_at",),
    ("finished_at",),
    ("timestamp",),
    ("timestamp_utc",),
    ("output_dir",),
    ("protocol_path",),
    ("checkpoint_path",),
    ("environment",),
    ("plots",),
    ("plot_files",),
)
CHECKPOINT_METADATA_EXCLUDED_PATHS: tuple[tuple[str, ...], ...] = (
    ("analysis_status",),
    ("protocol_id",),
    ("protocol_digest",),
)
REQUIRED_RECORD_KEYS = frozenset(
    {
        "arm",
        "seed",
        "code_digest",
        "coordinate_split_digest",
        "initial_tensor_digest",
        "model_spec",
        "config",
        "training",
        "metrics",
    }
)


class ReplayVerificationError(RuntimeError):
    """Raised when a fail-closed validation condition is not met."""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ReplayVerificationError(f"required JSON file is missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReplayVerificationError(f"could not read JSON file {path}: {error}") from error
    if not isinstance(value, dict):
        raise ReplayVerificationError(f"expected a JSON object in {path}")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ReplayVerificationError(
            f"value is not canonical finite JSON: {error}"
        ) from error


def _canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _remove_exact_paths(
    value: Mapping[str, Any], paths: tuple[tuple[str, ...], ...]
) -> tuple[dict[str, Any], list[str]]:
    result = copy.deepcopy(dict(value))
    removed: list[str] = []
    for path in paths:
        cursor: Any = result
        for component in path[:-1]:
            if not isinstance(cursor, dict) or component not in cursor:
                cursor = None
                break
            cursor = cursor[component]
        if isinstance(cursor, dict) and path[-1] in cursor:
            del cursor[path[-1]]
            removed.append(".".join(path))
    return result, removed


def _deep_differences(left: Any, right: Any, *, limit: int = 100) -> list[dict[str, Any]]:
    differences: list[dict[str, Any]] = []

    def walk(a: Any, b: Any, path: str) -> None:
        if len(differences) >= limit:
            return
        if type(a) is not type(b):
            differences.append(
                {"path": path, "kind": "type", "original": type(a).__name__, "replay": type(b).__name__}
            )
            return
        if isinstance(a, dict):
            left_keys = set(a)
            right_keys = set(b)
            for key in sorted(left_keys - right_keys):
                differences.append({"path": f"{path}.{key}", "kind": "missing_in_replay"})
                if len(differences) >= limit:
                    return
            for key in sorted(right_keys - left_keys):
                differences.append({"path": f"{path}.{key}", "kind": "unexpected_in_replay"})
                if len(differences) >= limit:
                    return
            for key in sorted(left_keys & right_keys):
                walk(a[key], b[key], f"{path}.{key}")
                if len(differences) >= limit:
                    return
            return
        if isinstance(a, list):
            if len(a) != len(b):
                differences.append(
                    {"path": path, "kind": "length", "original": len(a), "replay": len(b)}
                )
                return
            for index, (left_item, right_item) in enumerate(zip(a, b, strict=True)):
                walk(left_item, right_item, f"{path}[{index}]")
                if len(differences) >= limit:
                    return
            return
        if isinstance(a, float):
            # JSON artifacts are required to contain finite values.  Comparing
            # repr preserves distinctions such as -0.0 versus 0.0.
            if not math.isfinite(a) or not math.isfinite(b) or repr(a) != repr(b):
                differences.append({"path": path, "kind": "value", "original": a, "replay": b})
            return
        if a != b:
            differences.append({"path": path, "kind": "value", "original": a, "replay": b})

    walk(left, right, "$")
    return differences


def _load_checkpoint(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ReplayVerificationError(f"checkpoint is missing: {path}")
    try:
        value = torch.load(path, map_location="cpu", weights_only=True)
    except Exception as error:  # pragma: no cover - exact torch exception varies
        raise ReplayVerificationError(f"could not safely load checkpoint {path}: {error}") from error
    if not isinstance(value, dict):
        raise ReplayVerificationError(f"checkpoint is not a dictionary: {path}")
    state = value.get("state_dict")
    if not isinstance(state, Mapping):
        raise ReplayVerificationError(f"checkpoint has no mapping state_dict: {path}")
    return value


def _tensor_bytes(value: torch.Tensor) -> bytes:
    tensor = value.detach().cpu()
    if tensor.layout != torch.strided:
        raise ReplayVerificationError(f"unsupported non-strided tensor layout: {tensor.layout}")
    tensor = tensor.contiguous().reshape(-1)
    if tensor.numel() == 0:
        return b""
    return tensor.view(torch.uint8).numpy().tobytes()


def _state_digest(state: Mapping[str, Any]) -> str:
    digest = hashlib.sha256()
    for key in sorted(state):
        value = state[key]
        if not isinstance(key, str):
            raise ReplayVerificationError(f"state_dict key is not a string: {key!r}")
        if torch.is_tensor(value):
            tensor = value.detach().cpu()
            metadata = {
                "key": key,
                "kind": "tensor",
                "dtype": str(tensor.dtype),
                "shape": list(tensor.shape),
                "layout": str(tensor.layout),
            }
            payload = _tensor_bytes(tensor)
        else:
            # PyTorch modules can expose JSON-like get_extra_state payloads in
            # state_dict under keys such as `_extra_state`.
            metadata = {"key": key, "kind": "auxiliary_json"}
            payload = _canonical_json_bytes(value)
        encoded = _canonical_json_bytes(metadata)
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _compare_states(
    original: Mapping[str, Any], replay: Mapping[str, Any]
) -> dict[str, Any]:
    original_order = list(original)
    replay_order = list(replay)
    original_keys = sorted(original)
    replay_keys = sorted(replay)
    keys_equal = original_keys == replay_keys
    key_order_equal = original_order == replay_order
    mismatches: list[dict[str, Any]] = []
    dtypes_equal = True
    shapes_equal = True
    layouts_equal = True
    tensor_data_equal = True
    auxiliary_values_equal = True
    tensor_key_count = 0
    auxiliary_key_count = 0
    max_absolute_difference = 0.0
    difference_defined = True

    for key in sorted(set(original) | set(replay)):
        if key not in original:
            mismatches.append({"key": key, "kind": "unexpected_in_replay"})
            tensor_data_equal = False
            auxiliary_values_equal = False
            difference_defined = False
            continue
        if key not in replay:
            mismatches.append({"key": key, "kind": "missing_in_replay"})
            tensor_data_equal = False
            auxiliary_values_equal = False
            difference_defined = False
            continue
        left = original[key]
        right = replay[key]
        if torch.is_tensor(left) != torch.is_tensor(right):
            mismatches.append({"key": key, "kind": "state_entry_type"})
            tensor_data_equal = False
            auxiliary_values_equal = False
            difference_defined = False
            continue
        if not torch.is_tensor(left):
            auxiliary_key_count += 1
            left_bytes = _canonical_json_bytes(left)
            right_bytes = _canonical_json_bytes(right)
            if left_bytes != right_bytes:
                auxiliary_values_equal = False
                mismatches.append(
                    {
                        "key": key,
                        "kind": "auxiliary_json",
                        "differences": _deep_differences(left, right),
                    }
                )
            continue
        tensor_key_count += 1
        if left.dtype != right.dtype:
            dtypes_equal = False
            tensor_data_equal = False
            difference_defined = False
            mismatches.append(
                {"key": key, "kind": "dtype", "original": str(left.dtype), "replay": str(right.dtype)}
            )
            continue
        if tuple(left.shape) != tuple(right.shape):
            shapes_equal = False
            tensor_data_equal = False
            difference_defined = False
            mismatches.append(
                {"key": key, "kind": "shape", "original": list(left.shape), "replay": list(right.shape)}
            )
            continue
        if left.layout != right.layout:
            layouts_equal = False
            tensor_data_equal = False
            difference_defined = False
            mismatches.append(
                {"key": key, "kind": "layout", "original": str(left.layout), "replay": str(right.layout)}
            )
            continue
        left_bytes = _tensor_bytes(left)
        right_bytes = _tensor_bytes(right)
        if left_bytes != right_bytes:
            tensor_data_equal = False
            if len(mismatches) < 100:
                mismatches.append({"key": key, "kind": "tensor_bytes"})
            try:
                difference = (
                    left.detach().cpu().to(torch.float64)
                    - right.detach().cpu().to(torch.float64)
                ).abs()
                if difference.numel():
                    candidate = float(difference.max().item())
                    if not math.isfinite(candidate):
                        difference_defined = False
                    else:
                        max_absolute_difference = max(max_absolute_difference, candidate)
            except (RuntimeError, TypeError, ValueError):
                difference_defined = False

    original_digest = _state_digest(original)
    replay_digest = _state_digest(replay)
    tensors_bitwise_equal = (
        keys_equal
        and dtypes_equal
        and shapes_equal
        and layouts_equal
        and tensor_data_equal
    )
    all_entries_equal = tensors_bitwise_equal and auxiliary_values_equal
    return {
        "keys_equal": keys_equal,
        "key_order_equal": key_order_equal,
        "dtypes_equal": dtypes_equal,
        "shapes_equal": shapes_equal,
        "layouts_equal": layouts_equal,
        "tensor_key_count": tensor_key_count,
        "auxiliary_key_count": auxiliary_key_count,
        "tensor_data_bitwise_equal": tensor_data_equal,
        "all_tensors_bitwise_equal": tensors_bitwise_equal,
        "auxiliary_values_equal": auxiliary_values_equal,
        "all_state_entries_equal": all_entries_equal,
        "original_state_sha256": original_digest,
        "replay_state_sha256": replay_digest,
        "state_sha256_equal": original_digest == replay_digest,
        "max_parameter_absolute_difference": (
            max_absolute_difference if difference_defined else None
        ),
        "mismatches": mismatches,
    }


def _checkpoint_metadata(checkpoint: Mapping[str, Any]) -> dict[str, Any]:
    metadata = dict(checkpoint)
    metadata.pop("state_dict", None)
    return metadata


def _canonical_checkpoint_digest(metadata: Mapping[str, Any], state_digest: str) -> str:
    payload = {"metadata": dict(metadata), "state_dict_sha256": state_digest}
    return _canonical_json_sha256(payload)


def _make_replay_protocol(
    primary_protocol: Mapping[str, Any], *, arm: str, seed: int
) -> dict[str, Any]:
    arms = primary_protocol.get("arms")
    seeds = primary_protocol.get("seeds")
    if not isinstance(arms, dict) or arm not in arms:
        raise ReplayVerificationError(f"arm {arm!r} is absent from the primary protocol")
    if not isinstance(seeds, list) or seed not in seeds:
        raise ReplayVerificationError(f"seed {seed} is absent from the primary protocol")
    replay = copy.deepcopy(dict(primary_protocol))
    source_protocol_id = str(primary_protocol.get("protocol_id", "unknown"))
    replay["protocol_id"] = f"{source_protocol_id}-posthoc-replay-{arm}-seed-{seed}"
    replay["analysis_status"] = "posthoc_single_cell_bitwise_reproducibility_replay"
    replay["seeds"] = [seed]
    replay["arms"] = {arm: copy.deepcopy(arms[arm])}
    replay["gates"] = []
    oracle = copy.deepcopy(replay.get("oracle", {}))
    if not isinstance(oracle, dict):
        oracle = {}
    oracle["enabled"] = False
    replay["oracle"] = oracle
    replay["transport"] = {
        "enabled": False,
        "arms": [],
        "seed_pairs": [],
        "interpretation": "Disabled for the single-cell posthoc replay.",
    }
    replay["replay_of"] = {
        "protocol_id": source_protocol_id,
        "primary_protocol_canonical_sha256": _canonical_json_sha256(
            dict(primary_protocol)
        ),
        "arm": arm,
        "seed": seed,
        "semantic_record_exclusions": [".".join(path) for path in RECORD_EXCLUDED_PATHS],
        "checkpoint_metadata_exclusions": [
            ".".join(path) for path in CHECKPOINT_METADATA_EXCLUDED_PATHS
        ],
    }
    return replay


def _run_subprocess(
    protocol_path: Path,
    replay_dir: Path,
    log_path: Path,
    *,
    device: str,
    threads: int,
) -> int:
    command = [
        sys.executable,
        str(RUNNER),
        "--protocol",
        str(protocol_path),
        "--output-dir",
        str(replay_dir),
        "--device",
        device,
        "--threads",
        str(threads),
    ]
    with log_path.open("w", encoding="utf-8") as log:
        log.write("COMMAND " + json.dumps(command) + "\n")
        log.flush()
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log.write(line)
            log.flush()
        return process.wait()


def _validate_primary_receipts(
    primary_dir: Path,
    protocol: Mapping[str, Any],
    record: Mapping[str, Any],
    checkpoint: Mapping[str, Any],
    *,
    arm: str,
    seed: int,
) -> dict[str, Any]:
    receipt = _read_json(primary_dir / "RECEIPT.json")
    grid = _read_json(primary_dir / "GRID_AUDIT.json")
    protocol_sha = _sha256_file(primary_dir / "PROTOCOL.json")
    expected_cells = len(protocol.get("arms", {})) * len(protocol.get("seeds", []))
    checks = {
        "receipt_status_complete": receipt.get("status") == "complete",
        "receipt_grid_complete": receipt.get("grid_complete") is True,
        "grid_audit_complete": grid.get("complete") is True,
        "grid_audit_has_no_missing_cells": grid.get("missing_cells") == [],
        "grid_audit_has_no_unexpected_cells": grid.get("unexpected_cells") == [],
        "grid_audit_counts_match": (
            isinstance(grid.get("expected_cells"), int)
            and grid.get("expected_cells") == expected_cells
            and grid.get("observed_cells") == expected_cells
        ),
        "arm_in_receipt": arm in receipt.get("arms", []),
        "seed_in_receipt": seed in receipt.get("seeds", []),
        "record_arm_matches": record.get("arm") == arm,
        "record_seed_matches": record.get("seed") == seed,
        "checkpoint_arm_matches": checkpoint.get("arm") == arm,
        "checkpoint_seed_matches": checkpoint.get("seed") == seed,
        "record_protocol_digest_matches_file": record.get("protocol_digest") == protocol_sha,
        "checkpoint_protocol_digest_matches_file": checkpoint.get("protocol_digest") == protocol_sha,
        "receipt_protocol_digest_matches_file": receipt.get("protocol_digest") == protocol_sha,
        "protocol_id_consistent": (
            protocol.get("protocol_id")
            == receipt.get("protocol_id")
            == record.get("protocol_id")
            == checkpoint.get("protocol_id")
        ),
        "code_digest_consistent": (
            receipt.get("code_digest")
            == record.get("code_digest")
            == checkpoint.get("code_digest")
            == protocol.get("expected_code_digest")
        ),
        "coordinate_split_digest_consistent": (
            receipt.get("coordinate_split_digest")
            == record.get("coordinate_split_digest")
            == checkpoint.get("coordinate_split_digest")
            == protocol.get("expected_coordinate_split_digest")
        ),
        "package_version_consistent": (
            protocol.get("package_version")
            == receipt.get("package_version")
            == record.get("package_version")
            == checkpoint.get("package_version")
        ),
        "config_consistent": record.get("config") == checkpoint.get("config"),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ReplayVerificationError(
            "primary provenance validation failed: " + ", ".join(failed)
        )
    return checks


def _default_runtime(receipt: Mapping[str, Any]) -> tuple[str, int]:
    environment = receipt.get("environment", {})
    observed_device = str(environment.get("device", "cpu"))
    device = "cuda" if observed_device.startswith("cuda") else "cpu"
    try:
        threads = int(environment.get("torch_threads", 4))
    except (TypeError, ValueError):
        threads = 4
    return device, max(1, threads)


def _record_schema_valid(record: Mapping[str, Any]) -> bool:
    return bool(
        REQUIRED_RECORD_KEYS <= set(record)
        and isinstance(record.get("model_spec"), dict)
        and isinstance(record.get("config"), dict)
        and isinstance(record.get("training"), dict)
        and "elapsed_seconds" in record["training"]
        and isinstance(record.get("metrics"), dict)
    )


def _markdown(report: Mapping[str, Any]) -> str:
    validation = report.get("validation", {})
    state = validation.get("state_dict", {})
    outcome = "PASS" if report.get("overall_passed") else "FAIL"
    lines = [
        "# v0.3 single-cell reproducibility replay",
        "",
        f"**Outcome: {outcome}.**",
        "",
        f"Arm: `{report.get('arm')}`  ",
        f"Seed: `{report.get('seed')}`",
        "",
        "## Exact comparisons",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| Metric JSON, recursively exact | `{validation.get('metrics_exactly_equal')}` |",
        f"| Semantic arm record, recursively exact | `{validation.get('semantic_record_exactly_equal')}` |",
        f"| State keys and order equal | `{state.get('keys_equal') and state.get('key_order_equal')}` |",
        f"| State dtypes/shapes/layouts equal | `{state.get('dtypes_equal') and state.get('shapes_equal') and state.get('layouts_equal')}` |",
        f"| Every state tensor byte equal | `{state.get('all_tensors_bitwise_equal')}` |",
        f"| Auxiliary module state equal | `{state.get('auxiliary_values_equal')}` |",
        f"| Canonical state SHA-256 equal | `{state.get('state_sha256_equal')}` |",
        f"| Checkpoint metadata equal after declared provenance exclusions | `{validation.get('checkpoint_metadata_equal_after_exclusions')}` |",
        f"| Canonical checkpoint SHA-256 equal | `{validation.get('canonical_checkpoint_sha256_equal')}` |",
        f"| Raw `torch.save` file SHA-256 equal (informational) | `{validation.get('raw_checkpoint_sha256_equal')}` |",
        "",
        "The raw checkpoint file hash is informational because the replay uses a new",
        "protocol identifier and protocol digest. The pass criterion instead uses a",
        "canonical checkpoint hash that excludes only those declared provenance fields",
        "and includes the exact bytes of every state tensor.",
        "",
        "## Declared exclusions",
        "",
        "Semantic record: "
        + ", ".join(f"`{item}`" for item in report.get("exclusions", {}).get("semantic_record", [])),
        "",
        "Checkpoint metadata: "
        + ", ".join(f"`{item}`" for item in report.get("exclusions", {}).get("checkpoint_metadata", [])),
        "",
        "Metric JSON has no exclusions.",
    ]
    mismatches = report.get("mismatches", [])
    if mismatches:
        lines.extend(["", "## Mismatches", "", "```json", json.dumps(mismatches, indent=2, sort_keys=True), "```"])
    lines.append("")
    return "\n".join(lines)


def _self_check() -> int:
    original_state = {
        "weight": torch.tensor([[1.0, -0.0], [3.5, 4.0]], dtype=torch.float32),
        "index": torch.tensor([1, 2, 3], dtype=torch.int64),
    }
    matching_state = {key: value.clone() for key, value in original_state.items()}
    changed_state = {key: value.clone() for key, value in original_state.items()}
    changed_state["weight"][0, 0] += 1.0
    exact = _compare_states(original_state, matching_state)
    changed = _compare_states(original_state, changed_state)

    left_record = {
        "protocol_id": "primary",
        "protocol_digest": "a",
        "analysis_status": "primary",
        "training": {"elapsed_seconds": 1.0, "final_loss": 0.25},
        "metrics": {"accuracy": 1.0},
    }
    right_record = copy.deepcopy(left_record)
    right_record["protocol_id"] = "replay"
    right_record["protocol_digest"] = "b"
    right_record["analysis_status"] = "posthoc"
    right_record["training"]["elapsed_seconds"] = 2.0
    left_semantic, _ = _remove_exact_paths(left_record, RECORD_EXCLUDED_PATHS)
    right_semantic, _ = _remove_exact_paths(right_record, RECORD_EXCLUDED_PATHS)
    exclusions_work = _canonical_json_bytes(left_semantic) == _canonical_json_bytes(right_semantic)
    right_record["metrics"]["accuracy"] = 0.5
    changed_semantic, _ = _remove_exact_paths(right_record, RECORD_EXCLUDED_PATHS)
    semantic_change_detected = _canonical_json_bytes(left_semantic) != _canonical_json_bytes(changed_semantic)
    passed = bool(
        exact["all_tensors_bitwise_equal"]
        and exact["state_sha256_equal"]
        and not changed["all_tensors_bitwise_equal"]
        and not changed["state_sha256_equal"]
        and exclusions_work
        and semantic_change_detected
    )
    result = {
        "self_check_passed": passed,
        "exact_tensor_match_detected": exact["all_tensors_bitwise_equal"],
        "tensor_change_detected": not changed["all_tensors_bitwise_equal"],
        "declared_exclusions_work": exclusions_work,
        "semantic_change_detected": semantic_change_detected,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


def verify(args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    primary_dir = args.primary_dir.resolve()
    if not primary_dir.is_dir():
        raise ReplayVerificationError(f"primary directory does not exist: {primary_dir}")
    output_dir = (
        args.output_dir
        or (primary_dir.parent / "stage_a_reproducibility")
    ).resolve()
    if output_dir == primary_dir or output_dir.is_relative_to(primary_dir):
        raise ReplayVerificationError(
            "output directory must be separate from, and not inside, the immutable primary directory"
        )
    if primary_dir.is_relative_to(output_dir):
        raise ReplayVerificationError(
            "output directory must not contain the immutable primary directory"
        )
    if output_dir.exists() and not output_dir.is_dir():
        raise ReplayVerificationError(
            f"output path exists and is not a directory: {output_dir}"
        )
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ReplayVerificationError(
            f"output directory must be absent or empty: {output_dir}"
        )
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    report_json = output_dir / "REPRODUCIBILITY.json"
    report_md = output_dir / "REPRODUCIBILITY.md"
    replay_dir = output_dir
    replay_protocol_path = output_dir / "REPLAY_PROTOCOL.json"
    replay_log_path = output_dir / "REPLAY.log"

    primary_protocol_path = primary_dir / "PROTOCOL.json"
    primary_protocol = _read_json(primary_protocol_path)
    primary_record_path = primary_dir / "arms" / args.arm / f"seed_{args.seed}.json"
    primary_checkpoint_path = primary_dir / "checkpoints" / args.arm / f"seed_{args.seed}.pt"
    primary_record = _read_json(primary_record_path)
    primary_checkpoint = _load_checkpoint(primary_checkpoint_path)
    primary_checks = _validate_primary_receipts(
        primary_dir,
        primary_protocol,
        primary_record,
        primary_checkpoint,
        arm=args.arm,
        seed=args.seed,
    )
    primary_receipt = _read_json(primary_dir / "RECEIPT.json")
    default_device, default_threads = _default_runtime(primary_receipt)
    device = args.device or default_device
    threads = args.threads or default_threads

    replay_protocol = _make_replay_protocol(
        primary_protocol, arm=args.arm, seed=args.seed
    )
    temporary_protocol_handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=f".v03_replay_protocol_{args.arm}_{args.seed}_",
        suffix=".json",
        dir=output_dir.parent,
        delete=False,
    )
    temporary_protocol_path = Path(temporary_protocol_handle.name)
    temporary_log_handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=f".v03_replay_log_{args.arm}_{args.seed}_",
        suffix=".log",
        dir=output_dir.parent,
        delete=False,
    )
    temporary_log_path = Path(temporary_log_handle.name)
    temporary_log_handle.close()
    try:
        temporary_protocol_handle.write(
            json.dumps(
                replay_protocol,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n"
        )
        temporary_protocol_handle.close()
        return_code = _run_subprocess(
            temporary_protocol_path,
            replay_dir,
            temporary_log_path,
            device=device,
            threads=threads,
        )
        if replay_dir.is_dir():
            copied_protocol = replay_dir / "PROTOCOL.json"
            if copied_protocol.is_file():
                shutil.copyfile(copied_protocol, replay_protocol_path)
    finally:
        if not temporary_protocol_handle.closed:
            temporary_protocol_handle.close()
        if replay_dir.is_dir() and temporary_log_path.is_file():
            shutil.copyfile(temporary_log_path, replay_log_path)
        temporary_protocol_path.unlink(missing_ok=True)
        temporary_log_path.unlink(missing_ok=True)
    if return_code != 0:
        raise ReplayVerificationError(
            f"run_experiment.py returned {return_code}; see {replay_log_path}"
        )

    replay_receipt = _read_json(replay_dir / "RECEIPT.json")
    replay_grid = _read_json(replay_dir / "GRID_AUDIT.json")
    replay_protocol_from_run = _read_json(replay_dir / "PROTOCOL.json")
    replay_protocol_sha = _sha256_file(replay_dir / "PROTOCOL.json")
    replay_record_path = replay_dir / "arms" / args.arm / f"seed_{args.seed}.json"
    replay_checkpoint_path = replay_dir / "checkpoints" / args.arm / f"seed_{args.seed}.pt"
    replay_record = _read_json(replay_record_path)
    replay_checkpoint = _load_checkpoint(replay_checkpoint_path)
    replay_checks = {
        "receipt_status_complete": replay_receipt.get("status") == "complete",
        "receipt_grid_complete": replay_receipt.get("grid_complete") is True,
        "receipt_single_arm": replay_receipt.get("arms") == [args.arm],
        "receipt_single_seed": replay_receipt.get("seeds") == [args.seed],
        "grid_audit_complete": replay_grid.get("complete") is True,
        "grid_audit_exactly_one_cell": (
            replay_grid.get("expected_cells") == 1
            and replay_grid.get("observed_cells") == 1
            and replay_grid.get("missing_cells") == []
            and replay_grid.get("unexpected_cells") == []
        ),
        "record_arm_matches": replay_record.get("arm") == args.arm,
        "record_seed_matches": replay_record.get("seed") == args.seed,
        "checkpoint_arm_matches": replay_checkpoint.get("arm") == args.arm,
        "checkpoint_seed_matches": replay_checkpoint.get("seed") == args.seed,
        "protocol_copy_exact": (
            _canonical_json_bytes(replay_protocol_from_run)
            == _canonical_json_bytes(replay_protocol)
            and _sha256_file(replay_protocol_path) == replay_protocol_sha
        ),
        "protocol_digest_consistent": (
            replay_receipt.get("protocol_digest")
            == replay_record.get("protocol_digest")
            == replay_checkpoint.get("protocol_digest")
            == replay_protocol_sha
        ),
        "protocol_id_consistent": (
            replay_protocol.get("protocol_id")
            == replay_receipt.get("protocol_id")
            == replay_record.get("protocol_id")
            == replay_checkpoint.get("protocol_id")
        ),
        "analysis_status_consistent": (
            replay_protocol.get("analysis_status")
            == replay_receipt.get("analysis_status")
            == replay_record.get("analysis_status")
            == replay_checkpoint.get("analysis_status")
        ),
        "code_digest_matches_primary": (
            replay_receipt.get("code_digest")
            == replay_record.get("code_digest")
            == replay_checkpoint.get("code_digest")
            == primary_record.get("code_digest")
        ),
        "coordinate_split_digest_matches_primary": (
            replay_receipt.get("coordinate_split_digest")
            == replay_record.get("coordinate_split_digest")
            == replay_checkpoint.get("coordinate_split_digest")
            == primary_record.get("coordinate_split_digest")
        ),
        "package_version_consistent": (
            replay_protocol.get("package_version")
            == replay_receipt.get("package_version")
            == replay_record.get("package_version")
            == replay_checkpoint.get("package_version")
            == primary_protocol.get("package_version")
        ),
        "config_consistent": replay_record.get("config") == replay_checkpoint.get("config"),
        "primary_semantic_record_schema_valid": _record_schema_valid(primary_record),
        "replay_semantic_record_schema_valid": _record_schema_valid(replay_record),
    }

    state_comparison = _compare_states(
        primary_checkpoint["state_dict"], replay_checkpoint["state_dict"]
    )

    original_metrics = primary_record.get("metrics")
    replay_metrics = replay_record.get("metrics")
    metric_differences = _deep_differences(original_metrics, replay_metrics)
    metrics_equal = (
        not metric_differences
        and _canonical_json_bytes(original_metrics) == _canonical_json_bytes(replay_metrics)
    )

    original_semantic_record, original_record_exclusions = _remove_exact_paths(
        primary_record, RECORD_EXCLUDED_PATHS
    )
    replay_semantic_record, replay_record_exclusions = _remove_exact_paths(
        replay_record, RECORD_EXCLUDED_PATHS
    )
    semantic_record_differences = _deep_differences(
        original_semantic_record, replay_semantic_record
    )
    semantic_records_equal = (
        not semantic_record_differences
        and _canonical_json_bytes(original_semantic_record)
        == _canonical_json_bytes(replay_semantic_record)
    )

    original_metadata = _checkpoint_metadata(primary_checkpoint)
    replay_metadata = _checkpoint_metadata(replay_checkpoint)
    original_canonical_metadata, original_checkpoint_exclusions = _remove_exact_paths(
        original_metadata, CHECKPOINT_METADATA_EXCLUDED_PATHS
    )
    replay_canonical_metadata, replay_checkpoint_exclusions = _remove_exact_paths(
        replay_metadata, CHECKPOINT_METADATA_EXCLUDED_PATHS
    )
    metadata_differences = _deep_differences(
        original_canonical_metadata, replay_canonical_metadata
    )
    metadata_equal = (
        not metadata_differences
        and _canonical_json_bytes(original_canonical_metadata)
        == _canonical_json_bytes(replay_canonical_metadata)
    )
    original_canonical_checkpoint_sha = _canonical_checkpoint_digest(
        original_canonical_metadata, state_comparison["original_state_sha256"]
    )
    replay_canonical_checkpoint_sha = _canonical_checkpoint_digest(
        replay_canonical_metadata, state_comparison["replay_state_sha256"]
    )

    original_raw_checkpoint_sha = _sha256_file(primary_checkpoint_path)
    replay_raw_checkpoint_sha = _sha256_file(replay_checkpoint_path)
    canonical_checkpoint_equal = (
        original_canonical_checkpoint_sha == replay_canonical_checkpoint_sha
    )
    exclusions_symmetric = (
        original_record_exclusions == replay_record_exclusions
        and original_checkpoint_exclusions == replay_checkpoint_exclusions
    )
    required_checks = {
        "primary_provenance": all(primary_checks.values()),
        "replay_provenance": all(replay_checks.values()),
        "exclusions_symmetric": exclusions_symmetric,
        "metrics_exactly_equal": metrics_equal,
        "semantic_record_exactly_equal": semantic_records_equal,
        "state_keys_equal": state_comparison["keys_equal"],
        "state_key_order_equal": state_comparison["key_order_equal"],
        "state_dtypes_equal": state_comparison["dtypes_equal"],
        "state_shapes_equal": state_comparison["shapes_equal"],
        "state_layouts_equal": state_comparison["layouts_equal"],
        "state_tensor_bytes_equal": state_comparison["all_tensors_bitwise_equal"],
        "state_auxiliary_values_equal": state_comparison["auxiliary_values_equal"],
        "state_contains_tensors": state_comparison["tensor_key_count"] > 0,
        "state_sha256_equal": state_comparison["state_sha256_equal"],
        "checkpoint_metadata_equal_after_exclusions": metadata_equal,
        "canonical_checkpoint_sha256_equal": canonical_checkpoint_equal,
    }
    overall_passed = all(required_checks.values())
    mismatches = []
    if metric_differences:
        mismatches.append({"scope": "metrics", "differences": metric_differences})
    if semantic_record_differences:
        mismatches.append(
            {"scope": "semantic_record", "differences": semantic_record_differences}
        )
    if state_comparison["mismatches"]:
        mismatches.append(
            {"scope": "state_dict", "differences": state_comparison["mismatches"]}
        )
    if metadata_differences:
        mismatches.append(
            {"scope": "checkpoint_metadata", "differences": metadata_differences}
        )
    failed_required = [name for name, passed in required_checks.items() if not passed]
    if failed_required:
        mismatches.append({"scope": "required_checks", "failed": failed_required})

    report: dict[str, Any] = {
        "schema_version": 1,
        "analysis_status": "posthoc_single_cell_reproducibility_check",
        "status": "pass" if overall_passed else "fail",
        "overall_passed": overall_passed,
        "package_version": primary_protocol.get("package_version"),
        "arm": args.arm,
        "seed": args.seed,
        "runtime": {
            "python_executable": sys.executable,
            "device": device,
            "torch_threads": threads,
            "subprocess_return_code": return_code,
        },
        "paths": {
            "primary_dir": str(primary_dir),
            "replay_dir": str(replay_dir),
            "replay_protocol": str(replay_protocol_path),
            "replay_log": str(replay_log_path),
        },
        "protocols": {
            "primary_protocol_id": primary_protocol.get("protocol_id"),
            "primary_protocol_sha256": _sha256_file(primary_protocol_path),
            "replay_protocol_id": replay_protocol.get("protocol_id"),
            "replay_protocol_sha256": _sha256_file(replay_protocol_path),
        },
        "exclusions": {
            "semantic_record": [".".join(path) for path in RECORD_EXCLUDED_PATHS],
            "checkpoint_metadata": [
                ".".join(path) for path in CHECKPOINT_METADATA_EXCLUDED_PATHS
            ],
            "metrics": [],
        },
        "primary_provenance_checks": primary_checks,
        "replay_provenance_checks": replay_checks,
        "validation": {
            **required_checks,
            "state_dict": state_comparison,
            "original_semantic_record_sha256": _canonical_json_sha256(
                original_semantic_record
            ),
            "replay_semantic_record_sha256": _canonical_json_sha256(
                replay_semantic_record
            ),
            "original_metrics_sha256": _canonical_json_sha256(original_metrics),
            "replay_metrics_sha256": _canonical_json_sha256(replay_metrics),
            "original_canonical_checkpoint_sha256": original_canonical_checkpoint_sha,
            "replay_canonical_checkpoint_sha256": replay_canonical_checkpoint_sha,
            "original_raw_checkpoint_sha256": original_raw_checkpoint_sha,
            "replay_raw_checkpoint_sha256": replay_raw_checkpoint_sha,
            "raw_checkpoint_sha256_equal": (
                original_raw_checkpoint_sha == replay_raw_checkpoint_sha
            ),
        },
        # Compatibility fields used by the previous package verifier.
        "metrics_exactly_equal": metrics_equal,
        "metric_difference_count": len(metric_differences),
        "state_keys_equal": state_comparison["keys_equal"],
        "max_parameter_absolute_difference": state_comparison[
            "max_parameter_absolute_difference"
        ],
        "mismatches": mismatches,
    }
    _write_json(report_json, report)
    report_md.write_text(_markdown(report), encoding="utf-8")
    return report, report_json


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay one v0.3 primary cell and verify exact reproducibility"
    )
    parser.add_argument("--primary-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--arm", default="hard_correct")
    parser.add_argument("--seed", type=int, default=300)
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"))
    parser.add_argument("--threads", type=int)
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="exercise comparison primitives without launching training",
    )
    args = parser.parse_args()
    if args.self_check:
        return _self_check()
    if args.primary_dir is None:
        parser.error("--primary-dir is required unless --self-check is used")
    if args.threads is not None and args.threads < 1:
        parser.error("--threads must be at least 1")

    primary_dir = args.primary_dir.resolve()
    output_dir = (
        args.output_dir
        or (primary_dir.parent / "stage_a_reproducibility")
    ).resolve()
    unsafe_output = (
        output_dir == primary_dir
        or output_dir.is_relative_to(primary_dir)
        or primary_dir.is_relative_to(output_dir)
    )
    if unsafe_output:
        failure = {
            "schema_version": 1,
            "analysis_status": "posthoc_single_cell_reproducibility_check",
            "status": "fail",
            "overall_passed": False,
            "arm": args.arm,
            "seed": args.seed,
            "error": (
                "ReplayVerificationError: output directory must be separate from "
                "the immutable primary directory"
            ),
        }
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        return 1
    if output_dir.exists() and not output_dir.is_dir():
        failure = {
            "schema_version": 1,
            "analysis_status": "posthoc_single_cell_reproducibility_check",
            "status": "fail",
            "overall_passed": False,
            "arm": args.arm,
            "seed": args.seed,
            "error": "ReplayVerificationError: output path exists and is not a directory",
        }
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        return 1
    preexisting_nonempty = output_dir.exists() and any(output_dir.iterdir())
    report_path = output_dir / "REPRODUCIBILITY.json"
    markdown_path = output_dir / "REPRODUCIBILITY.md"
    try:
        report, _ = verify(args)
    except Exception as error:
        failure = {
            "schema_version": 1,
            "analysis_status": "posthoc_single_cell_reproducibility_check",
            "status": "fail",
            "overall_passed": False,
            "arm": args.arm,
            "seed": args.seed,
            "error": f"{type(error).__name__}: {error}",
        }
        # Never mutate a directory that was already occupied when invoked.
        if not preexisting_nonempty:
            output_dir.mkdir(parents=True, exist_ok=True)
            if not report_path.exists():
                _write_json(report_path, failure)
            if not markdown_path.exists():
                markdown_path.write_text(
                    "# v0.3 single-cell reproducibility replay\n\n"
                    f"**Outcome: FAIL.**\n\n`{failure['error']}`\n",
                    encoding="utf-8",
                )
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["overall_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
