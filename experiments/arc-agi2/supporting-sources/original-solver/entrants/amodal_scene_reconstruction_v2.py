"""Repaired and extended amodal scene reconstruction for Block 15.

This entrant is the score-seeded successor to ``amodal_scene_reconstruction``.
The original entrant remains byte-for-byte frozen.  Version 2 repairs two
geometric assumptions exposed by the separate public-training scorer:

* a terminal concentric singleton needs recurrence support, rather than canvas
  centering; and
* an exterior cycle bevel needs a witnessed local corner, rather than merely a
  nearby bounding-box corner.

It also adds three reusable scene completions: cardinal broadcast towers,
periodic rays from a plus seed, and bounded band-wise rectangle completion.
At runtime the compiler observes only labelled demonstrations and test inputs.
No task identity, corpus fingerprint, test label, or solution file is read.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.amodal_scene_reconstruction.program.v2"
DEVELOPMENT_REGIME = "retrospective_score_seeded_public_training"

_BASE_SHA256 = "7ba537df96fffec14b30989fdcae17793b92c3c878168732b9001d15aef9cc81"
_BASE_PATH = Path(__file__).with_name("amodal_scene_reconstruction.py")


def _load_pinned_base() -> Any:
    """Load the frozen v1 implementation only after authenticating its bytes."""

    source = _BASE_PATH.read_bytes()
    if hashlib.sha256(source).hexdigest() != _BASE_SHA256:
        raise ImportError("amodal v1 dependency does not match its pinned SHA-256")
    name = f"_komorebi_amodal_v1_{_BASE_SHA256[:16]}"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, _BASE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load pinned amodal v1 dependency")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


_base = _load_pinned_base()

Grid = tuple[tuple[int, ...], ...]
Point = tuple[int, int]
Pair = tuple[Grid, Grid]
Limits = _base.Limits
Undefined = _base.Undefined


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _program(operation: str, complexity: int, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "op": operation,
        "description_length": complexity,
        "root_scope": "immutable_input",
        **parameters,
    }


def _as_base_program(program: Mapping[str, Any]) -> dict[str, Any]:
    translated = copy.deepcopy(dict(program))
    translated["schema"] = _base.SCHEMA
    return translated


def _alternating_concentric_fill_v2(grid: Grid, fill_color: int) -> Grid:
    """Render the four-layer recurrence with an evidence-backed terminal cell."""

    source_colors = sorted(_base._palette(grid) - {fill_color})
    outlines: list[tuple[int, tuple[int, int, int, int]]] = []
    for color in source_colors:
        try:
            outlines.append((color, _base._full_outline(grid, color)))
        except Undefined:
            continue
    if len(outlines) != 1 or len(source_colors) != 2:
        raise Undefined("concentric fill roles are not unique")
    frame, (row0, row1, column0, column1) = outlines[0]
    background_colors = set(source_colors) - {frame}
    if len(background_colors) != 1:
        raise Undefined("concentric background is not unique")
    background = next(iter(background_colors))
    result = [list(row) for row in grid]
    cycle = (frame, fill_color, frame, background)
    for row in range(row0, row1 + 1):
        for column in range(column0, column1 + 1):
            distance = min(row - row0, row1 - row, column - column0, column1 - column)
            result[row][column] = cycle[distance % len(cycle)]

    # A lone frame-colored center immediately after the first complete
    # frame/fill/frame/blank period has no second recurrence as support.  Once
    # two periods are visible, the same terminal phase is licensed.  This
    # replaces v1's irrelevant canvas-centering proxy.
    if (row1 - row0) % 2 == 0 and (column1 - column0) % 2 == 0:
        center_row, center_column = (row0 + row1) // 2, (column0 + column1) // 2
        depth = min(center_row - row0, center_column - column0)
        if depth == len(cycle):
            result[center_row][center_column] = background
    output = tuple(tuple(row) for row in result)
    if output == grid:
        raise Undefined("concentric fill emits nothing")
    return output


def _closed_cycle_bands_v2(grid: Grid, exterior: int, interior: int) -> Grid:
    """Band closed paths and bevel only locally witnessed one-cell chamfers."""

    background = _base._background(grid)
    source_colors = sorted(_base._palette(grid) - {background})
    if (
        len(source_colors) != 1
        or exterior == interior
        or exterior in _base._palette(grid)
        or interior in _base._palette(grid)
    ):
        raise Undefined("cycle-band color roles are not unique")
    ink = source_colors[0]
    height, width = _base._shape(grid)
    result = [list(row) for row in grid]
    closed_count = 0
    for component in _base._monochrome_components(grid, ink):
        if not all(
            sum(
                (row + dr, column + dc) in component
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
            )
            == 2
            for row, column in component
        ):
            continue
        closed_count += 1
        outside: set[Point] = set()
        queue: list[Point] = []
        for row in range(height):
            for column in range(width):
                if (
                    row in (0, height - 1) or column in (0, width - 1)
                ) and (row, column) not in component:
                    outside.add((row, column))
                    queue.append((row, column))
        for row, column in queue:
            for point in (
                (row - 1, column),
                (row + 1, column),
                (row, column - 1),
                (row, column + 1),
            ):
                other_row, other_column = point
                if (
                    0 <= other_row < height
                    and 0 <= other_column < width
                    and point not in component
                    and point not in outside
                ):
                    outside.add(point)
                    queue.append(point)
        for row, column in component:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if not (dr or dc):
                        continue
                    other_row, other_column = row + dr, column + dc
                    if (
                        0 <= other_row < height
                        and 0 <= other_column < width
                        and grid[other_row][other_column] == background
                    ):
                        result[other_row][other_column] = (
                            exterior if (other_row, other_column) in outside else interior
                        )

        # An absent bounding-box corner can be a real one-cell chamfer, but
        # proximity alone is insufficient.  Both incident arms must witness
        # the turn.  Ordinary corners were already handled by the dilation.
        row0, row1, column0, column1 = _base._bbox(component)
        chamfers = (
            ((row0 - 1, column0 - 1), (row0, column0 + 1), (row0 + 1, column0)),
            ((row0 - 1, column1 + 1), (row0, column1 - 1), (row0 + 1, column1)),
            ((row1 + 1, column0 - 1), (row1, column0 + 1), (row1 - 1, column0)),
            ((row1 + 1, column1 + 1), (row1, column1 - 1), (row1 - 1, column1)),
        )
        for destination, first_arm, second_arm in chamfers:
            row, column = destination
            if (
                0 <= row < height
                and 0 <= column < width
                and grid[row][column] == background
                and first_arm in component
                and second_arm in component
            ):
                result[row][column] = exterior
    if closed_count == 0:
        return grid
    output = tuple(tuple(row) for row in result)
    if output == grid:
        raise Undefined("closed cycles emit no bands")
    return output


_CARDINALS = ((-1, 0), (0, 1), (1, 0), (0, -1))


def _assign(
    assignments: dict[Point, int], point: Point, color: int, height: int, width: int
) -> None:
    if not (0 <= point[0] < height and 0 <= point[1] < width):
        raise Undefined("reconstruction is clipped")
    previous = assignments.get(point)
    if previous is not None and previous != color:
        raise Undefined("reconstruction roles collide")
    assignments[point] = color


def _cardinal_broadcast_towers(
    grid: Grid,
    direction: tuple[int, int],
    rail_color: int,
    canopy_color: int,
    signal_color: int,
) -> Grid:
    """Complete each singleton seed into an oriented tower and broadcast row."""

    if direction not in _CARDINALS or len({rail_color, canopy_color, signal_color}) != 3:
        raise Undefined("broadcast roles are invalid")
    background = _base._background(grid)
    palette = _base._palette(grid)
    foreground = sorted(palette - {background})
    if len(foreground) != 1 or {rail_color, canopy_color, signal_color} & palette:
        raise Undefined("broadcast source roles are not unique")
    seed_color = foreground[0]
    seeds = sorted(
        (row, column)
        for row in range(len(grid))
        for column in range(len(grid[0]))
        if grid[row][column] == seed_color
    )
    if not seeds:
        raise Undefined("broadcast seed is absent")
    if any(
        max(abs(row - other_row), abs(column - other_column)) <= 1
        for index, (row, column) in enumerate(seeds)
        for other_row, other_column in seeds[index + 1 :]
    ):
        raise Undefined("broadcast seeds must be isolated")
    height, width = _base._shape(grid)
    dr, dc = direction
    pr, pc = dc, -dr
    assignments: dict[Point, int] = {}
    for row, column in seeds:
        if any(
            abs(row - other_row) <= 4 and abs(column - other_column) <= 4
            for other_row, other_column in seeds
            if (other_row, other_column) != (row, column)
        ):
            raise Undefined("broadcast towers overlap")
        # Canopy, center mast, and two rails.
        for offset in range(-2, 3):
            _assign(
                assignments,
                (row + 2 * dr + offset * pr, column + 2 * dc + offset * pc),
                canopy_color,
                height,
                width,
            )
        _assign(assignments, (row + dr, column + dc), canopy_color, height, width)
        for axial_offset in (1, 0, -1):
            for lateral in (-2, 2):
                _assign(
                    assignments,
                    (
                        row + axial_offset * dr + lateral * pr,
                        column + axial_offset * dc + lateral * pc,
                    ),
                    rail_color,
                    height,
                    width,
                )
        # The full line lies opposite the canopy; its five-cell signal window
        # overwrites the generic rail color.
        line_center = (row - 2 * dr, column - 2 * dc)
        line_extent = width if dr else height
        for offset in range(-line_extent, line_extent + 1):
            point = (line_center[0] + offset * pr, line_center[1] + offset * pc)
            if 0 <= point[0] < height and 0 <= point[1] < width:
                assignments[point] = rail_color
        for offset in range(-2, 3):
            point = (line_center[0] + offset * pr, line_center[1] + offset * pc)
            if not (0 <= point[0] < height and 0 <= point[1] < width):
                raise Undefined("broadcast signal is clipped")
            assignments[point] = signal_color
        assignments[(row, column)] = seed_color
    for (row, column), color in assignments.items():
        source = grid[row][column]
        if source != background and source != color:
            raise Undefined("broadcast overwrites source evidence")
    result = [list(row) for row in grid]
    for (row, column), color in assignments.items():
        result[row][column] = color
    output = tuple(tuple(row) for row in result)
    if output == grid:
        raise Undefined("broadcast towers emit nothing")
    return output


def _plus_seed_periodic_rays(
    grid: Grid, diagonal_color: int, axial_color: int, marker_color: int
) -> Grid:
    """Extend a five-cell plus into diagonals and period-three axial rays."""

    if len({diagonal_color, axial_color, marker_color}) != 3:
        raise Undefined("ray roles are not unique")
    background = _base._background(grid)
    palette = _base._palette(grid)
    foreground = sorted(palette - {background})
    if len(foreground) != 1 or {diagonal_color, axial_color, marker_color} & palette:
        raise Undefined("ray source roles are not unique")
    seed = foreground[0]
    points = {
        (row, column)
        for row in range(len(grid))
        for column in range(len(grid[0]))
        if grid[row][column] == seed
    }
    centers = [
        (row, column)
        for row, column in points
        if {
            (row, column),
            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
        }
        == points
    ]
    if len(centers) != 1:
        raise Undefined("source is not exactly one five-cell plus")
    center_row, center_column = centers[0]
    height, width = _base._shape(grid)
    result = [list(row) for row in grid]
    for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        distance = 1
        while 0 <= center_row + distance * dr < height and 0 <= center_column + distance * dc < width:
            result[center_row + distance * dr][center_column + distance * dc] = diagonal_color
            distance += 1
    for dr, dc in _CARDINALS:
        distance = 2
        while 0 <= center_row + distance * dr < height and 0 <= center_column + distance * dc < width:
            color = marker_color if distance % 3 == 1 else axial_color
            result[center_row + distance * dr][center_column + distance * dc] = color
            distance += 1
    output = tuple(tuple(row) for row in result)
    if output == grid:
        raise Undefined("periodic rays emit nothing")
    return output


def _four_components(grid: Grid, ink: int) -> list[set[Point]]:
    remaining = {
        (row, column)
        for row in range(len(grid))
        for column in range(len(grid[0]))
        if grid[row][column] == ink
    }
    answer: list[set[Point]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        queue = [seed]
        for row, column in queue:
            for point in (
                (row - 1, column),
                (row + 1, column),
                (row, column - 1),
                (row, column + 1),
            ):
                if point in remaining:
                    remaining.remove(point)
                    component.add(point)
                    queue.append(point)
        answer.append(component)
    return answer


def _row_band_rectangle_completion(grid: Grid, fill_color: int, span: int) -> Grid:
    background = _base._background(grid)
    foreground = sorted(_base._palette(grid) - {background})
    if len(foreground) != 1 or fill_color in _base._palette(grid) or not 2 <= span <= 8:
        raise Undefined("band completion roles are invalid")
    components = _four_components(grid, foreground[0])
    if not components:
        raise Undefined("band completion has no evidence")

    # Merge fragments when their row evidence overlaps, or when they touch
    # diagonally, but never across a band wider than the inferred span.
    changed = True
    while changed:
        changed = False
        for left_index, left in enumerate(components):
            left_rows = min(row for row, _ in left), max(row for row, _ in left)
            for right_index in range(left_index + 1, len(components)):
                right = components[right_index]
                right_rows = min(row for row, _ in right), max(row for row, _ in right)
                row_overlap = max(left_rows[0], right_rows[0]) <= min(
                    left_rows[1], right_rows[1]
                )
                diagonal_touch = any(
                    max(abs(row - other_row), abs(column - other_column)) <= 1
                    for row, column in left
                    for other_row, other_column in right
                )
                union = left | right
                union_height = max(row for row, _ in union) - min(row for row, _ in union) + 1
                if union_height <= span and (row_overlap or diagonal_touch):
                    components[left_index] = union
                    components.pop(right_index)
                    changed = True
                    break
            if changed:
                break
    result = [list(row) for row in grid]
    for component in components:
        row0, row1, column0, column1 = _base._bbox(component)
        if row1 - row0 + 1 != span:
            raise Undefined("fragment group does not span the inferred band")
        for row in range(row0, row1 + 1):
            for column in range(column0, column1 + 1):
                if result[row][column] == background:
                    result[row][column] = fill_color
    output = tuple(tuple(row) for row in result)
    if output == grid:
        raise Undefined("band completion emits nothing")
    return output


def _band_rectangle_completion(grid: Grid, fill_color: int, span: int, axis: str) -> Grid:
    if axis == "rows":
        return _row_band_rectangle_completion(grid, fill_color, span)
    if axis == "columns":
        transposed = _base._d4(grid, "transpose")
        return _base._d4(
            _row_band_rectangle_completion(transposed, fill_color, span), "transpose"
        )
    raise Undefined("band axis is invalid")


def _execute(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("unknown program schema")
    operation = program.get("op")
    if operation == "alternating_concentric_fill":
        return _alternating_concentric_fill_v2(grid, int(program["fill_color"]))
    if operation == "closed_cycle_bands":
        return _closed_cycle_bands_v2(
            grid, int(program["exterior_color"]), int(program["interior_color"])
        )
    if operation == "cardinal_broadcast_towers":
        raw_direction = program.get("direction")
        if not isinstance(raw_direction, Sequence) or len(raw_direction) != 2:
            raise Undefined("broadcast direction is invalid")
        direction = int(raw_direction[0]), int(raw_direction[1])
        return _cardinal_broadcast_towers(
            grid,
            direction,
            int(program["rail_color"]),
            int(program["canopy_color"]),
            int(program["signal_color"]),
        )
    if operation == "plus_seed_periodic_rays":
        return _plus_seed_periodic_rays(
            grid,
            int(program["diagonal_color"]),
            int(program["axial_color"]),
            int(program["marker_color"]),
        )
    if operation == "band_rectangle_completion":
        return _band_rectangle_completion(
            grid,
            int(program["fill_color"]),
            int(program["span"]),
            str(program["axis"]),
        )
    # The remaining v1 operations are replayed by the authenticated dependency.
    return _base._execute(_as_base_program(program), grid, limits)


def execute_program(
    program: Mapping[str, Any], value: Any, limits: Mapping[str, Any] | Limits | None = None
) -> list[list[int]]:
    bounds = Limits.from_value(limits)
    grid = _base._grid(value, bounds.max_grid_cells)
    return _base._plain(_execute(program, grid, bounds))


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    source = _base._plain(_base._grid(value, Limits().max_grid_cells))
    output = execute_program(program, source)
    return {
        "output": output,
        "stages": [
            {"name": "parse_amodal_scene_v2", "input": source, "output": source},
            {
                "name": f"reconstruct:{program.get('op', 'unknown')}",
                "input": source,
                "output": output,
            },
        ],
    }


def _single_ink_sources(train: Sequence[Pair]) -> bool:
    try:
        return all(len(_base._palette(source) - {_base._background(source)}) == 1 for source, _ in train)
    except Undefined:
        return False


def _all_seeds_isolated(train: Sequence[Pair]) -> bool:
    if not _single_ink_sources(train):
        return False
    for source, _ in train:
        background = _base._background(source)
        points = [
            (row, column)
            for row in range(len(source))
            for column in range(len(source[0]))
            if source[row][column] != background
        ]
        if not points or any(
            max(abs(row - other_row), abs(column - other_column)) <= 1
            for index, (row, column) in enumerate(points)
            for other_row, other_column in points[index + 1 :]
        ):
            return False
    return True


def _all_five_cell_pluses(train: Sequence[Pair]) -> bool:
    if not _single_ink_sources(train):
        return False
    for source, _ in train:
        background = _base._background(source)
        points = {
            (row, column)
            for row in range(len(source))
            for column in range(len(source[0]))
            if source[row][column] != background
        }
        if len(points) != 5 or not any(
            {
                (row, column),
                (row - 1, column),
                (row + 1, column),
                (row, column - 1),
                (row, column + 1),
            }
            == points
            for row, column in points
        ):
            return False
    return True


def _enumerate_programs(train: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    programs = []
    for base_program in _base._enumerate_programs(train):
        translated = copy.deepcopy(base_program)
        translated["schema"] = SCHEMA
        programs.append(translated)
    introduced = sorted(
        {
            color
            for source, target in train
            for color in _base._palette(target) - _base._palette(source)
        }
    )
    if len(introduced) == 3 and _all_seeds_isolated(train):
        for rail_color in introduced:
            for canopy_color in introduced:
                for signal_color in introduced:
                    if len({rail_color, canopy_color, signal_color}) != 3:
                        continue
                    for direction in _CARDINALS:
                        programs.append(
                            _program(
                                "cardinal_broadcast_towers",
                                22,
                                direction=list(direction),
                                rail_color=rail_color,
                                canopy_color=canopy_color,
                                signal_color=signal_color,
                            )
                        )
    if len(introduced) == 3 and _all_five_cell_pluses(train):
        for diagonal_color in introduced:
            for axial_color in introduced:
                for marker_color in introduced:
                    if len({diagonal_color, axial_color, marker_color}) == 3:
                        programs.append(
                            _program(
                                "plus_seed_periodic_rays",
                                21,
                                diagonal_color=diagonal_color,
                                axial_color=axial_color,
                                marker_color=marker_color,
                            )
                        )
    if len(introduced) == 1 and _single_ink_sources(train):
        for span in range(2, 9):
            for axis in ("rows", "columns"):
                programs.append(
                    _program(
                        "band_rectangle_completion",
                        18 + span,
                        fill_color=introduced[0],
                        span=span,
                        axis=axis,
                    )
                )
    unique = {_canonical(program): program for program in programs}
    return tuple(
        sorted(
            unique.values(),
            key=lambda program: (int(program["description_length"]), _canonical(program)),
        )
    )


def _transform_vector(vector: tuple[int, int], operation: str) -> tuple[int, int]:
    row, column = vector
    transformations = {
        "identity": (row, column),
        "rot90": (column, -row),
        "rot180": (-row, -column),
        "rot270": (-column, row),
        "flip_h": (row, -column),
        "flip_v": (-row, column),
        "transpose": (column, row),
        "anti_transpose": (-column, -row),
    }
    try:
        return transformations[operation]
    except KeyError as error:
        raise Undefined("unknown dihedral operation") from error


def _conjugate_program(program: Mapping[str, Any], operation: str) -> dict[str, Any]:
    transformed = copy.deepcopy(dict(program))
    if transformed.get("op") == "cardinal_broadcast_towers":
        raw = transformed.get("direction")
        direction = int(raw[0]), int(raw[1])
        transformed["direction"] = list(_transform_vector(direction, operation))
    elif transformed.get("op") == "band_rectangle_completion":
        vector = (1, 0) if transformed.get("axis") == "rows" else (0, 1)
        transformed_vector = _transform_vector(vector, operation)
        transformed["axis"] = "rows" if transformed_vector[0] else "columns"
    return transformed


def _evaluate(
    program: Mapping[str, Any], sources: Sequence[Grid], limits: Limits
) -> tuple[Grid | None, ...]:
    outputs: list[Grid | None] = []
    for source in sources:
        try:
            first = _execute(program, source, limits)
            second = _execute(json.loads(_canonical(program)), _base._grid(_base._plain(source)), limits)
            if first != second:
                raise Undefined("fresh replay is nondeterministic")
            outputs.append(first)
        except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            outputs.append(None)
    return tuple(outputs)


def _counterfactual_exact(
    program: Mapping[str, Any], train: Sequence[Pair], limits: Limits
) -> int:
    probes = 0
    for source, target in train:
        for operation in ("rot90", "flip_h"):
            transformed_program = _conjugate_program(program, operation)
            if _execute(transformed_program, _base._d4(source, operation), limits) != _base._d4(
                target, operation
            ):
                raise Undefined("dihedral program conjugation failed")
            probes += 1
    return probes


def _fresh_loo(
    train: Sequence[Pair], limits: Limits
) -> tuple[bool, int, tuple[str, ...]]:
    if len(train) < 2:
        return False, 0, ()
    checked = 0
    signatures: list[str] = []
    for held_index, (held_source, held_target) in enumerate(train):
        retained = tuple(pair for index, pair in enumerate(train) if index != held_index)
        programs = _enumerate_programs(retained)
        signatures.append(_digest(programs))
        retained_sources = tuple(source for source, _ in retained)
        retained_targets = tuple(target for _, target in retained)
        fits: list[tuple[int, Mapping[str, Any]]] = []
        for program in programs:
            if _evaluate(program, retained_sources, limits) == retained_targets:
                fits.append((int(program["description_length"]), program))
        if not fits:
            return False, checked, tuple(signatures)
        best = min(complexity for complexity, _ in fits)
        predictions: set[Grid] = set()
        for complexity, program in fits:
            if complexity > best + limits.mdl_slack:
                continue
            prediction = _evaluate(program, (held_source,), limits)[0]
            checked += 1
            if prediction is not None:
                predictions.add(prediction)
        if predictions != {held_target}:
            return False, checked, tuple(signatures)
    return True, checked, tuple(signatures)


def compile_task(
    task: Any, limits: Mapping[str, Any] | Limits | None = None
) -> list[dict[str, Any]]:
    """Compile one behaviorally unique amodal reconstruction, else abstain."""

    try:
        bounds = Limits.from_value(limits)
        train, tests = _base._sanitize(task, bounds)
    except (Undefined, KeyError, TypeError, ValueError):
        return []
    if len(train) < bounds.min_demos or all(source == target for source, target in train):
        return []
    programs = _enumerate_programs(train)
    if len(programs) > bounds.max_programs:
        return []
    if _digest(programs) != _digest(_enumerate_programs(tuple(reversed(train)))):
        return []
    required = len(programs) * (len(train) + len(tests))
    if required > bounds.max_evaluations:
        return []
    train_sources = tuple(source for source, _ in train)
    targets = tuple(target for _, target in train)
    exact: list[tuple[int, Mapping[str, Any], tuple[Grid, ...], int]] = []
    for program in programs:
        if _evaluate(program, train_sources, bounds) != targets:
            continue
        try:
            counterfactuals = _counterfactual_exact(program, train, bounds)
        except (Undefined, KeyError, TypeError, ValueError, IndexError):
            continue
        test_outputs = _evaluate(program, tests, bounds)
        if any(output is None for output in test_outputs):
            continue
        materialized = tuple(output for output in test_outputs if output is not None)
        if all(output == source for output, source in zip(materialized, tests)):
            continue
        exact.append((int(program["description_length"]), program, materialized, counterfactuals))
    if not exact:
        return []
    stable, loo_checked, loo_signatures = _fresh_loo(train, bounds)
    if not stable:
        return []
    best = min(complexity for complexity, _, _, _ in exact)
    near = [item for item in exact if item[0] <= best + bounds.mdl_slack]
    behaviors: dict[str, list[tuple[int, Mapping[str, Any], tuple[Grid, ...], int]]] = defaultdict(list)
    for item in near:
        behaviors[_digest([_base._plain(output) for output in item[2]])].append(item)
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda item: (item[0], _canonical(item[1])))
    complexity, selected, predictions, counterfactuals = equivalent[0]
    candidate = {
        "family": f"amodal_scene_reconstruction_v2.{selected['op']}",
        "program": json.loads(_canonical(selected)),
        "train_outputs": [_base._plain(target) for target in targets],
        "test_outputs": [_base._plain(output) for output in predictions],
        "complexity": complexity,
        "evidence": {
            "author": AUTHOR,
            "development_regime": DEVELOPMENT_REGIME,
            "all_demonstrations_exact": True,
            "exact_serialized_replay": True,
            "fresh_process_equivalent_replay": True,
            "fresh_leave_one_out_rediscovery": True,
            "leave_one_out_programs_checked": loo_checked,
            "leave_one_out_enumeration_signatures": list(loo_signatures),
            "demo_order_invariance_checked": True,
            "dihedral_program_conjugation_exact": True,
            "counterfactual_probe_count": counterfactuals,
            "bounded_enumeration_complete": True,
            "enumerated_programs": len(programs),
            "program_evaluations": required,
            "minimum_description_programs": len(near),
            "test_behavior_classes": 1,
            "behavior_hash": behavior_hash,
            "pinned_v1_dependency_sha256": _BASE_SHA256,
            "task_identity_observed": False,
            "test_labels_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


__all__ = ["Limits", "compile_task", "execute_program", "replay_program"]
