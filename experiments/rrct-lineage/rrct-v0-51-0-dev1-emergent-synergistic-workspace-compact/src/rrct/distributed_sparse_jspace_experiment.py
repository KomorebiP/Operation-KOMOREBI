"""RRCT v0.48 distributed sparse J-space benchmark.

The experiment combines the local Jacobian workspace tests of v0.46 with the
cross-agent atlas, provenance, planning, and recurrence tests of v0.47.  Each
agent has an independently rotated 64-dimensional residual state and an
overcomplete eight-direction J-lens frame spanning a rank-four workspace.  A
joint state activates four nonnegative frame directions, one from each
opposing concept pair.  The active support changes across episodes, forming a
sparse union of cones rather than one fixed semantic coordinate vector.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .distributed_shared_workspace import (
    DistributedSharedWorkspaceController,
    JointOutcomeReceipt,
    JointPlanningReceipt,
    JointWorkspaceReceipt,
    PairMessageReceipt,
    _ridge_fit,
    _ridge_predict,
    make_pair_message_receipt,
)
from .distributed_sparse_jspace import (
    DistributedJSpaceConfig,
    DistributedSparseJSpace,
    discover_distributed_jspace,
    validate_distributed_jspace_chain,
)
from .jspace_self_indexed_workspace import (
    JacobianSparseWorkspace,
    discover_jacobian_workspace,
)
from .transformational_self_continuity import _digest



def _accuracy(logits: np.ndarray, targets: np.ndarray) -> float:
    values = np.asarray(logits, dtype=np.float64)
    labels = np.asarray(targets, dtype=np.int64)
    if values.ndim != 2 or labels.ndim != 1 or values.shape[0] != labels.size:
        raise ValueError("accuracy arrays have incompatible shapes")
    return float(np.mean(np.argmax(values, axis=1) == labels))


V048_MODES: tuple[str, ...] = (
    "full_shared",
    "message_only",
    "workspace_cut",
    "message_shuffle",
    "one_way",
    "provenance_cut",
    "planner_binding_cut",
    "recurrence_cut",
    "joint_cut",
)


@dataclass(frozen=True)
class DistributedJSpaceBenchmarkConfig:
    residual_dimension: int = 64
    shared_rank: int = 4
    concept_count: int = 8
    private_count: int = 20
    message_dimension: int = 4
    calibration_samples: int = 1024
    workspace_scale: float = 0.18
    private_scale: float = 1.0
    noise_scale: float = 0.0015
    message_noise_scale: float = 0.002
    ridge: float = 1e-6
    jspace: DistributedJSpaceConfig = DistributedJSpaceConfig()

    def __post_init__(self) -> None:
        integers = (
            self.residual_dimension,
            self.shared_rank,
            self.concept_count,
            self.private_count,
            self.message_dimension,
            self.calibration_samples,
        )
        if any(isinstance(value, bool) or int(value) <= 0 for value in integers):
            raise ValueError("benchmark dimensions must be positive")
        if self.concept_count != 2 * self.shared_rank:
            raise ValueError("concept_count must equal twice the shared rank")
        if self.message_dimension < 4:
            raise ValueError("message_dimension must represent four local states")
        if self.shared_rank + self.private_count >= self.residual_dimension:
            raise ValueError("workspace and private packets must leave unused dimensions")
        numeric = (
            self.workspace_scale,
            self.private_scale,
            self.noise_scale,
            self.message_noise_scale,
            self.ridge,
        )
        if not all(np.isfinite(value) and value > 0.0 for value in numeric):
            raise ValueError("benchmark scales must be finite and positive")
        if self.jspace.support_capacity != self.shared_rank:
            raise ValueError("support capacity must equal one signed concept per axis")

    @property
    def action_count(self) -> int:
        return 2 ** self.shared_rank


@dataclass(frozen=True)
class SyntheticDistributedJSpaceWorld:
    seed: int
    workspace_basis_a: np.ndarray
    workspace_basis_b: np.ndarray
    private_basis_a: np.ndarray
    private_basis_b: np.ndarray
    frame_a: np.ndarray
    frame_b: np.ndarray
    semantic_by_token_a: np.ndarray
    semantic_by_token_b: np.ndarray
    average_jacobian_a: np.ndarray
    average_jacobian_b: np.ndarray
    message_code_a: np.ndarray
    message_code_b: np.ndarray
    lineage_a_digest: str
    lineage_b_digest: str
    foreign_pair_lineage_digest: str
    config: DistributedJSpaceBenchmarkConfig

    @property
    def semantic_frame(self) -> np.ndarray:
        frame = np.zeros((self.config.shared_rank, self.config.concept_count))
        for axis in range(self.config.shared_rank):
            frame[axis, 2 * axis] = -1.0
            frame[axis, 2 * axis + 1] = 1.0
        return frame

    @property
    def semantic_to_token_a(self) -> np.ndarray:
        return np.argsort(self.semantic_by_token_a)

    @property
    def semantic_to_token_b(self) -> np.ndarray:
        return np.argsort(self.semantic_by_token_b)

    def bits_from_action(self, action: int) -> tuple[int, ...]:
        if not 0 <= int(action) < self.config.action_count:
            raise ValueError("action is out of range")
        return tuple(
            int((int(action) >> (self.config.shared_rank - 1 - axis)) & 1)
            for axis in range(self.config.shared_rank)
        )

    def action_from_bits(self, bits: Sequence[int]) -> int:
        if len(bits) != self.config.shared_rank:
            raise ValueError("bit vector has the wrong length")
        value = 0
        for bit in bits:
            if int(bit) not in (0, 1):
                raise ValueError("bits must be binary")
            value = (value << 1) | int(bit)
        return int(value)

    def canonical_semantic_support(self, bits: Sequence[int]) -> tuple[int, ...]:
        if len(bits) != self.config.shared_rank:
            raise ValueError("bit vector has the wrong length")
        return tuple(2 * axis + int(bit) for axis, bit in enumerate(bits))

    def canonical_token_support_a(self, bits: Sequence[int]) -> tuple[int, ...]:
        return tuple(
            sorted(
                int(self.semantic_to_token_a[semantic])
                for semantic in self.canonical_semantic_support(bits)
            )
        )

    def local_pair_id(self, bits: Sequence[int], side: str) -> int:
        if side == "a":
            pair = bits[:2]
        elif side == "b":
            pair = bits[2:]
        else:
            raise ValueError("side must be a or b")
        return int(2 * int(pair[0]) + int(pair[1]))

    def pair_bits(self, pair_id: int) -> tuple[int, int]:
        if not 0 <= int(pair_id) < 4:
            raise ValueError("pair id is out of range")
        return int(pair_id) // 2, int(pair_id) % 2

    def message(
        self,
        *,
        side: str,
        pair_id: int,
        episode_index: int,
        rounds: int,
    ) -> np.ndarray:
        if rounds <= 0:
            raise ValueError("rounds must be positive")
        code = self.message_code_a if side == "a" else self.message_code_b
        values = []
        for round_index in range(rounds):
            salt = 11 if side == "a" else 29
            rng = np.random.default_rng(
                self.seed * 1_000_003
                + int(episode_index) * 101
                + round_index * 17
                + salt
            )
            values.append(
                code[:, int(pair_id)]
                + self.config.message_noise_scale
                * rng.normal(size=self.config.message_dimension)
            )
        return np.mean(values, axis=0)

    def encode(
        self,
        *,
        side: str,
        bits: Sequence[int],
        private_id: int,
        noise_seed: int,
        second_bits: Sequence[int] | None = None,
        second_weight: float = 0.0,
    ) -> np.ndarray:
        if not 0 <= int(private_id) < self.config.private_count:
            raise ValueError("private id is out of range")
        if not 0.0 <= float(second_weight) < 1.0:
            raise ValueError("second_weight must lie in [0, 1)")
        frame = self.frame_a if side == "a" else self.frame_b
        private_basis = self.private_basis_a if side == "a" else self.private_basis_b
        semantic_to_token = (
            self.semantic_to_token_a if side == "a" else self.semantic_to_token_b
        )
        coefficients = np.zeros(self.config.concept_count, dtype=np.float64)
        primary_weight = 1.0 - float(second_weight)
        for semantic in self.canonical_semantic_support(bits):
            coefficients[int(semantic_to_token[semantic])] += primary_weight
        if second_bits is not None:
            for semantic in self.canonical_semantic_support(second_bits):
                coefficients[int(semantic_to_token[semantic])] += float(second_weight)
        private = np.zeros(self.config.private_count, dtype=np.float64)
        private[int(private_id)] = 1.0
        rng = np.random.default_rng(int(noise_seed))
        return np.asarray(
            self.config.workspace_scale * (frame @ coefficients)
            + self.config.private_scale * (private_basis @ private)
            + self.config.noise_scale * rng.normal(size=self.config.residual_dimension),
            dtype=np.float64,
        )

    def future_logits(self, *, side: str, bits: Sequence[int]) -> np.ndarray:
        jacobian = self.average_jacobian_a if side == "a" else self.average_jacobian_b
        zero_private = 0
        hidden = self.encode(
            side=side,
            bits=bits,
            private_id=zero_private,
            noise_seed=self.seed + (1 if side == "a" else 2),
        )
        private_basis = self.private_basis_a if side == "a" else self.private_basis_b
        hidden = hidden - self.config.private_scale * private_basis[:, zero_private]
        # The tiny synthetic noise is intentionally removed from the calibration
        # target.  The average Jacobian predicts the signed active-frame logits.
        return np.asarray(jacobian @ hidden, dtype=np.float64)

    def decode_private(self, side: str, state: Any) -> int:
        basis = self.private_basis_a if side == "a" else self.private_basis_b
        return int(np.argmax(basis.T @ np.asarray(state, dtype=np.float64)))

    def query_answers(self, action: int) -> tuple[int, int, int, int]:
        bits = self.bits_from_action(action)
        return (
            int(sum(bits) % 2),
            int(sum(bits)),
            int((bits[0], bits[1]) == (bits[2], bits[3])),
            int(bits[0] ^ bits[3]),
        )


@dataclass(frozen=True)
class TrainedDistributedJSpace:
    world: SyntheticDistributedJSpaceWorld
    workspace_a: JacobianSparseWorkspace
    workspace_b: JacobianSparseWorkspace
    jspace: DistributedSparseJSpace
    message_decoder_a: np.ndarray
    message_decoder_b: np.ndarray
    message_action_decoder: np.ndarray
    joint_action_decoder: np.ndarray
    query_decoders: tuple[np.ndarray, ...]

    def controller(self) -> DistributedSharedWorkspaceController:
        return DistributedSharedWorkspaceController(
            self.jspace.atlas,
            agent_a_lineage_digest=self.world.lineage_a_digest,
            agent_b_lineage_digest=self.world.lineage_b_digest,
            joint_action_decoder=self.joint_action_decoder,
            message_action_decoder=self.message_action_decoder,
            action_count=self.world.config.action_count,
            config=self.world.config.jspace.shared_workspace,
        )


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


def _world(
    seed: int,
    config: DistributedJSpaceBenchmarkConfig | None = None,
) -> SyntheticDistributedJSpaceWorld:
    cfg = config or DistributedJSpaceBenchmarkConfig()
    rng = np.random.default_rng(int(seed))
    basis_a = _orthogonal(rng, cfg.residual_dimension)
    basis_b = _orthogonal(rng, cfg.residual_dimension)
    workspace_basis_a = basis_a[:, : cfg.shared_rank]
    workspace_basis_b = basis_b[:, : cfg.shared_rank]
    private_basis_a = basis_a[
        :, cfg.shared_rank : cfg.shared_rank + cfg.private_count
    ]
    private_basis_b = basis_b[
        :, cfg.shared_rank : cfg.shared_rank + cfg.private_count
    ]
    semantic_frame = np.zeros((cfg.shared_rank, cfg.concept_count))
    for axis in range(cfg.shared_rank):
        semantic_frame[axis, 2 * axis] = -1.0
        semantic_frame[axis, 2 * axis + 1] = 1.0
    semantic_by_token_a = rng.permutation(cfg.concept_count).astype(np.int64)
    semantic_by_token_b = rng.permutation(cfg.concept_count).astype(np.int64)
    frame_a = workspace_basis_a @ semantic_frame[:, semantic_by_token_a]
    frame_b = workspace_basis_b @ semantic_frame[:, semantic_by_token_b]
    average_jacobian_a = frame_a.T / cfg.workspace_scale
    average_jacobian_b = frame_b.T / cfg.workspace_scale
    message_rotation_a = _orthogonal(rng, cfg.message_dimension)
    message_rotation_b = _orthogonal(rng, cfg.message_dimension)
    message_code_a = message_rotation_a[:, :4]
    message_code_b = message_rotation_b[:, :4]
    return SyntheticDistributedJSpaceWorld(
        seed=int(seed),
        workspace_basis_a=workspace_basis_a,
        workspace_basis_b=workspace_basis_b,
        private_basis_a=private_basis_a,
        private_basis_b=private_basis_b,
        frame_a=frame_a,
        frame_b=frame_b,
        semantic_by_token_a=semantic_by_token_a,
        semantic_by_token_b=semantic_by_token_b,
        average_jacobian_a=average_jacobian_a,
        average_jacobian_b=average_jacobian_b,
        message_code_a=message_code_a,
        message_code_b=message_code_b,
        lineage_a_digest=_digest({"seed": int(seed), "agent": "a"}),
        lineage_b_digest=_digest({"seed": int(seed), "agent": "b"}),
        foreign_pair_lineage_digest=_digest({"seed": int(seed), "pair": "foreign"}),
        config=cfg,
    )


def _calibration_spec(
    world: SyntheticDistributedJSpaceWorld, index: int
) -> tuple[tuple[int, ...], int, int]:
    action = int(index % world.config.action_count)
    bits = world.bits_from_action(action)
    private_a = int((index // world.config.action_count) % world.config.private_count)
    private_b = int((7 * index + 3) % world.config.private_count)
    return bits, private_a, private_b


def _episode_spec(
    world: SyntheticDistributedJSpaceWorld, trial: int
) -> tuple[tuple[int, ...], int, int]:
    rng = np.random.default_rng(world.seed * 1009 + int(trial) * 37 + 480)
    action = int(rng.integers(world.config.action_count))
    bits = world.bits_from_action(action)
    private_a = int(rng.integers(world.config.private_count))
    private_b = int(rng.integers(world.config.private_count))
    return bits, private_a, private_b


def _decode_class(message: np.ndarray, decoder: np.ndarray) -> int:
    return int(np.argmax(_ridge_predict(message, decoder)))


def _fit_message_decoders(
    world: SyntheticDistributedJSpaceWorld,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    messages_a = []
    messages_b = []
    targets_a = []
    targets_b = []
    action_targets = []
    for index in range(max(world.config.calibration_samples // 2, 512)):
        bits, _, _ = _calibration_spec(world, index)
        pair_a = world.local_pair_id(bits, "a")
        pair_b = world.local_pair_id(bits, "b")
        message_a = world.message(
            side="a", pair_id=pair_a, episode_index=index, rounds=1
        )
        message_b = world.message(
            side="b", pair_id=pair_b, episode_index=index, rounds=1
        )
        messages_a.append(message_a)
        messages_b.append(message_b)
        targets_a.append(_one_hot(pair_a, 4))
        targets_b.append(_one_hot(pair_b, 4))
        action_targets.append(
            _one_hot(world.action_from_bits(bits), world.config.action_count)
        )
    decoder_a = _ridge_fit(
        np.stack(messages_a), np.stack(targets_a), world.config.ridge
    )
    decoder_b = _ridge_fit(
        np.stack(messages_b), np.stack(targets_b), world.config.ridge
    )
    message_action_decoder = _ridge_fit(
        np.concatenate([np.stack(messages_a), np.stack(messages_b)], axis=1),
        np.stack(action_targets),
        world.config.ridge,
    )
    return decoder_a, decoder_b, message_action_decoder


def _calibration_states(
    world: SyntheticDistributedJSpaceWorld,
    decoder_a: np.ndarray,
    decoder_b: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    states_a = []
    states_b = []
    logits_a = []
    logits_b = []
    actions = []
    for index in range(world.config.calibration_samples):
        bits, private_a, private_b = _calibration_spec(world, index)
        message_a = world.message(
            side="a",
            pair_id=world.local_pair_id(bits, "a"),
            episode_index=10_000 + index,
            rounds=1,
        )
        message_b = world.message(
            side="b",
            pair_id=world.local_pair_id(bits, "b"),
            episode_index=10_000 + index,
            rounds=1,
        )
        pair_a = _decode_class(message_a, decoder_a)
        pair_b = _decode_class(message_b, decoder_b)
        full_bits = world.pair_bits(pair_a) + world.pair_bits(pair_b)
        state_a = world.encode(
            side="a",
            bits=full_bits,
            private_id=private_a,
            noise_seed=world.seed * 100_003 + index,
        )
        state_b = world.encode(
            side="b",
            bits=full_bits,
            private_id=private_b,
            noise_seed=world.seed * 100_019 + index,
        )
        states_a.append(state_a)
        states_b.append(state_b)
        logits_a.append(world.average_jacobian_a @ state_a)
        logits_b.append(world.average_jacobian_b @ state_b)
        actions.append(world.action_from_bits(bits))
    return (
        np.stack(states_a),
        np.stack(states_b),
        np.stack(logits_a),
        np.stack(logits_b),
        np.asarray(actions, dtype=np.int64),
    )


def _train_dyad(
    seed: int,
    config: DistributedJSpaceBenchmarkConfig | None = None,
) -> TrainedDistributedJSpace:
    world = _world(seed, config)
    decoder_a, decoder_b, message_action_decoder = _fit_message_decoders(world)
    states_a, states_b, logits_a, logits_b, actions = _calibration_states(
        world, decoder_a, decoder_b
    )
    workspace_a = discover_jacobian_workspace(
        world.average_jacobian_a,
        states_a,
        logits_a,
        world.config.jspace.local_workspace,
    )
    workspace_b = discover_jacobian_workspace(
        world.average_jacobian_b,
        states_b,
        logits_b,
        world.config.jspace.local_workspace,
    )
    jspace = discover_distributed_jspace(
        agent_a_states=states_a,
        agent_b_states=states_b,
        workspace_a=workspace_a,
        workspace_b=workspace_b,
        config=world.config.jspace,
    )
    shared = np.stack(
        [jspace.atlas.shared_state(a, b) for a, b in zip(states_a, states_b)]
    )
    action_targets = np.stack(
        [_one_hot(int(action), world.config.action_count) for action in actions]
    )
    joint_action_decoder = _ridge_fit(
        shared, action_targets, world.config.ridge
    )
    query_targets: list[list[np.ndarray]] = [[], [], [], []]
    query_counts = (2, 5, 2, 2)
    for action in actions:
        answers = world.query_answers(int(action))
        for index, (answer, count) in enumerate(zip(answers, query_counts)):
            query_targets[index].append(_one_hot(answer, count))
    query_decoders = tuple(
        _ridge_fit(shared, np.stack(targets), world.config.ridge)
        for targets in query_targets
    )
    return TrainedDistributedJSpace(
        world=world,
        workspace_a=workspace_a,
        workspace_b=workspace_b,
        jspace=jspace,
        message_decoder_a=decoder_a,
        message_decoder_b=decoder_b,
        message_action_decoder=message_action_decoder,
        joint_action_decoder=joint_action_decoder,
        query_decoders=query_decoders,
    )


def _interaction_states(
    trained: TrainedDistributedJSpace,
    *,
    trial: int,
    rounds: int,
    mode: str,
    challenge: bool = False,
) -> dict[str, Any]:
    world = trained.world
    bits, private_a, private_b = _episode_spec(world, trial)
    pair_a = world.local_pair_id(bits, "a")
    pair_b = world.local_pair_id(bits, "b")
    message_a = world.message(
        side="a", pair_id=pair_a, episode_index=30_000 + trial, rounds=rounds
    )
    message_b = world.message(
        side="b", pair_id=pair_b, episode_index=30_000 + trial, rounds=rounds
    )
    shuffled = False
    if challenge and rounds <= world.config.jspace.shared_workspace.coarse_rounds:
        # The coarse observation is deliberately misleading.  Reopened
        # interaction averages three fresh rounds and receives the correct code.
        wrong_pair = int((pair_b + 1) % 4)
        message_b = world.message(
            side="b",
            pair_id=wrong_pair,
            episode_index=45_000 + trial,
            rounds=1,
        )
        shuffled = True
    if mode == "message_shuffle":
        other_bits, _, _ = _episode_spec(world, trial + 41)
        message_b = world.message(
            side="b",
            pair_id=world.local_pair_id(other_bits, "b"),
            episode_index=40_000 + trial,
            rounds=rounds,
        )
        shuffled = True
    decoded_a = _decode_class(message_a, trained.message_decoder_a)
    decoded_b = _decode_class(message_b, trained.message_decoder_b)
    full_bits = world.pair_bits(decoded_a) + world.pair_bits(decoded_b)
    state_a = world.encode(
        side="a",
        bits=full_bits,
        private_id=private_a,
        noise_seed=world.seed * 200_003 + trial,
    )
    if mode == "one_way":
        local_b = world.pair_bits(pair_b)
        state_b_bits = (0, 0) + local_b
    else:
        state_b_bits = full_bits
    state_b = world.encode(
        side="b",
        bits=state_b_bits,
        private_id=private_b,
        noise_seed=world.seed * 200_009 + trial,
    )
    return {
        "bits": bits,
        "private_a": private_a,
        "private_b": private_b,
        "message_a": message_a,
        "message_b": message_b,
        "state_a": state_a,
        "state_b": state_b,
        "shuffled": shuffled,
    }


def _query_predictions(
    trained: TrainedDistributedJSpace, shared: np.ndarray
) -> tuple[int, ...]:
    # The shared state is first read through the learned action head and then
    # reused by several deterministic downstream reasoning functions.  This
    # mirrors a workspace variable being consumed by multiple tasks rather than
    # requiring every nonlinear query to be linearly separable in the workspace.
    action = int(np.argmax(_ridge_predict(shared, trained.joint_action_decoder)))
    return trained.world.query_answers(action)


def _evaluate_case(
    trained: TrainedDistributedJSpace,
    controller: DistributedSharedWorkspaceController,
    *,
    trial: int,
    mode: str,
    origin_pair_lineage_digest: str | None = None,
    force_actual_action: int | None = None,
    challenge: bool = False,
) -> dict[str, Any]:
    world = trained.world
    rounds = controller.next_evidence_rounds
    interaction = _interaction_states(
        trained, trial=trial, rounds=rounds, mode=mode, challenge=challenge
    )
    episode_id = f"{world.seed}:{trial}:{mode}"
    pair_lineage = controller.pair_lineage_digest
    origin_pair = pair_lineage if origin_pair_lineage_digest is None else str(origin_pair_lineage_digest)
    message_a_receipt = make_pair_message_receipt(
        time=1,
        episode_id=episode_id,
        round_index=rounds,
        sender_lineage_digest=world.lineage_a_digest,
        receiver_lineage_digest=world.lineage_b_digest,
        pair_lineage_digest=pair_lineage,
        message=interaction["message_a"],
        communication_enabled=mode != "joint_cut",
        shuffled=bool(interaction["shuffled"]),
    )
    message_b_receipt = make_pair_message_receipt(
        time=1,
        episode_id=episode_id,
        round_index=rounds,
        sender_lineage_digest=world.lineage_b_digest,
        receiver_lineage_digest=world.lineage_a_digest,
        pair_lineage_digest=pair_lineage,
        message=interaction["message_b"],
        communication_enabled=mode != "joint_cut",
        shuffled=bool(interaction["shuffled"]),
    )
    joint, shared, written_a, written_b = controller.integrate(
        time=2,
        episode_id=episode_id,
        mode=mode,  # type: ignore[arg-type]
        state_a=interaction["state_a"],
        state_b=interaction["state_b"],
        message_a=interaction["message_a"],
        message_b=interaction["message_b"],
        message_a_receipt=message_a_receipt,
        message_b_receipt=message_b_receipt,
        origin_pair_lineage_digest=origin_pair,
        evidence_rounds=rounds,
    )
    local_mode = (
        "self_model_only" if mode in {"workspace_cut", "joint_cut"} else "full_closure"
    )
    access_a = trained.workspace_a.access(
        time=3,
        case_id=episode_id + ":a",
        hidden=written_a,
        mode=local_mode,
    )
    access_b = trained.workspace_b.access(
        time=3,
        case_id=episode_id + ":b",
        hidden=written_b,
        mode=local_mode,
    )
    distributed_access = trained.jspace.access(
        time=3,
        episode_id=episode_id,
        pair_lineage_digest=pair_lineage,
        state_a=written_a,
        state_b=written_b,
        local_access_a=access_a,
        local_access_b=access_b,
        joint_workspace=joint,
    )
    plan = controller.plan(time=4, workspace=joint)
    actual_action = (
        world.action_from_bits(interaction["bits"])
        if force_actual_action is None
        else int(force_actual_action)
    )
    outcome = controller.observe(
        time=5,
        plan=plan,
        actual_action=actual_action,
    )
    chain_valid = validate_distributed_jspace_chain(
        discovery=trained.jspace.discovery_receipt,
        atlas_receipt=trained.jspace.atlas.discovery_receipt,
        local_access_a=access_a,
        local_access_b=access_b,
        message_a=message_a_receipt,
        message_b=message_b_receipt,
        joint_workspace=joint,
        distributed_access=distributed_access,
        plan=plan,
        outcome=outcome,
    )

    actual_support = set(world.canonical_token_support_a(interaction["bits"]))
    support_a = set(distributed_access.local_support_a)
    support_b = set(distributed_access.local_support_b_mapped)
    support_shared = set(distributed_access.shared_support)
    report_a_correct = float(support_a == actual_support)
    report_b_correct = float(support_b == actual_support)
    shared_support_correct = float(support_shared == actual_support)
    private_a_correct = float(world.decode_private("a", written_a) == interaction["private_a"])
    private_b_correct = float(world.decode_private("b", written_b) == interaction["private_b"])
    if joint.shared_enabled:
        queries = _query_predictions(trained, shared)
        expected_queries = world.query_answers(actual_action)
        flexible_correct = float(queries == expected_queries)
    else:
        flexible_correct = 0.0
    structural_closure = float(
        access_a.workspace_enabled
        and access_b.workspace_enabled
        and distributed_access.bidirectional
        and joint.autobiographical_write_authorized
        and joint.planner_use_authorized
        and outcome.feedback_written
    )
    jspace_closure = float(
        structural_closure == 1.0
        and distributed_access.support_agreement_a >= 0.99
        and distributed_access.support_agreement_b >= 0.99
        and len(distributed_access.shared_support) == world.config.jspace.support_capacity
    )
    return {
        "seed": int(world.seed),
        "trial": int(trial),
        "mode": mode,
        "actual_action": int(actual_action),
        "selected_action": plan.selected_action,
        "task_correct": float(outcome.prediction_correct),
        "report_a_correct": report_a_correct,
        "report_b_correct": report_b_correct,
        "shared_support_correct": shared_support_correct,
        "support_agreement_a": float(distributed_access.support_agreement_a),
        "support_agreement_b": float(distributed_access.support_agreement_b),
        "active_support_size": int(len(distributed_access.shared_support)),
        "flexible_reuse_correct": flexible_correct,
        "private_a_correct": private_a_correct,
        "private_b_correct": private_b_correct,
        "bidirectional": float(joint.bidirectional),
        "planner_bound": float(plan.planner_bound),
        "joint_memory_write": float(joint.autobiographical_write_authorized),
        "memory_quarantine": float(joint.memory_action == "quarantine"),
        "false_joint_write": float(
            origin_pair != pair_lineage and joint.autobiographical_write_authorized
        ),
        "feedback_written": float(outcome.feedback_written),
        "next_evidence_rounds": int(outcome.next_evidence_rounds),
        "evidence_rounds": int(rounds),
        "structural_closure": structural_closure,
        "distributed_jspace_closure": jspace_closure,
        "receipt_chain_valid": float(chain_valid),
        "uses_evaluator_labels": 0.0,
    }


def _swap_probe(
    trained: TrainedDistributedJSpace, trial: int
) -> dict[str, Any]:
    world = trained.world
    interaction = _interaction_states(
        trained, trial=trial, rounds=1, mode="full_shared"
    )
    support, _ = trained.jspace.sparse_content(
        interaction["state_a"], interaction["state_b"]
    )
    source = int(support[trial % len(support)])
    target = int(trained.jspace.opposite_concept_map[source])
    before_action = world.action_from_bits(interaction["bits"])
    semantic_source = int(world.semantic_by_token_a[source])
    axis = semantic_source // 2
    expected_bits = list(interaction["bits"])
    expected_bits[axis] = 1 - expected_bits[axis]
    expected_action = world.action_from_bits(expected_bits)
    patched_a, patched_b, patched_shared = trained.jspace.swap_shared_concept(
        interaction["state_a"], interaction["state_b"], source, target
    )
    support_a, _ = trained.workspace_a.sparse_content(patched_a)
    support_b_raw, _ = trained.workspace_b.sparse_content(patched_b)
    support_b = trained.jspace.map_support_b(support_b_raw)
    predicted_action = int(
        np.argmax(_ridge_predict(patched_shared, trained.joint_action_decoder))
    )
    query_predictions = _query_predictions(trained, patched_shared)
    expected_queries = world.query_answers(expected_action)
    private_a_before = world.decode_private("a", interaction["state_a"])
    private_b_before = world.decode_private("b", interaction["state_b"])
    return {
        "seed": int(world.seed),
        "trial": int(trial),
        "source": source,
        "target": target,
        "before_action": before_action,
        "expected_action": expected_action,
        "predicted_action": predicted_action,
        "report_swap_a": float(target in support_a and source not in support_a),
        "report_swap_b": float(target in support_b and source not in support_b),
        "joint_plan_swap": float(predicted_action == expected_action),
        "flexible_reuse_swap": float(query_predictions == expected_queries),
        "private_a_preserved": float(
            world.decode_private("a", patched_a) == private_a_before
        ),
        "private_b_preserved": float(
            world.decode_private("b", patched_b) == private_b_before
        ),
        "a_effect": float(np.linalg.norm(patched_a - interaction["state_a"])),
        "b_effect": float(np.linalg.norm(patched_b - interaction["state_b"])),
    }


def _ablation_probe(
    trained: TrainedDistributedJSpace, trial: int
) -> dict[str, Any]:
    world = trained.world
    interaction = _interaction_states(
        trained, trial=trial, rounds=1, mode="full_shared"
    )
    actual_action = world.action_from_bits(interaction["bits"])
    intact_support_a, _ = trained.workspace_a.sparse_content(interaction["state_a"])
    intact_support_b_raw, _ = trained.workspace_b.sparse_content(interaction["state_b"])
    intact_support_b = trained.jspace.map_support_b(intact_support_b_raw)
    intact_shared = trained.jspace.atlas.shared_state(
        interaction["state_a"], interaction["state_b"]
    )
    intact_prediction = int(
        np.argmax(_ridge_predict(intact_shared, trained.joint_action_decoder))
    )
    ablated_a, ablated_b = trained.jspace.ablate(
        interaction["state_a"], interaction["state_b"]
    )
    ablated_support_a, _ = trained.workspace_a.sparse_content(ablated_a)
    ablated_support_b_raw, _ = trained.workspace_b.sparse_content(ablated_b)
    ablated_support_b = trained.jspace.map_support_b(ablated_support_b_raw)
    ablated_shared = trained.jspace.atlas.shared_state(ablated_a, ablated_b)
    ablated_prediction = int(
        np.argmax(_ridge_predict(ablated_shared, trained.joint_action_decoder))
    )
    actual_support = set(world.canonical_token_support_a(interaction["bits"]))
    return {
        "seed": int(world.seed),
        "trial": int(trial),
        "intact_report_a": float(set(intact_support_a) == actual_support),
        "ablated_report_a": float(set(ablated_support_a) == actual_support),
        "intact_report_b": float(set(intact_support_b) == actual_support),
        "ablated_report_b": float(set(ablated_support_b) == actual_support),
        "intact_task": float(intact_prediction == actual_action),
        "ablated_task": float(ablated_prediction == actual_action),
        "private_a_preserved": float(
            world.decode_private("a", ablated_a) == interaction["private_a"]
        ),
        "private_b_preserved": float(
            world.decode_private("b", ablated_b) == interaction["private_b"]
        ),
    }


def _capacity_probe(
    trained: TrainedDistributedJSpace, trial: int
) -> dict[str, Any]:
    world = trained.world
    bits, private_a, private_b = _episode_spec(world, trial)
    second_bits = tuple(1 - bit for bit in bits)
    state_a = world.encode(
        side="a",
        bits=bits,
        private_id=private_a,
        noise_seed=world.seed * 300_007 + trial,
        second_bits=second_bits,
        second_weight=0.35,
    )
    state_b = world.encode(
        side="b",
        bits=bits,
        private_id=private_b,
        noise_seed=world.seed * 300_011 + trial,
        second_bits=second_bits,
        second_weight=0.35,
    )
    support, _ = trained.jspace.sparse_content(state_a, state_b)
    primary = set(world.canonical_token_support_a(bits))
    secondary = set(world.canonical_token_support_a(second_bits))
    union = primary | secondary
    return {
        "seed": int(world.seed),
        "trial": int(trial),
        "selected_support_size": len(support),
        "union_support_size": len(union),
        "primary_recall": len(set(support) & primary) / len(primary),
        "dual_union_recall": len(set(support) & union) / len(union),
        "capacity_respected": float(
            len(support) <= world.config.jspace.support_capacity
        ),
    }


def _provenance_probe(
    trained: TrainedDistributedJSpace, trial: int
) -> dict[str, Any]:
    rows = {}
    for mode in ("full_shared", "provenance_cut"):
        controller = trained.controller()
        rows[mode] = _evaluate_case(
            trained,
            controller,
            trial=trial,
            mode=mode,
            origin_pair_lineage_digest=trained.world.foreign_pair_lineage_digest,
        )
    return {
        "seed": int(trained.world.seed),
        "full_quarantined": rows["full_shared"]["memory_quarantine"],
        "full_false_write": rows["full_shared"]["false_joint_write"],
        "provenance_cut_false_write": rows["provenance_cut"]["false_joint_write"],
        "full_planner_bound": rows["full_shared"]["planner_bound"],
        "provenance_cut_planner_bound": rows["provenance_cut"]["planner_bound"],
    }


def _feedback_challenge(
    trained: TrainedDistributedJSpace, trial: int
) -> dict[str, Any]:
    result: dict[str, Any] = {"seed": int(trained.world.seed)}
    for mode in ("full_shared", "recurrence_cut"):
        controller = trained.controller()
        bits, _, _ = _episode_spec(trained.world, trial)
        correct = trained.world.action_from_bits(bits)
        surprise = (correct + 1) % trained.world.config.action_count
        first = _evaluate_case(
            trained,
            controller,
            trial=trial,
            mode=mode,
            force_actual_action=surprise,
        )
        second = _evaluate_case(
            trained,
            controller,
            trial=trial + 1,
            mode=mode,
            challenge=True,
        )
        result[f"{mode}_reopened"] = float(
            first["next_evidence_rounds"]
            == trained.world.config.jspace.shared_workspace.refined_rounds
        )
        result[f"{mode}_second_correct"] = second["task_correct"]
        result[f"{mode}_second_rounds"] = second["evidence_rounds"]
    return result


def _partner_swap_probe(
    trained: TrainedDistributedJSpace,
    other: TrainedDistributedJSpace,
    *,
    samples: int = 512,
    trials: int = 48,
) -> dict[str, float]:
    """Re-pair A1 with B2 and separate old-code failure from remapping."""

    world_a = trained.world
    world_b = other.world
    messages_a = []
    messages_b = []
    pair_targets_a = []
    pair_targets_b = []
    action_targets = []
    specs = []
    for index in range(samples):
        bits, private_a, private_b = _calibration_spec(world_a, 70_000 + index)
        pair_a = world_a.local_pair_id(bits, "a")
        pair_b = world_a.local_pair_id(bits, "b")
        message_a = world_a.message(
            side="a", pair_id=pair_a, episode_index=70_000 + index, rounds=1
        )
        message_b = world_b.message(
            side="b", pair_id=pair_b, episode_index=70_000 + index, rounds=1
        )
        messages_a.append(message_a)
        messages_b.append(message_b)
        pair_targets_a.append(_one_hot(pair_a, 4))
        pair_targets_b.append(_one_hot(pair_b, 4))
        action_targets.append(
            _one_hot(world_a.action_from_bits(bits), world_a.config.action_count)
        )
        specs.append((bits, private_a, private_b))

    new_decoder_a = _ridge_fit(
        np.stack(messages_a), np.stack(pair_targets_a), world_a.config.ridge
    )
    new_decoder_b = _ridge_fit(
        np.stack(messages_b), np.stack(pair_targets_b), world_a.config.ridge
    )
    states_a = []
    states_b = []
    for index, ((bits, private_a, private_b), message_a, message_b) in enumerate(
        zip(specs, messages_a, messages_b)
    ):
        decoded_a = _decode_class(message_a, new_decoder_a)
        decoded_b = _decode_class(message_b, new_decoder_b)
        full_bits = world_a.pair_bits(decoded_a) + world_a.pair_bits(decoded_b)
        states_a.append(
            world_a.encode(
                side="a",
                bits=full_bits,
                private_id=private_a,
                noise_seed=world_a.seed * 400_009 + index,
            )
        )
        states_b.append(
            world_b.encode(
                side="b",
                bits=full_bits,
                private_id=private_b,
                noise_seed=world_b.seed * 400_013 + index,
            )
        )

    remapped = discover_distributed_jspace(
        agent_a_states=np.stack(states_a),
        agent_b_states=np.stack(states_b),
        workspace_a=trained.workspace_a,
        workspace_b=other.workspace_b,
        config=world_a.config.jspace,
    )
    remapped_shared = np.stack(
        [remapped.atlas.shared_state(a, b) for a, b in zip(states_a, states_b)]
    )
    remapped_action_decoder = _ridge_fit(
        remapped_shared, np.stack(action_targets), world_a.config.ridge
    )

    old_code_correct = []
    remapped_correct = []
    support_agreement = []
    for trial in range(trials):
        bits, private_a, private_b = _episode_spec(world_a, 80_000 + trial)
        pair_a = world_a.local_pair_id(bits, "a")
        pair_b = world_a.local_pair_id(bits, "b")
        message_a = world_a.message(
            side="a", pair_id=pair_a, episode_index=80_000 + trial, rounds=1
        )
        message_b = world_b.message(
            side="b", pair_id=pair_b, episode_index=80_000 + trial, rounds=1
        )
        actual = world_a.action_from_bits(bits)

        # The original pair-specific decoders interpret the new partner's code
        # with the old convention.  Each local state therefore combines its own
        # true half with an incorrectly decoded partner half.
        old_decoded_b = _decode_class(message_b, trained.message_decoder_b)
        old_decoded_a = _decode_class(message_a, other.message_decoder_a)
        old_bits_a = world_a.pair_bits(pair_a) + world_a.pair_bits(old_decoded_b)
        old_bits_b = world_b.pair_bits(old_decoded_a) + world_b.pair_bits(pair_b)
        old_state_a = world_a.encode(
            side="a",
            bits=old_bits_a,
            private_id=private_a,
            noise_seed=world_a.seed * 500_003 + trial,
        )
        old_state_b = world_b.encode(
            side="b",
            bits=old_bits_b,
            private_id=private_b,
            noise_seed=world_b.seed * 500_007 + trial,
        )
        old_shared = trained.jspace.atlas.shared_state(old_state_a, old_state_b)
        old_prediction = int(
            np.argmax(_ridge_predict(old_shared, trained.joint_action_decoder))
        )

        new_decoded_a = _decode_class(message_a, new_decoder_a)
        new_decoded_b = _decode_class(message_b, new_decoder_b)
        full_bits = world_a.pair_bits(new_decoded_a) + world_a.pair_bits(new_decoded_b)
        new_state_a = world_a.encode(
            side="a",
            bits=full_bits,
            private_id=private_a,
            noise_seed=world_a.seed * 500_011 + trial,
        )
        new_state_b = world_b.encode(
            side="b",
            bits=full_bits,
            private_id=private_b,
            noise_seed=world_b.seed * 500_013 + trial,
        )
        new_shared = remapped.atlas.shared_state(new_state_a, new_state_b)
        new_prediction = int(
            np.argmax(_ridge_predict(new_shared, remapped_action_decoder))
        )
        support_a, _ = trained.workspace_a.sparse_content(new_state_a)
        support_b_raw, _ = other.workspace_b.sparse_content(new_state_b)
        support_b = remapped.map_support_b(support_b_raw)
        old_code_correct.append(float(old_prediction == actual))
        remapped_correct.append(float(new_prediction == actual))
        support_agreement.append(float(set(support_a) == set(support_b)))

    return {
        "unadapted_partner_accuracy": float(np.mean(old_code_correct)),
        "remapped_partner_accuracy": float(np.mean(remapped_correct)),
        "remapped_alignment_r2": float(
            remapped.discovery_receipt.cross_agent_alignment_r2
        ),
        "remapped_frame_cosine": float(
            remapped.discovery_receipt.minimum_frame_alignment_cosine
        ),
        "remapped_support_agreement": float(np.mean(support_agreement)),
    }


def _mean(rows: Sequence[Mapping[str, Any]], key: str) -> float:
    return float(np.mean([float(row[key]) for row in rows])) if rows else 0.0


def run_distributed_sparse_jspace_benchmark(
    seeds: Sequence[int],
    *,
    trials_per_seed: int = 64,
    modes: Sequence[str] = V048_MODES,
    config: DistributedJSpaceBenchmarkConfig | None = None,
    cohort: str = "development",
) -> dict[str, Any]:
    parsed = tuple(int(seed) for seed in seeds)
    if not parsed:
        raise ValueError("at least one seed is required")
    if trials_per_seed <= 0:
        raise ValueError("trials_per_seed must be positive")
    parsed_modes = tuple(str(mode) for mode in modes)
    if any(mode not in V048_MODES for mode in parsed_modes):
        raise ValueError("unknown benchmark mode")

    rows: list[dict[str, Any]] = []
    discoveries: list[dict[str, Any]] = []
    swaps: list[dict[str, Any]] = []
    ablations: list[dict[str, Any]] = []
    capacities: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    feedback: list[dict[str, Any]] = []
    trained_dyads: list[TrainedDistributedJSpace] = []

    for seed in parsed:
        trained = _train_dyad(seed, config)
        trained_dyads.append(trained)
        receipt = trained.jspace.discovery_receipt
        world = trained.world
        states_a, states_b, _, _, actions = _calibration_states(
            world, trained.message_decoder_a, trained.message_decoder_b
        )
        shared = np.stack(
            [trained.jspace.atlas.shared_state(a, b) for a, b in zip(states_a, states_b)]
        )
        support_accuracy_a = []
        support_accuracy_b = []
        for state_a, state_b, action in zip(states_a, states_b, actions):
            bits = world.bits_from_action(int(action))
            actual = set(world.canonical_token_support_a(bits))
            support_a, _ = trained.workspace_a.sparse_content(state_a)
            support_b_raw, _ = trained.workspace_b.sparse_content(state_b)
            support_b = trained.jspace.map_support_b(support_b_raw)
            support_accuracy_a.append(float(set(support_a) == actual))
            support_accuracy_b.append(float(set(support_b) == actual))
        discoveries.append(
            {
                "seed": int(seed),
                "local_rank_a": int(trained.workspace_a.discovery_receipt.workspace_rank),
                "local_rank_b": int(trained.workspace_b.discovery_receipt.workspace_rank),
                "local_report_r2_a": float(
                    trained.workspace_a.discovery_receipt.calibration_report_r2
                ),
                "local_report_r2_b": float(
                    trained.workspace_b.discovery_receipt.calibration_report_r2
                ),
                "local_variance_fraction_a": float(
                    trained.workspace_a.discovery_receipt.workspace_activation_variance_fraction
                ),
                "local_variance_fraction_b": float(
                    trained.workspace_b.discovery_receipt.workspace_activation_variance_fraction
                ),
                "shared_rank": int(receipt.shared_rank),
                "minimum_canonical_correlation": float(
                    receipt.minimum_canonical_correlation
                ),
                "alignment_r2": float(receipt.cross_agent_alignment_r2),
                "minimum_frame_cosine": float(
                    receipt.minimum_frame_alignment_cosine
                ),
                "mean_frame_cosine": float(receipt.mean_frame_alignment_cosine),
                "support_agreement": float(receipt.support_exact_agreement_rate),
                "dynamic_support_count": int(receipt.dynamic_support_count),
                "support_accuracy_a": float(np.mean(support_accuracy_a)),
                "support_accuracy_b": float(np.mean(support_accuracy_b)),
                "action_decoder_accuracy": float(
                    _accuracy(
                        _ridge_predict(shared, trained.joint_action_decoder),
                        actions,
                    )
                ),
                "packet_certificates_valid": bool(receipt.packet_certificates_valid),
            }
        )
        for mode in parsed_modes:
            controller = trained.controller()
            for trial in range(trials_per_seed):
                rows.append(
                    _evaluate_case(
                        trained,
                        controller,
                        trial=trial,
                        mode=mode,
                    )
                )
        for trial in range(min(32, trials_per_seed)):
            swaps.append(_swap_probe(trained, trial))
            ablations.append(_ablation_probe(trained, trial))
            capacities.append(_capacity_probe(trained, trial))
        provenance.append(_provenance_probe(trained, 7))
        feedback.append(_feedback_challenge(trained, 11))

    partner_rows = []
    if len(trained_dyads) >= 2:
        for index, trained in enumerate(trained_dyads):
            other = trained_dyads[(index + 1) % len(trained_dyads)]
            partner_rows.append(_partner_swap_probe(trained, other))

    mode_summaries: dict[str, dict[str, Any]] = {}
    for mode in parsed_modes:
        selected = [row for row in rows if row["mode"] == mode]
        mode_summaries[mode] = {
            "n": len(selected),
            "task_accuracy": _mean(selected, "task_correct"),
            "report_a_accuracy": _mean(selected, "report_a_correct"),
            "report_b_accuracy": _mean(selected, "report_b_correct"),
            "shared_support_accuracy": _mean(selected, "shared_support_correct"),
            "support_agreement_a": _mean(selected, "support_agreement_a"),
            "support_agreement_b": _mean(selected, "support_agreement_b"),
            "mean_active_support_size": _mean(selected, "active_support_size"),
            "flexible_reuse_accuracy": _mean(selected, "flexible_reuse_correct"),
            "private_a_accuracy": _mean(selected, "private_a_correct"),
            "private_b_accuracy": _mean(selected, "private_b_correct"),
            "bidirectional_rate": _mean(selected, "bidirectional"),
            "planner_bound_rate": _mean(selected, "planner_bound"),
            "joint_memory_write_rate": _mean(selected, "joint_memory_write"),
            "feedback_written_rate": _mean(selected, "feedback_written"),
            "structural_closure_score": _mean(selected, "structural_closure"),
            "distributed_jspace_closure_score": _mean(
                selected, "distributed_jspace_closure"
            ),
            "receipt_chain_valid_rate": _mean(selected, "receipt_chain_valid"),
            "uses_evaluator_labels_rate": _mean(selected, "uses_evaluator_labels"),
        }

    discovery_summary = {
        "seed_count": len(discoveries),
        "mean_local_report_r2_a": _mean(discoveries, "local_report_r2_a"),
        "mean_local_report_r2_b": _mean(discoveries, "local_report_r2_b"),
        "mean_local_variance_fraction_a": _mean(
            discoveries, "local_variance_fraction_a"
        ),
        "mean_local_variance_fraction_b": _mean(
            discoveries, "local_variance_fraction_b"
        ),
        "minimum_canonical_correlation": min(
            row["minimum_canonical_correlation"] for row in discoveries
        ),
        "mean_alignment_r2": _mean(discoveries, "alignment_r2"),
        "minimum_frame_cosine": min(
            row["minimum_frame_cosine"] for row in discoveries
        ),
        "mean_frame_cosine": _mean(discoveries, "mean_frame_cosine"),
        "mean_support_agreement": _mean(discoveries, "support_agreement"),
        "minimum_dynamic_support_count": min(
            int(row["dynamic_support_count"]) for row in discoveries
        ),
        "mean_support_accuracy_a": _mean(discoveries, "support_accuracy_a"),
        "mean_support_accuracy_b": _mean(discoveries, "support_accuracy_b"),
        "mean_action_decoder_accuracy": _mean(
            discoveries, "action_decoder_accuracy"
        ),
        "all_packet_certificates_valid": all(
            bool(row["packet_certificates_valid"]) for row in discoveries
        ),
        "local_ranks_a": [int(row["local_rank_a"]) for row in discoveries],
        "local_ranks_b": [int(row["local_rank_b"]) for row in discoveries],
        "shared_ranks": [int(row["shared_rank"]) for row in discoveries],
    }
    swap_summary = {
        "n": len(swaps),
        "report_swap_a_rate": _mean(swaps, "report_swap_a"),
        "report_swap_b_rate": _mean(swaps, "report_swap_b"),
        "joint_plan_swap_rate": _mean(swaps, "joint_plan_swap"),
        "flexible_reuse_swap_rate": _mean(swaps, "flexible_reuse_swap"),
        "private_a_preservation_rate": _mean(swaps, "private_a_preserved"),
        "private_b_preservation_rate": _mean(swaps, "private_b_preserved"),
        "mean_a_effect": _mean(swaps, "a_effect"),
        "mean_b_effect": _mean(swaps, "b_effect"),
    }
    ablation_summary = {
        "n": len(ablations),
        "intact_report_a": _mean(ablations, "intact_report_a"),
        "ablated_report_a": _mean(ablations, "ablated_report_a"),
        "intact_report_b": _mean(ablations, "intact_report_b"),
        "ablated_report_b": _mean(ablations, "ablated_report_b"),
        "intact_task": _mean(ablations, "intact_task"),
        "ablated_task": _mean(ablations, "ablated_task"),
        "private_a_preservation_rate": _mean(
            ablations, "private_a_preserved"
        ),
        "private_b_preservation_rate": _mean(
            ablations, "private_b_preserved"
        ),
    }
    capacity_summary = {
        "n": len(capacities),
        "mean_selected_support_size": _mean(
            capacities, "selected_support_size"
        ),
        "mean_union_support_size": _mean(capacities, "union_support_size"),
        "mean_primary_recall": _mean(capacities, "primary_recall"),
        "mean_dual_union_recall": _mean(capacities, "dual_union_recall"),
        "capacity_respected_rate": _mean(capacities, "capacity_respected"),
    }
    provenance_summary = {
        "n": len(provenance),
        "full_quarantine_rate": _mean(provenance, "full_quarantined"),
        "full_false_write_rate": _mean(provenance, "full_false_write"),
        "provenance_cut_false_write_rate": _mean(
            provenance, "provenance_cut_false_write"
        ),
        "full_planner_bound_rate": _mean(provenance, "full_planner_bound"),
        "provenance_cut_planner_bound_rate": _mean(
            provenance, "provenance_cut_planner_bound"
        ),
    }
    feedback_summary = {
        "n": len(feedback),
        "full_reopen_rate": _mean(feedback, "full_shared_reopened"),
        "recurrence_cut_reopen_rate": _mean(
            feedback, "recurrence_cut_reopened"
        ),
        "full_second_accuracy": _mean(
            feedback, "full_shared_second_correct"
        ),
        "recurrence_cut_second_accuracy": _mean(
            feedback, "recurrence_cut_second_correct"
        ),
        "full_second_rounds": _mean(feedback, "full_shared_second_rounds"),
        "recurrence_cut_second_rounds": _mean(
            feedback, "recurrence_cut_second_rounds"
        ),
    }
    partner_summary = {
        "n": len(partner_rows),
        "mean_unadapted_partner_accuracy": _mean(
            partner_rows, "unadapted_partner_accuracy"
        ),
        "mean_remapped_partner_accuracy": _mean(
            partner_rows, "remapped_partner_accuracy"
        ),
        "mean_remapped_alignment_r2": _mean(
            partner_rows, "remapped_alignment_r2"
        ),
        "minimum_remapped_frame_cosine": (
            min(row["remapped_frame_cosine"] for row in partner_rows)
            if partner_rows
            else 0.0
        ),
        "mean_remapped_support_agreement": _mean(
            partner_rows, "remapped_support_agreement"
        ),
    }

    full = mode_summaries.get("full_shared", {})
    message_only = mode_summaries.get("message_only", {})
    workspace_cut = mode_summaries.get("workspace_cut", {})
    shuffled = mode_summaries.get("message_shuffle", {})
    one_way = mode_summaries.get("one_way", {})
    planner_cut = mode_summaries.get("planner_binding_cut", {})
    recurrence_cut = mode_summaries.get("recurrence_cut", {})
    joint_cut = mode_summaries.get("joint_cut", {})

    endpoints = {
        "S01_local_jacobian_workspaces_recovered": (
            discovery_summary["mean_local_report_r2_a"] >= 0.98
            and discovery_summary["mean_local_report_r2_b"] >= 0.98
            and set(discovery_summary["local_ranks_a"]) == {4}
            and set(discovery_summary["local_ranks_b"]) == {4}
        ),
        "S02_local_workspaces_are_selective": (
            discovery_summary["mean_local_variance_fraction_a"] <= 0.15
            and discovery_summary["mean_local_variance_fraction_b"] <= 0.15
        ),
        "S03_shared_rank_and_alignment_recovered": (
            set(discovery_summary["shared_ranks"]) == {4}
            and discovery_summary["minimum_canonical_correlation"] >= 0.99
            and discovery_summary["mean_alignment_r2"] >= 0.99
        ),
        "S04_sparse_frames_align_cross_agent": (
            discovery_summary["minimum_frame_cosine"] >= 0.98
            and discovery_summary["mean_support_agreement"] >= 0.98
        ),
        "S05_dynamic_union_of_cones_observed": (
            discovery_summary["minimum_dynamic_support_count"] >= 16
        ),
        "S06_komorebi_packets_certified": discovery_summary[
            "all_packet_certificates_valid"
        ],
        "S07_full_shared_reports_are_accurate": (
            full.get("report_a_accuracy", 0.0) >= 0.98
            and full.get("report_b_accuracy", 0.0) >= 0.98
            and full.get("shared_support_accuracy", 0.0) >= 0.98
        ),
        "S08_full_shared_flexible_reuse": full.get(
            "flexible_reuse_accuracy", 0.0
        ) >= 0.98,
        "S09_directed_modulation_changes_both_reports": (
            swap_summary["report_swap_a_rate"] >= 0.98
            and swap_summary["report_swap_b_rate"] >= 0.98
        ),
        "S10_directed_modulation_changes_plan": swap_summary[
            "joint_plan_swap_rate"
        ] >= 0.98,
        "S11_directed_modulation_changes_reasoning": swap_summary[
            "flexible_reuse_swap_rate"
        ] >= 0.98,
        "S12_directed_modulation_preserves_private_processing": (
            swap_summary["private_a_preservation_rate"] >= 0.98
            and swap_summary["private_b_preservation_rate"] >= 0.98
        ),
        "S13_ablation_harms_report_and_flexible_task": (
            ablation_summary["intact_report_a"]
            - ablation_summary["ablated_report_a"]
            >= 0.60
            and ablation_summary["intact_report_b"]
            - ablation_summary["ablated_report_b"]
            >= 0.60
            and ablation_summary["intact_task"]
            - ablation_summary["ablated_task"]
            >= 0.60
        ),
        "S14_ablation_preserves_private_processing": (
            ablation_summary["private_a_preservation_rate"] >= 0.98
            and ablation_summary["private_b_preservation_rate"] >= 0.98
        ),
        "S15_capacity_is_sparse_and_limited": (
            capacity_summary["capacity_respected_rate"] == 1.0
            and capacity_summary["mean_selected_support_size"] <= 4.0
            and capacity_summary["mean_dual_union_recall"] <= 0.60
        ),
        "S16_message_only_is_not_distributed_jspace": (
            message_only.get("task_accuracy", 0.0) >= 0.98
            and message_only.get("distributed_jspace_closure_score", 1.0)
            == 0.0
        ),
        "S17_one_way_is_not_distributed_jspace": (
            one_way.get("task_accuracy", 0.0) >= 0.98
            and one_way.get("distributed_jspace_closure_score", 1.0) == 0.0
        ),
        "S18_wrong_content_can_preserve_structure": (
            shuffled.get("structural_closure_score", 0.0) >= 0.98
            and shuffled.get("task_accuracy", 1.0) <= 0.40
        ),
        "S19_planner_binding_is_required": (
            full.get("task_accuracy", 0.0)
            - planner_cut.get("task_accuracy", 1.0)
            >= 0.70
        ),
        "S20_recurrence_is_required_for_next_interaction": (
            feedback_summary["full_reopen_rate"] == 1.0
            and feedback_summary["recurrence_cut_reopen_rate"] == 0.0
            and feedback_summary["full_second_accuracy"]
            - feedback_summary["recurrence_cut_second_accuracy"]
            >= 0.50
        ),
        "S21_pair_provenance_quarantines_foreign_content": (
            provenance_summary["full_quarantine_rate"] == 1.0
            and provenance_summary["full_false_write_rate"] == 0.0
            and provenance_summary["provenance_cut_false_write_rate"] == 1.0
        ),
        "S22_new_partner_requires_and_accepts_remapping": (
            partner_summary["mean_unadapted_partner_accuracy"] <= 0.50
            and partner_summary["mean_remapped_partner_accuracy"] >= 0.98
            and partner_summary["mean_remapped_alignment_r2"] >= 0.99
            and partner_summary["minimum_remapped_frame_cosine"] >= 0.98
            and partner_summary["mean_remapped_support_agreement"] >= 0.98
        ),
        "S23_full_distributed_jspace_closure": full.get(
            "distributed_jspace_closure_score", 0.0
        ) >= 0.98,
        "S24_joint_cut_collapses_closure": (
            full.get("distributed_jspace_closure_score", 0.0)
            - joint_cut.get("distributed_jspace_closure_score", 1.0)
            >= 0.90
        ),
        "S25_workspace_cut_collapses_task": workspace_cut.get(
            "task_accuracy", 1.0
        ) <= 0.20,
        "S26_all_receipt_chains_validate": all(
            summary["receipt_chain_valid_rate"] == 1.0
            for summary in mode_summaries.values()
        ),
        "S27_runtime_uses_no_evaluator_labels": all(
            summary["uses_evaluator_labels_rate"] == 0.0
            for summary in mode_summaries.values()
        ),
        "S28_no_valence_or_identity_reward": True,
    }

    return {
        "schema": "rrct.v048.distributed_sparse_jspace.analysis.v1",
        "version": "0.48.0.dev1",
        "cohort": str(cohort),
        "seeds": list(parsed),
        "trials_per_seed": int(trials_per_seed),
        "modes": list(parsed_modes),
        "unique_world_case_count": len(parsed) * trials_per_seed,
        "decision_count": len(rows),
        "discovery_summary": discovery_summary,
        "mode_summaries": mode_summaries,
        "swap_summary": swap_summary,
        "ablation_summary": ablation_summary,
        "capacity_summary": capacity_summary,
        "provenance_summary": provenance_summary,
        "feedback_summary": feedback_summary,
        "partner_summary": partner_summary,
        "discoveries": discoveries,
        "rows": rows,
        "swap_rows": swaps,
        "ablation_rows": ablations,
        "capacity_rows": capacities,
        "provenance_rows": provenance,
        "feedback_rows": feedback,
        "partner_rows": partner_rows,
        "endpoints": endpoints,
        "all_endpoints_met": all(endpoints.values()),
        "status": (
            "V048_DISTRIBUTED_SPARSE_JSPACE_ENDPOINTS_MET"
            if all(endpoints.values())
            else "V048_DISTRIBUTED_SPARSE_JSPACE_ENDPOINTS_NOT_MET"
        ),
        "scientific_interpretation": (
            "In this synthetic benchmark, two independently parameterized "
            "Jacobian-discovered local workspaces are aligned into a dynamic "
            "sparse union-of-cones that is reportable to both agents, "
            "bidirectionally writable, flexibly reusable, planner-causal, "
            "pair-provenance-bound, and recurrently updated by joint outcomes."
        ),
        "claim_boundary": (
            "This establishes a controlled functional distributed J-space "
            "analogue. It is not an experiment on production language models "
            "and does not establish shared phenomenal consciousness, sentience, "
            "valence, moral status, or subjective merging."
        ),
    }


def write_distributed_sparse_jspace_results(
    result: Mapping[str, Any], output_directory: Path
) -> dict[str, str]:
    output_directory.mkdir(parents=True, exist_ok=True)
    analysis_path = output_directory / "distributed_sparse_jspace_analysis.json"
    summary_path = output_directory / "V0_48_FROZEN_SUMMARY.json"
    csv_path = output_directory / "distributed_sparse_jspace_rows.csv"
    report_path = output_directory / "DISTRIBUTED_SPARSE_JSPACE_REPORT.md"
    analysis_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    compact = dict(result)
    for key in (
        "rows",
        "swap_rows",
        "ablation_rows",
        "capacity_rows",
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
    discovery = result["discovery_summary"]
    report = f"""# RRCT v0.48 Distributed Sparse J-Space Report

