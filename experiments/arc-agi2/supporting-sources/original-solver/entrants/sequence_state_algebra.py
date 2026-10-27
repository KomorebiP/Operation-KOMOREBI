"""Label-blind sequence and finite-state algebra for Block 15.

This entrant compiles a small grammar of executable state processes rather
than caching rasters.  Its current operators cover:

* multiseed Voronoi ownership followed by Chebyshev parity waves;
* periodic axial and diagonal emission from a five-cell cross;
* Chebyshev distance-shell completion with an input-derived wavelength;
* a bottom-anchored alternating row-displacement wave; and
* right-falling domino chains with variable rod lengths.

Every returned program exactly replays every demonstration, is re-induced in
leave-one-demonstration-out checks, survives palette-transport
counterfactuals, and belongs to a single held-input behavior class.  The
compiler reads demonstrations and held-out inputs only; task identity is
discarded by the compatibility wrapper.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.sequence_state_algebra.program.v1"


class Undefined(ValueError):
    """The requested structural state process is absent or ambiguous."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_examples: int = 20
    max_total_cells: int = 100_000
    max_candidates: int = 32
    max_programs: int = 128
    max_executor_calls: int = 4096
    max_counterfactuals: int = 80

    @classmethod
    def from_value(cls, value: Any) -> "Limits":
        if value is None:
            return cls()
        if isinstance(value, cls):
            return value
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        defaults = cls()
        aliases = {
            "candidate_cap": "max_candidates",
            "max_total_candidates": "max_programs",
            "max_replay_calls": "max_executor_calls",
            "max_replay_stages": None,
            "max_trace_bytes": None,
            "time_limit": None,
            "time_limit_seconds": None,
        }
        allowed = set(cls.__dataclass_fields__) | set(aliases)
        if set(value) - allowed:
            raise Undefined("unknown finite limit")
        parsed: dict[str, int] = {}
        for key, raw in value.items():
            target = aliases.get(key, key)
            if target is None:
                continue
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                raise Undefined("finite limits must be positive integers")
            ceiling = int(getattr(defaults, target))
            parsed[target] = min(parsed.get(target, raw), raw, ceiling)
        return cls(**parsed)


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("ascii")).hexdigest()


def _grid(value: Any, max_side: int = 30) -> Grid:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes, bytearray))
        or not value
        or len(value) > max_side
    ):
        raise Undefined("grid height is invalid")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if (
            not isinstance(raw_row, Sequence)
            or isinstance(raw_row, (str, bytes, bytearray))
            or not raw_row
            or len(raw_row) > max_side
        ):
            raise Undefined("grid row is invalid")
        row: list[int] = []
        for raw_cell in raw_row:
            if (
                isinstance(raw_cell, bool)
                or not isinstance(raw_cell, int)
                or not 0 <= raw_cell <= 9
            ):
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    return tuple(rows)


def _plain(value: Grid) -> list[list[int]]:
    return [list(row) for row in value]


def _shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def _palette(value: Grid) -> frozenset[int]:
    return frozenset(cell for row in value for cell in row)


def _mode(value: Grid) -> int:
    counts = Counter(cell for row in value for cell in row)
    peak = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == peak)
    if len(winners) != 1:
        raise Undefined("background mode is tied")
    return winners[0]


def _bbox(cells: Iterable[Cell]) -> tuple[int, int, int, int]:
    points = tuple(cells)
    if not points:
        raise Undefined("support is empty")
    return (
        min(row for row, _ in points),
        max(row for row, _ in points),
        min(column for _, column in points),
        max(column for _, column in points),
    )


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train, tests = task.get("train"), task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes, bytearray))
        or len(train) < 2
        or not isinstance(tests, Sequence)
        or isinstance(tests, (str, bytes, bytearray))
        or not tests
        or len(train) + len(tests) > limits.max_examples
    ):
        raise Undefined("task arity is invalid")
    total = 0
    pairs: list[Pair] = []
    held_inputs: list[Grid] = []
    for index, record in enumerate(train):
        if not isinstance(record, Mapping):
            raise Undefined(f"train[{index}] is invalid")
        source = _grid(record.get("input"), limits.max_side)
        target = _grid(record.get("output"), limits.max_side)
        total += len(source) * len(source[0]) + len(target) * len(target[0])
        pairs.append((source, target))
    for index, record in enumerate(tests):
        if not isinstance(record, Mapping):
            raise Undefined(f"test[{index}] is invalid")
        # The contract permits only the held-out input member.
        source = _grid(record.get("input"), limits.max_side)
        total += len(source) * len(source[0])
        held_inputs.append(source)
    if total > limits.max_total_cells:
        raise Undefined("task cell budget is exhausted")
    return tuple(pairs), tuple(held_inputs)


