#!/usr/bin/env python3
"""Rebuild the three PDFs from packaged source in an isolated directory."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile

root=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check-only',action='store_true',help='Build and compare text/page counts without replacing shipped PDFs.')
parser.add_argument('--report',type=Path,help='Write a JSON verification report to this path.')
args=parser.parse_args()
specs=[('traditional','Paper_III_Traditional_Final'),('visual_guide','Paper_III_Visual_Guide_Final'),('lean_guide','Paper_III_Lean_Guide_Final')]
results=[]
with tempfile.TemporaryDirectory(prefix='komorebi-paper-iii-') as work:
    work=Path(work)
    for folder,stem in specs:
        target=work/folder
        shutil.copytree(root/'editable'/folder,target,ignore=shutil.ignore_patterns('qa','__pycache__','*.pdf','*.aux','*.log','*.out','*.toc','*.fdb_latexmk','*.fls'))
        # Traditional figures are PDF source assets, not generated manuscripts.
        if folder=='traditional':
            shutil.copytree(root/'editable'/folder/'figures',target/'figures',dirs_exist_ok=True)
        result=subprocess.run([sys.executable,'build.py'],cwd=target,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if result.returncode:
            print(result.stdout[-12000:]);raise SystemExit(f'{folder}: build failed')
        rebuilt=target/(stem+'.pdf')
        if not rebuilt.is_file(): raise SystemExit(f'{folder}: expected PDF missing')
        before=root/'papers'/(stem+'.pdf')
        record={'document':stem,'build_returncode':0,'pdf_bytes':rebuilt.stat().st_size,'pdf_sha256':hashlib.sha256(rebuilt.read_bytes()).hexdigest()}
        if args.check_only:
            import fitz
            with fitz.open(before) as original, fitz.open(rebuilt) as fresh:
                record['pages']=len(fresh)
                record['page_count_match']=len(original)==len(fresh)
                record['extracted_text_match']=record['page_count_match'] and all(a.get_text()==b.get_text() for a,b in zip(original,fresh))
                if not (record['page_count_match'] and record['extracted_text_match']):
                    raise SystemExit(f'{folder}: rebuilt page count or extracted text differs')
        else:
            shutil.copy2(rebuilt,before)
        results.append(record)
report={'status':'PASS','check_only':args.check_only,'documents':results,'boundary':'PDF compilation and extracted-text/page comparison; no Lean compiler or mathematical tests invoked.'}
if args.report:
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
