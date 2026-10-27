from __future__ import annotations

import copy
import datetime as dt
import json
import pathlib
import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Any

from .exceptions import RRCTLabError
from .registry import get_experiment
from .utils import atomic_write_json, digest_object, get_dotted, scalarize
from .version import __version__


class RunLimitError(RRCTLabError):
    """Raised when a cooperative run exceeds a configured resource bound."""


def stable_checkpoint_digest(config: dict[str, Any]) -> str:
    clone = copy.deepcopy(config)
    run = clone.get("run", {})
    run.pop("resume", None)
    run.pop("overwrite", None)
    return digest_object(clone)


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class CheckpointManager:
    run_dir: pathlib.Path
    config_digest: str
    keep: int = 3
    directory_name: str = "checkpoints"

    @property
    def directory(self) -> pathlib.Path:
        path = self.run_dir / self.directory_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def latest_path(self) -> pathlib.Path:
        return self.directory / "latest.json"

    def load_latest(self) -> dict[str, Any] | None:
        if not self.latest_path.is_file():
            return None
        payload = json.loads(self.latest_path.read_text(encoding="utf-8"))
        if payload.get("config_digest") != self.config_digest:
            raise RunLimitError(
                "checkpoint configuration digest does not match the requested run"
            )
        if payload.get("state_digest") != digest_object(payload.get("state", {})):
            raise RunLimitError("checkpoint state digest is invalid")
        return payload

    def save(
        self,
        *,
        step: int,
        state: dict[str, Any],
        metrics: dict[str, Any] | None = None,
        status: str = "running",
        resume_count: int = 0,
    ) -> pathlib.Path:
        payload = {
            "schema": "rrct.lab.checkpoint.v2",
            "version": __version__,
            "created_at_utc": _utc_now(),
            "config_digest": self.config_digest,
            "step": int(step),
            "status": status,
            "resume_count": int(resume_count),
            "state": scalarize(state),
            "metrics": scalarize(metrics or {}),
            "state_digest": digest_object(state),
        }
        step_path = self.directory / f"step_{int(step):09d}.json"
        atomic_write_json(step_path, payload)
        atomic_write_json(self.latest_path, payload)
        self._prune()
        return step_path

    def mark_complete(
        self,
        step: int,
        state: dict[str, Any],
        metrics: dict[str, Any],
        *,
        resume_count: int = 0,
    ) -> None:
        self.save(
            step=step,
            state=state,
            metrics=metrics,
            status="completed",
            resume_count=resume_count,
        )

    def _prune(self) -> None:
        if self.keep <= 0:
            return
        paths = sorted(self.directory.glob("step_*.json"))
        for path in paths[:-self.keep]:
            path.unlink(missing_ok=True)


