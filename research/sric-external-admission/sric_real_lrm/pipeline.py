from __future__ import annotations

from typing import Any, Sequence
import numpy as np

from .adapters.base import LatentReasonerAdapter, UnsupportedAdapterOperation
from .audit import run_causal_audit
from .dataset import deterministic_calibration_audit_split
from .metrics import covariance_from_traces
from .hashing import sha256_object
from .schemas import AuditConfig, TaskRecord
from .semantic import run_semantic_escalation


CAUSAL_TERMINAL = {
    "ADAPTER_INVALID",
    "LATENT_UNUSED",
    "LATENT_UNORDERED",
    "LATENT_MAGNITUDE_ONLY",
    "SURFACE_UNSTABLE",
    "LATENT_GENERIC",
}



def _post_seal_explicit_cot_witness(
    adapter: LatentReasonerAdapter,
    records: Sequence[TaskRecord],
) -> dict[str, Any]:
    """Evaluate explicit-CoT mode only after the semantic quotient is sealed."""
    if not adapter.supports_mode("verbalized"):
        return {"available": False, "reason": "adapter_unsupported", "used_during_construction": False}
    losses: list[float] = []
    correctness: list[bool] = []
    try:
        for record in records:
            observation = adapter.generate_mode(record, "verbalized")
            losses.append(float(observation.answer_loss))
            if observation.predicted_answer is not None:
                correctness.append(
                    observation.predicted_answer.strip().lower() == record.answer.strip().lower()
                )
    except UnsupportedAdapterOperation:
        return {"available": False, "reason": "adapter_unsupported", "used_during_construction": False}
    return {
        "available": True,
        "task_count": len(losses),
        "mean_answer_loss": float(np.mean(losses)) if losses else None,
        "accuracy": float(np.mean(correctness)) if correctness else None,
        "used_during_construction": False,
        "role": "post_seal_comparison_witness_only",
    }

def run_block24_pipeline(
    adapter: LatentReasonerAdapter,
    records: Sequence[TaskRecord],
    config: AuditConfig,
) -> dict[str, Any]:
    """Run causal admission and conditionally escalate to semantic construction.

    Covariance-matched corruption is calibrated on a deterministic group-disjoint
    support before the causal audit. The semantic constructor receives only the
    causal-audit support.
    """
    causal_records = list(records)
    covariance_reference = None
    covariance_receipt: dict[str, Any] | None = None
    if config.run_covariance_noise:
        causal_split = deterministic_calibration_audit_split(
            records,
            seed=config.seed,
            calibration_fraction=config.causal_calibration_fraction,
        )
        calibration_records = causal_split["calibration"]
        causal_records = causal_split["audit"]
        calibration_traces = [adapter.capture(record).trace for record in calibration_records]
        covariance_reference = covariance_from_traces(calibration_traces)
        covariance_receipt = {
            "schema": "sric.real-lrm.covariance-calibration-receipt.v1",
            "task_ids": [record.task_id for record in calibration_records],
            "task_ids_sha256": sha256_object([record.task_id for record in calibration_records]),
            "group_ids": sorted({record.group_id for record in calibration_records}),
            "covariance_sha256": sha256_object(np.round(covariance_reference, 12).tolist()),
            "final_audit_excluded": True,
        }
    causal = run_causal_audit(
        adapter,
        causal_records,
        config,
        covariance_reference=covariance_reference,
        covariance_reference_receipt=covariance_receipt,
    )
    causal_status = str(causal["summary"]["status"])
    if causal_status not in {"CONTENT_SPECIFIC", "PROCEDURE_SPECIFIC"}:
        semantic: dict[str, Any] = {
            "status": "SEMANTIC_ESCALATION_NOT_ADMISSIBLE",
            "reason": causal_status,
        }
        overall = causal_status
    elif not config.semantic_escalation:
        semantic = {
            "status": "SEMANTIC_ESCALATION_DISABLED",
            "reason": "configuration",
        }
        overall = causal_status
    else:
        semantic = run_semantic_escalation(adapter, causal_records, config)
        if semantic.get("semantic_seal") is not None:
            semantic["post_seal_explicit_cot_witness"] = _post_seal_explicit_cot_witness(
                adapter, causal_records
            )
            if isinstance(semantic.get("chronology"), list):
                semantic["chronology"].append("explicit_cot_witness_revealed")
        else:
            semantic["post_seal_explicit_cot_witness"] = {
                "available": False,
                "reason": "no_semantic_quotient_seal",
                "used_during_construction": False,
            }
        semantic_status = str(semantic["status"])
        overall = causal_status if semantic_status.startswith("SEMANTIC_ESCALATION_") else semantic_status

    payload = {
        "schema": "sric.block24.external-lrm-causal-semantic-admission-result.v1",
        "overall_status": overall,
        "adapter": dict(adapter.model_fingerprint()),
        "config": config.to_mapping(),
        "causal_calibration": covariance_receipt,
        "causal_admission": causal,
        "semantic_escalation": semantic,
        "claim_boundary": {
            "real_checkpoint_evidence": not bool(adapter.model_fingerprint().get("engineered_positive_control", False)),
            "maximum_possible_status": "CAUSALLY_VALIDATED",
            "causal_specificity_tier": config.specificity_claim,
            "word_for_word_hidden_thought_transcript": False,
            "open_ended_recursive_self_improvement": False,
        },
    }
    return {**payload, "result_sha256": sha256_object(payload)}
