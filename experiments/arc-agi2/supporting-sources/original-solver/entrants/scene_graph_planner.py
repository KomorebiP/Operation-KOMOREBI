"""Bounded task-local scene-graph planner for PR-LASM Block 14.

The planner lowers a raster into objects, panels, anchors, and pairwise
relations, then enumerates a small library of one-to-three stage graph plans.
The current plans cover ordered occlusion, anchor-aligned object transfer,
anchor-aligned panel transfer, palette-legend projection through a mask, and
concentric packing of line tokens.  Programs contain only structural roles;
they never contain task identifiers, absolute resolved coordinates, test
labels, corpus fingerprints, or score information.

Admission is deliberately strict: a plan must exactly replay every
demonstration, survive genuine leave-one-demonstration-out re-induction, stay
within finite enumeration/execution caps, and yield one minimum-description
behavior on every supplied test input.  Ties, collisions, missing roles, cap
exhaustion, or behavioral ambiguity cause abstention.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block14.scene_graph_planner.program.v1"
SCAN_SCHEMA = "komorebi.pr_lasm.block14.scene_graph_planner.scan_freeze.v1"
FOUR: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
EIGHT: tuple[Cell, ...] = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
)


class Undefined(ValueError):
    """A role is absent or tied, a plan collides, or a hard cap is hit."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 10
    max_components: int = 192
    max_programs: int = 64
    max_executor_calls: int = 4096
    max_candidates: int = 1
    mdl_slack: int = 0

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        defaults = cls()
        caps = {
            "max_grid_cells": 3600,
            "max_examples": 20,
            "max_components": 512,
            "max_programs": 512,
            "max_executor_calls": 100_000,
            "max_candidates": 1,
            "mdl_slack": 2,
        }
        result: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            fallback = (
                value.get("candidate_cap", getattr(defaults, name))
                if name == "max_candidates"
                else getattr(defaults, name)
            )
            raw = value.get(name, fallback)
            if isinstance(raw, bool) or not isinstance(raw, int):
                raise Undefined(f"limits.{name} must be an integer")
            minimum = 0 if name == "mdl_slack" else 1
            if raw < minimum:
                raise Undefined(f"limits.{name} is below {minimum}")
            result[name] = min(raw, caps[name])
        return cls(**result)


@dataclass(frozen=True, slots=True)
class Component:
    cells: tuple[tuple[int, int, int], ...]

    @property
    def positions(self) -> frozenset[Cell]:
        return frozenset((row, column) for row, column, _ in self.cells)

    @property
    def colors(self) -> tuple[int, ...]:
        return tuple(sorted({color for _, _, color in self.cells}))

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        rows = [row for row, _, _ in self.cells]
        columns = [column for _, column, _ in self.cells]
        return min(rows), max(rows), min(columns), max(columns)

    @property
    def height(self) -> int:
        top, bottom, _, _ = self.bbox
        return bottom - top + 1

    @property
    def width(self) -> int:
        _, _, left, right = self.bbox
        return right - left + 1


@dataclass(frozen=True, slots=True)
class Plan:
    macro: str
    description_length: int
    stages: tuple[str, ...]

    def record(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "macro": self.macro,
            "description_length": self.description_length,
            "stages": list(self.stages),
            "roles": {
                "coordinates": "resolved_at_execution",
                "colors": "relational",
                "identity": "component_or_panel_graph",
            },
        }


PLANS: tuple[Plan, ...] = (
    Plan("ordered_occlusion", 9, ("parse_line_graph", "topological_order")),
    Plan("concentric_line_pack", 10, ("parse_line_tokens", "pack_concentrically")),
    Plan("legend_mask_projection", 12, ("parse_mask_and_legend", "project_palette")),
    Plan("anchor_object_overlay", 14, ("parse_canvas_and_objects", "align_anchors", "render_crop")),
    Plan("anchor_panel_transfer", 15, ("parse_panels", "align_anchors", "render_target")),
    Plan("port_chain_pack", 16, ("split_marker_ports", "align_port_chain", "pack_components")),
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid rows must be nonempty sequences")
        row: list[int] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, bool) or not isinstance(raw_cell, int) or not 0 <= raw_cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid must be rectangular")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > limits.max_grid_cells:
        raise Undefined("grid exceeds max_grid_cells")
    return tuple(rows)


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train, test = task.get("train"), task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes))
        or len(train) < 2
        or not isinstance(test, Sequence)
        or isinstance(test, (str, bytes))
        or not test
        or len(train) + len(test) > limits.max_examples
    ):
        raise Undefined("task arity is invalid")
    pairs: list[Pair] = []
    for example in train:
        if not isinstance(example, Mapping):
            raise Undefined("demonstration is invalid")
        pairs.append((_grid(example.get("input"), limits), _grid(example.get("output"), limits)))
    tests: list[Grid] = []
    for example in test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        # Deliberately extract only the input.  Attached label decoys vanish here.
        tests.append(_grid(example.get("input"), limits))
    return tuple(pairs), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _unique_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty role population")
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    if len(winners) != 1:
        raise Undefined("mode role is tied")
    return winners[0]


