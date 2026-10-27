from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


if __name__ == "__main__":
    run(sys.executable, "projector_generated_special_functions_iii.py")
    run(sys.executable, "generate_tables.py")
    run(sys.executable, "-m", "pytest", "-q")
    for _ in range(3):
        run("pdflatex", "-interaction=nonstopmode", "-halt-on-error", "Projector_Generated_Special_Functions_III.tex")
    print(ROOT / "Projector_Generated_Special_Functions_III.pdf")
