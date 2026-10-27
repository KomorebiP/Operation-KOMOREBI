#!/usr/bin/env python3
"""Build the three publication PDFs with the supplied LaTeX sources."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BOOKS = {"monograph": "Komorebi_Space_Monograph", "visual": "Komorebi_Space_Visual_Guide", "lean": "Komorebi_Space_Lean_Guide"}

def source_hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "source").rglob("*")) if p.is_file()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", choices=[*BOOKS, "all"], default="all")
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "books")
    args = parser.parse_args()
    if not shutil.which("pdflatex"):
        parser.error("pdflatex is required (TeX Live with the packages used in source/preamble.tex)")
    output = args.output.resolve()
    before = source_hashes()
    results = []
    output.mkdir(parents=True, exist_ok=True)
    for key, stem in BOOKS.items():
        if args.book not in (key, "all"):
            continue
        dest = output / key
        dest.mkdir(parents=True, exist_ok=True)
        command = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-recorder", "-output-directory=" + str(dest), stem + ".tex"]
        item = {"book": key, "command": command, "passes": []}
        results.append(item)
        for number in range(1, 4):
            with (dest / f"pass{number}.console.log").open("wb") as log:
                run = subprocess.run(command, cwd=ROOT / "source", stdout=log, stderr=subprocess.STDOUT)
            item["passes"].append({"pass": number, "exit_code": run.returncode})
            if run.returncode:
                (output / "build_report.json").write_text(json.dumps({"results": results, "source_hashes": before}, indent=2) + "\n")
                raise SystemExit(f"LaTeX failed for {key}; see {dest / f'pass{number}.console.log'}")
        final_log = (dest / (stem + ".log")).read_text(errors="replace")
        item["layout_warnings"] = [line for line in final_log.splitlines() if re.search(r"Overfull|undefined|multiply defined|Rerun to get|Missing character", line)]
        pdf = dest / (stem + ".pdf")
        item["pdf_sha256"] = hashlib.sha256(pdf.read_bytes()).hexdigest()
        print(pdf)
    unchanged = before == source_hashes()
    (output / "build_report.json").write_text(json.dumps({"source_unchanged": unchanged, "source_hashes": before, "results": results}, indent=2) + "\n")
    if not unchanged:
        raise SystemExit("Sources changed while the books were being built; rebuild from a frozen source tree.")
    if any(item["layout_warnings"] for item in results):
        raise SystemExit("Inspect layout/reference warnings in build_report.json.")

if __name__ == "__main__":
    main()
