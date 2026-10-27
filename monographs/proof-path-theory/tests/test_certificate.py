from __future__ import annotations

from pathlib import Path

import pytest

from proof_path_theory import (
    AlternativeJustificationError,
    Certificate,
    certificate_cost,
    load_proof_field,
    minimum_certificate,
    unique_and_dag_certificate,
    validate_certificate,
)


ROOT = Path(__file__).resolve().parents[1]


def test_unique_and_dag_core_is_valid_and_minimal() -> None:
    field = load_proof_field(ROOT / "examples" / "and_dag.json")
    certificate = unique_and_dag_certificate(field)
    assert certificate.node_ids == frozenset({"A", "D", "L1", "L2", "B"})
    assert validate_certificate(field, certificate).valid
    for node_id in certificate.node_ids.difference(field.premises | field.targets):
        smaller = Certificate(
            certificate.node_ids.difference({node_id}),
            certificate.justification_ids,
            certificate.targets,
        )
        assert not validate_certificate(field, smaller).valid


def test_alternative_field_rejects_unique_core_request() -> None:
    field = load_proof_field(ROOT / "examples" / "alternative_proofs.json")
    with pytest.raises(AlternativeJustificationError):
        unique_and_dag_certificate(field)


def test_minimum_certificate_selects_short_route() -> None:
    field = load_proof_field(ROOT / "examples" / "alternative_proofs.json")
    certificate = minimum_certificate(field)
    assert certificate.node_ids == frozenset({"A", "L-short", "B"})
    assert certificate.justification_ids == frozenset({"j-short", "j-B-short"})
    assert certificate_cost(field, certificate) == 1.0


def test_set_cover_encoding_has_cost_two() -> None:
    field = load_proof_field(ROOT / "examples" / "set_cover_certificate.json")
    certificate = minimum_certificate(field)
    selected_sets = certificate.node_ids.intersection({"S1", "S2", "S3", "S4"})
    assert len(selected_sets) == 2
    assert certificate_cost(field, certificate) == 2.0
    assert validate_certificate(field, certificate).valid


def test_invalid_certificate_reports_missing_target() -> None:
    field = load_proof_field(ROOT / "examples" / "and_dag.json")
    certificate = Certificate(
        frozenset({"A", "D"}),
        frozenset({"j-D"}),
        frozenset({"B"}),
    )
    report = validate_certificate(field, certificate)
    assert not report.valid
    assert report.missing_targets == frozenset({"B"})


def test_uncertified_certificate_is_rejected() -> None:
    field = load_proof_field(ROOT / "examples" / "and_dag.json")
    certificate = Certificate(
        frozenset({"A", "F"}),
        frozenset({"j-F"}),
        frozenset({"F"}),
    )
    report = validate_certificate(field, certificate)
    assert not report.valid
    assert report.uncertified_justifications == frozenset({"j-F"})


def test_search_limit_is_enforced() -> None:
    field = load_proof_field(ROOT / "examples" / "set_cover_certificate.json")
    with pytest.raises(RuntimeError, match="max_search_states"):
        minimum_certificate(field, max_search_states=1)
