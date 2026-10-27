#!/usr/bin/env python3
"""Build Paper XII companions from isolated editable-source copies."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile
import fitz

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check-only', action='store_true')
parser.add_argument('--report', type=Path)
parser.add_argument('--roles', nargs='+', choices=('traditional','visual_guide','lean_guide'), default=('traditional','visual_guide','lean_guide'))
args = parser.parse_args()
records = []
failures = []
env = dict(os.environ, SOURCE_DATE_EPOCH='1791244800', FORCE_SOURCE_DATE='1', PYTHONDONTWRITEBYTECODE='1')
with tempfile.TemporaryDirectory(prefix='komorebi-paper-xii-build-') as tmp:
    for role in args.roles:
        part = {'traditional':'Traditional','visual_guide':'Visual_Guide','lean_guide':'Lean_Guide'}[role]
        name = 'Paper_XII_'+part+'_Final.pdf'
        stage = Path(tmp)/role
        shutil.copytree(root/'editable'/role,stage,ignore=shutil.ignore_patterns('__pycache__','*.aux','*.log','*.out','*.toc','*.xdv','*.synctex.gz'))
        (stage/name).unlink(missing_ok=True)
        out = stage/'isolated_output'
        out.mkdir()
        cmd = [sys.executable,'build.py','--output-dir',str(out)]
        proc = subprocess.run(cmd,cwd=stage,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        fresh, shipped = out/name, root/'papers'/name
        rec = {'role':role,'command':[sys.executable,'build.py','--output-dir','<isolated new directory>'],'exit_status':proc.returncode,'build_output_tail':proc.stdout[-16000:]}
        if proc.returncode or not fresh.is_file():
            rec['status']='FAIL'; rec['failure']='Compilation failed' if proc.returncode else 'Expected named PDF was not produced'
            failures.append(role);records.append(rec);continue
        with fitz.open(shipped) as old, fitz.open(fresh) as new:
            rec.update(pages=len(new),nonempty_documents=len(old)>0 and len(new)>0,page_count_match=len(old)==len(new),extracted_text_match=len(old)==len(new) and all(a.get_text()==b.get_text() for a,b in zip(old,new)),byte_identical=shipped.read_bytes()==fresh.read_bytes(),sha256=hashlib.sha256(fresh.read_bytes()).hexdigest())
        passed=all(rec[k] for k in ['nonempty_documents','page_count_match','extracted_text_match','byte_identical'])
        rec['status']='PASS' if passed else 'DIFFERS'
        if args.check_only and not passed: failures.append(role)
        if not args.check_only: shutil.copy2(fresh,shipped)
        records.append(rec)
report={'status':'FAIL' if failures else 'PASS','check_only':args.check_only,'documents':records,'failures':failures,'scope':'Isolated PDF rebuild and byte/text/page comparison. This performs no Lean compilation or mathematical experiment.'}
if args.report:
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(bool(failures))
