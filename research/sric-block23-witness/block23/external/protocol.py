from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


@dataclasses.dataclass(frozen=True)
class PilotTask:
    task_id: str
    question: str
    answer: str
    proof_steps: tuple[str, ...] = ()
    proof_family: str | None = None
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class TraceRun:
    task_id: str
    trace: Array
    answer_loss: float
    answer_score: float
    predicted_answer: str
    metadata: dict[str, Any]


class LatentReasonerAdapter(ABC):
    """Minimal intervention surface required by the SRIC real-model pilot."""

    @abstractmethod
    def capture(self, task: PilotTask) -> TraceRun:
        raise NotImplementedError

    @abstractmethod
    def evaluate_trace(self, task: PilotTask, trace: Array) -> TraceRun:
        raise NotImplementedError

    def replay(self, task: PilotTask) -> tuple[TraceRun, TraceRun]:
        ordinary = self.capture(task)
        replayed = self.evaluate_trace(task, ordinary.trace.copy())
        return ordinary, replayed
