from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import product
import math
from typing import Callable, Iterable, Mapping, Sequence

import torch


Word = tuple[int, ...]
StepFunction = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


@dataclass(frozen=True)
class ActionEquivalenceClass:
    """Words with the same action on the demonstrated finite states."""

    signature: tuple[int, ...]
    word_indices: tuple[int, ...]
    words: tuple[Word, ...]


@dataclass(frozen=True)
class ScaleConsistency:
    """One non-overlapping word-depth bin of the consistency objective."""

    scale: int
    loss: torch.Tensor
    pair_count: int
    weight: float


@dataclass(frozen=True)
class CompositionConsistencyResult:
    """Differentiable loss and an auditable account of how it was formed."""

    loss: torch.Tensor
    consistency_loss: torch.Tensor
    separation_loss: torch.Tensor
    per_scale: tuple[ScaleConsistency, ...]
    equivalence_classes: tuple[ActionEquivalenceClass, ...]
    equivalent_pair_count: int
    separation_pair_count: int
    endpoints: torch.Tensor
    observed_states: torch.Tensor


_INTEGER_DTYPES = {
    torch.uint8,
    torch.int8,
    torch.int16,
    torch.int32,
    torch.int64,
}


def enumerate_action_words(
    num_actions: int,
    max_depth: int,
    *,
    min_depth: int = 0,
) -> tuple[Word, ...]:
    """Enumerate anonymous action words in depth-then-lexicographic order."""

    if isinstance(num_actions, bool) or not isinstance(num_actions, int):
        raise TypeError("num_actions must be an integer")
    if isinstance(min_depth, bool) or isinstance(max_depth, bool):
        raise TypeError("depth bounds must be integers")
    if not isinstance(min_depth, int) or not isinstance(max_depth, int):
        raise TypeError("depth bounds must be integers")
    if num_actions < 1:
        raise ValueError("num_actions must be positive")
    if min_depth < 0 or max_depth < min_depth:
        raise ValueError("depth bounds must satisfy 0 <= min_depth <= max_depth")
    return tuple(
        tuple(word)
        for depth in range(min_depth, max_depth + 1)
        for word in product(range(num_actions), repeat=depth)
    )


def finite_transition_map(action_table: torch.Tensor, *, atol: float = 1e-6) -> torch.Tensor:
    """Return an integer ``[actions, states]`` map from a finite table.

    Both integer transition maps and exact deterministic one-hot tables with shape
    ``[actions, source_states, target_states]`` are accepted. The table is treated
    as supervisory evidence, not as a differentiable model output.
    """

    if not isinstance(action_table, torch.Tensor):
        raise TypeError("action_table must be a torch.Tensor")
    if not math.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and nonnegative")

    if action_table.ndim == 2:
        if action_table.dtype not in _INTEGER_DTYPES:
            raise TypeError("a rank-two action_table must have an integer dtype")
        transition_map = action_table.to(dtype=torch.long)
    elif action_table.ndim == 3:
        if not action_table.is_floating_point():
            raise TypeError("a rank-three action_table must be floating point")
        actions, sources, targets = action_table.shape
        if actions < 1 or sources < 1 or targets != sources:
            raise ValueError("a dense action_table must have shape [A, S, S] with A,S > 0")
        detached = action_table.detach()
        if not bool(torch.isfinite(detached).all()):
            raise ValueError("action_table must contain only finite values")
        transition_map = detached.argmax(dim=-1)
        exact = torch.nn.functional.one_hot(transition_map, num_classes=targets).to(detached.dtype)
        if not torch.allclose(detached, exact, atol=atol, rtol=0.0):
            raise ValueError("dense action_table rows must be deterministic one-hot transitions")
    else:
        raise ValueError("action_table must have shape [A, S] or [A, S, S]")

    if transition_map.shape[0] < 1 or transition_map.shape[1] < 1:
        raise ValueError("action_table must contain at least one action and one state")
    state_count = int(transition_map.shape[1])
    if bool(((transition_map < 0) | (transition_map >= state_count)).any()):
        raise ValueError("action_table contains a target outside the finite state space")
    return transition_map


