from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))

from osl_formal_kernel import explore_kernel  # noqa: E402
from osl_information_flow import analyze_information_flow  # noqa: E402
from osl_kernel import verify_directory as verify_kernel_directory  # noqa: E402
from osl_metacore import build_report as build_metacore_report  # noqa: E402
from osl_model import SessionProtocol  # noqa: E402
from osl_parser import parse_and_check  # noqa: E402
from osl_session_verify import verify_session_protocol  # noqa: E402
from verify_osl_core_v03 import build_unified_report, conformance_report  # noqa: E402
from verify_trace import verify_directory as verify_trace_directory  # noqa: E402


def test_conformance_certificate_has_complete_audit_metadata() -> None:
    report = conformance_report(ROOT / "examples")
    assert report["all_checks_pass"]
    assert report["program_count"] == 66
    assert report["passed_program_count"] == 66
    assert report["accepted_program_count"] == 42
    assert report["expected_rejection_count"] == 24
    audited = [record for record in report["records"] if record["audit_receipt_count"] > 0]
    unaudited = [record["file"] for record in report["records"] if record["audit_receipt_count"] == 0]
    assert len(audited) == 64
    assert all(record["audit_chain_tip"] for record in audited)
    assert unaudited == ["102_unknown_proof_static.osl", "103_nested_transaction.osl"]


def test_trace_certificate_replays_every_packaged_program() -> None:
    report = verify_trace_directory(ROOT / "examples")
    assert report["all_checks_pass"]
    assert report["program_count"] == 66
    assert report["passed_count"] == 66
    assert report["failed_count"] == 0
    assert all(record["deterministic_replay"] for record in report["records"])


def test_independent_kernel_certificate_has_expected_totals() -> None:
    report = verify_kernel_directory(ROOT / "examples")
    assert report["all_checks_pass"]
    assert report["program_count"] == 66
    assert report["verified_program_count"] == 66
    assert report["receipt_count"] == 1149
    assert report["proof_count"] == 70
    assert report["transaction_rollback_count"] == 2


def test_integrated_abstract_kernel_is_exhaustive_and_clean() -> None:
    report = explore_kernel()
    assert report["all_checks_pass"]
    assert report["reachable_state_count"] == 740
    assert report["transition_count"] == 19240
    assert report["accepted_transition_count"] == 6464
    assert report["rejected_transition_count"] == 12776
    assert report["failure_count"] == 0


def test_decomposed_metacore_is_exhaustive_and_clean() -> None:
    report = build_metacore_report()
    assert report["aggregate"]["all_checks_pass"]
    assert report["aggregate"]["reachable_state_count"] == 1590
    assert report["aggregate"]["transition_attempt_count"] == 28718
    assert report["aggregate"]["stepped_transition_count"] == 15217
    assert report["aggregate"]["rejected_transition_count"] == 13501


def test_unified_certificate_binds_all_evidence_layers() -> None:
    report = build_unified_report(ROOT)
    assert report["all_checks_pass"]
    assert all(report["checks"].values())
    assert report["summary"]["total_finite_states_explored"] == 2330
    assert report["summary"]["total_finite_transition_checks"] == 47958
    assert report["summary"]["independent_kernel_receipt_count"] == 1149
    assert report["summary"]["independent_kernel_proof_count"] == 70
    assert set(report["certificate_digests"]) == {
        "conformance",
        "trace",
        "receipt_kernel",
        "abstract_kernel",
        "abstract_kernel_state_graph",
        "decomposed_metacore",
    }


def test_static_explicit_flow_certificate_classifies_safe_and_leaky_sources() -> None:
    reports = {}
    for name in (
        "28_safe_metadata_left.osl",
        "29_safe_metadata_right.osl",
        "30_leaky_metadata_left.osl",
        "31_leaky_metadata_right.osl",
    ):
        statements, _ = parse_and_check(
            (ROOT / "examples" / name).read_text(encoding="utf-8")
        )
        reports[name] = analyze_information_flow(statements)
    assert reports["28_safe_metadata_left.osl"].noninterference_in_supported_fragment
    assert reports["29_safe_metadata_right.osl"].noninterference_in_supported_fragment
    assert not reports["30_leaky_metadata_left.osl"].noninterference_in_supported_fragment
    assert not reports["31_leaky_metadata_right.osl"].noninterference_in_supported_fragment
    assert reports["30_leaky_metadata_left.osl"].explicit_leak_count == 1


def test_session_graph_certificate_separates_valid_and_deadlocked_protocols() -> None:
    valid = SessionProtocol(
        name="valid",
        participants=("A", "B"),
        initial_state="waiting_A",
        transitions={
            ("waiting_A", "communicate", "A", "B"): "waiting_B",
            ("waiting_B", "communicate", "B", "A"): "ready",
        },
        terminal_states={"ready"},
    )
    good = verify_session_protocol(valid)
    assert good.all_checks_pass
    assert good.reachable_states == ("ready", "waiting_A", "waiting_B")
    assert good.reachable_deadlocks == ()

    deadlocked = SessionProtocol(
        name="deadlocked",
        participants=("A", "B"),
        initial_state="waiting_A",
        transitions={
            ("waiting_A", "communicate", "A", "B"): "waiting_B",
        },
        terminal_states={"ready"},
    )
    bad = verify_session_protocol(deadlocked)
    assert not bad.all_checks_pass
    assert bad.reachable_deadlocks == ("waiting_B",)
