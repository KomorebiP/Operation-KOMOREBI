from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))

from audit_noninterference import audit  # noqa: E402
from osl_core import OSLRuntime, OSLError, run_program  # noqa: E402
from osl_model import OSLStaticError  # noqa: E402
from osl_parser import parse_and_check  # noqa: E402


def test_static_ast_and_report_are_deterministic() -> None:
    source = """
    module static
    lineage LA
    agent A lineage LA
    observe e by A content "event" confidence 0.9
    """
    first_statements, first_report = parse_and_check(source)
    second_statements, second_report = parse_and_check(source)
    assert first_statements == second_statements
    assert first_report == second_report
    assert first_report.statement_count == 4
    assert first_report.symbol_counts["packets"] == 1


def test_static_checker_rejects_unknown_proof_before_execution() -> None:
    source = """
    module static_fail
    lineage LA
    agent A lineage LA
    observe e by A content "event" confidence 0.9
    endorse e by A threshold 0.8
    authorize e by A for planning
    plan act by A using e effect read requires missing
    """
    runtime = OSLRuntime()
    with pytest.raises(OSLStaticError, match="unknown proof"):
        runtime.run_text(source)
    assert runtime.state.module is None


def test_first_class_use_proof_gates_planning() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        """
        module proof_use
        lineage LA
        lineage LB
        agent A lineage LA
        agent B lineage LB
        grant A effect externalAct uses 1 until 100
        observe e by B content "route blocked" confidence 0.95
        communicate e from B to A as eA
        endorse eA by A threshold 0.9
        authorize eA by A for planning
        proof pa access eA by A
        proof po origin eA source B lineage LB
        proof pc clear eA for A
        proof pe endorsement eA by A
        proof pu authorization eA by A for planning
        proof p_use use eA by A for planning from ["pa","po","pc","pe","pu"]
        plan act by A using eA effect externalAct requires p_use
        execute act by A
        feedback act by A observed 1.0
        """
    )
    assert state.actions["act"].executed
    assert state.actions["act"].required_proof == "p_use"
    assert runtime._proof_semantically_valid(state.proofs["p_use"])


def test_composite_proof_becomes_stale_when_packet_state_changes() -> None:
    runtime = OSLRuntime()
    with pytest.raises(OSLError, match="stale or semantically invalid"):
        runtime.run_text(
            """
            module stale
            lineage LA
            agent A lineage LA
            observe e by A content "event" confidence 0.95
            endorse e by A threshold 0.9
            authorize e by A for planning
            proof pa access e by A
            proof po origin e source A lineage LA
            proof pc clear e for A
            proof pe endorsement e by A
            proof pu authorization e by A for planning
            proof p_use use e by A for planning from ["pa","po","pc","pe","pu"]
            authorize e by A for read
            plan act by A using e effect read requires p_use
            """
        )


def test_ownership_proof_authorizes_observed_memory() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        """
        module ownership
        lineage LA
        agent A lineage LA
        observe e by A content "event" confidence 0.98
        proof pa access e by A
        proof po origin e source A lineage LA
        proof pc clear e for A
        proof pv observation e by A
        proof own ownership e by A as observed from ["pa","po","pc","pv"]
        write_memory e by A as observed requires own
        """
    )
    assert state.memories["A"][0].proof_digest == state.proofs["own"].proof_digest


def test_ownership_proof_cannot_forge_foreign_observation() -> None:
    runtime = OSLRuntime()
    with pytest.raises(OSLError, match="missing premises: observation"):
        runtime.run_text(
            """
            module ownership_fail
            lineage LA
            lineage LB
            agent A lineage LA
            agent B lineage LB
            observe e by B content "event" confidence 0.98
            communicate e from B to A as eA
            proof pa access eA by A
            proof po origin eA source B lineage LB
            proof pc clear eA for A
            proof own ownership eA by A as observed from ["pa","po","pc"]
            """
        )


def test_bounded_capability_is_consumed() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        """
        module cap
        lineage LA
        agent A lineage LA
        grant A effect externalAct uses 1 until 100
        observe e by A content "event" confidence 0.95
        endorse e by A threshold 0.9
        authorize e by A for planning
        plan act by A using e effect externalAct
        execute act by A
        """
    )
    assert state.capabilities["A"]["externalAct"].remaining_uses == 0
    assert state.actions["act"].capability_digest


def test_capability_proof_becomes_invalid_after_revocation() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        """
        module cap_proof
        lineage LA
        agent A lineage LA
        grant A effect externalAct
        proof p capability externalAct by A
        revoke A effect externalAct
        """
    )
    assert not runtime._proof_semantically_valid(state.proofs["p"])


def test_feedback_contract_is_checked_at_end_of_program() -> None:
    runtime = OSLRuntime()
    with pytest.raises(OSLError, match="lacks feedback"):
        runtime.run_text(
            """
            module contract
            lineage LA
            agent A lineage LA
            grant A effect externalAct
            contract feedback_required after execute require feedback within 2
            observe e by A content "event" confidence 0.95
            endorse e by A threshold 0.9
            authorize e by A for planning
            plan act by A using e effect externalAct
            execute act by A
            """
        )


