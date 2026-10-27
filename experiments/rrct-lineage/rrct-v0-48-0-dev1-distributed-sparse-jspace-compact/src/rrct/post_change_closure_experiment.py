"""RRCT v0.37 post-change functional-closure experiment.

This successor to the v0.36 pilot asks whether a newly discovered causal
boundary becomes functionally usable *after* hidden remapping and restoration,
and whether a disconnected boundary is retired before a fixed null tail.  It
keeps one live :class:`~rrct.unified_causal_loop.UnifiedCausalLoop` instance
throughout the entire trace.

The live policy also uses the transition model in a sealed one-step
counterfactual rollout.  Three evaluator-side downstream controls receive the
same public-certificate stream but either remove it, freeze its phase-entry
state, or shuffle its public identity.  The controls never feed information
back into the live runtime.

This is an exploratory engineering experiment.  It does not detect or
establish phenomenal awareness, sentience, valence, personhood, or moral
status.
"""

from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
import math
import os
import platform
import re
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from .causal_boundary import CausalBoundaryConfig
from .agent import RRCTAgent
from .unified_causal_loop import (
    ActionCandidate,
    ActionSelectionReceipt,
    PublicBoundaryCertificate,
    UnifiedCausalLoop,
    UnifiedCausalLoopConfig,
    _DiscountedRidge,
)
from .unified_causal_loop_experiment import (
    HardIntegrityError,
    V036_ACTIONS,
    V036_ACTION_DIM,
    V036_ACTION_KEYS,
    V036_CONTEXT_DIM,
    V036_HANDLE_COUNT,
    V036_OBSERVATION_DIM,
    V036_PROCESS_DIM,
    V036_SOURCE_COUNT,
    V036ExperimentConfig,
    _HiddenWorld,
    _PhaseTruth,
    _DurableRowStream,
    _action_candidates,
    _agent,
    _array_sha256,
    _boundary_config,
    _build_summary,
    _certificate_pair,
    _draw_process_bank_with_replay_receipt,
    _exclusive_json,
    _fsync_directory,
    _jsonl_row_bytes,
    _json_sha256,
    _jsonable,
    _pair_json,
    _phase_truth,
    _reveal_row,
    _row_hard_integrity,
    _stream_seed,
    _task_context,
    _hidden_world,
)

FloatArray = NDArray[np.float64]
ControlName = Literal["no_certificate", "phase_stale", "shuffled_certificate"]

V037_VERSION = "0.37.0.dev1"
V037_SCHEMA = "rrct.v037.post_change_closure.row.v1"
V037_SUMMARY_SCHEMA = "rrct.v037.post_change_closure.summary.v1"
V037_PILOT_SEEDS = (7301, 7307, 7313, 7319)
V037_FIRST_PILOT_SEED = V037_PILOT_SEEDS[0]
V037_CONTROL_NAMES: tuple[ControlName, ...] = (
    "no_certificate",
    "phase_stale",
    "shuffled_certificate",
)
V037_CONTROL_STREAM_TAGS: Mapping[ControlName, int] = {
    "no_certificate": 370_101,
    "phase_stale": 370_102,
    "shuffled_certificate": 370_103,
}
V037_RECOVERY_TAIL_STEPS = 480
V037_MAX_ALARM_LATENCY = 240
V037_MAX_PRIVATE_CHANGE_LATENCY = 960
V037_MAX_PUBLIC_RELEASE_DELAY = 5
V037_MAX_STALE_RETIREMENT_DELAY = 1
V037_MIN_CORRECT_TAIL_ACTIONS = 400
V037_MIN_CONTROL_RETURN_MARGIN = 0.15
V037_MAX_FINAL_RETURN_MSE = 0.08
V037_TRANSITION_ROLLOUT_WEIGHT = 0.35
V037_ROWS_ARTIFACT = "v037_post_change_closure_rows.jsonl"
V037_SUMMARY_ARTIFACT = "v037_post_change_closure_summary.json"
V037_RUN_START_RECEIPT = "v037_run_start_receipt.json"
V037_RUN_FAILURE_RECEIPT = "v037_run_failure_receipt.json"
V037_ATTEMPT_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
V037_PROJECT_ROOT = Path(__file__).resolve().parents[2]
V037_CAMPAIGN_ROOT = (
    V037_PROJECT_ROOT / "validation" / "v0.37_post_change_closure_campaign"
).resolve()
V037_FREEZE_MANIFEST = (
    V037_PROJECT_ROOT / "validation" / "V0_37_PREOUTCOME_FREEZE.json"
)
V037_FREEZE_CHECKSUM = (
    V037_PROJECT_ROOT / "validation" / "V0_37_PREOUTCOME_FREEZE.json.sha256"
)
V037_REQUIRED_FREEZE_FILES = (
    "pyproject.toml",
    "src/rrct/_version.py",
    "src/rrct/__init__.py",
    "src/rrct/unified_causal_loop.py",
    "src/rrct/unified_causal_loop_experiment.py",
    "src/rrct/post_change_closure_experiment.py",
    "tests/test_v036_development_protocol_spec.py",
    "tests/test_v036_unified_causal_loop.py",
    "tests/test_v037_post_change_closure.py",
    "validation/V0_37_POST_CHANGE_CLOSURE_PROTOCOL.md",
    "validation/V0_37_PILOT_ATTEMPTS.md",
    "validation/V0_37_SEED_REGISTRY.json",
    "validation/V0_37_PREEXECUTION_VALIDATION.json",
    "validation/V0_37_SOURCE_SHA256SUMS.txt",
)


@dataclass(frozen=True)
class V037ExperimentConfig(V036ExperimentConfig):
    """Fixed D1 schedule with an action tail after every structural decision."""

    stable_steps: int = 1_440
    world_shock_steps: int = 480
    remap_steps: int = 1_440
    disconnect_steps: int = 1_440
    restore_steps: int = 1_440
    recovery_tail_steps: int = V037_RECOVERY_TAIL_STEPS
    confirmation_budget_steps: int = 960

    def __post_init__(self) -> None:
        super().__post_init__()
        if isinstance(self.recovery_tail_steps, (bool, np.bool_)) or not isinstance(
            self.recovery_tail_steps, (int, np.integer)
        ):
            raise TypeError("recovery_tail_steps must be a positive integer")
        tail = int(self.recovery_tail_steps)
        if tail <= 0:
            raise ValueError("recovery_tail_steps must be a positive integer")
        object.__setattr__(self, "recovery_tail_steps", tail)
        if isinstance(self.confirmation_budget_steps, (bool, np.bool_)) or not isinstance(
            self.confirmation_budget_steps, (int, np.integer)
        ):
            raise TypeError("confirmation_budget_steps must be a positive integer")
        confirmation = int(self.confirmation_budget_steps)
        if confirmation <= 0:
            raise ValueError("confirmation_budget_steps must be a positive integer")
        object.__setattr__(self, "confirmation_budget_steps", confirmation)
        for name in ("remap_steps", "disconnect_steps", "restore_steps"):
            if int(getattr(self, name)) < confirmation + tail:
                raise ValueError(
                    f"{name} must reserve the confirmation budget plus the recovery tail"
                )


V037_D1_CONFIG = V037ExperimentConfig()


@dataclass(frozen=True)
class _ShadowSelection:
    time: int
    certificate_pair: tuple[int, int] | None
    certificate_rank: int
    observation: FloatArray
    context: FloatArray
    candidate_designs: FloatArray
    predicted_next_observations: FloatArray
    predicted_external_returns: FloatArray
    counterfactual_no_certificate_returns: FloatArray
    public_boundary_value_advantage: float
    one_step_rollout_values: FloatArray
    one_step_rollout_best_next_keys: tuple[str, ...]
    base_policy_scores: FloatArray
    policy_scores: FloatArray
    no_rollout_propensities: FloatArray
    propensities: FloatArray
    selected_index: int
    selected_key: str
    selected_action: FloatArray
    selected_propensity: float


@dataclass(frozen=True)
class _ShadowOutcome:
    transition_prediction_error: float
    predicted_external_return: float
    return_prediction_error: float
    inverse_propensity_weight: float


@dataclass(frozen=True)
class _ShadowPending:
    selection: _ShadowSelection
    next_observation: FloatArray
    realized_return: float
    gated_oracle_return: float
    task_opportunity_oracle: float
    gated_action_regret: float
    task_opportunity_regret: float
    gate_open: bool
    observation_noise_sha256: str
    return_noise: float
    task_return_multiplier: float


@dataclass(frozen=True)
class _V037Pending:
    transition_index: int
    phase: _PhaseTruth
    hidden_exogenous_source: int
    observation: FloatArray
    context: FloatArray
    process_bank: FloatArray
    process_bank_sha256: str
    process_bank_receipt: Any
    process_bank_commitment: Any
    step: Any
    next_observation: FloatArray
    realized_return: float
    oracle_return: float
    action_regret: float
    task_opportunity_oracle: float
    task_opportunity_regret: float
    action_gate_open: bool
    running_mean_return_prediction: float
    running_mean_return_observation_count: int
    controls: Mapping[ControlName, _ShadowPending]
    observation_noise_sha256: str
    return_noise: float
    task_return_multiplier: float


