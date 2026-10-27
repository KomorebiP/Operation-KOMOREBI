from __future__ import annotations

import pytest

from proof_path_theory import (
    ClaimNode,
    EvidenceKind,
    EvidenceRecord,
    Justification,
    NodeKind,
    ProofField,
    ValueVector,
)


def sample_field() -> ProofField:
    evidence = EvidenceRecord("proof", EvidenceKind.FORMAL_PROOF, "test", certifies=True)
    return ProofField(
        [
            ClaimNode("A", "A", NodeKind.PREMISE),
            ClaimNode("L", "lemma", NodeKind.LEMMA, ValueVector(verification=1)),
            ClaimNode("B", "B", NodeKind.THEOREM),
            ClaimNode("E", "example", NodeKind.EXAMPLE),
        ],
        [
            Justification("j1", ("A",), "L", "deduction", evidence_ids=("proof",)),
            Justification("j2", ("L",), "B", "deduction", evidence_ids=("proof",)),
            Justification("j3", ("A",), "E", "example", evidence_ids=("proof",)),
        ],
        premises=("A",),
        targets=("B",),
        evidence=(evidence,),
    )


def test_topological_order_respects_dependencies() -> None:
    field = sample_field()
    position = {node_id: index for index, node_id in enumerate(field.topological_order)}
    for left, right in field.dependency_edges():
        assert position[left] < position[right]


def test_derive_full_field() -> None:
    field = sample_field()
    assert field.derive() == frozenset({"A", "L", "B", "E"})


def test_derive_selected_subfield() -> None:
    field = sample_field()
    derived = field.derive(
        selected_nodes={"A", "L", "B"},
        selected_justifications={"j1", "j2"},
    )
    assert derived == frozenset({"A", "L", "B"})


def test_uncertified_justification_is_excluded() -> None:
    field = ProofField(
        [ClaimNode("A", "A", NodeKind.PREMISE), ClaimNode("B", "B")],
        [Justification("candidate", ("A",), "B", "guess", certified=False)],
        premises=("A",),
        targets=("B",),
    )
    assert "B" not in field.derive(certified_only=True)
    assert "B" in field.derive(certified_only=False)


def test_cycle_is_rejected() -> None:
    with pytest.raises(ValueError, match="cycle"):
        ProofField(
            [ClaimNode("A", "A"), ClaimNode("B", "B")],
            [
                Justification("j1", ("A",), "B", "rule"),
                Justification("j2", ("B",), "A", "rule"),
            ],
            targets=("B",),
        )


def test_unknown_reference_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown premise"):
        ProofField(
            [ClaimNode("B", "B")],
            [Justification("j", ("missing",), "B", "rule")],
            targets=("B",),
        )


def test_premise_must_be_leaf_kind() -> None:
    with pytest.raises(ValueError, match="leaf node kind"):
        ProofField([ClaimNode("A", "A", NodeKind.CLAIM)], [], premises=("A",))


def test_ancestors_and_descendants() -> None:
    field = sample_field()
    assert field.ancestors({"B"}) == frozenset({"A", "L", "B"})
    assert field.descendants({"A"}) == frozenset({"A", "L", "B", "E"})


def test_total_values() -> None:
    field = sample_field()
    assert field.total_values().verification == 1.0
