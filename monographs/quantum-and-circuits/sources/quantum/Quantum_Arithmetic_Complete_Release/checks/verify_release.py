#!/usr/bin/env python3
"""Verify release-file consistency. This does not verify new Lean proof terms."""
from pathlib import Path
import hashlib
import json
import zipfile
from datetime import datetime, timezone
import fitz

ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    return json.loads((ROOT / path).read_text())

checks = []
def require(name, condition):
    checks.append({"check": name, "passed": bool(condition)})
    if not condition:
        raise AssertionError(name)

concordance = read("lean/Lean_Concordance.json")
theorems = concordance["theorems"]
require("96 unique active theorem declarations", len(theorems) == 96 and len({r["name"] for r in theorems}) == 96)
require("module counts total 96", sum(concordance["module_theorem_counts"].values()) == 96)
require("20 manuscript claim contracts", {r["claim_id"] for r in concordance["manuscript_claim_concordance"]} == {f"QA{i:02}" for i in range(1,21)})
require("all sixteen recorded source/log hashes reconciled", len(concordance["hash_reconciliation"]) == 16 and all(r["matches_archived_report"] for r in concordance["hash_reconciliation"]))
for module in concordance["module_theorem_counts"]:
    rows = [r for r in theorems if r["module"] == module]
    source = ROOT / "lean" / "checked_checkpoint" / f"{module}.lean"
    require(f"active source hash: {module}", all(r["source_sha256"] == sha(source) for r in rows))
    lines = source.read_text().splitlines()
    require(f"declaration line locations: {module}", all(f"theorem {r['basename']}" in lines[r["source_line"] - 1] for r in rows))
require("standard archived axiom union", set(concordance["axiom_union"]) == {"propext", "Classical.choice", "Quot.sound"})

fresh = read("lean/FRESH_LEAN_STATUS.json")
require("fresh Lean status remains honestly NOT_RUN", fresh["status"] == "NOT_RUN" and not fresh["fresh_lean_build"] and not fresh["fresh_kernel_replay"])
result = read("verification/visual_release_run_v2/visual_results.json")
require("exact source replay passed 3003 assertions", result["status"] == "PASS" and result["source_verifier"]["exact_assertion_count"] == 3003)
require("exact release replay passed 5374 assertions", result["new_exact_assertion_count"] == 5374)
require("20 figures and 60 final assets", result["figure_count"] == 20 and len(result["assets"]) == 60)
for filename, record in result["assets"].items():
    require(f"figure hash: {filename}", sha(ROOT / filename) == record["sha256"])
run = read("verification/visual_release_run_v2/manifest.json")
require("bounded computation manifest passed", run["run"]["status"] == "completed" and run["run"]["exit_status"] == 0 and all(r["passed"] for r in run["checks"]))
for record in run["input_artifacts"]:
    require(f"bounded input hash: {record['path']}", sha(ROOT / record["path"]) == record["sha256"] == record["sha256_after"])

build = read("verification/document_build/BUILD_REPORT.json")
require("all three document builds recorded", len(build["documents"]) == 3 and build["status"] == "PASS")
documents = []
for record in build["documents"]:
    path = ROOT / record["file"]
    require(f"PDF hash: {record['document']}", sha(path) == record["sha256"])
    require(f"clean final typesetting log: {record['document']}", not record["warnings"])
    doc = fitz.open(path)
    require(f"nonempty publication pages: {record['document']}", all(len(p.get_text().strip()) > 20 for p in doc))
    require(f"no unresolved reference text: {record['document']}", all("??" not in p.get_text() for p in doc))
    documents.append({"document": record["document"], "file": record["file"], "pages": len(doc), "bytes": path.stat().st_size, "sha256": sha(path)})

archives = []
for path in sorted((ROOT / "downloads").rglob("*.zip")):
    with zipfile.ZipFile(path) as archive:
        require(f"input archive CRC: {path.name}", archive.testzip() is None)
        archives.append({"path": str(path.relative_to(ROOT)), "members": len(archive.namelist()), "sha256": sha(path)})
report = {"status": "PASS", "checked_at_utc": datetime.now(timezone.utc).isoformat(), "check_count": len(checks), "checks": checks, "documents": documents, "input_archives": archives, "scope": "File, declaration, hash, bounded-result, and publication consistency; no fresh Lean compiler or kernel execution."}
(ROOT / "verification" / "RELEASE_CHECKS.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"status": report["status"], "checks": len(checks), "documents": documents}, indent=2))
