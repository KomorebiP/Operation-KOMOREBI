#!/usr/bin/env python3
"""Read-only archival checks and isolated Paper VI Python/LaTeX replay. Never invokes Lean."""
from __future__ import annotations
import argparse, hashlib, json, math, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path,default=ROOT/'rebuilt/original_audit');args=ap.parse_args()
    src=ROOT/'original_snapshot';out=args.output_dir.resolve()
    if out==src or src in out.parents:raise SystemExit('Choose output outside original_snapshot')
    out.mkdir(parents=True,exist_ok=True)
    def inventory():return {p.relative_to(src).as_posix():sha(p) for p in sorted(src.rglob('*')) if p.is_file()}
    current=inventory();expected=json.loads((ROOT/'verification/ORIGINAL_SNAPSHOT_HASHES.json').read_text())
    if expected!=current:raise SystemExit('Original source tree changed')
    release=json.loads((src/'RELEASE_MANIFEST.json').read_text())['sha256']
    for name,h in release.items():
        if sha(src/name)!=h:raise SystemExit(f'Original manifest mismatch: {name}')
    report={'status':'RUNNING','scope':'Archival checks and isolated Python/LaTeX replay; no Lean invocation','source_files':len(current),'original_manifest_entries_checked':len(release),'commands':[]}
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',SOURCE_DATE_EPOCH='1789171200',FORCE_SOURCE_DATE='1')
    def run(cmd,cwd,name,timeout=240):
        t=time.monotonic()
        with (out/name).open('w') as h:p=subprocess.run(cmd,cwd=cwd,env=env,stdout=h,stderr=subprocess.STDOUT,timeout=timeout)
        report['commands'].append({'argv':cmd,'exit_code':p.returncode,'seconds':time.monotonic()-t,'log':name})
        if p.returncode:raise RuntimeError(f'{name} failed, exit {p.returncode}')
        return (out/name).read_text(errors='replace')
    with tempfile.TemporaryDirectory(prefix='paper_vi_original_') as td:
        copy=Path(td)/'release';shutil.copytree(src,copy)
        cmd="import importlib.util,json;from pathlib import Path;s=importlib.util.spec_from_file_location('v','verification/verify.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(json.dumps(m.static_checks(Path('.')),indent=2))"
        report['static_contract']=json.loads(run([sys.executable,'-c',cmd],copy,'static_contract.log'))
        txt=run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests','--junitxml='+str(out/'companion_junit.xml')],copy/'companion','companion_tests.log')
        report['companion_tests_passed']=int(re.search(r'(\d+) passed',txt).group(1))
        (copy/'companion/results').mkdir(exist_ok=True);(copy/'companion/tables').mkdir(exist_ok=True)
        txt=run([sys.executable,'run_all.py'],copy/'companion','original_generation.log')
        report['original_figure_pairs_produced']=int(re.search(r'Generated (\d+) figure pairs',txt).group(1))
        old=json.loads((src/'companion/results/numerical_results.json').read_text());new=json.loads((copy/'companion/results/numerical_results.json').read_text());diffs=[];nums=[]
        def compare(a,b,path=''):
            if isinstance(a,dict):
                if set(a)!=set(b):diffs.append({'keyset':path})
                for k in a:compare(a[k],b[k],path+'/'+k)
            elif isinstance(a,list):
                if len(a)!=len(b):diffs.append({'length':path})
                else:
                    for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
            elif isinstance(a,(int,float)) and not isinstance(a,bool):
                nums.append({'path':path,'old':a,'new':b,'exact':a==b,'close':math.isclose(a,b,rel_tol=1e-7,abs_tol=5e-10)})
                if not nums[-1]['close']:diffs.append(nums[-1])
            elif a!=b:diffs.append({'path':path,'old':a,'new':b})
        compare(old,new)
        (out/'NUMERICAL_COMPARISON.json').write_text(json.dumps({'numerical_metrics':len(nums),'all_exact':all(x['exact'] for x in nums),'tolerance':{'relative':1e-7,'absolute':5e-10},'differences_beyond_tolerance':diffs,'metrics':nums},indent=2))
        report.update(numerical_metrics_compared=len(nums),numerical_records_equal=old==new,numerical_within_declared_tolerance=not diffs)
        if diffs:raise RuntimeError('Original numerical replay differed beyond tolerance')
        tex=shutil.which('pdflatex')
        if not tex:raise RuntimeError('pdflatex missing')
        for i in range(3):run([tex,'-interaction=nonstopmode','-halt-on-error','Paper_VI_Reviewed.tex'],copy/'manuscript',f'manuscript_pass{i+1}.log')
        import fitz
        a=fitz.open(src/'manuscript/Paper_VI_Reviewed.pdf');b=fitz.open(copy/'manuscript/Paper_VI_Reviewed.pdf');checks=[]
        for i in range(min(len(a),len(b))):
            pa=a[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);pb=b[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
            checks.append({'page':i+1,'text_equal':a[i].get_text()==b[i].get_text(),'render_equal_72_dpi':(pa.width,pa.height,pa.samples)==(pb.width,pb.height,pb.samples)})
        report.update(original_pdf_pages=len(a),rebuilt_pdf_pages=len(b),original_rebuild_page_checks=checks,all_original_rebuild_pages_equal=len(a)==len(b) and all(v['text_equal'] and v['render_equal_72_dpi'] for v in checks))
        report['latex_warnings']=re.findall(r'^.*(?:Overfull|Underfull|undefined references|LaTeX Warning).*$',(copy/'manuscript/Paper_VI_Reviewed.log').read_text(errors='replace'),re.M)
        a.close();b.close();shutil.copy2(copy/'manuscript/Paper_VI_Reviewed.log',out/'original_latex.log')
    if current!=inventory():raise RuntimeError('Original tree changed during isolated replay')
    report.update(status='PASS',finished_utc=datetime.now(timezone.utc).isoformat(),original_snapshot_unchanged=True,lean_run=False)
    (out/'ORIGINAL_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['commands','original_rebuild_page_checks','latex_warnings']},indent=2))
if __name__=='__main__':
    try:main()
    except (OSError,RuntimeError,subprocess.SubprocessError) as e:raise SystemExit(f'Original replay failed: {e}') from e
