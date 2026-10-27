from __future__ import annotations

from collections import Counter
from pathlib import Path
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "Komorebi_Stratified_Universality_Foundations_v1.15.0_Block15.tex"
CONCORDANCE = ROOT / "Komorebi_Theorem_Concordance_v0.2.json"
VALIDATION = ROOT / "results" / "block15_lane_transport_validation.json"
GEN = ROOT / "generated"
RESULTS = ROOT / "results"
GEN.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


visited: set[Path] = set()
source_order: list[Path] = []
missing_inputs: list[str] = []


def collect(path: Path) -> str:
    path = path.resolve()
    if path in visited:
        return ""
    visited.add(path)
    source_order.append(path)
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    for item in re.findall(r"\\input\{([^}]+)\}", text):
        child = ROOT / item
        if child.suffix == "":
            child = child.with_suffix(".tex")
        if not child.exists():
            missing_inputs.append(str(child.relative_to(ROOT)))
        else:
            collect(child)
    return text


main_text = collect(MAIN)
full_text = "\n".join(
    path.read_text(encoding="utf-8") for path in source_order if path.exists()
)

check("main source exists", MAIN.exists(), MAIN.name)
check("all input files exist", not missing_inputs, ", ".join(missing_inputs))
for required in [
    "block14_section.tex",
    "block13_section.tex",
    "block15_section.tex",
    "publication_scope_section.tex",
    "publication_conclusion.tex",
]:
    check(
        f"required source included: {required}",
        rf"\input{{{required}}}" in main_text,
    )
check(
    "journal-facing version",
    "Consolidated Foundations Edition" in main_text
    and "Version 1.15.0" in main_text
    and "31 August 2026" in main_text,
)

