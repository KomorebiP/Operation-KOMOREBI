from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import product
import math
import operator as index_operator
import random
from typing import Callable, Hashable, Iterable, Mapping, Sequence

import torch


Suffix = tuple[int, ...]


@dataclass(frozen=True)
class OrientedRayBatch:
    """Normalized positive-ray representatives with explicit validity metadata."""

    representatives: torch.Tensor
    norms: torch.Tensor
    valid: torch.Tensor


@dataclass(frozen=True)
class ContinuationConstraintSet:
    """Homogeneous half-space constraints defining one finite-horizon packet."""

    normals: torch.Tensor
    suffixes: tuple[Suffix, ...]
    constraint_suffix_index: torch.Tensor
    targets: torch.Tensor
    competitors: torch.Tensor
    source_state: int

    @property
    def dimension(self) -> int:
        return int(self.normals.shape[-1])

    @property
    def constraint_count(self) -> int:
        return int(self.normals.shape[0])

    @property
    def horizon(self) -> int:
        return max((len(word) for word in self.suffixes), default=-1)


@dataclass(frozen=True)
class PacketMarginResult:
    """Scale-invariant signed distances to continuation boundaries."""

    signed_margins: torch.Tensor
    minimum_margin: torch.Tensor
    active_constraint: torch.Tensor
    inside: torch.Tensor
    valid_states: torch.Tensor
    valid_constraints: torch.Tensor
    state_norms: torch.Tensor
    normal_dual_norms: torch.Tensor


@dataclass(frozen=True)
class SuffixSplit:
    """A frozen construction/held-out split made before constraints are built."""

    construction: tuple[Suffix, ...]
    heldout: tuple[Suffix, ...]
    construction_group_keys: tuple[Hashable, ...]
    heldout_group_keys: tuple[Hashable, ...]
    seed: int


@dataclass(frozen=True)
class ContinuationConstraintSplit:
    construction: ContinuationConstraintSet
    heldout: ContinuationConstraintSet
    suffix_split: SuffixSplit


@dataclass(frozen=True)
class PacketErosionSummary:
    """Sample-based erosion summary for a nested sequence of packet constraints."""

    depths: tuple[int, ...]
    constraint_counts: tuple[int, ...]
    minimum_margin_by_depth: torch.Tensor
    inside_by_depth: torch.Tensor
    survival_fraction: torch.Tensor
    conditional_retention_fraction: torch.Tensor
    median_margin: torch.Tensor
    first_failure_depth: torch.Tensor
    valid_states: torch.Tensor
    monotonicity_violations: int


def _validate_state_tensor(states: torch.Tensor) -> None:
    if not isinstance(states, torch.Tensor):
        raise TypeError("states must be a torch.Tensor")
    if states.ndim < 1:
        raise ValueError("states must have at least one dimension")
    if states.shape[-1] < 1:
        raise ValueError("the ambient dimension must be positive")
    if not states.is_floating_point():
        raise TypeError("states must have a floating-point dtype")


