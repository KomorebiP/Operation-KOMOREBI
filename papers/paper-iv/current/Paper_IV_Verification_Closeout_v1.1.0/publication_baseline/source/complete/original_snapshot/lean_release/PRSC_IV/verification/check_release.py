#!/usr/bin/env python3
"""Fail-closed release gate for Projector-Resolved Seed Calculus IV.

The gate deliberately keeps four evidence classes separate:

* Lean compilation, theorem-map resolution, and kernel-axiom auditing
* finite symbolic or numerical regression suites
* manuscript source and reference consistency
* a deterministic clean PDF build

Finite regressions are never promoted to proof status by this program.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Iterable, Sequence
import zipfile


MAX_RELATIVE_PATH = 180
MAX_COMPONENT = 80
PORTABLE_COMPONENT = re.compile(r"(?:[A-Za-z0-9][A-Za-z0-9._+-]*|\.[A-Za-z0-9][A-Za-z0-9._+-]*)\Z")
LEAN_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_']*(?:\.[A-Za-z_][A-Za-z0-9_']*)+\Z")
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
MANIFEST_NAMES = ("MANIFEST.sha256", "SHA256SUMS.txt")
KNOWN_REGRESSION_SCRIPTS = {
    "verify_original_paper.py",
    "verify_original_tables.py",
    "verify_paper4_strengthened.py",
    "run_regressions.py",
}
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
AUTHORITATIVE_THEOREM_MAP = "formalization/lean/LEAN_THEOREM_MAP_v1.0.0.md"
LEAN_CONTRACT = "verification/lean_contract_v1.0.0.json"
# Updated only after an explicit review of the declaration/record boundary.
LEAN_CONTRACT_SHA256 = "7810897562e23b7539c63c38d0b9f016d0dda2912199baa58ff2f05d6c5bd925"


class GateFailure(RuntimeError):
    """A release invariant was not satisfied."""


@dataclass(frozen=True)
class RegisterRecord:
    number: str
    kind: str
    title: str
    label: str
    evidence: str
    status: str


@dataclass(frozen=True)
class MapRow:
    row_id: int
    record_numbers: tuple[str, ...]
    declarations: tuple[str, ...]
    boundary: str


@dataclass(frozen=True)
class LeanTarget:
    row_id: int
    record_labels: tuple[str, ...]
    kind: str
    declaration: str


class Reporter:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.development_skips: list[str] = []

    @staticmethod
    def passed(message: str) -> None:
        print(f"PASS: {message}")

    @staticmethod
    def info(message: str) -> None:
        print(f"INFO: {message}")

    def skip_development(self, message: str) -> None:
        if self.mode != "development":
            raise GateFailure(message)
        self.development_skips.append(message)
        print(f"SKIP (DEVELOPMENT STATUS, NOT RELEASE READY): {message}")


def fail(message: str) -> None:
    raise GateFailure(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_name(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def ignored(relative: str) -> bool:
    pure = PurePosixPath(relative)
    if any(part in IGNORED_DIRECTORIES for part in pure.parts):
        return True
    return any(relative.endswith(suffix) for suffix in IGNORED_SUFFIXES)


def release_files(root: Path) -> list[str]:
    names: list[str] = []
    symlinks: list[str] = []
    casefolded: dict[str, str] = {}

    for path in root.rglob("*"):
        name = relative_name(root, path)
        if ignored(name):
            continue
        if path.is_symlink():
            symlinks.append(name)
            continue
        if not path.is_file():
            continue

        pure = PurePosixPath(name)
        if (
            pure.is_absolute()
            or "\\" in name
            or any(part in {"", ".", ".."} for part in pure.parts)
        ):
            fail(f"unsafe release path: {name!r}")
        encoded = name.encode("utf-8")
        if len(encoded) > MAX_RELATIVE_PATH:
            fail(
                f"release path exceeds {MAX_RELATIVE_PATH} UTF-8 bytes: {name!r}"
            )
        for part in pure.parts:
            if len(part.encode("utf-8")) > MAX_COMPONENT:
                fail(
                    f"path component exceeds {MAX_COMPONENT} UTF-8 bytes: {part!r}"
                )
            if PORTABLE_COMPONENT.fullmatch(part) is None:
                fail(f"nonportable path component {part!r} in {name!r}")
        folded = name.casefold()
        if folded in casefolded and casefolded[folded] != name:
            fail(
                "case-insensitive path collision: "
                f"{casefolded[folded]!r} and {name!r}"
            )
        casefolded[folded] = name
        names.append(name)

    if symlinks:
        fail("release contains symbolic links: " + ", ".join(sorted(symlinks)))
    names.sort(key=lambda value: value.encode("utf-8"))
    return names


def check_transient_artifacts(root: Path, reporter: Reporter) -> None:
    transients: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        name = relative_name(root, path)
        pure = PurePosixPath(name)
        if any(part in IGNORED_DIRECTORIES for part in pure.parts):
            continue
        if any(name.endswith(suffix) for suffix in IGNORED_SUFFIXES):
            transients.append(name)
    if transients:
        reporter.skip_development(
            "transient build artifacts must be removed before packaging: "
            + ", ".join(sorted(transients))
        )
    else:
        reporter.passed("release tree contains no transient build artifacts")


def check_manifest(
    root: Path, files: Sequence[str], reporter: Reporter
) -> Path | None:
    manifests = [root / name for name in MANIFEST_NAMES if (root / name).is_file()]
    if len(manifests) > 1:
        fail("release contains more than one checksum manifest")
    if not manifests:
        reporter.skip_development(
            "checksum manifest is absent; generate it only after the file set is frozen"
        )
        return None

    manifest = manifests[0]
    manifest_name = relative_name(root, manifest)
    pattern = re.compile(r"([0-9a-f]{64})  ([^\x00-\x1f\x7f]+)\Z")
    entries: list[tuple[str, str]] = []
    for number, line in enumerate(
        manifest.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = pattern.fullmatch(line)
        if match is None:
            fail(f"malformed checksum line {number} in {manifest.name}")
        digest, name = match.groups()
        pure = PurePosixPath(name)
        if (
            pure.is_absolute()
            or name.startswith("./")
            or "\\" in name
            or any(part in {"", ".", ".."} for part in pure.parts)
        ):
            fail(f"unsafe checksum path on line {number}: {name!r}")
        entries.append((digest, name))

    listed = [name for _, name in entries]
    if listed != sorted(listed, key=lambda value: value.encode("utf-8")):
        fail("checksum entries are not sorted bytewise by path")
    duplicates = sorted(name for name, count in Counter(listed).items() if count > 1)
    if duplicates:
        fail("duplicate checksum entries: " + ", ".join(duplicates))
    if manifest_name in listed:
        fail("checksum manifest must not list itself")

    expected = [name for name in files if name != manifest_name]
    if listed != expected:
        missing = sorted(set(expected) - set(listed))
        extra = sorted(set(listed) - set(expected))
        fail(f"checksum/file-set mismatch; missing={missing}; extra={extra}")

    for expected_digest, name in entries:
        actual = sha256(root / name)
        if actual != expected_digest:
            fail(
                f"checksum mismatch for {name}: expected {expected_digest}, got {actual}"
            )
    reporter.passed(f"{manifest.name} covers all {len(entries)} release files")
    return manifest


def manifest_digest_map(manifest: Path) -> dict[str, str]:
    pattern = re.compile(r"([0-9a-f]{64})  ([^\x00-\x1f\x7f]+)\Z")
    entries: dict[str, str] = {}
    for number, line in enumerate(
        manifest.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = pattern.fullmatch(line)
        if match is None:
            fail(f"malformed checksum line {number} in {manifest.name}")
        digest, name = match.groups()
        if name in entries:
            fail(f"duplicate checksum entry in {manifest.name}: {name}")
        entries[name] = digest
    return entries


def check_archive(
    root: Path,
    archive_argument: Path | None,
    manifest: Path | None,
    files: Sequence[str],
    reporter: Reporter,
) -> None:
    if archive_argument is None:
        reporter.skip_development(
            "final ZIP was not supplied; pass --archive PATH to verify its exact entry set"
        )
        return
    if manifest is None:
        fail("a ZIP cannot be verified before the checksum manifest is frozen")
    archive = archive_argument.expanduser().resolve()
    if not archive.is_file() or archive.is_symlink():
        fail(f"archive is absent or not a regular file: {archive}")
    try:
        archive.relative_to(root)
    except ValueError:
        pass
    else:
        fail("the final ZIP must live outside the manifested release root")

    expected_files = set(files)
    manifest_name = relative_name(root, manifest)
    manifest_entries = manifest_digest_map(manifest)
    seen_raw: set[str] = set()
    seen_relative: set[str] = set()
    seen_casefolded: dict[str, str] = {}
    prefix: str | None = None

    try:
        zipped = zipfile.ZipFile(archive)
    except (OSError, zipfile.BadZipFile) as error:
        fail(f"cannot open ZIP archive: {error}")
    with zipped:
        infos = zipped.infolist()
        if not infos:
            fail("ZIP archive is empty")
        for info in infos:
            raw = info.filename
            if raw in seen_raw:
                fail(f"duplicate raw ZIP member: {raw!r}")
            seen_raw.add(raw)
            if (
                not raw
                or raw.endswith("/")
                or raw.startswith("/")
                or "\\" in raw
                or any(ord(character) < 32 or ord(character) == 127 for character in raw)
            ):
                fail(f"unsafe or non-file ZIP member: {raw!r}")
            pure = PurePosixPath(raw)
            if pure.as_posix() != raw:
                fail(f"ZIP member is not in canonical POSIX path form: {raw!r}")
            if any(part in {"", ".", ".."} for part in pure.parts) or len(pure.parts) < 2:
                fail(f"ZIP member lacks one safe top-level prefix: {raw!r}")
            member_prefix = pure.parts[0]
            if prefix is None:
                prefix = member_prefix
                if (
                    len(prefix.encode("utf-8")) > 40
                    or PORTABLE_COMPONENT.fullmatch(prefix) is None
                ):
                    fail(f"ZIP top-level prefix is not short and portable: {prefix!r}")
            elif member_prefix != prefix:
                fail("ZIP members do not share one exact top-level prefix")
            relative = PurePosixPath(*pure.parts[1:]).as_posix()
            if len(relative.encode("utf-8")) > MAX_RELATIVE_PATH:
                fail(f"ZIP member release path is too long: {relative!r}")
            for component in pure.parts:
                if (
                    len(component.encode("utf-8")) > MAX_COMPONENT
                    or PORTABLE_COMPONENT.fullmatch(component) is None
                ):
                    fail(f"nonportable ZIP path component in {raw!r}")
            if ".lake" in pure.parts or any(
                part in IGNORED_DIRECTORIES for part in pure.parts
            ):
                fail(f"ZIP contains a forbidden cache path: {raw!r}")
            if ignored(relative):
                fail(f"ZIP contains a transient or ignored artifact: {raw!r}")
            if info.flag_bits & 0x1:
                fail(f"ZIP member is encrypted: {raw!r}")
            if info.compress_type != zipfile.ZIP_DEFLATED:
                fail(f"ZIP member does not use the reviewed deflate method: {raw!r}")
            unix_mode = (info.external_attr >> 16) & 0xFFFF
            file_type = stat.S_IFMT(unix_mode)
            if file_type and not stat.S_ISREG(unix_mode):
                fail(f"ZIP member is a symlink or special file: {raw!r}")
            if relative == "VERIFY.sh" and not (unix_mode & 0o111):
                fail("ZIP does not preserve executable mode on VERIFY.sh")
            if relative in seen_relative:
                fail(f"duplicate normalized ZIP member: {relative!r}")
            seen_relative.add(relative)
            folded = relative.casefold()
            if folded in seen_casefolded and seen_casefolded[folded] != relative:
                fail(
                    "case-insensitive ZIP member collision: "
                    f"{seen_casefolded[folded]!r} and {relative!r}"
                )
            seen_casefolded[folded] = relative

        if seen_relative != expected_files:
            missing = sorted(expected_files - seen_relative)
            extra = sorted(seen_relative - expected_files)
            fail(f"ZIP/manifested-tree entry mismatch; missing={missing}; extra={extra}")
        embedded_manifest = zipped.read(f"{prefix}/{manifest_name}")
        if embedded_manifest != manifest.read_bytes():
            fail("ZIP embeds checksum-manifest bytes different from the verified tree")
        for name, expected_digest in manifest_entries.items():
            digest = hashlib.sha256()
            with zipped.open(f"{prefix}/{name}") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != expected_digest:
                fail(f"ZIP member checksum mismatch: {name}")
        corrupt = zipped.testzip()
        if corrupt is not None:
            fail(f"ZIP CRC check failed for {corrupt}")
    reporter.passed(
        f"ZIP has one short prefix and exactly {len(expected_files)} manifested files; "
        "all streamed hashes and CRCs pass"
    )


def textual_files(root: Path, files: Iterable[str]) -> Iterable[tuple[str, str]]:
    suffixes = {".cff", ".json", ".md", ".tex", ".txt", ".yaml", ".yml"}
    for name in files:
        if name == "verification/check_release.py":
            continue
        path = root / name
        if path.suffix.lower() not in suffixes:
            continue
        try:
            yield name, path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            fail(f"expected UTF-8 text in {name}: {error}")


def macro_payloads(source: str, macro: str) -> list[str]:
    pattern = re.compile(rf"\\{re.escape(macro)}\s*\{{([^{{}}]*)\}}")
    return [match.group(1).strip() for match in pattern.finditer(source)]


def check_evidence_claims(
    root: Path, files: Sequence[str], reporter: Reporter
) -> tuple[list[str], list[str]]:
    stale_counts = re.compile(r"\b(?:1246\s*/\s*1246|647\s*/\s*647|981\s*/\s*981)\b")
    safe_boundary = re.compile(
        r"regression|\bfinite\b|pass count never upgrades|"
        r"not (?:a |an )?(?:lean |formal )?proof|"
        r"does not (?:constitute|replace|establish).{0,40}proof|"
        r"cannot serve as theorem proof",
        re.IGNORECASE | re.DOTALL,
    )
    formal_overclaims = [
        re.compile(r"\blean[- ]complete\b", re.IGNORECASE),
        re.compile(r"\bfully formal(?:ized|ised)\b", re.IGNORECASE),
        re.compile(
            r"\b(?:all|every)\b.{0,50}\b(?:theorems?|results?)\b.{0,30}\b(?:proved|verified) in lean\b",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"\b(?:1246|647|981).{0,30}\b(?:lean|formal proof|proved theorem)",
            re.IGNORECASE | re.DOTALL,
        ),
    ]

    paper_source = (root / "paper/paper4.tex").read_text(encoding="utf-8")
    lean_targets = macro_payloads(paper_source, "statusleanfour")
    inherited_targets = macro_payloads(paper_source, "statusleanprior")

    for name, source in textual_files(root, files):
        legacy_location = name.startswith("verification/legacy/") or name.startswith(
            "provenance/legacy/"
        )
        for match in stale_counts.finditer(source):
            context = source[max(0, match.start() - 180) : match.end() + 180]
            if not legacy_location and safe_boundary.search(context) is None:
                fail(
                    f"stale finite-check total is presented without a regression/proof boundary in {name}"
                )
        if name.startswith("verification/legacy/") or name.startswith(
            "provenance/legacy/"
        ):
            continue
        for pattern in formal_overclaims:
            match = pattern.search(source)
            if match is not None:
                prefix = source[max(0, match.start() - 40) : match.start()]
                if re.search(
                    r"\b(?:not|never|is not|isn't)\b[^.!?\n]{0,30}$",
                    prefix,
                    re.IGNORECASE,
                ):
                    continue
                line = source.count("\n", 0, match.start()) + 1
                fail(f"unqualified formal-verification overclaim in {name}:{line}")

    reporter.passed(
        "finite check totals are separated from Lean and manuscript proof status"
    )
    return lean_targets, inherited_targets


def parse_requirements(root: Path) -> dict[str, str]:
    path = root / "requirements.txt"
    if not path.is_file():
        return {}
    pinned: dict[str, str] = {}
    pattern = re.compile(r"([A-Za-z0-9_.-]+)==([^\s;]+)\Z")
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        match = pattern.fullmatch(line)
        if match is None:
            fail(f"requirements.txt line {number} is not an exact version pin")
        project, version = match.groups()
        key = re.sub(r"[-_.]+", "-", project).lower()
        if key in pinned:
            fail(f"duplicate requirement pin: {project}")
        pinned[key] = version
    return pinned


def installed_version(project: str) -> str | None:
    try:
        return importlib.metadata.version(project)
    except importlib.metadata.PackageNotFoundError:
        return None


def copy_release_tree(root: Path, destination: Path) -> None:
    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored_names: set[str] = set()
        for name in names:
            path = Path(directory) / name
            try:
                relative = path.relative_to(root).as_posix()
            except ValueError:
                continue
            if ignored(relative):
                ignored_names.add(name)
        return ignored_names

    shutil.copytree(root, destination, ignore=ignore)


def run_command(
    command: Sequence[str], cwd: Path, *, environment: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["TZ"] = "UTC"
    env["LC_ALL"] = "C.UTF-8"
    if environment:
        env.update(environment)
    return subprocess.run(
        list(command),
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def run_regression_suites(
    root: Path, files: Sequence[str], requirements: dict[str, str], reporter: Reporter
) -> None:
    scripts = [
        name
        for name in files
        if PurePosixPath(name).name in KNOWN_REGRESSION_SCRIPTS
    ]
    if not scripts:
        reporter.info(
            "no optional finite regression suite is installed; this does not affect proof status"
        )
        return
    if not requirements:
        fail("regression scripts are present but requirements.txt is missing or empty")
    mismatches: list[str] = []
    for project, expected in sorted(requirements.items()):
        actual = installed_version(project)
        if actual != expected:
            mismatches.append(f"{project}: expected {expected}, installed {actual!r}")
    if mismatches:
        fail(
            "the pinned regression environment is not active; " + "; ".join(mismatches)
        )

    if any("pdftotext" in (root / script).read_text(encoding="utf-8") for script in scripts):
        if shutil.which("pdftotext") is None:
            fail("a regression script requires the external pdftotext command")

    with tempfile.TemporaryDirectory(prefix="prsc4-regression-") as temporary:
        copied_root = Path(temporary) / "release"
        copy_release_tree(root, copied_root)
        for script in scripts:
            result = run_command([sys.executable, str(copied_root / script)], copied_root)
            if result.returncode != 0:
                fail(
                    f"finite regression suite failed: {script}\n{result.stdout[-6000:]}"
                )
            first_line = next(
                (line.strip() for line in result.stdout.splitlines() if line.strip()),
                "completed without a summary",
            )
            reporter.passed(f"REGRESSION ONLY: {script}: {first_line}")


def release_metadata(root: Path) -> dict[str, object]:
    path = root / "RELEASE.json"
    if not path.is_file() or path.is_symlink():
        fail("RELEASE.json is absent or not a regular file")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        fail(f"invalid RELEASE.json: {error}")
    if not isinstance(payload, dict):
        fail("RELEASE.json must contain a JSON object")
    return payload


def nested_metadata(payload: dict[str, object], *keys: str) -> dict[str, object]:
    current: object = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            fail("RELEASE.json is missing " + ".".join(keys))
        current = current[key]
    if not isinstance(current, dict):
        fail("RELEASE.json field is not an object: " + ".".join(keys))
    return current


def check_metadata_values(
    section: dict[str, object], expected: dict[str, object], context: str
) -> None:
    mismatches = [
        f"{key}: {section.get(key)!r} != {value!r}"
        for key, value in expected.items()
        if section.get(key) != value
    ]
    if mismatches:
        fail(f"stale {context} metadata in RELEASE.json; " + "; ".join(mismatches))


RESULT_KINDS = {"Theorem", "Proposition", "Lemma", "Corollary"}
REGISTER_KINDS = RESULT_KINDS | {
    "Definition",
    "Example",
    "Remark",
    "Standardfact",
    "Boundary",
}


def strip_tex_comments(source: str) -> str:
    """Remove unescaped TeX comments while retaining line numbering."""

    cleaned: list[str] = []
    for line in source.splitlines(keepends=True):
        cut = len(line)
        for index, character in enumerate(line):
            if character != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                cut = index
                break
        suffix = "\n" if line.endswith("\n") else ""
        cleaned.append(line[:cut].rstrip("\r\n") + suffix)
    return "".join(cleaned)


def check_result_proof_pairing(source: str) -> tuple[int, int]:
    """Require one explicit proof environment after every theorem-like result."""

    source = strip_tex_comments(source)
    alternatives = "|".join(kind.lower() for kind in sorted(RESULT_KINDS))
    token = re.compile(rf"\\(begin|end)\{{({alternatives}|proof)\}}")
    active_result: tuple[str, int] | None = None
    awaiting_proof: tuple[str, int] | None = None
    active_proof: int | None = None
    results = 0
    proofs = 0

    def line_at(position: int) -> int:
        return source.count("\n", 0, position) + 1

    for match in token.finditer(source):
        action, environment = match.groups()
        line = line_at(match.start())
        is_result = environment.title() in RESULT_KINDS
        if action == "begin" and is_result:
            if active_result is not None:
                fail(
                    f"nested theorem-like environment at paper4.tex:{line}; "
                    f"opened at line {active_result[1]}"
                )
            if active_proof is not None:
                fail(f"theorem-like environment begins inside a proof at paper4.tex:{line}")
            if awaiting_proof is not None:
                fail(
                    f"{awaiting_proof[0]} at paper4.tex:{awaiting_proof[1]} "
                    "has no following proof environment"
                )
            active_result = (environment.title(), line)
            results += 1
        elif action == "end" and is_result:
            if active_result is None or active_result[0] != environment.title():
                fail(f"unbalanced {environment} environment at paper4.tex:{line}")
            awaiting_proof = active_result
            active_result = None
        elif action == "begin":
            if active_result is not None:
                fail(f"proof begins inside a theorem environment at paper4.tex:{line}")
            if active_proof is not None:
                fail(f"nested proof environment at paper4.tex:{line}")
            if awaiting_proof is None:
                fail(f"orphan proof environment at paper4.tex:{line}")
            awaiting_proof = None
            active_proof = line
            proofs += 1
        else:
            if active_proof is None:
                fail(f"unbalanced proof environment at paper4.tex:{line}")
            active_proof = None

    if active_result is not None:
        fail(f"unclosed {active_result[0]} at paper4.tex:{active_result[1]}")
    if active_proof is not None:
        fail(f"unclosed proof at paper4.tex:{active_proof}")
    if awaiting_proof is not None:
        fail(
            f"{awaiting_proof[0]} at paper4.tex:{awaiting_proof[1]} "
            "has no following proof environment"
        )
    return results, proofs


def parse_register(path: Path, paper_source: str) -> dict[str, RegisterRecord]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header = ["No.", "Type", "Title", "Label", "Evidence and status"]
    header_indices = [
        index for index, line in enumerate(lines) if markdown_cells(line) == header
    ]
    if len(header_indices) != 1:
        fail("mathematical register must contain one exact five-column header")
    header_index = header_indices[0]
    if header_index + 1 >= len(lines):
        fail("mathematical register is missing its Markdown separator")
    separator = markdown_cells(lines[header_index + 1])
    if separator is None or len(separator) != 5 or not all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        fail("mathematical register has a malformed Markdown separator")

    records: dict[str, RegisterRecord] = {}
    labels: set[str] = set()
    row_index = header_index + 2
    while row_index < len(lines) and lines[row_index].strip():
        cells = markdown_cells(lines[row_index])
        if cells is None or len(cells) != 5:
            fail(f"malformed mathematical-register row at line {row_index + 1}")
        number, kind, title, label_cell, evidence_cell = cells
        if re.fullmatch(r"\d+\.\d+", number) is None:
            fail(f"invalid mathematical-record number at register line {row_index + 1}")
        if kind not in REGISTER_KINDS:
            fail(f"unknown record type {kind!r} at register line {row_index + 1}")
        if not title:
            fail(f"empty mathematical-record title at register line {row_index + 1}")
        label_match = re.fullmatch(r"`([A-Za-z][A-Za-z0-9_.-]*:[A-Za-z0-9_.:-]+)`", label_cell)
        if label_match is None:
            fail(f"invalid TeX label cell at register line {row_index + 1}")
        label = label_match.group(1)
        evidence_parts = evidence_cell.split("; ")
        if len(evidence_parts) != 2:
            fail(f"invalid evidence/status cell at register line {row_index + 1}")
        evidence, status = evidence_parts

        if kind in RESULT_KINDS:
            if evidence not in {"P", "P + L(full)"}:
                fail(f"invalid result evidence {evidence!r} at register line {row_index + 1}")
            if status not in {"Article theorem", "Conditional article theorem"}:
                fail(f"invalid result status {status!r} at register line {row_index + 1}")
        else:
            expected = {
                "Definition": ("D", "Definition"),
                "Example": ("E", "Example"),
                "Remark": ("R", "Remark or boundary"),
                "Boundary": ("R", "Remark or boundary"),
                "Standardfact": ("I", "Imported standard fact"),
            }[kind]
            if (evidence, status) != expected:
                fail(
                    f"invalid evidence/status for {kind} at register line {row_index + 1}: "
                    f"{evidence_cell!r}"
                )
        if number in records:
            fail(f"duplicate mathematical-record number in register: {number}")
        if label in labels:
            fail(f"duplicate mathematical-record label in register: {label}")
        labels.add(label)
        records[number] = RegisterRecord(number, kind, title, label, evidence, status)
        row_index += 1

    if not records:
        fail("mathematical record register contains no rows")
    for trailing_index in range(row_index + 1, len(lines)):
        cells = markdown_cells(lines[trailing_index])
        if cells and cells[0] and re.fullmatch(r"\d+\.\d+", cells[0]):
            fail(f"noncontiguous trailing register row at line {trailing_index + 1}")

    previous_section: int | None = None
    previous_counter = 0
    for number in records:
        section, counter = map(int, number.split("."))
        if section != previous_section:
            if previous_section is not None and section <= previous_section:
                fail("mathematical-register sections are not strictly increasing")
            if counter != 1:
                fail(f"mathematical-register section {section} does not begin at 1")
            previous_section = section
            previous_counter = 1
        else:
            if counter != previous_counter + 1:
                fail(f"gap or reordering in mathematical-register section {section}")
            previous_counter = counter

    result_count, proof_count = check_result_proof_pairing(paper_source)
    parsed_result_count = sum(record.kind in RESULT_KINDS for record in records.values())
    standard_count = sum(record.kind == "Standardfact" for record in records.values())
    if result_count != parsed_result_count:
        fail(
            "register/manuscript theorem-like count mismatch: "
            f"{parsed_result_count} != {result_count}"
        )

    expected_summaries = {
        "Numbered records": len(records),
        "Theorem-like results": parsed_result_count,
        "Proof environments": proof_count,
        "Imported standard facts": standard_count,
    }
    register_source = "\n".join(lines)
    for label, expected in expected_summaries.items():
        matches = re.findall(rf"(?m)^- {re.escape(label)}: `(\d+)`$", register_source)
        if len(matches) != 1:
            fail(f"register must contain one exact {label!r} summary")
        if int(matches[0]) != expected:
            fail(
                f"register summary {label!r} is stale: "
                f"{matches[0]} != {expected}"
            )
    return records


def check_generated_register(
    root: Path, files: Sequence[str], reporter: Reporter
) -> dict[str, RegisterRecord]:
    script_name = "scripts/generate_register.py"
    register_name = "provenance/THEOREM_REGISTER.md"
    if script_name not in files or register_name not in files:
        reporter.skip_development(
            "record generator or provenance/THEOREM_REGISTER.md is absent"
        )
        return {}

    with tempfile.TemporaryDirectory(prefix="prsc4-register-") as temporary:
        copied_root = Path(temporary) / "release"
        copy_release_tree(root, copied_root)
        generated = copied_root / register_name
        # The copied release tree already contains the shipped register.  Remove
        # it before invoking the generator so a no-op, disabled, or incorrectly
        # targeted generator cannot pass by leaving that copy untouched.
        generated.unlink()
        result = run_command(
            [sys.executable, str(copied_root / script_name)], copied_root
        )
        if result.returncode != 0:
            fail(
                "mathematical record regeneration failed\n"
                + result.stdout[-6000:]
            )
        if not generated.is_file():
            fail(
                "mathematical record generator did not recreate "
                "provenance/THEOREM_REGISTER.md"
            )
        shipped = root / register_name
        if generated.read_bytes() != shipped.read_bytes():
            fail(
                "provenance/THEOREM_REGISTER.md is stale; regenerate it from paper4.tex"
            )

    paper_source = (root / "paper/paper4.tex").read_text(encoding="utf-8")
    records = parse_register(root / register_name, paper_source)
    result_records = sum(record.kind in RESULT_KINDS for record in records.values())
    proof_count = check_result_proof_pairing(paper_source)[1]
    standard_count = sum(record.kind == "Standardfact" for record in records.values())
    manuscript_metadata = nested_metadata(
        release_metadata(root), "verification", "manuscript"
    )
    check_metadata_values(
        manuscript_metadata,
        {
            "numbered_records": len(records),
            "theorem_like_results": result_records,
            "proof_environments": proof_count,
            "imported_standard_facts": standard_count,
        },
        "manuscript-count",
    )
    reporter.passed(
        f"mathematical register regenerates byte-identically "
        f"({len(records)} records, {result_records} theorem-like results, "
        f"{proof_count} paired proofs, {standard_count} imported standard fact)"
    )
    return records


def find_lean_root(root: Path) -> Path | None:
    candidates = [root / "formalization/lean", root / "lean"]
    incomplete = [
        path
        for path in candidates
        if path.is_dir()
        and not (
            (path / "lean-toolchain").is_file()
            and (
                (path / "lakefile.toml").is_file()
                or (path / "lakefile.lean").is_file()
            )
        )
    ]
    if incomplete:
        fail(
            "incomplete Lean project directory: "
            + ", ".join(path.as_posix() for path in incomplete)
        )
    projects = [
        path
        for path in candidates
        if path.is_dir()
        and (path / "lean-toolchain").is_file()
        and ((path / "lakefile.toml").is_file() or (path / "lakefile.lean").is_file())
    ]
    if len(projects) > 1:
        fail("multiple Lean project roots found")
    return projects[0] if projects else None


def path_exists(path: Path) -> bool:
    """Return true for every filesystem entry, including a broken symlink."""

    return os.path.lexists(path)


def check_lean_start_state(
    lean_root: Path | None,
    mode: str,
    cache_requested: bool,
    reporter: Reporter,
) -> None:
    """Check the local Lake state before any release command can create it."""

    if lean_root is None:
        if cache_requested:
            fail("--lean-packages-cache requires a complete Lean project")
        return

    lake_dir = lean_root / ".lake"
    if mode == "release" and path_exists(lake_dir):
        fail(
            "release verification must start from a clean extraction without "
            "formalization/lean/.lake"
        )
    if cache_requested and path_exists(lake_dir):
        fail(
            "--lean-packages-cache requires a clean Lean project without a local .lake"
        )
    if mode == "development" and not cache_requested and path_exists(lake_dir):
        reporter.info(
            "development Lean build may reuse .lake; the final release gate requires "
            "a clean extracted tree"
        )


def load_lake_git_pins(lean_root: Path) -> list[tuple[str, str]]:
    manifest = lean_root / "lake-manifest.json"
    if not manifest.is_file() or manifest.is_symlink():
        fail("Lean project is missing a regular lake-manifest.json dependency lock")
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        fail(f"invalid lake-manifest.json: {error}")
    if not isinstance(payload, dict):
        fail("lake-manifest.json must contain a JSON object")
    if payload.get("packagesDir") != ".lake/packages":
        fail("lake-manifest.json does not use the expected .lake/packages directory")
    packages = payload.get("packages")
    if not isinstance(packages, list) or not packages:
        fail("lake-manifest.json contains no pinned packages")

    pins: list[tuple[str, str]] = []
    seen: set[str] = set()
    for index, package in enumerate(packages, start=1):
        if not isinstance(package, dict):
            fail(f"lake-manifest package {index} is not an object")
        if package.get("type") != "git":
            fail(f"lake-manifest package {index} is not a Git dependency")
        name = package.get("name")
        revision = package.get("rev")
        if (
            not isinstance(name, str)
            or PORTABLE_COMPONENT.fullmatch(name) is None
            or "/" in name
            or "\\" in name
        ):
            fail(f"lake-manifest package {index} has an unsafe name")
        if name in seen:
            fail(f"lake-manifest contains duplicate package name: {name}")
        if not isinstance(revision, str) or re.fullmatch(r"[0-9a-f]{40}", revision) is None:
            fail(f"lake-manifest package {name} lacks an exact 40-hex revision")
        seen.add(name)
        pins.append((name, revision))
    return pins


def validate_lean_packages_cache(
    root: Path,
    lean_root: Path,
    cache_argument: Path,
    reporter: Reporter,
) -> Path:
    """Validate an external Lake packages cache without changing the release tree."""

    supplied = cache_argument.expanduser()
    if not supplied.is_dir() or supplied.is_symlink():
        fail(f"Lean packages cache is not a real directory: {supplied}")
    try:
        cache = supplied.resolve(strict=True)
    except OSError as error:
        fail(f"could not resolve Lean packages cache: {error}")
    try:
        cache.relative_to(root)
    except ValueError:
        pass
    else:
        fail("Lean packages cache must be external to the release root")

    git = shutil.which("git")
    if git is None:
        fail("git is required to validate --lean-packages-cache")
    pins = load_lake_git_pins(lean_root)
    for name, revision in pins:
        package = cache / name
        if not package.is_dir() or package.is_symlink():
            fail(f"Lean cache package is absent or not a real directory: {name}")

        top_level = run_command(
            [git, "-C", str(package), "rev-parse", "--show-toplevel"], lean_root
        )
        if top_level.returncode != 0:
            fail(f"Lean cache package is not a Git repository: {name}")
        try:
            repository_root = Path(top_level.stdout.strip()).resolve(strict=True)
        except OSError as error:
            fail(f"could not resolve Git root for Lean cache package {name}: {error}")
        if repository_root != package.resolve():
            fail(f"Lean cache package is not a repository root: {name}")

        head = run_command(
            [git, "-C", str(package), "rev-parse", "--verify", "HEAD^{commit}"],
            lean_root,
        )
        actual_revision = head.stdout.strip()
        if head.returncode != 0 or actual_revision != revision:
            fail(
                f"Lean cache package {name} is not at its pinned revision: "
                f"{actual_revision!r} != {revision}"
            )

        status = run_command(
            [git, "-C", str(package), "status", "--porcelain=v1", "--untracked-files=no"],
            lean_root,
        )
        if status.returncode != 0:
            fail(f"could not inspect tracked state of Lean cache package: {name}")
        if status.stdout.strip():
            fail(f"Lean cache package has tracked modifications: {name}")

    reporter.passed(
        f"external Lean package cache matches all {len(pins)} pinned Git revisions"
    )
    return cache


def install_lean_packages_cache(lean_root: Path, cache: Path) -> None:
    """Install the validated cache through the project's conventional local link."""

    lake_dir = lean_root / ".lake"
    build_dir = lake_dir / "build"
    if path_exists(lake_dir) or path_exists(build_dir):
        fail("local .lake or .lake/build appeared after the clean-start check")
    try:
        lake_dir.mkdir(mode=0o755)
        (lake_dir / "packages").symlink_to(cache, target_is_directory=True)
    except OSError as error:
        if lake_dir.is_dir() and not lake_dir.is_symlink():
            shutil.rmtree(lake_dir)
        fail(f"could not attach the validated Lean packages cache: {error}")


