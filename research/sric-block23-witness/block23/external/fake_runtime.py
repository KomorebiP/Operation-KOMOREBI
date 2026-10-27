from __future__ import annotations

import hashlib
import math

import numpy as np

from .protocol import LatentReasonerAdapter, PilotTask, TraceRun


class FakeLatentAdapter(LatentReasonerAdapter):
    """Deterministic protocol fixture. It is not evidence about an external checkpoint."""

    def __init__(self, steps: int = 6, hidden: int = 16):
        self.steps = steps
        self.hidden = hidden

    def _features(self, task: PilotTask) -> np.ndarray:
        semantic_key = task.proof_family or task.question
        digest = hashlib.sha256(semantic_key.encode()).digest()
        x = np.frombuffer(digest[: self.hidden], dtype=np.uint8).astype(float)
        x = (x - 127.5) / 127.5
        x[0] = 1.0 if task.answer.lower() == "true" else -1.0
        x[1] = float(task.metadata.get("proof_depth", len(task.proof_steps))) / 8.0
        return x

    def _native_trace(self, task: PilotTask) -> np.ndarray:
        x = self._features(task)
        trace = []
        h = np.zeros(self.hidden)
        for k in range(self.steps):
            h = np.tanh(0.62 * h + (0.45 + 0.08 * k) * x)
            h[2] += 0.15 * math.sin(k + x[1])
            trace.append(h.copy())
        return np.asarray(trace)

    def _run(self, task: PilotTask, trace: np.ndarray) -> TraceRun:
        native = self._native_trace(task)
        alignment = float(np.mean(trace * native))
        energy = float(np.mean(trace**2))
        correctness_logit = 5.0 * alignment + 0.5 * energy - 0.15
        p_correct = 1.0 / (1.0 + math.exp(-correctness_logit))
        loss = -math.log(max(p_correct, 1e-12))
        pred = task.answer if p_correct >= 0.5 else ("False" if task.answer.lower() == "true" else "True")
        return TraceRun(task.task_id, np.asarray(trace, float), loss, p_correct, pred, {"runtime": "fake"})

    def capture(self, task: PilotTask) -> TraceRun:
        return self._run(task, self._native_trace(task))

    def evaluate_trace(self, task: PilotTask, trace: np.ndarray) -> TraceRun:
        x = np.asarray(trace, float)
        if x.shape != (self.steps, self.hidden):
            raise ValueError(f"expected trace shape {(self.steps, self.hidden)}, got {x.shape}")
        return self._run(task, x)
