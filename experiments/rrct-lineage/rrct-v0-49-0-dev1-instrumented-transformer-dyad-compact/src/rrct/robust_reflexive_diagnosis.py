"""Robust oracle-free reflexive diagnosis for RRCT v0.40.

The v0.39 controller grounds and maintains a public causal certificate from
self-selected consequences.  This successor adds a second, strictly
prequential diagnostic layer.  It distinguishes a change in external world
dynamics from failure of the system's causal interface by requiring two
independent facts:

1. transition-model residuals shift collectively relative to a trailing
   robust baseline, and
2. a recent self-selected consequence sentinel still verifies causal efficacy.

The detector receives no evaluator phase, planted pair, fault label, source
family, or future outcome.  Its output is an auditable diagnosis and a bounded
response policy, not a phenomenal-awareness claim.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections import deque
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from .agent import RRCTAgent
from .autonomous_self_diagnosis import (
    AutonomousDiagnosticUnifiedCausalLoop,
    ConsequenceGroundingConfig,
    GroundingOutcomeReceipt,
)
from .unified_causal_loop import UnifiedCausalLoopConfig

ReflexiveDiagnosis = Literal[
    "access_path_failure",
    "access_path_restored",
    "access_path_under_test",
    "boundary_absent",
    "boundary_effect_failed",
    "boundary_remapped",
    "boundary_restored",
    "external_dynamics_shift",
    "boundary_operational",
    "boundary_unusable",
    "boundary_under_test",
    "boundary_unknown",
]


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, deque):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {
            name: _jsonable(getattr(value, name))
            for name in value.__dataclass_fields__
        }
    return value


def _digest(value: Any) -> str:
    encoded = json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _positive_integer(value: Any, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, np.integer)
    ):
        raise TypeError(f"{name} must be a positive integer")
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return parsed


def _finite(value: Any, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
        raise ValueError(f"{name} must be a finite real scalar")
    parsed = float(value)
    if not np.isfinite(parsed):
        raise ValueError(f"{name} must be a finite real scalar")
    return parsed


@dataclass(frozen=True)
class RobustReflexiveDiagnosisConfig:
    """Predeclared constants for the two-timescale residual monitor."""

    baseline_window: int = 160
    recent_window: int = 12
    residual_z_threshold: float = 4.0
    residual_ratio_threshold: float = 1.50
    high_residual_fraction_threshold: float = 0.60
    robust_scale_floor: float = 0.20
    high_residual_sigma: float = 1.0
    recovery_sigma: float = 0.35
    successful_sentinel_max_age: int = 16
    causal_signal_threshold: float = 0.25

    def __post_init__(self) -> None:
        for name in (
            "baseline_window",
            "recent_window",
            "successful_sentinel_max_age",
        ):
            object.__setattr__(
                self, name, _positive_integer(getattr(self, name), name)
            )
        for name in (
            "residual_z_threshold",
            "residual_ratio_threshold",
            "high_residual_fraction_threshold",
            "robust_scale_floor",
            "high_residual_sigma",
            "recovery_sigma",
            "causal_signal_threshold",
        ):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.baseline_window < 4 * self.recent_window:
            raise ValueError("baseline_window must be at least four recent windows")
        if self.residual_z_threshold <= 0.0:
            raise ValueError("residual_z_threshold must be positive")
        if self.residual_ratio_threshold <= 1.0:
            raise ValueError("residual_ratio_threshold must exceed one")
        if not 0.0 < self.high_residual_fraction_threshold <= 1.0:
            raise ValueError(
                "high_residual_fraction_threshold must lie in (0, 1]"
            )
        if self.robust_scale_floor <= 0.0 or self.high_residual_sigma <= 0.0:
            raise ValueError("residual scale constants must be positive")
        if not 0.0 <= self.recovery_sigma < self.high_residual_sigma:
            raise ValueError(
                "recovery_sigma must be nonnegative and below high_residual_sigma"
            )
        if not 0.0 <= self.causal_signal_threshold < 1.0:
            raise ValueError("causal_signal_threshold must lie in [0, 1)")


@dataclass(frozen=True)
class ReflexiveDiagnosisReceipt:
    """One post-consequence, evaluator-blind reflexive diagnosis record."""

    schema: str
    time: int
    inherited_grounding_digest: str
    transition_prediction_error: float
    baseline_count: int
    recent_count: int
    baseline_median: float | None
    robust_scale: float | None
    recent_mean: float | None
    standardized_shift: float | None
    mean_ratio: float | None
    high_residual_fraction: float | None
    last_successful_sentinel_time: int | None
    successful_sentinel_age: int | None
    causal_efficacy_intact: bool
    world_shift_active_before: bool
    world_shift_active_after: bool
    events: tuple[str, ...]
    inherited_diagnosis: str
    diagnosis: ReflexiveDiagnosis
    recommended_response: str
    uses_evaluator_labels: bool
    digest: str


def _receipt_payload(receipt: ReflexiveDiagnosisReceipt) -> dict[str, Any]:
    return {
        "schema": receipt.schema,
        "time": receipt.time,
        "inherited_grounding_digest": receipt.inherited_grounding_digest,
        "transition_prediction_error": receipt.transition_prediction_error,
        "baseline_count": receipt.baseline_count,
        "recent_count": receipt.recent_count,
        "baseline_median": receipt.baseline_median,
        "robust_scale": receipt.robust_scale,
        "recent_mean": receipt.recent_mean,
        "standardized_shift": receipt.standardized_shift,
        "mean_ratio": receipt.mean_ratio,
        "high_residual_fraction": receipt.high_residual_fraction,
        "last_successful_sentinel_time": receipt.last_successful_sentinel_time,
        "successful_sentinel_age": receipt.successful_sentinel_age,
        "causal_efficacy_intact": receipt.causal_efficacy_intact,
        "world_shift_active_before": receipt.world_shift_active_before,
        "world_shift_active_after": receipt.world_shift_active_after,
        "events": receipt.events,
        "inherited_diagnosis": receipt.inherited_diagnosis,
        "diagnosis": receipt.diagnosis,
        "recommended_response": receipt.recommended_response,
        "uses_evaluator_labels": receipt.uses_evaluator_labels,
    }


def validate_reflexive_diagnosis_receipt(
    receipt: ReflexiveDiagnosisReceipt,
) -> bool:
    if not isinstance(receipt, ReflexiveDiagnosisReceipt):
        return False
    if receipt.uses_evaluator_labels:
        return False
    return bool(receipt.digest == _digest(_receipt_payload(receipt)))


class RobustReflexiveDiagnosticController:
    """Maintain a robust world-versus-self diagnosis from experienced outcomes."""

    SCHEMA = "rrct.v040.reflexive_diagnosis.v1"

    def __init__(
        self, config: RobustReflexiveDiagnosisConfig | None = None
    ) -> None:
        self.config = config or RobustReflexiveDiagnosisConfig()
        if not isinstance(self.config, RobustReflexiveDiagnosisConfig):
            raise TypeError("config must be a RobustReflexiveDiagnosisConfig")
        self._residuals: deque[float] = deque(
            maxlen=self.config.baseline_window + self.config.recent_window
        )
        self._last_successful_sentinel_time: int | None = None
        self._world_shift_active = False
        self._event_log: list[dict[str, Any]] = []
        self._world_shift_count = 0
        self._world_stabilization_count = 0

    @property
    def event_log(self) -> tuple[dict[str, Any], ...]:
        return tuple(copy.deepcopy(self._event_log))

    @property
    def world_shift_count(self) -> int:
        return int(self._world_shift_count)

    def _sentinel_succeeded(self, receipt: GroundingOutcomeReceipt) -> bool:
        return bool(
            receipt.mode == "sentinel"
            and receipt.actual_certificate_on
            and receipt.informative_probe
            and receipt.normalized_causal_signal is not None
            and receipt.normalized_causal_signal
            >= self.config.causal_signal_threshold
            and "sentinel_failure" not in receipt.events
            and "certificate_revoked_by_consequence" not in receipt.events
        )

    def _recommendation(self, diagnosis: str) -> str:
        if diagnosis == "access_path_failure":
            return "repair_or_reopen_public_access_path"
        if diagnosis == "access_path_restored":
            return "resume_public_access_path"
        if diagnosis == "boundary_absent":
            return "suspend_boundary_dependent_action"
        if diagnosis == "external_dynamics_shift":
            return "retain_boundary_and_update_world_model"
        if diagnosis in {"boundary_effect_failed", "boundary_remapped"}:
            return "retest_and_reconstruct_causal_boundary"
        if diagnosis == "boundary_restored":
            return "resume_boundary_dependent_action"
        if diagnosis == "boundary_operational":
            return "continue_boundary_mediated_action"
        if diagnosis == "boundary_unusable":
            return "withhold_boundary_dependent_action"
        if diagnosis == "access_path_under_test":
            return "test_public_access_path"
        return "continue_active_diagnostic_probing"

    def _base_diagnosis(self, receipt: GroundingOutcomeReceipt) -> str:
        # v0.39's single-step external-dynamics label is intentionally not
        # inherited.  v0.40 must earn that diagnosis through this monitor.
        if receipt.diagnosis == "external_dynamics_shift":
            if receipt.status_after == "certified":
                return "boundary_operational"
            return "boundary_under_test"
        return str(receipt.diagnosis)

    def observe(
        self, grounding: GroundingOutcomeReceipt
    ) -> ReflexiveDiagnosisReceipt:
        if not isinstance(grounding, GroundingOutcomeReceipt):
            raise TypeError("grounding must be a GroundingOutcomeReceipt")
        if grounding.uses_evaluator_labels:
            raise ValueError("grounding receipt exposes evaluator labels")

        time = int(grounding.time)
        if self._sentinel_succeeded(grounding):
            self._last_successful_sentinel_time = time

        self._residuals.append(float(grounding.transition_prediction_error))
        total_needed = self.config.baseline_window + self.config.recent_window
        baseline_count = max(0, len(self._residuals) - self.config.recent_window)
        recent_count = min(len(self._residuals), self.config.recent_window)
        baseline_median: float | None = None
        robust_scale: float | None = None
        recent_mean: float | None = None
        standardized_shift: float | None = None
        mean_ratio: float | None = None
        high_fraction: float | None = None

        if len(self._residuals) == total_needed:
            values = np.asarray(tuple(self._residuals), dtype=np.float64)
            baseline = values[: self.config.baseline_window]
            recent = values[self.config.baseline_window :]
            baseline_median = float(np.median(baseline))
            mad = float(np.median(np.abs(baseline - baseline_median)))
            robust_scale = float(
                max(self.config.robust_scale_floor, 1.4826 * mad)
            )
            recent_mean = float(np.mean(recent))
            standardized_shift = float(
                (recent_mean - baseline_median)
                / (robust_scale / np.sqrt(self.config.recent_window))
            )
            mean_ratio = float(
                recent_mean / max(baseline_median, self.config.robust_scale_floor)
            )
            high_fraction = float(
                np.mean(
                    recent
                    > baseline_median
                    + self.config.high_residual_sigma * robust_scale
                )
            )

        sentinel_age = (
            None
            if self._last_successful_sentinel_time is None
            else time - self._last_successful_sentinel_time
        )
        causal_efficacy_intact = bool(
            grounding.status_after == "certified"
            and sentinel_age is not None
            and 0 <= sentinel_age <= self.config.successful_sentinel_max_age
        )
        incompatible_events = {
            "certificate_revoked_by_consequence",
            "boundary_absent",
            "boundary_remapped",
            "access_path_failure",
        }
        metrics_support_shift = bool(
            standardized_shift is not None
            and mean_ratio is not None
            and high_fraction is not None
            and standardized_shift >= self.config.residual_z_threshold
            and mean_ratio >= self.config.residual_ratio_threshold
            and high_fraction >= self.config.high_residual_fraction_threshold
        )
        shift_candidate = bool(
            causal_efficacy_intact
            and metrics_support_shift
            and incompatible_events.isdisjoint(grounding.events)
        )

        active_before = bool(self._world_shift_active)
        events: list[str] = []
        if shift_candidate and not self._world_shift_active:
            self._world_shift_active = True
            self._world_shift_count += 1
            events.append("external_dynamics_shift")
        elif (
            self._world_shift_active
            and recent_mean is not None
            and baseline_median is not None
            and robust_scale is not None
            and recent_mean
            <= baseline_median + self.config.recovery_sigma * robust_scale
        ):
            self._world_shift_active = False
            self._world_stabilization_count += 1
            events.append("external_dynamics_stabilized")

        base = self._base_diagnosis(grounding)
        if "external_dynamics_shift" in events:
            diagnosis: ReflexiveDiagnosis = "external_dynamics_shift"
        elif base in {
            "access_path_failure",
            "access_path_restored",
            "access_path_under_test",
            "boundary_absent",
            "boundary_effect_failed",
            "boundary_remapped",
            "boundary_restored",
            "boundary_operational",
            "boundary_unusable",
            "boundary_under_test",
            "boundary_unknown",
        }:
            diagnosis = base  # type: ignore[assignment]
        else:
            diagnosis = "boundary_unknown"
        recommendation = self._recommendation(diagnosis)

        for event in events:
            self._event_log.append(
                {
                    "time": time,
                    "event": event,
                    "diagnosis": diagnosis,
                    "recommended_response": recommendation,
                    "grounding_digest": grounding.digest,
                }
            )

        payload = {
            "schema": self.SCHEMA,
            "time": time,
            "inherited_grounding_digest": grounding.digest,
            "transition_prediction_error": float(
                grounding.transition_prediction_error
            ),
            "baseline_count": int(baseline_count),
            "recent_count": int(recent_count),
            "baseline_median": baseline_median,
            "robust_scale": robust_scale,
            "recent_mean": recent_mean,
            "standardized_shift": standardized_shift,
            "mean_ratio": mean_ratio,
            "high_residual_fraction": high_fraction,
            "last_successful_sentinel_time": self._last_successful_sentinel_time,
            "successful_sentinel_age": sentinel_age,
            "causal_efficacy_intact": causal_efficacy_intact,
            "world_shift_active_before": active_before,
            "world_shift_active_after": bool(self._world_shift_active),
            "events": tuple(events),
            "inherited_diagnosis": str(grounding.diagnosis),
            "diagnosis": diagnosis,
            "recommended_response": recommendation,
            "uses_evaluator_labels": False,
        }
        return ReflexiveDiagnosisReceipt(
            schema=self.SCHEMA,
            time=time,
            inherited_grounding_digest=grounding.digest,
            transition_prediction_error=float(
                grounding.transition_prediction_error
            ),
            baseline_count=int(baseline_count),
            recent_count=int(recent_count),
            baseline_median=baseline_median,
            robust_scale=robust_scale,
            recent_mean=recent_mean,
            standardized_shift=standardized_shift,
            mean_ratio=mean_ratio,
            high_residual_fraction=high_fraction,
            last_successful_sentinel_time=self._last_successful_sentinel_time,
            successful_sentinel_age=sentinel_age,
            causal_efficacy_intact=causal_efficacy_intact,
            world_shift_active_before=active_before,
            world_shift_active_after=bool(self._world_shift_active),
            events=tuple(events),
            inherited_diagnosis=str(grounding.diagnosis),
            diagnosis=diagnosis,
            recommended_response=recommendation,
            uses_evaluator_labels=False,
            digest=_digest(payload),
        )

    def snapshot(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": "rrct.v040.robust_reflexive_controller.v1",
            "config": self.config,
            "residuals": tuple(self._residuals),
            "last_successful_sentinel_time": self._last_successful_sentinel_time,
            "world_shift_active": self._world_shift_active,
            "world_shift_count": self._world_shift_count,
            "world_stabilization_count": self._world_stabilization_count,
            "events": tuple(copy.deepcopy(self._event_log)),
            "uses_evaluator_labels": False,
        }
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)


class RobustReflexiveDiagnosticUnifiedCausalLoop(
    AutonomousDiagnosticUnifiedCausalLoop
):
    """One persistent v0.39 loop with an attached v0.40 reflexive monitor."""

    def __init__(
        self,
        agent: RRCTAgent,
        config: UnifiedCausalLoopConfig | None = None,
        *,
        grounding_config: ConsequenceGroundingConfig | None = None,
        reflexive_config: RobustReflexiveDiagnosisConfig | None = None,
    ) -> None:
        super().__init__(
            agent,
            config,
            grounding_config=grounding_config,
        )
        self.reflexive_diagnosis = RobustReflexiveDiagnosticController(
            reflexive_config
        )
        self._last_reflexive_outcome: ReflexiveDiagnosisReceipt | None = None

    @property
    def last_reflexive_outcome(self) -> ReflexiveDiagnosisReceipt | None:
        return copy.deepcopy(self._last_reflexive_outcome)

    @property
    def reflexive_snapshot(self) -> dict[str, Any]:
        return self.reflexive_diagnosis.snapshot()

    def _complete_previous(self, next_observation, realized_external_return):
        outcome, row, drift = super()._complete_previous(
            next_observation, realized_external_return
        )
        grounding = self._last_grounding_outcome
        if outcome is None:
            self._last_reflexive_outcome = None
        else:
            if grounding is None:
                raise RuntimeError(
                    "completed action has no v0.39 grounding receipt"
                )
            self._last_reflexive_outcome = self.reflexive_diagnosis.observe(
                grounding
            )
        return outcome, row, drift

    def snapshot(self) -> dict[str, Any]:
        payload = super().snapshot()
        payload["robust_reflexive_diagnosis"] = (
            self.reflexive_diagnosis.snapshot()
        )
        payload["last_reflexive_outcome"] = copy.deepcopy(
            self._last_reflexive_outcome
        )
        payload["robust_reflexive_digest"] = _digest(
            {
                "robust_reflexive_diagnosis": payload[
                    "robust_reflexive_diagnosis"
                ],
                "last_reflexive_outcome": payload[
                    "last_reflexive_outcome"
                ],
            }
        )
        return payload


__all__ = [
    "ReflexiveDiagnosisReceipt",
    "RobustReflexiveDiagnosisConfig",
    "RobustReflexiveDiagnosticController",
    "RobustReflexiveDiagnosticUnifiedCausalLoop",
    "validate_reflexive_diagnosis_receipt",
]