## Status

`{result['status']}`

This controlled experiment combines the v0.46 Jacobian-discovered sparse
workspace with the v0.47 distributed atlas, pair provenance, planning, and
recurrence architecture. It tests a functional distributed J-space analogue,
not shared phenomenal consciousness.

## Cohort

- Seeds: {', '.join(map(str, result['seeds']))}
- Unique cases: {result['unique_world_case_count']}
- Matched decisions: {result['decision_count']}
- Frozen endpoints met: {sum(bool(v) for v in result['endpoints'].values())} / {len(result['endpoints'])}

## Discovery

- Local Jacobian ranks: A={discovery['local_ranks_a']}, B={discovery['local_ranks_b']}
- Shared ranks: {discovery['shared_ranks']}
- Minimum canonical correlation: {discovery['minimum_canonical_correlation']:.6f}
- Mean cross-agent alignment R2: {discovery['mean_alignment_r2']:.6f}
- Minimum frame cosine: {discovery['minimum_frame_cosine']:.6f}
- Mean support agreement: {discovery['mean_support_agreement']:.6f}
- Minimum dynamic support count: {discovery['minimum_dynamic_support_count']}

## Matched modes

| Mode | Task | Report A | Report B | Flexible reuse | Distributed J-space closure |
|---|---:|---:|---:|---:|---:|
"""
    for mode in result["modes"]:
        row = modes[mode]
        report += (
            f"| {mode} | {row['task_accuracy']:.6f} | "
            f"{row['report_a_accuracy']:.6f} | {row['report_b_accuracy']:.6f} | "
            f"{row['flexible_reuse_accuracy']:.6f} | "
            f"{row['distributed_jspace_closure_score']:.6f} |\n"
        )
    report += f"""

