from __future__ import annotations

import dataclasses
import hashlib
from typing import Any

import numpy as np


@dataclasses.dataclass
class DiscoveredQuotient:
    method: str
    rank: int
    basis: np.ndarray
    metrics: dict[str, float]
    receipt: str


def _ridge(x: np.ndarray, y: np.ndarray, ridge: float = 1e-5) -> np.ndarray:
    return np.linalg.solve(x.T @ x + ridge * np.eye(x.shape[1]), x.T @ y)


def _r2(y: np.ndarray, p: np.ndarray) -> float:
    return 1.0 - float(np.sum((y-p)**2)) / max(float(np.sum((y-y.mean(0, keepdims=True))**2)), 1e-12)


def _basis(matrix: np.ndarray, rank: int) -> np.ndarray:
    vals, vecs = np.linalg.eigh((matrix + matrix.T) / 2)
    return vecs[:, np.argsort(vals)[::-1][:rank]]


def discover_quotient(
    traces: np.ndarray,
    twin_traces: np.ndarray,
    intervention_traces: np.ndarray,
    answer_scores: np.ndarray,
    *,
    max_rank: int = 12,
) -> DiscoveredQuotient:
    """Gold-free finite quotient compiler for a captured real-model trace bank.

    Inputs are ordinary traces, semantic-preserving twin traces, traces under
    anonymous interventions, and external answer scores. No proof steps or
    intermediate semantic labels are accepted by this interface.
    """
    x = np.asarray(traces, float).reshape(len(traces), -1)
    xt = np.asarray(twin_traces, float).reshape(len(twin_traces), -1)
    xi = np.asarray(intervention_traces, float).reshape(intervention_traces.shape[0], intervention_traces.shape[1], -1)
    y_future = np.asarray(traces, float)[:, 1:, :].reshape(len(traces), -1)
    y_int = (xi - x[:, None, :]).reshape(len(traces), -1)
    y_ans = np.asarray(answer_scores, float).reshape(-1, 1)
    n = len(x)
    split = max(8, int(0.6*n))
    xc = x[:split] - x[:split].mean(0, keepdims=True)

    matrices: dict[str, np.ndarray] = {}
    matrices["pca"] = xc.T @ xc / max(split,1)
    for name, target in {
        "answer_only": y_ans,
        "predictive": y_future,
        "intervention": y_int,
        "joint": np.hstack([y_future, y_int, y_ans]),
    }.items():
        yc = target[:split] - target[:split].mean(0, keepdims=True)
        b = _ridge(xc, yc)
        matrices[name] = b @ b.T

    candidates: list[DiscoveredQuotient] = []
    for method, m in matrices.items():
        ranks = [1] if method == "answer_only" else range(1, min(max_rank, x.shape[1]) + 1)
        for rank in ranks:
            w = _basis(m, rank)
            q = x @ w; qt = xt @ w
            qtr, qte = q[:split], q[split:]
            pf = qte @ _ridge(qtr, y_future[:split])
            pi = qte @ _ridge(qtr, y_int[:split])
            pa = qte @ _ridge(qtr, y_ans[:split])
            scale = np.maximum(np.sqrt(np.mean(qte*qte, axis=1)), 1e-8)
            drift = float(np.mean(np.sqrt(np.mean((qte-qt[split:])**2, axis=1))/scale))
            metrics = {
                "future_r2": _r2(y_future[split:], pf),
                "intervention_r2": _r2(y_int[split:], pi),
                "answer_r2": _r2(y_ans[split:], pa),
                "twin_drift": drift,
            }
            valid = metrics["future_r2"] >= 0.20 and metrics["intervention_r2"] >= 0.10 and metrics["twin_drift"] <= 0.50
            if valid:
                payload = f"{method}|{rank}|" + "|".join(f"{k}:{metrics[k]:.12g}" for k in sorted(metrics))
                candidates.append(DiscoveredQuotient(method, rank, w, metrics, hashlib.sha256(payload.encode()).hexdigest()))
    if not candidates:
        raise RuntimeError("no gold-free quotient candidate passed the calibration gates")
    priority = {"intervention":0,"joint":1,"predictive":2,"pca":3,"answer_only":4}
    candidates.sort(key=lambda c:(c.rank, priority[c.method]))
    return candidates[0]