def _program(operator: str, description_length: int, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "description_length": int(description_length),
        "root_scope": "immutable_input",
        **parameters,
    }


def _distance(metric: str, left: Cell, right: Cell) -> int:
    dr, dc = abs(left[0] - right[0]), abs(left[1] - right[1])
    if metric == "manhattan":
        return dr + dc
    if metric == "chebyshev":
        return max(dr, dc)
    if metric == "euclidean_squared":
        return dr * dr + dc * dc
    raise Undefined("distance metric is invalid")


def _execute_voronoi_wave(program: Mapping[str, Any], value: Grid) -> Grid:
    background = _mode(value)
    seeds = tuple(
        (row, column, value[row][column])
        for row in range(len(value))
        for column in range(len(value[0]))
        if value[row][column] != background
    )
    if not 2 <= len(seeds) <= 8:
        raise Undefined("Voronoi wave needs two to eight seeds")
    colors = [color for _, _, color in seeds]
    if len(set(colors)) != len(colors):
        raise Undefined("Voronoi seed colors must be unique")
    if any(
        row not in {0, len(value) - 1} and column not in {0, len(value[0]) - 1}
        for row, column, _ in seeds
    ):
        raise Undefined("Voronoi seeds must lie on the canvas boundary")
    ownership = str(program.get("ownership_metric"))
    wave_metric = str(program.get("wave_metric"))
    modulus = int(program.get("modulus", 0))
    residue = int(program.get("residue", -1))
    if modulus < 2 or not 0 <= residue < modulus:
        raise Undefined("wave phase is invalid")
    output = [[background] * len(value[0]) for _ in value]
    for row in range(len(value)):
        for column in range(len(value[0])):
            owner_distances = [
                _distance(ownership, (row, column), (seed_row, seed_column))
                for seed_row, seed_column, _ in seeds
            ]
            minimum = min(owner_distances)
            owners = [
                index for index, distance in enumerate(owner_distances) if distance == minimum
            ]
            if len(owners) != 1:
                continue
            seed_row, seed_column, color = seeds[owners[0]]
            wave_distance = _distance(
                wave_metric, (row, column), (seed_row, seed_column)
            )
            if wave_distance % modulus == residue:
                output[row][column] = color
    return _grid(output)


def _cross_center(value: Grid) -> tuple[Cell, int, int]:
    background = _mode(value)
    colors = _palette(value) - {background}
    if len(colors) != 1:
        raise Undefined("cross input needs one material color")
    color = next(iter(colors))
    cells = {
        (row, column)
        for row in range(len(value))
        for column in range(len(value[0]))
        if value[row][column] == color
    }
    if len(cells) != 5:
        raise Undefined("cross must contain five cells")
    for center in sorted(cells):
        row, column = center
        expected = {
            center,
            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
        }
        if cells == expected:
            return center, color, background
    raise Undefined("material is not an axial radius-one cross")


