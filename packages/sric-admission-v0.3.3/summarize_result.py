from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


def fmt(effect: Mapping[str, Any] | None) -> str:
    if effect is None:
        return "not run"
    interval = effect.get("interval_95")
    mean = effect.get("mean")
    if mean is None:
        return "not available"
    if not isinstance(interval, (list, tuple)) or len(interval) != 2:
        return f"{float(mean):.6f}"
    return f"{float(mean):.6f} [{float(interval[0]):.6f}, {float(interval[1]):.6f}]"


def _calibration_label(result: Mapping[str, Any]) -> str:
    calibration = result.get("causal_calibration")
    if not isinstance(calibration, Mapping):
        return "disabled / not run"
    task_ids = calibration.get("task_ids", [])
    return str(len(task_ids) if isinstance(task_ids, list) else 0)


def _accuracy_label(value: Any) -> str:
    return "not available" if value is None else f"{float(value):.6f}"


def render_summary(result: Mapping[str, Any]) -> str:
    causal_result = result.get("causal_admission")
    if not isinstance(causal_result, Mapping):
        raise ValueError("Result is missing causal_admission")
    causal = causal_result.get("summary")
    if not isinstance(causal, Mapping):
        raise ValueError("Result is missing causal_admission.summary")
    semantic_obj = result.get("semantic_escalation")
    semantic: Mapping[str, Any] = semantic_obj if isinstance(semantic_obj, Mapping) else {}
    config_obj = result.get("config")
    config: Mapping[str, Any] = config_obj if isinstance(config_obj, Mapping) else {}

    lines = [
        "# SRIC Block 24 External-LRM Result",
        "",
        f"- Overall status: **`{result.get('overall_status', 'UNKNOWN')}`**",
        f"- Causal admission: **`{causal.get('status', 'UNKNOWN')}`**",
        f"- Semantic escalation: **`{semantic.get('status', 'NOT_RECORDED')}`**",
        f"- Requested maximum tasks: {config.get('max_tasks', 'not recorded')}",
        f"- Audit tasks: {causal.get('task_count', 'not recorded')}",
        f"- Covariance calibration tasks: {_calibration_label(result)}",
        f"- Latent-mode generated accuracy: {_accuracy_label(causal.get('latent_accuracy'))}",
        f"- Replay maximum absolute logit error: {float(causal.get('replay_max_abs', float('nan'))):.9g}",
        f"- Necessity: {fmt(causal.get('necessity'))}",
        f"- Order: {fmt(causal.get('order'))}",
        f"- Norm-matched structure: {fmt(causal.get('norm_structure'))}",
        f"- Covariance-matched structure: {fmt(causal.get('covariance_structure'))}",
        f"- Same-answer {causal.get('specificity_claim', 'specificity')} transplant: {fmt(causal.get('procedure_transplant'))}",
        f"- Different-answer transplant: {fmt(causal.get('different_answer_transplant'))}",
        f"- Semantic-twin transplant: {fmt(causal.get('twin_transplant'))}",
        f"- Mean first near-clean latent step: {causal.get('mean_first_near_clean_step', 'not available')}",
        f"- Result receipt: `{result.get('result_sha256', 'not recorded')}`",
        "",
        "## Causal gates",
        "",
    ]
    gates_obj = causal.get("gates")
    gates: Mapping[str, Any] = gates_obj if isinstance(gates_obj, Mapping) else {}
    lines.extend(f"- {name}: {'PASS' if bool(value) else 'FAIL'}" for name, value in gates.items())

    status = str(causal.get("status", "UNKNOWN"))
    interpretation = {
        "ADAPTER_INVALID": "Exact replay failed; later causal interpretation is inadmissible.",
        "LATENT_UNUSED": "Replay passed, but the zero-latent intervention did not meet the frozen necessity gate on this audited population.",
        "LATENT_UNORDERED": "Latent computation met the necessity gate, but the declared recurrent order did not.",
        "LATENT_MAGNITUDE_ONLY": "The trace mattered, but matched corruptions did not establish sufficient dependence on latent structure.",
        "SURFACE_UNSTABLE": "A semantic-preserving surface twin changed the trace's functional effect beyond the frozen tolerance.",
        "LATENT_GENERIC": "The trace passed earlier gates but lacked sufficient same-answer content specificity.",
        "CONTENT_SPECIFIC": "The trace was tied to proof-instance content beyond final-answer identity.",
        "PROCEDURE_SPECIFIC": "The trace passed the configured procedure-specificity gate.",
    }.get(status)
    if interpretation:
        lines.extend(["", "## Status interpretation", "", interpretation])

    selected = semantic.get("selected")
    if isinstance(selected, Mapping):
        seal_obj = semantic.get("semantic_seal")
        seal: Mapping[str, Any] = seal_obj if isinstance(seal_obj, Mapping) else {}
        final_obj = semantic.get("final_construction_metrics")
        final: Mapping[str, Any] = final_obj if isinstance(final_obj, Mapping) else {}
        proof_obj = semantic.get("post_seal_proof_witness")
        proof: Mapping[str, Any] = proof_obj if isinstance(proof_obj, Mapping) else {}
        patch_obj = semantic.get("causal_patching")
        patch: Mapping[str, Any] = patch_obj if isinstance(patch_obj, Mapping) else {}
        lines.extend(
            [
                "",
                "## Semantic quotient",
                "",
                f"- Method: `{selected.get('method', 'not recorded')}`",
                f"- Rank: {selected.get('rank', 'not recorded')}",
                f"- Quotient seal: `{seal.get('seal_sha256', 'not recorded')}`",
                f"- Final future R2: {float(final.get('future_r2', float('nan'))):.6f}",
                f"- Final answer-residual future R2: {float(final.get('procedure_future_r2', float('nan'))):.6f}",
                f"- Final intervention R2: {float(final.get('intervention_r2', float('nan'))):.6f}",
                f"- Post-seal proof-witness R2: {float(proof.get('r2', float('nan'))):.6f}",
                f"- Causal patching passed: {patch.get('passed', 'not recorded')}",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    Path(args.output).write_text(render_summary(result), encoding="utf-8")
    print(f"SUMMARY_PATH={Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
