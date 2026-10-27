from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json
import numpy as np

from .adapters.base import LatentReasonerAdapter
from .hashing import sha256_object
from .schemas import TaskRecord, TraceObservation


class CachedCaptureAdapter(LatentReasonerAdapter):
    """Content-addressed cache for ordinary and mode-specific trace captures.

    Supplied-trace interventions are intentionally not cached because their state
    space is much larger and because intervention replay should remain explicit.
    """

    def __init__(self, wrapped: LatentReasonerAdapter, root: str | Path):
        self.wrapped = wrapped
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._fingerprint_digest = sha256_object(dict(wrapped.model_fingerprint()))

    def _key(self, task: TaskRecord, mode: str) -> str:
        return sha256_object(
            {
                "model": self._fingerprint_digest,
                "task": task.to_mapping(),
                "mode": mode,
                "schema": "sric.capture-cache.v1",
            }
        )

    def _paths(self, key: str) -> tuple[Path, Path]:
        return self.root / f"{key}.npz", self.root / f"{key}.json"

    def _read(self, key: str) -> TraceObservation | None:
        array_path, json_path = self._paths(key)
        if not array_path.is_file() or not json_path.is_file():
            return None
        meta = json.loads(json_path.read_text(encoding="utf-8"))
        if meta.get("key") != key:
            raise ValueError(f"Capture cache metadata mismatch for {key}")
        with np.load(array_path, allow_pickle=False) as data:
            trace = data["trace"]
            logits = data["answer_logits"]
        return TraceObservation(
            trace=trace,
            answer_loss=float(meta["answer_loss"]),
            answer_logits=logits,
            predicted_answer=meta.get("predicted_answer"),
            generated_text=meta.get("generated_text"),
            generated_correct=meta.get("generated_correct"),
            mode=str(meta.get("mode", "latent")),
            metadata=dict(meta.get("metadata", {})),
        )

    def _write(self, key: str, observation: TraceObservation) -> None:
        array_path, json_path = self._paths(key)
        tmp_array = array_path.with_suffix(".tmp.npz")
        np.savez_compressed(
            tmp_array,
            trace=np.asarray(observation.trace),
            answer_logits=np.asarray(observation.answer_logits),
        )
        tmp_array.replace(array_path)
        payload = {
            "schema": "sric.capture-cache.v1",
            "key": key,
            "answer_loss": float(observation.answer_loss),
            "predicted_answer": observation.predicted_answer,
            "generated_text": observation.generated_text,
            "generated_correct": observation.generated_correct,
            "mode": observation.mode,
            "metadata": dict(observation.metadata),
        }
        tmp_json = json_path.with_suffix(".tmp.json")
        tmp_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp_json.replace(json_path)

    def capture(self, task: TaskRecord) -> TraceObservation:
        return self.capture_mode(task, "latent")

    def capture_mode(self, task: TaskRecord, mode: str) -> TraceObservation:
        key = self._key(task, mode)
        existing = self._read(key)
        if existing is not None:
            return existing
        observation = self.wrapped.capture_mode(task, mode)
        self._write(key, observation)
        return observation

    def score_with_trace(self, task: TaskRecord, trace: Any) -> TraceObservation:
        return self.wrapped.score_with_trace(task, trace)

    def supports_mode(self, mode: str) -> bool:
        return self.wrapped.supports_mode(mode)

    def generate_mode(self, task: TaskRecord, mode: str) -> TraceObservation:
        return self.wrapped.generate_mode(task, mode)

    def model_fingerprint(self) -> Mapping[str, Any]:
        return self.wrapped.model_fingerprint()

    def close(self) -> None:
        self.wrapped.close()
