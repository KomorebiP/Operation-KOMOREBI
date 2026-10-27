from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "2.1.0"


def main() -> int:
    errors: list[str] = []
    required = [
        "README.md",
        "LICENSE",
        "CITATION.cff",
        "pyproject.toml",
        "src/komorebi_pr_lasm/__init__.py",
        "src/komorebi_arc3_offline/__init__.py",
        ".github/workflows/ci.yml",
        "paper/Projector_Resolved_Large_Algebraic_Signal_Model.pdf",
    ]
    for name in required:
        if not (ROOT / name).exists():
            errors.append(f"missing required path: {name}")

    for name in [
        "pyproject.toml",
        "CITATION.cff",
        "src/komorebi_pr_lasm/__init__.py",
        "src/komorebi_arc3_offline/__init__.py",
    ]:
        text = (ROOT / name).read_text(encoding="utf-8")
        if EXPECTED_VERSION not in text:
            errors.append(f"version {EXPECTED_VERSION} not found in {name}")

    prohibited = [".env", "results", "recordings", "dist"]
    present = [name for name in prohibited if (ROOT / name).exists()]
    if present:
        errors.append(f"generated or sensitive paths present: {present}")

    result = {"ok": not errors, "version": EXPECTED_VERSION, "errors": errors}
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
