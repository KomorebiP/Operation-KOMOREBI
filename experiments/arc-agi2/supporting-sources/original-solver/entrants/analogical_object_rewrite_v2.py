"""Dynamic exemplar-to-peer analogical completion for PR-LASM Block 14.

This provenance-isolated extension learns a scene-local rewrite rather than a
fixed raster template.  A cohort of objects shares a base shape and an anchor
role up to D4.  The uniquely decorated exemplar supplies missing decorator
cells and colors to its partial peers after base+anchor alignment.  The local
template is rebuilt on every input, so base geometry may change across demos
and tests.

No task identifier, resolved coordinate, score, solution, result, baseline, or
submission is consulted.  Exact replay, leave-one-demo-out re-induction,
full-test behavior uniqueness, D4/palette covariance, and hard-cap abstention
are mandatory.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Callable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block14.analogical_object_rewrite_v2.program.v1"
SCAN_SCHEMA = "komorebi.pr_lasm.block14.analogical_object_rewrite_v2.scan_freeze.v1"
AUTHOR = "Komorebi P."
ORTHOGONAL: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))


class Undefined(ValueError):
    """A local object role or D4 correspondence is absent or tied."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 10
    max_objects: int = 64
    max_object_cells: int = 256
    max_executor_calls: int = 4_096
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
            "max_objects": 256,
            "max_object_cells": 900,
            "max_executor_calls": 100_000,
            "max_gauge_checks": 4_096,
            "max_candidates": 1,
            "mdl_slack": 2,
        }
        result: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            fallback = value.get("candidate_cap", getattr(defaults, name)) if name == "max_candidates" else getattr(defaults, name)
            raw = value.get(name, fallback)
            if isinstance(raw, bool) or not isinstance(raw, int):
                raise Undefined(f"limits.{name} must be an integer")
            minimum = 0 if name == "mdl_slack" else 1
            if raw < minimum:
                raise Undefined(f"limits.{name} is below {minimum}")
            result[name] = min(raw, ceilings[name])
        return cls(**result)


@dataclass(frozen=True, slots=True)
class Object:
    cells: frozenset[Cell]
    color_cells: Mapping[int, frozenset[Cell]]
    bbox: tuple[int, int, int, int]

    @property
    def area(self) -> int:
        return len(self.cells)


TRANSFORMS: tuple[tuple[str, Callable[[int, int], Cell]], ...] = (
    ("identity", lambda row, column: (row, column)),
    ("rotate_90", lambda row, column: (column, -row)),
    ("rotate_180", lambda row, column: (-row, -column)),
    ("rotate_270", lambda row, column: (-column, row)),
    ("reflect", lambda row, column: (row, -column)),
    ("reflect_rotate_90", lambda row, column: (-column, -row)),
    ("reflect_rotate_180", lambda row, column: (-row, column)),
    ("reflect_rotate_270", lambda row, column: (column, row)),
)


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
        raise Undefined("grid exceeds cell cap")
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
            raise Undefined("peer completion requires nonidentity same-shape pairs")
        demonstrations.append((source, target))
    tests: list[Grid] = []
    for example in test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        tests.append(_grid(example.get("input"), limits))
    return tuple(demonstrations), tuple(tests)


def _unique_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    if len(winners) != 1:
        raise Undefined("mode role is tied")
    return winners[0]


def _background(grid: Grid, role: str) -> int:
    height, width = _shape(grid)
    if role == "mode":
        return _unique_mode(cell for row in grid for cell in row)
    if role == "border_mode":
        return _unique_mode(
            grid[row][column]
            for row in range(height)
            for column in range(width)
            if row in {0, height - 1} or column in {0, width - 1}
        )
    if role == "corners":
        corners = (grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1])
        if len(set(corners)) != 1:
            raise Undefined("corner role is tied")
        return corners[0]
    raise Undefined("unknown background role")


def _bbox(cells: Iterable[Cell]) -> tuple[int, int, int, int]:
    points = tuple(cells)
    if not points:
        raise Undefined("empty object")
    return (
        min(row for row, _ in points),
        max(row for row, _ in points),
        min(column for _, column in points),
        max(column for _, column in points),
    )


