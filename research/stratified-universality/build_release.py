#!/usr/bin/env python3
"""Compile the three final documents without rewriting inherited evidence."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
DOCUMENTS = (
    ("traditional", "Stratified_Universality_Traditional.tex"),
    ("visual", "Stratified_Universality_Visual_Guide.tex"),
    ("lean", "Stratified_Universality_Lean_Guide.tex"),
)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document", choices=["all", "traditional", "visual", "lean"], default="all")
    args = parser.parse_args()
    tex = shutil.which("pdflatex")
    if tex is None:
        raise SystemExit("pdflatex is required; install the documented TeX dependencies first.")
    logs = ROOT / "build_logs"
    logs.mkdir(exist_ok=True)
    for folder, name in DOCUMENTS:
        if args.document not in ("all", folder):
            continue
        source = ROOT / folder / name
        if not source.is_file():
            raise SystemExit(f"Missing final document source: {source}")
        for run in range(1, 4):
            with (logs / f"{source.stem}_pass{run}.txt").open("wb") as log:
                result = subprocess.run(
                    [tex, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", name],
                    cwd=source.parent, stdout=log, stderr=subprocess.STDOUT,
                )
            if result.returncode:
                raise SystemExit(f"Build failed for {name}, pass {run}; inspect build_logs.")
        print(f"Built {folder}/{source.stem}.pdf")
    print("Document compilation does not rerun Python regression suites or certify Lean proofs.")

if __name__ == "__main__":
    main()
