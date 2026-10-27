#!/usr/bin/env python3
"""Build the complete PDF from canonical proof notes and curated visual chapters.

Pandoc conversion is followed by typography-only transformations: breakable
paths/URLs and search phrases, a display equation, and breakable table entries.
The canonical Markdown proofs are never changed by this builder.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent
CHAPTERS = [
    ("dilation_type", "dilation_full"),
    ("arithmetic_inverse", "arithmetic_full"),
    ("multi_prime_sieve", "sieve_full"),
    ("spectral_continuation", "spectral_full"),
    ("sequence_polyphase", "sequence_full"),
]


def format_tex(text, chapter):
    # LaTeX already numbers the appendix sections; do not duplicate Markdown's
    # editorial title prefixes in their visible headings.
    text = re.sub(r"(\\(?:sub)?section\{)\d+\.\s+", r"\1", text)
    def code(match):
        body = match.group(1)
        if r"\ " in body:
            return r"\texttt{\small " + body.replace(r"\ ", " ") + "}"
        if "/" in body or r"\_" in body:
            return r"\path{" + body.replace(r"\_", "_") + "}"
        return match.group(0)
    text = re.sub(r"\\texttt\{([^{}]+)\}", code, text)
    text = text.replace(r"\textasciitilde elkies", "~elkies")
    def url(match):
        body = match.group(0)
        suffix = "." if body.endswith(".") else ""
        if suffix:
            body = body[:-1]
        return r"\url{" + body.replace(r"\_", "_") + "}" + suffix
    text = re.sub(r"https?://[^\s{}]+", url, text)
    if chapter == "dilation_type":
        old = r"and \(R f_Q'(R)-f_Q(R)=2\sum_{n\ge0}n d_n(Q)R^{2n+1}\), proving the"
        new = r"and" + "\n" + r"\[R f_Q'(R)-f_Q(R)=2\sum_{n\ge0}n d_n(Q)R^{2n+1},\]" + "\nproving the"
        assert old in text
        text = text.replace(old, new)
    if chapter == "sequence_polyphase":
        # A comma-separated tuple in the middle table column must wrap.
        text = re.sub(r" & \\\(([^\n]+?,[^\n]+?)\\\) &",
                      lambda m: " & " + ", ".join(r"\(" + x + r"\)" for x in m.group(1).split(",")) + " &",
                      text)
    return text


def main():
    record = {"purpose": "Typography-only conversion of frozen proof notes", "chapters": [],
              "pandoc_version": subprocess.run(["pandoc", "--version"], check=True,
                                               capture_output=True, text=True).stdout.splitlines()[0],
              "pdflatex_version": subprocess.run(["pdflatex", "--version"], check=True,
                                                  capture_output=True, text=True).stdout.splitlines()[0]}
    for src, dst in CHAPTERS:
        source = ROOT / "new_results" / (src + ".md")
        target = ROOT / "sections" / (dst + ".tex")
        result = subprocess.run(["pandoc", "-f", "markdown+tex_math_single_backslash",
                                 "-t", "latex", "--no-highlight", str(source)],
                                check=True, capture_output=True, text=True)
        target.write_text(format_tex(result.stdout, src))
        record["chapters"].append({"source": str(source.relative_to(ROOT)),
                                  "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                                  "output": str(target.relative_to(ROOT)),
                                  "output_sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    for pass_number in (1, 2, 3):
        result = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                                cwd=ROOT, capture_output=True, text=True)
        (ROOT / "evidence" / f"latex-pass-{pass_number}.txt").write_text(result.stdout + result.stderr)
        result.check_returncode()
    record["main_tex_sha256"] = hashlib.sha256((ROOT / "main.tex").read_bytes()).hexdigest()
    record["main_pdf_sha256"] = hashlib.sha256((ROOT / "main.pdf").read_bytes()).hexdigest()
    (ROOT / "evidence" / "manuscript_build.json").write_text(json.dumps(record, indent=2) + "\n")
    warnings = [line for line in (ROOT / "main.log").read_text().splitlines()
                if "Overfull" in line or "Warning:" in line]
    print(json.dumps({"built": "main.pdf", "warnings": warnings}))


if __name__ == "__main__":
    main()