def remove_local_lake_cache_link(lean_root: Path, cache: Path) -> None:
    """Remove only the local Lake state created for an external-cache run."""

    lake_dir = lean_root / ".lake"
    packages = lake_dir / "packages"
    if lake_dir.is_symlink() or not lake_dir.is_dir():
        fail("generated local .lake directory changed type during verification")
    if not packages.is_symlink() or packages.resolve() != cache:
        fail("generated local .lake/packages link changed during verification")
    shutil.rmtree(lake_dir)


def markdown_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    in_code = False
    for character in stripped[1:-1]:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            current.append(character)
            escaped = True
        elif character == "`":
            current.append(character)
            in_code = not in_code
        elif character == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
    if escaped or in_code:
        fail("unterminated escape or code span in Markdown table row")
    cells.append("".join(current).strip())
    return cells


def parse_theorem_map(path: Path) -> list[MapRow]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header = [
        "ID",
        "Manuscript record",
        "Lean declaration",
        "Exact status and boundary",
    ]
    header_indices = [
        index for index, line in enumerate(lines) if markdown_cells(line) == header
    ]
    if len(header_indices) != 1:
        fail(f"{path.name} must contain one exact authoritative table header")
    header_index = header_indices[0]
    if header_index + 1 >= len(lines):
        fail(f"missing Markdown separator in {path.name}")
    separator = markdown_cells(lines[header_index + 1])
    if separator is None or len(separator) != 4 or not all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        fail(f"malformed Markdown separator in {path.name}")

    rows: list[MapRow] = []
    declarations_seen: set[str] = set()
    cursor = header_index + 2
    while cursor < len(lines) and lines[cursor].strip():
        cells = markdown_cells(lines[cursor])
        if cells is None or len(cells) != 4:
            fail(f"malformed theorem-map row at line {cursor + 1}")
        row_id_cell, record_cell, declaration_cell, boundary = cells
        if re.fullmatch(r"\d+", row_id_cell) is None:
            fail(f"invalid theorem-map row ID at line {cursor + 1}")
        row_id = int(row_id_cell)
        if row_id != len(rows) + 1:
            fail(
                f"theorem-map row IDs must be consecutive; expected {len(rows) + 1}, "
                f"found {row_id}"
            )
        if not record_cell:
            fail(f"empty manuscript-record cell at line {cursor + 1}")
        record_numbers = tuple(re.findall(r"\b\d+\.\d+\b", record_cell))
        if not record_numbers:
            fail(f"theorem-map row has no manuscript record number at line {cursor + 1}")
        if len(set(record_numbers)) != len(record_numbers):
            fail(f"duplicate manuscript record number at theorem-map line {cursor + 1}")

        declaration_parts = re.split(r"\s*,\s*", declaration_cell)
        names: list[str] = []
        for part in declaration_parts:
            match = re.fullmatch(r"`([^`]+)`", part)
            if match is None:
                fail(f"malformed declaration list at theorem-map line {cursor + 1}")
            name = match.group(1)
            if LEAN_NAME.fullmatch(name) is None:
                fail(f"invalid fully qualified Lean name in theorem map: {name!r}")
            if name in declarations_seen:
                fail(f"duplicate theorem-map declaration: {name}")
            declarations_seen.add(name)
            names.append(name)
        if not names:
            fail(f"empty declaration cell at line {cursor + 1}")
        if not boundary:
            fail(f"empty theorem-map boundary at line {cursor + 1}")
        rows.append(MapRow(row_id, record_numbers, tuple(names), boundary))
        cursor += 1

    if not rows:
        fail(f"theorem map contains no declarations: {path.name}")
    for trailing_index in range(cursor + 1, len(lines)):
        cells = markdown_cells(lines[trailing_index])
        if cells and cells[0] and re.fullmatch(r"\d+", cells[0]):
            fail(f"noncontiguous trailing theorem-map row at line {trailing_index + 1}")
    return rows


