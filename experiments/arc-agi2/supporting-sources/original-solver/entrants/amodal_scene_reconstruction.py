"""Amodal scene and latent-field reconstruction programs for Block 15.

The entrant reconstructs structures that are only partially visible in the
input: translation lattices behind damage masks, recursively substituted
wallpapers, nested rectangle stacks, sparse symmetric frames, and concentric
layers.  Each serialized program is task-identity blind and reads labelled
demonstrations plus test *inputs* only.  Compilation requires exact
demonstration replay, isolated leave-one-demonstration-out re-proposal,
dihedral counterfactual replay, deterministic execution, and one minimum-MDL
test behavior.  Unsupported or ambiguous scenes abstain.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Point = tuple[int, int]
Pair = tuple[Grid, Grid]

AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.amodal_scene_reconstruction.program.v1"


class Undefined(ValueError):
    """A role, reconstruction, or unique causal ordering is undefined."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 20
    max_programs: int = 64
    max_evaluations: int = 20_000
    max_lattice_vectors: int = 80
    max_lattice_pairs: int = 4_000
    max_candidates: int = 1
    min_demos: int = 2
    mdl_slack: int = 0

    @classmethod
    def from_value(cls, raw: Any) -> "Limits":
        if isinstance(raw, cls):
            return raw
        if raw is None:
            return cls()
        if not isinstance(raw, Mapping):
            raise Undefined("limits must be a mapping")
        defaults = cls()
        aliases = {"candidate_cap": "max_candidates"}
        ceilings = {
            "max_grid_cells": 3_600,
            "max_examples": 40,
            "max_programs": 256,
            "max_evaluations": 200_000,
            "max_lattice_vectors": 256,
            "max_lattice_pairs": 30_000,
            "max_candidates": 1,
            "min_demos": 10,
            "mdl_slack": 3,
        }
        values: dict[str, int] = {}
        for name, ceiling in ceilings.items():
            alias = next((key for key, target in aliases.items() if target == name), None)
            value = raw.get(name, raw.get(alias, getattr(defaults, name)))
            if isinstance(value, bool) or not isinstance(value, int):
                raise Undefined("finite limits must be integers")
            minimum = 0 if name == "mdl_slack" else 1
            if value < minimum:
                raise Undefined("finite limit is below its minimum")
            values[name] = min(value, ceiling)
        unknown = set(raw) - set(ceilings) - set(aliases) - {
            "max_replay_calls",
            "max_replay_stages",
            "max_total_candidates",
            "max_trace_bytes",
            "time_limit",
            "time_limit_seconds",
        }
        if unknown:
            raise Undefined("unknown finite limit")
        return cls(**values)


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


def _grid(value: Any, max_cells: int = 900) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty row sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if (
            not isinstance(raw_row, Sequence)
            or isinstance(raw_row, (str, bytes))
            or not raw_row
        ):
            raise Undefined("grid row is invalid")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif width != len(row):
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > max_cells:
        raise Undefined("grid exceeds the cell bound")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    raw_train, raw_test = task.get("train"), task.get("test")
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not raw_train
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not raw_test
        or len(raw_train) + len(raw_test) > limits.max_examples
    ):
        raise Undefined("task needs bounded nonempty train and test splits")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("training example is invalid")
        train.append(
            (
                _grid(example.get("input"), limits.max_grid_cells),
                _grid(example.get("output"), limits.max_grid_cells),
            )
        )
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        # Deliberately access only the input member of test records.
        tests.append(_grid(example.get("input"), limits.max_grid_cells))
    return tuple(train), tuple(tests)


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    peak = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == peak)
    if len(winners) != 1:
        raise Undefined("background mode is tied")
    return winners[0]


def _palette(grid: Grid) -> frozenset[int]:
    return frozenset(cell for row in grid for cell in row)


def _bbox(points: Iterable[Point]) -> tuple[int, int, int, int]:
    cells = tuple(points)
    if not cells:
        raise Undefined("empty support")
    return (
        min(row for row, _ in cells),
        max(row for row, _ in cells),
        min(column for _, column in cells),
        max(column for _, column in cells),
    )