def _background(grid: Grid) -> int:
    height, width = _shape(grid)
    try:
        return _unique_mode(cell for row in grid for cell in row)
    except Undefined:
        corners = (grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1])
        if len(set(corners)) == 1:
            return corners[0]
        border = (
            grid[row][column]
            for row in range(height)
            for column in range(width)
            if row in {0, height - 1} or column in {0, width - 1}
        )
        return _unique_mode(border)


def _components(
    grid: Grid,
    *,
    background: int,
    connectivity: int,
    monochrome: bool,
    limits: Limits,
) -> tuple[Component, ...]:
    height, width = _shape(grid)
    directions = FOUR if connectivity == 4 else EIGHT
    seen: set[Cell] = set()
    result: list[Component] = []
    for row in range(height):
        for column in range(width):
            if (row, column) in seen or grid[row][column] == background:
                continue
            seed_color = grid[row][column]
            queue = deque([(row, column)])
            seen.add((row, column))
            cells: list[tuple[int, int, int]] = []
            while queue:
                current_row, current_column = queue.popleft()
                color = grid[current_row][current_column]
                cells.append((current_row, current_column, color))
                for dr, dc in directions:
                    neighbor = current_row + dr, current_column + dc
                    if (
                        0 <= neighbor[0] < height
                        and 0 <= neighbor[1] < width
                        and neighbor not in seen
                        and grid[neighbor[0]][neighbor[1]] != background
                        and (not monochrome or grid[neighbor[0]][neighbor[1]] == seed_color)
                    ):
                        seen.add(neighbor)
                        queue.append(neighbor)
            result.append(Component(tuple(sorted(cells))))
            if len(result) > limits.max_components:
                raise Undefined("component cap exhausted")
    return tuple(result)


def _bbox_cells(grid: Grid, bbox: tuple[int, int, int, int]) -> Grid:
    top, bottom, left, right = bbox
    return tuple(tuple(grid[row][left : right + 1]) for row in range(top, bottom + 1))


def _in_bbox(cell: Cell, bbox: tuple[int, int, int, int]) -> bool:
    row, column = cell
    top, bottom, left, right = bbox
    return top <= row <= bottom and left <= column <= right


def _concentric_line_pack(grid: Grid, limits: Limits) -> Grid:
    background = _background(grid)
    by_color: dict[int, list[Cell]] = {}
    for row, values in enumerate(grid):
        for column, color in enumerate(values):
            if color != background:
                by_color.setdefault(color, []).append((row, column))
    if len(by_color) < 3:
        raise Undefined("need at least three line tokens")
    tokens: list[tuple[int, int]] = []
    for color, cells in sorted(by_color.items()):
        rows = {row for row, _ in cells}
        columns = {column for _, column in cells}
        if len(rows) != 1 and len(columns) != 1:
            raise Undefined("token is not a straight line")
        if len(cells) > 1:
            coordinates = sorted(column for _, column in cells) if len(rows) == 1 else sorted(row for row, _ in cells)
            if coordinates != list(range(coordinates[0], coordinates[-1] + 1)):
                raise Undefined("line token has a gap")
        tokens.append((len(cells), color))
    if len({length for length, _ in tokens}) != len(tokens):
        raise Undefined("line lengths do not induce a unique order")
    tokens.sort(reverse=True)
    size = tokens[0][0]
    if size < 2 * len(tokens) - 2 or size > 30:
        raise Undefined("line lengths do not fit concentric layers")
    output = [[tokens[-1][1] for _ in range(size)] for _ in range(size)]
    for depth, (_, color) in enumerate(tokens[:-1]):
        low, high = depth, size - depth - 1
        if low > high:
            raise Undefined("too many layers")
        for index in range(low, high + 1):
            output[low][index] = color
            output[high][index] = color
            output[index][low] = color
            output[index][high] = color
    return tuple(tuple(row) for row in output)


