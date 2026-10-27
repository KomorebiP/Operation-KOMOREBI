from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))

from osl_core import OSLError, OSLRuntime, OSLStaticError  # noqa: E402
from osl_kernel import (  # noqa: E402
    KernelVerifier,
    _proof_payload,
    digest,
)


ZERO_DIGEST = "0" * 64
SEMANTIC_KEYS = (
    "module",
    "agents",
    "lineage_parents",
    "spaces",
    "operators",
    "vectors",
    "packets",
    "proofs",
    "memories",
    "actions",
    "capabilities",
    "contracts",
    "sessions",
    "metadata",
    "secret_digests",
    "assertions",
    "step",
)


def _run(source: str, *, expect_error: bool = False) -> tuple[OSLRuntime, Exception | None]:
    """Run source while retaining the terminal trace for an expected rejection."""

    runtime = OSLRuntime()
    error: Exception | None = None
    try:
        runtime.run_text(source)
    except (OSLError, OSLStaticError) as exc:
        error = exc

    if expect_error:
        assert error is not None
    else:
        assert error is None, str(error)

    assert runtime.audit_log, "OSL-Core 0.4 must emit a trace for every outcome"
    assert runtime.audit_log[-1]["kind"] in {"program_complete", "program_reject"}
    return runtime, error


def _verify(
    receipts: list[dict[str, Any]],
    final_state: dict[str, Any],
    source: str,
) -> dict[str, Any]:
    """Call the source-bound OSL-Core 0.4 kernel API."""

    return KernelVerifier().verify(receipts, final_state, source=source)


def _assert_kernel_accepts(report: dict[str, Any]) -> None:
    assert report.get("all_checks_pass") is True, report.get("failures")
    assert int(report.get("failure_count", 0)) == 0


def _assert_kernel_rejects(report: dict[str, Any]) -> None:
    # Deliberately avoid coupling the regression to provisional property names.
    assert report.get("all_checks_pass") is False
    assert int(report.get("failure_count", len(report.get("failures", ())))) > 0


