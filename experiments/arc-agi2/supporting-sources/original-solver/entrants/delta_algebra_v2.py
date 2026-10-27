"""Provenance-isolated structural repairs for the Block 14 delta algebra.

Version 1 exposed two general failure witnesses without requiring access to a
held-out raster: a modal-background inversion and leakage from a local cell
predicate outside a coherent rectangle.  This entrant does not modify or
import v1.  It adds exactly two graph-level task-local macros:

* a corner-anchored component-depth wave over solid rectangles; and
* one-frame erosion of the unique largest solid monochrome rectangle.

Both macros are induced solely from demonstrations, serialize no resolved
coordinates, replay independently, require leave-one-demo-out recovery, and
must form a unique minimum-description behavior over every test input.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block14.delta_algebra_v2.program.v1"
SCAN_SCHEMA = "komorebi.pr_lasm.block14.delta_algebra_v2.scan_freeze.v1"
AUTHOR = "Komorebi P."
ORTHOGONAL: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))


class Undefined(ValueError):
    """A structural role is absent, tied, or outside the finite budgets."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 10
    max_components: int = 160
    max_rectangle_evaluations: int = 500_000
    max_executor_calls: int = 2_048
    max_gauge_checks: int = 1_024
    max_candidates: int = 1
    mdl_slack: int = 0

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        defaults = cls()
        ceilings = {
            "max_grid_cells": 3_600,
            "max_examples": 20,
            "max_components": 512,
            "max_rectangle_evaluations": 2_000_000,
            "max_executor_calls": 100_000,
            "max_gauge_checks": 4_096,
            "max_candidates": 1,
            "mdl_slack": 2,
        }
        result: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            raw = value.get(name, value.get("candidate_cap", getattr(defaults, name)) if name == "max_candidates" else getattr(defaults, name))
            if isinstance(raw, bool) or not isinstance(raw, int):
                raise Undefined(f"limits.{name} must be an integer")
            minimum = 0 if name == "mdl_slack" else 1
            if raw < minimum:
                raise Undefined(f"limits.{name} is below {minimum}")
            result[name] = min(raw, ceilings[name])
        return cls(**result)


@dataclass(frozen=True, slots=True)
class Component:
    color: int
    cells: frozenset[Cell]
    bbox: tuple[int, int, int, int]

    @property
    def height(self) -> int:
        return self.bbox[1] - self.bbox[0] + 1

    @property
    def width(self) -> int:
        return self.bbox[3] - self.bbox[2] + 1

    @property
    def solid(self) -> bool:
        return len(self.cells) == self.height * self.width


@dataclass(frozen=True, slots=True)
class Rectangle:
    top: int
    bottom: int
    left: int
    right: int
    color: int

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def area(self) -> int:
        return self.height * self.width


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row must be nonempty")
        row: list[int] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, bool) or not isinstance(raw_cell, int) or not 0 <= raw_cell <= 9:
                raise Undefined("ARC color is invalid")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > limits.max_grid_cells:
        raise Undefined("grid exceeds cell budget")
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
    demonstrations: list[Pair] = []
    for example in train:
        if not isinstance(example, Mapping):
            raise Undefined("demonstration is invalid")
        source = _grid(example.get("input"), limits)
        target = _grid(example.get("output"), limits)
        if _shape(source) != _shape(target) or source == target:
            raise Undefined("v2 macros require nonidentity same-shape pairs")
        demonstrations.append((source, target))
    tests = tuple(
        _grid(example.get("input"), limits)
        for example in test
        if isinstance(example, Mapping)
    )
    if len(tests) != len(test):
        raise Undefined("test example is invalid")
    return tuple(demonstrations), tests


def _uniform_corners(grid: Grid) -> int:
    corners = (grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1])
    if len(set(corners)) != 1:
        raise Undefined("corner identity is tied")
    return corners[0]


def _bbox(cells: frozenset[Cell]) -> tuple[int, int, int, int]:
    if not cells:
        raise Undefined("empty component")
    return (
        min(row for row, _ in cells),
        max(row for row, _ in cells),
        min(column for _, column in cells),
        max(column for _, column in cells),
    )


