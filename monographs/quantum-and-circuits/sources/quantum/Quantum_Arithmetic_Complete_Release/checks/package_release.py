#!/usr/bin/env python3
"""Assemble the source/evidence release after file and layout verification."""
from pathlib import Path
import hashlib
import json
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads((ROOT / p).read_text())
proofs = read("verification/RELEASE_CHECKS.json")
assert proofs["status"] == "PASS"
render = read("verification/RENDER_REPORT.json")
assert render["status"] == "PASS" and all(r["pages"] == r["rendered_pages"] and not r["empty_text_pages"] for r in render["documents"])

reviews = [
    ("reviews/TRADITIONAL_LAYOUT_REVIEW.json", "sha256", "traditional"),
    ("verification/VISUAL_LAYOUT_REVIEW.json", "sha256", "visual"),
    ("reviews/LEAN_LAYOUT_QA_FINAL.json", "pdf_sha256", "lean"),
]
by_kind = {d["document"]: d for d in proofs["documents"]}
for path, key, kind in reviews:
    r = read(path)
    assert r["status"] == "PASS" and r[key] == by_kind[kind]["sha256"], (path, kind)

identities = {
    "Komorebi_Quantum_Arithmetic_Lean_v0.2.0_Checked(1).zip": ("libfile_461f93b339888191bfac5bb03bab2fa0", "Authoritative later five-module, 96-theorem fixed-example checkpoint; archived execution evidence."),
    "Komorebi_Quantum_Arithmetic_Lean_v0.2.0_CHECKED.zip": ("libfile_0312d2fc49fc8191a13f61c727ca74c2", "Earlier overlapping four-module, 59-theorem checkpoint with its own proof boundary and controls."),
    "Komorebi_Quantum_Arithmetic_Lean_Verification.md": ("libfile_40f97689d03c81918ace6669417fbad8", "Earlier verification report; not the later formal receipt."),
    "Komorebi_Quantum_Arithmetic_Lean_Build_Log.txt": ("libfile_cbff9d1a46208191b878c752ce51076a", "Earlier archived compiler log; no new execution."),
    "Komorebi_Quantum_Arithmetic_Reproducibility.zip": ("libfile_7788450f2a74819194b9146ea0eab50d", "Original exact worked-example source, verifier, and scientific assets."),
    "Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.pdf": ("libfile_f9e5c7d99d2c8191bece3486786855c0", "Authenticated internal lineage; Proposition21.11 and Boundary21.12, printed pp189–190."),
    "block17_quantum_gauge_repair.patch": ("libfile_92b4b0c951c08191a9705984b5945105", "Related numerical QEC error-span repair; separate subsystem, not applied to this exact Fourier bridge."),
}
inventory = []
for p in sorted((ROOT / "downloads").rglob("*")):
    if p.is_file():
        identity, scope = identities[p.name]
        inventory.append({"path": str(p.relative_to(ROOT)), "original_file_identity": identity, "bytes": p.stat().st_size, "sha256": sha(p), "classification": scope})
(ROOT / "provenance" / "INPUT_INVENTORY.json").write_text(json.dumps({"inputs": inventory, "interpretation": "Identities and hashes authenticate the retrieved source revision; they do not substitute for mathematical proof."}, indent=2) + "\n")

status = {
    "title": "Quantum–Arithmetic Bridge: Projectors, Fourier Packets, and Unitary Realization",
    "author": "Komorebi P.", "version": "1.0.0", "publication_date": "2026-10-06", "publication_timezone": "America/Chicago",
    "assembled_at_utc": datetime.now(timezone.utc).isoformat(),
    "publication_status": "COMPLETE", "completed_scope": "General finite prose derivations and the fully explicit fixed q=12 arithmetic-to-signal-to-complex-state bridge.",
    "documents": proofs["documents"], "main_claims_independently_audited": 20,
    "scientific_figures": 20, "formal_checkpoint_named_theorems": 96,
    "formal_execution": {"archived_status": "PASS", "archived_date": "2026-09-21", "current_status": "NOT_RUN", "current_blocker": "Three pinned-runtime transfers failed HTTP502; no runtime bytes or Lean process.", "current_static_checks": "96 unique declaration locations and 16 source/log hash matches."},
    "current_exact_computation": {"source_assertions": 3003, "release_assertions": 5374, "numeric_tolerance": 1e-12, "largest_new_numeric_residual": 6.764165321960921e-15, "evidence": "verification/visual_release_run_v2/"},
    "resolved_findings": ["Six-point and doubled twelve-point Fourier tables distinguished.", "Ideal Lüders instrument specified for conditional state updates.", "Index sets distinguished from identity matrices.", "LuaLaTeX font dependency unavailable; XeLaTeX final builds pass.", "Preview renders serialized and staged after truncated draft image reads.", "Scientific plot labels, lane spacing, visual overflow, and proof/table page breaks corrected."],
    "remaining_separate_work": ["Fresh pinned Lean replay once runtime transfer succeeds.", "Arbitrary-modulus Lean formalization, beyond the inherited fixed example.", "Efficient preparation, gate synthesis, physical implementation, and resource bounds."],
    "proof_boundaries": ["Finite computations are not universal proofs.", "Phase-family and dephased-state extensions are prose results, not new inherited Lean declarations.", "No general quantum advantage or deterministic projector denoising is claimed."]
}
(ROOT / "RELEASE_STATUS.json").write_text(json.dumps(status, indent=2) + "\n")

archive_path = ROOT / "output" / "Komorebi_Quantum_Arithmetic_Complete_Release_2026-10-06.zip"
excluded_suffixes = {".aux", ".out", ".toc", ".synctex", ".pyc"}
def included(p):
    rel = p.relative_to(ROOT)
    if any(part in {".library_helpers", "preview", "__pycache__"} or part.startswith(".") for part in rel.parts):
        return False
    if p == archive_path or p.suffix in excluded_suffixes:
        return False
    if rel.parts[:2] == ("verification", "document_build") and p.suffix not in {".txt", ".log", ".json", ".md"}:
        return False
    return p.is_file()

files = sorted(p for p in ROOT.rglob("*") if included(p) and p != ROOT / "provenance" / "RELEASE_FILES.json")
entries = [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha(p)} for p in files]
manifest_path = ROOT / "provenance" / "RELEASE_FILES.json"
manifest_path.write_text(json.dumps({"schema_version": 1, "files": entries, "self_hash_excluded": True}, indent=2) + "\n")
files.append(manifest_path)
with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(files):
        z.write(p, arcname="Quantum_Arithmetic_Complete_Release/" + str(p.relative_to(ROOT)))
with zipfile.ZipFile(archive_path) as z:
    assert z.testzip() is None
    for entry in entries:
        content = z.read("Quantum_Arithmetic_Complete_Release/" + entry["path"])
        assert hashlib.sha256(content).hexdigest() == entry["sha256"]
print(json.dumps({"status": "PASS", "archive": str(archive_path), "members": len(files), "bytes": archive_path.stat().st_size, "sha256": sha(archive_path), "documents": [{"kind": r["document"], "pages": r["pages"]} for r in proofs["documents"]]}, indent=2))
