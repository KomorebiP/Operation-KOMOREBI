#!/usr/bin/env python3
"""Bounded lexical LaTeX validation, not a TeX compiler or proof checker."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "source/Projector_Resolved_Seed_Calculus_X_Block25_Amended.tex"
original = PATH.read_text()


def escaped(text, index):
    count = 0
    while index > 0 and text[index - 1] == "\\":
        count += 1
        index -= 1
    return count % 2 == 1


lines = []
for line in original.splitlines():
    cutoff = next((i for i, c in enumerate(line) if c == "%" and not escaped(line, i)), len(line))
    lines.append(line[:cutoff])
text = "\n".join(lines)
text = re.sub(r"(\\begin\{(?:lstlisting|verbatim)\})(.*?)(\\end\{(?:lstlisting|verbatim)\})",
              lambda m: m[1] + "\n" * m[2].count("\n") + m[3], text, flags=re.S)

errors = []
brace_depth = 0
for i, char in enumerate(text):
    if char in "{}" and not escaped(text, i):
        brace_depth += 1 if char == "{" else -1
        if brace_depth < 0:
            errors.append("Closing brace without opening brace")
            break
if brace_depth:
    errors.append(f"Final brace depth {brace_depth}")

stack = []
environments = []
for match in re.finditer(r"\\(begin|end)\{([^{}]+)\}", text):
    command, environment = match.groups()
    if command == "begin":
        stack.append(environment)
        environments.append(environment)
    elif not stack or stack.pop() != environment:
        errors.append(f"Mismatched environment: {environment}")
if stack:
    errors.append(f"Unclosed environments: {stack}")

delimiter_counts = {token: sum(not escaped(text, match.start())
                               for match in re.finditer(re.escape(token), text))
                    for token in [r"\[", r"\]", r"\(", r"\)"]}
if delimiter_counts[r"\["] != delimiter_counts[r"\]"]:
    errors.append("Unequal display-math delimiter counts")
if delimiter_counts[r"\("] != delimiter_counts[r"\)"]:
    errors.append("Unequal inline-math delimiter counts")
dollars = sum(char == "$" and not escaped(text, i) for i, char in enumerate(text))
if dollars % 2:
    errors.append("Odd count of unescaped dollar delimiters")

labels = re.findall(r"\\label\{([^{}]+)\}", text)
duplicates = sorted({label for label in labels if labels.count(label) > 1})
references = [key.strip()
              for group in re.findall(r"\\(?:ref|eqref|cref|Cref|autoref)\*?\{([^{}]+)\}", text)
              for key in group.split(",")]
missing_references = sorted(set(references) - set(labels))
bibitems = re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^{}]+)\}", text)
citations = [key.strip()
             for group in re.findall(r"\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{([^{}]+)\}", text)
             for key in group.split(",")]
missing_citations = sorted(set(citations) - set(bibitems))
if duplicates:
    errors.append(f"Duplicate labels: {duplicates}")
if missing_references:
    errors.append(f"Unresolved local references: {missing_references}")
if missing_citations:
    errors.append(f"Unresolved local citations: {missing_citations}")

result = {
    "scope": "Lexical brace, environment, delimiter, label/reference and local citation checks",
    "tex_compiler_run": False,
    "pdf_typeset": False,
    "source": str(PATH.relative_to(ROOT)),
    "source_sha256": hashlib.sha256(PATH.read_bytes()).hexdigest(),
    "environments": len(environments),
    "delimiter_counts": delimiter_counts,
    "unescaped_dollars": dollars,
    "labels": len(labels),
    "references": len(references),
    "bibitems": len(bibitems),
    "citations": len(citations),
    "errors": errors,
    "passed": not errors,
}
(ROOT / "proofreading_structure.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
raise SystemExit(bool(errors))
