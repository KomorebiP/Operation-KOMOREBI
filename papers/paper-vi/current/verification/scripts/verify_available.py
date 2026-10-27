#!/usr/bin/env python3
"""Reproduce available Paper VI gates in disposable copies, preserving recovered sources."""
from __future__ import annotations
import argparse, datetime, hashlib, importlib.util, json, math, os, platform, re, shutil, subprocess, sys, tempfile, time, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(p):return {x.relative_to(p).as_posix():digest(x) for x in sorted(p.rglob('*')) if x.is_file()}
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def flatten(x,p=''):
 if isinstance(x,dict):return {kk:vv for k,v in x.items() for kk,vv in flatten(v,p+'/'+str(k)).items()}
 if isinstance(x,list):return {kk:vv for k,v in enumerate(x) for kk,vv in flatten(v,p+'/'+str(k)).items()}
 return {p:x}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--downloads',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
 source=args.source.resolve();downloads=args.downloads.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
 before=tree(source);started=datetime.datetime.now(datetime.timezone.utc).isoformat();t0=time.monotonic()
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
 libs={}
 for name in ['numpy','scipy','matplotlib','sympy','mpmath','pytest']:
  try:mod=__import__(name);libs[name]={'available':True,'version':getattr(mod,'__version__','unknown')}
  except ImportError:libs[name]={'available':False}
 environment={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'libraries':libs,'lean':shutil.which('lean'),'lake':shutil.which('lake'),'python_optimization_level':sys.flags.optimize}
 if sys.flags.optimize:raise RuntimeError('Cannot run original assertions under optimized Python')
 commands=[]
 def run(name,argv,cwd,timeout=180):
  tick=time.monotonic();p=subprocess.run(argv,cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout)
  (out/(name+'.stdout.txt')).write_text(p.stdout);(out/(name+'.stderr.txt')).write_text(p.stderr)
  rec={'name':name,'argv':[str(x) for x in argv],'cwd':str(cwd),'timeout_seconds':timeout,'elapsed_seconds':time.monotonic()-tick,'exit_code':p.returncode,'status':'PASS' if p.returncode==0 else 'FAIL'};commands.append(rec)
  if p.returncode:raise RuntimeError(name+' failed; see raw logs')
  return p.stdout
 archives=[]
 mapping={'complete':'Paper_VI_Complete_v0.5.0_With_Visual_Appendix.zip','strengthened':'PSC_Paper_VI_Strengthened_Annals_Edition_Package.zip','annals':'PSC_Paper_VI_Annals_Human_Edition_Package.zip'}
 for branch,filename in mapping.items():
  p=downloads/filename
  with zipfile.ZipFile(p) as z:
   if z.testzip() is not None:raise RuntimeError('ZIP CRC failed')
   names=[n for n in z.namelist() if not n.endswith('/')];prefix=names[0].split('/')[0]+'/'
   expected={n[len(prefix):]:hashlib.sha256(z.read(n)).hexdigest() for n in names}
  actual=tree(source/branch)
  if expected!=actual:raise RuntimeError('Archive extraction mismatch '+branch)
  archives.append({'branch':branch,'archive':filename,'sha256':digest(p),'bytes':p.stat().st_size,'files':len(expected),'crc':'PASS','exact_file_set_and_byte_match':True})
 pins=json.loads((source/'complete/verification/ORIGINAL_SNAPSHOT_HASHES.json').read_text());snapshot=tree(source/'complete/original_snapshot')
 if snapshot!=pins:raise RuntimeError('Original snapshot manifest mismatch')
 with tempfile.TemporaryDirectory(prefix='isolated-',dir=out) as tmp:
  tmp=Path(tmp);shutil.copytree(source,tmp/'source');s=tmp/'source';original=s/'complete/original_snapshot'
  code="import sys,json;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'verification'));import verify;print(json.dumps(verify.static_checks(Path(sys.argv[1])),indent=2))"
  static=json.loads(run('static_contract',[sys.executable,'-B','-c',code,str(original)],tmp))
  run('original_verifier_controls',[sys.executable,'-B',str(original/'verification/test_verifier.py')],original)
  run('companion_direct_and_boundary',[sys.executable,'-B',str(HERE/'run_companion_subset.py'),'--companion',str(original/'companion'),'--out',str(out/'COMPANION_REPLAY.json')],tmp)
  code="import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from projector_transfer_semigroups.experiments import run_experiments;run_experiments(Path(sys.argv[2]));print('Original run_experiments completed; figures were not regenerated.')"
  run('original_experiments',[sys.executable,'-B','-c',code,str(original/'companion'),str(out/'NUMERICAL_RESULTS.json')],tmp)
  old=flatten(json.loads((original/'companion/results/numerical_results.json').read_text()));new=flatten(json.loads((out/'NUMERICAL_RESULTS.json').read_text()))
  if set(old)!=set(new):raise RuntimeError('Numerical result key mismatch')
  rows=[]
  for k,v in old.items():
   w=new[k]
   if isinstance(v,(float,int)) and not isinstance(v,bool):
    okay=math.isfinite(v) and math.isfinite(w) and math.isclose(v,w,rel_tol=1e-7,abs_tol=5e-10)
    rows.append({'path':k,'inherited':v,'fresh':w,'same_float':v==w,'within_tolerance':okay})
    if not okay:raise RuntimeError('Numerical difference: '+k)
   elif v!=w:raise RuntimeError('Non-numeric field difference '+k)
  numerical={'status':'PASS','numerical_fields':len(rows),'tolerance':{'relative':1e-7,'absolute':5e-10},'bit_equal_float_fields':sum(r['same_float'] for r in rows),'fields':rows,'meaning':'Agreement of numerical output values under the historical tolerance, not exact mathematics.'};write(out/'NUMERICAL_COMPARISON.json',numerical)
  suites=[]
  for branch,script,name in [('annals','verify_paper_vi.py','annals_numerical'),('strengthened','verify_paper_vi.py','strengthened_baseline'),('strengthened','verify_paper_vi_strengthened.py','strengthened_expanded')]:
   stdout=run(name,[sys.executable,'-B',str(s/branch/'verification'/script)],s/branch,240)
   match=re.search(r'(\d+)/(\d+) checks passed in (\d+) groups',stdout)
   if not match or match[1]!=match[2]:raise RuntimeError('Missing suite success summary')
   suites.append({'name':name,'branch':branch,'script':script,'checks_reported':int(match[1]),'groups':int(match[3]),'status':'PASS','meaning':'Original mixed tally of finite numerical comparisons and source/package assertions; not theorem count.'})
   if branch=='annals':shutil.copy2(s/branch/'verification/verification_results.json',out/'ANNALS_NUMERICAL_RESULTS.json')
  exact_text=run('independent_exact_rational',[sys.executable,'-B',str(HERE/'exact_rational_checks.py')],tmp)
  exact=json.loads(exact_text);write(out/'EXACT_RATIONAL_RESULTS.json',exact)
 after=tree(source)
 if before!=after:raise RuntimeError('Recovered source changed during verification')
 inherited=json.loads((source/'complete/original_snapshot/verification/verification_status.json').read_text())
 report={'status':'PASS_AVAILABLE_GATES','started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-t0,'environment':environment,'source_files_verified_unchanged':len(before),'source_sha256':before,'archive_reconciliation':archives,'original_snapshot_files':len(pins),'fresh':{'static_source_contract':static,'original_unittest_verifier_controls':6,'companion_unchanged_direct_test_functions':37,'companion_independent_boundary_cases':17,'original_experiment_numeric_fields_compared':len(rows),'original_numerical_suites':suites,'independent_exact_rational_checks':exact['checks_passed'],'independent_exact_false_controls':exact['false_controls_rejected']},'inherited':{'formal_release':'0.5.0-checked-fifth-block','recorded_timestamp':inherited['timestamp_utc'],'scoped_complete_results':33,'supporting_theorem_declarations':341,'production_proof_modules':47,'namespace_declarations':782,'original_pytest_cases':54,'original_visual_sympy_assertions':204,'original_visual_false_controls':11,'open_conjectures_excluded':3},'not_run':[{'gate':'Lean compiler build and namespace axiom audit','reason':'Lean and lake unavailable. No installation attempted.'},{'gate':'Original full verification/verify.py gate, including pytest dispatch','reason':'pytest unavailable; original 37 functions and 17 independently coded boundary cases are labeled separately.'},{'gate':'Original 204 SymPy visual assertions and 11 controls','reason':'SymPy unavailable; new finite Fraction witnesses cover only the listed finite examples.'},{'gate':'Original 19 companion figure-pair regeneration and 26 visual plate generation','reason':'Outside this computation run. Original figure bytes are preserved; PDF production is a separate step.'}],'non_claims':['No new Lean kernel verification.','Finite numerical and rational witnesses do not imply universal analytic results or close the three conjectures.','Source token scanning does not prove Lean source semantics or mathematical correspondence.','Numerical suite tallies have different counting conventions and overlap; do not sum them into a count of independent results.'],'commands':commands}
 write(out/'CURRENT_VERIFICATION.json',report)
 print(json.dumps({'status':report['status'],'source_files':len(before),'fresh':report['fresh'],'not_run':report['not_run']},indent=2))
if __name__=='__main__':main()
