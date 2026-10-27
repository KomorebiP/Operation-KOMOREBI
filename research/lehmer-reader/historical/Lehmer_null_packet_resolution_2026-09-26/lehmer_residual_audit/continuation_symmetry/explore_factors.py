import sys,time,json
from pathlib import Path
import sympy as s
from math import gcd
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent/'continuation_5core'));from explore_shell import shell,polynomial
from explore import sigma_primes
T=s.symbols('T');t=time.perf_counter();rows=[]
for p in sigma_primes(2000)[1]:
 B=[0]*11
 for v in shell(p):
  for j,b in enumerate(polynomial(v)):B[j]+=b
 poly=s.Poly.from_list(B[::-1],T)
 c,fs=s.factor_list(poly)
 row={'p':p,'B':B,'content':int(c),'degrees':[f.degree() for f,e in fs for _ in range(e)],'factors':[(list(map(int,reversed(f.all_coeffs()))),int(e)) for f,e in fs]}
 rows.append(row)
 if len(row['degrees'])!=1: print(p,row['degrees'],str(fs),flush=True)
res={'rows':rows,'runtime':time.perf_counter()-t}
(P/'FACTORIZATIONS.json').write_text(json.dumps(res,indent=2))
print('DONE',len(rows),res['runtime'])
