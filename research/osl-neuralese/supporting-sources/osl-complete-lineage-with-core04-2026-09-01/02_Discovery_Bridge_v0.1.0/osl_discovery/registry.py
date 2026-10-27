"""Append-only hash-chained registry for admitted OSL operators."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Mapping

from .core import CERTIFICATE_SCHEMA, digest_object, verify_certificate
from .worlds import canonical_json


REGISTRY_SCHEMA = "osl.discovery.registry-entry.v1"
GENESIS = "0" * 64


class RegistryError(ValueError):
    """Raised when registration is unsafe or a registry is malformed."""


def _read_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RegistryError(f"invalid JSON at registry line {line_number}") from exc
        if not isinstance(value, dict):
            raise RegistryError(f"registry line {line_number} is not an object")
        entries.append(value)
    return entries


def append_admission(path: str | Path, certificate: Mapping[str, Any]) -> dict[str, Any]:
    """Append one admitted certificate and return the exact registry entry."""

    if certificate.get("schema") != CERTIFICATE_SCHEMA:
        raise RegistryError("unsupported certificate schema")
    if certificate.get("status") != "ADMITTED" or certificate.get("decision") != "admit":
        raise RegistryError("only admitted certificates may enter the registry")
    certificate_verification = verify_certificate(None, certificate)
    if not certificate_verification["valid"]:
        raise RegistryError("certificate semantic replay or integrity check failed")
    certificate_digest = certificate["certificate_digest"]
    target = Path(path)
    entries = _read_entries(target)
    if entries:
        verification = verify_registry(target)
        if not verification["valid"]:
            raise RegistryError("refusing to append to an invalid registry")
        previous = entries[-1]["entry_digest"]
    else:
        previous = GENESIS
    duplicate = next(
        (entry for entry in entries if entry.get("transformation_id") == certificate.get("transformation_id")),
        None,
    )
    if duplicate is not None:
        raise RegistryError("transformation is already registered")
    entry = {
        "schema": REGISTRY_SCHEMA,
        "sequence": len(entries),
        "previous_entry_digest": previous,
        "certificate_digest": certificate_digest,
        "certificate": certificate,
        "candidate": certificate["candidate"],
        "transformation_id": certificate["transformation_id"],
        "representative": certificate["representative"],
    }
    entry["entry_digest"] = digest_object(entry)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json(entry) + "\n")
    return entry


def verify_registry(path: str | Path, expected_tip: str | None = None) -> dict[str, Any]:
    """Verify semantic replay, sequence, hashes, chain continuity, and an optional tip anchor."""

    target = Path(path)
    try:
        entries = _read_entries(target)
    except RegistryError as exc:
        return {
            "schema": "osl.discovery.registry-verification.v1",
            "valid": False,
            "entry_count": 0,
            "first_error": str(exc),
            "tip_digest": None,
        }
    previous = GENESIS
    seen_transformations: set[str] = set()
    error = None
    for index, entry in enumerate(entries):
        supplied_digest = entry.get("entry_digest")
        unsigned = dict(entry)
        unsigned.pop("entry_digest", None)
        certificate = entry.get("certificate")
        certificate_valid = isinstance(certificate, dict) and verify_certificate(None, certificate)["valid"]
        certificate_fields_match = bool(
            isinstance(certificate, dict)
            and entry.get("certificate_digest") == certificate.get("certificate_digest")
            and entry.get("candidate") == certificate.get("candidate")
            and entry.get("transformation_id") == certificate.get("transformation_id")
            and entry.get("representative") == certificate.get("representative")
        )
        checks = (
            entry.get("schema") == REGISTRY_SCHEMA,
            entry.get("sequence") == index,
            entry.get("previous_entry_digest") == previous,
            isinstance(supplied_digest, str) and supplied_digest == digest_object(unsigned),
            entry.get("transformation_id") not in seen_transformations,
            certificate_valid,
            certificate_fields_match,
        )
        if not all(checks):
            error = f"registry entry {index} failed structural, chain, digest, or uniqueness checks"
            break
        seen_transformations.add(entry["transformation_id"])
        previous = supplied_digest
    if error is None and expected_tip is not None and previous != expected_tip:
        error = "registry tip does not match the trusted expected tip"
    return {
        "schema": "osl.discovery.registry-verification.v1",
        "valid": error is None,
        "entry_count": len(entries),
        "first_error": error,
        "tip_digest": previous if entries else GENESIS,
        "expected_tip": expected_tip,
        "tip_anchor_matches": expected_tip is None or previous == expected_tip,
    }


__all__ = ["GENESIS", "REGISTRY_SCHEMA", "RegistryError", "append_admission", "verify_registry"]
