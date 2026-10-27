#!/usr/bin/env python3
"""Run the known Series06 audit commands in a new destination.

Commands below are fixed reviewed argv arrays. This does not execute commands
from evidence manifests. Requires Python, SymPy, NumPy and Matplotlib. Copies
reviewed code/data first and preserves this evidence directory unchanged.
"""
from __future__ import annotations
import argparse,importlib.metadata,json,platform,shutil,subprocess,sys
from pathlib import Path

SPECS=[
 ('carrier70','carrier70_contract.json',['work/carrier70/verify_certificate.py'],['work/carrier70/verify_certificate.py','--out']),
 ('transfer','transfer_contract.json',['work/transfer/checks/verify.py','work/transfer/results/transfer210.json'],['work/transfer/checks/verify.py','--out']),
 ('dual_cycles','dual_cycles_contract.json',['work/dual_cycles/checks/verify_all.py','work/dual_cycles/checks/capacity_inputs.json','work/dual_cycles/predecessor/Komorebi_Hodge_Carrier70_v0.1.0.zip'],['work/dual_cycles/checks/verify_all.py','--out']),
 ('weil','weil_contract.json',['work/weil/check_weil_candidate.py'],['work/weil/check_weil_candidate.py','--output']),
 ('dyadic_symbolic','dyadic_symbolic_contract.json',['work/dyadic/fermat_hodge_dyadic_uniqueness.py'],['work/dyadic/fermat_hodge_dyadic_uniqueness.py','--phase','symbolic','--max-symbolic-s','9','--out']),
 ('dyadic_exhaustive','dyadic_exhaustive_contract.json',['work/dyadic/fermat_hodge_dyadic_uniqueness.py'],['work/dyadic/fermat_hodge_dyadic_uniqueness.py','--phase','exhaustive','--max-exhaustive-m','32','--out']),
 ('dyadic_exhaustive128','dyadic_exhaustive128_contract.json',['work/dyadic/fermat_hodge_dyadic_uniqueness.py'],['work/dyadic/fermat_hodge_dyadic_uniqueness.py','--phase','exhaustive','--max-exhaustive-m','128','--out']),
 ('orthogonal','orthogonal_contract.json',['checks/orthogonal_checks.py','work/transfer/results/transfer210.json','work/dual_cycles/checks/capacity_inputs.json','work/k23/Fermat_Hodge_K23_CM_Type_Audit.json','runs/dyadic_exhaustive/result.json'],['checks/orthogonal_checks.py','--out']),
 ('weighted_dyadic','weighted_dyadic_contract.json',['checks/weighted_dyadic_check.py'],['checks/weighted_dyadic_check.py','--out']),
 ('k23_regenerated','k23_contract.json',['checks/regenerate_k23.py','work/k23/Fermat_Hodge_K23_CM_Type_Audit.json'],['checks/regenerate_k23.py','--out']),
 ('fermat33','fermat33_contract.json',['checks/replay_legacy.py','work/legacy/hodge_fermat33_klein_closure.py'],['checks/replay_legacy.py','--source','work/legacy/hodge_fermat33_klein_closure.py','--out']),
 ('klein_tower','klein_tower_contract.json',['checks/replay_legacy.py','work/legacy/hodge_infinite_klein_tower.py'],['checks/replay_legacy.py','--source','work/legacy/hodge_infinite_klein_tower.py','--out']),
 ('conductor','conductor_contract.json',['checks/replay_legacy.py','work/legacy/hodge_infinite_conductor_polyphase_v2.py'],['checks/replay_legacy.py','--source','work/legacy/hodge_infinite_conductor_polyphase_v2.py','--out']),
 ('odd_prime','odd_prime_contract.json',['checks/replay_legacy.py','work/legacy/fermat_hodge_odd_prime_power_audit.py'],['checks/replay_legacy.py','--odd','--source','work/legacy/fermat_hodge_odd_prime_power_audit.py','--out']),
 ('toys','toys_contract.json',['checks/replay_toys.py','work/legacy/projector_resolved_hodge_calculus.py'],['checks/replay_toys.py','--source','work/legacy/projector_resolved_hodge_calculus.py','--out'])
]

def main():
 p=argparse.ArgumentParser();p.add_argument('--destination',type=Path,required=True);a=p.parse_args()
 source=Path(__file__).resolve().parent;dest=a.destination.resolve()
 if dest.exists():raise SystemExit('Destination must be new. Existing evidence is never overwritten.')
 dest.mkdir(parents=True)
 for name in ('checks','helpers','work'):
  shutil.copytree(source/name,dest/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 versions={'Python':platform.python_version(),'SymPy':importlib.metadata.version('sympy'),'NumPy':importlib.metadata.version('numpy'),'Matplotlib':importlib.metadata.version('matplotlib')}
 for fn in source.glob('*_contract.json'):
  contract=json.loads(fn.read_text())
  for software in contract['software']:
   if software['name'] in versions:software['version']=versions[software['name']]
  (dest/fn.name).write_text(json.dumps(contract,indent=2)+'\n')
 outputs=[]
 for key,contract,inputs,argv in SPECS:
  cmd=[sys.executable,'helpers/run_experiment.py','--root',str(dest),'--contract',contract]
  for f in inputs:cmd+=['--input',f]
  result=f'runs/{key}/result.json'
  cmd+=['--output',f'runs/{key}','--result',result,'--timeout','120','--max-output-bytes','2097152','--max-memory-bytes','4294967296','--max-cpu-seconds','90','--max-cores','1','--max-threads','1','--',sys.executable,*argv,result]
  subprocess.run(cmd,cwd=dest,check=True)
  subprocess.run([sys.executable,'helpers/validate_manifest.py',f'runs/{key}/manifest.json','--root',str(dest)],cwd=dest,check=True)
  outputs.append(key)
 (dest/'REPLAY_COMPLETED.json').write_text(json.dumps({'status':'PASS','runs':outputs,'nonclaims':['Finite execution does not certify a universal Hodge proof']},indent=2)+'\n')
 print('All reviewed runs completed:',dest)
if __name__=='__main__':main()
