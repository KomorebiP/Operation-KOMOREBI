"""Codebook-resistant state and operator transport assays.

This module layers on top of the v0.2 affine transport implementation.  It is
deliberately task-agnostic: callers provide paired latent tensors, semantic
attribute labels, and (for functional checks) the model's step/decode
callbacks.  That keeps the same assay usable for the original eight-state
executor and for v0.3 multi-attribute tasks.

The important distinction is between:

* transporting a decoded label (a finite codebook), and
* transporting variation *within* a label plus the operators acting on it.

Accordingly, the API always keeps centroid/decode-reembed baselines visible,
supports within-codebook shuffled fits, and reports conditional residual and
cycle metrics in addition to endpoint accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Hashable, Mapping, Protocol, Sequence

import torch
from torch.nn import functional as F

from .transport import AffineTransport, random_matched_transport


TRANSPORT_ASSAY_SCHEMA = "komorebi.neuralese.functional_transport.v3"


class AppliesTensor(Protocol):
    """Minimal common protocol for state and operator transports."""

    def apply(self, values: torch.Tensor) -> torch.Tensor: ...


def _as_feature_matrix(values: torch.Tensor, *, name: str) -> torch.Tensor:
    if not torch.is_tensor(values) or values.ndim < 2:
        raise ValueError(f"{name} must have shape (examples, ...)")
    if values.shape[0] < 1:
        raise ValueError(f"{name} must contain at least one example")
    if not torch.is_floating_point(values):
        raise ValueError(f"{name} must be floating point")
    if not bool(torch.isfinite(values).all()):
        raise ValueError(f"{name} contains non-finite values")
    return values.reshape(values.shape[0], -1)


def _as_label_matrix(labels: torch.Tensor, *, name: str = "labels") -> torch.Tensor:
    if not torch.is_tensor(labels) or labels.ndim not in (1, 2):
        raise ValueError(f"{name} must have shape (examples,) or (examples, attributes)")
    if labels.shape[0] < 1:
        raise ValueError(f"{name} must contain at least one example")
    return labels.reshape(labels.shape[0], -1)


def _validate_pair(
    source: torch.Tensor,
    target: torch.Tensor,
    *,
    source_name: str,
    target_name: str,
) -> tuple[torch.Tensor, torch.Tensor]:
    source_flat = _as_feature_matrix(source, name=source_name)
    target_flat = _as_feature_matrix(target, name=target_name)
    if source.shape[0] != target.shape[0]:
        raise ValueError(f"{source_name} and {target_name} example counts differ")
    if source.device != target.device:
        raise ValueError(f"{source_name} and {target_name} must be on the same device")
    if source.dtype != target.dtype:
        raise ValueError(f"{source_name} and {target_name} must have the same dtype")
    return source_flat, target_flat


@dataclass(frozen=True)
class AffineFitDiagnostics:
    examples: int
    source_dim: int
    target_dim: int
    centered_rank: int
    maximum_rank: int
    condition_number: float | None
    largest_singular_value: float
    smallest_retained_singular_value: float | None
    ridge: float
    calculation_dtype: str

    def to_serializable(self) -> dict[str, Any]:
        return {
            "examples": self.examples,
            "source_dim": self.source_dim,
            "target_dim": self.target_dim,
            "centered_rank": self.centered_rank,
            "maximum_rank": self.maximum_rank,
            "condition_number": self.condition_number,
            "largest_singular_value": self.largest_singular_value,
            "smallest_retained_singular_value": self.smallest_retained_singular_value,
            "ridge": self.ridge,
            "calculation_dtype": self.calculation_dtype,
        }


def fit_stable_affine_transport(
    source_hidden: torch.Tensor,
    target_hidden: torch.Tensor,
    *,
    ridge: float = 1e-5,
    calculation_dtype: torch.dtype = torch.float64,
) -> tuple[AffineTransport, AffineFitDiagnostics]:
    """Fit centered ridge regression with an explicit SVD in fixed precision.

    V0.2 used float32 normal equations.  Residual-transport contrasts can be
    much smaller than total label variance, so v0.3 fixes the calculation dtype,
    avoids squaring the design condition number, and records rank/conditioning.
    Returned parameters are cast back to the model tensor dtype for direct use.
    """

    source, target = _validate_pair(
        source_hidden,
        target_hidden,
        source_name="source_hidden",
        target_name="target_hidden",
    )
    if ridge < 0:
        raise ValueError("ridge must be nonnegative")
    if calculation_dtype not in (torch.float32, torch.float64):
        raise ValueError("calculation_dtype must be torch.float32 or torch.float64")
    source_calc = source.to(dtype=calculation_dtype)
    target_calc = target.to(dtype=calculation_dtype)
    source_mean = source_calc.mean(dim=0)
    target_mean = target_calc.mean(dim=0)
    x = source_calc - source_mean
    y = target_calc - target_mean
    u, singular_values, vh = torch.linalg.svd(x, full_matrices=False)
    if singular_values.numel() == 0:
        raise ValueError("at least one singular value is required for affine fitting")
    tolerance = (
        max(x.shape)
        * torch.finfo(calculation_dtype).eps
        * singular_values.max()
    )
    retained = singular_values > tolerance
    rank = int(retained.sum().item())
    if rank == 0:
        condition: float | None = None
        smallest: float | None = None
    else:
        smallest_tensor = singular_values[retained][-1]
        condition = float((singular_values[0] / smallest_tensor).detach().cpu())
        smallest = float(smallest_tensor.detach().cpu())
    if ridge == 0:
        gains = torch.where(
            retained,
            singular_values.reciprocal(),
            torch.zeros_like(singular_values),
        )
    else:
        gains = singular_values / (singular_values.square() + float(ridge))
    weight_calc = (vh.T * gains.unsqueeze(0)) @ (u.T @ y)
    bias_calc = target_mean - source_mean @ weight_calc
    if not bool(torch.isfinite(weight_calc).all()) or not bool(torch.isfinite(bias_calc).all()):
        raise RuntimeError("affine transport fit produced non-finite parameters")
    dtype = source_hidden.dtype
    transport = AffineTransport(
        weight_calc.to(dtype=dtype),
        bias_calc.to(dtype=dtype),
        source_mean.to(dtype=dtype),
        target_mean.to(dtype=dtype),
    )
    diagnostics = AffineFitDiagnostics(
        examples=int(source.shape[0]),
        source_dim=int(source.shape[1]),
        target_dim=int(target.shape[1]),
        centered_rank=rank,
        maximum_rank=min(int(source.shape[0] - 1), int(source.shape[1])),
        condition_number=condition,
        largest_singular_value=float(singular_values[0].detach().cpu()),
        smallest_retained_singular_value=smallest,
        ridge=float(ridge),
        calculation_dtype=str(calculation_dtype).removeprefix("torch."),
    )
    return transport, diagnostics


def _r2(prediction: torch.Tensor, target: torch.Tensor, eps: float = 1e-12) -> float | None:
    prediction, target = _validate_pair(
        prediction,
        target,
        source_name="prediction",
        target_name="target",
    )
    residual = (prediction - target).square().sum()
    total = (target - target.mean(dim=0, keepdim=True)).square().sum()
    if float(total) <= eps:
        return None
    return float((1.0 - residual / total).detach().cpu())


def _representation_metrics(
    prediction: torch.Tensor,
    target: torch.Tensor,
    *,
    labels: torch.Tensor | None = None,
) -> dict[str, Any]:
    prediction_flat, target_flat = _validate_pair(
        prediction,
        target,
        source_name="prediction",
        target_name="target",
    )
    difference = prediction_flat - target_flat
    centered = target_flat - target_flat.mean(dim=0, keepdim=True)
    target_scale = centered.square().mean().sqrt()
    normalized_rmse = difference.square().mean().sqrt() / target_scale.clamp_min(1e-12)
    cosine = F.cosine_similarity(prediction_flat, target_flat, dim=1)
    metrics: dict[str, Any] = {
        "r2": _r2(prediction_flat, target_flat),
        "mse": float(difference.square().mean().detach().cpu()),
        "normalized_rmse": float(normalized_rmse.detach().cpu()),
        "cosine_mean": float(cosine.mean().detach().cpu()),
    }
    if labels is not None:
        metrics.update(conditional_residual_metrics(prediction_flat, target_flat, labels))
    return metrics


@dataclass(frozen=True)
class AttributeHoldout:
    """One semantic attribute and the values excluded from transport fitting."""

    column: int
    values: tuple[int | float, ...]

    def __post_init__(self) -> None:
        if self.column < 0:
            raise ValueError("holdout attribute column must be nonnegative")
        if not self.values:
            raise ValueError("holdout attribute values must be nonempty")


@dataclass(frozen=True)
class AttributeTupleHoldout:
    """Cartesian attribute combinations excluded from fitting as whole keys."""

    columns: tuple[int, ...]
    values: tuple[tuple[int | float, ...], ...]

    def __post_init__(self) -> None:
        if not self.columns or min(self.columns) < 0:
            raise ValueError("tuple-holdout columns must be nonempty and nonnegative")
        if len(set(self.columns)) != len(self.columns):
            raise ValueError("tuple-holdout columns must be unique")
        if not self.values:
            raise ValueError("tuple-holdout values must be nonempty")
        if any(len(row) != len(self.columns) for row in self.values):
            raise ValueError("every tuple-holdout value must match the column width")


@dataclass(frozen=True)
class HoldoutSpec:
    """Frozen factor holdout used to construct fit/evaluation rows.

    A fit row is rejected if it contains *any* held-out attribute value or a
    held-out context.  An evaluation row must satisfy *all* attribute clauses
    and, when contexts are specified, belong to one of those contexts.  This
    makes leakage impossible while allowing unused boundary rows.
    """

    attributes: tuple[AttributeHoldout, ...] = ()
    attribute_tuples: tuple[AttributeTupleHoldout, ...] = ()
    context_ids: tuple[Hashable, ...] = ()


@dataclass(frozen=True)
class HoldoutPartition:
    fit_mask: torch.Tensor
    evaluation_mask: torch.Tensor
    excluded_mask: torch.Tensor
    spec: HoldoutSpec

    @property
    def fit_examples(self) -> int:
        return int(self.fit_mask.sum().item())

    @property
    def evaluation_examples(self) -> int:
        return int(self.evaluation_mask.sum().item())

    @property
    def excluded_examples(self) -> int:
        return int(self.excluded_mask.sum().item())

    def to_serializable(self) -> dict[str, Any]:
        return {
            "fit_examples": self.fit_examples,
            "evaluation_examples": self.evaluation_examples,
            "excluded_examples": self.excluded_examples,
            "heldout_attributes": [
                {"column": item.column, "values": list(item.values)}
                for item in self.spec.attributes
            ],
            "heldout_attribute_tuples": [
                {
                    "columns": list(item.columns),
                    "values": [list(row) for row in item.values],
                }
                for item in self.spec.attribute_tuples
            ],
            "heldout_context_ids": [str(item) for item in self.spec.context_ids],
        }


def _context_membership(
    context_ids: Sequence[Hashable],
    heldout: set[Hashable],
    *,
    device: torch.device,
) -> torch.Tensor:
    return torch.tensor(
        [context in heldout for context in context_ids],
        dtype=torch.bool,
        device=device,
    )


def build_holdout_partition(
    attributes: torch.Tensor,
    context_ids: Sequence[Hashable],
    *,
    attribute_holdouts: Sequence[AttributeHoldout] = (),
    attribute_tuple_holdouts: Sequence[AttributeTupleHoldout] = (),
    heldout_context_ids: Sequence[Hashable] = (),
) -> HoldoutPartition:
    """Build a leakage-safe factor/context split over paired observations."""

    attribute_matrix = _as_label_matrix(attributes, name="attributes")
    count, width = attribute_matrix.shape
    if len(context_ids) != count:
        raise ValueError("context_ids must contain one identifier per example")
    spec = HoldoutSpec(
        attributes=tuple(attribute_holdouts),
        attribute_tuples=tuple(attribute_tuple_holdouts),
        context_ids=tuple(heldout_context_ids),
    )
    if not spec.attributes and not spec.attribute_tuples and not spec.context_ids:
        raise ValueError("at least one attribute or context holdout is required")

    any_attribute = torch.zeros(count, dtype=torch.bool, device=attributes.device)
    all_attributes = torch.ones(count, dtype=torch.bool, device=attributes.device)
    for holdout in spec.attributes:
        if holdout.column >= width:
            raise ValueError(
                f"holdout attribute column {holdout.column} is outside width {width}"
            )
        values = torch.as_tensor(
            holdout.values,
            device=attributes.device,
            dtype=attributes.dtype,
        )
        matches = (attribute_matrix[:, holdout.column, None] == values[None, :]).any(dim=1)
        any_attribute |= matches
        all_attributes &= matches

    for holdout in spec.attribute_tuples:
        if max(holdout.columns) >= width:
            raise ValueError("tuple-holdout column is outside the attribute width")
        candidates = torch.as_tensor(
            holdout.values,
            device=attributes.device,
            dtype=attributes.dtype,
        )
        selected = attribute_matrix[:, list(holdout.columns)]
        matches = (selected[:, None, :] == candidates[None, :, :]).all(dim=2).any(dim=1)
        any_attribute |= matches
        all_attributes &= matches

    if spec.context_ids:
        heldout_set = set(spec.context_ids)
        if len(heldout_set) != len(spec.context_ids):
            raise ValueError("heldout_context_ids contains duplicates")
        context_holdout = _context_membership(
            context_ids,
            heldout_set,
            device=attributes.device,
        )
    else:
        context_holdout = torch.zeros(count, dtype=torch.bool, device=attributes.device)

    fit_mask = ~(any_attribute | context_holdout)
    evaluation_mask = (
        all_attributes
        if spec.attributes or spec.attribute_tuples
        else torch.ones_like(fit_mask)
    )
    if spec.context_ids:
        evaluation_mask &= context_holdout
    excluded_mask = ~(fit_mask | evaluation_mask)

    if bool((fit_mask & evaluation_mask).any()):
        raise AssertionError("internal error: fit/evaluation partition overlap")
    if int(fit_mask.sum()) == 0:
        raise ValueError("holdout leaves no fitting examples")
    if int(evaluation_mask.sum()) == 0:
        raise ValueError("holdout leaves no evaluation examples")
    return HoldoutPartition(fit_mask, evaluation_mask, excluded_mask, spec)


@dataclass(frozen=True)
class PairedRepresentations:
    """Paired cross-model states, semantics, contexts, and optional operators."""

    source_states: torch.Tensor
    target_states: torch.Tensor
    attributes: torch.Tensor
    context_ids: tuple[Hashable, ...]
    source_operators: torch.Tensor | None = None
    target_operators: torch.Tensor | None = None
    operator_keys: torch.Tensor | None = None

    def __post_init__(self) -> None:
        source, target = _validate_pair(
            self.source_states,
            self.target_states,
            source_name="source_states",
            target_name="target_states",
        )
        labels = _as_label_matrix(self.attributes, name="attributes")
        count = source.shape[0]
        if target.shape[0] != count or labels.shape[0] != count:
            raise ValueError("state, target, and attribute example counts must agree")
        if len(self.context_ids) != count:
            raise ValueError("context_ids must contain one identifier per example")
        if (self.source_operators is None) != (self.target_operators is None):
            raise ValueError("source_operators and target_operators must be supplied together")
        if self.source_operators is not None:
            if self.source_operators.ndim < 3 or self.target_operators is None:
                raise ValueError("operators must have shape (examples, slots, ...)")
            if self.source_operators.shape[:2] != self.target_operators.shape[:2]:
                raise ValueError("source/target operator example and slot counts differ")
            if self.source_operators.shape[0] != count:
                raise ValueError("operator and state example counts differ")
            _as_feature_matrix(
                self.source_operators.flatten(0, 1),
                name="source_operators",
            )
            _as_feature_matrix(
                self.target_operators.flatten(0, 1),
                name="target_operators",
            )
        if self.operator_keys is not None:
            if self.source_operators is None:
                raise ValueError("operator_keys requires operator tensors")
            if self.operator_keys.ndim not in (2, 3):
                raise ValueError("operator_keys must have shape (examples, slots[, fields])")
            if self.operator_keys.shape[:2] != self.source_operators.shape[:2]:
                raise ValueError("operator_keys must align with operator examples and slots")

    @property
    def examples(self) -> int:
        return int(self.source_states.shape[0])

    def labels(self, columns: Sequence[int]) -> torch.Tensor:
        attributes = _as_label_matrix(self.attributes, name="attributes")
        if not columns:
            raise ValueError("at least one codebook label column is required")
        if min(columns) < 0 or max(columns) >= attributes.shape[1]:
            raise ValueError("codebook label column is out of range")
        return attributes[:, list(columns)]

    def subset(self, mask: torch.Tensor) -> "PairedRepresentations":
        mask = torch.as_tensor(mask, device=self.source_states.device, dtype=torch.bool)
        if mask.ndim != 1 or mask.shape[0] != self.examples:
            raise ValueError("subset mask must have one entry per example")
        indices = torch.nonzero(mask, as_tuple=False).flatten()
        def index_for(value: torch.Tensor | None) -> torch.Tensor | None:
            if value is None:
                return None
            return value.index_select(0, indices.to(value.device))

        return PairedRepresentations(
            source_states=self.source_states.index_select(0, indices),
            target_states=self.target_states.index_select(0, indices),
            attributes=self.attributes.index_select(0, indices.to(self.attributes.device)),
            context_ids=tuple(self.context_ids[int(index)] for index in indices.cpu().tolist()),
            source_operators=index_for(self.source_operators),
            target_operators=index_for(self.target_operators),
            operator_keys=index_for(self.operator_keys),
        )


def concatenate_paired_representations(
    *datasets: PairedRepresentations,
) -> PairedRepresentations:
    """Concatenate compatible collections without dropping audit metadata."""

    if not datasets:
        raise ValueError("at least one paired representation dataset is required")
    first = datasets[0]
    for dataset in datasets[1:]:
        if dataset.source_states.shape[1:] != first.source_states.shape[1:]:
            raise ValueError("source state shapes differ across datasets")
        if dataset.target_states.shape[1:] != first.target_states.shape[1:]:
            raise ValueError("target state shapes differ across datasets")
        if dataset.attributes.shape[1:] != first.attributes.shape[1:]:
            raise ValueError("attribute shapes differ across datasets")
        for name in ("source_operators", "target_operators", "operator_keys"):
            left = getattr(first, name)
            right = getattr(dataset, name)
            if (left is None) != (right is None):
                raise ValueError(f"{name} availability differs across datasets")
            if left is not None and right is not None and left.shape[1:] != right.shape[1:]:
                raise ValueError(f"{name} shapes differ across datasets")

    def concatenate_optional(name: str) -> torch.Tensor | None:
        values = [getattr(dataset, name) for dataset in datasets]
        if values[0] is None:
            return None
        return torch.cat(values, dim=0)  # type: ignore[arg-type]

    return PairedRepresentations(
        source_states=torch.cat([dataset.source_states for dataset in datasets], dim=0),
        target_states=torch.cat([dataset.target_states for dataset in datasets], dim=0),
        attributes=torch.cat([dataset.attributes for dataset in datasets], dim=0),
        context_ids=tuple(
            context
            for dataset in datasets
            for context in dataset.context_ids
        ),
        source_operators=concatenate_optional("source_operators"),
        target_operators=concatenate_optional("target_operators"),
        operator_keys=concatenate_optional("operator_keys"),
    )


@dataclass(frozen=True)
class TensorAffineTransport:
    """Affine transport for arbitrary per-example tensors, including operators."""

    affine: AffineTransport
    source_shape: tuple[int, ...]
    target_shape: tuple[int, ...]
    diagnostics: AffineFitDiagnostics | None = None

    def apply(self, values: torch.Tensor) -> torch.Tensor:
        trailing = len(self.source_shape)
        if trailing == 0 or values.ndim < trailing:
            raise ValueError("values have fewer dimensions than the transport source shape")
        if tuple(values.shape[-trailing:]) != self.source_shape:
            raise ValueError(
                f"expected trailing shape {self.source_shape}, got {tuple(values.shape[-trailing:])}"
            )
        leading = tuple(values.shape[:-trailing])
        flat = values.reshape(-1, self.affine.weight.shape[0])
        mapped = self.affine.apply(flat)
        return mapped.reshape(*leading, *self.target_shape)

    def to_serializable(self) -> dict[str, Any]:
        return {
            "source_shape": list(self.source_shape),
            "target_shape": list(self.target_shape),
            "affine": self.affine.to_serializable(),
            "fit_diagnostics": (
                None if self.diagnostics is None else self.diagnostics.to_serializable()
            ),
        }


def fit_tensor_transport(
    source: torch.Tensor,
    target: torch.Tensor,
    *,
    ridge: float = 1e-5,
) -> TensorAffineTransport:
    source_flat, target_flat = _validate_pair(
        source,
        target,
        source_name="source",
        target_name="target",
    )
    affine, diagnostics = fit_stable_affine_transport(source_flat, target_flat, ridge=ridge)
    return TensorAffineTransport(
        affine,
        tuple(source.shape[1:]),
        tuple(target.shape[1:]),
        diagnostics,
    )


@dataclass(frozen=True)
class ShuffledFit:
    transport: AffineTransport
    permutation: torch.Tensor
    movable_fraction: float
    diagnostics: AffineFitDiagnostics

    def apply(self, values: torch.Tensor) -> torch.Tensor:
        return self.transport.apply(values)


@dataclass(frozen=True)
class TensorShuffledFit:
    transport: TensorAffineTransport
    permutation: torch.Tensor
    movable_fraction: float

    def apply(self, values: torch.Tensor) -> torch.Tensor:
        return self.transport.apply(values)


def _group_ids(labels: torch.Tensor) -> torch.Tensor:
    labels = _as_label_matrix(labels)
    return torch.unique(labels, dim=0, sorted=True, return_inverse=True)[1]


def _within_group_permutation(groups: torch.Tensor, seed: int) -> tuple[torch.Tensor, float]:
    if groups.ndim != 1 or groups.shape[0] < 2:
        raise ValueError("groups must be a vector containing at least two examples")
    device = groups.device
    generator = torch.Generator(device=device).manual_seed(int(seed))
    order = torch.arange(groups.shape[0], device=device)
    movable = torch.zeros_like(order, dtype=torch.bool)
    for group in torch.unique(groups, sorted=True):
        members = torch.nonzero(groups == group, as_tuple=False).flatten()
        if members.numel() < 2:
            continue
        # A non-zero cyclic roll is a guaranteed within-group derangement.
        shift = int(
            torch.randint(
                1,
                int(members.numel()),
                (1,),
                generator=generator,
                device=device,
            ).item()
        )
        order[members] = members.roll(shift)
        movable[members] = True
    movable_fraction = float(movable.float().mean().cpu())
    if movable_fraction == 0.0:
        raise ValueError("no codebook group has enough examples for a within-group shuffle")
    return order, movable_fraction


def fit_within_codebook_shuffled_transport(
    source: torch.Tensor,
    target: torch.Tensor,
    labels: torch.Tensor,
    *,
    seed: int,
    ridge: float = 1e-5,
) -> ShuffledFit:
    """Destroy paired residuals while preserving the discrete label codebook."""

    source_flat, target_flat = _validate_pair(
        source,
        target,
        source_name="source",
        target_name="target",
    )
    labels = _as_label_matrix(labels)
    if labels.shape[0] != source_flat.shape[0]:
        raise ValueError("labels must align with transport pairs")
    permutation, fraction = _within_group_permutation(_group_ids(labels), seed)
    fitted, diagnostics = fit_stable_affine_transport(
        source_flat,
        target_flat[permutation],
        ridge=ridge,
    )
    return ShuffledFit(fitted, permutation, fraction, diagnostics)


def fit_shuffled_tensor_transport(
    source: torch.Tensor,
    target: torch.Tensor,
    *,
    seed: int,
    groups: torch.Tensor | None = None,
    ridge: float = 1e-5,
) -> TensorShuffledFit:
    """Fit a tensor map after removing operator-pair correspondence."""

    source_flat, target_flat = _validate_pair(
        source,
        target,
        source_name="source",
        target_name="target",
    )
    if groups is None:
        groups = torch.zeros(source.shape[0], device=source.device, dtype=torch.long)
    else:
        groups = torch.as_tensor(groups, device=source.device)
        if groups.ndim != 1 or groups.shape[0] != source.shape[0]:
            raise ValueError("groups must have one entry per tensor pair")
    permutation, fraction = _within_group_permutation(groups, seed)
    affine, diagnostics = fit_stable_affine_transport(
        source_flat,
        target_flat[permutation],
        ridge=ridge,
    )
    transport = TensorAffineTransport(
        affine,
        tuple(source.shape[1:]),
        tuple(target.shape[1:]),
        diagnostics,
    )
    return TensorShuffledFit(transport, permutation, fraction)


def random_matched_tensor_transport(
    reference: TensorAffineTransport,
    *,
    seed: int,
) -> TensorAffineTransport:
    return TensorAffineTransport(
        random_matched_transport(reference.affine, seed),
        reference.source_shape,
        reference.target_shape,
        None,
    )


@dataclass(frozen=True)
class CentroidBaseline:
    """Empirical target prototype for each discrete codebook key."""

    keys: torch.Tensor
    centroids: torch.Tensor
    fallback: torch.Tensor

    def _lookup(self, labels: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        labels = _as_label_matrix(labels)
        keys = self.keys.to(device=labels.device, dtype=labels.dtype)
        matches = (labels[:, None, :] == keys[None, :, :]).all(dim=2)
        covered = matches.any(dim=1)
        indices = matches.to(dtype=torch.long).argmax(dim=1)
        return indices, covered

    def apply(self, labels: torch.Tensor) -> torch.Tensor:
        indices, covered = self._lookup(labels)
        centroids = self.centroids.to(labels.device)[indices]
        fallback = self.fallback.to(labels.device).expand(labels.shape[0], -1)
        return torch.where(covered[:, None], centroids, fallback)

    def coverage(self, labels: torch.Tensor) -> float:
        return float(self._lookup(labels)[1].float().mean().cpu())


def fit_centroid_baseline(target: torch.Tensor, labels: torch.Tensor) -> CentroidBaseline:
    target_flat = _as_feature_matrix(target, name="target")
    labels = _as_label_matrix(labels)
    if labels.shape[0] != target_flat.shape[0]:
        raise ValueError("labels must align with target examples")
    keys, inverse = torch.unique(labels, dim=0, sorted=True, return_inverse=True)
    centroids = torch.empty(
        keys.shape[0],
        target_flat.shape[1],
        device=target_flat.device,
        dtype=target_flat.dtype,
    )
    for index in range(keys.shape[0]):
        centroids[index] = target_flat[inverse == index].mean(dim=0)
    return CentroidBaseline(keys.detach(), centroids.detach(), target_flat.mean(dim=0).detach())


def source_decode_target_reembed(
    source_hidden: torch.Tensor,
    source_decode: Callable[[torch.Tensor], torch.Tensor],
    target_reembed: Callable[[torch.Tensor], torch.Tensor],
) -> torch.Tensor:
    """Apply the explicit source-decode -> target-reembed codebook ceiling."""

    decoded = source_decode(source_hidden)
    if not torch.is_tensor(decoded) or decoded.shape[0] != source_hidden.shape[0]:
        raise ValueError("source_decode must return one semantic value per example")
    reembedded = target_reembed(decoded)
    if not torch.is_tensor(reembedded) or reembedded.shape[0] != source_hidden.shape[0]:
        raise ValueError("target_reembed must return one hidden state per example")
    _as_feature_matrix(reembedded, name="reembedded hidden")
    return reembedded


def conditional_residual_metrics(
    prediction: torch.Tensor,
    target: torch.Tensor,
    labels: torch.Tensor,
    *,
    eps: float = 1e-12,
) -> dict[str, Any]:
    """Score within-label structure after removing each label's centroid.

    A label-only prototype has exactly zero centered prediction and therefore
    conditional residual R² of zero (when target residual variance exists).
    A genuine transport can score above zero by matching contextual/payload
    variation among examples with the same label.
    """

    prediction, target = _validate_pair(
        prediction,
        target,
        source_name="prediction",
        target_name="target",
    )
    labels = _as_label_matrix(labels)
    if labels.shape[0] != target.shape[0]:
        raise ValueError("labels must align with predictions and targets")
    groups = _group_ids(labels)
    prediction_centered = torch.zeros_like(prediction)
    target_centered = torch.zeros_like(target)
    valid = torch.zeros(target.shape[0], dtype=torch.bool, device=target.device)
    valid_groups = 0
    for group in torch.unique(groups, sorted=True):
        members = groups == group
        if int(members.sum()) < 2:
            continue
        prediction_centered[members] = prediction[members] - prediction[members].mean(
            dim=0, keepdim=True
        )
        target_centered[members] = target[members] - target[members].mean(dim=0, keepdim=True)
        valid[members] = True
        valid_groups += 1
    if not bool(valid.any()):
        return {
            "conditional_residual_available": False,
            "conditional_residual_r2": None,
            "conditional_residual_mse": None,
            "conditional_residual_examples": 0,
            "conditional_residual_groups": 0,
            "conditional_target_variance": None,
        }
    difference = prediction_centered[valid] - target_centered[valid]
    total = target_centered[valid].square().sum()
    residual_r2 = None if float(total) <= eps else float((1.0 - difference.square().sum() / total).cpu())
    return {
        "conditional_residual_available": residual_r2 is not None,
        "conditional_residual_r2": residual_r2,
        "conditional_residual_mse": float(difference.square().mean().cpu()),
        "conditional_residual_examples": int(valid.sum()),
        "conditional_residual_groups": valid_groups,
        "conditional_target_variance": float(target_centered[valid].square().mean().cpu()),
    }


@dataclass(frozen=True)
class AssayMetadata:
    source_id: str
    target_id: str
    anchor_seed: int
    evaluation_seed: int
    anchor_partition: str
    evaluation_partition: str

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id:
            raise ValueError("source_id and target_id must be nonempty")
        if self.source_id == self.target_id:
            raise ValueError("source_id and target_id must identify distinct model fits")
        if self.anchor_seed == self.evaluation_seed:
            raise ValueError("anchor and evaluation seeds must be distinct")
        if self.anchor_partition == self.evaluation_partition:
            raise ValueError("anchor and evaluation partitions must be distinct")

    def to_serializable(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "anchor_seed": self.anchor_seed,
            "evaluation_seed": self.evaluation_seed,
            "anchor_partition": self.anchor_partition,
            "evaluation_partition": self.evaluation_partition,
        }


@dataclass(frozen=True)
class StateInducedOperatorTransport:
    """Conjugate square matrix codes using the fitted state-coordinate map."""

    state_transport: AffineTransport
    inverse: torch.Tensor

    @classmethod
    def from_state_transport(
        cls,
        state_transport: AffineTransport,
        *,
        max_condition: float = 1e8,
    ) -> "StateInducedOperatorTransport":
        source_dim, target_dim = state_transport.weight.shape
        if source_dim != target_dim:
            raise ValueError("state-induced operator transport requires equal state dimensions")
        transform = state_transport.weight.T
        condition = float(torch.linalg.cond(transform).detach().cpu())
        if not torch.isfinite(torch.tensor(condition)) or condition > max_condition:
            raise ValueError("state transport is too ill-conditioned for operator conjugation")
        return cls(state_transport, torch.linalg.inv(transform))

    def apply(self, operators: torch.Tensor) -> torch.Tensor:
        dimension = self.state_transport.weight.shape[0]
        if operators.ndim < 2 or tuple(operators.shape[-2:]) != (dimension, dimension):
            raise ValueError(f"operators must have trailing shape ({dimension}, {dimension})")
        transform = self.state_transport.weight.T
        return torch.matmul(torch.matmul(transform, operators), self.inverse)


@dataclass(frozen=True)
class FittedTransportAssay:
    metadata: AssayMetadata
    holdout: HoldoutPartition
    codebook_columns: tuple[int, ...]
    state_forward: AffineTransport
    state_reverse: AffineTransport
    state_forward_diagnostics: AffineFitDiagnostics
    state_reverse_diagnostics: AffineFitDiagnostics
    state_forward_shuffled: ShuffledFit
    state_reverse_shuffled: ShuffledFit
    state_forward_random: AffineTransport
    state_reverse_random: AffineTransport
    target_centroids: CentroidBaseline
    source_centroids: CentroidBaseline
    fit_context_ids: frozenset[Hashable]
    ridge: float
    shuffle_seed: int
    operator_forward: TensorAffineTransport | None = None
    operator_reverse: TensorAffineTransport | None = None
    operator_forward_shuffled: TensorShuffledFit | None = None
    operator_reverse_shuffled: TensorShuffledFit | None = None
    operator_forward_random: TensorAffineTransport | None = None
    operator_reverse_random: TensorAffineTransport | None = None
    induced_operator_forward: StateInducedOperatorTransport | None = None
    induced_operator_reverse: StateInducedOperatorTransport | None = None

    def _validate_evaluation_rows(self, data: PairedRepresentations) -> None:
        contexts = set(data.context_ids)
        if self.holdout.spec.context_ids:
            overlap = contexts & set(self.fit_context_ids)
            if overlap:
                preview = ", ".join(str(item) for item in sorted(overlap, key=str)[:3])
                raise ValueError(f"evaluation contexts leaked into transport fit: {preview}")
        attributes = _as_label_matrix(data.attributes, name="attributes")
        for holdout in self.holdout.spec.attributes:
            values = torch.as_tensor(
                holdout.values,
                device=attributes.device,
                dtype=attributes.dtype,
            )
            matches = (attributes[:, holdout.column, None] == values[None, :]).any(dim=1)
            if not bool(matches.all()):
                raise ValueError(
                    f"evaluation includes rows outside held-out attribute {holdout.column}"
                )
        for holdout in self.holdout.spec.attribute_tuples:
            candidates = torch.as_tensor(
                holdout.values,
                device=attributes.device,
                dtype=attributes.dtype,
            )
            selected = attributes[:, list(holdout.columns)]
            matches = (selected[:, None, :] == candidates[None, :, :]).all(dim=2).any(dim=1)
            if not bool(matches.all()):
                raise ValueError("evaluation includes rows outside held-out attribute tuples")
        if self.holdout.spec.context_ids:
            allowed = set(self.holdout.spec.context_ids)
            if not contexts <= allowed:
                raise ValueError("evaluation includes a context outside the held-out context set")

    def evaluate_latents(
        self,
        evaluation: PairedRepresentations,
        *,
        source_decode: Callable[[torch.Tensor], torch.Tensor] | None = None,
        target_reembed: Callable[[torch.Tensor], torch.Tensor] | None = None,
        target_decode: Callable[[torch.Tensor], torch.Tensor] | None = None,
        source_reembed: Callable[[torch.Tensor], torch.Tensor] | None = None,
    ) -> dict[str, Any]:
        """Evaluate frozen maps on isolated contexts/attributes."""

        self._validate_evaluation_rows(evaluation)
        labels = evaluation.labels(self.codebook_columns)
        forward = self.state_forward.apply(evaluation.source_states)
        reverse = self.state_reverse.apply(evaluation.target_states)
        forward_shuffled = self.state_forward_shuffled.apply(evaluation.source_states)
        reverse_shuffled = self.state_reverse_shuffled.apply(evaluation.target_states)
        forward_random = self.state_forward_random.apply(evaluation.source_states)
        reverse_random = self.state_reverse_random.apply(evaluation.target_states)
        target_centroid = self.target_centroids.apply(labels)
        source_centroid = self.source_centroids.apply(labels)

        state: dict[str, Any] = {
            "forward": _representation_metrics(forward, evaluation.target_states, labels=labels),
            "reverse": _representation_metrics(reverse, evaluation.source_states, labels=labels),
            "forward_within_codebook_shuffle": _representation_metrics(
                forward_shuffled, evaluation.target_states, labels=labels
            ),
            "reverse_within_codebook_shuffle": _representation_metrics(
                reverse_shuffled, evaluation.source_states, labels=labels
            ),
            "forward_random_map": _representation_metrics(
                forward_random, evaluation.target_states, labels=labels
            ),
            "reverse_random_map": _representation_metrics(
                reverse_random, evaluation.source_states, labels=labels
            ),
            "target_centroid_baseline": {
                **_representation_metrics(target_centroid, evaluation.target_states, labels=labels),
                "coverage": self.target_centroids.coverage(labels),
            },
            "source_centroid_baseline": {
                **_representation_metrics(source_centroid, evaluation.source_states, labels=labels),
                "coverage": self.source_centroids.coverage(labels),
            },
            "forward_decode_reembed_baseline": {
                "available": False,
                "reason": "source_decode and target_reembed callbacks were not supplied",
            },
            "reverse_decode_reembed_baseline": {
                "available": False,
                "reason": "target_decode and source_reembed callbacks were not supplied",
            },
            "cycle": cycle_consistency_metrics(
                self.state_forward,
                self.state_reverse,
                evaluation.source_states,
                evaluation.target_states,
                source_decode=source_decode,
                target_decode=target_decode,
                expected_attributes=evaluation.attributes,
            ),
        }
        state["forward_within_codebook_shuffle"]["movable_fraction"] = (
            self.state_forward_shuffled.movable_fraction
        )
        state["reverse_within_codebook_shuffle"]["movable_fraction"] = (
            self.state_reverse_shuffled.movable_fraction
        )
        if evaluation.source_states.shape[1:] == evaluation.target_states.shape[1:]:
            state["forward_identity_map"] = {
                "available": True,
                **_representation_metrics(
                    evaluation.source_states,
                    evaluation.target_states,
                    labels=labels,
                ),
            }
            state["reverse_identity_map"] = {
                "available": True,
                **_representation_metrics(
                    evaluation.target_states,
                    evaluation.source_states,
                    labels=labels,
                ),
            }
        else:
            state["forward_identity_map"] = {
                "available": False,
                "reason": "source and target state shapes differ",
            }
            state["reverse_identity_map"] = dict(state["forward_identity_map"])

        if target_reembed is not None and source_decode is None:
            raise ValueError("target_reembed requires source_decode")
        if source_decode is not None and target_reembed is not None:
            decoded_forward = source_decode_target_reembed(
                evaluation.source_states,
                source_decode,
                target_reembed,
            )
            state["forward_decode_reembed_baseline"] = _representation_metrics(
                decoded_forward,
                evaluation.target_states,
                labels=labels,
            )
            state["forward_decode_reembed_baseline"]["available"] = True
        if source_reembed is not None and target_decode is None:
            raise ValueError("source_reembed requires target_decode")
        if target_decode is not None and source_reembed is not None:
            decoded_reverse = source_decode_target_reembed(
                evaluation.target_states,
                target_decode,
                source_reembed,
            )
            state["reverse_decode_reembed_baseline"] = _representation_metrics(
                decoded_reverse,
                evaluation.source_states,
                labels=labels,
            )
            state["reverse_decode_reembed_baseline"]["available"] = True

        state["forward_codebook_contrast"] = {
            "conditional_residual_r2_minus_centroid": _subtract_optional(
                state["forward"]["conditional_residual_r2"],
                state["target_centroid_baseline"]["conditional_residual_r2"],
            ),
            "conditional_residual_r2_minus_within_codebook_shuffle": _subtract_optional(
                state["forward"]["conditional_residual_r2"],
                state["forward_within_codebook_shuffle"]["conditional_residual_r2"],
            ),
        }
        if state["forward_decode_reembed_baseline"]["available"]:
            state["forward_codebook_contrast"]["conditional_residual_r2_minus_decode_reembed"] = (
                _subtract_optional(
                    state["forward"]["conditional_residual_r2"],
                    state["forward_decode_reembed_baseline"]["conditional_residual_r2"],
                )
            )

        operator: dict[str, Any] = {"available": False}
        if self.operator_forward is not None and self.operator_reverse is not None:
            if evaluation.source_operators is None or evaluation.target_operators is None:
                raise ValueError("fitted assay expects evaluation operator codes")
            source_operators = evaluation.source_operators.flatten(0, 1)
            target_operators = evaluation.target_operators.flatten(0, 1)
            predicted_target = self.operator_forward.apply(source_operators)
            predicted_source = self.operator_reverse.apply(target_operators)
            operator = {
                "available": True,
                "state_induced_available": bool(
                    self.induced_operator_forward is not None
                    and self.induced_operator_reverse is not None
                ),
                "forward": _representation_metrics(predicted_target, target_operators),
                "reverse": _representation_metrics(predicted_source, source_operators),
                "cycle": cycle_consistency_metrics(
                    self.operator_forward,
                    self.operator_reverse,
                    source_operators,
                    target_operators,
                ),
            }
            if (
                self.operator_forward_shuffled is not None
                and self.operator_reverse_shuffled is not None
            ):
                operator["forward_shuffled_control"] = {
                    **_representation_metrics(
                        self.operator_forward_shuffled.apply(source_operators),
                        target_operators,
                    ),
                    "movable_fraction": self.operator_forward_shuffled.movable_fraction,
                }
                operator["reverse_shuffled_control"] = {
                    **_representation_metrics(
                        self.operator_reverse_shuffled.apply(target_operators),
                        source_operators,
                    ),
                    "movable_fraction": self.operator_reverse_shuffled.movable_fraction,
                }
            if self.operator_forward_random is not None and self.operator_reverse_random is not None:
                operator["forward_random_map"] = _representation_metrics(
                    self.operator_forward_random.apply(source_operators),
                    target_operators,
                )
                operator["reverse_random_map"] = _representation_metrics(
                    self.operator_reverse_random.apply(target_operators),
                    source_operators,
                )
            if source_operators.shape[1:] == target_operators.shape[1:]:
                operator["forward_identity_map"] = {
                    "available": True,
                    **_representation_metrics(source_operators, target_operators),
                }
                operator["reverse_identity_map"] = {
                    "available": True,
                    **_representation_metrics(target_operators, source_operators),
                }
            else:
                operator["forward_identity_map"] = {
                    "available": False,
                    "reason": "source and target operator shapes differ",
                }
                operator["reverse_identity_map"] = dict(operator["forward_identity_map"])
            if self.induced_operator_forward is not None:
                operator["state_induced_forward"] = _representation_metrics(
                    self.induced_operator_forward.apply(source_operators),
                    target_operators,
                )
            if self.induced_operator_reverse is not None:
                operator["state_induced_reverse"] = _representation_metrics(
                    self.induced_operator_reverse.apply(target_operators),
                    source_operators,
                )

        return {
            "schema": TRANSPORT_ASSAY_SCHEMA,
            "metadata": self.metadata.to_serializable(),
            "holdout": self.holdout.to_serializable(),
            "fit_config": {
                "ridge": self.ridge,
                "shuffle_seed": self.shuffle_seed,
                "calculation_dtype": "float64",
            },
            "fit_diagnostics": {
                "state_forward": self.state_forward_diagnostics.to_serializable(),
                "state_reverse": self.state_reverse_diagnostics.to_serializable(),
                "state_forward_within_codebook_shuffle": (
                    self.state_forward_shuffled.diagnostics.to_serializable()
                ),
                "state_reverse_within_codebook_shuffle": (
                    self.state_reverse_shuffled.diagnostics.to_serializable()
                ),
                "operator_forward": (
                    None
                    if self.operator_forward is None or self.operator_forward.diagnostics is None
                    else self.operator_forward.diagnostics.to_serializable()
                ),
                "operator_reverse": (
                    None
                    if self.operator_reverse is None or self.operator_reverse.diagnostics is None
                    else self.operator_reverse.diagnostics.to_serializable()
                ),
            },
            "evaluation_examples": evaluation.examples,
            "evaluation_contexts": len(set(evaluation.context_ids)),
            "fit_context_ids": sorted((str(item) for item in self.fit_context_ids)),
            "evaluation_context_ids": sorted(
                {str(item) for item in evaluation.context_ids}
            ),
            "codebook_columns": list(self.codebook_columns),
            "state": state,
            "operator": operator,
        }


def _subtract_optional(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return float(left - right)


def fit_transport_assay(
    data: PairedRepresentations,
    partition: HoldoutPartition,
    *,
    metadata: AssayMetadata,
    codebook_columns: Sequence[int],
    ridge: float = 1e-5,
    shuffle_seed: int = 0,
) -> FittedTransportAssay:
    """Fit all v0.3 maps exclusively on the holdout partition's fit rows."""

    if partition.fit_mask.shape != (data.examples,):
        raise ValueError("holdout partition does not align with paired data")
    fit = data.subset(partition.fit_mask)
    columns = tuple(int(column) for column in codebook_columns)
    labels = fit.labels(columns)
    state_forward, state_forward_diagnostics = fit_stable_affine_transport(
        fit.source_states,
        fit.target_states,
        ridge=ridge,
    )
    state_reverse, state_reverse_diagnostics = fit_stable_affine_transport(
        fit.target_states,
        fit.source_states,
        ridge=ridge,
    )
    forward_shuffled = fit_within_codebook_shuffled_transport(
        fit.source_states,
        fit.target_states,
        labels,
        seed=shuffle_seed,
        ridge=ridge,
    )
    reverse_shuffled = fit_within_codebook_shuffled_transport(
        fit.target_states,
        fit.source_states,
        labels,
        seed=shuffle_seed + 1,
        ridge=ridge,
    )
    operator_forward: TensorAffineTransport | None = None
    operator_reverse: TensorAffineTransport | None = None
    operator_forward_shuffled: TensorShuffledFit | None = None
    operator_reverse_shuffled: TensorShuffledFit | None = None
    operator_forward_random: TensorAffineTransport | None = None
    operator_reverse_random: TensorAffineTransport | None = None
    induced_forward: StateInducedOperatorTransport | None = None
    induced_reverse: StateInducedOperatorTransport | None = None
    if fit.source_operators is not None and fit.target_operators is not None:
        source_operators = fit.source_operators.flatten(0, 1)
        target_operators = fit.target_operators.flatten(0, 1)
        operator_forward = fit_tensor_transport(source_operators, target_operators, ridge=ridge)
        operator_reverse = fit_tensor_transport(target_operators, source_operators, ridge=ridge)
        if fit.operator_keys is None:
            operator_groups = None
        else:
            operator_groups = _group_ids(fit.operator_keys.flatten(0, 1))
        operator_forward_shuffled = fit_shuffled_tensor_transport(
            source_operators,
            target_operators,
            seed=shuffle_seed + 2,
            groups=operator_groups,
            ridge=ridge,
        )
        operator_reverse_shuffled = fit_shuffled_tensor_transport(
            target_operators,
            source_operators,
            seed=shuffle_seed + 3,
            groups=operator_groups,
            ridge=ridge,
        )
        operator_forward_random = random_matched_tensor_transport(
            operator_forward,
            seed=shuffle_seed + 4,
        )
        operator_reverse_random = random_matched_tensor_transport(
            operator_reverse,
            seed=shuffle_seed + 5,
        )
        source_shape = tuple(source_operators.shape[1:])
        target_shape = tuple(target_operators.shape[1:])
        if (
            len(source_shape) == 2
            and len(target_shape) == 2
            and source_shape[0] == source_shape[1] == state_forward.weight.shape[0]
            and target_shape[0] == target_shape[1] == state_forward.weight.shape[1]
        ):
            try:
                induced_forward = StateInducedOperatorTransport.from_state_transport(state_forward)
                induced_reverse = StateInducedOperatorTransport.from_state_transport(state_reverse)
            except ValueError:
                # Direct operator transport remains available; the receipt makes
                # structural conjugation unavailability explicit via missing keys.
                pass

    fit_contexts = frozenset(fit.context_ids)
    if partition.spec.context_ids and fit_contexts & set(partition.spec.context_ids):
        raise AssertionError("internal error: a held-out context entered transport fitting")
    return FittedTransportAssay(
        metadata=metadata,
        holdout=partition,
        codebook_columns=columns,
        state_forward=state_forward,
        state_reverse=state_reverse,
        state_forward_diagnostics=state_forward_diagnostics,
        state_reverse_diagnostics=state_reverse_diagnostics,
        state_forward_shuffled=forward_shuffled,
        state_reverse_shuffled=reverse_shuffled,
        state_forward_random=random_matched_transport(state_forward, shuffle_seed + 10),
        state_reverse_random=random_matched_transport(state_reverse, shuffle_seed + 11),
        target_centroids=fit_centroid_baseline(fit.target_states, labels),
        source_centroids=fit_centroid_baseline(fit.source_states, labels),
        fit_context_ids=fit_contexts,
        ridge=float(ridge),
        shuffle_seed=int(shuffle_seed),
        operator_forward=operator_forward,
        operator_reverse=operator_reverse,
        operator_forward_shuffled=operator_forward_shuffled,
        operator_reverse_shuffled=operator_reverse_shuffled,
        operator_forward_random=operator_forward_random,
        operator_reverse_random=operator_reverse_random,
        induced_operator_forward=induced_forward,
        induced_operator_reverse=induced_reverse,
    )