def _execute_cross_emission(program: Mapping[str, Any], value: Grid) -> Grid:
    (center_row, center_column), seed, background = _cross_center(value)
    expected_seed = int(program.get("seed_color", -1))
    expected_background = int(program.get("background_color", -1))
    if seed != expected_seed or background != expected_background:
        raise Undefined("cross roles do not match the compiled palette")
    diagonal = int(program.get("diagonal_color", -1))
    axial = int(program.get("axial_color", -1))
    phase = int(program.get("phase_color", -1))
    if len({background, seed, diagonal, axial, phase}) != 5:
        raise Undefined("cross emission roles must be distinct")
    output = _plain(value)
    for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        row, column = center_row + dr, center_column + dc
        while 0 <= row < len(value) and 0 <= column < len(value[0]):
            if value[row][column] != background:
                raise Undefined("diagonal ray collides with source material")
            output[row][column] = diagonal
            row += dr
            column += dc
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        step = 1
        row, column = center_row + 2 * dr, center_column + 2 * dc
        while 0 <= row < len(value) and 0 <= column < len(value[0]):
            if value[row][column] != background:
                raise Undefined("axial ray collides with source material")
            output[row][column] = phase if step % 3 == 0 else axial
            step += 1
            row += dr
            column += dc
    return _grid(output)


def _parallel_gap_period(value: Grid, foreground: int) -> int:
    height, width = _shape(value)
    all_gaps: list[int] = []
    axis_gaps: list[list[int]] = []
    for axis in ("rows", "columns"):
        gaps: list[int] = []
        line_count = height if axis == "rows" else width
        for line in range(line_count):
            positions = (
                [column for column in range(width) if value[line][column] == foreground]
                if axis == "rows"
                else [row for row in range(height) if value[row][line] == foreground]
            )
            runs: list[list[int]] = []
            for position in positions:
                if not runs or position > runs[-1][-1] + 1:
                    runs.append([position])
                else:
                    runs[-1].append(position)
            gaps.extend(
                runs[index + 1][0] - runs[index][-1] - 1
                for index in range(len(runs) - 1)
            )
        axis_gaps.append(gaps)
        all_gaps.extend(gaps)
    if any(not gaps for gaps in axis_gaps) or len(all_gaps) < 4:
        raise Undefined("parallel wavelength lacks bidirectional support")
    counts = Counter(all_gaps)
    peak = max(counts.values())
    winners = sorted(gap for gap, count in counts.items() if count == peak)
    if len(winners) != 1 or not 1 <= winners[0] <= 5:
        raise Undefined("parallel wavelength is ambiguous")
    period = winners[0] + 1
    if any(period - 1 not in gaps for gaps in axis_gaps):
        raise Undefined("wavelength is not witnessed on both axes")
    return period


def _execute_distance_shell(program: Mapping[str, Any], value: Grid) -> Grid:
    background = _mode(value)
    expected_background = int(program.get("background_color", -1))
    if background != expected_background or len(_palette(value)) != 2:
        raise Undefined("distance-shell source roles do not match")
    foreground = next(iter(_palette(value) - {background}))
    fill = int(program.get("fill_color", -1))
    if fill in {background, foreground}:
        raise Undefined("distance-shell fill role is not distinct")
    period = _parallel_gap_period(value, foreground)
    points = tuple(
        (row, column)
        for row in range(len(value))
        for column in range(len(value[0]))
        if value[row][column] == foreground
    )
    output: list[list[int]] = []
    for row in range(len(value)):
        output_row: list[int] = []
        for column in range(len(value[0])):
            distance = min(
                max(abs(row - seed_row), abs(column - seed_column))
                for seed_row, seed_column in points
            )
            output_row.append(foreground if distance % period == 0 else fill)
        output.append(output_row)
    return _grid(output)


def _execute_row_phase(program: Mapping[str, Any], value: Grid) -> Grid:
    background = _mode(value)
    if len(_palette(value)) != 2:
        raise Undefined("row phase wave needs a binary raster")
    cells = {
        (row, column)
        for row in range(len(value))
        for column in range(len(value[0]))
        if value[row][column] != background
    }
    top, bottom, _, _ = _bbox(cells)
    shifts = program.get("phase_shifts")
    if not isinstance(shifts, Sequence) or tuple(shifts) != (0, -1, 0, 1):
        raise Undefined("row phase schedule is invalid")
    output = [[background] * len(value[0]) for _ in value]
    for row, column in sorted(cells):
        distance = bottom - row
        destination = column + int(shifts[distance % len(shifts)])
        if not 0 <= destination < len(value[0]):
            raise Undefined("row phase wave clips material")
        if output[row][destination] != background:
            raise Undefined("row phase wave collides")
        output[row][destination] = value[row][column]
    if top == bottom or output == _plain(value):
        raise Undefined("row phase wave is degenerate")
    return _grid(output)


