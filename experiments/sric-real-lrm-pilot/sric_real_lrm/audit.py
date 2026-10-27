from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping, Sequence
import numpy as np

from .adapters.base import LatentReasonerAdapter
from .dataset import semantic_twin, validate_semantic_twin
from .donors import DonorAssignment, build_same_answer_far_proof_plan, validate_donor_plan
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


def _max_logit_error(first: TraceObservation, second: TraceObservation) -> float:
    left = np.asarray(first.answer_logits, dtype=np.float64)
    right = np.asarray(second.answer_logits, dtype=np.float64)
    if left.shape != right.shape:
        return float("inf")
    return float(np.max(np.abs(left - right))) if left.size else 0.0


def _score(adapter: LatentReasonerAdapter, task: TaskRecord, trace: Any) -> TraceObservation:
    observation = adapter.score_with_trace(task, trace)
    if not np.isfinite(observation.answer_loss):
        raise ValueError(f"Non-finite answer loss for {task.task_id}")
    return observation


def classify(summary: Mapping[str, Any], config: AuditConfig) -> tuple[str, dict[str, bool]]:
    thresholds = config.thresholds
    replay = summary["replay_max_abs"] <= thresholds.replay_max_abs
    necessity = (
        summary["necessity"]["mean"] >= thresholds.necessity_mean
        and summary["necessity"]["positive_fraction"] >= thresholds.necessity_positive_fraction
    )
    ordered = summary["order"]["mean"] >= thresholds.order_mean
    structured = summary["structure"]["mean"] >= thresholds.structure_mean
    procedure = (
        summary["procedure_transplant"]["mean"] >= thresholds.procedure_mean
        and summary["procedure_transplant"]["positive_fraction"] >= thresholds.procedure_positive_fraction
    )
    twin_stable = (
        abs(summary["twin_transplant"]["mean"]) <= thresholds.twin_abs_mean_max
        and summary["twin_max_abs"] <= thresholds.twin_absolute_ceiling
    )
    gates = {
        "replay": replay,
        "necessity": necessity,
        "ordered": ordered,
        "structured": structured,
        "procedure_specific": procedure,
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
        status = "PROCEDURE_SPECIFIC"
    return status, gates


def run_causal_audit(
    adapter: LatentReasonerAdapter,
    records: Sequence[TaskRecord],
    config: AuditConfig,
    donor_plan: Sequence[DonorAssignment] | None = None,
) -> dict[str, Any]:
    if not records:
        raise ValueError("Audit requires at least one task")
    donor_plan = list(donor_plan or build_same_answer_far_proof_plan(records))
    validate_donor_plan(records, donor_plan)
    by_id = {record.task_id: record for record in records}
    donor_by_recipient = {assignment.recipient_id: assignment for assignment in donor_plan}

    clean: dict[str, TraceObservation] = {}
    twins: dict[str, TaskRecord] = {}
    twin_clean: dict[str, TraceObservation] = {}
    for record in records:
        clean[record.task_id] = adapter.capture(record)
        twin = semantic_twin(record, 0)
        validate_semantic_twin(record, twin)
        twins[record.task_id] = twin
        twin_clean[record.task_id] = adapter.capture(twin)

    covariance = None
    if config.covariance_noise:
        covariance = covariance_from_traces(np.asarray(observation.trace) for observation in clean.values())

    rows: list[dict[str, Any]] = []
    for record in records:
        ordinary = clean[record.task_id]
        trace = np.asarray(ordinary.trace, dtype=np.float64)
        assignment = donor_by_recipient[record.task_id]
        donor_trace = clean[assignment.donor_id].trace
        replay = _score(adapter, record, trace)
        zero = _score(adapter, record, zero_trace(trace))
        permuted = _score(adapter, record, permute_trace(trace, record.task_id, config.seed))
        if covariance is None:
            noise_trace = norm_matched_noise(trace, record.task_id, config.seed)
        else:
            noise_trace = covariance_matched_noise(trace, covariance, record.task_id, config.seed)
        noise = _score(adapter, record, noise_trace)
        donor = _score(adapter, record, donor_trace)
        twin = _score(adapter, record, twin_clean[record.task_id].trace)

        truncation_losses: list[float] = []
        if config.truncation:
            truncation_losses = [
                _score(adapter, record, truncate_trace(trace, retained)).answer_loss
                for retained in range(trace.shape[0] + 1)
            ]

        row = {
            "task_id": record.task_id,
            "group_id": record.group_id,
            "orbit_id": record.orbit_id,
            "answer": record.answer,
            "proof_depth": record.proof_depth,
            "donor_id": assignment.donor_id,
            "donor_signature_distance": assignment.signature_distance,
            "clean_loss": ordinary.answer_loss,
            "replay_loss": replay.answer_loss,
            "zero_loss": zero.answer_loss,
            "permuted_loss": permuted.answer_loss,
            "noise_loss": noise.answer_loss,
            "procedure_donor_loss": donor.answer_loss,
            "twin_donor_loss": twin.answer_loss,
            "replay_max_abs": _max_logit_error(ordinary, replay),
            "necessity_effect": zero.answer_loss - ordinary.answer_loss,
            "order_effect": permuted.answer_loss - ordinary.answer_loss,
            "structure_effect": noise.answer_loss - ordinary.answer_loss,
            "procedure_transplant_effect": donor.answer_loss - ordinary.answer_loss,
            "twin_transplant_effect": twin.answer_loss - ordinary.answer_loss,
            "truncation_losses": truncation_losses,
            "predicted_answer": ordinary.predicted_answer,
        }
        rows.append(row)

    summary: dict[str, Any] = {
        "task_count": len(rows),
        "replay_max_abs": max(float(row["replay_max_abs"]) for row in rows),
        "replay_loss_max_abs": max(abs(float(row["replay_loss"]) - float(row["clean_loss"])) for row in rows),
        "twin_max_abs": max(abs(float(row["twin_transplant_effect"])) for row in rows),
        "necessity": summarize_effect(rows, "necessity_effect", replicates=config.bootstrap_replicates, seed=config.seed + 1),
        "order": summarize_effect(rows, "order_effect", replicates=config.bootstrap_replicates, seed=config.seed + 2),
        "structure": summarize_effect(rows, "structure_effect", replicates=config.bootstrap_replicates, seed=config.seed + 3),
        "procedure_transplant": summarize_effect(
            rows, "procedure_transplant_effect", replicates=config.bootstrap_replicates, seed=config.seed + 4
        ),
        "twin_transplant": summarize_effect(
            rows, "twin_transplant_effect", replicates=config.bootstrap_replicates, seed=config.seed + 5
        ),
    }
    status, gates = classify(summary, config)
    summary["status"] = status
    summary["gates"] = gates

    result_without_digest = {
        "schema": "sric.real-lrm.causal-audit-result.v1",
        "claim_level": "adapter-and-procedure-specificity-audit",
        "adapter": dict(adapter.model_fingerprint()),
        "config": config.to_mapping(),
        "donor_plan": [asdict(item) for item in donor_plan],
        "summary": summary,
        "rows": rows,
        "claim_boundary": {
            "real_model_semantics_established": False,
            "endogenous_ontology_established": False,
            "word_for_word_thought_transcript": False,
        },
    }
    return {**result_without_digest, "result_sha256": sha256_object(result_without_digest)}