def load_lean_contract(
    root: Path, reporter: Reporter
) -> tuple[list[LeanTarget], int, int] | None:
    path = root / LEAN_CONTRACT
    if not path.is_file() or path.is_symlink():
        reporter.skip_development(f"{LEAN_CONTRACT} is absent or not a regular file")
        return None
    actual_digest = sha256(path)
    if actual_digest != LEAN_CONTRACT_SHA256:
        fail(
            f"Lean contract digest is not the reviewed value: "
            f"{actual_digest} != {LEAN_CONTRACT_SHA256}"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        fail(f"invalid Lean contract JSON: {error}")
    if not isinstance(payload, dict) or set(payload) != {
        "schema_version",
        "theorem_map",
        "namespace_declarations",
        "namespace_theorems",
        "targets",
    }:
        fail("Lean contract has an unexpected top-level schema")
    if payload["schema_version"] != 1:
        fail("unsupported Lean contract schema version")
    if payload["theorem_map"] != AUTHORITATIVE_THEOREM_MAP:
        fail("Lean contract names the wrong authoritative theorem map")
    namespace_declarations = payload["namespace_declarations"]
    namespace_theorems = payload["namespace_theorems"]
    if (
        not isinstance(namespace_declarations, int)
        or isinstance(namespace_declarations, bool)
        or namespace_declarations <= 0
        or not isinstance(namespace_theorems, int)
        or isinstance(namespace_theorems, bool)
        or namespace_theorems <= 0
        or namespace_theorems > namespace_declarations
    ):
        fail("Lean contract has invalid namespace counts")
    raw_targets = payload["targets"]
    if not isinstance(raw_targets, list) or not raw_targets:
        fail("Lean contract target list is empty or invalid")

    targets: list[LeanTarget] = []
    seen_names: set[str] = set()
    last_row = 0
    seen_rows: set[int] = set()
    for index, raw in enumerate(raw_targets, start=1):
        if not isinstance(raw, dict) or set(raw) != {
            "row_id",
            "record_labels",
            "kind",
            "declaration",
        }:
            fail(f"Lean contract target {index} has an unexpected schema")
        row_id = raw["row_id"]
        labels = raw["record_labels"]
        kind = raw["kind"]
        declaration = raw["declaration"]
        if not isinstance(row_id, int) or isinstance(row_id, bool) or row_id <= 0:
            fail(f"Lean contract target {index} has an invalid row ID")
        if row_id < last_row or row_id > last_row + 1:
            fail("Lean contract targets are not grouped by consecutive row ID")
        if row_id != last_row:
            if row_id in seen_rows:
                fail(f"Lean contract row {row_id} is not contiguous")
            seen_rows.add(row_id)
            last_row = row_id
        if (
            not isinstance(labels, list)
            or not labels
            or not all(
                isinstance(label, str)
                and re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]*:[A-Za-z0-9_.:-]+", label)
                for label in labels
            )
            or len(set(labels)) != len(labels)
        ):
            fail(f"Lean contract target {index} has invalid record labels")
        if kind not in {"theorem", "definition"}:
            fail(f"Lean contract target {index} has invalid kind {kind!r}")
        if not isinstance(declaration, str) or LEAN_NAME.fullmatch(declaration) is None:
            fail(f"Lean contract target {index} has an invalid declaration name")
        if declaration in seen_names:
            fail(f"duplicate declaration in Lean contract: {declaration}")
        seen_names.add(declaration)
        targets.append(LeanTarget(row_id, tuple(labels), kind, declaration))
    if sorted(seen_rows) != list(range(1, max(seen_rows) + 1)):
        fail("Lean contract row IDs are not consecutive from 1")
    reporter.passed(
        f"review-anchored Lean contract contains {len(targets)} exact targets "
        f"({sum(target.kind == 'theorem' for target in targets)} theorems, "
        f"{sum(target.kind == 'definition' for target in targets)} definitions)"
    )
    return targets, namespace_declarations, namespace_theorems


