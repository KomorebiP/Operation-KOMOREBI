"""Independent evaluation for the v0.4 packet-closure factorial.

The training objectives deliberately live elsewhere.  Every entry point in
this module consumes already-built episode and word banks, switches the model
to evaluation mode temporarily, and runs without gradients.  In particular,
no evaluator constructs or consults a construction suffix bank when scoring a
held-out packet.

The packet metrics are reported in two complementary ways.  Strict packet
membership requires every held-out continuation to retain positive normalized
decoder margin.  Relation-group macro membership first takes the conjunction
within each induced-action class and then averages classes equally, so a class
with many syntactic rewrites cannot dominate the result.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
from itertools import combinations
import json
import math
import random
from typing import Any, Iterable, Iterator, Mapping, Sequence

import torch

from .algebra import canonical_maps
from .ambient_packets import Suffix, SuffixSplit, suffix_transition_signature, validate_suffix_split
from .composition_training import finite_transition_map
from .data import EpisodeBatch
from .models import RecurrentOperatorModel
from .packet_training import RelationGroupedSuffixPlan
from .stability_training import g_orthogonal_anchor_projector
from .switched_stability import projective_sequence_jacobian


FactorCell = tuple[bool, bool, bool]


def _numeric_summary(values: torch.Tensor | Iterable[float]) -> dict[str, float | int | None]:
    if isinstance(values, torch.Tensor):
        tensor = values.detach().to(device="cpu", dtype=torch.float64).reshape(-1)
    else:
        tensor = torch.tensor(tuple(values), dtype=torch.float64)
    total = int(tensor.numel())
    finite = tensor[torch.isfinite(tensor)]
    if finite.numel() == 0:
        return {
            "count": total,
            "finite_count": 0,
            "minimum": None,
            "p10": None,
            "median": None,
            "mean": None,
            "p90": None,
            "maximum": None,
        }
    return {
        "count": total,
        "finite_count": int(finite.numel()),
        "minimum": float(finite.min()),
        "p10": float(torch.quantile(finite, 0.10)),
        "median": float(torch.median(finite)),
        "mean": float(finite.mean()),
        "p90": float(torch.quantile(finite, 0.90)),
        "maximum": float(finite.max()),
    }


def _word_digest(transitions: torch.Tensor, words: tuple[Suffix, ...]) -> str:
    payload = {
        "transitions": transitions.detach().to(device="cpu", dtype=torch.long).tolist(),
        "words": [list(word) for word in words],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _canonical_words(
    words: Iterable[Sequence[int]],
    *,
    num_actions: int,
    name: str,
) -> tuple[Suffix, ...]:
    result: list[Suffix] = []
    for raw in words:
        try:
            word = tuple(raw)
        except TypeError as error:
            raise TypeError(f"each {name} word must be an iterable") from error
        for action in word:
            if isinstance(action, bool) or not isinstance(action, int):
                raise TypeError(f"{name} actions must be integers")
            if action < 0 or action >= num_actions:
                raise ValueError(f"{name} contains an action outside the canonical alphabet")
        result.append(word)
    if not result:
        raise ValueError(f"{name} must be nonempty")
    if len(set(result)) != len(result):
        raise ValueError(f"{name} words must be unique")
    return tuple(result)


def _transition_tensor(transitions: torch.Tensor) -> torch.Tensor:
    result = finite_transition_map(transitions).detach().to(device="cpu", dtype=torch.long)
    if result.shape[1] < 2:
        raise ValueError("canonical transitions require at least two semantic states")
    return result


def _relation_signature(transitions: torch.Tensor, word: Suffix) -> tuple[int, ...]:
    return suffix_transition_signature(transitions, word)


@dataclass(frozen=True)
class FrozenHeldoutBank:
    """A normalized external audit bank with relation-leakage metadata."""

    words: tuple[Suffix, ...]
    relation_signatures: tuple[tuple[int, ...], ...]
    fingerprint: str
    split_verified: bool

    @property
    def relation_group_count(self) -> int:
        return len(set(self.relation_signatures))

    def to_dict(self) -> dict[str, Any]:
        return {
            "word_count": len(self.words),
            "relation_group_count": self.relation_group_count,
            "maximum_depth": max(map(len, self.words)),
            "fingerprint": self.fingerprint,
            "split_verified": self.split_verified,
        }


HeldoutBankInput = SuffixSplit | RelationGroupedSuffixPlan | Iterable[Sequence[int]]


def freeze_heldout_bank(
    heldout: HeldoutBankInput,
    canonical_transitions: torch.Tensor,
    *,
    max_suffixes: int | None = 128,
) -> FrozenHeldoutBank:
    """Validate and fingerprint an externally chosen held-out suffix bank.

    Passing :class:`SuffixSplit` or :class:`RelationGroupedSuffixPlan` verifies
    that no induced-action class appears in both construction and held-out
    banks.  A raw word iterable is accepted for replay of an independently
    frozen bank, but is marked ``split_verified=False`` because construction
    membership is unavailable.  The default work cap prevents accidentally
    expanding a 511-word bank; pass ``max_suffixes=None`` for an explicitly
    requested exhaustive audit.
    """

    transitions = _transition_tensor(canonical_transitions)
    num_actions = int(transitions.shape[0])
    split_verified = False
    construction: tuple[Suffix, ...] | None = None

    if isinstance(heldout, RelationGroupedSuffixPlan):
        plan_transitions = torch.tensor(heldout.canonical_transitions, dtype=torch.long)
        if not torch.equal(plan_transitions, transitions):
            raise ValueError("held-out plan transitions do not match canonical_transitions")
        words = _canonical_words(heldout.heldout, num_actions=num_actions, name="heldout")
        construction = _canonical_words(
            heldout.construction,
            num_actions=num_actions,
            name="construction",
        )
        split_verified = True
    elif isinstance(heldout, SuffixSplit):
        relation_key = lambda word: _relation_signature(transitions, word)
        validate_suffix_split(heldout, equivalence_key=relation_key)
        words = _canonical_words(heldout.heldout, num_actions=num_actions, name="heldout")
        construction = _canonical_words(
            heldout.construction,
            num_actions=num_actions,
            name="construction",
        )
        split_verified = True
    else:
        words = _canonical_words(heldout, num_actions=num_actions, name="heldout")

    if max_suffixes is not None:
        if isinstance(max_suffixes, bool) or not isinstance(max_suffixes, int) or max_suffixes < 1:
            raise ValueError("max_suffixes must be a positive integer or None")
        if len(words) > max_suffixes:
            raise ValueError(
                f"held-out bank has {len(words)} words, exceeding max_suffixes={max_suffixes}; "
                "pass None to request exhaustive evaluation"
            )

    signatures = tuple(_relation_signature(transitions, word) for word in words)
    if construction is not None:
        construction_signatures = {
            _relation_signature(transitions, word) for word in construction
        }
        overlap = construction_signatures & set(signatures)
        if overlap:
            raise ValueError(
                f"relation-group leakage detected for {len(overlap)} induced transition(s)"
            )
    return FrozenHeldoutBank(
        words=words,
        relation_signatures=signatures,
        fingerprint=_word_digest(transitions, words),
        split_verified=split_verified,
    )


@contextmanager
def _temporary_eval(model: RecurrentOperatorModel) -> Iterator[None]:
    was_training = bool(model.training)
    model.eval()
    try:
        with torch.inference_mode():
            yield
    finally:
        model.train(was_training)


def _model_device(model: RecurrentOperatorModel) -> torch.device:
    try:
        return next(model.parameters()).device
    except StopIteration:
        return torch.device("cpu")


def _decoder_weight(model: RecurrentOperatorModel) -> torch.Tensor:
    decoder = getattr(model, "decoder", None)
    weight = getattr(decoder, "weight", None)
    if not isinstance(weight, torch.Tensor) or weight.ndim != 2 or not weight.is_floating_point():
        raise TypeError("packet evaluation requires a linear decoder with a rank-two weight")
    bias = getattr(decoder, "bias", None)
    if isinstance(bias, torch.Tensor) and not bool((bias.detach() == 0).all()):
        raise ValueError("packet evaluation requires a homogeneous decoder (no nonzero bias)")
    return weight


def _resolved_metric(
    model: RecurrentOperatorModel,
    dimension: int,
    reference: torch.Tensor,
    metric: torch.Tensor | None,
) -> torch.Tensor:
    candidate: Any = metric
    if candidate is None:
        candidate = getattr(model, "invariant_metric", None)
        if callable(candidate):
            candidate = candidate()
    if candidate is None:
        candidate = torch.eye(dimension, dtype=reference.dtype, device=reference.device)
    if not isinstance(candidate, torch.Tensor) or candidate.shape != (dimension, dimension):
        raise ValueError(f"metric must have shape ({dimension}, {dimension})")
    candidate = candidate.to(dtype=reference.dtype, device=reference.device)
    if not bool(torch.isfinite(candidate).all()):
        raise ValueError("metric must be finite")
    tolerance = 64.0 * torch.finfo(candidate.dtype).eps * max(1, dimension)
    if not torch.allclose(candidate, candidate.transpose(0, 1), atol=tolerance, rtol=tolerance):
        raise ValueError("metric must be symmetric")
    _, info = torch.linalg.cholesky_ex(candidate)
    if int(info.item()) != 0:
        raise ValueError("metric must be positive definite")
    return candidate


def _validate_batch(batch: EpisodeBatch, transitions: torch.Tensor) -> None:
    if not isinstance(batch, EpisodeBatch):
        raise TypeError("batch must be an EpisodeBatch")
    actions, states = map(int, transitions.shape)
    examples = int(batch.start.shape[0])
    if examples < 1:
        raise ValueError("episode batch must be nonempty")
    if batch.maps.shape != (examples, actions, states):
        raise ValueError("episode maps do not match canonical action/state counts")
    if batch.canonical_to_slot.shape != (examples, actions):
        raise ValueError("canonical_to_slot has the wrong shape")
    if batch.phi.shape != (examples, states):
        raise ValueError("phi has the wrong shape")
    expected = torch.arange(actions, dtype=torch.long).expand(examples, -1)
    if not torch.equal(torch.sort(batch.canonical_to_slot.cpu(), dim=1).values, expected):
        raise ValueError("each canonical_to_slot row must be a slot permutation")
    expected_states = torch.arange(states, dtype=torch.long).expand(examples, -1)
    if not torch.equal(torch.sort(batch.phi.cpu(), dim=1).values, expected_states):
        raise ValueError("each phi row must be a state permutation")
    if batch.target.shape != (examples,):
        raise ValueError("batch target has the wrong shape")

    # Verify the actual exposed episode action, not just tensor dimensions.
    # phi maps canonical state labels to visible labels.  Consequently, for
    # canonical source s and action a, the visible slot must map phi(s) to
    # phi(T_a(s)).
    maps = batch.maps.detach().to(device="cpu", dtype=torch.long)
    slots = batch.canonical_to_slot.detach().to(device="cpu", dtype=torch.long)
    phi = batch.phi.detach().to(device="cpu", dtype=torch.long)
    rows = torch.arange(examples)
    for action in range(actions):
        selected = maps[rows, slots[:, action]]
        actual = torch.gather(selected, 1, phi)
        expected_targets = phi[:, transitions[action]]
        if not torch.equal(actual, expected_targets):
            raise ValueError(
                "episode actions do not realize canonical_transitions under phi"
            )

    current = batch.start.detach().to(device="cpu", dtype=torch.long)
    op_slots = batch.op_slots.detach().to(device="cpu", dtype=torch.long)
    for step in range(op_slots.shape[1]):
        selected = maps[rows, op_slots[:, step]]
        current = selected[rows, current]
    if not torch.equal(current, batch.target.detach().to(device="cpu", dtype=torch.long)):
        raise ValueError("episode target is inconsistent with maps and op_slots")


@dataclass(frozen=True)
class _EndpointCapture:
    batch: EpisodeBatch
    hidden: torch.Tensor
    source_states: torch.Tensor
    operator_codes: torch.Tensor
    metric: torch.Tensor


def _capture_endpoint(
    model: RecurrentOperatorModel,
    batch: EpisodeBatch,
    transitions: torch.Tensor,
    metric: torch.Tensor | None,
) -> _EndpointCapture:
    actions, states = map(int, transitions.shape)
    _validate_batch(batch, transitions)
    working = batch.to(_model_device(model))
    trace = model.run(working.tables, working.op_slots, working.start)
    if trace.operator_codes is None:
        raise ValueError("recurrent trace did not expose operator codes")
    hidden = trace.hidden[-1]
    decoder = _decoder_weight(model)
    if hidden.ndim != 2 or hidden.shape[0] != working.start.shape[0]:
        raise ValueError("model returned an invalid terminal hidden state")
    if decoder.shape != (states, hidden.shape[1]):
        raise ValueError("decoder shape does not match semantic states and hidden dimension")
    geometry = _resolved_metric(model, int(hidden.shape[1]), hidden, metric)
    return _EndpointCapture(
        batch=working,
        hidden=hidden,
        source_states=working.target,
        operator_codes=trace.operator_codes,
        metric=geometry,
    )


def _minimum_decoder_margin(
    model: RecurrentOperatorModel,
    hidden: torch.Tensor,
    targets: torch.Tensor,
    metric: torch.Tensor,
) -> torch.Tensor:
    # Dynamics stay in the model's native dtype; boundary geometry is promoted
    # so a near-zero held-out margin is not decided by float32 cancellation.
    geometry_dtype = torch.float64
    hidden = hidden.to(dtype=geometry_dtype)
    metric = metric.to(dtype=geometry_dtype)
    decoder = _decoder_weight(model).to(dtype=geometry_dtype, device=hidden.device)
    if targets.shape != (hidden.shape[0],):
        raise ValueError("targets must have one state per hidden vector")
    state_squared = torch.einsum("bi,ij,bj->b", hidden, metric, hidden)
    state_norm = state_squared.clamp_min(0.0).sqrt()
    if bool((~torch.isfinite(state_norm) | (state_norm <= torch.finfo(hidden.dtype).tiny**0.5)).any()):
        raise ValueError("packet evaluation encountered a zero or non-finite hidden ray")
    contrasts = decoder[targets].unsqueeze(1) - decoder.unsqueeze(0)
    solved = torch.linalg.solve(
        metric,
        contrasts.reshape(-1, contrasts.shape[-1]).transpose(0, 1),
    ).transpose(0, 1).reshape_as(contrasts)
    dual_norm = torch.einsum("bsi,bsi->bs", contrasts, solved).clamp_min(0.0).sqrt()
    target_mask = torch.nn.functional.one_hot(targets, decoder.shape[0]).to(torch.bool)
    degenerate = (dual_norm <= torch.finfo(hidden.dtype).tiny**0.5) & ~target_mask
    if bool(degenerate.any()):
        raise ValueError("decoder contains a degenerate class contrast")
    numerator = torch.einsum("bsi,bi->bs", contrasts, hidden)
    margin = numerator / (dual_norm * state_norm.unsqueeze(1)).clamp_min(
        torch.finfo(hidden.dtype).tiny**0.5
    )
    return margin.masked_fill(target_mask, torch.inf).min(dim=1).values


@dataclass(frozen=True)
class HeldoutPacketEvaluation:
    bank: FrozenHeldoutBank
    minimum_margin_by_suffix: torch.Tensor
    inside_by_suffix: torch.Tensor
    target_by_suffix: torch.Tensor
    prediction_by_suffix: torch.Tensor
    boundary_tolerance: float

    @property
    def inside_by_example(self) -> torch.Tensor:
        return self.inside_by_suffix.all(dim=1)

    @property
    def minimum_margin_by_example(self) -> torch.Tensor:
        return self.minimum_margin_by_suffix.min(dim=1).values

    @property
    def membership_fraction(self) -> float:
        return float(self.inside_by_example.to(torch.float64).mean())

    @property
    def word_weighted_membership_fraction(self) -> float:
        return float(self.inside_by_suffix.to(torch.float64).mean())

    def relation_group_summaries(self) -> list[dict[str, Any]]:
        groups: dict[tuple[int, ...], list[int]] = {}
        for index, signature in enumerate(self.bank.relation_signatures):
            groups.setdefault(signature, []).append(index)
        output: list[dict[str, Any]] = []
        for signature in sorted(groups):
            indices = groups[signature]
            group_inside = self.inside_by_suffix[:, indices]
            group_margin = self.minimum_margin_by_suffix[:, indices].min(dim=1).values
            output.append(
                {
                    "signature": list(signature),
                    "suffix_count": len(indices),
                    "membership_fraction": float(
                        group_inside.all(dim=1).to(torch.float64).mean()
                    ),
                    "word_weighted_membership_fraction": float(
                        group_inside.to(torch.float64).mean()
                    ),
                    "minimum_margin": _numeric_summary(group_margin),
                }
            )
        return output

    @property
    def macro_relation_group_membership_fraction(self) -> float:
        summaries = self.relation_group_summaries()
        return sum(float(item["membership_fraction"]) for item in summaries) / len(summaries)

    def to_dict(self) -> dict[str, Any]:
        exact = self.prediction_by_suffix == self.target_by_suffix
        return {
            "bank": self.bank.to_dict(),
            "examples": int(self.inside_by_suffix.shape[0]),
            "boundary_tolerance": self.boundary_tolerance,
            "strict_membership_fraction": self.membership_fraction,
            "word_weighted_membership_fraction": self.word_weighted_membership_fraction,
            "macro_relation_group_membership_fraction": (
                self.macro_relation_group_membership_fraction
            ),
            "suffix_accuracy": float(exact.to(torch.float64).mean()),
            "finite_margin_fraction": float(
                torch.isfinite(self.minimum_margin_by_suffix).to(torch.float64).mean()
            ),
            "minimum_margin": _numeric_summary(self.minimum_margin_by_example),
            "suffix_minimum_margin": _numeric_summary(self.minimum_margin_by_suffix),
            "relation_groups": self.relation_group_summaries(),
        }


def _evaluate_bank_from_capture(
    model: RecurrentOperatorModel,
    capture: _EndpointCapture,
    bank: FrozenHeldoutBank,
    *,
    boundary_tolerance: float,
) -> HeldoutPacketEvaluation:
    target_rows: list[torch.Tensor] = []
    prediction_rows: list[torch.Tensor] = []
    margin_rows: list[torch.Tensor] = []
    batch = capture.batch
    examples = int(batch.start.shape[0])
    rows = torch.arange(examples, device=capture.hidden.device)

    for word in bank.words:
        hidden = capture.hidden
        target = capture.source_states
        for canonical_action in word:
            slot = batch.canonical_to_slot[:, canonical_action]
            code = capture.operator_codes[rows, slot]
            hidden = model.step_hidden(hidden, code)
            selected_map = batch.maps[rows, slot]
            target = selected_map[rows, target]
        logits = model.decode_hidden(hidden)
        target_rows.append(target)
        prediction_rows.append(logits.argmax(dim=1))
        margin_rows.append(_minimum_decoder_margin(model, hidden, target, capture.metric))

    margin = torch.stack(margin_rows, dim=1).detach().cpu()
    targets = torch.stack(target_rows, dim=1).detach().cpu()
    predictions = torch.stack(prediction_rows, dim=1).detach().cpu()
    return HeldoutPacketEvaluation(
        bank=bank,
        minimum_margin_by_suffix=margin,
        inside_by_suffix=margin > boundary_tolerance,
        target_by_suffix=targets,
        prediction_by_suffix=predictions,
        boundary_tolerance=float(boundary_tolerance),
    )


def evaluate_heldout_packet(
    model: RecurrentOperatorModel,
    batch: EpisodeBatch,
    heldout: HeldoutBankInput,
    canonical_transitions: torch.Tensor,
    *,
    metric: torch.Tensor | None = None,
    boundary_tolerance: float = 0.0,
    max_suffixes: int | None = 128,
) -> HeldoutPacketEvaluation:
    """Measure relation-grouped held-out continuation packet survival."""

    if not math.isfinite(boundary_tolerance):
        raise ValueError("boundary_tolerance must be finite")
    transitions = _transition_tensor(canonical_transitions)
    bank = freeze_heldout_bank(heldout, transitions, max_suffixes=max_suffixes)
    with _temporary_eval(model):
        capture = _capture_endpoint(model, batch, transitions, metric)
        return _evaluate_bank_from_capture(
            model,
            capture,
            bank,
            boundary_tolerance=boundary_tolerance,
        )


@dataclass(frozen=True)
class StructuredDeepAccuracy:
    per_family: Mapping[str, Mapping[str, float | int]]
    pooled_accuracy: float
    macro_family_accuracy: float
    minimum_family_accuracy: float
    total_examples: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "per_family": {key: dict(value) for key, value in self.per_family.items()},
            "pooled_accuracy": self.pooled_accuracy,
            "macro_family_accuracy": self.macro_family_accuracy,
            "minimum_family_accuracy": self.minimum_family_accuracy,
            "total_examples": self.total_examples,
        }


def evaluate_structured_deep_accuracy(
    model: RecurrentOperatorModel,
    batches: Mapping[str, EpisodeBatch],
) -> StructuredDeepAccuracy:
    """Evaluate already-frozen deep episode banks, with no family weighting by size."""

    if not batches:
        raise ValueError("at least one structured deep batch is required")
    per_family: dict[str, dict[str, float | int]] = {}
    total_correct = 0
    total_examples = 0
    with _temporary_eval(model):
        for family in sorted(batches):
            if not isinstance(family, str) or not family:
                raise ValueError("structured family labels must be nonempty strings")
            batch = batches[family].to(_model_device(model))
            if batch.family != family:
                raise ValueError("structured family label does not match the episode batch")
            transitions = torch.from_numpy(canonical_maps(family)).to(dtype=torch.long)
            _validate_batch(batch, transitions)
            logits = model.run(batch.tables, batch.op_slots, batch.start).logits
            if logits.ndim != 2 or logits.shape[0] != batch.target.shape[0]:
                raise ValueError("model returned invalid deep logits")
            finite = torch.isfinite(logits).all(dim=1)
            correct = (logits.argmax(dim=1) == batch.target) & finite
            examples = int(correct.numel())
            count = int(correct.sum())
            total_examples += examples
            total_correct += count
            per_family[family] = {
                "accuracy": count / examples,
                "finite_fraction": float(finite.to(torch.float64).mean()),
                "examples": examples,
                "depth": int(batch.op_slots.shape[1]),
            }
    accuracies = [float(value["accuracy"]) for value in per_family.values()]
    return StructuredDeepAccuracy(
        per_family=per_family,
        pooled_accuracy=total_correct / total_examples,
        macro_family_accuracy=sum(accuracies) / len(accuracies),
        minimum_family_accuracy=min(accuracies),
        total_examples=total_examples,
    )


def _validate_null_loops(
    loops: Mapping[str, Sequence[int]],
    transitions: torch.Tensor,
) -> dict[str, Suffix]:
    if not loops:
        raise ValueError("at least one null loop is required")
    identity = tuple(range(int(transitions.shape[1])))
    output: dict[str, Suffix] = {}
    for name, raw_word in loops.items():
        if not isinstance(name, str) or not name:
            raise ValueError("null-loop names must be nonempty strings")
        words = _canonical_words((raw_word,), num_actions=int(transitions.shape[0]), name="null loop")
        word = words[0]
        if not word:
            raise ValueError("null-loop words must be nonempty")
        if _relation_signature(transitions, word) != identity:
            raise ValueError(f"{name!r} is not a null loop under canonical_transitions")
        output[name] = word
    return output


@dataclass(frozen=True)
class NullLoopHeldoutRetention:
    bank: FrozenHeldoutBank
    repeats: tuple[int, ...]
    baseline: HeldoutPacketEvaluation
    relations: Mapping[str, Mapping[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "bank": self.bank.to_dict(),
            "repeats": list(self.repeats),
            "baseline": self.baseline.to_dict(),
            "relations": {name: dict(value) for name, value in self.relations.items()},
        }


def evaluate_null_loop_retention(
    model: RecurrentOperatorModel,
    batch: EpisodeBatch,
    heldout: HeldoutBankInput,
    canonical_transitions: torch.Tensor,
    loops: Mapping[str, Sequence[int]],
    *,
    repeats: Iterable[int] = (1, 2, 4, 8, 16, 32),
    metric: torch.Tensor | None = None,
    boundary_tolerance: float = 0.0,
    max_suffixes: int | None = 128,
) -> NullLoopHeldoutRetention:
    """Apply semantic null loops, then re-audit only held-out continuations."""

    transitions = _transition_tensor(canonical_transitions)
    bank = freeze_heldout_bank(heldout, transitions, max_suffixes=max_suffixes)
    checked_loops = _validate_null_loops(loops, transitions)
    repeat_values = tuple(sorted(set(repeats)))
    if not repeat_values or any(
        isinstance(value, bool) or not isinstance(value, int) or value < 1
        for value in repeat_values
    ):
        raise ValueError("repeats must contain positive integers")
    if not math.isfinite(boundary_tolerance):
        raise ValueError("boundary_tolerance must be finite")

    with _temporary_eval(model):
        base = _capture_endpoint(model, batch, transitions, metric)
        baseline = _evaluate_bank_from_capture(
            model,
            base,
            bank,
            boundary_tolerance=boundary_tolerance,
        )
        baseline_inside = baseline.inside_by_example
        baseline_word_inside = baseline.inside_by_suffix
        baseline_margin = baseline.minimum_margin_by_example
        examples = int(base.batch.start.shape[0])
        rows = torch.arange(examples, device=base.hidden.device)
        relation_results: dict[str, dict[str, Any]] = {}

        for relation_name, word in checked_loops.items():
            hidden = base.hidden
            completed = 0
            first_crossing = torch.full((examples,), -1, dtype=torch.long)
            repeat_results: dict[str, Any] = {}
            for requested in repeat_values:
                for _ in range(requested - completed):
                    for action in word:
                        slot = base.batch.canonical_to_slot[:, action]
                        code = base.operator_codes[rows, slot]
                        hidden = model.step_hidden(hidden, code)
                completed = requested
                current_capture = _EndpointCapture(
                    batch=base.batch,
                    hidden=hidden,
                    source_states=base.source_states,
                    operator_codes=base.operator_codes,
                    metric=base.metric,
                )
                audit = _evaluate_bank_from_capture(
                    model,
                    current_capture,
                    bank,
                    boundary_tolerance=boundary_tolerance,
                )
                inside = audit.inside_by_example
                crossed = baseline_inside & ~inside & (first_crossing < 0)
                first_crossing[crossed] = requested
                baseline_count = int(baseline_inside.sum())
                baseline_word_count = int(baseline_word_inside.sum())
                retained = int((inside & baseline_inside).sum())
                retained_words = int((audit.inside_by_suffix & baseline_word_inside).sum())
                positive = baseline_margin > 0
                ratios = audit.minimum_margin_by_example[positive] / baseline_margin[positive]
                logits = model.decode_hidden(hidden)
                finite_logits = torch.isfinite(logits).all(dim=1)
                repeat_results[str(requested)] = {
                    "strict_membership_fraction": audit.membership_fraction,
                    "conditional_retention_fraction": (
                        retained / baseline_count if baseline_count else None
                    ),
                    "conditional_word_retention_fraction": (
                        retained_words / baseline_word_count if baseline_word_count else None
                    ),
                    "current_label_accuracy": float(
                        (
                            (logits.argmax(dim=1) == base.source_states)
                            & finite_logits
                        ).to(torch.float64).mean()
                    ),
                    "finite_logit_fraction": float(
                        finite_logits.to(torch.float64).mean()
                    ),
                    "minimum_margin": _numeric_summary(audit.minimum_margin_by_example),
                    "positive_baseline_margin_ratio": _numeric_summary(ratios),
                    "macro_relation_group_membership_fraction": (
                        audit.macro_relation_group_membership_fraction
                    ),
                }
            relation_results[relation_name] = {
                "word": list(word),
                "by_repeat": repeat_results,
                "first_sampled_crossing": {
                    "never_fraction_among_baseline_members": (
                        float((first_crossing[baseline_inside] < 0).to(torch.float64).mean())
                        if bool(baseline_inside.any())
                        else None
                    ),
                    "observed": [
                        int(value)
                        for value in first_crossing[first_crossing >= 0].tolist()
                    ],
                },
            }
    return NullLoopHeldoutRetention(
        bank=bank,
        repeats=repeat_values,
        baseline=baseline,
        relations=relation_results,
    )


def sample_switch_words(
    *,
    num_actions: int,
    word_length: int,
    count: int = 64,
    seed: int = 0,
    include_constant_words: bool = True,
) -> tuple[Suffix, ...]:
    """Create a deterministic without-replacement switched-word audit bank."""

    for name, value in (("num_actions", num_actions), ("word_length", word_length), ("count", count)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
    if num_actions < 2 or word_length < 1 or count < 1:
        raise ValueError("num_actions >= 2, word_length >= 1, and count >= 1 are required")
    total = num_actions**word_length
    if count > total:
        raise ValueError("count exceeds the number of distinct words")
    forced_indices = {
        sum(action * num_actions**power for power in range(word_length))
        for action in range(num_actions)
    } if include_constant_words else set()
    if len(forced_indices) > count:
        raise ValueError("count is too small to include every constant word")
    population = [index for index in range(total) if index not in forced_indices]
    chosen = set(forced_indices)
    chosen.update(random.Random(int(seed)).sample(population, count - len(chosen)))

    def decode(index: int) -> Suffix:
        digits = [0] * word_length
        for position in range(word_length - 1, -1, -1):
            index, digits[position] = divmod(index, num_actions)
        return tuple(digits)

    return tuple(decode(index) for index in sorted(chosen))


@dataclass(frozen=True)
class SampledSwitchedGain:
    words: tuple[Suffix, ...]
    word_fingerprint: str
    log_gain: torch.Tensor
    defined: torch.Tensor
    correct: torch.Tensor
    mixed_word: torch.Tensor
    mixed_minus_constant_log_gain: torch.Tensor

    def to_dict(self) -> dict[str, Any]:
        defined_log = self.log_gain[self.defined]
        finite_gain = torch.exp(
            defined_log[torch.isfinite(defined_log)].clamp_max(
                math.log(torch.finfo(torch.float64).max)
            )
        )
        return {
            "bank": {
                "word_count": len(self.words),
                "word_length": len(self.words[0]),
                "fingerprint": self.word_fingerprint,
                "constant_word_count": int((~self.mixed_word).sum()),
                "mixed_word_count": int(self.mixed_word.sum()),
            },
            "episodes": int(self.log_gain.shape[0]),
            "defined_fraction": float(self.defined.to(torch.float64).mean()),
            "word_accuracy": (
                float(self.correct[self.defined].to(torch.float64).mean())
                if bool(self.defined.any())
                else None
            ),
            "log_projective_gain": _numeric_summary(defined_log),
            "projective_gain": _numeric_summary(finite_gain),
            "mixed_minus_constant_log_gain": _numeric_summary(
                self.mixed_minus_constant_log_gain
            ),
            "mixed_enhancement_fraction": (
                float(
                    (self.mixed_minus_constant_log_gain > 0).to(torch.float64).mean()
                )
                if self.mixed_minus_constant_log_gain.numel()
                else None
            ),
        }


def evaluate_sampled_switched_gain(
    model: RecurrentOperatorModel,
    batch: EpisodeBatch,
    words: Iterable[Sequence[int]],
    canonical_transitions: torch.Tensor,
    *,
    metric: torch.Tensor | None = None,
    episode_limit: int | None = None,
    max_words: int | None = 128,
) -> SampledSwitchedGain:
    """Measure projective Jacobian gain on a fixed sampled word bank.

    This diagnostic requires square linear operator codes, but depends only on
    the :class:`RecurrentOperatorModel` interface and not on a concrete model
    class.  The behavioral endpoint is decoded after the same normalized
    projective matrix sequence used for the Jacobian.
    """

    transitions = _transition_tensor(canonical_transitions)
    bank = _canonical_words(words, num_actions=int(transitions.shape[0]), name="switch bank")
    lengths = {len(word) for word in bank}
    if len(lengths) != 1 or next(iter(lengths)) < 1:
        raise ValueError("all switched words must share one positive length")
    if max_words is not None:
        if isinstance(max_words, bool) or not isinstance(max_words, int) or max_words < 1:
            raise ValueError("max_words must be a positive integer or None")
        if len(bank) > max_words:
            raise ValueError(
                f"switched bank has {len(bank)} words, exceeding max_words={max_words}; "
                "pass None to request exhaustive evaluation"
            )
    if episode_limit is not None and (
        isinstance(episode_limit, bool) or not isinstance(episode_limit, int) or episode_limit < 1
    ):
        raise ValueError("episode_limit must be a positive integer or None")

    with _temporary_eval(model):
        capture = _capture_endpoint(model, batch, transitions, metric)
        codes = capture.operator_codes
        if codes.ndim != 4 or codes.shape[-2:] != (capture.hidden.shape[1],) * 2:
            raise ValueError("switched gain requires square linear operator codes")
        examples = int(capture.hidden.shape[0])
        if episode_limit is not None:
            examples = min(examples, episode_limit)
        log_gain = torch.full((examples, len(bank)), torch.nan, dtype=torch.float64)
        defined = torch.zeros((examples, len(bank)), dtype=torch.bool)
        correct = torch.zeros((examples, len(bank)), dtype=torch.bool)
        mixed = torch.tensor([len(set(word)) > 1 for word in bank], dtype=torch.bool)
        enhancements: list[float] = []
        geometry_metric = capture.metric.to(dtype=torch.float64)
        decoder = _decoder_weight(model).detach().to(
            device=capture.hidden.device,
            dtype=torch.float64,
        )

        for episode in range(examples):
            episode_codes = codes[episode].to(dtype=torch.float64)
            state = capture.hidden[episode].to(dtype=torch.float64)
            episode_logs: list[float] = []
            episode_types: list[bool] = []
            for word_index, word in enumerate(bank):
                slot_indices = capture.batch.canonical_to_slot[episode, list(word)]
                sequence = episode_codes[slot_indices]
                try:
                    result = projective_sequence_jacobian(sequence, state, geometry_metric)
                except ValueError:
                    continue
                value = float(result.log_worst_singular_amplification)
                endpoint_logits = decoder @ result.endpoint
                if (
                    not math.isfinite(value)
                    or not bool(torch.isfinite(result.endpoint).all())
                    or not bool(torch.isfinite(endpoint_logits).all())
                ):
                    continue
                log_gain[episode, word_index] = value
                defined[episode, word_index] = True
                target = int(capture.source_states[episode])
                for action in word:
                    slot = int(capture.batch.canonical_to_slot[episode, action])
                    target = int(capture.batch.maps[episode, slot, target])
                prediction = int(endpoint_logits.argmax())
                correct[episode, word_index] = prediction == target
                if math.isfinite(value):
                    episode_logs.append(value)
                    episode_types.append(bool(mixed[word_index]))
            constant_logs = [value for value, kind in zip(episode_logs, episode_types) if not kind]
            mixed_logs = [value for value, kind in zip(episode_logs, episode_types) if kind]
            if constant_logs and mixed_logs:
                enhancements.append(max(mixed_logs) - max(constant_logs))

    return SampledSwitchedGain(
        words=bank,
        word_fingerprint=_word_digest(transitions, bank),
        log_gain=log_gain,
        defined=defined,
        correct=correct,
        mixed_word=mixed,
        mixed_minus_constant_log_gain=torch.tensor(enhancements, dtype=torch.float64),
    )


@dataclass(frozen=True)
class FactorialEffectEstimate:
    factors: tuple[str, ...]
    estimate: float
    coded_regression_coefficient: float
    replicate_estimates: tuple[float, ...]
    sample_standard_deviation: float | None
    standard_error: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "factors": list(self.factors),
            "estimate": self.estimate,
            "coded_regression_coefficient": self.coded_regression_coefficient,
            "replicate_estimates": list(self.replicate_estimates),
            "sample_standard_deviation": self.sample_standard_deviation,
            "standard_error": self.standard_error,
        }


@dataclass(frozen=True)
class FactorialEffectSummary:
    factor_names: tuple[str, str, str]
    replicate_count: int
    grand_mean: float
    cell_means: Mapping[str, float]
    effects: Mapping[str, FactorialEffectEstimate]

    def to_dict(self) -> dict[str, Any]:
        return {
            "factor_names": list(self.factor_names),
            "replicate_count": self.replicate_count,
            "grand_mean": self.grand_mean,
            "cell_means": dict(self.cell_means),
            "effects": {name: effect.to_dict() for name, effect in self.effects.items()},
        }


def _factor_cell(cell: Sequence[bool | int]) -> FactorCell:
    if len(cell) != 3 or any(
        not isinstance(value, (bool, int)) or int(value) not in (0, 1)
        for value in cell
    ):
        raise ValueError("factorial cell keys must contain exactly three binary levels")
    return (bool(cell[0]), bool(cell[1]), bool(cell[2]))


def factorial_effect_summary(
    cells: Mapping[Sequence[bool | int], Sequence[float] | torch.Tensor],
    *,
    factor_names: tuple[str, str, str] = (
        "anonymous_composition",
        "packet_margin",
        "delayed_return",
    ),
) -> FactorialEffectSummary:
    """Compute balanced, paired contrasts for a complete 2^3 factorial.

    Values at the same replicate index are treated as paired (normally the
    same training seed).  All eight cells and equal nonzero replicate counts
    are required.  Effects use the conventional high-minus-low scale, so each
    estimate is twice the signed mean over the eight cell means (equivalently,
    the signed cell sum divided by four).
    """

    if len(factor_names) != 3 or len(set(factor_names)) != 3 or any(
        not isinstance(name, str) or not name for name in factor_names
    ):
        raise ValueError("factor_names must contain three distinct nonempty names")
    normalized: dict[FactorCell, torch.Tensor] = {}
    for raw_cell, raw_values in cells.items():
        cell = _factor_cell(raw_cell)
        if cell in normalized:
            raise ValueError(f"duplicate factorial cell after normalization: {cell}")
        values = (
            raw_values.detach().to(device="cpu", dtype=torch.float64).reshape(-1)
            if isinstance(raw_values, torch.Tensor)
            else torch.tensor(tuple(raw_values), dtype=torch.float64)
        )
        if values.numel() < 1 or not bool(torch.isfinite(values).all()):
            raise ValueError("every factorial cell must contain finite replicates")
        normalized[cell] = values
    expected = {
        (first, second, third)
        for first in (False, True)
        for second in (False, True)
        for third in (False, True)
    }
    if set(normalized) != expected:
        missing = sorted(expected - set(normalized))
        extra = sorted(set(normalized) - expected)
        raise ValueError(f"factorial requires all eight cells; missing={missing}, extra={extra}")
    replicate_counts = {int(values.numel()) for values in normalized.values()}
    if len(replicate_counts) != 1:
        raise ValueError("factorial cells must have balanced replicate counts")
    replicate_count = next(iter(replicate_counts))
    cell_means = {
        "".join("1" if level else "0" for level in cell): float(normalized[cell].mean())
        for cell in sorted(normalized)
    }
    grand = sum(cell_means.values()) / 8.0
    effects: dict[str, FactorialEffectEstimate] = {}
    indices = range(3)
    for order in (1, 2, 3):
        for selected in combinations(indices, order):
            signed = torch.zeros(replicate_count, dtype=torch.float64)
            for cell, values in normalized.items():
                sign = math.prod(1.0 if cell[index] else -1.0 for index in selected)
                signed += sign * values
            paired_effect = signed / 4.0
            estimate = float(paired_effect.mean())
            if replicate_count > 1:
                deviation = float(paired_effect.std(unbiased=True))
                standard_error = deviation / math.sqrt(replicate_count)
            else:
                deviation = None
                standard_error = None
            names = tuple(factor_names[index] for index in selected)
            label = ":".join(names)
            effects[label] = FactorialEffectEstimate(
                factors=names,
                estimate=estimate,
                coded_regression_coefficient=estimate / 2.0,
                replicate_estimates=tuple(float(value) for value in paired_effect),
                sample_standard_deviation=deviation,
                standard_error=standard_error,
            )
    return FactorialEffectSummary(
        factor_names=factor_names,
        replicate_count=replicate_count,
        grand_mean=grand,
        cell_means=cell_means,
        effects=effects,
    )


def factorial_effect_summaries(
    cells: Mapping[
        Sequence[bool | int],
        Mapping[str, Sequence[float] | torch.Tensor],
    ],
    *,
    factor_names: tuple[str, str, str] = (
        "anonymous_composition",
        "packet_margin",
        "delayed_return",
    ),
) -> dict[str, FactorialEffectSummary]:
    """Compute :func:`factorial_effect_summary` for every shared metric."""

    if not cells:
        raise ValueError("factorial metric cells must be nonempty")
    metric_sets = [set(metrics) for metrics in cells.values()]
    if not metric_sets[0] or any(metrics != metric_sets[0] for metrics in metric_sets[1:]):
        raise ValueError("every factorial cell must provide the same nonempty metric set")
    return {
        metric: factorial_effect_summary(
            {cell: metrics[metric] for cell, metrics in cells.items()},
            factor_names=factor_names,
        )
        for metric in sorted(metric_sets[0])
    }


@dataclass(frozen=True)
class HardPolarGeometryAudit:
    """Numerical audit of a hard Euclidean-polar operator control.

    ``raw_relative_minimum_singular_value`` is deliberately descriptive.  A
    polar factor can be an exact isometry even when the learned matrix before
    retraction is nearly singular; the raw statistic identifies that fragile
    regime without confusing it with failure of the hard constraint.
    """

    per_batch: Mapping[str, Mapping[str, Any]]
    aggregate: Mapping[str, Any]
    switched_sanity: Mapping[str, SampledSwitchedGain]
    orthogonality_tolerance: float
    determinant_magnitude_tolerance: float
    projective_log_gain_tolerance: float
    raw_relative_singular_floor: float

    @property
    def hard_isometry_pass(self) -> bool:
        return bool(
            self.aggregate["all_finite"]
            and self.aggregate["maximum_frobenius_orthogonality_defect"]
            <= self.orthogonality_tolerance
            and self.aggregate["maximum_spectral_orthogonality_defect"]
            <= self.orthogonality_tolerance
            and self.aggregate["maximum_absolute_determinant_magnitude_defect"]
            <= self.determinant_magnitude_tolerance
        )

    @property
    def projective_switched_gain_sanity_pass(self) -> bool:
        return bool(
            self.aggregate["switched_defined_fraction"] == 1.0
            and self.aggregate["maximum_absolute_switched_log_gain"] is not None
            and self.aggregate["maximum_absolute_switched_log_gain"]
            <= self.projective_log_gain_tolerance
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "per_batch": {name: dict(values) for name, values in self.per_batch.items()},
            "aggregate": dict(self.aggregate),
            "switched_sanity": {
                name: value.to_dict() for name, value in self.switched_sanity.items()
            },
            "thresholds": {
                "orthogonality_tolerance": self.orthogonality_tolerance,
                "determinant_magnitude_tolerance": self.determinant_magnitude_tolerance,
                "projective_log_gain_tolerance": self.projective_log_gain_tolerance,
                "raw_relative_singular_floor": self.raw_relative_singular_floor,
            },
            "hard_isometry_pass": self.hard_isometry_pass,
            "projective_switched_gain_sanity_pass": (
                self.projective_switched_gain_sanity_pass
            ),
            "raw_prepolar_well_conditioned_pass": bool(
                self.aggregate["raw_relative_minimum_singular_value"]["minimum"]
                is not None
                and self.aggregate["raw_relative_minimum_singular_value"]["minimum"]
                >= self.raw_relative_singular_floor
            ),
        }


def _operator_bundle_matrices(
    model: RecurrentOperatorModel,
    tables: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    encoder = getattr(model, "encode_operator_bundle", None)
    if not callable(encoder):
        raise TypeError(
            "hard-polar geometry audit requires encode_operator_bundle() exposing "
            "matrices and raw_residuals"
        )
    bundle = encoder(tables)
    matrices = getattr(bundle, "matrices", None)
    raw = getattr(bundle, "raw_residuals", None)
    if not isinstance(matrices, torch.Tensor) or not isinstance(raw, torch.Tensor):
        raise TypeError(
            "encode_operator_bundle() must expose tensor matrices and raw_residuals"
        )
    if (
        matrices.ndim != 4
        or matrices.shape[-1] != matrices.shape[-2]
        or raw.shape != matrices.shape
        or not matrices.is_floating_point()
        or not raw.is_floating_point()
    ):
        raise ValueError(
            "post-polar and raw pre-polar matrices must share shape "
            "(batch, operators, dimension, dimension)"
        )
    if not bool(torch.isfinite(matrices).all()) or not bool(torch.isfinite(raw).all()):
        raise ValueError("hard-polar matrices must contain only finite values")
    return matrices, raw


def evaluate_hard_polar_geometry(
    model: RecurrentOperatorModel,
    batches: Mapping[str, EpisodeBatch],
    switched_words: Mapping[str, Iterable[Sequence[int]]],
    canonical_transitions: Mapping[str, torch.Tensor],
    *,
    switched_episode_limit: int | None = None,
    max_switched_words: int | None = 128,
    orthogonality_tolerance: float = 5e-5,
    determinant_magnitude_tolerance: float = 5e-5,
    projective_log_gain_tolerance: float = 1e-3,
    raw_relative_singular_floor: float = 1e-4,
) -> HardPolarGeometryAudit:
    """Audit actual and pre-retraction matrices on frozen episode banks.

    Orthogonality and determinant checks are performed in float64 against the
    exact Euclidean metric, which is the defining gauge of the hard-polar
    control.  Switched projective gain is evaluated only on the explicitly
    supplied word banks; no exhaustive word construction occurs here.
    """

    if not batches:
        raise ValueError("at least one hard-polar audit batch is required")
    labels = set(batches)
    if set(switched_words) != labels or set(canonical_transitions) != labels:
        raise ValueError(
            "batches, switched_words, and canonical_transitions must have identical labels"
        )
    for name in labels:
        if not isinstance(name, str) or not name:
            raise ValueError("hard-polar audit labels must be nonempty strings")
    for name, value in (
        ("orthogonality_tolerance", orthogonality_tolerance),
        ("determinant_magnitude_tolerance", determinant_magnitude_tolerance),
        ("projective_log_gain_tolerance", projective_log_gain_tolerance),
        ("raw_relative_singular_floor", raw_relative_singular_floor),
    ):
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(f"{name} must be finite and nonnegative")

    per_batch: dict[str, dict[str, Any]] = {}
    all_frobenius: list[torch.Tensor] = []
    all_spectral: list[torch.Tensor] = []
    all_absolute_determinant: list[torch.Tensor] = []
    all_determinant_defect: list[torch.Tensor] = []
    all_raw_relative_minimum: list[torch.Tensor] = []
    all_post_relative_minimum: list[torch.Tensor] = []
    component_counts = {"positive": 0, "negative": 0, "zero": 0}

    with _temporary_eval(model):
        for label in sorted(labels):
            working = batches[label].to(_model_device(model))
            matrices, raw = _operator_bundle_matrices(model, working.tables)
            post64 = matrices.detach().to(device="cpu", dtype=torch.float64)
            raw64 = raw.detach().to(device="cpu", dtype=torch.float64)
            dimension = int(post64.shape[-1])
            identity = torch.eye(dimension, dtype=torch.float64)
            defect = post64.transpose(-1, -2) @ post64 - identity
            frobenius = torch.linalg.matrix_norm(defect, ord="fro")
            spectral = torch.linalg.matrix_norm(defect, ord=2)
            determinant_sign, log_absolute_determinant = torch.linalg.slogdet(post64)
            absolute_determinant = torch.exp(log_absolute_determinant)
            determinant_defect = (absolute_determinant - 1.0).abs()
            raw_singular = torch.linalg.svdvals(raw64)
            post_singular = torch.linalg.svdvals(post64)
            raw_scale = raw_singular[..., 0]
            raw_relative_minimum = torch.where(
                raw_scale > 0.0,
                raw_singular[..., -1] / raw_scale,
                torch.nan,
            )
            post_relative_minimum = (
                post_singular[..., -1]
                / post_singular[..., 0].clamp_min(torch.finfo(torch.float64).tiny)
            )
            counts = {
                "positive": int((determinant_sign > 0).sum()),
                "negative": int((determinant_sign < 0).sum()),
                "zero": int((determinant_sign == 0).sum()),
            }
            for component, count in counts.items():
                component_counts[component] += count
            per_batch[label] = {
                "examples": int(post64.shape[0]),
                "operators_per_example": int(post64.shape[1]),
                "ambient_dimension": dimension,
                "frobenius_orthogonality_defect": _numeric_summary(frobenius),
                "spectral_orthogonality_defect": _numeric_summary(spectral),
                "absolute_determinant": _numeric_summary(absolute_determinant),
                "absolute_determinant_magnitude_defect": _numeric_summary(
                    determinant_defect
                ),
                "determinant_components": counts,
                "raw_relative_minimum_singular_value": _numeric_summary(
                    raw_relative_minimum
                ),
                "raw_below_relative_singular_floor_fraction": float(
                    (
                        (~torch.isfinite(raw_relative_minimum))
                        | (raw_relative_minimum < raw_relative_singular_floor)
                    ).to(torch.float64).mean()
                ),
                "postpolar_relative_minimum_singular_value": _numeric_summary(
                    post_relative_minimum
                ),
            }
            all_frobenius.append(frobenius.reshape(-1))
            all_spectral.append(spectral.reshape(-1))
            all_absolute_determinant.append(absolute_determinant.reshape(-1))
            all_determinant_defect.append(determinant_defect.reshape(-1))
            all_raw_relative_minimum.append(raw_relative_minimum.reshape(-1))
            all_post_relative_minimum.append(post_relative_minimum.reshape(-1))

    switched: dict[str, SampledSwitchedGain] = {}
    switched_logs: list[torch.Tensor] = []
    switched_defined_count = 0
    switched_total_count = 0
    for label in sorted(labels):
        dimension = int(per_batch[label]["ambient_dimension"])
        identity_metric = torch.eye(dimension, dtype=torch.float64)
        result = evaluate_sampled_switched_gain(
            model,
            batches[label],
            switched_words[label],
            canonical_transitions[label],
            metric=identity_metric,
            episode_limit=switched_episode_limit,
            max_words=max_switched_words,
        )
        switched[label] = result
        values = result.log_gain[result.defined]
        if values.numel():
            switched_logs.append(values.to(torch.float64))
        switched_defined_count += int(result.defined.sum())
        switched_total_count += int(result.defined.numel())

    concatenated_logs = (
        torch.cat(switched_logs)
        if switched_logs
        else torch.empty(0, dtype=torch.float64)
    )
    finite_logs = concatenated_logs[torch.isfinite(concatenated_logs)]
    maximum_absolute_log_gain = (
        float(finite_logs.abs().max())
        if finite_logs.numel() == switched_defined_count and finite_logs.numel() > 0
        else None
    )
    frobenius_all = torch.cat(all_frobenius)
    spectral_all = torch.cat(all_spectral)
    determinant_all = torch.cat(all_absolute_determinant)
    determinant_defect_all = torch.cat(all_determinant_defect)
    raw_relative_all = torch.cat(all_raw_relative_minimum)
    post_relative_all = torch.cat(all_post_relative_minimum)
    aggregate: dict[str, Any] = {
        "batch_count": len(labels),
        "operator_matrix_count": int(frobenius_all.numel()),
        "all_finite": bool(
            torch.isfinite(frobenius_all).all()
            and torch.isfinite(spectral_all).all()
            and torch.isfinite(determinant_all).all()
            and torch.isfinite(post_relative_all).all()
        ),
        "maximum_frobenius_orthogonality_defect": float(frobenius_all.max()),
        "maximum_spectral_orthogonality_defect": float(spectral_all.max()),
        "absolute_determinant": _numeric_summary(determinant_all),
        "maximum_absolute_determinant_magnitude_defect": float(
            determinant_defect_all.max()
        ),
        "determinant_components": component_counts,
        "raw_relative_minimum_singular_value": _numeric_summary(raw_relative_all),
        "raw_below_relative_singular_floor_fraction": float(
            (
                (~torch.isfinite(raw_relative_all))
                | (raw_relative_all < raw_relative_singular_floor)
            ).to(torch.float64).mean()
        ),
        "postpolar_relative_minimum_singular_value": _numeric_summary(
            post_relative_all
        ),
        "switched_defined_fraction": (
            switched_defined_count / switched_total_count
            if switched_total_count
            else 0.0
        ),
        "maximum_absolute_switched_log_gain": maximum_absolute_log_gain,
    }
    return HardPolarGeometryAudit(
        per_batch=per_batch,
        aggregate=aggregate,
        switched_sanity=switched,
        orthogonality_tolerance=float(orthogonality_tolerance),
        determinant_magnitude_tolerance=float(determinant_magnitude_tolerance),
        projective_log_gain_tolerance=float(projective_log_gain_tolerance),
        raw_relative_singular_floor=float(raw_relative_singular_floor),
    )


@dataclass(frozen=True)
class CausalRolloutCondition:
    """Per-example behavioral outcome for one ambient causal condition."""

    prediction: torch.Tensor
    correct: torch.Tensor
    finite: torch.Tensor
    defined: torch.Tensor
    state_valid_fraction: float

    @property
    def accuracy(self) -> float:
        return float(self.correct.to(torch.float64).mean())

    @property
    def finite_fraction(self) -> float:
        return float(self.finite.to(torch.float64).mean())

    @property
    def defined_fraction(self) -> float:
        return float(self.defined.to(torch.float64).mean())

    def agreement_with(self, reference: "CausalRolloutCondition") -> float:
        if self.prediction.shape != reference.prediction.shape:
            raise ValueError("causal rollout conditions have incompatible shapes")
        agreement = (
            (self.prediction == reference.prediction) & self.defined & reference.defined
        )
        return float(agreement.to(torch.float64).mean())

    def to_dict(
        self,
        *,
        reference: "CausalRolloutCondition | None" = None,
    ) -> dict[str, Any]:
        return {
            "accuracy": self.accuracy,
            "finite_fraction": self.finite_fraction,
            "defined_fraction": self.defined_fraction,
            "state_valid_fraction": self.state_valid_fraction,
            "agreement_with_native": (
                self.agreement_with(reference) if reference is not None else 1.0
            ),
        }


@dataclass(frozen=True)
class AmbientComplementCausalAssay:
    """Causal comparison for an exact anchor plane and its complement."""

    midpoint: int
    steps: int
    anchor_rank: int
    ambient_dimension: int
    projector_idempotence_error: float
    projector_metric_self_adjoint_error: float
    applied_anchor_rank: int
    applied_complement_rank: int
    applied_anchor_projector_idempotence_error: float
    applied_anchor_projector_metric_self_adjoint_error: float
    applied_complement_projector_idempotence_error: float
    applied_complement_projector_metric_self_adjoint_error: float
    native: CausalRolloutCondition
    p_confined: CausalRolloutCondition
    midpoint_q_ablated: CausalRolloutCondition
    matched_random_rank_control: CausalRolloutCondition
    native_q_energy_fraction: torch.Tensor
    midpoint_q_energy_fraction: torch.Tensor
    applied_q_removed_energy_fraction: torch.Tensor
    matched_random_removed_energy_fraction: torch.Tensor
    random_energy_match_mean_absolute_error: float
    random_energy_match_maximum_absolute_error: float
    random_projector_maximum_idempotence_error: float
    random_projector_maximum_metric_self_adjoint_error: float
    random_projector_minimum_effective_rank: int
    random_projector_maximum_effective_rank: int
    ideal_matched_random_removed_energy_fraction: torch.Tensor
    ideal_random_energy_match_mean_absolute_error: float
    ideal_random_energy_match_maximum_absolute_error: float
    ideal_random_projector_maximum_idempotence_error: float
    ideal_random_projector_maximum_metric_self_adjoint_error: float
    random_control_seed: int
    random_energy_match_tolerance: float
    applied_rank_tolerance: float
    minimum_accuracy_drop: float
    specificity_margin: float
    native_accuracy_floor: float

    @property
    def complement_rank(self) -> int:
        return self.ambient_dimension - self.anchor_rank

    @property
    def p_confined_accuracy_drop(self) -> float:
        return self.native.accuracy - self.p_confined.accuracy

    @property
    def q_ablation_accuracy_drop(self) -> float:
        return self.native.accuracy - self.midpoint_q_ablated.accuracy

    @property
    def random_control_accuracy_drop(self) -> float:
        return self.native.accuracy - self.matched_random_rank_control.accuracy

    @property
    def q_specific_excess_drop(self) -> float:
        return self.q_ablation_accuracy_drop - self.random_control_accuracy_drop

    @property
    def evidence_status(self) -> str:
        if self.random_energy_match_maximum_absolute_error > self.random_energy_match_tolerance:
            return "RANDOM_CONTROL_ENERGY_MATCH_FAILED"
        if any(
            condition.finite_fraction < 1.0 or condition.defined_fraction < 1.0
            for condition in (
                self.native,
                self.p_confined,
                self.midpoint_q_ablated,
                self.matched_random_rank_control,
            )
        ):
            return "CAUSAL_ROLLOUT_UNDEFINED"
        if self.native.accuracy < self.native_accuracy_floor:
            return "NATIVE_ACCURACY_BELOW_ATTRIBUTION_FLOOR"
        if self.q_ablation_accuracy_drop < self.minimum_accuracy_drop:
            return "NO_MEANINGFUL_Q_PERFORMANCE_DROP"
        if self.q_specific_excess_drop < self.specificity_margin:
            return "Q_DROP_NOT_SPECIFIC_TO_ANCHOR_COMPLEMENT"
        return "SUPPORTED_SPECIFIC_Q_PERFORMANCE_DROP"

    @property
    def supports_specific_ambient_attribution(self) -> bool:
        return self.evidence_status == "SUPPORTED_SPECIFIC_Q_PERFORMANCE_DROP"

    def _break_fraction(self, condition: CausalRolloutCondition) -> float | None:
        eligible = self.native.correct & self.native.defined
        count = int(eligible.sum())
        if count == 0:
            return None
        broken = eligible & (~condition.correct | ~condition.defined)
        return float(broken.sum()) / count

    def _correction_fraction(self, condition: CausalRolloutCondition) -> float | None:
        eligible = (~self.native.correct) & self.native.defined
        count = int(eligible.sum())
        if count == 0:
            return None
        corrected = eligible & condition.correct & condition.defined
        return float(corrected.sum()) / count

    def to_dict(self) -> dict[str, Any]:
        return {
            "geometry": {
                "steps": self.steps,
                "midpoint": self.midpoint,
                "anchor_rank": self.anchor_rank,
                "complement_rank": self.complement_rank,
                "ambient_dimension": self.ambient_dimension,
                "projector_idempotence_error": self.projector_idempotence_error,
                "projector_metric_self_adjoint_error": (
                    self.projector_metric_self_adjoint_error
                ),
                "applied_rank_tolerance": self.applied_rank_tolerance,
                "applied_anchor_rank": self.applied_anchor_rank,
                "applied_complement_rank": self.applied_complement_rank,
                "applied_anchor_projector_idempotence_error": (
                    self.applied_anchor_projector_idempotence_error
                ),
                "applied_anchor_projector_metric_self_adjoint_error": (
                    self.applied_anchor_projector_metric_self_adjoint_error
                ),
                "applied_complement_projector_idempotence_error": (
                    self.applied_complement_projector_idempotence_error
                ),
                "applied_complement_projector_metric_self_adjoint_error": (
                    self.applied_complement_projector_metric_self_adjoint_error
                ),
            },
            "conditions": {
                "native": self.native.to_dict(),
                "p_confined": self.p_confined.to_dict(reference=self.native),
                "midpoint_q_ablated": self.midpoint_q_ablated.to_dict(
                    reference=self.native
                ),
                "matched_random_rank_control": (
                    self.matched_random_rank_control.to_dict(reference=self.native)
                ),
            },
            "performance_drops": {
                "p_confined": self.p_confined_accuracy_drop,
                "midpoint_q_ablation": self.q_ablation_accuracy_drop,
                "matched_random_rank_control": self.random_control_accuracy_drop,
                "q_specific_excess_over_random": self.q_specific_excess_drop,
            },
            "native_conditioned_transitions": {
                "native_correct_count": int(
                    (self.native.correct & self.native.defined).sum()
                ),
                "native_error_count": int(
                    ((~self.native.correct) & self.native.defined).sum()
                ),
                "p_confined_break_fraction": self._break_fraction(self.p_confined),
                "p_confined_correction_fraction": self._correction_fraction(
                    self.p_confined
                ),
                "q_ablation_break_fraction": self._break_fraction(
                    self.midpoint_q_ablated
                ),
                "q_ablation_correction_fraction": self._correction_fraction(
                    self.midpoint_q_ablated
                ),
                "matched_random_break_fraction": self._break_fraction(
                    self.matched_random_rank_control
                ),
                "matched_random_correction_fraction": self._correction_fraction(
                    self.matched_random_rank_control
                ),
            },
            "q_energy_fraction": {
                "initial": _numeric_summary(self.native_q_energy_fraction[:, 0]),
                "midpoint": _numeric_summary(self.midpoint_q_energy_fraction),
                "final": _numeric_summary(self.native_q_energy_fraction[:, -1]),
                "all_native_states": _numeric_summary(self.native_q_energy_fraction),
            },
            "matched_random_control": {
                "rank": self.complement_rank,
                "applied_minimum_effective_rank": (
                    self.random_projector_minimum_effective_rank
                ),
                "applied_maximum_effective_rank": (
                    self.random_projector_maximum_effective_rank
                ),
                "seed": self.random_control_seed,
                "state_conditioned": True,
                "removed_energy_fraction": _numeric_summary(
                    self.matched_random_removed_energy_fraction
                ),
                "q_removed_energy_fraction": _numeric_summary(
                    self.applied_q_removed_energy_fraction
                ),
                "q_energy_match_mean_absolute_error": (
                    self.random_energy_match_mean_absolute_error
                ),
                "q_energy_match_maximum_absolute_error": (
                    self.random_energy_match_maximum_absolute_error
                ),
                "maximum_idempotence_error": (
                    self.random_projector_maximum_idempotence_error
                ),
                "maximum_metric_self_adjoint_error": (
                    self.random_projector_maximum_metric_self_adjoint_error
                ),
                "ideal_construction": {
                    "removed_energy_fraction": _numeric_summary(
                        self.ideal_matched_random_removed_energy_fraction
                    ),
                    "q_energy_match_mean_absolute_error": (
                        self.ideal_random_energy_match_mean_absolute_error
                    ),
                    "q_energy_match_maximum_absolute_error": (
                        self.ideal_random_energy_match_maximum_absolute_error
                    ),
                    "maximum_idempotence_error": (
                        self.ideal_random_projector_maximum_idempotence_error
                    ),
                    "maximum_metric_self_adjoint_error": (
                        self.ideal_random_projector_maximum_metric_self_adjoint_error
                    ),
                },
            },
            "attribution": {
                "status": self.evidence_status,
                "supports_specific_ambient_attribution": (
                    self.supports_specific_ambient_attribution
                ),
                "minimum_accuracy_drop": self.minimum_accuracy_drop,
                "specificity_margin": self.specificity_margin,
                "native_accuracy_floor": self.native_accuracy_floor,
                "native_accuracy_eligible": (
                    self.native.accuracy >= self.native_accuracy_floor
                ),
                "random_energy_match_tolerance": self.random_energy_match_tolerance,
            },
        }


def _condition_from_logits(
    logits: torch.Tensor,
    target: torch.Tensor,
    *,
    final_state_valid: torch.Tensor,
    state_valid_fraction: float,
) -> CausalRolloutCondition:
    if logits.ndim != 2 or logits.shape[0] != target.shape[0]:
        raise ValueError("model returned invalid causal-assay logits")
    finite = torch.isfinite(logits).all(dim=1)
    if final_state_valid.shape != finite.shape:
        raise ValueError("final-state validity must have one value per causal-assay example")
    defined = finite & final_state_valid
    prediction = logits.argmax(dim=1)
    correct = (prediction == target) & defined
    return CausalRolloutCondition(
        prediction=prediction.detach().to(device="cpu"),
        correct=correct.detach().to(device="cpu"),
        finite=finite.detach().to(device="cpu"),
        defined=defined.detach().to(device="cpu"),
        state_valid_fraction=float(state_valid_fraction),
    )


def _metric_energy(hidden: torch.Tensor, metric: torch.Tensor) -> torch.Tensor:
    return torch.einsum("...i,ij,...j->...", hidden, metric, hidden).clamp_min(0.0)


def _metric_normalize_after_projection(
    hidden: torch.Tensor,
    metric: torch.Tensor,
    *,
    zero_norm_tolerance: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    original_dtype = hidden.dtype
    geometry_hidden = hidden.to(dtype=torch.float64)
    squared = _metric_energy(geometry_hidden, metric)
    valid = torch.isfinite(squared) & (squared > zero_norm_tolerance**2)
    denominator = squared.clamp_min(zero_norm_tolerance**2).sqrt().unsqueeze(-1)
    normalized = geometry_hidden / denominator
    normalized = torch.where(valid.unsqueeze(-1), normalized, torch.zeros_like(normalized))
    return normalized.to(dtype=original_dtype), valid


def _valid_metric_state(
    hidden: torch.Tensor,
    metric: torch.Tensor,
    *,
    zero_norm_tolerance: float,
) -> torch.Tensor:
    geometry_hidden = hidden.to(dtype=torch.float64)
    squared = _metric_energy(geometry_hidden, metric)
    return (
        torch.isfinite(geometry_hidden).all(dim=-1)
        & torch.isfinite(squared)
        & (squared > zero_norm_tolerance**2)
    )


def _energy_matched_random_projectors(
    metric: torch.Tensor,
    hidden: torch.Tensor,
    removed_energy_fraction: torch.Tensor,
    rank: int,
    generator: torch.Generator,
) -> torch.Tensor:
    """Return per-state random projectors with exactly matched removed energy.

    The construction is performed in the Euclidean chart ``G = C.T @ C``.
    Each random subspace depends only on its intervention state and requested
    energy, never on the target or on a downstream behavioral effect.
    """

    dimension = int(metric.shape[0])
    if hidden.ndim != 2 or hidden.shape[1] != dimension:
        raise ValueError("hidden states do not match the metric dimension")
    if removed_energy_fraction.shape != (hidden.shape[0],):
        raise ValueError("removed-energy fraction must have one value per hidden state")
    if rank < 1 or rank >= dimension:
        raise ValueError("random projector rank must lie strictly between zero and dimension")
    chart = torch.linalg.cholesky(metric).transpose(0, 1)
    whitened = (chart @ hidden.transpose(0, 1)).transpose(0, 1)
    whitened_norm = torch.linalg.vector_norm(whitened, dim=1, keepdim=True)
    if bool((~torch.isfinite(whitened_norm) | (whitened_norm <= 0.0)).any()):
        raise ValueError("matched random control requires finite nonzero midpoint states")
    whitened = whitened / whitened_norm
    projectors: list[torch.Tensor] = []
    for episode, state in enumerate(whitened):
        random_direction = torch.randn(
            dimension,
            dtype=torch.float64,
            device="cpu",
            generator=generator,
        )
        random_direction = random_direction - torch.dot(random_direction, state) * state
        direction_norm = torch.linalg.vector_norm(random_direction)
        if float(direction_norm) <= 64.0 * torch.finfo(torch.float64).eps:
            coordinate = torch.zeros(dimension, dtype=torch.float64)
            coordinate[int(state.abs().argmin())] = 1.0
            random_direction = coordinate - torch.dot(coordinate, state) * state
            direction_norm = torch.linalg.vector_norm(random_direction)
        orthogonal_direction = random_direction / direction_norm

        remaining = torch.randn(
            dimension,
            rank - 1,
            dtype=torch.float64,
            device="cpu",
            generator=generator,
        )
        remaining = remaining - state[:, None] * (state @ remaining)[None, :]
        remaining = remaining - orthogonal_direction[:, None] * (
            orthogonal_direction @ remaining
        )[None, :]
        remaining = torch.linalg.qr(remaining, mode="reduced").Q
        # Remove roundoff-restored excluded components once more.
        remaining = remaining - state[:, None] * (state @ remaining)[None, :]
        remaining = remaining - orthogonal_direction[:, None] * (
            orthogonal_direction @ remaining
        )[None, :]
        remaining = torch.linalg.qr(remaining, mode="reduced").Q

        energy = removed_energy_fraction[episode].clamp(0.0, 1.0)
        first = energy.sqrt() * state + (1.0 - energy).sqrt() * orthogonal_direction
        frame = torch.cat((first[:, None], remaining), dim=1)
        euclidean_projector = frame @ frame.transpose(0, 1)
        projectors.append(torch.linalg.solve(chart, euclidean_projector @ chart))
    return torch.stack(projectors)


def _component_energy_fraction(
    hidden: torch.Tensor,
    projector: torch.Tensor,
    metric: torch.Tensor,
) -> torch.Tensor:
    component = hidden @ projector.transpose(0, 1)
    numerator = _metric_energy(component, metric)
    denominator = _metric_energy(hidden, metric)
    valid = torch.isfinite(denominator) & (denominator > torch.finfo(hidden.dtype).tiny)
    return torch.where(
        valid,
        numerator / denominator.clamp_min(torch.finfo(hidden.dtype).tiny),
        torch.nan,
    )


def evaluate_ambient_complement_causality(
    model: RecurrentOperatorModel,
    batch: EpisodeBatch,
    *,
    metric: torch.Tensor | None = None,
    midpoint: int | None = None,
    random_seed: int = 0,
    zero_norm_tolerance: float = 1e-10,
    random_energy_match_tolerance: float = 1e-6,
    applied_rank_tolerance: float = 1e-5,
    minimum_accuracy_drop: float = 0.05,
    specificity_margin: float = 0.05,
    native_accuracy_floor: float = 0.75,
) -> AmbientComplementCausalAssay:
    """Test whether the exact anchor complement makes a specific contribution.

    The assay compares an untouched rollout, confinement to the exact anchor
    plane after every step, a one-time removal of ``Qh`` at the midpoint, and
    an exact rank- and energy-matched random projector ablation.  Each random
    projector is sampled deterministically and conditioned only on its native
    midpoint state and ``Q`` energy; behavioral outcomes never influence its
    construction.

    Complement energy alone is not treated as evidence of computational use.
    The returned attribution status requires a target-accuracy loss under the
    ``Q`` ablation and an additional loss relative to the matched random-rank
    control.
    """

    if not isinstance(batch, EpisodeBatch):
        raise TypeError("batch must be an EpisodeBatch")
    steps = int(batch.op_slots.shape[1])
    if steps < 2:
        raise ValueError("ambient causal assay requires at least two recurrent steps")
    if midpoint is None:
        midpoint = steps // 2
    if isinstance(midpoint, bool) or not isinstance(midpoint, int) or not (0 < midpoint < steps):
        raise ValueError("midpoint must be an integer strictly inside the rollout")
    if isinstance(random_seed, bool) or not isinstance(random_seed, int):
        raise TypeError("random_seed must be an integer")
    for name, value in (
        ("zero_norm_tolerance", zero_norm_tolerance),
        ("random_energy_match_tolerance", random_energy_match_tolerance),
        ("applied_rank_tolerance", applied_rank_tolerance),
        ("minimum_accuracy_drop", minimum_accuracy_drop),
        ("specificity_margin", specificity_margin),
        ("native_accuracy_floor", native_accuracy_floor),
    ):
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(f"{name} must be finite and nonnegative")
    if native_accuracy_floor > 1.0:
        raise ValueError("native_accuracy_floor must not exceed one")

    device = _model_device(model)
    working = batch.to(device)
    with _temporary_eval(model):
        native_trace = model.run(working.tables, working.op_slots, working.start)
        if native_trace.operator_codes is None:
            raise ValueError("ambient causal assay requires exposed recurrent operator codes")
        if len(native_trace.hidden) != steps + 1:
            raise ValueError("model trace must expose the initial state and every recurrent state")
        native_hidden = torch.stack(native_trace.hidden, dim=1)
        if native_hidden.ndim != 3 or native_hidden.shape[:2] != (
            working.start.shape[0],
            steps + 1,
        ):
            raise ValueError("model trace contains invalid recurrent hidden states")
        dimension = int(native_hidden.shape[-1])
        geometry_metric = _resolved_metric(
            model,
            dimension,
            native_hidden,
            metric,
        ).detach().to(device="cpu", dtype=torch.float64)
        semantic_states = int(working.maps.shape[-1])
        anchor_labels = torch.arange(semantic_states, device=device)
        anchors = model.initial_hidden(anchor_labels)
        if anchors.shape != (semantic_states, dimension):
            raise ValueError(
                "model initial_hidden does not define one valid semantic anchor per state"
            )
        anchor_plane = g_orthogonal_anchor_projector(
            anchors.detach().to(device="cpu", dtype=torch.float64),
            geometry_metric,
        )
        complement_rank = dimension - anchor_plane.rank
        if complement_rank < 1:
            raise ValueError(
                "ambient causal assay requires a nonvacuous anchor complement (Q rank > 0)"
            )

        p = anchor_plane.projector
        q = anchor_plane.complement
        native_hidden64 = native_hidden.detach().to(device="cpu", dtype=torch.float64)
        native_q_energy = _component_energy_fraction(
            native_hidden64,
            q,
            geometry_metric,
        )
        midpoint_hidden64 = native_hidden64[:, midpoint]
        midpoint_q_energy = native_q_energy[:, midpoint]

        generator = torch.Generator(device="cpu")
        generator.manual_seed(int(random_seed))
        random_projectors = _energy_matched_random_projectors(
            geometry_metric,
            midpoint_hidden64,
            midpoint_q_energy,
            complement_rank,
            generator,
        )
        ideal_random_energy = torch.stack(
            [
                _component_energy_fraction(
                    midpoint_hidden64[episode : episode + 1],
                    random_projectors[episode],
                    geometry_metric,
                )[0]
                for episode in range(midpoint_hidden64.shape[0])
            ]
        )
        ideal_energy_match_error = (ideal_random_energy - midpoint_q_energy).abs()
        if not bool(torch.isfinite(ideal_energy_match_error).all()):
            raise ValueError("could not construct a finite matched random-rank control")
        ideal_random_idempotence_error = torch.linalg.matrix_norm(
            random_projectors @ random_projectors - random_projectors,
            ord="fro",
        )
        ideal_random_self_adjoint_error = torch.linalg.matrix_norm(
            random_projectors.transpose(-1, -2) @ geometry_metric
            - geometry_metric @ random_projectors,
            ord="fro",
        )

        p_device = p.to(device=device, dtype=native_hidden.dtype)
        random_device = random_projectors.to(device=device, dtype=native_hidden.dtype)
        intervention_metric = geometry_metric.to(device=device)
        applied_metric = geometry_metric.to(
            device=device,
            dtype=native_hidden.dtype,
        )
        identity_device = torch.eye(
            dimension,
            dtype=native_hidden.dtype,
            device=device,
        )
        q_device = identity_device - p_device
        applied_p_idempotence_error = torch.linalg.matrix_norm(
            p_device @ p_device - p_device,
            ord="fro",
        )
        applied_p_self_adjoint_error = torch.linalg.matrix_norm(
            p_device.transpose(-1, -2) @ applied_metric
            - applied_metric @ p_device,
            ord="fro",
        )
        applied_q_idempotence_error = torch.linalg.matrix_norm(
            q_device @ q_device - q_device,
            ord="fro",
        )
        applied_q_self_adjoint_error = torch.linalg.matrix_norm(
            q_device.transpose(-1, -2) @ applied_metric
            - applied_metric @ q_device,
            ord="fro",
        )
        applied_random_idempotence_error = torch.linalg.matrix_norm(
            random_device @ random_device - random_device,
            ord="fro",
        )
        applied_random_self_adjoint_error = torch.linalg.matrix_norm(
            random_device.transpose(-1, -2) @ applied_metric
            - applied_metric @ random_device,
            ord="fro",
        )
        applied_anchor_rank = int(
            torch.linalg.matrix_rank(
                p_device.detach().to(device="cpu", dtype=torch.float64),
                atol=applied_rank_tolerance,
                rtol=0.0,
            )
        )
        applied_complement_rank = int(
            torch.linalg.matrix_rank(
                q_device.detach().to(device="cpu", dtype=torch.float64),
                atol=applied_rank_tolerance,
                rtol=0.0,
            )
        )
        applied_random_ranks = torch.linalg.matrix_rank(
            random_device.detach().to(device="cpu", dtype=torch.float64),
            atol=applied_rank_tolerance,
            rtol=0.0,
        )
        rows = torch.arange(working.start.shape[0], device=device)
        codes = native_trace.operator_codes

        def project_and_normalize(
            hidden: torch.Tensor,
            projector: torch.Tensor,
        ) -> tuple[torch.Tensor, torch.Tensor]:
            projected = hidden @ projector.transpose(0, 1)
            return _metric_normalize_after_projection(
                projected,
                intervention_metric,
                zero_norm_tolerance=zero_norm_tolerance,
            )

        confined_hidden, confined_valid = project_and_normalize(
            native_trace.hidden[0],
            p_device,
        )
        confined_valid_total = int(confined_valid.sum())
        confined_valid_count = int(confined_valid.numel())
        confined_final_valid = confined_valid
        for time_index in range(steps):
            selected = codes[rows, working.op_slots[:, time_index]]
            confined_hidden = model.step_hidden(confined_hidden, selected)
            confined_hidden, valid = project_and_normalize(confined_hidden, p_device)
            confined_valid_total += int(valid.sum())
            confined_valid_count += int(valid.numel())
            confined_final_valid = valid
        confined_logits = model.decode_hidden(confined_hidden)

        q_ablated_hidden, q_valid = project_and_normalize(
            native_trace.hidden[midpoint],
            p_device,
        )
        q_valid_total = int(q_valid.sum())
        q_valid_count = int(q_valid.numel())
        q_final_valid = q_valid
        for time_index in range(midpoint, steps):
            selected = codes[rows, working.op_slots[:, time_index]]
            q_ablated_hidden = model.step_hidden(q_ablated_hidden, selected)
            q_final_valid = _valid_metric_state(
                q_ablated_hidden,
                intervention_metric,
                zero_norm_tolerance=zero_norm_tolerance,
            )
            q_valid_total += int(q_final_valid.sum())
            q_valid_count += int(q_ablated_hidden.shape[0])
        q_ablated_logits = model.decode_hidden(q_ablated_hidden)

        random_complement = identity_device.unsqueeze(0) - random_device
        random_projected = torch.bmm(
            random_complement,
            native_trace.hidden[midpoint].unsqueeze(-1),
        ).squeeze(-1)
        # The registered energy receipt concerns the exact cast-and-matmul
        # vectors used by the two interventions before their common
        # normalization, not the ideal float64 projectors alone.
        applied_midpoint = native_trace.hidden[midpoint]
        applied_q_projected = applied_midpoint @ p_device.transpose(0, 1)
        applied_q_removed64 = (
            applied_midpoint - applied_q_projected
        ).detach().to(device="cpu", dtype=torch.float64)
        applied_random_removed64 = (
            applied_midpoint - random_projected
        ).detach().to(device="cpu", dtype=torch.float64)
        applied_midpoint64 = applied_midpoint.detach().to(
            device="cpu", dtype=torch.float64
        )
        applied_denominator = _metric_energy(applied_midpoint64, geometry_metric)
        denominator_floor = torch.finfo(torch.float64).tiny
        applied_q_energy = _metric_energy(
            applied_q_removed64, geometry_metric
        ) / applied_denominator.clamp_min(denominator_floor)
        applied_random_energy = _metric_energy(
            applied_random_removed64, geometry_metric
        ) / applied_denominator.clamp_min(denominator_floor)
        applied_energy_match_error = (
            applied_random_energy - applied_q_energy
        ).abs()
        if not bool(torch.isfinite(applied_energy_match_error).all()):
            raise ValueError("applied random-rank control has non-finite energy match")
        random_ablated_hidden, random_valid = _metric_normalize_after_projection(
            random_projected,
            intervention_metric,
            zero_norm_tolerance=zero_norm_tolerance,
        )
        random_valid_total = int(random_valid.sum())
        random_valid_count = int(random_valid.numel())
        random_final_valid = random_valid
        for time_index in range(midpoint, steps):
            selected = codes[rows, working.op_slots[:, time_index]]
            random_ablated_hidden = model.step_hidden(random_ablated_hidden, selected)
            random_final_valid = _valid_metric_state(
                random_ablated_hidden,
                intervention_metric,
                zero_norm_tolerance=zero_norm_tolerance,
            )
            random_valid_total += int(random_final_valid.sum())
            random_valid_count += int(random_ablated_hidden.shape[0])
        random_logits = model.decode_hidden(random_ablated_hidden)

        native_state_valid = _valid_metric_state(
            native_hidden,
            intervention_metric,
            zero_norm_tolerance=zero_norm_tolerance,
        )
        native_condition = _condition_from_logits(
            native_trace.logits,
            working.target,
            final_state_valid=native_state_valid[:, -1],
            state_valid_fraction=float(native_state_valid.float().mean()),
        )
        confined_condition = _condition_from_logits(
            confined_logits,
            working.target,
            final_state_valid=confined_final_valid,
            state_valid_fraction=confined_valid_total / confined_valid_count,
        )
        q_condition = _condition_from_logits(
            q_ablated_logits,
            working.target,
            final_state_valid=q_final_valid,
            state_valid_fraction=q_valid_total / q_valid_count,
        )
        random_condition = _condition_from_logits(
            random_logits,
            working.target,
            final_state_valid=random_final_valid,
            state_valid_fraction=random_valid_total / random_valid_count,
        )

    return AmbientComplementCausalAssay(
        midpoint=midpoint,
        steps=steps,
        anchor_rank=anchor_plane.rank,
        ambient_dimension=dimension,
        projector_idempotence_error=float(anchor_plane.idempotence_error),
        projector_metric_self_adjoint_error=float(
            anchor_plane.metric_self_adjoint_error
        ),
        applied_anchor_rank=applied_anchor_rank,
        applied_complement_rank=applied_complement_rank,
        applied_anchor_projector_idempotence_error=float(
            applied_p_idempotence_error
        ),
        applied_anchor_projector_metric_self_adjoint_error=float(
            applied_p_self_adjoint_error
        ),
        applied_complement_projector_idempotence_error=float(
            applied_q_idempotence_error
        ),
        applied_complement_projector_metric_self_adjoint_error=float(
            applied_q_self_adjoint_error
        ),
        native=native_condition,
        p_confined=confined_condition,
        midpoint_q_ablated=q_condition,
        matched_random_rank_control=random_condition,
        native_q_energy_fraction=native_q_energy,
        midpoint_q_energy_fraction=midpoint_q_energy,
        applied_q_removed_energy_fraction=applied_q_energy,
        matched_random_removed_energy_fraction=applied_random_energy,
        random_energy_match_mean_absolute_error=float(
            applied_energy_match_error.mean()
        ),
        random_energy_match_maximum_absolute_error=float(
            applied_energy_match_error.max()
        ),
        random_projector_maximum_idempotence_error=float(
            applied_random_idempotence_error.max()
        ),
        random_projector_maximum_metric_self_adjoint_error=float(
            applied_random_self_adjoint_error.max()
        ),
        random_projector_minimum_effective_rank=int(applied_random_ranks.min()),
        random_projector_maximum_effective_rank=int(applied_random_ranks.max()),
        ideal_matched_random_removed_energy_fraction=ideal_random_energy,
        ideal_random_energy_match_mean_absolute_error=float(
            ideal_energy_match_error.mean()
        ),
        ideal_random_energy_match_maximum_absolute_error=float(
            ideal_energy_match_error.max()
        ),
        ideal_random_projector_maximum_idempotence_error=float(
            ideal_random_idempotence_error.max()
        ),
        ideal_random_projector_maximum_metric_self_adjoint_error=float(
            ideal_random_self_adjoint_error.max()
        ),
        random_control_seed=int(random_seed),
        random_energy_match_tolerance=float(random_energy_match_tolerance),
        applied_rank_tolerance=float(applied_rank_tolerance),
        minimum_accuracy_drop=float(minimum_accuracy_drop),
        specificity_margin=float(specificity_margin),
        native_accuracy_floor=float(native_accuracy_floor),
    )


@dataclass(frozen=True)
class PacketClosureArmEvaluation:
    heldout_packet: HeldoutPacketEvaluation
    structured_deep: StructuredDeepAccuracy
    null_loop_retention: NullLoopHeldoutRetention
    switched_gain: SampledSwitchedGain

    def to_dict(self) -> dict[str, Any]:
        return {
            "heldout_packet": self.heldout_packet.to_dict(),
            "structured_deep": self.structured_deep.to_dict(),
            "null_loop_retention": self.null_loop_retention.to_dict(),
            "switched_gain": self.switched_gain.to_dict(),
        }


def evaluate_packet_closure_arm(
    model: RecurrentOperatorModel,
    packet_batch: EpisodeBatch,
    deep_batches: Mapping[str, EpisodeBatch],
    heldout: HeldoutBankInput,
    canonical_transitions: torch.Tensor,
    null_loops: Mapping[str, Sequence[int]],
    switched_words: Iterable[Sequence[int]],
    *,
    null_repeats: Iterable[int] = (1, 2, 4, 8, 16, 32),
    metric: torch.Tensor | None = None,
    boundary_tolerance: float = 0.0,
    max_suffixes: int | None = 128,
    max_switched_words: int | None = 128,
    switched_episode_limit: int | None = None,
) -> PacketClosureArmEvaluation:
    """Run the four independent v0.4 measurements for one trained arm."""

    return PacketClosureArmEvaluation(
        heldout_packet=evaluate_heldout_packet(
            model,
            packet_batch,
            heldout,
            canonical_transitions,
            metric=metric,
            boundary_tolerance=boundary_tolerance,
            max_suffixes=max_suffixes,
        ),
        structured_deep=evaluate_structured_deep_accuracy(model, deep_batches),
        null_loop_retention=evaluate_null_loop_retention(
            model,
            packet_batch,
            heldout,
            canonical_transitions,
            null_loops,
            repeats=null_repeats,
            metric=metric,
            boundary_tolerance=boundary_tolerance,
            max_suffixes=max_suffixes,
        ),
        switched_gain=evaluate_sampled_switched_gain(
            model,
            packet_batch,
            switched_words,
            canonical_transitions,
            metric=metric,
            episode_limit=switched_episode_limit,
            max_words=max_switched_words,
        ),
    )


__all__ = [
    "AmbientComplementCausalAssay",
    "CausalRolloutCondition",
    "FactorialEffectEstimate",
    "FactorialEffectSummary",
    "FrozenHeldoutBank",
    "HeldoutPacketEvaluation",
    "HardPolarGeometryAudit",
    "NullLoopHeldoutRetention",
    "PacketClosureArmEvaluation",
    "SampledSwitchedGain",
    "StructuredDeepAccuracy",
    "evaluate_ambient_complement_causality",
    "evaluate_hard_polar_geometry",
    "evaluate_heldout_packet",
    "evaluate_null_loop_retention",
    "evaluate_packet_closure_arm",
    "evaluate_sampled_switched_gain",
    "evaluate_structured_deep_accuracy",
    "factorial_effect_summaries",
    "factorial_effect_summary",
    "freeze_heldout_bank",
    "sample_switch_words",
]
