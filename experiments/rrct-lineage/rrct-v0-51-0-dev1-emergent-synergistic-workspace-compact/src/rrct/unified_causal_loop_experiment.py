"""Hidden evaluator for the RRCT v0.36 unified causal-loop campaign.

The runtime receives only observations, an anonymous process bank fixed before
the current handle assignment, public task context, action candidates, and the
previously realized external return.  Planted ports, ranks, operators, phase
labels, counterfactual returns, and future noise remain in this module and are
used only after the corresponding runtime receipt has been sealed.

This is a synthetic functional-development experiment.  It is not a test for
phenomenal awareness or subjective experience.
"""

from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
import os
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from .agent import RRCTAgent
from .causal_boundary import CausalBoundaryConfig, CausalBoundaryUpdateReceipt
from .unified_causal_loop import (
    ActionCandidate,
    ActionOutcomeReceipt,
    ActionSelectionReceipt,
    DriftAssessment,
    ProcessBankCommitment,
    PublicBoundaryCertificate,
    PublicBoundaryGateReceipt,
    UnifiedCausalLoop,
    UnifiedCausalLoopConfig,
    UnifiedStepReceipt,
)

FloatArray = NDArray[np.float64]
V036_PILOT_SEEDS = (6451, 6457, 6463, 6469)
V036_DEVELOPMENT_SEEDS = (6501, 6507, 6513, 6519)
V036_FIRST_PILOT_SEED = 6451
V036_SCHEMA = "rrct.v036.unified_causal_loop.v1"
V036_AGENT_STREAM_TAG = 136_036
V036_POLICY_STREAM_TAG = 236_036
V036_BOUNDARY_STREAM_TAG = 336_036
V036_STRUCTURE_STREAM_TAG = 436_036
V036_WORLD_STREAM_TAG = 446_036
V036_BANK_STREAM_TAG = 536_036
V036_CONTEXT_STREAM_TAG = 636_036
V036_PROJECT_ROOT = Path(__file__).resolve().parents[2]
V036_CAMPAIGN_ROOT = (
    V036_PROJECT_ROOT / "validation" / "v0.36_unified_causal_loop_campaign"
).resolve()
V036_DEVELOPMENT_FREEZE_MANIFEST = (
    V036_PROJECT_ROOT / "validation" / "V0_36_PREOUTCOME_FREEZE.json"
)
V036_DEVELOPMENT_FREEZE_CHECKSUM = (
    V036_PROJECT_ROOT / "validation" / "V0_36_PREOUTCOME_FREEZE.json.sha256"
)
V036_REQUIRED_DEVELOPMENT_FREEZE_FILES = (
    "pyproject.toml",
    "uv.lock",
    "CITATION.cff",
    "V0_36_HANDOFF.md",
    "src/rrct/_version.py",
    "src/rrct/agent.py",
    "src/rrct/causal_boundary.py",
    "src/rrct/unified_causal_loop.py",
    "src/rrct/unified_causal_loop_experiment.py",
    "tests/test_v036_development_protocol_spec.py",
    "tests/test_v036_unified_causal_loop.py",
    "validation/V0_36_DEVELOPMENT_PROTOCOL.md",
    "validation/V0_36_DEV2_SOURCE_AND_EVIDENCE_SHA256SUMS.txt",
    "validation/V0_36_LINEAGE_AND_SEED_REGISTRY.json",
    "validation/V0_36_PILOT_ATTEMPTS.md",
    "validation/V0_36_PILOT_D0_EXECUTION_MANIFEST.json",
    "validation/V0_36_PILOT_D0_SOURCE_SHA256SUMS.txt",
    "validation/V0_36_PILOT_REPORT.md",
    "validation/V0_36_POSTPILOT_HARDENING.md",
    "validation/v0.36_unified_causal_loop_pilot_6451_d0_attempt2/artifact_sha256.json",
    "validation/v0.36_unified_causal_loop_pilot_6451_d0_attempt2/executed_source_snapshot.tar.gz",
    "validation/v0.36_unified_causal_loop_pilot_6451_d0_attempt2/v036_unified_causal_loop_rows.jsonl",
    "validation/v0.36_unified_causal_loop_pilot_6451_d0_attempt2/v036_unified_causal_loop_summary.json",
    "validation/v0.36_unified_causal_loop_campaign/claims/attempts/P-0001.json",
    "validation/v0.36_unified_causal_loop_campaign/claims/attempts/P-0002.json",
    "validation/v0.36_unified_causal_loop_campaign/claims/seeds/pilot-seed-6451.json",
)
V036_RUN_START_RECEIPT = "v036_run_start_receipt.json"
V036_ROWS_ARTIFACT = "v036_unified_causal_loop_rows.jsonl"
V036_ATTEMPT_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")

V036_OBSERVATION_DIM = 12
V036_PROCESS_DIM = 8
V036_SOURCE_COUNT = 6
V036_HANDLE_COUNT = 4
V036_ACTION_DIM = 2
V036_CONTEXT_DIM = 2
V036_ACTIONS = np.asarray(
    [
        [0.0, 0.0],
        [1.0, 0.0],
        [-1.0, 0.0],
        [0.0, 1.0],
        [0.0, -1.0],
    ],
    dtype=np.float64,
)
V036_ACTION_KEYS = ("hold", "east", "west", "north", "south")

PhaseName = Literal[
    "stable", "world_shock", "remap", "disconnect", "restore"
]


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


