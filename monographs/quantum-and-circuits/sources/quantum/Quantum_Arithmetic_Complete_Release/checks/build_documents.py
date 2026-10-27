#!/usr/bin/env python3
"""Build the three publication companions with pinned source inputs unchanged."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import hashlib
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "traditional": ("Quantum_Arithmetic_Traditional.tex", "Komorebi_Quantum_Arithmetic_Traditional_Paper"),
    "visual": ("Quantum_Arithmetic_Visual.tex", "Komorebi_Quantum_Arithmetic_Visual_Guide"),
    "lean": ("Quantum_Arithmetic_Lean.tex", "Komorebi_Quantum_Arithmetic_Lean_Guide"),
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("documents", nargs="*", choices=list(DOCS))
    args = parser.parse_args()
    selected = args.documents or list(DOCS)
    prior_report = ROOT / "verification" / "document_build" / "BUILD_REPORT.json"
    records = []
    if prior_report.exists():
        records = [r for r in json.loads(prior_report.read_text())["documents"] if r["document"] not in selected]
    (ROOT / "output").mkdir(exist_ok=True)
    for kind in selected:
        source, stem = DOCS[kind]
        build = ROOT / "verification" / "document_build" / kind
        build.mkdir(parents=True, exist_ok=True)
        command = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", f"-output-directory={build}", f"-jobname={stem}", source]
        for n in range(1, 4):
            run = subprocess.run(command, cwd=ROOT / kind, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
            (build / f"pass_{n}.txt").write_text(run.stdout)
            if run.returncode:
                print(run.stdout[-6000:])
                raise SystemExit(f"{kind}: LaTeX pass {n} failed ({run.returncode})")
        pdf = ROOT / "output" / f"{stem}.pdf"
        shutil.copyfile(build / pdf.name, pdf)
        log = (build / f"{stem}.log").read_text(errors="replace")
        warnings = [line for line in log.splitlines() if any(token in line for token in ("Overfull", "Underfull", "Warning:", "Missing character"))]
        records.append({"document": kind, "file": str(pdf.relative_to(ROOT)), "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "bytes": pdf.stat().st_size, "warnings": warnings, "passes": 3, "command": command})
        print(f"{kind}: {pdf.stat().st_size:,} bytes; {len(warnings)} layout/log messages")
    records.sort(key=lambda r: list(DOCS).index(r["document"]))
    manifest = {"built_at_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS", "documents": records, "note": "Document compilation is not Lean compilation."}
    (ROOT / "verification" / "document_build" / "BUILD_REPORT.json").write_text(json.dumps(manifest, indent=2) + "\n")

if __name__ == "__main__":
    main()
