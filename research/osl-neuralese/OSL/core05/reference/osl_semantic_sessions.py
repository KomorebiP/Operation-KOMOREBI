#!/usr/bin/env python3
"""Independent finite-session semantics for OSL-Core 0.5.

This module deliberately does not import ``OSLRuntime``, the OSL parser, the
runtime model, or the legacy session verifier.  It reads the small session and
transaction fragment directly from source, binds every relevant effect to its
statement boundary, reconstructs the finite protocol state, recomputes graph
verification reports, and compares the result with the committed final state.

The input receipt chain is untrusted.  Exact receipt schemas, the hash chain,
source correspondence, statement spans, transition legality, transaction
rollback, and the final session projection are all checked fail closed.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


RECEIPT_SCHEMA = "osl.core.receipt.v2"
CORE_VERSION = "0.5"
SUPPORTED_CORE_VERSIONS = frozenset({"0.4", "0.5"})
REPORT_SCHEMA = "osl.core.session-verification.v1"
SEMANTIC_REPORT_SCHEMA = "osl.core05.semantic-sessions.v1"
ZERO_DIGEST = "0" * 64
IDENT = r"[A-Za-z_][\w-]*"

_BASE_FIELDS = {
    "schema",
    "core_version",
    "index",
    "state_index",
    "step",
    "kind",
    "transaction",
    "previous_digest",
    "digest",
}

_PAYLOAD_FIELDS: dict[str, set[str]] = {
    "session_declare": {"session"},
    "session_transition_declare": {
        "session",
        "source_state",
        "event",
        "sender",
        "receiver",
        "target_state",
    },
    "session_terminal_declare": {"session", "state"},
    "session_verify": {"report"},
    "session_start": {"session"},
    "session_advance": {
        "session",
        "event",
        "sender",
        "receiver",
        "source_state",
        "target_state",
    },
    "transaction_begin": {"begin_audit_index", "checkpoint_digest"},
    "transaction_commit": {
        "begin_audit_index",
        "begin_step",
        "body_effect_span",
        "final_state_digest",
    },
    "transaction_rollback": {
        "automatic",
        "reason",
        "begin_audit_index",
        "begin_step",
        "checkpoint_digest",
        "body_effect_span",
        "pre_restore_digest",
        "discarded_chain_tip",
        "discarded_receipt_count",
        "restored_state_digest",
    },
}

_TRACKED_RECEIPT_KINDS = set(_PAYLOAD_FIELDS)

_SESSION_FIELDS = {
    "name",
    "participants",
    "initial_state",
    "current_state",
    "active",
    "terminal_states",
    "verification",
    "transitions",
    "history",
}

_TRANSITION_FIELDS = {"from", "event", "sender", "receiver", "to"}
_START_HISTORY_FIELDS = {"step", "event", "state"}
_ADVANCE_HISTORY_FIELDS = {
    "step",
    "event",
    "sender",
    "receiver",
    "from",
    "to",
    "terminal",
}

_VERIFICATION_FIELDS = {
    "schema",
    "session",
    "state_count",
    "transition_count",
    "initial_state",
    "terminal_states",
    "reachable_states",
    "unreachable_states",
    "reachable_deadlocks",
    "terminal_with_outgoing",
    "states_without_terminal_path",
    "deterministic",
    "initial_declared",
    "terminal_declared",
    "all_reachable_states_can_terminate",
    "all_checks_pass",
    "report_digest",
}

_COMMIT_FIELDS = _BASE_FIELDS | {
    "statement_ordinal",
    "line_number",
    "statement_kind",
    "source_digest",
    "node_digest",
    "before_semantic_digest",
    "after_semantic_digest",
    "emitted_receipt_indices",
    "effect_span",
}

_REJECT_FIELDS = _COMMIT_FIELDS | {"rolled_back", "error"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _without_digest(value: Mapping[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(dict(value))
    payload.pop("digest", None)
    return payload


def _normal(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _normal(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normal(item) for item in value]
    return value


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_sha256(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_ident(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(IDENT, value) is not None


@dataclass(frozen=True)
class _SourceStatement:
    ordinal: int
    line_number: int
    source: str
    kind: str
    args: dict[str, Any]
    expected_receipt: str

    @property
    def source_digest(self) -> str:
        return digest(self.source)

    @property
    def node_digest(self) -> str:
        payload = {
            "ordinal": self.ordinal,
            "line_number": self.line_number,
            "kind": self.kind,
            "source": self.source,
            "args": self.args,
        }
        return digest(payload)


@dataclass
class _Session:
    name: str
    participants: tuple[str, ...]
    initial_state: str
    current_state: str | None = None
    active: bool = False
    transitions: dict[tuple[str, str, str, str], str] = field(default_factory=dict)
    terminal_states: set[str] = field(default_factory=set)
    verification: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def canonical(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "participants": list(self.participants),
            "initial_state": self.initial_state,
            "current_state": self.current_state,
            "active": self.active,
            "terminal_states": sorted(self.terminal_states),
            "verification": copy.deepcopy(self.verification),
            "transitions": [
                {
                    "from": key[0],
                    "event": key[1],
                    "sender": key[2],
                    "receiver": key[3],
                    "to": target,
                }
                for key, target in sorted(self.transitions.items())
            ],
            "history": copy.deepcopy(self.history),
        }


def _finite_verification(protocol: _Session) -> dict[str, Any]:
    states = {protocol.initial_state, *protocol.terminal_states}
    outgoing: dict[str, set[str]] = {}
    incoming: dict[str, set[str]] = {}
    for (source, _event, _sender, _receiver), target in protocol.transitions.items():
        states.add(source)
        states.add(target)
        outgoing.setdefault(source, set()).add(target)
        incoming.setdefault(target, set()).add(source)

    reachable = {protocol.initial_state}
    frontier = [protocol.initial_state]
    while frontier:
        source = frontier.pop()
        for target in outgoing.get(source, set()):
            if target not in reachable:
                reachable.add(target)
                frontier.append(target)

    can_reach_terminal = set(protocol.terminal_states)
    frontier = list(protocol.terminal_states)
    while frontier:
        target = frontier.pop()
        for source in incoming.get(target, set()):
            if source not in can_reach_terminal:
                can_reach_terminal.add(source)
                frontier.append(source)

    reachable_deadlocks = {
        state
        for state in reachable
        if not outgoing.get(state) and state not in protocol.terminal_states
    }
    terminal_with_outgoing = {
        state for state in protocol.terminal_states if outgoing.get(state)
    }
    states_without_terminal_path = reachable - can_reach_terminal
    terminal_declared = bool(protocol.terminal_states)
    all_reachable_can_terminate = terminal_declared and not states_without_terminal_path
    checks = {
        "deterministic": True,
        "initial_declared": protocol.initial_state in states,
        "terminal_declared": terminal_declared,
        "no_reachable_nonterminal_deadlocks": not reachable_deadlocks,
        "no_terminal_outgoing_transitions": not terminal_with_outgoing,
        "all_reachable_states_can_terminate": all_reachable_can_terminate,
    }
    unsigned = {
        "schema": REPORT_SCHEMA,
        "session": protocol.name,
        "state_count": len(states),
        "transition_count": len(protocol.transitions),
        "initial_state": protocol.initial_state,
        "terminal_states": sorted(protocol.terminal_states),
        "reachable_states": sorted(reachable),
        "unreachable_states": sorted(states - reachable),
        "reachable_deadlocks": sorted(reachable_deadlocks),
        "terminal_with_outgoing": sorted(terminal_with_outgoing),
        "states_without_terminal_path": sorted(states_without_terminal_path),
        "deterministic": True,
        "initial_declared": protocol.initial_state in states,
        "terminal_declared": terminal_declared,
        "all_reachable_states_can_terminate": all_reachable_can_terminate,
        "all_checks_pass": all(checks.values()),
    }
    return {**unsigned, "report_digest": digest(unsigned)}


class SessionSemanticVerifier:
    """Fail-closed, source-bound reconstructor for the OSL session fragment."""

    def __init__(
        self,
        source: str,
        receipts: Sequence[Mapping[str, Any]],
        final_state: Mapping[str, Any] | None = None,
    ) -> None:
        self.source = source
        self.receipts = list(receipts) if isinstance(receipts, (list, tuple)) else []
        self.final_state = final_state
        self.failures: list[dict[str, Any]] = []
        self.source_statements: dict[int, _SourceStatement] = {}
        self.statement_count = 0
        self.boundaries: dict[int, dict[str, Any]] = {}
        self.emitted_owner: dict[int, dict[str, Any]] = {}
        self.tracked_by_boundary: dict[int, list[dict[str, Any]]] = {}
        self.sessions: dict[str, _Session] = {}
        self.active_transaction: dict[str, Any] | None = None
        self.counts = {
            "session_receipts": 0,
            "declarations": 0,
            "transition_declarations": 0,
            "terminal_declarations": 0,
            "finite_verifications": 0,
            "starts": 0,
            "advances": 0,
            "transaction_begins": 0,
            "transaction_commits": 0,
            "transaction_rollbacks": 0,
        }

    def fail(self, property_name: str, **details: Any) -> None:
        self.failures.append({"property": property_name, **details})

    def _expect(self, condition: bool, property_name: str, **details: Any) -> bool:
        if not condition:
            self.fail(property_name, **details)
        return condition

    def _strict_keys(
        self, value: Mapping[str, Any], expected: set[str], property_name: str, **details: Any
    ) -> bool:
        actual = set(value)
        return self._expect(
            actual == expected,
            property_name,
            missing=sorted(expected - actual),
            extra=sorted(actual - expected),
            **details,
        )

    def _parse_name_list(self, text: str, line_number: int) -> tuple[str, ...] | None:
        try:
            try:
                value = json.loads(text)
            except json.JSONDecodeError:
                value = ast.literal_eval(text)
            if not isinstance(value, (list, tuple)):
                raise ValueError("participants must be a list")
            names = tuple(str(item) for item in value)
            if len(names) != len(set(names)):
                raise ValueError("participants must be unique")
            return names
        except (SyntaxError, TypeError, ValueError) as exc:
            self.fail("source_session_syntax", line_number=line_number, error=str(exc))
            return None

    def _parse_source(self) -> None:
        if not isinstance(self.source, str):
            self.fail("source_type", expected="str")
            return
        patterns: list[tuple[str, str, str]] = [
            (
                "session",
                rf"session\s+({IDENT})\s+participants\s+(\[.*\])\s+initial\s+({IDENT})",
                "session_declare",
            ),
            (
                "session_transition",
                rf"session_transition\s+({IDENT})\s+({IDENT})\s+communicate\s+({IDENT})\s+({IDENT})\s*->\s*({IDENT})",
                "session_transition_declare",
            ),
            (
                "session_terminal",
                rf"session_terminal\s+({IDENT})\s+({IDENT})",
                "session_terminal_declare",
            ),
            ("verify_session", rf"verify_session\s+({IDENT})", "session_verify"),
            ("start_session", rf"start_session\s+({IDENT})", "session_start"),
            (
                "communicate",
                rf"communicate\s+({IDENT})\s+from\s+({IDENT})\s+to\s+({IDENT})\s+as\s+({IDENT})(?:\s+in\s+({IDENT}))?",
                "session_advance",
            ),
            ("begin_transaction", rf"begin_transaction\s+({IDENT})", "transaction_begin"),
            ("commit_transaction", rf"commit_transaction\s+({IDENT})", "transaction_commit"),
            ("rollback_transaction", rf"rollback_transaction\s+({IDENT})", "transaction_rollback"),
        ]
        for line_number, raw in enumerate(self.source.splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            ordinal = self.statement_count
            self.statement_count += 1
            head = line.split(None, 1)[0]
            for kind, pattern, expected_receipt in patterns:
                if head != kind:
                    continue
                match = re.fullmatch(pattern, line)
                if match is None:
                    self.fail("source_session_syntax", line_number=line_number, source=line)
                    break
                groups = match.groups()
                args: dict[str, Any]
                if kind == "session":
                    participants = self._parse_name_list(groups[1], line_number)
                    if participants is None:
                        break
                    args = {"name": groups[0], "participants": participants, "initial": groups[2]}
                elif kind == "session_transition":
                    args = {
                        "session": groups[0],
                        "source_state": groups[1],
                        "sender": groups[2],
                        "receiver": groups[3],
                        "target_state": groups[4],
                    }
                elif kind in {"session_terminal"}:
                    args = {"session": groups[0], "state": groups[1]}
                elif kind in {"verify_session", "start_session"}:
                    args = {"session": groups[0]}
                elif kind == "communicate":
                    args = {
                        "source_packet": groups[0],
                        "source_agent": groups[1],
                        "target_agent": groups[2],
                        "target_packet": groups[3],
                        "session": groups[4],
                    }
                    if groups[4] is None:
                        break
                else:
                    args = {"name": groups[0]}
                self.source_statements[ordinal] = _SourceStatement(
                    ordinal=ordinal,
                    line_number=line_number,
                    source=line,
                    kind=kind,
                    args=args,
                    expected_receipt=expected_receipt,
                )
                break

    def _validate_chain(self) -> None:
        if not isinstance(self.receipts, list):
            self.fail("receipt_sequence_type")
            return
        previous = ZERO_DIGEST
        chain_core_version: str | None = None
        for position, receipt in enumerate(self.receipts):
            if not isinstance(receipt, Mapping):
                self.fail("receipt_type", receipt_index=position)
                continue
            required = _BASE_FIELDS
            self._expect(required <= set(receipt), "receipt_envelope", receipt_index=position)
            self._expect(receipt.get("schema") == RECEIPT_SCHEMA, "receipt_schema", receipt_index=position)
            self._expect(
                receipt.get("core_version") in SUPPORTED_CORE_VERSIONS,
                "receipt_core_version",
                receipt_index=position,
            )
            if chain_core_version is None and receipt.get("core_version") in SUPPORTED_CORE_VERSIONS:
                chain_core_version = str(receipt.get("core_version"))
            elif chain_core_version is not None:
                self._expect(
                    receipt.get("core_version") == chain_core_version,
                    "receipt_core_version_consistency",
                    receipt_index=position,
                    expected=chain_core_version,
                    actual=receipt.get("core_version"),
                )
            self._expect(receipt.get("index") == position, "receipt_index", receipt_index=position)
            self._expect(_is_int(receipt.get("state_index")), "receipt_state_index", receipt_index=position)
            self._expect(_is_int(receipt.get("step")), "receipt_step", receipt_index=position)
            self._expect(receipt.get("previous_digest") == previous, "receipt_previous_digest", receipt_index=position)
            expected_digest = digest(_without_digest(receipt))
            self._expect(receipt.get("digest") == expected_digest, "receipt_digest", receipt_index=position)
            previous = str(receipt.get("digest", ""))

        opens = [r for r in self.receipts if isinstance(r, Mapping) and r.get("kind") == "program_open"]
        self._expect(len(opens) == 1, "source_program_open_count", actual=len(opens))
        if len(opens) == 1 and isinstance(self.source, str):
            opened = opens[0]
            self._expect(opened.get("source_digest") == digest(self.source), "source_program_digest")
            self._expect(opened.get("source_bytes") == len(self.source.encode("utf-8")), "source_program_bytes")
            self._expect(opened.get("source_lines") == len(self.source.splitlines()), "source_program_lines")

        accepts = [r for r in self.receipts if isinstance(r, Mapping) and r.get("kind") == "parse_accept"]
        if accepts:
            self._expect(len(accepts) == 1, "parse_accept_count", actual=len(accepts))
            self._expect(
                accepts[0].get("statement_count") == self.statement_count,
                "source_statement_count",
                expected=self.statement_count,
                actual=accepts[0].get("statement_count"),
            )

    def _validate_boundary(self, receipt: Mapping[str, Any]) -> None:
        index = receipt.get("index")
        kind = receipt.get("kind")
        expected_fields = _COMMIT_FIELDS if kind == "statement_commit" else _REJECT_FIELDS
        self._strict_keys(receipt, expected_fields, "statement_boundary_schema", receipt_index=index)
        ordinal = receipt.get("statement_ordinal")
        self._expect(_is_int(ordinal) and ordinal >= 0, "statement_boundary_ordinal", receipt_index=index)
        self._expect(_is_int(receipt.get("line_number")), "statement_boundary_line", receipt_index=index)
        for key in ("source_digest", "node_digest", "before_semantic_digest", "after_semantic_digest"):
            self._expect(_is_sha256(receipt.get(key)), "statement_boundary_digest", receipt_index=index, field=key)
        emitted = receipt.get("emitted_receipt_indices")
        span = receipt.get("effect_span")
        sequence_ok = isinstance(emitted, (list, tuple)) and all(_is_int(item) for item in emitted)
        span_ok = isinstance(span, (list, tuple)) and len(span) == 2 and all(_is_int(item) for item in span)
        self._expect(sequence_ok, "statement_emitted_indices", receipt_index=index)
        self._expect(span_ok, "statement_effect_span", receipt_index=index)
        if sequence_ok and span_ok:
            start, end = int(span[0]), int(span[1])
            self._expect(list(emitted) == list(range(start, end)), "statement_span_contiguous", receipt_index=index)
            self._expect(end == index, "statement_span_boundary", receipt_index=index)
            for emitted_index in emitted:
                if emitted_index in self.emitted_owner:
                    self.fail("statement_span_overlap", receipt_index=emitted_index)
                self.emitted_owner[int(emitted_index)] = dict(receipt)
        if kind == "statement_reject":
            self._expect(isinstance(receipt.get("rolled_back"), bool), "statement_rollback_flag", receipt_index=index)
            self._expect(isinstance(receipt.get("error"), str), "statement_error", receipt_index=index)

    def _execution_limit(self) -> int:
        terminals = [
            r
            for r in self.receipts
            if isinstance(r, Mapping) and r.get("kind") in {"program_complete", "program_reject"}
        ]
        self._expect(len(terminals) == 1, "program_terminal_count", actual=len(terminals))
        if len(terminals) != 1:
            return max(self.boundaries, default=-1)
        terminal = terminals[0]
        self._expect(terminal.get("index") == len(self.receipts) - 1, "program_terminal_last")
        if terminal.get("kind") == "program_complete" or terminal.get("phase") == "finalization":
            return self.statement_count - 1
        if terminal.get("phase") == "statement":
            failed = terminal.get("failed_ordinal")
            self._expect(_is_int(failed), "program_failed_ordinal")
            return int(failed) if _is_int(failed) else max(self.boundaries, default=-1)
        if terminal.get("phase") in {"parse", "static"}:
            return -1
        self.fail("program_terminal_phase", phase=terminal.get("phase"))
        return max(self.boundaries, default=-1)

    def _index_statement_boundaries(self) -> None:
        for receipt in self.receipts:
            if not isinstance(receipt, Mapping) or receipt.get("kind") not in {"statement_commit", "statement_reject"}:
                continue
            self._validate_boundary(receipt)
            ordinal = receipt.get("statement_ordinal")
            if not _is_int(ordinal):
                continue
            if ordinal in self.boundaries:
                self.fail("statement_boundary_duplicate", statement_ordinal=ordinal)
            self.boundaries[int(ordinal)] = dict(receipt)

        limit = self._execution_limit()
        for ordinal, statement in self.source_statements.items():
            boundary = self.boundaries.get(ordinal)
            if ordinal <= limit:
                if boundary is None:
                    self.fail("source_statement_boundary_missing", statement_ordinal=ordinal)
                    continue
                expected = {
                    "line_number": statement.line_number,
                    "statement_kind": statement.kind,
                    "source_digest": statement.source_digest,
                    "node_digest": statement.node_digest,
                }
                for key, value in expected.items():
                    self._expect(
                        boundary.get(key) == value,
                        "source_statement_boundary",
                        statement_ordinal=ordinal,
                        field=key,
                        expected=value,
                        actual=boundary.get(key),
                    )
            elif boundary is not None:
                self.fail("source_statement_executed_after_terminal", statement_ordinal=ordinal)

    def _validate_tracked_schema(self, receipt: Mapping[str, Any]) -> None:
        kind = str(receipt.get("kind"))
        self._strict_keys(
            receipt,
            _BASE_FIELDS | _PAYLOAD_FIELDS[kind],
            "tracked_receipt_schema",
            receipt_index=receipt.get("index"),
            kind=kind,
        )

    def _source_for_receipt(self, receipt: Mapping[str, Any]) -> _SourceStatement | None:
        index = receipt.get("index")
        owner = self.emitted_owner.get(index) if _is_int(index) else None
        if owner is None:
            self.fail("tracked_receipt_unbound", receipt_index=index, kind=receipt.get("kind"))
            return None
        ordinal = owner.get("statement_ordinal")
        if _is_int(ordinal):
            self.tracked_by_boundary.setdefault(int(ordinal), []).append(dict(receipt))
        statement = self.source_statements.get(ordinal) if _is_int(ordinal) else None
        kind = receipt.get("kind")
        if kind == "transaction_rollback" and receipt.get("automatic") is True:
            self._expect(owner.get("kind") == "statement_reject", "automatic_rollback_boundary", receipt_index=index)
            self._expect(owner.get("rolled_back") is True, "automatic_rollback_flag", receipt_index=index)
            return statement
        if statement is None:
            self.fail("tracked_receipt_source_statement", receipt_index=index, statement_ordinal=ordinal)
            return None
        self._expect(
            statement.expected_receipt == kind,
            "tracked_receipt_source_kind",
            receipt_index=index,
            expected=statement.expected_receipt,
            actual=kind,
        )
        self._expect(receipt.get("step") == owner.get("step"), "tracked_receipt_statement_step", receipt_index=index)
        return statement

    def _validate_session_payload(self, value: Any, context: str) -> dict[str, Any] | None:
        if not isinstance(value, Mapping):
            self.fail("session_payload_type", context=context)
            return None
        payload = _normal(value)
        self._strict_keys(payload, _SESSION_FIELDS, "session_payload_schema", context=context)
        self._expect(_is_ident(payload.get("name")), "session_payload_name", context=context)
        participants = payload.get("participants")
        self._expect(
            isinstance(participants, list)
            and len(participants) >= 2
            and len(participants) == len(set(participants))
            and all(_is_ident(item) for item in participants),
            "session_payload_participants",
            context=context,
        )
        self._expect(_is_ident(payload.get("initial_state")), "session_payload_initial", context=context)
        self._expect(
            payload.get("current_state") is None or _is_ident(payload.get("current_state")),
            "session_payload_current",
            context=context,
        )
        self._expect(isinstance(payload.get("active"), bool), "session_payload_active", context=context)
        terminals = payload.get("terminal_states")
        self._expect(
            isinstance(terminals, list)
            and terminals == sorted(set(terminals))
            and all(_is_ident(item) for item in terminals),
            "session_payload_terminals",
            context=context,
        )
        transitions = payload.get("transitions")
        if not isinstance(transitions, list):
            self.fail("session_payload_transitions", context=context)
        else:
            for position, transition in enumerate(transitions):
                if not isinstance(transition, Mapping):
                    self.fail("session_transition_type", context=context, position=position)
                    continue
                self._strict_keys(
                    transition,
                    _TRANSITION_FIELDS,
                    "session_transition_schema",
                    context=context,
                    position=position,
                )
                self._expect(
                    all(_is_ident(transition.get(key)) for key in _TRANSITION_FIELDS),
                    "session_transition_value",
                    context=context,
                    position=position,
                )
        history = payload.get("history")
        if not isinstance(history, list):
            self.fail("session_history_type", context=context)
        else:
            for position, event in enumerate(history):
                if not isinstance(event, Mapping):
                    self.fail("session_history_event_type", context=context, position=position)
                    continue
                expected = _START_HISTORY_FIELDS if event.get("event") == "start" else _ADVANCE_HISTORY_FIELDS
                self._strict_keys(
                    event,
                    expected,
                    "session_history_schema",
                    context=context,
                    position=position,
                )
        verification = payload.get("verification")
        if verification is not None:
            self._validate_verification_schema(verification, context)
        return payload

    def _validate_verification_schema(self, report: Any, context: str) -> dict[str, Any] | None:
        if not isinstance(report, Mapping):
            self.fail("session_verification_type", context=context)
            return None
        normalized = _normal(report)
        self._strict_keys(normalized, _VERIFICATION_FIELDS, "session_verification_schema", context=context)
        self._expect(normalized.get("schema") == REPORT_SCHEMA, "session_verification_version", context=context)
        for field_name in ("state_count", "transition_count"):
            self._expect(_is_int(normalized.get(field_name)), "session_verification_count", context=context, field=field_name)
        for field_name in (
            "terminal_states",
            "reachable_states",
            "unreachable_states",
            "reachable_deadlocks",
            "terminal_with_outgoing",
            "states_without_terminal_path",
        ):
            value = normalized.get(field_name)
            self._expect(
                isinstance(value, list) and value == sorted(set(value)) and all(_is_ident(item) for item in value),
                "session_verification_state_list",
                context=context,
                field=field_name,
            )
        for field_name in (
            "deterministic",
            "initial_declared",
            "terminal_declared",
            "all_reachable_states_can_terminate",
            "all_checks_pass",
        ):
            self._expect(isinstance(normalized.get(field_name), bool), "session_verification_boolean", context=context, field=field_name)
        self._expect(_is_sha256(normalized.get("report_digest")), "session_verification_digest", context=context)
        return normalized

    def _session_declare(self, receipt: Mapping[str, Any], statement: _SourceStatement | None) -> None:
        payload = self._validate_session_payload(receipt.get("session"), f"receipt:{receipt.get('index')}")
        if statement is None or payload is None:
            return
        args = statement.args
        expected = _Session(args["name"], tuple(args["participants"]), args["initial"]).canonical()
        self._expect(payload == expected, "session_declare_constructor", receipt_index=receipt.get("index"))
        self._expect(args["name"] not in self.sessions, "session_declare_unique", receipt_index=receipt.get("index"))
        if args["name"] not in self.sessions:
            self.sessions[args["name"]] = _Session(args["name"], tuple(args["participants"]), args["initial"])
            self.counts["declarations"] += 1

    def _session_transition(self, receipt: Mapping[str, Any], statement: _SourceStatement | None) -> None:
        if statement is None:
            return
        args = statement.args
        expected = {
            "session": args["session"],
            "source_state": args["source_state"],
            "event": "communicate",
            "sender": args["sender"],
            "receiver": args["receiver"],
            "target_state": args["target_state"],
        }
        for key, value in expected.items():
            self._expect(receipt.get(key) == value, "session_transition_source", receipt_index=receipt.get("index"), field=key)
        protocol = self.sessions.get(args["session"])
        if protocol is None:
            self.fail("session_transition_unknown", receipt_index=receipt.get("index"))
            return
        key = (args["source_state"], "communicate", args["sender"], args["receiver"])
        self._expect(key not in protocol.transitions, "session_transition_duplicate", receipt_index=receipt.get("index"))
        if key not in protocol.transitions:
            protocol.transitions[key] = args["target_state"]
            protocol.verification = None
            self.counts["transition_declarations"] += 1

    def _session_terminal(self, receipt: Mapping[str, Any], statement: _SourceStatement | None) -> None:
        if statement is None:
            return
        args = statement.args
        self._expect(receipt.get("session") == args["session"], "session_terminal_source", receipt_index=receipt.get("index"), field="session")
        self._expect(receipt.get("state") == args["state"], "session_terminal_source", receipt_index=receipt.get("index"), field="state")
        protocol = self.sessions.get(args["session"])
        if protocol is None:
            self.fail("session_terminal_unknown", receipt_index=receipt.get("index"))
            return
        protocol.terminal_states.add(args["state"])
        protocol.verification = None
        self.counts["terminal_declarations"] += 1

    def _session_verify(self, receipt: Mapping[str, Any], statement: _SourceStatement | None) -> None:
        report = self._validate_verification_schema(receipt.get("report"), f"receipt:{receipt.get('index')}")
        if statement is None:
            return
        protocol = self.sessions.get(statement.args["session"])
        if protocol is None:
            self.fail("session_verify_unknown", receipt_index=receipt.get("index"))
            return
        expected = _finite_verification(protocol)
        if report is not None:
            self._expect(report == expected, "session_verification_report", receipt_index=receipt.get("index"))
        protocol.verification = copy.deepcopy(expected)
        self.counts["finite_verifications"] += 1

    def _session_start(self, receipt: Mapping[str, Any], statement: _SourceStatement | None) -> None:
        payload = self._validate_session_payload(receipt.get("session"), f"receipt:{receipt.get('index')}")
        if statement is None:
            return
        protocol = self.sessions.get(statement.args["session"])
        if protocol is None:
            self.fail("session_start_unknown", receipt_index=receipt.get("index"))
            return
        legal = not protocol.active
        self._expect(legal, "session_start_inactive", receipt_index=receipt.get("index"))
        if protocol.terminal_states:
            verified = bool(protocol.verification and protocol.verification.get("all_checks_pass") is True)
            self._expect(verified, "session_start_verified", receipt_index=receipt.get("index"))
            legal = legal and verified
        if not legal:
            return
        protocol.active = True
        protocol.current_state = protocol.initial_state
        protocol.history.append({"step": receipt.get("step"), "event": "start", "state": protocol.initial_state})
        expected = protocol.canonical()
        if payload is not None:
            self._expect(payload == expected, "session_start_snapshot", receipt_index=receipt.get("index"))
        self.counts["starts"] += 1

    def _session_advance(self, receipt: Mapping[str, Any], statement: _SourceStatement | None) -> None:
        if statement is None:
            return
        args = statement.args
        expected_source = {
            "session": args["session"],
            "event": "communicate",
            "sender": args["source_agent"],
            "receiver": args["target_agent"],
        }
        for key, value in expected_source.items():
            self._expect(receipt.get(key) == value, "session_advance_source", receipt_index=receipt.get("index"), field=key)
        protocol = self.sessions.get(str(args["session"]))
        if protocol is None:
            self.fail("session_advance_unknown", receipt_index=receipt.get("index"))
            return
        legal = protocol.active and protocol.current_state is not None
        self._expect(legal, "session_advance_active", receipt_index=receipt.get("index"))
        participants = set(protocol.participants)
        self._expect(
            args["source_agent"] in participants and args["target_agent"] in participants,
            "session_advance_participants",
            receipt_index=receipt.get("index"),
        )
        key = (str(protocol.current_state), "communicate", args["source_agent"], args["target_agent"])
        target = protocol.transitions.get(key)
        self._expect(target is not None, "session_advance_transition", receipt_index=receipt.get("index"))
        if not legal or target is None:
            return
        source_state = protocol.current_state
        self._expect(receipt.get("source_state") == source_state, "session_advance_state", receipt_index=receipt.get("index"), field="source_state")
        self._expect(receipt.get("target_state") == target, "session_advance_state", receipt_index=receipt.get("index"), field="target_state")
        terminal = target in protocol.terminal_states
        protocol.current_state = target
        if terminal:
            protocol.active = False
        protocol.history.append(
            {
                "step": receipt.get("step"),
                "event": "communicate",
                "sender": args["source_agent"],
                "receiver": args["target_agent"],
                "from": source_state,
                "to": target,
                "terminal": terminal,
            }
        )
        self.counts["advances"] += 1

    def _transaction_begin(self, receipt: Mapping[str, Any], statement: _SourceStatement | None) -> None:
        name = None if statement is None else statement.args["name"]
        self._expect(name is not None and receipt.get("transaction") == name, "transaction_begin_source", receipt_index=receipt.get("index"))
        self._expect(self.active_transaction is None, "transaction_begin_nested", receipt_index=receipt.get("index"))
        self._expect(receipt.get("begin_audit_index") == receipt.get("index"), "transaction_begin_index", receipt_index=receipt.get("index"))
        self._expect(_is_sha256(receipt.get("checkpoint_digest")), "transaction_checkpoint_digest", receipt_index=receipt.get("index"))
        if name is not None and self.active_transaction is None:
            self.active_transaction = {
                "name": name,
                "begin_index": receipt.get("index"),
                "begin_step": receipt.get("step"),
                "checkpoint_digest": receipt.get("checkpoint_digest"),
                "sessions": copy.deepcopy(self.sessions),
            }
            self.counts["transaction_begins"] += 1

    def _validate_transaction_close(self, receipt: Mapping[str, Any]) -> bool:
        transaction = self.active_transaction
        index = receipt.get("index")
        if transaction is None:
            self.fail("transaction_close_without_begin", receipt_index=index)
            return False
        self._expect(receipt.get("transaction") == transaction["name"], "transaction_close_name", receipt_index=index)
        self._expect(receipt.get("begin_audit_index") == transaction["begin_index"], "transaction_close_begin_index", receipt_index=index)
        self._expect(receipt.get("begin_step") == transaction["begin_step"], "transaction_close_begin_step", receipt_index=index)
        span = receipt.get("body_effect_span")
        self._expect(
            isinstance(span, (list, tuple))
            and list(span) == [transaction["begin_index"] + 1, index],
            "transaction_body_span",
            receipt_index=index,
        )
        return True

    def _transaction_commit(self, receipt: Mapping[str, Any], statement: _SourceStatement | None) -> None:
        if statement is not None:
            self._expect(receipt.get("transaction") == statement.args["name"], "transaction_commit_source", receipt_index=receipt.get("index"))
        valid = self._validate_transaction_close(receipt)
        self._expect(_is_sha256(receipt.get("final_state_digest")), "transaction_final_digest", receipt_index=receipt.get("index"))
        if valid:
            self.active_transaction = None
            self.counts["transaction_commits"] += 1

    def _transaction_rollback(self, receipt: Mapping[str, Any], statement: _SourceStatement | None) -> None:
        automatic = receipt.get("automatic")
        self._expect(isinstance(automatic, bool), "transaction_rollback_automatic", receipt_index=receipt.get("index"))
        if automatic is False and statement is not None:
            self._expect(receipt.get("transaction") == statement.args["name"], "transaction_rollback_source", receipt_index=receipt.get("index"))
            self._expect(receipt.get("reason") == "explicit rollback", "transaction_rollback_reason", receipt_index=receipt.get("index"))
        valid = self._validate_transaction_close(receipt)
        transaction = self.active_transaction
        if transaction is not None:
            self._expect(receipt.get("checkpoint_digest") == transaction["checkpoint_digest"], "transaction_rollback_checkpoint", receipt_index=receipt.get("index"))
            self._expect(receipt.get("restored_state_digest") == transaction["checkpoint_digest"], "transaction_rollback_restored", receipt_index=receipt.get("index"))
            self._expect(receipt.get("discarded_receipt_count") == receipt.get("index") - transaction["begin_index"] - 1, "transaction_rollback_count", receipt_index=receipt.get("index"))
        self._expect(receipt.get("discarded_chain_tip") == receipt.get("previous_digest"), "transaction_rollback_chain_tip", receipt_index=receipt.get("index"))
        for key in ("pre_restore_digest", "checkpoint_digest", "restored_state_digest", "discarded_chain_tip"):
            self._expect(_is_sha256(receipt.get(key)), "transaction_rollback_digest", receipt_index=receipt.get("index"), field=key)
        self._expect(isinstance(receipt.get("reason"), str), "transaction_rollback_reason_type", receipt_index=receipt.get("index"))
        if valid and transaction is not None:
            self.sessions = copy.deepcopy(transaction["sessions"])
            self.active_transaction = None
            self.counts["transaction_rollbacks"] += 1

    def _process_receipts(self) -> None:
        handlers = {
            "session_declare": self._session_declare,
            "session_transition_declare": self._session_transition,
            "session_terminal_declare": self._session_terminal,
            "session_verify": self._session_verify,
            "session_start": self._session_start,
            "session_advance": self._session_advance,
            "transaction_begin": self._transaction_begin,
            "transaction_commit": self._transaction_commit,
            "transaction_rollback": self._transaction_rollback,
        }
        for receipt in self.receipts:
            if not isinstance(receipt, Mapping) or receipt.get("kind") not in _TRACKED_RECEIPT_KINDS:
                continue
            self._validate_tracked_schema(receipt)
            statement = self._source_for_receipt(receipt)
            kind = str(receipt.get("kind"))
            if kind.startswith("session_"):
                self.counts["session_receipts"] += 1
                transaction = None if self.active_transaction is None else self.active_transaction["name"]
                self._expect(receipt.get("transaction") == transaction, "session_transaction_context", receipt_index=receipt.get("index"))
            handlers[kind](receipt, statement)

        if self.active_transaction is not None:
            self.fail("transaction_unclosed", transaction=self.active_transaction["name"])

        for ordinal, statement in self.source_statements.items():
            boundary = self.boundaries.get(ordinal)
            if boundary is None:
                continue
            tracked = self.tracked_by_boundary.get(ordinal, [])
            matching = [
                receipt
                for receipt in tracked
                if receipt.get("kind") == statement.expected_receipt
                and not (receipt.get("kind") == "transaction_rollback" and receipt.get("automatic") is True)
            ]
            if boundary.get("kind") == "statement_commit" or statement.kind == "verify_session":
                self._expect(len(matching) == 1, "source_statement_effect_count", statement_ordinal=ordinal, actual=len(matching))
            else:
                self._expect(len(matching) <= 1, "source_statement_effect_count", statement_ordinal=ordinal, actual=len(matching))

    def _compare_final_state(self) -> None:
        terminal_states: Mapping[str, Any] | None = None
        terminals = [
            receipt
            for receipt in self.receipts
            if isinstance(receipt, Mapping) and receipt.get("kind") in {"program_complete", "program_reject"}
        ]
        if len(terminals) == 1:
            semantic = terminals[0].get("final_semantic_state")
            if isinstance(semantic, Mapping) and isinstance(semantic.get("sessions"), Mapping):
                terminal_states = semantic["sessions"]

        supplied_states: Mapping[str, Any] | None = None
        if self.final_state is not None:
            if isinstance(self.final_state, Mapping) and isinstance(self.final_state.get("sessions"), Mapping):
                supplied_states = self.final_state["sessions"]
            else:
                self.fail("final_state_sessions_missing")

        actual = supplied_states if supplied_states is not None else terminal_states
        if actual is None:
            self.fail("final_session_projection_missing")
            return
        if supplied_states is not None and terminal_states is not None:
            self._expect(
                _normal(supplied_states) == _normal(terminal_states),
                "terminal_final_session_projection",
            )

        normalized_actual = _normal(actual)
        if isinstance(normalized_actual, Mapping):
            for name, payload in normalized_actual.items():
                self._expect(_is_ident(name), "final_session_name", session=name)
                validated = self._validate_session_payload(payload, f"final:{name}")
                if validated is not None:
                    self._expect(validated.get("name") == name, "final_session_key", session=name)
        expected = {name: protocol.canonical() for name, protocol in sorted(self.sessions.items())}
        self._expect(normalized_actual == expected, "final_session_state", expected=expected, actual=normalized_actual)

    def verify(self) -> dict[str, Any]:
        try:
            self._parse_source()
            self._validate_chain()
            self._index_statement_boundaries()
            self._process_receipts()
            self._compare_final_state()
        except Exception as exc:  # fail closed on malformed adversarial input
            self.fail("session_verifier_internal_error", error_type=type(exc).__name__)

        reconstructed = {name: protocol.canonical() for name, protocol in sorted(self.sessions.items())}
        unsigned = {
            "schema": SEMANTIC_REPORT_SCHEMA,
            "all_checks_pass": not self.failures,
            "source_bound": not any(
                failure["property"].startswith("source_")
                or failure["property"].startswith("tracked_receipt_")
                for failure in self.failures
            ),
            "session_count": len(reconstructed),
            **self.counts,
            "reconstructed_sessions": reconstructed,
            "failure_count": len(self.failures),
            "failures": copy.deepcopy(self.failures),
        }
        return {**unsigned, "report_digest": digest(unsigned)}


def verify_session_semantics(
    source: str,
    receipts: Sequence[Mapping[str, Any]],
    final_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify and reconstruct session semantics without invoking the runtime."""

    try:
        return SessionSemanticVerifier(source, receipts, final_state).verify()
    except Exception as exc:  # constructor/input failures are also fail closed
        unsigned = {
            "schema": SEMANTIC_REPORT_SCHEMA,
            "all_checks_pass": False,
            "source_bound": False,
            "session_count": 0,
            "session_receipts": 0,
            "declarations": 0,
            "transition_declarations": 0,
            "terminal_declarations": 0,
            "finite_verifications": 0,
            "starts": 0,
            "advances": 0,
            "transaction_begins": 0,
            "transaction_commits": 0,
            "transaction_rollbacks": 0,
            "reconstructed_sessions": {},
            "failure_count": 1,
            "failures": [{"property": "session_verifier_input_error", "error_type": type(exc).__name__}],
        }
        return {**unsigned, "report_digest": digest(unsigned)}


__all__ = [
    "CORE_VERSION",
    "SUPPORTED_CORE_VERSIONS",
    "RECEIPT_SCHEMA",
    "REPORT_SCHEMA",
    "SEMANTIC_REPORT_SCHEMA",
    "SessionSemanticVerifier",
    "canonical_json",
    "digest",
    "verify_session_semantics",
]
