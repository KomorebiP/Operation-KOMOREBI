"""Exact pointwise-degree checks. Finite evidence, not a proof of P vs NP."""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import json,random,struct,sys
from explore_profiles import profile,monomials,affine_masks
R=Path(__file__).resolve().parents[1]
P=R/'predecessor/komorebi_pnp_cut_comparison/checks'
sys.path.insert(0,str(P))
from verify_cut_comparison import degree,variables,one,trace,validate,monomial_oracle

def load(n):
 data=(R/f'results/profiles{n}.bin').read_bytes()
 nn,pts,num=struct.unpack('<III',data[:12]);assert (nn,pts,num)==(n,1<<n,1<<(1<<n))
 assert len(data)==12+5*num+pts*num
 rows=[tuple(data[12+5*i:17+5*i]) for i in range(num)]
 local=[data[12+5*num+v*num:12+5*num+(v+1)*num] for v in range(pts)]
 return rows,local

def affine_ops(f,n,y):
 c=f;ops=[]
 if c&1:ops.append(('N',y));c^=one(n)
 for i,v in enumerate(variables(n)):
  if c>>(1<<i)&1:ops.append(('C',i,y));c^=v
 assert c==0
 return ops

def optimal_small(f,n):
 d=degree(f,n);vs=variables(n);mask=one(n)
 if d<=1:
  y=n;return affine_ops(f,n,y),n+1,y,0
 if d==2:
  linears=[0]
  for v in vs:linears += [t^v for t in linears[:]]
  for s in range(1,1<<n):
   for t in range(s+1,1<<n):
    residual=f^(linears[s]&linears[t])
    if degree(residual,n)<=1:
     a,b,y=n,n+1,n+2
     p=[('C',i,a) for i in range(n) if s>>i&1]+[('C',i,b) for i in range(n) if t>>i&1]
     return p+[('T',a,b,y)]+p[::-1]+affine_ops(residual,n,y),n+3,y,1
  raise AssertionError('quadratic rank-two factorization')
 assert n==3 and d==3
 for shift in range(8):
  g=mask
  for i in range(3):g &= vs[i]^(mask if shift>>i&1 else 0)
  residual=f^g
  if degree(residual,n)<=1:
   p=[('N',i) for i in range(3) if shift>>i&1]
   core,w,y=monomial_oracle(3)
   return p+core+p[::-1]+affine_ops(residual,3,y),w,y,3
 raise AssertionError('cubic translation')