def test_feedback_contract_is_discharged() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        """
        module contract_ok
        lineage LA
        agent A lineage LA
        grant A effect externalAct
        contract feedback_required after execute require feedback within 2
        observe e by A content "event" confidence 0.95
        endorse e by A threshold 0.9
        authorize e by A for planning
        plan act by A using e effect externalAct
        execute act by A
        feedback act by A observed 1.0
        """
    )
    assert state.contracts["feedback_required"].pending == {}
    assert state.contracts["feedback_required"].violations == []


def test_explicit_transaction_rollback_restores_memory() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        """
        module rollback
        lineage LA
        agent A lineage LA
        begin_transaction tx
        observe temp by A content "temp" confidence 0.99
        write_memory temp by A as observed
        rollback_transaction tx
        """
    )
    assert state.memories["A"] == []
    assert "temp" not in state.packets
    assert any(item["kind"] == "transaction_rollback" for item in runtime.audit_log)
    assert runtime.audit_log[-1]["kind"] == "program_complete"


def test_automatic_transaction_rollback_removes_partial_operator() -> None:
    runtime = OSLRuntime()
    with pytest.raises(OSLError, match="transaction 'tx' rolled back"):
        runtime.run_text(
            """
            module rollback_auto
            space H dim 2
            begin_transaction tx
            operator bad : H -> H kind projector matrix [[1,1],[0,1]]
            commit_transaction tx
            """
        )
    assert "bad" not in runtime.state.operators
    assert any(item["kind"] == "transaction_rollback" for item in runtime.audit_log)
    assert runtime.audit_log[-1]["kind"] == "program_reject"


def test_session_protocol_enforces_message_order() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        """
        module session
        lineage LA
        lineage LB
        agent A lineage LA
        agent B lineage LB
        session S participants ["A","B"] initial waiting_A
        session_transition S waiting_A communicate A B -> waiting_B
        session_transition S waiting_B communicate B A -> ready
        start_session S
        observe a by A content "a" confidence 0.9
        communicate a from A to B as aB in S
        observe b by B content "b" confidence 0.9
        communicate b from B to A as bA in S
        """
    )
    assert state.sessions["S"].current_state == "ready"
    assert len(state.sessions["S"].history) == 3


def test_session_protocol_rejects_out_of_order_message() -> None:
    runtime = OSLRuntime()
    with pytest.raises(OSLError, match="no transition"):
        runtime.run_text(
            """
            module session_fail
            lineage LA
            lineage LB
            agent A lineage LA
            agent B lineage LB
            session S participants ["A","B"] initial waiting_A
            session_transition S waiting_A communicate A B -> waiting_B
            start_session S
            observe b by B content "b" confidence 0.9
            communicate b from B to A as bA in S
            """
        )


def test_neural_candidate_requires_trusted_origin_and_relevance() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        """
        module neural
        lineage LA
        agent A lineage LA
        neural_propose p to A feature f441 content "claim" confidence 0.82
        attest origin p by A lineage LA as p_origin
        attest relevance p by A for planning as p_rel
        admit p by A using ["p_origin","p_rel"]
        """
    )
    packet = state.packets["p"]
    assert packet.status == "admitted"
    assert packet.provenance == "inferred"
    assert packet.obligations == set()
    assert "A" not in packet.quarantined_by


def test_neural_candidate_cannot_be_endorsed_before_admission() -> None:
    runtime = OSLRuntime()
    with pytest.raises(OSLError, match="cannot endorse quarantined packet"):
        runtime.run_text(
            """
            module neural_fail
            lineage LA
            agent A lineage LA
            neural_propose p to A feature f1 content "claim" confidence 0.99
            endorse p by A threshold 0.9
            """
        )


def test_public_projection_contains_secret_digest_but_not_secret_value() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        """
        module secrets
        lineage LA
        agent A lineage LA
        secret private_goal value "do-not-disclose"
        metadata fixed value 7 source trusted
        """
    )
    snapshot_text = json.dumps(state.snapshot(), sort_keys=True)
    public_text = json.dumps(state.public_projection(), sort_keys=True)
    assert "do-not-disclose" not in snapshot_text
    assert "do-not-disclose" not in public_text
    assert "private_goal" in snapshot_text


def test_paired_trace_noninterference_safe_and_leaky_examples() -> None:
    safe = audit(
        ROOT / "examples/28_safe_metadata_left.osl",
        ROOT / "examples/29_safe_metadata_right.osl",
    )
    leak = audit(
        ROOT / "examples/30_leaky_metadata_left.osl",
        ROOT / "examples/31_leaky_metadata_right.osl",
    )
    assert safe["noninterference"]
    assert safe["difference_count"] == 0
    assert not leak["noninterference"]
    assert leak["difference_count"] >= 1


def test_snapshot_and_proof_digests_are_replay_deterministic() -> None:
    source = """
    module deterministic
    lineage LA
    agent A lineage LA
    observe e by A content "event" confidence 0.9
    proof p access e by A
    """
    first = OSLRuntime().run_text(source)
    second = OSLRuntime().run_text(source)
    assert first.snapshot() == second.snapshot()
    assert first.proofs["p"].proof_digest == second.proofs["p"].proof_digest


def test_every_packaged_program_has_deterministic_result() -> None:
    for path in sorted((ROOT / "examples").glob("*.osl")):
        first = run_program(path)
        second = run_program(path)
        assert first["ok"] == second["ok"], path.name
        assert first["error"] == second["error"], path.name
        assert first["state"] == second["state"], path.name
