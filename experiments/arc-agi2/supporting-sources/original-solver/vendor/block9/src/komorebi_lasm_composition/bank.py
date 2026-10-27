"""Audit evidence and verified runtime banks for composite abstractions.

The two stores in this module are intentionally different:

* :class:`AbstractionEvidenceBank` is an audit-time mutable ledger.  It may
  contain corpus aliases and canonical training-content hashes.
* :class:`RuntimeAbstractionBank` is immutable and task-independent.  It stores
  typed templates but no source IDs, grids, training hashes, observed hole
  values, answer hashes, or timing.

Promotion is fail closed: stable means two distinct canonical training-content
identities and zero wrong activations.  Re-observing the same content through
another task alias never increases support.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

from .abstraction import (
    CompositeMacroTemplate,
    LeafTemplate,
    PromotionStatus,
    SubtreeOccurrence,
    TypedHole,
    anti_unify_subtrees,
    canonical_training_content_hash,
    canonical_value,
    content_hash,
    extract_template_bindings,
    normalize_leaf_sequence,
    self_validate_abstraction,
)


_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_ARC_ALIAS_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{8}(?![0-9a-f])")
_FORBIDDEN_RUNTIME_KEYS = {
    "taskid", "taskids", "sourcetaskid", "sourcetaskids", "exacttaskids",
    "wrongtaskids", "auditid", "auditids", "programid", "programids",
    "traininghash", "traininghashes", "trainingcontenthash",
    "trainingcontenthashes", "trainingpairhash", "trainingpairhashes",
    "targethash", "targethashes", "outputhash", "outputhashes",
    "expectedhash", "expectedhashes", "answerhash", "answerhashes",
    "rawgrid", "rawgrids", "inputgrid", "inputgrids", "outputgrid",
    "outputgrids", "targetgrid", "targetgrids", "expectedgrid",
    "expectedgrids", "answergrid", "answergrids", "outputs", "targets",
    "answers", "observedholevalue", "observedholevalues", "holevalues",
    "sourcebindings", "observedbindings", "elapsed", "elapsedseconds",
    "timing", "timestamp", "duration", "walltime", "walltimeseconds",
}


def _key_token(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def assert_runtime_safe(record: Any, *, path: tuple[str, ...] = ()) -> None:
    """Reject audit provenance and answer-bearing payloads recursively."""
    if isinstance(record, Mapping):
        for key, value in record.items():
            token = _key_token(key)
            if token in _FORBIDDEN_RUNTIME_KEYS:
                location = ".".join(path + (str(key),))
                raise ValueError(f"audit-only or answer-bearing runtime field: {location}")
            assert_runtime_safe(value, path=path + (str(key),))
    elif isinstance(record, (list, tuple)):
        for index, value in enumerate(record):
            assert_runtime_safe(value, path=path + (str(index),))
    elif isinstance(record, str) and _ARC_ALIAS_RE.search(record):
        # Full SHA-256 identities are structural and are intentionally allowed;
        # isolated eight-hex tokens have the exact shape of ARC corpus aliases.
        location = ".".join(path) or "$"
        raise ValueError(f"task-alias-shaped runtime value: {location}")


def _canonical_content_identity(
    *,
    training_content: Any | None,
    training_content_hash: str | None,
) -> str:
    if training_content is not None:
        computed = canonical_training_content_hash(training_content)
        if training_content_hash is not None and str(training_content_hash) != computed:
            raise ValueError("training content hash does not match canonical content")
        return computed
    if training_content_hash is None:
        raise ValueError("training content or a canonical content hash is required")
    identity = str(training_content_hash)
    if not _HASH_RE.fullmatch(identity):
        raise ValueError("training content identity must be a lowercase SHA-256 hash")
    return identity


@dataclass(frozen=True)
class AuditObservation:
    """One audit-only activation record, never serialized into runtime data."""

    macro_id: str
    training_content_hash: str
    correct: bool
    audit_id: str | None = None
    program_id: str | None = None

    def __post_init__(self) -> None:
        if not _HASH_RE.fullmatch(self.macro_id):
            raise ValueError("macro_id must be a SHA-256 hash")
        if not _HASH_RE.fullmatch(self.training_content_hash):
            raise ValueError("training_content_hash must be a SHA-256 hash")

    def to_record(self) -> dict[str, Any]:
        return {
            "macro_id": self.macro_id,
            "training_content_hash": self.training_content_hash,
            "correct": bool(self.correct),
            "audit_id": self.audit_id,
            "program_id": self.program_id,
        }


@dataclass
class _EvidenceState:
    template: CompositeMacroTemplate
    exact_content_hashes: set[str] = field(default_factory=set)
    wrong_content_hashes: set[str] = field(default_factory=set)
    observations: list[AuditObservation] = field(default_factory=list)

    @property
    def promoted_template(self) -> CompositeMacroTemplate:
        return self.template.with_evidence(
            support_count=len(self.exact_content_hashes),
            wrong_activation_count=len(self.wrong_content_hashes),
        )


@dataclass
class AbstractionEvidenceBank:
    """Mutable audit-time evidence with content-identity support accounting."""

    minimum_support: int = 2
    _states: dict[str, _EvidenceState] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if isinstance(self.minimum_support, bool) or not isinstance(self.minimum_support, int) or self.minimum_support != 2:
            raise ValueError("Block 9 stable support is fixed at two")

    def observe(
        self,
        template: CompositeMacroTemplate,
        *,
        correct: bool,
        training_content: Any | None = None,
        training_content_hash: str | None = None,
        audit_id: str | None = None,
        task_id: str | None = None,
        program_id: str | None = None,
    ) -> CompositeMacroTemplate:
        """Observe an activation; aliases of one content hash count only once."""
        if not isinstance(correct, bool):
            raise TypeError("correct must be Boolean")
        identity = _canonical_content_identity(
            training_content=training_content,
            training_content_hash=training_content_hash,
        )
        if audit_id is not None and task_id is not None and str(audit_id) != str(task_id):
            raise ValueError("audit_id and task_id disagree")
        source_alias = audit_id if audit_id is not None else task_id
        state = self._states.get(template.macro_id)
        if state is None:
            # Declared counts cannot be trusted without their distinct content
            # identities.  The evidence bank reconstructs them from zero.
            clean = replace(
                template, status=PromotionStatus.CANDIDATE,
                support_count=0, wrong_activation_count=0,
            )
            state = _EvidenceState(clean)
            self._states[template.macro_id] = state
        elif state.template.identity_record != template.identity_record:
            raise ValueError("macro ID collision with different template structure")
        if correct:
            state.exact_content_hashes.add(identity)
        else:
            state.wrong_content_hashes.add(identity)
        state.observations.append(AuditObservation(
            macro_id=template.macro_id, training_content_hash=identity,
            correct=correct, audit_id=(None if source_alias is None else str(source_alias)),
            program_id=(None if program_id is None else str(program_id)),
        ))
        return state.promoted_template

    observe_template = observe

    def ingest_occurrences(
        self,
        occurrences: Sequence[SubtreeOccurrence],
        *,
        name: str | None = None,
    ) -> CompositeMacroTemplate:
        """Anti-unify occurrences and enter their distinct evidence atomically."""
        template = anti_unify_subtrees(occurrences, name=name, minimum_support=2)
        for occurrence in occurrences:
            self.observe(
                template, correct=occurrence.correct,
                training_content_hash=occurrence.training_content_hash,
                audit_id=occurrence.audit_id, program_id=occurrence.program_id,
            )
        return self.template(template.macro_id)

    def template(self, macro_id: str) -> CompositeMacroTemplate:
        try:
            return self._states[str(macro_id)].promoted_template
        except KeyError as exc:
            raise KeyError(f"unknown composite macro: {macro_id}") from exc

    def templates(self) -> tuple[CompositeMacroTemplate, ...]:
        return tuple(sorted(
            (state.promoted_template for state in self._states.values()),
            key=lambda item: (item.semantic_schema, item.macro_id),
        ))

    def stable_templates(self) -> tuple[CompositeMacroTemplate, ...]:
        return tuple(item for item in self.templates() if item.status is PromotionStatus.STABLE)

    def provisional_templates(self) -> tuple[CompositeMacroTemplate, ...]:
        return tuple(item for item in self.templates() if item.status is PromotionStatus.PROVISIONAL)

    def retired_templates(self) -> tuple[CompositeMacroTemplate, ...]:
        return tuple(item for item in self.templates() if item.status is PromotionStatus.RETIRED)

    def runtime_bank(
        self,
        *,
        stable_only: bool = True,
        maximum_rank: int = 1,
        expanded_leaf_budget: int = 64,
    ) -> "RuntimeAbstractionBank":
        if not isinstance(stable_only, bool):
            raise TypeError("stable_only must be Boolean")
        if not stable_only:
            raise ValueError("provisional templates belong only to the audit evidence bank")
        templates = self.stable_templates()
        return RuntimeAbstractionBank(
            templates, minimum_support=2, maximum_rank=maximum_rank,
            expanded_leaf_budget=expanded_leaf_budget,
        )

    stable_bank = runtime_bank

    def audit_record(self) -> dict[str, Any]:
        """Serialize provenance separately from all runtime bank records."""
        states = []
        for macro_id, state in sorted(self._states.items()):
            promoted = state.promoted_template
            states.append({
                "macro_id": macro_id,
                "semantic_schema": promoted.semantic_schema,
                "status": promoted.status.value,
                "support_count": promoted.support_count,
                "wrong_activation_count": promoted.wrong_activation_count,
                "exact_training_content_hashes": sorted(state.exact_content_hashes),
                "wrong_training_content_hashes": sorted(state.wrong_content_hashes),
                "observations": [item.to_record() for item in state.observations],
            })
        record = {
            "schema": "komorebi.lasm_composite_abstraction_audit",
            "schema_version": 1,
            "minimum_support": 2,
            "states": states,
        }
        record["content_hash"] = content_hash(record)
        return record


def _internal_dependencies(
    template: CompositeMacroTemplate,
    macro_ids: set[str],
) -> tuple[str, ...]:
    leaf_references = {
        leaf.source_macro_id for leaf in template.leaves
        if leaf.source_macro_id is not None and leaf.source_macro_id in macro_ids
    }
    return tuple(sorted(set(template.dependencies) | leaf_references))


@dataclass(frozen=True)
class RuntimeAbstractionBank:
    """Immutable, hash-verified DAG of task-independent macro templates."""

    macros: tuple[CompositeMacroTemplate, ...]
    minimum_support: int = 2
    maximum_rank: int = 1
    expanded_leaf_budget: int = 64
    schema_version: int = 1

    def __post_init__(self) -> None:
        if isinstance(self.macros, (str, bytes, bytearray, Mapping)):
            raise TypeError("runtime macros must be a finite sequence")
        object.__setattr__(self, "macros", tuple(self.macros))
        for label, value in (
            ("minimum_support", self.minimum_support),
            ("maximum_rank", self.maximum_rank),
            ("expanded_leaf_budget", self.expanded_leaf_budget),
            ("schema_version", self.schema_version),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{label} must be an integer")
        if self.minimum_support != 2:
            raise ValueError("Block 9 stable support is fixed at two")
        if self.maximum_rank != 1:
            raise ValueError("this release enforces the audited rank-1 production boundary")
        if self.expanded_leaf_budget < 2:
            raise ValueError("expanded leaf budget must be at least two")
        if self.schema_version != 1:
            raise ValueError("unsupported runtime-bank schema version")
        ids = [macro.macro_id for macro in self.macros]
        if len(ids) != len(set(ids)):
            raise ValueError("runtime macro IDs must be unique")
        if any(macro.status is not PromotionStatus.STABLE for macro in self.macros):
            raise ValueError("runtime banks may contain stable macros only")
        if any(macro.minimum_support != 2 for macro in self.macros):
            raise ValueError("runtime macro support policy mismatch")
        if any(
            leaf.status not in {"primitive", "stable"}
            for macro in self.macros for leaf in macro.leaves
        ):
            raise ValueError("runtime macro leaves must be primitive or stable")
        self._validate_dag_and_budgets()
        assert_runtime_safe(self._payload_record())

    @property
    def by_id(self) -> dict[str, CompositeMacroTemplate]:
        return {macro.macro_id: macro for macro in self.macros}

    def _validate_dag_and_budgets(self) -> None:
        by_id = self.by_id
        ids = set(by_id)
        dependencies: dict[str, tuple[str, ...]] = {}
        for macro_id, macro in by_id.items():
            missing = set(macro.dependencies) - ids
            if missing:
                raise ValueError(
                    f"macro {macro_id} has missing dependencies: {sorted(missing)}"
                )
            leaf_dependencies = {
                leaf.source_macro_id for leaf in macro.leaves
                if leaf.source_macro_id in ids
            }
            if set(macro.dependencies) != leaf_dependencies:
                raise ValueError(
                    f"macro {macro_id} dependency metadata must exactly match positioned leaf references"
                )
            dependencies[macro_id] = tuple(sorted(leaf_dependencies))
            if macro_id in dependencies[macro_id]:
                raise ValueError(f"macro {macro_id} directly depends on itself")

        state: dict[str, int] = {}
        order: list[str] = []

        def visit(macro_id: str) -> None:
            mark = state.get(macro_id, 0)
            if mark == 1:
                raise ValueError("composite abstraction dependency cycle")
            if mark == 2:
                return
            state[macro_id] = 1
            for dependency in dependencies[macro_id]:
                visit(dependency)
            state[macro_id] = 2
            order.append(macro_id)

        for macro_id in sorted(ids):
            visit(macro_id)

        # Independently mined macros start hole names at h0.  Until a composer
        # explicitly alpha-renames them, a reachable collision is ambiguous
        # and must not silently bind two unrelated coordinates together.
        def reachable_holes(macro_id: str, seen: set[str]) -> dict[str, str]:
            if macro_id in seen:
                return {}
            seen.add(macro_id)
            owners = {hole.name: macro_id for hole in by_id[macro_id].holes}
            for dependency in dependencies[macro_id]:
                for name, owner in reachable_holes(dependency, seen).items():
                    previous = owners.get(name)
                    if previous is not None and previous != owner:
                        raise ValueError(
                            f"reachable hole name collision {name!r} between {previous} and {owner}; alpha-rename before composition"
                        )
                    owners[name] = owner
            return owners

        for macro_id in sorted(ids):
            reachable_holes(macro_id, set())

        expanded: dict[str, int] = {}
        for macro_id in order:
            macro = by_id[macro_id]
            count = 0
            for leaf in macro.leaves:
                if leaf.source_macro_id in ids:
                    count += expanded[str(leaf.source_macro_id)]
                else:
                    count += 1
            expected_rank = 1 + max(
                (by_id[dependency].rank for dependency in dependencies[macro_id]),
                default=0,
            )
            if macro.rank != expected_rank:
                raise ValueError(
                    f"macro {macro_id} rank {macro.rank} does not match DAG rank {expected_rank}"
                )
            if macro.rank > self.maximum_rank:
                raise ValueError(f"macro {macro_id} exceeds maximum rank")
            if macro.expanded_leaf_count != count:
                raise ValueError(
                    f"macro {macro_id} declares {macro.expanded_leaf_count} expanded leaves; expected {count}"
                )
            if count > self.expanded_leaf_budget:
                raise ValueError(f"macro {macro_id} exceeds expanded leaf budget")
            expanded[macro_id] = count

    def _payload_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composite_abstraction_bank",
            "schema_version": 1,
            "minimum_support": 2,
            "maximum_rank": int(self.maximum_rank),
            "expanded_leaf_budget": int(self.expanded_leaf_budget),
            "macros": [
                macro.to_runtime_record()
                for macro in sorted(self.macros, key=lambda item: item.macro_id)
            ],
        }

    @property
    def bank_id(self) -> str:
        return content_hash(self._payload_record())

    @property
    def canonical_bank_hash(self) -> str:
        return self.bank_id

    def to_runtime_record(self) -> dict[str, Any]:
        record = {**self._payload_record(), "bank_id": self.bank_id}
        record["content_hash"] = content_hash(record)
        assert_runtime_safe(record)
        return record

    to_record = to_runtime_record

    @classmethod
    def from_runtime_record(cls, record: Mapping[str, Any]) -> "RuntimeAbstractionBank":
        assert_runtime_safe(record)
        unknown = set(record) - {
            "schema", "schema_version", "minimum_support", "maximum_rank",
            "expanded_leaf_budget", "macros", "bank_id", "content_hash",
        }
        if unknown:
            raise ValueError(f"unknown runtime-bank fields: {sorted(unknown)}")
        required = {
            "schema", "schema_version", "minimum_support", "maximum_rank",
            "expanded_leaf_budget", "macros", "bank_id", "content_hash",
        }
        missing = required - set(record)
        if missing:
            raise ValueError(f"missing runtime-bank fields: {sorted(missing)}")
        if record.get("schema") != "komorebi.lasm_composite_abstraction_bank":
            raise ValueError("not a Block 9 composite abstraction bank")
        schema_version = record.get("schema_version", 1)
        if isinstance(schema_version, bool) or not isinstance(schema_version, int) or schema_version != 1:
            raise ValueError("unsupported runtime-bank schema version")
        macros = tuple(
            CompositeMacroTemplate.from_runtime_record(item)
            for item in record.get("macros", ())
        )
        bank = cls(
            macros=macros,
            minimum_support=record.get("minimum_support", 2),
            maximum_rank=record.get("maximum_rank", 1),
            expanded_leaf_budget=record.get("expanded_leaf_budget", 64),
            schema_version=schema_version,
        )
        if record.get("bank_id") != bank.bank_id:
            raise ValueError("canonical abstraction bank hash mismatch")
        payload = {key: value for key, value in record.items() if key != "content_hash"}
        if record.get("content_hash") != content_hash(payload):
            raise ValueError("abstraction bank content hash mismatch")
        return bank

    @classmethod
    def verify_runtime_record(cls, record: Mapping[str, Any]) -> "RuntimeAbstractionBank":
        """Parse, validate hashes, validate DAG ranks, and validate budgets."""
        return cls.from_runtime_record(record)

    def matching_schema(
        self,
        semantic_schema: str,
        *,
        stable_only: bool = True,
    ) -> tuple[CompositeMacroTemplate, ...]:
        return tuple(
            macro for macro in sorted(self.macros, key=lambda item: item.macro_id)
            if macro.semantic_schema == semantic_schema
            and (not stable_only or macro.status is PromotionStatus.STABLE)
        )

    def permits(self, macro_id: str, *, stable_only: bool = True) -> bool:
        macro = self.by_id.get(str(macro_id))
        return macro is not None and (
            not stable_only or macro.status is PromotionStatus.STABLE
        )

    def expand(
        self,
        macro_id: str,
        bindings: Mapping[str, Any] | None = None,
        *,
        stable_only: bool = True,
        maximum_expanded_leaves: int | None = None,
    ) -> tuple[dict[str, Any], ...]:
        """Expand one DAG node; stable-only execution is the default."""
        if not isinstance(stable_only, bool):
            raise TypeError("stable_only must be Boolean")
        by_id = self.by_id
        if maximum_expanded_leaves is not None and (
            isinstance(maximum_expanded_leaves, bool)
            or not isinstance(maximum_expanded_leaves, int)
        ):
            raise TypeError("maximum_expanded_leaves must be an integer or None")
        limit = self.expanded_leaf_budget if maximum_expanded_leaves is None else min(
            maximum_expanded_leaves, self.expanded_leaf_budget,
        )
        if limit < 1:
            raise ValueError("maximum expanded leaves must be positive")
        provided = dict(bindings or {})

        reachable: set[str] = set()

        def collect_holes(current_id: str, seen: set[str]) -> None:
            if current_id in seen:
                return
            seen.add(current_id)
            macro = by_id[current_id]
            reachable.update(hole.name for hole in macro.holes)
            for dependency in _internal_dependencies(macro, set(by_id)):
                collect_holes(dependency, seen)

        if str(macro_id) not in by_id:
            raise KeyError(f"unknown composite macro: {macro_id}")
        collect_holes(str(macro_id), set())
        unknown = set(provided) - reachable
        if unknown:
            raise ValueError(f"unknown hole bindings: {sorted(unknown)}")

        def visit(current_id: str, stack: tuple[str, ...]) -> list[dict[str, Any]]:
            if current_id in stack:
                raise ValueError("composite abstraction expansion cycle")
            try:
                macro = by_id[current_id]
            except KeyError as exc:
                raise KeyError(f"unknown composite macro: {current_id}") from exc
            if stable_only and macro.status is not PromotionStatus.STABLE:
                raise PermissionError("non-stable composite expansion is disabled")
            missing = {
                hole.name for hole in macro.holes
                if not hole.optional and hole.name not in provided
            }
            if missing:
                raise ValueError(f"missing hole bindings: {sorted(missing)}")
            result: list[dict[str, Any]] = []
            for leaf in macro.leaves:
                reference = leaf.source_macro_id
                if reference in by_id:
                    result.extend(visit(str(reference), stack + (current_id,)))
                else:
                    result.append(leaf.instantiate(provided))
                if len(result) > limit:
                    raise RuntimeError("expanded leaf budget exceeded")
            return result

        return tuple(visit(str(macro_id), ()))


def expand_template(
    template: CompositeMacroTemplate,
    bindings: Mapping[str, Any] | None = None,
    *,
    bank: RuntimeAbstractionBank | None = None,
    stable_only: bool = True,
    expanded_leaf_budget: int = 64,
) -> tuple[dict[str, Any], ...]:
    """Convenience expansion with the same stable-only default as the bank."""
    if bank is None:
        bank = RuntimeAbstractionBank(
            (template,), expanded_leaf_budget=expanded_leaf_budget,
            maximum_rank=1,
        )
    elif template.macro_id not in bank.by_id:
        raise ValueError("template is not a member of the supplied runtime bank")
    return bank.expand(
        template.macro_id, bindings, stable_only=stable_only,
        maximum_expanded_leaves=expanded_leaf_budget,
    )


def self_validate_bank() -> dict[str, Any]:
    """Dependency-free smoke validation of promotion, isolation, and hashes."""
    abstraction = self_validate_abstraction()
    leaves_a = (
        {"namespace": "primitive", "family": "crop_bbox", "parameters": {}},
        {"namespace": "compiler", "family": "panel_program", "parameters": {
            "spec": "equal:2x1", "operation": "select:0|id", "recolor": [[0, 0]],
        }},
    )
    leaves_b = (
        {"namespace": "primitive", "family": "crop_bbox", "parameters": {}},
        {"namespace": "compiler", "family": "role_panel_program", "parameters": {
            "panelization": ["equal", 2, 1], "operation": ["select", 0, "id"],
            "recolor": [[0, 0]],
        }},
    )
    hash_a = canonical_training_content_hash({"train": "a"})
    hash_b = canonical_training_content_hash({"train": "b"})
    occurrence_a = SubtreeOccurrence(
        tuple(canonical_value(item) for item in normalize_leaf_sequence(leaves_a)),
        hash_a, audit_id="alias-a",
    )
    occurrence_b = SubtreeOccurrence(
        tuple(canonical_value(item) for item in normalize_leaf_sequence(leaves_b)),
        hash_b, audit_id="alias-b",
    )
    template = anti_unify_subtrees((occurrence_a, occurrence_b))
    evidence = AbstractionEvidenceBank()
    evidence.observe(template, correct=True, training_content_hash=hash_a, task_id="alias-a")
    alias_template = evidence.observe(
        template, correct=True, training_content_hash=hash_a, task_id="alias-a-copy",
    )
    assert alias_template.support_count == 1
    stable = evidence.observe(
        template, correct=True, training_content_hash=hash_b, task_id="alias-b",
    )
    assert stable.status is PromotionStatus.STABLE and stable.support_count == 2
    runtime = evidence.runtime_bank()
    caller_owned_macros = list(runtime.macros)
    immutable_runtime = RuntimeAbstractionBank(caller_owned_macros)
    immutable_bank_id = immutable_runtime.bank_id
    caller_owned_macros.clear()
    assert immutable_runtime.bank_id == immutable_bank_id
    assert len(immutable_runtime.macros) == 1
    serialized = runtime.to_runtime_record()
    assert_runtime_safe(serialized)
    restored = RuntimeAbstractionBank.from_runtime_record(serialized)
    assert restored.bank_id == runtime.bank_id
    expanded = restored.expand(
        stable.macro_id, extract_template_bindings(stable, occurrence_a)
    )
    assert len(expanded) == 2
    assert expanded[1]["family"] == "panel_program"
    assert expanded[1]["macro_schema"] == "panel_program"
    assert expanded[1]["parameters"] == {
        "operation": "select:0|id", "recolor": [[0, 0]], "spec": "equal:2x1",
    }
    role_expanded = restored.expand(
        stable.macro_id, extract_template_bindings(stable, occurrence_b)
    )
    assert role_expanded[1]["family"] == "role_panel_program"
    assert role_expanded[1]["macro_schema"] == "role_panel_program"
    assert role_expanded[1]["parameters"]["panelization"] == ["equal", 2, 1]
    audit = evidence.audit_record()
    assert any(item.get("audit_id") == "alias-a" for item in audit["states"][0]["observations"])
    assert "training_content_hash" not in str(serialized)
    return {
        **abstraction,
        "alias_support_after_duplicate": alias_template.support_count,
        "stable_support": stable.support_count,
        "runtime_macro_count": len(runtime.macros),
        "expanded_leaves": len(expanded),
        "bank_hash_verified": True,
        "runtime_audit_isolation": True,
        "runtime_deep_immutability": True,
        "passed": True,
    }


__all__ = [
    "AbstractionEvidenceBank", "AuditObservation", "PromotionStatus",
    "RuntimeAbstractionBank", "assert_runtime_safe", "expand_template",
    "self_validate_bank",
]
