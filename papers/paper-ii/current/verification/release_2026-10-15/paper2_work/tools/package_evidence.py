#!/usr/bin/env python3
"""Copy Paper II release evidence after the release owner accepts the final gates.

This helper copies evidence only. It does not run Lean, certify gates, produce a
ZIP/root manifest/release status, or modify production sources or publications.
An existing destination is never overwritten. Run explicitly with --copy.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile

RELEASE_NAME = "Komorebi_Paper_II_Release_2026-10-15"
EVIDENCE_NAME = "release_2026-10-15"
BLOCKED_DIRECTORIES = {
    ".git", ".lake", ".cache", "__pycache__", "node_modules", "objects",
    "build", "buildobjects", "build_objects", "inputs", "recovered",
    "library_helpers", "image_cache", "images_cache", "preview", "previews",
}
BLOCKED_SUFFIXES = {
    ".olean", ".ilean", ".o", ".a", ".so", ".dylib", ".dll", ".exe",
    ".pyc", ".pyo", ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".pdf",
}
BRANCHES = (
    "weighted", "contour_bridge", "coordinates", "arithmetic", "smith",
    "resultant", "transfer", "transfer_promoted", "defects",
)
TOOL_FILES = (
    "check_module.py", "replay_current.py", "replay_current_adaptation.json",
    "assemble_correspondence.py", "accept_current_correspondence.py",
    "package_evidence.py", "finalize_release.py",
)
CHECK_DIRECTORY = re.compile(r".*_checks?$|.*_check[0-9]+$")
RELEASE_WORK_RECORD = re.compile(r"(?:CHECKPOINT.*|.*INTEGRITY.*|.*SOURCE.*MANIFEST.*)\.jsonl?$", re.I)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def forbidden_component(name: str) -> bool:
    lower = name.lower()
    return (
        name in BLOCKED_DIRECTORIES
        or lower.startswith(("preview_", "previews_", "image_cache", "library_", "upload_"))
        or lower in {"cache", "rendered", "renders", "render_pages"}
    )


def allowed_file(path: Path) -> bool:
    return path.suffix.lower() not in BLOCKED_SUFFIXES and not forbidden_component(path.name)


def regular_files(root: Path):
    """Walk only the selected tree, pruning caches before descending."""
    if root.is_symlink():
        raise ValueError(f"Selected evidence tree is a symlink: {root}")
    if not root.is_dir():
        return
    for parent, directories, names in os.walk(root, followlinks=False):
        directories[:] = sorted(d for d in directories if not forbidden_component(d))
        for directory in directories:
            candidate = Path(parent) / directory
            if candidate.is_symlink():
                raise ValueError(f"Selected evidence directory is a symlink: {candidate}")
        for name in sorted(names):
            path = Path(parent) / name
            if not allowed_file(path):
                continue
            mode = path.lstat().st_mode
            if not stat.S_ISREG(mode):
                raise ValueError(f"Selected evidence is not a regular file: {path}")
            yield path


def select_files(workspace: Path) -> tuple[dict[Path, set[str]], list[str]]:
    work = workspace / "paper2_work"
    if not work.is_dir():
        raise ValueError(f"Missing evidence workspace: {work}")
    selected: dict[Path, set[str]] = {}
    optional_missing: list[str] = []

    def add(path: Path, category: str) -> None:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Selected source must be a regular file: {path}")
        # The mapping must remain a local, traversal-free workspace-relative tree.
        path.relative_to(workspace)
        if allowed_file(path):
            selected.setdefault(path, set()).add(category)

    def tree(path: Path, category: str, *, audit_only: bool = False) -> None:
        if not path.exists():
            optional_missing.append(str(path.relative_to(workspace)))
            return
        for file in regular_files(path):
            if not audit_only or file.suffix.lower() in {".json", ".jsonl", ".txt", ".diff", ".patch"}:
                add(file, category)

    tree(work / "audit", "mathematical/editorial/semantic audit", audit_only=True)
    tree(work / "audit" / "upstream_duplicate_review", "exact upstream overlap review and kernel-body controls")
    add(work / "audit" / "review_final_receipt.py", "independent final receipt validation")
    for branch in BRANCHES:
        tree(work / branch, "branch drafts, reports and retained check evidence")
    # Names include coordinate_checks, transfer_check01, helper_review_check,
    # baseline_owned_reviewed_check, and all future sibling attempts of that form.
    for child in sorted(work.iterdir()):
        if child.is_dir() and CHECK_DIRECTORY.fullmatch(child.name):
            tree(child, "development check receipts, logs and source snapshots")
    for name in ("baseline_compile", "baseline_owned_probe", "runtime_probe"):
        tree(work / name, "baseline/runtime source and receipt evidence")
    for child in sorted(work.iterdir()):
        if child.is_dir() and (child.name == "final_audit" or child.name.startswith("final_audit_")
                               or child.name.startswith("audit_controls_")):
            tree(child, "final replay or positive/negative control evidence")
    tree(work / "computation_final", "bounded computation evidence and replay tools")
    tree(work / "scripts", "editorial and evidence recording scripts")
    for child in sorted(work.iterdir()):
        if child.is_dir() and (child.name == "editorial_before" or child.name.startswith("editorial_before_")):
            tree(child, "pre-edit manuscript snapshots")
    for name in TOOL_FILES:
        path = work / "tools" / name
        if not path.is_file():
            raise ValueError(f"Required replay/packaging tool missing: {path}")
        add(path, "replay/correspondence/packaging tool")
    tree(work / "tools" / "final_audit", "final audit tools, fixtures and helper reviews")
    # Current top-level records include checkpoint, continuity, source-module,
    # runtime-resource, cleanup, and object-deduplication provenance records.
    # Library delivery requests/results and the process lock are intentionally absent.
    for file in sorted(work.iterdir()):
        if file.is_file() and file.suffix.lower() in {".json", ".jsonl", ".txt", ".diff", ".sha256"}:
            if allowed_file(file):
                add(file, "checkpoint, integrity, source inventory or runtime provenance")
    # Paper I's sibling release_work checkpoints remain outside this Paper II
    # evidence package. The shared runtime is bound by runtime_bindings.json.
    if not selected:
        raise ValueError("No evidence selected")
    return selected, optional_missing


def readme(workspace: Path, total: int, count: int) -> str:
    return f"""PAPER II — RELEASE EVIDENCE, 2026-10-15

