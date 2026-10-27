"""RRCT v0.42 causal self-model necessity and counterfactual receipts.

This successor layer turns temporal identity from a merely inspectable state
into an explicitly intervenable causal variable.  An intervention is
precommitted before execution and is triggered only by the controller's own
third recognized return, never by evaluator phase labels or hidden world truth.

The runtime retains the v0.41 fail-closed rule: historical memory can reduce the
fresh evidence burden, but it cannot by itself authorize an ordinary action.
Every committed episode receives a direct commit receipt, and every later
certificate-ON action receives an authorization receipt bound to that commit.
"""
from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from typing import Any, Literal

import numpy as np

from .agent import RRCTAgent, StepResult
from .autonomous_self_diagnosis import ConsequenceGroundingConfig
from .robust_reflexive_diagnosis import RobustReflexiveDiagnosisConfig
from .temporal_self_identity import (
    HistoricalGroundingPriorReceipt,
    TemporalSelfIdentityConfig,
    TemporalSelfIdentityUnifiedCausalLoop,
    _canonical_key,
    _digest,
)
from .unified_causal_loop import (
    PublicBoundaryCertificate,
    UnifiedCausalLoop,
    UnifiedCausalLoopConfig,
)

Signature = tuple[tuple[int, int], int, int]
InterventionMode = Literal["intact", "withhold_target", "swap_target"]
PriorPolicy = Literal["keyed", "generic"]


@dataclass(frozen=True)
class CausalSelfModelInterventionConfig:
    """Predeclared surgical intervention over one recognized return.

    ``target_known_return_ordinal`` counts only new certificate signatures whose
    structural key already exists in the temporal controller's grounded
    registry.  The count therefore comes from the model's own history rather
    than evaluator phase names.
    """

    mode: InterventionMode = "intact"
    target_known_return_ordinal: int = 3

    def __post_init__(self) -> None:
        if self.mode not in {"intact", "withhold_target", "swap_target"}:
            raise ValueError("unknown causal self-model intervention mode")
        value = self.target_known_return_ordinal
        if isinstance(value, (bool, np.bool_)) or not isinstance(
            value, (int, np.integer)
        ):
            raise TypeError("target_known_return_ordinal must be an integer")
        if int(value) <= 0:
            raise ValueError("target_known_return_ordinal must be positive")
        object.__setattr__(self, "target_known_return_ordinal", int(value))


@dataclass(frozen=True)
class CounterfactualModePrediction:
    """One pre-outcome prediction derived from the internal model state."""

    mode: InterventionMode
    source_identity_id: str | None
    source_episode_id: str | None
    source_signature: Signature | None
    source_evidence_digest: str | None
    minimum_fresh_on_samples: int
    minimum_fresh_off_samples: int
    minimum_candidate_to_commit_latency: int
    minimum_candidate_to_authorization_latency: int
    expected_prior_path: str
    prediction_is_conditional_on_future_consequence: bool


@dataclass(frozen=True)
class SelfModelCounterfactualReceipt:
    """Pre-outcome forecasts for matched interventions on temporal memory."""

    schema: str
    time: int
    target_signature: Signature
    known_return_ordinal: int
    assigned_mode: InterventionMode
    predictions: tuple[CounterfactualModePrediction, ...]
    future_function_unknown: bool
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class SelfModelInterventionReceipt:
    """Receipt for the actual precommitted intervention delivered to grounding."""

    schema: str
    time: int
    target_signature: Signature
    known_return_ordinal: int
    mode: InterventionMode
    event: Literal[
        "keyed_prior_passed",
        "keyed_prior_withheld",
        "wrong_source_prior_substituted",
    ]
    issued_prior_digest: str | None
    issued_prior_policy: PriorPolicy | None
    issued_source_signature: Signature | None
    issued_source_identity_id: str | None
    delivered_prior_digest: str | None
    delivered_prior_policy: PriorPolicy | None
    delivered_source_signature: Signature | None
    delivered_source_identity_id: str | None
    counterfactual_digest: str
    intervention_config_digest: str
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class SelfModelCommitEventReceipt:
    """Direct causal receipt for a newly grounded identity episode."""

    schema: str
    time: int
    target_signature: Signature
    certificate_epoch: int
    certificate_digest: str
    identity_id: str
    episode_id: str
    recognition_class: str
    grounding_digest: str
    temporal_identity_digest: str
    fresh_evidence_digest: str
    fresh_evidence_rows: tuple[int, ...]
    fresh_on_samples: int
    fresh_off_samples: int
    issued_historical_prior_digest: str | None
    active_historical_prior_digest: str | None
    historical_prior_compatibility: str | None
    historical_prior_used: bool
    intervention_receipt_digest: str | None
    counterfactual_receipt_digest: str | None
    quarantined_prior_excluded_from_commit: bool
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class SelfModelActionAuthorizationReceipt:
    """Bind an actual certificate-ON action to the episode commit it uses."""

    schema: str
    time: int
    target_signature: Signature
    certificate_digest: str
    identity_id: str
    episode_id: str
    commit_event_digest: str
    temporal_authorization_digest: str
    active_historical_prior_digest: str | None
    intervention_receipt_digest: str | None
    uses_evaluator_labels: bool
    digest: str


