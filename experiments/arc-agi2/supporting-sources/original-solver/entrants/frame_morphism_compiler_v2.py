"""Retrospective score-seeded keyed-exemplar frame morphisms.

Author: Komorebi P.

This entrant is intentionally independent of the frozen v1 implementation.  It
learns a color-keyed geometric action from demonstrations, then applies that
action to scene-local exemplars and isolated key tokens.  No task identity or
corpus value is available to the runtime.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, fields
import hashlib
import itertools
import json
from typing import Any, Iterable, Mapping, Sequence


AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.frame_morphism_compiler.program.v2"

Cell = tuple[int, int]
Grid = tuple[tuple[int, ...], ...]
Pair = tuple[Grid, Grid]


class Undefined(ValueError):
    """The structural preconditions do not determine an output."""


@dataclass(frozen=True)
class Limits:
    max_examples: int = 8
    max_tests: int = 4
    max_grid_area: int = 900
    max_colors: int = 10
    max_component_area: int = 81
    max_key_colors: int = 3
    max_rule_maps: int = 512
    max_executor_calls: int = 512
    max_gauge_checks: int = 192
    max_candidates: int = 1

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        defaults = cls()
        names = {field.name for field in fields(cls)}
        data: dict[str, int] = {}
        for name in names:
            raw = value.get(name, getattr(defaults, name))
            if name == "max_candidates" and "candidate_cap" in value:
                raw = value["candidate_cap"]
            if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
                raise Undefined("invalid positive limit")
            data[name] = min(raw, getattr(defaults, name))
        return cls(**data)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, (list, tuple)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for row in value:
        if not isinstance(row, (list, tuple)) or not row:
            raise Undefined("grid rows must be nonempty sequences")
        frozen: list[int] = []
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("grid colors must be integers in [0, 9]")
            frozen.append(cell)
        if width is None:
            width = len(frozen)
        elif len(frozen) != width:
            raise Undefined("grid must be rectangular")
        rows.append(tuple(frozen))
    if len(rows) * int(width or 0) > limits.max_grid_area:
        raise Undefined("grid area exceeds limit")
    if len({cell for row in rows for cell in row}) > limits.max_colors:
        raise Undefined("color count exceeds limit")
    return tuple(rows)


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train = task.get("train")
    tests = task.get("test")
    if not isinstance(train, (list, tuple)) or not 3 <= len(train) <= limits.max_examples:
        raise Undefined("three or more demonstrations are required")
    if not isinstance(tests, (list, tuple)) or not 1 <= len(tests) <= limits.max_tests:
        raise Undefined("invalid test set")
    demonstrations: list[Pair] = []
    for example in train:
        if not isinstance(example, Mapping) or "input" not in example or "output" not in example:
            raise Undefined("malformed demonstration")
        source = _grid(example["input"], limits)
        target = _grid(example["output"], limits)
        demonstrations.append((source, target))
    probes: list[Grid] = []
    for example in tests:
        if not isinstance(example, Mapping) or "input" not in example:
            raise Undefined("malformed test example")
        # A supplied test output is deliberately ignored.
        probes.append(_grid(example["input"], limits))
    return tuple(demonstrations), tuple(probes)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def _components(grid: Grid, background: int) -> tuple[frozenset[Cell], ...]:
    height, width = _shape(grid)
    seen: set[Cell] = set()
    result: list[frozenset[Cell]] = []
    directions = tuple(
        (dr, dc)
        for dr in (-1, 0, 1)
        for dc in (-1, 0, 1)
        if (dr, dc) != (0, 0)
    )
    for row in range(height):
        for column in range(width):
            if grid[row][column] == background or (row, column) in seen:
                continue
            queue = deque([(row, column)])
            seen.add((row, column))
            component: set[Cell] = set()
            while queue:
                current = queue.popleft()
                component.add(current)
                for dr, dc in directions:
                    neighbor = current[0] + dr, current[1] + dc
                    if not (0 <= neighbor[0] < height and 0 <= neighbor[1] < width):
                        continue
                    if neighbor in seen or grid[neighbor[0]][neighbor[1]] == background:
                        continue
                    seen.add(neighbor)
                    queue.append(neighbor)
            result.append(frozenset(component))
    return tuple(sorted(result, key=lambda cells: (min(cells), len(cells), tuple(sorted(cells)))))


_MATRICES: dict[str, tuple[tuple[int, int], tuple[int, int]]] = {
    "identity": ((1, 0), (0, 1)),
    "rotate_90": ((0, 1), (-1, 0)),
    "rotate_180": ((-1, 0), (0, -1)),
    "rotate_270": ((0, -1), (1, 0)),
    "reflect_columns": ((1, 0), (0, -1)),
    "reflect_rows": ((-1, 0), (0, 1)),
    "reflect_main_diagonal": ((0, 1), (1, 0)),
    "reflect_anti_diagonal": ((0, -1), (-1, 0)),
}
_TRANSFORMS = tuple(sorted(_MATRICES))


def _matmul(
    left: tuple[tuple[int, int], tuple[int, int]],
    right: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    return (
        (
            left[0][0] * right[0][0] + left[0][1] * right[1][0],
            left[0][0] * right[0][1] + left[0][1] * right[1][1],
        ),
        (
            left[1][0] * right[0][0] + left[1][1] * right[1][0],
            left[1][0] * right[0][1] + left[1][1] * right[1][1],
        ),
    )


def _transpose(matrix: tuple[tuple[int, int], tuple[int, int]]) -> tuple[tuple[int, int], tuple[int, int]]:
    return ((matrix[0][0], matrix[1][0]), (matrix[0][1], matrix[1][1]))


def _matrix_name(matrix: tuple[tuple[int, int], tuple[int, int]]) -> str:
    matches = [name for name, candidate in _MATRICES.items() if candidate == matrix]
    if len(matches) != 1:
        raise Undefined("invalid dihedral transform")
    return matches[0]


def _relative_transform(cell: Cell, name: str) -> Cell:
    try:
        matrix = _MATRICES[name]
    except KeyError as exc:
        raise Undefined("unknown dihedral transform") from exc
    row, column = cell
    return (
        matrix[0][0] * row + matrix[0][1] * column,
        matrix[1][0] * row + matrix[1][1] * column,
    )


def _transform_grid(grid: Grid, name: str) -> Grid:
    height, width = _shape(grid)
    mapped = {
        (row, column): _relative_transform((row, column), name)
        for row in range(height)
        for column in range(width)
    }
    row_shift = -min(row for row, _ in mapped.values())
    column_shift = -min(column for _, column in mapped.values())
    placed = {
        (target[0] + row_shift, target[1] + column_shift): grid[source[0]][source[1]]
        for source, target in mapped.items()
    }
    new_height = max(row for row, _ in placed) + 1
    new_width = max(column for _, column in placed) + 1
    return tuple(
        tuple(placed[(row, column)] for column in range(new_width))
        for row in range(new_height)
    )


def _conjugate(inner: str, outer: str) -> str:
    outer_matrix = _MATRICES[outer]
    matrix = _matmul(
        _matmul(outer_matrix, _MATRICES[inner]),
        _transpose(outer_matrix),
    )
    return _matrix_name(matrix)


def _scene_templates(
    grid: Grid, limits: Limits
) -> dict[int, tuple[dict[Cell, int], tuple[Cell, ...]]]:
    """Return key -> (anchor-relative exemplar, isolated target anchors)."""

    background = _background(grid)
    components = _components(grid, background)
    owner = {cell: component for component in components for cell in component}
    by_color: dict[int, list[Cell]] = {}
    for row, line in enumerate(grid):
        for column, color in enumerate(line):
            if color != background:
                by_color.setdefault(color, []).append((row, column))

    candidates: dict[int, list[tuple[dict[Cell, int], tuple[Cell, ...]]]] = {}
    for component in components:
        if not 2 <= len(component) <= limits.max_component_area:
            continue
        colors = Counter(grid[row][column] for row, column in component)
        if len(colors) < 2:
            continue
        for key_color, count in colors.items():
            if count != 1:
                continue
            anchor = next(cell for cell in component if grid[cell[0]][cell[1]] == key_color)
            outside = [cell for cell in by_color[key_color] if cell not in component]
            if not outside or any(len(owner[cell]) != 1 for cell in outside):
                continue
            template = {
                (row - anchor[0], column - anchor[1]): grid[row][column]
                for row, column in component
            }
            candidates.setdefault(key_color, []).append((template, tuple(sorted(outside))))

    if not candidates or len(candidates) > limits.max_key_colors:
        raise Undefined("no bounded keyed exemplar scene")
    result: dict[int, tuple[dict[Cell, int], tuple[Cell, ...]]] = {}
    for key_color, variants in candidates.items():
        unique = {
            _canonical(
                {
                    "template": [[row, column, color] for (row, column), color in sorted(template.items())],
                    "targets": [list(cell) for cell in targets],
                }
            ): (template, targets)
            for template, targets in variants
        }
        if len(unique) != 1:
            raise Undefined("key does not identify one exemplar")
        result[key_color] = next(iter(unique.values()))
    return result


def _edits_for_rule(
    grid: Grid,
    key_color: int,
    template: Mapping[Cell, int],
    targets: Sequence[Cell],
    transform: str,
) -> dict[Cell, int]:
    background = _background(grid)
    height, width = _shape(grid)
    transformed: dict[Cell, int] = {}
    for relative, color in template.items():
        target_relative = _relative_transform(relative, transform)
        prior = transformed.get(target_relative, color)
        if prior != color:
            raise Undefined("transform collapsed differently colored cells")
        transformed[target_relative] = color
    if transformed.get((0, 0)) != key_color:
        raise Undefined("key anchor was not preserved")

    edits: dict[Cell, int] = {}
    for anchor in targets:
        for (dr, dc), color in transformed.items():
            row, column = anchor[0] + dr, anchor[1] + dc
            if not (0 <= row < height and 0 <= column < width):
                raise Undefined("transformed exemplar crosses the canvas")
            current = grid[row][column]
            if current not in {background, color}:
                raise Undefined("transformed exemplar collides with the scene")
            if current == background:
                previous = edits.get((row, column), color)
                if previous != color:
                    raise Undefined("transformed exemplars conflict")
                edits[(row, column)] = color
    if not edits:
        raise Undefined("rule adds no cells")
    return edits


def _merge_edits(parts: Iterable[Mapping[Cell, int]]) -> dict[Cell, int]:
    result: dict[Cell, int] = {}
    for part in parts:
        for cell, color in part.items():
            prior = result.get(cell, color)
            if prior != color:
                raise Undefined("keyed rules collide")
            result[cell] = color
    return result


def _render(grid: Grid, edits: Mapping[Cell, int]) -> Grid:
    result = [list(row) for row in grid]
    for (row, column), color in edits.items():
        result[row][column] = color
    return tuple(tuple(row) for row in result)


def _rules_from_program(program: Mapping[str, Any]) -> dict[int, str]:
    if program.get("schema") != SCHEMA or program.get("operator") != "complete_keyed_exemplars":
        raise Undefined("unsupported program")
    raw = program.get("key_rules")
    if not isinstance(raw, list) or not raw:
        raise Undefined("missing key rules")
    rules: dict[int, str] = {}
    for item in raw:
        if not isinstance(item, Mapping):
            raise Undefined("malformed key rule")
        color = item.get("key_color")
        transform = item.get("transform")
        if isinstance(color, bool) or not isinstance(color, int) or not 0 <= color <= 9:
            raise Undefined("invalid key color")
        if transform not in _MATRICES or color in rules:
            raise Undefined("invalid or duplicate key rule")
        rules[color] = str(transform)
    return rules


def _execute_internal(
    program: Mapping[str, Any], grid: Grid, limits: Limits
) -> tuple[Grid, dict[str, Any]]:
    rules = _rules_from_program(program)
    scene = _scene_templates(grid, limits)
    if not set(scene).issubset(rules):
        raise Undefined("scene contains an unlearned key")
    edits = _merge_edits(
        _edits_for_rule(grid, key, template, targets, rules[key])
        for key, (template, targets) in sorted(scene.items())
    )
    output = _render(grid, edits)
    return output, {
        "key_count": len(scene),
        "target_count": sum(len(targets) for _, targets in scene.values()),
        "added_cells": len(edits),
        "coordinate_gauge": "anchor_relative_d4",
    }


def _target_additions(source: Grid, target: Grid) -> dict[Cell, int]:
    if _shape(source) != _shape(target):
        raise Undefined("shape-changing demonstration")
    background = _background(source)
    edits: dict[Cell, int] = {}
    for row in range(len(source)):
        for column in range(len(source[0])):
            before, after = source[row][column], target[row][column]
            if before == after:
                continue
            if before != background or after == background:
                raise Undefined("demonstration is not additive exemplar completion")
            edits[(row, column)] = after
    if not edits:
        raise Undefined("demonstration contains no additions")
    return edits


def _pair_rule_maps(source: Grid, target: Grid, limits: Limits) -> tuple[dict[int, str], ...]:
    expected = _target_additions(source, target)
    scene = _scene_templates(source, limits)
    options: list[tuple[int, tuple[tuple[str, dict[Cell, int]], ...]]] = []
    for key, (template, targets) in sorted(scene.items()):
        candidates: list[tuple[str, dict[Cell, int]]] = []
        for transform in _TRANSFORMS:
            try:
                edits = _edits_for_rule(source, key, template, targets, transform)
            except Undefined:
                continue
            if all(expected.get(cell) == color for cell, color in edits.items()):
                candidates.append((transform, edits))
        if not candidates:
            raise Undefined("no transform explains a key")
        options.append((key, tuple(candidates)))

    mappings: dict[str, dict[int, str]] = {}
    for choice in itertools.product(*(candidates for _, candidates in options)):
        try:
            combined = _merge_edits(edits for _, edits in choice)
        except Undefined:
            continue
        if combined != expected:
            continue
        mapping = {key: transform for (key, _), (transform, _) in zip(options, choice)}
        mappings[_canonical(mapping)] = mapping
        if len(mappings) > limits.max_rule_maps:
            raise Undefined("rule-map cap exceeded")
    if not mappings:
        raise Undefined("demonstration has no exact keyed rule map")
    return tuple(mappings[key] for key in sorted(mappings))


def _merge_rule_maps(left: Mapping[int, str], right: Mapping[int, str]) -> dict[int, str] | None:
    result = dict(left)
    for key, transform in right.items():
        if key in result and result[key] != transform:
            return None
        result[key] = transform
    return result


def _program(mapping: Mapping[int, str]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": "complete_keyed_exemplars",
        "key_rules": [
            {"key_color": key, "transform": transform}
            for key, transform in sorted(mapping.items())
        ],
        "description_length": 18 + 2 * len(mapping),
    }


def _induce(demonstrations: Sequence[Pair], limits: Limits) -> tuple[dict[str, Any], ...]:
    partials: list[dict[int, str]] = [{}]
    observations: Counter[int] = Counter()
    for source, target in demonstrations:
        pair_maps = _pair_rule_maps(source, target, limits)
        for key in pair_maps[0]:
            observations[key] += 1
        merged: dict[str, dict[int, str]] = {}
        for partial, pair_map in itertools.product(partials, pair_maps):
            candidate = _merge_rule_maps(partial, pair_map)
            if candidate is None:
                continue
            merged[_canonical(candidate)] = candidate
            if len(merged) > limits.max_rule_maps:
                raise Undefined("cross-demo rule-map cap exceeded")
        if not merged:
            raise Undefined("demonstrations disagree on key semantics")
        partials = [merged[key] for key in sorted(merged)]
    if not observations or any(count < 2 for count in observations.values()):
        raise Undefined("each key action needs repeated demonstration support")
    return tuple(_program(mapping) for mapping in partials)


def _behavior(
    program: Mapping[str, Any], grids: Sequence[Grid], limits: Limits
) -> tuple[Grid, ...]:
    return tuple(_execute_internal(program, grid, limits)[0] for grid in grids)


def _loo(demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, list[dict[str, Any]]]:
    witnesses: list[dict[str, Any]] = []
    for held_index, (source, target) in enumerate(demonstrations):
        subset = tuple(pair for index, pair in enumerate(demonstrations) if index != held_index)
        try:
            programs = _induce(subset, limits)
        except Undefined:
            return False, witnesses
        behaviors: dict[str, tuple[Grid, ...]] = {}
        for program in programs:
            try:
                output = _behavior(program, (source,), limits)
            except Undefined:
                continue
            behaviors[_digest([_plain(grid) for grid in output])] = output
        if len(behaviors) != 1 or next(iter(behaviors.values())) != (target,):
            return False, witnesses
        witnesses.append(
            {
                "held_out_index": held_index,
                "proposal_demo_count": len(subset),
                "held_out_behavior_classes": 1,
                "held_out_exact": True,
                "held_out_output_hash": _digest(_plain(target)),
            }
        )
    return True, witnesses


def _transport_program_d4(program: Mapping[str, Any], outer: str) -> dict[str, Any]:
    transported = json.loads(_canonical(program))
    for rule in transported["key_rules"]:
        rule["transform"] = _conjugate(str(rule["transform"]), outer)
    return transported


def _swap_grid(grid: Grid, left: int, right: int) -> Grid:
    return tuple(
        tuple(right if cell == left else left if cell == right else cell for cell in row)
        for row in grid
    )


def _transport_program_palette(program: Mapping[str, Any], left: int, right: int) -> dict[str, Any]:
    transported = json.loads(_canonical(program))
    for rule in transported["key_rules"]:
        color = int(rule["key_color"])
        rule["key_color"] = right if color == left else left if color == right else color
    transported["key_rules"].sort(key=lambda rule: int(rule["key_color"]))
    return transported


def _gauge(
    program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits
) -> tuple[bool, int, int]:
    d4_checks = 0
    palette_checks = 0
    for source, target in demonstrations:
        for outer in _TRANSFORMS:
            d4_checks += 1
            if d4_checks + palette_checks > limits.max_gauge_checks:
                return False, d4_checks, palette_checks
            transformed_source = _transform_grid(source, outer)
            transformed_target = _transform_grid(target, outer)
            transported = _transport_program_d4(program, outer)
            try:
                actual = _execute_internal(transported, transformed_source, limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if actual != transformed_target:
                return False, d4_checks, palette_checks

        colors = sorted({cell for row in source for cell in row} | {cell for row in target for cell in row})
        absent = next((color for color in range(10) if color not in colors), None)
        swaps = list(itertools.combinations(colors, 2))
        if absent is not None:
            swaps.extend((color, absent) for color in colors)
        for left, right in swaps:
            palette_checks += 1
            if d4_checks + palette_checks > limits.max_gauge_checks:
                return False, d4_checks, palette_checks
            transformed_program = _transport_program_palette(program, left, right)
            try:
                actual = _execute_internal(
                    transformed_program, _swap_grid(source, left, right), limits
                )[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if actual != _swap_grid(target, left, right):
                return False, d4_checks, palette_checks
    return True, d4_checks, palette_checks


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    limits = Limits()
    grid = _grid(value, limits)
    return _plain(_execute_internal(program, grid, limits)[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    limits = Limits()
    grid = _grid(value, limits)
    output, receipt = _execute_internal(program, grid, limits)
    lifted = {
        "kind": "keyed_exemplar_atlas",
        "shape": list(_shape(grid)),
        "coordinate_identity": "key_anchor_relative",
    }
    applied = {"operator": program["operator"], "receipt": receipt}
    return {
        "output": _plain(output),
        "stages": [
            {"name": "lift-keyed-exemplars", "input": _plain(grid), "output": lifted},
            {"name": "apply-learned-d4-action", "input": lifted, "output": applied},
            {"name": "render-with-lineage", "input": applied, "output": _plain(output)},
        ],
    }


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one uniquely determined keyed-exemplar behavior or abstain."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, probes = _sanitize(task, bounds)
        programs = _induce(demonstrations, bounds)
    except (Undefined, TypeError, ValueError, KeyError, IndexError):
        return []
    if len(programs) > bounds.max_rule_maps:
        return []

    exact: list[dict[str, Any]] = []
    executor_calls = 0
    for program in programs:
        try:
            train_outputs = _behavior(
                program, tuple(source for source, _ in demonstrations), bounds
            )
            executor_calls += len(demonstrations)
            if train_outputs != tuple(target for _, target in demonstrations):
                continue
            _behavior(program, probes, bounds)
            executor_calls += len(probes)
        except Undefined:
            continue
        if executor_calls > bounds.max_executor_calls:
            return []
        exact.append(program)
    if not exact:
        return []

    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = {}
    for program in exact:
        try:
            outputs = _behavior(program, probes, bounds)
        except Undefined:
            continue
        behavior_hash = _digest([_plain(grid) for grid in outputs])
        behaviors.setdefault(behavior_hash, []).append((program, outputs))
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
    representative, outputs = equivalent[0]

    loo_ok, witnesses = _loo(demonstrations, bounds)
    if not loo_ok:
        return []
    gauge_ok, d4_checks, palette_checks = _gauge(representative, demonstrations, bounds)
    if not gauge_ok:
        return []
    try:
        train_outputs = _behavior(
            representative, tuple(source for source, _ in demonstrations), bounds
        )
    except Undefined:
        return []
    if train_outputs != tuple(target for _, target in demonstrations):
        return []

    candidate = {
        "family": "frame_morphism_compiler_v2",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "development_mode": "retrospective_score_seeded",
            "intrinsic_coordinate_frames": True,
            "key_actions_induced_from_demonstrations": True,
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_witnesses": witnesses,
            "finite_test_behavior_classes": 1,
            "equivalent_program_count": len(equivalent),
            "d4_gauge_checks": d4_checks,
            "palette_gauge_checks": palette_checks,
            "test_labels_used": False,
            "behavior_hash": behavior_hash,
        },
    }
    replayed_train = [replay_program(representative, _plain(source)) for source, _ in demonstrations]
    replayed_test = [replay_program(representative, _plain(probe)) for probe in probes]
    if [item["output"] for item in replayed_train] != candidate["train_outputs"]:
        return []
    if [item["output"] for item in replayed_test] != candidate["test_outputs"]:
        return []
    return [candidate][: bounds.max_candidates]
