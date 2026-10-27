#!/usr/bin/env python3
"""Build the monograph from its editable source; no network access is required."""
from pathlib import Path
import re
import shutil
import subprocess
import sys

def main() -> int:
    root = Path(__file__).resolve().parent
    engine = shutil.which("xelatex")
    if engine is None:
        print("XeLaTeX was not found. Install TeX Live or MiKTeX, then rerun.", file=sys.stderr)
        return 1
    output = root / "build"
    output.mkdir(exist_ok=True)
    command = [engine, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
               "-jobname=Special_Functions_Monograph", "-output-directory=" + str(output), "main.tex"]
    for iteration in range(1, 4):
        try:
            result = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=180)
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"Build failed: {error}", file=sys.stderr)
            return 1
        (output / f"pass_{iteration}.txt").write_text(result.stdout, encoding="utf-8")
        if result.returncode:
            print(result.stdout[-10000:], file=sys.stderr)
            return result.returncode
    log = (output / "Special_Functions_Monograph.log").read_text(encoding="utf-8", errors="replace")
    patterns = (r"Overfull ", r"Undefined control sequence", r"Missing character:",
                r"There were undefined references", r"Font Warning:")
    problems = [pattern for pattern in patterns if re.search(pattern, log)]
    if problems:
        print("Review required: " + ", ".join(problems), file=sys.stderr)
        return 2
    print(output / "Special_Functions_Monograph.pdf")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