def _d4(grid: Grid, operation: str) -> Grid:
    if operation == "identity":
        return grid
    if operation == "rot90":
        height, width = _shape(grid)
        return tuple(
            tuple(grid[height - 1 - row][column] for row in range(height))
            for column in range(width)
        )
    if operation == "rot180":
        return _d4(_d4(grid, "rot90"), "rot90")
    if operation == "rot270":
        return _d4(_d4(grid, "rot180"), "rot90")
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in grid)
    if operation == "flip_v":
        return tuple(reversed(grid))
    if operation == "transpose":
        return tuple(tuple(grid[row][column] for row in range(len(grid))) for column in range(len(grid[0])))
    if operation == "anti_transpose":
        return _d4(_d4(grid, "transpose"), "rot180")
    raise Undefined("unknown dihedral operation")


_D4 = (
    "identity",
    "rot90",
    "rot180",
    "rot270",
    "flip_h",
    "flip_v",
    "transpose",
    "anti_transpose",
)
_D4_INVERSE = {
    "identity": "identity",
    "rot90": "rot270",
    "rot180": "rot180",
    "rot270": "rot90",
    "flip_h": "flip_h",
    "flip_v": "flip_v",
    "transpose": "transpose",
    "anti_transpose": "anti_transpose",
}


def _oriented_unique(grid: Grid, core: Any) -> Grid:
    outputs: dict[str, Grid] = {}
    for operation in _D4:
        try:
            transformed = _d4(grid, operation)
            result = core(transformed)
            restored = _d4(result, _D4_INVERSE[operation])
            outputs[_digest(restored)] = restored
        except (Undefined, KeyError, TypeError, ValueError, IndexError):
            continue
    if len(outputs) != 1:
        raise Undefined("oriented reconstruction is absent or behaviorally ambiguous")
    return next(iter(outputs.values()))


class _UnionFind:
    def __init__(self, grid: Grid, mask: int) -> None:
        height, width = _shape(grid)
        size = height * width
        self.parent = list(range(size))
        self.color: list[int | None] = [None] * size
        for row in range(height):
            for column in range(width):
                value = grid[row][column]
                if value != mask:
                    self.color[row * width + column] = value

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> bool:
        left, right = self.find(left), self.find(right)
        if left == right:
            return True
        left_color, right_color = self.color[left], self.color[right]
        if left_color is not None and right_color is not None and left_color != right_color:
            return False
        if left > right:
            left, right = right, left
            left_color, right_color = right_color, left_color
        self.parent[right] = left
        self.color[left] = left_color if left_color is not None else right_color
        return True


