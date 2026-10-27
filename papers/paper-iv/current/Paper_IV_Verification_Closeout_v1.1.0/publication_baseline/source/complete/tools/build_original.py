#!/usr/bin/env python3
"""Rebuild the selected proofread manuscript in a temporary directory, without editing it."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'original_snapshot/proofread_review/PRSC_IV_Review'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'rebuilt/original')
    args=parser.parse_args();out=args.output_dir.resolve()
    protected=ROOT/'original_snapshot'
    if out==protected or protected in out.parents:raise RuntimeError('Choose an output outside original_snapshot.')
    out.mkdir(parents=True,exist_ok=True);logs=out/'logs';logs.mkdir(exist_ok=True)
    tex=shutil.which('pdflatex')
    if not tex:raise RuntimeError('pdflatex is not installed.')
    bib=shutil.which('bibtex') or shutil.which('bibtex.original')
    env=os.environ.copy();env.setdefault('SOURCE_DATE_EPOCH','1789171200');env.setdefault('FORCE_SOURCE_DATE','1')
    before={p.name:sha(p) for p in (SOURCE/'paper').iterdir() if p.is_file()}
    commands=[]
    with tempfile.TemporaryDirectory(prefix='paper_iv_original_') as td:
        work=Path(td)
        for p in (SOURCE/'paper').iterdir():
            if p.is_file():shutil.copy2(p,work/p.name)
        def run(argv,name):
            t=time.monotonic()
            with (logs/name).open('w') as f:
                result=subprocess.run(argv,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120)
            commands.append({'argv':argv,'exit_code':result.returncode,'seconds':time.monotonic()-t,'log':name})
            if result.returncode:raise RuntimeError('Original typesetting failed. See '+str(logs/name))
        run([tex,'-interaction=nonstopmode','-halt-on-error','paper4.tex'],'latex1.log')
        if bib:run([bib,'paper4'],'bibtex.log')
        else:shutil.copy2(ROOT/'tools/rebuild_assets/proofread/paper4.bbl',work/'paper4.bbl')
        for k in (2,3):run([tex,'-interaction=nonstopmode','-halt-on-error','paper4.tex'],f'latex{k}.log')
        dest=out/'Paper_IV_Proofread_Rebuilt.pdf';shutil.copy2(work/'paper4.pdf',dest)
        shutil.copy2(work/'paper4.log',logs/'paper4.log')
        import fitz
        a=fitz.open(SOURCE/'PRSC_IV_Proofread_Draft.pdf');b=fitz.open(dest)
        if len(a)!=39 or len(b)!=39:raise RuntimeError('Original typesetting changed the expected page count.')
        compared=[]
        for i in range(39):
            x=a[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);y=b[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
            compared.append({'page':i+1,'same_text':a[i].get_text()==b[i].get_text(),
                'same_render_72dpi':(x.width,x.height,x.samples)==(y.width,y.height,y.samples)})
        a.close();b.close()
        after={p.name:sha(p) for p in (SOURCE/'paper').iterdir() if p.is_file()}
        if before!=after:raise RuntimeError('Preserved original source changed unexpectedly.')
        same=all(p['same_text'] and p['same_render_72dpi'] for p in compared)
        report={'status':'PASS' if same else 'REBUILT_WITH_RENDER_DIFFERENCES',
            'scope':'LaTeX rebuild of the later proofread draft, not a Lean build.',
            'generated_utc':datetime.now(timezone.utc).isoformat(),'pages':39,'source_unchanged':True,
            'bibtex_program':bib,'used_saved_bbl':not bool(bib),'commands':commands,
            'all_pages_match_saved_text_and_render':same,'page_comparisons':compared,
            'saved_pdf_sha256':sha(SOURCE/'PRSC_IV_Proofread_Draft.pdf'),'rebuilt_pdf_sha256':sha(dest)}
        (out/'ORIGINAL_REBUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
        print(f'{report["status"]}: 39-page original rebuild. Matching text and render: {sum(p["same_text"] and p["same_render_72dpi"] for p in compared)}/39.')

if __name__=='__main__':
    try:main()
    except (OSError,RuntimeError,ImportError,subprocess.SubprocessError) as exc:raise SystemExit(f'Original rebuild failed: {exc}')
