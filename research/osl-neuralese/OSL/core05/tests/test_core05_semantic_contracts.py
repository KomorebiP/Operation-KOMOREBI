from __future__ import annotations

import copy
import sys
from pathlib import Path
from textwrap import dedent

import pytest


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))

from osl_core import OSLRuntime  # noqa: E402
from osl_model import OSLError  # noqa: E402
from osl_semantic_contracts import verify_contract_semantics  # noqa: E402


FEEDBACK_SOURCE = dedent(
    """
    module independent_feedback_contract
    lineage L_A
    agent A lineage L_A
    grant A effect externalAct
    contract feedback_required after execute require feedback within 3
    observe estimate by A content "candidate-value" confidence 0.92
    endorse estimate by A threshold 0.90
    authorize estimate by A for planning
    plan act by A using estimate effect externalAct expected 2.0
    execute act by A
    feedback act by A observed 2.2
    check_contracts
    assert contract feedback_required violations 0
    """
).strip() + "\n"


INVARIANT_SOURCE = dedent(
    """
    module independent_contract_invariants
    lineage L_A
    agent A lineage L_A
    contract no_foreign always no_foreign_observed
    contract no_simulated always no_simulated_observed
    contract no_quarantine_endorse always quarantine_blocks_endorsement
    contract capability_required always capability_confinement
    observe real_event by A content "real-event" confidence 0.97
    write_memory real_event by A as observed
    simulate imagined by A content "imagined-event" confidence 0.60
    write_memory imagined by A as simulated
    check_contracts
    assert contract no_foreign violations 0
    assert contract no_simulated violations 0
    assert contract no_quarantine_endorse violations 0
    assert contract capability_required violations 0
    """
).strip() + "\n"


VIOLATION_SOURCE = dedent(
    """
    module independent_feedback_violation
    lineage L_A
    agent A lineage L_A
    grant A effect externalAct
    contract feedback_required after execute require feedback within 2
    observe evidence by A content "action" confidence 0.95
    endorse evidence by A threshold 0.90
    authorize evidence by A for planning
    plan act by A using evidence effect externalAct
    execute act by A
    """
).strip() + "\n"


TRANSACTION_SOURCE = dedent(
    """
    module independent_contract_transaction
    lineage L_A
    agent A lineage L_A
    grant A effect externalAct
    contract feedback_required after execute require feedback within 5
    observe evidence by A content "action" confidence 0.95
    endorse evidence by A threshold 0.90
    authorize evidence by A for planning
    plan act by A using evidence effect externalAct
    execute act by A
    begin_transaction temporary_scope
    contract temporary always no_foreign_observed
    observe temporary_packet by A content "temporary" confidence 0.90
    rollback_transaction temporary_scope
    feedback act by A observed 1.0
    check_contracts
    """
).strip() + "\n"


AUTO_ROLLBACK_SOURCE = dedent(
    """
    module independent_contract_auto_rollback
    lineage L_A
    agent A lineage L_A
    grant A effect externalAct
    contract feedback_required after execute require feedback within 1
    observe evidence by A content "action" confidence 0.95
    endorse evidence by A threshold 0.90
    authorize evidence by A for planning
    plan act by A using evidence effect externalAct
    execute act by A
    begin_transaction deadline_scope
    show
    rollback_transaction deadline_scope
    """
).strip() + "\n"


def _accepted(source: str) -> tuple[list[dict], dict]:
    runtime = OSLRuntime()
    state = runtime.run_text(source)
    return copy.deepcopy(runtime.audit_log), state.snapshot()


def _rejected(source: str) -> tuple[list[dict], dict]:
    runtime = OSLRuntime()
    with pytest.raises(OSLError):
        runtime.run_text(source)
    return copy.deepcopy(runtime.audit_log), runtime.state.snapshot()


def _assert_rejected(report: dict) -> None:
    assert not report["all_checks_pass"], report
    assert report["failure_count"] > 0


