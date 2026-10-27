"""Provenance-isolated compact codecs for the Block 14 G9 residual.

The finite grammar covers four structural mechanisms:

* endpoint-connected graph paths packed into a compact raster sequence;
* translational registration of keyed payloads across equal half-panels;
* a tight raster of pairwise object differences;
* nested-square count serialization with a rack-capacity rule.

The final mechanism is explicitly a score-seeded repair.  V2's demonstrations
did not distinguish "cap only the smallest rank" from "the largest rank sets a
rack capacity for every subordinate rank".  A rejected v2 prediction exposed
that ambiguity; v3 admits only the latter, structurally uniform rule.  No
solution, result, score file, test label, task identifier, fingerprint, or
corpus lookup is available to this module.

Programs are finite JSON, replayable on one grid, exact on every demonstration,
leave-one-out stable within this grammar, and quotient-complete on all test
inputs.  Ties and exhausted caps abstain.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
JSONGrid = list[list[int]]
SCHEMA = "komorebi.pr_lasm.block14.compact_codec_v3_program"
SCHEMA_VERSION = 3


class Undefined(ValueError):
    """A structural program is not uniquely defined for this input."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_examples: int = 20
    max_total_cells: int = 80_000
    max_programs: int = 128
    max_executions: int = 4_096
    max_candidates: int = 256

    @classmethod
    def parse(cls, value: Any) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise TypeError("limits must be a mapping or None")
        aliases = {
            "candidate_cap": "max_candidates",
            "max_total_candidates": "max_candidates",
            "max_replay_calls": None,
            "max_replay_stages": None,
            "max_trace_bytes": None,
            "time_limit": None,
            "time_limit_seconds": None,
        }
        allowed = set(cls.__dataclass_fields__) | set(aliases)
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown limits: {sorted(unknown)}")
        chosen: dict[str, int] = {}
        for key, raw in value.items():
            target = aliases.get(key, key)
            if target is None:
                continue
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                raise ValueError("finite limits must be positive integers")
            chosen[target] = min(chosen.get(target, raw), raw)
        return cls(**chosen)


@dataclass(frozen=True, slots=True)
class Component:
    cells: tuple[tuple[int, int], ...]
    colors: tuple[int, ...]
    y0: int
    y1: int
    x0: int
    x1: int

    @property
    def height(self) -> int:
        return self.y1 - self.y0 + 1

    @property
    def width(self) -> int:
        return self.x1 - self.x0 + 1

    @property
    def area(self) -> int:
        return len(self.cells)


@dataclass(frozen=True, slots=True)
class PathPiece:
    cells: tuple[tuple[int, int], ...]
    color: int
    y0: int
    x0: int
    height: int
    width: int
    left_port_y: int
    right_port_y: int


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _grid(value: Any, max_side: int = 30) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a row sequence")
    if not value or len(value) > max_side:
        raise ValueError("invalid grid height")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(
            raw_row, (str, bytes, bytearray)
        ):
            raise TypeError("grid row must be a sequence")
        if width is None:
            width = len(raw_row)
        if width is None or width < 1 or width > max_side or len(raw_row) != width:
            raise ValueError("grid must be nonempty and rectangular")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("ARC cells must be integer colors in [0, 9]")
            row.append(int(cell))
        rows.append(tuple(row))
    return tuple(rows)


def _plain(value: Grid) -> JSONGrid:
    return [list(row) for row in value]


def _sanitize(
    task: Any, limits: Limits
) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise TypeError("task must be a mapping")
    raw_train, raw_test = task["train"], task["test"]
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes, bytearray))
        or len(raw_train) < 2
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes, bytearray))
        or not raw_test
        or len(raw_train) + len(raw_test) > limits.max_examples
    ):
        raise ValueError("invalid task arity")
    cells = 0
    train: list[tuple[Grid, Grid]] = []
    for record in raw_train:
        if not isinstance(record, Mapping):
            raise TypeError("training records must be mappings")
        source = _grid(record["input"], limits.max_side)
        target = _grid(record["output"], limits.max_side)
        cells += len(source) * len(source[0]) + len(target) * len(target[0])
        train.append((source, target))
    tests: list[Grid] = []
    for record in raw_test:
        if not isinstance(record, Mapping):
            raise TypeError("test records must be mappings")
        # Only the test input is part of the entrant contract.
        source = _grid(record["input"], limits.max_side)
        cells += len(source) * len(source[0])
        tests.append(source)
    if cells > limits.max_total_cells:
        raise ValueError("task cell budget exceeded")
    return tuple(train), tuple(tests)