def _normalize_words(words: Iterable[Sequence[int]], num_actions: int) -> tuple[Word, ...]:
    normalized: list[Word] = []
    for raw_word in words:
        try:
            word = tuple(raw_word)
        except TypeError as exc:
            raise TypeError("each word must be an iterable of integer action slots") from exc
        for action in word:
            if isinstance(action, bool) or not isinstance(action, int):
                raise TypeError("word actions must be integers")
            if action < 0 or action >= num_actions:
                raise ValueError("word contains an action outside the demonstrated alphabet")
        normalized.append(word)
    if not normalized:
        raise ValueError("at least one word is required")
    if len(set(normalized)) != len(normalized):
        raise ValueError("words must be unique")
    return tuple(normalized)


def _observed_state_indices(
    observed_states: Sequence[int] | torch.Tensor | None,
    state_count: int,
    *,
    device: torch.device,
) -> torch.Tensor:
    if observed_states is None:
        return torch.arange(state_count, dtype=torch.long, device=device)
    if isinstance(observed_states, torch.Tensor):
        if observed_states.ndim != 1 or observed_states.dtype not in _INTEGER_DTYPES:
            raise TypeError("observed_states must be a one-dimensional integer tensor")
        indices = observed_states.to(device=device, dtype=torch.long)
    else:
        values = tuple(observed_states)
        if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
            raise TypeError("observed_states must contain integers")
        indices = torch.tensor(values, dtype=torch.long, device=device)
    if indices.numel() < 1:
        raise ValueError("observed_states must not be empty")
    if torch.unique(indices).numel() != indices.numel():
        raise ValueError("observed_states must be unique")
    if bool(((indices < 0) | (indices >= state_count)).any()):
        raise ValueError("observed_states contains an index outside the finite state space")
    return indices


def _execute_transition_map(transition_map: torch.Tensor, word: Word) -> torch.Tensor:
    current = torch.arange(transition_map.shape[1], dtype=torch.long, device=transition_map.device)
    for action in word:
        current = transition_map[action, current]
    return current


def induced_action(
    action_table: torch.Tensor,
    word: Sequence[int],
) -> torch.Tensor:
    """Execute ``word`` left-to-right on every source state in the table."""

    transition_map = finite_transition_map(action_table)
    normalized = _normalize_words((word,), int(transition_map.shape[0]))[0]
    return _execute_transition_map(transition_map, normalized)


def group_words_by_demonstrated_action(
    action_table: torch.Tensor,
    words: Iterable[Sequence[int]],
    *,
    observed_states: Sequence[int] | torch.Tensor | None = None,
) -> tuple[ActionEquivalenceClass, ...]:
    """Group words solely by their induced action on demonstrated states.

    No generator name, family label, or hand-written relation is inspected. This
    remains valid when visible operator slots are arbitrarily permuted per episode.
    With a partial ``observed_states`` set, equivalence means observational
    equivalence on exactly that set and nowhere else.
    """

    transition_map = finite_transition_map(action_table)
    normalized = _normalize_words(words, int(transition_map.shape[0]))
    observed = _observed_state_indices(
        observed_states,
        int(transition_map.shape[1]),
        device=transition_map.device,
    )
    grouped: dict[tuple[int, ...], list[tuple[int, Word]]] = defaultdict(list)
    for index, word in enumerate(normalized):
        action = _execute_transition_map(transition_map, word)
        signature = tuple(int(value) for value in action[observed].tolist())
        grouped[signature].append((index, word))
    return tuple(
        ActionEquivalenceClass(
            signature=signature,
            word_indices=tuple(index for index, _ in members),
            words=tuple(word for _, word in members),
        )
        for signature, members in grouped.items()
    )


def spd_metric_from_factor(factor: torch.Tensor, *, diagonal_floor: float = 1e-4) -> torch.Tensor:
    """Construct a differentiable positive-definite metric ``L L^T + floor I``."""

    if not isinstance(factor, torch.Tensor) or factor.ndim != 2:
        raise TypeError("factor must be a rank-two torch.Tensor")
    if not factor.is_floating_point() or factor.shape[0] != factor.shape[1] or factor.shape[0] < 1:
        raise ValueError("factor must be a nonempty square floating-point tensor")
    if not math.isfinite(diagonal_floor) or diagonal_floor <= 0:
        raise ValueError("diagonal_floor must be finite and positive")
    identity = torch.eye(factor.shape[0], dtype=factor.dtype, device=factor.device)
    return factor @ factor.transpose(0, 1) + diagonal_floor * identity


