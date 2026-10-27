from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence
import hashlib
import numpy as np

from .adapters.base import LatentReasonerAdapter
from .dataset import (
    deterministic_group_split,
    query_polarity_counterfactual,
    semantic_twin,
    validate_polarity_counterfactual,
    validate_semantic_twin,
)
from .donors import (
    build_different_answer_far_proof_plan,
    build_same_answer_far_proof_plan,
)
from .hashing import sha256_object
from .schemas import AuditConfig, TaskRecord
from .witness import proof_witness_matrix


@dataclass
class SemanticDataset:
    x: np.ndarray
    twin_x: np.ndarray
    future: np.ndarray
    intervention: np.ndarray
    answer: np.ndarray
    task_ids: list[str]
    group_ids: list[str]
    steps: np.ndarray
    records: list[TaskRecord]
    clean_traces: dict[str, np.ndarray]
    counterfactual_traces: dict[str, np.ndarray]
    clean_losses: dict[str, float]


@dataclass(frozen=True)
class CandidateBasis:
    method: str
    rank: int
    center: np.ndarray
    basis: np.ndarray


def _ensure_trace(trace: Any) -> np.ndarray:
    array = np.asarray(trace, dtype=np.float64)
    if array.ndim != 2 or array.shape[0] < 2:
        raise ValueError(f"Semantic escalation requires a [steps, hidden] trace with >=2 steps, got {array.shape}")
    if not np.isfinite(array).all():
        raise ValueError("Trace contains non-finite values")
    return array


def collect_semantic_dataset(
    adapter: LatentReasonerAdapter,
    records: Sequence[TaskRecord],
    config: AuditConfig,
) -> SemanticDataset:
    x_rows: list[np.ndarray] = []
    twin_rows: list[np.ndarray] = []
    future_rows: list[np.ndarray] = []
    intervention_rows: list[np.ndarray] = []
    answers: list[float] = []
    task_ids: list[str] = []
    group_ids: list[str] = []
    steps: list[int] = []
    clean_traces: dict[str, np.ndarray] = {}
    counterfactual_traces: dict[str, np.ndarray] = {}
    clean_losses: dict[str, float] = {}

    for record in records:
        clean_observation = adapter.capture(record)
        twin_record = semantic_twin(record, twin_index=17)
        validate_semantic_twin(record, twin_record)
        twin_observation = adapter.capture(twin_record)
        counterfactual_record = query_polarity_counterfactual(record, intervention_index=0)
        validate_polarity_counterfactual(record, counterfactual_record)
        counterfactual_observation = adapter.capture(counterfactual_record)

        clean = _ensure_trace(clean_observation.trace)
        twin = _ensure_trace(twin_observation.trace)
        counterfactual = _ensure_trace(counterfactual_observation.trace)
        if clean.shape != twin.shape or clean.shape != counterfactual.shape:
            raise ValueError(f"Trace shape mismatch for semantic orbit {record.task_id}")
        clean_traces[record.task_id] = clean
        counterfactual_traces[record.task_id] = counterfactual
        clean_losses[record.task_id] = float(clean_observation.answer_loss)
        label = 1.0 if record.answer.strip().lower() in {"true", "yes", "1"} else -1.0
        for step in range(clean.shape[0] - 1):
            x_rows.append(clean[step])
            twin_rows.append(twin[step])
            future_rows.append(clean[step + 1])
            intervention_rows.append(counterfactual[step] - clean[step])
            answers.append(label)
            task_ids.append(record.task_id)
            group_ids.append(record.group_id)
            steps.append(step)

    if not x_rows:
        raise ValueError("No semantic samples were collected")
    return SemanticDataset(
        x=np.stack(x_rows),
        twin_x=np.stack(twin_rows),
        future=np.stack(future_rows),
        intervention=np.stack(intervention_rows),
        answer=np.asarray(answers, dtype=np.float64),
        task_ids=task_ids,
        group_ids=group_ids,
        steps=np.asarray(steps, dtype=np.int64),
        records=list(records),
        clean_traces=clean_traces,
        counterfactual_traces=counterfactual_traces,
        clean_losses=clean_losses,
    )


