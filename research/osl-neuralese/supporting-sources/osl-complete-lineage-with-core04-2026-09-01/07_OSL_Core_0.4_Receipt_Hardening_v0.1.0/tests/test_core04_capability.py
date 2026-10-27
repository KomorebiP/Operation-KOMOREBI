from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
sys.path.insert(0, str(REFERENCE))

from osl_core import OSLRuntime  # noqa: E402
from osl_kernel import KernelVerifier, _action_payload, digest  # noqa: E402


ONE_USE_SOURCE = """
module core04_one_use
lineage L_A
agent A lineage L_A
grant A effect externalAct uses 1 until 9
observe evidence by A content "ready" confidence 0.99
endorse evidence by A threshold 0.9
authorize evidence by A for planning
plan act by A using evidence effect externalAct expected 1.0
execute act by A
feedback act by A observed 1.25
""".strip() + "\n"


TWO_USE_SOURCE = """
module core04_two_use
lineage L_A
agent A lineage L_A
grant A effect externalAct uses 2 until 100
observe evidence by A content "ready" confidence 0.99
endorse evidence by A threshold 0.9
authorize evidence by A for planning
plan first by A using evidence effect externalAct
execute first by A
plan second by A using evidence effect externalAct
execute second by A
""".strip() + "\n"


DUPLICATE_EXECUTION_SOURCE = """
module core04_duplicate_execution
lineage L_A
agent A lineage L_A
grant A effect externalAct uses 2 until 100
observe evidence by A content "ready" confidence 0.99
endorse evidence by A threshold 0.9
authorize evidence by A for planning
plan act by A using evidence effect externalAct
execute act by A
""".strip() + "\n"


REVOKE_SOURCE = """
module core04_one_use
lineage L_A
agent A lineage L_A
grant A effect externalAct uses 1 until 9
observe evidence by A content "ready" confidence 0.99
endorse evidence by A threshold 0.9
authorize evidence by A for planning
plan act by A using evidence effect externalAct expected 1.0
revoke A effect externalAct
""".strip() + "\n"


UNUSED_EXPIRED_SOURCE = """
module core04_unused_expired
lineage L_A
agent A lineage L_A
grant A effect externalAct uses 1 until 4
lineage L_B
""".strip() + "\n"


DEFAULT_GRANT_SOURCE = """
module core04_default_grants
lineage L_A
agent A lineage L_A
""".strip() + "\n"


