from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping

from .model import ProofField


@dataclass(frozen=True, slots=True)
class ClaimRevision:
    claim_id: str
    status: str
    note: str = ""
    evidence_ids: tuple[str, ...] = ()
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("claim_id must be nonempty")
        if not self.status.strip():
            raise ValueError("status must be nonempty")
        if not self.timestamp_utc.strip():
            raise ValueError("timestamp_utc must be nonempty")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence_ids must be unique")


@dataclass(frozen=True, slots=True)
class LedgerSnapshot:
    version: str
    revisions: tuple[ClaimRevision, ...]
    parent_digest: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("version must be nonempty")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "parent_digest": self.parent_digest,
            "revisions": [
                {
                    "claim_id": revision.claim_id,
                    "status": revision.status,
                    "note": revision.note,
                    "evidence_ids": list(revision.evidence_ids),
                    "timestamp_utc": revision.timestamp_utc,
                }
                for revision in self.revisions
            ],
            "metadata": dict(sorted(self.metadata.items())),
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return sha256(encoded).hexdigest()


def affected_descendants(
    field: ProofField,
    changed_nodes: Iterable[str],
    *,
    certified_only: bool = False,
) -> frozenset[str]:
    """Return the conservative forward syntactic dependency closure."""
    changed = frozenset(changed_nodes)
    return field.descendants(
        changed,
        certified_only=certified_only,
        include_starts=True,
    )


def append_only_derivability_preserved(
    earlier: ProofField,
    later: ProofField,
    *,
    targets: Iterable[str] | None = None,
) -> bool:
    """Check the finite append-only condition that preserves earlier derivability."""
    if not set(earlier.nodes).issubset(later.nodes):
        return False
    for node_id, node in earlier.nodes.items():
        if later.nodes[node_id] != node:
            return False
    if not set(earlier.justifications).issubset(later.justifications):
        return False
    for justification_id, justification in earlier.justifications.items():
        if later.justifications[justification_id] != justification:
            return False
    if not set(earlier.evidence).issubset(later.evidence):
        return False
    for evidence_id, record in earlier.evidence.items():
        if later.evidence[evidence_id] != record:
            return False
    if not earlier.premises.issubset(later.premises):
        return False
    target_set = earlier.targets if targets is None else frozenset(targets)
    unknown_targets = target_set.difference(earlier.nodes)
    if unknown_targets:
        raise KeyError(sorted(unknown_targets)[0])
    earlier_derived = earlier.derive(certified_only=True)
    later_derived = later.derive(certified_only=True)
    return target_set.intersection(earlier_derived).issubset(later_derived)


def provenance_digest(*parts: str) -> str:
    """Hash an ordered string tuple using the version-2 provenance format.

    The versioned prefix and JSON array preserve tuple boundaries, empty parts,
    order, and Unicode code points before hashing. No Unicode normalization is
    performed. Parts must contain Unicode scalar values, not surrogate code
    points. This does not claim SHA-256 is collision-free.

    Digests differ from the legacy separator-joined format. Keep historical
    digests with their original format marker; see docs/PROVENANCE_FORMAT.md.
    LedgerSnapshot.digest has its own unchanged serialization contract.
    """
    if any(not isinstance(part, str) for part in parts):
        raise TypeError("provenance_digest parts must all be strings")
    if any(0xD800 <= ord(char) <= 0xDFFF for part in parts for char in part):
        raise ValueError("provenance_digest parts must not contain surrogate code points")
    encoded = json.dumps(list(parts), ensure_ascii=True, separators=(",", ":"))
    payload = b"proof-path-provenance:v2\x00" + encoded.encode("ascii")
    return sha256(payload).hexdigest()
