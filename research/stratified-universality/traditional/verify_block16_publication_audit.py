from __future__ import annotations

"""Source, validation, concordance, and PDF audit for the Block 16 extension.

This is an internal release-integrity audit. It checks synchronization and
reproducibility surfaces; it is not independent mathematical peer review.
"""

from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import sys

import fitz


ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.tex"
PDF = ROOT / "Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.pdf"
CONCORDANCE = ROOT / "Komorebi_Theorem_Concordance_v0.3.json"
VALIDATION = ROOT / "results" / "block16_holonomy_lane_transport_validation.json"
BLOCK16 = ROOT / "block16_section.tex"
RESULTS = ROOT / "results"
GENERATED = ROOT / "generated"
RESULTS.mkdir(exist_ok=True)
GENERATED.mkdir(exist_ok=True)

RESULT_PATH = RESULTS / "block16_publication_audit.json"
COUNTS_PATH = GENERATED / "block16_publication_counts.tex"
TABLE_PATH = GENERATED / "block16_publication_audit_table.tex"

EXPECTED_VALIDATION_TOTAL = 1_344_823
EXPECTED_VALIDATION_COUNTS = {
    "group_action_and_orbit_descent": 7_780,
    "permutation_intertwiner_basis": 3_537,
    "orbital_path_composition": 1_212_963,
    "selector_controls": 994,
    "equivariant_refinement": 10_162,
    "cyclotomic_rational_descent": 109_374,
    "source_contract": 13,
}

checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        check(f"UTF-8 source readable: {path.name}", False, str(error))
        return ""


visited: set[Path] = set()
source_order: list[Path] = []
missing_inputs: list[str] = []


def collect(path: Path) -> None:
    path = path.resolve()
    if path in visited:
        return
    visited.add(path)
    source_order.append(path)
    if not path.exists():
        return
    text = read_text(path)
    for item in re.findall(r"\\input\{([^}]+)\}", text):
        child = ROOT / item
        if child.suffix == "":
            child = child.with_suffix(".tex")
        if not child.exists():
            missing_inputs.append(str(child.relative_to(ROOT)))
        else:
            collect(child)


check("main source exists", MAIN.exists(), MAIN.name)
check("Block 16 theorem source exists", BLOCK16.exists(), BLOCK16.name)
check("Block 16 validation JSON exists", VALIDATION.exists(), str(VALIDATION))
check("concordance v0.3 exists", CONCORDANCE.exists(), CONCORDANCE.name)
collect(MAIN)
main_text = read_text(MAIN) if MAIN.exists() else ""
full_text = "\n".join(read_text(path) for path in source_order if path.exists())
check("all recursive TeX inputs exist", not missing_inputs, ", ".join(missing_inputs))

for required in [
    "block13_section.tex",
    "block15_section.tex",
    "block16_section.tex",
    "publication_scope_section.tex",
    "publication_conclusion.tex",
]:
    check(
        f"required source included: {required}",
        rf"\input{{{required}}}" in main_text,
    )

check(
    "journal-facing version is 1.16.0",
    "Version 1.16.0" in main_text
    and "31 August 2026" in main_text
    and "Holonomy-Twisted" in main_text,
)
check(
    "Block 16 validation macros are included",
    r"\input{generated/block16_counts.tex}" in main_text,
)
check(
    "Block 16 publication table is included",
    r"\input{generated/block16_publication_audit_table.tex}" in main_text,
)

abstract_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", main_text, re.S)
abstract_words = 0
if abstract_match:
    clean = re.sub(
        r"\\[A-Za-z@]+(?:\[[^]]*\])?(?:\{[^}]*\})?",
        " ",
        abstract_match.group(1),
    )
    clean = re.sub(r"[^A-Za-z0-9-]+", " ", clean)
    abstract_words = len(clean.split())
check("abstract present", abstract_match is not None)
check("abstract length at most 350 words", abstract_words <= 350, str(abstract_words))

front_marker = r"\part{Common foundations and finite assembly}"
front_end = main_text.find(front_marker)
front_text = main_text[: front_end if front_end >= 0 else len(main_text)]
for phrase in ["Progressive expansion", "next block", "Work Package 0"]:
    check(f"front matter excludes development phrase: {phrase}", phrase not in front_text)

