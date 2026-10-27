from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))

from osl_core import OSLError, OSLRuntime  # noqa: E402
from osl_kernel import KernelVerifier, digest  # noqa: E402


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


def _packet_content_payload(packet: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "name",
        "content",
        "source_agent",
        "source_lineage",
        "provenance",
        "confidence",
        "simulated",
        "parent_digest",
        "latent_source",
    )
    return {key: packet.get(key) for key in keys}


def _packet_state_payload(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        **_packet_content_payload(packet),
        "accessible_to": sorted(packet.get("accessible_to", [])),
        "bound_to": sorted(packet.get("bound_to", [])),
        "quarantined_by": sorted(packet.get("quarantined_by", [])),
        "endorsed_by": sorted(packet.get("endorsed_by", [])),
        "authorizations": {
            agent: sorted(scopes)
            for agent, scopes in sorted(packet.get("authorizations", {}).items())
        },
        "observation_tokens": sorted(packet.get("observation_tokens", [])),
        "status": packet.get("status"),
        "obligations": sorted(packet.get("obligations", [])),
        "support": packet.get("support"),
        "refutation": packet.get("refutation"),
        "unresolved": packet.get("unresolved"),
        "content_digest": packet.get("content_digest"),
    }


def _record_payload(record: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "agent",
        "packet_name",
        "content",
        "memory_class",
        "source_agent",
        "source_lineage",
        "packet_digest",
        "proof_digest",
    )
    return {key: record.get(key) for key in keys}


def _refresh_packet(packet: dict[str, Any]) -> None:
    packet["content_digest"] = digest(_packet_content_payload(packet))
    packet["packet_digest"] = digest(_packet_state_payload(packet))


def _semantic_state(snapshot: dict[str, Any]) -> dict[str, Any]:
    state = {key: copy.deepcopy(snapshot[key]) for key in SEMANTIC_KEYS}
    state["semantic_digest"] = digest(state)
    return state


def _rehash(receipts: list[dict[str, Any]]) -> None:
    """Rebuild every link, including the terminal's preterminal commitment."""

    previous = ZERO_DIGEST
    for index, receipt in enumerate(receipts):
        receipt["index"] = index
        if "state_index" in receipt:
            receipt["state_index"] = index
        receipt["previous_digest"] = previous
        if receipt.get("kind") in {"program_complete", "program_reject"}:
            if "preterminal_chain_tip" in receipt:
                receipt["preterminal_chain_tip"] = previous
            if "audit_receipt_count" in receipt:
                receipt["audit_receipt_count"] = len(receipts)
        receipt.pop("digest", None)
        receipt["digest"] = digest(receipt)
        previous = receipt["digest"]


def _refresh_evidence(
    final_state: dict[str, Any],
    receipts: list[dict[str, Any]],
    *,
    changed_statement_kind: str | None = None,
) -> dict[str, Any]:
    """Keep final and boundary evidence coherent after a semantic mutation."""

    semantic = _semantic_state(final_state)
    if changed_statement_kind is not None:
        boundary = next(
            receipt
            for receipt in reversed(receipts)
            if receipt.get("kind") == "statement_commit"
            and receipt.get("statement_kind") == changed_statement_kind
        )
        boundary["after_semantic_digest"] = semantic["semantic_digest"]

    terminal = receipts[-1]
    assert terminal["kind"] in {"program_complete", "program_reject"}
    terminal["final_semantic_state"] = copy.deepcopy(semantic)
    terminal["semantic_digest"] = semantic["semantic_digest"]

    _rehash(receipts)
    snapshot = copy.deepcopy(final_state)
    snapshot["receipt_count"] = len(receipts)
    snapshot["receipt_chain_tip"] = receipts[-1]["digest"]
    snapshot.pop("snapshot_digest", None)
    snapshot["snapshot_digest"] = digest(snapshot)
    return snapshot


