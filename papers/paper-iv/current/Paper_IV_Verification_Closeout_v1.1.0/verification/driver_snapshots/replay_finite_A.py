#!/usr/bin/env python3
"""Run the recovered Paper IV finite suites without mutating historical evidence."""
from pathlib import Path
import argparse, hashlib, importlib.metadata, importlib.util, json, os, subprocess, sys, tempfile, time, signal
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'publication_baseline'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve()
 if out.exists():raise SystemExit('Choose a new output directory; prior results are immutable.')
 out.mkdir(parents=True);report={'schema':'paper_iv.finite_replay.v1','status':'RUNNING','python':sys.version,'dependencies':{},'checks':[],'scope':'Bounded arithmetic and historical-source regression checks, not universal mathematical proofs.'}
 for name in ['sympy','mpmath','numpy','pandas','matplotlib']:
  try:report['dependencies'][name]=importlib.metadata.version(name)
  except importlib.metadata.PackageNotFoundError:report['dependencies'][name]=None
 def save(): (out/'FINITE_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n')
 def run(name,cmd,result=None):
  log=out/(name+'.log');start=time.monotonic();print('RUN',name,flush=True)
  with log.open('wb') as f:
   p=subprocess.Popen(cmd,cwd=BASE,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   timed=False
   try:rc=p.wait(timeout=600)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait();timed=True
  row={'name':name,'argv':cmd,'returncode':rc,'timed_out':timed,'seconds':round(time.monotonic()-start,3),'log_sha256':sha(log),'log':log.name,'status':'PASS' if rc==0 and not timed else 'FAIL'}
  if result and result.exists():row['result_sha256']=sha(result);row['result']=result.name
  report['checks'].append(row);save();print(row['status'],name,row['seconds'],flush=True)
  if row['status']!='PASS':raise RuntimeError(name+' failed')
 try:
  before={p.relative_to(BASE).as_posix():sha(p) for p in BASE.rglob('*') if p.is_file()}
  run('algebra_exact',[sys.executable,'-B','audit/algebra_exact_checks.py'])
  stages=[
   ('exact_visual','source/complete/visual_appendix/checks/verify_examples.py','source/complete/visual_appendix/checks/EXACT_CHECKS.json','visual_result.json'),
   ('original_tables','source/strengthened/verification/verify_original_tables.py','source/strengthened/verification/ORIGINAL_TABLE_RERUN_RESULTS.txt','tables_result.txt'),
   ('strengthened','source/strengthened/verification/verify_paper4_strengthened.py','source/strengthened/verification/STRENGTHENED_RERUN_RESULTS.txt','strengthened_result.txt'),
   ('original_paper','source/strengthened/verification/verify_original_paper.py','source/strengthened/verification/ORIGINAL_PAPER_RERUN_RESULTS.txt','original_result.txt')]
  for name,script,historical,result in stages:
   target=out/result;run(name,[sys.executable,'-B','verification/monograph_checks/run_inherited.py',script,historical,str(target)],target)
  # Reuse only the exact arithmetic functions, not the inaccurate historical environment report.
  path=BASE/'verification/scripts/verify_available.py';spec=importlib.util.spec_from_file_location('paper_iv_exact',path);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
  tables=mod.numeric_tables(BASE/'source/strengthened/verification/original_data');brackets=mod.brackets(BASE/'source/complete/visual_appendix/checks/EXACT_CHECKS.json')
  (out/'rational_tables_and_brackets.json').write_text(json.dumps({'tables':tables,'brackets':brackets},indent=2)+'\n');report['rational_tables_and_brackets']={'status':'PASS','rows':tables['total_rows'],'brackets':len(brackets['brackets'])}
  after={p.relative_to(BASE).as_posix():sha(p) for p in BASE.rglob('*') if p.is_file()}
  if before!=after:raise RuntimeError('Historical baseline changed during finite replay')
  report['baseline_files_unchanged']=len(before);report['status']='PASS';save();return 0
 except BaseException as exc:report['status']='FAILED';report['error']=str(exc);save();print(exc,flush=True);return 1
if __name__=='__main__':sys.exit(main())