def subset_dataset(dataset: SemanticDataset, record_ids: set[str]) -> SemanticDataset:
    mask = np.asarray([task_id in record_ids for task_id in dataset.task_ids], dtype=bool)
    records = [record for record in dataset.records if record.task_id in record_ids]
    return SemanticDataset(
        x=dataset.x[mask],
        twin_x=dataset.twin_x[mask],
        future=dataset.future[mask],
        intervention=dataset.intervention[mask],
        answer=dataset.answer[mask],
        task_ids=[task for task, keep in zip(dataset.task_ids, mask) if keep],
        group_ids=[group for group, keep in zip(dataset.group_ids, mask) if keep],
        steps=dataset.steps[mask],
        records=records,
        clean_traces={key: value for key, value in dataset.clean_traces.items() if key in record_ids},
        counterfactual_traces={key: value for key, value in dataset.counterfactual_traces.items() if key in record_ids},
        clean_losses={key: value for key, value in dataset.clean_losses.items() if key in record_ids},
    )


def _canonical_orthonormal(columns: np.ndarray, rank: int) -> np.ndarray:
    matrix = np.asarray(columns, dtype=np.float64)
    if matrix.ndim != 2:
        raise ValueError("Basis source must be a matrix")
    u, singular, _ = np.linalg.svd(matrix, full_matrices=False)
    basis = u[:, : min(rank, u.shape[1])].copy()
    if basis.shape[1] < rank:
        # Deterministic completion from the standard basis.
        candidates = np.eye(matrix.shape[0])
        for column in candidates.T:
            residual = column - basis @ (basis.T @ column) if basis.size else column
            norm = np.linalg.norm(residual)
            if norm > 1e-10:
                basis = np.column_stack([basis, residual / norm])
            if basis.shape[1] >= rank:
                break
    basis = basis[:, :rank]
    for index in range(basis.shape[1]):
        pivot = int(np.argmax(np.abs(basis[:, index])))
        if basis[pivot, index] < 0:
            basis[:, index] *= -1
    return basis


def _target_scale(target: np.ndarray) -> np.ndarray:
    target = np.asarray(target, dtype=np.float64)
    centered = target - target.mean(axis=0, keepdims=True)
    scale = float(np.sqrt(np.mean(centered**2)))
    return centered / max(scale, 1e-12)


def _answer_residual_future(dataset: SemanticDataset, ridge: float = 1e-6) -> np.ndarray:
    """Remove the future-state component predictable from final answer alone."""
    answer_x = dataset.answer.reshape(-1, 1)
    model = _ridge_fit(answer_x, dataset.future, ridge)
    return dataset.future - _ridge_predict(answer_x, model)


def _basis_source(method: str, x_centered: np.ndarray, dataset: SemanticDataset, seed: int) -> np.ndarray:
    if method == "pca":
        return x_centered.T
    if method == "answer_only":
        return x_centered.T @ dataset.answer.reshape(-1, 1)
    if method == "predictive":
        return x_centered.T @ _target_scale(_answer_residual_future(dataset))
    if method == "intervention":
        return x_centered.T @ _target_scale(dataset.intervention)
    if method == "joint":
        targets = np.concatenate(
            [
                _target_scale(_answer_residual_future(dataset)),
                _target_scale(dataset.intervention),
                _target_scale(dataset.answer.reshape(-1, 1)),
            ],
            axis=1,
        )
        return x_centered.T @ targets
    if method == "random":
        digest = hashlib.sha256(f"{seed}:semantic-random-basis".encode("utf-8")).digest()
        rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
        return rng.standard_normal((x_centered.shape[1], x_centered.shape[1]))
    if method == "full_state":
        return np.eye(x_centered.shape[1])
    raise ValueError(f"Unknown semantic candidate method: {method}")