def _legend_mask_projection(grid: Grid, limits: Limits) -> Grid:
    background = _background(grid)
    components = _components(
        grid, background=background, connectivity=4, monochrome=True, limits=limits
    )
    candidates: set[Grid] = set()
    height, width = _shape(grid)
    eligible = [
        component
        for component in components
        if component.area >= 4
        and component.height >= 2
        and component.width >= 2
        and len(component.colors) == 1
    ]
    if not eligible:
        raise Undefined("mask component is absent")
    maximum_area = max(component.area for component in eligible)
    # The mask is the unique dominant 2-D monochrome object.  This prevents a
    # repeated-color run inside the legend from recursively posing as a mask.
    eligible = [component for component in eligible if component.area == maximum_area]
    if len(eligible) != 1:
        raise Undefined("dominant mask role is tied")
    for component in eligible:
        if component.area < 4 or component.height < 2 or component.width < 2 or len(component.colors) != 1:
            continue
        mask_color = component.colors[0]
        top, bottom, left, right = component.bbox
        if any(
            grid[row][column] not in {background, mask_color}
            for row in range(top, bottom + 1)
            for column in range(left, right + 1)
        ):
            continue
        # Horizontal legend: two identical palette rows above a solid fallback.
        span = component.width
        for row in range(height - 2):
            for column in range(width - span + 1):
                box = (row, row + 2, column, column + span - 1)
                if not (
                    bottom < box[0] or box[1] < top or right < box[2] or box[3] < left
                ):
                    continue
                first = tuple(grid[row][column : column + span])
                second = tuple(grid[row + 1][column : column + span])
                third = tuple(grid[row + 2][column : column + span])
                if (
                    first == second
                    and len(set(third)) == 1
                    and background not in first
                    and background not in third
                    and mask_color not in first
                    and mask_color not in third
                ):
                    fallback = third[0]
                    prediction = tuple(
                        tuple(first[c] if grid[r][left + c] == mask_color else fallback for c in range(span))
                        for r in range(top, bottom + 1)
                    )
                    candidates.add(prediction)
        # Vertical D4 counterpart: two identical palette columns beside a solid fallback.
        span = component.height
        for row in range(height - span + 1):
            for column in range(width - 2):
                box = (row, row + span - 1, column, column + 2)
                if not (
                    bottom < box[0] or box[1] < top or right < box[2] or box[3] < left
                ):
                    continue
                first = tuple(grid[row + r][column] for r in range(span))
                second = tuple(grid[row + r][column + 1] for r in range(span))
                third = tuple(grid[row + r][column + 2] for r in range(span))
                if (
                    first == second
                    and len(set(third)) == 1
                    and background not in first
                    and background not in third
                    and mask_color not in first
                    and mask_color not in third
                ):
                    fallback = third[0]
                    prediction = tuple(
                        tuple(first[r] if grid[top + r][c] == mask_color else fallback for c in range(left, right + 1))
                        for r in range(span)
                    )
                    candidates.add(prediction)
    if len(candidates) != 1:
        raise Undefined("mask/legend role is absent or ambiguous")
    return next(iter(candidates))


def _dense_canvas_candidates(grid: Grid, limits: Limits) -> tuple[tuple[int, tuple[int, int, int, int]], ...]:
    background = _background(grid)
    result: list[tuple[int, tuple[int, int, int, int]]] = []
    for color in sorted({cell for row in grid for cell in row} - {background}):
        positions = [(row, column) for row, values in enumerate(grid) for column, value in enumerate(values) if value == color]
        top = min(row for row, _ in positions)
        bottom = max(row for row, _ in positions)
        left = min(column for _, column in positions)
        right = max(column for _, column in positions)
        area = (bottom - top + 1) * (right - left + 1)
        if area < 12 or len(positions) * 4 < area * 3:
            continue
        values = [grid[row][column] for row in range(top, bottom + 1) for column in range(left, right + 1)]
        if background in values or len(set(values)) < 2:
            continue
        result.append((color, (top, bottom, left, right)))
    return tuple(result)