@dataclass(frozen=True, slots=True)
class _Rod:
    column: int
    top: int
    length: int
    color: int


def _vertical_rods(value: Grid) -> tuple[int, tuple[_Rod, ...]]:
    background = _mode(value)
    height, width = _shape(value)
    rods: list[_Rod] = []
    for column in range(width):
        material = [(row, value[row][column]) for row in range(height) if value[row][column] != background]
        if not material:
            continue
        rows = [row for row, _ in material]
        colors = {color for _, color in material}
        if (
            len(colors) != 1
            or rows[-1] != height - 1
            or rows != list(range(rows[0], height))
            or len(rows) < 2
        ):
            raise Undefined("material is not a bottom-supported vertical rod")
        rods.append(_Rod(column, rows[0], len(rows), next(iter(colors))))
    if len(rods) < 2:
        raise Undefined("domino system needs at least two rods")
    return background, tuple(rods)


def _execute_domino(program: Mapping[str, Any], value: Grid) -> Grid:
    background, rods = _vertical_rods(value)
    initiator = int(program.get("initiator_color", -1))
    follower = int(program.get("follower_color", -1))
    if _palette(value) != {background, initiator, follower}:
        raise Undefined("domino palette does not match the program")
    active = {index for index, rod in enumerate(rods) if rod.color == initiator}
    if not active:
        raise Undefined("domino system has no initiator")
    by_column = {rod.column: index for index, rod in enumerate(rods)}
    queue = deque(sorted(active))
    while queue:
        index = queue.popleft()
        rod = rods[index]
        end = rod.column + rod.length - 1
        if end >= len(value[0]):
            raise Undefined("a domino would fall beyond the canvas")
        if any(other.column in range(rod.column + 1, end + 1) for other in rods):
            raise Undefined("a falling domino intersects an upright rod")
        successor = by_column.get(end + 1)
        if successor is not None and successor not in active:
            if rods[successor].color != follower:
                raise Undefined("a chain encounters a non-follower rod")
            active.add(successor)
            queue.append(successor)
    output = _plain(value)
    floor = len(value) - 1
    for index in sorted(active):
        rod = rods[index]
        for row in range(rod.top, floor + 1):
            output[row][rod.column] = background
    for index in sorted(active):
        rod = rods[index]
        for column in range(rod.column, rod.column + rod.length):
            if output[floor][column] != background:
                raise Undefined("fallen dominoes collide with stationary material")
            output[floor][column] = rod.color
    return _grid(output)


def _validate_program(program: Mapping[str, Any]) -> str:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("program schema is invalid")
    operator = program.get("operator")
    if not isinstance(operator, str):
        raise Undefined("program operator is invalid")
    return operator


def _execute(program: Mapping[str, Any], value: Grid) -> Grid:
    operator = _validate_program(program)
    if operator == "multiseed_voronoi_chebyshev_parity":
        return _execute_voronoi_wave(program, value)
    if operator == "cross_periodic_ray_emission":
        return _execute_cross_emission(program, value)
    if operator == "chebyshev_distance_shell_completion":
        return _execute_distance_shell(program, value)
    if operator == "bottom_anchored_alternating_row_wave":
        return _execute_row_phase(program, value)
    if operator == "right_falling_domino_chain":
        return _execute_domino(program, value)
    raise Undefined("program operator is unknown")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized sequence-state program deterministically."""

    return _plain(_execute(program, _grid(value)))


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Tournament replay hook with one contiguous state-transition stage."""

    source = _grid(value)
    output = _execute(program, source)
    operator = _validate_program(program)
    return {
        "output": _plain(output),
        "stages": [
            {
                "name": f"sequence-state:{operator}",
                "input": _plain(source),
                "output": _plain(output),
            }
        ],
    }


