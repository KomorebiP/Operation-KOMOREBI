#!/usr/bin/env python3
"""Build the sixteen physics manuscripts with XeLaTeX; no Lean execution."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    "Physics_Foundations_Monograph",
    "Physics_Foundations_Visual_Atlas",
    "Physics_Foundations_Lean_Companion",
    "Physics_Dirac_Monograph",
    "Physics_Visual_Atlas",
    "Physics_Lean_Companion",
    "Physics_Gauge_Monograph",
    "Physics_Gauge_Visual_Atlas",
    "Physics_Gauge_Lean_Companion",
    "Physics_Gravity_Monograph",
    "Physics_Gravity_Visual_Atlas",
    "Physics_Gravity_Verification_Companion",
    "Physics_Adic_Monograph",
    "Physics_Adic_Visual_Atlas",
    "Physics_Adic_Verification_Companion",
    "Physics_Collection_Guide",
)


def main():
    engine = shutil.which("xelatex")
    if engine is None:
        sys.exit("XeLaTeX is required. Install TeX Live or MiKTeX and add xelatex to PATH.")
    (ROOT / "pdfs").mkdir(exist_ok=True)
    logs = ROOT / "build_logs"
    logs.mkdir(exist_ok=True)
    names = tuple(sys.argv[1:]) or NAMES
    unknown = set(names) - set(NAMES)
    if unknown:
        sys.exit("Unknown document: " + ", ".join(sorted(unknown)))
    for name in names:
        for pass_number in range(1, 4):
            log = logs / f"{name}_pass_{pass_number}.txt"
            with log.open("w", encoding="utf-8") as output:
                result = subprocess.run(
                    [engine, "-interaction=nonstopmode", "-halt-on-error", name + ".tex"],
                    cwd=ROOT / "source", stdout=output, stderr=subprocess.STDOUT,
                )
            if result.returncode:
                sys.exit(f"Build failed: {name}, pass {pass_number}. See {log}")
        shutil.copy2(ROOT / "source" / (name + ".pdf"), ROOT / "pdfs" / (name + ".pdf"))
        print(f"Built pdfs/{name}.pdf")


if __name__ == "__main__":
    main()