def crosscheck_map_contract(
    rows: Sequence[MapRow],
    records: dict[str, RegisterRecord],
    targets: Sequence[LeanTarget],
) -> tuple[list[str], list[str]]:
    records_by_label = {record.label: record for record in records.values()}
    targets_by_row: dict[int, list[LeanTarget]] = {}
    for target in targets:
        targets_by_row.setdefault(target.row_id, []).append(target)
    if [row.row_id for row in rows] != sorted(targets_by_row):
        fail("theorem-map row IDs disagree with the reviewed Lean contract")

    mapped_records: list[str] = []
    mapped: list[str] = []
    for row in rows:
        unknown_numbers = [number for number in row.record_numbers if number not in records]
        if unknown_numbers:
            fail(
                f"theorem-map row {row.row_id} refers to unknown manuscript records: "
                + ", ".join(unknown_numbers)
            )
        actual_labels = tuple(records[number].label for number in row.record_numbers)
        expected_targets = targets_by_row[row.row_id]
        expected_labels = expected_targets[0].record_labels
        if any(target.record_labels != expected_labels for target in expected_targets):
            fail(f"Lean contract row {row.row_id} has inconsistent record associations")
        if actual_labels != expected_labels:
            fail(
                f"theorem-map row {row.row_id} record association changed: "
                f"{actual_labels} != {expected_labels}"
            )
        expected_names = tuple(target.declaration for target in expected_targets)
        if row.declarations != expected_names:
            fail(
                f"theorem-map row {row.row_id} target list changed: "
                f"{row.declarations} != {expected_names}"
            )
        for label in actual_labels:
            record = records_by_label[label]
            if record.kind in RESULT_KINDS and record.evidence != "P + L(full)":
                fail(
                    f"Lean-mapped result {record.number} ({label}) is not exactly "
                    "marked P + L(full)"
                )
        mapped_records.extend(row.record_numbers)
        mapped.extend(row.declarations)

    contract_labels = {
        label for target in targets for label in target.record_labels
    }
    unknown_labels = sorted(contract_labels - set(records_by_label))
    if unknown_labels:
        fail("Lean contract contains unknown manuscript labels: " + ", ".join(unknown_labels))
    full_labels = {
        record.label
        for record in records.values()
        if record.evidence == "P + L(full)"
    }
    if full_labels != {
        label
        for label in contract_labels
        if records_by_label[label].kind in RESULT_KINDS
    }:
        fail("register L(full) result set disagrees with the reviewed Lean contract")
    return mapped, mapped_records


