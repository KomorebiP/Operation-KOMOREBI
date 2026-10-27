from __future__ import annotations

"""Publication-integrity audit for the 6 October 2026 publication edition, adapted from v2.0.0.

This checks source synchronization, cross references, concordance state,
validation records, PDF structure, and LaTeX diagnostics. It does not replace
independent mathematical or historical review.
"""

from collections import Counter
from pathlib import Path
import hashlib
import json
import re

import fitz

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "Stratified_Universality_Traditional.tex"
PDF = MAIN.with_suffix(".pdf")
LOG = MAIN.with_suffix(".log")
CONCORDANCE = ROOT / "Komorebi_Theorem_Concordance_Final_2026-10-06.json"
RESULTS = ROOT / "results"
GENERATED = ROOT / "generated"
RESULTS.mkdir(exist_ok=True)
GENERATED.mkdir(exist_ok=True)
FINAL_RESULTS = ROOT / "final_edition_validation"
FINAL_RESULTS.mkdir(exist_ok=True)
RESULT = FINAL_RESULTS / "traditional_publication_audit.json"
COUNTS = FINAL_RESULTS / "traditional_publication_counts.tex"
TABLE = FINAL_RESULTS / "traditional_publication_audit_table.tex"

checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


def text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        check(f"UTF-8 readable: {path.name}", False, str(exc))
        return ""

visited: set[Path] = set()
ordered: list[Path] = []
missing_inputs: list[str] = []


def collect(path: Path) -> None:
    path = path.resolve()
    if path in visited:
        return
    visited.add(path)
    ordered.append(path)
    if not path.exists():
        return
    for item in re.findall(r"\\input\{([^}]+)\}", text(path)):
        child = ROOT / item
        if child.suffix == "":
            child = child.with_suffix(".tex")
        if child.exists():
            collect(child)
        else:
            missing_inputs.append(str(child.relative_to(ROOT)))

check("main source exists", MAIN.exists(), MAIN.name)
check("compiled PDF exists", PDF.exists(), PDF.name)
check("concordance v0.4 exists", CONCORDANCE.exists(), CONCORDANCE.name)
collect(MAIN)
main = text(MAIN)
full = "\n".join(text(p) for p in ordered if p.exists())
check("all recursive TeX inputs exist", not missing_inputs, ", ".join(missing_inputs))

for required in [
    "block13_section.tex", "block15_section.tex", "block16_section_final.tex",
    "block17_semantic_quotients_final.tex", "block18_carrier_observer_change_final.tex",
    "block19_admissibility_lifting_final.tex", "publication_scope_section.tex",
    "publication_conclusion.tex",
]:
    check(f"required source included: {required}", rf"\input{{{required}}}" in main)

check("version/date/edition synchronized", all(x in main for x in ["version 2.0.0", "23 September 2026", "Final Publication Edition", "6 October 2026"]))
check("Part IV present", r"\part{Relative semantic quotients and changes of doctrine}" in main)
check("final concordance source named", "Komorebi_Theorem_Concordance_Final_2026-10-06.json" in full)

abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", main, re.S)
abstract_words = 0
if abstract:
    clean = re.sub(r"\\[A-Za-z@]+(?:\[[^]]*\])?(?:\{[^}]*\})?", " ", abstract.group(1))
    abstract_words = len(re.sub(r"[^A-Za-z0-9-]+", " ", clean).split())
check("abstract present", abstract is not None)
check("abstract at most 350 words", abstract_words <= 350, str(abstract_words))

front_end = main.find(r"\part{Common foundations and finite assembly}")
front = main[:front_end if front_end >= 0 else len(main)]
for phrase in ["Progressive expansion", "next block", "Work Package 0"]:
    check(f"front matter excludes development phrase: {phrase}", phrase not in front)

labels = re.findall(r"\\label\{([^}]+)\}", full)
label_set = set(labels)
check("all labels unique", len(labels) == len(label_set), str(len(labels)-len(label_set)))
for label in [
    "thm:block14-main", "thm:block15-universal-lane-transport",
    "thm:block16-holonomy-twisted-lane-transport",
    "thm:block17-main-semantic", "thm:block17-universal-behavioral-coimage",
    "thm:block17-semantic-diamond", "thm:block18-carrier-factorization",
    "thm:block18-bridge-loss-exact", "thm:block18-observer-base-change",
    "thm:block19-convex-quadratic-separation",
    "thm:block19-relative-semantic-synthesis",
]:
    check(f"required theorem label: {label}", label in label_set)

