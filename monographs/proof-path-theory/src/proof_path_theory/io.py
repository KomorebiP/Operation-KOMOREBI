from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any, Mapping

from .certificate import Certificate
from .model import (
    ClaimNode,
    CostVector,
    EvidenceKind,
    EvidenceRecord,
    Justification,
    NodeKind,
    ProofField,
    ValueVector,
)


def bundled_schema(kind: str = "proof-field") -> dict[str, Any]:
    """Load a JSON Schema bundled with the installed package."""
    names = {
        "proof-field": "proof-field.schema.json",
        "certificate": "certificate.schema.json",
    }
    try:
        filename = names[kind]
    except KeyError as exc:
        raise ValueError("kind must be 'proof-field' or 'certificate'") from exc
    resource = files("proof_path_theory").joinpath("schemas", filename)
    payload = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("bundled schema is not a JSON object")
    return payload


def proof_field_to_dict(field: ProofField) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "metadata": field.metadata,
        "premises": sorted(field.premises),
        "targets": sorted(field.targets),
        "nodes": [
            {
                "id": node.id,
                "label": node.label,
                "kind": node.kind.value,
                "values": node.values.as_dict(),
                "costs": node.costs.as_dict(),
                "metadata": dict(node.metadata),
            }
            for node in sorted(field.nodes.values(), key=lambda item: item.id)
        ],
        "evidence": [
            {
                "id": record.id,
                "kind": record.kind.value,
                "source": record.source,
                "scope": record.scope,
                "certifies": record.certifies,
                "note": record.note,
            }
            for record in sorted(field.evidence.values(), key=lambda item: item.id)
        ],
        "justifications": [
            {
                "id": justification.id,
                "premises": list(justification.premises),
                "conclusion": justification.conclusion,
                "rule": justification.rule,
                "certified": justification.certified,
                "evidence_ids": list(justification.evidence_ids),
                "metadata": dict(justification.metadata),
            }
            for justification in sorted(
                field.justifications.values(), key=lambda item: item.id
            )
        ],
    }


def _require_list(payload: Mapping[str, Any], key: str) -> list[Any]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a JSON array")
    return value


def _strict_bool(item: Mapping[str, Any], key: str, default: bool) -> bool:
    value = item.get(key, default)
    if type(value) is not bool:
        raise ValueError(f"{key} must be a JSON boolean, not a coerced value")
    return value


def proof_field_from_dict(payload: Mapping[str, Any]) -> ProofField:
    version = str(payload.get("schema_version", "1.0"))
    if version != "1.0":
        raise ValueError(f"unsupported proof-field schema_version: {version}")
    nodes = [
        ClaimNode(
            id=str(item["id"]),
            label=str(item.get("label", item["id"])),
            kind=NodeKind(item.get("kind", NodeKind.CLAIM.value)),
            values=ValueVector(**item.get("values", {})),
            costs=CostVector(**item.get("costs", {})),
            metadata=item.get("metadata", {}),
        )
        for item in _require_list(payload, "nodes")
    ]
    evidence = [
        EvidenceRecord(
            id=str(item["id"]),
            kind=EvidenceKind(item["kind"]),
            source=str(item["source"]),
            scope=str(item.get("scope", "")),
            certifies=_strict_bool(item, "certifies", False),
            note=str(item.get("note", "")),
        )
        for item in _require_list(payload, "evidence")
    ]
    justifications = [
        Justification(
            id=str(item["id"]),
            premises=tuple(str(value) for value in item.get("premises", [])),
            conclusion=str(item["conclusion"]),
            rule=str(item.get("rule", "unspecified")),
            certified=_strict_bool(item, "certified", True),
            evidence_ids=tuple(str(value) for value in item.get("evidence_ids", [])),
            metadata=item.get("metadata", {}),
        )
        for item in _require_list(payload, "justifications")
    ]
    return ProofField(
        nodes,
        justifications,
        premises=payload.get("premises", []),
        targets=payload.get("targets", []),
        evidence=evidence,
        metadata=payload.get("metadata", {}),
    )


def load_proof_field(path: str | Path) -> ProofField:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("proof-field JSON must contain an object")
    return proof_field_from_dict(payload)


def save_proof_field(field: ProofField, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(proof_field_to_dict(field), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def certificate_to_dict(certificate: Certificate) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "nodes": sorted(certificate.node_ids),
        "justifications": sorted(certificate.justification_ids),
        "targets": sorted(certificate.targets),
    }


def certificate_from_dict(payload: Mapping[str, Any]) -> Certificate:
    version = str(payload.get("schema_version", "1.0"))
    if version != "1.0":
        raise ValueError(f"unsupported certificate schema_version: {version}")
    return Certificate(
        node_ids=frozenset(str(value) for value in payload.get("nodes", [])),
        justification_ids=frozenset(
            str(value) for value in payload.get("justifications", [])
        ),
        targets=frozenset(str(value) for value in payload.get("targets", [])),
    )


def load_certificate(path: str | Path) -> Certificate:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("certificate JSON must contain an object")
    return certificate_from_dict(payload)


def save_certificate(certificate: Certificate, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(certificate_to_dict(certificate), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path
