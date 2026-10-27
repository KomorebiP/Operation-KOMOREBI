from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))

from osl_core import OSLRuntime, OSLError  # noqa: E402
from osl_kernel import KernelVerifier, digest, verify_directory  # noqa: E402
from osl_metacore import build_report  # noqa: E402


def _run(name: str) -> OSLRuntime:
    runtime = OSLRuntime()
    try:
        runtime.run_file(ROOT / "examples" / name)
    except OSLError:
        pass
    return runtime


def _rehash_chain(receipts: list[dict]) -> None:
    previous = "0" * 64
    for index, receipt in enumerate(receipts):
        receipt["index"] = index
        receipt["previous_digest"] = previous
        receipt.pop("digest", None)
        receipt["digest"] = digest(receipt)
        previous = receipt["digest"]


def test_exhaustive_finite_metacore_reaches_fixpoint() -> None:
    report = build_report()
    assert report["aggregate"]["all_checks_pass"]
    assert report["aggregate"]["reachable_state_count"] == 1590
    assert report["aggregate"]["transition_attempt_count"] == 28718
    assert all(model["fixpoint_reached"] for model in report["models"])
    assert all(not model["counterexamples"] for model in report["models"])


def test_metacore_checks_all_declared_invariants() -> None:
    report = build_report()
    checks = {
        key: value
        for model in report["models"]
        for key, value in {
            **model["invariant_checks"],
            **model["special_checks"],
        }.items()
    }
    assert checks["no_forged_observed_memory"]
    assert checks["simulated_not_observed"]
    assert checks["communicated_not_observed"]
    assert checks["capability_confinement"]
    assert checks["execute_consumes_one"]
    assert checks["no_overdue_accepted_state"]
    assert checks["rollback_equivalence"]
    assert checks["session_trace_fidelity"]


def test_independent_kernel_verifies_complete_program_suite() -> None:
    report = verify_directory(ROOT / "examples")
    assert report["program_count"] == 66
    assert report["verified_program_count"] == 66
    assert report["receipt_count"] == 1825
    assert report["proof_count"] == 70
    assert report["all_checks_pass"]


def test_kernel_rejects_raw_receipt_tampering() -> None:
    runtime = _run("02_communicated_route.osl")
    receipts = copy.deepcopy(runtime.audit_log)
    receipts[3]["to_agent"] = "B"
    report = KernelVerifier().verify(receipts, runtime.state.snapshot())
    assert not report["all_checks_pass"]
    assert any(item["property"] == "receipt_digest" for item in report["failures"])


def test_kernel_rejects_rehashed_provenance_forgery() -> None:
    runtime = _run("02_communicated_route.osl")
    receipts = copy.deepcopy(runtime.audit_log)
    memory_receipt = next(item for item in receipts if item["kind"] == "memory_write")
    record = memory_receipt["record"]
    record["memory_class"] = "observed"
    record_payload = {
        key: record.get(key)
        for key in (
            "agent",
            "packet_name",
            "content",
            "memory_class",
            "source_agent",
            "source_lineage",
            "packet_digest",
            "proof_digest",
        )
    }
    record["record_digest"] = digest(record_payload)
    _rehash_chain(receipts)
    report = KernelVerifier().verify(receipts, runtime.state.snapshot())
    assert not report["all_checks_pass"]
    properties = {item["property"] for item in report["failures"]}
    assert "memory_provenance_compatibility" in properties
    assert "observed_memory_nonforging" in properties


def test_append_only_audit_log_survives_transaction_rollback() -> None:
    runtime = _run("107_transaction_auto_rollback.osl")
    kinds = [receipt["kind"] for receipt in runtime.audit_log]
    assert "transaction_begin" in kinds
    assert "transaction_rollback" in kinds
    assert kinds[-1] == "program_reject"
    # Core 0.4 keeps the state-facing receipt mirror aligned with the global
    # append-only audit instead of restoring an obsolete transactional prefix.
    assert len(runtime.audit_log) == len(runtime.state.receipts)
    source = (ROOT / "examples" / "107_transaction_auto_rollback.osl").read_text()
    report = KernelVerifier().verify(
        runtime.audit_log, runtime.state.snapshot(), source=source
    )
    assert report["all_checks_pass"]
    assert report["rolled_back_transaction_count"] == 1


def test_linear_proof_is_consumed_exactly_once() -> None:
    runtime = _run("37_linear_use_once.osl")
    proof = runtime.state.proofs["p_use"]
    assert proof.resource_mode == "linear"
    assert proof.remaining_uses == 0
    assert proof.consumed_step is not None
    assert any(receipt["kind"] == "proof_consume" for receipt in runtime.audit_log)
    source = (ROOT / "examples" / "37_linear_use_once.osl").read_text()
    report = KernelVerifier().verify(
        runtime.audit_log, runtime.state.snapshot(), source=source
    )
    assert report["all_checks_pass"]


def test_unconsumed_linear_proof_causes_safe_program_rejection() -> None:
    runtime = _run("109_linear_proof_unconsumed.osl")
    assert runtime.audit_log[-1]["kind"] == "program_reject"
    assert "linear proofs must be consumed exactly once" in runtime.audit_log[-1]["error"]
    source = (ROOT / "examples" / "109_linear_proof_unconsumed.osl").read_text()
    report = KernelVerifier().verify(
        runtime.audit_log, runtime.state.snapshot(), source=source
    )
    assert report["all_checks_pass"]
