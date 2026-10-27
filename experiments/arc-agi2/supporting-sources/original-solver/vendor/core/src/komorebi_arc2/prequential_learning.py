"""Prequential macro discovery and promotion for the ARC solver.

The online solver remains read only.  This controller owns the sequence order,
opens a prediction receipt, supplies an immutable learner snapshot to the
solver, and accepts a label only after the prediction state has been sealed.
A program becomes reusable only after it was proposed before reveal and solved
at least two distinct earlier task sources exactly.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

from . import entry
from .learning_bank import (
    AdmissionEvidence,
    AdmissionProposal,
    BankMode,
    MacroBank,
    ProgramDiscoveryCertificate,
    content_hash_text,
)
from .macro_runtime import LearnerSnapshot, task_source_content_hash
from .program_ast import (
    TypedProgramAST,
    TypedProgramInterpreter,
    ast_from_primitive_names,
    interpreter_from_legacy_ops,
)

PREQUENTIAL_STATE_SCHEMA = "komorebi.arc2.prequential_learner_state"
PREQUENTIAL_STATE_VERSION = 2

DEFAULT_MACRO_PRIMITIVES = (
    "rot90",
    "rot180",
    "rot270",
    "flip_h",
    "flip_v",
    "transpose",
    "anti_transpose",
    "crop_bbox",
    "remove_uniform_border",
    "fill_holes",
    "extend_lines_h",
    "extend_lines_v",
    "extend_lines_both",
    "sym_lr",
    "sym_rl",
    "sym_tb",
    "sym_bt",
    "upscale_2",
    "downscale_2_majority",
)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash_record(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def legacy_macro_interpreter() -> TypedProgramInterpreter:
    return interpreter_from_legacy_ops(
        entry.PRIMS,
        grid_normalizer=entry.sanitize_grid,
    )


def legacy_macro_interpreter_contract() -> str:
    """Bind macro admissions to the solver build and primitive implementation."""

    source_path = Path(entry.__file__).resolve()
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    primitive_records = [
        {"name": op.name, "kind": op.kind, "cost": int(op.cost)}
        for op in sorted(entry.PRIMS, key=lambda item: item.name)
    ]
    return _hash_record(
        {
            "schema": "komorebi.arc2.legacy_macro_interpreter_contract",
            "schema_version": 1,
            "solver_version": entry.SOLVER_VERSION,
            "entry_source_sha256": source_hash,
            "primitives": primitive_records,
        }
    )


@dataclass(frozen=True)
class MacroMinerConfig:
    primitive_names: tuple[str, ...] = DEFAULT_MACRO_PRIMITIVES
    maximum_depth: int = 3
    maximum_evaluations: int = 10000
    maximum_exact: int = 64

    def __post_init__(self) -> None:
        if not self.primitive_names or len(set(self.primitive_names)) != len(self.primitive_names):
            raise ValueError("macro primitive names must be nonempty and unique")
        if self.maximum_depth < 1:
            raise ValueError("maximum macro depth must be positive")
        if self.maximum_evaluations < 1 or self.maximum_exact < 1:
            raise ValueError("macro search caps must be positive")


@dataclass(frozen=True)
class MacroMiningResult:
    programs: tuple[TypedProgramAST, ...]
    evaluated_programs: int
    exact_programs: int
    exhausted: bool


@dataclass(frozen=True)
class PrequentialLearnerState:
    """Immutable persistent state between fully revealed task positions."""

    bank: MacroBank
    catalog: tuple[TypedProgramAST, ...] = ()
    schema_version: int = PREQUENTIAL_STATE_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != PREQUENTIAL_STATE_VERSION:
            raise ValueError(f"unsupported prequential learner version {self.schema_version}")
        if self.bank.pending is not None:
            raise ValueError("persistent learner state cannot contain a pending query")
        hashes = tuple(program.content_hash() for program in self.catalog)
        if hashes != tuple(sorted(set(hashes))):
            raise ValueError("learner program catalog must be unique and hash sorted")

    @classmethod
    def empty(cls, *, mode: BankMode = BankMode.LEARNING) -> "PrequentialLearnerState":
        return cls(bank=MacroBank.empty(mode=mode))

    def to_record(self) -> dict[str, object]:
        return {
            "schema": PREQUENTIAL_STATE_SCHEMA,
            "schema_version": self.schema_version,
            "bank": self.bank.to_record(),
            "catalog": [program.to_record() for program in self.catalog],
        }

    def to_json(self) -> str:
        return _canonical_json(self.to_record())

    def content_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_record(cls, raw: object) -> "PrequentialLearnerState":
        if not isinstance(raw, Mapping):
            raise TypeError("prequential learner state must be a mapping")
        expected = {"schema", "schema_version", "bank", "catalog"}
        if set(raw) != expected:
            raise ValueError("prequential learner state fields do not match the schema")
        if raw["schema"] != PREQUENTIAL_STATE_SCHEMA:
            raise ValueError(f"unknown learner-state schema {raw['schema']!r}")
        raw_catalog = raw["catalog"]
        if not isinstance(raw_catalog, list):
            raise TypeError("learner catalog must be a list")
        return cls(
            bank=MacroBank.from_record(raw["bank"]),
            catalog=tuple(TypedProgramAST.from_record(item) for item in raw_catalog),
            schema_version=int(raw["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> "PrequentialLearnerState":
        return cls.from_record(json.loads(payload))


@dataclass(frozen=True)
class PendingPrequentialQuery:
    prior_state_hash: str
    opened_bank: MacroBank
    snapshot: LearnerSnapshot
    programs: tuple[TypedProgramAST, ...]
    catalog_after_mining: tuple[TypedProgramAST, ...]
    train: tuple[tuple[np.ndarray, np.ndarray], ...]
    tests: tuple[np.ndarray, ...]
    mining: MacroMiningResult
    discovery_certificates: tuple[ProgramDiscoveryCertificate, ...]


@dataclass(frozen=True)
class PrequentialUpdate:
    state: PrequentialLearnerState
    exact_program_hashes: tuple[str, ...]
    admitted_macro_hashes: tuple[str, ...]
    rejected_macro_reasons: tuple[str, ...]


def _program_tuple(program: TypedProgramAST) -> tuple[entry.Op, ...]:
    record = program.to_record()["root"]
    # The miner emits only calls and flat sequences generated from legacy names.
    if not isinstance(record, Mapping):
        raise TypeError("program root must be a mapping")
    kind = record.get("kind")
    if kind == "call":
        names = (str(record["primitive"]),)
    elif kind == "sequence":
        raw_steps = record.get("steps")
        if not isinstance(raw_steps, list):
            raise TypeError("sequence steps must be a list")
        names = tuple(str(step["primitive"]) for step in raw_steps if isinstance(step, Mapping))
    elif kind == "identity":
        names = ()
    else:
        raise ValueError(f"unsupported mined program root {kind!r}")
    operations = {operation.name: operation for operation in entry.PRIMS}
    return tuple(operations[name] for name in names)


def mine_exact_demo_programs(
    train: Sequence[tuple[np.ndarray, np.ndarray]],
    *,
    config: MacroMinerConfig = MacroMinerConfig(),
) -> MacroMiningResult:
    """Search a small portable depth-three grammar using demonstrations only."""

    operations = {operation.name: operation for operation in entry.PRIMS}
    missing = [name for name in config.primitive_names if name not in operations]
    if missing:
        raise ValueError(f"unknown macro-miner primitives: {missing}")
    active = tuple(operations[name] for name in config.primitive_names)
    exact_programs: dict[str, TypedProgramAST] = {}
    evaluated = 0
    exhausted = True
    for depth in range(1, config.maximum_depth + 1):
        for program_ops in itertools.product(active, repeat=depth):
            if evaluated >= config.maximum_evaluations:
                exhausted = False
                break
            if not entry.valid_program(program_ops):
                continue
            evaluated += 1
            predictions = tuple(entry.apply_program(source, program_ops) for source, _ in train)
            if not all(
                entry.exact(prediction, target)
                for prediction, (_, target) in zip(predictions, train)
            ):
                continue
            if train and all(
                entry.exact(prediction, source)
                for prediction, (source, _) in zip(predictions, train)
            ):
                continue
            ast = ast_from_primitive_names(tuple(operation.name for operation in program_ops))
            exact_programs[ast.content_hash()] = ast
        if not exhausted:
            break
    ordered = sorted(
        exact_programs.values(),
        key=lambda program: (
            len(_program_tuple(program)),
            entry.program_cost(_program_tuple(program)),
            program.content_hash(),
        ),
    )[: config.maximum_exact]
    return MacroMiningResult(
        programs=tuple(ordered),
        evaluated_programs=evaluated,
        exact_programs=len(exact_programs),
        exhausted=exhausted,
    )


def macro_miner_contract(config: MacroMinerConfig) -> str:
    """Hash the finite search grammar and its deterministic selection policy."""

    return _hash_record(
        {
            "schema": "komorebi.arc2.macro_miner_contract",
            "schema_version": 1,
            "primitive_names": list(config.primitive_names),
            "maximum_depth": config.maximum_depth,
            "maximum_evaluations": config.maximum_evaluations,
            "maximum_exact": config.maximum_exact,
            "selection": (
                "depth_then_program_cost_then_program_hash; "
                "fold-first canonical identity"
            ),
        }
    )


def _demo_group_hash(source: np.ndarray, target: np.ndarray) -> str:
    return _hash_record(
        {
            "source": entry.grid_to_list(source),
            "target": entry.grid_to_list(target),
        }
    )


def _build_discovery_certificates(
    programs: Sequence[TypedProgramAST],
    train: Sequence[tuple[np.ndarray, np.ndarray]],
    *,
    config: MacroMinerConfig,
    source_content_hash: str,
    interpreter_contract: str,
) -> tuple[ProgramDiscoveryCertificate, ...]:
    """Re-mine every distinct nonidentity fold before the query is opened."""

    interpreter = legacy_macro_interpreter()
    nonidentity_groups: dict[
        str, list[tuple[np.ndarray, np.ndarray]]
    ] = {}
    for source, target in train:
        if entry.exact(source, target):
            continue
        group_hash = _demo_group_hash(source, target)
        nonidentity_groups.setdefault(group_hash, []).append((source, target))
    ordered_groups = tuple(sorted(nonidentity_groups))

    fold_selected: dict[str, str] = {}
    for group_hash in ordered_groups:
        remaining = tuple(
            (source, target)
            for source, target in train
            if _demo_group_hash(source, target) != group_hash
        )
        if not remaining:
            fold_selected[group_hash] = _hash_record(
                {"status": "no_remaining_fold", "group_hash": group_hash}
            )
            continue
        fold = mine_exact_demo_programs(remaining, config=config)
        fold_selected[group_hash] = (
            fold.programs[0].content_hash()
            if fold.programs
            else _hash_record(
                {"status": "no_exact_fold_program", "group_hash": group_hash}
            )
        )

    certificates: list[ProgramDiscoveryCertificate] = []
    for program in sorted(programs, key=lambda item: item.content_hash()):
        program_hash = program.content_hash()
        full_exact = all(
            entry.exact(
                np.asarray(interpreter.execute(program, source), dtype=np.int16),
                target,
            )
            for source, target in train
        )
        held_exact = all(
            all(
                entry.exact(
                    np.asarray(
                        interpreter.execute(program, source), dtype=np.int16
                    ),
                    target,
                )
                for source, target in nonidentity_groups[group_hash]
            )
            for group_hash in ordered_groups
        )
        selections = tuple(
            fold_selected[group_hash] for group_hash in ordered_groups
        )
        loo_exact = bool(
            full_exact
            and held_exact
            and len(ordered_groups) >= 2
            and all(selected == program_hash for selected in selections)
        )
        certificates.append(
            ProgramDiscoveryCertificate(
                program_hash=program_hash,
                source_content_hash=source_content_hash,
                interpreter_contract=interpreter_contract,
                miner_contract=macro_miner_contract(config),
                distinct_nonidentity_group_hashes=ordered_groups,
                fold_selected_program_hashes=selections,
                full_demo_exact=full_exact,
                demo_loo_exact=loo_exact,
            )
        )
    return tuple(certificates)


def _parse_task(task: Mapping[str, object]) -> tuple[
    tuple[tuple[np.ndarray, np.ndarray], ...],
    tuple[np.ndarray, ...],
]:
    raw_train = task.get("train", [])
    raw_test = task.get("test", [])
    if not isinstance(raw_train, list) or not isinstance(raw_test, list):
        raise TypeError("task train and test fields must be lists")
    train = tuple(
        (entry.as_array(item["input"]), entry.as_array(item["output"]))
        for item in raw_train
        if isinstance(item, Mapping) and "input" in item and "output" in item
    )
    tests = tuple(
        entry.as_array(item["input"])
        for item in raw_test
        if isinstance(item, Mapping) and "input" in item
    )
    if not train or not tests:
        raise ValueError("prequential tasks require at least one demonstration and test input")
    return train, tests


def _merge_catalog(
    old: Sequence[TypedProgramAST],
    new: Sequence[TypedProgramAST],
) -> tuple[TypedProgramAST, ...]:
    by_hash = {program.content_hash(): program for program in old}
    by_hash.update({program.content_hash(): program for program in new})
    return tuple(by_hash[key] for key in sorted(by_hash))


def _program_behavior_signature(
    program: TypedProgramAST,
    interpreter: TypedProgramInterpreter,
    train: Sequence[tuple[np.ndarray, np.ndarray]],
    tests: Sequence[np.ndarray],
) -> tuple[tuple[int, int, bytes], ...]:
    inputs = [source for source, _ in train] + list(tests)
    outputs = [
        np.asarray(interpreter.execute(program, source), dtype=np.int16)
        for source in inputs
    ]
    return tuple(
        (int(output.shape[0]), int(output.shape[1]), output.tobytes())
        for output in outputs
    )


def _behavior_quotient_programs(
    programs: Sequence[TypedProgramAST],
    interpreter: TypedProgramInterpreter,
    train: Sequence[tuple[np.ndarray, np.ndarray]],
    tests: Sequence[np.ndarray],
) -> tuple[TypedProgramAST, ...]:
    """Keep one minimum-description representative per current behavior class."""

    selected: dict[tuple[tuple[int, int, bytes], ...], TypedProgramAST] = {}
    ordered = sorted(
        programs,
        key=lambda program: (
            len(_program_tuple(program)),
            entry.program_cost(_program_tuple(program)),
            program.content_hash(),
        ),
    )
    for program in ordered:
        signature = _program_behavior_signature(program, interpreter, train, tests)
        selected.setdefault(signature, program)
    return tuple(sorted(selected.values(), key=lambda program: program.content_hash()))


def begin_prequential_query(
    state: PrequentialLearnerState,
    task: Mapping[str, object],
    *,
    config: MacroMinerConfig = MacroMinerConfig(),
) -> PendingPrequentialQuery:
    """Mine demo-exact programs and seal a read-only prediction snapshot."""

    train, tests = _parse_task(task)
    mining = mine_exact_demo_programs(train, config=config)
    catalog = _merge_catalog(state.catalog, mining.programs)
    # Previously seen programs are recommitted only if they remain exact on the
    # current demonstrations.  This allows additional prospective support while
    # preventing a stale program from borrowing a receipt from a nonmatching task.
    pre_reveal: list[TypedProgramAST] = []
    interpreter = legacy_macro_interpreter()
    for program in catalog:
        if all(
            entry.exact(
                np.asarray(interpreter.execute(program, source), dtype=np.int16),
                target,
            )
            for source, target in train
        ):
            pre_reveal.append(program)
    pre_reveal = list(
        _behavior_quotient_programs(pre_reveal, interpreter, train, tests)
    )
    source_hash = task_source_content_hash(task)
    interpreter_contract = legacy_macro_interpreter_contract()
    certificates = _build_discovery_certificates(
        pre_reveal,
        train,
        config=config,
        source_content_hash=source_hash,
        interpreter_contract=interpreter_contract,
    )
    opened_bank, opening = state.bank.begin_query(
        source_content_hash=source_hash,
        registry=interpreter.registry,
        interpreter_contract=interpreter_contract,
        pre_reveal_programs=pre_reveal,
        discovery_certificates=certificates,
    )
    snapshot = LearnerSnapshot.from_opened_bank(opened_bank, opening)
    return PendingPrequentialQuery(
        prior_state_hash=state.content_hash(),
        opened_bank=opened_bank,
        snapshot=snapshot,
        programs=tuple(sorted(pre_reveal, key=lambda program: program.content_hash())),
        catalog_after_mining=catalog,
        train=train,
        tests=tests,
        mining=mining,
        discovery_certificates=certificates,
    )


def solve_prequential_query(
    pending: PendingPrequentialQuery,
    task: Mapping[str, object],
    *,
    time_limit: float = entry.DEFAULT_TIME_LIMIT_PER_TASK,
    macro_promotion_policy: str = "attempt2",
    diagnostics: dict[str, object] | None = None,
):
    """Run the ordinary solver with the already sealed read-only snapshot."""

    return entry.solve_task(
        dict(task),
        time_limit=time_limit,
        learner_snapshot=pending.snapshot,
        macro_promotion_policy=macro_promotion_policy,
        diagnostics=diagnostics,
    )


def _exact_on_tests(
    program: TypedProgramAST,
    interpreter: TypedProgramInterpreter,
    tests: Sequence[np.ndarray],
    true_outputs: Sequence[object],
) -> bool:
    if len(tests) != len(true_outputs):
        raise ValueError("true-output count must match the number of test inputs")
    return all(
        entry.exact(
            np.asarray(interpreter.execute(program, source), dtype=np.int16),
            entry.as_array(target),
        )
        for source, target in zip(tests, true_outputs)
    )


def _uncompressed_evidence_bits(
    program: TypedProgramAST,
    receipt_hashes: Sequence[str],
) -> int:
    repeated = [
        {"receipt_hash": receipt_hash, "program": program.to_record()}
        for receipt_hash in receipt_hashes
    ]
    return len(_canonical_json(repeated).encode("utf-8")) * 8


def reveal_prequential_query(
    pending: PendingPrequentialQuery,
    true_outputs: Sequence[object],
) -> PrequentialUpdate:
    """Reveal one label and admit repeated exact programs for later tasks."""

    interpreter = legacy_macro_interpreter()
    exact_hashes: set[str] = set()
    program_by_hash = {
        program.content_hash(): program for program in pending.catalog_after_mining
    }
    for item in pending.snapshot.macros:
        program_by_hash[item.macro.program_hash] = item.macro.program
    for program_hash in pending.opened_bank.pending.committed_program_hashes:  # type: ignore[union-attr]
        program = program_by_hash.get(program_hash)
        if program is None:
            continue
        if _exact_on_tests(program, interpreter, pending.tests, true_outputs):
            exact_hashes.add(program_hash)

    current_receipt_hash = pending.snapshot.receipt.content_hash()
    receipt_by_hash = {
        observation.receipt_hash: observation.receipt
        for observation in pending.opened_bank.observations
    }
    receipt_by_hash[current_receipt_hash] = pending.snapshot.receipt
    existing_macro_programs = {
        entry_record.macro.program_hash for entry_record in pending.opened_bank.entries
    }
    proposals: list[AdmissionProposal] = []
    for program_hash in sorted(exact_hashes):
        if program_hash in existing_macro_programs:
            continue
        program = program_by_hash[program_hash]
        sources = [
            observation.receipt_hash
            for observation in pending.opened_bank.observations
            if program_hash in observation.exact_program_hashes
            and program_hash in observation.receipt.committed_program_hashes
        ]
        sources.append(current_receipt_hash)
        source_receipts = tuple(sorted(set(sources)))
        if len(source_receipts) < 2:
            continue
        demo_loo_exact = all(
            any(
                certificate.program_hash == program_hash
                and certificate.full_demo_exact
                and certificate.demo_loo_exact
                for certificate in receipt_by_hash[receipt_hash].discovery_certificates
            )
            for receipt_hash in source_receipts
        )
        proposals.append(
            AdmissionProposal(
                program=program,
                evidence=AdmissionEvidence(
                    source_receipt_hashes=source_receipts,
                    demo_loo_exact=demo_loo_exact,
                    uncompressed_description_bits=_uncompressed_evidence_bits(
                        program, source_receipts
                    ),
                ),
            )
        )

    label_hash = content_hash_text(
        _canonical_json([entry.grid_to_list(entry.as_array(value)) for value in true_outputs])
    )
    updated_bank, update = pending.opened_bank.reveal_and_update(
        receipt_hash=current_receipt_hash,
        label_content_hash=label_hash,
        exact_program_hashes=tuple(sorted(exact_hashes)),
        proposals=proposals,
    )
    state = PrequentialLearnerState(
        bank=updated_bank,
        catalog=pending.catalog_after_mining,
    )
    return PrequentialUpdate(
        state=state,
        exact_program_hashes=tuple(sorted(exact_hashes)),
        admitted_macro_hashes=tuple(
            decision.macro_hash for decision in update.decisions if decision.accepted
        ),
        rejected_macro_reasons=tuple(
            decision.reason for decision in update.decisions if not decision.accepted
        ),
    )


__all__ = [
    "DEFAULT_MACRO_PRIMITIVES",
    "MacroMinerConfig",
    "MacroMiningResult",
    "PendingPrequentialQuery",
    "PrequentialLearnerState",
    "PrequentialUpdate",
    "begin_prequential_query",
    "legacy_macro_interpreter",
    "legacy_macro_interpreter_contract",
    "macro_miner_contract",
    "mine_exact_demo_programs",
    "reveal_prequential_query",
    "solve_prequential_query",
]