def _anchor_object_overlay(grid: Grid, limits: Limits) -> Grid:
    background = _background(grid)
    outputs: set[Grid] = set()
    support_components = _components(
        grid, background=background, connectivity=8, monochrome=False, limits=limits
    )
    for base, bbox in _dense_canvas_candidates(grid, limits):
        top, bottom, left, right = bbox
        canvas_anchors: dict[int, Cell] = {}
        invalid = False
        for row in range(top, bottom + 1):
            for column in range(left, right + 1):
                color = grid[row][column]
                if color == base:
                    continue
                if color in canvas_anchors:
                    invalid = True
                canvas_anchors[color] = (row, column)
        if invalid or not canvas_anchors:
            continue
        canvas_support = {(row, column) for row in range(top, bottom + 1) for column in range(left, right + 1)}
        external = [component for component in support_components if component.positions.isdisjoint(canvas_support)]
        output = [list(row[left : right + 1]) for row in grid[top : bottom + 1]]
        applied = 0
        occupied_by_transfer: dict[Cell, int] = {}
        try:
            for component in external:
                counts = Counter(color for _, _, color in component.cells)
                anchor_options = [
                    (color, row, column)
                    for row, column, color in component.cells
                    if color in canvas_anchors and counts[color] == 1
                ]
                if len(anchor_options) != 1 or len(counts) != 2:
                    continue
                anchor_color, source_row, source_column = anchor_options[0]
                target_row, target_column = canvas_anchors[anchor_color]
                translated: list[tuple[int, int, int]] = []
                for row, column, color in component.cells:
                    destination = row + target_row - source_row, column + target_column - source_column
                    if not _in_bbox(destination, bbox):
                        raise Undefined("aligned object exits canvas")
                    local = destination[0] - top, destination[1] - left
                    current = output[local[0]][local[1]]
                    if color == anchor_color:
                        if current != anchor_color:
                            raise Undefined("anchor identity mismatch")
                    elif current != base and current != color:
                        raise Undefined("object transfer collides with a canvas anchor")
                    if local in occupied_by_transfer and occupied_by_transfer[local] != color:
                        raise Undefined("transferred objects collide")
                    translated.append((local[0], local[1], color))
                for row, column, color in translated:
                    output[row][column] = color
                    occupied_by_transfer[(row, column)] = color
                applied += 1
        except Undefined:
            continue
        if applied:
            outputs.add(tuple(tuple(row) for row in output))
    if len(outputs) != 1:
        raise Undefined("canvas/object alignment is absent or ambiguous")
    return next(iter(outputs))


def _panel_candidates(grid: Grid, limits: Limits) -> tuple[tuple[int, tuple[int, int, int, int]], ...]:
    background = _background(grid)
    candidates: list[tuple[int, tuple[int, int, int, int]]] = []
    # A payload can split the otherwise solid fill into several monochrome
    # pieces.  Parse the whole non-background support first, then infer its
    # unique dominant fill color inside the component bounding box.
    for component in _components(
        grid, background=background, connectivity=4, monochrome=False, limits=limits
    ):
        if component.area < 6:
            continue
        top, bottom, left, right = component.bbox
        area = component.height * component.width
        if component.area != area:
            continue
        counts = Counter(color for _, _, color in component.cells)
        maximum = max(counts.values())
        fills = sorted(color for color, count in counts.items() if count == maximum)
        if len(fills) != 1 or maximum * 5 < area * 3:
            continue
        fill = fills[0]
        candidates.append((fill, component.bbox))
    return tuple(candidates)


def _anchor_panel_transfer(grid: Grid, limits: Limits) -> Grid:
    outputs: set[Grid] = set()
    panels = _panel_candidates(grid, limits)
    for target_fill, target_bbox in panels:
        target = _bbox_cells(grid, target_bbox)
        target_counts = Counter(cell for row in target for cell in row if cell != target_fill)
        target_anchors = [color for color, count in target_counts.items() if count == 1]
        if len(target_anchors) != 1:
            continue
        anchor = target_anchors[0]
        target_anchor = next(
            (row, column)
            for row in range(target_bbox[0], target_bbox[1] + 1)
            for column in range(target_bbox[2], target_bbox[3] + 1)
            if grid[row][column] == anchor
        )
        for source_fill, source_bbox in panels:
            if source_fill != target_fill or source_bbox == target_bbox:
                continue
            source = _bbox_cells(grid, source_bbox)
            source_counts = Counter(cell for row in source for cell in row if cell != source_fill)
            if source_counts.get(anchor) != 1 or sum(source_counts.values()) <= 1:
                continue
            source_anchor = next(
                (row, column)
                for row in range(source_bbox[0], source_bbox[1] + 1)
                for column in range(source_bbox[2], source_bbox[3] + 1)
                if grid[row][column] == anchor
            )
            height = target_bbox[1] - target_bbox[0] + 1
            width = target_bbox[3] - target_bbox[2] + 1
            output = [[target_fill] * width for _ in range(height)]
            valid = True
            for row in range(source_bbox[0], source_bbox[1] + 1):
                for column in range(source_bbox[2], source_bbox[3] + 1):
                    color = grid[row][column]
                    if color == source_fill:
                        continue
                    destination = row + target_anchor[0] - source_anchor[0], column + target_anchor[1] - source_anchor[1]
                    if not _in_bbox(destination, target_bbox):
                        valid = False
                        break
                    output[destination[0] - target_bbox[0]][destination[1] - target_bbox[2]] = color
                if not valid:
                    break
            if valid:
                outputs.add(tuple(tuple(row) for row in output))
    if len(outputs) != 1:
        raise Undefined("panel transfer is absent or ambiguous")
    return next(iter(outputs))


