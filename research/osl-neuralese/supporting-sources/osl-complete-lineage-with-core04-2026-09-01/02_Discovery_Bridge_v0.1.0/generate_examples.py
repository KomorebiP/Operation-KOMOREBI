"""Regenerate all committed examples from their source proposals."""

from __future__ import annotations

import json
from pathlib import Path

from osl_discovery import append_admission, emit_osl, synthesize, verify_registry
from osl_discovery.worlds import canonical_json


ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"
GENERATED = ROOT / "generated"
CASES = {
    "flip_both": "flip_both_proposal.json",
    "ambiguous": "ambiguous_proposal.json",
    "inconsistent": "inconsistent_proposal.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    GENERATED.mkdir(exist_ok=True)
    certificates = {}
    report = {"schema": "osl.discovery.example-generation.v1", "cases": {}}
    for stem, proposal_name in CASES.items():
        proposal = load(EXAMPLES / proposal_name)
        certificate = synthesize(proposal)
        certificates[stem] = certificate
        write_json(GENERATED / f"{stem}_certificate.json", certificate)
        decision_name = {
            "admit": "admission",
            "quarantine": "quarantine",
            "reject": "rejection",
        }[certificate["decision"]]
        (GENERATED / f"{stem}_{decision_name}.osl").write_text(
            emit_osl(proposal, certificate), encoding="utf-8", newline="\n"
        )
        report["cases"][stem] = {
            "status": certificate["status"],
            "decision": certificate["decision"],
            "certificate_digest": certificate["certificate_digest"],
        }

    registry = GENERATED / "OPERATOR_REGISTRY.jsonl"
    registry.write_text("", encoding="utf-8", newline="\n")
    entry = append_admission(registry, certificates["flip_both"])
    registry_report = verify_registry(registry, expected_tip=entry["entry_digest"])
    report["registry"] = registry_report
    write_json(GENERATED / "GENERATION_REPORT.json", report)
    print(canonical_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
