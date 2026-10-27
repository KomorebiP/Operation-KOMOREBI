from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping, Sequence
import numpy as np

from .adapters.base import LatentReasonerAdapter, UnsupportedAdapterOperation
from .dataset import semantic_twin, validate_semantic_twin
from .donors import (
    DonorAssignment,
    build_different_answer_far_proof_plan,
    build_same_answer_far_proof_plan,
    validate_donor_plan,
)
from .hashing import sha256_object
from .interventions import (
    covariance_matched_noise,
    norm_matched_noise,
    permute_trace,
    truncate_trace,
    zero_trace,
)
from .metrics import covariance_from_traces, summarize_effect
from .schemas import AuditConfig, TaskRecord, TraceObservation
from .validation import validated_adapter, finite_array, AdapterValidationError


def _max_logit_error(first: TraceObservation, second: TraceObservation) -> float:
    left = finite_array(first.answer_logits, "clean answer logits")
    right = finite_array(second.answer_logits, "replayed answer logits")
    if left.shape != right.shape:
        return float("inf")
    return float(np.max(np.abs(left - right))) if left.size else 0.0


def _score(adapter: LatentReasonerAdapter, task: TaskRecord, trace: Any) -> TraceObservation:
    observation = adapter.score_with_trace(task, trace)
    if not np.isfinite(observation.answer_loss):
        raise ValueError(f"Non-finite answer loss for {task.task_id}")
    return observation


def _accuracy(observations: Sequence[tuple[TaskRecord, TraceObservation]]) -> float | None:
    usable = [
        (task, observation)
        for task, observation in observations
        if observation.predicted_answer is not None
    ]
    if not usable:
        return None
    return float(
        np.mean(
            [
                observation.predicted_answer.strip().lower() == task.answer.strip().lower()
                for task, observation in usable
            ]
        )
    )


def classify(summary: Mapping[str, Any], config: AuditConfig) -> tuple[str, dict[str, bool]]:
    thresholds = config.thresholds
    replay = summary["replay_max_abs"] <= thresholds.replay_max_abs
    necessity = (
        summary["necessity"]["mean"] >= thresholds.necessity_mean
        and summary["necessity"]["positive_fraction"] >= thresholds.necessity_positive_fraction
    )
    ordered = summary["order"]["mean"] >= thresholds.order_mean
    norm_structured = summary["norm_structure"]["mean"] >= thresholds.structure_mean
    covariance_structured = (
        True
        if summary.get("covariance_structure") is None
        else summary["covariance_structure"]["mean"] >= thresholds.covariance_structure_mean
    )
    structured = norm_structured and covariance_structured
    procedure = (
        summary["procedure_transplant"]["mean"] >= thresholds.procedure_mean
        and summary["procedure_transplant"]["positive_fraction"] >= thresholds.procedure_positive_fraction
    )
    twin_stable = (
        abs(summary["twin_transplant"]["mean"]) <= thresholds.twin_abs_mean_max
        and summary["twin_max_abs"] <= thresholds.twin_absolute_ceiling
    )
    specificity_label = f"{config.specificity_claim}_specific"
    gates = {
        "replay": replay,
        "necessity": necessity,
        "ordered": ordered,
        "norm_structured": norm_structured,
        "covariance_structured": covariance_structured,
        "specificity": procedure,
        specificity_label: procedure,
        "semantic_twin_stable": twin_stable,
    }
    if not replay:
        status = "ADAPTER_INVALID"
    elif not necessity:
        status = "LATENT_UNUSED"
    elif not ordered:
        status = "LATENT_UNORDERED"
    elif not structured:
        status = "LATENT_MAGNITUDE_ONLY"
    elif not twin_stable:
        status = "SURFACE_UNSTABLE"
    elif not procedure:
        status = "LATENT_GENERIC"
    else:
        status = "PROCEDURE_SPECIFIC" if config.specificity_claim == "procedure" else "CONTENT_SPECIFIC"
    return status, gates


