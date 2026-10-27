#!/usr/bin/env python3
"""Verify RRCT v0.44 compact evidence and optionally replay the frozen cohort."""
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


def _close(left: Any, right: Any, tolerance: float = 1e-12) -> bool:
    try:
        return abs(float(left) - float(right)) <= tolerance
    except (TypeError, ValueError):
        return False


def _verify_result_manifest(results: Path) -> tuple[dict[str, Any], dict[str, bool]]:
    manifest_path = results / "RESULT_SHA256.json"
    companion_path = manifest_path.with_suffix(manifest_path.suffix + ".sha256")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    companion = companion_path.read_text(encoding="utf-8").strip().split()
    checks: dict[str, bool] = {
        "result_manifest_companion_matches": bool(
            companion and companion[0] == _sha256(manifest_path)
        ),
        "result_manifest_schema": payload.get("schema")
        == "rrct.v044.result_manifest.v1",
        "result_manifest_endpoints_met": payload.get("all_frozen_endpoints_met")
        is True,
    }
    entries = payload.get("files", [])
    checks["result_manifest_has_files"] = isinstance(entries, list) and len(entries) >= 7
    observed: set[str] = set()
    for entry in entries:
        relative = entry.get("relative_path")
        if not isinstance(relative, str) or relative in observed:
            checks[f"result_manifest_unique::{relative}"] = False
            continue
        observed.add(relative)
        path = results / relative
        try:
            path.resolve().relative_to(results.resolve())
            confined = True
        except ValueError:
            confined = False
        checks[f"result_file_confined::{relative}"] = confined
        checks[f"result_file_present::{relative}"] = path.is_file()
        checks[f"result_file_size::{relative}"] = bool(
            path.is_file() and path.stat().st_size == entry.get("size_bytes")
        )
        checks[f"result_file_sha256::{relative}"] = bool(
            path.is_file() and _sha256(path) == entry.get("sha256")
        )
    return payload, checks


def _mean(rows: Sequence[Mapping[str, Any]], key: str) -> float:
    if not rows:
        return float("nan")
    return sum(float(row[key]) for row in rows) / len(rows)


def _recompute_mode_summary(
    rows: list[Mapping[str, Any]], mode: str, scenarios: Sequence[str]
) -> dict[str, Any]:
    selected = [row for row in rows if row["mode"] == mode]
    if not selected:
        raise ValueError(f"no decision rows for mode {mode}")
    by_scenario: dict[str, Any] = {}
    for scenario in scenarios:
        subset = [row for row in selected if row["scenario"] == scenario]
        by_scenario[scenario] = {
            "n": len(subset),
            "relation_accuracy": _mean(subset, "relation_correct"),
            "group_accuracy": _mean(subset, "group_status_correct"),
            "task_accuracy": _mean(subset, "task_correct"),
            "mean_regret": _mean(subset, "regret"),
            "mean_total_evidence_cost": _mean(subset, "total_evidence_cost"),
            "refinement_rate": _mean(subset, "refinement_requested"),
        }
    return {
        "n": len(selected),
        "relation_accuracy": _mean(selected, "relation_correct"),
        "group_accuracy": _mean(selected, "group_status_correct"),
        "continuation_recall": _mean(selected, "continuation_recall"),
        "replacement_specificity": _mean(selected, "replacement_specificity"),
        "unresolved_accuracy": _mean(selected, "unresolved_accuracy"),
        "fork_exact_rate": _mean(selected, "fork_exact"),
        "task_accuracy": _mean(selected, "task_correct"),
        "mean_regret": _mean(selected, "regret"),
        "mean_continuity_evidence_rows": _mean(
            selected, "continuity_evidence_rows"
        ),
        "mean_planning_discovery_cost": _mean(
            selected, "planning_discovery_cost"
        ),
        "mean_total_evidence_cost": _mean(selected, "total_evidence_cost"),
        "refinement_rate": _mean(selected, "refinement_requested"),
        "wrong_memory_transfer_rate": _mean(selected, "wrong_memory_transfer"),
        "receipt_chain_valid_rate": _mean(selected, "receipt_chain_valid"),
        "superior_replacement_acceptance": _mean(
            [
                row
                for row in selected
                if row["scenario"] == "superior_replacement"
            ],
            "selected_superior_replacement",
        ),
        "lineage_registration_rate": _mean(
            selected, "successor_lineage_registered"
        ),
        "by_scenario": by_scenario,
    }


