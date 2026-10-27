from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference"))

from osl_core import OSLRuntime  # noqa: E402
from osl_model import OSLStaticError  # noqa: E402


def _rejected(source: str, match: str) -> OSLRuntime:
    runtime = OSLRuntime()
    with pytest.raises(OSLStaticError, match=match):
        runtime.run_text(source)
    terminal = runtime.audit_log[-1]
    assert terminal["kind"] == "program_reject"
    assert terminal["phase"] in {"parse", "static"}
    assert terminal["reason_code"] in {"E_PARSE", "E_STATIC"}
    return runtime


def test_unknown_operator_kind_is_rejected() -> None:
    _rejected(
        """\
module bad_kind
space H dim 2
operator A : H -> H kind mystery matrix [[1,0],[0,1]]
""",
        "unknown operator kind",
    )


def test_transport_cannot_overwrite_an_existing_operator() -> None:
    _rejected(
        """\
module duplicate_transport_result
space H dim 2
operator A : H -> H kind linear matrix [[1,0],[0,1]]
operator T : H -> H kind transport matrix [[0,-1],[1,0]]
transport A via T as A
""",
        "already declared",
    )


@pytest.mark.parametrize(
    ("declarations", "message"),
    [
        ('secret private value "a"\nsecret private value "b"', "secret.*already declared"),
        (
            "metadata public value 1 source trusted\n"
            "metadata public value 2 source trusted",
            "metadata.*already declared",
        ),
    ],
)
def test_secret_and_metadata_names_are_unique(
    declarations: str, message: str
) -> None:
    _rejected(f"module duplicate_name\n{declarations}\n", message)


@pytest.mark.parametrize("confidence", ["-0.1", "1.1", "1e309"])
def test_infer_confidence_must_be_finite_probability(confidence: str) -> None:
    _rejected(
        f"""\
module bad_infer_confidence
lineage L
agent A lineage L
observe source by A content "source" confidence 0.8
infer result by A from source content "result" confidence {confidence}
""",
        "confidence must|numeric value must be finite",
    )


@pytest.mark.parametrize(
    ("statement", "message"),
    [
        (
            'vector x in H values [1,"not-a-number"]',
            "vector values must be a one-dimensional array of finite real numbers",
        ),
        (
            "vector x in H values [1,NaN]",
            "non-finite numeric literal",
        ),
        (
            "operator A : H -> H kind linear matrix [[1,0],[0,1e309]]",
            "non-finite numeric literal",
        ),
        (
            "operator A : H -> H kind linear matrix [[1,0],[0]]",
            "operator matrix must be a rectangular array of finite real numbers",
        ),
    ],
)
def test_malformed_and_nonfinite_numeric_inputs_are_audited_rejections(
    statement: str, message: str
) -> None:
    _rejected(f"module bad_numeric\nspace H dim 2\n{statement}\n", message)


def test_projector_must_be_a_square_endomorphism() -> None:
    _rejected(
        """\
module rectangular_projector
space H dim 2
space K dim 2
operator P : H -> K kind projector matrix [[1,0],[0,1]]
""",
        "projector must be a square endomorphism",
    )


def test_operator_matrix_must_match_declared_dimensions() -> None:
    _rejected(
        """\
module wrong_matrix_shape
space H dim 2
operator P : H -> H kind projector matrix [[1,0]]
""",
        "has shape.*expected",
    )


def test_projector_check_requires_an_endomorphism() -> None:
    _rejected(
        """\
module rectangular_projector_check
space H dim 2
space K dim 3
operator A : H -> K kind linear matrix [[1,0],[0,1],[0,0]]
check_projector A
""",
        "projector check requires a square endomorphism",
    )


@pytest.mark.parametrize(
    ("statement", "message"),
    [
        (
            "check_projector P tolerance -1e-9",
            "projector tolerance must be finite and nonnegative",
        ),
        (
            "check_projector P tolerance 1e309",
            "numeric value must be finite",
        ),
        (
            "check_intertwiner T between P and P tolerance -1e-9",
            "intertwiner tolerance must be finite and nonnegative",
        ),
        (
            "check_intertwiner T between P and P tolerance 1e309",
            "numeric value must be finite",
        ),
    ],
)
def test_operator_check_tolerances_are_finite_and_nonnegative(
    statement: str, message: str
) -> None:
    _rejected(
        f"""\
module bad_tolerance
space H dim 2
operator P : H -> H kind projector matrix [[1,0],[0,0]]
operator T : H -> H kind transport matrix [[1,0],[0,1]]
{statement}
""",
        message,
    )


def test_zero_tolerances_and_valid_numeric_inputs_remain_accepted() -> None:
    runtime = OSLRuntime()
    state = runtime.run_text(
        """\
module valid_numeric_boundary
space H dim 2
vector x in H values [1,0]
operator P : H -> H kind projector matrix [[1,0],[0,0]]
operator T : H -> H kind transport matrix [[1,0],[0,1]]
apply y = P(x)
check_projector P tolerance 0
check_intertwiner T between P and P tolerance 0
"""
    )
    assert state.vectors["y"].value.tolist() == [1.0, 0.0]
    assert runtime.audit_log[-1]["kind"] == "program_complete"
