"""Exact finite soft-interface completion surfaces.

This module deliberately knows nothing about checkpoints or episode generation.  It
accepts the already evaluated trajectory tree for *one episode* and computes the
probability and centered-logit endpoints frozen in the v0.3.0 research spec.

Tree convention
---------------
At depth ``d`` a layer has shape ``(n_roots, 2**d, n_features)``.  A flattened
``(n_roots * 2**d, n_features)`` layer is accepted as well.  Word indices use
canonical binary order, so the two children of word ``i`` are ``2*i`` (R) and
``2*i + 1`` (F).  Consequently the exact-depth-h descendants of a history word
``i`` are the contiguous interval ``[i*2**h, (i+1)*2**h)``.  Concatenating
depth blocks in increasing depth gives the declared breadth-first suffix order.

All floating inputs must be float64 and finite.  Invalid data raise
``SoftSurfaceError``; values are never clipped or imputed.  Every public result
contains only JSON-serializable Python objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


PROBABILITY_EXACT_TOLERANCE = 1e-10
CENTERED_LOGIT_RELATIVE_TOLERANCE = 1e-10


class SoftSurfaceError(ValueError):
    """Raised when a tree or derived endpoint violates the frozen contract."""


@dataclass
class _VectorMoments:
    """Stable per-coordinate moments for one semantic label."""

    count: int
    mean: np.ndarray
    m2: np.ndarray
    minimum: np.ndarray
    maximum: np.ndarray


@dataclass
class _ScalarBlock:
    """Moments after reducing coordinates that occupy one signature block."""

    count: int
    dimension: int
    sse: float
    maximum_coordinate_range: float
    maximum_absolute_coordinate: float


def _ordered_layers(
    layers: Sequence[np.ndarray] | Mapping[int, np.ndarray],
    name: str,
) -> list[np.ndarray]:
    if isinstance(layers, Mapping):
        if not all(isinstance(key, (int, np.integer)) for key in layers):
            raise SoftSurfaceError(f"{name} depth keys must be integers")
        keys = sorted(int(key) for key in layers)
        if keys != list(range(len(keys))):
            raise SoftSurfaceError(f"{name} depths must be consecutive from zero")
        return [np.asarray(layers[depth]) for depth in keys]
    output = [np.asarray(layer) for layer in layers]
    if not output:
        raise SoftSurfaceError(f"{name} must contain at least depth zero")
    return output


def _normalise_feature_layers(
    layers: Sequence[np.ndarray] | Mapping[int, np.ndarray],
    name: str,
    required_depth: int,
    root_count: int | None = None,
) -> tuple[list[np.ndarray], int, int]:
    raw = _ordered_layers(layers, name)
    if len(raw) <= required_depth:
        raise SoftSurfaceError(
            f"{name} supplies depths 0..{len(raw) - 1}, but depth "
            f"{required_depth} is required"
        )

    first = raw[0]
    if first.dtype != np.dtype(np.float64):
        raise SoftSurfaceError(f"{name}[0] must have dtype float64")
    if first.ndim == 2:
        inferred_roots, feature_count = first.shape
    elif first.ndim == 3 and first.shape[1] == 1:
        inferred_roots, _, feature_count = first.shape
    else:
        raise SoftSurfaceError(
            f"{name}[0] must have shape (roots, features) or (roots, 1, features)"
        )
    if inferred_roots < 1 or feature_count < 1:
        raise SoftSurfaceError(f"{name} must have positive root and feature counts")
    if root_count is not None and inferred_roots != root_count:
        raise SoftSurfaceError(
            f"{name} root count {inferred_roots} does not match {root_count}"
        )

    output: list[np.ndarray] = []
    for depth, layer in enumerate(raw[: required_depth + 1]):
        if layer.dtype != np.dtype(np.float64):
            raise SoftSurfaceError(f"{name}[{depth}] must have dtype float64")
        width = 1 << depth
        if layer.ndim == 2 and layer.shape == (inferred_roots * width, feature_count):
            shaped = layer.reshape(inferred_roots, width, feature_count)
        elif layer.ndim == 3 and layer.shape == (
            inferred_roots,
            width,
            feature_count,
        ):
            shaped = layer
        else:
            raise SoftSurfaceError(
                f"{name}[{depth}] has shape {layer.shape}; expected "
                f"({inferred_roots * width}, {feature_count}) or "
                f"({inferred_roots}, {width}, {feature_count})"
            )
        if not np.all(np.isfinite(shaped)):
            raise SoftSurfaceError(f"{name}[{depth}] contains a nonfinite value")
        output.append(shaped)
    return output, inferred_roots, feature_count


def _normalise_semantic_layers(
    layers: Sequence[np.ndarray] | Mapping[int, np.ndarray],
    required_depth: int,
    root_count: int,
    label_count: int,
) -> list[np.ndarray]:
    raw = _ordered_layers(layers, "semantics")
    if len(raw) <= required_depth:
        raise SoftSurfaceError(
            f"semantics supplies depths 0..{len(raw) - 1}, but depth "
            f"{required_depth} is required"
        )
    output: list[np.ndarray] = []
    for depth, layer in enumerate(raw[: required_depth + 1]):
        if not np.issubdtype(layer.dtype, np.integer):
            raise SoftSurfaceError(f"semantics[{depth}] must have an integer dtype")
        width = 1 << depth
        if layer.ndim == 1 and layer.shape == (root_count * width,):
            shaped = layer.reshape(root_count, width)
        elif layer.ndim == 2 and layer.shape == (root_count, width):
            shaped = layer
        elif layer.ndim == 3 and layer.shape == (root_count, width, 1):
            shaped = layer[..., 0]
        else:
            raise SoftSurfaceError(
                f"semantics[{depth}] has shape {layer.shape}; expected "
                f"({root_count * width},) or ({root_count}, {width})"
            )
        if np.any(shaped < 0) or np.any(shaped >= label_count):
            raise SoftSurfaceError(
                f"semantics[{depth}] contains a label outside 0..{label_count - 1}"
            )
        output.append(shaped.astype(np.int64, copy=False))
    return output


def _exact_suffix_block(
    layers: Sequence[np.ndarray], history_depth: int, suffix_depth: int
) -> np.ndarray:
    """Return exact-shell signatures in canonical suffix order.

    Rows are root-major then history-word-major.  Columns are
    suffix-word-major then feature-major.
    """

    target = layers[history_depth + suffix_depth]
    roots, _, features = target.shape
    history_width = 1 << history_depth
    suffix_width = 1 << suffix_depth
    return target.reshape(roots, history_width, suffix_width, features).reshape(
        roots * history_width, suffix_width * features
    )


def exact_suffix_signature_block(
    layers: Sequence[np.ndarray] | Mapping[int, np.ndarray],
    history_depth: int,
    suffix_depth: int,
) -> list[list[float]]:
    """Expose a small exact-shell gather as a JSON-serializable nested list.

    This helper is principally useful for structural parity tests.  Production
    surface computation uses the same layout without materialising cumulative
    signatures.
    """

    if history_depth < 0 or suffix_depth < 0:
        raise SoftSurfaceError("history_depth and suffix_depth must be nonnegative")
    normalised, _, _ = _normalise_feature_layers(
        layers,
        "values",
        history_depth + suffix_depth,
    )
    return _exact_suffix_block(normalised, history_depth, suffix_depth).tolist()


def _moments(matrix: np.ndarray) -> _VectorMoments:
    if matrix.ndim != 2 or matrix.shape[0] < 1 or matrix.shape[1] < 1:
        raise SoftSurfaceError("moment matrix must be nonempty and two-dimensional")
    if matrix.dtype != np.dtype(np.float64) or not np.all(np.isfinite(matrix)):
        raise SoftSurfaceError("moment matrix must be finite float64")
    mean = np.mean(matrix, axis=0, dtype=np.float64)
    residual = matrix - mean
    m2 = np.sum(residual * residual, axis=0, dtype=np.float64)
    minimum = np.min(matrix, axis=0)
    maximum = np.max(matrix, axis=0)
    for value, field in ((mean, "mean"), (m2, "m2"), (minimum, "minimum"), (maximum, "maximum")):
        if not np.all(np.isfinite(value)):
            raise SoftSurfaceError(f"nonfinite derived {field}")
    return _VectorMoments(
        count=int(matrix.shape[0]),
        mean=mean,
        m2=m2,
        minimum=minimum,
        maximum=maximum,
    )


def _merge_vector_moments(
    left: _VectorMoments | None, right: _VectorMoments
) -> _VectorMoments:
    if left is None:
        return _VectorMoments(
            count=right.count,
            mean=right.mean.copy(),
            m2=right.m2.copy(),
            minimum=right.minimum.copy(),
            maximum=right.maximum.copy(),
        )
    if left.mean.shape != right.mean.shape:
        raise SoftSurfaceError("cannot merge moment vectors of different dimensions")
    total = left.count + right.count
    delta = right.mean - left.mean
    weight = float(right.count) / float(total)
    mean = left.mean + delta * weight
    m2 = (
        left.m2
        + right.m2
        + delta * delta * (float(left.count) * float(right.count) / float(total))
    )
    minimum = np.minimum(left.minimum, right.minimum)
    maximum = np.maximum(left.maximum, right.maximum)
    if not (
        np.all(np.isfinite(mean))
        and np.all(np.isfinite(m2))
        and np.all(np.isfinite(minimum))
        and np.all(np.isfinite(maximum))
    ):
        raise SoftSurfaceError("nonfinite value while merging history shells")
    return _VectorMoments(total, mean, m2, minimum, maximum)


def _reduce_vector_moments(moment: _VectorMoments) -> _ScalarBlock:
    coordinate_range = moment.maximum - moment.minimum
    if np.any(coordinate_range < 0.0) or np.any(moment.m2 < 0.0):
        raise SoftSurfaceError("invalid negative range or sum of squared deviations")
    block = _ScalarBlock(
        count=moment.count,
        dimension=int(moment.mean.size),
        sse=float(np.sum(moment.m2, dtype=np.float64)),
        maximum_coordinate_range=float(np.max(coordinate_range)),
        maximum_absolute_coordinate=float(
            max(np.max(np.abs(moment.minimum)), np.max(np.abs(moment.maximum)))
        ),
    )
    _validate_scalar_block(block)
    return block


def _validate_scalar_block(block: _ScalarBlock) -> None:
    if block.count < 1 or block.dimension < 1:
        raise SoftSurfaceError("scalar block must have positive count and dimension")
    values = (
        block.sse,
        block.maximum_coordinate_range,
        block.maximum_absolute_coordinate,
    )
    if not all(np.isfinite(value) and value >= 0.0 for value in values):
        raise SoftSurfaceError("scalar block contains an invalid derived statistic")


def _concatenate_scalar_blocks(
    left: _ScalarBlock | None, right: _ScalarBlock
) -> _ScalarBlock:
    """Join disjoint signature-coordinate blocks for the same history rows."""

    if left is None:
        return _ScalarBlock(
            count=right.count,
            dimension=right.dimension,
            sse=right.sse,
            maximum_coordinate_range=right.maximum_coordinate_range,
            maximum_absolute_coordinate=right.maximum_absolute_coordinate,
        )
    if left.count != right.count:
        raise SoftSurfaceError("future blocks have inconsistent history counts")
    output = _ScalarBlock(
        count=left.count,
        dimension=left.dimension + right.dimension,
        sse=left.sse + right.sse,
        maximum_coordinate_range=max(
            left.maximum_coordinate_range, right.maximum_coordinate_range
        ),
        maximum_absolute_coordinate=max(
            left.maximum_absolute_coordinate, right.maximum_absolute_coordinate
        ),
    )
    _validate_scalar_block(output)
    return output


def _cell_result(
    blocks: Sequence[_ScalarBlock | None],
    *,
    history_depth: int,
    future_depth: int,
    history_mode: str,
    future_mode: str,
    feature_count: int,
    interface: str,
) -> dict[str, object]:
    present = [block for block in blocks if block is not None]
    if not present:
        raise SoftSurfaceError("a cell contains no semantic labels")
    dimensions = {block.dimension for block in present}
    if len(dimensions) != 1:
        raise SoftSurfaceError("semantic labels have inconsistent signature dimensions")
    signature_dimension = dimensions.pop()
    expected_suffix_count = (
        (1 << (future_depth + 1)) - 1
        if future_mode == "leq"
        else 1 << future_depth
    )
    if signature_dimension != expected_suffix_count * feature_count:
        raise SoftSurfaceError("signature dimension disagrees with the suffix domain")

    per_label: list[dict[str, object]] = []
    total_sse = 0.0
    total_scalar_count = 0
    max_label_rms = 0.0
    max_range = 0.0
    max_abs = 0.0
    history_count = 0
    for label, block in enumerate(blocks):
        if block is None:
            per_label.append(
                {
                    "semantic_label": label,
                    "history_count": 0,
                    "rms_deviation": None,
                    "maximum_coordinate_range": None,
                    "maximum_absolute_coordinate": None,
                }
            )
            continue
        denominator = block.count * block.dimension
        rms = float(np.sqrt(block.sse / float(denominator)))
        if not np.isfinite(rms):
            raise SoftSurfaceError("nonfinite label RMS")
        per_label.append(
            {
                "semantic_label": label,
                "history_count": block.count,
                "rms_deviation": rms,
                "maximum_coordinate_range": block.maximum_coordinate_range,
                "maximum_absolute_coordinate": block.maximum_absolute_coordinate,
            }
        )
        total_sse += block.sse
        total_scalar_count += denominator
        history_count += block.count
        max_label_rms = max(max_label_rms, rms)
        max_range = max(max_range, block.maximum_coordinate_range)
        max_abs = max(max_abs, block.maximum_absolute_coordinate)

    pooled_rms = float(np.sqrt(total_sse / float(total_scalar_count)))
    if interface == "probability":
        exact_tolerance = PROBABILITY_EXACT_TOLERANCE
        tolerance_kind = "absolute"
    elif interface == "centered_logit":
        exact_tolerance = CENTERED_LOGIT_RELATIVE_TOLERANCE * max(1.0, max_abs)
        tolerance_kind = "relative_to_cell_max_abs"
    else:
        raise SoftSurfaceError(f"unknown soft interface: {interface}")
    values = (pooled_rms, max_label_rms, max_range, max_abs, exact_tolerance)
    if not all(np.isfinite(value) and value >= 0.0 for value in values):
        raise SoftSurfaceError("cell contains an invalid derived statistic")

    all_labels_present = len(present) == len(blocks)
    return {
        "L": int(history_depth),
        "H": int(future_depth),
        "history_mode": history_mode,
        "future_mode": future_mode,
        "history_count": int(history_count),
        "suffix_count": int(expected_suffix_count),
        "signature_scalar_dimension": int(signature_dimension),
        "scalar_observation_count": int(history_count * signature_dimension),
        "semantic_label_count_observed": int(len(present)),
        "all_semantic_labels_present": bool(all_labels_present),
        "within_label_rms_deviation": pooled_rms,
        "maximum_label_rms_deviation": max_label_rms,
        "maximum_within_label_coordinate_range": max_range,
        "maximum_absolute_coordinate": max_abs,
        "exact_tolerance": float(exact_tolerance),
        "tolerance_kind": tolerance_kind,
        "exact_soft_collapse_pass": bool(all_labels_present and max_range <= exact_tolerance),
        "per_label": per_label,
    }


def compute_soft_interface_surface(
    values_by_depth: Sequence[np.ndarray] | Mapping[int, np.ndarray],
    semantics_by_depth: Sequence[np.ndarray] | Mapping[int, np.ndarray],
    *,
    interface: str,
    max_history_depth: int = 8,
    max_future_horizon: int = 8,
    label_count: int = 8,
) -> dict[str, object]:
    """Compute all cumulative and exact-shell cells for one soft interface.

    The implementation visits every exact history/exact suffix pair once.  It
    keeps stable coordinate-wise moments only while history shells are merged,
    then reduces each disjoint future-depth block to scalar sufficient statistics.
    Thus it exactly matches explicit breadth-first concatenation without allocating
    the largest cumulative signature matrices.
    """

    if interface not in {"probability", "centered_logit"}:
        raise SoftSurfaceError("interface must be 'probability' or 'centered_logit'")
    if max_history_depth < 0 or max_future_horizon < 0:
        raise SoftSurfaceError("maximum depths must be nonnegative")
    if label_count < 1:
        raise SoftSurfaceError("label_count must be positive")
    required_depth = max_history_depth + max_future_horizon
    layers, root_count, feature_count = _normalise_feature_layers(
        values_by_depth,
        interface,
        required_depth,
    )
    semantics = _normalise_semantic_layers(
        semantics_by_depth,
        max_history_depth,
        root_count,
        label_count,
    )

    # blocks[history mode][L][exact suffix depth][semantic label]
    blocks: dict[str, list[list[list[_ScalarBlock | None]]]] = {
        "eq": [
            [[None for _ in range(label_count)] for _ in range(max_future_horizon + 1)]
            for _ in range(max_history_depth + 1)
        ],
        "leq": [
            [[None for _ in range(label_count)] for _ in range(max_future_horizon + 1)]
            for _ in range(max_history_depth + 1)
        ],
    }

    for suffix_depth in range(max_future_horizon + 1):
        cumulative_moments: list[_VectorMoments | None] = [None] * label_count
        for history_depth in range(max_history_depth + 1):
            matrix = _exact_suffix_block(layers, history_depth, suffix_depth)
            labels = semantics[history_depth].reshape(-1)
            if matrix.shape[0] != labels.size:
                raise SoftSurfaceError("history rows and semantic labels disagree")
            for label in range(label_count):
                selected = matrix[labels == label]
                exact = _moments(selected) if selected.shape[0] else None
                if exact is not None:
                    blocks["eq"][history_depth][suffix_depth][label] = (
                        _reduce_vector_moments(exact)
                    )
                    cumulative_moments[label] = _merge_vector_moments(
                        cumulative_moments[label], exact
                    )
                if cumulative_moments[label] is not None:
                    blocks["leq"][history_depth][suffix_depth][label] = (
                        _reduce_vector_moments(cumulative_moments[label])
                    )

    view_names = {
        ("leq", "leq"): "cumulative_history_cumulative_future",
        ("eq", "leq"): "exact_history_cumulative_future",
        ("leq", "eq"): "cumulative_history_exact_future",
        ("eq", "eq"): "exact_history_exact_future",
    }
    views: dict[str, list[dict[str, object]]] = {name: [] for name in view_names.values()}
    for history_mode in ("leq", "eq"):
        for history_depth in range(max_history_depth + 1):
            cumulative_future: list[_ScalarBlock | None] = [None] * label_count
            for suffix_depth in range(max_future_horizon + 1):
                exact_blocks = blocks[history_mode][history_depth][suffix_depth]
                exact_result = _cell_result(
                    exact_blocks,
                    history_depth=history_depth,
                    future_depth=suffix_depth,
                    history_mode=history_mode,
                    future_mode="eq",
                    feature_count=feature_count,
                    interface=interface,
                )
                views[view_names[(history_mode, "eq")]].append(exact_result)
                for label, block in enumerate(exact_blocks):
                    if block is not None:
                        cumulative_future[label] = _concatenate_scalar_blocks(
                            cumulative_future[label], block
                        )
                cumulative_result = _cell_result(
                    cumulative_future,
                    history_depth=history_depth,
                    future_depth=suffix_depth,
                    history_mode=history_mode,
                    future_mode="leq",
                    feature_count=feature_count,
                    interface=interface,
                )
                views[view_names[(history_mode, "leq")]].append(cumulative_result)

    primary = views["cumulative_history_cumulative_future"]
    expected_cells = (max_history_depth + 1) * (max_future_horizon + 1)
    if any(len(cells) != expected_cells for cells in views.values()):
        raise SoftSurfaceError("surface cell count is incomplete")
    return {
        "interface": interface,
        "root_count": int(root_count),
        "feature_count": int(feature_count),
        "semantic_label_count": int(label_count),
        "max_history_depth": int(max_history_depth),
        "max_future_horizon": int(max_future_horizon),
        "cell_count_per_view": int(expected_cells),
        "all_cumulative_cells_exact_soft_collapse": bool(
            all(cell["exact_soft_collapse_pass"] for cell in primary)
        ),
        "views": views,
    }


def compute_soft_completion_surface(
    probabilities_by_depth: Sequence[np.ndarray] | Mapping[int, np.ndarray],
    centered_logits_by_depth: Sequence[np.ndarray] | Mapping[int, np.ndarray],
    semantics_by_depth: Sequence[np.ndarray] | Mapping[int, np.ndarray],
    *,
    max_history_depth: int = 8,
    max_future_horizon: int = 8,
    label_count: int = 8,
) -> dict[str, object]:
    """Compute both registered soft interfaces for one episode."""

    probability = compute_soft_interface_surface(
        probabilities_by_depth,
        semantics_by_depth,
        interface="probability",
        max_history_depth=max_history_depth,
        max_future_horizon=max_future_horizon,
        label_count=label_count,
    )
    centered_logit = compute_soft_interface_surface(
        centered_logits_by_depth,
        semantics_by_depth,
        interface="centered_logit",
        max_history_depth=max_history_depth,
        max_future_horizon=max_future_horizon,
        label_count=label_count,
    )
    if probability["root_count"] != centered_logit["root_count"]:
        raise SoftSurfaceError("soft interfaces have different root counts")
    return {
        "schema": "komorebi.neuralese.soft_completion_surface.v1",
        "episode_local": True,
        "suffix_order": "breadth_first_depth_then_canonical_binary_word",
        "float_dtype": "float64",
        "max_history_depth": int(max_history_depth),
        "max_future_horizon": int(max_future_horizon),
        "interfaces": {
            "probability": probability,
            "centered_logit": centered_logit,
        },
        "both_interfaces_exact_on_cumulative_rectangle": bool(
            probability["all_cumulative_cells_exact_soft_collapse"]
            and centered_logit["all_cumulative_cells_exact_soft_collapse"]
        ),
    }


__all__ = [
    "CENTERED_LOGIT_RELATIVE_TOLERANCE",
    "PROBABILITY_EXACT_TOLERANCE",
    "SoftSurfaceError",
    "compute_soft_completion_surface",
    "compute_soft_interface_surface",
    "exact_suffix_signature_block",
]
