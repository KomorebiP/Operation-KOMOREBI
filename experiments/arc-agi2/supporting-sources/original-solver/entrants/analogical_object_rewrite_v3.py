"""Reference-mediated normalized object rewrites for PR-LASM Block 14.

The entrant derives each rewrite from object roles visible in the current
scene.  One branch expands isolated tokens through a multicolor reference
object.  A second branch uses shapes embedded in frame-like reference objects
to recolor D4-equivalent free peers.  Both branches transport colors by role,
never by serialized palette literal, and never store absolute coordinates.

Compilation consumes demonstration pairs and held-out inputs only.  It demands
exact demonstration replay, genuine leave-one-demo-out re-induction, unique
held-out behavior, D4 and palette covariance, and bounded enumeration.

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
SCHEMA = "komorebi.pr_lasm.block14.analogical_object_rewrite_v3.program.v1"
SCAN_SCHEMA = "komorebi.pr_lasm.block14.analogical_object_rewrite_v3.scan_freeze.v1"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """A required role is absent, ambiguous, or outside a hard cap."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 10
    max_components: int = 128
    max_component_cells: int = 900
    max_executor_calls: int = 8_192
    max_gauge_checks: int = 2_048
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
            "max_component_cells": 3_600,
            "max_executor_calls": 100_000,
            "max_gauge_checks": 8_192,
            "max_candidates": 1,
            "mdl_slack": 3,
        }
        parsed: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            fallback = value.get("candidate_cap", getattr(defaults, name)) if name == "max_candidates" else getattr(defaults, name)
            raw = value.get(name, fallback)
            if isinstance(raw, bool) or not isinstance(raw, int):
                raise Undefined(f"limits.{name} must be an integer")
            minimum = 0 if name == "mdl_slack" else 1
            if raw < minimum:
                raise Undefined(f"limits.{name} is below {minimum}")
            parsed[name] = min(raw, ceilings[name])
        return cls(**parsed)


@dataclass(frozen=True, slots=True)
class Component:
    color: int | None
    cells: frozenset[Cell]
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
            raise Undefined("reference rewrite requires a nonidentity same-shape pair")
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
    winners = sorted(value for value, count in counts.items() if count == maximum)
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
        corners = grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1]
        if len(set(corners)) != 1:
            raise Undefined("corner role is tied")
        return corners[0]
    raise Undefined("unknown background role")


def _bbox(cells: Iterable[Cell]) -> tuple[int, int, int, int]:
    points = tuple(cells)
    if not points:
        raise Undefined("empty component")
    return (
        min(row for row, _ in points),
        max(row for row, _ in points),
        min(column for _, column in points),
        max(column for _, column in points),
    )


def _components(
    grid: Grid,
    background: int,
    connectivity: int,
    limits: Limits,
    *,
    monochrome: bool,
) -> tuple[Component, ...]:
    if connectivity not in {4, 8}:
        raise Undefined("connectivity is invalid")
    height, width = _shape(grid)
    pending = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background
    }
    steps: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
    if connectivity == 8:
        steps += ((-1, -1), (-1, 1), (1, -1), (1, 1))
    answer: list[Component] = []
    while pending:
        seed = min(pending)
        pending.remove(seed)
        seed_color = grid[seed[0]][seed[1]]
        cells = {seed}
        queue = deque([seed])
        while queue:
            row, column = queue.popleft()
            for dr, dc in steps:
                point = row + dr, column + dc
                if point not in pending:
                    continue
                if monochrome and grid[point[0]][point[1]] != seed_color:
                    continue
                pending.remove(point)
                cells.add(point)
                queue.append(point)
        if len(cells) > limits.max_component_cells:
            raise Undefined("component cell cap exhausted")
        frozen = frozenset(cells)
        colors = {grid[row][column] for row, column in frozen}
        color = next(iter(colors)) if len(colors) == 1 else None
        answer.append(Component(color, frozen, _bbox(frozen)))
        if len(answer) > limits.max_components:
            raise Undefined("component count cap exhausted")
    return tuple(sorted(answer, key=lambda item: (item.bbox, item.color if item.color is not None else 10)))


