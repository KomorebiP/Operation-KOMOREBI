#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parents[2]
d=root/'evidence/arithmetic';out=root/sys.argv[1]
runs=[('cyclotomic','cyclotomic_check113.py',[]),('simple_character','self_twist113.py',[]),('original_central','central_twist113.py',['0']),('corrected_central','central_twist113.py',['1']),('opposite_central','central_twist113.py',['2']),('normalization','central_normalization_check113.py',[])]
results={}
for name,script,args in runs:
 p=subprocess.run([sys.executable,str(d/script),*args],capture_output=True,text=True,timeout=30,cwd=root)
 assert p.returncode==0,(name,p.stderr)
 obj=json.loads(p.stdout)
 assert obj.get('all_checks_pass',obj.get('all_assertions_pass',True))
 results[name]=obj
assert not results['original_central']['remaining_scalar_is_one']
assert results['original_central']['uniformizer_commutator_H_character']=='1/3'
assert results['corrected_central']['remaining_scalar_is_one']
assert results['corrected_central']['uniformizer_commutator_H_character']=='0'
assert not results['opposite_central']['remaining_scalar_is_one']
assert results['opposite_central']['uniformizer_commutator_H_character']=='2/3'
(out/'result.json').write_text(json.dumps({'all_assertions_pass':True,'results':results,'non_claim':'No corrected-theta AI occurrence, H5, or Claim16.2 proof.'},indent=2)+'\n')
print('All six exact arithmetic executions pass; central scalar sequence: zeta3, 1, zeta3^2.')