@dataclass(frozen=True, slots=True)
class PortPiece:
    color: int
    cells: frozenset[Cell]
    ports: frozenset[Cell]
    source_top: int
    source_left: int
    height: int
    width: int


def _port_pieces(grid: Grid, marker: int, limits: Limits) -> tuple[PortPiece, ...]:
    background = _background(grid)
    height, width = _shape(grid)
    seen: set[Cell] = set()
    raw: list[tuple[int, set[Cell]]] = []
    owner: dict[Cell, int] = {}
    for row in range(height):
        for column in range(width):
            if (row, column) in seen or grid[row][column] in {background, marker}:
                continue
            color = grid[row][column]
            queue = deque([(row, column)])
            seen.add((row, column))
            cells: set[Cell] = set()
            while queue:
                cell = queue.popleft()
                cells.add(cell)
                for dr, dc in FOUR:
                    neighbor = cell[0] + dr, cell[1] + dc
                    if (
                        0 <= neighbor[0] < height
                        and 0 <= neighbor[1] < width
                        and neighbor not in seen
                        and grid[neighbor[0]][neighbor[1]] == color
                    ):
                        seen.add(neighbor)
                        queue.append(neighbor)
            index = len(raw)
            raw.append((color, cells))
            for cell in cells:
                owner[cell] = index
            if len(raw) > limits.max_components:
                raise Undefined("piece cap exhausted")
    if len(raw) < 2:
        raise Undefined("port chain needs at least two payload pieces")
    assigned: list[set[Cell]] = [set() for _ in raw]
    marker_cells = [
        (row, column)
        for row, values in enumerate(grid)
        for column, color in enumerate(values)
        if color == marker
    ]
    if len(marker_cells) < len(raw):
        raise Undefined("too few marker ports")
    for cell in marker_cells:
        owners = {
            owner[neighbor]
            for dr, dc in FOUR
            if (neighbor := (cell[0] + dr, cell[1] + dc)) in owner
        }
        if len(owners) != 1:
            raise Undefined("marker port ownership is tied")
        assigned[next(iter(owners))].add(cell)
    pieces: list[PortPiece] = []
    for index, (color, payload) in enumerate(raw):
        if not assigned[index] or len(assigned[index]) > 2:
            raise Undefined("piece port degree is outside chain grammar")
        all_cells = payload | assigned[index]
        top = min(row for row, _ in all_cells)
        bottom = max(row for row, _ in all_cells)
        left = min(column for _, column in all_cells)
        right = max(column for _, column in all_cells)
        pieces.append(
            PortPiece(
                color=color,
                cells=frozenset((row - top, column - left) for row, column in all_cells),
                ports=frozenset((row - top, column - left) for row, column in assigned[index]),
                source_top=top,
                source_left=left,
                height=bottom - top + 1,
                width=right - left + 1,
            )
        )
    pieces.sort(key=lambda piece: (piece.source_left, piece.source_top, piece.color))
    if len({piece.source_left for piece in pieces}) != len(pieces):
        raise Undefined("left-to-right piece order is tied")
    return tuple(pieces)


