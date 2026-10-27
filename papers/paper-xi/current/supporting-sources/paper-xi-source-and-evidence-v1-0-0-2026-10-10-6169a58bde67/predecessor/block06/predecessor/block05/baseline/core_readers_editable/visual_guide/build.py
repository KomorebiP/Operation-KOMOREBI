"""Portable Paper XI visual-guide build, requiring Python/Matplotlib and pdfLaTeX."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

def main():
    root=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=root/'build')
    out=ap.parse_args().output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env.setdefault('SOURCE_DATE_EPOCH','1791244800');env['FORCE_SOURCE_DATE']='1'
    subprocess.run([sys.executable,str(root/'generate_figures.py'),'--output-dir',str(out/'figures')],check=True,env=env)
    name='Paper_XI_Visual_Guide_Final'
    if (out/(name+'.tex')).resolve()!=(root/(name+'.tex')).resolve():shutil.copy2(root/(name+'.tex'),out/(name+'.tex'))
    engine=shutil.which('pdflatex')
    if not engine:raise RuntimeError('pdfLaTeX is required to build the editable TeX source')
    for passno in range(3):
        p=subprocess.run([engine,'-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=out,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/f'latex_pass_{passno+1}.txt').write_text(p.stdout)
        if p.returncode:raise RuntimeError(f'LaTeX pass {passno+1} failed; see output log')
    pdf=out/(name+'.pdf');report={'status':'PASS','pdf':str(pdf),'bytes':pdf.stat().st_size,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'figures':len(list((out/'figures').glob('*.pdf'))),'source_date_epoch':env['SOURCE_DATE_EPOCH']}
    (out/'BUILD_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