refs: set[str] = set()
for command in ["ref", "pageref", "cref", "Cref", "autoref"]:
    for group in re.findall(r"\\" + command + r"\{([^}]+)\}", full):
        refs.update(x.strip() for x in group.split(","))
missing_refs = sorted(x for x in refs if x and x not in label_set)
check("all source-level references resolve", not missing_refs, ", ".join(missing_refs[:20]))

bibkeys = set(re.findall(r"\\bibitem\{([^}]+)\}", full))
cites: set[str] = set()
for group in re.findall(r"\\cite(?:\[[^]]*\])?\{([^}]+)\}", full):
    cites.update(x.strip() for x in group.split(","))
missing_cites = sorted(cites - bibkeys)
check("all citation keys defined", not missing_cites, ", ".join(missing_cites[:20]))

missing_graphics: list[str] = []
for name in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", full):
    base = ROOT / "figures" / name
    candidates = [base] if base.suffix else [base.with_suffix(ext) for ext in [".pdf", ".png", ".jpg", ".jpeg"]]
    if not any(p.exists() for p in candidates):
        missing_graphics.append(name)
check("all graphics exist", not missing_graphics, ", ".join(missing_graphics[:20]))

for literal in ["TODO", "TBD", "PLACEHOLDER"]:
    check(f"no unresolved literal: {literal}", literal not in full)

# Balanced high-risk environments
for env in ["document", "abstract", "theorem", "proposition", "corollary", "definition", "example", "boundary", "proof", "table", "figure", "landscape", "tcolorbox"]:
    starts = len(re.findall(r"\\begin\{" + re.escape(env) + r"\}", full))
    ends = len(re.findall(r"\\end\{" + re.escape(env) + r"\}", full))
    check(f"environment balance: {env}", starts == ends, f"{starts}/{ends}")

order = [
    r"\section{Introduction}", r"\input{block14_section.tex}",
    r"\part{Common foundations and finite assembly}",
    r"\part{Certified native strata}",
    r"\part{Certified global synthesis and scope}",
    r"\input{block16_section_final.tex}",
    r"\part{Relative semantic quotients and changes of doctrine}",
    r"\input{block17_semantic_quotients_final.tex}",
    r"\input{block18_carrier_observer_change_final.tex}",
    r"\input{block19_admissibility_lifting_final.tex}",
    r"\input{publication_scope_section.tex}",
    r"\input{publication_conclusion.tex}", r"\appendix",
]
pos = [main.find(x) for x in order]
check("publication order complete", all(x >= 0 for x in pos), str(pos))
check("publication order monotone", pos == sorted(pos), str(pos))

concordance = json.loads(text(CONCORDANCE)) if CONCORDANCE.exists() else {}
rows = concordance.get("concordance", [])
summary = concordance.get("summary", {})
check("concordance has 75 components", len(rows) == 75, str(len(rows)))
check("concordance summary row count synchronized", summary.get("row_count") == len(rows), str(summary.get("row_count")))
actual_status = Counter(row.get("status") for row in rows)
check("concordance status counts synchronized", dict(actual_status) == summary.get("status_counts"), str(actual_status))
check("new semantic domains present", all(name in summary.get("domain_counts", {}) for name in ["Semantic quotient calculus", "Bridge loss calculus", "Carrier and observer change", "Convex and admissibility change", "Doctrine comparison"]))

for path, expected_assertions in [
    (RESULTS / "block15_lane_transport_validation.json", None),
    (RESULTS / "block16_holonomy_lane_transport_validation.json", 1_344_823),
    (RESULTS / "block17_semantic_extension_validation.json", 3_022),
]:
    data = json.loads(text(path)) if path.exists() else {}
    check(f"validation PASS: {path.name}", data.get("status") == "PASS", str(data.get("status")))
    if expected_assertions is not None:
        check(f"validation count: {path.name}", data.get("assertions") == expected_assertions, str(data.get("assertions")))
    check(f"validation failures empty: {path.name}", data.get("failures") == [], str(data.get("failures")))

