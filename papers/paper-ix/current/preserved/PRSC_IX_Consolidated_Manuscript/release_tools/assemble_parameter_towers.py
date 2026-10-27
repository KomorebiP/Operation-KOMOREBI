#!/usr/bin/env python3
"""Assemble and verify the cumulative Paper IX prescribed-parameter tower source release."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import zipfile


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--verification", type=Path, required=True)
    parser.add_argument("--docs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    expected_base_sha = "c1d3ebbfbe08e66698fb485a453a1c039a56ba8b19dd6d771838875fad2ea854"
    assert digest(args.base.read_bytes()) == expected_base_sha
    report_path = args.verification / "polynomial_parameter_towers_verification.json"
    report = json.loads(report_path.read_text())
    assert report["status"] == "PASS" and all(run["passed"] for run in report["runs"])
    review = json.loads((args.project / "audit/REVIEWED_SOURCES.json").read_text())
    assert review["verdict"] == "proved as written"
    reconciliation = review["fresh_release_gate_reconciliation"]
    assert reconciliation["status"] == "PASS"
    assert reconciliation["report_sha256"] == digest(report_path.read_bytes())
    inventory = json.loads((args.project / "inventory.json").read_text())
    assert digest((args.project / "inventory.json").read_bytes()) == report["inventory_sha256"]
    for group in ("modules", "control_support", "contracts"):
        for record in inventory[group]:
            assert digest((args.project / record["source"]).read_bytes()) == record["sha256"]

    release = "PRSC_IX_Complete_Parameter_Towers"
    previous_prefix = "PRSC_IX_Complete_Prescribed_Parameters/"
    replaced = {"README.md", "REMAINING_CHECKLIST.md", "MANIFEST.json",
                "RELEASE_AUDIT.json", "PACKAGE_COMPLETENESS.json"}
    files: dict[str, bytes] = {}
    coverage = []
    with zipfile.ZipFile(args.base) as base:
        assert base.testzip() is None
        for info in base.infolist():
            assert not info.is_dir() and info.filename.startswith(previous_prefix)
            relative = info.filename[len(previous_prefix):]
            assert ".." not in PurePosixPath(relative).parts and not relative.startswith("/")
            destination = ("historical/prescribed_parameters_release_root/" + relative
                           if relative in replaced else relative)
            assert destination not in files
            data = base.read(info)
            files[destination] = data
            coverage.append({"previous_path": relative, "current_path": destination,
                             "sha256": digest(data), "bytes": len(data)})
    assert len(coverage) == 1589

    for path in sorted(args.project.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(args.project)
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".olean", ".ilean"}:
            continue
        assert "verification" not in relative.parts
        files["polynomial_parameter_towers/" + relative.as_posix()] = path.read_bytes()
    for path in sorted(args.verification.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(args.verification)
        if "build" in relative.parts or "__pycache__" in relative.parts:
            continue
        files["polynomial_parameter_towers/verification/" + relative.as_posix()] = path.read_bytes()
    for name in ("README.md", "REMAINING_CHECKLIST.md"):
        files[name] = (args.docs / name).read_bytes()
    files["release_tools/assemble_parameter_towers.py"] = Path(__file__).read_bytes()
    updater = Path(__file__).with_name("update_docs.py")
    if updater.is_file():
        files["release_tools/update_parameter_tower_docs.py"] = updater.read_bytes()
    files["replay_paper9_parameter_towers.py"] = b'''#!/usr/bin/env python3
"""Replay the fresh prescribed-parameter tower gate with the separately supplied pinned kit."""
import argparse
from pathlib import Path
import subprocess
import sys
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--kit', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
script = Path(__file__).resolve().parent / 'polynomial_parameter_towers/scripts/verify_polynomial_parameter_towers.py'
raise SystemExit(subprocess.run([sys.executable, str(script), '--kit', str(args.kit.resolve()),
    '--output', str(args.output.resolve())]).returncode)
'''

    previous_modules = {record["module"] for record in json.loads(
        files["polynomial_prescribed/inventory.json"])["modules"]}
    assert len(previous_modules) == 39
    for module in previous_modules:
        assert files[f"polynomial_prescribed/formalization/{module}.lean"] == files[
            f"polynomial_parameter_towers/formalization/{module}.lean"]
    new_modules = [entry for entry in inventory["modules"] if entry["module"] not in previous_modules]
    new_declarations = Counter(item["kind"] for entry in new_modules for item in entry["declarations"])
    assert len(new_modules) == 6 and new_declarations == {"theorem": 24, "def": 1}

    files["PACKAGE_COMPLETENESS.json"] = json_bytes({
        "status": "PASS", "direct_previous_archive": args.base.name,
        "direct_previous_archive_sha256": expected_base_sha,
        "direct_previous_files": len(coverage), "files_preserved_by_content_hash": len(coverage),
        "scope": "Every file from the immediately preceding prescribed-parameter archive is retained exactly. Older coverage and recovery limitations retain their historical status.",
        "coverage": coverage})
    files["RELEASE_AUDIT.json"] = json_bytes({
        "release": release, "author": "Komorebi P.", "date": "2026-09-08", "status": "PASS",
        "target": "Compatible actual integer polynomial towers for every prescribed parameter path under initial solved-block surjectivity; arbitrary prescribed p-adic endpoints, all retained precisions, exact branching for every digit, and square-case uniqueness.",
        "main_theorem": "Komorebi.PolynomialPrescribedPadicTower.exists_prescribed_padic_root_with_tower",
        "new_mathematical_modules": len(new_modules), "new_declarations": dict(new_declarations),
        "fresh_mathematical_modules": report["module_count"],
        "inherited_mathematical_modules_unchanged": report["inherited_modules_preserved"],
        "fresh_checks": len(report["runs"]), "fresh_checks_passed": sum(r["passed"] for r in report["runs"]),
        "explicit_declaration_audits_including_controls_and_contracts": report["explicit_declaration_audits"],
        "declarations_including_controls_and_contracts": report["declarations"],
        "allowed_axioms": report["allowed_axioms"], "runtime": report["runtime"],
        "verification_report": "polynomial_parameter_towers/verification/polynomial_parameter_towers_verification.json",
        "verification_report_sha256": digest(report_path.read_bytes()),
        "inventory_sha256": report["inventory_sha256"],
        "independent_review_record_sha256": digest((args.project / "audit/REVIEWED_SOURCES.json").read_bytes()),
        "previous_archive_sha256": expected_base_sha, "previous_files_preserved": len(coverage),
        "first_order_motion": "Preserved Lean-certified theorem from previous release.",
        "prescribed_parameter_towers": "Lean-certified compatible integer towers for every prescribed path from initial solved-block surjectivity, actual p-adic endpoints for arbitrary allowed targets, all stage precisions, every-digit exact counts, square uniqueness.",
        "limitations": ["Earlier non-polynomial proofs are preserved with their historical verification, not recompiled in this gate.",
                        "General singular infinite towers without solved-block surjectivity are outside the new theorem.",
                        "Earlier rectangular chart interfaces retain their integer coefficients and integer centers.",
                        "No claim of analytic regularity, native presentation invariance, or global/completed descent."]})

    for item in coverage:
        assert digest(files[item["current_path"]]) == item["sha256"]
    manifest = {"release": release, "manifest_excludes_itself": True, "algorithm": "SHA-256",
                "file_count_excluding_manifest": len(files),
                "files": [{"path": name, "bytes": len(data), "sha256": digest(data)}
                          for name, data in sorted(files.items())]}
    files["MANIFEST.json"] = json_bytes(manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(files.items()):
            archive.writestr(release + "/" + name, data)
    with zipfile.ZipFile(args.output) as archive:
        assert archive.testzip() is None
        assert len(archive.infolist()) == len(files)
        for item in manifest["files"]:
            assert digest(archive.read(release + "/" + item["path"])) == item["sha256"]
        for item in coverage:
            assert digest(archive.read(release + "/" + item["current_path"])) == item["sha256"]
    print(json.dumps({"status": "PASS", "path": str(args.output.resolve()),
                      "files": len(files), "bytes": args.output.stat().st_size,
                      "sha256": digest(args.output.read_bytes()),
                      "prior_files_preserved": len(coverage)}, indent=2))


if __name__ == "__main__":
    main()
