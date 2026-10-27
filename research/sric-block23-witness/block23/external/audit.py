from __future__ import annotations

import dataclasses
from typing import Iterable

import numpy as np

from .interventions import norm_matched_noise, permute_trace, truncate_trace, zero_trace
from .protocol import LatentReasonerAdapter, PilotTask


@dataclasses.dataclass(frozen=True)
class CausalAuditConfig:
    replay_tolerance: float = 1e-6
    permutation: tuple[int, ...] | None = None
    noise_seed: int = 23023


def run_causal_audit(
    adapter: LatentReasonerAdapter,
    tasks: list[PilotTask],
    *,
    donors: dict[str, str] | None = None,
    twins: dict[str, PilotTask] | None = None,
    config: CausalAuditConfig = CausalAuditConfig(),
) -> list[dict]:
    by_id = {t.task_id: t for t in tasks}
    native = {t.task_id: adapter.capture(t) for t in tasks}
    records: list[dict] = []
    for idx, task in enumerate(tasks):
        base = native[task.task_id]
        k = len(base.trace)
        permutation = config.permutation or tuple(reversed(range(k)))
        replay = adapter.evaluate_trace(task, base.trace.copy())
        zero = adapter.evaluate_trace(task, zero_trace(base.trace))
        perm = adapter.evaluate_trace(task, permute_trace(base.trace, permutation))
        noise = adapter.evaluate_trace(task, norm_matched_noise(base.trace, config.noise_seed + idx))
        trunc = [adapter.evaluate_trace(task, truncate_trace(base.trace, keep)).answer_loss for keep in range(k + 1)]
        row = {
            "task_id": task.task_id,
            "ordinary_loss": base.answer_loss,
            "ordinary_score": base.answer_score,
            "replay_loss": replay.answer_loss,
            "replay_error": abs(replay.answer_loss - base.answer_loss),
            "zero_cost": zero.answer_loss - base.answer_loss,
            "permutation_cost": perm.answer_loss - base.answer_loss,
            "noise_cost": noise.answer_loss - base.answer_loss,
            "truncation_losses": trunc,
            "answer": task.answer,
            "proof_depth": int(task.metadata.get("proof_depth", len(task.proof_steps))),
        }
        if donors and task.task_id in donors:
            donor_id = donors[task.task_id]
            donor = native[donor_id]
            transplanted = adapter.evaluate_trace(task, donor.trace)
            row.update({
                "donor_task_id": donor_id,
                "same_answer_program_cost": transplanted.answer_loss - base.answer_loss,
            })
        if twins and task.task_id in twins:
            twin = twins[task.task_id]
            twin_native = adapter.capture(twin)
            twin_transplant = adapter.evaluate_trace(task, twin_native.trace)
            row["semantic_twin_cost"] = twin_transplant.answer_loss - base.answer_loss
        records.append(row)
    return records


def summarize_causal_audit(records: Iterable[dict]) -> dict:
    rows = list(records)
    def mean(key: str) -> float | None:
        vals = [float(r[key]) for r in rows if key in r]
        return float(np.mean(vals)) if vals else None
    return {
        "tasks": len(rows),
        "mean_replay_error": mean("replay_error"),
        "max_replay_error": max((float(r["replay_error"]) for r in rows), default=None),
        "mean_zero_cost": mean("zero_cost"),
        "mean_permutation_cost": mean("permutation_cost"),
        "mean_noise_cost": mean("noise_cost"),
        "mean_same_answer_program_cost": mean("same_answer_program_cost"),
        "mean_semantic_twin_cost": mean("semantic_twin_cost"),
        "positive_program_fraction": float(np.mean([r["same_answer_program_cost"] > 0 for r in rows if "same_answer_program_cost" in r])) if any("same_answer_program_cost" in r for r in rows) else None,
    }
