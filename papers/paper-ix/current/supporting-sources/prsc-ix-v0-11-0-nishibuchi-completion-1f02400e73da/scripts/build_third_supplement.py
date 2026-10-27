#!/usr/bin/env python3
"""Build the third mathematical supplement. Author: Komorebi P."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / "docs/Paper_IX_Third_Lean_Block_Supplement.tex"
    out = args.output_dir or root / "verification/third_pdf_build"
    out.mkdir(parents=True, exist_ok=True)
    if not shutil.which("pdflatex"):
        print("pdflatex is required", file=sys.stderr)
        return 2
    try:
        for i in range(1, 3):
            result = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                 "-output-directory", str(out.resolve()), str(source.resolve())],
                 cwd=source.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                 timeout=120)
            (out / f"pass_{i}.log").write_bytes(result.stdout)
            if result.returncode:
                sys.stderr.buffer.write(result.stdout)
                return result.returncode
        pdf = out / source.with_suffix(".pdf").name
        shutil.copy2(pdf, source.with_suffix(".pdf"))
        print(source.with_suffix(".pdf"))
        return 0
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
