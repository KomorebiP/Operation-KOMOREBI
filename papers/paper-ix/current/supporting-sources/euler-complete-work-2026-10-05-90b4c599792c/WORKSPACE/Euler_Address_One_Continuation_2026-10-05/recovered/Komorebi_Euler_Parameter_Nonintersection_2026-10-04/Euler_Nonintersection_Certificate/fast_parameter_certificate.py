#!/usr/bin/env python3
"""Whole-parameter finite certificate; local-first independent assembly."""
from __future__ import annotations
import argparse, hashlib, json, platform, time
from functools import lru_cache
from fractions import Fraction
from pathlib import Path
import build_parameter_certificate as slow
base=slow.base

@lru_cache(None)
def fast_twoB(n:int,P:int)->int:
 # Keep odd binomial units and their valuations separately. No giant exact
 # n-choose-k is constructed. All unit inverses are modulo 2^P.
 M=1<<P;limit=min(n,P);unit=1;valuation=0;total=0
 for k in range(limit+1):
  if k:
   numerator=n-k+1;vn=slow.val(numerator,P+10000);vd=slow.val(k,P+10000)
   unit=unit*((numerator>>vn)%M)*pow(k>>vd,-1,M)%M
   valuation+=vn-vd
   assert valuation>=0
  if base.B[k]:
   weight=base.fmod((1<<k)*base.B[k],P)
   bc=(unit<<valuation)%M if valuation<P else 0
   total=(total+bc*weight)%M
 return total*pow((1-pow(2,n-1,M))%M,-1,M)%M


def linmul(a,c,s,D,M):
 out=[0]*min(len(a)+1,D+1)
 for i in range(len(out)):
  out[i]=(c*(a[i] if i<len(a) else 0)+(s*a[i-1] if i else 0))%M
 return out

def local_horner(a,c,k,prec,D):
 M=1<<prec;s=1<<k;out=[0]*(D+1)
 for aj in reversed(a[:prec]):
  for i in range(D,0,-1):out[i]=(c*out[i]+s*out[i-1])%M
  out[0]=(c*out[0]+aj)%M
 return out

def conv(a,b,D,M):
 out=[0]*(min(D,len(a)+len(b)-2)+1)
 for i,x in enumerate(a):
  if x:
   for j in range(min(len(b),len(out)-i)):
    if b[j]:out[i+j]=(out[i+j]+x*b[j])%M
 return out

