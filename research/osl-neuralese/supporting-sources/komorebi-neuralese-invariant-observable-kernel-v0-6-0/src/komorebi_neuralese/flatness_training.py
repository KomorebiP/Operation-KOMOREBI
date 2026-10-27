"""Training primitives for the v0.5 Flat Packet Connection experiment.

The v0.4 hard-polar model fixes every executed operator in ``O(12)``.  That
controls metric growth but leaves path-dependent angular holonomy.  This
module adds two deliberately distinct, anonymous relation objectives:

``exact``
    Equivalent paths must induce the same full twelve-dimensional operator.

``packet``
    Repeated relation holonomy must be invisible to a frozen decoder observer
    after every anonymous BFS normal-form suffix.  The observer is detached so
    it cannot move to conceal relation residue.

The relation cells are derived from the visible integer operator tables.  No
canonical D4 name, relation label, conjugating permutation, or generator-slot
alignment is passed to the model.  This is explicit anonymous relation
supervision, not spontaneous relation discovery.

The inherited v0.4 label firewall remains active: terminal and construction
cross-entropy never use identity or r^2 endpoint-action groups.  The flatness
losses do expose short same-action path pairs, so v0.5 claims only transfer to
held-out *derived consequences*, not structurally unseen relations.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import time
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import torch
from torch import nn

from .algebra import N_STATES
from .data import EpisodeBatch, EpisodeGenerator
from .packet_closure_train import (
    PacketClosureArmSpec,
    PacketClosureLossResult,
    PacketClosureTrainConfig,
    V04ConstructionBank,
    build_packet_closure_model,
    compute_packet_closure_losses,
    make_v04_construction_bank,
    packet_closure_optimizer_parameter_groups,
    sample_v04_terminal_batch,
    state_dict_digest,
)
from .packet_models import PolarIsometricTableOperatorRNN


V05_PLAN_VERSION = "v0.5-flat-packet-connection-v2"
TRAIN_PROBE_MAX_LENGTH = 3
RELATION_CELL_COUNT = 9
PACKET_SUFFIX_COUNT = N_STATES
PACKET_HOLONOMY_POWERS: tuple[int, ...] = (1, 2, 4, 8, 16)
PACKET_DELAY_STEPS = 400
PACKET_RAMP_END_STEP = 800
PACKET_DENOMINATOR_FLOOR = 1e-4


@dataclass(frozen=True)
class FlatnessArmSpec:
    """One supervision-matched v0.5 arm."""

    name: str
    exact_flatness: bool = False
    packet_flatness: bool = False
    shuffled_equivalence: bool = False
    legacy_cr: bool = False

    def validate(self) -> None:
        if self.shuffled_equivalence and not self.packet_flatness:
            raise ValueError("shuffled-equivalence arms require packet flatness")
        if self.legacy_cr and (
            self.exact_flatness or self.packet_flatness or self.shuffled_equivalence
        ):
            raise ValueError("the legacy CR comparator cannot receive v0.5 flatness losses")


FLATNESS_ARMS: Mapping[str, FlatnessArmSpec] = {
    "polar_supervised": FlatnessArmSpec("polar_supervised"),
    "polar_cr_v04": FlatnessArmSpec("polar_cr_v04", legacy_cr=True),
    "polar_exact_flat": FlatnessArmSpec("polar_exact_flat", exact_flatness=True),
    "polar_packet_flat": FlatnessArmSpec("polar_packet_flat", packet_flatness=True),
    "polar_hybrid_flat": FlatnessArmSpec(
        "polar_hybrid_flat", exact_flatness=True, packet_flatness=True
    ),
    "polar_shuffled_packet": FlatnessArmSpec(
        "polar_shuffled_packet",
        packet_flatness=True,
        shuffled_equivalence=True,
    ),
}

PRIMARY_FLATNESS_ARMS: tuple[str, ...] = tuple(FLATNESS_ARMS)


@dataclass(frozen=True)
class FlatnessTrainConfig:
    """Training configuration shared by all arms within one seed."""

    seed: int
    steps: int
    batch_size: int
    train_max_length: int = 4
    hidden_dim: int = 12
    learning_rate: float = 2e-3
    weight_decay: float = 1e-6
    grad_clip: float = 5.0
    warmup_steps: int = 200
    construction_words_per_step: int = 4
    relation_cells_per_step: int = RELATION_CELL_COUNT
    probes_per_step: int = PACKET_SUFFIX_COUNT
    exact_weight: float = 0.30
    packet_weight: float = 0.05
    episode_seed_base: int = 50_000
    checkpoints: int = 9
    device: str = "cpu"

    def validate(self) -> None:
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise TypeError("seed must be an integer")
        for name in (
            "steps",
            "batch_size",
            "train_max_length",
            "construction_words_per_step",
            "relation_cells_per_step",
            "probes_per_step",
            "checkpoints",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.hidden_dim != 12:
            raise ValueError("v0.5 requires a twelve-dimensional hard-polar model")
        if self.relation_cells_per_step != RELATION_CELL_COUNT:
            raise ValueError("v0.5-v2 requires all nine relation cells at every step")
        if self.probes_per_step != PACKET_SUFFIX_COUNT:
            raise ValueError("v0.5-v2 requires all eight BFS normal-form suffixes")
        for name in ("learning_rate", "grad_clip", "exact_weight", "packet_weight"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
        if not math.isfinite(self.weight_decay) or self.weight_decay < 0.0:
            raise ValueError("weight_decay must be finite and nonnegative")
        if self.warmup_steps < 0:
            raise ValueError("warmup_steps must be nonnegative")
        if not isinstance(self.device, str) or not self.device:
            raise ValueError("device must be a nonempty string")

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
            construction_words_per_step=self.construction_words_per_step,
            checkpoints=self.checkpoints,
            episode_seed_base=self.episode_seed_base,
            device=self.device,
        )


@dataclass(frozen=True)
class RelationCellBank:
    """The non-tree cells of a visible finite transformation Cayley graph."""

    normal_forms: tuple[tuple[int, ...], ...]
    signatures: tuple[tuple[int, ...], ...]
    cells: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]
    shuffled_cells: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]
    fingerprint: str


@dataclass(frozen=True)
class FlatnessLosses:
    total: torch.Tensor
    base: PacketClosureLossResult
    exact: torch.Tensor
    packet: torch.Tensor
    warmup: float
    packet_ramp: float
    cell_indices: tuple[int, ...]
    probe_indices: tuple[int, ...]


@dataclass
class TrainedFlatnessArm:
    arm: FlatnessArmSpec
    config: FlatnessTrainConfig
    model: PolarIsometricTableOperatorRNN
    trajectory: list[dict[str, Any]]
    elapsed_seconds: float
    final_loss: float
    parameter_count: int
    initial_state_digest: str
    final_state_digest: str
    episode_stream_digest: str
    terminal_proposal_stream_digest: str
    relation_schedule_digest: str
    terminal_proposal_count: int
    terminal_candidates_accepted: int
    terminal_candidates_rejected: int


def get_flatness_arm(name: str | FlatnessArmSpec) -> FlatnessArmSpec:
    if isinstance(name, FlatnessArmSpec):
        name.validate()
        return name
    try:
        result = FLATNESS_ARMS[name]
    except KeyError as error:
        raise ValueError(f"unknown v0.5 arm: {name}") from error
    result.validate()
    return result


def _integer_maps(maps: torch.Tensor | np.ndarray) -> np.ndarray:
    if isinstance(maps, torch.Tensor):
        local = maps.detach().to(device="cpu")
        if local.is_floating_point() or local.is_complex():
            raise TypeError("visible maps must have an integer dtype")
        array = local.numpy().astype(np.int64, copy=False)
    else:
        array = np.asarray(maps)
        if not np.issubdtype(array.dtype, np.integer):
            raise TypeError("visible maps must have an integer dtype")
        array = array.astype(np.int64, copy=False)
    if array.shape != (2, N_STATES):
        raise ValueError(f"visible maps must have shape (2, {N_STATES})")
    expected = np.arange(N_STATES)
    if not all(np.array_equal(np.sort(row), expected) for row in array):
        raise ValueError("each visible map must be a permutation")
    return array


def word_signature(
    maps: torch.Tensor | np.ndarray,
    word: Sequence[int],
) -> tuple[int, ...]:
    """Return the full induced permutation under the written application order."""

    array = _integer_maps(maps)
    current = np.arange(N_STATES, dtype=np.int64)
    for raw in word:
        if isinstance(raw, bool) or not isinstance(raw, (int, np.integer)):
            raise TypeError("word entries must be integers")
        action = int(raw)
        if action not in (0, 1):
            raise ValueError("word entries must be visible slots zero or one")
        current = array[action, current]
    return tuple(int(value) for value in current)


def relation_cell_bank(maps: torch.Tensor | np.ndarray) -> RelationCellBank:
    """Derive a relation-complete BFS cell bank from two visible tables.

    The eight D4 transformations are discovered by table action alone.  Each
    of the sixteen directed Cayley edges is compared with the BFS normal form
    of its endpoint.  Removing the seven tree edges leaves nine non-tree cells.
    """

    array = _integer_maps(maps)
    identity = tuple(range(N_STATES))
    representatives: dict[tuple[int, ...], tuple[int, ...]] = {identity: ()}
    queue: list[tuple[int, ...]] = [()]
    cursor = 0
    while cursor < len(queue):
        word = queue[cursor]
        cursor += 1
        for action in (0, 1):
            candidate = word + (action,)
            signature = word_signature(array, candidate)
            if signature not in representatives:
                representatives[signature] = candidate
                queue.append(candidate)
        if len(representatives) > 64:
            raise ValueError("visible tables generate more than the supported finite group")
    if len(representatives) != N_STATES:
        raise ValueError(
            f"v0.5 construction requires eight induced actions; found {len(representatives)}"
        )
    ordered = tuple(sorted(representatives.items(), key=lambda item: (len(item[1]), item[1])))
    cells: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for signature, normal in ordered:
        if word_signature(array, normal) != signature:
            raise RuntimeError("BFS normal form has the wrong induced action")
        for action in (0, 1):
            left = normal + (action,)
            right = representatives[word_signature(array, left)]
            if left != right:
                cells.append((left, right))
    cells_tuple = tuple(cells)
    if len(cells_tuple) != 9:
        raise ValueError(f"D4 relation cell bank must contain nine cells; found {len(cells_tuple)}")
    if any(word_signature(array, left) != word_signature(array, right) for left, right in cells_tuple):
        raise RuntimeError("relation cell bank contains a non-equivalent pair")

    # Derange the right branches while preserving their complete multiset.
    # This gives the false-equivalence arm identical path-length and token-load
    # distributions without ever supplying a true equality.
    right_branches = tuple(right for _, right in cells_tuple)
    candidates = {
        index: tuple(
            other
            for other in range(len(cells_tuple))
            if word_signature(array, cells_tuple[index][0])
            != word_signature(array, right_branches[other])
        )
        for index in range(len(cells_tuple))
    }
    assignment: dict[int, int] = {}
    used: set[int] = set()

    def solve(position: int) -> bool:
        if position == len(cells_tuple):
            return True
        for other in candidates[position]:
            if other in used:
                continue
            assignment[position] = other
            used.add(other)
            if solve(position + 1):
                return True
            used.remove(other)
            del assignment[position]
        return False

    if not solve(0):
        raise RuntimeError("could not build a deterministic false-equivalence derangement")
    shuffled = tuple(
        (cells_tuple[index][0], right_branches[assignment[index]])
        for index in range(len(cells_tuple))
    )
    if any(word_signature(array, left) == word_signature(array, right) for left, right in shuffled):
        raise RuntimeError("false-equivalence bank accidentally contains a true equality")

    payload = {
        "plan_version": V05_PLAN_VERSION,
        "maps": array.tolist(),
        "normal_forms": [list(word) for _, word in ordered],
        "cells": [[list(left), list(right)] for left, right in cells_tuple],
        "shuffled_cells": [[list(left), list(right)] for left, right in shuffled],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return RelationCellBank(
        normal_forms=tuple(word for _, word in ordered),
        signatures=tuple(signature for signature, _ in ordered),
        cells=cells_tuple,
        shuffled_cells=shuffled,
        fingerprint=hashlib.sha256(encoded).hexdigest(),
    )


def enumerate_probe_words(max_length: int = TRAIN_PROBE_MAX_LENGTH) -> tuple[tuple[int, ...], ...]:
    if isinstance(max_length, bool) or not isinstance(max_length, int) or max_length < 0:
        raise ValueError("max_length must be a nonnegative integer")
    return tuple(
        word
        for length in range(max_length + 1)
        for word in itertools.product((0, 1), repeat=length)
    )


def _ordered_product(codes: torch.Tensor, word: Sequence[int]) -> torch.Tensor:
    """Return ``M[-1] ... M[0]`` for one context's operator codes."""

    if codes.ndim != 3 or codes.shape[0] != 2 or codes.shape[-1] != codes.shape[-2]:
        raise ValueError("codes must have shape (2, hidden, hidden)")
    product = torch.eye(codes.shape[-1], dtype=codes.dtype, device=codes.device)
    for action in word:
        product = codes[int(action)] @ product
    return product