def _exact(program: Mapping[str, Any], pairs: Sequence[Pair]) -> bool:
    try:
        return all(_execute(program, source) == target for source, target in pairs)
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return False


def _cross_programs(pairs: Sequence[Pair]) -> list[dict[str, Any]]:
    parameter_sets: set[tuple[int, int, int, int, int]] = set()
    for source, target in pairs:
        center, seed, background = _cross_center(source)
        changed: dict[str, set[int]] = {"diagonal": set(), "axial": set()}
        phase_values: set[int] = set()
        axial_values: set[int] = set()
        for row in range(len(source)):
            for column in range(len(source[0])):
                if source[row][column] == target[row][column]:
                    continue
                if source[row][column] != background:
                    raise Undefined("cross emission overwrites source material")
                dr, dc = row - center[0], column - center[1]
                if dr and dc and abs(dr) == abs(dc):
                    changed["diagonal"].add(target[row][column])
                elif (dr == 0) != (dc == 0) and abs(dr or dc) >= 2:
                    step = abs(dr or dc) - 1
                    changed["axial"].add(target[row][column])
                    (phase_values if step % 3 == 0 else axial_values).add(
                        target[row][column]
                    )
                else:
                    raise Undefined("cross emission changes an unsupported cell")
        if (
            len(changed["diagonal"]) != 1
            or len(phase_values) != 1
            or len(axial_values) != 1
        ):
            raise Undefined("cross emission colors are ambiguous")
        diagonal = next(iter(changed["diagonal"]))
        axial = next(iter(axial_values))
        phase = next(iter(phase_values))
        parameter_sets.add((background, seed, diagonal, axial, phase))
    if len(parameter_sets) != 1:
        raise Undefined("cross emission roles vary across demonstrations")
    background, seed, diagonal, axial, phase = next(iter(parameter_sets))
    return [
        _program(
            "cross_periodic_ray_emission",
            17,
            background_color=background,
            seed_color=seed,
            diagonal_color=diagonal,
            axial_color=axial,
            phase_color=phase,
            axial_sequence=[axial, axial, phase],
            diagonal_policy="constant_from_center",
        )
    ]


def _distance_shell_programs(pairs: Sequence[Pair]) -> list[dict[str, Any]]:
    backgrounds: set[int] = set()
    fills: set[int] = set()
    for source, target in pairs:
        background = _mode(source)
        if len(_palette(source)) != 2:
            raise Undefined("distance-shell source is not binary")
        foreground = next(iter(_palette(source) - {background}))
        target_other = _palette(target) - {foreground}
        if len(target_other) != 1 or background in _palette(target):
            raise Undefined("distance-shell target roles are ambiguous")
        backgrounds.add(background)
        fills.add(next(iter(target_other)))
        _parallel_gap_period(source, foreground)
    if len(backgrounds) != 1 or len(fills) != 1:
        raise Undefined("distance-shell colors vary across demonstrations")
    return [
        _program(
            "chebyshev_distance_shell_completion",
            15,
            background_color=next(iter(backgrounds)),
            fill_color=next(iter(fills)),
            period_policy="modal_parallel_gap_plus_one",
            metric="chebyshev",
            foreground_residue=0,
        )
    ]


def _row_phase_programs(pairs: Sequence[Pair]) -> list[dict[str, Any]]:
    for source, target in pairs:
        if (
            _shape(source) != _shape(target)
            or len(_palette(source)) != 2
            or _palette(source) != _palette(target)
            or Counter(cell for row in source for cell in row)
            != Counter(cell for row in target for cell in row)
        ):
            raise Undefined("row phase invariants do not hold")
    return [
        _program(
            "bottom_anchored_alternating_row_wave",
            12,
            background_role="input_mode",
            anchor="foreground_bbox_bottom",
            phase_shifts=[0, -1, 0, 1],
            collision_policy="exact_nonoverlap",
        )
    ]


