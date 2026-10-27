from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping
import json
import os

from .hashing import sha256_object
from .schemas import AuditConfig


SEAL_SCHEMA = "sric.real-lrm.preaudit-seal.v1"


def source_date_epoch() -> int:
    raw = os.environ.get("SOURCE_DATE_EPOCH", "1788480000")
    return int(raw)


def build_protocol_seal(
    config: AuditConfig,
    *,
    external_repository: Mapping[str, Any],
    model_fingerprint: Mapping[str, Any],
    dataset_fingerprint: Mapping[str, Any],
    donor_plan_digest: str,
    output_contract: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "schema": SEAL_SCHEMA,
        "source_date_epoch": source_date_epoch(),
        "config": asdict(config),
        "external_repository": dict(external_repository),
        "model_fingerprint": dict(model_fingerprint),
        "dataset_fingerprint": dict(dataset_fingerprint),
        "donor_plan_digest": donor_plan_digest,
        "output_contract": dict(output_contract),
        "audit_outcomes_present": False,
    }
    return {**payload, "seal_sha256": sha256_object(payload)}


def write_seal(path: str | Path, seal: Mapping[str, Any]) -> None:
    Path(path).write_text(json.dumps(dict(seal), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_seal(seal: Mapping[str, Any]) -> None:
    if seal.get("schema") != SEAL_SCHEMA:
        raise ValueError("Unknown seal schema")
    stated = seal.get("seal_sha256")
    payload = {k: v for k, v in seal.items() if k != "seal_sha256"}
    actual = sha256_object(payload)
    if actual != stated:
        raise ValueError(f"Seal digest mismatch: expected {stated}, got {actual}")
    if seal.get("audit_outcomes_present") is not False:
        raise ValueError("Pre-audit seal contains or permits audit outcomes")


def load_and_verify_seal(path: str | Path) -> dict[str, Any]:
    seal = json.loads(Path(path).read_text(encoding="utf-8"))
    verify_seal(seal)
    return seal