@dataclass
class RunContext:
    run_dir: pathlib.Path
    config: dict[str, Any]
    checkpoint_manager: CheckpointManager
    started_at: float = field(default_factory=time.monotonic)
    resume_payload: dict[str, Any] | None = None
    checkpoint_interval: int = 0
    timeout_seconds: float = 0.0
    memory_limit_mb: float = 0.0
    _last_checkpoint_step: int = -1

    @classmethod
    def create(cls, run_dir: pathlib.Path, config: dict[str, Any]) -> "RunContext":
        digest = stable_checkpoint_digest(config)
        manager = CheckpointManager(
            run_dir=run_dir,
            config_digest=digest,
            keep=max(0, int(config.get("run", {}).get("checkpoint_keep", 3))),
        )
        resume = bool(config.get("run", {}).get("resume", False))
        payload = manager.load_latest() if resume else None
        family = str(config.get("experiment", {}).get("family", ""))
        checkpoint_key = get_experiment(family).checkpoint_interval_key
        interval = int(get_dotted(config, checkpoint_key, 0)) if checkpoint_key else 0
        context = cls(
            run_dir=run_dir,
            config=config,
            checkpoint_manager=manager,
            resume_payload=payload,
            checkpoint_interval=max(0, interval),
            timeout_seconds=float(config.get("runtime", {}).get("timeout_seconds", 0)),
            memory_limit_mb=float(config.get("runtime", {}).get("memory_limit_mb", 0)),
        )
        context.update_state("running")
        return context

    @property
    def resumed(self) -> bool:
        return self.resume_payload is not None

    @property
    def resume_count(self) -> int:
        if self.resume_payload is None:
            return 0
        return int(self.resume_payload.get("resume_count", 0)) + 1

    @property
    def resume_state(self) -> dict[str, Any] | None:
        if self.resume_payload is None:
            return None
        state = self.resume_payload.get("state")
        return state if isinstance(state, dict) else None

    @property
    def resume_step(self) -> int:
        if self.resume_payload is None:
            return 0
        return int(self.resume_payload.get("step", 0))

    @property
    def state_path(self) -> pathlib.Path:
        return self.run_dir / "run_state.json"

    def update_state(self, status: str, detail: str | None = None) -> None:
        current, peak = tracemalloc.get_traced_memory() if tracemalloc.is_tracing() else (0, 0)
        payload = {
            "schema": "rrct.lab.run_state.v1",
            "version": __version__,
            "updated_at_utc": _utc_now(),
            "status": status,
            "step": max(self.resume_step, self._last_checkpoint_step),
            "resume_count": self.resume_count,
            "elapsed_seconds": time.monotonic() - self.started_at,
            "current_python_memory_mb": current / (1024.0 * 1024.0),
            "peak_python_memory_mb": peak / (1024.0 * 1024.0),
            "config_digest": stable_checkpoint_digest(self.config),
            "checkpoint_present": self.checkpoint_manager.latest_path.is_file(),
        }
        if detail:
            payload["detail"] = detail
        atomic_write_json(self.state_path, payload)

    def check_limits(self) -> None:
        elapsed = time.monotonic() - self.started_at
        if self.timeout_seconds > 0 and elapsed > self.timeout_seconds:
            raise RunLimitError(
                f"run exceeded runtime.timeout_seconds={self.timeout_seconds:g}"
            )
        if self.memory_limit_mb > 0 and tracemalloc.is_tracing():
            _, peak = tracemalloc.get_traced_memory()
            peak_mb = peak / (1024.0 * 1024.0)
            if peak_mb > self.memory_limit_mb:
                raise RunLimitError(
                    f"Python-tracked peak memory {peak_mb:.1f} MB exceeds "
                    f"runtime.memory_limit_mb={self.memory_limit_mb:g}"
                )

    def should_checkpoint(self, step: int) -> bool:
        return (
            self.checkpoint_interval > 0
            and step > self._last_checkpoint_step
            and step % self.checkpoint_interval == 0
        )

    def checkpoint(
        self,
        step: int,
        state: dict[str, Any],
        metrics: dict[str, Any] | None = None,
        *,
        force: bool = False,
    ) -> None:
        self.check_limits()
        if force or self.should_checkpoint(step):
            self.checkpoint_manager.save(
                step=step,
                state=state,
                metrics=metrics,
                status="running",
                resume_count=self.resume_count,
            )
            self._last_checkpoint_step = step
            self.update_state("running")

    def mark_completed(self, step: int, metrics: dict[str, Any]) -> None:
        if bool(self.config.get("run", {}).get("checkpoint_on_completion", True)):
            latest = self.checkpoint_manager.load_latest()
            state = (
                latest.get("state", {})
                if isinstance(latest, dict) and isinstance(latest.get("state"), dict)
                else {}
            )
            state = {**state, "phase": "completed"}
            self.checkpoint_manager.mark_complete(
                step,
                state,
                metrics,
                resume_count=self.resume_count,
            )
        self._last_checkpoint_step = step
        self.update_state("completed")


    def mark_completed_without_checkpoint(self, step: int) -> None:
        self._last_checkpoint_step = step
        self.update_state("completed")

    def mark_interrupted(self, step: int, detail: str = "checkpointed interruption") -> None:
        self._last_checkpoint_step = step
        self.update_state("interrupted", detail)

    def mark_failed(self, detail: str) -> None:
        self.update_state("failed", detail)