def _compare_summary(
    prefix: str,
    recomputed: Mapping[str, Any],
    stored: Mapping[str, Any],
    checks: dict[str, bool],
) -> None:
    for name, value in recomputed.items():
        if name == "by_scenario":
            for scenario, metrics in value.items():
                stored_metrics = stored.get("by_scenario", {}).get(scenario, {})
                for metric, metric_value in metrics.items():
                    check = f"{prefix}::{scenario}::{metric}"
                    if metric == "n":
                        checks[check] = int(metric_value) == int(
                            stored_metrics.get(metric, -1)
                        )
                    else:
                        checks[check] = _close(
                            metric_value, stored_metrics.get(metric)
                        )
        elif name == "n":
            checks[f"{prefix}::{name}"] = int(value) == int(stored.get(name, -1))
        else:
            checks[f"{prefix}::{name}"] = _close(value, stored.get(name))


def _verify_multigeneration(
    challenges: Sequence[Mapping[str, Any]],
    seeds: Sequence[int],
    lineage_sequence: Sequence[str],
) -> dict[str, bool]:
    checks: dict[str, bool] = {
        "multigeneration_count": len(challenges) == len(seeds) == 4,
        "multigeneration_seed_set": [int(value["seed"]) for value in challenges]
        == list(seeds),
    }
    for challenge in challenges:
        seed = int(challenge.get("seed", -1))
        prefix = f"multigeneration::{seed}"
        stages = challenge.get("stages", [])
        checks[f"{prefix}::schema"] = challenge.get("schema") == (
            "rrct.v044.multigeneration_lineage_challenge.v1"
        )
        checks[f"{prefix}::complete"] = challenge.get("complete") is True
        checks[f"{prefix}::all_checks_pass"] = (
            challenge.get("all_checks_pass") is True
        )
        checks[f"{prefix}::parent_chain_valid"] = (
            challenge.get("parent_chain_valid") is True
        )
        checks[f"{prefix}::generations_valid"] = (
            challenge.get("generations_valid") is True
        )
        checks[f"{prefix}::reward_and_label_free"] = (
            challenge.get("reward_and_label_free") is True
        )
        checks[f"{prefix}::sequence"] = challenge.get("sequence") == list(
            lineage_sequence
        )
        checks[f"{prefix}::stage_count"] = len(stages) == len(lineage_sequence) == 5
        checks[f"{prefix}::final_generation"] = int(
            challenge.get("final_generation", -1)
        ) == 5
        checks[f"{prefix}::lineage_count"] = int(
            challenge.get("lineage_count", -1)
        ) == 6
        previous = challenge.get("initial_lineage_digest")
        chain_valid = _valid_sha(previous)
        for index, stage in enumerate(stages):
            chain_valid = chain_valid and (
                int(stage.get("stage_index", -1)) == index
                and stage.get("scenario") == lineage_sequence[index]
                and int(stage.get("predecessor_generation", -1)) == index
                and int(stage.get("successor_generation", -1)) == index + 1
                and stage.get("predecessor_lineage_digest") == previous
                and stage.get("successor_parent_digest") == previous
                and stage.get("receipt_chain_valid") is True
                and stage.get("stage_pass") is True
                and _valid_sha(stage.get("transition_digest"))
                and _valid_sha(stage.get("adjudication_digest"))
                and _valid_sha(stage.get("planning_digest"))
                and _valid_sha(stage.get("outcome_digest"))
                and _valid_sha(stage.get("successor_lineage_digest"))
            )
            previous = stage.get("successor_lineage_digest")
        chain_valid = chain_valid and previous == challenge.get(
            "final_lineage_digest"
        )
        checks[f"{prefix}::independent_parent_chain"] = bool(chain_valid)
    return checks


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify RRCT v0.44 evidence, receipts, summaries, and replay"
    )
    parser.add_argument("--skip-replay", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("validation/V0_44_RELEASE_VERIFICATION.json"),
    )
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    results = (
        root
        / "validation/v0.44.0_transformational_self_continuity/results"
    )

    from rrct.transformational_self_continuity_experiment import (  # noqa: PLC0415
        V044_HOLDOUT_SEEDS,
        V044_LINEAGE_SEQUENCE,
        V044_MODES,
        V044_SCENARIOS,
        V044_TRIALS_PER_SCENARIO,
        _verify_holdout_freeze,
        run_transformational_self_continuity_cohort,
    )

    checks: dict[str, bool] = {}
    freeze_sha = _verify_holdout_freeze()
    checks["preoutcome_freeze_verifies"] = _valid_sha(freeze_sha)

    result_manifest, manifest_checks = _verify_result_manifest(results)
    checks.update(manifest_checks)

    analysis_path = results / "transformational_self_continuity_analysis.json"
    summary_path = results / "transformational_self_continuity_summary.json"
    csv_path = results / "transformational_self_continuity_decisions.csv"
    execution_path = results / "HOLDOUT_EXECUTION_RECEIPT.json"
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    execution = json.loads(execution_path.read_text(encoding="utf-8"))

    checks.update(
        {
            "analysis_schema": analysis.get("schema")
            == "rrct.v044.transformational_self_continuity_analysis.v1",
            "analysis_is_frozen_holdout": analysis.get("cohort")
            == "frozen_holdout",
            "analysis_status": analysis.get("scientific_status")
            == "fresh_frozen_holdout_functional_development",
            "analysis_seeds_match_freeze": analysis.get("seeds")
            == list(V044_HOLDOUT_SEEDS),
            "analysis_modes_match_freeze": analysis.get("modes")
            == list(V044_MODES),
            "analysis_scenarios_match_freeze": analysis.get("scenarios")
            == list(V044_SCENARIOS),
            "analysis_trials_match_freeze": int(
                analysis.get("trials_per_scenario", -1)
            )
            == V044_TRIALS_PER_SCENARIO,
            "analysis_freeze_digest_matches": analysis.get(
                "preoutcome_freeze_sha256"
            )
            == freeze_sha,
            "all_23_endpoints_present": len(
                analysis.get("frozen_endpoints", {})
            )
            == 23,
            "all_frozen_endpoints_met": analysis.get(
                "all_frozen_endpoints_met"
            )
            is True
            and all(analysis.get("frozen_endpoints", {}).values()),
            "execution_schema": execution.get("schema")
            == "rrct.v044.holdout_execution.v1",
            "execution_analysis_sha_matches": execution.get("analysis_sha256")
            == _sha256(analysis_path),
            "execution_freeze_sha_matches": execution.get(
                "preoutcome_freeze_sha256"
            )
            == freeze_sha,
            "execution_seeds_match": execution.get("holdout_seeds")
            == list(V044_HOLDOUT_SEEDS),
            "execution_endpoints_met": execution.get(
                "all_frozen_endpoints_met"
            )
            is True,
            "execution_verified_before_outcome": execution.get(
                "outcome_opened_only_after_freeze_verification"
            )
            is True,
            "result_manifest_analysis_sha_matches": result_manifest.get(
                "analysis_sha256"
            )
            == _sha256(analysis_path),
            "result_manifest_freeze_sha_matches": result_manifest.get(
                "preoutcome_freeze_sha256"
            )
            == freeze_sha,
            "summary_schema": summary.get("schema")
            == "rrct.v044.transformational_self_continuity_summary.v1",
            "summary_status": summary.get("status")
            == "V044_FROZEN_ENDPOINTS_MET",
            "summary_version": summary.get("version") == "0.44.0.dev1",
            "summary_freeze_digest_matches": summary.get(
                "preoutcome_freeze_sha256"
            )
            == freeze_sha,
            "summary_seeds_match": summary.get("holdout_seeds")
            == list(V044_HOLDOUT_SEEDS),
            "summary_modes_match": summary.get("modes") == list(V044_MODES),
            "summary_scenario_count": int(summary.get("scenario_count", -1))
            == len(V044_SCENARIOS),
            "summary_trial_count": int(summary.get("trials_per_scenario", -1))
            == V044_TRIALS_PER_SCENARIO,
            "summary_endpoint_map_matches": summary.get("frozen_endpoints")
            == analysis.get("frozen_endpoints"),
            "summary_intact_matches": summary.get("intact")
            == analysis.get("mode_summaries", {}).get("intact"),
            "summary_controls_match": summary.get("key_controls")
            == {
                mode: value
                for mode, value in analysis.get("mode_summaries", {}).items()
                if mode != "intact"
            },
            "summary_analysis_sha_matches": summary.get("artifact_sha256", {}).get(
                "analysis"
            )
            == _sha256(analysis_path),
            "summary_csv_sha_matches": summary.get("artifact_sha256", {}).get(
                "decision_csv"
            )
            == _sha256(csv_path),
            "summary_report_sha_matches": summary.get("artifact_sha256", {}).get(
                "report"
            )
            == _sha256(results / "TRANSFORMATIONAL_SELF_CONTINUITY_REPORT.md"),
            "summary_execution_sha_matches": summary.get("artifact_sha256", {}).get(
                "execution_receipt"
            )
            == _sha256(execution_path),
        }
    )

    rows = list(analysis.get("decision_rows", []))
    expected_rows = (
        len(V044_HOLDOUT_SEEDS)
        * len(V044_SCENARIOS)
        * V044_TRIALS_PER_SCENARIO
        * len(V044_MODES)
    )
    mode_counts = Counter(str(row.get("mode")) for row in rows)
    scenario_mode_counts = Counter(
        (str(row.get("scenario")), str(row.get("mode"))) for row in rows
    )
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
            "decision_row_count": len(rows) == expected_rows == 4608,
            "decision_keys_unique": len(decision_keys) == len(rows),
            "mode_counts_balanced": set(mode_counts.values()) == {576}
            and set(mode_counts) == set(V044_MODES),
            "scenario_mode_counts_balanced": set(
                scenario_mode_counts.values()
            )
            == {64},
            "all_receipt_chains_valid": all(
                bool(row["receipt_chain_valid"]) for row in rows
            ),
            "no_evaluator_labels_in_rows": not any(
                bool(row["uses_evaluator_labels"]) for row in rows
            ),
            "all_transition_digests_well_formed": all(
                _valid_sha(row["transition_digest"]) for row in rows
            ),
            "all_adjudication_digests_well_formed": all(
                _valid_sha(row["adjudication_digest"]) for row in rows
            ),
            "all_plan_digests_well_formed": all(
                _valid_sha(row["planning_digest"]) for row in rows
            ),
            "all_outcome_digests_well_formed": all(
                _valid_sha(row["outcome_digest"]) for row in rows
            ),
            "all_assessment_digests_well_formed": all(
                isinstance(row.get("assessment_digests"), dict)
                and bool(row["assessment_digests"])
                and all(_valid_sha(value) for value in row["assessment_digests"].values())
                for row in rows
            ),
        }
    )

    for mode in V044_MODES:
        recomputed = _recompute_mode_summary(rows, mode, V044_SCENARIOS)
        stored = analysis["mode_summaries"][mode]
        _compare_summary(
            f"summary_recomputed::{mode}", recomputed, stored, checks
        )

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    checks["csv_row_count_matches_json"] = len(csv_rows) == len(rows)
    checks["summary_matched_decision_count"] = int(
        summary.get("matched_arm_decisions", -1)
    ) == len(rows)

    audit = analysis.get("runtime_reward_and_label_audit", {})
    checks["runtime_nonvalenced"] = (
        audit.get("explicit_survival_reward_values") == [0.0]
        and audit.get("explicit_identity_reward_values") == [0.0]
        and audit.get("explicit_continuity_reward_values") == [0.0]
        and audit.get("uses_evaluator_labels") is False
        and int(audit.get("snapshot_count", -1)) == len(rows)
    )

    challenges = analysis.get("multigeneration_lineage_challenges", [])
    checks.update(
        _verify_multigeneration(
            challenges, V044_HOLDOUT_SEEDS, V044_LINEAGE_SEQUENCE
        )
    )
    compact_challenges = summary.get("multigeneration_lineages", [])
    checks["compact_multigeneration_count"] = len(compact_challenges) == 4
    checks["compact_multigeneration_all_pass"] = all(
        value.get("all_checks_pass") is True
        and int(value.get("final_generation", -1)) == 5
        and int(value.get("lineage_count", -1)) == 6
        and value.get("parent_chain_valid") is True
        for value in compact_challenges
    )

    replay_equal: bool | None = None
    normalized_replay_sha: str | None = None
    if not args.skip_replay:
        replay = run_transformational_self_continuity_cohort(
            V044_HOLDOUT_SEEDS,
            cohort="frozen_holdout",
        )
        stored_normalized = dict(analysis)
        stored_normalized.pop("execution_receipt", None)
        replay_equal = stored_normalized == replay
        canonical = json.dumps(
            replay, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        normalized_replay_sha = hashlib.sha256(canonical).hexdigest()
        checks["deterministic_replay_exact"] = replay_equal
        checks["normalized_replay_sha_matches_summary"] = (
            normalized_replay_sha == summary.get("normalized_replay_sha256")
        )

    output = args.output
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "rrct.v044.release_verification.v1",
        "verified_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "preoutcome_freeze_sha256": freeze_sha,
        "analysis_sha256": _sha256(analysis_path),
        "result_manifest_sha256": _sha256(results / "RESULT_SHA256.json"),
        "deterministic_replay_requested": not args.skip_replay,
        "deterministic_replay_exact": replay_equal,
        "normalized_replay_sha256": normalized_replay_sha,
        "checks": checks,
        "check_count": len(checks),
        "all_checks_pass": all(checks.values()),
        "failed_checks": sorted(
            name for name, passed in checks.items() if not passed
        ),
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
                    "V044_RELEASE_VERIFIED"
                    if payload["all_checks_pass"]
                    else "V044_RELEASE_VERIFICATION_FAILED"
                ),
                "all_checks_pass": payload["all_checks_pass"],
                "check_count": len(checks),
                "failed_checks": payload["failed_checks"],
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
