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
from osl_semantic_numeric import (  # noqa: E402
    NumericSemanticReconstructor,
    digest,
    verify_numeric_semantics,
)


ZERO_DIGEST = "0" * 64


def _run(source: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    runtime = OSLRuntime()
    try:
        runtime.run_text(source)
    except OSLError:
        pass
    return copy.deepcopy(runtime.audit_log), runtime.state.snapshot()


def _rehash(receipts: list[dict[str, Any]]) -> None:
    previous = ZERO_DIGEST
    for index, receipt in enumerate(receipts):
        receipt["index"] = index
        receipt["state_index"] = index
        receipt["previous_digest"] = previous
        if receipt.get("kind") in {"program_complete", "program_reject"}:
            receipt["preterminal_chain_tip"] = previous
            receipt["audit_receipt_count"] = len(receipts)
        receipt.pop("digest", None)
        receipt["digest"] = digest(receipt)
        previous = receipt["digest"]


def _properties(report: dict[str, Any]) -> set[str]:
    return {failure["property"] for failure in report["failures"]}


FULL_NUMERIC_SOURCE = """\
module numeric_independence
space H dim 2
space K dim 2
vector x in H values [1.5,-2.0]
operator A : H -> K kind linear matrix [[2,0],[0,3]]
apply y = A(x)
operator P : H -> H kind projector matrix [[1,0],[0,0]]
operator T : H -> H kind linear matrix [[1,1],[0,1]]
transport P via T as P2
check_projector P2 tolerance 1e-12
operator J : H -> K kind linear matrix [[1,0],[0,1]]
operator L : H -> H kind linear matrix [[2,0],[0,1]]
operator R : K -> K kind linear matrix [[2,0],[0,1]]
check_intertwiner J between L and R tolerance 1e-12
"""


def test_reconstructs_complete_numerical_fragment_without_runtime_replay() -> None:
    receipts, final_state = _run(FULL_NUMERIC_SOURCE)
    report = verify_numeric_semantics(FULL_NUMERIC_SOURCE, receipts, final_state)

    assert report["all_checks_pass"], report["failures"]
    assert report["counters"]["numeric_statements"] == 13
    assert report["counters"]["numeric_receipts"] == 13
    assert report["reconstructed"]["vectors"]["y"]["value"] == [3.0, -6.0]
    assert report["reconstructed"]["operators"]["P2"]["matrix"] == [
        [1.0, -1.0],
        [0.0, 0.0],
    ]
    assert report["projector_checks"] == [
        {
            "statement_ordinal": 9,
            "operator": "P2",
            "residual": 0.0,
            "tolerance": 1e-12,
            "passed": True,
        }
    ]
    assert report["intertwiner_checks"][0]["passed"] is True


def test_rejects_consistently_rehashed_false_application_result() -> None:
    receipts, final_state = _run(FULL_NUMERIC_SOURCE)
    forged = copy.deepcopy(receipts)
    application = next(item for item in forged if item["kind"] == "operator_apply")
    application["result"]["value"] = [3.0, -5.0]
    _rehash(forged)

    report = verify_numeric_semantics(FULL_NUMERIC_SOURCE, forged, final_state)

    assert not report["all_checks_pass"]
    assert "operator_apply_value" in _properties(report)


def test_rejects_extra_numerical_receipt_field_under_strict_schema() -> None:
    receipts, final_state = _run(FULL_NUMERIC_SOURCE)
    forged = copy.deepcopy(receipts)
    application = next(item for item in forged if item["kind"] == "operator_apply")
    application["unbound_note"] = "forged"
    _rehash(forged)

    report = verify_numeric_semantics(FULL_NUMERIC_SOURCE, forged, final_state)

    assert not report["all_checks_pass"]
    assert "operator_apply_schema" in _properties(report)
    assert report["checks"]["strict_schemas"] is False


def test_rejects_final_vector_table_mutation() -> None:
    receipts, final_state = _run(FULL_NUMERIC_SOURCE)
    forged_state = copy.deepcopy(final_state)
    forged_state["vectors"]["y"]["value"] = [3.0, -5.0]

    report = verify_numeric_semantics(FULL_NUMERIC_SOURCE, receipts, forged_state)

    assert not report["all_checks_pass"]
    assert "final_vectors_correspondence" in _properties(report)


def test_independently_accepts_runtime_rejection_for_bad_projector() -> None:
    source = """\
module bad_projector
space H dim 2
operator badP : H -> H kind projector matrix [[1,1],[0,1]]
"""
    receipts, final_state = _run(source)

    report = verify_numeric_semantics(source, receipts, final_state)

    assert report["all_checks_pass"], report["failures"]
    assert report["counters"]["numeric_rejections"] == 1
    assert "badP" not in report["reconstructed"]["operators"]
    assert "declared projector but is not idempotent" in report["numeric_rejections"][0]["reason"]


def test_independently_accepts_runtime_rejection_for_singular_transport() -> None:
    source = """\
module singular_transport
space H dim 2
operator P : H -> H kind projector matrix [[1,0],[0,0]]
operator T : H -> H kind linear matrix [[1,0],[0,0]]
transport P via T as impossible
"""
    receipts, final_state = _run(source)

    report = verify_numeric_semantics(source, receipts, final_state)

    assert report["all_checks_pass"], report["failures"]
    assert report["numeric_rejections"][0]["statement_kind"] == "transport"
    assert "impossible" not in report["reconstructed"]["operators"]


def test_rejects_rehashed_projector_tolerance_mutation() -> None:
    receipts, final_state = _run(FULL_NUMERIC_SOURCE)
    forged = copy.deepcopy(receipts)
    check = next(item for item in forged if item["kind"] == "projector_check")
    check["tolerance"] = 1.0
    _rehash(forged)

    report = verify_numeric_semantics(FULL_NUMERIC_SOURCE, forged, final_state)

    assert not report["all_checks_pass"]
    assert "projector_check_tolerance" in _properties(report)


def test_transaction_rollback_restores_numerical_tables() -> None:
    source = """\
module numeric_rollback
space H dim 2
begin_transaction trial
vector temporary in H values [4,5]
operator P : H -> H kind projector matrix [[1,0],[0,0]]
rollback_transaction trial
"""
    receipts, final_state = _run(source)

    report = verify_numeric_semantics(source, receipts, final_state)

    assert report["all_checks_pass"], report["failures"]
    assert report["counters"]["transaction_rollbacks"] == 1
    assert report["reconstructed"]["spaces"] == {"H": {"name": "H", "dim": 2}}
    assert report["reconstructed"]["vectors"] == {}
    assert report["reconstructed"]["operators"] == {}


def test_automatic_transaction_rollback_restores_numerical_tables() -> None:
    source = """\
module numeric_auto_rollback
space H dim 2
begin_transaction trial
vector temporary in H values [4,5]
operator badP : H -> H kind projector matrix [[1,1],[0,1]]
commit_transaction trial
"""
    receipts, final_state = _run(source)

    report = verify_numeric_semantics(source, receipts, final_state)

    assert report["all_checks_pass"], report["failures"]
    assert report["counters"]["transaction_rollbacks"] == 1
    assert report["reconstructed"]["vectors"] == {}
    assert report["reconstructed"]["operators"] == {}


def test_malformed_inputs_fail_closed_without_raising() -> None:
    verifier = NumericSemanticReconstructor()

    report = verifier.verify("module malformed\n", [{"kind": "program_open"}], None)

    assert not report["all_checks_pass"]
    assert report["failure_count"] > 0


def test_independent_module_has_no_runtime_or_parser_import() -> None:
    source_text = (REFERENCE / "osl_semantic_numeric.py").read_text(encoding="utf-8")

    assert "import osl_core" not in source_text
    assert "from .osl_core" not in source_text
    assert "import osl_parser" not in source_text
    assert "from .osl_parser" not in source_text


@pytest.mark.parametrize(
    "filename",
    [
        "05_operator_projector.osl",
        "06_coordinate_transport.osl",
        "07_intertwiner.osl",
        "94_bad_projector.osl",
        "107_transaction_auto_rollback.osl",
    ],
)
def test_existing_numeric_corpus_examples(filename: str) -> None:
    source = (ROOT / "examples" / filename).read_text(encoding="utf-8")
    receipts, final_state = _run(source)

    report = verify_numeric_semantics(source, receipts, final_state)

    assert report["all_checks_pass"], (filename, report["failures"])
