#!/usr/bin/env python3
"""Regenerate the bounded finite assertions; audit exact predecessor bytes.
No network, package installation, or mathematical proof claim is made here.
"""
from __future__ import annotations
import argparse,copy,hashlib,io,json,os,platform,shutil,subprocess,sys,tempfile,time,zipfile
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
PREDECESSOR='predecessor/Komorebi_Beal_Block78_Finite_Local_Flexibility_v7.8.0.zip'
PRE_SHA='52f161856a358670436bf42d18dc9654a1db60b82010e6979f8b7dafd3821713'
def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def check_files(root,entries):
 for rel,digest in entries.items():
  p=Path(rel)
  if p.is_absolute() or '..' in p.parts:raise AssertionError('unsafe manifest path')
  if not (root/p).is_file() or sha(root/p)!=digest:raise AssertionError('changed or missing '+rel)
def check_lineage():
 rec=json.loads((ROOT/'work79/source_records/INHERITED_INPUTS.json').read_text())
 assert sha(ROOT/PREDECESSOR)==PRE_SHA==rec['predecessor_sha256']
 left=rec['leaves'][:];raw=(ROOT/PREDECESSOR).read_bytes();depth=0
 while left:
  z=zipfile.ZipFile(io.BytesIO(raw));this=[r for r in left if r['archive_depth']==depth]
  for r in this:
   assert hashlib.sha256(raw).hexdigest()==r['archive_sha256']
   assert hashlib.sha256(z.read(r['archive_member'])).hexdigest()==r['sha256']
   left.remove(r)
  if not left:break
  ps=[n for n in z.namelist() if n.endswith('.zip') and (n.startswith('predecessor/') or '/predecessor/' in n)]
  assert len(ps)==1,ps
  raw=z.read(ps[0]);depth+=1
 return len(rec['leaves']),depth+1

def rank(M):
 A=[r[:] for r in M];i=0
 for j in range(len(A[0])):
  k=next((k for k in range(i,len(A)) if A[k][j]%7),None)
  if k is None:continue
  A[i],A[k]=A[k],A[i];iv=pow(A[i][j]%7,-1,7);A[i]=[v*iv%7 for v in A[i]]
  for k in range(i+1,len(A)):
   t=A[k][j];A[k]=[(x-t*y)%7 for x,y in zip(A[k],A[i])]
  i+=1
  if i==len(A):break
 return i

def validate_result(d):
 assert d['status']=='PASS' and d['version']=='7.9.0'
 a=d['nilpotence_and_support']
 assert a['traceless_matrices']==117649 and a['nilpotent_matrices']==2401
 assert a['nilpotents_with_lower_zero']==49 and a['support_packets']==806736
 assert a['quadratic_wrong_sign_rejected']==790272
 aux=d['auxiliary_toric'];assert aux['cases']==33614 and aux['norm_one_mod7_beta_zero_cases']==28812
 assert aux['nonzero_upper_inertia_allowed'] and not aux['all_candidates_excluded']
 rr=d['restricted_p_tangent'];assert rr['patterns_eliminated']==0 and rr['not_an_absolute_affine_solution']
 cols={v['q']:v for v in rr['residue_data']}
 for lab,e in rr['patterns'].items():
  S=e['support'];assert len(S)==9 and len(set(S))==9
  fixed=[[cols[q]['unit_logs'][i] for q in S] for i in range(5)]
  assert fixed==e['fixed_rows'] and rank(fixed)==e['fixed_rank']==3
  minus=[q for q in S if q%7==6];assert e['extra_frobenius_primes']==minus
  M=fixed+[[(0 if q==ell else cols[q]['rational_logs'][str(ell)]) for q in S] for ell in minus]
  assert M==e['augmented_rows']
  n={'A':6,'B':6,'C':5,'D':6}[lab];assert rank(M)==e['augmented_rank']==n
  basis=e['kernel_basis'];assert len(basis)==9-n and rank(basis)==len(basis)
  assert all(sum(a*b for a,b in zip(row,v))%7==0 for row in M for v in basis)
  assert e['semilinear_difference_dimension_bound']==len(basis)
  assert e['plus_dimension']+e['minus_dimension']==len(basis)
  assert e['affine_count_bound_over_k_if_nonempty']==49**len(basis)
  assert e['common_semilinear_frame_count_bound_if_nonempty']==7**len(basis)
 pc=d['local_positive_control'];p=pc['prime'];B=int(pc['B_mod_q8']);m=p**8
 assert p==5167 and pc['A']==3238 and pc['C']==5167 and pc['B_mod_q']==3658
 assert 0<=B<m and (pow(B,5,m)+pc['A']**3-pc['C']**7)%m==0
 assert pc['local_frey_only'] and pc['ordinary_integer_B_not_claimed']

