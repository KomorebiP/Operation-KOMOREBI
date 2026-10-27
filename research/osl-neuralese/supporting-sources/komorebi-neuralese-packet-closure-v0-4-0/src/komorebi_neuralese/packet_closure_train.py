"""Prospective v0.4 packet-closure training integration.

The legacy eleven-arm screen shares an identical projective operator model,
initial state, terminal episode stream, and construction-only supervision.  A
separate four-arm primary panel crosses raw versus hard-polar operators with
supervision-matched versus composition-and-return (CR) training without
changing that screen.  In every panel the held-out null-loop and ``r^2`` action
groups are excluded as loss-bearing endpoints in both the auxiliary bank and
terminal episode stream. Reserved actions may still occur at intermediate
prefixes; this is an endpoint-action firewall, not a relation-unseen split.

This module intentionally supplies differentiable *training surrogates*, not
stability certificates.  The switched objective controls sampled max-prefix
projective tangent gain; exhaustive worst-case switched gain remains an
evaluation quantity.  The exact anchor split has rank eight in the mandatory twelve-
dimensional ambient space, leaving a four-dimensional ambient complement for
the delayed-return/Feshbach term.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from typing import Any, Mapping, Sequence

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from .algebra import N_STATES, canonical_maps
from .ambient_packets import enumerate_suffixes, suffix_transition_signature
from .composition_training import anonymous_multiscale_composition_loss
from .data import EpisodeBatch, EpisodeGenerator
from .models import RecurrentOperatorModel
from .packet_models import (
    PacketRunTrace,
    PolarIsometricTableOperatorRNN,
    ProjectiveLinearTableOperatorRNN,
)
from .packet_training import (
    RelationGroupedSuffixPlan,
    construction_packet_margin_loss,
)
from .stability_training import (
    anchor_gram_conditioning_loss,
    feshbach_block_diagnostics,
    feshbach_return_diagnostics,
    g_orthogonal_anchor_projector,
    metric_conditioning_regularizer,
    scale_free_conformal_defect,
    switched_projective_tangent_gain_hinge,
)


V04_PLAN_VERSION = "v0.4-d4-null-and-r2-firewall"
V04_TERMINAL_FIREWALL_VERSION = "v0.4-d4-terminal-endpoint-rejection-v1"


@dataclass(frozen=True)
class PacketClosureArmSpec:
    """One preregistered arm in the supervision-matched ablation panel."""

    name: str
    learn_metric: bool
    composition: bool
    margin: bool
    conformal: bool
    switched_gain: bool
    delayed_return: bool
    model_family: str = "raw"


PACKET_CLOSURE_ARMS: Mapping[str, PacketClosureArmSpec] = {
    "euclidean_supervised": PacketClosureArmSpec(
        name="euclidean_supervised",
        learn_metric=False,
        composition=False,
        margin=False,
        conformal=False,
        switched_gain=False,
        delayed_return=False,
    ),
    "learned_metric_supervised": PacketClosureArmSpec(
        name="learned_metric_supervised",
        learn_metric=True,
        composition=False,
        margin=False,
        conformal=False,
        switched_gain=False,
        delayed_return=False,
    ),
    "euclidean_p111": PacketClosureArmSpec(
        name="euclidean_p111",
        learn_metric=False,
        composition=True,
        margin=True,
        conformal=True,
        switched_gain=True,
        delayed_return=True,
    ),
    "p000": PacketClosureArmSpec(
        name="p000",
        learn_metric=True,
        composition=False,
        margin=False,
        conformal=True,
        switched_gain=True,
        delayed_return=False,
    ),
    "p001": PacketClosureArmSpec(
        name="p001",
        learn_metric=True,
        composition=False,
        margin=False,
        conformal=True,
        switched_gain=True,
        delayed_return=True,
    ),
    "p010": PacketClosureArmSpec(
        name="p010",
        learn_metric=True,
        composition=False,
        margin=True,
        conformal=True,
        switched_gain=True,
        delayed_return=False,
    ),
    "p011": PacketClosureArmSpec(
        name="p011",
        learn_metric=True,
        composition=False,
        margin=True,
        conformal=True,
        switched_gain=True,
        delayed_return=True,
    ),
    "p100": PacketClosureArmSpec(
        name="p100",
        learn_metric=True,
        composition=True,
        margin=False,
        conformal=True,
        switched_gain=True,
        delayed_return=False,
    ),
    "p101": PacketClosureArmSpec(
        name="p101",
        learn_metric=True,
        composition=True,
        margin=False,
        conformal=True,
        switched_gain=True,
        delayed_return=True,
    ),
    "p110": PacketClosureArmSpec(
        name="p110",
        learn_metric=True,
        composition=True,
        margin=True,
        conformal=True,
        switched_gain=True,
        delayed_return=False,
    ),
    "p111": PacketClosureArmSpec(
        name="p111",
        learn_metric=True,
        composition=True,
        margin=True,
        conformal=True,
        switched_gain=True,
        delayed_return=True,
    ),
}

# These arms are deliberately kept outside ``PACKET_CLOSURE_ARMS`` so the
# already-frozen eleven-arm screen remains byte-for-byte stable for callers
# that derive its membership from that registry.
PACKET_CLOSURE_FOLLOWUP_ARMS: Mapping[str, PacketClosureArmSpec] = {
    "euclidean_cr": PacketClosureArmSpec(
        name="euclidean_cr",
        learn_metric=False,
        composition=True,
        margin=False,
        conformal=False,
        switched_gain=False,
        delayed_return=True,
    ),
    "polar_supervised": PacketClosureArmSpec(
        name="polar_supervised",
        learn_metric=False,
        composition=False,
        margin=False,
        conformal=False,
        switched_gain=False,
        delayed_return=False,
        model_family="polar",
    ),
    "polar_cr": PacketClosureArmSpec(
        name="polar_cr",
        learn_metric=False,
        composition=True,
        margin=False,
        conformal=False,
        switched_gain=False,
        delayed_return=True,
        model_family="polar",
    ),
}

# Raw/polar architecture x supervision/CR objective.  The ordering fixes the
# two within-architecture contrasts used by the primary runner.
PRIMARY_PACKET_CLOSURE_ARMS: tuple[str, ...] = (
    "euclidean_supervised",
    "euclidean_cr",
    "polar_supervised",
    "polar_cr",
)

PACKET_CLOSURE_ARM_ALIASES: Mapping[str, str] = {
    "euclidean_supervision": "euclidean_supervised",
    "learned_g_supervision": "learned_metric_supervised",
    "full": "p111",
    "minus_composition": "p011",
    "minus_margin": "p101",
    "minus_return": "p110",
}


@dataclass(frozen=True)
class PacketClosureLossWeights:
    """Frozen provisional coefficients for the v0.4 developmental block."""

    construction_ce: float = 0.25
    anchor: float = 0.01
    composition: float = 0.10
    margin: float = 0.10
    conformal: float = 0.05
    switched_gain: float = 0.02
    delayed_return: float = 0.05

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"loss weight {name} must be finite and nonnegative")


@dataclass(frozen=True)
class PacketClosureTrainConfig:
    """Training configuration shared by every arm in a paired seed block."""

    seed: int
    steps: int
    batch_size: int
    train_max_length: int = 4
    hidden_dim: int = 12
    learning_rate: float = 2e-3
    metric_learning_rate_scale: float = 0.10
    weight_decay: float = 1e-6
    grad_clip: float = 5.0
    warmup_steps: int = 200
    auxiliary_max_depth: int = 4
    stability_return_depths: tuple[int, ...] = (2, 4, 8)
    auxiliary_contexts: int = 1
    construction_words_per_step: int = 4
    required_margin: float = 0.10
    margin_temperature: float = 0.05
    switched_gain_target: float = 2.0
    episode_seed_base: int = 40_000
    checkpoints: int = 11
    device: str = "cpu"
    weights: PacketClosureLossWeights = field(default_factory=PacketClosureLossWeights)

    def validate(self) -> None:
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise TypeError("seed must be an integer")
        if self.steps < 1 or self.batch_size < 1:
            raise ValueError("steps and batch_size must be positive")
        if self.train_max_length < 1:
            raise ValueError("train_max_length must be positive")
        if self.hidden_dim != 12:
            raise ValueError("v0.4 learned packet closure requires hidden_dim == 12")
        if self.learning_rate <= 0.0 or not math.isfinite(self.learning_rate):
            raise ValueError("learning_rate must be finite and positive")
        if (
            self.metric_learning_rate_scale <= 0.0
            or not math.isfinite(self.metric_learning_rate_scale)
        ):
            raise ValueError("metric_learning_rate_scale must be finite and positive")
        if self.weight_decay < 0.0 or not math.isfinite(self.weight_decay):
            raise ValueError("weight_decay must be finite and nonnegative")
        if self.grad_clip <= 0.0 or not math.isfinite(self.grad_clip):
            raise ValueError("grad_clip must be finite and positive")
        if self.warmup_steps < 0:
            raise ValueError("warmup_steps must be nonnegative")
        if self.auxiliary_max_depth != 4:
            raise ValueError("the frozen v0.4 construction bank requires auxiliary_max_depth == 4")
        if tuple(self.stability_return_depths) != (2, 4, 8):
            raise ValueError("the frozen v0.4 return-only path depths must equal (2, 4, 8)")
        if self.auxiliary_contexts < 1:
            raise ValueError("auxiliary_contexts must be positive")
        if self.construction_words_per_step < 1:
            raise ValueError("construction_words_per_step must be positive")
        if not 0.0 <= self.required_margin < 1.0:
            raise ValueError("required_margin must lie in [0, 1)")
        if self.margin_temperature <= 0.0:
            raise ValueError("margin_temperature must be positive")
        if self.switched_gain_target <= 0.0:
            raise ValueError("switched_gain_target must be positive")
        if self.checkpoints < 1:
            raise ValueError("checkpoints must be positive")
        self.weights.validate()


@dataclass(frozen=True)
class ConstructionEndpointResult:
    loss: torch.Tensor
    accuracy: torch.Tensor
    suffix_count: int


@dataclass(frozen=True)
class TerminalFirewallSample:
    """One accepted D4 batch and auditable rejection-sampling counts."""

    batch: EpisodeBatch
    accepted_count: int
    rejected_count: int
    proposal_count: int
    identity_rejection_count: int
    r2_rejection_count: int
    policy_digest: str
    proposal_digest: str


@dataclass(frozen=True)
class V04ConstructionBank:
    """Construction-only view passed to every loss-bearing training path.

    It deliberately has no ``heldout`` field.  Its small interface is also
    accepted by :func:`construction_packet_margin_loss`, whose implementation
    reads only these construction-side properties.
    """

    canonical_transitions: tuple[tuple[int, ...], ...]
    construction: tuple[tuple[int, ...], ...]
    fingerprint: str
    plan_version: str = V04_PLAN_VERSION

    @property
    def num_actions(self) -> int:
        return len(self.canonical_transitions)

    @property
    def num_states(self) -> int:
        return len(self.canonical_transitions[0])

    @property
    def construction_group_signatures(self) -> tuple[tuple[int, ...], ...]:
        transitions = torch.tensor(self.canonical_transitions, dtype=torch.long)
        signatures = {
            _transition_signature(transitions, word) for word in self.construction
        }
        return tuple(sorted(signatures))


@dataclass(frozen=True)
class PacketClosureLossResult:
    total: torch.Tensor
    terminal: torch.Tensor
    construction_ce: torch.Tensor
    anchor: torch.Tensor
    composition: torch.Tensor
    margin: torch.Tensor
    conformal: torch.Tensor
    switched_gain: torch.Tensor
    delayed_return: torch.Tensor
    terminal_accuracy: torch.Tensor
    construction_accuracy: torch.Tensor
    warmup: float
    active_components: tuple[str, ...]
    construction_word_indices: tuple[int, ...]
    stability_word: tuple[int, ...]
    nuisance_rank: int
    p_to_q_norm: torch.Tensor
    q_to_p_norm: torch.Tensor
    q_to_q_norm: torch.Tensor
    return_fraction: torch.Tensor


@dataclass
class TrainedPacketClosureArm:
    """A trained arm plus only construction-side provenance metadata."""

    arm: PacketClosureArmSpec
    config: PacketClosureTrainConfig
    model: RecurrentOperatorModel
    trajectory: list[dict[str, Any]]
    elapsed_seconds: float
    final_loss: float
    parameter_count: int
    trainable_parameter_count: int
    initial_state_digest: str
    final_state_digest: str
    shared_initialization_digest: str
    episode_stream_digest: str
    terminal_proposal_stream_digest: str
    terminal_firewall_policy_digest: str
    terminal_proposal_count: int
    terminal_candidates_accepted: int
    terminal_candidates_rejected: int
    terminal_identity_rejections: int
    terminal_r2_rejections: int
    construction_digest: str
    construction_words: tuple[tuple[int, ...], ...]
    plan_version: str


def get_packet_closure_arm(name: str) -> PacketClosureArmSpec:
    name = PACKET_CLOSURE_ARM_ALIASES.get(name, name)
    if name in PACKET_CLOSURE_ARMS:
        return PACKET_CLOSURE_ARMS[name]
    if name in PACKET_CLOSURE_FOLLOWUP_ARMS:
        return PACKET_CLOSURE_FOLLOWUP_ARMS[name]
    raise ValueError(f"unknown packet-closure arm: {name}")


def _transition_signature(
    transitions: torch.Tensor,
    word: Sequence[int],
) -> tuple[int, ...]:
    return suffix_transition_signature(transitions, tuple(int(item) for item in word))


@lru_cache(maxsize=1)
def terminal_firewall_policy_digest() -> str:
    """Hash the terminal rejection policy without constructing an eval bank."""

    transitions = torch.from_numpy(canonical_maps("d4")).to(dtype=torch.long)
    identity_signature = tuple(range(N_STATES))
    r2_signature = _transition_signature(transitions, (0, 0))
    payload = {
        "policy_version": V04_TERMINAL_FIREWALL_VERSION,
        "family": "d4",
        "sampler": "rowwise-rejection-until-full",
        "canonical_transitions": transitions.tolist(),
        "reserved_action_signatures": {
            "identity": identity_signature,
            "r2": r2_signature,
        },
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def d4_terminal_action_signatures(canonical_ops: torch.Tensor) -> torch.Tensor:
    """Return the full induced D4 action for every canonical operator word."""

    if not isinstance(canonical_ops, torch.Tensor):
        raise TypeError("canonical_ops must be a torch.Tensor")
    if canonical_ops.ndim != 2:
        raise ValueError("canonical_ops must have shape [batch, length]")
    if canonical_ops.is_floating_point() or canonical_ops.is_complex():
        raise TypeError("canonical_ops must have an integer dtype")
    if canonical_ops.numel() and not bool(
        ((canonical_ops >= 0) & (canonical_ops < 2)).all()
    ):
        raise ValueError("D4 canonical operator indices must be zero or one")
    transitions = torch.as_tensor(
        canonical_maps("d4"),
        dtype=torch.long,
        device=canonical_ops.device,
    )
    current = torch.arange(
        N_STATES,
        dtype=torch.long,
        device=canonical_ops.device,
    ).expand(canonical_ops.shape[0], -1)
    for action in canonical_ops.to(dtype=torch.long).unbind(dim=1):
        selected = transitions.index_select(0, action)
        current = torch.gather(selected, 1, current)
    return current


def _d4_terminal_reservation_masks(
    canonical_ops: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    signatures = d4_terminal_action_signatures(canonical_ops)
    identity = torch.arange(
        N_STATES,
        dtype=torch.long,
        device=canonical_ops.device,
    )
    transitions = torch.as_tensor(
        canonical_maps("d4"),
        dtype=torch.long,
        device=canonical_ops.device,
    )
    r2 = transitions[0, transitions[0]]
    return (signatures == identity).all(dim=-1), (signatures == r2).all(dim=-1)


def d4_terminal_reserved_mask(canonical_ops: torch.Tensor) -> torch.Tensor:
    """Mark words whose complete action is identity or the reserved ``r^2``."""

    identity, r2 = _d4_terminal_reservation_masks(canonical_ops)
    return identity | r2


def _select_episode_rows(batch: EpisodeBatch, keep: torch.Tensor) -> EpisodeBatch:
    if keep.ndim != 1 or keep.shape[0] != batch.start.shape[0]:
        raise ValueError("episode row selector has the wrong shape")
    return EpisodeBatch(
        tables=batch.tables[keep],
        maps=batch.maps[keep],
        op_slots=batch.op_slots[keep],
        canonical_ops=batch.canonical_ops[keep],
        start=batch.start[keep],
        target=batch.target[keep],
        intermediates=batch.intermediates[keep],
        canonical_to_slot=batch.canonical_to_slot[keep],
        phi=batch.phi[keep],
        family=batch.family,
    )


def _concatenate_episode_batches(batches: Sequence[EpisodeBatch]) -> EpisodeBatch:
    if not batches:
        raise ValueError("at least one accepted episode batch is required")
    families = {batch.family for batch in batches}
    if len(families) != 1:
        raise ValueError("cannot concatenate episode batches from different families")

    def concatenate(name: str) -> torch.Tensor:
        return torch.cat([getattr(batch, name) for batch in batches], dim=0)

    return EpisodeBatch(
        tables=concatenate("tables"),
        maps=concatenate("maps"),
        op_slots=concatenate("op_slots"),
        canonical_ops=concatenate("canonical_ops"),
        start=concatenate("start"),
        target=concatenate("target"),
        intermediates=concatenate("intermediates"),
        canonical_to_slot=concatenate("canonical_to_slot"),
        phi=concatenate("phi"),
        family=batches[0].family,
    )


_EPISODE_TENSOR_FIELDS = (
    "tables",
    "maps",
    "op_slots",
    "canonical_ops",
    "start",
    "target",
    "intermediates",
    "canonical_to_slot",
    "phi",
)


def _update_episode_batch_bytes(digest: "hashlib._Hash", batch: EpisodeBatch) -> None:
    digest.update(batch.family.encode("ascii"))
    for name in _EPISODE_TENSOR_FIELDS:
        tensor = getattr(batch, name).detach().to(device="cpu").contiguous()
        digest.update(name.encode("ascii"))
        digest.update(str(tensor.dtype).encode("ascii"))
        digest.update(json.dumps(list(tensor.shape), separators=(",", ":")).encode("ascii"))
        digest.update(tensor.numpy().tobytes())


def sample_v04_terminal_batch(
    generator: EpisodeGenerator,
    batch_size: int,
    length: int,
) -> TerminalFirewallSample:
    """Sample a full D4 batch conditioned away from reserved action groups.

    Rejected rows are discarded before any tensor reaches a loss-bearing path.
    Sampling only the remaining number of rows on each retry avoids silently
    discarding accepted candidates and gives exact accepted/rejected counts.
    """

    if not isinstance(generator, EpisodeGenerator):
        raise TypeError("generator must be an EpisodeGenerator")
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    if length < 1:
        raise ValueError("terminal firewall cannot admit the empty identity word")
    accepted_batches: list[EpisodeBatch] = []
    accepted_count = 0
    rejected_count = 0
    identity_rejection_count = 0
    r2_rejection_count = 0
    proposal_count = 0
    refill_index = 0
    proposal_digest = hashlib.sha256()
    proposal_digest.update(b"terminal-proposals")
    proposal_digest.update(terminal_firewall_policy_digest().encode("ascii"))
    proposal_digest.update(int(batch_size).to_bytes(8, byteorder="little", signed=False))
    proposal_digest.update(int(length).to_bytes(8, byteorder="little", signed=False))
    maximum_candidates = max(1024, batch_size * 1024)
    while accepted_count < batch_size:
        remaining = batch_size - accepted_count
        candidate = generator.sample(remaining, length, family="d4")
        identity_rejected, r2_rejected = _d4_terminal_reservation_masks(
            candidate.canonical_ops
        )
        reserved = identity_rejected | r2_rejected
        candidate_count = int(candidate.start.shape[0])
        proposal_count += candidate_count
        identity_count = int(identity_rejected.sum())
        r2_count = int(r2_rejected.sum())
        identity_rejection_count += identity_count
        r2_rejection_count += r2_count
        rejected_count += identity_count + r2_count
        proposal_digest.update(
            int(refill_index).to_bytes(8, byteorder="little", signed=False)
        )
        proposal_digest.update(
            int(candidate_count).to_bytes(8, byteorder="little", signed=False)
        )
        _update_episode_batch_bytes(proposal_digest, candidate)
        classification = (
            identity_rejected.to(dtype=torch.uint8)
            + 2 * r2_rejected.to(dtype=torch.uint8)
        ).detach().to(device="cpu").contiguous()
        proposal_digest.update(b"reservation-class")
        proposal_digest.update(classification.numpy().tobytes())
        keep = ~reserved
        kept = int(keep.sum())
        if kept:
            accepted_batches.append(_select_episode_rows(candidate, keep))
            accepted_count += kept
        if accepted_count + rejected_count > maximum_candidates:
            raise RuntimeError("terminal firewall exceeded its deterministic retry bound")
        refill_index += 1
    batch = _concatenate_episode_batches(accepted_batches)
    if batch.start.shape[0] != batch_size or bool(
        d4_terminal_reserved_mask(batch.canonical_ops).any()
    ):
        raise RuntimeError("terminal firewall admitted a reserved D4 action group")
    return TerminalFirewallSample(
        batch=batch,
        accepted_count=accepted_count,
        rejected_count=rejected_count,
        proposal_count=proposal_count,
        identity_rejection_count=identity_rejection_count,
        r2_rejection_count=r2_rejection_count,
        policy_digest=terminal_firewall_policy_digest(),
        proposal_digest=proposal_digest.hexdigest(),
    )


def _v04_transition_data(
    max_depth: int,
) -> tuple[torch.Tensor, tuple[int, ...], tuple[int, ...], set[tuple[int, ...]]]:
    if max_depth < 2:
        raise ValueError("max_depth must be at least two")
    transitions = torch.from_numpy(canonical_maps("d4")).to(dtype=torch.long)
    identity_signature = tuple(range(int(transitions.shape[1])))
    r2_signature = _transition_signature(transitions, (0, 0))
    generator_signatures = {
        _transition_signature(transitions, (0,)),
        _transition_signature(transitions, (1,)),
    }
    if identity_signature in generator_signatures or r2_signature in generator_signatures:
        raise RuntimeError("the D4 audit groups unexpectedly overlap a generator group")
    return transitions, identity_signature, r2_signature, generator_signatures


def make_v04_construction_bank(max_depth: int = 4) -> V04ConstructionBank:
    """Instantiate only the frozen construction side of the v0.4 firewall."""

    transitions, identity_signature, r2_signature, generator_signatures = (
        _v04_transition_data(max_depth)
    )
    construction: list[tuple[int, ...]] = []
    for word in enumerate_suffixes(int(transitions.shape[0]), max_depth):
        if not word:
            continue
        signature = _transition_signature(transitions, word)
        if signature not in {identity_signature, r2_signature}:
            construction.append(word)
    construction_signatures = {
        _transition_signature(transitions, word) for word in construction
    }
    if not generator_signatures.issubset(construction_signatures):
        raise RuntimeError("both D4 generator action groups must remain in construction")
    canonical = tuple(
        tuple(int(value) for value in row) for row in transitions.tolist()
    )
    payload = {
        "plan_version": V04_PLAN_VERSION,
        "canonical_transitions": canonical,
        "construction": tuple(construction),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return V04ConstructionBank(
        canonical_transitions=canonical,
        construction=tuple(construction),
        fingerprint=hashlib.sha256(encoded).hexdigest(),
    )


def _validate_v04_construction_bank(bank: V04ConstructionBank) -> None:
    transitions = torch.from_numpy(canonical_maps("d4")).to(dtype=torch.long)
    canonical = tuple(
        tuple(int(value) for value in row) for row in transitions.tolist()
    )
    if bank.canonical_transitions != canonical:
        raise ValueError("construction bank must use the canonical D4 transitions")
    identity = tuple(range(N_STATES))
    r2 = _transition_signature(transitions, (0, 0))
    for word in bank.construction:
        if not word:
            raise ValueError("construction bank cannot contain the empty identity word")
        signature = _transition_signature(transitions, word)
        if signature in {identity, r2}:
            raise ValueError(
                "construction endpoint firewall rejected an identity or r2 action signature"
            )


def make_v04_suffix_plan(max_depth: int = 4) -> RelationGroupedSuffixPlan:
    """Instantiate the held-out bank for post-checkpoint evaluation only.

    The empty word is included on the held-out identity side so packet
    membership also requires the captured prefix state itself to decode
    correctly. Every nonempty identity-action word and every word acting as
    ``r^2`` is reserved as a complete endpoint-action group. Training should
    call :func:`make_v04_construction_bank` instead.
    """

    transitions, identity_signature, r2_signature, _ = _v04_transition_data(max_depth)
    bank = make_v04_construction_bank(max_depth)

    heldout: list[tuple[int, ...]] = [()]
    for word in enumerate_suffixes(int(transitions.shape[0]), max_depth):
        if not word:
            continue
        signature = _transition_signature(transitions, word)
        if signature in {identity_signature, r2_signature}:
            heldout.append(word)
    fraction = len(heldout) / (len(bank.construction) + len(heldout))
    return RelationGroupedSuffixPlan(
        canonical_transitions=bank.canonical_transitions,
        construction=bank.construction,
        heldout=tuple(heldout),
        seed=0,
        heldout_fraction=fraction,
    )


def construction_digest(plan: V04ConstructionBank | RelationGroupedSuffixPlan) -> str:
    """Hash construction data only; the audit bank is intentionally absent."""

    payload = {
        "plan_version": V04_PLAN_VERSION,
        "canonical_transitions": plan.canonical_transitions,
        "construction": plan.construction,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def construction_checkpoint_metadata(
    plan: V04ConstructionBank | RelationGroupedSuffixPlan,
) -> dict[str, object]:
    """Return the only suffix-plan fields permitted in checkpoint metadata."""

    return {
        "plan_version": V04_PLAN_VERSION,
        "construction_digest": construction_digest(plan),
        "construction_words": [list(word) for word in plan.construction],
    }


def state_dict_digest(model: nn.Module) -> str:
    """Deterministically hash tensor names, dtypes, shapes, and raw CPU bytes."""

    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        local = tensor.detach().to(device="cpu").contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(local.dtype).encode("ascii"))
        digest.update(json.dumps(list(local.shape), separators=(",", ":")).encode("ascii"))
        digest.update(local.numpy().tobytes())
    return digest.hexdigest()


def shared_initialization_digest(model: nn.Module) -> str:
    """Hash initialization shared across raw and polar architectures.

    Raw and hard-polar models use identical initialized parameter tensors.
    This secondary digest omits the operator encoder for compatibility with
    earlier screens; the full state digest independently verifies that the
    operator encoder is paired as well.
    """

    digest = hashlib.sha256()
    included = 0
    for name, tensor in sorted(model.state_dict().items()):
        if name == "operator_encoder.weight":
            continue
        local = tensor.detach().to(device="cpu").contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(local.dtype).encode("ascii"))
        digest.update(json.dumps(list(local.shape), separators=(",", ":")).encode("ascii"))
        digest.update(local.numpy().tobytes())
        included += 1
    if not included:
        raise ValueError("model exposes no shared initialization tensors")
    return digest.hexdigest()


def _freeze_euclidean_metric(model: RecurrentOperatorModel) -> None:
    diagonal = getattr(model, "metric_log_diagonal", None)
    lower = getattr(model, "metric_strict_lower", None)
    if not isinstance(diagonal, nn.Parameter) or not isinstance(lower, nn.Parameter):
        raise TypeError("Euclidean control requires the standard learned-metric parameters")
    with torch.no_grad():
        diagonal.zero_()
        lower.zero_()
    diagonal.requires_grad_(False)
    lower.requires_grad_(False)


def packet_closure_optimizer_parameter_groups(
    model: RecurrentOperatorModel,
    config: PacketClosureTrainConfig,
) -> list[dict[str, object]]:
    """Separate the slowly moving metric chart from task parameters.

    The Euclidean controls have frozen metric coordinates and therefore expose
    only the base group. Learned-metric arms use exactly the same task LR plus
    a second group at ``metric_learning_rate_scale * learning_rate``.
    """

    config.validate()
    metric_parameters = tuple(
        parameter
        for name, parameter in model.named_parameters()
        if name in {"metric_log_diagonal", "metric_strict_lower"}
        and parameter.requires_grad
    )
    metric_ids = {id(parameter) for parameter in metric_parameters}
    task_parameters = tuple(
        parameter
        for parameter in model.parameters()
        if parameter.requires_grad and id(parameter) not in metric_ids
    )
    if not task_parameters:
        raise ValueError("packet-closure model has no trainable task parameters")
    groups: list[dict[str, object]] = [
        {
            "params": task_parameters,
            "lr": config.learning_rate,
            "group_name": "task",
        }
    ]
    if metric_parameters:
        groups.append(
            {
                "params": metric_parameters,
                "lr": config.learning_rate * config.metric_learning_rate_scale,
                "group_name": "metric",
            }
        )
    return groups


def _update_episode_digest(
    digest: "hashlib._Hash",
    batch: EpisodeBatch,
    *,
    step: int,
    stability_word: tuple[int, ...],
    construction_word_indices: tuple[int, ...],
    terminal_accepted_count: int,
    terminal_rejected_count: int,
    terminal_firewall_digest: str,
) -> None:
    digest.update(int(step).to_bytes(8, byteorder="little", signed=False))
    digest.update(b"terminal-firewall-policy")
    digest.update(terminal_firewall_digest.encode("ascii"))
    digest.update(int(terminal_accepted_count).to_bytes(8, byteorder="little", signed=False))
    digest.update(int(terminal_rejected_count).to_bytes(8, byteorder="little", signed=False))
    digest.update(bytes(stability_word))
    for index in construction_word_indices:
        digest.update(int(index).to_bytes(4, byteorder="little", signed=False))
    _update_episode_batch_bytes(digest, batch)


def build_packet_closure_model(
    config: PacketClosureTrainConfig,
    arm: str | PacketClosureArmSpec,
) -> ProjectiveLinearTableOperatorRNN:
    """Build an exactly initialized raw or hard-polar operator model."""

    config.validate()
    spec = get_packet_closure_arm(arm) if isinstance(arm, str) else arm
    torch.manual_seed(config.seed)
    if spec.model_family == "raw":
        model = ProjectiveLinearTableOperatorRNN(hidden_dim=config.hidden_dim)
    elif spec.model_family == "polar":
        if spec.learn_metric:
            raise ValueError("hard-polar arms require the fixed Euclidean metric")
        model = PolarIsometricTableOperatorRNN(hidden_dim=config.hidden_dim)
    else:
        raise ValueError(f"unknown packet-closure model family: {spec.model_family}")
    if not spec.learn_metric:
        _freeze_euclidean_metric(model)
    return model


def _validate_model_family(
    model: RecurrentOperatorModel,
    spec: PacketClosureArmSpec,
) -> None:
    is_polar = isinstance(model, PolarIsometricTableOperatorRNN)
    expected_polar = spec.model_family == "polar"
    if spec.model_family not in {"raw", "polar"}:
        raise ValueError(f"unknown packet-closure model family: {spec.model_family}")
    if is_polar != expected_polar:
        raise TypeError(
            f"arm {spec.name} requires a {spec.model_family} packet-closure model"
        )


def _model_metric(model: RecurrentOperatorModel) -> torch.Tensor:
    candidate = getattr(model, "invariant_metric", None)
    if candidate is None:
        raise TypeError("packet-closure model must expose invariant_metric")
    metric = candidate() if callable(candidate) else candidate
    if not isinstance(metric, torch.Tensor):
        raise TypeError("invariant_metric must resolve to a tensor")
    return metric


def _state_anchors(model: RecurrentOperatorModel) -> torch.Tensor:
    candidate = getattr(model, "state_anchors", None)
    if callable(candidate):
        anchors = candidate()
    else:
        embedding = getattr(model, "state_embedding", None)
        if embedding is None:
            raise TypeError("packet-closure model must expose state anchors")
        states = torch.arange(N_STATES, device=embedding.weight.device)
        anchors = model.initial_hidden(states)
    if anchors.shape != (N_STATES, getattr(model, "hidden_dim", -1)):
        raise ValueError("state anchors must have shape [states, hidden_dim]")
    return anchors


def _decoder_weight(model: RecurrentOperatorModel) -> torch.Tensor:
    decoder = getattr(model, "decoder", None)
    weight = getattr(decoder, "weight", None)
    if not isinstance(weight, torch.Tensor):
        raise TypeError("packet-closure model must expose a linear decoder weight")
    return weight


def construction_endpoint_cross_entropy(
    model: RecurrentOperatorModel,
    hidden: torch.Tensor,
    operator_matrices: torch.Tensor,
    slot_transitions: torch.Tensor,
    canonical_to_slot: torch.Tensor,
    source_states: torch.Tensor,
    plan: V04ConstructionBank,
) -> ConstructionEndpointResult:
    """Apply construction suffixes only and supervise their terminal endpoints."""

    if not plan.construction:
        raise ValueError("construction bank must be nonempty")
    batch = hidden.shape[0]
    rows = torch.arange(batch, device=hidden.device)
    losses: list[torch.Tensor] = []
    accuracies: list[torch.Tensor] = []
    for word in plan.construction:
        endpoint = hidden
        target = source_states
        for canonical_action in word:
            slots = canonical_to_slot[:, canonical_action]
            codes = operator_matrices[rows, slots]
            endpoint = model.step_hidden(endpoint, codes)
            transitions = slot_transitions[rows, slots]
            target = transitions[rows, target]
        logits = model.decode_hidden(endpoint)
        losses.append(F.cross_entropy(logits, target))
        accuracies.append((logits.argmax(dim=-1) == target).to(logits.dtype).mean())
    return ConstructionEndpointResult(
        loss=torch.stack(losses).mean(),
        accuracy=torch.stack(accuracies).mean(),
        suffix_count=len(plan.construction),
    )


@lru_cache(maxsize=16)
def _cached_stability_word_schedule(
    canonical_transitions: tuple[tuple[int, ...], ...],
    construction: tuple[tuple[int, ...], ...],
    normalized_depths: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    transitions = torch.tensor(canonical_transitions, dtype=torch.long)
    allowed = {
        _transition_signature(transitions, word) for word in construction
    }
    selected: list[tuple[int, ...]] = []
    for depth in normalized_depths:
        first_by_signature: dict[tuple[int, ...], tuple[int, ...]] = {}
        for word in enumerate_suffixes(len(canonical_transitions), depth):
            if len(word) != depth:
                continue
            signature = _transition_signature(transitions, word)
            prefixes_are_construction = all(
                _transition_signature(transitions, word[:prefix_depth]) in allowed
                for prefix_depth in range(1, len(word) + 1)
            )
            if (
                signature in allowed
                and prefixes_are_construction
                and signature not in first_by_signature
            ):
                first_by_signature[signature] = word
        selected.extend(first_by_signature[signature] for signature in sorted(first_by_signature))
    if not selected:
        raise ValueError("construction groups yield no switched stability words")
    if any(_transition_signature(transitions, word) not in allowed for word in selected):
        raise RuntimeError("non-construction action entered the stability schedule")
    return tuple(selected)


def make_v04_stability_word_schedule(
    plan: V04ConstructionBank,
    *,
    depths: Sequence[int] = (2, 4, 8),
) -> tuple[tuple[int, ...], ...]:
    """Choose fixed allowed-group switched words at each required depth.

    The schedule is independent of the depth-four endpoint-supervision bank.
    At each depth, it takes the lexicographically first word for every
    construction-side induced action that occurs at that depth.  Reserved
    identity and r2 action signatures are rejected at the endpoint and at
    every nonempty prefix before a word can enter the schedule.
    """

    normalized_depths = tuple(int(depth) for depth in depths)
    if not normalized_depths or any(depth < 2 for depth in normalized_depths):
        raise ValueError("stability depths must be at least two")
    if len(set(normalized_depths)) != len(normalized_depths):
        raise ValueError("stability depths must be unique")
    return _cached_stability_word_schedule(
        plan.canonical_transitions,
        plan.construction,
        normalized_depths,
    )


def _metric_scale_normalize_operators(
    operators: torch.Tensor,
    metric: torch.Tensor,
    *,
    eps: float = 1e-12,
) -> torch.Tensor:
    """Remove each operator's projectively irrelevant metric Frobenius scale."""

    conformal = scale_free_conformal_defect(operators, metric, eps=eps)
    dimension = operators.shape[-1]
    scales = conformal.metric_frobenius_norm.clamp_min(eps) / math.sqrt(dimension)
    return operators / scales[..., None, None]


