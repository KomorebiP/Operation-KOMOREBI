"""Exact port/value/cost audit. Finite checks do not replace universal Lean proofs."""
from pathlib import Path
from itertools import product
from collections import Counter
from datetime import datetime,timezone
from math import gcd
import ast,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from costed_echelon import Meter,euclid_coeff,euclid_gcd,signed_coeff,coordinates,residue,normalize,insert,update,discover_costed,units_bound
from bounded_echelon import BoundedEchelon,discover_bounded

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def span(rows,m,d):
 return {tuple(sum(c[i]*rows[i][j] for i in range(len(rows)))%m for j in range(d)) for c in product(range(m),repeat=len(rows))}
def steps(a,b):
 n=0
 while b:a,b=b,a%b;n+=1
 return n

def main():
 start=time.monotonic();started=datetime.now(timezone.utc).isoformat();counts=Counter()
 records=json.loads((ROOT/'source_records/EXPORTED_DATA.json').read_text())
 expected=json.loads((ROOT/'source_records/COSTED_CASES.json').read_text())
 inputs=[Path(__file__),ROOT/'costed_echelon.py',ROOT/'bounded_echelon.py',ROOT/'discover.py',ROOT/'chainring.py',ROOT/'source_records/EXPORTED_DATA.json',ROOT/'source_records/COSTED_CASES.json']
 inputs += [ROOT/x['source'] for x in records]+list((ROOT/'formalization').glob('CostedComputed*.lean'))
 before={str(p.relative_to(ROOT)):sha(p) for p in set(inputs)}
 results=[]
 for rec,saved in zip(records,expected,strict=True):
  src=json.loads((ROOT/rec['source']).read_text());ans,st=discover_costed(src);old,oldst=discover_bounded(src)
  assert ans==rec['result']==old;counts['ordered_answers']+=1
  assert st['final_basis']==oldst['final_basis'];counts['canonical_values']+=1
  assert st['units']==saved['units'];counts['deterministic_arithmetic_units']+=1
  assert st['units']==sum(st['unit_counts'].values())<=st['bound'];counts['complete_cost_bound']+=1
  p,r,d=src['p'],src['r'],src['dimension'];k=len(src['actions']);o=len(src['observations'])
  assert st['fuel']==o+k*r*d+1
  assert st['initial_units']==d*(d*d-1)//3;counts['initial_normalization_count']+=1
  idx=rec['index'];prefix=f'c{idx:03}_';text=(ROOT/f'formalization/CostedComputed{idx//12:02}.lean').read_text()
  def lit(name):
   line=next(x for x in text.splitlines() if x.startswith('def '+prefix+name+' :'))
   return ast.literal_eval(line.split(':=',1)[1].strip().replace('![','['))
  assert lit('A')==src['actions'] and lit('O')==src['observations'];counts['literal_source_binding']+=1
  assert lit('result')==[(t['word'],t['observation']) for t in ans];counts['literal_answer_binding']+=1
  assert f'(some {prefix}result, {st["units"]}) := by decide +kernel' in text;counts['literal_cost_binding']+=1
  assert f'ZMod ({p}^{r})' in text;counts['literal_modulus_binding']+=1
  counts['accepted_tests']+=st['accepted'];counts['queue_decisions']+=st['decisions'];counts['arithmetic_units']+=st['units']
  results.append({'index':idx,'source':rec['source'],**st})
 for q in range(1,65):
  for a in range(-64,65):
   met=Meter();s,t=signed_coeff(q,a,met);E=steps(q,abs(a))
   assert q*s+a*t==gcd(q,a);counts['bezout_values']+=1
   assert met.units==5*E+5;counts['bezout_exact_units']+=1
   met=Meter();g=euclid_gcd(q,abs(a),met)
   assert g==gcd(q,a) and met.units==2*E+1;counts['gcd_exact_units']+=1
   assert E<=2*abs(a).bit_length();counts['euclid_depth_bound']+=1
 configs=[(1,2),(2,0),(2,2),(3,2),(4,2),(6,2),(8,1),(9,1),(12,1)]
 for m,d in configs:
  vectors=list(product(range(m),repeat=d))
  for length in range(3):
   for rows in product(vectors,repeat=length):
    B=[[m if i==j else 0 for j in range(d)] for i in range(d)];old=BoundedEchelon(m,d)
    for v in rows:
     met=Meter();raw=insert(B,v,met)
     E=(met.counts['zero_compare']-2*d)//2
     assert met.units==3*d*d+8*d+7*E;counts['exact_insertion_decomposition']+=1
     met=Meter();B=normalize(raw,met)
     assert met.units==d*(d*d-1)//3;counts['exact_normalization_units']+=1
     old.insert(v);assert B==old.rows;counts['independent_insert_value']+=1
    expected_span=span(rows,m,d)
    for v in vectors:
     met=Meter();c=coordinates(B,v,met)
     assert (c is not None)==(v in expected_span);counts['exhaustive_membership_value']+=1
     assert met.units<=d*d+2*d;counts['membership_cost_bound']+=1
     if c is not None:
      assert [sum(c[i]*B[i][j] for i in range(d)) for j in range(d)]==list(v)
      assert met.units==d*d+2*d;counts['successful_membership_exact_count']+=1
     met=Meter();vmod=residue(B,v,met)
     assert met.units==d*(d+1);counts['residue_exact_units']+=1
     assert coordinates(B,[v[i]-vmod[i] for i in range(d)],Meter()) is not None
     counts['residue_coset_value']+=1
    counts['generating_lists']+=1
 # Zero fuel retains its costs and returns unresolved, never a successful empty list.
 src=json.loads((ROOT/records[0]['source']).read_text());ans,st=discover_costed(src,fuel=0)
 assert ans is None and not st['success'];counts['fuel_exhaustion_unresolved']+=1
 assert st['units']==st['initial_units'];counts['fuel_exhaustion_initial_cost']+=1
 rejected=[]
 def reject(name,fn):
  try:fn()
  except (ValueError,RuntimeError,TypeError):rejected.append(name)
  else:raise AssertionError(name)
 reject('bad_pivot',lambda:coordinates([[0]],[1],Meter()))
 reject('bad_dimension',lambda:coordinates([[2]],[1,2],Meter()))
 reject('float_coefficient',lambda:coordinates([[2]],[1.0],Meter()))
 reject('nontriangular_basis',lambda:normalize([[2,0],[1,2]],Meter()))
 reject('negative_fuel',lambda:discover_costed(src,fuel=-1))
 reject('boolean_fuel',lambda:discover_costed(src,fuel=True))
 counts['invalid_input_rejections']=len(rejected)
 assert before=={str(p.relative_to(ROOT)):sha(p) for p in set(inputs)}
 result={'status':'PASS','started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':time.monotonic()-start,
   'counts':dict(counts),'cases':results,'rejections':rejected,'exhaustive_modulus_dimensions':configs,'max_generator_list_length':2,
   'signed_bezout_q':[1,64],'signed_bezout_a':[-64,64], 'randomness_used':False,
   'inputs':[{'path':p,'sha256':h} for p,h in sorted(before.items())],'all_inputs_unchanged':True,
   'non_claims':['Python port is not verified extraction','Units belong to an explicitly stipulated scalar arithmetic model, not runtime instructions or bit operations','No state-space enumeration in discovery','No independent-referee or novelty verdict']}
 (ROOT/'results/PYTHON_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','cases']},indent=2))
if __name__=='__main__':main()