def _checked_metric(
    metric: torch.Tensor | None,
    dimension: int,
    *,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor | None:
    if metric is None:
        return None
    if not isinstance(metric, torch.Tensor) or metric.ndim != 2:
        raise TypeError("metric must be a rank-two torch.Tensor or None")
    if metric.shape != (dimension, dimension):
        raise ValueError(f"metric must have shape ({dimension}, {dimension})")
    if not metric.is_floating_point():
        raise TypeError("metric must have a floating-point dtype")
    candidate = metric.to(dtype=dtype, device=device)
    detached = candidate.detach()
    if not bool(torch.isfinite(detached).all()):
        raise ValueError("metric must contain only finite values")
    tolerance = 64.0 * torch.finfo(dtype).eps * max(1, dimension)
    if not torch.allclose(detached, detached.transpose(0, 1), atol=tolerance, rtol=tolerance):
        raise ValueError("metric must be symmetric")
    _, info = torch.linalg.cholesky_ex(detached)
    if int(info.item()) != 0:
        raise ValueError("metric must be positive definite")
    return candidate


def oriented_projective_chordal_loss(
    left: torch.Tensor,
    right: torch.Tensor,
    metric: torch.Tensor | None = None,
    *,
    eps: float = 1e-12,
) -> torch.Tensor:
    """Return ``1 - cos_G(left, right)`` on oriented positive rays.

    The loss is invariant to independent positive rescaling of either endpoint.
    Under a coordinate change ``h' = C h`` it is also invariant when the metric is
    transported by ``G' = C^{-T} G C^{-1}``. Antipodes are deliberately distinct
    and have loss two. Near-zero vectors incur loss rather than becoming valid rays.
    """

    if not isinstance(left, torch.Tensor) or not isinstance(right, torch.Tensor):
        raise TypeError("left and right must be torch.Tensor objects")
    if not left.is_floating_point() or not right.is_floating_point():
        raise TypeError("left and right must have floating-point dtypes")
    if left.shape[-1:] != right.shape[-1:] or left.shape[-1] < 1:
        raise ValueError("left and right must share a positive ambient dimension")
    if left.dtype != right.dtype or left.device != right.device:
        raise ValueError("left and right must share dtype and device")
    if not math.isfinite(eps) or eps <= 0:
        raise ValueError("eps must be finite and positive")
    try:
        left_b, right_b = torch.broadcast_tensors(left, right)
    except RuntimeError as exc:
        raise ValueError("left and right leading dimensions must be broadcastable") from exc
    checked_metric = _checked_metric(
        metric,
        int(left.shape[-1]),
        dtype=left.dtype,
        device=left.device,
    )
    if checked_metric is None:
        cross = (left_b * right_b).sum(dim=-1)
        left_sq = (left_b * left_b).sum(dim=-1)
        right_sq = (right_b * right_b).sum(dim=-1)
    else:
        cross = torch.einsum("...i,ij,...j->...", left_b, checked_metric, right_b)
        left_sq = torch.einsum("...i,ij,...j->...", left_b, checked_metric, left_b)
        right_sq = torch.einsum("...i,ij,...j->...", right_b, checked_metric, right_b)
    denominator = left_sq.clamp_min(eps * eps).sqrt() * right_sq.clamp_min(eps * eps).sqrt()
    cosine = (cross / denominator).clamp(-1.0, 1.0)
    return 1.0 - cosine


def rollout_word_endpoints(
    initial_states: torch.Tensor,
    operator_codes: torch.Tensor,
    words: Iterable[Sequence[int]],
    step_fn: StepFunction,
) -> tuple[torch.Tensor, tuple[Word, ...]]:
    """Execute every word from every finite start state with shared-prefix reuse.

    ``step_fn`` receives tensors shaped ``[states, hidden]`` and
    ``[states, *code_shape]``. The output must have the same shape as the hidden
    batch. Every distinct word prefix is evaluated once, so this is suitable for
    the small exhaustive word banks used by finite-table episodes.
    """

    if not isinstance(initial_states, torch.Tensor) or initial_states.ndim != 2:
        raise TypeError("initial_states must be a rank-two torch.Tensor")
    if not initial_states.is_floating_point() or initial_states.shape[0] < 1 or initial_states.shape[1] < 1:
        raise ValueError("initial_states must be a nonempty floating-point [S, H] tensor")
    if not isinstance(operator_codes, torch.Tensor) or operator_codes.ndim < 2:
        raise TypeError("operator_codes must have shape [A, *code_shape]")
    if not operator_codes.is_floating_point() or operator_codes.shape[0] < 1:
        raise ValueError("operator_codes must contain at least one floating-point code")
    if initial_states.dtype != operator_codes.dtype or initial_states.device != operator_codes.device:
        raise ValueError("initial_states and operator_codes must share dtype and device")
    if not callable(step_fn):
        raise TypeError("step_fn must be callable")

    normalized = _normalize_words(words, int(operator_codes.shape[0]))
    state_count = int(initial_states.shape[0])
    cache: dict[Word, torch.Tensor] = {(): initial_states}

    def endpoint(word: Word) -> torch.Tensor:
        cached = cache.get(word)
        if cached is not None:
            return cached
        parent = endpoint(word[:-1])
        code = operator_codes[word[-1]]
        code_batch = code.unsqueeze(0).expand((state_count,) + tuple(code.shape))
        updated = step_fn(parent, code_batch)
        if not isinstance(updated, torch.Tensor) or updated.shape != initial_states.shape:
            raise ValueError("step_fn must return a tensor with the same shape as initial_states")
        if updated.dtype != initial_states.dtype or updated.device != initial_states.device:
            raise ValueError("step_fn output must preserve hidden dtype and device")
        cache[word] = updated
        return updated

    endpoints = torch.stack(tuple(endpoint(word) for word in normalized), dim=0)
    return endpoints, normalized


def _scale_bins(
    words: tuple[Word, ...],
    scales: Sequence[int] | None,
) -> tuple[int, ...]:
    if scales is None:
        return tuple(sorted({len(word) for word in words}))
    result = tuple(scales)
    if not result:
        raise ValueError("scales must not be empty")
    if any(isinstance(scale, bool) or not isinstance(scale, int) for scale in result):
        raise TypeError("scales must contain integers")
    if any(scale < 0 for scale in result) or tuple(sorted(set(result))) != result:
        raise ValueError("scales must be unique, nonnegative, and strictly increasing")
    if result[-1] < max(map(len, words)):
        raise ValueError("the largest scale must cover the longest word")
    return result


def _pair_scale(left: Word, right: Word, scale_bins: tuple[int, ...]) -> int:
    depth = max(len(left), len(right))
    for scale in scale_bins:
        if depth <= scale:
            return scale
    raise RuntimeError("scale bins do not cover a word pair")


def multiscale_composition_consistency_loss(
    endpoints: torch.Tensor,
    action_table: torch.Tensor,
    words: Iterable[Sequence[int]],
    *,
    observed_states: Sequence[int] | torch.Tensor | None = None,
    metric: torch.Tensor | None = None,
    scales: Sequence[int] | None = None,
    scale_weights: Mapping[int, float] | None = None,
    separation_weight: float = 0.0,
    separation_margin: float = 0.5,
    eps: float = 1e-12,
) -> CompositionConsistencyResult:
    """Build an anonymous, multiscale projective composition objective.

    ``endpoints[w, s]`` is the latent endpoint obtained by executing word ``w``
    from demonstrated finite state ``s``. Word pairs are positive examples exactly
    when the supplied transition table demonstrates the same induced action. The
    pairs are assigned once to the smallest requested scale covering both word
    lengths, preventing long words from silently dominating through nested recounts.

    An optional contrastive term keeps demonstrably different actions apart only
    on source states where their finite outputs differ. It is useful when this loss
    is trained without a strong terminal objective, but defaults to zero so the
    consistency term does not invent semantic inequalities beyond the table.
    """

    if not isinstance(endpoints, torch.Tensor) or endpoints.ndim != 3:
        raise TypeError("endpoints must be a rank-three [words, states, hidden] tensor")
    if not endpoints.is_floating_point() or min(endpoints.shape) < 1:
        raise ValueError("endpoints must be nonempty and floating point")
    transition_map = finite_transition_map(action_table)
    normalized = _normalize_words(words, int(transition_map.shape[0]))
    if endpoints.shape[0] != len(normalized):
        raise ValueError("the first endpoint dimension must equal the number of words")
    if endpoints.shape[1] != transition_map.shape[1]:
        raise ValueError("the endpoint state dimension must match the finite action table")
    if not math.isfinite(separation_weight) or separation_weight < 0:
        raise ValueError("separation_weight must be finite and nonnegative")
    if not math.isfinite(separation_margin) or not 0 <= separation_margin <= 2:
        raise ValueError("separation_margin must lie in [0, 2]")

    table_observed = _observed_state_indices(
        observed_states,
        int(transition_map.shape[1]),
        device=transition_map.device,
    )
    endpoint_observed = table_observed.to(device=endpoints.device)
    selected_endpoints = endpoints.index_select(1, endpoint_observed)
    classes = group_words_by_demonstrated_action(
        transition_map,
        normalized,
        observed_states=table_observed,
    )
    bins = _scale_bins(normalized, scales)

    weights: dict[int, float] = {}
    for scale in bins:
        value = 1.0 if scale_weights is None else float(scale_weights.get(scale, 0.0))
        if not math.isfinite(value) or value < 0:
            raise ValueError("scale weights must be finite and nonnegative")
        weights[scale] = value
    if scale_weights is not None:
        unknown = set(scale_weights).difference(bins)
        if unknown:
            raise ValueError(f"scale_weights contains unknown scales: {sorted(unknown)}")

    by_scale: dict[int, list[torch.Tensor]] = {scale: [] for scale in bins}
    equivalent_pair_count = 0
    for action_class in classes:
        indices = action_class.word_indices
        for offset, left_index in enumerate(indices):
            for right_index in indices[offset + 1 :]:
                value = oriented_projective_chordal_loss(
                    selected_endpoints[left_index],
                    selected_endpoints[right_index],
                    metric,
                    eps=eps,
                ).mean()
                scale = _pair_scale(normalized[left_index], normalized[right_index], bins)
                by_scale[scale].append(value)
                equivalent_pair_count += 1

    differentiable_zero = endpoints.sum() * 0.0
    scale_records: list[ScaleConsistency] = []
    active_losses: list[torch.Tensor] = []
    active_weights: list[float] = []
    for scale in bins:
        values = by_scale[scale]
        scale_loss = torch.stack(values).mean() if values else differentiable_zero
        scale_records.append(
            ScaleConsistency(
                scale=scale,
                loss=scale_loss,
                pair_count=len(values),
                weight=weights[scale],
            )
        )
        if values and weights[scale] > 0:
            active_losses.append(scale_loss)
            active_weights.append(weights[scale])
    if equivalent_pair_count and not active_losses:
        raise ValueError("at least one occupied scale must have positive weight")
    if active_losses:
        numerator = sum(weight * value for weight, value in zip(active_weights, active_losses))
        consistency = numerator / sum(active_weights)
    else:
        consistency = differentiable_zero

    separation_values: list[torch.Tensor] = []
    if separation_weight > 0:
        for left_class_index, left_class in enumerate(classes):
            left_signature = torch.tensor(
                left_class.signature,
                dtype=torch.long,
                device=endpoints.device,
            )
            for right_class in classes[left_class_index + 1 :]:
                right_signature = torch.tensor(
                    right_class.signature,
                    dtype=torch.long,
                    device=endpoints.device,
                )
                mismatch = left_signature != right_signature
                if not bool(mismatch.any()):
                    raise RuntimeError("distinct action classes unexpectedly share a signature")
                for left_index in left_class.word_indices:
                    for right_index in right_class.word_indices:
                        distance = oriented_projective_chordal_loss(
                            selected_endpoints[left_index, mismatch],
                            selected_endpoints[right_index, mismatch],
                            metric,
                            eps=eps,
                        ).mean()
                        separation_values.append(torch.relu(distance.new_tensor(separation_margin) - distance))
    separation = torch.stack(separation_values).mean() if separation_values else differentiable_zero
    total = consistency + separation_weight * separation
    return CompositionConsistencyResult(
        loss=total,
        consistency_loss=consistency,
        separation_loss=separation,
        per_scale=tuple(scale_records),
        equivalence_classes=classes,
        equivalent_pair_count=equivalent_pair_count,
        separation_pair_count=len(separation_values),
        endpoints=endpoints,
        observed_states=endpoint_observed,
    )


def anonymous_multiscale_composition_loss(
    initial_states: torch.Tensor,
    operator_codes: torch.Tensor,
    action_table: torch.Tensor,
    words: Iterable[Sequence[int]],
    step_fn: StepFunction,
    **loss_options: object,
) -> CompositionConsistencyResult:
    """Roll out a recurrent substrate and evaluate anonymous composition closure."""

    endpoints, normalized = rollout_word_endpoints(initial_states, operator_codes, words, step_fn)
    return multiscale_composition_consistency_loss(
        endpoints,
        action_table,
        normalized,
        **loss_options,
    )
