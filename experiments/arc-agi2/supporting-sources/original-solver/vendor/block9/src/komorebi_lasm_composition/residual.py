"""Residual analysis and well-founded progress certificates.

Residual distance is measured independently for every demonstration.  Aggregate
compensation is forbidden: an accepted step is nonincreasing on every example
and strictly decreasing on at least one.  The production ``residual_subset``
mode is stronger still, permitting only removal of currently wrong cells.
"""
from __future__ import annotations

from collections import Counter
from numbers import Integral
from typing import Any, Iterable, Mapping, Sequence

from .model import (
    ExampleResidual,
    Grid,
    Measure,
    ProgressCertificate,
    ProgressMode,
    ResidualBatch,
    sha256_record,
    validate_grid,
)


_MISSING = object()
_VALID_MODES = frozenset(
    {"residual_subset", "strict_descent", "shape_correction"}
)


def _grid_sequence(values: Sequence[object], label: str) -> tuple[Grid, ...]:
    if isinstance(values, (str, bytes, bytearray, Mapping)):
        raise TypeError(f"{label} must be a finite grid sequence")
    try:
        count = len(values)
        raw = [values[index] for index in range(count)]
    except (TypeError, AttributeError, KeyError, IndexError) as error:
        raise TypeError(f"{label} must be a finite indexable grid sequence") from error
    if not raw:
        raise ValueError(f"{label} must be nonempty")
    return tuple(validate_grid(grid) for grid in raw)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def infer_background(grid: object) -> int:
    """Deterministic root background role: highest count, then lowest color."""

    frozen = validate_grid(grid)
    counts = Counter(cell for row in frozen for cell in row)
    maximum = max(counts.values())
    return min(color for color, count in counts.items() if count == maximum)


def _role_background(role: object, current: Grid) -> int:
    if role is None:
        return infer_background(current)
    if isinstance(role, bool):
        raise TypeError("background role cannot be Boolean")
    if isinstance(role, Integral):
        color = role
    elif isinstance(role, Mapping):
        candidates = (
            role.get("background_color", _MISSING),
            role.get("background", _MISSING),
            role.get("bg", _MISSING),
        )
        selected = next((value for value in candidates if value is not _MISSING), _MISSING)
        if selected is _MISSING:
            raise ValueError("root role mapping has no background color")
        color = selected
    else:
        selected = _MISSING
        for name in ("background_color", "background", "bg"):
            if hasattr(role, name):
                selected = getattr(role, name)
                break
        if selected is _MISSING:
            raise TypeError("root role must provide a background color")
        color = selected
    if (
        isinstance(color, bool)
        or not isinstance(color, Integral)
        or not 0 <= int(color) <= 9
    ):
        raise ValueError("root background color must be an integer in 0..9")
    return int(color)


def _normalize_backgrounds(
    currents: tuple[Grid, ...],
    root_roles: Sequence[object] | None,
) -> tuple[int, ...]:
    if root_roles is None:
        return tuple(infer_background(current) for current in currents)
    if isinstance(root_roles, (str, bytes, bytearray, Mapping)):
        raise TypeError("root_roles must be a sequence with one item per demonstration")
    try:
        count = len(root_roles)
    except (TypeError, AttributeError) as error:
        raise TypeError("root_roles must be a finite sequence") from error
    if count != len(currents):
        raise ValueError("root_roles must match the demonstration count")
    return tuple(
        _role_background(root_roles[index], current)
        for index, current in enumerate(currents)
    )


def mismatch_coordinates(current: object, target: object) -> frozenset[tuple[int, int]]:
    """Return top-left-aligned mismatch coordinates, including shape overhangs."""

    source = validate_grid(current)
    expected = validate_grid(target)
    source_height, source_width = _shape(source)
    target_height, target_width = _shape(expected)
    height = max(source_height, target_height)
    width = max(source_width, target_width)
    mismatches: set[tuple[int, int]] = set()
    for row in range(height):
        for column in range(width):
            left = (
                source[row][column]
                if row < source_height and column < source_width
                else _MISSING
            )
            right = (
                expected[row][column]
                if row < target_height and column < target_width
                else _MISSING
            )
            if left != right:
                mismatches.add((row, column))
    return frozenset(mismatches)


def _component_count(cells: frozenset[tuple[int, int]]) -> int:
    remaining = set(cells)
    count = 0
    while remaining:
        count += 1
        stack = [remaining.pop()]
        while stack:
            row, column = stack.pop()
            for neighbor in (
                (row - 1, column),
                (row + 1, column),
                (row, column - 1),
                (row, column + 1),
            ):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
    return count


def residual_measure(current: object, target: object) -> Measure:
    """The well-founded per-example residual measure.

    Coordinates are ``(shape mismatch, dimension distance, wrong cells,
    wrong-cell components)`` and are compared lexicographically.
    """

    source = validate_grid(current)
    expected = validate_grid(target)
    source_shape = _shape(source)
    target_shape = _shape(expected)
    mismatches = mismatch_coordinates(source, expected)
    return (
        int(source_shape != target_shape),
        abs(source_shape[0] - target_shape[0])
        + abs(source_shape[1] - target_shape[1]),
        len(mismatches),
        _component_count(mismatches),
    )