def _domino_programs(pairs: Sequence[Pair]) -> list[dict[str, Any]]:
    common_orders: set[tuple[int, int]] | None = None
    for source, target in pairs:
        background, rods = _vertical_rods(source)
        colors = sorted({rod.color for rod in rods})
        if len(colors) != 2 or _shape(source) != _shape(target):
            raise Undefined("domino roles are ambiguous")
        orders = {(left, right) for left in colors for right in colors if left != right}
        valid: set[tuple[int, int]] = set()
        for initiator, follower in orders:
            proposal = _program(
                "right_falling_domino_chain",
                16,
                initiator_color=initiator,
                follower_color=follower,
                background_color=background,
                support_edge="bottom",
                fall_direction="right",
                trigger_gap=0,
            )
            if _exact(proposal, ((source, target),)):
                valid.add((initiator, follower))
        common_orders = valid if common_orders is None else common_orders & valid
    if not common_orders:
        raise Undefined("no common domino role assignment")
    programs = []
    for initiator, follower in sorted(common_orders):
        programs.append(
            _program(
                "right_falling_domino_chain",
                16,
                initiator_color=initiator,
                follower_color=follower,
                background_role="input_mode",
                support_edge="bottom",
                fall_direction="right",
                trigger_gap=0,
            )
        )
    return programs


def _voronoi_programs(pairs: Sequence[Pair]) -> list[dict[str, Any]]:
    programs: list[dict[str, Any]] = []
    for ownership in ("manhattan", "euclidean_squared"):
        proposal = _program(
            "multiseed_voronoi_chebyshev_parity",
            14 if ownership == "manhattan" else 15,
            background_role="input_mode",
            seed_selector="distinct_boundary_singletons",
            ownership_metric=ownership,
            ownership_ties="background",
            wave_metric="chebyshev",
            modulus=2,
            residue=0,
        )
        if _exact(proposal, pairs):
            programs.append(proposal)
    return programs


def _infer(operator: str, pairs: Sequence[Pair]) -> list[dict[str, Any]]:
    if not pairs:
        return []
    try:
        if operator == "multiseed_voronoi_chebyshev_parity":
            proposals = _voronoi_programs(pairs)
        elif operator == "cross_periodic_ray_emission":
            proposals = _cross_programs(pairs)
        elif operator == "chebyshev_distance_shell_completion":
            proposals = _distance_shell_programs(pairs)
        elif operator == "bottom_anchored_alternating_row_wave":
            proposals = _row_phase_programs(pairs)
        elif operator == "right_falling_domino_chain":
            proposals = _domino_programs(pairs)
        else:
            raise Undefined("unknown inference operator")
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []
    unique = {_canonical(program): program for program in proposals if _exact(program, pairs)}
    return [unique[key] for key in sorted(unique)]


def _loo(operator: str, pairs: Sequence[Pair]) -> tuple[bool, list[dict[str, Any]]]:
    witnesses: list[dict[str, Any]] = []
    for held_index, (source, target) in enumerate(pairs):
        subset = tuple(pair for index, pair in enumerate(pairs) if index != held_index)
        programs = _infer(operator, subset)
        behaviors: dict[str, Grid] = {}
        for program in programs:
            try:
                output = _execute(program, source)
            except (Undefined, KeyError, TypeError, ValueError, IndexError):
                continue
            behaviors.setdefault(_canonical(_plain(output)), output)
        exact = len(behaviors) == 1 and next(iter(behaviors.values())) == target
        witnesses.append(
            {
                "held_out_index": held_index,
                "reinduced_programs": len(programs),
                "behavior_classes": len(behaviors),
                "held_out_exact": exact,
            }
        )
        if not exact:
            return False, witnesses
    return True, witnesses


_COLOR_KEYS = frozenset(
    {
        "background_color",
        "seed_color",
        "diagonal_color",
        "axial_color",
        "phase_color",
        "fill_color",
        "initiator_color",
        "follower_color",
    }
)


def _swap_grid(value: Grid, left: int, right: int) -> Grid:
    return tuple(
        tuple(right if cell == left else left if cell == right else cell for cell in row)
        for row in value
    )


