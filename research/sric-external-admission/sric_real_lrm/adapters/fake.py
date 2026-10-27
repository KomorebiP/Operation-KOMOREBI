from __future__ import annotations

import hashlib
from typing import Any, Mapping
import numpy as np

from .base import LatentReasonerAdapter, UnsupportedAdapterOperation
from ..schemas import TaskRecord, TraceObservation
from ..witness import protected_proof_witness


def _stable_scalar(text: str, seed: int) -> float:
    digest = hashlib.sha256(f"{seed}:{text}".encode("utf-8")).digest()
    integer = int.from_bytes(digest[:8], "big")
    return integer / float(2**64 - 1)


def fake_semantic_code(task: TaskRecord, step: int, num_latents: int, seed: int = 2301) -> np.ndarray:
    """Audit-only protected semantics for the engineered fixture."""
    return protected_proof_witness(task, step, num_latents, seed=seed)



class FakeProcedureLatentAdapter(LatentReasonerAdapter):
    """Engineered causal-semantic positive control.

    The recurrent trace contains a four-dimensional protected semantic packet
    (answer polarity, a two-dimensional procedure coordinate, and progress) inside
    a larger hidden state. Equal-answer, different-proof traces are therefore not
    interchangeable, while premise-order twins are. This is not a trained language
    model and must never be reported as real-model evidence.
    """

    def __init__(self, num_latents: int = 6, hidden_size: int = 32, seed: int = 2301):
        if num_latents < 2:
            raise ValueError("num_latents must be at least two")
        if hidden_size < 12:
            raise ValueError("hidden_size must be at least twelve")
        self.num_latents = num_latents
        self.hidden_size = hidden_size
        self.seed = seed
        rng = np.random.default_rng(seed)
        q, _ = np.linalg.qr(rng.standard_normal((hidden_size, 10)))
        self.semantic_basis = q[:, :4]
        self.nuisance_basis = q[:, 4:10]

    def _root_id(self, task: TaskRecord) -> str:
        metadata = dict(task.metadata)
        return str(
            metadata.get("semantic_twin_of")
            or metadata.get("counterfactual_of")
            or task.task_id.split("::", 1)[0]
        )

    def _nuisance(self, task: TaskRecord, step: int) -> np.ndarray:
        text = f"{self.seed}:{self._root_id(task)}:nuisance:{step}".encode("utf-8")
        local_seed = int.from_bytes(hashlib.sha256(text).digest()[:8], "big")
        rng = np.random.default_rng(local_seed)
        return rng.standard_normal(6)

    def _canonical_trace(self, task: TaskRecord) -> np.ndarray:
        trace: list[np.ndarray] = []
        state = np.zeros(self.hidden_size, dtype=np.float64)
        for step in range(self.num_latents):
            z = fake_semantic_code(task, step, self.num_latents, self.seed)
            semantic = self.semantic_basis @ z
            nuisance = self.nuisance_basis @ self._nuisance(task, step)
            clock = np.sin((step + 1) * np.arange(1, self.hidden_size + 1) / 13.0) * 0.03
            state = np.tanh(0.30 * state + 1.15 * semantic + 0.42 * nuisance + clock)
            trace.append(state.copy())
        return np.stack(trace)

    def _score(self, task: TaskRecord, trace: Any, *, mode: str = "latent") -> TraceObservation:
        trace_array = np.asarray(trace, dtype=np.float64)
        canonical = self._canonical_trace(task)
        if trace_array.shape != canonical.shape:
            raise ValueError(f"Expected trace shape {canonical.shape}, got {trace_array.shape}")
        # Only the protected semantic packet enters the task score. High-variance
        # nuisance coordinates remain present in the trace so PCA is a meaningful
        # negative control rather than an accidental oracle.
        semantic_trace = trace_array @ self.semantic_basis
        semantic_canonical = canonical @ self.semantic_basis
        step_weights = np.linspace(0.8, 1.4, self.num_latents)[:, None]
        mismatch = float(np.mean(step_weights * (semantic_trace - semantic_canonical) ** 2))
        transition = np.diff(semantic_trace, axis=0)
        canonical_transition = np.diff(semantic_canonical, axis=0)
        transition_mismatch = float(np.mean((transition - canonical_transition) ** 2))
        loss = 0.045 + 5.2 * mismatch + 2.1 * transition_mismatch
        correct_index = 1 if task.answer.strip().lower() in {"true", "yes", "1"} else 0
        margin = max(0.01, 5.5 - 5.0 * loss)
        logits = np.array([0.0, 0.0], dtype=np.float64)
        logits[correct_index] = margin
        logits[1 - correct_index] = -margin
        predicted = "True" if int(np.argmax(logits)) == 1 else "False"
        return TraceObservation(
            trace=trace_array,
            answer_loss=loss,
            answer_logits=logits,
            predicted_answer=predicted,
            generated_text=predicted,
            generated_correct=predicted.strip().lower() == task.answer.strip().lower(),
            mode=mode,
            metadata={"engineered_fixture": True, "mismatch": mismatch},
        )

    def capture(self, task: TaskRecord) -> TraceObservation:
        return self._score(task, self._canonical_trace(task))

    def score_with_trace(self, task: TaskRecord, trace: Any) -> TraceObservation:
        return self._score(task, trace)

    def supports_mode(self, mode: str) -> bool:
        return mode in {"latent", "direct", "verbalized"}

    def capture_mode(self, task: TaskRecord, mode: str) -> TraceObservation:
        if mode == "latent":
            return self.capture(task)
        if mode == "direct":
            # Direct mode lacks procedure computation but may still exploit answer cues.
            trace = np.zeros((self.num_latents, self.hidden_size), dtype=np.float64)
            observation = self._score(task, trace, mode=mode)
            return TraceObservation(
                trace=trace,
                answer_loss=max(0.18, observation.answer_loss * 0.42),
                answer_logits=observation.answer_logits * 0.55,
                predicted_answer=observation.predicted_answer,
                generated_text=observation.generated_text,
                generated_correct=observation.generated_correct,
                mode=mode,
                metadata={**dict(observation.metadata), "mode_control": True},
            )
        if mode == "verbalized":
            observation = self.capture(task)
            return TraceObservation(
                trace=observation.trace,
                answer_loss=observation.answer_loss + 0.015,
                answer_logits=observation.answer_logits * 0.96,
                predicted_answer=observation.predicted_answer,
                generated_text=f"formal proof omitted ### {observation.predicted_answer}",
                generated_correct=observation.generated_correct,
                mode=mode,
                metadata={**dict(observation.metadata), "mode_control": True},
            )
        raise UnsupportedAdapterOperation(f"Unsupported fake mode: {mode}")

    def generate_mode(self, task: TaskRecord, mode: str) -> TraceObservation:
        return self.capture_mode(task, mode)

    def model_fingerprint(self) -> Mapping[str, Any]:
        return {
            "adapter": "FakeProcedureLatentAdapter",
            "num_latents": self.num_latents,
            "hidden_size": self.hidden_size,
            "seed": self.seed,
            "semantic_rank": 4,
            "engineered_positive_control": True,
        }
