"""Standard-library integrity and exogenous-yoking audit for v0.41 development.

The auditor deliberately imports no RRCT modules.  All schemas, schedules,
condition mappings, and yoking fields are specified independently below.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Mapping


VERSION = "0.41.1.dev2"
ROW_SCHEMA = "rrct.v041.temporal_self_identity.row.v3"
SUMMARY_SCHEMA = "rrct.v041.temporal_self_identity.summary.v3"
START_SCHEMA = "rrct.v041.development_condition.start.v1"
FINISH_SCHEMA = "rrct.v041.development_condition.finish.v1"
AUDIT_SCHEMA = "rrct.v041.development_integrity_yoking_audit.v1"

START_NAME = "start_receipt.json"
ROWS_NAME = "sealed_rows.jsonl"
SUMMARY_NAME = "summary.json"
FINISH_NAME = "finish_receipt.json"
MANIFEST_NAME = "artifact_sha256.json"
MANIFEST_MEMBERS = (START_NAME, ROWS_NAME, SUMMARY_NAME, FINISH_NAME)

EXPECTED_SEED = 41_011
EXPECTED_ROW_COUNT = 10_560
RMINUS_START = 9_120
RMINUS_STOP = 10_560
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

PHASE_STEPS: tuple[tuple[str, int], ...] = (
    ("identity_a_initial", 1_440),
    ("world_shock_a", 480),
    ("identity_b_first", 1_440),
    ("disconnect_one", 1_440),
    ("identity_a_return_one", 1_440),
    ("identity_b_return", 1_440),
    ("disconnect_two", 1_440),
    ("identity_a_return_two", 1_440),
)
PHASE_COUNTS = dict(PHASE_STEPS)

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

YOKE_FIELDS = (
    "transition_index",
    "phase",
    "phase_offset",
    "process_bank_sha256",
    "process_bank_generation_receipt",
    "task_context",
    "observation_noise_sha256",
    "return_noise",
    "hidden_pair_evaluator_only",
    "hidden_rank_evaluator_only",
    "hidden_exogenous_source_evaluator_only",
    "access_fault_active_evaluator_only",
)

MANDATORY_ROW_INTEGRITY = (
    "hard_integrity_valid",
    "v039_wrapper_integrity",
    "v040_wrapper_integrity",
    "v041_wrapper_integrity",
    "temporal_action_gate_binding_valid",
    "runtime_identity_ok",
)


class AuditFailure(RuntimeError):
    """A fail-closed development audit violation."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AuditFailure(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_nonfinite(token: str) -> None:
    raise AuditFailure(f"nonfinite JSON token: {token}")


