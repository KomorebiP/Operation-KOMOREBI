from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))

from osl_core import OSLRuntime, OSLError  # noqa: E402
from osl_information_flow import analyze_information_flow  # noqa: E402
from osl_metacore import build_report  # noqa: E402
from osl_model import verify_receipt_chain  # noqa: E402
from osl_parser import parse_and_check  # noqa: E402
from osl_session_verify import verify_session_protocol  # noqa: E402


def _linear_ownership_source(*, write_twice: bool = False) -> str:
    second = "write_memory e by A as observed requires own" if write_twice else ""
    return f'''
    module linear
    lineage LA
    agent A lineage LA
    observe e by A content "event" confidence 0.98
    proof pa access e by A
    proof po origin e source A lineage LA
    proof pc clear e for A
    proof pv observation e by A
    proof own ownership e by A as observed from ["pa","po","pc","pv"] mode linear
    write_memory e by A as observed requires own
    {second}
    '''


def test_linear_ownership_proof_is_consumed_exactly_once() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(_linear_ownership_source())
    proof = state.proofs["own"]
    assert proof.resource_mode == "linear"
    assert proof.remaining_uses == 0
    assert proof.consumed_step is not None


def test_linear_ownership_proof_cannot_be_reused() -> None:
    with pytest.raises(OSLError, match="stale or semantically invalid"):
        OSLRuntime().run_text(_linear_ownership_source(write_twice=True))


def test_unconsumed_linear_proof_rejects_program_completion() -> None:
    with pytest.raises(OSLError, match="linear proofs must be consumed exactly once"):
        OSLRuntime().run_text(
            '''
            module linear_unused
            lineage LA
            agent A lineage LA
            observe e by A content "event" confidence 0.98
            proof p access e by A mode linear
            '''
        )


def test_affine_use_proof_is_at_most_once_but_need_not_be_used() -> None:
    state = OSLRuntime().run_text(
        '''
        module affine_unused
        lineage LA
        agent A lineage LA
        observe e by A content "event" confidence 0.98
        proof p access e by A mode affine
        '''
    )
    assert state.proofs["p"].remaining_uses == 1


def test_append_only_receipt_chain_verifies_after_transaction_rollback() -> None:
    runtime = OSLRuntime()
    runtime.run_text(
        '''
        module receipt_chain
        lineage LA
        agent A lineage LA
        begin_transaction tx
        observe temp by A content "temp" confidence 0.9
        rollback_transaction tx
        verify_receipts
        '''
    )
    report = verify_receipt_chain(runtime.audit_log)
    assert report["all_checks_pass"]
    assert report["receipt_count"] == len(runtime.audit_log)
    assert any(item["kind"] == "transaction_rollback" for item in runtime.audit_log)


def test_receipt_chain_detects_tampering() -> None:
    runtime = OSLRuntime()
    runtime.run_text("module tamper\n")
    altered = copy.deepcopy(runtime.audit_log)
    altered[1]["kind"] = "forged"
    report = verify_receipt_chain(altered)
    assert not report["all_checks_pass"]
    assert any(item.startswith("digest:") for item in report["failed_checks"])


def test_verified_session_reaches_declared_terminal() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        '''
        module verified_session
        lineage LA
        lineage LB
        agent A lineage LA
        agent B lineage LB
        session S participants ["A","B"] initial waiting_A
        session_transition S waiting_A communicate A B -> waiting_B
        session_transition S waiting_B communicate B A -> ready
        session_terminal S ready
        verify_session S
        start_session S
        observe a by A content "a" confidence 0.9
        communicate a from A to B as aB in S
        observe b by B content "b" confidence 0.9
        communicate b from B to A as bA in S
        '''
    )
    session = state.sessions["S"]
    assert session.current_state == "ready"
    assert not session.active
    assert session.verification and session.verification["all_checks_pass"]


def test_session_verifier_rejects_reachable_deadlock() -> None:
    with pytest.raises(OSLError, match="reachable deadlocks"):
        OSLRuntime().run_text(
            '''
            module deadlock
            lineage LA
            lineage LB
            agent A lineage LA
            agent B lineage LB
            session S participants ["A","B"] initial waiting_A
            session_transition S waiting_A communicate A B -> waiting_B
            session_terminal S ready
            verify_session S
            '''
        )


def test_session_verifier_rejects_terminal_with_outgoing_transition() -> None:
    with pytest.raises(OSLError, match="terminal states with outgoing transitions"):
        OSLRuntime().run_text(
            '''
            module terminal_outgoing
            lineage LA
            lineage LB
            agent A lineage LA
            agent B lineage LB
            session S participants ["A","B"] initial waiting_A
            session_transition S waiting_A communicate A B -> ready
            session_transition S ready communicate B A -> waiting_A
            session_terminal S ready
            verify_session S
            '''
        )


def test_static_information_flow_distinguishes_safe_and_leaky_programs() -> None:
    safe, _ = parse_and_check(
        '''
        module safe
        secret private_goal value "alpha"
        metadata timestamp value 7 source trusted
        '''
    )
    leaky, _ = parse_and_check(
        '''
        module leaky
        secret private_goal value "alpha"
        metadata covert from_secret private_goal source agent
        '''
    )
    safe_report = analyze_information_flow(safe)
    leaky_report = analyze_information_flow(leaky)
    assert safe_report.noninterference_in_supported_fragment
    assert not leaky_report.noninterference_in_supported_fragment
    assert leaky_report.explicit_leak_count == 1


def test_finite_metatheory_certificate_passes_declared_checks() -> None:
    report = build_report()
    assert report["aggregate"]["all_checks_pass"]
    assert report["aggregate"]["reachable_state_count"] == 1590
    assert report["aggregate"]["transition_attempt_count"] == 28718
    assert all(not model["counterexamples"] for model in report["models"])
