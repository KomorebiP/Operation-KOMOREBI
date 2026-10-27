#!/usr/bin/env python3
"""Verify packaged RRCT v0.43 evidence and optionally replay it exactly."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _valid_sha(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _verify_result_manifest(results: Path) -> tuple[dict[str, Any], dict[str, bool]]:
    manifest_path = results / "RESULT_SHA256.json"
    companion_path = results / "RESULT_SHA256.json.sha256"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    companion = companion_path.read_text(encoding="utf-8").strip().split()
    checks = {
        "result_manifest_companion_matches": bool(
            companion and companion[0] == _sha256(manifest_path)
        ),
        "result_manifest_schema": payload.get("schema")
        == "rrct.v043.result_manifest.v1",
        "result_manifest_endpoints_met": payload.get("all_frozen_endpoints_met")
        is True,
    }
    for entry in payload.get("files", []):
        relative = entry.get("relative_path")
        path = results / str(relative)
        checks[f"result_file_present::{relative}"] = path.is_file()
        checks[f"result_file_size::{relative}"] = bool(
            path.is_file() and path.stat().st_size == entry.get("size_bytes")
        )
        checks[f"result_file_sha256::{relative}"] = bool(
            path.is_file() and _sha256(path) == entry.get("sha256")
        )
    return payload, checks


def _recompute_mode_summary(rows: list[Mapping[str, Any]], mode: str) -> dict[str, float]:
    selected = [row for row in rows if row["mode"] == mode]
    if not selected:
        raise ValueError(f"no rows for mode {mode}")

    def mean(name: str) -> float:
        return sum(float(row[name]) for row in selected) / len(selected)

    replacements = [
        row for row in selected if row["scenario"] == "superior_replacement"
    ]
    return {
        "accuracy": mean("correct"),
        "mean_regret": mean("regret"),
        "mean_samples_per_candidate": mean("samples_per_candidate"),
        "refinement_rate": mean("refinement_used"),
        "receipt_chain_valid_rate": mean("receipt_chain_valid"),
        "self_model_authorized_rate": mean("self_model_authorized"),
        "superior_replacement_acceptance": sum(
            float(row["selected_better_replacement"]) for row in replacements
        )
        / len(replacements),
    }


def _close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify RRCT v0.43 package checksums, summaries, and replay"
    )
    parser.add_argument("--skip-replay", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("validation/V0_43_RELEASE_VERIFICATION.json"),
    )
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    results = root / "validation/v0.43.0_whole_loop_causal_closure/results"

    from rrct.whole_loop_causal_closure_experiment import (  # noqa: PLC0415
        V043_HOLDOUT_SEEDS,
        _verify_holdout_freeze,
        run_whole_loop_closure_cohort,
    )

    checks: dict[str, bool] = {}
    freeze_sha = _verify_holdout_freeze()
    checks["preoutcome_freeze_verifies"] = _valid_sha(freeze_sha)

    result_manifest, manifest_checks = _verify_result_manifest(results)
    checks.update(manifest_checks)

    analysis_path = results / "whole_loop_closure_analysis.json"
    summary_path = results / "whole_loop_closure_summary.json"
    csv_path = results / "whole_loop_decisions.csv"
    execution_path = results / "HOLDOUT_EXECUTION_RECEIPT.json"
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    execution = json.loads(execution_path.read_text(encoding="utf-8"))

    checks.update(
        {
            "analysis_schema": analysis.get("schema")
            == "rrct.v043.whole_loop_causal_closure_analysis.v1",
            "analysis_is_frozen_holdout": analysis.get("cohort")
            == "frozen_holdout",
            "analysis_status": analysis.get("scientific_status")
            == "fresh_frozen_holdout_functional_development",
            "analysis_seeds_match_freeze": analysis.get("seeds")
            == list(V043_HOLDOUT_SEEDS),
            "analysis_freeze_digest_matches": analysis.get(
                "preoutcome_freeze_sha256"
            )
            == freeze_sha,
            "all_19_endpoints_present": len(analysis.get("frozen_endpoints", {}))
            == 19,
            "all_frozen_endpoints_met": analysis.get(
                "all_frozen_endpoints_met"
            )
            is True
            and all(analysis.get("frozen_endpoints", {}).values()),
            "execution_analysis_sha_matches": execution.get("analysis_sha256")
            == _sha256(analysis_path),
            "execution_freeze_sha_matches": execution.get(
                "preoutcome_freeze_sha256"
            )
            == freeze_sha,
            "execution_verified_before_outcome": execution.get(
                "outcome_opened_only_after_freeze_verification"
            )
            is True,
            "result_manifest_analysis_sha_matches": result_manifest.get(
                "analysis_sha256"
            )
            == _sha256(analysis_path),
            "summary_analysis_sha_context_matches": summary.get(
                "preoutcome_freeze_sha256"
            )
            == freeze_sha,
            "summary_endpoints_match": summary.get("frozen_endpoints")
            == analysis.get("frozen_endpoints"),
            "summary_modes_match": summary.get("mode_summaries")
            == analysis.get("mode_summaries"),
        }
    )

    rows = list(analysis.get("decision_rows", []))
    expected_rows = (
        len(V043_HOLDOUT_SEEDS)
        * len(analysis.get("scenarios", []))
        * int(analysis.get("trials_per_scenario", 0))
        * len(analysis.get("modes", []))
    )
    mode_counts = Counter(str(row.get("mode")) for row in rows)
    decision_keys = {
        (
            int(row["seed"]),
            str(row["scenario"]),
            int(row["trial"]),
            str(row["mode"]),
        )
        for row in rows
    }
    checks.update(
        {
            "decision_row_count": len(rows) == expected_rows == 3072,
            "decision_keys_unique": len(decision_keys) == len(rows),
            "mode_counts_balanced": set(mode_counts.values()) == {384},
            "all_compact_chain_flags_valid": all(
                bool(row["receipt_chain_valid"]) for row in rows
            ),
            "all_future_outcomes_unknown_at_commit": all(
                bool(row["future_outcome_unknown_at_commit"]) for row in rows
            ),
            "no_evaluator_labels_in_rows": not any(
                bool(row["uses_evaluator_labels"]) for row in rows
            ),
            "all_state_digests_well_formed": all(
                _valid_sha(row["integrated_state_digest"]) for row in rows
            ),
            "all_plan_digests_well_formed": all(
                _valid_sha(row["planning_digest"]) for row in rows
            ),
            "all_outcome_digests_well_formed": all(
                _valid_sha(row["outcome_digest"]) for row in rows
            ),
        }
    )

    for mode in analysis["modes"]:
        recomputed = _recompute_mode_summary(rows, mode)
        stored = analysis["mode_summaries"][mode]
        for metric, value in recomputed.items():
            checks[f"summary_recomputed::{mode}::{metric}"] = _close(
                value, stored[metric]
            )

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    checks["csv_row_count_matches_json"] = len(csv_rows) == len(rows)
    checks["feedback_challenges_all_pass"] = all(
        challenge.get("all_checks_pass") is True
        for challenge in analysis.get("feedback_reopening_challenges", [])
    ) and len(analysis.get("feedback_reopening_challenges", [])) == 4
    audit = analysis.get("runtime_reward_and_label_audit", {})
    checks["runtime_nonvalenced"] = (
        audit.get("explicit_survival_reward_values") == [0.0]
        and audit.get("explicit_identity_reward_values") == [0.0]
        and audit.get("uses_evaluator_labels") is False
    )

    replay_equal: bool | None = None
    if not args.skip_replay:
        replay = run_whole_loop_closure_cohort(
            V043_HOLDOUT_SEEDS,
            cohort="frozen_holdout",
        )
        stored_normalized = dict(analysis)
        stored_normalized.pop("execution_receipt", None)
        replay_equal = stored_normalized == replay
        checks["deterministic_replay_exact"] = replay_equal

    output = args.output
    if not output.is_absolute():
        output = root / output
    payload = {
        "schema": "rrct.v043.release_verification.v1",
        "verified_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "preoutcome_freeze_sha256": freeze_sha,
        "analysis_sha256": _sha256(analysis_path),
        "result_manifest_sha256": _sha256(results / "RESULT_SHA256.json"),
        "deterministic_replay_requested": not args.skip_replay,
        "deterministic_replay_exact": replay_equal,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "known_compact_package_omissions": [
            "validation/V0_36_LINEAGE_AND_SEED_REGISTRY.json",
            "validation/V0_36_DEVELOPMENT_PROTOCOL.md",
            "validation/freeze_v038_source.py",
        ],
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{_sha256(output)}  {output.name}\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": (
                    "V043_RELEASE_VERIFIED"
                    if payload["all_checks_pass"]
                    else "V043_RELEASE_VERIFICATION_FAILED"
                ),
                "all_checks_pass": payload["all_checks_pass"],
                "check_count": len(checks),
                "deterministic_replay_exact": replay_equal,
                "output": str(output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