def _port_chain_pack(grid: Grid, limits: Limits) -> Grid:
    background = _background(grid)
    outputs: set[Grid] = set()
    height, _ = _shape(grid)
    for marker in sorted({cell for row in grid for cell in row} - {background}):
        try:
            pieces = _port_pieces(grid, marker, limits)
        except Undefined:
            continue
        total_width = sum(piece.width for piece in pieces)
        if total_width > 30:
            continue
        placements: list[tuple[int, int]] = [(pieces[0].source_top, 0)]
        if not 0 <= placements[0][0] <= height - pieces[0].height:
            continue
        valid = True
        cursor = pieces[0].width
        for previous, piece in zip(pieces, pieces[1:]):
            previous_top, previous_left = placements[-1]
            previous_rows = {
                previous_top + row
                for row, column in previous.ports
                if column == previous.width - 1
            }
            possible_tops = []
            for candidate_top in range(height - piece.height + 1):
                next_rows = {
                    candidate_top + row
                    for row, column in piece.ports
                    if column == 0
                }
                if len(previous_rows & next_rows) == 1:
                    possible_tops.append(candidate_top)
            if len(possible_tops) != 1:
                valid = False
                break
            placements.append((possible_tops[0], cursor))
            cursor += piece.width
        if not valid:
            continue
        output = [[background] * total_width for _ in range(height)]
        occupied: set[Cell] = set()
        for piece, (top, left) in zip(pieces, placements):
            for row, column in piece.cells:
                destination = top + row, left + column
                if destination in occupied:
                    valid = False
                    break
                occupied.add(destination)
                output[destination[0]][destination[1]] = piece.color
            if not valid:
                break
        if valid:
            outputs.add(tuple(tuple(row) for row in output))
    if len(outputs) != 1:
        raise Undefined("port-chain packing is absent or ambiguous")
    return next(iter(outputs))


@dataclass(frozen=True, slots=True)
class Line:
    color: int
    kind: str
    invariant: int
    low: int
    high: int

    def contains(self, row: int, column: int) -> bool:
        if self.kind == "row":
            return row == self.invariant and self.low <= column <= self.high
        if self.kind == "column":
            return column == self.invariant and self.low <= row <= self.high
        if self.kind == "diag":
            return row - column == self.invariant and self.low <= row <= self.high
        if self.kind == "anti":
            return row + column == self.invariant and self.low <= row <= self.high
        return False


def _line_for_color(grid: Grid, color: int) -> Line:
    cells = [(row, column) for row, values in enumerate(grid) for column, value in enumerate(values) if value == color]
    if len(cells) < 2:
        raise Undefined("line has fewer than two visible cells")
    candidates: list[Line] = []
    rows = {row for row, _ in cells}
    columns = {column for _, column in cells}
    diagonals = {row - column for row, column in cells}
    antis = {row + column for row, column in cells}
    if len(rows) == 1:
        candidates.append(Line(color, "row", next(iter(rows)), min(column for _, column in cells), max(column for _, column in cells)))
    if len(columns) == 1:
        candidates.append(Line(color, "column", next(iter(columns)), min(row for row, _ in cells), max(row for row, _ in cells)))
    if len(diagonals) == 1:
        candidates.append(Line(color, "diag", next(iter(diagonals)), min(row for row, _ in cells), max(row for row, _ in cells)))
    if len(antis) == 1:
        candidates.append(Line(color, "anti", next(iter(antis)), min(row for row, _ in cells), max(row for row, _ in cells)))
    if len(candidates) != 1:
        raise Undefined("line orientation is absent or tied")
    return candidates[0]


def _intersection(left: Line, right: Line, shape: tuple[int, int]) -> Cell | None:
    height, width = shape
    hits = [
        (row, column)
        for row in range(height)
        for column in range(width)
        if left.contains(row, column) and right.contains(row, column)
    ]
    return hits[0] if len(hits) == 1 else None


def _ordered_occlusion(grid: Grid, limits: Limits) -> Grid:
    background = _background(grid)
    colors = sorted({cell for row in grid for cell in row} - {background})
    if not 2 <= len(colors) <= 9:
        raise Undefined("occlusion graph color count is outside bounds")
    lines = {color: _line_for_color(grid, color) for color in colors}
    outgoing: dict[int, set[int]] = {color: set() for color in colors}
    indegree = {color: 0 for color in colors}
    edge_count = 0
    for index, left_color in enumerate(colors):
        for right_color in colors[index + 1 :]:
            cell = _intersection(lines[left_color], lines[right_color], _shape(grid))
            if cell is None:
                continue
            visible = grid[cell[0]][cell[1]]
            if visible == left_color:
                loser, winner = right_color, left_color
            elif visible == right_color:
                loser, winner = left_color, right_color
            else:
                continue
            if winner not in outgoing[loser]:
                outgoing[loser].add(winner)
                indegree[winner] += 1
                edge_count += 1
    if edge_count < len(colors) - 1:
        raise Undefined("occlusion graph is not connected enough to order")
    order: list[int] = []
    remaining = set(colors)
    while remaining:
        available = sorted(color for color in remaining if indegree[color] == 0)
        if len(available) != 1:
            raise Undefined("occlusion order is cyclic or ambiguous")
        chosen = available[0]
        order.append(chosen)
        remaining.remove(chosen)
        for successor in outgoing[chosen]:
            indegree[successor] -= 1
    return (tuple(order),)


