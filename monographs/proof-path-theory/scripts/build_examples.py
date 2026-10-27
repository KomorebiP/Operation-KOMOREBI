from pathlib import Path

from proof_path_theory import (
    ClaimNode,
    CostVector,
    EvidenceKind,
    EvidenceRecord,
    Justification,
    NodeKind,
    ProofField,
    ValueVector,
    save_proof_field,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def and_dag() -> ProofField:
    proof = EvidenceRecord("e-proof", EvidenceKind.FORMAL_PROOF, "declared derivation", certifies=True)
    exact = EvidenceRecord("e-exact", EvidenceKind.EXACT_COMPUTATION, "finite exact check", scope="displayed example", certifies=True)
    candidate = EvidenceRecord("e-candidate", EvidenceKind.CONJECTURE, "recorded failed route", certifies=False)
    nodes = [
        ClaimNode("A", "Premise A", NodeKind.PREMISE, ValueVector(verification=1), CostVector(storage=0.2, audit=0.1)),
        ClaimNode("D", "Definition", NodeKind.DEFINITION, ValueVector(verification=1, meaning=2), CostVector(storage=0.4, audit=0.2)),
        ClaimNode("L1", "First lemma", NodeKind.LEMMA, ValueVector(verification=2, discovery=1), CostVector(storage=0.8, audit=0.6)),
        ClaimNode("L2", "Second lemma", NodeKind.LEMMA, ValueVector(verification=2, meaning=1), CostVector(storage=0.7, audit=0.5)),
        ClaimNode("B", "Target theorem", NodeKind.THEOREM, ValueVector(verification=4), CostVector(storage=0.3, audit=0.4)),
        ClaimNode("E", "Worked example", NodeKind.EXAMPLE, ValueVector(discovery=2, meaning=3, bridge=1), CostVector(storage=0.7, recovery=1.0)),
        ClaimNode("F", "Failed route", NodeKind.FAILED_ROUTE, ValueVector(discovery=3, bridge=4), CostVector(storage=0.5, recovery=4.0)),
        ClaimNode("C", "Boundary case", NodeKind.BOUNDARY_CASE, ValueVector(discovery=2, meaning=2, bridge=3), CostVector(storage=0.6, recovery=2.5)),
    ]
    justifications = [
        Justification("j-D", ("A",), "D", "definition introduction", evidence_ids=("e-proof",)),
        Justification("j-L1", ("A", "D"), "L1", "deduction", evidence_ids=("e-proof",)),
        Justification("j-L2", ("L1",), "L2", "deduction", evidence_ids=("e-proof",)),
        Justification("j-B", ("L2",), "B", "deduction", evidence_ids=("e-proof",)),
        Justification("j-E", ("D",), "E", "exact example", evidence_ids=("e-exact",)),
        Justification("j-F", ("A",), "F", "candidate analogy", certified=False, evidence_ids=("e-candidate",)),
        Justification("j-C", ("E",), "C", "boundary extraction", evidence_ids=("e-exact",)),
    ]
    return ProofField(nodes, justifications, premises=("A",), targets=("B",), evidence=(proof, exact, candidate), metadata={"title": "AND-DAG proof field with optional discovery nodes"})


def alternative_proofs() -> ProofField:
    proof = EvidenceRecord("e-proof", EvidenceKind.FORMAL_PROOF, "two certified derivations", certifies=True)
    nodes = [
        ClaimNode("A", "Premise A", NodeKind.PREMISE, costs=CostVector(storage=0.0)),
        ClaimNode("L-short", "Short lemma", NodeKind.LEMMA, values=ValueVector(verification=2), costs=CostVector(storage=1.0)),
        ClaimNode("L-rich", "Explanatory lemma", NodeKind.LEMMA, values=ValueVector(verification=2, discovery=3, meaning=4, bridge=2), costs=CostVector(storage=3.0)),
        ClaimNode("B", "Target theorem", NodeKind.THEOREM, values=ValueVector(verification=4), costs=CostVector(storage=0.0)),
    ]
    justifications = [
        Justification("j-short", ("A",), "L-short", "short derivation", evidence_ids=("e-proof",)),
        Justification("j-rich", ("A",), "L-rich", "expanded derivation", evidence_ids=("e-proof",)),
        Justification("j-B-short", ("L-short",), "B", "conclusion via short lemma", evidence_ids=("e-proof",)),
        Justification("j-B-rich", ("L-rich",), "B", "conclusion via explanatory lemma", evidence_ids=("e-proof",)),
    ]
    return ProofField(nodes, justifications, premises=("A",), targets=("B",), evidence=(proof,), metadata={"title": "Alternative certified derivations"})


def set_cover_instance() -> ProofField:
    proof = EvidenceRecord("e-proof", EvidenceKind.FORMAL_PROOF, "finite set-cover encoding", certifies=True)
    universe = ("u1", "u2", "u3", "u4")
    subsets = {
        "S1": ("u1", "u2"),
        "S2": ("u2", "u3"),
        "S3": ("u3", "u4"),
        "S4": ("u1", "u4"),
    }
    nodes = [
        ClaimNode(name, f"Optional lemma {name}", NodeKind.AXIOM, costs=CostVector(storage=1.0))
        for name in subsets
    ]
    nodes.extend(
        ClaimNode(element, f"Element obligation {element}", NodeKind.CLAIM, costs=CostVector(storage=0.0))
        for element in universe
    )
    nodes.append(ClaimNode("T", "All obligations discharged", NodeKind.THEOREM, costs=CostVector(storage=0.0)))
    justifications = []
    for subset, elements in subsets.items():
        for element in elements:
            justifications.append(
                Justification(
                    f"j-{subset}-{element}",
                    (subset,),
                    element,
                    "coverage witness",
                    evidence_ids=("e-proof",),
                )
            )
    justifications.append(
        Justification("j-target", universe, "T", "conjunction", evidence_ids=("e-proof",))
    )
    return ProofField(nodes, justifications, targets=("T",), evidence=(proof,), metadata={"title": "Minimum certificate as set cover"})


def main() -> None:
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    save_proof_field(and_dag(), EXAMPLES / "and_dag.json")
    save_proof_field(alternative_proofs(), EXAMPLES / "alternative_proofs.json")
    save_proof_field(set_cover_instance(), EXAMPLES / "set_cover_certificate.json")


if __name__ == "__main__":
    main()