def test_feedback_contract_is_reconstructed_without_runtime_replay() -> None:
    receipts, final_state = _accepted(FEEDBACK_SOURCE)

    report = verify_contract_semantics(FEEDBACK_SOURCE, receipts, final_state)

    assert report["all_checks_pass"], report
    assert report["independent"] is True
    assert report["counters"]["obligations_created"] == 1
    assert report["counters"]["obligations_discharged"] == 1
    assert report["reconstructed_contracts"]["feedback_required"]["pending"] == {}


def test_all_non_deadline_templates_are_checked() -> None:
    receipts, final_state = _accepted(INVARIANT_SOURCE)

    report = verify_contract_semantics(INVARIANT_SOURCE, receipts, final_state)

    assert report["all_checks_pass"], report
    assert set(report["reconstructed_contracts"]) == {
        "no_foreign",
        "no_simulated",
        "no_quarantine_endorse",
        "capability_required",
    }


def test_authentic_finalization_rejection_is_a_verified_contract_outcome() -> None:
    receipts, final_state = _rejected(VIOLATION_SOURCE)

    report = verify_contract_semantics(VIOLATION_SOURCE, receipts, final_state)

    assert report["all_checks_pass"], report
    assert report["counters"]["detected_violations"] == 1
    contract = report["reconstructed_contracts"]["feedback_required"]
    assert contract["pending"] == {"act": 12}
    assert contract["violations"] == ["action 'act' lacks feedback by step 12"]


def test_source_bound_declaration_rejects_consistently_tampered_deadline() -> None:
    receipts, final_state = _accepted(FEEDBACK_SOURCE)
    mutated = copy.deepcopy(receipts)
    declaration = next(item for item in mutated if item.get("kind") == "contract_declare")
    declaration["contract"]["within"] = 300
    terminal = mutated[-1]
    terminal["final_semantic_state"]["contracts"]["feedback_required"]["within"] = 300
    tampered_state = copy.deepcopy(final_state)
    tampered_state["contracts"]["feedback_required"]["within"] = 300

    report = verify_contract_semantics(FEEDBACK_SOURCE, mutated, tampered_state)

    _assert_rejected(report)
    assert any(
        failure["property"] == "contract_declaration_exact"
        for failure in report["failures"]
    )


def test_missing_feedback_event_cannot_be_hidden_by_empty_final_pending_state() -> None:
    receipts, final_state = _accepted(FEEDBACK_SOURCE)
    mutated = copy.deepcopy(receipts)
    feedback = next(item for item in mutated if item.get("kind") == "feedback")
    feedback["kind"] = "show"

    report = verify_contract_semantics(FEEDBACK_SOURCE, mutated, final_state)

    _assert_rejected(report)
    properties = {failure["property"] for failure in report["failures"]}
    assert "contract_statement_required_event" in properties
    assert "contract_final_violation_accepted" in properties
    assert "contract_final_state_exact" in properties


def test_contract_check_snapshot_is_not_decorative() -> None:
    receipts, final_state = _accepted(FEEDBACK_SOURCE)
    mutated = copy.deepcopy(receipts)
    check = next(item for item in mutated if item.get("kind") == "contract_check")
    check["contracts"]["feedback_required"]["pending"] = {"invented": 999}

    report = verify_contract_semantics(FEEDBACK_SOURCE, mutated, final_state)

    _assert_rejected(report)
    assert any(
        failure["property"] == "contract_check_exact"
        for failure in report["failures"]
    )


def test_final_contract_state_requires_exact_correspondence() -> None:
    receipts, final_state = _accepted(FEEDBACK_SOURCE)
    mutated_state = copy.deepcopy(final_state)
    mutated_state["contracts"]["feedback_required"]["violations"] = ["invented"]

    report = verify_contract_semantics(FEEDBACK_SOURCE, receipts, mutated_state)

    _assert_rejected(report)
    assert any(
        failure["property"] == "contract_final_state_exact"
        for failure in report["failures"]
    )


