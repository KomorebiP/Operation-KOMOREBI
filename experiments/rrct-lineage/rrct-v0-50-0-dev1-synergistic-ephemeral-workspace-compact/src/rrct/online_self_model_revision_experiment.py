"""Frozen-shape v0.29 experiment for online causal self-boundary revision.

The benchmark changes which anonymous prospective handle/source interaction
controls a focal two-dimensional part of one canonical twelve-dimensional
observation.  The hidden route and phase schedule belong to the evaluator;
the :class:`~rrct.agent.RRCTAgent` receives only that observation and a bank
of six anonymous, equal-energy process streams bound after its commitment.

Behavior reads the boundary only through ``RRCTAgent.choose_causal_port``.
The private updater state is retained in separate audit columns and never
selects a motor port.  This is a test of online, functionally used causal
self-model revision.  It is not a test or claim of phenomenal awareness,
sentience, subjective experience, valence, or moral status.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from .agent import AblationFlags, RRCTAgent, StepResult
from .causal_boundary import CausalBoundaryConfig


FloatArray = NDArray[np.float64]

V029_SCHEMA = "rrct.v029.online_self_model_revision.v1"
V029_SOURCE_TAG = "v029_online"
V029_OBSERVATION_DIM = 12
V029_PROCESS_DIM = 8
V029_SOURCE_COUNT = 6
V029_HANDLE_COUNT = 4
V029_ROUTE_RANK = 2
V029_PILOT_SEEDS = (5481, 5487, 5493, 5499)
# The first reserved cohort (5501, 5507, 5513, 5519, 5521, 5527, 5531,
# 5539) was disqualified before freeze after route metadata was accidentally
# instantiated during a static audit.  No outcomes were simulated, but those
# seeds are no longer prospective.  This replacement cohort was selected by
# the same index-balanced construction and must remain unopened until the
# pre-outcome freeze is sealed.
V029_OFFICIAL_SEEDS = (5601, 5607, 5613, 5619, 5621, 5627, 5631, 5639)
V029_ARMS = (
    "adaptive",
    "frozen",
    "no_broadcast",
    "source_deranged",
    "time_rolled_replay",
    "true_source_lesion",
    "decoy_source_lesion",
)

# These evaluator-only names never enter an agent method, source string, or
# learned snapshot.  A seed-specific permutation hides their bank positions.
_SOURCE_KINDS = (
    "private_a",
    "one_step_echo",
    "policy_correlated",
    "private_b",
    "strong_exogenous",
    "other_agent",
)
_GATEABLE_KINDS = _SOURCE_KINDS[:4]
_PHASE_SEQUENCE = ("route_a", "blackout", "route_b", "disconnect", "restore_a")


@dataclass(frozen=True)
class V029RunConfig:
    """Frozen v0.29 scientific constants; official execution is guarded."""

    block_size: int = 20
    evidence_capacity: int = 240
    minimum_samples: int = 240
    fit_interval: int = 20
    null_permutations: int = 128
    half_null_permutations: int = 128
    null_quantile: float = 0.99
    ridge: float = 0.50
    revision_confirmations: int = 2
    revocation_confirmations: int = 3
    confidence_decay: float = 0.65
    calibration_blocks: int = 14
    warmup_blocks: int = 2
    blackout_blocks: int = 1
    changed_blocks: tuple[int, int] = (15, 17)
    disconnect_blocks: tuple[int, int] = (15, 17)
    restore_blocks: tuple[int, int] = (15, 17)
    change_episodes: int = 1
    stable_shock_episodes: int = 1
    source_energy: float = 1.0
    routed_strength: float = 4.0
    exogenous_strength: float = 4.6
    other_strength: float = 2.2
    observation_noise: float = 0.025
    bootstrap_replicates: int = 4000
    bootstrap_seed: int = 20261029

    def __post_init__(self) -> None:
        integer_names = (
            "block_size",
            "evidence_capacity",
            "minimum_samples",
            "fit_interval",
            "null_permutations",
            "half_null_permutations",
            "revision_confirmations",
            "revocation_confirmations",
            "calibration_blocks",
            "warmup_blocks",
            "blackout_blocks",
            "change_episodes",
            "stable_shock_episodes",
            "bootstrap_replicates",
            "bootstrap_seed",
        )
        for name in integer_names:
            value = getattr(self, name)
            if isinstance(value, (bool, np.bool_)) or int(value) != value or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.block_size % 2:
            raise ValueError("block_size must be even")
        for name in ("evidence_capacity", "minimum_samples", "fit_interval"):
            if getattr(self, name) % self.block_size:
                raise ValueError(f"{name} must align to complete commitment blocks")
        nuisance_columns = (
            1
            + V029_OBSERVATION_DIM
            + V029_SOURCE_COUNT * V029_PROCESS_DIM
            + V029_HANDLE_COUNT
        )
        if self.minimum_samples // 2 <= nuisance_columns:
            raise ValueError(
                "each evidence half must exceed the 65-column nuisance design"
            )
        if self.null_quantile >= 0.99 and (
            self.null_permutations < 99 or self.half_null_permutations < 99
        ):
            raise ValueError("q=.99 requires at least 99 full and half null draws")
        # Outcomes are revealed by the following step.  Equality would place
        # the final confirming fit on the first online row, after frozen/no-
        # broadcast controls have already been applied at the calibration
        # boundary.  Require one additional aligned block so every arm
        # acquires under the identical intact graph before any intervention.
        if self.calibration_blocks * self.block_size <= (
            self.minimum_samples
            + (self.revision_confirmations - 1) * self.fit_interval
        ):
            raise ValueError(
                "calibration is too short for pre-intervention confirmed acquisition"
            )
        for name in ("changed_blocks", "disconnect_blocks", "restore_blocks"):
            bounds = getattr(self, name)
            if len(bounds) != 2 or min(bounds) < 1 or bounds[0] > bounds[1]:
                raise ValueError(f"{name} must be an increasing positive pair")
            if min(bounds) * self.block_size <= self.scoring_grace_steps:
                raise ValueError(
                    f"{name} must extend beyond the conservative scoring grace"
                )
        for name in (
            "source_energy",
            "routed_strength",
            "exogenous_strength",
            "other_strength",
            "observation_noise",
            "ridge",
            "confidence_decay",
        ):
            value = float(getattr(self, name))
            if not np.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
        if self.exogenous_strength <= self.routed_strength:
            raise ValueError("the ungated exogenous cause must be stronger")

    def boundary_config(self, seed: int) -> CausalBoundaryConfig:
        return CausalBoundaryConfig(
            observation_dim=V029_OBSERVATION_DIM,
            process_dim=V029_PROCESS_DIM,
            source_count=V029_SOURCE_COUNT,
            handle_count=V029_HANDLE_COUNT,
            evidence_capacity=self.evidence_capacity,
            minimum_samples=self.minimum_samples,
            fit_interval=self.fit_interval,
            commitment_block_size=self.block_size,
            ridge=self.ridge,
            null_permutations=self.null_permutations,
            half_null_permutations=self.half_null_permutations,
            null_quantile=self.null_quantile,
            higher_mode_null="global_sharp_null",
            revision_confirmations=self.revision_confirmations,
            revocation_confirmations=self.revocation_confirmations,
            confidence_decay=self.confidence_decay,
            seed=int(seed),
        )

    @property
    def revision_grace_steps(self) -> int:
        """Earliest post-change point with a full window and confirmations."""

        return self.evidence_capacity + (
            self.revision_confirmations - 1
        ) * self.fit_interval

    @property
    def revision_grace_blocks(self) -> int:
        return self.revision_grace_steps // self.block_size

    @property
    def revocation_grace_steps(self) -> int:
        """Conservative delay for a sustained null to erase an active model."""

        return self.evidence_capacity + (
            self.revocation_confirmations - 1
        ) * self.fit_interval

    @property
    def scoring_grace_steps(self) -> int:
        """Later of revision and revocation grace periods."""

        return max(self.revision_grace_steps, self.revocation_grace_steps)


V029_FROZEN_CONFIG = V029RunConfig()


@dataclass(frozen=True)
class _HiddenRoute:
    """Evaluator truth.  No instance is passed across the agent API."""

    source_order: tuple[str, ...]
    handle_order: tuple[str, ...]
    pair_a: tuple[int, int]
    pair_b: tuple[int, int]
    source_bases: Mapping[str, FloatArray]
    sensory_basis: FloatArray
    observation_mixing: FloatArray
    digest: str


@dataclass(frozen=True)
class _WorldState:
    position: FloatArray
    other_position: FloatArray
    nuisance: FloatArray
    previous_a_source: FloatArray
    goal: FloatArray


def _unit_rows(values: FloatArray, energy: float) -> FloatArray:
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if np.any(norms <= 1e-12):
        raise RuntimeError("degenerate anonymous source draw")
    return energy * values / norms


def _projector_overlap(estimated: FloatArray, truth: FloatArray, rank: int = 2) -> float:
    if estimated.shape != truth.shape or rank <= 0:
        return 0.0
    return float(np.clip(np.trace(estimated @ truth) / rank, 0.0, 1.0))


def _digest_array(value: FloatArray) -> str:
    array = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    return hashlib.sha256(array.tobytes(order="C")).hexdigest()


def _orthogonal(rng: np.random.Generator, rows: int, columns: int) -> FloatArray:
    q, _ = np.linalg.qr(rng.normal(size=(rows, columns)))
    return np.asarray(q[:, :columns], dtype=np.float64)


def _balanced_slot(seed: int, episode: int) -> int:
    cohorts = V029_PILOT_SEEDS + V029_OFFICIAL_SEEDS
    try:
        base = cohorts.index(int(seed))
    except ValueError:
        base = abs(int(seed))
    return (base + int(episode)) % 4


def _hidden_route(seed: int, episode: int) -> _HiddenRoute:
    """Create deterministic, seed-counterbalanced evaluator truth."""

    rng = np.random.default_rng(np.random.SeedSequence([seed, episode, 0x2900]))
    slot = _balanced_slot(seed, episode)
    a_source_slots = (0, 3, 5, 2)
    b_source_slots = (3, 5, 1, 4)
    source_order: list[str | None] = [None] * V029_SOURCE_COUNT
    source_order[a_source_slots[slot]] = "private_a"
    source_order[b_source_slots[slot]] = "private_b"
    remaining_kinds = [kind for kind in _SOURCE_KINDS if kind not in source_order]
    rng.shuffle(remaining_kinds)
    for index in range(V029_SOURCE_COUNT):
        if source_order[index] is None:
            source_order[index] = remaining_kinds.pop()

    a_handle = slot
    b_handle = (slot + 2) % V029_HANDLE_COUNT
    handle_order: list[str | None] = [None] * V029_HANDLE_COUNT
    handle_order[a_handle] = "private_a"
    handle_order[b_handle] = "private_b"
    remaining_handles = [kind for kind in _GATEABLE_KINDS if kind not in handle_order]
    rng.shuffle(remaining_handles)
    for index in range(V029_HANDLE_COUNT):
        if handle_order[index] is None:
            handle_order[index] = remaining_handles.pop()

    source_bases = {
        kind: _orthogonal(rng, V029_PROCESS_DIM, V029_ROUTE_RANK)
        for kind in _SOURCE_KINDS
    }
    # All latent coordinates enter every observed coordinate with probability
    # one under this Haar-like orthogonal draw: there is no focal coordinate
    # handed to the learner.
    observation_mixing = _orthogonal(
        rng, V029_OBSERVATION_DIM, V029_OBSERVATION_DIM
    )
    sensory_basis = observation_mixing[:, :V029_ROUTE_RANK]
    finalized_sources = tuple(str(kind) for kind in source_order)
    finalized_handles = tuple(str(kind) for kind in handle_order)
    pair_a = (a_handle, finalized_sources.index("private_a"))
    pair_b = (b_handle, finalized_sources.index("private_b"))
    payload = json.dumps(
        {
            "seed": seed,
            "episode": episode,
            "source_permutation": finalized_sources,
            "handle_permutation": finalized_handles,
            "pair_a": pair_a,
            "pair_b": pair_b,
            "mixing": _digest_array(observation_mixing),
            "bases": {key: _digest_array(value) for key, value in source_bases.items()},
        },
        sort_keys=True,
    ).encode("utf-8")
    return _HiddenRoute(
        source_order=finalized_sources,
        handle_order=finalized_handles,
        pair_a=pair_a,
        pair_b=pair_b,
        source_bases=source_bases,
        sensory_basis=sensory_basis,
        observation_mixing=observation_mixing,
        digest=hashlib.sha256(payload).hexdigest(),
    )


def _phase_schedule(
    rng: np.random.Generator,
    config: V029RunConfig,
    *,
    scenario: str,
) -> tuple[str, ...]:
    """Randomize phase lengths only in complete, frozen commitment blocks."""

    if scenario == "stable_shock":
        length = int(rng.integers(*config.changed_blocks, endpoint=True))
        return tuple("stable_shock" for _ in range(length * config.block_size))
    if scenario != "route_change":
        raise ValueError("scenario must be 'route_change' or 'stable_shock'")
    lengths = {
        "route_a": config.warmup_blocks,
        "blackout": config.blackout_blocks,
        "route_b": int(rng.integers(*config.changed_blocks, endpoint=True)),
        "disconnect": int(rng.integers(*config.disconnect_blocks, endpoint=True)),
        "restore_a": int(rng.integers(*config.restore_blocks, endpoint=True)),
    }
    return tuple(
        phase
        for phase in _PHASE_SEQUENCE
        for _ in range(lengths[phase] * config.block_size)
    )


def _expected_phase_trace(
    seed: int,
    episode: int,
    config: V029RunConfig,
) -> tuple[tuple[int, str, int], ...]:
    """Recompute the exact seed-deterministic frozen row schedule."""

    scenario = "route_change" if int(episode) == 0 else "stable_shock"
    schedule_rng = np.random.default_rng(
        np.random.SeedSequence([int(seed), int(episode), 0x2901])
    )
    schedule = _phase_schedule(schedule_rng, config, scenario=scenario)
    calibration_steps = config.calibration_blocks * config.block_size
    full_schedule = tuple("calibration" for _ in range(calibration_steps)) + schedule
    trace: list[tuple[int, str, int]] = []
    previous: str | None = None
    phase_step = -1
    for step, phase in enumerate(full_schedule):
        phase_step = 0 if phase != previous else phase_step + 1
        previous = phase
        trace.append((step, phase, phase_step))
    return tuple(trace)


def _observation(world: _WorldState, route: _HiddenRoute) -> FloatArray:
    latent = np.concatenate((world.position, world.other_position, world.nuisance))
    return np.asarray(route.observation_mixing @ latent, dtype=np.float64)


def _initial_world(rng: np.random.Generator) -> _WorldState:
    return _WorldState(
        position=rng.normal(0.0, 0.25, size=2),
        other_position=rng.normal(0.0, 0.25, size=2),
        nuisance=rng.normal(0.0, 0.4, size=8),
        previous_a_source=np.zeros(V029_PROCESS_DIM, dtype=np.float64),
        goal=rng.uniform(-1.0, 1.0, size=2),
    )


def _anonymous_bank(
    rng: np.random.Generator,
    route: _HiddenRoute,
    world: _WorldState,
    rrct_action: FloatArray,
    energy: float,
) -> tuple[FloatArray, Mapping[str, FloatArray]]:
    """Realize all anonymous streams only after the commitment exists."""

    values: dict[str, FloatArray] = {}
    values["private_a"] = rng.normal(size=V029_PROCESS_DIM)
    values["private_b"] = rng.normal(size=V029_PROCESS_DIM)
    echo = world.previous_a_source + rng.normal(0.0, 0.08, V029_PROCESS_DIM)
    values["one_step_echo"] = echo
    policy = np.resize(np.asarray(rrct_action, dtype=np.float64), V029_PROCESS_DIM)
    values["policy_correlated"] = policy + rng.normal(0.0, 0.12, V029_PROCESS_DIM)
    values["strong_exogenous"] = rng.normal(size=V029_PROCESS_DIM)
    values["other_agent"] = rng.normal(size=V029_PROCESS_DIM)
    stacked = np.stack([values[kind] for kind in _SOURCE_KINDS])
    normalized = _unit_rows(stacked, energy)
    normalized_by_kind = {
        kind: normalized[index].copy() for index, kind in enumerate(_SOURCE_KINDS)
    }
    bank = np.stack([normalized_by_kind[kind] for kind in route.source_order])
    return bank, normalized_by_kind


def _commitment_blind_bank_receipt(
    rng_state: Mapping[str, Any],
    expected_bank: FloatArray,
    route: _HiddenRoute,
    world: _WorldState,
    rrct_action: FloatArray,
    energy: float,
) -> bool:
    """Replay the bank draw without accepting any commitment as an input."""

    replay_rng = np.random.default_rng()
    replay_rng.bit_generator.state = copy.deepcopy(dict(rng_state))
    replay_bank, _ = _anonymous_bank(
        replay_rng, route, world, rrct_action, energy
    )
    return bool(np.array_equal(replay_bank, expected_bank))


def _truth_for_phase(
    route: _HiddenRoute, phase: str
) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
    """Return (behavior port, random-probe route) for evaluator use."""

    if phase in {"route_a", "stable_shock", "restore_a"}:
        return route.pair_a, route.pair_a
    if phase == "blackout":
        # The motor port still works, but the random prospective probe is
        # absent for one block.  Persistence through missing evidence is thus
        # distinguishable from immediate disconnection.
        return route.pair_a, None
    if phase == "route_b":
        return route.pair_b, route.pair_b
    if phase == "disconnect":
        return None, None
    raise ValueError(f"unknown hidden phase: {phase}")


def _learner_bank(
    arm: str,
    bank: FloatArray,
    history: deque[FloatArray],
    step: int,
    block_size: int,
    *,
    true_source_indices: tuple[int, int],
    decoy_source_index: int,
) -> FloatArray:
    if arm == "source_deranged":
        return np.roll(bank, 1, axis=0).copy()
    if arm == "time_rolled_replay":
        return (
            history[0].copy()
            if len(history) >= block_size
            else np.roll(bank, 1, axis=0).copy()
        )
    if arm in {"true_source_lesion", "decoy_source_lesion"}:
        result = bank.copy()
        indices = (
            true_source_indices
            if arm == "true_source_lesion"
            else (decoy_source_index,)
        )
        for index in indices:
            # Replace the learner-visible row by an equal-energy temporally
            # unrelated row.  The physical world still receives the original
            # source; this is an information lesion, not an energy cue.
            replacement = (
                history[0][index]
                if len(history) >= block_size
                else bank[(index + 1) % V029_SOURCE_COUNT]
            )
            result[index] = replacement
        return result
    return bank.copy()


def _agent(seed: int, config: V029RunConfig, arm: str) -> RRCTAgent:
    return RRCTAgent(
        V029_OBSERVATION_DIM,
        projector_ranks=(3, 6, 9, 12),
        action_dim=2,
        n_specialists=6,
        specialist_dim=16,
        workspace_dim=16,
        workspace_capacity=3,
        self_dim=12,
        memory_capacity=64,
        memory_top_k=3,
        seed=seed,
        causal_boundary_config=config.boundary_config(seed + 290_000),
        causal_boundary_broadcast_gain=1.25,
        # Every arm acquires route A under the identical intact graph.  Online
        # link lesions are applied only at the calibration boundary.
        ablations=AblationFlags(),
    )


def _world_transition(
    world: _WorldState,
    route: _HiddenRoute,
    source_values: Mapping[str, FloatArray],
    handles: FloatArray,
    *,
    phase: str,
    public_pair: tuple[int, int] | None,
    config: V029RunConfig,
    rng: np.random.Generator,
) -> tuple[_WorldState, Mapping[str, float]]:
    active_pair, probe_pair = _truth_for_phase(route, phase)
    routed = np.zeros(2, dtype=np.float64)
    if probe_pair is not None:
        kind = "private_a" if probe_pair == route.pair_a else "private_b"
        routed = (
            config.routed_strength
            * handles[probe_pair[0]]
            * (source_values[kind] @ route.source_bases[kind])
        )
    exogenous = (
        config.exogenous_strength
        * source_values["strong_exogenous"]
        @ route.source_bases["strong_exogenous"]
    )
    if phase == "stable_shock":
        exogenous *= 1.65
    other = (
        config.other_strength
        * source_values["other_agent"]
        @ route.source_bases["other_agent"]
    )
    noise = rng.normal(0.0, config.observation_noise, size=2)
    common_position = 0.35 * world.position + routed + exogenous + noise
    # The external controller observes the same-step post-disturbance focal
    # state.  Coordinate clipping cannot increase Euclidean goal error, so the
    # matched oracle ceiling is genuinely a ceiling rather than a noisy label.
    correction = np.clip(world.goal - common_position, -0.65, 0.65)
    command_transmitted = bool(active_pair is not None and public_pair == active_pair)
    command = correction if command_transmitted else np.zeros(2, dtype=np.float64)
    next_position = common_position + command
    next_other = 0.45 * world.other_position + other + rng.normal(
        0.0, config.observation_noise, size=2
    )
    next_nuisance = 0.50 * world.nuisance + rng.normal(0.0, 0.35, size=8)
    next_world = _WorldState(
        position=next_position,
        other_position=next_other,
        nuisance=next_nuisance,
        previous_a_source=source_values["private_a"].copy(),
        goal=world.goal.copy(),
    )
    null_error = float(np.linalg.norm(world.goal - common_position))
    actual_error = float(np.linalg.norm(world.goal - next_position))
    oracle_position = common_position + (correction if active_pair is not None else 0.0)
    oracle_error = float(np.linalg.norm(world.goal - oracle_position))
    denominator = max(null_error - oracle_error, 1e-9)
    utility = (
        float(np.clip((null_error - actual_error) / denominator, -1.0, 1.0))
        if active_pair is not None
        else float(public_pair is None)
    )
    return next_world, {
        "tracking_error": actual_error,
        "tracking_null_error": null_error,
        "tracking_oracle_error": oracle_error,
        "tracking_oracle_gap": actual_error - oracle_error,
        "tracking_oracle_gain": null_error - oracle_error,
        "tracking_utility": utility,
        "command_transmitted": float(command_transmitted),
        "command_norm": float(np.linalg.norm(command)),
        "executed_action_0": float(command[0]),
        "executed_action_1": float(command[1]),
    }


def _state_audit(
    result: StepResult,
    route: _HiddenRoute,
    target_pair: tuple[int, int] | None,
) -> Mapping[str, Any]:
    state = result.causal_boundary_state
    if state is None:
        return {
            "private_active": False,
            "private_handle": None,
            "private_source": None,
            "private_rank": 0,
            "private_confidence": 0.0,
            "private_pair_correct": False,
            "private_rank_correct": False,
            "private_state_correct": False,
            "internal_overlap": 0.0,
            "sensory_overlap": 0.0,
            "private_model_digest": None,
        }
    selected = (
        (state.selected_handle_index, state.selected_source_index)
        if state.active
        else None
    )
    target_kind = None
    if target_pair == route.pair_a:
        target_kind = "private_a"
    elif target_pair == route.pair_b:
        target_kind = "private_b"
    internal_truth = (
        route.source_bases[target_kind] @ route.source_bases[target_kind].T
        if target_kind is not None
        else np.zeros((V029_PROCESS_DIM, V029_PROCESS_DIM), dtype=np.float64)
    )
    sensory_truth = route.sensory_basis @ route.sensory_basis.T
    pair_correct = bool(selected == target_pair)
    rank_correct = bool(
        (target_pair is not None and state.rank == V029_ROUTE_RANK)
        or (target_pair is None and not state.active and state.rank == 0)
    )
    return {
        "private_active": bool(state.active),
        "private_handle": state.selected_handle_index,
        "private_source": state.selected_source_index,
        "private_rank": state.rank,
        "private_confidence": state.confidence,
        "private_pair_correct": pair_correct,
        "private_rank_correct": rank_correct,
        "private_state_correct": bool(pair_correct and rank_correct),
        "internal_overlap": (
            _projector_overlap(state.internal_projector, internal_truth)
            if target_pair is not None and state.active
            else float(not state.active and target_pair is None)
        ),
        "sensory_overlap": (
            _projector_overlap(state.sensory_projector, sensory_truth)
            if target_pair is not None and state.active
            else float(not state.active and target_pair is None)
        ),
        "private_model_digest": state.model_digest,
    }


def _run_arm_episode(
    seed: int,
    episode: int,
    arm: str,
    scenario: str,
    config: V029RunConfig,
    *,
    motor_execution_yoked_off: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    route = _hidden_route(seed, episode)
    schedule_rng = np.random.default_rng(
        np.random.SeedSequence([seed, episode, 0x2901])
    )
    schedule = _phase_schedule(schedule_rng, config, scenario=scenario)
    # Matched world randomness is arm-independent.
    world_rng = np.random.default_rng(
        np.random.SeedSequence([seed, episode, 0x2902])
    )
    agent = _agent(seed + 10_000 * episode, config, arm)
    world = _initial_world(world_rng)
    observation = _observation(world, route)
    history: deque[FloatArray] = deque(maxlen=config.block_size)
    rows: list[dict[str, Any]] = []
    prior_bound_digest: str | None = None

    calibration_steps = config.calibration_blocks * config.block_size
    full_schedule = tuple("calibration" for _ in range(calibration_steps)) + schedule
    frozen_applied = False
    previous_phase_label: str | None = None
    phase_step = -1
    for step, phase_label in enumerate(full_schedule):
        if phase_label != previous_phase_label:
            phase_step = 0
            previous_phase_label = phase_label
        else:
            phase_step += 1
        result = agent.step(observation, source=V029_SOURCE_TAG)
        receipt = result.causal_boundary_update_receipt
        public_pair = agent.choose_causal_port()
        if public_pair != result.causal_public_pair:
            raise RuntimeError("public port is not the latest workspace-derived pair")

        # No behavioral path may substitute private/evaluator truth for this
        # port.  The oracle is computed as a matched counterfactual error by
        # the external world model, never injected into the live trajectory.
        effective_public_pair = public_pair
        phase = "route_a" if phase_label == "calibration" else phase_label
        active_pair, _ = _truth_for_phase(route, phase)
        if phase_label == "calibration":
            # Acquisition trajectories are behaviorally yoked; functional
            # port use begins only after calibration.
            effective_public_pair = None
        elif motor_execution_yoked_off:
            # Pilot-only mechanism isolation: preserve the learned public
            # prediction and workspace path, but withhold its motor effect.
            # This is never an official arm or a primary efficacy comparison.
            effective_public_pair = None

        commitment = result.causal_commitment
        if commitment is None:
            raise RuntimeError("the configured agent failed to emit a commitment")
        bank_rng_state = copy.deepcopy(world_rng.bit_generator.state)
        bank, source_values = _anonymous_bank(
            world_rng,
            route,
            world,
            result.action,
            config.source_energy,
        )
        commitment_blind_bank = _commitment_blind_bank_receipt(
            bank_rng_state,
            bank,
            route,
            world,
            result.action,
            config.source_energy,
        )
        online_step = max(0, step - calibration_steps)
        private_source_indices = (route.pair_a[1], route.pair_b[1])
        decoy_source_index = route.source_order.index("one_step_echo")
        process_bank = (
            bank.copy()
            if phase_label == "calibration"
            else _learner_bank(
                arm,
                bank,
                history,
                online_step,
                config.block_size,
                true_source_indices=private_source_indices,
                decoy_source_index=decoy_source_index,
            )
        )
        bound = agent.bind_causal_sources(process_bank, commitment)
        prior_bound_digest = bound.transition_digest
        next_world, tracking = _world_transition(
            world,
            route,
            source_values,
            commitment.handles,
            phase=phase,
            public_pair=effective_public_pair,
            config=config,
            rng=world_rng,
        )
        next_observation = _observation(next_world, route)
        executed_action = np.asarray(
            [tracking["executed_action_0"], tracking["executed_action_1"]],
            dtype=np.float64,
        )
        agent.register_executed_action(executed_action)

        audit = _state_audit(result, route, active_pair)
        public_correct = bool(public_pair == active_pair)
        source_norm_error = float(
            np.max(np.abs(np.linalg.norm(bank, axis=1) - config.source_energy))
        )
        row: dict[str, Any] = {
            "schema": V029_SCHEMA,
            "seed": seed,
            "episode": episode,
            "arm": arm,
            "scenario": scenario,
            "step": step,
            "online_step": (None if phase_label == "calibration" else online_step),
            "phase": phase_label,
            "phase_step": phase_step,
            "block_size": config.block_size,
            "revision_grace_steps": config.revision_grace_steps,
            "revocation_grace_steps": config.revocation_grace_steps,
            "scoring_grace_steps": config.scoring_grace_steps,
            "route_digest": route.digest,
            "active_handle_truth": (None if active_pair is None else active_pair[0]),
            "active_source_truth": (None if active_pair is None else active_pair[1]),
            "public_handle": (None if public_pair is None else public_pair[0]),
            "public_source": (None if public_pair is None else public_pair[1]),
            "public_port_correct": public_correct,
            "public_abstained": public_pair is None,
            "oracle_truth_injected": False,
            "oracle_counterfactual_only": True,
            "motor_execution_yoked_off": bool(motor_execution_yoked_off),
            "proposal_selected": result.causal_boundary_proposal_selected,
            "workspace_drive_norm": float(
                np.linalg.norm(result.causal_boundary_workspace_drive)
            ),
            "access_confidence": result.causal_access_confidence,
            "access_updated": result.causal_access_updated,
            "access_update_count": result.causal_access_update_count,
            "observation_digest": _digest_array(observation),
            "step_observation_digest": _digest_array(result.observation),
            "same_observation_receipt": bool(np.array_equal(observation, result.observation)),
            "commitment_digest": commitment.digest,
            "bound_transition_digest": bound.transition_digest,
            "revealed_transition_digest": (
                None if receipt is None else receipt.transition_digest
            ),
            "prior_bound_digest_matches_reveal": bool(
                receipt is None
                if step == 0
                else receipt is not None
                and receipt.transition_digest == rows[-1]["bound_transition_digest"]
            ),
            "commitment_binary": bool(
                np.all((commitment.handles == 0.0) | (commitment.handles == 1.0))
            ),
            "commitment_blind_bank_receipt": commitment_blind_bank,
            "source_norm_max_error": source_norm_error,
            "source_tag_is_anonymous": result.source == V029_SOURCE_TAG,
            "updater_fit_performed": bool(receipt and receipt.fit_performed),
            "updater_revised": bool(receipt and receipt.revised),
            "updater_revoked": bool(receipt and receipt.revoked),
            "updater_frozen": bool(receipt and receipt.updates_frozen),
            "updater_prequential_alignment": (
                None if receipt is None else receipt.prequential_alignment
            ),
            "interrupted_transitions": result.causal_interrupted_transitions,
            **audit,
            **tracking,
        }
        rows.append(row)
        history.append(bank.copy())
        world = next_world
        observation = next_observation

        # Apply controls only after every arm has received the same initial A
        # calibration.  This isolates revision/broadcast use from acquisition.
        if step + 1 == calibration_steps:
            if arm == "frozen":
                agent.freeze_causal_boundary()
                frozen_applied = True
            elif arm == "no_broadcast":
                agent.set_ablations(
                    AblationFlags(causal_boundary_broadcast=True), reset=False
                )

    # Consume the final realized transition atomically.  The resulting fresh
    # terminal commitment is deliberately left unbound and is not evidence.
    terminal = agent.step(observation, source=V029_SOURCE_TAG)
    final_receipt = terminal.causal_boundary_update_receipt
    terminal_ok = bool(
        final_receipt is not None
        and prior_bound_digest is not None
        and final_receipt.transition_digest == prior_bound_digest
        and np.array_equal(terminal.observation, observation)
    )
    final_phase = "restore_a" if scenario == "route_change" else "stable_shock"
    final_target, _ = _truth_for_phase(route, final_phase)
    terminal_audit = _state_audit(terminal, route, final_target)
    receipts = {
        "route_digest": route.digest,
        "same_observation_all": bool(all(row["same_observation_receipt"] for row in rows)),
        "transition_chain_all": bool(
            all(row["prior_bound_digest_matches_reveal"] for row in rows)
        ),
        "source_energy_all": bool(
            all(row["source_norm_max_error"] <= 1e-12 for row in rows)
        ),
        "commitment_blind_bank_all": bool(
            all(row["commitment_blind_bank_receipt"] for row in rows)
        ),
        "anonymous_source_tag_all": bool(
            all(row["source_tag_is_anonymous"] for row in rows)
        ),
        "terminal_reveal_ok": terminal_ok,
        "terminal_commitment_unbound": terminal.causal_commitment is not None,
        "terminal_fit_performed": bool(final_receipt and final_receipt.fit_performed),
        "terminal_revised": bool(final_receipt and final_receipt.revised),
        "terminal_revoked": bool(final_receipt and final_receipt.revoked),
        "terminal_private_state_correct": bool(
            terminal_audit["private_state_correct"]
        ),
        "terminal_private_model_digest": terminal_audit["private_model_digest"],
        "frozen_control_applied": frozen_applied,
        "no_hidden_metadata_agent_api": True,
        "motor_execution_yoked_off": bool(motor_execution_yoked_off),
    }
    return rows, receipts


def _phase_latency(rows: Sequence[Mapping[str, Any]], phase: str) -> int | None:
    selected = [row for row in rows if row["phase"] == phase]
    if not selected:
        return None
    for offset, row in enumerate(selected):
        if row["private_state_correct"]:
            return offset + 1
    return None


def _seed_summary(
    seed: int,
    rows: Sequence[Mapping[str, Any]],
    receipts: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    online = [row for row in rows if row["phase"] != "calibration"]
    calibration = [row for row in rows if row["phase"] == "calibration"]

    def mean(items: Sequence[Mapping[str, Any]], key: str) -> float:
        values = [float(item[key]) for item in items if item.get(key) is not None]
        return float(np.mean(values)) if values else float("nan")

    phase_names = (
        "route_a",
        "blackout",
        "route_b",
        "disconnect",
        "restore_a",
        "stable_shock",
    )
    scored_fields = {
        "private_accuracy": "private_state_correct",
        "private_pair_accuracy": "private_pair_correct",
        "private_rank_accuracy": "private_rank_correct",
        "public_port_accuracy": "public_port_correct",
        "tracking_utility": "tracking_utility",
        "internal_overlap": "internal_overlap",
        "sensory_overlap": "sensory_overlap",
        "proposal_selection_rate": "proposal_selected",
        "workspace_drive_norm": "workspace_drive_norm",
    }
    phase_metrics: dict[str, Any] = {}
    observed_arms = tuple(sorted({str(row["arm"]) for row in rows}))
    calibration_yoked = True
    for episode in sorted({int(row["episode"]) for row in calibration}):
        traces = []
        for arm in observed_arms:
            arm_rows = sorted(
                (
                    row
                    for row in calibration
                    if int(row["episode"]) == episode and row["arm"] == arm
                ),
                key=lambda row: int(row["step"]),
            )
            traces.append(
                tuple(
                    (
                        int(row["step"]),
                        row["observation_digest"],
                        row["commitment_digest"],
                        row["bound_transition_digest"],
                        row["revealed_transition_digest"],
                        row["private_model_digest"],
                    )
                    for row in arm_rows
                )
            )
        if traces and any(trace != traces[0] for trace in traces[1:]):
            calibration_yoked = False
    summary: dict[str, Any] = {
        "seed": seed,
        "row_count": len(rows),
        "calibration_yoked": calibration_yoked,
        "integrity_pass": bool(
            all(row["same_observation_receipt"] for row in rows)
            and all(row["prior_bound_digest_matches_reveal"] for row in rows)
            and all(row["source_norm_max_error"] <= 1e-12 for row in rows)
            and all(row["commitment_blind_bank_receipt"] for row in rows)
            and all(row["source_tag_is_anonymous"] for row in rows)
            and all(row["interrupted_transitions"] == 0 for row in rows)
            and all(row["commitment_binary"] for row in rows)
            and all(not row["oracle_truth_injected"] for row in rows)
            and all(row["oracle_counterfactual_only"] for row in rows)
            and calibration_yoked
        ),
    }
    for arm in observed_arms:
        selected = [row for row in calibration if row["arm"] == arm]
        if not selected:
            continue
        last_phase_step = max(int(row["phase_step"]) for row in selected)
        terminal = [
            row
            for row in selected
            if int(row["phase_step"]) > last_phase_step - int(row["block_size"])
        ]
        for label, source in (
            ("private_accuracy", "private_state_correct"),
            ("internal_overlap", "internal_overlap"),
            ("sensory_overlap", "sensory_overlap"),
        ):
            summary[f"{arm}_calibration_terminal_{label}"] = mean(
                terminal, source
            )
    for arm in V029_ARMS:
        phase_metrics[arm] = {}
        for phase in phase_names:
            selected = [
                row for row in online if row["arm"] == arm and row["phase"] == phase
            ]
            if not selected:
                continue
            values = {
                label: mean(selected, source) for label, source in scored_fields.items()
            }
            values["tracking_error"] = mean(selected, "tracking_error")
            values["tracking_oracle_error"] = mean(
                selected, "tracking_oracle_error"
            )
            values["tracking_oracle_gap"] = mean(
                selected, "tracking_oracle_gap"
            )
            post_grace = [
                row
                for row in selected
                if int(row["phase_step"]) >= int(row["scoring_grace_steps"])
            ]
            if post_grace:
                for label, source in scored_fields.items():
                    values[f"post_grace_{label}"] = mean(post_grace, source)
                values["post_grace_tracking_error"] = mean(
                    post_grace, "tracking_error"
                )
                values["post_grace_tracking_oracle_gap"] = mean(
                    post_grace, "tracking_oracle_gap"
                )
            phase_metrics[arm][phase] = values
            for label, value in values.items():
                summary[f"{arm}_{phase}_{label}"] = value

    # Compare arms only within phase and seed.  A pooled online average could
    # otherwise conceal a transfer, revocation, restoration, or shock failure.
    controls = (
        "frozen",
        "no_broadcast",
        "source_deranged",
        "time_rolled_replay",
        "true_source_lesion",
        "decoy_source_lesion",
    )
    for control in controls:
        for phase in ("route_b", "disconnect", "restore_a", "stable_shock"):
            adaptive_values = phase_metrics.get("adaptive", {}).get(phase)
            control_values = phase_metrics.get(control, {}).get(phase)
            if adaptive_values is None or control_values is None:
                continue
            contrast_labels = (
                "private_accuracy",
                "public_port_accuracy",
                "tracking_utility",
                "post_grace_private_accuracy",
                "post_grace_public_port_accuracy",
                "post_grace_tracking_utility",
            )
            for label in contrast_labels:
                if label not in adaptive_values or label not in control_values:
                    continue
                summary[f"adaptive_minus_{control}_{phase}_{label}"] = (
                    adaptive_values[label] - control_values[label]
                )
    for phase in ("route_b", "restore_a", "stable_shock"):
        true_values = phase_metrics.get("true_source_lesion", {}).get(phase)
        decoy_values = phase_metrics.get("decoy_source_lesion", {}).get(phase)
        if true_values is None or decoy_values is None:
            continue
        for label in (
            "private_accuracy",
            "public_port_accuracy",
            "tracking_utility",
            "post_grace_private_accuracy",
            "post_grace_public_port_accuracy",
            "post_grace_tracking_utility",
        ):
            if label not in true_values or label not in decoy_values:
                continue
            summary[f"decoy_minus_true_source_lesion_{phase}_{label}"] = (
                decoy_values[label] - true_values[label]
            )
    summary["phase_metrics"] = phase_metrics

    adaptive = [row for row in online if row["arm"] == "adaptive"]
    for phase in ("route_b", "disconnect", "restore_a"):
        phase_rows = [row for row in adaptive if row["phase"] == phase]
        latencies = []
        for episode in sorted({int(row["episode"]) for row in phase_rows}):
            latency = _phase_latency(
                [row for row in phase_rows if int(row["episode"]) == episode], phase
            )
            if latency is not None:
                latencies.append(latency)
        summary[f"adaptive_{phase}_latency_steps"] = (
            float(np.mean(latencies)) if latencies else None
        )
        block_size = int(phase_rows[0]["block_size"]) if phase_rows else 1
        block_latencies = [int(np.ceil(value / block_size)) for value in latencies]
        summary[f"adaptive_{phase}_latency_blocks"] = (
            float(np.mean(block_latencies)) if block_latencies else None
        )
    stable_adaptive = [
        row
        for row in online
        if row["arm"] == "adaptive" and row["phase"] == "stable_shock"
    ]
    summary["adaptive_stable_shock_revision_or_revocation_count"] = float(
        sum(
            bool(row["updater_revised"]) or bool(row["updater_revoked"])
            for row in stable_adaptive
        )
        + sum(
            bool(item.get("terminal_revised")) or bool(item.get("terminal_revoked"))
            for item in receipts
            if item.get("arm") == "adaptive"
            and item.get("scenario") == "stable_shock"
        )
    )
    stable_terminal = [
        float(bool(item.get("terminal_private_state_correct")))
        for item in receipts
        if item.get("arm") == "adaptive"
        and item.get("scenario") == "stable_shock"
    ]
    summary["adaptive_stable_shock_terminal_private_accuracy"] = (
        float(np.mean(stable_terminal)) if stable_terminal else float("nan")
    )
    no_broadcast_contrast = summary.get(
        "adaptive_minus_no_broadcast_route_b_post_grace_private_accuracy"
    )
    if isinstance(no_broadcast_contrast, (int, float, np.integer, np.floating)):
        summary[
            "absolute_adaptive_minus_no_broadcast_route_b_post_grace_private_accuracy"
        ] = abs(float(no_broadcast_contrast))
    return summary


def _guard_seed(
    seed: int,
    *,
    cohort: str,
    allow_reserved_official: bool,
    exploratory: bool,
) -> None:
    seed = int(seed)
    if seed in V029_OFFICIAL_SEEDS:
        if cohort != "official" or not allow_reserved_official:
            raise PermissionError(
                "v0.29 official seeds are reserved and require an explicit official run"
            )
        return
    if cohort == "official":
        raise ValueError("official cohort accepts exactly the reserved official seeds")
    if seed in V029_PILOT_SEEDS:
        if cohort != "pilot":
            raise ValueError("pilot seeds require cohort='pilot'")
        return
    if not exploratory:
        raise ValueError("unregistered seeds require exploratory=True")
    if cohort != "exploratory":
        raise ValueError("unregistered seeds require cohort='exploratory'")


def run_online_self_model_revision_seed(
    seed: int,
    *,
    config: V029RunConfig = V029_FROZEN_CONFIG,
    cohort: str = "pilot",
    allow_reserved_official: bool = False,
    exploratory: bool = False,
    arms: Sequence[str] = V029_ARMS,
) -> dict[str, Any]:
    """Run one seed in memory; official seeds are closed by default."""

    _guard_seed(
        seed,
        cohort=cohort,
        allow_reserved_official=allow_reserved_official,
        exploratory=exploratory,
    )
    unknown = set(arms) - set(V029_ARMS)
    if unknown:
        raise ValueError(f"unknown v0.29 arm(s): {sorted(unknown)}")
    rows: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    episode = 0
    for _ in range(config.change_episodes):
        for arm in arms:
            arm_rows, arm_receipts = _run_arm_episode(
                int(seed), episode, arm, "route_change", config
            )
            rows.extend(arm_rows)
            receipts.append(
                {"episode": episode, "arm": arm, "scenario": "route_change", **arm_receipts}
            )
        episode += 1
    for _ in range(config.stable_shock_episodes):
        for arm in arms:
            arm_rows, arm_receipts = _run_arm_episode(
                int(seed), episode, arm, "stable_shock", config
            )
            rows.extend(arm_rows)
            receipts.append(
                {"episode": episode, "arm": arm, "scenario": "stable_shock", **arm_receipts}
            )
        episode += 1
    return {
        "schema": V029_SCHEMA,
        "seed": int(seed),
        "cohort": cohort,
        "config": asdict(config),
        "rows": rows,
        "seed_summary": _seed_summary(int(seed), rows, receipts),
        "integrity_receipts": receipts,
    }


def run_v029_exploratory(
    seed: int,
    *,
    config: V029RunConfig,
    arms: Sequence[str] = ("adaptive", "frozen", "no_broadcast"),
) -> dict[str, Any]:
    """Configurable smoke/power entry point that cannot open reserved seeds."""

    if int(seed) in V029_PILOT_SEEDS + V029_OFFICIAL_SEEDS:
        raise PermissionError("exploratory entry point refuses pilot and official seeds")
    return run_online_self_model_revision_seed(
        int(seed),
        config=config,
        cohort="exploratory",
        exploratory=True,
        arms=arms,
    )


def run_v029_motor_yoked_pilot(
    seed: int,
    *,
    config: V029RunConfig = V029_FROZEN_CONFIG,
) -> dict[str, Any]:
    """Isolate closed-loop motor cancellation on a declared pilot seed.

    Public boundary predictions and workspace access remain live, while the
    external world withholds the corrective command.  The diagnostic is
    restricted to the stable-shock episode and cannot open official seeds.
    """

    if int(seed) not in V029_PILOT_SEEDS:
        raise PermissionError(
            "motor-yoked diagnostics accept only declared v0.29 pilot seeds"
        )
    rows, receipts = _run_arm_episode(
        int(seed),
        1,
        "adaptive",
        "stable_shock",
        config,
        motor_execution_yoked_off=True,
    )
    return {
        "schema": "rrct.v029.closed_loop_cancellation_diagnostic.v1",
        "seed": int(seed),
        "cohort": "pilot_diagnostic",
        "config": asdict(config),
        "rows": rows,
        "seed_summary": _seed_summary(
            int(seed),
            rows,
            [
                {
                    "episode": 1,
                    "arm": "adaptive",
                    "scenario": "stable_shock",
                    **receipts,
                }
            ],
        ),
        "integrity_receipts": [
            {
                "episode": 1,
                "arm": "adaptive",
                "scenario": "stable_shock",
                **receipts,
            }
        ],
        "claim_boundary": (
            "Pilot-only mechanism isolation of motor cancellation; not an "
            "official efficacy arm and not evidence of phenomenal awareness."
        ),
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    fields = sorted({str(key) for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(_jsonable(row.get(key)), sort_keys=True)
                    if isinstance(row.get(key), (dict, list, tuple))
                    else _jsonable(row.get(key))
                    for key in fields
                }
            )


def _bootstrap_ci(
    values: FloatArray, replicates: int, rng: np.random.Generator
) -> tuple[float, float]:
    if values.size == 0:
        return float("nan"), float("nan")
    indices = rng.integers(0, values.size, size=(replicates, values.size))
    means = values[indices].mean(axis=1)
    low, high = np.quantile(means, (0.025, 0.975))
    return float(low), float(high)


def _primary_gates(
    seed_summaries: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return frozen primary gates evaluated seed-first and failing closed.

    Tracking utility remains a reported outcome, but in the online phases the
    exact-port actuator makes it numerically identical to public-port accuracy.
    It is therefore not counted again as an independent primary gate.
    """

    gates: list[dict[str, Any]] = []

    def add(name: str, key: str, relation: str, threshold: float) -> None:
        observed: list[dict[str, Any]] = []
        passed = True
        for item in seed_summaries:
            raw = item.get(key)
            value = (
                float(raw)
                if isinstance(raw, (int, float, np.integer, np.floating))
                and not isinstance(raw, (bool, np.bool_))
                and np.isfinite(float(raw))
                else None
            )
            observed.append({"seed": int(item["seed"]), "value": value})
            if value is None:
                passed = False
            elif relation == ">=" and value < threshold:
                passed = False
            elif relation == "<=" and value > threshold:
                passed = False
        gates.append(
            {
                "name": name,
                "metric": key,
                "relation": relation,
                "threshold": threshold,
                "per_seed": observed,
                "pass": passed,
            }
        )

    # Every arm's complete calibration trace is structurally compared by the
    # integrity receipt.  One acquisition gate plus that yoking check avoids
    # counting the identical model seven times.
    add(
        "intact calibration acquires the exact boundary",
        "adaptive_calibration_terminal_private_accuracy",
        ">=",
        0.95,
    )
    for phase in ("route_a", "blackout"):
        label = "initial route" if phase == "route_a" else "probe blackout"
        add(
            f"adaptive {label} retains exact private pair/rank",
            f"adaptive_{phase}_private_accuracy",
            ">=",
            0.90,
        )
        add(
            f"adaptive {label} public port",
            f"adaptive_{phase}_public_port_accuracy",
            ">=",
            0.70,
        )
        add(
            f"adaptive {label} internal projector",
            f"adaptive_{phase}_internal_overlap",
            ">=",
            0.85,
        )
        add(
            f"adaptive {label} sensory projector",
            f"adaptive_{phase}_sensory_overlap",
            ">=",
            0.85,
        )
    for phase in ("route_b", "disconnect", "restore_a"):
        add(
            f"adaptive {phase} exact private pair/rank",
            f"adaptive_{phase}_post_grace_private_accuracy",
            ">=",
            0.80,
        )
        add(
            f"adaptive {phase} public port",
            f"adaptive_{phase}_post_grace_public_port_accuracy",
            ">=",
            0.65,
        )
        if phase != "disconnect":
            # Null-state projector overlaps are defined as one exactly when
            # the private null state is correct, so separate disconnect
            # projector gates would merely recount the accuracy gate.
            add(
                f"adaptive {phase} internal projector",
                f"adaptive_{phase}_post_grace_internal_overlap",
                ">=",
                0.70,
            )
            add(
                f"adaptive {phase} sensory projector",
                f"adaptive_{phase}_post_grace_sensory_overlap",
                ">=",
                0.70,
            )
        latency_threshold = {
            "route_b": 14.0,
            "disconnect": 6.0,
            "restore_a": 14.0,
        }[phase]
        add(
            f"adaptive {phase} latency",
            f"adaptive_{phase}_latency_blocks",
            "<=",
            latency_threshold,
        )
    add(
        "stable shock preserves exact boundary",
        "adaptive_stable_shock_private_accuracy",
        ">=",
        0.90,
    )
    add(
        "stable shock preserves public use",
        "adaptive_stable_shock_public_port_accuracy",
        ">=",
        0.75,
    )
    add(
        "stable shock preserves internal projector",
        "adaptive_stable_shock_internal_overlap",
        ">=",
        0.85,
    )
    add(
        "stable shock preserves sensory projector",
        "adaptive_stable_shock_sensory_overlap",
        ">=",
        0.85,
    )
    add(
        "stable shock causes no boundary revision or revocation",
        "adaptive_stable_shock_revision_or_revocation_count",
        "<=",
        0.0,
    )
    add(
        "stable shock terminal reveal retains the exact boundary",
        "adaptive_stable_shock_terminal_private_accuracy",
        ">=",
        1.0,
    )
    add(
        "frozen boundary does not acquire the transferred route",
        "frozen_route_b_post_grace_private_accuracy",
        "<=",
        0.20,
    )
    for control, label in (
        ("source_deranged", "source derangement"),
        ("time_rolled_replay", "time-rolled replay"),
        ("true_source_lesion", "true-source lesion"),
    ):
        add(
            f"{label} does not acquire the transferred route",
            f"{control}_route_b_post_grace_private_accuracy",
            "<=",
            0.20,
        )
    add(
        "decoy lesion preserves transferred-route acquisition",
        "decoy_source_lesion_route_b_post_grace_private_accuracy",
        ">=",
        0.70,
    )
    add(
        "no-broadcast leaves private revision matched",
        "absolute_adaptive_minus_no_broadcast_route_b_post_grace_private_accuracy",
        "<=",
        0.10,
    )
    add(
        "no-broadcast blocks public port",
        "no_broadcast_route_b_post_grace_public_port_accuracy",
        "<=",
        0.10,
    )
    return gates