def _rehash_trace(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deep-copy and rebuild a complete receipt chain after adversarial edits."""

    altered = copy.deepcopy(receipts)
    start = next(
        (
            index + 1
            for index, receipt in enumerate(altered)
            if receipt.get("kind") == "static_check"
        ),
        0,
    )
    for index, receipt in enumerate(altered):
        if receipt.get("kind") in {"statement_commit", "statement_reject"}:
            receipt["emitted_receipt_indices"] = tuple(range(start, index))
            receipt["effect_span"] = (start, index)
            start = index + 1
    previous = ZERO_DIGEST
    for index, receipt in enumerate(altered):
        receipt["index"] = index
        # The focused traces below contain no rollback, so state and audit indices
        # coincide. Keeping both coherent prevents an incidental index failure.
        if "state_index" in receipt:
            receipt["state_index"] = index
        receipt["previous_digest"] = previous
        if receipt.get("kind") in {"program_complete", "program_reject"}:
            receipt["preterminal_chain_tip"] = previous
            receipt["audit_receipt_count"] = len(altered)
        receipt.pop("digest", None)
        receipt["digest"] = digest(receipt)
        previous = receipt["digest"]
    return altered


def _rehash_proof(proof: dict[str, Any]) -> None:
    proof["proof_digest"] = digest(_proof_payload(proof))


def _semantic_digest(final_state: dict[str, Any]) -> str:
    payload = {key: copy.deepcopy(final_state[key]) for key in SEMANTIC_KEYS}
    return digest(payload)


def _refresh_snapshot(
    final_state: dict[str, Any], receipts: list[dict[str, Any]]
) -> dict[str, Any]:
    """Refresh receipt metadata and the self-digest of a copied final snapshot."""

    snapshot = copy.deepcopy(final_state)
    snapshot["receipt_count"] = len(receipts)
    snapshot["receipt_chain_tip"] = receipts[-1]["digest"] if receipts else ZERO_DIGEST
    snapshot.pop("snapshot_digest", None)
    snapshot["snapshot_digest"] = digest(snapshot)
    return snapshot


ACCESS_SOURCE = """\
module forged_access
lineage LA
lineage LB
agent A lineage LA
agent B lineage LB
observe e by A content "event" confidence 0.90
proof p access e by A
"""


def test_kernel_rejects_rehashed_false_primitive_access_proof() -> None:
    runtime, _ = _run(ACCESS_SOURCE)
    baseline = _verify(runtime.audit_log, runtime.state.snapshot(), ACCESS_SOURCE)
    _assert_kernel_accepts(baseline)

    altered = copy.deepcopy(runtime.audit_log)
    proof_receipt = next(item for item in altered if item["kind"] == "proof_construct")
    proof_receipt["proof"]["agent"] = "B"
    _rehash_proof(proof_receipt["proof"])
    altered = _rehash_trace(altered)

    # Keep the supplied final proof table consistent with the forgery. A strict
    # kernel must still reject because B is not in packet e's access relation.
    final_state = copy.deepcopy(runtime.state.snapshot())
    final_state["proofs"]["p"] = copy.deepcopy(proof_receipt["proof"])
    terminal_state = {
        key: copy.deepcopy(final_state[key]) for key in SEMANTIC_KEYS
    }
    semantic_digest = digest(terminal_state)
    terminal_state["semantic_digest"] = semantic_digest
    proof_boundary = next(
        item
        for item in altered
        if item["kind"] == "statement_commit"
        and item.get("statement_kind") == "proof"
    )
    proof_boundary["after_semantic_digest"] = semantic_digest
    altered[-1]["semantic_digest"] = semantic_digest
    altered[-1]["final_semantic_state"] = terminal_state
    altered = _rehash_trace(altered)
    final_state = _refresh_snapshot(final_state, altered)

    report = _verify(altered, final_state, ACCESS_SOURCE)
    _assert_kernel_rejects(report)


LINEAR_SOURCE = """\
module duplicate_linear
lineage LA
agent A lineage LA
observe e by A content "event" confidence 0.98
proof pa access e by A
proof po origin e source A lineage LA
proof pc clear e for A
proof pv observation e by A
proof own ownership e by A as observed from ["pa","po","pc","pv"] mode linear
write_memory e by A as observed requires own
"""


def test_kernel_rejects_duplicate_construction_that_resets_linear_proof() -> None:
    runtime, _ = _run(LINEAR_SOURCE)
    baseline = _verify(runtime.audit_log, runtime.state.snapshot(), LINEAR_SOURCE)
    _assert_kernel_accepts(baseline)

    altered = copy.deepcopy(runtime.audit_log)
    construction = copy.deepcopy(
        next(
            item
            for item in altered
            if item["kind"] == "proof_construct"
            and item.get("proof", {}).get("name") == "own"
        )
    )
    consumption = copy.deepcopy(
        next(
            item
            for item in altered
            if item["kind"] == "proof_consume" and item.get("proof") == "own"
        )
    )
    terminal_index = next(
        index
        for index, item in enumerate(altered)
        if item["kind"] == "program_complete"
    )
    terminal_step = altered[terminal_index]["step"]
    construction["step"] = terminal_step
    consumption["step"] = terminal_step
    altered[terminal_index:terminal_index] = [construction, consumption]
    altered = _rehash_trace(altered)
    final_state = _refresh_snapshot(runtime.state.snapshot(), altered)

    report = _verify(altered, final_state, LINEAR_SOURCE)
    _assert_kernel_rejects(report)

    # A gate cannot merely name a suitable proof: its immediately preceding,
    # source-owned use/consume receipt is part of the authorization transition.
    altered = [
        item
        for item in runtime.audit_log
        if not (item.get("kind") == "proof_consume" and item.get("proof") == "own")
    ]
    altered = _rehash_trace(altered)
    final_state = copy.deepcopy(runtime.state.snapshot())
    final_state["proofs"]["own"]["remaining_uses"] = 1
    final_state["proofs"]["own"]["consumed_step"] = None
    final_state = _refresh_snapshot(final_state, altered)
    report = _verify(altered, final_state, LINEAR_SOURCE)
    _assert_kernel_rejects(report)


STALE_CAPABILITY_SOURCE = """\
module stale_capability
lineage LA
agent A lineage LA
grant A effect externalAct uses 1 until 100
proof p_cap capability externalAct by A
revoke A effect externalAct
grant A effect externalAct uses 1 until 100
assert proof p_cap valid false
"""


def test_capability_proof_does_not_revive_after_identical_regrant() -> None:
    # Identical grant parameters make this an epoch/identity test, not merely a
    # comparison of effect, use count, or expiry fields.
    runtime, _ = _run(STALE_CAPABILITY_SOURCE)
    report = _verify(
        runtime.audit_log,
        runtime.state.snapshot(),
        STALE_CAPABILITY_SOURCE,
    )
    _assert_kernel_accepts(report)
    assert runtime.audit_log[-1]["kind"] == "program_complete"


PERSISTENT_PROOF_SOURCE = """\
module final_correspondence
lineage LA
agent A lineage LA
observe e by A content "event" confidence 0.90
proof p access e by A
"""


def test_kernel_rejects_missing_proof_in_final_snapshot() -> None:
    runtime, _ = _run(PERSISTENT_PROOF_SOURCE)
    final_state = copy.deepcopy(runtime.state.snapshot())
    del final_state["proofs"]["p"]
    final_state = _refresh_snapshot(final_state, runtime.audit_log)

    report = _verify(runtime.audit_log, final_state, PERSISTENT_PROOF_SOURCE)
    _assert_kernel_rejects(report)


def test_kernel_rejects_trace_without_terminal_receipt() -> None:
    runtime, _ = _run(PERSISTENT_PROOF_SOURCE)
    assert runtime.audit_log[-1]["kind"] == "program_complete"
    altered = _rehash_trace(runtime.audit_log[:-1])
    final_state = _refresh_snapshot(runtime.state.snapshot(), altered)

    report = _verify(altered, final_state, PERSISTENT_PROOF_SOURCE)
    _assert_kernel_rejects(report)


def test_rejected_runtime_trace_is_terminal_and_kernel_verifiable() -> None:
    source = """\
module static_rejection_receipt
lineage LA
agent A lineage LA
observe e by A content "event" confidence 0.90
plan act by A using e effect read requires missing_proof
"""
    runtime, _ = _run(source, expect_error=True)
    assert runtime.audit_log[-1]["kind"] == "program_reject"
    _assert_kernel_accepts(_verify(runtime.audit_log, runtime.state.snapshot(), source))