@pytest.mark.parametrize(
    ("mutator", "expected_property"),
    [
        (
            lambda receipts: next(
                item for item in receipts if item.get("kind") == "memory_write"
            )["record"].update(source_lineage="L_FORGED"),
            "contract_violation_was_committed",
        ),
        (
            lambda receipts: next(
                item for item in receipts if item.get("kind") == "observe"
            )["packet"].update(quarantined_by=["A"], endorsed_by=["A"]),
            "contract_violation_was_committed",
        ),
    ],
)
def test_invariant_receipt_mutations_are_detected(mutator, expected_property: str) -> None:
    receipts, final_state = _accepted(INVARIANT_SOURCE)
    mutated = copy.deepcopy(receipts)
    mutator(mutated)

    report = verify_contract_semantics(INVARIANT_SOURCE, mutated, final_state)

    _assert_rejected(report)
    assert any(
        failure["property"] == expected_property for failure in report["failures"]
    )


def test_capability_confinement_detects_forged_execute_action() -> None:
    source = FEEDBACK_SOURCE.replace(
        "contract feedback_required after execute require feedback within 3\n",
        "contract capability_required always capability_confinement\n"
        "contract feedback_required after execute require feedback within 3\n",
    )
    receipts, final_state = _accepted(source)
    mutated = copy.deepcopy(receipts)
    execute = next(item for item in mutated if item.get("kind") == "execute")
    execute["action"]["capability_digest"] = None

    report = verify_contract_semantics(source, mutated, final_state)

    _assert_rejected(report)
    assert any(
        failure["property"] == "contract_violation_was_committed"
        for failure in report["failures"]
    )


def test_transaction_rollback_restores_declarations_and_pending_obligations() -> None:
    receipts, final_state = _accepted(TRANSACTION_SOURCE)

    report = verify_contract_semantics(TRANSACTION_SOURCE, receipts, final_state)

    assert report["all_checks_pass"], report
    assert report["counters"]["transaction_begins"] == 1
    assert report["counters"]["transaction_rollbacks"] == 1
    assert set(report["reconstructed_contracts"]) == {"feedback_required"}
    assert report["reconstructed_contracts"]["feedback_required"]["pending"] == {}


def test_transaction_commit_retains_contract_declaration() -> None:
    source = TRANSACTION_SOURCE.replace(
        "rollback_transaction temporary_scope",
        "commit_transaction temporary_scope",
    )
    receipts, final_state = _accepted(source)

    report = verify_contract_semantics(source, receipts, final_state)

    assert report["all_checks_pass"], report
    assert report["counters"]["transaction_commits"] == 1
    assert set(report["reconstructed_contracts"]) == {
        "feedback_required",
        "temporary",
    }


def test_automatic_rollback_restores_pre_violation_contract_state() -> None:
    receipts, final_state = _rejected(AUTO_ROLLBACK_SOURCE)

    report = verify_contract_semantics(AUTO_ROLLBACK_SOURCE, receipts, final_state)

    assert report["all_checks_pass"], report
    assert report["counters"]["transaction_rollbacks"] == 1
    assert report["counters"]["detected_violations"] == 1
    contract = report["reconstructed_contracts"]["feedback_required"]
    assert contract["pending"] == {"act": 11}
    assert contract["violations"] == []


def test_rollback_cannot_be_relabelled_as_commit() -> None:
    receipts, final_state = _accepted(TRANSACTION_SOURCE)
    mutated = copy.deepcopy(receipts)
    rollback = next(item for item in mutated if item.get("kind") == "transaction_rollback")
    rollback["kind"] = "transaction_commit"

    report = verify_contract_semantics(TRANSACTION_SOURCE, mutated, final_state)

    _assert_rejected(report)
    properties = {failure["property"] for failure in report["failures"]}
    assert "contract_event_source_kind" in properties
    assert "contract_final_state_exact" in properties


def test_authentic_unknown_template_static_rejection_is_verified() -> None:
    source = "module bad_contract\ncontract c always unknown_template\n"
    receipts, final_state = _rejected(source)

    report = verify_contract_semantics(source, receipts, final_state)

    assert report["all_checks_pass"], report
    assert report["source_issues"][0]["property"] == "contract_unknown_template"


def test_malformed_input_fails_closed() -> None:
    report = verify_contract_semantics(FEEDBACK_SOURCE, [{"kind": "program_complete"}], {})

    _assert_rejected(report)
