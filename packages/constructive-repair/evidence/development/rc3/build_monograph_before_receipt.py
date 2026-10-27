#!/usr/bin/env python3
"""Build the standalone monograph; preserve all TeX diagnostics."""
from pathlib import Path
import subprocess,shutil,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
    src=ROOT/'monograph/Constructive_Repair.tex';out=ROOT/'evidence/latex';out.mkdir(parents=True,exist_ok=True)
    for i in range(1,4):
        q=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',
                          '-output-directory',str(out),str(src)],cwd=src.parent,capture_output=True,text=True,timeout=90, encoding="utf-8")
        (out/f'pass_{i:02d}.stdout.log').write_text(q.stdout+q.stderr, encoding="utf-8")
        if q.returncode:raise RuntimeError(f'pdfLaTeX pass {i} failed; see log')
    log=(out/'Constructive_Repair.log').read_text(errors='replace', encoding="utf-8")
    checks={'no_overfull':'Overfull \\hbox' not in log and 'Overfull \\vbox' not in log,
            'no_undefined_references':'undefined references' not in log and 'Reference `' not in log,
            'no_missing_characters':'Missing character:' not in log,
            'no_rerun_needed':'Rerun to get' not in log and 'Label(s) may have changed' not in log}
    dest=src.with_suffix('.pdf');shutil.copy2(out/'Constructive_Repair.pdf',dest)
    result={'latex_checks':checks,'pdf_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
            'tex_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'render_inspection':'PENDING'}
    (ROOT/'evidence/document_build.json').write_text(json.dumps(result,indent=2), encoding="utf-8")
    print(json.dumps(result,indent=2))
    if not all(checks.values()):raise RuntimeError('TeX preflight failed; inspect diagnostics')
if __name__=='__main__':main()
