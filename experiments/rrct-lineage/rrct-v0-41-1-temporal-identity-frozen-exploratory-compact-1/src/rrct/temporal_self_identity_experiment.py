"""RRCT v0.41 repeated-change temporal self-identity experiment.

The experiment preserves the v0.39 oracle-free grounding and v0.40 robust
world-versus-self diagnosis layers. It subjects one uninterrupted runtime to
repeated returns of two hidden causal-route identities:

    A -> world shock on A -> B -> null -> A -> B -> null -> A

Every causal certificate epoch is new. The temporal controller may recognize a
returning route class from its own history, but the action path must still earn
a fresh consequence-grounded authorization. Evaluator phase names and hidden
route truth are used only in the sealed post-outcome score.
"""
from __future__ import annotations

import copy
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any, Literal

import numpy as np

from .agent import RRCTAgent
from .autonomous_self_diagnosis import (
    ConsequenceGroundingConfig,
    GroundingOutcomeReceipt,
)
from .autonomous_self_diagnosis_experiment import (
    V039_ACCESS_FAULT_STEPS,
    V039_MAX_ACCESS_FAULT_DIAGNOSIS_LATENCY,
    _V039FaultInjectableAgent,
    _agent_v039,
    _wrap_v039_row,
)
from .causal_boundary import CausalBoundaryConfig, DIRECT_ACCESS_SNAPSHOT_SCHEMA
from .post_change_closure_experiment import (
    V037ExperimentConfig,
    V037_MIN_CORRECT_TAIL_ACTIONS,
    run_post_change_closure_trace,
)
from .robust_reflexive_diagnosis import (
    ReflexiveDiagnosisReceipt,
    RobustReflexiveDiagnosisConfig,
)
from .robust_reflexive_diagnosis_experiment import _wrap_v040_row
from .temporal_self_identity import (
    HistoricalGroundingPriorReceipt,
    TemporalIdentityReceipt,
    TemporalSelfIdentityConfig,
    TemporalSelfIdentityUnifiedCausalLoop,
    temporal_action_authorization_digest,
    validate_historical_grounding_prior_receipt,
    validate_temporal_identity_receipt,
)
from .unified_causal_loop import UnifiedCausalLoop, UnifiedCausalLoopConfig
from .unified_causal_loop_experiment import (
    _HiddenWorld,
    _PhaseTruth,
    _json_sha256,
)

V041_VERSION = "0.41.1.dev2"
V041_ROW_SCHEMA = "rrct.v041.temporal_self_identity.row.v3"
V041_SUMMARY_SCHEMA = "rrct.v041.temporal_self_identity.summary.v3"
V041_DEVELOPMENT_SEED = 41001
V041_ACCESS_FAULT_PHASE = "identity_a_initial"
V041_ACCESS_FAULT_START_OFFSET = 1_120
V041_MAX_WORLD_SHIFT_DIAGNOSIS_LATENCY = 32
V041_MIN_ACTIVE_TAIL_ACTIONS = 430
V041_MIN_DISCONNECT_NULL_ACTIONS = 470
V041_MAX_RETURN_RECOGNITION_TO_GROUNDING_DELAY = 4
V041_A_RETURN_MULTIPLIER = 1.40
V041_B_RETURN_MULTIPLIER = 0.65
V041_SAME_KEY_LURE_MULTIPLIER = 0.00
V041WorldVariant = Literal["true_recurrence", "same_key_null_lure"]