def _receipt_digest(payload: dict[str, Any]) -> str:
    return _digest(payload)


def _payload_without_digest(receipt: Any) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def _valid_sha256(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _valid_optional_sha256(value: Any) -> bool:
    return value is None or _valid_sha256(value)


def _valid_signature(value: Any) -> bool:
    if not isinstance(value, tuple) or len(value) != 3:
        return False
    pair, rank, epoch = value
    if not isinstance(pair, tuple) or len(pair) != 2:
        return False
    return all(
        not isinstance(item, (bool, np.bool_))
        and isinstance(item, (int, np.integer))
        and int(item) >= 0
        for item in (*pair, rank, epoch)
    )


def _valid_time(value: Any) -> bool:
    return bool(
        not isinstance(value, (bool, np.bool_))
        and isinstance(value, (int, np.integer))
        and int(value) >= 0
    )


def _valid_ordinal(value: Any) -> bool:
    return bool(
        not isinstance(value, (bool, np.bool_))
        and isinstance(value, (int, np.integer))
        and int(value) > 0
    )


def _complete_source_binding(prediction: CounterfactualModePrediction) -> bool:
    fields = (
        prediction.source_identity_id,
        prediction.source_episode_id,
        prediction.source_signature,
        prediction.source_evidence_digest,
    )
    return all(value is None for value in fields) or all(
        value is not None for value in fields
    )


def validate_self_model_counterfactual_receipt(
    receipt: SelfModelCounterfactualReceipt,
) -> bool:
    if not isinstance(receipt, SelfModelCounterfactualReceipt):
        return False
    if receipt.schema != "rrct.v042.self_model_counterfactual.v1":
        return False
    if not _valid_time(receipt.time) or not _valid_signature(
        receipt.target_signature
    ):
        return False
    if not _valid_ordinal(receipt.known_return_ordinal):
        return False
    if receipt.uses_evaluator_labels or not receipt.future_function_unknown:
        return False
    if receipt.assigned_mode not in {
        "intact",
        "withhold_target",
        "swap_target",
    }:
        return False
    if len(receipt.predictions) != 3:
        return False
    if {prediction.mode for prediction in receipt.predictions} != {
        "intact",
        "withhold_target",
        "swap_target",
    }:
        return False
    for prediction in receipt.predictions:
        if not isinstance(prediction, CounterfactualModePrediction):
            return False
        if not prediction.prediction_is_conditional_on_future_consequence:
            return False
        if not _complete_source_binding(prediction):
            return False
        if prediction.source_signature is not None and not _valid_signature(
            prediction.source_signature
        ):
            return False
        if prediction.source_evidence_digest is not None and not _valid_sha256(
            prediction.source_evidence_digest
        ):
            return False
        if min(
            prediction.minimum_fresh_on_samples,
            prediction.minimum_fresh_off_samples,
            prediction.minimum_candidate_to_commit_latency,
            prediction.minimum_candidate_to_authorization_latency,
        ) <= 0:
            return False
        source_key = _canonical_key(prediction.source_signature)
        target_key = _canonical_key(receipt.target_signature)
        if prediction.mode == "intact" and source_key != target_key:
            return False
        if prediction.mode == "withhold_target" and source_key is not None:
            return False
        if prediction.mode == "swap_target" and (
            source_key is None or source_key == target_key
        ):
            return False
    if not _valid_sha256(receipt.digest):
        return False
    return receipt.digest == _receipt_digest(_payload_without_digest(receipt))


def validate_self_model_intervention_receipt(
    receipt: SelfModelInterventionReceipt,
) -> bool:
    if not isinstance(receipt, SelfModelInterventionReceipt):
        return False
    if receipt.schema != "rrct.v042.self_model_intervention.v1":
        return False
    if (
        not _valid_time(receipt.time)
        or not _valid_signature(receipt.target_signature)
        or not _valid_ordinal(receipt.known_return_ordinal)
    ):
        return False
    if receipt.uses_evaluator_labels:
        return False
    expected_event = {
        "intact": "keyed_prior_passed",
        "withhold_target": "keyed_prior_withheld",
        "swap_target": "wrong_source_prior_substituted",
    }.get(receipt.mode)
    if expected_event != receipt.event:
        return False
    if not _valid_sha256(receipt.issued_prior_digest):
        return False
    expected_issued_policy = (
        "generic" if receipt.mode == "swap_target" else "keyed"
    )
    if receipt.issued_prior_policy != expected_issued_policy:
        return False
    if (
        not _valid_signature(receipt.issued_source_signature)
        or not isinstance(receipt.issued_source_identity_id, str)
        or not receipt.issued_source_identity_id
    ):
        return False
    issued_key = _canonical_key(receipt.issued_source_signature)
    target_key = _canonical_key(receipt.target_signature)
    if receipt.mode in {"intact", "withhold_target"}:
        if issued_key != target_key:
            return False
    elif issued_key is None or issued_key == target_key:
        return False
    if receipt.mode == "withhold_target":
        if (
            receipt.delivered_prior_digest is not None
            or receipt.delivered_prior_policy is not None
            or receipt.delivered_source_signature is not None
            or receipt.delivered_source_identity_id is not None
        ):
            return False
    else:
        if (
            receipt.delivered_prior_digest != receipt.issued_prior_digest
            or receipt.delivered_prior_policy != receipt.issued_prior_policy
            or receipt.delivered_source_signature
            != receipt.issued_source_signature
            or receipt.delivered_source_identity_id
            != receipt.issued_source_identity_id
        ):
            return False
    if receipt.mode == "swap_target" and receipt.delivered_prior_policy != "generic":
        return False
    if receipt.mode == "intact" and receipt.delivered_prior_policy != "keyed":
        return False
    if not _valid_sha256(receipt.counterfactual_digest):
        return False
    if not _valid_sha256(receipt.intervention_config_digest):
        return False
    if not _valid_sha256(receipt.digest):
        return False
    return receipt.digest == _receipt_digest(_payload_without_digest(receipt))


def validate_self_model_commit_event_receipt(
    receipt: SelfModelCommitEventReceipt,
) -> bool:
    if not isinstance(receipt, SelfModelCommitEventReceipt):
        return False
    if receipt.schema != "rrct.v042.self_model_commit_event.v1":
        return False
    if not _valid_time(receipt.time) or not _valid_signature(
        receipt.target_signature
    ):
        return False
    if receipt.uses_evaluator_labels:
        return False
    if receipt.certificate_epoch != receipt.target_signature[2]:
        return False
    if receipt.fresh_on_samples <= 0 or receipt.fresh_off_samples <= 0:
        return False
    if (
        not receipt.fresh_evidence_rows
        or tuple(sorted(set(receipt.fresh_evidence_rows)))
        != receipt.fresh_evidence_rows
        or any(not _valid_time(value) for value in receipt.fresh_evidence_rows)
    ):
        return False
    required_digests = (
        receipt.certificate_digest,
        receipt.grounding_digest,
        receipt.temporal_identity_digest,
        receipt.fresh_evidence_digest,
    )
    if not all(_valid_sha256(value) for value in required_digests):
        return False
    optional_digests = (
        receipt.issued_historical_prior_digest,
        receipt.active_historical_prior_digest,
        receipt.intervention_receipt_digest,
        receipt.counterfactual_receipt_digest,
    )
    if not all(_valid_optional_sha256(value) for value in optional_digests):
        return False
    if bool(receipt.intervention_receipt_digest) != bool(
        receipt.counterfactual_receipt_digest
    ):
        return False
    if not receipt.identity_id or not receipt.episode_id:
        return False
    if receipt.historical_prior_used and (
        receipt.active_historical_prior_digest is None
        or receipt.historical_prior_compatibility != "compatible"
    ):
        return False
    if receipt.historical_prior_compatibility == "quarantined":
        if receipt.active_historical_prior_digest is not None:
            return False
        if receipt.historical_prior_used:
            return False
        if not receipt.quarantined_prior_excluded_from_commit:
            return False
    if not _valid_sha256(receipt.digest):
        return False
    return receipt.digest == _receipt_digest(_payload_without_digest(receipt))


def validate_self_model_action_authorization_receipt(
    receipt: SelfModelActionAuthorizationReceipt,
) -> bool:
    if not isinstance(receipt, SelfModelActionAuthorizationReceipt):
        return False
    if receipt.schema != "rrct.v042.self_model_action_authorization.v1":
        return False
    if not _valid_time(receipt.time) or not _valid_signature(
        receipt.target_signature
    ):
        return False
    if receipt.uses_evaluator_labels:
        return False
    if not receipt.identity_id or not receipt.episode_id:
        return False
    if not _valid_sha256(receipt.certificate_digest):
        return False
    if not _valid_sha256(receipt.commit_event_digest):
        return False
    if not _valid_sha256(receipt.temporal_authorization_digest):
        return False
    if not _valid_optional_sha256(receipt.active_historical_prior_digest):
        return False
    if not _valid_optional_sha256(receipt.intervention_receipt_digest):
        return False
    if not _valid_sha256(receipt.digest):
        return False
    return receipt.digest == _receipt_digest(_payload_without_digest(receipt))


def validate_self_model_receipt_chain(
    counterfactual: SelfModelCounterfactualReceipt,
    intervention: SelfModelInterventionReceipt,
    commit: SelfModelCommitEventReceipt,
    authorization: SelfModelActionAuthorizationReceipt | None = None,
) -> bool:
    """Validate the complete causal chain from forecast through action use."""

    if not validate_self_model_counterfactual_receipt(counterfactual):
        return False
    if not validate_self_model_intervention_receipt(intervention):
        return False
    if not validate_self_model_commit_event_receipt(commit):
        return False
    if authorization is not None and not validate_self_model_action_authorization_receipt(
        authorization
    ):
        return False
    if not (
        counterfactual.target_signature
        == intervention.target_signature
        == commit.target_signature
    ):
        return False
    if counterfactual.known_return_ordinal != intervention.known_return_ordinal:
        return False
    if counterfactual.assigned_mode != intervention.mode:
        return False
    if intervention.counterfactual_digest != counterfactual.digest:
        return False
    if commit.counterfactual_receipt_digest != counterfactual.digest:
        return False
    if commit.intervention_receipt_digest != intervention.digest:
        return False
    if commit.issued_historical_prior_digest != intervention.issued_prior_digest:
        return False
    if commit.time < intervention.time:
        return False
    if intervention.mode == "intact":
        if (
            not commit.historical_prior_used
            or commit.active_historical_prior_digest
            != intervention.delivered_prior_digest
        ):
            return False
    elif intervention.mode == "withhold_target":
        if commit.historical_prior_used or commit.active_historical_prior_digest is not None:
            return False
    elif commit.historical_prior_compatibility == "quarantined":
        if commit.historical_prior_used or commit.active_historical_prior_digest is not None:
            return False
    if authorization is None:
        return True
    if authorization.time < commit.time:
        return False
    if authorization.target_signature != commit.target_signature:
        return False
    if authorization.identity_id != commit.identity_id:
        return False
    if authorization.episode_id != commit.episode_id:
        return False
    if authorization.commit_event_digest != commit.digest:
        return False
    if authorization.intervention_receipt_digest != intervention.digest:
        return False
    if authorization.certificate_digest != commit.certificate_digest:
        return False
    return True


class CausalSelfModelNecessityUnifiedCausalLoop(
    TemporalSelfIdentityUnifiedCausalLoop
):
    """Persistent v0.41 loop with one evaluator-blind self-model intervention."""

    def __init__(
        self,
        agent: RRCTAgent,
        config: UnifiedCausalLoopConfig | None = None,
        *,
        grounding_config: ConsequenceGroundingConfig | None = None,
        reflexive_config: RobustReflexiveDiagnosisConfig | None = None,
        temporal_identity_config: TemporalSelfIdentityConfig | None = None,
        intervention_config: CausalSelfModelInterventionConfig | None = None,
    ) -> None:
        temporal = temporal_identity_config or TemporalSelfIdentityConfig(
            historical_prior_enabled=True,
            history_policy="keyed",
        )
        if temporal.history_policy != "keyed" or not temporal.historical_prior_enabled:
            raise ValueError(
                "v0.42 surgical interventions require a keyed temporal controller"
            )
        super().__init__(
            agent,
            config,
            grounding_config=grounding_config,
            reflexive_config=reflexive_config,
            temporal_identity_config=temporal,
        )
        self.intervention_config = (
            intervention_config or CausalSelfModelInterventionConfig()
        )
        if not isinstance(
            self.intervention_config, CausalSelfModelInterventionConfig
        ):
            raise TypeError(
                "intervention_config must be CausalSelfModelInterventionConfig"
            )
        self._intervention_config_digest = _digest(
            {
                "schema": "rrct.v042.intervention_config.v1",
                "config": self.intervention_config,
            }
        )
        self._known_signature_ordinals: dict[Signature, int] = {}
        self._target_signature: Signature | None = None
        self._target_counterfactual: SelfModelCounterfactualReceipt | None = None
        self._target_intervention: SelfModelInterventionReceipt | None = None
        self._target_issued_prior: HistoricalGroundingPriorReceipt | None = None
        self._current_v042_counterfactual: SelfModelCounterfactualReceipt | None = None
        self._current_v042_intervention: SelfModelInterventionReceipt | None = None
        self._current_v042_issued_prior: HistoricalGroundingPriorReceipt | None = None
        self._current_v042_authorization: (
            SelfModelActionAuthorizationReceipt | None
        ) = None
        self._last_v042_counterfactual: SelfModelCounterfactualReceipt | None = None
        self._last_v042_intervention: SelfModelInterventionReceipt | None = None
        self._last_v042_commit: SelfModelCommitEventReceipt | None = None
        self._last_v042_authorization: (
            SelfModelActionAuthorizationReceipt | None
        ) = None
        self._commit_by_episode: dict[str, SelfModelCommitEventReceipt] = {}
        self._commit_by_signature: dict[Signature, SelfModelCommitEventReceipt] = {}
        self._intervention_event_count = 0

    @property
    def last_self_model_counterfactual(
        self,
    ) -> SelfModelCounterfactualReceipt | None:
        return copy.deepcopy(self._last_v042_counterfactual)

    @property
    def last_self_model_intervention(
        self,
    ) -> SelfModelInterventionReceipt | None:
        return copy.deepcopy(self._last_v042_intervention)

    @property
    def last_self_model_commit_event(
        self,
    ) -> SelfModelCommitEventReceipt | None:
        return copy.deepcopy(self._last_v042_commit)

    @property
    def last_self_model_action_authorization(
        self,
    ) -> SelfModelActionAuthorizationReceipt | None:
        return copy.deepcopy(self._last_v042_authorization)

    @property
    def target_signature(self) -> Signature | None:
        return copy.deepcopy(self._target_signature)

    @property
    def target_self_model_counterfactual(
        self,
    ) -> SelfModelCounterfactualReceipt | None:
        return copy.deepcopy(self._target_counterfactual)

    @property
    def target_self_model_intervention(
        self,
    ) -> SelfModelInterventionReceipt | None:
        return copy.deepcopy(self._target_intervention)

    @property
    def target_issued_historical_prior(
        self,
    ) -> HistoricalGroundingPriorReceipt | None:
        return copy.deepcopy(self._target_issued_prior)

    @property
    def intervention_event_count(self) -> int:
        return int(self._intervention_event_count)

    @property
    def commit_event_receipts(
        self,
    ) -> tuple[SelfModelCommitEventReceipt, ...]:
        return tuple(
            copy.deepcopy(self._commit_by_episode[key])
            for key in sorted(self._commit_by_episode)
        )

    def _episode_sources(
        self, signature: Signature
    ) -> tuple[Any | None, Any | None]:
        target_key = _canonical_key(signature)
        snapshot = self.temporal_identity.snapshot()
        episodes = [
            episode
            for episode in snapshot["episodes"]
            if episode.raw_signature != signature
            and episode.fresh_grounding_satisfied
        ]
        keyed = [episode for episode in episodes if episode.canonical_key == target_key]
        keyed_source = (
            None
            if not keyed
            else max(keyed, key=lambda item: (item.grounded_time, item.episode_id))
        )
        wrong_sources = [
            episode for episode in episodes if episode.canonical_key != target_key
        ]
        wrong_source = (
            None
            if not wrong_sources
            else max(
                wrong_sources,
                key=lambda item: (item.grounded_time, item.episode_id),
            )
        )
        return keyed_source, wrong_source

    def _prediction(
        self,
        mode: InterventionMode,
        source: Any | None,
    ) -> CounterfactualModePrediction:
        if mode == "intact":
            on_samples = self.temporal_identity.config.minimum_return_fresh_on_samples
            off_samples = self.temporal_identity.config.minimum_return_fresh_off_samples
            path = "keyed_prior_then_fresh_consequence_confirmation"
        elif mode == "withhold_target":
            on_samples = self.temporal_identity.config.minimum_novel_fresh_on_samples
            off_samples = self.temporal_identity.config.minimum_novel_fresh_off_samples
            path = "no_prior_full_fresh_reconstruction"
        else:
            on_samples = self.temporal_identity.config.minimum_novel_fresh_on_samples
            off_samples = self.temporal_identity.config.minimum_novel_fresh_off_samples
            path = "wrong_source_prior_test_then_quarantine_or_full_reconstruction"
        total = int(on_samples + off_samples)
        return CounterfactualModePrediction(
            mode=mode,
            source_identity_id=None if source is None else source.canonical_id,
            source_episode_id=None if source is None else source.episode_id,
            source_signature=(
                None if source is None else source.raw_signature
            ),
            source_evidence_digest=(
                None if source is None else source.fresh_evidence_digest
            ),
            minimum_fresh_on_samples=int(on_samples),
            minimum_fresh_off_samples=int(off_samples),
            minimum_candidate_to_commit_latency=max(0, total - 1),
            minimum_candidate_to_authorization_latency=max(1, total),
            expected_prior_path=path,
            prediction_is_conditional_on_future_consequence=True,
        )

    def _build_counterfactual(
        self,
        *,
        time: int,
        signature: Signature,
        ordinal: int,
    ) -> SelfModelCounterfactualReceipt:
        keyed_source, wrong_source = self._episode_sources(signature)
        if keyed_source is None:
            raise RuntimeError(
                "recognized return has no grounded keyed source episode"
            )
        if wrong_source is None:
            raise RuntimeError(
                "swap control requires one grounded nonmatching source episode"
            )
        predictions = (
            self._prediction("intact", keyed_source),
            self._prediction("withhold_target", None),
            self._prediction("swap_target", wrong_source),
        )
        payload = {
            "schema": "rrct.v042.self_model_counterfactual.v1",
            "time": int(time),
            "target_signature": signature,
            "known_return_ordinal": int(ordinal),
            "assigned_mode": self.intervention_config.mode,
            "predictions": predictions,
            "future_function_unknown": True,
            "uses_evaluator_labels": False,
        }
        receipt = SelfModelCounterfactualReceipt(
            **payload,
            digest=_receipt_digest(payload),
        )
        if not validate_self_model_counterfactual_receipt(receipt):
            raise RuntimeError("invalid self-model counterfactual receipt")
        return receipt

    def _known_return_ordinal(self, signature: Signature) -> int | None:
        existing = self._known_signature_ordinals.get(signature)
        if existing is not None:
            return existing
        if not self.temporal_identity.recognizes_structural_key(signature):
            return None
        ordinal = len(self._known_signature_ordinals) + 1
        self._known_signature_ordinals[signature] = ordinal
        return ordinal

    def _intervention_for(
        self,
        *,
        time: int,
        signature: Signature,
        issued: HistoricalGroundingPriorReceipt | None,
        ordinal: int,
    ) -> tuple[
        HistoricalGroundingPriorReceipt | None,
        SelfModelInterventionReceipt,
    ]:
        mode = self.intervention_config.mode
        if issued is None:
            raise RuntimeError("target self-model intervention has no source receipt")
        if mode == "intact":
            delivered = issued
            event = "keyed_prior_passed"
        elif mode == "withhold_target":
            delivered = None
            event = "keyed_prior_withheld"
        else:
            delivered = issued
            event = "wrong_source_prior_substituted"
        counterfactual = self._target_counterfactual
        if counterfactual is None:
            raise RuntimeError("target intervention lacks its counterfactual receipt")
        payload = {
            "schema": "rrct.v042.self_model_intervention.v1",
            "time": int(time),
            "target_signature": signature,
            "known_return_ordinal": int(ordinal),
            "mode": mode,
            "event": event,
            "issued_prior_digest": issued.digest,
            "issued_prior_policy": issued.history_policy,
            "issued_source_signature": issued.source_signature,
            "issued_source_identity_id": issued.source_identity_id,
            "delivered_prior_digest": None if delivered is None else delivered.digest,
            "delivered_prior_policy": (
                None if delivered is None else delivered.history_policy
            ),
            "delivered_source_signature": (
                None if delivered is None else delivered.source_signature
            ),
            "delivered_source_identity_id": (
                None if delivered is None else delivered.source_identity_id
            ),
            "counterfactual_digest": counterfactual.digest,
            "intervention_config_digest": self._intervention_config_digest,
            "uses_evaluator_labels": False,
        }
        receipt = SelfModelInterventionReceipt(
            **payload,
            digest=_receipt_digest(payload),
        )
        if not validate_self_model_intervention_receipt(receipt):
            raise RuntimeError("invalid self-model intervention receipt")
        return delivered, receipt

    def _authorization_receipt(
        self,
        *,
        time: int,
        raw: PublicBoundaryCertificate,
        authorization_digest: str,
    ) -> SelfModelActionAuthorizationReceipt:
        snapshot = self.temporal_identity.snapshot()
        identity_id = snapshot["active_identity_id"]
        episode_id = snapshot["active_episode_id"]
        if identity_id is None or episode_id is None:
            raise RuntimeError("temporal authorization has no active identity episode")
        commit = self._commit_by_episode.get(episode_id)
        if commit is None:
            raise RuntimeError("temporal authorization has no bound commit receipt")
        active_prior = self.grounding.prior_for(raw.structural_signature)
        intervention = (
            self._target_intervention
            if raw.structural_signature == self._target_signature
            else None
        )
        payload = {
            "schema": "rrct.v042.self_model_action_authorization.v1",
            "time": int(time),
            "target_signature": raw.structural_signature,
            "certificate_digest": raw.digest,
            "identity_id": identity_id,
            "episode_id": episode_id,
            "commit_event_digest": commit.digest,
            "temporal_authorization_digest": authorization_digest,
            "active_historical_prior_digest": (
                None if active_prior is None else active_prior.digest
            ),
            "intervention_receipt_digest": (
                None if intervention is None else intervention.digest
            ),
            "uses_evaluator_labels": False,
        }
        receipt = SelfModelActionAuthorizationReceipt(
            **payload,
            digest=_receipt_digest(payload),
        )
        if not validate_self_model_action_authorization_receipt(receipt):
            raise RuntimeError("invalid self-model action authorization receipt")
        return receipt

    def _public_certificate(
        self, result: StepResult
    ) -> PublicBoundaryCertificate | None:
        raw = UnifiedCausalLoop._public_certificate(self, result)
        issued: HistoricalGroundingPriorReceipt | None = None
        delivered: HistoricalGroundingPriorReceipt | None = None
        intervention: SelfModelInterventionReceipt | None = None
        counterfactual: SelfModelCounterfactualReceipt | None = None
        prior = None
        if raw is not None:
            signature = raw.structural_signature
            ordinal = self._known_return_ordinal(signature)
            registered = self.grounding.registered_prior_for(signature)
            if registered is not None:
                issued = registered
                delivered = registered
            elif self.grounding.can_accept_historical_prior(signature):
                is_target = bool(
                    ordinal == self.intervention_config.target_known_return_ordinal
                )
                policy: Literal["keyed", "generic"] = "keyed"
                if is_target and self.intervention_config.mode == "swap_target":
                    policy = "generic"
                issued = self.temporal_identity.prepare_historical_prior(
                    raw,
                    time=result.time,
                    policy_override=policy,
                    exclude_target_key=(policy == "generic"),
                )
                if is_target:
                    if self._target_signature is None:
                        self._target_signature = signature
                    elif self._target_signature != signature:
                        raise RuntimeError(
                            "precommitted intervention matched more than one signature"
                        )
                    if self._target_counterfactual is None:
                        self._target_counterfactual = self._build_counterfactual(
                            time=result.time,
                            signature=signature,
                            ordinal=int(ordinal),
                        )
                    counterfactual = self._target_counterfactual
                    if self._target_intervention is None:
                        delivered, self._target_intervention = self._intervention_for(
                            time=result.time,
                            signature=signature,
                            issued=issued,
                            ordinal=int(ordinal),
                        )
                        self._target_issued_prior = copy.deepcopy(issued)
                        self._intervention_event_count += 1
                    else:
                        delivered = (
                            None
                            if self.intervention_config.mode == "withhold_target"
                            else issued
                        )
                    intervention = self._target_intervention
                else:
                    delivered = issued
            prior = self.grounding.apply_historical_prior(
                raw, delivered, time=result.time
            )

        plan = self.grounding.plan(
            time=result.time,
            raw_certificate=raw,
            result=result,
        )
        self._current_grounding_plan = plan
        self._current_historical_grounding_prior = copy.deepcopy(prior)
        self._current_v042_issued_prior = copy.deepcopy(issued)
        self._current_v042_counterfactual = copy.deepcopy(counterfactual)
        self._current_v042_intervention = copy.deepcopy(intervention)
        self._current_temporal_action_authorization_digest = None
        self._current_v042_authorization = None
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
            self._current_v042_authorization = self._authorization_receipt(
                time=result.time,
                raw=raw,
                authorization_digest=authorization,
            )
        return raw

    def _build_commit_receipt(self) -> SelfModelCommitEventReceipt | None:
        temporal = self._last_temporal_identity_outcome
        grounding = self._last_grounding_outcome
        if temporal is None or grounding is None:
            return None
        if not set(temporal.events).intersection(
            {"known_identity_returned_grounded", "novel_identity_grounded"}
        ):
            return None
        episode_id = temporal.active_episode_after
        identity_id = temporal.active_identity_after
        signature = temporal.raw_signature
        certificate_digest = temporal.raw_certificate_digest
        if (
            episode_id is None
            or identity_id is None
            or signature is None
            or certificate_digest is None
        ):
            raise RuntimeError("grounded temporal event lacks episode bindings")
        snapshot = self.temporal_identity.snapshot()
        matches = [
            episode for episode in snapshot["episodes"] if episode.episode_id == episode_id
        ]
        if len(matches) != 1:
            raise RuntimeError("grounded temporal episode is absent from registry")
        episode = matches[0]
        active_prior = self._last_historical_grounding_prior
        issued_prior = self._last_issued_historical_grounding_prior
        if signature == self._target_signature and issued_prior is None:
            issued_prior = self._target_issued_prior
        compatibility = self._last_historical_prior_compatibility
        intervention = (
            self._target_intervention if signature == self._target_signature else None
        )
        counterfactual = (
            self._target_counterfactual if signature == self._target_signature else None
        )
        quarantined_excluded = bool(
            compatibility != "quarantined"
            or (
                active_prior is None
                and episode.historical_prior_digest is None
                and not episode.historical_prior_used
            )
        )
        payload = {
            "schema": "rrct.v042.self_model_commit_event.v1",
            "time": int(temporal.time),
            "target_signature": signature,
            "certificate_epoch": int(signature[2]),
            "certificate_digest": certificate_digest,
            "identity_id": identity_id,
            "episode_id": episode_id,
            "recognition_class": episode.recognition_class,
            "grounding_digest": grounding.digest,
            "temporal_identity_digest": temporal.digest,
            "fresh_evidence_digest": episode.fresh_evidence_digest,
            "fresh_evidence_rows": tuple(episode.fresh_evidence_rows),
            "fresh_on_samples": int(episode.fresh_on_samples),
            "fresh_off_samples": int(episode.fresh_off_samples),
            "issued_historical_prior_digest": (
                None if issued_prior is None else issued_prior.digest
            ),
            "active_historical_prior_digest": (
                None if active_prior is None else active_prior.digest
            ),
            "historical_prior_compatibility": compatibility,
            "historical_prior_used": bool(episode.historical_prior_used),
            "intervention_receipt_digest": (
                None if intervention is None else intervention.digest
            ),
            "counterfactual_receipt_digest": (
                None if counterfactual is None else counterfactual.digest
            ),
            "quarantined_prior_excluded_from_commit": quarantined_excluded,
            "uses_evaluator_labels": False,
        }
        receipt = SelfModelCommitEventReceipt(
            **payload,
            digest=_receipt_digest(payload),
        )
        if not validate_self_model_commit_event_receipt(receipt):
            raise RuntimeError("invalid self-model commit event receipt")
        return receipt

    def _complete_previous(self, next_observation, realized_external_return):
        completed_counterfactual = copy.deepcopy(
            self._current_v042_counterfactual
        )
        completed_intervention = copy.deepcopy(self._current_v042_intervention)
        completed_issued = copy.deepcopy(self._current_v042_issued_prior)
        completed_authorization = copy.deepcopy(
            self._current_v042_authorization
        )
        outcome, row, drift = super()._complete_previous(
            next_observation, realized_external_return
        )
        self._last_v042_counterfactual = completed_counterfactual
        self._last_v042_intervention = completed_intervention
        self._last_v042_authorization = completed_authorization
        if outcome is None:
            self._last_v042_commit = None
        else:
            # Preserve the actual temporal-controller issuance even when the
            # surgical intervention withheld it from the grounder.
            self._last_issued_historical_grounding_prior = completed_issued
            commit = self._build_commit_receipt()
            self._last_v042_commit = commit
            if commit is not None:
                self._commit_by_episode[commit.episode_id] = commit
                self._commit_by_signature[commit.target_signature] = commit
        return outcome, row, drift

    def snapshot(self) -> dict[str, Any]:
        payload = super().snapshot()
        inherited_digest = payload.pop("digest", None)
        payload.update(
            {
                "schema": "rrct.v042.causal_self_model_necessity_runtime.v1",
                "intervention_config": self.intervention_config,
                "intervention_config_digest": self._intervention_config_digest,
                "known_signature_ordinals": tuple(
                    sorted(self._known_signature_ordinals.items(), key=repr)
                ),
                "target_signature": self._target_signature,
                "target_counterfactual": copy.deepcopy(
                    self._target_counterfactual
                ),
                "target_intervention": copy.deepcopy(self._target_intervention),
                "target_issued_historical_prior": copy.deepcopy(
                    self._target_issued_prior
                ),
                "last_self_model_counterfactual": copy.deepcopy(
                    self._last_v042_counterfactual
                ),
                "last_self_model_intervention": copy.deepcopy(
                    self._last_v042_intervention
                ),
                "last_self_model_commit": copy.deepcopy(self._last_v042_commit),
                "last_self_model_authorization": copy.deepcopy(
                    self._last_v042_authorization
                ),
                "commit_receipts": tuple(
                    self._commit_by_episode[key]
                    for key in sorted(self._commit_by_episode)
                ),
                "intervention_event_count": int(self._intervention_event_count),
                "uses_evaluator_labels": False,
                "inherited_runtime_digest": inherited_digest,
            }
        )
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)


__all__ = [
    "CausalSelfModelInterventionConfig",
    "CausalSelfModelNecessityUnifiedCausalLoop",
    "CounterfactualModePrediction",
    "InterventionMode",
    "SelfModelActionAuthorizationReceipt",
    "SelfModelCommitEventReceipt",
    "SelfModelCounterfactualReceipt",
    "SelfModelInterventionReceipt",
    "validate_self_model_action_authorization_receipt",
    "validate_self_model_commit_event_receipt",
    "validate_self_model_counterfactual_receipt",
    "validate_self_model_intervention_receipt",
    "validate_self_model_receipt_chain",
]
