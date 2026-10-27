from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, BinaryIO, Iterable


MANIFEST_NAME = "PACKAGE_MANIFEST.json"
MANIFEST_SCHEMA = "komorebi.neuralese.g1d.package_manifest.v1"
FIXED_SOURCE_SEED = 711001
FIXED_SOURCE_CONFIG_DIGEST = (
    "872349b749392924dab4b70eefe516751667d8d74ed91f73bb325b8277ce2a41"
)
FIXED_SOURCE_CHECKPOINT_SHA256 = (
    "ea0f9506334f6958c43e73596eb7404f785abd92be7668024b0c01efac1eae75"
)
FIXED_SOURCE_CLAIM = "G1_ENGINEERING_PASS"
FIXED_SOURCE_PACKAGE_MANIFEST_SHA256 = (
    "fb3a29e2c799fc1139fc7378b6bdf92f8d0dafc775ba8250021662a4ba0632d7"
)
FIXED_SOURCE_INVENTORY_SHA256 = (
    "9edb435418bc9a7d908a7dc0025db0b2adb0047f22e687d09c6b21925c8fa3bb"
)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_inventory(root: str | Path, *, exclude: Iterable[str] = ()) -> dict[str, Path]:
    package_root = Path(root).resolve()
    excluded = set(exclude)
    result: dict[str, Path] = {}
    for path in package_root.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"symlinks are not allowed: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(package_root)
        if relative.as_posix() in excluded:
            continue
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        name = relative.as_posix()
        if name in result:
            raise RuntimeError(f"duplicate file path: {name}")
        result[name] = path
    return result


def directory_hashes(root: str | Path) -> dict[str, dict[str, Any]]:
    return {
        name: {"size": path.stat().st_size, "sha256": sha256_file(path)}
        for name, path in sorted(file_inventory(root).items())
    }


def verify_fixed_source_identity(
    root: str | Path, source_verification: dict[str, Any]
) -> dict[str, Any]:
    """Fail closed unless *root* is the registered seed-711001 pilot."""

    run_root = Path(root).resolve()
    config_path = run_root / "resolved_config.json"
    checkpoint_path = run_root / "checkpoint.pt"
    if not config_path.is_file() or not checkpoint_path.is_file():
        raise RuntimeError("fixed source config or checkpoint is missing")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    observed_checkpoint_sha256 = sha256_file(checkpoint_path)
    observed_inventory_sha256 = hashlib.sha256(
        json.dumps(
            directory_hashes(run_root), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    expected_verification = {
        "status": "PASS",
        "profile": "pilot",
        "seed": FIXED_SOURCE_SEED,
        "claim": FIXED_SOURCE_CLAIM,
        "config_digest": FIXED_SOURCE_CONFIG_DIGEST,
        "package_manifest_sha256": FIXED_SOURCE_PACKAGE_MANIFEST_SHA256,
    }
    if any(
        source_verification.get(name) != value
        for name, value in expected_verification.items()
    ):
        raise RuntimeError("source-run verification is not the fixed registered pilot")
    if (
        config.get("seed") != FIXED_SOURCE_SEED
        or config.get("profile") != "pilot"
        or config.get("config_digest") != FIXED_SOURCE_CONFIG_DIGEST
        or observed_checkpoint_sha256 != FIXED_SOURCE_CHECKPOINT_SHA256
        or observed_inventory_sha256 != FIXED_SOURCE_INVENTORY_SHA256
    ):
        raise RuntimeError("source run does not match the fixed seed-711001 identity")
    return {
        "schema": "komorebi.neuralese.g1d.fixed_source.v1",
        "status": "PASS",
        "profile": "pilot",
        "seed": FIXED_SOURCE_SEED,
        "claim": FIXED_SOURCE_CLAIM,
        "config_digest": FIXED_SOURCE_CONFIG_DIGEST,
        "checkpoint_sha256": observed_checkpoint_sha256,
        "source_inventory_sha256": observed_inventory_sha256,
        "source_package_manifest_sha256": FIXED_SOURCE_PACKAGE_MANIFEST_SHA256,
        "cross_file_verification": source_verification,
    }


def verify_package_manifest(root: str | Path) -> dict[str, Any]:
    package_root = Path(root).resolve()
    manifest_path = package_root / MANIFEST_NAME
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise RuntimeError(f"{MANIFEST_NAME} is missing or invalid")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema",
        "entry_count",
        "entries",
    }:
        raise RuntimeError("package manifest top-level schema is malformed")
    if manifest["schema"] != MANIFEST_SCHEMA:
        raise RuntimeError("package manifest schema mismatch")
    entries = manifest["entries"]
    if (
        isinstance(manifest["entry_count"], bool)
        or not isinstance(manifest["entry_count"], int)
        or not isinstance(entries, list)
        or manifest["entry_count"] != len(entries)
    ):
        raise RuntimeError("package manifest entry count mismatch")
    expected: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "size", "sha256"}:
            raise RuntimeError("malformed package manifest entry")
        name = entry["path"]
        if (
            not isinstance(name, str)
            or not name
            or name.startswith("/")
            or "\\" in name
            or any(part in {"", ".", ".."} for part in name.split("/"))
            or name == MANIFEST_NAME
            or name in expected
        ):
            raise RuntimeError(f"invalid or duplicate manifest path: {name!r}")
        if (
            isinstance(entry["size"], bool)
            or not isinstance(entry["size"], int)
            or entry["size"] < 0
        ):
            raise RuntimeError(f"invalid manifest size: {name}")
        digest = entry["sha256"]
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or digest != digest.lower()
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise RuntimeError(f"invalid manifest hash: {name}")
        expected[name] = entry
    if list(expected) != sorted(expected):
        raise RuntimeError("manifest entries are not canonically ordered")
    observed = file_inventory(package_root, exclude=(MANIFEST_NAME,))
    if set(expected) != set(observed):
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        raise RuntimeError(f"package coverage mismatch; missing={missing}; extra={extra}")
    for name, path in observed.items():
        entry = expected[name]
        if path.stat().st_size != entry["size"] or sha256_file(path) != entry["sha256"]:
            raise RuntimeError(f"package byte mismatch: {name}")
    return {
        "schema": MANIFEST_SCHEMA,
        "entry_count": len(entries),
        "manifest_sha256": sha256_file(manifest_path),
    }


def atomic_json(path: str | Path, value: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=destination.name + ".", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def atomic_text(path: str | Path, value: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=destination.name + ".", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
            if not value.endswith("\n"):
                handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def acquire_lock(path: str | Path) -> BinaryIO:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle = destination.open("a+b")
    try:
        if destination.stat().st_size == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException:
        handle.close()
        raise RuntimeError(f"another process holds the diagnostic lock: {destination}")
    return handle


def release_lock(handle: BinaryIO) -> None:
    if handle.closed:
        return
    try:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()
