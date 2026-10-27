from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX_PATH = ROOT / "Hypergraph_Lumpability_Bayesian_Refinement.tex"
LOG_PATH = ROOT / "Hypergraph_Lumpability_Bayesian_Refinement.log"
RESULT_PATH = ROOT / "results" / "verification.json"
OUTPUT_PATH = ROOT / "results" / "manuscript_audit.json"
EXPECTED_VERSION = "0.1.4"
PROOF_ENVIRONMENTS = ("theorem", "proposition", "lemma", "corollary")
SKIP_ENVIRONMENTS = {
    "equation",
    "equation*",
    "align",
    "align*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "array",
    "cases",
    "split",
    "tabular",
    "tabularx",
    "longtable",
    "lstlisting",
    "verbatim",
    "thebibliography",
}


def strip_tex_comments(text: str) -> str:
    """Remove unescaped TeX comments while preserving line structure."""

    cleaned: list[str] = []
    for line in text.splitlines():
        cut = len(line)
        for index, char in enumerate(line):
            if char != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                cut = index
                break
        cleaned.append(line[:cut])
    return "\n".join(cleaned)


def add_check(checks: list[dict[str, object]], check_id: str, passed: bool, detail: object) -> None:
    checks.append(
        {
            "id": check_id,
            "status": "PASS" if passed else "FAIL",
            "detail": detail,
        }
    )


def theorem_proof_audit(tex: str) -> tuple[int, list[dict[str, object]]]:
    env_union = "|".join(PROOF_ENVIRONMENTS)
    begin_pattern = re.compile(rf"\\begin\{{({env_union})\}}")
    section_pattern = re.compile(r"\\(?:part|section|subsection|subsubsection)\*?\{")
    end_document_pattern = re.compile(r"\\end\{document\}")
    statements = list(begin_pattern.finditer(tex))
    missing: list[dict[str, object]] = []

    for index, statement in enumerate(statements):
        env = statement.group(1)
        end_marker = f"\\end{{{env}}}"
        end_position = tex.find(end_marker, statement.end())
        if end_position < 0:
            missing.append(
                {
                    "environment": env,
                    "line": tex.count("\n", 0, statement.start()) + 1,
                    "reason": "missing environment terminator",
                }
            )
            continue
        segment_start = end_position + len(end_marker)
        boundaries = [len(tex)]
        if index + 1 < len(statements):
            boundaries.append(statements[index + 1].start())
        section_match = section_pattern.search(tex, segment_start)
        if section_match:
            boundaries.append(section_match.start())
        document_match = end_document_pattern.search(tex, segment_start)
        if document_match:
            boundaries.append(document_match.start())
        segment = tex[segment_start : min(boundaries)]
        if "\\begin{proof}" not in segment:
            missing.append(
                {
                    "environment": env,
                    "line": tex.count("\n", 0, statement.start()) + 1,
                    "reason": "no proof before the next statement or section",
                }
            )
    return len(statements), missing


def _remove_inline_math(text: str) -> str:
    """Remove ordinary inline math while preserving surrounding prose."""

    return re.sub(r"(?<!\\)\$(?:\\.|[^$])*?(?<!\\)\$", " MATH ", text)


