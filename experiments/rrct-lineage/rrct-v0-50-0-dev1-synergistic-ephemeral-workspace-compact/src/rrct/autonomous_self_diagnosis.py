"""Oracle-free consequence grounding and active self-diagnosis for RRCT v0.39.

The private causal-boundary learner and workspace may expose one candidate
structural certificate.  This module does not trust that candidate merely
because an internal module produced it.  Instead, a persistent controller
selects certificate-ON and certificate-OFF interventions, chooses high-value
actions for those probes, and authorizes ordinary use only after experienced
returns support a causal contrast.

No evaluator phase, planted route, hidden pair, source-family label, or future
outcome is accepted by the controller.  The controller can also distinguish a
missing access path from an inactive private boundary by comparing public
transport with already available internal health telemetry.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import deque
from dataclasses import dataclass, field, replace
from typing import Any, Literal

import numpy as np

from .agent import RRCTAgent, StepResult
from .unified_causal_loop import (
    ActionCandidate,
    ActionOutcomeReceipt,
    ActionSelectionReceipt,
    DriftAssessment,
    PublicBoundaryCertificate,
    PublicBoundaryGateReceipt,
    RandomizedTransitionRow,
    UnifiedCausalLoop,
    UnifiedCausalLoopConfig,
)

Signature = tuple[tuple[int, int], int, int]
GroundingStatus = Literal["unverified", "certified", "rejected", "revoked"]
ProbeMode = Literal[
    "no_candidate",
    "access_fault",
    "probe_on",
    "probe_off",
    "sentinel",
    "ordinary_use",
    "withheld",
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


def _finite(value: Any, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
        raise ValueError(f"{name} must be a finite real scalar")
    parsed = float(value)
    if not np.isfinite(parsed):
        raise ValueError(f"{name} must be a finite real scalar")
    return parsed


def _positive_integer(value: Any, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, np.integer)
    ):
        raise TypeError(f"{name} must be a positive integer")
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return parsed


@dataclass(frozen=True)
class ConsequenceGroundingConfig:
    """Predeclared truth-free constants for active certificate testing."""

    minimum_on_samples: int = 2
    minimum_off_samples: int = 2
    rejection_samples_each: int = 6
    maximum_samples_each: int = 12
    certification_margin: float = 0.45
    rejection_margin: float = 0.20
    confidence_z: float = 2.0
    prior_noise_scale: float = 0.08
    minimum_probe_opportunity: float = 0.45
    sentinel_interval: int = 32
    sentinel_failure_threshold: float = 0.25
    sentinel_failures_to_revoke: int = 2
    epistemic_action_bonus: float = 24.0
    task_return_scale: float = 1.0
    action_cost: float = 0.04
    access_fault_confirmations: int = 2
    transition_baseline_capacity: int = 160
    transition_minimum_baseline: int = 48
    transition_spike_z: float = 7.0
    transition_spike_floor: float = 0.20
    restoration_absence_threshold: int = 480

    def __post_init__(self) -> None:
        for name in (
            "minimum_on_samples",
            "minimum_off_samples",
            "rejection_samples_each",
            "maximum_samples_each",
            "sentinel_interval",
            "sentinel_failures_to_revoke",
            "access_fault_confirmations",
            "transition_baseline_capacity",
            "transition_minimum_baseline",
            "restoration_absence_threshold",
        ):
            object.__setattr__(
                self, name, _positive_integer(getattr(self, name), name)
            )
        for name in (
            "certification_margin",
            "rejection_margin",
            "confidence_z",
            "prior_noise_scale",
            "minimum_probe_opportunity",
            "sentinel_failure_threshold",
            "epistemic_action_bonus",
            "task_return_scale",
            "action_cost",
            "transition_spike_z",
            "transition_spike_floor",
        ):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.minimum_on_samples > self.maximum_samples_each:
            raise ValueError("minimum_on_samples exceeds maximum_samples_each")
        if self.minimum_off_samples > self.maximum_samples_each:
            raise ValueError("minimum_off_samples exceeds maximum_samples_each")
        if self.rejection_samples_each > self.maximum_samples_each:
            raise ValueError("rejection_samples_each exceeds maximum_samples_each")
        if self.transition_minimum_baseline > self.transition_baseline_capacity:
            raise ValueError("transition baseline minimum exceeds capacity")
        if not 0.0 < self.rejection_margin < self.certification_margin:
            raise ValueError(
                "margins must satisfy 0 < rejection < certification"
            )
        if self.confidence_z <= 0.0 or self.prior_noise_scale <= 0.0:
            raise ValueError("confidence_z and prior_noise_scale must be positive")
        if self.minimum_probe_opportunity <= 0.0:
            raise ValueError("minimum_probe_opportunity must be positive")
        if not 0.0 <= self.sentinel_failure_threshold < 1.0:
            raise ValueError("sentinel_failure_threshold must lie in [0, 1)")
        if self.epistemic_action_bonus <= 0.0:
            raise ValueError("epistemic_action_bonus must be positive")
        if self.task_return_scale <= 0.0 or self.action_cost < 0.0:
            raise ValueError("invalid public task-value constants")
        if self.transition_spike_z <= 0.0 or self.transition_spike_floor <= 0.0:
            raise ValueError("transition spike constants must be positive")


@dataclass
class _CandidateLedger:
    signature: Signature
    first_seen_time: int
    status: GroundingStatus = "unverified"
    on_samples: deque[float] = field(default_factory=deque)
    off_samples: deque[float] = field(default_factory=deque)
    certified_time: int | None = None
    rejected_time: int | None = None
    revoked_time: int | None = None
    next_sentinel_time: int | None = None
    consecutive_sentinel_failures: int = 0
    last_evidence_time: int | None = None


@dataclass
class _PendingGroundingPlan:
    time: int
    raw_signature: Signature | None
    raw_certificate_digest: str | None
    mode: ProbeMode
    requested_certificate_on: bool
    actual_certificate_on: bool = False
    status_before: GroundingStatus | None = None
    reason: str = ""
    expected_information_gain: float = 0.0
    on_count_before: int = 0
    off_count_before: int = 0
    posterior_delta_before: float | None = None
    lower_bound_before: float | None = None
    upper_bound_before: float | None = None
    private_boundary_active: bool = False
    workspace_candidate_selected: bool = False
    workspace_drive_norm: float = 0.0
    access_update_count: int = 0
    access_fault_suspected: bool = False
    plan_events: tuple[str, ...] = ()
    selected_key: str | None = None
    selected_action: np.ndarray | None = None
    observable_context: np.ndarray | None = None
    probe_opportunity: float | None = None


@dataclass(frozen=True)
class GroundingOutcomeReceipt:
    """Post-outcome audit record for one self-selected diagnostic decision."""

    time: int
    raw_signature: Signature | None
    raw_certificate_digest: str | None
    mode: ProbeMode
    requested_certificate_on: bool
    actual_certificate_on: bool
    status_before: GroundingStatus | None
    status_after: GroundingStatus | None
    reason: str
    expected_information_gain: float
    selected_key: str
    selected_action: tuple[float, ...]
    observable_context: tuple[float, ...]
    probe_opportunity: float
    informative_probe: bool
    realized_external_return: float | None
    normalized_causal_signal: float | None
    on_count_before: int
    off_count_before: int
    on_count_after: int
    off_count_after: int
    posterior_delta: float | None
    lower_bound: float | None
    upper_bound: float | None
    consecutive_sentinel_failures: int
    transition_prediction_error: float
    events: tuple[str, ...]
    diagnosis: str
    recommended_response: str
    private_boundary_active: bool
    workspace_candidate_selected: bool
    workspace_drive_norm: float
    access_update_count: int
    uses_evaluator_labels: bool
    digest: str



def _grounding_receipt_payload(
    receipt: GroundingOutcomeReceipt,
) -> dict[str, Any]:
    return {
        "schema": "rrct.v039.grounding_outcome.v1",
        "time": receipt.time,
        "raw_signature": receipt.raw_signature,
        "raw_certificate_digest": receipt.raw_certificate_digest,
        "mode": receipt.mode,
        "requested_certificate_on": receipt.requested_certificate_on,
        "actual_certificate_on": receipt.actual_certificate_on,
        "status_before": receipt.status_before,
        "status_after": receipt.status_after,
        "reason": receipt.reason,
        "expected_information_gain": receipt.expected_information_gain,
        "selected_key": receipt.selected_key,
        "selected_action": receipt.selected_action,
        "observable_context": receipt.observable_context,
        "probe_opportunity": receipt.probe_opportunity,
        "informative_probe": receipt.informative_probe,
        "realized_external_return": receipt.realized_external_return,
        "normalized_causal_signal": receipt.normalized_causal_signal,
        "on_count_before": receipt.on_count_before,
        "off_count_before": receipt.off_count_before,
        "on_count_after": receipt.on_count_after,
        "off_count_after": receipt.off_count_after,
        "posterior_delta": receipt.posterior_delta,
        "lower_bound": receipt.lower_bound,
        "upper_bound": receipt.upper_bound,
        "consecutive_sentinel_failures": (
            receipt.consecutive_sentinel_failures
        ),
        "transition_prediction_error": receipt.transition_prediction_error,
        "events": receipt.events,
        "diagnosis": receipt.diagnosis,
        "recommended_response": receipt.recommended_response,
        "private_boundary_active": receipt.private_boundary_active,
        "workspace_candidate_selected": (
            receipt.workspace_candidate_selected
        ),
        "workspace_drive_norm": receipt.workspace_drive_norm,
        "access_update_count": receipt.access_update_count,
        "uses_evaluator_labels": receipt.uses_evaluator_labels,
    }


def validate_grounding_outcome_receipt(
    receipt: GroundingOutcomeReceipt,
) -> bool:
    """Recompute the complete v0.39 post-outcome receipt digest."""

    if not isinstance(receipt, GroundingOutcomeReceipt):
        return False
    return bool(receipt.digest == _digest(_grounding_receipt_payload(receipt)))


class ConsequenceGroundedAccessController:
    """Actively test and maintain public causal-certificate authorization."""

    def __init__(
        self, config: ConsequenceGroundingConfig | None = None
    ) -> None:
        self.config = config or ConsequenceGroundingConfig()
        if not isinstance(self.config, ConsequenceGroundingConfig):
            raise TypeError("config must be a ConsequenceGroundingConfig")
        self._ledgers: dict[Signature, _CandidateLedger] = {}
        self._current_raw_signature: Signature | None = None
        self._last_certified_signature: Signature | None = None
        self._ever_certified = False
        self._absence_active = False
        self._absence_event_emitted = False
        self._absence_started_time: int | None = None
        self._access_fault_streak = 0
        self._access_fault_active = False
        self._transition_errors: deque[float] = deque(
            maxlen=self.config.transition_baseline_capacity
        )
        self._events: list[dict[str, Any]] = []
        self._probe_count = 0
        self._informative_probe_count = 0
        self._authorization_count = 0
        self._revocation_count = 0
        self._access_fault_count = 0

    @property
    def event_log(self) -> tuple[dict[str, Any], ...]:
        return tuple(copy.deepcopy(self._events))

    @property
    def probe_count(self) -> int:
        return self._probe_count

    @property
    def informative_probe_count(self) -> int:
        return self._informative_probe_count

    @property
    def authorization_count(self) -> int:
        return self._authorization_count

    @property
    def revocation_count(self) -> int:
        return self._revocation_count

    @property
    def access_fault_count(self) -> int:
        return self._access_fault_count

    def _ledger(self, signature: Signature, time: int) -> _CandidateLedger:
        ledger = self._ledgers.get(signature)
        if ledger is None:
            ledger = _CandidateLedger(signature=signature, first_seen_time=int(time))
            ledger.on_samples = deque(maxlen=self.config.maximum_samples_each)
            ledger.off_samples = deque(maxlen=self.config.maximum_samples_each)
            self._ledgers[signature] = ledger
        return ledger

    def _posterior(
        self, ledger: _CandidateLedger
    ) -> tuple[float | None, float | None, float | None]:
        on = np.asarray(tuple(ledger.on_samples), dtype=np.float64)
        off = np.asarray(tuple(ledger.off_samples), dtype=np.float64)
        if len(on) == 0 or len(off) == 0:
            return None, None, None
        delta = float(np.mean(on) - np.mean(off))
        on_var = (
            float(np.var(on, ddof=1)) if len(on) > 1 else 0.0
        )
        off_var = (
            float(np.var(off, ddof=1)) if len(off) > 1 else 0.0
        )
        prior_var = self.config.prior_noise_scale**2
        standard_error = math.sqrt(
            (on_var + prior_var) / len(on)
            + (off_var + prior_var) / len(off)
        )
        lower = delta - self.config.confidence_z * standard_error
        upper = delta + self.config.confidence_z * standard_error
        return float(delta), float(lower), float(upper)

    def _information_gain(self, count: int) -> float:
        variance = self.config.prior_noise_scale**2
        before = variance / max(count, 1)
        after = variance / (count + 1)
        return float(max(0.0, before - after))

    def _workspace_expected(self, result: StepResult) -> bool:
        return bool(
            result.causal_boundary_state is not None
            and result.causal_boundary_state.active
            and result.causal_boundary_proposal_selected
            and "causal_boundary" in result.selected_specialists
            and float(np.linalg.norm(result.causal_boundary_workspace_drive))
            > 1e-12
            and "causal_boundary_broadcast" not in result.ablations
            and "broadcast" not in result.ablations
        )

    def plan(
        self,
        *,
        time: int,
        raw_certificate: PublicBoundaryCertificate | None,
        result: StepResult,
    ) -> _PendingGroundingPlan:
        """Choose the next diagnostic intervention without evaluator truth."""

        plan_events: list[str] = []
        raw_signature = (
            None
            if raw_certificate is None
            else raw_certificate.structural_signature
        )
        private_active = bool(
            result.causal_boundary_state is not None
            and result.causal_boundary_state.active
        )
        workspace_expected = self._workspace_expected(result)
        drive_norm = float(
            np.linalg.norm(result.causal_boundary_workspace_drive)
        )
        access_fault = bool(workspace_expected and raw_certificate is None)
        if access_fault:
            self._access_fault_streak += 1
        else:
            self._access_fault_streak = 0
            if self._access_fault_active and raw_certificate is not None:
                self._events.append(
                    {
                        "time": int(time),
                        "event": "access_path_restored",
                        "signature": raw_signature,
                    }
                )
                plan_events.append("access_path_restored")
                self._access_fault_active = False
        if self._access_fault_streak >= self.config.access_fault_confirmations:
            if not self._access_fault_active:
                self._events.append(
                    {
                        "time": int(time),
                        "event": "access_path_failure",
                        "signature": self._current_raw_signature,
                    }
                )
                plan_events.append("access_path_failure")
                self._access_fault_count += 1
            self._access_fault_active = True

        if raw_signature is None:
            self._current_raw_signature = None
            if self._ever_certified and not access_fault:
                self._absence_active = True
                if self._absence_started_time is None:
                    self._absence_started_time = int(time)
            return _PendingGroundingPlan(
                time=int(time),
                raw_signature=None,
                raw_certificate_digest=None,
                mode="access_fault" if access_fault else "no_candidate",
                requested_certificate_on=False,
                status_before=None,
                reason=(
                    "private boundary is active but the workspace-selected "
                    "candidate did not traverse the access path"
                    if access_fault
                    else "no workspace-selected causal candidate is available"
                ),
                private_boundary_active=private_active,
                workspace_candidate_selected=bool(
                    result.causal_boundary_proposal_selected
                ),
                workspace_drive_norm=drive_norm,
                access_update_count=int(result.causal_access_update_count),
                access_fault_suspected=access_fault,
                plan_events=tuple(plan_events),
            )

        if raw_signature != self._current_raw_signature:
            self._current_raw_signature = raw_signature
        ledger = self._ledger(raw_signature, time)
        delta, lower, upper = self._posterior(ledger)
        n_on = len(ledger.on_samples)
        n_off = len(ledger.off_samples)

        if ledger.status == "certified":
            due = (
                ledger.next_sentinel_time is None
                or int(time) >= ledger.next_sentinel_time
            )
            mode: ProbeMode = "sentinel" if due else "ordinary_use"
            requested_on = True
            reason = (
                "periodic consequence sentinel is due"
                if due
                else "candidate remains consequence-certified"
            )
            information_gain = 0.0
        elif ledger.status in {"rejected", "revoked"}:
            mode = "withheld"
            requested_on = False
            reason = f"candidate is {ledger.status} and remains fail-closed"
            information_gain = 0.0
        else:
            choose_on = bool(n_on <= n_off)
            if n_on >= self.config.maximum_samples_each:
                choose_on = False
            if n_off >= self.config.maximum_samples_each:
                choose_on = True
            mode = "probe_on" if choose_on else "probe_off"
            requested_on = choose_on
            target_count = n_on if choose_on else n_off
            information_gain = self._information_gain(target_count)
            reason = (
                "certificate-ON intervention maximizes expected reduction "
                "in causal-contrast uncertainty"
                if choose_on
                else "certificate-OFF intervention maximizes expected reduction "
                "in causal-contrast uncertainty"
            )

        return _PendingGroundingPlan(
            time=int(time),
            raw_signature=raw_signature,
            raw_certificate_digest=raw_certificate.digest,
            mode=mode,
            requested_certificate_on=requested_on,
            status_before=ledger.status,
            reason=reason,
            expected_information_gain=information_gain,
            on_count_before=n_on,
            off_count_before=n_off,
            posterior_delta_before=delta,
            lower_bound_before=lower,
            upper_bound_before=upper,
            private_boundary_active=private_active,
            workspace_candidate_selected=bool(
                result.causal_boundary_proposal_selected
            ),
            workspace_drive_norm=drive_norm,
            access_update_count=int(result.causal_access_update_count),
            access_fault_suspected=False,
            plan_events=tuple(plan_events),
        )

    def finalize_gate(
        self,
        plan: _PendingGroundingPlan,
        effective_certificate: PublicBoundaryCertificate | None,
    ) -> None:
        plan.actual_certificate_on = bool(effective_certificate is not None)

    def _expected_task_value(
        self, action: np.ndarray, context: np.ndarray
    ) -> float:
        return float(
            self.config.task_return_scale * np.dot(action, context)
            - self.config.action_cost * np.dot(action, action)
        )

    def diagnostic_candidates(
        self,
        plan: _PendingGroundingPlan,
        context: np.ndarray,
        candidates: tuple[ActionCandidate, ...],
    ) -> tuple[ActionCandidate, ...]:
        """Attach an epistemic bonus to the most informative public action."""

        if plan.mode not in {"probe_on", "probe_off", "sentinel"}:
            return candidates
        values = np.asarray(
            [
                self._expected_task_value(candidate.action, context)
                for candidate in candidates
            ],
            dtype=np.float64,
        )
        best_index = int(np.argmax(values))
        return tuple(
            replace(
                candidate,
                alternative_competence=(
                    max(
                        float(candidate.alternative_competence),
                        self.config.epistemic_action_bonus,
                    )
                    if index == best_index
                    else float(candidate.alternative_competence)
                ),
            )
            for index, candidate in enumerate(candidates)
        )

    def bind_selection(
        self,
        plan: _PendingGroundingPlan,
        selection: ActionSelectionReceipt,
    ) -> _PendingGroundingPlan:
        plan.selected_key = selection.selected_key
        plan.selected_action = np.asarray(
            selection.selected_action, dtype=np.float64
        ).copy()
        plan.observable_context = np.asarray(
            selection.observable_context, dtype=np.float64
        ).copy()
        plan.probe_opportunity = self._expected_task_value(
            plan.selected_action, plan.observable_context
        )
        if plan.mode in {"probe_on", "probe_off", "sentinel"}:
            self._probe_count += 1
        return plan

    def _transition_shift(
        self, transition_error: float, causal_signal_intact: bool
    ) -> bool:
        history = np.asarray(tuple(self._transition_errors), dtype=np.float64)
        shift = False
        if (
            causal_signal_intact
            and len(history) >= self.config.transition_minimum_baseline
        ):
            median = float(np.median(history))
            mad = float(np.median(np.abs(history - median)))
            scale = max(
                self.config.transition_spike_floor,
                self.config.transition_spike_z * 1.4826 * mad,
            )
            shift = bool(transition_error > median + scale)
        self._transition_errors.append(float(transition_error))
        return shift

    def _recommendation(
        self,
        *,
        diagnosis: str,
        status: GroundingStatus | None,
    ) -> str:
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
        if status == "certified":
            return "continue_boundary_mediated_action"
        if status in {"rejected", "revoked"}:
            return "withhold_boundary_dependent_action"
        return "continue_active_diagnostic_probing"

    def observe(
        self,
        plan: _PendingGroundingPlan,
        outcome: ActionOutcomeReceipt,
    ) -> GroundingOutcomeReceipt:
        """Update grounding only from the selected action and its consequence."""

        if plan.selected_key is None or plan.selected_action is None:
            raise RuntimeError("grounding plan was not bound to an action")
        if plan.observable_context is None or plan.probe_opportunity is None:
            raise RuntimeError("grounding plan has no observable action context")

        events: list[str] = list(plan.plan_events)
        ledger = (
            None
            if plan.raw_signature is None
            else self._ledger(plan.raw_signature, plan.time)
        )
        realized = outcome.realized_external_return
        informative = bool(
            plan.probe_opportunity >= self.config.minimum_probe_opportunity
            and realized is not None
        )
        normalized: float | None = None
        if informative and realized is not None:
            normalized = float(
                np.clip(realized / plan.probe_opportunity, -3.0, 3.0)
            )

        status_before = plan.status_before
        if (
            plan.mode in {"probe_on", "probe_off", "sentinel"}
            and informative
        ):
            self._informative_probe_count += 1
        if (
            ledger is not None
            and plan.mode in {"probe_on", "probe_off"}
            and informative
            and normalized is not None
            and plan.actual_certificate_on == plan.requested_certificate_on
        ):
            target = (
                ledger.on_samples
                if plan.actual_certificate_on
                else ledger.off_samples
            )
            target.append(normalized)
            ledger.last_evidence_time = int(outcome.reveal_time)

        if ledger is not None and plan.mode == "sentinel":
            if not plan.actual_certificate_on:
                # A downstream gate block is not evidence against the
                # candidate.  Keep the sentinel due and try again.
                ledger.next_sentinel_time = int(outcome.reveal_time)
                events.append("sentinel_deferred_gate_blocked")
            elif not informative or normalized is None:
                # An action with little positive task opportunity cannot
                # distinguish a connected certificate from a null gate.
                ledger.next_sentinel_time = int(outcome.reveal_time)
                events.append("sentinel_deferred_uninformative")
            elif normalized >= self.config.sentinel_failure_threshold:
                ledger.consecutive_sentinel_failures = 0
                ledger.next_sentinel_time = (
                    int(outcome.reveal_time) + self.config.sentinel_interval
                )
            else:
                ledger.consecutive_sentinel_failures += 1
                # A genuinely informative failure triggers immediate
                # confirmatory probing.
                ledger.next_sentinel_time = int(outcome.reveal_time)
                events.append("sentinel_failure")
                if (
                    ledger.consecutive_sentinel_failures
                    >= self.config.sentinel_failures_to_revoke
                    and ledger.status == "certified"
                ):
                    ledger.status = "revoked"
                    ledger.revoked_time = int(outcome.reveal_time)
                    self._revocation_count += 1
                    events.append("certificate_revoked_by_consequence")

        delta: float | None = None
        lower: float | None = None
        upper: float | None = None
        if ledger is not None:
            delta, lower, upper = self._posterior(ledger)
            n_on = len(ledger.on_samples)
            n_off = len(ledger.off_samples)
            if ledger.status == "unverified" and lower is not None:
                if (
                    n_on >= self.config.minimum_on_samples
                    and n_off >= self.config.minimum_off_samples
                    and lower >= self.config.certification_margin
                ):
                    ledger.status = "certified"
                    ledger.certified_time = int(outcome.reveal_time)
                    ledger.next_sentinel_time = (
                        int(outcome.reveal_time) + self.config.sentinel_interval
                    )
                    self._authorization_count += 1
                    self._ever_certified = True
                    absence_duration = (
                        None
                        if self._absence_started_time is None
                        else int(outcome.reveal_time)
                        - self._absence_started_time
                    )
                    if self._last_certified_signature is None:
                        events.append("initial_boundary_certified")
                    elif (
                        self._absence_active
                        and absence_duration is not None
                        and absence_duration
                        >= self.config.restoration_absence_threshold
                    ):
                        events.append("boundary_restored")
                    elif self._last_certified_signature != ledger.signature:
                        events.append("boundary_remapped")
                    else:
                        events.append("boundary_recertified")
                    self._absence_active = False
                    self._absence_event_emitted = False
                    self._absence_started_time = None
                    self._last_certified_signature = ledger.signature
                elif (
                    n_on >= self.config.rejection_samples_each
                    and n_off >= self.config.rejection_samples_each
                    and upper is not None
                    and upper <= self.config.rejection_margin
                ) or (
                    n_on >= self.config.maximum_samples_each
                    and n_off >= self.config.maximum_samples_each
                ):
                    ledger.status = "rejected"
                    ledger.rejected_time = int(outcome.reveal_time)
                    events.append("candidate_rejected_by_consequence")
            n_on_after = len(ledger.on_samples)
            n_off_after = len(ledger.off_samples)
            status_after: GroundingStatus | None = ledger.status
            sentinel_failures = ledger.consecutive_sentinel_failures
        else:
            n_on_after = 0
            n_off_after = 0
            status_after = None
            sentinel_failures = 0
            if self._ever_certified and not plan.access_fault_suspected:
                if not self._absence_event_emitted:
                    events.append("boundary_absent")
                    self._events.append(
                        {
                            "time": int(outcome.reveal_time),
                            "event": "boundary_absent",
                            "signature": self._last_certified_signature,
                        }
                    )
                    self._absence_event_emitted = True
                self._absence_active = True

        signal_intact = bool(
            normalized is not None
            and plan.actual_certificate_on
            and normalized >= self.config.sentinel_failure_threshold
        )
        if self._transition_shift(
            float(outcome.transition_prediction_error), signal_intact
        ):
            events.append("external_dynamics_shift")

        if "access_path_failure" in events or (
            plan.access_fault_suspected and self._access_fault_active
        ):
            diagnosis = "access_path_failure"
        elif "access_path_restored" in events:
            diagnosis = "access_path_restored"
        elif plan.access_fault_suspected:
            diagnosis = "access_path_under_test"
        elif "boundary_absent" in events or (
            plan.mode == "no_candidate" and self._ever_certified
        ):
            diagnosis = "boundary_absent"
        elif "certificate_revoked_by_consequence" in events:
            diagnosis = "boundary_effect_failed"
        elif "boundary_remapped" in events:
            diagnosis = "boundary_remapped"
        elif "boundary_restored" in events:
            diagnosis = "boundary_restored"
        elif "external_dynamics_shift" in events:
            diagnosis = "external_dynamics_shift"
        elif status_after == "certified":
            diagnosis = "boundary_operational"
        elif status_after in {"rejected", "revoked"}:
            diagnosis = "boundary_unusable"
        elif plan.raw_signature is not None:
            diagnosis = "boundary_under_test"
        else:
            diagnosis = "boundary_unknown"

        recommendation = self._recommendation(
            diagnosis=diagnosis, status=status_after
        )
        for event in events:
            if event not in {
                "sentinel_failure",
                "access_path_failure",
                "access_path_restored",
            }:
                self._events.append(
                    {
                        "time": int(outcome.reveal_time),
                        "event": event,
                        "signature": plan.raw_signature,
                        "diagnosis": diagnosis,
                        "recommended_response": recommendation,
                    }
                )

        payload = {
            "schema": "rrct.v039.grounding_outcome.v1",
            "time": plan.time,
            "raw_signature": plan.raw_signature,
            "raw_certificate_digest": plan.raw_certificate_digest,
            "mode": plan.mode,
            "requested_certificate_on": plan.requested_certificate_on,
            "actual_certificate_on": plan.actual_certificate_on,
            "status_before": status_before,
            "status_after": status_after,
            "reason": plan.reason,
            "expected_information_gain": plan.expected_information_gain,
            "selected_key": plan.selected_key,
            "selected_action": tuple(float(x) for x in plan.selected_action),
            "observable_context": tuple(
                float(x) for x in plan.observable_context
            ),
            "probe_opportunity": float(plan.probe_opportunity),
            "informative_probe": informative,
            "realized_external_return": realized,
            "normalized_causal_signal": normalized,
            "on_count_before": plan.on_count_before,
            "off_count_before": plan.off_count_before,
            "on_count_after": n_on_after,
            "off_count_after": n_off_after,
            "posterior_delta": delta,
            "lower_bound": lower,
            "upper_bound": upper,
            "consecutive_sentinel_failures": sentinel_failures,
            "transition_prediction_error": outcome.transition_prediction_error,
            "events": tuple(events),
            "diagnosis": diagnosis,
            "recommended_response": recommendation,
            "private_boundary_active": plan.private_boundary_active,
            "workspace_candidate_selected": plan.workspace_candidate_selected,
            "workspace_drive_norm": plan.workspace_drive_norm,
            "access_update_count": plan.access_update_count,
            "uses_evaluator_labels": False,
        }
        receipt = GroundingOutcomeReceipt(
            time=int(plan.time),
            raw_signature=plan.raw_signature,
            raw_certificate_digest=plan.raw_certificate_digest,
            mode=plan.mode,
            requested_certificate_on=bool(plan.requested_certificate_on),
            actual_certificate_on=bool(plan.actual_certificate_on),
            status_before=status_before,
            status_after=status_after,
            reason=plan.reason,
            expected_information_gain=float(plan.expected_information_gain),
            selected_key=plan.selected_key,
            selected_action=tuple(float(x) for x in plan.selected_action),
            observable_context=tuple(
                float(x) for x in plan.observable_context
            ),
            probe_opportunity=float(plan.probe_opportunity),
            informative_probe=informative,
            realized_external_return=(
                None if realized is None else float(realized)
            ),
            normalized_causal_signal=normalized,
            on_count_before=int(plan.on_count_before),
            off_count_before=int(plan.off_count_before),
            on_count_after=int(n_on_after),
            off_count_after=int(n_off_after),
            posterior_delta=delta,
            lower_bound=lower,
            upper_bound=upper,
            consecutive_sentinel_failures=int(sentinel_failures),
            transition_prediction_error=float(
                outcome.transition_prediction_error
            ),
            events=tuple(events),
            diagnosis=diagnosis,
            recommended_response=recommendation,
            private_boundary_active=bool(plan.private_boundary_active),
            workspace_candidate_selected=bool(
                plan.workspace_candidate_selected
            ),
            workspace_drive_norm=float(plan.workspace_drive_norm),
            access_update_count=int(plan.access_update_count),
            uses_evaluator_labels=False,
            digest=_digest(payload),
        )
        return receipt

    def snapshot(self) -> dict[str, Any]:
        ledgers: list[dict[str, Any]] = []
        for signature in sorted(self._ledgers, key=repr):
            ledger = self._ledgers[signature]
            delta, lower, upper = self._posterior(ledger)
            ledgers.append(
                {
                    "signature": signature,
                    "first_seen_time": ledger.first_seen_time,
                    "status": ledger.status,
                    "on_samples": tuple(ledger.on_samples),
                    "off_samples": tuple(ledger.off_samples),
                    "posterior_delta": delta,
                    "lower_bound": lower,
                    "upper_bound": upper,
                    "certified_time": ledger.certified_time,
                    "rejected_time": ledger.rejected_time,
                    "revoked_time": ledger.revoked_time,
                    "next_sentinel_time": ledger.next_sentinel_time,
                    "consecutive_sentinel_failures": (
                        ledger.consecutive_sentinel_failures
                    ),
                    "last_evidence_time": ledger.last_evidence_time,
                }
            )
        payload: dict[str, Any] = {
            "schema": "rrct.v039.consequence_grounded_access.v1",
            "config": self.config,
            "ledgers": tuple(ledgers),
            "current_raw_signature": self._current_raw_signature,
            "last_certified_signature": self._last_certified_signature,
            "ever_certified": self._ever_certified,
            "absence_active": self._absence_active,
            "absence_started_time": self._absence_started_time,
            "access_fault_active": self._access_fault_active,
            "access_fault_streak": self._access_fault_streak,
            "transition_errors": tuple(self._transition_errors),
            "events": tuple(copy.deepcopy(self._events)),
            "probe_count": self._probe_count,
            "informative_probe_count": self._informative_probe_count,
            "authorization_count": self._authorization_count,
            "revocation_count": self._revocation_count,
            "access_fault_count": self._access_fault_count,
            "uses_evaluator_labels": False,
        }
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)


class AutonomousDiagnosticUnifiedCausalLoop(UnifiedCausalLoop):
    """Unified loop whose public certificate is grounded by active probes."""

    def __init__(
        self,
        agent: RRCTAgent,
        config: UnifiedCausalLoopConfig | None = None,
        *,
        grounding_config: ConsequenceGroundingConfig | None = None,
    ) -> None:
        super().__init__(agent, config)
        self.grounding = ConsequenceGroundedAccessController(
            grounding_config
        )
        self._current_grounding_plan: _PendingGroundingPlan | None = None
        self._pending_grounding_plan: _PendingGroundingPlan | None = None
        self._last_grounding_outcome: GroundingOutcomeReceipt | None = None

    @property
    def last_grounding_outcome(self) -> GroundingOutcomeReceipt | None:
        return copy.deepcopy(self._last_grounding_outcome)

    @property
    def grounding_snapshot(self) -> dict[str, Any]:
        return self.grounding.snapshot()

    def _complete_previous(
        self,
        next_observation: np.ndarray,
        realized_external_return: float | None,
    ) -> tuple[
        ActionOutcomeReceipt | None,
        RandomizedTransitionRow | None,
        DriftAssessment | None,
    ]:
        pending_plan = self._pending_grounding_plan
        outcome, row, drift = super()._complete_previous(
            next_observation, realized_external_return
        )
        if outcome is None:
            if pending_plan is not None:
                raise RuntimeError("grounding plan exists without pending outcome")
            self._last_grounding_outcome = None
        else:
            if pending_plan is None:
                raise RuntimeError("pending action has no grounding plan")
            self._last_grounding_outcome = self.grounding.observe(
                pending_plan, outcome
            )
        self._pending_grounding_plan = None
        return outcome, row, drift

    def _public_certificate(
        self, result: StepResult
    ) -> PublicBoundaryCertificate | None:
        raw = super()._public_certificate(result)
        plan = self.grounding.plan(
            time=result.time,
            raw_certificate=raw,
            result=result,
        )
        self._current_grounding_plan = plan
        return raw if plan.requested_certificate_on else None

    def _gate_public_certificate(
        self,
        *,
        time: int,
        raw_certificate: PublicBoundaryCertificate | None,
        drift: DriftAssessment | None,
    ) -> tuple[PublicBoundaryCertificate | None, PublicBoundaryGateReceipt]:
        effective, receipt = super()._gate_public_certificate(
            time=time,
            raw_certificate=raw_certificate,
            drift=drift,
        )
        if self._current_grounding_plan is None:
            raise RuntimeError("public gate has no grounding plan")
        self.grounding.finalize_gate(
            self._current_grounding_plan, effective
        )
        return effective, receipt

    def _select_action(
        self,
        *,
        time: int,
        observation: np.ndarray,
        context: np.ndarray,
        candidates: tuple[ActionCandidate, ...],
        certificate: PublicBoundaryCertificate | None,
    ) -> ActionSelectionReceipt:
        plan = self._current_grounding_plan
        if plan is None:
            raise RuntimeError("action selection has no grounding plan")
        diagnostic_candidates = self.grounding.diagnostic_candidates(
            plan, context, candidates
        )
        selection = super()._select_action(
            time=time,
            observation=observation,
            context=context,
            candidates=diagnostic_candidates,
            certificate=certificate,
        )
        self._pending_grounding_plan = self.grounding.bind_selection(
            plan, selection
        )
        self._current_grounding_plan = None
        return selection

    def snapshot(self) -> dict[str, Any]:
        payload = super().snapshot()
        payload["autonomous_grounding"] = self.grounding.snapshot()
        payload["last_grounding_outcome"] = copy.deepcopy(
            self._last_grounding_outcome
        )
        payload["autonomous_grounding_digest"] = _digest(
            {
                "autonomous_grounding": payload["autonomous_grounding"],
                "last_grounding_outcome": payload["last_grounding_outcome"],
            }
        )
        return payload


__all__ = [
    "AutonomousDiagnosticUnifiedCausalLoop",
    "ConsequenceGroundedAccessController",
    "ConsequenceGroundingConfig",
    "GroundingOutcomeReceipt",
    "validate_grounding_outcome_receipt",
]
