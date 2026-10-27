"""Label-blind counterfactual probes for Block 11 program hypotheses.

The generator consumes labelled *training* demonstrations, sanitized test
inputs, and the already-frozen Block 11 program records.  It never opens a
public test solution.  Exact-score evaluation lives in ``score.py`` and is a
separate process/artifact.

The experiment has two purposes:

* expose the smallest input on which training-equivalent programs disagree;
* use only independently inferred structural contracts to falsify a program.

Merely finding disagreement is not permission to guess.  A behavior is
recommended only when exactly one competitor survives a declared hard
contract.  Otherwise the certificate explicitly preserves abstention.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
from typing import Any, Callable, Iterable, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]
Executor = Callable[[Grid], Grid]
SCHEMA_VERSION = 1
GENERATOR_SCHEMA = "komorebi.block12.counterfactual_probe_freeze"


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def grid(value: Any) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a sequence of rows")
    rows: list[tuple[int, ...]] = []
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes, bytearray)):
            raise TypeError("grid row must be a sequence")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("ARC cells must be integers in [0, 9]")
            row.append(int(cell))
        rows.append(tuple(row))
    result = tuple(rows)
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        raise ValueError("grid must be nonempty and rectangular")
    if len(result) > 30 or len(result[0]) > 30:
        raise ValueError("grid exceeds ARC's 30x30 limit")
    return result


def shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def mode_color(value: Grid) -> int:
    counts = Counter(cell for row in value for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def d4(value: Grid, operation: str) -> Grid:
    value = grid(value)
    if operation == "identity":
        return value
    if operation == "rot90":
        return tuple(tuple(value[len(value) - 1 - y][x] for y in range(len(value))) for x in range(len(value[0])))
    if operation == "rot180":
        return tuple(tuple(reversed(row)) for row in reversed(value))
    if operation == "rot270":
        return tuple(tuple(value[y][len(value[0]) - 1 - x] for y in range(len(value))) for x in range(len(value[0])))
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in value)
    if operation == "flip_v":
        return tuple(reversed(value))
    if operation == "transpose":
        return tuple(tuple(value[y][x] for y in range(len(value))) for x in range(len(value[0])))
    if operation == "anti_transpose":
        return d4(d4(d4(value, "transpose"), "flip_h"), "flip_v")
    raise ValueError(f"unknown D4 operation {operation!r}")


D4_OPERATIONS = (
    "identity", "rot90", "rot180", "rot270",
    "flip_h", "flip_v", "transpose", "anti_transpose",
)
D4_INVERSE = {
    "identity": "identity", "rot90": "rot270", "rot180": "rot180",
    "rot270": "rot90", "flip_h": "flip_h", "flip_v": "flip_v",
    "transpose": "transpose", "anti_transpose": "anti_transpose",
}


def recolor(value: Grid, permutation: Mapping[int, int]) -> Grid:
    return tuple(tuple(int(permutation.get(cell, cell)) for cell in row) for row in value)


def palette_permutation(task: Mapping[str, Any]) -> dict[int, int] | None:
    """Return one deterministic bijection that fixes the inferred background."""

    inputs = [grid(example["input"]) for example in task["train"]]
    inputs.extend(grid(example["input"]) for example in task["test"])
    counts = Counter(cell for value in inputs for row in value for cell in row)
    background = min(counts, key=lambda color: (-counts[color], color))
    foreground = sorted(color for color in counts if color != background)
    if len(foreground) >= 2:
        left, right = foreground[:2]
    elif foreground:
        unused = next((color for color in range(10) if color not in counts and color != background), None)
        if unused is None:
            return None
        left, right = foreground[0], unused
    else:
        return None
    result = {color: color for color in range(10)}
    result[left], result[right] = right, left
    return result


def pad(value: Grid, top: int, bottom: int, left: int, right: int, color: int) -> Grid:
    height, width = shape(value)
    if height + top + bottom > 30 or width + left + right > 30:
        raise ValueError("padding exceeds ARC dimensions")
    blank = (color,) * (width + left + right)
    return (
        *((blank,) * top),
        *(tuple((color,) * left + row + (color,) * right) for row in value),
        *((blank,) * bottom),
    )


def duplicate_row(value: Grid, index: int) -> Grid:
    if len(value) >= 30 or not 0 <= index < len(value):
        raise ValueError("invalid row duplication")
    return value[: index + 1] + (value[index],) + value[index + 1 :]


def duplicate_column(value: Grid, index: int) -> Grid:
    if len(value[0]) >= 30 or not 0 <= index < len(value[0]):
        raise ValueError("invalid column duplication")
    return tuple(row[: index + 1] + (row[index],) + row[index + 1 :] for row in value)


def insert_gap_row(value: Grid, index: int, color: int) -> Grid:
    if len(value) >= 30 or not 0 <= index < len(value):
        raise ValueError("invalid row gap")
    return value[: index + 1] + ((color,) * len(value[0]),) + value[index + 1 :]


def insert_gap_column(value: Grid, index: int, color: int) -> Grid:
    if len(value[0]) >= 30 or not 0 <= index < len(value[0]):
        raise ValueError("invalid column gap")
    return tuple(row[: index + 1] + (color,) + row[index + 1 :] for row in value)


def components(value: Grid, *, connectivity: int = 4) -> tuple[tuple[tuple[int, int], ...], ...]:
    background = mode_color(value)
    foreground = {(y, x) for y, row in enumerate(value) for x, cell in enumerate(row) if cell != background}
    offsets = ((-1, 0), (1, 0), (0, -1), (0, 1))
    if connectivity == 8:
        offsets += ((-1, -1), (-1, 1), (1, -1), (1, 1))
    result: list[tuple[tuple[int, int], ...]] = []
    while foreground:
        start = min(foreground)
        foreground.remove(start)
        queue = deque([start])
        found = [start]
        while queue:
            y, x = queue.popleft()
            for dy, dx in offsets:
                cell = (y + dy, x + dx)
                if cell in foreground:
                    foreground.remove(cell)
                    queue.append(cell)
                    found.append(cell)
        result.append(tuple(sorted(found)))
    return tuple(sorted(result, key=lambda item: (len(item), item)))


def delete_component(value: Grid, component: Sequence[tuple[int, int]]) -> Grid:
    background = mode_color(value)
    mutable = [list(row) for row in value]
    for y, x in component:
        mutable[y][x] = background
    return tuple(tuple(row) for row in mutable)


def diagonal_atom(value: Grid) -> Grid | None:
    background = mode_color(value)
    color = next((cell for row in value for cell in row if cell != background), None)
    if color is None:
        return None
    return ((color, background), (background, color))


@dataclass(frozen=True, slots=True)
class Probe:
    input_grid: Grid
    atom: str
    seed: str
    metadata: tuple[tuple[str, Any], ...] = ()

    @property
    def probe_id(self) -> str:
        return digest({
            "input": self.input_grid,
            "atom": self.atom,
            "seed": self.seed,
            "metadata": self.metadata,
        })

    def to_record(self, *, include_grid: bool = True) -> dict[str, Any]:
        record: dict[str, Any] = {
            "probe_id": self.probe_id,
            "atom": self.atom,
            "seed": self.seed,
            "shape": list(shape(self.input_grid)),
            "nonbackground_cells": sum(
                cell != mode_color(self.input_grid)
                for row in self.input_grid for cell in row
            ),
            "metadata": dict(self.metadata),
        }
        if include_grid:
            record["input"] = self.input_grid
        return record


def generate_probes(task: Mapping[str, Any], *, maximum: int = 256) -> tuple[Probe, ...]:
    """Generate a deterministic bounded probe set from task-visible inputs."""

    if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
        raise ValueError("maximum must be a positive integer")
    seeds: list[tuple[str, Grid]] = []
    for index, example in enumerate(task["train"]):
        seeds.append((f"train:{index}", grid(example["input"])))
    for index, example in enumerate(task["test"]):
        # The input key is the only test field accessed.
        seeds.append((f"test:{index}", grid(example["input"])))
    proposals: list[Probe] = []
    for seed_name, value in seeds:
        background = mode_color(value)
        proposals.append(Probe(value, "identity", seed_name))
        for operation in D4_OPERATIONS[1:]:
            proposals.append(Probe(d4(value, operation), "d4", seed_name, (("operation", operation),)))
        if len(value) < 30 and len(value[0]) < 30:
            for name, margins in (
                ("pad_top", (1, 0, 0, 0)),
                ("pad_bottom", (0, 1, 0, 0)),
                ("pad_left", (0, 0, 1, 0)),
                ("pad_right", (0, 0, 0, 1)),
                ("translate_in_padding", (1, 0, 1, 0)),
            ):
                proposals.append(Probe(pad(value, *margins, background), name, seed_name, (("margins", margins),)))
        for index in range(min(len(value), 8)):
            if len(value) < 30:
                proposals.append(Probe(duplicate_row(value, index), "duplicate_row", seed_name, (("index", index),)))
                proposals.append(Probe(insert_gap_row(value, index, background), "row_spacing", seed_name, (("index", index),)))
        for index in range(min(len(value[0]), 8)):
            if len(value[0]) < 30:
                proposals.append(Probe(duplicate_column(value, index), "duplicate_column", seed_name, (("index", index),)))
                proposals.append(Probe(insert_gap_column(value, index, background), "column_spacing", seed_name, (("index", index),)))
        for index, component in enumerate(components(value)[:4]):
            proposals.append(Probe(delete_component(value, component), "delete_component", seed_name, (("component", index),)))
        atom = diagonal_atom(value)
        if atom is not None:
            proposals.append(Probe(atom, "diagonal_touch_atom", seed_name))
        colors = sorted({cell for row in value for cell in row if cell != background})
        if colors:
            replacement = next((color for color in range(10) if color not in {background, *colors}), None)
            if replacement is not None:
                permutation = {color: color for color in range(10)}
                permutation[colors[0]], permutation[replacement] = replacement, colors[0]
                proposals.append(Probe(
                    recolor(value, permutation), "palette_role_swap", seed_name,
                    (("left", colors[0]), ("right", replacement)),
                ))
    unique: dict[str, Probe] = {}
    for proposal in proposals:
        key = digest(proposal.input_grid)
        unique.setdefault(key, proposal)
    ordered = sorted(unique.values(), key=lambda item: (shape(item.input_grid)[0] * shape(item.input_grid)[1], item.probe_id))
    return tuple(ordered[:maximum])


@dataclass(frozen=True, slots=True)
class ExecutableHypothesis:
    behavior_hash: str
    lane: str
    schema_keys: tuple[str, ...]
    program_id: str
    program_record: Mapping[str, Any]
    execute: Executor

    @property
    def hypothesis_id(self) -> str:
        return digest({
            "behavior_hash": self.behavior_hash,
            "lane": self.lane,
            "schema_keys": self.schema_keys,
            "program_id": self.program_id,
        })


def _repo_imports(repo_root: Path) -> None:
    roots = [
        "block11/src", "block10/src", "block9/src", "block8/src", "block7/src",
        "block6/src", "block5/src", "block4/src", "block2/src", "src",
    ]
    for relative in reversed(roots):
        path = str(repo_root / relative)
        if path not in sys.path:
            sys.path.insert(0, path)


def _residual_from_record(record: Mapping[str, Any]) -> Any:
    from komorebi_lasm_transfer.residual_composition import (
        ResidualCompositionProgram, TypedResidualStage,
    )

    stages = []
    for raw in record["stages"]:
        stages.append(TypedResidualStage(
            namespace=str(raw["namespace"]),
            family=str(raw["family"]),
            program_json=str(raw["program_json"]),
            cost=int(raw["cost"]),
            semantic_id=str(raw["semantic_id"]),
            input_type=str(raw["input_type"]),
            output_type=str(raw["output_type"]),
            schema_version=int(raw["schema_version"]),
        ))
    value = ResidualCompositionProgram(tuple(stages), tuple(record["route_kinds"]), int(record["schema_version"]))
    if value.program_id != record.get("program_id"):
        raise ValueError("residual program identity mismatch")
    return value


def hypotheses_from_candidate(candidate: Mapping[str, Any], repo_root: Path) -> tuple[ExecutableHypothesis, ...]:
    """Rehydrate every representative exposed by a frozen behavior class."""

    _repo_imports(repo_root)
    result: list[ExecutableHypothesis] = []
    for mechanism in candidate.get("mechanisms", ()):
        lane = str(mechanism["lane"])
        records: list[Mapping[str, Any]] = []
        if lane == "shape_layout":
            records.extend(mechanism.get("programs", ()))
        elif "representative_program" in mechanism:
            records.append(mechanism["representative_program"])
        for record in records:
            if lane == "action_schema":
                from komorebi_lasm_action.tools import ToolProgram, execute_tool
                program = ToolProgram.from_record(record)
                executor = lambda value, program=program: grid(execute_tool(program, value))
                program_id = program.tool_id
            elif lane == "shape_layout":
                from komorebi_lasm_transfer.shape_layout import ShapeLayoutProgram
                program = ShapeLayoutProgram.from_record(record)
                executor = lambda value, program=program: grid(program.execute(value))
                program_id = program.program_id
            elif lane == "ambient_topology":
                from komorebi_lasm_transfer.ambient_topology import AmbientTopologyProgram
                program = AmbientTopologyProgram.from_record(record)
                executor = lambda value, program=program: grid(program.execute(value))
                program_id = program.program_id
            elif lane == "residual_composition":
                from komorebi_lasm_transfer.residual_composition import execute_residual_program
                program = _residual_from_record(record)
                executor = lambda value, program=program: grid(execute_residual_program(program, value))
                program_id = program.program_id
            else:
                continue
            result.append(ExecutableHypothesis(
                behavior_hash=str(candidate["behavior_hash"]),
                lane=lane,
                schema_keys=tuple(sorted(str(item) for item in mechanism.get("schema_keys", ()))),
                program_id=program_id,
                program_record=dict(record),
                execute=executor,
            ))
    by_id = {item.hypothesis_id: item for item in result}
    return tuple(by_id[key] for key in sorted(by_id))


def execute_safely(hypothesis: ExecutableHypothesis, value: Grid) -> tuple[str, Grid | str]:
    try:
        return "ok", grid(hypothesis.execute(value))
    except Exception as error:  # the certificate records fail-closed executor behavior
        return "error", f"{type(error).__name__}: {error}"


def behavior_signature(hypotheses: Sequence[ExecutableHypothesis], value: Grid) -> tuple[Any, ...]:
    return tuple(execute_safely(hypothesis, value) for hypothesis in hypotheses)


def differing_coordinates(records: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    """Return semantic record paths whose values vary across hypotheses."""

    if len(records) < 2:
        return ()
    ignored = {"content_hash", "program_id", "tool_id", "parameters_json"}

    def flatten(value: Any, prefix: str = "") -> dict[str, str]:
        result: dict[str, str] = {}
        if isinstance(value, Mapping):
            for key in sorted(value):
                if key in ignored:
                    continue
                child = f"{prefix}.{key}" if prefix else str(key)
                result.update(flatten(value[key], child))
        elif isinstance(value, (list, tuple)):
            for index, item in enumerate(value):
                result.update(flatten(item, f"{prefix}[{index}]"))
        else:
            result[prefix] = canonical_json(value)
        return result

    flattened = [flatten(record) for record in records]
    paths = sorted(set().union(*(set(item) for item in flattened)))
    return tuple(
        path for path in paths
        if len({item.get(path, "<missing>") for item in flattened}) > 1
    )


def refinement_axes(paths: Sequence[str]) -> tuple[str, ...]:
    mapping = {
        "source_mode": "run_multiplicity",
        "connectivity": "connectivity_choice",
        "selector": "component_selector",
        "monochrome_components": "color_partition",
        "background_role": "background_binding",
        "paint_role": "palette_binding",
        "row_factor": "row_scale",
        "column_factor": "column_scale",
    }
    result = set()
    for path in paths:
        leaf = path.rsplit(".", 1)[-1]
        leaf = leaf.split("[", 1)[0]
        result.add(mapping.get(leaf, leaf))
    return tuple(sorted(result))


def distinguishes(hypotheses: Sequence[ExecutableHypothesis], value: Grid) -> bool:
    signatures = behavior_signature(hypotheses, value)
    return len({canonical_json(item) for item in signatures}) > 1


def minimize_distinguishing_grid(value: Grid, hypotheses: Sequence[ExecutableHypothesis]) -> Grid:
    """Greedily obtain a deterministic 1-minimal candidate-disagreement grid."""

    current = grid(value)
    if not distinguishes(hypotheses, current):
        raise ValueError("input does not distinguish hypotheses")
    changed = True
    while changed:
        changed = False
        background = mode_color(current)
        candidates: list[Grid] = []
        if len(current) > 1:
            candidates.extend((current[1:], current[:-1]))
        if len(current[0]) > 1:
            candidates.append(tuple(tuple(row[1:]) for row in current))
            candidates.append(tuple(tuple(row[:-1]) for row in current))
        for y, row in enumerate(current):
            for x, cell in enumerate(row):
                if cell == background:
                    continue
                mutable = [list(item) for item in current]
                mutable[y][x] = background
                if all(cell == background for item in mutable for cell in item):
                    continue
                candidates.append(tuple(tuple(item) for item in mutable))
        valid = [candidate for candidate in candidates if distinguishes(hypotheses, candidate)]
        if valid:
            current = min(valid, key=lambda item: (len(item) * len(item[0]), sum(cell != mode_color(item) for row in item for cell in row), digest(item)))
            changed = True
    return current


def repeat_pixels(value: Grid, rows: int, columns: int) -> Grid:
    return tuple(
        tuple(cell for cell in row for _ in range(columns))
        for row in value for _ in range(rows)
    )


def infer_contracts(task: Mapping[str, Any]) -> dict[str, Any]:
    pairs = [(grid(example["input"]), grid(example["output"])) for example in task["train"]]
    contracts: dict[str, Any] = {}
    if all(shape(source) == shape(target) for source, target in pairs):
        contracts["shape_law"] = {"kind": "identity"}
    else:
        exact_repeats = []
        for row_factor in range(1, 7):
            for column_factor in range(1, 7):
                if (row_factor, column_factor) == (1, 1):
                    continue
                if all(repeat_pixels(source, row_factor, column_factor) == target for source, target in pairs):
                    exact_repeats.append((row_factor, column_factor))
        # A direct cell-block law is allowed to become hard only after at
        # least two differently shaped demonstrations independently support
        # the same factors.  This is a finite leave-one-demonstration-out
        # check: each remaining example identifies the factors and the held
        # out raster must replay exactly.
        distinct_source_shapes = len({shape(source) for source, _ in pairs})
        loo_validated = False
        if len(exact_repeats) == 1 and len(pairs) >= 2 and distinct_source_shapes >= 2:
            candidate_factors = exact_repeats[0]
            loo_validated = all(
                all(
                    repeat_pixels(source, *candidate_factors) == target
                    for index, (source, target) in enumerate(pairs) if index != held_out
                )
                and repeat_pixels(pairs[held_out][0], *candidate_factors) == pairs[held_out][1]
                for held_out in range(len(pairs))
            )
        if len(exact_repeats) == 1 and loo_validated:
            rows, columns = exact_repeats[0]
            contracts["shape_law"] = {
                "kind": "full_nearest_neighbor_replication",
                "row_factor": rows,
                "column_factor": columns,
                "evidence_examples": len(pairs),
                "distinct_source_shapes": distinct_source_shapes,
                "leave_one_demonstration_out": True,
                "assumption_tier": "finite_exact_cell_law",
            }
        elif len({shape(target) for _, target in pairs}) == 1:
            contracts["shape_law"] = {"kind": "fixed", "shape": list(shape(pairs[0][1]))}
    if all(shape(source) == shape(target) for source, target in pairs):
        relations = []
        for source, target in pairs:
            background = mode_color(source)
            before = {(y, x) for y, row in enumerate(source) for x, cell in enumerate(row) if cell != background}
            after = {(y, x) for y, row in enumerate(target) for x, cell in enumerate(row) if cell != background}
            relations.append("add" if before <= after else "remove" if after <= before else "mixed")
        if len(set(relations)) == 1:
            contracts["support_law"] = relations[0]
    return contracts


def check_contracts(
    hypothesis: ExecutableHypothesis,
    probes: Sequence[Probe],
    contracts: Mapping[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    shape_law = contracts.get("shape_law", {})
    kind = shape_law.get("kind")
    for probe in probes:
        status, observed = execute_safely(hypothesis, probe.input_grid)
        if status != "ok":
            # Domain-specific ARC programs may be deliberately inapplicable
            # to arbitrary synthetic scenes.  Only the certified full pixel
            # replication law asserts totality over every valid grid.
            if kind == "full_nearest_neighbor_replication":
                checks.append({"probe_id": probe.probe_id, "contract": "executor_totality", "passed": False, "error": observed})
            continue
        assert isinstance(observed, tuple)
        if kind == "identity":
            passed = shape(observed) == shape(probe.input_grid)
            checks.append({"probe_id": probe.probe_id, "contract": "identity_shape", "passed": passed})
        elif kind == "full_nearest_neighbor_replication":
            expected = repeat_pixels(probe.input_grid, int(shape_law["row_factor"]), int(shape_law["column_factor"]))
            passed = observed == expected
            checks.append({
                "probe_id": probe.probe_id,
                "contract": "full_nearest_neighbor_replication",
                "passed": passed,
                "expected_hash": digest(expected),
                "observed_hash": digest(observed),
            })
        elif kind == "fixed":
            passed = list(shape(observed)) == list(shape_law["shape"])
            checks.append({"probe_id": probe.probe_id, "contract": "fixed_shape", "passed": passed})
    failures = [item for item in checks if not item["passed"]]
    return {
        "hypothesis_id": hypothesis.hypothesis_id,
        "checks": len(checks),
        "passed": len(checks) - len(failures),
        "failed": len(failures),
        "first_failure": failures[0] if failures else None,
        "failed_probe_ids": sorted({item["probe_id"] for item in failures}),
        "survives_hard_contracts": not failures,
    }


def minimum_hitting_set_certificate(
    hypotheses: Sequence[ExecutableHypothesis],
    checks: Sequence[Mapping[str, Any]],
    probes: Sequence[Probe],
    winning_behavior_hash: str,
    *,
    maximum_combinations: int = 100_000,
    maximum_cardinality: int = 8,
) -> dict[str, Any] | None:
    """Return an exact minimum probe set relative to the frozen pool.

    A single executable winner must survive the complete set, while every
    represented rival program is rejected by at least one selected probe.
    The exhaustive subset search is bounded explicitly.  If the finite proof
    cannot be completed inside the declared budget, the returned record is an
    incomplete certificate and callers must abstain.
    """

    if (
        isinstance(maximum_combinations, bool)
        or not isinstance(maximum_combinations, int)
        or maximum_combinations < 1
    ):
        raise ValueError("maximum_combinations must be a positive integer")
    if (
        isinstance(maximum_cardinality, bool)
        or not isinstance(maximum_cardinality, int)
        or maximum_cardinality < 0
    ):
        raise ValueError("maximum_cardinality must be a nonnegative integer")

    probe_by_id = {probe.probe_id: probe for probe in probes}
    check_by_hypothesis = {str(item["hypothesis_id"]): item for item in checks}
    winners = [item for item in hypotheses if item.behavior_hash == winning_behavior_hash]
    rivals = [item for item in hypotheses if item.behavior_hash != winning_behavior_hash]
    if not winners or not rivals:
        return None
    best: tuple[Any, ...] | None = None
    best_record: dict[str, Any] | None = None
    combinations_checked = 0
    exhausted = False
    for winner in winners:
        winner_failures = set(check_by_hypothesis[winner.hypothesis_id]["failed_probe_ids"])
        coverage: dict[str, set[str]] = {}
        for rival in rivals:
            for probe_id in check_by_hypothesis[rival.hypothesis_id]["failed_probe_ids"]:
                if probe_id not in winner_failures:
                    coverage.setdefault(probe_id, set()).add(rival.hypothesis_id)
        universe = {rival.hypothesis_id for rival in rivals}
        atom_priority = {
            "duplicate_row": 0,
            "duplicate_column": 1,
            "row_spacing": 2,
            "column_spacing": 3,
            "pad_top": 4,
            "pad_bottom": 4,
            "pad_left": 4,
            "pad_right": 4,
            "translate_in_padding": 5,
            "d4": 6,
            "palette_role_swap": 7,
            "delete_component": 8,
            "diagonal_touch_atom": 9,
            "identity": 10,
        }
        useful = sorted(
            coverage,
            key=lambda probe_id: (
                # Prefer actual interventions to an identity view of the test.
                atom_priority.get(probe_by_id[probe_id].atom, 8),
                probe_by_id[probe_id].seed.startswith("test:"),
                shape(probe_by_id[probe_id].input_grid)[0] * shape(probe_by_id[probe_id].input_grid)[1],
                probe_id,
            ),
        )
        selected: tuple[str, ...] | None = None
        search_cardinality = min(len(useful), maximum_cardinality)
        for size in range(1, search_cardinality + 1):
            for candidate in combinations(useful, size):
                if combinations_checked >= maximum_combinations:
                    exhausted = True
                    break
                combinations_checked += 1
                if set().union(*(coverage[item] for item in candidate)) >= universe:
                    selected = candidate
                    break
            if exhausted:
                break
            if selected is not None:
                break
        if exhausted:
            break
        if selected is None:
            if len(useful) > maximum_cardinality:
                exhausted = True
                break
            continue
        rank = (
            len(selected),
            sum(atom_priority.get(probe_by_id[item].atom, 8) for item in selected),
            sum(shape(probe_by_id[item].input_grid)[0] * shape(probe_by_id[item].input_grid)[1] for item in selected),
            tuple(selected),
            winner.hypothesis_id,
        )
        if best is None or rank < best:
            best = rank
            best_record = {
                "scope": "exact relative to the frozen probe pool and represented executable inventory",
                "winner_hypothesis_id": winner.hypothesis_id,
                "winner_behavior_hash": winning_behavior_hash,
                "rival_hypothesis_ids": sorted(universe),
                "selected_probe_ids": list(selected),
                "selected_probes": [probe_by_id[item].to_record() for item in selected],
                "elimination_coverage": {
                    item: sorted(coverage[item]) for item in selected
                },
                "minimum_cardinality": len(selected),
                "complete": True,
                "status": "exact_minimum",
                "search_budget": {
                    "maximum_combinations": maximum_combinations,
                    "maximum_cardinality": maximum_cardinality,
                },
                "smaller_subset_exhaustion": {
                    "checked_cardinalities": list(range(len(selected))),
                    "all_smaller_subsets_fail_to_cover_every_rival": True,
                    "zero_subset_covers_rivals": False,
                },
            }
    if exhausted:
        incomplete = {
            "scope": "frozen probe pool and represented executable inventory",
            "complete": False,
            "status": "resource_exhausted",
            "winning_behavior_hash": winning_behavior_hash,
            "combinations_checked": combinations_checked,
            "search_budget": {
                "maximum_combinations": maximum_combinations,
                "maximum_cardinality": maximum_cardinality,
            },
        }
        incomplete["certificate_hash"] = digest(incomplete)
        return incomplete
    if best_record is not None:
        best_record["combinations_checked"] = combinations_checked
        best_record["certificate_hash"] = digest(best_record)
    return best_record


def evaluate_record(
    task_id: str,
    task: Mapping[str, Any],
    frozen_record: Mapping[str, Any],
    repo_root: Path,
    *,
    maximum_probes: int = 256,
    maximum_hitting_set_combinations: int = 100_000,
    maximum_hitting_set_cardinality: int = 8,
    frozen_probes: Sequence[Probe] | None = None,
) -> dict[str, Any]:
    candidates = list(frozen_record.get("candidates", ()))
    hypotheses = [
        hypothesis
        for candidate in candidates
        for hypothesis in hypotheses_from_candidate(candidate, repo_root)
    ]
    probes = tuple(frozen_probes) if frozen_probes is not None else generate_probes(task, maximum=maximum_probes)
    contracts = infer_contracts(task)
    checks = [check_contracts(hypothesis, probes, contracts) for hypothesis in hypotheses]
    coordinate_paths = differing_coordinates([item.program_record for item in hypotheses])
    behavior_survival: dict[str, bool] = {}
    inventory_complete = all(
        all(mechanism.get("lane") == "shape_layout" and "programs" in mechanism for mechanism in candidate.get("mechanisms", ()))
        for candidate in candidates
    )
    for candidate in candidates:
        members = [
            check for check, hypothesis in zip(checks, hypotheses)
            if hypothesis.behavior_hash == candidate["behavior_hash"]
        ]
        behavior_survival[str(candidate["behavior_hash"])] = bool(members) and any(
            item["survives_hard_contracts"] for item in members
        )
    survivors = sorted(key for key, survives in behavior_survival.items() if survives)

    discriminating = [probe for probe in probes if len(hypotheses) >= 2 and distinguishes(hypotheses, probe.input_grid)]
    minimal_record = None
    if discriminating:
        initial = min(discriminating, key=lambda item: (shape(item.input_grid)[0] * shape(item.input_grid)[1], item.probe_id))
        minimal = minimize_distinguishing_grid(initial.input_grid, hypotheses)
        outputs = []
        for hypothesis in hypotheses:
            status, observed = execute_safely(hypothesis, minimal)
            outputs.append({
                "hypothesis_id": hypothesis.hypothesis_id,
                "behavior_hash": hypothesis.behavior_hash,
                "program_id": hypothesis.program_id,
                "lane": hypothesis.lane,
                "status": status,
                "output_shape": list(shape(observed)) if status == "ok" else None,
                "output_hash": digest(observed) if status == "ok" else "",
                "error": observed if status == "error" else None,
            })
        minimal_record = {
            "source_probe_id": initial.probe_id,
            "source_atom": initial.atom,
            "input": minimal,
            "input_hash": digest(minimal),
            "shape": list(shape(minimal)),
            "nonbackground_cells": sum(cell != mode_color(minimal) for row in minimal for cell in row),
            "outputs": outputs,
        }

    recommended = (
        survivors[0]
        if len(candidates) > 1 and len(survivors) == 1 and inventory_complete
        else ""
    )
    hitting_set = minimum_hitting_set_certificate(
        hypotheses,
        checks,
        probes,
        recommended,
        maximum_combinations=maximum_hitting_set_combinations,
        maximum_cardinality=maximum_hitting_set_cardinality,
    ) if recommended else None
    hitting_set_incomplete = bool(
        hitting_set is not None and not hitting_set.get("complete", False)
    )
    if recommended and (hitting_set is None or hitting_set_incomplete):
        # A recommendation without an executable elimination proof is invalid.
        recommended = ""
    status = (
        "resolved_by_hard_contract" if recommended
        else "hitting_set_limit_abstention" if hitting_set_incomplete
        else "distinguished_but_underidentified" if len(candidates) > 1 and minimal_record
        else "candidate_stress_tested" if candidates
        else "no_executable_candidate"
    )
    body = {
        "schema": "komorebi.block12.counterfactual_task_certificate",
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "label_access": "none",
        "candidate_behaviors": len(candidates),
        "executable_hypotheses": len(hypotheses),
        "probe_count": len(probes),
        "discriminating_probes": len(discriminating),
        "contracts": contracts,
        "differing_program_coordinates": list(coordinate_paths),
        "refinement_axes": list(refinement_axes(coordinate_paths)),
        "contract_checks": checks,
        "behavior_survival": behavior_survival,
        "executable_inventory_complete_for_selection": inventory_complete,
        "recommended_behavior_hash": recommended,
        "selection_status": status,
        "minimum_hitting_set_certificate": hitting_set,
        "minimal_distinguishing_certificate": minimal_record,
        "probe_set_hash": digest([probe.to_record() for probe in probes]),
    }
    body["content_hash"] = digest(body)
    return body


def transform_task(task: Mapping[str, Any], kind: str) -> tuple[dict[str, Any], Callable[[Grid], Grid]]:
    """Create a gauge-conjugated task and its inverse output map."""

    if kind in D4_OPERATIONS[1:]:
        forward = lambda value: d4(value, kind)
        inverse = lambda value: d4(value, D4_INVERSE[kind])
    elif kind == "palette":
        permutation = palette_permutation(task)
        if permutation is None:
            raise ValueError("task has no nontrivial palette permutation")
        inverse_map = {right: left for left, right in permutation.items()}
        forward = lambda value: recolor(value, permutation)
        inverse = lambda value: recolor(value, inverse_map)
    else:
        raise ValueError("unknown task transformation")
    transformed = {
        "train": [
            {"input": forward(grid(example["input"])), "output": forward(grid(example["output"]))}
            for example in task["train"]
        ],
        "test": [
            {"input": forward(grid(example["input"]))}
            for example in task["test"]
        ],
    }
    return transformed, inverse


def augmentation_search_task(
    task_id: str,
    task: Mapping[str, Any],
    block10_record: Mapping[str, Any],
    repo_root: Path,
    *,
    transformations: Sequence[str] = ("rot90", "rot180", "flip_h", "transpose", "palette"),
) -> dict[str, Any]:
    """Search conjugate compiler gauges without opening a held-out solution."""

    _repo_imports(repo_root)
    from komorebi_lasm_transfer.compiler import compile_transfer_task

    variants: list[dict[str, Any]] = []
    for kind in transformations:
        try:
            transformed, inverse = transform_task(task, kind)
            record = compile_transfer_task(
                task_id,
                transformed,
                block10_record,
                allow_provisional_action=True,
                allow_provisional_shape=True,
                allow_provisional_residual=True,
                allow_provisional_ambient=True,
            )
            if record.get("unique_test_behavior") and len(record.get("candidates", ())) == 1:
                predictions = tuple(inverse(grid(value)) for value in record["candidates"][0]["test_predictions"])
                variants.append({
                    "transformation": kind,
                    "status": "unique",
                    "prediction": predictions,
                    "prediction_hash": digest(predictions),
                    "source_behavior_hash": record["candidates"][0]["behavior_hash"],
                })
            else:
                variants.append({
                    "transformation": kind,
                    "status": "ambiguous" if record.get("candidates") else "no_candidate",
                    "candidate_behaviors": len(record.get("candidates", ())),
                    "error": record.get("error"),
                })
        except Exception as error:
            variants.append({"transformation": kind, "status": "error", "error": f"{type(error).__name__}: {error}"})
    groups: dict[str, list[dict[str, Any]]] = {}
    for variant in variants:
        if variant["status"] == "unique":
            groups.setdefault(variant["prediction_hash"], []).append(variant)
    consensus = ""
    prediction: tuple[Grid, ...] | None = None
    # Two independently transformed compiler runs must agree and no successful
    # transformed run may disagree.  This remains a hypothesis, not a commit.
    if len(groups) == 1 and sum(len(items) for items in groups.values()) >= 2:
        consensus = next(iter(groups))
        prediction = groups[consensus][0]["prediction"]
    body = {
        "schema": "komorebi.block12.gauge_augmentation_search",
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "label_access": "none",
        "variants": variants,
        "unique_variant_count": sum(item["status"] == "unique" for item in variants),
        "behavior_groups": {key: len(items) for key, items in sorted(groups.items())},
        "consensus_prediction_hash": consensus,
        "consensus_prediction": prediction,
        "eligible_for_score_only": prediction is not None,
    }
    body["content_hash"] = digest(body)
    return body


def deterministic_sample(task_ids: Iterable[str], count: int, salt: str) -> tuple[str, ...]:
    ranked = sorted(set(task_ids), key=lambda task_id: (digest([salt, task_id]), task_id))
    return tuple(ranked[:count])


def freeze_experiment(
    challenges: Mapping[str, Any],
    block11_freeze: Mapping[str, Any],
    block10_records: Mapping[str, Any],
    repo_root: Path,
    *,
    search_sample: int = 16,
    maximum_probes: int = 256,
) -> dict[str, Any]:
    """Run the complete label-blind experiment and return its frozen record."""

    if block11_freeze.get("phase") != "prediction_freeze_before_solution_open" or block11_freeze.get("label_access") != "none":
        raise ValueError("Block 11 input is not an authenticated label-blind freeze")
    records = block11_freeze["records"]
    if set(challenges) != set(records) or set(challenges) != set(block10_records):
        raise ValueError("corpus task sets disagree")
    bank = json.loads((repo_root / "block11/results/runtime_schema_bank.json").read_text())
    provisional = {
        entry["schema_key"] for entry in bank["entries"] if entry["explicitly_provisional"]
    }
    target_ids = []
    for task_id, record in records.items():
        if len(record.get("candidates", ())) > 1:
            target_ids.append(task_id)
            continue
        keys = {
            f"{mechanism['lane']}:{key}"
            for candidate in record.get("candidates", ())
            for mechanism in candidate.get("mechanisms", ())
            for key in mechanism.get("schema_keys", ())
        }
        if keys & provisional:
            target_ids.append(task_id)
    # Freeze the task-only pool before any candidate is executed.  Its
    # construction function cannot accept candidates, predictions, or a
    # solution stream.
    probe_pools = {
        task_id: generate_probes(challenges[task_id], maximum=maximum_probes)
        for task_id in sorted(set(target_ids))
    }
    probe_pool_records = {
        task_id: {
            "schema": "komorebi.block12.task_only_probe_pool",
            "schema_version": SCHEMA_VERSION,
            "task_id": task_id,
            "label_access": "none",
            "probes": [probe.to_record() for probe in probes],
            "pool_hash": digest([probe.to_record() for probe in probes]),
        }
        for task_id, probes in probe_pools.items()
    }
    certificates = {
        task_id: evaluate_record(
            task_id, challenges[task_id], records[task_id], repo_root,
            maximum_probes=maximum_probes,
            frozen_probes=probe_pools[task_id],
        )
        for task_id in sorted(set(target_ids))
    }

    # Sampling is based solely on the frozen compiler state, never correctness.
    no_candidate = [
        task_id for task_id, record in records.items()
        if record.get("route_eligible") and not record.get("candidates") and not record.get("error")
    ]
    sample_ids = deterministic_sample(no_candidate, search_sample, "block12-counterfactual-gauge-v1")
    augmentation = {
        task_id: augmentation_search_task(
            task_id, challenges[task_id], block10_records[task_id], repo_root,
        )
        for task_id in sample_ids
    }
    body = {
        "schema": GENERATOR_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "author": "Komorebi P.",
        "phase": "counterfactual_prediction_freeze_before_solution_open",
        "label_access": "none",
        "claim_boundary": "Training outputs constrain probes; test outputs and public solution files are not opened.",
        "source_hashes": {
            "block11_freeze": digest(block11_freeze),
            "challenge_corpus": digest(challenges),
            "block10_records": digest(block10_records),
        },
        "policy": {
            "ambiguity_resolution": "exactly one behavior survives a declared hard contract",
            "unresolved_ambiguity": "abstain",
            "augmentation_consensus": "at least two successful conjugate compilers and no disagreement",
            "augmentation_status": "score-only experiment; never automatically committed",
            "sample_selection": "SHA-256 rank over zero-candidate frozen records",
        },
        "target_task_ids": sorted(certificates),
        "probe_pools": probe_pool_records,
        "certificates": certificates,
        "search_sample_task_ids": list(sample_ids),
        "augmentation_search": augmentation,
        "refinement_queue": [
            {
                "task_id": task_id,
                "selection_status": certificate["selection_status"],
                "axes": certificate["refinement_axes"],
                "certificate_hash": certificate["content_hash"],
            }
            for task_id, certificate in sorted(certificates.items())
            if certificate["refinement_axes"]
        ],
        "summary": {
            "target_tasks": len(certificates),
            "ambiguous_tasks": sum(len(records[task_id].get("candidates", ())) > 1 for task_id in certificates),
            "resolved_ambiguities": sum(bool(item["recommended_behavior_hash"]) for item in certificates.values()),
            "preserved_abstentions": sum(item["selection_status"] == "distinguished_but_underidentified" for item in certificates.values()),
            "provisional_tasks_stress_tested": sum(len(records[task_id].get("candidates", ())) == 1 for task_id in certificates),
            "search_sample_tasks": len(augmentation),
            "augmentation_consensus_candidates": sum(item["eligible_for_score_only"] for item in augmentation.values()),
        },
    }
    body["content_hash"] = digest(body)
    return body


def compact_summary(freeze: Mapping[str, Any]) -> dict[str, Any]:
    """Strip raster-heavy search traces while retaining auditable digests."""

    ambiguities = {}
    for task_id, certificate in freeze["certificates"].items():
        ambiguities[task_id] = {
            "selection_status": certificate["selection_status"],
            "candidate_behaviors": certificate["candidate_behaviors"],
            "probe_count": certificate["probe_count"],
            "discriminating_probes": certificate["discriminating_probes"],
            "recommended_behavior_hash": certificate["recommended_behavior_hash"],
            "minimum_hitting_set_certificate": certificate["minimum_hitting_set_certificate"],
            "minimal_distinguishing_certificate": certificate["minimal_distinguishing_certificate"],
            "content_hash": certificate["content_hash"],
        }
    augmentation = {
        task_id: {
            "unique_variant_count": record["unique_variant_count"],
            "behavior_groups": record["behavior_groups"],
            "consensus_prediction_hash": record["consensus_prediction_hash"],
            "eligible_for_score_only": record["eligible_for_score_only"],
            "content_hash": record["content_hash"],
        }
        for task_id, record in freeze["augmentation_search"].items()
    }
    body = {
        "schema": "komorebi.block12.counterfactual_probe_summary",
        "schema_version": SCHEMA_VERSION,
        "author": freeze["author"],
        "label_access": "none",
        "freeze_content_hash": freeze["content_hash"],
        "source_hashes": freeze["source_hashes"],
        "summary": freeze["summary"],
        "refinement_queue": freeze["refinement_queue"],
        "ambiguity_certificates": ambiguities,
        "augmentation_search": augmentation,
    }
    body["content_hash"] = digest(body)
    return body


__all__ = [
    "D4_INVERSE", "D4_OPERATIONS", "ExecutableHypothesis", "Probe",
    "augmentation_search_task", "canonical_json", "check_contracts",
    "compact_summary", "components", "d4", "deterministic_sample", "digest",
    "distinguishes", "evaluate_record", "freeze_experiment", "generate_probes",
    "grid", "hypotheses_from_candidate", "infer_contracts",
    "minimize_distinguishing_grid", "palette_permutation", "recolor",
    "repeat_pixels", "shape", "transform_task",
]
