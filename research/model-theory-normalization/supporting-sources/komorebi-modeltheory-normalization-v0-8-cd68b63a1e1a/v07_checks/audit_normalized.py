#!/usr/bin/env python3
"""Exact finite audit of the unverified Python port, separate from Lean proofs."""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from itertools import product
from datetime import datetime,timezone
import ast,copy,hashlib,json,random,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from normalized_echelon import normalize_rows,NormalizedEchelon,discover_normalized
from integer_echelon import IntegerEchelon,discover_echelon
from chainring import module_form

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def enum_span(rows,m,d):
 return {tuple(sum(c[i]*rows[i][j] for i in range(len(rows)))%m for j in range(d)) for c in product(range(m),repeat=len(rows))}
def bits(rows):return max((abs(x).bit_length() for row in rows for x in row),default=0)
def main():
 start=datetime.now(timezone.utc).isoformat();t=time.monotonic();counts=Counter();rng=random.Random(2026092107)
 records=json.loads((ROOT/'v06_evidence/EXPORTED_DATA.json').read_text())
 inputs=[Path(__file__),ROOT/'normalized_echelon.py',ROOT/'integer_echelon.py',ROOT/'discover.py',ROOT/'chainring.py',ROOT/'v06_evidence/EXPORTED_DATA.json']+[ROOT/r['source'] for r in records]+sorted((ROOT/'formalization').glob('NormalizedComputed*.lean'))
 before={str(p.relative_to(ROOT)):sha(p) for p in inputs};outcomes=[]
 # Baseline instrumentation measures at completed insertion boundaries, not inside updates.
 import integer_echelon,chainring,discover
 class OldCheckpoint(IntegerEchelon):
  def __post_init__(self):super().__post_init__();self.checkpoint_bits=bits(self.rows);baseline_objects.append(self)
  def insert(self,v):super().insert(v);self.checkpoint_bits=max(self.checkpoint_bits,bits(self.rows))
 baseline_objects=[]
 old_cls=integer_echelon.IntegerEchelon;old_mf=chainring.module_form;old_df=discover.module_form
 def forbidden(*a,**k):raise AssertionError('Smith called by an echelon discovery algorithm')
 integer_echelon.IntegerEchelon=OldCheckpoint;chainring.module_form=discover.module_form=forbidden
 try:
  for rec in records:
   source=json.loads((ROOT/rec['source']).read_text())
   tests,stats=discover_normalized(source);base_tests,base_stats=discover_echelon(source)
   assert tests==base_tests==rec['result'];counts['ordered_discovery_results']+=1
   assert base_stats==rec['stats'];counts['baseline_statistics_reproduced']+=1
   tests2,stats2=discover_normalized(source);assert (tests,stats)==(tests2,stats2);counts['deterministic_new_statistics']+=1
   assert stats['max_checkpoint_bits']<=(source['p']**source['r']).bit_length();counts['per_source_stored_bit_bound']+=1
   assert stats['gcd_updates']==source['dimension']*stats['accepted'];counts['gcd_update_count']+=1
   assert stats['normalization_divisions']==stats['accepted']*source['dimension']*(source['dimension']-1)//2;counts['normalization_division_count']+=1
   counts['accepted_tests']+=stats['accepted'];counts['queue_decisions']+=stats['decisions']
   idx=rec['index'];prefix=f'c{idx:03}_';text=(ROOT/f'formalization/NormalizedComputed{idx//12:02}.lean').read_text()
   def literal(name):
    line=next(l for l in text.splitlines() if l.startswith('def '+prefix+name+' :'))
    return ast.literal_eval(line.split(':=',1)[1].strip().replace('![','['))
   assert literal('A')==source['actions'] and literal('O')==source['observations'];counts['source_literal_transcription']+=1
   assert literal('result')==[(t['word'],t['observation']) for t in tests];counts['answer_literal_transcription']+=1
   assert f'abbrev {prefix}R := ZMod ({source["p"]}^{source["r"]})' in text;counts['modulus_transcription']+=1
   outcomes.append({'index':idx,'source':rec['source'],'old_checkpoint_bits':baseline_objects[-1].checkpoint_bits,'old_partial_basis_bits':base_stats['max_integer_bits'],'normalized':stats})
 finally:
  integer_echelon.IntegerEchelon=old_cls;chainring.module_form=old_mf;discover.module_form=old_df
 configs=[(1,2),(2,0),(2,2),(3,2),(4,2),(6,2),(8,1),(9,1),(12,1)]
 for m,d in configs:
  vectors=list(product(range(m),repeat=d))
  for length in range(3):
   for rows in product(vectors,repeat=length):
    B=NormalizedEchelon(m,d)
    for v in rows:B.insert(v)
    expected=enum_span(rows,m,d)
    assert enum_span(B.rows,m,d)==expected;counts['exhaustive_basis_image']+=1
    assert normalize_rows(B.rows)==B.rows;counts['normalization_idempotence']+=1
    C=NormalizedEchelon(m,d)
    for v in reversed(rows):C.insert(v)
    assert B.key()==C.key();counts['exhaustive_insertion_order']+=1
    for v in vectors:
     coeff=B.coordinates(v);assert (coeff is not None)==(v in expected);counts['exhaustive_membership']+=1
     if coeff is not None:
      assert [sum(coeff[i]*B.rows[i][j] for i in range(d)) for j in range(d)]==list(v);counts['integer_reconstruction']+=1
    counts['generating_lists']+=1
 # General integer bases: both directions have exact row-combination witnesses.
 for case in range(150):
  d=case%7;rows=[[0 if j<i else (rng.randrange(1,50) if j==i else rng.randrange(-10**6,10**6)) for j in range(d)] for i in range(d)]
  reduced=normalize_rows(rows);A=IntegerEchelon(1,d);A.rows=rows;B=IntegerEchelon(1,d);B.rows=reduced
  for old,new in [(A,B),(B,A)]:
   for row in new.rows:
    c=old.coordinates(row);assert c is not None and [sum(c[i]*old.rows[i][j] for i in range(d)) for j in range(d)]==row;counts['integer_lattice_row_certificate']+=1
  assert normalize_rows(reduced)==reduced;counts['general_idempotence']+=1
  # Integer shear by a lower row is invertible and must preserve the normal form.
  if d>=2:
   i=rng.randrange(d-1);j=rng.randrange(i+1,d);a=rng.randrange(-100,101);sheared=copy.deepcopy(rows)
   sheared[i]=[x+a*y for x,y in zip(rows[i],rows[j])]
   assert normalize_rows(sheared)==reduced;counts['unimodular_shear_canonical']+=1
 for case in range(90):
  p=[2,3,5][case%3];r=1+case%5;m=p**r;d=1+case%6
  rows=[[rng.randrange(-2*m,2*m) for _ in range(d)] for _ in range(1+case%7)]
  B=NormalizedEchelon(m,d);C=NormalizedEchelon(m,d)
  for v in rows:B.insert(v)
  altered=[[x+m*rng.randrange(-4,5) for x in v] for v in reversed(rows)]
  for v in altered:C.insert(v)
  assert B.key()==C.key();counts['representative_and_order_invariance']+=1
  form=module_form([[x%m for x in v] for v in rows],p,r)
  for _ in range(12):
   v=[rng.randrange(-2*m,2*m) for _ in range(d)]
   assert B.contains(v)==(form.coordinates([x%m for x in v]) is not None);counts['independent_smith_membership']+=1
 B=NormalizedEchelon(64,2);B.insert([2,32])
 assert B.rows==[[2,32],[0,64]] and B.contains([4,0]) and not B.contains([2,0]);counts['coupled_constraint_retained']+=1
 bad=IntegerEchelon(64,2);bad.rows=[[2,0],[0,64]]
 assert bad.contains([2,0]) and not B.contains([2,0]);counts['own_pivot_clipping_counterexample']+=1
 rejected=[]
 def reject(name,f):
  try:f()
  except (ValueError,RuntimeError):rejected.append(name)
  else:raise AssertionError(name)
 reject('nonsquare',lambda:normalize_rows([[1,2]]));reject('negative_pivot',lambda:normalize_rows([[-1]]));reject('zero_pivot',lambda:normalize_rows([[0]]));reject('lower_entry',lambda:normalize_rows([[1,0],[1,1]]));reject('float',lambda:normalize_rows([[1.0]]));reject('zero_modulus',lambda:NormalizedEchelon(0,1));reject('negative_dimension',lambda:NormalizedEchelon(4,-1));reject('bad_vector',lambda:NormalizedEchelon(4,2).insert([1]));reject('cap_unresolved',lambda:discover_normalized(json.loads((ROOT/records[0]['source']).read_text()),candidate_cap=0));counts['invalid_input_or_cap_controls']=len(rejected)
 assert before=={str(p.relative_to(ROOT)):sha(p) for p in inputs}
 peaks={'old_checkpoint_bits':max(x['old_checkpoint_bits'] for x in outcomes),'old_partial_basis_bits':max(x['old_partial_basis_bits'] for x in outcomes),'new_checkpoint_bits':max(x['normalized']['max_checkpoint_bits'] for x in outcomes),'new_pre_normalization_basis_bits':max(x['normalized']['max_pre_normalization_bits'] for x in outcomes)}
 result={'status':'PASS','started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':time.monotonic()-t,'seed':2026092107,'counts':dict(counts),'peaks':peaks,'cases':outcomes,'exhaustive_configs':configs,'exhaustive_max_generators':2,'general_integer_bases':150,'random_smith_cases':90,'rejections':rejected,'inputs':[{'path':p,'sha256':h} for p,h in sorted(before.items())],'all_inputs_unchanged':True,'non_claims':['Python code extraction is not verified','No wall-time speedup benchmark','Peak pre-normalization basis size is not maximum size of every temporary arithmetic operand','No new held-out structural discovery']}
 dump(ROOT/'results_v07/PYTHON_AUDIT.json',result)
 print(json.dumps({k:v for k,v in result.items() if k not in ['cases','inputs']},indent=2))
if __name__=='__main__':main()
