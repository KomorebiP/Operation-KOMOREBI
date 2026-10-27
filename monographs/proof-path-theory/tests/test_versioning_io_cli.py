from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from proof_path_theory import (
    ClaimNode,
    Justification,
    NodeKind,
    ProofField,
    affected_descendants,
    append_only_derivability_preserved,
    certificate_from_dict,
    certificate_to_dict,
    load_proof_field,
    minimum_certificate,
    proof_field_from_dict,
    proof_field_to_dict,
    provenance_digest,
)

ROOT = Path(__file__).resolve().parents[1]


def test_io_round_trip() -> None:
    field = load_proof_field(ROOT / "examples" / "and_dag.json")
    clone = proof_field_from_dict(proof_field_to_dict(field))
    assert clone.topological_order == field.topological_order
    assert clone.nodes == field.nodes
    assert clone.justifications == field.justifications


def test_certificate_round_trip() -> None:
    field = load_proof_field(ROOT / "examples" / "alternative_proofs.json")
    certificate = minimum_certificate(field)
    assert certificate_from_dict(certificate_to_dict(certificate)) == certificate


def test_affected_descendants() -> None:
    field = load_proof_field(ROOT / "examples" / "and_dag.json")
    assert affected_descendants(field, {"L1"}, certified_only=True) == frozenset({"L1", "L2", "B"})


def test_append_only_update_preserves_derivability() -> None:
    earlier = load_proof_field(ROOT / "examples" / "alternative_proofs.json")
    later = ProofField(
        tuple(earlier.nodes.values()) + (ClaimNode("E", "extra example", NodeKind.EXAMPLE),),
        tuple(earlier.justifications.values()) + (Justification("j-extra", ("A",), "E", "example"),),
        premises=earlier.premises,
        targets=earlier.targets,
        evidence=tuple(earlier.evidence.values()),
        metadata=earlier.metadata,
    )
    assert append_only_derivability_preserved(earlier, later)


def test_provenance_digest_is_stable_and_order_sensitive() -> None:
    assert provenance_digest("A", "B") == provenance_digest("A", "B")
    assert provenance_digest("A", "B") != provenance_digest("B", "A")


def test_cli_validate_and_minimum(tmp_path: Path) -> None:
    field_path = ROOT / "examples" / "alternative_proofs.json"
    validate = subprocess.run(
        [sys.executable, "-m", "proof_path_theory.cli", "validate", str(field_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(validate.stdout)["valid"] is True
    output = tmp_path / "certificate.json"
    minimum = subprocess.run(
        [
            sys.executable,
            "-m",
            "proof_path_theory.cli",
            "minimum",
            str(field_path),
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert output.exists()
    assert json.loads(minimum.stdout)["cost"] == 1.0
