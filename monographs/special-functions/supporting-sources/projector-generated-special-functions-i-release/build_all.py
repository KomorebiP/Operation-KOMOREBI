from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = "Projector_Generated_Special_Functions_I.tex"


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    source = (ROOT / "projector_generated_special_functions.py").read_text(encoding="utf-8")
    listing = source.replace("Möbius", "Mobius").replace("Báez", "Baez").replace("•", "*")
    (ROOT / "projector_generated_special_functions_listing.py").write_text(listing, encoding="utf-8")
    run([sys.executable, "projector_generated_special_functions.py"])
    run([sys.executable, "generate_tables.py"])
    run([sys.executable, "-m", "pytest", "-q"])
    for _ in range(3):
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", TEX])
    print(f"Built {ROOT / TEX.replace('.tex', '.pdf')}")


if __name__ == "__main__":
    main()