def _run(source: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    runtime = OSLRuntime()
    runtime.run_text(source, filename="<core04-capability-test>")
    return copy.deepcopy(runtime.audit_log), copy.deepcopy(runtime.state.snapshot())


def _verify(
    source: str, receipts: list[dict[str, Any]], final_state: dict[str, Any]
) -> dict[str, Any]:
    return KernelVerifier().verify(receipts, final_state, source=source)


def _refresh_action_digest(action: dict[str, Any]) -> None:
    action["action_digest"] = digest(_action_payload(action))


def _refresh_snapshot_digest(final_state: dict[str, Any]) -> None:
    payload = copy.deepcopy(final_state)
    payload.pop("snapshot_digest", None)
    final_state["snapshot_digest"] = digest(payload)


def _refresh_boundary_indices(receipts: list[dict[str, Any]]) -> None:
    start = next(
        (
            index + 1
            for index, receipt in enumerate(receipts)
            if receipt.get("kind") == "static_check"
        ),
        0,
    )
    for index, receipt in enumerate(receipts):
        if receipt.get("kind") in {"statement_commit", "statement_reject"}:
            receipt["emitted_receipt_indices"] = tuple(range(start, index))
            receipt["effect_span"] = (start, index)
            start = index + 1


def _rehash(
    receipts: list[dict[str, Any]], final_state: dict[str, Any]
) -> None:
    for index, receipt in enumerate(receipts):
        receipt["index"] = index
        if "state_index" in receipt:
            receipt["state_index"] = index
    _refresh_boundary_indices(receipts)

    previous = "0" * 64
    for receipt in receipts:
        receipt["previous_digest"] = previous
        if receipt.get("kind") in {"program_complete", "program_reject"}:
            receipt["preterminal_chain_tip"] = previous
            receipt["audit_receipt_count"] = len(receipts)
        receipt.pop("digest", None)
        receipt["digest"] = digest(receipt)
        previous = receipt["digest"]

    final_state["receipt_count"] = len(receipts)
    final_state["receipt_chain_tip"] = previous
    _refresh_snapshot_digest(final_state)


def _explicit_grant(receipt: dict[str, Any]) -> bool:
    capability = receipt.get("capability")
    return bool(
        receipt.get("kind") == "capability_grant"
        and isinstance(capability, dict)
        and capability.get("effect") == "externalAct"
        and capability.get("source") == "grant"
    )


def _remaining(final_state: dict[str, Any]) -> int | None:
    return final_state["capabilities"]["A"]["externalAct"]["remaining_uses"]


def test_one_use_execution_and_feedback_verify() -> None:
    receipts, final_state = _run(ONE_USE_SOURCE)

    assert _remaining(final_state) == 0
    assert _verify(ONE_USE_SOURCE, receipts, final_state)["all_checks_pass"]

    extra_field = copy.deepcopy(receipts)
    feedback = next(item for item in extra_field if item.get("kind") == "feedback")
    feedback["action"]["noncanonical_extra"] = True
    _rehash(extra_field, final_state)
    assert not _verify(ONE_USE_SOURCE, extra_field, final_state)["all_checks_pass"]

    malformed = copy.deepcopy(receipts)
    feedback = next(item for item in malformed if item.get("kind") == "feedback")
    del feedback["action"]
    _rehash(malformed, final_state)
    report = _verify(ONE_USE_SOURCE, malformed, final_state)
    assert not report["all_checks_pass"]

    # Expiry constrains use, not grant existence: an intentionally unused,
    # already-expired grant remains a valid ledger entry.
    unused_expired = """\
module core04_unused_expired
lineage L_A
agent A lineage L_A
grant A effect externalAct uses 1 until 0
"""
    expired_receipts, expired_state = _run(unused_expired)
    assert _verify(unused_expired, expired_receipts, expired_state)["all_checks_pass"]


def test_two_use_capability_is_consumed_exactly_twice() -> None:
    receipts, final_state = _run(TWO_USE_SOURCE)

    assert _remaining(final_state) == 0
    assert _verify(TWO_USE_SOURCE, receipts, final_state)["all_checks_pass"]

    unused_receipts, unused_state = _run(UNUSED_EXPIRED_SOURCE)
    assert unused_state["step"] > 4
    assert _verify(UNUSED_EXPIRED_SOURCE, unused_receipts, unused_state)[
        "all_checks_pass"
    ]


def test_kernel_rejects_fully_rehashed_trace_missing_grant() -> None:
    receipts, final_state = _run(ONE_USE_SOURCE)
    receipts = [receipt for receipt in receipts if not _explicit_grant(receipt)]
    _rehash(receipts, final_state)

    assert not _verify(ONE_USE_SOURCE, receipts, final_state)["all_checks_pass"]

    receipts, final_state = _run(DEFAULT_GRANT_SOURCE)
    grant_index = next(
        index
        for index, receipt in enumerate(receipts)
        if receipt.get("kind") == "capability_grant"
        and receipt.get("capability", {}).get("source") == "default"
    )
    receipts.insert(grant_index + 1, copy.deepcopy(receipts[grant_index]))
    _rehash(receipts, final_state)
    assert not _verify(DEFAULT_GRANT_SOURCE, receipts, final_state)["all_checks_pass"]

    # The agent declaration authorizes exactly the three ordered defaults;
    # duplicating one is not a source-authorized grant epoch.
    receipts, final_state = _run(ONE_USE_SOURCE)
    default_grant = next(
        receipt
        for receipt in receipts
        if receipt.get("kind") == "capability_grant"
        and receipt.get("implicit") is True
    )
    insert_at = receipts.index(default_grant) + 1
    receipts.insert(insert_at, copy.deepcopy(default_grant))
    _rehash(receipts, final_state)
    assert not _verify(ONE_USE_SOURCE, receipts, final_state)["all_checks_pass"]


def test_kernel_rejects_fully_rehashed_forged_grant_digest() -> None:
    receipts, final_state = _run(ONE_USE_SOURCE)
    forged_digest = "f" * 64
    latest_action: dict[str, Any] | None = None

    for receipt in receipts:
        action = receipt.get("action")
        if receipt.get("kind") not in {"execute", "feedback"} or not isinstance(action, dict):
            continue
        if latest_action is not None and "prior_action_digest" in receipt:
            receipt["prior_action_digest"] = latest_action["action_digest"]
        action["capability_digest"] = forged_digest
        _refresh_action_digest(action)
        latest_action = copy.deepcopy(action)

    assert latest_action is not None
    final_state["actions"]["act"] = latest_action
    _rehash(receipts, final_state)

    assert not _verify(ONE_USE_SOURCE, receipts, final_state)["all_checks_pass"]


def test_kernel_rejects_fully_rehashed_execution_after_revoke() -> None:
    receipts, final_state = _run(ONE_USE_SOURCE)
    revoked_receipts, _ = _run(REVOKE_SOURCE)
    revoke = copy.deepcopy(
        next(receipt for receipt in revoked_receipts if receipt.get("kind") == "capability_revoke")
    )
    execute_index = next(
        index for index, receipt in enumerate(receipts) if receipt.get("kind") == "execute"
    )
    receipts.insert(execute_index, revoke)
    _rehash(receipts, final_state)

    assert not _verify(ONE_USE_SOURCE, receipts, final_state)["all_checks_pass"]


def test_kernel_rejects_fully_rehashed_expired_execution() -> None:
    receipts, final_state = _run(ONE_USE_SOURCE)
    execute_index = next(
        index for index, receipt in enumerate(receipts) if receipt.get("kind") == "execute"
    )
    execute_step = int(receipts[execute_index]["step"])
    for receipt in receipts[execute_index:]:
        if int(receipt.get("step", -1)) == execute_step:
            receipt["step"] = execute_step + 1
        else:
            break
    _rehash(receipts, final_state)

    assert not _verify(ONE_USE_SOURCE, receipts, final_state)["all_checks_pass"]

    receipts, final_state = _run(ONE_USE_SOURCE)
    execute_index = next(
        index for index, receipt in enumerate(receipts) if receipt.get("kind") == "execute"
    )
    original_step = int(receipts[execute_index]["step"])
    for receipt in receipts[execute_index:]:
        if int(receipt.get("step", -1)) == original_step:
            receipt["step"] = original_step - 1
        else:
            break
    _rehash(receipts, final_state)
    assert not _verify(ONE_USE_SOURCE, receipts, final_state)["all_checks_pass"]

    # Receipt time is derived from the source statement ordinal. Collapsing an
    # execute onto the prior plan step must not let an attacker choose the
    # instant at which expiry is evaluated.
    receipts, final_state = _run(ONE_USE_SOURCE)
    execute_index = next(
        index for index, receipt in enumerate(receipts) if receipt.get("kind") == "execute"
    )
    execute_step = int(receipts[execute_index]["step"])
    receipts[execute_index]["step"] = execute_step - 1
    execute_boundary = next(
        receipt
        for receipt in receipts[execute_index + 1 :]
        if receipt.get("kind") == "statement_commit"
    )
    execute_boundary["step"] = execute_step - 1
    _rehash(receipts, final_state)
    assert not _verify(ONE_USE_SOURCE, receipts, final_state)["all_checks_pass"]


def test_kernel_rejects_fully_rehashed_duplicate_execute() -> None:
    receipts, final_state = _run(DUPLICATE_EXECUTION_SOURCE)
    execute_index = next(
        index for index, receipt in enumerate(receipts) if receipt.get("kind") == "execute"
    )
    original = receipts[execute_index]
    duplicate = copy.deepcopy(original)
    action = duplicate["action"]
    if "prior_action_digest" in duplicate:
        duplicate["prior_action_digest"] = action["action_digest"]
    if isinstance(original.get("capability_after"), dict):
        duplicate["capability_before"] = copy.deepcopy(original["capability_after"])
        duplicate["capability_after"] = copy.deepcopy(original["capability_after"])
        remaining = duplicate["capability_after"].get("remaining_uses")
        if remaining is not None:
            duplicate["capability_after"]["remaining_uses"] = remaining - 1
    receipts.insert(execute_index + 1, duplicate)
    final_state["capabilities"]["A"]["externalAct"]["remaining_uses"] = 0
    _rehash(receipts, final_state)

    assert not _verify(DUPLICATE_EXECUTION_SOURCE, receipts, final_state)["all_checks_pass"]

    receipts, final_state = _run(DUPLICATE_EXECUTION_SOURCE)
    execute = next(receipt for receipt in receipts if receipt.get("kind") == "execute")
    execute["action"]["attacker_extension"] = True
    _rehash(receipts, final_state)
    assert not _verify(DUPLICATE_EXECUTION_SOURCE, receipts, final_state)["all_checks_pass"]


def test_kernel_rejects_fully_rehashed_duplicate_feedback() -> None:
    receipts, final_state = _run(ONE_USE_SOURCE)
    feedback_index = next(
        index for index, receipt in enumerate(receipts) if receipt.get("kind") == "feedback"
    )
    duplicate = copy.deepcopy(receipts[feedback_index])
    if "prior_action_digest" in duplicate:
        duplicate["prior_action_digest"] = duplicate["action"]["action_digest"]
    receipts.insert(feedback_index + 1, duplicate)
    _rehash(receipts, final_state)

    assert not _verify(ONE_USE_SOURCE, receipts, final_state)["all_checks_pass"]

    # Malformed numeric evidence is rejected as a report, never propagated as
    # an exception from the verifier boundary.
    receipts, final_state = _run(ONE_USE_SOURCE)
    feedback = next(receipt for receipt in receipts if receipt.get("kind") == "feedback")
    feedback["prediction_error"] = {"not": "a number"}
    _rehash(receipts, final_state)
    report = _verify(ONE_USE_SOURCE, receipts, final_state)
    assert report["all_checks_pass"] is False
    assert report["failure_count"] > 0


def test_kernel_rejects_exact_final_capability_mismatch() -> None:
    receipts, final_state = _run(TWO_USE_SOURCE)
    final_state["capabilities"]["A"]["externalAct"]["remaining_uses"] = 1
    _refresh_snapshot_digest(final_state)

    assert not _verify(TWO_USE_SOURCE, receipts, final_state)["all_checks_pass"]
