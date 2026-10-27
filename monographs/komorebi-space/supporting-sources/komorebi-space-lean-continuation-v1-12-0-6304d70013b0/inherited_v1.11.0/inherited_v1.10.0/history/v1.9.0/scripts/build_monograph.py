#!/usr/bin/env python3
"""Build only the revised monograph; do not rerun Lean or historical finite suites."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def snapshot():
    return {str(p.relative_to(SOURCE)):sha(p) for p in sorted(SOURCE.rglob('*')) if p.is_file()}

def main():
    label = sys.argv[1] if len(sys.argv)>1 else 'publication'
    if not re.fullmatch(r'[a-zA-Z0-9_-]+',label):
        raise SystemExit('Use a simple immutable build label')
    run = ROOT / 'audit' / label
    run.mkdir(parents=True, exist_ok=False)
    pub = ROOT / 'publication'
    pub.mkdir(exist_ok=True)
    before = snapshot()
    records=[]
    for index in range(1,4):
        cmd=['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',
             '-recorder',f'-output-directory={pub}','Komorebi_Space_Monograph.tex']
        result=subprocess.run(cmd,cwd=SOURCE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        log=run/f'pass_{index}.log'
        log.write_bytes(result.stdout)
        records.append({'pass':index,'returncode':result.returncode,'log':log.name,'sha256':sha(log)})
        if result.returncode:
            (run/'receipt.json').write_text(json.dumps({'status':'FAIL','passes':records},indent=2)+'\n')
            print(result.stdout.decode(errors='replace')[-8000:])
            raise SystemExit(result.returncode)
    log=(pub/'Komorebi_Space_Monograph.log').read_text()
    blocking=re.findall(r'^.*(?:undefined references|multiply defined|Label\(s\) may have changed|Overfull|Missing character|LaTeX Font Warning|Package .* Warning).*$' ,log,re.M)
    if snapshot()!=before:
        blocking.append('Manuscript changed during compilation')
    receipt={'status':'PASS' if not blocking else 'NEEDS_REVIEW','passes':records,
             'source_sha256':before,'pdf_sha256':sha(pub/'Komorebi_Space_Monograph.pdf'),
             'blocking_diagnostics':blocking,
             'underfull_diagnostics':re.findall(r'^Underfull.*$',log,re.M),
             'lean_executed':False,'historical_finite_suites_rerun':False}
    (run/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='source_sha256'},indent=2))
    if blocking:
        raise SystemExit(1)

if __name__=='__main__':
    main()
