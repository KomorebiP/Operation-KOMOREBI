from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAPER = ROOT / "Projector_Generated_Special_Functions_II.tex"
PDF = ROOT / "Projector_Generated_Special_Functions_II.pdf"


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    run([sys.executable, "projector_generated_special_functions_ii.py", "--base", "."])
    run([sys.executable, "generate_tables.py"])
    run([sys.executable, "-m", "pytest", "-q"])
    if shutil.which("pdflatex") is None:
        raise SystemExit("pdflatex was not found. Install a TeX distribution before building the paper.")
    for _ in range(3):
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", PAPER.name])
    if not PDF.exists():
        raise SystemExit("The PDF build did not create the expected file.")
    summary = json.loads((ROOT / "results" / "results.json").read_text())
    print(json.dumps({"pdf": PDF.name, "pages": _pdf_pages(PDF), **summary}, indent=2))


def _pdf_pages(path: Path) -> int | None:
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    return None


if __name__ == "__main__":
    main()