def lean_module_names(lean_root: Path) -> list[str]:
    modules: list[str] = []
    for path in lean_root.rglob("*.lean"):
        relative = path.relative_to(lean_root)
        if any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue
        if "kernelaudit" in path.stem.casefold():
            continue
        parts = list(relative.with_suffix("").parts)
        if not all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_']*", part) for part in parts):
            fail(f"Lean module has a non-module path: {relative.as_posix()}")
        modules.append(".".join(parts))
    return sorted(set(modules))


def check_axiom_output(output: str, context: str) -> None:
    forbidden_markers = ("sorryAx", "declaration uses 'sorry'", "declaration uses \"sorry\"")
    for marker in forbidden_markers:
        if marker.lower() in output.lower():
            fail(f"{context} contains forbidden proof placeholder {marker!r}")
    for block in re.findall(r"depends on axioms:\s*\[([^\]]*)\]", output, re.DOTALL):
        axioms = {
            item.strip().strip("'\"")
            for item in block.replace("\n", " ").split(",")
            if item.strip()
        }
        unexpected = sorted(axioms - ALLOWED_AXIOMS)
        if unexpected:
            fail(f"{context} uses non-allowlisted axioms: {unexpected}")


def kernel_sentinels(output: str) -> list[tuple[int, int, int]]:
    return [
        tuple(map(int, values))
        for values in re.findall(
            r"FAIL-CLOSED PAPER IV v1\.0\.0 KERNEL AUDIT PASS: "
            r"(\d+) declarations \((\d+) theoremInfo\); "
            r"(\d+) explicit mapped targets; allowed axioms only: "
            r"propext, Classical\.choice, Quot\.sound",
            output,
        )
    ]