def _objects(grid: Grid, background: int, limits: Limits) -> tuple[Object, ...]:
    height, width = _shape(grid)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background
    }
    answer: list[Object] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        cells = {seed}
        queue = deque([seed])
        while queue:
            row, column = queue.popleft()
            for dr, dc in ORTHOGONAL:
                point = row + dr, column + dc
                if point in remaining:
                    remaining.remove(point)
                    cells.add(point)
                    queue.append(point)
        if len(cells) > limits.max_object_cells:
            raise Undefined("object cell cap exhausted")
        frozen = frozenset(cells)
        by_color: dict[int, frozenset[Cell]] = {}
        for color in sorted({grid[row][column] for row, column in frozen}):
            by_color[color] = frozenset((row, column) for row, column in frozen if grid[row][column] == color)
        answer.append(Object(frozen, by_color, _bbox(frozen)))
        if len(answer) > limits.max_objects:
            raise Undefined("object count cap exhausted")
    if len(answer) < 3:
        raise Undefined("peer completion requires at least three objects")
    return tuple(sorted(answer, key=lambda item: item.bbox))


def _relative(cells: Iterable[Cell], origin: Cell) -> frozenset[Cell]:
    return frozenset((row - origin[0], column - origin[1]) for row, column in cells)


def _transform_with_base(
    points: Iterable[Cell],
    base: Iterable[Cell],
    transform: Callable[[int, int], Cell],
) -> tuple[frozenset[Cell], frozenset[Cell]]:
    transformed_base_raw = frozenset(transform(row, column) for row, column in base)
    if not transformed_base_raw:
        raise Undefined("base template is empty")
    shift_row = -min(row for row, _ in transformed_base_raw)
    shift_column = -min(column for _, column in transformed_base_raw)
    transformed_base = frozenset((row + shift_row, column + shift_column) for row, column in transformed_base_raw)
    transformed_points = frozenset(
        (row + shift_row, column + shift_column)
        for row, column in (transform(row, column) for row, column in points)
    )
    return transformed_points, transformed_base


def _scene_roles(grid: Grid, background_role: str, limits: Limits) -> tuple[int, tuple[Object, ...], int, int, int]:
    background = _background(grid, background_role)
    objects = _objects(grid, background, limits)
    palettes = [set(obj.color_cells) for obj in objects]
    common = set.intersection(*palettes)
    base_candidates: list[int] = []
    for color in common:
        if all(
            len(obj.color_cells[color]) > len(cells)
            for obj in objects
            for other, cells in obj.color_cells.items()
            if other != color
        ):
            base_candidates.append(color)
    if len(base_candidates) != 1:
        raise Undefined("common modal base role is tied")
    base = base_candidates[0]
    anchor_candidates = sorted(color for color in common if color != base)
    if len(anchor_candidates) != 1:
        raise Undefined("shared anchor role is tied")
    anchor = anchor_candidates[0]
    decorator_counts = [
        sum(len(cells) for color, cells in obj.color_cells.items() if color not in {base, anchor})
        for obj in objects
    ]
    maximum = max(decorator_counts)
    if maximum <= 0 or decorator_counts.count(maximum) != 1:
        raise Undefined("decorated exemplar role is tied")
    exemplar_index = decorator_counts.index(maximum)
    if any(count != 0 for index, count in enumerate(decorator_counts) if index != exemplar_index):
        raise Undefined("partial peers already contain unaligned decorators")
    return background, objects, base, anchor, exemplar_index


def _peer_decorations(
    exemplar: Object,
    peer: Object,
    base_color: int,
    anchor_color: int,
) -> dict[Cell, int]:
    exemplar_origin = (
        min(row for row, _ in exemplar.color_cells[base_color]),
        min(column for _, column in exemplar.color_cells[base_color]),
    )
    peer_origin = (
        min(row for row, _ in peer.color_cells[base_color]),
        min(column for _, column in peer.color_cells[base_color]),
    )
    exemplar_base = _relative(exemplar.color_cells[base_color], exemplar_origin)
    exemplar_anchor = _relative(exemplar.color_cells[anchor_color], exemplar_origin)
    peer_base = _relative(peer.color_cells[base_color], peer_origin)
    peer_anchor = _relative(peer.color_cells[anchor_color], peer_origin)
    exemplar_decorators = {
        color: _relative(cells, exemplar_origin)
        for color, cells in exemplar.color_cells.items()
        if color not in {base_color, anchor_color}
    }
    possibilities: dict[str, dict[Cell, int]] = {}
    for _, transform in TRANSFORMS:
        transformed_anchor, transformed_base = _transform_with_base(exemplar_anchor, exemplar_base, transform)
        if transformed_base != peer_base or transformed_anchor != peer_anchor:
            continue
        decoration: dict[Cell, int] = {}
        for color, cells in exemplar_decorators.items():
            transformed_cells, _ = _transform_with_base(cells, exemplar_base, transform)
            for row, column in transformed_cells:
                point = peer_origin[0] + row, peer_origin[1] + column
                previous = decoration.get(point)
                if previous is not None and previous != color:
                    raise Undefined("decorator transformations conflict")
                decoration[point] = color
        possibilities[_canonical([[row, column, color] for (row, column), color in sorted(decoration.items())])] = decoration
    if len(possibilities) != 1:
        raise Undefined("base+anchor D4 alignment is absent or behaviorally tied")
    return next(iter(possibilities.values()))


