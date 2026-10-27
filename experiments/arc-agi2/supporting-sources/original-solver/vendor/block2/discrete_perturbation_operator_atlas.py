#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Discrete Perturbation Operator Atlas for the Komorebi ARC-AGI2 solver.

This module is an additive, source-blind challenger.  Every emitted operator
packet is induced only from a task's training demonstrations.  The held-out
input is used solely for execution after the operator has passed the exact
training gate.  No task identifiers, expected test grids, or fixed raster
coordinates occur in the runtime grammar.

The first block transfers the perturbation-packet idea from continuous image
geometry to finite categorical transformations.  Each compiler represents a
small typed neighbourhood around an interpretable mechanism, and each family
abstains unless one deterministic program reconstructs every demonstration.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple

import numpy as np

Array = np.ndarray
Grid = List[List[int]]
SCHEMA = "komorebi.arc.discrete-perturbation-operator-packet.v1"
ATLAS_SCHEMA = "komorebi.arc.discrete-perturbation-operator-atlas.v1"
TOOL_VERSION = "0.1.0"
MAX_SIDE = 30


class PerturbationAtlasError(ValueError):
    """Invalid source, packet, or bounded execution state."""


class PerturbationAtlasAbstention(PerturbationAtlasError):
    """No unique protected interpretation exists for the source."""


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def sanitize_grid(value: object) -> Array:
    try:
        array = np.asarray(value)
    except (TypeError, ValueError) as error:
        raise PerturbationAtlasError("ARC grid is not rectangular") from error
    if array.ndim != 2 or array.size == 0:
        raise PerturbationAtlasError("ARC grids must be nonempty two-dimensional arrays")
    if array.shape[0] > MAX_SIDE or array.shape[1] > MAX_SIDE:
        raise PerturbationAtlasError("ARC grid exceeds the 30x30 finite contract")
    if not np.issubdtype(array.dtype, np.integer):
        if not np.all(np.isfinite(array)) or not np.all(array == np.rint(array)):
            raise PerturbationAtlasError("ARC grid contains nonintegral values")
    array = np.asarray(array, dtype=np.int16)
    if np.any(array < 0) or np.any(array > 9):
        raise PerturbationAtlasError("ARC colors must lie in [0, 9]")
    return array.copy()


def exact(left: object, right: object) -> bool:
    a = sanitize_grid(left)
    b = sanitize_grid(right)
    return a.shape == b.shape and bool(np.array_equal(a, b))


def grid_hash(grid: object) -> str:
    array = sanitize_grid(grid)
    record = {"shape": list(array.shape), "grid": array.tolist()}
    return hashlib.sha256(canonical_json(record).encode("ascii")).hexdigest()


def _unique_mode(values: Iterable[int], *, role: str) -> int:
    counts = Counter(int(value) for value in values)
    if not counts:
        raise PerturbationAtlasAbstention(f"{role} has no values")
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    if len(winners) != 1:
        raise PerturbationAtlasAbstention(f"{role} mode is ambiguous")
    return winners[0]


def infer_background(grid: object) -> int:
    array = sanitize_grid(grid)
    return _unique_mode((int(value) for value in array.ravel()), role="background")


def infer_border_background(grid: object) -> int:
    """Infer an exterior canvas color from a unique finite-raster border mode."""
    array = sanitize_grid(grid)
    border = np.concatenate(
        (array[0, :], array[-1, :], array[1:-1, 0], array[1:-1, -1])
    )
    return _unique_mode((int(value) for value in border), role="border background")


def grid_to_list(grid: object) -> Grid:
    return [[int(value) for value in row] for row in sanitize_grid(grid)]


@dataclass(frozen=True)
class OperatorPacket:
    """One exact-training-gated discrete operator packet."""

    family: str
    name: str
    complexity: int
    train_grids: Tuple[Array, ...]
    test_grids: Tuple[Array, ...]
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise PerturbationAtlasError("unsupported operator packet schema")
        if not self.family or not self.name:
            raise PerturbationAtlasError("operator packet family and name are required")
        if type(self.complexity) is not int or self.complexity <= 0:
            raise PerturbationAtlasError("operator packet complexity must be positive")
        object.__setattr__(self, "train_grids", tuple(sanitize_grid(g) for g in self.train_grids))
        object.__setattr__(self, "test_grids", tuple(sanitize_grid(g) for g in self.test_grids))
        canonical_json(dict(self.metadata))

    @property
    def semantic_record(self) -> Dict[str, object]:
        return {
            "schema": self.schema,
            "family": self.family,
            "name": self.name,
            "complexity": self.complexity,
            "metadata": dict(self.metadata),
        }

    @property
    def program_hash(self) -> str:
        return hashlib.sha256(canonical_json(self.semantic_record).encode("ascii")).hexdigest()

    @property
    def behavior_hash(self) -> str:
        record = {
            "train": [grid_hash(grid) for grid in self.train_grids],
            "test": [grid_hash(grid) for grid in self.test_grids],
        }
        return hashlib.sha256(canonical_json(record).encode("ascii")).hexdigest()

    def to_record(self, *, include_grids: bool = False) -> Dict[str, object]:
        record = {
            **self.semantic_record,
            "program_hash": self.program_hash,
            "behavior_hash": self.behavior_hash,
            "train_count": len(self.train_grids),
            "test_count": len(self.test_grids),
        }
        if include_grids:
            record["train_grids"] = [grid_to_list(grid) for grid in self.train_grids]
            record["test_grids"] = [grid_to_list(grid) for grid in self.test_grids]
        return record


@dataclass(frozen=True)
class AtlasCompilation:
    packets: Tuple[OperatorPacket, ...]
    abstentions: Tuple[Mapping[str, object], ...]

    def to_record(self, *, include_grids: bool = False) -> Dict[str, object]:
        return {
            "schema": ATLAS_SCHEMA,
            "tool_version": TOOL_VERSION,
            "packet_count": len(self.packets),
            "families": dict(Counter(packet.family for packet in self.packets)),
            "packets": [packet.to_record(include_grids=include_grids) for packet in self.packets],
            "abstentions": [dict(record) for record in self.abstentions],
        }