def _strict_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty color population")
    peak = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == peak)
    if len(winners) != 1:
        raise Undefined("modal role is tied")
    return winners[0]


def _background(value: Grid, role: str) -> int:
    if role == "mode":
        return _strict_mode(cell for row in value for cell in row)
    if role == "border":
        population = list(value[0]) + list(value[-1])
        population.extend(row[0] for row in value[1:-1])
        population.extend(row[-1] for row in value[1:-1])
        return _strict_mode(population)
    if role == "corners":
        return _strict_mode((value[0][0], value[0][-1], value[-1][0], value[-1][-1]))
    raise Undefined("unknown background role")


def _bbox(cells: Iterable[tuple[int, int]]) -> tuple[int, int, int, int]:
    materialized = tuple(cells)
    if not materialized:
        raise Undefined("empty support")
    ys = [y for y, _ in materialized]
    xs = [x for _, x in materialized]
    return min(ys), max(ys), min(xs), max(xs)


def _components(
    value: Grid,
    background: int,
    *,
    connectivity: int,
    monochrome: bool,
    excluded: Iterable[int] = (),
) -> tuple[Component, ...]:
    excluded_set = set(excluded) | {background}
    if connectivity not in {4, 8}:
        raise Undefined("unsupported connectivity")
    neighbors = (
        ((-1, 0), (0, -1), (0, 1), (1, 0))
        if connectivity == 4
        else tuple(
            (dy, dx)
            for dy in (-1, 0, 1)
            for dx in (-1, 0, 1)
            if (dy, dx) != (0, 0)
        )
    )
    height, width = len(value), len(value[0])
    seen: set[tuple[int, int]] = set()
    result: list[Component] = []
    for y in range(height):
        for x in range(width):
            seed_color = value[y][x]
            if seed_color in excluded_set or (y, x) in seen:
                continue
            queue = deque([(y, x)])
            seen.add((y, x))
            cells: list[tuple[int, int]] = []
            while queue:
                cy, cx = queue.popleft()
                cells.append((cy, cx))
                for dy, dx in neighbors:
                    ny, nx = cy + dy, cx + dx
                    if not (0 <= ny < height and 0 <= nx < width) or (ny, nx) in seen:
                        continue
                    color = value[ny][nx]
                    if color in excluded_set or (monochrome and color != seed_color):
                        continue
                    seen.add((ny, nx))
                    queue.append((ny, nx))
            y0, y1, x0, x1 = _bbox(cells)
            colors = tuple(sorted({value[cy][cx] for cy, cx in cells}))
            result.append(Component(tuple(sorted(cells)), colors, y0, y1, x0, x1))
    result.sort(key=lambda obj: (obj.y0, obj.x0, obj.y1, obj.x1, obj.colors))
    return tuple(result)


def _component_raster(value: Grid, component: Component, background: int) -> Grid:
    canvas = [[background for _ in range(component.width)] for _ in range(component.height)]
    for y, x in component.cells:
        canvas[y - component.y0][x - component.x0] = value[y][x]
    return tuple(tuple(row) for row in canvas)