def _normalize(points: Iterable[Cell], transform: Callable[[int, int], Cell]) -> frozenset[Cell]:
    transformed = frozenset(transform(row, column) for row, column in points)
    if not transformed:
        raise Undefined("shape is empty")
    top = min(row for row, _ in transformed)
    left = min(column for _, column in transformed)
    return frozenset((row - top, column - left) for row, column in transformed)


def _shape_key(points: Iterable[Cell]) -> str:
    variants = []
    frozen = frozenset(points)
    for _, transform in TRANSFORMS:
        normalized = _normalize(frozen, transform)
        variants.append(_canonical([[row, column] for row, column in sorted(normalized)]))
    return min(variants)


def _strictly_inside(inner: Component, outer: Component) -> bool:
    top, bottom, left, right = outer.bbox
    return all(top < row < bottom and left < column < right for row, column in inner.cells)


def _is_closed_rectangular_frame(component: Component) -> bool:
    top, bottom, left, right = component.bbox
    if bottom - top < 2 or right - left < 2:
        return False
    perimeter = {
        (row, column)
        for row in range(top, bottom + 1)
        for column in range(left, right + 1)
        if row in {top, bottom} or column in {left, right}
    }
    return perimeter.issubset(component.cells)


def _execute_token_expansion(
    grid: Grid,
    background_role: str,
    connectivity: int,
    limits: Limits,
) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid, background_role)
    components = _components(grid, background, connectivity, limits, monochrome=False)
    references: list[Component] = []
    tokens: list[Component] = []
    for component in components:
        colors = {grid[row][column] for row, column in component.cells}
        if component.area == 1:
            tokens.append(component)
        elif len(colors) >= 2:
            references.append(component)
        else:
            raise Undefined("token expansion has an unrelated monochrome object")
    if not references or len(tokens) < 2:
        raise Undefined("token expansion lacks references or isolated peers")

    output = [list(row) for row in grid]
    used_references: set[int] = set()
    additions: set[Cell] = set()
    receipts: list[dict[str, Any]] = []
    for token in tokens:
        point = next(iter(token.cells))
        token_color = grid[point[0]][point[1]]
        placements: dict[str, tuple[int, dict[Cell, int]]] = {}
        for reference_index, reference in enumerate(references):
            matching = [cell for cell in reference.cells if grid[cell[0]][cell[1]] == token_color]
            if len(matching) != 1:
                continue
            anchor = matching[0]
            translated: dict[Cell, int] = {}
            for row, column in reference.cells:
                destination = point[0] + row - anchor[0], point[1] + column - anchor[1]
                if destination in translated and translated[destination] != grid[row][column]:
                    raise Undefined("translated reference colors conflict")
                translated[destination] = grid[row][column]
            key = _canonical([[row, column, color] for (row, column), color in sorted(translated.items())])
            placements[key] = reference_index, translated
        if len(placements) != 1:
            raise Undefined("token-to-reference lookup is absent or behaviorally tied")
        reference_index, translated = next(iter(placements.values()))
        used_references.add(reference_index)
        for destination, color in translated.items():
            row, column = destination
            if not (0 <= row < len(grid) and 0 <= column < len(grid[0])):
                # ARC scenes clip translated patterns at the canvas boundary;
                # the anchor itself remains in bounds and preserves identity.
                continue
            source_color = grid[row][column]
            if destination == point:
                if source_color != color:
                    raise Undefined("reference anchor does not preserve token color")
            elif source_color != background:
                raise Undefined("translated reference collides with source support")
            previous = output[row][column]
            if previous not in {background, color}:
                raise Undefined("translated peer claims conflict")
            output[row][column] = color
            if source_color == background:
                additions.add(destination)
        receipts.append({"reference_role": reference_index, "transferred_cells": len(translated)})
    if used_references != set(range(len(references))) or len(additions) < 2:
        raise Undefined("not every reference is evidenced by a peer expansion")
    return tuple(tuple(row) for row in output), {
        "macro": "reference_token_expansion",
        "background": background,
        "reference_count": len(references),
        "token_count": len(tokens),
        "support_additions": len(additions),
        "peer_receipts": receipts,
    }


