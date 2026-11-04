#!/usr/bin/env python3
"""Check that the published Lean-companion receipts still match their sources.

This is a source/evidence consistency check. It does not run Lean.
"""
import json
from pathlib import Path

from verify_lean_companion import ALLOWED_AXIOMS, sha256, source_inventory

PROJECTS = ("formal/reader-examples", "formal/kcos-certification")
RECORD = "verification/2026-11-04/run.json"


def check_project(root, relative):
    project = root / relative
    config = json.loads((project / "verification.json").read_text())
    source_inventory(project, config)
    report = json.loads((project / RECORD).read_text())
    if report["status"] != "PASS":
        raise ValueError("Recorded Lean run did not pass: " + relative)
    if report["verifier_sha256"] != sha256(root / "tools/verify_lean_companion.py"):
        raise ValueError("Verifier changed after the recorded run: " + relative)
    for path, expected in report["source_sha256"].items():
        if sha256(project / path) != expected:
            raise ValueError("Source changed after the recorded run: " + relative + "/" + path)
    expected_sources = {"lakefile.toml", "lake-manifest.json", "lean-toolchain",
                        "verification.json", "CLAIM_MAP.json", config["library"] + ".lean",
                        *config["production"], *config.get("support_sources", []),
                        *[c["path"] for c in config["positive_controls"]],
                        *[c["path"] for c in config["negative_controls"]]}
    if set(report["source_sha256"]) != expected_sources:
        raise ValueError("Recorded source list differs from the configured project: " + relative)
    checks = report["checks"]
    names = {row["name"] for row in checks}
    required = {"compiler", "lake", "strict_build", "production_axioms", "project_kernel_replay",
                "positive_control_axioms", *[Path(c["path"]).stem for c in config["positive_controls"]],
                *[Path(c["path"]).stem for c in config["negative_controls"]]}
    if (not required <= names or len(names) != len(checks)
            or not all(row["passed"] for row in checks)):
        raise ValueError("Required replay gates are absent or failed: " + relative)
    for check in checks:
        if sha256(project / Path(RECORD).parent / check["log"]) != check["log_sha256"]:
            raise ValueError("Compiler evidence changed: " + relative + "/" + check["log"])
    expected_names = {row["name"] for row in config["declarations"]}
    if (len(report["axioms"]) != len(expected_names)
            or {row["name"] for row in report["axioms"]} != expected_names):
        raise ValueError("Axiom audit does not cover the exact declaration inventory")
    for field in ("axioms", "positive_control_axioms", "retained_prerequisite_axioms"):
        if any(set(row["axioms"]) - ALLOWED_AXIOMS for row in report.get(field, [])):
            raise ValueError("Unexpected recorded axiom dependency: " + relative)
    if report["negative_controls_rejected"] != len(config["negative_controls"]):
        raise ValueError("Incorrect rejection count")
    if report["audited_declarations"] != len(expected_names):
        raise ValueError("Incorrect declaration count")
    for binding in report.get("retained_prerequisites", []):
        if sha256(root / binding["source"]) != binding["sha256"]:
            raise ValueError("Retained prerequisite no longer matches its stated original")
    return {"project": config["library"], "theorem_declarations": report["theorem_count"],
            "audited_declarations": report["audited_declarations"],
            "rejected_controls": report["negative_controls_rejected"],
            "status": "PASS", "new_lean_execution": False}


def main():
    root = Path(__file__).resolve().parents[1]
    results = [check_project(root, relative) for relative in PROJECTS]
    print(json.dumps({"status": "PASS", "projects": results}, indent=2))


if __name__ == "__main__":
    main()
