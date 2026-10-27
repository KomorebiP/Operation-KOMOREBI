"""Bounded construction and expansion entrant for PR-LASM Block 13.

The entrant learns only from labelled demonstrations and executes the surviving
programs on copied test inputs.  Its grammar covers pixel substitutions,
Kronecker masks, dihedral tile layouts, separator-defined panels, carrier/motif
stamping, and a small recursively applied construction body.  Every emitted
program replays every demonstration exactly; malformed, ambiguous, oversized,
or partially executable proposals are ordinary abstentions.

The surrounding tournament owns scoring and promotion.  This module owns only
finite task-local proposal generation and deterministic behavioral quotienting.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import itertools
import json
from typing import Any, Callable, Iterable, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]

D4 = (
    "id",
    "fliplr",
    "flipud",
    "r180",
    "transpose",
    "r90",
    "r270",
    "anti_transpose",
)


class _Undefined(Exception):
    """Internal total-with-failure signal; never escapes ``compile_task``."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_grid_cells: int = 900
    max_candidates: int = 128
    max_hypotheses: int = 20_000
    max_layout_combinations: int = 256
    max_depth: int = 4
    max_factor: int = 8
    max_panels: int = 9

    @classmethod
    def from_value(cls, raw: Mapping[str, Any] | None) -> "Limits":
        if raw is None:
            return cls()
        if not isinstance(raw, Mapping):
            raise _Undefined("limits must be a mapping")
        defaults = cls()
        values: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            value = raw.get(name, getattr(defaults, name))
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise _Undefined(f"invalid limit {name}")
            values[name] = value
        # The recursion language is intentionally frozen at depths 1--4.
        values["max_depth"] = min(values["max_depth"], 4)
        return cls(**values)


def _plain(value: Grid) -> list[list[int]]:
    return [list(row) for row in value]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("ascii")).hexdigest()


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, (list, tuple)) or not value:
        raise _Undefined("grid must be a nonempty row sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, (list, tuple)) or not raw_row:
            raise _Undefined("grid row must be a nonempty sequence")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise _Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise _Undefined("ragged grid")
        rows.append(tuple(row))
    if len(rows) > limits.max_side or int(width or 0) > limits.max_side:
        raise _Undefined("grid exceeds side bound")
    if len(rows) * int(width or 0) > limits.max_grid_cells:
        raise _Undefined("grid exceeds cell bound")
    return tuple(rows)


def _shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def _checked(value: Grid, limits: Limits) -> Grid:
    height, width = _shape(value)
    if height > limits.max_side or width > limits.max_side:
        raise _Undefined("constructed grid exceeds side bound")
    if height * width > limits.max_grid_cells:
        raise _Undefined("constructed grid exceeds cell bound")
    if any(not 0 <= cell <= 9 for row in value for cell in row):
        raise _Undefined("constructed color outside ARC palette")
    return value


def _sanitize(
    task: Any, limits: Limits
) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise _Undefined("task must be a mapping")
    raw_train = task.get("train")
    raw_test = task.get("test")
    if not isinstance(raw_train, (list, tuple)) or not raw_train:
        raise _Undefined("at least one demonstration is required")
    if not isinstance(raw_test, (list, tuple)) or not raw_test:
        raise _Undefined("at least one test input is required")
    demonstrations: list[tuple[Grid, Grid]] = []
    for example in raw_train:
        if not isinstance(example, Mapping) or "input" not in example or "output" not in example:
            raise _Undefined("malformed demonstration")
        demonstrations.append(
            (_grid(example["input"], limits), _grid(example["output"], limits))
        )
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping) or "input" not in example:
            raise _Undefined("malformed test input")
        # Copy only the authorized field.  Any accidentally attached label is
        # deliberately unreachable to induction and execution.
        tests.append(_grid(example["input"], limits))
    return tuple(demonstrations), tuple(tests)


