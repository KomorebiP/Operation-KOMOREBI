"""Score-seeded semantic repairs for the Block 15 topology/shape lane.

This entrant is a retrospective repair branch: aggregate score feedback exposed
two overly broad v1 predicates, after which their semantics were replaced by
general raster laws.  Runtime induction remains identity-free and receives
only labelled demonstrations plus held-input rasters.  The module contains no
task identifiers, corpus fingerprints, stored outputs, coordinates, or score
lookups.

The finite grammar contains two repairs.  Dihedral stencil matching gives
orientation-preserving copies priority and admits reflected copies only when
they do not collide with that stronger evidence.  Diagonal-wave filtering
selects whole 8-connected components by a demonstrated minimum straight
diagonal run, rather than by a coincidental bounding-box aspect ratio.

Every exposed behavior exactly replays all demonstrations, survives isolated
leave-one-demonstration-out re-proposal, D4 and palette counterfactuals, and is
unique on the held inputs.  Ambiguity and exhausted bounds abstain.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Callable, Iterable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block15.topology_shape_compiler.program.v2"
AUTHOR = "Komorebi P."
INDUCTION_REGIME = "retrospective_score_seeded_schema_repair"


class Undefined(ValueError):
    """The finite grammar has no unique, bounded structural interpretation."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 40
    max_examples: int = 20
    max_cells: int = 120_000
    max_programs: int = 256
    max_candidates: int = 1
    max_counterfactuals: int = 128
    max_placements: int = 20_000
    max_exemplar_cells: int = 32
    max_stencil_hits: int = 256
    max_pack_states: int = 60_000

    @classmethod
    def parse(cls, raw: Any) -> "Limits":
        if raw is None:
            return cls()
        if not isinstance(raw, Mapping):
            raise Undefined("limits must be a mapping")
        aliases = {
            "candidate_cap": "max_candidates",
            "max_grid_cells": "max_cells",
            "max_replay_calls": None,
            "max_replay_stages": None,
            "max_trace_bytes": None,
            "time_limit": None,
            "time_limit_seconds": None,
            "ambiguity_slack": None,
            "max_partition_states": "max_pack_states",
        }
        fields = set(cls.__dataclass_fields__)
        values: dict[str, int] = {}
        for raw_name, raw_value in raw.items():
            name = aliases.get(str(raw_name), str(raw_name))
            if name is None or name not in fields:
                continue
            if isinstance(raw_value, bool) or not isinstance(raw_value, int) or raw_value < 1:
                raise Undefined("finite limits must be positive integers")
            values[name] = raw_value
        return cls(**values)


@dataclass(frozen=True, slots=True)
class Proposal:
    family: str
    program: Mapping[str, Any]
    complexity: int


_N8 = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if dr or dc
)


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


def _grid(value: Any, max_side: int = 40) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise Undefined("grid must be a row sequence")
    if not value or len(value) > max_side:
        raise Undefined("invalid grid height")
    width: int | None = None
    result: list[tuple[int, ...]] = []
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(
            raw_row, (str, bytes, bytearray)
        ):
            raise Undefined("grid row must be a sequence")
        if width is None:
            width = len(raw_row)
        if width is None or width < 1 or width > max_side or len(raw_row) != width:
            raise Undefined("grid must be nonempty and rectangular")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        result.append(tuple(row))
    return tuple(result)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train, test = task.get("train"), task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes, bytearray))
        or len(train) < 2
        or not isinstance(test, Sequence)
        or isinstance(test, (str, bytes, bytearray))
        or not test
        or len(train) + len(test) > limits.max_examples
    ):
        raise Undefined("invalid task arity")
    demonstrations: list[Pair] = []
    tests: list[Grid] = []
    cells = 0
    for record in train:
        if not isinstance(record, Mapping):
            raise Undefined("invalid demonstration")
        source = _grid(record.get("input"), limits.max_side)
        target = _grid(record.get("output"), limits.max_side)
        cells += len(source) * len(source[0]) + len(target) * len(target[0])
        demonstrations.append((source, target))
    for record in test:
        if not isinstance(record, Mapping):
            raise Undefined("invalid test record")
        # Deliberately read only the input key of a held record.
        source = _grid(record.get("input"), limits.max_side)
        cells += len(source) * len(source[0])
        tests.append(source)
    if cells > limits.max_cells:
        raise Undefined("cell budget exhausted")
    return tuple(demonstrations), tuple(tests)


