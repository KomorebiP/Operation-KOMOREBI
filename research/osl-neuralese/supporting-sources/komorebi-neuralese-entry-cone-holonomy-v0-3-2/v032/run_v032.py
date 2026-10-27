#!/usr/bin/env python3
"""Run the frozen Neuralese v0.3.2 execution-correction profile once.

Author: Komorebi P.

This wrapper changes no scientific computation from v0.3.1.  It authenticates
the complete v0.3.1 byte freeze, records the failed pre-ledger v0.3.1 attempt,
corrects the lineage-record shape check, and delegates every learned diagnostic
to the frozen v0.3.1 functions.  No checkpoint may be deserialized before the
v0.3.2 run-start ledger exists.
"""

from __future__ import annotations

import sys


if __name__ == "__main__" and sys.flags.isolated != 1:
    raise RuntimeError(
        "registered execution requires isolated mode: python -I -B v032/run_v032.py"
    )

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import platform
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
V031 = ROOT / "v031"

VERSION = "0.3.2"
AUTHOR = "Komorebi P."
EXPECTED_PYTHON_IMPLEMENTATION = "CPython"
EXPECTED_PYTHON_VERSION = "3.12.13"
EXPECTED_NUMPY_VERSION = "2.3.5"
EXPECTED_V031_EXECUTION_FREEZE_SHA256 = (
    "2600536f3009ed4294bad0432680021915d2b17a15fe6ab973bd835061f7f662"
)
_EXPECTED_ATTESTATION = (
    "No v0.3.2 learned endpoint was inspected before this correction freeze "
    "was written. The v0.3.1 bootstrap read checkpoint bytes only to verify "
    "their SHA-256 digests; v0.3.1 aborted before its run-start ledger, before "
    "restricted checkpoint deserialization, and before endpoint evaluation."
)
_EXPECTED_V031_ABORT_BOUNDARY = {
    "registered_result_absent": True,
    "restricted_checkpoint_deserialization": "not_performed",
    "run_started_ledger_absent": True,
    "sha256_bootstrap_checkpoint_byte_reads": "performed",
    "status": "V031_ABORTED_BEFORE_LEDGER_AND_CHECKPOINT_DESERIALIZATION",
}

_EXPECTED_INHERITED_PROFILE = {
    "checkpoint_seeds": [0, 1],
    "episode_seeds": {"0": 940000, "1": 941000},
    "episodes_per_checkpoint": 8,
    "entry_maximum_suffix_horizon": 8,
    "cone_maximum_history_depth": 8,
    "cone_maximum_suffix_horizon": 8,
    "relation_maximum_inserted_token_budget": 64,
    "relation_repeat_grids": {
        "f2": list(range(33)),
        "r4": list(range(17)),
        "frfr": list(range(17)),
        "rfrf": list(range(17)),
    },
    "path_base_cases_per_episode": 64,
    "path_maximum_suffix_horizon": 8,
    "matched_control_budgets": [16, 32, 64],
    "matched_reference_count": 12,
    "matched_exact_length_control_count": 48,
    "matched_total_path_count": 60,
    "parity_sandwich_materialized": False,
}

_V032_FREEZE_SCHEMA = (
    "komorebi.neuralese.entry_cone_holonomy.correction_execution_freeze.v1"
)
_V032_FREEZE_STATUS = "FROZEN_BEFORE_V032_LEARNED_ENDPOINT_EXECUTION"
_V031_FREEZE_SCHEMA = "komorebi.neuralese.entry_cone_holonomy.execution_freeze.v1"
_V031_FREEZE_STATUS = "FROZEN_BEFORE_FRESH_LEARNED_ENDPOINT_EXECUTION"

_V032_REQUIRED_FILES = frozenset(
    {
        "results/V031_INVALID_ATTEMPT.json",
        "v031/V031_EXECUTION_FREEZE.json",
        "v032/V032_ABORT_DISCLOSURE.json",
        "v032/V032_PREREGISTRATION.json",
        "v032/V032_RESEARCH_SPEC.md",
        "v032/__init__.py",
        "v032/freeze_v032.py",
        "v032/requirements.txt",
        "v032/run_v032.py",
        "v032/test_v032_contract.py",
        "run_lineage_regression.py",
    }
)

_V031_REQUIRED_FILES = frozenset(
    {
        "DESIGN_DISCLOSURE.json",
        "EXECUTION_FREEZE.json",
        "checkpoint_io.py",
        "checkpoints/projective_terminal_seed0.pt",
        "checkpoints/projective_terminal_seed1.pt",
        "core.py",
        "results/LINEAGE_REGRESSION.json",
        "v031/__init__.py",
        "v031/V031_FROZEN_INPUTS.json",
        "v031/V031_MATCHED_WORD_BANK.json",
        "v031/V031_PREFREEZE_VALIDATION.json",
        "v031/V031_PREREGISTRATION.json",
        "v031/V031_RESEARCH_SPEC.md",
        "v031/requirements.txt",
        "v031/entry_recurrence_probe.py",
        "v031/freeze_v031.py",
        "v031/generate_v031_inputs.py",
        "v031/generate_word_bank.py",
        "v031/holonomy_spectroscopy.py",
        "v031/matched_controls.py",
        "v031/run_v031.py",
        "v031/test_entry_recurrence_probe.py",
        "v031/test_holonomy_spectroscopy.py",
        "v031/test_matched_controls.py",
        "v031/test_v031_contract.py",
        "v031/test_v031_engine.py",
        "v031/v031_engine.py",
    }
)

