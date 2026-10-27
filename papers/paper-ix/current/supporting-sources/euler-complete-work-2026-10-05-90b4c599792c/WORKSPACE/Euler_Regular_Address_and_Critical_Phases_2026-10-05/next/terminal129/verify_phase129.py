#!/usr/bin/env python3
from pathlib import Path
from math import comb
from fractions import Fraction
import sys,json,time,hashlib,platform
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'critical_phases/vendor'))
import dyadic_modular as d

def af(a,s,h,M):
 k=(h&-h).bit_length()-1;deg=min(len(a)-1,(M.bit_length()-2)//k)
 return d.trim([sum(a[n]*comb(n,i)*pow(s,n-i,M) for n in range(i,len(a)))*pow(h,i,M)%M for i in range(deg+1)])
started=time.time();rec=json.loads((ROOT/'phase_129.json').read_text());P=rec['P'];r=(1<<515)-129;M=1<<P
assert rec['source_sha256']==hashlib.sha256((ROOT/'build_phase129.py').read_bytes()).hexdigest()
assert P<=516-(2*(129+2*P)).bit_length()
assert 3*(rec['computed_packet_max']+1)+1-r.bit_count()-rec['mu']>=P
assert [d.gamma_mod(r,q,rec['mu'],P) for q in range(rec['computed_packet_max']+1)]==rec['gamma']
assert d.trim(d.source_polynomial(P))==d.trim(rec['source'])
assert rec['lower_V_mod256']==[8,219,236,192,64]
assert [x for x in range(256) if d.evaluate(rec['lower_V_mod256'],x,256)==0]==[104]
local=[af(p,104,128,M) for p in(rec['low'],rec['high'])]
assert all(z%(1<<130)==0 for p in local for z in p)
A,C=([z>>130 for z in p] for p in local)
assert d.trim(A)==d.trim(rec['A']) and d.trim(C)==d.trim(rec['C'])
N=94;mm=1<<N
W=d.add(d.mul(A,[i*C[i] for i in range(1,len(C))],mm),[-z for z in d.mul(C,[i*A[i] for i in range(1,len(A))],mm)],mm)
assert W==rec['W'];atlas=rec['atlas']
assert sum((Fraction(1,1<<a['k']) for a in atlas),Fraction())==1
roots=[]
for i,a in enumerate(atlas):
 assert a['kind'] in('constant','simple_root')
 for b in atlas[:i]:assert (a['s']-b['s'])%(1<<min(a['k'],b['k']))
 content=a.get('value',a.get('content'));poly=af(W,a['s'],1<<a['k'],1<<(content+1))
 assert all(z%(1<<content)==0 for z in poly)
 assert d.trim([z>>content for z in poly])==a['reduction']
 if a['kind']=='simple_root':
  assert (a['s'],a['k'],content) in((2,3,6),(6,3,6))
  f=af(W,a['s'],8,mm);assert all(z%64==0 for z in f);f=[z//64 for z in f]
  z=0
  for bits in range(1,N-6+1):
   m=1<<bits;cs=[q for q in(z,z+(1<<(bits-1))) if d.evaluate(f,q,m)==0]
   assert len(cs)==1;z=cs[0]
  y=a['s']+8*z;assert y==a['root_mod'] and a['root_bits']==91
  for poly in(A,C):assert af(poly,a['s'],8,4)==[2]
  m=1<<91;av=d.evaluate(A,y,m);cv=d.evaluate(C,y,m);assert av%4==cv%4==2
  B=-(cv//2)*pow(av//2,-1,m//2)%(m//2)
  roots.append({'Y':y,'Y_bits':91,'B':B,'B_bits':90})
assert len(roots)==2
assert [z['Y'] for z in roots]==[z['Y'] for z in rec['candidates']]
assert [z['B'] for z in roots]==[z['B'] for z in rec['candidates']]
assert all(z['B']>(1<<89) for z in roots)
result={'status':'passed','coefficient_domain':'exact Z/2^P Z, integer/Fraction arithmetic','independent_gamma_coefficients':len(rec['gamma']),'independent_source_coefficients':len(rec['source']),'atlas_mass':'1','pairwise_disjoint_cover':True,'direct_binomial_leaves':len(atlas),'nonunit_division_valuation_loss':1,'roots':roots,'python':platform.python_version(),'seconds':time.time()-started,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'data_sha256':hashlib.sha256((ROOT/'phase_129.json').read_bytes()).hexdigest(),'nonclaims':['The inherited finite-template theorem remains a mathematical dependency','No exact singular member constructed','No universal Euler simplicity','No Lean compilation']}
(ROOT/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