def _exact_packet(
    *,
    family: str,
    name: str,
    complexity: int,
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    apply: Callable[[Array], Array],
    metadata: Optional[Mapping[str, object]] = None,
) -> Optional[OperatorPacket]:
    if not train or not any(not exact(source, target) for source, target in train):
        return None
    try:
        train_predictions = tuple(sanitize_grid(apply(source)) for source, _ in train)
        if not all(exact(prediction, target) for prediction, (_, target) in zip(train_predictions, train)):
            return None
        test_predictions = tuple(sanitize_grid(apply(source)) for source in tests)
    except (PerturbationAtlasError, ValueError, IndexError, KeyError, TypeError, OverflowError):
        return None
    if not test_predictions:
        return None
    return OperatorPacket(
        family=family,
        name=name,
        complexity=int(complexity),
        train_grids=train_predictions,
        test_grids=test_predictions,
        metadata={
            "exact_demonstration_contract": True,
            "source_blind_test_execution": True,
            "task_id_free": True,
            "answer_grid_free": True,
            **dict(metadata or {}),
        },
    )


def _nonseparator_intervals(flags: Sequence[bool]) -> List[Tuple[int, int]]:
    intervals: List[Tuple[int, int]] = []
    start: Optional[int] = None
    for index, separator in enumerate(flags):
        if separator:
            if start is not None:
                intervals.append((start, index))
                start = None
        elif start is None:
            start = index
    if start is not None:
        intervals.append((start, len(flags)))
    return intervals


def _split_uniform_panels(grid: Array) -> List[Array]:
    array = sanitize_grid(grid)
    background = infer_background(array)
    row_intervals = _nonseparator_intervals([bool(np.all(row == background)) for row in array])
    col_intervals = _nonseparator_intervals([bool(np.all(array[:, col] == background)) for col in range(array.shape[1])])
    if len(row_intervals) * len(col_intervals) < 3:
        raise PerturbationAtlasAbstention("fewer than three separator-defined panels")
    panels = [
        array[r0:r1, c0:c1].copy()
        for r0, r1 in row_intervals
        for c0, c1 in col_intervals
    ]
    if not panels or len({panel.shape for panel in panels}) != 1:
        raise PerturbationAtlasAbstention("separator-defined panels do not share one shape")
    return panels


