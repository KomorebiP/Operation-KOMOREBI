#!/usr/bin/env python3
"""Independent temporal-contract semantics for OSL-Core 0.5.

This module deliberately does not import the OSL parser, data model, or
runtime.  It parses the small contract-facing source surface itself and treats
receipts and terminal state as untrusted evidence.  The verifier reconstructs
contract declarations, invariant checks, feedback obligations, and transaction
rollback from the receipt stream.

The result is finite executable assurance for the five currently declared
contract templates.  It is not a proof about arbitrary future templates and it
does not replace the independent lifecycle, provenance, or action verifiers.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any


REPORT_SCHEMA = "osl.core05.contract-semantics.v1"

CONTRACT_TEMPLATES = {
    "no_foreign_observed",
    "no_simulated_observed",
    "quarantine_blocks_endorsement",
    "capability_confinement",
    "feedback_deadline",
}

PACKET_RECEIPT_KINDS = {
    "observe",
    "infer",
    "simulate",
    "inject",
    "neural_proposal",
    "communicate",
    "bind",
    "quarantine",
    "endorse",
    "authorize",
    "neural_admission",
    "neural_rejection",
}

TERMINAL_KINDS = {"program_complete", "program_reject"}
BOUNDARY_KINDS = {"statement_commit", "statement_reject"}
IDENT = r"[A-Za-z_][\w-]*"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _strict_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass(frozen=True)
class _SourceStatement:
    ordinal: int
    line_number: int
    source: str
    kind: str
    args: dict[str, Any]


def _parse_source(source: str) -> tuple[list[_SourceStatement], list[dict[str, Any]]]:
    """Parse the contract-facing subset without importing the OSL parser."""

    statements: list[_SourceStatement] = []
    issues: list[dict[str, Any]] = []
    declared: set[str] = set()

    for line_number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        kind = line.split(None, 1)[0]
        args: dict[str, Any] = {}

        if match := re.fullmatch(rf"contract\s+({IDENT})\s+always\s+({IDENT})", line):
            kind = "contract"
            args = {
                "name": match.group(1),
                "template": match.group(2),
                "within": None,
            }
        elif match := re.fullmatch(
            rf"contract\s+({IDENT})\s+after\s+execute\s+require\s+feedback\s+within\s+(\d+)",
            line,
        ):
            kind = "contract"
            args = {
                "name": match.group(1),
                "template": "feedback_deadline",
                "within": int(match.group(2)),
            }
        elif line.startswith("contract "):
            kind = "contract_invalid"
            issues.append(
                {
                    "property": "contract_source_syntax",
                    "line_number": line_number,
                    "source": line,
                }
            )
        elif line == "check_contracts":
            kind = "check_contracts"
        elif match := re.fullmatch(rf"execute\s+({IDENT})\s+by\s+({IDENT})", line):
            kind = "execute"
            args = {"action": match.group(1), "agent": match.group(2)}
        elif match := re.fullmatch(
            rf"feedback\s+({IDENT})\s+by\s+({IDENT})\s+observed\s+(.+)", line
        ):
            kind = "feedback"
            args = {"action": match.group(1), "agent": match.group(2)}
        elif match := re.fullmatch(rf"agent\s+({IDENT})\s+lineage\s+({IDENT})", line):
            kind = "agent"
            args = {"name": match.group(1), "lineage": match.group(2)}
        elif match := re.fullmatch(rf"begin_transaction\s+({IDENT})", line):
            kind = "begin_transaction"
            args = {"name": match.group(1)}
        elif match := re.fullmatch(rf"commit_transaction\s+({IDENT})", line):
            kind = "commit_transaction"
            args = {"name": match.group(1)}
        elif match := re.fullmatch(rf"rollback_transaction\s+({IDENT})", line):
            kind = "rollback_transaction"
            args = {"name": match.group(1)}

        statement = _SourceStatement(
            ordinal=len(statements),
            line_number=line_number,
            source=line,
            kind=kind,
            args=args,
        )
        statements.append(statement)

        if kind != "contract":
            continue
        name = str(args["name"])
        template = str(args["template"])
        within = args["within"]
        if template not in CONTRACT_TEMPLATES:
            issues.append(
                {
                    "property": "contract_unknown_template",
                    "line_number": line_number,
                    "contract": name,
                    "template": template,
                }
            )
        if name in declared:
            issues.append(
                {
                    "property": "contract_duplicate_declaration",
                    "line_number": line_number,
                    "contract": name,
                }
            )
        declared.add(name)
        if template == "feedback_deadline" and (
            not _strict_int(within) or int(within) <= 0
        ):
            issues.append(
                {
                    "property": "contract_nonpositive_deadline",
                    "line_number": line_number,
                    "contract": name,
                    "within": within,
                }
            )

    return statements, issues


class ContractSemanticVerifier:
    """Reconstruct and verify the finite OSL contract state machine."""

    def __init__(self) -> None:
        self.failures: list[dict[str, Any]] = []
        self.contracts: dict[str, dict[str, Any]] = {}
        self.agents: dict[str, dict[str, Any]] = {}
        self.packets: dict[str, dict[str, Any]] = {}
        self.memories: dict[str, list[dict[str, Any]]] = {}
        self.actions: dict[str, dict[str, Any]] = {}
        self.transaction: dict[str, Any] | None = None
        self.detected_violations: list[dict[str, Any]] = []
        self.counters = {
            "contract_declarations": 0,
            "contract_checks": 0,
            "execute_events": 0,
            "feedback_events": 0,
            "obligations_created": 0,
            "obligations_discharged": 0,
            "transaction_begins": 0,
            "transaction_commits": 0,
            "transaction_rollbacks": 0,
            "semantic_checks": 0,
            "detected_violations": 0,
        }

    def _fail(self, property_name: str, **details: Any) -> None:
        self.failures.append({"property": property_name, **details})

    def _expect(self, condition: bool, property_name: str, **details: Any) -> None:
        if not condition:
            self._fail(property_name, **details)

    def _snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(
            {
                "contracts": self.contracts,
                "agents": self.agents,
                "packets": self.packets,
                "memories": self.memories,
                "actions": self.actions,
            }
        )

    def _restore(self, snapshot: dict[str, Any]) -> None:
        self.contracts = copy.deepcopy(snapshot["contracts"])
        self.agents = copy.deepcopy(snapshot["agents"])
        self.packets = copy.deepcopy(snapshot["packets"])
        self.memories = copy.deepcopy(snapshot["memories"])
        self.actions = copy.deepcopy(snapshot["actions"])

    def _contract_state(self) -> dict[str, dict[str, Any]]:
        return {name: copy.deepcopy(value) for name, value in sorted(self.contracts.items())}

    def _declare_contract(
        self,
        receipt: dict[str, Any],
        statement: _SourceStatement,
        receipt_index: int,
    ) -> None:
        observed = receipt.get("contract")
        expected = {
            "name": statement.args.get("name"),
            "template": statement.args.get("template"),
            "within": statement.args.get("within"),
            "pending": {},
            "violations": [],
            "declared_step": statement.ordinal + 1,
        }
        self._expect(
            observed == expected,
            "contract_declaration_exact",
            receipt_index=receipt_index,
            expected=expected,
            observed=observed,
        )
        if not isinstance(observed, dict):
            return
        name = observed.get("name")
        template = observed.get("template")
        self._expect(
            isinstance(name, str) and name not in self.contracts,
            "contract_declaration_unique",
            receipt_index=receipt_index,
            contract=name,
        )
        self._expect(
            template in CONTRACT_TEMPLATES,
            "contract_template_known",
            receipt_index=receipt_index,
            template=template,
        )
        if template == "feedback_deadline":
            within = observed.get("within")
            self._expect(
                _strict_int(within) and within > 0,
                "feedback_deadline_positive",
                receipt_index=receipt_index,
                within=within,
            )
        if isinstance(name, str) and name not in self.contracts:
            self.contracts[name] = copy.deepcopy(observed)
            self.counters["contract_declarations"] += 1

    def _apply_agent(
        self,
        receipt: dict[str, Any],
        statement: _SourceStatement,
        receipt_index: int,
    ) -> None:
        agent = receipt.get("agent")
        expected = {
            "name": statement.args.get("name"),
            "lineage": statement.args.get("lineage"),
        }
        self._expect(
            agent == expected,
            "contract_agent_source_correspondence",
            receipt_index=receipt_index,
            expected=expected,
            observed=agent,
        )
        if isinstance(agent, dict) and isinstance(agent.get("name"), str):
            self.agents[str(agent["name"])] = copy.deepcopy(agent)
            self.memories.setdefault(str(agent["name"]), [])

    def _apply_execute(
        self,
        receipt: dict[str, Any],
        statement: _SourceStatement,
        receipt_index: int,
    ) -> None:
        action = receipt.get("action")
        self._expect(
            isinstance(action, dict)
            and action.get("name") == statement.args.get("action")
            and action.get("agent") == statement.args.get("agent")
            and action.get("executed") is True
            and action.get("observed") is None,
            "contract_execute_source_correspondence",
            receipt_index=receipt_index,
            source_args=statement.args,
            action=action,
        )
        if not isinstance(action, dict) or not isinstance(action.get("name"), str):
            return
        name = str(action["name"])
        self.actions[name] = copy.deepcopy(action)
        for contract in self.contracts.values():
            if contract.get("template") != "feedback_deadline":
                continue
            within = contract.get("within")
            if not _strict_int(within):
                continue
            contract.setdefault("pending", {})[name] = int(receipt.get("step")) + within
            self.counters["obligations_created"] += 1
        self.counters["execute_events"] += 1

    def _apply_feedback(
        self,
        receipt: dict[str, Any],
        statement: _SourceStatement,
        receipt_index: int,
    ) -> None:
        action = receipt.get("action")
        self._expect(
            isinstance(action, dict)
            and action.get("name") == statement.args.get("action")
            and action.get("agent") == statement.args.get("agent")
            and action.get("executed") is True
            and action.get("observed") is not None,
            "contract_feedback_source_correspondence",
            receipt_index=receipt_index,
            source_args=statement.args,
            action=action,
        )
        if not isinstance(action, dict) or not isinstance(action.get("name"), str):
            return
        name = str(action["name"])
        self.actions[name] = copy.deepcopy(action)
        for contract in self.contracts.values():
            pending = contract.get("pending")
            if contract.get("template") == "feedback_deadline" and isinstance(pending, dict):
                if name in pending:
                    self.counters["obligations_discharged"] += 1
                pending.pop(name, None)
        self.counters["feedback_events"] += 1

    def _first_violation(self, *, step: int, final: bool) -> tuple[str, str] | None:
        """Return the first runtime-ordered violation without mutating state."""

        self.counters["semantic_checks"] += 1
        for name, contract in self.contracts.items():
            template = contract.get("template")
            if template == "no_foreign_observed":
                for agent_name, records in self.memories.items():
                    lineage = self.agents.get(agent_name, {}).get("lineage")
                    for record in records:
                        if record.get("memory_class") == "observed" and (
                            record.get("source_agent") != agent_name
                            or record.get("source_lineage") != lineage
                        ):
                            return (
                                name,
                                f"foreign record {record.get('packet_name')!r} "
                                f"written as observed by {agent_name}",
                            )
            elif template == "no_simulated_observed":
                for agent_name, records in self.memories.items():
                    for record in records:
                        packet = self.packets.get(str(record.get("packet_name")))
                        if (
                            record.get("memory_class") == "observed"
                            and packet is not None
                            and (
                                packet.get("simulated") is True
                                or packet.get("provenance") == "simulated"
                            )
                        ):
                            return (
                                name,
                                f"simulated packet {record.get('packet_name')!r} "
                                f"written as observed by {agent_name}",
                            )
            elif template == "quarantine_blocks_endorsement":
                for packet_name, packet in self.packets.items():
                    quarantined = packet.get("quarantined_by", [])
                    endorsed = packet.get("endorsed_by", [])
                    if not isinstance(quarantined, list) or not isinstance(endorsed, list):
                        continue
                    overlap = sorted(set(quarantined) & set(endorsed))
                    if overlap:
                        return (
                            name,
                            f"packet {packet_name!r} is both quarantined and "
                            f"endorsed by {overlap}",
                        )
            elif template == "capability_confinement":
                for action_name, action in self.actions.items():
                    if action.get("executed") is True and action.get("capability_digest") is None:
                        return (
                            name,
                            f"executed action {action_name!r} lacks a capability receipt",
                        )
            elif template == "feedback_deadline":
                pending = contract.get("pending", {})
                if not isinstance(pending, dict):
                    continue
                for action_name, due in sorted(pending.items()):
                    if _strict_int(due) and (final or step > due):
                        return (
                            name,
                            f"action {action_name!r} lacks feedback by step {due}",
                        )
        return None

    def _record_violation(
        self,
        violation: tuple[str, str],
        *,
        step: int,
        final: bool,
    ) -> str:
        name, message = violation
        contract = self.contracts.get(name)
        if contract is not None:
            violations = contract.setdefault("violations", [])
            if isinstance(violations, list) and message not in violations:
                violations.append(message)
        self.detected_violations.append(
            {"contract": name, "message": message, "step": step, "final": final}
        )
        self.counters["detected_violations"] += 1
        return f"contract {name!r} violated: {message}"

    @staticmethod
    def _is_contract_error(error: Any) -> bool:
        return isinstance(error, str) and "contract '" in error and " violated: " in error

    def _apply_receipt(
        self,
        receipt: dict[str, Any],
        statement: _SourceStatement,
        receipt_index: int,
        *,
        boundary_contract_error: bool,
    ) -> tuple[str, str] | None:
        """Apply one receipt and return an automatic-rollback error and tx name."""

        kind = receipt.get("kind")
        self._expect(
            receipt.get("step") == statement.ordinal + 1,
            "contract_event_step",
            receipt_index=receipt_index,
            expected=statement.ordinal + 1,
            observed=receipt.get("step"),
        )

        if kind == "agent_declare":
            self._apply_agent(receipt, statement, receipt_index)
        elif kind == "contract_declare":
            self._declare_contract(receipt, statement, receipt_index)
        elif kind == "contract_check":
            observed = receipt.get("contracts")
            expected = self._contract_state()
            self._expect(
                observed == expected,
                "contract_check_exact",
                receipt_index=receipt_index,
                expected=expected,
                observed=observed,
            )
            self.counters["contract_checks"] += 1
        elif kind == "plan":
            action = receipt.get("action")
            if isinstance(action, dict) and isinstance(action.get("name"), str):
                self.actions[str(action["name"])] = copy.deepcopy(action)
        elif kind == "execute":
            self._apply_execute(receipt, statement, receipt_index)
        elif kind == "feedback":
            self._apply_feedback(receipt, statement, receipt_index)
        elif kind == "memory_write":
            record = receipt.get("record")
            if isinstance(record, dict) and isinstance(record.get("agent"), str):
                agent = str(record["agent"])
                self.memories.setdefault(agent, []).append(copy.deepcopy(record))
        elif kind in PACKET_RECEIPT_KINDS:
            packet = receipt.get("packet")
            if isinstance(packet, dict) and isinstance(packet.get("name"), str):
                self.packets[str(packet["name"])] = copy.deepcopy(packet)
        elif kind == "transaction_begin":
            self._expect(
                self.transaction is None,
                "contract_transaction_not_nested",
                receipt_index=receipt_index,
            )
            expected_name = statement.args.get("name")
            self._expect(
                statement.kind == "begin_transaction"
                and receipt.get("transaction") == expected_name,
                "contract_transaction_begin_source_correspondence",
                receipt_index=receipt_index,
                expected=expected_name,
                observed=receipt.get("transaction"),
            )
            self.transaction = {
                "name": receipt.get("transaction"),
                "snapshot": self._snapshot(),
            }
            self.counters["transaction_begins"] += 1
        elif kind == "transaction_commit":
            active_name = None if self.transaction is None else self.transaction.get("name")
            self._expect(
                self.transaction is not None and receipt.get("transaction") == active_name,
                "contract_transaction_commit_active",
                receipt_index=receipt_index,
                active=active_name,
                observed=receipt.get("transaction"),
            )
            if statement.kind == "commit_transaction":
                self._expect(
                    statement.args.get("name") == receipt.get("transaction"),
                    "contract_transaction_commit_source_correspondence",
                    receipt_index=receipt_index,
                )
            self.transaction = None
            self.counters["transaction_commits"] += 1
        elif kind == "transaction_rollback":
            active_name = None if self.transaction is None else self.transaction.get("name")
            self._expect(
                self.transaction is not None and receipt.get("transaction") == active_name,
                "contract_transaction_rollback_active",
                receipt_index=receipt_index,
                active=active_name,
                observed=receipt.get("transaction"),
            )
            pre_restore_error: str | None = None
            if boundary_contract_error and receipt.get("automatic") is True:
                violation = self._first_violation(step=statement.ordinal + 1, final=False)
                if violation is not None:
                    pre_restore_error = self._record_violation(
                        violation, step=statement.ordinal + 1, final=False
                    )
            if self.transaction is not None:
                snapshot = self.transaction.get("snapshot")
                if isinstance(snapshot, dict):
                    self._restore(snapshot)
            if receipt.get("automatic") is False:
                self._expect(
                    statement.kind == "rollback_transaction"
                    and statement.args.get("name") == receipt.get("transaction"),
                    "contract_transaction_rollback_source_correspondence",
                    receipt_index=receipt_index,
                )
            self.transaction = None
            self.counters["transaction_rollbacks"] += 1
            if pre_restore_error is not None:
                return pre_restore_error, str(active_name)
            return None
        return None

    def _validate_event_owner(
        self,
        kind: str,
        statement: _SourceStatement,
        receipt_index: int,
        receipt: dict[str, Any],
    ) -> None:
        expected_source_kind = {
            "agent_declare": "agent",
            "contract_declare": "contract",
            "contract_check": "check_contracts",
            "execute": "execute",
            "feedback": "feedback",
            "transaction_begin": "begin_transaction",
            "transaction_commit": "commit_transaction",
        }.get(kind)
        if expected_source_kind is not None:
            self._expect(
                statement.kind == expected_source_kind,
                "contract_event_source_kind",
                receipt_index=receipt_index,
                receipt_kind=kind,
                expected_source_kind=expected_source_kind,
                observed_source_kind=statement.kind,
            )
        if kind == "transaction_rollback" and receipt.get("automatic") is not True:
            self._expect(
                statement.kind == "rollback_transaction",
                "contract_event_source_kind",
                receipt_index=receipt_index,
                receipt_kind=kind,
                expected_source_kind="rollback_transaction",
                observed_source_kind=statement.kind,
            )

    def _check_required_event(
        self,
        statement: _SourceStatement,
        boundary: dict[str, Any],
        events: list[tuple[int, dict[str, Any]]],
    ) -> None:
        required = {
            "agent": "agent_declare",
            "contract": "contract_declare",
            "check_contracts": "contract_check",
            "execute": "execute",
            "feedback": "feedback",
            "begin_transaction": "transaction_begin",
            "commit_transaction": "transaction_commit",
            "rollback_transaction": "transaction_rollback",
        }.get(statement.kind)
        if required is None:
            return
        count = sum(
            receipt.get("kind") == required
            and (
                required != "transaction_rollback"
                or receipt.get("automatic") is not True
            )
            for _, receipt in events
        )
        if boundary.get("kind") == "statement_commit":
            self._expect(
                count == 1,
                "contract_statement_required_event",
                statement_ordinal=statement.ordinal,
                statement_kind=statement.kind,
                receipt_kind=required,
                count=count,
            )
        else:
            self._expect(
                count <= 1,
                "contract_statement_event_multiplicity",
                statement_ordinal=statement.ordinal,
                receipt_kind=required,
                count=count,
            )

    def _verify_strict(
        self,
        source: str,
        receipts: list[dict[str, Any]],
        final_state: dict[str, Any] | None,
    ) -> dict[str, Any]:
        statements, source_issues = _parse_source(source)
        records = copy.deepcopy(receipts)
        self._expect(bool(records), "contract_evidence_nonempty")
        self._expect(
            all(isinstance(receipt, dict) for receipt in records),
            "contract_receipts_are_objects",
        )
        if not records or not all(isinstance(receipt, dict) for receipt in records):
            return self._report(source, records, final_state)

        terminals = [
            (index, receipt)
            for index, receipt in enumerate(records)
            if receipt.get("kind") in TERMINAL_KINDS
        ]
        self._expect(len(terminals) == 1, "contract_terminal_exactly_one", count=len(terminals))
        terminal = terminals[0][1] if len(terminals) == 1 else {}
        terminal_index = terminals[0][0] if len(terminals) == 1 else -1
        if terminal_index >= 0:
            self._expect(
                terminal_index == len(records) - 1,
                "contract_terminal_last",
                terminal_index=terminal_index,
                receipt_count=len(records),
            )

        boundaries: list[tuple[int, dict[str, Any], _SourceStatement, list[tuple[int, dict[str, Any]]]]] = []
        owned_indices: dict[int, int] = {}
        expected_ordinal = 0
        for boundary_index, boundary in enumerate(records):
            if boundary.get("kind") not in BOUNDARY_KINDS:
                continue
            ordinal = boundary.get("statement_ordinal")
            if not _strict_int(ordinal) or not (0 <= ordinal < len(statements)):
                self._fail(
                    "contract_boundary_ordinal",
                    receipt_index=boundary_index,
                    ordinal=ordinal,
                )
                continue
            statement = statements[ordinal]
            self._expect(
                ordinal == expected_ordinal,
                "contract_boundary_sequence",
                receipt_index=boundary_index,
                expected=expected_ordinal,
                observed=ordinal,
            )
            expected_ordinal = ordinal + 1
            self._expect(
                boundary.get("line_number") == statement.line_number
                and boundary.get("source_digest") == _digest(statement.source)
                and boundary.get("step") == ordinal + 1,
                "contract_boundary_source_correspondence",
                receipt_index=boundary_index,
                statement_ordinal=ordinal,
            )
            if statement.kind in {
                "agent",
                "contract",
                "check_contracts",
                "execute",
                "feedback",
                "begin_transaction",
                "commit_transaction",
                "rollback_transaction",
            }:
                self._expect(
                    boundary.get("statement_kind") == statement.kind,
                    "contract_boundary_statement_kind",
                    receipt_index=boundary_index,
                    expected=statement.kind,
                    observed=boundary.get("statement_kind"),
                )

            span = boundary.get("effect_span")
            emitted = boundary.get("emitted_receipt_indices")
            if (
                not isinstance(span, (list, tuple))
                or len(span) != 2
                or not all(_strict_int(item) for item in span)
            ):
                self._fail("contract_boundary_effect_span", receipt_index=boundary_index, span=span)
                events: list[tuple[int, dict[str, Any]]] = []
            else:
                start, end = int(span[0]), int(span[1])
                self._expect(
                    0 <= start <= end == boundary_index,
                    "contract_boundary_effect_span",
                    receipt_index=boundary_index,
                    span=list(span),
                )
                expected_emitted = list(range(start, end))
                self._expect(
                    list(emitted) == expected_emitted
                    if isinstance(emitted, (list, tuple))
                    else False,
                    "contract_boundary_emitted_indices",
                    receipt_index=boundary_index,
                    expected=expected_emitted,
                    observed=emitted,
                )
                events = [
                    (index, records[index])
                    for index in range(max(0, start), min(end, len(records)))
                ]
                for event_index, _event in events:
                    self._expect(
                        event_index not in owned_indices,
                        "contract_effect_span_disjoint",
                        receipt_index=event_index,
                        prior_owner=owned_indices.get(event_index),
                        owner=ordinal,
                    )
                    owned_indices[event_index] = ordinal
            boundaries.append((boundary_index, boundary, statement, events))

        relevant_kinds = (
            PACKET_RECEIPT_KINDS
            | {
                "agent_declare",
                "memory_write",
                "plan",
                "execute",
                "feedback",
                "contract_declare",
                "contract_check",
                "transaction_begin",
                "transaction_commit",
                "transaction_rollback",
            }
        )
        for index, receipt in enumerate(records):
            if receipt.get("kind") in relevant_kinds:
                self._expect(
                    index in owned_indices,
                    "contract_event_has_statement_owner",
                    receipt_index=index,
                    kind=receipt.get("kind"),
                )

        source_has_contract_issue = bool(source_issues)
        if source_has_contract_issue:
            expected_phase = (
                "parse"
                if any(
                    issue.get("property") == "contract_source_syntax"
                    for issue in source_issues
                )
                else "static"
            )
            self._expect(
                terminal.get("kind") == "program_reject"
                and terminal.get("phase") == expected_phase,
                "contract_source_issue_rejected_in_phase",
                expected_phase=expected_phase,
                terminal_kind=terminal.get("kind"),
                terminal_phase=terminal.get("phase"),
                source_issues=source_issues,
            )
        if terminal.get("phase") in {"parse", "static"}:
            self._expect(
                not any(
                    receipt.get("kind") in {"contract_declare", "contract_check"}
                    for receipt in records
                ),
                "contract_rejected_source_has_no_contract_effects",
            )

        for _boundary_index, boundary, statement, events in boundaries:
            boundary_error = boundary.get("error")
            boundary_contract_error = self._is_contract_error(boundary_error)
            self._check_required_event(statement, boundary, events)
            pre_restore: tuple[str, str] | None = None
            for event_index, receipt in events:
                kind = str(receipt.get("kind"))
                if kind in relevant_kinds:
                    self._validate_event_owner(kind, statement, event_index, receipt)
                    rollback_result = self._apply_receipt(
                        receipt,
                        statement,
                        event_index,
                        boundary_contract_error=boundary_contract_error,
                    )
                    if rollback_result is not None:
                        pre_restore = rollback_result

            if boundary.get("kind") == "statement_commit":
                violation = self._first_violation(step=statement.ordinal + 1, final=False)
                if violation is not None:
                    error = self._record_violation(
                        violation, step=statement.ordinal + 1, final=False
                    )
                    self._fail(
                        "contract_violation_was_committed",
                        statement_ordinal=statement.ordinal,
                        error=error,
                    )
            elif boundary_contract_error:
                expected_error = None if pre_restore is None else pre_restore[0]
                if expected_error is None:
                    violation = self._first_violation(step=statement.ordinal + 1, final=False)
                    if violation is not None:
                        expected_error = self._record_violation(
                            violation, step=statement.ordinal + 1, final=False
                        )
                self._expect(
                    expected_error is not None,
                    "contract_statement_rejection_has_violation",
                    statement_ordinal=statement.ordinal,
                    observed_error=boundary_error,
                )
                if expected_error is not None:
                    expected_plain = f"line {statement.line_number}: {expected_error}"
                    if pre_restore is not None:
                        active_tx_name = pre_restore[1]
                        expected_plain = (
                            f"line {statement.line_number}: transaction {active_tx_name!r} rolled back: "
                            f"line {statement.line_number}: {expected_error}"
                        )
                    self._expect(
                        boundary_error == expected_plain,
                        "contract_statement_rejection_error",
                        statement_ordinal=statement.ordinal,
                        expected=expected_plain,
                        observed=boundary_error,
                    )

        if terminal.get("kind") == "program_complete":
            final_step = terminal.get("step")
            if _strict_int(final_step):
                violation = self._first_violation(step=final_step, final=True)
                if violation is not None:
                    error = self._record_violation(violation, step=final_step, final=True)
                    self._fail("contract_final_violation_accepted", error=error)
        elif (
            terminal.get("kind") == "program_reject"
            and terminal.get("phase") == "finalization"
            and self._is_contract_error(terminal.get("error"))
        ):
            final_step = terminal.get("step")
            violation = (
                self._first_violation(step=final_step, final=True)
                if _strict_int(final_step)
                else None
            )
            self._expect(
                violation is not None,
                "contract_final_rejection_has_violation",
                observed_error=terminal.get("error"),
            )
            if violation is not None:
                error = self._record_violation(violation, step=final_step, final=True)
                last_line = statements[-1].line_number if statements else 0
                expected = f"line {last_line}: {error}"
                self._expect(
                    terminal.get("error") == expected,
                    "contract_final_rejection_error",
                    expected=expected,
                    observed=terminal.get("error"),
                )

        self._expect(
            self.transaction is None,
            "contract_transactions_closed",
            active=None if self.transaction is None else self.transaction.get("name"),
        )

        expected_contracts = self._contract_state()
        terminal_state = terminal.get("final_semantic_state")
        if isinstance(terminal_state, dict):
            self._expect(
                terminal_state.get("contracts") == expected_contracts,
                "contract_terminal_state_exact",
                expected=expected_contracts,
                observed=terminal_state.get("contracts"),
            )
        else:
            self._fail("contract_terminal_semantic_state", observed=terminal_state)
        if final_state is not None:
            self._expect(
                isinstance(final_state, dict)
                and final_state.get("contracts") == expected_contracts,
                "contract_final_state_exact",
                expected=expected_contracts,
                observed=(
                    final_state.get("contracts") if isinstance(final_state, dict) else final_state
                ),
            )

        return self._report(source, records, final_state, source_issues=source_issues)

    def _report(
        self,
        source: str,
        receipts: list[dict[str, Any]],
        final_state: dict[str, Any] | None,
        *,
        source_issues: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        failure_properties = {failure.get("property") for failure in self.failures}
        categories = {
            "source_and_boundaries": {
                name
                for name in failure_properties
                if isinstance(name, str)
                and (
                    "source" in name
                    or "boundary" in name
                    or "statement_required" in name
                    or "statement_event" in name
                    or "effect_span" in name
                )
            },
            "declarations": {
                name
                for name in failure_properties
                if isinstance(name, str)
                and ("declaration" in name or "template" in name or "deadline_positive" in name)
            },
            "template_invariants": {
                name
                for name in failure_properties
                if isinstance(name, str) and "violation" in name
            },
            "feedback_obligations": {
                name
                for name in failure_properties
                if isinstance(name, str)
                and ("execute" in name or "feedback" in name or "final_rejection" in name)
            },
            "transactions": {
                name
                for name in failure_properties
                if isinstance(name, str) and "transaction" in name
            },
            "check_receipts": {
                name
                for name in failure_properties
                if isinstance(name, str) and "contract_check" in name
            },
            "final_state": {
                name
                for name in failure_properties
                if isinstance(name, str) and ("final_state" in name or "terminal_state" in name)
            },
        }
        checks = {
            name: not any(property_name in properties for property_name in failure_properties)
            for name, properties in categories.items()
        }
        payload: dict[str, Any] = {
            "schema": REPORT_SCHEMA,
            "independent": True,
            "source_bound": True,
            "checks": checks,
            "all_checks_pass": not self.failures,
            "failure_count": len(self.failures),
            "failures": copy.deepcopy(self.failures),
            "counters": copy.deepcopy(self.counters),
            "source_statement_count": len(_parse_source(source)[0]),
            "source_issues": copy.deepcopy(source_issues or []),
            "reconstructed_contracts": self._contract_state(),
            "detected_contract_violations": copy.deepcopy(self.detected_violations),
            "receipt_count": len(receipts),
            "final_state_compared": final_state is not None,
            "claim_boundary": (
                "Independent finite reconstruction covers the five declared OSL "
                "contract templates, feedback deadlines, contract-check snapshots, "
                "and contract-relevant transaction rollback. It consumes receipt "
                "events for agent, packet, memory, action, and capability fields but "
                "does not independently prove the complete semantics that produced "
                "those events. It imports and replays no OSL runtime."
            ),
        }
        payload["verification_digest"] = _digest(payload)
        return payload

    def verify(
        self,
        source: str,
        receipts: list[dict[str, Any]],
        final_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Fail closed on malformed inputs and never propagate verifier errors."""

        try:
            if not isinstance(source, str):
                raise TypeError("source must be a string")
            if not isinstance(receipts, list):
                raise TypeError("receipts must be a list")
            if final_state is not None and not isinstance(final_state, dict):
                raise TypeError("final_state must be an object when provided")
            return self._verify_strict(source, receipts, final_state)
        except Exception as exc:
            self._fail(
                "contract_malformed_verifier_input",
                error_type=type(exc).__name__,
                error=str(exc),
            )
            try:
                safe_source = source if isinstance(source, str) else ""
                safe_receipts = receipts if isinstance(receipts, list) else []
                safe_final = final_state if isinstance(final_state, dict) else None
                return self._report(safe_source, safe_receipts, safe_final)
            except Exception:
                return {
                    "schema": REPORT_SCHEMA,
                    "independent": True,
                    "source_bound": isinstance(source, str),
                    "checks": {},
                    "all_checks_pass": False,
                    "failure_count": 1,
                    "failures": [{"property": "contract_malformed_verifier_input"}],
                }


def verify_contract_semantics(
    source: str,
    receipts: list[dict[str, Any]],
    final_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify OSL temporal-contract semantics without importing the runtime."""

    return ContractSemanticVerifier().verify(source, receipts, final_state)


__all__ = ["ContractSemanticVerifier", "verify_contract_semantics"]
