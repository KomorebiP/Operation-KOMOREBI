from __future__ import annotations

import hashlib
from typing import Any, Mapping
import numpy as np

from .base import LatentReasonerAdapter
from ..schemas import TaskRecord, TraceObservation


class FakeProcedureLatentAdapter(LatentReasonerAdapter):
    """Engineered positive control for the audit pipeline.

    The trace is invariant to surface-only semantic twins, carries answer information,
    and carries step-specific proof information beyond the final answer. It is not a
    trained language model and must never be reported as real-model evidence.
    """

    def __init__(self, num_latents: int = 6, hidden_size: int = 32, seed: int = 2301):
        if num_latents < 2:
            raise ValueError("num_latents must be at least two")
        if hidden_size < 8:
            raise ValueError("hidden_size must be at least eight")
        self.num_latents = num_latents
        self.hidden_size = hidden_size
        self.seed = seed

    def _vector(self, text: str) -> np.ndarray:
        digest = hashlib.sha256(f"{self.seed}:{text}".encode("utf-8")).digest()
        local_seed = int.from_bytes(digest[:8], "big")
        rng = np.random.default_rng(local_seed)
        vector = rng.standard_normal(self.hidden_size)
        return vector / max(np.linalg.norm(vector), 1e-12)

    def _canonical_trace(self, task: TaskRecord) -> np.ndarray:
        answer_vector = self._vector(f"answer:{task.answer.strip().lower()}")
        proof_items = task.proof_signature or ("empty-proof",)
        trace: list[np.ndarray] = []
        state = self._vector("initial-state") * 0.15
        for step in range(self.num_latents):
            proof_item = proof_items[min(step, len(proof_items) - 1)]
            procedure = self._vector(f"procedure:{proof_item}:latent-step:{step}")
            clock = self._vector(f"clock:{step}")
            state = np.tanh(0.42 * state + 0.92 * procedure + 0.38 * answer_vector + 0.28 * clock)
            trace.append(state.copy())
        return np.stack(trace)

    def _score(self, task: TaskRecord, trace: Any) -> TraceObservation:
        trace_array = np.asarray(trace, dtype=np.float64)
        canonical = self._canonical_trace(task)
        if trace_array.shape != canonical.shape:
            raise ValueError(f"Expected trace shape {canonical.shape}, got {trace_array.shape}")
        step_weights = np.linspace(0.7, 1.3, self.num_latents)[:, None]
        mismatch = float(np.mean(step_weights * (trace_array - canonical) ** 2))
        transition = np.diff(trace_array, axis=0)
        canonical_transition = np.diff(canonical, axis=0)
        transition_mismatch = float(np.mean((transition - canonical_transition) ** 2))
        loss = 0.075 + 2.8 * mismatch + 0.9 * transition_mismatch
        correct_index = 1 if task.answer.strip().lower() in {"true", "yes", "1"} else 0
        margin = max(0.01, 4.0 - 3.0 * loss)
        logits = np.array([0.0, 0.0], dtype=np.float64)
        logits[correct_index] = margin
        logits[1 - correct_index] = -margin
        predicted = "True" if int(np.argmax(logits)) == 1 else "False"
        return TraceObservation(
            trace=trace_array,
            answer_loss=loss,
            answer_logits=logits,
            predicted_answer=predicted,
            metadata={"engineered_fixture": True, "mismatch": mismatch},
        )

    def capture(self, task: TaskRecord) -> TraceObservation:
        return self._score(task, self._canonical_trace(task))

    def score_with_trace(self, task: TaskRecord, trace: Any) -> TraceObservation:
        return self._score(task, trace)

    def model_fingerprint(self) -> Mapping[str, Any]:
        return {
            "adapter": "FakeProcedureLatentAdapter",
            "num_latents": self.num_latents,
            "hidden_size": self.hidden_size,
            "seed": self.seed,
            "engineered_positive_control": True,
        }
