"""Run deterministic release checks with no third-party dependencies."""

from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import sys
import unittest

from osl_discovery import emit_osl, synthesize, verify_certificate, verify_registry
from osl_discovery.worlds import canonical_json


ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"
GENERATED = ROOT / "generated"
EXCLUDED_FILES = {"SHA256SUMS.txt"}
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_manifest() -> dict:
    manifest = ROOT / "SHA256SUMS.txt"
    if not manifest.exists():
        return {"valid": False, "entry_count": 0, "errors": ["SHA256SUMS.txt is missing"]}
    expected_paths = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.name not in EXCLUDED_FILES
        and path.suffix != ".pyc"
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
    }
    entries = {}
    errors = []
    for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            digest, relative = line.split("  ", 1)
        except ValueError:
            errors.append(f"malformed manifest line {line_number}")
            continue
        if relative in entries:
            errors.append(f"duplicate manifest path {relative}")
        entries[relative] = digest
    if set(entries) != expected_paths:
        errors.append("manifest file set does not match the release file set")
    for relative, expected_digest in entries.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing file {relative}")
        elif sha256(path.read_bytes()).hexdigest() != expected_digest:
            errors.append(f"digest mismatch for {relative}")
    return {"valid": not errors, "entry_count": len(entries), "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osl-core", help="path to the OSL-Core 0.3 reference directory")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)
    if args.osl_core:
        os.environ["OSL_CORE_REFERENCE"] = str(Path(args.osl_core).resolve())

    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)

    artifact_checks = {}
    mapping = {
        "flip_both": "flip_both_proposal.json",
        "ambiguous": "ambiguous_proposal.json",
        "inconsistent": "inconsistent_proposal.json",
    }
    for stem, proposal_name in mapping.items():
        proposal = load(EXAMPLES / proposal_name)
        certificate = load(GENERATED / f"{stem}_certificate.json")
        decision_name = {
            "admit": "admission",
            "quarantine": "quarantine",
            "reject": "rejection",
        }[certificate["decision"]]
        osl_path = GENERATED / f"{stem}_{decision_name}.osl"
        artifact_checks[stem] = {
            "certificate_valid": verify_certificate(proposal, certificate)["valid"],
            "certificate_matches_regeneration": certificate == synthesize(proposal),
            "osl_matches_regeneration": osl_path.read_text(encoding="utf-8") == emit_osl(proposal, certificate),
        }

    generation_report = load(GENERATED / "GENERATION_REPORT.json")
    expected_tip = generation_report["registry"]["tip_digest"]
    registry = verify_registry(GENERATED / "OPERATOR_REGISTRY.jsonl", expected_tip=expected_tip)
    manifest = verify_manifest()
    artifacts_valid = (
        all(all(case.values()) for case in artifact_checks.values())
        and registry["valid"]
        and manifest["valid"]
    )
    all_valid = result.wasSuccessful() and artifacts_valid
    report = {
        "schema": "osl.discovery.release-verification.v1",
        "release": "OSL Discovery Bridge v0.1.0",
        "canonical_upstream": "OSL v0.5 / OSL-Core 0.3",
        "all_checks_pass": all_valid,
        "tests": {
            "run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "osl_core_integration_enabled": bool(args.osl_core),
        },
        "generated_artifacts": artifact_checks,
        "manifest": manifest,
        "registry": registry,
        "claim_boundary": (
            "Exact bounded finite-world discovery and deterministic replay; "
            "not open-world, neural-internal, or proof-assistant verification."
        ),
    }
    if args.write_report:
        (ROOT / "VERIFICATION_REPORT.json").write_text(
            canonical_json(report) + "\n", encoding="utf-8", newline="\n"
        )
    print(json.dumps(report, indent=2, sort_keys=True))
    if not all_valid:
        print(stream.getvalue(), file=sys.stderr)
    return 0 if all_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