def _components(grid: Grid, background: int, limits: Limits) -> tuple[Component, ...]:
    height, width = _shape(grid)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background
    }
    answer: list[Component] = []
    while remaining:
        seed = min(remaining)
        color = grid[seed[0]][seed[1]]
        remaining.remove(seed)
        cells = {seed}
        queue = deque([seed])
        while queue:
            row, column = queue.popleft()
            for dr, dc in ORTHOGONAL:
                point = row + dr, column + dc
                if point in remaining and grid[point[0]][point[1]] == color:
                    remaining.remove(point)
                    cells.add(point)
                    queue.append(point)
        frozen = frozenset(cells)
        answer.append(Component(color, frozen, _bbox(frozen)))
        if len(answer) > limits.max_components:
            raise Undefined("component budget exhausted")
    return tuple(sorted(answer, key=lambda item: (item.bbox, item.color)))


def _action_record(source_colors: set[int], target_colors: set[int], background: int | None = None) -> dict[str, Any]:
    if len(target_colors) != 1:
        raise Undefined("emission role is not uniform")
    target = next(iter(target_colors))
    if len(source_colors) == 1 and target == next(iter(source_colors)):
        return {"kind": "source_color"}
    if background is not None and target == background:
        return {"kind": "background"}
    return {"kind": "literal", "color": target}


def _resolve_action(action: Mapping[str, Any], *, source_color: int, background: int | None = None) -> int:
    kind = action.get("kind")
    if kind == "source_color":
        return source_color
    if kind == "background":
        if background is None:
            raise Undefined("background action is unavailable")
        return background
    if kind == "literal":
        value = action.get("color")
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 9:
            raise Undefined("literal emission is invalid")
        return value
    raise Undefined("unknown emission action")


def _execute_depth_wave(program: Mapping[str, Any], grid: Grid, limits: Limits) -> tuple[Grid, dict[str, Any]]:
    background = _uniform_corners(grid)
    components = _components(grid, background, limits)
    if not components or any(not component.solid for component in components):
        raise Undefined("depth wave requires solid rectangular components")
    raw_mapping = program.get("depth_actions")
    if not isinstance(raw_mapping, Sequence) or isinstance(raw_mapping, (str, bytes)) or not raw_mapping:
        raise Undefined("depth action table is invalid")
    mapping: dict[int, Mapping[str, Any]] = {}
    for item in raw_mapping:
        if not isinstance(item, Mapping) or not isinstance(item.get("depth"), int) or not isinstance(item.get("action"), Mapping):
            raise Undefined("depth action is invalid")
        depth = int(item["depth"])
        if depth < 0 or depth in mapping:
            raise Undefined("depth action key is invalid")
        mapping[depth] = item["action"]
    output = [list(row) for row in grid]
    component_records: list[dict[str, Any]] = []
    for component in components:
        top, bottom, left, right = component.bbox
        depths: Counter[int] = Counter()
        for row, column in component.cells:
            depth = min(row - top, bottom - row, column - left, right - column)
            action = mapping.get(depth)
            if action is None:
                raise Undefined("test requires an unseen component depth")
            output[row][column] = _resolve_action(action, source_color=component.color, background=background)
            depths[depth] += 1
        component_records.append(
            {
                "shape": [component.height, component.width],
                "source_color": component.color,
                "depth_histogram": {str(depth): count for depth, count in sorted(depths.items())},
            }
        )
    return tuple(tuple(row) for row in output), {
        "macro": "component_depth_wave",
        "background": background,
        "component_count": len(components),
        "components": component_records,
    }


def _largest_rectangles(grid: Grid, limits: Limits) -> tuple[Rectangle, ...]:
    height, width = _shape(grid)
    best_area = 0
    winners: set[Rectangle] = set()
    evaluations = 0
    palette = sorted({cell for row in grid for cell in row})
    for color in palette:
        heights = [0] * width
        for bottom in range(height):
            for column in range(width):
                heights[column] = heights[column] + 1 if grid[bottom][column] == color else 0
            for left in range(width):
                minimum_height = height + 1
                for right in range(left, width):
                    evaluations += 1
                    if evaluations > limits.max_rectangle_evaluations:
                        raise Undefined("rectangle search budget exhausted")
                    minimum_height = min(minimum_height, heights[right])
                    if minimum_height == 0:
                        continue
                    rectangle = Rectangle(bottom - minimum_height + 1, bottom, left, right, color)
                    area = rectangle.area
                    if area > best_area:
                        best_area = area
                        winners = {rectangle}
                    elif area == best_area:
                        winners.add(rectangle)
    if best_area == 0:
        raise Undefined("solid rectangle role is absent")
    return tuple(sorted(winners, key=lambda item: (item.top, item.bottom, item.left, item.right, item.color)))


