import sys,itertools,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'computations'))
from inherited_reciprocity_checks import build, rref, kernel
qs=[97,197,293,491,587,883,1373,1471,1567,1667]
rows,ps,_,M=build(qs);M=[[x%7 for x in row] for row in M]
ks=[(p['logs']['phi']%7,p['logs']['3']%7,p['logs']['sqrt5']%7) for p in ps]
cache={}; patterns={}
for u in range(7):
 for r in range(1,7):
  z=tuple(i for i,l in enumerate(ks) if (l[0]*u+l[1]*r+l[2])%7==0)
  patterns.setdefault(z,[]).append((u,r))
bad=[]
for comb in itertools.chain.from_iterable(itertools.combinations(range(len(ps)),s) for s in range(1,6)):
 sub=[[row[i] for i in comb] for row in M]
 K=kernel(sub)
 if len(K)!=1 or not all(K[0]):continue
 matches=[(u,r) for z,uv in patterns.items() if set(comb)<=set(z) for u,r in uv]
 if matches:bad.append({'indices':comb,'q':sorted(set(ps[i]['q'] for i in comb)),'coefficients':K[0], 'alpha':matches})
minsets=[]
for b in bad:
 s=set(b['q'])
 if not any(set(c['q'])<s for c in bad) and b['q'] not in minsets:minsets.append(b['q'])
print('PLACES',[(p['label'],k) for p,k in zip(ps,ks)])
print('BAD CIRCUITS',len(bad)); print('MINIMAL BAD PRIME SETS',minsets)
good=[]
for mask in range(1<<len(qs)):
 subset=[q for i,q in enumerate(qs) if mask>>i&1]
 if not any(set(bs)<=set(subset) for bs in minsets):good.append(subset)
maxgood=[s for s in good if not any(set(s)<set(t) for t in good)]
print('MAXIMAL GOOD',maxgood)
Path(__file__).with_name('scan_result.json').write_text(json.dumps({'qs':qs,'places':ps,'matrix':M,'bad_circuits':bad,'minimal_bad_prime_sets':minsets,'maximal_good_sets':maxgood},indent=2))
