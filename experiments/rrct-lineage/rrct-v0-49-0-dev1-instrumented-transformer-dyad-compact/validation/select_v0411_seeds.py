"""Select the RRCT v0.41.1 fresh-pilot seeds exactly once.

The selector draws twelve unique nine-digit candidates before scanning any
project outcome, scans the explicit project/evidence surface for standalone
decimal occurrences, and selects the first four candidates with zero
occurrences.  It never redraws after seeing scan results.  The scan manifest,
unopened registry, and selection receipt are published exclusively as one
fail-closed transaction; the receipt is the final commit marker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
from collections.abc import Mapping
from pathlib import Path
from typing import Any

VERSION = "0.41.1.dev2"
SCAN_SCHEMA = "rrct.v0411.seed_selection_scan_manifest.v1"
RECEIPT_SCHEMA = "rrct.v0411.seed_selection_receipt.v1"
REGISTRY_SCHEMA = "rrct.v0411.seed_registry.v1"

SCAN_NAME = "V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json"
RECEIPT_NAME = "V0_41_1_SEED_SELECTION_RECEIPT.json"
REGISTRY_NAME = "V0_41_1_SEED_REGISTRY.json"
SELECTOR_RELATIVE_PATH = "validation/select_v0411_seeds.py"
TRANSACTION_DIRECTORY_NAME = ".V0_41_1_SEED_SELECTION_TRANSACTION"
CAMPAIGN_DIRECTORY_NAME = "v0.41.1_frozen_exploratory_pilot_campaign"

CANDIDATE_COUNT = 12
SELECTED_COUNT = 4
CANDIDATE_FLOOR = 100_000_000
CANDIDATE_SPAN = 800_000_000
DRAW_EXPRESSION = "secrets.randbelow(800_000_000) + 100_000_000"
SCAN_RULE = "standalone_decimal_occurrences_not_adjacent_to_ascii_digits"

CONDITIONS: dict[str, dict[str, Any]] = {
    "K_RPLUS": {
        "history_policy": "keyed",
        "historical_prior_enabled": True,
        "world_variant": "true_recurrence",
    },
    "N_RPLUS": {
        "history_policy": "withheld",
        "historical_prior_enabled": False,
        "world_variant": "true_recurrence",
    },
    "G_RPLUS": {
        "history_policy": "generic",
        "historical_prior_enabled": True,
        "world_variant": "true_recurrence",
    },
    "K_RMINUS": {
        "history_policy": "keyed",
        "historical_prior_enabled": True,
        "world_variant": "same_key_null_lure",
    },
    "N_RMINUS": {
        "history_policy": "withheld",
        "historical_prior_enabled": False,
        "world_variant": "same_key_null_lure",
    },
    "G_RMINUS": {
        "history_policy": "generic",
        "historical_prior_enabled": True,
        "world_variant": "same_key_null_lure",
    },
}

CACHE_DIRECTORY_NAMES = frozenset(
    {
        ".cache",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
    }
)
SELECTOR_OUTPUT_NAMES = frozenset({SCAN_NAME, RECEIPT_NAME, REGISTRY_NAME})


class SeedSelectionError(RuntimeError):
    """One fail-closed prospective seed-selection violation."""


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(
        os.fspath(directory), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_exclusive_bytes(path: Path, value: bytes) -> None:
    descriptor = os.open(os.fspath(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        remaining = memoryview(value)
        while remaining:
            written = os.write(descriptor, remaining)
            if written <= 0:
                raise OSError(f"seed-selection write made no progress: {path}")
            remaining = remaining[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _validation_directory(project_root: Path) -> Path:
    root = project_root.resolve(strict=True)
    validation = root / "validation"
    if not validation.is_dir():
        raise FileNotFoundError(f"validation directory is missing: {validation}")
    return validation


def _assert_preselection_state(project_root: Path) -> None:
    validation = _validation_directory(project_root)
    conflicts = [
        validation / SCAN_NAME,
        validation / RECEIPT_NAME,
        validation / REGISTRY_NAME,
        validation / TRANSACTION_DIRECTORY_NAME,
        validation / "V0_41_1_PREOUTCOME_FREEZE.json",
        validation / "V0_41_1_PREOUTCOME_FREEZE.json.sha256",
        validation / CAMPAIGN_DIRECTORY_NAME,
    ]
    conflicts.extend(validation.glob("V0_41_1_EXECUTED_SOURCE_*.tar.gz"))
    conflicts.extend(validation.glob(".V0_41_1_EXECUTED_SOURCE_*.tar.gz"))
    present = sorted({path for path in conflicts if path.exists()})
    if present:
        names = ", ".join(path.relative_to(project_root).as_posix() for path in present)
        raise FileExistsError(
            f"seed selection is already consumed or too late: {names}"
        )


def _draw_candidates() -> tuple[list[int], int]:
    candidates: list[int] = []
    observed: set[int] = set()
    call_count = 0
    while len(candidates) < CANDIDATE_COUNT:
        raw = secrets.randbelow(CANDIDATE_SPAN)
        call_count += 1
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise SeedSelectionError("secrets.randbelow returned a non-integer")
        candidate = raw + CANDIDATE_FLOOR
        if not CANDIDATE_FLOOR <= candidate < CANDIDATE_FLOOR + CANDIDATE_SPAN:
            raise SeedSelectionError(
                "generated candidate lies outside the frozen range"
            )
        if candidate in observed:
            continue
        observed.add(candidate)
        candidates.append(candidate)
    return candidates, call_count


def _exclusion_reason(relative: Path) -> str | None:
    if any(part in CACHE_DIRECTORY_NAMES for part in relative.parts):
        return "venv_or_cache_directory"
    if relative.parts[:2] == ("validation", CAMPAIGN_DIRECTORY_NAME):
        return "future_campaign_output"
    if len(relative.parts) == 2 and relative.parts[0] == "validation":
        name = relative.name
        if name in SELECTOR_OUTPUT_NAMES or name == TRANSACTION_DIRECTORY_NAME:
            return "future_seed_selection_output"
        if name in {
            "V0_41_1_PREOUTCOME_FREEZE.json",
            "V0_41_1_PREOUTCOME_FREEZE.json.sha256",
        }:
            return "future_freeze_output"
        if re.fullmatch(r"\.?V0_41_1_EXECUTED_SOURCE_.*\.tar\.gz", name):
            return "future_freeze_output"
    return None


def _surface_files(project_root: Path) -> tuple[list[Path], list[dict[str, str]]]:
    root = project_root.resolve(strict=True)
    files: list[Path] = []
    excluded: list[dict[str, str]] = []

    def fail_walk(error: OSError) -> None:
        raise SeedSelectionError(f"project-surface traversal failed: {error}")

    for directory, directory_names, file_names in os.walk(
        root, followlinks=False, onerror=fail_walk
    ):
        directory_path = Path(directory)
        kept_directories: list[str] = []
        for name in sorted(directory_names):
            path = directory_path / name
            relative = path.relative_to(root)
            reason = _exclusion_reason(relative)
            if reason is not None:
                excluded.append(
                    {"relative_path": relative.as_posix(), "reason": reason}
                )
                continue
            if path.is_symlink():
                raise SeedSelectionError(
                    f"unscannable symlink in project surface: {relative.as_posix()}"
                )
            kept_directories.append(name)
        directory_names[:] = kept_directories
        for name in sorted(file_names):
            path = directory_path / name
            relative = path.relative_to(root)
            reason = _exclusion_reason(relative)
            if reason is not None:
                excluded.append(
                    {"relative_path": relative.as_posix(), "reason": reason}
                )
                continue
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                raise SeedSelectionError(
                    f"unscannable symlink in project surface: {relative.as_posix()}"
                )
            if not stat.S_ISREG(metadata.st_mode):
                raise SeedSelectionError(
                    f"non-regular project-surface entry: {relative.as_posix()}"
                )
            files.append(path)
    files.sort(key=lambda path: path.relative_to(root).as_posix())
    excluded.sort(key=lambda item: (item["relative_path"], item["reason"]))
    return files, excluded


def _scan_surface(
    project_root: Path, candidates: list[int]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    root = project_root.resolve(strict=True)
    files, excluded = _surface_files(root)
    patterns = {
        candidate: re.compile(
            rb"(?<![0-9])" + str(candidate).encode("ascii") + rb"(?![0-9])"
        )
        for candidate in candidates
    }
    occurrences: dict[int, list[str]] = {candidate: [] for candidate in candidates}
    file_records: list[dict[str, Any]] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        file_records.append(
            {
                "relative_path": relative,
                "size_bytes": len(data),
                "sha256": _sha256_bytes(data),
            }
        )
        for candidate, pattern in patterns.items():
            count = len(pattern.findall(data))
            occurrences[candidate].extend([relative] * count)

    candidate_records = [
        {
            "generation_index": index,
            "candidate": candidate,
            "standalone_decimal_occurrence_count": len(occurrences[candidate]),
            "occurrence_paths": occurrences[candidate],
            "zero_occurrence": not occurrences[candidate],
        }
        for index, candidate in enumerate(candidates)
    ]
    return file_records, candidate_records, excluded


def _publish_transaction(validation: Path, values: Mapping[str, bytes]) -> None:
    transaction = validation / TRANSACTION_DIRECTORY_NAME
    transaction.mkdir(mode=0o700, exist_ok=False)
    _fsync_directory(validation)
    published: list[Path] = []
    try:
        for name, value in values.items():
            _write_exclusive_bytes(transaction / name, value)
        _fsync_directory(transaction)
        # Receipt is deliberately last: it is the transaction commit marker.
        for name in (SCAN_NAME, REGISTRY_NAME, RECEIPT_NAME):
            source = transaction / name
            destination = validation / name
            os.link(source, destination)
            published.append(destination)
            _fsync_directory(validation)
    except BaseException:
        for path in reversed(published):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        _fsync_directory(validation)
        raise
    finally:
        for name in values:
            try:
                (transaction / name).unlink()
            except FileNotFoundError:
                pass
        try:
            transaction.rmdir()
        except FileNotFoundError:
            pass
        _fsync_directory(validation)


def select_seeds(project_root: Path) -> dict[str, Any]:
    """Generate, scan, select, and exclusively publish one unopened registry."""

    root = project_root.resolve(strict=True)
    _assert_preselection_state(root)
    candidates, randbelow_call_count = _draw_candidates()
    file_records, candidate_records, excluded_entries = _scan_surface(root, candidates)
    selected = [
        record["candidate"] for record in candidate_records if record["zero_occurrence"]
    ][:SELECTED_COUNT]
    if len(selected) != SELECTED_COUNT:
        raise SeedSelectionError(
            "fewer than four of the twelve generated candidates have zero "
            "standalone-decimal occurrences; no redraw and no publication"
        )

    selector_record = next(
        (
            record
            for record in file_records
            if record["relative_path"] == SELECTOR_RELATIVE_PATH
        ),
        None,
    )
    if selector_record is None:
        raise SeedSelectionError(
            f"selector is absent from scan: {SELECTOR_RELATIVE_PATH}"
        )

    scan_surface_sha256 = _canonical_sha256(file_records)
    scan_manifest = {
        "schema": SCAN_SCHEMA,
        "version": VERSION,
        "scientific_status": "pre_registry_complete_project_evidence_scan",
        "scan_rule": SCAN_RULE,
        "project_surface_policy": {
            "root": ".",
            "follow_symlinks": False,
            "regular_files_only": True,
            "excluded_directory_names": sorted(CACHE_DIRECTORY_NAMES),
            "excluded_future_output_names": sorted(SELECTOR_OUTPUT_NAMES),
            "excluded_campaign_directory": f"validation/{CAMPAIGN_DIRECTORY_NAME}",
            "excluded_freeze_output_patterns": [
                "validation/V0_41_1_PREOUTCOME_FREEZE.json*",
                "validation/V0_41_1_EXECUTED_SOURCE_*.tar.gz",
                "validation/.V0_41_1_EXECUTED_SOURCE_*.tar.gz",
            ],
        },
        "file_count": len(file_records),
        "files": file_records,
        "scan_surface_sha256": scan_surface_sha256,
        "excluded_entries": excluded_entries,
    }
    scan_bytes = _canonical_bytes(scan_manifest)
    scan_sha256 = _sha256_bytes(scan_bytes)

    registry = {
        "schema": REGISTRY_SCHEMA,
        "version": VERSION,
        "scientific_status": "fresh_pilot_seed_registry_selected_unopened",
        "registry_state": "unopened",
        "cohort_opened": False,
        "fresh_pilot_seeds": selected,
        "conditions": CONDITIONS,
        "opened_seed_condition_pairs": [],
        "seed_selection_receipt_relative_path": f"validation/{RECEIPT_NAME}",
        "seed_selection_scan_manifest_relative_path": f"validation/{SCAN_NAME}",
        "seed_selection_scan_manifest_sha256": scan_sha256,
    }
    registry_bytes = _canonical_bytes(registry)
    registry_sha256 = _sha256_bytes(registry_bytes)

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "version": VERSION,
        "scientific_status": "preoutcome_seed_selection_complete_unopened",
        "selection_method": "single_nonrepeated_secrets_randbelow_draw_loop",
        "draw_expression": DRAW_EXPRESSION,
        "candidate_count": CANDIDATE_COUNT,
        "candidate_generation_order": candidates,
        "randbelow_call_count": randbelow_call_count,
        "duplicate_draw_count": randbelow_call_count - CANDIDATE_COUNT,
        "scan_rule": SCAN_RULE,
        "candidate_scan_records": candidate_records,
        "selection_rule": "first_four_candidates_in_generation_order_with_zero_occurrences",
        "selected_fresh_pilot_seeds": selected,
        "selection_state": "unopened",
        "registry_state_at_selection": "unopened",
        "cohort_opened": False,
        "opened_seed_condition_pairs": [],
        "rows_or_outcomes_opened": 0,
        "no_redraw_after_scan": True,
        "wall_clock_time_in_record": False,
        "scan_manifest": {
            "relative_path": f"validation/{SCAN_NAME}",
            "schema": SCAN_SCHEMA,
            "sha256": scan_sha256,
            "file_count": len(file_records),
            "scan_surface_sha256": scan_surface_sha256,
        },
        "selector": {
            "relative_path": SELECTOR_RELATIVE_PATH,
            "sha256": selector_record["sha256"],
        },
        "seed_registry": {
            "relative_path": f"validation/{REGISTRY_NAME}",
            "schema": REGISTRY_SCHEMA,
            "sha256": registry_sha256,
            "registry_state": "unopened",
        },
    }
    receipt_bytes = _canonical_bytes(receipt)

    # Catch ordinary concurrent edits between the initial scan and publication.
    # The three outputs themselves still do not exist and therefore cannot
    # contaminate this repeat scan.
    repeat_files, repeat_candidates, repeat_excluded = _scan_surface(root, candidates)
    if (
        repeat_files != file_records
        or repeat_candidates != candidate_records
        or repeat_excluded != excluded_entries
    ):
        raise SeedSelectionError(
            "project/evidence surface changed during selection; no publication"
        )

    validation = root / "validation"
    _publish_transaction(
        validation,
        {
            SCAN_NAME: scan_bytes,
            REGISTRY_NAME: registry_bytes,
            RECEIPT_NAME: receipt_bytes,
        },
    )
    return {
        "scan_manifest": str(validation / SCAN_NAME),
        "scan_manifest_sha256": scan_sha256,
        "selection_receipt": str(validation / RECEIPT_NAME),
        "selection_receipt_sha256": _sha256_bytes(receipt_bytes),
        "seed_registry": str(validation / REGISTRY_NAME),
        "seed_registry_sha256": registry_sha256,
        "selected_seed_count": SELECTED_COUNT,
        "candidate_count": CANDIDATE_COUNT,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Select and seal the RRCT v0.41.1 fresh-pilot seed registry."
    )
    parser.add_argument("--project-root", required=True, type=Path)
    arguments = parser.parse_args()
    print(
        json.dumps(
            select_seeds(arguments.project_root),
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
