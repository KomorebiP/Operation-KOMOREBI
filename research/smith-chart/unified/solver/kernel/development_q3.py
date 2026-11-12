"""Komorebi P. Frozen 60-example q3 development graph generator.
THIS IS TRAINING/DEVELOPMENT DATA, not a holdout benchmark.
The sparse template shapes were selected after inspecting its failures.
"""
import json,random,itertools,time
from pathlib import Path
from holdout_q3 import derive,witness
from recursive_modules import synthesize
from algebraic_witness import verify_algebraic_circuit


def run(seed=14039,limit=60):
 rng=random.Random(seed)
 pairs=list(itertools.combinations(range(4),2))
 records=[];attempts=0;t=time.perf_counter()
 while len(records)<limit and attempts<3000:
  attempts+=1
  R=rng.sample(pairs,rng.choice([3,4]))
  Q=rng.sample(pairs,3)
  kind=rng.choice([['L','L','C'],['C','C','L']]);rng.shuffle(kind)
  edges=[(tp,*ab,rng.choice([1,2,3,4])) for tp,ab in zip(kind,Q)]
  edges.extend(('R',*ab,rng.choice([1,2,3,4,5])) for ab in R)
  try:
   P,Qcoeff=derive(edges)
   if max(len(P),len(Qcoeff))-1!=3:continue
   verify_algebraic_circuit(witness(edges,P,Qcoeff),{'P':P,'Q':Qcoeff},3)
   result=synthesize(P,Qcoeff)
  except (ValueError,ZeroDivisionError):continue
  records.append({'P':P,'Q':Qcoeff,'result':result['status'],'known_reactive':3,'known_edges':len(edges),'input_edges':edges})
 return {'status':'COMPLETE' if len(records)==limit else 'PARTIAL','seed':seed,
         'valid_cases':len(records),'attempted':attempts,
         'certified':sum(x['result']=='CERTIFIED_MINIMUM' for x in records),
         'elapsed_seconds':time.perf_counter()-t,
         'records':records}

if __name__=='__main__':
 d=run()
 p=Path(__file__).parents[1]/'results/independent_graph_q3.json'
 p.write_text(json.dumps({'trials':d['valid_cases'],'solved':d['certified'],'status':d['status'],'cases':d['records']},indent=2))
 print(json.dumps({k:v for k,v in d.items() if k!='records'},indent=2))