def fit_transport_assay_from_datasets(
    anchors: PairedRepresentations,
    evaluation: PairedRepresentations,
    *,
    metadata: AssayMetadata,
    codebook_columns: Sequence[int],
    heldout_attribute_columns: Sequence[int] = (),
    ridge: float = 1e-5,
    shuffle_seed: int = 0,
) -> FittedTransportAssay:
    """Convenience entry point for separate anchor/evaluation sets.

    Context identifiers must be disjoint.  Columns declared as attribute
    holdouts must also have disjoint value sets.  These checks run before any
    fit, then the function constructs the same auditable partition used by the
    lower-level API.
    """

    anchor_contexts = set(anchors.context_ids)
    evaluation_contexts = set(evaluation.context_ids)
    context_overlap = anchor_contexts & evaluation_contexts
    if context_overlap:
        preview = ", ".join(str(item) for item in sorted(context_overlap, key=str)[:3])
        raise ValueError(f"anchor/evaluation context overlap: {preview}")
    anchor_attributes = _as_label_matrix(anchors.attributes, name="anchor attributes")
    evaluation_attributes = _as_label_matrix(
        evaluation.attributes,
        name="evaluation attributes",
    )
    if anchor_attributes.shape[1] != evaluation_attributes.shape[1]:
        raise ValueError("anchor/evaluation attribute widths differ")
    attribute_holdouts: list[AttributeHoldout] = []
    for raw_column in heldout_attribute_columns:
        column = int(raw_column)
        if not 0 <= column < anchor_attributes.shape[1]:
            raise ValueError("heldout attribute column is out of range")
        anchor_values = set(anchor_attributes[:, column].detach().cpu().tolist())
        evaluation_values = set(evaluation_attributes[:, column].detach().cpu().tolist())
        overlap = anchor_values & evaluation_values
        if overlap:
            raise ValueError(
                f"held-out attribute {column} leaked into anchors: {sorted(overlap)[:3]}"
            )
        attribute_holdouts.append(
            AttributeHoldout(column, tuple(sorted(evaluation_values)))
        )

    combined = concatenate_paired_representations(anchors, evaluation)
    # Preserve first-seen ordering while removing repeated context identifiers.
    heldout_contexts = tuple(dict.fromkeys(evaluation.context_ids))
    partition = build_holdout_partition(
        combined.attributes,
        combined.context_ids,
        attribute_holdouts=attribute_holdouts,
        heldout_context_ids=heldout_contexts,
    )
    if partition.fit_examples != anchors.examples:
        raise AssertionError("constructed holdout did not select every anchor exactly once")
    if partition.evaluation_examples != evaluation.examples:
        raise AssertionError("constructed holdout did not select every evaluation row exactly once")
    return fit_transport_assay(
        combined,
        partition,
        metadata=metadata,
        codebook_columns=codebook_columns,
        ridge=ridge,
        shuffle_seed=shuffle_seed,
    )


