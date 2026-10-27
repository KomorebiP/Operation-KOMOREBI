#!/usr/bin/env python3
"""Exact verifier. LP proposal software is not invoked by this script.
Universal implications depend on the harmonic-theta and level-one arguments
spelled out in RESEARCH_NOTE.md, not on a bounded sample of shell identities.
"""
import sys,json,time,hashlib,platform,itertools,math,datetime
from fractions import Fraction as F
from pathlib import Path
import sympy as s
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parent/'continuation_5core'))
from explore_shell import shell,weight,polynomial
from explore import tau_triangular,product_tau
K=json.load(open(H/'KERNELS_EXTENDED.json'));K7=json.load(open(H/'KERNELS.json'))

def ev(k,v):
 pp=[sum(x**i for x in v) for i in range(2,6)]
 return sum(c*math.prod(x**a for x,a in zip(pp,ex)) for ex,c in k['terms'])
def frac(x):return F(*x)

def main():
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();tt=time.perf_counter()
 inputs=[Path(__file__),H/'KERNELS_EXTENDED.json',H/'KERNELS.json',H/'POSITIVITY_RESULTS.json',H/'EXTENDED_RESULTS.json',H/'DUAL_31.json',H/'FACTORIZATIONS.json',H/'kernel_lp.py',H/'RESEARCH_NOTE.md',H/'SOURCES.md',H.parent/'continuation_5core'/'explore_shell.py',H.parent/'explore.py']
 hashes={str(p.relative_to(H.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
 # Exact symbolic identities for every retained null polynomial.
 from kernel_lp import L, vs as variables
 harmonic_checks=initial_zero_checks=0
 for k in K:
     expression=sum(c*math.prod(x**a for x,a in zip(variables,ex)) for ex,c in k['terms'])
     assert L(expression).is_zero
     harmonic_checks+=1
     for n in range(1,(12+k['degree'])//12+1):
         assert sum(weight(v)*ev(k,v) for v in shell(n))==0
         initial_zero_checks+=1
 tau=tau_triangular(16249);assert tau[:129]==product_tau(128)
 counts={'shells_checked':0,'kernel_shell_identities':0,'packet_symmetry_checks':0,'moment16_identities':0,'moment18_identities':0,'rational_positivity_certificates':0,'exact_margin_checks':0}
 s3=[0]*16250;s5=[0]*16250
 for d in range(1,16250):
  for n in range(d,16250,d):s3[n]+=d**3;s5[n]+=d**5
 samples=[]
 for n in list(range(1,129))+[2411,16249]:
  vs=list(shell(n));ww=[weight(v) for v in vs];assert sum(ww)==tau[n];counts['shells_checked']+=1
  ks=K if n<=128 else K[:2]
  for k in ks:assert sum(w*ev(k,v) for w,v in zip(ww,vs))==0;counts['kernel_shell_identities']+=1
  Vset=set(vs)
  for v,w in zip(vs,ww):
   jv=tuple(-v[(-i)%5] for i in range(5));assert jv in Vset and weight(jv)==w;counts['packet_symmetry_checks']+=1
  assert sum(w*sum(z**3 for z in v) for w,v in zip(ww,vs))==0
  r4=sum(w*sum(z**4 for z in v) for w,v in zip(ww,vs))
  r33=sum(w*sum(z**3 for z in v)**2 for w,v in zip(ww,vs))
  a16=tau[n]+240*sum(s3[j]*tau[n-j] for j in range(1,n))
  a18=tau[n]-504*sum(s5[j]*tau[n-j] for j in range(1,n))
  assert 13*r4==470*n*n*tau[n]-28*a16;counts['moment16_identities']+=1
  assert 900*n*r4-27000*n**3*tau[n]-320*r33==3600*a18;counts['moment18_identities']+=1
  if n in [1,7,31,2411,16249]:samples.append({'n':n,'tau':tau[n],'R4':r4,'a16':a16,'R33':r33,'a18':a18})
 certs=[]
 for fn in ['POSITIVITY_RESULTS.json','EXTENDED_RESULTS.json']:
  for row in json.load(open(H/fn))['rows']:
   p=row['p'];vs=list(shell(p));ww=[weight(v) for v in vs]
   for a in row['attempts']:
    if not a.get('certified'):continue
    ks=[k for k in K if k['degree']<=a['max_degree']];cc=list(map(frac,a['coefficients']));assert len(cc)==len(ks)
    margins=[a['sign']*(1 if w>0 else -1)*(1+sum(c*ev(k,v) for c,k in zip(cc,ks))) for v,w in zip(vs,ww)]
    assert min(margins)>0 and min(margins)==frac(a['margin']);counts['exact_margin_checks']+=len(margins)
    assert a['sign']*tau[p]>0
    counts['rational_positivity_certificates']+=1;certs.append({'p':p,'max_degree':a['max_degree'],'sign':a['sign'],'margin':a['margin']})
 dual=json.load(open(H/'DUAL_31.json'));points=list(map(tuple,dual['points']));y=list(map(frac,dual['weights']));sg=dual['signs'];assert all(q>0 for q in y) and sum(y)==1
 allsignatures={(tuple(ev(k,v) for k in K7),1 if weight(v)>0 else -1) for v in shell(31)}
 assert {(tuple(ev(k,v) for k in K7),sign) for v,sign in zip(points,sg)}==allsignatures
 assert sum(c*sign for c,sign in zip(y,sg))==0
 for k in K7:assert sum(c*sign*ev(k,v) for c,sign,v in zip(y,sg,points))==0
 counts['dual_positive_weights']=len(y);counts['dual_zero_relations']=len(K7)+1
 counts['symbolic_harmonic_identities']=harmonic_checks;counts['initial_zero_coefficients']=initial_zero_checks
 # Explicit p7 elimination, independent of LP output.
 aa=F(383,1411344000000);bb=F(139,61158240000000);terms=[]
 for v in shell(7):
  w=weight(v);f=1+aa*ev(K[0],v)+bb*ev(K[1],v);terms.append({'v':v,'W':w,'factor':[f.numerator,f.denominator]});assert w*f<=0
 assert sum(weight(tuple(a['v']))*frac(a['factor']) for a in terms)==tau[7]
 assert len([a for a in terms if frac(a['factor'])!=0])==2
 # All discriminant cosets represented by a_i+t/5, sum a_i=-t.
 total=regular=0
 for t in range(5):
  for first in itertools.product(range(5),repeat=4):
   aa4=(-t-sum(first))%5;res=(*first,aa4);ints=(*first,-t-sum(first));total+=1
   if len(set(res))==5:
    regular+=1;assert t==0 and sum(z*z for z in ints)%10==0
 assert total==3125 and regular==120
 # Exact counterexample to an aggregate root bound inherited from packets.
 rr=next(a for a in json.load(open(H/'FACTORIZATIONS.json'))['rows'] if a['p']==31);B=rr['B']
 val=lambda z:sum(b*z**j for j,b in enumerate(B))
 assert val(10)<0<val(11)
 # Recheck stored irreducibility reports by exact SymPy factorization.
 T=s.symbols('T');irreducible=0
 for e in json.load(open(H/'FACTORIZATIONS.json'))['rows']:
  po=s.Poly.from_list(e['B'][::-1],T);c,fs=s.factor_list(po)
  ds=[f.degree() for f,m in fs for _ in range(m)];assert ds==e['degrees']
  if e['p']>=7:assert len(ds)==1;irreducible+=1
 after={str(p.relative_to(H.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};assert hashes==after
 out={'status':'PASS','counts':counts,'certificates':certs,'p7_elimination':terms,'sample_moments':samples,'p31_root_bound_counterexample':{'P10':val(10),'P11':val(11)},'discriminant_cosets':total,'regular_cosets':regular,'irreducible_prime_polynomials_p_ge7_through2000':irreducible,'runtime_seconds':time.perf_counter()-tt,'nonclaims':['Not a proof of Lehmer for all primes.','LP proposal failures are not impossibility proofs unless an exact dual is supplied.','The p31 exact obstruction concerns the seven stored corrections through invariant degree16, not all conceivable methods.','Finite irreducibility observations are not a universal irreducibility theorem.','Harmonic theta modularity and level-one valence are external mathematical dependencies, not certified by sampling.','No Lean or novelty/priority verification.']}
 (H/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
 manifest={'status':'completed','started_utc':start,'command':'python continuation_symmetry/verify_all.py','software':{'python':sys.version,'sympy':s.__version__},'platform':platform.platform(),'runtime_seconds':out['runtime_seconds'],'domains':'exact integers/rationals; exact symbolic factorization. LP was only a proposal generator in separate scripts.','inputs_sha256_before':hashes,'inputs_sha256_after':after,'outputs_sha256':{'VERIFICATION.json':hashlib.sha256((H/'VERIFICATION.json').read_bytes()).hexdigest()},'nonclaims':out['nonclaims'],'manifest_schema_validation':'not run; this is a plain audit record, not a validated Mathbox manifest'}
 (H/'AUDIT_RECORD.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'counts':counts,'certificates':[{k:a[k] for k in ['p','max_degree','sign']} for a in certs],'runtime':out['runtime_seconds'],'p31root':out['p31_root_bound_counterexample']},indent=2))
if __name__=='__main__':main()
