#!/usr/bin/env python3
"""Finite independent checks of the port; not a substitute for the Lean proofs."""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from itertools import product
from math import gcd
from pathlib import Path
import ast, hashlib, json, random, sys, time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from bounded_echelon import ArithmeticLog,BoundedEchelon,bounded_bezout,discover_bounded
from normalized_echelon import NormalizedEchelon,discover_normalized
from chainring import module_form
SEED=2026092108

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def enum_span(rows,m,d):
 return {tuple(sum(c[i]*rows[i][j] for i in range(len(rows)))%m for j in range(d)) for c in product(range(m),repeat=len(rows))}
def core_peak(log):return max((v for k,v in log.peaks.items() if k not in ['source_row','stored']),default=0)

def main():
 started=datetime.now(timezone.utc).isoformat();start=time.monotonic();counts=Counter();rng=random.Random(SEED)
 records=json.loads((ROOT/'v06_evidence/EXPORTED_DATA.json').read_text())
 inputs=[Path(__file__),ROOT/'bounded_echelon.py',ROOT/'normalized_echelon.py',ROOT/'integer_echelon.py',ROOT/'chainring.py',ROOT/'discover.py',ROOT/'v06_evidence/EXPORTED_DATA.json']+[ROOT/r['source'] for r in records]+sorted((ROOT/'formalization').glob('BoundedComputed*.lean'))
 before={str(p.relative_to(ROOT)):sha(p) for p in set(inputs)}
 outcomes=[]
 for rec in records:
  src=json.loads((ROOT/rec['source']).read_text());tests,stats=discover_bounded(src);old,_=discover_normalized(src)
  assert tests==old==rec['result'];counts['frozen_ordered_outputs']+=1
  B=NormalizedEchelon(src['p']**src['r'],src['dimension'])
  from discover import observation_row
  # Rebuild the reference canonical lattice using original, actual observation rows.
  for test in tests:
   B.insert(observation_row(src,test['word'],test['observation']))
  assert B.rows==stats['final_basis'];counts['same_canonical_basis']+=1
  assert (tests,stats)==discover_bounded(src);counts['deterministic_port']+=1
  m=src['p']**src['r'];d=src['dimension'];a=stats['accepted'];c=stats['counts']
  assert stats['arithmetic_peak']<=stats['proved_cap'];counts['temporary_magnitude_cap']+=1
  assert stats['arithmetic_peak'].bit_length()<=stats['proved_bit_budget'];counts['temporary_bit_budget']+=1
  assert c.get('insert_levels',0)==a*d;counts['insert_level_count']+=1
  assert c.get('insertion_products',0)==2*a*d*(d-1);counts['insertion_product_count']+=1
  assert c.get('normalization_pivots',0)==a*d*(d-1)//2;counts['normalization_division_count']+=1
  assert c.get('normalization_products',0)==a*d*(d-1)*(d-2)//6;counts['normalization_product_count']+=1
  assert c.get('membership_pivots',0)<=stats['decisions']*d;counts['membership_level_bound']+=1
  assert stats['phase_peaks'].get('source_row',0)<=m*m+m;counts['source_row_operand_bound']+=1
  idx=rec['index'];prefix=f'c{idx:03}_';text=(ROOT/f'formalization/BoundedComputed{idx//12:02}.lean').read_text()
  def literal(name):
   line=next(l for l in text.splitlines() if l.startswith('def '+prefix+name+' :'))
   return ast.literal_eval(line.split(':=',1)[1].strip().replace('![','['))
  assert literal('A')==src['actions'] and literal('O')==src['observations'];counts['literal_source']+=1
  assert literal('result')==[(t['word'],t['observation']) for t in tests];counts['literal_output']+=1
  assert f'abbrev {prefix}R := ZMod ({src["p"]}^{src["r"]})' in text;counts['literal_modulus']+=1
  counts['accepted_tests']+=a;counts['queue_decisions']+=stats['decisions']
  outcomes.append({'index':idx,'source':rec['source'],'modulus':m,'dimension':d,**stats})
 # Exhaust all bounded signed Bezout inputs and compare with independent math.gcd.
 for q in range(1,65):
  for a in range(-256,257):
   log=ArithmeticLog();g,s,t=bounded_bezout(q,a,log)
   assert g==gcd(q,a) and q*s+a*t==g;counts['bezout_identity']+=1
   assert abs(s)<=max(1,abs(a)) and abs(t)<=q;counts['bezout_coefficients']+=1
   assert log.peaks['euclid']<=max(q,abs(a),1);counts['euclid_peak']+=1
   assert log.counts['euclid_divisions']<=2*abs(a).bit_length();counts['euclid_binary_depth']+=1
 # Consecutive Fibonacci numbers exercise long Euclidean chains rather than larger random inputs.
 f0,f1=1,1
 for n in range(1,161):
  f0,f1=f1,f0+f1
  for sign in [-1,1]:
   log=ArithmeticLog();g,s,t=bounded_bezout(f1,sign*f0,log)
   assert g==1 and f1*s+sign*f0*t==1
   assert log.peaks['euclid']<=f1 and log.counts['euclid_divisions']<=2*f0.bit_length()
   counts['fibonacci_signed_stress']+=1
 configs=[(1,2),(2,0),(2,2),(3,2),(4,2),(6,2),(8,1),(9,1),(12,1)]
 for m,d in configs:
  vectors=list(product(range(m),repeat=d))
  for length in range(3):
   for rows in product(vectors,repeat=length):
    B=BoundedEchelon(m,d)
    for v in rows:B.insert(v)
    expected=enum_span(rows,m,d)
    assert enum_span(B.rows,m,d)==expected;counts['exhaustive_basis_image']+=1
    C=BoundedEchelon(m,d)
    for v in reversed(rows):C.insert(v)
    assert B.key()==C.key();counts['exhaustive_canonical_order']+=1
    for v in vectors:
     cs=B.coordinates(v)
     assert (cs is not None)==(v in expected);counts['exhaustive_membership']+=1
     if cs is not None:
      assert [sum(cs[i]*B.rows[i][j] for i in range(d)) for j in range(d)]==list(v)
      counts['exact_integer_reconstruction']+=1
    assert core_peak(B.log)<=m*(2*m*(m+1))**d;counts['exhaustive_temporary_cap']+=1
 # Negative integer representatives have a C-dependent bound, not the canonical C=m bound.
 for case in range(90):
  p=[2,3,5][case%3];r=1+case%5;m=p**r;d=1+case%6
  rows=[[rng.randrange(-2*m,2*m) for _ in range(d)] for _ in range(1+case%7)]
  B=BoundedEchelon(m,d);C=NormalizedEchelon(m,d)
  for v in rows:
   B.log=ArithmeticLog();B.insert(v);C.insert(v)
   cap=max(m,*map(abs,v))*(2*m*(m+1))**d
   assert core_peak(B.log)<=cap;counts['signed_insertion_general_cap']+=1
   assert B.rows==C.rows;counts['signed_canonical_equality']+=1
  form=module_form([[x%m for x in row] for row in rows],p,r)
  for _ in range(12):
   v=[rng.randrange(-2*m,2*m) for _ in range(d)]
   assert B.contains(v)==(form.coordinates([x%m for x in v]) is not None)
   counts['independent_smith_membership']+=1
  changed=BoundedEchelon(m,d)
  for v in reversed(rows):changed.insert([x+m*rng.randrange(-3,4) for x in v])
  assert changed.key()==B.key();counts['representative_invariance']+=1
 B=BoundedEchelon(4,2);B.insert([3,3]);assert B.rows==[[1,1],[0,4]] and core_peak(B.log)==12
 counts['actual_temporary_exceeds_modulus']=1
 B=BoundedEchelon(64,2);B.insert([2,32]);assert B.rows==[[2,32],[0,64]] and B.contains([4,0]) and not B.contains([2,0]);counts['coupled_congruence_retained']=1
 rejected=[]
 def reject(name,f):
  try:f()
  except (ValueError,RuntimeError):rejected.append(name)
  else:raise AssertionError(name)
 reject('zero_modulus',lambda:BoundedEchelon(0,1));reject('negative_dimension',lambda:BoundedEchelon(4,-1))
 reject('false_modulus',lambda:BoundedEchelon(True,1));reject('bad_vector',lambda:BoundedEchelon(4,2).insert([1]))
 reject('float_vector',lambda:BoundedEchelon(4,1).insert([1.0]));reject('zero_pivot',lambda:bounded_bezout(0,1))
 reject('float_bezout',lambda:bounded_bezout(2,1.0));reject('negative_cap',lambda:discover_bounded(json.loads((ROOT/records[0]['source']).read_text()),candidate_cap=-1))
 reject('cap_unresolved',lambda:discover_bounded(json.loads((ROOT/records[0]['source']).read_text()),candidate_cap=0))
 counts['invalid_or_cap_rejections']=len(rejected)
 assert before=={str(p.relative_to(ROOT)):sha(p) for p in set(inputs)}
 result={'status':'PASS','started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':time.monotonic()-start,'seed':SEED,
  'counts':dict(counts),'cases':outcomes,'max_core_bits':max(x['arithmetic_peak'].bit_length() for x in outcomes),
  'max_stored_bits':max(x['phase_bits'].get('stored',0) for x in outcomes),'exhaustive_configs':configs,'maximum_generators':2,
  'bezout_q':[1,64],'bezout_a':[-256,256],'signed_fibonacci_pairs':320,'random_smith_cases':90,
  'rejections':rejected,'inputs':[{'path':p,'sha256':h} for p,h in sorted(before.items())],'all_inputs_unchanged':True,
  'non_claims':['Python is a separately audited port, not verified code extraction','Peak model is high-level coefficient arithmetic, not internal big-integer division or proof-checker memory','No wall-time speedup comparison','Random cases are not an exhaustive universal proof','No new held-out mathematical discovery']}
 dump(ROOT/'results_v08/PYTHON_AUDIT.json',result)
 print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','cases']},indent=2))
if __name__=='__main__':main()