def check_lean(
    root: Path,
    mode: str,
    lean_status_targets: Sequence[str],
    register_records: dict[str, RegisterRecord],
    reporter: Reporter,
    external_cache: Path | None,
) -> None:
    lean_root = find_lean_root(root)
    if lean_root is None:
        if lean_status_targets:
            fail("manuscript claims Paper IV Lean declarations but no Lean project exists")
        reporter.skip_development(
            "formalization/lean is absent; Paper IV Lean compilation, map, and kernel gates were not run"
        )
        return

    if external_cache is not None:
        packages = lean_root / ".lake/packages"
        if not packages.is_symlink() or packages.resolve() != external_cache:
            fail("validated external Lean cache is not attached at .lake/packages")
        if path_exists(lean_root / ".lake/build"):
            fail("local .lake/build must not preexist the warning-fatal Lean build")

    authoritative_map = root / AUTHORITATIVE_THEOREM_MAP
    discovered_maps = sorted(
        path
        for path in root.rglob("LEAN_THEOREM_MAP*.md")
        if not ignored(relative_name(root, path))
    )
    if not authoritative_map.is_file() or authoritative_map.is_symlink():
        reporter.skip_development(
            f"authoritative theorem map {AUTHORITATIVE_THEOREM_MAP} is absent"
        )
        map_rows: list[MapRow] = []
    elif discovered_maps != [authoritative_map]:
        fail(
            "the authoritative theorem map must be the only release-relevant map; found "
            + ", ".join(relative_name(root, path) for path in discovered_maps)
        )
    else:
        map_rows = parse_theorem_map(authoritative_map)

    contract_data = load_lean_contract(root, reporter)
    expected_targets: list[LeanTarget] = []
    expected_namespace: tuple[int, int] | None = None
    if contract_data is not None:
        expected_targets, expected_declarations, expected_theorems = contract_data
        expected_namespace = (expected_declarations, expected_theorems)

    if map_rows and expected_targets:
        if not register_records:
            fail("reviewed Lean contract cannot be checked without the record register")
        mapped, manuscript_records = crosscheck_map_contract(
            map_rows, register_records, expected_targets
        )
        reporter.passed(
            f"theorem map preserves {len(map_rows)} reviewed row associations across "
            f"{len(set(manuscript_records))} current manuscript records"
        )
    elif map_rows:
        mapped = [name for row in map_rows for name in row.declarations]
        manuscript_records = [
            number for row in map_rows for number in row.record_numbers
        ]
        unknown_records = sorted(set(manuscript_records) - set(register_records))
        if unknown_records:
            fail(
                "Lean theorem map refers to unknown manuscript records: "
                + ", ".join(unknown_records)
            )
    else:
        mapped = []
        manuscript_records = []

    missing_status = sorted(set(lean_status_targets) - set(mapped))
    if missing_status:
        fail(
            "manuscript Lean status names are absent from the theorem map: "
            + ", ".join(missing_status)
        )

    toolchain = (lean_root / "lean-toolchain").read_text(encoding="utf-8").strip()
    if not toolchain or re.search(r"\b(?:stable|nightly|latest)\b", toolchain, re.I):
        fail(f"Lean toolchain is not pinned to an exact release: {toolchain!r}")
    if not (lean_root / "lake-manifest.json").is_file():
        fail("Lean project is missing lake-manifest.json dependency lock")
    lakefile = (
        lean_root / "lakefile.toml"
        if (lean_root / "lakefile.toml").is_file()
        else lean_root / "lakefile.lean"
    )
    lake_source = lakefile.read_text(encoding="utf-8")
    warning_fatal = (
        "warningAsError" in lake_source
        or (
            "moreLeanArgs" in lake_source
            and re.search(r"[\"']-E[\"']", lake_source)
            and re.search(r"[\"']warning[\"']", lake_source)
        )
    )
    if not warning_fatal:
        fail("Lean project does not configure warnings as errors")
    lake = shutil.which("lake")
    if lake is None:
        fail("lake is required for the pinned Lean build")

    build = run_command(
        [lake, "--wfail", "build"],
        lean_root,
        environment={"LEAN_ABORT_ON_PANIC": "1"},
    )
    if build.returncode != 0:
        fail(f"warning-fatal Lean build failed\n{build.stdout[-10000:]}")
    if re.search(r"(?im)^.*\bwarning:", build.stdout):
        fail("Lean build emitted a warning despite the warning-fatal configuration")
    reporter.passed(f"pinned warning-fatal Lean build ({toolchain})")

    if mapped:
        modules = lean_module_names(lean_root)
        if not modules:
            fail("Lean project contains no importable source modules")
        with tempfile.TemporaryDirectory(prefix="prsc4-lean-probe-") as temporary:
            probe = Path(temporary) / "ReviewedTargets.lean"
            probe_lines: list[str] = []
            for module in modules:
                probe_lines.append(f"import {module}")
            probe_lines.extend(["", "set_option maxRecDepth 10000", ""])
            for name in mapped:
                probe_lines.append(f"#check {name}")
            kind_sentinels: list[str] = []
            if expected_targets:
                # Each command is compiled separately. A single command with
                # hundreds of matches can exhaust Lean's LCNF heartbeat limit.
                probe_lines.extend(["", "open Lean Elab Command", ""])
                batch_size = 64
                for offset in range(0, len(expected_targets), batch_size):
                    batch = expected_targets[offset : offset + batch_size]
                    probe_lines.extend(["run_cmd do", "  let env ← getEnv"])
                    for target in batch:
                        constructor = "thmInfo" if target.kind == "theorem" else "defnInfo"
                        probe_lines.extend(
                            [
                                f"  match env.find? ``{target.declaration} with",
                                f"  | some (.{constructor} _) => pure ()",
                                f"  | some _ => throwError \"wrong declaration kind: {target.declaration}\"",
                                f"  | none => throwError \"missing reviewed declaration: {target.declaration}\"",
                            ]
                        )
                    sentinel = f"FAIL-CLOSED REVIEWED LEAN KIND BATCH PASS: {offset}:{len(batch)}"
                    kind_sentinels.append(sentinel)
                    probe_lines.extend([f'  logInfo "{sentinel}"', ""])
                probe_lines.extend([
                    "run_cmd do",
                    f'  logInfo "FAIL-CLOSED REVIEWED LEAN TARGET KIND PASS: {len(expected_targets)}"',
                ])
            probe.write_text("\n".join(probe_lines) + "\n", encoding="utf-8")
            resolution = run_command(
                [lake, "env", "lean", "-E", "warning", str(probe)], lean_root
            )
        if resolution.returncode != 0:
            fail(
                "theorem-map declaration resolution failed\n"
                + resolution.stdout[-10000:]
            )
        if expected_targets:
            kind_sentinels.append(
                f"FAIL-CLOSED REVIEWED LEAN TARGET KIND PASS: {len(expected_targets)}"
            )
            if any(resolution.stdout.count(sentinel) != 1 for sentinel in kind_sentinels):
                fail("Lean declaration-kind probe lacks an exact unique batch/pass sentinel")
        reporter.passed(
            f"all {len(mapped)} theorem-map names resolve with their reviewed Lean kinds"
        )

    expected_audit = lean_root / "KomorebiPaperIV/KernelAudit.lean"
    audit_files = sorted(
        path
        for path in lean_root.rglob("*.lean")
        if "kernelaudit" in path.stem.casefold()
        and not any(part in IGNORED_DIRECTORIES for part in path.parts)
    )
    if not expected_audit.is_file() or expected_audit.is_symlink():
        reporter.skip_development("Lean KernelAudit source is not yet integrated")
        return
    if audit_files != [expected_audit]:
        fail("expected exactly KomorebiPaperIV/KernelAudit.lean as the kernel audit")

    combined_outputs: list[str] = []
    audit_targets: list[str] = []
    for audit in audit_files:
        audit_source = audit.read_text(encoding="utf-8")
        targets = re.findall(
            r"(?m)^\s*#print\s+axioms\s+([A-Za-z_][A-Za-z0-9_']*(?:\.[A-Za-z_][A-Za-z0-9_']*)+)\s*$",
            audit_source,
        )
        if not targets:
            fail(f"kernel audit contains no active #print axioms directives: {audit}")
        audit_targets.extend(targets)
        result = run_command(
            [lake, "env", "lean", "-E", "warning", str(audit)], lean_root
        )
        if result.returncode != 0:
            fail(f"kernel axiom audit failed: {audit}\n{result.stdout[-10000:]}")
        check_axiom_output(result.stdout, relative_name(root, audit))
        combined_outputs.append(result.stdout)

    duplicates = sorted(
        name for name, count in Counter(audit_targets).items() if count > 1
    )
    if duplicates:
        fail("duplicate kernel-audit targets: " + ", ".join(duplicates))
    if mapped:
        missing_audit = sorted(set(mapped) - set(audit_targets))
        extra_audit = sorted(set(audit_targets) - set(mapped))
        if missing_audit or extra_audit:
            fail(
                "kernel-audit target set disagrees with the reviewed theorem map; "
                f"missing={missing_audit}; extra={extra_audit}"
            )

    live_joined = "\n".join(combined_outputs)
    live_sentinels = kernel_sentinels(live_joined)
    if len(live_sentinels) != 1:
        fail("live kernel audit lacks one exact Paper IV pass sentinel")
    live_declarations, live_theorems, live_mapped = live_sentinels[0]
    if live_theorems > live_declarations:
        fail("kernel sentinel reports more theorems than declarations")
    if live_mapped != len(audit_targets):
        fail(
            "live kernel sentinel target count disagrees with #print axioms list: "
            f"{live_mapped} != {len(audit_targets)}"
        )
    if expected_namespace is not None and (
        live_declarations,
        live_theorems,
    ) != expected_namespace:
        fail(
            "live kernel namespace counts disagree with the reviewed contract: "
            f"{(live_declarations, live_theorems)} != {expected_namespace}"
        )

    formalization_metadata = nested_metadata(
        release_metadata(root), "verification", "formalization"
    )
    check_metadata_values(
        formalization_metadata,
        {
            "theorem_map_rows": len(map_rows),
            "mapped_declarations": len(mapped),
            "mapped_theorems": sum(
                target.kind == "theorem" for target in expected_targets
            ),
            "mapped_constructions": sum(
                target.kind == "definition" for target in expected_targets
            ),
            "namespace_declarations": live_declarations,
            "namespace_theorem_declarations": live_theorems,
        },
        "Lean-formalization",
    )

    expected_transcript = lean_root / "kernel_audit_output.txt"
    transcripts = sorted(
        path
        for path in root.rglob("kernel_audit_output*.txt")
        if not ignored(relative_name(root, path))
    )
    if not expected_transcript.is_file() or expected_transcript.is_symlink():
        reporter.skip_development("saved kernel-audit transcript is not yet integrated")
    else:
        if transcripts != [expected_transcript]:
            fail("expected exactly formalization/lean/kernel_audit_output.txt")
        joined = "\n".join(path.read_text(encoding="utf-8") for path in transcripts)
        check_axiom_output(joined, "saved kernel-audit transcript")
        transcript_targets = re.findall(
            r"(?m)^'([A-Za-z_][A-Za-z0-9_']*(?:\.[A-Za-z_][A-Za-z0-9_']*)+)' "
            r"(?:depends on axioms:|does not depend on any axioms)",
            joined,
        )
        if len(transcript_targets) != len(set(transcript_targets)):
            fail("saved kernel transcript contains duplicate declaration reports")
        if set(transcript_targets) != set(audit_targets):
            fail(
                "saved kernel transcript target set disagrees with KernelAudit source"
            )
        sentinels = kernel_sentinels(joined)
        if len(sentinels) != 1:
            fail("saved kernel transcript lacks one exact Paper IV pass sentinel")
        if sentinels[0] != live_sentinels[0]:
            fail("saved kernel sentinel disagrees with the live kernel audit")
        _declarations, _theorems, mapped_total = sentinels[0]
        if mapped and mapped_total != len(mapped):
            fail(
                "kernel sentinel mapped-target count disagrees with theorem map: "
                f"{mapped_total} != {len(mapped)}"
            )
        reporter.passed(
            f"kernel transcript covers all {len(audit_targets)} explicit targets"
        )
    reporter.passed(
        f"live kernel audit permits only {', '.join(sorted(ALLOWED_AXIOMS))}"
    )


