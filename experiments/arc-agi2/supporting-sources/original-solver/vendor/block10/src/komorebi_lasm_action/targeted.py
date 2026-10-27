"""Finite task-local tools for clear relational ARC mechanisms.

The compilers in this module inspect labelled *training demonstrations* only.
They emit small, target-free programs whose execution depends exclusively on
the current grid.  The public audit executes a frozen program on test inputs
only after exact replay of every training pair.

These families are deliberately structural.  They contain no task IDs,
expected test hashes, or source-grid literals.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
import json
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Sequence

from komorebi_lasm_composition.model import (
    Grid,
    canonical_json,
    canonical_value,
    sha256_record,
    validate_grid,
)


_TARGETED_PARAMETER_KEYS: Mapping[str, frozenset[str]] = MappingProxyType({
    "checkerboard_from_uniform_rows": frozenset(),
    "midpoint_cross": frozenset(("fill_color", "radius")),
    "outward_diagonal_emitters": frozenset(),
    "arrow_guided_reflected_copy": frozenset(),
    "marker_quadrant_fill": frozenset(("marker_color",)),
    "missing_corner_diagonal_rays": frozenset(),
    "diagonal_plus_connect": frozenset(("fill_color",)),
    "exterior_marker_projection": frozenset(),
    "diagonal_tail_extension": frozenset(),
    "reference_shape_recolor": frozenset(("divider_color",)),
    "triangular_cycle_extension": frozenset(),
    "quarter_turn_orbit_completion": frozenset(),
})


def _targeted_integer(
    value: object, name: str, *, minimum: int, maximum: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _validate_targeted_parameters(family: str, parameters: Mapping[str, Any]) -> None:
    expected = _TARGETED_PARAMETER_KEYS.get(family)
    if expected is None:
        raise ValueError(f"unknown targeted tool family {family!r}")
    actual = frozenset(parameters)
    if actual != expected:
        raise ValueError(
            "targeted tool parameter keys differ from schema; "
            f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
        )
    for name in ("fill_color", "marker_color", "divider_color"):
        if name in parameters:
            _targeted_integer(parameters[name], name, minimum=0, maximum=9)
    if "radius" in parameters:
        _targeted_integer(parameters["radius"], "radius", minimum=1, maximum=3)


def _grid(value: Any) -> Grid:
    return validate_grid(value)


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    border = Counter(
        list(grid[0]) + list(grid[-1])
        + [row[0] for row in grid[1:-1]]
        + [row[-1] for row in grid[1:-1]]
    )
    score = {color: (counts[color], border[color]) for color in counts}
    maximum = max(score.values())
    winners = [color for color, value in score.items() if value == maximum]
    if len(winners) != 1:
        raise ValueError("background role is ambiguous")
    return winners[0]


def _positions(grid: Grid, color: int) -> set[tuple[int, int]]:
    return {
        (row_index, column_index)
        for row_index, row in enumerate(grid)
        for column_index, cell in enumerate(row)
        if cell == color
    }


def _bbox(cells: Iterable[tuple[int, int]]) -> tuple[int, int, int, int]:
    points = tuple(cells)
    if not points:
        raise ValueError("a bounding box requires at least one cell")
    rows = [point[0] for point in points]
    columns = [point[1] for point in points]
    return min(rows), max(rows) + 1, min(columns), max(columns) + 1


def _components(
    cells: Iterable[tuple[int, int]], *, diagonal: bool = False,
) -> tuple[frozenset[tuple[int, int]], ...]:
    remaining = set(cells)
    result: list[frozenset[tuple[int, int]]] = []
    directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
    if diagonal:
        directions += ((-1, -1), (-1, 1), (1, -1), (1, 1))
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = deque((seed,))
        component = {seed}
        while queue:
            row, column = queue.popleft()
            for delta_row, delta_column in directions:
                neighbor = row + delta_row, column + delta_column
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        result.append(frozenset(component))
    return tuple(sorted(result, key=lambda item: (min(item), len(item))))


def _replace(grid: Grid, updates: Mapping[tuple[int, int], int]) -> Grid:
    rows = [list(row) for row in grid]
    for (row, column), color in updates.items():
        if not (0 <= row < len(rows) and 0 <= column < len(rows[0])):
            raise ValueError("update lies outside the grid")
        rows[row][column] = int(color)
    return _grid(rows)


def _changed_fill_colors(source: Grid, target: Grid) -> tuple[int, ...]:
    if (len(source), len(source[0])) != (len(target), len(target[0])):
        return ()
    return tuple(sorted({
        target[row][column]
        for row in range(len(source))
        for column in range(len(source[0]))
        if source[row][column] != target[row][column]
    }))


@dataclass(frozen=True, slots=True)
class TargetedToolProgram:
    """One immutable executable task-local tool."""

    family: str
    parameters_json: str = "{}"
    cost: int = 4
    schema_version: int = 1

    def __post_init__(self) -> None:
        if self.family not in _EXECUTORS:
            raise ValueError(f"unknown targeted tool family {self.family!r}")
        try:
            parameters = json.loads(self.parameters_json)
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError("parameters_json must encode canonical JSON") from error
        if not isinstance(parameters, dict) or canonical_json(parameters) != self.parameters_json:
            raise ValueError("parameters_json must encode a canonical object")
        _validate_targeted_parameters(self.family, parameters)
        if isinstance(self.cost, bool) or not isinstance(self.cost, int) or self.cost < 1:
            raise ValueError("cost must be a positive integer")
        if self.schema_version != 1:
            raise ValueError("schema_version must equal 1")

    @property
    def parameters(self) -> Mapping[str, Any]:
        return MappingProxyType(json.loads(self.parameters_json))

    @property
    def semantic_hash(self) -> str:
        return sha256_record({
            "family": self.family,
            "parameters": json.loads(self.parameters_json),
        })

    @property
    def content_hash(self) -> str:
        return sha256_record(self.to_record(include_hash=False))

    def to_record(self, *, include_hash: bool = True) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_action.targeted_tool_program",
            "schema_version": 1,
            "family": self.family,
            "parameters": canonical_value(json.loads(self.parameters_json)),
            "cost": self.cost,
            "semantic_hash": self.semantic_hash,
        }
        if include_hash:
            record["content_hash"] = sha256_record(record)
        return record

    @classmethod
    def create(
        cls, family: str, parameters: Mapping[str, Any] | None = None, *, cost: int = 4,
    ) -> "TargetedToolProgram":
        return cls(family, canonical_json({} if parameters is None else parameters), cost)

    def execute(self, grid: Any) -> Grid:
        return _grid(_EXECUTORS[self.family](_grid(grid), dict(self.parameters)))


@dataclass(frozen=True, slots=True)
class TargetedCompilationResult:
    """Demo-exact targeted programs with complete executor-call accounting."""

    programs: tuple[TargetedToolProgram, ...]
    programs_considered: int
    executions_performed: int
    limit_reached: str = ""
    schema_version: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(self, "programs", tuple(self.programs))
        if not all(isinstance(program, TargetedToolProgram) for program in self.programs):
            raise TypeError("programs must contain TargetedToolProgram records")
        for name in ("programs_considered", "executions_performed"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.limit_reached not in {"", "program_cap"}:
            raise ValueError("unknown targeted compilation limit")
        if self.schema_version != 1:
            raise ValueError("schema_version must equal 1")

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_action.targeted_compilation_result",
            "schema_version": 1,
            "programs": [program.to_record() for program in self.programs],
            "programs_considered": self.programs_considered,
            "executions_performed": self.executions_performed,
            "limit_reached": self.limit_reached,
        }
        record["content_hash"] = sha256_record(record)
        return record


_D4_ACTIONS = ("id", "r90", "r180", "r270", "fliplr", "flipud", "transpose", "anti_transpose")
_D4_INVERSE = {
    "id": "id", "r90": "r270", "r180": "r180", "r270": "r90",
    "fliplr": "fliplr", "flipud": "flipud", "transpose": "transpose",
    "anti_transpose": "anti_transpose",
}


def _d4(grid: Grid, action: str) -> Grid:
    source = _grid(grid)
    if action == "id":
        return source
    if action == "r90":
        return tuple(tuple(source[row][column] for row in range(len(source))) for column in range(len(source[0]) - 1, -1, -1))
    if action == "r180":
        return tuple(tuple(reversed(row)) for row in reversed(source))
    if action == "r270":
        return tuple(tuple(source[row][column] for row in range(len(source) - 1, -1, -1)) for column in range(len(source[0])))
    if action == "fliplr":
        return tuple(tuple(reversed(row)) for row in source)
    if action == "flipud":
        return tuple(reversed(source))
    if action == "transpose":
        return tuple(tuple(source[row][column] for row in range(len(source))) for column in range(len(source[0])))
    if action == "anti_transpose":
        return _d4(_d4(_d4(source, "transpose"), "r180"), "id")
    raise ValueError(f"unknown D4 action {action!r}")


@dataclass(frozen=True, slots=True)
class GaugeTargetedProgram:
    """A targeted tool transported through an exact D4 coordinate chart."""

    gauge: str
    inner: TargetedToolProgram
    schema_version: int = 1

    def __post_init__(self) -> None:
        if self.gauge not in _D4_ACTIONS:
            raise ValueError("unknown D4 gauge")
        if not isinstance(self.inner, TargetedToolProgram):
            raise TypeError("inner must be a TargetedToolProgram")
        if self.schema_version != 1:
            raise ValueError("schema_version must equal 1")

    @property
    def family(self) -> str:
        return self.inner.family

    @property
    def cost(self) -> int:
        return self.inner.cost + (0 if self.gauge == "id" else 2)

    @property
    def semantic_hash(self) -> str:
        return sha256_record({
            "gauge": self.gauge,
            "inner_semantic_hash": self.inner.semantic_hash,
        })

    @property
    def content_hash(self) -> str:
        return sha256_record(self.to_record(include_hash=False))

    def execute(self, grid: Any) -> Grid:
        normalized = _d4(_grid(grid), self.gauge)
        transformed = self.inner.execute(normalized)
        return _d4(transformed, _D4_INVERSE[self.gauge])

    def to_record(self, *, include_hash: bool = True) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_action.gauge_targeted_program",
            "schema_version": 1,
            "gauge": self.gauge,
            "inverse_gauge": _D4_INVERSE[self.gauge],
            "inner": self.inner.to_record(),
            "semantic_hash": self.semantic_hash,
            "cost": self.cost,
        }
        if include_hash:
            record["content_hash"] = sha256_record(record)
        return record


def _checkerboard_from_uniform_rows(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    del parameters
    if len(grid) != 2 or len(grid[0]) < 2:
        raise ValueError("expected exactly two nontrivial rows")
    if any(len(set(row)) != 1 for row in grid) or grid[0][0] == grid[1][0]:
        raise ValueError("rows must be uniform and use distinct colors")
    first, second = grid[0][0], grid[1][0]
    return tuple(
        tuple(first if (row + column) % 2 == 0 else second for column in range(len(grid[0])))
        for row in range(2)
    )


def _midpoint_cross(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    background = _background(grid)
    foreground = [
        (row, column, cell)
        for row, values in enumerate(grid)
        for column, cell in enumerate(values)
        if cell != background
    ]
    if len(foreground) != 2 or foreground[0][2] != foreground[1][2]:
        raise ValueError("expected two equal singleton markers")
    row_a, column_a, _ = foreground[0]
    row_b, column_b, _ = foreground[1]
    if row_a != row_b and column_a != column_b:
        raise ValueError("markers must be axis aligned")
    if (row_a + row_b) % 2 or (column_a + column_b) % 2:
        raise ValueError("marker midpoint must be integral")
    center_row = (row_a + row_b) // 2
    center_column = (column_a + column_b) // 2
    radius = int(parameters["radius"])
    fill = int(parameters["fill_color"])
    updates: dict[tuple[int, int], int] = {}
    for distance in range(-radius, radius + 1):
        updates[center_row + distance, center_column] = fill
        updates[center_row, center_column + distance] = fill
    for position in updates:
        row, column = position
        if not (0 <= row < len(grid) and 0 <= column < len(grid[0])):
            raise ValueError("cross would leave the grid")
        if grid[row][column] != background:
            raise ValueError("cross overlaps a marker")
    return _replace(grid, updates)


def _outward_diagonal_emitters(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    del parameters
    background = _background(grid)
    colors = sorted({cell for row in grid for cell in row} - {background})
    if len(colors) != 2:
        raise ValueError("expected a two-color emitter")
    bottom = max(row for row, values in enumerate(grid) if any(cell != background for cell in values))
    candidates: list[Grid] = []
    for scaffold in colors:
        marker = colors[1] if scaffold == colors[0] else colors[0]
        scaffold_cells = _positions(grid, scaffold)
        marker_cells = _positions(grid, marker)
        if not scaffold_cells or not marker_cells or any(row != bottom for row, _ in marker_cells):
            continue
        top = min(row for row, _ in scaffold_cells)
        top_columns = sorted(column for row, column in scaffold_cells if row == top)
        if not top_columns or max(row for row, _ in scaffold_cells) != bottom:
            continue
        left, right = min(top_columns), max(top_columns)
        updates: dict[tuple[int, int], int] = {}
        step = 1
        while top - step >= 0:
            row = top - step
            for column in {left - step, right + step}:
                if 0 <= column < len(grid[0]):
                    if grid[row][column] != background:
                        raise ValueError("emitter ray collides with foreground")
                    updates[row, column] = marker
            step += 1
        if updates:
            candidates.append(_replace(grid, updates))
    if len(set(candidates)) != 1:
        raise ValueError("emitter binding is absent or ambiguous")
    return candidates[0]


def _arrow_reflected_copy(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    del parameters
    background = _background(grid)
    colors = sorted({cell for row in grid for cell in row} - {background})
    if len(colors) != 2:
        raise ValueError("expected payload and control colors")
    bindings: list[tuple[int, int, set[tuple[int, int]]]] = []
    for control_color in colors:
        control = _positions(grid, control_color)
        y0, y1, x0, x1 = _bbox(control)
        if (y1 - y0, x1 - x0, len(control)) != (3, 3, 5):
            continue
        relative = {(row - y0, column - x0) for row, column in control}
        base = {(1, 0), (1, 1), (1, 2), (2, 1)}
        if relative == base | {(0, 0)}:
            direction = -1
        elif relative == base | {(0, 2)}:
            direction = 1
        else:
            continue
        payload_color = colors[1] if control_color == colors[0] else colors[0]
        payload = _positions(grid, payload_color)
        if not payload or max(row for row, _ in payload) >= y0:
            continue
        bindings.append((direction, payload_color, payload))
    if len(bindings) != 1:
        raise ValueError("arrow binding is absent or ambiguous")
    direction, payload_color, payload = bindings[0]
    y0, y1, x0, x1 = _bbox(payload)
    width = x1 - x0
    destination_left = x1 if direction > 0 else x0 - width
    if destination_left < 0 or destination_left + width > len(grid[0]):
        raise ValueError("reflected copy would leave the grid")
    updates: dict[tuple[int, int], int] = {}
    for row, column in payload:
        relative_column = column - x0
        destination = row, destination_left + (width - 1 - relative_column)
        if grid[destination[0]][destination[1]] != background:
            raise ValueError("reflected copy collides with foreground")
        updates[destination] = payload_color
    return _replace(grid, updates)


def _marker_quadrant_fill(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    height, width = len(grid), len(grid[0])
    if height % 2 or width % 2:
        raise ValueError("quadrant fill requires even dimensions")
    background = _background(grid)
    marker_color = int(parameters["marker_color"])
    markers = _positions(grid, marker_color)
    if len(markers) != 1:
        raise ValueError("expected exactly one quadrant marker")
    marker_row, marker_column = next(iter(markers))
    top = marker_row < height // 2
    left = marker_column < width // 2
    row_start = 0 if top else height // 2
    column_start = 0 if left else width // 2
    result = [[background for _ in range(width)] for _ in range(height)]
    for row in range(row_start, row_start + height // 2):
        for column in range(column_start, column_start + width // 2):
            result[row][column] = marker_color
    return _grid(result)


def _missing_corner_diagonal_rays(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    del parameters
    background = _background(grid)
    colors = {cell for row in grid for cell in row} - {background}
    if len(colors) != 1:
        raise ValueError("expected one foreground color")
    color = next(iter(colors))
    components = _components(_positions(grid, color), diagonal=False)
    if not components:
        raise ValueError("expected at least one L packet")
    updates: dict[tuple[int, int], int] = {}
    for component in components:
        y0, y1, x0, x1 = _bbox(component)
        box = {(row, column) for row in range(y0, y1) for column in range(x0, x1)}
        if (y1 - y0, x1 - x0, len(component)) != (2, 2, 3) or len(box - component) != 1:
            raise ValueError("foreground components must be 2x2 L packets")
        missing_row, missing_column = next(iter(box - component))
        delta_row = -1 if missing_row == y0 else 1
        delta_column = -1 if missing_column == x0 else 1
        row, column = missing_row + delta_row, missing_column + delta_column
        while 0 <= row < len(grid) and 0 <= column < len(grid[0]):
            if grid[row][column] != background:
                raise ValueError("diagonal ray collides with foreground")
            updates[row, column] = color
            row += delta_row
            column += delta_column
    if not updates:
        raise ValueError("no diagonal ray cells were available")
    return _replace(grid, updates)


def _plus_centers(grid: Grid) -> tuple[tuple[int, int, int], ...]:
    background = _background(grid)
    colors = {cell for row in grid for cell in row} - {background}
    if len(colors) != 1:
        raise ValueError("expected one plus color")
    color = next(iter(colors))
    result: list[tuple[int, int, int]] = []
    for component in _components(_positions(grid, color), diagonal=False):
        if len(component) != 5:
            raise ValueError("each packet must be a five-cell plus")
        centers = [
            (row, column)
            for row, column in component
            if all((row + dr, column + dc) in component for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)))
        ]
        if len(centers) != 1:
            raise ValueError("malformed plus packet")
        result.append((centers[0][0], centers[0][1], color))
    if len(result) < 2:
        raise ValueError("expected multiple plus packets")
    return tuple(sorted(result))


def _diagonal_plus_connect(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    centers = _plus_centers(grid)
    fill = int(parameters["fill_color"])
    background = _background(grid)
    updates: dict[tuple[int, int], int] = {}
    for index, (row_a, column_a, _) in enumerate(centers):
        for row_b, column_b, _ in centers[index + 1:]:
            delta_row = row_b - row_a
            delta_column = column_b - column_a
            if abs(delta_row) != abs(delta_column):
                continue
            step_row = 1 if delta_row > 0 else -1
            step_column = 1 if delta_column > 0 else -1
            for step in range(1, abs(delta_row)):
                position = row_a + step * step_row, column_a + step * step_column
                if grid[position[0]][position[1]] == background:
                    updates[position] = fill
    if not updates:
        raise ValueError("no diagonally aligned plus packets")
    return _replace(grid, updates)


def _exterior_marker_projection(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    del parameters
    background = _background(grid)
    colors = sorted({cell for row in grid for cell in row} - {background})
    rectangles: list[tuple[int, int, int, int, int, int]] = []
    for color in colors:
        cells = _positions(grid, color)
        y0, y1, x0, x1 = _bbox(cells)
        area = (y1 - y0) * (x1 - x0)
        if area >= 4 and len(cells) == area:
            rectangles.append((area, color, y0, y1, x0, x1))
    if not rectangles:
        raise ValueError("no solid projection canvas")
    rectangles.sort(reverse=True)
    if len(rectangles) > 1 and rectangles[0][0] == rectangles[1][0]:
        raise ValueError("projection canvas is ambiguous")
    _, canvas_color, y0, y1, x0, x1 = rectangles[0]
    updates: dict[tuple[int, int], int] = {}
    marker_count = 0
    for color in colors:
        if color == canvas_color:
            continue
        components = _components(_positions(grid, color), diagonal=False)
        if any(len(component) != 1 for component in components):
            raise ValueError("exterior markers must be singleton components")
        for component in components:
            row, column = next(iter(component))
            destinations: list[tuple[int, int]] = []
            if y0 <= row < y1 and column < x0:
                destinations.append((row, x0))
            if y0 <= row < y1 and column >= x1:
                destinations.append((row, x1 - 1))
            if x0 <= column < x1 and row < y0:
                destinations.append((y0, column))
            if x0 <= column < x1 and row >= y1:
                destinations.append((y1 - 1, column))
            if len(destinations) != 1:
                raise ValueError("marker is not uniquely aligned with the canvas")
            prior = updates.get(destinations[0])
            if prior is not None and prior != color:
                raise ValueError("projected markers create a color conflict")
            updates[destinations[0]] = color
            marker_count += 1
    if not marker_count:
        raise ValueError("no exterior markers")
    return _replace(grid, updates)


def _diagonal_tail_extension(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    del parameters
    background = _background(grid)
    colors = {cell for row in grid for cell in row} - {background}
    if len(colors) != 1:
        raise ValueError("expected one foreground color")
    color = next(iter(colors))
    cells = _positions(grid, color)
    cores: list[tuple[int, int]] = []
    for row in range(len(grid) - 1):
        for column in range(len(grid[0]) - 1):
            square = {(row, column), (row + 1, column), (row, column + 1), (row + 1, column + 1)}
            if square <= cells:
                cores.append((row, column))
    if len(cores) != 1:
        raise ValueError("expected one 2x2 core")
    core_row, core_column = cores[0]
    core = {
        (core_row, core_column), (core_row + 1, core_column),
        (core_row, core_column + 1), (core_row + 1, core_column + 1),
    }
    tail_specs = {
        (core_row - 1, core_column - 1): (-1, -1),
        (core_row - 1, core_column + 2): (-1, 1),
        (core_row + 2, core_column - 1): (1, -1),
        (core_row + 2, core_column + 2): (1, 1),
    }
    tails = cells - core
    if not tails or any(tail not in tail_specs for tail in tails):
        raise ValueError("foreground outside the core must be a diagonal tail")
    updates: dict[tuple[int, int], int] = {}
    for tail in tails:
        delta_row, delta_column = tail_specs[tail]
        row, column = tail[0] + delta_row, tail[1] + delta_column
        while 0 <= row < len(grid) and 0 <= column < len(grid[0]):
            if grid[row][column] != background:
                raise ValueError("tail ray collides with foreground")
            updates[row, column] = color
            row += delta_row
            column += delta_column
    if not updates:
        raise ValueError("tails cannot be extended")
    return _replace(grid, updates)


def _normalized_shape(cells: Iterable[tuple[int, int]]) -> frozenset[tuple[int, int]]:
    points = tuple(cells)
    y0, _, x0, _ = _bbox(points)
    return frozenset((row - y0, column - x0) for row, column in points)


def _reference_shape_recolor(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    """Recolor objects matching a template isolated by an L-shaped key."""

    background = _background(grid)
    divider_color = int(parameters["divider_color"])
    divider = _positions(grid, divider_color)
    if not divider:
        raise ValueError("divider color is absent")
    bindings: list[tuple[int, int]] = []
    height, width = len(grid), len(grid[0])
    # The four orientations are represented by reflecting coordinates into a
    # top-left key frame.  Store the axis reflections as booleans.
    for flip_rows in (False, True):
        for flip_columns in (False, True):
            transformed = {
                ((height - 1 - row) if flip_rows else row,
                 (width - 1 - column) if flip_columns else column)
                for row, column in divider
            }
            row_candidates = sorted({row for row, _ in transformed})
            column_candidates = sorted({column for _, column in transformed})
            for corner_row in row_candidates:
                for corner_column in column_candidates:
                    expected = (
                        {(corner_row, column) for column in range(corner_column + 1)}
                        | {(row, corner_column) for row in range(corner_row + 1)}
                    )
                    if corner_row >= 2 and corner_column >= 2 and transformed == expected:
                        bindings.append((int(flip_rows), int(flip_columns)))
    if len(bindings) != 1:
        raise ValueError("L-shaped reference divider is absent or ambiguous")
    flip_rows, flip_columns = (bool(value) for value in bindings[0])
    transformed_divider = {
        ((height - 1 - row) if flip_rows else row,
         (width - 1 - column) if flip_columns else column)
        for row, column in divider
    }
    corner_row = max(row for row, _ in transformed_divider)
    corner_column = max(column for _, column in transformed_divider)

    def transform(point: tuple[int, int]) -> tuple[int, int]:
        row, column = point
        return (
            (height - 1 - row) if flip_rows else row,
            (width - 1 - column) if flip_columns else column,
        )

    reference_cells = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if transform((row, column))[0] < corner_row
        and transform((row, column))[1] < corner_column
        and grid[row][column] not in (background, divider_color)
    }
    reference_components = _components(reference_cells, diagonal=False)
    if len(reference_components) != 1:
        raise ValueError("key region must contain one reference object")
    reference = reference_components[0]
    reference_shape = _normalized_shape(reference)

    matches: list[frozenset[tuple[int, int]]] = []
    for color in sorted({cell for row in grid for cell in row} - {background, divider_color}):
        for component in _components(_positions(grid, color), diagonal=False):
            if component != reference and _normalized_shape(component) == reference_shape:
                matches.append(component)
    if not matches:
        raise ValueError("no object matches the reference shape")
    updates = {position: divider_color for component in matches for position in component}
    return _replace(grid, updates)


def _triangular_cycle_extension(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    """Continue a colored prefix at positions 0,1,3,6,... across one row."""

    del parameters
    background = _background(grid)
    occupied_rows = [
        row for row, values in enumerate(grid)
        if any(cell != background for cell in values)
    ]
    if len(occupied_rows) != 1:
        raise ValueError("expected one active sequence row")
    active_row = occupied_rows[0]
    positions = [
        column for column, cell in enumerate(grid[active_row])
        if cell != background
    ]
    if len(positions) < 2:
        raise ValueError("expected a nontrivial triangular prefix")
    expected_prefix = [index * (index + 1) // 2 for index in range(len(positions))]
    if positions != expected_prefix:
        raise ValueError("occupied cells are not an initial triangular sequence")
    colors = [grid[active_row][column] for column in positions]
    updates: dict[tuple[int, int], int] = {}
    index = len(positions)
    while True:
        column = index * (index + 1) // 2
        if column >= len(grid[0]):
            break
        updates[active_row, column] = colors[index % len(colors)]
        index += 1
    if not updates:
        raise ValueError("triangular sequence already reaches the boundary")
    return _replace(grid, updates)


def _quarter_turn_orbit_completion(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    """Complete colored quarter-turn orbits around a filled symmetric square core."""

    del parameters
    background = _background(grid)
    height, width = len(grid), len(grid[0])
    foreground = {
        (row, column)
        for row, values in enumerate(grid)
        for column, cell in enumerate(values)
        if cell != background
    }
    candidates: list[tuple[int, int, int]] = []
    for size in range(2, min(height, width, 8) + 1):
        for y0 in range(height - size + 1):
            for x0 in range(width - size + 1):
                square = {
                    (row, column)
                    for row in range(y0, y0 + size)
                    for column in range(x0, x0 + size)
                }
                if not square < foreground:
                    continue
                pattern = tuple(
                    tuple(grid[y0 + row][x0 + column] for column in range(size))
                    for row in range(size)
                )
                if any(_d4(pattern, action) != pattern for action in _D4_ACTIONS):
                    continue
                candidates.append((size, y0, x0))
    if not candidates:
        raise ValueError("no filled D4-symmetric core")
    maximum = max(size for size, _, _ in candidates)
    maximal = [(size, y0, x0) for size, y0, x0 in candidates if size == maximum]
    if len(maximal) != 1:
        raise ValueError("symmetric core is ambiguous")
    size, y0, x0 = maximal[0]
    center_row_twice = 2 * y0 + size - 1
    center_column_twice = 2 * x0 + size - 1
    updates: dict[tuple[int, int], int] = {}
    transforms = (
        lambda row, column: (row, column),
        lambda row, column: (-column, row),
        lambda row, column: (-row, -column),
        lambda row, column: (column, -row),
    )
    for row, column in foreground:
        relative_row = 2 * row - center_row_twice
        relative_column = 2 * column - center_column_twice
        color = grid[row][column]
        for transform in transforms:
            transformed_row, transformed_column = transform(relative_row, relative_column)
            destination_row_twice = center_row_twice + transformed_row
            destination_column_twice = center_column_twice + transformed_column
            if destination_row_twice % 2 or destination_column_twice % 2:
                raise ValueError("quarter-turn orbit leaves the integer lattice")
            destination = destination_row_twice // 2, destination_column_twice // 2
            if not (0 <= destination[0] < height and 0 <= destination[1] < width):
                raise ValueError("quarter-turn orbit leaves the grid")
            existing = updates.get(destination, grid[destination[0]][destination[1]])
            if existing not in (background, color):
                raise ValueError("quarter-turn orbit creates a color conflict")
            updates[destination] = color
    if all(grid[row][column] == color for (row, column), color in updates.items()):
        raise ValueError("quarter-turn orbit is already complete")
    return _replace(grid, updates)


_EXECUTORS: dict[str, Callable[[Grid, Mapping[str, Any]], Grid]] = {
    "checkerboard_from_uniform_rows": _checkerboard_from_uniform_rows,
    "midpoint_cross": _midpoint_cross,
    "outward_diagonal_emitters": _outward_diagonal_emitters,
    "arrow_guided_reflected_copy": _arrow_reflected_copy,
    "marker_quadrant_fill": _marker_quadrant_fill,
    "missing_corner_diagonal_rays": _missing_corner_diagonal_rays,
    "diagonal_plus_connect": _diagonal_plus_connect,
    "exterior_marker_projection": _exterior_marker_projection,
    "diagonal_tail_extension": _diagonal_tail_extension,
    "reference_shape_recolor": _reference_shape_recolor,
    "triangular_cycle_extension": _triangular_cycle_extension,
    "quarter_turn_orbit_completion": _quarter_turn_orbit_completion,
}


def execute_targeted_tool(program: TargetedToolProgram, grid: Any) -> Grid:
    if not isinstance(program, TargetedToolProgram):
        raise TypeError("program must be a TargetedToolProgram")
    return program.execute(grid)


def _same_shape_pair(pair: Mapping[str, Any]) -> tuple[Grid, Grid]:
    source = _grid(pair["input"])
    target = _grid(pair["output"])
    if (len(source), len(source[0])) != (len(target), len(target[0])):
        raise ValueError("targeted tools require shape preservation")
    return source, target


def _candidate_specs(training: Sequence[tuple[Grid, Grid]]) -> Iterable[TargetedToolProgram]:
    yield TargetedToolProgram.create("checkerboard_from_uniform_rows", cost=3)
    yield TargetedToolProgram.create("outward_diagonal_emitters", cost=4)
    yield TargetedToolProgram.create("arrow_guided_reflected_copy", cost=5)
    yield TargetedToolProgram.create("missing_corner_diagonal_rays", cost=4)
    yield TargetedToolProgram.create("exterior_marker_projection", cost=5)
    yield TargetedToolProgram.create("diagonal_tail_extension", cost=4)
    yield TargetedToolProgram.create("triangular_cycle_extension", cost=4)
    yield TargetedToolProgram.create("quarter_turn_orbit_completion", cost=5)

    fill_sets = [_changed_fill_colors(source, target) for source, target in training]
    common_fills = set(fill_sets[0]) if fill_sets else set()
    for fills in fill_sets[1:]:
        common_fills &= set(fills)
    for fill in sorted(common_fills):
        for radius in range(1, 4):
            yield TargetedToolProgram.create(
                "midpoint_cross", {"fill_color": fill, "radius": radius}, cost=4,
            )
        yield TargetedToolProgram.create(
            "diagonal_plus_connect", {"fill_color": fill}, cost=5,
        )
        yield TargetedToolProgram.create(
            "reference_shape_recolor", {"divider_color": fill}, cost=5,
        )

    output_foregrounds: list[set[int]] = []
    for source, target in training:
        try:
            background = _background(source)
        except ValueError:
            output_foregrounds = []
            break
        output_foregrounds.append({cell for row in target for cell in row} - {background})
    common_output = set.intersection(*output_foregrounds) if output_foregrounds else set()
    for marker_color in sorted(common_output):
        yield TargetedToolProgram.create(
            "marker_quadrant_fill", {"marker_color": marker_color}, cost=4,
        )


def compile_targeted_tools_traced(
    task: Mapping[str, Any], *, budget: int = 256,
) -> TargetedCompilationResult:
    """Return exact tools and count every attempted demonstration execution."""

    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
        raise ValueError("budget must be a positive integer")
    raw_training = task.get("train")
    if not isinstance(raw_training, Sequence) or isinstance(raw_training, (str, bytes)) or not raw_training:
        raise ValueError("task must contain nonempty training demonstrations")
    try:
        training = tuple(_same_shape_pair(pair) for pair in raw_training)
    except ValueError:
        return TargetedCompilationResult((), 0, 0)
    exact: dict[str, TargetedToolProgram] = {}
    considered = 0
    executions = 0
    limit_reached = ""
    for program in _candidate_specs(training):
        if considered >= budget:
            limit_reached = "program_cap"
            break
        considered += 1
        outputs: list[Grid] = []
        failed = False
        for source, _ in training:
            executions += 1
            try:
                outputs.append(program.execute(source))
            except (KeyError, TypeError, ValueError, OverflowError):
                failed = True
                break
        if failed:
            continue
        if tuple(outputs) == tuple(target for _, target in training):
            exact.setdefault(program.semantic_hash, program)
    programs = tuple(sorted(
        exact.values(), key=lambda item: (item.cost, item.family, item.parameters_json),
    ))
    return TargetedCompilationResult(
        programs=programs,
        programs_considered=considered,
        executions_performed=executions,
        limit_reached=limit_reached,
    )


def compile_targeted_tools(task: Mapping[str, Any], *, budget: int = 256) -> tuple[TargetedToolProgram, ...]:
    """Return every finite tool that exactly replays all demonstrations."""

    return compile_targeted_tools_traced(task, budget=budget).programs


def execute_targeted_candidates(
    programs: Sequence[TargetedToolProgram], test_inputs: Sequence[Any],
) -> tuple[tuple[Grid, ...], ...]:
    """Execute frozen programs and quotient them by complete test behavior."""

    inputs = tuple(_grid(grid) for grid in test_inputs)
    behaviors: dict[str, tuple[Grid, ...]] = {}
    for program in programs:
        try:
            outputs = tuple(program.execute(grid) for grid in inputs)
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        behaviors.setdefault(sha256_record(outputs), outputs)
    return tuple(behaviors[key] for key in sorted(behaviors))


def compile_gauge_targeted_tools(
    task: Mapping[str, Any], *, budget_per_gauge: int = 256,
) -> tuple[GaugeTargetedProgram, ...]:
    """Compile the finite D4 orbit of every targeted tool.

    Training input and output grids are transformed together.  Test inputs are
    not touched during compilation, and execution applies the exact inverse
    chart after the inner program.
    """

    raw_training = task.get("train")
    if not isinstance(raw_training, Sequence) or isinstance(raw_training, (str, bytes)) or not raw_training:
        raise ValueError("task must contain nonempty training demonstrations")
    exact: dict[str, GaugeTargetedProgram] = {}
    for gauge in _D4_ACTIONS:
        try:
            transformed_task = {
                "train": [
                    {
                        "input": [list(row) for row in _d4(_grid(pair["input"]), gauge)],
                        "output": [list(row) for row in _d4(_grid(pair["output"]), gauge)],
                    }
                    for pair in raw_training
                ]
            }
        except (KeyError, TypeError, ValueError):
            continue
        for inner in compile_targeted_tools(transformed_task, budget=budget_per_gauge):
            program = GaugeTargetedProgram(gauge, inner)
            try:
                if all(program.execute(pair["input"]) == _grid(pair["output"]) for pair in raw_training):
                    exact.setdefault(program.semantic_hash, program)
            except (KeyError, TypeError, ValueError, OverflowError):
                continue
    return tuple(sorted(exact.values(), key=lambda item: (item.cost, item.family, item.gauge, item.semantic_hash)))


def execute_gauge_targeted_candidates(
    programs: Sequence[GaugeTargetedProgram], test_inputs: Sequence[Any],
) -> tuple[tuple[Grid, ...], ...]:
    inputs = tuple(_grid(grid) for grid in test_inputs)
    behaviors: dict[str, tuple[Grid, ...]] = {}
    for program in programs:
        try:
            outputs = tuple(program.execute(grid) for grid in inputs)
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        behaviors.setdefault(sha256_record(outputs), outputs)
    return tuple(behaviors[key] for key in sorted(behaviors))


__all__ = [
    "TargetedCompilationResult",
    "TargetedToolProgram",
    "GaugeTargetedProgram",
    "compile_gauge_targeted_tools",
    "compile_targeted_tools",
    "compile_targeted_tools_traced",
    "execute_gauge_targeted_candidates",
    "execute_targeted_candidates",
    "execute_targeted_tool",
]
