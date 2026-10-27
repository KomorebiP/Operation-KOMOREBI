"""Relational feature induction entrant for PR-LASM Block 13.

This module is deliberately task-local.  It receives labelled demonstrations and
sanitized test inputs, constructs finite per-cell relational feature tables, and
returns only programs that reproduce every demonstration exactly.  It never
accepts a task identifier or a test output.

The entrant is a tournament proposal generator rather than a production
authorization policy.  The Block 13 harness remains responsible for freezing,
quotienting, scoring, and promotion.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import itertools
import json
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


Grid = list[list[int]]
Cell = tuple[int, int]
PAD = -1


@dataclass(frozen=True)
class Limits:
    max_side: int = 30
    max_features: int = 48
    max_depth: int = 4
    beam_width: int = 64
    max_programs: int = 128
    max_table_entries: int = 4096

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        known = {field: int(value.get(field, getattr(cls(), field))) for field in cls.__dataclass_fields__}
        return cls(**known)


class Inapplicable(ValueError):
    """Raised for malformed or out-of-domain ARC tasks."""


def _grid(value: Any, limits: Limits) -> np.ndarray:
    array = np.asarray(value)
    if array.ndim != 2 or array.size == 0:
        raise Inapplicable("grid must be a nonempty matrix")
    if array.shape[0] > limits.max_side or array.shape[1] > limits.max_side:
        raise Inapplicable("grid exceeds the declared side limit")
    if array.dtype.kind not in {"i", "u"}:
        raise Inapplicable("grid colors must be integral")
    array = array.astype(np.int16, copy=True)
    if np.any(array < 0) or np.any(array > 9):
        raise Inapplicable("grid color outside ARC palette")
    return array


def _plain(array: np.ndarray) -> Grid:
    return [[int(value) for value in row] for row in array.tolist()]


def _mode(array: np.ndarray) -> int:
    counts = Counter(int(value) for value in array.flat)
    return min(counts, key=lambda value: (-counts[value], value))


def _components(mask: np.ndarray, connectivity: int) -> list[list[Cell]]:
    height, width = mask.shape
    unseen = {(int(row), int(column)) for row, column in zip(*np.where(mask))}
    directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
    if connectivity == 8:
        directions += ((-1, -1), (-1, 1), (1, -1), (1, 1))
    output: list[list[Cell]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        cells: list[Cell] = []
        while queue:
            row, column = queue.popleft()
            cells.append((row, column))
            for dr, dc in directions:
                other = (row + dr, column + dc)
                if other in unseen and 0 <= other[0] < height and 0 <= other[1] < width:
                    unseen.remove(other)
                    queue.append(other)
        output.append(sorted(cells))
    return sorted(output, key=lambda cells: (cells[0], len(cells)))


def _hole_count(cells: Sequence[Cell]) -> int:
    if not cells:
        return 0
    top = min(row for row, _ in cells)
    bottom = max(row for row, _ in cells)
    left = min(column for _, column in cells)
    right = max(column for _, column in cells)
    height, width = bottom - top + 3, right - left + 3
    occupied = np.zeros((height, width), dtype=bool)
    for row, column in cells:
        occupied[row - top + 1, column - left + 1] = True
    exterior = np.zeros_like(occupied)
    queue = deque([(0, 0)])
    exterior[0, 0] = True
    while queue:
        row, column = queue.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rr, cc = row + dr, column + dc
            if 0 <= rr < height and 0 <= cc < width and not occupied[rr, cc] and not exterior[rr, cc]:
                exterior[rr, cc] = True
                queue.append((rr, cc))
    return len(_components(~occupied & ~exterior, 4))


def _rank(values: Iterable[int], value: int) -> tuple[int, int]:
    ordered = sorted(set(int(item) for item in values))
    return ordered.index(int(value)), len(ordered)


def _window(array: np.ndarray, row: int, column: int, radius: int, *, support: bool, background: int) -> tuple[int, ...]:
    values: list[int] = []
    height, width = array.shape
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            rr, cc = row + dr, column + dc
            if not (0 <= rr < height and 0 <= cc < width):
                values.append(PAD)
            else:
                color = int(array[rr, cc])
                values.append(int(color != background) if support else color)
    return tuple(values)


def _ray(array: np.ndarray, row: int, column: int, dr: int, dc: int, background: int) -> tuple[int, int]:
    height, width = array.shape
    rr, cc, distance = row + dr, column + dc, 1
    while 0 <= rr < height and 0 <= cc < width:
        color = int(array[rr, cc])
        if color != background:
            return color, distance
        rr += dr
        cc += dc
        distance += 1
    return PAD, 0


def _cell_feature_maps(array: np.ndarray) -> dict[str, np.ndarray]:
    """Return a deterministic bank of hashable categorical feature arrays."""

    height, width = array.shape
    background = _mode(array)
    support = array != background
    rows, columns = np.indices(array.shape)
    maps: dict[str, np.ndarray] = {}

    def object_map(function) -> np.ndarray:
        result = np.empty(array.shape, dtype=object)
        for row in range(height):
            for column in range(width):
                result[row, column] = function(row, column)
        return result

    maps["color"] = array.astype(object)
    maps["is_background"] = (array == background).astype(object)
    maps["border_role"] = object_map(
        lambda r, c: (
            int(r == 0), int(r == height - 1), int(c == 0), int(c == width - 1)
        )
    )
    maps["border_distance"] = object_map(
        lambda r, c: (r, height - 1 - r, c, width - 1 - c)
    )
    maps["normalized_position"] = object_map(
        lambda r, c: (
            Fraction(r, max(1, height - 1)), Fraction(c, max(1, width - 1))
        )
    )
    maps["diagonal_role"] = object_map(
        lambda r, c: (
            int(r * max(1, width - 1) == c * max(1, height - 1)),
            int(r * max(1, width - 1) == (width - 1 - c) * max(1, height - 1)),
        )
    )
    maps["row_signature"] = object_map(lambda r, c: tuple(int(value) for value in array[r, :]))
    maps["column_signature"] = object_map(lambda r, c: tuple(int(value) for value in array[:, c]))
    maps["row_support_signature"] = object_map(lambda r, c: tuple(int(value) for value in support[r, :]))
    maps["column_support_signature"] = object_map(lambda r, c: tuple(int(value) for value in support[:, c]))
    maps["row_nonbackground_count"] = object_map(lambda r, c: int(np.count_nonzero(support[r, :])))
    maps["column_nonbackground_count"] = object_map(lambda r, c: int(np.count_nonzero(support[:, c])))
    maps["row_same_color_count"] = object_map(lambda r, c: int(np.count_nonzero(array[r, :] == array[r, c])))
    maps["column_same_color_count"] = object_map(lambda r, c: int(np.count_nonzero(array[:, c] == array[r, c])))

    for radius in (1, 2):
        maps[f"patch_r{radius}"] = object_map(
            lambda r, c, radius=radius: _window(array, r, c, radius, support=False, background=background)
        )
        maps[f"support_patch_r{radius}"] = object_map(
            lambda r, c, radius=radius: _window(array, r, c, radius, support=True, background=background)
        )
        maps[f"histogram_r{radius}"] = object_map(
            lambda r, c, radius=radius: tuple(
                sorted(
                    Counter(
                        value
                        for value in _window(array, r, c, radius, support=False, background=background)
                        if value != PAD
                    ).items()
                )
            )
        )

    neighbor_directions = {
        "orthogonal_neighbors": ((-1, 0), (1, 0), (0, -1), (0, 1)),
        "diagonal_neighbors": ((-1, -1), (-1, 1), (1, -1), (1, 1)),
        "all_neighbors": tuple(
            (dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)
        ),
    }
    for name, directions in neighbor_directions.items():
        maps[name] = object_map(
            lambda r, c, directions=directions: tuple(
                int(array[r + dr, c + dc]) if 0 <= r + dr < height and 0 <= c + dc < width else PAD
                for dr, dc in directions
            )
        )
        maps[f"{name}_same_count"] = object_map(
            lambda r, c, directions=directions: sum(
                0 <= r + dr < height
                and 0 <= c + dc < width
                and int(array[r + dr, c + dc]) == int(array[r, c])
                for dr, dc in directions
            )
        )

    ray_directions = (
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1),
    )
    maps["ray_signature"] = object_map(
        lambda r, c: tuple(_ray(array, r, c, dr, dc, background) for dr, dc in ray_directions)
    )
    maps["horizontal_ray_pair"] = object_map(
        lambda r, c: (_ray(array, r, c, 0, -1, background), _ray(array, r, c, 0, 1, background))
    )
    maps["vertical_ray_pair"] = object_map(
        lambda r, c: (_ray(array, r, c, -1, 0, background), _ray(array, r, c, 1, 0, background))
    )
    maps["diagonal_ray_pairs"] = object_map(
        lambda r, c: (
            _ray(array, r, c, -1, -1, background), _ray(array, r, c, 1, 1, background),
            _ray(array, r, c, -1, 1, background), _ray(array, r, c, 1, -1, background),
        )
    )

    maps["symmetry_colors"] = object_map(
        lambda r, c: (
            int(array[height - 1 - r, c]), int(array[r, width - 1 - c]),
            int(array[height - 1 - r, width - 1 - c]),
        )
    )
    if height == width:
        maps["square_dihedral_colors"] = object_map(
            lambda r, c: (
                int(array[c, r]), int(array[width - 1 - c, r]),
                int(array[c, height - 1 - r]), int(array[width - 1 - c, height - 1 - r]),
            )
        )

    foreground_cells = [(int(row), int(column)) for row, column in zip(*np.where(support))]
    if foreground_cells:
        top = min(row for row, _ in foreground_cells)
        bottom = max(row for row, _ in foreground_cells)
        left = min(column for _, column in foreground_cells)
        right = max(column for _, column in foreground_cells)
        maps["foreground_bbox_role"] = object_map(
            lambda r, c: (
                int(top <= r <= bottom and left <= c <= right),
                r - top, bottom - r, c - left, right - c,
            )
        )
        maps["nearest_foreground"] = object_map(
            lambda r, c: min(
                (
                    abs(r - rr) + abs(c - cc),
                    max(abs(r - rr), abs(c - cc)),
                    int(array[rr, cc]),
                )
                for rr, cc in foreground_cells
            )
        )

    for connectivity in (4, 8):
        component_records: list[tuple[list[Cell], int]] = []
        for color in sorted(int(value) for value in np.unique(array) if int(value) != background):
            for cells in _components(array == color, connectivity):
                component_records.append((cells, color))
        component_records.sort(key=lambda item: (item[0][0], item[1]))
        cell_to_record: dict[Cell, tuple[Any, ...]] = {}
        sizes = [len(cells) for cells, _ in component_records]
        for cells, color in component_records:
            top = min(row for row, _ in cells)
            bottom = max(row for row, _ in cells)
            left = min(column for _, column in cells)
            right = max(column for _, column in cells)
            record = (
                color,
                len(cells),
                bottom - top + 1,
                right - left + 1,
                _hole_count(cells),
                _rank(sizes, len(cells)),
            )
            for cell in cells:
                cell_to_record[cell] = record
        maps[f"component_c{connectivity}"] = object_map(
            lambda r, c, records=cell_to_record: records.get((r, c), (background, 0, 0, 0, 0, (-1, len(set(sizes)))))
        )

    return maps


def _hashable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return (value.numerator, value.denominator)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, tuple):
        return tuple(_hashable(item) for item in value)
    return value


def _feature_rows(array: np.ndarray, feature_names: Sequence[str]) -> list[tuple[Any, ...]]:
    maps = _cell_feature_maps(array)
    return [
        tuple(_hashable(maps[name][row, column]) for name in feature_names)
        for row in range(array.shape[0])
        for column in range(array.shape[1])
    ]


def _deterministic_table(keys: Sequence[tuple[Any, ...]], labels: Sequence[int]) -> dict[tuple[Any, ...], int] | None:
    table: dict[tuple[Any, ...], int] = {}
    for key, label in zip(keys, labels):
        label = int(label)
        if key in table and table[key] != label:
            return None
        table[key] = label
    return table


def _conflict_score(keys: Sequence[tuple[Any, ...]], labels: Sequence[int]) -> tuple[int, int]:
    groups: dict[tuple[Any, ...], Counter[int]] = {}
    for key, label in zip(keys, labels):
        groups.setdefault(key, Counter())[int(label)] += 1
    conflicts = sum(sum(counts.values()) - max(counts.values()) for counts in groups.values())
    return conflicts, len(groups)


def _candidate_feature_sets(
    feature_names: Sequence[str],
    rows_by_grid: Sequence[dict[str, list[Any]]],
    labels: Sequence[int],
    limits: Limits,
) -> list[tuple[str, ...]]:
    """Beam-search minimal categorical feature conjunctions."""

    flat: dict[str, list[Any]] = {
        name: list(itertools.chain.from_iterable(grid[name] for grid in rows_by_grid))
        for name in feature_names
    }

    def keys(names: tuple[str, ...]) -> list[tuple[Any, ...]]:
        return [tuple(flat[name][index] for name in names) for index in range(len(labels))]

    frontier: list[tuple[str, ...]] = [()]
    exact_sets: list[tuple[str, ...]] = []
    seen = {()}
    for _depth in range(1, limits.max_depth + 1):
        expanded: list[tuple[tuple[int, int, int, tuple[str, ...]], tuple[str, ...]]] = []
        for prefix in frontier:
            start = feature_names.index(prefix[-1]) + 1 if prefix else 0
            for name in feature_names[start:]:
                proposal = prefix + (name,)
                if proposal in seen:
                    continue
                seen.add(proposal)
                proposal_keys = keys(proposal)
                conflicts, groups = _conflict_score(proposal_keys, labels)
                if conflicts == 0:
                    if len(set(proposal_keys)) <= limits.max_table_entries:
                        exact_sets.append(proposal)
                    continue
                expanded.append(((conflicts, len(proposal), -groups, proposal), proposal))
        expanded.sort(key=lambda item: item[0])
        frontier = [proposal for _, proposal in expanded[: limits.beam_width]]
        if not frontier:
            break
    return sorted(set(exact_sets), key=lambda names: (len(names), names))


def _serialize_key(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_serialize_key(item) for item in value]
    return value


def _table_record(table: Mapping[tuple[Any, ...], int]) -> list[dict[str, Any]]:
    return [
        {"key": _serialize_key(key), "output": int(table[key])}
        for key in sorted(table, key=repr)
    ]


def _predict(
    array: np.ndarray,
    feature_names: Sequence[str],
    table: Mapping[tuple[Any, ...], int],
    fallback: str,
    output_mode: int,
) -> tuple[np.ndarray, int]:
    keys = _feature_rows(array, feature_names)
    background = _mode(array)
    result = array.copy()
    unseen = 0
    for index, key in enumerate(keys):
        row, column = divmod(index, array.shape[1])
        if key in table:
            result[row, column] = int(table[key])
            continue
        unseen += 1
        if fallback == "background":
            result[row, column] = background
        elif fallback == "output_mode":
            result[row, column] = output_mode
        elif fallback != "identity":
            raise AssertionError(f"unknown fallback {fallback}")
    return result, unseen


def _loo_exact(
    feature_names: Sequence[str],
    fallback: str,
    train_inputs: Sequence[np.ndarray],
    train_outputs: Sequence[np.ndarray],
    output_mode: int,
) -> bool:
    if len(train_inputs) < 2:
        return False
    for held_out in range(len(train_inputs)):
        keys: list[tuple[Any, ...]] = []
        labels: list[int] = []
        for index, (source, target) in enumerate(zip(train_inputs, train_outputs)):
            if index == held_out:
                continue
            keys.extend(_feature_rows(source, feature_names))
            labels.extend(int(value) for value in target.flat)
        table = _deterministic_table(keys, labels)
        if table is None:
            return False
        predicted, _ = _predict(train_inputs[held_out], feature_names, table, fallback, output_mode)
        if not np.array_equal(predicted, train_outputs[held_out]):
            return False
    return True


def _behavior_hash(outputs: Sequence[np.ndarray]) -> str:
    payload = json.dumps([_plain(array) for array in outputs], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compile_task(task: Mapping[str, Any], limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile exact demonstration-fitting relational feature programs.

    Returned candidates are sorted deterministically and quotiented by their
    complete test behavior.  An empty list is a normal abstention.
    """

    bounds = Limits.from_value(limits)
    if not isinstance(task, Mapping):
        return []
    train_raw = task.get("train")
    test_raw = task.get("test")
    if not isinstance(train_raw, Sequence) or isinstance(train_raw, (str, bytes)) or not train_raw:
        return []
    if not isinstance(test_raw, Sequence) or isinstance(test_raw, (str, bytes)) or not test_raw:
        return []
    try:
        train_inputs = [_grid(example["input"], bounds) for example in train_raw]
        train_outputs = [_grid(example["output"], bounds) for example in train_raw]
        test_inputs = [_grid(example["input"], bounds) for example in test_raw]
    except (KeyError, TypeError, Inapplicable):
        return []
    if any(source.shape != target.shape for source, target in zip(train_inputs, train_outputs)):
        return []

    maps_by_input = [_cell_feature_maps(array) for array in train_inputs]
    feature_names = sorted(set.intersection(*(set(maps) for maps in maps_by_input)))
    priority = [
        "color", "is_background", "component_c4", "component_c8",
        "orthogonal_neighbors", "diagonal_neighbors", "all_neighbors",
        "orthogonal_neighbors_same_count", "diagonal_neighbors_same_count",
        "row_nonbackground_count", "column_nonbackground_count",
        "row_same_color_count", "column_same_color_count",
        "horizontal_ray_pair", "vertical_ray_pair", "diagonal_ray_pairs", "ray_signature",
        "border_role", "diagonal_role", "foreground_bbox_role", "nearest_foreground",
        "symmetry_colors", "square_dihedral_colors",
        "support_patch_r1", "histogram_r1", "patch_r1",
        "support_patch_r2", "histogram_r2", "patch_r2",
        "row_support_signature", "column_support_signature",
        "row_signature", "column_signature", "border_distance", "normalized_position",
    ]
    feature_names = [name for name in priority if name in feature_names][: bounds.max_features]
    rows_by_grid: list[dict[str, list[Any]]] = []
    for maps, source in zip(maps_by_input, train_inputs):
        rows_by_grid.append(
            {
                name: [_hashable(maps[name][row, column]) for row in range(source.shape[0]) for column in range(source.shape[1])]
                for name in feature_names
            }
        )
    labels = [int(value) for target in train_outputs for value in target.flat]
    feature_sets = _candidate_feature_sets(feature_names, rows_by_grid, labels, bounds)
    if not feature_sets:
        return []

    output_counts = Counter(labels)
    output_mode = min(output_counts, key=lambda color: (-output_counts[color], color))
    proposals: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    for names in feature_sets:
        keys = list(
            itertools.chain.from_iterable(
                [tuple(grid[name][index] for name in names) for index in range(len(next(iter(grid.values()))))]
                for grid in rows_by_grid
            )
        )
        table = _deterministic_table(keys, labels)
        if table is None or len(table) > bounds.max_table_entries:
            continue
        for fallback in ("identity", "background", "output_mode"):
            train_predictions = [
                _predict(source, names, table, fallback, output_mode)[0]
                for source in train_inputs
            ]
            if not all(np.array_equal(predicted, expected) for predicted, expected in zip(train_predictions, train_outputs)):
                continue
            test_results = [_predict(source, names, table, fallback, output_mode) for source in test_inputs]
            test_predictions = [result for result, _ in test_results]
            unseen = sum(count for _, count in test_results)
            cells = sum(source.size for source in test_inputs)
            loo = _loo_exact(names, fallback, train_inputs, train_outputs, output_mode)
            program = {
                "operator": "categorical_cell_feature_table",
                "features": list(names),
                "fallback": fallback,
                "output_mode": int(output_mode),
                "table": _table_record(table),
            }
            candidate = {
                "family": "feature_induction",
                "program": program,
                "train_outputs": [_plain(array) for array in train_predictions],
                "test_outputs": [_plain(array) for array in test_predictions],
                "complexity": int(4 * len(names) + len(table)),
                "evidence": {
                    "all_demonstrations_exact": True,
                    "demonstration_permutation_invariant": True,
                    "leave_one_demonstration_out_exact": loo,
                    "test_key_coverage": float((cells - unseen) / cells) if cells else 0.0,
                    "unseen_test_keys": int(unseen),
                    "table_entries": len(table),
                    "feature_depth": len(names),
                },
            }
            rank = (
                0 if loo else 1,
                unseen,
                len(names),
                len(table),
                fallback,
                tuple(names),
            )
            proposals.append((rank, candidate))

    proposals.sort(key=lambda item: item[0])
    seen_behaviors: set[str] = set()
    output: list[dict[str, Any]] = []
    for _, candidate in proposals:
        behavior = _behavior_hash([np.asarray(grid, dtype=np.int16) for grid in candidate["test_outputs"]])
        if behavior in seen_behaviors:
            continue
        seen_behaviors.add(behavior)
        candidate["evidence"]["behavior_hash"] = behavior
        output.append(candidate)
        if len(output) >= bounds.max_programs:
            break
    return output


__all__ = ["Limits", "compile_task"]