def _obstruction_summary(
    current: Grid,
    target: Grid,
    background: int,
) -> tuple[tuple[str, ...], int, int, int]:
    if _shape(current) != _shape(target):
        return ("shape_change",), 0, 0, 0

    added = 0
    removed = 0
    recolored = 0
    for source_row, target_row in zip(current, target):
        for source, expected in zip(source_row, target_row):
            if source == expected:
                continue
            source_support = source != background
            target_support = expected != background
            if not source_support and target_support:
                added += 1
            elif source_support and not target_support:
                removed += 1
            elif source_support and target_support:
                recolored += 1

    if added == removed == recolored == 0:
        kinds = ("exact",)
    elif added and not removed and not recolored:
        kinds = ("support_add",)
    elif removed and not added and not recolored:
        kinds = ("support_remove",)
    elif recolored and not added and not removed:
        kinds = ("recolor",)
    elif added or removed:
        kinds = ("support_mixed",)
    else:
        kinds = ("mixed",)
    return tuple(sorted(kinds)), added, removed, recolored


def derive_example_residual(
    current: object,
    target: object,
    root_background: object | None = None,
) -> ExampleResidual:
    source = validate_grid(current)
    expected = validate_grid(target)
    background = _role_background(root_background, source)
    mismatches = mismatch_coordinates(source, expected)
    kinds, added, removed, recolored = _obstruction_summary(
        source, expected, background
    )
    return ExampleResidual(
        current_hash=sha256_record(source),
        target_hash=sha256_record(expected),
        current_shape=_shape(source),
        target_shape=_shape(expected),
        measure=residual_measure(source, expected),
        mismatch_count=len(mismatches),
        mismatch_components=_component_count(mismatches),
        obstruction_kinds=kinds,
        background_color=background,
        added_cells=added,
        removed_cells=removed,
        recolored_cells=recolored,
    )


def _route_lanes(union_kinds: Iterable[str]) -> tuple[str, ...]:
    kinds = set(union_kinds)
    lanes: list[str] = []
    if "shape_change" in kinds:
        lanes.append("shape_constructor")
    if "support_add" in kinds or "support_mixed" in kinds:
        lanes.extend(("support_completion", "ambient_construction"))
    if "support_remove" in kinds or "support_mixed" in kinds:
        lanes.append("support_reduction")
    if "recolor" in kinds or "mixed" in kinds:
        lanes.append("role_rebinding")
    if kinds == {"exact"}:
        lanes.append("exact")
    else:
        lanes.append("residual_scene")
    return tuple(dict.fromkeys(lanes))


def derive_residual_batch(
    currents: Sequence[object],
    targets: Sequence[object],
    root_roles: Sequence[object] | None = None,
    *,
    root_backgrounds: Sequence[object] | None = None,
) -> ResidualBatch:
    """Recompute a residual packet from the current intermediate states.

    ``root_roles`` (or its explicit ``root_backgrounds`` alias) should be reused
    at every depth so that support semantics cannot oscillate when an
    intermediate grid changes its modal color.
    """

    source_grids = _grid_sequence(currents, "currents")
    target_grids = _grid_sequence(targets, "targets")
    if len(source_grids) != len(target_grids):
        raise ValueError("currents and targets must have equal length")
    if root_roles is not None and root_backgrounds is not None:
        raise ValueError("provide root_roles or root_backgrounds, not both")
    selected_roles = root_backgrounds if root_backgrounds is not None else root_roles
    backgrounds = _normalize_backgrounds(source_grids, selected_roles)
    examples = tuple(
        derive_example_residual(current, target, background)
        for current, target, background in zip(
            source_grids, target_grids, backgrounds
        )
    )
    union = tuple(
        sorted({kind for example in examples for kind in example.obstruction_kinds})
    )
    common = set(examples[0].obstruction_kinds)
    for example in examples[1:]:
        common.intersection_update(example.obstruction_kinds)
    return ResidualBatch(
        examples=examples,
        common_kinds=tuple(sorted(common)),
        union_kinds=union,
        route_lanes=_route_lanes(union),
    )


def state_hash(grids: Sequence[object]) -> str:
    return sha256_record(_grid_sequence(grids, "state grids"))


def _invalid_transition(
    before_measures: tuple[Measure, ...],
    after_measures: tuple[Measure, ...],
) -> bool:
    for before, after in zip(before_measures, after_measures):
        if after > before:
            return True
        if before == (0, 0, 0, 0) and after != before:
            return True
    return not any(after < before for before, after in zip(before_measures, after_measures))