def _policy_propensities(
    scores: FloatArray,
    config: UnifiedCausalLoopConfig,
) -> FloatArray:
    values = np.asarray(scores, dtype=np.float64)
    logits = (values - float(np.max(values))) / config.policy_temperature
    logits = np.clip(logits, -60.0, 0.0)
    softmax = np.exp(logits)
    softmax /= float(np.sum(softmax))
    count = len(values)
    mixed = (
        (1.0 - config.exploration_probability) * softmax
        + config.exploration_probability / count
    )
    floor = config.minimum_propensity
    propensities = floor + (1.0 - count * floor) * mixed
    propensities /= float(np.sum(propensities))
    return np.asarray(propensities, dtype=np.float64)


def _certificate_identity(
    certificate: PublicBoundaryCertificate | None,
) -> FloatArray:
    result = np.zeros(1 + V036_HANDLE_COUNT + V036_SOURCE_COUNT, dtype=np.float64)
    if certificate is not None:
        result[0] = 1.0
        handle_index, source_index = certificate.pair
        result[1 + int(handle_index)] = 1.0
        result[1 + V036_HANDLE_COUNT + int(source_index)] = 1.0
    return result


def _shadow_design(
    observation: FloatArray,
    context: FloatArray,
    candidate: ActionCandidate,
    certificate: PublicBoundaryCertificate | None,
) -> FloatArray:
    """Mirror the live public action design, with candidate previews fixed null."""

    if certificate is None:
        rank = confidence = uncertainty = change_alarm = 0.0
    else:
        maximum_rank = max(1, min(V036_PROCESS_DIM, V036_OBSERVATION_DIM))
        rank = float(certificate.rank) / maximum_rank
        confidence = float(certificate.confidence)
        uncertainty = float(certificate.uncertainty)
        change_alarm = float(certificate.change_alarm)
    route_strength = 0.0
    identity = _certificate_identity(certificate)
    scalars = np.asarray(
        [
            np.tanh(candidate.immediate_external_value),
            np.tanh(candidate.alternative_competence),
            np.tanh(route_strength),
            rank,
            confidence,
            uncertainty,
            change_alarm,
        ],
        dtype=np.float64,
    )
    certificate_scalars = np.asarray(
        [
            np.tanh(route_strength),
            rank,
            confidence,
            uncertainty,
            change_alarm,
        ],
        dtype=np.float64,
    )
    action_context = np.outer(candidate.action, np.tanh(context)).reshape(-1)
    action_observation = np.outer(
        candidate.action, np.tanh(observation)
    ).reshape(-1)
    action_squared = np.square(candidate.action)
    action_certificate = np.outer(
        candidate.action, certificate_scalars
    ).reshape(-1)
    action_context_when_public = action_context * identity[0]
    action_identity = np.outer(candidate.action, identity).reshape(-1)
    return np.concatenate(
        (
            np.ones(1, dtype=np.float64),
            np.tanh(observation),
            np.tanh(context),
            candidate.action,
            scalars,
            identity,
            action_context,
            action_observation,
            action_squared,
            action_certificate,
            action_context_when_public,
            action_identity,
        )
    )


class _ShadowPolicy:
    """Downstream policy control with no private boundary learner."""

    def __init__(
        self,
        name: ControlName,
        config: UnifiedCausalLoopConfig,
        *,
        seed: int,
    ) -> None:
        self.name = name
        self.config = config
        probe = _shadow_design(
            np.zeros(V036_OBSERVATION_DIM, dtype=np.float64),
            np.zeros(V036_CONTEXT_DIM, dtype=np.float64),
            _action_candidates()[0],
            None,
        )
        self.design_dim = int(len(probe))
        self.transition_model = _DiscountedRidge(
            self.design_dim,
            V036_OBSERVATION_DIM,
            ridge=config.model_ridge,
            discount=config.model_discount,
        )
        self.return_model = _DiscountedRidge(
            self.design_dim,
            1,
            ridge=config.model_ridge,
            discount=config.model_discount,
        )
        self.rng = np.random.default_rng(seed)

    def select(
        self,
        *,
        time: int,
        observation: FloatArray,
        context: FloatArray,
        certificate: PublicBoundaryCertificate | None,
    ) -> _ShadowSelection:
        candidates = _action_candidates()
        designs = np.stack(
            [
                _shadow_design(observation, context, candidate, certificate)
                for candidate in candidates
            ]
        )
        predicted_next = np.asarray(
            designs @ self.transition_model.coefficients(), dtype=np.float64
        )
        predicted_returns = np.asarray(
            (designs @ self.return_model.coefficients())[:, 0], dtype=np.float64
        )
        null_designs = np.stack(
            [
                _shadow_design(observation, context, candidate, None)
                for candidate in candidates
            ]
        )
        null_returns = np.asarray(
            (null_designs @ self.return_model.coefficients())[:, 0],
            dtype=np.float64,
        )
        boundary_advantage = (
            0.0
            if certificate is None
            else float(np.max(predicted_returns) - np.max(null_returns))
        )
        bounded = np.clip(
            predicted_returns,
            -self.config.candidate_value_bound,
            self.config.candidate_value_bound,
        )
        rollout_values = np.zeros(len(candidates), dtype=np.float64)
        best_next_keys = [candidates[0].key for _ in candidates]
        if self.config.transition_rollout_weight > 0.0:
            for first_index, next_observation in enumerate(predicted_next):
                future_designs = np.stack(
                    [
                        _shadow_design(
                            np.asarray(next_observation, dtype=np.float64),
                            context,
                            candidate,
                            certificate,
                        )
                        for candidate in candidates
                    ]
                )
                future_returns = np.asarray(
                    (future_designs @ self.return_model.coefficients())[:, 0],
                    dtype=np.float64,
                )
                future_returns = np.clip(
                    future_returns,
                    -self.config.candidate_value_bound,
                    self.config.candidate_value_bound,
                )
                future_scores = np.asarray(
                    [
                        candidate.immediate_external_value
                        + max(
                            float(future_returns[index]),
                            candidate.alternative_competence,
                        )
                        for index, candidate in enumerate(candidates)
                    ],
                    dtype=np.float64,
                )
                best_index = int(np.argmax(future_scores))
                rollout_values[first_index] = float(future_scores[best_index])
                best_next_keys[first_index] = candidates[best_index].key
        base_scores = np.asarray(
            [
                candidate.immediate_external_value
                + max(float(bounded[index]), candidate.alternative_competence)
                for index, candidate in enumerate(candidates)
            ],
            dtype=np.float64,
        )
        scores = base_scores + self.config.transition_rollout_weight * np.clip(
            rollout_values,
            -self.config.candidate_value_bound,
            self.config.candidate_value_bound,
        )
        no_rollout_propensities = _policy_propensities(base_scores, self.config)
        propensities = _policy_propensities(scores, self.config)
        selected_index = int(self.rng.choice(len(candidates), p=propensities))
        selected = candidates[selected_index]
        return _ShadowSelection(
            time=int(time),
            certificate_pair=_certificate_pair(certificate),
            certificate_rank=0 if certificate is None else int(certificate.rank),
            observation=np.asarray(observation, dtype=np.float64).copy(),
            context=np.asarray(context, dtype=np.float64).copy(),
            candidate_designs=designs,
            predicted_next_observations=predicted_next,
            predicted_external_returns=predicted_returns,
            counterfactual_no_certificate_returns=null_returns,
            public_boundary_value_advantage=boundary_advantage,
            one_step_rollout_values=rollout_values,
            one_step_rollout_best_next_keys=tuple(best_next_keys),
            base_policy_scores=base_scores,
            policy_scores=scores,
            no_rollout_propensities=no_rollout_propensities,
            propensities=propensities,
            selected_index=selected_index,
            selected_key=selected.key,
            selected_action=np.asarray(selected.action, dtype=np.float64).copy(),
            selected_propensity=float(propensities[selected_index]),
        )

    def reveal(self, pending: _ShadowPending) -> _ShadowOutcome:
        selection = pending.selection
        design = selection.candidate_designs[selection.selected_index]
        predicted_next = selection.predicted_next_observations[
            selection.selected_index
        ]
        predicted_return = float(
            selection.predicted_external_returns[selection.selected_index]
        )
        transition_error = float(
            np.linalg.norm(pending.next_observation - predicted_next)
            / math.sqrt(V036_OBSERVATION_DIM)
        )
        return_error = float(pending.realized_return - predicted_return)
        inverse_weight = min(
            1.0 / selection.selected_propensity,
            self.config.maximum_inverse_propensity,
        )
        self.transition_model.update(
            design, pending.next_observation, weight=inverse_weight
        )
        self.return_model.update(
            design,
            np.asarray([pending.realized_return], dtype=np.float64),
            weight=inverse_weight,
        )
        return _ShadowOutcome(
            transition_prediction_error=transition_error,
            predicted_external_return=predicted_return,
            return_prediction_error=return_error,
            inverse_propensity_weight=float(inverse_weight),
        )

    def counts(self) -> dict[str, int]:
        return {
            "transition": int(self.transition_model.observation_count),
            "return": int(self.return_model.observation_count),
        }


