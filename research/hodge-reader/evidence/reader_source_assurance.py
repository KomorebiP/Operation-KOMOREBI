"""Static LaTeX source assurance, not a parser or mathematical proof checker."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
sources = sorted(PAPER.glob("*.tex")) + sorted((PAPER / "tables").glob("*.tex"))
sources.append(ROOT / "shared/preamble.tex")
labels = {}
refs = []
cites = []
bibitems = []
inputs = []
graphics = []
environment_checks = []
literal_newline_tokens = []
for source in sources:
    text = source.read_text()
    name = source.relative_to(ROOT).as_posix()
    def position(match):
        return {"file": name, "line": text[:match.start()].count("\n") + 1}
    for match in re.finditer(r"\\label\{([^}]+)\}", text):
        if "#" not in match[1]:
            labels.setdefault(match[1], []).append(position(match))
    for match in re.finditer(r"\\(?:ref|eqref|pageref|autoref)\{([^}]+)\}", text):
        refs.append({"label": match[1], **position(match)})
    for match in re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", text):
        cites.extend(key.strip() for key in match[1].split(","))
    bibitems.extend(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", text))
    for match in re.finditer(r"\\input\{([^}]+)\}", text):
        item = match[1]
        path = PAPER / item
        if not path.suffix:
            path = path.with_suffix(".tex")
        inputs.append({"path": item, "exists": path.is_file(), **position(match)})
    for match in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
        item = match[1]
        if "#" in item:
            continue
        candidates = [PAPER / item, PAPER / "historical_assets/figures" / item,
                      ROOT / "shared/figures" / item]
        graphics.append({"path": item, "exists": any(p.is_file() for p in candidates),
                         **position(match)})
    stack = []
    mismatches = []
    for match in re.finditer(r"\\(begin|end)\{([^}]+)\}", text):
        kind, env = match.groups()
        if kind == "begin":
            stack.append(env)
        elif not stack or stack[-1] != env:
            mismatches.append({"environment": env, "stack_top": stack[-1] if stack else None,
                               **position(match)})
        else:
            stack.pop()
    environment_checks.append({"file": name, "mismatches": mismatches, "unclosed": stack})
    for match in re.finditer(r"\\n(?=\\|[A-Z])", text):
        literal_newline_tokens.append(position(match))

log_path = PAPER / "main.log"
pdf_path = PAPER / "main.pdf"
log = log_path.read_text(errors="replace") if log_path.exists() else ""
record = {
    "date": "2026-10-09",
    "mode": "static_source_assurance_and_build_log_inspection",
    "not_a_Lean_or_mathematical_proof_check": True,
    "files": [{"file": p.relative_to(ROOT).as_posix(),
               "bytes": p.stat().st_size,
               "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],
    "source_file_count": len(sources),
    "label_count": len(labels),
    "reference_count": len(refs),
    "duplicate_labels": {key: locs for key, locs in labels.items() if len(locs) > 1},
    "unresolved_labels": [ref for ref in refs if ref["label"] not in labels],
    "citation_keys": sorted(set(cites)),
    "bibliography_key_count": len(bibitems),
    "missing_citation_keys": sorted(set(cites) - set(bibitems)),
    "duplicate_bibliography_keys": sorted({key for key in bibitems if bibitems.count(key) > 1}),
    "inputs": inputs,
    "missing_inputs": [item for item in inputs if not item["exists"]],
    "graphics": graphics,
    "missing_graphics": [item for item in graphics if not item["exists"]],
    "environment_checks": environment_checks,
    "environment_problems": [item for item in environment_checks if item["mismatches"] or item["unclosed"]],
    "literal_backslash_n_insertions": literal_newline_tokens,
    "reader_pdf": {"exists": pdf_path.is_file(),
                   "bytes": pdf_path.stat().st_size if pdf_path.is_file() else None,
                   "sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest() if pdf_path.is_file() else None},
    "build_log": {"exists": log_path.is_file(),
                  "sha256": hashlib.sha256(log_path.read_bytes()).hexdigest() if log_path.is_file() else None,
                  "output_line": next((line for line in log.splitlines() if line.startswith("Output written")), None),
                  "undefined_reference_or_citation": bool(re.search(r"(?:Reference|Citation).*undefined|There were undefined", log)),
                  "multiply_defined": "multiply defined" in log,
                  "missing_character": "Missing character" in log,
                  "fatal_error": "Fatal error" in log,
                  "overfull_lines": [line for line in log.splitlines() if "Overfull" in line]},
}
output = ROOT / "evidence/reader_source_assurance.json"
output.write_text(json.dumps(record, indent=2) + "\n")
keys = ["source_file_count", "label_count", "reference_count", "bibliography_key_count",
        "duplicate_labels", "unresolved_labels", "missing_citation_keys", "missing_inputs",
        "missing_graphics", "environment_problems", "literal_backslash_n_insertions", "build_log"]
print(json.dumps({key: record[key] for key in keys}, indent=2))
