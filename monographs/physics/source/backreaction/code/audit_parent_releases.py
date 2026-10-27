#!/usr/bin/env python3
"""Read-only provenance and reproducibility audit for the frozen parent releases."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_manifest(root: Path, manifest: Path) -> dict:
    checked = 0
    failed: list[dict] = []
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        expected, relative = raw.split(None, 1)
        relative = relative.lstrip(" *")
        target = root / relative
        checked += 1
        if not target.is_file():
            failed.append({"path": relative, "reason": "missing"})
        else:
            observed = sha256(target)
            if observed.lower() != expected.lower():
                failed.append(
                    {
                        "path": relative,
                        "reason": "hash_mismatch",
                        "expected": expected,
                        "observed": observed,
                    }
                )
    return {"checked": checked, "failed": failed}


def flatten_counts(obj) -> tuple[int, int]:
    if isinstance(obj, dict):
        for pass_key, fail_key in (
            ("pass_count", "fail_count"),
            ("checks_pass", "checks_fail"),
            ("pass", "fail"),
        ):
            if isinstance(obj.get(pass_key), int) and isinstance(obj.get(fail_key), int):
                return int(obj[pass_key]), int(obj[fail_key])
        checks = obj.get("checks")
        if isinstance(checks, list):
            passes = sum(
                str(row.get("status", "")).upper() == "PASS"
                for row in checks
                if isinstance(row, dict)
            )
            failures = sum(
                str(row.get("status", "")).upper() == "FAIL"
                for row in checks
                if isinstance(row, dict)
            )
            return passes, failures
        if isinstance(checks, dict):
            p, f = flatten_counts(checks)
            if p or f:
                return p, f
        for key in ("counts", "verification", "validation", "summary"):
            if key in obj:
                p, f = flatten_counts(obj[key])
                if p or f:
                    return p, f
        passes = failures = 0
        for value in obj.values():
            p, f = flatten_counts(value)
            passes += p
            failures += f
        return passes, failures
    if isinstance(obj, list):
        passes = failures = 0
        for value in obj:
            p, f = flatten_counts(value)
            passes += p
            failures += f
        return passes, failures
    return 0, 0


def json_verification_ledger(root: Path) -> list[dict]:
    rows = []
    for path in sorted((root / "data").rglob("*Verification.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append(
                {
                    "path": str(path.relative_to(root)),
                    "pass": 0,
                    "fail": 1,
                    "status": "PARSE_FAILURE",
                    "note": str(exc),
                }
            )
            continue
        passes, failures = flatten_counts(data)
        if passes == failures == 0 and isinstance(data, dict) and "checks" in data:
            checks = data["checks"]
            if isinstance(checks, list):
                passes = sum(
                    str(row.get("status", "")).upper() == "PASS"
                    for row in checks
                    if isinstance(row, dict)
                )
                failures = sum(
                    str(row.get("status", "")).upper() == "FAIL"
                    for row in checks
                    if isinstance(row, dict)
                )
        rows.append(
            {
                "path": str(path.relative_to(root)),
                "pass": passes,
                "fail": failures,
                "status": "FROZEN_OUTPUT_ONLY",
                "note": "Counts describe the archived record and are not a rerun",
            }
        )
    return rows


def cross_volume_lineage(volume_i: Path, volume_ii: Path) -> list[dict]:
    by_hash: dict[str, list[Path]] = {}
    for path in volume_i.rglob("*"):
        if path.is_file() and path.stat().st_size > 0:
            by_hash.setdefault(sha256(path), []).append(path)
    rows: list[dict] = []
    for path in volume_ii.rglob("*"):
        if not path.is_file() or path.stat().st_size == 0:
            continue
        digest = sha256(path)
        ancestors = by_hash.get(digest, [])
        if ancestors:
            ancestor = next(
                (candidate for candidate in ancestors if candidate.name == path.name),
                ancestors[0],
            )
            rows.append(
                {
                    "volume_ii_path": str(path.relative_to(volume_ii)),
                    "volume_i_path": str(ancestor.relative_to(volume_i)),
                    "sha256": digest,
                    "size_bytes": path.stat().st_size,
                    "meaning": "byte-identical lineage, not independent reproduction",
                }
            )
    return rows


def python_root_audit(root: Path) -> list[dict]:
    rows = []
    pattern = re.compile(r"ROOT\s*=\s*Path\(__file__\)\.resolve\(\)\.parents\[(\d+)\]")
    for path in sorted((root / "verification").rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            ast.parse(text)
            syntax = "PASS"
        except SyntaxError as exc:
            syntax = f"FAIL line {exc.lineno}"
        match = pattern.search(text)
        depth = int(match.group(1)) if match else None
        expected_root = path.resolve().parents[depth] if depth is not None else None
        misplaced = bool(depth is not None and expected_root.name == "verification")
        rows.append(
            {
                "path": str(path.relative_to(root)),
                "syntax": syntax,
                "declared_parent_index": depth,
                "resolved_root_name": expected_root.name if expected_root else "",
                "requires_staging": misplaced,
                "status": "REQUIRES_STAGING" if misplaced else "STATIC_ONLY",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--volume-i", required=True, type=Path)
    parser.add_argument("--volume-ii", required=True, type=Path)
    parser.add_argument("--supplement-i", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    manifest_result = verify_manifest(
        args.volume_ii, args.volume_ii / "SOURCE_CONTENT_SHA256SUMS.txt"
    )
    ledger = json_verification_ledger(args.volume_ii)
    lineage = cross_volume_lineage(args.volume_i, args.volume_ii)
    roots = python_root_audit(args.volume_ii)
    write_csv(args.output / "frozen_verification_ledger.csv", ledger)
    write_csv(args.output / "cross_volume_lineage.csv", lineage)
    write_csv(args.output / "python_staging_audit.csv", roots)

    cited_paths = [
        "verification/Scale_Covariant_Dark_Sector_Verification.py",
        "data/Scale_Covariant_Dark_Sector_Verification.json",
        "data/scale_covariant_dark_checks.csv",
        "RELEASE_MANIFEST.json",
    ]
    broken = []
    for relative in cited_paths:
        target = args.volume_ii / relative
        broken.append(
            {
                "path": relative,
                "exists": target.exists(),
                "status": "PRESENT" if target.exists() else "MISSING",
                "boundary": "required by chapter or release documentation",
            }
        )
    typo_source = (
        args.supplement_i
        / "source/Projector_Refinement_Physics_Volume_I_Technical_Supplement.tex"
    )
    typo_present = typo_source.is_file() and "\textbf{CORR.}" in typo_source.read_text(
        encoding="utf-8", errors="replace"
    )
    broken.append(
        {
            "path": str(typo_source.relative_to(args.supplement_i)),
            "exists": typo_source.exists(),
            "status": "RELEASED_TYPO" if typo_present else "NO_MATCH",
            "boundary": "must be corrected by a versioned patch, not silent overwrite",
        }
    )
    write_csv(args.output / "errata_and_broken_references.csv", broken)

    total_pass = sum(int(row["pass"]) for row in ledger)
    total_fail = sum(int(row["fail"]) for row in ledger)
    summary = {
        "volume_ii_manifest_entries": manifest_result["checked"],
        "volume_ii_manifest_failures": len(manifest_result["failed"]),
        "frozen_verification_files": len(ledger),
        "frozen_internal_pass_count": total_pass,
        "frozen_internal_fail_count": total_fail,
        "cross_volume_identical_file_pairs": len(lineage),
        "scripts_requiring_staging": sum(bool(row["requires_staging"]) for row in roots),
        "missing_declared_paths": sum(row["status"] == "MISSING" for row in broken),
        "released_volume_i_supplement_typo_detected": typo_present,
        "manifest_failures": manifest_result["failed"],
        "claim_boundary": "Integrity and lineage do not establish scientific correctness",
    }
    (args.output / "parent_release_audit.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if manifest_result["failed"]:
        raise SystemExit("parent manifest failure")


if __name__ == "__main__":
    main()