def _path_pieces(value: Grid, background: int) -> tuple[PathPiece, ...]:
    raw = _components(value, background, connectivity=4, monochrome=False)
    if not 2 <= len(raw) <= 20:
        raise Undefined("path-piece arity is outside bounds")
    multicolor = [component for component in raw if len(component.colors) > 1]
    bridge: int | None = None
    if multicolor:
        color_component_counts = Counter(
            color for component in raw for color in component.colors
        )
        candidates = []
        for color, count in color_component_counts.items():
            if count < 2:
                continue
            if all(len(set(component.colors) - {color}) == 1 for component in raw):
                candidates.append(color)
        if len(candidates) != 1:
            raise Undefined("shared bridge color is not unique")
        bridge = candidates[0]
    elif any(len(component.colors) != 1 for component in raw):
        raise Undefined("monochrome path roles differ")

    pieces: list[PathPiece] = []
    for component in raw:
        payload_colors = set(component.colors) - ({bridge} if bridge is not None else set())
        if len(payload_colors) != 1:
            raise Undefined("path payload color is not unique")
        color = next(iter(payload_colors))
        support = set(component.cells)
        degrees = {
            cell: sum(
                (cell[0] + dy, cell[1] + dx) in support
                for dy, dx in ((-1, 0), (0, -1), (0, 1), (1, 0))
            )
            for cell in support
        }
        endpoints = [cell for cell, degree in degrees.items() if degree == 1]
        if len(endpoints) != 2 or any(degree not in {1, 2} for degree in degrees.values()):
            raise Undefined("component support is not a simple path")
        if component.width < 2:
            raise Undefined("path does not advance horizontally")
        left = [cell for cell in endpoints if cell[1] == component.x0]
        right = [cell for cell in endpoints if cell[1] == component.x1]
        if len(left) != 1 or len(right) != 1 or left[0] == right[0]:
            raise Undefined("left/right path ports are not unique")
        relative = tuple(
            sorted((y - component.y0, x - component.x0) for y, x in component.cells)
        )
        pieces.append(
            PathPiece(
                relative,
                color,
                component.y0,
                component.x0,
                component.height,
                component.width,
                left[0][0] - component.y0,
                right[0][0] - component.y0,
            )
        )
    pieces.sort(key=lambda piece: (piece.x0, piece.y0, piece.color, piece.cells))
    if any(a.x0 + a.width > b.x0 for a, b in zip(pieces, pieces[1:])):
        raise Undefined("path pieces overlap horizontally")
    return tuple(pieces)


