from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def run(*args: str) -> None:
    subprocess.run(list(args), cwd=ROOT, check=True)


run(sys.executable, "generate_figures.py")
run(sys.executable, "generate_catalog.py")
run(sys.executable, "-m", "pytest", "-q")
print("Python generation and tests completed.")