def aggregate_online_self_model_revision_results(
    parts: Iterable[Mapping[str, Any]],
    output_dir: str | Path,
    *,
    expected_seeds: Sequence[int] = V029_OFFICIAL_SEEDS,
    bootstrap_replicates: int = 4000,
    bootstrap_seed: int = 20261029,
    status: str,
    recompute_seed_summaries: bool = True,
    strict: bool = True,
) -> dict[str, Any]:
    """Aggregate exact seed parts and write CSV/JSON/SHA-256 artifacts."""

    if not isinstance(status, str) or not status.strip():
        raise ValueError("status must be supplied as a nonempty string")
    parts = tuple(parts)
    observed = tuple(sorted(int(part["seed"]) for part in parts))
    expected = tuple(sorted(int(seed) for seed in expected_seeds))
    if observed != expected or len(set(observed)) != len(observed):
        raise ValueError(
            f"aggregator requires exact seeds {expected}; observed {observed}"
        )
    parts = tuple(sorted(parts, key=lambda part: int(part["seed"])))
    for part in parts:
        if part.get("schema") != V029_SCHEMA:
            raise ValueError("part schema mismatch")
        if int(part["seed_summary"]["seed"]) != int(part["seed"]):
            raise ValueError("seed summary does not match part seed")
    if strict:
        expected_cohort = (
            "official"
            if expected == tuple(sorted(V029_OFFICIAL_SEEDS))
            else "pilot"
            if expected == tuple(sorted(V029_PILOT_SEEDS))
            else None
        )
        expected_config = asdict(V029_FROZEN_CONFIG)
        expected_receipts = {
            (0, arm, "route_change") for arm in V029_ARMS
        } | {
            (1, arm, "stable_shock") for arm in V029_ARMS
        }
        for part in parts:
            part_seed = int(part["seed"])
            if expected_cohort is None or part.get("cohort") != expected_cohort:
                raise ValueError("part cohort does not match the expected seed cohort")
            if part.get("config") != expected_config:
                raise ValueError("part config does not match the frozen v0.29 config")
            part_rows = part.get("rows")
            if not isinstance(part_rows, list) or not part_rows:
                raise ValueError("part rows must be a nonempty list")
            if {row.get("arm") for row in part_rows} != set(V029_ARMS):
                raise ValueError("part rows do not contain exactly the frozen arms")
            observed_groups = {
                (int(row.get("episode", -1)), row.get("arm"), row.get("scenario"))
                for row in part_rows
            }
            if observed_groups != expected_receipts:
                raise ValueError("part rows do not cover the exact arm/episode schedule")
            for row in part_rows:
                if row.get("schema") != V029_SCHEMA or int(row.get("seed", -1)) != part_seed:
                    raise ValueError("row schema or seed does not match its part")
                if row.get("motor_execution_yoked_off", False):
                    raise ValueError("official/pilot efficacy rows cannot be motor-yoked")
                if row.get("commitment_binary") is not True:
                    raise ValueError("row contains a nonbinary causal commitment")
                if row.get("oracle_truth_injected") is not False:
                    raise ValueError("row reports injected evaluator truth")
                if row.get("oracle_counterfactual_only") is not True:
                    raise ValueError("row oracle is not counterfactual-only")
                episode = int(row.get("episode", -1))
                scenario = row.get("scenario")
                if (episode, scenario) not in {
                    (0, "route_change"),
                    (1, "stable_shock"),
                }:
                    raise ValueError("row episode/scenario schedule is invalid")
            for episode, arm, scenario in sorted(expected_receipts):
                group = [
                    row
                    for row in part_rows
                    if int(row["episode"]) == episode
                    and row["arm"] == arm
                    and row["scenario"] == scenario
                ]
                steps = [int(row["step"]) for row in group]
                if steps != list(range(len(group))):
                    raise ValueError("part row steps are duplicated, missing, or reordered")
                allowed_phases = (
                    {"calibration", "route_a", "blackout", "route_b", "disconnect", "restore_a"}
                    if scenario == "route_change"
                    else {"calibration", "stable_shock"}
                )
                if {row["phase"] for row in group} - allowed_phases:
                    raise ValueError("part row phase is invalid for its scenario")
                observed_trace = tuple(
                    (int(row["step"]), row["phase"], int(row["phase_step"]))
                    for row in group
                )
                if observed_trace != _expected_phase_trace(
                    part_seed,
                    episode,
                    V029_FROZEN_CONFIG,
                ):
                    raise ValueError("part rows do not match the frozen seeded schedule")
            raw_receipts = part.get("integrity_receipts")
            if not isinstance(raw_receipts, list):
                raise ValueError("part integrity_receipts must be a list")
            observed_receipts = {
                (int(item.get("episode", -1)), item.get("arm"), item.get("scenario"))
                for item in raw_receipts
            }
            if observed_receipts != expected_receipts or len(raw_receipts) != len(
                expected_receipts
            ):
                raise ValueError("part does not contain the exact arm/episode receipts")
            for item in raw_receipts:
                for key in (
                    "same_observation_all",
                    "transition_chain_all",
                    "source_energy_all",
                    "commitment_blind_bank_all",
                    "anonymous_source_tag_all",
                    "terminal_reveal_ok",
                    "terminal_commitment_unbound",
                    "no_hidden_metadata_agent_api",
                ):
                    if item.get(key) is not True:
                        raise ValueError(f"part integrity receipt failed: {key}")
                if item.get("motor_execution_yoked_off", False):
                    raise ValueError("efficacy receipt cannot be motor-yoked")
                for key in (
                    "terminal_fit_performed",
                    "terminal_revised",
                    "terminal_revoked",
                    "terminal_private_state_correct",
                ):
                    if not isinstance(item.get(key), (bool, np.bool_)):
                        raise ValueError(f"terminal receipt flag is missing: {key}")
                if bool(item["terminal_fit_performed"]) != (
                    item.get("arm") != "frozen"
                ):
                    raise ValueError("terminal fit schedule is inconsistent")
                if not isinstance(item.get("terminal_private_model_digest"), str):
                    raise ValueError("terminal private model digest is missing")
                if bool(item.get("frozen_control_applied")) != (
                    item.get("arm") == "frozen"
                ):
                    raise ValueError("frozen-control receipt is inconsistent")
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("output directory must be empty")

    rows = [dict(row) for part in parts for row in part["rows"]]
    seed_summaries = [
        (
            _seed_summary(
                int(part["seed"]),
                part["rows"],
                part["integrity_receipts"],
            )
            if recompute_seed_summaries
            else dict(part["seed_summary"])
        )
        for part in parts
    ]
    receipts = [
        {"seed": int(part["seed"]), **dict(receipt)}
        for part in parts
        for receipt in part["integrity_receipts"]
    ]
    common_keys = set.intersection(*(set(item) for item in seed_summaries))
    metrics = tuple(
        sorted(
            key
            for key in common_keys
            if (
                key.startswith("adaptive_")
                or key.startswith("adaptive_minus_")
                or key.startswith("decoy_minus_true_source_lesion_")
            )
            and all(
                isinstance(item.get(key), (int, float, np.integer, np.floating))
                and not isinstance(item.get(key), (bool, np.bool_))
                and np.isfinite(float(item[key]))
                for item in seed_summaries
            )
        )
    )
    if not metrics:
        raise ValueError("seed summaries contain no common finite phase metrics")
    rng = np.random.default_rng(bootstrap_seed)
    aggregate_metrics: dict[str, Any] = {}
    for metric in metrics:
        values = np.asarray(
            [float(item[metric]) for item in seed_summaries], dtype=np.float64
        )
        low, high = _bootstrap_ci(values, bootstrap_replicates, rng)
        aggregate_metrics[metric] = {
            "seed_mean": float(np.mean(values)),
            "seed_bootstrap_95_ci": [low, high],
        }
    gates = _primary_gates(seed_summaries)
    integrity_pass = bool(
        all(item.get("integrity_pass", False) for item in seed_summaries)
        and all(
            item.get("same_observation_all", False)
            and item.get("transition_chain_all", False)
            and item.get("source_energy_all", False)
            and item.get("commitment_blind_bank_all", False)
            and item.get("anonymous_source_tag_all", False)
            and item.get("terminal_reveal_ok", False)
            for item in receipts
        )
    )
    all_gates_pass = bool(all(item["pass"] for item in gates))
    summary = {
        "schema": V029_SCHEMA,
        "status": status.strip(),
        "seeds": list(expected),
        "seed_count": len(expected),
        "bootstrap_replicates": int(bootstrap_replicates),
        "bootstrap_seed": int(bootstrap_seed),
        "metrics": aggregate_metrics,
        "primary_gates": gates,
        "all_primary_gates_pass": all_gates_pass,
        "integrity_pass": integrity_pass,
        "overall_pass": bool(integrity_pass and all_gates_pass),
        "seed_summaries_recomputed_from_rows": bool(recompute_seed_summaries),
        "strict_part_validation": bool(strict),
        "claim_boundary": (
            "Passing evidence supports online, functionally used revision of "
            "an agent-owned causal self-boundary within this benchmark; "
            "it would not establish phenomenal awareness or consciousness."
        ),
    }

    rows_path = destination / "v029_online_revision_rows.csv"
    seeds_path = destination / "v029_online_revision_seed_summaries.csv"
    receipts_path = destination / "v029_online_revision_integrity.json"
    summary_path = destination / "v029_online_revision_summary.json"
    _write_csv(rows_path, rows)
    _write_csv(seeds_path, seed_summaries)
    receipts_path.write_text(
        json.dumps(_jsonable(receipts), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(_jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    hash_payload = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (rows_path, seeds_path, receipts_path, summary_path)
    }
    hashes_path = destination / "v029_online_revision_sha256.json"
    hashes_path.write_text(
        json.dumps(hash_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "summary": summary,
        "paths": {
            "rows": str(rows_path),
            "seed_summaries": str(seeds_path),
            "integrity": str(receipts_path),
            "summary": str(summary_path),
            "sha256": str(hashes_path),
        },
        "hashes": hash_payload,
    }


__all__ = [
    "V029_ARMS",
    "V029_OFFICIAL_SEEDS",
    "V029_PILOT_SEEDS",
    "V029_FROZEN_CONFIG",
    "V029RunConfig",
    "aggregate_online_self_model_revision_results",
    "run_online_self_model_revision_seed",
    "run_v029_motor_yoked_pilot",
    "run_v029_exploratory",
]
