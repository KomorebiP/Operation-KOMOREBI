#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    checks: dict[str, bool] = {}

    freeze_path = ROOT / "validation/PREOUTCOME_FREEZE.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    companion = freeze_path.with_suffix(freeze_path.suffix + ".sha256")
    checks["preoutcome_manifest_companion"] = (
        companion.is_file()
        and companion.read_text(encoding="utf-8").split()[0] == sha256(freeze_path)
    )
    checks["preoutcome_status"] = (
        freeze.get("status") == "FROZEN_BEFORE_HOLDOUT"
        and freeze.get("holdout_outcomes_inspected") is False
    )
    checks["preoutcome_file_count"] = (
        freeze.get("file_count") == len(freeze.get("files", {})) == 9
    )
    for relative, expected in freeze["files"].items():
        path = ROOT / relative
        checks[f"sealed_present::{relative}"] = path.is_file()
        checks[f"sealed_size::{relative}"] = (
            path.is_file() and path.stat().st_size == expected["size_bytes"]
        )
        checks[f"sealed_sha::{relative}"] = (
            path.is_file() and sha256(path) == expected["sha256"]
        )

    point_paths = sorted((ROOT / "holdout_results/points").glob("*.json"))
    posthoc_paths = sorted((ROOT / "holdout_results/posthoc").glob("*.json"))
    checks["frozen_point_count"] = len(point_paths) == 28
    checks["posthoc_point_count"] = len(posthoc_paths) == 4
    points = pd.DataFrame(
        [json.loads(path.read_text(encoding="utf-8")) for path in point_paths]
    )
    checks["terminal_only"] = bool(
        points["uses_intermediate_workspace_labels_for_training"].eq(False).all()
    )
    checks["no_valence"] = bool(points["valence_model_present"].eq(False).all())
    checks["no_self_preservation_reward"] = bool(
        points["self_preservation_reward"].eq(0.0).all()
    )

    analysis = json.loads(
        (ROOT / "holdout_results/HOLDOUT_ANALYSIS.json").read_text(encoding="utf-8")
    )
    checks["frozen_failure_preserved"] = (
        analysis["status"] == "V054_HOLDOUT_ENDPOINTS_NOT_MET"
        and analysis["all_endpoints_met"] is False
        and sum(bool(value) for value in analysis["endpoints"].values()) == 13
    )
    checks["exact_failed_endpoints_preserved"] = all(
        analysis["endpoints"][key] is False
        for key in (
            "E05_d2_400_near_above",
            "E06_d2_800_above",
            "E15_above_action",
        )
    )

    validation = json.loads(
        (ROOT / "holdout_results/SCALING_VALIDATION.json").read_text(encoding="utf-8")
    )
    checks["formula_holdout_auc"] = validation["original_formula_holdout"]["auc"] >= 0.89
    checks["posthoc_completion"] = (
        validation["posthoc_d2_h32_s1200"]["n"] == 4
        and validation["posthoc_d2_h32_s1200"]["emergence_rate"] == 1.0
    )

    representative = json.loads(
        (ROOT / "holdout_results/REPRESENTATIVE_REPLAY_VERIFICATION.json").read_text(
            encoding="utf-8"
        )
    )
    posthoc_replay = json.loads(
        (ROOT / "holdout_results/POSTHOC_REPLAY_VERIFICATION.json").read_text(
            encoding="utf-8"
        )
    )
    checks["representative_replay"] = representative["all_scientific_exact"] is True
    checks["posthoc_replay"] = posthoc_replay["all_scientific_exact"] is True

    required = [
        "BLOCK_SUMMARY.md",
        "RESULT_REPORT.md",
        "PROTOCOL.md",
        "FORMULAIC_SCALING_LAW.md",
        "holdout_results/HOLDOUT_POINTS.csv",
        "holdout_results/UNCERTAINTY_ANALYSIS.json",
        "figures/01_development_emergence_dim2.png",
        "figures/02_development_emergence_dim4.png",
        "figures/03_holdout_phase_transition.png",
        "figures/04_formula_calibration.png",
        "figures/05_full_causal_metrics.png",
    ]
    for relative in required:
        checks[f"required::{relative}"] = (ROOT / relative).is_file()

    payload = {
        "schema": "rrct.v054.release_verification.v1",
        "version": "0.54.0.dev1",
        "scientific_status": analysis["status"],
        "release_status": "V054_RELEASE_VERIFIED" if all(checks.values()) else "V054_RELEASE_VERIFICATION_FAILED",
        "checks_passed": sum(bool(value) for value in checks.values()),
        "check_count": len(checks),
        "all_checks_pass": all(checks.values()),
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
        "preoutcome_freeze_sha256": sha256(freeze_path),
        "holdout_analysis_sha256": sha256(ROOT / "holdout_results/HOLDOUT_ANALYSIS.json"),
        "scaling_validation_sha256": sha256(ROOT / "holdout_results/SCALING_VALIDATION.json"),
        "claim_boundary": (
            "A phase-transition-like scaling boundary for terminally learned workspace semantics "
            "inside a supplied synthetic hierarchy. Not spontaneous hierarchy discovery, a universal "
            "cognitive scaling law, brain equivalence, functional awareness, or subjective experience."
        ),
    }
    output = ROOT / "V0_54_RELEASE_VERIFICATION.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
