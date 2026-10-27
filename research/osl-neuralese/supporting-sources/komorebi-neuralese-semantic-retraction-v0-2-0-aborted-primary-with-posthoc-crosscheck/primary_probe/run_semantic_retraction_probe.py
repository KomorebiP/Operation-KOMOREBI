#!/usr/bin/env python3
"""Frozen-checkpoint semantic-retraction and finite decision trace-agreement probe.

This module is deliberately external to the v0.4 source archive.  Its default
entry point cannot touch learned checkpoints. A learned-panel run is enabled
only after the frozen protocol byte digest matches the machine contract and a
separate static-review release matches both protocol and implementation bytes.

The model path is kept in torch.float32, including table encoding, hard-polar
SVD, recurrence, interventions, normalization, decoding, and continuation.
Only detached diagnostic copies are promoted to numpy.float64.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import gc
import hashlib
import importlib
import io
import itertools
import json
import math
import os
from pathlib import Path, PurePosixPath
import resource
import shutil
import stat
import sys
import time
from types import SimpleNamespace
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import torch
from torch import nn


AUTHOR = "Komorebi P."
VERSION = "0.2.0"
SCHEMA = "komorebi.neuralese.semantic_retraction_probe.v1"
ANALYSIS_STATUS = "POSTHOC_FROZEN_CHECKPOINT_PROBE"
CLAIM_BOUNDARY = (
    "Posthoc audit of sealed learned checkpoints. This cannot repair, replace, "
    "or supersede any original v0.4 confirmatory gate."
)
DECLARED_PEAK_WORKING_SET_CEILING_BYTES = 768 * 1024 * 1024
TORCH_INTRAOP_THREADS = 1
TORCH_INTEROP_THREADS = 1
MAXIMUM_CHECKPOINT_SHARD_BYTES = 64 * 1024 * 1024
MAXIMUM_EXACT_CONTROL_BYTES = 96 * 1024 * 1024
MAXIMUM_BUNDLE_METADATA_BYTES = 64 * 1024 * 1024
RESULT_DISK_SAFETY_MARGIN_BYTES = 256 * 1024 * 1024
MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND = (
    12 * MAXIMUM_CHECKPOINT_SHARD_BYTES
    + MAXIMUM_EXACT_CONTROL_BYTES
    + MAXIMUM_BUNDLE_METADATA_BYTES
    + RESULT_DISK_SAFETY_MARGIN_BYTES
)

PRIOR_CONTEXT_SEED = 2026090301
CALIBRATION_CONTEXT_SEED = 2026090311
EVALUATION_CONTEXT_SEED = 2026090312
CONTEXT_COUNT = 32
CALIBRATION_PATH_SEED = 2026090321
EVALUATION_PATH_SEED = 2026090322
STRESS_PATH_SEED = 2026090323
RANDOM_RAY_SEED = 2026090324
NOMINAL_DEPTH_BANDS = (8, 32, 64)
PAIRS_PER_ENDPOINT_BAND = 2
CONTINUATION_MAX_LENGTH = 4
INTERVENTION_NAMES = (
    "native_h",
    "native_h_prime",
    "sham_scale",
    "oracle_anchor",
    "self_anchor",
    "nearest_anchor",
    "oracle_prototype",
    "self_prototype",
    "anchor_projection",
    "wrong_anchor",
    "wrong_prototype",
    "random_ray",
)
PERIODIC_CONDITION_NAMES = (
    "native",
    "sham_scale",
    "oracle_anchor",
    "self_anchor",
    "nearest_anchor",
    "self_prototype",
    "anchor_projection",
)
PERIODIC_CADENCES = (1, 4, 8, 16)
SUFFIX_STRATUM_NAMES = (
    "empty",
    "length_1",
    "length_2",
    "length_3",
    "length_4",
    "nonempty",
    "all",
)
EXPECTED_ARCHIVE_SHA256 = (
    "4132faa934e94647ec267c0140240397b459c68b6770e95edc30144c39f3662d"
)
EXPECTED_PACKAGE_MANIFEST_SHA256 = (
    "10f9b59dc7a233dbccad772fa223cd51a8866c18e799c9227c7c3d1a2b5dab8a"
)

HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parents[1]
PROTOCOL_PATH = HERE.parent / "ANALYSIS_PROTOCOL.md"
THEORETICAL_FRAMEWORK_PATH = HERE.parent / "THEORETICAL_FRAMEWORK.md"
ROOT_PROTOCOL_RECEIPT_PATH = HERE.parent / "PROTOCOL_RECEIPT.json"
MACHINE_CONTRACT_PATH = HERE / "PROTOCOL.json"
STATIC_REVIEW_RELEASE_PATH = HERE / "STATIC_REVIEW_PASS.json"
MANIFEST_DRY_RUN_PATH = HERE / "MANIFEST_DRY_RUN.json"
TEST_PATH = HERE / "test_semantic_retraction_probe.py"
EVALUATION_BANK_SPEND_PATH = HERE / "EVALUATION_BANK_SPENT.json"
INDEPENDENT_CROSSCHECK_ROOT = HERE.parent / "independent_crosscheck"
INDEPENDENT_CROSSCHECK_PROTOCOL_PATH = INDEPENDENT_CROSSCHECK_ROOT / "PROTOCOL.json"
INDEPENDENT_CROSSCHECK_IMPLEMENTATION_PATH = (
    INDEPENDENT_CROSSCHECK_ROOT / "probe_null_retraction.py"
)
INDEPENDENT_CROSSCHECK_TEST_PATH = (
    INDEPENDENT_CROSSCHECK_ROOT / "test_null_retraction.py"
)
INDEPENDENT_CROSSCHECK_FREEZE_RECEIPT_PATH = (
    INDEPENDENT_CROSSCHECK_ROOT / "FROZEN_PROTOCOL.sha256"
)
DEFAULT_RESULT_BUNDLE = HERE / "RESULTS.bundle"
DEFAULT_CONTROL_OUTPUT = HERE / "EXACT_CONTROL_STANDALONE.json"
RUN_FILENAME = "RUN.json"
EXACT_CONTROL_FILENAME = "EXACT_CONTROL.json"
SPEND_RECEIPT_FILENAME = "SPEND_RECEIPT.json"
BUNDLE_MANIFEST_FILENAME = "MANIFEST.json"
COMMIT_FILENAME = "COMMIT.json"
CHECKPOINT_DIRECTORY_NAME = "checkpoints"
REQUIRED_RESULT_BUNDLE_SUFFIX = ".bundle"
REQUIRED_FROZEN_PROTOCOL_HEADER = (
    "Freeze state: FROZEN BEFORE LEARNED OUTCOMES — terminal receipt required"
)
REQUIRED_STATIC_REVIEW_CHECKS = (
    "normative_protocol_matches_runtime_contract",
    "checkpoint_free_manifest_matches_runtime",
    "sealed_source_import_and_checkpoint_census_fail_closed",
    "evaluation_banks_random_stream_and_thresholds_are_frozen",
    "exact_controls_and_test_suite_pass",
    "resource_budget_and_disk_headroom_pass",
    "exclusive_commit_last_bundle_and_spend_firewall_pass",
    "independent_crosscheck_is_frozen_and_checkpoint_free",
    "no_learned_checkpoint_was_loaded_or_inspected",
)
REQUIRED_SPEND_RECEIPT_KEYS = (
    "schema",
    "version",
    "author",
    "status",
    "created_unix_time_ns",
    "no_rerun_or_resume_is_prospective",
    "crash_after_this_receipt_still_spends_bank",
    "planned_bundle_leaf_name",
    "planned_bundle_absolute_path_non_normative",
    "protocol_sha256",
    "implementation_sha256",
    "test_sha256",
    "machine_contract_sha256",
    "manifest_file_sha256",
    "manifest_freeze_receipt_sha256",
    "static_review_file_sha256",
    "theoretical_framework_sha256",
    "root_protocol_receipt_file_sha256",
    "root_protocol_receipt_internal_sha256",
    "source_archive_sha256",
    "source_package_manifest_sha256",
    "evaluation_context_sha256",
    "evaluation_path_sha256",
    "continuation_sha256",
    "random_key_manifest_sha256",
    "exact_control_sha256",
    "receipt_sha256",
)
REQUIRED_ARMS = (
    "euclidean_supervised",
    "euclidean_cr",
    "polar_supervised",
    "polar_cr",
)
REQUIRED_SEEDS = (101, 211, 307)
REQUIRED_PASS_BEARING_CLAIM_LABELS = (
    "NATIVE_FINITE_DECISION_TRACE_AGREEMENT_H4_COVERAGE_0.99",
    "NATIVE_FINITE_LOGIT_TRACE_AGREEMENT_H4_P95",
    "ORACLE_ANCHOR_SEMANTIC_REPAIR_INTERFACE",
    "ORACLE_PROTOTYPE_SEMANTIC_REPAIR_INTERFACE",
    "AUTONOMOUS_ONE_SHOT_RETRACTION__SELF_ANCHOR",
    "AUTONOMOUS_ONE_SHOT_RETRACTION__NEAREST_ANCHOR",
    "AUTONOMOUS_ONE_SHOT_RETRACTION__SELF_PROTOTYPE",
    "AUTONOMOUS_PERIODIC_DEPTH_REPAIR__SELF_ANCHOR",
    "AUTONOMOUS_PERIODIC_DEPTH_REPAIR__NEAREST_ANCHOR",
    "AUTONOMOUS_PERIODIC_DEPTH_REPAIR__SELF_PROTOTYPE",
    "PERIODIC_ANCHOR_SPAN_PROJECTION_REPAIR",
)
REQUIRED_ROOT_ARTIFACT_KEYS = (
    "analysis_protocol",
    "theoretical_framework",
    "primary_implementation",
    "primary_tests",
    "primary_machine_contract",
    "primary_manifest_dry_run",
    "primary_static_review",
    "independent_crosscheck_protocol",
    "independent_crosscheck_implementation",
    "independent_crosscheck_tests",
    "independent_crosscheck_freeze_receipt",
)
REQUIRED_EXACT_CONTROL_KEYS = (
    "schema",
    "version",
    "author",
    "source",
    "torch_thread_runtime",
    "context_bank",
    "path_bank",
    "continuation_bank",
    "audit",
    "result",
    "periodic",
)
REQUIRED_CHECKPOINT_SHARD_KEYS = (
    "schema",
    "version",
    "author",
    "arm",
    "seed",
    "model_family",
    "checkpoint_filename",
    "checkpoint_sha256",
    "whole_analysis_state_dict_control",
    "prototype_audit",
    "one_shot_primary",
    "one_shot_stress_descriptive",
    "periodic",
    "independent_claim_matrix",
)
REQUIRED_RUN_KEYS = (
    "schema",
    "version",
    "author",
    "analysis_status",
    "result_validity",
    "claim_boundary",
    "protocol",
    "source",
    "runtime",
    "context_banks",
    "path_banks",
    "continuation_bank",
    "random_key_manifest",
    "evaluation_bank_spend_receipt",
    "exact_compiled_control",
    "checkpoint_results",
    "arm_level_independent_claim_matrix",
    "output_layout",
)
REQUIRED_CHECKPOINT_SUMMARY_KEYS = (
    "arm",
    "seed",
    "model_family",
    "checkpoint_filename",
    "checkpoint_sha256",
    "checkpoint_shard",
    "checkpoint_shard_sha256",
    "checkpoint_shard_bytes",
    "whole_analysis_state_dict_unchanged",
    "independent_claim_matrix",
)
DEFAULT_ARCHIVE = (
    WORK_ROOT
    / "learned_archive_retry"
    / "Komorebi_Neuralese_Packet_Closure_v0.4.0.zip"
)
DEFAULT_PACKAGE = (
    WORK_ROOT
    / "learned_archive_retry"
    / "extracted_v04"
    / "Komorebi_Neuralese_Packet_Closure_v0.4.0"
)


def configure_frozen_torch_threads() -> dict[str, int]:
    """Pin tiny CPU kernels to the deterministic single-thread execution lane."""

    torch.set_num_threads(TORCH_INTRAOP_THREADS)
    if torch.get_num_interop_threads() != TORCH_INTEROP_THREADS:
        try:
            torch.set_num_interop_threads(TORCH_INTEROP_THREADS)
        except RuntimeError as exc:
            raise RuntimeError(
                "torch inter-op pool was initialized before the frozen thread pin"
            ) from exc
    receipt = {
        "intraop_threads": int(torch.get_num_threads()),
        "interop_threads": int(torch.get_num_interop_threads()),
    }
    if receipt != {
        "intraop_threads": TORCH_INTRAOP_THREADS,
        "interop_threads": TORCH_INTEROP_THREADS,
    }:
        raise RuntimeError("torch thread runtime differs from the frozen single-thread lane")
    return receipt


FROZEN_TORCH_THREAD_RECEIPT = configure_frozen_torch_threads()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def is_sha256_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def type_strict_equal(left: Any, right: Any) -> bool:
    """Recursively compare values without Python's bool/int numeric coercion."""

    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        if len(left) != len(right) or set(left) != set(right):
            return False
        return all(type_strict_equal(left[key], right[key]) for key in left)
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(
            type_strict_equal(first, second)
            for first, second in zip(left, right, strict=True)
        )
    return bool(left == right)


def _reject_nonfinite_json_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON constant is forbidden: {value}")


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key is forbidden: {key}")
        result[key] = value
    return result


def loads_json_bytes_strict(payload: bytes) -> Any:
    """Decode strict JSON from the exact bytes supplied by the caller."""

    return json.loads(
        payload.decode("utf-8"),
        parse_constant=_reject_nonfinite_json_constant,
        object_pairs_hook=_reject_duplicate_json_keys,
    )


def read_file_snapshot(
    path: Path,
    *,
    label: str,
    maximum_bytes: int = MAXIMUM_BUNDLE_METADATA_BYTES,
) -> tuple[bytes, str]:
    """Read one immutable regular-file snapshot through a no-follow descriptor."""

    path = Path(path)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise RuntimeError(f"{label} is absent, unreadable, or symbolic") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise RuntimeError(f"{label} is not a regular file")
        if before.st_size < 0 or before.st_size > int(maximum_bytes):
            raise RuntimeError(f"{label} exceeds its frozen byte ceiling")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, int(maximum_bytes) + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > int(maximum_bytes):
                raise RuntimeError(f"{label} grew beyond its frozen byte ceiling")
        after = os.fstat(descriptor)
        identity_before = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        identity_after = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if identity_after != identity_before or total != before.st_size:
            raise RuntimeError(f"{label} changed while it was being read")
        payload = b"".join(chunks)
        return payload, hashlib.sha256(payload).hexdigest()
    finally:
        os.close(descriptor)


def read_json_snapshot(
    path: Path,
    *,
    label: str,
    maximum_bytes: int = MAXIMUM_BUNDLE_METADATA_BYTES,
) -> tuple[Any, str, bytes]:
    """Hash and strict-decode the same bounded file bytes exactly once."""

    payload, digest = read_file_snapshot(
        path, label=label, maximum_bytes=maximum_bytes
    )
    return loads_json_bytes_strict(payload), digest, payload


def load_json_strict(path: Path) -> Any:
    """Load standards-compliant JSON while rejecting duplicate object keys."""

    value, _, _ = read_json_snapshot(path, label=f"JSON file {path}")
    return value


def peak_resident_set_bytes() -> int:
    """Return Linux ru_maxrss in bytes for the fail-closed execution budget."""

    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def assert_peak_memory_within_budget() -> int:
    peak = peak_resident_set_bytes()
    if peak > DECLARED_PEAK_WORKING_SET_CEILING_BYTES:
        raise MemoryError(
            "observed peak resident set exceeded the frozen working-set ceiling"
        )
    return peak


def numeric_summary(values: Iterable[float]) -> dict[str, float | int | None]:
    array = np.asarray(tuple(values), dtype=np.float64).reshape(-1)
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return {
            "count": int(array.size),
            "finite_count": 0,
            "minimum": None,
            "p05": None,
            "median": None,
            "mean": None,
            "p95": None,
            "maximum": None,
        }
    return {
        "count": int(array.size),
        "finite_count": int(finite.size),
        "minimum": float(np.min(finite)),
        "p05": float(np.quantile(finite, 0.05)),
        "median": float(np.median(finite)),
        "mean": float(np.mean(finite)),
        "p95": float(np.quantile(finite, 0.95, method="higher")),
        "maximum": float(np.max(finite)),
    }


def load_sealed_package_manifest(package: Path) -> dict[str, Any]:
    manifest_path = package / "MANIFEST.json"
    manifest, manifest_sha256, _ = read_json_snapshot(
        manifest_path, label="sealed package manifest"
    )
    if manifest_sha256 != EXPECTED_PACKAGE_MANIFEST_SHA256:
        raise RuntimeError("extracted package manifest is not the sealed v0.4 manifest")
    if (
        manifest.get("schema") != "komorebi.neuralese.package_manifest.v4"
        or manifest.get("version") != "0.4.0"
        or manifest.get("author") != AUTHOR
    ):
        raise RuntimeError("extracted package manifest metadata mismatch")
    return manifest


def _read_package_file_snapshot_against_sealed_manifest(
    package: Path, relative: str | Path
) -> tuple[bytes, dict[str, Any]]:
    """Read once and bind one artifact to the hard-bound sealed manifest."""

    package = package.resolve()
    manifest = load_sealed_package_manifest(package)
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise RuntimeError("sealed package artifact path escapes package root")
    relative_posix = relative_path.as_posix()
    records = {str(row["path"]): row for row in manifest.get("files", [])}
    if relative_posix not in records:
        raise RuntimeError(f"artifact absent from sealed package manifest: {relative_posix}")
    package_root = package
    path = package / relative_path
    resolved = path.resolve()
    if not resolved.is_relative_to(package_root):
        raise RuntimeError("sealed package artifact resolves outside package root")
    cursor = path
    while cursor != package:
        if cursor.is_symlink():
            raise RuntimeError(f"symbolic link forbidden for sealed artifact: {relative_posix}")
        cursor = cursor.parent
    record = records[relative_posix]
    if not path.is_file():
        raise RuntimeError(f"sealed artifact is not a regular file: {relative_posix}")
    payload, actual_sha = read_file_snapshot(
        path,
        label=f"sealed package artifact {relative_posix}",
        maximum_bytes=max(int(record["size"]), 1),
    )
    if len(payload) != int(record["size"]):
        raise RuntimeError(f"sealed artifact size mismatch: {relative_posix}")
    if actual_sha != str(record["sha256"]):
        raise RuntimeError(f"sealed artifact SHA-256 mismatch: {relative_posix}")
    return payload, {
        "path": relative_posix,
        "size": int(record["size"]),
        "sha256": actual_sha,
        "manifest_sha256": EXPECTED_PACKAGE_MANIFEST_SHA256,
    }


def verify_package_file_against_sealed_manifest(
    package: Path, relative: str | Path
) -> dict[str, Any]:
    """Bind one extracted artifact to the hard-bound manifest from the sealed ZIP."""

    _, binding = _read_package_file_snapshot_against_sealed_manifest(
        package, relative
    )
    return binding


def verify_package_source_integrity(package: Path) -> dict[str, Any]:
    """Bind every importable source file to the manifest from the sealed archive."""

    package = package.resolve()
    manifest = load_sealed_package_manifest(package)
    source_records = {
        str(record["path"]): record
        for record in manifest.get("files", [])
        if str(record.get("path", "")).startswith("src/")
    }
    source_root = package / "src"
    if source_root.is_symlink() or not source_root.is_dir():
        raise RuntimeError("sealed source root must be a real directory, not a link")
    linked_source_entries = [
        path.relative_to(package).as_posix()
        for path in source_root.rglob("*")
        if path.is_symlink()
    ]
    if linked_source_entries:
        raise RuntimeError(
            f"symbolic links are forbidden in extracted source: {linked_source_entries}"
        )
    actual_source_paths = {
        path.relative_to(package).as_posix()
        for path in source_root.rglob("*")
        if path.is_file()
    }
    if actual_source_paths != set(source_records):
        raise RuntimeError("extracted importable source file set differs from manifest")
    expected_source_directories = {"src"}
    for relative in source_records:
        parent = PurePosixPath(relative).parent
        while parent.as_posix() not in (".", ""):
            expected_source_directories.add(parent.as_posix())
            parent = parent.parent
    actual_source_directories = {"src"} | {
        path.relative_to(package).as_posix()
        for path in source_root.rglob("*")
        if path.is_dir()
    }
    if actual_source_directories != expected_source_directories:
        raise RuntimeError("extracted source directory set differs from manifest ancestry")
    digest = hashlib.sha256()
    for relative in sorted(source_records):
        record = source_records[relative]
        path = package / relative
        if path.is_symlink():
            raise RuntimeError("symbolic links are forbidden in extracted source")
        source_bytes, actual_sha = read_file_snapshot(
            path,
            label=f"sealed source {relative}",
            maximum_bytes=max(int(record["size"]), 1),
        )
        if len(source_bytes) != int(record["size"]):
            raise RuntimeError(f"source size mismatch: {relative}")
        if actual_sha != record["sha256"]:
            raise RuntimeError(f"source SHA-256 mismatch: {relative}")
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(actual_sha.encode("ascii") + b"\0")
    return {
        "archive_sha256_binding": EXPECTED_ARCHIVE_SHA256,
        "manifest_sha256": EXPECTED_PACKAGE_MANIFEST_SHA256,
        "source_file_count": len(source_records),
        "ordered_source_receipt_sha256": digest.hexdigest(),
    }


def _module_origin_under_source(module: Any, source_root: Path) -> Path | None:
    raw_origin = getattr(module, "__file__", None)
    if not isinstance(raw_origin, str):
        return None
    try:
        origin = Path(raw_origin).resolve(strict=True)
    except (FileNotFoundError, OSError):
        return None
    return origin if origin.is_relative_to(source_root) else None


def _verify_imported_v04_module_origins(
    package: Path, source_root: Path
) -> dict[str, Any]:
    """Require every loaded package module to resolve to a sealed source file."""

    manifest = load_sealed_package_manifest(package)
    source_records = {
        str(record["path"]): record
        for record in manifest.get("files", [])
        if str(record.get("path", "")).startswith("src/")
    }
    loaded_names = sorted(
        name
        for name in sys.modules
        if name == "komorebi_neuralese" or name.startswith("komorebi_neuralese.")
    )
    if not loaded_names:
        raise RuntimeError("sealed package import produced no package modules")
    digest = hashlib.sha256()
    module_receipts: list[dict[str, str]] = []
    for name in loaded_names:
        module = sys.modules[name]
        origin = _module_origin_under_source(module, source_root)
        if origin is None:
            raise RuntimeError(f"imported module is outside sealed source: {name}")
        relative = origin.relative_to(package).as_posix()
        record = source_records.get(relative)
        if record is None:
            raise RuntimeError(f"imported module is absent from sealed manifest: {name}")
        actual_sha = sha256_file(origin)
        if actual_sha != str(record["sha256"]):
            raise RuntimeError(f"imported module source hash mismatch: {name}")
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(actual_sha.encode("ascii") + b"\0")
        module_receipts.append(
            {"module": name, "source_path": relative, "sha256": actual_sha}
        )
    return {
        "sealed_source_root_forced_to_sys_path_zero": True,
        "loaded_module_count": len(module_receipts),
        "loaded_modules": module_receipts,
        "ordered_loaded_module_receipt_sha256": digest.hexdigest(),
    }


def import_v04_api(package: Path) -> dict[str, Any]:
    """Import only source APIs needed to reconstruct the sealed v0.4 models."""

    if sys.pycache_prefix is not None:
        raise RuntimeError(
            "external Python bytecode-cache prefixes are forbidden for sealed imports"
        )
    # Never read or create timestamp/hash bytecode for the sealed package. The
    # source census below rejects every non-manifest file, including old pyc.
    sys.dont_write_bytecode = True
    package = package.resolve()
    source_integrity_before = verify_package_source_integrity(package)
    source = package / "src"
    if source.is_symlink() or not source.is_dir():
        raise FileNotFoundError(f"missing package source directory: {source}")
    source = source.resolve(strict=True)

    preloaded_names = sorted(
        name
        for name in sys.modules
        if name == "komorebi_neuralese" or name.startswith("komorebi_neuralese.")
    )
    foreign_preloads = [
        name
        for name in preloaded_names
        if _module_origin_under_source(sys.modules[name], source) is None
    ]
    # Purge the entire package namespace so every call is a fresh import from the
    # sealed root. A foreign preload is still a fail-closed event, not something
    # silently repaired by this purge.
    for name in sorted(preloaded_names, key=lambda value: value.count("."), reverse=True):
        sys.modules.pop(name, None)
    if foreign_preloads:
        raise RuntimeError(
            f"foreign preloaded komorebi_neuralese modules rejected: {foreign_preloads}"
        )

    source_text = str(source)
    retained_sys_path: list[str] = []
    for entry in sys.path:
        try:
            candidate = Path(entry or os.getcwd()).resolve()
        except (OSError, RuntimeError):
            retained_sys_path.append(entry)
            continue
        if candidate != source:
            retained_sys_path.append(entry)
    sys.path[:] = [source_text, *retained_sys_path]
    if sys.path[0] != source_text:
        raise RuntimeError("could not force sealed source root to sys.path[0]")
    importlib.invalidate_caches()

    algebra = importlib.import_module("komorebi_neuralese.algebra")
    data = importlib.import_module("komorebi_neuralese.data")
    closure_train = importlib.import_module(
        "komorebi_neuralese.packet_closure_train"
    )
    packet_models = importlib.import_module("komorebi_neuralese.packet_models")
    import_origin_receipt = _verify_imported_v04_module_origins(package, source)
    source_integrity_after = verify_package_source_integrity(package)
    if not type_strict_equal(source_integrity_after, source_integrity_before):
        raise RuntimeError("sealed source changed across import")

    return {
        "canonical_maps": algebra.canonical_maps,
        "EpisodeGenerator": data.EpisodeGenerator,
        "get_packet_closure_arm": closure_train.get_packet_closure_arm,
        "state_dict_digest": closure_train.state_dict_digest,
        "PolarIsometricTableOperatorRNN": (
            packet_models.PolarIsometricTableOperatorRNN
        ),
        "ProjectiveLinearTableOperatorRNN": (
            packet_models.ProjectiveLinearTableOperatorRNN
        ),
        "import_origin_receipt": import_origin_receipt,
    }


@dataclass(frozen=True)
class ContextBank:
    tables: np.ndarray
    maps: np.ndarray
    phi: np.ndarray
    canonical_to_slot: np.ndarray
    keys: tuple[str, ...]
    receipt: dict[str, Any]


def make_context_bank(
    episode_generator_class: type,
    *,
    seed: int,
    count: int = CONTEXT_COUNT,
    excluded_keys: Iterable[str] = (),
    split: str = "unspecified",
) -> ContextBank:
    """Retain unique D4 contexts, deduplicating tables plus slot assignment."""

    if count < 1:
        raise ValueError("context count must be positive")
    generator = episode_generator_class(int(seed))
    retained: list[Any] = []
    excluded = set(excluded_keys)
    keys: set[str] = set()
    key_order: list[str] = []
    draws = 0
    while len(retained) < count and draws < 10000:
        batch = generator.sample(1, 0, family="d4")
        table = batch.tables[0].detach().cpu().numpy()
        slots = batch.canonical_to_slot[0].detach().cpu().numpy()
        key = hashlib.sha256(table.tobytes() + slots.tobytes()).hexdigest()
        draws += 1
        if key in keys or key in excluded:
            continue
        keys.add(key)
        key_order.append(key)
        retained.append(batch)
    if len(retained) != count:
        raise RuntimeError(f"could not construct {count} unique deterministic D4 contexts")

    tables = np.concatenate(
        [batch.tables.detach().cpu().numpy() for batch in retained], axis=0
    ).astype(np.float32, copy=False)
    maps = np.concatenate(
        [batch.maps.detach().cpu().numpy() for batch in retained], axis=0
    ).astype(np.int64, copy=False)
    phi = np.concatenate(
        [batch.phi.detach().cpu().numpy() for batch in retained], axis=0
    ).astype(np.int64, copy=False)
    canonical_to_slot = np.concatenate(
        [batch.canonical_to_slot.detach().cpu().numpy() for batch in retained], axis=0
    ).astype(np.int64, copy=False)
    payload = {
        "split": split,
        "seed": int(seed),
        "count": int(count),
        "family": "d4",
        "draws_required": int(draws),
        "phi": phi.tolist(),
        "canonical_to_slot": canonical_to_slot.tolist(),
        "maps": maps.tolist(),
        "table_dtype": "float32",
        "context_keys": key_order,
    }
    raw_tensor_digest = hashlib.sha256()
    for name, tensor in (
        ("tables", tables),
        ("maps", maps),
        ("phi", phi),
        ("canonical_to_slot", canonical_to_slot),
    ):
        raw_tensor_digest.update(name.encode("utf-8") + b"\0")
        raw_tensor_digest.update(str(tensor.dtype).encode("ascii") + b"\0")
        raw_tensor_digest.update(np.asarray(tensor.shape, dtype=np.int64).tobytes())
        raw_tensor_digest.update(np.ascontiguousarray(tensor).tobytes())
    return ContextBank(
        tables=tables,
        maps=maps,
        phi=phi,
        canonical_to_slot=canonical_to_slot,
        keys=tuple(key_order),
        receipt={
            **payload,
            "unique": True,
            "sha256": canonical_json_digest(payload),
            "raw_tensor_sha256": raw_tensor_digest.hexdigest(),
        },
    )


def make_disjoint_context_banks(episode_generator_class: type) -> dict[str, ContextBank]:
    """Construct prior, calibration, and evaluation banks before model loading."""

    prior = make_context_bank(
        episode_generator_class,
        seed=PRIOR_CONTEXT_SEED,
        split="prior_probe_exclusion",
    )
    calibration = make_context_bank(
        episode_generator_class,
        seed=CALIBRATION_CONTEXT_SEED,
        excluded_keys=prior.keys,
        split="calibration",
    )
    evaluation = make_context_bank(
        episode_generator_class,
        seed=EVALUATION_CONTEXT_SEED,
        excluded_keys=(*prior.keys, *calibration.keys),
        split="evaluation",
    )
    if set(prior.keys) & set(calibration.keys):
        raise RuntimeError("prior and calibration context banks overlap")
    if set(prior.keys) & set(evaluation.keys):
        raise RuntimeError("prior and evaluation context banks overlap")
    if set(calibration.keys) & set(evaluation.keys):
        raise RuntimeError("calibration and evaluation context banks overlap")
    return {"prior": prior, "calibration": calibration, "evaluation": evaluation}


def words_upto(maximum_length: int, alphabet: int = 2) -> tuple[tuple[int, ...], ...]:
    if maximum_length < 0:
        raise ValueError("maximum_length must be nonnegative")
    if alphabet < 1:
        raise ValueError("alphabet must be positive")
    words: list[tuple[int, ...]] = [()]
    for length in range(1, maximum_length + 1):
        words.extend(itertools.product(range(alphabet), repeat=length))
    return tuple(words)


def apply_state_word(
    canonical_maps: np.ndarray,
    state: int,
    word: Sequence[int],
) -> int:
    current = int(state)
    for action in word:
        current = int(canonical_maps[int(action), current])
    return current


def state_map_for_word(canonical_maps: np.ndarray, word: Sequence[int]) -> np.ndarray:
    return np.asarray(
        [apply_state_word(canonical_maps, state, word) for state in range(8)],
        dtype=np.int64,
    )


@dataclass(frozen=True)
class PrefixRecord:
    length: int
    replicate: int
    start_canonical: int
    terminal_canonical: int
    word: tuple[int, ...]


@dataclass(frozen=True)
class PrefixBank:
    records: tuple[PrefixRecord, ...]
    receipt: dict[str, Any]


def lexicographic_shortest_representatives(
    canonical_maps: np.ndarray,
) -> tuple[tuple[int, ...], ...]:
    """Return the lexicographically tie-broken shortest word for each D4 element."""

    representatives: list[tuple[int, ...] | None] = [None] * 8
    for word in words_upto(8):
        endpoint = apply_state_word(canonical_maps, 0, word)
        if representatives[endpoint] is None:
            representatives[endpoint] = word
        if all(candidate is not None for candidate in representatives):
            break
    if any(candidate is None for candidate in representatives):
        raise RuntimeError("D4 generators did not reach all eight endpoints")
    return tuple(candidate for candidate in representatives if candidate is not None)


def maximum_symbol_run(word: Sequence[int]) -> int:
    if not word:
        return 0
    maximum = 1
    current = 1
    for left, right in zip(word, word[1:]):
        if int(left) == int(right):
            current += 1
            maximum = max(maximum, current)
        else:
            current = 1
    return maximum


def generator_count_imbalance(word: Sequence[int]) -> int:
    zeros = sum(int(symbol) == 0 for symbol in word)
    ones = len(word) - zeros
    return abs(zeros - ones)


@dataclass(frozen=True)
class PathPair:
    nominal_band: int
    exact_length: int
    endpoint: int
    endpoint_parity: int
    pair_index: int
    number_r: int
    number_f: int
    word_a: tuple[int, ...]
    word_b: tuple[int, ...]
    full_state_map: tuple[int, ...]


@dataclass(frozen=True)
class PathPairBank:
    split: str
    pairs: tuple[PathPair, ...]
    receipt: dict[str, Any]

    @property
    def words(self) -> tuple[tuple[int, ...], ...]:
        return tuple(
            word
            for pair in self.pairs
            for word in (pair.word_a, pair.word_b)
        )


@dataclass(frozen=True)
class NativePrefixCacheEntry:
    hidden: torch.Tensor
    logits: torch.Tensor
    true_canonical: torch.Tensor
    checkpoints: Mapping[int, tuple[torch.Tensor, torch.Tensor, torch.Tensor]]
    trajectory_hidden: torch.Tensor


def _qualifying_word(
    canonical_maps: np.ndarray,
    word: tuple[int, ...],
    endpoint: int,
) -> bool:
    return bool(
        apply_state_word(canonical_maps, 0, word) == int(endpoint)
        and generator_count_imbalance(word) <= 2
        and maximum_symbol_run(word) <= 4
    )


def path_eligibility_dynamic_program(
    canonical_maps: np.ndarray, exact_length: int
) -> dict[int, dict[int, int]]:
    """Count run-filtered words by endpoint and r-count without enumeration."""

    # State is (current group endpoint, number_r, last_symbol, current_run).
    states: dict[tuple[int, int, int, int], int] = {(0, 0, -1, 0): 1}
    for _ in range(int(exact_length)):
        updated: dict[tuple[int, int, int, int], int] = {}
        for (endpoint, number_r, last, run), count in states.items():
            for symbol in (0, 1):
                next_run = run + 1 if symbol == last else 1
                if next_run > 4:
                    continue
                next_endpoint = int(canonical_maps[symbol, endpoint])
                key = (
                    next_endpoint,
                    number_r + int(symbol == 0),
                    symbol,
                    next_run,
                )
                updated[key] = updated.get(key, 0) + count
        states = updated
    output: dict[int, dict[int, int]] = {endpoint: {} for endpoint in range(8)}
    for (endpoint, number_r, _last, _run), count in states.items():
        number_f = exact_length - number_r
        if abs(number_r - number_f) <= 2:
            output[endpoint][number_r] = output[endpoint].get(number_r, 0) + count
    return output


def eligibility_audit(
    canonical_maps: np.ndarray,
    nominal_bands: Sequence[int],
    *,
    required_pairs: int = PAIRS_PER_ENDPOINT_BAND,
) -> dict[str, Any]:
    parity_vector = (0, 1, 0, 1, 1, 0, 1, 0)
    cells: list[dict[str, Any]] = []
    cache: dict[int, dict[int, dict[int, int]]] = {}
    for nominal_band in sorted(int(value) for value in nominal_bands):
        for endpoint in range(8):
            exact_length = nominal_band + parity_vector[endpoint]
            if exact_length not in cache:
                cache[exact_length] = path_eligibility_dynamic_program(
                    canonical_maps, exact_length
                )
            by_histogram = cache[exact_length][endpoint]
            possible_pairs = sum(count // 2 for count in by_histogram.values())
            cells.append(
                {
                    "nominal_band": nominal_band,
                    "endpoint": endpoint,
                    "exact_length": exact_length,
                    "eligible_by_number_r": {
                        str(key): int(value) for key, value in sorted(by_histogram.items())
                    },
                    "possible_disjoint_same_histogram_pairs": int(possible_pairs),
                    "pass": possible_pairs >= int(required_pairs),
                }
            )
    passed = all(cell["pass"] for cell in cells)
    if not passed:
        raise RuntimeError("dynamic-programming path eligibility audit failed")
    return {
        "method": "dynamic programming over endpoint, r-count, last symbol, and linear run length",
        "required_disjoint_same_histogram_pairs_per_cell": int(required_pairs),
        "cells": cells,
        "pass": passed,
    }


def make_endpoint_matched_path_bank(
    canonical_maps: np.ndarray,
    *,
    seed: int,
    split: str,
    nominal_bands: Sequence[int] = NOMINAL_DEPTH_BANDS,
    pairs_per_endpoint_band: int = PAIRS_PER_ENDPOINT_BAND,
    excluded_words: Iterable[Sequence[int]] = (),
) -> PathPairBank:
    """Generate frozen parity-corrected, endpoint-matched unordered word pairs."""

    if pairs_per_endpoint_band < 1:
        raise ValueError("pairs_per_endpoint_band must be positive")
    shortest = lexicographic_shortest_representatives(canonical_maps)
    parity_vector = (0, 1, 0, 1, 1, 0, 1, 0)
    derived_parity = tuple(len(word) % 2 for word in shortest)
    if derived_parity != parity_vector:
        raise RuntimeError("D4 shortest-word parity does not match frozen vector")
    eligibility = eligibility_audit(
        canonical_maps,
        nominal_bands,
        required_pairs=int(pairs_per_endpoint_band),
    )
    forbidden = {tuple(int(symbol) for symbol in word) for word in excluded_words}
    retained_words = set(forbidden)
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    pairs: list[PathPair] = []
    total_draws = 0
    rejection_records: list[dict[str, Any]] = []

    for nominal_band in sorted(int(value) for value in nominal_bands):
        if nominal_band < 1:
            raise ValueError("nominal depth bands must be positive")
        for endpoint in range(8):
            parity = parity_vector[endpoint]
            exact_length = nominal_band + parity
            queues: dict[int, list[tuple[int, ...]]] = {}
            draws_for_cell = 0
            cell_pairs: list[tuple[tuple[int, ...], tuple[int, ...], int]] = []
            rejected = {
                "duplicate": 0,
                "endpoint": 0,
                "imbalance": 0,
                "run_length": 0,
            }
            while len(cell_pairs) < int(pairs_per_endpoint_band):
                if draws_for_cell >= 1_000_000:
                    raise RuntimeError(
                        f"could not fill path cell split={split} band={nominal_band} endpoint={endpoint}"
                    )
                word = tuple(
                    int(value)
                    for value in rng.integers(
                        0, 2, size=exact_length, dtype=np.uint8
                    )
                )
                draws_for_cell += 1
                total_draws += 1
                if word in retained_words:
                    rejected["duplicate"] += 1
                    continue
                if apply_state_word(canonical_maps, 0, word) != endpoint:
                    rejected["endpoint"] += 1
                    continue
                if generator_count_imbalance(word) > 2:
                    rejected["imbalance"] += 1
                    continue
                if maximum_symbol_run(word) > 4:
                    rejected["run_length"] += 1
                    continue
                retained_words.add(word)
                number_r = sum(symbol == 0 for symbol in word)
                queue = queues.setdefault(number_r, [])
                queue.append(word)
                if len(queue) == 2:
                    cell_pairs.append((queue.pop(0), queue.pop(0), number_r))

            rejection_records.append(
                {
                    "nominal_band": nominal_band,
                    "endpoint": endpoint,
                    "exact_length": exact_length,
                    "draws": draws_for_cell,
                    "rejected": rejected,
                    "unpaired_eligible_words_retained": sum(len(queue) for queue in queues.values()),
                }
            )
            for pair_index, (first, second, number_r) in enumerate(cell_pairs):
                word_a, word_b = sorted((first, second))
                if word_a == word_b:
                    raise RuntimeError("endpoint-matched pair contains duplicate words")
                state_map_a = tuple(int(value) for value in state_map_for_word(canonical_maps, word_a))
                state_map_b = tuple(int(value) for value in state_map_for_word(canonical_maps, word_b))
                if state_map_a != state_map_b:
                    raise RuntimeError("same-endpoint D4 paths disagree on the eight-state action")
                expected_state_map = tuple(
                    int(value)
                    for value in state_map_for_word(
                        canonical_maps, shortest[endpoint]
                    )
                )
                if tuple(sorted(state_map_a)) != tuple(range(8)):
                    raise RuntimeError("retained D4 path does not act as a permutation")
                if state_map_a != expected_state_map:
                    raise RuntimeError(
                        "retained D4 path does not equal its endpoint action on all starts"
                    )
                pairs.append(
                    PathPair(
                        nominal_band=nominal_band,
                        exact_length=exact_length,
                        endpoint=endpoint,
                        endpoint_parity=parity,
                        pair_index=pair_index,
                        number_r=number_r,
                        number_f=exact_length - number_r,
                        word_a=word_a,
                        word_b=word_b,
                        full_state_map=state_map_a,
                    )
                )

    serialized = [
        {
            "nominal_band": pair.nominal_band,
            "exact_length": pair.exact_length,
            "endpoint": pair.endpoint,
            "endpoint_parity": pair.endpoint_parity,
            "pair_index": pair.pair_index,
            "number_r": pair.number_r,
            "number_f": pair.number_f,
            "word_a": list(pair.word_a),
            "word_b": list(pair.word_b),
            "full_state_map": list(pair.full_state_map),
        }
        for pair in pairs
    ]
    payload = {
        "split": split,
        "seed": int(seed),
        "rng": "numpy.random.Generator(numpy.random.PCG64(seed))",
        "candidate_draw": "integers(0,2,size=exact_length,dtype=uint8)",
        "nominal_bands": [int(value) for value in nominal_bands],
        "pairs_per_endpoint_band": int(pairs_per_endpoint_band),
        "all_eight_starts": True,
        "parity_rule": "exact_length = nominal_band + chi(endpoint)",
        "parity_vector": list(parity_vector),
        "generator_count_imbalance_maximum": 2,
        "identical_symbol_run_maximum": 4,
        "shortest_representatives": [list(word) for word in shortest],
        "dynamic_programming_eligibility_audit": eligibility,
        "rejection_counts": rejection_records,
        "pairs": serialized,
    }
    raw_digest = hashlib.sha256()
    for pair in pairs:
        for word in (pair.word_a, pair.word_b):
            raw_digest.update(np.asarray([len(word)], dtype=np.int64).tobytes())
            raw_digest.update(np.asarray(word, dtype=np.uint8).tobytes())
    return PathPairBank(
        split=split,
        pairs=tuple(pairs),
        receipt={
            **payload,
            "pair_count": len(pairs),
            "word_count": 2 * len(pairs),
            "draw_count": total_draws,
            "sha256": canonical_json_digest(payload),
            "raw_word_sha256": raw_digest.hexdigest(),
        },
    )


@dataclass(frozen=True)
class StressPathBank:
    words_by_endpoint: tuple[tuple[int, ...], ...]
    receipt: dict[str, Any]


def make_stress_path_bank(
    canonical_maps: np.ndarray,
    *,
    seed: int = STRESS_PATH_SEED,
    nominal_depth: int = 16,
    excluded_words: Iterable[Sequence[int]] = (),
) -> StressPathBank:
    parity_vector = (0, 1, 0, 1, 1, 0, 1, 0)
    shortest = lexicographic_shortest_representatives(canonical_maps)
    forbidden = {tuple(int(symbol) for symbol in word) for word in excluded_words}
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    words: list[tuple[int, ...]] = []
    total_draws = 0
    cell_draws: list[int] = []
    full_maps: list[list[int]] = []
    for endpoint in range(8):
        exact_length = int(nominal_depth) + parity_vector[endpoint]
        draws = 0
        while True:
            if draws >= 1_000_000:
                raise RuntimeError("could not construct endpoint-balanced stress bank")
            word = tuple(
                int(value)
                for value in rng.integers(0, 2, size=exact_length, dtype=np.uint8)
            )
            draws += 1
            total_draws += 1
            if word in forbidden or word in words:
                continue
            if _qualifying_word(canonical_maps, word, endpoint):
                full_map = state_map_for_word(canonical_maps, word)
                expected_map = state_map_for_word(
                    canonical_maps, shortest[endpoint]
                )
                if not np.array_equal(np.sort(full_map), np.arange(8)):
                    raise RuntimeError("stress D4 path does not act as a permutation")
                if not np.array_equal(full_map, expected_map):
                    raise RuntimeError(
                        "stress D4 path does not equal its endpoint action on all starts"
                    )
                words.append(word)
                cell_draws.append(draws)
                full_maps.append(
                    full_map.astype(int).tolist()
                )
                break
    payload = {
        "seed": int(seed),
        "rng": "numpy.random.Generator(numpy.random.PCG64(seed))",
        "candidate_draw": "integers(0,2,size=exact_length,dtype=uint8)",
        "nominal_depth": int(nominal_depth),
        "parity_vector": list(parity_vector),
        "generator_count_imbalance_maximum": 2,
        "identical_symbol_run_maximum": 4,
        "endpoint_balanced": True,
        "words": [list(word) for word in words],
        "full_state_maps": full_maps,
        "draws_by_endpoint": cell_draws,
        "total_draws": total_draws,
    }
    return StressPathBank(
        words_by_endpoint=tuple(words),
        receipt={**payload, "sha256": canonical_json_digest(payload)},
    )


def make_disjoint_path_banks(canonical_maps: np.ndarray) -> dict[str, Any]:
    calibration = make_endpoint_matched_path_bank(
        canonical_maps,
        seed=CALIBRATION_PATH_SEED,
        split="calibration",
    )
    evaluation = make_endpoint_matched_path_bank(
        canonical_maps,
        seed=EVALUATION_PATH_SEED,
        split="evaluation",
        excluded_words=calibration.words,
    )
    stress = make_stress_path_bank(
        canonical_maps,
        excluded_words=(*calibration.words, *evaluation.words),
    )
    if set(calibration.words) & set(evaluation.words):
        raise RuntimeError("calibration and evaluation path banks overlap")
    return {
        "calibration": calibration,
        "evaluation": evaluation,
        "stress": stress,
    }


def random_ray_key(
    *,
    split_code: int,
    context_id: int,
    nominal_band: int,
    endpoint: int,
    pair_id: int,
    start: int,
    draw_id: int,
) -> tuple[int, ...]:
    return (
        RANDOM_RAY_SEED,
        int(split_code),
        int(context_id),
        int(nominal_band),
        int(endpoint),
        int(pair_id),
        int(start),
        int(draw_id),
    )


def random_base_standard_normal(key: Sequence[int]) -> np.ndarray:
    """Draw the one frozen float64 Gaussian vector for an entropy-vector key."""

    if len(tuple(key)) != 8:
        raise ValueError("random-ray entropy vector must contain eight integers")
    seed_sequence = np.random.SeedSequence([int(value) for value in key])
    draw = np.random.Generator(np.random.PCG64(seed_sequence)).standard_normal(12)
    if draw.dtype != np.float64 or not np.isfinite(draw).all():
        raise FloatingPointError("random-ray base stream produced an invalid draw")
    return draw


def make_random_key_manifest(
    context_count: int,
    path_bank: PathPairBank,
    *,
    split_code: int = 2,
) -> dict[str, Any]:
    keys = [
        list(
            random_ray_key(
                split_code=split_code,
                context_id=context,
                nominal_band=pair.nominal_band,
                endpoint=pair.endpoint,
                pair_id=pair.pair_index,
                start=start,
                draw_id=draw,
            )
        )
        for context in range(int(context_count))
        for pair in path_bank.pairs
        for start in range(8)
        for draw in range(4)
    ]
    base_stream_digest = hashlib.sha256()
    for key in keys:
        draw = random_base_standard_normal(key)
        base_stream_digest.update(
            np.ascontiguousarray(draw, dtype=np.float64).tobytes()
        )
    payload = {
        "seed": RANDOM_RAY_SEED,
        "split_code": int(split_code),
        "key_order": [
            "seed",
            "split_code",
            "context_id",
            "nominal_band",
            "endpoint",
            "pair_id",
            "start",
            "draw_id",
        ],
        "seed_sequence": "numpy.random.SeedSequence([seed,split_code,context_id,nominal_band,endpoint,pair_id,start,draw_id]) entropy vector; not spawn key",
        "generator": "numpy.random.Generator(numpy.random.PCG64(seed_sequence))",
        "draw": "one standard_normal(12) call producing float64",
        "all_indices_zero_based": True,
        "orientation_in_key": False,
        "keys": keys,
        "base_standard_normal_stream_sha256": base_stream_digest.hexdigest(),
    }
    return {**payload, "key_count": len(keys), "sha256": canonical_json_digest(payload)}


def random_ray_states(
    model: nn.Module,
    *,
    split_code: int,
    context_id: int,
    pair: PathPair,
    starts: Sequence[int],
    base_stream_digest: Any | None = None,
) -> torch.Tensor:
    """Return four keyed G-unit rays per start as (draw, start, hidden)."""

    metric32 = model.invariant_metric()
    metric = metric32.detach().cpu().numpy().astype(np.float64)
    lower = np.linalg.cholesky(0.5 * (metric + metric.T))
    rows = np.empty((4, len(starts), 12), dtype=np.float64)
    # Consumption order is exactly the manifest order: start-major, draw-minor.
    for start_index, start in enumerate(starts):
        for draw_id in range(4):
            key = random_ray_key(
                split_code=split_code,
                context_id=context_id,
                nominal_band=pair.nominal_band,
                endpoint=pair.endpoint,
                pair_id=pair.pair_index,
                start=int(start),
                draw_id=draw_id,
            )
            z = random_base_standard_normal(key)
            if base_stream_digest is not None:
                base_stream_digest.update(
                    np.ascontiguousarray(z, dtype=np.float64).tobytes()
                )
            norm = float(np.linalg.norm(z))
            if not np.isfinite(norm) or norm <= 0.0:
                raise FloatingPointError("random-ray base draw has invalid Euclidean norm")
            ray = np.linalg.solve(lower.T, z / norm)
            rows[draw_id, start_index] = ray
    tensor = torch.from_numpy(rows.astype(np.float32))
    flat = checked_model_normalize(model, tensor.reshape(-1, 12), metric32)
    return flat.reshape(4, len(starts), 12)


def make_balanced_prefix_bank(
    canonical_maps: np.ndarray,
    *,
    seed: int = EVALUATION_PATH_SEED,
    lengths: Sequence[int] = NOMINAL_DEPTH_BANDS,
    replicates_per_terminal: int = PAIRS_PER_ENDPOINT_BAND,
) -> PrefixBank:
    """Legacy single-word helper retained only for isolated unit tests.

    It is not the frozen primary path construction. For each sampled word, its state action is a permutation.  We invert that
    permutation once for every desired terminal state.  This avoids rejection
    sampling and guarantees equal counts for all eight semantic states even
    when word parity constrains reachability from a fixed start.
    """

    clean_lengths = tuple(int(length) for length in lengths)
    if not clean_lengths or any(length < 0 for length in clean_lengths):
        raise ValueError("prefix lengths must be a nonempty sequence of nonnegative integers")
    if len(set(clean_lengths)) != len(clean_lengths):
        raise ValueError("prefix lengths must be unique")
    if replicates_per_terminal < 1:
        raise ValueError("replicates_per_terminal must be positive")

    rng = np.random.default_rng(int(seed))
    records: list[PrefixRecord] = []
    for length in clean_lengths:
        for replicate in range(int(replicates_per_terminal)):
            word = tuple(
                int(value)
                for value in rng.integers(0, 2, size=length, dtype=np.int64)
            )
            state_map = state_map_for_word(canonical_maps, word)
            if not np.array_equal(np.sort(state_map), np.arange(8)):
                raise RuntimeError("a D4 word did not act as a permutation")
            inverse = np.argsort(state_map)
            for terminal in range(8):
                start = int(inverse[terminal])
                if apply_state_word(canonical_maps, start, word) != terminal:
                    raise RuntimeError("balanced-prefix inversion failed")
                records.append(
                    PrefixRecord(
                        length=length,
                        replicate=replicate,
                        start_canonical=start,
                        terminal_canonical=terminal,
                        word=word,
                    )
                )

    serialized = [
        {
            "length": record.length,
            "replicate": record.replicate,
            "start_canonical": record.start_canonical,
            "terminal_canonical": record.terminal_canonical,
            "word": list(record.word),
        }
        for record in records
    ]
    payload = {
        "seed": int(seed),
        "lengths": list(clean_lengths),
        "replicates_per_terminal": int(replicates_per_terminal),
        "balance_axis": "terminal_semantic_state_at_intervention_cut",
        "records": serialized,
    }
    return PrefixBank(
        records=tuple(records),
        receipt={
            **payload,
            "record_count": len(records),
            "sha256": canonical_json_digest(payload),
        },
    )


@dataclass(frozen=True)
class ContinuationBank:
    words: tuple[tuple[int, ...], ...]
    receipt: dict[str, Any]


def make_continuation_bank(
    *, maximum_length: int = CONTINUATION_MAX_LENGTH
) -> ContinuationBank:
    words = words_upto(maximum_length)
    bfs_tags = {
        "epsilon": (),
        "r": (0,),
        "rr": (0, 0),
        "rrr": (0, 0, 0),
        "f": (1,),
        "fr": (1, 0),
        "rrf": (0, 0, 1),
        "rf": (0, 1),
    }
    if maximum_length >= 3 and any(word not in words for word in bfs_tags.values()):
        raise RuntimeError("BFS continuation tags are absent from W4")
    payload = {
        "construction": "lexicographic exhaustive binary words through maximum_length",
        "maximum_length": int(maximum_length),
        "words": [list(word) for word in words],
        "bfs_tags": {name: list(word) for name, word in bfs_tags.items()},
        "bfs_tags_are_members_not_extra_cases": True,
    }
    return ContinuationBank(
        words=words,
        receipt={**payload, "count": len(words), "sha256": canonical_json_digest(payload)},
    )


def canonical_words_to_slots(
    words: Sequence[Sequence[int]], canonical_to_slot: np.ndarray
) -> np.ndarray:
    if not words:
        return np.empty((0, 0), dtype=np.int64)
    lengths = {len(word) for word in words}
    if len(lengths) != 1:
        raise ValueError("word batch must have a common length")
    output = np.empty((len(words), next(iter(lengths))), dtype=np.int64)
    for row, word in enumerate(words):
        for column, action in enumerate(word):
            output[row, column] = int(canonical_to_slot[int(action)])
    return output


def verify_float32_model(model: nn.Module) -> None:
    floating_parameters = [parameter for parameter in model.parameters() if parameter.is_floating_point()]
    floating_buffers = [buffer for buffer in model.buffers() if buffer.is_floating_point()]
    if any(tensor.dtype != torch.float32 for tensor in (*floating_parameters, *floating_buffers)):
        raise TypeError("model forward path must remain torch.float32")


@dataclass(frozen=True)
class InterventionBatch:
    hidden: Mapping[str, torch.Tensor]
    selected_visible: Mapping[str, torch.Tensor]


@dataclass(frozen=True)
class ProjectorBundle:
    numpy64: np.ndarray
    torch32: torch.Tensor
    audit: dict[str, Any]


def construct_anchor_projector(model: nn.Module) -> ProjectorBundle:
    """Construct P_B through the frozen whitened SVD route, then audit post-cast."""

    anchors32 = model.state_anchors()
    metric32 = model.invariant_metric()
    if anchors32.dtype != torch.float32 or metric32.dtype != torch.float32:
        raise TypeError("projector inputs must originate from the float32 model")
    anchors = anchors32.detach().cpu().numpy().astype(np.float64).T
    metric = metric32.detach().cpu().numpy().astype(np.float64)
    antisymmetry = float(np.max(np.abs(metric - metric.T)))
    if not np.isfinite(metric).all() or antisymmetry > 1e-6:
        raise RuntimeError("recurrence metric is nonfinite or insufficiently symmetric")
    metric = 0.5 * (metric + metric.T)
    eigenvalues = np.linalg.eigvalsh(metric)
    if eigenvalues[-1] <= 0.0 or eigenvalues[0] <= 1e-8 * eigenvalues[-1]:
        raise RuntimeError("recurrence metric fails the frozen positive-definiteness gate")
    gram = anchors.T @ metric @ anchors
    gram_singular = np.linalg.svd(gram, compute_uv=False)
    gram_rank = int(np.count_nonzero(gram_singular > 1e-8 * gram_singular[0]))
    rank = int(np.linalg.matrix_rank(anchors))
    gram_condition = float(gram_singular[0] / gram_singular[-1])
    if rank != 8 or gram_rank != 8:
        raise RuntimeError("anchor projector requires a full-rank eight-anchor chart")
    if gram_condition > 1e8:
        raise RuntimeError("anchor Gram matrix exceeds the frozen condition limit")
    lower = np.linalg.cholesky(metric)
    whitener = lower.T
    whitened_anchors = whitener @ anchors
    left, singular, _ = np.linalg.svd(whitened_anchors, full_matrices=False)
    if int(np.count_nonzero(singular > 1e-8 * singular[0])) != 8:
        raise RuntimeError("checked thin SVD did not recover eight anchor directions")
    orthonormal = left[:, :8]
    projector = np.linalg.solve(whitener, orthonormal @ orthonormal.T @ whitener)
    if not np.isfinite(projector).all():
        raise FloatingPointError("anchor projector is nonfinite")
    projector32 = projector.astype(np.float32).astype(np.float64)
    idempotence_matrix = projector32 @ projector32 - projector32
    self_adjointness_matrix = projector32.T @ metric - metric @ projector32
    anchor_residual = projector32 @ anchors - anchors
    idempotence = float(np.max(np.abs(idempotence_matrix)))
    self_adjointness = float(np.max(np.abs(self_adjointness_matrix)))
    anchor_preservation = float(np.max(np.abs(anchor_residual)))
    trace_error = abs(float(np.trace(projector32)) - 8.0)
    audit = {
        "construction": "C^-1 Q Q^T C from G=C^T C and checked thin SVD(CB), float64 then cast float32",
        "post_cast_rank": int(np.linalg.matrix_rank(projector32)),
        "anchor_rank": rank,
        "gram_rank": gram_rank,
        "metric_maximum_antisymmetric_entry": antisymmetry,
        "metric_minimum_eigenvalue": float(eigenvalues[0]),
        "metric_maximum_eigenvalue": float(eigenvalues[-1]),
        "anchor_gram_relative_rank_tolerance": 1e-8,
        "trace": float(np.trace(projector32)),
        "trace_error_from_eight": trace_error,
        "maximum_absolute_idempotence_residual": idempotence,
        "maximum_absolute_g_self_adjointness_residual": self_adjointness,
        "maximum_absolute_anchor_preservation_residual": anchor_preservation,
        "condition_number_anchor_gram": gram_condition,
        "post_cast_absolute_tolerance": 1e-5,
        "pass": bool(
            np.linalg.matrix_rank(projector32) == 8
            and trace_error <= 1e-5
            and idempotence <= 1e-5
            and self_adjointness <= 1e-5
            and anchor_preservation <= 1e-5
        ),
    }
    if not audit["pass"]:
        raise RuntimeError("anchor projector audit failed")
    return ProjectorBundle(
        numpy64=projector,
        torch32=torch.from_numpy(projector.astype(np.float32)),
        audit=audit,
    )


@dataclass(frozen=True)
class PrototypeBundle:
    torch32: torch.Tensor
    numpy64: np.ndarray
    audit: dict[str, Any]


def checked_model_normalize(
    model: nn.Module,
    hidden: torch.Tensor,
    metric: torch.Tensor | None = None,
) -> torch.Tensor:
    """Apply the packaged float32 normalization after the frozen norm guard."""

    if hidden.dtype != torch.float32:
        raise TypeError("normalization input must be torch.float32")
    if metric is None:
        metric = model.invariant_metric()
    squared = torch.einsum("...i,ij,...j->...", hidden, metric, hidden)
    if bool((~torch.isfinite(squared)).any()) or bool((squared <= 1e-12).any()):
        raise FloatingPointError("squared metric norm is nonfinite or not strictly above 1e-12")
    normalized = model.normalize_hidden(hidden, metric)
    if normalized.dtype != torch.float32 or not bool(torch.isfinite(normalized).all()):
        raise FloatingPointError("packaged normalization produced an invalid state")
    return normalized


def checked_decode_hidden(model: nn.Module, hidden: torch.Tensor) -> torch.Tensor:
    """Decode only finite float32 hidden states and fail on nonfinite logits."""

    if hidden.dtype != torch.float32 or not bool(torch.isfinite(hidden).all()):
        raise FloatingPointError("decoder input is not a finite float32 hidden state")
    logits = model.decode_hidden(hidden)
    if logits.dtype != torch.float32 or not bool(torch.isfinite(logits).all()):
        raise FloatingPointError("decoder produced nonfinite or non-float32 logits")
    return logits


def oriented_metric_selector(
    hidden: torch.Tensor,
    candidates: torch.Tensor,
    metric: torch.Tensor,
) -> torch.Tensor:
    """Select by detached float64 G_s cosine, breaking exact ties to lowest label."""

    if hidden.dtype != torch.float32 or candidates.dtype != torch.float32:
        raise TypeError("selector inputs must originate from float32 model states")
    hidden64 = hidden.detach().cpu().numpy().astype(np.float64)
    candidates64 = candidates.detach().cpu().numpy().astype(np.float64)
    metric64 = metric.detach().cpu().numpy().astype(np.float64)
    metric_s = 0.5 * (metric64 + metric64.T)
    numerators = hidden64 @ metric_s @ candidates64.T
    hidden_norm = np.sqrt(
        np.einsum("bi,ij,bj->b", hidden64, metric_s, hidden64)
    )
    candidate_norm = np.sqrt(
        np.einsum("bi,ij,bj->b", candidates64, metric_s, candidates64)
    )
    denominators = hidden_norm[:, None] * candidate_norm[None, :]
    if np.any(~np.isfinite(denominators)) or np.any(denominators <= 1e-12):
        raise FloatingPointError("selector cosine has an invalid norm denominator")
    scores = numerators / denominators
    # numpy.argmax returns the first index, which is the lowest visible label.
    return torch.from_numpy(np.argmax(scores, axis=1).astype(np.int64)).long()


def prototypes_from_labeled_states(
    model: nn.Module,
    states: torch.Tensor,
    visible_labels: torch.Tensor,
) -> PrototypeBundle:
    """Build one positive-ray prototype per visible class using float64 reductions."""

    if states.dtype != torch.float32 or visible_labels.dtype != torch.long:
        raise TypeError("calibration states must be float32 and labels torch.long")
    if states.ndim != 2 or visible_labels.shape != (states.shape[0],):
        raise ValueError("calibration state and label shapes disagree")
    metric32 = model.invariant_metric()
    metric_raw = metric32.detach().cpu().numpy().astype(np.float64)
    metric = 0.5 * (metric_raw + metric_raw.T)
    state64 = states.detach().cpu().numpy().astype(np.float64)
    labels = visible_labels.detach().cpu().numpy().astype(np.int64)
    norm_squared = np.einsum("bi,ij,bj->b", state64, metric, state64)
    if np.any(~np.isfinite(norm_squared)) or np.any(norm_squared <= 1e-12):
        raise FloatingPointError("calibration contribution has invalid metric norm")
    unit = state64 / np.sqrt(norm_squared)[:, None]
    prototypes = np.empty((8, state64.shape[1]), dtype=np.float64)
    counts: list[int] = []
    resultant_norms: list[float] = []
    mean_resultant_lengths: list[float] = []
    for label in range(8):
        selected = unit[labels == label]
        if selected.shape[0] == 0:
            raise RuntimeError(f"prototype class {label} has no calibration contributions")
        resultant = np.sum(selected, axis=0, dtype=np.float64)
        squared = float(resultant @ metric @ resultant)
        if not np.isfinite(squared) or squared <= 1e-12:
            raise FloatingPointError(f"prototype class {label} has zero or nonfinite resultant")
        norm = math.sqrt(squared)
        prototypes[label] = resultant / norm
        counts.append(int(selected.shape[0]))
        resultant_norms.append(norm)
        mean_resultant_lengths.append(norm / selected.shape[0])
    prototype32 = torch.from_numpy(prototypes.astype(np.float32))
    prototype32 = checked_model_normalize(model, prototype32, metric32)
    if not bool(torch.isfinite(prototype32).all()):
        raise FloatingPointError("float32 prototype conversion is nonfinite")
    prototype_bytes = (
        prototype32.detach().cpu().contiguous().numpy().astype(np.float32, copy=False)
    )
    return PrototypeBundle(
        torch32=prototype32,
        numpy64=prototypes,
        audit={
            "counts_by_visible_class": counts,
            "balanced_visible_class_counts": len(set(counts)) == 1,
            "resultant_norms": resultant_norms,
            "mean_resultant_lengths": mean_resultant_lengths,
            "minimum_mean_resultant_length": min(mean_resultant_lengths),
            "positive_ray_sign_flips": 0,
            "depth_specific": False,
            "coordinates_pooled_across_checkpoints": False,
            "float32_tensor_sha256": hashlib.sha256(
                prototype_bytes.tobytes()
            ).hexdigest(),
            "float32_class_tensor_sha256": [
                hashlib.sha256(prototype_bytes[label].tobytes()).hexdigest()
                for label in range(8)
            ],
        },
    )


def construct_interventions(
    model: nn.Module,
    hidden_h: torch.Tensor,
    hidden_h_prime: torch.Tensor,
    true_canonical: torch.Tensor,
    phi: torch.Tensor,
    canonical_maps: np.ndarray,
    projector: ProjectorBundle,
    prototypes: PrototypeBundle,
) -> InterventionBatch:
    """Construct all frozen one-shot branches without leaving float32."""

    if hidden_h.dtype != torch.float32 or hidden_h_prime.dtype != torch.float32:
        raise TypeError("intervention input must be torch.float32")
    if true_canonical.dtype != torch.long or phi.dtype != torch.long:
        raise TypeError("semantic labels and phi must be torch.long")
    if (
        hidden_h.ndim != 2
        or hidden_h_prime.shape != hidden_h.shape
        or true_canonical.shape != (hidden_h.shape[0],)
    ):
        raise ValueError("hidden and true_canonical batch shapes disagree")
    if phi.shape != (8,):
        raise ValueError("phi must map eight canonical states to visible labels")

    anchors = model.state_anchors()
    metric = model.invariant_metric()
    if anchors.dtype != torch.float32 or metric.dtype != torch.float32:
        raise TypeError("anchor and metric construction must remain torch.float32")
    true_visible = phi[true_canonical]

    decoded_visible = checked_decode_hidden(model, hidden_h).argmax(dim=-1)
    nearest_visible = oriented_metric_selector(hidden_h, anchors, metric)
    wrong_canonical_np = canonical_maps[0, true_canonical.detach().cpu().numpy()]
    wrong_canonical = torch.from_numpy(
        np.asarray(wrong_canonical_np, dtype=np.int64)
    ).to(dtype=torch.long)
    wrong_visible = phi[wrong_canonical]

    prototype32 = prototypes.torch32
    if prototype32.dtype != torch.float32 or prototype32.shape != anchors.shape:
        raise TypeError("prototype chart must be float32 and match anchor shape")
    nearest_prototype_visible = oriented_metric_selector(
        hidden_h, prototype32, metric
    )

    projected = hidden_h @ projector.torch32.transpose(0, 1)
    projected = checked_model_normalize(model, projected, metric)
    candidates = {
        "native_h": hidden_h.clone(),
        "native_h_prime": hidden_h_prime.clone(),
        "sham_scale": checked_model_normalize(model, 7.0 * hidden_h, metric),
        "oracle_anchor": anchors[true_visible],
        "self_anchor": anchors[decoded_visible],
        "nearest_anchor": anchors[nearest_visible],
        "oracle_prototype": prototype32[true_visible],
        "self_prototype": prototype32[nearest_prototype_visible],
        "anchor_projection": projected,
        "wrong_anchor": anchors[wrong_visible],
        "wrong_prototype": prototype32[wrong_visible],
    }
    for name, candidate in candidates.items():
        if candidate.dtype != torch.float32:
            raise TypeError(f"{name} left the torch.float32 intervention path")
        if not bool(torch.isfinite(candidate).all()):
            raise FloatingPointError(f"{name} produced a nonfinite state")

    sentinel = torch.full_like(true_visible, -1)
    selected = {
        "native_h": sentinel,
        "native_h_prime": sentinel,
        "sham_scale": sentinel,
        "oracle_anchor": true_visible,
        "self_anchor": decoded_visible,
        "nearest_anchor": nearest_visible,
        "oracle_prototype": true_visible,
        "self_prototype": nearest_prototype_visible,
        "anchor_projection": sentinel,
        "wrong_anchor": wrong_visible,
        "wrong_prototype": wrong_visible,
    }
    return InterventionBatch(hidden=candidates, selected_visible=selected)


def _numpy64(tensor: torch.Tensor) -> np.ndarray:
    if tensor.dtype != torch.float32:
        raise TypeError("only float32 model outputs may enter the diagnostic promotion boundary")
    return tensor.detach().cpu().numpy().astype(np.float64)


def _row_oriented_angles(
    first: np.ndarray,
    second: np.ndarray,
    metric: np.ndarray | None = None,
) -> np.ndarray:
    if metric is None:
        numerators = np.einsum("bi,bi->b", first, second)
        first_norms = np.linalg.norm(first, axis=1)
        second_norms = np.linalg.norm(second, axis=1)
    else:
        numerators = np.einsum("bi,ij,bj->b", first, metric, second)
        first_norms = np.sqrt(
            np.clip(np.einsum("bi,ij,bj->b", first, metric, first), 0.0, None)
        )
        second_norms = np.sqrt(
            np.clip(np.einsum("bi,ij,bj->b", second, metric, second), 0.0, None)
        )
    denominators = first_norms * second_norms
    output = np.full(first.shape[0], np.nan, dtype=np.float64)
    valid = (
        np.isfinite(numerators)
        & np.isfinite(first_norms)
        & np.isfinite(second_norms)
        & (first_norms > 1e-12)
        & (second_norms > 1e-12)
    )
    output[valid] = np.arccos(
        np.clip(numerators[valid] / denominators[valid], -1.0, 1.0)
    )
    return output


def paired_future_diagnostics(
    native_logits: torch.Tensor,
    candidate_logits: torch.Tensor,
    native_hidden: torch.Tensor,
    candidate_hidden: torch.Tensor,
    target_visible: torch.Tensor,
    metric: torch.Tensor,
    native_prime_logits: torch.Tensor | None = None,
    native_prime_hidden: torch.Tensor | None = None,
    counterfactual_visible: torch.Tensor | None = None,
) -> dict[str, np.ndarray]:
    """Promote detached float32 outputs, then compute paired float64 metrics."""

    if native_prime_logits is None:
        native_prime_logits = native_logits
    if native_prime_hidden is None:
        native_prime_hidden = native_hidden
    for tensor in (
        native_logits,
        native_prime_logits,
        candidate_logits,
        native_hidden,
        native_prime_hidden,
        candidate_hidden,
        metric,
    ):
        if tensor.dtype != torch.float32:
            raise TypeError("model outputs and metric must be torch.float32 before diagnostics")
        if not bool(torch.isfinite(tensor).all()):
            raise FloatingPointError(
                "nonfinite float32 model output or metric reached diagnostics"
            )
    if target_visible.dtype != torch.long:
        raise TypeError("target_visible must be torch.long")
    if counterfactual_visible is None:
        counterfactual_visible = target_visible
    if counterfactual_visible.dtype != torch.long:
        raise TypeError("counterfactual_visible must be torch.long")

    native_l = _numpy64(native_logits)
    native_prime_l = _numpy64(native_prime_logits)
    candidate_l = _numpy64(candidate_logits)
    native_h = _numpy64(native_hidden)
    native_prime_h = _numpy64(native_prime_hidden)
    candidate_h = _numpy64(candidate_hidden)
    metric64_raw = _numpy64(metric)
    metric64 = 0.5 * (metric64_raw + metric64_raw.T)
    target = target_visible.detach().cpu().numpy().astype(np.int64)
    counterfactual = counterfactual_visible.detach().cpu().numpy().astype(np.int64)
    if (
        np.any(target < 0)
        or np.any(target >= candidate_l.shape[1])
        or np.any(counterfactual < 0)
        or np.any(counterfactual >= candidate_l.shape[1])
    ):
        raise ValueError("diagnostic target is outside the decoder label range")
    rows = np.arange(target.shape[0])

    native_prediction = np.argmax(native_l, axis=1)
    native_prime_prediction = np.argmax(native_prime_l, axis=1)
    candidate_prediction = np.argmax(candidate_l, axis=1)
    shifted = candidate_l - np.max(candidate_l, axis=1, keepdims=True)
    probabilities = np.exp(shifted)
    probabilities /= np.sum(probabilities, axis=1, keepdims=True)
    native_shifted = native_l - np.max(native_l, axis=1, keepdims=True)
    native_probabilities = np.exp(native_shifted)
    native_probabilities /= np.sum(native_probabilities, axis=1, keepdims=True)
    native_prime_shifted = native_prime_l - np.max(
        native_prime_l, axis=1, keepdims=True
    )
    native_prime_probabilities = np.exp(native_prime_shifted)
    native_prime_probabilities /= np.sum(
        native_prime_probabilities, axis=1, keepdims=True
    )
    masked = candidate_l.copy()
    masked[rows, target] = -np.inf
    margin = candidate_l[rows, target] - np.max(masked, axis=1)

    native_centered = native_l - native_l.mean(axis=1, keepdims=True)
    native_prime_centered = native_prime_l - native_prime_l.mean(
        axis=1, keepdims=True
    )
    candidate_centered = candidate_l - candidate_l.mean(axis=1, keepdims=True)
    native_correct = native_prediction == target
    native_prime_correct = native_prime_prediction == target
    candidate_correct = candidate_prediction == target
    tv_h = 0.5 * np.sum(
        np.abs(probabilities - native_probabilities), axis=1
    )
    tv_prime = 0.5 * np.sum(
        np.abs(probabilities - native_prime_probabilities), axis=1
    )
    logit_angle_h = _row_oriented_angles(native_centered, candidate_centered)
    logit_angle_prime = _row_oriented_angles(
        native_prime_centered, candidate_centered
    )
    hidden_angle_h = _row_oriented_angles(native_h, candidate_h, metric64)
    hidden_angle_prime = _row_oriented_angles(
        native_prime_h, candidate_h, metric64
    )
    if (
        not np.isfinite(probabilities).all()
        or not np.isfinite(native_probabilities).all()
        or not np.isfinite(native_prime_probabilities).all()
        or not np.isfinite(tv_h).all()
        or not np.isfinite(tv_prime).all()
        or not np.isfinite(margin).all()
        or not np.isfinite(hidden_angle_h).all()
        or not np.isfinite(hidden_angle_prime).all()
    ):
        raise FloatingPointError(
            "nonfinite probability, total variation, or margin invalidates checkpoint"
        )
    return {
        "accuracy": candidate_correct.astype(np.float64),
        "counterfactual_accuracy": (
            candidate_prediction == counterfactual
        ).astype(np.float64),
        "native_h_accuracy": native_correct.astype(np.float64),
        "native_h_prime_accuracy": native_prime_correct.astype(np.float64),
        "native_h_agreement": (candidate_prediction == native_prediction).astype(np.float64),
        "native_h_prime_agreement": (
            candidate_prediction == native_prime_prediction
        ).astype(np.float64),
        "joint_native_h_and_candidate_correct": (
            native_correct & candidate_correct
        ).astype(np.float64),
        "joint_both_natives_and_candidate_correct": (
            native_correct & native_prime_correct & candidate_correct
        ).astype(np.float64),
        "damage_numerator": (native_correct & ~candidate_correct).astype(np.float64),
        "damage_denominator": native_correct.astype(np.float64),
        "rescue_numerator": (~native_correct & candidate_correct).astype(np.float64),
        "rescue_denominator": (~native_correct).astype(np.float64),
        "target_probability": probabilities[rows, target],
        "correct_margin": margin,
        "softmax_tv_to_native_h": tv_h,
        "softmax_tv_to_native_h_prime": tv_prime,
        "centered_logit_angle_to_native_h": logit_angle_h,
        "centered_logit_angle_to_native_h_prime": logit_angle_prime,
        "hidden_metric_angle_to_native_h": hidden_angle_h,
        "hidden_metric_angle_to_native_h_prime": hidden_angle_prime,
    }


class TensorAccumulator:
    """Finite-safe sums indexed by intervention, prefix, suffix, and cut state."""

    METRICS = (
        "accuracy",
        "counterfactual_accuracy",
        "native_h_accuracy",
        "native_h_prime_accuracy",
        "native_h_agreement",
        "native_h_prime_agreement",
        "joint_native_h_and_candidate_correct",
        "joint_both_natives_and_candidate_correct",
        "damage_numerator",
        "damage_denominator",
        "rescue_numerator",
        "rescue_denominator",
        "target_probability",
        "correct_margin",
        "softmax_tv_to_native_h",
        "softmax_tv_to_native_h_prime",
        "centered_logit_angle_to_native_h",
        "centered_logit_angle_to_native_h_prime",
        "hidden_metric_angle_to_native_h",
        "hidden_metric_angle_to_native_h_prime",
    )

    def __init__(
        self,
        shape: tuple[int, int, int, int],
        axes: Sequence[str] = (
            "intervention",
            "prefix_length",
            "continuation_word",
            "canonical_state_at_cut",
        ),
    ) -> None:
        self.shape = shape
        if len(tuple(axes)) != 4:
            raise ValueError("TensorAccumulator requires exactly four axis labels")
        self.axes = tuple(str(axis) for axis in axes)
        self.case_count = np.zeros(shape, dtype=np.int64)
        self.sums = {name: np.zeros(shape, dtype=np.float64) for name in self.METRICS}
        self.finite_counts = {name: np.zeros(shape, dtype=np.int64) for name in self.METRICS}

    def add_batch(
        self,
        intervention_index: int,
        prefix_index: int,
        continuation_index: int,
        cut_states: np.ndarray,
        metrics: Mapping[str, np.ndarray],
    ) -> None:
        for row, cut_state in enumerate(np.asarray(cut_states, dtype=np.int64)):
            index = (
                int(intervention_index),
                int(prefix_index),
                int(continuation_index),
                int(cut_state),
            )
            self.case_count[index] += 1
            for name in self.METRICS:
                value = float(metrics[name][row])
                if np.isfinite(value):
                    self.sums[name][index] += value
                    self.finite_counts[name][index] += 1

    def add_dense_panel(
        self,
        first_indices: np.ndarray,
        second_indices: np.ndarray,
        continuation_indices: np.ndarray,
        cut_states: np.ndarray,
        metrics: Mapping[str, np.ndarray],
    ) -> None:
        """Accumulate a complete mode-by-continuation panel without Python rows.

        ``metrics`` uses the frozen logical order ``[mode, continuation, row]``.
        Every mode must contain the same positive multiplicity of every canonical
        cut state.  Stable sorting then exposes each occurrence separately, so
        float64 additions retain the scalar accumulator's trajectory/row order
        instead of changing the scientific reduction to a pooled sum.
        """

        first = np.asarray(first_indices, dtype=np.int64).reshape(-1)
        second = np.asarray(second_indices, dtype=np.int64).reshape(-1)
        continuation = np.asarray(continuation_indices, dtype=np.int64).reshape(-1)
        states = np.asarray(cut_states, dtype=np.int64)
        if states.ndim == 1:
            states = np.broadcast_to(states[None, :], (first.size, states.size))
        if states.shape[0] != first.size or second.shape != first.shape:
            raise ValueError("dense accumulator mode axes disagree")
        if first.size == 0 or continuation.size == 0 or states.shape[1] == 0:
            raise ValueError("dense accumulator panel must be nonempty")
        state_count = int(self.shape[3])
        if states.shape[1] % state_count:
            raise ValueError("dense accumulator rows do not balance canonical states")
        multiplicity = states.shape[1] // state_count
        order = np.argsort(states, axis=1, kind="stable")
        ordered_states = np.take_along_axis(states, order, axis=1)
        expected_states = np.repeat(
            np.arange(state_count, dtype=np.int64), multiplicity
        )
        if not np.array_equal(
            ordered_states,
            np.broadcast_to(expected_states[None, :], ordered_states.shape),
        ):
            raise ValueError("dense accumulator cut-state panel is not balanced")
        index = (
            first[:, None, None],
            second[:, None, None],
            continuation[None, :, None],
            np.arange(state_count, dtype=np.int64)[None, None, :],
        )
        # The logical mode pairs are required to be unique, making advanced
        # indexed in-place addition well-defined for every destination cell.
        if len(set(zip(first.tolist(), second.tolist()))) != first.size:
            raise ValueError("dense accumulator logical mode indices are duplicated")
        self.case_count[index] += int(multiplicity)
        for name in self.METRICS:
            value = np.asarray(metrics[name], dtype=np.float64)
            expected_shape = (first.size, continuation.size, states.shape[1])
            if value.shape != expected_shape:
                raise ValueError(
                    f"dense accumulator metric {name} has shape {value.shape}, "
                    f"expected {expected_shape}"
                )
            ordered = np.take_along_axis(value, order[:, None, :], axis=2)
            ordered = ordered.reshape(
                first.size, continuation.size, state_count, multiplicity
            )
            # Add repeated state occurrences one at a time.  In particular, the
            # two one-shot source orientations keep their former scalar order.
            for occurrence in range(multiplicity):
                item = ordered[..., occurrence]
                finite = np.isfinite(item)
                self.sums[name][index] += np.where(finite, item, 0.0)
                self.finite_counts[name][index] += finite.astype(np.int64)

    def serialize(self) -> dict[str, Any]:
        means: dict[str, Any] = {}
        for name in self.METRICS:
            with np.errstate(invalid="ignore", divide="ignore"):
                mean = self.sums[name] / self.finite_counts[name]
            mean[self.finite_counts[name] == 0] = np.nan
            means[name] = _json_safe_array(mean)
        return {
            "axes": list(self.axes),
            "shape": list(self.shape),
            "case_count": self.case_count.tolist(),
            # All non-angle diagnostics hard-fail before accumulation and therefore
            # have finite_count == case_count. Only the two tie-aware angles need
            # separate completeness arrays in the persisted compact record.
            "finite_count_for_tie_aware_angles": {
                name: self.finite_counts[name].tolist()
                for name in (
                    "centered_logit_angle_to_native_h",
                    "centered_logit_angle_to_native_h_prime",
                )
            },
            "mean": means,
        }


def encode_context_once(model: nn.Module, table: np.ndarray) -> torch.Tensor:
    """Encode one exact table context once and retain its float32 recurrent codes."""

    table32 = torch.from_numpy(
        np.asarray(table, dtype=np.float32)[None, ...]
    ).to(dtype=torch.float32)
    if hasattr(model, "encode_operator_bundle"):
        codes = model.encode_operator_bundle(table32).matrices
    else:
        codes = model.encode_operators(table32)
    if codes.dtype != torch.float32 or codes.shape[0] != 1:
        raise TypeError("encoded context must be a one-example float32 operator bundle")
    if not bool(torch.isfinite(codes).all()):
        raise FloatingPointError("encoded operator bundle is nonfinite")
    return codes


def run_word_batch(
    model: nn.Module,
    encoded_context: torch.Tensor,
    canonical_to_slot: np.ndarray,
    phi: np.ndarray,
    starts_canonical: np.ndarray,
    words: Sequence[Sequence[int]],
) -> SimpleNamespace:
    """Run a common-length word batch from exact visible initial anchors."""

    starts = np.asarray(starts_canonical, dtype=np.int64)
    if len(words) != starts.shape[0]:
        raise ValueError("word and start batch sizes disagree")
    starts_visible = torch.from_numpy(np.asarray(phi, dtype=np.int64)[starts]).long()
    initial = model.initial_hidden(starts_visible)
    slots = torch.from_numpy(
        canonical_words_to_slots(words, canonical_to_slot)
    ).long()
    codes = encoded_context.expand(starts.shape[0], -1, -1, -1)
    trace = model.continue_from_hidden(initial, codes, slots)
    if trace.hidden[-1].dtype != torch.float32 or trace.logits.dtype != torch.float32:
        raise TypeError("word rollout left torch.float32")
    if (
        not bool(torch.isfinite(trace.hidden[-1]).all())
        or not bool(torch.isfinite(trace.logits).all())
    ):
        raise FloatingPointError("word rollout produced nonfinite hidden states or logits")
    proposals = getattr(trace, "pre_normalized_hidden", None)
    if proposals:
        metric = model.invariant_metric()
        for proposal in proposals:
            squared = torch.einsum("bi,ij,bj->b", proposal, metric, proposal)
            if bool((~torch.isfinite(squared)).any()) or bool((squared <= 1e-12).any()):
                raise FloatingPointError(
                    "packaged rollout proposal violates the frozen pre-normalization guard"
                )
    return trace


def custom_rollout_float32(
    model: nn.Module,
    hidden: torch.Tensor,
    operator_codes: torch.Tensor,
    op_slots: torch.Tensor,
) -> SimpleNamespace:
    """Independent recurrence used to check the packaged continuation plumbing."""

    if hidden.dtype != torch.float32 or operator_codes.dtype != torch.float32:
        raise TypeError("custom rollout inputs must be float32")
    metric = model.invariant_metric()
    state = checked_model_normalize(model, hidden, metric)
    rows = torch.arange(state.shape[0])
    trajectory = [state]
    for time_index in range(op_slots.shape[1]):
        selected = operator_codes[rows, op_slots[:, time_index]]
        proposal = torch.bmm(selected, state.unsqueeze(-1)).squeeze(-1)
        state = checked_model_normalize(model, proposal, metric)
        trajectory.append(state)
    return SimpleNamespace(logits=checked_decode_hidden(model, state), hidden=trajectory)


@torch.inference_mode()
def rollout_word_set_reusing_tree(
    model: nn.Module,
    hidden: torch.Tensor,
    encoded_context: torch.Tensor,
    canonical_to_slot: np.ndarray,
    words: Sequence[tuple[int, ...]],
) -> dict[tuple[int, ...], SimpleNamespace]:
    """Roll the prefix closure of any requested word set once per unique edge."""

    ordered = tuple(tuple(int(value) for value in word) for word in words)
    batch = hidden.shape[0]
    codes = encoded_context
    if codes.shape[0] == 1:
        codes = codes.expand(batch, -1, -1, -1)
    if codes.shape[0] != batch:
        raise ValueError("operator code and hidden batch sizes disagree")
    metric = model.invariant_metric()
    root = checked_model_normalize(model, hidden, metric)
    tree: dict[tuple[int, ...], SimpleNamespace] = {
        (): SimpleNamespace(hidden=root, logits=checked_decode_hidden(model, root))
    }
    required_prefixes: set[tuple[int, ...]] = {()}
    for word in ordered:
        for length in range(1, len(word) + 1):
            required_prefixes.add(word[:length])
    rows = torch.arange(batch)
    for word in sorted(required_prefixes, key=lambda value: (len(value), value)):
        if not word:
            continue
        parent = tree[word[:-1]].hidden
        slot = int(canonical_to_slot[word[-1]])
        selected = codes[rows, slot]
        proposal = torch.bmm(selected, parent.unsqueeze(-1)).squeeze(-1)
        state = checked_model_normalize(model, proposal, metric)
        tree[word] = SimpleNamespace(
            hidden=state, logits=checked_decode_hidden(model, state)
        )
    return {word: tree[word] for word in ordered}


def concatenate_trace_rows(*traces: SimpleNamespace) -> SimpleNamespace:
    """Concatenate already-computed tree nodes without another model step."""

    if not traces:
        raise ValueError("at least one trace is required")
    hidden = torch.cat(tuple(trace.hidden for trace in traces), dim=0)
    logits = torch.cat(tuple(trace.logits for trace in traces), dim=0)
    if hidden.dtype != torch.float32 or logits.dtype != torch.float32:
        raise TypeError("tree-node reuse must preserve the float32 forward boundary")
    return SimpleNamespace(hidden=hidden, logits=logits)


def repeat_trace_rows(trace: SimpleNamespace, repeats: int = 2) -> SimpleNamespace:
    """Repeat an orientation-invariant tree node only at the diagnostic boundary."""

    if repeats < 1:
        raise ValueError("trace repeats must be positive")
    return concatenate_trace_rows(*(trace for _ in range(int(repeats))))


class ContextStratumAccumulator:
    """Online context-equal reductions for the prespecified suffix strata."""

    METRICS = (
        "accuracy",
        "counterfactual_accuracy",
        "native_h_accuracy",
        "joint_native_h_and_candidate_correct",
        "damage_numerator",
        "damage_denominator",
        "rescue_numerator",
        "rescue_denominator",
        "correct_selection_and_suffix_correct",
        "correct_selection_denominator",
    )

    def __init__(self, interventions: int, bands: int, contexts: int) -> None:
        shape = (
            int(interventions),
            int(bands),
            int(contexts),
            len(SUFFIX_STRATUM_NAMES),
        )
        self.sums = {
            name: np.zeros(shape, dtype=np.float64) for name in self.METRICS
        }
        self.finite_counts = {
            name: np.zeros(shape, dtype=np.int64) for name in self.METRICS
        }

    @staticmethod
    def _strata_for_length(length: int) -> tuple[int, ...]:
        names = [SUFFIX_STRATUM_NAMES.index("all")]
        if int(length) == 0:
            names.append(SUFFIX_STRATUM_NAMES.index("empty"))
        else:
            label = f"length_{int(length)}"
            if label not in SUFFIX_STRATUM_NAMES:
                raise ValueError("continuation length exceeds the frozen W4 strata")
            names.extend(
                (
                    SUFFIX_STRATUM_NAMES.index(label),
                    SUFFIX_STRATUM_NAMES.index("nonempty"),
                )
            )
        return tuple(names)

    def add_batch(
        self,
        intervention_index: int,
        band_index: int,
        context_index: int,
        continuation_length: int,
        diagnostics: Mapping[str, np.ndarray],
        selected_visible: np.ndarray | None,
        true_visible: np.ndarray,
    ) -> None:
        values = {
            name: np.asarray(diagnostics[name], dtype=np.float64)
            for name in self.METRICS
            if name in diagnostics
        }
        accuracy = np.asarray(diagnostics["accuracy"], dtype=np.float64)
        if selected_visible is None:
            selection_denominator = np.full_like(accuracy, np.nan)
            selection_joint = np.full_like(accuracy, np.nan)
        else:
            selected = np.asarray(selected_visible, dtype=np.int64)
            truth = np.asarray(true_visible, dtype=np.int64)
            selectable = selected >= 0
            selection_correct = selectable & (selected == truth)
            selection_denominator = selection_correct.astype(np.float64)
            selection_joint = selection_denominator * accuracy
            selection_denominator[~selectable] = np.nan
            selection_joint[~selectable] = np.nan
        values["correct_selection_denominator"] = selection_denominator
        values["correct_selection_and_suffix_correct"] = selection_joint
        for stratum in self._strata_for_length(int(continuation_length)):
            index = (
                int(intervention_index),
                int(band_index),
                int(context_index),
                int(stratum),
            )
            for name, array in values.items():
                finite = np.isfinite(array)
                self.sums[name][index] += float(np.sum(array[finite]))
                self.finite_counts[name][index] += int(np.count_nonzero(finite))

    def add_dense_panel(
        self,
        band_index: int,
        context_index: int,
        continuation_lengths: Sequence[int],
        diagnostics: Mapping[str, np.ndarray],
        selected_visible: Sequence[np.ndarray | None],
        true_visible: np.ndarray,
    ) -> None:
        """Accumulate ``[continuation, intervention, row]`` in frozen order."""

        lengths = tuple(int(value) for value in continuation_lengths)
        intervention_count = self.sums[self.METRICS[0]].shape[0]
        if len(selected_visible) != intervention_count:
            raise ValueError("dense context-stratum selector panel has wrong width")
        accuracy = np.asarray(diagnostics["accuracy"], dtype=np.float64)
        if accuracy.ndim != 3 or accuracy.shape[:2] != (
            len(lengths),
            intervention_count,
        ):
            raise ValueError("dense context-stratum diagnostic panel has wrong shape")
        row_count = accuracy.shape[2]
        truth = np.asarray(true_visible, dtype=np.int64).reshape(-1)
        if truth.size != row_count:
            raise ValueError("dense context-stratum truth width disagrees")
        values = {
            name: np.asarray(diagnostics[name], dtype=np.float64)
            for name in self.METRICS
            if name in diagnostics
        }
        for name, value in values.items():
            if value.shape != accuracy.shape:
                raise ValueError(f"dense context metric {name} has wrong shape")
        selection_denominator = np.full_like(accuracy, np.nan)
        selection_joint = np.full_like(accuracy, np.nan)
        for intervention_index, selected_raw in enumerate(selected_visible):
            if selected_raw is None:
                continue
            selected = np.asarray(selected_raw, dtype=np.int64).reshape(-1)
            if selected.size != row_count:
                raise ValueError("dense context selector width disagrees")
            selectable = selected >= 0
            correct = selectable & (selected == truth)
            denominator = correct.astype(np.float64)
            denominator[~selectable] = np.nan
            joint = denominator[None, :] * accuracy[:, intervention_index, :]
            joint[:, ~selectable] = np.nan
            selection_denominator[:, intervention_index, :] = denominator[None, :]
            selection_joint[:, intervention_index, :] = joint
        values["correct_selection_denominator"] = selection_denominator
        values["correct_selection_and_suffix_correct"] = selection_joint

        # Keep continuation order explicit.  Within a continuation, NumPy sums
        # the same row vector previously passed to add_batch, while all logical
        # interventions are reduced together.
        destination = (
            np.arange(intervention_count, dtype=np.int64),
            int(band_index),
            int(context_index),
        )
        for continuation_index, length in enumerate(lengths):
            for stratum in self._strata_for_length(length):
                for name, value in values.items():
                    row = value[continuation_index]
                    finite = np.isfinite(row)
                    self.sums[name][destination + (int(stratum),)] += np.sum(
                        np.where(finite, row, 0.0), axis=1
                    )
                    self.finite_counts[name][destination + (int(stratum),)] += np.sum(
                        finite, axis=1, dtype=np.int64
                    )

    def mean_summary(
        self,
        metric: str,
        intervention_index: int,
        band_index: int,
        stratum: str,
    ) -> dict[str, Any]:
        stratum_index = SUFFIX_STRATUM_NAMES.index(stratum)
        numerator = self.sums[metric][
            int(intervention_index), int(band_index), :, stratum_index
        ]
        denominator = self.finite_counts[metric][
            int(intervention_index), int(band_index), :, stratum_index
        ].astype(np.float64)
        return _context_ratio_summary(numerator, denominator)

    def ratio_summary(
        self,
        numerator_metric: str,
        denominator_metric: str,
        intervention_index: int,
        band_index: int,
        stratum: str,
    ) -> dict[str, Any]:
        stratum_index = SUFFIX_STRATUM_NAMES.index(stratum)
        numerator = self.sums[numerator_metric][
            int(intervention_index), int(band_index), :, stratum_index
        ]
        denominator = self.sums[denominator_metric][
            int(intervention_index), int(band_index), :, stratum_index
        ]
        return _context_ratio_summary(numerator, denominator)

    def serialize(self) -> dict[str, Any]:
        return {
            "axes": ["intervention", "nominal_depth_band", "context", "suffix_stratum"],
            "suffix_strata": list(SUFFIX_STRATUM_NAMES),
            "sum": {name: values.tolist() for name, values in self.sums.items()},
            "finite_count": {
                name: values.tolist() for name, values in self.finite_counts.items()
            },
        }


def _context_ratio_summary(
    numerator: np.ndarray, denominator: np.ndarray
) -> dict[str, Any]:
    numerator64 = np.asarray(numerator, dtype=np.float64)
    denominator64 = np.asarray(denominator, dtype=np.float64)
    valid = (
        np.isfinite(numerator64)
        & np.isfinite(denominator64)
        & (denominator64 > 0.0)
    )
    ratios = np.full(numerator64.shape, np.nan, dtype=np.float64)
    ratios[valid] = numerator64[valid] / denominator64[valid]
    return {
        "numerator_by_context": numerator64.tolist(),
        "denominator_by_context": denominator64.tolist(),
        "ratio_by_context": _json_safe_array(ratios),
        "equal_context_mean": (
            float(np.mean(ratios[valid])) if bool(np.any(valid)) else None
        ),
        "worst_context": (
            float(np.min(ratios[valid])) if bool(np.any(valid)) else None
        ),
        "zero_or_invalid_denominator_context_count": int(np.count_nonzero(~valid)),
        "all_context_denominators_positive": bool(np.all(valid)),
        "pooled_numerator": float(np.sum(numerator64[valid])),
        "pooled_denominator": float(np.sum(denominator64[valid])),
    }


def _summary_value(summary: Mapping[str, Any], key: str = "equal_context_mean") -> float:
    value = summary.get(key)
    return float(value) if value is not None else math.nan


def build_conditional_outcome_summaries(
    context_strata: ContextStratumAccumulator,
    bands: Sequence[int],
) -> dict[str, Any]:
    """Report context-equal conditional damage and rescue for every frozen cell."""

    output: dict[str, Any] = {}
    for intervention_index, intervention in enumerate(INTERVENTION_NAMES):
        by_band: dict[str, Any] = {}
        for band_index, band in enumerate(bands):
            by_stratum: dict[str, Any] = {}
            for stratum in SUFFIX_STRATUM_NAMES:
                damage = context_strata.ratio_summary(
                    "damage_numerator",
                    "damage_denominator",
                    intervention_index,
                    band_index,
                    stratum,
                )
                rescue = context_strata.ratio_summary(
                    "rescue_numerator",
                    "rescue_denominator",
                    intervention_index,
                    band_index,
                    stratum,
                )
                rescue_denominators = np.asarray(
                    rescue["denominator_by_context"], dtype=np.float64
                )
                if bool(np.all(np.isfinite(rescue_denominators))) and not bool(
                    np.any(rescue_denominators > 0.0)
                ):
                    rescue_status = "N/A_ZERO_NATIVE_ERROR_DENOMINATOR"
                elif rescue["all_context_denominators_positive"]:
                    rescue_status = "DEFINED_ALL_CONTEXTS"
                else:
                    rescue_status = "PARTIALLY_DEFINED_ZERO_CONTEXT_DENOMINATOR"
                damage["status"] = (
                    "DEFINED_ALL_CONTEXTS"
                    if damage["all_context_denominators_positive"]
                    else "PARTIALLY_DEFINED_ZERO_CONTEXT_DENOMINATOR"
                )
                rescue["status"] = rescue_status
                by_stratum[stratum] = {"damage": damage, "rescue": rescue}
            by_band[str(int(band))] = by_stratum
        output[intervention] = by_band
    return {
        "axes": ["intervention", "nominal_depth_band", "suffix_stratum"],
        "context_weighting": "equal context after within-context numerator/denominator",
        "zero_native_error_rescue_rule": "null/N/A, never treated as zero",
        "by_condition": output,
    }


def build_one_shot_gate_inputs(
    *,
    context_strata: ContextStratumAccumulator,
    bands: Sequence[int],
    native_summary: Mapping[str, Any] | None,
    exhaustive_selectors: Mapping[str, Any],
    selector_correct: Mapping[str, np.ndarray],
    selector_total: Mapping[str, np.ndarray],
    selector_idempotent: Mapping[str, Sequence[int]],
    selector_cut_hidden_maximum: Mapping[str, float],
) -> dict[str, Any]:
    """Compute every one-shot gate from preserved numerators and denominators."""

    intervention_index = {name: index for index, name in enumerate(INTERVENTION_NAMES)}
    band_index = {int(band): index for index, band in enumerate(bands)}
    native_decision_pass = False
    native_logit_pass = False
    if native_summary is not None:
        native_decision_pass = bool(
            native_summary["all_suffix_trace_equivalence_fraction"] >= 0.99
            and native_summary["joint_all_suffix_correct_fraction"] >= 0.99
            and native_summary["worst_context_trace_equivalence_fraction"] >= 0.95
        )
        native_logit_pass = bool(
            native_decision_pass
            and native_summary[
                "p95_pairwise_maximum_centered_logit_angle_with_undefined_as_pi"
            ]
            <= 0.05
            and native_summary["undefined_centered_logit_angle_count"] == 0
            and native_summary["p95_pairwise_maximum_softmax_total_variation"]
            <= 0.01
        )
    output: dict[str, Any] = {
        "native_finite_decision_trace_agreement_h4_coverage_0_99": {
            "inputs": native_summary,
            "pass": native_decision_pass,
        },
        "native_finite_logit_trace_agreement_h4_p95": {
            "inputs": native_summary,
            "pass": native_logit_pass,
        },
        "oracle": {},
        "autonomous": {},
        "state_specificity": {},
    }
    if 64 not in band_index:
        output["not_evaluated_reason"] = "nominal band 64 is absent"
        return output
    deep = band_index[64]
    shallow = band_index.get(8)
    random_accuracy = context_strata.mean_summary(
        "accuracy", intervention_index["random_ray"], deep, "nonempty"
    )

    def specificity(family: str) -> dict[str, Any]:
        wrong_name = "wrong_anchor" if family == "anchor" else "wrong_prototype"
        wrong = intervention_index[wrong_name]
        counterfactual_all = context_strata.mean_summary(
            "counterfactual_accuracy", wrong, deep, "all"
        )
        counterfactual_empty = context_strata.mean_summary(
            "counterfactual_accuracy", wrong, deep, "empty"
        )
        factual_all = context_strata.mean_summary("accuracy", wrong, deep, "all")
        passed = bool(
            counterfactual_all["all_context_denominators_positive"]
            and counterfactual_empty["all_context_denominators_positive"]
            and factual_all["all_context_denominators_positive"]
            and _summary_value(counterfactual_all) >= 0.95
            and _summary_value(counterfactual_empty) >= 0.95
            and _summary_value(factual_all) <= 0.05
        )
        record = {
            "wrong_condition": wrong_name,
            "counterfactual_accuracy_full_W4": counterfactual_all,
            "counterfactual_accuracy_empty_suffix": counterfactual_empty,
            "factual_leakage_full_W4": factual_all,
            "pass": passed,
        }
        output["state_specificity"][family] = record
        return record

    specificity_by_family = {
        family: specificity(family) for family in ("anchor", "prototype")
    }

    for condition, family in (
        ("oracle_anchor", "anchor"),
        ("oracle_prototype", "prototype"),
    ):
        index = intervention_index[condition]
        accuracy = context_strata.mean_summary("accuracy", index, deep, "nonempty")
        native_correct_agreement = context_strata.ratio_summary(
            "joint_native_h_and_candidate_correct",
            "native_h_accuracy",
            index,
            deep,
            "nonempty",
        )
        damage = context_strata.ratio_summary(
            "damage_numerator", "damage_denominator", index, deep, "nonempty"
        )
        empty_accuracy = context_strata.mean_summary(
            "accuracy", index, deep, "empty"
        )
        shallow_damage = (
            context_strata.ratio_summary(
                "damage_numerator",
                "damage_denominator",
                index,
                shallow,
                "nonempty",
            )
            if shallow is not None
            else None
        )
        random_margin = _summary_value(accuracy) - _summary_value(random_accuracy)
        passed = bool(
            accuracy["all_context_denominators_positive"]
            and native_correct_agreement["all_context_denominators_positive"]
            and damage["all_context_denominators_positive"]
            and empty_accuracy["all_context_denominators_positive"]
            and _summary_value(accuracy) >= 0.99
            and _summary_value(native_correct_agreement) >= 0.99
            and _summary_value(damage) <= 0.01
            and _summary_value(accuracy, "worst_context") >= 0.95
            and random_accuracy["all_context_denominators_positive"]
            and random_margin >= 0.20
            and _summary_value(empty_accuracy) == 1.0
            and _summary_value(empty_accuracy, "worst_context") == 1.0
            and shallow_damage is not None
            and shallow_damage["all_context_denominators_positive"]
            and _summary_value(shallow_damage) <= 0.01
            and specificity_by_family[family]["pass"]
        )
        output["oracle"][condition] = {
            "accuracy_nonempty_W4": accuracy,
            "agreement_on_native_correct_nonempty_W4": native_correct_agreement,
            "damage_nonempty_W4": damage,
            "empty_suffix_accuracy": empty_accuracy,
            "band_8_damage_nonempty_W4": shallow_damage,
            "random_ray_accuracy_nonempty_W4": random_accuracy,
            "accuracy_margin_over_random_ray": random_margin,
            "state_specificity": specificity_by_family[family],
            "pass": passed,
        }

    for condition, family in (
        ("self_anchor", "anchor"),
        ("nearest_anchor", "anchor"),
        ("self_prototype", "prototype"),
    ):
        index = intervention_index[condition]
        accuracy = context_strata.mean_summary("accuracy", index, deep, "nonempty")
        conditional_accuracy = context_strata.ratio_summary(
            "correct_selection_and_suffix_correct",
            "correct_selection_denominator",
            index,
            deep,
            "nonempty",
        )
        damage = context_strata.ratio_summary(
            "damage_numerator", "damage_denominator", index, deep, "nonempty"
        )
        shallow_damage = (
            context_strata.ratio_summary(
                "damage_numerator",
                "damage_denominator",
                index,
                shallow,
                "nonempty",
            )
            if shallow is not None
            else None
        )
        cut_denominator = int(np.sum(selector_total[condition][deep]))
        cut_numerator = int(np.sum(selector_correct[condition][deep]))
        selector_accuracy_value = (
            cut_numerator / cut_denominator if cut_denominator else math.nan
        )
        exhaustive = exhaustive_selectors[condition]
        section_validity = (
            exhaustive["section_validity_numerator"]
            / exhaustive["section_validity_denominator"]
        )
        decoder_consistency = (
            exhaustive["decoder_consistency_numerator"]
            / exhaustive["decoder_consistency_denominator"]
        )
        section_idempotence = (
            exhaustive["idempotence_numerator"]
            / exhaustive["idempotence_denominator"]
        )
        cut_idempotence = (
            selector_idempotent[condition][0]
            / selector_idempotent[condition][1]
            if selector_idempotent[condition][1]
            else math.nan
        )
        generator_pass = all(
            exhaustive["generators"][generator]["numerator"]
            / exhaustive["generators"][generator]["denominator"]
            >= 0.99
            and exhaustive["generators"][generator]["worst_context_accuracy"]
            >= 0.95
            for generator in ("r", "f")
        )
        random_margin = _summary_value(accuracy) - _summary_value(random_accuracy)
        structural_pass = bool(
            section_validity == 1.0
            and decoder_consistency == 1.0
            and section_idempotence == 1.0
            and cut_idempotence == 1.0
            and exhaustive["maximum_absolute_hidden_idempotence_difference"] <= 1e-6
            and selector_cut_hidden_maximum[condition] <= 1e-6
            and generator_pass
        )
        passed = bool(
            cut_denominator > 0
            and selector_accuracy_value >= 0.99
            and conditional_accuracy["all_context_denominators_positive"]
            and _summary_value(conditional_accuracy) >= 0.99
            and accuracy["all_context_denominators_positive"]
            and _summary_value(accuracy) >= 0.95
            and damage["all_context_denominators_positive"]
            and _summary_value(damage) <= 0.01
            and shallow_damage is not None
            and shallow_damage["all_context_denominators_positive"]
            and _summary_value(shallow_damage) <= 0.01
            and random_accuracy["all_context_denominators_positive"]
            and random_margin >= 0.20
            and structural_pass
            and specificity_by_family[family]["pass"]
        )
        output["autonomous"][condition] = {
            "selector_accuracy_at_cuts": {
                "numerator": cut_numerator,
                "denominator": cut_denominator,
                "value": selector_accuracy_value,
            },
            "conditional_suffix_accuracy_given_correct_selection": conditional_accuracy,
            "unconditional_accuracy_nonempty_W4": accuracy,
            "damage_nonempty_W4": damage,
            "band_8_damage_nonempty_W4": shallow_damage,
            "random_ray_accuracy_nonempty_W4": random_accuracy,
            "accuracy_margin_over_random_ray": random_margin,
            "section_validity": section_validity,
            "decoder_consistency": decoder_consistency,
            "section_idempotence": section_idempotence,
            "cut_idempotence": cut_idempotence,
            "section_hidden_idempotence_maximum": exhaustive[
                "maximum_absolute_hidden_idempotence_difference"
            ],
            "cut_hidden_idempotence_maximum": selector_cut_hidden_maximum[condition],
            "generators": exhaustive["generators"],
            "structural_prerequisites_pass": structural_pass,
            "state_specificity": specificity_by_family[family],
            "pass": passed,
        }
    return output


def _model_tensor_digest(model: nn.Module) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        array = tensor.detach().cpu().contiguous().numpy()
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(str(array.dtype).encode("ascii") + b"\0")
        digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
        digest.update(array.tobytes())
    return digest.hexdigest()


@torch.inference_mode()
def build_calibration_prototypes(
    model: nn.Module,
    context_bank: ContextBank,
    path_bank: PathPairBank,
    canonical_maps: np.ndarray,
) -> PrototypeBundle:
    """Fit held-out prototypes from calibration contexts and paired histories only."""

    states: list[torch.Tensor] = []
    labels: list[torch.Tensor] = []
    starts = np.arange(8, dtype=np.int64)
    stratum_count = 0
    ordered_pairs = tuple(
        sorted(
            path_bank.pairs,
            key=lambda pair: (
                pair.nominal_band,
                pair.endpoint,
                pair.pair_index,
            ),
        )
    )
    if ordered_pairs != path_bank.pairs:
        raise RuntimeError("calibration path bank is not in its frozen traversal order")
    for context_index in range(context_bank.tables.shape[0]):
        encoded = encode_context_once(model, context_bank.tables[context_index])
        phi = context_bank.phi[context_index]
        slots = context_bank.canonical_to_slot[context_index]
        for pair in ordered_pairs:
            for word in (pair.word_a, pair.word_b):
                trace = run_word_batch(
                    model,
                    encoded,
                    slots,
                    phi,
                    starts,
                    [word] * 8,
                )
                terminal = np.asarray(
                    [apply_state_word(canonical_maps, int(start), word) for start in starts],
                    dtype=np.int64,
                )
                states.append(trace.hidden[-1])
                labels.append(torch.from_numpy(phi[terminal]).long())
                stratum_count += 1
    all_states = torch.cat(states, dim=0)
    all_labels = torch.cat(labels, dim=0)
    bundle = prototypes_from_labeled_states(model, all_states, all_labels)
    audit = dict(bundle.audit)
    audit.update(
        {
            "source_split": "calibration_only",
            "source_cartesian_product": (
                "calibration_context_bank x calibration_path_bank"
            ),
            "contribution_order": [
                "context_index",
                "ascending_nominal_band",
                "canonical_endpoint",
                "pair_index",
                "lexicographic_member",
                "canonical_start",
            ],
            "float64_estimator_uses_symmetric_metric": True,
            "float32_packaged_normalization_applications_after_cast": 1,
            "context_count": int(context_bank.tables.shape[0]),
            "depth_bands": list(NOMINAL_DEPTH_BANDS),
            "group_endpoints": 8,
            "pairs_per_endpoint_band": PAIRS_PER_ENDPOINT_BAND,
            "pair_members": 2,
            "starts": 8,
            "complete_strata_processed": stratum_count,
        }
    )
    if not audit["balanced_visible_class_counts"]:
        raise RuntimeError("calibration prototype contributions are not class-balanced")
    return PrototypeBundle(
        torch32=bundle.torch32,
        numpy64=bundle.numpy64,
        audit=audit,
    )


def selector_labels(
    model: nn.Module,
    hidden: torch.Tensor,
    prototypes: PrototypeBundle,
) -> dict[str, torch.Tensor]:
    metric = model.invariant_metric()
    anchors = model.state_anchors()
    return {
        "self_anchor": checked_decode_hidden(model, hidden).argmax(dim=-1),
        "nearest_anchor": oriented_metric_selector(hidden, anchors, metric),
        "self_prototype": oriented_metric_selector(
            hidden, prototypes.torch32, metric
        ),
    }


@torch.inference_mode()
def selector_section_audit_for_context(
    model: nn.Module,
    encoded_context: torch.Tensor,
    canonical_to_slot: np.ndarray,
    phi: np.ndarray,
    canonical_maps: np.ndarray,
    prototypes: PrototypeBundle,
) -> dict[str, Any]:
    """Audit all eight section labels and both generator successors exhaustively."""

    phi_np = np.asarray(phi, dtype=np.int64)
    inverse_phi = np.argsort(phi_np)
    labels = torch.arange(8, dtype=torch.long)
    codes = encoded_context.expand(8, -1, -1, -1)
    output: dict[str, Any] = {}
    for name in ("self_anchor", "nearest_anchor", "self_prototype"):
        section = (
            prototypes.torch32
            if name == "self_prototype"
            else model.state_anchors()
        )
        first = selector_labels(model, section, prototypes)[name]
        if name == "self_prototype":
            reset_once = prototypes.torch32[first]
        else:
            reset_once = model.state_anchors()[first]
        second = selector_labels(model, reset_once, prototypes)[name]
        if name == "self_prototype":
            reset_twice = prototypes.torch32[second]
        else:
            reset_twice = model.state_anchors()[second]
        section_valid = first == labels
        decoder_consistent = checked_decode_hidden(model, section).argmax(dim=-1) == labels
        idempotent = second == first
        hidden_difference = torch.max(torch.abs(reset_twice - reset_once), dim=1).values
        generator_records: dict[str, Any] = {}
        for action, action_name in ((0, "r"), (1, "f")):
            slots = torch.full(
                (8, 1), int(canonical_to_slot[action]), dtype=torch.long
            )
            successor = model.continue_from_hidden(section, codes, slots)
            selected = selector_labels(model, successor.hidden[-1], prototypes)[name]
            canonical_labels = inverse_phi[np.arange(8)]
            expected_canonical = canonical_maps[action, canonical_labels]
            expected_visible = torch.from_numpy(phi_np[expected_canonical]).long()
            correct = selected == expected_visible
            generator_records[action_name] = {
                "numerator": int(torch.count_nonzero(correct).item()),
                "denominator": 8,
                "selected_visible": selected.tolist(),
                "expected_visible": expected_visible.tolist(),
            }
        output[name] = {
            "section_validity_numerator": int(
                torch.count_nonzero(section_valid).item()
            ),
            "section_validity_denominator": 8,
            "decoder_consistency_numerator": int(
                torch.count_nonzero(decoder_consistent).item()
            ),
            "decoder_consistency_denominator": 8,
            "idempotence_numerator": int(torch.count_nonzero(idempotent).item()),
            "idempotence_denominator": 8,
            "maximum_absolute_hidden_idempotence_difference": float(
                torch.max(hidden_difference).item()
            ),
            "generators": generator_records,
        }
    return output


def _json_safe_array(array: np.ndarray) -> Any:
    """Encode nonfinite diagnostic cells as null rather than nonstandard JSON NaN."""

    value = np.asarray(array)
    if np.issubdtype(value.dtype, np.floating):
        output = value.astype(object)
        output[~np.isfinite(value)] = None
        return output.tolist()
    return value.tolist()


@torch.inference_mode()
def evaluate_paired_model(
    model: nn.Module,
    context_bank: ContextBank,
    path_bank: PathPairBank,
    continuation_bank: ContinuationBank,
    canonical_maps: np.ndarray,
    prototypes: PrototypeBundle,
    encoded_contexts: Sequence[torch.Tensor] | None = None,
    secondary_continuation_bank: ContinuationBank | None = None,
    native_prefix_cache: dict[tuple[int, int, int], NativePrefixCacheEntry]
    | None = None,
) -> dict[str, Any]:
    """Run the frozen one-shot paired-history protocol on one model."""

    model = model.to(device="cpu").eval()
    verify_float32_model(model)
    primary_words = tuple(continuation_bank.words)
    secondary_words = (
        tuple(secondary_continuation_bank.words)
        if secondary_continuation_bank is not None
        else ()
    )
    if set(primary_words) & set(secondary_words):
        raise ValueError("primary and secondary continuation words overlap")
    tree_words = primary_words + secondary_words
    is_full_primary_w4 = primary_words == words_upto(
        CONTINUATION_MAX_LENGTH
    )
    before_digest = _model_tensor_digest(model)
    projector = construct_anchor_projector(model)
    bands = tuple(sorted({pair.nominal_band for pair in path_bank.pairs}))
    band_index = {band: index for index, band in enumerate(bands)}
    shape = (len(INTERVENTION_NAMES), len(bands), len(continuation_bank.words), 8)
    accumulator = TensorAccumulator(
        shape,
        axes=(
            "intervention",
            "nominal_depth_band",
            "continuation_word",
            "canonical_state_at_cut",
        ),
    )
    random_draw_accumulator = TensorAccumulator(
        (4, len(bands), len(continuation_bank.words), 8),
        axes=(
            "random_draw",
            "nominal_depth_band",
            "continuation_word",
            "canonical_state_at_cut",
        ),
    )
    secondary_accumulator = (
        TensorAccumulator(
            (len(INTERVENTION_NAMES), len(bands), len(secondary_words), 8),
            axes=(
                "intervention",
                "nominal_depth_band",
                "stress_word",
                "canonical_state_at_cut",
            ),
        )
        if secondary_words
        else None
    )
    secondary_random_draw_accumulator = (
        TensorAccumulator(
            (4, len(bands), len(secondary_words), 8),
            axes=(
                "random_draw",
                "nominal_depth_band",
                "stress_word",
                "canonical_state_at_cut",
            ),
        )
        if secondary_words
        else None
    )
    context_strata = ContextStratumAccumulator(
        len(INTERVENTION_NAMES), len(bands), context_bank.tables.shape[0]
    )
    random_key_manifest = make_random_key_manifest(
        context_bank.tables.shape[0], path_bank, split_code=2
    )
    consumed_base_stream_digest = hashlib.sha256()
    transformed_ray_digest = hashlib.sha256()
    context_metrics = ("accuracy", "native_h_agreement", "native_h_prime_agreement")
    context_sums = {
        name: np.zeros((len(INTERVENTION_NAMES), len(bands), context_bank.tables.shape[0]))
        for name in context_metrics
    }
    context_counts = {
        name: np.zeros_like(values, dtype=np.int64)
        for name, values in context_sums.items()
    }
    selector_names = ("self_anchor", "nearest_anchor", "self_prototype")
    selector_correct = {
        name: np.zeros((len(bands), 8), dtype=np.int64) for name in selector_names
    }
    selector_total = {
        name: np.zeros((len(bands), 8), dtype=np.int64) for name in selector_names
    }
    selector_idempotent = {name: [0, 0] for name in selector_names}
    selector_commutes = {name: [0, 0] for name in selector_names}
    selector_cut_hidden_idempotence_maximum = {name: 0.0 for name in selector_names}
    section_audits: list[dict[str, Any]] = []
    pair_shape = (context_bank.tables.shape[0], len(path_bank.pairs), 8)
    pair_max_disagreement = np.zeros(pair_shape, dtype=np.float64)
    pair_max_tv = np.zeros(pair_shape, dtype=np.float64)
    pair_max_angle = np.full(pair_shape, np.nan, dtype=np.float64)
    pair_undefined_angles = np.zeros(pair_shape, dtype=np.int64)
    pair_gate_angle_with_undefined_as_pi = np.zeros(pair_shape, dtype=np.float64)
    pair_joint_all_suffix_correct = np.zeros(pair_shape, dtype=np.float64)
    custom_rollout_max_hidden_difference = 0.0
    custom_rollout_max_logit_difference = 0.0
    custom_rollout_prediction_failures = 0
    sham_max_hidden_difference = 0.0
    sham_max_logit_difference = 0.0
    sham_prediction_failures = 0
    branch_max_hidden_difference_to_native = {
        name: 0.0 for name in INTERVENTION_NAMES if name != "random_ray"
    }
    branch_max_logit_difference_to_native = {
        name: 0.0 for name in INTERVENTION_NAMES if name != "random_ray"
    }
    target_firewall_cases = 0
    target_firewall_failures = 0
    direct_generator_firewall_cases = 0
    direct_generator_firewall_failures = 0
    wrong_state_identity_failures = 0
    starts = np.arange(8, dtype=np.int64)
    if encoded_contexts is not None and len(encoded_contexts) != context_bank.tables.shape[0]:
        raise ValueError("encoded evaluation-context cache has the wrong length")
    for context_index in range(context_bank.tables.shape[0]):
        phi_np = context_bank.phi[context_index]
        inverse_phi = np.argsort(phi_np)
        slots_np = context_bank.canonical_to_slot[context_index]
        visible_maps = context_bank.maps[context_index]
        phi = torch.from_numpy(phi_np).long()
        encoded_one = (
            encoded_contexts[context_index]
            if encoded_contexts is not None
            else encode_context_once(model, context_bank.tables[context_index])
        )
        if encoded_one.dtype != torch.float32 or not bool(torch.isfinite(encoded_one).all()):
            raise FloatingPointError("cached encoded context is not finite float32")
        metric = model.invariant_metric()
        section_audits.append(
            selector_section_audit_for_context(
                model,
                encoded_one,
                slots_np,
                phi_np,
                canonical_maps,
                prototypes,
            )
        )
        for action in (0, 1):
            slot = int(slots_np[action])
            for canonical_state in range(8):
                visible_state = int(phi_np[canonical_state])
                actual_visible = int(visible_maps[slot, visible_state])
                expected_visible = int(
                    phi_np[canonical_maps[action, canonical_state]]
                )
                direct_generator_firewall_cases += 1
                direct_generator_firewall_failures += int(
                    actual_visible != expected_visible
                )

        for pair_index, pair in enumerate(path_bank.pairs):
            prefix_index = band_index[pair.nominal_band]
            trace_h = run_word_batch(
                model, encoded_one, slots_np, phi_np, starts, [pair.word_a] * 8
            )
            trace_prime = run_word_batch(
                model, encoded_one, slots_np, phi_np, starts, [pair.word_b] * 8
            )
            hidden_h = trace_h.hidden[-1]
            hidden_prime = trace_prime.hidden[-1]
            cut_canonical = np.asarray(
                [
                    apply_state_word(canonical_maps, int(start), pair.word_a)
                    for start in starts
                ],
                dtype=np.int64,
            )
            cut_canonical_prime = np.asarray(
                [
                    apply_state_word(canonical_maps, int(start), pair.word_b)
                    for start in starts
                ],
                dtype=np.int64,
            )
            if not np.array_equal(cut_canonical, cut_canonical_prime):
                raise RuntimeError("endpoint-matched paths do not share semantic endpoints")
            if native_prefix_cache is not None and pair.nominal_band in (8, 64):
                for member_index, (word, trace) in enumerate(
                    ((pair.word_a, trace_h), (pair.word_b, trace_prime))
                ):
                    if len(trace.hidden) != len(word) + 1:
                        raise RuntimeError("packaged prefix trajectory has wrong length")
                    truth_at_step = starts.copy()
                    checkpoints: dict[
                        int, tuple[torch.Tensor, torch.Tensor, torch.Tensor]
                    ] = {}
                    for step, action in enumerate(word, start=1):
                        truth_at_step = canonical_maps[int(action), truth_at_step]
                        if step in (8, 16, 32):
                            state_at_step = trace.hidden[step]
                            checkpoints[step] = (
                                state_at_step.detach().clone(),
                                checked_decode_hidden(model, state_at_step)
                                .detach()
                                .clone(),
                                torch.from_numpy(
                                    truth_at_step.astype(np.int64, copy=True)
                                ).long(),
                            )
                    cache_key = (context_index, pair_index, member_index)
                    if cache_key in native_prefix_cache:
                        raise RuntimeError("native prefix cache key was populated twice")
                    native_prefix_cache[cache_key] = NativePrefixCacheEntry(
                        hidden=trace.hidden[-1].detach().clone(),
                        logits=trace.logits.detach().clone(),
                        true_canonical=torch.from_numpy(
                            truth_at_step.astype(np.int64, copy=True)
                        ).long(),
                        checkpoints=checkpoints,
                        # One contiguous tensor, rather than one Python mapping
                        # entry/tensor triple per step, bounds the shared-cache
                        # object overhead while retaining every sham reference.
                        trajectory_hidden=torch.stack(
                            tuple(trace.hidden[1:]), dim=0
                        ).detach().clone(),
                    )
            cut_tensor = torch.from_numpy(cut_canonical).long()
            codes_base = encoded_one.expand(8, -1, -1, -1)

            # Integer-map target firewall, including randomized visible slot order.
            for firewall_word in (pair.word_a, pair.word_b):
                visible_current = phi_np[starts].copy()
                for action in firewall_word:
                    slot = int(slots_np[int(action)])
                    visible_current = visible_maps[slot, visible_current]
                target_firewall_cases += 8
                target_firewall_failures += int(
                    np.count_nonzero(visible_current != phi_np[cut_canonical])
                )

            if pair_index == 0:
                word_slots = torch.from_numpy(
                    canonical_words_to_slots([pair.word_a] * 8, slots_np)
                ).long()
                initial = model.initial_hidden(torch.from_numpy(phi_np[starts]).long())
                custom = custom_rollout_float32(
                    model, initial, codes_base, word_slots
                )
                packaged = trace_h
                custom_rollout_max_hidden_difference = max(
                    custom_rollout_max_hidden_difference,
                    float(torch.max(torch.abs(custom.hidden[-1] - packaged.hidden[-1])).item()),
                )
                custom_rollout_max_logit_difference = max(
                    custom_rollout_max_logit_difference,
                    float(torch.max(torch.abs(custom.logits - packaged.logits)).item()),
                )
                custom_rollout_prediction_failures += int(
                    torch.count_nonzero(
                        custom.logits.argmax(dim=-1)
                        != packaged.logits.argmax(dim=-1)
                    ).item()
                )

            # Stack both source orientations with equal multiplicity. The random-ray
            # key deliberately omits orientation, so the same four rays serve both.
            source_hidden = torch.cat((hidden_h, hidden_prime), dim=0)
            other_hidden = torch.cat((hidden_prime, hidden_h), dim=0)
            cut_canonical_oriented = np.tile(cut_canonical, 2)
            cut_tensor_oriented = torch.from_numpy(cut_canonical_oriented).long()
            cut_visible_oriented = phi[cut_tensor_oriented]
            codes = encoded_one.expand(16, -1, -1, -1)
            random_base = random_ray_states(
                model,
                split_code=2,
                context_id=context_index,
                pair=pair,
                starts=starts,
                base_stream_digest=consumed_base_stream_digest,
            )
            transformed_ray_digest.update(
                random_base.detach().cpu().contiguous().numpy().tobytes()
            )
            interventions = construct_interventions(
                model,
                source_hidden,
                other_hidden,
                cut_tensor_oriented,
                phi,
                canonical_maps,
                projector,
                prototypes,
            )
            for wrong_name in ("wrong_anchor", "wrong_prototype"):
                wrong_state_identity_failures += int(
                    torch.count_nonzero(
                        interventions.selected_visible[wrong_name]
                        == cut_visible_oriented
                    ).item()
                )
            sham_max_hidden_difference = max(
                sham_max_hidden_difference,
                float(
                    torch.max(
                        torch.abs(interventions.hidden["sham_scale"] - source_hidden)
                    ).item()
                ),
            )

            selected = selector_labels(model, source_hidden, prototypes)
            for name in selector_names:
                selected_np = selected[name].detach().cpu().numpy()
                for row, cut_state in enumerate(cut_canonical_oriented):
                    selector_total[name][prefix_index, cut_state] += 1
                    selector_correct[name][prefix_index, cut_state] += int(
                        selected_np[row] == phi_np[cut_state]
                    )

                if name == "self_anchor":
                    section = model.state_anchors()[selected[name]]
                elif name == "nearest_anchor":
                    section = model.state_anchors()[selected[name]]
                else:
                    section = prototypes.torch32[selected[name]]
                selected_twice = selector_labels(model, section, prototypes)[name]
                if name == "self_prototype":
                    section_twice = prototypes.torch32[selected_twice]
                else:
                    section_twice = model.state_anchors()[selected_twice]
                selector_idempotent[name][0] += int(
                    torch.count_nonzero(selected_twice == selected[name]).item()
                )
                selector_idempotent[name][1] += int(selected[name].numel())
                selector_cut_hidden_idempotence_maximum[name] = max(
                    selector_cut_hidden_idempotence_maximum[name],
                    float(torch.max(torch.abs(section_twice - section)).item()),
                )

                selected_canonical = inverse_phi[selected_np]
                for action in (0, 1):
                    next_slots = torch.full(
                        (16, 1), int(slots_np[action]), dtype=torch.long
                    )
                    next_trace = model.continue_from_hidden(
                        section, codes, next_slots
                    )
                    next_selected = selector_labels(
                        model, next_trace.hidden[-1], prototypes
                    )[name]
                    expected_canonical = canonical_maps[action, selected_canonical]
                    expected_visible = torch.from_numpy(phi_np[expected_canonical]).long()
                    selector_commutes[name][0] += int(
                        torch.count_nonzero(next_selected == expected_visible).item()
                    )
                    selector_commutes[name][1] += 16

            # Exactly twenty physically distinct eight-start branches remain after
            # reusing native histories and every orientation-invariant reset. Stack
            # all 160 states and traverse the suffix set once, so a W4 tree edge is
            # one batched recurrent call rather than one call per intervention.
            physical_groups = (
                hidden_h,
                hidden_prime,
                interventions.hidden["sham_scale"][:8],
                interventions.hidden["sham_scale"][8:],
                interventions.hidden["oracle_anchor"][:8],
                interventions.hidden["self_anchor"][:8],
                interventions.hidden["self_anchor"][8:],
                interventions.hidden["nearest_anchor"][:8],
                interventions.hidden["nearest_anchor"][8:],
                interventions.hidden["oracle_prototype"][:8],
                interventions.hidden["self_prototype"][:8],
                interventions.hidden["self_prototype"][8:],
                interventions.hidden["anchor_projection"][:8],
                interventions.hidden["anchor_projection"][8:],
                interventions.hidden["wrong_anchor"][:8],
                interventions.hidden["wrong_prototype"][:8],
                random_base[0],
                random_base[1],
                random_base[2],
                random_base[3],
            )
            if len(physical_groups) != 20 or any(
                group.shape != (8, 12) for group in physical_groups
            ):
                raise RuntimeError("one-shot physical branch stack is malformed")
            physical_tree = rollout_word_set_reusing_tree(
                model,
                torch.cat(physical_groups, dim=0),
                encoded_one,
                slots_np,
                tree_words,
            )

            def physical_trace(node: SimpleNamespace, group: int) -> SimpleNamespace:
                start_row = int(group) * 8
                stop_row = start_row + 8
                return SimpleNamespace(
                    hidden=node.hidden[start_row:stop_row],
                    logits=node.logits[start_row:stop_row],
                )

            oriented_groups = {
                "native_h": (0, 1),
                "native_h_prime": (1, 0),
                "sham_scale": (2, 3),
                "oracle_anchor": (4, 4),
                "self_anchor": (5, 6),
                "nearest_anchor": (7, 8),
                "oracle_prototype": (9, 9),
                "self_prototype": (10, 11),
                "anchor_projection": (12, 13),
                "wrong_anchor": (14, 14),
                "wrong_prototype": (15, 15),
            }

            # Materialize the small completed suffix tree in frozen word order,
            # then cross the NumPy diagnostic boundary once for the whole panel.
            # This preserves every logical cell while avoiding one Python/NumPy
            # call per continuation (and, below, per periodic logical mode).
            word_count = len(tree_words)
            physical_hidden = torch.stack(
                tuple(physical_tree[word].hidden for word in tree_words), dim=0
            ).reshape(word_count, 20, 8, 12)
            physical_logits = torch.stack(
                tuple(physical_tree[word].logits for word in tree_words), dim=0
            ).reshape(word_count, 20, 8, 8)
            target_canonical_base = np.stack(
                tuple(
                    np.asarray(
                        [
                            apply_state_word(canonical_maps, int(state), word)
                            for state in cut_canonical
                        ],
                        dtype=np.int64,
                    )
                    for word in tree_words
                ),
                axis=0,
            )
            target_visible_base = phi[torch.from_numpy(target_canonical_base).long()]
            pair_native_hidden = physical_hidden[:, 0]
            pair_native_logits = physical_logits[:, 0]
            pair_prime_hidden = physical_hidden[:, 1]
            pair_prime_logits = physical_logits[:, 1]
            native_pair_flat = paired_future_diagnostics(
                pair_native_logits.reshape(-1, 8),
                pair_prime_logits.reshape(-1, 8),
                pair_native_hidden.reshape(-1, 12),
                pair_prime_hidden.reshape(-1, 12),
                target_visible_base.reshape(-1),
                metric,
                native_prime_logits=pair_prime_logits.reshape(-1, 8),
                native_prime_hidden=pair_prime_hidden.reshape(-1, 12),
            )
            native_pair = {
                name: value.reshape(word_count, 8)
                for name, value in native_pair_flat.items()
            }

            target_canonical = np.concatenate(
                (target_canonical_base, target_canonical_base), axis=1
            )
            target_visible = phi[torch.from_numpy(target_canonical).long()]
            wrong_cut = canonical_maps[0, cut_canonical_oriented]
            wrong_future = np.stack(
                tuple(
                    np.asarray(
                        [
                            apply_state_word(canonical_maps, int(state), word)
                            for state in wrong_cut
                        ],
                        dtype=np.int64,
                    )
                    for word in tree_words
                ),
                axis=0,
            )
            counterfactual_visible = phi[torch.from_numpy(wrong_future).long()]
            native_future_hidden = torch.cat(
                (physical_hidden[:, 0], physical_hidden[:, 1]), dim=1
            )
            native_future_logits = torch.cat(
                (physical_logits[:, 0], physical_logits[:, 1]), dim=1
            )
            prime_future_hidden = torch.cat(
                (physical_hidden[:, 1], physical_hidden[:, 0]), dim=1
            )
            prime_future_logits = torch.cat(
                (physical_logits[:, 1], physical_logits[:, 0]), dim=1
            )
            nonrandom_names = tuple(
                name for name in INTERVENTION_NAMES if name != "random_ray"
            )
            candidate_hidden_by_name: dict[str, torch.Tensor] = {}
            candidate_logits_by_name: dict[str, torch.Tensor] = {}
            candidate_hidden: list[torch.Tensor] = []
            candidate_logits: list[torch.Tensor] = []
            counterfactual_targets: list[torch.Tensor] = []
            for name in nonrandom_names:
                if name not in oriented_groups:
                    raise RuntimeError(f"unmapped one-shot intervention branch: {name}")
                left_group, right_group = oriented_groups[name]
                hidden = torch.cat(
                    (physical_hidden[:, left_group], physical_hidden[:, right_group]),
                    dim=1,
                )
                logits = torch.cat(
                    (physical_logits[:, left_group], physical_logits[:, right_group]),
                    dim=1,
                )
                candidate_hidden_by_name[name] = hidden
                candidate_logits_by_name[name] = logits
                candidate_hidden.append(hidden)
                candidate_logits.append(logits)
                counterfactual_targets.append(
                    counterfactual_visible
                    if name in ("wrong_anchor", "wrong_prototype")
                    else target_visible
                )
                branch_max_hidden_difference_to_native[name] = max(
                    branch_max_hidden_difference_to_native[name],
                    float(torch.max(torch.abs(hidden - native_future_hidden)).item()),
                )
                branch_max_logit_difference_to_native[name] = max(
                    branch_max_logit_difference_to_native[name],
                    float(torch.max(torch.abs(logits - native_future_logits)).item()),
                )
            for draw_id in range(4):
                random_hidden = torch.cat(
                    (physical_hidden[:, 16 + draw_id], physical_hidden[:, 16 + draw_id]),
                    dim=1,
                )
                random_logits = torch.cat(
                    (physical_logits[:, 16 + draw_id], physical_logits[:, 16 + draw_id]),
                    dim=1,
                )
                candidate_hidden.append(random_hidden)
                candidate_logits.append(random_logits)
                counterfactual_targets.append(target_visible)
            diagnostic_group_count = len(candidate_hidden)
            if diagnostic_group_count != len(nonrandom_names) + 4:
                raise RuntimeError("one-shot diagnostic stack has wrong group count")
            candidate_hidden_tensor = torch.stack(candidate_hidden, dim=1)
            candidate_logits_tensor = torch.stack(candidate_logits, dim=1)
            stacked_diagnostics_flat = paired_future_diagnostics(
                native_future_logits[:, None].expand(
                    -1, diagnostic_group_count, -1, -1
                ).reshape(-1, 8),
                candidate_logits_tensor.reshape(-1, 8),
                native_future_hidden[:, None].expand(
                    -1, diagnostic_group_count, -1, -1
                ).reshape(-1, 12),
                candidate_hidden_tensor.reshape(-1, 12),
                target_visible[:, None].expand(
                    -1, diagnostic_group_count, -1
                ).reshape(-1),
                metric,
                native_prime_logits=prime_future_logits[:, None].expand(
                    -1, diagnostic_group_count, -1, -1
                ).reshape(-1, 8),
                native_prime_hidden=prime_future_hidden[:, None].expand(
                    -1, diagnostic_group_count, -1, -1
                ).reshape(-1, 12),
                counterfactual_visible=torch.stack(counterfactual_targets, dim=1)
                .reshape(-1),
            )
            stacked_diagnostics = {
                name: value.reshape(word_count, diagnostic_group_count, 16)
                for name, value in stacked_diagnostics_flat.items()
            }
            nonrandom_index = {name: index for index, name in enumerate(nonrandom_names)}
            random_group_slice = slice(len(nonrandom_names), diagnostic_group_count)
            intervention_panel = {
                metric_name: np.stack(
                    tuple(
                        (
                            np.mean(values[:, random_group_slice, :], axis=1)
                            if intervention == "random_ray"
                            else values[:, nonrandom_index[intervention], :]
                        )
                        for intervention in INTERVENTION_NAMES
                    ),
                    axis=1,
                )
                for metric_name, values in stacked_diagnostics.items()
            }

            sham_hidden = candidate_hidden_by_name["sham_scale"]
            sham_logits = candidate_logits_by_name["sham_scale"]
            sham_max_hidden_difference = max(
                sham_max_hidden_difference,
                float(torch.max(torch.abs(sham_hidden - native_future_hidden)).item()),
            )
            sham_max_logit_difference = max(
                sham_max_logit_difference,
                float(torch.max(torch.abs(sham_logits - native_future_logits)).item()),
            )
            sham_prediction_failures += int(
                torch.count_nonzero(
                    sham_logits.argmax(dim=-1)
                    != native_future_logits.argmax(dim=-1)
                ).item()
            )

            primary_count = len(primary_words)
            accumulator.add_dense_panel(
                np.arange(len(INTERVENTION_NAMES), dtype=np.int64),
                np.full(len(INTERVENTION_NAMES), prefix_index, dtype=np.int64),
                np.arange(primary_count, dtype=np.int64),
                np.broadcast_to(
                    cut_canonical_oriented[None, :],
                    (len(INTERVENTION_NAMES), cut_canonical_oriented.size),
                ),
                {
                    name: np.transpose(value[:primary_count], (1, 0, 2))
                    for name, value in intervention_panel.items()
                },
            )
            random_draw_panel = {
                name: np.transpose(
                    value[:, random_group_slice, :], (1, 0, 2)
                )
                for name, value in stacked_diagnostics.items()
            }
            random_draw_accumulator.add_dense_panel(
                np.arange(4, dtype=np.int64),
                np.full(4, prefix_index, dtype=np.int64),
                np.arange(primary_count, dtype=np.int64),
                np.broadcast_to(cut_canonical_oriented[None, :], (4, 16)),
                {name: value[:, :primary_count] for name, value in random_draw_panel.items()},
            )
            if secondary_words:
                if secondary_accumulator is None or secondary_random_draw_accumulator is None:
                    raise RuntimeError("secondary continuation accumulators are absent")
                secondary_count = len(secondary_words)
                secondary_accumulator.add_dense_panel(
                    np.arange(len(INTERVENTION_NAMES), dtype=np.int64),
                    np.full(len(INTERVENTION_NAMES), prefix_index, dtype=np.int64),
                    np.arange(secondary_count, dtype=np.int64),
                    np.broadcast_to(
                        cut_canonical_oriented[None, :],
                        (len(INTERVENTION_NAMES), 16),
                    ),
                    {
                        name: np.transpose(value[primary_count:], (1, 0, 2))
                        for name, value in intervention_panel.items()
                    },
                )
                secondary_random_draw_accumulator.add_dense_panel(
                    np.arange(4, dtype=np.int64),
                    np.full(4, prefix_index, dtype=np.int64),
                    np.arange(secondary_count, dtype=np.int64),
                    np.broadcast_to(cut_canonical_oriented[None, :], (4, 16)),
                    {
                        name: value[:, primary_count:]
                        for name, value in random_draw_panel.items()
                    },
                )

            selected_panel = tuple(
                (
                    interventions.selected_visible[name].detach().cpu().numpy()
                    if name in interventions.selected_visible
                    else None
                )
                for name in INTERVENTION_NAMES
            )
            context_strata.add_dense_panel(
                prefix_index,
                context_index,
                tuple(len(word) for word in primary_words),
                {name: value[:primary_count] for name, value in intervention_panel.items()},
                selected_panel,
                cut_visible_oriented.detach().cpu().numpy(),
            )
            for continuation_index in range(primary_count):
                for metric_name in context_metrics:
                    values = intervention_panel[metric_name][continuation_index]
                    finite = np.isfinite(values)
                    context_sums[metric_name][:, prefix_index, context_index] += np.sum(
                        np.where(finite, values, 0.0), axis=1
                    )
                    context_counts[metric_name][:, prefix_index, context_index] += np.sum(
                        finite, axis=1, dtype=np.int64
                    )

            disagreement_stack = 1.0 - native_pair["native_h_agreement"][:primary_count]
            tv_stack = native_pair["softmax_tv_to_native_h"][:primary_count]
            angle_stack = native_pair["centered_logit_angle_to_native_h"][:primary_count]
            joint_stack = (
                native_pair["native_h_accuracy"][:primary_count]
                * native_pair["accuracy"][:primary_count]
            )
            pair_max_disagreement[context_index, pair_index] = np.max(
                disagreement_stack, axis=0
            )
            pair_max_tv[context_index, pair_index] = np.max(tv_stack, axis=0)
            pair_joint_all_suffix_correct[context_index, pair_index] = np.min(
                joint_stack, axis=0
            )
            for start_index in range(8):
                finite = angle_stack[:, start_index][
                    np.isfinite(angle_stack[:, start_index])
                ]
                pair_undefined_angles[context_index, pair_index, start_index] = int(
                    angle_stack.shape[0] - finite.size
                )
                if finite.size:
                    pair_max_angle[context_index, pair_index, start_index] = float(
                        np.max(finite)
                    )
                pair_gate_angle_with_undefined_as_pi[
                    context_index, pair_index, start_index
                ] = (
                    math.pi
                    if finite.size != angle_stack.shape[0]
                    else float(np.max(finite))
                )

    after_digest = _model_tensor_digest(model)
    if before_digest != after_digest:
        raise RuntimeError("model state dictionary changed during analysis")
    if target_firewall_failures:
        raise RuntimeError("integer-map target firewall failed")
    if direct_generator_firewall_failures:
        raise RuntimeError("direct state-generator target firewall failed")
    if wrong_state_identity_failures:
        raise RuntimeError("a frozen wrong-state control did not differ from truth")
    consumed_base_stream_sha256 = consumed_base_stream_digest.hexdigest()
    if (
        consumed_base_stream_sha256
        != random_key_manifest["base_standard_normal_stream_sha256"]
    ):
        raise RuntimeError("runtime random-ray base stream differs from frozen manifest")
    with np.errstate(invalid="ignore", divide="ignore"):
        context_means = {
            name: context_sums[name] / context_counts[name] for name in context_metrics
        }
        selector_accuracy = {
            name: selector_correct[name] / selector_total[name] for name in selector_names
        }
    checkpoint_equal_context_mean = {
        name: np.nanmean(values, axis=2) for name, values in context_means.items()
    }
    deepest_pair_indices = [
        index for index, pair in enumerate(path_bank.pairs) if pair.nominal_band == 64
    ]
    native_gate_summary: dict[str, Any] | None = None
    if deepest_pair_indices:
        deep_disagreement = pair_max_disagreement[:, deepest_pair_indices, :]
        deep_joint = pair_joint_all_suffix_correct[:, deepest_pair_indices, :]
        deep_tv = pair_max_tv[:, deepest_pair_indices, :]
        deep_angle = pair_gate_angle_with_undefined_as_pi[:, deepest_pair_indices, :]
        deep_undefined = pair_undefined_angles[:, deepest_pair_indices, :]
        per_context_trace = np.mean(deep_disagreement == 0.0, axis=(1, 2))
        per_context_joint = np.mean(deep_joint == 1.0, axis=(1, 2))
        native_gate_summary = {
            "deepest_nominal_band": 64,
            "all_suffix_trace_equivalence_fraction": float(
                np.mean(deep_disagreement == 0.0)
            ),
            "joint_all_suffix_correct_fraction": float(np.mean(deep_joint == 1.0)),
            "worst_context_trace_equivalence_fraction": float(
                np.min(per_context_trace)
            ),
            "worst_context_joint_all_suffix_correct_fraction": float(
                np.min(per_context_joint)
            ),
            "p95_pairwise_maximum_softmax_total_variation": float(
                np.quantile(deep_tv, 0.95, method="higher")
            ),
            "p95_pairwise_maximum_centered_logit_angle_with_undefined_as_pi": float(
                np.quantile(deep_angle, 0.95, method="higher")
            ),
            "undefined_centered_logit_angle_count": int(np.sum(deep_undefined)),
            "case_count": int(deep_disagreement.size),
        }

    exhaustive_selector_summary: dict[str, Any] = {}
    for name in selector_names:
        section_numerator = sum(
            context[name]["section_validity_numerator"] for context in section_audits
        )
        section_denominator = sum(
            context[name]["section_validity_denominator"] for context in section_audits
        )
        decoder_numerator = sum(
            context[name]["decoder_consistency_numerator"] for context in section_audits
        )
        decoder_denominator = sum(
            context[name]["decoder_consistency_denominator"] for context in section_audits
        )
        idem_numerator = sum(
            context[name]["idempotence_numerator"] for context in section_audits
        )
        idem_denominator = sum(
            context[name]["idempotence_denominator"] for context in section_audits
        )
        generator_summary: dict[str, Any] = {}
        for generator_name in ("r", "f"):
            values = [
                context[name]["generators"][generator_name]["numerator"]
                / context[name]["generators"][generator_name]["denominator"]
                for context in section_audits
            ]
            generator_summary[generator_name] = {
                "numerator": sum(
                    context[name]["generators"][generator_name]["numerator"]
                    for context in section_audits
                ),
                "denominator": sum(
                    context[name]["generators"][generator_name]["denominator"]
                    for context in section_audits
                ),
                "worst_context_accuracy": min(values),
            }
        exhaustive_selector_summary[name] = {
            "section_validity_numerator": section_numerator,
            "section_validity_denominator": section_denominator,
            "decoder_consistency_numerator": decoder_numerator,
            "decoder_consistency_denominator": decoder_denominator,
            "idempotence_numerator": idem_numerator,
            "idempotence_denominator": idem_denominator,
            "maximum_absolute_hidden_idempotence_difference": max(
                context[name]["maximum_absolute_hidden_idempotence_difference"]
                for context in section_audits
            ),
            "generators": generator_summary,
        }
    one_shot_gate_inputs = (
        build_one_shot_gate_inputs(
            context_strata=context_strata,
            bands=bands,
            native_summary=native_gate_summary,
            exhaustive_selectors=exhaustive_selector_summary,
            selector_correct=selector_correct,
            selector_total=selector_total,
            selector_idempotent=selector_idempotent,
            selector_cut_hidden_maximum=selector_cut_hidden_idempotence_maximum,
        )
        if is_full_primary_w4
        else {
            "not_evaluated_reason": (
                "fixed one-shot gates require the exact exhaustive 31-word W4 bank"
            )
        }
    )
    time_zero_labels = torch.arange(8, dtype=torch.long)
    time_zero_native = model.initial_hidden(time_zero_labels)
    time_zero_oracle_anchor = model.state_anchors()[time_zero_labels]
    time_zero_hidden_difference = float(
        torch.max(torch.abs(time_zero_native - time_zero_oracle_anchor)).item()
    )
    time_zero_decoding_equal = bool(
        torch.equal(
            checked_decode_hidden(model, time_zero_native).argmax(dim=-1),
            checked_decode_hidden(model, time_zero_oracle_anchor).argmax(dim=-1),
        )
    )
    time_zero_oracle_anchor_pass = bool(
        time_zero_hidden_difference <= 1e-6 and time_zero_decoding_equal
    )
    custom_rollout_pass = bool(
        custom_rollout_max_hidden_difference <= 1e-6
        and custom_rollout_max_logit_difference <= 1e-6
        and custom_rollout_prediction_failures == 0
    )
    sham_scale_pass = bool(
        sham_max_hidden_difference <= 1e-6
        and sham_max_logit_difference <= 1e-5
        and sham_prediction_failures == 0
    )
    if not custom_rollout_pass:
        raise RuntimeError("custom rollout does not match packaged rollout")
    if not sham_scale_pass:
        raise RuntimeError("sham scale control failed")
    if not time_zero_oracle_anchor_pass:
        raise RuntimeError("time-zero oracle-anchor identity control failed")
    return {
        "interventions": list(INTERVENTION_NAMES),
        "nominal_depth_bands": list(bands),
        "continuation_words": [list(word) for word in continuation_bank.words],
        "future": accumulator.serialize(),
        "context_summary_axes": ["intervention", "nominal_depth_band", "context"],
        "context_sum": {
            name: values.tolist() for name, values in context_sums.items()
        },
        "context_count": {
            name: values.tolist() for name, values in context_counts.items()
        },
        "context_mean": {
            name: _json_safe_array(values) for name, values in context_means.items()
        },
        "checkpoint_equal_context_mean_axes": [
            "intervention",
            "nominal_depth_band",
        ],
        "checkpoint_equal_context_mean": {
            name: _json_safe_array(values)
            for name, values in checkpoint_equal_context_mean.items()
        },
        "context_equal_suffix_stratum_reductions": context_strata.serialize(),
        "conditional_damage_and_rescue": build_conditional_outcome_summaries(
            context_strata, bands
        ),
        "native_pair_pseudometric_axes": ["context", "path_pair", "canonical_start"],
        "native_pair_pseudometric": {
            "maximum_argmax_disagreement": pair_max_disagreement.tolist(),
            "maximum_softmax_total_variation": pair_max_tv.tolist(),
            "maximum_centered_logit_angle": _json_safe_array(pair_max_angle),
            "gate_angle_with_undefined_as_pi": pair_gate_angle_with_undefined_as_pi.tolist(),
            "undefined_centered_logit_angle_count": pair_undefined_angles.tolist(),
            "joint_correct_for_every_suffix": pair_joint_all_suffix_correct.tolist(),
            "maximum_argmax_disagreement_distribution": numeric_summary(
                pair_max_disagreement.reshape(-1)
            ),
            "maximum_softmax_total_variation_distribution": numeric_summary(
                pair_max_tv.reshape(-1)
            ),
            "maximum_centered_logit_angle_distribution": numeric_summary(
                pair_max_angle.reshape(-1)
            ),
        },
        "native_deepest_band_gate_inputs": native_gate_summary,
        "fixed_gate_inputs": one_shot_gate_inputs,
        "selector_accuracy_axes": ["nominal_depth_band", "canonical_state_at_cut"],
        "selectors": {
            name: {
                "correct": selector_correct[name].tolist(),
                "total": selector_total[name].tolist(),
                "accuracy": _json_safe_array(selector_accuracy[name]),
                "idempotence_numerator": selector_idempotent[name][0],
                "idempotence_denominator": selector_idempotent[name][1],
                "cut_state_maximum_absolute_hidden_idempotence_difference": selector_cut_hidden_idempotence_maximum[name],
                "one_step_commutation_numerator": selector_commutes[name][0],
                "one_step_commutation_denominator": selector_commutes[name][1],
            }
            for name in selector_names
        },
        "exhaustive_section_selector_audit": exhaustive_selector_summary,
        "per_context_exhaustive_section_selector_audit": section_audits,
        "random_ray": {
            "draws_per_unordered_pair_start_case": 4,
            "same_draws_reused_across_source_orientations": True,
            "case_metrics_average_draws_before_context_aggregation": True,
            "key_manifest_receipt": {
                "sha256": random_key_manifest["sha256"],
                "key_count": random_key_manifest["key_count"],
                "base_standard_normal_stream_sha256": random_key_manifest[
                    "base_standard_normal_stream_sha256"
                ],
            },
            "consumed_base_stream_order": (
                "context,path_pair,start,draw,coordinate; each vector float64 C-order"
            ),
            "consumed_base_standard_normal_stream_sha256": (
                consumed_base_stream_sha256
            ),
            "base_stream_matches_key_manifest": True,
            "transformed_float32_ray_order": (
                "context,path_pair,draw,start,hidden_coordinate; float32 C-order"
            ),
            "transformed_float32_ray_sha256": transformed_ray_digest.hexdigest(),
            "raw_draw_metrics": random_draw_accumulator.serialize(),
        },
        "secondary_stress_descriptive": (
            {
                "continuation_words": [list(word) for word in secondary_words],
                "future": secondary_accumulator.serialize(),
                "random_ray_raw_draw_metrics": (
                    secondary_random_draw_accumulator.serialize()
                ),
                "shares_native_prefixes_sections_random_rays_with_primary": True,
                "enters_primary_gates": False,
            }
            if secondary_accumulator is not None
            and secondary_random_draw_accumulator is not None
            else None
        ),
        "controls": {
            "projector": projector.audit,
            "custom_rollout_max_hidden_absolute_difference": custom_rollout_max_hidden_difference,
            "custom_rollout_max_logit_absolute_difference": custom_rollout_max_logit_difference,
            "custom_rollout_prediction_failures": custom_rollout_prediction_failures,
            "custom_rollout_matches_packaged": custom_rollout_pass,
            "sham_scale_max_hidden_absolute_difference": sham_max_hidden_difference,
            "sham_scale_max_logit_absolute_difference": sham_max_logit_difference,
            "sham_scale_prediction_failures": sham_prediction_failures,
            "sham_scale_within_float32_tolerance": sham_scale_pass,
            "target_firewall_cases": target_firewall_cases,
            "target_firewall_failures": target_firewall_failures,
            "direct_state_generator_firewall_cases": direct_generator_firewall_cases,
            "direct_state_generator_firewall_failures": (
                direct_generator_firewall_failures
            ),
            "time_zero_oracle_anchor": {
                "maximum_absolute_hidden_difference": time_zero_hidden_difference,
                "identical_decoding": time_zero_decoding_equal,
                "pass": time_zero_oracle_anchor_pass,
                "oracle_prototype_not_subject_to_this_identity_control": True,
            },
            "wrong_anchor_and_prototype_identity_failures": wrong_state_identity_failures,
            "wrong_anchor_and_prototype_differ_from_truth": (
                wrong_state_identity_failures == 0
            ),
            "branch_maximum_absolute_hidden_difference_to_native": (
                branch_max_hidden_difference_to_native
            ),
            "branch_maximum_absolute_logit_difference_to_native": (
                branch_max_logit_difference_to_native
            ),
            "state_dict_digest_before": before_digest,
            "state_dict_digest_after": after_digest,
            "state_dict_unchanged": before_digest == after_digest,
        },
        "dtype": {
            "model_operator_and_intervention_path": "torch.float32",
            "diagnostics_after_detach": "numpy.float64",
        },
    }


def _periodic_reset(
    condition: str,
    model: nn.Module,
    hidden: torch.Tensor,
    true_canonical: torch.Tensor,
    phi: torch.Tensor,
    projector: ProjectorBundle,
    prototypes: PrototypeBundle,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Apply one scheduled repair and return state plus selected visible label."""

    sentinel = torch.full_like(true_canonical, -1)
    metric = model.invariant_metric()
    anchors = model.state_anchors()
    if condition == "native":
        return hidden, sentinel
    if condition == "sham_scale":
        return checked_model_normalize(model, 7.0 * hidden, metric), sentinel
    if condition == "oracle_anchor":
        selected = phi[true_canonical]
        return anchors[selected], selected
    if condition == "self_anchor":
        selected = checked_decode_hidden(model, hidden).argmax(dim=-1)
        return anchors[selected], selected
    if condition == "nearest_anchor":
        selected = oriented_metric_selector(hidden, anchors, metric)
        return anchors[selected], selected
    if condition == "self_prototype":
        selected = oriented_metric_selector(hidden, prototypes.torch32, metric)
        return prototypes.torch32[selected], selected
    if condition == "anchor_projection":
        projected = hidden @ projector.torch32.transpose(0, 1)
        return checked_model_normalize(model, projected, metric), sentinel
    raise ValueError(f"unknown periodic condition: {condition}")


@dataclass
class PeriodicEventCounts:
    reset_events: int = 0
    selected_events: int = 0
    selector_correct: int = 0
    error_corrected: int = 0
    error_propagated: int = 0
    correct_damaged: int = 0
    correct_preserved: int = 0

    def add(self, other: "PeriodicEventCounts") -> None:
        for field in self.__dataclass_fields__:
            setattr(self, field, int(getattr(self, field)) + int(getattr(other, field)))


@dataclass(frozen=True)
class PeriodicTrace:
    hidden: torch.Tensor
    logits: torch.Tensor
    true_canonical: torch.Tensor
    elapsed_steps: int
    checkpoints: Mapping[int, tuple[torch.Tensor, torch.Tensor]]
    events: PeriodicEventCounts


@torch.inference_mode()
def periodic_evolve(
    model: nn.Module,
    hidden: torch.Tensor,
    encoded_codes: torch.Tensor,
    canonical_to_slot: np.ndarray,
    phi: torch.Tensor,
    canonical_maps: np.ndarray,
    true_canonical: torch.Tensor,
    word: Sequence[int],
    *,
    condition: str,
    cadence: int,
    projector: ProjectorBundle,
    prototypes: PrototypeBundle,
    elapsed_steps: int = 0,
    checkpoint_steps: Iterable[int] = (),
) -> PeriodicTrace:
    """Evolve one branch with a cadence that continues across prefix and suffix."""

    if cadence not in PERIODIC_CADENCES:
        raise ValueError("cadence is outside the frozen dose-response set")
    if condition not in PERIODIC_CONDITION_NAMES:
        raise ValueError("condition is outside the frozen periodic set")
    if hidden.dtype != torch.float32 or encoded_codes.dtype != torch.float32:
        raise TypeError("periodic model path must remain float32")
    state = checked_model_normalize(model, hidden, model.invariant_metric())
    truth = true_canonical.clone()
    rows = torch.arange(state.shape[0])
    codes = encoded_codes
    if codes.shape[0] == 1:
        codes = codes.expand(state.shape[0], -1, -1, -1)
    checkpoints: dict[int, tuple[torch.Tensor, torch.Tensor]] = {}
    checkpoint_set = {int(value) for value in checkpoint_steps}
    events = PeriodicEventCounts()
    current_step = int(elapsed_steps)
    for action_value in word:
        action = int(action_value)
        slot = int(canonical_to_slot[action])
        selected_code = codes[rows, slot]
        proposal = torch.bmm(selected_code, state.unsqueeze(-1)).squeeze(-1)
        state = checked_model_normalize(model, proposal, model.invariant_metric())
        truth = torch.from_numpy(
            canonical_maps[action, truth.detach().cpu().numpy()].astype(np.int64)
        ).long()
        current_step += 1
        if current_step % cadence == 0:
            before_prediction = checked_decode_hidden(model, state).argmax(dim=-1)
            true_visible = phi[truth]
            before_correct = before_prediction == true_visible
            state, selected_visible = _periodic_reset(
                condition, model, state, truth, phi, projector, prototypes
            )
            after_prediction = checked_decode_hidden(model, state).argmax(dim=-1)
            after_correct = after_prediction == true_visible
            events.reset_events += int(state.shape[0])
            selectable = selected_visible >= 0
            events.selected_events += int(torch.count_nonzero(selectable).item())
            events.selector_correct += int(
                torch.count_nonzero(selectable & (selected_visible == true_visible)).item()
            )
            events.error_corrected += int(
                torch.count_nonzero((~before_correct) & after_correct).item()
            )
            events.error_propagated += int(
                torch.count_nonzero((~before_correct) & (~after_correct)).item()
            )
            events.correct_damaged += int(
                torch.count_nonzero(before_correct & (~after_correct)).item()
            )
            events.correct_preserved += int(
                torch.count_nonzero(before_correct & after_correct).item()
            )
        if current_step in checkpoint_set:
            checkpoints[current_step] = (checked_decode_hidden(model, state), truth.clone())
    logits = checked_decode_hidden(model, state)
    if logits.dtype != torch.float32:
        raise TypeError("periodic decoder path left float32")
    return PeriodicTrace(
        hidden=state,
        logits=logits,
        true_canonical=truth,
        elapsed_steps=current_step,
        checkpoints=checkpoints,
        events=events,
    )


@dataclass(frozen=True)
class StackedPeriodicTrace:
    hidden: torch.Tensor
    logits: torch.Tensor
    true_canonical: torch.Tensor
    elapsed_steps: int
    checkpoints: Mapping[
        int, tuple[torch.Tensor, torch.Tensor, torch.Tensor]
    ]
    events: tuple[PeriodicEventCounts, ...]
    sham_control_by_cadence: Mapping[str, Mapping[str, float | int]]


def periodic_mode_layout() -> tuple[tuple[str, int], ...]:
    """Logical reporting layout (seven conditions by four cadences)."""

    return tuple(
        (condition, cadence)
        for condition in PERIODIC_CONDITION_NAMES
        for cadence in PERIODIC_CADENCES
    )


def periodic_repair_layout() -> tuple[tuple[str, int], ...]:
    """Physical prefix modes; native is supplied by the shared raw-prefix cache."""

    return tuple(
        (condition, cadence)
        for condition in PERIODIC_CONDITION_NAMES
        if condition != "native"
        for cadence in PERIODIC_CADENCES
    )


def periodic_suffix_physical_layout() -> tuple[tuple[str, int], ...]:
    """One cadence-independent native branch plus all repair modes."""

    return (("native", 0),) + periodic_repair_layout()


def _sum_periodic_events(
    first: PeriodicEventCounts, second: PeriodicEventCounts
) -> PeriodicEventCounts:
    return PeriodicEventCounts(
        **{
            field: int(getattr(first, field)) + int(getattr(second, field))
            for field in PeriodicEventCounts.__dataclass_fields__
        }
    )


def _empty_periodic_sham_control() -> dict[str, dict[str, float | int]]:
    return {
        str(cadence): {
            "maximum_absolute_hidden_difference": 0.0,
            "maximum_absolute_logit_difference": 0.0,
            "prediction_failures": 0,
            "prediction_cases": 0,
        }
        for cadence in PERIODIC_CADENCES
    }


def _periodic_sham_snapshot(
    model: nn.Module,
    hidden: torch.Tensor,
    layout: Sequence[tuple[str, int]],
    mode_batch_size: int,
) -> dict[str, dict[str, float | int]]:
    output = _empty_periodic_sham_control()
    native_modes = [
        index for index, (condition, _cadence) in enumerate(layout) if condition == "native"
    ]
    if not native_modes:
        return output
    for cadence in PERIODIC_CADENCES:
        native_index = (
            tuple(layout).index(("native", cadence))
            if ("native", cadence) in layout
            else native_modes[0]
        )
        sham_index = tuple(layout).index(("sham_scale", cadence))
        native_rows = slice(
            native_index * int(mode_batch_size),
            (native_index + 1) * int(mode_batch_size),
        )
        sham_rows = slice(
            sham_index * int(mode_batch_size),
            (sham_index + 1) * int(mode_batch_size),
        )
        native_hidden = hidden[native_rows]
        sham_hidden = hidden[sham_rows]
        native_logits = checked_decode_hidden(model, native_hidden)
        sham_logits = checked_decode_hidden(model, sham_hidden)
        output[str(cadence)] = {
            "maximum_absolute_hidden_difference": float(
                torch.max(torch.abs(native_hidden - sham_hidden)).item()
            ),
            "maximum_absolute_logit_difference": float(
                torch.max(torch.abs(native_logits - sham_logits)).item()
            ),
            "prediction_failures": int(
                torch.count_nonzero(
                    native_logits.argmax(dim=-1) != sham_logits.argmax(dim=-1)
                ).item()
            ),
            "prediction_cases": int(mode_batch_size),
        }
    return output


def _merge_periodic_sham_controls(
    first: Mapping[str, Mapping[str, float | int]],
    second: Mapping[str, Mapping[str, float | int]],
) -> dict[str, dict[str, float | int]]:
    output = _empty_periodic_sham_control()
    for cadence in PERIODIC_CADENCES:
        key = str(cadence)
        output[key] = {
            "maximum_absolute_hidden_difference": max(
                float(first[key]["maximum_absolute_hidden_difference"]),
                float(second[key]["maximum_absolute_hidden_difference"]),
            ),
            "maximum_absolute_logit_difference": max(
                float(first[key]["maximum_absolute_logit_difference"]),
                float(second[key]["maximum_absolute_logit_difference"]),
            ),
            "prediction_failures": int(first[key]["prediction_failures"])
            + int(second[key]["prediction_failures"]),
            "prediction_cases": int(first[key]["prediction_cases"])
            + int(second[key]["prediction_cases"]),
        }
    return output


def validate_periodic_sham_control(
    control: Mapping[str, Mapping[str, float | int]],
) -> bool:
    """Fail closed unless every frozen cadence has a finite, populated sham audit."""

    if set(control) != {str(value) for value in PERIODIC_CADENCES}:
        raise RuntimeError("periodic sham control cadence panel is incomplete")
    for cadence in PERIODIC_CADENCES:
        record = control[str(cadence)]
        hidden_difference = float(record["maximum_absolute_hidden_difference"])
        logit_difference = float(record["maximum_absolute_logit_difference"])
        prediction_failures = int(record["prediction_failures"])
        prediction_cases = int(record["prediction_cases"])
        if (
            not np.isfinite(hidden_difference)
            or not np.isfinite(logit_difference)
            or prediction_cases <= 0
            or hidden_difference > 1e-6
            or logit_difference > 1e-5
            or prediction_failures != 0
        ):
            raise RuntimeError("periodic sham-scale control failed")
    return True


@torch.inference_mode()
def _stacked_periodic_step(
    model: nn.Module,
    hidden: torch.Tensor,
    encoded_codes: torch.Tensor,
    canonical_to_slot: np.ndarray,
    phi: torch.Tensor,
    canonical_maps: np.ndarray,
    true_canonical: torch.Tensor,
    action: int,
    *,
    elapsed_steps: int,
    layout: Sequence[tuple[str, int]],
    mode_batch_size: int,
    projector: ProjectorBundle,
    prototypes: PrototypeBundle,
) -> tuple[torch.Tensor, torch.Tensor, tuple[PeriodicEventCounts, ...]]:
    """Advance every condition/cadence mode in one float32 recurrent batch."""

    total = len(layout) * int(mode_batch_size)
    if hidden.shape[0] != total or true_canonical.shape != (total,):
        raise ValueError("stacked periodic mode shape mismatch")
    codes = encoded_codes
    if codes.shape[0] == 1:
        codes = codes.expand(total, -1, -1, -1)
    rows = torch.arange(total)
    slot = int(canonical_to_slot[int(action)])
    proposal = torch.bmm(codes[rows, slot], hidden.unsqueeze(-1)).squeeze(-1)
    state = checked_model_normalize(model, proposal, model.invariant_metric())
    truth = torch.from_numpy(
        np.asarray(canonical_maps[int(action)], dtype=np.int64)
    ).long()[true_canonical]
    current_step = int(elapsed_steps) + 1
    state = state.clone()
    edge_events = [PeriodicEventCounts() for _ in layout]
    scheduled_modes = tuple(
        mode_index
        for mode_index, (condition, cadence) in enumerate(layout)
        if condition != "native" and current_step % int(cadence) == 0
    )
    if scheduled_modes:
        row_offsets = torch.arange(int(mode_batch_size), dtype=torch.long)
        scheduled_rows = (
            torch.tensor(scheduled_modes, dtype=torch.long)[:, None]
            * int(mode_batch_size)
            + row_offsets[None, :]
        ).reshape(-1)
        scheduled_state = state[scheduled_rows]
        scheduled_truth = truth[scheduled_rows]
        true_visible = phi[scheduled_truth]
        before_prediction = checked_decode_hidden(
            model, scheduled_state
        ).argmax(dim=-1)
        reset_state = scheduled_state.clone()
        selected_visible = torch.full_like(scheduled_truth, -1)
        for condition in PERIODIC_CONDITION_NAMES:
            local_modes = tuple(
                local_index
                for local_index, mode_index in enumerate(scheduled_modes)
                if layout[mode_index][0] == condition
            )
            if not local_modes:
                continue
            local_rows = (
                torch.tensor(local_modes, dtype=torch.long)[:, None]
                * int(mode_batch_size)
                + row_offsets[None, :]
            ).reshape(-1)
            condition_state, condition_selected = _periodic_reset(
                condition,
                model,
                scheduled_state[local_rows],
                scheduled_truth[local_rows],
                phi,
                projector,
                prototypes,
            )
            reset_state[local_rows] = condition_state
            selected_visible[local_rows] = condition_selected
        state[scheduled_rows] = reset_state
        after_prediction = checked_decode_hidden(model, reset_state).argmax(dim=-1)
        before_correct = (before_prediction == true_visible).reshape(
            len(scheduled_modes), int(mode_batch_size)
        )
        after_correct = (after_prediction == true_visible).reshape(
            len(scheduled_modes), int(mode_batch_size)
        )
        selected_panel = selected_visible.reshape(
            len(scheduled_modes), int(mode_batch_size)
        )
        true_visible_panel = true_visible.reshape(
            len(scheduled_modes), int(mode_batch_size)
        )
        selectable = selected_panel >= 0
        event_arrays = {
            "selected_events": selectable.sum(dim=1),
            "selector_correct": (
                selectable & (selected_panel == true_visible_panel)
            ).sum(dim=1),
            "error_corrected": ((~before_correct) & after_correct).sum(dim=1),
            "error_propagated": ((~before_correct) & (~after_correct)).sum(dim=1),
            "correct_damaged": (before_correct & (~after_correct)).sum(dim=1),
            "correct_preserved": (before_correct & after_correct).sum(dim=1),
        }
        event_numpy = {
            name: value.detach().cpu().numpy().astype(np.int64)
            for name, value in event_arrays.items()
        }
        for local_index, mode_index in enumerate(scheduled_modes):
            events = edge_events[mode_index]
            events.reset_events = int(mode_batch_size)
            for field_name, value in event_numpy.items():
                setattr(events, field_name, int(value[local_index]))
    return state, truth, tuple(edge_events)


@torch.inference_mode()
def periodic_evolve_stacked(
    model: nn.Module,
    hidden: torch.Tensor,
    encoded_codes: torch.Tensor,
    canonical_to_slot: np.ndarray,
    phi: torch.Tensor,
    canonical_maps: np.ndarray,
    true_canonical: torch.Tensor,
    word: Sequence[int],
    *,
    elapsed_steps: int,
    layout: Sequence[tuple[str, int]],
    mode_batch_size: int,
    projector: ProjectorBundle,
    prototypes: PrototypeBundle,
    checkpoint_steps: Iterable[int] = (),
) -> StackedPeriodicTrace:
    state = checked_model_normalize(model, hidden, model.invariant_metric())
    truth = true_canonical.clone()
    elapsed = int(elapsed_steps)
    cumulative = [PeriodicEventCounts() for _ in layout]
    sham_control = _empty_periodic_sham_control()
    checkpoints: dict[
        int, tuple[torch.Tensor, torch.Tensor, torch.Tensor]
    ] = {}
    checkpoint_set = {int(value) for value in checkpoint_steps}
    has_native_sham_reference = any(condition == "native" for condition, _ in layout)
    for action in word:
        state, truth, edge = _stacked_periodic_step(
            model,
            state,
            encoded_codes,
            canonical_to_slot,
            phi,
            canonical_maps,
            truth,
            int(action),
            elapsed_steps=elapsed,
            layout=layout,
            mode_batch_size=mode_batch_size,
            projector=projector,
            prototypes=prototypes,
        )
        elapsed += 1
        for previous, addition in zip(cumulative, edge):
            previous.add(addition)
        if has_native_sham_reference:
            sham_control = _merge_periodic_sham_controls(
                sham_control,
                _periodic_sham_snapshot(model, state, layout, mode_batch_size),
            )
        if elapsed in checkpoint_set:
            checkpoints[elapsed] = (
                state.clone(),
                checked_decode_hidden(model, state),
                truth.clone(),
            )
    logits = checked_decode_hidden(model, state)
    if logits.dtype != torch.float32 or state.dtype != torch.float32:
        raise TypeError("stacked periodic path left float32")
    return StackedPeriodicTrace(
        hidden=state,
        logits=logits,
        true_canonical=truth,
        elapsed_steps=elapsed,
        checkpoints=checkpoints,
        events=tuple(cumulative),
        sham_control_by_cadence=sham_control,
    )


@torch.inference_mode()
def periodic_suffix_tree_stacked(
    model: nn.Module,
    prefix: StackedPeriodicTrace,
    encoded_codes: torch.Tensor,
    canonical_to_slot: np.ndarray,
    phi: torch.Tensor,
    canonical_maps: np.ndarray,
    words: Sequence[tuple[int, ...]],
    *,
    layout: Sequence[tuple[str, int]],
    mode_batch_size: int,
    projector: ProjectorBundle,
    prototypes: PrototypeBundle,
) -> dict[tuple[int, ...], StackedPeriodicTrace]:
    """Continue all modes through one absolute-clock, prefix-closed suffix trie."""

    ordered = tuple(tuple(int(value) for value in word) for word in words)
    word_set = set(ordered)
    if () not in word_set or any(word[:-1] not in word_set for word in ordered if word):
        raise ValueError("periodic suffix tree requires a prefix-closed word set")
    zero_events = tuple(PeriodicEventCounts() for _ in layout)
    zero_sham = _empty_periodic_sham_control()
    output: dict[tuple[int, ...], StackedPeriodicTrace] = {
        (): StackedPeriodicTrace(
            hidden=prefix.hidden,
            logits=prefix.logits,
            true_canonical=prefix.true_canonical,
            elapsed_steps=prefix.elapsed_steps,
            checkpoints={},
            events=zero_events,
            sham_control_by_cadence=zero_sham,
        )
    }
    for word in ordered:
        if not word:
            continue
        parent = output[word[:-1]]
        state, truth, edge = _stacked_periodic_step(
            model,
            parent.hidden,
            encoded_codes,
            canonical_to_slot,
            phi,
            canonical_maps,
            parent.true_canonical,
            word[-1],
            elapsed_steps=parent.elapsed_steps,
            layout=layout,
            mode_batch_size=mode_batch_size,
            projector=projector,
            prototypes=prototypes,
        )
        cumulative = tuple(
            _sum_periodic_events(previous, addition)
            for previous, addition in zip(parent.events, edge)
        )
        sham_control = _merge_periodic_sham_controls(
            parent.sham_control_by_cadence,
            _periodic_sham_snapshot(model, state, layout, mode_batch_size),
        )
        output[word] = StackedPeriodicTrace(
            hidden=state,
            logits=checked_decode_hidden(model, state),
            true_canonical=truth,
            elapsed_steps=parent.elapsed_steps + 1,
            checkpoints={},
            events=cumulative,
            sham_control_by_cadence=sham_control,
        )
    return output


@torch.inference_mode()
def evaluate_periodic_model(
    model: nn.Module,
    context_bank: ContextBank,
    path_bank: PathPairBank,
    continuation_bank: ContinuationBank,
    canonical_maps: np.ndarray,
    prototypes: PrototypeBundle,
    encoded_contexts: Sequence[torch.Tensor] | None = None,
    native_prefix_cache: Mapping[
        tuple[int, int, int], NativePrefixCacheEntry
    ]
    | None = None,
) -> dict[str, Any]:
    """Evaluate the frozen periodic repair dose-response on depth-64/65 paths."""

    model = model.to(device="cpu").eval()
    verify_float32_model(model)
    projector = construct_anchor_projector(model)
    periodic_bands = (8, 64)
    selected_pairs = [
        (pair_index, pair)
        for pair_index, pair in enumerate(path_bank.pairs)
        if pair.nominal_band in periodic_bands
    ]
    if len(selected_pairs) != 2 * 8 * PAIRS_PER_ENDPOINT_BAND:
        raise RuntimeError("band-8 and band-64 periodic path panels are incomplete")
    shape = (
        len(PERIODIC_CONDITION_NAMES),
        len(PERIODIC_CADENCES),
        len(continuation_bank.words),
        8,
    )
    accumulators = {
        f"band_{band}_{'odd' if parity else 'even'}": TensorAccumulator(
            shape,
            axes=(
                "condition",
                "cadence",
                "continuation_word",
                "canonical_state_at_cut",
            ),
        )
        for band in periodic_bands
        for parity in (0, 1)
    }
    prefix_steps = (8, 16, 32)
    prefix_correct = np.zeros(
        (
            len(PERIODIC_CONDITION_NAMES),
            len(PERIODIC_CADENCES),
            len(periodic_bands),
            2,
            len(prefix_steps) + 1,
        ),
        dtype=np.int64,
    )
    prefix_total = np.zeros_like(prefix_correct)
    event_totals = {
        condition: {str(cadence): PeriodicEventCounts() for cadence in PERIODIC_CADENCES}
        for condition in PERIODIC_CONDITION_NAMES
    }
    periodic_sham_control = _empty_periodic_sham_control()
    starts_np = np.arange(8, dtype=np.int64)
    starts = torch.from_numpy(starts_np).long()
    logical_layout = periodic_mode_layout()
    repair_layout = periodic_repair_layout()
    repair_layout_index = {mode: index for index, mode in enumerate(repair_layout)}
    suffix_layout = periodic_suffix_physical_layout()
    suffix_layout_index = {mode: index for index, mode in enumerate(suffix_layout)}
    periodic_context_correct = np.zeros(
        (
            len(PERIODIC_CONDITION_NAMES),
            len(PERIODIC_CADENCES),
            len(periodic_bands),
            2,
            context_bank.tables.shape[0],
        ),
        dtype=np.float64,
    )
    periodic_context_total = np.zeros_like(periodic_context_correct, dtype=np.int64)
    branch_max_hidden_difference_to_native = np.zeros(
        (len(PERIODIC_CONDITION_NAMES), len(PERIODIC_CADENCES)),
        dtype=np.float64,
    )
    branch_max_logit_difference_to_native = np.zeros_like(
        branch_max_hidden_difference_to_native
    )
    branch_comparison_cases = np.zeros_like(
        branch_max_hidden_difference_to_native, dtype=np.int64
    )
    metric = model.invariant_metric()

    def record_native_discrepancy(
        condition_index: int,
        cadence_index: int,
        native_hidden: torch.Tensor,
        candidate_hidden: torch.Tensor,
        native_logits: torch.Tensor,
        candidate_logits: torch.Tensor,
    ) -> None:
        tensors = (native_hidden, candidate_hidden, native_logits, candidate_logits)
        if any(tensor.dtype != torch.float32 for tensor in tensors):
            raise TypeError("periodic exact-discrepancy operands must be float32")
        if any(not bool(torch.isfinite(tensor).all()) for tensor in tensors):
            raise FloatingPointError("periodic discrepancy operand is nonfinite")
        if native_hidden.shape != candidate_hidden.shape:
            raise ValueError("periodic hidden discrepancy shapes disagree")
        if native_logits.shape != candidate_logits.shape:
            raise ValueError("periodic logit discrepancy shapes disagree")
        branch_max_hidden_difference_to_native[condition_index, cadence_index] = max(
            branch_max_hidden_difference_to_native[condition_index, cadence_index],
            float(torch.max(torch.abs(candidate_hidden - native_hidden)).item()),
        )
        branch_max_logit_difference_to_native[condition_index, cadence_index] = max(
            branch_max_logit_difference_to_native[condition_index, cadence_index],
            float(torch.max(torch.abs(candidate_logits - native_logits)).item()),
        )
        branch_comparison_cases[condition_index, cadence_index] += int(
            native_hidden.shape[0]
        )

    def record_native_discrepancy_panel(
        condition_indices: np.ndarray,
        cadence_indices: np.ndarray,
        native_hidden: torch.Tensor,
        candidate_hidden: torch.Tensor,
        native_logits: torch.Tensor,
        candidate_logits: torch.Tensor,
    ) -> None:
        """Update all logical modes from ``[mode, ..., feature]`` tensors."""

        tensors = (native_hidden, candidate_hidden, native_logits, candidate_logits)
        if any(tensor.dtype != torch.float32 for tensor in tensors):
            raise TypeError("periodic exact-discrepancy operands must be float32")
        if any(not bool(torch.isfinite(tensor).all()) for tensor in tensors):
            raise FloatingPointError("periodic discrepancy operand is nonfinite")
        if native_hidden.shape != candidate_hidden.shape:
            raise ValueError("periodic hidden discrepancy panel shapes disagree")
        if native_logits.shape != candidate_logits.shape:
            raise ValueError("periodic logit discrepancy panel shapes disagree")
        if native_hidden.ndim < 3 or native_logits.ndim < 3:
            raise ValueError("periodic discrepancy panel requires a logical-mode axis")
        mode_count = int(native_hidden.shape[0])
        conditions = np.asarray(condition_indices, dtype=np.int64).reshape(-1)
        cadences = np.asarray(cadence_indices, dtype=np.int64).reshape(-1)
        if conditions.size != mode_count or cadences.size != mode_count:
            raise ValueError("periodic discrepancy logical index width disagrees")
        hidden_maximum = (
            torch.abs(candidate_hidden - native_hidden)
            .reshape(mode_count, -1)
            .amax(dim=1)
            .detach()
            .cpu()
            .numpy()
            .astype(np.float64)
        )
        logit_maximum = (
            torch.abs(candidate_logits - native_logits)
            .reshape(mode_count, -1)
            .amax(dim=1)
            .detach()
            .cpu()
            .numpy()
            .astype(np.float64)
        )
        comparison_count = int(np.prod(native_hidden.shape[1:-1], dtype=np.int64))
        for mode_index, (condition_index, cadence_index) in enumerate(
            zip(conditions, cadences)
        ):
            branch_max_hidden_difference_to_native[
                condition_index, cadence_index
            ] = max(
                branch_max_hidden_difference_to_native[
                    condition_index, cadence_index
                ],
                float(hidden_maximum[mode_index]),
            )
            branch_max_logit_difference_to_native[
                condition_index, cadence_index
            ] = max(
                branch_max_logit_difference_to_native[
                    condition_index, cadence_index
                ],
                float(logit_maximum[mode_index]),
            )
            branch_comparison_cases[condition_index, cadence_index] += comparison_count
    if encoded_contexts is not None and len(encoded_contexts) != context_bank.tables.shape[0]:
        raise ValueError("encoded evaluation-context cache has the wrong length")
    expected_native_cache_entries = (
        context_bank.tables.shape[0] * len(selected_pairs) * 2
    )
    if (
        native_prefix_cache is not None
        and len(native_prefix_cache) != expected_native_cache_entries
    ):
        raise RuntimeError("shared native prefix cache has the wrong entry count")

    for context_index in range(context_bank.tables.shape[0]):
        phi_np = context_bank.phi[context_index]
        phi = torch.from_numpy(phi_np).long()
        slots = context_bank.canonical_to_slot[context_index]
        encoded = (
            encoded_contexts[context_index]
            if encoded_contexts is not None
            else encode_context_once(model, context_bank.tables[context_index])
        )
        if encoded.dtype != torch.float32 or not bool(torch.isfinite(encoded).all()):
            raise FloatingPointError("cached encoded context is not finite float32")
        initial = model.initial_hidden(torch.from_numpy(phi_np[starts_np]).long())
        for pair_index, pair in selected_pairs:
            band_position = periodic_bands.index(pair.nominal_band)
            parity = int(pair.endpoint_parity)
            stratum_name = (
                f"band_{pair.nominal_band}_{'odd' if parity else 'even'}"
            )
            for member_index, word in enumerate((pair.word_a, pair.word_b)):
                cache_key = (context_index, pair_index, member_index)
                if native_prefix_cache is not None:
                    if cache_key not in native_prefix_cache:
                        raise RuntimeError("shared native prefix cache is incomplete")
                    native_prefix = native_prefix_cache[cache_key]
                else:
                    native_trace = run_word_batch(
                        model,
                        encoded,
                        slots,
                        phi_np,
                        starts_np,
                        [word] * 8,
                    )
                    truth_at_step = starts_np.copy()
                    native_checkpoints: dict[
                        int, tuple[torch.Tensor, torch.Tensor, torch.Tensor]
                    ] = {}
                    for step, action in enumerate(word, start=1):
                        truth_at_step = canonical_maps[int(action), truth_at_step]
                        if step in prefix_steps:
                            checkpoint_hidden = native_trace.hidden[step]
                            native_checkpoints[step] = (
                                checkpoint_hidden,
                                checked_decode_hidden(model, checkpoint_hidden),
                                torch.from_numpy(
                                    truth_at_step.astype(np.int64, copy=True)
                                ).long(),
                            )
                    native_prefix = NativePrefixCacheEntry(
                        hidden=native_trace.hidden[-1],
                        logits=native_trace.logits,
                        true_canonical=torch.from_numpy(
                            truth_at_step.astype(np.int64, copy=True)
                        ).long(),
                        checkpoints=native_checkpoints,
                        trajectory_hidden=torch.stack(
                            tuple(native_trace.hidden[1:]), dim=0
                        ),
                    )

                stacked_initial = initial.repeat((len(repair_layout), 1))
                stacked_truth = starts.repeat(len(repair_layout))
                prefix = periodic_evolve_stacked(
                    model,
                    stacked_initial,
                    encoded,
                    slots,
                    phi,
                    canonical_maps,
                    stacked_truth,
                    word,
                    elapsed_steps=0,
                    layout=repair_layout,
                    mode_batch_size=8,
                    projector=projector,
                    prototypes=prototypes,
                    checkpoint_steps=tuple(range(1, len(word) + 1)),
                )
                suffix_prefix = StackedPeriodicTrace(
                    hidden=torch.cat((native_prefix.hidden, prefix.hidden), dim=0),
                    logits=torch.cat((native_prefix.logits, prefix.logits), dim=0),
                    true_canonical=torch.cat(
                        (native_prefix.true_canonical, prefix.true_canonical), dim=0
                    ),
                    elapsed_steps=len(word),
                    checkpoints={},
                    events=tuple(PeriodicEventCounts() for _ in suffix_layout),
                    sham_control_by_cadence=_empty_periodic_sham_control(),
                )
                suffix_tree = periodic_suffix_tree_stacked(
                    model,
                    suffix_prefix,
                    encoded,
                    slots,
                    phi,
                    canonical_maps,
                    continuation_bank.words,
                    layout=suffix_layout,
                    mode_batch_size=8,
                    projector=projector,
                    prototypes=prototypes,
                )

                prefix_sham_control = _empty_periodic_sham_control()
                native_trajectory_hidden = native_prefix.trajectory_hidden
                if native_trajectory_hidden.shape != (len(word), 8, 12):
                    raise RuntimeError("packed native prefix trajectory has wrong shape")
                native_trajectory_logits = checked_decode_hidden(
                    model, native_trajectory_hidden.reshape(-1, 12)
                ).reshape(len(word), 8, 8)
                for cadence in PERIODIC_CADENCES:
                    repair_mode = repair_layout_index[("sham_scale", cadence)]
                    repair_rows = slice(repair_mode * 8, (repair_mode + 1) * 8)
                    comparisons: list[
                        tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]
                    ] = []
                    for step in range(1, len(word) + 1):
                        native_hidden = native_trajectory_hidden[step - 1]
                        native_logits = native_trajectory_logits[step - 1]
                        repair_hidden_all, repair_logits_all, _ = prefix.checkpoints[step]
                        comparisons.append(
                            (
                                native_hidden,
                                repair_hidden_all[repair_rows],
                                native_logits,
                                repair_logits_all[repair_rows],
                            )
                        )
                    prefix_sham_control[str(cadence)] = {
                        "maximum_absolute_hidden_difference": max(
                            float(torch.max(torch.abs(left - right)).item())
                            for left, right, _left_logits, _right_logits in comparisons
                        ),
                        "maximum_absolute_logit_difference": max(
                            float(
                                torch.max(
                                    torch.abs(left_logits - right_logits)
                                ).item()
                            )
                            for _left, _right, left_logits, right_logits in comparisons
                        ),
                        "prediction_failures": sum(
                            int(
                                torch.count_nonzero(
                                    left_logits.argmax(dim=-1)
                                    != right_logits.argmax(dim=-1)
                                ).item()
                            )
                            for _left, _right, left_logits, right_logits in comparisons
                        ),
                        "prediction_cases": 8 * len(comparisons),
                    }
                for continuation in continuation_bank.words:
                    trajectory_sham = _merge_periodic_sham_controls(
                        prefix_sham_control,
                        suffix_tree[continuation].sham_control_by_cadence,
                    )
                    periodic_sham_control = _merge_periodic_sham_controls(
                        periodic_sham_control, trajectory_sham
                    )

                condition_indices = np.asarray(
                    [PERIODIC_CONDITION_NAMES.index(item[0]) for item in logical_layout],
                    dtype=np.int64,
                )
                cadence_indices = np.asarray(
                    [PERIODIC_CADENCES.index(item[1]) for item in logical_layout],
                    dtype=np.int64,
                )
                suffix_mode_indices = np.asarray(
                    [
                        suffix_layout_index[("native", 0)]
                        if condition == "native"
                        else suffix_layout_index[(condition, cadence)]
                        for condition, cadence in logical_layout
                    ],
                    dtype=np.int64,
                )

                def logical_prefix_panel(
                    native_value: torch.Tensor,
                    repaired_value: torch.Tensor,
                ) -> torch.Tensor:
                    repaired = repaired_value.reshape(len(repair_layout), 8, *repaired_value.shape[1:])
                    return torch.stack(
                        tuple(
                            native_value
                            if condition == "native"
                            else repaired[repair_layout_index[(condition, cadence)]]
                            for condition, cadence in logical_layout
                        ),
                        dim=0,
                    )

                # Prefix checkpoints keep their prespecified reporting cells, but
                # all 28 logical modes are compared and counted in one tensor pass.
                for checkpoint_index, step in enumerate(prefix_steps):
                    if step > len(word):
                        continue
                    native_checkpoint_hidden, native_checkpoint_logits, native_truth = (
                        native_prefix.checkpoints[step]
                    )
                    all_hidden, all_logits, all_truth = prefix.checkpoints[step]
                    hidden_panel = logical_prefix_panel(
                        native_checkpoint_hidden, all_hidden
                    )
                    logits_panel = logical_prefix_panel(
                        native_checkpoint_logits, all_logits
                    )
                    truth_panel = logical_prefix_panel(native_truth, all_truth)
                    native_hidden_panel = native_checkpoint_hidden[None].expand_as(
                        hidden_panel
                    )
                    native_logits_panel = native_checkpoint_logits[None].expand_as(
                        logits_panel
                    )
                    record_native_discrepancy_panel(
                        condition_indices,
                        cadence_indices,
                        native_hidden_panel,
                        hidden_panel,
                        native_logits_panel,
                        logits_panel,
                    )
                    correct = (
                        logits_panel.argmax(dim=-1) == phi[truth_panel]
                    ).sum(dim=1).detach().cpu().numpy().astype(np.int64)
                    prefix_correct[
                        condition_indices,
                        cadence_indices,
                        band_position,
                        parity,
                        checkpoint_index,
                    ] += correct
                    prefix_total[
                        condition_indices,
                        cadence_indices,
                        band_position,
                        parity,
                        checkpoint_index,
                    ] += 8

                prefix_hidden_panel = logical_prefix_panel(
                    native_prefix.hidden, prefix.hidden
                )
                prefix_logits_panel = logical_prefix_panel(
                    native_prefix.logits, prefix.logits
                )
                prefix_truth_panel = logical_prefix_panel(
                    native_prefix.true_canonical, prefix.true_canonical
                )
                terminal_correct = (
                    prefix_logits_panel.argmax(dim=-1) == phi[prefix_truth_panel]
                ).sum(dim=1).detach().cpu().numpy().astype(np.int64)
                prefix_correct[
                    condition_indices,
                    cadence_indices,
                    band_position,
                    parity,
                    len(prefix_steps),
                ] += terminal_correct
                prefix_total[
                    condition_indices,
                    cadence_indices,
                    band_position,
                    parity,
                    len(prefix_steps),
                ] += 8
                record_native_discrepancy_panel(
                    condition_indices,
                    cadence_indices,
                    native_prefix.hidden[None].expand_as(prefix_hidden_panel),
                    prefix_hidden_panel,
                    native_prefix.logits[None].expand_as(prefix_logits_panel),
                    prefix_logits_panel,
                )

                continuation_words = tuple(continuation_bank.words)
                continuation_count = len(continuation_words)
                physical_hidden = torch.stack(
                    tuple(suffix_tree[item].hidden for item in continuation_words),
                    dim=0,
                ).reshape(continuation_count, len(suffix_layout), 8, 12)
                physical_logits = torch.stack(
                    tuple(suffix_tree[item].logits for item in continuation_words),
                    dim=0,
                ).reshape(continuation_count, len(suffix_layout), 8, 8)
                physical_truth = torch.stack(
                    tuple(suffix_tree[item].true_canonical for item in continuation_words),
                    dim=0,
                ).reshape(continuation_count, len(suffix_layout), 8)
                candidate_hidden = physical_hidden[:, suffix_mode_indices].permute(
                    1, 0, 2, 3
                )
                candidate_logits = physical_logits[:, suffix_mode_indices].permute(
                    1, 0, 2, 3
                )
                candidate_truth = physical_truth[:, suffix_mode_indices].permute(1, 0, 2)
                native_hidden = physical_hidden[:, 0][None].expand_as(candidate_hidden)
                native_logits = physical_logits[:, 0][None].expand_as(candidate_logits)
                record_native_discrepancy_panel(
                    condition_indices,
                    cadence_indices,
                    native_hidden,
                    candidate_hidden,
                    native_logits,
                    candidate_logits,
                )
                metrics_flat = paired_future_diagnostics(
                    native_logits.reshape(-1, 8),
                    candidate_logits.reshape(-1, 8),
                    native_hidden.reshape(-1, 12),
                    candidate_hidden.reshape(-1, 12),
                    phi[candidate_truth].reshape(-1),
                    metric,
                )
                metrics_panel = {
                    name: value.reshape(
                        len(logical_layout), continuation_count, 8
                    )
                    for name, value in metrics_flat.items()
                }
                accumulators[stratum_name].add_dense_panel(
                    condition_indices,
                    cadence_indices,
                    np.arange(continuation_count, dtype=np.int64),
                    prefix_truth_panel.detach().cpu().numpy(),
                    metrics_panel,
                )
                accuracy = metrics_panel["accuracy"]
                finite_accuracy = np.isfinite(accuracy)
                periodic_context_correct[
                    condition_indices,
                    cadence_indices,
                    band_position,
                    parity,
                    context_index,
                ] += np.sum(
                    np.where(finite_accuracy, accuracy, 0.0), axis=(1, 2)
                )
                periodic_context_total[
                    condition_indices,
                    cadence_indices,
                    band_position,
                    parity,
                    context_index,
                ] += np.sum(finite_accuracy, axis=(1, 2), dtype=np.int64)

                # Event fields are integer counts.  Algebraically aggregating the
                # repeated prefix contribution is exactly the former nested loop.
                for mode_index, (condition, cadence) in enumerate(logical_layout):
                    if condition == "native":
                        prefix_mode_events = PeriodicEventCounts()
                    else:
                        prefix_mode_events = prefix.events[
                            repair_layout_index[(condition, cadence)]
                        ]
                    suffix_mode_index = int(suffix_mode_indices[mode_index])
                    addition = PeriodicEventCounts()
                    for field_name in PeriodicEventCounts.__dataclass_fields__:
                        setattr(
                            addition,
                            field_name,
                            continuation_count
                            * int(getattr(prefix_mode_events, field_name))
                            + sum(
                                int(
                                    getattr(
                                        suffix_tree[continuation].events[
                                            suffix_mode_index
                                        ],
                                        field_name,
                                    )
                                )
                                for continuation in continuation_words
                            ),
                        )
                    event_totals[condition][str(cadence)].add(addition)

    with np.errstate(invalid="ignore", divide="ignore"):
        prefix_accuracy = prefix_correct / prefix_total
    periodic_sham_pass = validate_periodic_sham_control(periodic_sham_control)
    if (
        not np.isfinite(branch_max_hidden_difference_to_native).all()
        or not np.isfinite(branch_max_logit_difference_to_native).all()
        or not np.all(branch_comparison_cases > 0)
    ):
        raise RuntimeError("periodic discrepancy audit is incomplete or nonfinite")

    primary_cadence_index = PERIODIC_CADENCES.index(4)
    periodic_behavioral_gates: dict[str, Any] = {}

    def periodic_accuracy_summary(
        condition_index: int, band_position: int, parity: int | None
    ) -> dict[str, Any]:
        if parity is None:
            numerator = np.sum(
                periodic_context_correct[
                    condition_index, primary_cadence_index, band_position
                ],
                axis=0,
            )
            denominator = np.sum(
                periodic_context_total[
                    condition_index, primary_cadence_index, band_position
                ],
                axis=0,
            )
        else:
            numerator = periodic_context_correct[
                condition_index,
                primary_cadence_index,
                band_position,
                int(parity),
            ]
            denominator = periodic_context_total[
                condition_index,
                primary_cadence_index,
                band_position,
                int(parity),
            ]
        return _context_ratio_summary(numerator, denominator)

    native_condition_index = PERIODIC_CONDITION_NAMES.index("native")
    deep_position = periodic_bands.index(64)
    shallow_position = periodic_bands.index(8)
    for condition_index, condition in enumerate(PERIODIC_CONDITION_NAMES):
        deep_records: dict[str, Any] = {}
        deep_pass = True
        for label, parity in (("pooled", None), ("even", 0), ("odd", 1)):
            candidate = periodic_accuracy_summary(
                condition_index, deep_position, parity
            )
            native = periodic_accuracy_summary(
                native_condition_index, deep_position, parity
            )
            candidate_accuracy = _summary_value(candidate)
            native_accuracy = _summary_value(native)
            native_error = 1.0 - native_accuracy
            damage = native_accuracy - candidate_accuracy
            if native_error < 0.01:
                relative_error_reduction: float | None = None
                reduction_rule = "low_native_error_accuracy_and_no_degradation"
                reduction_pass = bool(
                    candidate_accuracy >= 0.99 and damage <= 0.01
                )
            else:
                relative_error_reduction = (
                    (1.0 - native_accuracy) - (1.0 - candidate_accuracy)
                ) / native_error
                reduction_rule = "relative_error_reduction_at_least_0.50"
                reduction_pass = bool(relative_error_reduction >= 0.50)
            stratum_pass = bool(
                candidate["all_context_denominators_positive"]
                and native["all_context_denominators_positive"]
                and candidate_accuracy >= 0.95
                and reduction_pass
            )
            deep_pass = bool(deep_pass and stratum_pass)
            deep_records[label] = {
                "candidate_accuracy": candidate,
                "native_accuracy": native,
                "native_error": native_error,
                "absolute_accuracy_damage": damage,
                "relative_error_reduction": relative_error_reduction,
                "reduction_rule": reduction_rule,
                "reduction_pass": reduction_pass,
                "pass": stratum_pass,
            }
        shallow_records: dict[str, Any] = {}
        shallow_pass = True
        for label, parity in (("pooled", None), ("even", 0), ("odd", 1)):
            candidate = periodic_accuracy_summary(
                condition_index, shallow_position, parity
            )
            native = periodic_accuracy_summary(
                native_condition_index, shallow_position, parity
            )
            damage = _summary_value(native) - _summary_value(candidate)
            stratum_pass = bool(
                candidate["all_context_denominators_positive"]
                and native["all_context_denominators_positive"]
                and damage <= 0.01
            )
            shallow_pass = bool(shallow_pass and stratum_pass)
            shallow_records[label] = {
                "candidate_accuracy": candidate,
                "native_accuracy": native,
                "absolute_accuracy_damage": damage,
                "pass": stratum_pass,
            }
        periodic_behavioral_gates[condition] = {
            "primary_cadence": 4,
            "band_64_full_W4": deep_records,
            "band_8_full_W4_damage_control": shallow_records,
            "behavioral_pass": bool(deep_pass and shallow_pass),
            "semantic_retraction_label_eligible": condition
            not in ("native", "sham_scale", "oracle_anchor", "anchor_projection"),
            "projection_label_only": condition == "anchor_projection",
            "oracle_is_teacher_forced_upper_bound": condition == "oracle_anchor",
        }
    return {
        "conditions": list(PERIODIC_CONDITION_NAMES),
        "cadences": list(PERIODIC_CADENCES),
        "continuation_words": [list(word) for word in continuation_bank.words],
        "future_by_band_and_parity": {
            name: accumulator.serialize()
            for name, accumulator in accumulators.items()
        },
        "context_accuracy_axes": [
            "condition",
            "cadence",
            "nominal_band",
            "endpoint_parity",
            "context",
        ],
        "context_accuracy_correct": periodic_context_correct.tolist(),
        "context_accuracy_total": periodic_context_total.tolist(),
        "fixed_behavioral_gate_inputs": periodic_behavioral_gates,
        "prefix_accuracy_axes": [
            "condition",
            "cadence",
            "nominal_band",
            "endpoint_parity",
            "checkpoint",
        ],
        "nominal_bands": list(periodic_bands),
        "endpoint_parity_labels": ["even", "odd"],
        "prefix_checkpoints": [8, 16, 32, "actual_terminal"],
        "named_checkpoints_only_when_reached": True,
        "prefix_correct": prefix_correct.tolist(),
        "prefix_total": prefix_total.tolist(),
        "prefix_accuracy": _json_safe_array(prefix_accuracy),
        "events": {
            condition: {
                cadence: asdict(counts) for cadence, counts in by_cadence.items()
            }
            for condition, by_cadence in event_totals.items()
        },
        "event_counting_unit": (
            "logical context x path-member x canonical-start x W4-word trajectory; "
            "each record includes prefix plus that suffix path"
        ),
        "periodic_sham_scale_control": {
            "by_cadence": periodic_sham_control,
            "prefix_native_reference_storage": (
                "one packed float32 [step,start,hidden] tensor per path member"
            ),
            "every_prefix_and_suffix_step_compared": True,
            "hidden_absolute_tolerance": 1e-6,
            "logit_absolute_tolerance": 1e-5,
            "requires_identical_predictions": True,
            "pass": periodic_sham_pass,
        },
        "native_discrepancy_control": {
            "axes": ["condition", "cadence"],
            "maximum_absolute_normalized_hidden_difference": (
                branch_max_hidden_difference_to_native.tolist()
            ),
            "maximum_absolute_logit_difference": (
                branch_max_logit_difference_to_native.tolist()
            ),
            "comparison_cases": branch_comparison_cases.tolist(),
            "all_cells_populated_and_finite": True,
        },
        "primary_cadence": 4,
        "absolute_clock": {
            "first_prefix_action_is_step_one": True,
            "suffix_phase_restarts": False,
            "unscheduled_terminal_reset": False,
            "K1_both_exact_lengths_64_and_65_end_post_reset": True,
            "K4_K8_K16_length64_post_reset_length65_one_raw_step_after_reset": True,
        },
        "oracle_is_upper_bound_not_autonomous": True,
        "dtype": {
            "model_operator_reset_and_decoder_path": "torch.float32",
            "diagnostics_after_detach": "numpy.float64",
        },
    }


def compile_anchor_action(
    anchors: np.ndarray,
    visible_map: np.ndarray,
) -> np.ndarray:
    """Compile a full-space action that permutes anchors and fixes the complement."""

    anchors64 = np.asarray(anchors, dtype=np.float64)
    if anchors64.ndim != 2 or anchors64.shape[1] != 8:
        raise ValueError("anchors must have shape (hidden_dim, 8)")
    if np.linalg.matrix_rank(anchors64) != 8:
        raise RuntimeError("anchor compiler requires eight independent columns")
    inverse = np.linalg.pinv(anchors64, rcond=1e-12)
    projector = anchors64 @ inverse
    permutation = np.zeros((8, 8), dtype=np.float64)
    permutation[np.asarray(visible_map, dtype=np.int64), np.arange(8)] = 1.0
    return anchors64 @ permutation @ inverse + np.eye(anchors64.shape[0]) - projector


class ExactCompiledModel(nn.Module):
    """Float32, table-conditioned exact D4 action used only as a positive control."""

    def __init__(self, hidden_dim: int = 12) -> None:
        super().__init__()
        if hidden_dim < 8:
            raise ValueError("hidden_dim must be at least eight")
        anchors = torch.zeros((8, hidden_dim), dtype=torch.float32)
        anchors[:, :8] = torch.eye(8, dtype=torch.float32)
        self.register_buffer("_anchors", anchors)
        self.register_buffer("_metric", torch.eye(hidden_dim, dtype=torch.float32))
        self.decoder = nn.Linear(hidden_dim, 8, bias=False)
        with torch.no_grad():
            self.decoder.weight.zero_()
            self.decoder.weight[:, :8] = torch.eye(8, dtype=torch.float32)
        self.decoder.weight.requires_grad_(False)

    def invariant_metric(self) -> torch.Tensor:
        return self._metric

    def state_anchors(self) -> torch.Tensor:
        return self._anchors

    def normalize_hidden(
        self, hidden: torch.Tensor, metric: torch.Tensor | None = None
    ) -> torch.Tensor:
        if metric is None:
            metric = self._metric
        squared = torch.einsum("...i,ij,...j->...", hidden, metric, hidden)
        if bool((squared <= 0.0).any()):
            raise FloatingPointError("cannot normalize a zero control state")
        return hidden / torch.sqrt(squared).unsqueeze(-1)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return self._anchors[start]

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.decoder(hidden)

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        if tables.dtype != torch.float32:
            raise TypeError("exact-control tables must be float32")
        maps = tables.argmax(dim=-1)
        batch, slots = maps.shape[:2]
        hidden_dim = self._anchors.shape[1]
        output = torch.empty(
            (batch, slots, hidden_dim, hidden_dim), dtype=torch.float32
        )
        anchor_matrix = self._anchors.transpose(0, 1).detach().cpu().numpy()
        for batch_index in range(batch):
            for slot in range(slots):
                compiled = compile_anchor_action(
                    anchor_matrix,
                    maps[batch_index, slot].detach().cpu().numpy(),
                )
                output[batch_index, slot] = torch.from_numpy(
                    compiled.astype(np.float32)
                )
        return output

    def encode_operator_bundle(self, tables: torch.Tensor) -> SimpleNamespace:
        return SimpleNamespace(matrices=self.encode_operators(tables))

    def _rollout(
        self,
        hidden: torch.Tensor,
        operator_codes: torch.Tensor,
        op_slots: torch.Tensor,
    ) -> SimpleNamespace:
        hidden = self.normalize_hidden(hidden)
        rows = torch.arange(hidden.shape[0])
        trajectory = [hidden]
        for time_index in range(op_slots.shape[1]):
            selected = operator_codes[rows, op_slots[:, time_index]]
            hidden = torch.bmm(selected, hidden.unsqueeze(-1)).squeeze(-1)
            hidden = self.normalize_hidden(hidden)
            trajectory.append(hidden)
        return SimpleNamespace(
            logits=self.decode_hidden(hidden),
            hidden=trajectory,
            operator_codes=operator_codes,
        )

    def run(
        self, tables: torch.Tensor, op_slots: torch.Tensor, start: torch.Tensor
    ) -> SimpleNamespace:
        return self._rollout(
            self.initial_hidden(start), self.encode_operators(tables), op_slots
        )

    def continue_from_hidden(
        self,
        hidden: torch.Tensor,
        operator_codes: torch.Tensor,
        op_slots: torch.Tensor,
    ) -> SimpleNamespace:
        return self._rollout(hidden, operator_codes, op_slots)


def _finite_values_from_tensor(result: dict[str, Any], metric: str) -> np.ndarray:
    values = np.asarray(result["future"]["mean"][metric], dtype=np.float64)
    return values[np.isfinite(values)]


def audit_exact_control(result: dict[str, Any], tolerance: float = 1e-6) -> dict[str, Any]:
    intervention_axis = {name: index for index, name in enumerate(result["interventions"])}
    accuracy = np.asarray(result["future"]["mean"]["accuracy"], dtype=np.float64)
    agreement = np.asarray(
        result["future"]["mean"]["native_h_agreement"], dtype=np.float64
    )
    logit_angle = np.asarray(
        result["future"]["mean"]["centered_logit_angle_to_native_h"], dtype=np.float64
    )
    hidden_angle = np.asarray(
        result["future"]["mean"]["hidden_metric_angle_to_native_h"], dtype=np.float64
    )
    counterfactual = np.asarray(
        result["future"]["mean"]["counterfactual_accuracy"], dtype=np.float64
    )

    expected_names = tuple(
        name
        for name in INTERVENTION_NAMES
        if name not in ("wrong_anchor", "wrong_prototype", "random_ray")
    )
    expected_indices = [intervention_axis[name] for name in expected_names]
    case_count = np.asarray(result["future"]["case_count"], dtype=np.int64)
    required_indices = expected_indices + [
        intervention_axis["wrong_anchor"],
        intervention_axis["wrong_prototype"],
    ]
    required_arrays = (
        accuracy[required_indices],
        agreement[required_indices],
        counterfactual[required_indices],
        logit_angle[expected_indices],
        hidden_angle[expected_indices],
    )
    complete_finite_panel = bool(
        np.all(case_count[required_indices] > 0)
        and all(np.isfinite(values).all() for values in required_arrays)
    )
    if not complete_finite_panel:
        raise RuntimeError("exact control has an empty or nonfinite required cell")
    expected_accuracy_min = float(np.min(accuracy[expected_indices]))
    expected_agreement_min = float(np.min(agreement[expected_indices]))
    expected_logit_angle_max = float(np.max(logit_angle[expected_indices]))
    expected_hidden_angle_max = float(np.max(hidden_angle[expected_indices]))
    wrong_results = {}
    for wrong_name in ("wrong_anchor", "wrong_prototype"):
        wrong_index = intervention_axis[wrong_name]
        wrong_results[wrong_name] = {
            "factual_accuracy_maximum": float(np.max(accuracy[wrong_index])),
            "native_agreement_maximum": float(np.max(agreement[wrong_index])),
            "counterfactual_accuracy_minimum": float(
                np.min(counterfactual[wrong_index])
            ),
        }
    wrong_accuracy_max = max(
        row["factual_accuracy_maximum"] for row in wrong_results.values()
    )
    wrong_agreement_max = max(
        row["native_agreement_maximum"] for row in wrong_results.values()
    )
    wrong_counterfactual_min = min(
        row["counterfactual_accuracy_minimum"] for row in wrong_results.values()
    )
    controls = result["controls"]
    exact_hidden_difference_max = max(
        float(
            controls["branch_maximum_absolute_hidden_difference_to_native"][name]
        )
        for name in expected_names
    )
    exact_logit_difference_max = max(
        float(
            controls["branch_maximum_absolute_logit_difference_to_native"][name]
        )
        for name in expected_names
    )
    passed = bool(
        expected_accuracy_min == 1.0
        and expected_agreement_min == 1.0
        and expected_logit_angle_max <= tolerance
        and expected_hidden_angle_max <= tolerance
        and exact_hidden_difference_max <= tolerance
        and exact_logit_difference_max <= tolerance
        and wrong_accuracy_max == 0.0
        and wrong_agreement_max == 0.0
        and wrong_counterfactual_min == 1.0
        and controls["projector"]["pass"]
        and controls["custom_rollout_matches_packaged"]
        and controls["sham_scale_within_float32_tolerance"]
        and controls["target_firewall_failures"] == 0
        and controls["direct_state_generator_firewall_failures"] == 0
        and controls["time_zero_oracle_anchor"]["pass"]
        and controls["wrong_anchor_and_prototype_differ_from_truth"]
        and controls["state_dict_unchanged"]
    )
    return {
        "expected_non_wrong_interventions": list(expected_names),
        "expected_accuracy_minimum": expected_accuracy_min,
        "expected_native_agreement_minimum": expected_agreement_min,
        "expected_centered_logit_angle_maximum": expected_logit_angle_max,
        "expected_hidden_angle_maximum": expected_hidden_angle_max,
        "expected_normalized_hidden_maximum_absolute_difference": exact_hidden_difference_max,
        "expected_logit_maximum_absolute_difference": exact_logit_difference_max,
        "wrong_control_accuracy_maximum": wrong_accuracy_max,
        "wrong_control_native_agreement_maximum": wrong_agreement_max,
        "wrong_control_counterfactual_accuracy_minimum": wrong_counterfactual_min,
        "wrong_controls_by_family": wrong_results,
        "plumbing_controls": controls,
        "tolerance": tolerance,
        "complete_finite_required_panel": complete_finite_panel,
        "pass": passed,
    }


def run_exact_compiled_control(
    api: Mapping[str, Any],
    *,
    context_count: int = CONTEXT_COUNT,
    nominal_bands: Sequence[int] = NOMINAL_DEPTH_BANDS,
    pairs_per_endpoint_band: int = PAIRS_PER_ENDPOINT_BAND,
    continuation_max_length: int = CONTINUATION_MAX_LENGTH,
    run_periodic: bool = True,
) -> dict[str, Any]:
    canonical_maps = api["canonical_maps"]("d4").astype(np.int64)
    contexts = make_context_bank(
        api["EpisodeGenerator"],
        seed=EVALUATION_CONTEXT_SEED,
        count=int(context_count),
        split="exact_control",
    )
    paths = make_endpoint_matched_path_bank(
        canonical_maps,
        seed=EVALUATION_PATH_SEED,
        split="exact_control",
        nominal_bands=nominal_bands,
        pairs_per_endpoint_band=int(pairs_per_endpoint_band),
    )
    continuations = make_continuation_bank(maximum_length=continuation_max_length)
    model = ExactCompiledModel(hidden_dim=12)
    anchors = model.state_anchors()
    prototypes = PrototypeBundle(
        torch32=anchors.clone(),
        numpy64=anchors.detach().cpu().numpy().astype(np.float64),
        audit={"source": "exact anchor chart", "pass": True},
    )
    result = evaluate_paired_model(
        model, contexts, paths, continuations, canonical_maps, prototypes
    )
    audit = audit_exact_control(result)
    periodic: dict[str, Any] | None = None
    if run_periodic:
        if 64 not in tuple(int(value) for value in nominal_bands):
            raise ValueError("periodic exact control requires nominal band 64")
        periodic = evaluate_periodic_model(
            model, contexts, paths, continuations, canonical_maps, prototypes
        )
        periodic_accuracy_parts: list[np.ndarray] = []
        periodic_case_count_parts: list[np.ndarray] = []
        for panel in periodic["future_by_band_and_parity"].values():
            periodic_accuracy_parts.append(
                np.asarray(panel["mean"]["accuracy"], dtype=np.float64).reshape(-1)
            )
            periodic_case_count_parts.append(
                np.asarray(panel["case_count"], dtype=np.int64).reshape(-1)
            )
        periodic_accuracy = np.concatenate(periodic_accuracy_parts)
        periodic_case_count = np.concatenate(periodic_case_count_parts)
        discrepancy = periodic["native_discrepancy_control"]
        periodic_hidden_difference = np.asarray(
            discrepancy["maximum_absolute_normalized_hidden_difference"],
            dtype=np.float64,
        )
        periodic_logit_difference = np.asarray(
            discrepancy["maximum_absolute_logit_difference"], dtype=np.float64
        )
        periodic_comparison_cases = np.asarray(
            discrepancy["comparison_cases"], dtype=np.int64
        )
        periodic_complete = bool(
            periodic_accuracy.size > 0
            and np.isfinite(periodic_accuracy).all()
            and np.all(periodic_case_count > 0)
            and np.isfinite(periodic_hidden_difference).all()
            and np.isfinite(periodic_logit_difference).all()
            and np.all(periodic_comparison_cases > 0)
        )
        if not periodic_complete:
            raise RuntimeError("exact periodic control has a missing or nonfinite cell")
        periodic_accuracy_minimum = float(np.min(periodic_accuracy))
        periodic_hidden_maximum = float(np.max(periodic_hidden_difference))
        periodic_logit_maximum = float(np.max(periodic_logit_difference))
        periodic["exact_control_accuracy_minimum"] = periodic_accuracy_minimum
        periodic["exact_control_normalized_hidden_maximum_absolute_difference"] = (
            periodic_hidden_maximum
        )
        periodic["exact_control_logit_maximum_absolute_difference"] = (
            periodic_logit_maximum
        )
        periodic["exact_control_complete_finite_panel"] = periodic_complete
        periodic["pass"] = bool(
            periodic_accuracy_minimum == 1.0
            and periodic_hidden_maximum <= 1e-6
            and periodic_logit_maximum <= 1e-6
        )
        audit["exact_periodic_closure_pass"] = periodic["pass"]
        audit["pass"] = bool(audit["pass"] and periodic["pass"])
    return {
        "schema": "komorebi.neuralese.semantic_retraction_exact_control.v1",
        "version": VERSION,
        "author": AUTHOR,
        "source": "synthetic exact compiler; no learned checkpoint loaded",
        "torch_thread_runtime": dict(FROZEN_TORCH_THREAD_RECEIPT),
        "context_bank": contexts.receipt,
        "path_bank": paths.receipt,
        "continuation_bank": continuations.receipt,
        "audit": audit,
        "result": result,
        "periodic": periodic,
    }


def verify_checkpoint_census(
    package: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Verify every sealed checkpoint receipt without loading any learned tensor."""

    result_dir = package / "results" / "packet_closure_pilot"
    seal_path = result_dir / "CHECKPOINT_SEAL.json"
    seal_bytes, seal_binding = _read_package_file_snapshot_against_sealed_manifest(
        package, seal_path.relative_to(package)
    )
    seal = loads_json_bytes_strict(seal_bytes)
    if seal.get("schema") != "komorebi.neuralese.packet_closure.checkpoint_seal.v1":
        raise RuntimeError("unexpected checkpoint-seal schema")
    if seal.get("version") != "0.4.0" or seal.get("profile") != "pilot":
        raise RuntimeError("checkpoint seal is not the official v0.4 pilot")
    if seal.get("strict_checkpoint_firewall") is not True:
        raise RuntimeError("strict checkpoint firewall was not sealed")
    if seal.get("source_integrity_at_seal", {}).get("valid") is not True:
        raise RuntimeError("checkpoint seal lacks valid source-integrity receipt")
    receipts = seal.get("checkpoints", [])
    expected_cells = {
        (arm, seed)
        for arm in (
            "euclidean_supervised",
            "euclidean_cr",
            "polar_supervised",
            "polar_cr",
        )
        for seed in (101, 211, 307)
    }
    actual_cells = {(str(row["arm"]), int(row["seed"])) for row in receipts}
    if len(receipts) != 12 or actual_cells != expected_cells:
        raise RuntimeError("checkpoint seal is not the complete official 4 x 3 census")

    verified: list[dict[str, Any]] = []
    for receipt in receipts:
        checkpoint = result_dir / str(receipt["path"])
        checkpoint_binding = verify_package_file_against_sealed_manifest(
            package, checkpoint.relative_to(package)
        )
        checkpoint_sha = checkpoint_binding["sha256"]
        if checkpoint_sha != receipt["sha256"]:
            raise RuntimeError(f"checkpoint SHA-256 mismatch: {checkpoint.name}")
        verified.append(
            {
                "arm": str(receipt["arm"]),
                "seed": int(receipt["seed"]),
                "checkpoint": checkpoint,
                "checkpoint_sha256": checkpoint_sha,
                "sealed_state_dict_digest": str(receipt["state_dict_digest"]),
                "sealed_manifest_binding": checkpoint_binding,
            }
        )
    verified.sort(key=lambda row: (str(row["arm"]), int(row["seed"])))
    seal["extracted_artifact_manifest_binding"] = seal_binding
    return verified, seal


def load_one_verified_checkpoint(
    verified: Mapping[str, Any],
    seal: Mapping[str, Any],
    api: Mapping[str, Any],
) -> dict[str, Any]:
    """Load exactly one already-hashed checkpoint, strictly and weights-only."""

    checkpoint = Path(verified["checkpoint"])
    sealed_size = verified.get("sealed_manifest_binding", {}).get("size")
    if type(sealed_size) is not int or sealed_size <= 0:
        raise RuntimeError(f"checkpoint has an invalid sealed size: {checkpoint.name}")
    checkpoint_bytes, checkpoint_sha256 = read_file_snapshot(
        checkpoint,
        label=f"sealed checkpoint {checkpoint.name}",
        maximum_bytes=sealed_size,
    )
    if (
        len(checkpoint_bytes) != sealed_size
        or checkpoint_sha256 != verified["checkpoint_sha256"]
    ):
        raise RuntimeError(f"checkpoint changed after census verification: {checkpoint.name}")
    # Load the exact bytes that were hashed above. This closes the path-level
    # hash/open race without relaxing weights_only deserialization.
    payload = torch.load(
        io.BytesIO(checkpoint_bytes), map_location="cpu", weights_only=True
    )
    del checkpoint_bytes
    arm = str(verified["arm"])
    seed = int(verified["seed"])
    if payload.get("arm") != arm or int(payload["train_config"]["seed"]) != seed:
        raise RuntimeError(f"checkpoint metadata mismatch: {checkpoint.name}")
    if payload.get("schema") != "komorebi.neuralese.packet_closure.checkpoint.v1":
        raise RuntimeError(f"checkpoint schema mismatch: {checkpoint.name}")
    if payload.get("version") != "0.4.0":
        raise RuntimeError(f"checkpoint version mismatch: {checkpoint.name}")
    if payload.get("source_digest") != seal.get("source_digest"):
        raise RuntimeError(f"checkpoint source digest mismatch: {checkpoint.name}")
    if payload.get("contract_sha256") != seal.get("contract_sha256"):
        raise RuntimeError(f"checkpoint contract digest mismatch: {checkpoint.name}")
    if payload.get("arm_spec") != asdict(api["get_packet_closure_arm"](arm)):
        raise RuntimeError(f"checkpoint arm specification mismatch: {checkpoint.name}")

    hidden_dim = int(payload["train_config"]["hidden_dim"])
    family = str(payload["arm_spec"]["model_family"])
    if family == "raw":
        model = api["ProjectiveLinearTableOperatorRNN"](hidden_dim=hidden_dim)
    elif family == "polar":
        model = api["PolarIsometricTableOperatorRNN"](hidden_dim=hidden_dim)
    else:
        raise RuntimeError(f"unknown frozen model family: {family}")
    incompatibility = model.load_state_dict(payload["state_dict"], strict=True)
    if incompatibility.missing_keys or incompatibility.unexpected_keys:
        raise RuntimeError(f"non-strict state load for {checkpoint.name}")
    model = model.to(device="cpu", dtype=torch.float32).eval()
    verify_float32_model(model)
    state_digest = api["state_dict_digest"](model)
    if state_digest != payload["provenance"]["final_state_digest"]:
        raise RuntimeError(f"checkpoint final-state digest mismatch: {checkpoint.name}")
    if state_digest != verified["sealed_state_dict_digest"]:
        raise RuntimeError(f"checkpoint seal state digest mismatch: {checkpoint.name}")
    return {
        **dict(verified),
        "model_family": family,
        "model": model,
        "loaded_state_dict_digest": state_digest,
    }


def manifest_only_dry_run(package: Path = DEFAULT_PACKAGE) -> dict[str, Any]:
    """Freeze all model-independent manifests and compute the prospective budget."""

    source_integrity = verify_package_source_integrity(package)
    api = import_v04_api(package)
    canonical_maps = api["canonical_maps"]("d4").astype(np.int64)
    context_banks = make_disjoint_context_banks(api["EpisodeGenerator"])
    path_banks = make_disjoint_path_banks(canonical_maps)
    continuations = make_continuation_bank()
    random_manifest = make_random_key_manifest(
        CONTEXT_COUNT, path_banks["evaluation"], split_code=2
    )

    evaluation_pairs = path_banks["evaluation"].pairs
    calibration_pairs = path_banks["calibration"].pairs
    evaluation_prefix_edges = sum(pair.exact_length for pair in evaluation_pairs)
    calibration_prefix_edges = sum(pair.exact_length for pair in calibration_pairs)
    w4_tree_edges = len(continuations.words) - 1
    stress_words = tuple(path_banks["stress"].words_by_endpoint)
    stress_prefixes = {
        word[:length]
        for word in stress_words
        for length in range(1, len(word) + 1)
    }
    merged_suffix_prefixes = {
        word[:length]
        for word in tuple(continuations.words) + stress_words
        for length in range(1, len(word) + 1)
    }
    stress_tree_edges = len(stress_prefixes)
    merged_suffix_tree_edges = len(merged_suffix_prefixes)
    incremental_stress_edges = merged_suffix_tree_edges - w4_tree_edges
    source_orientation_cases = CONTEXT_COUNT * len(evaluation_pairs) * 8 * 2
    unordered_start_cases = CONTEXT_COUNT * len(evaluation_pairs) * 8
    # Physical branch starts after reusing orientation-invariant resets and rays.
    physical_one_shot_branches_per_unordered_case = 20
    calibration_prefix_matvec = CONTEXT_COUNT * 2 * 8 * calibration_prefix_edges
    evaluation_prefix_matvec = CONTEXT_COUNT * 2 * 8 * evaluation_prefix_edges
    custom_rollout_matvec = CONTEXT_COUNT * 8 * evaluation_pairs[0].exact_length
    exhaustive_selector_matvec = CONTEXT_COUNT * 3 * 2 * 8
    cut_selector_commutation_matvec = (
        CONTEXT_COUNT * len(evaluation_pairs) * 3 * 2 * 16
    )
    one_shot_merged_suffix_matvec = (
        unordered_start_cases
        * physical_one_shot_branches_per_unordered_case
        * merged_suffix_tree_edges
    )
    one_shot_w4_matvec = (
        unordered_start_cases
        * physical_one_shot_branches_per_unordered_case
        * w4_tree_edges
    )
    one_shot_incremental_stress_matvec = (
        unordered_start_cases
        * physical_one_shot_branches_per_unordered_case
        * incremental_stress_edges
    )
    periodic_pairs = [
        pair for pair in evaluation_pairs if pair.nominal_band in (8, 64)
    ]
    periodic_prefix_edge_sum = sum(pair.exact_length for pair in periodic_pairs)
    periodic_logical_modes = len(periodic_mode_layout())
    periodic_prefix_modes = len(periodic_repair_layout())
    periodic_suffix_modes = len(periodic_suffix_physical_layout())
    periodic_prefix_matvec = (
        CONTEXT_COUNT * 2 * 8 * periodic_prefix_modes * periodic_prefix_edge_sum
    )
    periodic_w4_matvec = (
        CONTEXT_COUNT
        * len(periodic_pairs)
        * 2
        * 8
        * periodic_suffix_modes
        * w4_tree_edges
    )
    learned_per_checkpoint_matvec = (
        calibration_prefix_matvec
        + evaluation_prefix_matvec
        + custom_rollout_matvec
        + exhaustive_selector_matvec
        + cut_selector_commutation_matvec
        + one_shot_merged_suffix_matvec
        + periodic_prefix_matvec
        + periodic_w4_matvec
    )

    calibration_prefix_kernel_calls = CONTEXT_COUNT * 2 * calibration_prefix_edges
    evaluation_prefix_kernel_calls = CONTEXT_COUNT * 2 * evaluation_prefix_edges
    custom_rollout_kernel_calls = CONTEXT_COUNT * evaluation_pairs[0].exact_length
    exhaustive_selector_kernel_calls = CONTEXT_COUNT * 3 * 2
    cut_selector_commutation_kernel_calls = (
        CONTEXT_COUNT * len(evaluation_pairs) * 3 * 2
    )
    one_shot_merged_suffix_kernel_calls = (
        CONTEXT_COUNT * len(evaluation_pairs) * merged_suffix_tree_edges
    )
    one_shot_w4_kernel_calls = CONTEXT_COUNT * len(evaluation_pairs) * w4_tree_edges
    one_shot_incremental_stress_kernel_calls = (
        CONTEXT_COUNT * len(evaluation_pairs) * incremental_stress_edges
    )
    periodic_prefix_kernel_calls = CONTEXT_COUNT * 2 * periodic_prefix_edge_sum
    periodic_w4_kernel_calls = (
        CONTEXT_COUNT * len(periodic_pairs) * 2 * w4_tree_edges
    )
    total_kernel_calls = (
        calibration_prefix_kernel_calls
        + evaluation_prefix_kernel_calls
        + custom_rollout_kernel_calls
        + exhaustive_selector_kernel_calls
        + cut_selector_commutation_kernel_calls
        + one_shot_merged_suffix_kernel_calls
        + periodic_prefix_kernel_calls
        + periodic_w4_kernel_calls
    )
    exact_periodic_native_prefix_matvec = (
        CONTEXT_COUNT * 2 * 8 * periodic_prefix_edge_sum
    )
    exact_control_matvec = (
        evaluation_prefix_matvec
        + custom_rollout_matvec
        + exhaustive_selector_matvec
        + cut_selector_commutation_matvec
        + one_shot_w4_matvec
        + exact_periodic_native_prefix_matvec
        + periodic_prefix_matvec
        + periodic_w4_matvec
    )
    exact_periodic_native_prefix_kernel_calls = (
        CONTEXT_COUNT * 2 * periodic_prefix_edge_sum
    )
    exact_control_kernel_calls = (
        evaluation_prefix_kernel_calls
        + custom_rollout_kernel_calls
        + exhaustive_selector_kernel_calls
        + cut_selector_commutation_kernel_calls
        + one_shot_w4_kernel_calls
        + exact_periodic_native_prefix_kernel_calls
        + periodic_prefix_kernel_calls
        + periodic_w4_kernel_calls
    )

    largest_start_chunk = max(
        physical_one_shot_branches_per_unordered_case * 8,
        periodic_prefix_modes * 8,
        periodic_suffix_modes * 8,
    )
    operator_bytes = largest_start_chunk * 2 * 12 * 12 * 4
    one_shot_tree_bytes = (
        (merged_suffix_tree_edges + 1) * 20 * 8 * (12 + 8) * 4
    )
    periodic_tree_bytes = (
        len(continuations.words) * periodic_suffix_modes * 8 * (12 + 8) * 4
    )
    periodic_repair_all_step_checkpoint_payload_bytes = (
        max(pair.exact_length for pair in periodic_pairs)
        * periodic_prefix_modes
        * 8
        * (((12 + 8) * 4) + 8)
    )
    periodic_repair_all_step_checkpoint_conservative_bytes = max(
        8 * 1024 * 1024,
        4 * periodic_repair_all_step_checkpoint_payload_bytes,
    )
    batched_diagnostic_panel_conservative_bytes = 16 * 1024 * 1024

    def tensor_accumulator_live_bytes(cells: int) -> int:
        # case_count plus a float64 sum and int64 finite count per metric.
        return int(cells) * (8 + len(TensorAccumulator.METRICS) * 16)

    one_shot_cells = (
        len(INTERVENTION_NAMES)
        * len(NOMINAL_DEPTH_BANDS)
        * len(continuations.words)
        * 8
    )
    random_cells = 4 * len(NOMINAL_DEPTH_BANDS) * len(continuations.words) * 8
    stress_cells = (
        len(INTERVENTION_NAMES)
        * len(NOMINAL_DEPTH_BANDS)
        * len(stress_words)
        * 8
    )
    stress_random_cells = 4 * len(NOMINAL_DEPTH_BANDS) * len(stress_words) * 8
    one_shot_accumulator_bytes = tensor_accumulator_live_bytes(one_shot_cells)
    random_accumulator_bytes = tensor_accumulator_live_bytes(random_cells)
    stress_accumulator_bytes = tensor_accumulator_live_bytes(stress_cells)
    stress_random_accumulator_bytes = tensor_accumulator_live_bytes(
        stress_random_cells
    )
    context_stratum_bytes = (
        len(ContextStratumAccumulator.METRICS)
        * len(INTERVENTION_NAMES)
        * len(NOMINAL_DEPTH_BANDS)
        * CONTEXT_COUNT
        * len(SUFFIX_STRATUM_NAMES)
        * 16
    )
    periodic_cells = (
        4
        * len(PERIODIC_CONDITION_NAMES)
        * len(PERIODIC_CADENCES)
        * len(continuations.words)
        * 8
    )
    periodic_accumulator_bytes = tensor_accumulator_live_bytes(periodic_cells)
    periodic_context_bytes = (
        2
        * len(PERIODIC_CONDITION_NAMES)
        * len(PERIODIC_CADENCES)
        * 2
        * 2
        * CONTEXT_COUNT
        * 8
    )
    accumulator_bytes = (
        one_shot_accumulator_bytes
        + random_accumulator_bytes
        + stress_accumulator_bytes
        + stress_random_accumulator_bytes
        + context_stratum_bytes
        + periodic_accumulator_bytes
        + periodic_context_bytes
    )
    calibration_endpoint_panel_bytes = 4 * 1024 * 1024
    packed_native_trajectory_steps = CONTEXT_COUNT * 2 * periodic_prefix_edge_sum
    packed_native_trajectory_payload_bytes = (
        packed_native_trajectory_steps * 8 * 12 * 4
    )
    packed_native_trajectory_tensor_count = (
        CONTEXT_COUNT * len(periodic_pairs) * 2
    )
    # Includes terminal/named checkpoint tensors, dictionaries, allocator slack,
    # and more than 2x the packed all-step hidden payload.
    native_prefix_cache_bytes = max(
        96 * 1024 * 1024,
        2 * packed_native_trajectory_payload_bytes + 32 * 1024 * 1024,
    )
    one_loaded_model_and_payload_bytes = 64 * 1024 * 1024
    serialized_single_checkpoint_python_upper_bound = 256 * 1024 * 1024
    interpreter_torch_numpy_baseline_allowance = 128 * 1024 * 1024
    streaming_json_chunk_allowance = 1 * 1024 * 1024
    estimated_peak = (
        operator_bytes
        + max(one_shot_tree_bytes, periodic_tree_bytes)
        + periodic_repair_all_step_checkpoint_conservative_bytes
        + batched_diagnostic_panel_conservative_bytes
        + accumulator_bytes
        + calibration_endpoint_panel_bytes
        + native_prefix_cache_bytes
        + one_loaded_model_and_payload_bytes
        + serialized_single_checkpoint_python_upper_bound
        + interpreter_torch_numpy_baseline_allowance
        + streaming_json_chunk_allowance
    )
    declared_peak_ceiling = DECLARED_PEAK_WORKING_SET_CEILING_BYTES
    receipts = {
        "contexts": {
            name: {
                "canonical_json_sha256": bank.receipt["sha256"],
                "raw_tensor_sha256": bank.receipt["raw_tensor_sha256"],
            }
            for name, bank in context_banks.items()
        },
        "paths": {
            "calibration": {
                "canonical_json_sha256": path_banks["calibration"].receipt["sha256"],
                "raw_word_sha256": path_banks["calibration"].receipt["raw_word_sha256"],
            },
            "evaluation": {
                "canonical_json_sha256": path_banks["evaluation"].receipt["sha256"],
                "raw_word_sha256": path_banks["evaluation"].receipt["raw_word_sha256"],
            },
            "stress": {
                "canonical_json_sha256": path_banks["stress"].receipt["sha256"]
            },
        },
        "continuations": continuations.receipt["sha256"],
        "random_keys": random_manifest["sha256"],
    }
    counts = {
        "prior_contexts": CONTEXT_COUNT,
        "calibration_contexts": CONTEXT_COUNT,
        "evaluation_contexts": CONTEXT_COUNT,
        "path_pairs_per_split": len(evaluation_pairs),
        "calibration_path_members": 2 * len(calibration_pairs),
        "calibration_prototype_endpoint_contributions": (
            CONTEXT_COUNT * len(calibration_pairs) * 2 * 8
        ),
        "calibration_prototype_contributions_per_visible_class": (
            CONTEXT_COUNT * len(calibration_pairs) * 2
        ),
        "evaluation_encoded_contexts_per_checkpoint": CONTEXT_COUNT,
        "path_pairs_per_nominal_band": 8 * PAIRS_PER_ENDPOINT_BAND,
        "path_pairs_per_endpoint_band_cell": PAIRS_PER_ENDPOINT_BAND,
        "words_per_path_split": 2 * len(evaluation_pairs),
        "canonical_starts_per_path_member": 8,
        "unordered_pair_start_evaluation_cases": unordered_start_cases,
        "source_orientation_evaluation_cases": source_orientation_cases,
        "primary_suffix_words": len(continuations.words),
        "primary_nonempty_suffix_words": len(continuations.words) - 1,
        "primary_suffix_tree_edges": w4_tree_edges,
        "stress_suffix_words": len(stress_words),
        "stress_suffix_tree_edges_if_standalone": stress_tree_edges,
        "merged_W4_plus_stress_suffix_tree_edges": merged_suffix_tree_edges,
        "incremental_stress_edges_beyond_W4": incremental_stress_edges,
        "single_reset_interventions": len(INTERVENTION_NAMES),
        "single_reset_intervention_names": list(INTERVENTION_NAMES),
        "logical_primary_cases_per_intervention": source_orientation_cases
        * len(continuations.words),
        "logical_primary_cases_all_interventions": source_orientation_cases
        * len(continuations.words)
        * len(INTERVENTION_NAMES),
        "logical_stress_cases_per_intervention": source_orientation_cases
        * len(path_banks["stress"].words_by_endpoint),
        "logical_stress_cases_all_interventions": source_orientation_cases
        * len(path_banks["stress"].words_by_endpoint)
        * len(INTERVENTION_NAMES),
        "physical_one_shot_branch_groups_per_unordered_pair_start": 20,
        "physical_one_shot_starting_states_per_context_pair": 20 * 8,
        "periodic_conditions": len(PERIODIC_CONDITION_NAMES),
        "periodic_condition_names": list(PERIODIC_CONDITION_NAMES),
        "periodic_cadences": len(PERIODIC_CADENCES),
        "periodic_cadence_values": list(PERIODIC_CADENCES),
        "periodic_condition_cadence_logical_modes": periodic_logical_modes,
        "periodic_prefix_physical_repair_modes": periodic_prefix_modes,
        "periodic_suffix_physical_modes": periodic_suffix_modes,
        "periodic_path_pairs_bands_8_and_64": len(periodic_pairs),
        "periodic_path_members_bands_8_and_64": 2 * len(periodic_pairs),
        "packed_native_prefix_trajectory_step_records": packed_native_trajectory_steps,
        "packed_native_prefix_trajectory_tensor_count": (
            packed_native_trajectory_tensor_count
        ),
        "periodic_prefix_starting_trajectories_all_modes": CONTEXT_COUNT
        * len(periodic_pairs)
        * 2
        * 8
        * periodic_logical_modes,
        "periodic_prefix_physical_starting_trajectories": CONTEXT_COUNT
        * len(periodic_pairs)
        * 2
        * 8
        * periodic_prefix_modes,
        "periodic_suffix_logical_cases_all_modes": CONTEXT_COUNT
        * len(periodic_pairs)
        * 2
        * 8
        * periodic_logical_modes
        * len(continuations.words),
        "random_draws_per_unordered_pair_start": 4,
        "random_key_count": random_manifest["key_count"],
        "random_raw_primary_orientation_draw_cases": source_orientation_cases
        * 4
        * len(continuations.words),
    }
    budget = {
        "maximum_starting_state_chunk": largest_start_chunk,
        "required_chunk_ceiling": 4096,
        "chunk_ceiling_pass": largest_start_chunk <= 4096,
        "maximum_checkpoint_shard_bytes": MAXIMUM_CHECKPOINT_SHARD_BYTES,
        "maximum_exact_control_bytes": MAXIMUM_EXACT_CONTROL_BYTES,
        "maximum_bundle_metadata_bytes": MAXIMUM_BUNDLE_METADATA_BYTES,
        "result_disk_safety_margin_bytes": RESULT_DISK_SAFETY_MARGIN_BYTES,
        "minimum_free_disk_bytes_before_spend": (
            MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND
        ),
        "result_bundle_file_count": 17,
        "result_bundle_layout": {
            "run": RUN_FILENAME,
            "exact_control": EXACT_CONTROL_FILENAME,
            "internal_spend_receipt": SPEND_RECEIPT_FILENAME,
            "checkpoint_directory": CHECKPOINT_DIRECTORY_NAME,
            "checkpoint_shards": 12,
            "manifest": BUNDLE_MANIFEST_FILENAME,
            "commit_last": COMMIT_FILENAME,
        },
        "physical_one_shot_branches_per_unordered_case_after_reuse": physical_one_shot_branches_per_unordered_case,
        "float32_recurrent_matvec_per_checkpoint": {
            "calibration_prefix": calibration_prefix_matvec,
            "evaluation_prefix_shared_primary_stress_periodic_native": evaluation_prefix_matvec,
            "custom_rollout_control": custom_rollout_matvec,
            "exhaustive_section_selector_generator_control": exhaustive_selector_matvec,
            "cut_selector_commutation_control": cut_selector_commutation_matvec,
            "one_shot_merged_W4_plus_stress_tree": one_shot_merged_suffix_matvec,
            "one_shot_W4_tree": one_shot_w4_matvec,
            "one_shot_incremental_stress_edges": one_shot_incremental_stress_matvec,
            "periodic_repair_prefix_native_is_cached": periodic_prefix_matvec,
            "periodic_W4_physical_tree": periodic_w4_matvec,
            "total": learned_per_checkpoint_matvec,
        },
        "float32_recurrent_matvec_all_12_checkpoints": 12
        * learned_per_checkpoint_matvec,
        "checkpoint_free_exact_compiled_preflight_matvec": {
            "one_shot_evaluation_prefix": evaluation_prefix_matvec,
            "custom_rollout_control": custom_rollout_matvec,
            "exhaustive_section_selector_generator_control": exhaustive_selector_matvec,
            "cut_selector_commutation_control": cut_selector_commutation_matvec,
            "one_shot_W4_tree": one_shot_w4_matvec,
            "periodic_native_prefix_not_cached_in_preflight": exact_periodic_native_prefix_matvec,
            "periodic_repair_prefix": periodic_prefix_matvec,
            "periodic_W4_physical_tree": periodic_w4_matvec,
            "total": exact_control_matvec,
        },
        "total_matvec_exact_preflight_plus_all_12_checkpoints": (
            exact_control_matvec + 12 * learned_per_checkpoint_matvec
        ),
        "batched_recurrent_kernel_calls_per_checkpoint": {
            "calibration_prefix": calibration_prefix_kernel_calls,
            "evaluation_prefix_shared_primary_stress_periodic_native": evaluation_prefix_kernel_calls,
            "custom_rollout_control": custom_rollout_kernel_calls,
            "exhaustive_section_selector_generator_control": exhaustive_selector_kernel_calls,
            "cut_selector_commutation_control": cut_selector_commutation_kernel_calls,
            "one_shot_merged_W4_plus_stress_tree": one_shot_merged_suffix_kernel_calls,
            "one_shot_W4_tree": one_shot_w4_kernel_calls,
            "one_shot_incremental_stress_edges": one_shot_incremental_stress_kernel_calls,
            "periodic_repair_prefix_native_is_cached": periodic_prefix_kernel_calls,
            "periodic_W4_physical_tree": periodic_w4_kernel_calls,
            "total": total_kernel_calls,
        },
        "checkpoint_free_exact_compiled_preflight_kernel_calls": {
            "total": exact_control_kernel_calls,
            "periodic_native_prefix_not_cached": exact_periodic_native_prefix_kernel_calls,
        },
        "total_kernel_calls_exact_preflight_plus_all_12_checkpoints": (
            exact_control_kernel_calls + 12 * total_kernel_calls
        ),
        "estimated_peak_working_set_bytes": estimated_peak,
        "declared_peak_working_set_ceiling_bytes": declared_peak_ceiling,
        "estimated_peak_within_declared_ceiling": estimated_peak
        <= declared_peak_ceiling,
        "estimate_components": {
            "operator_chunk": operator_bytes,
            "one_shot_merged_tree_hidden_and_logits": one_shot_tree_bytes,
            "periodic_tree_hidden_and_logits": periodic_tree_bytes,
            "periodic_repair_all_step_checkpoint_payload": (
                periodic_repair_all_step_checkpoint_payload_bytes
            ),
            "periodic_repair_all_step_checkpoint_conservative": (
                periodic_repair_all_step_checkpoint_conservative_bytes
            ),
            "batched_diagnostic_panel_conservative": (
                batched_diagnostic_panel_conservative_bytes
            ),
            "online_accumulators_total": accumulator_bytes,
            "one_shot_accumulator": one_shot_accumulator_bytes,
            "random_draw_accumulator": random_accumulator_bytes,
            "stress_accumulator": stress_accumulator_bytes,
            "stress_random_draw_accumulator": stress_random_accumulator_bytes,
            "context_stratum_accumulator": context_stratum_bytes,
            "periodic_accumulators": periodic_accumulator_bytes,
            "periodic_context_arrays": periodic_context_bytes,
            "calibration_endpoint_panel_conservative": calibration_endpoint_panel_bytes,
            "native_prefix_cache_conservative": native_prefix_cache_bytes,
            "packed_native_prefix_trajectory_float32_payload": (
                packed_native_trajectory_payload_bytes
            ),
            "one_loaded_model_and_payload_conservative": one_loaded_model_and_payload_bytes,
            "serialized_single_checkpoint_python_upper_bound": serialized_single_checkpoint_python_upper_bound,
            "interpreter_torch_numpy_baseline_allowance": interpreter_torch_numpy_baseline_allowance,
            "streaming_json_chunk_allowance": streaming_json_chunk_allowance,
        },
        "full_panel_hidden_or_logits_retained": False,
        "full_twelve_checkpoint_results_retained": False,
        "one_checkpoint_result_serialized_then_released": True,
        "one_shot_merged_trie_traversals_per_context_pair": 1,
        "periodic_prefix_physical_modes_per_path_member": periodic_prefix_modes,
        "periodic_suffix_physical_modes_per_path_member": periodic_suffix_modes,
        "periodic_W4_trie_traversals_per_context_path_member": 1,
        "evaluation_prefix_reconstruction_disclosed": (
            "once; shared by primary, stress, and periodic native-prefix cache"
        ),
    }
    payload = {
        "schema": "komorebi.neuralese.semantic_retraction_manifest_dry_run.v1",
        "version": VERSION,
        "author": AUTHOR,
        "analysis_status": "MANIFEST_ONLY_NO_CHECKPOINT_LOAD",
        "learned_checkpoint_load_count": 0,
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "machine_contract_sha256": sha256_file(MACHINE_CONTRACT_PATH),
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
        "test_sha256": sha256_file(TEST_PATH),
        "torch_thread_runtime": dict(FROZEN_TORCH_THREAD_RECEIPT),
        "package_source_integrity": source_integrity,
        "sealed_import_origin_receipt": api["import_origin_receipt"],
        "receipts": receipts,
        "counts": counts,
        "budget": budget,
        "context_manifests": {
            name: bank.receipt for name, bank in context_banks.items()
        },
        "path_manifests": {
            "calibration": path_banks["calibration"].receipt,
            "evaluation": path_banks["evaluation"].receipt,
            "stress": path_banks["stress"].receipt,
        },
        "continuation_manifest": continuations.receipt,
        "random_key_manifest": random_manifest,
    }
    payload["freeze_receipt_sha256"] = canonical_json_digest(payload)
    return payload


def load_machine_contract(path: Path = MACHINE_CONTRACT_PATH) -> dict[str, Any]:
    contract, _, _ = read_json_snapshot(path, label="machine protocol contract")
    return contract


def assert_manifest_matches_runtime(
    manifest_path: Path = MANIFEST_DRY_RUN_PATH,
    *,
    package: Path = DEFAULT_PACKAGE,
) -> dict[str, Any]:
    """Regenerate checkpoint-free banks and require byte-equivalent manifest data."""

    saved, saved_file_sha256, _ = read_json_snapshot(
        manifest_path, label="checkpoint-free manifest receipt"
    )
    claimed_freeze_digest = saved.get("freeze_receipt_sha256")
    digest_payload = dict(saved)
    digest_payload.pop("freeze_receipt_sha256", None)
    if claimed_freeze_digest != canonical_json_digest(digest_payload):
        raise RuntimeError("manifest freeze receipt digest is internally inconsistent")
    expected = manifest_only_dry_run(package.resolve())
    if not type_strict_equal(saved, expected):
        raise RuntimeError(
            "saved context/path/count/budget manifest does not match runtime regeneration"
        )
    return {
        "path": str(manifest_path),
        "file_sha256": saved_file_sha256,
        "freeze_receipt_sha256": claimed_freeze_digest,
        "receipts": saved["receipts"],
        "counts": saved["counts"],
        "budget": saved["budget"],
    }


def validate_protocol_matches_runtime(protocol: Mapping[str, Any]) -> None:
    if set(protocol) != {
        "schema",
        "version",
        "author",
        "status",
        "normative_protocol",
        "normative_protocol_sha256",
        "runtime_contract",
        "execution_firewall",
    }:
        raise RuntimeError("machine protocol contract has an unexpected top-level key set")
    if (
        protocol.get("schema")
        != "komorebi.neuralese.semantic_retraction_runtime_contract.v1"
        or protocol.get("version") != VERSION
        or protocol.get("author") != AUTHOR
        or protocol.get("normative_protocol") != "../ANALYSIS_PROTOCOL.md"
        or protocol.get("status") not in {"DRAFT_LOCKED", "FROZEN_POSTHOC"}
    ):
        raise RuntimeError("machine protocol contract metadata is invalid")
    expected = {
        "prior_context_seed": PRIOR_CONTEXT_SEED,
        "calibration_context_seed": CALIBRATION_CONTEXT_SEED,
        "evaluation_context_seed": EVALUATION_CONTEXT_SEED,
        "context_count_per_new_split": CONTEXT_COUNT,
        "calibration_path_seed": CALIBRATION_PATH_SEED,
        "evaluation_path_seed": EVALUATION_PATH_SEED,
        "stress_path_seed": STRESS_PATH_SEED,
        "nominal_depth_bands": list(NOMINAL_DEPTH_BANDS),
        "endpoint_parity_vector": [0, 1, 0, 1, 1, 0, 1, 0],
        "exact_length_rule": "nominal_band + endpoint_parity",
        "pairs_per_endpoint_band": PAIRS_PER_ENDPOINT_BAND,
        "path_rng": "numpy.random.Generator(numpy.random.PCG64(seed))",
        "path_candidate_dtype": "numpy.uint8",
        "path_pair_same_generator_histogram": True,
        "path_generator_count_imbalance_maximum": 2,
        "path_identical_symbol_run_maximum": 4,
        "all_canonical_starts": 8,
        "continuation_max_length": CONTINUATION_MAX_LENGTH,
        "continuation_word_count": len(words_upto(CONTINUATION_MAX_LENGTH)),
        "suffix_strata": list(SUFFIX_STRATUM_NAMES),
        "random_ray_seed": RANDOM_RAY_SEED,
        "random_ray_evaluation_split_code": 2,
        "random_draws_per_unordered_pair_start": 4,
        "random_seed_sequence_encoding": "entropy_vector_not_spawn_key",
        "random_base_dimension": 12,
        "periodic_cadences": list(PERIODIC_CADENCES),
        "primary_periodic_cadence": 4,
        "periodic_nominal_depth_bands": [8, 64],
        "periodic_clock": "absolute_from_first_prefix_action_through_suffix",
        "interventions": list(INTERVENTION_NAMES),
        "periodic_conditions": list(PERIODIC_CONDITION_NAMES),
        "periodic_prefix_sham_all_steps": True,
        "wrong_anchor_action": "canonical_r",
        "model_operator_forward_dtype": "torch.float32",
        "detached_diagnostic_dtype": "numpy.float64",
        "torch_intraop_threads": TORCH_INTRAOP_THREADS,
        "torch_interop_threads": TORCH_INTEROP_THREADS,
        "maximum_starting_state_chunk": 4096,
        "maximum_checkpoint_shard_bytes": MAXIMUM_CHECKPOINT_SHARD_BYTES,
        "maximum_exact_control_bytes": MAXIMUM_EXACT_CONTROL_BYTES,
        "maximum_bundle_metadata_bytes": MAXIMUM_BUNDLE_METADATA_BYTES,
        "minimum_free_disk_bytes_before_spend": (
            MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND
        ),
        "result_bundle_layout": [
            RUN_FILENAME,
            EXACT_CONTROL_FILENAME,
            SPEND_RECEIPT_FILENAME,
            f"{CHECKPOINT_DIRECTORY_NAME}/<12 arm-seed shards>",
            BUNDLE_MANIFEST_FILENAME,
            COMMIT_FILENAME,
        ],
        "result_bundle_required_suffix": REQUIRED_RESULT_BUNDLE_SUFFIX,
        "result_bundles_may_not_be_nested": True,
        "review_binds_test_sha256": True,
    }
    actual = protocol.get("runtime_contract")
    if not type_strict_equal(actual, expected):
        raise RuntimeError("protocol runtime_contract does not exactly match implementation constants")
    expected_firewall = {
        "learned_run_locked_pending_static_review": True,
        "required_manifest_file": "MANIFEST_DRY_RUN.json",
        "manifest_must_match_checkpoint_free_runtime_regeneration": True,
        "required_release_file": "STATIC_REVIEW_PASS.json",
        "release_must_match_protocol_contract_implementation_test_and_manifest_sha256": True,
        "evaluation_bank_spend_receipt_created_before_first_learned_evaluation": True,
        "learned_outputs_and_spend_receipt_are_exclusive_non_overwritable": True,
        "result_output_is_self_contained_commit_last_bundle": True,
        "result_bundle_must_verify_before_return": True,
        "internal_and_external_spend_receipts_byte_identical": True,
        "synthetic_control_output_is_exclusive_and_protected": True,
        "saved_manifest_publication_or_overwrite_forbidden_after_spend_or_static_release": True,
        "root_protocol_receipt_binds_theory_primary_and_crosscheck": True,
        "sealed_source_import_origin_verified": True,
        "external_python_bytecode_cache_prefix_forbidden": True,
        "checkpoint_load_uses_prehashed_bytes": True,
        "pre_spend_manifest_budget_and_disk_headroom_required": True,
        "static_review_schema_and_required_checks_are_exact": True,
        "static_review_binds_theoretical_framework_sha256": True,
        "authoritative_external_spend_marker_published_before_internal_copy": True,
        "learned_bundle_suffix_and_non_nesting_required": True,
    }
    if not type_strict_equal(protocol.get("execution_firewall"), expected_firewall):
        raise RuntimeError("protocol execution_firewall does not match implementation")


def validate_root_protocol_receipt(
    manifest: Mapping[str, Any],
    *,
    receipt_path: Path = ROOT_PROTOCOL_RECEIPT_PATH,
) -> dict[str, Any]:
    """Validate the terminal, non-self-referential freeze receipt."""

    project_root = HERE.parent.resolve()
    artifact_paths = {
        "analysis_protocol": PROTOCOL_PATH,
        "theoretical_framework": THEORETICAL_FRAMEWORK_PATH,
        "primary_implementation": Path(__file__).resolve(),
        "primary_tests": TEST_PATH,
        "primary_machine_contract": MACHINE_CONTRACT_PATH,
        "primary_manifest_dry_run": MANIFEST_DRY_RUN_PATH,
        "primary_static_review": STATIC_REVIEW_RELEASE_PATH,
        "independent_crosscheck_protocol": INDEPENDENT_CROSSCHECK_PROTOCOL_PATH,
        "independent_crosscheck_implementation": (
            INDEPENDENT_CROSSCHECK_IMPLEMENTATION_PATH
        ),
        "independent_crosscheck_tests": INDEPENDENT_CROSSCHECK_TEST_PATH,
        "independent_crosscheck_freeze_receipt": (
            INDEPENDENT_CROSSCHECK_FREEZE_RECEIPT_PATH
        ),
    }
    expected_relative_paths: dict[str, str] = {}
    expected_hashes: dict[str, str] = {}
    for name, path in artifact_paths.items():
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"freeze artifact is absent or symbolic: {name}")
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(project_root):
            raise RuntimeError(f"freeze artifact escapes project root: {name}")
        expected_relative_paths[name] = resolved.relative_to(project_root).as_posix()
        _, expected_hashes[name] = read_file_snapshot(
            resolved, label=f"freeze artifact {name}"
        )

    frozen_crosscheck_bytes, frozen_crosscheck_receipt_sha = read_file_snapshot(
        INDEPENDENT_CROSSCHECK_FREEZE_RECEIPT_PATH,
        label="independent crosscheck freeze receipt",
    )
    frozen_crosscheck_protocol = frozen_crosscheck_bytes.decode("utf-8").strip()
    if (
        frozen_crosscheck_receipt_sha
        != expected_hashes["independent_crosscheck_freeze_receipt"]
    ):
        raise RuntimeError("independent crosscheck freeze receipt snapshot mismatch")
    if frozen_crosscheck_protocol != expected_hashes["independent_crosscheck_protocol"]:
        raise RuntimeError("independent crosscheck freeze receipt does not bind its protocol")

    receipt, receipt_file_sha256, _ = read_json_snapshot(
        receipt_path, label="root protocol receipt"
    )
    required_top_level = {
        "schema",
        "version",
        "author",
        "status",
        "frozen_date",
        "frozen_before_learned_outcomes",
        "bank_seeds",
        "artifact_paths",
        "artifact_sha256",
        "source_provenance",
        "manifest_freeze_receipt_sha256",
        "receipt_sha256",
    }
    if set(receipt) != required_top_level:
        raise RuntimeError("root protocol receipt has an unexpected key set")
    if (
        receipt.get("schema")
        != "komorebi.neuralese.semantic_retraction.protocol_receipt.v1"
        or receipt.get("version") != VERSION
        or receipt.get("author") != AUTHOR
        or receipt.get("status") != "FROZEN_BEFORE_LEARNED_OUTCOMES"
        or receipt.get("frozen_before_learned_outcomes") is not True
        or not isinstance(receipt.get("frozen_date"), str)
        or not receipt["frozen_date"]
    ):
        raise RuntimeError("root protocol receipt metadata is invalid")
    expected_seeds = {
        "prior_context": PRIOR_CONTEXT_SEED,
        "calibration_context": CALIBRATION_CONTEXT_SEED,
        "evaluation_context": EVALUATION_CONTEXT_SEED,
        "calibration_path": CALIBRATION_PATH_SEED,
        "evaluation_path": EVALUATION_PATH_SEED,
        "stress_path": STRESS_PATH_SEED,
        "random_ray": RANDOM_RAY_SEED,
    }
    if not type_strict_equal(receipt.get("bank_seeds"), expected_seeds):
        raise RuntimeError("root protocol receipt bank seeds mismatch")
    if not type_strict_equal(receipt.get("artifact_paths"), expected_relative_paths):
        raise RuntimeError("root protocol receipt artifact paths mismatch")
    if not type_strict_equal(receipt.get("artifact_sha256"), expected_hashes):
        raise RuntimeError("root protocol receipt artifact hashes mismatch")
    if not type_strict_equal(
        receipt.get("source_provenance"),
        {
            "source_archive_sha256": EXPECTED_ARCHIVE_SHA256,
            "source_package_manifest_sha256": EXPECTED_PACKAGE_MANIFEST_SHA256,
        },
    ):
        raise RuntimeError("root protocol receipt source provenance mismatch")
    if (
        receipt.get("manifest_freeze_receipt_sha256")
        != manifest["freeze_receipt_sha256"]
    ):
        raise RuntimeError("root protocol receipt manifest digest mismatch")
    digest_payload = dict(receipt)
    claimed_receipt_sha = digest_payload.pop("receipt_sha256")
    if claimed_receipt_sha != canonical_json_digest(digest_payload):
        raise RuntimeError("root protocol receipt internal digest mismatch")
    return {
        "schema": receipt["schema"],
        "version": receipt["version"],
        "author": receipt["author"],
        "status": receipt["status"],
        "path": ROOT_PROTOCOL_RECEIPT_PATH.name,
        "file_sha256": receipt_file_sha256,
        "receipt_sha256": claimed_receipt_sha,
        "artifact_sha256": expected_hashes,
        "source_provenance": receipt["source_provenance"],
    }


def validate_static_review_release(
    review: Mapping[str, Any],
    *,
    protocol_sha256: str,
    theoretical_framework_sha256: str,
    implementation_sha256: str,
    test_sha256: str,
    machine_contract_sha256: str,
    manifest_file_sha256: str,
    manifest_freeze_receipt_sha256: str,
) -> None:
    """Require one exact, deterministic all-PASS static-review release."""

    required_keys = {
        "schema",
        "version",
        "author",
        "status",
        "protocol_sha256",
        "theoretical_framework_sha256",
        "implementation_sha256",
        "test_sha256",
        "machine_contract_sha256",
        "manifest_file_sha256",
        "manifest_freeze_receipt_sha256",
        "checks",
    }
    if set(review) != required_keys:
        raise RuntimeError("static review release has an unexpected key set")
    if (
        review.get("schema")
        != "komorebi.neuralese.semantic_retraction.static_review.v1"
        or review.get("version") != VERSION
        or review.get("author") != AUTHOR
        or review.get("status") != "PASS"
    ):
        raise RuntimeError("static review release metadata is invalid")
    expected_hashes = {
        "protocol_sha256": protocol_sha256,
        "theoretical_framework_sha256": theoretical_framework_sha256,
        "implementation_sha256": implementation_sha256,
        "test_sha256": test_sha256,
        "machine_contract_sha256": machine_contract_sha256,
        "manifest_file_sha256": manifest_file_sha256,
        "manifest_freeze_receipt_sha256": manifest_freeze_receipt_sha256,
    }
    if any(review.get(key) != value for key, value in expected_hashes.items()):
        raise RuntimeError("static review release artifact hashes mismatch")
    expected_checks = {name: True for name in REQUIRED_STATIC_REVIEW_CHECKS}
    checks = review.get("checks")
    if (
        not type_strict_equal(checks, expected_checks)
        or not isinstance(checks, dict)
        or any(checks.get(name) is not True for name in REQUIRED_STATIC_REVIEW_CHECKS)
    ):
        raise RuntimeError("static review release required checks are not exact all-PASS")


def assert_protocol_frozen(
    protocol_path: Path = PROTOCOL_PATH,
    machine_contract_path: Path = MACHINE_CONTRACT_PATH,
    review_release_path: Path = STATIC_REVIEW_RELEASE_PATH,
    manifest_path: Path = MANIFEST_DRY_RUN_PATH,
    package: Path = DEFAULT_PACKAGE,
) -> dict[str, Any]:
    """Fail closed until frozen bytes and a post-test static review both agree."""

    contract, machine_contract_sha256, _ = read_json_snapshot(
        machine_contract_path, label="machine protocol contract"
    )
    if contract.get("status") != "FROZEN_POSTHOC":
        raise RuntimeError("protocol is not frozen; learned checkpoints must not be evaluated")
    validate_protocol_matches_runtime(contract)
    protocol_bytes, actual_protocol_sha = read_file_snapshot(
        protocol_path, label="normative analysis protocol"
    )
    protocol_header_lines = protocol_bytes.decode("utf-8").splitlines()[:8]
    freeze_header_lines = [
        line for line in protocol_header_lines if line.startswith("Freeze state:")
    ]
    if freeze_header_lines != [REQUIRED_FROZEN_PROTOCOL_HEADER]:
        raise RuntimeError("normative protocol does not carry the exact frozen header")
    if contract.get("normative_protocol_sha256") != actual_protocol_sha:
        raise RuntimeError("normative protocol bytes do not match the frozen runtime contract")
    manifest = assert_manifest_matches_runtime(
        manifest_path, package=package
    )
    if review_release_path.is_symlink() or not review_release_path.is_file():
        raise RuntimeError("static review release is absent; learned evaluation remains locked")
    review, review_file_sha256, _ = read_json_snapshot(
        review_release_path, label="static review release"
    )
    _, implementation_sha = read_file_snapshot(
        Path(__file__).resolve(), label="primary implementation"
    )
    _, test_sha = read_file_snapshot(TEST_PATH, label="primary test suite")
    _, theoretical_framework_sha256 = read_file_snapshot(
        THEORETICAL_FRAMEWORK_PATH, label="theoretical framework"
    )
    validate_static_review_release(
        review,
        protocol_sha256=actual_protocol_sha,
        theoretical_framework_sha256=theoretical_framework_sha256,
        implementation_sha256=implementation_sha,
        test_sha256=test_sha,
        machine_contract_sha256=machine_contract_sha256,
        manifest_file_sha256=manifest["file_sha256"],
        manifest_freeze_receipt_sha256=manifest["freeze_receipt_sha256"],
    )
    root_receipt = validate_root_protocol_receipt(manifest)
    expected_snapshot_hashes = {
        "analysis_protocol": actual_protocol_sha,
        "primary_implementation": implementation_sha,
        "primary_tests": test_sha,
        "primary_machine_contract": machine_contract_sha256,
        "primary_manifest_dry_run": manifest["file_sha256"],
        "primary_static_review": review_file_sha256,
        "theoretical_framework": theoretical_framework_sha256,
    }
    for name, expected_sha256 in expected_snapshot_hashes.items():
        if root_receipt["artifact_sha256"].get(name) != expected_sha256:
            raise RuntimeError(
                f"root receipt differs from interpreted frozen snapshot: {name}"
            )
    return {
        "contract": contract,
        "protocol_sha256": actual_protocol_sha,
        "implementation_sha256": implementation_sha,
        "test_sha256": test_sha,
        "machine_contract_sha256": machine_contract_sha256,
        "static_review_file_sha256": review_file_sha256,
        "manifest": manifest,
        "review": review,
        "root_protocol_receipt": root_receipt,
    }


def build_independent_claim_matrix(
    one_shot: Mapping[str, Any], periodic: Mapping[str, Any]
) -> dict[str, Any]:
    """Combine prespecified gate booleans without imposing a claim hierarchy."""

    def literal_bool(value: Any, *, label: str) -> bool:
        if type(value) is not bool:
            raise RuntimeError(f"claim gate {label} is not a literal boolean")
        return value

    one = one_shot["fixed_gate_inputs"]
    periodic_behavior = periodic["fixed_behavioral_gate_inputs"]
    native_or_oracle_records = {
        "native coverage": one.get(
            "native_finite_decision_trace_agreement_h4_coverage_0_99"
        ),
        "native logit": one.get("native_finite_logit_trace_agreement_h4_p95"),
        "oracle anchor": one.get("oracle", {}).get("oracle_anchor"),
        "oracle prototype": one.get("oracle", {}).get("oracle_prototype"),
    }
    for label, record in native_or_oracle_records.items():
        if not isinstance(record, Mapping):
            raise RuntimeError(f"claim gate {label} is absent or malformed")
        literal_bool(record.get("pass"), label=label)
    autonomous_one_shot: dict[str, Any] = {}
    for condition, record in one.get("autonomous", {}).items():
        if not isinstance(record, Mapping):
            raise RuntimeError(f"autonomous one-shot gate is malformed: {condition}")
        autonomous_one_shot[condition] = {
            "pass": literal_bool(
                record.get("pass"), label=f"autonomous one-shot {condition}"
            ),
            "gate_inputs": record,
        }
    autonomous_periodic: dict[str, Any] = {}
    for condition in ("self_anchor", "nearest_anchor", "self_prototype"):
        structural = one.get("autonomous", {}).get(condition, {})
        behavior = periodic_behavior[condition]
        behavioral_pass = literal_bool(
            behavior.get("behavioral_pass"),
            label=f"autonomous periodic behavior {condition}",
        )
        structural_pass = literal_bool(
            structural.get("structural_prerequisites_pass"),
            label=f"autonomous periodic structure {condition}",
        )
        state_specificity = structural.get("state_specificity", {})
        if not isinstance(state_specificity, Mapping):
            raise RuntimeError(
                f"autonomous periodic state specificity is malformed: {condition}"
            )
        state_specificity_pass = literal_bool(
            state_specificity.get("pass"),
            label=f"autonomous periodic specificity {condition}",
        )
        random_margin = structural.get("accuracy_margin_over_random_ray")
        if type(random_margin) not in (int, float) or not math.isfinite(
            float(random_margin)
        ):
            raise RuntimeError(
                f"autonomous random margin is not a finite real number: {condition}"
            )
        random_control_pass = bool(float(random_margin) >= 0.20)
        passed = bool(
            behavioral_pass
            and structural_pass
            and state_specificity_pass
            and random_control_pass
        )
        autonomous_periodic[condition] = {
            "behavioral_gate": behavior,
            "structural_prerequisites_pass": structural_pass,
            "state_specificity": state_specificity,
            "accuracy_margin_over_random_ray": random_margin,
            "random_control_pass": random_control_pass,
            "pass": passed,
        }
    return {
        "labels_are_independent_not_hierarchical": True,
        "NATIVE_FINITE_DECISION_TRACE_AGREEMENT_H4_COVERAGE_0.99": one.get(
            "native_finite_decision_trace_agreement_h4_coverage_0_99"
        ),
        "NATIVE_FINITE_LOGIT_TRACE_AGREEMENT_H4_P95": one.get(
            "native_finite_logit_trace_agreement_h4_p95"
        ),
        "ORACLE_ANCHOR_SEMANTIC_REPAIR_INTERFACE": one.get("oracle", {}).get(
            "oracle_anchor"
        ),
        "ORACLE_PROTOTYPE_SEMANTIC_REPAIR_INTERFACE": one.get("oracle", {}).get(
            "oracle_prototype"
        ),
        **{
            f"AUTONOMOUS_ONE_SHOT_RETRACTION__{condition.upper()}": record
            for condition, record in autonomous_one_shot.items()
        },
        **{
            f"AUTONOMOUS_PERIODIC_DEPTH_REPAIR__{condition.upper()}": record
            for condition, record in autonomous_periodic.items()
        },
        "PERIODIC_ANCHOR_SPAN_PROJECTION_REPAIR": {
            "behavioral_gate": periodic_behavior["anchor_projection"],
            "pass": literal_bool(
                periodic_behavior["anchor_projection"].get("behavioral_pass"),
                label="periodic anchor projection",
            ),
            "ambient_ablation_only": True,
            "semantic_retraction_label_eligible": False,
        },
        "qualification": (
            "All native trace labels are finite-bank empirical coverage statements; "
            "none assert universal trace equivalence."
        ),
    }


def aggregate_arm_claim_matrices(
    checkpoint_summaries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require every arm-level label to pass independently in all three seeds."""

    required_arms = (
        "euclidean_supervised",
        "euclidean_cr",
        "polar_supervised",
        "polar_cr",
    )
    required_seeds = (101, 211, 307)
    required_cells = {
        (arm, seed) for arm in required_arms for seed in required_seeds
    }
    if any(
        not isinstance(record, Mapping)
        or type(record.get("arm")) is not str
        or type(record.get("seed")) is not int
        for record in checkpoint_summaries
    ):
        raise RuntimeError("arm aggregation cell identifiers have invalid types")
    actual_cells = [
        (record["arm"], record["seed"]) for record in checkpoint_summaries
    ]
    if len(actual_cells) != 12 or set(actual_cells) != required_cells:
        raise RuntimeError("arm aggregation requires the exact unique 4 x 3 panel")
    output: dict[str, Any] = {}
    for arm in required_arms:
        arm_records = [
            record for record in checkpoint_summaries if record["arm"] == arm
        ]
        by_seed = {
            record["seed"]: record
            for record in arm_records
        }
        if len(arm_records) != 3 or set(by_seed) != set(required_seeds):
            raise RuntimeError(f"arm {arm} does not have exactly seeds 101, 211, 307")
        matrices = {
            seed: by_seed[seed]["independent_claim_matrix"] for seed in required_seeds
        }
        label_sets = [
            {
                key
                for key, value in matrix.items()
                if isinstance(value, Mapping) and "pass" in value
            }
            for matrix in matrices.values()
        ]
        required_labels = set(REQUIRED_PASS_BEARING_CLAIM_LABELS)
        if not label_sets or any(labels != required_labels for labels in label_sets):
            raise RuntimeError(f"arm {arm} does not have the exact frozen claim labels")
        for seed, matrix in matrices.items():
            for label in REQUIRED_PASS_BEARING_CLAIM_LABELS:
                if type(matrix[label]["pass"]) is not bool:
                    raise RuntimeError(
                        f"arm {arm} seed {seed} label {label} has non-boolean pass"
                    )
        labels: dict[str, Any] = {}
        for label in sorted(required_labels):
            seed_records = {
                str(seed): {
                    "pass": matrices[seed][label]["pass"],
                    "record": matrices[seed][label],
                    "checkpoint_shard": by_seed[seed].get("checkpoint_shard"),
                    "checkpoint_shard_sha256": by_seed[seed].get(
                        "checkpoint_shard_sha256"
                    ),
                }
                for seed in required_seeds
            }
            labels[label] = {
                "aggregation": "logical AND over exactly seeds 101, 211, 307",
                "required_seeds": list(required_seeds),
                "per_seed": seed_records,
                "pass": all(
                    record["pass"] is True for record in seed_records.values()
                ),
            }
        output[arm] = {
            "required_seed_count": 3,
            "required_seeds": list(required_seeds),
            "all_required_seeds_present": True,
            "labels": labels,
        }
    return {
        "target_arm_not_privileged_in_computation": True,
        "claim_rule": "an arm label passes iff every one of its three sealed seeds passes",
        "arms": output,
    }


def _canonical_new_leaf_path(path: Path, *, label: str) -> Path:
    """Resolve a new leaf through a real, existing, symlink-free parent path."""

    absolute = Path(os.path.abspath(os.fspath(path)))
    if not absolute.name:
        raise RuntimeError(f"{label} has no leaf name")
    cursor = absolute.parent
    while True:
        if cursor.is_symlink():
            raise RuntimeError(f"{label} has symbolic-link ancestry")
        if cursor == cursor.parent:
            break
        cursor = cursor.parent
    if not absolute.parent.is_dir():
        raise RuntimeError(f"{label} parent must already exist")
    return absolute.parent.resolve(strict=True) / absolute.name


def result_bundle_path(output_path: Path) -> Path:
    """Return the canonical learned bundle directory path."""

    return _canonical_new_leaf_path(output_path, label="learned result bundle")


def _path_lexists(path: Path) -> bool:
    return os.path.lexists(os.fspath(path))


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_json_exclusive(path: Path, payload: Mapping[str, Any]) -> str:
    """Atomically publish durable JSON and refuse dangling links or overwrites."""

    path = Path(os.path.abspath(os.fspath(path)))
    parent = path.parent
    if parent.is_symlink() or not parent.is_dir():
        raise RuntimeError(f"JSON output parent is absent or symbolic: {parent}")
    if _path_lexists(path):
        raise FileExistsError(f"refusing to overwrite JSON artifact: {path}")
    temporary = parent / f".{path.name}.tmp.{os.getpid()}.{time.time_ns()}"
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        # A hard-link publication is atomic and fails at the kernel boundary if
        # another process created the target after our lexists check.
        os.link(temporary, path, follow_symlinks=False)
        _fsync_directory(parent)
    finally:
        if _path_lexists(temporary):
            temporary.unlink()
            _fsync_directory(parent)
    return sha256_file(path)


class _CountingTextWriter:
    def __init__(self) -> None:
        self.byte_count = 0

    def write(self, value: str) -> int:
        self.byte_count += len(value.encode("utf-8"))
        return len(value)


def assert_json_serializable_within_limit(
    payload: Mapping[str, Any], maximum_bytes: int, *, label: str
) -> int:
    counter = _CountingTextWriter()
    json.dump(payload, counter, indent=2, sort_keys=True, allow_nan=False)
    counter.write("\n")
    if counter.byte_count > int(maximum_bytes):
        raise RuntimeError(
            f"{label} serialized size {counter.byte_count} exceeds {maximum_bytes}"
        )
    return counter.byte_count


def _protected_primary_artifact_paths() -> tuple[Path, ...]:
    return tuple(
        Path(os.path.abspath(os.fspath(path)))
        for path in (
            Path(__file__).resolve(),
            PROTOCOL_PATH,
            THEORETICAL_FRAMEWORK_PATH,
            ROOT_PROTOCOL_RECEIPT_PATH,
            MACHINE_CONTRACT_PATH,
            STATIC_REVIEW_RELEASE_PATH,
            MANIFEST_DRY_RUN_PATH,
            TEST_PATH,
            EVALUATION_BANK_SPEND_PATH,
            DEFAULT_RESULT_BUNDLE,
        )
    )


def assert_safe_control_output_path(
    output_path: Path, *, package: Path = DEFAULT_PACKAGE
) -> Path:
    output = _canonical_new_leaf_path(output_path, label="control output")
    if _path_lexists(output):
        raise FileExistsError(f"control output already exists: {output}")
    if output in set(_protected_primary_artifact_paths()):
        raise RuntimeError("control output aliases a protected protocol artifact")
    if any(
        parent.suffix == REQUIRED_RESULT_BUNDLE_SUFFIX
        for parent in (output, *output.parents)
    ):
        raise RuntimeError("control output may not be placed in a result bundle")
    sealed_package = package.resolve(strict=True)
    if output.is_relative_to(sealed_package):
        raise RuntimeError("control output may not modify the selected sealed package")
    if output.parent.is_symlink() or not output.parent.is_dir():
        raise RuntimeError("control output parent must be an existing real directory")
    if not os.access(output.parent, os.W_OK | os.X_OK):
        raise PermissionError("control output parent is not writable")
    return output


def assert_fresh_learned_output_paths(
    output_path: Path,
    *,
    spend_path: Path = EVALUATION_BANK_SPEND_PATH,
) -> Path:
    """Fail closed if this evaluation bank may already have been exposed."""

    bundle_path = result_bundle_path(output_path)
    if bundle_path.suffix != REQUIRED_RESULT_BUNDLE_SUFFIX:
        raise RuntimeError(
            f"learned output must end in {REQUIRED_RESULT_BUNDLE_SUFFIX}"
        )
    if any(
        parent.suffix == REQUIRED_RESULT_BUNDLE_SUFFIX
        for parent in bundle_path.parents
    ):
        raise RuntimeError("learned result bundles may not be nested")
    spend_path = _canonical_new_leaf_path(
        spend_path, label="external evaluation-bank spend marker"
    )
    canonical_spend = _canonical_new_leaf_path(
        EVALUATION_BANK_SPEND_PATH,
        label="canonical evaluation-bank spend marker",
    )
    if spend_path != canonical_spend:
        raise RuntimeError("production learned runs must use the global spend marker")
    if bundle_path == spend_path or bundle_path in set(
        _protected_primary_artifact_paths()
    ) - {DEFAULT_RESULT_BUNDLE}:
        raise RuntimeError("learned bundle aliases a protected protocol artifact")
    if bundle_path.parent.is_symlink() or not bundle_path.parent.is_dir():
        raise RuntimeError("learned bundle parent must be an existing real directory")
    if not os.access(bundle_path.parent, os.W_OK | os.X_OK):
        raise PermissionError("learned bundle parent is not writable")
    collisions = [str(path) for path in (spend_path, bundle_path) if _path_lexists(path)]
    if collisions:
        raise RuntimeError(
            "prospective learned execution refused because a spend/output artifact "
            f"already exists: {collisions}"
        )
    return bundle_path


def reserve_result_bundle(bundle_path: Path) -> None:
    """Atomically reserve the complete learned-output namespace before spend."""

    bundle_path.mkdir(mode=0o755, exist_ok=False)
    _fsync_directory(bundle_path.parent)


def assert_manifest_budget_and_disk_headroom(
    freeze: Mapping[str, Any], bundle_path: Path
) -> dict[str, Any]:
    """Fail before bank spend unless frozen resource bounds are internally valid."""

    budget = freeze["manifest"]["budget"]
    required_exact = {
        "maximum_checkpoint_shard_bytes": MAXIMUM_CHECKPOINT_SHARD_BYTES,
        "maximum_exact_control_bytes": MAXIMUM_EXACT_CONTROL_BYTES,
        "maximum_bundle_metadata_bytes": MAXIMUM_BUNDLE_METADATA_BYTES,
        "result_disk_safety_margin_bytes": RESULT_DISK_SAFETY_MARGIN_BYTES,
        "minimum_free_disk_bytes_before_spend": MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND,
        "result_bundle_file_count": 17,
    }
    if any(budget.get(key) != value for key, value in required_exact.items()):
        raise RuntimeError("frozen manifest result-publication budget mismatch")
    if budget.get("chunk_ceiling_pass") is not True:
        raise RuntimeError("frozen manifest chunk budget did not pass")
    if budget.get("estimated_peak_within_declared_ceiling") is not True:
        raise RuntimeError("frozen manifest peak-memory estimate did not pass")
    if (
        int(budget.get("maximum_starting_state_chunk", -1))
        > int(budget.get("required_chunk_ceiling", -1))
        or int(budget.get("estimated_peak_working_set_bytes", -1))
        > int(budget.get("declared_peak_working_set_ceiling_bytes", -1))
    ):
        raise RuntimeError("frozen manifest resource inequalities are inconsistent")
    disk = shutil.disk_usage(bundle_path.parent)
    if disk.free < MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND:
        raise RuntimeError(
            "insufficient free disk before evaluation-bank spend: "
            f"{disk.free} < {MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND}"
        )
    return {
        "free_bytes_before_spend": int(disk.free),
        "required_free_bytes_before_spend": MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND,
        "headroom_pass": True,
        "manifest_budget_checks_pass": True,
    }


def create_evaluation_bank_spend_receipt(
    *,
    bundle_path: Path,
    freeze: Mapping[str, Any],
    context_banks: Mapping[str, ContextBank],
    path_banks: Mapping[str, Any],
    continuations: ContinuationBank,
    random_manifest: Mapping[str, Any],
    exact_control_sha256: str,
    spend_path: Path = EVALUATION_BANK_SPEND_PATH,
) -> tuple[dict[str, Any], str]:
    """Irrevocably spend the bank before the first learned evaluation occurs."""

    bundle_path = result_bundle_path(bundle_path)
    spend_path = _canonical_new_leaf_path(
        spend_path, label="external evaluation-bank spend marker"
    )
    canonical_spend_path = _canonical_new_leaf_path(
        EVALUATION_BANK_SPEND_PATH,
        label="canonical evaluation-bank spend marker",
    )
    if spend_path != canonical_spend_path:
        raise RuntimeError("production learned runs must use the global spend marker")
    if _path_lexists(spend_path):
        raise RuntimeError("evaluation bank is already spent")
    if bundle_path.is_symlink() or not bundle_path.is_dir():
        raise RuntimeError("result bundle was not atomically reserved before spend")
    if {entry.name for entry in bundle_path.iterdir()} != {
        CHECKPOINT_DIRECTORY_NAME,
        EXACT_CONTROL_FILENAME,
    }:
        raise RuntimeError("reserved result bundle pre-spend layout is incomplete")
    checkpoint_directory = bundle_path / CHECKPOINT_DIRECTORY_NAME
    if (
        checkpoint_directory.is_symlink()
        or not checkpoint_directory.is_dir()
        or any(checkpoint_directory.iterdir())
    ):
        raise RuntimeError("checkpoint shard directory is not empty before spend")
    receipt = {
        "schema": "komorebi.neuralese.evaluation_bank_spend.v1",
        "version": VERSION,
        "author": AUTHOR,
        "status": "SPENT_BEFORE_FIRST_LEARNED_EVALUATION",
        "created_unix_time_ns": time.time_ns(),
        "no_rerun_or_resume_is_prospective": True,
        "crash_after_this_receipt_still_spends_bank": True,
        "planned_bundle_leaf_name": bundle_path.name,
        "planned_bundle_absolute_path_non_normative": str(bundle_path),
        "protocol_sha256": freeze["protocol_sha256"],
        "implementation_sha256": freeze["implementation_sha256"],
        "test_sha256": freeze["test_sha256"],
        "machine_contract_sha256": freeze["machine_contract_sha256"],
        "manifest_file_sha256": freeze["manifest"]["file_sha256"],
        "manifest_freeze_receipt_sha256": freeze["manifest"][
            "freeze_receipt_sha256"
        ],
        "static_review_file_sha256": freeze["root_protocol_receipt"][
            "artifact_sha256"
        ]["primary_static_review"],
        "theoretical_framework_sha256": freeze["root_protocol_receipt"][
            "artifact_sha256"
        ]["theoretical_framework"],
        "root_protocol_receipt_file_sha256": freeze["root_protocol_receipt"][
            "file_sha256"
        ],
        "root_protocol_receipt_internal_sha256": freeze[
            "root_protocol_receipt"
        ]["receipt_sha256"],
        "source_archive_sha256": freeze["root_protocol_receipt"][
            "source_provenance"
        ]["source_archive_sha256"],
        "source_package_manifest_sha256": freeze["root_protocol_receipt"][
            "source_provenance"
        ]["source_package_manifest_sha256"],
        "evaluation_context_sha256": context_banks["evaluation"].receipt["sha256"],
        "evaluation_path_sha256": path_banks["evaluation"].receipt["sha256"],
        "continuation_sha256": continuations.receipt["sha256"],
        "random_key_manifest_sha256": random_manifest["sha256"],
        "exact_control_sha256": exact_control_sha256,
    }
    receipt["receipt_sha256"] = canonical_json_digest(receipt)
    # The global marker is authoritative: publish and fsync it first so every
    # subsequent failure leaves the evaluation bank durably spent.
    external_sha = _write_json_exclusive(spend_path, receipt)
    internal_sha = _write_json_exclusive(
        bundle_path / SPEND_RECEIPT_FILENAME, receipt
    )
    if internal_sha != external_sha:
        raise RuntimeError("internal and external spend receipts differ")
    return receipt, external_sha


def _bundle_member(bundle_path: Path, relative: str) -> Path:
    if not isinstance(relative, str) or "\\" in relative:
        raise RuntimeError("bundle member path is not portable POSIX text")
    member = PurePosixPath(relative)
    if (
        member.is_absolute()
        or not member.parts
        or any(part in ("", ".", "..") for part in member.parts)
        or member.as_posix() != relative
    ):
        raise RuntimeError(f"bundle member path escapes or is noncanonical: {relative}")
    target = bundle_path.joinpath(*member.parts)
    resolved = target.resolve(strict=True)
    if not resolved.is_relative_to(bundle_path.resolve(strict=True)):
        raise RuntimeError(f"bundle member resolves outside bundle: {relative}")
    cursor = target
    while cursor != bundle_path:
        if cursor.is_symlink():
            raise RuntimeError(f"symbolic links are forbidden in bundle: {relative}")
        cursor = cursor.parent
    if not target.is_file():
        raise RuntimeError(f"bundle member is not a regular file: {relative}")
    return target


def _expected_checkpoint_shards() -> dict[str, tuple[str, int]]:
    return {
        f"{CHECKPOINT_DIRECTORY_NAME}/{arm}__seed_{seed}.json": (arm, seed)
        for arm in REQUIRED_ARMS
        for seed in REQUIRED_SEEDS
    }


def _assert_exact_bundle_census(
    bundle_path: Path, expected_shards: Mapping[str, tuple[str, int]]
) -> None:
    """Require the exact regular, non-link bundle tree at one instant."""

    expected_root_entries = {
        RUN_FILENAME,
        EXACT_CONTROL_FILENAME,
        SPEND_RECEIPT_FILENAME,
        BUNDLE_MANIFEST_FILENAME,
        COMMIT_FILENAME,
        CHECKPOINT_DIRECTORY_NAME,
    }
    root_entries = list(bundle_path.iterdir())
    if {entry.name for entry in root_entries} != expected_root_entries:
        raise RuntimeError("result bundle has missing or extra root entries")
    checkpoint_dir = bundle_path / CHECKPOINT_DIRECTORY_NAME
    for entry in root_entries:
        if entry.is_symlink():
            raise RuntimeError(f"symbolic link forbidden in result bundle: {entry.name}")
        if entry == checkpoint_dir:
            if not entry.is_dir():
                raise RuntimeError("checkpoint shard directory is not a directory")
        elif not entry.is_file():
            raise RuntimeError(f"bundle root member is not a regular file: {entry.name}")
    shard_entries = list(checkpoint_dir.iterdir())
    actual_shards = {
        f"{CHECKPOINT_DIRECTORY_NAME}/{entry.name}" for entry in shard_entries
    }
    if actual_shards != set(expected_shards):
        raise RuntimeError("checkpoint shard directory is not the exact 4 x 3 census")
    if any(entry.is_symlink() or not entry.is_file() for entry in shard_entries):
        raise RuntimeError("checkpoint shard entries must be regular non-link files")


def verify_result_bundle(
    bundle_path: Path,
    *,
    external_spend_path: Path | None = None,
) -> dict[str, Any]:
    """Verify a committed bundle without trusting any path stored inside it."""

    external_spend_marker_checked = external_spend_path is not None
    bundle_path = result_bundle_path(bundle_path)
    if bundle_path.suffix != REQUIRED_RESULT_BUNDLE_SUFFIX:
        raise RuntimeError(
            f"committed result bundle must end in {REQUIRED_RESULT_BUNDLE_SUFFIX}"
        )
    if any(
        parent.suffix == REQUIRED_RESULT_BUNDLE_SUFFIX
        for parent in bundle_path.parents
    ):
        raise RuntimeError("committed result bundles may not be nested")
    if bundle_path.is_symlink() or not bundle_path.is_dir():
        raise RuntimeError("result bundle is absent, symbolic, or not a directory")
    expected_shards = _expected_checkpoint_shards()
    _assert_exact_bundle_census(bundle_path, expected_shards)

    commit_path = _bundle_member(bundle_path, COMMIT_FILENAME)
    run_path = _bundle_member(bundle_path, RUN_FILENAME)
    exact_path = _bundle_member(bundle_path, EXACT_CONTROL_FILENAME)
    spend_member_path = _bundle_member(bundle_path, SPEND_RECEIPT_FILENAME)
    manifest_path = _bundle_member(bundle_path, BUNDLE_MANIFEST_FILENAME)
    if exact_path.stat().st_size > MAXIMUM_EXACT_CONTROL_BYTES:
        raise RuntimeError("committed exact-control file exceeds frozen byte ceiling")
    metadata_size = sum(
        path.stat().st_size
        for path in (commit_path, run_path, spend_member_path, manifest_path)
    )
    if metadata_size > MAXIMUM_BUNDLE_METADATA_BYTES:
        raise RuntimeError("committed bundle metadata exceeds frozen byte ceiling")
    for shard_relative in expected_shards:
        if (
            _bundle_member(bundle_path, shard_relative).stat().st_size
            > MAXIMUM_CHECKPOINT_SHARD_BYTES
        ):
            raise RuntimeError(f"checkpoint shard exceeds byte ceiling: {shard_relative}")

    commit_bytes, commit_sha256 = read_file_snapshot(
        commit_path, label="result COMMIT"
    )
    commit = loads_json_bytes_strict(commit_bytes)
    if not isinstance(commit, Mapping) or set(commit) != {
        "schema",
        "version",
        "author",
        "status",
        "result_validity",
        "run",
        "bundle_manifest",
        "exact_control",
        "spend_receipt",
        "checkpoint_shard_count",
    }:
        raise RuntimeError("result COMMIT has an unexpected key set")
    if (
        commit.get("schema")
        != "komorebi.neuralese.semantic_retraction_result_commit.v1"
        or commit.get("version") != VERSION
        or commit.get("author") != AUTHOR
        or commit.get("status") != "COMMITTED"
        or commit.get("result_validity") != "VALID_ONLY_WITH_THIS_COMMIT"
        or type(commit.get("checkpoint_shard_count")) is not int
        or commit.get("checkpoint_shard_count") != 12
    ):
        raise RuntimeError("result COMMIT metadata is invalid")

    descriptor_specs = {
        "run": RUN_FILENAME,
        "bundle_manifest": BUNDLE_MANIFEST_FILENAME,
        "exact_control": EXACT_CONTROL_FILENAME,
        "spend_receipt": SPEND_RECEIPT_FILENAME,
    }
    loaded: dict[str, Any] = {}
    loaded_bytes: dict[str, bytes] = {}
    verified_member_hashes: dict[str, str] = {COMMIT_FILENAME: commit_sha256}
    for key, expected_relative in descriptor_specs.items():
        descriptor = commit.get(key)
        if not isinstance(descriptor, Mapping) or set(descriptor) != {"path", "sha256"}:
            raise RuntimeError(f"invalid COMMIT descriptor: {key}")
        if descriptor["path"] != expected_relative:
            raise RuntimeError(f"noncanonical COMMIT path: {key}")
        path = _bundle_member(bundle_path, descriptor["path"])
        payload_bytes, actual_sha256 = read_file_snapshot(
            path,
            label=f"committed bundle member {descriptor['path']}",
            maximum_bytes=(
                MAXIMUM_EXACT_CONTROL_BYTES
                if key == "exact_control"
                else MAXIMUM_BUNDLE_METADATA_BYTES
            ),
        )
        if actual_sha256 != descriptor["sha256"]:
            raise RuntimeError(f"COMMIT hash mismatch: {key}")
        loaded[key] = loads_json_bytes_strict(payload_bytes)
        loaded_bytes[key] = payload_bytes
        verified_member_hashes[descriptor["path"]] = actual_sha256
    if (
        len(commit_bytes)
        + len(loaded_bytes["run"])
        + len(loaded_bytes["bundle_manifest"])
        + len(loaded_bytes["spend_receipt"])
        > MAXIMUM_BUNDLE_METADATA_BYTES
    ):
        raise RuntimeError("bundle metadata grew beyond its byte ceiling during read")

    run = loaded["run"]
    manifest = loaded["bundle_manifest"]
    exact = loaded["exact_control"]
    internal_spend = loaded["spend_receipt"]
    if (
        not isinstance(exact, Mapping)
        or set(exact) != set(REQUIRED_EXACT_CONTROL_KEYS)
        or exact.get("schema")
        != "komorebi.neuralese.semantic_retraction_exact_control.v1"
        or exact.get("version") != VERSION
        or exact.get("author") != AUTHOR
        or exact.get("audit", {}).get("pass") is not True
    ):
        raise RuntimeError("exact-control bundle member is invalid")
    if internal_spend.get("exact_control_sha256") != commit["exact_control"]["sha256"]:
        raise RuntimeError("spend receipt does not bind the exact-control bytes")
    exact_summary = manifest.get("exact_control_summary")
    if (
        not isinstance(exact_summary, Mapping)
        or set(exact_summary)
        != {
            "path",
            "sha256",
            "serialized_bytes",
            "audit",
            "context_bank",
            "path_bank",
            "continuation_bank",
        }
        or exact_summary.get("path") != commit["exact_control"]["path"]
        or exact_summary.get("sha256") != commit["exact_control"]["sha256"]
        or type(exact_summary.get("serialized_bytes")) is not int
        or exact_summary.get("serialized_bytes") != len(loaded_bytes["exact_control"])
        or not type_strict_equal(exact_summary.get("audit"), exact.get("audit"))
        or not type_strict_equal(
            exact_summary.get("context_bank"), exact.get("context_bank")
        )
        or not type_strict_equal(
            exact_summary.get("path_bank"), exact.get("path_bank")
        )
        or not type_strict_equal(
            exact_summary.get("continuation_bank"), exact.get("continuation_bank")
        )
    ):
        raise RuntimeError("exact-control summary does not bind exact-control content")
    del exact
    loaded.pop("exact_control", None)
    loaded_bytes.pop("exact_control", None)
    gc.collect()
    if not isinstance(internal_spend, Mapping) or set(internal_spend) != set(
        REQUIRED_SPEND_RECEIPT_KEYS
    ):
        raise RuntimeError("internal spend receipt has an unexpected key set")
    created_unix_time_ns = internal_spend.get("created_unix_time_ns")
    planned_leaf = internal_spend.get("planned_bundle_leaf_name")
    planned_absolute = internal_spend.get(
        "planned_bundle_absolute_path_non_normative"
    )
    if (
        internal_spend.get("schema")
        != "komorebi.neuralese.evaluation_bank_spend.v1"
        or internal_spend.get("version") != VERSION
        or internal_spend.get("author") != AUTHOR
        or internal_spend.get("status")
        != "SPENT_BEFORE_FIRST_LEARNED_EVALUATION"
        or internal_spend.get("no_rerun_or_resume_is_prospective") is not True
        or internal_spend.get("crash_after_this_receipt_still_spends_bank")
        is not True
        or not isinstance(created_unix_time_ns, int)
        or isinstance(created_unix_time_ns, bool)
        or created_unix_time_ns <= 0
        or not isinstance(planned_leaf, str)
        or "\\" in planned_leaf
        or PurePosixPath(planned_leaf).name != planned_leaf
        or not planned_leaf.endswith(REQUIRED_RESULT_BUNDLE_SUFFIX)
        or not isinstance(planned_absolute, str)
        or not Path(planned_absolute).is_absolute()
        or Path(planned_absolute).name != planned_leaf
        or planned_leaf != bundle_path.name
    ):
        raise RuntimeError("internal spend receipt is invalid")
    spend_digest_payload = dict(internal_spend)
    claimed_spend_digest = spend_digest_payload.pop("receipt_sha256", None)
    if claimed_spend_digest != canonical_json_digest(spend_digest_payload):
        raise RuntimeError("internal spend receipt digest is inconsistent")

    if external_spend_path is not None:
        external_spend_path = _canonical_new_leaf_path(
            external_spend_path, label="external live spend marker"
        )
        if external_spend_path.is_symlink() or not external_spend_path.is_file():
            raise RuntimeError("external live spend marker is absent or symbolic")
        external_spend_bytes, _ = read_file_snapshot(
            external_spend_path,
            label="external live spend marker",
            maximum_bytes=len(loaded_bytes["spend_receipt"]),
        )
        if external_spend_bytes != loaded_bytes["spend_receipt"]:
            raise RuntimeError("external and internal spend markers are not byte-identical")

    required_manifest_keys = {
        "schema",
        "version",
        "author",
        "status",
        "result_validity",
        "run",
        "exact_control",
        "exact_control_summary",
        "spend_receipt",
        "checkpoint_shards",
        "required_checkpoint_cells",
        "arm_level_independent_claim_matrix",
    }
    if not isinstance(manifest, Mapping) or set(manifest) != required_manifest_keys:
        raise RuntimeError("bundle manifest has an unexpected key set")
    if (
        manifest.get("schema")
        != "komorebi.neuralese.semantic_retraction_result_bundle.v1"
        or manifest.get("version") != VERSION
        or manifest.get("author") != AUTHOR
        or manifest.get("status") != "COMPLETE_PENDING_COMMIT"
        or manifest.get("result_validity") != "VALID_ONLY_WITH_COMMIT"
    ):
        raise RuntimeError("bundle manifest metadata is invalid")
    for manifest_key, commit_key in (
        ("run", "run"),
        ("exact_control", "exact_control"),
        ("spend_receipt", "spend_receipt"),
    ):
        if not type_strict_equal(manifest.get(manifest_key), commit[commit_key]):
            raise RuntimeError(f"manifest/COMMIT descriptor mismatch: {manifest_key}")
    required_cells_payload = [
        {"arm": arm, "seed": seed}
        for arm in REQUIRED_ARMS
        for seed in REQUIRED_SEEDS
    ]
    if not type_strict_equal(
        manifest.get("required_checkpoint_cells"), required_cells_payload
    ):
        raise RuntimeError("bundle manifest required-cell census mismatch")

    if (
        not isinstance(run, Mapping)
        or set(run) != set(REQUIRED_RUN_KEYS)
        or run.get("schema") != SCHEMA
        or run.get("version") != VERSION
        or run.get("author") != AUTHOR
        or run.get("analysis_status") != ANALYSIS_STATUS
        or run.get("result_validity") != "VALID_ONLY_WITH_COMMIT"
        or run.get("claim_boundary") != CLAIM_BOUNDARY
    ):
        raise RuntimeError("RUN.json metadata or top-level schema is invalid")
    run_descriptors = run.get("checkpoint_results")
    if not isinstance(run_descriptors, list) or len(run_descriptors) != 12:
        raise RuntimeError("RUN.json does not cite exactly 12 checkpoint results")
    run_by_cell: dict[tuple[str, int], Mapping[str, Any]] = {}
    for row in run_descriptors:
        if not isinstance(row, Mapping) or set(row) != set(
            REQUIRED_CHECKPOINT_SUMMARY_KEYS
        ):
            raise RuntimeError("RUN.json checkpoint summary has an unexpected key set")
        if row.get("whole_analysis_state_dict_unchanged") is not True:
            raise RuntimeError("RUN.json checkpoint state-control flag is not true")
        if type(row.get("arm")) is not str or type(row.get("seed")) is not int:
            raise RuntimeError("RUN.json checkpoint cell identifiers have invalid types")
        cell = (row["arm"], row["seed"])
        if cell not in set(expected_shards.values()):
            raise RuntimeError("RUN.json checkpoint cell is outside the frozen 4 x 3 panel")
        expected_model_family = "polar" if row["arm"].startswith("polar_") else "raw"
        expected_checkpoint_filename = f"{row['arm']}_seed{row['seed']}.pt"
        expected_shard_path = (
            f"{CHECKPOINT_DIRECTORY_NAME}/{row['arm']}__seed_{row['seed']}.json"
        )
        if (
            type(row.get("model_family")) is not str
            or row.get("model_family") != expected_model_family
            or type(row.get("checkpoint_filename")) is not str
            or row.get("checkpoint_filename") != expected_checkpoint_filename
            or not is_sha256_text(row.get("checkpoint_sha256"))
            or type(row.get("checkpoint_shard")) is not str
            or row.get("checkpoint_shard") != expected_shard_path
            or not is_sha256_text(row.get("checkpoint_shard_sha256"))
            or type(row.get("checkpoint_shard_bytes")) is not int
            or row.get("checkpoint_shard_bytes") <= 0
        ):
            raise RuntimeError("RUN.json checkpoint summary metadata is invalid")
        if cell in run_by_cell:
            raise RuntimeError("RUN.json contains a duplicate checkpoint cell")
        run_by_cell[cell] = row

    shard_descriptors = manifest.get("checkpoint_shards")
    if not isinstance(shard_descriptors, list) or len(shard_descriptors) != 12:
        raise RuntimeError("bundle manifest must contain exactly 12 checkpoint shards")
    manifest_cells: set[tuple[str, int]] = set()
    manifest_paths: set[str] = set()
    verified_state_controls: dict[tuple[str, int], Mapping[str, Any]] = {}
    for descriptor in shard_descriptors:
        if not isinstance(descriptor, Mapping) or set(descriptor) != {
            "arm",
            "seed",
            "path",
            "sha256",
        }:
            raise RuntimeError("checkpoint shard descriptor has an unexpected key set")
        relative = descriptor["path"]
        if (
            type(descriptor.get("arm")) is not str
            or type(descriptor.get("seed")) is not int
        ):
            raise RuntimeError("checkpoint shard descriptor cell has invalid types")
        cell = (descriptor["arm"], descriptor["seed"])
        if relative not in expected_shards or expected_shards[relative] != cell:
            raise RuntimeError("checkpoint shard descriptor path/cell mismatch")
        if relative in manifest_paths or cell in manifest_cells:
            raise RuntimeError("duplicate checkpoint shard descriptor")
        shard_path = _bundle_member(bundle_path, relative)
        shard_bytes, shard_sha256 = read_file_snapshot(
            shard_path,
            label=f"checkpoint shard {relative}",
            maximum_bytes=MAXIMUM_CHECKPOINT_SHARD_BYTES,
        )
        if shard_sha256 != descriptor["sha256"]:
            raise RuntimeError(f"checkpoint shard hash mismatch: {relative}")
        shard = loads_json_bytes_strict(shard_bytes)
        if (
            not isinstance(shard, Mapping)
            or set(shard) != set(REQUIRED_CHECKPOINT_SHARD_KEYS)
            or shard.get("schema")
            != "komorebi.neuralese.semantic_retraction_checkpoint_result.v1"
            or shard.get("version") != VERSION
            or shard.get("author") != AUTHOR
            or type(shard.get("arm")) is not str
            or type(shard.get("seed")) is not int
            or (shard.get("arm"), shard.get("seed")) != cell
            or type(shard.get("model_family")) is not str
            or shard.get("model_family")
            != ("polar" if descriptor["arm"].startswith("polar_") else "raw")
            or type(shard.get("checkpoint_filename")) is not str
            or shard.get("checkpoint_filename")
            != f"{descriptor['arm']}_seed{descriptor['seed']}.pt"
            or not is_sha256_text(shard.get("checkpoint_sha256"))
        ):
            raise RuntimeError(f"checkpoint shard metadata mismatch: {relative}")
        state_control = shard.get("whole_analysis_state_dict_control")
        required_state_control_keys = {
            "independent_digest_before",
            "independent_digest_after",
            "seal_compatible_digest_before",
            "seal_compatible_digest_after",
            "sealed_digest",
            "unchanged",
            "seal_match",
        }
        if (
            not isinstance(state_control, Mapping)
            or set(state_control) != required_state_control_keys
            or state_control.get("unchanged") is not True
            or state_control.get("seal_match") is not True
            or not is_sha256_text(state_control.get("independent_digest_before"))
            or not is_sha256_text(state_control.get("seal_compatible_digest_before"))
            or not is_sha256_text(state_control.get("sealed_digest"))
            or state_control.get("independent_digest_before")
            != state_control.get("independent_digest_after")
            or not (
                state_control.get("seal_compatible_digest_before")
                == state_control.get("seal_compatible_digest_after")
                == state_control.get("sealed_digest")
            )
        ):
            raise RuntimeError(f"checkpoint shard state control is invalid: {relative}")
        try:
            recomputed_claim_matrix = build_independent_claim_matrix(
                shard["one_shot_primary"], shard["periodic"]
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(
                f"checkpoint shard lacks valid claim inputs: {relative}"
            ) from exc
        if not type_strict_equal(
            shard.get("independent_claim_matrix"), recomputed_claim_matrix
        ):
            raise RuntimeError(
                f"checkpoint shard claim matrix differs from gate inputs: {relative}"
            )
        run_row = run_by_cell.get(cell)
        if run_row is None or any(
            not type_strict_equal(shard.get(key), run_row.get(key))
            for key in (
                "checkpoint_filename",
                "checkpoint_sha256",
                "model_family",
                "independent_claim_matrix",
            )
        ):
            raise RuntimeError(f"checkpoint shard/RUN cross-link mismatch: {relative}")
        if (
            type(run_row.get("checkpoint_shard_bytes")) is not int
            or run_row.get("checkpoint_shard_bytes") != len(shard_bytes)
        ):
            raise RuntimeError(f"checkpoint shard byte-count mismatch: {relative}")
        manifest_paths.add(relative)
        manifest_cells.add(cell)
        verified_state_controls[cell] = state_control
        verified_member_hashes[relative] = shard_sha256
        del shard_bytes
        del shard
        gc.collect()
        assert_peak_memory_within_budget()
    if manifest_paths != set(expected_shards) or manifest_cells != set(
        expected_shards.values()
    ):
        raise RuntimeError("checkpoint shard manifest does not cover exact 4 x 3 panel")

    run_index = {
        (str(row["arm"]), int(row["seed"])): (
            row.get("checkpoint_shard"),
            row.get("checkpoint_shard_sha256"),
        )
        for row in run_descriptors
    }
    manifest_index = {
        (str(row["arm"]), int(row["seed"])): (row["path"], row["sha256"])
        for row in shard_descriptors
    }
    if not type_strict_equal(run_index, manifest_index):
        raise RuntimeError("RUN.json checkpoint index differs from bundle manifest")
    if not type_strict_equal(
        run.get("exact_compiled_control"), manifest.get("exact_control_summary")
    ):
        raise RuntimeError("RUN.json exact-control receipt differs from bundle manifest")
    if not type_strict_equal(
        run.get("evaluation_bank_spend_receipt"), internal_spend
    ):
        raise RuntimeError("RUN.json spend receipt differs from bundle member")
    if not type_strict_equal(
        run.get("arm_level_independent_claim_matrix"),
        manifest.get("arm_level_independent_claim_matrix"),
    ):
        raise RuntimeError("RUN.json arm aggregation differs from bundle manifest")
    recomputed_arm_matrix = aggregate_arm_claim_matrices(run_descriptors)
    if not type_strict_equal(
        run.get("arm_level_independent_claim_matrix"), recomputed_arm_matrix
    ):
        raise RuntimeError("committed arm aggregation is not the exact three-seed AND")

    source = run.get("source")
    required_source_keys = {
        "archive_filename",
        "archive_absolute_path_non_normative",
        "archive_sha256",
        "archive_verified",
        "package_source_integrity",
        "sealed_import_origin_receipt",
        "checkpoint_seal_sha256",
        "checkpoint_seal_manifest_binding",
        "official_checkpoint_count",
        "seal_receipt_count",
        "all_checkpoint_receipts_verified",
        "all_checkpoint_files_bound_to_sealed_package_manifest",
        "weights_only_load",
        "checkpoint_load_bound_to_prehashed_bytes",
        "strict_state_load",
        "one_model_loaded_at_a_time",
        "closing_provenance_reverification",
    }
    if not isinstance(source, Mapping) or set(source) != required_source_keys:
        raise RuntimeError("RUN source has an unexpected key set")
    archive_filename = source.get("archive_filename")
    archive_absolute = source.get("archive_absolute_path_non_normative")
    if (
        type(archive_filename) is not str
        or not archive_filename
        or "\\" in archive_filename
        or PurePosixPath(archive_filename).name != archive_filename
        or type(archive_absolute) is not str
        or not Path(archive_absolute).is_absolute()
        or Path(archive_absolute).name != archive_filename
    ):
        raise RuntimeError("RUN source archive naming metadata is invalid")

    import_receipt = source.get("sealed_import_origin_receipt")
    required_import_receipt_keys = {
        "sealed_source_root_forced_to_sys_path_zero",
        "loaded_module_count",
        "loaded_modules",
        "ordered_loaded_module_receipt_sha256",
    }
    if (
        not isinstance(import_receipt, Mapping)
        or set(import_receipt) != required_import_receipt_keys
        or import_receipt.get("sealed_source_root_forced_to_sys_path_zero") is not True
        or type(import_receipt.get("loaded_module_count")) is not int
        or import_receipt.get("loaded_module_count") <= 0
        or not isinstance(import_receipt.get("loaded_modules"), list)
        or len(import_receipt["loaded_modules"])
        != import_receipt["loaded_module_count"]
        or not is_sha256_text(
            import_receipt.get("ordered_loaded_module_receipt_sha256")
        )
    ):
        raise RuntimeError("RUN sealed-import origin receipt is invalid")
    loaded_module_names: set[str] = set()
    loaded_module_order: list[str] = []
    loaded_module_digest = hashlib.sha256()
    for module_record in import_receipt["loaded_modules"]:
        if (
            not isinstance(module_record, Mapping)
            or set(module_record) != {"module", "source_path", "sha256"}
            or type(module_record.get("module")) is not str
            or not (
                module_record["module"] == "komorebi_neuralese"
                or module_record["module"].startswith("komorebi_neuralese.")
            )
            or type(module_record.get("source_path")) is not str
            or not module_record["source_path"].startswith(
                "src/komorebi_neuralese/"
            )
            or PurePosixPath(module_record["source_path"]).is_absolute()
            or ".." in PurePosixPath(module_record["source_path"]).parts
            or not is_sha256_text(module_record.get("sha256"))
            or module_record["module"] in loaded_module_names
        ):
            raise RuntimeError("RUN sealed-import module receipt is invalid")
        loaded_module_names.add(module_record["module"])
        loaded_module_order.append(module_record["module"])
        loaded_module_digest.update(module_record["module"].encode("utf-8") + b"\0")
        loaded_module_digest.update(
            module_record["source_path"].encode("utf-8") + b"\0"
        )
        loaded_module_digest.update(module_record["sha256"].encode("ascii") + b"\0")
    if (
        loaded_module_order != sorted(loaded_module_order)
        or loaded_module_digest.hexdigest()
        != import_receipt["ordered_loaded_module_receipt_sha256"]
    ):
        raise RuntimeError("RUN sealed-import ordered receipt digest is invalid")

    closing = source.get("closing_provenance_reverification", {})
    source_integrity = source.get("package_source_integrity")
    seal_binding = source.get("checkpoint_seal_manifest_binding", {})
    if not isinstance(closing, Mapping) or set(closing) != {
        "archive_sha256_before",
        "archive_sha256_after",
        "source_integrity_before",
        "source_integrity_after",
        "checkpoint_census_before_sha256",
        "checkpoint_census_after_sha256",
        "checkpoint_seal_sha256_before",
        "checkpoint_seal_sha256_after",
        "all_reverified_before_commit",
    }:
        raise RuntimeError("RUN closing provenance has an unexpected key set")
    recomputed_census = [
        {
            "arm": cell[0],
            "seed": cell[1],
            "checkpoint_sha256": run_by_cell[cell].get("checkpoint_sha256"),
            "sealed_state_dict_digest": verified_state_controls[cell].get(
                "sealed_digest"
            ),
        }
        for cell in sorted(run_by_cell)
    ]
    if any(
        not is_sha256_text(record["checkpoint_sha256"])
        or not is_sha256_text(record["sealed_state_dict_digest"])
        for record in recomputed_census
    ):
        raise RuntimeError("checkpoint census contains a malformed digest")
    recomputed_census_sha256 = canonical_json_digest(recomputed_census)
    if (
        not isinstance(source, Mapping)
        or source.get("archive_sha256") != EXPECTED_ARCHIVE_SHA256
        or source.get("archive_verified") is not True
        or source.get("all_checkpoint_receipts_verified") is not True
        or source.get("all_checkpoint_files_bound_to_sealed_package_manifest")
        is not True
        or source.get("weights_only_load") is not True
        or source.get("checkpoint_load_bound_to_prehashed_bytes") is not True
        or source.get("strict_state_load") is not True
        or source.get("one_model_loaded_at_a_time") is not True
        or type(source.get("official_checkpoint_count")) is not int
        or source.get("official_checkpoint_count") != 12
        or type(source.get("seal_receipt_count")) is not int
        or source.get("seal_receipt_count") != 12
        or not isinstance(source_integrity, Mapping)
        or set(source_integrity)
        != {
            "archive_sha256_binding",
            "manifest_sha256",
            "source_file_count",
            "ordered_source_receipt_sha256",
        }
        or source_integrity.get("archive_sha256_binding")
        != EXPECTED_ARCHIVE_SHA256
        or source_integrity.get("manifest_sha256")
        != EXPECTED_PACKAGE_MANIFEST_SHA256
        or type(source_integrity.get("source_file_count")) is not int
        or source_integrity.get("source_file_count") <= 0
        or not is_sha256_text(
            source_integrity.get("ordered_source_receipt_sha256")
        )
        or not isinstance(seal_binding, Mapping)
        or set(seal_binding) != {"path", "size", "sha256", "manifest_sha256"}
        or seal_binding.get("path")
        != "results/packet_closure_pilot/CHECKPOINT_SEAL.json"
        or type(seal_binding.get("size")) is not int
        or seal_binding.get("size") <= 0
        or not is_sha256_text(seal_binding.get("sha256"))
        or seal_binding.get("manifest_sha256")
        != EXPECTED_PACKAGE_MANIFEST_SHA256
        or not is_sha256_text(source.get("checkpoint_seal_sha256"))
        or source.get("checkpoint_seal_sha256") != seal_binding.get("sha256")
        or not isinstance(closing, Mapping)
        or closing.get("archive_sha256_before") != EXPECTED_ARCHIVE_SHA256
        or closing.get("archive_sha256_after") != EXPECTED_ARCHIVE_SHA256
        or not type_strict_equal(
            closing.get("source_integrity_before"), source_integrity
        )
        or not type_strict_equal(
            closing.get("source_integrity_after"), source_integrity
        )
        or closing.get("checkpoint_census_before_sha256")
        != recomputed_census_sha256
        or closing.get("checkpoint_census_after_sha256")
        != recomputed_census_sha256
        or closing.get("checkpoint_seal_sha256_before")
        != seal_binding.get("sha256")
        or closing.get("checkpoint_seal_sha256_after")
        != seal_binding.get("sha256")
        or closing.get("all_reverified_before_commit") is not True
    ):
        raise RuntimeError("RUN source/checkpoint closing provenance is invalid")

    runtime = run.get("runtime")
    required_runtime_keys = {
        "python",
        "numpy",
        "torch",
        "device",
        "intraop_threads",
        "interop_threads",
        "model_and_operator_forward_dtype",
        "diagnostic_dtype_after_detach",
        "elapsed_seconds",
        "observed_peak_resident_set_bytes",
        "declared_peak_working_set_ceiling_bytes",
        "observed_peak_within_declared_ceiling",
        "pre_spend_resource_firewall",
    }
    pre_spend = runtime.get("pre_spend_resource_firewall") if isinstance(
        runtime, Mapping
    ) else None
    if (
        not isinstance(runtime, Mapping)
        or set(runtime) != required_runtime_keys
        or any(type(runtime.get(key)) is not str or not runtime.get(key) for key in ("python", "numpy", "torch"))
        or runtime.get("device") != "cpu"
        or type(runtime.get("intraop_threads")) is not int
        or runtime.get("intraop_threads") != TORCH_INTRAOP_THREADS
        or type(runtime.get("interop_threads")) is not int
        or runtime.get("interop_threads") != TORCH_INTEROP_THREADS
        or runtime.get("model_and_operator_forward_dtype") != "torch.float32"
        or runtime.get("diagnostic_dtype_after_detach") != "numpy.float64"
        or type(runtime.get("elapsed_seconds")) not in (int, float)
        or not math.isfinite(float(runtime.get("elapsed_seconds")))
        or float(runtime.get("elapsed_seconds")) < 0.0
        or type(runtime.get("observed_peak_resident_set_bytes")) is not int
        or runtime.get("observed_peak_resident_set_bytes") <= 0
        or runtime.get("observed_peak_resident_set_bytes")
        > DECLARED_PEAK_WORKING_SET_CEILING_BYTES
        or type(runtime.get("declared_peak_working_set_ceiling_bytes")) is not int
        or runtime.get("declared_peak_working_set_ceiling_bytes")
        != DECLARED_PEAK_WORKING_SET_CEILING_BYTES
        or runtime.get("observed_peak_within_declared_ceiling") is not True
    ):
        raise RuntimeError("RUN runtime receipt is invalid")
    if (
        not isinstance(pre_spend, Mapping)
        or set(pre_spend)
        != {
            "free_bytes_before_spend",
            "required_free_bytes_before_spend",
            "headroom_pass",
            "manifest_budget_checks_pass",
        }
        or type(pre_spend.get("free_bytes_before_spend")) is not int
        or type(pre_spend.get("required_free_bytes_before_spend")) is not int
        or pre_spend.get("required_free_bytes_before_spend")
        != MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND
        or pre_spend.get("free_bytes_before_spend")
        < pre_spend.get("required_free_bytes_before_spend")
        or pre_spend.get("headroom_pass") is not True
        or pre_spend.get("manifest_budget_checks_pass") is not True
    ):
        raise RuntimeError("RUN pre-spend resource receipt is invalid")

    output_layout = run.get("output_layout")
    expected_output_layout = {
        "one_checkpoint_shard_written_before_next_model_load": True,
        "bundle_root": ".",
        "run": RUN_FILENAME,
        "exact_control": EXACT_CONTROL_FILENAME,
        "internal_spend_receipt": SPEND_RECEIPT_FILENAME,
        "checkpoint_directory": CHECKPOINT_DIRECTORY_NAME,
        "manifest": BUNDLE_MANIFEST_FILENAME,
        "commit": COMMIT_FILENAME,
        "all_paths_relative_and_portable": True,
        "commit_written_last": True,
    }
    if not type_strict_equal(output_layout, expected_output_layout):
        raise RuntimeError("RUN output layout is not the exact frozen layout")

    protocol = run.get("protocol")
    required_protocol_keys = {
        "path",
        "sha256",
        "implementation_sha256",
        "test_sha256",
        "status",
        "static_review",
        "root_protocol_receipt",
    }
    if (
        not isinstance(protocol, Mapping)
        or set(protocol) != required_protocol_keys
        or protocol.get("path") != "ANALYSIS_PROTOCOL.md"
        or protocol.get("status") != "FROZEN_POSTHOC"
        or not is_sha256_text(protocol.get("sha256"))
        or not is_sha256_text(protocol.get("implementation_sha256"))
        or not is_sha256_text(protocol.get("test_sha256"))
    ):
        raise RuntimeError("RUN protocol summary is invalid")
    root_receipt = protocol.get("root_protocol_receipt", {})
    required_root_summary_keys = {
        "schema",
        "version",
        "author",
        "status",
        "path",
        "file_sha256",
        "receipt_sha256",
        "artifact_sha256",
        "source_provenance",
    }
    if (
        not isinstance(root_receipt, Mapping)
        or set(root_receipt) != required_root_summary_keys
        or root_receipt.get("schema")
        != "komorebi.neuralese.semantic_retraction.protocol_receipt.v1"
        or root_receipt.get("version") != VERSION
        or root_receipt.get("author") != AUTHOR
        or root_receipt.get("status") != "FROZEN_BEFORE_LEARNED_OUTCOMES"
        or root_receipt.get("path") != ROOT_PROTOCOL_RECEIPT_PATH.name
        or not is_sha256_text(root_receipt.get("file_sha256"))
        or not is_sha256_text(root_receipt.get("receipt_sha256"))
    ):
        raise RuntimeError("RUN embeds an invalid root protocol receipt summary")
    artifact_hashes = root_receipt.get("artifact_sha256", {})
    source_provenance = root_receipt.get("source_provenance", {})
    if not isinstance(artifact_hashes, Mapping) or set(artifact_hashes) != set(
        REQUIRED_ROOT_ARTIFACT_KEYS
    ):
        raise RuntimeError("embedded root receipt has an invalid artifact hash key set")
    if any(not is_sha256_text(value) for value in artifact_hashes.values()):
        raise RuntimeError("embedded root receipt has a malformed artifact hash")
    expected_source_provenance = {
        "source_archive_sha256": EXPECTED_ARCHIVE_SHA256,
        "source_package_manifest_sha256": EXPECTED_PACKAGE_MANIFEST_SHA256,
    }
    if not type_strict_equal(source_provenance, expected_source_provenance):
        raise RuntimeError("embedded source provenance differs from sealed constants")
    if (
        artifact_hashes.get("analysis_protocol") != protocol.get("sha256")
        or artifact_hashes.get("primary_implementation")
        != protocol.get("implementation_sha256")
        or artifact_hashes.get("primary_tests") != protocol.get("test_sha256")
    ):
        raise RuntimeError("RUN protocol summary differs from terminal artifact receipt")
    validate_static_review_release(
        protocol.get("static_review", {}),
        protocol_sha256=protocol.get("sha256"),
        theoretical_framework_sha256=artifact_hashes.get("theoretical_framework"),
        implementation_sha256=protocol.get("implementation_sha256"),
        test_sha256=protocol.get("test_sha256"),
        machine_contract_sha256=artifact_hashes.get("primary_machine_contract"),
        manifest_file_sha256=artifact_hashes.get("primary_manifest_dry_run"),
        manifest_freeze_receipt_sha256=internal_spend.get(
            "manifest_freeze_receipt_sha256"
        ),
    )
    expected_spend_links = {
        "protocol_sha256": protocol.get("sha256"),
        "implementation_sha256": protocol.get("implementation_sha256"),
        "test_sha256": protocol.get("test_sha256"),
        "machine_contract_sha256": artifact_hashes.get(
            "primary_machine_contract"
        ),
        "manifest_file_sha256": artifact_hashes.get("primary_manifest_dry_run"),
        "static_review_file_sha256": artifact_hashes.get("primary_static_review"),
        "theoretical_framework_sha256": artifact_hashes.get(
            "theoretical_framework"
        ),
        "root_protocol_receipt_file_sha256": root_receipt.get("file_sha256"),
        "root_protocol_receipt_internal_sha256": root_receipt.get(
            "receipt_sha256"
        ),
        "source_archive_sha256": source_provenance.get("source_archive_sha256"),
        "source_package_manifest_sha256": source_provenance.get(
            "source_package_manifest_sha256"
        ),
        "evaluation_context_sha256": run.get("context_banks", {})
        .get("evaluation", {})
        .get("sha256"),
        "evaluation_path_sha256": run.get("path_banks", {})
        .get("evaluation", {})
        .get("sha256"),
        "continuation_sha256": run.get("continuation_bank", {}).get("sha256"),
        "random_key_manifest_sha256": run.get("random_key_manifest", {}).get(
            "sha256"
        ),
        "exact_control_sha256": commit["exact_control"]["sha256"],
    }
    for key, expected_value in expected_spend_links.items():
        if expected_value is None or internal_spend.get(key) != expected_value:
            raise RuntimeError(f"spend/RUN provenance cross-link mismatch: {key}")
    review_manifest_digest = protocol.get("static_review", {}).get(
        "manifest_freeze_receipt_sha256"
    )
    if internal_spend.get("manifest_freeze_receipt_sha256") != review_manifest_digest:
        raise RuntimeError("spend receipt manifest freeze digest mismatch")

    expected_verified_files = {
        COMMIT_FILENAME,
        RUN_FILENAME,
        BUNDLE_MANIFEST_FILENAME,
        EXACT_CONTROL_FILENAME,
        SPEND_RECEIPT_FILENAME,
        *expected_shards,
    }
    if set(verified_member_hashes) != expected_verified_files:
        raise RuntimeError("bundle verifier did not bind the exact complete file set")
    for relative, expected_sha256 in verified_member_hashes.items():
        if relative == EXACT_CONTROL_FILENAME:
            maximum_bytes = MAXIMUM_EXACT_CONTROL_BYTES
        elif relative.startswith(f"{CHECKPOINT_DIRECTORY_NAME}/"):
            maximum_bytes = MAXIMUM_CHECKPOINT_SHARD_BYTES
        else:
            maximum_bytes = MAXIMUM_BUNDLE_METADATA_BYTES
        _, final_sha256 = read_file_snapshot(
            _bundle_member(bundle_path, relative),
            label=f"terminal bundle member {relative}",
            maximum_bytes=maximum_bytes,
        )
        if final_sha256 != expected_sha256:
            raise RuntimeError(f"bundle member changed during verification: {relative}")
    _assert_exact_bundle_census(bundle_path, expected_shards)
    if external_spend_marker_checked:
        if external_spend_path is None:
            raise RuntimeError("external spend marker path was lost during verification")
        terminal_external_bytes, terminal_external_sha256 = read_file_snapshot(
            external_spend_path,
            label="terminal external live spend marker",
            maximum_bytes=len(loaded_bytes["spend_receipt"]),
        )
        if (
            terminal_external_sha256
            != verified_member_hashes[SPEND_RECEIPT_FILENAME]
            or terminal_external_bytes != loaded_bytes["spend_receipt"]
        ):
            raise RuntimeError("external spend marker changed during bundle verification")
    assert_peak_memory_within_budget()

    return {
        "status": "PASS",
        "schema": "komorebi.neuralese.semantic_retraction_bundle_verification.v1",
        "bundle_manifest_sha256": commit["bundle_manifest"]["sha256"],
        "run_sha256": commit["run"]["sha256"],
        "exact_control_sha256": commit["exact_control"]["sha256"],
        "spend_receipt_sha256": commit["spend_receipt"]["sha256"],
        "commit_sha256": commit_sha256,
        "checkpoint_shard_count": 12,
        "exact_file_set": True,
        "portable_relative_paths": True,
        "no_symbolic_links": True,
        "external_spend_marker_checked": external_spend_marker_checked,
    }


def run_learned_panel(
    package: Path,
    archive: Path,
    output_path: Path,
    *,
    spend_path: Path = EVALUATION_BANK_SPEND_PATH,
) -> dict[str, Any]:
    """Run once only after the frozen firewall succeeds; stream one model at a time."""

    output_path = result_bundle_path(output_path)
    spend_path = Path(os.path.abspath(os.fspath(spend_path)))
    bundle_path = assert_fresh_learned_output_paths(
        output_path, spend_path=spend_path
    )
    package = package.resolve()
    archive = Path(os.path.abspath(os.fspath(archive)))
    if archive.is_symlink() or not archive.is_file():
        raise RuntimeError("source archive is absent or symbolic")
    archive = archive.resolve(strict=True)
    prospective_bundle = bundle_path.parent.resolve(strict=True) / bundle_path.name
    if prospective_bundle.is_relative_to(package):
        raise RuntimeError("learned result bundle may not modify the sealed package")
    freeze = assert_protocol_frozen(package=package)
    started = time.time()
    archive_sha = sha256_file(archive)
    if archive_sha != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("v0.4 source archive SHA-256 mismatch")
    source_integrity = verify_package_source_integrity(package)
    api = import_v04_api(package)
    import_origin_receipt = api["import_origin_receipt"]
    canonical_maps = api["canonical_maps"]("d4").astype(np.int64)
    context_banks = make_disjoint_context_banks(api["EpisodeGenerator"])
    path_banks = make_disjoint_path_banks(canonical_maps)
    continuations = make_continuation_bank()
    stress_continuations = ContinuationBank(
        words=path_banks["stress"].words_by_endpoint,
        receipt=path_banks["stress"].receipt,
    )
    random_manifest = make_random_key_manifest(
        CONTEXT_COUNT, path_banks["evaluation"], split_code=2
    )
    exact_control = run_exact_compiled_control(api)
    if not exact_control["audit"]["pass"]:
        raise RuntimeError("exact compiled positive control failed before checkpoint loading")
    exact_serialized_bytes = assert_json_serializable_within_limit(
        exact_control,
        MAXIMUM_EXACT_CONTROL_BYTES,
        label="exact compiled control",
    )
    checkpoint_census, seal = verify_checkpoint_census(package)
    observed_peak_rss_bytes = assert_peak_memory_within_budget()
    freeze_before_spend = assert_protocol_frozen(package=package)
    if not type_strict_equal(freeze_before_spend, freeze):
        raise RuntimeError("frozen analysis artifacts changed during pre-spend controls")
    freeze = freeze_before_spend
    disk_preflight = assert_manifest_budget_and_disk_headroom(freeze, bundle_path)

    # Reserve and prove the whole namespace before the global spend marker is
    # published. Everything before the marker is checkpoint-free.
    reserve_result_bundle(bundle_path)
    shard_dir = bundle_path / CHECKPOINT_DIRECTORY_NAME
    shard_dir.mkdir(mode=0o755, exist_ok=False)
    _fsync_directory(bundle_path)
    exact_path = bundle_path / EXACT_CONTROL_FILENAME
    exact_sha = _write_json_exclusive(exact_path, exact_control)
    if exact_path.stat().st_size != exact_serialized_bytes:
        raise RuntimeError("exact-control serialization size changed after preflight")
    exact_control_receipt = {
        "path": EXACT_CONTROL_FILENAME,
        "sha256": exact_sha,
        "serialized_bytes": exact_serialized_bytes,
        "audit": exact_control["audit"],
        "context_bank": exact_control["context_bank"],
        "path_bank": exact_control["path_bank"],
        "continuation_bank": exact_control["continuation_bank"],
    }
    freeze_at_spend_marker = assert_protocol_frozen(package=package)
    if not type_strict_equal(freeze_at_spend_marker, freeze):
        raise RuntimeError("frozen analysis artifacts changed before spend publication")

    # Publish the authoritative global lock first, then its portable bundle copy.
    # No learned model is loaded until both byte-identical copies exist.
    spend_receipt, spend_file_sha = create_evaluation_bank_spend_receipt(
        bundle_path=bundle_path,
        freeze=freeze,
        context_banks=context_banks,
        path_banks=path_banks,
        continuations=continuations,
        random_manifest=random_manifest,
        exact_control_sha256=exact_sha,
        spend_path=spend_path,
    )
    del exact_control
    gc.collect()

    checkpoint_summaries: list[dict[str, Any]] = []
    for index, verified in enumerate(checkpoint_census, start=1):
        checkpoint = load_one_verified_checkpoint(verified, seal, api)
        model = checkpoint["model"]
        whole_analysis_independent_digest_before = _model_tensor_digest(model)
        whole_analysis_seal_compatible_digest_before = api["state_dict_digest"](model)
        if not (
            whole_analysis_seal_compatible_digest_before
            == checkpoint["loaded_state_dict_digest"]
            == checkpoint["sealed_state_dict_digest"]
        ):
            raise RuntimeError("pre-analysis model digest does not match checkpoint seal")
        print(
            f"[{index:02d}/12] semantic-retraction arm={checkpoint['arm']} seed={checkpoint['seed']}",
            flush=True,
        )
        prototypes = build_calibration_prototypes(
            model,
            context_banks["calibration"],
            path_banks["calibration"],
            canonical_maps,
        )
        evaluation_encoded_contexts = tuple(
            encode_context_once(model, context_banks["evaluation"].tables[context_index])
            for context_index in range(context_banks["evaluation"].tables.shape[0])
        )
        native_prefix_cache: dict[
            tuple[int, int, int], NativePrefixCacheEntry
        ] = {}
        model_result = evaluate_paired_model(
            model,
            context_banks["evaluation"],
            path_banks["evaluation"],
            continuations,
            canonical_maps,
            prototypes,
            evaluation_encoded_contexts,
            secondary_continuation_bank=stress_continuations,
            native_prefix_cache=native_prefix_cache,
        )
        stress_result = model_result.pop("secondary_stress_descriptive")
        periodic_result = evaluate_periodic_model(
            model,
            context_banks["evaluation"],
            path_banks["evaluation"],
            continuations,
            canonical_maps,
            prototypes,
            evaluation_encoded_contexts,
            native_prefix_cache=native_prefix_cache,
        )
        whole_analysis_independent_digest_after = _model_tensor_digest(model)
        whole_analysis_seal_compatible_digest_after = api["state_dict_digest"](model)
        if not (
            whole_analysis_independent_digest_before
            == whole_analysis_independent_digest_after
            and whole_analysis_seal_compatible_digest_before
            == whole_analysis_seal_compatible_digest_after
            == checkpoint["sealed_state_dict_digest"]
        ):
            raise RuntimeError("model state dictionary changed during full checkpoint analysis")
        claim_matrix = build_independent_claim_matrix(model_result, periodic_result)
        shard_payload = {
            "schema": "komorebi.neuralese.semantic_retraction_checkpoint_result.v1",
            "version": VERSION,
            "author": AUTHOR,
            "arm": checkpoint["arm"],
            "seed": checkpoint["seed"],
            "model_family": checkpoint["model_family"],
            "checkpoint_filename": checkpoint["checkpoint"].name,
            "checkpoint_sha256": checkpoint["checkpoint_sha256"],
            "whole_analysis_state_dict_control": {
                "independent_digest_before": whole_analysis_independent_digest_before,
                "independent_digest_after": whole_analysis_independent_digest_after,
                "seal_compatible_digest_before": whole_analysis_seal_compatible_digest_before,
                "seal_compatible_digest_after": whole_analysis_seal_compatible_digest_after,
                "sealed_digest": checkpoint["sealed_state_dict_digest"],
                "unchanged": True,
                "seal_match": True,
            },
            "prototype_audit": prototypes.audit,
            "one_shot_primary": model_result,
            "one_shot_stress_descriptive": stress_result,
            "periodic": periodic_result,
            "independent_claim_matrix": claim_matrix,
        }
        shard_relative = (
            f"{CHECKPOINT_DIRECTORY_NAME}/"
            f"{checkpoint['arm']}__seed_{checkpoint['seed']}.json"
        )
        shard_path = bundle_path.joinpath(*PurePosixPath(shard_relative).parts)
        shard_sha = _write_json_exclusive(shard_path, shard_payload)
        shard_bytes = shard_path.stat().st_size
        if shard_bytes > MAXIMUM_CHECKPOINT_SHARD_BYTES:
            raise RuntimeError(
                f"checkpoint shard exceeds frozen byte ceiling: {shard_relative}"
            )
        checkpoint_summaries.append(
            {
                "arm": checkpoint["arm"],
                "seed": checkpoint["seed"],
                "model_family": checkpoint["model_family"],
                "checkpoint_filename": checkpoint["checkpoint"].name,
                "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                "checkpoint_shard": shard_relative,
                "checkpoint_shard_sha256": shard_sha,
                "checkpoint_shard_bytes": shard_bytes,
                "whole_analysis_state_dict_unchanged": True,
                "independent_claim_matrix": claim_matrix,
            }
        )
        del shard_payload, periodic_result, stress_result, model_result
        del native_prefix_cache, evaluation_encoded_contexts, prototypes
        del checkpoint, model
        gc.collect()
        observed_peak_rss_bytes = max(
            observed_peak_rss_bytes, assert_peak_memory_within_budget()
        )

    arm_claim_matrix = aggregate_arm_claim_matrices(checkpoint_summaries)
    freeze_before_commit = assert_protocol_frozen(package=package)
    if not type_strict_equal(freeze_before_commit, freeze):
        raise RuntimeError("frozen analysis artifacts changed during learned execution")

    def census_receipt(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "arm": str(row["arm"]),
                "seed": int(row["seed"]),
                "checkpoint_sha256": str(row["checkpoint_sha256"]),
                "sealed_state_dict_digest": str(row["sealed_state_dict_digest"]),
            }
            for row in rows
        ]

    closing_archive_sha = sha256_file(archive)
    closing_source_integrity = verify_package_source_integrity(package)
    closing_checkpoint_census, closing_seal = verify_checkpoint_census(package)
    if closing_archive_sha != archive_sha:
        raise RuntimeError("source archive changed during learned analysis")
    if not type_strict_equal(closing_source_integrity, source_integrity):
        raise RuntimeError("sealed source changed during learned analysis")
    if not type_strict_equal(
        census_receipt(closing_checkpoint_census), census_receipt(checkpoint_census)
    ):
        raise RuntimeError("sealed checkpoint census changed during learned analysis")
    closing_provenance = {
        "archive_sha256_before": archive_sha,
        "archive_sha256_after": closing_archive_sha,
        "source_integrity_before": source_integrity,
        "source_integrity_after": closing_source_integrity,
        "checkpoint_census_before_sha256": canonical_json_digest(
            census_receipt(checkpoint_census)
        ),
        "checkpoint_census_after_sha256": canonical_json_digest(
            census_receipt(closing_checkpoint_census)
        ),
        "checkpoint_seal_sha256_before": seal[
            "extracted_artifact_manifest_binding"
        ]["sha256"],
        "checkpoint_seal_sha256_after": closing_seal[
            "extracted_artifact_manifest_binding"
        ]["sha256"],
        "all_reverified_before_commit": True,
    }
    result = {
        "schema": SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "analysis_status": ANALYSIS_STATUS,
        "result_validity": "VALID_ONLY_WITH_COMMIT",
        "claim_boundary": CLAIM_BOUNDARY,
        "protocol": {
            "path": "ANALYSIS_PROTOCOL.md",
            "sha256": freeze["protocol_sha256"],
            "implementation_sha256": freeze["implementation_sha256"],
            "test_sha256": freeze["test_sha256"],
            "status": freeze["contract"]["status"],
            "static_review": freeze["review"],
            "root_protocol_receipt": freeze["root_protocol_receipt"],
        },
        "source": {
            "archive_filename": archive.name,
            "archive_absolute_path_non_normative": str(archive),
            "archive_sha256": archive_sha,
            "archive_verified": True,
            "package_source_integrity": source_integrity,
            "sealed_import_origin_receipt": import_origin_receipt,
            "checkpoint_seal_sha256": sha256_file(
                package / "results" / "packet_closure_pilot" / "CHECKPOINT_SEAL.json"
            ),
            "checkpoint_seal_manifest_binding": seal[
                "extracted_artifact_manifest_binding"
            ],
            "official_checkpoint_count": len(checkpoint_census),
            "seal_receipt_count": len(seal["checkpoints"]),
            "all_checkpoint_receipts_verified": True,
            "all_checkpoint_files_bound_to_sealed_package_manifest": True,
            "weights_only_load": True,
            "checkpoint_load_bound_to_prehashed_bytes": True,
            "strict_state_load": True,
            "one_model_loaded_at_a_time": True,
            "closing_provenance_reverification": closing_provenance,
        },
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "torch": torch.__version__,
            "device": "cpu",
            "intraop_threads": int(torch.get_num_threads()),
            "interop_threads": int(torch.get_num_interop_threads()),
            "model_and_operator_forward_dtype": "torch.float32",
            "diagnostic_dtype_after_detach": "numpy.float64",
            "elapsed_seconds": time.time() - started,
            "observed_peak_resident_set_bytes": observed_peak_rss_bytes,
            "declared_peak_working_set_ceiling_bytes": (
                DECLARED_PEAK_WORKING_SET_CEILING_BYTES
            ),
            "observed_peak_within_declared_ceiling": True,
            "pre_spend_resource_firewall": disk_preflight,
        },
        "context_banks": {
            name: bank.receipt for name, bank in context_banks.items()
        },
        "path_banks": {
            "calibration": path_banks["calibration"].receipt,
            "evaluation": path_banks["evaluation"].receipt,
            "stress": path_banks["stress"].receipt,
        },
        "continuation_bank": continuations.receipt,
        "random_key_manifest": random_manifest,
        "evaluation_bank_spend_receipt": spend_receipt,
        "exact_compiled_control": exact_control_receipt,
        "checkpoint_results": checkpoint_summaries,
        "arm_level_independent_claim_matrix": arm_claim_matrix,
        "output_layout": {
            "one_checkpoint_shard_written_before_next_model_load": True,
            "bundle_root": ".",
            "run": RUN_FILENAME,
            "exact_control": EXACT_CONTROL_FILENAME,
            "internal_spend_receipt": SPEND_RECEIPT_FILENAME,
            "checkpoint_directory": CHECKPOINT_DIRECTORY_NAME,
            "manifest": BUNDLE_MANIFEST_FILENAME,
            "commit": COMMIT_FILENAME,
            "all_paths_relative_and_portable": True,
            "commit_written_last": True,
        },
    }
    run_path = bundle_path / RUN_FILENAME
    run_sha = _write_json_exclusive(run_path, result)
    run_bytes = run_path.stat().st_size

    exact_descriptor = {"path": EXACT_CONTROL_FILENAME, "sha256": exact_sha}
    spend_descriptor = {
        "path": SPEND_RECEIPT_FILENAME,
        "sha256": spend_file_sha,
    }
    run_descriptor = {"path": RUN_FILENAME, "sha256": run_sha}
    checkpoint_descriptors = [
        {
            "arm": record["arm"],
            "seed": record["seed"],
            "path": record["checkpoint_shard"],
            "sha256": record["checkpoint_shard_sha256"],
        }
        for record in checkpoint_summaries
    ]
    bundle_manifest_path = bundle_path / BUNDLE_MANIFEST_FILENAME
    bundle_manifest = {
        "schema": "komorebi.neuralese.semantic_retraction_result_bundle.v1",
        "version": VERSION,
        "author": AUTHOR,
        "status": "COMPLETE_PENDING_COMMIT",
        "result_validity": "VALID_ONLY_WITH_COMMIT",
        "run": run_descriptor,
        "exact_control": exact_descriptor,
        "exact_control_summary": exact_control_receipt,
        "spend_receipt": spend_descriptor,
        "checkpoint_shards": checkpoint_descriptors,
        "required_checkpoint_cells": [
            {"arm": arm, "seed": seed}
            for arm in REQUIRED_ARMS
            for seed in REQUIRED_SEEDS
        ],
        "arm_level_independent_claim_matrix": arm_claim_matrix,
    }
    bundle_manifest_sha = _write_json_exclusive(bundle_manifest_path, bundle_manifest)
    metadata_bytes = (
        run_bytes
        + bundle_manifest_path.stat().st_size
        + (bundle_path / SPEND_RECEIPT_FILENAME).stat().st_size
    )
    if metadata_bytes > MAXIMUM_BUNDLE_METADATA_BYTES:
        raise RuntimeError("bundle metadata exceeds frozen byte ceiling")
    commit = {
        "schema": "komorebi.neuralese.semantic_retraction_result_commit.v1",
        "version": VERSION,
        "author": AUTHOR,
        "status": "COMMITTED",
        "result_validity": "VALID_ONLY_WITH_THIS_COMMIT",
        "run": run_descriptor,
        "bundle_manifest": {
            "path": BUNDLE_MANIFEST_FILENAME,
            "sha256": bundle_manifest_sha,
        },
        "exact_control": exact_descriptor,
        "spend_receipt": spend_descriptor,
        "checkpoint_shard_count": len(checkpoint_summaries),
    }
    terminal_archive_sha = sha256_file(archive)
    terminal_source_integrity = verify_package_source_integrity(package)
    terminal_checkpoint_census, terminal_seal = verify_checkpoint_census(package)
    if (
        terminal_archive_sha != archive_sha
        or not type_strict_equal(terminal_source_integrity, source_integrity)
        or not type_strict_equal(
            census_receipt(terminal_checkpoint_census),
            census_receipt(checkpoint_census),
        )
        or terminal_seal["extracted_artifact_manifest_binding"]["sha256"]
        != seal["extracted_artifact_manifest_binding"]["sha256"]
    ):
        raise RuntimeError("sealed source provenance changed before COMMIT publication")
    terminal_freeze = assert_protocol_frozen(package=package)
    if not type_strict_equal(terminal_freeze, freeze):
        raise RuntimeError("frozen analysis artifacts changed before COMMIT publication")
    _write_json_exclusive(bundle_path / COMMIT_FILENAME, commit)
    verification = verify_result_bundle(
        bundle_path, external_spend_path=spend_path
    )
    if verification.get("status") != "PASS":
        raise RuntimeError("post-commit result bundle verification did not pass")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--run-controls",
        action="store_true",
        help="run only synthetic exact compiled controls; learned checkpoints stay untouched",
    )
    modes.add_argument(
        "--manifest-only",
        action="store_true",
        help="regenerate checkpoint-free bank/count/budget receipt; no checkpoint load",
    )
    modes.add_argument(
        "--execute-learned",
        action="store_true",
        help="requires a byte-matched frozen protocol receipt",
    )
    modes.add_argument(
        "--verify-bundle",
        action="store_true",
        help="verify a committed portable result bundle without loading checkpoints",
    )
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "learned mode: self-contained bundle directory (default RESULTS.bundle); "
            "verify mode: bundle directory; control mode: exclusive standalone JSON file"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.verify_bundle:
        bundle_path = args.output if args.output is not None else DEFAULT_RESULT_BUNDLE
        print(json.dumps(verify_result_bundle(bundle_path), sort_keys=True))
        return 0
    if args.execute_learned:
        bundle_path = args.output if args.output is not None else DEFAULT_RESULT_BUNDLE
        assert_fresh_learned_output_paths(bundle_path)
        run_learned_panel(
            args.package, args.archive, bundle_path
        )
        print(f"wrote and verified committed bundle {bundle_path}")
        return 0
    if args.manifest_only:
        if args.output is not None:
            raise RuntimeError("--manifest-only writes only the frozen manifest path")
        if _path_lexists(EVALUATION_BANK_SPEND_PATH):
            raise RuntimeError(
                "saved manifest publication/overwrite is forbidden after bank spend"
            )
        if _path_lexists(STATIC_REVIEW_RELEASE_PATH):
            raise RuntimeError(
                "saved manifest publication/overwrite is forbidden after static release"
            )
        results = manifest_only_dry_run(args.package.resolve())
        _write_json_exclusive(MANIFEST_DRY_RUN_PATH, results)
        print(f"wrote {MANIFEST_DRY_RUN_PATH}")
        return 0
    if args.run_controls:
        control_output = (
            args.output if args.output is not None else DEFAULT_CONTROL_OUTPUT
        )
        control_output = assert_safe_control_output_path(
            control_output, package=args.package
        )
        api = import_v04_api(args.package.resolve())
        results = run_exact_compiled_control(api)
        if not results["audit"]["pass"]:
            raise RuntimeError("exact compiled positive control failed")
        assert_json_serializable_within_limit(
            results,
            MAXIMUM_EXACT_CONTROL_BYTES,
            label="standalone exact compiled control",
        )
        _write_json_exclusive(control_output, results)
        print(f"wrote {control_output}")
        return 0

    if args.output is not None:
        raise RuntimeError("--output requires --run-controls or --execute-learned")

    contract = load_machine_contract()
    learned_state = "LOCKED"
    lock_reason: str | None = None
    try:
        assert_fresh_learned_output_paths(DEFAULT_RESULT_BUNDLE)
        assert_protocol_frozen(package=args.package.resolve())
        learned_state = "ARMED_NOT_EXECUTED"
    except (FileExistsError, OSError, RuntimeError, ValueError) as exc:
        lock_reason = str(exc)
    print(
        json.dumps(
            {
                "status": contract["status"],
                "learned_evaluation": learned_state,
                "unlock_state": (
                    "UNLOCKED_BY_FROZEN_RECEIPTS"
                    if learned_state == "ARMED_NOT_EXECUTED"
                    else "LOCKED"
                ),
                "lock_reason": lock_reason,
                "protocol_sha256": sha256_file(PROTOCOL_PATH),
                "static_review_release_present": STATIC_REVIEW_RELEASE_PATH.is_file(),
                "next_safe_actions": (
                    ["execute learned panel once"]
                    if learned_state == "ARMED_NOT_EXECUTED"
                    else ["run unit tests", "complete frozen receipts and static review"]
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
