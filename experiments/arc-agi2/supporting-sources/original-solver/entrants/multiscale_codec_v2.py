"""Score-seeded semantic repairs for the Block 15 multi-scale codec.

V2 preserves the frozen V1 entrant and repairs three generalization faults
exposed only after its G32 prediction freeze was scored:

* scalar codebooks now require injective structural codes, unless the feature
  is an explicit binary predicate; this rejects lossy connectivity aliases;
* stencil cells inherit the uniquely nearest side legend, including interior
  cells, while equidistant axes retain the stencil color;
* panel progression transports the latest motif into the extrapolated frame
  before extending its periodic or boundary signature.

The repairs are retrospective public-training development.  Runtime remains
task-ID-free and accepts only demonstration pairs plus held-out inputs.  No
solution, score, cached output, fingerprint, or task suppression is available
to the entrant.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
import json
from typing import Any

import multiscale_codec as _v1


Grid = _v1.Grid
Cell = _v1.Cell
Pair = _v1.Pair
Limits = _v1.Limits
Undefined = _v1.Undefined
AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.multiscale_codec.program.v2"


def _orthogonal_symmetry_span3(grid: Grid, background_role: str) -> str:
    mask = _v1._mask(grid, background_role)
    horizontal = mask == tuple(reversed(mask))
    vertical = mask == _v1._reflect(mask)
    span = max(_v1._shape(mask))
    return _v1._canonical(horizontal and vertical and span >= 3)


def _feature(grid: Grid, background_role: str, feature: str) -> str:
    if feature == "orthogonal_symmetry_span3":
        return _orthogonal_symmetry_span3(grid, background_role)
    return _v1._mask_feature(grid, background_role, feature)


def _infer_scalar_programs(demonstrations: Sequence[Pair]) -> list[dict[str, Any]]:
    if any(_v1._shape(target) != (1, 1) for _, target in demonstrations):
        return []
    if any(len(source) > 9 or len(source[0]) > 9 for source, _ in demonstrations):
        return []
    roles = (
        ["zero"]
        if all(0 in {cell for row in source for cell in row} for source, _ in demonstrations)
        else ["mode"]
    )
    # Atomic connectivity is retained only when it is an injective code.  Rich
    # topology and exact canonical masks are likewise forbidden from merging
    # several structures into one label.  The final feature is an explicit
    # two-class causal predicate and is therefore allowed to abstract.
    features = (
        "components4",
        "canonical_mask",
        "topology",
        "orthogonal_symmetry_span3",
    )
    programs: list[dict[str, Any]] = []
    for role in roles:
        for feature in features:
            mapping: dict[str, int] = {}
            valid = True
            try:
                for source, target in demonstrations:
                    key = _feature(source, role, feature)
                    value = target[0][0]
                    if key in mapping and mapping[key] != value:
                        valid = False
                        break
                    mapping[key] = value
            except Undefined:
                valid = False
            if not valid or len(mapping) < 2 or len(set(mapping.values())) < 2:
                continue
            if feature != "orthogonal_symmetry_span3" and len(mapping) != len(set(mapping.values())):
                continue
            if feature == "orthogonal_symmetry_span3" and set(mapping) != {"false", "true"}:
                continue
            programs.append(
                {
                    "schema": SCHEMA,
                    "operator": "scalar_feature_codebook",
                    "background_role": role,
                    "feature": feature,
                    "mapping": [[key, mapping[key]] for key in sorted(mapping)],
                    "description_length": 9 + len(mapping),
                    "score_seeded_repair": True,
                }
            )
    return programs


def _scalar_codebook(program: Mapping[str, Any], grid: Grid) -> Grid:
    role = str(program.get("background_role"))
    feature = str(program.get("feature"))
    raw_mapping = program.get("mapping")
    if not isinstance(raw_mapping, list):
        raise Undefined("malformed codebook")
    mapping: dict[str, int] = {}
    for record in raw_mapping:
        if (
            not isinstance(record, list)
            or len(record) != 2
            or not isinstance(record[0], str)
            or isinstance(record[1], bool)
            or not isinstance(record[1], int)
            or not 0 <= record[1] <= 9
        ):
            raise Undefined("malformed codebook entry")
        mapping[record[0]] = int(record[1])
    key = _feature(grid, role, feature)
    if key not in mapping:
        raise Undefined("unseen structural code")
    return ((mapping[key],),)


def _nearest_side_stencil_legend(grid: Grid) -> Grid:
    background = _v1._background(grid)
    height, width = _v1._shape(grid)
    outputs: set[Grid] = set()
    runs = _v1._horizontal_runs(grid, background)
    for top_run, bottom_run in __import__("itertools").combinations(runs, 2):
        top, start, end, top_color = top_run
        bottom, start2, end2, bottom_color = bottom_run
        if start != start2 or end != end2 or bottom <= top + 1:
            continue
        left, right = start - 1, end + 1
        if left < 0 or right >= width:
            continue
        if any(
            grid[row][column] != background
            for row, column in ((top, left), (top, right), (bottom, left), (bottom, right))
        ):
            continue
        left_values = [grid[row][left] for row in range(top + 1, bottom)]
        right_values = [grid[row][right] for row in range(top + 1, bottom)]
        if (
            not left_values
            or background in left_values
            or len(set(left_values)) != 1
            or background in right_values
            or len(set(right_values)) != 1
        ):
            continue
        left_color, right_color = left_values[0], right_values[0]
        side_colors = (top_color, right_color, bottom_color, left_color)
        if len(set(side_colors)) != 4:
            continue
        if any(
            grid[row][column] != background
            for row in range(top + 1, bottom)
            for column in range(left + 1, right)
        ):
            continue
        frame_cells = (
            {(top, column) for column in range(start, end + 1)}
            | {(bottom, column) for column in range(start, end + 1)}
            | {(row, left) for row in range(top + 1, bottom)}
            | {(row, right) for row in range(top + 1, bottom)}
        )
        outside = [
            (row, column)
            for row in range(height)
            for column in range(width)
            if grid[row][column] != background and (row, column) not in frame_cells
        ]
        if not outside:
            continue
        stencil_colors = {grid[row][column] for row, column in outside}
        if len(stencil_colors) != 1:
            continue
        stencil_color = next(iter(stencil_colors))
        stencil = _v1._crop(grid, _v1._bbox(outside))
        inner_height, inner_width = bottom - top - 1, right - left - 1
        if _v1._shape(stencil) != (inner_height, inner_width):
            continue
        occupied = {
            (row, column)
            for row in range(inner_height)
            for column in range(inner_width)
            if stencil[row][column] == stencil_color
        }
        if not occupied:
            continue
        canvas = [[background] * (inner_width + 2) for _ in range(inner_height + 2)]
        for column in range(1, inner_width + 1):
            canvas[0][column] = top_color
            canvas[-1][column] = bottom_color
        for row in range(1, inner_height + 1):
            canvas[row][0] = left_color
            canvas[row][-1] = right_color
        unique_axes: set[int] = set()
        for row, column in occupied:
            distances = {
                top_color: row,
                right_color: inner_width - 1 - column,
                bottom_color: inner_height - 1 - row,
                left_color: column,
            }
            nearest = min(distances.values())
            winners = {color for color, distance in distances.items() if distance == nearest}
            if len(winners) == 1:
                color = next(iter(winners))
                unique_axes.add(color)
                canvas[row + 1][column + 1] = color
            else:
                canvas[row + 1][column + 1] = stencil_color
        if len(unique_axes) < 2:
            continue
        outputs.add(_v1._freeze(canvas))
    if len(outputs) != 1:
        raise Undefined("nearest-side stencil legend is absent or ambiguous")
    return next(iter(outputs))


def _panel_affine_growth(grid: Grid) -> Grid:
    outputs: set[Grid] = set()
    for _axis, panels in _v1._split_panels(grid):
        base = panels[-1]
        visible = panels[:-1]
        if len(visible) < 2 or any(_v1._shape(panel) != _v1._shape(base) for panel in visible):
            continue
        try:
            base_background = _v1._background(base)
        except Undefined:
            continue
        if any(
            panel[row][column] == base_background and panel[row][column] != base[row][column]
            for panel in visible
            for row in range(len(base))
            for column in range(len(base[0]))
        ):
            continue
        colors = sorted({cell for panel in panels for row in panel for cell in row})
        records: list[
            tuple[int, Grid, tuple[int, int, int, int], tuple[int, int, int, int]]
        ] = []
        valid = True
        for color in colors:
            if color == base_background:
                continue
            occurrences: list[tuple[int, Grid, set[Cell]]] = []
            for index, panel in enumerate(visible):
                support = {
                    (row, column)
                    for row, line in enumerate(panel)
                    for column, value in enumerate(line)
                    if value == color and value != base[row][column]
                }
                if support:
                    occurrences.append((index, panel, support))
            if not occurrences:
                continue
            if len(occurrences) < 2:
                valid = False
                break
            periods = {right[0] - left[0] for left, right in zip(occurrences, occurrences[1:])}
            if len(periods) != 1:
                valid = False
                break
            recurrence = next(iter(periods))
            if len(visible) - occurrences[-1][0] != recurrence:
                continue
            previous, latest = occurrences[-2], occurrences[-1]
            records.append((color, latest[1], _v1._bbox(previous[2]), _v1._bbox(latest[2])))
        if not valid or not records:
            continue
        canvas = [list(row) for row in base]
        for color, latest_panel, box0, box1 in sorted(records, reverse=True):
            predicted = tuple(2 * newest - older for older, newest in zip(box0, box1))
            top, bottom, left, right = predicted
            panel_height, panel_width = _v1._shape(base)
            if not (0 <= top <= bottom < panel_height and 0 <= left <= right < panel_width):
                valid = False
                break
            old_height = box1[1] - box1[0] + 1
            old_width = box1[3] - box1[2] + 1
            new_height = bottom - top + 1
            new_width = right - left + 1
            row_signatures = tuple(
                tuple(
                    latest_panel[box1[0] + row][box1[2] + column] == color
                    for column in range(old_width)
                )
                for row in range(old_height)
            )
            column_signatures = tuple(
                tuple(row_signatures[row][column] for row in range(old_height))
                for column in range(old_width)
            )

            def period(signatures: Sequence[tuple[bool, ...]]) -> int | None:
                for candidate in range(1, len(signatures) // 2 + 1):
                    if all(signatures[index] == signatures[index % candidate] for index in range(len(signatures))):
                        return candidate
                return None

            row_period, column_period = period(row_signatures), period(column_signatures)

            def project(offset: int, new_size: int, size: int, repeat: int | None) -> int:
                if repeat is not None:
                    return offset % repeat
                if size == 1 or new_size == 1:
                    return 0
                numerator = offset * (size - 1)
                denominator = new_size - 1
                lower, remainder = divmod(numerator, denominator)
                # Ties use the earlier motif coordinate.  D4 checks below
                # reject a program whenever this convention is not covariant
                # for the demonstrated structure.
                return lower if 2 * remainder <= denominator else min(size - 1, lower + 1)

            # V2 maps motif-local coordinates into the predicted box.  V1
            # instead reused absolute coordinates, which failed when a motif
            # translated while growing.
            for row in range(new_height):
                source_row = box1[0] + project(row, new_height, old_height, row_period)
                for column in range(new_width):
                    source_column = box1[2] + project(column, new_width, old_width, column_period)
                    if latest_panel[source_row][source_column] == color:
                        canvas[top + row][left + column] = color
        if valid:
            outputs.add(_v1._freeze(canvas))
    if len(outputs) != 1:
        raise Undefined("panel progression is absent or ambiguous")
    return next(iter(outputs))


_FIXED_PROGRAMS: tuple[dict[str, Any], ...] = (
    {"schema": SCHEMA, "operator": "line_layer_order", "description_length": 9},
    {"schema": SCHEMA, "operator": "corner_frame_payload", "description_length": 14},
    {"schema": SCHEMA, "operator": "nearest_side_stencil_legend", "description_length": 16, "score_seeded_repair": True},
    {"schema": SCHEMA, "operator": "panel_affine_growth", "description_length": 13, "score_seeded_repair": True},
)


def _execute(program: Mapping[str, Any], grid: Grid) -> Grid:
    if program.get("schema") != SCHEMA:
        raise Undefined("wrong program schema")
    operator = program.get("operator")
    if operator == "line_layer_order":
        return _v1._line_layer_order(grid)
    if operator == "scalar_feature_codebook":
        return _scalar_codebook(program, grid)
    if operator == "corner_frame_payload":
        return _v1._corner_frame_payload(grid)
    if operator == "nearest_side_stencil_legend":
        return _nearest_side_stencil_legend(grid)
    if operator == "panel_affine_growth":
        return _panel_affine_growth(grid)
    raise Undefined("unknown operator")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    if not isinstance(program, Mapping):
        raise ValueError("program must be a mapping")
    return _v1._plain(_execute(program, _v1._grid(value)))


def replay_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    return execute_program(program, value)


def _programs(demonstrations: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    programs = list(_FIXED_PROGRAMS) + _infer_scalar_programs(demonstrations)
    unique = {_v1._canonical(program): program for program in programs}
    return tuple(unique[key] for key in sorted(unique))


def _behavior(program: Mapping[str, Any], grids: Sequence[Grid]) -> tuple[Grid, ...]:
    return tuple(_execute(program, grid) for grid in grids)


def _counterfactuals(program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int]:
    checks = 0
    invariant = program.get("operator") in {"line_layer_order", "scalar_feature_codebook"}
    for source, target in demonstrations:
        for quarter_turns in range(4):
            for reflected in (False, True):
                transformed_source = _v1._transform(source, quarter_turns, reflected)
                expected = target if invariant else _v1._transform(target, quarter_turns, reflected)
                checks += 1
                if checks > limits.max_counterfactual_checks:
                    return False, checks
                try:
                    actual = _execute(program, transformed_source)
                except (Undefined, ValueError, KeyError, IndexError, ZeroDivisionError):
                    return False, checks
                if actual != expected:
                    return False, checks
    return True, checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _v1._sanitize(task, bounds)
    except (Undefined, TypeError, ValueError, KeyError):
        return []
    programs = _programs(demonstrations)
    if len(programs) > bounds.max_programs:
        return []
    expected = tuple(target for _, target in demonstrations)
    exact: list[tuple[dict[str, Any], tuple[Grid, ...]]] = []
    calls = 0
    for program in programs:
        try:
            train_outputs = _behavior(program, tuple(source for source, _ in demonstrations))
            calls += len(demonstrations)
            if train_outputs != expected:
                continue
            test_outputs = _behavior(program, tests)
            calls += len(tests)
            if calls > bounds.max_executor_calls:
                return []
        except (Undefined, TypeError, ValueError, KeyError, IndexError, ZeroDivisionError):
            continue
        exact.append((program, test_outputs))
    if not exact:
        return []
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = defaultdict(list)
    for program, outputs in exact:
        behaviors[_v1._digest([_v1._plain(grid) for grid in outputs])].append((program, outputs))
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalents = next(iter(sorted(behaviors.items())))
    equivalents.sort(key=lambda item: (int(item[0]["description_length"]), _v1._canonical(item[0])))
    representative, test_outputs = equivalents[0]
    counterfactual_ok, counterfactual_checks = _counterfactuals(representative, demonstrations, bounds)
    if not counterfactual_ok:
        return []
    train_outputs = _behavior(representative, tuple(source for source, _ in demonstrations))
    if train_outputs != expected:
        return []
    candidate = {
        "family": "multiscale_codec_v2",
        "program": json.loads(_v1._canonical(representative)),
        "train_outputs": [_v1._plain(grid) for grid in train_outputs],
        "test_outputs": [_v1._plain(grid) for grid in test_outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "development_mode": "retrospective_public_training_score_seeded_repair",
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "serialized_replay_program": True,
            "finite_enumeration_complete": True,
            "programs_enumerated": len(programs),
            "exact_programs": len(exact),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalents),
            "d4_counterfactual_checks": counterfactual_checks,
            "injective_scalar_guard": True,
            "bounded_search": True,
            "hard_caps_exhausted": False,
            "task_identity_observed": False,
            "test_labels_observed_at_runtime": False,
            "solution_store_observed_at_runtime": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _v1._digest(candidate)
    return [candidate][: bounds.max_candidates]


__all__ = ["AUTHOR", "Limits", "SCHEMA", "compile_task", "execute_program", "replay_program"]