def _execute_framed_shape_transfer(
    grid: Grid,
    background_role: str,
    connectivity: int,
    limits: Limits,
) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid, background_role)
    components = _components(grid, background, connectivity, limits, monochrome=True)
    colors = sorted({component.color for component in components if component.color is not None})
    container_options: list[tuple[int, tuple[Component, ...], tuple[Component, ...]]] = []
    for color in colors:
        containers = tuple(
            component
            for component in components
            if component.color == color
            and _is_closed_rectangular_frame(component)
        )
        if not containers:
            continue
        contained = tuple(
            component
            for component in components
            if component.color != color and any(_strictly_inside(component, container) for container in containers)
        )
        active_containers = {
            index
            for index, container in enumerate(containers)
            if any(_strictly_inside(component, container) for component in contained)
        }
        if contained and len(active_containers) == len(containers):
            container_options.append((int(color), containers, contained))
    if not container_options:
        raise Undefined("no frame-mediated reference role")
    maximum = max(len(option[2]) for option in container_options)
    winners = [option for option in container_options if len(option[2]) == maximum]
    if len(winners) != 1:
        raise Undefined("frame color role is tied")
    container_color, containers, references = winners[0]

    excluded = {id(component) for component in references} | {
        id(component) for component in components if component.color == container_color
    }
    free_candidates = tuple(
        component
        for component in components
        if id(component) not in excluded
        and not any(_strictly_inside(component, container) for container in containers)
    )
    free_counts = Counter(component.color for component in free_candidates)
    if not free_counts:
        raise Undefined("free peer color role is absent or tied")
    maximum_free_count = max(free_counts.values())
    peer_color_winners = sorted(
        color for color, count in free_counts.items() if count == maximum_free_count
    )
    if len(peer_color_winners) != 1 or maximum_free_count < 2:
        raise Undefined("free peer color role is absent or tied")
    peer_color = peer_color_winners[0]
    if peer_color is None:
        raise Undefined("free peer color is invalid")
    free = tuple(component for component in free_candidates if component.color == peer_color)

    reference_roles: dict[str, set[int]] = {}
    for reference in references:
        if reference.color is None or reference.color in {container_color, peer_color}:
            raise Undefined("reference color collides with frame or peer role")
        reference_roles.setdefault(_shape_key(reference.cells), set()).add(reference.color)
    if not reference_roles or any(len(palette) != 1 for palette in reference_roles.values()):
        raise Undefined("shape-to-reference-color role is tied")

    output = [list(row) for row in grid]
    recolored = 0
    preserved = 0
    receipts: list[dict[str, Any]] = []
    for peer in free:
        key = _shape_key(peer.cells)
        if key not in reference_roles:
            preserved += 1
            continue
        target_color = next(iter(reference_roles[key]))
        for row, column in peer.cells:
            output[row][column] = target_color
        recolored += 1
        receipts.append({"peer_area": peer.area, "reference_shape_hash": hashlib.sha256(key.encode("utf-8")).hexdigest()})
    if recolored < 1 or preserved < 1:
        raise Undefined("reference transfer requires both matched and unmatched peers")
    return tuple(tuple(row) for row in output), {
        "macro": "framed_shape_role_transfer",
        "background": background,
        "container_count": len(containers),
        "reference_count": len(references),
        "peer_count": len(free),
        "recolored_peer_count": recolored,
        "preserved_peer_count": preserved,
        "peer_receipts": receipts,
    }