def _unique_largest_rectangle(grid: Grid, limits: Limits) -> Rectangle:
    winners = _largest_rectangles(grid, limits)
    if len(winners) != 1:
        raise Undefined("largest solid rectangle role is tied")
    rectangle = winners[0]
    if rectangle.height < 3 or rectangle.width < 3:
        raise Undefined("largest solid rectangle has no strict erosion")
    return rectangle


def _execute_rectangle_erosion(program: Mapping[str, Any], grid: Grid, limits: Limits) -> tuple[Grid, dict[str, Any]]:
    rectangle = _unique_largest_rectangle(grid, limits)
    thickness = program.get("thickness")
    if thickness != 1:
        raise Undefined("only the frozen one-frame erosion macro is admitted")
    action = program.get("emission")
    if not isinstance(action, Mapping):
        raise Undefined("erosion emission is invalid")
    output = [list(row) for row in grid]
    color = _resolve_action(action, source_color=rectangle.color)
    for row in range(rectangle.top + 1, rectangle.bottom):
        for column in range(rectangle.left + 1, rectangle.right):
            output[row][column] = color
    return tuple(tuple(row) for row in output), {
        "macro": "largest_rectangle_erosion",
        "selected_shape": [rectangle.height, rectangle.width],
        "selected_color": rectangle.color,
        "eroded_shape": [rectangle.height - 2, rectangle.width - 2],
        "emission": color,
    }


