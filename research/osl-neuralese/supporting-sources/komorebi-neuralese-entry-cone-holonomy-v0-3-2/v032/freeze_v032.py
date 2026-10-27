#!/usr/bin/env python3
"""Create and validate the fail-closed Neuralese v0.3.2 correction freeze.

Author: Komorebi P.

This script performs structural validation and byte hashing only.  It never
imports checkpoint I/O, NumPy, or a learned scientific module and never
deserializes a checkpoint.
"""

from __future__ import annotations

import sys


if __name__ == "__main__" and sys.flags.isolated != 1:
    raise RuntimeError(
        "freeze creation requires isolated mode: python -I -B v032/freeze_v032.py"
    )

import argparse
import ast
import hashlib
import json
import os
import platform
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "komorebi.neuralese.entry_cone_holonomy.correction_execution_freeze.v1"
VERSION = "0.3.2"
AUTHOR = "Komorebi P."
STATUS = "FROZEN_BEFORE_V032_LEARNED_ENDPOINT_EXECUTION"
TARGET_NAME = "V032_EXECUTION_FREEZE.json"
EXPECTED_PYTHON_IMPLEMENTATION = "CPython"
EXPECTED_PYTHON_VERSION = "3.12.13"
EXPECTED_NUMPY_VERSION = "2.3.5"
EXPECTED_V031_EXECUTION_FREEZE_SHA256 = (
    "2600536f3009ed4294bad0432680021915d2b17a15fe6ab973bd835061f7f662"
)
EXPECTED_V031_INVALID_SHA256 = (
    "e72b827ba30f7f3d16a5ff8837c5cec5716ebc20914982e98944c417db785f64"
)
EXPECTED_REQUIREMENTS = "numpy==2.3.5\n"
EXPECTED_UNIT_TEST_COUNT = 15
EXPECTED_ATTESTATION = (
    "No v0.3.2 learned endpoint was inspected before this correction freeze "
    "was written. The v0.3.1 bootstrap read checkpoint bytes only to verify "
    "their SHA-256 digests; v0.3.1 aborted before its run-start ledger, before "
    "restricted checkpoint deserialization, and before endpoint evaluation."
)
EXPECTED_V031_ABORT_BOUNDARY = {
    "registered_result_absent": True,
    "restricted_checkpoint_deserialization": "not_performed",
    "run_started_ledger_absent": True,
    "sha256_bootstrap_checkpoint_byte_reads": "performed",
    "status": "V031_ABORTED_BEFORE_LEDGER_AND_CHECKPOINT_DESERIALIZATION",
}
EXPECTED_CORRECTION_CHANGED = (
    "The only scientific acceptance-logic change is that the execution wrapper "
    "validates seed-level lineage aggregates where they exist and derives "
    "maximum merge multiplicity from all authenticated per-episode records. "
    "Operational integrity is additionally hardened with isolated-mode startup, "
    "exact-path authenticated module loading, private read-only checkpoint "
    "snapshots, and durable one-shot artifact ownership."
)
EXPECTED_CORRECTION_UNCHANGED = (
    "Every v0.3.1 frozen scientific input, scientific module, checkpoint, "
    "episode, word, grid, gate, composite, and claim boundary."
)
EXPECTED_PREREG_ABORT_TEXT = (
    "V031 bootstrap read both checkpoint files only as raw bytes for SHA-256 "
    "authentication; it aborted before creation of V031_RUN_STARTED.json, "
    "before restricted checkpoint deserialization, and before fresh endpoint "
    "execution."
)

REQUIRED_ROOT_RELATIVE_FILES: tuple[str, ...] = (
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
)

V031_REQUIRED_ROOT_RELATIVE_FILES: tuple[str, ...] = (
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
)

EXPECTED_OUTPUTS = {
    "registered_run_started": "results/V032_RUN_STARTED.json",
    "registered_invalid_attempt": "results/V032_INVALID_ATTEMPT.json",
    "registered_result": "results/V032_ENTRY_CONE_HOLONOMY_RESULTS.json",
    "alternate_profiles": "forbidden",
    "overwrite": "forbidden",
}

EXPECTED_RUNTIME = {
    "python_implementation": EXPECTED_PYTHON_IMPLEMENTATION,
    "python_version": EXPECTED_PYTHON_VERSION,
    "numpy_version": EXPECTED_NUMPY_VERSION,
}

