"""Bounded nonvalenced regulation of RRCT feedback strength.

The regulator implements one narrow hypothesis: useful recurrent integration
may require state-aligned feedback rather than either minimal or maximal
coupling.  Telemetry from a completed step can change gains only for the next
step.  No reward, welfare, persistence, or self-preservation variable is
represented here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping

import numpy as np
from numpy.typing import ArrayLike


def _finite_scalar(value: Any, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
        raise ValueError(f"{name} must be a finite real scalar")
    array = np.asarray(value)
    if array.dtype.kind not in "iuf":
        raise ValueError(f"{name} must be a finite real scalar")
    parsed = float(value)
    if not np.isfinite(parsed):
        raise ValueError(f"{name} must be a finite real scalar")
    return parsed


def _finite_vector(values: ArrayLike, name: str) -> np.ndarray:
    try:
        vector = np.asarray(values, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite real array") from exc
    if vector.ndim != 1 or vector.size == 0 or not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must be a nonempty finite real vector")
    return vector


@dataclass(frozen=True)
class FeedbackTelemetry:
    """Bounded diagnostics computed from one completed causal step."""

    surprise: float
    differentiation: float
    redundancy: float
    saturation: float
    temporal_novelty: float
    salience_entropy: float
    demand: float
    congestion: float
    control_signal: float


@dataclass(frozen=True)
class FeedbackControlRecord:
    """One post-step gain decision, applied beginning on the next step."""

    update_index: int
    applied_recurrent_gain: float
    applied_closure_gain: float
    desired_recurrent_gain: float
    desired_closure_gain: float
    next_recurrent_gain: float
    next_closure_gain: float
    recurrent_slew_limited: bool
    closure_slew_limited: bool
    recurrent_bound_clipped: bool
    closure_bound_clipped: bool
    telemetry: FeedbackTelemetry


def compute_feedback_telemetry(
    *,
    specialist_states: ArrayLike,
    specialist_salience: ArrayLike,
    workspace: ArrayLike,
    prediction_error: ArrayLike,
    previous_workspace: ArrayLike,
    workspace_proposal_states: ArrayLike | None = None,
    workspace_weights: ArrayLike | None = None,
) -> FeedbackTelemetry:
    """Compute bounded load and congestion telemetry without changing state.

    When selected workspace proposal states and weights are supplied, breadth,
    differentiation, and redundancy describe information that actually entered
    the global workspace.  The proposal-wide inputs remain as a documented
    fallback for standalone diagnostics.
    """

    try:
        states = np.asarray(specialist_states, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("specialist_states must be a finite real matrix") from exc
    if states.ndim != 2 or min(states.shape) <= 0 or not np.all(np.isfinite(states)):
        raise ValueError("specialist_states must be a nonempty finite real matrix")
    salience = _finite_vector(specialist_salience, "specialist_salience")
    if salience.shape != (states.shape[0],):
        raise ValueError("specialist_salience must match the specialist count")
    if np.any(salience < 0.0):
        raise ValueError("specialist_salience must be nonnegative")
    current = _finite_vector(workspace, "workspace")
    error = _finite_vector(prediction_error, "prediction_error")
    previous = _finite_vector(previous_workspace, "previous_workspace")
    if error.shape != current.shape or previous.shape != current.shape:
        raise ValueError("workspace, prediction_error, and previous_workspace must match")

    if (workspace_proposal_states is None) != (workspace_weights is None):
        raise ValueError(
            "workspace_proposal_states and workspace_weights must be supplied together"
        )
    if workspace_proposal_states is None:
        access_states = states
        weight_values = salience.copy()
        weight_total = float(np.sum(weight_values))
        if weight_total <= np.finfo(np.float64).eps:
            weights = np.full(
                access_states.shape[0], 1.0 / access_states.shape[0], dtype=np.float64
            )
        else:
            weights = weight_values / weight_total
    else:
        try:
            access_states = np.asarray(workspace_proposal_states, dtype=np.float64)
            weights = np.asarray(workspace_weights, dtype=np.float64)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(
                "workspace proposal states and weights must be finite real arrays"
            ) from exc
        if (
            access_states.ndim != 2
            or access_states.shape[1:] != (states.shape[1],)
            or weights.shape != (access_states.shape[0],)
            or not np.all(np.isfinite(access_states))
            or not np.all(np.isfinite(weights))
            or np.any(weights < 0.0)
        ):
            raise ValueError(
                "workspace proposal states and weights have incompatible values"
            )
        if access_states.shape[0] == 0:
            weights = np.zeros(0, dtype=np.float64)
        else:
            weight_total = float(np.sum(weights))
            if weight_total <= np.finfo(np.float64).eps:
                raise ValueError("nonempty workspace weights must have positive mass")
            weights = weights / weight_total

    row_norms = np.linalg.norm(access_states, axis=1)
    active = row_norms > np.finfo(np.float64).eps
    normalized = np.zeros_like(access_states)
    normalized[active] = access_states[active] / row_norms[active, None]
    weighted_power = float(np.sum(weights * np.square(row_norms)))
    activity_rms = float(
        np.sqrt(weighted_power / max(access_states.shape[1], 1))
    )
    activity_gate = float(activity_rms / (activity_rms + 0.05))
    if np.count_nonzero(active) >= 2:
        gram = np.abs(normalized[active] @ normalized[active].T)
        active_weights = weights[active]
        pair_weights = np.outer(active_weights, active_weights)
        np.fill_diagonal(pair_weights, 0.0)
        pair_total = float(np.sum(pair_weights))
        redundancy = (
            float(np.sum(pair_weights * gram) / pair_total) * activity_gate
            if pair_total > np.finfo(np.float64).eps
            else 0.0
        )
    else:
        redundancy = 0.0

    rank_cap = min(access_states.shape) if access_states.size else 0
    if weighted_power <= np.finfo(np.float64).eps or rank_cap <= 1:
        differentiation = 0.0
    else:
        second_moment = access_states.T @ (weights[:, None] * access_states)
        squared_trace = float(np.sum(np.square(second_moment)))
        participation_rank = (
            weighted_power * weighted_power / squared_trace
            if squared_trace > np.finfo(np.float64).eps
            else 1.0
        )
        differentiation = (
            (participation_rank - 1.0) / float(rank_cap - 1)
        ) * activity_gate

    if weights.size <= 1:
        raw_access_entropy = 0.0
    else:
        positive = weights > 0.0
        entropy = -float(np.sum(weights[positive] * np.log(weights[positive])))
        raw_access_entropy = entropy / float(np.log(weights.size))
    salience_entropy = raw_access_entropy * activity_gate

    surprise = float(
        np.clip(
            np.linalg.norm(error) / (2.0 * (np.linalg.norm(current) + 0.25)),
            0.0,
            1.0,
        )
    )
    saturation = float(np.clip(np.sqrt(np.mean(np.square(current))), 0.0, 1.0))
    current_norm = float(np.linalg.norm(current))
    previous_norm = float(np.linalg.norm(previous))
    total_norm = current_norm + previous_norm
    if total_norm <= np.finfo(np.float64).eps:
        temporal_novelty = 0.0
    else:
        temporal_novelty = float(
            np.clip(np.linalg.norm(current - previous) / total_norm, 0.0, 1.0)
        )

    differentiation = float(np.clip(differentiation, 0.0, 1.0))
    redundancy = float(np.clip(redundancy, 0.0, 1.0))
    salience_entropy = float(np.clip(salience_entropy, 0.0, 1.0))
    access_concentration = float(
        np.clip(activity_gate * (1.0 - raw_access_entropy), 0.0, 1.0)
    )
    demand = float(
        np.clip(
            0.38 * surprise
            + 0.30 * differentiation
            + 0.20 * temporal_novelty
            + 0.12 * salience_entropy,
            0.0,
            1.0,
        )
    )
    congestion = float(
        np.clip(
            0.45 * saturation
            + 0.35 * redundancy
            + 0.20 * access_concentration,
            0.0,
            1.0,
        )
    )
    control_signal = float(
        np.clip(0.18 + 0.95 * demand - 0.75 * congestion, 0.0, 1.0)
    )
    return FeedbackTelemetry(
        surprise=surprise,
        differentiation=differentiation,
        redundancy=redundancy,
        saturation=saturation,
        temporal_novelty=temporal_novelty,
        salience_entropy=salience_entropy,
        demand=demand,
        congestion=congestion,
        control_signal=control_signal,
    )


class AdaptiveFeedbackRegulator:
    """Deterministic next-step regulator for recurrent and closure gains."""

    SNAPSHOT_SCHEMA = "rrct.adaptive_feedback_regulator.v1"

    def __init__(
        self,
        initial_recurrent_gain: float,
        initial_closure_gain: float,
        *,
        minimum_gain: float = 0.15,
        maximum_gain: float = 1.20,
        adaptation_rate: float = 0.35,
        maximum_step: float = 0.12,
        deadband: float = 0.02,
    ) -> None:
        self.minimum_gain = _finite_scalar(minimum_gain, "minimum_gain")
        self.maximum_gain = _finite_scalar(maximum_gain, "maximum_gain")
        self.adaptation_rate = _finite_scalar(adaptation_rate, "adaptation_rate")
        self.maximum_step = _finite_scalar(maximum_step, "maximum_step")
        self.deadband = _finite_scalar(deadband, "deadband")
        if self.minimum_gain < 0.0 or self.maximum_gain <= self.minimum_gain:
            raise ValueError("gain bounds must satisfy 0 <= minimum < maximum")
        if not 0.0 < self.adaptation_rate <= 1.0:
            raise ValueError("adaptation_rate must lie in (0, 1]")
        if self.maximum_step <= 0.0:
            raise ValueError("maximum_step must be positive")
        if not 0.0 <= self.deadband < 1.0:
            raise ValueError("deadband must lie in [0, 1)")
        self._initial_recurrent_gain = self._bounded_initial(
            initial_recurrent_gain, "initial_recurrent_gain"
        )
        self._initial_closure_gain = self._bounded_initial(
            initial_closure_gain, "initial_closure_gain"
        )
        self.current_recurrent_gain = self._initial_recurrent_gain
        self.current_closure_gain = self._initial_closure_gain
        self.update_count = 0
        self.last_record: FeedbackControlRecord | None = None

    def _bounded_initial(self, value: Any, name: str) -> float:
        parsed = _finite_scalar(value, name)
        if not self.minimum_gain <= parsed <= self.maximum_gain:
            raise ValueError(f"{name} must lie within the configured gain bounds")
        return parsed

    @property
    def configuration(self) -> dict[str, float]:
        return {
            "initial_recurrent_gain": self._initial_recurrent_gain,
            "initial_closure_gain": self._initial_closure_gain,
            "minimum_gain": self.minimum_gain,
            "maximum_gain": self.maximum_gain,
            "adaptation_rate": self.adaptation_rate,
            "maximum_step": self.maximum_step,
            "deadband": self.deadband,
        }

    def reset(
        self,
        *,
        initial_recurrent_gain: float | None = None,
        initial_closure_gain: float | None = None,
    ) -> None:
        if initial_recurrent_gain is not None:
            self._initial_recurrent_gain = self._bounded_initial(
                initial_recurrent_gain, "initial_recurrent_gain"
            )
        if initial_closure_gain is not None:
            self._initial_closure_gain = self._bounded_initial(
                initial_closure_gain, "initial_closure_gain"
            )
        self.current_recurrent_gain = self._initial_recurrent_gain
        self.current_closure_gain = self._initial_closure_gain
        self.update_count = 0
        self.last_record = None

    def set_current(self, recurrent_gain: float, closure_gain: float) -> None:
        recurrent = self._bounded_initial(recurrent_gain, "recurrent_gain")
        closure = self._bounded_initial(closure_gain, "closure_gain")
        self.current_recurrent_gain = recurrent
        self.current_closure_gain = closure
        self.update_count = 0
        self.last_record = None

    def _next_gain(self, current: float, desired: float) -> tuple[float, bool, bool]:
        span = self.maximum_gain - self.minimum_gain
        if abs(desired - current) <= self.deadband * span:
            return current, False, False
        proposed_delta = self.adaptation_rate * (desired - current)
        limited_delta = float(np.clip(proposed_delta, -self.maximum_step, self.maximum_step))
        slew_limited = not np.isclose(limited_delta, proposed_delta, rtol=0.0, atol=1e-15)
        raw_next = current + limited_delta
        next_gain = float(np.clip(raw_next, self.minimum_gain, self.maximum_gain))
        bound_clipped = not np.isclose(next_gain, raw_next, rtol=0.0, atol=1e-15)
        return next_gain, slew_limited, bound_clipped

    def _desired_gains(self, telemetry: FeedbackTelemetry) -> tuple[float, float]:
        span = self.maximum_gain - self.minimum_gain
        recurrent_unit = telemetry.control_signal
        closure_unit = float(
            np.clip(
                0.20
                + 0.55 * telemetry.control_signal
                + 0.15 * telemetry.differentiation
                - 0.45 * telemetry.surprise
                - 0.25 * telemetry.redundancy
                - 0.15 * telemetry.saturation,
                0.0,
                1.0,
            )
        )
        return (
            self.minimum_gain + span * recurrent_unit,
            self.minimum_gain + span * closure_unit,
        )

    def update(self, telemetry: FeedbackTelemetry) -> FeedbackControlRecord:
        if not isinstance(telemetry, FeedbackTelemetry):
            raise TypeError("telemetry must be FeedbackTelemetry")
        if any(
            isinstance(value, (bool, np.bool_))
            for value in asdict(telemetry).values()
        ):
            raise ValueError("feedback telemetry coordinates must be real scalars")
        values = np.asarray(tuple(asdict(telemetry).values()), dtype=np.float64)
        if values.shape != (9,) or not np.all(np.isfinite(values)) or np.any(values < 0.0) or np.any(values > 1.0):
            raise ValueError("feedback telemetry coordinates must lie in [0, 1]")
        desired_recurrent, desired_closure = self._desired_gains(telemetry)
        applied_recurrent = self.current_recurrent_gain
        applied_closure = self.current_closure_gain
        next_recurrent, recurrent_slew, recurrent_clip = self._next_gain(
            applied_recurrent, desired_recurrent
        )
        next_closure, closure_slew, closure_clip = self._next_gain(
            applied_closure, desired_closure
        )
        record = FeedbackControlRecord(
            update_index=self.update_count,
            applied_recurrent_gain=applied_recurrent,
            applied_closure_gain=applied_closure,
            desired_recurrent_gain=desired_recurrent,
            desired_closure_gain=desired_closure,
            next_recurrent_gain=next_recurrent,
            next_closure_gain=next_closure,
            recurrent_slew_limited=recurrent_slew,
            closure_slew_limited=closure_slew,
            recurrent_bound_clipped=recurrent_clip,
            closure_bound_clipped=closure_clip,
            telemetry=telemetry,
        )
        self.current_recurrent_gain = next_recurrent
        self.current_closure_gain = next_closure
        self.update_count += 1
        self.last_record = record
        return record

    @staticmethod
    def _digest_payload(payload: Mapping[str, Any]) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        ).hexdigest()

    def snapshot(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": self.SNAPSHOT_SCHEMA,
            "configuration": self.configuration,
            "current_recurrent_gain": self.current_recurrent_gain,
            "current_closure_gain": self.current_closure_gain,
            "update_count": self.update_count,
            "last_record": asdict(self.last_record) if self.last_record is not None else None,
        }
        payload["digest"] = self._digest_payload(payload)
        return payload

    def load_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        if not isinstance(snapshot, Mapping):
            raise TypeError("feedback snapshot must be a mapping")
        expected = {
            "schema",
            "configuration",
            "current_recurrent_gain",
            "current_closure_gain",
            "update_count",
            "last_record",
            "digest",
        }
        if set(snapshot) != expected:
            raise ValueError("feedback snapshot fields do not match the schema")
        payload = {key: snapshot[key] for key in expected if key != "digest"}
        if snapshot["schema"] != self.SNAPSHOT_SCHEMA:
            raise ValueError("feedback snapshot schema is unsupported")
        if not isinstance(snapshot["digest"], str) or snapshot["digest"] != self._digest_payload(payload):
            raise ValueError("feedback snapshot digest is invalid")
        configuration = snapshot["configuration"]
        if not isinstance(configuration, Mapping) or set(configuration) != set(
            self.configuration
        ):
            raise ValueError("feedback snapshot configuration does not match")
        for name, expected_value in self.configuration.items():
            if _finite_scalar(configuration[name], name) != expected_value:
                raise ValueError("feedback snapshot configuration does not match")
        recurrent = self._bounded_initial(
            snapshot["current_recurrent_gain"], "current_recurrent_gain"
        )
        closure = self._bounded_initial(
            snapshot["current_closure_gain"], "current_closure_gain"
        )
        update_value = snapshot["update_count"]
        if isinstance(update_value, (bool, np.bool_)) or not isinstance(update_value, (int, np.integer)) or int(update_value) < 0:
            raise ValueError("update_count must be a nonnegative integer")
        record_payload = snapshot["last_record"]
        record: FeedbackControlRecord | None
        if record_payload is None:
            record = None
        else:
            if not isinstance(record_payload, Mapping):
                raise ValueError("last_record must be a mapping or null")
            record_fields = {
                "update_index",
                "applied_recurrent_gain",
                "applied_closure_gain",
                "desired_recurrent_gain",
                "desired_closure_gain",
                "next_recurrent_gain",
                "next_closure_gain",
                "recurrent_slew_limited",
                "closure_slew_limited",
                "recurrent_bound_clipped",
                "closure_bound_clipped",
                "telemetry",
            }
            if set(record_payload) != record_fields or not isinstance(record_payload["telemetry"], Mapping):
                raise ValueError("last_record fields do not match the schema")
            telemetry_fields = set(FeedbackTelemetry.__dataclass_fields__)
            if set(record_payload["telemetry"]) != telemetry_fields:
                raise ValueError("feedback telemetry fields do not match the schema")
            telemetry = FeedbackTelemetry(
                **{
                    key: _finite_scalar(record_payload["telemetry"][key], key)
                    for key in telemetry_fields
                }
            )
            telemetry_values = np.asarray(tuple(asdict(telemetry).values()))
            if np.any(telemetry_values < 0.0) or np.any(telemetry_values > 1.0):
                raise ValueError("feedback telemetry coordinates must lie in [0, 1]")
            for name in (
                "recurrent_slew_limited",
                "closure_slew_limited",
                "recurrent_bound_clipped",
                "closure_bound_clipped",
            ):
                if not isinstance(record_payload[name], (bool, np.bool_)):
                    raise ValueError(f"{name} must be boolean")
            index_value = record_payload["update_index"]
            if isinstance(index_value, (bool, np.bool_)) or not isinstance(index_value, (int, np.integer)) or int(index_value) < 0:
                raise ValueError("update_index must be a nonnegative integer")
            scalar_names = record_fields - {
                "update_index",
                "recurrent_slew_limited",
                "closure_slew_limited",
                "recurrent_bound_clipped",
                "closure_bound_clipped",
                "telemetry",
            }
            scalar_values = {
                name: _finite_scalar(record_payload[name], name) for name in scalar_names
            }
            for name, value in scalar_values.items():
                if not self.minimum_gain <= value <= self.maximum_gain:
                    raise ValueError(f"{name} must lie within the configured gain bounds")
            record = FeedbackControlRecord(
                update_index=int(index_value),
                recurrent_slew_limited=bool(record_payload["recurrent_slew_limited"]),
                closure_slew_limited=bool(record_payload["closure_slew_limited"]),
                recurrent_bound_clipped=bool(record_payload["recurrent_bound_clipped"]),
                closure_bound_clipped=bool(record_payload["closure_bound_clipped"]),
                telemetry=telemetry,
                **scalar_values,
            )
            expected_desired_recurrent, expected_desired_closure = (
                self._desired_gains(telemetry)
            )
            if not np.isclose(
                record.desired_recurrent_gain,
                expected_desired_recurrent,
                rtol=0.0,
                atol=1e-15,
            ):
                raise ValueError("desired recurrent gain is inconsistent with telemetry")
            if not np.isclose(
                record.desired_closure_gain,
                expected_desired_closure,
                rtol=0.0,
                atol=1e-15,
            ):
                raise ValueError("desired closure gain is inconsistent with telemetry")
            expected_recurrent = self._next_gain(
                record.applied_recurrent_gain,
                record.desired_recurrent_gain,
            )
            expected_closure = self._next_gain(
                record.applied_closure_gain,
                record.desired_closure_gain,
            )
            if (
                not np.isclose(
                    record.next_recurrent_gain,
                    expected_recurrent[0],
                    rtol=0.0,
                    atol=1e-15,
                )
                or record.recurrent_slew_limited != expected_recurrent[1]
                or record.recurrent_bound_clipped != expected_recurrent[2]
            ):
                raise ValueError("recurrent control record is internally inconsistent")
            if (
                not np.isclose(
                    record.next_closure_gain,
                    expected_closure[0],
                    rtol=0.0,
                    atol=1e-15,
                )
                or record.closure_slew_limited != expected_closure[1]
                or record.closure_bound_clipped != expected_closure[2]
            ):
                raise ValueError("closure control record is internally inconsistent")
        if (record is None) != (int(update_value) == 0):
            raise ValueError("last_record and update_count are inconsistent")
        if record is not None:
            if record.update_index != int(update_value) - 1:
                raise ValueError("last_record sequence is not contiguous")
            if not np.isclose(record.next_recurrent_gain, recurrent, rtol=0.0, atol=1e-15):
                raise ValueError("last_record recurrent gain does not match state")
            if not np.isclose(record.next_closure_gain, closure, rtol=0.0, atol=1e-15):
                raise ValueError("last_record closure gain does not match state")
        self.current_recurrent_gain = recurrent
        self.current_closure_gain = closure
        self.update_count = int(update_value)
        self.last_record = record


__all__ = [
    "AdaptiveFeedbackRegulator",
    "FeedbackControlRecord",
    "FeedbackTelemetry",
    "compute_feedback_telemetry",
]
