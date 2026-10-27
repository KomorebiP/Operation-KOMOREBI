from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from ..schemas import TaskRecord, TraceObservation


class LatentReasonerAdapter(ABC):
    """Minimal interface required by the SRIC causal audit."""

    @abstractmethod
    def capture(self, task: TaskRecord) -> TraceObservation:
        """Run ordinary latent execution and return the exact reinjected trace."""

    @abstractmethod
    def score_with_trace(self, task: TaskRecord, trace: Any) -> TraceObservation:
        """Teacher-force the protected answer while injecting a supplied trace."""

    @abstractmethod
    def model_fingerprint(self) -> Mapping[str, Any]:
        """Return immutable model and adapter identity fields."""

    def close(self) -> None:
        """Release resources. Adapters may override this method."""
        return None