labels = re.findall(r"\\label\{([^}]+)\}", full_text)
label_set = set(labels)
required_labels = [
    "thm:block15-universal-lane-transport",
    "thm:block15-lane-descent",
    "def:block16-holonomy-profiled-lane-datum",
    "def:block16-matrix-local-system",
    "thm:block16-holonomy-twisted-lane-transport",
    "thm:block16-orbit-descent",
    "thm:block16-permutation-orbital-calculus",
    "prop:block16-rational-cyclotomic-orbit-lanes",
    "bnd:block16-finite-twisted-scope",
]
for label in required_labels:
    check(f"required theorem label: {label}", label in label_set)
check("all labels are unique", len(labels) == len(label_set), str(len(labels) - len(label_set)))

refs: set[str] = set()
for command in ("ref", "pageref", "cref", "Cref", "autoref"):
    for group in re.findall(r"\\" + command + r"\{([^}]+)\}", full_text):
        refs.update(item.strip() for item in group.split(","))
missing_refs = sorted(item for item in refs if item and item not in label_set)
check("all source-level cross references resolve", not missing_refs, ", ".join(missing_refs[:25]))

bibkeys = set(re.findall(r"\\bibitem\{([^}]+)\}", full_text))
cites: set[str] = set()
for group in re.findall(r"\\cite(?:\[[^]]*\])?\{([^}]+)\}", full_text):
    cites.update(item.strip() for item in group.split(","))
missing_cites = sorted(cites - bibkeys)
check("all citation keys are defined", not missing_cites, ", ".join(missing_cites[:25]))

missing_graphics: list[str] = []
graphics = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", full_text)
for name in graphics:
    path = ROOT / "figures" / name
    candidates = [path] if path.suffix else [path.with_suffix(ext) for ext in (".pdf", ".png", ".jpg", ".jpeg")]
    if not any(candidate.exists() for candidate in candidates):
        missing_graphics.append(name)
check("all included graphics exist", not missing_graphics, ", ".join(missing_graphics[:25]))

for literal in ("TODO", "TBD", "PLACEHOLDER"):
    check(f"no unresolved literal: {literal}", literal not in full_text)

order = [
    r"\section{Introduction}",
    r"\input{block14_section.tex}",
    r"\part{Common foundations and finite assembly}",
    r"\part{Certified native strata}",
    r"\part{Certified global synthesis and scope}",
    r"\input{block13_section.tex}",
    r"\input{block15_section.tex}",
    r"\input{block16_section.tex}",
    r"\input{publication_scope_section.tex}",
    r"\input{publication_conclusion.tex}",
    r"\appendix",
]
positions = [main_text.find(token) for token in order]
check("publication proof order is complete", all(pos >= 0 for pos in positions), str(positions))
check("publication proof order is monotone", positions == sorted(positions), str(positions))

for environment in [
    "document",
    "abstract",
    "theorem",
    "proposition",
    "lemma",
    "corollary",
    "definition",
    "example",
    "remark",
    "boundary",
    "proof",
    "table",
    "figure",
    "landscape",
    "tcolorbox",
]:
    begins = len(re.findall(r"\\begin\{" + re.escape(environment) + r"\}", full_text))
    ends = len(re.findall(r"\\end\{" + re.escape(environment) + r"\}", full_text))
    check(f"environment balance: {environment}", begins == ends, f"{begins}/{ends}")

normalized = " ".join(full_text.split())
for phrase in [
    "matrix local system",
    "simultaneous monodromy image",
    "finest ordinary globally labeled coarsening",
    "pair orbits form an exact basis",
    "countably infinite lane sums",
    "not an external validation record",
]:
    check(f"claim-boundary/source phrase present: {phrase}", phrase in normalized)

concordance_data: dict[str, object] = {}
try:
    parsed = json.loads(read_text(CONCORDANCE))
    if isinstance(parsed, dict):
        concordance_data = parsed
        check("concordance parses as an object", True)
    else:
        check("concordance parses as an object", False, type(parsed).__name__)
except json.JSONDecodeError as error:
    check("concordance parses as an object", False, str(error))