def _translation_vectors(grid: Grid, mask: int, limits: Limits) -> tuple[tuple[int, int, int], ...]:
    height, width = _shape(grid)
    known = sum(cell != mask for row in grid for cell in row)
    minimum_support = max(6, known // 25)
    vectors: list[tuple[int, int, int]] = []
    for dr in range(height):
        for dc in range(-(width - 1), width):
            if dr == 0 and dc <= 0:
                continue
            support = 0
            compatible = True
            for row in range(height):
                other_row = row + dr
                if not 0 <= other_row < height:
                    continue
                for column in range(width):
                    other_column = column + dc
                    if not 0 <= other_column < width:
                        continue
                    left, right = grid[row][column], grid[other_row][other_column]
                    if left != mask and right != mask:
                        support += 1
                        if left != right:
                            compatible = False
                            break
                if not compatible:
                    break
            if compatible and support >= minimum_support:
                vectors.append((dr, dc, support))
    vectors.sort(key=lambda item: (abs(item[0]) + abs(item[1]), -item[2], item))
    return tuple(vectors[: limits.max_lattice_vectors])


def _lattice_fill(grid: Grid, mask: int, limits: Limits) -> Grid:
    if all(cell != mask for row in grid for cell in row):
        raise Undefined("mask is absent")
    height, width = _shape(grid)
    vectors = _translation_vectors(grid, mask, limits)
    pairs: list[tuple[int, int, int, tuple[int, int, int], tuple[int, int, int]]] = []
    for index, left in enumerate(vectors):
        for right in vectors[index + 1 :]:
            determinant = abs(left[0] * right[1] - left[1] * right[0])
            if determinant:
                length = abs(left[0]) + abs(left[1]) + abs(right[0]) + abs(right[1])
                pairs.append((determinant, length, -(left[2] + right[2]), left, right))
    pairs.sort()
    if len(pairs) > limits.max_lattice_pairs:
        pairs = pairs[: limits.max_lattice_pairs]
    behaviors: dict[str, Grid] = {}
    best_metric: tuple[int, int, int] | None = None
    for determinant, length, support, left, right in pairs:
        metric = determinant, length, support
        if best_metric is not None and metric != best_metric:
            break
        union_find = _UnionFind(grid, mask)
        compatible = True
        for dr, dc, _ in (left, right):
            for row in range(height):
                other_row = row + dr
                if not 0 <= other_row < height:
                    continue
                for column in range(width):
                    other_column = column + dc
                    if 0 <= other_column < width and not union_find.union(
                        row * width + column, other_row * width + other_column
                    ):
                        compatible = False
                        break
                if not compatible:
                    break
            if not compatible:
                break
        if not compatible:
            continue
        rows: list[tuple[int, ...]] = []
        for row in range(height):
            result_row: list[int] = []
            for column in range(width):
                root = union_find.find(row * width + column)
                color = union_find.color[root]
                if color is None:
                    compatible = False
                    break
                result_row.append(color)
            if not compatible:
                break
            rows.append(tuple(result_row))
        if not compatible:
            continue
        output = tuple(rows)
        if output == grid:
            continue
        if best_metric is None:
            best_metric = metric
        behaviors[_digest(output)] = output
    if len(behaviors) != 1:
        raise Undefined("minimum lattice basis is absent or behaviorally ambiguous")
    return next(iter(behaviors.values()))


def _substitution_wallpaper_corner(grid: Grid) -> Grid:
    background = _background(grid)
    height, width = _shape(grid)
    foreground = {
        grid[row][column]
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background
    }
    if len(foreground) != 2:
        raise Undefined("wallpaper seed needs primary and substitution colors")
    detections: list[tuple[int, int, int, int]] = []
    for core_height in range(1, height):
        for core_width in range(1, width):
            border = {
                *(grid[core_height][column] for column in range(core_width + 1)),
                *(grid[row][core_width] for row in range(core_height + 1)),
            }
            if len(border) != 1:
                continue
            substitution = next(iter(border))
            if substitution == background:
                continue
            core_palette = {
                grid[row][column]
                for row in range(core_height)
                for column in range(core_width)
            }
            primary_colors = core_palette - {background}
            if len(primary_colors) != 1:
                continue
            primary = next(iter(primary_colors))
            if primary == substitution:
                continue
            if any(
                grid[row][column] != background
                for row in range(height)
                for column in range(width)
                if row > core_height or column > core_width
            ):
                continue
            detections.append((core_height, core_width, primary, substitution))
    if len(detections) != 1:
        raise Undefined("wallpaper seed framing is ambiguous")
    core_height, core_width, primary, substitution = detections[0]
    support = tuple(
        tuple(grid[row][column] == primary for column in range(core_width))
        for row in range(core_height)
    )
    tile_height, tile_width = core_height * core_height, core_width * core_width
    tile = [[background for _ in range(tile_width)] for _ in range(tile_height)]
    for outer_row in range(core_height):
        for outer_column in range(core_width):
            color = primary if support[outer_row][outer_column] else substitution
            for inner_row in range(core_height):
                for inner_column in range(core_width):
                    if support[inner_row][inner_column]:
                        tile[outer_row * core_height + inner_row][
                            outer_column * core_width + inner_column
                        ] = color
    return tuple(
        tuple(tile[row % tile_height][column % tile_width] for column in range(width))
        for row in range(height)
    )


def _substitution_wallpaper(grid: Grid) -> Grid:
    return _oriented_unique(grid, _substitution_wallpaper_corner)


def _full_outline(grid: Grid, color: int) -> tuple[int, int, int, int]:
    points = {
        (row, column)
        for row in range(len(grid))
        for column in range(len(grid[0]))
        if grid[row][column] == color
    }
    bounds = _bbox(points)
    row0, row1, column0, column1 = bounds
    perimeter = {
        (row, column)
        for row in range(row0, row1 + 1)
        for column in range(column0, column1 + 1)
        if row in (row0, row1) or column in (column0, column1)
    }
    if points != perimeter or row1 - row0 < 2 or column1 - column0 < 2:
        raise Undefined("source is not one complete rectangular outline")
    return bounds


def _alternating_concentric_fill(grid: Grid, fill_color: int) -> Grid:
    source_colors = sorted(_palette(grid) - {fill_color})
    outlines: list[tuple[int, tuple[int, int, int, int]]] = []
    for color in source_colors:
        try:
            outlines.append((color, _full_outline(grid, color)))
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
    # A lone terminal cell is supported only when the source frame and canvas
    # share a center.  Off-centre odd frames leave that uncorroborated cell as
    # background; the surrounding blank ring remains the stopping witness.
    if (row1 - row0) % 2 == 0 and (column1 - column0) % 2 == 0:
        center_row, center_column = (row0 + row1) // 2, (column0 + column1) // 2
        if 2 * center_row != len(grid) - 1 or 2 * center_column != len(grid[0]) - 1:
            result[center_row][center_column] = background
    output = tuple(tuple(row) for row in result)
    if output == grid:
        raise Undefined("concentric fill emits nothing")
    return output


def _header_chebyshev_corner(grid: Grid) -> Grid:
    background = _background(grid)
    height, width = _shape(grid)
    if height < 5 or width < 3:
        raise Undefined("header scene is too small")
    divider = grid[1][0]
    if divider == background or any(cell != divider for cell in grid[1]):
        raise Undefined("canonical divider is absent")
    if grid[0][0] == background:
        raise Undefined("header must begin with the seed role")
    seeds = [
        (row, column, grid[row][column])
        for row in range(2, height)
        for column in range(width)
        if grid[row][column] != background
    ]
    if len(seeds) != 1 or seeds[0][2] != grid[0][0]:
        raise Undefined("header scene needs one matching seed")
    seed_row, seed_column, _ = seeds[0]
    radius = max((column for column, color in enumerate(grid[0]) if color != background), default=-1)
    if radius < 1 or radius > max(height, width):
        raise Undefined("header radius is invalid")
    if any(
        grid[row][column] != background
        for row in range(2, height)
        for column in range(width)
        if (row, column) != (seed_row, seed_column)
    ):
        raise Undefined("header scene contains unrelated foreground")
    sequence = grid[0][: radius + 1]
    result = [list(row) for row in grid]
    for row in range(2, height):
        for column in range(width):
            distance = max(abs(row - seed_row), abs(column - seed_column))
            if distance <= radius:
                result[row][column] = sequence[distance]
    if radius == seed_column and grid[0][radius] != background:
        result[0][radius] = divider
    output = tuple(tuple(row) for row in result)
    if output == grid:
        raise Undefined("header scene emits nothing")
    return output


def _header_chebyshev_layers(grid: Grid) -> Grid:
    return _oriented_unique(grid, _header_chebyshev_corner)


def _sparse_dotted_frames(grid: Grid, step: int) -> Grid:
    background = _background(grid)
    height, width = _shape(grid)
    if height != width or height < 2 * step + 3 or height % 2 == 0:
        raise Undefined("dotted-frame canvas must be a sufficiently large odd square")
    points = [
        (row, column, grid[row][column])
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background
    ]
    if len(points) < 2:
        raise Undefined("dotted-frame evidence is insufficient")
    corners: dict[int, set[int]] = defaultdict(set)
    edges: dict[int, set[int]] = defaultdict(set)
    for row, column, color in points:
        row_depth = min(row, height - 1 - row)
        column_depth = min(column, width - 1 - column)
        shell = min(row_depth, column_depth)
        if shell <= 0 or shell % step != 1 % step:
            raise Undefined("dotted-frame evidence has the wrong phase")
        if (row_depth - shell) % step or (column_depth - shell) % step:
            raise Undefined("dotted-frame evidence is off lattice")
        destination = corners if row_depth == column_depth else edges
        destination[shell].add(color)
    if any(len(colors) != 1 for colors in (*corners.values(), *edges.values())):
        raise Undefined("a shell role has conflicting colors")
    result = [list(row) for row in grid]
    for shell in sorted(set(corners) | set(edges)):
        far = height - 1 - shell
        if far <= shell or (far - shell) % step:
            raise Undefined("shell does not close on the inferred lattice")
        corner_color = next(iter(corners[shell])) if shell in corners else None
        edge_color = next(iter(edges[shell])) if shell in edges else None
        coordinates = range(shell, far + 1, step)
        for offset in coordinates:
            for row, column in (
                (shell, offset),
                (far, offset),
                (offset, shell),
                (offset, far),
            ):
                is_corner = row in (shell, far) and column in (shell, far)
                color = corner_color if is_corner else edge_color
                if color is not None:
                    result[row][column] = color
    output = tuple(tuple(row) for row in result)
    if output == grid:
        raise Undefined("dotted-frame completion emits nothing")
    return output


def _monochrome_components(grid: Grid, color: int) -> tuple[frozenset[Point], ...]:
    remaining = {
        (row, column)
        for row in range(len(grid))
        for column in range(len(grid[0]))
        if grid[row][column] == color
    }
    components: list[frozenset[Point]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = [seed]
        component = {seed}
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
        components.append(frozenset(component))
    return tuple(sorted(components, key=lambda component: (min(component), len(component))))


def _closed_cycle_bands(grid: Grid, exterior: int, interior: int) -> Grid:
    background = _background(grid)
    source_colors = sorted(_palette(grid) - {background})
    if (
        len(source_colors) != 1
        or exterior == interior
        or exterior in _palette(grid)
        or interior in _palette(grid)
    ):
        raise Undefined("cycle-band color roles are not unique")
    ink = source_colors[0]
    height, width = _shape(grid)
    result = [list(row) for row in grid]
    closed_count = 0
    for component in _monochrome_components(grid, ink):
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
        # Close a one-cell bevel in the external band.  This is a geometric
        # continuation of the expanded bounding corners, not a fill of the
        # entire bounding rectangle.
        row0, row1, column0, column1 = _bbox(component)
        for row, column in (
            (row0 - 1, column0 - 1),
            (row0 - 1, column1 + 1),
            (row1 + 1, column0 - 1),
            (row1 + 1, column1 + 1),
        ):
            if (
                0 <= row < height
                and 0 <= column < width
                and grid[row][column] == background
                and min(
                    max(abs(row - source_row), abs(column - source_column))
                    for source_row, source_column in component
                )
                <= 2
            ):
                result[row][column] = exterior
    if closed_count == 0:
        return grid
    output = tuple(tuple(row) for row in result)
    if output == grid:
        raise Undefined("closed cycles emit no bands")
    return output


def _color_bboxes(grid: Grid) -> dict[int, tuple[int, int, int, int]]:
    background = _background(grid)
    answer: dict[int, tuple[int, int, int, int]] = {}
    for color in sorted(_palette(grid) - {background}):
        points = (
            (row, column)
            for row in range(len(grid))
            for column in range(len(grid[0]))
            if grid[row][column] == color
        )
        answer[color] = _bbox(points)
    if len(answer) < 3:
        raise Undefined("rectangle stack needs at least three colors")
    return answer


def _render_nested(sequence: Sequence[int], side: int) -> Grid:
    if side < 2 or (side + 1) // 2 != len(sequence):
        raise Undefined("nested renderer side and layer count disagree")
    return tuple(
        tuple(sequence[min(row, column, side - 1 - row, side - 1 - column)] for column in range(side))
        for row in range(side)
    )


def _size_sorted_rectangle_stack(grid: Grid) -> Grid:
    bboxes = _color_bboxes(grid)
    ranked = []
    for color, (row0, row1, column0, column1) in bboxes.items():
        height, width = row1 - row0 + 1, column1 - column0 + 1
        ranked.append((max(height, width), min(height, width), color))
    if len({extent for extent, _, _ in ranked}) != len(ranked):
        raise Undefined("rectangle extents do not define a total size order")
    ranked.sort(reverse=True)
    side = ranked[0][0]
    sequence = [color for _, _, color in ranked]
    return _render_nested(sequence, side)


def _perimeter(bounds: tuple[int, int, int, int]) -> frozenset[Point]:
    row0, row1, column0, column1 = bounds
    return frozenset(
        (row, column)
        for row in range(row0, row1 + 1)
        for column in range(column0, column1 + 1)
        if row in (row0, row1) or column in (column0, column1)
    )


def _unique_topological_order(edges: Mapping[int, set[int]]) -> tuple[int, ...]:
    remaining = {node: set(destinations) for node, destinations in edges.items()}
    order: list[int] = []
    while remaining:
        indegree = {node: 0 for node in remaining}
        for source, destinations in remaining.items():
            for destination in destinations:
                if destination in indegree and destination != source:
                    indegree[destination] += 1
        roots = sorted(node for node, degree in indegree.items() if degree == 0)
        if len(roots) != 1:
            raise Undefined("occlusion graph lacks a unique total order")
        root = roots[0]
        order.append(root)
        remaining.pop(root)
        for destinations in remaining.values():
            destinations.discard(root)
    return tuple(order)


def _occlusion_order_rectangle_stack(grid: Grid) -> Grid:
    bboxes = _color_bboxes(grid)
    edges: dict[int, set[int]] = {color: set() for color in bboxes}
    colors = sorted(bboxes)
    for index, left in enumerate(colors):
        for right in colors[index + 1 :]:
            crossings = _perimeter(bboxes[left]) & _perimeter(bboxes[right])
            visible = Counter(grid[row][column] for row, column in crossings)
            left_votes, right_votes = visible[left], visible[right]
            if left_votes > right_votes:
                edges[right].add(left)
            elif right_votes > left_votes:
                edges[left].add(right)
    order = _unique_topological_order(edges)
    return _render_nested(order, 2 * len(order) - 1)


def _execute(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("unknown program schema")
    operation = program.get("op")
    if operation == "masked_translation_lattice":
        return _lattice_fill(grid, int(program["mask_color"]), limits)
    if operation == "recursive_substitution_wallpaper":
        return _substitution_wallpaper(grid)
    if operation == "alternating_concentric_fill":
        return _alternating_concentric_fill(grid, int(program["fill_color"]))
    if operation == "header_chebyshev_layers":
        return _header_chebyshev_layers(grid)
    if operation == "sparse_dotted_frames":
        return _sparse_dotted_frames(grid, int(program["step"]))
    if operation == "closed_cycle_bands":
        return _closed_cycle_bands(
            grid,
            int(program["exterior_color"]),
            int(program["interior_color"]),
        )
    if operation == "size_sorted_rectangle_stack":
        return _size_sorted_rectangle_stack(grid)
    if operation == "occlusion_order_rectangle_stack":
        return _occlusion_order_rectangle_stack(grid)
    raise Undefined("unknown amodal operation")


def execute_program(
    program: Mapping[str, Any], value: Any, limits: Mapping[str, Any] | Limits | None = None
) -> list[list[int]]:
    bounds = Limits.from_value(limits)
    grid = _grid(value, bounds.max_grid_cells)
    return _plain(_execute(program, grid, bounds))


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    source = _plain(_grid(value, Limits().max_grid_cells))
    output = execute_program(program, source)
    return {
        "output": output,
        "stages": [
            {"name": "parse_amodal_scene", "input": source, "output": source},
            {
                "name": f"reconstruct:{program.get('op', 'unknown')}",
                "input": source,
                "output": output,
            },
        ],
    }


def _program(operation: str, complexity: int, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "op": operation,
        "description_length": complexity,
        "root_scope": "immutable_input",
        **parameters,
    }


def _enumerate_programs(train: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    programs = [
        _program("sparse_dotted_frames", 13, step=2),
        _program("header_chebyshev_layers", 15),
        _program("size_sorted_rectangle_stack", 16),
        _program("recursive_substitution_wallpaper", 17),
        _program("occlusion_order_rectangle_stack", 18),
    ]
    introduced = sorted(
        {
            color
            for source, target in train
            for color in _palette(target) - _palette(source)
        }
    )
    programs.extend(
        _program("alternating_concentric_fill", 14, fill_color=color)
        for color in introduced
    )
    for exterior in introduced:
        for interior in introduced:
            if exterior != interior:
                programs.append(
                    _program(
                        "closed_cycle_bands",
                        12,
                        exterior_color=exterior,
                        interior_color=interior,
                    )
                )
    changed_sources = {
        before
        for source, target in train
        if _shape(source) == _shape(target)
        for source_row, target_row in zip(source, target)
        for before, after in zip(source_row, target_row)
        if before != after
    }
    if len(changed_sources) == 1:
        programs.append(
            _program(
                "masked_translation_lattice",
                20,
                mask_color=next(iter(changed_sources)),
            )
        )
    return tuple(sorted(programs, key=lambda program: (int(program["description_length"]), _canonical(program))))


def _evaluate(program: Mapping[str, Any], sources: Sequence[Grid], limits: Limits) -> tuple[Grid | None, ...]:
    outputs: list[Grid | None] = []
    for source in sources:
        try:
            first = _execute(program, source, limits)
            second = _execute(json.loads(_canonical(program)), _grid(_plain(source)), limits)
            if first != second:
                raise Undefined("fresh replay is nondeterministic")
            outputs.append(first)
        except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            outputs.append(None)
    return tuple(outputs)


def _counterfactual_exact(program: Mapping[str, Any], train: Sequence[Pair], limits: Limits) -> int:
    probes = 0
    for source, target in train:
        for operation in ("rot90", "flip_h"):
            transformed_source = _d4(source, operation)
            transformed_target = _d4(target, operation)
            if _execute(program, transformed_source, limits) != transformed_target:
                raise Undefined("dihedral counterfactual failed")
            probes += 1
    return probes


def _fresh_loo(train: Sequence[Pair], limits: Limits) -> tuple[bool, int, tuple[str, ...]]:
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
            predictions = _evaluate(program, retained_sources, limits)
            if predictions == retained_targets:
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
        train, tests = _sanitize(task, bounds)
    except (Undefined, KeyError, TypeError, ValueError):
        return []
    if len(train) < bounds.min_demos:
        return []
    if all(source == target for source, target in train):
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
        train_outputs = _evaluate(program, train_sources, bounds)
        if train_outputs != targets:
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
        behaviors[_digest([_plain(output) for output in item[2]])].append(item)
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda item: (item[0], _canonical(item[1])))
    complexity, selected, predictions, counterfactuals = equivalent[0]
    candidate = {
        "family": f"amodal_scene_reconstruction.{selected['op']}",
        "program": json.loads(_canonical(selected)),
        "train_outputs": [_plain(target) for target in targets],
        "test_outputs": [_plain(output) for output in predictions],
        "complexity": complexity,
        "evidence": {
            "author": AUTHOR,
            "all_demonstrations_exact": True,
            "exact_serialized_replay": True,
            "fresh_process_equivalent_replay": True,
            "fresh_leave_one_out_rediscovery": True,
            "leave_one_out_programs_checked": loo_checked,
            "leave_one_out_enumeration_signatures": list(loo_signatures),
            "demo_order_invariance_checked": True,
            "dihedral_counterfactual_exact": True,
            "counterfactual_probe_count": counterfactuals,
            "bounded_enumeration_complete": True,
            "enumerated_programs": len(programs),
            "program_evaluations": required,
            "minimum_description_programs": len(near),
            "test_behavior_classes": 1,
            "behavior_hash": behavior_hash,
            "task_identity_observed": False,
            "test_labels_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


__all__ = [
    "Limits",
    "compile_task",
    "execute_program",
    "replay_program",
]
