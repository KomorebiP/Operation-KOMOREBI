from __future__ import annotations

import argparse
import hashlib
import py_compile
import re
from pathlib import Path, PurePosixPath


RESULTS_DIRECTORY = re.compile(
    r"results_(?:smoke|pilot|full|confirmatory)_\d{8}_\d{6}(?:_\d{3})?"
)
TRANSCRIPT_FILE = re.compile(
    r"OSL_HF_V03_WINDOWS_TRANSCRIPT_\d{8}_\d{6}(?:_\d{3})?\.txt"
)
FAILURE_FILE = re.compile(r"FAILED_OSL_HF_V03_\d{8}_\d{6}(?:_\d{3})?\.zip")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def is_runtime_artifact(path: Path, root: Path) -> bool:
    """Return whether *path* is a narrowly recognized generated artifact.

    Source coverage remains exact.  Only files created by Python or by the
    bundled Windows runner are excluded from the source-manifest comparison.
    """
    relative = path.relative_to(root)
    parts = relative.parts
    name = relative.name
    if "__pycache__" in parts:
        return True
    if parts and (parts[0] == "results" or RESULTS_DIRECTORY.fullmatch(parts[0])):
        return True
    if len(parts) == 1 and TRANSCRIPT_FILE.fullmatch(name):
        return True
    if len(parts) == 1 and FAILURE_FILE.fullmatch(name):
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the OSL v0.3 source package")
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--require-clean-release",
        action="store_true",
        help="reject even recognized runtime artifacts before release packaging",
    )
    args = parser.parse_args()
    root = args.package.resolve()
    check(root.is_dir(), f"package directory does not exist: {root}")
    manifest_path = root / "PACKAGE_SHA256SUMS.txt"
    check(manifest_path.is_file(), "missing PACKAGE_SHA256SUMS.txt")
    entries = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        check(re.fullmatch(r"[0-9a-f]{64}", expected) is not None, f"invalid checksum: {relative}")
        posix = PurePosixPath(relative)
        check(not posix.is_absolute() and ".." not in posix.parts and "\\" not in relative, f"unsafe path: {relative}")
        check(relative not in entries, f"duplicate path: {relative}")
        entries[relative] = expected
    paths = list(root.rglob("*"))
    check(not any(path.is_symlink() for path in paths), "package contains a symbolic link")
    runtime_artifacts = [path for path in paths if is_runtime_artifact(path, root)]
    if args.require_clean_release:
        check(not runtime_artifacts, "clean release check found generated runtime artifacts")
    actual = {
        path.relative_to(root).as_posix()
        for path in paths
        if path.is_file()
        and path.name != "PACKAGE_SHA256SUMS.txt"
        and not is_runtime_artifact(path, root)
    }
    check(set(entries) == actual, "package manifest does not exactly cover the package")
    check(
        not any(is_runtime_artifact(root / relative, root) for relative in entries),
        "package manifest contains a generated runtime artifact",
    )
    for relative, expected in entries.items():
        check(sha256(root / relative) == expected, f"checksum mismatch: {relative}")
    for name in ["run_experiment.py", "smoke_tests.py", "verify_results.py", "verify_package.py"]:
        py_compile.compile(str(root / name), doraise=True)
    print(f"verified package: {root}")


if __name__ == "__main__":
    main()