This directory contains {count} byte-for-byte evidence copies ({total} payload bytes).
EVIDENCE_INDEX.json maps each original absolute source path and workspace-relative
path to its packaged path, byte size and SHA-256. The index is an evidence-copy
index, not a proof-coverage certificate or release gate/status declaration.
Failed development and negative-control receipts are deliberately retained.

HISTORICAL LOCATIONS
The original workspace was {workspace}.
Absolute paths inside original receipts, logs, scripts and reports are historical
provenance. Their bytes have not been rewritten to simulate a new execution.
Use EVIDENCE_INDEX.json to locate an included original source in this directory.
A referenced path may identify an intentionally omitted compiler object, external
runtime/dependency source, recovered input archive, or other external input.

LAYOUT AND REPLAY
Workspace-relative paths are preserved, notably paper2_work/tools/ alongside
paper2_work/baseline_compile/, paper2_work/final_audit/ and the branch check trees.
The sibling replay_current.py dependency of check_module.py is included. The
final-audit helper directory, fixtures, runtime bindings and helper reviews are
also included. All tools are preserved as executed, including any historical
absolute defaults; inspect and explicitly adapt those locations for relocation.
The production sources remain elsewhere in the release at formal/current.
Compiler/dependency runtimes and .olean/.ilean objects are deliberately omitted.
A fresh replay needs the pinned external runtime and newly rebuilt objects; these
copies alone do not constitute a ready-to-run compiler environment. Existing
recorded PASS results do not certify a subsequent replay or a broader claim.

EXCLUSIONS AND SCOPE
No runtime, imported/recovered archive, library transfer material, object tree,
bytecode, preview/image cache or publication PDF is included. This helper does
not alter production sources/publications, create an archive or root manifest,
or decide the final replay/correspondence/visual-QA gates. The release owner runs
it only after accepting those separate gates.