@dataclass(frozen=True)
class V041ExperimentConfig(V037ExperimentConfig):
    """Repeated A/B/null schedule for one persistent runtime."""

    identity_a_initial_steps: int = 1_440
    world_shock_a_steps: int = 480
    identity_b_first_steps: int = 1_440
    disconnect_one_steps: int = 1_440
    identity_a_return_one_steps: int = 1_440
    identity_b_return_steps: int = 1_440
    disconnect_two_steps: int = 1_440
    identity_a_return_two_steps: int = 1_440

    def __post_init__(self) -> None:
        super().__post_init__()
        names = (
            "identity_a_initial_steps",
            "world_shock_a_steps",
            "identity_b_first_steps",
            "disconnect_one_steps",
            "identity_a_return_one_steps",
            "identity_b_return_steps",
            "disconnect_two_steps",
            "identity_a_return_two_steps",
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
        minimum = self.confirmation_budget_steps + self.recovery_tail_steps
        for name in (
            "identity_a_initial_steps",
            "identity_b_first_steps",
            "disconnect_one_steps",
            "identity_a_return_one_steps",
            "identity_b_return_steps",
            "disconnect_two_steps",
            "identity_a_return_two_steps",
        ):
            if int(getattr(self, name)) < minimum:
                raise ValueError(
                    f"{name} must reserve confirmation plus recovery tail"
                )

    @property
    def phase_steps(self) -> tuple[tuple[str, int], ...]:
        return (
            ("identity_a_initial", self.identity_a_initial_steps),
            ("world_shock_a", self.world_shock_a_steps),
            ("identity_b_first", self.identity_b_first_steps),
            ("disconnect_one", self.disconnect_one_steps),
            ("identity_a_return_one", self.identity_a_return_one_steps),
            ("identity_b_return", self.identity_b_return_steps),
            ("disconnect_two", self.disconnect_two_steps),
            ("identity_a_return_two", self.identity_a_return_two_steps),
        )


V041_D1_CONFIG = V041ExperimentConfig()

_A_PHASES = {
    "identity_a_initial",
    "world_shock_a",
    "identity_a_return_one",
    "identity_a_return_two",
}
_B_PHASES = {"identity_b_first", "identity_b_return"}
_DISCONNECT_PHASES = {"disconnect_one", "disconnect_two"}
_ACTIVE_PHASES = tuple(
    name
    for name, _steps in V041_D1_CONFIG.phase_steps
    if name not in _DISCONNECT_PHASES and name != "world_shock_a"
)


def _v041_phase_truth(
    config: V037ExperimentConfig,
    world: _HiddenWorld,
    transition_index: int,
) -> _PhaseTruth:
    if not isinstance(config, V041ExperimentConfig):
        raise TypeError("v0.41 phase resolver requires V041ExperimentConfig")
    if not 0 <= int(transition_index) < config.total_steps:
        raise IndexError("transition index lies outside the v0.41 schedule")
    start = 0
    for name, steps in config.phase_steps:
        if transition_index < start + steps:
            offset = int(transition_index - start)
            if name in _A_PHASES:
                pair = world.stable_pair
                effect = world.stable_effect
                rank = 2
            elif name in _B_PHASES:
                pair = world.remap_pair
                effect = world.remap_effect
                rank = 2
            elif name in _DISCONNECT_PHASES:
                pair = None
                effect = None
                rank = 0
            else:
                raise RuntimeError(f"unknown v0.41 phase {name!r}")
            multiplier = (
                config.world_shock_multiplier
                if name == "world_shock_a"
                else 1.0
            )
            return _PhaseTruth(name, offset, pair, rank, effect, multiplier)
        start += steps
    raise RuntimeError("v0.41 phase schedule is incomplete")


def _v041_task_return_multiplier(
    _config: V037ExperimentConfig,
    _world: _HiddenWorld,
    phase: _PhaseTruth,
    *,
    world_variant: V041WorldVariant,
) -> float:
    """Evaluator-side functional fingerprints hidden from the runtime."""

    if phase.name in _B_PHASES:
        return V041_B_RETURN_MULTIPLIER
    if (
        world_variant == "same_key_null_lure"
        and phase.name == "identity_a_return_two"
    ):
        return V041_SAME_KEY_LURE_MULTIPLIER
    return V041_A_RETURN_MULTIPLIER


def _minimal_engine_summary(
    seed: int,
    config: V041ExperimentConfig,
    boundary_config: CausalBoundaryConfig,
    runtime_config: UnifiedCausalLoopConfig,
    rows: Sequence[Mapping[str, Any]],
    runtime: UnifiedCausalLoop,
    runtime_instance_digest: str,
    phase_model_counts: Mapping[str, Mapping[str, int]],
    control_model_counts: Mapping[str, Mapping[str, Mapping[str, int]]],
) -> dict[str, Any]:
    del boundary_config, runtime_config
    phase_counts = {
        name: sum(row["phase"] == name for row in rows)
        for name, _steps in config.phase_steps
    }
    integrity = {
        "row_count_exact": len(rows) == config.total_steps,
        "phase_counts_exact": all(
            phase_counts[name] == steps for name, steps in config.phase_steps
        ),
        "all_hard_integrity": all(
            bool(row.get("hard_integrity_valid")) for row in rows
        ),
        "single_runtime": all(bool(row["runtime_identity_ok"]) for row in rows),
        "zero_resets": all(int(row["reset_count"]) == 0 for row in rows),
        "no_evaluator_truth_leak": all(
            not bool(row["evaluator_truth_leak"]) for row in rows
        ),
    }
    return {
        "schema": "rrct.v041.multicycle_engine_summary.v1",
        "seed": int(seed),
        "row_count": len(rows),
        "phase_counts": phase_counts,
        "phase_model_counts": copy.deepcopy(dict(phase_model_counts)),
        "control_model_counts": copy.deepcopy(dict(control_model_counts)),
        "runtime_instance_digest": runtime_instance_digest,
        "terminal_runtime_digest": runtime.snapshot()["digest"],
        "integrity": integrity,
        "all_endpoints_met": all(integrity.values()),
    }


def _receipt_mapping(receipt: TemporalIdentityReceipt) -> dict[str, Any]:
    return copy.deepcopy(asdict(receipt))


def _prior_mapping(
    prior: HistoricalGroundingPriorReceipt | None,
) -> dict[str, Any] | None:
    return None if prior is None else copy.deepcopy(asdict(prior))


def _wrap_v041_row(
    v040_row: Mapping[str, Any],
    *,
    grounding: GroundingOutcomeReceipt,
    reflexive: ReflexiveDiagnosisReceipt,
    temporal: TemporalIdentityReceipt,
    historical_prior: HistoricalGroundingPriorReceipt | None,
    issued_historical_prior: HistoricalGroundingPriorReceipt | None,
    historical_prior_compatibility: str | None,
    history_policy: Literal["keyed", "withheld", "generic"],
    temporal_action_authorization: str | None,
    world_variant_evaluator_only: V041WorldVariant,
) -> dict[str, Any]:
    wrapped = copy.deepcopy(dict(v040_row))
    v040_schema = wrapped.get("schema")
    v040_sha = _json_sha256(wrapped)
    wrapped["schema"] = V041_ROW_SCHEMA
    wrapped["v040_row_schema"] = v040_schema
    wrapped["v040_row_sha256"] = v040_sha
    wrapped["temporal_self_identity"] = _receipt_mapping(temporal)
    wrapped["historical_grounding_prior"] = _prior_mapping(historical_prior)
    wrapped["issued_historical_grounding_prior"] = _prior_mapping(
        issued_historical_prior
    )
    wrapped["historical_prior_compatibility"] = historical_prior_compatibility
    wrapped["history_policy"] = history_policy
    wrapped["temporal_action_authorization_digest"] = (
        temporal_action_authorization
    )
    wrapped["world_variant_evaluator_only"] = world_variant_evaluator_only
    expected_action_authorization = None
    if (
        grounding.mode in {"ordinary_use", "sentinel"}
        and grounding.actual_certificate_on
        and temporal.raw_signature is not None
        and temporal.raw_certificate_digest is not None
        and temporal.active_identity_before is not None
        and temporal.active_episode_before is not None
    ):
        expected_action_authorization = temporal_action_authorization_digest(
            temporal.raw_signature,
            temporal.raw_certificate_digest,
            temporal.active_identity_before,
            temporal.active_episode_before,
        )
    action_binding_valid = bool(
        temporal_action_authorization == expected_action_authorization
    )
    wrapped["temporal_action_gate_binding_valid"] = action_binding_valid
    prior_digest = None if historical_prior is None else historical_prior.digest
    issued_prior_digest = (
        None if issued_historical_prior is None else issued_historical_prior.digest
    )
    payload = {
        "v040_row_sha256": v040_sha,
        "grounding_digest": grounding.digest,
        "reflexive_digest": reflexive.digest,
        "temporal_identity_digest": temporal.digest,
        "historical_grounding_prior_digest": prior_digest,
        "issued_historical_grounding_prior_digest": issued_prior_digest,
        "historical_prior_compatibility": historical_prior_compatibility,
        "history_policy": history_policy,
        "temporal_action_authorization_digest": temporal_action_authorization,
        "world_variant_evaluator_only": world_variant_evaluator_only,
    }
    wrapped["v041_wrapper_digest"] = _json_sha256(payload)
    wrapped["v041_wrapper_integrity"] = bool(
        wrapped.get("v040_wrapper_integrity", False)
        and v040_schema == "rrct.v040.robust_reflexive_diagnosis.row.v1"
        and temporal.time == int(wrapped["transition_index"])
        and temporal.inherited_grounding_digest == grounding.digest
        and temporal.inherited_reflexive_digest == reflexive.digest
        and validate_temporal_identity_receipt(temporal)
        and history_policy in {"keyed", "withheld", "generic"}
        and world_variant_evaluator_only
        in {"true_recurrence", "same_key_null_lure"}
        and action_binding_valid
        and (
            issued_historical_prior is None
            or (
                validate_historical_grounding_prior_receipt(
                    issued_historical_prior
                )
                and issued_historical_prior.history_policy == history_policy
                and temporal.raw_signature
                == issued_historical_prior.target_signature
            )
        )
        and (
            historical_prior_compatibility
            in {None, "pending", "on_compatible", "compatible", "quarantined"}
        )
        and (
            (
                historical_prior is None
                and temporal.historical_prior_digest is None
            )
            or (
                historical_prior is not None
                and validate_historical_grounding_prior_receipt(historical_prior)
                and temporal.historical_prior_digest == historical_prior.digest
                and temporal.historical_prior_source_signature
                == historical_prior.source_signature
                and temporal.raw_signature == historical_prior.target_signature
                and issued_historical_prior is not None
                and historical_prior.digest == issued_historical_prior.digest
                and historical_prior_compatibility != "quarantined"
            )
        )
        and not temporal.uses_evaluator_labels
    )
    return wrapped


def _phase_rows(
    rows: Sequence[Mapping[str, Any]], phase: str
) -> list[Mapping[str, Any]]:
    return [row for row in rows if row["phase"] == phase]


def _tail(rows: Sequence[Mapping[str, Any]], steps: int) -> list[Mapping[str, Any]]:
    return list(rows[-min(int(steps), len(rows)) :])


def _event_rows(
    rows: Sequence[Mapping[str, Any]], event: str
) -> list[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if event in row["temporal_self_identity"]["events"]
    ]


def _build_v041_summary(
    seed: int,
    rows: Sequence[Mapping[str, Any]],
    engine_summary: Mapping[str, Any],
    runtime: TemporalSelfIdentityUnifiedCausalLoop,
    agent: RRCTAgent,
    config: V041ExperimentConfig,
    world_variant: V041WorldVariant,
) -> dict[str, Any]:
    temporal_snapshot = runtime.temporal_identity_snapshot
    grounding_snapshot = runtime.grounding_snapshot
    reflexive_snapshot = runtime.reflexive_snapshot
    access_snapshot = agent.causal_boundary_snapshot()["access_readout"]

    phase_tails: dict[str, dict[str, Any]] = {}
    for phase, _steps in config.phase_steps:
        tail = _tail(_phase_rows(rows, phase), config.recovery_tail_steps)
        if phase in _DISCONNECT_PHASES or (
            world_variant == "same_key_null_lure"
            and phase == "identity_a_return_two"
        ):
            correct = sum(row["action_public_pair"] is None for row in tail)
        else:
            correct = sum(bool(row["action_gate_open_evaluator_only"]) for row in tail)
        phase_tails[phase] = {
            "rows": len(tail),
            "correct_actions": int(correct),
            "correct_fraction": float(correct / max(1, len(tail))),
        }

    registry = list(temporal_snapshot["registry"])
    episodes = list(temporal_snapshot["episodes"])
    canonical_sequence = [episode.canonical_id for episode in episodes]
    if world_variant == "true_recurrence":
        expected_recurrence = bool(
            len(canonical_sequence) == 5
            and canonical_sequence[0] == canonical_sequence[2]
            and canonical_sequence[0] == canonical_sequence[4]
            and canonical_sequence[1] == canonical_sequence[3]
            and canonical_sequence[0] != canonical_sequence[1]
        )
        expected_episode_count = 5
        expected_return_count = 3
        expected_registry_returns = [1, 2]
    else:
        expected_recurrence = bool(
            len(canonical_sequence) == 4
            and canonical_sequence[0] == canonical_sequence[2]
            and canonical_sequence[1] == canonical_sequence[3]
            and canonical_sequence[0] != canonical_sequence[1]
        )
        expected_episode_count = 4
        expected_return_count = 2
        expected_registry_returns = [1, 1]

    known_candidate_rows = _event_rows(
        rows, "known_identity_candidate_recognized"
    )
    known_grounded_rows = _event_rows(rows, "known_identity_returned_grounded")
    recognition_delays: list[int] = []
    for grounded in known_grounded_rows:
        signature = grounded["temporal_self_identity"]["raw_signature"]
        prior = [
            row
            for row in known_candidate_rows
            if row["temporal_self_identity"]["raw_signature"] == signature
            and int(row["transition_index"])
            <= int(grounded["transition_index"])
        ]
        if prior:
            recognition_delays.append(
                int(grounded["transition_index"])
                - int(prior[0]["transition_index"])
            )

    shock_events = [
        row
        for row in rows
        if "external_dynamics_shift"
        in row["robust_reflexive_diagnosis"]["events"]
    ]
    shock_offsets = [
        int(row["phase_offset"])
        for row in shock_events
        if row["phase"] == "world_shock_a"
    ]
    nonshock_world_events = [
        row for row in shock_events if row["phase"] != "world_shock_a"
    ]

    access_failure = [
        row
        for row in rows
        if "access_path_failure" in row["autonomous_grounding"]["events"]
    ]
    access_restored = [
        row
        for row in rows
        if "access_path_restored" in row["autonomous_grounding"]["events"]
    ]
    access_identity_continuity = False
    if access_failure and access_restored:
        failed = access_failure[0]["temporal_self_identity"]
        restored = access_restored[0]["temporal_self_identity"]
        access_identity_continuity = bool(
            failed["active_identity_before"] is not None
            and failed["active_identity_after"] == failed["active_identity_before"]
            and restored["active_identity_after"] == failed["active_identity_after"]
            and restored["active_episode_after"] == failed["active_episode_after"]
        )

    novel_episodes = [
        episode for episode in episodes if episode.recognition_class == "novel"
    ]
    returning_episodes = [
        episode for episode in episodes if episode.recognition_class == "known"
    ]
    history_policy = runtime.temporal_identity.config.history_policy
    keyed_history = history_policy == "keyed"
    if keyed_history:
        returning_grounding_valid = all(
            episode.historical_prior_used
            and episode.historical_prior_digest is not None
            and episode.prior_source_episode_id is not None
            and episode.fresh_on_samples
            >= runtime.temporal_identity.config.minimum_return_fresh_on_samples
            and episode.fresh_off_samples
            >= runtime.temporal_identity.config.minimum_return_fresh_off_samples
            for episode in returning_episodes
        )
    else:
        returning_grounding_valid = all(
            not episode.historical_prior_used
            and episode.historical_prior_digest is None
            and episode.prior_source_episode_id is None
            and episode.fresh_on_samples
            >= runtime.temporal_identity.config.minimum_novel_fresh_on_samples
            and episode.fresh_off_samples
            >= runtime.temporal_identity.config.minimum_novel_fresh_off_samples
            for episode in returning_episodes
        )
    all_episode_grounding_fresh = bool(
        len(episodes) == expected_episode_count
        and len(novel_episodes) == 2
        and len(returning_episodes) == expected_return_count
        and all(episode.fresh_grounding_satisfied for episode in episodes)
        and all(
            not episode.historical_prior_used
            and episode.fresh_on_samples
            >= runtime.temporal_identity.config.minimum_novel_fresh_on_samples
            and episode.fresh_off_samples
            >= runtime.temporal_identity.config.minimum_novel_fresh_off_samples
            for episode in novel_episodes
        )
        and returning_grounding_valid
    )

    active_tail_pass = all(
        phase_tails[phase]["correct_actions"] >= V041_MIN_ACTIVE_TAIL_ACTIONS
        for phase in (
            "identity_a_initial",
            "world_shock_a",
            "identity_b_first",
            "identity_a_return_one",
            "identity_b_return",
            *(
                ("identity_a_return_two",)
                if world_variant == "true_recurrence"
                else ()
            ),
        )
    )
    disconnect_pass = all(
        phase_tails[phase]["correct_actions"]
        >= V041_MIN_DISCONNECT_NULL_ACTIONS
        for phase in _DISCONNECT_PHASES
    )

    visibility_interruptions = _event_rows(
        rows, "identity_candidate_visibility_interrupted"
    )
    visibility_restorations = _event_rows(
        rows, "identity_candidate_visibility_restored"
    )
    reconstruction_pending = _event_rows(rows, "identity_reconstruction_pending")
    confirmed_absence = _event_rows(rows, "identity_absence_confirmed")
    visibility_identity_safe = bool(
        all(
            row["temporal_self_identity"]["active_identity_before"] is not None
            and row["temporal_self_identity"]["active_identity_before"]
            == row["temporal_self_identity"]["active_identity_after"]
            and row["temporal_self_identity"]["active_episode_before"] is not None
            and row["temporal_self_identity"]["active_episode_before"]
            == row["temporal_self_identity"]["active_episode_after"]
            for row in visibility_interruptions + visibility_restorations
        )
        and all(
            row["temporal_self_identity"]["active_episode_before"] is None
            and row["temporal_self_identity"]["active_episode_after"] is None
            for row in reconstruction_pending
        )
        and len(confirmed_absence) == len(_DISCONNECT_PHASES)
        and all(row["phase"] in _DISCONNECT_PHASES for row in confirmed_absence)
        and all(episode.close_reason != "boundary_absent" for episode in episodes)
        and int(temporal_snapshot["absence_count"]) == len(_DISCONNECT_PHASES)
        and not bool(temporal_snapshot["candidate_visibility_interrupted"])
    )
    target_rows = _phase_rows(rows, "identity_a_return_two")
    target_ordinary_authorizations = [
        row
        for row in target_rows
        if row["autonomous_grounding"]["mode"] == "ordinary_use"
        and row["autonomous_grounding"]["actual_certificate_on"]
    ]
    target_episode_commits = [
        row
        for row in target_rows
        if set(row["temporal_self_identity"]["events"]).intersection(
            {"known_identity_returned_grounded", "novel_identity_grounded"}
        )
    ]
    target_quarantines = [
        row
        for row in target_rows
        if row.get("historical_prior_compatibility") == "quarantined"
    ]
    if world_variant == "true_recurrence":
        target_condition_safe = bool(
            target_episode_commits and target_ordinary_authorizations
        )
    else:
        target_condition_safe = bool(
            not target_episode_commits
            and not target_ordinary_authorizations
            and any(
                row["temporal_self_identity"]["raw_signature"] is not None
                and row["autonomous_grounding"]["private_boundary_active"]
                for row in target_rows
            )
            and any(
                "candidate_rejected_by_consequence"
                in row["autonomous_grounding"]["events"]
                for row in target_rows
            )
            and (
                history_policy == "withheld"
                or bool(target_quarantines)
            )
        )

    integrity = {
        "engine_integrity": bool(all(engine_summary["integrity"].values())),
        "all_v039_wrappers_valid": all(
            bool(row.get("v039_wrapper_integrity")) for row in rows
        ),
        "all_v040_wrappers_valid": all(
            bool(row.get("v040_wrapper_integrity")) for row in rows
        ),
        "all_v041_wrappers_valid": all(
            bool(row.get("v041_wrapper_integrity")) for row in rows
        ),
        "direct_access_schema_exact": (
            access_snapshot.get("schema") == DIRECT_ACCESS_SNAPSHOT_SCHEMA
        ),
        "zero_access_label_updates": bool(
            access_snapshot.get("uses_class_labels") is False
            and int(access_snapshot.get("update_count", -1)) == 0
            and all(int(row["causal_access_updates"]) == 0 for row in rows)
        ),
        "all_successor_layers_oracle_free": bool(
            grounding_snapshot["uses_evaluator_labels"] is False
            and reflexive_snapshot["uses_evaluator_labels"] is False
            and temporal_snapshot["uses_evaluator_labels"] is False
            and all(
                not row["autonomous_grounding"]["uses_evaluator_labels"]
                and not row["robust_reflexive_diagnosis"]["uses_evaluator_labels"]
                and not row["temporal_self_identity"]["uses_evaluator_labels"]
                for row in rows
            )
        ),
        "single_persistent_runtime": all(
            bool(row["runtime_identity_ok"]) and int(row["reset_count"]) == 0
            for row in rows
        ),
    }

    endpoints = {
        "H01_integrity_and_oracle_exclusion": bool(all(integrity.values())),
        "H02_two_distinct_canonical_identities": bool(
            len(registry) == 2
            and len({item["canonical_id"] for item in registry}) == 2
        ),
        "H03_recurrent_identity_sequence_preserved": expected_recurrence,
        "H04_every_episode_freshly_consequence_grounded": bool(
            all_episode_grounding_fresh
            and temporal_snapshot["stale_reuse_count"] == 0
            and temporal_snapshot["premature_authorization_count"] == 0
            and temporal_snapshot["prior_integrity_failure_count"] == 0
        ),
        "H05_repeated_active_action_recovery": bool(active_tail_pass),
        "H06_repeated_disconnection_null_action": bool(disconnect_pass),
        "H07_world_change_does_not_fragment_identity": bool(
            len(shock_offsets) == 1
            and not nonshock_world_events
            and shock_offsets[0] <= V041_MAX_WORLD_SHIFT_DIAGNOSIS_LATENCY
            and canonical_sequence
            and canonical_sequence[0] == episodes[0].canonical_id
        ),
        "H08_access_failure_preserves_identity_episode": bool(
            access_identity_continuity
            and int(access_failure[0]["phase_offset"])
            - V041_ACCESS_FAULT_START_OFFSET
            <= V039_MAX_ACCESS_FAULT_DIAGNOSIS_LATENCY
        ) if access_failure else False,
        "H09_known_returns_recognized_before_fresh_grounding": bool(
            len(known_candidate_rows) == 3
            and len(known_grounded_rows) == expected_return_count
            and len(recognition_delays) == expected_return_count
            and all(
                0 <= delay <= V041_MAX_RETURN_RECOGNITION_TO_GROUNDING_DELAY
                for delay in recognition_delays
            )
            and (
                (
                    keyed_history
                    and all(
                        episode.historical_prior_used
                        for episode in returning_episodes
                    )
                    and all(
                        episode.fresh_on_samples == 1
                        for episode in returning_episodes
                    )
                    and all(
                        episode.fresh_off_samples == 1
                        for episode in returning_episodes
                    )
                )
                or (
                    not keyed_history
                    and all(
                        not episode.historical_prior_used
                        for episode in returning_episodes
                    )
                    and all(
                        episode.fresh_on_samples
                        >= runtime.temporal_identity.config.minimum_novel_fresh_on_samples
                        for episode in returning_episodes
                    )
                    and all(
                        episode.fresh_off_samples
                        >= runtime.temporal_identity.config.minimum_novel_fresh_off_samples
                        for episode in returning_episodes
                    )
                )
            )
        ),
        "H10_no_catastrophic_identity_merge_or_forgetting": bool(
            expected_recurrence
            and len(episodes) == expected_episode_count
            and sorted(item["return_count"] for item in registry)
            == expected_registry_returns
            and temporal_snapshot["stale_reuse_count"] == 0
        ),
        "H11_visibility_access_and_absence_not_conflated": (
            visibility_identity_safe
        ),
        "H12_condition_specific_target_behavior": target_condition_safe,
    }
    all_met = bool(all(endpoints.values()))
    return {
        "schema": V041_SUMMARY_SCHEMA,
        "version": V041_VERSION,
        "condition": {
            "history_policy": runtime.temporal_identity.config.history_policy,
            "world_variant": world_variant,
            "a_return_multiplier": V041_A_RETURN_MULTIPLIER,
            "b_return_multiplier": V041_B_RETURN_MULTIPLIER,
            "same_key_lure_multiplier": V041_SAME_KEY_LURE_MULTIPLIER,
        },
        "scientific_status": "developmental_temporal_causal_self_identity",
        "seed": int(seed),
        "schedule": list(config.phase_steps),
        "phase_tails": phase_tails,
        "temporal_identity": {
            "canonical_identity_count": len(registry),
            "episode_count": len(episodes),
            "canonical_sequence": canonical_sequence,
            "registry": copy.deepcopy(registry),
            "episodes": [asdict(episode) for episode in episodes],
            "known_candidate_count": len(known_candidate_rows),
            "known_return_grounding_count": len(known_grounded_rows),
            "recognition_to_grounding_delays": recognition_delays,
            "stale_reuse_count": int(temporal_snapshot["stale_reuse_count"]),
            "premature_authorization_count": int(
                temporal_snapshot["premature_authorization_count"]
            ),
            "prior_integrity_failure_count": int(
                temporal_snapshot["prior_integrity_failure_count"]
            ),
            "historical_prior_episode_count": int(
                sum(episode.historical_prior_used for episode in episodes)
            ),
            "historical_prior_enabled": bool(
                runtime.temporal_identity.config.historical_prior_enabled
            ),
            "history_policy": history_policy,
            "historical_prior_quarantine_count": int(
                grounding_snapshot["temporal_historical_prior_quarantine_count"]
            ),
            "temporal_action_gate_block_count": int(
                runtime.snapshot()["temporal_action_gate_block_count"]
            ),
            "snapshot_digest": temporal_snapshot["digest"],
        },
        "world_shift": {
            "offsets": shock_offsets,
            "nonshock_count": len(nonshock_world_events),
        },
        "access_fault": {
            "failure_offsets": [int(row["phase_offset"]) for row in access_failure],
            "restoration_offsets": [
                int(row["phase_offset"]) for row in access_restored
            ],
            "identity_continuity": access_identity_continuity,
        },
        "candidate_visibility": {
            "interruption_count": len(visibility_interruptions),
            "restoration_count": len(visibility_restorations),
            "reconstruction_pending_count": len(reconstruction_pending),
            "confirmed_absence_count": len(confirmed_absence),
            "identity_safe": visibility_identity_safe,
        },
        "integrity": integrity,
        "endpoints": endpoints,
        "all_endpoints_met": all_met,
        "earliest_failed_layer": next(
            (name for name, value in endpoints.items() if not value), None
        ),
        "status": (
            "V041_DEVELOPMENT_ENDPOINTS_MET"
            if all_met
            else "V041_DEVELOPMENT_ENDPOINTS_NOT_MET"
        ),
        "engine_summary": copy.deepcopy(dict(engine_summary)),
        "interpretation_boundary": (
            "Evidence for evaluator-blind temporal continuity of remembered "
            "causal-route identity classes across repeated remapping, absence, "
            "and return in one bounded persistent runtime. Each episode still "
            "requires fresh consequence grounding. No subjective-awareness "
            "claim is made."
        ),
    }


def run_temporal_self_identity_trace(
    seed: int,
    *,
    experiment_config: V041ExperimentConfig = V041_D1_CONFIG,
    boundary_config: CausalBoundaryConfig | None = None,
    runtime_config: UnifiedCausalLoopConfig | None = None,
    grounding_config: ConsequenceGroundingConfig | None = None,
    reflexive_config: RobustReflexiveDiagnosisConfig | None = None,
    temporal_identity_config: TemporalSelfIdentityConfig | None = None,
    inject_access_fault: bool = True,
    world_variant: V041WorldVariant = "true_recurrence",
    sealed_row_sink: Callable[[Mapping[str, Any]], None] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if world_variant not in {"true_recurrence", "same_key_null_lure"}:
        raise ValueError("unknown v0.41 world variant")
    created_agents: list[RRCTAgent] = []
    created_runtimes: list[TemporalSelfIdentityUnifiedCausalLoop] = []
    wrapped_rows: list[dict[str, Any]] = []

    def agent_factory(config: CausalBoundaryConfig, run_seed: int) -> RRCTAgent:
        agent = _agent_v039(config, run_seed)
        created_agents.append(agent)
        return agent

    def runtime_factory(
        agent: RRCTAgent, config: UnifiedCausalLoopConfig
    ) -> TemporalSelfIdentityUnifiedCausalLoop:
        runtime = TemporalSelfIdentityUnifiedCausalLoop(
            agent,
            config,
            grounding_config=grounding_config,
            reflexive_config=reflexive_config,
            temporal_identity_config=temporal_identity_config,
        )
        created_runtimes.append(runtime)
        return runtime

    def pre_step_hook(
        transition_index: int,
        phase: _PhaseTruth,
        agent: RRCTAgent,
        runtime: UnifiedCausalLoop,
    ) -> None:
        del transition_index, runtime
        if not isinstance(agent, _V039FaultInjectableAgent):
            raise RuntimeError("v0.41 access-fault agent type was lost")
        fault_active = bool(
            inject_access_fault
            and phase.name == V041_ACCESS_FAULT_PHASE
            and V041_ACCESS_FAULT_START_OFFSET
            <= int(phase.offset)
            < V041_ACCESS_FAULT_START_OFFSET + V039_ACCESS_FAULT_STEPS
        )
        agent.set_v039_access_transport_enabled(not fault_active)

    def row_sink(row: Mapping[str, Any]) -> None:
        if len(created_agents) != 1 or len(created_runtimes) != 1:
            raise RuntimeError("v0.41 row arrived before runtime construction")
        agent = created_agents[0]
        runtime = created_runtimes[0]
        result = agent.last_result
        grounding = runtime.last_grounding_outcome
        reflexive = runtime.last_reflexive_outcome
        temporal = runtime.last_temporal_identity_outcome
        historical_prior = runtime.last_historical_grounding_prior
        issued_historical_prior = (
            runtime.last_issued_historical_grounding_prior
        )
        historical_prior_compatibility = (
            runtime.last_historical_prior_compatibility
        )
        temporal_action_authorization = (
            runtime.last_temporal_action_authorization_digest
        )
        if result is None or grounding is None or reflexive is None or temporal is None:
            raise RuntimeError("v0.41 row arrived without successor telemetry")
        v039_row = _wrap_v039_row(
            row,
            grounding=grounding,
            causal_access_updated=result.causal_access_updated,
            causal_access_updates=result.causal_access_update_count,
            access_fault_active_evaluator_only=bool(
                inject_access_fault
                and row["phase"] == V041_ACCESS_FAULT_PHASE
                and V041_ACCESS_FAULT_START_OFFSET
                <= int(row["phase_offset"])
                < V041_ACCESS_FAULT_START_OFFSET + V039_ACCESS_FAULT_STEPS
            ),
        )
        v040_row = _wrap_v040_row(
            v039_row,
            grounding=grounding,
            reflexive=reflexive,
        )
        wrapped = _wrap_v041_row(
            v040_row,
            grounding=grounding,
            reflexive=reflexive,
            temporal=temporal,
            historical_prior=historical_prior,
            issued_historical_prior=issued_historical_prior,
            historical_prior_compatibility=historical_prior_compatibility,
            history_policy=runtime.temporal_identity.config.history_policy,
            temporal_action_authorization=temporal_action_authorization,
            world_variant_evaluator_only=world_variant,
        )
        wrapped_rows.append(wrapped)
        if sealed_row_sink is not None:
            sealed_row_sink(wrapped)

    _, engine_summary = run_post_change_closure_trace(
        int(seed),
        experiment_config=experiment_config,
        boundary_config=boundary_config,
        runtime_config=runtime_config,
        agent_factory=agent_factory,
        runtime_factory=runtime_factory,
        pre_step_hook=pre_step_hook,
        phase_truth_factory=_v041_phase_truth,
        summary_factory=_minimal_engine_summary,
        task_return_multiplier_factory=lambda config, world, phase: (
            _v041_task_return_multiplier(
                config,
                world,
                phase,
                world_variant=world_variant,
            )
        ),
        sealed_row_sink=row_sink,
    )
    if len(created_agents) != 1 or len(created_runtimes) != 1:
        raise RuntimeError("v0.41 did not retain one persistent runtime")
    summary = _build_v041_summary(
        int(seed),
        wrapped_rows,
        engine_summary,
        created_runtimes[0],
        created_agents[0],
        experiment_config,
        world_variant,
    )
    return wrapped_rows, summary


__all__ = [
    "V041_D1_CONFIG",
    "V041_DEVELOPMENT_SEED",
    "V041ExperimentConfig",
    "V041_ROW_SCHEMA",
    "V041_SUMMARY_SCHEMA",
    "V041WorldVariant",
    "run_temporal_self_identity_trace",
]