def certify_transition(
    before: Sequence[object],
    after: Sequence[object],
    targets: Sequence[object],
    mode: ProgressMode = "residual_subset",
    *,
    root_roles: Sequence[object] | None = None,
    root_backgrounds: Sequence[object] | None = None,
    visited_state_hashes: Iterable[str] = (),
) -> ProgressCertificate | None:
    """Return a certificate exactly when a transition makes valid progress.

    Invalid semantic transitions return ``None``.  Malformed grids and malformed
    API arguments raise, keeping input validation distinct from search rejection.
    """

    if mode not in _VALID_MODES:
        raise ValueError("invalid progress mode")
    before_grids = _grid_sequence(before, "before grids")
    after_grids = _grid_sequence(after, "after grids")
    target_grids = _grid_sequence(targets, "target grids")
    if not (
        len(before_grids) == len(after_grids) == len(target_grids)
    ):
        raise ValueError("before, after, and targets must have equal length")
    if root_roles is not None and root_backgrounds is not None:
        raise ValueError("provide root_roles or root_backgrounds, not both")
    selected_roles = root_backgrounds if root_backgrounds is not None else root_roles
    backgrounds = _normalize_backgrounds(before_grids, selected_roles)

    before_state = sha256_record(before_grids)
    after_state = sha256_record(after_grids)
    if before_state == after_state:
        return None
    visited = tuple(visited_state_hashes)
    if any(not isinstance(digest, str) for digest in visited):
        raise TypeError("visited_state_hashes must contain strings")
    if after_state in visited:
        return None

    before_batch = derive_residual_batch(
        before_grids, target_grids, root_backgrounds=backgrounds
    )
    after_batch = derive_residual_batch(
        after_grids, target_grids, root_backgrounds=backgrounds
    )
    before_measures = before_batch.measures
    after_measures = after_batch.measures
    if _invalid_transition(before_measures, after_measures):
        return None

    before_errors = tuple(
        mismatch_coordinates(current, target)
        for current, target in zip(before_grids, target_grids)
    )
    after_errors = tuple(
        mismatch_coordinates(current, target)
        for current, target in zip(after_grids, target_grids)
    )
    corrected = tuple(
        len(old_errors - new_errors)
        for old_errors, new_errors in zip(before_errors, after_errors)
    )
    introduced = tuple(
        len(new_errors - old_errors)
        for old_errors, new_errors in zip(before_errors, after_errors)
    )

    if mode == "residual_subset":
        # Cellwise subset comparison is meaningful only after target shape has
        # been reached.  Shape-changing work has its own explicit lane.
        if any(
            _shape(current) != _shape(target)
            or _shape(candidate) != _shape(target)
            for current, candidate, target in zip(
                before_grids, after_grids, target_grids
            )
        ):
            return None
        if any(
            not new_errors.issubset(old_errors)
            for old_errors, new_errors in zip(before_errors, after_errors)
        ):
            return None
        if not any(
            new_errors < old_errors
            for old_errors, new_errors in zip(before_errors, after_errors)
        ):
            return None
    elif mode == "shape_correction":
        # A shape-correct demonstration can never leave its target shape.
        if any(
            _shape(current) == _shape(target)
            and _shape(candidate) != _shape(target)
            for current, candidate, target in zip(
                before_grids, after_grids, target_grids
            )
        ):
            return None
        if not any(
            after_measure[:2] < before_measure[:2]
            for before_measure, after_measure in zip(
                before_measures, after_measures
            )
        ):
            return None

    try:
        return ProgressCertificate(
            before_packet_id=before_batch.aggregate_packet_id,
            after_packet_id=after_batch.aggregate_packet_id,
            before_measures=before_measures,
            after_measures=after_measures,
            corrected_cells=corrected,
            introduced_errors=introduced,
            mode=mode,
            before_state_hash=before_state,
            after_state_hash=after_state,
        )
    except ValueError:
        # The record repeats the core invariants defensively.  A failure here is
        # a rejected proposal, not a partially valid certificate.
        return None


def require_certified_transition(
    before: Sequence[object],
    after: Sequence[object],
    targets: Sequence[object],
    mode: ProgressMode = "residual_subset",
    **kwargs: Any,
) -> ProgressCertificate:
    certificate = certify_transition(before, after, targets, mode, **kwargs)
    if certificate is None:
        raise ValueError("transition does not satisfy the requested progress contract")
    return certificate


def verify_progress_certificate(
    certificate: ProgressCertificate,
    before: Sequence[object],
    after: Sequence[object],
    targets: Sequence[object],
    *,
    root_roles: Sequence[object] | None = None,
    root_backgrounds: Sequence[object] | None = None,
) -> bool:
    if not isinstance(certificate, ProgressCertificate):
        return False
    recomputed = certify_transition(
        before,
        after,
        targets,
        certificate.mode,
        root_roles=root_roles,
        root_backgrounds=root_backgrounds,
    )
    return recomputed is not None and recomputed.to_record() == certificate.to_record()


def transition_decreases(
    before: Sequence[object],
    after: Sequence[object],
    targets: Sequence[object],
    mode: ProgressMode = "residual_subset",
    **kwargs: Any,
) -> bool:
    return certify_transition(before, after, targets, mode, **kwargs) is not None


__all__ = [
    "ExampleResidual",
    "ProgressCertificate",
    "ResidualBatch",
    "certify_transition",
    "derive_example_residual",
    "derive_residual_batch",
    "infer_background",
    "mismatch_coordinates",
    "require_certified_transition",
    "residual_measure",
    "state_hash",
    "transition_decreases",
    "verify_progress_certificate",
]