def _array_sha256(value: FloatArray) -> str:
    array = np.ascontiguousarray(value, dtype=np.float64)
    digest = hashlib.sha256()
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(repr(array.shape).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _json_sha256(value: Any) -> str:
    encoded = json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _stream_seed(run_seed: int, stream_tag: int) -> int:
    """Derive a deterministic, run-specific seed for one fixed stream tag."""

    state = np.random.SeedSequence(
        [int(run_seed), int(stream_tag)]
    ).generate_state(1, dtype=np.uint32)
    return int(state[0])


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _failure_jsonable(value: Any) -> Any:
    """Encode an invalid row without permitting JSON NaN/Infinity tokens."""

    if isinstance(value, np.ndarray):
        return _failure_jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _failure_jsonable(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        if np.isnan(value):
            label = "NaN"
        elif value > 0.0:
            label = "+Infinity"
        else:
            label = "-Infinity"
        return {
            "schema": "rrct.v036.tagged_nonfinite.v1",
            "value": label,
        }
    if is_dataclass(value):
        return {
            field.name: _failure_jsonable(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {
            str(key): _failure_jsonable(item) for key, item in value.items()
        }
    if isinstance(value, (tuple, list)):
        return [_failure_jsonable(item) for item in value]
    return value


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def _fsync_directory(directory: Path) -> None:
    """Durably publish a newly created campaign file."""

    descriptor = os.open(
        os.fspath(directory), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_all(descriptor: int, payload: bytes) -> None:
    remaining = memoryview(payload)
    while remaining:
        written = os.write(descriptor, remaining)
        if written <= 0:
            raise OSError("durable campaign write made no progress")
        remaining = remaining[written:]


def _exclusive_json(path: Path, payload: Mapping[str, Any]) -> str:
    """Create one durable JSON receipt without any overwrite window."""

    encoded = (
        json.dumps(
            _jsonable(payload),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    descriptor = os.open(
        os.fspath(path),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )
    try:
        _write_all(descriptor, encoded)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    _fsync_directory(path.parent)
    return hashlib.sha256(encoded).hexdigest()


def _jsonl_row_bytes(row: Mapping[str, Any]) -> bytes:
    payload = (
        _failure_jsonable(row)
        if row.get("hard_integrity_valid") is False
        else _jsonable(row)
    )
    return (
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


class _DurableRowStream:
    """Append-only, per-row-fsynced evidence recoverable after interruption."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._descriptor = os.open(
            os.fspath(path),
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        self._digest = hashlib.sha256()
        self.row_count = 0
        self._closed = False
        _fsync_directory(path.parent)

    @property
    def sha256(self) -> str:
        return self._digest.hexdigest()

    def append(self, row: Mapping[str, Any]) -> None:
        if self._closed:
            raise RuntimeError("durable row stream is closed")
        encoded = _jsonl_row_bytes(row)
        _write_all(self._descriptor, encoded)
        os.fsync(self._descriptor)
        self._digest.update(encoded)
        self.row_count += 1

    def close(self) -> None:
        if not self._closed:
            os.fsync(self._descriptor)
            os.close(self._descriptor)
            self._closed = True
            _fsync_directory(self.path.parent)


class HardIntegrityError(RuntimeError):
    """A durably recorded D0 invariant failure that invalidates the seed."""


@dataclass(frozen=True)
class V036ExperimentConfig:
    """Evaluator-only world and fixed D0 schedule constants."""

    stable_steps: int = 1_440
    world_shock_steps: int = 480
    remap_steps: int = 960
    disconnect_steps: int = 960
    restore_steps: int = 960
    observation_persistence: float = 0.42
    observation_noise: float = 0.035
    return_noise: float = 0.025
    process_energy: float = float(np.sqrt(V036_PROCESS_DIM))
    routed_mode_one: float = 5.8
    routed_mode_two: float = 4.6
    exogenous_mode_one: float = 9.0
    exogenous_mode_two: float = 8.0
    world_shock_multiplier: float = 2.4
    action_observation_scale: float = 0.55
    task_return_scale: float = 1.0
    action_cost: float = 0.04

    def __post_init__(self) -> None:
        for name in (
            "stable_steps",
            "world_shock_steps",
            "remap_steps",
            "disconnect_steps",
            "restore_steps",
        ):
            object.__setattr__(
                self, name, _positive_integer(getattr(self, name), name)
            )
        for name in (
            "observation_noise",
            "return_noise",
            "process_energy",
            "routed_mode_one",
            "routed_mode_two",
            "exogenous_mode_one",
            "exogenous_mode_two",
            "world_shock_multiplier",
            "action_observation_scale",
            "task_return_scale",
            "action_cost",
        ):
            value = _finite(getattr(self, name), name)
            if value < 0.0 or (name not in {"observation_noise", "return_noise", "action_cost"} and value <= 0.0):
                raise ValueError(f"{name} has an invalid sign")
            object.__setattr__(self, name, value)
        persistence = _finite(
            self.observation_persistence, "observation_persistence"
        )
        if not 0.0 <= persistence < 1.0:
            raise ValueError("observation_persistence must lie in [0, 1)")
        object.__setattr__(self, "observation_persistence", persistence)
        if self.routed_mode_one <= self.routed_mode_two:
            raise ValueError("routed mode one must exceed routed mode two")
        if self.exogenous_mode_two <= self.routed_mode_one:
            raise ValueError("the raw-bank exogenous decoy must be stronger than the route")

    @property
    def phase_steps(self) -> tuple[tuple[PhaseName, int], ...]:
        return (
            ("stable", self.stable_steps),
            ("world_shock", self.world_shock_steps),
            ("remap", self.remap_steps),
            ("disconnect", self.disconnect_steps),
            ("restore", self.restore_steps),
        )

    @property
    def total_steps(self) -> int:
        return int(sum(steps for _, steps in self.phase_steps))

    @property
    def is_d0_schedule(self) -> bool:
        return tuple(steps for _, steps in self.phase_steps) == (
            1_440,
            480,
            960,
            960,
            960,
        )


V036_D0_CONFIG = V036ExperimentConfig()


@dataclass(frozen=True)
class _HiddenWorld:
    stable_pair: tuple[int, int]
    remap_pair: tuple[int, int]
    stable_effect: FloatArray
    remap_effect: FloatArray
    stable_internal_projector: FloatArray
    stable_sensory_projector: FloatArray
    remap_internal_projector: FloatArray
    remap_sensory_projector: FloatArray
    exogenous_source: int
    exogenous_effect: FloatArray
    action_effect: FloatArray


@dataclass(frozen=True)
class _PhaseTruth:
    name: PhaseName
    offset: int
    pair: tuple[int, int] | None
    rank: int
    effect: FloatArray | None
    exogenous_multiplier: float


@dataclass(frozen=True)
class _PendingEvaluatorTransition:
    transition_index: int
    phase: _PhaseTruth
    hidden_exogenous_source: int
    observation: FloatArray
    context: FloatArray
    process_bank: FloatArray
    process_bank_sha256: str
    process_bank_receipt: _EvaluatorBankReceipt
    process_bank_commitment: ProcessBankCommitment
    step: UnifiedStepReceipt
    next_observation: FloatArray
    realized_return: float
    oracle_return: float
    action_regret: float
    action_gate_open: bool
    running_mean_return_prediction: float
    running_mean_return_observation_count: int


@dataclass(frozen=True)
class _EvaluatorBankReceipt:
    """Replay evidence that a bank draw did not depend on the live handles."""

    sequence_id: int
    rng_state_before_sha256: str
    process_bank_sha256: str
    replay_process_bank_sha256: str
    replay_valid: bool
    draw_arguments: tuple[str, ...]
    digest: str


def _orthogonal(rng: np.random.Generator, dimension: int) -> FloatArray:
    q, _ = np.linalg.qr(rng.normal(size=(dimension, dimension)))
    return np.asarray(q, dtype=np.float64)


def _hidden_world(seed: int, config: V036ExperimentConfig) -> _HiddenWorld:
    """Construct evaluator truth. No returned field is accepted by the runtime."""

    rng = np.random.default_rng(
        _stream_seed(seed, V036_STRUCTURE_STREAM_TAG)
    )
    handles = rng.permutation(V036_HANDLE_COUNT)
    sources = rng.permutation(V036_SOURCE_COUNT)
    stable_pair = (int(handles[0]), int(sources[0]))
    remap_pair = (int(handles[1]), int(sources[1]))
    exogenous_source = int(sources[2])
    internal = _orthogonal(rng, V036_PROCESS_DIM)
    sensory = _orthogonal(rng, V036_OBSERVATION_DIM)
    stable_internal = internal[:, :2]
    remap_internal = internal[:, 2:4]
    exogenous_internal = internal[:, 4:6]
    stable_sensory = sensory[:, :2]
    remap_sensory = sensory[:, 2:4]
    exogenous_sensory = sensory[:, 4:6]
    action_sensory = sensory[:, 6:8]
    stable_effect = (
        stable_internal
        @ np.diag([config.routed_mode_one, config.routed_mode_two])
        @ stable_sensory.T
    )
    remap_effect = (
        remap_internal
        @ np.diag([config.routed_mode_one, config.routed_mode_two])
        @ remap_sensory.T
    )
    exogenous_effect = (
        exogenous_internal
        @ np.diag([config.exogenous_mode_one, config.exogenous_mode_two])
        @ exogenous_sensory.T
    )
    action_effect = config.action_observation_scale * action_sensory.T
    return _HiddenWorld(
        stable_pair=stable_pair,
        remap_pair=remap_pair,
        stable_effect=stable_effect,
        remap_effect=remap_effect,
        stable_internal_projector=stable_internal @ stable_internal.T,
        stable_sensory_projector=stable_sensory @ stable_sensory.T,
        remap_internal_projector=remap_internal @ remap_internal.T,
        remap_sensory_projector=remap_sensory @ remap_sensory.T,
        exogenous_source=exogenous_source,
        exogenous_effect=exogenous_effect,
        action_effect=action_effect,
    )


def _phase_truth(
    config: V036ExperimentConfig,
    world: _HiddenWorld,
    transition_index: int,
) -> _PhaseTruth:
    if not 0 <= transition_index < config.total_steps:
        raise IndexError("transition index lies outside the fixed schedule")
    start = 0
    for name, steps in config.phase_steps:
        if transition_index < start + steps:
            offset = transition_index - start
            if name in {"stable", "world_shock", "restore"}:
                pair = world.stable_pair
                effect = world.stable_effect
                rank = 2
            elif name == "remap":
                pair = world.remap_pair
                effect = world.remap_effect
                rank = 2
            else:
                pair = None
                effect = None
                rank = 0
            multiplier = (
                config.world_shock_multiplier if name == "world_shock" else 1.0
            )
            return _PhaseTruth(name, offset, pair, rank, effect, multiplier)
        start += steps
    raise RuntimeError("phase schedule is incomplete")


def _equal_energy_process_bank(
    rng: np.random.Generator,
    *,
    energy: float,
) -> FloatArray:
    """Draw an anonymous bank without accepting a phase, pair, or handle."""

    raw = rng.normal(size=(V036_SOURCE_COUNT, V036_PROCESS_DIM))
    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    if np.any(norms <= 1e-12):
        raise FloatingPointError("degenerate process-bank row")
    bank = float(energy) * raw / norms
    if not np.allclose(
        np.linalg.norm(bank, axis=1),
        float(energy),
        rtol=0.0,
        atol=1e-12,
    ):
        raise FloatingPointError("process-bank energy normalization failed")
    return np.asarray(bank, dtype=np.float64)


def _draw_process_bank_with_replay_receipt(
    rng: np.random.Generator,
    *,
    energy: float,
    sequence_id: int,
) -> tuple[FloatArray, _EvaluatorBankReceipt]:
    """Draw and replay a bank before any current handle exists.

    The state is captured before the draw, then installed into a fresh
    generator of the same bit-generator class.  Equality of the two hashes is
    a dynamic check complementing the helper's handle-free API.
    """

    state_before = copy.deepcopy(rng.bit_generator.state)
    state_digest = _json_sha256(state_before)
    bank = _equal_energy_process_bank(rng, energy=energy)
    replay_bit_generator = type(rng.bit_generator)()
    replay_bit_generator.state = copy.deepcopy(state_before)
    replay_rng = np.random.Generator(replay_bit_generator)
    replay_bank = _equal_energy_process_bank(replay_rng, energy=energy)
    bank_sha = _array_sha256(bank)
    replay_sha = _array_sha256(replay_bank)
    replay_valid = bool(
        bank_sha == replay_sha
        and np.array_equal(bank, replay_bank)
    )
    payload = {
        "schema": "rrct.v036.evaluator_process_bank_receipt.v1",
        "sequence_id": int(sequence_id),
        "rng_state_before_sha256": state_digest,
        "process_bank_sha256": bank_sha,
        "replay_process_bank_sha256": replay_sha,
        "replay_valid": replay_valid,
        "draw_arguments": ("rng", "energy"),
    }
    receipt = _EvaluatorBankReceipt(
        sequence_id=int(sequence_id),
        rng_state_before_sha256=state_digest,
        process_bank_sha256=bank_sha,
        replay_process_bank_sha256=replay_sha,
        replay_valid=replay_valid,
        draw_arguments=("rng", "energy"),
        digest=_json_sha256(payload),
    )
    if not replay_valid:
        raise RuntimeError("process-bank replay diverged before handle assignment")
    return bank, receipt


def _task_context(rng: np.random.Generator) -> FloatArray:
    angle = float(rng.uniform(-np.pi, np.pi))
    return np.asarray([np.cos(angle), np.sin(angle)], dtype=np.float64)


def _action_candidates() -> tuple[ActionCandidate, ...]:
    return tuple(
        ActionCandidate(
            key=key,
            action=action.copy(),
            immediate_external_value=0.0,
            alternative_competence=0.0,
            preview_effect_operator=None,
        )
        for key, action in zip(V036_ACTION_KEYS, V036_ACTIONS, strict=True)
    )


def _certificate_pair(
    certificate: PublicBoundaryCertificate | None,
) -> tuple[int, int] | None:
    return None if certificate is None else tuple(certificate.pair)


def _world_transition(
    rng: np.random.Generator,
    config: V036ExperimentConfig,
    world: _HiddenWorld,
    phase: _PhaseTruth,
    observation: FloatArray,
    process_bank: FloatArray,
    handles: FloatArray,
    action: FloatArray,
    context: FloatArray,
    certificate_pair: tuple[int, int] | None,
) -> tuple[FloatArray, float, float, float, bool]:
    """Apply hidden dynamics only after the action and causal receipts exist."""

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
        + rng.normal(0.0, config.observation_noise, V036_OBSERVATION_DIM)
    )
    noiseless_returns = np.zeros(len(V036_ACTIONS), dtype=np.float64)
    if gate_open:
        noiseless_returns = (
            config.task_return_scale * (V036_ACTIONS @ context)
            - config.action_cost * np.sum(V036_ACTIONS * V036_ACTIONS, axis=1)
        )
    selected_matches = np.all(V036_ACTIONS == action[None, :], axis=1)
    if int(np.sum(selected_matches)) != 1:
        raise RuntimeError("selected action is not one of the fixed candidates")
    selected_index = int(np.flatnonzero(selected_matches)[0])
    selected_noiseless = float(noiseless_returns[selected_index])
    oracle_return = float(np.max(noiseless_returns))
    realized_return = selected_noiseless + float(
        rng.normal(0.0, config.return_noise)
    )
    return (
        np.asarray(next_observation, dtype=np.float64),
        realized_return,
        oracle_return,
        oracle_return - selected_noiseless,
        gate_open,
    )


def _boundary_config(run_seed: int) -> CausalBoundaryConfig:
    return CausalBoundaryConfig(
        observation_dim=V036_OBSERVATION_DIM,
        process_dim=V036_PROCESS_DIM,
        source_count=V036_SOURCE_COUNT,
        handle_count=V036_HANDLE_COUNT,
        evidence_capacity=480,
        minimum_samples=480,
        fit_interval=480,
        structural_confirmation_interval=480,
        commitment_block_size=20,
        ridge=0.50,
        null_permutations=128,
        half_null_permutations=128,
        null_quantile=0.99,
        higher_mode_null="cross_fitted_reduced_rank_randomization_bootstrap",
        revision_confirmations=2,
        revocation_confirmations=2,
        confidence_decay=0.65,
        seed=_stream_seed(run_seed, V036_BOUNDARY_STREAM_TAG),
    )


def _runtime_config(run_seed: int) -> UnifiedCausalLoopConfig:
    return UnifiedCausalLoopConfig(
        context_dim=V036_CONTEXT_DIM,
        exploration_probability=0.15,
        policy_temperature=0.35,
        minimum_propensity=0.01,
        maximum_inverse_propensity=20.0,
        model_ridge=0.50,
        model_discount=0.997,
        candidate_value_bound=1_000.0,
        drift_capacity=960,
        drift_baseline_samples=240,
        drift_recent_samples=240,
        drift_fit_interval=40,
        drift_ridge=0.50,
        drift_threshold=0.30,
        seed=_stream_seed(run_seed, V036_POLICY_STREAM_TAG),
    )


def _agent(boundary_config: CausalBoundaryConfig, run_seed: int) -> RRCTAgent:
    return RRCTAgent(
        V036_OBSERVATION_DIM,
        projector_ranks=(3, 6, 9, 12),
        action_dim=V036_ACTION_DIM,
        n_specialists=6,
        specialist_dim=16,
        workspace_dim=16,
        workspace_capacity=3,
        self_dim=12,
        memory_capacity=64,
        memory_top_k=3,
        seed=_stream_seed(run_seed, V036_AGENT_STREAM_TAG),
        causal_boundary_config=boundary_config,
        causal_boundary_broadcast_gain=2.0,
    )


def _pair_json(pair: tuple[int, int] | None) -> list[int] | None:
    return None if pair is None else [int(pair[0]), int(pair[1])]


def _public_design_telemetry(
    selection: ActionSelectionReceipt,
    certificate: PublicBoundaryCertificate | None,
) -> dict[str, Any]:
    """Audit the public identity fields already sealed into action designs."""

    designs = np.asarray(selection.candidate_designs, dtype=np.float64)
    identity_dim = 1 + V036_HANDLE_COUNT + V036_SOURCE_COUNT
    identity_start = (
        1
        + V036_OBSERVATION_DIM
        + V036_CONTEXT_DIM
        + V036_ACTION_DIM
        + 7
    )
    identity_stop = identity_start + identity_dim
    action_identity_width = V036_ACTION_DIM * identity_dim
    identity_columns = designs[:, identity_start:identity_stop]
    action_identity_columns = designs[:, -action_identity_width:]
    expected_identity = np.zeros(identity_dim, dtype=np.float64)
    if certificate is not None:
        expected_identity[0] = 1.0
        handle_index, source_index = certificate.pair
        expected_identity[1 + handle_index] = 1.0
        expected_identity[1 + V036_HANDLE_COUNT + source_index] = 1.0
    expected_identities = np.repeat(
        expected_identity[None, :], len(selection.candidate_keys), axis=0
    )
    expected_interactions = np.stack(
        [
            np.outer(action, expected_identity).reshape(-1)
            for action in np.asarray(selection.candidate_actions, dtype=np.float64)
        ]
    )
    expected_digest = None if certificate is None else certificate.digest
    return {
        "expected_public_identity": expected_identity.tolist(),
        "candidate_public_identity_columns": identity_columns.tolist(),
        "candidate_action_public_identity_interactions": (
            action_identity_columns.tolist()
        ),
        "public_identity_encoding_valid": bool(
            np.array_equal(identity_columns, expected_identities)
        ),
        "public_action_identity_interactions_valid": bool(
            np.array_equal(action_identity_columns, expected_interactions)
        ),
        "action_certificate_reference_valid": bool(
            selection.public_certificate_digest == expected_digest
        ),
    }


def _reveal_row(
    pending: _PendingEvaluatorTransition,
    outcome: ActionOutcomeReceipt,
    drift: DriftAssessment | None,
    update: CausalBoundaryUpdateReceipt,
    public_after: PublicBoundaryCertificate | None,
    public_gate_after: PublicBoundaryGateReceipt | None,
    runtime_instance_digest: str,
    runtime_identity_ok: bool,
    *,
    interrupted_transitions: int,
    sanitized_agent_audit_valid: bool,
) -> dict[str, Any]:
    fit_pair = (
        None
        if update.fit_handle_index is None or update.fit_source_index is None
        else (int(update.fit_handle_index), int(update.fit_source_index))
    )
    state_pair = (
        None
        if update.selected_handle_index is None
        or update.selected_source_index is None
        else (
            int(update.selected_handle_index),
            int(update.selected_source_index),
        )
    )
    action_public = pending.step.public_boundary
    action_public_pair = _certificate_pair(action_public)
    phase_pair = pending.phase.pair
    exact = bool(state_pair == phase_pair and int(update.rank) == pending.phase.rank)
    public_exact = bool(
        (public_after is None and pending.phase.rank == 0)
        or (
            public_after is not None
            and tuple(public_after.pair) == phase_pair
            and int(public_after.rank) == pending.phase.rank
        )
    )
    selection = pending.step.action_selection
    design_telemetry = _public_design_telemetry(selection, action_public)
    prequential_checks = {
        "selection_to_outcome": outcome.selection_digest == selection.digest,
        "selected_action_to_step": bool(
            np.array_equal(selection.selected_action, pending.step.action)
            and selection.selected_key == pending.step.action_key
        ),
        "selected_propensity_to_step": bool(
            selection.selected_propensity == pending.step.action_propensity
            and selection.selected_propensity
            == float(selection.propensities[selection.selected_index])
        ),
        "propensities_normalized": bool(
            np.all(np.isfinite(selection.propensities))
            and np.isclose(float(np.sum(selection.propensities)), 1.0)
        ),
        "commitment_to_update": (
            update.commitment_digest == pending.step.causal_commitment.digest
        ),
        "commitment_to_bound_transition": (
            pending.step.bound_transition.commitment_digest
            == pending.step.causal_commitment.digest
        ),
        "transition_to_update": (
            update.transition_digest
            == pending.step.bound_transition.transition_digest
        ),
        "bank_commitment_to_step": (
            pending.process_bank_commitment.digest
            == pending.step.process_bank_commitment_digest
        ),
        "bank_draw_to_commitment": bool(
            pending.process_bank_receipt.sequence_id
            == pending.process_bank_commitment.sequence_id
            == pending.transition_index
            and pending.process_bank_receipt.process_bank_sha256
            == _array_sha256(pending.process_bank_commitment.process_bank)
            and pending.process_bank_commitment.agent_time == selection.time
        ),
        "reveal_time": outcome.reveal_time == selection.time + 1,
        "model_updates": bool(
            outcome.transition_model_updated and outcome.return_model_updated
        ),
        "realized_return_matches": bool(
            outcome.realized_external_return is not None
            and float(outcome.realized_external_return)
            == float(pending.realized_return)
        ),
        "sanitized_agent_audit": sanitized_agent_audit_valid,
    }
    row = {
        "schema": V036_SCHEMA,
        "seed": None,
        "transition_index": pending.transition_index,
        "phase": pending.phase.name,
        "phase_offset": pending.phase.offset,
        "runtime_instance_digest": runtime_instance_digest,
        "runtime_identity_ok": runtime_identity_ok,
        "reset_count": 0,
        "evaluator_truth_leak": False,
        "hidden_pair_evaluator_only": _pair_json(phase_pair),
        "hidden_rank_evaluator_only": pending.phase.rank,
        "hidden_exogenous_source_evaluator_only": (
            pending.hidden_exogenous_source
        ),
        "process_bank_sha256": pending.process_bank_sha256,
        "process_bank_generation_receipt": _jsonable(
            pending.process_bank_receipt
        ),
        "process_bank_replay_valid": pending.process_bank_receipt.replay_valid,
        "process_bank_commitment_digest": pending.process_bank_commitment.digest,
        "process_bank_row_norms": np.linalg.norm(
            pending.process_bank, axis=1
        ).tolist(),
        "equal_energy_bank": bool(
            np.allclose(
                np.linalg.norm(pending.process_bank, axis=1),
                np.linalg.norm(pending.process_bank[0]),
                rtol=0.0,
                atol=1e-12,
            )
        ),
        "causal_handle_commitment_digest": pending.step.causal_commitment.digest,
        "causal_handles": pending.step.causal_commitment.handles.tolist(),
        "bound_transition_digest": pending.step.bound_transition.transition_digest,
        "outcome_digest": update.outcome_digest,
        "action_outcome_digest": outcome.digest,
        "causal_boundary_update_receipt": _jsonable(update),
        "prequential_checks": prequential_checks,
        "prequential_chain_valid": bool(all(prequential_checks.values())),
        "observation": pending.observation.tolist(),
        "next_observation": pending.next_observation.tolist(),
        "task_context": pending.context.tolist(),
        "candidate_keys": list(selection.candidate_keys),
        "candidate_actions": selection.candidate_actions.tolist(),
        "candidate_preview_all_null": True,
        "route_strengths": selection.route_strengths.tolist(),
        "predicted_next_observations": (
            selection.predicted_next_observations.tolist()
        ),
        "predicted_external_returns": selection.predicted_external_returns.tolist(),
        "policy_scores": selection.policy_scores.tolist(),
        "action_propensities": selection.propensities.tolist(),
        "selected_action_index": selection.selected_index,
        "selected_action_key": selection.selected_key,
        "selected_action": selection.selected_action.tolist(),
        "selected_propensity": selection.selected_propensity,
        "action_public_certificate_digest": selection.public_certificate_digest,
        "action_public_pair": _pair_json(action_public_pair),
        "action_public_rank": None if action_public is None else action_public.rank,
        "action_public_exact_evaluator_only": bool(
            (action_public is None and pending.phase.rank == 0)
            or (
                action_public_pair == phase_pair
                and action_public is not None
                and int(action_public.rank) == pending.phase.rank
            )
        ),
        "action_public_workspace_access_digest": (
            None
            if action_public is None
            else action_public.workspace_access_digest
        ),
        "action_gate_open_evaluator_only": pending.action_gate_open,
        "realized_external_return": pending.realized_return,
        "oracle_external_return_evaluator_only": pending.oracle_return,
        "action_regret_evaluator_only": pending.action_regret,
        "running_mean_return_prediction_evaluator_only": (
            pending.running_mean_return_prediction
        ),
        "running_mean_return_observation_count_evaluator_only": (
            pending.running_mean_return_observation_count
        ),
        "running_mean_return_prediction_error_evaluator_only": (
            pending.realized_return - pending.running_mean_return_prediction
        ),
        "predicted_selected_return": outcome.predicted_external_return,
        "return_prediction_error": outcome.return_prediction_error,
        "transition_prediction_error": outcome.transition_prediction_error,
        "inverse_propensity_weight": outcome.inverse_propensity_weight,
        "transition_model_updated": outcome.transition_model_updated,
        "return_model_updated": outcome.return_model_updated,
        "fit_performed": update.fit_performed,
        "fit_pair": _pair_json(fit_pair),
        "fit_rank": update.fit_rank,
        "fit_confidence": update.fit_confidence,
        "structural_event": update.structural_event,
        "boundary_pair_after_reveal": _pair_json(state_pair),
        "boundary_rank_after_reveal": update.rank,
        "boundary_confidence_after_reveal": update.confidence,
        "boundary_epoch_after_reveal": update.epoch,
        "boundary_model_digest_after_reveal": update.model_digest_after,
        "structural_exact_evaluator_only": exact,
        "public_certificate_after_reveal": (
            None if public_after is None else public_after.digest
        ),
        "public_pair_after_reveal": (
            None if public_after is None else _pair_json(tuple(public_after.pair))
        ),
        "public_rank_after_reveal": (
            None if public_after is None else public_after.rank
        ),
        "public_workspace_access_digest_after_reveal": (
            None
            if public_after is None
            else public_after.workspace_access_digest
        ),
        "public_exact_evaluator_only": public_exact,
        "action_public_gate_receipt": _jsonable(
            pending.step.public_boundary_gate
        ),
        "action_public_gate_event": pending.step.public_boundary_gate.event,
        "action_public_quarantine_active": (
            pending.step.public_boundary_gate.quarantine_active
        ),
        "action_public_quarantine_signature": _jsonable(
            pending.step.public_boundary_gate.quarantine_signature
        ),
        "public_gate_after_reveal": (
            None if public_gate_after is None else _jsonable(public_gate_after)
        ),
        "public_gate_event_after_reveal": (
            None if public_gate_after is None else public_gate_after.event
        ),
        "public_quarantine_active_after_reveal": bool(
            public_gate_after is not None and public_gate_after.quarantine_active
        ),
        "public_quarantine_signature_after_reveal": (
            None
            if public_gate_after is None
            else _jsonable(public_gate_after.quarantine_signature)
        ),
        "drift": None if drift is None else _jsonable(drift),
        "reopen_requested": bool(drift is not None and drift.reopen_requested),
        "interrupted_transitions": int(interrupted_transitions),
    }
    row.update(design_telemetry)
    return row


def _row_hard_integrity(row: Mapping[str, Any]) -> dict[str, bool]:
    """Return the per-row invariants whose failure must stop the seed."""

    propensities = np.asarray(row["action_propensities"], dtype=np.float64)
    route_strengths = np.asarray(row["route_strengths"], dtype=np.float64)
    finite_arrays = (
        propensities,
        route_strengths,
        np.asarray(row["causal_handles"], dtype=np.float64),
        np.asarray(row["observation"], dtype=np.float64),
        np.asarray(row["next_observation"], dtype=np.float64),
        np.asarray(row["task_context"], dtype=np.float64),
        np.asarray(row["candidate_actions"], dtype=np.float64),
        np.asarray(row["predicted_next_observations"], dtype=np.float64),
        np.asarray(row["predicted_external_returns"], dtype=np.float64),
        np.asarray(row["policy_scores"], dtype=np.float64),
    )
    finite_scalars = (
        row["selected_propensity"],
        row["realized_external_return"],
        row["predicted_selected_return"],
        row["transition_prediction_error"],
        row["return_prediction_error"],
        row["inverse_propensity_weight"],
    )
    return {
        "runtime_identity": bool(row["runtime_identity_ok"]),
        "zero_resets": int(row["reset_count"]) == 0,
        "no_evaluator_truth_leak": not bool(row["evaluator_truth_leak"]),
        "prequential_chain": bool(row["prequential_chain_valid"]),
        "equal_energy_bank": bool(row["equal_energy_bank"]),
        "process_bank_replay": bool(row["process_bank_replay_valid"]),
        "finite_numeric_payload": bool(
            all(np.all(np.isfinite(value)) for value in finite_arrays)
            and all(value is not None and np.isfinite(float(value)) for value in finite_scalars)
        ),
        "propensities_normalized": bool(
            propensities.ndim == 1
            and len(propensities) > 0
            and np.isclose(float(np.sum(propensities)), 1.0)
        ),
        "minimum_propensity": bool(
            len(propensities) > 0 and float(np.min(propensities)) >= 0.01
        ),
        "maximum_inverse_weight": float(row["inverse_propensity_weight"]) <= 20.0,
        "models_updated_once": bool(
            row["transition_model_updated"] and row["return_model_updated"]
        ),
        "zero_interruptions": int(row["interrupted_transitions"]) == 0,
        "candidate_previews_null": bool(row["candidate_preview_all_null"]),
        "route_strengths_zero": bool(
            np.array_equal(route_strengths, np.zeros_like(route_strengths))
        ),
        "public_identity_encoding": bool(row["public_identity_encoding_valid"]),
        "public_action_identity_interactions": bool(
            row["public_action_identity_interactions_valid"]
        ),
        "public_certificate_reference": bool(
            row["action_certificate_reference_valid"]
        ),
    }


def _seal_row_or_stop(
    row: dict[str, Any],
    sealed_row_sink: Callable[[Mapping[str, Any]], None] | None,
) -> None:
    checks = _row_hard_integrity(row)
    row["hard_integrity_checks"] = checks
    row["hard_integrity_valid"] = bool(all(checks.values()))
    if not row["hard_integrity_valid"]:
        row["failure_row_schema"] = "rrct.v036.hard_integrity_failure_row.v1"
    if sealed_row_sink is not None:
        sealed_row_sink(row)
    if not row["hard_integrity_valid"]:
        failed = ", ".join(name for name, valid in checks.items() if not valid)
        raise HardIntegrityError(
            "hard-integrity failure after sealing transition "
            f"{row['transition_index']}: {failed}"
        )


def _split_mse(rows: Sequence[Mapping[str, Any]], key: str) -> dict[str, float]:
    values = [float(row[key]) ** 2 for row in rows if row[key] is not None]
    if not values:
        return {"first_half": 0.0, "second_half": 0.0}
    split = max(1, len(values) // 2)
    return {
        "first_half": float(np.mean(values[:split])),
        "second_half": float(np.mean(values[split:])),
    }


def _phase_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("phase summary requires rows")
    terminal = rows[-1]
    drift_rows = [row for row in rows if row["drift"] is not None]
    reopen = [row for row in drift_rows if row["reopen_requested"]]
    return {
        "rows": len(rows),
        "structural_exact_fraction": float(
            np.mean([bool(row["structural_exact_evaluator_only"]) for row in rows])
        ),
        "public_available_fraction": float(
            np.mean([row["action_public_certificate_digest"] is not None for row in rows])
        ),
        "public_exact_fraction": float(
            np.mean([bool(row["public_exact_evaluator_only"]) for row in rows])
        ),
        "action_public_exact_fraction": float(
            np.mean(
                [bool(row["action_public_exact_evaluator_only"]) for row in rows]
            )
        ),
        "certificate_reference_fraction": float(
            np.mean(
                [bool(row["action_certificate_reference_valid"]) for row in rows]
            )
        ),
        "public_identity_encoding_fraction": float(
            np.mean([bool(row["public_identity_encoding_valid"]) for row in rows])
        ),
        "public_action_identity_interaction_fraction": float(
            np.mean(
                [
                    bool(row["public_action_identity_interactions_valid"])
                    for row in rows
                ]
            )
        ),
        "minimum_selected_propensity": float(
            min(float(row["selected_propensity"]) for row in rows)
        ),
        "maximum_selected_propensity": float(
            max(float(row["selected_propensity"]) for row in rows)
        ),
        "minimum_logged_action_propensity": float(
            min(float(np.min(row["action_propensities"])) for row in rows)
        ),
        "maximum_logged_action_propensity": float(
            max(float(np.max(row["action_propensities"])) for row in rows)
        ),
        "maximum_inverse_propensity_weight": float(
            max(float(row["inverse_propensity_weight"]) for row in rows)
        ),
        "transition_mse": _split_mse(rows, "transition_prediction_error"),
        "return_mse": _split_mse(rows, "return_prediction_error"),
        "running_mean_reference_return_mse": _split_mse(
            rows, "running_mean_return_prediction_error_evaluator_only"
        ),
        "mean_external_return": float(
            np.mean([float(row["realized_external_return"]) for row in rows])
        ),
        "mean_action_regret": float(
            np.mean([float(row["action_regret_evaluator_only"]) for row in rows])
        ),
        "action_gate_open_fraction": float(
            np.mean([bool(row["action_gate_open_evaluator_only"]) for row in rows])
        ),
        "drift_assessment_count": len(drift_rows),
        "reopen_count": len(reopen),
        "first_reopen_latency": (
            None if not reopen else int(reopen[0]["phase_offset"]) + 1
        ),
        "maximum_relative_drift": (
            0.0
            if not drift_rows
            else float(max(float(row["drift"]["relative_drift"]) for row in drift_rows))
        ),
        "structural_events": {
            event: sum(row["structural_event"] == event for row in rows)
            for event in (
                "acquisition_candidate",
                "acquisition",
                "structural_candidate",
                "pair_revision",
                "rank_revision",
                "null_candidate",
                "revocation",
                "parameter_refresh",
            )
        },
        "terminal_pair": terminal["boundary_pair_after_reveal"],
        "terminal_rank": terminal["boundary_rank_after_reveal"],
        "terminal_epoch": terminal["boundary_epoch_after_reveal"],
        "terminal_public_pair": terminal["public_pair_after_reveal"],
        "terminal_public_rank": terminal["public_rank_after_reveal"],
        "terminal_exact": bool(terminal["structural_exact_evaluator_only"]),
    }


def _campaign_status(seed: int, endpoints: Mapping[str, bool]) -> str:
    """Keep exploratory pilot outcomes distinct from development claims."""

    if not bool(endpoints.get("E01_integrity", False)):
        return "INTEGRITY_FAIL"
    endpoints_met = bool(endpoints) and all(bool(value) for value in endpoints.values())
    if int(seed) in V036_PILOT_SEEDS:
        return "PILOT_ENDPOINTS_MET" if endpoints_met else "PILOT_ENDPOINTS_NOT_MET"
    return (
        "DEVELOPMENT_SEED_ENDPOINTS_MET"
        if endpoints_met
        else "DEVELOPMENT_TARGET_NOT_MET"
    )


def _build_summary(
    seed: int,
    config: V036ExperimentConfig,
    boundary_config: CausalBoundaryConfig,
    runtime_config: UnifiedCausalLoopConfig,
    rows: Sequence[Mapping[str, Any]],
    runtime: UnifiedCausalLoop,
    runtime_instance_digest: str,
    phase_model_counts: Mapping[str, Mapping[str, int]],
    *,
    unflushed_transition: bool,
) -> dict[str, Any]:
    grouped = {
        name: [row for row in rows if row["phase"] == name]
        for name, _ in config.phase_steps
    }
    phases = {name: _phase_summary(values) for name, values in grouped.items()}
    p0 = grouped["stable"]
    p1 = grouped["world_shock"]
    p2 = grouped["remap"]
    p3 = grouped["disconnect"]
    p4 = grouped["restore"]
    first_fit = p0[479] if len(p0) >= 480 else None
    second_fit = p0[959] if len(p0) >= 960 else None
    tail = p0[1_200:1_440] if len(p0) >= 1_440 else []
    p0_signature = (
        p0[-1]["boundary_pair_after_reveal"],
        p0[-1]["boundary_rank_after_reveal"],
        p0[-1]["boundary_epoch_after_reveal"],
    )
    p1_terminal_signature = (
        p1[-1]["boundary_pair_after_reveal"],
        p1[-1]["boundary_rank_after_reveal"],
        p1[-1]["boundary_epoch_after_reveal"],
    )
    snapshot = runtime.snapshot()
    terminal_receipt = runtime.terminal_receipt
    post_admission_tail = p0[960:1_440] if len(p0) >= 1_440 else []
    post_admission_return_mse = _split_mse(
        post_admission_tail, "return_prediction_error"
    )
    integrity = {
        "row_hard_integrity_all": all(
            bool(row.get("hard_integrity_valid", False)) for row in rows
        ),
        "one_runtime_instance": all(row["runtime_identity_ok"] for row in rows),
        "row_count_exact": len(rows) == config.total_steps,
        "zero_resets": all(int(row["reset_count"]) == 0 for row in rows),
        "zero_evaluator_truth_leaks": not any(
            bool(row["evaluator_truth_leak"]) for row in rows
        ),
        "prequential_chain_all": all(bool(row["prequential_chain_valid"]) for row in rows),
        "equal_energy_all": all(bool(row["equal_energy_bank"]) for row in rows),
        "process_bank_replay_all": all(
            bool(row["process_bank_replay_valid"]) for row in rows
        ),
        "all_propensities_finite": all(
            np.isfinite(float(row["selected_propensity"])) for row in rows
        ),
        "minimum_propensity_respected": min(
            float(row["selected_propensity"]) for row in rows
        ) >= 0.01,
        "maximum_inverse_weight_respected": max(
            float(row["inverse_propensity_weight"]) for row in rows
        ) <= 20.0,
        "terminal_transition_flushed": not unflushed_transition,
        "terminal_runtime_closed": bool(runtime.closed),
        "terminal_receipt_closed": bool(
            terminal_receipt is not None and terminal_receipt.closed
        ),
        "terminal_no_precommitted_bank": snapshot["precommitted_bank"] is None,
        "terminal_no_pending_runtime_transition": (
            snapshot["pending_transition"] is None
        ),
        "terminal_transition_digest_matches": bool(
            terminal_receipt is not None
            and terminal_receipt.causal_transition_digest
            == rows[-1]["bound_transition_digest"]
        ),
        "terminal_action_outcome_digest_matches": bool(
            terminal_receipt is not None
            and terminal_receipt.previous_action_outcome.digest
            == rows[-1]["action_outcome_digest"]
        ),
        "terminal_time_exact": bool(
            terminal_receipt is not None
            and terminal_receipt.time == config.total_steps
        ),
        "randomized_row_count_exact": int(runtime.randomized_row_count)
        == config.total_steps,
        "zero_interruptions": int(rows[-1]["interrupted_transitions"]) == 0,
        "sanitized_agent_audit_all": all(
            bool(row["prequential_checks"]["sanitized_agent_audit"])
            for row in rows
        ),
        "candidate_previews_all_null": all(
            bool(row["candidate_preview_all_null"]) for row in rows
        ),
        "route_strengths_all_zero": all(
            np.allclose(row["route_strengths"], 0.0) for row in rows
        ),
        "public_design_encodings_all_valid": all(
            bool(row["public_identity_encoding_valid"])
            and bool(row["public_action_identity_interactions_valid"])
            for row in rows
        ),
        "certificate_references_all_valid": all(
            bool(row["action_certificate_reference_valid"]) for row in rows
        ),
    }
    endpoints: dict[str, bool] = {}
    endpoints["E01_integrity"] = bool(all(integrity.values()))
    endpoints["E02_persistent_acquisition"] = bool(
        first_fit is not None
        and second_fit is not None
        and first_fit["fit_pair"] == first_fit["hidden_pair_evaluator_only"]
        and int(first_fit["fit_rank"]) == 2
        and int(first_fit["boundary_rank_after_reveal"]) == 0
        and first_fit["structural_event"] == "acquisition_candidate"
        and second_fit["boundary_pair_after_reveal"]
        == second_fit["hidden_pair_evaluator_only"]
        and int(second_fit["boundary_rank_after_reveal"]) == 2
        and second_fit["structural_event"] == "acquisition"
    )
    endpoints["E03_public_post_admission_use"] = bool(
        len(tail) == 240
        and np.mean(
            [row["action_public_certificate_digest"] is not None for row in tail]
        )
        >= 0.90
        and all(
            np.all(np.isfinite(row["route_strengths"]))
            and np.all(np.isfinite(row["predicted_next_observations"]))
            and np.all(np.isfinite(row["predicted_external_returns"]))
            and bool(row["action_certificate_reference_valid"])
            and bool(row["public_identity_encoding_valid"])
            and bool(row["public_action_identity_interactions_valid"])
            for row in tail
        )
        and all(
            row["action_public_certificate_digest"] is None
            or bool(row["action_public_exact_evaluator_only"])
            for row in tail
        )
        and all(
            np.allclose(row["route_strengths"], 0.0)
            for row in tail
        )
    )
    endpoints["E04_prequential_learning"] = bool(
        phases["stable"]["transition_mse"]["second_half"]
        < phases["stable"]["transition_mse"]["first_half"]
        and len(post_admission_tail) == 480
        and post_admission_return_mse["second_half"]
        < post_admission_return_mse["first_half"]
        and all(row["transition_model_updated"] and row["return_model_updated"] for row in p0)
    )
    endpoints["E05_world_shock_retention"] = bool(
        p1_terminal_signature == p0_signature
        and not any(
            row["structural_event"] in {"pair_revision", "rank_revision", "revocation"}
            for row in p1
        )
        and not any(row["reopen_requested"] for row in p1)
    )
    endpoints["E06_hidden_remap_revision"] = bool(
        any(row["reopen_requested"] for row in p2)
        and phases["remap"]["terminal_exact"]
        and any(
            row["structural_event"] in {"pair_revision", "rank_revision"}
            for row in p2
        )
    )
    endpoints["E07_disconnect_revocation"] = bool(
        any(row["reopen_requested"] for row in p3)
        and phases["disconnect"]["terminal_rank"] == 0
        and phases["disconnect"]["terminal_public_pair"] is None
        and any(row["structural_event"] == "revocation" for row in p3)
        and not any(
            row["boundary_rank_after_reveal"] > 0
            and row["boundary_pair_after_reveal"] is not None
            and row["boundary_pair_after_reveal"][1]
            == row["hidden_exogenous_source_evaluator_only"]
            for row in p3
        )
    )
    endpoints["E08_restoration_reacquisition"] = bool(
        any(row["reopen_requested"] for row in p4)
        and phases["restore"]["terminal_exact"]
        and any(row["structural_event"] == "acquisition" for row in p4)
        and phase_model_counts["restore"]["transition"]
        > phase_model_counts["disconnect"]["transition"]
        and phase_model_counts["restore"]["return"]
        > phase_model_counts["disconnect"]["return"]
    )
    status = _campaign_status(seed, endpoints)
    earliest_failed_layer = next(
        (name for name, met in endpoints.items() if not met), None
    )
    return {
        "schema": "rrct.v036.unified_causal_loop.summary.v1",
        "version": "0.36.0.dev2",
        "seed": int(seed),
        "campaign_kind": "pilot" if seed in V036_PILOT_SEEDS else "development",
        "config": asdict(config),
        "causal_boundary_config": _jsonable(boundary_config),
        "unified_runtime_config": _jsonable(runtime_config),
        "derived_stream_seeds": {
            "agent": _stream_seed(seed, V036_AGENT_STREAM_TAG),
            "boundary": _stream_seed(seed, V036_BOUNDARY_STREAM_TAG),
            "policy": _stream_seed(seed, V036_POLICY_STREAM_TAG),
            "hidden_structure_evaluator_only": _stream_seed(
                seed, V036_STRUCTURE_STREAM_TAG
            ),
            "world_noise_evaluator_only": _stream_seed(
                seed, V036_WORLD_STREAM_TAG
            ),
            "process_bank": _stream_seed(seed, V036_BANK_STREAM_TAG),
            "task_context": _stream_seed(seed, V036_CONTEXT_STREAM_TAG),
        },
        "runtime_instance_digest": runtime_instance_digest,
        "fixed_actions": V036_ACTIONS.tolist(),
        "phase_summaries": phases,
        "stable_post_admission_return_mse": post_admission_return_mse,
        "phase_model_update_counts": _jsonable(phase_model_counts),
        "terminal_flush": (
            None if terminal_receipt is None else _jsonable(terminal_receipt)
        ),
        "terminal_flush_audit": {
            "closed": bool(runtime.closed),
            "successor_action_emitted": False,
            "successor_causal_commitment_emitted": False,
            "precommitted_bank_remaining": (
                snapshot["precommitted_bank"] is not None
            ),
            "pending_transition_remaining": (
                snapshot["pending_transition"] is not None
            ),
        },
        "integrity": integrity,
        "endpoints": endpoints,
        "earliest_failed_layer": earliest_failed_layer,
        "all_endpoints_met": bool(all(endpoints.values())),
        "status": status,
        "interpretation_boundary": (
            "Persistent truth-free boundary-mediated action-loop development in "
            "a bounded synthetic world; not evidence of phenomenal awareness, "
            "subjective experience, sentience, or valence."
        ),
    }


def _run_trace(
    seed: int,
    *,
    experiment_config: V036ExperimentConfig,
    boundary_config: CausalBoundaryConfig,
    runtime_config: UnifiedCausalLoopConfig,
    sealed_row_sink: Callable[[Mapping[str, Any]], None] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Execute a fixed trace; optionally durably seal each completed row.

    ``sealed_row_sink`` defaults to ``None`` so existing in-memory tests and
    diagnostic callers retain the original API behavior.
    """

    world = _hidden_world(seed, experiment_config)
    world_rng = np.random.default_rng(
        _stream_seed(seed, V036_WORLD_STREAM_TAG)
    )
    bank_rng = np.random.default_rng(
        _stream_seed(seed, V036_BANK_STREAM_TAG)
    )
    context_rng = np.random.default_rng(
        _stream_seed(seed, V036_CONTEXT_STREAM_TAG)
    )
    agent = _agent(boundary_config, seed)
    runtime = UnifiedCausalLoop(agent, runtime_config)
    runtime_identity = id(runtime)
    agent_identity = id(agent)
    runtime_instance_digest = runtime.snapshot()["digest"]
    observation = world_rng.normal(0.0, 0.25, V036_OBSERVATION_DIM)
    previous_return: float | None = None
    pending: _PendingEvaluatorTransition | None = None
    rows: list[dict[str, Any]] = []
    phase_model_counts: dict[str, dict[str, int]] = {}
    phase_lengths = dict(experiment_config.phase_steps)
    running_return_sum = 0.0
    running_return_count = 0

    for transition_index in range(experiment_config.total_steps):
        phase = _phase_truth(experiment_config, world, transition_index)
        bank, bank_receipt = _draw_process_bank_with_replay_receipt(
            bank_rng,
            energy=experiment_config.process_energy,
            sequence_id=transition_index,
        )
        bank_sha = _array_sha256(bank)
        if bank_receipt.process_bank_sha256 != bank_sha:
            raise RuntimeError("process bank receipt does not bind the live bank")
        bank_commitment = runtime.precommit_process_bank(bank)
        if _array_sha256(bank_commitment.process_bank) != bank_sha:
            raise RuntimeError("process bank changed after precommitment")
        context = _task_context(context_rng)
        step = runtime.advance(
            observation,
            _action_candidates(),
            observable_context=context,
            realized_external_return=previous_return,
            source="v036_unified_causal_loop",
        )
        runtime_identity_ok = bool(
            id(runtime) == runtime_identity and id(agent) == agent_identity
        )
        if pending is not None:
            if step.previous_action_outcome is None:
                raise RuntimeError("pending evaluator transition has no outcome")
            if step.causal_boundary_update is None:
                raise RuntimeError("pending causal transition has no update receipt")
            running_return_sum += float(pending.realized_return)
            running_return_count += 1
        # This private access audits only the already revealed prior row.  A
        # failing row is durably sealed and stops the seed before any current
        # world consequence or world-noise draw is consumed.
        agent_result = agent.last_result
        if agent_result is None:
            raise RuntimeError("agent emitted no step result")
        if pending is not None:
            outcome = step.previous_action_outcome
            update = step.causal_boundary_update
            if outcome is None:
                raise RuntimeError("pending evaluator transition has no outcome")
            if update is None:
                raise RuntimeError("pending causal transition has no update receipt")
            agent_update = agent_result.causal_boundary_update_receipt
            audit_valid = bool(
                agent_update is not None and agent_update == update
            )
            row = _reveal_row(
                pending,
                outcome,
                step.drift,
                update,
                step.public_boundary,
                step.public_boundary_gate,
                runtime_instance_digest,
                runtime_identity_ok,
                interrupted_transitions=(
                    agent_result.causal_interrupted_transitions
                ),
                sanitized_agent_audit_valid=audit_valid,
            )
            row["seed"] = int(seed)
            _seal_row_or_stop(row, sealed_row_sink)
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

        running_mean_prediction = (
            0.0
            if running_return_count == 0
            else running_return_sum / running_return_count
        )
        # Only a current action whose preceding revealed row passed every hard
        # integrity check is allowed to reach evaluator world dynamics.
        (
            next_observation,
            realized_return,
            oracle_return,
            action_regret,
            gate_open,
        ) = _world_transition(
            world_rng,
            experiment_config,
            world,
            phase,
            observation,
            bank,
            step.causal_commitment.handles,
            step.action,
            context,
            _certificate_pair(step.public_boundary),
        )

        pending = _PendingEvaluatorTransition(
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
            realized_return=realized_return,
            oracle_return=oracle_return,
            action_regret=action_regret,
            action_gate_open=gate_open,
            running_mean_return_prediction=float(running_mean_prediction),
            running_mean_return_observation_count=running_return_count,
        )
        observation = next_observation
        previous_return = realized_return

    if pending is None or previous_return is None:
        raise RuntimeError("fixed trace produced no terminal transition")
    if not hasattr(runtime, "flush"):
        raise RuntimeError("UnifiedCausalLoop lacks the D0 terminal flush API")
    flushed = runtime.flush(
        observation,
        realized_external_return=previous_return,
        source="v036_unified_causal_loop_terminal_flush",
    )
    # The flush contract mirrors the outcome/certificate portion of a step but
    # emits no action or new causal commitment.
    outcome = flushed.previous_action_outcome
    if outcome is None:
        raise RuntimeError("terminal flush emitted no action outcome")
    agent_result = agent.last_result
    if agent_result is None:
        raise RuntimeError("terminal flush emitted no agent result")
    update = flushed.causal_boundary_update
    if update is None:
        raise RuntimeError("terminal flush emitted no causal update receipt")
    agent_update = agent_result.causal_boundary_update_receipt
    row = _reveal_row(
        pending,
        outcome,
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
    row["seed"] = int(seed)
    _seal_row_or_stop(row, sealed_row_sink)
    rows.append(row)
    terminal_snapshot = runtime.snapshot()
    phase_model_counts[pending.phase.name] = {
        "transition": int(
            terminal_snapshot["transition_model"]["observation_count"]
        ),
        "return": int(terminal_snapshot["return_model"]["observation_count"]),
    }
    unflushed = bool(runtime.awaiting_outcome)
    summary = _build_summary(
        seed,
        experiment_config,
        boundary_config,
        runtime_config,
        rows,
        runtime,
        runtime_instance_digest,
        phase_model_counts,
        unflushed_transition=unflushed,
    )
    return rows, summary


def _write_evidence_artifacts(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    destination: Path,
    *,
    presealed_rows_sha256: str | None = None,
    presealed_row_count: int | None = None,
    additional_hashes: Mapping[str, str] | None = None,
) -> dict[str, str]:
    rows_path = destination / V036_ROWS_ARTIFACT
    expected_rows_digest = hashlib.sha256()
    for row in rows:
        expected_rows_digest.update(_jsonl_row_bytes(row))
    expected_rows_sha256 = expected_rows_digest.hexdigest()
    if presealed_rows_sha256 is None:
        stream = _DurableRowStream(rows_path)
        try:
            for row in rows:
                stream.append(row)
        finally:
            stream.close()
        rows_sha256 = stream.sha256
    else:
        if presealed_row_count != len(rows):
            raise RuntimeError("presealed row count does not match completed trace")
        if presealed_rows_sha256 != expected_rows_sha256:
            raise RuntimeError("presealed row digest does not match completed trace")
        if not rows_path.is_file():
            raise FileNotFoundError("presealed row stream is missing")
        rows_sha256 = hashlib.sha256(rows_path.read_bytes()).hexdigest()
        if rows_sha256 != presealed_rows_sha256:
            raise RuntimeError("durable row stream changed after sealing")
    summary_path = destination / "v036_unified_causal_loop_summary.json"
    summary_sha256 = _exclusive_json(summary_path, summary)
    hashes = {
        rows_path.name: rows_sha256,
        summary_path.name: summary_sha256,
    }
    if additional_hashes is not None:
        for name, digest in additional_hashes.items():
            if (
                not isinstance(name, str)
                or Path(name).name != name
                or name in hashes
                or not isinstance(digest, str)
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise ValueError("invalid additional artifact hash")
            hashes[name] = digest
    manifest_path = destination / "artifact_sha256.json"
    _exclusive_json(manifest_path, hashes)
    return hashes


def _validate_attempt_id(attempt_id: str | None) -> str:
    if (
        not isinstance(attempt_id, str)
        or V036_ATTEMPT_PATTERN.fullmatch(attempt_id) is None
    ):
        raise ValueError(
            "attempt_id is required and must contain only letters, digits, '.', '_', or '-'"
        )
    return attempt_id


def _verify_development_freeze() -> str:
    """Verify the immutable source manifest before any development seed opens."""

    manifest_path = Path(V036_DEVELOPMENT_FREEZE_MANIFEST)
    checksum_path = Path(V036_DEVELOPMENT_FREEZE_CHECKSUM)
    if not manifest_path.is_file() or not checksum_path.is_file():
        raise RuntimeError(
            "development execution requires a frozen v0.36 source manifest"
        )
    raw = manifest_path.read_bytes()
    manifest_sha256 = hashlib.sha256(raw).hexdigest()
    checksum_fields = checksum_path.read_text(encoding="ascii").strip().split()
    if (
        len(checksum_fields) != 2
        or checksum_fields[0] != manifest_sha256
        or checksum_fields[1] != manifest_path.name
    ):
        raise RuntimeError("v0.36 development freeze checksum companion mismatch")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("invalid v0.36 development freeze manifest") from exc
    if (
        not isinstance(payload, Mapping)
        or payload.get("schema") != "rrct.v036.preoutcome_freeze.v1"
        or payload.get("status") != "sealed_before_development_outcomes"
        or payload.get("development_seeds") != list(V036_DEVELOPMENT_SEEDS)
        or not isinstance(payload.get("files"), Mapping)
        or not payload["files"]
    ):
        raise RuntimeError("v0.36 development freeze metadata mismatch")
    project_root = Path(V036_PROJECT_ROOT).resolve()
    listed_files = payload["files"]
    if any(not isinstance(name, str) for name in listed_files):
        raise RuntimeError("development freeze file names must be strings")
    required_files = set(V036_REQUIRED_DEVELOPMENT_FREEZE_FILES)
    for directory, pattern in (
        (project_root / "src" / "rrct", "*.py"),
        (project_root / "tests", "test_*.py"),
    ):
        if directory.is_dir():
            required_files.update(
                path.relative_to(project_root).as_posix()
                for path in directory.glob(pattern)
                if path.is_file()
            )
    omitted = sorted(required_files.difference(listed_files))
    if omitted:
        preview = ", ".join(omitted[:5])
        suffix = "" if len(omitted) <= 5 else f" (+{len(omitted) - 5} more)"
        raise RuntimeError(
            f"development freeze omits required files: {preview}{suffix}"
        )
    for relative_name, expected in listed_files.items():
        if not isinstance(relative_name, str) or not isinstance(expected, Mapping):
            raise TypeError("invalid file entry in v0.36 development freeze")
        candidate = (project_root / relative_name).resolve()
        try:
            candidate.relative_to(project_root)
        except ValueError as exc:
            raise RuntimeError("development freeze file escapes project root") from exc
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
                f"frozen source checksum mismatch: {relative_name}"
            )
    return manifest_sha256


def _prepare_campaign_attempt(
    *,
    seed: int,
    cohort: Literal["pilot", "development"],
    attempt_id: str,
    output: str | Path,
    development_freeze_sha256: str | None,
) -> tuple[Path, Path, str]:
    """Claim one attempt and seed, then publish a pre-RNG start receipt."""

    root = Path(V036_CAMPAIGN_ROOT).resolve()
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
        raise ValueError("output must be inside the fixed campaign_root") from exc
    if not relative_output.parts or relative_output.parts[0] == "claims":
        raise ValueError("output must be a run directory outside the claim ledger")
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("v0.36 output directory must be empty")

    claim_base = {
        "schema": "rrct.v036.campaign_claim.v1",
        "version": "0.36.0.dev2",
        "attempt_id": attempt_id,
        "cohort": cohort,
        "seed": int(seed),
        "campaign_root": os.fspath(root),
        "output_directory": os.fspath(destination),
        "development_freeze_sha256": development_freeze_sha256,
        "permanent": True,
    }
    attempt_claim_path = attempt_claims / f"{attempt_id}.json"
    seed_claim_path = seed_claims / f"{cohort}-seed-{seed}.json"
    allocation_lock = claims / "allocation.lock"
    lock_descriptor = os.open(
        os.fspath(allocation_lock), os.O_RDWR | os.O_CREAT, 0o600
    )
    try:
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        if attempt_claim_path.exists():
            raise FileExistsError(
                f"campaign attempt is already claimed: {attempt_id}"
            )
        if seed_claim_path.exists():
            raise FileExistsError(
                f"campaign cohort/seed is already claimed: {cohort}/{seed}"
            )
        # Seed first prevents a duplicate-seed request from leaving an orphan
        # attempt claim. The allocation lock makes the preceding existence
        # checks and both exclusive creates one compliant-harness transaction.
        seed_claim_sha256 = _exclusive_json(
            seed_claim_path,
            {**claim_base, "claim_kind": "cohort_seed_once"},
        )
        attempt_claim_sha256 = _exclusive_json(
            attempt_claim_path,
            {**claim_base, "claim_kind": "campaign_unique_attempt"},
        )
    finally:
        fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        os.close(lock_descriptor)
    start_payload = {
        "schema": "rrct.v036.run_start.v1",
        "version": "0.36.0.dev2",
        "status": "started_before_rng_construction",
        "attempt_id": attempt_id,
        "cohort": cohort,
        "seed": int(seed),
        "campaign_root": os.fspath(root),
        "output_directory": os.fspath(destination),
        "development_freeze_sha256": development_freeze_sha256,
        "expected_transition_count": V036_D0_CONFIG.total_steps,
        "attempt_claim": os.fspath(attempt_claim_path.relative_to(root)),
        "attempt_claim_sha256": attempt_claim_sha256,
        "seed_claim": os.fspath(seed_claim_path.relative_to(root)),
        "seed_claim_sha256": seed_claim_sha256,
    }
    start_sha256 = _exclusive_json(
        destination / V036_RUN_START_RECEIPT,
        start_payload,
    )
    return root, destination, start_sha256


def run_unified_causal_loop_seed(
    seed: int,
    output: str | Path,
    *,
    cohort: Literal["pilot", "development"] = "pilot",
    allow_development: bool = False,
    attempt_id: str | None = None,
) -> dict[str, Any]:
    """Run one claimed D0 attempt with recoverable, non-overwriting evidence."""

    seed = int(seed)
    if cohort not in {"pilot", "development"}:
        raise ValueError("cohort must be 'pilot' or 'development'")
    allowed = V036_PILOT_SEEDS if cohort == "pilot" else V036_DEVELOPMENT_SEEDS
    if seed not in allowed:
        raise ValueError(f"seed is not reserved for the v0.36 {cohort} cohort")
    development_freeze_sha256: str | None = None
    if cohort == "development":
        if not allow_development:
            raise PermissionError(
                "designated development seeds require the frozen development harness"
            )
        development_freeze_sha256 = _verify_development_freeze()
    validated_attempt = _validate_attempt_id(attempt_id)
    root, destination, start_sha256 = _prepare_campaign_attempt(
        seed=seed,
        cohort=cohort,
        attempt_id=validated_attempt,
        output=output,
        development_freeze_sha256=development_freeze_sha256,
    )
    row_stream = _DurableRowStream(destination / V036_ROWS_ARTIFACT)
    try:
        # All random stream/configuration construction occurs after the durable
        # run-start receipt and permanent campaign claims above.
        boundary_config = _boundary_config(seed)
        runtime_config = _runtime_config(seed)
        rows, raw_summary = _run_trace(
            seed,
            experiment_config=V036_D0_CONFIG,
            boundary_config=boundary_config,
            runtime_config=runtime_config,
            sealed_row_sink=row_stream.append,
        )
        row_stream.close()
        summary = dict(raw_summary)
        summary["campaign_attempt"] = {
            "attempt_id": validated_attempt,
            "campaign_root": os.fspath(root),
            "run_start_receipt": V036_RUN_START_RECEIPT,
            "run_start_receipt_sha256": start_sha256,
            "durably_streamed_rows": row_stream.row_count,
        }
        _write_evidence_artifacts(
            rows,
            summary,
            destination,
            presealed_rows_sha256=row_stream.sha256,
            presealed_row_count=row_stream.row_count,
            additional_hashes={V036_RUN_START_RECEIPT: start_sha256},
        )
        return summary
    except BaseException as exc:
        try:
            row_stream.close()
        except OSError as close_error:
            exc.add_note(f"durable row stream close also failed: {close_error}")
        failure = {
            "schema": "rrct.v036.run_failure.v1",
            "version": "0.36.0.dev2",
            "status": "INTEGRITY_FAIL",
            "scientific_classification": "INTEGRITY_FAIL",
            "operational_status": "interrupted_or_failed",
            "typed_hard_integrity_failure": isinstance(exc, HardIntegrityError),
            "attempt_id": validated_attempt,
            "cohort": cohort,
            "seed": seed,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "durably_streamed_rows": row_stream.row_count,
            "partial_rows_sha256": row_stream.sha256,
        }
        try:
            _exclusive_json(
                destination / "v036_run_failure_receipt.json", failure
            )
        except OSError as receipt_error:
            exc.add_note(f"failure receipt write also failed: {receipt_error}")
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one reserved RRCT v0.36 unified causal-loop seed"
    )
    parser.add_argument("--seed", type=int, default=V036_FIRST_PILOT_SEED)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--attempt-id",
        required=True,
        help="unique immutable identifier for this campaign attempt",
    )
    parser.add_argument(
        "--cohort", choices=("pilot", "development"), default="pilot"
    )
    parser.add_argument(
        "--allow-development",
        action="store_true",
        help="reserved for a subsequently frozen development harness",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_unified_causal_loop_seed(
        args.seed,
        args.output,
        cohort=args.cohort,
        allow_development=args.allow_development,
        attempt_id=args.attempt_id,
    )
    print(json.dumps(_jsonable(result), indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] != "INTEGRITY_FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "V036_D0_CONFIG",
    "V036_DEVELOPMENT_SEEDS",
    "V036_FIRST_PILOT_SEED",
    "V036_PILOT_SEEDS",
    "HardIntegrityError",
    "V036ExperimentConfig",
    "run_unified_causal_loop_seed",
]