def construct_candidate_bases(
    discovery: SemanticDataset,
    config: AuditConfig,
) -> list[CandidateBasis]:
    center = discovery.x.mean(axis=0)
    x_centered = discovery.x - center
    hidden = x_centered.shape[1]
    max_rank = min(config.semantic_thresholds.max_rank, hidden)
    candidates: list[CandidateBasis] = []
    for method in ("answer_only", "pca", "predictive", "intervention", "joint", "random"):
        source = _basis_source(method, x_centered, discovery, config.seed)
        ranks = [1] if method == "answer_only" else list(range(1, max_rank + 1))
        for rank in ranks:
            basis = _canonical_orthonormal(source, rank)
            candidates.append(CandidateBasis(method=method, rank=rank, center=center.copy(), basis=basis))
    candidates.append(
        CandidateBasis(
            method="full_state",
            rank=hidden,
            center=center.copy(),
            basis=np.eye(hidden, dtype=np.float64),
        )
    )
    return candidates


def _ridge_fit(x: np.ndarray, y: np.ndarray, ridge: float) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if y.ndim == 1:
        y = y[:, None]
    x_mean = x.mean(axis=0, keepdims=True)
    y_mean = y.mean(axis=0, keepdims=True)
    xc = x - x_mean
    yc = y - y_mean
    gram = xc.T @ xc + ridge * np.eye(xc.shape[1])
    weights = np.linalg.solve(gram, xc.T @ yc)
    intercept = y_mean - x_mean @ weights
    return weights, intercept.reshape(-1)