def _clean_prose_fragment(fragment: str) -> str:
    """Reduce one TeX fragment to visible prose for style checks."""

    text = _remove_inline_math(fragment)
    text = re.sub(
        r"\\texorpdfstring\{([^{}]*)\}\{[^{}]*\}",
        r"\1",
        text,
    )
    text = re.sub(
        r"\\(?:label|ref|eqref|Cref|cref|cite|pageref|url|href|includegraphics|input)"
        r"(?:\[[^\]]*\])?\{[^{}]*\}(?:\{[^{}]*\})?",
        " ",
        text,
    )
    text = re.sub(r"\\texttt\{[^{}]*\}", " ", text)
    for _ in range(4):
        text = re.sub(
            r"\\(?:textbf|emph|textit|mathrm|mathsf|operatorname|mbox)\{([^{}]*)\}",
            r"\1",
            text,
        )
    text = re.sub(r"\\begin\{[^{}]*\}(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"\\end\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace(r"\&", "&").replace(r"\%", "%").replace("~", " ")
    text = re.sub(r"[{}\\]", " ", text)
    return " ".join(text.split())


def extract_prose_lines(tex: str) -> list[dict[str, object]]:
    """Return line numbered visible prose outside math, code, tables, and references."""

    lines = tex.splitlines()
    stack: list[str] = []
    in_display = False
    body_started = False
    prose: list[dict[str, object]] = []

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line
        if not body_started:
            if r"\begin{document}" in line:
                body_started = True
            continue
        if r"\end{document}" in line:
            break
        begins = re.findall(r"\\begin\{([^{}]+)\}", line)
        ends = re.findall(r"\\end\{([^{}]+)\}", line)
        skip = any(env in SKIP_ENVIRONMENTS for env in stack)

        scan = line
        if in_display:
            if r"\]" in scan:
                scan = scan.split(r"\]", 1)[1]
                in_display = False
            else:
                scan = ""
        while r"\[" in scan:
            before, after = scan.split(r"\[", 1)
            if r"\]" in after:
                after = after.split(r"\]", 1)[1]
                scan = before + " " + after
            else:
                scan = before
                in_display = True
                break

        if not skip and scan.strip():
            cleaned = _clean_prose_fragment(scan)
            if re.search(r"[A-Za-z]", cleaned):
                prose.append({"line": line_number, "text": cleaned})

        for env in begins:
            stack.append(env)
        for env in ends:
            if env in stack:
                reverse_index = stack[::-1].index(env)
                stack.pop(len(stack) - 1 - reverse_index)

    return prose


def prose_style_findings(prose: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    semicolons: list[dict[str, object]] = []
    dashes: list[dict[str, object]] = []
    word_hyphen = re.compile(r"\b[A-Za-z]{2,}-[A-Za-z]{2,}\b")

    for row in prose:
        text = str(row["text"])
        if ";" in text:
            semicolons.append(row)
        if (
            "--" in text
            or "–" in text
            or "—" in text
            or word_hyphen.search(text)
            or re.search(r"\s-\s", text)
        ):
            dashes.append(row)
    return semicolons, dashes


def reference_whitespace_findings(tex: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    pattern = re.compile(r"\\(label|ref|eqref|Cref|cref)\{([^{}]+)\}")
    for match in pattern.finditer(tex):
        argument = match.group(2)
        if re.search(r"\s", argument):
            findings.append(
                {
                    "line": tex.count("\n", 0, match.start()) + 1,
                    "command": match.group(1),
                    "argument": argument,
                }
            )
    return findings


def main() -> int:
    raw_tex = TEX_PATH.read_text(encoding="utf-8")
    tex = strip_tex_comments(raw_tex)
    checks: list[dict[str, object]] = []

    statement_count, missing_proofs = theorem_proof_audit(tex)
    add_check(
        checks,
        "AUD-PROOFS",
        not missing_proofs,
        {
            "statement_count": statement_count,
            "missing_proof_count": len(missing_proofs),
            "missing": missing_proofs,
        },
    )

    required_markers = {
        "AUD-ANALYTIC-SUMMABILITY": r"\label{eq:fine-normal-summability}",
        "AUD-NORMALIZATION-MAX": r"{\max\{\one^Tu,\one^Tv\}}",
        "AUD-LIKELIHOOD-POSITIVITY": r"\abs{\eta}<\lambda_1^{\coarse}",
        "AUD-INTERNAL-COMPLETE": "complete for internal use",
        "AUD-EXTERNAL-REVIEW-PENDING": "independent proof review",
        "AUD-PRIORITY-REVIEW-PENDING": "historical priority",
        "AUD-EVIDENCE-INITIAL": r"\mu_0^{\coarse}=C\mu_0^{\fine}",
        "AUD-SEQUENCE-EVIDENCE": r"Z_{1:N}^{\fine}=\prod_{k=1}^N z_k^{\fine}",
        "AUD-TOLERANCE-BOUNDARY": "A positive numerical tolerance produces an approximate certificate rather than an exact algebraic decision.",
        "AUD-TOTAL-DEFECT": r"\Delta_m^{\mathrm{total}}",
        "AUD-FIBER-OSCILLATION-SCOPE": r"When $q\geq2$ and commutation is required for every interior prior",
        "AUD-EVIDENCE-PROBABILITY": r"Assume $\widehat\mu_k^{\fine}$ is a probability vector.",
        "AUD-HMM-COMPOSITION": r"\Bup_{\lambda_{y_N}^{\fine}}\circ M_{\fine}",
    }
    lowered = tex.lower()
    for check_id, marker in required_markers.items():
        haystack = lowered if marker == marker.lower() and "\\" not in marker else tex
        needle = marker.lower() if haystack is lowered else marker
        add_check(checks, check_id, needle in haystack, marker)

    version_sources = {
        "VERSION": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "pyproject.toml": re.search(
            r'^version\s*=\s*"([^"]+)"',
            (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        ).group(1),
        "src/priq/__init__.py": re.search(
            r'^__version__\s*=\s*"([^"]+)"',
            (ROOT / "src" / "priq" / "__init__.py").read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        ).group(1),
        "manuscript": re.search(
            r"version\s+([0-9]+\.[0-9]+\.[0-9]+)",
            raw_tex,
            flags=re.IGNORECASE,
        ).group(1),
    }
    add_check(
        checks,
        "AUD-VERSION",
        all(value == EXPECTED_VERSION for value in version_sources.values()),
        version_sources,
    )

    verification = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    add_check(
        checks,
        "AUD-CERTIFICATES",
        verification.get("version") == EXPECTED_VERSION and verification.get("fail_count") == 0,
        {
            "version": verification.get("version"),
            "pass_count": verification.get("pass_count"),
            "fail_count": verification.get("fail_count"),
        },
    )

    prose = extract_prose_lines(tex)
    semicolon_findings, dash_findings = prose_style_findings(prose)
    add_check(
        checks,
        "AUD-PROSE-SEMICOLONS",
        not semicolon_findings,
        {"finding_count": len(semicolon_findings), "findings": semicolon_findings},
    )
    add_check(
        checks,
        "AUD-PROSE-DASHES",
        not dash_findings,
        {"finding_count": len(dash_findings), "findings": dash_findings},
    )

    repeated_word_findings: list[dict[str, object]] = []
    repeated_pattern = re.compile(r"\b([A-Za-z]+)\s+\1\b", flags=re.IGNORECASE)
    for row in prose:
        match = repeated_pattern.search(str(row["text"]))
        if match:
            repeated_word_findings.append(
                {
                    "line": row["line"],
                    "match": match.group(0),
                    "text": row["text"],
                }
            )
    add_check(
        checks,
        "AUD-REPEATED-WORDS",
        not repeated_word_findings,
        {
            "finding_count": len(repeated_word_findings),
            "findings": repeated_word_findings,
        },
    )

    reference_findings = reference_whitespace_findings(tex)
    add_check(
        checks,
        "AUD-LABEL-WHITESPACE",
        not reference_findings,
        {"finding_count": len(reference_findings), "findings": reference_findings},
    )

    awkward_fragments = (
        "A aggregation",
        "an hypergraph",
        "an coefficient",
        "within each fiber directions",
        "trajectory- or",
        "whether guided",
        "will be used throughout",
        "partition-refinement",
        "output-aggregated",
        "four-state run",
        "omitted-energy",
        "scalar polynomial coefficients",
    )
    awkward_found = [fragment for fragment in awkward_fragments if fragment in tex]
    add_check(
        checks,
        "AUD-PROSE-REGRESSIONS",
        not awkward_found,
        {"forbidden_fragments_found": awkward_found},
    )

    if LOG_PATH.exists():
        log_text = LOG_PATH.read_text(encoding="utf-8", errors="replace")
        forbidden = {
            "LaTeX Error": r"LaTeX Error",
            "Undefined control sequence": r"Undefined control sequence",
            "undefined references": r"There were undefined references|undefined references",
            "undefined citations": r"There were undefined citations|undefined citations",
            "overfull boxes": r"Overfull \\hbox|Overfull \\vbox",
        }
        findings = {
            label: bool(re.search(pattern, log_text, flags=re.IGNORECASE))
            for label, pattern in forbidden.items()
        }
        add_check(checks, "AUD-LATEX-LOG", not any(findings.values()), findings)
    else:
        add_check(checks, "AUD-LATEX-LOG", False, "LaTeX log is missing")

    pass_count = sum(check["status"] == "PASS" for check in checks)
    fail_count = len(checks) - pass_count
    report = {
        "schema": "priq.manuscript-audit.v3",
        "version": EXPECTED_VERSION,
        "status": "PASS" if fail_count == 0 else "FAIL",
        "pass_count": pass_count,
        "fail_count": fail_count,
        "theorem_like_statement_count": statement_count,
        "missing_proof_count": len(missing_proofs),
        "visible_prose_line_count": len(prose),
        "checks": checks,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"manuscript audit: {report['status']} "
        f"({pass_count} passed, {fail_count} failed, "
        f"{statement_count} theorem-like statements, {len(missing_proofs)} missing proofs)"
    )
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
