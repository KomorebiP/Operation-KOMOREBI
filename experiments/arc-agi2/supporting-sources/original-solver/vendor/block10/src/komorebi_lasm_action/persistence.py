"""Byte-stable persistence for target-free predictive capsule snapshots."""
from __future__ import annotations

import os
import tempfile
import hashlib
from pathlib import Path
from typing import Any, Mapping

from .canonical import (
    SNAPSHOT_FORMAT,
    canonical_bytes,
    canonical_value,
    content_hash,
    decode_json_bytes,
    require_sha256,
)
from .model import CapsuleSnapshot


MAX_SNAPSHOT_BYTES = 16 * 1024 * 1024


def snapshot_envelope(snapshot: CapsuleSnapshot) -> dict[str, Any]:
    if not isinstance(snapshot, CapsuleSnapshot):
        raise TypeError("snapshot must be a CapsuleSnapshot")
    body = {
        "format": SNAPSHOT_FORMAT,
        "snapshot_hash": snapshot.snapshot_hash,
        "snapshot": snapshot.to_record(),
    }
    return {**body, "envelope_hash": content_hash(body)}


def snapshot_to_bytes(snapshot: CapsuleSnapshot) -> bytes:
    """Serialize one snapshot to its unique canonical UTF-8 representation."""

    payload = canonical_bytes(snapshot_envelope(snapshot))
    if len(payload) > MAX_SNAPSHOT_BYTES:
        raise ValueError(f"snapshot exceeds {MAX_SNAPSHOT_BYTES} bytes")
    return payload


def snapshot_from_bytes(
    payload: bytes | bytearray | str,
    *,
    require_canonical: bool = True,
) -> CapsuleSnapshot:
    """Strictly decode and verify a snapshot envelope.

    Canonical input is required by default so two accepted byte streams cannot
    name the same persistent snapshot.  Set ``require_canonical=False`` only at
    a human-authored import boundary; reserialization is always canonical.
    """

    raw = payload.encode("utf-8") if isinstance(payload, str) else bytes(payload)
    if len(raw) > MAX_SNAPSHOT_BYTES:
        raise ValueError(f"snapshot exceeds {MAX_SNAPSHOT_BYTES} bytes")
    value = decode_json_bytes(raw)
    if not isinstance(value, Mapping):
        raise TypeError("snapshot envelope must be a JSON object")
    allowed = {"format", "snapshot_hash", "snapshot", "envelope_hash"}
    unknown = set(value) - allowed
    missing = allowed - set(value)
    if unknown:
        raise ValueError(f"unknown snapshot envelope fields: {sorted(unknown)}")
    if missing:
        raise ValueError(f"missing snapshot envelope fields: {sorted(missing)}")
    if value["format"] != SNAPSHOT_FORMAT:
        raise ValueError("unsupported snapshot format")
    expected_envelope_hash = content_hash(
        {
            "format": value["format"],
            "snapshot_hash": value["snapshot_hash"],
            "snapshot": value["snapshot"],
        }
    )
    require_sha256(value["envelope_hash"], "envelope_hash")
    if value["envelope_hash"] != expected_envelope_hash:
        raise ValueError("snapshot envelope hash does not match its contents")
    snapshot = CapsuleSnapshot.from_record(value["snapshot"])
    require_sha256(value["snapshot_hash"], "snapshot_hash")
    if value["snapshot_hash"] != snapshot.snapshot_hash:
        raise ValueError("envelope snapshot_hash does not match decoded snapshot")
    if require_canonical and raw != canonical_bytes(value):
        raise ValueError("snapshot payload is valid JSON but not canonical JSON")
    return snapshot


def snapshot_roundtrip(snapshot: CapsuleSnapshot) -> CapsuleSnapshot:
    """Round-trip a snapshot and prove exact canonical byte stability."""

    first = snapshot_to_bytes(snapshot)
    restored = snapshot_from_bytes(first)
    second = snapshot_to_bytes(restored)
    if first != second:
        raise RuntimeError("snapshot serialization is not byte-stable")
    if restored.snapshot_hash != snapshot.snapshot_hash:
        raise RuntimeError("snapshot identity changed across round-trip")
    return restored


def verify_snapshot_roundtrip(snapshot: CapsuleSnapshot) -> bool:
    snapshot_roundtrip(snapshot)
    return True


def save_snapshot(path: str | os.PathLike[str], snapshot: CapsuleSnapshot) -> str:
    """Atomically write one canonical snapshot and return its SHA-256 hash."""

    destination = Path(path)
    if destination.exists() and destination.is_dir():
        raise IsADirectoryError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = snapshot_to_bytes(snapshot)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
    return hashlib.sha256(payload).hexdigest()


def load_snapshot(
    path: str | os.PathLike[str], *, require_canonical: bool = True
) -> CapsuleSnapshot:
    source = Path(path)
    size = source.stat().st_size
    if size > MAX_SNAPSHOT_BYTES:
        raise ValueError(f"snapshot exceeds {MAX_SNAPSHOT_BYTES} bytes")
    with source.open("rb") as handle:
        payload = handle.read(MAX_SNAPSHOT_BYTES + 1)
    return snapshot_from_bytes(payload, require_canonical=require_canonical)


def snapshot_file_hash(path: str | os.PathLike[str]) -> str:
    source = Path(path)
    size = source.stat().st_size
    if size > MAX_SNAPSHOT_BYTES:
        raise ValueError(f"snapshot exceeds {MAX_SNAPSHOT_BYTES} bytes")
    with source.open("rb") as handle:
        payload = handle.read(MAX_SNAPSHOT_BYTES + 1)
    # Verification is intentional: this is the digest of an accepted snapshot,
    # not merely of arbitrary bytes bearing the expected file extension.
    snapshot_from_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


# Concise aliases used by command-line and integration layers.
dumps_snapshot = snapshot_to_bytes
loads_snapshot = snapshot_from_bytes
write_snapshot = save_snapshot
read_snapshot = load_snapshot


__all__ = [
    "MAX_SNAPSHOT_BYTES",
    "snapshot_envelope",
    "snapshot_to_bytes",
    "snapshot_from_bytes",
    "snapshot_roundtrip",
    "verify_snapshot_roundtrip",
    "save_snapshot",
    "load_snapshot",
    "snapshot_file_hash",
    "dumps_snapshot",
    "loads_snapshot",
    "write_snapshot",
    "read_snapshot",
]
