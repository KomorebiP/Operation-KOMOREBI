#!/usr/bin/env python3
"""Finalize a checksum manifest and build the deterministic Paper III ZIP."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
import zipfile


DEFAULT_ROOT_NAME = "Projector_Resolved_Seed_Calculus_III_v1.0.1"
DEFAULT_EPOCH = 1788393600
EXCLUDED_PARTS = {".git", ".lake", "__pycache__"}
EXCLUDED_SUFFIXES = {
    ".aux",
    ".fdb_latexmk",
    ".fls",
    ".ilean",
    ".log",
    ".olean",
    ".out",
    ".pyc",
    ".synctex.gz",
    ".toc",
    ".trace",
    ".zip",
}
SENTINEL_RE = re.compile(rb"__" + rb"FINAL_[A-Z0-9_]+__")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def excluded(relative: PurePosixPath) -> bool:
    relative_name = relative.as_posix()
    return any(part in EXCLUDED_PARTS for part in relative.parts) or any(
        relative_name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES
    )


def release_files(source: Path) -> list[Path]:
    files: list[Path] = []
    for path in source.rglob("*"):
        relative = PurePosixPath(path.relative_to(source).as_posix())
        if excluded(relative):
            continue
        if path.is_symlink():
            raise ValueError(f"release input contains a non-excluded symlink: {relative}")
        if path.is_file() and relative.as_posix() != "SHA256SUMS.txt":
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(source).as_posix().encode())


def check_finalized(source: Path, files: list[Path]) -> None:
    for path in files:
        match = SENTINEL_RE.search(path.read_bytes())
        if match is not None:
            relative = path.relative_to(source).as_posix()
            sentinel = match.group().decode("ascii")
            raise ValueError(f"unresolved release sentinel in {relative}: {sentinel}")


def write_manifest(source: Path, files: list[Path]) -> Path:
    manifest = source / "SHA256SUMS.txt"
    lines = [
        f"{sha256(path)}  {path.relative_to(source).as_posix()}"
        for path in files
    ]
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return manifest


def zip_info(name: str, epoch: int, mode: int, *, directory: bool) -> zipfile.ZipInfo:
    timestamp = time.gmtime(max(epoch, 315532800))[:6]
    info = zipfile.ZipInfo(name, date_time=timestamp)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED if directory else zipfile.ZIP_DEFLATED
    file_type = stat.S_IFDIR if directory else stat.S_IFREG
    info.external_attr = (file_type | mode) << 16
    if directory:
        info.external_attr |= 0x10
    return info


def build_zip(source: Path, output: Path, root_name: str, epoch: int) -> None:
    paths = sorted(
        (path for path in source.rglob("*") if not excluded(PurePosixPath(path.relative_to(source).as_posix()))),
        key=lambda path: path.relative_to(source).as_posix().encode(),
    )
    directories = [path for path in paths if path.is_dir() and not path.is_symlink()]
    files = [path for path in paths if path.is_file() and not path.is_symlink()]

    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        archive.writestr(zip_info(f"{root_name}/", epoch, 0o755, directory=True), b"")
        for directory in directories:
            relative = directory.relative_to(source).as_posix()
            archive.writestr(
                zip_info(f"{root_name}/{relative}/", epoch, 0o755, directory=True),
                b"",
            )
        for path in files:
            relative = path.relative_to(source).as_posix()
            mode = 0o755 if os.access(path, os.X_OK) else 0o644
            archive.writestr(
                zip_info(f"{root_name}/{relative}", epoch, mode, directory=False),
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )


def parse_args() -> argparse.Namespace:
    script_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=script_root)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root-name", default=DEFAULT_ROOT_NAME)
    parser.add_argument(
        "--epoch",
        type=int,
        default=int(os.environ.get("SOURCE_DATE_EPOCH", DEFAULT_EPOCH)),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing output ZIP",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if not source.is_dir():
        raise ValueError(f"source directory does not exist: {source}")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.root_name):
        raise ValueError("root name must contain only letters, digits, dot, underscore, or hyphen")
    if source == output or source in output.parents:
        raise ValueError("output ZIP must be outside the source release tree")
    if output.exists() and not args.force:
        raise FileExistsError(f"output exists (pass --force to replace it): {output}")
    if output.exists() and args.force:
        output.unlink()
    output.parent.mkdir(parents=True, exist_ok=True)

    files = release_files(source)
    check_finalized(source, files)
    write_manifest(source, files)
    subprocess.run([source / "VERIFY.sh"], cwd=source, check=True)
    build_zip(source, output, args.root_name, args.epoch)
    print(f"ZIP: {output}")
    print(f"SHA-256: {sha256(output)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
