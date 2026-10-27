"""Build the theorem reference with an installed pdfLaTeX (no network access)."""
from pathlib import Path
import shutil
import subprocess
import sys


def main() -> int:
    root = Path(__file__).resolve().parent
    engine = shutil.which("pdflatex")
    if engine is None:
        print("pdflatex was not found. Install a TeX distribution with the packages listed in the source.", file=sys.stderr)
        return 2
    out = root / "build"
    out.mkdir(exist_ok=True)
    for step in range(1, 4):
        log = out / f"pass-{step}.log"
        try:
            with log.open("w", encoding="utf-8") as stream:
                run = subprocess.run([engine, "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={out}", "theorems.tex"], cwd=root, stdout=stream, stderr=subprocess.STDOUT, timeout=120, check=False)
        except subprocess.TimeoutExpired:
            print(f"Compilation timed out. Inspect {log}", file=sys.stderr)
            return 1
        if run.returncode:
            print(f"Compilation failed. Inspect {log}", file=sys.stderr)
            return run.returncode
    print(out / "theorems.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