if concordance_data:
    rows_value = concordance_data.get("concordance")
    rows = rows_value if isinstance(rows_value, list) else []
    ids = [row.get("id") for row in rows if isinstance(row, dict)]
    statuses = Counter(row.get("status") for row in rows if isinstance(row, dict))
    domains = Counter(row.get("domain") for row in rows if isinstance(row, dict))
    summary = concordance_data.get("summary") if isinstance(concordance_data.get("summary"), dict) else {}
    check("concordance version is 0.3", concordance_data.get("version") == "0.3")
    check("concordance has 57 rows", len(rows) == 57, str(len(rows)))
    check("concordance identifiers are unique", len(ids) == len(set(ids)))
    check("concordance includes FND-17", "FND-17" in ids)
    check("concordance internal-proof count is 39", statuses.get("proved internally") == 39, str(statuses))
    check("concordance Foundations count is 17", domains.get("Foundations") == 17, str(domains))
    check("concordance row summary agrees", summary.get("row_count") == len(rows), str(summary.get("row_count")))
    check("concordance status summary agrees", summary.get("status_counts") == dict(statuses), str(summary.get("status_counts")))
    check("concordance domain summary agrees", summary.get("domain_counts") == dict(domains), str(summary.get("domain_counts")))
    fnd17 = [row for row in rows if isinstance(row, dict) and row.get("id") == "FND-17"]
    check(
        "FND-17 points to all principal Block 16 labels",
        len(fnd17) == 1
        and all(
            label in str(fnd17[0].get("exact_theorem_or_section", ""))
            for label in required_labels[4:8]
        ),
    )
    editions_value = concordance_data.get("edition_control")
    editions = editions_value if isinstance(editions_value, list) else []
    b16_editions = [row for row in editions if isinstance(row, dict) and row.get("file") == "block16_section.tex"]
    actual_hash = hashlib.sha256(BLOCK16.read_bytes()).hexdigest() if BLOCK16.exists() else ""
    check(
        "Block 16 edition hash is synchronized",
        len(b16_editions) == 1 and b16_editions[0].get("sha256") == actual_hash,
        f"ledger={b16_editions[0].get('sha256') if b16_editions else 'missing'} actual={actual_hash}",
    )

validation_data: dict[str, object] = {}
try:
    parsed = json.loads(read_text(VALIDATION))
    if isinstance(parsed, dict):
        validation_data = parsed
        check("Block 16 validation parses as an object", True)
    else:
        check("Block 16 validation parses as an object", False, type(parsed).__name__)
except json.JSONDecodeError as error:
    check("Block 16 validation parses as an object", False, str(error))

if validation_data:
    counts = validation_data.get("counts")
    expected_counts = validation_data.get("expected_counts")
    failures = validation_data.get("failures")
    check("Block 16 validation status PASS", validation_data.get("status") == "PASS")
    check("Block 16 validation assertion total is frozen", validation_data.get("assertions") == EXPECTED_VALIDATION_TOTAL, str(validation_data.get("assertions")))
    check("Block 16 expected assertion total is frozen", validation_data.get("expected_assertions") == EXPECTED_VALIDATION_TOTAL, str(validation_data.get("expected_assertions")))
    check("Block 16 category counts match frozen contract", counts == EXPECTED_VALIDATION_COUNTS, str(counts))
    check("Block 16 expected counts match frozen contract", expected_counts == EXPECTED_VALIDATION_COUNTS, str(expected_counts))
    check("Block 16 validation has zero failures", isinstance(failures, list) and len(failures) == 0, str(failures))
    check("Block 16 category counts sum to total", isinstance(counts, dict) and sum(counts.values()) == EXPECTED_VALIDATION_TOTAL)

pdf_pages = 0
pdf_metadata: dict[str, str] = {}
pdf_text_hits = False
if PDF.exists():
    try:
        with fitz.open(PDF) as document:
            pdf_pages = document.page_count
            pdf_metadata = {k: str(v or "") for k, v in document.metadata.items()}
            pdf_text_hits = any(
                "Holonomy-Twisted Universal Lane Transport Theorem" in document[index].get_text()
                for index in range(document.page_count)
            )
        check("compiled PDF opens", True)
    except Exception as error:  # audit should report, not mask, renderer failures
        check("compiled PDF opens", False, str(error))
else:
    check("compiled PDF opens", False, "missing PDF")
check("compiled PDF has 239 pages", pdf_pages == 239, str(pdf_pages))
check("compiled PDF contains the Block 16 theorem", pdf_text_hits)
check(
    "compiled PDF metadata names holonomy-twisted scope",
    "holonomy-twisted" in pdf_metadata.get("subject", "").lower(),
    pdf_metadata.get("subject", ""),
)

