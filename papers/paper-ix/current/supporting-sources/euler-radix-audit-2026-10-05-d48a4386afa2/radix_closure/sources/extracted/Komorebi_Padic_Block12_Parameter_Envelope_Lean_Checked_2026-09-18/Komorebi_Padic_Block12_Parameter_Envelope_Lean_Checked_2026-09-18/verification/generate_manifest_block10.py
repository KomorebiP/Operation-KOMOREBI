#!/usr/bin/env python3
"""Generate Block 10 computation manifest, file listing, and checksum ledger."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def files_excluding(excluded: set[str]) -> list[Path]:
    paths: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".lake" in path.parts:
            continue
        rel = str(path.relative_to(ROOT))
        if rel in excluded:
            continue
        paths.append(path)
    return sorted(paths)


def main() -> None:
    source = load("results/static_source_audit_block10.json")
    axioms = load("results/axiom_audit_block10.json")
    controls = load("results/kernel_controls_block10.json")
    vectors = load("results/lean_vector_replay_block10.json")
    build = load("results/BUILD_VERIFICATION_BLOCK10.json")
    radix = load("results/radix_compiler_audit.json")
    suffix = load("results/suffix_window_audit.json")
    boundary = load("results/final_fiber_boundary_audit.json")
    complexity = load("results/compiler_complexity_audit.json")
    closed = load("results/representative_budget_closed_form_audit.json")

    finite_total = (
        int(radix["total_checks"])
        + int(suffix["total_recorded_checks"])
        + int(boundary["total_recorded_checks_and_cases"])
        + int(complexity["total_recorded_checks_and_cases"])
        + int(closed["total_recorded_checks_and_cases"])
    )

    excluded_from_manifest_hashes = {
        "COMPUTATION_MANIFEST.json", "COMPUTATION_MANIFEST.sha256",
        "CHECKSUMS.sha256", "FOCUSED_MANIFEST.txt",
        "results/FOCUSED_RELEASE_VERIFICATION.json",
        "logs/generate_manifest_block10.log", "logs/verify_release_block10.log",
        "logs/checksum_verify_block10.log",
    }
    hash_paths = files_excluding(excluded_from_manifest_hashes)
    hashes = {str(path.relative_to(ROOT)): sha256(path) for path in hash_paths}

    manifest = {
        "schema": "komorebi-padic-block10-computation-manifest-v1",
        "block": "Komorebi_Padic_Representative_Budget_Closed_Form_Block10",
        "status": "PASS",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "claim_contract": {
            "universal_claims": [
                "For all natural p and B, radixRepresentativeBudget p B equals B + p*d*(d-1)/2 + d*(s+1), where d=(B-1)/p and s=(B-1)%p.",
                "The formula includes the totalized natural-number cases B=0, p=0, and p=1.",
                "The Block 09 finite-sum compiler envelope equals the Block 10 closed envelope.",
                "At prime p and positive r, the exact total compiler count is bounded by the closed envelope.",
                "The dependent closed-form certificate retains exact executable data and proofs of the decomposition and bound.",
            ],
            "hypotheses": [
                "No hypothesis for the representative-budget formula.",
                "p.Prime and 0 < r for the end-to-end compiler total bound and certificate.",
            ],
            "arithmetic_domain": "Lean natural numbers and Python arbitrary-precision integers",
            "timeout_policy": "Timeout is inconclusive.",
            "nonclaims": [
                "No wall-clock or memory-complexity theorem.",
                "No asymptotic optimality or tightness theorem.",
                "No end-to-end compiler theorem for composite bases.",
                "No stable Lean 4.34.0 compatibility claim.",
                "No novelty or priority claim.",
            ],
        },
        "lean": {
            "toolchain": "leanprover/lean4:v4.34.0-rc2",
            "lean_commit": "6a10ac8c22beadecabdbb0919c2b50214762f91d",
            "mathlib_revision": "aeb72f1e9981b6d35b426b16dca7759be3e7ba06",
            "warning_as_error_clean_build": build["clean_build"]["status"],
            "root_jobs": build["clean_build"]["jobs"],
            "production_files": source["lean_file_count"],
            "declaration_counts": source["declaration_counts"],
            "compiled_olean_ilean_artifacts": build["lean"]["compiled_olean_ilean_artifacts"],
            "native_decide_files": vectors["file_count"],
            "native_decide_examples": vectors["example_count"],
            "axiom_audit": axioms["status"],
            "axiom_audit_theorems": axioms["theorem_count"],
            "observed_axioms": axioms["observed_axioms"],
            "unexpected_axioms": axioms["unexpected_axioms"],
            "negative_controls": controls["status"],
            "predecessor_theorems": source["predecessor_theorem_count"],
            "new_theorems": len(source["added_theorems"]),
            "changed_predecessor_theorem_statements": len(source["changed_predecessor_theorem_statements"]),
        },
        "computation": {
            "block05_radix": {"status": radix["status"], "recorded_checks": radix["total_checks"]},
            "block06_suffix": {"status": suffix["status"], "recorded_checks": suffix["total_recorded_checks"], "failure_count": suffix["failure_count"]},
            "block08_boundary": {"status": boundary["status"], "recorded_checks_and_cases": boundary["total_recorded_checks_and_cases"], "failure_count": boundary["failure_count"]},
            "block09_complexity": {"status": complexity["status"], "recorded_checks_and_cases": complexity["total_recorded_checks_and_cases"], "failure_count": complexity["failure_count"]},
            "block10_closed_form": {
                "status": closed["status"],
                "recorded_checks_and_cases": closed["total_recorded_checks_and_cases"],
                "failure_count": closed["failure_count"],
                "parameters": closed["parameters"],
                "maxima": closed["maxima"],
                "compiler_stress_records": closed["compiler_stress_records"],
            },
            "combined_recorded_checks_and_cases": finite_total,
        },
        "runtime_archive": {
            "sha256": "f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7",
            "status": "HASH_VERIFIED_AND_EXTRACTED",
            "standalone_xz_test": "INCONCLUSIVE_TIMEOUT",
        },
        "inconclusive_or_corrected_attempts": build["inconclusive_or_corrected_attempts"],
        "sha256": hashes,
    }
    manifest_path = ROOT / "COMPUTATION_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "COMPUTATION_MANIFEST.sha256").write_text(
        f"{sha256(manifest_path)}  {manifest_path.name}\n", encoding="utf-8"
    )

    listing_excluded = {"FOCUSED_MANIFEST.txt", "CHECKSUMS.sha256", "results/FOCUSED_RELEASE_VERIFICATION.json", "logs/generate_manifest_block10.log", "logs/verify_release_block10.log", "logs/checksum_verify_block10.log"}
    listing = files_excluding(listing_excluded)
    (ROOT / "FOCUSED_MANIFEST.txt").write_text(
        "\n".join(str(path.relative_to(ROOT)) for path in listing) + "\n", encoding="utf-8"
    )

    checksum_excluded = {"CHECKSUMS.sha256", "results/FOCUSED_RELEASE_VERIFICATION.json", "logs/generate_manifest_block10.log", "logs/verify_release_block10.log", "logs/checksum_verify_block10.log"}
    checksum_paths = files_excluding(checksum_excluded)
    (ROOT / "CHECKSUMS.sha256").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(ROOT)}\n" for path in checksum_paths),
        encoding="utf-8",
    )
    print(json.dumps({
        "manifest_hashed_files": len(hashes),
        "manifest_sha256": sha256(manifest_path),
        "listed_files": len(listing),
        "checksum_entries": len(checksum_paths),
        "combined_finite": finite_total,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
