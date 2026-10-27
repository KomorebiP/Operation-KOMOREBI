from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, BinaryIO


PACKAGE_MANIFEST_NAME = "PACKAGE_MANIFEST.json"
PACKAGE_MANIFEST_SCHEMA = "komorebi.neuralese.g1.package_manifest.v1"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_file_inventory(root: str | Path) -> dict[str, Path]:
    """Return every release file covered by the package manifest."""
    package_root = Path(root).resolve()
    if not package_root.is_dir():
        raise FileNotFoundError(f"package directory not found: {package_root}")
    files: dict[str, Path] = {}
    for path in package_root.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"package symlinks are not allowed: {path}")
        if not path.is_file() or path == package_root / PACKAGE_MANIFEST_NAME:
            continue
        relative = path.relative_to(package_root)
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        name = relative.as_posix()
        if name in files:
            raise RuntimeError(f"duplicate package path: {name}")
        files[name] = path
    return files


def verify_package_manifest(root: str | Path) -> dict[str, Any]:
    """Fail closed unless the manifest exactly covers the current package bytes."""
    package_root = Path(root).resolve()
    manifest_path = package_root / PACKAGE_MANIFEST_NAME
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise RuntimeError(f"{PACKAGE_MANIFEST_NAME} is missing or is not a regular file")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"cannot read {PACKAGE_MANIFEST_NAME}: {error}") from error
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema",
        "entry_count",
        "entries",
    }:
        raise RuntimeError("package manifest top-level schema is malformed")
    if manifest["schema"] != PACKAGE_MANIFEST_SCHEMA:
        raise RuntimeError("package manifest schema mismatch")
    entries = manifest["entries"]
    count = manifest["entry_count"]
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or count < 0
        or not isinstance(entries, list)
        or count != len(entries)
    ):
        raise RuntimeError("package manifest entry count mismatch")
    expected: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "size", "sha256"}:
            raise RuntimeError("malformed package manifest entry")
        name = entry["path"]
        size = entry["size"]
        digest = entry["sha256"]
        if (
            not isinstance(name, str)
            or not name
            or name.startswith("/")
            or "\\" in name
            or any(part in {"", ".", ".."} for part in name.split("/"))
            or name == PACKAGE_MANIFEST_NAME
        ):
            raise RuntimeError(f"invalid manifest path: {name!r}")
        if name in expected:
            raise RuntimeError(f"duplicate manifest path: {name}")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise RuntimeError(f"invalid manifest size: {name}")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or digest != digest.lower()
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise RuntimeError(f"invalid manifest hash: {name}")
        expected[name] = entry
    if list(expected) != sorted(expected):
        raise RuntimeError("package manifest entries are not canonically ordered")
    observed = package_file_inventory(package_root)
    if set(expected) != set(observed):
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        raise RuntimeError(f"package coverage mismatch; missing={missing}; extra={extra}")
    for name, path in observed.items():
        entry = expected[name]
        if path.stat().st_size != entry["size"]:
            raise RuntimeError(f"package size mismatch: {name}")
        if sha256_file(path) != entry["sha256"]:
            raise RuntimeError(f"package hash mismatch: {name}")
    return {
        "schema": PACKAGE_MANIFEST_SCHEMA,
        "entry_count": count,
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


def append_jsonl(path: str | Path, value: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def acquire_run_lock(path: str | Path) -> BinaryIO:
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
        raise RuntimeError(f"another process holds the run lock: {destination}")
    return handle


def release_run_lock(handle: BinaryIO) -> None:
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