def local_split(P,c,k,gam,src):
 M=1<<P;D=(P-1)//k
 lo=[0]*(D+1);hi=[0]*(D+1);pq=[1]
 for q,g in enumerate(gam):
  if q:
   i=q-1;pq=linmul(pq,c-i,1<<k,D,M);pq=linmul(pq,2*c-2*i-1,1<<(k+1),D,M)
  if not g or not any(pq):continue
  vg=slow.val(g,P);vp=min(slow.val(a,P) for a in pq);Pe=P-vg-vp
  if Pe<=0:continue
  # The source has [X^n]A in 2^n Z2. All omitted source coefficients
  # and all local degrees >floor((Pe-1)/k) vanish modulo 2^Pe.
  smallM=1<<Pe;ds=min(D,(Pe-1)//k)
  source_local=local_horner(src,c-q,k,Pe,ds)
  normpq=[(a>>vp)%smallM for a in pq]
  term=conv(normpq,source_local,D,smallM);gu=g>>vg
  target=lo if q<161 else hi
  for n,a in enumerate(term):target[n]=(target[n]+((gu*a)<<(vg+vp)))%M
 return lo,hi

def make_affine(lo,hi,content,P):
 M=1<<P;h0=[(17659*l+u)%M for l,u in zip(lo,hi)];h1=[((1<<18)*l)%M for l in lo]
 assert all(z%(1<<content)==0 for z in h0+h1)
 return [z>>content for z in h0],[z>>content for z in h1]

def lower_V(gam):
 M=128;src=list(base.source(7));pq=[1];out=[0]*(2*160+len(src))
 for q in range(161):
  if q:
   i=q-1;pq=base.mul(pq,[-i,1],M);pq=base.mul(pq,[-2*i-1,2],M)
  assert gam[q]%(1<<153)==0
  g=(gam[q]>>153)%M
  if g:
   term=base.mul(pq,base.shift(src,-q,M),M)
   for n,a in enumerate(term):out[n]=(out[n]+g*a)%M
 assert out[1]%2==1 and all(a%2==0 for n,a in enumerate(out) if n!=1)
 assert [x for x in range(128) if base.ev(out,x,128)==0]==[90]
 return out

def run(P,path):
 started=time.time();base.B=base.bernoullis(max(256,P))
 base.twoB=fast_twoB
 r=(1<<640)-161;mu=-154;Q=(P+r.bit_count()+mu-2)//3;M=1<<P
 budget=641-(2*(161+2*P)).bit_length();assert P<=budget
 gam=base.gamma(r,mu,P,Q);src=list(base.source(P))
 assert all(slow.val(a,P)>=n for n,a in enumerate(src))
 lo,hi=local_split(P,10202,15,gam,src);H0,H1=make_affine(lo,hi,178,P)
 N=P-179;(tau,zeta),Q0,Q1,trace=slow.lift_joint(H0,H1,N)
 clo,chi=local_split(P,90,7,gam,src);A0,A1=make_affine(clo,chi,162,P)
 assert all(x%512==0 for x in base.deriv(A1))
 roots=sorted({x%256 for x in range(512) if base.ev(base.deriv(A0),x,512)==0})
 assert roots==[79,221]
 assert slow.val(base.ev(A0,221,1<<16),16)==2 and all(x%8==0 for x in A1)
 V=lower_V(gam)
 # Independently eliminate T modulo the finite modulus using H1 as a unit,
 # and solve Q0-H0*Q1/H1 by binary lifting in Z. This is NOT the joint test.
 def tm(z,m):return (-base.ev(H0,z,m)*pow(base.ev(H1,z,m),-1,m))%m
 def em(z,m):return (base.ev(Q0,z,m)+tm(z,m)*base.ev(Q1,z,m))%m
 zs=[z for z in (0,1) if em(z,2)==0];assert len(zs)==1
 for k in range(1,N):
  nxt=1<<(k+1);xs=[z for z in (zs[0],zs[0]+(1<<k)) if em(z,nxt)==0]
  assert len(xs)==1;zs=xs
 assert (tm(zs[0],1<<N),zs[0])==(tau,zeta)
 result={'status':'finite certificate passed','global_precision':P,'finite_template_precision_budget':budget,'computed_packet_max':Q,
 'parity_packet_cutoff':2*P,'deep_content':178,'joint_precision':N,'candidate_T_residue':str(tau),'candidate_Z_residue':str(zeta),
 'candidate_T_bitlength':tau.bit_length(),'excluded_initial_parameter_interval':[0,str(tau)],
 'H0':list(map(str,H0)),'H1':list(map(str,H1)),'Q0':list(map(str,Q0)),'Q1':list(map(str,Q1)),
 'cubic_H0':list(map(str,A0)),'cubic_H1':list(map(str,A1)),'lower_V_mod128':list(map(str,V)),
 'lower_root_mod128':[90],'cubic_critical_residues_mod256':roots,'other_branch_value_valuation':2,
 'joint_lift_trace':trace,'independent_rational_elimination_lift':'passed',
 'source_sha256':hashlib.sha256(slow.BASE.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'python':platform.python_version(),'seconds':time.time()-started,
 'scope':'all T with true terminal label 161 subject to finite-precision template; exact integer nonintersection outside one parameter residue class',
 'nonclaims':['No Lean compilation','No exact singularity inferred from a modular candidate','No analytic interpolation of actual undepleted parameter family']}
 path=Path(path)
 if path.exists():raise FileExistsError(path)
 path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['H0','H1','Q0','Q1','cubic_H0','cubic_H1','lower_V_mod128','joint_lift_trace']},indent=2),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--precision',type=int,default=512);p.add_argument('--out',required=True);a=p.parse_args();run(a.precision,a.out)