def _loads_json(payload: bytes, *, source: str) -> Any:
    try:
        return json.loads(
            payload,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except AuditFailure:
        raise
    except Exception as error:
        raise AuditFailure(f"invalid JSON in {source}: {error}") from error


def _load_json(path: Path) -> Any:
    if not path.is_file():
        raise AuditFailure(f"required artifact is missing: {path}")
    return _loads_json(path.read_bytes(), source=path.as_posix())


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _exclusive_json(path: Path, payload: Mapping[str, Any]) -> str:
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    descriptor = os.open(
        os.fspath(path),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )
    try:
        view = memoryview(encoded)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("audit write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    parent_descriptor = os.open(
        os.fspath(path.parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
    )
    try:
        os.fsync(parent_descriptor)
    finally:
        os.close(parent_descriptor)
    return hashlib.sha256(encoded).hexdigest()


def _expected_phase(index: int) -> tuple[str, int]:
    start = 0
    for phase, count in PHASE_STEPS:
        stop = start + count
        if start <= index < stop:
            return phase, index - start
        start = stop
    raise AuditFailure(f"row index outside schedule: {index}")


def _expected_multiplier(condition_id: str, phase: str, index: int) -> float:
    if phase in {"identity_b_first", "identity_b_return"}:
        return 0.65
    if condition_id.endswith("RMINUS") and RMINUS_START <= index < RMINUS_STOP:
        return 0.0
    return 1.40


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        raise AuditFailure(f"{label} is not a lowercase SHA-256 digest")
    return value


def _validate_static_artifacts(
    matrix_root: Path,
    condition_id: str,
    seed: int,
) -> dict[str, Any]:
    expected = CONDITIONS[condition_id]
    directory = matrix_root / condition_id
    if not directory.is_dir():
        raise AuditFailure(f"condition directory is missing: {condition_id}")

    manifest = _load_json(directory / MANIFEST_NAME)
    if not isinstance(manifest, dict) or set(manifest) != set(MANIFEST_MEMBERS):
        raise AuditFailure(f"{condition_id} artifact manifest has the wrong members")
    for name, digest in manifest.items():
        _require_sha256(digest, f"{condition_id}/{name} manifest digest")

    artifact_hashes: dict[str, str] = {}
    for name in (START_NAME, SUMMARY_NAME, FINISH_NAME):
        actual = _sha256_file(directory / name)
        if actual != manifest[name]:
            raise AuditFailure(f"{condition_id}/{name} hash mismatch")
        artifact_hashes[name] = actual

    start = _load_json(directory / START_NAME)
    finish = _load_json(directory / FINISH_NAME)
    summary = _load_json(directory / SUMMARY_NAME)
    if not all(isinstance(item, dict) for item in (start, finish, summary)):
        raise AuditFailure(f"{condition_id} receipt or summary is not an object")

    if start.get("schema") != START_SCHEMA or start.get("version") != VERSION:
        raise AuditFailure(f"{condition_id} start receipt schema/version mismatch")
    if finish.get("schema") != FINISH_SCHEMA or finish.get("version") != VERSION:
        raise AuditFailure(f"{condition_id} finish receipt schema/version mismatch")
    if summary.get("schema") != SUMMARY_SCHEMA or summary.get("version") != VERSION:
        raise AuditFailure(f"{condition_id} summary schema/version mismatch")
    if any(int(item.get("seed", -1)) != seed for item in (start, finish, summary)):
        raise AuditFailure(f"{condition_id} seed mismatch")
    if start.get("condition_id") != condition_id:
        raise AuditFailure(f"{condition_id} start condition mismatch")
    if finish.get("condition_id") != condition_id:
        raise AuditFailure(f"{condition_id} finish condition mismatch")

    for item_name, item in (("start", start), ("finish", finish)):
        if item.get("history_policy") != expected["history_policy"]:
            raise AuditFailure(f"{condition_id} {item_name} history-policy mismatch")
        if item.get("world_variant") != expected["world_variant"]:
            raise AuditFailure(f"{condition_id} {item_name} world-variant mismatch")
    if bool(start.get("historical_prior_enabled")) != bool(
        expected["historical_prior_enabled"]
    ):
        raise AuditFailure(f"{condition_id} prior-enabled switch mismatch")
    if int(start.get("expected_transition_count", -1)) != EXPECTED_ROW_COUNT:
        raise AuditFailure(f"{condition_id} expected row count mismatch")
    if start.get("expected_phase_counts") != PHASE_COUNTS:
        raise AuditFailure(f"{condition_id} expected phase counts mismatch")
    _require_sha256(
        start.get("condition_config_sha256"),
        f"{condition_id} condition-config commitment",
    )
    if finish.get("start_receipt_sha256") != manifest[START_NAME]:
        raise AuditFailure(f"{condition_id} finish/start binding mismatch")
    if finish.get("summary_sha256") != manifest[SUMMARY_NAME]:
        raise AuditFailure(f"{condition_id} finish/summary binding mismatch")
    if int(finish.get("rows_count", -1)) != EXPECTED_ROW_COUNT:
        raise AuditFailure(f"{condition_id} finish row count mismatch")
    if finish.get("rows_sha256") != manifest[ROWS_NAME]:
        raise AuditFailure(f"{condition_id} finish/rows binding mismatch")
    if finish.get("integrity_complete") is not True:
        raise AuditFailure(f"{condition_id} finish is not integrity-complete")
    if finish.get("status") != "V041_DEVELOPMENT_CONDITION_INTEGRITY_COMPLETE":
        raise AuditFailure(f"{condition_id} finish status mismatch")

    summary_condition = summary.get("condition")
    if not isinstance(summary_condition, dict):
        raise AuditFailure(f"{condition_id} summary condition is missing")
    if summary_condition.get("history_policy") != expected["history_policy"]:
        raise AuditFailure(f"{condition_id} summary history-policy mismatch")
    if summary_condition.get("world_variant") != expected["world_variant"]:
        raise AuditFailure(f"{condition_id} summary world-variant mismatch")
    if not isinstance(summary.get("integrity"), dict) or not all(
        bool(value) for value in summary["integrity"].values()
    ):
        raise AuditFailure(f"{condition_id} summary integrity failed")
    engine_integrity = summary.get("engine_summary", {}).get("integrity")
    if not isinstance(engine_integrity, dict) or not all(
        bool(value) for value in engine_integrity.values()
    ):
        raise AuditFailure(f"{condition_id} engine integrity failed")

    source_hashes = start.get("source_sha256")
    if not isinstance(source_hashes, dict) or not source_hashes:
        raise AuditFailure(f"{condition_id} source hash map is missing")
    for relative, digest in source_hashes.items():
        if not isinstance(relative, str):
            raise AuditFailure(f"{condition_id} source path is not a string")
        _require_sha256(digest, f"{condition_id} source digest for {relative}")

    return {
        "directory": directory,
        "manifest": manifest,
        "artifact_manifest_sha256": _sha256_file(directory / MANIFEST_NAME),
        "artifact_hashes": artifact_hashes,
        "start": start,
        "finish": finish,
        "summary": summary,
        "source_sha256": source_hashes,
    }


def _row_yoke_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    missing = [field for field in YOKE_FIELDS if field not in row]
    if missing:
        raise AuditFailure(f"row is missing yoking fields: {missing}")
    return {field: row[field] for field in YOKE_FIELDS}


def _audit_rows(
    static: Mapping[str, Mapping[str, Any]],
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    handles: dict[str, BinaryIO] = {}
    row_file_digests = {name: hashlib.sha256() for name in CONDITIONS}
    yoke_digests = {name: hashlib.sha256() for name in CONDITIONS}
    multiplier_digests = {name: hashlib.sha256() for name in CONDITIONS}
    phase_counts = {
        name: {phase: 0 for phase, _count in PHASE_STEPS}
        for name in CONDITIONS
    }
    multiplier_pair_differences = {policy: 0 for policy in ("K", "N", "G")}
    try:
        for condition_id in CONDITIONS:
            directory = static[condition_id]["directory"]
            handles[condition_id] = (directory / ROWS_NAME).open("rb")

        for index in range(EXPECTED_ROW_COUNT):
            expected_phase, expected_offset = _expected_phase(index)
            parsed_rows: dict[str, dict[str, Any]] = {}
            raw_lines: dict[str, bytes] = {}
            for condition_id, expected in CONDITIONS.items():
                raw = handles[condition_id].readline()
                if not raw:
                    raise AuditFailure(
                        f"{condition_id} rows ended before index {index}"
                    )
                if not raw.endswith(b"\n"):
                    raise AuditFailure(f"{condition_id} row {index} has no LF")
                row_file_digests[condition_id].update(raw)
                row = _loads_json(
                    raw,
                    source=f"{condition_id}/{ROWS_NAME}:{index + 1}",
                )
                if not isinstance(row, dict):
                    raise AuditFailure(f"{condition_id} row {index} is not an object")
                canonical = _canonical_bytes(row) + b"\n"
                if canonical != raw:
                    raise AuditFailure(f"{condition_id} row {index} is not canonical")
                if row.get("schema") != ROW_SCHEMA:
                    raise AuditFailure(f"{condition_id} row {index} schema mismatch")
                if int(row.get("seed", -1)) != seed:
                    raise AuditFailure(f"{condition_id} row {index} seed mismatch")
                if int(row.get("transition_index", -1)) != index:
                    raise AuditFailure(
                        f"{condition_id} row {index} transition sequence mismatch"
                    )
                if row.get("phase") != expected_phase:
                    raise AuditFailure(f"{condition_id} row {index} phase mismatch")
                if int(row.get("phase_offset", -1)) != expected_offset:
                    raise AuditFailure(
                        f"{condition_id} row {index} phase-offset mismatch"
                    )
                if row.get("history_policy") != expected["history_policy"]:
                    raise AuditFailure(
                        f"{condition_id} row {index} history-policy mismatch"
                    )
                if (
                    row.get("world_variant_evaluator_only")
                    != expected["world_variant"]
                ):
                    raise AuditFailure(
                        f"{condition_id} row {index} world-variant mismatch"
                    )
                multiplier = float(
                    row.get("task_return_multiplier_evaluator_only", float("nan"))
                )
                expected_multiplier = _expected_multiplier(
                    condition_id,
                    expected_phase,
                    index,
                )
                if multiplier != expected_multiplier:
                    raise AuditFailure(
                        f"{condition_id} row {index} multiplier mismatch: "
                        f"{multiplier} != {expected_multiplier}"
                    )
                if not all(
                    bool(row.get(field)) for field in MANDATORY_ROW_INTEGRITY
                ):
                    raise AuditFailure(
                        f"{condition_id} row {index} failed mandatory integrity"
                    )
                if int(row.get("reset_count", -1)) != 0:
                    raise AuditFailure(f"{condition_id} row {index} records reset")
                if bool(row.get("evaluator_truth_leak")):
                    raise AuditFailure(
                        f"{condition_id} row {index} records evaluator leakage"
                    )

                yoke_payload = _row_yoke_payload(row)
                yoke_digests[condition_id].update(_canonical_bytes(yoke_payload) + b"\n")
                multiplier_digests[condition_id].update(
                    _canonical_bytes(multiplier) + b"\n"
                )
                phase_counts[condition_id][expected_phase] += 1
                parsed_rows[condition_id] = row
                raw_lines[condition_id] = raw

            reference_yoke = _row_yoke_payload(parsed_rows["K_RPLUS"])
            for condition_id in CONDITIONS:
                if _row_yoke_payload(parsed_rows[condition_id]) != reference_yoke:
                    differing = [
                        field
                        for field in YOKE_FIELDS
                        if parsed_rows[condition_id][field]
                        != parsed_rows["K_RPLUS"][field]
                    ]
                    raise AuditFailure(
                        f"cross-arm exogenous yoke mismatch at row {index}, "
                        f"condition {condition_id}, fields {differing}"
                    )

            for policy in ("K", "N", "G"):
                plus = float(
                    parsed_rows[f"{policy}_RPLUS"][
                        "task_return_multiplier_evaluator_only"
                    ]
                )
                minus = float(
                    parsed_rows[f"{policy}_RMINUS"][
                        "task_return_multiplier_evaluator_only"
                    ]
                )
                if index < RMINUS_START:
                    if plus != minus:
                        raise AuditFailure(
                            f"{policy} R+/R- multiplier differs before row 9120"
                        )
                else:
                    if plus != 1.40 or minus != 0.0:
                        raise AuditFailure(
                            f"{policy} R+/R- final multiplier contrast is wrong"
                        )
                    multiplier_pair_differences[policy] += 1

        for condition_id, handle in handles.items():
            if handle.readline() != b"":
                raise AuditFailure(f"{condition_id} contains more than 10,560 rows")
    finally:
        for handle in handles.values():
            handle.close()

    condition_audits: dict[str, Any] = {}
    for condition_id in CONDITIONS:
        rows_sha = row_file_digests[condition_id].hexdigest()
        expected_rows_sha = static[condition_id]["manifest"][ROWS_NAME]
        if rows_sha != expected_rows_sha:
            raise AuditFailure(f"{condition_id} rows hash mismatch")
        if phase_counts[condition_id] != PHASE_COUNTS:
            raise AuditFailure(f"{condition_id} phase counts mismatch")
        condition_audits[condition_id] = {
            "seed": seed,
            "row_count": EXPECTED_ROW_COUNT,
            "phase_counts": phase_counts[condition_id],
            "rows_sha256": rows_sha,
            "start_receipt_sha256": static[condition_id]["manifest"][START_NAME],
            "summary_sha256": static[condition_id]["manifest"][SUMMARY_NAME],
            "finish_receipt_sha256": static[condition_id]["manifest"][FINISH_NAME],
            "artifact_manifest_sha256": static[condition_id][
                "artifact_manifest_sha256"
            ],
            "exogenous_yoke_sha256": yoke_digests[condition_id].hexdigest(),
            "multiplier_sequence_sha256": multiplier_digests[
                condition_id
            ].hexdigest(),
            "integrity_complete": True,
            "scientific_all_endpoints_met": bool(
                static[condition_id]["finish"].get(
                    "scientific_all_endpoints_met"
                )
            ),
        }

    yoke_values = {
        audit["exogenous_yoke_sha256"] for audit in condition_audits.values()
    }
    yoking = {
        "fields": list(YOKE_FIELDS),
        "all_six_exogenous_yoke_digests_equal": len(yoke_values) == 1,
        "exogenous_yoke_sha256": next(iter(yoke_values)),
        "rows_compared_per_condition": EXPECTED_ROW_COUNT,
    }
    multiplier_yoking = {
        "rplus_rminus_identical_through_index": RMINUS_START - 1,
        "final_contrast_start_index": RMINUS_START,
        "final_contrast_stop_index_exclusive": RMINUS_STOP,
        "rplus_final_multiplier": 1.40,
        "rminus_final_multiplier": 0.0,
        "different_rows_by_policy": multiplier_pair_differences,
        "exact_final_difference_only": all(
            count == RMINUS_STOP - RMINUS_START
            for count in multiplier_pair_differences.values()
        ),
    }
    return condition_audits, yoking, multiplier_yoking


def audit_matrix(matrix_root: Path, *, seed: int) -> dict[str, Any]:
    matrix_root = matrix_root.resolve(strict=True)
    if not matrix_root.is_dir():
        raise AuditFailure("matrix root is not a directory")
    static = {
        condition_id: _validate_static_artifacts(matrix_root, condition_id, seed)
        for condition_id in CONDITIONS
    }

    source_maps = [static[name]["source_sha256"] for name in CONDITIONS]
    if any(source_map != source_maps[0] for source_map in source_maps[1:]):
        raise AuditFailure("condition start receipts do not share one source map")
    common_source = dict(source_maps[0])
    project_root = Path(__file__).resolve().parents[1]
    current_source_checks: dict[str, bool] = {}
    for relative, expected_sha in common_source.items():
        path = project_root / relative
        current_source_checks[relative] = bool(
            path.is_file() and _sha256_file(path) == expected_sha
        )
    if not all(current_source_checks.values()):
        raise AuditFailure("current development source differs from executed source")

    condition_audits, yoking, multiplier_yoking = _audit_rows(static, seed)
    criteria = {
        "six_conditions_complete": set(condition_audits) == set(CONDITIONS),
        "all_artifact_hashes_valid": True,
        "all_conditions_10560_rows": all(
            audit["row_count"] == EXPECTED_ROW_COUNT
            for audit in condition_audits.values()
        ),
        "all_schedules_exact": all(
            audit["phase_counts"] == PHASE_COUNTS
            for audit in condition_audits.values()
        ),
        "one_common_executed_source": True,
        "executed_source_matches_current": all(current_source_checks.values()),
        "cross_arm_exogenous_yoking_exact": bool(
            yoking["all_six_exogenous_yoke_digests_equal"]
        ),
        "rplus_rminus_multiplier_contrast_exact": bool(
            multiplier_yoking["exact_final_difference_only"]
        ),
    }
    passed = all(criteria.values())
    return {
        "schema": AUDIT_SCHEMA,
        "version": VERSION,
        "development_only": True,
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "matrix_root": matrix_root.as_posix(),
        "seed": seed,
        "expected": {
            "condition_ids": list(CONDITIONS),
            "conditions": CONDITIONS,
            "row_schema": ROW_SCHEMA,
            "rows_per_condition": EXPECTED_ROW_COUNT,
            "total_rows": EXPECTED_ROW_COUNT * len(CONDITIONS),
            "phase_counts": PHASE_COUNTS,
        },
        "common_source_sha256": common_source,
        "current_source_checks": current_source_checks,
        "condition_audits": condition_audits,
        "cross_arm_exogenous_yoking": yoking,
        "multiplier_yoking": multiplier_yoking,
        "criteria": criteria,
        "all_checks_pass": passed,
        "status": (
            "V041_DEVELOPMENT_INTEGRITY_YOKING_PASS"
            if passed
            else "V041_DEVELOPMENT_INTEGRITY_YOKING_FAIL"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit v0.41 development matrix integrity and yoking."
    )
    parser.add_argument("--matrix-root", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=EXPECTED_SEED)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.matrix_root / "integrity_yoking_audit.json"
    if output.resolve(strict=False).parent != args.matrix_root.resolve(strict=True):
        raise AuditFailure("audit output must be a direct child of matrix root")
    result = audit_matrix(args.matrix_root, seed=int(args.seed))
    audit_sha = _exclusive_json(output, result)
    print(
        json.dumps(
            {
                "output": output.resolve().as_posix(),
                "audit_sha256": audit_sha,
                "status": result["status"],
                "total_rows": result["expected"]["total_rows"],
                "criteria": result["criteria"],
            },
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ),
        flush=True,
    )
    return 0 if result["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
