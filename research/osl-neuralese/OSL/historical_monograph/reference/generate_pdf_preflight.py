#!/usr/bin/env python3
"""Emit deterministic structural preflight information for the v0.5 PDF."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from osl_model import digest


def run(*args: str) -> str:
    return subprocess.run(args, text=True, capture_output=True, check=True).stdout


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    pdf = root / "operator_symbolic_ai_language_v0.5.pdf"
    log = root / "operator_symbolic_ai_language_v0.5.log"
    info = run("pdfinfo", str(pdf))
    pages_match = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    encrypted_match = re.search(r"^Encrypted:\s+(\S+)$", info, re.MULTILINE)
    pages = int(pages_match.group(1)) if pages_match else -1
    encrypted = encrypted_match.group(1) if encrypted_match else "unknown"
    fonts = run("pdffonts", str(pdf)).splitlines()[2:]
    all_embedded = all((line.split()[4] == "yes") for line in fonts if line.split())
    text = run("pdftotext", str(pdf), "-")
    log_text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    bad_patterns = {
        "overfull": bool(re.search(r"Overfull", log_text)),
        "undefined_references": bool(re.search(r"undefined references", log_text, re.I)),
        "multiply_defined": bool(re.search(r"multiply defined", log_text, re.I)),
    }
    payload = {
        "schema": "operator-symbolic-ai.pdf-preflight.v1",
        "pdf": pdf.name,
        "pages": pages,
        "encrypted": encrypted,
        "font_rows": len(fonts),
        "all_fonts_embedded": all_embedded,
        "title_present": "Operator-Symbolic Languages for Artificial Intelligence" in text,
        "language_present": "OSL-Core 0.3" in text,
        "bad_log_patterns": bad_patterns,
        "all_checks_pass": pdf.is_file() and pages >= 80 and encrypted == "no" and all_embedded and not any(bad_patterns.values()),
    }
    payload["report_digest"] = digest(payload)
    (root / "PDF_PREFLIGHT.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
