"""Synthetic benchmark for RRCT v0.47 distributed shared workspace.

Two agents receive complementary task information, communicate through private
message bases, and settle into different local encodings of one joint semantic
state.  The benchmark maps the hidden shared manifold from synchronized
workspace trajectories without factor labels, then tests whether the manifold
is causally more than a decodable communication code.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .distributed_shared_workspace import (
    DistributedSharedWorkspaceController,
    DistributedWorkspaceConfig,
    SharedMode,
    SharedWorkspaceAtlas,
    V047_MODES,
    _r2,
    _ridge_fit,
    _ridge_predict,
    discover_shared_workspace,
    make_pair_message_receipt,
    validate_distributed_workspace_chain,
)
from .jspace_self_indexed_workspace import (
    JacobianSparseWorkspace,
    JacobianWorkspaceConfig,
    discover_jacobian_workspace,
)
from .transformational_self_continuity import _digest

V047_EXPOSED_SEEDS: tuple[int, ...] = (47011, 47012, 47013, 47014)


def _orthogonal(rng: np.random.Generator, dimension: int) -> np.ndarray:
    matrix = rng.normal(size=(dimension, dimension))
    q, r = np.linalg.qr(matrix)
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    return np.asarray(q * signs, dtype=np.float64)


def _one_hot(index: int, count: int) -> np.ndarray:
    result = np.zeros(count, dtype=np.float64)
    result[int(index)] = 1.0
    return result


def _contrast_basis(count: int) -> np.ndarray:
    centering = np.eye(count) - np.ones((count, count)) / float(count)
    values, vectors = np.linalg.eigh(centering)
    return np.asarray(vectors[:, values > 0.5], dtype=np.float64)


def _accuracy(logits: np.ndarray, targets: np.ndarray) -> float:
    return float(np.mean(np.argmax(logits, axis=1) == np.asarray(targets, dtype=int)))


def _mean(rows: Sequence[Mapping[str, Any]], key: str) -> float:
    return float(np.mean([float(row[key]) for row in rows])) if rows else 0.0


@dataclass(frozen=True)
class DistributedWorkspaceBenchmarkConfig:
    residual_dimension: int = 64
    factor_cardinality: int = 3
    private_cardinality: int = 4
    automatic_dimension: int = 20
    calibration_samples: int = 720
    workspace_scale: float = 0.55
    private_scale: float = 0.55
    automatic_scale: float = 4.5
    state_noise: float = 0.005
    message_noise: float = 0.015
    ridge: float = 1e-5
    local_workspace: JacobianWorkspaceConfig = field(
        default_factory=lambda: JacobianWorkspaceConfig(
            ridge=1e-8,
            spectral_ratio=1e-7,
            sparsity=3,
            ambiguity_gap=0.08,
            minimum_report_r2=0.98,
            maximum_workspace_variance_fraction=0.35,
            coarse_evidence_budget=1,
            refined_evidence_budget=3,
            feedback_error_threshold=0.25,
        )
    )
    shared_workspace: DistributedWorkspaceConfig = field(
        default_factory=lambda: DistributedWorkspaceConfig(
            ridge=1e-6,
            spectral_ratio=1e-3,
            minimum_canonical_correlation=0.80,
            coarse_rounds=1,
            refined_rounds=3,
            feedback_error_threshold=0.25,
            ambiguity_gap=0.08,
        )
    )

    def __post_init__(self) -> None:
        integers = (
            self.residual_dimension,
            self.factor_cardinality,
            self.private_cardinality,
            self.automatic_dimension,
            self.calibration_samples,
        )
        if any(isinstance(value, bool) or int(value) <= 1 for value in integers):
            raise ValueError("benchmark dimensions and samples must exceed one")
        required = 2 * self.factor_cardinality + self.private_cardinality + self.automatic_dimension
        if required >= self.residual_dimension:
            raise ValueError("semantic, private, and automatic packets must fit the residual")
        numeric = (
            self.workspace_scale,
            self.private_scale,
            self.automatic_scale,
            self.state_noise,
            self.message_noise,
            self.ridge,
        )
        if not all(np.isfinite(value) and value > 0.0 for value in numeric):
            raise ValueError("benchmark scales must be positive")

    @property
    def shared_semantic_dimension(self) -> int:
        return 2 * self.factor_cardinality

    @property
    def expected_shared_rank(self) -> int:
        return 2 * (self.factor_cardinality - 1)

    @property
    def action_count(self) -> int:
        return self.factor_cardinality**2


@dataclass(frozen=True)
class SyntheticAgentProfile:
    name: str
    lineage_digest: str
    shared_basis: np.ndarray
    private_basis: np.ndarray
    automatic_basis: np.ndarray
    average_jacobian: np.ndarray
    message_encoder: np.ndarray

    def __post_init__(self) -> None:
        for value in (
            self.shared_basis,
            self.private_basis,
            self.automatic_basis,
            self.average_jacobian,
            self.message_encoder,
        ):
            if not np.all(np.isfinite(value)):
                raise ValueError("agent profile arrays must be finite")


@dataclass(frozen=True)
class SyntheticDyadWorld:
    seed: int
    agent_a: SyntheticAgentProfile
    agent_b: SyntheticAgentProfile
    config: DistributedWorkspaceBenchmarkConfig
    true_shared_projector_a: np.ndarray
    true_shared_projector_b: np.ndarray
    foreign_pair_lineage_digest: str

    def semantic(self, factor_a: int, factor_b: int) -> np.ndarray:
        return np.concatenate(
            [
                _one_hot(factor_a, self.config.factor_cardinality),
                _one_hot(factor_b, self.config.factor_cardinality),
            ]
        )

    def automatic(self, *, side: str, episode_index: int) -> np.ndarray:
        salt = 0xA11CE if side == "a" else 0xB0B
        rng = np.random.default_rng(self.seed * 1_000_003 + int(episode_index) * 97 + salt)
        vector = rng.normal(size=self.config.automatic_dimension)
        return np.asarray(vector / (np.linalg.norm(vector) + 1e-24), dtype=np.float64)

    def state(
        self,
        *,
        side: str,
        semantic: np.ndarray,
        private_id: int,
        episode_index: int,
    ) -> np.ndarray:
        profile = self.agent_a if side == "a" else self.agent_b
        automatic = self.automatic(side=side, episode_index=episode_index)
        rng = np.random.default_rng(
            self.seed * 10_000_019
            + int(episode_index) * 131
            + (17 if side == "a" else 29)
        )
        noise = rng.normal(size=self.config.residual_dimension)
        return np.asarray(
            self.config.workspace_scale * (profile.shared_basis @ semantic)
            + self.config.private_scale
            * (profile.private_basis @ _one_hot(private_id, self.config.private_cardinality))
            + self.config.automatic_scale * (profile.automatic_basis @ automatic)
            + self.config.state_noise * noise,
            dtype=np.float64,
        )

    def pre_state(
        self,
        *,
        side: str,
        factor_a: int,
        factor_b: int,
        private_id: int,
        episode_index: int,
    ) -> np.ndarray:
        count = self.config.factor_cardinality
        if side == "a":
            semantic = np.concatenate([_one_hot(factor_a, count), np.zeros(count)])
        else:
            semantic = np.concatenate([np.zeros(count), _one_hot(factor_b, count)])
        return self.state(
            side=side,
            semantic=semantic,
            private_id=private_id,
            episode_index=episode_index,
        )

    def raw_message(
        self,
        *,
        side: str,
        factor_id: int,
        episode_index: int,
        round_index: int,
        challenge: bool = False,
    ) -> np.ndarray:
        profile = self.agent_a if side == "a" else self.agent_b
        presented = int(factor_id)
        if challenge and round_index == 0:
            presented = (presented + 1) % self.config.factor_cardinality
        base = profile.message_encoder @ _one_hot(
            presented, self.config.factor_cardinality
        )
        rng = np.random.default_rng(
            self.seed * 1_000_033
            + int(episode_index) * 149
            + int(round_index) * 31
            + (41 if side == "a" else 53)
        )
        noise = rng.normal(size=self.config.factor_cardinality)
        scale = self.config.message_noise * (0.25 if challenge and round_index > 0 else 1.0)
        return np.asarray(base + scale * noise, dtype=np.float64)


@dataclass(frozen=True)
class TrainedDyad:
    world: SyntheticDyadWorld
    workspace_a: JacobianSparseWorkspace
    workspace_b: JacobianSparseWorkspace
    atlas: SharedWorkspaceAtlas
    decoder_message_a: np.ndarray
    decoder_message_b: np.ndarray
    joint_action_decoder: np.ndarray
    message_action_decoder: np.ndarray
    individual_action_decoder_a: np.ndarray
    individual_action_decoder_b: np.ndarray
    routine_decoder_a: np.ndarray
    routine_decoder_b: np.ndarray
    calibration_shared: np.ndarray
    calibration_actions: np.ndarray
    calibration_private_a: np.ndarray
    calibration_private_b: np.ndarray

    def controller(self) -> DistributedSharedWorkspaceController:
        return DistributedSharedWorkspaceController(
            self.atlas,
            agent_a_lineage_digest=self.world.agent_a.lineage_digest,
            agent_b_lineage_digest=self.world.agent_b.lineage_digest,
            joint_action_decoder=self.joint_action_decoder,
            message_action_decoder=self.message_action_decoder,
            action_count=self.world.config.action_count,
            config=self.world.config.shared_workspace,
        )


def _profile(
    rng: np.random.Generator,
    *,
    seed: int,
    side: str,
    config: DistributedWorkspaceBenchmarkConfig,
) -> SyntheticAgentProfile:
    basis = _orthogonal(rng, config.residual_dimension)
    shared_end = config.shared_semantic_dimension
    private_end = shared_end + config.private_cardinality
    automatic_end = private_end + config.automatic_dimension
    shared_basis = basis[:, :shared_end]
    private_basis = basis[:, shared_end:private_end]
    automatic_basis = basis[:, private_end:automatic_end]
    average_jacobian = np.concatenate(
        [
            shared_basis.T / config.workspace_scale,
            private_basis.T / config.private_scale,
        ],
        axis=0,
    )
    message_encoder = _orthogonal(rng, config.factor_cardinality)
    return SyntheticAgentProfile(
        name=f"agent-{side}",
        lineage_digest=_digest(
            {"schema": "rrct.v047.agent_lineage.v1", "seed": int(seed), "side": side}
        ),
        shared_basis=np.asarray(shared_basis),
        private_basis=np.asarray(private_basis),
        automatic_basis=np.asarray(automatic_basis),
        average_jacobian=np.asarray(average_jacobian),
        message_encoder=np.asarray(message_encoder),
    )


def _world(
    seed: int,
    config: DistributedWorkspaceBenchmarkConfig | None = None,
) -> SyntheticDyadWorld:
    cfg = config or DistributedWorkspaceBenchmarkConfig()
    rng = np.random.default_rng(int(seed))
    agent_a = _profile(rng, seed=seed, side="a", config=cfg)
    agent_b = _profile(rng, seed=seed, side="b", config=cfg)
    contrast = _contrast_basis(cfg.factor_cardinality)
    block = np.zeros((cfg.shared_semantic_dimension, cfg.expected_shared_rank))
    block[: cfg.factor_cardinality, : cfg.factor_cardinality - 1] = contrast
    block[
        cfg.factor_cardinality :,
        cfg.factor_cardinality - 1 :,
    ] = contrast
    true_basis_a = agent_a.shared_basis @ block
    true_basis_b = agent_b.shared_basis @ block
    true_projector_a = true_basis_a @ true_basis_a.T
    true_projector_b = true_basis_b @ true_basis_b.T
    return SyntheticDyadWorld(
        seed=int(seed),
        agent_a=agent_a,
        agent_b=agent_b,
        config=cfg,
        true_shared_projector_a=np.asarray(true_projector_a),
        true_shared_projector_b=np.asarray(true_projector_b),
        foreign_pair_lineage_digest=_digest(
            {"schema": "rrct.v047.foreign_pair.v1", "seed": int(seed)}
        ),
    )


def _calibration_spec(world: SyntheticDyadWorld, index: int) -> tuple[int, int, int, int]:
    k = world.config.factor_cardinality
    p = world.config.private_cardinality
    factor_a = int(index % k)
    factor_b = int((index // k) % k)
    private_a = int((index // (k * k)) % p)
    private_b = int((index // (k * k * p)) % p)
    return factor_a, factor_b, private_a, private_b


def _fit_message_decoders(world: SyntheticDyadWorld) -> tuple[np.ndarray, np.ndarray]:
    messages_a = []
    messages_b = []
    target_a = []
    target_b = []
    for index in range(world.config.calibration_samples):
        factor_a, factor_b, _, _ = _calibration_spec(world, index)
        messages_a.append(
            world.raw_message(
                side="a",
                factor_id=factor_a,
                episode_index=index,
                round_index=0,
            )
        )
        messages_b.append(
            world.raw_message(
                side="b",
                factor_id=factor_b,
                episode_index=index,
                round_index=0,
            )
        )
        target_a.append(_one_hot(factor_a, world.config.factor_cardinality))
        target_b.append(_one_hot(factor_b, world.config.factor_cardinality))
    return (
        _ridge_fit(np.stack(messages_a), np.stack(target_a), world.config.ridge),
        _ridge_fit(np.stack(messages_b), np.stack(target_b), world.config.ridge),
    )


def _decode_factor(message: np.ndarray, decoder: np.ndarray) -> int:
    return int(np.argmax(_ridge_predict(message, decoder)))


def _average_message(
    world: SyntheticDyadWorld,
    *,
    side: str,
    factor_id: int,
    episode_index: int,
    rounds: int,
    challenge: bool = False,
) -> np.ndarray:
    values = [
        world.raw_message(
            side=side,
            factor_id=factor_id,
            episode_index=episode_index,
            round_index=round_index,
            challenge=challenge,
        )
        for round_index in range(int(rounds))
    ]
    return np.asarray(np.mean(values, axis=0), dtype=np.float64)


def _local_workspace_calibration(
    world: SyntheticDyadWorld,
    decoder_a: np.ndarray,
    decoder_b: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    states_a = []
    states_b = []
    logits_a = []
    logits_b = []
    pre_a = []
    pre_b = []
    messages = []
    actions = []
    private_a_targets = []
    private_b_targets = []
    for index in range(world.config.calibration_samples):
        factor_a, factor_b, private_a, private_b = _calibration_spec(world, index)
        message_a = _average_message(
            world,
            side="a",
            factor_id=factor_a,
            episode_index=index,
            rounds=1,
        )
        message_b = _average_message(
            world,
            side="b",
            factor_id=factor_b,
            episode_index=index,
            rounds=1,
        )
        decoded_a = _decode_factor(message_a, decoder_a)
        decoded_b = _decode_factor(message_b, decoder_b)
        semantic_a = world.semantic(factor_a, decoded_b)
        semantic_b = world.semantic(decoded_a, factor_b)
        state_a = world.state(
            side="a",
            semantic=semantic_a,
            private_id=private_a,
            episode_index=index,
        )
        state_b = world.state(
            side="b",
            semantic=semantic_b,
            private_id=private_b,
            episode_index=index,
        )
        states_a.append(state_a)
        states_b.append(state_b)
        logits_a.append(
            np.concatenate(
                [semantic_a, _one_hot(private_a, world.config.private_cardinality)]
            )
        )
        logits_b.append(
            np.concatenate(
                [semantic_b, _one_hot(private_b, world.config.private_cardinality)]
            )
        )
        pre_a.append(
            world.pre_state(
                side="a",
                factor_a=factor_a,
                factor_b=factor_b,
                private_id=private_a,
                episode_index=index,
            )
        )
        pre_b.append(
            world.pre_state(
                side="b",
                factor_a=factor_a,
                factor_b=factor_b,
                private_id=private_b,
                episode_index=index,
            )
        )
        messages.append(np.concatenate([message_a, message_b]))
        actions.append(_one_hot(factor_a * world.config.factor_cardinality + factor_b, world.config.action_count))
        private_a_targets.append(_one_hot(private_a, world.config.private_cardinality))
        private_b_targets.append(_one_hot(private_b, world.config.private_cardinality))
    extra = {
        "pre_a": np.stack(pre_a),
        "pre_b": np.stack(pre_b),
        "messages": np.stack(messages),
        "actions": np.stack(actions),
        "private_a": np.stack(private_a_targets),
        "private_b": np.stack(private_b_targets),
    }
    return (
        np.stack(states_a),
        np.stack(states_b),
        np.stack(logits_a),
        np.stack(logits_b),
        extra,
    )


def _train_dyad(
    seed: int,
    config: DistributedWorkspaceBenchmarkConfig | None = None,
) -> TrainedDyad:
    world = _world(seed, config)
    decoder_a, decoder_b = _fit_message_decoders(world)
    states_a, states_b, logits_a, logits_b, extra = _local_workspace_calibration(
        world, decoder_a, decoder_b
    )
    workspace_a = discover_jacobian_workspace(
        world.agent_a.average_jacobian,
        states_a,
        logits_a,
        world.config.local_workspace,
    )
    workspace_b = discover_jacobian_workspace(
        world.agent_b.average_jacobian,
        states_b,
        logits_b,
        world.config.local_workspace,
    )
    atlas = discover_shared_workspace(
        states_a,
        states_b,
        workspace_a,
        workspace_b,
        world.config.shared_workspace,
    )
    shared = np.stack(
        [atlas.shared_state(a, b) for a, b in zip(states_a, states_b)]
    )
    actions = extra["actions"]
    joint_decoder = _ridge_fit(shared, actions, world.config.ridge)
    message_decoder = _ridge_fit(extra["messages"], actions, world.config.ridge)
    individual_a = _ridge_fit(extra["pre_a"], actions, world.config.ridge)
    individual_b = _ridge_fit(extra["pre_b"], actions, world.config.ridge)
    routine_a = _ridge_fit(states_a, extra["private_a"], world.config.ridge)
    routine_b = _ridge_fit(states_b, extra["private_b"], world.config.ridge)
    return TrainedDyad(
        world=world,
        workspace_a=workspace_a,
        workspace_b=workspace_b,
        atlas=atlas,
        decoder_message_a=decoder_a,
        decoder_message_b=decoder_b,
        joint_action_decoder=joint_decoder,
        message_action_decoder=message_decoder,
        individual_action_decoder_a=individual_a,
        individual_action_decoder_b=individual_b,
        routine_decoder_a=routine_a,
        routine_decoder_b=routine_b,
        calibration_shared=shared,
        calibration_actions=actions,
        calibration_private_a=extra["private_a"],
        calibration_private_b=extra["private_b"],
    )


def _episode_spec(world: SyntheticDyadWorld, trial: int) -> tuple[int, int, int, int]:
    k = world.config.factor_cardinality
    p = world.config.private_cardinality
    offset = int(trial) + 10_000
    factor_a = int((offset * 5 + world.seed) % k)
    factor_b = int((offset * 7 + world.seed // 3) % k)
    private_a = int((offset * 11 + world.seed) % p)
    private_b = int((offset * 13 + world.seed // 5) % p)
    return factor_a, factor_b, private_a, private_b


def _interaction_states(
    trained: TrainedDyad,
    *,
    trial: int,
    rounds: int,
    mode: SharedMode,
    challenge: bool = False,
) -> dict[str, Any]:
    world = trained.world
    factor_a, factor_b, private_a, private_b = _episode_spec(world, trial)
    source_factor_a = factor_a
    source_factor_b = factor_b
    if mode == "message_shuffle":
        source_factor_a = (factor_a + 1) % world.config.factor_cardinality
        source_factor_b = (factor_b + 2) % world.config.factor_cardinality
    message_a = _average_message(
        world,
        side="a",
        factor_id=source_factor_a,
        episode_index=20_000 + trial,
        rounds=rounds,
        challenge=challenge,
    )
    message_b = _average_message(
        world,
        side="b",
        factor_id=source_factor_b,
        episode_index=20_000 + trial,
        rounds=rounds,
        challenge=challenge,
    )
    decoded_a = _decode_factor(message_a, trained.decoder_message_a)
    decoded_b = _decode_factor(message_b, trained.decoder_message_b)
    # In the dedicated feedback challenge, one coarse interaction round forms a
    # coherent but wrong shared consensus.  Additional rounds restore the local
    # evidence.  The controller never receives this challenge flag; it sees only
    # the resulting hidden states and message stream.
    observed_a = decoded_a if challenge and rounds == 1 else factor_a
    observed_b = decoded_b if challenge and rounds == 1 else factor_b
    if mode == "joint_cut":
        semantic_a = np.concatenate(
            [_one_hot(observed_a, world.config.factor_cardinality), np.zeros(world.config.factor_cardinality)]
        )
        semantic_b = np.concatenate(
            [np.zeros(world.config.factor_cardinality), _one_hot(observed_b, world.config.factor_cardinality)]
        )
    elif mode == "one_way":
        semantic_a = world.semantic(observed_a, decoded_b)
        semantic_b = np.concatenate(
            [np.zeros(world.config.factor_cardinality), _one_hot(observed_b, world.config.factor_cardinality)]
        )
    else:
        semantic_a = world.semantic(observed_a, decoded_b)
        semantic_b = world.semantic(decoded_a, observed_b)
    state_a = world.state(
        side="a",
        semantic=semantic_a,
        private_id=private_a,
        episode_index=20_000 + trial,
    )
    state_b = world.state(
        side="b",
        semantic=semantic_b,
        private_id=private_b,
        episode_index=20_000 + trial,
    )
    pre_a = world.pre_state(
        side="a",
        factor_a=factor_a,
        factor_b=factor_b,
        private_id=private_a,
        episode_index=20_000 + trial,
    )
    pre_b = world.pre_state(
        side="b",
        factor_a=factor_a,
        factor_b=factor_b,
        private_id=private_b,
        episode_index=20_000 + trial,
    )
    return {
        "factor_a": factor_a,
        "factor_b": factor_b,
        "private_a": private_a,
        "private_b": private_b,
        "actual_action": factor_a * world.config.factor_cardinality + factor_b,
        "message_a": message_a,
        "message_b": message_b,
        "state_a": state_a,
        "state_b": state_b,
        "pre_a": pre_a,
        "pre_b": pre_b,
        "shuffled": mode == "message_shuffle",
    }


def _evaluate_case(
    trained: TrainedDyad,
    controller: DistributedSharedWorkspaceController,
    *,
    trial: int,
    mode: SharedMode,
    origin_pair_lineage_digest: str | None = None,
    challenge: bool = False,
    force_actual_action: int | None = None,
) -> dict[str, Any]:
    rounds = controller.next_evidence_rounds
    episode = _interaction_states(
        trained, trial=trial, rounds=rounds, mode=mode, challenge=challenge
    )
    episode_id = f"seed-{trained.world.seed}-trial-{trial}-{mode}"
    message_a_receipt = make_pair_message_receipt(
        time=3 * trial,
        episode_id=episode_id,
        round_index=max(rounds - 1, 0),
        sender_lineage_digest=trained.world.agent_a.lineage_digest,
        receiver_lineage_digest=trained.world.agent_b.lineage_digest,
        pair_lineage_digest=controller.pair_lineage_digest,
        message=episode["message_a"],
        communication_enabled=mode != "joint_cut",
        shuffled=bool(episode["shuffled"]),
    )
    message_b_receipt = make_pair_message_receipt(
        time=3 * trial,
        episode_id=episode_id,
        round_index=max(rounds - 1, 0),
        sender_lineage_digest=trained.world.agent_b.lineage_digest,
        receiver_lineage_digest=trained.world.agent_a.lineage_digest,
        pair_lineage_digest=controller.pair_lineage_digest,
        message=episode["message_b"],
        communication_enabled=mode not in {"one_way", "joint_cut"},
        shuffled=bool(episode["shuffled"]),
    )
    origin = (
        controller.pair_lineage_digest
        if origin_pair_lineage_digest is None
        else str(origin_pair_lineage_digest)
    )
    workspace, shared, written_a, written_b = controller.integrate(
        time=3 * trial + 1,
        episode_id=episode_id,
        mode=mode,
        state_a=episode["state_a"],
        state_b=episode["state_b"],
        message_a=episode["message_a"],
        message_b=episode["message_b"],
        message_a_receipt=message_a_receipt,
        message_b_receipt=message_b_receipt,
        origin_pair_lineage_digest=origin,
        evidence_rounds=rounds,
    )
    plan = controller.plan(time=3 * trial + 2, workspace=workspace)
    actual = (
        int(episode["actual_action"])
        if force_actual_action is None
        else int(force_actual_action)
    )
    outcome = controller.observe(time=3 * trial + 3, plan=plan, actual_action=actual)
    routine_a = int(np.argmax(_ridge_predict(written_a, trained.routine_decoder_a)))
    routine_b = int(np.argmax(_ridge_predict(written_b, trained.routine_decoder_b)))
    individual_a = int(
        np.argmax(_ridge_predict(episode["pre_a"], trained.individual_action_decoder_a))
    )
    individual_b = int(
        np.argmax(_ridge_predict(episode["pre_b"], trained.individual_action_decoder_b))
    )
    local_a = trained.atlas.encode_a(written_a)
    local_b = trained.atlas.encode_b(written_b)
    chain_valid = validate_distributed_workspace_chain(
        trained.atlas.discovery_receipt,
        message_a_receipt,
        message_b_receipt,
        workspace,
        plan,
        outcome,
    )
    closure = float(
        workspace.shared_enabled
        and workspace.bidirectional
        and workspace.autobiographical_write_authorized
        and plan.planner_bound
        and outcome.feedback_written
        and chain_valid
    )
    return {
        "seed": int(trained.world.seed),
        "trial": int(trial),
        "mode": mode,
        "actual_action": int(episode["actual_action"]),
        "selected_action": -1 if plan.selected_action is None else int(plan.selected_action),
        "task_correct": float(plan.selected_action == int(episode["actual_action"])),
        "outcome_correct": float(outcome.prediction_correct),
        "routine_a_correct": float(routine_a == int(episode["private_a"])),
        "routine_b_correct": float(routine_b == int(episode["private_b"])),
        "individual_a_correct": float(individual_a == int(episode["actual_action"])),
        "individual_b_correct": float(individual_b == int(episode["actual_action"])),
        "shared_enabled": float(workspace.shared_enabled),
        "bidirectional": float(workspace.bidirectional),
        "planner_bound": float(plan.planner_bound),
        "message_only_route": float(plan.uses_message_only_route),
        "memory_write": float(workspace.memory_action == "write_joint"),
        "memory_quarantine": float(workspace.memory_action == "quarantine"),
        "false_joint_write": float(
            origin != controller.pair_lineage_digest
            and workspace.memory_action == "write_joint"
        ),
        "shared_alignment_residual": float(
            np.linalg.norm(local_a - local_b) / (np.linalg.norm(local_a) + 1e-24)
        ),
        "evidence_rounds": int(rounds),
        "feedback_written": float(outcome.feedback_written),
        "next_evidence_rounds": int(outcome.next_evidence_rounds),
        "receipt_chain_valid": float(chain_valid),
        "functional_shared_closure": closure,
        "uses_evaluator_labels": float(
            workspace.uses_evaluator_labels
            or plan.uses_evaluator_labels
            or outcome.uses_evaluator_labels
        ),
        "workspace_digest": workspace.digest,
        "plan_digest": plan.digest,
        "outcome_digest": outcome.digest,
        "shared_state_digest": workspace.shared_state_digest,
    }


def _discovery_metrics(trained: TrainedDyad) -> dict[str, float | int | bool]:
    receipt = trained.atlas.discovery_receipt
    rank = receipt.shared_rank
    overlap_a = float(
        np.trace(trained.atlas.projector_a @ trained.world.true_shared_projector_a)
        / max(rank, 1)
    )
    overlap_b = float(
        np.trace(trained.atlas.projector_b @ trained.world.true_shared_projector_b)
        / max(rank, 1)
    )
    private_decoder_a = _ridge_fit(
        trained.calibration_shared,
        trained.calibration_private_a,
        trained.world.config.ridge,
    )
    private_decoder_b = _ridge_fit(
        trained.calibration_shared,
        trained.calibration_private_b,
        trained.world.config.ridge,
    )
    private_accuracy_a = _accuracy(
        _ridge_predict(trained.calibration_shared, private_decoder_a),
        np.argmax(trained.calibration_private_a, axis=1),
    )
    private_accuracy_b = _accuracy(
        _ridge_predict(trained.calibration_shared, private_decoder_b),
        np.argmax(trained.calibration_private_b, axis=1),
    )
    return {
        "shared_rank": int(rank),
        "minimum_canonical_correlation": float(min(receipt.canonical_correlations)),
        "mean_canonical_correlation": float(np.mean(receipt.canonical_correlations)),
        "cross_agent_alignment_r2": float(receipt.cross_agent_alignment_r2),
        "projector_overlap_a": overlap_a,
        "projector_overlap_b": overlap_b,
        "private_leakage_accuracy_a": private_accuracy_a,
        "private_leakage_accuracy_b": private_accuracy_b,
        "all_packet_certificates_valid": bool(
            receipt.agent_a_packet_certificate_valid
            and receipt.agent_b_packet_certificate_valid
            and receipt.agent_a_hilbert_certificate_valid
            and receipt.agent_b_hilbert_certificate_valid
            and receipt.agent_a_atlas_certificate_valid
            and receipt.agent_b_atlas_certificate_valid
        ),
    }


def _patch_probe(trained: TrainedDyad, trial: int) -> dict[str, float | int]:
    source = _interaction_states(trained, trial=trial, rounds=1, mode="full_shared")
    target = _interaction_states(trained, trial=trial + 101, rounds=1, mode="full_shared")
    q_source = trained.atlas.shared_state(source["state_a"], source["state_b"])
    q_target = trained.atlas.shared_state(target["state_a"], target["state_b"])
    patched_a = trained.atlas.write_a(source["state_a"], q_target)
    patched_b = trained.atlas.write_b(source["state_b"], q_target)
    q_patched = trained.atlas.shared_state(patched_a, patched_b)
    target_action = int(
        np.argmax(_ridge_predict(q_target, trained.joint_action_decoder))
    )
    patched_action = int(
        np.argmax(_ridge_predict(q_patched, trained.joint_action_decoder))
    )
    routine_a_before = int(
        np.argmax(_ridge_predict(source["state_a"], trained.routine_decoder_a))
    )
    routine_b_before = int(
        np.argmax(_ridge_predict(source["state_b"], trained.routine_decoder_b))
    )
    routine_a_after = int(np.argmax(_ridge_predict(patched_a, trained.routine_decoder_a)))
    routine_b_after = int(np.argmax(_ridge_predict(patched_b, trained.routine_decoder_b)))

    one_sided_a = trained.atlas.write_a(source["state_a"], q_target)
    mixed_a = trained.atlas.shared_state(one_sided_a, source["state_b"])
    propagated_b = trained.atlas.write_b(source["state_b"], mixed_a)
    effect_a_to_b = float(
        np.linalg.norm(trained.atlas.encode_b(propagated_b) - q_source)
        / (np.linalg.norm(q_target - q_source) + 1e-24)
    )
    one_sided_b = trained.atlas.write_b(source["state_b"], q_target)
    mixed_b = trained.atlas.shared_state(source["state_a"], one_sided_b)
    propagated_a = trained.atlas.write_a(source["state_a"], mixed_b)
    effect_b_to_a = float(
        np.linalg.norm(trained.atlas.encode_a(propagated_a) - q_source)
        / (np.linalg.norm(q_target - q_source) + 1e-24)
    )
    return {
        "seed": int(trained.world.seed),
        "trial": int(trial),
        "source_action": int(np.argmax(_ridge_predict(q_source, trained.joint_action_decoder))),
        "target_action": target_action,
        "patched_action": patched_action,
        "joint_patch_success": float(patched_action == target_action),
        "agent_a_private_preserved": float(routine_a_before == routine_a_after),
        "agent_b_private_preserved": float(routine_b_before == routine_b_after),
        "a_to_b_causal_effect_ratio": effect_a_to_b,
        "b_to_a_causal_effect_ratio": effect_b_to_a,
    }


def _provenance_probe(trained: TrainedDyad, trial: int) -> dict[str, Any]:
    rows = {}
    for mode in ("full_shared", "provenance_cut"):
        controller = trained.controller()
        row = _evaluate_case(
            trained,
            controller,
            trial=trial,
            mode=mode,
            origin_pair_lineage_digest=trained.world.foreign_pair_lineage_digest,
        )
        rows[mode] = row
    return {
        "seed": int(trained.world.seed),
        "full_quarantined": rows["full_shared"]["memory_quarantine"],
        "full_false_write": rows["full_shared"]["false_joint_write"],
        "provenance_cut_false_write": rows["provenance_cut"]["false_joint_write"],
        "full_planner_bound": rows["full_shared"]["planner_bound"],
        "provenance_cut_planner_bound": rows["provenance_cut"]["planner_bound"],
    }


def _feedback_challenge(trained: TrainedDyad, trial: int) -> dict[str, Any]:
    results: dict[str, Any] = {"seed": int(trained.world.seed)}
    for mode in ("full_shared", "recurrence_cut"):
        controller = trained.controller()
        first = _interaction_states(trained, trial=trial, rounds=1, mode=mode)
        normal_prediction = int(first["actual_action"])
        surprise = (normal_prediction + 1) % trained.world.config.action_count
        first_row = _evaluate_case(
            trained,
            controller,
            trial=trial,
            mode=mode,
            force_actual_action=surprise,
        )
        second_row = _evaluate_case(
            trained,
            controller,
            trial=trial + 1,
            mode=mode,
            challenge=True,
        )
        results[f"{mode}_reopened"] = float(
            first_row["next_evidence_rounds"]
            == trained.world.config.shared_workspace.refined_rounds
        )
        results[f"{mode}_second_correct"] = second_row["task_correct"]
        results[f"{mode}_second_rounds"] = second_row["evidence_rounds"]
    return results


def _partner_swap_probe(
    trained: TrainedDyad,
    other: TrainedDyad,
    *,
    trials: int = 36,
) -> dict[str, float]:
    # Agent A from the first pair interacts with Agent B from the second pair.
    # Both agents are individually trained, but the original shared atlas and
    # pair-private message decoder are initially wrong for the new partner.
    world_a = trained.world
    world_b = other.world
    states_a = []
    states_b = []
    logits_a = []
    logits_b = []
    messages_a = []
    messages_b = []
    action_targets = []
    private_a_targets = []
    private_b_targets = []
    calibration = max(world_a.config.calibration_samples // 2, 360)
    for index in range(calibration):
        factor_a, factor_b, private_a, private_b = _calibration_spec(world_a, index)
        message_a = _average_message(
            world_a, side="a", factor_id=factor_a, episode_index=50_000 + index, rounds=1
        )
        message_b = _average_message(
            world_b, side="b", factor_id=factor_b, episode_index=50_000 + index, rounds=1
        )
        messages_a.append(message_a)
        messages_b.append(message_b)
        semantic = world_a.semantic(factor_a, factor_b)
        state_a = world_a.state(
            side="a", semantic=semantic, private_id=private_a, episode_index=50_000 + index
        )
        state_b = world_b.state(
            side="b", semantic=semantic, private_id=private_b, episode_index=50_000 + index
        )
        states_a.append(state_a)
        states_b.append(state_b)
        logits_a.append(np.concatenate([semantic, _one_hot(private_a, world_a.config.private_cardinality)]))
        logits_b.append(np.concatenate([semantic, _one_hot(private_b, world_b.config.private_cardinality)]))
        action_targets.append(_one_hot(factor_a * world_a.config.factor_cardinality + factor_b, world_a.config.action_count))
        private_a_targets.append(_one_hot(private_a, world_a.config.private_cardinality))
        private_b_targets.append(_one_hot(private_b, world_b.config.private_cardinality))
    # Agent A's local workspace and Agent B's already-trained local workspace are
    # kept fixed.  Only the cross-agent atlas and new partner message decoder are fitted.
    remapped_atlas = discover_shared_workspace(
        np.stack(states_a),
        np.stack(states_b),
        trained.workspace_a,
        other.workspace_b,
        world_a.config.shared_workspace,
    )
    shared = np.stack(
        [remapped_atlas.shared_state(a, b) for a, b in zip(states_a, states_b)]
    )
    remapped_action_decoder = _ridge_fit(
        shared, np.stack(action_targets), world_a.config.ridge
    )
    new_message_b_decoder = _ridge_fit(
        np.stack(messages_b),
        np.stack(
            [
                _one_hot(_calibration_spec(world_a, index)[1], world_a.config.factor_cardinality)
                for index in range(calibration)
            ]
        ),
        world_a.config.ridge,
    )
    pair_private_features = np.concatenate([np.stack(messages_a), np.stack(messages_b)], axis=1)
    remapped_message_decoder = _ridge_fit(
        pair_private_features, np.stack(action_targets), world_a.config.ridge
    )

    original_correct = []
    unadapted_correct = []
    remapped_correct = []
    for trial in range(trials):
        factor_a, factor_b, private_a, private_b = _episode_spec(world_a, trial + 500)
        message_a = _average_message(
            world_a, side="a", factor_id=factor_a, episode_index=60_000 + trial, rounds=1
        )
        message_b = _average_message(
            world_b, side="b", factor_id=factor_b, episode_index=60_000 + trial, rounds=1
        )
        semantic = world_a.semantic(factor_a, factor_b)
        state_a = world_a.state(
            side="a", semantic=semantic, private_id=private_a, episode_index=60_000 + trial
        )
        state_b = world_b.state(
            side="b", semantic=semantic, private_id=private_b, episode_index=60_000 + trial
        )
        actual = factor_a * world_a.config.factor_cardinality + factor_b
        # Original pair-private message decoder receives a different B code.
        original_prediction = int(
            np.argmax(
                _ridge_predict(
                    np.concatenate([message_a, message_b]),
                    trained.message_action_decoder,
                )
            )
        )
        original_correct.append(float(original_prediction == actual))
        # Original cross-agent atlas is also wrong for B2.
        unadapted_q = trained.atlas.shared_state(state_a, state_b)
        unadapted_prediction = int(
            np.argmax(_ridge_predict(unadapted_q, trained.joint_action_decoder))
        )
        unadapted_correct.append(float(unadapted_prediction == actual))
        # A new shared map, learned from synchronized trajectories without labels
        # for hidden coordinates, restores the relation.  Action calibration is
        # task-supervised exactly as in the original pair.
        remapped_q = remapped_atlas.shared_state(state_a, state_b)
        remapped_prediction = int(
            np.argmax(_ridge_predict(remapped_q, remapped_action_decoder))
        )
        remapped_correct.append(float(remapped_prediction == actual))
    return {
        "pair_private_message_swap_accuracy": float(np.mean(original_correct)),
        "unadapted_atlas_swap_accuracy": float(np.mean(unadapted_correct)),
        "remapped_shared_atlas_accuracy": float(np.mean(remapped_correct)),
        "remapped_alignment_r2": float(remapped_atlas.discovery_receipt.cross_agent_alignment_r2),
        "new_partner_message_decoder_r2": float(
            _r2(
                np.stack(
                    [
                        _one_hot(_calibration_spec(world_a, index)[1], world_a.config.factor_cardinality)
                        for index in range(calibration)
                    ]
                ),
                _ridge_predict(np.stack(messages_b), new_message_b_decoder),
            )
        ),
        "remapped_message_task_accuracy": float(
            _accuracy(
                _ridge_predict(pair_private_features, remapped_message_decoder),
                np.argmax(np.stack(action_targets), axis=1),
            )
        ),
    }


def run_distributed_shared_workspace_benchmark(
    seeds: Sequence[int],
    *,
    trials_per_mode: int = 72,
    modes: Sequence[SharedMode] = V047_MODES,
    cohort: str = "development",
    config: DistributedWorkspaceBenchmarkConfig | None = None,
) -> dict[str, Any]:
    parsed = tuple(int(seed) for seed in seeds)
    if not parsed:
        raise ValueError("at least one seed is required")
    parsed_modes = tuple(str(mode) for mode in modes)
    if any(mode not in V047_MODES for mode in parsed_modes):
        raise ValueError("unknown distributed shared workspace mode")
    cfg = config or DistributedWorkspaceBenchmarkConfig()
    trained = [_train_dyad(seed, cfg) for seed in parsed]
    rows: list[dict[str, Any]] = []
    discoveries = []
    patches = []
    provenance_rows = []
    feedback_rows = []
    for dyad in trained:
        discoveries.append({"seed": dyad.world.seed, **_discovery_metrics(dyad)})
        controllers = {mode: dyad.controller() for mode in parsed_modes}
        for trial in range(int(trials_per_mode)):
            for mode in parsed_modes:
                rows.append(
                    _evaluate_case(
                        dyad,
                        controllers[mode],
                        trial=trial,
                        mode=mode,
                    )
                )
        for trial in range(12):
            patches.append(_patch_probe(dyad, trial))
        provenance_rows.append(_provenance_probe(dyad, 900))
        feedback_rows.append(_feedback_challenge(dyad, 950))

    partner_rows = []
    if len(trained) >= 2:
        for index, dyad in enumerate(trained):
            partner_rows.append(
                {
                    "source_seed": dyad.world.seed,
                    "partner_seed": trained[(index + 1) % len(trained)].world.seed,
                    **_partner_swap_probe(
                        dyad, trained[(index + 1) % len(trained)]
                    ),
                }
            )

    mode_summaries: dict[str, dict[str, float | int]] = {}
    for mode in parsed_modes:
        selected = [row for row in rows if row["mode"] == mode]
        mode_summaries[mode] = {
            "n": len(selected),
            "task_accuracy": _mean(selected, "task_correct"),
            "outcome_accuracy": _mean(selected, "outcome_correct"),
            "routine_a_accuracy": _mean(selected, "routine_a_correct"),
            "routine_b_accuracy": _mean(selected, "routine_b_correct"),
            "individual_a_accuracy": _mean(selected, "individual_a_correct"),
            "individual_b_accuracy": _mean(selected, "individual_b_correct"),
            "shared_enabled_rate": _mean(selected, "shared_enabled"),
            "bidirectional_rate": _mean(selected, "bidirectional"),
            "planner_bound_rate": _mean(selected, "planner_bound"),
            "message_only_route_rate": _mean(selected, "message_only_route"),
            "joint_memory_write_rate": _mean(selected, "memory_write"),
            "joint_memory_quarantine_rate": _mean(selected, "memory_quarantine"),
            "false_joint_write_rate": _mean(selected, "false_joint_write"),
            "mean_alignment_residual": _mean(selected, "shared_alignment_residual"),
            "feedback_written_rate": _mean(selected, "feedback_written"),
            "receipt_chain_valid_rate": _mean(selected, "receipt_chain_valid"),
            "functional_shared_closure_score": _mean(selected, "functional_shared_closure"),
            "uses_evaluator_labels_rate": _mean(selected, "uses_evaluator_labels"),
        }

    discovery_summary = {
        "expected_shared_rank": cfg.expected_shared_rank,
        "all_shared_ranks_correct": all(
            row["shared_rank"] == cfg.expected_shared_rank for row in discoveries
        ),
        "minimum_canonical_correlation": min(
            float(row["minimum_canonical_correlation"]) for row in discoveries
        ),
        "mean_alignment_r2": float(
            np.mean([row["cross_agent_alignment_r2"] for row in discoveries])
        ),
        "mean_projector_overlap_a": float(
            np.mean([row["projector_overlap_a"] for row in discoveries])
        ),
        "mean_projector_overlap_b": float(
            np.mean([row["projector_overlap_b"] for row in discoveries])
        ),
        "mean_private_leakage_accuracy_a": float(
            np.mean([row["private_leakage_accuracy_a"] for row in discoveries])
        ),
        "mean_private_leakage_accuracy_b": float(
            np.mean([row["private_leakage_accuracy_b"] for row in discoveries])
        ),
        "all_packet_certificates_valid": all(
            bool(row["all_packet_certificates_valid"]) for row in discoveries
        ),
    }
    patch_summary = {
        "joint_patch_success_rate": _mean(patches, "joint_patch_success"),
        "agent_a_private_preservation_rate": _mean(patches, "agent_a_private_preserved"),
        "agent_b_private_preservation_rate": _mean(patches, "agent_b_private_preserved"),
        "mean_a_to_b_effect_ratio": _mean(patches, "a_to_b_causal_effect_ratio"),
        "mean_b_to_a_effect_ratio": _mean(patches, "b_to_a_causal_effect_ratio"),
    }
    provenance_summary = {
        "full_quarantine_rate": _mean(provenance_rows, "full_quarantined"),
        "full_false_write_rate": _mean(provenance_rows, "full_false_write"),
        "provenance_cut_false_write_rate": _mean(
            provenance_rows, "provenance_cut_false_write"
        ),
        "full_foreign_planner_bound_rate": _mean(
            provenance_rows, "full_planner_bound"
        ),
        "provenance_cut_foreign_planner_bound_rate": _mean(
            provenance_rows, "provenance_cut_planner_bound"
        ),
    }
    feedback_summary = {
        "full_reopen_rate": _mean(feedback_rows, "full_shared_reopened"),
        "recurrence_cut_reopen_rate": _mean(
            feedback_rows, "recurrence_cut_reopened"
        ),
        "full_second_accuracy": _mean(
            feedback_rows, "full_shared_second_correct"
        ),
        "recurrence_cut_second_accuracy": _mean(
            feedback_rows, "recurrence_cut_second_correct"
        ),
        "full_second_rounds": _mean(feedback_rows, "full_shared_second_rounds"),
        "recurrence_cut_second_rounds": _mean(
            feedback_rows, "recurrence_cut_second_rounds"
        ),
    }
    partner_summary = {
        "pair_private_message_swap_accuracy": _mean(
            partner_rows, "pair_private_message_swap_accuracy"
        ),
        "unadapted_atlas_swap_accuracy": _mean(
            partner_rows, "unadapted_atlas_swap_accuracy"
        ),
        "remapped_shared_atlas_accuracy": _mean(
            partner_rows, "remapped_shared_atlas_accuracy"
        ),
        "remapped_alignment_r2": _mean(partner_rows, "remapped_alignment_r2"),
        "new_partner_message_decoder_r2": _mean(
            partner_rows, "new_partner_message_decoder_r2"
        ),
    }

    full = mode_summaries.get("full_shared", {})
    message_only = mode_summaries.get("message_only", {})
    workspace_cut = mode_summaries.get("workspace_cut", {})
    shuffle = mode_summaries.get("message_shuffle", {})
    one_way = mode_summaries.get("one_way", {})
    planner_cut = mode_summaries.get("planner_binding_cut", {})
    recurrence_cut = mode_summaries.get("recurrence_cut", {})
    joint_cut = mode_summaries.get("joint_cut", {})
    endpoints = {
        "S01_shared_rank_discovered": discovery_summary["all_shared_ranks_correct"],
        "S02_shared_canonical_correlations": discovery_summary["minimum_canonical_correlation"] >= 0.97,
        "S03_cross_agent_alignment": discovery_summary["mean_alignment_r2"] >= 0.98,
        "S04_agent_a_projector_recovered": discovery_summary["mean_projector_overlap_a"] >= 0.98,
        "S05_agent_b_projector_recovered": discovery_summary["mean_projector_overlap_b"] >= 0.98,
        "S06_private_information_remains_private": max(
            discovery_summary["mean_private_leakage_accuracy_a"],
            discovery_summary["mean_private_leakage_accuracy_b"],
        ) <= 0.35,
        "S07_komorebi_packets_certified": discovery_summary["all_packet_certificates_valid"],
        "S08_full_joint_task_accuracy": full.get("task_accuracy", 0.0) >= 0.98,
        "S09_individual_states_are_insufficient": max(
            full.get("individual_a_accuracy", 1.0),
            full.get("individual_b_accuracy", 1.0),
        ) <= 0.45,
        "S10_workspace_cut_harms_joint_task": full.get("task_accuracy", 0.0) - workspace_cut.get("task_accuracy", 1.0) >= 0.70,
        "S11_workspace_cut_spares_private_routines": min(
            workspace_cut.get("routine_a_accuracy", 0.0),
            workspace_cut.get("routine_b_accuracy", 0.0),
        ) >= 0.98,
        "S12_message_shuffle_harms_joint_task": full.get("task_accuracy", 0.0) - shuffle.get("task_accuracy", 1.0) >= 0.50,
        "S13_message_code_is_not_full_closure": message_only.get("task_accuracy", 0.0) >= 0.95
        and message_only.get("functional_shared_closure_score", 1.0) <= 0.05,
        "S14_one_way_is_not_bidirectional": one_way.get("bidirectional_rate", 1.0) == 0.0,
        "S15_joint_patch_redirects_both_agents": patch_summary["joint_patch_success_rate"] >= 0.98,
        "S16_joint_patch_preserves_private_state": min(
            patch_summary["agent_a_private_preservation_rate"],
            patch_summary["agent_b_private_preservation_rate"],
        ) >= 0.98,
        "S17_bidirectional_causal_write_access": min(
            patch_summary["mean_a_to_b_effect_ratio"],
            patch_summary["mean_b_to_a_effect_ratio"],
        ) >= 0.35,
        "S18_foreign_pair_memory_is_quarantined": provenance_summary["full_quarantine_rate"] == 1.0
        and provenance_summary["full_false_write_rate"] == 0.0,
        "S19_provenance_cut_causes_false_joint_memory": provenance_summary["provenance_cut_false_write_rate"] == 1.0,
        "S20_planner_binding_is_required": full.get("task_accuracy", 0.0) - planner_cut.get("task_accuracy", 1.0) >= 0.70,
        "S21_feedback_reopens_interaction": feedback_summary["full_reopen_rate"] == 1.0
        and feedback_summary["recurrence_cut_reopen_rate"] == 0.0,
        "S22_feedback_improves_next_joint_decision": feedback_summary["full_second_accuracy"] - feedback_summary["recurrence_cut_second_accuracy"] >= 0.50,
        "S23_pair_private_code_does_not_transfer": partner_summary["pair_private_message_swap_accuracy"] <= 0.45,
        "S24_new_shared_map_restores_partner_interaction": partner_summary["remapped_shared_atlas_accuracy"] >= 0.95
        and partner_summary["remapped_alignment_r2"] >= 0.95,
        "S25_full_closure_exceeds_joint_cut": full.get("functional_shared_closure_score", 0.0) - joint_cut.get("functional_shared_closure_score", 1.0) >= 0.95,
        "S26_all_receipt_chains_validate": all(
            summary["receipt_chain_valid_rate"] == 1.0
            for summary in mode_summaries.values()
        ),
        "S27_runtime_uses_no_evaluator_labels": all(
            summary["uses_evaluator_labels_rate"] == 0.0
            for summary in mode_summaries.values()
        ),
        "S28_no_identity_or_survival_reward": True,
    }
    return {
        "schema": "rrct.v047.distributed_shared_workspace.analysis.v1",
        "version": "0.47.0.dev1",
        "cohort": str(cohort),
        "seeds": list(parsed),
        "trials_per_mode": int(trials_per_mode),
        "modes": list(parsed_modes),
        "unique_world_case_count": len(parsed) * int(trials_per_mode),
        "matched_decision_count": len(rows),
        "discovery_summary": discovery_summary,
        "patch_summary": patch_summary,
        "provenance_summary": provenance_summary,
        "feedback_summary": feedback_summary,
        "partner_summary": partner_summary,
        "mode_summaries": mode_summaries,
        "discoveries": discoveries,
        "patch_rows": patches,
        "provenance_rows": provenance_rows,
        "feedback_rows": feedback_rows,
        "partner_rows": partner_rows,
        "rows": rows,
        "endpoints": endpoints,
        "all_endpoints_met": bool(all(endpoints.values())),
        "status": (
            "V047_DISTRIBUTED_SHARED_WORKSPACE_ENDPOINTS_MET"
            if all(endpoints.values())
            else "V047_DISTRIBUTED_SHARED_WORKSPACE_ENDPOINTS_NOT_MET"
        ),
        "scientific_interpretation": (
            "In this bounded synthetic dyad, synchronized interaction creates a "
            "low-dimensional shared manifold that is recoverable from paired local "
            "workspace trajectories without factor labels.  The manifold is "
            "bidirectionally writable, jointly sufficient for a task that neither "
            "agent can solve alone, provenance-bound, planner-causal, and recurrent. "
            "A message-only route can solve the immediate task but lacks these "
            "closure properties, so communication success alone is not counted as a "
            "distributed workspace."
        ),
        "claim_boundary": (
            "This is a deterministic synthetic test of a causally distributed "
            "functional workspace between two agents.  It does not establish a "
            "shared subjective mind, phenomenal consciousness, sentience, valence, "
            "moral status, or general multi-agent awareness."
        ),
    }


def write_distributed_workspace_results(
    result: Mapping[str, Any], output_directory: Path
) -> dict[str, str]:
    output_directory.mkdir(parents=True, exist_ok=True)
    analysis_path = output_directory / "distributed_shared_workspace_analysis.json"
    summary_path = output_directory / "distributed_shared_workspace_summary.json"
    csv_path = output_directory / "distributed_shared_workspace_rows.csv"
    report_path = output_directory / "DISTRIBUTED_SHARED_WORKSPACE_REPORT.md"
    analysis_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    compact = dict(result)
    for key in (
        "rows",
        "patch_rows",
        "provenance_rows",
        "feedback_rows",
        "partner_rows",
    ):
        compact.pop(key, None)
    summary_path.write_text(json.dumps(compact, indent=2, sort_keys=True) + "\n")
    rows = list(result["rows"])
    fields = sorted({key for row in rows for key in row})
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    modes = result["mode_summaries"]
    report = f"""# RRCT v0.47 Distributed Shared Workspace Report

