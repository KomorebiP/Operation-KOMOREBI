"""Restore the authenticated Block17 source and apply the isolated limit fix.

Python standard library only. Author: Komorebi P.
This prepares source files; it does not run compilers or establish a score.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import zipfile

ARCHIVE = "Komorebi_PR_LASM_Block17_Full_Bank_Integration.zip"
ARCHIVE_SHA256 = "457d66c2a45e729a3b4db9bae55a19d4f016f4a602090b82cb9e3380be3cd1b0"
PATCH_NAMES = ("entrants13/extraction.py", "bank13.json")
PATCH_SHA256 = {
    "entrants13/extraction.py": "e7e99cbb85f4b1a288f2145d38194b2bd7f44f8ee7212971c3410d497197e9a2",
    "bank13.json": "294d07bb868406cddda604f348f70a22c78945f1da9444a443889659f83cc020",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def relative_name(value: str) -> PurePosixPath:
    p = PurePosixPath(value)
    if not value or "\\" in value or p.is_absolute() or any(x in {"", ".", ".."} for x in value.split("/")):
        raise ValueError(f"unsafe relative path: {value!r}")
    if any(":" in x for x in p.parts):
        raise ValueError(f"unsafe relative path: {value!r}")
    return p


def verify_package(root: Path) -> dict:
    manifest = json.loads((root / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "komorebi.block17.limitfix.package.v1":
        raise ValueError("wrong package manifest schema")
    files = manifest["files"]
    for name, expected in files.items():
        relative_name(name)
        path = root / name
        if path.is_symlink() or not path.is_file() or sha256(path) != expected["sha256"] or path.stat().st_size != expected["bytes"]:
            raise ValueError(f"package member mismatch: {name}")
    required = {ARCHIVE, "original_source_identity.json", *("patches/" + n for n in PATCH_NAMES)}
    if not required.issubset(files):
        raise ValueError("missing pinned restore input")
    if files[ARCHIVE]["sha256"] != ARCHIVE_SHA256:
        raise ValueError("wrong original source archive")
    return manifest


def prepare(root: Path, destination: Path, apply_fix: bool = True) -> dict:
    root = root.resolve(strict=True)
    destination = destination.absolute()
    if os.path.lexists(destination):
        raise ValueError("destination already exists")
    destination = destination.resolve(strict=False)
    if destination == root or destination.is_relative_to(root):
        raise ValueError("destination must be outside the extracted package")
    destination.parent.mkdir(parents=True, exist_ok=True)
    verify_package(root)
    identity = json.loads((root / "original_source_identity.json").read_text(encoding="utf-8"))
    expected = identity["files"]
    for name in expected:
        relative_name(name)
    if len(expected) != 388:
        raise ValueError("wrong original source inventory")
    patches = {name: root / "patches" / name for name in PATCH_NAMES}
    if any(sha256(path) != PATCH_SHA256[name] for name, path in patches.items()):
        raise ValueError("wrong diagnostic correction payload")
    extraction_sha = sha256(patches["entrants13/extraction.py"])
    registry = json.loads(patches["bank13.json"].read_text(encoding="utf-8"))
    if registry.get("extraction") != extraction_sha:
        raise ValueError("patched registry does not pin patched extraction")

    with zipfile.ZipFile(root / ARCHIVE) as archive:
        members = archive.infolist()
        names = [item.filename for item in members]
        if len(set(names)) != len(names) or set(names) != {"block17/" + name for name in expected}:
            raise ValueError("source archive inventory mismatch")
        original_registry = json.loads(archive.read("block17/bank13.json"))
        expected_registry = {**original_registry, "extraction": extraction_sha}
        if registry != expected_registry:
            raise ValueError("registry patch changed entries other than extraction")
        if shutil.disk_usage(destination.parent).free < sum(item.file_size for item in members) + 1024 ** 3:
            raise ValueError("insufficient free disk space for source and reserve")
        # mkdir acquires the destination without replacing any pre-existing path.
        destination.mkdir()
        try:
            with tempfile.TemporaryDirectory(prefix=".limitfix-", dir=destination) as staging:
                stage = Path(staging)
                for item in members:
                    relative_name(item.filename)
                    if item.is_dir() or stat.S_ISLNK(item.external_attr >> 16):
                        raise ValueError("unexpected archive directory or symlink")
                    name = item.filename.removeprefix("block17/")
                    out = stage / "block17" / name
                    out.parent.mkdir(parents=True, exist_ok=True)
                    h = hashlib.sha256()
                    size = 0
                    with archive.open(item) as source, out.open("xb") as sink:
                        for chunk in iter(lambda: source.read(1024 * 1024), b""):
                            size += len(chunk)
                            h.update(chunk)
                            sink.write(chunk)
                    if size != item.file_size or h.hexdigest() != expected[name]:
                        raise ValueError(f"original source mismatch: {name}")
                changes = []
                for name, patch in (patches.items() if apply_fix else ()):
                    out = stage / "block17" / name
                    before = sha256(out)
                    shutil.copyfile(patch, out)
                    after = sha256(out)
                    if before == after:
                        raise ValueError(f"patch did not change source: {name}")
                    changes.append({"path": name, "before_sha256": before, "after_sha256": after})
                os.rename(stage / "block17", destination / "block17")
        except BaseException:
            # Only remove our reserved directory when empty. Do not remove other files.
            try:
                destination.rmdir()
            except OSError:
                pass
            raise
    return {"status": "prepared", "source_root": str(destination / "block17"),
            "authenticated_original_files": len(expected), "changes": changes,
            "source_version": "extraction_limitfix" if apply_fix else "original_Block17",
            "compilers_run": False, "new_evaluation_score": None}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    p.add_argument("--destination", type=Path)
    p.add_argument("--verify-only", action="store_true")
    p.add_argument("--original-only", action="store_true", help="restore the unchanged reference for fresh comparison")
    args = p.parse_args()
    try:
        if args.verify_only:
            manifest = verify_package(args.root.resolve(strict=True))
            result = {"status": "package_hashes_verified", "members": len(manifest["files"]), "compilers_run": False}
        else:
            if args.destination is None:
                p.error("--destination is required unless --verify-only is used")
            result = prepare(args.root, args.destination, apply_fix=not args.original_only)
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": f"{type(exc).__name__}: {exc}"}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
