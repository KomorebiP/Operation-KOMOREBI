from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from proof_path_theory import (
    BridgeGraph,
    Certificate,
    ClaimNode,
    EvidenceKind,
    EvidenceRecord,
    GoalWeights,
    Justification,
    NodeKind,
    ProofField,
    Representation,
    ValueVector,
    append_only_derivability_preserved,
    bundled_schema,
    certificate_from_dict,
    load_proof_field,
    minimum_certificate,
    proof_field_from_dict,
    stopping_depth,
    weighted_estimator_variance,
)

ROOT = Path(__file__).resolve().parents[1]


def test_nonfinite_value_is_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        ValueVector(discovery=math.nan)


def test_repeated_evidence_reference_is_rejected() -> None:
    with pytest.raises(ValueError, match="repeats an evidence id"):
        Justification(
            "j",
            ("A",),
            "B",
            "rule",
            evidence_ids=("e", "e"),
        )


def test_representation_must_retain_its_certificate_nodes() -> None:
    certificate = Certificate(
        frozenset({"A", "B"}),
        frozenset({"j"}),
        frozenset({"B"}),
    )
    with pytest.raises(ValueError, match="certificate nodes"):
        Representation("broken", frozenset({"B"}), certificate=certificate)


def test_negative_goal_weight_is_rejected() -> None:
    with pytest.raises(ValueError, match="weight"):
        GoalWeights(discovery=-1.0)


def test_bridge_weights_must_be_known_and_nonnegative() -> None:
    graph = BridgeGraph(("A", "T"), (("A", "T"),))
    with pytest.raises(KeyError):
        graph.target_utility(("A",), {"missing": 1.0})
    with pytest.raises(ValueError, match="nonnegative"):
        graph.target_utility(("A",), {"T": -1.0})


def test_nonsymmetric_covariance_is_rejected() -> None:
    covariance = np.array([[1.0, 0.3], [0.2, 1.0]])
    with pytest.raises(ValueError, match="symmetric"):
        weighted_estimator_variance(np.array([0.5, 0.5]), covariance)


def test_unknown_schema_versions_are_rejected() -> None:
    with pytest.raises(ValueError, match="schema_version"):
        proof_field_from_dict({"schema_version": "9.9", "nodes": [], "justifications": []})
    with pytest.raises(ValueError, match="schema_version"):
        certificate_from_dict(
            {
                "schema_version": "9.9",
                "nodes": [],
                "justifications": [],
                "targets": ["T"],
            }
        )


def test_bundled_schemas_are_available() -> None:
    field_schema = bundled_schema("proof-field")
    certificate_schema = bundled_schema("certificate")
    assert field_schema["properties"]["schema_version"]["const"] == "1.0"
    assert certificate_schema["properties"]["schema_version"]["const"] == "1.0"


def test_append_only_check_rejects_evidence_mutation() -> None:
    earlier = ProofField(
        (
            ClaimNode("A", "premise", NodeKind.PREMISE),
            ClaimNode("B", "target", NodeKind.THEOREM),
        ),
        (Justification("j", ("A",), "B", "deduction", evidence_ids=("e",)),),
        premises=("A",),
        targets=("B",),
        evidence=(
            EvidenceRecord(
                "e",
                EvidenceKind.FORMAL_PROOF,
                "proof.tex",
                certifies=True,
            ),
        ),
    )
    later = ProofField(
        tuple(earlier.nodes.values()),
        tuple(earlier.justifications.values()),
        premises=earlier.premises,
        targets=earlier.targets,
        evidence=(
            EvidenceRecord(
                "e",
                EvidenceKind.INTERPRETATION,
                "proof.tex",
                certifies=False,
            ),
        ),
    )
    assert not append_only_derivability_preserved(earlier, later)


def test_search_and_stopping_guards() -> None:
    field = load_proof_field(ROOT / "examples" / "alternative_proofs.json")
    with pytest.raises(ValueError, match="positive"):
        minimum_certificate(field, max_search_states=0)
    with pytest.raises(ValueError, match="nonincreasing"):
        stopping_depth(
            [1.0, 1.1],
            [0.0, 1.0],
            residual_tolerance=0.1,
            marginal_gain_floor=0.01,
        )