def compile_unique_panel_extraction(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    def apply(grid: Array) -> Array:
        panels = _split_uniform_panels(grid)
        groups: Dict[str, List[Array]] = defaultdict(list)
        for panel in panels:
            groups[grid_hash(panel)].append(panel)
        unique = [values[0] for values in groups.values() if len(values) == 1]
        repeated = [len(values) for values in groups.values() if len(values) >= 2]
        if len(unique) != 1 or not repeated:
            raise PerturbationAtlasAbstention("panel multiplicities do not identify one unique panel")
        return unique[0]

    packet = _exact_packet(
        family="discrete_unique_panel_extraction",
        name="extract_unique_separator_panel",
        complexity=10,
        train=train,
        tests=tests,
        apply=apply,
        metadata={"perturbation_axes": ["panel_multiplicity", "separator_partition"]},
    )
    return [packet] if packet is not None else []


def _components(mask: Array, *, connectivity: int = 4) -> List[List[Tuple[int, int]]]:
    mask = np.asarray(mask, dtype=bool)
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if connectivity == 8:
        directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    output: List[List[Tuple[int, int]]] = []
    for row in range(height):
        for column in range(width):
            if not mask[row, column] or seen[row, column]:
                continue
            queue = deque([(row, column)])
            seen[row, column] = True
            component: List[Tuple[int, int]] = []
            while queue:
                r, c = queue.popleft()
                component.append((r, c))
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < height and 0 <= nc < width and mask[nr, nc] and not seen[nr, nc]:
                        seen[nr, nc] = True
                        queue.append((nr, nc))
            output.append(component)
    return output


def _colored_components(grid: Array, background: int, *, connectivity: int = 4) -> List[Dict[str, object]]:
    array = sanitize_grid(grid)
    result: List[Dict[str, object]] = []
    for color in sorted(int(value) for value in np.unique(array) if int(value) != background):
        for component in _components(array == color, connectivity=connectivity):
            rows = [cell[0] for cell in component]
            cols = [cell[1] for cell in component]
            result.append(
                {
                    "color": color,
                    "cells": tuple(sorted(component)),
                    "size": len(component),
                    "bbox": (min(rows), min(cols), max(rows) + 1, max(cols) + 1),
                }
            )
    return result


def compile_consumed_marker_recolor(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    for connectivity in (4, 8):
        role_records: List[Tuple[int, int]] = []
        valid = True
        for source, target in train:
            source = sanitize_grid(source)
            target = sanitize_grid(target)
            if source.shape != target.shape:
                valid = False
                break
            background = infer_background(source)
            components = _colored_components(source, background, connectivity=connectivity)
            singletons = [item for item in components if int(item["size"]) == 1]
            larger = [item for item in components if int(item["size"]) > 1]
            if len(singletons) != 1 or len(larger) != 1:
                valid = False
                break
            marker, body = singletons[0], larger[0]
            marker_color = int(marker["color"])
            expected = np.full_like(source, background)
            for row, column in body["cells"]:
                expected[row, column] = marker_color
            if not exact(expected, target):
                valid = False
                break
            role_records.append((int(body["color"]), marker_color))
        if not valid:
            continue

        def apply(grid: Array, conn: int = connectivity) -> Array:
            source = sanitize_grid(grid)
            background = infer_background(source)
            components = _colored_components(source, background, connectivity=conn)
            singletons = [item for item in components if int(item["size"]) == 1]
            larger = [item for item in components if int(item["size"]) > 1]
            if len(singletons) != 1 or len(larger) != 1:
                raise PerturbationAtlasAbstention("source lacks one body and one singleton marker")
            marker, body = singletons[0], larger[0]
            output = np.full_like(source, background)
            for row, column in body["cells"]:
                output[row, column] = int(marker["color"])
            return output

        packet = _exact_packet(
            family="discrete_consumed_marker_recolor",
            name=f"recolor_body_from_consumed_singleton_c{connectivity}",
            complexity=12,
            train=train,
            tests=tests,
            apply=apply,
            metadata={
                "connectivity": connectivity,
                "perturbation_axes": ["marker_consumption", "role_rebinding"],
            },
        )
        if packet is not None:
            return [packet]
    return []


def compile_foreground_translation_recolor(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    packets: List[OperatorPacket] = []
    target_roles: List[Tuple[int, int]] = []
    for source, target in train:
        source = sanitize_grid(source)
        target = sanitize_grid(target)
        if source.shape != target.shape:
            return []
        source_bg = infer_background(source)
        target_bg = infer_background(target)
        source_colors = [int(v) for v in np.unique(source) if int(v) != source_bg]
        target_colors = [int(v) for v in np.unique(target) if int(v) != target_bg]
        if len(source_colors) != 1 or len(target_colors) != 1:
            return []
        target_roles.append((target_bg, target_colors[0]))
    if len(set(target_roles)) != 1:
        return []
    target_background, paint_color = target_roles[0]

    for dr in range(-3, 4):
        for dc in range(-3, 4):
            if (dr, dc) == (0, 0):
                continue

            def apply(grid: Array, row_shift: int = dr, col_shift: int = dc) -> Array:
                source = sanitize_grid(grid)
                source_bg = infer_background(source)
                mask = source != source_bg
                output = np.full(source.shape, target_background, dtype=np.int16)
                for row, column in zip(*np.nonzero(mask)):
                    nr, nc = int(row) + row_shift, int(column) + col_shift
                    if 0 <= nr < source.shape[0] and 0 <= nc < source.shape[1]:
                        output[nr, nc] = paint_color
                return output

            packet = _exact_packet(
                family="discrete_foreground_translation_recolor",
                name=f"translate_foreground_{dr}_{dc}_recolor",
                complexity=8 + abs(dr) + abs(dc),
                train=train,
                tests=tests,
                apply=apply,
                metadata={
                    "row_shift": dr,
                    "column_shift": dc,
                    "paint_color": paint_color,
                    "output_background": target_background,
                    "perturbation_axes": ["translation", "categorical_recolor", "source_erasure"],
                },
            )
            if packet is not None:
                packets.append(packet)
    return packets


def _cast_rays(grid: Array, direction: Tuple[int, int], *, stop_before_signal: bool) -> Array:
    source = sanitize_grid(grid)
    background = infer_background(source)
    output = source.copy()
    dr, dc = direction
    seeds = [(int(r), int(c), int(source[r, c])) for r, c in zip(*np.nonzero(source != background))]
    seeds.sort(key=lambda item: item[0] * dr + item[1] * dc)
    for row, column, color in seeds:
        nr, nc = row + dr, column + dc
        while 0 <= nr < source.shape[0] and 0 <= nc < source.shape[1]:
            if source[nr, nc] != background:
                if stop_before_signal:
                    break
                nr += dr
                nc += dc
                continue
            output[nr, nc] = color
            nr += dr
            nc += dc
    output[source != background] = source[source != background]
    return output


def compile_directional_ray_extension(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    directions = {
        "north": (-1, 0),
        "south": (1, 0),
        "west": (0, -1),
        "east": (0, 1),
        "north_west": (-1, -1),
        "north_east": (-1, 1),
        "south_west": (1, -1),
        "south_east": (1, 1),
    }
    packets: List[OperatorPacket] = []
    for direction_name, vector in directions.items():
        for stop_before_signal in (True, False):
            packet = _exact_packet(
                family="discrete_directional_ray_extension",
                name=f"extend_{direction_name}_{'until_signal' if stop_before_signal else 'through_signal'}",
                complexity=8 if stop_before_signal else 9,
                train=train,
                tests=tests,
                apply=lambda grid, d=vector, stop=stop_before_signal: _cast_rays(grid, d, stop_before_signal=stop),
                metadata={
                    "direction": direction_name,
                    "stop_before_signal": stop_before_signal,
                    "perturbation_axes": ["ray_direction", "ray_stopping_rule"],
                },
            )
            if packet is not None:
                packets.append(packet)
    return packets


def _line_views(grid: Array, axis: str) -> List[Array]:
    source = sanitize_grid(grid)
    if axis == "row":
        return [source[row, :].copy() for row in range(source.shape[0])]
    if axis == "column":
        return [source[:, column].copy() for column in range(source.shape[1])]
    raise PerturbationAtlasError("unknown line axis")


def _assemble_lines(lines: Sequence[Array], axis: str) -> Array:
    if not lines:
        raise PerturbationAtlasAbstention("no lines to assemble")
    if axis == "row":
        return np.vstack(lines).astype(np.int16)
    if axis == "column":
        return np.column_stack(lines).astype(np.int16)
    raise PerturbationAtlasError("unknown line axis")


def compile_uniform_axis_predicate_render(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    predicates: Dict[str, Tuple[bool, Callable[[Array, Optional[int]], bool]]] = {
        "all_equal": (False, lambda line, bg: len(set(int(v) for v in line)) == 1),
        "all_nonbackground_equal": (
            True,
            lambda line, bg: bg is not None
            and bool(np.any(line != bg))
            and len(set(int(v) for v in line if int(v) != bg)) == 1,
        ),
        "palindrome": (False, lambda line, bg: bool(np.array_equal(line, line[::-1]))),
        "foreground_count_even": (
            True,
            lambda line, bg: bg is not None
            and int(np.count_nonzero(line != bg)) > 0
            and int(np.count_nonzero(line != bg)) % 2 == 0,
        ),
    }
    packets: List[OperatorPacket] = []
    for axis in ("row", "column"):
        for predicate_name, (needs_background, predicate) in predicates.items():
            mapping: Dict[bool, int] = {}
            valid = True
            for source, target in train:
                source = sanitize_grid(source)
                target = sanitize_grid(target)
                if source.shape != target.shape:
                    valid = False
                    break
                try:
                    background = infer_background(source) if needs_background else None
                except PerturbationAtlasError:
                    valid = False
                    break
                source_lines = _line_views(source, axis)
                target_lines = _line_views(target, axis)
                for source_line, target_line in zip(source_lines, target_lines):
                    if len(set(int(value) for value in target_line)) != 1:
                        valid = False
                        break
                    key = bool(predicate(source_line, background))
                    value = int(target_line[0])
                    previous = mapping.get(key)
                    if previous is not None and previous != value:
                        valid = False
                        break
                    mapping[key] = value
                if not valid:
                    break
            if not valid or set(mapping) != {False, True} or mapping[False] == mapping[True]:
                continue

            def apply(
                grid: Array,
                line_axis: str = axis,
                pred: Callable[[Array, Optional[int]], bool] = predicate,
                requires_background: bool = needs_background,
                value_map: Dict[bool, int] = dict(mapping),
            ) -> Array:
                source = sanitize_grid(grid)
                background = infer_background(source) if requires_background else None
                lines = [
                    np.full(line.shape, value_map[bool(pred(line, background))], dtype=np.int16)
                    for line in _line_views(source, line_axis)
                ]
                return _assemble_lines(lines, line_axis)

            packet = _exact_packet(
                family="discrete_uniform_axis_predicate_render",
                name=f"render_{axis}_{predicate_name}",
                complexity=9,
                train=train,
                tests=tests,
                apply=apply,
                metadata={
                    "axis": axis,
                    "predicate": predicate_name,
                    "background_required": needs_background,
                    "false_color": mapping[False],
                    "true_color": mapping[True],
                    "perturbation_axes": ["axis", "line_predicate", "categorical_render"],
                },
            )
            if packet is not None:
                packets.append(packet)
    return packets

def _qualifying_pair_lines(grid: Array, axis: str) -> List[Tuple[int, Tuple[int, int], Tuple[int, int]]]:
    source = sanitize_grid(grid)
    background = infer_background(source)
    output: List[Tuple[int, Tuple[int, int], Tuple[int, int]]] = []
    for index, line in enumerate(_line_views(source, axis)):
        positions = [position for position, value in enumerate(line) if int(value) != background]
        if len(positions) != 2 or positions[1] != positions[0] + 1:
            continue
        values = (int(line[positions[0]]), int(line[positions[1]]))
        if values[0] == values[1]:
            continue
        output.append((index, (positions[0], positions[1]), values))
    return output


def _ordered_pair_phase_apply(grid: Array, axis: str, shift: int, reference: str) -> Array:
    source = sanitize_grid(grid)
    background = infer_background(source)
    lines = _line_views(source, axis)
    qualifying = _qualifying_pair_lines(source, axis)
    if len(qualifying) < 2:
        raise PerturbationAtlasAbstention("fewer than two ordered-pair lines")
    anchor = qualifying[0] if reference == "first" else qualifying[-1]
    reference_values = anchor[2]
    reversed_values = (reference_values[1], reference_values[0])
    for index, positions, values in qualifying:
        if values != reversed_values:
            continue
        line = lines[index].copy()
        target_positions = (positions[0] + shift, positions[1] + shift)
        if target_positions[0] < 0 or target_positions[1] >= line.size:
            raise PerturbationAtlasAbstention("ordered-pair shift leaves the raster")
        line[positions[0]] = background
        line[positions[1]] = background
        line[target_positions[0]] = values[0]
        line[target_positions[1]] = values[1]
        lines[index] = line
    return _assemble_lines(lines, axis)


def compile_ordered_pair_phase_transport(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    packets: List[OperatorPacket] = []
    for axis in ("row", "column"):
        for reference in ("first", "last"):
            for shift in (-1, 1):
                packet = _exact_packet(
                    family="discrete_ordered_pair_phase_transport",
                    name=f"{axis}_{reference}_pair_reverse_shift_{shift}",
                    complexity=11,
                    train=train,
                    tests=tests,
                    apply=lambda grid, a=axis, s=shift, r=reference: _ordered_pair_phase_apply(grid, a, s, r),
                    metadata={
                        "axis": axis,
                        "reference": reference,
                        "shift": shift,
                        "perturbation_axes": ["phase_order", "translation", "line_orientation"],
                    },
                )
                if packet is not None:
                    packets.append(packet)
    return packets


def _extract_embedded_components(grid: Array) -> Tuple[Array, int, List[Dict[str, object]]]:
    source = sanitize_grid(grid)
    outer_background = infer_border_background(source)
    rows, cols = np.nonzero(source != outer_background)
    if rows.size == 0:
        raise PerturbationAtlasAbstention("no nonbackground canvas")
    r0, r1 = int(rows.min()), int(rows.max()) + 1
    c0, c1 = int(cols.min()), int(cols.max()) + 1
    crop = source[r0:r1, c0:c1].copy()
    if np.any(crop == outer_background):
        raise PerturbationAtlasAbstention("nonbackground support is not a solid canvas rectangle")
    counts = Counter(int(value) for value in crop.ravel())
    canvas = min(counts, key=lambda color: (-counts[color], color))
    components: List[Dict[str, object]] = []
    for color in sorted(int(value) for value in np.unique(crop) if int(value) != canvas):
        for cells in _components(crop == color, connectivity=4):
            rows2 = [cell[0] for cell in cells]
            cols2 = [cell[1] for cell in cells]
            bbox = (min(rows2), min(cols2), max(rows2) + 1, max(cols2) + 1)
            block = crop[bbox[0]:bbox[2], bbox[1]:bbox[3]]
            if block.size != len(cells) or not np.all(block == color):
                raise PerturbationAtlasAbstention("embedded component is not a solid rectangle")
            components.append({"color": color, "bbox": bbox, "size": len(cells)})
    if not components:
        raise PerturbationAtlasAbstention("no embedded patch components")
    if len({(item["bbox"][2] - item["bbox"][0], item["bbox"][3] - item["bbox"][1]) for item in components}) != 1:
        raise PerturbationAtlasAbstention("embedded patch shapes disagree")
    return crop, canvas, components


def compile_embedded_patch_layout_serialization(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    output_shapes = {sanitize_grid(target).shape for _, target in train}
    if len(output_shapes) != 1:
        return []
    output_shape = next(iter(output_shapes))
    if output_shape[0] < 2 or output_shape[1] < 2 or output_shape[0] * output_shape[1] > 25:
        return []
    # The compact layout preserves the exterior background role.  Infer that
    # role from the source border rather than from output color frequency: in
    # very small outputs every color can occur once, making a numeric tie-break
    # non-equivariant under palette permutation.
    backgrounds = {infer_border_background(source) for source, _ in train}
    if len(backgrounds) != 1:
        return []
    output_background = next(iter(backgrounds))
    if any(output_background not in set(int(value) for value in np.unique(target)) for _, target in train):
        return []

    def apply(grid: Array) -> Array:
        crop, _, components = _extract_embedded_components(grid)
        result = np.full(output_shape, output_background, dtype=np.int16)
        for item in components:
            r0, c0, r1, c1 = item["bbox"]
            center_row = 0.5 * (r0 + r1 - 1)
            center_col = 0.5 * (c0 + c1 - 1)
            slot_row = min(output_shape[0] - 1, int(center_row * output_shape[0] / crop.shape[0]))
            slot_col = min(output_shape[1] - 1, int(center_col * output_shape[1] / crop.shape[1]))
            if result[slot_row, slot_col] != output_background:
                raise PerturbationAtlasAbstention("multiple embedded patches map to one layout slot")
            result[slot_row, slot_col] = int(item["color"])
        return result

    packet = _exact_packet(
        family="discrete_embedded_patch_layout_serialization",
        name=f"serialize_solid_patches_{output_shape[0]}x{output_shape[1]}",
        complexity=13 + output_shape[0] * output_shape[1],
        train=train,
        tests=tests,
        apply=apply,
        metadata={
            "output_shape": list(output_shape),
            "output_background": output_background,
            "perturbation_axes": ["canvas_projection", "component_layout", "compact_serialization"],
        },
    )
    return [packet] if packet is not None else []


def compile_axis_cross_intersection(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    intersection_colors: List[int] = []
    for source, target in train:
        source = sanitize_grid(source)
        target = sanitize_grid(target)
        if source.shape != target.shape:
            return []
        background = infer_background(source)
        components = _colored_components(source, background, connectivity=4)
        if len(components) != 2 or any(int(item["size"]) != 1 for item in components):
            return []
        cells = [item["cells"][0] for item in components]
        if cells[0][0] == cells[1][0] or cells[0][1] == cells[1][1]:
            return []
        crossings = [(cells[0][0], cells[1][1]), (cells[1][0], cells[0][1])]
        colors = {int(target[row, column]) for row, column in crossings}
        if len(colors) != 1:
            return []
        intersection_colors.append(next(iter(colors)))
    if len(set(intersection_colors)) != 1:
        return []
    intersection_color = intersection_colors[0]

    def apply(grid: Array) -> Array:
        source = sanitize_grid(grid)
        background = infer_background(source)
        components = _colored_components(source, background, connectivity=4)
        if len(components) != 2 or any(int(item["size"]) != 1 for item in components):
            raise PerturbationAtlasAbstention("cross rule requires two singleton seeds")
        first, second = components
        (r1, c1), (r2, c2) = first["cells"][0], second["cells"][0]
        if r1 == r2 or c1 == c2:
            raise PerturbationAtlasAbstention("cross seeds must occupy different rows and columns")
        output = np.full_like(source, background)
        output[r1, :] = int(first["color"])
        output[:, c1] = int(first["color"])
        output[r2, :] = int(second["color"])
        output[:, c2] = int(second["color"])
        output[r1, c2] = intersection_color
        output[r2, c1] = intersection_color
        output[r1, c1] = int(first["color"])
        output[r2, c2] = int(second["color"])
        return output

    packet = _exact_packet(
        family="discrete_axis_cross_intersection",
        name="project_two_singletons_to_orthogonal_crosses",
        complexity=12,
        train=train,
        tests=tests,
        apply=apply,
        metadata={
            "intersection_color": intersection_color,
            "perturbation_axes": ["axis_projection", "pairwise_intersection", "nonlinear_two_object_interaction"],
        },
    )
    return [packet] if packet is not None else []


def compile_template_axis_broadcast(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    packets: List[OperatorPacket] = []
    paint_candidates = sorted({int(value) for _, target in train for value in np.unique(target)})
    for orientation in ("row_template", "column_template"):
        for paint_color in paint_candidates:
            def apply(grid: Array, orient: str = orientation, paint: int = paint_color) -> Array:
                source = sanitize_grid(grid)
                background = infer_background(source)
                colors = [int(value) for value in np.unique(source) if int(value) != background]
                if len(colors) != 1:
                    raise PerturbationAtlasAbstention("broadcast rule requires one input signal color")
                signal = colors[0]
                row_counts = np.count_nonzero(source == signal, axis=1)
                col_counts = np.count_nonzero(source == signal, axis=0)
                output = source.copy()
                if orient == "row_template":
                    template_row = int(np.argmax(row_counts))
                    trigger_col = int(np.argmax(col_counts))
                    if row_counts[template_row] < 2 or col_counts[trigger_col] < 2:
                        raise PerturbationAtlasAbstention("no row template and orthogonal trigger column")
                    template_positions = [int(c) for c in np.nonzero(source[template_row] == signal)[0]]
                    trigger_rows = [int(r) for r in np.nonzero(source[:, trigger_col] == signal)[0] if int(r) != template_row]
                    if not trigger_rows:
                        raise PerturbationAtlasAbstention("no trigger rows")
                    for row in trigger_rows:
                        for column in template_positions:
                            if output[row, column] == background:
                                output[row, column] = paint
                else:
                    template_col = int(np.argmax(col_counts))
                    trigger_row = int(np.argmax(row_counts))
                    if col_counts[template_col] < 2 or row_counts[trigger_row] < 2:
                        raise PerturbationAtlasAbstention("no column template and orthogonal trigger row")
                    template_positions = [int(r) for r in np.nonzero(source[:, template_col] == signal)[0]]
                    trigger_cols = [int(c) for c in np.nonzero(source[trigger_row] == signal)[0] if int(c) != template_col]
                    if not trigger_cols:
                        raise PerturbationAtlasAbstention("no trigger columns")
                    for column in trigger_cols:
                        for row in template_positions:
                            if output[row, column] == background:
                                output[row, column] = paint
                return output

            packet = _exact_packet(
                family="discrete_template_axis_broadcast",
                name=f"{orientation}_paint_{paint_color}",
                complexity=12,
                train=train,
                tests=tests,
                apply=apply,
                metadata={
                    "orientation": orientation,
                    "paint_color": paint_color,
                    "perturbation_axes": ["template_selection", "orthogonal_broadcast", "role_color"],
                },
            )
            if packet is not None:
                packets.append(packet)
    return packets



def _neighbor_offsets(connectivity: int) -> Tuple[Tuple[int, int], ...]:
    if connectivity == 4:
        return ((-1, 0), (1, 0), (0, -1), (0, 1))
    if connectivity == 8:
        return (
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )
    raise PerturbationAtlasError("connectivity must be 4 or 8")


def _adjacent_pair_recode_apply(
    grid: Array,
    source_color: int,
    partner_color: int,
    paint_color: int,
    connectivity: int,
) -> Array:
    source = sanitize_grid(grid)
    background = infer_background(source)
    if len({background, source_color, partner_color, paint_color}) < 4:
        raise PerturbationAtlasAbstention("adjacent-pair roles must be distinct")
    source_mask = source == source_color
    partner_mask = source == partner_color
    selected_source = np.zeros_like(source_mask)
    selected_partner = np.zeros_like(partner_mask)
    offsets = _neighbor_offsets(connectivity)
    height, width = source.shape
    for row, column in zip(*np.nonzero(source_mask)):
        for dr, dc in offsets:
            nr, nc = int(row) + dr, int(column) + dc
            if 0 <= nr < height and 0 <= nc < width and partner_mask[nr, nc]:
                selected_source[row, column] = True
                selected_partner[nr, nc] = True
    if not np.any(selected_source) or not np.any(selected_partner):
        raise PerturbationAtlasAbstention("no qualifying adjacent pair")
    output = source.copy()
    output[selected_source] = paint_color
    output[selected_partner] = background
    return output


def compile_adjacent_pair_recode(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    source_to_paint: set[Tuple[int, int]] = set()
    erased_colors: set[int] = set()
    for source, target in train:
        source = sanitize_grid(source)
        target = sanitize_grid(target)
        if source.shape != target.shape:
            return []
        try:
            background = infer_background(source)
        except PerturbationAtlasError:
            return []
        changed = source != target
        for before, after in zip(source[changed], target[changed]):
            left, right = int(before), int(after)
            if right == background and left != background:
                erased_colors.add(left)
            elif left != right and left != background and right != background:
                source_to_paint.add((left, right))
    packets: List[OperatorPacket] = []
    for source_color, paint_color in sorted(source_to_paint):
        for partner_color in sorted(erased_colors):
            if len({source_color, partner_color, paint_color}) < 3:
                continue
            for connectivity in (4, 8):
                active_pairs = 0
                inactive_sources = 0
                inactive_partners = 0
                offsets = _neighbor_offsets(connectivity)
                valid_witness = True
                for source, _ in train:
                    source = sanitize_grid(source)
                    height, width = source.shape
                    source_positions = [tuple(map(int, cell)) for cell in np.argwhere(source == source_color)]
                    partner_positions = [tuple(map(int, cell)) for cell in np.argwhere(source == partner_color)]
                    for row, column in source_positions:
                        adjacent = any(
                            0 <= row + dr < height
                            and 0 <= column + dc < width
                            and int(source[row + dr, column + dc]) == partner_color
                            for dr, dc in offsets
                        )
                        active_pairs += int(adjacent)
                        inactive_sources += int(not adjacent)
                    for row, column in partner_positions:
                        adjacent = any(
                            0 <= row + dr < height
                            and 0 <= column + dc < width
                            and int(source[row + dr, column + dc]) == source_color
                            for dr, dc in offsets
                        )
                        inactive_partners += int(not adjacent)
                if active_pairs < 2 or inactive_sources < 1 or inactive_partners < 1:
                    valid_witness = False
                if not valid_witness:
                    continue
                packet = _exact_packet(
                    family="discrete_adjacent_pair_recode",
                    name=(
                        f"adjacent_{source_color}_{partner_color}_to_"
                        f"{paint_color}_background_c{connectivity}"
                    ),
                    complexity=13 if connectivity == 4 else 14,
                    train=train,
                    tests=tests,
                    apply=lambda grid, a=source_color, b=partner_color, c=paint_color, conn=connectivity: _adjacent_pair_recode_apply(
                        grid, a, b, c, conn
                    ),
                    metadata={
                        "source_color": source_color,
                        "partner_color": partner_color,
                        "paint_color": paint_color,
                        "connectivity": connectivity,
                        "active_pair_witnesses": active_pairs,
                        "inactive_source_witnesses": inactive_sources,
                        "inactive_partner_witnesses": inactive_partners,
                        "perturbation_axes": [
                            "conditional_adjacency",
                            "partner_consumption",
                            "categorical_recode",
                        ],
                    },
                )
                if packet is not None:
                    packets.append(packet)
    # When both 4- and 8-connectivity explain every demonstration, retain the
    # simpler 4-connected interpretation.  This is an explicit structural
    # prior, not a test-output tie-break, and prevents an ambiguous family
    # emission on sparse witness sets.
    if packets:
        minimum = min(packet.complexity for packet in packets)
        packets = [packet for packet in packets if packet.complexity == minimum]
    return packets


def _component_bbox_completion_apply(
    grid: Array,
    source_color: int,
    fill_color: int,
    connectivity: int,
) -> Array:
    source = sanitize_grid(grid)
    background = infer_background(source)
    if source_color in {background, fill_color} or fill_color == background:
        raise PerturbationAtlasAbstention("component-completion roles must be distinct")
    components = _components(source == source_color, connectivity=connectivity)
    if len(components) < 2:
        raise PerturbationAtlasAbstention("fewer than two source components")
    output = source.copy()
    filled = 0
    for component in components:
        if len(component) < 2:
            raise PerturbationAtlasAbstention("singleton source component is not a rectangle witness")
        rows = [cell[0] for cell in component]
        columns = [cell[1] for cell in component]
        r0, r1 = min(rows), max(rows) + 1
        c0, c1 = min(columns), max(columns) + 1
        region = output[r0:r1, c0:c1]
        holes = region == background
        if not np.any(holes):
            raise PerturbationAtlasAbstention("source component bounding box has no background hole")
        region[holes] = fill_color
        filled += int(np.count_nonzero(holes))
    if filled < 2:
        raise PerturbationAtlasAbstention("insufficient completed support")
    return output


def compile_component_bbox_completion(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    if not train:
        return []
    source_colors: set[int] = set()
    fill_colors: set[int] = set()
    for source, target in train:
        source = sanitize_grid(source)
        target = sanitize_grid(target)
        if source.shape != target.shape:
            return []
        try:
            background = infer_background(source)
        except PerturbationAtlasError:
            return []
        source_colors.update(int(value) for value in np.unique(source) if int(value) != background)
        changed = source != target
        fill_colors.update(
            int(value)
            for value in target[changed]
            if int(value) not in {background}
        )
    packets: List[OperatorPacket] = []
    for source_color in sorted(source_colors):
        for fill_color in sorted(fill_colors):
            if source_color == fill_color:
                continue
            for connectivity in (4, 8):
                packet = _exact_packet(
                    family="discrete_component_bbox_completion",
                    name=f"complete_{source_color}_bbox_with_{fill_color}_c{connectivity}",
                    complexity=13 if connectivity == 4 else 14,
                    train=train,
                    tests=tests,
                    apply=lambda grid, source_role=source_color, fill_role=fill_color, conn=connectivity: _component_bbox_completion_apply(
                        grid, source_role, fill_role, conn
                    ),
                    metadata={
                        "source_color": source_color,
                        "fill_color": fill_color,
                        "connectivity": connectivity,
                        "perturbation_axes": [
                            "component_connectivity",
                            "bounding_box_closure",
                            "background_hole_fill",
                        ],
                    },
                )
                if packet is not None:
                    packets.append(packet)
    return packets

def _consecutive_groups(indices: Iterable[int]) -> List[Tuple[int, int]]:
    values = sorted(set(int(index) for index in indices))
    if not values:
        return []
    groups: List[Tuple[int, int]] = []
    start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1:
            previous = value
            continue
        groups.append((start, previous + 1))
        start = previous = value
    groups.append((start, previous + 1))
    return groups


def _lattice_gap_apply(grid: Array, internal_color: int, external_color: int) -> Array:
    source = sanitize_grid(grid)
    background = infer_background(source)
    colors = [int(value) for value in np.unique(source) if int(value) != background]
    if len(colors) != 1:
        raise PerturbationAtlasAbstention("lattice completion requires one source color")
    mask = source != background
    occupied_rows = [int(index) for index in np.nonzero(np.any(mask, axis=1))[0]]
    occupied_cols = [int(index) for index in np.nonzero(np.any(mask, axis=0))[0]]
    if len(_consecutive_groups(occupied_rows)) < 2 or len(_consecutive_groups(occupied_cols)) < 2:
        raise PerturbationAtlasAbstention("source does not contain a repeated row-column lattice")
    rmin, rmax = min(occupied_rows), max(occupied_rows)
    cmin, cmax = min(occupied_cols), max(occupied_cols)
    row_set, col_set = set(occupied_rows), set(occupied_cols)
    internal_rows = {row for row in range(rmin, rmax + 1) if row not in row_set}
    internal_cols = {col for col in range(cmin, cmax + 1) if col not in col_set}
    external_rows = {row for row in range(source.shape[0]) if row < rmin or row > rmax}
    external_cols = {col for col in range(source.shape[1]) if col < cmin or col > cmax}
    if not internal_rows or not internal_cols:
        raise PerturbationAtlasAbstention("lattice has no internal row and column gaps")
    output = source.copy()
    for row in range(source.shape[0]):
        for col in range(source.shape[1]):
            if output[row, col] != background:
                continue
            if row in internal_rows and cmin <= col <= cmax:
                output[row, col] = internal_color
            elif row in row_set and col in internal_cols:
                output[row, col] = internal_color
            elif row in internal_rows and col in external_cols:
                output[row, col] = external_color
            elif row in external_rows and col in internal_cols:
                output[row, col] = external_color
    return output


def compile_lattice_gap_completion(
    train: Sequence[Tuple[Array, Array]], tests: Sequence[Array]
) -> List[OperatorPacket]:
    added_colors: set[int] = set()
    for source, target in train:
        source = sanitize_grid(source)
        target = sanitize_grid(target)
        if source.shape != target.shape:
            return []
        source_palette = set(int(value) for value in np.unique(source))
        added_colors.update(int(value) for value in np.unique(target) if int(value) not in source_palette)
    if len(added_colors) != 2:
        return []
    packets: List[OperatorPacket] = []
    first, second = sorted(added_colors)
    for internal_color, external_color in ((first, second), (second, first)):
        packet = _exact_packet(
            family="discrete_lattice_gap_completion",
            name=f"complete_internal_{internal_color}_external_{external_color}",
            complexity=14,
            train=train,
            tests=tests,
            apply=lambda grid, inside=internal_color, outside=external_color: _lattice_gap_apply(grid, inside, outside),
            metadata={
                "internal_color": internal_color,
                "external_color": external_color,
                "perturbation_axes": ["lattice_gap", "interior_boundary", "external_continuation"],
            },
        )
        if packet is not None:
            packets.append(packet)
    return packets


COMPILERS: Tuple[Tuple[str, Callable[[Sequence[Tuple[Array, Array]], Sequence[Array]], List[OperatorPacket]]], ...] = (
    ("unique_panel_extraction", compile_unique_panel_extraction),
    ("consumed_marker_recolor", compile_consumed_marker_recolor),
    ("foreground_translation_recolor", compile_foreground_translation_recolor),
    ("directional_ray_extension", compile_directional_ray_extension),
    ("uniform_axis_predicate_render", compile_uniform_axis_predicate_render),
    ("ordered_pair_phase_transport", compile_ordered_pair_phase_transport),
    ("embedded_patch_layout_serialization", compile_embedded_patch_layout_serialization),
    ("axis_cross_intersection", compile_axis_cross_intersection),
    ("template_axis_broadcast", compile_template_axis_broadcast),
    ("adjacent_pair_recode", compile_adjacent_pair_recode),
    ("component_bbox_completion", compile_component_bbox_completion),
    ("lattice_gap_completion", compile_lattice_gap_completion),
)


def compile_discrete_perturbation_operator_atlas(
    train: Sequence[Tuple[object, object]],
    tests: Sequence[object],
) -> AtlasCompilation:
    normalized_train = [(sanitize_grid(source), sanitize_grid(target)) for source, target in train]
    normalized_tests = [sanitize_grid(source) for source in tests]
    packets: List[OperatorPacket] = []
    abstentions: List[Mapping[str, object]] = []
    for compiler_name, compiler in COMPILERS:
        try:
            generated = compiler(normalized_train, normalized_tests)
        except Exception as error:  # lane isolation is part of the contract
            abstentions.append(
                {
                    "compiler": compiler_name,
                    "reason": f"{type(error).__name__}: {error}",
                }
            )
            continue
        if not generated:
            abstentions.append({"compiler": compiler_name, "reason": "no_exact_training_program"})
            continue
        packets.extend(generated)

    # Canonicalize exact duplicate semantics and behaviors without conflating
    # distinct families.  Within one family/name, retain the least complex
    # deterministic record.
    deduplicated: Dict[Tuple[str, str, str], OperatorPacket] = {}
    for packet in packets:
        key = (packet.family, packet.name, packet.behavior_hash)
        previous = deduplicated.get(key)
        if previous is None or packet.complexity < previous.complexity:
            deduplicated[key] = packet
    ordered = tuple(
        sorted(
            deduplicated.values(),
            key=lambda packet: (packet.complexity, packet.family, packet.name, packet.behavior_hash),
        )
    )
    return AtlasCompilation(packets=ordered, abstentions=tuple(abstentions))


def unanimous_family_outputs(
    compilation: AtlasCompilation,
    test_count: int,
) -> Dict[str, Tuple[Optional[Array], Mapping[str, object]]]:
    by_family: Dict[str, List[OperatorPacket]] = defaultdict(list)
    for packet in compilation.packets:
        by_family[packet.family].append(packet)
    outputs: Dict[str, Tuple[Optional[Array], Mapping[str, object]]] = {}
    for family, packets in sorted(by_family.items()):
        per_test: List[Optional[Array]] = []
        for test_index in range(test_count):
            behaviors: Dict[str, Array] = {}
            for packet in packets:
                if test_index >= len(packet.test_grids):
                    continue
                grid = packet.test_grids[test_index]
                behaviors.setdefault(grid_hash(grid), grid)
            per_test.append(next(iter(behaviors.values())).copy() if len(behaviors) == 1 else None)
        if test_count == 1:
            outputs[family] = (
                per_test[0],
                {
                    "candidate_count": len(packets),
                    "unanimous": per_test[0] is not None,
                    "program_hashes": [packet.program_hash for packet in packets],
                    "names": [packet.name for packet in packets],
                },
            )
        else:
            # Multi-output tasks are represented by a synthetic stacked record
            # only in the audit helper; callers should use family_outputs_by_test.
            outputs[family] = (
                None,
                {
                    "candidate_count": len(packets),
                    "unanimous_by_test": [grid is not None for grid in per_test],
                    "program_hashes": [packet.program_hash for packet in packets],
                    "names": [packet.name for packet in packets],
                },
            )
    return outputs


def family_outputs_by_test(
    compilation: AtlasCompilation,
    test_count: int,
) -> Dict[str, List[Optional[Array]]]:
    by_family: Dict[str, List[OperatorPacket]] = defaultdict(list)
    for packet in compilation.packets:
        by_family[packet.family].append(packet)
    output: Dict[str, List[Optional[Array]]] = {}
    for family, packets in sorted(by_family.items()):
        values: List[Optional[Array]] = []
        for test_index in range(test_count):
            behaviors: Dict[str, Array] = {}
            for packet in packets:
                if test_index < len(packet.test_grids):
                    behaviors.setdefault(grid_hash(packet.test_grids[test_index]), packet.test_grids[test_index])
            values.append(next(iter(behaviors.values())).copy() if len(behaviors) == 1 else None)
        output[family] = values
    return output


def implementation_fingerprint() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


__all__ = [
    "ATLAS_SCHEMA",
    "AtlasCompilation",
    "COMPILERS",
    "OperatorPacket",
    "PerturbationAtlasAbstention",
    "PerturbationAtlasError",
    "SCHEMA",
    "TOOL_VERSION",
    "compile_discrete_perturbation_operator_atlas",
    "family_outputs_by_test",
    "grid_hash",
    "implementation_fingerprint",
]
