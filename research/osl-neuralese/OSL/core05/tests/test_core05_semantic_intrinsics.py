from __future__ import annotations

import copy
import sys
from pathlib import Path


REFERENCE = Path(__file__).resolve().parents[1] / "reference"
if str(REFERENCE) not in sys.path:
    sys.path.insert(0, str(REFERENCE))

from osl_core import OSLRuntime
from osl_semantic_intrinsics import digest, verify_intrinsic_semantics


SOURCE = """\
module intrinsic
lineage L_A
agent A lineage L_A
observe p by A content "evidence" confidence 1.0
verify_receipts
"""


def runtime_trace():
    runtime = OSLRuntime()
    runtime.run_text(SOURCE)
    return runtime.audit_log, runtime.state.snapshot()


def rehash(receipts):
    previous = "0" * 64
    for index, receipt in enumerate(receipts):
        receipt["index"] = index
        receipt["state_index"] = index
        receipt["previous_digest"] = previous
        unsigned = dict(receipt)
        unsigned.pop("digest", None)
        receipt["digest"] = digest(unsigned)
        previous = receipt["digest"]


def test_receipt_intrinsic_is_independently_recomputed() -> None:
    receipts, final_state = runtime_trace()
    report = verify_intrinsic_semantics(SOURCE, receipts, final_state)
    assert report["all_checks_pass"], report["failures"]
    assert report["counters"]["receipt_chain_verifications"] == 1


def test_fully_rehashed_forged_intrinsic_report_is_rejected() -> None:
    receipts, final_state = runtime_trace()
    mutated = copy.deepcopy(receipts)
    intrinsic = next(item for item in mutated if item["kind"] == "receipt_chain_verify")
    intrinsic["report"]["receipt_count"] = 0
    intrinsic["report"]["verification_digest"] = digest(
        {key: value for key, value in intrinsic["report"].items() if key != "verification_digest"}
    )
    rehash(mutated)
    report = verify_intrinsic_semantics(SOURCE, mutated, final_state)
    assert not report["all_checks_pass"]
    assert any(item["code"] == "intrinsic_receipt_report" for item in report["failures"])


def test_intrinsic_verifier_fails_closed() -> None:
    report = verify_intrinsic_semantics("verify_receipts", [None], {})  # type: ignore[list-item]
    assert not report["all_checks_pass"]