def _execute_free_shape_transfer(
    grid: Grid,
    background_role: str,
    connectivity: int,
    limits: Limits,
    *,
    action: str,
) -> tuple[Grid, dict[str, Any]]:
    if action not in {"reference_recolor", "delete"}:
        raise Undefined("free-shape action is invalid")
    background = _background(grid, background_role)
    components = _components(grid, background, connectivity, limits, monochrome=True)
    by_color: dict[int, list[Component]] = {}
    for component in components:
        if component.color is None:
            raise Undefined("monochrome atlas emitted a mixed component")
        by_color.setdefault(component.color, []).append(component)

    behaviors: dict[str, tuple[Grid, dict[str, Any]]] = {}
    for peer_color, peers in sorted(by_color.items()):
        if len(peers) < 2:
            continue
        reference_roles: dict[str, set[int]] = {}
        for reference_color, reference_components in by_color.items():
            if reference_color == peer_color:
                continue
            for reference in reference_components:
                reference_roles.setdefault(_shape_key(reference.cells), set()).add(reference_color)
        if not reference_roles or any(len(palette) != 1 for palette in reference_roles.values()):
            continue
        output = [list(row) for row in grid]
        matched = 0
        preserved = 0
        receipts: list[dict[str, Any]] = []
        for peer in peers:
            key = _shape_key(peer.cells)
            if key not in reference_roles:
                preserved += 1
                continue
            reference_color = next(iter(reference_roles[key]))
            target_color = reference_color if action == "reference_recolor" else background
            for row, column in peer.cells:
                output[row][column] = target_color
            matched += 1
            receipts.append(
                {
                    "peer_area": peer.area,
                    "reference_shape_hash": hashlib.sha256(key.encode("utf-8")).hexdigest(),
                }
            )
        if matched < 1 or preserved < 1:
            continue
        frozen = tuple(tuple(row) for row in output)
        if frozen == grid:
            continue
        record = {
            "macro": f"free_shape_{action}",
            "background": background,
            "peer_count": len(peers),
            "matched_peer_count": matched,
            "preserved_peer_count": preserved,
            "peer_receipts": receipts,
        }
        behaviors[_digest(_plain(frozen))] = frozen, record
    if len(behaviors) != 1:
        raise Undefined("free peer/reference role is absent or behaviorally tied")
    return next(iter(behaviors.values()))


def _execute_internal(program: Mapping[str, Any], grid: Grid, limits: Limits) -> tuple[Grid, dict[str, Any]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid analogical-object v3 program")
    background = program.get("background")
    connectivity = program.get("connectivity")
    if background not in {"mode", "border_mode", "corners"} or connectivity not in {4, 8}:
        raise Undefined("invalid program roles")
    macro = program.get("macro")
    if macro == "reference_token_expansion":
        return _execute_token_expansion(grid, str(background), int(connectivity), limits)
    if macro == "framed_shape_role_transfer":
        return _execute_framed_shape_transfer(grid, str(background), int(connectivity), limits)
    if macro == "free_shape_reference_recolor":
        return _execute_free_shape_transfer(
            grid,
            str(background),
            int(connectivity),
            limits,
            action="reference_recolor",
        )
    if macro == "free_shape_delete":
        return _execute_free_shape_transfer(
            grid,
            str(background),
            int(connectivity),
            limits,
            action="delete",
        )
    raise Undefined("unknown analogical-object v3 macro")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized role-only rewrite."""

    limits = Limits()
    grid = _grid(value, limits)
    return _plain(_execute_internal(program, grid, limits)[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Replay one program with an explicit parse/match/rewrite chain."""

    limits = Limits()
    grid = _grid(value, limits)
    output, receipt = _execute_internal(program, grid, limits)
    parsed = {
        "kind": "reference_mediated_object_scene",
        "shape": list(_shape(grid)),
        "background_role": program["background"],
        "connectivity": program["connectivity"],
    }
    matched = {
        "macro": program["macro"],
        "dynamic_scene_roles": True,
        "receipt": receipt,
    }
    return {
        "output": _plain(output),
        "stages": [
            {"name": "parse-normalized-object-atlas", "input": _plain(grid), "output": parsed},
            {"name": "resolve-reference-and-peer-roles", "input": parsed, "output": matched},
            {"name": "transport-reference-support-edit", "input": matched, "output": _plain(output)},
        ],
    }


def _program(macro: str, background: str, connectivity: int) -> dict[str, Any]:
    base_lengths = {
        "reference_token_expansion": 14,
        "framed_shape_role_transfer": 14,
        "free_shape_reference_recolor": 16,
        "free_shape_delete": 15,
    }
    base_length = base_lengths[macro]
    if macro == "reference_token_expansion":
        reference_role = "unique_multicolor_component_containing_token_color"
        peer_role = "isolated_color_token"
        correspondence = "translate_reference_so_unique_same-color_cell_meets_token"
        support_edit = "add_reference_support"
    elif macro == "framed_shape_role_transfer":
        reference_role = "foreign_shape_strictly_inside_unique_closed_frame_color"
        peer_role = "free_monochrome_components_of_unique_modal_peer_color"
        correspondence = "D4_normalized_support_equality"
        support_edit = "recolor_matched_peer_support"
    else:
        reference_role = "other_color_components_with_unique_shape_to_color_role"
        peer_role = "unique_behavioral_color_cohort_with_matched_and_unmatched_shapes"
        correspondence = "D4_normalized_support_equality"
        support_edit = "delete_matched_peer_support" if macro == "free_shape_delete" else "recolor_matched_peer_to_reference_color"
    return {
        "schema": SCHEMA,
        "macro": macro,
        "background": background,
        "connectivity": connectivity,
        "atlas": "scene_local_normalized_components",
        "reference_role": reference_role,
        "peer_role": peer_role,
        "correspondence": correspondence,
        "support_edit": support_edit,
        "description_length": base_length + (0 if background == "mode" else 1) + (0 if connectivity == 4 else 1),
    }


def _enumerate_programs() -> tuple[dict[str, Any], ...]:
    return tuple(
        _program(macro, background, connectivity)
        for macro in (
            "reference_token_expansion",
            "framed_shape_role_transfer",
            "free_shape_reference_recolor",
            "free_shape_delete",
        )
        for background in ("mode", "border_mode", "corners")
        for connectivity in (4, 8)
    )


def _exact_programs(demonstrations: Sequence[Pair], tests: Sequence[Grid], limits: Limits) -> tuple[dict[str, Any], ...]:
    exact: list[dict[str, Any]] = []
    calls = 0
    for program in _enumerate_programs():
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
            key=lambda program: (int(program["description_length"]), _canonical(program)),
        )
    )