def _execute_internal(program: Mapping[str, Any], grid: Grid, limits: Limits) -> tuple[Grid, dict[str, Any]]:
    if (
        not isinstance(program, Mapping)
        or program.get("schema") != SCHEMA
        or program.get("macro") != "peer_exemplar_completion"
    ):
        raise Undefined("invalid peer-completion program")
    background_role = program.get("background")
    if background_role not in {"mode", "border_mode", "corners"}:
        raise Undefined("invalid root identity role")
    background, objects, base, anchor, exemplar_index = _scene_roles(grid, str(background_role), limits)
    exemplar = objects[exemplar_index]
    output = [list(row) for row in grid]
    claims: dict[Cell, int] = {}
    peer_records: list[dict[str, Any]] = []
    for index, peer in enumerate(objects):
        if index == exemplar_index:
            continue
        decoration = _peer_decorations(exemplar, peer, base, anchor)
        for point, color in decoration.items():
            row, column = point
            if not (0 <= row < len(grid) and 0 <= column < len(grid[0])):
                raise Undefined("transferred decorator leaves the canvas")
            if grid[row][column] != background:
                raise Undefined("transferred decorator collides with source support")
            previous = claims.get(point)
            if previous is not None and previous != color:
                raise Undefined("peer decorator claims conflict")
            claims[point] = color
        peer_records.append({"peer_index": index, "transferred_cells": len(decoration)})
    if not claims:
        raise Undefined("peer completion is an identity")
    for (row, column), color in claims.items():
        output[row][column] = color
    return tuple(tuple(row) for row in output), {
        "macro": "peer_exemplar_completion",
        "background": background,
        "object_count": len(objects),
        "base_color": base,
        "anchor_color": anchor,
        "exemplar_index": exemplar_index,
        "decorator_palette": sorted(color for color in exemplar.color_cells if color not in {base, anchor}),
        "peer_receipts": peer_records,
        "transferred_cell_count": len(claims),
    }


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized dynamic exemplar program."""

    limits = Limits()
    grid = _grid(value, limits)
    return _plain(_execute_internal(program, grid, limits)[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Tournament replay with cohort, alignment, and completion stages."""

    limits = Limits()
    grid = _grid(value, limits)
    output, record = _execute_internal(program, grid, limits)
    parsed = {
        "kind": "analogical_object_cohort",
        "shape": list(_shape(grid)),
        "background_role": program["background"],
    }
    return {
        "output": _plain(output),
        "stages": [
            {"name": "parse-peer-cohort", "input": _plain(grid), "output": parsed},
            {"name": "align-exemplar-by-base-anchor", "input": parsed, "output": record},
            {"name": "transfer-missing-decorators", "input": record, "output": _plain(output)},
        ],
    }


def _program(background: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "macro": "peer_exemplar_completion",
        "background": background,
        "partition": "multicolor_components_4",
        "base_role": "unique_common_per_object_modal_color",
        "anchor_role": "unique_nonbase_color_present_in_every_object",
        "exemplar_role": "unique_max_nonbase_nonanchor_decorator_support",
        "correspondence": "D4_align_base_plus_anchor",
        "rewrite": "copy_exemplar_decorators_to_partial_peers",
        "description_length": 13 + (0 if background == "mode" else 1),
    }