def _swap_program(program: Mapping[str, Any], left: int, right: int) -> dict[str, Any]:
    transported = json.loads(_canonical(program))
    for key in _COLOR_KEYS:
        if key in transported:
            value = transported[key]
            transported[key] = right if value == left else left if value == right else value
    if "axial_sequence" in transported:
        transported["axial_sequence"] = [
            right if value == left else left if value == right else value
            for value in transported["axial_sequence"]
        ]
    return transported


def _palette_counterfactuals(
    program: Mapping[str, Any], pairs: Sequence[Pair], limits: Limits
) -> tuple[bool, int]:
    used = sorted(
        {
            cell
            for source, target in pairs
            for grid in (source, target)
            for row in grid
            for cell in row
        }
    )
    absent = next((color for color in range(10) if color not in used), None)
    if absent is None:
        return False, 0
    checks = 0
    for color in used:
        transported = _swap_program(program, color, absent)
        for source, target in pairs:
            checks += 1
            if checks > limits.max_counterfactuals:
                raise Undefined("counterfactual budget is exhausted")
            try:
                actual = _execute(transported, _swap_grid(source, color, absent))
            except (Undefined, KeyError, TypeError, ValueError, IndexError):
                return False, checks
            if actual != _swap_grid(target, color, absent):
                return False, checks
    return checks > 0, checks


def _candidate(
    program: Mapping[str, Any],
    pairs: Sequence[Pair],
    tests: Sequence[Grid],
    limits: Limits,
) -> dict[str, Any] | None:
    operator = str(program.get("operator"))
    try:
        train_outputs = tuple(_execute(program, source) for source, _ in pairs)
        if train_outputs != tuple(target for _, target in pairs):
            return None
        test_outputs = tuple(_execute(program, source) for source in tests)
        loo_ok, loo_witnesses = _loo(operator, pairs)
        if not loo_ok:
            return None
        palette_ok, palette_checks = _palette_counterfactuals(program, pairs, limits)
        if not palette_ok:
            return None
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return None
    candidate = {
        "family": "sequence_state_algebra",
        "program": json.loads(_canonical(program)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in test_outputs],
        "complexity": int(program["description_length"]),
        "evidence": {
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_witnesses": loo_witnesses,
            "palette_transport_counterfactuals": palette_checks,
            "complete_behavior_quotient": True,
            "unique_test_behavior": True,
            "bounded_grammar": True,
            "bounded_execution": True,
            "task_identity_observed": False,
            "held_out_labels_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return candidate


def compile_task(task: Any, limits: Mapping[str, Any] | Limits | None = None) -> list[dict[str, Any]]:
    """Compile one behavior-unique finite-state candidate, or abstain."""

    try:
        bounds = Limits.from_value(limits)
        pairs, tests = _sanitize(task, bounds)
    except (Undefined, KeyError, TypeError, ValueError, IndexError):
        return []
    operators = (
        "multiseed_voronoi_chebyshev_parity",
        "cross_periodic_ray_emission",
        "chebyshev_distance_shell_completion",
        "bottom_anchored_alternating_row_wave",
        "right_falling_domino_chain",
    )
    candidates: list[dict[str, Any]] = []
    enumerated = 0
    for operator in operators:
        programs = _infer(operator, pairs)
        enumerated += len(programs)
        if enumerated > bounds.max_programs:
            return []
        for program in programs:
            candidate = _candidate(program, pairs, tests, bounds)
            if candidate is not None:
                candidates.append(candidate)
    if not candidates:
        return []
    behaviors: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        behaviors.setdefault(_digest(candidate["test_outputs"]), []).append(candidate)
    if len(behaviors) != 1:
        return []
    equivalent = next(iter(behaviors.values()))
    equivalent.sort(key=lambda item: (item["complexity"], _canonical(item["program"])))
    return equivalent[: bounds.max_candidates]


def predict_task(task_id: Any, task: Any) -> list[list[list[int]]]:
    """Compatibility wrapper; task identity is deliberately ignored."""

    del task_id
    candidates = compile_task(task)
    return candidates[0]["test_outputs"] if len(candidates) == 1 else []


__all__ = [
    "AUTHOR",
    "Limits",
    "SCHEMA",
    "Undefined",
    "compile_task",
    "execute_program",
    "predict_task",
    "replay_program",
]