def _shuffled_certificate(
    certificate: PublicBoundaryCertificate | None,
) -> PublicBoundaryCertificate | None:
    if certificate is None:
        return None
    handle, source = certificate.pair
    pair = (
        (int(handle) + 1) % V036_HANDLE_COUNT,
        (int(source) + 1) % V036_SOURCE_COUNT,
    )
    payload = {
        "schema": "rrct.v037.shuffled_public_certificate.v1",
        "source_digest": certificate.digest,
        "pair": pair,
    }
    return replace(
        certificate,
        pair=pair,
        digest=_json_sha256(payload),
    )


def _control_certificate(
    name: ControlName,
    live_certificate: PublicBoundaryCertificate | None,
    stale_certificate: PublicBoundaryCertificate | None,
) -> PublicBoundaryCertificate | None:
    if name == "no_certificate":
        return None
    if name == "phase_stale":
        return copy.deepcopy(stale_certificate)
    if name == "shuffled_certificate":
        return _shuffled_certificate(live_certificate)
    raise ValueError(f"unknown control {name!r}")


def _world_transition_with_shared_noise(
    config: V037ExperimentConfig,
    world: _HiddenWorld,
    phase: _PhaseTruth,
    observation: FloatArray,
    process_bank: FloatArray,
    handles: FloatArray,
    action: FloatArray,
    context: FloatArray,
    certificate_pair: tuple[int, int] | None,
    observation_noise: FloatArray,
    return_noise: float,
    task_return_multiplier: float = 1.0,
) -> tuple[FloatArray, float, float, float, float, float, bool]:
    """Apply one arm using noise fixed before any arm-specific consequence."""

    exogenous = (
        phase.exogenous_multiplier
        * process_bank[world.exogenous_source]
        @ world.exogenous_effect
    )
    routed = np.zeros(V036_OBSERVATION_DIM, dtype=np.float64)
    if phase.pair is not None and phase.effect is not None:
        handle, source = phase.pair
        routed = handles[handle] * process_bank[source] @ phase.effect
    gate_open = bool(phase.pair is not None and certificate_pair == phase.pair)
    action_observation = (
        action @ world.action_effect
        if gate_open
        else np.zeros(V036_OBSERVATION_DIM, dtype=np.float64)
    )
    next_observation = (
        config.observation_persistence * observation
        + exogenous
        + routed
        + action_observation
        + observation_noise
    )
    task_returns = np.zeros(len(V036_ACTIONS), dtype=np.float64)
    if phase.pair is not None:
        task_returns = float(task_return_multiplier) * (
            config.task_return_scale * (V036_ACTIONS @ context)
            - config.action_cost * np.sum(V036_ACTIONS * V036_ACTIONS, axis=1)
        )
    gated_returns = task_returns if gate_open else np.zeros_like(task_returns)
    selected_matches = np.all(V036_ACTIONS == action[None, :], axis=1)
    if int(np.sum(selected_matches)) != 1:
        raise RuntimeError("selected action is not one of the fixed candidates")
    selected_index = int(np.flatnonzero(selected_matches)[0])
    selected_noiseless = float(gated_returns[selected_index])
    gated_oracle = float(np.max(gated_returns))
    opportunity_oracle = float(np.max(task_returns))
    realized_return = selected_noiseless + float(return_noise)
    return (
        np.asarray(next_observation, dtype=np.float64),
        realized_return,
        gated_oracle,
        gated_oracle - selected_noiseless,
        opportunity_oracle,
        opportunity_oracle - selected_noiseless,
        gate_open,
    )


def _runtime_config_v037(run_seed: int) -> UnifiedCausalLoopConfig:
    base = UnifiedCausalLoopConfig(
        context_dim=V036_CONTEXT_DIM,
        exploration_probability=0.15,
        policy_temperature=0.35,
        minimum_propensity=0.01,
        maximum_inverse_propensity=20.0,
        model_ridge=0.50,
        model_discount=0.997,
        transition_rollout_weight=V037_TRANSITION_ROLLOUT_WEIGHT,
        candidate_value_bound=1_000.0,
        drift_capacity=960,
        drift_baseline_samples=240,
        drift_recent_samples=240,
        drift_fit_interval=40,
        drift_ridge=0.50,
        drift_threshold=0.30,
        quarantine_public_certificate_on_drift=True,
        seed=_stream_seed(run_seed, 36_005),
    )
    return base


def _rollout_row(selection: ActionSelectionReceipt) -> dict[str, Any]:
    rollout = np.asarray(selection.one_step_rollout_values, dtype=np.float64)
    scores = np.asarray(selection.policy_scores, dtype=np.float64)
    base_scores = scores - selection.transition_rollout_weight * rollout
    no_rollout_propensities = _policy_propensities(
        base_scores,
        UnifiedCausalLoopConfig(
            context_dim=V036_CONTEXT_DIM,
            exploration_probability=0.15,
            policy_temperature=0.35,
            minimum_propensity=0.01,
            maximum_inverse_propensity=20.0,
            model_ridge=0.50,
            model_discount=0.997,
            transition_rollout_weight=selection.transition_rollout_weight,
            candidate_value_bound=1_000.0,
            drift_capacity=960,
            drift_baseline_samples=240,
            drift_recent_samples=240,
            drift_fit_interval=40,
            drift_ridge=0.50,
            drift_threshold=0.30,
        ),
    )
    propensities = np.asarray(selection.propensities, dtype=np.float64)
    return {
        "transition_rollout_weight": float(selection.transition_rollout_weight),
        "one_step_rollout_values": rollout.tolist(),
        "one_step_rollout_best_next_keys": list(
            selection.one_step_rollout_best_next_keys
        ),
        "base_policy_scores_without_rollout": base_scores.tolist(),
        "policy_score_reconstruction_valid": bool(
            np.allclose(
                scores,
                base_scores + selection.transition_rollout_weight * rollout,
                rtol=0.0,
                atol=1e-12,
            )
        ),
        "no_rollout_propensities": no_rollout_propensities.tolist(),
        "rollout_propensity_l1_shift": float(
            np.sum(np.abs(propensities - no_rollout_propensities))
        ),
        "rollout_changes_greedy_action": bool(
            int(np.argmax(scores)) != int(np.argmax(base_scores))
        ),
        "counterfactual_no_certificate_returns": (
            selection.counterfactual_no_certificate_returns.tolist()
        ),
        "public_boundary_value_advantage": float(
            selection.public_boundary_value_advantage
        ),
    }


def _control_row(
    pending: _ShadowPending,
    outcome: _ShadowOutcome,
) -> dict[str, Any]:
    selection = pending.selection
    return {
        "certificate_pair": _pair_json(selection.certificate_pair),
        "certificate_rank": int(selection.certificate_rank),
        "selected_action_index": int(selection.selected_index),
        "selected_action_key": selection.selected_key,
        "selected_action": selection.selected_action.tolist(),
        "selected_propensity": float(selection.selected_propensity),
        "action_propensities": selection.propensities.tolist(),
        "no_rollout_propensities": selection.no_rollout_propensities.tolist(),
        "predicted_external_returns": (
            selection.predicted_external_returns.tolist()
        ),
        "counterfactual_no_certificate_returns": (
            selection.counterfactual_no_certificate_returns.tolist()
        ),
        "public_boundary_value_advantage": float(
            selection.public_boundary_value_advantage
        ),
        "one_step_rollout_values": selection.one_step_rollout_values.tolist(),
        "one_step_rollout_best_next_keys": list(
            selection.one_step_rollout_best_next_keys
        ),
        "base_policy_scores_without_rollout": (
            selection.base_policy_scores.tolist()
        ),
        "policy_scores": selection.policy_scores.tolist(),
        "rollout_propensity_l1_shift": float(
            np.sum(
                np.abs(
                    selection.propensities
                    - selection.no_rollout_propensities
                )
            )
        ),
        "rollout_changes_greedy_action": bool(
            int(np.argmax(selection.policy_scores))
            != int(np.argmax(selection.base_policy_scores))
        ),
        "gate_open_evaluator_only": bool(pending.gate_open),
        "realized_external_return": float(pending.realized_return),
        "gated_oracle_return_evaluator_only": float(
            pending.gated_oracle_return
        ),
        "task_opportunity_oracle_evaluator_only": float(
            pending.task_opportunity_oracle
        ),
        "gated_action_regret_evaluator_only": float(
            pending.gated_action_regret
        ),
        "task_opportunity_regret_evaluator_only": float(
            pending.task_opportunity_regret
        ),
        "task_return_multiplier_evaluator_only": float(
            pending.task_return_multiplier
        ),
        "predicted_selected_return": float(
            outcome.predicted_external_return
        ),
        "return_prediction_error": float(outcome.return_prediction_error),
        "transition_prediction_error": float(
            outcome.transition_prediction_error
        ),
        "inverse_propensity_weight": float(outcome.inverse_propensity_weight),
        "observation_noise_sha256": pending.observation_noise_sha256,
        "return_noise": float(pending.return_noise),
    }