abstract_match = re.search(
    r"\\begin\{abstract\}(.*?)\\end\{abstract\}", main_text, re.S
)
abstract_words = 0
if abstract_match:
    clean = re.sub(
        r"\\[A-Za-z@]+(?:\[[^]]*\])?(?:\{[^}]*\})?", " ", abstract_match.group(1)
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
for label in [
    "thm:additive-karoubi-envelope",
    "thm:atlas-assembly",
    "thm:block13-normalizer-coherence",
    "thm:block13-certified-invariant-descent",
    "thm:block13-global-completeness",
    "thm:block14-main",
    "thm:block15-universal-lane-transport",
    "thm:block15-abelian-fold-exact-sequence",
    "prop:block15-visible-support-ledger",
    "thm:block15-factorial-residue-realization",
    "thm:block15-lane-descent",
]:
    check(f"required theorem label: {label}", label in label_set)
check(
    "Block 15 theorem label present",
    any(label.startswith("thm:block15") for label in label_set),
)
check("labels are unique", len(labels) == len(label_set), str(len(labels) - len(label_set)))

refs: set[str] = set()
for command in ("ref", "pageref", "cref", "Cref", "autoref"):
    for group in re.findall(r"\\" + command + r"\{([^}]+)\}", full_text):
        refs.update(item.strip() for item in group.split(","))
missing_refs = sorted(item for item in refs if item and item not in label_set)
check(
    "all cross references resolve at source level",
    not missing_refs,
    ", ".join(missing_refs[:20]),
)

bibkeys = set(re.findall(r"\\bibitem\{([^}]+)\}", full_text))
cites: set[str] = set()
for group in re.findall(r"\\cite(?:\[[^]]*\])?\{([^}]+)\}", full_text):
    cites.update(item.strip() for item in group.split(","))
missing_cites = sorted(cites - bibkeys)
check("all citation keys are defined", not missing_cites, ", ".join(missing_cites))

missing_graphics: list[str] = []
graphics = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", full_text)
for name in graphics:
    path = ROOT / "figures" / name
    candidates = (
        [path]
        if path.suffix
        else [path.with_suffix(ext) for ext in (".pdf", ".png", ".jpg", ".jpeg")]
    )
    if not any(candidate.exists() for candidate in candidates):
        missing_graphics.append(name)
check("all included graphics exist", not missing_graphics, ", ".join(missing_graphics[:20]))

for literal in ["TODO", "TBD", "PLACEHOLDER"]:
    check(f"no unresolved literal: {literal}", literal not in full_text)

order = [
    r"\section{Introduction}",
    r"\input{block14_section.tex}",
    r"\part{Common foundations and finite assembly}",
    r"\section{Resolved theories, packet coordinates, and preservation profiles}",
    r"\section{Finite profiled resolved atlas assembly}",
    r"\part{Certified native strata}",
    r"\part{Certified global synthesis and scope}",
    r"\input{block13_section.tex}",
    r"\input{block15_section.tex}",
    r"\input{publication_scope_section.tex}",
    r"\input{publication_conclusion.tex}",
    r"\appendix",
]
positions = [main_text.find(token) for token in order]
check("publication proof order is complete", all(pos >= 0 for pos in positions), str(positions))
check("publication proof order is monotone", positions == sorted(positions), str(positions))

check(
    "independent-validation boundary stated",
    "independent peer validation" in full_text
    or "independent peer review" in full_text,
)
check(
    "finite-profile boundary stated",
    "finite profiled" in full_text.lower()
    and ("lane count" in full_text.lower() or "address count" in full_text.lower()),
)

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

concordance_data: dict[str, object] = {}
if CONCORDANCE.exists():
    try:
        concordance_data = json.loads(CONCORDANCE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        check("concordance parses", False, str(error))
else:
    check("concordance parses", False, "missing file")

if concordance_data:
    rows = concordance_data.get("concordance", [])
    summary_record = concordance_data.get("summary", {})
    ids = [row.get("id") for row in rows]
    status_counts = dict(Counter(row.get("status") for row in rows))
    domain_counts = dict(Counter(row.get("domain") for row in rows))
    check("concordance version is 0.2", concordance_data.get("version") == "0.2")
    check("concordance has 56 rows", len(rows) == 56, str(len(rows)))
    check("concordance identifiers are unique", len(ids) == len(set(ids)))
    check("concordance includes FND-16", "FND-16" in ids)
    check(
        "concordance row-count summary agrees",
        summary_record.get("row_count") == len(rows),
        f"{summary_record.get('row_count')}/{len(rows)}",
    )
    check(
        "concordance status summary agrees",
        summary_record.get("status_counts") == status_counts,
        f"{summary_record.get('status_counts')} / {status_counts}",
    )
    check(
        "concordance domain summary agrees",
        summary_record.get("domain_counts") == domain_counts,
        f"{summary_record.get('domain_counts')} / {domain_counts}",
    )
    check(
        "concordance internally proved count is 38",
        status_counts.get("proved internally") == 38,
        str(status_counts.get("proved internally")),
    )
    check(
        "concordance Foundations count is 16",
        domain_counts.get("Foundations") == 16,
        str(domain_counts.get("Foundations")),
    )
    edition_rows = concordance_data.get("edition_control", [])
    block15_editions = [
        row for row in edition_rows if row.get("file") == "block15_section.tex"
    ]
    actual_block15_hash = (
        hashlib.sha256((ROOT / "block15_section.tex").read_bytes()).hexdigest()
        if (ROOT / "block15_section.tex").exists()
        else ""
    )
    check(
        "Block 15 edition hash is synchronized",
        len(block15_editions) == 1
        and block15_editions[0].get("sha256") == actual_block15_hash,
        f"ledger={block15_editions[0].get('sha256') if block15_editions else 'missing'} actual={actual_block15_hash}",
    )

validation_data: dict[str, object] = {}
validation_parse_ok = False
validation_parse_detail = ""
if VALIDATION.exists():
    try:
        parsed_validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
        if isinstance(parsed_validation, dict):
            validation_data = parsed_validation
            validation_parse_ok = True
        else:
            validation_parse_detail = "top-level JSON value is not an object"
    except (json.JSONDecodeError, OSError) as error:
        validation_parse_detail = str(error)
else:
    validation_parse_detail = "missing file"
check("lane validation JSON parses as an object", validation_parse_ok, validation_parse_detail)


def exact_nonnegative_int(value: object) -> int | None:
    return value if type(value) is int and value >= 0 else None


def exact_count_map(value: object) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None
    if not all(
        isinstance(key, str) and exact_nonnegative_int(count) is not None
        for key, count in value.items()
    ):
        return None
    return dict(value)


failure_list_value = validation_data.get("failures")
failure_list = failure_list_value if isinstance(failure_list_value, list) else None
listed_failure_count = len(failure_list) if failure_list is not None else None
recorded_failure_count = exact_nonnegative_int(validation_data.get("failure_count"))
observed_total = exact_nonnegative_int(validation_data.get("total_assertions"))
expected_total = exact_nonnegative_int(
    validation_data.get("expected_total_assertions")
)
category_counts = exact_count_map(validation_data.get("category_counts"))
expected_category_counts = exact_count_map(
    validation_data.get("expected_category_counts")
)
category_total = sum(category_counts.values()) if category_counts is not None else None
expected_category_total = (
    sum(expected_category_counts.values())
    if expected_category_counts is not None
    else None
)

check("lane validation status PASS", validation_data.get("status") == "PASS")
check(
    "lane validation failures field is a list",
    failure_list is not None,
    type(failure_list_value).__name__,
)
check(
    "lane validation failure_count is a nonnegative integer",
    recorded_failure_count is not None,
    str(validation_data.get("failure_count")),
)
check(
    "lane validation failure_count agrees with failures",
    recorded_failure_count is not None
    and listed_failure_count is not None
    and recorded_failure_count == listed_failure_count,
    f"recorded={recorded_failure_count} listed={listed_failure_count}",
)
check(
    "lane validation has zero failures",
    recorded_failure_count == 0 and listed_failure_count == 0,
    f"recorded={recorded_failure_count} listed={listed_failure_count}",
)
check(
    "lane validation category_counts schema is valid",
    category_counts is not None,
    type(validation_data.get("category_counts")).__name__,
)
check(
    "lane validation expected_category_counts schema is valid",
    expected_category_counts is not None,
    type(validation_data.get("expected_category_counts")).__name__,
)
check(
    "lane validation category counts agree with expected counts",
    category_counts is not None
    and expected_category_counts is not None
    and category_counts == expected_category_counts,
    f"observed={category_counts} expected={expected_category_counts}",
)
check(
    "lane validation category counts sum to observed total",
    category_total is not None
    and observed_total is not None
    and category_total == observed_total,
    f"categories={category_total} observed={observed_total}",
)
check(
    "lane validation expected category counts sum to expected total",
    expected_category_total is not None
    and expected_total is not None
    and expected_category_total == expected_total,
    f"categories={expected_category_total} expected={expected_total}",
)
check(
    "lane validation observed and expected totals agree",
    observed_total is not None
    and expected_total is not None
    and observed_total == expected_total,
    f"observed={observed_total} expected={expected_total}",
)
check(
    "lane validation expected assertion count is 197099",
    expected_total == 197099,
    str(expected_total),
)

lane_validation_record_ok = (
    validation_parse_ok
    and validation_data.get("status") == "PASS"
    and recorded_failure_count == 0
    and listed_failure_count == 0
    and category_counts is not None
    and expected_category_counts is not None
    and category_counts == expected_category_counts
    and category_total == observed_total
    and expected_category_total == expected_total
    and observed_total == expected_total == 197099
)

build_sh = (ROOT / "Build.sh").read_text(encoding="utf-8")
build_ps1 = (ROOT / "Build.ps1").read_text(encoding="utf-8")
direct_powershell_python_calls = [
    line.strip()
    for line in build_ps1.splitlines()
    if re.match(r"^\s*python(?:\.exe)?\s+", line, re.I)
]
check(
    "shell build gates Block 15 verifier and audit",
    "set -euo pipefail" in build_sh
    and "python verify_block15_lane_transport.py" in build_sh
    and "python verify_block15_publication_audit.py" in build_sh,
)
check(
    "PowerShell build gates Block 15 verifier and audit",
    "verify_block15_lane_transport.py" in build_ps1
    and "Block 15 lane verifier failed" in build_ps1
    and "verify_block15_publication_audit.py" in build_ps1
    and "Block 15 publication audit failed" in build_ps1,
)
check(
    "PowerShell build wraps every Python step in a fail-fast gate",
    "function Invoke-PythonChecked" in build_ps1
    and "& python $Script" in build_ps1
    and "$ExitCode = $LASTEXITCODE" in build_ps1
    and not direct_powershell_python_calls,
    ", ".join(direct_powershell_python_calls),
)

failures = [record for record in checks if not record["pass"]]
summary = {
    "audit_checks": len(checks),
    "audit_failures": len(failures),
    "abstract_words": abstract_words,
    "source_graph_files": len(source_order),
    "labels": len(labels),
    "references": len(refs),
    "citations": len(cites),
    "graphics": len(graphics),
    "lane_validation_status": validation_data.get("status"),
    "lane_validation_assertions": observed_total,
    "lane_validation_expected_assertions": expected_total,
    "lane_validation_failure_count": recorded_failure_count,
    "lane_validation_category_assertions": category_total,
    "failures": failures,
    "checks": checks,
}
(RESULTS / "block15_publication_audit.json").write_text(
    json.dumps(summary, indent=2) + "\n", encoding="utf-8"
)

counts = "\n".join(
    [
        rf"\newcommand{{\BlockFifteenAuditChecks}}{{{summary['audit_checks']:,}}}",
        rf"\newcommand{{\BlockFifteenAuditFailures}}{{{summary['audit_failures']:,}}}",
        rf"\newcommand{{\BlockFifteenAbstractWords}}{{{abstract_words:,}}}",
        rf"\newcommand{{\BlockFifteenSourceFiles}}{{{summary['source_graph_files']:,}}}",
        rf"\newcommand{{\BlockFifteenLabels}}{{{summary['labels']:,}}}",
        rf"\newcommand{{\BlockFifteenReferences}}{{{summary['references']:,}}}",
    ]
) + "\n"
(GEN / "block15_publication_counts.tex").write_text(counts, encoding="utf-8")

rows = [
    ("Source graph", f"{summary['source_graph_files']:,} TeX files", not missing_inputs),
    ("Abstract length", f"{abstract_words:,} words", abstract_words <= 350),
    (
        "Labels and references",
        f"{summary['labels']:,} labels; {summary['references']:,} references",
        not missing_refs and len(labels) == len(label_set),
    ),
    ("Citation keys", f"{summary['citations']:,} cited keys", not missing_cites),
    ("Graphics", f"{summary['graphics']:,} included assets", not missing_graphics),
    (
        "Lane verifier",
        f"{int(observed_total or 0):,} exact assertions",
        lane_validation_record_ok,
    ),
    (
        "Publication structure audit",
        f"{summary['audit_checks']:,} assertions",
        not failures,
    ),
]
table_lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\small",
    r"\caption{Publication-source audit for the Block 15 consolidated edition.}",
    r"\label{tab:block15-publication-audit}",
    r"\begin{tabularx}{\textwidth}{@{}L{0.27\textwidth}YL{0.12\textwidth}@{}}",
    r"\toprule",
    "Audit area & Record & Status \\\\",
    r"\midrule",
]
for area, record, passed in rows:
    table_lines.append(f"{area} & {record} & {'PASS' if passed else 'FAIL'} \\\\")
table_lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table}", ""])
(GEN / "block15_publication_audit_table.tex").write_text(
    "\n".join(table_lines), encoding="utf-8"
)

print(
    json.dumps(
        {
            key: summary[key]
            for key in [
                "audit_checks",
                "audit_failures",
                "abstract_words",
                "source_graph_files",
                "labels",
                "references",
                "citations",
                "graphics",
                "lane_validation_status",
                "lane_validation_assertions",
                "lane_validation_expected_assertions",
                "lane_validation_failure_count",
                "lane_validation_category_assertions",
            ]
        },
        indent=2,
    )
)
if failures:
    for failure in failures:
        print("FAIL:", failure["name"], failure["detail"])
    raise SystemExit(1)