def check_final_latex_log(log: Path) -> None:
    source = log.read_text(encoding="utf-8", errors="replace")
    failures = {
        "undefined references": r"undefined references",
        "undefined citations": r"citation.+undefined",
        "overfull boxes": r"Overfull \\[hv]box",
        "underfull boxes": r"Underfull \\[hv]box",
        "missing characters": r"Missing character:",
        "multiply defined labels": r"multiply defined",
    }
    findings: list[str] = []
    lines = source.splitlines()
    for label, pattern in failures.items():
        matches = list(re.finditer(pattern, source, re.IGNORECASE))
        if not matches:
            continue
        locations: list[str] = []
        for match in matches[:6]:
            line_number = source.count("\n", 0, match.start()) + 1
            excerpt = " ".join(
                part.strip()
                for part in lines[line_number - 1 : min(line_number + 2, len(lines))]
            )
            locations.append(f"log line {line_number}: {excerpt}")
        findings.append(f"{label} ({len(matches)}): " + " || ".join(locations))
    if findings:
        fail("final LaTeX log is not clean\n" + "\n".join(findings))


def check_aux_register(aux: Path, records: dict[str, RegisterRecord]) -> None:
    labels: dict[str, str] = {}
    for number, line in enumerate(
        aux.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
    ):
        match = re.match(r"\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}", line)
        if match is None:
            continue
        label, displayed_number = match.groups()
        if label.endswith("@cref"):
            continue
        if label in labels:
            fail(f"duplicate base label {label!r} in rebuilt AUX at line {number}")
        labels[label] = displayed_number
    expected = {record.label: record.number for record in records.values()}
    nonrecord_extras = {
        label for label in set(labels) - set(expected) if not label.startswith("sec:")
    }
    if not set(expected).issubset(labels) or nonrecord_extras:
        missing = sorted(set(expected) - set(labels))
        extra = sorted(nonrecord_extras)
        fail(f"rebuilt AUX/register label mismatch; missing={missing}; extra={extra}")
    wrong_numbers = sorted(
        f"{label}: {labels[label]} != {record_number}"
        for label, record_number in expected.items()
        if labels[label] != record_number
    )
    if wrong_numbers:
        fail("rebuilt AUX/register numbering mismatch; " + "; ".join(wrong_numbers))


