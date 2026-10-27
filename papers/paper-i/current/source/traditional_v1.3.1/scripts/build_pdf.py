#!/usr/bin/env python3
"""Compile three passes, fail on unresolved references or box overflow.

A successful compile is not a visual inspection or a PDF/UA/press certificate.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, time
from pathlib import Path

def main() -> int:
    root=Path(__file__).resolve().parents[1]
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=root/'verification/pdf_rebuild');a=ap.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    report={'status':'RUNNING','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'passes':[],'visual_review':'NOT_RUN_BY_THIS_SCRIPT'}
    def save(): (out/'build.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    compiler=shutil.which('pdflatex')
    if not compiler:report.update(status='FAIL',error='pdflatex not on PATH');save();return 1
    stem='Projector_Resolved_Seed_Calculus_I'
    report['compiler_version']=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0]
    report['tex_sha256']=hashlib.sha256((root/'paper'/(stem+'.tex')).read_bytes()).hexdigest()
    for i in range(1,4):
        cmd=[compiler,'-interaction=nonstopmode','-halt-on-error','-output-directory',str(out),stem+'.tex']
        with (out/f'pass{i}.log').open('w') as f:p=subprocess.run(cmd,cwd=root/'paper',stdout=f,stderr=subprocess.STDOUT,timeout=180)
        report['passes'].append({'command':cmd,'returncode':p.returncode});save()
        if p.returncode:report['status']='FAIL';save();return 1
    text=(out/(stem+'.log')).read_text(errors='replace')
    problems=[x for x in text.splitlines() if any(t in x for t in ('Overfull \\hbox','Overfull \\vbox','undefined references','undefined on input','multiply defined'))]
    report['warnings']=[x for x in text.splitlines() if 'Warning' in x or 'Underfull' in x]
    report['layout_errors']=problems
    if problems:report['status']='FAIL';save();return 1
    pdf=out/(stem+'.pdf');shutil.copy2(pdf,root/'paper'/(stem+'.pdf'))
    report.update(status='PASS',pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    save();print('PDF compilation: PASS');return 0
if __name__=='__main__':raise SystemExit(main())