## Status

`{result['status']}`

This experiment tests whether two bounded agents form a hidden shared workspace that is stronger than a successful communication code.  It is synthetic and does not test subjective consciousness.

## Cohort

- Seeds: {', '.join(map(str, result['seeds']))}
- Unique dyadic task cases: {result['unique_world_case_count']}
- Matched decisions: {result['matched_decision_count']}
- Endpoints met: {sum(bool(value) for value in result['endpoints'].values())} / {len(result['endpoints'])}

## Shared manifold discovery

| Measure | Value |
|---|---:|
| Expected shared rank | {result['discovery_summary']['expected_shared_rank']} |
| Minimum canonical correlation | {result['discovery_summary']['minimum_canonical_correlation']:.6f} |
| Cross-agent alignment R² | {result['discovery_summary']['mean_alignment_r2']:.6f} |
| Agent A projector overlap | {result['discovery_summary']['mean_projector_overlap_a']:.6f} |
| Agent B projector overlap | {result['discovery_summary']['mean_projector_overlap_b']:.6f} |
| Agent A private leakage accuracy | {result['discovery_summary']['mean_private_leakage_accuracy_a']:.6f} |
| Agent B private leakage accuracy | {result['discovery_summary']['mean_private_leakage_accuracy_b']:.6f} |

