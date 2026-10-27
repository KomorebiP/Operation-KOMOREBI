#!/usr/bin/env python3
"""Exact bounded audit of the untrusted producer, independent checker, and
literal source export. Universality of the Lean checker is a separate theorem.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from itertools import product
import ast,copy,hashlib,json,sys,time,subprocess
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from certified_backend import certified_discover,BoundedSpanProposer
from new_checks.check_trace import check_trace,canonical
from v05_checks.export_checked_data import export


def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 start=time.monotonic();started_at=datetime.now(timezone.utc).isoformat();counts=Counter();records=json.loads((ROOT/'v05_evidence/EXPORTED_DATA.json').read_text())
 inputs=[ROOT/'certified_backend.py',ROOT/'chainring.py',ROOT/'discover.py',
         ROOT/'new_checks/check_trace.py',Path(__file__),ROOT/'v05_checks/export_checked_data.py',
         ROOT/'v05_checks/generate_all.py']
 inputs+=list((ROOT/'certificates').glob('*.source.json'))
 inputs+=[ROOT/x['source'] for x in records]+[ROOT/x['trace'] for x in records]
 inputs+=sorted(set(ROOT/'formalization'/(x['module']+'.lean') for x in records))
 before={str(p.relative_to(ROOT)):digest(p) for p in set(inputs)}
 for rec in records:
  s=json.loads((ROOT/rec['source']).read_text());t,stats=certified_discover(s)
  stored=json.loads((ROOT/rec['trace']).read_text())
  assert t==stored and stats==rec['stats'];counts['deterministic_trace_regeneration']+=1
  checked=check_trace(s,t);assert checked==rec['checked'];counts['independent_complete_trace']+=1
  assert stats['max_smith_rows']<=s['dimension']+1;counts['bounded_smith_width']+=1
  counts['accepted_membership_witnesses']+=checked['accepted'];counts['skipped_membership_witnesses']+=checked['skipped']
  if rec['index']<202:
   name=Path(rec['source']).name.replace('.source.json','.trace.json')
   old=json.loads((ROOT/'queue_traces'/name).read_text())
   assert t['result']==old['result'];counts['parent_literal_result_preserved']+=1
  # Reparse numerical literals independently from the exporter helper.
  text=(ROOT/'formalization'/(rec['module']+'.lean')).read_text();pre=rec['prefix']
  def literal(name):
   line=next(l for l in text.splitlines() if l.startswith('def '+pre+name+' :'))
   raw=line.split(':=',1)[1].strip().replace('![','[').replace('Fin.elim0','[]')
   return ast.literal_eval(raw)
  assert literal('A')==s['actions'] and literal('O')==s['observations'];counts['literal_source_matrix_agreement']+=1
  assert f'abbrev {pre}R := ZMod {s["p"]**s["r"]}' in text;counts['literal_modulus_agreement']+=1
  out=literal('result');assert out==[(x['word'],x['observation']) for x in t['result']]
  counts['literal_output_agreement']+=1
  a=text.index(f'def {pre}evidence ');b=text.index(f'def {pre}result ',a)
  body=text[a:b].split(':= [',1)[1].strip();assert body.endswith(']');body=body[:-1]
  parsed=[]
  for line in body.splitlines():
   line=line.strip().rstrip(',')
   if not line:continue
   if line.startswith('.combination '):parsed.append(('skip',ast.literal_eval(line[len('.combination '):])))
   elif line.startswith('.separation ('):
    raw=line[len('.separation ('):-1].replace('![','[').replace('Fin.elim0','[]')
    parsed.append(('accept',ast.literal_eval(raw)))
   else:raise AssertionError('unparsed evidence')
  assert parsed==[(e['decision'],e.get('coefficients',e.get('delta'))) for e in t['events']]
  counts['literal_evidence_agreement']+=1

 # Exhaust all generating lists of length <=2 and all candidate rows in small rings.
 for p,r,d in [(2,1,2),(3,1,2),(2,2,2),(2,3,1),(3,2,1)]:
  m=p**r;vecs=list(product(range(m),repeat=d))
  for size in range(3):
   for G in product(vecs,repeat=size):
    backend=BoundedSpanProposer(p,r,d);raw=[]
    for g in G:
     row=list(g)
     if backend.membership(row) is None:raw.append(row);backend.insert(row)
    span={tuple(sum(c[i]*G[i][j] for i in range(size))%m for j in range(d))
          for c in product(range(m),repeat=size)}
    for v in vecs:
     c=backend.membership(list(v));assert (c is not None)==(v in span)
     counts['exhaustive_membership_decisions']+=1
     if c is not None:
      assert tuple(sum(c[i]*raw[i][j] for i in range(len(raw)))%m for j in range(d))==v
      counts['exhaustive_positive_witnesses']+=1
     else:
      delta=backend.separator(list(v));dot=lambda row:sum(x*y for x,y in zip(row,delta))%m
      assert all(dot(row)==0 for row in raw) and dot(v)!=0
      counts['exhaustive_negative_witnesses']+=1
    for b,c in zip(backend.basis,backend.provenance):
     assert b==[sum(c[i]*raw[i][j] for i in range(len(raw)))%m for j in range(d)]
     counts['exhaustive_basis_provenance']+=1
    counts['exhaustive_generator_lists']+=1

 source=json.loads((ROOT/'certified_data/descending_torsion.source.json').read_text())
 trace=json.loads((ROOT/'certified_data/descending_torsion.trace.json').read_text())
 mutations=[]
 def bad(label,edit,edit_source=None):
  s=copy.deepcopy(source);t=copy.deepcopy(trace)
  if edit_source:edit_source(s)
  edit(t,s);mutations.append((label,s,t))
 bad('missing_first',lambda t,s:t['events'].pop(0))
 bad('missing_last',lambda t,s:t['events'].pop())
 bad('trailing',lambda t,s:t['events'].append(copy.deepcopy(t['events'][-1])))
 bad('zero_separator',lambda t,s:t['events'][0].__setitem__('delta',[0]))
 bad('wrong_coefficients',lambda t,s:t['events'][24]['coefficients'].__setitem__(0,(t['events'][24]['coefficients'][0]+1)%(2**24)))
 bad('short_coefficients',lambda t,s:t['events'][24]['coefficients'].pop())
 bad('long_coefficients',lambda t,s:t['events'][24]['coefficients'].append(0))
 bad('wrong_result',lambda t,s:t.__setitem__('result',[]))
 bad('wrong_word',lambda t,s:t['events'][0]['test'].__setitem__('word',[0]))
 bad('extra_field',lambda t,s:t['events'][0].__setitem__('claimed_truth',True))
 bad('stale_source',lambda t,s:None,lambda s:s['actions'][0][0].__setitem__(0,2))
 bad('rebound_wrong_source',lambda t,s:t.__setitem__('source_sha256',hashlib.sha256(canonical(s)).hexdigest()),lambda s:s['actions'][0][0].__setitem__(0,2))
 rejected=[]
 for name,s,t in mutations:
  try:check_trace(s,t)
  except (ValueError,TypeError,KeyError,AssertionError):rejected.append(name);counts['corrupt_trace_rejected']+=1
  else:raise AssertionError('accepted corruption '+name)
 try:certified_discover(source,candidate_cap=1)
 except RuntimeError as e:assert 'unresolved' in str(e);counts['cap_is_unresolved']+=1
 else:raise AssertionError('cap wrongly succeeded')
 checker=ast.parse((ROOT/'new_checks/check_trace.py').read_text())
 imports=[n.module for n in ast.walk(checker) if isinstance(n,ast.ImportFrom)]
 assert not any(x in imports for x in ['chainring','certified_backend','discover']);counts['independent_checker_imports']+=1
 for rel,h in before.items():assert digest(ROOT/rel)==h
 counts['input_hashes_unchanged']+=1
 result={'status':'PASS','started_at':started_at,'finished_at':datetime.now(timezone.utc).isoformat(),'counts':dict(counts),'seconds':time.monotonic()-start,
 'cases':len(records),'stress':records[-1]['stats'],'rejected_mutations':rejected,
 'ranges':{'frozen_profiles':202,'new_stress':'p=2, r=24, dimension=1, 24 descending-valuation observations, identity action',
 'exhaustive_membership':{'rings_and_dimensions':[[2,1,2],[3,1,2],[2,2,2],[2,3,1],[3,2,1]],'generator_list_lengths':[0,1,2],'all_candidate_vectors':True}},
 'input_hashes':before,
 'nonclaims':['Python producer, parser and exporter are not verified executables.','No comparative runtime advantage or structural holdout claimed.','Membership checking is proved; the fast Smith algorithm is still unverified.']}
 dump(ROOT/'results_v05/BACKEND_AUDIT.json',result)
 print(json.dumps({k:v for k,v in result.items() if k!='input_hashes'},indent=2))
if __name__=='__main__':main()
