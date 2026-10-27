from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference"))

from osl_semantic_sessions import (  # noqa: E402
    CORE_VERSION,
    RECEIPT_SCHEMA,
    ZERO_DIGEST,
    digest,
    verify_session_semantics,
)


def _records() -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for line in (ROOT / "CORE04_TRACE_BUNDLE.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        records[record["file"]] = record
    return records


def _rehash(receipts: list[dict[str, Any]]) -> None:
    previous = ZERO_DIGEST
    for receipt in receipts:
        receipt["previous_digest"] = previous
        if "preterminal_chain_tip" in receipt:
            receipt["preterminal_chain_tip"] = previous
        payload = copy.deepcopy(receipt)
        payload.pop("digest", None)
        receipt["digest"] = digest(payload)
        previous = receipt["digest"]


def _properties(report: dict[str, Any]) -> set[str]:
    return {failure["property"] for failure in report["failures"]}


def test_all_shipped_session_traces_reconstruct_independently() -> None:
    checked = 0
    for record in _records().values():
        if record["final_state"].get("sessions") or any(
            receipt["kind"].startswith("session_") for receipt in record["receipts"]
        ):
            report = verify_session_semantics(
                record["source"], record["receipts"], record["final_state"]
            )
            assert report["all_checks_pass"], (record["file"], report["failures"])
            assert report["source_bound"]
            checked += 1
    assert checked == 9


def test_verified_terminal_session_reconstructs_report_history_and_terminal_state() -> None:
    record = _records()["39_verified_terminal_session.osl"]
    report = verify_session_semantics(record["source"], record["receipts"], record["final_state"])
    assert report["all_checks_pass"]
    assert report["finite_verifications"] == 1
    assert report["starts"] == 1
    assert report["advances"] == 2
    session = report["reconstructed_sessions"]["S"]
    assert session["verification"]["all_checks_pass"] is True
    assert session["current_state"] == "ready"
    assert session["active"] is False
    assert session["history"][-1]["terminal"] is True


def test_rehashed_transition_mutation_is_rejected_by_source_binding() -> None:
    record = copy.deepcopy(_records()["39_verified_terminal_session.osl"])
    transition = next(
        receipt
        for receipt in record["receipts"]
        if receipt["kind"] == "session_transition_declare"
    )
    transition["target_state"] = "forged"
    _rehash(record["receipts"])
    report = verify_session_semantics(record["source"], record["receipts"], record["final_state"])
    assert not report["all_checks_pass"]
    assert "session_transition_source" in _properties(report)


def test_rehashed_finite_report_mutation_is_rejected_by_recomputation() -> None:
    record = copy.deepcopy(_records()["39_verified_terminal_session.osl"])
    verification = next(
        receipt for receipt in record["receipts"] if receipt["kind"] == "session_verify"
    )["report"]
    verification["reachable_states"] = ["ready", "waiting_A"]
    unsigned = copy.deepcopy(verification)
    unsigned.pop("report_digest")
    verification["report_digest"] = digest(unsigned)
    _rehash(record["receipts"])
    report = verify_session_semantics(record["source"], record["receipts"], record["final_state"])
    assert not report["all_checks_pass"]
    assert "session_verification_report" in _properties(report)


def test_rehashed_advance_mutation_is_rejected_by_small_step_semantics() -> None:
    record = copy.deepcopy(_records()["24_session_protocol.osl"])
    advance = next(
        receipt for receipt in record["receipts"] if receipt["kind"] == "session_advance"
    )
    advance["target_state"] = "ready"
    _rehash(record["receipts"])
    report = verify_session_semantics(record["source"], record["receipts"], record["final_state"])
    assert not report["all_checks_pass"]
    assert "session_advance_state" in _properties(report)


def test_strict_session_receipt_schema_rejects_extra_field_after_rehash() -> None:
    record = copy.deepcopy(_records()["24_session_protocol.osl"])
    declaration = next(
        receipt for receipt in record["receipts"] if receipt["kind"] == "session_declare"
    )
    declaration["decorative_claim"] = True
    _rehash(record["receipts"])
    report = verify_session_semantics(record["source"], record["receipts"], record["final_state"])
    assert not report["all_checks_pass"]
    assert "tracked_receipt_schema" in _properties(report)


def test_final_active_and_current_state_are_not_decorative() -> None:
    record = copy.deepcopy(_records()["39_verified_terminal_session.osl"])
    record["final_state"]["sessions"]["S"]["active"] = True
    record["final_state"]["sessions"]["S"]["current_state"] = "waiting_B"
    report = verify_session_semantics(record["source"], record["receipts"], record["final_state"])
    assert not report["all_checks_pass"]
    assert {"terminal_final_session_projection", "final_session_state"} <= _properties(report)


class _TraceBuilder:
    def __init__(self, close_kind: str) -> None:
        self.close_kind = close_kind
        close_line = "rollback_transaction T" if close_kind == "rollback" else "commit_transaction T"
        self.lines = [
            "module tx_session",
            "session S participants [\"A\",\"B\"] initial waiting_A",
            "session_transition S waiting_A communicate A B -> ready",
            "begin_transaction T",
            "start_session S",
            "communicate p from A to B as q in S",
            close_line,
        ]
        self.source = "\n".join(self.lines) + "\n"
        self.receipts: list[dict[str, Any]] = []
        self.previous = ZERO_DIGEST
        self.begin_index = -1
        self.begin_step = -1
        self.checkpoint_digest = "c" * 64
        self.session = {
            "name": "S",
            "participants": ["A", "B"],
            "initial_state": "waiting_A",
            "current_state": None,
            "active": False,
            "terminal_states": [],
            "verification": None,
            "transitions": [],
            "history": [],
        }

    def append(self, kind: str, step: int, transaction: str | None = None, **payload: Any) -> dict[str, Any]:
        receipt = {
            "schema": RECEIPT_SCHEMA,
            "core_version": CORE_VERSION,
            "index": len(self.receipts),
            "state_index": len(self.receipts),
            "step": step,
            "kind": kind,
            "transaction": transaction,
            "previous_digest": self.previous,
            **payload,
        }
        receipt["digest"] = digest(receipt)
        self.receipts.append(receipt)
        self.previous = receipt["digest"]
        return receipt

    @staticmethod
    def statement(line: str, ordinal: int) -> tuple[str, dict[str, Any]]:
        if line.startswith("module "):
            return "module", {"name": "tx_session"}
        if line.startswith("session S participants"):
            return "session", {"name": "S", "participants": ("A", "B"), "initial": "waiting_A"}
        if line.startswith("session_transition"):
            return "session_transition", {
                "session": "S",
                "source_state": "waiting_A",
                "sender": "A",
                "receiver": "B",
                "target_state": "ready",
            }
        if line == "begin_transaction T":
            return "begin_transaction", {"name": "T"}
        if line == "start_session S":
            return "start_session", {"session": "S"}
        if line.startswith("communicate"):
            return "communicate", {
                "source_packet": "p",
                "source_agent": "A",
                "target_agent": "B",
                "target_packet": "q",
                "session": "S",
            }
        return (
            "rollback_transaction" if line.startswith("rollback") else "commit_transaction",
            {"name": "T"},
        )

    def boundary(self, ordinal: int, step: int, start: int, transaction: str | None) -> None:
        line = self.lines[ordinal]
        kind, args = self.statement(line, ordinal)
        manifest = {
            "ordinal": ordinal,
            "line_number": ordinal + 1,
            "kind": kind,
            "source": line,
            "args": args,
        }
        node_digest = digest(manifest)
        self.append(
            "statement_commit",
            step,
            transaction,
            statement_ordinal=ordinal,
            line_number=ordinal + 1,
            statement_kind=kind,
            source_digest=digest(line),
            node_digest=node_digest,
            before_semantic_digest="a" * 64,
            after_semantic_digest="b" * 64,
            emitted_receipt_indices=list(range(start, len(self.receipts))),
            effect_span=[start, len(self.receipts)],
        )

    def build(self) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
        self.append(
            "program_open",
            0,
            filename="synthetic.osl",
            source_digest=digest(self.source),
            source_bytes=len(self.source.encode("utf-8")),
            source_lines=len(self.source.splitlines()),
        )
        self.append("parse_accept", 0, ast_digest="d" * 64, statement_count=len(self.lines))
        self.append("static_check", 0, ast_digest="d" * 64, report={})

        for ordinal, line in enumerate(self.lines):
            step = ordinal + 1
            start = len(self.receipts)
            transaction = "T" if self.begin_index >= 0 else None
            if line.startswith("session S participants"):
                self.append("session_declare", step, transaction, session=copy.deepcopy(self.session))
            elif line.startswith("session_transition"):
                transition = {
                    "from": "waiting_A",
                    "event": "communicate",
                    "sender": "A",
                    "receiver": "B",
                    "to": "ready",
                }
                self.session["transitions"] = [transition]
                self.append(
                    "session_transition_declare",
                    step,
                    transaction,
                    session="S",
                    source_state="waiting_A",
                    event="communicate",
                    sender="A",
                    receiver="B",
                    target_state="ready",
                )
            elif line == "begin_transaction T":
                self.begin_index = len(self.receipts)
                self.begin_step = step
                transaction = "T"
                self.append(
                    "transaction_begin",
                    step,
                    "T",
                    begin_audit_index=self.begin_index,
                    checkpoint_digest=self.checkpoint_digest,
                )
            elif line == "start_session S":
                self.session["active"] = True
                self.session["current_state"] = "waiting_A"
                self.session["history"].append({"step": step, "event": "start", "state": "waiting_A"})
                self.append("session_start", step, "T", session=copy.deepcopy(self.session))
            elif line.startswith("communicate"):
                self.session["current_state"] = "ready"
                self.session["history"].append(
                    {
                        "step": step,
                        "event": "communicate",
                        "sender": "A",
                        "receiver": "B",
                        "from": "waiting_A",
                        "to": "ready",
                        "terminal": False,
                    }
                )
                self.append(
                    "session_advance",
                    step,
                    "T",
                    session="S",
                    event="communicate",
                    sender="A",
                    receiver="B",
                    source_state="waiting_A",
                    target_state="ready",
                )
                self.append("communicate", step, "T", from_agent="A", to_agent="B", session="S", packet={})
            elif line == "rollback_transaction T":
                rollback_index = len(self.receipts)
                self.append(
                    "transaction_rollback",
                    step,
                    "T",
                    automatic=False,
                    reason="explicit rollback",
                    begin_audit_index=self.begin_index,
                    begin_step=self.begin_step,
                    checkpoint_digest=self.checkpoint_digest,
                    body_effect_span=[self.begin_index + 1, rollback_index],
                    pre_restore_digest="e" * 64,
                    discarded_chain_tip=self.previous,
                    discarded_receipt_count=rollback_index - self.begin_index - 1,
                    restored_state_digest=self.checkpoint_digest,
                )
                self.session["active"] = False
                self.session["current_state"] = None
                self.session["history"] = []
                transaction = None
            elif line == "commit_transaction T":
                commit_index = len(self.receipts)
                self.append(
                    "transaction_commit",
                    step,
                    "T",
                    begin_audit_index=self.begin_index,
                    begin_step=self.begin_step,
                    body_effect_span=[self.begin_index + 1, commit_index],
                    final_state_digest="f" * 64,
                )
                transaction = None
            self.boundary(ordinal, step, start, transaction)

        final_state = {"sessions": {"S": copy.deepcopy(self.session)}}
        self.append(
            "program_complete",
            len(self.lines),
            outcome="accepted",
            phase="complete",
            source_digest=digest(self.source),
            ast_digest="d" * 64,
            statement_count=len(self.lines),
            committed_count=len(self.lines),
            failed_ordinal=None,
            failed_line=None,
            failed_statement_kind=None,
            reason_code=None,
            error=None,
            final_semantic_state=copy.deepcopy(final_state),
            semantic_digest="1" * 64,
            preterminal_chain_tip=self.previous,
            audit_receipt_count=len(self.receipts) + 1,
        )
        return self.source, self.receipts, final_state


def test_transaction_rollback_restores_session_checkpoint() -> None:
    source, receipts, final_state = _TraceBuilder("rollback").build()
    report = verify_session_semantics(source, receipts, final_state)
    assert report["all_checks_pass"], report["failures"]
    assert report["transaction_rollbacks"] == 1
    session = report["reconstructed_sessions"]["S"]
    assert session["current_state"] is None
    assert session["active"] is False
    assert session["history"] == []


def test_transaction_commit_preserves_session_effects() -> None:
    source, receipts, final_state = _TraceBuilder("commit").build()
    report = verify_session_semantics(source, receipts, final_state)
    assert report["all_checks_pass"], report["failures"]
    assert report["transaction_commits"] == 1
    session = report["reconstructed_sessions"]["S"]
    assert session["current_state"] == "ready"
    assert session["active"] is True
    assert len(session["history"]) == 2


def test_transaction_rollback_flag_mutation_is_rejected_after_rehash() -> None:
    source, receipts, final_state = _TraceBuilder("rollback").build()
    rollback = next(receipt for receipt in receipts if receipt["kind"] == "transaction_rollback")
    rollback["automatic"] = True
    _rehash(receipts)
    report = verify_session_semantics(source, receipts, final_state)
    assert not report["all_checks_pass"]
    assert "automatic_rollback_boundary" in _properties(report)


def test_malformed_input_returns_a_fail_closed_report() -> None:
    report = verify_session_semantics("module malformed\n", [{"kind": "session_declare"}], {})
    assert report["all_checks_pass"] is False
    assert report["failure_count"] > 0
    assert len(report["report_digest"]) == 64
