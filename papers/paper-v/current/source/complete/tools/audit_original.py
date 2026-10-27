#!/usr/bin/env python3
"""Replay non-Lean checks in an isolated copy. Never modifies the preserved release."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile,time,platform
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def require(v,m):
    if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=ROOT/'verification/original_replay');a=ap.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'original_snapshot';snapshot=json.loads((ROOT/'verification/ORIGINAL_SNAPSHOT_HASHES.json').read_text());require(all(sha(source/p)==h for p,h in snapshot.items()),'Source snapshot hash mismatch')
    report={'status':'RUNNING','scope':'Source integrity, original finite tests, numerical and typesetting replay. No Lean invocation.','started_utc':datetime.now(timezone.utc).isoformat(),'commands':[]}
    env=os.environ.copy();env.update(MPLBACKEND='Agg',PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    def save(): (out/'ORIGINAL_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    def run(cmd,cwd,log,timeout=180):
        start=time.monotonic()
        with (out/log).open('w') as f:
            try:p=subprocess.run(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
            except subprocess.TimeoutExpired:
                report['commands'].append({'argv':cmd,'status':'TIMEOUT','seconds':time.monotonic()-start,'log':log});save();raise
        report['commands'].append({'argv':cmd,'exit_code':p.returncode,'seconds':time.monotonic()-start,'log':log});save();require(p.returncode==0,f'Failed step: {log}')
    try:
      with tempfile.TemporaryDirectory(prefix='paper_v_original_') as d:
        work=Path(d)/'snapshot';shutil.copytree(source,work)
        run([sys.executable,'-m','pytest','-q','tests','--junitxml='+str(out/'companion_junit.xml')],work/'companion','companion_tests.log')
        env['PYTHONPATH']=str(work/'tests')
        run([sys.executable,'-m','pytest','-q','tests','--junitxml='+str(out/'independent_junit.xml')],work,'independent_tests.log',240)
        import xml.etree.ElementTree as ET
        for stem in ['companion','independent']:
            suites=list(ET.parse(out/(stem+'_junit.xml')).getroot().iter('testsuite'))
            require(all(sum(int(s.get(k,0)) for s in suites)==0 for k in ['failures','errors','skipped']),f'{stem} tests not clean')
            report[stem+'_tests_passed']=sum(int(s.get('tests',0)) for s in suites)
        code="import importlib.util,json;from pathlib import Path;p=Path('verification/verify.py');s=importlib.util.spec_from_file_location('v',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(json.dumps(m.static_checks(Path('.').resolve()),indent=2))"
        run([sys.executable,'-c',code],work,'static_contract.log');report['static_contract_pass']=True
        run([sys.executable,'run_all.py'],work/'companion','original_generation.log',240)
        import numpy as np
        old=json.loads((source/'companion/results/numerical_results.json').read_text());new=json.loads((work/'companion/results/numerical_results.json').read_text());compared=[]
        def compare(a,b,path=''):
            if isinstance(a,dict):
                require(a.keys()==b.keys(),f'JSON keys {path}')
                for k in a:compare(a[k],b[k],path+'/'+k)
            elif isinstance(a,list):
                require(len(a)==len(b),f'JSON length {path}')
                for i,(u,v) in enumerate(zip(a,b)):compare(u,v,path+'/'+str(i))
            elif isinstance(a,float):
                require(np.isfinite(b) and np.isclose(a,b,atol=1e-12,rtol=1e-10),f'Numeric mismatch {path}: {a} != {b}');compared.append({'key':path,'original':a,'replayed':b,'exactly_equal':a==b})
            else:require(a==b,f'JSON value {path}')
        compare(old,new);report['numerical_metrics_compared']=len(compared);report['numerical_records_exactly_equal']=old==new;report['numerical_rtol']=1e-10;report['numerical_atol']=1e-12
        (out/'NUMERICAL_COMPARISON.json').write_text(json.dumps(compared,indent=2)+'\n')
        for ext in ['pdf','png']:require(len(list((work/'companion/figures').glob('*.'+ext)))==18,f'Expected 18 {ext} figures')
        report['figure_pairs_regenerated']=18
        for i in range(3):run(['pdflatex','-interaction=nonstopmode','-halt-on-error','Paper_V_Expanded_Lean_Checked.tex'],work/'manuscript',f'manuscript_pass{i+1}.log')
        import fitz
        pub=fitz.open(source/'manuscript/Paper_V_Expanded_Lean_Checked.pdf');reb=fitz.open(work/'manuscript/Paper_V_Expanded_Lean_Checked.pdf')
        require(len(pub)==len(reb)==39,'Original rebuilt page count differs')
        pages=[]
        for i in range(len(pub)):
            eq=pub[i].get_text()==reb[i].get_text();aa=pub[i].get_pixmap();bb=reb[i].get_pixmap();same=(aa.width,aa.height,aa.samples)==(bb.width,bb.height,bb.samples)
            pages.append({'page':i+1,'same_text':eq,'same_render_72dpi':same})
        report['manuscript_pages']=39;report['manuscript_page_comparison']=pages
        report['original_rebuild_text_identical']=all(p['same_text'] for p in pages);report['original_rebuild_render_identical']=all(p['same_render_72dpi'] for p in pages)
        shutil.copy2(work/'manuscript/Paper_V_Expanded_Lean_Checked.log',out/'original_latex.log')
        report['snapshot_files_preserved']=len(snapshot)
        require(all(sha(source/p)==h for p,h in snapshot.items()),'Source changed during isolated checks')
        report['status']='PASS';report['finished_utc']=datetime.now(timezone.utc).isoformat();report['python']=platform.python_version();report['lean_rerun']=False;save();print(json.dumps({k:v for k,v in report.items() if k not in ['commands','manuscript_page_comparison']},indent=2))
    except Exception as e:
        report['status']='FAIL';report['error']=str(e);save();raise
if __name__=='__main__':main()