def _ordered_product(operators: torch.Tensor) -> torch.Tensor:
    """Return ``M[-1] ... M[0]`` with leading batch axes preserved."""

    dimension = operators.shape[-1]
    product = torch.eye(
        dimension,
        dtype=operators.dtype,
        device=operators.device,
    ).expand(operators.shape[:-3] + (dimension, dimension))
    for operator in operators.unbind(dim=-3):
        product = operator @ product
    return product


def _warmup_multiplier(step: int, warmup_steps: int) -> float:
    if warmup_steps == 0:
        return 1.0
    return min(1.0, (step + 1) / warmup_steps)


def construction_minibank(
    bank: V04ConstructionBank,
    *,
    step: int,
    words_per_step: int,
) -> tuple[V04ConstructionBank, tuple[int, ...]]:
    """Take a deterministic cyclic construction-only mini-bank.

    Contiguous cycling makes each of the 20 frozen depth-four words receive
    equal exposure over complete cycles.  The same indices are included in the
    paired stream digest for every arm.
    """

    if step < 0:
        raise ValueError("step must be nonnegative")
    if words_per_step < 1:
        raise ValueError("words_per_step must be positive")
    count = len(bank.construction)
    selected_count = min(words_per_step, count)
    start = (step * selected_count) % count
    indices = tuple((start + offset) % count for offset in range(selected_count))
    words = tuple(bank.construction[index] for index in indices)
    payload = {
        "parent": bank.fingerprint,
        "indices": indices,
        "construction": words,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return (
        V04ConstructionBank(
            canonical_transitions=bank.canonical_transitions,
            construction=words,
            fingerprint=hashlib.sha256(encoded).hexdigest(),
        ),
        indices,
    )


def compute_packet_closure_losses(
    model: RecurrentOperatorModel,
    batch: EpisodeBatch,
    plan: V04ConstructionBank,
    arm: str | PacketClosureArmSpec,
    config: PacketClosureTrainConfig,
    *,
    step: int,
) -> PacketClosureLossResult:
    """Compute one arm's loss from a construction-only bank."""

    config.validate()
    if not isinstance(plan, V04ConstructionBank):
        raise TypeError("training losses require V04ConstructionBank, never an evaluation plan")
    _validate_v04_construction_bank(plan)
    if batch.family != "d4":
        raise ValueError("v0.4 packet-closure training requires D4 terminal episodes")
    if bool(d4_terminal_reserved_mask(batch.canonical_ops).any()):
        raise ValueError(
            "terminal endpoint firewall rejected an identity or r2 action signature"
        )
    spec = get_packet_closure_arm(arm) if isinstance(arm, str) else arm
    trace = model.run(batch.tables, batch.op_slots, batch.start)
    terminal_loss = F.cross_entropy(trace.logits, batch.target)
    terminal_accuracy = (
        trace.logits.argmax(dim=-1) == batch.target
    ).to(trace.logits.dtype).mean()
    if trace.operator_codes is None:
        raise TypeError("packet-closure model must expose recurrent operator matrices")
    operator_matrices = trace.operator_codes
    contexts = min(config.auxiliary_contexts, int(batch.start.shape[0]))
    source_states = batch.start[:contexts]
    initial_hidden = model.initial_hidden(source_states)
    mini_plan, construction_indices = construction_minibank(
        plan,
        step=step,
        words_per_step=config.construction_words_per_step,
    )
    common_construction = construction_endpoint_cross_entropy(
        model,
        initial_hidden,
        operator_matrices[:contexts],
        batch.maps[:contexts],
        batch.canonical_to_slot[:contexts],
        source_states,
        mini_plan,
    )
    metric = _model_metric(model)
    anchors = _state_anchors(model)
    anchor_conditioning = anchor_gram_conditioning_loss(anchors, metric)
    metric_conditioning = metric_conditioning_regularizer(metric)
    anchor_loss = anchor_conditioning.loss + metric_conditioning.loss
    zero = terminal_loss * 0.0

    composition_loss = zero
    if spec.composition:
        all_starts = torch.arange(N_STATES, device=batch.start.device)
        anchor_states = model.initial_hidden(all_starts)
        per_context: list[torch.Tensor] = []
        scale_bins = tuple(range(1, config.auxiliary_max_depth + 1))
        for context in range(contexts):
            canonical_slots = batch.canonical_to_slot[context]
            canonical_codes = operator_matrices[context].index_select(0, canonical_slots)
            canonical_table = batch.maps[context].index_select(0, canonical_slots)
            result = anonymous_multiscale_composition_loss(
                anchor_states,
                canonical_codes,
                canonical_table,
                plan.construction,
                model.step_hidden,
                metric=metric,
                scales=scale_bins,
            )
            per_context.append(result.loss)
        composition_loss = torch.stack(per_context).mean()

    margin_loss = zero
    if spec.margin:
        margin_result = construction_packet_margin_loss(
            initial_hidden,
            operator_matrices[:contexts],
            _decoder_weight(model),
            metric,
            batch.maps[:contexts],
            batch.canonical_to_slot[:contexts],
            source_states,
            mini_plan,
            required_margin=config.required_margin,
            temperature=config.margin_temperature,
        )
        margin_loss = margin_result.loss

    conformal_loss = zero
    if spec.conformal:
        conformal_result = scale_free_conformal_defect(
            operator_matrices[:contexts],
            metric,
            near_zero_weight=1.0,
        )
        conformal_loss = conformal_result.loss

    stability_words = make_v04_stability_word_schedule(
        plan,
        depths=config.stability_return_depths,
    )
    stability_word = stability_words[step % len(stability_words)]
    switched_loss = zero
    return_loss = zero
    p_to_q = zero
    q_to_p = zero
    q_to_q = zero
    return_fraction = zero
    nuisance_rank = config.hidden_dim - N_STATES
    if spec.switched_gain or spec.delayed_return:
        stability_slots = EpisodeGenerator.slots_for_word(
            batch.canonical_to_slot[:contexts], stability_word
        )
        stability_trace = model.run(
            batch.tables[:contexts],
            stability_slots,
            source_states,
        )
        if not isinstance(stability_trace, PacketRunTrace):
            raise TypeError("packet closure requires a PacketRunTrace")
        selected_operators = stability_trace.selected_operator_matrices
        normalized_selected = _metric_scale_normalize_operators(
            selected_operators,
            metric,
        )
        plane = g_orthogonal_anchor_projector(anchors, metric)
        nuisance_rank = plane.ambient_dimension - plane.rank
        generator_blocks = feshbach_block_diagnostics(
            _metric_scale_normalize_operators(operator_matrices[:contexts], metric),
            plane,
            metric,
        )
        p_to_q = generator_blocks.p_to_q_energy.clamp_min(0.0).sqrt().mean()
        q_to_p = generator_blocks.q_to_p_energy.clamp_min(0.0).sqrt().mean()
        q_to_q = generator_blocks.q_to_q_energy.clamp_min(0.0).sqrt().mean()
        if spec.switched_gain:
            gain_result = switched_projective_tangent_gain_hinge(
                normalized_selected,
                stability_trace.hidden[0],
                metric,
                maximum_gain=config.switched_gain_target,
                near_zero_weight=1.0,
            )
            switched_loss = gain_result.loss
        if spec.delayed_return:
            departure = normalized_selected[:, 0]
            return_operator = normalized_selected[:, -1]
            complement_product = _ordered_product(normalized_selected[:, 1:-1])
            delayed = feshbach_return_diagnostics(
                return_operator,
                complement_product,
                departure,
                plane,
                metric,
            )
            # Operators have already been normalized in their metric
            # Frobenius scale.  The direct return energy is the scientific
            # target; the ratio is retained only as a diagnostic because its
            # denominator could otherwise be manipulated.
            return_loss = delayed.return_energy.mean() / config.hidden_dim
            return_fraction = delayed.full_product_fraction.mean()

    warmup = _warmup_multiplier(step, config.warmup_steps)
    weights = config.weights
    structural = (
        weights.construction_ce * common_construction.loss
        + weights.anchor * anchor_loss
        + (weights.composition * composition_loss if spec.composition else zero)
        + (weights.margin * margin_loss if spec.margin else zero)
        + (weights.conformal * conformal_loss if spec.conformal else zero)
        + (weights.switched_gain * switched_loss if spec.switched_gain else zero)
        + (weights.delayed_return * return_loss if spec.delayed_return else zero)
    )
    total = terminal_loss + warmup * structural
    active = ["terminal", "construction_ce", "anchor"]
    for name, enabled in (
        ("composition", spec.composition),
        ("margin", spec.margin),
        ("conformal", spec.conformal),
        ("switched_gain", spec.switched_gain),
        ("delayed_return", spec.delayed_return),
    ):
        if enabled:
            active.append(name)
    return PacketClosureLossResult(
        total=total,
        terminal=terminal_loss,
        construction_ce=common_construction.loss,
        anchor=anchor_loss,
        composition=composition_loss,
        margin=margin_loss,
        conformal=conformal_loss,
        switched_gain=switched_loss,
        delayed_return=return_loss,
        terminal_accuracy=terminal_accuracy,
        construction_accuracy=common_construction.accuracy,
        warmup=warmup,
        active_components=tuple(active),
        construction_word_indices=construction_indices,
        stability_word=stability_word,
        nuisance_rank=nuisance_rank,
        p_to_q_norm=p_to_q,
        q_to_p_norm=q_to_p,
        q_to_q_norm=q_to_q,
        return_fraction=return_fraction,
    )


def _loss_record(
    losses: PacketClosureLossResult,
    *,
    step: int,
    length: int,
    gradient_norm: float,
    metric: torch.Tensor,
    base_learning_rate: float,
    metric_learning_rate: float | None,
    terminal_accepted_count: int,
    terminal_rejected_count: int,
    terminal_proposal_count: int,
    terminal_identity_rejections: int,
    terminal_r2_rejections: int,
    terminal_accepted_cumulative: int,
    terminal_rejected_cumulative: int,
    terminal_proposal_cumulative: int,
    terminal_identity_rejections_cumulative: int,
    terminal_r2_rejections_cumulative: int,
    terminal_firewall_digest: str,
    terminal_proposal_digest: str,
) -> dict[str, Any]:
    eigenvalues = torch.linalg.eigvalsh(metric.detach().to(torch.float64))
    condition = float(eigenvalues.max() / eigenvalues.min().clamp_min(1e-30))
    return {
        "step": step + 1,
        "length": length,
        "loss": float(losses.total.detach()),
        "terminal_loss": float(losses.terminal.detach()),
        "construction_ce_loss": float(losses.construction_ce.detach()),
        "anchor_loss": float(losses.anchor.detach()),
        "composition_loss": float(losses.composition.detach()),
        "margin_loss": float(losses.margin.detach()),
        "conformal_loss": float(losses.conformal.detach()),
        "switched_gain_loss": float(losses.switched_gain.detach()),
        "delayed_return_loss": float(losses.delayed_return.detach()),
        "terminal_accuracy": float(losses.terminal_accuracy.detach()),
        "construction_accuracy": float(losses.construction_accuracy.detach()),
        "gradient_norm_before_clip": gradient_norm,
        "base_learning_rate": base_learning_rate,
        "metric_learning_rate": metric_learning_rate,
        "terminal_firewall_policy_digest": terminal_firewall_digest,
        "terminal_candidates_accepted": terminal_accepted_count,
        "terminal_candidates_rejected": terminal_rejected_count,
        "terminal_proposal_count": terminal_proposal_count,
        "terminal_identity_rejections": terminal_identity_rejections,
        "terminal_r2_rejections": terminal_r2_rejections,
        "terminal_candidates_accepted_cumulative": terminal_accepted_cumulative,
        "terminal_candidates_rejected_cumulative": terminal_rejected_cumulative,
        "terminal_proposal_count_cumulative": terminal_proposal_cumulative,
        "terminal_identity_rejections_cumulative": (
            terminal_identity_rejections_cumulative
        ),
        "terminal_r2_rejections_cumulative": terminal_r2_rejections_cumulative,
        "terminal_proposal_digest": terminal_proposal_digest,
        "warmup": losses.warmup,
        "metric_condition": condition,
        "construction_word_indices": list(losses.construction_word_indices),
        "stability_word": list(losses.stability_word),
        "retained_rank": N_STATES,
        "nuisance_rank": losses.nuisance_rank,
        "p_to_q_norm": float(losses.p_to_q_norm.detach()),
        "q_to_p_norm": float(losses.q_to_p_norm.detach()),
        "q_to_q_norm": float(losses.q_to_q_norm.detach()),
        "return_fraction": float(losses.return_fraction.detach()),
        "active_components": list(losses.active_components),
    }


def train_packet_closure_arm(
    arm: str | PacketClosureArmSpec,
    config: PacketClosureTrainConfig,
    *,
    model: RecurrentOperatorModel | None = None,
    plan: V04ConstructionBank | None = None,
) -> TrainedPacketClosureArm:
    """Train one paired arm on a deterministic episode stream."""

    config.validate()
    spec = get_packet_closure_arm(arm) if isinstance(arm, str) else arm
    if model is None:
        model = build_packet_closure_model(config, spec)
    elif not isinstance(model, RecurrentOperatorModel):
        raise TypeError("v0.4 arms require a RecurrentOperatorModel")
    if getattr(model, "hidden_dim", None) != config.hidden_dim:
        raise ValueError("provided model does not match the training configuration")
    _validate_model_family(model, spec)
    if not spec.learn_metric:
        _freeze_euclidean_metric(model)
    plan = make_v04_construction_bank(config.auxiliary_max_depth) if plan is None else plan
    if not isinstance(plan, V04ConstructionBank):
        raise TypeError("training requires V04ConstructionBank, never an evaluation plan")
    _validate_v04_construction_bank(plan)
    safe_metadata = construction_checkpoint_metadata(plan)

    initial_digest = state_dict_digest(model)
    shared_initial_digest = shared_initialization_digest(model)
    device = torch.device(config.device)
    model = model.to(device)
    model.train()
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    optimizer_groups = packet_closure_optimizer_parameter_groups(model, config)
    optimizer = torch.optim.AdamW(
        optimizer_groups,
        weight_decay=config.weight_decay,
    )
    generator = EpisodeGenerator(config.episode_seed_base + config.seed)
    stream_digest = hashlib.sha256()
    proposal_stream_digest = hashlib.sha256()
    proposal_stream_digest.update(b"terminal-proposal-stream")
    proposal_stream_digest.update(terminal_firewall_policy_digest().encode("ascii"))
    trajectory: list[dict[str, Any]] = []
    checkpoint_indices = set(
        np.linspace(
            0,
            config.steps - 1,
            num=min(config.checkpoints, config.steps),
            dtype=int,
        ).tolist()
    )
    stability_words = make_v04_stability_word_schedule(
        plan,
        depths=config.stability_return_depths,
    )
    final_loss = math.nan
    firewall_digest = terminal_firewall_policy_digest()
    terminal_accepted_total = 0
    terminal_rejected_total = 0
    terminal_proposal_total = 0
    terminal_identity_rejections_total = 0
    terminal_r2_rejections_total = 0
    started = time.perf_counter()
    for step in range(config.steps):
        length = int(generator.rng.integers(1, config.train_max_length + 1))
        terminal_sample = sample_v04_terminal_batch(
            generator,
            config.batch_size,
            length,
        )
        if terminal_sample.policy_digest != firewall_digest:
            raise RuntimeError("terminal firewall policy changed within a run")
        cpu_batch = terminal_sample.batch
        terminal_accepted_total += terminal_sample.accepted_count
        terminal_rejected_total += terminal_sample.rejected_count
        terminal_proposal_total += terminal_sample.proposal_count
        terminal_identity_rejections_total += terminal_sample.identity_rejection_count
        terminal_r2_rejections_total += terminal_sample.r2_rejection_count
        proposal_stream_digest.update(
            int(step).to_bytes(8, byteorder="little", signed=False)
        )
        proposal_stream_digest.update(terminal_sample.proposal_digest.encode("ascii"))
        stability_word = stability_words[step % len(stability_words)]
        _, construction_indices = construction_minibank(
            plan,
            step=step,
            words_per_step=config.construction_words_per_step,
        )
        _update_episode_digest(
            stream_digest,
            cpu_batch,
            step=step,
            stability_word=stability_word,
            construction_word_indices=construction_indices,
            terminal_accepted_count=terminal_sample.accepted_count,
            terminal_rejected_count=terminal_sample.rejected_count,
            terminal_firewall_digest=terminal_sample.policy_digest,
        )
        batch = cpu_batch.to(device)
        optimizer.zero_grad(set_to_none=True)
        losses = compute_packet_closure_losses(
            model,
            batch,
            plan,
            spec,
            config,
            step=step,
        )
        if not bool(torch.isfinite(losses.total.detach())):
            raise FloatingPointError(f"non-finite loss at step {step}")
        losses.total.backward()
        gradient_norm = float(torch.nn.utils.clip_grad_norm_(trainable, config.grad_clip))
        if not math.isfinite(gradient_norm):
            raise FloatingPointError(f"non-finite gradient norm at step {step}")
        optimizer.step()
        final_loss = float(losses.total.detach())
        if step in checkpoint_indices:
            trajectory.append(
                _loss_record(
                    losses,
                    step=step,
                    length=length,
                    gradient_norm=gradient_norm,
                    metric=_model_metric(model),
                    base_learning_rate=config.learning_rate,
                    metric_learning_rate=(
                        config.learning_rate * config.metric_learning_rate_scale
                        if spec.learn_metric
                        else None
                    ),
                    terminal_accepted_count=terminal_sample.accepted_count,
                    terminal_rejected_count=terminal_sample.rejected_count,
                    terminal_proposal_count=terminal_sample.proposal_count,
                    terminal_identity_rejections=(
                        terminal_sample.identity_rejection_count
                    ),
                    terminal_r2_rejections=terminal_sample.r2_rejection_count,
                    terminal_accepted_cumulative=terminal_accepted_total,
                    terminal_rejected_cumulative=terminal_rejected_total,
                    terminal_proposal_cumulative=terminal_proposal_total,
                    terminal_identity_rejections_cumulative=(
                        terminal_identity_rejections_total
                    ),
                    terminal_r2_rejections_cumulative=(
                        terminal_r2_rejections_total
                    ),
                    terminal_firewall_digest=terminal_sample.policy_digest,
                    terminal_proposal_digest=terminal_sample.proposal_digest,
                )
            )

    elapsed = time.perf_counter() - started
    model.eval()
    return TrainedPacketClosureArm(
        arm=spec,
        config=config,
        model=model,
        trajectory=trajectory,
        elapsed_seconds=elapsed,
        final_loss=final_loss,
        parameter_count=sum(parameter.numel() for parameter in model.parameters()),
        trainable_parameter_count=sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad),
        initial_state_digest=initial_digest,
        final_state_digest=state_dict_digest(model),
        shared_initialization_digest=shared_initial_digest,
        episode_stream_digest=stream_digest.hexdigest(),
        terminal_proposal_stream_digest=proposal_stream_digest.hexdigest(),
        terminal_firewall_policy_digest=firewall_digest,
        terminal_proposal_count=terminal_proposal_total,
        terminal_candidates_accepted=terminal_accepted_total,
        terminal_candidates_rejected=terminal_rejected_total,
        terminal_identity_rejections=terminal_identity_rejections_total,
        terminal_r2_rejections=terminal_r2_rejections_total,
        construction_digest=str(safe_metadata["construction_digest"]),
        construction_words=plan.construction,
        plan_version=V04_PLAN_VERSION,
    )


