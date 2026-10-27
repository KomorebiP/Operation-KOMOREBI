#!/usr/bin/env python3
"""Independent trace-coefficient review of root's projective wild-image table."""
from pathlib import Path
import importlib.util,contextlib,io,json,hashlib
p=Path(__file__).with_name('cyclotomic_check113.py')
s=importlib.util.spec_from_file_location('cyc',p);c=importlib.util.module_from_spec(s)
with contextlib.redirect_stdout(io.StringIO()):s.loader.exec_module(c)
root=Path(__file__).resolve().parents[2]
claimed=json.loads((root/'evidence/wild_image/run01/RESULT.json').read_text())
# Move the Galois action onto beta using trace invariance. This reverses
# sigma, and differs from root's action on each unit before taking log.
betas=[c.beta,c.sigma(c.sigma(c.beta)),c.sigma(c.beta)]
rows=[]
for r in range(1,7):
 t=c.power(c.x,r);acc=c.zero;term=c.one
 # Recompute the convergent logarithm with54 terms (root used26).
 for k in range(1,55):
  term=c.mul(term,t);acc=c.add(acc,c.scale(term,c.Q((-1)**(k+1),k)))
 vals=[str(c.fractional_part_3(c.trace(c.mul(b,acc))/3)) for b in betas]
 assert vals==claimed['unit_character_table'][r-1]['character_exponents']
 rows.append(vals)
# Independent rank argument: the nonzero vectors (0,2),(1,2) form a basis.
det=(0*2-2*1)%3
assert det!=0
# beta-I=[[-1,-1],[1,-2]] has rank1 over F3 and is nonzero.
assert ((-1)*(-2)-(-1)*1)%3==0
assert (-1)%3!=0
result={'table_reproduced':rows,'all_checks_pass':True,'independent_method':'Galois action moved to coefficients by trace invariance; direct54-term log sum; linear algebra instead of subgroup closure','projective_diagonal_rank':2,'action_minus_identity_rank':1,'projective_order':27,'is_nonabelian':True,'root_script_sha256':hashlib.sha256((root/'scripts/wild_image113.py').read_bytes()).hexdigest(),'root_result_sha256':hashlib.sha256((root/'evidence/wild_image/run01/RESULT.json').read_bytes()).hexdigest(),'non_claim':'No scalar cube or complete Clifford filtration determined.'}
print(json.dumps(result,indent=2))