def _exact_programs(demonstrations: Sequence[Pair], tests: Sequence[Grid], limits: Limits) -> tuple[dict[str, Any], ...]:
    exact: list[dict[str, Any]] = []
    calls = 0
    for background in ("mode", "border_mode", "corners"):
        program = _program(background)
        try:
            predictions = []
            for source, _ in demonstrations:
                predictions.append(_execute_internal(program, source, limits)[0])
                calls += 1
            for source in tests:
                _execute_internal(program, source, limits)
                calls += 1
            if calls > limits.max_executor_calls:
                raise Undefined("executor call cap exhausted")
        except Undefined:
            continue
        if tuple(predictions) == tuple(target for _, target in demonstrations):
            exact.append(program)
    if not exact:
        return ()
    best = min(int(program["description_length"]) for program in exact)
    return tuple(
        sorted(
            (program for program in exact if int(program["description_length"]) <= best + limits.mdl_slack),
            key=lambda item: (int(item["description_length"]), _canonical(item)),
        )
    )


def _behavior(program: Mapping[str, Any], grids: Sequence[Grid], limits: Limits) -> tuple[Grid, ...]:
    return tuple(_execute_internal(program, grid, limits)[0] for grid in grids)


def _loo(demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    checks = 0
    class_count = 0
    for held_out, (source, target) in enumerate(demonstrations):
        training = tuple(pair for index, pair in enumerate(demonstrations) if index != held_out)
        programs = _exact_programs(training, (source,), limits)
        behaviors: dict[str, tuple[Grid, ...]] = {}
        for program in programs:
            try:
                outputs = _behavior(program, (source,), limits)
            except Undefined:
                continue
            behaviors[_digest([_plain(grid) for grid in outputs])] = outputs
            checks += 1
        class_count += len(behaviors)
        if len(behaviors) != 1 or next(iter(behaviors.values())) != (target,):
            return False, checks, class_count
    return True, checks, class_count


def _rotate90(grid: Grid) -> Grid:
    return tuple(tuple(row) for row in zip(*reversed(grid)))


def _swap_grid(grid: Grid, left: int, right: int) -> Grid:
    return tuple(tuple(right if value == left else left if value == right else value for value in row) for row in grid)


def _gauge(program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    d4_checks = 0
    palette_checks = 0
    for source, target in demonstrations:
        pairs: dict[str, tuple[Grid, Grid]] = {}
        transformed_source, transformed_target = source, target
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
                prediction = _execute_internal(program, _swap_grid(source, left, right), limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if prediction != _swap_grid(target, left, right):
                return False, d4_checks, palette_checks
    return True, d4_checks, palette_checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one dynamic exemplar-to-peer rewrite or abstain."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
        programs = _exact_programs(demonstrations, tests, bounds)
    except (Undefined, TypeError, ValueError):
        return []
    if not programs:
        return []
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = {}
    for program in programs:
        try:
            outputs = _behavior(program, tests, bounds)
        except Undefined:
            continue
        behaviors.setdefault(_digest([_plain(grid) for grid in outputs]), []).append((program, outputs))
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
    representative, outputs = equivalent[0]
    loo_ok, loo_checks, loo_classes = _loo(demonstrations, bounds)
    if not loo_ok:
        return []
    gauge_ok, d4_checks, palette_checks = _gauge(representative, demonstrations, bounds)
    if not gauge_ok:
        return []
    try:
        train_outputs = _behavior(representative, tuple(source for source, _ in demonstrations), bounds)
    except Undefined:
        return []
    if train_outputs != tuple(target for _, target in demonstrations):
        return []
    candidate = {
        "family": "analogical_object_rewrite_v2",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "dynamic_scene_local_template": True,
            "root_identity_transported": True,
            "all_demos_exact": True,
            "exact_replay": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_program_checks": loo_checks,
            "leave_one_out_behavior_classes": loo_classes,
            "enumeration_complete": True,
            "programs_enumerated": 3,
            "hard_caps_exhausted": False,
            "near_mdl_programs": len(programs),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalent),
            "d4_covariance_checks": d4_checks,
            "palette_covariance_checks": palette_checks,
            "serialized_resolved_coordinates": False,
            "serialized_literal_colors": False,
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
    run_name: str = "analogical-object-rewrite-v2-scan",
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
            "Challenge-only dynamic exemplar scan. No solution, score, result, baseline, "
            "submission, task lookup, or resolved coordinate is used."
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
    parser.add_argument("--run-name", default="analogical-object-rewrite-v2-scan")
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
