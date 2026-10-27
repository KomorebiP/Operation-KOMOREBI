#!/usr/bin/env python3
"""Run narrow source replays with current software and version2 manifests."""
from __future__ import annotations
import argparse,importlib.metadata,json,platform,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
CHECKS=ROOT/'verification/monograph_checks'
def main():
 p=argparse.ArgumentParser();p.add_argument('--modes',nargs='+',default=['integrity','static','unit','original','sixth','fifth','structured','test-functions','sympy'],choices=['integrity','static','unit','original','sixth','fifth','structured','test-functions','pytest','sympy','portable','vectors']);p.add_argument('--suffix',default='20261009');a=p.parse_args()
 software=[{'name':'Python','version':platform.python_version()}]+[{'name':x,'version':importlib.metadata.version(x)} for x in ['numpy','scipy','pandas','matplotlib','sympy']]
 basic=['verification/monograph_checks/replay_isolated.py','verification/checks/replay.py','verification/checks/run_experiment.py','verification/checks/validate_manifest.py']
 source=[q.relative_to(ROOT).as_posix() for q in sorted((ROOT/'source').rglob('*')) if q.is_file()]
 guides=[q.relative_to(ROOT).as_posix() for q in sorted((ROOT/'editable/visual_guide').rglob('*.py')) if q.is_file()]
 paths=[]
 for mode in a.modes:
  if mode in ['sympy','portable','vectors','pytest']:
   contract={'claim_id':'PAPER_VIII_MONOGRAPH_'+mode.upper()+'_BOUNDED_REPLAY_'+a.suffix,'mathematics':{'assertion_tested':{'sympy':'190 unchanged original SymPy exact worked assertions and11 deliberately false shortcut controls.','portable':'208 independent integer/rational/Gaussian-rational finite assertions and15 shortcut controls on displayed guide models.','vectors':'30 original deterministic vector plates generated; compare delivered authored geometry separately.','pytest':'Actual pytest collection/execution of34unchanged archival tests.'}[mode],'coefficient_domain':'Exact SymPy integer/rational symbolic arithmetic and independent fractions.Fraction/Q(i) worked models; plotting coordinates convert stated formulas to decimal geometry. Archival pytest numeric comparisons retain source binary64 tolerances.','conventions':'Entries(target,source); conjugate transpose in complex isometries; ordinary transpose for column-major vectorization; declared finite model costs are not timing results.','inputs':guides if mode!='pytest' else source,'bounds':{'positive':190 if mode=='sympy' else 208 if mode=='portable' else 34 if mode=='pytest' else 30,'controls':11 if mode=='sympy' else 15 if mode=='portable' else 0,'scope':'Unchanged finite examples and source test family; no extrapolation.'},'non_claims':['No Lean or Lake kernel execution.','No CPU/GPU/CUDA benchmark reproduction or correctness-reference authentication.','No universal theorem proved by these finite cases.','Repeated independent portable and original symbolic assertions overlap as model examples.']},'randomness':{'used':False,'generator':'','seed':None}}
  else:
   contract=json.loads((ROOT/'verification/contracts'/f'{mode}.json').read_text());contract['claim_id']='PAPER_VIII_MONOGRAPH_'+mode.upper()+'_BOUNDED_REPLAY_'+a.suffix
  artifacts=basic+source
  if mode in ['sympy','portable','vectors']:artifacts+=guides
  if mode=='portable':artifacts+=['editable/visual_guide/source/pages.tex','editable/visual_guide/source/extended_pages.tex']
  if mode=='vectors':artifacts += [q.relative_to(ROOT).as_posix() for q in sorted((ROOT/'editable/visual_guide/graphics').glob('*.tex'))]
  if mode=='pytest':software.append({'name':'pytest','version':importlib.metadata.version('pytest')})
  contract['software']=software;contract['execution_artifacts']=artifacts
  cp=CHECKS/'contracts'/f'{mode}_{a.suffix}.json';cp.parent.mkdir(parents=True,exist_ok=True);cp.write_text(json.dumps(contract,indent=2)+'\n')
  dest=f'verification/monograph_checks/run_{mode}_{a.suffix}'
  cmd=[sys.executable,'verification/checks/run_experiment.py','--root',str(ROOT),'--contract',str(cp),'--output',dest,'--result',dest+'/result.json','--timeout','240','--max-output-bytes','4194304','--max-memory-bytes','2147483648','--max-cpu-seconds','210','--max-cores','1','--max-threads','1']
  if mode=='vectors':
   for q in sorted((ROOT/'editable/visual_guide/graphics').glob('*.tex')):cmd+=['--result',dest+'/generated_graphics/'+q.name]
  for rel in artifacts:cmd+=['--input',rel]
  cmd+=['--',sys.executable,'verification/monograph_checks/replay_isolated.py',mode,'--out',dest]
  r=subprocess.run(cmd,cwd=ROOT);assert r.returncode==0,(mode,r.returncode)
  val=subprocess.run([sys.executable,'verification/checks/validate_manifest.py',dest+'/manifest.json','--root',str(ROOT)],cwd=ROOT,text=True,capture_output=True)
  (ROOT/dest/'VALIDATION.txt').write_text(val.stdout+val.stderr);assert val.returncode==0,(mode,val.stdout,val.stderr)
  paths.append(dest+'/manifest.json');print('PASS CURRENT MANIFEST:',mode,flush=True)
 print(json.dumps(paths,indent=2))
if __name__=='__main__':main()
