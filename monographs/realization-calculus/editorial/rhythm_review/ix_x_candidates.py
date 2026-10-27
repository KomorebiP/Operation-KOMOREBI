#!/usr/bin/env python3
"""Inventory rhythm candidates without editing canonical TeX."""
from pathlib import Path
import collections
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "editorial/rhythm_review"
MATH = r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$|(?<!\\)\\\(.*?(?<!\\)\\\)|(?<!\\)\\\[.*?(?<!\\)\\\]|\\begin\{(?:equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|displaymath|math)\}.*?\\end\{(?:equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|displaymath|math)\}"
LITERAL = r"\\begin\{(?:Verbatim|verbatim|lstlisting|minted|alltt|tikzpicture)\}.*?\\end\{(?:Verbatim|verbatim|lstlisting|minted|alltt|tikzpicture)\}"
MACROS = r"\\(?:code|lean|mcode|target|source|path|url|nolinkurl|texttt|VerbatimInput|label|hypertarget|input|include|includegraphics|cite|bibitem|href|ref|eqref|cref|Cref|pageref)\s*(?:\[[^\]]*\])?\{[^{}]*\}"
PATTERNS = {
    "semicolon": r"(?<!\\);",
    "dash": r"—|–|(?<!-)---?(?!-)",
    "hyphenated_word": r"\b[A-Za-z]+(?:-[A-Za-z]+)+\b",
    "formulaic": r"\b(?:It is (?:important|essential|worth)|in order to|The important|The key|This distinction|rather than|not merely|genuine|actually|clearly|for completeness)\b",
}


def blank(match):
    return "".join("\n" if char == "\n" else " " for char in match.group())


def mask(text):
    text = re.sub(r"(?m)(?<!\\)%.*", blank, text)
    text = re.sub(LITERAL, blank, text, flags=re.S)
    text = re.sub(MATH, blank, text, flags=re.S)
    text = re.sub(MACROS, blank, text, flags=re.S)
    text = re.sub(r"\\hyperref\[[^\]]*\]", blank, text)
    doc = text.find(r"\begin{document}")
    if doc >= 0:
        text = "".join("\n" if c == "\n" else " " for c in text[:doc]) + text[doc:]
    return text


def main():
    files = json.loads((ROOT / "editorial/prose_review/ix_x_manifest.json").read_text())
    files = [name for name in files if not name.endswith(("historical_checkpoint_frontmatter.tex", "/preamble.tex"))]
    records, totals, hyphens = [], collections.Counter(), collections.Counter()
    for name in files:
        text = (ROOT / name).read_text()
        clean = mask(text)
        for match in re.finditer(r"\S.*?(?=\n\s*\n|\Z)", clean, flags=re.S):
            paragraph = match.group()
            candidates = {key: [m.group() for m in re.finditer(pattern, paragraph, re.I)] for key, pattern in PATTERNS.items()}
            candidates = {key: values for key, values in candidates.items() if values}
            if not candidates:
                continue
            totals.update({key: len(values) for key, values in candidates.items()})
            hyphens.update(candidates.get("hyphenated_word", []))
            records.append({"file": name, "line": clean[:match.start()].count("\n") + 1,
                            "masked_paragraph": paragraph, "candidates": candidates})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ix_x_candidates.json").write_text(json.dumps({"files": files, "totals": totals, "hyphenated_words": hyphens, "paragraphs": records}, indent=2) + "\n")
    print(json.dumps({"files": len(files), "paragraphs": len(records), "totals": totals, "unique_hyphenated_words": len(hyphens)}, indent=2))


if __name__ == "__main__":
    main()
