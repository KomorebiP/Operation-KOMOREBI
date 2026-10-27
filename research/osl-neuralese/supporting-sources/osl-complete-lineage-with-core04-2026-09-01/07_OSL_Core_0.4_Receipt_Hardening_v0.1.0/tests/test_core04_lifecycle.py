from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))

from osl_core import OSLRuntime  # noqa: E402
from osl_kernel import KernelVerifier, digest  # noqa: E402
from osl_model import OSLStaticError  # noqa: E402


TERMINAL_KINDS = {"program_complete", "program_reject"}


def _rehash(receipts: list[dict[str, Any]]) -> None:
    """Rebuild the public hash chain after an adversarial trace mutation."""

    previous = "0" * 64
    for index, receipt in enumerate(receipts):
        receipt["index"] = index
        if "state_index" in receipt:
            receipt["state_index"] = index
        receipt["previous_digest"] = previous
        receipt.pop("digest", None)
        receipt["digest"] = digest(receipt)
        previous = receipt["digest"]


def _align_evidence(
    final_state: dict[str, Any], receipts: list[dict[str, Any]]
) -> dict[str, Any]:
    """Keep envelope fields coherent so lifecycle checks see the real defect."""

    state = copy.deepcopy(final_state)
    tip = receipts[-1]["digest"] if receipts else "0" * 64
    for key in ("receipt_count", "audit_receipt_count"):
        if key in state:
            state[key] = len(receipts)
    for key in ("receipt_chain_tip", "audit_chain_tip"):
        if key in state:
            state[key] = tip
    if "snapshot_digest" in state:
        state.pop("snapshot_digest")
        state["snapshot_digest"] = digest(state)
    return state


def _run(source: str) -> tuple[OSLRuntime, dict[str, Any], list[dict[str, Any]]]:
    runtime = OSLRuntime()
    state = runtime.run_text(source)
    final_state = state.snapshot()
    receipts = copy.deepcopy(runtime.audit_log)
    report = KernelVerifier().verify(receipts, final_state, source=source)
    assert report["all_checks_pass"], report
    return runtime, final_state, receipts


def _assert_strict_rejection(report: dict[str, Any]) -> None:
    assert not report["all_checks_pass"], report
    assert report.get("failure_count", len(report.get("failures", ()))) > 0


def test_empty_trace_is_not_a_valid_empty_program() -> None:
    source = ""
    final_state = OSLRuntime().state.snapshot()
    report = KernelVerifier().verify([], final_state, source=source)
    _assert_strict_rejection(report)


def test_missing_terminal_is_rejected_after_full_chain_rehash() -> None:
    source = "module lifecycle_missing_terminal\n"
    _runtime, final_state, receipts = _run(source)
    assert receipts[-1]["kind"] == "program_complete"
    receipts.pop()
    _rehash(receipts)
    final_state = _align_evidence(final_state, receipts)

    report = KernelVerifier().verify(receipts, final_state, source=source)
    _assert_strict_rejection(report)


def test_double_terminal_is_rejected_after_full_chain_rehash() -> None:
    source = "module lifecycle_double_terminal\n"
    _runtime, final_state, receipts = _run(source)
    terminal = copy.deepcopy(receipts[-1])
    assert terminal["kind"] in TERMINAL_KINDS
    receipts.append(terminal)
    _rehash(receipts)
    final_state = _align_evidence(final_state, receipts)

    report = KernelVerifier().verify(receipts, final_state, source=source)
    _assert_strict_rejection(report)


def test_terminal_must_be_last_even_when_the_chain_is_rehashed() -> None:
    source = "module lifecycle_nonlast_terminal\n"
    _runtime, final_state, receipts = _run(source)
    terminal = receipts.pop()
    assert receipts
    receipts.insert(len(receipts) - 1, terminal)
    assert sum(r["kind"] in TERMINAL_KINDS for r in receipts) == 1
    assert receipts[-1]["kind"] not in TERMINAL_KINDS
    _rehash(receipts)
    final_state = _align_evidence(final_state, receipts)

    report = KernelVerifier().verify(receipts, final_state, source=source)
    _assert_strict_rejection(report)


def test_receipts_are_bound_to_the_exact_source() -> None:
    original = "module source_alpha\n"
    substituted = "module source_beta\n"
    _runtime, final_state, receipts = _run(original)

    report = KernelVerifier().verify(receipts, final_state, source=substituted)
    _assert_strict_rejection(report)

    report = KernelVerifier().verify(receipts, final_state, source=None)
    _assert_strict_rejection(report)


def test_terminal_semantic_digest_is_not_a_decorative_field() -> None:
    source = "module lifecycle_terminal_state\n"
    _runtime, final_state, receipts = _run(source)
    terminal = receipts[-1]
    digest_key = (
        "final_semantic_digest"
        if "final_semantic_digest" in terminal
        else "semantic_digest"
    )
    assert digest_key in terminal
    terminal[digest_key] = "0" * 64
    _rehash(receipts)
    final_state = _align_evidence(final_state, receipts)

    report = KernelVerifier().verify(receipts, final_state, source=source)
    _assert_strict_rejection(report)


def test_parse_rejection_has_a_complete_verifiable_trace() -> None:
    source = "module parse_failure\nthis is not an osl statement\n"
    runtime = OSLRuntime()
    with pytest.raises(OSLStaticError):
        runtime.run_text(source)

    kinds = [receipt["kind"] for receipt in runtime.audit_log]
    assert kinds[0] == "program_open"
    assert "parse_reject" in kinds
    assert "parse_accept" not in kinds
    assert "static_check" not in kinds
    assert kinds[-1] == "program_reject"
    assert sum(kind in TERMINAL_KINDS for kind in kinds) == 1

    report = KernelVerifier().verify(
        runtime.audit_log, runtime.state.snapshot(), source=source
    )
    assert report["all_checks_pass"], report

    mutated = copy.deepcopy(runtime.audit_log)
    mutated[-1]["phase"] = "statement"
    _rehash(mutated)
    mutated_state = _align_evidence(runtime.state.snapshot(), mutated)
    report = KernelVerifier().verify(mutated, mutated_state, source=source)
    _assert_strict_rejection(report)


def test_static_rejection_has_a_complete_verifiable_trace() -> None:
    source = "module static_failure\nagent A lineage missing_lineage\n"
    runtime = OSLRuntime()
    with pytest.raises(OSLStaticError):
        runtime.run_text(source)

    kinds = [receipt["kind"] for receipt in runtime.audit_log]
    assert kinds[0] == "program_open"
    assert "parse_accept" in kinds
    assert "static_reject" in kinds
    assert "static_check" not in kinds
    assert kinds[-1] == "program_reject"
    assert sum(kind in TERMINAL_KINDS for kind in kinds) == 1

    report = KernelVerifier().verify(
        runtime.audit_log, runtime.state.snapshot(), source=source
    )
    assert report["all_checks_pass"], report


def test_rollback_restores_the_private_secret_store() -> None:
    source = '''
    module rollback_private_secret
    begin_transaction trial
    secret ephemeral value "rollback-only-secret"
    rollback_transaction trial
    '''
    runtime, final_state, receipts = _run(source)

    assert "ephemeral" not in runtime._secrets
    assert "ephemeral" not in runtime.state.secret_digests
    assert any(receipt["kind"] == "transaction_rollback" for receipt in receipts)
    assert receipts[-1]["kind"] == "program_complete"

    report = KernelVerifier().verify(receipts, final_state, source=source)
    assert report["all_checks_pass"], report