def _validated_metric(
    metric: torch.Tensor | None,
    dimension: int,
    *,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor | None:
    if metric is None:
        return None
    if not isinstance(metric, torch.Tensor):
        raise TypeError("metric must be a torch.Tensor or None")
    if metric.shape != (dimension, dimension):
        raise ValueError(f"metric must have shape ({dimension}, {dimension})")
    if not metric.is_floating_point():
        raise TypeError("metric must have a floating-point dtype")
    candidate = metric.to(dtype=dtype, device=device)
    if not bool(torch.isfinite(candidate).all()):
        raise ValueError("metric must contain only finite values")
    tolerance = 64.0 * torch.finfo(candidate.dtype).eps * max(1, dimension)
    if not torch.allclose(candidate, candidate.transpose(0, 1), atol=tolerance, rtol=tolerance):
        raise ValueError("metric must be symmetric")
    _, info = torch.linalg.cholesky_ex(candidate)
    if int(info.item()) != 0:
        raise ValueError("metric must be positive definite")
    return candidate


def _metric_norms(states: torch.Tensor, metric: torch.Tensor | None) -> torch.Tensor:
    if metric is None:
        return torch.linalg.vector_norm(states, dim=-1)
    squared = torch.einsum("...i,ij,...j->...", states, metric, states)
    roundoff = 64.0 * torch.finfo(states.dtype).eps
    return squared.clamp_min(-roundoff).clamp_min(0.0).sqrt()


def normalize_oriented_rays(
    states: torch.Tensor,
    metric: torch.Tensor | None = None,
    *,
    eps: float = 1e-12,
) -> OrientedRayBatch:
    """Normalize by positive scale without identifying antipodal states.

    Invalid or zero states are returned as zero representatives and marked false in
    ``valid``. This makes batched diagnostics total while preventing a zero vector
    from being silently treated as a projective point.
    """

    _validate_state_tensor(states)
    if eps <= 0 or not math.isfinite(eps):
        raise ValueError("eps must be finite and positive")
    checked_metric = _validated_metric(
        metric,
        states.shape[-1],
        dtype=states.dtype,
        device=states.device,
    )
    norms = _metric_norms(states, checked_metric)
    finite_states = torch.isfinite(states).all(dim=-1)
    valid = finite_states & torch.isfinite(norms) & (norms > eps)
    safe_norms = torch.where(valid, norms, torch.ones_like(norms))
    representatives = states / safe_norms.unsqueeze(-1)
    representatives = torch.where(valid.unsqueeze(-1), representatives, torch.zeros_like(representatives))
    return OrientedRayBatch(representatives=representatives, norms=norms, valid=valid)


def oriented_projective_normalize(
    states: torch.Tensor,
    metric: torch.Tensor | None = None,
    *,
    eps: float = 1e-12,
    zero_policy: str = "raise",
) -> torch.Tensor:
    """Return positive-ray representatives, with an explicit zero-state policy."""

    rays = normalize_oriented_rays(states, metric, eps=eps)
    if zero_policy == "raise":
        invalid = int((~rays.valid).sum().item())
        if invalid:
            raise ValueError(f"cannot normalize {invalid} zero or non-finite state(s)")
    elif zero_policy != "zeros":
        raise ValueError("zero_policy must be 'raise' or 'zeros'")
    return rays.representatives


def oriented_projective_distance(
    left: torch.Tensor,
    right: torch.Tensor,
    metric: torch.Tensor | None = None,
    *,
    eps: float = 1e-12,
    zero_policy: str = "raise",
) -> torch.Tensor:
    """Angular distance on oriented rays. Antipodes have distance pi, not zero."""

    if left.shape != right.shape:
        raise ValueError("left and right must have identical shapes")
    if left.dtype != right.dtype or left.device != right.device:
        raise ValueError("left and right must have identical dtypes and devices")
    left_unit = oriented_projective_normalize(left, metric, eps=eps, zero_policy=zero_policy)
    right_unit = oriented_projective_normalize(right, metric, eps=eps, zero_policy=zero_policy)
    checked_metric = _validated_metric(
        metric,
        left.shape[-1],
        dtype=left.dtype,
        device=left.device,
    )
    if checked_metric is None:
        cosine = (left_unit * right_unit).sum(dim=-1)
    else:
        cosine = torch.einsum("...i,ij,...j->...", left_unit, checked_metric, right_unit)
    distance = torch.acos(cosine.clamp(-1.0, 1.0))
    if zero_policy == "zeros":
        valid = normalize_oriented_rays(left, metric, eps=eps).valid
        valid &= normalize_oriented_rays(right, metric, eps=eps).valid
        distance = torch.where(valid, distance, torch.full_like(distance, torch.nan))
    return distance


def enumerate_suffixes(
    num_actions: int,
    max_depth: int,
    *,
    min_depth: int = 0,
) -> tuple[Suffix, ...]:
    """Enumerate action words in depth-then-lexicographic order."""

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
    words: list[Suffix] = []
    for depth in range(min_depth, max_depth + 1):
        words.extend(tuple(int(action) for action in word) for word in product(range(num_actions), repeat=depth))
    return tuple(words)


def _canonical_suffixes(suffixes: Iterable[Sequence[int]], num_actions: int | None = None) -> tuple[Suffix, ...]:
    canonical_words: list[Suffix] = []
    for word in suffixes:
        converted: list[int] = []
        for action in word:
            if isinstance(action, bool):
                raise TypeError("suffix actions must be integers, not booleans")
            try:
                converted.append(index_operator.index(action))
            except TypeError as error:
                raise TypeError("suffix actions must be integers") from error
        canonical_words.append(tuple(converted))
    canonical = tuple(canonical_words)
    if len(set(canonical)) != len(canonical):
        raise ValueError("suffixes must be unique")
    if num_actions is not None:
        for word in canonical:
            if any(action < 0 or action >= num_actions for action in word):
                raise ValueError("suffix contains an action outside the operator alphabet")
    return canonical


def suffix_transition_signature(transitions: torch.Tensor, suffix: Sequence[int]) -> tuple[int, ...]:
    """Return the action word's transition on every semantic state.

    This signature can be supplied as an equivalence key when splitting suffixes,
    keeping relation-equivalent words on the same side of the split.
    """

    if not isinstance(transitions, torch.Tensor) or transitions.ndim != 2:
        raise ValueError("transitions must have shape [num_actions, num_states]")
    num_actions, num_states = transitions.shape
    if num_actions < 1 or num_states < 1:
        raise ValueError("transitions must be nonempty")
    integer_dtypes = {torch.int8, torch.int16, torch.int32, torch.int64, torch.uint8}
    if transitions.dtype not in integer_dtypes:
        raise TypeError("transitions must have an integer dtype")
    if not bool(((transitions >= 0) & (transitions < num_states)).all()):
        raise ValueError("transitions contain an invalid target state")
    word = _canonical_suffixes((suffix,), num_actions)[0]
    state = torch.arange(num_states, dtype=torch.long, device=transitions.device)
    table = transitions.to(dtype=torch.long)
    for action in word:
        state = table[action, state]
    return tuple(int(value) for value in state.detach().cpu().tolist())


def split_suffixes_for_validation(
    suffixes: Iterable[Sequence[int]],
    *,
    heldout_fraction: float = 0.25,
    seed: int = 0,
    equivalence_key: Callable[[Suffix], Hashable] | None = None,
    stratify_by_depth: bool = True,
    keep_empty_in_construction: bool = True,
) -> SuffixSplit:
    """Split words before packet construction to prevent definitional leakage.

    ``equivalence_key`` may identify algebraically equivalent words. Entire key
    groups are assigned together, so equivalent suffixes cannot occur in both the
    construction and held-out constraint sets.
    """

    if not 0.0 < heldout_fraction < 1.0:
        raise ValueError("heldout_fraction must lie strictly between zero and one")
    canonical = _canonical_suffixes(suffixes)
    if len(canonical) < 2:
        raise ValueError("at least two distinct suffixes are required for a split")

    key_function = equivalence_key if equivalence_key is not None else lambda word: word
    keyed: dict[Hashable, list[Suffix]] = defaultdict(list)
    for word in canonical:
        key = key_function(word)
        try:
            hash(key)
        except TypeError as error:
            raise TypeError("equivalence_key must return hashable values") from error
        keyed[key].append(word)

    forced_construction: set[Hashable] = set()
    if keep_empty_in_construction and () in canonical:
        forced_construction.add(key_function(()))

    available_keys = [key for key in keyed if key not in forced_construction]
    if len(available_keys) < 1:
        raise ValueError("no group remains available for held-out evaluation")

    strata: dict[int, list[Hashable]] = defaultdict(list)
    if stratify_by_depth and equivalence_key is None:
        for key in available_keys:
            word = keyed[key][0]
            strata[len(word)].append(key)
    else:
        strata[0].extend(available_keys)

    rng = random.Random(int(seed))
    heldout_keys: set[Hashable] = set()
    for stratum in sorted(strata):
        keys = list(strata[stratum])
        rng.shuffle(keys)
        if len(keys) == 1:
            count = 0
        else:
            count = max(1, min(len(keys) - 1, int(round(heldout_fraction * len(keys)))))
        heldout_keys.update(keys[:count])

    if not heldout_keys:
        candidates = list(available_keys)
        rng.shuffle(candidates)
        heldout_keys.add(candidates[0])

    construction_keys = set(keyed) - heldout_keys
    if not construction_keys:
        raise ValueError("split would leave no construction suffixes")

    construction = tuple(word for word in canonical if key_function(word) in construction_keys)
    heldout = tuple(word for word in canonical if key_function(word) in heldout_keys)
    split = SuffixSplit(
        construction=construction,
        heldout=heldout,
        construction_group_keys=tuple(sorted(construction_keys, key=repr)),
        heldout_group_keys=tuple(sorted(heldout_keys, key=repr)),
        seed=int(seed),
    )
    validate_suffix_split(split, equivalence_key=equivalence_key)
    return split


def validate_suffix_split(
    split: SuffixSplit,
    *,
    equivalence_key: Callable[[Suffix], Hashable] | None = None,
) -> None:
    """Reject exact-word or equivalence-group leakage in a suffix split."""

    construction = _canonical_suffixes(split.construction)
    heldout = _canonical_suffixes(split.heldout)
    if not construction or not heldout:
        raise ValueError("construction and held-out suffix sets must both be nonempty")
    overlap = set(construction) & set(heldout)
    if overlap:
        raise ValueError(f"suffix leakage detected for {len(overlap)} exact word(s)")
    key_function = equivalence_key if equivalence_key is not None else lambda word: word
    construction_keys = {key_function(word) for word in construction}
    heldout_keys = {key_function(word) for word in heldout}
    group_overlap = construction_keys & heldout_keys
    if group_overlap:
        raise ValueError(f"equivalence-group leakage detected for {len(group_overlap)} group(s)")


def _validate_system(
    decoder: torch.Tensor,
    operators: torch.Tensor,
    transitions: torch.Tensor,
) -> tuple[int, int, int, torch.dtype]:
    if not isinstance(decoder, torch.Tensor) or decoder.ndim != 2 or not decoder.is_floating_point():
        raise ValueError("decoder must be a floating tensor with shape [num_states, dimension]")
    if not isinstance(operators, torch.Tensor) or operators.ndim != 3 or not operators.is_floating_point():
        raise ValueError("operators must be a floating tensor with shape [num_actions, dimension, dimension]")
    if decoder.device != operators.device:
        raise ValueError("decoder and operators must be on the same device")
    num_states, dimension = decoder.shape
    num_actions = operators.shape[0]
    if num_states < 2 or dimension < 1 or num_actions < 1:
        raise ValueError("the system must have at least two states, one action, and one ambient dimension")
    if operators.shape[1:] != (dimension, dimension):
        raise ValueError("operator dimensions do not match the decoder")
    if not isinstance(transitions, torch.Tensor):
        raise TypeError("transitions must be a torch.Tensor")
    integer_dtypes = {
        torch.int8,
        torch.int16,
        torch.int32,
        torch.int64,
        torch.uint8,
    }
    if transitions.shape != (num_actions, num_states) or transitions.dtype not in integer_dtypes:
        raise ValueError("transitions must be an integer tensor with shape [num_actions, num_states]")
    if not bool(((transitions >= 0) & (transitions < num_states)).all()):
        raise ValueError("transitions contain an invalid target state")
    if not bool(torch.isfinite(decoder).all()) or not bool(torch.isfinite(operators).all()):
        raise ValueError("decoder and operators must be finite")
    dtype = torch.promote_types(decoder.dtype, operators.dtype)
    return num_states, num_actions, dimension, dtype


def build_continuation_constraints(
    decoder: torch.Tensor,
    operators: torch.Tensor,
    transitions: torch.Tensor,
    source_state: int,
    *,
    suffixes: Iterable[Sequence[int]] | None = None,
    max_depth: int | None = None,
) -> ContinuationConstraintSet:
    """Construct pulled-back decoder inequalities for one semantic source state."""

    num_states, num_actions, dimension, dtype = _validate_system(decoder, operators, transitions)
    if isinstance(source_state, bool) or not isinstance(source_state, int):
        raise TypeError("source_state must be an integer")
    if source_state < 0 or source_state >= num_states:
        raise ValueError("source_state is outside the semantic state space")
    if (suffixes is None) == (max_depth is None):
        raise ValueError("provide exactly one of suffixes or max_depth")
    if max_depth is not None:
        words = enumerate_suffixes(num_actions, max_depth)
    else:
        assert suffixes is not None
        words = _canonical_suffixes(suffixes, num_actions)
    if not words:
        raise ValueError("at least one suffix is required")

    work_decoder = decoder.to(dtype=dtype)
    work_operators = operators.to(dtype=dtype)
    table = transitions.to(device=decoder.device, dtype=torch.long)
    identity = torch.eye(dimension, dtype=dtype, device=decoder.device)
    normal_rows: list[torch.Tensor] = []
    suffix_indices: list[int] = []
    targets: list[int] = []
    competitors: list[int] = []

    for suffix_index, word in enumerate(words):
        composite = identity
        target = int(source_state)
        for action in word:
            composite = work_operators[action] @ composite
            target = int(table[action, target].item())
        for competitor in range(num_states):
            if competitor == target:
                continue
            contrast = work_decoder[target] - work_decoder[competitor]
            normal_rows.append(composite.transpose(0, 1) @ contrast)
            suffix_indices.append(suffix_index)
            targets.append(target)
            competitors.append(competitor)

    normals = torch.stack(normal_rows, dim=0)
    index_device = decoder.device
    return ContinuationConstraintSet(
        normals=normals,
        suffixes=words,
        constraint_suffix_index=torch.tensor(suffix_indices, dtype=torch.long, device=index_device),
        targets=torch.tensor(targets, dtype=torch.long, device=index_device),
        competitors=torch.tensor(competitors, dtype=torch.long, device=index_device),
        source_state=int(source_state),
    )


def build_constraint_split(
    decoder: torch.Tensor,
    operators: torch.Tensor,
    transitions: torch.Tensor,
    source_state: int,
    split: SuffixSplit,
    *,
    equivalence_key: Callable[[Suffix], Hashable] | None = None,
) -> ContinuationConstraintSplit:
    """Build construction and held-out constraints only after validating the split."""

    validate_suffix_split(split, equivalence_key=equivalence_key)
    construction = build_continuation_constraints(
        decoder,
        operators,
        transitions,
        source_state,
        suffixes=split.construction,
    )
    heldout = build_continuation_constraints(
        decoder,
        operators,
        transitions,
        source_state,
        suffixes=split.heldout,
    )
    return ContinuationConstraintSplit(construction=construction, heldout=heldout, suffix_split=split)


def continuation_margins(
    states: torch.Tensor,
    constraints: ContinuationConstraintSet | torch.Tensor,
    metric: torch.Tensor | None = None,
    *,
    eps: float = 1e-12,
    boundary_tolerance: float = 0.0,
) -> PacketMarginResult:
    """Evaluate normalized signed continuation margins for arbitrary state batches.

    Zero/non-finite states receive NaN margins and are never inside. A zero or
    non-finite constraint normal represents an unsatisfiable strict inequality and
    receives margin ``-inf`` for valid states.
    """

    _validate_state_tensor(states)
    normals = constraints.normals if isinstance(constraints, ContinuationConstraintSet) else constraints
    if not isinstance(normals, torch.Tensor) or normals.ndim != 2 or not normals.is_floating_point():
        raise ValueError("constraints must supply a floating matrix of normal rows")
    if normals.shape[1] != states.shape[-1]:
        raise ValueError("constraint dimension does not match the states")
    if normals.device != states.device:
        raise ValueError("states and constraints must be on the same device")
    if not math.isfinite(boundary_tolerance):
        raise ValueError("boundary_tolerance must be finite")
    checked_metric = _validated_metric(
        metric,
        states.shape[-1],
        dtype=states.dtype,
        device=states.device,
    )
    rays = normalize_oriented_rays(states, checked_metric, eps=eps)
    work_normals = normals.to(dtype=states.dtype)
    finite_normals = torch.isfinite(work_normals).all(dim=-1)
    if checked_metric is None:
        dual_norms = torch.linalg.vector_norm(work_normals, dim=-1)
    else:
        solved = torch.linalg.solve(checked_metric, work_normals.transpose(0, 1)).transpose(0, 1)
        dual_squared = (work_normals * solved).sum(dim=-1)
        dual_norms = dual_squared.clamp_min(0.0).sqrt()
    valid_constraints = finite_normals & torch.isfinite(dual_norms) & (dual_norms > eps)

    leading_shape = states.shape[:-1]
    if normals.shape[0] == 0:
        signed = states.new_empty((*leading_shape, 0))
        minimum = torch.full(leading_shape, torch.inf, dtype=states.dtype, device=states.device)
        active = torch.full(leading_shape, -1, dtype=torch.long, device=states.device)
        inside = rays.valid.clone()
    else:
        numerators = torch.einsum("...i,ci->...c", rays.representatives, work_normals)
        safe_dual = torch.where(valid_constraints, dual_norms, torch.ones_like(dual_norms))
        signed = numerators / safe_dual
        negative_infinity = torch.full_like(signed, -torch.inf)
        signed = torch.where(valid_constraints, signed, negative_infinity)
        signed = torch.where(rays.valid.unsqueeze(-1), signed, torch.full_like(signed, torch.nan))
        safe_for_min = torch.where(rays.valid.unsqueeze(-1), signed, torch.full_like(signed, torch.inf))
        minimum, active = safe_for_min.min(dim=-1)
        minimum = torch.where(rays.valid, minimum, torch.full_like(minimum, torch.nan))
        active = torch.where(rays.valid, active, torch.full_like(active, -1))
        inside = rays.valid & valid_constraints.all() & (minimum > boundary_tolerance)

    return PacketMarginResult(
        signed_margins=signed,
        minimum_margin=minimum,
        active_constraint=active,
        inside=inside,
        valid_states=rays.valid,
        valid_constraints=valid_constraints,
        state_norms=rays.norms,
        normal_dual_norms=dual_norms,
    )


def summarize_packet_erosion(
    states: torch.Tensor,
    constraints_by_depth: Mapping[int, ContinuationConstraintSet],
    metric: torch.Tensor | None = None,
    *,
    eps: float = 1e-12,
    boundary_tolerance: float = 0.0,
    monotonicity_tolerance: float = 1e-7,
) -> PacketErosionSummary:
    """Summarize how sampled packet membership and margins change with horizon."""

    _validate_state_tensor(states)
    if states.ndim != 2:
        raise ValueError("erosion summaries require states with shape [examples, dimension]")
    if not constraints_by_depth:
        raise ValueError("constraints_by_depth must be nonempty")
    if any(not isinstance(depth, int) or isinstance(depth, bool) for depth in constraints_by_depth):
        raise TypeError("depth keys must be integers")
    depths = tuple(sorted(constraints_by_depth))
    if depths[0] < 0:
        raise ValueError("depth keys must be nonnegative")
    sources = {constraints_by_depth[depth].source_state for depth in depths}
    if len(sources) != 1:
        raise ValueError("all erosion constraint sets must use the same source state")
    for depth in depths:
        constraints = constraints_by_depth[depth]
        if constraints.horizon > depth:
            raise ValueError("a constraint set cannot contain suffixes deeper than its depth key")
    results = [
        continuation_margins(
            states,
            constraints_by_depth[depth],
            metric,
            eps=eps,
            boundary_tolerance=boundary_tolerance,
        )
        for depth in depths
    ]
    margins = torch.stack([result.minimum_margin for result in results], dim=1)
    inside = torch.stack([result.inside for result in results], dim=1)
    valid = results[0].valid_states
    valid_count = int(valid.sum().item())
    if valid_count:
        survival = inside[valid].to(dtype=states.dtype).mean(dim=0)
        finite_margins = margins[valid]
        median = torch.nanmedian(finite_margins, dim=0).values
    else:
        survival = torch.full((len(depths),), torch.nan, dtype=states.dtype, device=states.device)
        median = torch.full_like(survival, torch.nan)

    initial_inside = inside[:, 0] & valid
    initial_count = int(initial_inside.sum().item())
    if initial_count:
        retention = inside[initial_inside].to(dtype=states.dtype).mean(dim=0)
    else:
        retention = torch.full((len(depths),), torch.nan, dtype=states.dtype, device=states.device)

    first_failure = torch.full((states.shape[0],), -1, dtype=torch.long, device=states.device)
    first_failure[~valid] = -2
    for column, depth in enumerate(depths):
        newly_failed = valid & (first_failure < 0) & (~inside[:, column])
        first_failure[newly_failed] = depth

    if len(depths) > 1:
        comparable = torch.isfinite(margins[:, :-1]) & torch.isfinite(margins[:, 1:])
        increases = comparable & (margins[:, 1:] > margins[:, :-1] + monotonicity_tolerance)
        reentries = inside[:, 1:] & (~inside[:, :-1])
        violations = int((increases | reentries).sum().item())
    else:
        violations = 0

    return PacketErosionSummary(
        depths=depths,
        constraint_counts=tuple(constraints_by_depth[depth].constraint_count for depth in depths),
        minimum_margin_by_depth=margins,
        inside_by_depth=inside,
        survival_fraction=survival,
        conditional_retention_fraction=retention,
        median_margin=median,
        first_failure_depth=first_failure,
        valid_states=valid,
        monotonicity_violations=violations,
    )


__all__ = [
    "ContinuationConstraintSet",
    "ContinuationConstraintSplit",
    "OrientedRayBatch",
    "PacketErosionSummary",
    "PacketMarginResult",
    "Suffix",
    "SuffixSplit",
    "build_constraint_split",
    "build_continuation_constraints",
    "continuation_margins",
    "enumerate_suffixes",
    "normalize_oriented_rays",
    "oriented_projective_distance",
    "oriented_projective_normalize",
    "split_suffixes_for_validation",
    "suffix_transition_signature",
    "summarize_packet_erosion",
    "validate_suffix_split",
]
