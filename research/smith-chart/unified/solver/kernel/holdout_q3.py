"""Komorebi P. Distinct-seed four-node degree-three holdout, not training data."""
import random,itertools,time,json
from pathlib import Path
from fractions import Fraction as F
import sympy as S
from recursive_modules import synthesize
from algebraic_witness import verify_algebraic_circuit
s=S.Symbol('s')

def derive(edges):
 M=S.zeros(3)
 for t,a,b,v in edges:
  y=S.Rational(1,v) if t=='R' else S.Rational(1,v)/s if t=='L' else S.Rational(v)*s
  if a:M[a-1,a-1]+=y
  if b:M[b-1,b-1]+=y
  if a and b:M[a-1,b-1]-=y;M[b-1,a-1]-=y
 z=S.cancel(M.minor_submatrix(0,0).det()/M.det())
 p,q=map(lambda a:S.Poly(a,s),S.fraction(z))
 return list(map(str,reversed(p.all_coeffs()))),list(map(str,reversed(q.all_coeffs())))

def witness(edges,P,Q):
 return {'format':'komorebi-algebraic-circuit-v1','target':{'P':P,'Q':Q},
 'storage_budget':3,'field':{'polynomial':['0','1'],'interval':['-1','1']},
 'branches':[{'type':{'R':'g','L':'h','C':'c'}[t],'nodes':[a,b],
 'coefficient':[str(F(v) if t=='C' else F(1,v))]} for t,a,b,v in edges]}

def run(seed=2026111207,limit=50):
 rng=random.Random(seed);pairs=list(itertools.combinations(range(4),2))
 out=[];attempts=0;t=time.perf_counter()
 while len(out)<limit and attempts<3000:
  attempts+=1
  react=rng.sample(pairs,3);res=rng.sample(pairs,rng.choice((3,4,5)))
  ts=rng.choice((['L','L','C'],['L','C','C']));rng.shuffle(ts)
  ed=[(tp,*ab,rng.randint(1,7)) for tp,ab in zip(ts,react)]
  ed.extend(('R',*ab,rng.randint(1,7)) for ab in res)
  try:
   P,Q=derive(ed)
   if max(len(P),len(Q))-1!=3:continue
   c=witness(ed,P,Q);verify_algebraic_circuit(c,{'P':P,'Q':Q},3)
   r=synthesize(P,Q,max_degree=3)
  except (ValueError,ZeroDivisionError):continue
  out.append({'P':P,'Q':Q,'result':r['status'],'known_exact_witness':c,
   'route':r.get('core_route',r.get('route','UNKNOWN'))})
  if len(out)%10==0:print('HOLDOUT',len(out),sum(x['result']=='CERTIFIED_MINIMUM' for x in out),'elapsed',round(time.perf_counter()-t,2),flush=True)
 result={'status':'COMPLETE' if len(out)==limit else 'PARTIAL','seed':seed,
  'valid_cases':len(out),'attempted_graphs':attempts,
  'certified':sum(x['result']=='CERTIFIED_MINIMUM' for x in out),
  'unknown':sum(x['result']!='CERTIFIED_MINIMUM' for x in out),
  'elapsed_seconds':time.perf_counter()-t,
  'sampling_scope':'four nodes, 3 mixed reactives, 3-5 resistors, physical values 1..7',
  'cases':out}
 (Path(__file__).parents[1]/'results/holdout_q3.json').write_text(json.dumps(result,indent=2))
 return result
if __name__=='__main__':
 d=run();print(json.dumps({k:v for k,v in d.items() if k!='cases'},indent=2))
