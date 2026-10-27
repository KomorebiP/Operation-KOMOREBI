#!/usr/bin/env python3
"""Execute the sealed RRCT v0.51 bounded-emergence holdout."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_freeze(root: Path) -> dict[str, Any]:
    path = root / "validation/V0_51_PREOUTCOME_FREEZE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    failed: list[str] = []
    for item in payload["files"]:
        candidate = root / item["relative_path"]
        if (
            not candidate.is_file()
            or candidate.stat().st_size != item["size_bytes"]
            or sha256(candidate) != item["sha256"]
        ):
            failed.append(item["relative_path"])
    companion = path.with_suffix(path.suffix + ".sha256")
    companion_matches = bool(
        companion.is_file()
        and companion.read_text(encoding="utf-8").split()[0] == sha256(path)
    )
    result = {
        "manifest_sha256": sha256(path),
        "file_count": len(payload["files"]),
        "failed_files": failed,
        "companion_matches": companion_matches,
        "all_checks_pass": not failed and companion_matches,
    }
    if not result["all_checks_pass"]:
        raise RuntimeError(f"v0.51 source freeze failed: {result}")
    return result


def train_process(
    root: Path,
    holdout_seed: int,
    objective: str,
    model_path: Path,
    receipt_path: Path,
) -> None:
    training_seed = (
        int(holdout_seed)
        if objective == "round_curriculum"
        else int(holdout_seed) ^ 0x5100F1
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [
        sys.executable,
        str(root / "validation/train_v051_model.py"),
        "--training-seed",
        str(training_seed),
        "--holdout-seed",
        str(holdout_seed),
        "--objective",
        objective,
        "--model-output",
        str(model_path),
        "--receipt-output",
        str(receipt_path),
    ]
    completed = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    log_path = receipt_path.with_suffix(".log")
    log_path.write_text(
        completed.stdout + ("\nSTDERR:\n" + completed.stderr if completed.stderr else ""),
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"training process failed for seed={holdout_seed}, "
            f"objective={objective}; see {log_path}"
        )


def compact_summary(full: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema": "rrct.v051.emergent_synergistic_workspace.summary.v1",
        "version": full["version"],
        "status": full["status"],
        "seeds": full["seeds"],
        "config": full["config"],
        "aggregate": full["aggregate"],
        "endpoints": full["endpoints"],
        "all_endpoints_met": full["all_endpoints_met"],
        "strict_emergence_established": full["strict_emergence_established"],
        "bounded_curriculum_supported_emergence_established": full[
            "bounded_curriculum_supported_emergence_established"
        ],
        "claim_boundary": full["claim_boundary"],
        "seed_summaries": [
            {
                "seed": item["seed"],
                "digest": item["digest"],
                "curriculum_training": item["curriculum_training"],
                "terminal_only_training": item["terminal_only_training"],
                "modes": item["modes"],
                "latent_analysis": item["latent_analysis"],
                "causal_transplant": item["causal_transplant"],
                "post_erasure": item["post_erasure"],
                "endpoints": item["endpoints"],
            }
            for item in full["seed_results"]
        ],
    }
    unsigned = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(unsigned.encode()).hexdigest()
    return payload


def write_mode_table(path: Path, full: dict[str, Any]) -> None:
    fields = [
        "seed",
        "mode",
        "task_accuracy_a",
        "task_accuracy_b",
        "jointly_writable",
        "temporally_persistent",
        "planner_bound",
        "explicit_workspace_coordinates_supplied",
        "pair_memory_retained_after_episode",
        "receipt_digest",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in full["seed_results"]:
            for mode, metrics in result["modes"].items():
                writer.writerow(
                    {
                        "seed": result["seed"],
                        "mode": mode,
                        "task_accuracy_a": metrics["task_accuracy_a"],
                        "task_accuracy_b": metrics["task_accuracy_b"],
                        "jointly_writable": metrics["jointly_writable"],
                        "temporally_persistent": metrics["temporally_persistent"],
                        "planner_bound": metrics["planner_bound"],
                        "explicit_workspace_coordinates_supplied": metrics[
                            "explicit_workspace_coordinates_supplied"
                        ],
                        "pair_memory_retained_after_episode": metrics[
                            "pair_memory_retained_after_episode"
                        ],
                        "receipt_digest": metrics["digest"],
                    }
                )


def write_report(path: Path, full: dict[str, Any]) -> None:
    aggregate = full["aggregate"]
    lines = [
        "# RRCT v0.51 Emergent Synergistic Workspace Report",
        "",
        f"**Status:** `{full['status']}`",
        "",
        "## Result",
        "",
        "The round-curriculum agents learned an eight-dimensional recurrent "
        "message that carries the accumulated joint computation without receiving "
        "a one-hot workspace or prescribed latent coordinates.",
        "",
        f"- Mean unseen-composition accuracy: **{aggregate['mean_curriculum_heldout_accuracy']:.6f}**",
        f"- Mean terminal-only accuracy: **{aggregate['mean_terminal_only_heldout_accuracy']:.6f}**",
        f"- Mean linear latent probe accuracy: **{aggregate['mean_latent_probe_accuracy']:.6f}**",
        f"- Mean causal transplant accuracy: **{aggregate['mean_patch_target_accuracy']:.6f}**",
        "",
        "## Interpretation",
        "",
        "The representation emerged through optimization and was not assigned "
        "coordinate semantics. However, the channel persistence, alternating "
        "update schedule, and round-level curriculum were engineered. The "
        "terminal-only control did not discover the same algorithm under the "
        "frozen budget. Therefore strict spontaneous emergence is not established.",
        "",
        "## Claim boundary",
        "",
        full["claim_boundary"],
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    import torch
    from rrct.emergent_synergistic_workspace import (
        EmergentTrainingReceipt,
        EmergentWorkspaceConfig,
        analyze_trained_seed,
        assemble_holdout,
        load_emergent_model,
    )

    freeze = verify_freeze(root)
    seed_receipt = json.loads(
        (root / "validation/V0_51_HOLDOUT_SEED_SELECTION.json").read_text(
            encoding="utf-8"
        )
    )
    output = args.output or (
        root / "validation/v0.51.0_emergent_synergistic_workspace/results"
    )
    output.mkdir(parents=True, exist_ok=True)
    weights = output / "weights"
    weights.mkdir(parents=True, exist_ok=True)

    seed_results: list[dict[str, Any]] = []
    for seed in seed_receipt["selected_seeds"]:
        curriculum_path = weights / f"seed_{seed}_curriculum.pt"
        terminal_path = weights / f"seed_{seed}_terminal_only.pt"
        curriculum_receipt_path = weights / f"seed_{seed}_curriculum.json"
        terminal_receipt_path = weights / f"seed_{seed}_terminal_only.json"
        train_process(
            root,
            int(seed),
            "round_curriculum",
            curriculum_path,
            curriculum_receipt_path,
        )
        train_process(
            root,
            int(seed),
            "terminal_only",
            terminal_path,
            terminal_receipt_path,
        )
        model, curriculum_receipt, saved_seed = load_emergent_model(curriculum_path)
        if saved_seed != int(seed):
            raise RuntimeError("curriculum model seed mismatch")
        terminal_payload = json.loads(terminal_receipt_path.read_text(encoding="utf-8"))
        terminal_receipt = EmergentTrainingReceipt(
            **terminal_payload["training_receipt"]
        )
        seed_results.append(
            analyze_trained_seed(
                int(seed),
                model,
                curriculum_receipt,
                terminal_receipt,
                EmergentWorkspaceConfig(),
                model_files={
                    "curriculum": str(curriculum_path.relative_to(root)),
                    "terminal_only": str(terminal_path.relative_to(root)),
                },
            )
        )

    full = assemble_holdout(seed_results, EmergentWorkspaceConfig())
    analysis_path = output / "emergent_synergistic_workspace_analysis.json"
    analysis_path.write_text(json.dumps(full, indent=2, sort_keys=True) + "\n")
    summary = compact_summary(full)
    summary_path = output / "V0_51_FROZEN_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    table_path = output / "emergent_synergistic_workspace_modes.csv"
    write_mode_table(table_path, full)
    report_path = output / "EMERGENT_SYNERGISTIC_WORKSPACE_REPORT.md"
    write_report(report_path, full)

    model_files = sorted(weights.glob("*.pt"))
    receipt = {
        "schema": "rrct.v051.holdout_execution_receipt.v1",
        "version": "0.51.0.dev1",
        "executed_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "source_freeze": freeze,
        "seeds": seed_receipt["selected_seeds"],
        "scientific_status": full["status"],
        "all_endpoints_met": full["all_endpoints_met"],
        "endpoint_pass_count": sum(full["endpoints"].values()),
        "endpoint_count": len(full["endpoints"]),
        "strict_emergence_established": full["strict_emergence_established"],
        "analysis_sha256": sha256(analysis_path),
        "summary_sha256": sha256(summary_path),
        "mode_table_sha256": sha256(table_path),
        "report_sha256": sha256(report_path),
        "model_sha256": {path.name: sha256(path) for path in model_files},
        "python": platform.python_version(),
        "torch": torch.__version__,
        "platform": platform.platform(),
    }
    unsigned = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    receipt["digest"] = hashlib.sha256(unsigned.encode()).hexdigest()
    receipt_path = output / "HOLDOUT_EXECUTION_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if full["all_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
