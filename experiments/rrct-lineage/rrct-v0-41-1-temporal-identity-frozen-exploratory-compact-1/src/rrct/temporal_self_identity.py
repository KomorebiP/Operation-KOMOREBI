"""Temporal causal self-identity and memory-guided revalidation for RRCT v0.41.

RRCT v0.39 grounds each public causal certificate from self-selected
consequences. RRCT v0.40 separates external world change from failure of that
causal interface. This module adds a bounded temporal identity layer that asks
whether a newly exposed route is novel or a return of a previously grounded
causal-route class.

The temporal controller never receives evaluator phase names, planted route
truth, hidden source labels, or future outcomes. It canonicalizes the publicly
available structural route ``(pair, rank)`` while preserving every certificate
epoch as a distinct episode.  Canonical identity is not granted by that
structural key alone: a freshly grounded ON/OFF consequence fingerprint must
also match a prior episode.  A remembered identity contributes only a bounded
historical ON/OFF prior, and the first fresh ON/OFF evidence must agree with it
before it remains on the action path.  Certificate digests and epochs are never
reused.
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

from .agent import RRCTAgent, StepResult
from .autonomous_self_diagnosis import (
    ConsequenceGroundedAccessController,
    ConsequenceGroundingConfig,
    GroundingOutcomeReceipt,
    Signature,
    validate_grounding_outcome_receipt,
)
from .robust_reflexive_diagnosis import (
    ReflexiveDiagnosisReceipt,
    RobustReflexiveDiagnosisConfig,
    RobustReflexiveDiagnosticUnifiedCausalLoop,
    validate_reflexive_diagnosis_receipt,
)
from .unified_causal_loop import (
    ActionOutcomeReceipt,
    DriftAssessment,
    PublicBoundaryCertificate,
    PublicBoundaryGateReceipt,
    UnifiedCausalLoop,
    UnifiedCausalLoopConfig,
)

CanonicalKey = tuple[tuple[int, int], int]
CandidateClass = Literal["none", "novel", "known"]
HistoryPolicy = Literal["keyed", "withheld", "generic"]
TemporalDiagnosis = Literal[
    "novel_identity_candidate",
    "known_identity_candidate",
    "novel_identity_grounded",
    "known_identity_returned",
    "identity_episode_revoked",
    "identity_absent",
    "identity_access_interrupted",
    "identity_access_restored",
    "identity_candidate_visibility_interrupted",
    "identity_candidate_visibility_restored",
    "identity_reconstruction_pending",
    "identity_continuity_retained",
    "stale_identity_reuse_detected",
    "premature_identity_authorization_detected",
    "identity_prior_integrity_failure",
    "identity_unknown",
]


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set)):
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


def _canonical_key(signature: Signature | None) -> CanonicalKey | None:
    if signature is None:
        return None
    pair, rank, _epoch = signature
    return (tuple(int(value) for value in pair), int(rank))


def _valid_signature(signature: Any) -> bool:
    if not isinstance(signature, tuple) or len(signature) != 3:
        return False
    pair, rank, epoch = signature
    if not isinstance(pair, tuple) or len(pair) != 2:
        return False
    values = (*pair, rank, epoch)
    return all(
        not isinstance(value, (bool, np.bool_))
        and isinstance(value, (int, np.integer))
        and int(value) >= 0
        for value in values
    )


def _valid_digest(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def temporal_action_authorization_digest(
    signature: Signature,
    certificate_digest: str,
    identity_id: str,
    episode_id: str,
) -> str:
    """Commit the exact temporal episode that authorizes one action path."""

    return _digest(
        {
            "schema": "rrct.v041.temporal_action_authorization.v1",
            "signature": signature,
            "certificate_digest": certificate_digest,
            "identity_id": identity_id,
            "episode_id": episode_id,
            "uses_evaluator_labels": False,
        }
    )


def _target_epoch_binding_digest(signature: Signature) -> str:
    return _digest(
        {
            "schema": "rrct.v041.target_epoch_binding.v1",
            "target_signature": signature,
        }
    )


@dataclass(frozen=True)
class TemporalSelfIdentityConfig:
    """Predeclared temporal-identity safety requirements."""

    minimum_novel_fresh_on_samples: int = 2
    minimum_novel_fresh_off_samples: int = 2
    minimum_return_fresh_on_samples: int = 1
    minimum_return_fresh_off_samples: int = 1
    historical_prior_samples_each: int = 1
    historical_prior_enabled: bool = True
    history_policy: HistoryPolicy = "keyed"
    historical_compatibility_tolerance: float = 0.25

    def __post_init__(self) -> None:
        if not isinstance(self.historical_prior_enabled, (bool, np.bool_)):
            raise TypeError("historical_prior_enabled must be a boolean")
        object.__setattr__(
            self,
            "historical_prior_enabled",
            bool(self.historical_prior_enabled),
        )
        if self.history_policy not in {"keyed", "withheld", "generic"}:
            raise ValueError("history_policy must be keyed, withheld, or generic")
        if not self.historical_prior_enabled:
            object.__setattr__(self, "history_policy", "withheld")
        tolerance = float(self.historical_compatibility_tolerance)
        if not np.isfinite(tolerance) or tolerance <= 0.0:
            raise ValueError(
                "historical_compatibility_tolerance must be positive and finite"
            )
        object.__setattr__(
            self, "historical_compatibility_tolerance", tolerance
        )
        names = (
            "minimum_novel_fresh_on_samples",
            "minimum_novel_fresh_off_samples",
            "minimum_return_fresh_on_samples",
            "minimum_return_fresh_off_samples",
            "historical_prior_samples_each",
        )
        for name in names:
            value = getattr(self, name)
            if isinstance(value, (bool, np.bool_)) or not isinstance(
                value, (int, np.integer)
            ):
                raise TypeError(f"{name} must be a positive integer")
            parsed = int(value)
            if parsed <= 0:
                raise ValueError(f"{name} must be a positive integer")
            object.__setattr__(self, name, parsed)
        if self.historical_prior_samples_each != 1:
            raise ValueError(
                "v0.41 permits exactly one bounded historical sample per arm"
            )


@dataclass(frozen=True)
class HistoricalGroundingPriorReceipt:
    """Evaluator-blind bounded prior copied from one earlier grounded epoch."""

    schema: str
    target_signature: Signature
    source_signature: Signature
    target_epoch_binding_digest: str
    source_identity_id: str
    source_episode_id: str
    source_evidence_digest: str
    history_policy: Literal["keyed", "generic"]
    seeded_time: int
    source_certified_time: int
    on_value: float
    off_value: float
    prior_on_count: int
    prior_off_count: int
    uses_evaluator_labels: bool
    digest: str


def _prior_payload(receipt: HistoricalGroundingPriorReceipt) -> dict[str, Any]:
    return {
        "schema": receipt.schema,
        "target_signature": receipt.target_signature,
        "source_signature": receipt.source_signature,
        "target_epoch_binding_digest": receipt.target_epoch_binding_digest,
        "source_identity_id": receipt.source_identity_id,
        "source_episode_id": receipt.source_episode_id,
        "source_evidence_digest": receipt.source_evidence_digest,
        "history_policy": receipt.history_policy,
        "seeded_time": receipt.seeded_time,
        "source_certified_time": receipt.source_certified_time,
        "on_value": receipt.on_value,
        "off_value": receipt.off_value,
        "prior_on_count": receipt.prior_on_count,
        "prior_off_count": receipt.prior_off_count,
        "uses_evaluator_labels": receipt.uses_evaluator_labels,
    }


def validate_historical_grounding_prior_receipt(
    receipt: HistoricalGroundingPriorReceipt,
) -> bool:
    if not isinstance(receipt, HistoricalGroundingPriorReceipt):
        return False
    if receipt.schema != "rrct.v041.historical_grounding_prior.v3":
        return False
    if not isinstance(receipt.uses_evaluator_labels, (bool, np.bool_)):
        return False
    if receipt.uses_evaluator_labels:
        return False
    if receipt.history_policy not in {"keyed", "generic"}:
        return False
    if not _valid_signature(receipt.target_signature) or not _valid_signature(
        receipt.source_signature
    ):
        return False
    try:
        target_key = _canonical_key(receipt.target_signature)
        source_key = _canonical_key(receipt.source_signature)
    except (TypeError, ValueError):
        return False
    if target_key is None or source_key is None:
        return False
    same_key = target_key == source_key
    if receipt.history_policy == "keyed" and not same_key:
        return False
    # The generic control deliberately ignores identity when choosing its
    # source.  It may therefore happen to select either the same or a different
    # structural key; only exact target-epoch reuse is forbidden below.
    if receipt.target_signature == receipt.source_signature:
        return False
    for value in (
        receipt.target_epoch_binding_digest,
        receipt.source_evidence_digest,
    ):
        if not _valid_digest(value):
            return False
    if (
        not isinstance(receipt.source_identity_id, str)
        or not receipt.source_identity_id
        or not isinstance(receipt.source_episode_id, str)
        or not receipt.source_episode_id
    ):
        return False
    if receipt.target_epoch_binding_digest != _target_epoch_binding_digest(
        receipt.target_signature
    ):
        return False
    if (
        isinstance(receipt.prior_on_count, (bool, np.bool_))
        or not isinstance(receipt.prior_on_count, (int, np.integer))
        or isinstance(receipt.prior_off_count, (bool, np.bool_))
        or not isinstance(receipt.prior_off_count, (int, np.integer))
        or receipt.prior_on_count != 1
        or receipt.prior_off_count != 1
    ):
        return False
    if (
        isinstance(receipt.seeded_time, (bool, np.bool_))
        or not isinstance(receipt.seeded_time, (int, np.integer))
        or isinstance(receipt.source_certified_time, (bool, np.bool_))
        or not isinstance(receipt.source_certified_time, (int, np.integer))
        or int(receipt.seeded_time) < 0
        or int(receipt.source_certified_time) < 0
        or int(receipt.source_certified_time) >= int(receipt.seeded_time)
    ):
        return False
    if (
        isinstance(receipt.on_value, (bool, np.bool_))
        or isinstance(receipt.off_value, (bool, np.bool_))
        or not np.isfinite(receipt.on_value)
        or not np.isfinite(receipt.off_value)
    ):
        return False
    return bool(receipt.digest == _digest(_prior_payload(receipt)))


class TemporalPriorConsequenceGroundedAccessController(
    ConsequenceGroundedAccessController
):
    """v0.39 grounder with a bounded, consequence-only return prior."""

    PRIOR_SCHEMA = "rrct.v041.historical_grounding_prior.v3"

    def __init__(
        self,
        config: ConsequenceGroundingConfig | None = None,
        *,
        historical_prior_enabled: bool = True,
        historical_compatibility_tolerance: float = 0.25,
    ) -> None:
        super().__init__(config)
        if not isinstance(historical_prior_enabled, (bool, np.bool_)):
            raise TypeError("historical_prior_enabled must be a boolean")
        self.historical_prior_enabled = bool(historical_prior_enabled)
        tolerance = float(historical_compatibility_tolerance)
        if not np.isfinite(tolerance) or tolerance <= 0.0:
            raise ValueError(
                "historical_compatibility_tolerance must be positive and finite"
            )
        self.historical_compatibility_tolerance = tolerance
        self._historical_priors: dict[
            Signature, HistoricalGroundingPriorReceipt
        ] = {}
        self._historical_prior_compatibility: dict[Signature, str] = {}
        self._historical_prior_quarantine_count = 0
        self._candidate_visibility_gap_signature: Signature | None = None

    def apply_historical_prior(
        self,
        raw_certificate: PublicBoundaryCertificate,
        prior: HistoricalGroundingPriorReceipt | None,
        *,
        time: int,
    ) -> HistoricalGroundingPriorReceipt | None:
        """Apply only a temporal-controller-issued prior to a new epoch.

        The grounder deliberately performs no cross-epoch ledger search.  A
        historical contribution can enter the action path only through a
        source-bound temporal-identity receipt.
        """

        if not self.historical_prior_enabled or prior is None:
            return None
        signature = raw_certificate.structural_signature
        if not validate_historical_grounding_prior_receipt(prior):
            raise ValueError("historical grounding prior failed validation")
        if prior.target_signature != signature:
            raise ValueError("historical grounding prior targets another epoch")
        if prior.target_epoch_binding_digest != _target_epoch_binding_digest(
            signature
        ):
            raise ValueError("historical grounding prior targets another epoch")
        existing = self._historical_priors.get(signature)
        if existing is not None:
            if existing.digest != prior.digest:
                raise RuntimeError("conflicting historical priors target one epoch")
            return existing
        if int(prior.seeded_time) != int(time):
            raise ValueError("historical grounding prior was not issued now")
        target = self._ledger(signature, int(time))
        if target.on_samples or target.off_samples:
            return None
        target.on_samples.append(float(prior.on_value))
        target.off_samples.append(float(prior.off_value))
        self._historical_priors[signature] = copy.deepcopy(prior)
        self._historical_prior_compatibility[signature] = "pending"
        return copy.deepcopy(prior)

    def prior_for(
        self, signature: Signature | None
    ) -> HistoricalGroundingPriorReceipt | None:
        if signature is None:
            return None
        if self._historical_prior_compatibility.get(signature) == "quarantined":
            return None
        return copy.deepcopy(self._historical_priors.get(signature))

    def compatibility_for(self, signature: Signature | None) -> str | None:
        if signature is None:
            return None
        return self._historical_prior_compatibility.get(signature)

    def registered_prior_for(
        self, signature: Signature | None
    ) -> HistoricalGroundingPriorReceipt | None:
        if signature is None:
            return None
        return copy.deepcopy(self._historical_priors.get(signature))

    def can_accept_historical_prior(self, signature: Signature) -> bool:
        if signature in self._historical_priors:
            return False
        ledger = self._ledgers.get(signature)
        return bool(
            ledger is None
            or (not ledger.on_samples and not ledger.off_samples)
        )

    def force_revalidation(
        self,
        signature: Signature,
        *,
        time: int,
        reason: str,
    ) -> None:
        """Fail closed when a lower certificate lacks temporal authority."""

        ledger = self._ledger(signature, int(time))
        ledger.status = "unverified"
        ledger.on_samples.clear()
        ledger.off_samples.clear()
        ledger.certified_time = None
        ledger.next_sentinel_time = None
        ledger.consecutive_sentinel_failures = 0
        if signature in self._historical_priors:
            self._historical_prior_compatibility[signature] = "quarantined"
        self._events.append(
            {
                "time": int(time),
                "event": "temporal_authorization_missing_revalidation_forced",
                "signature": signature,
                "reason": str(reason),
            }
        )

    def observe(
        self,
        plan,
        outcome: ActionOutcomeReceipt,
    ) -> GroundingOutcomeReceipt:
        """Quarantine incompatible history before it can certify a return."""

        signature = plan.raw_signature
        prior = (
            None if signature is None else self._historical_priors.get(signature)
        )
        compatibility = (
            None
            if signature is None
            else self._historical_prior_compatibility.get(signature)
        )
        if (
            prior is not None
            and compatibility == "pending"
            and plan.mode in {"probe_on", "probe_off"}
            and plan.probe_opportunity is not None
            and plan.probe_opportunity >= self.config.minimum_probe_opportunity
            and outcome.realized_external_return is not None
            and plan.actual_certificate_on == plan.requested_certificate_on
        ):
            normalized = float(
                np.clip(
                    outcome.realized_external_return / plan.probe_opportunity,
                    -3.0,
                    3.0,
                )
            )
            ledger = self._ledger(signature, plan.time)
            target = prior.on_value if plan.actual_certificate_on else prior.off_value
            compatible = bool(
                abs(normalized - float(target))
                <= self.historical_compatibility_tolerance
            )
            marker = "on" if plan.actual_certificate_on else "off"
            self._historical_prior_compatibility[signature] = (
                f"{marker}_compatible" if compatible else "quarantined"
            )
            if not compatible:
                if ledger.on_samples:
                    ledger.on_samples.popleft()
                if ledger.off_samples:
                    ledger.off_samples.popleft()
                self._historical_prior_quarantine_count += 1
            elif marker == "off":
                self._historical_prior_compatibility[signature] = "compatible"
        elif prior is not None and compatibility == "on_compatible" and (
            plan.mode == "probe_off"
            and plan.probe_opportunity is not None
            and plan.probe_opportunity >= self.config.minimum_probe_opportunity
            and outcome.realized_external_return is not None
            and plan.actual_certificate_on == plan.requested_certificate_on
        ):
            normalized = float(
                np.clip(
                    outcome.realized_external_return / plan.probe_opportunity,
                    -3.0,
                    3.0,
                )
            )
            ledger = self._ledger(signature, plan.time)
            compatible = bool(
                abs(normalized - float(prior.off_value))
                <= self.historical_compatibility_tolerance
            )
            if compatible:
                self._historical_prior_compatibility[signature] = "compatible"
            else:
                if ledger.on_samples:
                    ledger.on_samples.popleft()
                if ledger.off_samples:
                    ledger.off_samples.popleft()
                self._historical_prior_compatibility[signature] = "quarantined"
                self._historical_prior_quarantine_count += 1
        receipt = super().observe(plan, outcome)
        return receipt

    def plan(
        self,
        *,
        time: int,
        raw_certificate: PublicBoundaryCertificate | None,
        result: StepResult,
    ):
        """Preserve a certified route across a transient workspace miss.

        The inherited v0.39 grounder correctly fails closed whenever no raw
        workspace candidate is available.  It originally treated even a
        one-row candidate-selection miss as boundary absence and retained that
        absence latch until a new certification event.  Temporal identity must
        instead distinguish loss of *candidate visibility* from loss of causal
        efficacy.  When the same still-certified signature becomes visible
        again, clear only the inherited absence latch and emit an auditable
        restoration event.  No action is authorized during the missing row,
        no evidence is fabricated, and the next scheduled consequence
        sentinel still tests the route.
        """

        if raw_certificate is None:
            private_active = bool(
                result.causal_boundary_state is not None
                and result.causal_boundary_state.active
            )
            access_fault = bool(self._workspace_expected(result))
            if private_active and not access_fault:
                self._candidate_visibility_gap_signature = (
                    self._last_certified_signature
                )
            elif not private_active:
                self._candidate_visibility_gap_signature = None

        plan = super().plan(
            time=int(time),
            raw_certificate=raw_certificate,
            result=result,
        )
        signature = (
            None
            if raw_certificate is None
            else raw_certificate.structural_signature
        )
        if (
            signature is not None
            and self._absence_active
            and plan.status_before == "certified"
            and signature == self._last_certified_signature
            and signature == self._candidate_visibility_gap_signature
        ):
            plan.plan_events = tuple(plan.plan_events) + (
                "boundary_candidate_visibility_restored",
            )
            self._absence_active = False
            self._absence_event_emitted = False
            self._absence_started_time = None
            self._candidate_visibility_gap_signature = None
        return plan

    def snapshot(self) -> dict[str, Any]:
        payload = super().snapshot()
        inherited_digest = payload.pop("digest", None)
        priors = tuple(
            self._historical_priors[signature]
            for signature in sorted(self._historical_priors, key=repr)
        )
        payload["temporal_historical_priors"] = copy.deepcopy(priors)
        payload["temporal_historical_prior_count"] = len(priors)
        payload["temporal_historical_priors_use_evaluator_labels"] = False
        payload["temporal_historical_prior_enabled"] = (
            self.historical_prior_enabled
        )
        payload["temporal_historical_prior_compatibility"] = copy.deepcopy(
            self._historical_prior_compatibility
        )
        payload["temporal_historical_prior_quarantine_count"] = int(
            self._historical_prior_quarantine_count
        )
        payload["candidate_visibility_gap_signature"] = (
            self._candidate_visibility_gap_signature
        )
        payload["temporal_historical_prior_digest"] = _digest(
            {
                "priors": priors,
                "uses_evaluator_labels": False,
            }
        )
        payload["inherited_grounding_controller_digest"] = inherited_digest
        payload["digest"] = _digest(payload)
        return payload


@dataclass
class _CanonicalIdentity:
    canonical_id: str
    key: CanonicalKey
    prototype_on_mean: float
    prototype_off_mean: float
    first_grounded_time: int
    last_grounded_time: int
    episode_ids: list[str] = field(default_factory=list)
    return_count: int = 0


@dataclass
class _IdentityEpisode:
    episode_id: str
    canonical_id: str
    canonical_key: CanonicalKey
    raw_signature: Signature
    certificate_digest: str
    recognized_time: int
    grounded_time: int
    recognition_class: CandidateClass
    grounding_digest: str
    total_on_samples: int
    total_off_samples: int
    fresh_on_samples: int
    fresh_off_samples: int
    historical_prior_used: bool
    historical_prior_digest: str | None
    prior_source_episode_id: str | None
    fresh_grounding_satisfied: bool
    fresh_on_mean: float
    fresh_off_mean: float
    fresh_evidence_digest: str
    fresh_evidence_rows: tuple[int, ...]
    closed_time: int | None = None
    close_reason: str | None = None


@dataclass(frozen=True)
class TemporalIdentityReceipt:
    """One evaluator-blind temporal self-identity audit record."""

    schema: str
    time: int
    inherited_grounding_digest: str
    inherited_reflexive_digest: str
    historical_prior_digest: str | None
    historical_prior_source_signature: Signature | None
    historical_prior_valid: bool
    raw_signature: Signature | None
    raw_certificate_digest: str | None
    canonical_key: CanonicalKey | None
    candidate_classification: CandidateClass
    candidate_recognition_time: int | None
    active_identity_before: str | None
    active_identity_after: str | None
    active_episode_before: str | None
    active_episode_after: str | None
    canonical_identity_count: int
    identity_episode_count: int
    fresh_grounding_event: bool
    fresh_on_samples: int
    fresh_off_samples: int
    fresh_grounding_satisfied: bool
    stale_certificate_reuse_detected: bool
    premature_ordinary_authorization_detected: bool
    events: tuple[str, ...]
    inherited_diagnosis: str
    diagnosis: TemporalDiagnosis
    recommended_response: str
    uses_evaluator_labels: bool
    digest: str


def _receipt_payload(receipt: TemporalIdentityReceipt) -> dict[str, Any]:
    return {
        "schema": receipt.schema,
        "time": receipt.time,
        "inherited_grounding_digest": receipt.inherited_grounding_digest,
        "inherited_reflexive_digest": receipt.inherited_reflexive_digest,
        "historical_prior_digest": receipt.historical_prior_digest,
        "historical_prior_source_signature": (
            receipt.historical_prior_source_signature
        ),
        "historical_prior_valid": receipt.historical_prior_valid,
        "raw_signature": receipt.raw_signature,
        "raw_certificate_digest": receipt.raw_certificate_digest,
        "canonical_key": receipt.canonical_key,
        "candidate_classification": receipt.candidate_classification,
        "candidate_recognition_time": receipt.candidate_recognition_time,
        "active_identity_before": receipt.active_identity_before,
        "active_identity_after": receipt.active_identity_after,
        "active_episode_before": receipt.active_episode_before,
        "active_episode_after": receipt.active_episode_after,
        "canonical_identity_count": receipt.canonical_identity_count,
        "identity_episode_count": receipt.identity_episode_count,
        "fresh_grounding_event": receipt.fresh_grounding_event,
        "fresh_on_samples": receipt.fresh_on_samples,
        "fresh_off_samples": receipt.fresh_off_samples,
        "fresh_grounding_satisfied": receipt.fresh_grounding_satisfied,
        "stale_certificate_reuse_detected": (
            receipt.stale_certificate_reuse_detected
        ),
        "premature_ordinary_authorization_detected": (
            receipt.premature_ordinary_authorization_detected
        ),
        "events": receipt.events,
        "inherited_diagnosis": receipt.inherited_diagnosis,
        "diagnosis": receipt.diagnosis,
        "recommended_response": receipt.recommended_response,
        "uses_evaluator_labels": receipt.uses_evaluator_labels,
    }


def validate_temporal_identity_receipt(receipt: TemporalIdentityReceipt) -> bool:
    if not isinstance(receipt, TemporalIdentityReceipt):
        return False
    if receipt.schema != "rrct.v041.temporal_identity.v2":
        return False
    if receipt.uses_evaluator_labels:
        return False
    return bool(receipt.digest == _digest(_receipt_payload(receipt)))


class TemporalSelfIdentityController:
    """Maintain canonical route identities and freshly grounded episodes."""

    SCHEMA = "rrct.v041.temporal_identity.v2"
    _GROUNDING_EVENTS = {
        "initial_boundary_certified",
        "boundary_remapped",
        "boundary_restored",
        "boundary_recertified",
    }

    def __init__(self, config: TemporalSelfIdentityConfig | None = None) -> None:
        self.config = config or TemporalSelfIdentityConfig()
        if not isinstance(self.config, TemporalSelfIdentityConfig):
            raise TypeError("config must be a TemporalSelfIdentityConfig")
        # More than one functional identity may share a structural route key.
        # This is essential for the same-key/changed-function lure: dropping a
        # certificate epoch is a candidate-generation rule, not an identity
        # equivalence oracle.
        self._registry: dict[str, _CanonicalIdentity] = {}
        self._episodes: list[_IdentityEpisode] = []
        self._seen_raw_signatures: set[Signature] = set()
        self._recognitions: dict[Signature, tuple[int, CandidateClass]] = {}
        self._fresh_evidence: dict[
            Signature, dict[str, list[tuple[int, float]]]
        ] = {}
        self._issued_historical_priors: dict[
            Signature, HistoricalGroundingPriorReceipt
        ] = {}
        self._active_identity_id: str | None = None
        self._active_episode_id: str | None = None
        self._active_raw_signature: Signature | None = None
        self._active_certificate_digest: str | None = None
        self._retired_epoch_bindings: set[str] = set()
        self._event_log: list[dict[str, Any]] = []
        self._stale_reuse_count = 0
        self._premature_authorization_count = 0
        self._prior_integrity_failure_count = 0
        self._absence_count = 0
        self._access_interruption_count = 0
        self._candidate_visibility_interruption_count = 0
        self._candidate_visibility_interrupted = False
        self._reconstruction_pending_count = 0

    @property
    def event_log(self) -> tuple[dict[str, Any], ...]:
        return tuple(copy.deepcopy(self._event_log))

    def _new_canonical_id(self) -> str:
        return f"identity-{len(self._registry) + 1:04d}"

    def _identities_for_key(self, key: CanonicalKey | None) -> list[_CanonicalIdentity]:
        if key is None:
            return []
        return [identity for identity in self._registry.values() if identity.key == key]

    def _matching_identity(
        self,
        key: CanonicalKey,
        *,
        on_mean: float,
        off_mean: float,
    ) -> _CanonicalIdentity | None:
        candidates = self._identities_for_key(key)
        if not candidates:
            return None
        scored = [
            (
                max(
                    abs(float(on_mean) - identity.prototype_on_mean),
                    abs(float(off_mean) - identity.prototype_off_mean),
                ),
                identity.canonical_id,
                identity,
            )
            for identity in candidates
        ]
        distance, _canonical_id, best = min(scored, key=lambda item: (item[0], item[1]))
        if distance > self.config.historical_compatibility_tolerance:
            return None
        return best

    def _new_episode_id(self) -> str:
        return f"episode-{len(self._episodes) + 1:04d}"

    def _active_episode(self) -> _IdentityEpisode | None:
        if self._active_episode_id is None:
            return None
        for episode in reversed(self._episodes):
            if episode.episode_id == self._active_episode_id:
                return episode
        raise RuntimeError("active temporal identity episode was lost")

    def _episode_for_signature(
        self, signature: Signature | None
    ) -> _IdentityEpisode | None:
        if signature is None:
            return None
        for episode in reversed(self._episodes):
            if episode.raw_signature == signature:
                return episode
        return None

    def _record_fresh_evidence(self, grounding: GroundingOutcomeReceipt) -> None:
        signature = grounding.raw_signature
        if (
            signature is None
            or grounding.mode not in {"probe_on", "probe_off"}
            or not grounding.informative_probe
            or grounding.normalized_causal_signal is None
            or grounding.actual_certificate_on
            != grounding.requested_certificate_on
        ):
            return
        evidence = self._fresh_evidence.setdefault(
            signature, {"on": [], "off": []}
        )
        arm = "on" if grounding.actual_certificate_on else "off"
        evidence[arm].append(
            (int(grounding.time), float(grounding.normalized_causal_signal))
        )

    def _episode_evidence(
        self, episode: _IdentityEpisode
    ) -> tuple[tuple[int, float], tuple[int, float]]:
        evidence = self._fresh_evidence.get(episode.raw_signature)
        if evidence is None or not evidence["on"] or not evidence["off"]:
            raise RuntimeError("grounded temporal episode has no fresh evidence")
        return tuple(evidence["on"]), tuple(evidence["off"])

    def prepare_historical_prior(
        self,
        raw_certificate: PublicBoundaryCertificate,
        *,
        time: int,
    ) -> HistoricalGroundingPriorReceipt | None:
        """Issue one source-bound prior from the temporal identity registry."""

        if self.config.history_policy == "withheld":
            return None
        signature = raw_certificate.structural_signature
        existing = self._issued_historical_priors.get(signature)
        if existing is not None:
            return copy.deepcopy(existing)
        target_key = _canonical_key(signature)
        if not self._identities_for_key(target_key):
            # Equal-size generic memory is a return-memory control, not a way
            # to accelerate the first acquisition of an unseen route class.
            return None
        candidates: list[_IdentityEpisode] = []
        for episode in self._episodes:
            if (
                episode.raw_signature == signature
                or not episode.fresh_grounding_satisfied
            ):
                continue
            same_key = episode.canonical_key == target_key
            if self.config.history_policy == "keyed" and same_key:
                candidates.append(episode)
            elif self.config.history_policy == "generic":
                candidates.append(episode)
        if not candidates:
            return None
        source = max(
            candidates,
            key=lambda episode: (episode.grounded_time, episode.episode_id),
        )
        on_value = float(source.fresh_on_mean)
        off_value = float(source.fresh_off_mean)
        payload = {
            "schema": "rrct.v041.historical_grounding_prior.v3",
            "target_signature": signature,
            "source_signature": source.raw_signature,
            "target_epoch_binding_digest": _target_epoch_binding_digest(
                signature
            ),
            "source_identity_id": source.canonical_id,
            "source_episode_id": source.episode_id,
            "source_evidence_digest": source.fresh_evidence_digest,
            "history_policy": self.config.history_policy,
            "seeded_time": int(time),
            "source_certified_time": int(source.grounded_time),
            "on_value": on_value,
            "off_value": off_value,
            "prior_on_count": 1,
            "prior_off_count": 1,
            "uses_evaluator_labels": False,
        }
        receipt = HistoricalGroundingPriorReceipt(
            **payload,
            digest=_digest(payload),
        )
        if not validate_historical_grounding_prior_receipt(receipt):
            raise RuntimeError("temporal controller issued an invalid prior")
        self._issued_historical_priors[signature] = receipt
        return copy.deepcopy(receipt)

    def authorizes_ordinary_action(
        self,
        signature: Signature | None,
        certificate_digest: str | None,
    ) -> bool:
        episode = self._active_episode()
        return bool(
            episode is not None
            and episode.fresh_grounding_satisfied
            and signature == episode.raw_signature
            and isinstance(certificate_digest, str)
            and len(certificate_digest) == 64
        )

    def ordinary_action_authorization_digest(
        self,
        signature: Signature | None,
        certificate_digest: str | None,
    ) -> str | None:
        if not self.authorizes_ordinary_action(signature, certificate_digest):
            return None
        return temporal_action_authorization_digest(
            signature,
            certificate_digest,
            self._active_identity_id,
            self._active_episode_id,
        )

    def _close_active(self, time: int, reason: str) -> None:
        episode = self._active_episode()
        if episode is not None and episode.closed_time is None:
            episode.closed_time = int(time)
            episode.close_reason = str(reason)
            self._retired_epoch_bindings.add(
                _target_epoch_binding_digest(episode.raw_signature)
            )
        self._active_identity_id = None
        self._active_episode_id = None
        self._active_raw_signature = None
        self._active_certificate_digest = None

    def _recommendation(self, diagnosis: TemporalDiagnosis) -> str:
        if diagnosis == "known_identity_returned":
            return "link_prior_identity_after_fresh_consequence_revalidation"
        if diagnosis == "novel_identity_grounded":
            return "register_identity_and_continue_grounded_action"
        if diagnosis in {"known_identity_candidate", "novel_identity_candidate"}:
            return "recognize_candidate_without_ordinary_authorization"
        if diagnosis == "identity_episode_revoked":
            return "retire_episode_and_retest_boundary"
        if diagnosis == "identity_absent":
            return "preserve_history_and_suspend_boundary_action"
        if diagnosis == "identity_access_interrupted":
            return "retain_identity_and_repair_access_path"
        if diagnosis == "identity_access_restored":
            return "resume_access_to_existing_identity"
        if diagnosis == "identity_candidate_visibility_interrupted":
            return "retain_identity_fail_closed_and_wait_for_candidate_visibility"
        if diagnosis == "identity_candidate_visibility_restored":
            return "resume_existing_identity_and_continue_consequence_sentinels"
        if diagnosis == "identity_reconstruction_pending":
            return "continue_fail_closed_boundary_reconstruction"
        if diagnosis == "stale_identity_reuse_detected":
            return "fail_closed_and_reject_retired_certificate"
        if diagnosis == "premature_identity_authorization_detected":
            return "fail_closed_until_fresh_consequence_grounding"
        if diagnosis == "identity_prior_integrity_failure":
            return "discard_historical_prior_and_retest_from_scratch"
        if diagnosis == "identity_continuity_retained":
            return "retain_current_identity_episode"
        return "continue_temporal_identity_observation"

    def observe(
        self,
        grounding: GroundingOutcomeReceipt,
        reflexive: ReflexiveDiagnosisReceipt,
        historical_prior: HistoricalGroundingPriorReceipt | None = None,
    ) -> TemporalIdentityReceipt:
        if not isinstance(grounding, GroundingOutcomeReceipt):
            raise TypeError("grounding must be a GroundingOutcomeReceipt")
        if not isinstance(reflexive, ReflexiveDiagnosisReceipt):
            raise TypeError("reflexive must be a ReflexiveDiagnosisReceipt")
        if not validate_grounding_outcome_receipt(grounding):
            raise ValueError("grounding receipt digest is invalid")
        if not validate_reflexive_diagnosis_receipt(reflexive):
            raise ValueError("reflexive receipt digest is invalid")
        if grounding.uses_evaluator_labels or reflexive.uses_evaluator_labels:
            raise ValueError("temporal identity input exposes evaluator labels")
        if reflexive.inherited_grounding_digest != grounding.digest:
            raise ValueError("reflexive and grounding receipts are not chained")

        time = int(grounding.time)
        raw_signature = grounding.raw_signature
        raw_digest = grounding.raw_certificate_digest
        canonical_key = _canonical_key(raw_signature)
        active_identity_before = self._active_identity_id
        active_episode_before = self._active_episode_id
        events: list[str] = []
        self._record_fresh_evidence(grounding)

        source_episode = (
            None
            if historical_prior is None
            else self._episode_for_signature(historical_prior.source_signature)
        )
        prior_valid = bool(
            historical_prior is not None
            and validate_historical_grounding_prior_receipt(historical_prior)
            and historical_prior.target_signature == raw_signature
            and historical_prior.target_epoch_binding_digest
            == _target_epoch_binding_digest(raw_signature)
            and historical_prior.history_policy == self.config.history_policy
            and source_episode is not None
            and source_episode.episode_id == historical_prior.source_episode_id
            and source_episode.canonical_id == historical_prior.source_identity_id
            and source_episode.fresh_evidence_digest
            == historical_prior.source_evidence_digest
        )
        if historical_prior is not None and not prior_valid:
            self._prior_integrity_failure_count += 1
            events.append("historical_identity_prior_integrity_failure")

        prior_on = historical_prior.prior_on_count if prior_valid else 0
        prior_off = historical_prior.prior_off_count if prior_valid else 0
        fresh_on = max(0, int(grounding.on_count_after) - int(prior_on))
        fresh_off = max(0, int(grounding.off_count_after) - int(prior_off))

        candidate_class: CandidateClass = "none"
        recognition_time: int | None = None
        if raw_signature is not None and canonical_key is not None:
            known = bool(self._identities_for_key(canonical_key))
            candidate_class = "known" if known else "novel"
            if raw_signature not in self._seen_raw_signatures:
                self._seen_raw_signatures.add(raw_signature)
                recognition_time = time
                self._recognitions[raw_signature] = (time, candidate_class)
                events.append(
                    "known_identity_candidate_recognized"
                    if known
                    else "novel_identity_candidate_detected"
                )
                if prior_valid:
                    events.append("historical_identity_prior_applied")
            else:
                recognition_time = self._recognitions[raw_signature][0]

        retired_epoch = bool(
            raw_signature is not None
            and _target_epoch_binding_digest(raw_signature)
            in self._retired_epoch_bindings
        )
        stale_reuse = bool(retired_epoch and grounding.actual_certificate_on)
        if stale_reuse:
            self._stale_reuse_count += 1
            events.append("stale_identity_certificate_reused")

        premature = bool(
            grounding.mode == "ordinary_use"
            and grounding.actual_certificate_on
            and grounding.status_before != "certified"
        )
        if premature:
            self._premature_authorization_count += 1
            events.append("ordinary_action_before_fresh_grounding")

        fresh_grounding_event = bool(
            self._GROUNDING_EVENTS.intersection(grounding.events)
            and grounding.status_after == "certified"
            and raw_signature is not None
            and raw_digest is not None
            and canonical_key is not None
        )
        if prior_valid:
            fresh_grounding_satisfied = bool(
                fresh_grounding_event
                and not retired_epoch
                and fresh_on >= self.config.minimum_return_fresh_on_samples
                and fresh_off >= self.config.minimum_return_fresh_off_samples
                and grounding.lower_bound is not None
            )
        else:
            fresh_grounding_satisfied = bool(
                fresh_grounding_event
                and not retired_epoch
                and historical_prior is None
                and fresh_on >= self.config.minimum_novel_fresh_on_samples
                and fresh_off >= self.config.minimum_novel_fresh_off_samples
                and grounding.lower_bound is not None
            )

        active_episode = self._active_episode()
        duplicate_active_grounding = bool(
            fresh_grounding_event
            and active_episode is not None
            and active_episode.raw_signature == raw_signature
        )

        grounded_novel = False
        grounded_return = False
        if fresh_grounding_event and not fresh_grounding_satisfied:
            events.append("fresh_grounding_evidence_incomplete")
        if duplicate_active_grounding:
            events.append("duplicate_active_epoch_grounding_ignored")
        if (
            fresh_grounding_event
            and fresh_grounding_satisfied
            and not duplicate_active_grounding
        ):
            evidence = self._fresh_evidence.get(raw_signature)
            if evidence is None or not evidence["on"] or not evidence["off"]:
                raise RuntimeError(
                    "freshly grounded identity has no primitive evidence"
                )
            on_records = tuple(evidence["on"])
            off_records = tuple(evidence["off"])
            fresh_on_mean = float(
                np.mean([value for _row, value in on_records])
            )
            fresh_off_mean = float(
                np.mean([value for _row, value in off_records])
            )
            identity = self._matching_identity(
                canonical_key,
                on_mean=fresh_on_mean,
                off_mean=fresh_off_mean,
            )
            if identity is None:
                identity = _CanonicalIdentity(
                    canonical_id=self._new_canonical_id(),
                    key=canonical_key,
                    prototype_on_mean=fresh_on_mean,
                    prototype_off_mean=fresh_off_mean,
                    first_grounded_time=time,
                    last_grounded_time=time,
                )
                self._registry[identity.canonical_id] = identity
                grounded_novel = True
            else:
                grounded_return = bool(identity.episode_ids)
                identity.last_grounded_time = time

            if (
                prior_valid
                and historical_prior.history_policy == "keyed"
                and source_episode is not None
                and source_episode.canonical_key != canonical_key
            ):
                self._prior_integrity_failure_count += 1
                events.append("historical_identity_prior_crossed_identity")
                raise RuntimeError("keyed temporal prior crossed identities")

            if self._active_episode_id is not None:
                active = self._active_episode()
                if active is None or active.raw_signature != raw_signature:
                    self._close_active(time, "superseded_by_fresh_grounding")

            evidence_payload = {
                "signature": raw_signature,
                "on": on_records,
                "off": off_records,
            }
            episode = _IdentityEpisode(
                episode_id=self._new_episode_id(),
                canonical_id=identity.canonical_id,
                canonical_key=canonical_key,
                raw_signature=raw_signature,
                certificate_digest=raw_digest,
                recognized_time=(
                    time if recognition_time is None else int(recognition_time)
                ),
                grounded_time=time,
                recognition_class=("novel" if grounded_novel else "known"),
                grounding_digest=grounding.digest,
                total_on_samples=int(grounding.on_count_after),
                total_off_samples=int(grounding.off_count_after),
                fresh_on_samples=int(fresh_on),
                fresh_off_samples=int(fresh_off),
                historical_prior_used=bool(prior_valid),
                historical_prior_digest=(
                    None if not prior_valid else historical_prior.digest
                ),
                prior_source_episode_id=(
                    None if source_episode is None else source_episode.episode_id
                ),
                fresh_grounding_satisfied=bool(fresh_grounding_satisfied),
                fresh_on_mean=fresh_on_mean,
                fresh_off_mean=fresh_off_mean,
                fresh_evidence_digest=_digest(evidence_payload),
                fresh_evidence_rows=tuple(
                    sorted(
                        {
                            int(row)
                            for row, _value in on_records + off_records
                        }
                    )
                ),
            )
            self._episodes.append(episode)
            identity.episode_ids.append(episode.episode_id)
            identity.return_count = max(0, len(identity.episode_ids) - 1)
            self._active_identity_id = identity.canonical_id
            self._active_episode_id = episode.episode_id
            self._active_raw_signature = raw_signature
            self._active_certificate_digest = raw_digest
            events.append(
                "known_identity_returned_grounded"
                if grounded_return
                else "novel_identity_grounded"
            )

        if "certificate_revoked_by_consequence" in grounding.events:
            if self._active_episode_id is not None:
                self._close_active(time, "consequence_revocation")
            self._candidate_visibility_interrupted = False
            events.append("identity_episode_revoked")

        if "boundary_absent" in grounding.events:
            if grounding.private_boundary_active:
                if self._active_episode_id is not None:
                    if not self._candidate_visibility_interrupted:
                        self._candidate_visibility_interruption_count += 1
                    self._candidate_visibility_interrupted = True
                    events.append("identity_candidate_visibility_interrupted")
                else:
                    self._reconstruction_pending_count += 1
                    events.append("identity_reconstruction_pending")
            else:
                if self._active_episode_id is not None:
                    self._close_active(time, "boundary_absent")
                self._candidate_visibility_interrupted = False
                self._absence_count += 1
                events.append("identity_absence_confirmed")

        visibility_restored = bool(
            self._candidate_visibility_interrupted
            and active_episode_before is not None
            and self._active_episode_id == active_episode_before
            and (
                "boundary_candidate_visibility_restored" in grounding.events
                or (
                    raw_signature is not None
                    and raw_signature == self._active_raw_signature
                    and grounding.status_after == "certified"
                )
            )
        )
        if visibility_restored:
            self._candidate_visibility_interrupted = False
            events.append("identity_candidate_visibility_restored")

        if "access_path_failure" in grounding.events:
            self._access_interruption_count += 1
            events.append("identity_access_path_interrupted")
        if "access_path_restored" in grounding.events:
            events.append("identity_access_path_restored")

        prior_failure = any(
            event in events
            for event in (
                "historical_identity_prior_integrity_failure",
                "historical_identity_prior_source_unbound",
                "historical_identity_prior_crossed_identity",
            )
        )
        if stale_reuse:
            diagnosis: TemporalDiagnosis = "stale_identity_reuse_detected"
        elif premature:
            diagnosis = "premature_identity_authorization_detected"
        elif prior_failure:
            diagnosis = "identity_prior_integrity_failure"
        elif grounded_return:
            diagnosis = "known_identity_returned"
        elif grounded_novel:
            diagnosis = "novel_identity_grounded"
        elif "identity_episode_revoked" in events:
            diagnosis = "identity_episode_revoked"
        elif "identity_absence_confirmed" in events:
            diagnosis = "identity_absent"
        elif "identity_access_path_interrupted" in events:
            diagnosis = "identity_access_interrupted"
        elif "identity_access_path_restored" in events:
            diagnosis = "identity_access_restored"
        elif "identity_candidate_visibility_interrupted" in events:
            diagnosis = "identity_candidate_visibility_interrupted"
        elif "identity_candidate_visibility_restored" in events:
            diagnosis = "identity_candidate_visibility_restored"
        elif "identity_reconstruction_pending" in events:
            diagnosis = "identity_reconstruction_pending"
        elif "known_identity_candidate_recognized" in events:
            diagnosis = "known_identity_candidate"
        elif "novel_identity_candidate_detected" in events:
            diagnosis = "novel_identity_candidate"
        elif self._active_identity_id is not None:
            diagnosis = "identity_continuity_retained"
        else:
            diagnosis = "identity_unknown"

        recommendation = self._recommendation(diagnosis)
        for event in events:
            self._event_log.append(
                {
                    "time": time,
                    "event": event,
                    "raw_signature": raw_signature,
                    "raw_certificate_digest": raw_digest,
                    "canonical_key": canonical_key,
                    "active_identity_after": self._active_identity_id,
                    "active_episode_after": self._active_episode_id,
                    "grounding_digest": grounding.digest,
                    "reflexive_digest": reflexive.digest,
                    "historical_prior_digest": (
                        None if historical_prior is None else historical_prior.digest
                    ),
                    "diagnosis": diagnosis,
                    "recommended_response": recommendation,
                }
            )

        payload = {
            "schema": self.SCHEMA,
            "time": time,
            "inherited_grounding_digest": grounding.digest,
            "inherited_reflexive_digest": reflexive.digest,
            "historical_prior_digest": (
                None if historical_prior is None else historical_prior.digest
            ),
            "historical_prior_source_signature": (
                None
                if historical_prior is None
                else historical_prior.source_signature
            ),
            "historical_prior_valid": prior_valid,
            "raw_signature": raw_signature,
            "raw_certificate_digest": raw_digest,
            "canonical_key": canonical_key,
            "candidate_classification": candidate_class,
            "candidate_recognition_time": recognition_time,
            "active_identity_before": active_identity_before,
            "active_identity_after": self._active_identity_id,
            "active_episode_before": active_episode_before,
            "active_episode_after": self._active_episode_id,
            "canonical_identity_count": len(self._registry),
            "identity_episode_count": len(self._episodes),
            "fresh_grounding_event": fresh_grounding_event,
            "fresh_on_samples": int(fresh_on),
            "fresh_off_samples": int(fresh_off),
            "fresh_grounding_satisfied": bool(fresh_grounding_satisfied),
            "stale_certificate_reuse_detected": stale_reuse,
            "premature_ordinary_authorization_detected": premature,
            "events": tuple(events),
            "inherited_diagnosis": reflexive.diagnosis,
            "diagnosis": diagnosis,
            "recommended_response": recommendation,
            "uses_evaluator_labels": False,
        }
        return TemporalIdentityReceipt(
            schema=self.SCHEMA,
            time=time,
            inherited_grounding_digest=grounding.digest,
            inherited_reflexive_digest=reflexive.digest,
            historical_prior_digest=(
                None if historical_prior is None else historical_prior.digest
            ),
            historical_prior_source_signature=(
                None
                if historical_prior is None
                else historical_prior.source_signature
            ),
            historical_prior_valid=prior_valid,
            raw_signature=raw_signature,
            raw_certificate_digest=raw_digest,
            canonical_key=canonical_key,
            candidate_classification=candidate_class,
            candidate_recognition_time=recognition_time,
            active_identity_before=active_identity_before,
            active_identity_after=self._active_identity_id,
            active_episode_before=active_episode_before,
            active_episode_after=self._active_episode_id,
            canonical_identity_count=len(self._registry),
            identity_episode_count=len(self._episodes),
            fresh_grounding_event=fresh_grounding_event,
            fresh_on_samples=int(fresh_on),
            fresh_off_samples=int(fresh_off),
            fresh_grounding_satisfied=bool(fresh_grounding_satisfied),
            stale_certificate_reuse_detected=stale_reuse,
            premature_ordinary_authorization_detected=premature,
            events=tuple(events),
            inherited_diagnosis=reflexive.diagnosis,
            diagnosis=diagnosis,
            recommended_response=recommendation,
            uses_evaluator_labels=False,
            digest=_digest(payload),
        )

    def snapshot(self) -> dict[str, Any]:
        registry = []
        for canonical_id in sorted(self._registry):
            item = self._registry[canonical_id]
            registry.append(
                {
                    "canonical_id": item.canonical_id,
                    "key": item.key,
                    "prototype_on_mean": item.prototype_on_mean,
                    "prototype_off_mean": item.prototype_off_mean,
                    "first_grounded_time": item.first_grounded_time,
                    "last_grounded_time": item.last_grounded_time,
                    "episode_ids": tuple(item.episode_ids),
                    "return_count": item.return_count,
                }
            )
        episodes = [copy.deepcopy(episode) for episode in self._episodes]
        payload: dict[str, Any] = {
            "schema": "rrct.v041.temporal_identity_controller.v2",
            "config": self.config,
            "registry": tuple(registry),
            "episodes": tuple(episodes),
            "active_identity_id": self._active_identity_id,
            "active_episode_id": self._active_episode_id,
            "active_raw_signature": self._active_raw_signature,
            "active_certificate_digest": self._active_certificate_digest,
            "retired_epoch_binding_digests": tuple(
                sorted(self._retired_epoch_bindings)
            ),
            "stale_reuse_count": self._stale_reuse_count,
            "premature_authorization_count": self._premature_authorization_count,
            "prior_integrity_failure_count": self._prior_integrity_failure_count,
            "absence_count": self._absence_count,
            "access_interruption_count": self._access_interruption_count,
            "candidate_visibility_interruption_count": (
                self._candidate_visibility_interruption_count
            ),
            "candidate_visibility_interrupted": (
                self._candidate_visibility_interrupted
            ),
            "reconstruction_pending_count": self._reconstruction_pending_count,
            "events": tuple(copy.deepcopy(self._event_log)),
            "seen_raw_signatures": tuple(
                sorted(self._seen_raw_signatures, key=repr)
            ),
            "recognitions": tuple(
                (
                    signature,
                    int(self._recognitions[signature][0]),
                    self._recognitions[signature][1],
                )
                for signature in sorted(self._recognitions, key=repr)
            ),
            "fresh_evidence": tuple(
                (
                    signature,
                    tuple(self._fresh_evidence[signature]["on"]),
                    tuple(self._fresh_evidence[signature]["off"]),
                )
                for signature in sorted(self._fresh_evidence, key=repr)
            ),
            "issued_historical_priors": tuple(
                self._issued_historical_priors[signature]
                for signature in sorted(self._issued_historical_priors, key=repr)
            ),
            "uses_evaluator_labels": False,
        }
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)


class TemporalSelfIdentityUnifiedCausalLoop(
    RobustReflexiveDiagnosticUnifiedCausalLoop
):
    """One persistent v0.40 loop with causal temporal-identity memory."""

    def __init__(
        self,
        agent: RRCTAgent,
        config: UnifiedCausalLoopConfig | None = None,
        *,
        grounding_config: ConsequenceGroundingConfig | None = None,
        reflexive_config: RobustReflexiveDiagnosisConfig | None = None,
        temporal_identity_config: TemporalSelfIdentityConfig | None = None,
    ) -> None:
        super().__init__(
            agent,
            config,
            grounding_config=grounding_config,
            reflexive_config=reflexive_config,
        )
        # Replace the untouched v0.39 controller before the first action. The
        # subclass preserves the entire v0.39 interface and adds only bounded
        # consequence-derived priors for recognized route returns.
        temporal_config = temporal_identity_config or TemporalSelfIdentityConfig()
        self.grounding = TemporalPriorConsequenceGroundedAccessController(
            grounding_config,
            historical_prior_enabled=temporal_config.historical_prior_enabled,
            historical_compatibility_tolerance=(
                temporal_config.historical_compatibility_tolerance
            ),
        )
        self.temporal_identity = TemporalSelfIdentityController(temporal_config)
        required_on = temporal_config.minimum_novel_fresh_on_samples
        required_off = temporal_config.minimum_novel_fresh_off_samples
        if temporal_config.history_policy != "withheld":
            required_on = max(
                required_on,
                temporal_config.historical_prior_samples_each
                + temporal_config.minimum_return_fresh_on_samples,
            )
            required_off = max(
                required_off,
                temporal_config.historical_prior_samples_each
                + temporal_config.minimum_return_fresh_off_samples,
            )
        if self.grounding.config.minimum_on_samples < required_on:
            raise ValueError("grounder ON minimum is below temporal freshness minimum")
        if self.grounding.config.minimum_off_samples < required_off:
            raise ValueError("grounder OFF minimum is below temporal freshness minimum")
        self._last_temporal_identity_outcome: TemporalIdentityReceipt | None = None
        self._last_historical_grounding_prior: (
            HistoricalGroundingPriorReceipt | None
        ) = None
        self._current_historical_grounding_prior: (
            HistoricalGroundingPriorReceipt | None
        ) = None
        self._last_issued_historical_grounding_prior: (
            HistoricalGroundingPriorReceipt | None
        ) = None
        self._last_historical_prior_compatibility: str | None = None
        self._current_temporal_action_authorization_digest: str | None = None
        self._last_temporal_action_authorization_digest: str | None = None
        self._temporal_action_gate_block_count = 0

    @property
    def last_temporal_identity_outcome(self) -> TemporalIdentityReceipt | None:
        return copy.deepcopy(self._last_temporal_identity_outcome)

    @property
    def temporal_identity_snapshot(self) -> dict[str, Any]:
        return self.temporal_identity.snapshot()

    @property
    def last_historical_grounding_prior(
        self,
    ) -> HistoricalGroundingPriorReceipt | None:
        return copy.deepcopy(self._last_historical_grounding_prior)

    @property
    def last_issued_historical_grounding_prior(
        self,
    ) -> HistoricalGroundingPriorReceipt | None:
        return copy.deepcopy(self._last_issued_historical_grounding_prior)

    @property
    def last_historical_prior_compatibility(self) -> str | None:
        return self._last_historical_prior_compatibility

    @property
    def last_temporal_action_authorization_digest(self) -> str | None:
        return self._last_temporal_action_authorization_digest

    def _public_certificate(
        self, result: StepResult
    ) -> PublicBoundaryCertificate | None:
        raw = UnifiedCausalLoop._public_certificate(self, result)
        prior = None
        if raw is not None:
            issued = self.grounding.registered_prior_for(
                raw.structural_signature
            )
            if (
                issued is None
                and self.grounding.can_accept_historical_prior(
                    raw.structural_signature
                )
            ):
                issued = self.temporal_identity.prepare_historical_prior(
                    raw, time=result.time
                )
            prior = self.grounding.apply_historical_prior(
                raw, issued, time=result.time
            )
        plan = self.grounding.plan(
            time=result.time,
            raw_certificate=raw,
            result=result,
        )
        self._current_grounding_plan = plan
        self._current_historical_grounding_prior = copy.deepcopy(prior)
        self._current_temporal_action_authorization_digest = None
        if not plan.requested_certificate_on or raw is None:
            return None
        if plan.mode in {"ordinary_use", "sentinel"}:
            authorization = (
                self.temporal_identity.ordinary_action_authorization_digest(
                    raw.structural_signature, raw.digest
                )
            )
            self._current_temporal_action_authorization_digest = authorization
            if authorization is None:
                self.grounding.force_revalidation(
                    raw.structural_signature,
                    time=result.time,
                    reason=f"{plan.mode}_requires_temporal_episode",
                )
                plan.plan_events = tuple(plan.plan_events) + (
                    "temporal_authorization_missing_revalidation_forced",
                )
                self._temporal_action_gate_block_count += 1
                return None
        return raw

    def _complete_previous(self, next_observation, realized_external_return):
        completed_authorization = (
            self._current_temporal_action_authorization_digest
        )
        outcome, row, drift = super()._complete_previous(
            next_observation, realized_external_return
        )
        if outcome is None:
            self._last_temporal_identity_outcome = None
            self._last_historical_grounding_prior = None
            self._last_issued_historical_grounding_prior = None
            self._last_historical_prior_compatibility = None
            self._last_temporal_action_authorization_digest = None
        else:
            grounding = self._last_grounding_outcome
            reflexive = self._last_reflexive_outcome
            if grounding is None or reflexive is None:
                raise RuntimeError(
                    "completed action has no chained v0.39/v0.40 receipts"
                )
            issued_prior = copy.deepcopy(self._current_historical_grounding_prior)
            compatibility = self.grounding.compatibility_for(
                grounding.raw_signature
            )
            prior = self.grounding.prior_for(grounding.raw_signature)
            self._last_historical_grounding_prior = copy.deepcopy(prior)
            self._last_issued_historical_grounding_prior = issued_prior
            self._last_historical_prior_compatibility = compatibility
            self._last_temporal_action_authorization_digest = (
                completed_authorization
            )
            self._last_temporal_identity_outcome = self.temporal_identity.observe(
                grounding, reflexive, prior
            )
        return outcome, row, drift

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
        if effective is None:
            self._current_temporal_action_authorization_digest = None
        return effective, receipt

    def snapshot(self) -> dict[str, Any]:
        payload = super().snapshot()
        inherited_digest = payload.pop("digest", None)
        payload["temporal_self_identity"] = self.temporal_identity.snapshot()
        payload["last_temporal_identity_outcome"] = copy.deepcopy(
            self._last_temporal_identity_outcome
        )
        payload["last_historical_grounding_prior"] = copy.deepcopy(
            self._last_historical_grounding_prior
        )
        payload["last_issued_historical_grounding_prior"] = copy.deepcopy(
            self._last_issued_historical_grounding_prior
        )
        payload["last_historical_prior_compatibility"] = (
            self._last_historical_prior_compatibility
        )
        payload["last_temporal_action_authorization_digest"] = (
            self._last_temporal_action_authorization_digest
        )
        payload["temporal_action_gate_block_count"] = int(
            self._temporal_action_gate_block_count
        )
        payload["temporal_self_identity_digest"] = _digest(
            {
                "temporal_self_identity": payload["temporal_self_identity"],
                "last_temporal_identity_outcome": payload[
                    "last_temporal_identity_outcome"
                ],
                "last_historical_grounding_prior": payload[
                    "last_historical_grounding_prior"
                ],
                "last_issued_historical_grounding_prior": payload[
                    "last_issued_historical_grounding_prior"
                ],
                "last_historical_prior_compatibility": payload[
                    "last_historical_prior_compatibility"
                ],
            }
        )
        payload["inherited_runtime_digest"] = inherited_digest
        payload["digest"] = _digest(payload)
        return payload


__all__ = [
    "HistoricalGroundingPriorReceipt",
    "TemporalIdentityReceipt",
    "TemporalPriorConsequenceGroundedAccessController",
    "TemporalSelfIdentityConfig",
    "TemporalSelfIdentityController",
    "TemporalSelfIdentityUnifiedCausalLoop",
    "validate_historical_grounding_prior_receipt",
    "validate_temporal_identity_receipt",
]