def _components(grid: Grid, color: int) -> tuple[frozenset[Cell], ...]:
    unseen = {
        (row, column)
        for row in range(len(grid))
        for column in range(len(grid[0]))
        if grid[row][column] == color
    }
    result: list[frozenset[Cell]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        component = {root}
        while queue:
            row, column = queue.popleft()
            for dr, dc in _N8:
                other = row + dr, column + dc
                if other in unseen:
                    unseen.remove(other)
                    component.add(other)
                    queue.append(other)
        result.append(frozenset(component))
    return tuple(sorted(result, key=lambda cells: (min(cells), len(cells))))


def _bbox(cells: Iterable[Cell]) -> tuple[int, int, int, int]:
    materialized = tuple(cells)
    if not materialized:
        raise Undefined("empty support")
    return (
        min(row for row, _ in materialized),
        max(row for row, _ in materialized),
        min(column for _, column in materialized),
        max(column for _, column in materialized),
    )


def _normalize(cells: Iterable[Cell]) -> frozenset[Cell]:
    materialized = frozenset(cells)
    top, _, left, _ = _bbox(materialized)
    return frozenset((row - top, column - left) for row, column in materialized)


def _rotate(grid: Grid) -> Grid:
    height, width = _shape(grid)
    return tuple(
        tuple(grid[height - 1 - row][column] for row in range(height))
        for column in range(width)
    )


def _d4(grid: Grid, operation: str) -> Grid:
    if operation == "identity":
        return grid
    if operation == "rot90":
        return _rotate(grid)
    if operation == "rot180":
        return _rotate(_rotate(grid))
    if operation == "rot270":
        return _rotate(_rotate(_rotate(grid)))
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in grid)
    raise Undefined("unknown D4 operation")


def _shape_orbit(cells: Iterable[Cell], *, reflections: bool) -> frozenset[frozenset[Cell]]:
    source = _normalize(cells)
    operations: tuple[Callable[[int, int], Cell], ...] = (
        lambda row, column: (row, column),
        lambda row, column: (column, -row),
        lambda row, column: (-row, -column),
        lambda row, column: (-column, row),
    )
    if reflections:
        operations += (
            lambda row, column: (row, -column),
            lambda row, column: (-row, column),
            lambda row, column: (column, row),
            lambda row, column: (-column, -row),
        )
    return frozenset(
        _normalize(operation(row, column) for row, column in source)
        for operation in operations
    )


def _program(operator: str, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "root_scope": "immutable_input",
        **parameters,
    }


def _stencil_matches(
    grid: Grid,
    source: int,
    stencils: Iterable[frozenset[Cell]],
    placement_cap: int,
) -> frozenset[frozenset[Cell]]:
    height, width = _shape(grid)
    matches: set[frozenset[Cell]] = set()
    placements = 0
    for stencil in sorted(stencils, key=lambda cells: tuple(sorted(cells))):
        stencil_height = max(row for row, _ in stencil) + 1
        stencil_width = max(column for _, column in stencil) + 1
        for top in range(height - stencil_height + 1):
            for left in range(width - stencil_width + 1):
                placements += 1
                if placements > placement_cap:
                    raise Undefined("stencil placement budget exhausted")
                cells = frozenset(
                    (top + row, left + column) for row, column in stencil
                )
                if all(grid[row][column] == source for row, column in cells):
                    matches.add(cells)
    return frozenset(matches)


