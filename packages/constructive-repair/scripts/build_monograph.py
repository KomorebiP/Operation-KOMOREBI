#!/usr/bin/env python3
"""Compile the monograph with source-bound receipts and retained TeX diagnostics."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import subprocess
import shutil
import json
import hashlib
import re
import time
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'evidence/latex_rc3')
    a=ap.parse_args();src=ROOT/'monograph/Constructive_Repair.tex';out=a.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    source_hash=hashlib.sha256(src.read_bytes()).hexdigest()
    commands=[]
    for i in range(1,4):
        argv=['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',
              '-output-directory',str(out),str(src)]
        start=time.monotonic()
        q=subprocess.run(argv,cwd=src.parent,capture_output=True,text=True,timeout=90,encoding='utf-8')
        (out/f'pass_{i:02d}.stdout.log').write_text(q.stdout+q.stderr,encoding='utf-8')
        commands.append({'argv':argv,'returncode':q.returncode,'seconds':time.monotonic()-start})
        if q.returncode:raise RuntimeError(f'pdfLaTeX pass {i} failed; see retained log')
    log=(out/'Constructive_Repair.log').read_text(errors='replace',encoding='utf-8')
    checks={'no_overfull_boxes':'Overfull \\hbox' not in log and 'Overfull \\vbox' not in log,
            'references_resolved':'undefined references' not in log and 'Reference `' not in log and
                'Rerun to get' not in log and 'Label(s) may have changed' not in log,
            'no_missing_characters':'Missing character:' not in log}
    if not all(checks.values()):raise RuntimeError('TeX preflight failed; inspect retained diagnostics')
    if hashlib.sha256(src.read_bytes()).hexdigest()!=source_hash:raise RuntimeError('LaTeX source changed during compilation')
    page_match=re.search(r'Output written on .*?\((\d+) pages?',log,re.S)
    if page_match is None:raise RuntimeError('Page count absent from TeX build log')
    dest=src.with_suffix('.pdf');shutil.copy2(out/'Constructive_Repair.pdf',dest)
    result={'status':'PASS','source_sha256':source_hash,
            'pdf_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'pages':int(page_match[1]),
            **checks,'commands':commands,'finished_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'LaTeX compilation and diagnostics; visual review recorded separately'}
    (ROOT/'monograph/build_receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