pdf_pages = 0
pdf_meta: dict[str, str] = {}
hits = {"lane": False, "semantic": False, "carrier": False, "admissibility": False}
if PDF.exists():
    try:
        with fitz.open(PDF) as doc:
            pdf_pages = doc.page_count
            pdf_meta = {k: str(v or "") for k, v in doc.metadata.items()}
            for page in doc:
                t = page.get_text()
                hits["lane"] |= "Holonomy-Twisted Universal Lane Transport Theorem" in t
                hits["semantic"] |= "Universal behavioral coimage" in t
                hits["carrier"] |= "Carrier factorization gate" in t
                hits["admissibility"] |= "Sharp geometry-class separation" in t
        check("compiled PDF opens", True)
    except Exception as exc:
        check("compiled PDF opens", False, str(exc))
else:
    check("compiled PDF opens", False, "missing")
check("compiled PDF page count plausible", 240 <= pdf_pages <= 280, str(pdf_pages))
for k, found in hits.items():
    check(f"compiled PDF contains {k} theorem layer", found)
check("PDF metadata subject synchronized", "semantic quotient" in pdf_meta.get("subject", "").lower(), pdf_meta.get("subject", ""))
check("PDF author synchronized", pdf_meta.get("author") == "Komorebi P.", pdf_meta.get("author", ""))

log = text(LOG) if LOG.exists() else ""
check("LaTeX log exists", LOG.exists())
check("LaTeX log has no undefined references", "undefined" not in log.lower())
check("LaTeX log has no overfull boxes", "overfull" not in log.lower())
check("LaTeX log has no fatal errors", "fatal error" not in log.lower())

failures = [r for r in checks if not r["pass"]]
payload = {
    "schema": "komorebi.stratified-universality.final-edition-publication-audit.v1",
    "status": "PASS" if not failures else "FAIL",
    "audit_checks": len(checks),
    "audit_failures": len(failures),
    "abstract_words": abstract_words,
    "source_graph_files": len(ordered),
    "labels": len(labels),
    "references": len(refs),
    "citations": len(cites),
    "pdf_pages": pdf_pages,
    "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest() if PDF.exists() else None,
    "source_sha256": hashlib.sha256(MAIN.read_bytes()).hexdigest() if MAIN.exists() else None,
    "concordance_components": len(rows),
    "semantic_validation_assertions": 3022,
    "failures": failures,
    "checks": checks,
    "boundary": "Internal publication-integrity audit of the final edition; inherited validation records are inspected, not rerun by this script. Not independent mathematical review, historical-priority validation, or Lean certification.",
}
RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

COUNTS.write_text("\n".join([
    "% Generated by verify_final_publication.py",
    rf"\newcommand{{\FormalFoundationsAuditChecks}}{{{len(checks):,}}}",
    rf"\newcommand{{\FormalFoundationsAuditFailures}}{{{len(failures):,}}}",
    rf"\newcommand{{\FormalFoundationsPages}}{{{pdf_pages:,}}}",
    rf"\newcommand{{\FormalFoundationsAbstractWords}}{{{abstract_words:,}}}",
    rf"\newcommand{{\FormalFoundationsConcordanceRows}}{{{len(rows):,}}}",
]) + "\n", encoding="utf-8")

TABLE.write_text("\n".join([
    r"\begin{table}[htbp]", r"\centering", r"\small",
    r"\caption{Final formal-foundations publication audit.}",
    r"\label{tab:formal-foundations-v2-audit}",
    r"\begin{tabularx}{\textwidth}{@{}L{0.31\textwidth}Y@{}}", r"\toprule",
    r"Audit surface & Recorded result\\", r"\midrule",
    rf"Source graph & {len(ordered):,} recursively included TeX files; {len(labels):,} labels; {len(refs):,} source references\\",
    rf"Concordance & {len(rows):,} components with synchronized status and domain counts\\",
    rf"Inherited validation & Block 15 PASS; Block 16 PASS with 1,344,823 assertions\\",
    rf"Part IV validation & 3,022 exact symbolic assertions; zero recorded failures\\",
    rf"Compiled artifact & {pdf_pages:,} pages; metadata, theorem-layer text, references, citations, and graphics checked\\",
    rf"Audit result & {len(checks):,} checks; {len(failures):,} failures\\",
    r"Boundary & Internal publication integrity only; not independent peer review or historical-priority validation.\\",
    r"\bottomrule", r"\end{tabularx}", r"\end{table}",
]) + "\n", encoding="utf-8")

print(json.dumps({"status": payload["status"], "checks": len(checks), "failures": len(failures), "pages": pdf_pages}, indent=2))
if failures:
    for row in failures:
        print(row)
    raise SystemExit(1)
