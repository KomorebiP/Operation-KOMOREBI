"""Training integration for the v0.6 Invariant Observable Kernel block.

This module keeps the v0.4/v0.5 terminal firewall, construction stream, and
table-derived relation-cell bank fixed while comparing three distinct claims:

``polar_*``
    The inherited unrestricted twelve-dimensional hard-polar architecture.

``learned_intertwiner``
    The same unrestricted architecture augmented by a learned rank-seven
    contrast observer ``Pi``.  ``Pi`` is row orthonormal, but it never constructs the
    recurrent state or operators.  Its semantic operator and readout are the
    *induced* quantities ``T_g = Pi M_g Pi.T`` and ``C = J D Pi.T``.  Thus the
    intertwining and readout residuals cannot be laundered by unconstrained
    auxiliary heads.  The centered anchor-Gram constraint
    ``(Pi B).T (Pi B) ~= I - 11.T / 8`` supplies quotient-anchor geometry
    without selecting an arbitrary ``O(7)`` basis for the observed quotient.

``hard_kernel_*``
    The learned-frame direct-sum architecture.  Its semantic and ambient
    subspaces are invariant by construction.  The ambient table encoder is a
    seeded, frozen random map and the ambient state is dormant; this experiment
    does not claim that the fiber performs useful memory computation.

All relation objectives use anonymous same-action path pairs derived from the
visible integer tables.  Consequently every positive v0.6 result is an
explicit-pressure result, never evidence for spontaneous operator discovery.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np
import torch
from torch import nn

from .algebra import N_STATES
from .data import EpisodeBatch, EpisodeGenerator
from .flatness_training import (
    RELATION_CELL_COUNT,
    RelationCellBank,
    _ordered_product,
    relation_cell_bank,
)
from .invariant_kernel_models import (
    AMBIENT_DIM as AMBIENT_FIBER_DIM,
    CENTERED_NULL_DIM,
    COMMON_LOGIT_DIM,
    OBSERVABLE_DIM,
    LearnedFrameBlockIsometricOperatorRNN,
)
from .models import RecurrentOperatorModel
from .packet_closure_train import (
    PacketClosureArmSpec,
    PacketClosureLossResult,
    PacketClosureLossWeights,
    PacketClosureTrainConfig,
    V04ConstructionBank,
    compute_packet_closure_losses,
    construction_checkpoint_metadata,
    make_v04_construction_bank,
    packet_closure_optimizer_parameter_groups,
    sample_v04_terminal_batch,
    state_dict_digest,
    terminal_firewall_policy_digest,
)
from .packet_models import PacketRunTrace, PolarIsometricTableOperatorRNN


V06_PLAN_VERSION = "v0.6-invariant-observable-kernel-dev2"
OBSERVER_DIM = OBSERVABLE_DIM


@dataclass(frozen=True)
class InvariantKernelArmSpec:
    """One arm in the supervision-matched v0.6 developmental panel."""

    name: str
    architecture: str = "polar"
    legacy_cr: bool = False
    exact_flatness: bool = False
    learned_intertwiner: bool = False
    semantic_flatness: bool = False

    def validate(self) -> None:
        if self.architecture not in {"polar", "hard_kernel"}:
            raise ValueError(f"unknown v0.6 architecture: {self.architecture}")
        flags = (self.exact_flatness, self.learned_intertwiner, self.semantic_flatness)
        if sum(bool(value) for value in flags) > 1:
            raise ValueError("v0.6 auxiliary mechanisms must be isolated by arm")
        if self.learned_intertwiner and self.architecture != "polar":
            raise ValueError("the learned observer requires the unrestricted polar model")
        if self.semantic_flatness and self.architecture != "hard_kernel":
            raise ValueError("semantic flatness requires the hard-kernel model")
        if self.legacy_cr and any(flags):
            raise ValueError("the legacy CR comparator cannot receive v0.6 objectives")


INVARIANT_KERNEL_ARMS: Mapping[str, InvariantKernelArmSpec] = {
    "polar_supervised": InvariantKernelArmSpec("polar_supervised"),
    "polar_cr": InvariantKernelArmSpec("polar_cr", legacy_cr=True),
    "polar_exact": InvariantKernelArmSpec("polar_exact", exact_flatness=True),
    "learned_intertwiner": InvariantKernelArmSpec(
        "learned_intertwiner", learned_intertwiner=True
    ),
    "hard_kernel_supervised": InvariantKernelArmSpec(
        "hard_kernel_supervised", architecture="hard_kernel"
    ),
    "hard_kernel_semantic_flat": InvariantKernelArmSpec(
        "hard_kernel_semantic_flat",
        architecture="hard_kernel",
        semantic_flatness=True,
    ),
}

PRIMARY_INVARIANT_KERNEL_ARMS: tuple[str, ...] = tuple(INVARIANT_KERNEL_ARMS)


def regular_simplex_chart(
    *,
    dtype: torch.dtype = torch.float32,
    device: torch.device | str | None = None,
) -> torch.Tensor:
    """Return a deterministic ``7 x 8`` Helmert contrast chart.

    Its rows are orthonormal, its row sums vanish, and ``S.T @ S`` is the
    eight-class centering matrix.  The chart therefore represents exactly the
    seven behaviorally identifiable logit contrasts; the missing direction is
    the common-logit gauge.
    """

    if not isinstance(dtype, torch.dtype) or not dtype.is_floating_point:
        raise TypeError("dtype must be a floating torch dtype")
    result = torch.zeros(OBSERVER_DIM, N_STATES, dtype=dtype, device=device)
    for row in range(OBSERVER_DIM):
        denominator = math.sqrt((row + 1) * (row + 2))
        result[row, : row + 1] = 1.0 / denominator
        result[row, row + 1] = -(row + 1) / denominator
    return result


@dataclass(frozen=True)
class InvariantKernelLossWeights:
    """Developmental coefficients; every auxiliary term is linearly warmed."""

    exact_flatness: float = 0.30
    observer_anchor_geometry: float = 0.10
    observer_centered_readout: float = 1.00
    observer_intertwining: float = 10.00
    observer_semantic_relation: float = 0.30
    hard_semantic_flatness: float = 0.30

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"loss weight {name} must be finite and positive")


@dataclass(frozen=True)
class InvariantKernelTrainConfig:
    """Configuration shared across the six paired v0.6 arms."""

    seed: int
    steps: int
    batch_size: int
    train_max_length: int = 4
    hidden_dim: int = 12
    learning_rate: float = 2e-3
    weight_decay: float = 1e-6
    grad_clip: float = 5.0
    warmup_steps: int = 200
    auxiliary_delay_steps: int = 800
    auxiliary_ramp_end_step: int = 1600
    auxiliary_contexts: int = 8
    construction_words_per_step: int = 4
    relation_cells_per_step: int = RELATION_CELL_COUNT
    episode_seed_base: int = 50_000
    gauge_seed_base: int = 60_700
    ambient_seed_base: int = 61_700
    checkpoints: int = 9
    device: str = "cpu"
    base_weights: PacketClosureLossWeights = field(default_factory=PacketClosureLossWeights)
    weights: InvariantKernelLossWeights = field(default_factory=InvariantKernelLossWeights)

    def validate(self) -> None:
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise TypeError("seed must be an integer")
        for name in (
            "steps",
            "batch_size",
            "train_max_length",
            "auxiliary_contexts",
            "construction_words_per_step",
            "relation_cells_per_step",
            "checkpoints",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        for name in ("episode_seed_base", "gauge_seed_base", "ambient_seed_base"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
        if self.hidden_dim != 12:
            raise ValueError("v0.6 requires hidden_dim == 12")
        if self.auxiliary_contexts > self.batch_size:
            raise ValueError("auxiliary_contexts cannot exceed batch_size")
        if self.relation_cells_per_step != RELATION_CELL_COUNT:
            raise ValueError("v0.6 requires all nine relation cells at every step")
        for name in ("learning_rate", "grad_clip"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
        if not math.isfinite(self.weight_decay) or self.weight_decay < 0.0:
            raise ValueError("weight_decay must be finite and nonnegative")
        for name in ("warmup_steps", "auxiliary_delay_steps", "auxiliary_ramp_end_step"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
        if self.warmup_steps < 0:
            raise ValueError("warmup_steps must be nonnegative")
        if self.auxiliary_delay_steps < 0:
            raise ValueError("auxiliary_delay_steps must be nonnegative")
        if self.auxiliary_ramp_end_step <= self.auxiliary_delay_steps:
            raise ValueError(
                "auxiliary_ramp_end_step must be greater than auxiliary_delay_steps"
            )
        if not isinstance(self.device, str) or not self.device:
            raise ValueError("device must be a nonempty string")
        self.base_weights.validate()
        self.weights.validate()

    def base_config(self) -> PacketClosureTrainConfig:
        self.validate()
        return PacketClosureTrainConfig(
            seed=self.seed,
            steps=self.steps,
            batch_size=self.batch_size,
            train_max_length=self.train_max_length,
            hidden_dim=self.hidden_dim,
            learning_rate=self.learning_rate,
            weight_decay=self.weight_decay,
            grad_clip=self.grad_clip,
            warmup_steps=self.warmup_steps,
            auxiliary_contexts=self.auxiliary_contexts,
            construction_words_per_step=self.construction_words_per_step,
            episode_seed_base=self.episode_seed_base,
            checkpoints=self.checkpoints,
            device=self.device,
            weights=self.base_weights,
        )


class LinearPolarTableOperatorRNN(PolarIsometricTableOperatorRNN):
    """Hard-polar table model with truly linear executed recurrence.

    The inherited projective implementation divides by a global hidden norm
    inside ``_rollout``.  That division is redundant on natural trajectories
    because every executed operator is orthogonal, but it couples a causal
    kernel injection into observable logit scale.  This shared base removes
    that coupling for *all* v0.6 polar arms while retaining a fully compatible
    :class:`PacketRunTrace`.  Radial values are diagnostic norms, not removed
    scales.
    """

    model_name = "linear_polar_isometric_table"
    projective_normalization = False

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return self.linear_step(hidden, code)

    def _rollout(
        self,
        hidden: torch.Tensor,
        operator_matrices: torch.Tensor,
        op_slots: torch.Tensor,
        *,
        raw_operator_matrices: torch.Tensor | None,
        residual_operator_matrices: torch.Tensor | None,
    ) -> PacketRunTrace:
        """Execute direct polar recurrence while retaining radial diagnostics."""

        metric = self.invariant_metric()
        self._validate_rollout_inputs(operator_matrices, op_slots, hidden)
        batch = hidden.shape[0]
        rows = torch.arange(batch, device=hidden.device)
        trajectory = [hidden]
        proposals: list[torch.Tensor] = []
        radial_norms: list[torch.Tensor] = []
        selected: list[torch.Tensor] = []

        for time_index in range(op_slots.shape[1]):
            code = operator_matrices[rows, op_slots[:, time_index]]
            proposal = self.linear_step(hidden, code)
            radius = self.hidden_norm(proposal, metric)
            hidden = proposal
            selected.append(code)
            proposals.append(proposal)
            radial_norms.append(radius)
            trajectory.append(hidden)

        if selected:
            selected_tensor = torch.stack(selected, dim=1)
            radius_tensor = torch.stack(radial_norms, dim=1)
        else:
            selected_tensor = operator_matrices.new_empty(
                (batch, 0, self.hidden_dim, self.hidden_dim)
            )
            radius_tensor = operator_matrices.new_empty((batch, 0))

        return PacketRunTrace(
            logits=self.decode_hidden(hidden),
            hidden=trajectory,
            operator_codes=operator_matrices,
            raw_operator_matrices=raw_operator_matrices,
            residual_operator_matrices=residual_operator_matrices,
            selected_operator_matrices=selected_tensor,
            pre_normalized_hidden=proposals,
            radial_norms=radius_tensor,
            metric=metric,
        )


class LearnedIntertwinerPolarRNN(LinearPolarTableOperatorRNN):
    """Unrestricted polar recurrence with a non-constructive rank-seven observer.

    The only additional learned tensor is ``observer_raw``.  QR retraction of
    its transpose yields a row-orthonormal ``Pi``.  There are intentionally no
    free ``C`` or ``T`` parameters: both are induced from the executed decoder
    and recurrent operators, preventing an auxiliary head from laundering
    violations of the claimed quotient structure.
    """

    model_name = "polar_isometric_learned_intertwiner"

    def __init__(self, hidden_dim: int = 12, observer_dim: int = OBSERVER_DIM) -> None:
        if observer_dim != OBSERVER_DIM:
            raise ValueError(f"v0.6 observer_dim must equal {OBSERVER_DIM}")
        super().__init__(hidden_dim=hidden_dim)
        self.observer_dim = int(observer_dim)
        centering = torch.eye(N_STATES) - torch.ones(N_STATES, N_STATES) / N_STATES
        self.register_buffer("_logit_centering", centering, persistent=False)
        # Initialize the auxiliary observer from what is *already* observable
        # at the output boundary.  For eight logits, J @ D has rank at most
        # seven and its right singular frame is a coordinate-free estimate of
        # the instantaneous observable subspace.  No operator table, target,
        # group element, or continuation is consulted.  Training must still
        # discover whether this instantaneous kernel can be made forward
        # invariant under every learned recurrent operator.  In particular,
        # neither this initialization nor the anchor-Gram objective selects a
        # target basis inside the seven-dimensional quotient.
        with torch.no_grad():
            centered = self._logit_centering @ self.decoder.weight
            _, singular, right = torch.linalg.svd(centered, full_matrices=False)
            if singular.numel() < self.observer_dim or not bool(
                torch.isfinite(singular).all()
            ):
                raise RuntimeError("initial centered readout has invalid rank data")
            initial = right[: self.observer_dim].clone()
        self.observer_raw = nn.Parameter(initial)

    def observer_matrix(self) -> torch.Tensor:
        """Return row-orthonormal ``Pi`` with shape ``(7, 12)``."""

        orthonormal_columns, _ = torch.linalg.qr(
            self.observer_raw.transpose(-1, -2), mode="reduced"
        )
        return orthonormal_columns.transpose(-1, -2)

    def observer_projector(self) -> torch.Tensor:
        observer = self.observer_matrix()
        return observer.transpose(-1, -2) @ observer

    def induced_semantic_operators(self, operator_codes: torch.Tensor) -> torch.Tensor:
        if operator_codes.ndim < 2 or operator_codes.shape[-2:] != (
            self.hidden_dim,
            self.hidden_dim,
        ):
            raise ValueError("operator_codes must end in (hidden_dim, hidden_dim)")
        observer = self.observer_matrix()
        return observer @ operator_codes @ observer.transpose(-1, -2)

    def centered_decoder(self) -> torch.Tensor:
        return self._logit_centering.to(dtype=self.decoder.weight.dtype) @ self.decoder.weight

    def induced_centered_readout(self) -> torch.Tensor:
        """Return ``C = J D Pi.T``; this is derived, not a free head."""

        return self.centered_decoder() @ self.observer_matrix().transpose(-1, -2)


@dataclass(frozen=True)
class LearnedIntertwinerLosses:
    anchor_geometry: torch.Tensor
    centered_readout: torch.Tensor
    intertwining: torch.Tensor
    semantic_relation: torch.Tensor
    observer_orthogonality: torch.Tensor


@dataclass(frozen=True)
class RelationContextPlan:
    """Deterministic relation banks for the paired prefix of one batch.

    The selected rows are fixed before arm-specific objectives are inspected.
    Keeping the banks in one immutable object lets optimization and provenance
    consume exactly the same visible presentations.
    """

    indices: tuple[int, ...]
    banks: tuple[RelationCellBank, ...]


@dataclass(frozen=True)
class InvariantKernelLosses:
    total: torch.Tensor
    base: PacketClosureLossResult
    exact_flatness: torch.Tensor
    observer_anchor_geometry: torch.Tensor
    observer_centered_readout: torch.Tensor
    observer_intertwining: torch.Tensor
    observer_semantic_relation: torch.Tensor
    observer_orthogonality: torch.Tensor
    hard_semantic_flatness: torch.Tensor
    auxiliary_multiplier: float
    auxiliary_delay_steps: int
    auxiliary_ramp_end_step: int
    relation_context_indices: tuple[int, ...]
    relation_cell_indices: tuple[int, ...]
    relation_cells_per_context: int
    relation_cells_total: int

    @property
    def warmup(self) -> float:
        """Compatibility alias for the v0.6 auxiliary multiplier."""

        return self.auxiliary_multiplier


@dataclass
class TrainedInvariantKernelArm:
    arm: InvariantKernelArmSpec
    config: InvariantKernelTrainConfig
    model: RecurrentOperatorModel
    trajectory: list[dict[str, Any]]
    elapsed_seconds: float
    final_loss: float
    parameter_count: int
    trainable_parameter_count: int
    initial_state_digest: str
    core_initial_state_digest: str
    final_state_digest: str
    episode_stream_digest: str
    terminal_proposal_stream_digest: str
    relation_schedule_digest: str
    terminal_firewall_policy_digest: str
    terminal_proposal_count: int
    terminal_candidates_accepted: int
    terminal_candidates_rejected: int
    terminal_identity_rejections: int
    terminal_r2_rejections: int
    construction_digest: str
    construction_words: tuple[tuple[int, ...], ...]
    ambient_initial_digest: str | None
    ambient_final_digest: str | None
    plan_version: str = V06_PLAN_VERSION


def get_invariant_kernel_arm(
    arm: str | InvariantKernelArmSpec,
) -> InvariantKernelArmSpec:
    if isinstance(arm, InvariantKernelArmSpec):
        arm.validate()
        return arm
    try:
        result = INVARIANT_KERNEL_ARMS[arm]
    except KeyError as error:
        raise ValueError(f"unknown v0.6 arm: {arm}") from error
    result.validate()
    return result


def _base_arm_spec(spec: InvariantKernelArmSpec) -> PacketClosureArmSpec:
    return PacketClosureArmSpec(
        name=spec.name,
        learn_metric=False,
        composition=spec.legacy_cr,
        margin=False,
        conformal=False,
        switched_gain=False,
        delayed_return=spec.legacy_cr,
        model_family="polar",
    )


def _tensor_digest(name: str, tensor: torch.Tensor) -> str:
    digest = hashlib.sha256()
    local = tensor.detach().to(device="cpu").contiguous()
    digest.update(name.encode("utf-8"))
    digest.update(str(local.dtype).encode("ascii"))
    digest.update(json.dumps(list(local.shape), separators=(",", ":")).encode("ascii"))
    digest.update(local.numpy().tobytes())
    return digest.hexdigest()


def _core_state_digest(model: RecurrentOperatorModel) -> str:
    """Hash comparable task tensors while excluding observer-only state."""

    excluded = {"observer_raw", "_logit_centering"}
    digest = hashlib.sha256()
    included = 0
    for name, tensor in sorted(model.state_dict().items()):
        if name in excluded:
            continue
        local = tensor.detach().to(device="cpu").contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(local.dtype).encode("ascii"))
        digest.update(json.dumps(list(local.shape), separators=(",", ":")).encode("ascii"))
        digest.update(local.numpy().tobytes())
        included += 1
    if not included:
        raise RuntimeError("v0.6 model exposes no core state tensors")
    return digest.hexdigest()


def build_invariant_kernel_model(
    config: InvariantKernelTrainConfig,
    arm: str | InvariantKernelArmSpec,
) -> RecurrentOperatorModel:
    """Build an exactly reproducible v0.6 model without touching data RNGs."""

    config.validate()
    spec = get_invariant_kernel_arm(arm)
    torch.manual_seed(config.seed)
    if spec.architecture == "polar":
        if spec.learned_intertwiner:
            return LearnedIntertwinerPolarRNN(hidden_dim=config.hidden_dim)
        return LinearPolarTableOperatorRNN(hidden_dim=config.hidden_dim)

    model = LearnedFrameBlockIsometricOperatorRNN(
        hidden_dim=config.hidden_dim,
        semantic_dim=OBSERVER_DIM,
        gauge_seed=config.gauge_seed_base + config.seed,
    )
    # The fiber is a fixed random comparator.  Because anchors have exactly
    # zero fiber coordinate and the direct sum forbids cross-block transport,
    # this block is dormant under the task objective.
    generator = torch.Generator(device="cpu").manual_seed(
        config.ambient_seed_base + config.seed
    )
    with torch.no_grad():
        model.ambient_operator_encoder.weight.normal_(
            mean=0.0,
            std=0.02,
            generator=generator,
        )
    model.ambient_operator_encoder.weight.requires_grad_(False)
    return model


def _mean_square(value: torch.Tensor) -> torch.Tensor:
    if value.numel() == 0:
        raise ValueError("cannot measure an empty residual")
    return value.square().mean()


def relation_product_loss(
    operator_codes: torch.Tensor,
    pairs: Sequence[tuple[Sequence[int], Sequence[int]]],
) -> torch.Tensor:
    """v0.5-normalized equality residual for anonymous path products.

    This retains the inherited normalization: mean squared Frobenius residual
    across cells divided by ``4 * dimension``.  Keeping that scale fixed makes
    the ``polar_exact`` coefficient directly comparable with v0.5.
    """

    if operator_codes.ndim != 3 or operator_codes.shape[0] != 2:
        raise ValueError("operator_codes must have shape (2, dimension, dimension)")
    if operator_codes.shape[-1] != operator_codes.shape[-2]:
        raise ValueError("operator_codes must end in square dimensions")
    if not pairs:
        raise ValueError("pairs must be nonempty")
    residuals = [
        _ordered_product(operator_codes, left)
        - _ordered_product(operator_codes, right)
        for left, right in pairs
    ]
    stacked = torch.stack(residuals)
    dimension = operator_codes.shape[-1]
    return stacked.square().sum(dim=(-2, -1)).mean() / (4.0 * dimension)


def build_relation_context_plan(
    batch: EpisodeBatch,
    contexts: int,
) -> RelationContextPlan:
    """Select the fixed paired prefix and derive every context's own cell bank.

    Accepted rows are exchangeable samples of visible coordinate systems.  A
    deterministic prefix therefore avoids another RNG stream while remaining
    an unbiased sample of the conditional training distribution.  Truncation
    is forbidden: the registered number of contexts must actually be present.
    """

    if not isinstance(batch, EpisodeBatch):
        raise TypeError("batch must be an EpisodeBatch")
    if isinstance(contexts, bool) or not isinstance(contexts, int):
        raise TypeError("contexts must be an integer")
    if contexts < 1:
        raise ValueError("contexts must be positive")
    if batch.family != "d4":
        raise ValueError("v0.6 relation contexts require D4 episodes")
    if batch.maps.ndim != 3 or batch.maps.shape[1:] != (2, N_STATES):
        raise ValueError("batch maps must have shape (batch, 2, 8)")
    available = int(batch.maps.shape[0])
    if available < contexts:
        raise ValueError(
            f"registered auxiliary_contexts={contexts} exceeds batch rows={available}"
        )
    indices = tuple(range(contexts))
    banks = tuple(relation_cell_bank(batch.maps[index]) for index in indices)
    if any(len(bank.cells) != RELATION_CELL_COUNT for bank in banks):
        raise RuntimeError("a relation context no longer contains all nine cells")
    return RelationContextPlan(indices=indices, banks=banks)


def mean_relation_product_loss(
    operator_codes: torch.Tensor,
    pairs_by_context: Sequence[
        Sequence[tuple[Sequence[int], Sequence[int]]]
    ],
) -> torch.Tensor:
    """Average normalized relation loss across paired visible contexts."""

    if operator_codes.ndim != 4 or operator_codes.shape[1] != 2:
        raise ValueError(
            "operator_codes must have shape (contexts, 2, dimension, dimension)"
        )
    if operator_codes.shape[-1] != operator_codes.shape[-2]:
        raise ValueError("operator_codes must end in square dimensions")
    if len(pairs_by_context) != int(operator_codes.shape[0]):
        raise ValueError("one relation-pair bank is required per operator context")
    losses = [
        relation_product_loss(operator_codes[index], pairs)
        for index, pairs in enumerate(pairs_by_context)
    ]
    if not losses:
        raise ValueError("at least one relation context is required")
    return torch.stack(losses).mean()


def learned_intertwiner_losses(
    model: LearnedIntertwinerPolarRNN,
    operator_codes: torch.Tensor,
    pairs_by_context: Sequence[
        Sequence[tuple[Sequence[int], Sequence[int]]]
    ],
) -> LearnedIntertwinerLosses:
    """Compute induced quotient residuals without independent C/T escape routes."""

    if not isinstance(model, LearnedIntertwinerPolarRNN):
        raise TypeError("learned intertwiner losses require LearnedIntertwinerPolarRNN")
    if operator_codes.ndim != 4 or operator_codes.shape[1:] != (
        2,
        model.hidden_dim,
        model.hidden_dim,
    ):
        raise ValueError("operator_codes must have shape (contexts, 2, 12, 12)")
    if len(pairs_by_context) != int(operator_codes.shape[0]):
        raise ValueError("one relation-pair bank is required per operator context")
    observer = model.observer_matrix()
    observer_projector = observer.transpose(-1, -2) @ observer
    identity_hidden = torch.eye(
        model.hidden_dim,
        dtype=observer.dtype,
        device=observer.device,
    )
    kernel_projector = identity_hidden - observer_projector
    anchors = model.state_anchors().transpose(-1, -2)
    observed_anchors = observer @ anchors
    anchor_gram = observed_anchors.transpose(-1, -2) @ observed_anchors
    target_gram = model._logit_centering.to(
        dtype=anchors.dtype,
        device=anchors.device,
    )
    anchor_geometry = (anchor_gram - target_gram).square().sum() / model.observer_dim

    centered_decoder = model.centered_decoder()
    induced_readout = model.induced_centered_readout()
    readout_residual = centered_decoder - induced_readout @ observer
    readout_denominator = centered_decoder.square().sum().detach() + 1e-4
    centered_readout = readout_residual.square().sum() / readout_denominator

    semantic_codes = model.induced_semantic_operators(operator_codes)
    observer_batched = observer.view(1, 1, model.observer_dim, model.hidden_dim)
    kernel_batched = kernel_projector.view(
        1, 1, model.hidden_dim, model.hidden_dim
    )
    observer_transpose_batched = observer.transpose(-1, -2).view(
        1, 1, model.hidden_dim, model.observer_dim
    )
    forward_leakage = observer_batched @ operator_codes @ kernel_batched
    reverse_leakage = (
        kernel_batched @ operator_codes @ observer_transpose_batched
    )
    intertwining = (
        forward_leakage.square().sum(dim=(-2, -1))
        + reverse_leakage.square().sum(dim=(-2, -1))
    ).mean() / (2.0 * model.observer_dim)
    semantic_relation = mean_relation_product_loss(
        semantic_codes,
        pairs_by_context,
    )
    identity = torch.eye(
        model.observer_dim,
        dtype=observer.dtype,
        device=observer.device,
    )
    observer_orthogonality = _mean_square(observer @ observer.transpose(-1, -2) - identity)

    # Keep the equivalent projector form observable in autograd/debuggers.  It
    # is algebraically the same residual as Pi M (I - Pi.T Pi).
    if observer_projector.shape != (model.hidden_dim, model.hidden_dim):
        raise RuntimeError("observer projector has an invalid shape")
    return LearnedIntertwinerLosses(
        anchor_geometry=anchor_geometry,
        centered_readout=centered_readout,
        intertwining=intertwining,
        semantic_relation=semantic_relation,
        observer_orthogonality=observer_orthogonality,
    )


def auxiliary_schedule_multiplier(
    step: int,
    delay_steps: int,
    ramp_end_step: int,
) -> float:
    """Delay v0.6 constraints, then linearly ramp by completed step count.

    With the default ``(800, 1600)`` schedule the multiplier is zero through
    completed step 800, equals ``1/800`` at completed step 801, and reaches one
    at completed step 1600.  This schedule is independent of the inherited base
    structural warmup.
    """

    if isinstance(step, bool) or not isinstance(step, int) or step < 0:
        raise ValueError("step must be a nonnegative integer")
    for name, value in (("delay_steps", delay_steps), ("ramp_end_step", ramp_end_step)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
    if delay_steps < 0:
        raise ValueError("delay_steps must be nonnegative")
    if ramp_end_step <= delay_steps:
        raise ValueError("ramp_end_step must be greater than delay_steps")
    completed_step = step + 1
    if completed_step <= delay_steps:
        return 0.0
    if completed_step >= ramp_end_step:
        return 1.0
    return (completed_step - delay_steps) / (ramp_end_step - delay_steps)


def compute_invariant_kernel_losses(
    model: RecurrentOperatorModel,
    batch: EpisodeBatch,
    construction: V04ConstructionBank,
    arm: str | InvariantKernelArmSpec,
    config: InvariantKernelTrainConfig,
    *,
    step: int,
    relation_plan: RelationContextPlan | None = None,
) -> InvariantKernelLosses:
    """Compute one v0.6 objective from the paired v0.5-compatible streams."""

    config.validate()
    spec = get_invariant_kernel_arm(arm)
    if getattr(model, "hidden_dim", None) != config.hidden_dim:
        raise ValueError("model hidden dimension does not match config")
    if spec.learned_intertwiner != isinstance(model, LearnedIntertwinerPolarRNN):
        raise TypeError("model does not match the learned-intertwiner arm")
    if spec.architecture == "polar" and not isinstance(
        model, PolarIsometricTableOperatorRNN
    ):
        raise TypeError("unrestricted v0.6 arms require the hard-polar architecture")
    if (spec.architecture == "hard_kernel") != isinstance(
        model, LearnedFrameBlockIsometricOperatorRNN
    ):
        raise TypeError("model does not match the requested v0.6 architecture")

    base = compute_packet_closure_losses(
        model,
        batch,
        construction,
        _base_arm_spec(spec),
        config.base_config(),
        step=step,
    )
    if relation_plan is None:
        relation_plan = build_relation_context_plan(
            batch,
            config.auxiliary_contexts,
        )
    expected_context_indices = tuple(range(config.auxiliary_contexts))
    if relation_plan.indices != expected_context_indices:
        raise ValueError("relation plan does not use the registered paired prefix")
    if len(relation_plan.banks) != config.auxiliary_contexts:
        raise ValueError("relation plan context count does not match config")
    pairs_by_context = tuple(bank.cells for bank in relation_plan.banks)
    cell_indices = tuple(range(len(pairs_by_context[0])))
    if len(cell_indices) != config.relation_cells_per_step:
        raise RuntimeError("relation bank no longer matches the v0.6 contract")
    if any(len(pairs) != len(cell_indices) for pairs in pairs_by_context):
        raise RuntimeError("relation plan does not expose all cells in every context")

    codes = model.encode_operators(batch.tables[: config.auxiliary_contexts])
    zero = base.total * 0.0
    exact = zero
    observer_losses = LearnedIntertwinerLosses(zero, zero, zero, zero, zero)
    hard_semantic = zero
    if spec.exact_flatness:
        exact = mean_relation_product_loss(codes, pairs_by_context)
    if spec.learned_intertwiner:
        assert isinstance(model, LearnedIntertwinerPolarRNN)
        observer_losses = learned_intertwiner_losses(
            model,
            codes,
            pairs_by_context,
        )
    if spec.semantic_flatness:
        assert isinstance(model, LearnedFrameBlockIsometricOperatorRNN)
        semantic_codes = model.encode_operator_bundle(
            batch.tables[: config.auxiliary_contexts]
        ).semantic_blocks
        hard_semantic = mean_relation_product_loss(
            semantic_codes,
            pairs_by_context,
        )

    auxiliary_multiplier = auxiliary_schedule_multiplier(
        step,
        config.auxiliary_delay_steps,
        config.auxiliary_ramp_end_step,
    )
    weights = config.weights
    auxiliary = (
        weights.exact_flatness * exact
        + weights.observer_anchor_geometry * observer_losses.anchor_geometry
        + weights.observer_centered_readout * observer_losses.centered_readout
        + weights.observer_intertwining * observer_losses.intertwining
        + weights.observer_semantic_relation * observer_losses.semantic_relation
        + weights.hard_semantic_flatness * hard_semantic
    )
    return InvariantKernelLosses(
        total=base.total + auxiliary_multiplier * auxiliary,
        base=base,
        exact_flatness=exact,
        observer_anchor_geometry=observer_losses.anchor_geometry,
        observer_centered_readout=observer_losses.centered_readout,
        observer_intertwining=observer_losses.intertwining,
        observer_semantic_relation=observer_losses.semantic_relation,
        observer_orthogonality=observer_losses.observer_orthogonality,
        hard_semantic_flatness=hard_semantic,
        auxiliary_multiplier=auxiliary_multiplier,
        auxiliary_delay_steps=config.auxiliary_delay_steps,
        auxiliary_ramp_end_step=config.auxiliary_ramp_end_step,
        relation_context_indices=relation_plan.indices,
        relation_cell_indices=cell_indices,
        relation_cells_per_context=len(cell_indices),
        relation_cells_total=len(relation_plan.indices) * len(cell_indices),
    )


def _update_tensor_digest(digest: "hashlib._Hash", tensor: torch.Tensor) -> None:
    local = tensor.detach().to(device="cpu").contiguous()
    digest.update(str(local.dtype).encode("ascii"))
    digest.update(json.dumps(list(local.shape), separators=(",", ":")).encode("ascii"))
    digest.update(local.numpy().tobytes())


def _update_episode_digest(digest: "hashlib._Hash", batch: EpisodeBatch, step: int) -> None:
    digest.update(int(step).to_bytes(8, "little", signed=False))
    digest.update(batch.family.encode("ascii"))
    for tensor in (
        batch.tables,
        batch.maps,
        batch.op_slots,
        batch.canonical_ops,
        batch.start,
        batch.target,
        batch.intermediates,
        batch.canonical_to_slot,
        batch.phi,
    ):
        _update_tensor_digest(digest, tensor)


def _update_relation_schedule_digest(
    digest: "hashlib._Hash",
    plan: RelationContextPlan,
    *,
    step: int,
) -> None:
    """Bind the receipt to every selected context and its exact cell bank."""

    digest.update(int(step).to_bytes(8, "little", signed=False))
    digest.update(len(plan.indices).to_bytes(4, "little", signed=False))
    for index, bank in zip(plan.indices, plan.banks, strict=True):
        digest.update(int(index).to_bytes(4, "little", signed=False))
        digest.update(bank.fingerprint.encode("ascii"))
        digest.update(len(bank.cells).to_bytes(4, "little", signed=False))
        digest.update(json.dumps(bank.cells, separators=(",", ":")).encode("ascii"))


def _trajectory_row(
    losses: InvariantKernelLosses,
    *,
    step: int,
    length: int,
    gradient_norm: float,
) -> dict[str, Any]:
    return {
        "step": step + 1,
        "length": length,
        "loss": float(losses.total.detach()),
        "terminal_loss": float(losses.base.terminal.detach()),
        "construction_ce_loss": float(losses.base.construction_ce.detach()),
        "legacy_composition_loss": float(losses.base.composition.detach()),
        "legacy_delayed_return_loss": float(losses.base.delayed_return.detach()),
        "exact_flatness_loss": float(losses.exact_flatness.detach()),
        "observer_anchor_geometry_loss": float(
            losses.observer_anchor_geometry.detach()
        ),
        "observer_centered_readout_loss": float(
            losses.observer_centered_readout.detach()
        ),
        "observer_intertwining_loss": float(losses.observer_intertwining.detach()),
        "observer_semantic_relation_loss": float(
            losses.observer_semantic_relation.detach()
        ),
        "observer_orthogonality_residual": float(
            losses.observer_orthogonality.detach()
        ),
        "hard_semantic_flatness_loss": float(losses.hard_semantic_flatness.detach()),
        "terminal_accuracy": float(losses.base.terminal_accuracy.detach()),
        "construction_accuracy": float(losses.base.construction_accuracy.detach()),
        "gradient_norm_before_clip": gradient_norm,
        "base_warmup": losses.base.warmup,
        "auxiliary_multiplier": losses.auxiliary_multiplier,
        "auxiliary_delay_steps": losses.auxiliary_delay_steps,
        "auxiliary_ramp_end_step": losses.auxiliary_ramp_end_step,
        "relation_context_indices": list(losses.relation_context_indices),
        "relation_cell_indices": list(losses.relation_cell_indices),
        "relation_cells_per_context": losses.relation_cells_per_context,
        "relation_cells_total": losses.relation_cells_total,
    }


def train_invariant_kernel_arm(
    arm: str | InvariantKernelArmSpec,
    config: InvariantKernelTrainConfig,
    *,
    model: RecurrentOperatorModel | None = None,
    construction: V04ConstructionBank | None = None,
) -> TrainedInvariantKernelArm:
    """Train one arm on a deterministic paired terminal/relation stream."""

    config.validate()
    spec = get_invariant_kernel_arm(arm)
    if model is None:
        model = build_invariant_kernel_model(config, spec)
    if not isinstance(model, RecurrentOperatorModel):
        raise TypeError("v0.6 arms require a RecurrentOperatorModel")
    if getattr(model, "hidden_dim", None) != config.hidden_dim:
        raise ValueError("provided model does not match the training configuration")
    construction = (
        make_v04_construction_bank(config.base_config().auxiliary_max_depth)
        if construction is None
        else construction
    )
    if not isinstance(construction, V04ConstructionBank):
        raise TypeError("training requires V04ConstructionBank, never an evaluation plan")
    safe_construction = construction_checkpoint_metadata(construction)

    initial_digest = state_dict_digest(model)
    core_initial_digest = _core_state_digest(model)
    ambient_initial: str | None = None
    ambient_parameter = getattr(
        getattr(model, "ambient_operator_encoder", None), "weight", None
    )
    if isinstance(ambient_parameter, torch.Tensor):
        if ambient_parameter.requires_grad:
            raise RuntimeError("hard-kernel ambient encoder must be frozen")
        ambient_initial = _tensor_digest("ambient_operator_encoder.weight", ambient_parameter)

    device = torch.device(config.device)
    model = model.to(device)
    model.train()
    optimizer = torch.optim.AdamW(
        packet_closure_optimizer_parameter_groups(model, config.base_config()),
        weight_decay=config.weight_decay,
    )
    trainable = tuple(parameter for parameter in model.parameters() if parameter.requires_grad)
    generator = EpisodeGenerator(config.episode_seed_base + config.seed)
    episode_digest = hashlib.sha256(b"v0.6-episode-stream")
    proposal_digest = hashlib.sha256(b"v0.6-terminal-proposal-stream")
    relation_digest = hashlib.sha256(b"v0.6-relation-schedule-dev2")
    checkpoints = set(
        np.linspace(
            0,
            config.steps - 1,
            num=min(config.checkpoints, config.steps),
            dtype=int,
        ).tolist()
    )
    trajectory: list[dict[str, Any]] = []
    accepted_total = 0
    rejected_total = 0
    proposal_total = 0
    identity_rejections = 0
    r2_rejections = 0
    firewall_digest = terminal_firewall_policy_digest()
    final_loss = math.nan
    started = time.perf_counter()
    for step in range(config.steps):
        length = int(generator.rng.integers(1, config.train_max_length + 1))
        sample = sample_v04_terminal_batch(generator, config.batch_size, length)
        if sample.policy_digest != firewall_digest:
            raise RuntimeError("terminal firewall policy changed within a v0.6 run")
        accepted_total += sample.accepted_count
        rejected_total += sample.rejected_count
        proposal_total += sample.proposal_count
        identity_rejections += sample.identity_rejection_count
        r2_rejections += sample.r2_rejection_count
        proposal_digest.update(int(step).to_bytes(8, "little", signed=False))
        proposal_digest.update(sample.proposal_digest.encode("ascii"))
        _update_episode_digest(episode_digest, sample.batch, step)

        relation_plan = build_relation_context_plan(
            sample.batch,
            config.auxiliary_contexts,
        )
        _update_relation_schedule_digest(
            relation_digest,
            relation_plan,
            step=step,
        )

        batch = sample.batch.to(device)
        optimizer.zero_grad(set_to_none=True)
        losses = compute_invariant_kernel_losses(
            model,
            batch,
            construction,
            spec,
            config,
            step=step,
            relation_plan=relation_plan,
        )
        if not bool(torch.isfinite(losses.total.detach())):
            raise FloatingPointError(f"non-finite v0.6 loss at step {step}")
        losses.total.backward()
        gradient_norm = float(torch.nn.utils.clip_grad_norm_(trainable, config.grad_clip))
        if not math.isfinite(gradient_norm):
            raise FloatingPointError(f"non-finite v0.6 gradient norm at step {step}")
        optimizer.step()
        final_loss = float(losses.total.detach())
        if step in checkpoints:
            trajectory.append(
                _trajectory_row(
                    losses,
                    step=step,
                    length=length,
                    gradient_norm=gradient_norm,
                )
            )

    elapsed = time.perf_counter() - started
    model.eval()
    ambient_final: str | None = None
    ambient_parameter = getattr(
        getattr(model, "ambient_operator_encoder", None), "weight", None
    )
    if isinstance(ambient_parameter, torch.Tensor):
        ambient_final = _tensor_digest("ambient_operator_encoder.weight", ambient_parameter)
        if ambient_initial != ambient_final:
            raise RuntimeError("frozen hard-kernel ambient encoder changed during training")
    return TrainedInvariantKernelArm(
        arm=spec,
        config=config,
        model=model,
        trajectory=trajectory,
        elapsed_seconds=elapsed,
        final_loss=final_loss,
        parameter_count=sum(parameter.numel() for parameter in model.parameters()),
        trainable_parameter_count=sum(
            parameter.numel() for parameter in model.parameters() if parameter.requires_grad
        ),
        initial_state_digest=initial_digest,
        core_initial_state_digest=core_initial_digest,
        final_state_digest=state_dict_digest(model),
        episode_stream_digest=episode_digest.hexdigest(),
        terminal_proposal_stream_digest=proposal_digest.hexdigest(),
        relation_schedule_digest=relation_digest.hexdigest(),
        terminal_firewall_policy_digest=firewall_digest,
        terminal_proposal_count=proposal_total,
        terminal_candidates_accepted=accepted_total,
        terminal_candidates_rejected=rejected_total,
        terminal_identity_rejections=identity_rejections,
        terminal_r2_rejections=r2_rejections,
        construction_digest=str(safe_construction["construction_digest"]),
        construction_words=construction.construction,
        ambient_initial_digest=ambient_initial,
        ambient_final_digest=ambient_final,
    )


def train_paired_invariant_kernel_panel(
    config: InvariantKernelTrainConfig,
    arm_names: Sequence[str] = PRIMARY_INVARIANT_KERNEL_ARMS,
) -> dict[str, TrainedInvariantKernelArm]:
    """Train requested arms independently on identical accepted/proposal streams."""

    names = tuple(arm_names)
    if not names or len(names) != len(set(names)):
        raise ValueError("arm_names must be nonempty and unique")
    specs = tuple(get_invariant_kernel_arm(name) for name in names)
    construction = make_v04_construction_bank(config.base_config().auxiliary_max_depth)
    results = {
        spec.name: train_invariant_kernel_arm(
            spec,
            config,
            construction=construction,
        )
        for spec in specs
    }
    for attribute in (
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "terminal_firewall_policy_digest",
        "terminal_proposal_count",
        "terminal_candidates_accepted",
        "terminal_candidates_rejected",
        "terminal_identity_rejections",
        "terminal_r2_rejections",
        "construction_digest",
        "construction_words",
    ):
        values = {getattr(result, attribute) for result in results.values()}
        if len(values) != 1:
            raise RuntimeError(f"paired v0.6 arms disagree on {attribute}")

    polar = [
        result
        for result in results.values()
        if result.arm.architecture == "polar"
    ]
    if len({result.core_initial_state_digest for result in polar}) > 1:
        raise RuntimeError("unrestricted polar arms did not share core initialization")
    hard = [
        result
        for result in results.values()
        if result.arm.architecture == "hard_kernel"
    ]
    if len({result.initial_state_digest for result in hard}) > 1:
        raise RuntimeError("hard-kernel arms did not share full initialization")
    return results


def invariant_kernel_checkpoint_metadata(
    trained: TrainedInvariantKernelArm,
) -> dict[str, Any]:
    """Return JSON-safe training provenance with no held-out evaluation data."""

    if not isinstance(trained, TrainedInvariantKernelArm):
        raise TypeError("trained must be a TrainedInvariantKernelArm")
    return {
        "plan_version": trained.plan_version,
        "arm": asdict(trained.arm),
        "config": asdict(trained.config),
        "model_class": type(trained.model).__name__,
        "parameter_count": trained.parameter_count,
        "trainable_parameter_count": trained.trainable_parameter_count,
        "initial_state_digest": trained.initial_state_digest,
        "core_initial_state_digest": trained.core_initial_state_digest,
        "final_state_digest": trained.final_state_digest,
        "episode_stream_digest": trained.episode_stream_digest,
        "terminal_proposal_stream_digest": trained.terminal_proposal_stream_digest,
        "relation_schedule_digest": trained.relation_schedule_digest,
        "terminal_firewall_policy_digest": trained.terminal_firewall_policy_digest,
        "terminal_counts": {
            "proposals": trained.terminal_proposal_count,
            "accepted": trained.terminal_candidates_accepted,
            "rejected": trained.terminal_candidates_rejected,
            "identity_rejections": trained.terminal_identity_rejections,
            "r2_rejections": trained.terminal_r2_rejections,
        },
        "construction": {
            "digest": trained.construction_digest,
            "words": [list(word) for word in trained.construction_words],
        },
        "ambient_encoder": {
            "frozen_random_dormant": trained.arm.architecture == "hard_kernel",
            "initial_digest": trained.ambient_initial_digest,
            "final_digest": trained.ambient_final_digest,
        },
        "hard_anchor_contract": (
            "orthogonal_anchor_completion_via_common_logit_gauge"
            if trained.arm.architecture == "hard_kernel"
            else None
        ),
        "auxiliary_schedule": {
            "delay_steps": trained.config.auxiliary_delay_steps,
            "ramp_end_step": trained.config.auxiliary_ramp_end_step,
            "base_warmup_steps": trained.config.warmup_steps,
            "base_warmup_is_independent": True,
        },
        "relation_exposure": {
            "selection": "first_n_accepted_rows_without_replacement",
            "contexts_per_step": trained.config.auxiliary_contexts,
            "cells_per_context": trained.config.relation_cells_per_step,
            "cells_per_step_total": (
                trained.config.auxiliary_contexts
                * trained.config.relation_cells_per_step
            ),
            "aggregation": "mean_over_contexts_and_cells_not_sum",
            "shared_across_arms": True,
        },
        "claim_boundary": {
            "explicit_pressure_only": True,
            "spontaneous_emergence": False,
            "anchor_geometry_is_supervised": trained.arm.learned_intertwiner,
            "observer_constructs_recurrence": False,
            "learned_intertwiner_projective_normalization": False,
            "ambient_fiber_is_useful_memory": False,
        },
    }


def invariant_kernel_training_contract(
    config: InvariantKernelTrainConfig,
) -> dict[str, Any]:
    """Return the JSON-safe developmental training contract."""

    config.validate()
    return {
        "plan_version": V06_PLAN_VERSION,
        "arms": [asdict(INVARIANT_KERNEL_ARMS[name]) for name in PRIMARY_INVARIANT_KERNEL_ARMS],
        "config": asdict(config),
        "stream_lineage": {
            "terminal": "v0.5-compatible D4 terminal stream with identity/r2 endpoint firewall",
            "construction": "v0.4 construction-only suffix bank",
            "relations": "all nine table-derived non-tree same-action cells",
        },
        "auxiliary_schedule": {
            "delay_steps": config.auxiliary_delay_steps,
            "ramp_end_step": config.auxiliary_ramp_end_step,
            "rule": (
                "zero through completed delay_steps; linear ramp thereafter; "
                "one at completed ramp_end_step"
            ),
            "base_warmup_steps": config.warmup_steps,
            "base_warmup_is_independent": True,
        },
        "relation_exposure": {
            "selection": "first_n_accepted_rows_without_replacement",
            "contexts_per_step": config.auxiliary_contexts,
            "cells_per_context": config.relation_cells_per_step,
            "cells_per_step_total": (
                config.auxiliary_contexts * config.relation_cells_per_step
            ),
            "aggregation": "mean_over_contexts_and_cells_not_sum",
            "shared_across_arms": True,
        },
        "learned_intertwiner": {
            "observer_rank": OBSERVER_DIM,
            "centered_null_rank": CENTERED_NULL_DIM,
            "row_orthonormal": True,
            "registered_anchor_geometry": (
                "basis-free 8x8 centered-simplex Gram I - 11^T/8 "
                "(explicit quotient-anchor geometry supervision)"
            ),
            "observer_initialization": (
                "instantaneous centered-readout rowspace only; no operator, "
                "target, continuation, or future-observability information"
            ),
            "semantic_operator": "T_g = Pi M_g Pi^T (induced, no free T head)",
            "centered_readout": "C = J D Pi^T (induced, no free C head)",
            "intertwining_residual": "Pi M_g - T_g Pi",
            "decoder_residual": "J D - C Pi",
            "loss_normalization": {
                "anchor_geometry": (
                    "||(Pi B)^T(Pi B) - (I_8 - 11^T/8)||_F^2 / 7"
                ),
                "centered_readout": (
                    "||J D Q||_F^2 / (stopgrad ||J D||_F^2 + 1e-4)"
                ),
                "two_way_intertwining": (
                    "mean_context,g (||Pi M_g Q||_F^2 + "
                    "||Q M_g Pi^T||_F^2) / 14"
                ),
                "semantic_relation": (
                    "context mean of mean-cell squared Frobenius / (4 * 7)"
                ),
            },
            "constructs_model": False,
            "rollout": (
                "direct linear polar recurrence; radial norms are diagnostic "
                "and are not divided out"
            ),
        },
        "hard_kernel": {
            "split": [OBSERVER_DIM, COMMON_LOGIT_DIM, AMBIENT_FIBER_DIM],
            "centered_null_rank": CENTERED_NULL_DIM,
            "global_frame": "fixed seeded orthogonal gauge",
            "ambient_encoder": "fixed seeded random and frozen",
            "ambient_state": "dormant under task initialization and direct-sum recurrence",
            "anchor_contract": "orthogonal_anchor_completion_via_common_logit_gauge",
            "semantic_relation_pressure": "anonymous same-action products in A_g",
        },
        "claim_boundary": "explicit-pressure developmental comparison only",
    }


__all__ = [
    "AMBIENT_FIBER_DIM",
    "CENTERED_NULL_DIM",
    "COMMON_LOGIT_DIM",
    "INVARIANT_KERNEL_ARMS",
    "OBSERVER_DIM",
    "PRIMARY_INVARIANT_KERNEL_ARMS",
    "V06_PLAN_VERSION",
    "InvariantKernelArmSpec",
    "InvariantKernelLossWeights",
    "InvariantKernelLosses",
    "InvariantKernelTrainConfig",
    "LearnedIntertwinerLosses",
    "LearnedIntertwinerPolarRNN",
    "LinearPolarTableOperatorRNN",
    "RelationContextPlan",
    "TrainedInvariantKernelArm",
    "build_relation_context_plan",
    "build_invariant_kernel_model",
    "auxiliary_schedule_multiplier",
    "compute_invariant_kernel_losses",
    "get_invariant_kernel_arm",
    "invariant_kernel_checkpoint_metadata",
    "invariant_kernel_training_contract",
    "learned_intertwiner_losses",
    "mean_relation_product_loss",
    "relation_product_loss",
    "regular_simplex_chart",
    "train_invariant_kernel_arm",
    "train_paired_invariant_kernel_panel",
]