def _execute_internal(program: Mapping[str, Any], grid: Grid, limits: Limits) -> tuple[Grid, dict[str, Any]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid v2 program")
    macro = program.get("macro")
    if macro == "component_depth_wave":
        return _execute_depth_wave(program, grid, limits)
    if macro == "largest_rectangle_erosion":
        return _execute_rectangle_erosion(program, grid, limits)
    raise Undefined("unknown v2 macro")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one independently serialized structural repair program."""

    limits = Limits()
    grid = _grid(value, limits)
    return _plain(_execute_internal(program, grid, limits)[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Tournament replay with graph selection and render receipts."""

    limits = Limits()
    grid = _grid(value, limits)
    output, graph_record = _execute_internal(program, grid, limits)
    parsed = {
        "kind": "v2_graph_scene",
        "shape": list(_shape(grid)),
        "palette": sorted({cell for row in grid for cell in row}),
    }
    return {
        "output": _plain(output),
        "stages": [
            {"name": "parse-graph-scene", "input": _plain(grid), "output": parsed},
            {"name": "resolve-structural-macro", "input": parsed, "output": graph_record},
            {"name": "render-graph-edit", "input": graph_record, "output": _plain(output)},
        ],
    }


def _infer_depth_wave(demonstrations: Sequence[Pair], tests: Sequence[Grid], limits: Limits) -> dict[str, Any] | None:
    observations: dict[int, list[tuple[int, int]]] = {}
    try:
        for demo, (source, target) in enumerate(demonstrations):
            background = _uniform_corners(source)
            components = _components(source, background, limits)
            if not components or any(not component.solid for component in components):
                return None
            support = frozenset(cell for component in components for cell in component.cells)
            for row in range(len(source)):
                for column in range(len(source[0])):
                    if (row, column) not in support and source[row][column] != target[row][column]:
                        return None
            for component in components:
                top, bottom, left, right = component.bbox
                for row, column in component.cells:
                    depth = min(row - top, bottom - row, column - left, right - column)
                    observations.setdefault(depth, []).append((component.color, target[row][column]))
        # Cross-demonstration support is enforced by the outer leave-one-out
        # re-induction.  Requiring two witnesses *inside* each LOO fold would
        # incorrectly reject a depth seen in two of three original examples.
        if not observations:
            return None
        actions = []
        for depth in sorted(observations):
            pairs = observations[depth]
            action = _action_record({source for source, _ in pairs}, {target for _, target in pairs})
            if any(_resolve_action(action, source_color=source) != target for source, target in pairs):
                return None
            actions.append({"depth": depth, "action": action})
        program = {
            "schema": SCHEMA,
            "macro": "component_depth_wave",
            "background": "uniform_corners",
            "depth_actions": actions,
            "description_length": 4 + sum(1 + (2 if item["action"]["kind"] == "literal" else 1) for item in actions),
        }
        for source, target in demonstrations:
            if _execute_internal(program, source, limits)[0] != target:
                return None
        for source in tests:
            _execute_internal(program, source, limits)
        return program
    except Undefined:
        return None


def _infer_rectangle_erosion(demonstrations: Sequence[Pair], tests: Sequence[Grid], limits: Limits) -> dict[str, Any] | None:
    emissions: set[int] = set()
    try:
        for source, target in demonstrations:
            rectangle = _unique_largest_rectangle(source, limits)
            interior = {
                (row, column)
                for row in range(rectangle.top + 1, rectangle.bottom)
                for column in range(rectangle.left + 1, rectangle.right)
            }
            changed = {
                (row, column)
                for row in range(len(source))
                for column in range(len(source[0]))
                if source[row][column] != target[row][column]
            }
            if changed != interior:
                return None
            colors = {target[row][column] for row, column in interior}
            if len(colors) != 1:
                return None
            emissions.update(colors)
        if len(emissions) != 1:
            return None
        program = {
            "schema": SCHEMA,
            "macro": "largest_rectangle_erosion",
            "selector": "unique_largest_solid_monochrome_rectangle",
            "thickness": 1,
            "emission": {"kind": "literal", "color": next(iter(emissions))},
            "description_length": 9,
        }
        for source, target in demonstrations:
            if _execute_internal(program, source, limits)[0] != target:
                return None
        for source in tests:
            _execute_internal(program, source, limits)
        return program
    except Undefined:
        return None


def _infer_kind(kind: str, demonstrations: Sequence[Pair], tests: Sequence[Grid], limits: Limits) -> dict[str, Any] | None:
    if kind == "component_depth_wave":
        return _infer_depth_wave(demonstrations, tests, limits)
    if kind == "largest_rectangle_erosion":
        return _infer_rectangle_erosion(demonstrations, tests, limits)
    raise Undefined("unknown inference kind")


def _loo(kind: str, demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int]:
    checks = 0
    for held_out, (source, target) in enumerate(demonstrations):
        training = tuple(pair for index, pair in enumerate(demonstrations) if index != held_out)
        if not training:
            return False, checks
        program = _infer_kind(kind, training, (source,), limits)
        if program is None:
            return False, checks
        try:
            prediction = _execute_internal(program, source, limits)[0]
        except Undefined:
            return False, checks
        checks += 1
        if prediction != target:
            return False, checks
    return True, checks


def _rotate90(grid: Grid) -> Grid:
    return tuple(tuple(row) for row in zip(*reversed(grid)))


def _swap_grid(grid: Grid, left: int, right: int) -> Grid:
    return tuple(tuple(right if value == left else left if value == right else value for value in row) for row in grid)


def _swap_program(program: Mapping[str, Any], left: int, right: int) -> dict[str, Any]:
    result = json.loads(_canonical(program))
    actions: list[dict[str, Any]] = []
    if result["macro"] == "component_depth_wave":
        actions.extend(item["action"] for item in result["depth_actions"])
    else:
        actions.append(result["emission"])
    for action in actions:
        if action.get("kind") == "literal":
            value = action["color"]
            action["color"] = right if value == left else left if value == right else value
    return result


def _gauge(program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    d4_checks = 0
    palette_checks = 0
    for source, target in demonstrations:
        transformed_source, transformed_target = source, target
        pairs: dict[str, tuple[Grid, Grid]] = {}
        for _ in range(4):
            pairs.setdefault(_canonical(_plain(transformed_source)), (transformed_source, transformed_target))
            reflected_source = tuple(tuple(reversed(row)) for row in transformed_source)
            reflected_target = tuple(tuple(reversed(row)) for row in transformed_target)
            pairs.setdefault(_canonical(_plain(reflected_source)), (reflected_source, reflected_target))
            transformed_source, transformed_target = _rotate90(transformed_source), _rotate90(transformed_target)
        for source_variant, target_variant in pairs.values():
            d4_checks += 1
            if d4_checks + palette_checks > limits.max_gauge_checks:
                return False, d4_checks, palette_checks
            try:
                if _execute_internal(program, source_variant, limits)[0] != target_variant:
                    return False, d4_checks, palette_checks
            except Undefined:
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
            try:
                prediction = _execute_internal(_swap_program(program, left, right), _swap_grid(source, left, right), limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if prediction != _swap_grid(target, left, right):
                return False, d4_checks, palette_checks
    return True, d4_checks, palette_checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one unique graph-level repair or abstain."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
    except (Undefined, TypeError, ValueError):
        return []
    candidates: list[tuple[dict[str, Any], int, int, int]] = []
    executor_calls = 0
    for kind in ("component_depth_wave", "largest_rectangle_erosion"):
        program = _infer_kind(kind, demonstrations, tests, bounds)
        if program is None:
            continue
        loo_ok, loo_checks = _loo(kind, demonstrations, bounds)
        if not loo_ok:
            continue
        gauge_ok, d4_checks, palette_checks = _gauge(program, demonstrations, bounds)
        if not gauge_ok:
            continue
        candidates.append((program, loo_checks, d4_checks, palette_checks))
    if not candidates:
        return []
    best = min(int(program["description_length"]) for program, _, _, _ in candidates)
    near = [item for item in candidates if int(item[0]["description_length"]) <= best + bounds.mdl_slack]
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...], int, int, int]]] = {}
    for program, loo_checks, d4_checks, palette_checks in near:
        try:
            outputs = tuple(_execute_internal(program, grid, bounds)[0] for grid in tests)
            executor_calls += len(tests)
        except Undefined:
            continue
        behaviors.setdefault(_digest([_plain(grid) for grid in outputs]), []).append(
            (program, outputs, loo_checks, d4_checks, palette_checks)
        )
    if executor_calls > bounds.max_executor_calls or len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
    program, outputs, loo_checks, d4_checks, palette_checks = equivalent[0]
    try:
        train_outputs = tuple(_execute_internal(program, source, bounds)[0] for source, _ in demonstrations)
    except Undefined:
        return []
    if train_outputs != tuple(target for _, target in demonstrations):
        return []
    candidate = {
        "family": "delta_algebra_v2",
        "program": json.loads(_canonical(program)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in outputs],
        "complexity": int(program["description_length"]),
        "evidence": {
            "structural_repair": True,
            "provenance_isolated_from_v1": True,
            "all_demos_exact": True,
            "exact_replay": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_checks": loo_checks,
            "enumeration_complete": True,
            "macros_enumerated": 2,
            "hard_caps_exhausted": False,
            "near_mdl_programs": len(near),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "d4_covariance_checks": d4_checks,
            "palette_covariance_checks": palette_checks,
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
        "train": [{"input": example["input"], "output": example["output"]} for example in task["train"]],
        "test": [{"input": example["input"]} for example in task["test"]],
    }


def freeze_scan(
    challenges: Mapping[str, Mapping[str, Any]],
    *,
    limits: Mapping[str, Any] | None = None,
    source_hash: str | None = None,
    entrant_source_hash: str | None = None,
    run_name: str = "delta-algebra-v2-scan",
) -> dict[str, Any]:
    records: dict[str, Any] = {}
    activated = 0
    for raw_task_id, task in sorted(challenges.items(), key=lambda item: str(item[0])):
        safe = _safe_task(task)
        candidates = compile_task(safe, limits=limits)
        if len(candidates) > 1:
            raise AssertionError("compile_task violated its one-candidate contract")
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
            "Challenge-only deterministic structural-repair scan. No solution, score, "
            "baseline, submission, or v1 prediction artifact is read by compilation."
        ),
    }
    body["semantic_hash"] = _digest(body)
    body["content_hash"] = _digest(body)
    return body


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-name", default="delta-algebra-v2-scan")
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
    print(_canonical({"activation_count": frozen["activation_count"], "content_hash": frozen["content_hash"], "source_task_count": frozen["source_task_count"]}))
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
