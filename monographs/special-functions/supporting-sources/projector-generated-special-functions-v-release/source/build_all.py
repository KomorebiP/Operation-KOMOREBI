from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    run([sys.executable, "projector_generated_special_functions_v.py"])
    run([sys.executable, "-m", "pytest", "-q"])
    for _ in range(3):
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "Projector_Generated_Special_Functions_V.tex"])


if __name__ == "__main__":
    main()