RESULT_PATH = ROOT / "results" / "V032_ENTRY_CONE_HOLONOMY_RESULTS.json"
INVALID_ATTEMPT_PATH = ROOT / "results" / "V032_INVALID_ATTEMPT.json"
RUN_STARTED_PATH = ROOT / "results" / "V032_RUN_STARTED.json"
V031_INVALID_ATTEMPT_PATH = ROOT / "results" / "V031_INVALID_ATTEMPT.json"
V031_RUN_STARTED_PATH = ROOT / "results" / "V031_RUN_STARTED.json"
V031_RESULT_PATH = ROOT / "results" / "V031_ENTRY_CONE_HOLONOMY_RESULTS.json"

sys.dont_write_bytecode = True
_BOOTSTRAP_AUTHENTICATED = False
_BOOTSTRAP_RECORD: dict[str, Any] | None = None
_AUTHENTICATED_PYTHON_SOURCE_BYTES: dict[Path, bytes] = {}
_RUN_STARTED_LEDGER_OWNED = False


def _duplicate_rejector(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def _load_json_stdlib(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle, object_pairs_hook=_duplicate_rejector)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _file_sha256_stdlib(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_root_file(relative: str) -> Path:
    if not isinstance(relative, str):
        raise ValueError("frozen path is not a string")
    candidate = (ROOT / relative).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError as error:
        raise ValueError(f"unsafe frozen path: {relative}") from error
    if not candidate.is_file():
        raise FileNotFoundError(f"frozen input is missing: {relative}")
    return candidate


def _validate_digest_map(
    digest_map: Any, expected_files: frozenset[str], label: str
) -> dict[str, str]:
    if not isinstance(digest_map, dict) or set(digest_map) != expected_files:
        raise ValueError(f"{label} has a nonregistered byte map")
    validated: dict[str, str] = {}
    for relative, expected in digest_map.items():
        if not isinstance(expected, str) or len(expected) != 64:
            raise ValueError(f"{label} has a malformed digest for {relative}")
        observed = _file_sha256_stdlib(_safe_root_file(relative))
        if observed != expected:
            raise ValueError(f"{label} digest mismatch: {relative}")
        validated[relative] = observed
    return validated


def _reject_executable_bytecode() -> None:
    pyc_files = sorted(
        str(path.relative_to(ROOT)) for path in ROOT.rglob("*.pyc") if path.is_file()
    )
    cache_directories = sorted(
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("__pycache__")
        if path.is_dir()
    )
    if pyc_files or cache_directories:
        raise RuntimeError(
            "executable Python bytecode/cache is forbidden for the registered run: "
            f"pyc={pyc_files}, cache_dirs={cache_directories}"
        )


def _reject_local_import_shadowing() -> dict[str, Any]:
    """Reject local alternatives that Python could execute before frozen sources."""

    expected_modules = {
        "checkpoint_io": (ROOT / "checkpoint_io.py").resolve(),
        "core": (ROOT / "core.py").resolve(),
        "entry_recurrence_probe": (V031 / "entry_recurrence_probe.py").resolve(),
        "freeze_v031": (V031 / "freeze_v031.py").resolve(),
        "holonomy_spectroscopy": (V031 / "holonomy_spectroscopy.py").resolve(),
        "matched_controls": (V031 / "matched_controls.py").resolve(),
        "run_v031": (V031 / "run_v031.py").resolve(),
        "v031_engine": (V031 / "v031_engine.py").resolve(),
        "freeze_v032": (HERE / "freeze_v032.py").resolve(),
    }
    executable_suffixes = {".py", ".pyc", ".so", ".pyd", ".dll", ".dylib"}
    for name, expected in expected_modules.items():
        for directory in (ROOT, V031, HERE):
            for candidate in directory.glob(f"{name}.*"):
                if candidate.is_file() and candidate.suffix.lower() in executable_suffixes:
                    if candidate.resolve() != expected:
                        raise RuntimeError(f"local import shadow is forbidden: {candidate}")
            package_candidate = directory / name
            if package_candidate.is_dir():
                raise RuntimeError(
                    f"local package shadow is forbidden: {package_candidate}"
                )
    for package_name, expected_directory in (("v031", V031), ("v032", HERE)):
        for directory in (ROOT, V031, HERE):
            for candidate in directory.glob(f"{package_name}.*"):
                if (
                    candidate.is_file()
                    and candidate.suffix.lower() in executable_suffixes
                ):
                    raise RuntimeError(f"local package shadow is forbidden: {candidate}")
            package_directory = directory / package_name
            if package_directory.is_dir() and (
                package_directory.resolve() != expected_directory.resolve()
            ):
                raise RuntimeError(
                    f"local package shadow is forbidden: {package_directory}"
                )
        if not expected_directory.is_dir():
            raise RuntimeError(f"registered package path is missing: {package_name}")
    return {"passed": True, "registered_module_count": len(expected_modules) + 2}


def _validate_v031_abort_evidence() -> dict[str, Any]:
    attempt = _load_json_stdlib(V031_INVALID_ATTEMPT_PATH)
    expected = {
        "schema": "komorebi.neuralese.entry_cone_holonomy.invalid_attempt.v1",
        "version": "0.3.1",
        "author": AUTHOR,
        "status": "ABORTED_FAIL_CLOSED",
        "error_type": "ValueError",
        "error": "lineage regression mismatch for checkpoint 0",
        "registered_result_created": False,
    }
    for field, value in expected.items():
        if attempt.get(field) != value:
            raise ValueError(f"v0.3.1 abort evidence mismatch: {field}")
    if V031_RUN_STARTED_PATH.exists() or V031_RESULT_PATH.exists():
        raise ValueError("v0.3.1 unexpectedly crossed its run-start boundary")
    return {
        "passed": True,
        "invalid_attempt_sha256": _file_sha256_stdlib(V031_INVALID_ATTEMPT_PATH),
        "run_started_ledger_absent": True,
        "registered_result_absent": True,
        "sha256_bootstrap_checkpoint_byte_reads": "performed",
        "restricted_checkpoint_deserialization": "not_performed",
        "status": "V031_ABORTED_BEFORE_LEDGER_AND_CHECKPOINT_DESERIALIZATION",
    }


def _bootstrap_validate_frozen_bytes() -> dict[str, Any]:
    """Authenticate v0.3.2 and nested v0.3.1 bytes using only stdlib."""

    global _AUTHENTICATED_PYTHON_SOURCE_BYTES

    v032_path = HERE / "V032_EXECUTION_FREEZE.json"
    v032 = _load_json_stdlib(v032_path)
    if (
        v032.get("schema") != _V032_FREEZE_SCHEMA
        or v032.get("version") != VERSION
        or v032.get("author") != AUTHOR
        or v032.get("status") != _V032_FREEZE_STATUS
    ):
        raise ValueError("v0.3.2 execution-freeze identity or status mismatch")
    expected_outputs = {
        "registered_run_started": "results/V032_RUN_STARTED.json",
        "registered_invalid_attempt": "results/V032_INVALID_ATTEMPT.json",
        "registered_result": "results/V032_ENTRY_CONE_HOLONOMY_RESULTS.json",
        "alternate_profiles": "forbidden",
        "overwrite": "forbidden",
    }
    if v032.get("registered_outputs") != expected_outputs:
        raise ValueError("v0.3.2 registered outputs changed")
    expected_runtime = {
        "python_implementation": EXPECTED_PYTHON_IMPLEMENTATION,
        "python_version": EXPECTED_PYTHON_VERSION,
        "numpy_version": EXPECTED_NUMPY_VERSION,
    }
    if v032.get("runtime_contract") != expected_runtime:
        raise ValueError("v0.3.2 runtime contract changed")
    if v032.get("inherited_scientific_profile") != _EXPECTED_INHERITED_PROFILE:
        raise ValueError("v0.3.2 inherited scientific profile changed")
    if v032.get("attestation") != _EXPECTED_ATTESTATION:
        raise ValueError("v0.3.2 preexecution attestation changed")
    v032_files = _validate_digest_map(
        v032.get("files"), _V032_REQUIRED_FILES, "v0.3.2 execution freeze"
    )

    v031_path = V031 / "V031_EXECUTION_FREEZE.json"
    v031_freeze_sha256 = _file_sha256_stdlib(v031_path)
    if v031_freeze_sha256 != EXPECTED_V031_EXECUTION_FREEZE_SHA256:
        raise ValueError("historical v0.3.1 execution-freeze digest mismatch")
    v031 = _load_json_stdlib(v031_path)
    if (
        v031.get("schema") != _V031_FREEZE_SCHEMA
        or v031.get("version") != "0.3.1"
        or v031.get("author") != AUTHOR
        or v031.get("status") != _V031_FREEZE_STATUS
    ):
        raise ValueError("nested v0.3.1 execution-freeze identity mismatch")
    v031_files = _validate_digest_map(
        v031.get("files"), _V031_REQUIRED_FILES, "nested v0.3.1 execution freeze"
    )
    v031_profile = dict(v031.get("registered_profile", {}))
    for field in (
        "registered_run_started",
        "registered_result",
        "runtime_contract",
        "alternate_profiles",
        "overwrite",
    ):
        v031_profile.pop(field, None)
    if v031_profile != _EXPECTED_INHERITED_PROFILE:
        raise ValueError("nested v0.3.1 scientific profile changed")
    abort = _validate_v031_abort_evidence()
    if v032.get("v031_execution_freeze_sha256") != v031_freeze_sha256:
        raise ValueError("v0.3.1 execution-freeze digest attestation changed")
    if v032.get("v031_invalid_attempt_sha256") != abort["invalid_attempt_sha256"]:
        raise ValueError("v0.3.1 invalid-attempt digest attestation changed")
    if v032.get("v031_abort_boundary") != _EXPECTED_V031_ABORT_BOUNDARY:
        raise ValueError("v0.3.1 abort-boundary attestation changed")
    authenticated_sources: dict[Path, bytes] = {}
    for relative, expected in {**v031_files, **v032_files}.items():
        if not relative.endswith(".py"):
            continue
        path = _safe_root_file(relative).resolve()
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError(f"authenticated source changed during capture: {relative}")
        authenticated_sources[path] = payload
    _AUTHENTICATED_PYTHON_SOURCE_BYTES = authenticated_sources
    return {
        "v032_execution_freeze_sha256": _file_sha256_stdlib(v032_path),
        "v032_file_count": len(v032_files),
        "v031_execution_freeze_sha256": v031_freeze_sha256,
        "v031_frozen_file_count": len(v031_files),
        "v031_abort_evidence": abort,
        "authenticated_python_source_count": len(authenticated_sources),
    }


# This boundary deliberately precedes NumPy, checkpoint I/O, and every local
# scientific import.
if __name__ == "__main__":
    _reject_executable_bytecode()
    _reject_local_import_shadowing()
    _BOOTSTRAP_RECORD = _bootstrap_validate_frozen_bytes()
    _BOOTSTRAP_AUTHENTICATED = True

if (
    platform.python_implementation() != EXPECTED_PYTHON_IMPLEMENTATION
    or platform.python_version() != EXPECTED_PYTHON_VERSION
):
    raise RuntimeError(
        "registered runtime requires "
        f"{EXPECTED_PYTHON_IMPLEMENTATION} {EXPECTED_PYTHON_VERSION}; observed "
        f"{platform.python_implementation()} {platform.python_version()}"
    )

import numpy as np

if np.__version__ != EXPECTED_NUMPY_VERSION:
    raise RuntimeError(
        f"registered runtime requires NumPy {EXPECTED_NUMPY_VERSION}; "
        f"observed {np.__version__}"
    )

def _load_registered_local_module(name: str, path: Path) -> Any:
    """Execute one authenticated local source by exact path, never by search path."""

    if name in sys.modules:
        raise ImportError(f"registered module name already exists: {name}")
    resolved = path.resolve()
    if _BOOTSTRAP_AUTHENTICATED:
        try:
            payload = _AUTHENTICATED_PYTHON_SOURCE_BYTES[resolved]
        except KeyError as error:
            raise ImportError(f"authenticated source bytes are missing: {path}") from error
    else:
        payload = resolved.read_bytes()
    specification = importlib.util.spec_from_loader(name, loader=None, origin=str(resolved))
    if specification is None:
        raise ImportError(f"cannot construct registered module spec: {path}")
    module = importlib.util.module_from_spec(specification)
    module.__file__ = str(resolved)
    sys.modules[name] = module
    try:
        code = compile(payload, str(resolved), "exec", dont_inherit=True)
        exec(code, module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    if Path(module.__file__).resolve() != resolved:
        raise ImportError(f"registered module origin changed: {name}")
    return module


# Dependency order is explicit. The effective import search path remains the
# isolated interpreter's standard-library/site-packages path; authenticated
# project sources are loaded only from their registered absolute paths.
checkpoint_io = _load_registered_local_module("checkpoint_io", ROOT / "checkpoint_io.py")
_load_registered_local_module("core", ROOT / "core.py")
_load_registered_local_module(
    "entry_recurrence_probe", V031 / "entry_recurrence_probe.py"
)
_load_registered_local_module("freeze_v031", V031 / "freeze_v031.py")
_load_registered_local_module(
    "holonomy_spectroscopy", V031 / "holonomy_spectroscopy.py"
)
_load_registered_local_module("matched_controls", V031 / "matched_controls.py")
_load_registered_local_module("v031_engine", V031 / "v031_engine.py")
_isolated_search_path = list(sys.path)
try:
    frozen_v031 = _load_registered_local_module(
        "_komorebi_frozen_v031_runner", V031 / "run_v031.py"
    )
finally:
    sys.path[:] = _isolated_search_path
if sys.path != _isolated_search_path:
    raise RuntimeError("failed to restore isolated import search path")
if _BOOTSTRAP_AUTHENTICATED:
    local_search_roots = {ROOT.resolve(), V031.resolve(), HERE.resolve()}
    for entry in sys.path:
        if entry and Path(entry).resolve() in local_search_roots:
            raise RuntimeError("local project directory entered isolated import path")
correction_freeze = _load_registered_local_module(
    "_komorebi_v032_correction_freeze", HERE / "freeze_v032.py"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _refuse_existing_execution_artifacts() -> None:
    for path in (RUN_STARTED_PATH, INVALID_ATTEMPT_PATH, RESULT_PATH):
        if path.exists():
            raise FileExistsError(
                "refusing learned-endpoint execution because a v0.3.2 execution "
                f"artifact already exists: {path}"
            )


def _acquire_execution_lock() -> int:
    """Exclusively claim the frozen execution record without a new lock file."""

    path = HERE / "V032_EXECUTION_FREEZE.json"
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    descriptor = os.open(path, flags)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _release_execution_lock(descriptor: int) -> None:
    try:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def _validate_runtime_contract() -> dict[str, Any]:
    observed = {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
    }
    expected = {
        "python_implementation": EXPECTED_PYTHON_IMPLEMENTATION,
        "python_version": EXPECTED_PYTHON_VERSION,
        "numpy_version": EXPECTED_NUMPY_VERSION,
    }
    if observed != expected:
        raise RuntimeError(f"registered runtime mismatch: {observed!r} != {expected!r}")
    return {"passed": True, "expected": expected, "observed": observed}


def _validate_module_locations() -> None:
    if Path(frozen_v031.__file__).resolve() != (V031 / "run_v031.py").resolve():
        raise ImportError("v0.3.1 runner module collision")
    if Path(correction_freeze.__file__).resolve() != (HERE / "freeze_v032.py").resolve():
        raise ImportError("v0.3.2 freeze module collision")
    frozen_v031._validate_module_locations()


def _validate_lineage_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate real seed aggregates and derive merge maxima from episodes."""

    expected_root_keys = {
        "schema",
        "purpose",
        "expected_decisions_per_seed",
        "expected_accuracy",
        "expected_maximum_split_multiplicity",
        "seeds",
        "passed",
        "runner_sha256",
    }
    if set(value) != expected_root_keys:
        raise ValueError("lineage regression root keys changed")

    if value.get("schema") != "komorebi.neuralese.v0.2.1.lineage_regression.v1":
        raise ValueError("lineage regression schema mismatch")
    if (
        value.get("purpose")
        != "Reproduce the already-known v0.2.1 ordinary exact-L6/H3 hard endpoint; this is not a new v0.3.0 scientific result."
        or
        value.get("expected_accuracy") != 1.0
        or value.get("expected_decisions_per_seed") != 61_440
        or value.get("expected_maximum_split_multiplicity") != 1
        or not bool(value.get("passed"))
    ):
        raise ValueError("lineage regression root contract mismatch")
    seeds = value.get("seeds")
    if not isinstance(seeds, Mapping) or set(seeds) != {"0", "1"}:
        raise ValueError("lineage checkpoint keys changed")

    seed_validations: dict[str, Any] = {}
    total_decisions = 0
    total_correct = 0
    for seed in ("0", "1"):
        record = seeds[seed]
        if not isinstance(record, Mapping):
            raise ValueError(f"lineage checkpoint {seed} is not an object")
        expected_seed_keys = {
            "audited_first_episode_count",
            "correct_decision_count",
            "decision_count",
            "episode_seed",
            "episodes",
            "future_horizon",
            "future_mode",
            "history_depth",
            "history_mode",
            "maximum_split_multiplicity",
            "passed",
            "sampled_batch_size",
            "semantic_continuation_accuracy",
        }
        if set(record) != expected_seed_keys:
            raise ValueError(f"lineage checkpoint {seed} keys changed")
        expected_episode_seed = 910_000 + 1_000 * int(seed)
        aggregate_expected = {
            "audited_first_episode_count": 8,
            "correct_decision_count": 61_440,
            "decision_count": 61_440,
            "episode_seed": expected_episode_seed,
            "future_horizon": 3,
            "future_mode": "cumulative",
            "history_depth": 6,
            "history_mode": "exact",
            "maximum_split_multiplicity": 1,
            "passed": True,
            "sampled_batch_size": 64,
            "semantic_continuation_accuracy": 1.0,
        }
        for field, expected in aggregate_expected.items():
            if record.get(field) != expected:
                raise ValueError(
                    f"lineage aggregate mismatch for checkpoint {seed}: {field}"
                )
        episodes = record.get("episodes")
        if not isinstance(episodes, list) or len(episodes) != 8:
            raise ValueError(f"lineage episode panel changed for checkpoint {seed}")
        maximum_merge = 0
        episode_decisions = 0
        for expected_index, episode in enumerate(episodes):
            if not isinstance(episode, Mapping):
                raise ValueError("lineage episode is not an object")
            expected_episode_keys = {
                "decision_count",
                "episode_index",
                "maximum_merge_multiplicity",
                "maximum_split_multiplicity",
                "minimum_target_margin",
                "passed",
                "semantic_continuation_accuracy",
                "signature_class_count",
            }
            if set(episode) != expected_episode_keys:
                raise ValueError(
                    f"lineage episode keys changed for checkpoint {seed}, "
                    f"episode {expected_index}"
                )
            expected_fields = {
                "episode_index": expected_index,
                "decision_count": 7_680,
                "maximum_merge_multiplicity": 1,
                "maximum_split_multiplicity": 1,
                "passed": True,
                "semantic_continuation_accuracy": 1.0,
                "signature_class_count": 8,
            }
            for field, expected in expected_fields.items():
                if episode.get(field) != expected:
                    raise ValueError(
                        f"lineage episode mismatch for checkpoint {seed}, "
                        f"episode {expected_index}: {field}"
                    )
            margin = episode.get("minimum_target_margin")
            if not isinstance(margin, (int, float)) or not np.isfinite(margin) or margin <= 0:
                raise ValueError("lineage episode has invalid minimum target margin")
            maximum_merge = max(maximum_merge, int(episode["maximum_merge_multiplicity"]))
            episode_decisions += int(episode["decision_count"])
        if maximum_merge != 1:
            raise ValueError(f"lineage merge multiplicity mismatch for checkpoint {seed}")
        if episode_decisions != int(record["decision_count"]):
            raise ValueError(f"lineage episode decision sum mismatch for checkpoint {seed}")
        total_decisions += int(record["decision_count"])
        total_correct += int(record["correct_decision_count"])
        seed_validations[seed] = {
            "passed": True,
            "decision_count": int(record["decision_count"]),
            "semantic_continuation_accuracy": float(
                record["semantic_continuation_accuracy"]
            ),
            "maximum_split_multiplicity": int(
                record["maximum_split_multiplicity"]
            ),
            "derived_maximum_merge_multiplicity": maximum_merge,
            "episode_count": len(episodes),
        }
    if total_decisions != 122_880 or total_correct != 122_880:
        raise ValueError("lineage cross-check totals changed")
    return {
        "passed": True,
        "seeds": seed_validations,
        "total_episode_count": 16,
        "total_decision_count": total_decisions,
        "total_correct_decision_count": total_correct,
    }


def _validate_lineage() -> dict[str, Any]:
    path = ROOT / "results" / "LINEAGE_REGRESSION.json"
    value = _load_json_stdlib(path)
    runner_path = ROOT / "run_lineage_regression.py"
    root_freeze_path = ROOT / "EXECUTION_FREEZE.json"
    runner_sha256 = _file_sha256_stdlib(runner_path)
    root_freeze = _load_json_stdlib(root_freeze_path)
    if value.get("runner_sha256") != runner_sha256:
        raise ValueError("lineage runner digest does not match the lineage record")
    if root_freeze.get("files", {}).get("run_lineage_regression.py") != runner_sha256:
        raise ValueError("lineage runner digest does not match the root execution freeze")
    validated = _validate_lineage_payload(value)
    return {
        **validated,
        "path": str(path),
        "sha256": checkpoint_io.file_sha256(path),
        "runner_sha256": runner_sha256,
        "correction": (
            "seed-level aggregates validated; maximum merge multiplicity derived "
            "from the eight authenticated episode records per checkpoint"
        ),
    }


def _create_run_started_ledger(
    correction_validation: Mapping[str, Any], abort_validation: Mapping[str, Any]
) -> dict[str, Any]:
    global _RUN_STARTED_LEDGER_OWNED
    frozen_v031.atomic_create_json(
        RUN_STARTED_PATH,
        {
            "schema": "komorebi.neuralese.entry_cone_holonomy.run_started.v2",
            "version": VERSION,
            "author": AUTHOR,
            "status": "CREATED_BEFORE_LEARNED_CHECKPOINT_LOADING",
            "utc": utc_now(),
            "execution_freeze_sha256": correction_validation["freeze_sha256"],
            "v031_execution_freeze_sha256": correction_validation[
                "v031_execution_freeze_sha256"
            ],
            "v031_abort_evidence_sha256": abort_validation[
                "invalid_attempt_sha256"
            ],
            "registered_result": str(RESULT_PATH),
            "registered_invalid_attempt": str(INVALID_ATTEMPT_PATH),
            "runtime_contract": {
                "python_implementation": platform.python_implementation(),
                "python_version": platform.python_version(),
                "numpy_version": np.__version__,
            },
        },
    )
    _RUN_STARTED_LEDGER_OWNED = True
    _fsync_parent_directory(RUN_STARTED_PATH)
    return {
        "passed": True,
        "path": str(RUN_STARTED_PATH),
        "sha256": _file_sha256_stdlib(RUN_STARTED_PATH),
        "status": "CREATED_BEFORE_LEARNED_CHECKPOINT_LOADING",
    }


def _fsync_parent_directory(path: Path) -> None:
    directory_fd = os.open(Path(path).parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _read_authenticated_checkpoint_bytes(path: Path, expected_sha256: str) -> bytes:
    """Read one stable checkpoint inode once and authenticate those exact bytes."""

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
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
    if identity_before != identity_after:
        raise RuntimeError(f"checkpoint changed during authenticated read: {path}")
    payload = b"".join(chunks)
    if len(payload) != before.st_size:
        raise RuntimeError(f"checkpoint byte count changed during read: {path}")
    observed = hashlib.sha256(payload).hexdigest()
    if observed != expected_sha256:
        raise ValueError(
            f"checkpoint digest mismatch for {path.name}: {observed} != {expected_sha256}"
        )
    return payload


def _load_checkpoint_from_authenticated_snapshot(
    source: Path, expected_sha256: str, snapshot_directory: Path
) -> Any:
    """Deserialize a private read-only snapshot of one authenticated byte read."""

    payload = _read_authenticated_checkpoint_bytes(source, expected_sha256)
    snapshot = Path(snapshot_directory) / source.name
    descriptor = os.open(snapshot, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o400)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("failed to write authenticated checkpoint snapshot")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    checkpoint = checkpoint_io.load_checkpoint(snapshot, expected_sha256)
    if checkpoint.sha256 != expected_sha256:
        raise ValueError("restricted loader returned a nonauthenticated checkpoint")
    if _file_sha256_stdlib(snapshot) != expected_sha256:
        raise RuntimeError("private checkpoint snapshot changed during deserialization")
    return checkpoint


def _assemble_composites(
    entry_results: Mapping[str, Any],
    cone_results: Mapping[str, Any],
    relation_results: Mapping[str, Any],
    matched_results: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, bool]]:
    integrity_gates = {
        "lineage_integrity": True,
        **entry_results["integrity_gates"],
        **cone_results["integrity_gates"],
        **relation_results["integrity_gates"],
        **matched_results["integrity_gates"],
    }
    diagnostic_predicates = {
        **entry_results["diagnostic_predicates"],
        **cone_results["diagnostic_predicates"],
        **relation_results["diagnostic_predicates"],
        **matched_results["diagnostic_predicates"],
    }
    entry_localized = bool(
        all(entry_results["integrity_gates"].values())
        and all(entry_results["diagnostic_predicates"].values())
    )
    cone_safe = bool(
        cone_results["integrity_gates"][
            "K1_direct_and_recursive_suffix_audits_agree"
        ]
        and cone_results["diagnostic_predicates"][
            "K0_all_observed_recurrent_states_survive_H8"
        ]
    )
    cone_robust = bool(
        cone_safe
        and cone_results["diagnostic_predicates"][
            "K2_all_angular_clearances_exceed_1e_minus_10"
        ]
    )
    relation_valid = bool(all(relation_results["integrity_gates"].values()))
    long_path_exit = bool(
        relation_valid
        and relation_results["diagnostic_predicates"][
            "H1_at_least_one_fresh_cone_exit_by_64_tokens"
        ]
    )
    composites = {
        "entry_localized_finite": entry_localized,
        "finite_observed_cone_safe": cone_safe,
        "finite_observed_cone_robust": cone_robust,
        "registered_long_path_exit": long_path_exit,
        "registered_broadly_replicated_long_path_exit": bool(
            long_path_exit
            and relation_results["diagnostic_predicates"][
                "H2_same_relation_repeat_exit_in_all_checkpoint_half_strata"
            ]
        ),
        "registered_delayed_reveal": bool(
            long_path_exit
            and relation_results["diagnostic_predicates"][
                "H3_at_least_one_delayed_hard_reveal"
            ]
        ),
        "matched_panel_interpretable": bool(
            all(matched_results["integrity_gates"].values())
        ),
        "full_finite_factorization": bool(entry_localized and cone_safe and long_path_exit),
    }
    return integrity_gates, diagnostic_predicates, composites


CLAIM_BOUNDARY = [
    "two frozen eight-state D4 systems only",
    "fresh coordinate episodes are not held-out task-family support",
    "finite observed-state cone membership is not ambient or infinite closure",
    "spectra describe ambient projective mechanisms, not a causal quotient certificate",
    "deterministic controls do not define a population of words or models",
    "long-path and matched conclusions use only the registered 64-case deterministic transversal per episode and suffixes through H=8",
    "old 930000/931000 relation spectroscopy and continuation outcomes are exploratory design context; fresh endpoints are adaptive-developmental and nonconfirmatory",
    "no causal-quotient minimality claim",
    "no global invariant metric or normally attracting fiber claim",
    "no spontaneous, universal, or architecture-independent Neuralese claim",
]


def run_registered() -> dict[str, Any]:
    if not _BOOTSTRAP_AUTHENTICATED or _BOOTSTRAP_RECORD is None:
        raise RuntimeError(
            "run_registered is available only through the authenticated direct CLI"
        )
    started_wall = utc_now()
    started = time.perf_counter()
    _refuse_existing_execution_artifacts()
    runtime_validation = _validate_runtime_contract()
    _validate_module_locations()
    correction_validation = correction_freeze.validate_execution_freeze(
        HERE / "V032_EXECUTION_FREEZE.json", ROOT
    )
    inherited_freeze_validation = frozen_v031.freeze.validate_execution_freeze(
        V031 / "V031_EXECUTION_FREEZE.json", ROOT
    )
    prereg_validation = correction_freeze.validate_preregistration(
        HERE / "V032_PREREGISTRATION.json"
    )
    frozen_input_validation = frozen_v031.freeze.validate_frozen_inputs(
        V031 / "V031_FROZEN_INPUTS.json"
    )
    word_bank_validation = frozen_v031.freeze.validate_matched_word_bank(
        V031 / "V031_MATCHED_WORD_BANK.json"
    )
    lineage_validation = _validate_lineage()
    abort_validation = _validate_v031_abort_evidence()
    input_payload = _load_json_stdlib(V031 / "V031_FROZEN_INPUTS.json")
    bank = _load_json_stdlib(V031 / "V031_MATCHED_WORD_BANK.json")
    frozen_v031.progress(
        "v0.3.2 freeze, inherited v0.3.1 bytes, abort evidence, inputs, bank, "
        "and corrected lineage validated"
    )

    if os.environ.get("KOMOREBI_V032_PREENDPOINT_STRUCTURAL_ONLY") == "1":
        raise RuntimeError(
            "learned checkpoint loading is forbidden under the v0.3.2 "
            "preendpoint structural-only guard"
        )
    run_started_validation = _create_run_started_ledger(
        correction_validation, abort_validation
    )
    frozen_v031.progress(
        "irreversible v0.3.2 run-start ledger created before checkpoint loading"
    )

    checkpoints: dict[int, Any] = {}
    with tempfile.TemporaryDirectory(prefix="komorebi-v032-checkpoints-") as temporary:
        snapshot_directory = Path(temporary)
        os.chmod(snapshot_directory, 0o700)
        for seed in (0, 1):
            path = ROOT / "checkpoints" / f"projective_terminal_seed{seed}.pt"
            checkpoint = _load_checkpoint_from_authenticated_snapshot(
                path,
                frozen_v031.CHECKPOINT_DIGESTS[seed],
                snapshot_directory,
            )
            if int(checkpoint.metadata.get("config", {}).get("seed", -1)) != seed:
                raise ValueError(f"checkpoint metadata seed mismatch for seed {seed}")
            checkpoints[seed] = checkpoint
    frozen_v031.progress("restricted checkpoint loading completed")

    contexts = frozen_v031.build_contexts(checkpoints, input_payload)
    entry_results = frozen_v031.run_entry_module(
        checkpoints, contexts, input_payload
    )
    frozen_v031.progress("entry module complete")
    cone_results = frozen_v031.run_cone_module(contexts)
    frozen_v031.progress("finite observed-state cone module complete")
    relation_results = frozen_v031.run_relation_module(contexts)
    frozen_v031.progress("dense relation and spectroscopy module complete")
    matched_results = frozen_v031.run_matched_module(contexts, bank)
    frozen_v031.progress("matched-control module complete")

    integrity_gates, diagnostic_predicates, composites = _assemble_composites(
        entry_results, cone_results, relation_results, matched_results
    )
    elapsed = time.perf_counter() - started
    return {
        "schema": "komorebi.neuralese.entry_cone_holonomy.result.v1",
        "version": VERSION,
        "author": AUTHOR,
        "status": "REGISTERED_EXECUTION_COMPLETE",
        "scientific_class": "prospectively_frozen_adaptive_developmental_diagnostic",
        "scientific_design_version": "0.3.1",
        "correction_runner_version": VERSION,
        "integrity": {
            "runtime_contract": runtime_validation,
            "run_started_ledger": run_started_validation,
            "execution_freeze": correction_validation,
            "inherited_v031_execution_freeze": inherited_freeze_validation,
            "v031_abort_evidence": abort_validation,
            "preregistration": prereg_validation,
            "frozen_inputs": frozen_input_validation,
            "matched_word_bank": word_bank_validation,
            "lineage": lineage_validation,
            "checkpoint_sha256": {
                str(seed): checkpoints[seed].sha256 for seed in (0, 1)
            },
        },
        "entry": entry_results,
        "finite_observed_cones": cone_results,
        "relations": relation_results,
        "matched_controls": matched_results,
        "integrity_gates": integrity_gates,
        "diagnostic_predicates": diagnostic_predicates,
        "preregistered_composites": composites,
        "claim_boundary": list(CLAIM_BOUNDARY),
        "execution": {
            "started_utc": started_wall,
            "finished_utc": utc_now(),
            "elapsed_seconds": elapsed,
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "registered_output": str(RESULT_PATH),
            "run_started_ledger": str(RUN_STARTED_PATH),
            "alternate_profiles": "not accepted",
            "overwrite": "refused",
            "correction_lineage": (
                "v0.3.1 bootstrap authenticated raw checkpoint bytes but aborted "
                "before its ledger and restricted checkpoint deserialization; "
                "v0.3.2 reuses its frozen scientific computation"
            ),
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    execution_lock = _acquire_execution_lock()
    try:
        _refuse_existing_execution_artifacts()
        try:
            result = run_registered()
            frozen_v031.atomic_create_json(RESULT_PATH, result)
            _fsync_parent_directory(RESULT_PATH)
        except Exception as error:
            attempt = {
                "schema": "komorebi.neuralese.entry_cone_holonomy.invalid_attempt.v2",
                "version": VERSION,
                "author": AUTHOR,
                "status": "ABORTED_FAIL_CLOSED",
                "utc": utc_now(),
                "error_type": type(error).__name__,
                "error": str(error),
                "registered_result_created": False,
            }
            should_record_invalid = bool(
                not RESULT_PATH.exists()
                and (_RUN_STARTED_LEDGER_OWNED or not RUN_STARTED_PATH.exists())
            )
            if should_record_invalid and not INVALID_ATTEMPT_PATH.exists():
                frozen_v031.atomic_create_json(INVALID_ATTEMPT_PATH, attempt)
                _fsync_parent_directory(INVALID_ATTEMPT_PATH)
            raise
    finally:
        _release_execution_lock(execution_lock)
    print(f"V032_RESULT={RESULT_PATH}")
    print(f"V032_RESULT_SHA256={checkpoint_io.file_sha256(RESULT_PATH)}")
    print(f"V032_ELAPSED_SECONDS={result['execution']['elapsed_seconds']:.6f}")
    for name, passed in result["integrity_gates"].items():
        print(f"{name}={'PASS' if passed else 'FAIL'}")
    for name, observed in result["diagnostic_predicates"].items():
        rendered = (
            "INVALID_UNDER_REGISTERED_PRECONDITION"
            if observed is None
            else ("TRUE" if observed else "FALSE")
        )
        print(f"{name}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