def main():
 report={'status':'PASS','arithmetic':'exact Boolean/F2','seed':20260921}
 total=brute=circ_inputs=cuts=0;distribution=Counter();raw_strict=orbit_strict=0
 for n in range(1,4):
  rows,local=load(n);pts=1<<n
  for f,row in enumerate(rows):
   ds,a,b,ao,bo=row
   assert ds==max(degree(f,n),0)
   bv=[255]*pts;sub=f
   while sub:
    dh=degree(sub,n)
    for v in range(pts):
     if sub>>v&1:bv[v]=min(bv[v],dh)
    sub=(sub-1)&f;brute+=1
   assert all(bv[v]==local[v][f] for v in range(pts))
   aa,bb=profile(f,n);assert (aa,bb)==(a,b)
   assert ao==max(rows[f^l][1] for l in affine_masks(n))
   assert bo==max(rows[f^l][2] for l in affine_masks(n))
   ops,w,y,T=optimal_small(f,n);validate(ops,w)
   assert T==sum(g[0]=='T' for g in ops)==max(0,ds-1,2*bo-3)
   distribution[T]+=1
   z=variables(n)+[0]*(w-n);mask=one(n)
   A=trace(ops,z,mask);B=trace(ops[::-1],z,mask)
   expected=z.copy();expected[y]=f;assert A[-1]==expected
   z1=z.copy();z1[y]=mask;expected[y]^=mask;assert trace(ops,z1,mask)[-1]==expected
   tally=[0]
   for gate in ops:tally.append(tally[-1]+(gate[0]=='T'))
   for j in range(len(ops)+1):
    hs=[u^v for u,v in zip(A[j],B[len(ops)-j])];support=0
    for h in hs:assert not(h&(~f&mask));support|=h
    assert support==f
    cap=max(tally[j],T-tally[j])+1
    assert b<=cap
    assert all(degree(h,n)<=cap for h in hs)
    cuts+=1
   # Separate scalar replay, independent of bit-sliced trace.
   for x in range(pts):
    for y0 in (0,1):
     state=[x>>i&1 for i in range(n)]+[0]*(w-n);state[y]=y0;expect=state[:];expect[y]^=f>>x&1
     for g in ops:
      if g[0]=='N':state[g[1]]^=1
      elif g[0]=='C':state[g[2]]^=state[g[1]]
      else:state[g[3]]^=state[g[1]]&state[g[2]]
     assert state==expect;circ_inputs+=1
   total+=1
 report['small_exhaustive']={'functions':total,'supported_functions_independently_enumerated':brute,'optimal_oracle_total_by_Toffoli_count':dict(distribution),'full_scalar_inputs_including_target':circ_inputs,'cuts':cuts}
 rows,local=load(4)
 raw_strict=sum(r[2]>r[1] for r in rows);orbit_strict=sum(r[4]>r[3] for r in rows)
 rng=random.Random(20260921)
 chosen=sorted(set([0,65535,*range(256),*(rng.randrange(65536) for _ in range(512))]))
 mono=0
 for f in chosen:
  a,b=profile(f,4);assert (a,b)==rows[f][1:3]
 for f,row in enumerate(rows):
  if all(not(f>>x&1) or all(f>>(x|1<<i)&1 for i in range(4)) for x in range(16)):
   mins=[x for x in range(16) if f>>x&1 and all(not(f>>(x^(1<<i))&1) for i in range(4) if x>>i&1)]
   assert row[1]==min((x.bit_count() for x in mins),default=0)
   assert row[2]==max((x.bit_count() for x in mins),default=0)
   mono+=1
 report['four_inputs']={'all_truth_tables':65536,'subset_minimum_algorithm':'degree of every nonzero support computed, then exact subset-min transforms per point','independent_evaluation_span_checks':len(chosen),'all_monotone_functions':mono,'raw_beta_exceeds_alpha':raw_strict,'affine_orbit_beta_exceeds_affine_orbit_alpha':orbit_strict}
 families=[]
 for n in range(4,10):
  pts=1<<n;f=sum((bool(x&1 and x&2) or (x>>2)==(1<<(n-2))-1)<<x for x in range(pts))
  x1=sum((x&1)<<x for x in range(pts));g=f^x1
  mons=monomials(n);features=[sum((x&s==s)<<j for j,s in enumerate(mons)) for x in range(pts)]
  assert profile(f,n,features)==(2,n-2)
  assert profile(g,n,features)==(3,n-1)
  # Exhaust all affine output masks through 8 inputs. Ninth input: specific shift only.
  ao=bo=None
  if n<=8:
   p=[profile(f^l,n,features) for l in affine_masks(n)]
   ao=max(a for a,b in p);bo=max(b for a,b in p);assert (ao,bo)==(3,n-1)
  # Explicit negative moment certificate on x_2=1, all but the sole positive.
  v=((1<<n)-1)^1;face=[x for x in range(pts) if x&2]
  negatives=[x for x in face if x!=v];assert all(not(g>>x&1) for x in negatives)
  for s in mons:
   if s.bit_count()>n-2:break
   parity=0
   for u in negatives:parity^=int(u&s==s)
   assert parity==int(v&s==s)
  families.append({'n':n,'f_alpha':2,'f_beta':n-2,'shift_alpha':3,'shift_beta':n-1,'all_affine_masks_checked':(1<<(n+1)) if n<=8 else 0,'affine_orbit_alpha':ao,'affine_orbit_beta':bo,'old_affine_optimized_bound':n-1,'complete_bound':2*n-5,'negative_moment_certificate_points':len(negatives)})
 report['unbalanced_OR_family']=families
 (R/'results/completeness.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