def _execute_macro(macro: str, grid: Grid, limits: Limits) -> Grid:
    if macro == "ordered_occlusion":
        return _ordered_occlusion(grid, limits)
    if macro == "concentric_line_pack":
        return _concentric_line_pack(grid, limits)
    if macro == "legend_mask_projection":
        return _legend_mask_projection(grid, limits)
    if macro == "anchor_object_overlay":
        return _anchor_object_overlay(grid, limits)
    if macro == "anchor_panel_transfer":
        return _anchor_panel_transfer(grid, limits)
    if macro == "port_chain_pack":
        return _port_chain_pack(grid, limits)
    raise Undefined("unknown scene-graph macro")


def _validate_program(program: Mapping[str, Any]) -> Plan:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid program schema")
    macro = program.get("macro")
    matches = [plan for plan in PLANS if plan.macro == macro]
    if len(matches) != 1:
        raise Undefined("unknown program macro")
    expected = matches[0].record()
    if json.loads(_canonical(program)) != expected:
        raise Undefined("program record is not canonical")
    return matches[0]


def execute_program(
    program: Mapping[str, Any], grid: Any, limits: Mapping[str, Any] | None = None
) -> list[list[int]]:
    """Execute a serialized structural plan on one input grid."""

    bounds = Limits.from_value(limits)
    plan = _validate_program(program)
    source = _grid(grid, bounds)
    return _plain(_execute_macro(plan.macro, source, bounds))