def train_paired_packet_closure_panel(
    config: PacketClosureTrainConfig,
    *,
    arm_names: Sequence[str] | None = None,
) -> dict[str, TrainedPacketClosureArm]:
    """Train arms independently from the same initialization and episode stream."""

    requested = tuple(PACKET_CLOSURE_ARMS) if arm_names is None else tuple(arm_names)
    names = tuple(get_packet_closure_arm(name).name for name in requested)
    if not names or len(set(names)) != len(names):
        raise ValueError("arm_names must be a nonempty unique sequence")
    plan = make_v04_construction_bank(config.auxiliary_max_depth)
    results: dict[str, TrainedPacketClosureArm] = {}
    for name in names:
        spec = get_packet_closure_arm(name)
        model = build_packet_closure_model(config, spec)
        results[name] = train_packet_closure_arm(
            spec,
            config,
            model=model,
            plan=plan,
        )
    initial_digests = {result.initial_state_digest for result in results.values()}
    shared_initial_digests = {
        result.shared_initialization_digest for result in results.values()
    }
    stream_digests = {result.episode_stream_digest for result in results.values()}
    proposal_stream_digests = {
        result.terminal_proposal_stream_digest for result in results.values()
    }
    firewall_digests = {
        result.terminal_firewall_policy_digest for result in results.values()
    }
    terminal_counts = {
        (
            result.terminal_proposal_count,
            result.terminal_candidates_accepted,
            result.terminal_candidates_rejected,
            result.terminal_identity_rejections,
            result.terminal_r2_rejections,
        )
        for result in results.values()
    }
    if len(initial_digests) != 1:
        raise RuntimeError("paired arms did not begin from an identical state_dict")
    if len(shared_initial_digests) != 1:
        raise RuntimeError("paired architectures did not share anchor/decoder initialization")
    if len(stream_digests) != 1:
        raise RuntimeError("paired arms did not consume an identical episode stream")
    if len(proposal_stream_digests) != 1:
        raise RuntimeError("paired arms did not consume identical terminal proposals")
    if len(firewall_digests) != 1 or len(terminal_counts) != 1:
        raise RuntimeError("paired arms did not apply an identical terminal firewall")
    return results


