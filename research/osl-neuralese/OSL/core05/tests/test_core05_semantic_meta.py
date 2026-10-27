from __future__ import annotations

import copy
import sys
from pathlib import Path


REFERENCE = Path(__file__).resolve().parents[1] / "reference"
if str(REFERENCE) not in sys.path:
    sys.path.insert(0, str(REFERENCE))

from osl_core import OSLRuntime
from osl_semantic_meta import verify_meta_semantics


def run(source: str):
    runtime = OSLRuntime()
    state = runtime.run_text(source)
    return runtime, state.snapshot()


def metadata_source() -> str:
    return """\
module meta_semantics
lineage L_A
agent A lineage L_A
secret private_goal value {"target":"alpha","rank":3}
metadata public_stamp value [7,8] source trusted
metadata exposed from_secret private_goal source agent
assert metadata public_stamp equals [7,8]
show
"""


def test_meta_semantics_reconstructs_exact_final_state() -> None:
    runtime, final_state = run(metadata_source())
    report = verify_meta_semantics(metadata_source(), runtime.audit_log, final_state)
    assert report["all_checks_pass"], report["failures"]
    assert report["counters"] == {
        "secret_registers": 1,
        "metadata_publications": 2,
        "assertions": 1,
        "shows": 1,
        "transaction_restores": 0,
    }
    assert report["reconstructed"]["metadata"] == final_state["metadata"]
    assert report["reconstructed"]["secret_digests"] == final_state["secret_digests"]
    assert report["reconstructed"]["assertions"] == 1


def test_meta_semantics_restores_secret_metadata_and_assertions_on_rollback() -> None:
    source = """\
module meta_rollback
secret stable value "outside"
begin_transaction provisional
secret temporary value "inside"
metadata temporary_public from_secret temporary source agent
assert metadata temporary_public equals "inside"
rollback_transaction provisional
show
"""
    runtime, final_state = run(source)
    report = verify_meta_semantics(source, runtime.audit_log, final_state)
    assert report["all_checks_pass"], report["failures"]
    assert report["reconstructed"]["secret_digests"] == final_state["secret_digests"]
    assert set(final_state["secret_digests"]) == {"stable"}
    assert final_state["metadata"] == {}
    assert final_state["assertions"] == 0
    assert report["counters"]["transaction_restores"] == 1


def test_meta_semantics_rejects_rehashed_value_claim_semantically() -> None:
    runtime, final_state = run(metadata_source())
    mutated = copy.deepcopy(runtime.audit_log)
    receipt = next(item for item in mutated if item["kind"] == "metadata_publish")
    receipt["metadata_digest"] = "0" * 64
    report = verify_meta_semantics(metadata_source(), mutated, final_state)
    assert not report["all_checks_pass"]
    assert any(item["code"] == "metadata_digest" for item in report["failures"])


def test_meta_semantics_rejects_assertion_and_show_mutations() -> None:
    runtime, final_state = run(metadata_source())
    mutated = copy.deepcopy(runtime.audit_log)
    assertion = next(item for item in mutated if item["kind"] == "assert_pass")
    assertion["assertion_count"] = 9
    show = next(item for item in mutated if item["kind"] == "show")
    show["semantic_digest"] = "f" * 64
    report = verify_meta_semantics(metadata_source(), mutated, final_state)
    assert not report["all_checks_pass"]
    codes = {item["code"] for item in report["failures"]}
    assert "assert_count" in codes
    assert "show_boundary_semantic_digest" in codes


def test_meta_semantics_compares_final_state_bidirectionally() -> None:
    runtime, final_state = run(metadata_source())
    mutated_state = copy.deepcopy(final_state)
    mutated_state["metadata"]["invented"] = {
        "value": 1,
        "source": "trusted",
        "step": 1,
        "digest": "0" * 64,
    }
    report = verify_meta_semantics(metadata_source(), runtime.audit_log, mutated_state)
    assert not report["all_checks_pass"]
    assert any(
        item["code"] == "meta_final_state_mismatch"
        and item.get("field") == "metadata"
        for item in report["failures"]
    )


def test_meta_semantics_fails_closed_on_malformed_input() -> None:
    report = verify_meta_semantics("secret", [{"kind": "metadata_publish"}], {})
    assert not report["all_checks_pass"]
    assert report["failures"]
