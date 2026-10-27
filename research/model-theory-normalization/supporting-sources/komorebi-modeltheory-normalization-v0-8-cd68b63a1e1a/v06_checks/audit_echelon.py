#!/usr/bin/env python3
"""Independent bounded execution audit. Universal correctness is in the Lean files."""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from itertools import product
import ast,copy,hashlib,json,random,sys,time
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from integer_echelon import IntegerEchelon,discover_echelon,bezout
from chainring import module_form

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def enum_span(G,m,d):
    return {tuple(sum(c[i]*G[i][j] for i in range(len(G)))%m for j in range(d))
            for c in product(range(m),repeat=len(G))}

def main():
    started=datetime.now(timezone.utc).isoformat();t=time.monotonic();C=Counter()
    records=json.loads((ROOT/'v06_evidence/EXPORTED_DATA.json').read_text())
    inputs=[ROOT/'integer_echelon.py',ROOT/'discover.py',ROOT/'chainring.py',Path(__file__),
            ROOT/'v06_checks/generate.py',ROOT/'v06_checks/batch_export.py',ROOT/'v06_evidence/EXPORTED_DATA.json']
    inputs+= [ROOT/r['source'] for r in records]
    inputs+= sorted((ROOT/'formalization').glob('EchelonComputed*.lean'))
    inputs+= sorted((ROOT/'certified_data').glob('*.trace.json'))
    before={str(p.relative_to(ROOT)):sha(p) for p in set(inputs)}
    outcomes=[]
    # Actual new port, no old Smith solver invoked for discovery.
    import chainring,discover
    old_a,old_b=chainring.module_form,discover.module_form
    def forbid(*a,**kw):raise AssertionError('new discovery called Smith')
    chainring.module_form=discover.module_form=forbid
    try:
      for rec in records:
        source=json.loads((ROOT/rec['source']).read_text())
        answer,stats=discover_echelon(source)
        prior=json.loads((ROOT/'certified_data'/Path(rec['source']).name.replace('.source.json','.trace.json')).read_text())
        assert answer==prior['result']==rec['result'];C['frozen_ordered_discovery_results']+=1
        assert stats==rec['stats'];C['deterministic_statistics']+=1
        assert stats['gcd_updates']==source['dimension']*stats['accepted'];C['one_gcd_per_insertion_column']+=1
        assert stats['membership_pivots']<=source['dimension']*stats['decisions'];C['membership_division_bound']+=1
        C['accepted_tests']+=stats['accepted'];C['queue_decisions']+=stats['decisions']
        # Independently reparse actual Lean literals, not exporter routines.
        idx=rec['index'];prefix=f'c{idx:03}_';text=(ROOT/f'formalization/EchelonComputed{idx//12:02}.lean').read_text()
        def lit(name):
          line=next(l for l in text.splitlines() if l.startswith('def '+prefix+name+' :'))
          return ast.literal_eval(line.split(':=',1)[1].strip().replace('![','['))
        assert lit('A')==source['actions'] and lit('O')==source['observations'];C['literal_source_transcription']+=1
        assert lit('result')==[(v['word'],v['observation']) for v in answer];C['literal_answer_transcription']+=1
        assert f'abbrev {prefix}R := ZMod ({source["p"]}^{source["r"]})' in text;C['literal_modulus_transcription']+=1
        outcomes.append({'source':rec['source'],'stats':stats})
    finally:chainring.module_form,discover.module_form=old_a,old_b
    # Exact exhaustive reference independent of echelon and Smith.
    configurations=[(1,2),(2,0),(2,2),(3,2),(4,2),(6,2),(8,1),(9,1),(12,1)]
    for m,d in configurations:
      vs=list(product(range(m),repeat=d))
      for length in range(3):
        for G in product(vs,repeat=length):
          B=IntegerEchelon(m,d)
          for v in G:B.insert(v)
          expected=enum_span(G,m,d)
          assert enum_span(B.rows,m,d)==expected;C['exhaustive_basis_image']+=1
          for v in vs:
            c=B.coordinates(v)
            assert (c is not None)==(v in expected);C['exhaustive_membership']+=1
            if c is not None:
              assert [sum(c[i]*B.rows[i][j] for i in range(d)) for j in range(d)]==list(v)
              C['exact_integer_reconstruction']+=1
          C['exhaustive_generating_lists']+=1
    # Bézout integer signs and nonunit quotients.
    for q in range(1,65):
      for a in range(-64,65):
        g,s,u=bezout(q,a)
        assert g>0 and q%g==a%g==0 and s*q+u*a==g and s*(q//g)+u*(a//g)==1
        C['bezout_determinant_identity']+=1
    rng=random.Random(2026092106)
    for case in range(90):
      p=[2,3,5][case%3];r=1+case%5;m=p**r;d=1+case%6
      G=[[rng.randrange(-2*m,2*m) for _ in range(d)] for _ in range(1+case%7)]
      B=IntegerEchelon(m,d)
      for v in G:B.insert(v)
      form=module_form([[a%m for a in v] for v in G],p,r)
      for _ in range(12):
        v=[rng.randrange(-2*m,2*m) for _ in range(d)]
        assert B.contains(v)==(form.coordinates([a%m for a in v]) is not None)
        C['independent_smith_membership']+=1
        vv=[a+m*rng.randrange(-4,5) for a in v]
        assert B.contains(v)==B.contains(vv);C['representative_shift_invariance']+=1
    # Independent coupled arithmetic anchor; diagonalization would accept the false state.
    B=IntegerEchelon(64,2);B.insert([2,32])
    assert B.contains([4,0]) and not B.contains([0,32]);C['coupled_torsion_anchor']+=1
    rejected=[]
    def reject(label,thunk):
      try:thunk()
      except (ValueError,RuntimeError):rejected.append(label)
      else:raise AssertionError(label+' accepted')
    reject('zero_modulus',lambda:IntegerEchelon(0,2))
    reject('negative_dimension',lambda:IntegerEchelon(4,-1))
    reject('wrong_row_length',lambda:IntegerEchelon(4,2).insert([1]))
    reject('noninteger_row',lambda:IntegerEchelon(4,1).insert([0.5]))
    reject('boolean_modulus',lambda:IntegerEchelon(True,1))
    reject('nonpositive_pivot',lambda:bezout(0,1))
    source=json.loads((ROOT/'certificates/hidden_p2_r2_d4.source.json').read_text())
    reject('candidate_cap_unresolved',lambda:discover_echelon(source,candidate_cap=0))
    reject('negative_cap',lambda:discover_echelon(source,candidate_cap=-1))
    bad=copy.deepcopy(source);bad['word_order']='right_to_left'
    reject('wrong_word_interface',lambda:discover_echelon(bad))
    bad=copy.deepcopy(source);bad['initial_interface']='single_seed'
    reject('wrong_initial_interface',lambda:discover_echelon(bad))
    C['invalid_input_or_cap_controls']=len(rejected)
    assert before=={str(p.relative_to(ROOT)):sha(p) for p in set(inputs)}
    result={'status':'PASS','started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
      'runtime_seconds':time.monotonic()-t,'seed':2026092106,'counts':dict(C),
      'exhaustive_modulus_dimension_pairs':configurations,'exhaustive_max_generators':2,
      'random_cases':90,'random_queries_each':12,'rejections':rejected,'cases':outcomes,
      'inputs':[{'path':p,'sha256':h} for p,h in sorted(before.items())],
      'scope':'Python port bounded validation; actual Lean algorithm and universal proofs are separate. No comparative timing or bit-complexity claim.'}
    dump(ROOT/'results_v06/PYTHON_AUDIT.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['cases','inputs']},indent=2))
if __name__=='__main__':main()
