"""Restore the frozen solver and minimal helpers into a new offline workspace."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import zipfile

SOURCE = "Komorebi_PR_LASM_Block17_Full_Bank_Integration.zip"
RESULTS = "ARC_AGI2_Block17_public_evaluation_results_2026-10-09.zip"
HISTORY = "HISTORICAL_TRAINING_REPLAY_EVIDENCE.zip"
SOURCE_SHA = "457d66c2a45e729a3b4db9bae55a19d4f016f4a602090b82cb9e3380be3cd1b0"
HELPERS = (
    "arc-evidence/scripts/finalize_block17_public_evaluation.py",
    "arc-evidence/scripts/score_arc_submission.py",
    "arc-evidence/later-source-audit/stream_fresh_block17_dispatch.py",
    "arc-evidence/later-source-audit/stream_block17_dispatch.py",
    "arc-evidence/later-source-audit/verify_block17_unchanged.py",
    "arc-evidence/later-source-audit/block17_source_before.json",
    "arc-offline-data/arc-agi_evaluation_challenges.json",
    "arc-offline-data/arc-agi_evaluation_solutions.json",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def file_hash(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def safe_member(name):
    path = PurePosixPath(name)
    require(not path.is_absolute() and ".." not in path.parts and
            "\\" not in name and ":" not in name and name != "",
            f"Unsafe archive path: {name!r}")
    return path


def extract_one(archive, name, target):
    safe_member(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(name) as source, target.open("xb") as output:
        shutil.copyfileobj(source, output, length=1024 * 1024)


def prepare(root, destination):
    root = root.resolve()
    require(not destination.is_symlink(), "Destination already exists as a symlink; choose a new workspace.")
    destination = destination.resolve()
    require(not destination.exists(), "Destination already exists; choose a new workspace.")
    require(not destination.is_relative_to(root) and not root.is_relative_to(destination),
            "Destination must be outside the handoff and must not contain it.")
    require(destination.parent.is_dir(), "Destination parent must already exist.")
    verifier = root / "verify_release.py"
    require(verifier.is_file(), "Run this from the complete extracted handoff.")
    checked = subprocess.run([sys.executable, str(verifier), "--root", str(root)],
                             capture_output=True, text=True)
    require(checked.returncode == 0,
            "Handoff verifier failed: " + (checked.stderr.strip() or checked.stdout.strip()))
    verification = json.loads(checked.stdout)
    require(verification.get("integrity_pass") is True, "Offline handoff verification did not pass.")
    require(file_hash(root / SOURCE) == SOURCE_SHA, "Frozen source archive identity changed.")

    with zipfile.ZipFile(root / SOURCE) as source, \
            zipfile.ZipFile(root / RESULTS) as results, \
            zipfile.ZipFile(root / HISTORY) as history:
        members = source.infolist()
        require(len({m.filename for m in members}) == len(members), "Duplicate source archive member.")
        files = [m for m in members if not m.is_dir()]
        require(len(files) == 388 and all(safe_member(m.filename).parts[0] == "block17" for m in files),
                "Unexpected source archive inventory.")
        source_bytes = sum(m.file_size for m in files)
        helper_archives = {}
        for name in HELPERS:
            safe_member(name)
            require(name in results.namelist() or name in history.namelist(),
                    f"Required helper or data missing: {name}")
            helper_archives[name] = results if name in results.namelist() else history
        baseline_helper = "arc-evidence/later-source-audit/capture_restored_block17_baseline.py"
        require(baseline_helper in results.namelist() or baseline_helper in history.namelist(),
                "Restored-baseline helper is missing.")
        required_bytes = source_bytes + sum(helper_archives[n].getinfo(n).file_size for n in HELPERS)
        free_bytes = shutil.disk_usage(destination.parent).free
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            stat = os.statvfs(destination.parent)
            free_bytes = stat.f_bfree * stat.f_frsize
        require(free_bytes >= required_bytes + 1024 ** 3,
                "Insufficient free disk for restoration and an initial output reserve.")
        # Only now create anything. A failed extraction is retained for inspection;
        # a later attempt must use another destination and cannot overwrite it.
        destination.mkdir()
        for member in files:
            extract_one(source, member.filename, destination / "arc-fullbank" / member.filename)
        for name in HELPERS:
            extract_one(helper_archives[name], name, destination / name)
        carrier = results if baseline_helper in results.namelist() else history
        extract_one(carrier, baseline_helper, destination / baseline_helper)

    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1")
    baseline = destination / "arc-offline-runs/restored_block17_source_before.json"
    authenticated = subprocess.run([sys.executable, str(destination / baseline_helper),
                                    "--root", str(destination / "arc-fullbank/block17"),
                                    "--reference", str(destination / "arc-evidence/later-source-audit/block17_source_before.json"),
                                    "--output", str(baseline)], capture_output=True, text=True, env=env)
    require(authenticated.returncode == 0,
            "Restored source authentication failed: " +
            (authenticated.stderr.strip() or authenticated.stdout.strip()))
    receipt = {
        "schema": "komorebi.arc-agi2.block17.prepared-rerun.v1",
        "workspace": str(destination), "source_archive_sha256": SOURCE_SHA,
        "source_files": 388, "source_restoration_bytes": source_bytes,
        "source_baseline": str(baseline), "source_baseline_sha256": file_hash(baseline),
        "handoff_verified": True, "compiler_calls": 0, "runtime_tests_run": False,
        "archived_fresh_census_checkpoints_and_owner_receipts_copied": False,
        "scope": "Fresh workspace restoration only. Compilation and scoring are separate commands.",
    }
    (destination / "PREPARATION_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.root, args.destination), indent=2, sort_keys=True))
    except (OSError, ValueError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        print(f"Preparation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
