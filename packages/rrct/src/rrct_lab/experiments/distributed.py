from __future__ import annotations

from typing import Any

import numpy as np

from rrct_lab.experiments.common import cfg, enabled
from rrct_lab.results import ExperimentResult
from rrct_lab.utils import (
    accuracy,
    nearest_centroid_fit,
    nearest_centroid_predict,
    orthogonal_matrix,
    r2_score,
    seed_everything,
)


def _contrast3(values: np.ndarray) -> np.ndarray:
    table = np.asarray(
        [
            [1.0, 0.0],
            [-0.5, np.sqrt(3.0) / 2.0],
            [-0.5, -np.sqrt(3.0) / 2.0],
        ]
    )
    return table[values]


def _cca(x: np.ndarray, y: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x0 = x - x.mean(axis=0, keepdims=True)
    y0 = y - y.mean(axis=0, keepdims=True)
    n = max(1, len(x0) - 1)
    cxx = x0.T @ x0 / n + 1e-6 * np.eye(x0.shape[1])
    cyy = y0.T @ y0 / n + 1e-6 * np.eye(y0.shape[1])
    cxy = x0.T @ y0 / n
    ex, vx = np.linalg.eigh(cxx)
    ey, vy = np.linalg.eigh(cyy)
    wx = vx @ np.diag(1.0 / np.sqrt(np.clip(ex, 1e-8, None))) @ vx.T
    wy = vy @ np.diag(1.0 / np.sqrt(np.clip(ey, 1e-8, None))) @ vy.T
    u, s, vt = np.linalg.svd(wx @ cxy @ wy, full_matrices=False)
    ax = wx @ u[:, :rank]
    by = wy @ vt.T[:, :rank]
    return ax, by, s[:rank]


def _procrustes(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    u, _, vt = np.linalg.svd(source.T @ target, full_matrices=False)
    return u @ vt


def run(config: dict[str, Any]) -> ExperimentResult:
    seed = int(cfg(config, "run.seed", 580001))
    rng = seed_everything(seed, bool(cfg(config, "run.deterministic", True)))
    n_cal = int(cfg(config, "experiment.calibration_episodes", 256))
    n_eval = int(cfg(config, "experiment.holdout_episodes", 512))
    total = n_cal + n_eval
    state_dim = max(12, int(cfg(config, "experiment.state_dim", 32)))
    private_dim = min(4, max(2, int(cfg(config, "interaction.private_state_dimension", 4))))
    factor_a = rng.integers(0, 3, total)
    factor_b = rng.integers(0, 3, total)
    private_a = rng.integers(0, 4, total)
    private_b = rng.integers(0, 4, total)
    task_target = 3 * factor_a + factor_b
    communication = enabled(config, "communication")
    distributed = enabled(config, "distributed_workspace", "workspace_cut")
    alignment = enabled(config, "coordinate_alignment")
    pair_memory = enabled(config, "pair_memory", "memory_cut")
    recurrence = enabled(config, "recurrence", "recurrence_cut")
    planner = enabled(config, "planner_binding", "planner_binding_cut")
    bidirectional = bool(cfg(config, "workspace.bidirectional", True)) and not bool(
        cfg(config, "interventions.one_way", False)
    )
    if bool(cfg(config, "interventions.message_shuffle", False)):
        factor_b_seen_a = rng.permutation(factor_b)
        factor_a_seen_b = rng.permutation(factor_a)
    elif communication:
        factor_b_seen_a = factor_b.copy()
        factor_a_seen_b = factor_a.copy()
    else:
        factor_b_seen_a = np.zeros_like(factor_b)
        factor_a_seen_b = np.zeros_like(factor_a)

    shared_a = np.concatenate((_contrast3(factor_a), _contrast3(factor_b_seen_a)), axis=1)
    shared_b = np.concatenate((_contrast3(factor_a_seen_b), _contrast3(factor_b)), axis=1)
    private_table = np.eye(4)
    pa = private_table[private_a][:, :private_dim]
    pb = private_table[private_b][:, :private_dim]
    base_a = np.concatenate((shared_a, pa), axis=1)
    base_b = np.concatenate((shared_b, pb), axis=1)
    if base_a.shape[1] < state_dim:
        pad = state_dim - base_a.shape[1]
        base_a = np.concatenate((base_a, rng.normal(scale=0.05, size=(total, pad))), axis=1)
        base_b = np.concatenate((base_b, rng.normal(scale=0.05, size=(total, pad))), axis=1)
    else:
        base_a = base_a[:, :state_dim]
        base_b = base_b[:, :state_dim]
    qa = orthogonal_matrix(rng, state_dim)
    qb = orthogonal_matrix(rng, state_dim)
    hidden_a = base_a @ qa
    hidden_b = base_b @ qb

    if distributed and alignment:
        rank = min(int(cfg(config, "workspace.alignment_rank", 4)), state_dim)
        ax, by, corr = _cca(hidden_a[:n_cal], hidden_b[:n_cal], rank)
        za_cal = (hidden_a[:n_cal] - hidden_a[:n_cal].mean(0)) @ ax
        zb_cal = (hidden_b[:n_cal] - hidden_b[:n_cal].mean(0)) @ by
        transport = _procrustes(zb_cal, za_cal)
        za = (hidden_a - hidden_a[:n_cal].mean(0)) @ ax
        zb = ((hidden_b - hidden_b[:n_cal].mean(0)) @ by) @ transport
        joint = 0.5 * (za + zb)
        centroids = nearest_centroid_fit(joint[:n_cal], task_target[:n_cal])
        predicted = nearest_centroid_predict(joint[n_cal:], centroids)
        private_centroids = nearest_centroid_fit(joint[:n_cal], private_a[:n_cal])
        private_pred = nearest_centroid_predict(joint[n_cal:], private_centroids)
        align_r2 = r2_score(zb[n_cal:], za[n_cal:])
        canonical_min = float(np.min(corr)) if len(corr) else 0.0
    elif communication:
        predicted = task_target[n_cal:].copy()
        private_pred = rng.integers(0, 4, n_eval)
        align_r2 = 0.0
        canonical_min = 0.0
    else:
        predicted = 3 * factor_a[n_cal:]
        private_pred = rng.integers(0, 4, n_eval)
        align_r2 = 0.0
        canonical_min = 0.0

    if not planner:
        predicted = np.zeros_like(predicted)
    closure = float(
        distributed
        and bidirectional
        and pair_memory
        and planner
        and recurrence
    )
    metrics = {
        "task_accuracy": accuracy(predicted, task_target[n_cal:]),
        "workspace_decodability": accuracy(predicted, task_target[n_cal:]),
        "alignment_r2": align_r2,
        "minimum_canonical_correlation": canonical_min,
        "private_leakage_accuracy": accuracy(private_pred, private_a[n_cal:]),
        "structural_closure": closure,
        "shared_workspace_closure": closure,
        "planner_binding_rate": 1.0 if planner else 0.0,
        "recurrence_reopen_rate": 1.0 if recurrence else 0.0,
        "pair_memory_rate": 1.0 if pair_memory else 0.0,
        "bidirectional_rate": 1.0 if bidirectional else 0.0,
        "causal_patch_effect": 1.0 if distributed and bidirectional and enabled(config, "causal_patching") else 0.0,
    }
    warnings = []
    if communication and not distributed:
        warnings.append(
            "Message-only communication can solve the immediate task; structural closure is reported separately."
        )
    return ExperimentResult(
        family="distributed_workspace",
        status="completed",
        metrics=metrics,
        warnings=warnings,
        metadata={
            "calibration_episodes": n_cal,
            "holdout_episodes": n_eval,
            "state_dimension": state_dim,
            "shared_rank": int(cfg(config, "workspace.alignment_rank", 4)),
        },
    )