def rejection_tests(d):
 tests=[]
 def reject(name,change):
  e=copy.deepcopy(d);change(e)
  try:validate_result(e)
  except (AssertionError,KeyError,ValueError):tests.append(name);return
  raise AssertionError('corruption accepted: '+name)
 reject('false nilpotent count',lambda e:e['nilpotence_and_support'].__setitem__('nilpotents_with_lower_zero',50))
 reject('wrong quadratic sign count',lambda e:e['nilpotence_and_support'].__setitem__('quadratic_wrong_sign_rejected',0))
 reject('false upper-inertia exclusion',lambda e:e['auxiliary_toric'].__setitem__('all_candidates_excluded',True))
 reject('changed kernel vector',lambda e:e['restricted_p_tangent']['patterns']['C']['kernel_basis'][0].__setitem__(0,(e['restricted_p_tangent']['patterns']['C']['kernel_basis'][0][0]+1)%7))
 reject('changed fixed-seven residue row',lambda e:e['restricted_p_tangent']['residue_data'][0]['unit_logs'].__setitem__(4,0))
 reject('invented empty affine set',lambda e:e['restricted_p_tangent']['patterns']['A'].__setitem__('common_semilinear_frame_count_bound_if_nonempty',0))
 reject('changed Hensel root',lambda e:e['local_positive_control'].__setitem__('B_mod_q8',str(int(e['local_positive_control']['B_mod_q8'])+1)))
 reject('omitted Frobenius condition',lambda e:e['restricted_p_tangent']['patterns']['A']['extra_frobenius_primes'].pop())
 reject('false elimination of eight patterns',lambda e:e['restricted_p_tangent'].__setitem__('patterns_eliminated',8))
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'README.md';p.write_bytes((ROOT/'README.md').read_bytes()+b'\nCORRUPTED\n')
  try:check_files(Path(td),{'README.md':sha(ROOT/'README.md')})
  except AssertionError:tests.append('modified payload')
  else:raise AssertionError('payload corruption accepted')
 return tests

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path);ap.add_argument('--replay-predecessor',action='store_true');args=ap.parse_args()
 start=time.monotonic();date=datetime.now(timezone.utc).isoformat()
 manifest=json.loads((ROOT/'MANIFEST.json').read_text());check_files(ROOT,manifest['files'])
 leaves,levels=check_lineage();statuses=[];results=[];env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
 with tempfile.TemporaryDirectory(prefix='beal79_rebuild_') as td:
  tmp=Path(td);src=tmp/'work79/computations';src.mkdir(parents=True)
  for p in (ROOT/'work79/computations').glob('*.py'):shutil.copy2(p,src/p.name)
  # No expected output is copied into the scratch calculation.
  assert not (tmp/'work79/verification').exists()
  for name in ['primary79','independent79']:
   t=time.monotonic();cp=subprocess.run([sys.executable,'-B',str(src/(name+'.py'))],cwd=tmp,env=env,text=True,capture_output=True)
   if cp.returncode:raise RuntimeError(name+' failed\n'+cp.stdout[-1000:]+cp.stderr[-3000:])
   got=json.loads((tmp/'work79/verification'/(name+'.json')).read_text());validate_result(got)
   frozen=json.loads((ROOT/'work79/verification'/(name+'.json')).read_text());assert got==frozen
   results.append(got);statuses.append({'name':name,'exit_status':cp.returncode,'runtime_seconds':round(time.monotonic()-t,4)})
 assert results[0]==results[1]
 corruptions=rejection_tests(results[0]);predecessor=None
 if args.replay_predecessor:
  with tempfile.TemporaryDirectory(prefix='beal78_replay_') as td:
   base=Path(td)
   with zipfile.ZipFile(ROOT/PREDECESSOR) as z:
    for n in z.namelist():
     assert not Path(n).is_absolute() and '..' not in Path(n).parts
    z.extractall(base)
   vp=base/'verify.py';assert vp.is_file()
   report=base/'replay.json';t=time.monotonic()
   cp=subprocess.run([sys.executable,'-B',str(vp),'--report',str(report)],cwd=base,env=env,text=True,capture_output=True)
   if cp.returncode:raise RuntimeError('predecessor failed\n'+cp.stderr[-3000:]+cp.stdout[-1000:])
   predecessor={'exit_status':0,'runtime_seconds':round(time.monotonic()-t,4),'result':json.loads(report.read_text()),'historical_chain_replayed':False}
 rec=ROOT/'work79/verification/COMPUTATION_MANIFEST.json'
 if rec.exists():
  cp=subprocess.run([sys.executable,'-B',str(ROOT/'work79/computations/validate_manifest_v1.py'),str(rec),'--root',str(ROOT)],text=True,capture_output=True)
  if cp.returncode:raise RuntimeError('computation record invalid: '+cp.stderr+cp.stdout)
 check_files(ROOT,manifest['files'])
 out={'status':'PASS_DECLARED_CHECKS','version':'7.9.0','started_at':date,
      'runtime_seconds':round(time.monotonic()-start,4),'process_exit_status':0,
      'python':platform.python_version(),'payload_hashes_checked':len(manifest['files']),
      'pinned_inherited_leaves':leaves,'archive_levels_inspected':levels,
      'predecessor_sha256':PRE_SHA,'scientific_runs':statuses,
      'full_result_equality':True,'corruptions_rejected':corruptions,
      'immediate_predecessor_replay':predecessor,
      'nonclaims':['No actual affine p0 computed','No full restricted Selmer nonemptiness/exclusion computation',
                  'No bounded pattern eliminated','No new Lean compilation','No independent mathematical review']}
 if args.report:
  args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 print('PASS_DECLARED_CHECKS');print(json.dumps(out,sort_keys=True,indent=2))
if __name__=='__main__':main()
