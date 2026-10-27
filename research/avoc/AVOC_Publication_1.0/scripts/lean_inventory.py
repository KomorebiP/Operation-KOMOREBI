#!/usr/bin/env python3
"""Fresh read-only AVOC source/receipt inventory. This does not run Lean.

The release's exact qualified-name inventory is retained as provenance and
checked against the declaration at each recorded source line. SHA-256 receipts
are checked against actual source bytes. No lexical check is a kernel proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    default = Path(__file__).resolve().parents[1] / "source" / "AVOC_Formal_v0.41.0"
    ap.add_argument("--source", type=Path, default=default)
    ap.add_argument("--output", type=Path,
                    default=Path(__file__).resolve().parents[1] / "reviews" / "lean_inventory.json")
    args = ap.parse_args()
    source = args.source.resolve()
    evidence = source / "results" / "v0.41.0"
    inventory_file = evidence / "declaration_inventory.json"
    counts_file = evidence / "source_counts.json"
    decls = json.loads(inventory_file.read_text())
    counts = json.loads(counts_file.read_text())
    audit = json.loads((source / "AUDIT.json").read_text())
    axiom = json.loads((evidence / "axiom_audit_summary.json").read_text())
    progress = json.loads((evidence / "build_progress.json").read_text())
    release = json.loads((evidence / "release_verification.json").read_text())
    negative = json.loads((evidence / "negative_all" / "summary.json").read_text())
    errors = []
    names = [d["qualified_name"] for d in decls]
    if len(names) != len(set(names)):
        errors.append("Duplicate qualified names in archived inventory")
    if len(decls) != audit["theorem_declarations"]:
        errors.append("Archived declaration count mismatch")
    modules = []
    module_decl_count = Counter(d["module"] for d in decls)
    # FullAudit/Audit are reporting targets rather than mathematical modules.
    source_files = sorted(p for p in (source / "AVOC").glob("*.lean")
                          if p.name not in {"Audit.lean", "FullAudit.lean"})
    for file in source_files:
        rel = file.relative_to(source).as_posix()
        content = file.read_text()
        imports = re.findall(r"^import\s+(\S+)", content, re.M)
        digest = sha256(file)
        expected = counts["source_sha256"].get(rel)
        if expected is not None and digest != expected:
            errors.append(f"Source digest mismatch: {rel}")
        modules.append({"path": rel, "sha256": digest,
                        "lines": len(content.splitlines()),
                        "archived_named_declarations": module_decl_count[rel],
                        "imports": imports,
                        "archived_source_digest_matches": digest == expected if expected else None})
    checked_decls = []
    for d in decls:
        file = source / d["module"]
        lines = file.read_text().splitlines()
        start = d["line"] - 1
        actual = lines[start] if 0 <= start < len(lines) else ""
        pattern = r"\b" + re.escape(d["kind"]) + r"\s+" + re.escape(d["name"]) + r"(?:\s|\{|\(|:|$)"
        ok = re.search(pattern, actual) is not None
        if not ok:
            errors.append(f"Recorded source line does not declare {d['qualified_name']}")
        statement = "\n".join(lines[start:]).split("\n\n", 1)[0]
        # This is an excerpt terminator, not a Lean parser or elaborator.
        proof_start = re.search(r":=\s*by\b", statement)
        stop = proof_start.start() if proof_start else statement.find(":=")
        if stop >= 0:
            statement = statement[:stop].rstrip()
        else:
            statement = statement.split("\n\n", 1)[0]
        checked_decls.append({**d, "recorded_line_matches": ok,
                              "statement_excerpt": statement,
                              "source_sha256": sha256(file)})
    for label, condition in [
        ("195 non-audit modules", len(modules) == audit["non_audit_modules"]),
        ("axiom inventory digest", sha256(inventory_file) == axiom["inventory_sha256"]),
        ("archived reports", axiom["reports"] == len(decls) and axiom["passed"]),
        ("archived 222 builds", progress["passed"] == audit["local_targets"] and progress["complete"]),
        ("archived 135 negative rejections", negative["substantive_rejections"] == audit["negative_rejections"] and negative["complete"]),
        ("archived final release status", release["passed"] and not release["errors"]),
    ]:
        if not condition:
            errors.append(f"Mismatch: {label}")
    result = {
        "schema": "avoc-publication-lean-source-inventory-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source), "status": "PASS" if not errors else "FAIL",
        "fresh_check_scope": "Source bytes, recorded declaration lines, module/import inventory, and archived receipt consistency only",
        "fresh_kernel_compilation": "NOT_RUN_HERE",
        "fresh_axiom_print_execution": "NOT_RUN_HERE",
        "fresh_actual_lean_oracle": "NOT_RUN_HERE",
        "counts": {"non_audit_mathematical_modules": len(modules),
                   "named_declarations": len(decls),
                   "modules_with_named_declarations": len(module_decl_count),
                   "modules_with_pinned_declaration_source_digests": len(counts["source_sha256"]),
                   "private_named_declarations": sum(bool(d["private"]) for d in decls)},
        "archived_evidence": {
            "version": audit["version"], "clean_targets_passed": progress["passed"],
            "named_axiom_reports": axiom["reports"], "axiom_union": axiom["axiom_union"],
            "substantive_negative_rejections": negative["substantive_rejections"],
            "actual_lean_oracle_words": audit["recorder_actual_lean_words"],
            "python_reference_oracle_words": audit["recorder_python_oracle_words"],
            "lean_commit": audit["lean_commit"], "mathlib_commit": audit["mathlib"],
            "evidence_sha256": {f.relative_to(source).as_posix(): sha256(f) for f in
                [source / "AUDIT.json", inventory_file, counts_file, evidence / "axiom_audit_summary.json",
                 evidence / "build_progress.json", evidence / "release_verification.json",
                 evidence / "negative_all" / "summary.json"]}},
        "errors": errors, "modules": modules, "declarations": checked_decls,
        "limitations": ["No universal lexical-parser claim", "No fresh kernel or runtime execution",
                        "Archived evidence remains archived evidence", "Module counts are not counts of independent discoveries"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"],
                      "errors": errors, "output": str(args.output),
                      "fresh_kernel_compilation": result["fresh_kernel_compilation"]}, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