def _orientation_prioritized_dihedral_stencil(
    grid: Grid, program: Mapping[str, Any]
) -> Grid:
    source = int(program["source"])
    exemplar = int(program["exemplar"])
    paint = int(program["paint"])
    placement_cap = int(program.get("placement_cap", 20_000))
    exemplar_cap = int(program.get("exemplar_cap", 32))
    hit_cap = int(program.get("hit_cap", 256))
    state_cap = int(program.get("state_cap", 60_000))
    components = _components(grid, exemplar)
    if len(components) != 1 or not 3 <= len(components[0]) <= exemplar_cap:
        raise Undefined("one bounded nontrivial exemplar is required")

    rotations = _shape_orbit(components[0], reflections=False)
    dihedral = _shape_orbit(components[0], reflections=True)
    core_matches = _stencil_matches(grid, source, rotations, placement_cap)
    reflected_matches = _stencil_matches(
        grid, source, dihedral - rotations, placement_cap
    )
    hits = sorted(
        [(cells, True) for cells in core_matches]
        + [(cells, False) for cells in reflected_matches],
        key=lambda item: (not item[1], tuple(sorted(item[0]))),
    )
    if not hits or len(hits) > hit_cap:
        raise Undefined("stencil-hit inventory is absent or exceeds its bound")

    # Treat congruent hits as candidate objects.  First maximize the number of
    # pairwise-disjoint objects, then the number related to the exemplar by an
    # orientation-preserving transform.  The latter is a group-invariant
    # minimum-description tie break: C4 is the normal orientation-preserving
    # subgroup of D4.  Different optimal painted unions are genuine ambiguity.
    suffix_core = [0] * (len(hits) + 1)
    for index in range(len(hits) - 1, -1, -1):
        suffix_core[index] = suffix_core[index + 1] + int(hits[index][1])
    best = (-1, -1)
    behaviors: set[frozenset[Cell]] = set()
    states = 0

    def search(
        index: int,
        occupied: frozenset[Cell],
        count: int,
        core_count: int,
    ) -> None:
        nonlocal best, states
        states += 1
        if states > state_cap:
            raise Undefined("stencil packing state budget exhausted")
        remaining = len(hits) - index
        if count + remaining < best[0]:
            return
        if count + remaining == best[0] and core_count + suffix_core[index] < best[1]:
            return
        if index == len(hits):
            objective = count, core_count
            if objective > best:
                best = objective
                behaviors.clear()
                behaviors.add(occupied)
            elif objective == best:
                behaviors.add(occupied)
            return
        cells, orientation_preserving = hits[index]
        if cells.isdisjoint(occupied):
            search(
                index + 1,
                occupied | cells,
                count + 1,
                core_count + int(orientation_preserving),
            )
        search(index + 1, occupied, count, core_count)

    search(0, frozenset(), 0, 0)
    if best[0] < 1 or len(behaviors) != 1:
        raise Undefined("optimal stencil packing has no unique painted behavior")
    selected = next(iter(behaviors))
    if not selected:
        raise Undefined("exemplar has no non-conflicting rendered copies")
    output = [list(row) for row in grid]
    changed = 0
    for row, column in selected:
        if output[row][column] == source:
            output[row][column] = paint
            changed += 1
    if not changed:
        raise Undefined("stencil repair emitted nothing")
    return tuple(tuple(row) for row in output)


def _longest_diagonal_run(component: frozenset[Cell]) -> int:
    longest = 1
    for dr, dc in ((1, 1), (1, -1)):
        for row, column in component:
            if (row - dr, column - dc) in component:
                continue
            length = 1
            while (row + length * dr, column + length * dc) in component:
                length += 1
            longest = max(longest, length)
    return longest


