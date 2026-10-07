#!/usr/bin/env python3
"""Show export-ledger changes; update only with --write after source identity passes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from check_github_ready import ROOT, is_generated

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Explicitly rewrite FILE_HASHES.json; does not approve publication.')
    args=parser.parse_args()
    proc=subprocess.run([sys.executable,'-B',str(ROOT/'tools/check_candidate.py')],cwd=ROOT,text=True,capture_output=True,timeout=180)
    if proc.returncode:
        print(proc.stdout or proc.stderr,file=sys.stderr)
        return 1
    files={p.relative_to(ROOT).as_posix():p for p in ROOT.rglob('*') if p.is_file() and not is_generated(p.relative_to(ROOT)) and p.relative_to(ROOT).as_posix()!='FILE_HASHES.json'}
    for name,p in files.items():
        if p.is_symlink() or p.name.startswith('.env') or p.suffix.lower() in {'.zip','.bundle','.pem','.key','.ttf','.otf','.woff','.woff2','.olean','.ilean','.exe','.dll'}:
            raise SystemExit('Refusing an unapproved export artifact: '+name)
    ledger={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in sorted(files.items())}
    path=ROOT/'FILE_HASHES.json'
    old=json.loads(path.read_text()) if path.exists() else {}
    changes={'added':sorted(set(ledger)-set(old)), 'removed':sorted(set(old)-set(ledger)),
             'changed':sorted(n for n in set(old)&set(ledger) if old[n]!=ledger[n])}
    if args.write:
        path.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'LEDGER_WRITTEN' if args.write else 'DRY_RUN_NO_CHANGES','sealed_files':len(ledger),
                      'changes':changes,'scope':'Identity ledger only; not a proof replay or publication clearance.'},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