INDEX INTEGRITY
Every copied file appears in files with a SHA-256. This generated README appears
in generated_files with its SHA-256. The index cannot contain its own checksum;
the final release's separate integrity mechanism may cover it after packaging.
"""


def package(workspace: Path, destination: Path, max_bytes: int) -> dict:
    selected, optional_missing = select_files(workspace)
    rows = []
    for source in sorted(selected):
        relative = source.relative_to(workspace).as_posix()
        rows.append({
            "source_path": str(source), "source_workspace_relative": relative,
            "packaged_path": relative, "bytes": source.stat().st_size,
            "sha256": digest(source), "categories": sorted(selected[source]),
        })
    total = sum(row["bytes"] for row in rows)
    if total > max_bytes:
        raise ValueError(f"Selected payload {total} bytes exceeds --max-bytes={max_bytes}")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Refusing to overwrite evidence destination: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    capacity = os.statvfs(destination.parent)
    # This managed runtime already runs as uid 0. Its filesystem reports zero
    # unprivileged availability while reserved free blocks remain writable.
    available = (capacity.f_bfree if os.geteuid() == 0 else capacity.f_bavail) * capacity.f_frsize
    if available < total + 16 * 1024 * 1024:
        raise OSError("Insufficient free space for evidence plus 16 MiB staging margin")
    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.staging-", dir=destination.parent))
    try:
        for row in rows:
            source = Path(row["source_path"])
            target = staging / row["packaged_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if target.stat().st_size != row["bytes"] or digest(target) != row["sha256"]:
                raise RuntimeError(f"Copy or concurrent source-change mismatch: {source}")
        # A fresh selection plus rehash detects new/removed/changed evidence during
        # the copy. Run only once upstream tools and QA writers have quiesced.
        current, _ = select_files(workspace)
        if set(current) != set(selected):
            raise RuntimeError("Evidence file selection changed during packaging")
        for row in rows:
            source = Path(row["source_path"])
            if source.stat().st_size != row["bytes"] or digest(source) != row["sha256"]:
                raise RuntimeError(f"Evidence source changed during packaging: {source}")
        note = staging / "README.txt"
        note.write_text(readme(workspace, total, len(rows)), encoding="utf-8")
        index = {
            "schema": "paper-ii-evidence-copy-index/v1",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "historical_workspace_root": str(workspace),
            "destination_path": str(destination),
            "interpretation": "Byte-identical evidence copies, not a release status or proof certificate.",
            "payload_file_count": len(rows), "payload_bytes": total,
            "category_file_counts": dict(sorted(Counter(c for row in rows for c in row["categories"]).items())),
            "maximum_payload_bytes": max_bytes,
            "available_bytes_before_copy": available,
            "optional_selected_roots_absent": optional_missing,
            "excluded_directory_names": sorted(BLOCKED_DIRECTORIES),
            "excluded_file_suffixes": sorted(BLOCKED_SUFFIXES),
            "files": rows,
            "generated_files": [{"packaged_path": "README.txt", "bytes": note.stat().st_size,
                                  "sha256": digest(note), "source_path": None}],
        }
        (staging / "EVIDENCE_INDEX.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
        # Check again immediately before committing; never merge into an existing tree.
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f"Destination appeared while packaging: {destination}")
        staging.rename(destination)
    except BaseException:
        shutil.rmtree(staging)
        raise
    return {"destination": str(destination), "files": len(rows), "payload_bytes": total,
            "index": str(destination / "EVIDENCE_INDEX.json")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--copy", action="store_true", required=True,
                        help="Explicitly copy after the release owner accepts all final gates.")
    parser.add_argument("--workspace-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--destination", type=Path,
                        help="Default: release package verification/release_2026-10-15.")
    parser.add_argument("--max-bytes", type=int, default=250 * 1024 * 1024)
    args = parser.parse_args()
    workspace = args.workspace_root.resolve(strict=True)
    expected = workspace / "release_package" / RELEASE_NAME / "verification" / EVIDENCE_NAME
    destination = (args.destination or expected).absolute()
    # Even an explicit override may only choose a fresh direct evidence folder in
    # this release's verification tree, preventing accidental production writes.
    verification = expected.parent.resolve(strict=True)
    if destination.parent.resolve(strict=True) != verification or destination.name in {"", ".", ".."}:
        parser.error("Destination must be a direct child of this release's verification directory")
    if args.max_bytes <= 0:
        parser.error("--max-bytes must be positive")
    try:
        result = package(workspace, destination, args.max_bytes)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Evidence packaging failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