def cycle_consistency_metrics(
    forward: AppliesTensor,
    reverse: AppliesTensor,
    source: torch.Tensor,
    target: torch.Tensor,
    *,
    source_decode: Callable[[torch.Tensor], torch.Tensor] | None = None,
    target_decode: Callable[[torch.Tensor], torch.Tensor] | None = None,
    expected_attributes: torch.Tensor | None = None,
) -> dict[str, Any]:
    """Measure both directions and A->B->A / B->A->B cycles."""

    source_to_target = forward.apply(source)
    target_to_source = reverse.apply(target)
    source_cycle = reverse.apply(source_to_target)
    target_cycle = forward.apply(target_to_source)
    output: dict[str, Any] = {
        "source_cycle": _representation_metrics(source_cycle, source),
        "target_cycle": _representation_metrics(target_cycle, target),
        "source_to_target_to_source": True,
        "target_to_source_to_target": True,
    }
    if expected_attributes is not None:
        expected = _as_label_matrix(expected_attributes, name="expected_attributes")
        if expected.shape[0] != source.shape[0]:
            raise ValueError("expected_attributes must align with cycle examples")
        if source_decode is not None:
            decoded = _as_label_matrix(source_decode(source_cycle), name="source cycle decode")
            if decoded.shape != expected.shape:
                raise ValueError("source cycle decoder output shape differs from expected attributes")
            output["source_cycle_attribute_accuracy"] = float(
                (decoded == expected).all(dim=1).float().mean().cpu()
            )
        if target_decode is not None:
            decoded = _as_label_matrix(target_decode(target_cycle), name="target cycle decode")
            if decoded.shape != expected.shape:
                raise ValueError("target cycle decoder output shape differs from expected attributes")
            output["target_cycle_attribute_accuracy"] = float(
                (decoded == expected).all(dim=1).float().mean().cpu()
            )
    return output