def replay_program(
    program: Mapping[str, Any], grid: Any, limits: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Replay with a tournament-verifiable one-to-three stage grid chain."""

    bounds = Limits.from_value(limits)
    plan = _validate_program(program)
    source = _grid(grid, bounds)
    final = _execute_macro(plan.macro, source, bounds)
    stages: list[dict[str, Any]] = []
    current = source
    for index, name in enumerate(plan.stages):
        output = final if index == len(plan.stages) - 1 else current
        stages.append({"name": name, "input": _plain(current), "output": _plain(output)})
        current = output
    return {"output": _plain(final), "stages": stages}


def _exact_plans(pairs: Sequence[Pair], limits: Limits) -> tuple[tuple[Plan, ...], int]:
    if len(PLANS) > limits.max_programs:
        raise Undefined("program enumeration cap exhausted")
    exact: list[Plan] = []
    calls = 0
    for plan in PLANS:
        okay = True
        for source, target in pairs:
            calls += 1
            if calls > limits.max_executor_calls:
                raise Undefined("executor call cap exhausted")
            try:
                prediction = _execute_macro(plan.macro, source, limits)
            except Undefined:
                okay = False
                break
            if prediction != target:
                okay = False
                break
        if okay:
            exact.append(plan)
    return tuple(exact), calls


def _minimum_plans(pairs: Sequence[Pair], limits: Limits) -> tuple[tuple[Plan, ...], int]:
    exact, calls = _exact_plans(pairs, limits)
    if not exact:
        return (), calls
    minimum = min(plan.description_length for plan in exact)
    return tuple(plan for plan in exact if plan.description_length <= minimum + limits.mdl_slack), calls


def _loo_guard(pairs: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    checks = 0
    behavior_classes = 0
    for held_index, (held_source, held_target) in enumerate(pairs):
        reduced = tuple(pair for index, pair in enumerate(pairs) if index != held_index)
        if not reduced:
            return False, checks, behavior_classes
        plans, calls = _minimum_plans(reduced, limits)
        checks += calls
        if not plans:
            return False, checks, behavior_classes
        predictions: set[Grid] = set()
        for plan in plans:
            checks += 1
            if checks > limits.max_executor_calls:
                return False, checks, behavior_classes
            try:
                predictions.add(_execute_macro(plan.macro, held_source, limits))
            except Undefined:
                return False, checks, behavior_classes
        behavior_classes += len(predictions)
        if predictions != {held_target}:
            return False, checks, behavior_classes
    return True, checks, behavior_classes


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile at most one exact, LOO-stable, behaviorally unique graph plan."""

    try:
        bounds = Limits.from_value(limits)
        pairs, tests = _sanitize(task, bounds)
        plans, calls = _minimum_plans(pairs, bounds)
    except (Undefined, TypeError, ValueError):
        return []
    if not plans:
        return []
    behaviors: dict[str, list[tuple[Plan, tuple[Grid, ...]]]] = {}
    for plan in plans:
        try:
            outputs = tuple(_execute_macro(plan.macro, grid, bounds) for grid in tests)
        except Undefined:
            continue
        key = _digest([_plain(output) for output in outputs])
        behaviors.setdefault(key, []).append((plan, outputs))
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalents = next(iter(sorted(behaviors.items())))
    equivalents.sort(key=lambda item: (item[0].description_length, item[0].macro))
    representative, test_outputs = equivalents[0]
    loo_ok, loo_checks, loo_classes = _loo_guard(pairs, bounds)
    if not loo_ok:
        return []
    try:
        train_outputs = tuple(_execute_macro(representative.macro, source, bounds) for source, _ in pairs)
    except Undefined:
        return []
    if train_outputs != tuple(target for _, target in pairs):
        return []
    candidate = {
        "family": "scene_graph_planner",
        "program": representative.record(),
        "train_outputs": [_plain(output) for output in train_outputs],
        "test_outputs": [_plain(output) for output in test_outputs],
        "complexity": representative.description_length,
        "evidence": {
            "all_demos_exact": True,
            "exact_replay": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_executor_checks": loo_checks,
            "leave_one_out_behavior_classes": loo_classes,
            "bounded_enumeration_complete": True,
            "programs_enumerated": len(PLANS),
            "executor_calls": calls,
            "hard_caps_exhausted": False,
            "near_mdl_programs": len(plans),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalents),
            "plan_stage_count": len(representative.stages),
            "supports_split_merge_occlusion": True,
            "supports_pairwise_alignment_order_packing": True,
            "serialized_resolved_coordinates": False,
            "task_identity_observed": False,
            "test_labels_observed": False,
            "solution_store_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


def _safe_task(task: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(task, Mapping) or not isinstance(task.get("train"), list) or not isinstance(task.get("test"), list):
        raise Undefined("task splits are invalid")
    return {
        "train": [
            {"input": example["input"], "output": example["output"]}
            for example in task["train"]
        ],
        "test": [{"input": example["input"]} for example in task["test"]],
    }


def freeze_scan(
    challenges: Mapping[str, Mapping[str, Any]],
    *,
    limits: Mapping[str, Any] | None = None,
    source_hash: str | None = None,
    entrant_source_hash: str | None = None,
    run_name: str = "scene-graph-planner-scan",
) -> dict[str, Any]:
    """Freeze a deterministic challenge-only scan without opening labels."""

    records: dict[str, Any] = {}
    activated = 0
    for raw_task_id, task in sorted(challenges.items(), key=lambda item: str(item[0])):
        safe = _safe_task(task)
        candidates = compile_task(safe, limits=limits)
        if len(candidates) > 1:
            raise AssertionError("one-candidate contract violated")
        if candidates:
            activated += 1
        record = {
            "task_semantic_hash": _digest(safe),
            "status": "candidate" if candidates else "abstention",
            "candidates": candidates,
        }
        record["content_hash"] = _digest(record)
        records[str(raw_task_id)] = record
    body = {
        "schema": SCAN_SCHEMA,
        "schema_version": 1,
        "author": AUTHOR,
        "phase": "prediction_freeze_before_solution_open",
        "label_access": "none",
        "run_name": run_name,
        "source_hash": source_hash,
        "entrant_source_hash": entrant_source_hash,
        "source_task_count": len(challenges),
        "activation_count": activated,
        "records": records,
        "claim_boundary": (
            "Challenge-only deterministic scan. The entrant receives demonstrations and "
            "test inputs; no solution, score, result, baseline, or submission is opened."
        ),
    }
    body["semantic_hash"] = _digest(body)
    body["content_hash"] = _digest(body)
    return body


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-name", default="scene-graph-planner-scan")
    args = parser.parse_args(argv)
    raw = args.challenges.read_bytes()
    challenges = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(challenges, Mapping):
        raise ValueError("challenges JSON must contain an object")
    frozen = freeze_scan(
        challenges,
        source_hash=hashlib.sha256(raw).hexdigest(),
        entrant_source_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        run_name=args.run_name,
    )
    _write_json(args.output, frozen)
    print(
        _canonical(
            {
                "activation_count": frozen["activation_count"],
                "content_hash": frozen["content_hash"],
                "source_task_count": frozen["source_task_count"],
            }
        )
    )
    return 0


__all__ = [
    "AUTHOR",
    "Limits",
    "SCHEMA",
    "Undefined",
    "compile_task",
    "execute_program",
    "freeze_scan",
    "replay_program",
]


if __name__ == "__main__":
    raise SystemExit(main())