def prepare_latex_build(root: Path, destination: Path) -> None:
    paper = root / "paper"
    for path in paper.rglob("*"):
        if not path.is_file() or path.name == "paper4.pdf" or ignored(
            path.relative_to(paper).as_posix()
        ):
            continue
        target = destination / path.relative_to(paper)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

    tex = destination / "paper4.tex"
    source = tex.read_text(encoding="utf-8")
    bib_source = destination / "references.bib"
    bibliography_groups = re.findall(r"\\bibliography\{([^}]+)\}", source)
    if bibliography_groups and not bib_source.is_file():
        fail("paper4.tex requests a bibliography but paper/references.bib is absent")
    for group in bibliography_groups:
        for entry in group.split(","):
            name = entry.strip()
            if not name:
                fail("paper4.tex contains an empty bibliography name")
            target = destination / f"{name}.bib"
            if not target.exists():
                shutil.copy2(bib_source, target)

    styles = re.findall(r"\\bibliographystyle\{([^}]+)\}", source)
    for style in styles:
        local = destination / f"{style}.bst"
        if local.is_file():
            continue
        kpsewhich = shutil.which("kpsewhich")
        if kpsewhich is None:
            fail(f"kpsewhich is needed to locate bibliography style {style}.bst")
        lookup = run_command([kpsewhich, f"{style}.bst"], destination)
        if lookup.returncode != 0 or not lookup.stdout.strip():
            fail(
                f"bibliography style {style}.bst is not bundled and is unavailable in TeX"
            )


def one_pdf_build(root: Path, destination: Path) -> Path:
    destination.mkdir(parents=True)
    prepare_latex_build(root, destination)
    pdflatex = shutil.which("pdflatex")
    bibtex = shutil.which("bibtex")
    if pdflatex is None or bibtex is None:
        fail("pdflatex and bibtex are required for the clean paper build")
    environment = {"SOURCE_DATE_EPOCH": "1788393600", "FORCE_SOURCE_DATE": "1"}
    latex_command = [
        pdflatex,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        "paper4.tex",
    ]
    first = run_command(latex_command, destination, environment=environment)
    if first.returncode != 0:
        fail(f"first pdflatex pass failed\n{first.stdout[-10000:]}")
    bib = run_command([bibtex, "paper4"], destination, environment=environment)
    if bib.returncode != 0:
        fail(f"bibtex failed\n{bib.stdout[-10000:]}")
    for pass_number in range(2, 5):
        result = run_command(latex_command, destination, environment=environment)
        if result.returncode != 0:
            fail(
                f"pdflatex pass {pass_number} failed\n{result.stdout[-10000:]}"
            )
    pdf = destination / "paper4.pdf"
    log = destination / "paper4.log"
    if not pdf.is_file() or not pdf.stat().st_size:
        fail("clean LaTeX build did not produce paper4.pdf")
    check_final_latex_log(log)
    return pdf


def check_pdf(
    root: Path,
    mode: str,
    write_pdf: bool,
    manifest: Path | None,
    register_records: dict[str, RegisterRecord],
    reporter: Reporter,
) -> None:
    if write_pdf and manifest is not None:
        fail("--write-pdf is disabled while a checksum manifest exists")
    with tempfile.TemporaryDirectory(prefix="prsc4-pdf-") as temporary:
        base = Path(temporary)
        first = one_pdf_build(root, base / "a")
        second = one_pdf_build(root, base / "b")
        first_hash = sha256(first)
        second_hash = sha256(second)
        if first_hash != second_hash:
            fail(
                "clean PDF builds are not deterministic: "
                f"{first_hash} != {second_hash}"
            )
        reporter.passed(f"deterministic clean PDF rebuild: {first_hash}")
        check_aux_register(first.with_suffix(".aux"), register_records)
        check_aux_register(second.with_suffix(".aux"), register_records)
        reporter.passed(
            f"both clean AUX builds match all {len(register_records)} register labels and numbers"
        )

        installed = root / "paper/paper4.pdf"
        if write_pdf:
            shutil.copy2(first, installed)
            reporter.passed("installed clean rebuild at paper/paper4.pdf")
        elif not installed.is_file():
            reporter.skip_development(
                "paper/paper4.pdf is absent; rerun --development --write-pdf before freezing"
            )
        else:
            installed_hash = sha256(installed)
            if installed_hash != first_hash:
                if mode == "release":
                    fail(
                        "shipped paper/paper4.pdf is stale: "
                        f"shipped {installed_hash}, rebuilt {first_hash}"
                    )
                reporter.skip_development(
                    "paper/paper4.pdf differs from the clean deterministic rebuild"
                )
            else:
                reporter.passed("shipped PDF is byte-identical to the clean rebuild")

        pdfinfo = shutil.which("pdfinfo")
        if pdfinfo is None:
            reporter.skip_development(
                "pdfinfo is unavailable, so rebuilt-PDF structural parsing was not run"
            )
        else:
            result = run_command([pdfinfo, str(first)], root)
            if result.returncode != 0 or "Pages:" not in result.stdout:
                fail("pdfinfo could not parse the rebuilt PDF")
            page_match = re.search(r"(?m)^Pages:\s+(\d+)\s*$", result.stdout)
            if page_match is None:
                fail("pdfinfo did not report an integer page count")
            manuscript_metadata = nested_metadata(
                release_metadata(root), "verification", "manuscript"
            )
            check_metadata_values(
                manuscript_metadata,
                {
                    "pdf_pages": int(page_match.group(1)),
                    "pdf_sha256": first_hash,
                },
                "manuscript PDF",
            )
            reporter.passed("rebuilt PDF passes pdfinfo structural parsing")
        pdffonts = shutil.which("pdffonts")
        if pdffonts is None:
            reporter.skip_development(
                "pdffonts is unavailable, so embedded-font verification was not run"
            )
        else:
            result = run_command([pdffonts, str(first)], root)
            if result.returncode != 0:
                fail("pdffonts could not inspect the rebuilt PDF")
            rows = [line for line in result.stdout.splitlines()[2:] if line.strip()]
            embedded: list[str] = []
            for row in rows:
                match = re.search(
                    r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$",
                    row,
                    re.IGNORECASE,
                )
                if match is None:
                    fail(f"could not parse pdffonts row: {row!r}")
                embedded.append(match.group(1).lower())
            if not embedded or any(value != "yes" for value in embedded):
                fail("rebuilt PDF contains an unembedded font")
            reporter.passed("all rebuilt PDF fonts are embedded")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--mode", choices=("release", "development"), required=True)
    parser.add_argument("--write-pdf", action="store_true")
    parser.add_argument(
        "--archive",
        type=Path,
        help="final ZIP outside the release root; mandatory for a release pass",
    )
    parser.add_argument(
        "--lean-packages-cache",
        type=Path,
        help=(
            "validated external .lake/packages directory; package Git HEADs must "
            "match lake-manifest.json exactly"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    reporter = Reporter(args.mode)
    lean_root: Path | None = None
    lean_cache: Path | None = None
    try:
        if args.write_pdf and args.mode != "development":
            fail("--write-pdf is permitted only in explicit development mode")
        if args.write_pdf and args.archive is not None:
            fail("--write-pdf cannot be combined with final archive verification")
        if not (root / "paper/paper4.tex").is_file():
            fail("missing paper/paper4.tex")
        if not (root / "paper/references.bib").is_file():
            fail("missing paper/references.bib")
        if not os.access(root / "VERIFY.sh", os.X_OK):
            fail("VERIFY.sh is not executable")

        lean_root = find_lean_root(root)
        check_lean_start_state(
            lean_root,
            args.mode,
            args.lean_packages_cache is not None,
            reporter,
        )
        if args.lean_packages_cache is not None:
            if lean_root is None:
                fail("--lean-packages-cache requires a complete Lean project")
            lean_cache = validate_lean_packages_cache(
                root, lean_root, args.lean_packages_cache, reporter
            )

        check_transient_artifacts(root, reporter)
        files = release_files(root)
        reporter.passed(
            f"{len(files)} release-relevant files use short portable paths"
        )
        archive_metadata = nested_metadata(
            release_metadata(root), "verification", "archive"
        )
        check_metadata_values(
            archive_metadata,
            {
                "checksum_manifest_entries": sum(
                    name not in MANIFEST_NAMES for name in files
                )
            },
            "archive file-count",
        )
        manifest = check_manifest(root, files, reporter)
        check_archive(root, args.archive, manifest, files, reporter)
        lean_targets, _inherited_targets = check_evidence_claims(
            root, files, reporter
        )
        requirements = parse_requirements(root)
        if requirements:
            reporter.passed(
                f"requirements.txt contains {len(requirements)} exact version pins"
            )
        run_regression_suites(root, files, requirements, reporter)
        register_records = check_generated_register(root, files, reporter)
        if lean_cache is not None:
            assert lean_root is not None
            install_lean_packages_cache(lean_root, lean_cache)
        try:
            check_lean(
                root,
                args.mode,
                lean_targets,
                register_records,
                reporter,
                lean_cache,
            )
        finally:
            if lean_cache is not None:
                assert lean_root is not None
                remove_local_lake_cache_link(lean_root, lean_cache)
        check_pdf(
            root,
            args.mode,
            args.write_pdf,
            manifest,
            register_records,
            reporter,
        )
    except GateFailure as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if reporter.development_skips:
        print(
            "DEVELOPMENT CHECKPOINT PASS: executable checks passed, but "
            f"{len(reporter.development_skips)} release gate(s) were explicitly skipped."
        )
        print("NOT RELEASE READY")
    else:
        print("FAIL-CLOSED PAPER IV RELEASE VERIFICATION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