def _diagonal_run_component_filter(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    paint = int(program["paint"])
    minimum_run = int(program["minimum_run"])
    if not 3 <= minimum_run <= 8:
        raise Undefined("diagonal-run threshold is outside the finite grammar")
    selected = [
        component
        for component in _components(grid, source)
        if _longest_diagonal_run(component) >= minimum_run
    ]
    if not selected:
        raise Undefined("no component contains the demonstrated diagonal wave")
    output = [list(row) for row in grid]
    for component in selected:
        for row, column in component:
            output[row][column] = paint
    return tuple(tuple(row) for row in output)


_EXECUTORS: dict[str, Callable[[Grid, Mapping[str, Any]], Grid]] = {
    "orientation_prioritized_dihedral_stencil": _orientation_prioritized_dihedral_stencil,
    "diagonal_run_component_filter": _diagonal_run_component_filter,
}


def execute_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Execute one serialized, bounded v2 topology repair program."""

    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("unknown program schema")
    executor = _EXECUTORS.get(str(program.get("operator")))
    if executor is None:
        raise Undefined("unknown topology-repair operator")
    return _plain(executor(_grid(grid), program))


def replay_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Tournament replay hook; neither the program nor raster is mutated."""

    return execute_program(program, grid)


def _same_shape_nonidentity(train: Sequence[Pair]) -> bool:
    return all(_shape(source) == _shape(target) and source != target for source, target in train)


def _changed_pairs(source: Grid, target: Grid) -> set[tuple[int, int]]:
    return {
        (before, after)
        for before_row, after_row in zip(source, target)
        for before, after in zip(before_row, after_row)
        if before != after
    }


def _exact(program: Mapping[str, Any], train: Sequence[Pair]) -> bool:
    try:
        return all(_grid(execute_program(program, source)) == target for source, target in train)
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return False


def _enumerate(train: Sequence[Pair], limits: Limits) -> tuple[Proposal, ...]:
    if not _same_shape_nonidentity(train):
        return ()
    changed = [_changed_pairs(source, target) for source, target in train]
    common_pairs = sorted(set.intersection(*changed)) if changed else []
    common_input_colors = set.intersection(
        *[{cell for row in source for cell in row} for source, _ in train]
    )
    proposals: dict[str, Proposal] = {}
    attempts = 0

    def add(family: str, program: Mapping[str, Any], complexity: int) -> None:
        nonlocal attempts
        attempts += 1
        if attempts > limits.max_programs:
            raise Undefined("program enumeration budget exhausted")
        key = _canonical(program)
        if key not in proposals and _exact(program, train):
            proposals[key] = Proposal(family, dict(program), complexity)

    for source, paint in common_pairs:
        for minimum_run in range(3, 9):
            add(
                "topology.diagonal_run_component_filter",
                _program(
                    "diagonal_run_component_filter",
                    source=source,
                    paint=paint,
                    minimum_run=minimum_run,
                ),
                8 + minimum_run,
            )
        if paint in common_input_colors:
            add(
                "topology.orientation_prioritized_dihedral_stencil",
                _program(
                    "orientation_prioritized_dihedral_stencil",
                    source=source,
                    exemplar=paint,
                    paint=paint,
                    placement_cap=limits.max_placements,
                    exemplar_cap=limits.max_exemplar_cells,
                    hit_cap=limits.max_stencil_hits,
                    state_cap=limits.max_pack_states,
                ),
                16,
            )
    return tuple(
        sorted(
            proposals.values(),
            key=lambda proposal: (proposal.complexity, _canonical(proposal.program)),
        )
    )


def _loo_exact(proposal: Proposal, train: Sequence[Pair], limits: Limits) -> bool:
    key = _canonical(proposal.program)
    for held_index in range(len(train)):
        retained = train[:held_index] + train[held_index + 1 :]
        if not retained:
            return False
        try:
            alternatives = _enumerate(retained, limits)
        except Undefined:
            return False
        if key not in {_canonical(other.program) for other in alternatives}:
            return False
        try:
            prediction = _grid(execute_program(proposal.program, train[held_index][0]))
        except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            return False
        if prediction != train[held_index][1]:
            return False
    return True


def _recolor(grid: Grid, mapping: Mapping[int, int]) -> Grid:
    return tuple(tuple(mapping.get(cell, cell) for cell in row) for row in grid)


def _recolor_program(program: Mapping[str, Any], mapping: Mapping[int, int]) -> Mapping[str, Any]:
    transformed = dict(program)
    for key in ("source", "exemplar", "paint"):
        if key in transformed:
            transformed[key] = mapping.get(int(transformed[key]), int(transformed[key]))
    return transformed


def _counterfactual_exact(proposal: Proposal, train: Sequence[Pair], limits: Limits) -> int:
    probes = 0
    palette = {color: (color + 1) % 10 for color in range(10)}
    for source, target in train:
        for operation in ("rot90", "flip_h"):
            if probes >= limits.max_counterfactuals:
                raise Undefined("counterfactual budget exhausted")
            prediction = _grid(execute_program(proposal.program, _d4(source, operation)))
            if prediction != _d4(target, operation):
                raise Undefined("D4 counterfactual failed")
            probes += 1
        if probes >= limits.max_counterfactuals:
            raise Undefined("counterfactual budget exhausted")
        recolored_source = _recolor(source, palette)
        recolored_target = _recolor(target, palette)
        prediction = _grid(
            execute_program(_recolor_program(proposal.program, palette), recolored_source)
        )
        if prediction != recolored_target:
            raise Undefined("palette counterfactual failed")
        probes += 1
    return probes


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one uniquely guarded repaired behavior, or abstain."""

    try:
        bounds = Limits.parse(limits)
        train, tests = _sanitize(task, bounds)
        proposals = _enumerate(train, bounds)
        guarded: list[tuple[Proposal, tuple[Grid, ...], int]] = []
        for proposal in proposals:
            if not _loo_exact(proposal, train, bounds):
                continue
            try:
                probes = _counterfactual_exact(proposal, train, bounds)
                predictions = tuple(
                    _grid(execute_program(proposal.program, source)) for source in tests
                )
            except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                continue
            if all(prediction == source for prediction, source in zip(predictions, tests)):
                continue
            guarded.append((proposal, predictions, probes))
        if not guarded:
            return []

        behaviors: dict[str, list[tuple[Proposal, tuple[Grid, ...], int]]] = {}
        for item in guarded:
            behavior_hash = _digest([_plain(output) for output in item[1]])
            behaviors.setdefault(behavior_hash, []).append(item)
        if len(behaviors) != 1:
            return []
        behavior_hash, equivalent = next(iter(behaviors.items()))
        proposal, predictions, probes = min(
            equivalent,
            key=lambda item: (item[0].complexity, _canonical(item[0].program)),
        )
        return [
            {
                "family": proposal.family,
                "program": dict(proposal.program),
                "train_outputs": [_plain(target) for _, target in train],
                "test_outputs": [_plain(output) for output in predictions],
                "complexity": proposal.complexity,
                "evidence": {
                    "author": AUTHOR,
                    "induction_regime": INDUCTION_REGIME,
                    "runtime_label_access": "demonstrations_only",
                    "held_test_access": "input_key_only",
                    "task_identity_access": "none",
                    "all_demonstrations_exact": True,
                    "leave_one_demonstration_out_exact": True,
                    "loo_mode": "isolated_reproposal_then_held_execution",
                    "d4_counterfactual_exact": True,
                    "palette_counterfactual_exact": True,
                    "counterfactual_probe_count": probes,
                    "bounded_program_enumeration": True,
                    "program_attempt_cap": bounds.max_programs,
                    "bounded_stencil_placement": True,
                    "stencil_placement_cap": bounds.max_placements,
                    "bounded_stencil_packing": True,
                    "stencil_hit_cap": bounds.max_stencil_hits,
                    "stencil_pack_state_cap": bounds.max_pack_states,
                    "unique_test_behavior": True,
                    "equivalent_guarded_program_count": len(equivalent),
                    "ambiguity_abstention": True,
                    "behavior_hash": behavior_hash,
                },
            }
        ][: bounds.max_candidates]
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []


__all__ = ["Limits", "compile_task", "execute_program", "replay_program"]
