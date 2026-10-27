"""Conflict-grounded, finite language growth for ARC grids.

This module is an isolated implementation seam for the Block 15 mechanism::

    conflict -> source-only probe -> Seq constructor -> refined binding

It deliberately does not modify the frozen solver portfolio.  The compiler
uses ARC training outputs only to score executable programs by exact equality.
Tokenizers, probes, and compiled programs are invoked with source grids only.
No hidden class label is represented in the API or in a compilation receipt.

The implementation is intentionally finite.  Callers provide a bounded set of
primitive programs and probes, and ``max_seq_pairs`` bounds the constructor
expansion.  The result is an executable router plus a JSON-safe certificate.
This is a mechanism for auditable language growth, not unrestricted program
invention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import itertools
import json
import math
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Protocol, Sequence, Tuple

import numpy as np

from .program_ast import CallNode, SequenceNode, TypedProgramAST


ARCGrid = np.ndarray
GridExecutor = Callable[[ARCGrid], ARCGrid]
InputTokenizer = Callable[[ARCGrid], str]


class LanguageCompilationError(ValueError):
    """Raised when the evidence cannot certify a conservative language delta."""


class LanguageExecutionError(ValueError):
    """Raised when a probe or program violates its declared runtime contract."""


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _record_hash(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _arc_grid(value: object) -> ARCGrid:
    raw = np.asarray(value)
    if raw.ndim != 2 or raw.size == 0:
        raise LanguageExecutionError("an ARC grid must be nonempty and two-dimensional")
    if raw.shape[0] > 30 or raw.shape[1] > 30:
        raise LanguageExecutionError("an ARC grid cannot exceed 30 by 30")
    if not np.issubdtype(raw.dtype, np.integer):
        if not np.all(np.equal(raw, np.floor(raw))):
            raise LanguageExecutionError("an ARC grid must contain integer colors")
    grid = np.asarray(raw, dtype=np.int16)
    if np.any(grid < 0) or np.any(grid > 9):
        raise LanguageExecutionError("an ARC grid contains a color outside 0 through 9")
    return np.ascontiguousarray(grid.copy())


def _grid_record(grid: ARCGrid) -> List[List[int]]:
    return _arc_grid(grid).astype(int).tolist()


def _grid_hash(grid: ARCGrid) -> str:
    return _record_hash(_grid_record(grid))


def _exact(left: ARCGrid, right: ARCGrid) -> bool:
    return bool(np.array_equal(_arc_grid(left), _arc_grid(right)))


class GridProgram(Protocol):
    """Structural protocol for typed, executable ARC-grid programs."""

    @property
    def program_id(self) -> str:
        ...

    @property
    def complexity(self) -> int:
        ...

    def run(self, grid: ARCGrid) -> ARCGrid:
        ...

    def to_record(self) -> Dict[str, object]:
        ...


@dataclass(frozen=True)
class PrimitiveProgram:
    """A named grid-to-grid primitive with a serializable leaf AST."""

    opcode: str
    executor: GridExecutor = field(compare=False, hash=False, repr=False)
    cost: int = 1

    def __post_init__(self) -> None:
        if not self.opcode or not isinstance(self.opcode, str):
            raise ValueError("a primitive opcode must be a nonempty string")
        if isinstance(self.cost, bool) or int(self.cost) <= 0:
            raise ValueError("a primitive cost must be positive")
        if not callable(self.executor):
            raise TypeError("a primitive executor must be callable")

    @property
    def program_id(self) -> str:
        return f"primitive:{self.opcode}"

    @property
    def complexity(self) -> int:
        return int(self.cost)

    @property
    def ast(self) -> TypedProgramAST:
        return TypedProgramAST(CallNode(self.opcode))

    def run(self, grid: ARCGrid) -> ARCGrid:
        source = _arc_grid(grid)
        try:
            output = self.executor(source.copy())
        except Exception as exc:
            raise LanguageExecutionError(
                f"primitive {self.opcode!r} failed: {type(exc).__name__}"
            ) from exc
        return _arc_grid(output)

    def to_record(self) -> Dict[str, object]:
        return self.ast.to_record()


@dataclass(frozen=True)
class SeqProgram:
    """Typed ordered composition: run ``first``, then run ``second``."""

    first: GridProgram
    second: GridProgram
    constructor_cost: int = 1

    def __post_init__(self) -> None:
        if isinstance(self.constructor_cost, bool) or int(self.constructor_cost) <= 0:
            raise ValueError("the Seq constructor cost must be positive")

    @property
    def program_id(self) -> str:
        digest = _record_hash(self.to_record())[:20]
        return f"seq:{digest}"

    @property
    def complexity(self) -> int:
        return int(self.first.complexity) + int(self.second.complexity) + int(
            self.constructor_cost
        )

    @property
    def ast(self) -> TypedProgramAST:
        first = TypedProgramAST.from_record(self.first.to_record()).root
        second = TypedProgramAST.from_record(self.second.to_record()).root
        steps = []
        steps.extend(first.steps if isinstance(first, SequenceNode) else (first,))
        steps.extend(second.steps if isinstance(second, SequenceNode) else (second,))
        return TypedProgramAST(SequenceNode(tuple(steps)))

    def run(self, grid: ARCGrid) -> ARCGrid:
        return self.second.run(self.first.run(_arc_grid(grid)))

    def to_record(self) -> Dict[str, object]:
        return self.ast.to_record()


def program_from_record(
    record: Mapping[str, object],
    primitive_registry: Mapping[str, PrimitiveProgram],
) -> GridProgram:
    """Rehydrate a canonical typed AST from a reviewed primitive registry."""

    try:
        ast = TypedProgramAST.from_record(record)
    except (KeyError, TypeError, ValueError) as exc:
        raise LanguageCompilationError("invalid canonical typed program AST") from exc

    def restore(node: object) -> GridProgram:
        if isinstance(node, CallNode):
            if node.primitive not in primitive_registry:
                raise LanguageCompilationError(
                    f"unregistered primitive opcode {node.primitive!r}"
                )
            primitive = primitive_registry[node.primitive]
            if primitive.ast.root != node:
                raise LanguageCompilationError(
                    "primitive registry signature does not match the AST"
                )
            return primitive
        if isinstance(node, SequenceNode):
            restored = tuple(restore(step) for step in node.steps)
            program = restored[0]
            for following in restored[1:]:
                program = SeqProgram(program, following)
            return program
        raise LanguageCompilationError(
            "the conflict compiler supports call and nonempty sequence ASTs"
        )

    program = restore(ast.root)
    if program.to_record() != dict(record):
        raise LanguageCompilationError("the typed AST has inconsistent derived metadata")
    return program


@dataclass(frozen=True)
class ScalarProbe:
    """A typed scalar diagnostic computed from an input grid only."""

    probe_id: str
    executor: Callable[[ARCGrid], float] = field(compare=False, hash=False, repr=False)
    cost: int = 1

    def __post_init__(self) -> None:
        if not self.probe_id or not isinstance(self.probe_id, str):
            raise ValueError("a probe ID must be a nonempty string")
        if isinstance(self.cost, bool) or int(self.cost) <= 0:
            raise ValueError("a probe cost must be positive")
        if not callable(self.executor):
            raise TypeError("a probe executor must be callable")

    def evaluate(self, grid: ARCGrid) -> float:
        source = _arc_grid(grid)
        try:
            response = float(self.executor(source.copy()))
        except Exception as exc:
            raise LanguageExecutionError(
                f"probe {self.probe_id!r} failed: {type(exc).__name__}"
            ) from exc
        if not math.isfinite(response):
            raise LanguageExecutionError(f"probe {self.probe_id!r} returned a nonfinite value")
        return response

    def to_record(self) -> Dict[str, object]:
        return {
            "schema": "sric.arc.scalar-probe.v1",
            "probe_id": self.probe_id,
            "input_type": "arc_grid",
            "output_type": "finite_scalar",
            "runtime_arguments": ["source_grid"],
            "target_access": False,
            "cost": int(self.cost),
        }


@dataclass(frozen=True)
class TrainingCase:
    """One ARC input-output witness.  There is intentionally no label field."""

    case_id: str
    source: ARCGrid = field(compare=False, hash=False, repr=False)
    target: ARCGrid = field(compare=False, hash=False, repr=False)

    def __post_init__(self) -> None:
        if not self.case_id or not isinstance(self.case_id, str):
            raise ValueError("a case ID must be a nonempty string")
        object.__setattr__(self, "source", _arc_grid(self.source))
        object.__setattr__(self, "target", _arc_grid(self.target))


@dataclass(frozen=True)
class LedgerEntry:
    case_id: str
    source_hash: str
    target_hash: str
    base_token: str
    inherited_acceptable: Tuple[str, ...]
    expanded_acceptable: Tuple[str, ...]
    inherited_execution_failures: Tuple[str, ...]
    expanded_execution_failures: Tuple[str, ...]

    def to_record(self) -> Dict[str, object]:
        return {
            "source_hash": self.source_hash,
            "target_hash": self.target_hash,
            "base_token": self.base_token,
            "inherited_acceptable": list(self.inherited_acceptable),
            "expanded_acceptable": list(self.expanded_acceptable),
            "inherited_execution_failures": list(self.inherited_execution_failures),
            "expanded_execution_failures": list(self.expanded_execution_failures),
        }


@dataclass(frozen=True)
class ConflictLedger:
    entries: Tuple[LedgerEntry, ...]
    inherited_language_hash: str
    expanded_language_hash: str

    @property
    def ledger_hash(self) -> str:
        return _record_hash(self.to_record())

    def to_record(self) -> Dict[str, object]:
        return {
            "schema": "sric.arc.conflict-ledger.v1",
            "evidence_boundary": {
                "tokenizer_runtime_arguments": ["source_grid"],
                "program_runtime_arguments": ["source_grid"],
                "development_feedback": "exact_program_output_equals_arc_training_target",
                "hidden_class_labels_used": False,
                "raw_grids_stored": False,
                "case_ids_stored": False,
            },
            "inherited_language_hash": self.inherited_language_hash,
            "expanded_language_hash": self.expanded_language_hash,
            "entries": [entry.to_record() for entry in self.entries],
        }


@dataclass(frozen=True)
class ConflictCertificate:
    base_token: str
    case_ids: Tuple[str, ...]
    conflict_kind: str
    inherited_common: Tuple[str, ...]
    expanded_common: Tuple[str, ...]
    inherited_covered_cases: int
    expanded_covered_cases: int
    ledger_hash: str

    def to_record(self) -> Dict[str, object]:
        return {
            "schema": "sric.arc.conflict-certificate.v1",
            "base_token": self.base_token,
            "witness_count": len(self.case_ids),
            "conflict_kind": self.conflict_kind,
            "inherited_common_acceptable_programs": list(self.inherited_common),
            "expanded_common_acceptable_programs": list(self.expanded_common),
            "inherited_covered_cases": int(self.inherited_covered_cases),
            "expanded_covered_cases": int(self.expanded_covered_cases),
            "required_conditions": {
                "at_least_two_witnesses": len(self.case_ids) >= 2,
                "no_single_inherited_program_resolves_cell": not self.inherited_common,
                "every_witness_correctable_in_expanded_language": self.expanded_covered_cases
                == len(self.case_ids),
                "no_single_expanded_program_resolves_cell": not self.expanded_common,
            },
            "ledger_hash": self.ledger_hash,
        }


def _language_map(programs: Sequence[GridProgram]) -> Dict[str, GridProgram]:
    output: Dict[str, GridProgram] = {}
    records: Dict[str, str] = {}
    for program in programs:
        program_id = str(program.program_id)
        record = _canonical_json(
            {
                "program_ast": program.to_record(),
                "search_complexity": int(program.complexity),
            }
        )
        if program_id in records and records[program_id] != record:
            raise LanguageCompilationError(f"program ID collision for {program_id!r}")
        output.setdefault(program_id, program)
        records.setdefault(program_id, record)
    return dict(sorted(output.items()))


def _language_hash(programs: Mapping[str, GridProgram]) -> str:
    return _record_hash([program.to_record() for _, program in sorted(programs.items())])


def expand_seq_language(
    atoms: Sequence[GridProgram],
    *,
    max_pairs: int = 256,
    allow_self_composition: bool = False,
) -> Tuple[SeqProgram, ...]:
    """Enumerate a deterministic, bounded ordered-pair constructor language."""

    if isinstance(max_pairs, bool) or int(max_pairs) < 0:
        raise ValueError("max_pairs must be a nonnegative integer")
    ordered = list(_language_map(atoms).values())
    output: List[SeqProgram] = []
    for first, second in itertools.product(ordered, repeat=2):
        if not allow_self_composition and first.program_id == second.program_id:
            continue
        output.append(SeqProgram(first, second))
        if len(output) >= int(max_pairs):
            break
    return tuple(output)


def _acceptable_programs(
    case: TrainingCase,
    programs: Mapping[str, GridProgram],
) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    acceptable: List[str] = []
    failed: List[str] = []
    for program_id, program in sorted(programs.items()):
        try:
            prediction = program.run(case.source)
        except LanguageExecutionError:
            failed.append(program_id)
            continue
        if _exact(prediction, case.target):
            acceptable.append(program_id)
    return tuple(acceptable), tuple(failed)


def build_conflict_ledger(
    cases: Sequence[TrainingCase],
    tokenizer: InputTokenizer,
    inherited_programs: Sequence[GridProgram],
    expanded_programs: Sequence[GridProgram],
) -> ConflictLedger:
    """Evaluate a finite language without exposing targets to tokenization."""

    if not cases:
        raise LanguageCompilationError("a conflict ledger requires training cases")
    inherited = _language_map(inherited_programs)
    expanded = _language_map(expanded_programs)
    if not inherited:
        raise LanguageCompilationError("the inherited language cannot be empty")
    if not set(inherited).issubset(expanded):
        raise LanguageCompilationError(
            "the expanded language must conservatively embed the inherited language"
        )
    rows: List[LedgerEntry] = []
    seen_case_ids: set[str] = set()
    ordered_cases = sorted(
        cases,
        key=lambda case: (_grid_hash(case.source), _grid_hash(case.target), case.case_id),
    )
    for case in ordered_cases:
        if case.case_id in seen_case_ids:
            raise LanguageCompilationError(f"duplicate case ID {case.case_id!r}")
        seen_case_ids.add(case.case_id)
        try:
            base_token = tokenizer(case.source.copy())
        except Exception as exc:
            raise LanguageCompilationError(
                f"the source-only tokenizer failed on {case.case_id!r}: {type(exc).__name__}"
            ) from exc
        if not isinstance(base_token, str) or not base_token:
            raise LanguageCompilationError("the source-only tokenizer must return a nonempty string")
        inherited_ok, inherited_failed = _acceptable_programs(case, inherited)
        expanded_ok, expanded_failed = _acceptable_programs(case, expanded)
        rows.append(
            LedgerEntry(
                case_id=case.case_id,
                source_hash=_grid_hash(case.source),
                target_hash=_grid_hash(case.target),
                base_token=base_token,
                inherited_acceptable=inherited_ok,
                expanded_acceptable=expanded_ok,
                inherited_execution_failures=inherited_failed,
                expanded_execution_failures=expanded_failed,
            )
        )
    return ConflictLedger(
        entries=tuple(rows),
        inherited_language_hash=_language_hash(inherited),
        expanded_language_hash=_language_hash(expanded),
    )


def _intersection(values: Iterable[Sequence[str]]) -> Tuple[str, ...]:
    rows = [set(value) for value in values]
    if not rows:
        return ()
    return tuple(sorted(set.intersection(*rows)))


def certify_conflict(
    ledger: ConflictLedger,
    *,
    base_token: Optional[str] = None,
) -> ConflictCertificate:
    """Certify a same-token conflict that needs both routing and language growth."""

    tokens = sorted({entry.base_token for entry in ledger.entries})
    if base_token is not None:
        tokens = [base_token]
    for token in tokens:
        entries = tuple(entry for entry in ledger.entries if entry.base_token == token)
        if len(entries) < 2:
            continue
        inherited_common = _intersection(entry.inherited_acceptable for entry in entries)
        expanded_common = _intersection(entry.expanded_acceptable for entry in entries)
        inherited_covered = sum(bool(entry.inherited_acceptable) for entry in entries)
        expanded_covered = sum(bool(entry.expanded_acceptable) for entry in entries)
        if inherited_common:
            continue
        if expanded_covered != len(entries):
            continue
        if expanded_common:
            continue
        if inherited_covered == len(entries):
            kind = "representation_alias"
        elif inherited_covered == 0:
            kind = "coupled_representation_and_grammar"
        else:
            kind = "mixed_representation_and_grammar"
        return ConflictCertificate(
            base_token=token,
            case_ids=tuple(sorted(entry.case_id for entry in entries)),
            conflict_kind=kind,
            inherited_common=inherited_common,
            expanded_common=expanded_common,
            inherited_covered_cases=inherited_covered,
            expanded_covered_cases=expanded_covered,
            ledger_hash=ledger.ledger_hash,
        )
    requested = "any token" if base_token is None else repr(base_token)
    raise LanguageCompilationError(
        f"no certifiable coupled conflict exists for {requested}"
    )


@dataclass(frozen=True)
class CoupledLanguageCertificate:
    conflict: ConflictCertificate
    probe_record: Dict[str, object]
    threshold: float
    lower_token: str
    upper_token: str
    lower_program_id: str
    upper_program_id: str
    lower_program_ast: Dict[str, object]
    upper_program_ast: Dict[str, object]
    lower_support: int
    upper_support: int
    minimum_probe_margin: float
    shuffled_binding_exact_cases: int
    development_case_count: int
    inherited_language_hash: str
    expanded_language_hash: str
    searched_probe_count: int
    searched_seq_count: int

    @property
    def certificate_id(self) -> str:
        return _record_hash(self.to_record())

    def to_record(self) -> Dict[str, object]:
        return {
            "schema": "sric.arc.coupled-language-certificate.v1",
            "claim_scope": "finite_conflict_grounded_language_growth",
            "conflict": self.conflict.to_record(),
            "diagnostic_refinement": {
                "base_token": self.conflict.base_token,
                "probe": self.probe_record,
                "threshold": float(self.threshold),
                "lower_token": self.lower_token,
                "upper_token": self.upper_token,
                "projection_to_parent": {
                    self.lower_token: self.conflict.base_token,
                    self.upper_token: self.conflict.base_token,
                },
                "minimum_probe_margin": float(self.minimum_probe_margin),
            },
            "constructor": {
                "name": "Seq",
                "input_type": "arc_grid",
                "intermediate_type": "arc_grid",
                "output_type": "arc_grid",
                "searched_seq_count": int(self.searched_seq_count),
                "at_least_one_selected_binding_uses_seq": any(
                    isinstance(ast.get("root"), Mapping)
                    and ast["root"].get("kind") == "sequence"
                    for ast in (self.lower_program_ast, self.upper_program_ast)
                ),
            },
            "bindings": [
                {
                    "refined_token": self.lower_token,
                    "program_id": self.lower_program_id,
                    "program_ast": self.lower_program_ast,
                    "development_support": int(self.lower_support),
                },
                {
                    "refined_token": self.upper_token,
                    "program_id": self.upper_program_id,
                    "program_ast": self.upper_program_ast,
                    "development_support": int(self.upper_support),
                },
            ],
            "controls": {
                "grammar_only_resolves_conflict": bool(self.conflict.expanded_common),
                "taxonomy_only_resolves_conflict": False,
                "shuffled_binding_exact_cases": int(self.shuffled_binding_exact_cases),
                "full_binding_exact_cases": int(self.development_case_count),
                "binding_is_nontrivial": self.shuffled_binding_exact_cases
                < self.development_case_count,
                "parent_language_conservatively_embedded": True,
            },
            "search_receipt": {
                "searched_probe_count": int(self.searched_probe_count),
                "inherited_language_hash": self.inherited_language_hash,
                "expanded_language_hash": self.expanded_language_hash,
                "development_case_count": int(self.development_case_count),
                "selection_feedback": "exact_program_output_equals_arc_training_target",
                "hidden_class_labels_used": False,
            },
            "runtime_boundary": {
                "tokenizer_arguments": ["source_grid"],
                "probe_arguments": ["source_grid"],
                "program_arguments": ["source_grid"],
                "target_available_at_runtime": False,
            },
        }


@dataclass
class CompiledLanguageDelta:
    """Executable refined binding with an unchanged parent fallback."""

    certificate: CoupledLanguageCertificate
    ledger: ConflictLedger
    tokenizer: InputTokenizer = field(repr=False)
    probe: ScalarProbe = field(repr=False)
    programs: Dict[str, GridProgram] = field(repr=False)
    parent_fallback: Optional[GridProgram] = field(default=None, repr=False)

    def refined_token(self, grid: ARCGrid) -> Optional[str]:
        source = _arc_grid(grid)
        try:
            parent_token = self.tokenizer(source.copy())
        except Exception as exc:
            raise LanguageExecutionError(
                f"the source-only tokenizer failed: {type(exc).__name__}"
            ) from exc
        if parent_token != self.certificate.conflict.base_token:
            return None
        response = self.probe.evaluate(source)
        if response <= self.certificate.threshold:
            return self.certificate.lower_token
        return self.certificate.upper_token

    def selected_program(self, grid: ARCGrid) -> GridProgram:
        token = self.refined_token(grid)
        if token is None:
            if self.parent_fallback is None:
                raise LanguageExecutionError(
                    "the input lies outside the refined token and no parent fallback is registered"
                )
            return self.parent_fallback
        program_id = (
            self.certificate.lower_program_id
            if token == self.certificate.lower_token
            else self.certificate.upper_program_id
        )
        return self.programs[program_id]

    def run(self, grid: ARCGrid) -> ARCGrid:
        source = _arc_grid(grid)
        return self.selected_program(source).run(source)

    def to_record(self) -> Dict[str, object]:
        return {
            "schema": "sric.arc.compiled-language-delta.v1",
            "certificate_id": self.certificate.certificate_id,
            "certificate": self.certificate.to_record(),
            "ledger_hash": self.ledger.ledger_hash,
            "parent_fallback": (
                None if self.parent_fallback is None else self.parent_fallback.to_record()
            ),
        }


@dataclass
class LanguageDeltaCandidate:
    """A RuleCandidate-compatible adapter without importing the frozen entry."""

    name: str
    grids: List[ARCGrid]
    train_error: int
    complexity: int
    family: str
    train_grids: Tuple[ARCGrid, ...]
    metadata: Dict[str, object]


def _thresholds(responses: Sequence[float]) -> Tuple[float, ...]:
    unique = sorted(set(float(response) for response in responses))
    return tuple((left + right) / 2.0 for left, right in zip(unique, unique[1:]))


def _taxonomy_only_solution_exists(
    entries: Sequence[LedgerEntry],
    cases_by_id: Mapping[str, TrainingCase],
    probes: Sequence[ScalarProbe],
    *,
    minimum_branch_support: int,
) -> bool:
    for probe in probes:
        responses = {entry.case_id: probe.evaluate(cases_by_id[entry.case_id].source) for entry in entries}
        for threshold in _thresholds(list(responses.values())):
            lower = [entry for entry in entries if responses[entry.case_id] <= threshold]
            upper = [entry for entry in entries if responses[entry.case_id] > threshold]
            if min(len(lower), len(upper)) < minimum_branch_support:
                continue
            if _intersection(entry.inherited_acceptable for entry in lower) and _intersection(
                entry.inherited_acceptable for entry in upper
            ):
                return True
    return False


def compile_coupled_language(
    cases: Sequence[TrainingCase],
    tokenizer: InputTokenizer,
    inherited_programs: Sequence[GridProgram],
    constructor_atoms: Sequence[GridProgram],
    probes: Sequence[ScalarProbe],
    *,
    base_token: Optional[str] = None,
    max_seq_pairs: int = 256,
    minimum_branch_support: int = 2,
    parent_fallback: Optional[GridProgram] = None,
) -> CompiledLanguageDelta:
    """Compile one finite, coupled diagnostic and grammar refinement.

    A successful result certifies all of the following on the supplied
    development cases:

    * one coarse input-derived token has no universally acceptable program;
    * adding ``Seq`` makes every witness individually correctable;
    * no single expanded program resolves the token, so grammar alone fails;
    * no supplied probe can route inherited programs alone, so taxonomy alone
      fails; and
    * one source-only scalar split binds each cell to an exact program, with at
      least one binding using ``Seq`` and a nontrivial shuffled-binding control.
    """

    if isinstance(minimum_branch_support, bool) or int(minimum_branch_support) < 1:
        raise ValueError("minimum_branch_support must be a positive integer")
    if len(probes) == 0:
        raise LanguageCompilationError("the finite probe family cannot be empty")
    probe_ids = [probe.probe_id for probe in probes]
    if len(set(probe_ids)) != len(probe_ids):
        raise LanguageCompilationError("probe IDs must be unique")
    inherited = _language_map(inherited_programs)
    seq_programs = expand_seq_language(
        constructor_atoms,
        max_pairs=max_seq_pairs,
        allow_self_composition=False,
    )
    expanded = _language_map(tuple(inherited.values()) + seq_programs)
    ledger = build_conflict_ledger(cases, tokenizer, tuple(inherited.values()), tuple(expanded.values()))
    conflict = certify_conflict(ledger, base_token=base_token)
    entries = tuple(entry for entry in ledger.entries if entry.base_token == conflict.base_token)
    case_ids = {entry.case_id for entry in entries}
    cases_by_id = {case.case_id: case for case in cases if case.case_id in case_ids}
    if set(cases_by_id) != case_ids:
        raise LanguageCompilationError("the conflict ledger cannot be joined to its cases")
    if _taxonomy_only_solution_exists(
        entries,
        cases_by_id,
        probes,
        minimum_branch_support=int(minimum_branch_support),
    ):
        raise LanguageCompilationError(
            "the supplied probes can solve this conflict without constructor growth"
        )

    candidates: List[
        Tuple[
            Tuple[object, ...],
            ScalarProbe,
            float,
            Tuple[LedgerEntry, ...],
            Tuple[LedgerEntry, ...],
            str,
            str,
            float,
            int,
        ]
    ] = []
    for probe in sorted(probes, key=lambda item: item.probe_id):
        responses = {
            entry.case_id: probe.evaluate(cases_by_id[entry.case_id].source)
            for entry in entries
        }
        for threshold in _thresholds(list(responses.values())):
            lower = tuple(entry for entry in entries if responses[entry.case_id] <= threshold)
            upper = tuple(entry for entry in entries if responses[entry.case_id] > threshold)
            if min(len(lower), len(upper)) < int(minimum_branch_support):
                continue
            lower_common = _intersection(entry.expanded_acceptable for entry in lower)
            upper_common = _intersection(entry.expanded_acceptable for entry in upper)
            if not lower_common or not upper_common:
                continue
            margin = min(abs(response - threshold) for response in responses.values())
            for lower_program_id, upper_program_id in itertools.product(
                lower_common, upper_common
            ):
                lower_program = expanded[lower_program_id]
                upper_program = expanded[upper_program_id]
                if not isinstance(lower_program, SeqProgram) and not isinstance(
                    upper_program, SeqProgram
                ):
                    continue
                shuffled_exact = sum(
                    upper_program_id in entry.expanded_acceptable for entry in lower
                ) + sum(lower_program_id in entry.expanded_acceptable for entry in upper)
                if shuffled_exact == len(entries):
                    continue
                total_complexity = (
                    int(probe.cost)
                    + int(lower_program.complexity)
                    + int(upper_program.complexity)
                )
                key: Tuple[object, ...] = (
                    total_complexity,
                    -float(margin),
                    probe.probe_id,
                    float(threshold),
                    lower_program_id,
                    upper_program_id,
                )
                candidates.append(
                    (
                        key,
                        probe,
                        float(threshold),
                        lower,
                        upper,
                        lower_program_id,
                        upper_program_id,
                        float(margin),
                        int(shuffled_exact),
                    )
                )
    if not candidates:
        raise LanguageCompilationError(
            "no supplied source-only probe and Seq binding resolves the certified conflict"
        )
    (
        _,
        probe,
        threshold,
        lower,
        upper,
        lower_program_id,
        upper_program_id,
        margin,
        shuffled_exact,
    ) = min(candidates, key=lambda row: row[0])
    lower_token = f"{conflict.base_token}|{probe.probe_id}:low"
    upper_token = f"{conflict.base_token}|{probe.probe_id}:high"
    certificate = CoupledLanguageCertificate(
        conflict=conflict,
        probe_record=probe.to_record(),
        threshold=threshold,
        lower_token=lower_token,
        upper_token=upper_token,
        lower_program_id=lower_program_id,
        upper_program_id=upper_program_id,
        lower_program_ast=expanded[lower_program_id].to_record(),
        upper_program_ast=expanded[upper_program_id].to_record(),
        lower_support=len(lower),
        upper_support=len(upper),
        minimum_probe_margin=margin,
        shuffled_binding_exact_cases=shuffled_exact,
        development_case_count=len(entries),
        inherited_language_hash=ledger.inherited_language_hash,
        expanded_language_hash=ledger.expanded_language_hash,
        searched_probe_count=len(probes),
        searched_seq_count=len(seq_programs),
    )
    return CompiledLanguageDelta(
        certificate=certificate,
        ledger=ledger,
        tokenizer=tokenizer,
        probe=probe,
        programs=expanded,
        parent_fallback=parent_fallback,
    )


def materialize_language_delta_candidate(
    delta: CompiledLanguageDelta,
    training_cases: Sequence[TrainingCase],
    test_inputs: Sequence[ARCGrid],
) -> LanguageDeltaCandidate:
    """Adapt a compiled delta to the structural contract used by RuleCandidate."""

    train_predictions = tuple(delta.run(case.source) for case in training_cases)
    if not all(
        _exact(prediction, case.target)
        for prediction, case in zip(train_predictions, training_cases)
    ):
        raise LanguageCompilationError(
            "the compiled language delta does not reproduce every training target"
        )
    test_predictions = [delta.run(grid) for grid in test_inputs]
    selected_complexity = max(
        delta.programs[delta.certificate.lower_program_id].complexity,
        delta.programs[delta.certificate.upper_program_id].complexity,
    )
    metadata = {
        "schema": "sric-arc-conflict-compiled-candidate-v1",
        "compiler_block": "conflict_grounded_language_growth",
        "language_delta": delta.to_record(),
        "provenance_kind": "test_input_transform",
        "test_input_grounded": True,
        "permutation_invariant": True,
        "admissible": True,
        "exact_demonstration_contract": True,
        "partial_program": False,
        "hidden_class_labels_used": False,
    }
    return LanguageDeltaCandidate(
        name=f"conflict_language:{delta.certificate.certificate_id[:16]}",
        grids=test_predictions,
        train_error=0,
        complexity=int(delta.probe.cost) + int(selected_complexity),
        family="sric_conflict_compiled_language",
        train_grids=train_predictions,
        metadata=metadata,
    )


__all__ = [
    "CompiledLanguageDelta",
    "ConflictCertificate",
    "ConflictLedger",
    "GridProgram",
    "LanguageCompilationError",
    "LanguageDeltaCandidate",
    "LanguageExecutionError",
    "PrimitiveProgram",
    "ScalarProbe",
    "SeqProgram",
    "TrainingCase",
    "build_conflict_ledger",
    "certify_conflict",
    "compile_coupled_language",
    "expand_seq_language",
    "materialize_language_delta_candidate",
    "program_from_record",
]