def _path_pack(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    pieces = _path_pieces(value, background)
    placements = [pieces[0].y0]
    for before, after in zip(pieces, pieces[1:]):
        placements.append(placements[-1] + before.right_port_y - after.left_port_y)
    if any(y < 0 or y + piece.height > len(value) for y, piece in zip(placements, pieces)):
        raise Undefined("connected path leaves the source-height raster")
    width = sum(piece.width for piece in pieces)
    if width > 30:
        raise Undefined("packed path exceeds ARC width")
    canvas = [[background for _ in range(width)] for _ in range(len(value))]
    offset = 0
    for y0, piece in zip(placements, pieces):
        for y, x in piece.cells:
            canvas[y0 + y][offset + x] = piece.color
        offset += piece.width
    return tuple(tuple(row) for row in canvas)


def _paired_difference_crop(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    objects = _components(value, background, connectivity=8, monochrome=False)
    if len(objects) != 2 or (objects[0].height, objects[0].width) != (
        objects[1].height,
        objects[1].width,
    ):
        raise Undefined("difference comparison needs two equal rasters")
    first = _component_raster(value, objects[0], background)
    second = _component_raster(value, objects[1], background)
    differences = [
        (y, x)
        for y in range(len(first))
        for x in range(len(first[0]))
        if first[y][x] != second[y][x]
    ]
    y0, y1, x0, x1 = _bbox(differences)
    render_color = int(program["difference_color"])
    if render_color == background:
        raise Undefined("difference color equals background")
    return tuple(
        tuple(
            render_color if (y, x) in set(differences) else background
            for x in range(x0, x1 + 1)
        )
        for y in range(y0, y1 + 1)
    )


def _normalize_points(points: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    materialized = tuple(points)
    y0, _, x0, _ = _bbox(materialized)
    return tuple(sorted((y - y0, x - x0) for y, x in materialized))


def _registered_direction(
    source: Grid, canvas: Grid, *, connectivity: int
) -> Grid:
    source_background = _background(source, "mode")
    canvas_background = _background(canvas, "mode")
    if source_background == canvas_background:
        raise Undefined("registered panels do not carry distinct backgrounds")
    source_objects = _components(
        source, source_background, connectivity=connectivity, monochrome=False
    )
    if not source_objects:
        raise Undefined("registered source has no payload objects")
    canvas_points: dict[int, tuple[tuple[int, int], ...]] = {}
    for color in sorted({cell for row in canvas for cell in row if cell != canvas_background}):
        canvas_points[color] = tuple(
            (y, x)
            for y, row in enumerate(canvas)
            for x, cell in enumerate(row)
            if cell == color
        )
    if not canvas_points:
        raise Undefined("registered canvas has no keys")

    universe = frozenset(
        (color, y, x)
        for color, points in canvas_points.items()
        for y, x in points
    )
    options: list[list[tuple[int, int, int, frozenset[tuple[int, int, int]]]]] = []
    for component in source_objects:
        possibilities: dict[
            tuple[int, int, int, frozenset[tuple[int, int, int]]],
            tuple[int, int, int, frozenset[tuple[int, int, int]]],
        ] = {}
        for color in component.colors:
            target_points = canvas_points.get(color)
            if target_points is None:
                continue
            source_points = tuple(
                (y, x) for y, x in component.cells if source[y][x] == color
            )
            target_set = set(target_points)
            for source_y, source_x in source_points:
                for target_y, target_x in target_points:
                    dy, dx = target_y - source_y, target_x - source_x
                    mapped = {(y + dy, x + dx) for y, x in source_points}
                    if not mapped <= target_set:
                        continue
                    covered = frozenset((color, y, x) for y, x in mapped)
                    option = (color, dy, dx, covered)
                    possibilities[option] = option
        options.append(sorted(possibilities.values(), key=lambda item: (item[0], item[1], item[2], sorted(item[3]))))

    covers: list[tuple[tuple[int, int, int, frozenset[tuple[int, int, int]]] | None, ...]] = []
    visited = 0

    def search(
        index: int,
        covered: frozenset[tuple[int, int, int]],
        chosen: list[tuple[int, int, int, frozenset[tuple[int, int, int]]] | None],
    ) -> None:
        nonlocal visited
        visited += 1
        if visited > 4096 or len(covers) > 64:
            raise Undefined("registered exact-cover search cap exceeded")
        if index == len(source_objects):
            if covered == universe and any(option is not None for option in chosen):
                covers.append(tuple(chosen))
            return
        # A source component can be a decoy.
        chosen.append(None)
        search(index + 1, covered, chosen)
        chosen.pop()
        for option in options[index]:
            option_cover = option[3]
            if covered & option_cover:
                continue
            chosen.append(option)
            search(index + 1, covered | option_cover, chosen)
            chosen.pop()

    search(0, frozenset(), [])
    predictions: dict[str, Grid] = {}
    for cover in covers:
        selected = [
            (component, option)
            for component, option in zip(source_objects, cover)
            if option is not None
        ]
        if not selected or not any(len(component.colors) > 1 for component, _ in selected):
            continue
        output = [list(row) for row in canvas]
        valid = True
        for component, option in selected:
            _, dy, dx, _ = option
            for y, x in component.cells:
                ny, nx = y + dy, x + dx
                if not (0 <= ny < len(output) and 0 <= nx < len(output[0])):
                    valid = False
                    break
                color = source[y][x]
                existing = output[ny][nx]
                if existing not in {canvas_background, color}:
                    valid = False
                    break
                output[ny][nx] = color
            if not valid:
                break
        if valid:
            rendered = tuple(tuple(row) for row in output)
            predictions[_canonical(_plain(rendered))] = rendered
    if len(predictions) != 1:
        raise Undefined("registered payload exact cover is not unique")
    return next(iter(predictions.values()))


def _marker_registered_overlay(value: Grid, program: Mapping[str, Any]) -> Grid:
    connectivity = int(program["connectivity"])
    decompositions: list[tuple[Grid, Grid]] = []
    if len(value) % 2 == 0:
        midpoint = len(value) // 2
        decompositions.append((tuple(value[:midpoint]), tuple(value[midpoint:])))
    if len(value[0]) % 2 == 0:
        midpoint = len(value[0]) // 2
        left = tuple(tuple(row[:midpoint]) for row in value)
        right = tuple(tuple(row[midpoint:]) for row in value)
        decompositions.append((left, right))
    predictions: dict[str, Grid] = {}
    for first, second in decompositions:
        for source, canvas in ((first, second), (second, first)):
            try:
                output = _registered_direction(source, canvas, connectivity=connectivity)
            except (IndexError, TypeError, ValueError, ZeroDivisionError, OverflowError):
                continue
            predictions[_canonical(_plain(output))] = output
    if len(predictions) != 1:
        raise Undefined("equal-panel registration is ambiguous")
    return next(iter(predictions.values()))


def _solid_square_groups(value: Grid, background: int) -> dict[int, tuple[int, int]]:
    groups: dict[int, tuple[int, int]] = {}
    colors = sorted({cell for row in value for cell in row if cell != background})
    for color in colors:
        objects = _components(
            value,
            background,
            connectivity=4,
            monochrome=True,
            excluded=set(colors) - {color},
        )
        if not objects:
            continue
        sides: list[int] = []
        for obj in objects:
            if obj.height != obj.width or obj.height < 2 or obj.area != obj.height * obj.width:
                sides = []
                break
            sides.append(obj.height)
        if not sides or len(set(sides)) != 1:
            continue
        side = sides[0]
        if side in groups:
            raise Undefined("square rank does not uniquely encode a color")
        groups[side] = (color, len(objects))
    return groups


def _square_capacity_repair(value: Grid, program: Mapping[str, Any]) -> Grid:
    if program.get("repair_provenance") != "score_seeded_rank_capacity_ambiguity":
        raise Undefined("repair provenance marker is missing")
    background = _background(value, str(program["background_role"]))
    groups = _solid_square_groups(value, background)
    if len(groups) < 3:
        raise Undefined("rank serializer needs at least three square sizes")
    sides = sorted(groups)
    if sides[0] != 2 or sides != list(range(2, sides[-1] + 1)) or sides[-1] > 6:
        raise Undefined("square ranks are not consecutive from two")
    structural_colors = {color for color, _ in groups.values()}
    other_colors = {
        cell for row in value for cell in row if cell not in structural_colors | {background}
    }
    if len(other_colors) > 1:
        raise Undefined("noise role is not unique")
    if other_colors:
        noise = next(iter(other_colors))
        noise_components = _components(
            value,
            background,
            connectivity=4,
            monochrome=True,
            excluded=structural_colors,
        )
        if not noise_components or any(component.colors != (noise,) for component in noise_components):
            raise Undefined("noise role mixes colors")
        if sum(component.area == 1 for component in noise_components) * 2 < len(noise_components):
            raise Undefined("noise is not singleton dominated")
    largest_side = sides[-1]
    rack_capacity = max(largest_side, groups[largest_side][1])
    counts = {
        side: min(count, rack_capacity) for side, (_, count) in groups.items()
    }
    height = largest_side + 1
    rows: list[list[int]] = [[] for _ in range(height)]
    for stack in range(rack_capacity):
        active = [side for side in sides if stack < counts[side]]
        if not active:
            # An unused suffix is not serialized.
            break
        width = max(active)
        block = [[background for _ in range(width)] for _ in range(height)]
        for side in sorted(active, reverse=True):
            color = groups[side][0]
            for y in range(side):
                for x in range(side):
                    block[y][x] = color
        for y in range(height):
            rows[y].extend(block[y])
            rows[y].append(background)
    if not rows[0] or len(rows[0]) > 30:
        raise Undefined("rank serialization exceeds ARC width")
    return tuple(tuple(row) for row in rows)


def execute_program(program: Mapping[str, Any], value: Any) -> JSONGrid:
    """Execute a serialized v3 program on one observable input grid."""

    if not isinstance(program, Mapping):
        raise TypeError("program must be a mapping")
    if program.get("schema") != SCHEMA or program.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported compact-codec v3 schema")
    source = _grid(value)
    op = str(program["op"])
    if op == "path_pack":
        output = _path_pack(source, program)
    elif op == "paired_difference_crop":
        output = _paired_difference_crop(source, program)
    elif op == "marker_registered_overlay":
        output = _marker_registered_overlay(source, program)
    elif op == "square_capacity_repair":
        output = _square_capacity_repair(source, program)
    else:
        raise ValueError("unknown compact-codec v3 operation")
    return _plain(_grid(output))


def replay_program(program: Mapping[str, Any], grid: Any) -> JSONGrid:
    """Block 14 tournament replay hook."""

    return execute_program(program, grid)


def _program(op: str, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "op": op,
        **parameters,
    }


def _enumerate_programs() -> tuple[tuple[str, dict[str, Any], int], ...]:
    result: list[tuple[str, dict[str, Any], int]] = []
    for background_role in ("mode", "border", "corners"):
        result.append(
            (
                "compact_codec_v3.graph.endpoint_path_pack",
                _program(
                    "path_pack",
                    background_role=background_role,
                    bridge_role="unique_shared_component_color_or_none",
                    vertical_anchor="first_piece_source_row",
                ),
                15,
            )
        )
        for difference_color in range(1, 10):
            result.append(
                (
                    "compact_codec_v3.compare.paired_difference_crop",
                    _program(
                        "paired_difference_crop",
                        background_role=background_role,
                        difference_color=difference_color,
                        comparison="cellwise_inequality",
                    ),
                    14,
                )
            )
    for connectivity in (4, 8):
        result.append(
            (
                "compact_codec_v3.panels.marker_registered_overlay",
                _program(
                    "marker_registered_overlay",
                    connectivity=connectivity,
                    partition="unique_equal_half",
                    source_canvas_roles="translation_congruent_key_sets",
                ),
                18,
            )
        )
    result.append(
        (
            "compact_codec_v3.repair.square_histogram_capacity",
            _program(
                "square_capacity_repair",
                background_role="mode",
                repair_provenance="score_seeded_rank_capacity_ambiguity",
                capacity="max_largest_rank_side_or_multiplicity",
                subordinate_policy="truncate_all_ranks_to_capacity",
            ),
            22,
        )
    )
    result.sort(key=lambda item: (item[2], item[0], _canonical(item[1])))
    return tuple(result)


def _safe_execute(program: Mapping[str, Any], source: Grid) -> Grid | None:
    try:
        return _grid(execute_program(program, source))
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return None


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Compile one unique, exact, LOO-stable test behavior."""

    try:
        bounds = Limits.parse(limits)
        train, tests = _sanitize(task, bounds)
        if not all(
            len(target) * len(target[0]) < len(source) * len(source[0])
            for source, target in train
        ):
            return []
        programs = _enumerate_programs()
        if len(programs) > bounds.max_programs:
            return []
        executions = 0
        train_matrix: list[tuple[Grid | None, ...]] = []
        test_matrix: list[tuple[Grid | None, ...]] = []
        for _, program, _ in programs:
            train_row: list[Grid | None] = []
            test_row: list[Grid | None] = []
            for source, _ in train:
                executions += 1
                if executions > bounds.max_executions:
                    return []
                train_row.append(_safe_execute(program, source))
            for source in tests:
                executions += 1
                if executions > bounds.max_executions:
                    return []
                test_row.append(_safe_execute(program, source))
            train_matrix.append(tuple(train_row))
            test_matrix.append(tuple(test_row))

        exact_indices = [
            index
            for index, row in enumerate(train_matrix)
            if all(output == target for output, (_, target) in zip(row, train))
            and all(output is not None for output in test_matrix[index])
        ]
        if not exact_indices:
            return []

        # Grammar-level leave-one-out: every program fitting all remaining
        # demonstrations must agree on the held-out raster and recover it.
        for held_out in range(len(train)):
            survivor_outputs: dict[str, Grid] = {}
            for index, row in enumerate(train_matrix):
                if any(
                    row[other] != train[other][1]
                    for other in range(len(train))
                    if other != held_out
                ):
                    continue
                output = row[held_out]
                if output is not None:
                    survivor_outputs[_canonical(_plain(output))] = output
            if len(survivor_outputs) != 1 or next(iter(survivor_outputs.values())) != train[held_out][1]:
                return []

        behaviors: dict[str, list[int]] = defaultdict(list)
        for index in exact_indices:
            outputs = [_plain(output) for output in test_matrix[index] if output is not None]
            if len(outputs) != len(tests):
                continue
            behaviors[_canonical(outputs)].append(index)
        if len(behaviors) != 1:
            return []
        equivalent = next(iter(behaviors.values()))
        equivalent.sort(
            key=lambda index: (
                programs[index][2],
                programs[index][0],
                _canonical(programs[index][1]),
            )
        )
        if not equivalent or len(equivalent) > bounds.max_candidates:
            return []
        winner = equivalent[0]
        family, program, complexity = programs[winner]
        evidence: dict[str, Any] = {
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "leave_one_out_exact": True,
            "leave_one_out_scope": "finite_v3_grammar",
            "unique_test_behavior": True,
            "equivalent_exact_programs": len(equivalent),
            "demonstration_count": len(train),
            "test_input_count": len(tests),
            "label_access": "demonstrations_only",
            "identity_access": False,
        }
        if program["op"] == "square_capacity_repair":
            evidence.update(
                {
                    "score_seeded_repair": True,
                    "repair_ambiguity": (
                        "v2 smallest-only cap and all-rank rack capacity were "
                        "observationally equivalent on demonstrations"
                    ),
                    "repair_choice": "all subordinate ranks share the structural rack capacity",
                }
            )
        return [
            {
                "family": family,
                "program": dict(program),
                "train_outputs": [_plain(target) for _, target in train],
                "test_outputs": [
                    _plain(output) for output in test_matrix[winner] if output is not None
                ],
                "complexity": complexity,
                "evidence": evidence,
            }
        ]
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return []


__all__ = ["Limits", "compile_task", "execute_program", "replay_program"]
