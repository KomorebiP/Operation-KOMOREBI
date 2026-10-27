#!/usr/bin/env python3
"""Read-only source, archived receipt, axiom and publication-excerpt inventory.

This performs no Lean compilation and never rewrites the archived evidence.
"""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "source/FD_Certified_Inference_Core_v1.0.0_Checked"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=ROOT / "reviews/lean_inventory.json")
    args = parser.parse_args()
    source = args.source.resolve()
    failures = []

    def check(ok, message):
        if not ok:
            failures.append(message)

    seal = json.loads((source / "FINAL_VERIFICATION_RECEIPT.json").read_text())
    order = json.loads((source / "MODULE_ORDER.json").read_text())
    declarations = json.loads((source / "DECLARATIONS.json").read_text())
    audit = json.loads((source / "AXIOM_AUDIT.json").read_text())
    receipt_map = {x["module"]: x for x in seal["successful_final_modules"]}
    check(len(order) == len(set(order)) == 117, "module order is not 117 unique modules")
    check(set(order) == set(receipt_map), "module order/final-receipt coverage differs")
    check(len(declarations) == 543, "declaration inventory is not 543 entries")
    check(len({d["name"] for d in declarations}) == 543, "duplicate audited names")
    parsed_declarations = set()
    for path in (source / "Komorebi").glob("*.lean"):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            match = re.search(r"^\s*(?:@\[[^]]+\]\s*)?(?:private\s+)?(?:theorem|lemma)\s+(\S+)", line)
            if match:
                parsed_declarations.add((path.stem, number, match.group(1)))
    check(parsed_declarations == {(d["module"], d["line"], d["name"].split(".")[-1]) for d in declarations},
          "independently parsed theorem/lemma inventory differs")
    check({d["name"] for d in declarations} == {d["name"] for d in audit["declarations"]},
          "declaration/axiom-audit coverage differs")
    allowlist = {"propext", "Classical.choice", "Quot.sound"}
    check(set(audit["allowed_axioms"]) == allowlist, "axiom allowlist differs")

    manifest_checked = 0
    for line in (source / "MANIFEST_SHA256.txt").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        path = source / relative
        check(path.is_file() and sha(path) == expected, "manifest mismatch: " + relative)
        manifest_checked += 1

    modules = []
    dependency_checks = 0
    for name in order:
        path = source / "Komorebi" / (name + ".lean")
        digest = sha(path)
        receipt = receipt_map[name]
        raw_receipt = json.loads((source / receipt["receipt_path"]).read_text())
        check({k: v for k, v in receipt.items() if k != "receipt_path"} == raw_receipt,
              "sealed/raw receipt differs: " + name)
        check(receipt["exit_status"] == 0, "nonzero archived final exit: " + name)
        for field in ("source_sha256_before", "source_sha256_after", "staged_source_sha256"):
            check(receipt[field] == digest, "source hash differs: " + name + ":" + field)
        receipt_dir = (source / receipt["receipt_path"]).parent
        check(sha(receipt_dir / (name + ".lean")) == digest,
              "attempt-source snapshot differs: " + name)
        check(sha(receipt_dir / (name + ".log")) == receipt["log_sha256"],
              "archived log differs: " + name)
        imports = re.findall(r"^import Komorebi\.([A-Za-z0-9_]+)$", path.read_text(), re.M)
        check(set(receipt["dependencies"]) == {"Komorebi." + x for x in imports},
              "direct project import coverage differs: " + name)
        for dep, evidence in receipt["dependencies"].items():
            dep_name = dep.removeprefix("Komorebi.")
            check(sha(source / "Komorebi" / (dep_name + ".lean")) == evidence["source_sha256"],
                  "dependency source differs: " + name + " -> " + dep_name)
            check(receipt_map[dep_name]["output_sha256"] == evidence["olean_sha256"],
                  "recorded dependency output differs: " + name + " -> " + dep_name)
            dependency_checks += 1
        count = sum(d["module"] == name for d in declarations)
        modules.append({"module": name, "source_sha256": digest, "theorems_lemmas": count,
                        "direct_project_imports": imports, "receipt": receipt["receipt_path"]})

    union = set()
    for d in audit["declarations"]:
        path = source / "Komorebi" / (d["module"] + ".lean")
        lines = path.read_text().splitlines()
        token = d["name"].split(".")[-1]
        line = lines[d["line"] - 1]
        check(re.search(r"\b(?:theorem|lemma)\s+" + re.escape(token) + r"\b", line) is not None,
              "declaration line differs: " + d["name"])
        check(d["source_sha256"] == sha(path), "axiom source hash differs: " + d["name"])
        check(set(d["axioms"]) <= allowlist, "unexpected axiom: " + d["name"])
        union.update(d["axioms"])

    manuscript = ROOT / "manuscripts/lean.tex"
    excerpts = []
    if manuscript.exists():
        tex = manuscript.read_text()
        pattern = r"^%% SOURCE_EXCERPT (\{[^\n]+\})\n\s*[^\n]*\n\s*\\begin\{lstlisting\}\[[^\n]*\]\n(.*?)\n\\end\{lstlisting\}"
        for metadata, actual in re.findall(pattern, tex, re.M | re.S):
            e = json.loads(metadata)
            path = source / e["file"]
            expected = "\n".join(path.read_text().splitlines()[e["first_line"] - 1:e["last_line"]])
            check(actual == expected, "publication excerpt differs: " + e["name"])
            check(hashlib.sha256(actual.encode()).hexdigest() == e["excerpt_sha256"],
                  "publication excerpt digest differs: " + e["name"])
            excerpts.append(e)
        check(len(excerpts) == tex.count("%% SOURCE_EXCERPT "), "unparsed source excerpt")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "method": "Fresh read-only Python verification; no Lean compiler invoked",
        "source": str(source), "manifest_files_checked": manifest_checked,
        "active_modules": len(order), "named_theorem_lemma_declarations": len(declarations),
        "independently_parsed_theorem_lemma_declarations": len(parsed_declarations),
        "declarations_by_kind": dict(collections.Counter(d["kind"] for d in declarations)),
        "declarations_by_group": dict(collections.Counter(d["group"] for d in declarations)),
        "direct_project_dependency_records_checked": dependency_checks,
        "archived_kernel_builds": len(receipt_map), "archived_axiom_reports": len(audit["declarations"]),
        "axiom_union": sorted(union), "archived_environment": seal["environment"],
        "fresh_kernel_build": "NOT_RUN: pinned Lean runtime unavailable in this publication session",
        "compiled_outputs_present": len(list(source.rglob("*.olean"))),
        "compiled_output_boundary": "Recorded output/dependency hashes agree across receipts; .olean payloads are absent and cannot be rehashed here",
        "negative_controls_archived": seal["negative_controls"],
        "publication_excerpt_counts": dict(collections.Counter(e["kind"] for e in excerpts)),
        "publication_excerpts": excerpts, "modules": modules, "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "manifest_files_checked", "active_modules",
          "named_theorem_lemma_declarations", "direct_project_dependency_records_checked",
          "publication_excerpt_counts", "fresh_kernel_build", "failures")}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