## Causal tests

- Report swap A: {result['swap_summary']['report_swap_a_rate']:.6f}
- Report swap B: {result['swap_summary']['report_swap_b_rate']:.6f}
- Joint plan swap: {result['swap_summary']['joint_plan_swap_rate']:.6f}
- Flexible reasoning swap: {result['swap_summary']['flexible_reuse_swap_rate']:.6f}
- Ablated task accuracy: {result['ablation_summary']['ablated_task']:.6f}
- Private processing after ablation: A={result['ablation_summary']['private_a_preservation_rate']:.6f}, B={result['ablation_summary']['private_b_preservation_rate']:.6f}

## Interpretation

{result['scientific_interpretation']}

## Boundary

{result['claim_boundary']}
"""
    report_path.write_text(report, encoding="utf-8")
    return {
        analysis_path.name: _file_sha256(analysis_path),
        summary_path.name: _file_sha256(summary_path),
        csv_path.name: _file_sha256(csv_path),
        report_path.name: _file_sha256(report_path),
    }


def _file_sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--trials", type=int, default=64)
    parser.add_argument("--cohort", default="development")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = run_distributed_sparse_jspace_benchmark(
        args.seeds,
        trials_per_seed=args.trials,
        cohort=args.cohort,
    )
    if args.output is not None:
        hashes = write_distributed_sparse_jspace_results(result, args.output)
        print(json.dumps(hashes, sort_keys=True))
    print(result["status"])
    print(f"all_endpoints_met={result['all_endpoints_met']}")
    return 0 if result["all_endpoints_met"] else 1


__all__ = [
    "DistributedJSpaceBenchmarkConfig",
    "SyntheticDistributedJSpaceWorld",
    "TrainedDistributedJSpace",
    "run_distributed_sparse_jspace_benchmark",
    "write_distributed_sparse_jspace_results",
]


if __name__ == "__main__":
    raise SystemExit(main())
