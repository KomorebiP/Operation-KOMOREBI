from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback
from typing import Any


ROOT = Path(__file__).resolve().parent
VENDOR_ROOT = ROOT / "vendor" / "g1_v0_1_1"
sys.path.insert(0, str(VENDOR_ROOT))
sys.path.insert(0, str(ROOT))

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

from g1d.integrity import (  # noqa: E402
    acquire_lock,
    atomic_json,
    atomic_text,
    directory_hashes,
    release_lock,
    sha256_file,
    verify_fixed_source_identity,
    verify_package_manifest,
)
from g1d.static_analysis import analyze_run_artifacts, read_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only post-hoc diagnostics for a Neuralese G1 checkpoint"
    )
    parser.add_argument("--model", help="Local Qwen2.5-0.5B-Instruct directory")
    parser.add_argument(
        "--run",
        default=str(ROOT / "input_run" / "pilot-711001"),
        help="Verified G1 run directory",
    )
    parser.add_argument("--output", required=True, help="Separate diagnostic output directory")
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="Analyze saved predictions without loading the model or checkpoint tensors",
    )
    return parser.parse_args()


def _overlap(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _atomic_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            for record in records:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _atomic_torch(path: Path, value: Any) -> None:
    import torch

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    os.close(descriptor)
    try:
        torch.save(value, temporary_name)
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _artifact_manifest(output: Path, names: list[str]) -> dict[str, Any]:
    entries = []
    for name in sorted(names):
        path = output / name
        if not path.is_file():
            raise RuntimeError(f"diagnostic artifact is missing: {name}")
        entries.append(
            {"path": name, "size": path.stat().st_size, "sha256": sha256_file(path)}
        )
    return {
        "schema": "komorebi.neuralese.g1d.artifact_manifest.v1",
        "entry_count": len(entries),
        "entries": entries,
    }


def _report(static: dict[str, Any], dynamic: dict[str, Any] | None) -> str:
    accuracy = static["accuracy"]["test_iid"]
    deltas = static["iid_causal_deltas"]
    agreement = static["cross_mode_prediction_agreement"]["test_iid"]
    lines = [
        "# Komorebi Neuralese G1-D1 diagnostic report",
        "",
        "## Source result",
        "",
        f"- Source claim: `{static['source_run']['claim']}`",
        f"- Recurrent IID accuracy: {accuracy['recurrent']['overall']:.6f}",
        f"- Recurrent minus zero: {deltas['recurrent_minus_zero']:.6f}",
        f"- Recurrent minus shuffle: {deltas['recurrent_minus_shuffle']:.6f}",
        f"- Recurrent minus no-feedback: {deltas['recurrent_minus_no_feedback']:.6f}",
        f"- Recurrent/shuffle top-one agreement: {agreement['recurrent__shuffle']['agreement']:.4%}",
        f"- Recurrent/no-feedback top-one agreement: {agreement['recurrent__no_feedback']['agreement']:.4%}",
        f"- Generic steering signature: {static['generic_steering_signature']}",
        "",
    ]
    if dynamic is None:
        lines.extend(
            [
                "## Scope",
                "",
                "This was a static artifact analysis. Latent-state localization remains pending.",
            ]
        )
        return "\n".join(lines) + "\n"
    verdict = dynamic["verdict"]
    spectrum = dynamic["spectrum"]["matrices"]["output_projection.weight"]
    final_evidence = verdict["probe_evidence"]["final_workspace_state"]
    decoded_evidence = verdict["probe_evidence"]["final_decoded_injection"]
    transport = verdict["paired_incompatible_donor_semantic_transport"]
    lines.extend(
        [
            "## Checkpoint diagnosis",
            "",
            f"- Primary localization hypothesis: `{verdict['primary_diagnosis']}`",
            f"- Output projection top-one energy: {spectrum['top1_energy_fraction']:.4%}",
            f"- Output projection stable rank: {spectrum['stable_rank']:.6f}",
            f"- Source final-state probe: `{verdict['probe_evidence']['source_activation']['iid_signal_evidence']}`",
            f"- Initial workspace-state probe: `{verdict['probe_evidence']['initial_workspace_state']['iid_signal_evidence']}`",
            f"- Final workspace-state probe: `{final_evidence['iid_signal_evidence']}`",
            f"- Final decoded-injection probe: `{decoded_evidence['iid_signal_evidence']}`",
            f"- Final state IID/OOD balanced accuracy: {final_evidence['iid_balanced_accuracy']:.6f} / {final_evidence['ood_balanced_accuracy']:.6f}",
            f"- Final state IID/OOD lift over raw metadata: {final_evidence['iid_lift_over_raw_metadata']:.6f} / {final_evidence['ood_lift_over_raw_metadata']:.6f}",
            f"- Final no-feedback probe IID balanced accuracy: {verdict['no_feedback_probe_iid_balanced_accuracy']:.6f}",
            f"- Paired incompatible-donor semantic shift IID: {transport['iid']['mean_preference_shift']:.6f} (99% clustered interval {transport['iid']['clustered_99pct']})",
            f"- Rank-one projection agreement with full output: {verdict['rank1_projection_top1_agreement_with_full']:.4%}",
            "",
            "## Interpretation boundary",
            "",
            verdict["interpretation_boundary"],
            "",
            "This report is diagnostic-only. It does not alter the failed registered G1 scientific result.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    started = time.time()
    package_verification = verify_package_manifest(ROOT)
    from neuralese_g1.integrity import verify_package_manifest as verify_g1_package
    from neuralese_g1.results import verify_run_directory

    upstream_verification = verify_g1_package(VENDOR_ROOT)
    run_root = Path(args.run).resolve()
    output = Path(args.output).resolve()
    if not run_root.is_dir():
        raise FileNotFoundError(f"source run directory not found: {run_root}")
    if output == ROOT or ROOT in output.parents:
        raise RuntimeError("diagnostic output must be outside the immutable package")
    if _overlap(output, run_root):
        raise RuntimeError("diagnostic output must not overlap the source run")
    source_cross_file_verification = verify_run_directory(
        run_root, require_checkpoint_validation=False
    )
    fixed_source_verification = verify_fixed_source_identity(
        run_root, source_cross_file_verification
    )
    model_root = None if args.static_only else Path(str(args.model or "")).resolve()
    if not args.static_only:
        if not args.model or model_root is None or not model_root.is_dir():
            raise FileNotFoundError("a valid local model directory is required")
        if _overlap(output, model_root):
            raise RuntimeError("diagnostic output must not overlap the model directory")
    if output.exists():
        if not output.is_dir() or any(output.iterdir()):
            raise RuntimeError("diagnostic output already exists and is not empty")
    else:
        output.mkdir(parents=True, exist_ok=False)
    lock = acquire_lock(output / ".g1d.lock")
    try:
        input_hashes_before = directory_hashes(run_root)
        static = analyze_run_artifacts(run_root)
        atomic_json(output / "static_analysis.json", static)
        dynamic = None
        if not args.static_only:
            from g1d.dynamic import load_and_diagnose

            dynamic = load_and_diagnose(
                model_path=model_root,
                run_dir=run_root,
                static_analysis=static,
                progress=print,
            )
            atomic_json(output / "checkpoint_spectrum.json", dynamic["spectrum"])
            atomic_json(output / "state_geometry.json", dynamic["geometry"])
            atomic_json(output / "probe_results.json", dynamic["probes"])
            atomic_json(output / "recurrence_results.json", dynamic["recurrence"])
            atomic_json(output / "bridge_results.json", dynamic["intervention_summary"])
            atomic_json(output / "dynamic_replay.json", dynamic["replay"])
            atomic_json(output / "diagnostic_verdict.json", dynamic["verdict"])
            _atomic_jsonl(
                output / "intervention_predictions.jsonl",
                dynamic["intervention_records"],
            )
            _atomic_torch(output / "feature_bank.pt", dynamic["feature_bank"])
        atomic_text(output / "diagnostic_report.md", _report(static, dynamic))
        input_hashes_after = directory_hashes(run_root)
        if input_hashes_after != input_hashes_before:
            raise RuntimeError("source run bytes changed during diagnostics")
        preflight = {
            "schema": "komorebi.neuralese.g1d.preflight.v1",
            "status": "PASS",
            "scope": "STATIC_ONLY" if args.static_only else "FULL_DIAGNOSTIC",
            "claim": "DIAGNOSTIC_ONLY",
            "package": package_verification,
            "upstream_package": upstream_verification,
            "source_run_verification": (
                fixed_source_verification
                if dynamic is None
                else dynamic["fixed_source_verification"]
            ),
            "source_run": str(run_root),
            "source_run_hashes": input_hashes_before,
            "source_run_immutable": True,
            "model": None if dynamic is None else dynamic["model"],
            "diagnostic_selection": (
                None if dynamic is None else dynamic["selection"]
            ),
            "elapsed_seconds": time.time() - started,
        }
        atomic_json(output / "diagnostic_preflight.json", preflight)
        artifact_names = [
            "static_analysis.json",
            "diagnostic_report.md",
            "diagnostic_preflight.json",
        ]
        if dynamic is not None:
            artifact_names.extend(
                [
                    "checkpoint_spectrum.json",
                    "state_geometry.json",
                    "probe_results.json",
                    "recurrence_results.json",
                    "bridge_results.json",
                    "dynamic_replay.json",
                    "diagnostic_verdict.json",
                    "intervention_predictions.jsonl",
                    "feature_bank.pt",
                ]
            )
        manifest = _artifact_manifest(output, artifact_names)
        atomic_json(output / "artifact_manifest.json", manifest)
        verification = {
            "schema": "komorebi.neuralese.g1d.verification.v1",
            "status": "PASS",
            "claim": "DIAGNOSTIC_ONLY",
            "scope": preflight["scope"],
            "artifact_manifest_sha256": sha256_file(output / "artifact_manifest.json"),
            "artifact_count": manifest["entry_count"],
            "source_run_immutable": True,
            "dynamic_replay_exact": (
                None
                if dynamic is None
                else all(value["exact"] for value in dynamic["replay"].values())
            ),
        }
        atomic_json(output / "verification.json", verification)
        print(f"G1D_ARTIFACTS_WRITTEN scope={preflight['scope']}")
        if dynamic is not None:
            print(f"G1D_LOCALIZATION={dynamic['verdict']['primary_diagnosis']}")
            print(
                "G1D_FINAL_STATE_PROBE_IID="
                f"{dynamic['verdict']['final_state_probe_iid_balanced_accuracy']:.6f}"
            )
            print(
                "G1D_OUTPUT_PROJECTION_TOP1_ENERGY="
                f"{dynamic['verdict']['output_projection_top1_energy_fraction']:.6f}"
            )
        print(f"OUTPUT={output}")
    finally:
        release_lock(lock)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"G1D_STATUS=FAIL: {error}", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)