EXPECTED_PROFILE = {
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

EXPECTED_CLAIM_BOUNDARY = [
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


class FreezeValidationError(ValueError):
    """Raised when a correction-freeze invariant fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FreezeValidationError(message)


def _duplicate_rejector(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise FreezeValidationError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def load_json(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle, object_pairs_hook=_duplicate_rejector)
    _require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_file(root: Path, relative: str) -> Path:
    root = Path(root).resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise FreezeValidationError(f"unsafe frozen path: {relative}") from error
    _require(candidate.is_file(), f"required frozen file is missing: {relative}")
    return candidate


def _require_exact_keys(
    observed: Iterable[Any], expected: Iterable[Any], label: str
) -> None:
    observed_set = set(observed)
    expected_set = set(expected)
    _require(
        observed_set == expected_set,
        f"{label} key mismatch; missing={sorted(expected_set-observed_set)}; "
        f"extra={sorted(observed_set-expected_set)}",
    )


def validate_no_executable_bytecode(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    pyc = sorted(str(path.relative_to(root)) for path in root.rglob("*.pyc"))
    caches = sorted(
        str(path.relative_to(root)) for path in root.rglob("__pycache__")
    )
    _require(not pyc and not caches, f"remove executable caches: pyc={pyc}, dirs={caches}")
    return {"passed": True, "pyc_file_count": 0, "pycache_directory_count": 0}


def validate_v031_frozen_bytes(
    root: Path, *, include_checkpoint_bytes: bool = True
) -> dict[str, Any]:
    root = Path(root).resolve()
    freeze_path = root / "v031" / "V031_EXECUTION_FREEZE.json"
    freeze_sha256_before = file_sha256(freeze_path)
    _require(
        freeze_sha256_before == EXPECTED_V031_EXECUTION_FREEZE_SHA256,
        "historical v0.3.1 execution-freeze digest mismatch",
    )
    value = load_json(freeze_path)
    _require(
        value.get("schema")
        == "komorebi.neuralese.entry_cone_holonomy.execution_freeze.v1",
        "v0.3.1 freeze schema mismatch",
    )
    _require(value.get("version") == "0.3.1", "v0.3.1 version mismatch")
    _require(value.get("author") == AUTHOR, "v0.3.1 author mismatch")
    _require(
        value.get("status") == "FROZEN_BEFORE_FRESH_LEARNED_ENDPOINT_EXECUTION",
        "v0.3.1 freeze status mismatch",
    )
    files = value.get("files")
    _require(isinstance(files, dict), "v0.3.1 digest map is missing")
    _require_exact_keys(files, V031_REQUIRED_ROOT_RELATIVE_FILES, "v0.3.1 digest map")
    checkpoint_paths = {
        "checkpoints/projective_terminal_seed0.pt",
        "checkpoints/projective_terminal_seed1.pt",
    }
    validated_file_count = 0
    for relative, expected in files.items():
        _require(
            isinstance(expected, str) and len(expected) == 64,
            f"invalid v0.3.1 digest: {relative}",
        )
        if not include_checkpoint_bytes and relative in checkpoint_paths:
            _require(
                not (root / relative).exists(),
                f"checkpoint unexpectedly present in structural sandbox: {relative}",
            )
            continue
        _require(
            file_sha256(_safe_file(root, relative)) == expected,
            f"v0.3.1 frozen byte changed: {relative}",
        )
        validated_file_count += 1
    _require(
        value.get("registered_profile", {}).get("runtime_contract") == EXPECTED_RUNTIME,
        "v0.3.1 runtime contract mismatch",
    )
    inherited_profile = dict(value["registered_profile"])
    for field in (
        "registered_run_started",
        "registered_result",
        "runtime_contract",
        "alternate_profiles",
        "overwrite",
    ):
        inherited_profile.pop(field, None)
    _require(inherited_profile == EXPECTED_PROFILE, "v0.3.1 scientific profile changed")
    freeze_sha256_after = file_sha256(freeze_path)
    _require(
        freeze_sha256_after == freeze_sha256_before,
        "v0.3.1 execution freeze changed during validation",
    )
    return {
        "passed": True,
        "freeze_sha256": freeze_sha256_after,
        "frozen_file_count": len(files),
        "validated_file_count": validated_file_count,
        "checkpoint_bytes_included": include_checkpoint_bytes,
    }


def validate_v031_abort_evidence(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    path = root / "results" / "V031_INVALID_ATTEMPT.json"
    value = load_json(path)
    expected = {
        "schema": "komorebi.neuralese.entry_cone_holonomy.invalid_attempt.v1",
        "version": "0.3.1",
        "author": AUTHOR,
        "status": "ABORTED_FAIL_CLOSED",
        "error_type": "ValueError",
        "error": "lineage regression mismatch for checkpoint 0",
        "registered_result_created": False,
    }
    for field, wanted in expected.items():
        _require(value.get(field) == wanted, f"v0.3.1 abort field mismatch: {field}")
    observed_sha256 = file_sha256(path)
    _require(
        observed_sha256 == EXPECTED_V031_INVALID_SHA256,
        "v0.3.1 invalid-attempt bytes changed",
    )
    _require(
        not (root / "results" / "V031_RUN_STARTED.json").exists(),
        "V031_RUN_STARTED.json exists",
    )
    _require(
        not (root / "results" / "V031_ENTRY_CONE_HOLONOMY_RESULTS.json").exists(),
        "V031 result exists",
    )
    return {
        "passed": True,
        "invalid_attempt_sha256": observed_sha256,
        "run_started_ledger_absent": True,
        "registered_result_absent": True,
        "sha256_bootstrap_checkpoint_byte_reads": "performed",
        "restricted_checkpoint_deserialization": "not_performed",
        "status": "V031_ABORTED_BEFORE_LEDGER_AND_CHECKPOINT_DESERIALIZATION",
    }


def validate_lineage_provenance(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    lineage = load_json(root / "results" / "LINEAGE_REGRESSION.json")
    root_freeze = load_json(root / "EXECUTION_FREEZE.json")
    runner_sha = file_sha256(root / "run_lineage_regression.py")
    _require(lineage.get("runner_sha256") == runner_sha, "lineage runner digest mismatch")
    _require(
        root_freeze.get("files", {}).get("run_lineage_regression.py") == runner_sha,
        "root freeze lineage-runner digest mismatch",
    )
    return {"passed": True, "runner_sha256": runner_sha}


def validate_requirements(root: Path) -> dict[str, Any]:
    path = Path(root).resolve() / "v032" / "requirements.txt"
    observed = path.read_text(encoding="utf-8")
    _require(observed == EXPECTED_REQUIREMENTS, "v0.3.2 requirements changed")
    return {"passed": True, "content": observed.rstrip("\n")}


def validate_v032_execution_artifacts_absent(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    paths = (
        root / "v032" / TARGET_NAME,
        root / "results" / "V032_RUN_STARTED.json",
        root / "results" / "V032_INVALID_ATTEMPT.json",
        root / "results" / "V032_ENTRY_CONE_HOLONOMY_RESULTS.json",
    )
    existing = [str(path.relative_to(root)) for path in paths if path.exists()]
    _require(not existing, f"v0.3.2 execution artifact already exists: {existing}")
    return {"passed": True, "absent_file_count": len(paths)}


def validate_preregistration(path: Path) -> dict[str, Any]:
    value = load_json(path)
    _require_exact_keys(
        value,
        {
            "schema",
            "version",
            "author",
            "status",
            "scientific_class",
            "correction",
            "inherited_profile",
            "registered_outputs",
            "runtime_contract",
            "claim_boundary",
        },
        "v0.3.2 preregistration",
    )
    _require(
        value.get("schema")
        == "komorebi.neuralese.entry_cone_holonomy.preregistration.v2",
        "v0.3.2 preregistration schema mismatch",
    )
    _require(value.get("version") == VERSION, "preregistration version mismatch")
    _require(value.get("author") == AUTHOR, "preregistration author mismatch")
    _require(
        value.get("status") == "REGISTERED_BEFORE_V032_LEARNED_ENDPOINT_EXECUTION",
        "preregistration status mismatch",
    )
    _require(
        value.get("scientific_class")
        == "prospectively_frozen_adaptive_developmental_diagnostic",
        "scientific class changed",
    )
    _require(value.get("inherited_profile") == EXPECTED_PROFILE, "profile changed")
    _require(value.get("registered_outputs") == EXPECTED_OUTPUTS, "outputs changed")
    _require(value.get("runtime_contract") == EXPECTED_RUNTIME, "runtime changed")
    _require(
        value.get("claim_boundary") == EXPECTED_CLAIM_BOUNDARY,
        "claim boundary changed",
    )
    correction = value.get("correction", {})
    _require_exact_keys(
        correction,
        {"changed", "unchanged", "v031_abort_boundary"},
        "v0.3.2 correction disclosure",
    )
    _require(
        correction.get("changed") == EXPECTED_CORRECTION_CHANGED,
        "correction scope changed",
    )
    _require(
        correction.get("unchanged") == EXPECTED_CORRECTION_UNCHANGED,
        "scientific inheritance claim changed",
    )
    _require(
        correction.get("v031_abort_boundary") == EXPECTED_PREREG_ABORT_TEXT,
        "v0.3.1 abort boundary changed",
    )
    return {"passed": True, "schema": value["schema"], "version": VERSION}


def validate_runner_contract(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    source = (root / "v032" / "run_v032.py").read_text(encoding="utf-8")
    tree = ast.parse(source, filename="v032/run_v032.py")

    def call_name(call: ast.Call) -> str:
        parts: list[str] = []
        cursor: ast.expr = call.func
        while isinstance(cursor, ast.Attribute):
            parts.append(cursor.attr)
            cursor = cursor.value
        if isinstance(cursor, ast.Name):
            parts.append(cursor.id)
        return ".".join(reversed(parts))

    def isolated_guard_line(parsed: ast.Module, label: str) -> int:
        candidates = [
            node
            for node in parsed.body
            if isinstance(node, ast.If)
            and "sys.flags.isolated" in ast.unparse(node.test)
            and "__name__" in ast.unparse(node.test)
        ]
        _require(len(candidates) == 1, f"{label} isolated-mode guard changed")
        guard_line = candidates[0].lineno
        sys_imports = [
            node.lineno
            for node in parsed.body
            if isinstance(node, ast.Import)
            and [alias.name for alias in node.names] == ["sys"]
        ]
        _require(len(sys_imports) == 1, f"{label} early sys import changed")
        other_imports = [
            node.lineno
            for node in parsed.body
            if isinstance(node, (ast.Import, ast.ImportFrom))
            and not (
                isinstance(node, ast.ImportFrom) and node.module == "__future__"
            )
            and node.lineno not in sys_imports
        ]
        _require(
            sys_imports[0] < guard_line < min(other_imports),
            f"{label} imports precede isolated-mode guard",
        )
        return guard_line

    isolated_line = isolated_guard_line(tree, "runner")
    freeze_source = (root / "v032" / "freeze_v032.py").read_text(encoding="utf-8")
    freeze_tree = ast.parse(freeze_source, filename="v032/freeze_v032.py")
    freeze_isolated_line = isolated_guard_line(freeze_tree, "freeze builder")

    run_nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "run_registered"
    ]
    _require(len(run_nodes) == 1, "runner must define run_registered exactly once")
    main_nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "main"
    ]
    _require(len(main_nodes) == 1, "runner must define main exactly once")
    calls = [node for node in ast.walk(run_nodes[0]) if isinstance(node, ast.Call)]
    names = [call_name(node) for node in calls]
    required_exactly_once = (
        "_create_run_started_ledger",
        "_load_checkpoint_from_authenticated_snapshot",
        "frozen_v031.build_contexts",
        "frozen_v031.run_entry_module",
        "frozen_v031.run_cone_module",
        "frozen_v031.run_relation_module",
        "frozen_v031.run_matched_module",
    )
    for name in required_exactly_once:
        _require(names.count(name) == 1, f"runner call-count mismatch: {name}")
    line_by_name = {
        name: next(node.lineno for node in calls if call_name(node) == name)
        for name in required_exactly_once
    }
    _require(
        line_by_name["_create_run_started_ledger"]
        < line_by_name["_load_checkpoint_from_authenticated_snapshot"],
        "checkpoint snapshot/load precedes v0.3.2 ledger",
    )
    _require(
        names.count("checkpoint_io.load_checkpoint") == 0,
        "run_registered bypasses authenticated checkpoint snapshots",
    )
    all_names = [call_name(node) for node in ast.walk(tree) if isinstance(node, ast.Call)]
    _require(
        all_names.count("checkpoint_io.load_checkpoint") == 1,
        "restricted loader must occur exactly once in the snapshot helper",
    )
    _require(not any(name.startswith("sys.path.") for name in all_names),
             "registered runner mutates the import search path")
    numpy_imports = [
        node.lineno
        for node in tree.body
        if isinstance(node, ast.Import)
        and [alias.name for alias in node.names] == ["numpy"]
    ]
    _require(len(numpy_imports) == 1, "NumPy import contract changed")
    bootstrap_calls = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and call_name(node) == "_bootstrap_validate_frozen_bytes"
    ]
    shadow_calls = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and call_name(node) == "_reject_local_import_shadowing"
    ]
    _require(
        len(bootstrap_calls) == 1
        and len(shadow_calls) == 1
        and isolated_line < shadow_calls[0] < bootstrap_calls[0] < numpy_imports[0],
        "bootstrap/import order changed",
    )
    exact_loader_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and call_name(node) == "_load_registered_local_module"
    ]
    _require(len(exact_loader_calls) == 9, "exact-path local module set changed")
    _require(
        min(node.lineno for node in exact_loader_calls) > numpy_imports[0],
        "local project module executes before bootstrap/NumPy boundary",
    )
    main_calls = [node for node in ast.walk(main_nodes[0]) if isinstance(node, ast.Call)]
    main_call_names = [call_name(node) for node in main_calls]
    for name in (
        "_acquire_execution_lock",
        "_refuse_existing_execution_artifacts",
        "run_registered",
        "_release_execution_lock",
    ):
        _require(main_call_names.count(name) == 1, f"main call-count mismatch: {name}")
    main_line_by_name = {
        name: next(node.lineno for node in main_calls if call_name(node) == name)
        for name in (
            "_acquire_execution_lock",
            "_refuse_existing_execution_artifacts",
            "run_registered",
            "_release_execution_lock",
        )
    }
    _require(
        main_line_by_name["_acquire_execution_lock"]
        < main_line_by_name["_refuse_existing_execution_artifacts"]
        < main_line_by_name["run_registered"]
        < main_line_by_name["_release_execution_lock"],
        "one-shot execution lock order changed",
    )
    finally_calls = [
        call_name(node)
        for candidate in ast.walk(main_nodes[0])
        if isinstance(candidate, ast.Try)
        for statement in candidate.finalbody
        for node in ast.walk(statement)
        if isinstance(node, ast.Call)
    ]
    _require(
        finally_calls.count("_release_execution_lock") == 1,
        "execution lock is not released in a finally block",
    )
    return {
        "passed": True,
        "delegated_module_count": 5,
        "exact_path_local_module_count": len(exact_loader_calls),
        "isolated_mode_guard_line": isolated_line,
        "freeze_isolated_mode_guard_line": freeze_isolated_line,
        "execution_lock_call_line": main_line_by_name["_acquire_execution_lock"],
        "execution_unlock_call_line": main_line_by_name["_release_execution_lock"],
        "ledger_call_line": line_by_name["_create_run_started_ledger"],
        "checkpoint_snapshot_call_line": line_by_name[
            "_load_checkpoint_from_authenticated_snapshot"
        ],
        "restricted_loader_call_count": 1,
    }


def _snapshot_registered_files(root: Path) -> dict[str, str]:
    registered = sorted(
        set(REQUIRED_ROOT_RELATIVE_FILES) | set(V031_REQUIRED_ROOT_RELATIVE_FILES)
    )
    return {
        relative: file_sha256(_safe_file(root, relative)) for relative in registered
    }


def run_unit_tests(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    copied_paths = sorted(
        (set(REQUIRED_ROOT_RELATIVE_FILES) | set(V031_REQUIRED_ROOT_RELATIVE_FILES))
        - {
            "checkpoints/projective_terminal_seed0.pt",
            "checkpoints/projective_terminal_seed1.pt",
        }
    )
    with tempfile.TemporaryDirectory(prefix="komorebi-v032-structural-") as temporary:
        sandbox_root = Path(temporary) / "package"
        for relative in copied_paths:
            source = _safe_file(root, relative)
            target = sandbox_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        _require(
            not any((sandbox_root / "checkpoints").glob("*.pt")),
            "checkpoint entered the structural-test sandbox",
        )
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["KOMOREBI_V032_PREENDPOINT_STRUCTURAL_ONLY"] = "1"
        environment["PYTHONPATH"] = os.pathsep.join(
            (str(sandbox_root), str(sandbox_root / "v031"))
        )
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-Werror",
                "-m",
                "unittest",
                "-v",
                "v032.test_v032_contract",
            ],
            cwd=sandbox_root,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
    if completed.returncode != 0:
        raise FreezeValidationError(
            "v0.3.2 unit tests failed:\n" + completed.stdout + completed.stderr
        )
    count = sum(1 for line in completed.stderr.splitlines() if line.startswith("test_"))
    _require(count == EXPECTED_UNIT_TEST_COUNT, "v0.3.2 test count changed")
    return {
        "passed": True,
        "status": "PASS",
        "test_count": count,
        "isolated_test_sandbox": True,
        "learned_checkpoint_files_present_in_test_sandbox": False,
        "learned_checkpoint_deserialization": "not_performed",
        "learned_endpoint_execution": "not_performed",
        "preendpoint_guard_environment": (
            "KOMOREBI_V032_PREENDPOINT_STRUCTURAL_ONLY=1"
        ),
    }


def prefreeze_validation(root: Path, *, run_tests: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    execution_artifacts_absent = validate_v032_execution_artifacts_absent(root)
    snapshot_before = _snapshot_registered_files(root)
    runtime = {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
    }
    _require(
        runtime
        == {
            "python_implementation": EXPECTED_PYTHON_IMPLEMENTATION,
            "python_version": EXPECTED_PYTHON_VERSION,
        },
        f"runtime mismatch: {runtime}",
    )
    validations = {
        "runtime": runtime,
        "no_executable_bytecode": validate_no_executable_bytecode(root),
        "v031_frozen_bytes": validate_v031_frozen_bytes(root),
        "v031_abort_evidence": validate_v031_abort_evidence(root),
        "lineage_provenance": validate_lineage_provenance(root),
        "requirements": validate_requirements(root),
        "preregistration": validate_preregistration(
            root / "v032" / "V032_PREREGISTRATION.json"
        ),
        "runner_contract": validate_runner_contract(root),
        "execution_artifacts_absent": execution_artifacts_absent,
    }
    if run_tests:
        validations["unit_tests"] = run_unit_tests(root)
    snapshot_after = _snapshot_registered_files(root)
    _require(snapshot_after == snapshot_before, "registered bytes changed during validation")
    validations["source_snapshot"] = {
        "passed": True,
        "file_count": len(snapshot_after),
        "files": snapshot_after,
    }
    validations["no_executable_bytecode_after_tests"] = validate_no_executable_bytecode(
        root
    )
    return {"passed": True, **validations}


def build_execution_freeze(root: Path, validation: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(root).resolve()
    _require(validation.get("passed") is True, "prefreeze validation did not pass")
    validated_snapshot = validation.get("source_snapshot", {}).get("files")
    _require(isinstance(validated_snapshot, dict), "validated source snapshot missing")
    current_snapshot = _snapshot_registered_files(root)
    _require(
        current_snapshot == validated_snapshot,
        "registered bytes changed after prefreeze validation",
    )
    files = {
        relative: current_snapshot[relative]
        for relative in REQUIRED_ROOT_RELATIVE_FILES
    }
    inherited = validation["v031_frozen_bytes"]
    abort = validation["v031_abort_evidence"]
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "status": STATUS,
        "date": date.today().isoformat(),
        "attestation": EXPECTED_ATTESTATION,
        "runtime_contract": EXPECTED_RUNTIME,
        "registered_outputs": EXPECTED_OUTPUTS,
        "inherited_scientific_profile": EXPECTED_PROFILE,
        "v031_execution_freeze_sha256": inherited["freeze_sha256"],
        "v031_invalid_attempt_sha256": abort["invalid_attempt_sha256"],
        "v031_abort_boundary": EXPECTED_V031_ABORT_BOUNDARY,
        "files": files,
        "preexecution_validation": dict(validation),
    }


def _atomic_create_json(path: Path, value: Mapping[str, Any]) -> None:
    path = Path(path)
    _require(not path.exists(), f"refusing to overwrite freeze: {path}")
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def validate_execution_freeze(
    path: Path, root: Path | None = None
) -> dict[str, Any]:
    path = Path(path).resolve()
    root = path.parent.parent.resolve() if root is None else Path(root).resolve()
    value = load_json(path)
    _require_exact_keys(
        value,
        {
            "schema",
            "version",
            "author",
            "status",
            "date",
            "attestation",
            "runtime_contract",
            "registered_outputs",
            "inherited_scientific_profile",
            "v031_execution_freeze_sha256",
            "v031_invalid_attempt_sha256",
            "v031_abort_boundary",
            "files",
            "preexecution_validation",
        },
        "correction freeze",
    )
    _require(value.get("schema") == SCHEMA, "correction freeze schema mismatch")
    _require(value.get("version") == VERSION, "correction freeze version mismatch")
    _require(value.get("author") == AUTHOR, "correction freeze author mismatch")
    _require(value.get("status") == STATUS, "correction freeze status mismatch")
    try:
        frozen_date = date.fromisoformat(value.get("date", ""))
    except (TypeError, ValueError) as error:
        raise FreezeValidationError("correction freeze date is invalid") from error
    _require(frozen_date <= date.today(), "correction freeze date is in the future")
    _require(value.get("attestation") == EXPECTED_ATTESTATION, "attestation changed")
    _require(value.get("runtime_contract") == EXPECTED_RUNTIME, "runtime changed")
    _require(value.get("registered_outputs") == EXPECTED_OUTPUTS, "outputs changed")
    _require(
        value.get("inherited_scientific_profile") == EXPECTED_PROFILE,
        "scientific profile changed",
    )
    _require(
        value.get("v031_abort_boundary") == EXPECTED_V031_ABORT_BOUNDARY,
        "v0.3.1 abort boundary changed",
    )
    preexecution = value.get("preexecution_validation")
    _require(isinstance(preexecution, dict), "preexecution validation is missing")
    _require(preexecution.get("passed") is True, "preexecution validation did not pass")
    unit_tests = preexecution.get("unit_tests", {})
    _require(
        unit_tests.get("test_count") == EXPECTED_UNIT_TEST_COUNT
        and unit_tests.get("isolated_test_sandbox") is True
        and unit_tests.get("learned_checkpoint_files_present_in_test_sandbox")
        is False
        and unit_tests.get("learned_checkpoint_deserialization") == "not_performed"
        and unit_tests.get("learned_endpoint_execution") == "not_performed",
        "structural-test attestation changed",
    )
    _require(
        preexecution.get("source_snapshot", {}).get("files")
        == _snapshot_registered_files(root),
        "validated source snapshot changed",
    )
    files = value.get("files")
    _require(isinstance(files, dict), "correction digest map missing")
    _require_exact_keys(files, REQUIRED_ROOT_RELATIVE_FILES, "correction digest map")
    for relative, expected in files.items():
        _require(
            file_sha256(_safe_file(root, relative)) == expected,
            f"correction frozen byte changed: {relative}",
        )
    nested = validate_v031_frozen_bytes(root)
    abort = validate_v031_abort_evidence(root)
    _require(
        value.get("v031_execution_freeze_sha256") == nested["freeze_sha256"],
        "nested freeze digest mismatch",
    )
    _require(
        nested["freeze_sha256"] == EXPECTED_V031_EXECUTION_FREEZE_SHA256,
        "historical v0.3.1 freeze pin changed",
    )
    _require(
        value.get("v031_invalid_attempt_sha256") == abort["invalid_attempt_sha256"],
        "abort evidence digest mismatch",
    )
    return {
        "passed": True,
        "freeze_sha256": file_sha256(path),
        "frozen_file_count": len(files),
        "v031_execution_freeze_sha256": nested["freeze_sha256"],
        "v031_frozen_file_count": nested["frozen_file_count"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    arguments = parser.parse_args(argv)
    root = arguments.package_root.resolve()
    target = root / "v032" / TARGET_NAME
    _require(not target.exists(), f"refusing to overwrite freeze: {target}")
    validation = prefreeze_validation(root, run_tests=True)
    freeze = build_execution_freeze(root, validation)
    _atomic_create_json(target, freeze)
    result = validate_execution_freeze(target, root)
    print(f"V032_EXECUTION_FREEZE={target}")
    print(f"V032_EXECUTION_FREEZE_SHA256={result['freeze_sha256']}")
    print(f"V032_FROZEN_FILE_COUNT={result['frozen_file_count']}")
    print(f"V031_NESTED_FROZEN_FILE_COUNT={result['v031_frozen_file_count']}")
    print(f"V032_TEST_COUNT={validation['unit_tests']['test_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
