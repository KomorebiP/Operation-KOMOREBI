"""Pin final evidence and build the distributable archive.

This checks audit provenance, not the proofs' mathematical correctness.
"""
import hashlib
import json
import platform
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parent
    computation_root = root / "computation"
    for directory in ("run512", "supplemental96", "paired96"):
        subprocess.run(
            [sys.executable, "validate_manifest.py",
             f"{directory}/manifest.json", "--root", "."],
            cwd=computation_root, check=True
        )
    audited = [
        ("review/GLOBAL_PROOF_AUDIT.md",
         "combinatorial/THRESHOLD_FREE_EIGENFLAT_PROOF.md"),
        ("review/SHARP_PERIOD_AUDIT.md",
         "sharp_periods/SHARP_PERIOD_LEMMA.md"),
        ("review/PRIME_POWER_AUDIT.md", "GENERAL_PRIME_POWER_TRANSFER.md"),
        ("review/FACTORIAL_AUDIT.md",
         "combinatorial/factorial_j2/FACTORIAL_J2_PROOF.md"),
        ("review/FACTORIAL_ROUTE_AUDIT.md", "measure/factorial_route.md"),
        ("review/FACTORIAL_ROUTE_CRITICAL_AUDIT.md",
         "measure/factorial_route.md"),
    ]
    dependencies = []
    for audit_name, proof_name in audited:
        audit, proof = root / audit_name, root / proof_name
        proof_sha = sha(proof)
        if proof_sha not in audit.read_text():
            raise SystemExit(f"Audit does not pin final proof: {audit_name}")
        dependencies.append({
            "audit": audit_name, "proof": proof_name, "proof_sha256": proof_sha
        })
    files = sorted(
        p for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
        and p.suffix != ".pyc" and p.name != "CHECKPOINT_MANIFEST.json"
    )
    manifest = {
        "checkpoint": "Euler threshold-free strengthening",
        "date": "2026-10-06",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "scope": "All-row congruences, exact stated valuations, periods, "
                 "and analytic radii; no new Lean compilation.",
        "audit_dependencies": dependencies,
        "computation_manifests_validated": [
            "computation/run512/manifest.json",
            "computation/supplemental96/manifest.json",
            "computation/paired96/manifest.json",
        ],
        "files": [
            {"path": str(p.relative_to(root)), "bytes": p.stat().st_size,
             "sha256": sha(p)}
            for p in files
        ],
    }
    manifest_path = root / "CHECKPOINT_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    subprocess.run([sys.executable, str(root / "verify_checkpoint.py")],
                   check=True)
    output = root.parent / "Euler_Threshold_Free_Strengthening_2026-10-06.zip"
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as archive:
        for path in files + [manifest_path]:
            archive.write(path, str(Path(root.name) / path.relative_to(root)))
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise SystemExit(f"Corrupt archive member: {bad}")
    print(json.dumps({
        "archive": str(output), "bytes": output.stat().st_size,
        "sha256": sha(output), "pinned_files": len(files)
    }))


if __name__ == "__main__":
    main()
