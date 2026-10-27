#!/usr/bin/env python3
"""Create and verify a deterministic, manifest-driven Paper IV ZIP."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
import zipfile


MANIFEST = "SHA256SUMS.txt"
FIXED_TIME = (2026, 9, 5, 0, 0, 0)
IGNORED_DIRECTORIES = {
    ".git",
    ".lake",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}
IGNORED_SUFFIXES = {
    ".aux",
    ".bbl",
    ".blg",
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
}
PORTABLE_COMPONENT = re.compile(
    r"(?:[A-Za-z0-9][A-Za-z0-9._+-]*|\.[A-Za-z0-9][A-Za-z0-9._+-]*)\Z"
)


class PackagingError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ignored(name: str) -> bool:
    pure = PurePosixPath(name)
    return any(part in IGNORED_DIRECTORIES for part in pure.parts) or any(
        name.endswith(suffix) for suffix in IGNORED_SUFFIXES
    )


def validate_relative_name(name: str) -> None:
    pure = PurePosixPath(name)
    if (
        not name
        or pure.is_absolute()
        or "\\" in name
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        raise PackagingError(f"unsafe relative path: {name!r}")
    if len(name.encode("utf-8")) > 180:
        raise PackagingError(f"relative path is too long: {name!r}")
    for part in pure.parts:
        if len(part.encode("utf-8")) > 80:
            raise PackagingError(f"path component is too long: {part!r}")
        if PORTABLE_COMPONENT.fullmatch(part) is None:
            raise PackagingError(f"nonportable path component: {part!r}")


def release_files(root: Path) -> list[str]:
    files: list[str] = []
    folded: dict[str, str] = {}
    for path in root.rglob("*"):
        name = path.relative_to(root).as_posix()
        if ignored(name) or name == MANIFEST:
            continue
        if path.is_symlink():
            raise PackagingError(f"release file is a symbolic link: {name}")
        if not path.is_file():
            continue
        validate_relative_name(name)
        prior = folded.get(name.casefold())
        if prior is not None and prior != name:
            raise PackagingError(
                f"case-insensitive path collision: {prior!r} and {name!r}"
            )
        folded[name.casefold()] = name
        files.append(name)
    return sorted(files, key=lambda value: value.encode("utf-8"))


def write_manifest(root: Path, files: list[str]) -> None:
    lines = [f"{sha256_file(root / name)}  {name}\n" for name in files]
    target = root / MANIFEST
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="\n", dir=root, delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.writelines(lines)
    temporary.replace(target)


def read_manifest(root: Path) -> tuple[list[str], dict[str, str]]:
    path = root / MANIFEST
    if not path.is_file() or path.is_symlink():
        raise PackagingError(f"missing regular {MANIFEST}")
    pattern = re.compile(r"([0-9a-f]{64})  ([^\x00-\x1f\x7f]+)\Z")
    names: list[str] = []
    digests: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = pattern.fullmatch(line)
        if match is None:
            raise PackagingError(f"malformed manifest line {number}")
        digest, name = match.groups()
        validate_relative_name(name)
        if name == MANIFEST:
            raise PackagingError("the checksum manifest must not list itself")
        if name in digests:
            raise PackagingError(f"duplicate manifest path: {name}")
        names.append(name)
        digests[name] = digest
    expected_order = sorted(names, key=lambda value: value.encode("utf-8"))
    if names != expected_order:
        raise PackagingError("manifest paths are not sorted bytewise")
    return names, digests


def zip_info(archive_name: str, executable: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(archive_name, FIXED_TIME)
    info.create_system = 3
    mode = 0o755 if executable else 0o644
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def build_zip(root: Path, output: Path, prefix: str, force: bool) -> None:
    validate_relative_name(prefix)
    if "/" in prefix:
        raise PackagingError("archive prefix must be one short path component")
    root = root.resolve()
    output = output.resolve()
    if output == root or root in output.parents:
        raise PackagingError("ZIP output must be outside the release root")
    if output.exists() and not force:
        raise PackagingError(f"output already exists: {output}")

    disk_files = release_files(root)
    names, digests = read_manifest(root)
    if names != disk_files:
        missing = sorted(set(disk_files) - set(names))
        extra = sorted(set(names) - set(disk_files))
        raise PackagingError(
            f"manifest/file-set mismatch; missing={missing}; extra={extra}"
        )
    for name in names:
        actual = sha256_file(root / name)
        if actual != digests[name]:
            raise PackagingError(
                f"disk checksum mismatch for {name}: {actual} != {digests[name]}"
            )

    members = sorted([MANIFEST, *names], key=lambda value: value.encode("utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=output.parent, suffix=".zip", delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(
            temporary,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            strict_timestamps=True,
        ) as archive:
            for name in members:
                data = (root / name).read_bytes()
                executable = name == "VERIFY.sh"
                archive.writestr(
                    zip_info(f"{prefix}/{name}", executable),
                    data,
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
        verify_zip(temporary, root, prefix, names, digests)
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def verify_zip(
    archive_path: Path,
    root: Path,
    prefix: str,
    names: list[str],
    digests: dict[str, str],
) -> None:
    expected = [f"{prefix}/{name}" for name in sorted(
        [MANIFEST, *names], key=lambda value: value.encode("utf-8")
    )]
    with zipfile.ZipFile(archive_path, "r") as archive:
        infos = archive.infolist()
        raw_names = [info.filename for info in infos]
        if raw_names != expected or len(raw_names) != len(set(raw_names)):
            raise PackagingError("archive members do not exactly match the manifest")
        if archive.testzip() is not None:
            raise PackagingError("archive CRC validation failed")
        for info in infos:
            if info.is_dir() or info.flag_bits & 0x1:
                raise PackagingError(f"invalid archive member: {info.filename}")
            if info.compress_type != zipfile.ZIP_DEFLATED:
                raise PackagingError(
                    f"unexpected compression method: {info.filename}"
                )
            mode = info.external_attr >> 16
            if mode and not stat.S_ISREG(mode):
                raise PackagingError(f"non-regular archive member: {info.filename}")
            if ".lake" in PurePosixPath(info.filename).parts:
                raise PackagingError(f"build cache leaked into ZIP: {info.filename}")
            data = archive.read(info)
            relative = info.filename.removeprefix(prefix + "/")
            expected_digest = (
                sha256_file(root / MANIFEST)
                if relative == MANIFEST
                else digests[relative]
            )
            if sha256_bytes(data) != expected_digest:
                raise PackagingError(f"archived checksum mismatch: {info.filename}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prefix", default="PRSC_IV")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        files = release_files(root)
        if args.write_manifest:
            write_manifest(root, files)
        build_zip(root, args.output, args.prefix, args.force)
    except (OSError, PackagingError, zipfile.BadZipFile) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: deterministic manifest-driven ZIP: {args.output.resolve()}")
    print(f"SHA-256: {sha256_file(args.output.resolve())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