def _seal_v037_row_or_stop(
    row: dict[str, Any],
    sealed_row_sink: Callable[[Mapping[str, Any]], None] | None,
) -> None:
    checks = dict(_row_hard_integrity(row))
    rollout = row["transition_rollout"]
    controls = row["controls"]
    action_gate = row["action_public_gate_receipt"]
    public_gate = row["public_gate_after_reveal"]
    checks.update(
        {
            "v037_schema": row.get("schema") == V037_SCHEMA,
            "rollout_weight_positive": float(
                rollout["transition_rollout_weight"]
            ) > 0.0,
            "rollout_score_reconstruction": bool(
                rollout["policy_score_reconstruction_valid"]
            ),
            "rollout_payload_finite": bool(
                np.all(
                    np.isfinite(
                        np.asarray(
                            rollout["one_step_rollout_values"],
                            dtype=np.float64,
                        )
                    )
                )
                and np.isfinite(
                    float(rollout["rollout_propensity_l1_shift"])
                )
                and np.isfinite(
                    float(rollout["public_boundary_value_advantage"])
                )
            ),
            "shared_noise_bound": bool(
                all(
                    arm["observation_noise_sha256"]
                    == row["observation_noise_sha256"]
                    and arm["return_noise"] == row["return_noise"]
                    for arm in controls.values()
                )
            ),
            "control_names_exact": set(controls) == set(V037_CONTROL_NAMES),
            "public_gate_quarantine_enabled": bool(
                action_gate["quarantine_enabled"]
                and public_gate is not None
                and public_gate["quarantine_enabled"]
            ),
            "action_gate_certificate_binding": (
                action_gate["effective_certificate_digest"]
                == row["action_public_certificate_digest"]
            ),
            "reveal_gate_certificate_binding": (
                public_gate is not None
                and public_gate["effective_certificate_digest"]
                == row["public_certificate_after_reveal"]
            ),
            "control_payloads_finite": bool(
                all(
                    np.isfinite(float(arm["realized_external_return"]))
                    and np.isfinite(float(arm["return_prediction_error"]))
                    and np.isfinite(float(arm["transition_prediction_error"]))
                    and np.isclose(
                        float(np.sum(arm["action_propensities"])), 1.0
                    )
                    and float(np.min(arm["action_propensities"])) >= 0.01
                    and float(arm["inverse_propensity_weight"]) <= 20.0
                    for arm in controls.values()
                )
            ),
        }
    )
    row["hard_integrity_checks"] = checks
    row["hard_integrity_valid"] = bool(all(checks.values()))
    if not row["hard_integrity_valid"]:
        row["failure_row_schema"] = "rrct.v037.hard_integrity_failure_row.v1"
    if sealed_row_sink is not None:
        sealed_row_sink(row)
    if not row["hard_integrity_valid"]:
        failed = ", ".join(name for name, valid in checks.items() if not valid)
        raise HardIntegrityError(
            "v0.37 hard-integrity failure after sealing transition "
            f"{row['transition_index']}: {failed}"
        )


def _first_offset(
    rows: Sequence[Mapping[str, Any]],
    predicate: Callable[[Mapping[str, Any]], bool],
) -> int | None:
    for row in rows:
        if predicate(row):
            return int(row["phase_offset"]) + 1
    return None


def _mse(rows: Sequence[Mapping[str, Any]], key: str) -> float:
    values = [float(row[key]) ** 2 for row in rows]
    return 0.0 if not values else float(np.mean(values))


def _mean(rows: Sequence[Mapping[str, Any]], key: str) -> float:
    values = [float(row[key]) for row in rows]
    return 0.0 if not values else float(np.mean(values))