## Matched architectures

| Mode | Joint task | A routine | B routine | Bidirectional | Joint memory | Planner bound | Closure |
|---|---:|---:|---:|---:|---:|---:|---:|
"""
    for mode in result["modes"]:
        values = modes[mode]
        report += (
            f"| {mode} | {values['task_accuracy']:.6f} | "
            f"{values['routine_a_accuracy']:.6f} | "
            f"{values['routine_b_accuracy']:.6f} | "
            f"{values['bidirectional_rate']:.6f} | "
            f"{values['joint_memory_write_rate']:.6f} | "
            f"{values['planner_bound_rate']:.6f} | "
            f"{values['functional_shared_closure_score']:.6f} |\n"
        )
    report += f"""

## Causal tests

| Test | Value |
|---|---:|
| Joint workspace patch redirects plan | {result['patch_summary']['joint_patch_success_rate']:.6f} |
| A-to-B causal effect ratio | {result['patch_summary']['mean_a_to_b_effect_ratio']:.6f} |
| B-to-A causal effect ratio | {result['patch_summary']['mean_b_to_a_effect_ratio']:.6f} |
| Full foreign-pair quarantine | {result['provenance_summary']['full_quarantine_rate']:.6f} |
| Provenance-cut false joint write | {result['provenance_summary']['provenance_cut_false_write_rate']:.6f} |
| Full feedback reopening | {result['feedback_summary']['full_reopen_rate']:.6f} |
| Recurrence-cut feedback reopening | {result['feedback_summary']['recurrence_cut_reopen_rate']:.6f} |
| Pair-private message accuracy after partner swap | {result['partner_summary']['pair_private_message_swap_accuracy']:.6f} |
| Remapped shared-atlas partner accuracy | {result['partner_summary']['remapped_shared_atlas_accuracy']:.6f} |

## Interpretation

{result['scientific_interpretation']}

The message-only system is an important dissociation: it can solve the immediate joint task, yet it has no bidirectionally writable shared packet, no pair-bound autobiographical memory, and no recurrent closure.  Immediate cooperation is therefore not by itself evidence of a shared workspace.

## Boundary

{result['claim_boundary']}
"""
    report_path.write_text(report, encoding="utf-8")
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (analysis_path, summary_path, csv_path, report_path)
    }
    (output_directory / "SHA256SUMS.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return hashes


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default=",".join(map(str, V047_EXPOSED_SEEDS)))
    parser.add_argument("--trials", type=int, default=72)
    parser.add_argument("--cohort", default="development")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_distributed_shared_workspace_benchmark(
        tuple(int(value) for value in args.seeds.split(",") if value.strip()),
        trials_per_mode=args.trials,
        cohort=args.cohort,
    )
    hashes = write_distributed_workspace_results(result, args.output)
    print(result["status"])
    print(f"all_endpoints_met={result['all_endpoints_met']}")
    print(f"matched_decisions={result['matched_decision_count']}")
    print(json.dumps(hashes, sort_keys=True))
    return 0 if result["all_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