def _run(source: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    runtime = OSLRuntime()
    state = runtime.run_text(source)
    receipts = copy.deepcopy(runtime.audit_log)
    final_state = state.snapshot()
    report = KernelVerifier().verify(receipts, final_state, source=source)
    assert report["all_checks_pass"], report
    return receipts, final_state


def _assert_rejected(report: dict[str, Any]) -> None:
    assert report.get("all_checks_pass") is False, report
    assert int(report.get("failure_count", len(report.get("failures", ())))) > 0


OBSERVE_SOURCE = """\
module observe_constructor
lineage LA
agent A lineage LA
observe e by A content "event" confidence 0.90
"""


def test_rejects_fully_rehashed_observe_constructor_forgery() -> None:
    receipts, final_state = _run(OBSERVE_SOURCE)
    altered = copy.deepcopy(receipts)
    observe = next(receipt for receipt in altered if receipt["kind"] == "observe")
    packet = observe["packet"]
    packet["provenance"] = "simulated"
    packet["simulated"] = True
    packet["observation_tokens"] = []
    packet["status"] = "provisional"
    packet["obligations"] = ["forged"]
    _refresh_packet(packet)

    forged_state = copy.deepcopy(final_state)
    forged_state["packets"][packet["name"]] = copy.deepcopy(packet)
    forged_state = _refresh_evidence(
        forged_state, altered, changed_statement_kind="observe"
    )

    report = KernelVerifier().verify(altered, forged_state, source=OBSERVE_SOURCE)
    _assert_rejected(report)


COMMUNICATE_SOURCE = """\
module communicate_preserves_source
lineage LA
lineage LB
agent A lineage LA
agent B lineage LB
observe e by A content "event" confidence 0.90
communicate e from A to B as e_at_B
"""


def test_rejects_fully_rehashed_communicated_field_forgery() -> None:
    receipts, final_state = _run(COMMUNICATE_SOURCE)
    altered = copy.deepcopy(receipts)
    communicate = next(
        receipt for receipt in altered if receipt["kind"] == "communicate"
    )
    packet = communicate["packet"]
    packet["content"] = "forged replacement"
    packet["source_agent"] = "B"
    packet["source_lineage"] = "LB"
    packet["observation_tokens"] = ["B"]
    _refresh_packet(packet)

    forged_state = copy.deepcopy(final_state)
    forged_state["packets"][packet["name"]] = copy.deepcopy(packet)
    forged_state = _refresh_evidence(
        forged_state, altered, changed_statement_kind="communicate"
    )

    report = KernelVerifier().verify(altered, forged_state, source=COMMUNICATE_SOURCE)
    _assert_rejected(report)


MEMORY_SOURCE = """\
module memory_packet_binding
lineage LA
agent A lineage LA
observe e by A content "event" confidence 0.90
write_memory e by A as observed
"""


def test_rejects_fully_rehashed_memory_record_mismatch() -> None:
    receipts, final_state = _run(MEMORY_SOURCE)
    altered = copy.deepcopy(receipts)
    memory = next(receipt for receipt in altered if receipt["kind"] == "memory_write")
    record = memory["record"]
    record["content"] = "forged memory"
    record["source_agent"] = "external"
    record["source_lineage"] = "external"
    record["record_digest"] = digest(_record_payload(record))

    forged_state = copy.deepcopy(final_state)
    forged_state["memories"]["A"][0] = copy.deepcopy(record)
    forged_state = _refresh_evidence(
        forged_state, altered, changed_statement_kind="write_memory"
    )

    report = KernelVerifier().verify(altered, forged_state, source=MEMORY_SOURCE)
    _assert_rejected(report)


ADMISSION_SOURCE = """\
module admission_proof_binding
lineage LA
agent A lineage LA
neural_propose candidate to A feature f1 content "route blocked" confidence 0.82
attest origin candidate by A lineage LA as p_origin
attest relevance candidate by A for planning as p_relevance
admit candidate by A using ["p_origin","p_relevance"]
"""


def test_rejects_fully_rehashed_admission_with_bogus_proof_digests() -> None:
    receipts, final_state = _run(ADMISSION_SOURCE)
    altered = copy.deepcopy(receipts)
    admission = next(
        receipt for receipt in altered if receipt["kind"] == "neural_admission"
    )
    admission["origin_proof"] = ZERO_DIGEST
    admission["relevance_proof"] = "f" * 64
    _rehash(altered)

    forged_state = copy.deepcopy(final_state)
    forged_state["receipt_chain_tip"] = altered[-1]["digest"]
    forged_state.pop("snapshot_digest", None)
    forged_state["snapshot_digest"] = digest(forged_state)

    report = KernelVerifier().verify(altered, forged_state, source=ADMISSION_SOURCE)
    _assert_rejected(report)


def test_rejects_fully_rehashed_unknown_receipt_kind() -> None:
    receipts, final_state = _run("module reject_unknown_receipt\n")
    altered = copy.deepcopy(receipts)
    terminal = altered.pop()
    prior = altered[-1]
    altered.append(
        {
            "schema": prior["schema"],
            "core_version": prior["core_version"],
            "index": len(altered),
            "state_index": len(altered),
            "step": prior["step"],
            "kind": "unknown_semantic_transition",
            "transaction": None,
            "previous_digest": prior["digest"],
            "payload": "forged",
        }
    )
    altered.append(terminal)
    _rehash(altered)

    forged_state = copy.deepcopy(final_state)
    forged_state["receipt_count"] = len(altered)
    forged_state["receipt_chain_tip"] = altered[-1]["digest"]
    forged_state.pop("snapshot_digest", None)
    forged_state["snapshot_digest"] = digest(forged_state)

    report = KernelVerifier().verify(
        altered, forged_state, source="module reject_unknown_receipt\n"
    )
    _assert_rejected(report)


QUARANTINE_LAUNDERING_SOURCE = """\
module reject_quarantine_laundering
lineage LA
lineage LB
agent A lineage LA
agent B lineage LB
inject x to A content "untrusted" confidence 0.90
communicate x from A to B as laundered
"""


def test_communication_cannot_launder_a_quarantined_packet() -> None:
    runtime = OSLRuntime()
    with pytest.raises(OSLError):
        runtime.run_text(QUARANTINE_LAUNDERING_SOURCE)

    assert runtime.audit_log[-1]["kind"] == "program_reject"
    assert "laundered" not in runtime.state.packets
    report = KernelVerifier().verify(
        runtime.audit_log,
        runtime.state.snapshot(),
        source=QUARANTINE_LAUNDERING_SOURCE,
    )
    assert report["all_checks_pass"], report