def _broadcast_component_mask(
    mask: torch.Tensor | Sequence[int] | Sequence[bool],
    *,
    examples: int,
    components: int,
    device: torch.device,
    name: str,
) -> torch.Tensor:
    if torch.is_tensor(mask):
        result = mask.to(device=device, dtype=torch.bool)
        if result.shape == (components,):
            return result.unsqueeze(0).expand(examples, -1)
        if result.shape == (examples, components):
            return result
        raise ValueError(f"{name} must have shape ({components},) or ({examples}, {components})")
    values = list(mask)
    if len(values) == components and all(isinstance(item, bool) for item in values):
        return torch.tensor(values, dtype=torch.bool, device=device).unsqueeze(0).expand(examples, -1)
    result = torch.zeros(examples, components, dtype=torch.bool, device=device)
    for index in values:
        if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < components:
            raise ValueError(f"{name} component index out of range")
        result[:, index] = True
    return result


def _masked_element_accuracy(
    equality: torch.Tensor,
    mask: torch.Tensor,
) -> float | None:
    selected = equality[mask]
    return float(selected.float().mean().cpu()) if selected.numel() else None


def _masked_row_success(
    equality: torch.Tensor,
    mask: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    valid = mask.any(dim=1)
    success = (equality | ~mask).all(dim=1)
    return success, valid


def _conditional_fraction(mask: torch.Tensor, successes: torch.Tensor) -> float | None:
    if mask.ndim != 1 or successes.shape != mask.shape:
        raise ValueError("conditional mask and successes must be aligned vectors")
    return float(successes[mask].float().mean().cpu()) if bool(mask.any()) else None


def conditional_fidelity_metrics(
    predicted: torch.Tensor,
    expected: torch.Tensor,
    *,
    conditions: Mapping[str, torch.Tensor] | None = None,
) -> dict[str, Any]:
    """Report joint/per-attribute fidelity under explicit eligibility masks.

    Typical masks are ``both_native_correct``, ``counterfactual_distinguishing``,
    and ``heldout_context``.  Empty strata remain ``None`` with a zero count;
    they are never converted into vacuous successes.
    """

    predicted = _as_label_matrix(predicted, name="predicted")
    expected = _as_label_matrix(expected, name="expected")
    if predicted.shape != expected.shape:
        raise ValueError("predicted and expected attribute shapes must match")
    equality = predicted == expected
    joint = equality.all(dim=1)
    output: dict[str, Any] = {
        "examples": int(predicted.shape[0]),
        "joint_fidelity": float(joint.float().mean().cpu()),
        "attribute_fidelity": {
            str(index): float(equality[:, index].float().mean().cpu())
            for index in range(predicted.shape[1])
        },
        "conditions": {},
    }
    if not conditions:
        return output
    all_conditions = torch.ones(
        predicted.shape[0],
        dtype=torch.bool,
        device=predicted.device,
    )
    for name, raw_mask in conditions.items():
        if not name:
            raise ValueError("condition names must be nonempty")
        mask = torch.as_tensor(raw_mask, device=predicted.device, dtype=torch.bool)
        if mask.shape != joint.shape:
            raise ValueError(f"condition {name!r} must have one entry per example")
        all_conditions &= mask
        count = int(mask.sum())
        output["conditions"][name] = {
            "examples": count,
            "fraction": float(mask.float().mean().cpu()),
            "joint_fidelity": _conditional_fraction(mask, joint),
            "attribute_fidelity": {
                str(index): _conditional_fraction(mask, equality[:, index])
                for index in range(predicted.shape[1])
            },
        }
    output["all_conditions"] = {
        "examples": int(all_conditions.sum()),
        "fraction": float(all_conditions.float().mean().cpu()),
        "joint_fidelity": _conditional_fraction(all_conditions, joint),
        "attribute_fidelity": {
            str(index): _conditional_fraction(all_conditions, equality[:, index])
            for index in range(predicted.shape[1])
        },
    }
    return output


def score_component_patch(
    predicted: torch.Tensor,
    counterfactual: torch.Tensor,
    factual: torch.Tensor,
    *,
    patched_components: torch.Tensor | Sequence[int] | Sequence[bool],
    invariant_components: torch.Tensor | Sequence[int] | Sequence[bool] | None = None,
    condition_mask: torch.Tensor | None = None,
    native_prediction: torch.Tensor | None = None,
    native_target: torch.Tensor | None = None,
) -> dict[str, Any]:
    """Score intended changes and preservation for a component-specific patch.

    ``counterfactual`` supplies desired values for patched components;
    ``factual`` supplies values that must remain invariant elsewhere.  Masks may
    be global component vectors or per-example masks (for example, operator
    write/preserved masks from the sparse task audit).
    """

    predicted = _as_label_matrix(predicted, name="predicted")
    counterfactual = _as_label_matrix(counterfactual, name="counterfactual")
    factual = _as_label_matrix(factual, name="factual")
    if predicted.shape != counterfactual.shape or factual.shape != predicted.shape:
        raise ValueError("predicted, counterfactual, and factual shapes must match")
    examples, components = predicted.shape
    patch_mask = _broadcast_component_mask(
        patched_components,
        examples=examples,
        components=components,
        device=predicted.device,
        name="patched_components",
    )
    if not bool(patch_mask.any()):
        raise ValueError("patched_components selects no components")
    invariant_mask = (
        ~patch_mask
        if invariant_components is None
        else _broadcast_component_mask(
            invariant_components,
            examples=examples,
            components=components,
            device=predicted.device,
            name="invariant_components",
        )
    )
    if bool((patch_mask & invariant_mask).any()):
        raise ValueError("patched and invariant component masks overlap")

    patch_equal = predicted == counterfactual
    invariant_equal = predicted == factual
    patch_success, patch_valid = _masked_row_success(patch_equal, patch_mask)
    invariant_success, invariant_valid = _masked_row_success(invariant_equal, invariant_mask)
    intended = torch.where(patch_mask, counterfactual, factual)
    scored_mask = patch_mask | invariant_mask
    joint_success = ((predicted == intended) | ~scored_mask).all(dim=1)
    distinguishing = ((counterfactual != factual) & patch_mask).any(dim=1)

    if condition_mask is None:
        condition = torch.ones(examples, dtype=torch.bool, device=predicted.device)
    else:
        condition = torch.as_tensor(condition_mask, device=predicted.device, dtype=torch.bool)
        if condition.shape != (examples,):
            raise ValueError("condition_mask must have one entry per example")

    native_success: torch.Tensor | None = None
    if (native_prediction is None) != (native_target is None):
        raise ValueError("native_prediction and native_target must be supplied together")
    if native_prediction is not None and native_target is not None:
        native_prediction = _as_label_matrix(native_prediction, name="native_prediction")
        native_target = _as_label_matrix(native_target, name="native_target")
        if native_prediction.shape != predicted.shape or native_target.shape != predicted.shape:
            raise ValueError("native predictions/targets must match patched prediction shape")
        native_success = (native_prediction == native_target).all(dim=1)

    per_component = {
        str(index): float(patch_equal[:, index].float().mean().cpu())
        for index in range(components)
        if bool(patch_mask[:, index].any())
    }
    metrics: dict[str, Any] = {
        "examples": examples,
        "patched_elements": int(patch_mask.sum()),
        "invariant_elements": int(invariant_mask.sum()),
        "patched_element_accuracy": _masked_element_accuracy(patch_equal, patch_mask),
        "patched_row_accuracy": _conditional_fraction(patch_valid, patch_success),
        "invariant_element_accuracy": _masked_element_accuracy(invariant_equal, invariant_mask),
        "invariant_row_accuracy": _conditional_fraction(invariant_valid, invariant_success),
        "joint_component_fidelity": float(joint_success.float().mean().cpu()),
        "distinguishing_fraction": float(distinguishing.float().mean().cpu()),
        "joint_fidelity_on_distinguishing": _conditional_fraction(distinguishing, joint_success),
        "patched_fidelity_on_distinguishing": _conditional_fraction(
            distinguishing & patch_valid, patch_success
        ),
        "invariance_on_distinguishing": _conditional_fraction(
            distinguishing & invariant_valid, invariant_success
        ),
        "condition_fraction": float(condition.float().mean().cpu()),
        "joint_fidelity_conditioned": _conditional_fraction(condition, joint_success),
        "patched_component_accuracy": per_component,
    }
    if native_success is not None:
        metrics.update(
            {
                "native_success_fraction": float(native_success.float().mean().cpu()),
                "joint_fidelity_on_native_success": _conditional_fraction(
                    native_success, joint_success
                ),
                "joint_fidelity_on_native_and_condition": _conditional_fraction(
                    native_success & condition, joint_success
                ),
                "joint_fidelity_on_native_distinguishing": _conditional_fraction(
                    native_success & distinguishing, joint_success
                ),
            }
        )
    return metrics


def score_component_patches(
    predictions: Mapping[str, torch.Tensor],
    counterfactual: torch.Tensor,
    factual: torch.Tensor,
    *,
    patched_components: torch.Tensor | Sequence[int] | Sequence[bool],
    invariant_components: torch.Tensor | Sequence[int] | Sequence[bool] | None = None,
    condition_mask: torch.Tensor | None = None,
    native_prediction: torch.Tensor | None = None,
    native_target: torch.Tensor | None = None,
    baseline: str | None = None,
) -> dict[str, Any]:
    """Score aligned and baseline patch predictions under one identical mask."""

    if not predictions:
        raise ValueError("predictions must contain at least one method")
    by_method = {
        name: score_component_patch(
            prediction,
            counterfactual,
            factual,
            patched_components=patched_components,
            invariant_components=invariant_components,
            condition_mask=condition_mask,
            native_prediction=native_prediction,
            native_target=native_target,
        )
        for name, prediction in predictions.items()
    }
    # Direct method keys are the stable receipt paths; ``by_method`` is kept as
    # a convenient namespace for programmatic iteration.
    output: dict[str, Any] = {**by_method, "by_method": by_method}
    if baseline is not None:
        if baseline not in by_method:
            raise ValueError(f"baseline {baseline!r} is not present in predictions")
        baseline_score = by_method[baseline]["joint_component_fidelity"]
        output["joint_fidelity_minus_baseline"] = {
            name: metrics["joint_component_fidelity"] - baseline_score
            for name, metrics in by_method.items()
            if name != baseline
        }
    return output


@dataclass(frozen=True)
class StatePatchResult:
    transported_hidden: torch.Tensor
    continued_hidden: torch.Tensor
    decoded: torch.Tensor


def transport_state_patch(
    source_hidden: torch.Tensor,
    state_transport: AppliesTensor,
    *,
    target_continue: Callable[[torch.Tensor], torch.Tensor],
    target_decode: Callable[[torch.Tensor], torch.Tensor],
) -> StatePatchResult:
    """Transport a source state, continue it in a target context, and decode."""

    transported = state_transport.apply(source_hidden)
    continued = target_continue(transported)
    if not torch.is_tensor(continued) or continued.shape[0] != source_hidden.shape[0]:
        raise ValueError("target_continue must return one hidden state per example")
    decoded = target_decode(continued)
    if not torch.is_tensor(decoded) or decoded.shape[0] != source_hidden.shape[0]:
        raise ValueError("target_decode must return one prediction per example")
    return StatePatchResult(transported, continued, decoded)


@dataclass(frozen=True)
class OperatorPatchResult:
    transported_code: torch.Tensor
    next_hidden: torch.Tensor
    decoded: torch.Tensor


def transport_operator_patch(
    target_hidden: torch.Tensor,
    source_operator: torch.Tensor,
    operator_transport: AppliesTensor,
    *,
    target_step: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
    target_decode: Callable[[torch.Tensor], torch.Tensor],
) -> OperatorPatchResult:
    """Patch one source operator into a target state via an explicit code map."""

    transported = operator_transport.apply(source_operator)
    next_hidden = target_step(target_hidden, transported)
    decoded = target_decode(next_hidden)
    if decoded.shape[0] != target_hidden.shape[0]:
        raise ValueError("target_decode must return one prediction per target state")
    return OperatorPatchResult(transported, next_hidden, decoded)


def operator_intertwining_metrics(
    source_hidden: torch.Tensor,
    target_hidden: torch.Tensor,
    source_operator: torch.Tensor,
    target_operator: torch.Tensor,
    state_transport: AppliesTensor,
    operator_transport: AppliesTensor,
    *,
    source_step: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
    target_step: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
    target_decode: Callable[[torch.Tensor], torch.Tensor] | None = None,
    expected_attributes: torch.Tensor | None = None,
    native_success_mask: torch.Tensor | None = None,
) -> dict[str, Any]:
    """Test transported operators, not only transported state endpoints.

    The commuting square compares ``T_state(step_A(h, op))`` with
    ``step_B(T_state(h), T_op(op))``.  A second comparison uses B's paired
    native operator code, exposing a direct operator-map failure even when a
    decoder could hide it.
    """

    mapped_hidden = state_transport.apply(source_hidden)
    mapped_operator = operator_transport.apply(source_operator)
    source_next_then_map = state_transport.apply(source_step(source_hidden, source_operator))
    map_then_target_step = target_step(mapped_hidden, mapped_operator)
    native_target_next = target_step(target_hidden, target_operator)
    output: dict[str, Any] = {
        "commuting_square": _representation_metrics(
            map_then_target_step,
            source_next_then_map,
        ),
        "transported_step_vs_native_target": _representation_metrics(
            map_then_target_step,
            native_target_next,
        ),
        "transported_operator_vs_paired_target": _representation_metrics(
            mapped_operator,
            target_operator,
        ),
    }
    if (target_decode is None) != (expected_attributes is None):
        raise ValueError("target_decode and expected_attributes must be supplied together")
    if target_decode is not None and expected_attributes is not None:
        decoded = _as_label_matrix(target_decode(map_then_target_step), name="target decode")
        expected = _as_label_matrix(expected_attributes, name="expected_attributes")
        if decoded.shape != expected.shape:
            raise ValueError("decoded operator-patch output and expected attributes differ")
        exact = (decoded == expected).all(dim=1)
        output["attribute_fidelity"] = float(exact.float().mean().cpu())
        if native_success_mask is not None:
            mask = torch.as_tensor(
                native_success_mask,
                device=exact.device,
                dtype=torch.bool,
            )
            if mask.shape != exact.shape:
                raise ValueError("native_success_mask must have one entry per example")
            output["attribute_fidelity_on_native_success"] = _conditional_fraction(mask, exact)
            output["native_success_fraction"] = float(mask.float().mean().cpu())
    return output


__all__ = [
    "TRANSPORT_ASSAY_SCHEMA",
    "AffineFitDiagnostics",
    "AssayMetadata",
    "AttributeHoldout",
    "CentroidBaseline",
    "FittedTransportAssay",
    "HoldoutPartition",
    "HoldoutSpec",
    "OperatorPatchResult",
    "PairedRepresentations",
    "ShuffledFit",
    "StatePatchResult",
    "StateInducedOperatorTransport",
    "TensorAffineTransport",
    "TensorShuffledFit",
    "build_holdout_partition",
    "concatenate_paired_representations",
    "conditional_fidelity_metrics",
    "conditional_residual_metrics",
    "cycle_consistency_metrics",
    "fit_centroid_baseline",
    "fit_tensor_transport",
    "fit_transport_assay",
    "fit_transport_assay_from_datasets",
    "fit_stable_affine_transport",
    "fit_shuffled_tensor_transport",
    "fit_within_codebook_shuffled_transport",
    "operator_intertwining_metrics",
    "score_component_patch",
    "score_component_patches",
    "source_decode_target_reembed",
    "random_matched_tensor_transport",
    "transport_operator_patch",
    "transport_state_patch",
]
