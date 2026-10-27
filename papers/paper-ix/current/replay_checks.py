#!/usr/bin/env python3
"""Replay nine bounded arithmetic/metadata gates in a new external output directory.
Uses installed Python, NumPy and matplotlib. Does not install software or run Lean.
Counts overlap and must not be added as independent theorem evidence.
"""
from __future__ import annotations
import argparse,concurrent.futures,hashlib,json,os,shutil,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path);ap.add_argument('--jobs',type=int,default=3);args=ap.parse_args()
    dest=args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='paper_ix_replay_'))
    if dest==ROOT or dest.is_relative_to(ROOT):raise SystemExit('Use an output directory outside this frozen release.')
    if dest.exists() and any(dest.iterdir()):raise SystemExit('Output directory must be empty.')
    if args.jobs<1:raise SystemExit('--jobs must be positive.')
    dest.mkdir(parents=True,exist_ok=True);fig=dest/'visual_figures'
    (fig/'sources').mkdir(parents=True);shutil.copy2(ROOT/'sources/generate_figures.py',fig/'sources/generate_figures.py')
    jobs=[
      ('delta_boundary','evidence/delta_boundary_checks.py',[str(dest/'delta_boundary/result.json')],120),
      ('metric_tables','evidence/metric_table_checks.py',[str(dest/'metric_tables/result.json')],120),
      ('formal_source_reconciliation','sources/lean/audit_sources.py',['--source',str(ROOT/'preserved/PRSC_IX_Consolidated_Manuscript'),'--output',str(dest/'formal_source_reconciliation')],120),
      ('dyadic_512','preserved/threshold_free/computation/check_dyadic_differences.py',['--bound','512','--precision','4096','--order','128','--rational-bound','16','--output',str(dest/'dyadic_512/result.json')],300),
      ('factorial_extension','preserved/threshold_free/computation/check_factorial_extension.py',['--bound','96','--precision','1024','--output',str(dest/'factorial_extension/result.json')],120),
      ('factorial_frontier','preserved/threshold_free/computation/check_factorial_frontier.py',['--bound','96','--precision','1024','--mixed-order','5','--output',str(dest/'factorial_frontier/result.json')],120),
      ('visual_figures',str(fig/'sources/generate_figures.py'),[],180),
      ('worked_examples','tools/worked_examples.py',['--output',str(dest/'worked_examples/result.json')],120),
      ('reconstructed_figures','tools/reconstructed_figures.py',['--output',str(dest/'reconstructed_figures/result.json')],120)]
    def run(job):
        name,source,extra,limit=job;out=dest/name;out.mkdir(exist_ok=True);script=Path(source)
        if not script.is_absolute():script=ROOT/script
        cmd=[sys.executable,str(script)]+extra;start=time.monotonic()
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        try:
            p=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,timeout=limit);code=p.returncode;stdout=p.stdout;stderr=p.stderr;timed=False
        except subprocess.TimeoutExpired as e:code=None;stdout=e.stdout or b'';stderr=e.stderr or b'';timed=True
        (out/'stdout.txt').write_bytes(stdout);(out/'stderr.txt').write_bytes(stderr)
        r={'name':name,'command':cmd,'cwd':str(ROOT),'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'status':'PASS' if code==0 else 'FAIL','exit_code':code,'timed_out':timed,'seconds':round(time.monotonic()-start,3),'timeout_seconds':limit}
        (out/'execution.json').write_text(json.dumps(r,indent=2)+'\n');print(name,r['status'],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:rows=list(ex.map(run,jobs))
    report={'status':'PASS' if all(x['status']=='PASS'for x in rows) else 'FAIL','gates':rows,'scope':'Finite arithmetic, source/log reconciliation, and figure-data generation. Not Lean compilation or universal proof.'}
    (dest/'SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n');print('Report:',dest/'SUMMARY.json');raise SystemExit(report['status']!='PASS')
if __name__=='__main__':main()