log_path = PDF.with_suffix(".log")
log_text = read_text(log_path) if log_path.exists() else ""
check("LaTeX log exists", log_path.exists())
check("LaTeX log has no undefined references", "undefined" not in log_text.lower())
check("LaTeX log has no overfull boxes", "overfull" not in log_text.lower())
check("LaTeX log has no fatal errors", "fatal error" not in log_text.lower())

failures = [record for record in checks if not record["pass"]]
summary = {
    "status": "PASS" if not failures else "FAIL",
    "audit_checks": len(checks),
    "audit_failures": len(failures),
    "abstract_words": abstract_words,
    "source_graph_files": len(source_order),
    "labels": len(labels),
    "references": len(refs),
    "citations": len(cites),
    "graphics": len(graphics),
    "pdf_pages": pdf_pages,
    "validation_assertions": validation_data.get("assertions"),
    "validation_failures": len(validation_data.get("failures", [])) if isinstance(validation_data.get("failures"), list) else None,
    "failures": failures,
    "checks": checks,
    "boundary": "Internal release-integrity audit; not independent peer review or historical-priority validation.",
}
RESULT_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

COUNTS_PATH.write_text(
    "\n".join(
        [
            "% Generated by verify_block16_publication_audit.py",
            rf"\newcommand{{\BlockSixteenAuditChecks}}{{{summary['audit_checks']:,}}}",
            rf"\newcommand{{\BlockSixteenAuditFailures}}{{{summary['audit_failures']:,}}}",
            rf"\newcommand{{\BlockSixteenAbstractWords}}{{{abstract_words:,}}}",
            rf"\newcommand{{\BlockSixteenSourceFiles}}{{{summary['source_graph_files']:,}}}",
            rf"\newcommand{{\BlockSixteenLabels}}{{{summary['labels']:,}}}",
            rf"\newcommand{{\BlockSixteenReferences}}{{{summary['references']:,}}}",
            "",
        ]
    ),
    encoding="utf-8",
)

rows = [
    ("Source graph", f"{summary['source_graph_files']:,} TeX files", not missing_inputs),
    ("Abstract", f"{abstract_words:,} words", abstract_match is not None and abstract_words <= 350),
    ("Labels and references", f"{summary['labels']:,} labels; {summary['references']:,} references", not missing_refs and len(labels) == len(label_set)),
    ("Citation keys", f"{summary['citations']:,} cited keys", not missing_cites),
    ("Graphics", f"{summary['graphics']:,} included assets", not missing_graphics),
    ("Block 16 verifier", f"{EXPECTED_VALIDATION_TOTAL:,} exact assertions", validation_data.get("status") == "PASS" and validation_data.get("assertions") == EXPECTED_VALIDATION_TOTAL and validation_data.get("failures") == []),
    ("Concordance", "57 synchronized entries through FND-17", any(isinstance(row, dict) and row.get("id") == "FND-17" for row in concordance_data.get("concordance", []) if isinstance(concordance_data.get("concordance"), list))),
    ("Compiled PDF", f"{pdf_pages:,} pages", pdf_pages == 239 and pdf_text_hits),
    ("Publication audit", f"{summary['audit_checks']:,} checks", not failures),
]
lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\small",
    r"\caption{Publication-source and release-integrity audit for the Block 16 holonomy-twisted extension.}",
    r"\label{tab:block16-publication-audit}",
    r"\begin{tabularx}{\textwidth}{@{}L{0.27\textwidth}YL{0.12\textwidth}@{}}",
    r"\toprule",
    r"Audit area & Record & Status \\",
    r"\midrule",
]
for area, record, passed in rows:
    status_text = "PASS" if passed else "FAIL"
    lines.append(f"{area} & {record} & {status_text}" + r" \\")
lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table}", ""])
TABLE_PATH.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({key: summary[key] for key in [
    "status", "audit_checks", "audit_failures", "abstract_words",
    "source_graph_files", "labels", "references", "citations",
    "graphics", "pdf_pages", "validation_assertions", "validation_failures",
]}, indent=2))
if failures:
    for failure in failures:
        print(f"FAIL: {failure['name']}: {failure['detail']}", file=sys.stderr)
    raise SystemExit(1)