def run_causal_audit(
    adapter: LatentReasonerAdapter,
    records: Sequence[TaskRecord],
    config: AuditConfig,
    donor_plan: Sequence[DonorAssignment] | None = None,
    different_answer_plan: Sequence[DonorAssignment] | None = None,
    covariance_reference: np.ndarray | None = None,
    covariance_reference_receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    adapter = validated_adapter(adapter, config)
    if not records:
        raise ValueError("Audit requires at least one task")
    donor_plan = list(donor_plan or build_same_answer_far_proof_plan(records))
    different_answer_plan = list(different_answer_plan or build_different_answer_far_proof_plan(records))
    validate_donor_plan(records, donor_plan, expected_relation="same")
    validate_donor_plan(records, different_answer_plan, expected_relation="different")
    by_id = {record.task_id: record for record in records}
    donor_by_recipient = {assignment.recipient_id: assignment for assignment in donor_plan}
    different_by_recipient = {assignment.recipient_id: assignment for assignment in different_answer_plan}

    clean: dict[str, TraceObservation] = {}
    twins: dict[str, TaskRecord] = {}
    twin_clean: dict[str, TraceObservation] = {}
    for record in records:
        clean[record.task_id] = adapter.capture(record)
        twin = semantic_twin(record, 0)
        validate_semantic_twin(record, twin)
        twins[record.task_id] = twin
        twin_clean[record.task_id] = adapter.capture(twin)

    if config.run_covariance_noise:
        covariance = (
            np.asarray(covariance_reference, dtype=np.float64)
            if covariance_reference is not None
            else covariance_from_traces(
                np.asarray(observation.trace, dtype=np.float64) for observation in clean.values()
            )
        )
        covariance_source = "calibration_support" if covariance_reference is not None else "audit_support_fallback"
    else:
        covariance = None
        covariance_source = "disabled"

    rows: list[dict[str, Any]] = []
    for record in records:
        ordinary = clean[record.task_id]
        trace = np.asarray(ordinary.trace, dtype=np.float64)
        assignment = donor_by_recipient[record.task_id]
        different_assignment = different_by_recipient[record.task_id]
        donor_trace = clean[assignment.donor_id].trace
        different_trace = clean[different_assignment.donor_id].trace
        replay = _score(adapter, record, trace)
        zero = _score(adapter, record, zero_trace(trace))
        permuted = _score(adapter, record, permute_trace(trace, record.task_id, config.seed))
        norm_noise = _score(adapter, record, norm_matched_noise(trace, record.task_id, config.seed))
        covariance_noise = None
        if covariance is not None:
            covariance_noise = _score(
                adapter,
                record,
                covariance_matched_noise(trace, covariance, record.task_id, config.seed),
            )
        donor = _score(adapter, record, donor_trace)
        different_donor = _score(adapter, record, different_trace)
        twin = _score(adapter, record, twin_clean[record.task_id].trace)

        truncation_losses: list[float] = []
        first_near_clean_step: int | None = None
        if config.truncation:
            truncation_losses = [
                _score(adapter, record, truncate_trace(trace, retained)).answer_loss
                for retained in range(trace.shape[0] + 1)
            ]
            tolerance = max(0.005, 0.05 * abs(float(ordinary.answer_loss)))
            for retained, loss in enumerate(truncation_losses):
                if loss <= float(ordinary.answer_loss) + tolerance:
                    first_near_clean_step = retained
                    break

        row = {
            "task_id": record.task_id,
            "group_id": record.group_id,
            "orbit_id": record.orbit_id,
            "answer": record.answer,
            "proof_depth": record.proof_depth,
            "donor_id": assignment.donor_id,
            "different_answer_donor_id": different_assignment.donor_id,
            "donor_signature_distance": assignment.signature_distance,
            "different_donor_signature_distance": different_assignment.signature_distance,
            "clean_loss": ordinary.answer_loss,
            "replay_loss": replay.answer_loss,
            "zero_loss": zero.answer_loss,
            "permuted_loss": permuted.answer_loss,
            "norm_noise_loss": norm_noise.answer_loss,
            "covariance_noise_loss": None if covariance_noise is None else covariance_noise.answer_loss,
            "procedure_donor_loss": donor.answer_loss,
            "different_answer_donor_loss": different_donor.answer_loss,
            "twin_donor_loss": twin.answer_loss,
            "replay_max_abs": _max_logit_error(ordinary, replay),
            "necessity_effect": zero.answer_loss - ordinary.answer_loss,
            "order_effect": permuted.answer_loss - ordinary.answer_loss,
            "norm_structure_effect": norm_noise.answer_loss - ordinary.answer_loss,
            "covariance_structure_effect": None if covariance_noise is None else covariance_noise.answer_loss - ordinary.answer_loss,
            "procedure_transplant_effect": donor.answer_loss - ordinary.answer_loss,
            "different_answer_transplant_effect": different_donor.answer_loss - ordinary.answer_loss,
            "twin_transplant_effect": twin.answer_loss - ordinary.answer_loss,
            "truncation_losses": truncation_losses,
            "first_near_clean_step": first_near_clean_step,
            "predicted_answer": ordinary.predicted_answer,
            "generated_correct": ordinary.generated_correct,
        }
        rows.append(row)

    if not all(np.isfinite(row["replay_max_abs"]) for row in rows):
        raise AdapterValidationError("Every replay error must be finite before aggregation")

    summary: dict[str, Any] = {
        "task_count": len(rows),
        "specificity_claim": config.specificity_claim,
        "covariance_source": covariance_source,
        "covariance_reference_receipt": None if covariance_reference_receipt is None else dict(covariance_reference_receipt),
        "replay_max_abs": max(float(row["replay_max_abs"]) for row in rows),
        "replay_loss_max_abs": max(abs(float(row["replay_loss"]) - float(row["clean_loss"])) for row in rows),
        "twin_max_abs": max(abs(float(row["twin_transplant_effect"])) for row in rows),
        "latent_accuracy": _accuracy([(record, clean[record.task_id]) for record in records]),
        "necessity": summarize_effect(rows, "necessity_effect", replicates=config.bootstrap_replicates, seed=config.seed + 1),
        "order": summarize_effect(rows, "order_effect", replicates=config.bootstrap_replicates, seed=config.seed + 2),
        "norm_structure": summarize_effect(rows, "norm_structure_effect", replicates=config.bootstrap_replicates, seed=config.seed + 3),
        "covariance_structure": None,
        "procedure_transplant": summarize_effect(
            rows, "procedure_transplant_effect", replicates=config.bootstrap_replicates, seed=config.seed + 4
        ),
        "different_answer_transplant": summarize_effect(
            rows, "different_answer_transplant_effect", replicates=config.bootstrap_replicates, seed=config.seed + 5
        ),
        "twin_transplant": summarize_effect(
            rows, "twin_transplant_effect", replicates=config.bootstrap_replicates, seed=config.seed + 6
        ),
        "mean_first_near_clean_step": None,
    }
    summary["specificity_transplant"] = dict(summary["procedure_transplant"])
    if covariance is not None:
        summary["covariance_structure"] = summarize_effect(
            rows,
            "covariance_structure_effect",
            replicates=config.bootstrap_replicates,
            seed=config.seed + 7,
        )
    retained = [row["first_near_clean_step"] for row in rows if row["first_near_clean_step"] is not None]
    if retained:
        summary["mean_first_near_clean_step"] = float(np.mean(retained))

    mode_controls: dict[str, Any] = {}
    if config.run_mode_controls:
        # Explicit CoT uses the gold proof steps and is therefore reserved as a
        # post-seal witness. Only the direct-answer control is admissible here.
        for mode in ("direct",):
            if not adapter.supports_mode(mode):
                mode_controls[mode] = {"available": False}
                continue
            observations: list[tuple[TaskRecord, TraceObservation]] = []
            losses: list[float] = []
            try:
                for record in records:
                    observation = adapter.capture_mode(record, mode)
                    observations.append((record, observation))
                    losses.append(float(observation.answer_loss))
                mode_controls[mode] = {
                    "available": True,
                    "mean_answer_loss": float(np.mean(losses)),
                    "accuracy": _accuracy(observations),
                }
            except UnsupportedAdapterOperation:
                mode_controls[mode] = {"available": False}
        mode_controls["verbalized"] = {
            "available": False,
            "reason": "reserved_for_post_seal_witness",
            "used_before_semantic_seal": False,
        }
    summary["mode_controls"] = mode_controls

    status, gates = classify(summary, config)
    summary["status"] = status
    summary["gates"] = gates

    result_without_digest = {
        "schema": "sric.real-lrm.causal-audit-result.v2",
        "claim_level": "external-latent-causal-admission",
        "adapter": dict(adapter.model_fingerprint()),
        "config": config.to_mapping(),
        "same_answer_donor_plan": [asdict(item) for item in donor_plan],
        "different_answer_donor_plan": [asdict(item) for item in different_answer_plan],
        "summary": summary,
        "rows": rows,
        "claim_boundary": {
            "real_model_semantics_established": False,
            "specificity_claim": config.specificity_claim,
            "prontoqa_procedure_algorithm_claim": False,
            "endogenous_ontology_established": False,
            "word_for_word_thought_transcript": False,
        },
    }
    return {**result_without_digest, "result_sha256": sha256_object(result_without_digest)}