def relation_flatness_losses(
    model: PolarIsometricTableOperatorRNN,
    operator_codes: torch.Tensor,
    pairs: Sequence[tuple[Sequence[int], Sequence[int]]],
    probes: Sequence[Sequence[int]],
    *,
    powers: Sequence[int] = PACKET_HOLONOMY_POWERS,
    denominator_floor: float = PACKET_DENOMINATOR_FLOOR,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return the exact and v2 multiscale packet-flatness objectives.

    For a relation cell with latent products ``L`` and ``R``, the relative
    holonomy is ``H = R.T @ L``.  The packet term observes

    ``J D S (H**k - I) B``

    at every supplied repetition scale ``k`` and suffix ``S``.  The anchor
    frame ``B``, decoder ``D``, suffix products, and mean-square denominator
    are detached.  Consequently the packet gradient can reduce only the
    relation holonomy; it cannot move the observer to hide that holonomy.
    """

    if not isinstance(model, PolarIsometricTableOperatorRNN):
        raise TypeError("v0.5 flatness losses require the hard-polar model")
    if not pairs or not probes:
        raise ValueError("pairs and probes must both be nonempty")
    checked_powers: list[int] = []
    for power in powers:
        if isinstance(power, bool) or not isinstance(power, (int, np.integer)):
            raise TypeError("holonomy powers must be integers")
        value = int(power)
        if value < 1:
            raise ValueError("holonomy powers must be positive")
        checked_powers.append(value)
    if not checked_powers:
        raise ValueError("at least one holonomy power is required")
    floor = float(denominator_floor)
    if not math.isfinite(floor) or floor <= 0.0:
        raise ValueError("denominator_floor must be finite and positive")

    if operator_codes.ndim != 3 or operator_codes.shape[0] != 2:
        raise ValueError("operator_codes must have shape (2, hidden, hidden)")
    dimension = operator_codes.shape[-1]
    if operator_codes.shape[-2] != dimension or dimension != model.hidden_dim:
        raise ValueError("operator_codes hidden dimensions do not match the model")

    # B, D, and every suffix observer are frozen for this objective.  Products
    # making up H remain live, so packet gradients still reach the operator
    # encoder through both branches of every relation cell.
    anchors = model.state_anchors().transpose(0, 1).detach()
    decoder = model.decoder.weight.detach()
    left_products: list[torch.Tensor] = []
    right_products: list[torch.Tensor] = []
    for left, right in pairs:
        left_products.append(_ordered_product(operator_codes, left))
        right_products.append(_ordered_product(operator_codes, right))
    left_stack = torch.stack(left_products)
    right_stack = torch.stack(right_products)

    exact = (left_stack - right_stack).square().sum(dim=(-2, -1)).mean()
    exact = exact / (4.0 * dimension)

    holonomy = right_stack.transpose(-2, -1) @ left_stack
    identity = torch.eye(dimension, dtype=operator_codes.dtype, device=operator_codes.device)
    deltas = torch.stack(
        [torch.linalg.matrix_power(holonomy, power) - identity for power in checked_powers]
    )

    suffixes = torch.stack(
        [_ordered_product(operator_codes, word).detach() for word in probes]
    )
    observers = decoder.unsqueeze(0) @ suffixes
    observers = observers - observers.mean(dim=-2, keepdim=True)
    baseline = observers @ anchors
    denominators = baseline.square().mean(dim=(-2, -1)).detach().clamp_min(floor)

    displaced = deltas @ anchors
    residual = torch.einsum("soh,kchn->kcson", observers, displaced)
    numerators = residual.square().mean(dim=(-2, -1))
    packet = (numerators / denominators.view(1, 1, -1)).mean()
    return exact, packet


def _base_arm_spec(spec: FlatnessArmSpec) -> PacketClosureArmSpec:
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


def build_flatness_model(
    config: FlatnessTrainConfig,
    arm: str | FlatnessArmSpec,
) -> PolarIsometricTableOperatorRNN:
    spec = get_flatness_arm(arm)
    model = build_packet_closure_model(config.base_config(), _base_arm_spec(spec))
    if not isinstance(model, PolarIsometricTableOperatorRNN):
        raise RuntimeError("v0.5 model construction did not return the hard-polar architecture")
    return model


def _cyclic_indices(count: int, take: int, step: int, stride: int) -> tuple[int, ...]:
    if count < 1 or take < 1:
        raise ValueError("cyclic schedule requires positive counts")
    start = (step * stride) % count
    return tuple((start + offset) % count for offset in range(min(take, count)))


def _packet_ramp_multiplier(step: int) -> float:
    """Delay packet gradients through step 400, then ramp through step 800."""

    if isinstance(step, bool) or not isinstance(step, int) or step < 0:
        raise ValueError("step must be a nonnegative integer")
    completed_step = step + 1
    if completed_step <= PACKET_DELAY_STEPS:
        return 0.0
    if completed_step >= PACKET_RAMP_END_STEP:
        return 1.0
    return (completed_step - PACKET_DELAY_STEPS) / (
        PACKET_RAMP_END_STEP - PACKET_DELAY_STEPS
    )


def compute_flatness_losses(
    model: PolarIsometricTableOperatorRNN,
    batch: EpisodeBatch,
    construction: V04ConstructionBank,
    arm: str | FlatnessArmSpec,
    config: FlatnessTrainConfig,
    *,
    step: int,
) -> FlatnessLosses:
    """Compute one supervision-matched v0.5 training objective."""

    config.validate()
    spec = get_flatness_arm(arm)
    base_config = config.base_config()
    base = compute_packet_closure_losses(
        model,
        batch,
        construction,
        _base_arm_spec(spec),
        base_config,
        step=step,
    )
    bundle = model.encode_operator_bundle(batch.tables[:1])
    codes = bundle.matrices[0]
    bank = relation_cell_bank(batch.maps[0])
    all_pairs = bank.shuffled_cells if spec.shuffled_equivalence else bank.cells
    cell_indices = tuple(range(len(all_pairs)))
    all_probes = bank.normal_forms
    probe_indices = tuple(range(len(all_probes)))
    selected_pairs = tuple(all_pairs[index] for index in cell_indices)
    selected_probes = tuple(all_probes[index] for index in probe_indices)
    exact, packet = relation_flatness_losses(model, codes, selected_pairs, selected_probes)
    warmup = 1.0 if config.warmup_steps == 0 else min(1.0, (step + 1) / config.warmup_steps)
    packet_ramp = _packet_ramp_multiplier(step)
    total = base.total
    if spec.exact_flatness:
        total = total + warmup * config.exact_weight * exact
    if spec.packet_flatness:
        total = total + packet_ramp * config.packet_weight * packet
    return FlatnessLosses(
        total=total,
        base=base,
        exact=exact,
        packet=packet,
        warmup=warmup,
        packet_ramp=packet_ramp,
        cell_indices=cell_indices,
        probe_indices=probe_indices,
    )


def _update_tensor_digest(digest: "hashlib._Hash", tensor: torch.Tensor) -> None:
    local = tensor.detach().to(device="cpu").contiguous()
    digest.update(str(local.dtype).encode("ascii"))
    digest.update(json.dumps(list(local.shape), separators=(",", ":")).encode("ascii"))
    digest.update(local.numpy().tobytes())


def _update_episode_digest(digest: "hashlib._Hash", batch: EpisodeBatch, step: int) -> None:
    digest.update(int(step).to_bytes(8, "little", signed=False))
    for tensor in (
        batch.tables,
        batch.maps,
        batch.op_slots,
        batch.canonical_ops,
        batch.start,
        batch.target,
        batch.canonical_to_slot,
        batch.phi,
    ):
        _update_tensor_digest(digest, tensor)


def _trajectory_row(
    losses: FlatnessLosses,
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
        "exact_flatness_loss": float(losses.exact.detach()),
        "packet_flatness_loss": float(losses.packet.detach()),
        "terminal_accuracy": float(losses.base.terminal_accuracy.detach()),
        "construction_accuracy": float(losses.base.construction_accuracy.detach()),
        "gradient_norm_before_clip": gradient_norm,
        "warmup": losses.warmup,
        "packet_ramp": losses.packet_ramp,
        "cell_indices": list(losses.cell_indices),
        "probe_indices": list(losses.probe_indices),
    }


def train_flatness_arm(
    arm: str | FlatnessArmSpec,
    config: FlatnessTrainConfig,
    *,
    model: PolarIsometricTableOperatorRNN | None = None,
) -> TrainedFlatnessArm:
    """Train one arm on the deterministic paired terminal/relation stream."""

    config.validate()
    spec = get_flatness_arm(arm)
    if model is None:
        model = build_flatness_model(config, spec)
    if not isinstance(model, PolarIsometricTableOperatorRNN):
        raise TypeError("v0.5 arms require PolarIsometricTableOperatorRNN")
    initial_digest = state_dict_digest(model)
    base_config = config.base_config()
    construction = make_v04_construction_bank(base_config.auxiliary_max_depth)
    device = torch.device(config.device)
    model = model.to(device)
    model.train()
    optimizer = torch.optim.AdamW(
        packet_closure_optimizer_parameter_groups(model, base_config),
        weight_decay=config.weight_decay,
    )
    trainable = tuple(parameter for parameter in model.parameters() if parameter.requires_grad)
    generator = EpisodeGenerator(config.episode_seed_base + config.seed)
    episode_digest = hashlib.sha256(b"v0.5-episode-stream")
    proposal_digest = hashlib.sha256(b"v0.5-terminal-proposal-stream")
    relation_digest = hashlib.sha256(b"v0.5-relation-schedule")
    checkpoints = set(
        np.linspace(0, config.steps - 1, num=min(config.checkpoints, config.steps), dtype=int).tolist()
    )
    trajectory: list[dict[str, Any]] = []
    accepted_total = 0
    rejected_total = 0
    proposal_total = 0
    final_loss = math.nan
    started = time.perf_counter()
    for step in range(config.steps):
        length = int(generator.rng.integers(1, config.train_max_length + 1))
        sample = sample_v04_terminal_batch(generator, config.batch_size, length)
        accepted_total += sample.accepted_count
        rejected_total += sample.rejected_count
        proposal_total += sample.proposal_count
        proposal_digest.update(sample.proposal_digest.encode("ascii"))
        _update_episode_digest(episode_digest, sample.batch, step)

        bank = relation_cell_bank(sample.batch.maps[0])
        cells = bank.shuffled_cells if spec.shuffled_equivalence else bank.cells
        cell_indices = tuple(range(len(cells)))
        probe_words = bank.normal_forms
        probe_indices = tuple(range(len(probe_words)))
        relation_digest.update(bank.fingerprint.encode("ascii"))
        relation_digest.update(
            b"shuffled" if spec.shuffled_equivalence else b"equivalent"
        )
        relation_digest.update(bytes(cell_indices))
        relation_digest.update(bytes(probe_indices))
        selected_pairs = [cells[index] for index in cell_indices]
        relation_digest.update(
            json.dumps(
                selected_pairs,
                separators=(",", ":"),
            ).encode("ascii")
        )

        batch = sample.batch.to(device)
        optimizer.zero_grad(set_to_none=True)
        losses = compute_flatness_losses(
            model,
            batch,
            construction,
            spec,
            config,
            step=step,
        )
        if not bool(torch.isfinite(losses.total.detach())):
            raise FloatingPointError(f"non-finite v0.5 loss at step {step}")
        losses.total.backward()
        gradient_norm = float(torch.nn.utils.clip_grad_norm_(trainable, config.grad_clip))
        if not math.isfinite(gradient_norm):
            raise FloatingPointError(f"non-finite v0.5 gradient norm at step {step}")
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
    return TrainedFlatnessArm(
        arm=spec,
        config=config,
        model=model,
        trajectory=trajectory,
        elapsed_seconds=elapsed,
        final_loss=final_loss,
        parameter_count=sum(parameter.numel() for parameter in model.parameters()),
        initial_state_digest=initial_digest,
        final_state_digest=state_dict_digest(model),
        episode_stream_digest=episode_digest.hexdigest(),
        terminal_proposal_stream_digest=proposal_digest.hexdigest(),
        relation_schedule_digest=relation_digest.hexdigest(),
        terminal_proposal_count=proposal_total,
        terminal_candidates_accepted=accepted_total,
        terminal_candidates_rejected=rejected_total,
    )


def train_paired_flatness_panel(
    config: FlatnessTrainConfig,
    arm_names: Sequence[str] = PRIMARY_FLATNESS_ARMS,
) -> dict[str, TrainedFlatnessArm]:
    """Train all requested arms from identical initialization and streams."""

    names = tuple(arm_names)
    if not names or len(names) != len(set(names)):
        raise ValueError("arm_names must be nonempty and unique")
    results = {name: train_flatness_arm(name, config) for name in names}
    for attribute in (
        "initial_state_digest",
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "terminal_proposal_count",
        "terminal_candidates_accepted",
        "terminal_candidates_rejected",
    ):
        values = {getattr(result, attribute) for result in results.values()}
        if len(values) != 1:
            raise RuntimeError(f"paired v0.5 arms disagree on {attribute}")
    # Positive and shuffled arms intentionally hash different pair assignments;
    # all non-shuffled arms must still share the exact schedule digest.
    positive_digests = {
        result.relation_schedule_digest
        for result in results.values()
        if not result.arm.shuffled_equivalence
    }
    if len(positive_digests) != 1:
        raise RuntimeError("positive-relation arms consumed different relation schedules")
    return results


def flatness_training_contract(config: FlatnessTrainConfig) -> dict[str, Any]:
    """Return the JSON-safe frozen training contract."""

    config.validate()
    return {
        "plan_version": V05_PLAN_VERSION,
        "arms": [asdict(FLATNESS_ARMS[name]) for name in PRIMARY_FLATNESS_ARMS],
        "config": asdict(config),
        "base_label_firewall": "v0.4 identity-and-r2 endpoint-action rejection",
        "structural_exposure": "nine table-derived non-tree same-action cells",
        "train_probe_family": "all eight table-derived BFS normal forms",
        "packet_holonomy_powers": list(PACKET_HOLONOMY_POWERS),
        "packet_delay_steps": PACKET_DELAY_STEPS,
        "packet_ramp_end_step": PACKET_RAMP_END_STEP,
        "packet_denominator_floor": PACKET_DENOMINATOR_FLOOR,
        "loss_normalization": {
            "exact": "squared Frobenius / (4 * hidden_dim)",
            "packet_numerator": "mean-square of J D S (H^k - I) B",
            "packet_denominator": "detached mean-square of J D S B, floored at 1e-4",
            "packet_observer": "B, D, S, and denominator stop-gradient",
        },
    }


__all__ = [
    "FLATNESS_ARMS",
    "PACKET_DELAY_STEPS",
    "PACKET_DENOMINATOR_FLOOR",
    "PACKET_HOLONOMY_POWERS",
    "PACKET_RAMP_END_STEP",
    "PACKET_SUFFIX_COUNT",
    "PRIMARY_FLATNESS_ARMS",
    "RELATION_CELL_COUNT",
    "TRAIN_PROBE_MAX_LENGTH",
    "V05_PLAN_VERSION",
    "FlatnessArmSpec",
    "FlatnessLosses",
    "FlatnessTrainConfig",
    "RelationCellBank",
    "TrainedFlatnessArm",
    "build_flatness_model",
    "compute_flatness_losses",
    "enumerate_probe_words",
    "flatness_training_contract",
    "get_flatness_arm",
    "relation_cell_bank",
    "relation_flatness_losses",
    "train_flatness_arm",
    "train_paired_flatness_panel",
    "word_signature",
]
