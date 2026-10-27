"""Fail-closed development runner for one RRCT v0.41 matrix condition.

This runner is intentionally development-only.  It claims exactly one output
directory, streams the complete row trace durably, and treats scientific
endpoint failure as a retained result rather than an execution failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


START_NAME = "start_receipt.json"
ROWS_NAME = "sealed_rows.jsonl"
SUMMARY_NAME = "summary.json"
FINISH_NAME = "finish_receipt.json"
ARTIFACT_NAME = "artifact_sha256.json"

START_SCHEMA = "rrct.v041.development_condition.start.v1"
FINISH_SCHEMA = "rrct.v041.development_condition.finish.v1"

CONDITIONS: dict[str, dict[str, Any]] = {
    "K_RPLUS": {
        "historical_prior_enabled": True,
        "history_policy": "keyed",
        "world_variant": "true_recurrence",
    },
    "N_RPLUS": {
        "historical_prior_enabled": False,
        "history_policy": "withheld",
        "world_variant": "true_recurrence",
    },
    "G_RPLUS": {
        "historical_prior_enabled": True,
        "history_policy": "generic",
        "world_variant": "true_recurrence",
    },
    "K_RMINUS": {
        "historical_prior_enabled": True,
        "history_policy": "keyed",
        "world_variant": "same_key_null_lure",
    },
    "N_RMINUS": {
        "historical_prior_enabled": False,
        "history_policy": "withheld",
        "world_variant": "same_key_null_lure",
    },
    "G_RMINUS": {
        "historical_prior_enabled": True,
        "history_policy": "generic",
        "world_variant": "same_key_null_lure",
    },
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _expected_phase(
    index: int,
    phase_steps: tuple[tuple[str, int], ...],
) -> tuple[str, int]:
    start = 0
    for name, count in phase_steps:
        stop = start + int(count)
        if start <= index < stop:
            return str(name), int(index - start)
        start = stop
    raise IndexError(f"transition index {index} lies outside the frozen schedule")


def _expected_multiplier(phase: str, world_variant: str) -> float:
    from rrct.temporal_self_identity_experiment import (
        V041_A_RETURN_MULTIPLIER,
        V041_B_RETURN_MULTIPLIER,
        V041_SAME_KEY_LURE_MULTIPLIER,
    )

    if phase in {"identity_b_first", "identity_b_return"}:
        return float(V041_B_RETURN_MULTIPLIER)
    if world_variant == "same_key_null_lure" and phase == "identity_a_return_two":
        return float(V041_SAME_KEY_LURE_MULTIPLIER)
    return float(V041_A_RETURN_MULTIPLIER)


def _source_hashes(project_root: Path) -> dict[str, str]:
    paths = (
        "src/rrct/post_change_closure_experiment.py",
        "src/rrct/temporal_self_identity.py",
        "src/rrct/temporal_self_identity_experiment.py",
        "validation/run_v041_development_condition.py",
    )
    result: dict[str, str] = {}
    for relative in paths:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(f"required development source is missing: {relative}")
        result[relative] = _sha256_file(path)
    return result


def run_condition(
    *,
    project_root: Path,
    seed: int,
    condition_id: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Execute one complete development condition into a new directory."""

    from rrct.temporal_self_identity import TemporalSelfIdentityConfig
    from rrct.temporal_self_identity_experiment import (
        V041_D1_CONFIG,
        V041_ROW_SCHEMA,
        V041_SUMMARY_SCHEMA,
        V041_VERSION,
        run_temporal_self_identity_trace,
    )
    from rrct.unified_causal_loop_experiment import (
        _DurableRowStream,
        _exclusive_json,
        _fsync_directory,
        _jsonl_row_bytes,
    )

    project_root = project_root.resolve(strict=True)
    if condition_id not in CONDITIONS:
        raise ValueError(f"unknown condition_id {condition_id!r}")
    if isinstance(seed, bool) or not 0 <= int(seed) < 2**63:
        raise ValueError("seed must be an integer in [0, 2**63)")
    seed = int(seed)

    condition = dict(CONDITIONS[condition_id])
    output_dir = output_dir.resolve(strict=False)
    if output_dir.name != condition_id:
        raise ValueError("output directory basename must equal condition_id")
    if not output_dir.parent.is_dir():
        raise FileNotFoundError("output directory parent does not exist")
    output_dir.mkdir(exist_ok=False)
    _fsync_directory(output_dir.parent)

    temporal_config = TemporalSelfIdentityConfig(
        historical_prior_enabled=bool(condition["historical_prior_enabled"]),
        history_policy=condition["history_policy"],
    )
    if temporal_config.history_policy != condition["history_policy"]:
        raise RuntimeError(
            "temporal configuration changed the registered history policy"
        )
    if (
        temporal_config.historical_prior_enabled
        != condition["historical_prior_enabled"]
    ):
        raise RuntimeError(
            "temporal configuration changed the registered prior switch"
        )

    phase_steps = tuple(
        (str(name), int(count)) for name, count in V041_D1_CONFIG.phase_steps
    )
    expected_count = int(V041_D1_CONFIG.total_steps)
    if expected_count != 10_560:
        raise RuntimeError("v0.41 development schedule is not exactly 10,560 transitions")
    expected_phase_counts = {name: count for name, count in phase_steps}
    if sum(expected_phase_counts.values()) != expected_count:
        raise RuntimeError("v0.41 phase schedule does not sum to the expected row count")

    condition_payload = {
        "condition_id": condition_id,
        "temporal_identity_config": asdict(temporal_config),
        "world_variant": condition["world_variant"],
        "experiment_config": asdict(V041_D1_CONFIG),
        "phase_steps": phase_steps,
    }
    source_hashes = _source_hashes(project_root)
    start_receipt = {
        "schema": START_SCHEMA,
        "version": V041_VERSION,
        "development_only": True,
        "seed": seed,
        "condition_id": condition_id,
        "history_policy": temporal_config.history_policy,
        "historical_prior_enabled": temporal_config.historical_prior_enabled,
        "world_variant": condition["world_variant"],
        "expected_transition_count": expected_count,
        "expected_phase_counts": expected_phase_counts,
        "condition_config_sha256": _canonical_sha256(condition_payload),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "executable": sys.executable,
            "platform": platform.platform(),
            "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
            "openblas_num_threads": os.environ.get("OPENBLAS_NUM_THREADS"),
            "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
            "mkl_num_threads": os.environ.get("MKL_NUM_THREADS"),
        },
        "source_sha256": source_hashes,
        "row_serialization": {
            "json_sort_keys": True,
            "json_separators": [",", ":"],
            "allow_nan": False,
            "line_ending": "LF",
            "fsync_each_row": True,
        },
        "success_semantics": "integrity_complete_independent_of_scientific_endpoints",
    }
    start_sha = _exclusive_json(output_dir / START_NAME, start_receipt)

    stream = _DurableRowStream(output_dir / ROWS_NAME)
    phase_counts = {name: 0 for name, _count in phase_steps}
    try:
        def sink(row: Mapping[str, Any]) -> None:
            index = stream.row_count
            if row.get("schema") != V041_ROW_SCHEMA:
                raise RuntimeError(f"row {index} has the wrong v0.41 schema")
            if int(row.get("seed", -1)) != seed:
                raise RuntimeError(f"row {index} has the wrong seed")
            if int(row.get("transition_index", -1)) != index:
                raise RuntimeError(f"row {index} breaks the transition sequence")
            expected_phase, expected_offset = _expected_phase(index, phase_steps)
            if row.get("phase") != expected_phase:
                raise RuntimeError(f"row {index} has the wrong phase")
            if int(row.get("phase_offset", -1)) != expected_offset:
                raise RuntimeError(f"row {index} has the wrong phase offset")
            if row.get("history_policy") != temporal_config.history_policy:
                raise RuntimeError(f"row {index} has the wrong history policy")
            if (
                row.get("world_variant_evaluator_only")
                != condition["world_variant"]
            ):
                raise RuntimeError(f"row {index} has the wrong world variant")
            multiplier = float(
                row.get("task_return_multiplier_evaluator_only", float("nan"))
            )
            if multiplier != _expected_multiplier(
                expected_phase,
                condition["world_variant"],
            ):
                raise RuntimeError(f"row {index} has the wrong task-return multiplier")
            required_integrity = (
                "hard_integrity_valid",
                "v039_wrapper_integrity",
                "v040_wrapper_integrity",
                "v041_wrapper_integrity",
                "temporal_action_gate_binding_valid",
                "runtime_identity_ok",
            )
            if not all(bool(row.get(name)) for name in required_integrity):
                raise RuntimeError(f"row {index} failed a mandatory integrity check")
            if int(row.get("reset_count", -1)) != 0:
                raise RuntimeError(f"row {index} records a runtime reset")
            if bool(row.get("evaluator_truth_leak")):
                raise RuntimeError(f"row {index} records evaluator-truth leakage")
            phase_counts[expected_phase] += 1
            stream.append(row)
            if stream.row_count % 480 == 0:
                print(
                    f"condition={condition_id} seed={seed} "
                    f"rows={stream.row_count}/{expected_count} "
                    f"phase={expected_phase} offset={expected_offset}",
                    flush=True,
                )

        completed_rows, summary = run_temporal_self_identity_trace(
            seed,
            temporal_identity_config=temporal_config,
            world_variant=condition["world_variant"],
            sealed_row_sink=sink,
        )
        stream.close()

        if stream.row_count != expected_count:
            raise RuntimeError("durable row stream has the wrong row count")
        if len(completed_rows) != expected_count:
            raise RuntimeError("returned trace has the wrong row count")
        if phase_counts != expected_phase_counts:
            raise RuntimeError("durable row stream has the wrong phase counts")

        returned_digest = hashlib.sha256()
        for row in completed_rows:
            returned_digest.update(_jsonl_row_bytes(row))
        if returned_digest.hexdigest() != stream.sha256:
            raise RuntimeError("returned rows disagree with the durable row stream")
        if _sha256_file(output_dir / ROWS_NAME) != stream.sha256:
            raise RuntimeError("durable row file hash disagrees with the stream hash")

        if summary.get("schema") != V041_SUMMARY_SCHEMA:
            raise RuntimeError("run summary has the wrong schema")
        if summary.get("version") != V041_VERSION:
            raise RuntimeError("run summary has the wrong version")
        if int(summary.get("seed", -1)) != seed:
            raise RuntimeError("run summary has the wrong seed")
        summary_condition = summary.get("condition")
        if not isinstance(summary_condition, Mapping):
            raise RuntimeError("run summary has no condition mapping")
        if (
            summary_condition.get("history_policy")
            != temporal_config.history_policy
        ):
            raise RuntimeError("run summary has the wrong history policy")
        if summary_condition.get("world_variant") != condition["world_variant"]:
            raise RuntimeError("run summary has the wrong world variant")
        summary_schedule = [
            [str(name), int(count)] for name, count in summary.get("schedule", ())
        ]
        if summary_schedule != [[name, count] for name, count in phase_steps]:
            raise RuntimeError("run summary has the wrong phase schedule")
        summary_integrity = summary.get("integrity")
        if not isinstance(summary_integrity, Mapping) or not summary_integrity:
            raise RuntimeError("run summary has no integrity section")
        if not all(bool(value) for value in summary_integrity.values()):
            raise RuntimeError("run summary reports an integrity failure")
        engine_integrity = summary.get("engine_summary", {}).get("integrity")
        if not isinstance(engine_integrity, Mapping) or not engine_integrity:
            raise RuntimeError("run summary has no engine-integrity section")
        if not all(bool(value) for value in engine_integrity.values()):
            raise RuntimeError("engine summary reports an integrity failure")
        if bool(summary["temporal_identity"]["historical_prior_enabled"]) != bool(
            temporal_config.historical_prior_enabled
        ):
            raise RuntimeError("run summary has the wrong historical-prior switch")

        summary_sha = _exclusive_json(output_dir / SUMMARY_NAME, summary)
        finish_receipt = {
            "schema": FINISH_SCHEMA,
            "version": V041_VERSION,
            "development_only": True,
            "seed": seed,
            "condition_id": condition_id,
            "history_policy": temporal_config.history_policy,
            "world_variant": condition["world_variant"],
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "start_receipt_sha256": start_sha,
            "rows_count": stream.row_count,
            "rows_sha256": stream.sha256,
            "summary_sha256": summary_sha,
            "integrity_complete": True,
            "scientific_all_endpoints_met": bool(summary.get("all_endpoints_met")),
            "scientific_status": summary.get("status"),
            "status": "V041_DEVELOPMENT_CONDITION_INTEGRITY_COMPLETE",
        }
        finish_sha = _exclusive_json(output_dir / FINISH_NAME, finish_receipt)
        artifact_hashes = {
            START_NAME: _sha256_file(output_dir / START_NAME),
            ROWS_NAME: _sha256_file(output_dir / ROWS_NAME),
            SUMMARY_NAME: _sha256_file(output_dir / SUMMARY_NAME),
            FINISH_NAME: _sha256_file(output_dir / FINISH_NAME),
        }
        if artifact_hashes != {
            START_NAME: start_sha,
            ROWS_NAME: stream.sha256,
            SUMMARY_NAME: summary_sha,
            FINISH_NAME: finish_sha,
        }:
            raise RuntimeError("artifact hashes changed before manifest creation")
        _exclusive_json(output_dir / ARTIFACT_NAME, artifact_hashes)
        return finish_receipt
    except BaseException:
        stream.close()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one fail-closed RRCT v0.41 development condition."
    )
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--condition-id", choices=tuple(CONDITIONS), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    finish = run_condition(
        project_root=project_root,
        seed=args.seed,
        condition_id=args.condition_id,
        output_dir=args.output_dir,
    )
    print(json.dumps(finish, indent=2, sort_keys=True, allow_nan=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