__all__ = [
    "PACKET_CLOSURE_ARM_ALIASES",
    "PACKET_CLOSURE_ARMS",
    "PACKET_CLOSURE_FOLLOWUP_ARMS",
    "PRIMARY_PACKET_CLOSURE_ARMS",
    "PacketClosureArmSpec",
    "PacketClosureLossResult",
    "PacketClosureLossWeights",
    "PacketClosureTrainConfig",
    "TerminalFirewallSample",
    "TrainedPacketClosureArm",
    "V04ConstructionBank",
    "V04_PLAN_VERSION",
    "V04_TERMINAL_FIREWALL_VERSION",
    "build_packet_closure_model",
    "compute_packet_closure_losses",
    "construction_checkpoint_metadata",
    "construction_digest",
    "construction_endpoint_cross_entropy",
    "construction_minibank",
    "d4_terminal_action_signatures",
    "d4_terminal_reserved_mask",
    "get_packet_closure_arm",
    "make_v04_stability_word_schedule",
    "make_v04_construction_bank",
    "make_v04_suffix_plan",
    "packet_closure_optimizer_parameter_groups",
    "sample_v04_terminal_batch",
    "shared_initialization_digest",
    "state_dict_digest",
    "terminal_firewall_policy_digest",
    "train_packet_closure_arm",
    "train_paired_packet_closure_panel",
]