def _behavior(program: Mapping[str, Any], grids: Sequence[Grid], limits: Limits) -> tuple[Grid, ...]:
    return tuple(_execute_internal(program, grid, limits)[0] for grid in grids)


def _loo(demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    checks = 0
    classes = 0
    for held_index, (source, target) in enumerate(demonstrations):
        training = tuple(pair for index, pair in enumerate(demonstrations) if index != held_index)
        programs = _exact_programs(training, (source,), limits)
        behaviors: dict[str, tuple[Grid, ...]] = {}
        for program in programs:
            try:
                outputs = _behavior(program, (source,), limits)
            except Undefined:
                continue
            behaviors[_digest([_plain(output) for output in outputs])] = outputs
            checks += 1
        classes += len(behaviors)
        if len(behaviors) != 1 or next(iter(behaviors.values())) != (target,):
            return False, checks, classes
    return True, checks, classes


def _rotate90(grid: Grid) -> Grid:
    return tuple(tuple(row) for row in zip(*reversed(grid)))


def _swap_grid(grid: Grid, left: int, right: int) -> Grid:
    return tuple(tuple(right if value == left else left if value == right else value for value in row) for row in grid)


def _gauge(program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    d4_checks = 0
    palette_checks = 0
    for source, target in demonstrations:
        pairs: dict[str, tuple[Grid, Grid]] = {}
        rotated_source, rotated_target = source, target
        for _ in range(4):
            pairs.setdefault(_canonical(_plain(rotated_source)), (rotated_source, rotated_target))
            reflected_source = tuple(tuple(reversed(row)) for row in rotated_source)
            reflected_target = tuple(tuple(reversed(row)) for row in rotated_target)
            pairs.setdefault(_canonical(_plain(reflected_source)), (reflected_source, reflected_target))
            rotated_source, rotated_target = _rotate90(rotated_source), _rotate90(rotated_target)
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
    """Compile one unambiguous reference-mediated object rewrite or abstain."""

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
        "family": "analogical_object_rewrite_v3",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "dynamic_scene_local_references": True,
            "normalized_object_atlas": True,
            "support_edits_enabled": True,
            "root_identity_transported": True,
            "all_demos_exact": True,
            "exact_replay": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_program_checks": loo_checks,
            "leave_one_out_behavior_classes": loo_classes,
            "enumeration_complete": True,
            "programs_enumerated": len(_enumerate_programs()),
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
    run_name: str = "analogical-object-rewrite-v3-scan",
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
            "Challenge-only reference-mediated object scan. No solution, score, result, "
            "baseline, submission, task lookup, or resolved coordinate is used."
        ),
    }
    body["semantic_hash"] = _digest(body)
    body["content_hash"] = _digest(body)
    return body


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-name", default="analogical-object-rewrite-v3-scan")
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
    print(
        _canonical(
            {
                "activation_count": frozen["activation_count"],
                "content_hash": frozen["content_hash"],
                "source_task_count": frozen["source_task_count"],
            }
        )
    )
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