def _mode(value: Grid) -> int:
    counts = Counter(cell for row in value for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def _background(value: Grid, role: str) -> int:
    if role == "zero":
        return 0
    if role == "mode":
        return _mode(value)
    if role == "corner":
        corners = (value[0][0], value[0][-1], value[-1][0], value[-1][-1])
        counts = Counter(corners)
        return min(counts, key=lambda color: (-counts[color], color))
    raise _Undefined("unknown background role")


def _d4(value: Grid, name: str) -> Grid:
    if name == "id":
        return value
    if name == "fliplr":
        return tuple(tuple(reversed(row)) for row in value)
    if name == "flipud":
        return tuple(reversed(value))
    if name == "r180":
        return tuple(tuple(reversed(row)) for row in reversed(value))
    transposed = tuple(
        tuple(value[row][column] for row in range(len(value)))
        for column in range(len(value[0]))
    )
    if name == "transpose":
        return transposed
    if name == "r90":
        return tuple(tuple(reversed(row)) for row in transposed)
    if name == "r270":
        return tuple(reversed(transposed))
    if name == "anti_transpose":
        return tuple(tuple(reversed(row)) for row in reversed(transposed))
    raise _Undefined("unknown dihedral transform")


def _slice(value: Grid, top: int, left: int, height: int, width: int) -> Grid:
    return tuple(tuple(value[row][left : left + width]) for row in range(top, top + height))


def _substitute(value: Grid, block: Callable[[int], Grid]) -> Grid:
    pieces: list[list[int]] = []
    block_height: int | None = None
    block_width: int | None = None
    for source_row in value:
        row_blocks = [block(cell) for cell in source_row]
        if not row_blocks:
            raise _Undefined("empty substitution row")
        shapes = {_shape(item) for item in row_blocks}
        if len(shapes) != 1:
            raise _Undefined("substitution blocks disagree in shape")
        current_height, current_width = next(iter(shapes))
        if block_height is None:
            block_height, block_width = current_height, current_width
        elif (current_height, current_width) != (block_height, block_width):
            raise _Undefined("substitution shape changed between rows")
        for local_row in range(current_height):
            pieces.append(
                [cell for item in row_blocks for cell in item[local_row]]
            )
    if not pieces or not pieces[0]:
        raise _Undefined("empty substitution result")
    return tuple(tuple(row) for row in pieces)


def _layout(
    value: Grid,
    rows: int,
    columns: int,
    transforms: Sequence[str],
    separator_width: int,
    separator_color: int,
) -> Grid:
    if rows < 1 or columns < 1 or len(transforms) != rows * columns:
        raise _Undefined("invalid layout arity")
    tiles = [_d4(value, name) for name in transforms]
    shapes = {_shape(tile) for tile in tiles}
    if len(shapes) != 1:
        raise _Undefined("layout tiles do not share a shape")
    tile_height, tile_width = next(iter(shapes))
    width = columns * tile_width + (columns - 1) * separator_width
    output: list[tuple[int, ...]] = []
    for tile_row in range(rows):
        for local_row in range(tile_height):
            row: list[int] = []
            for tile_column in range(columns):
                if tile_column:
                    row.extend([separator_color] * separator_width)
                tile = tiles[tile_row * columns + tile_column]
                row.extend(tile[local_row])
            output.append(tuple(row))
        if tile_row + 1 < rows:
            output.extend(tuple(separator_color for _ in range(width)) for _ in range(separator_width))
    return tuple(output)


def _separator_value(spec: Mapping[str, Any] | None, value: Grid) -> int:
    if spec is None:
        return 0
    kind = spec.get("kind")
    if kind == "literal":
        color = spec.get("color")
        if isinstance(color, bool) or not isinstance(color, int) or not 0 <= color <= 9:
            raise _Undefined("invalid literal separator")
        return color
    if kind == "background":
        return _background(value, str(spec.get("role")))
    raise _Undefined("invalid separator specification")


def _line_groups(indices: Iterable[int]) -> tuple[tuple[int, int], ...]:
    ordered = sorted(set(indices))
    if not ordered:
        return ()
    groups: list[tuple[int, int]] = []
    start = previous = ordered[0]
    for index in ordered[1:]:
        if index != previous + 1:
            groups.append((start, previous + 1))
            start = index
        previous = index
    groups.append((start, previous + 1))
    return tuple(groups)


def _split_two(value: Grid, separator: int, axis: str) -> tuple[Grid, Grid]:
    height, width = _shape(value)
    if axis == "horizontal":
        lines = [row for row in range(height) if all(cell == separator for cell in value[row])]
        groups = _line_groups(lines)
        if len(groups) != 1 or groups[0][0] == 0 or groups[0][1] == height:
            raise _Undefined("separator is not one internal horizontal run")
        start, stop = groups[0]
        return tuple(value[:start]), tuple(value[stop:])
    if axis == "vertical":
        lines = [
            column
            for column in range(width)
            if all(value[row][column] == separator for row in range(height))
        ]
        groups = _line_groups(lines)
        if len(groups) != 1 or groups[0][0] == 0 or groups[0][1] == width:
            raise _Undefined("separator is not one internal vertical run")
        start, stop = groups[0]
        left = tuple(tuple(row[:start]) for row in value)
        right = tuple(tuple(row[stop:]) for row in value)
        return left, right
    raise _Undefined("unknown panel axis")


def _intervals(length: int, separators: set[int]) -> tuple[tuple[int, int], ...]:
    result: list[tuple[int, int]] = []
    start = 0
    for index in range(length + 1):
        if index == length or index in separators:
            if start < index:
                result.append((start, index))
            start = index + 1
    return tuple(result)


def _split_lattice(value: Grid, separator: int, max_panels: int) -> tuple[Grid, ...]:
    height, width = _shape(value)
    row_lines = {
        row for row in range(height) if all(cell == separator for cell in value[row])
    }
    column_lines = {
        column
        for column in range(width)
        if all(value[row][column] == separator for row in range(height))
    }
    if 0 in row_lines or height - 1 in row_lines or 0 in column_lines or width - 1 in column_lines:
        raise _Undefined("edge-colored bands are not panel separators")
    row_intervals = _intervals(height, row_lines)
    column_intervals = _intervals(width, column_lines)
    count = len(row_intervals) * len(column_intervals)
    if not 2 <= count <= max_panels:
        raise _Undefined("separator does not define a bounded panel lattice")
    return tuple(
        _slice(value, top, left, bottom - top, right - left)
        for top, bottom in row_intervals
        for left, right in column_intervals
    )


def _program(core: Mapping[str, Any], prefix: Sequence[Mapping[str, Any]], post: str) -> dict[str, Any]:
    steps = [dict(item) for item in prefix] + [dict(core)]
    if post != "id":
        steps.append({"operator": "dihedral", "transform": post})
    if len(steps) == 1:
        return steps[0]
    return {"operator": "compose", "steps": steps, "composition_depth": len(steps)}


class _Collector:
    def __init__(
        self,
        demonstrations: Sequence[tuple[Grid, Grid]],
        tests: Sequence[Grid],
        limits: Limits,
    ) -> None:
        self.demonstrations = tuple(demonstrations)
        self.tests = tuple(tests)
        self.limits = limits
        self.attempts = 0
        self.proposals: list[dict[str, Any]] = []

    def consider(
        self,
        family: str,
        program: Mapping[str, Any],
        execute: Callable[[Grid], Grid],
        complexity: int,
        *,
        construction_depth: int,
        shape_rule: str,
    ) -> None:
        if self.attempts >= self.limits.max_hypotheses:
            return
        self.attempts += 1
        try:
            # Serializing here also proves that the program is portable JSON,
            # rather than a closure masquerading as a program record.
            _canonical(program)
            train_predictions = tuple(
                _checked(execute(source), self.limits)
                for source, _ in self.demonstrations
            )
            if any(
                predicted != expected
                for predicted, (_, expected) in zip(train_predictions, self.demonstrations)
            ):
                return
            test_predictions = tuple(
                _checked(execute(source), self.limits) for source in self.tests
            )
        except (_Undefined, IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
            return
        candidate = {
            "family": family,
            "program": json.loads(_canonical(program)),
            "train_outputs": [_plain(value) for value in train_predictions],
            "test_outputs": [_plain(value) for value in test_predictions],
            "complexity": int(complexity),
            "evidence": {
                "all_demonstrations_exact": True,
                "demonstration_count": len(self.demonstrations),
                "test_count": len(self.tests),
                "construction_depth": int(construction_depth),
                "shape_rule": shape_rule,
                "output_shapes": [list(_shape(value)) for value in test_predictions],
                "bounded_search": True,
            },
        }
        self.proposals.append(candidate)


def _resolve_preprocessed(
    inputs: Sequence[Grid], preprocess: Callable[[Grid], Grid]
) -> tuple[Grid, ...]:
    return tuple(preprocess(value) for value in inputs)


def _infer_substitutions(
    collector: _Collector,
    sources: Sequence[Grid],
    targets: Sequence[Grid],
    preprocess: Callable[[Grid], Grid],
    test_sources: Sequence[Grid],
    prefix: Sequence[Mapping[str, Any]],
    family: str | None = None,
    complexity_add: int = 0,
    post: str = "id",
) -> None:
    factors: list[tuple[int, int]] = []
    for source, target in zip(sources, targets):
        source_height, source_width = _shape(source)
        target_height, target_width = _shape(target)
        if target_height % source_height or target_width % source_width:
            return
        factors.append((target_height // source_height, target_width // source_width))
    if not factors or len(set(factors)) != 1:
        return
    block_height, block_width = factors[0]
    if (
        (block_height, block_width) == (1, 1)
        or block_height > collector.limits.max_factor
        or block_width > collector.limits.max_factor
    ):
        return

    observations: dict[int, Grid] = {}
    consistent = True
    for source, target in zip(sources, targets):
        for row in range(len(source)):
            for column in range(len(source[0])):
                color = source[row][column]
                patch = _slice(
                    target,
                    row * block_height,
                    column * block_width,
                    block_height,
                    block_width,
                )
                if color in observations and observations[color] != patch:
                    consistent = False
                observations.setdefault(color, patch)
    if consistent:
        mapping = dict(observations)

        def execute_concrete(raw: Grid, mapping: Mapping[int, Grid] = mapping) -> Grid:
            source = preprocess(raw)

            def block(color: int) -> Grid:
                if color not in mapping:
                    raise _Undefined("unseen substitution symbol")
                return mapping[color]

            return _d4(_substitute(source, block), post)

        core = {
            "operator": "pixel_substitution",
            "block_shape": [block_height, block_width],
            "symbols": [
                {"color": color, "pattern": _plain(mapping[color])}
                for color in sorted(mapping)
            ],
            "shape": {"kind": "multiply", "rows": block_height, "columns": block_width},
        }
        collector.consider(
            family or "pixel_substitution",
            _program(core, prefix, post),
            execute_concrete,
            complexity_add + 18 + len(mapping) * block_height * block_width,
            construction_depth=len(prefix) + 1 + int(post != "id"),
            shape_rule=f"multiply({block_height},{block_width})",
        )

    for role in ("zero", "mode", "corner"):
        mask: list[list[int | None]] = [
            [None for _ in range(block_width)] for _ in range(block_height)
        ]
        blank_valid = True
        mask_valid = True
        saw_background = False
        saw_foreground = False
        active_observations: list[tuple[Grid, int]] = []
        for source, target in zip(sources, targets):
            background = _background(source, role)
            for row in range(len(source)):
                for column in range(len(source[0])):
                    color = source[row][column]
                    patch = _slice(
                        target,
                        row * block_height,
                        column * block_width,
                        block_height,
                        block_width,
                    )
                    if color == background:
                        saw_background = True
                        if any(cell != background for patch_row in patch for cell in patch_row):
                            blank_valid = False
                            mask_valid = False
                    else:
                        saw_foreground = True
                        active_observations.append((patch, background))
                        for local_row in range(block_height):
                            for local_column in range(block_width):
                                value = patch[local_row][local_column]
                                code = 1 if value == color else 0 if value == background else -1
                                if code < 0:
                                    mask_valid = False
                                    continue
                                prior = mask[local_row][local_column]
                                if prior is not None and prior != code:
                                    mask_valid = False
                                mask[local_row][local_column] = code
        if blank_valid and mask_valid and saw_background and saw_foreground and all(
            value is not None for row in mask for value in row
        ) and any(value == 1 for row in mask for value in row):
            frozen_mask = tuple(tuple(int(value) for value in row) for row in mask)

            def execute_mask(raw: Grid, role: str = role, frozen_mask: Grid = frozen_mask) -> Grid:
                source = preprocess(raw)
                background = _background(source, role)

                def block(color: int) -> Grid:
                    if color == background:
                        return tuple(
                            tuple(background for _ in range(block_width))
                            for _ in range(block_height)
                        )
                    return tuple(
                        tuple(color if mark else background for mark in mask_row)
                        for mask_row in frozen_mask
                    )

                return _d4(_substitute(source, block), post)

            core = {
                "operator": "mask_kronecker_substitution",
                "background": role,
                "mask": _plain(frozen_mask),
                "shape": {"kind": "multiply", "rows": block_height, "columns": block_width},
            }
            collector.consider(
                family or "mask_kronecker",
                _program(core, prefix, post),
                execute_mask,
                complexity_add + 5 + block_height * block_width + sum(map(sum, frozen_mask)),
                construction_depth=len(prefix) + 1 + int(post != "id"),
                shape_rule=f"kronecker({block_height},{block_width})",
            )

        # A fixed motif is useful when carrier colors select placement but do
        # not determine motif colors.  Background-valued cells remain dynamic.
        if blank_valid and saw_background and active_observations:
            template: list[list[int | str]] = []
            for local_row in range(block_height):
                template_row: list[int | str] = []
                for local_column in range(block_width):
                    values = [patch[local_row][local_column] for patch, _ in active_observations]
                    backgrounds = [background for _, background in active_observations]
                    if all(value == background for value, background in zip(values, backgrounds)):
                        template_row.append("background")
                    elif len(set(values)) == 1:
                        template_row.append(values[0])
                    else:
                        template_row.append("invalid")
                template.append(template_row)
            if all(token != "invalid" for row in template for token in row) and any(
                isinstance(token, int) for row in template for token in row
            ):
                frozen_template = tuple(tuple(row) for row in template)

                def execute_motif(
                    raw: Grid,
                    role: str = role,
                    frozen_template: tuple[tuple[int | str, ...], ...] = frozen_template,
                ) -> Grid:
                    source = preprocess(raw)
                    background = _background(source, role)

                    def block(color: int) -> Grid:
                        if color == background:
                            return tuple(
                                tuple(background for _ in range(block_width))
                                for _ in range(block_height)
                            )
                        return tuple(
                            tuple(background if token == "background" else int(token) for token in row)
                            for row in frozen_template
                        )

                    return _d4(_substitute(source, block), post)

                core = {
                    "operator": "carrier_motif_substitution",
                    "background": role,
                    "motif": [list(row) for row in frozen_template],
                    "shape": {"kind": "multiply", "rows": block_height, "columns": block_width},
                }
                collector.consider(
                    family or "motif_stamping",
                    _program(core, prefix, post),
                    execute_motif,
                    complexity_add + 10 + block_height * block_width,
                    construction_depth=len(prefix) + 1 + int(post != "id"),
                    shape_rule=f"carrier_stamp({block_height},{block_width})",
                )


def _layout_separator_color(
    target: Grid,
    rows: int,
    columns: int,
    tile_height: int,
    tile_width: int,
    separator_width: int,
) -> int:
    values: set[int] = set()
    total_height, total_width = _shape(target)
    for row in range(total_height):
        within_row = row % (tile_height + separator_width)
        row_gap = separator_width > 0 and within_row >= tile_height and row < total_height - tile_height
        for column in range(total_width):
            within_column = column % (tile_width + separator_width)
            column_gap = (
                separator_width > 0
                and within_column >= tile_width
                and column < total_width - tile_width
            )
            if row_gap or column_gap:
                values.add(target[row][column])
    if len(values) != 1:
        raise _Undefined("layout separator is not uniform")
    return next(iter(values))


def _infer_layouts(
    collector: _Collector,
    sources: Sequence[Grid],
    targets: Sequence[Grid],
    preprocess: Callable[[Grid], Grid],
    test_sources: Sequence[Grid],
    prefix: Sequence[Mapping[str, Any]],
    family: str | None = None,
    complexity_add: int = 0,
) -> None:
    known_sources = tuple(sources) + tuple(test_sources)
    maximum_layout = min(4, collector.limits.max_factor)
    for rows in range(1, maximum_layout + 1):
        for columns in range(1, maximum_layout + 1):
            if rows * columns < 2 or rows * columns > 16:
                continue
            for separator_width in (0, 1, 2):
                compatible = True
                separator_colors: list[int] = []
                for source, target in zip(sources, targets):
                    height, width = _shape(source)
                    expected = (
                        rows * height + (rows - 1) * separator_width,
                        columns * width + (columns - 1) * separator_width,
                    )
                    if _shape(target) != expected:
                        compatible = False
                        break
                    if separator_width:
                        try:
                            separator_colors.append(
                                _layout_separator_color(
                                    target, rows, columns, height, width, separator_width
                                )
                            )
                        except _Undefined:
                            compatible = False
                            break
                if not compatible:
                    continue
                separator_specs: list[Mapping[str, Any] | None] = []
                if separator_width == 0:
                    separator_specs.append(None)
                else:
                    if len(set(separator_colors)) == 1:
                        separator_specs.append(
                            {"kind": "literal", "color": separator_colors[0]}
                        )
                    for role in ("zero", "mode", "corner"):
                        if all(
                            color == _background(source, role)
                            for source, color in zip(sources, separator_colors)
                        ):
                            separator_specs.append({"kind": "background", "role": role})
                unique_specs = {
                    _canonical(spec): spec for spec in separator_specs
                }
                for separator_spec in (unique_specs[key] for key in sorted(unique_specs)):
                    options_by_position: list[tuple[str, ...]] = []
                    for position in range(rows * columns):
                        tile_row, tile_column = divmod(position, columns)
                        options: list[str] = []
                        for name in D4:
                            valid = True
                            for source, target in zip(sources, targets):
                                height, width = _shape(source)
                                transformed = _d4(source, name)
                                if _shape(transformed) != (height, width):
                                    valid = False
                                    break
                                top = tile_row * (height + separator_width)
                                left = tile_column * (width + separator_width)
                                if _slice(target, top, left, height, width) != transformed:
                                    valid = False
                                    break
                            if valid:
                                options.append(name)
                        if not options:
                            compatible = False
                            break
                        # Quotient transform aliases by their behavior on all
                        # visible inputs.  Symmetric demonstrations therefore
                        # cannot create an exponential syntactic accident.
                        representatives: dict[str, str] = {}
                        for name in options:
                            signature = _canonical([_plain(_d4(value, name)) for value in known_sources])
                            representatives.setdefault(signature, name)
                        options_by_position.append(tuple(sorted(representatives.values())))
                    if not compatible or len(options_by_position) != rows * columns:
                        continue
                    combinations = 1
                    for options in options_by_position:
                        combinations *= len(options)
                    if combinations > collector.limits.max_layout_combinations:
                        continue
                    for transforms in itertools.product(*options_by_position):

                        def execute_layout(
                            raw: Grid,
                            transforms: tuple[str, ...] = tuple(transforms),
                            separator_spec: Mapping[str, Any] | None = separator_spec,
                        ) -> Grid:
                            source = preprocess(raw)
                            separator = _separator_value(separator_spec, source)
                            return _layout(
                                source,
                                rows,
                                columns,
                                transforms,
                                separator_width,
                                separator,
                            )

                        core = {
                            "operator": "dihedral_tile_layout",
                            "rows": rows,
                            "columns": columns,
                            "transforms": list(transforms),
                            "separator_width": separator_width,
                            "separator": separator_spec,
                            "shape": {
                                "kind": "tile_layout",
                                "rows": rows,
                                "columns": columns,
                                "separator_width": separator_width,
                            },
                        }
                        collector.consider(
                            family or "tile_mirror_rotation_layout",
                            _program(core, prefix, "id"),
                            execute_layout,
                            complexity_add
                            + 4
                            + rows * columns
                            + sum(name != "id" for name in transforms)
                            + separator_width,
                            construction_depth=len(prefix) + 1,
                            shape_rule=f"tile({rows},{columns},separator={separator_width})",
                        )


_BODY_LAYOUTS: tuple[tuple[str, int, int, tuple[str, ...]], ...] = (
    ("mirror_right", 1, 2, ("id", "fliplr")),
    ("mirror_left", 1, 2, ("fliplr", "id")),
    ("mirror_down", 2, 1, ("id", "flipud")),
    ("mirror_up", 2, 1, ("flipud", "id")),
    ("mirror_quadrants", 2, 2, ("id", "fliplr", "flipud", "r180")),
    ("rotation_pinwheel", 2, 2, ("id", "r90", "r270", "r180")),
)


def _apply_layout_body(value: Grid, body: str) -> Grid:
    for name, rows, columns, transforms in _BODY_LAYOUTS:
        if name == body:
            return _layout(value, rows, columns, transforms, 0, 0)
    raise _Undefined("unknown iterative layout body")


def _infer_layout_iterations(
    collector: _Collector,
    sources: Sequence[Grid],
    targets: Sequence[Grid],
    preprocess: Callable[[Grid], Grid],
    prefix: Sequence[Mapping[str, Any]],
    family: str | None = None,
    complexity_add: int = 0,
) -> None:
    for body, _, _, _ in _BODY_LAYOUTS:
        for depth in range(1, collector.limits.max_depth + 1):

            def execute(
                raw: Grid, body: str = body, depth: int = depth
            ) -> Grid:
                state = preprocess(raw)
                for _ in range(depth):
                    state = _checked(_apply_layout_body(state, body), collector.limits)
                return state

            try:
                if execute(collector.demonstrations[0][0]) != collector.demonstrations[0][1]:
                    continue
            except _Undefined:
                continue
            core = {
                "operator": "shared_body_iteration",
                "body": {"operator": "dihedral_layout", "name": body},
                "depth": depth,
                "depth_bound": 4,
            }
            collector.consider(
                family or "shared_body_iteration",
                _program(core, prefix, "id"),
                execute,
                complexity_add + 4 + depth,
                construction_depth=len(prefix) + depth,
                shape_rule=f"iterate_layout({body},{depth})",
            )


def _iterate_mask(
    value: Grid,
    background_role: str,
    mask: Grid,
    depth: int,
    limits: Limits,
) -> Grid:
    background = _background(value, background_role)
    state = value
    for _ in range(depth):
        state_height, state_width = _shape(state)
        mask_height, mask_width = _shape(mask)
        if (
            state_height * mask_height > limits.max_side
            or state_width * mask_width > limits.max_side
            or state_height * state_width * mask_height * mask_width
            > limits.max_grid_cells
        ):
            raise _Undefined("iterated mask exceeds construction bound")

        def block(color: int) -> Grid:
            if color == background:
                return tuple(tuple(background for _ in row) for row in mask)
            return tuple(
                tuple(color if mark else background for mark in row) for row in mask
            )

        state = _substitute(state, block)
    return state


def _integer_root(value: int, depth: int, maximum: int) -> int | None:
    for base in range(1, maximum + 1):
        power = base**depth
        if power == value:
            return base
        if power > value:
            break
    return None


def _infer_mask_iterations(
    collector: _Collector,
    sources: Sequence[Grid],
    targets: Sequence[Grid],
    preprocess: Callable[[Grid], Grid],
    prefix: Sequence[Mapping[str, Any]],
    family: str | None = None,
    complexity_add: int = 0,
) -> None:
    for depth in range(2, collector.limits.max_depth + 1):
        base_shapes: list[tuple[int, int]] = []
        for source, target in zip(sources, targets):
            source_height, source_width = _shape(source)
            target_height, target_width = _shape(target)
            if target_height % source_height or target_width % source_width:
                base_shapes = []
                break
            base_height = _integer_root(
                target_height // source_height, depth, min(3, collector.limits.max_factor)
            )
            base_width = _integer_root(
                target_width // source_width, depth, min(3, collector.limits.max_factor)
            )
            if base_height is None or base_width is None:
                base_shapes = []
                break
            base_shapes.append((base_height, base_width))
        if not base_shapes or len(set(base_shapes)) != 1:
            continue
        mask_height, mask_width = base_shapes[0]
        area = mask_height * mask_width
        if (mask_height, mask_width) == (1, 1) or area > 9:
            continue
        for bits in range(1, 1 << area):
            mask = tuple(
                tuple((bits >> (row * mask_width + column)) & 1 for column in range(mask_width))
                for row in range(mask_height)
            )
            for role in ("zero", "mode", "corner"):

                def execute(
                    raw: Grid,
                    role: str = role,
                    mask: Grid = mask,
                    depth: int = depth,
                ) -> Grid:
                    return _iterate_mask(
                        preprocess(raw), role, mask, depth, collector.limits
                    )

                try:
                    if execute(collector.demonstrations[0][0]) != collector.demonstrations[0][1]:
                        continue
                except _Undefined:
                    continue
                core = {
                    "operator": "shared_body_iteration",
                    "body": {
                        "operator": "mask_kronecker_substitution",
                        "background": role,
                        "mask": _plain(mask),
                    },
                    "depth": depth,
                    "depth_bound": 4,
                }
                collector.consider(
                    family or "shared_body_iteration",
                    _program(core, prefix, "id"),
                    execute,
                    complexity_add + 4 + depth + sum(map(sum, mask)),
                    construction_depth=len(prefix) + depth,
                    shape_rule=f"iterate_kronecker({mask_height},{mask_width},{depth})",
                )


def _recursive_motif(
    value: Grid,
    background_role: str,
    transform: str,
    color_mode: str,
    depth: int,
    limits: Limits,
) -> Grid:
    background = _background(value, background_role)
    motif = _d4(value, transform)
    state = value
    for _ in range(depth):
        state_height, state_width = _shape(state)
        motif_height, motif_width = _shape(motif)
        if (
            state_height * motif_height > limits.max_side
            or state_width * motif_width > limits.max_side
            or state_height * state_width * motif_height * motif_width
            > limits.max_grid_cells
        ):
            raise _Undefined("recursive motif exceeds construction bound")

        def block(color: int) -> Grid:
            if color == background:
                return tuple(tuple(background for _ in row) for row in motif)
            if color_mode == "literal":
                return motif
            if color_mode == "recolor":
                return tuple(
                    tuple(color if cell != background else background for cell in row)
                    for row in motif
                )
            raise _Undefined("unknown recursive motif color mode")

        state = _substitute(state, block)
    return state


def _infer_recursive_motifs(
    collector: _Collector,
    preprocess: Callable[[Grid], Grid],
    prefix: Sequence[Mapping[str, Any]],
    family: str | None = None,
    complexity_add: int = 0,
) -> None:
    for role in ("zero", "mode", "corner"):
        for transform in D4:
            for color_mode in ("literal", "recolor"):
                for depth in range(1, collector.limits.max_depth + 1):

                    def execute(
                        raw: Grid,
                        role: str = role,
                        transform: str = transform,
                        color_mode: str = color_mode,
                        depth: int = depth,
                    ) -> Grid:
                        return _recursive_motif(
                            preprocess(raw),
                            role,
                            transform,
                            color_mode,
                            depth,
                            collector.limits,
                        )

                    try:
                        if execute(collector.demonstrations[0][0]) != collector.demonstrations[0][1]:
                            continue
                    except _Undefined:
                        continue
                    core = {
                        "operator": "recursive_motif_substitution",
                        "background": role,
                        "motif_source": "initial_input",
                        "motif_transform": transform,
                        "color_mode": color_mode,
                        "depth": depth,
                        "depth_bound": 4,
                    }
                    collector.consider(
                        family or "recursive_motif",
                        _program(core, prefix, "id"),
                        execute,
                        complexity_add + 5 + depth + int(transform != "id"),
                        construction_depth=len(prefix) + depth,
                        shape_rule=f"recursive_motif({transform},{depth})",
                    )


def _active(color: int, background: int, spec: Mapping[str, Any]) -> bool:
    kind = spec.get("kind")
    if kind == "non_background":
        return color != background
    if kind == "color":
        selected = spec.get("color")
        return color == selected
    raise _Undefined("invalid carrier activation rule")


def _stamp_panels(
    value: Grid,
    separator: int,
    axis: str,
    carrier_index: int,
    carrier_transform: str,
    motif_transform: str,
    carrier_background_role: str,
    motif_background_role: str,
    active_spec: Mapping[str, Any],
    color_mode: str,
) -> Grid:
    panels = _split_two(value, separator, axis)
    carrier = _d4(panels[carrier_index], carrier_transform)
    motif = _d4(panels[1 - carrier_index], motif_transform)
    carrier_background = _background(carrier, carrier_background_role)
    motif_background = _background(motif, motif_background_role)

    def block(color: int) -> Grid:
        if not _active(color, carrier_background, active_spec):
            return tuple(tuple(carrier_background for _ in row) for row in motif)
        if color_mode == "literal":
            return motif
        if color_mode == "support_literal":
            return tuple(
                tuple(
                    carrier_background if cell == motif_background else cell for cell in row
                )
                for row in motif
            )
        if color_mode == "recolor":
            return tuple(
                tuple(color if cell != motif_background else carrier_background for cell in row)
                for row in motif
            )
        raise _Undefined("unknown stamping color mode")

    return _substitute(carrier, block)


def _infer_embedded_motif_stamps(collector: _Collector) -> None:
    raw_sources = tuple(source for source, _ in collector.demonstrations)
    first_palette = sorted({cell for row in raw_sources[0] for cell in row})
    for separator in first_palette:
        for axis in ("horizontal", "vertical"):
            try:
                train_panels = tuple(_split_two(value, separator, axis) for value in raw_sources)
                tuple(_split_two(value, separator, axis) for value in collector.tests)
            except _Undefined:
                continue
            for carrier_index in (0, 1):
                palette_intersection = set(
                    cell for row in train_panels[0][carrier_index] for cell in row
                )
                for panels in train_panels[1:]:
                    palette_intersection &= {
                        cell for row in panels[carrier_index] for cell in row
                    }
                active_specs: list[Mapping[str, Any]] = [{"kind": "non_background"}]
                active_specs.extend(
                    {"kind": "color", "color": color}
                    for color in sorted(palette_intersection)
                )
                for carrier_transform in D4:
                    for motif_transform in D4:
                        # All later choices preserve these dimensions.  This
                        # relational shape guard avoids enumerating thousands
                        # of paint variants for an impossible panel pairing.
                        if any(
                            _shape(target)
                            != (
                                _shape(_d4(panels[carrier_index], carrier_transform))[0]
                                * _shape(_d4(panels[1 - carrier_index], motif_transform))[0],
                                _shape(_d4(panels[carrier_index], carrier_transform))[1]
                                * _shape(_d4(panels[1 - carrier_index], motif_transform))[1],
                            )
                            for panels, (_, target) in zip(
                                train_panels, collector.demonstrations
                            )
                        ):
                            continue
                        for carrier_background_role in ("zero", "mode", "corner"):
                            for motif_background_role in ("zero", "mode", "corner"):
                                for active_spec in active_specs:
                                    for color_mode in ("literal", "support_literal", "recolor"):

                                        def execute(
                                            raw: Grid,
                                            separator: int = separator,
                                            axis: str = axis,
                                            carrier_index: int = carrier_index,
                                            carrier_transform: str = carrier_transform,
                                            motif_transform: str = motif_transform,
                                            carrier_background_role: str = carrier_background_role,
                                            motif_background_role: str = motif_background_role,
                                            active_spec: Mapping[str, Any] = active_spec,
                                            color_mode: str = color_mode,
                                        ) -> Grid:
                                            return _stamp_panels(
                                                raw,
                                                separator,
                                                axis,
                                                carrier_index,
                                                carrier_transform,
                                                motif_transform,
                                                carrier_background_role,
                                                motif_background_role,
                                                active_spec,
                                                color_mode,
                                            )

                                        try:
                                            if execute(raw_sources[0]) != collector.demonstrations[0][1]:
                                                continue
                                        except _Undefined:
                                            continue
                                        program = {
                                            "operator": "separator_carrier_motif_stamp",
                                            "separator": separator,
                                            "axis": axis,
                                            "carrier_panel": carrier_index,
                                            "motif_panel": 1 - carrier_index,
                                            "carrier_transform": carrier_transform,
                                            "motif_transform": motif_transform,
                                            "carrier_background": carrier_background_role,
                                            "motif_background": motif_background_role,
                                            "activation": dict(active_spec),
                                            "color_mode": color_mode,
                                            "shape": {"kind": "carrier_times_motif"},
                                        }
                                        collector.consider(
                                            "motif_stamping",
                                            program,
                                            execute,
                                            13
                                            + int(carrier_transform != "id")
                                            + int(motif_transform != "id")
                                            + int(active_spec.get("kind") == "color"),
                                            construction_depth=2,
                                            shape_rule="carrier_times_motif",
                                        )


def _infer_panel_expansions(collector: _Collector) -> None:
    raw_train = tuple(source for source, _ in collector.demonstrations)
    raw_targets = tuple(target for _, target in collector.demonstrations)
    first_palette = sorted({cell for row in raw_train[0] for cell in row})
    seen: set[str] = set()
    for separator in first_palette:
        try:
            train_panel_sets = tuple(
                _split_lattice(value, separator, collector.limits.max_panels)
                for value in raw_train
            )
            test_panel_sets = tuple(
                _split_lattice(value, separator, collector.limits.max_panels)
                for value in collector.tests
            )
        except _Undefined:
            continue
        counts = {len(panels) for panels in train_panel_sets + test_panel_sets}
        if len(counts) != 1:
            continue
        panel_count = next(iter(counts))
        for panel_index in range(panel_count):
            sources = tuple(panels[panel_index] for panels in train_panel_sets)
            test_sources = tuple(panels[panel_index] for panels in test_panel_sets)
            signature = _digest(
                {
                    "separator": separator,
                    "panel": panel_index,
                    "train": [_plain(value) for value in sources],
                    "test": [_plain(value) for value in test_sources],
                }
            )
            if signature in seen:
                continue
            seen.add(signature)

            def preprocess(
                raw: Grid,
                separator: int = separator,
                panel_index: int = panel_index,
                panel_count: int = panel_count,
            ) -> Grid:
                panels = _split_lattice(raw, separator, collector.limits.max_panels)
                if len(panels) != panel_count:
                    raise _Undefined("panel arity changed")
                return panels[panel_index]

            prefix = (
                {
                    "operator": "select_separator_panel",
                    "separator": separator,
                    "panel_index": panel_index,
                    "panel_count": panel_count,
                },
            )
            _infer_substitutions(
                collector,
                sources,
                raw_targets,
                preprocess,
                test_sources,
                prefix,
                family="separator_panel_expansion",
                complexity_add=6,
            )
            _infer_layouts(
                collector,
                sources,
                raw_targets,
                preprocess,
                test_sources,
                prefix,
                family="separator_panel_expansion",
                complexity_add=6,
            )
            _infer_layout_iterations(
                collector,
                sources,
                raw_targets,
                preprocess,
                prefix,
                family="separator_panel_expansion",
                complexity_add=6,
            )
            _infer_mask_iterations(
                collector,
                sources,
                raw_targets,
                preprocess,
                prefix,
                family="separator_panel_expansion",
                complexity_add=6,
            )
            _infer_recursive_motifs(
                collector,
                preprocess,
                prefix,
                family="separator_panel_expansion",
                complexity_add=6,
            )


def _infer_conservative_compositions(
    collector: _Collector,
    raw_sources: Sequence[Grid],
    raw_targets: Sequence[Grid],
) -> None:
    # One input-side dihedral normalization followed by one learned expansion.
    for transform in D4[1:]:
        sources = tuple(_d4(value, transform) for value in raw_sources)
        test_sources = tuple(_d4(value, transform) for value in collector.tests)

        def preprocess(raw: Grid, transform: str = transform) -> Grid:
            return _d4(raw, transform)

        prefix = ({"operator": "dihedral", "transform": transform},)
        _infer_substitutions(
            collector,
            sources,
            raw_targets,
            preprocess,
            test_sources,
            prefix,
            family="conservative_composition",
            complexity_add=4,
        )

    # One expansion followed by one output-side dihedral normalization.
    inverse = {
        "fliplr": "fliplr",
        "flipud": "flipud",
        "r180": "r180",
        "transpose": "transpose",
        "r90": "r270",
        "r270": "r90",
        "anti_transpose": "anti_transpose",
    }
    identity = lambda value: value
    for post in D4[1:]:
        normalized_targets = tuple(_d4(value, inverse[post]) for value in raw_targets)
        _infer_substitutions(
            collector,
            raw_sources,
            normalized_targets,
            identity,
            collector.tests,
            (),
            family="conservative_composition",
            complexity_add=4,
            post=post,
        )


def _finalize(collector: _Collector) -> list[dict[str, Any]]:
    family_priority = {
        "shared_body_iteration": 0,
        "recursive_motif": 1,
        "motif_stamping": 2,
        "separator_panel_expansion": 3,
        "mask_kronecker": 4,
        "tile_mirror_rotation_layout": 5,
        "conservative_composition": 6,
        "pixel_substitution": 7,
    }
    ordered = sorted(
        collector.proposals,
        key=lambda item: (
            item["complexity"],
            family_priority.get(item["family"], 99),
            item["family"],
            _canonical(item["program"]),
        ),
    )
    seen_behaviors: set[str] = set()
    result: list[dict[str, Any]] = []
    for candidate in ordered:
        behavior = _digest(candidate["test_outputs"])
        if behavior in seen_behaviors:
            continue
        seen_behaviors.add(behavior)
        candidate["evidence"]["behavior_hash"] = behavior
        result.append(candidate)
        if len(result) >= collector.limits.max_candidates:
            break
    return result


def compile_task(
    task: Mapping[str, Any], limits: Mapping[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Return deterministic, exact-replay expansion candidates.

    The normal negative result is ``[]``.  No exception caused by task data,
    resource bounds, or an inapplicable construction escapes this boundary.
    """

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
        collector = _Collector(demonstrations, tests, bounds)
        raw_sources = tuple(source for source, _ in demonstrations)
        raw_targets = tuple(target for _, target in demonstrations)
        identity = lambda value: value

        # This lane is intentionally restricted to genuine shape construction.
        if not any(_shape(source) != _shape(target) for source, target in demonstrations):
            return []

        _infer_substitutions(
            collector,
            raw_sources,
            raw_targets,
            identity,
            tests,
            (),
        )
        _infer_layouts(
            collector,
            raw_sources,
            raw_targets,
            identity,
            tests,
            (),
        )
        _infer_layout_iterations(collector, raw_sources, raw_targets, identity, ())
        _infer_mask_iterations(collector, raw_sources, raw_targets, identity, ())
        _infer_recursive_motifs(collector, identity, ())
        _infer_embedded_motif_stamps(collector)
        _infer_panel_expansions(collector)
        _infer_conservative_compositions(collector, raw_sources, raw_targets)
        return _finalize(collector)
    except (
        _Undefined,
        IndexError,
        KeyError,
        OverflowError,
        TypeError,
        ValueError,
        ZeroDivisionError,
    ):
        return []


__all__ = ["D4", "Limits", "compile_task"]
