"""Differentiable continuation-packet training with an audit firewall.

The training objective in this module is deliberately narrower than the packet
diagnostics in :mod:`komorebi_neuralese.ambient_packets`.  A frozen suffix bank
is split *by induced transition*, so two relation-equivalent words can never be
placed on opposite sides of the construction/audit boundary.  The training
function then accepts the plan but reads only ``plan.construction``.  Held-out
words are evaluated by a separate ``torch.no_grad`` entry point.

For an endpoint ``h`` with correct decoder row ``d_y``, competitor ``d_j``,
and learned positive-definite ambient metric ``G``, the signed margin is

    <d_y - d_j, h> / (||d_y - d_j||_{G^-1} ||h||_G).

It is therefore invariant to positive rescaling of either the hidden state or
the decoder contrast.  Recurrent suffix execution normalizes after every
matrix, matching the positive-ray recurrence used by the v0.4 model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
from typing import Iterable, Sequence

import torch
from torch.nn import functional as F

from .ambient_packets import (
    Suffix,
    enumerate_suffixes,
    split_suffixes_for_validation,
    suffix_transition_signature,
)


CanonicalTransitions = tuple[tuple[int, ...], ...]


def _canonical_word(word: Sequence[int], num_actions: int) -> Suffix:
    converted: list[int] = []
    for action in word:
        if isinstance(action, bool) or not isinstance(action, int):
            raise TypeError("suffix actions must be integers, not booleans")
        if action < 0 or action >= num_actions:
            raise ValueError("suffix contains an action outside the canonical alphabet")
        converted.append(int(action))
    return tuple(converted)


def _canonical_transition_tuple(transitions: torch.Tensor) -> CanonicalTransitions:
    if not isinstance(transitions, torch.Tensor) or transitions.ndim != 2:
        raise ValueError("canonical_transitions must have shape [actions, states]")
    integer_dtypes = {torch.int8, torch.int16, torch.int32, torch.int64, torch.uint8}
    if transitions.dtype not in integer_dtypes:
        raise TypeError("canonical_transitions must have an integer dtype")
    actions, states = transitions.shape
    if actions < 1 or states < 2:
        raise ValueError("at least one action and two semantic states are required")
    local = transitions.detach().to(device="cpu", dtype=torch.long).contiguous()
    if not bool(((local >= 0) & (local < states)).all()):
        raise ValueError("canonical_transitions contains an invalid target state")
    return tuple(tuple(int(value) for value in row) for row in local.tolist())


def _tuple_transition_signature(transitions: CanonicalTransitions, word: Suffix) -> tuple[int, ...]:
    state = list(range(len(transitions[0])))
    for action in word:
        action_map = transitions[action]
        state = [action_map[source] for source in state]
    return tuple(state)


def _plan_digest(
    transitions: CanonicalTransitions,
    construction: tuple[Suffix, ...],
    heldout: tuple[Suffix, ...],
    seed: int,
    heldout_fraction: float,
) -> str:
    payload = {
        "canonical_transitions": transitions,
        "construction": construction,
        "heldout": heldout,
        "seed": int(seed),
        "heldout_fraction": float(heldout_fraction),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class RelationGroupedSuffixPlan:
    """Immutable construction/held-out plan grouped by semantic action.

    ``canonical_transitions`` records the exact finite action system used to
    define relation equivalence.  The constructor rechecks every word and
    rejects both exact and induced-transition leakage, including for manually
    constructed plans used in small tests.
    """

    canonical_transitions: CanonicalTransitions
    construction: tuple[Suffix, ...]
    heldout: tuple[Suffix, ...]
    seed: int
    heldout_fraction: float
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        transitions = tuple(tuple(int(value) for value in row) for row in self.canonical_transitions)
        if not transitions or not transitions[0]:
            raise ValueError("canonical_transitions must be nonempty")
        states = len(transitions[0])
        if states < 2 or any(len(row) != states for row in transitions):
            raise ValueError("canonical transition rows must share at least two states")
        if any(value < 0 or value >= states for row in transitions for value in row):
            raise ValueError("canonical_transitions contains an invalid target state")
        actions = len(transitions)
        construction = tuple(_canonical_word(word, actions) for word in self.construction)
        heldout = tuple(_canonical_word(word, actions) for word in self.heldout)
        if not construction or not heldout:
            raise ValueError("construction and held-out suffix banks must both be nonempty")
        if len(set(construction)) != len(construction) or len(set(heldout)) != len(heldout):
            raise ValueError("suffixes within each bank must be unique")
        exact_overlap = set(construction) & set(heldout)
        if exact_overlap:
            raise ValueError(f"suffix leakage detected for {len(exact_overlap)} exact word(s)")
        construction_groups = {_tuple_transition_signature(transitions, word) for word in construction}
        heldout_groups = {_tuple_transition_signature(transitions, word) for word in heldout}
        group_overlap = construction_groups & heldout_groups
        if group_overlap:
            raise ValueError(
                f"relation-group leakage detected for {len(group_overlap)} induced transition(s)"
            )
        if not math.isfinite(float(self.heldout_fraction)) or not 0.0 < self.heldout_fraction < 1.0:
            raise ValueError("heldout_fraction must lie strictly between zero and one")
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise TypeError("seed must be an integer")
        object.__setattr__(self, "canonical_transitions", transitions)
        object.__setattr__(self, "construction", construction)
        object.__setattr__(self, "heldout", heldout)
        object.__setattr__(
            self,
            "fingerprint",
            _plan_digest(transitions, construction, heldout, self.seed, self.heldout_fraction),
        )

    @property
    def num_actions(self) -> int:
        return len(self.canonical_transitions)

    @property
    def num_states(self) -> int:
        return len(self.canonical_transitions[0])

    @property
    def construction_group_signatures(self) -> tuple[tuple[int, ...], ...]:
        signatures = {_tuple_transition_signature(self.canonical_transitions, word) for word in self.construction}
        return tuple(sorted(signatures))

    @property
    def heldout_group_signatures(self) -> tuple[tuple[int, ...], ...]:
        signatures = {_tuple_transition_signature(self.canonical_transitions, word) for word in self.heldout}
        return tuple(sorted(signatures))


def make_relation_grouped_suffix_plan(
    canonical_transitions: torch.Tensor,
    *,
    max_depth: int,
    heldout_fraction: float = 0.25,
    seed: int = 0,
) -> RelationGroupedSuffixPlan:
    """Create a deterministic split without touching process-global RNG state.

    Words that induce the same transition on every semantic state are one
    indivisible relation group.  The empty word and every word equivalent to it
    are forced into construction, making the base decoder boundary part of the
    trained packet while keeping all identity rewrites on the same side.
    """

    transitions_tuple = _canonical_transition_tuple(canonical_transitions)
    local = torch.tensor(transitions_tuple, dtype=torch.long, device="cpu")
    suffixes = enumerate_suffixes(local.shape[0], max_depth)

    def relation_key(word: Suffix) -> tuple[int, ...]:
        return suffix_transition_signature(local, word)

    split = split_suffixes_for_validation(
        suffixes,
        heldout_fraction=heldout_fraction,
        seed=seed,
        equivalence_key=relation_key,
        stratify_by_depth=False,
        keep_empty_in_construction=True,
    )
    return RelationGroupedSuffixPlan(
        canonical_transitions=transitions_tuple,
        construction=split.construction,
        heldout=split.heldout,
        seed=int(seed),
        heldout_fraction=float(heldout_fraction),
    )


@dataclass(frozen=True)
class ContinuationMarginEvaluation:
    """Per-suffix normalized margins from a construction or held-out rollout."""

    suffixes: tuple[Suffix, ...]
    target_states: torch.Tensor
    class_margins: torch.Tensor
    suffix_minimum_margin: torch.Tensor
    minimum_margin: torch.Tensor
    degenerate_decoder_contrasts: torch.Tensor


@dataclass(frozen=True)
class PacketMarginTrainingResult:
    """Differentiable construction loss and its non-detached diagnostics."""

    loss: torch.Tensor
    per_example_loss: torch.Tensor
    evaluation: ContinuationMarginEvaluation
    required_margin: float
    temperature: float
    plan_fingerprint: str


@dataclass(frozen=True)
class HeldoutPacketAudit:
    """Detached audit result.  This type is never consumed by the loss path."""

    evaluation: ContinuationMarginEvaluation
    inside: torch.Tensor
    survival_fraction: float
    boundary_tolerance: float
    plan_fingerprint: str


def _expanded_float_batch(tensor: torch.Tensor, batch: int, name: str, rank: int) -> torch.Tensor:
    if not isinstance(tensor, torch.Tensor) or not tensor.is_floating_point():
        raise TypeError(f"{name} must be a floating tensor")
    if tensor.ndim == rank - 1:
        tensor = tensor.unsqueeze(0).expand(batch, *tensor.shape)
    if tensor.ndim != rank or tensor.shape[0] != batch:
        raise ValueError(f"{name} must have rank {rank} with leading batch {batch}")
    return tensor


def _expanded_integer_batch(tensor: torch.Tensor, batch: int, name: str, rank: int) -> torch.Tensor:
    integer_dtypes = {torch.int8, torch.int16, torch.int32, torch.int64, torch.uint8}
    if not isinstance(tensor, torch.Tensor) or tensor.dtype not in integer_dtypes:
        raise TypeError(f"{name} must be an integer tensor")
    if tensor.ndim == rank - 1:
        tensor = tensor.unsqueeze(0).expand(batch, *tensor.shape)
    if tensor.ndim != rank or tensor.shape[0] != batch:
        raise ValueError(f"{name} must have rank {rank} with leading batch {batch}")
    return tensor.to(dtype=torch.long)


def _validate_rollout_inputs(
    hidden: torch.Tensor,
    operator_matrices: torch.Tensor,
    decoder_weight: torch.Tensor,
    metric: torch.Tensor,
    slot_transitions: torch.Tensor,
    canonical_to_slot: torch.Tensor,
    source_states: torch.Tensor,
    plan: RelationGroupedSuffixPlan,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    if not isinstance(hidden, torch.Tensor) or hidden.ndim != 2 or not hidden.is_floating_point():
        raise ValueError("hidden must be a floating tensor with shape [batch, dimension]")
    batch, dimension = hidden.shape
    if batch < 1 or dimension < 1:
        raise ValueError("hidden must contain a nonempty batch and ambient dimension")
    operator_matrices = _expanded_float_batch(operator_matrices, batch, "operator_matrices", 4)
    slot_transitions = _expanded_integer_batch(slot_transitions, batch, "slot_transitions", 3)
    canonical_to_slot = _expanded_integer_batch(canonical_to_slot, batch, "canonical_to_slot", 2)
    if not isinstance(decoder_weight, torch.Tensor) or decoder_weight.ndim != 2:
        raise ValueError("decoder_weight must have shape [states, dimension]")
    if not decoder_weight.is_floating_point():
        raise TypeError("decoder_weight must be floating point")
    if not isinstance(source_states, torch.Tensor) or source_states.ndim != 1:
        raise ValueError("source_states must have shape [batch]")
    if not isinstance(metric, torch.Tensor) or metric.shape != (dimension, dimension):
        raise ValueError("metric must have shape [dimension, dimension]")
    if not metric.is_floating_point():
        raise TypeError("metric must be floating point")
    integer_dtypes = {torch.int8, torch.int16, torch.int32, torch.int64, torch.uint8}
    if source_states.dtype not in integer_dtypes or source_states.shape[0] != batch:
        raise ValueError("source_states must be an integer tensor with shape [batch]")
    source_states = source_states.to(dtype=torch.long)

    slots = operator_matrices.shape[1]
    states = decoder_weight.shape[0]
    if operator_matrices.shape[2:] != (dimension, dimension):
        raise ValueError("operator_matrices ambient dimensions do not match hidden")
    if decoder_weight.shape != (states, dimension) or states != plan.num_states:
        raise ValueError("decoder dimensions do not match the plan")
    if slot_transitions.shape != (batch, slots, states):
        raise ValueError("slot_transitions must have shape [batch, slots, states]")
    if canonical_to_slot.shape != (batch, plan.num_actions) or slots != plan.num_actions:
        raise ValueError("canonical_to_slot and operator slots must match the plan actions")

    device = hidden.device
    if any(
        tensor.device != device
        for tensor in (
            operator_matrices,
            decoder_weight,
            metric,
            slot_transitions,
            canonical_to_slot,
            source_states,
        )
    ):
        raise ValueError("all rollout tensors must be on the same device")
    if (
        operator_matrices.dtype != hidden.dtype
        or decoder_weight.dtype != hidden.dtype
        or metric.dtype != hidden.dtype
    ):
        raise ValueError("hidden, operator_matrices, decoder_weight, and metric must share a dtype")
    if not bool(torch.isfinite(hidden).all()):
        raise ValueError("hidden must be finite")
    if not bool(torch.isfinite(operator_matrices).all()):
        raise ValueError("operator_matrices must be finite")
    if not bool(torch.isfinite(decoder_weight).all()):
        raise ValueError("decoder_weight must be finite")
    if not bool(torch.isfinite(metric).all()):
        raise ValueError("metric must be finite")
    tolerance = 64.0 * torch.finfo(metric.dtype).eps * max(1, dimension)
    if not torch.allclose(metric, metric.transpose(0, 1), atol=tolerance, rtol=tolerance):
        raise ValueError("metric must be symmetric")
    _, cholesky_info = torch.linalg.cholesky_ex(metric)
    if int(cholesky_info.item()) != 0:
        raise ValueError("metric must be positive definite")
    if not bool(((slot_transitions >= 0) & (slot_transitions < states)).all()):
        raise ValueError("slot_transitions contains an invalid target state")
    if not bool(((source_states >= 0) & (source_states < states)).all()):
        raise ValueError("source_states contains an invalid semantic state")
    expected_slots = torch.arange(slots, dtype=torch.long, device=device).expand(batch, -1)
    if not torch.equal(torch.sort(canonical_to_slot, dim=1).values, expected_slots):
        raise ValueError("each canonical_to_slot row must be a permutation of the slots")
    return operator_matrices, metric, slot_transitions, canonical_to_slot, source_states


def _normalize_positive_ray(state: torch.Tensor, metric: torch.Tensor, eps: float) -> torch.Tensor:
    squared_norms = torch.einsum("...i,ij,...j->...", state, metric, state)
    norms = squared_norms.clamp_min(0.0).sqrt()
    if not bool(torch.isfinite(norms).all()) or bool((norms <= eps).any()):
        raise ValueError("suffix rollout reached a zero or non-finite projective state")
    return state / norms.unsqueeze(-1)


def _evaluate_suffix_bank(
    hidden: torch.Tensor,
    operator_matrices: torch.Tensor,
    decoder_weight: torch.Tensor,
    metric: torch.Tensor,
    slot_transitions: torch.Tensor,
    canonical_to_slot: torch.Tensor,
    source_states: torch.Tensor,
    suffixes: tuple[Suffix, ...],
    *,
    eps: float,
) -> ContinuationMarginEvaluation:
    if not suffixes:
        raise ValueError("suffix bank must be nonempty")
    batch = hidden.shape[0]
    rows = torch.arange(batch, dtype=torch.long, device=hidden.device)
    class_margin_rows: list[torch.Tensor] = []
    target_rows: list[torch.Tensor] = []
    degenerate_rows: list[torch.Tensor] = []

    for suffix in suffixes:
        endpoint = hidden
        target = source_states
        for canonical_action in suffix:
            slot = canonical_to_slot[:, canonical_action]
            selected_matrix = operator_matrices[rows, slot]
            endpoint = torch.bmm(selected_matrix, endpoint.unsqueeze(-1)).squeeze(-1)
            endpoint = _normalize_positive_ray(endpoint, metric, eps)
            selected_transition = slot_transitions[rows, slot]
            target = selected_transition[rows, target]

        endpoint = _normalize_positive_ray(endpoint, metric, eps)
        correct_rows = decoder_weight[target]
        contrasts = correct_rows.unsqueeze(1) - decoder_weight.unsqueeze(0)
        solved_contrasts = torch.linalg.solve(
            metric,
            contrasts.reshape(-1, contrasts.shape[-1]).transpose(0, 1),
        ).transpose(0, 1).reshape_as(contrasts)
        dual_squared = torch.einsum("bsh,bsh->bs", contrasts, solved_contrasts)
        # Flooring before sqrt avoids an infinite derivative at coincident
        # decoder rows while retaining a flag that the contrast is degenerate.
        dual_norms = dual_squared.clamp_min(eps * eps).sqrt()
        numerators = torch.einsum("bsh,bh->bs", contrasts, endpoint)
        margins = numerators / dual_norms
        target_mask = F.one_hot(target, num_classes=decoder_weight.shape[0]).to(dtype=torch.bool)
        margins = margins.masked_fill(target_mask, torch.inf)
        degenerate = (dual_squared <= eps * eps) & ~target_mask
        class_margin_rows.append(margins)
        target_rows.append(target)
        degenerate_rows.append(degenerate)

    class_margins = torch.stack(class_margin_rows, dim=1)
    targets = torch.stack(target_rows, dim=1)
    degenerates = torch.stack(degenerate_rows, dim=1)
    suffix_minimum = class_margins.min(dim=-1).values
    return ContinuationMarginEvaluation(
        suffixes=suffixes,
        target_states=targets,
        class_margins=class_margins,
        suffix_minimum_margin=suffix_minimum,
        minimum_margin=suffix_minimum.min(dim=-1).values,
        degenerate_decoder_contrasts=degenerates,
    )


def construction_packet_margin_loss(
    hidden: torch.Tensor,
    operator_matrices: torch.Tensor,
    decoder_weight: torch.Tensor,
    metric: torch.Tensor,
    slot_transitions: torch.Tensor,
    canonical_to_slot: torch.Tensor,
    source_states: torch.Tensor,
    plan: RelationGroupedSuffixPlan,
    *,
    required_margin: float = 0.10,
    temperature: float = 0.05,
    eps: float = 1e-8,
    reduction: str = "mean",
) -> PacketMarginTrainingResult:
    """Penalize construction-packet violations, never held-out constraints.

    The smooth hinge is applied to every non-target decoder inequality rather
    than only the currently worst one.  This gives useful gradients throughout
    the packet while ``evaluation.minimum_margin`` retains the exact hard gate.
    """

    if not 0.0 <= required_margin < 1.0 or not math.isfinite(required_margin):
        raise ValueError("required_margin must be finite and lie in [0, 1)")
    if temperature <= 0.0 or not math.isfinite(temperature):
        raise ValueError("temperature must be finite and positive")
    if eps <= 0.0 or not math.isfinite(eps):
        raise ValueError("eps must be finite and positive")
    if reduction not in {"mean", "sum", "none"}:
        raise ValueError("reduction must be 'mean', 'sum', or 'none'")
    operator_matrices, metric, slot_transitions, canonical_to_slot, source_states = _validate_rollout_inputs(
        hidden,
        operator_matrices,
        decoder_weight,
        metric,
        slot_transitions,
        canonical_to_slot,
        source_states,
        plan,
    )

    # This is the audit firewall: no held-out word is fetched or executed here.
    evaluation = _evaluate_suffix_bank(
        hidden,
        operator_matrices,
        decoder_weight,
        metric,
        slot_transitions,
        canonical_to_slot,
        source_states,
        plan.construction,
        eps=eps,
    )
    target_mask = F.one_hot(
        evaluation.target_states,
        num_classes=decoder_weight.shape[0],
    ).to(dtype=torch.bool)
    competitor_margins = evaluation.class_margins.masked_select(~target_mask).reshape(
        hidden.shape[0], len(plan.construction), decoder_weight.shape[0] - 1
    )
    penalties = temperature * F.softplus((required_margin - competitor_margins) / temperature)
    per_example = penalties.mean(dim=(1, 2))
    if reduction == "mean":
        loss = per_example.mean()
    elif reduction == "sum":
        loss = per_example.sum()
    else:
        loss = per_example
    return PacketMarginTrainingResult(
        loss=loss,
        per_example_loss=per_example,
        evaluation=evaluation,
        required_margin=float(required_margin),
        temperature=float(temperature),
        plan_fingerprint=plan.fingerprint,
    )


@torch.no_grad()
def audit_heldout_packet(
    hidden: torch.Tensor,
    operator_matrices: torch.Tensor,
    decoder_weight: torch.Tensor,
    metric: torch.Tensor,
    slot_transitions: torch.Tensor,
    canonical_to_slot: torch.Tensor,
    source_states: torch.Tensor,
    plan: RelationGroupedSuffixPlan,
    *,
    boundary_tolerance: float = 0.0,
    eps: float = 1e-8,
) -> HeldoutPacketAudit:
    """Evaluate the frozen held-out suffixes without constructing a gradient."""

    if not math.isfinite(boundary_tolerance):
        raise ValueError("boundary_tolerance must be finite")
    if eps <= 0.0 or not math.isfinite(eps):
        raise ValueError("eps must be finite and positive")
    operator_matrices, metric, slot_transitions, canonical_to_slot, source_states = _validate_rollout_inputs(
        hidden,
        operator_matrices,
        decoder_weight,
        metric,
        slot_transitions,
        canonical_to_slot,
        source_states,
        plan,
    )
    evaluation = _evaluate_suffix_bank(
        hidden,
        operator_matrices,
        decoder_weight,
        metric,
        slot_transitions,
        canonical_to_slot,
        source_states,
        plan.heldout,
        eps=eps,
    )
    inside = evaluation.minimum_margin > boundary_tolerance
    return HeldoutPacketAudit(
        evaluation=evaluation,
        inside=inside,
        survival_fraction=float(inside.to(dtype=torch.float64).mean().item()),
        boundary_tolerance=float(boundary_tolerance),
        plan_fingerprint=plan.fingerprint,
    )


def relation_groups(
    plan: RelationGroupedSuffixPlan,
    suffixes: Iterable[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    """Return induced transitions for external split audits and reports."""

    words = tuple(_canonical_word(word, plan.num_actions) for word in suffixes)
    return tuple(_tuple_transition_signature(plan.canonical_transitions, word) for word in words)


__all__ = [
    "ContinuationMarginEvaluation",
    "HeldoutPacketAudit",
    "PacketMarginTrainingResult",
    "RelationGroupedSuffixPlan",
    "audit_heldout_packet",
    "construction_packet_margin_loss",
    "make_relation_grouped_suffix_plan",
    "relation_groups",
]
