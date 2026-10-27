"""Build the expanded conjecture monographs and their separate visual guides."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--figures", action="store_true")
parser.add_argument("--only", choices=["collatz", "riemann", "collatz_visual", "riemann_visual"])
args = parser.parse_args()
if args.figures:
    subprocess.run([sys.executable, str(ROOT / "shared" / "figures.py")], check=True)
    for guide in ["collatz_visual", "riemann_visual"]:
        subprocess.run([sys.executable, str(ROOT / guide / "figures.py")], check=True)
outdir = ROOT / "pdf"
outdir.mkdir(exist_ok=True)
names = {
    "collatz": "Komorebi_Collatz_Conjecture_Piece_v1.1.pdf",
    "riemann": "Komorebi_Riemann_Conjecture_Piece_v1.1.pdf",
    "collatz_visual": "Komorebi_Collatz_Visual_Guide_v1.1.pdf",
    "riemann_visual": "Komorebi_Riemann_Visual_Guide_v1.1.pdf",
}
for name in ([args.only] if args.only else names):
    folder = ROOT / name
    for _ in range(2):
        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            cwd=folder, text=True, capture_output=True,
        )
        (folder / "build_stdout.log").write_text(proc.stdout + proc.stderr)
        if proc.returncode:
            print(proc.stdout[-7000:], file=sys.stderr)
            raise SystemExit(proc.returncode)
    dest = outdir / names[name]
    shutil.copyfile(folder / "main.pdf", dest)
    print(dest)
