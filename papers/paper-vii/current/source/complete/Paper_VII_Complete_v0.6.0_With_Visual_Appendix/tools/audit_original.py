#!/usr/bin/env python3
"""Replay the preserved numerical companion and TeX in a temporary directory.
No Lean build is performed. Outputs are written outside both source snapshots.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def flatten(x,p=''):
    if isinstance(x,dict):
        for k,v in x.items():yield from flatten(v,p+'/'+str(k))
    elif isinstance(x,list):
        for k,v in enumerate(x):yield from flatten(v,p+'/'+str(k))
    else:yield p,x

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'rebuilt_original');args=ap.parse_args()
    out=args.out.resolve()
    for protected in [ROOT/'original_snapshot',ROOT/'original_companion',ROOT/'visual_appendix',ROOT/'reading',ROOT/'related_editorial_v0.5.1']:
        if out==protected or protected in out.parents:raise ValueError('Use an output directory outside preserved inputs.')
    if out==ROOT:raise ValueError('Use a dedicated output directory.')
    out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'original_companion';proof=ROOT/'original_snapshot';commands=[]
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',SOURCE_DATE_EPOCH='1789171200',FORCE_SOURCE_DATE='1')
    expected={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()}
    with tempfile.TemporaryDirectory(prefix='paper_vii_original_') as td:
        work=Path(td)/'companion';shutil.copytree(source,work)
        def run(argv,log,cwd=work,timeout=160):
            t=time.monotonic()
            with (out/log).open('w') as h:p=subprocess.run(argv,cwd=cwd,env=env,stdout=h,stderr=subprocess.STDOUT,timeout=timeout)
            commands.append({'argv':argv,'exit_code':p.returncode,'seconds':time.monotonic()-t,'log':log})
            if p.returncode:raise RuntimeError(f'{log} failed')
        run([sys.executable,'-m','pytest','-q','tests'],'original_tests.log')
        run([sys.executable,'run_all.py'],'original_figures.log')
        stored=json.loads((source/'results/numerical_results.json').read_text());new=json.loads((work/'results/numerical_results.json').read_text())
        aa,bb=dict(flatten(stored)),dict(flatten(new));num=[k for k,v in aa.items() if isinstance(v,(int,float)) and not isinstance(v,bool)]
        numerical={k:{'old':aa[k],'new':bb.get(k),'exact_equal':aa[k]==bb.get(k)} for k in num}
        same=aa==bb
        (out/'numerical_comparison.json').write_text(json.dumps({'all_records_equal':same,'numeric_fields':len(num),'records':numerical},indent=2)+'\n')
        figs=list((work/'figures').glob('*.pdf'));pngs=list((work/'figures').glob('*.png'))
        if len(figs)!=19 or len(pngs)!=19:raise RuntimeError('Wrong original figure count')
        # Rebuild original source using its original shipped figures, not regenerated ones.
        shutil.rmtree(work/'figures');shutil.copytree(source/'figures',work/'figures')
        tex='Projector_Resolved_Seed_Calculus_VII.tex'
        for j in range(3):run(['pdflatex','-interaction=nonstopmode','-halt-on-error',tex],f'original_latex_{j+1}.log')
        import fitz
        a=fitz.open(source/'Projector_Resolved_Seed_Calculus_VII.pdf');b=fitz.open(work/'Projector_Resolved_Seed_Calculus_VII.pdf')
        pc=[]
        for i in range(min(len(a),len(b))):
            x,y=a[i].get_pixmap(alpha=False),b[i].get_pixmap(alpha=False)
            pc.append({'page':i+1,'same_text':a[i].get_text()==b[i].get_text(),'same_render_at_72_dpi':(x.width,x.height,x.samples)==(y.width,y.height,y.samples)})
        result={'scope':'numerical/software/typesetting replay only; no Lean invocation','commands':commands,'numerical_records_match':same,'numeric_fields':len(num),'figure_pdf_count':len(figs),'figure_png_count':len(pngs),'source_pages':len(a),'rebuilt_pages':len(b),'manuscript_page_comparison':pc,'sources_unchanged':expected=={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()}}
        shutil.copy2(work/'Projector_Resolved_Seed_Calculus_VII.pdf',out/'Original_Manuscript_Rebuilt.pdf')
        # Auditing the verifier is software regression, not kernel certification.
        sw=Path(td)/'verifier';shutil.copytree(proof/'scripts',sw)
        run([sys.executable,'test_verifier.py'],'verifier_software_tests.log',cwd=sw)
        result['status']='PASS' if same and result['sources_unchanged'] and len(a)==len(b) and all(t['same_text'] and t['same_render_at_72_dpi'] for t in pc) else 'COMPLETED_WITH_RECORDED_DIFFERENCES'
        a.close();b.close()
        (out/'ORIGINAL_REPLAY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
        print(result['status'],len(num),'numeric fields;',len(pc),'pages')
if __name__=='__main__':main()
