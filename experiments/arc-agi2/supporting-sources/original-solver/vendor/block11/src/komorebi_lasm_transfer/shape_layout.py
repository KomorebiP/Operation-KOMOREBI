"""Safe shape/layout constructors promoted by the Block 11 lane-C audit.

This module intentionally contains only three schemas:

* adjacent-run quotienting over rows then columns (stable),
* behavior-quotiented nearest-neighbor replication (stable), and
* primitive periodic-tile extraction (provisional, opt-in).

Compilation uses labelled training demonstrations and test inputs only.  A
program has no field capable of storing a target, prediction, task identifier,
or expected-output hash.  The finite grammar is enumerated completely before
any candidate may be emitted, and all admitted programs are quotiented by the
complete tuple of test-input raster behaviors.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]
SCHEMA_VERSION = 1
PROGRAM_SCHEMA = "komorebi.lasm_transfer.shape_layout_program"
COMPILER_SCHEMA = "komorebi.lasm_transfer.shape_layout_compilation"

ADJACENT_RUN_QUOTIENT = "adjacent_run_quotient"
NEAREST_NEIGHBOR_REPLICATION = "nearest_neighbor_replication"
PERIODIC_TILE_EXTRACT = "periodic_tile_extract"

STABLE_SCHEMAS = frozenset({ADJACENT_RUN_QUOTIENT, NEAREST_NEIGHBOR_REPLICATION})
PROVISIONAL_SCHEMAS = frozenset({PERIODIC_TILE_EXTRACT})
_ALL_SCHEMAS = STABLE_SCHEMAS | PROVISIONAL_SCHEMAS

_SOURCE_MODES = (
    ("full", "none"),
    ("dedupe_rc", "none"),
    ("squeeze_uniform_rc", "mode"),
    ("squeeze_uniform_rc", "corner"),
    ("crop_nonbackground", "mode"),
    ("crop_nonbackground", "corner"),
)
_COLOR_ROLES = frozenset({"none", "mode", "corner"})
_MAX_FACTOR = 6
_MAX_GRID_DIMENSION = 30
_FORBIDDEN_RECORD_FIELDS = frozenset(
    {"task_id", "target", "targets", "output", "outputs", "prediction", "predictions", "answer", "label"}
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _content_hash(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("ascii")).hexdigest()


def validate_grid(value: Any, *, output: bool = False) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a sequence of rows")
    rows = []
    for row in value:
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes, bytearray)):
            raise TypeError("grid row must be a sequence")
        values = []
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int):
                raise TypeError("grid cells must be integers")
            if cell < 0 or cell > 9:
                raise ValueError("ARC colors must lie in [0, 9]")
            values.append(int(cell))
        rows.append(tuple(values))
    result = tuple(rows)
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        raise ValueError("grid must be nonempty and rectangular")
    if len(result) > _MAX_GRID_DIMENSION or len(result[0]) > _MAX_GRID_DIMENSION:
        kind = "output" if output else "input"
        raise ValueError(f"{kind} grid exceeds ARC's 30x30 bound")
    return result


def _shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def _mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise ValueError("cannot select a color from an empty collection")
    return min(counts, key=lambda item: (-counts[item], item))


def _resolve_color(source: Grid, role: str) -> int:
    if role == "mode":
        return _mode(cell for row in source for cell in row)
    if role == "corner":
        return _mode((source[0][0], source[0][-1], source[-1][0], source[-1][-1]))
    raise ValueError(f"color role {role!r} is not executable")


def _dedupe_rows_columns(source: Grid) -> Grid:
    rows = tuple(
        row for index, row in enumerate(source)
        if index == 0 or row != source[index - 1]
    )
    columns = tuple(
        x for x in range(len(rows[0]))
        if x == 0 or any(row[x] != row[x - 1] for row in rows)
    )
    return tuple(tuple(row[x] for x in columns) for row in rows)


def _squeeze_uniform(source: Grid, background_role: str) -> Grid:
    background = _resolve_color(source, background_role)
    remove_rows = {
        y for y, row in enumerate(source) if all(cell == background for cell in row)
    }
    remove_columns = {
        x for x in range(len(source[0]))
        if all(source[y][x] == background for y in range(len(source)))
    }
    result = tuple(
        tuple(cell for x, cell in enumerate(row) if x not in remove_columns)
        for y, row in enumerate(source)
        if y not in remove_rows
    )
    if not result or not result[0]:
        raise ValueError("uniform squeeze removed the complete grid")
    return result


def _crop_nonbackground(source: Grid, background_role: str) -> Grid:
    background = _resolve_color(source, background_role)
    cells = [
        (y, x)
        for y, row in enumerate(source)
        for x, cell in enumerate(row)
        if cell != background
    ]
    if not cells:
        raise ValueError("cannot crop an empty foreground")
    ys = [cell[0] for cell in cells]
    xs = [cell[1] for cell in cells]
    y0, y1, x0, x1 = min(ys), max(ys) + 1, min(xs), max(xs) + 1
    return tuple(tuple(row[x0:x1]) for row in source[y0:y1])


def _primitive_period(source: Grid) -> Grid:
    height, width = _shape(source)
    for rows in range(1, height + 1):
        if height % rows:
            continue
        for columns in range(1, width + 1):
            if width % columns:
                continue
            tile = tuple(tuple(source[y][x] for x in range(columns)) for y in range(rows))
            if all(
                source[y][x] == tile[y % rows][x % columns]
                for y in range(height)
                for x in range(width)
            ):
                return tile
    return source


def _latent_source(source: Grid, mode: str, background_role: str) -> Grid:
    if mode == "full":
        return source
    if mode == "dedupe_rc":
        return _dedupe_rows_columns(source)
    if mode == "squeeze_uniform_rc":
        return _squeeze_uniform(source, background_role)
    if mode == "crop_nonbackground":
        return _crop_nonbackground(source, background_role)
    raise ValueError(f"unsupported latent source mode {mode!r}")


def _repeat_pixels(source: Grid, rows: int, columns: int) -> Grid:
    return tuple(
        tuple(cell for cell in row for _ in range(columns))
        for row in source
        for _ in range(rows)
    )


@dataclass(frozen=True, slots=True)
class ShapeLayoutProgram:
    """Immutable, target-free executable shape/layout program."""

    family: str
    source_mode: str
    background_role: str = "none"
    row_factor: int = 1
    column_factor: int = 1

    def __post_init__(self) -> None:
        if self.family not in _ALL_SCHEMAS:
            raise ValueError(f"unsupported shape/layout family {self.family!r}")
        if self.background_role not in _COLOR_ROLES:
            raise ValueError("unsupported background role")
        if (
            isinstance(self.row_factor, bool)
            or not isinstance(self.row_factor, int)
            or isinstance(self.column_factor, bool)
            or not isinstance(self.column_factor, int)
        ):
            raise TypeError("replication factors must be integers")
        if not 1 <= self.row_factor <= _MAX_FACTOR or not 1 <= self.column_factor <= _MAX_FACTOR:
            raise ValueError("replication factors must lie in [1, 6]")
        if self.family == ADJACENT_RUN_QUOTIENT:
            if (self.source_mode, self.background_role, self.row_factor, self.column_factor) != (
                "dedupe_rc", "none", 1, 1,
            ):
                raise ValueError("adjacent-run quotient has one closed identity-transform form")
        elif self.family == PERIODIC_TILE_EXTRACT:
            if (self.source_mode, self.background_role, self.row_factor, self.column_factor) != (
                "periodic_tile", "none", 1, 1,
            ):
                raise ValueError("periodic extraction has one closed identity-transform form")
        else:
            if (self.row_factor, self.column_factor) == (1, 1):
                raise ValueError("nearest-neighbor replication must enlarge at least one axis")
            if (self.source_mode, self.background_role) not in _SOURCE_MODES:
                raise ValueError("nearest-neighbor source/role pair is outside the finite grammar")

    @classmethod
    def adjacent_run_quotient(cls) -> "ShapeLayoutProgram":
        return cls(ADJACENT_RUN_QUOTIENT, "dedupe_rc")

    @classmethod
    def nearest_neighbor_replication(
        cls,
        row_factor: int,
        column_factor: int,
        *,
        source_mode: str = "full",
        background_role: str = "none",
    ) -> "ShapeLayoutProgram":
        return cls(
            NEAREST_NEIGHBOR_REPLICATION,
            source_mode,
            background_role,
            row_factor,
            column_factor,
        )

    @classmethod
    def periodic_tile_extract(cls) -> "ShapeLayoutProgram":
        return cls(PERIODIC_TILE_EXTRACT, "periodic_tile")

    @property
    def parameters(self) -> dict[str, Any]:
        if self.family == NEAREST_NEIGHBOR_REPLICATION:
            return {
                "source_mode": self.source_mode,
                "background_role": self.background_role,
                "row_factor": self.row_factor,
                "column_factor": self.column_factor,
                "transform": "identity",
            }
        return {"source_mode": self.source_mode, "transform": "identity"}

    @property
    def program_id(self) -> str:
        return _content_hash(self.identity_record())

    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": PROGRAM_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "family": self.family,
            "parameters": self.parameters,
        }

    def to_record(self) -> dict[str, Any]:
        body = self.identity_record()
        body["program_id"] = self.program_id
        return body

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "ShapeLayoutProgram":
        if not isinstance(record, Mapping):
            raise TypeError("program record must be a mapping")
        if _FORBIDDEN_RECORD_FIELDS & set(record):
            raise ValueError("program record contains a target-bearing field")
        allowed = {"schema", "schema_version", "family", "parameters", "program_id"}
        if set(record) - allowed:
            raise ValueError("program record has unknown fields")
        if record.get("schema") != PROGRAM_SCHEMA or record.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("program schema contract mismatch")
        parameters = record.get("parameters")
        if not isinstance(parameters, Mapping):
            raise TypeError("program parameters must be a mapping")
        family = str(record.get("family"))
        if family == ADJACENT_RUN_QUOTIENT:
            expected = {"source_mode", "transform"}
            if (
                set(parameters) != expected
                or parameters.get("source_mode") != "dedupe_rc"
                or parameters.get("transform") != "identity"
            ):
                raise ValueError("invalid adjacent-run parameter record")
            value = cls.adjacent_run_quotient()
        elif family == PERIODIC_TILE_EXTRACT:
            expected = {"source_mode", "transform"}
            if (
                set(parameters) != expected
                or parameters.get("source_mode") != "periodic_tile"
                or parameters.get("transform") != "identity"
            ):
                raise ValueError("invalid periodic parameter record")
            value = cls.periodic_tile_extract()
        elif family == NEAREST_NEIGHBOR_REPLICATION:
            expected = {
                "source_mode", "background_role", "row_factor", "column_factor", "transform",
            }
            if set(parameters) != expected or parameters.get("transform") != "identity":
                raise ValueError("invalid replication parameter record")
            value = cls.nearest_neighbor_replication(
                parameters["row_factor"],
                parameters["column_factor"],
                source_mode=str(parameters["source_mode"]),
                background_role=str(parameters["background_role"]),
            )
        else:
            raise ValueError("unknown or structurally excluded program family")
        claimed = record.get("program_id")
        if claimed is not None and claimed != value.program_id:
            raise ValueError("program identity mismatch")
        return value

    def execute(self, value: Any) -> Grid:
        source = validate_grid(value)
        if self.family == ADJACENT_RUN_QUOTIENT:
            result = _dedupe_rows_columns(source)
        elif self.family == PERIODIC_TILE_EXTRACT:
            result = _primitive_period(source)
        else:
            packet = _latent_source(source, self.source_mode, self.background_role)
            result = _repeat_pixels(packet, self.row_factor, self.column_factor)
        return validate_grid(result, output=True)


Program = ShapeLayoutProgram


class PromotionStatus(str, Enum):
    STABLE = "stable"
    PROVISIONAL = "provisional"


@dataclass(frozen=True, slots=True)
class PromotionPolicy:
    allow_stable: bool = True
    allow_provisional_periodic: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.allow_stable, bool) or not isinstance(
            self.allow_provisional_periodic, bool,
        ):
            raise TypeError("promotion policy flags must be Boolean")

    @property
    def policy_id(self) -> str:
        return _content_hash({
            "schema": "komorebi.lasm_transfer.shape_layout_promotion_policy",
            "schema_version": SCHEMA_VERSION,
            "allow_stable": self.allow_stable,
            "allow_provisional_periodic": self.allow_provisional_periodic,
        })


@dataclass(frozen=True, slots=True)
class PromotionDecision:
    family: str
    status: PromotionStatus
    admissible: bool
    policy_id: str
    reason: str

    def to_record(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "status": self.status.value,
            "admissible": self.admissible,
            "policy_id": self.policy_id,
            "reason": self.reason,
        }


def classify_promotion(
    program_or_family: ShapeLayoutProgram | str,
    policy: PromotionPolicy | None = None,
) -> PromotionDecision:
    """Classify one of the closed schemas without consulting task evidence."""

    policy = policy or PromotionPolicy()
    family = (
        program_or_family.family
        if isinstance(program_or_family, ShapeLayoutProgram)
        else str(program_or_family)
    )
    if family not in _ALL_SCHEMAS:
        raise ValueError("family is not part of the safe shape/layout grammar")
    if family in STABLE_SCHEMAS:
        status = PromotionStatus.STABLE
        admissible = policy.allow_stable
        reason = "stable corpus-supported schema" if admissible else "stable schemas disabled by policy"
    else:
        status = PromotionStatus.PROVISIONAL
        admissible = policy.allow_provisional_periodic
        reason = (
            "provisional periodic schema explicitly enabled"
            if admissible
            else "provisional periodic schema requires an explicit policy flag"
        )
    return PromotionDecision(family, status, admissible, policy.policy_id, reason)


def enumerate_programs() -> tuple[ShapeLayoutProgram, ...]:
    """Return the complete finite grammar in deterministic identity order."""

    values = [
        ShapeLayoutProgram.adjacent_run_quotient(),
        ShapeLayoutProgram.periodic_tile_extract(),
    ]
    for source_mode, background_role in _SOURCE_MODES:
        for row_factor in range(1, _MAX_FACTOR + 1):
            for column_factor in range(1, _MAX_FACTOR + 1):
                if (row_factor, column_factor) == (1, 1):
                    continue
                values.append(ShapeLayoutProgram.nearest_neighbor_replication(
                    row_factor,
                    column_factor,
                    source_mode=source_mode,
                    background_role=background_role,
                ))
    return tuple(sorted(values, key=lambda item: item.program_id))


_GRAMMAR = enumerate_programs()
GRAMMAR_SIZE = len(_GRAMMAR)
GRAMMAR_CONTRACT_HASH = _content_hash({
    "schema": "komorebi.lasm_transfer.shape_layout_grammar",
    "schema_version": SCHEMA_VERSION,
    "program_ids": [program.program_id for program in _GRAMMAR],
    "unsafe_families_present": False,
})


@dataclass(frozen=True, slots=True)
class ShapeLayoutLimits:
    max_training_examples: int = 10
    max_test_examples: int = 10
    max_programs: int = GRAMMAR_SIZE

    def __post_init__(self) -> None:
        for name in ("max_training_examples", "max_test_examples", "max_programs"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")


@dataclass(frozen=True, slots=True)
class BehaviorClass:
    behavior_hash: str
    predictions: tuple[Grid, ...]
    programs: tuple[ShapeLayoutProgram, ...]

    def to_record(self) -> dict[str, Any]:
        return {
            "behavior_hash": self.behavior_hash,
            "predictions": self.predictions,
            "program_ids": [program.program_id for program in self.programs],
        }


@dataclass(frozen=True, slots=True)
class CompilationTrace:
    routed: bool
    complete: bool
    grammar_contract_hash: str
    programs_enumerated: int
    demonstration_executions: int
    execution_rejections: int
    exact_programs: int
    admitted_programs: int
    test_executions: int
    behavior_classes: int
    limit_reached: str = ""

    def to_record(self) -> dict[str, Any]:
        return {
            "routed": self.routed,
            "complete": self.complete,
            "grammar_contract_hash": self.grammar_contract_hash,
            "programs_enumerated": self.programs_enumerated,
            "demonstration_executions": self.demonstration_executions,
            "execution_rejections": self.execution_rejections,
            "exact_programs": self.exact_programs,
            "admitted_programs": self.admitted_programs,
            "test_executions": self.test_executions,
            "behavior_classes": self.behavior_classes,
            "limit_reached": self.limit_reached,
        }


@dataclass(frozen=True, slots=True)
class CompilationResult:
    exact_programs: tuple[ShapeLayoutProgram, ...]
    admitted_programs: tuple[ShapeLayoutProgram, ...]
    behaviors: tuple[BehaviorClass, ...]
    trace: CompilationTrace
    policy_id: str

    @property
    def selected_behavior(self) -> BehaviorClass | None:
        return self.behaviors[0] if len(self.behaviors) == 1 else None

    @property
    def selected_prediction(self) -> tuple[Grid, ...] | None:
        selected = self.selected_behavior
        return None if selected is None else selected.predictions

    @property
    def ambiguous(self) -> bool:
        return len(self.behaviors) > 1

    def to_record(self) -> dict[str, Any]:
        body = {
            "schema": COMPILER_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "policy_id": self.policy_id,
            "exact_programs": [program.to_record() for program in self.exact_programs],
            "admitted_program_ids": [program.program_id for program in self.admitted_programs],
            "behaviors": [behavior.to_record() for behavior in self.behaviors],
            "selected_behavior_hash": (
                self.selected_behavior.behavior_hash if self.selected_behavior else ""
            ),
            "ambiguous": self.ambiguous,
            "trace": self.trace.to_record(),
        }
        body["content_hash"] = _content_hash(body)
        return body


def _fail_closed_result(
    policy: PromotionPolicy,
    *,
    routed: bool,
    limit_reached: str,
) -> CompilationResult:
    return CompilationResult(
        (), (), (),
        CompilationTrace(
            routed=routed,
            complete=False,
            grammar_contract_hash=GRAMMAR_CONTRACT_HASH,
            programs_enumerated=0,
            demonstration_executions=0,
            execution_rejections=0,
            exact_programs=0,
            admitted_programs=0,
            test_executions=0,
            behavior_classes=0,
            limit_reached=limit_reached,
        ),
        policy.policy_id,
    )


def _examples(task: Mapping[str, Any], limits: ShapeLayoutLimits) -> tuple[
    tuple[tuple[Grid, Grid], ...], tuple[Grid, ...], str,
]:
    if not isinstance(task, Mapping):
        raise TypeError("task must be a mapping")
    training = task.get("train")
    tests = task.get("test")
    if not isinstance(training, Sequence) or isinstance(training, (str, bytes, bytearray)) or not training:
        raise ValueError("task requires a nonempty training sequence")
    if not isinstance(tests, Sequence) or isinstance(tests, (str, bytes, bytearray)) or not tests:
        raise ValueError("task requires a nonempty test sequence")
    if len(training) > limits.max_training_examples:
        return (), (), "training_example_limit"
    if len(tests) > limits.max_test_examples:
        return (), (), "test_example_limit"
    # Test mappings are accessed only through the `input` key. Any attached
    # output/label is neither inspected nor copied into a program or trace.
    demonstrations = tuple(
        (validate_grid(example["input"]), validate_grid(example["output"], output=True))
        for example in training
    )
    test_inputs = tuple(validate_grid(example["input"]) for example in tests)
    return demonstrations, test_inputs, ""


def compile_shape_layout(
    task: Mapping[str, Any],
    *,
    policy: PromotionPolicy | None = None,
    limits: ShapeLayoutLimits | None = None,
) -> CompilationResult:
    """Compile safe constructors and quotient their complete test behaviors."""

    policy = policy or PromotionPolicy()
    limits = limits or ShapeLayoutLimits()
    demonstrations, test_inputs, input_limit = _examples(task, limits)
    if input_limit:
        return _fail_closed_result(policy, routed=False, limit_reached=input_limit)
    routed = any(_shape(source) != _shape(target) for source, target in demonstrations)
    if not routed:
        return CompilationResult(
            (), (), (),
            CompilationTrace(
                routed=False,
                complete=True,
                grammar_contract_hash=GRAMMAR_CONTRACT_HASH,
                programs_enumerated=0,
                demonstration_executions=0,
                execution_rejections=0,
                exact_programs=0,
                admitted_programs=0,
                test_executions=0,
                behavior_classes=0,
            ),
            policy.policy_id,
        )
    if limits.max_programs < GRAMMAR_SIZE:
        return _fail_closed_result(policy, routed=True, limit_reached="program_enumeration_limit")

    demonstration_executions = execution_rejections = 0
    exact = []
    for program in _GRAMMAR:
        matches = True
        for source, target in demonstrations:
            demonstration_executions += 1
            try:
                observed = program.execute(source)
            except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
                execution_rejections += 1
                matches = False
                break
            if observed != target:
                matches = False
                break
        if matches:
            exact.append(program)

    admitted = [program for program in exact if classify_promotion(program, policy).admissible]
    groups: dict[str, dict[str, Any]] = {}
    surviving = []
    test_executions = 0
    for program in admitted:
        predictions = []
        valid = True
        for source in test_inputs:
            test_executions += 1
            try:
                predictions.append(program.execute(source))
            except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
                execution_rejections += 1
                valid = False
                break
        if not valid:
            continue
        behavior = tuple(predictions)
        behavior_hash = _content_hash(behavior)
        item = groups.setdefault(
            behavior_hash,
            {"predictions": behavior, "programs": []},
        )
        item["programs"].append(program)
        surviving.append(program)
    behaviors = tuple(
        BehaviorClass(
            behavior_hash,
            groups[behavior_hash]["predictions"],
            tuple(sorted(groups[behavior_hash]["programs"], key=lambda item: item.program_id)),
        )
        for behavior_hash in sorted(groups)
    )
    surviving.sort(key=lambda item: item.program_id)
    exact.sort(key=lambda item: item.program_id)
    trace = CompilationTrace(
        routed=True,
        complete=True,
        grammar_contract_hash=GRAMMAR_CONTRACT_HASH,
        programs_enumerated=GRAMMAR_SIZE,
        demonstration_executions=demonstration_executions,
        execution_rejections=execution_rejections,
        exact_programs=len(exact),
        admitted_programs=len(surviving),
        test_executions=test_executions,
        behavior_classes=len(behaviors),
    )
    return CompilationResult(
        tuple(exact), tuple(surviving), behaviors, trace, policy.policy_id,
    )


def execute_shape_layout(program: ShapeLayoutProgram | Mapping[str, Any], value: Any) -> Grid:
    parsed = (
        program
        if isinstance(program, ShapeLayoutProgram)
        else ShapeLayoutProgram.from_record(program)
    )
    return parsed.execute(value)


compile_programs = compile_shape_layout
execute = execute_shape_layout


__all__ = [
    "ADJACENT_RUN_QUOTIENT",
    "BehaviorClass",
    "COMPILER_SCHEMA",
    "CompilationResult",
    "CompilationTrace",
    "GRAMMAR_CONTRACT_HASH",
    "GRAMMAR_SIZE",
    "Grid",
    "NEAREST_NEIGHBOR_REPLICATION",
    "PERIODIC_TILE_EXTRACT",
    "PROGRAM_SCHEMA",
    "PROVISIONAL_SCHEMAS",
    "Program",
    "PromotionDecision",
    "PromotionPolicy",
    "PromotionStatus",
    "SCHEMA_VERSION",
    "STABLE_SCHEMAS",
    "ShapeLayoutLimits",
    "ShapeLayoutProgram",
    "classify_promotion",
    "compile_programs",
    "compile_shape_layout",
    "enumerate_programs",
    "execute",
    "execute_shape_layout",
    "validate_grid",
]