def _ridge_predict(x: np.ndarray, model: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    weights, intercept = model
    return np.asarray(x, dtype=np.float64) @ weights + intercept


def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    denominator = float(np.sum((y_true - y_true.mean(axis=0, keepdims=True)) ** 2))
    numerator = float(np.sum((y_true - y_pred) ** 2))
    if denominator <= 1e-12:
        return 1.0 if numerator <= 1e-12 else 0.0
    return 1.0 - numerator / denominator


def _project(dataset: SemanticDataset, candidate: CandidateBasis) -> tuple[np.ndarray, np.ndarray]:
    z = (dataset.x - candidate.center) @ candidate.basis
    twin_z = (dataset.twin_x - candidate.center) @ candidate.basis
    return z, twin_z


def fit_candidate_heads(
    candidate: CandidateBasis,
    training: SemanticDataset,
    ridge: float,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    z, _ = _project(training, candidate)
    answer_baseline = _ridge_fit(training.answer.reshape(-1, 1), training.future, ridge)
    future_residual = training.future - _ridge_predict(training.answer.reshape(-1, 1), answer_baseline)
    return {
        "future": _ridge_fit(z, training.future, ridge),
        "procedure_future": _ridge_fit(z, future_residual, ridge),
        "future_answer_baseline": answer_baseline,
        "intervention": _ridge_fit(z, training.intervention, ridge),
        "answer": _ridge_fit(z, training.answer, ridge),
    }


def evaluate_candidate(
    candidate: CandidateBasis,
    training: SemanticDataset,
    evaluation: SemanticDataset,
    config: AuditConfig,
) -> dict[str, Any]:
    ridge = config.semantic_thresholds.ridge
    heads = fit_candidate_heads(candidate, training, ridge)
    z, twin_z = _project(evaluation, candidate)
    future_r2 = _r2(evaluation.future, _ridge_predict(z, heads["future"]))
    evaluation_future_residual = evaluation.future - _ridge_predict(
        evaluation.answer.reshape(-1, 1), heads["future_answer_baseline"]
    )
    procedure_future_r2 = _r2(
        evaluation_future_residual,
        _ridge_predict(z, heads["procedure_future"]),
    )
    intervention_r2 = _r2(evaluation.intervention, _ridge_predict(z, heads["intervention"]))
    answer_score = _ridge_predict(z, heads["answer"]).reshape(-1)
    answer_accuracy = float(np.mean(np.sign(answer_score) == np.sign(evaluation.answer)))
    denominator = float(np.mean(np.linalg.norm(z, axis=1)))
    twin_drift = float(np.mean(np.linalg.norm(twin_z - z, axis=1)) / max(denominator, 1e-12))
    thresholds = config.semantic_thresholds
    eligible_rank = candidate.method != "full_state" and candidate.rank <= thresholds.max_rank
    gates = {
        "future": future_r2 >= thresholds.future_r2,
        "procedure_future": procedure_future_r2 >= thresholds.procedure_future_r2,
        "intervention": intervention_r2 >= thresholds.intervention_r2,
        "answer": answer_accuracy >= thresholds.answer_accuracy,
        "twin": twin_drift <= thresholds.twin_drift_max,
        "rank": eligible_rank,
    }
    normalized_margins = [
        future_r2 / max(thresholds.future_r2, 1e-12),
        procedure_future_r2 / max(thresholds.procedure_future_r2, 1e-12),
        intervention_r2 / max(thresholds.intervention_r2, 1e-12),
        answer_accuracy / max(thresholds.answer_accuracy, 1e-12),
        thresholds.twin_drift_max / max(twin_drift, 1e-12),
    ]
    return {
        "method": candidate.method,
        "rank": candidate.rank,
        "future_r2": float(future_r2),
        "procedure_future_r2": float(procedure_future_r2),
        "intervention_r2": float(intervention_r2),
        "answer_accuracy": answer_accuracy,
        "twin_drift": twin_drift,
        "gates": gates,
        "valid": all(gates.values()),
        "weakest_normalized_margin": float(min(normalized_margins)),
        "basis_sha256": sha256_object(np.round(candidate.basis, 12).tolist()),
    }


def select_candidate(
    candidates: Sequence[CandidateBasis],
    metrics: Sequence[Mapping[str, Any]],
) -> tuple[CandidateBasis | None, dict[str, Any] | None]:
    if len(candidates) != len(metrics):
        raise ValueError("candidate and metric lengths differ")
    valid = [
        (candidate, dict(metric))
        for candidate, metric in zip(candidates, metrics)
        if bool(metric["valid"])
    ]
    if not valid:
        return None, None
    method_order = {
        "predictive": 0,
        "intervention": 1,
        "joint": 2,
        "pca": 3,
        "answer_only": 4,
        "random": 5,
        "full_state": 6,
    }
    valid.sort(
        key=lambda item: (
            item[0].rank,
            -float(item[1]["weakest_normalized_margin"]),
            method_order.get(item[0].method, 99),
        )
    )
    return valid[0]


def _combine(first: SemanticDataset, second: SemanticDataset) -> SemanticDataset:
    records = {record.task_id: record for record in [*first.records, *second.records]}
    return SemanticDataset(
        x=np.concatenate([first.x, second.x], axis=0),
        twin_x=np.concatenate([first.twin_x, second.twin_x], axis=0),
        future=np.concatenate([first.future, second.future], axis=0),
        intervention=np.concatenate([first.intervention, second.intervention], axis=0),
        answer=np.concatenate([first.answer, second.answer], axis=0),
        task_ids=[*first.task_ids, *second.task_ids],
        group_ids=[*first.group_ids, *second.group_ids],
        steps=np.concatenate([first.steps, second.steps], axis=0),
        records=list(records.values()),
        clean_traces={**first.clean_traces, **second.clean_traces},
        counterfactual_traces={**first.counterfactual_traces, **second.counterfactual_traces},
        clean_losses={**first.clean_losses, **second.clean_losses},
    )


def _same_rank_control(
    method: str,
    rank: int,
    training: SemanticDataset,
    config: AuditConfig,
) -> CandidateBasis:
    center = training.x.mean(axis=0)
    source = _basis_source(method, training.x - center, training, config.seed + 911)
    return CandidateBasis(method=method, rank=rank, center=center, basis=_canonical_orthonormal(source, rank))


def _patch_trace(base: np.ndarray, donor: np.ndarray, basis: np.ndarray) -> np.ndarray:
    if base.shape != donor.shape:
        raise ValueError("Cannot patch traces with different shapes")
    projector = basis @ basis.T
    return base + (donor - base) @ projector


def evaluate_causal_patching(
    adapter: LatentReasonerAdapter,
    candidate: CandidateBasis,
    training: SemanticDataset,
    final: SemanticDataset,
    config: AuditConfig,
) -> dict[str, Any]:
    records = final.records
    if len(records) < 4:
        return {"available": False, "reason": "too_few_final_tasks"}
    by_id = {record.task_id: record for record in records}
    different = build_different_answer_far_proof_plan(records)
    same = build_same_answer_far_proof_plan(records)
    controls = {
        "pca": _same_rank_control("pca", candidate.rank, training, config),
        "random": _same_rank_control("random", candidate.rank, training, config),
        "answer_only": _same_rank_control("answer_only", min(1, candidate.rank), training, config),
    }
    rows: list[dict[str, Any]] = []
    for different_assignment, same_assignment in zip(different, same):
        recipient = by_id[different_assignment.recipient_id]
        base_trace = final.clean_traces[recipient.task_id]
        different_trace = final.clean_traces[different_assignment.donor_id]
        same_trace = final.clean_traces[same_assignment.donor_id]
        clean_loss = final.clean_losses[recipient.task_id]
        full_different = float(adapter.score_with_trace(recipient, different_trace).answer_loss - clean_loss)
        full_same = float(adapter.score_with_trace(recipient, same_trace).answer_loss - clean_loss)
        selected_different = float(
            adapter.score_with_trace(recipient, _patch_trace(base_trace, different_trace, candidate.basis)).answer_loss
            - clean_loss
        )
        selected_same = float(
            adapter.score_with_trace(recipient, _patch_trace(base_trace, same_trace, candidate.basis)).answer_loss
            - clean_loss
        )
        control_effects: dict[str, float] = {}
        for name, control in controls.items():
            control_effects[name] = float(
                adapter.score_with_trace(recipient, _patch_trace(base_trace, different_trace, control.basis)).answer_loss
                - clean_loss
            )
        rows.append(
            {
                "task_id": recipient.task_id,
                "different_donor_id": different_assignment.donor_id,
                "same_donor_id": same_assignment.donor_id,
                "full_different_effect": full_different,
                "full_same_effect": full_same,
                "selected_different_effect": selected_different,
                "selected_same_effect": selected_same,
                "controls": control_effects,
            }
        )
    full = np.asarray([row["full_different_effect"] for row in rows], dtype=np.float64)
    selected = np.asarray([row["selected_different_effect"] for row in rows], dtype=np.float64)
    valid = full > 1e-9
    recovery = float(np.mean(selected[valid]) / max(float(np.mean(full[valid])), 1e-12)) if np.any(valid) else 0.0
    positive_fraction = float(np.mean(selected > 0.0))
    control_means = {
        name: float(np.mean([row["controls"][name] for row in rows]))
        for name in controls
    }
    selected_mean = float(np.mean(selected))
    # PCA is retained as a descriptive control because it may genuinely contain
    # the semantic packet. The causal gate only requires superiority over the
    # answer-only and random equal-rank shortcuts.
    shortcut_control = max(
        control_means.get("random", float("-inf")),
        control_means.get("answer_only", float("-inf")),
    )
    thresholds = config.semantic_thresholds
    gates = {
        "recovery_ratio": recovery >= thresholds.patch_recovery_ratio,
        "positive_fraction": positive_fraction >= thresholds.patch_positive_fraction,
        "shortcut_control_advantage": selected_mean > shortcut_control,
    }
    return {
        "available": True,
        "selected_mean_effect": selected_mean,
        "full_mean_effect": float(np.mean(full)),
        "recovery_ratio": recovery,
        "positive_fraction": positive_fraction,
        "same_answer_selected_mean_effect": float(np.mean([row["selected_same_effect"] for row in rows])),
        "control_mean_effects": control_means,
        "gates": gates,
        "passed": all(gates.values()),
        "rows": rows,
    }


def run_semantic_escalation(
    adapter: LatentReasonerAdapter,
    records: Sequence[TaskRecord],
    config: AuditConfig,
) -> dict[str, Any]:
    thresholds = config.semantic_thresholds
    if len(records) < thresholds.minimum_tasks:
        return {
            "status": "SEMANTIC_ESCALATION_SKIPPED",
            "reason": "insufficient_tasks",
            "task_count": len(records),
            "minimum_tasks": thresholds.minimum_tasks,
        }
    chronology: list[str] = ["split_declared"]
    splits = deterministic_group_split(
        records,
        seed=config.seed,
        discovery_fraction=config.semantic_discovery_fraction,
        calibration_fraction=config.semantic_calibration_fraction,
    )
    split_receipt = {
        name: [record.task_id for record in split_records]
        for name, split_records in splits.items()
    }

    # Final-support trajectories are intentionally not computed before the quotient
    # and every construction threshold have been sealed.
    discovery = collect_semantic_dataset(adapter, splits["discovery"], config)
    chronology.append("discovery_captured")
    calibration = collect_semantic_dataset(adapter, splits["calibration"], config)
    chronology.append("calibration_captured")
    if discovery.x.shape[0] == 0 or calibration.x.shape[0] == 0 or not splits["final"]:
        return {"status": "SEMANTIC_ESCALATION_SKIPPED", "reason": "empty_split"}

    candidates = construct_candidate_bases(discovery, config)
    candidate_metrics = [evaluate_candidate(candidate, discovery, calibration, config) for candidate in candidates]
    selected, selected_metrics = select_candidate(candidates, candidate_metrics)
    chronology.append("candidate_selection_completed")
    if selected is None or selected_metrics is None:
        result = {
            "status": "ONTOLOGY_UNDERIDENTIFIED",
            "split_receipt": split_receipt,
            "candidate_metrics": candidate_metrics,
            "selected": None,
            "chronology": chronology,
            "final_support_captured": False,
        }
        return {**result, "semantic_result_sha256": sha256_object(result)}

    semantic_seal_payload = {
        "schema": "sric.real-lrm.semantic-quotient-seal.v1",
        "selected_method": selected.method,
        "selected_rank": selected.rank,
        "basis_sha256": sha256_object(np.round(selected.basis, 12).tolist()),
        "center_sha256": sha256_object(np.round(selected.center, 12).tolist()),
        "split_receipt": split_receipt,
        "thresholds": config.to_mapping()["semantic_thresholds"],
        "gold_proof_witness_excluded_from_construction": True,
    }
    semantic_seal = {**semantic_seal_payload, "seal_sha256": sha256_object(semantic_seal_payload)}
    chronology.append("semantic_quotient_sealed")

    final = collect_semantic_dataset(adapter, splits["final"], config)
    chronology.append("final_support_captured")
    training = _combine(discovery, calibration)
    final_metrics = evaluate_candidate(selected, training, final, config)
    # Audit-only proof witness is revealed after the quotient has been sealed.
    train_z, _ = _project(training, selected)
    final_z, _ = _project(final, selected)
    num_latents = int(next(iter(final.clean_traces.values())).shape[0])
    train_witness = proof_witness_matrix(training.records, num_latents=num_latents, seed=config.seed)
    final_witness = proof_witness_matrix(final.records, num_latents=num_latents, seed=config.seed)
    witness_model = _ridge_fit(train_z, train_witness, thresholds.ridge)
    proof_witness_r2 = _r2(final_witness, _ridge_predict(final_z, witness_model))
    proof_gate = proof_witness_r2 >= thresholds.proof_witness_r2

    patching = evaluate_causal_patching(adapter, selected, training, final, config)
    if proof_gate and patching.get("passed", False):
        status = "CAUSALLY_VALIDATED"
    elif proof_gate:
        status = "SEMANTICALLY_IDENTIFIED"
    else:
        status = "SEMANTIC_CANDIDATE"

    result = {
        "schema": "sric.real-lrm.semantic-escalation-result.v1",
        "status": status,
        "split_receipt": split_receipt,
        "candidate_metrics": candidate_metrics,
        "selected": {
            **dict(selected_metrics),
            "center": selected.center.tolist(),
            "basis": selected.basis.tolist(),
        },
        "semantic_seal": semantic_seal,
        "chronology": chronology + ["post_seal_witness_revealed", "causal_patching_completed"],
        "final_support_captured_before_seal": False,
        "final_construction_metrics": final_metrics,
        "post_seal_proof_witness": {
            "r2": float(proof_witness_r2),
            "threshold": thresholds.proof_witness_r2,
            "passed": proof_gate,
            "used_during_construction": False,
            "witness_scope": "answer, proof depth, recurrent progress, and audit-only proof-instance content",
            "algorithmic_procedure_claim": False,
        },
        "causal_patching": patching,
        "claim_boundary": {
            "word_for_word_thought_transcript": False,
            "unique_natural_language_semantics": False,
            "unrestricted_ontology_discovery": False,
        },
    }
    return {**result, "semantic_result_sha256": sha256_object(result)}