def _tail_summary(
    rows: Sequence[Mapping[str, Any]],
    tail_steps: int,
) -> dict[str, Any]:
    tail = list(rows[-tail_steps:])
    split = max(1, len(tail) // 2)
    controls: dict[str, Any] = {}
    for name in V037_CONTROL_NAMES:
        controls[name] = {
            "mean_external_return": float(
                np.mean(
                    [
                        float(row["controls"][name]["realized_external_return"])
                        for row in tail
                    ]
                )
            ),
            "mean_task_opportunity_regret": float(
                np.mean(
                    [
                        float(
                            row["controls"][name][
                                "task_opportunity_regret_evaluator_only"
                            ]
                        )
                        for row in tail
                    ]
                )
            ),
            "gate_open_fraction": float(
                np.mean(
                    [
                        bool(row["controls"][name]["gate_open_evaluator_only"])
                        for row in tail
                    ]
                )
            ),
            "return_mse": float(
                np.mean(
                    [
                        float(row["controls"][name]["return_prediction_error"])
                        ** 2
                        for row in tail
                    ]
                )
            ),
        }
    return {
        "rows": len(tail),
        "correct_gated_actions": int(
            sum(bool(row["action_gate_open_evaluator_only"]) for row in tail)
        ),
        "action_gate_open_fraction": float(
            np.mean([bool(row["action_gate_open_evaluator_only"]) for row in tail])
        ),
        "action_public_exact_fraction": float(
            np.mean(
                [bool(row["action_public_exact_evaluator_only"]) for row in tail]
            )
        ),
        "action_public_null_fraction": float(
            np.mean([row["action_public_pair"] is None for row in tail])
        ),
        "mean_external_return": _mean(tail, "realized_external_return"),
        "mean_task_opportunity_regret": _mean(
            tail, "task_opportunity_regret_evaluator_only"
        ),
        "return_mse_first_half": _mse(
            tail[:split], "return_prediction_error"
        ),
        "return_mse_second_half": _mse(
            tail[split:], "return_prediction_error"
        ),
        "transition_mse_first_half": _mse(
            tail[:split], "transition_prediction_error"
        ),
        "transition_mse_second_half": _mse(
            tail[split:], "transition_prediction_error"
        ),
        "mean_public_boundary_value_advantage": float(
            np.mean(
                [
                    float(
                        row["transition_rollout"][
                            "public_boundary_value_advantage"
                        ]
                    )
                    for row in tail
                ]
            )
        ),
        "rollout_nonzero_propensity_shift_fraction": float(
            np.mean(
                [
                    float(
                        row["transition_rollout"][
                            "rollout_propensity_l1_shift"
                        ]
                    )
                    > 1e-12
                    for row in tail
                ]
            )
        ),
        "rollout_greedy_change_fraction": float(
            np.mean(
                [
                    bool(
                        row["transition_rollout"][
                            "rollout_changes_greedy_action"
                        ]
                    )
                    for row in tail
                ]
            )
        ),
        "controls": controls,
    }


def _change_summary(
    phase_rows: Sequence[Mapping[str, Any]],
    phase: str,
    tail_steps: int,
) -> dict[str, Any]:
    if phase == "remap":
        event_names = {"pair_revision", "rank_revision"}
        action_correct = lambda row: bool(row["action_gate_open_evaluator_only"])
    elif phase == "disconnect":
        event_names = {"revocation"}
        action_correct = lambda row: row["action_public_pair"] is None
    elif phase == "restore":
        event_names = {"acquisition"}
        action_correct = lambda row: bool(row["action_gate_open_evaluator_only"])
    else:
        raise ValueError(phase)
    alarm = _first_offset(phase_rows, lambda row: bool(row["reopen_requested"]))
    quarantine_entry = _first_offset(
        phase_rows,
        lambda row: row["public_gate_event_after_reveal"] == "entered",
    )
    private = _first_offset(
        phase_rows, lambda row: row["structural_event"] in event_names
    )
    alarm_row = next(
        (
            row
            for row in phase_rows
            if alarm is not None
            and int(row["phase_offset"]) + 1 == alarm
        ),
        None,
    )
    stale_digest = (
        None
        if alarm_row is None
        else alarm_row["action_public_certificate_digest"]
    )
    stale_retired = None
    stale_reuse_after_retirement = 0
    if alarm is not None and stale_digest is not None:
        stale_retired = _first_offset(
            phase_rows,
            lambda row: int(row["phase_offset"]) + 1 > alarm
            and row["action_public_certificate_digest"] != stale_digest,
        )
        if stale_retired is not None:
            stale_reuse_after_retirement = int(
                sum(
                    int(row["phase_offset"]) + 1 >= stale_retired
                    and row["action_public_certificate_digest"] == stale_digest
                    for row in phase_rows
                )
            )
    first_correct = None
    if private is not None:
        first_correct = _first_offset(
            phase_rows,
            lambda row: int(row["phase_offset"]) + 1 > private
            and action_correct(row),
        )
    return {
        "alarm_latency": alarm,
        "quarantine_entry_latency": quarantine_entry,
        "stale_action_retirement_latency": stale_retired,
        "stale_action_retirement_delay": (
            None
            if alarm is None or stale_retired is None
            else int(stale_retired - alarm)
        ),
        "stale_action_reuse_after_retirement_count": (
            stale_reuse_after_retirement
        ),
        "private_change_latency": private,
        "first_correct_action_latency": first_correct,
        "public_release_delay": (
            None
            if private is None or first_correct is None
            else int(first_correct - private)
        ),
        "tail": _tail_summary(phase_rows, tail_steps),
    }


def _build_v037_summary(
    seed: int,
    config: V037ExperimentConfig,
    boundary_config: CausalBoundaryConfig,
    runtime_config: UnifiedCausalLoopConfig,
    rows: Sequence[Mapping[str, Any]],
    runtime: UnifiedCausalLoop,
    runtime_instance_digest: str,
    phase_model_counts: Mapping[str, Mapping[str, int]],
    control_model_counts: Mapping[str, Mapping[str, Mapping[str, int]]],
) -> dict[str, Any]:
    base = _build_summary(
        seed,
        config,
        boundary_config,
        runtime_config,
        rows,
        runtime,
        runtime_instance_digest,
        phase_model_counts,
        unflushed_transition=bool(runtime.awaiting_outcome),
    )
    grouped = {
        name: [row for row in rows if row["phase"] == name]
        for name, _ in config.phase_steps
    }
    changes = {
        phase: _change_summary(
            grouped[phase], phase, config.recovery_tail_steps
        )
        for phase in ("remap", "disconnect", "restore")
    }
    stable_tail = _tail_summary(grouped["stable"], config.recovery_tail_steps)
    shock_tail = _tail_summary(
        grouped["world_shock"], min(config.recovery_tail_steps, len(grouped["world_shock"]))
    )

    remap_tail = changes["remap"]["tail"]
    disconnect_tail = changes["disconnect"]["tail"]
    restore_tail = changes["restore"]["tail"]

    def active_control_margin(tail: Mapping[str, Any]) -> float:
        return float(tail["mean_external_return"]) - max(
            float(tail["controls"][name]["mean_external_return"])
            for name in V037_CONTROL_NAMES
        )

    rollout_shift_fraction = float(
        np.mean(
            [
                float(
                    row["transition_rollout"]["rollout_propensity_l1_shift"]
                )
                > 1e-12
                for row in rows
            ]
        )
    )
    rollout_greedy_changes = int(
        sum(
            bool(
                row["transition_rollout"]["rollout_changes_greedy_action"]
            )
            for row in rows
        )
    )
    integrity = dict(base["integrity"])
    integrity.update(
        {
            "v037_row_schema_all": all(
                row["schema"] == V037_SCHEMA for row in rows
            ),
            "v037_controls_all_present": all(
                set(row["controls"]) == set(V037_CONTROL_NAMES) for row in rows
            ),
            "v037_rollout_all_reconstructed": all(
                bool(
                    row["transition_rollout"][
                        "policy_score_reconstruction_valid"
                    ]
                )
                for row in rows
            ),
            "v037_shared_noise_all": all(
                all(
                    row["controls"][name]["observation_noise_sha256"]
                    == row["observation_noise_sha256"]
                    and row["controls"][name]["return_noise"]
                    == row["return_noise"]
                    for name in V037_CONTROL_NAMES
                )
                for row in rows
            ),
            "v037_hard_integrity_all": all(
                bool(row["hard_integrity_valid"]) for row in rows
            ),
        }
    )
    endpoints = {
        "F01_integrity": bool(all(integrity.values())),
        "F02_initial_public_closure": bool(
            stable_tail["correct_gated_actions"]
            >= V037_MIN_CORRECT_TAIL_ACTIONS
            and stable_tail["action_public_exact_fraction"] >= 0.90
            and shock_tail["action_gate_open_fraction"] >= 0.90
        ),
        "F03_remap_latency_and_action_recovery": bool(
            changes["remap"]["alarm_latency"] is not None
            and int(changes["remap"]["alarm_latency"])
            <= V037_MAX_ALARM_LATENCY
            and changes["remap"]["quarantine_entry_latency"]
            == changes["remap"]["alarm_latency"]
            and changes["remap"]["stale_action_retirement_delay"] is not None
            and int(changes["remap"]["stale_action_retirement_delay"])
            <= V037_MAX_STALE_RETIREMENT_DELAY
            and int(
                changes["remap"][
                    "stale_action_reuse_after_retirement_count"
                ]
            )
            == 0
            and changes["remap"]["private_change_latency"] is not None
            and int(changes["remap"]["private_change_latency"])
            <= V037_MAX_PRIVATE_CHANGE_LATENCY
            and changes["remap"]["public_release_delay"] is not None
            and int(changes["remap"]["public_release_delay"])
            <= V037_MAX_PUBLIC_RELEASE_DELAY
            and remap_tail["correct_gated_actions"]
            >= V037_MIN_CORRECT_TAIL_ACTIONS
        ),
        "F04_disconnect_retirement_and_devaluation": bool(
            changes["disconnect"]["alarm_latency"] is not None
            and int(changes["disconnect"]["alarm_latency"])
            <= V037_MAX_ALARM_LATENCY
            and changes["disconnect"]["quarantine_entry_latency"]
            == changes["disconnect"]["alarm_latency"]
            and changes["disconnect"]["stale_action_retirement_delay"]
            is not None
            and int(
                changes["disconnect"]["stale_action_retirement_delay"]
            )
            <= V037_MAX_STALE_RETIREMENT_DELAY
            and int(
                changes["disconnect"][
                    "stale_action_reuse_after_retirement_count"
                ]
            )
            == 0
            and changes["disconnect"]["private_change_latency"] is not None
            and int(changes["disconnect"]["private_change_latency"])
            <= V037_MAX_PRIVATE_CHANGE_LATENCY
            and changes["disconnect"]["public_release_delay"] is not None
            and int(changes["disconnect"]["public_release_delay"])
            <= V037_MAX_PUBLIC_RELEASE_DELAY
            and disconnect_tail["action_public_null_fraction"] >= 0.90
            and abs(
                float(
                    disconnect_tail[
                        "mean_public_boundary_value_advantage"
                    ]
                )
            )
            <= 1e-12
        ),
        "F05_restoration_reacquisition_and_action_recovery": bool(
            changes["restore"]["alarm_latency"] is not None
            and int(changes["restore"]["alarm_latency"])
            <= V037_MAX_ALARM_LATENCY
            and changes["restore"]["private_change_latency"] is not None
            and int(changes["restore"]["private_change_latency"])
            <= V037_MAX_PRIVATE_CHANGE_LATENCY
            and changes["restore"]["public_release_delay"] is not None
            and int(changes["restore"]["public_release_delay"])
            <= V037_MAX_PUBLIC_RELEASE_DELAY
            and restore_tail["correct_gated_actions"]
            >= V037_MIN_CORRECT_TAIL_ACTIONS
        ),
        "F06_active_tail_control_separation": bool(
            active_control_margin(remap_tail)
            >= V037_MIN_CONTROL_RETURN_MARGIN
            and active_control_margin(restore_tail)
            >= V037_MIN_CONTROL_RETURN_MARGIN
        ),
        "F07_prequential_return_recovery": bool(
            float(remap_tail["return_mse_second_half"])
            < float(remap_tail["return_mse_first_half"])
            and float(remap_tail["return_mse_second_half"])
            <= V037_MAX_FINAL_RETURN_MSE
            and float(restore_tail["return_mse_second_half"])
            <= V037_MAX_FINAL_RETURN_MSE
        ),
        "F08_transition_rollout_functionally_active": bool(
            runtime_config.transition_rollout_weight > 0.0
            and rollout_shift_fraction >= 0.10
            and rollout_greedy_changes > 0
        ),
        "F09_boundary_value_devaluation_revaluation": bool(
            float(stable_tail["mean_public_boundary_value_advantage"]) > 0.0
            and abs(
                float(
                    disconnect_tail[
                        "mean_public_boundary_value_advantage"
                    ]
                )
            )
            <= 1e-12
            and float(restore_tail["mean_public_boundary_value_advantage"])
            > 0.0
        ),
        "F10_world_shock_specificity": bool(
            not any(
                bool(row["reopen_requested"])
                for row in grouped["world_shock"]
            )
            and not any(
                row["public_gate_event_after_reveal"] == "entered"
                or bool(row["public_quarantine_active_after_reveal"])
                for row in grouped["world_shock"]
            )
        ),
    }
    all_met = bool(all(endpoints.values()))
    status = (
        "EXPLORATORY_PILOT_ENDPOINTS_MET"
        if all_met
        else "EXPLORATORY_PILOT_ENDPOINTS_NOT_MET"
    )
    return {
        "schema": V037_SUMMARY_SCHEMA,
        "version": V037_VERSION,
        "scientific_status": "exploratory_single_seed_pilot",
        "seed": int(seed),
        "config": asdict(config),
        "causal_boundary_config": _jsonable(boundary_config),
        "unified_runtime_config": _jsonable(runtime_config),
        "runtime_instance_digest": runtime_instance_digest,
        "phase_summaries_v036_compatible": base["phase_summaries"],
        "stable_tail": stable_tail,
        "world_shock_tail": shock_tail,
        "post_change": changes,
        "control_return_margins": {
            "remap": active_control_margin(remap_tail),
            "restore": active_control_margin(restore_tail),
        },
        "rollout_audit": {
            "weight": runtime_config.transition_rollout_weight,
            "nonzero_propensity_shift_fraction": rollout_shift_fraction,
            "greedy_action_change_count": rollout_greedy_changes,
        },
        "phase_model_update_counts": _jsonable(phase_model_counts),
        "control_model_update_counts": _jsonable(control_model_counts),
        "integrity": integrity,
        "endpoints": endpoints,
        "earliest_failed_layer": next(
            (name for name, met in endpoints.items() if not met), None
        ),
        "all_endpoints_met": all_met,
        "status": status,
        "interpretation_boundary": (
            "Exploratory evidence for post-change functional closure and "
            "boundary-conditioned control in a bounded synthetic runtime; "
            "not evidence of phenomenal awareness, sentience, or valence."
        ),
    }


def run_post_change_closure_trace(
    seed: int,
    *,
    experiment_config: V037ExperimentConfig = V037_D1_CONFIG,
    boundary_config: CausalBoundaryConfig | None = None,
    runtime_config: UnifiedCausalLoopConfig | None = None,
    agent_factory: Callable[[CausalBoundaryConfig, int], RRCTAgent] | None = None,
    runtime_factory: (
        Callable[[RRCTAgent, UnifiedCausalLoopConfig], UnifiedCausalLoop]
        | None
    ) = None,
    pre_step_hook: (
        Callable[[int, _PhaseTruth, RRCTAgent, UnifiedCausalLoop], None]
        | None
    ) = None,
    phase_truth_factory: (
        Callable[[V037ExperimentConfig, _HiddenWorld, int], _PhaseTruth]
        | None
    ) = None,
    summary_factory: Callable[..., dict[str, Any]] | None = None,
    task_return_multiplier_factory: (
        Callable[[V037ExperimentConfig, _HiddenWorld, _PhaseTruth], float]
        | None
    ) = None,
    sealed_row_sink: Callable[[Mapping[str, Any]], None] | None = None,
    retain_rows: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run one uninterrupted D1 trace and all three downstream controls.

    ``retain_rows=False`` supports successor experiments that seal every row
    through ``sealed_row_sink`` while retaining only compact derived evidence.
    A custom ``summary_factory`` is required in that mode because the legacy
    summary builder expects the complete in-memory row sequence.
    """

    if not isinstance(retain_rows, bool):
        raise TypeError("retain_rows must be a bool")
    if not retain_rows and summary_factory is None:
        raise ValueError(
            "summary_factory is required when retain_rows is False"
        )
    seed = int(seed)
    boundary = boundary_config or _boundary_config(seed)
    runtime_cfg = runtime_config or _runtime_config_v037(seed)
    world = _hidden_world(seed, experiment_config)
    world_rng = np.random.default_rng(_stream_seed(seed, 36_004))
    bank_rng = np.random.default_rng(_stream_seed(seed, 36_006))
    context_rng = np.random.default_rng(_stream_seed(seed, 36_007))
    agent = (agent_factory or _agent)(boundary, seed)
    runtime = (
        UnifiedCausalLoop(agent, runtime_cfg)
        if runtime_factory is None
        else runtime_factory(agent, runtime_cfg)
    )
    runtime_identity = id(runtime)
    agent_identity = id(agent)
    runtime_instance_digest = runtime.snapshot()["digest"]

    controls = {
        name: _ShadowPolicy(
            name,
            runtime_cfg,
            seed=_stream_seed(seed, V037_CONTROL_STREAM_TAGS[name]),
        )
        for name in V037_CONTROL_NAMES
    }
    observation = world_rng.normal(0.0, 0.25, V036_OBSERVATION_DIM)
    control_observations = {
        name: observation.copy() for name in V037_CONTROL_NAMES
    }
    previous_return: float | None = None
    pending: _V037Pending | None = None
    rows: list[dict[str, Any]] = []
    phase_model_counts: dict[str, dict[str, int]] = {}
    control_model_counts: dict[str, dict[str, dict[str, int]]] = {}
    phase_lengths = dict(experiment_config.phase_steps)
    stale_by_phase: dict[str, PublicBoundaryCertificate | None] = {}
    running_return_sum = 0.0
    running_return_count = 0
    phase_resolver = phase_truth_factory or _phase_truth
    summary_builder = summary_factory or _build_v037_summary

    for transition_index in range(experiment_config.total_steps):
        phase = phase_resolver(experiment_config, world, transition_index)
        if pre_step_hook is not None:
            pre_step_hook(transition_index, phase, agent, runtime)
        bank, bank_receipt = _draw_process_bank_with_replay_receipt(
            bank_rng,
            energy=experiment_config.process_energy,
            sequence_id=transition_index,
        )
        bank_sha = _array_sha256(bank)
        bank_commitment = runtime.precommit_process_bank(bank)
        context = _task_context(context_rng)
        step = runtime.advance(
            observation,
            _action_candidates(),
            observable_context=context,
            realized_external_return=previous_return,
            source="v037_post_change_closure",
        )
        runtime_identity_ok = bool(
            id(runtime) == runtime_identity and id(agent) == agent_identity
        )

        control_outcomes: dict[ControlName, _ShadowOutcome] = {}
        if pending is not None:
            if step.previous_action_outcome is None:
                raise RuntimeError("pending live transition has no outcome")
            if step.causal_boundary_update is None:
                raise RuntimeError("pending live transition has no causal update")
            for name in V037_CONTROL_NAMES:
                control_outcomes[name] = controls[name].reveal(
                    pending.controls[name]
                )
            running_return_sum += float(pending.realized_return)
            running_return_count += 1
            agent_result = agent.last_result
            if agent_result is None:
                raise RuntimeError("agent emitted no step result")
            update = step.causal_boundary_update
            agent_update = agent_result.causal_boundary_update_receipt
            row = _reveal_row(
                pending,
                step.previous_action_outcome,
                step.drift,
                update,
                step.public_boundary,
                step.public_boundary_gate,
                runtime_instance_digest,
                runtime_identity_ok,
                interrupted_transitions=agent_result.causal_interrupted_transitions,
                sanitized_agent_audit_valid=bool(
                    agent_update is not None and agent_update == update
                ),
            )
            row["schema"] = V037_SCHEMA
            row["seed"] = seed
            row["task_opportunity_oracle_evaluator_only"] = float(
                pending.task_opportunity_oracle
            )
            row["task_opportunity_regret_evaluator_only"] = float(
                pending.task_opportunity_regret
            )
            row["observation_noise_sha256"] = pending.observation_noise_sha256
            row["return_noise"] = float(pending.return_noise)
            row["task_return_multiplier_evaluator_only"] = float(
                pending.task_return_multiplier
            )
            row["transition_rollout"] = _rollout_row(
                pending.step.action_selection
            )
            row["controls"] = {
                name: _control_row(
                    pending.controls[name], control_outcomes[name]
                )
                for name in V037_CONTROL_NAMES
            }
            _seal_v037_row_or_stop(row, sealed_row_sink)
            if retain_rows:
                rows.append(row)
            if pending.phase.offset + 1 == phase_lengths[pending.phase.name]:
                snapshot = runtime.snapshot()
                phase_model_counts[pending.phase.name] = {
                    "transition": int(
                        snapshot["transition_model"]["observation_count"]
                    ),
                    "return": int(
                        snapshot["return_model"]["observation_count"]
                    ),
                }
                control_model_counts[pending.phase.name] = {
                    name: controls[name].counts()
                    for name in V037_CONTROL_NAMES
                }

        if phase.offset == 0:
            stale_by_phase[phase.name] = copy.deepcopy(step.public_boundary)
        stale_certificate = stale_by_phase[phase.name]
        control_selections: dict[ControlName, _ShadowSelection] = {}
        for name in V037_CONTROL_NAMES:
            control_selections[name] = controls[name].select(
                time=step.time,
                observation=control_observations[name],
                context=context,
                certificate=_control_certificate(
                    name, step.public_boundary, stale_certificate
                ),
            )

        running_mean_prediction = (
            0.0
            if running_return_count == 0
            else running_return_sum / running_return_count
        )
        observation_noise = world_rng.normal(
            0.0,
            experiment_config.observation_noise,
            V036_OBSERVATION_DIM,
        )
        return_noise = float(
            world_rng.normal(0.0, experiment_config.return_noise)
        )
        task_return_multiplier = float(
            1.0
            if task_return_multiplier_factory is None
            else task_return_multiplier_factory(experiment_config, world, phase)
        )
        if not np.isfinite(task_return_multiplier) or task_return_multiplier < 0.0:
            raise ValueError("task return multiplier must be nonnegative and finite")
        observation_noise_sha = _array_sha256(observation_noise)
        live_transition = _world_transition_with_shared_noise(
            experiment_config,
            world,
            phase,
            observation,
            bank,
            step.causal_commitment.handles,
            step.action,
            context,
            _certificate_pair(step.public_boundary),
            observation_noise,
            return_noise,
            task_return_multiplier,
        )
        (
            next_observation,
            realized_return,
            oracle_return,
            action_regret,
            opportunity_oracle,
            opportunity_regret,
            gate_open,
        ) = live_transition

        control_pending: dict[ControlName, _ShadowPending] = {}
        for name in V037_CONTROL_NAMES:
            selection = control_selections[name]
            consequence = _world_transition_with_shared_noise(
                experiment_config,
                world,
                phase,
                control_observations[name],
                bank,
                step.causal_commitment.handles,
                selection.selected_action,
                context,
                selection.certificate_pair,
                observation_noise,
                return_noise,
                task_return_multiplier,
            )
            (
                control_next,
                control_return,
                control_oracle,
                control_regret,
                control_opportunity_oracle,
                control_opportunity_regret,
                control_gate,
            ) = consequence
            control_pending[name] = _ShadowPending(
                selection=selection,
                next_observation=control_next.copy(),
                realized_return=float(control_return),
                gated_oracle_return=float(control_oracle),
                task_opportunity_oracle=float(control_opportunity_oracle),
                gated_action_regret=float(control_regret),
                task_opportunity_regret=float(control_opportunity_regret),
                gate_open=bool(control_gate),
                observation_noise_sha256=observation_noise_sha,
                return_noise=return_noise,
                task_return_multiplier=task_return_multiplier,
            )
            control_observations[name] = control_next

        pending = _V037Pending(
            transition_index=transition_index,
            phase=phase,
            hidden_exogenous_source=world.exogenous_source,
            observation=observation.copy(),
            context=context.copy(),
            process_bank=bank.copy(),
            process_bank_sha256=bank_sha,
            process_bank_receipt=bank_receipt,
            process_bank_commitment=copy.deepcopy(bank_commitment),
            step=copy.deepcopy(step),
            next_observation=next_observation.copy(),
            realized_return=float(realized_return),
            oracle_return=float(oracle_return),
            action_regret=float(action_regret),
            task_opportunity_oracle=float(opportunity_oracle),
            task_opportunity_regret=float(opportunity_regret),
            action_gate_open=bool(gate_open),
            running_mean_return_prediction=float(running_mean_prediction),
            running_mean_return_observation_count=running_return_count,
            controls=copy.deepcopy(control_pending),
            observation_noise_sha256=observation_noise_sha,
            return_noise=return_noise,
            task_return_multiplier=task_return_multiplier,
        )
        observation = next_observation
        previous_return = float(realized_return)

    if pending is None or previous_return is None:
        raise RuntimeError("D1 trace produced no terminal transition")
    flushed = runtime.flush(
        observation,
        realized_external_return=previous_return,
        source="v037_post_change_closure_terminal_flush",
    )
    control_outcomes = {
        name: controls[name].reveal(pending.controls[name])
        for name in V037_CONTROL_NAMES
    }
    agent_result = agent.last_result
    if agent_result is None or flushed.causal_boundary_update is None:
        raise RuntimeError("terminal flush emitted incomplete audit state")
    update = flushed.causal_boundary_update
    agent_update = agent_result.causal_boundary_update_receipt
    row = _reveal_row(
        pending,
        flushed.previous_action_outcome,
        flushed.drift,
        update,
        flushed.public_boundary,
        flushed.public_boundary_gate,
        runtime_instance_digest,
        bool(id(runtime) == runtime_identity and id(agent) == agent_identity),
        interrupted_transitions=agent_result.causal_interrupted_transitions,
        sanitized_agent_audit_valid=bool(
            agent_update is not None and agent_update == update
        ),
    )
    row["schema"] = V037_SCHEMA
    row["seed"] = seed
    row["task_opportunity_oracle_evaluator_only"] = float(
        pending.task_opportunity_oracle
    )
    row["task_opportunity_regret_evaluator_only"] = float(
        pending.task_opportunity_regret
    )
    row["observation_noise_sha256"] = pending.observation_noise_sha256
    row["return_noise"] = float(pending.return_noise)
    row["task_return_multiplier_evaluator_only"] = float(
        pending.task_return_multiplier
    )
    row["transition_rollout"] = _rollout_row(pending.step.action_selection)
    row["controls"] = {
        name: _control_row(pending.controls[name], control_outcomes[name])
        for name in V037_CONTROL_NAMES
    }
    _seal_v037_row_or_stop(row, sealed_row_sink)
    if retain_rows:
        rows.append(row)
    terminal_snapshot = runtime.snapshot()
    phase_model_counts[pending.phase.name] = {
        "transition": int(
            terminal_snapshot["transition_model"]["observation_count"]
        ),
        "return": int(terminal_snapshot["return_model"]["observation_count"]),
    }
    control_model_counts[pending.phase.name] = {
        name: controls[name].counts() for name in V037_CONTROL_NAMES
    }
    summary = summary_builder(
        seed,
        experiment_config,
        boundary,
        runtime_cfg,
        rows,
        runtime,
        runtime_instance_digest,
        phase_model_counts,
        control_model_counts,
    )
    return rows, summary


def write_v037_evidence(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    destination: Path,
) -> dict[str, str]:
    destination.mkdir(parents=True, exist_ok=False)
    rows_path = destination / V037_ROWS_ARTIFACT
    summary_path = destination / V037_SUMMARY_ARTIFACT
    digest = hashlib.sha256()
    with rows_path.open("wb") as handle:
        for row in rows:
            encoded = (
                json.dumps(
                    _jsonable(row),
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
            handle.write(encoded)
            digest.update(encoded)
    summary_text = (
        json.dumps(
            _jsonable(summary),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )
    summary_path.write_text(summary_text, encoding="utf-8")
    hashes = {
        V037_ROWS_ARTIFACT: digest.hexdigest(),
        V037_SUMMARY_ARTIFACT: hashlib.sha256(
            summary_text.encode("utf-8")
        ).hexdigest(),
    }
    (destination / "artifact_sha256.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return hashes


def _validate_v037_attempt_id(attempt_id: str | None) -> str:
    if (
        not isinstance(attempt_id, str)
        or V037_ATTEMPT_PATTERN.fullmatch(attempt_id) is None
    ):
        raise ValueError(
            "attempt_id is required and must contain only letters, digits, "
            "'.', '_', or '-'"
        )
    return attempt_id


def _verify_v037_preoutcome_freeze() -> str:
    """Verify the D1 source seal before a fresh pilot seed is consumed."""

    if not V037_FREEZE_MANIFEST.is_file() or not V037_FREEZE_CHECKSUM.is_file():
        raise RuntimeError("v0.37 execution requires a pre-outcome source freeze")
    raw = V037_FREEZE_MANIFEST.read_bytes()
    manifest_sha256 = hashlib.sha256(raw).hexdigest()
    checksum_fields = V037_FREEZE_CHECKSUM.read_text(
        encoding="ascii"
    ).strip().split()
    if (
        len(checksum_fields) != 2
        or checksum_fields[0] != manifest_sha256
        or checksum_fields[1] != V037_FREEZE_MANIFEST.name
    ):
        raise RuntimeError("v0.37 freeze checksum companion mismatch")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("invalid v0.37 freeze manifest") from exc
    if (
        not isinstance(payload, Mapping)
        or payload.get("schema") != "rrct.v037.preoutcome_freeze.v1"
        or payload.get("status") != "sealed_before_fresh_pilot_outcomes"
        or payload.get("pilot_seeds") != list(V037_PILOT_SEEDS)
        or not isinstance(payload.get("files"), Mapping)
        or not payload["files"]
    ):
        raise RuntimeError("v0.37 freeze metadata mismatch")
    listed_files = payload["files"]
    required = set(V037_REQUIRED_FREEZE_FILES)
    source_directory = V037_PROJECT_ROOT / "src" / "rrct"
    if source_directory.is_dir():
        required.update(
            path.relative_to(V037_PROJECT_ROOT).as_posix()
            for path in source_directory.glob("*.py")
            if path.is_file()
        )
    omitted = sorted(required.difference(listed_files))
    if omitted:
        raise RuntimeError(
            "v0.37 freeze omits required files: " + ", ".join(omitted[:8])
        )
    for relative_name, expected in listed_files.items():
        if not isinstance(relative_name, str) or not isinstance(expected, Mapping):
            raise TypeError("invalid file entry in v0.37 freeze")
        candidate = (V037_PROJECT_ROOT / relative_name).resolve()
        try:
            candidate.relative_to(V037_PROJECT_ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError("v0.37 freeze file escapes project root") from exc
        expected_sha256 = expected.get("sha256")
        expected_size = expected.get("size")
        if (
            not candidate.is_file()
            or not isinstance(expected_sha256, str)
            or len(expected_sha256) != 64
            or any(
                character not in "0123456789abcdef"
                for character in expected_sha256
            )
            or isinstance(expected_size, bool)
            or not isinstance(expected_size, int)
            or expected_size < 0
        ):
            raise RuntimeError("invalid frozen source file metadata")
        contents = candidate.read_bytes()
        if (
            len(contents) != expected_size
            or hashlib.sha256(contents).hexdigest() != expected_sha256
        ):
            raise RuntimeError(
                f"frozen v0.37 source checksum mismatch: {relative_name}"
            )
    return manifest_sha256


def _prepare_v037_campaign_attempt(
    *,
    seed: int,
    attempt_id: str,
    output: str | Path,
    freeze_sha256: str,
) -> tuple[Path, Path, str]:
    """Claim a pilot seed and publish a durable receipt before RNG creation."""

    root = V037_CAMPAIGN_ROOT.resolve()
    destination = Path(output).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    claims = root / "claims"
    attempt_claims = claims / "attempts"
    seed_claims = claims / "seeds"
    attempt_claims.mkdir(parents=True, exist_ok=True)
    seed_claims.mkdir(parents=True, exist_ok=True)
    _fsync_directory(claims)
    _fsync_directory(root)
    try:
        relative_output = destination.relative_to(root)
    except ValueError as exc:
        raise ValueError("output must be inside the fixed v0.37 campaign root") from exc
    if not relative_output.parts or relative_output.parts[0] == "claims":
        raise ValueError("output must be a run directory outside the claim ledger")
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("v0.37 output directory must be empty")

    claim_base = {
        "schema": "rrct.v037.campaign_claim.v1",
        "version": V037_VERSION,
        "attempt_id": attempt_id,
        "cohort": "pilot",
        "seed": int(seed),
        "campaign_root": os.fspath(root),
        "output_directory": os.fspath(destination),
        "preoutcome_freeze_sha256": freeze_sha256,
        "permanent": True,
    }
    attempt_claim_path = attempt_claims / f"{attempt_id}.json"
    seed_claim_path = seed_claims / f"pilot-seed-{seed}.json"
    allocation_lock = claims / "allocation.lock"
    lock_descriptor = os.open(
        os.fspath(allocation_lock), os.O_RDWR | os.O_CREAT, 0o600
    )
    try:
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        if attempt_claim_path.exists():
            raise FileExistsError(
                f"v0.37 campaign attempt is already claimed: {attempt_id}"
            )
        if seed_claim_path.exists():
            raise FileExistsError(
                f"v0.37 pilot seed is already claimed: {seed}"
            )
        seed_claim_sha256 = _exclusive_json(
            seed_claim_path,
            {**claim_base, "claim_kind": "pilot_seed_once"},
        )
        attempt_claim_sha256 = _exclusive_json(
            attempt_claim_path,
            {**claim_base, "claim_kind": "campaign_unique_attempt"},
        )
    finally:
        fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        os.close(lock_descriptor)

    start_payload = {
        "schema": "rrct.v037.run_start.v1",
        "version": V037_VERSION,
        "status": "started_before_rng_construction",
        "attempt_id": attempt_id,
        "cohort": "pilot",
        "seed": int(seed),
        "campaign_root": os.fspath(root),
        "output_directory": os.fspath(destination),
        "preoutcome_freeze_sha256": freeze_sha256,
        "expected_transition_count": V037_D1_CONFIG.total_steps,
        "expected_terminal_flushes": 1,
        "attempt_claim": os.fspath(attempt_claim_path.relative_to(root)),
        "attempt_claim_sha256": attempt_claim_sha256,
        "seed_claim": os.fspath(seed_claim_path.relative_to(root)),
        "seed_claim_sha256": seed_claim_sha256,
        "environment": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "executable": sys.executable,
        },
    }
    start_sha256 = _exclusive_json(
        destination / V037_RUN_START_RECEIPT,
        start_payload,
    )
    return root, destination, start_sha256


def _write_claimed_v037_artifacts(
    *,
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    destination: Path,
    row_stream: _DurableRowStream,
    start_sha256: str,
) -> dict[str, str]:
    expected_digest = hashlib.sha256()
    for row in rows:
        expected_digest.update(_jsonl_row_bytes(row))
    if row_stream.row_count != len(rows):
        raise RuntimeError("durable v0.37 row count does not match completed trace")
    if row_stream.sha256 != expected_digest.hexdigest():
        raise RuntimeError("durable v0.37 row digest does not match completed trace")
    rows_path = destination / V037_ROWS_ARTIFACT
    rows_sha256 = hashlib.sha256(rows_path.read_bytes()).hexdigest()
    if rows_sha256 != row_stream.sha256:
        raise RuntimeError("durable v0.37 row stream changed after sealing")
    summary_sha256 = _exclusive_json(
        destination / V037_SUMMARY_ARTIFACT,
        summary,
    )
    hashes = {
        V037_ROWS_ARTIFACT: rows_sha256,
        V037_SUMMARY_ARTIFACT: summary_sha256,
        V037_RUN_START_RECEIPT: start_sha256,
    }
    _exclusive_json(destination / "artifact_sha256.json", hashes)
    return hashes


def _default_progress_reporter(row: Mapping[str, Any]) -> None:
    phase = str(row["phase"])
    offset = int(row["phase_offset"]) + 1
    structural = str(row["structural_event"])
    gate_event = str(row["public_gate_event_after_reveal"])
    should_report = (
        offset == 1
        or offset % 120 == 0
        or bool(row["reopen_requested"])
        or structural != "none"
        or gate_event in {"entered", "released"}
    )
    if not should_report:
        return
    payload = {
        "schema": "rrct.v037.progress.v1",
        "phase": phase,
        "phase_offset": offset,
        "transition_index": int(row["transition_index"]),
        "structural_event": structural,
        "reopen_requested": bool(row["reopen_requested"]),
        "public_gate_event_after_reveal": gate_event,
        "action_public_pair": row["action_public_pair"],
        "public_pair_after_reveal": row["public_pair_after_reveal"],
        "action_gate_open_evaluator_only": bool(
            row["action_gate_open_evaluator_only"]
        ),
        "hard_integrity_valid": bool(row["hard_integrity_valid"]),
    }
    print(json.dumps(payload, sort_keys=True), flush=True)


def run_claimed_v037_pilot(
    seed: int,
    output: str | Path,
    *,
    attempt_id: str | None,
    progress_reporter: Callable[[Mapping[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Run one fresh, permanently claimed D1 pilot with durable row evidence."""

    seed = int(seed)
    if seed not in V037_PILOT_SEEDS:
        raise ValueError("seed is not reserved for the v0.37 pilot cohort")
    validated_attempt = _validate_v037_attempt_id(attempt_id)
    freeze_sha256 = _verify_v037_preoutcome_freeze()
    root, destination, start_sha256 = _prepare_v037_campaign_attempt(
        seed=seed,
        attempt_id=validated_attempt,
        output=output,
        freeze_sha256=freeze_sha256,
    )
    row_stream = _DurableRowStream(destination / V037_ROWS_ARTIFACT)
    reporter = progress_reporter or _default_progress_reporter

    def sealed_sink(row: Mapping[str, Any]) -> None:
        row_stream.append(row)
        reporter(row)

    try:
        rows, raw_summary = run_post_change_closure_trace(
            seed,
            experiment_config=V037_D1_CONFIG,
            sealed_row_sink=sealed_sink,
        )
        row_stream.close()
        summary = dict(raw_summary)
        summary["campaign_attempt"] = {
            "attempt_id": validated_attempt,
            "campaign_root": os.fspath(root),
            "preoutcome_freeze_sha256": freeze_sha256,
            "run_start_receipt": V037_RUN_START_RECEIPT,
            "run_start_receipt_sha256": start_sha256,
            "durably_streamed_rows": row_stream.row_count,
        }
        hashes = _write_claimed_v037_artifacts(
            rows=rows,
            summary=summary,
            destination=destination,
            row_stream=row_stream,
            start_sha256=start_sha256,
        )
        print(
            json.dumps(
                {
                    "schema": "rrct.v037.completion.v1",
                    "attempt_id": validated_attempt,
                    "seed": seed,
                    "status": summary["status"],
                    "all_endpoints_met": summary["all_endpoints_met"],
                    "artifact_sha256": hashes,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return summary
    except BaseException as exc:
        try:
            row_stream.close()
        except OSError as close_error:
            exc.add_note(f"durable row stream close also failed: {close_error}")
        failure = {
            "schema": "rrct.v037.run_failure.v1",
            "version": V037_VERSION,
            "status": "INTEGRITY_FAIL",
            "scientific_classification": "INTEGRITY_FAIL",
            "operational_status": "interrupted_or_failed",
            "typed_hard_integrity_failure": isinstance(exc, HardIntegrityError),
            "attempt_id": validated_attempt,
            "cohort": "pilot",
            "seed": seed,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "durably_streamed_rows": row_stream.row_count,
            "partial_rows_sha256": row_stream.sha256,
        }
        try:
            _exclusive_json(destination / V037_RUN_FAILURE_RECEIPT, failure)
        except OSError as receipt_error:
            exc.add_note(f"failure receipt write also failed: {receipt_error}")
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the exploratory RRCT v0.37 post-change closure pilot"
    )
    parser.add_argument("--seed", type=int, default=V037_FIRST_PILOT_SEED)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--attempt-id",
        required=True,
        help="unique immutable identifier for this v0.37 campaign attempt",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_claimed_v037_pilot(
        args.seed,
        args.output,
        attempt_id=args.attempt_id,
    )
    return 0 if bool(summary["integrity"]["v037_hard_integrity_all"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "V037_D1_CONFIG",
    "V037ExperimentConfig",
    "run_claimed_v037_pilot",
    "run_post_change_closure_trace",
    "write_v037_evidence",
]
