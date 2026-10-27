#!/usr/bin/env python3
"""Finite coefficient certificate for a terminal-161 parameter cylinder.
No all-precision analytic interpolation of the integer Euler family is assumed.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, platform, time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'Euler_Closure_Attempt/Komorebi_Euler_Cubic_Unit_v26/checks/check_critical_value.py'
spec=importlib.util.spec_from_file_location('inherited_euler',BASE)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)

def val(n:int,cap:int)->int:
 return cap if n==0 else (abs(n)&-abs(n)).bit_length()-1

def add(a,b,mod):
 return [((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0))%mod for i in range(max(len(a),len(b)))]

def split_residual(P:int):
 r=(1<<640)-161; mu=-154;j=161; mod=1<<P
 # Here s2(r)=638. The general scalar bound makes every later packet zero
 # coefficientwise even BEFORE localization. This computes the same template
 # as the longer parity cutoff q<2P.
 Q=(P+r.bit_count()+mu-2)//3
 gam=base.gamma(r,mu,P,Q); src=list(base.source(P)); low=[0]*(2*Q+P); high=[0]*len(low); pq=[1]
 for q,g in enumerate(gam):
  if q:
   i=q-1;pq=base.mul(pq,[-i,1],mod);pq=base.mul(pq,[-2*i-1,2],mod)
  if g:
   term=base.mul(pq,base.shift(src,-q,mod),mod); target=low if q<j else high
   for n,a in enumerate(term):target[n]=(target[n]+g*a)%mod
 return low,high,Q

def norm_affine(low,high,center,depth,content,P):
 mod=1<<P;s=17659;a=1<<18
 L=base.local(low,center,depth,P);U=base.local(high,center,depth,P)
 H0=[(s*l+u)%mod for l,u in zip(L,U)]
 H1=[(a*l)%mod for l in L]
 assert all(z%(1<<content)==0 for z in H0+H1),'required normalization does not hold'
 return [z>>content for z in H0],[z>>content for z in H1]

def lift_joint(H0,H1,N):
 mod=1<<N
 d0=base.deriv(H0);d1=base.deriv(H1)
 assert all(z%2==0 for z in d0+d1)
 Q0=[(z//2)%mod for z in d0];Q1=[(z//2)%mod for z in d1]
 # Global mod-2 normal form of the half derivative is fixed affine in Z.
 assert Q0[1]%2==1 and all(z%2==0 for z in Q0[2:])
 assert all(z%2==0 for z in Q1)
 assert H1[0]%2==1 and all(z%2==0 for z in H1[1:])
 def eq(t,z,m):return ((base.ev(H0,z,m)+t*base.ev(H1,z,m))%m,(base.ev(Q0,z,m)+t*base.ev(Q1,z,m))%m)
 roots=[(t,z) for t in (0,1) for z in (0,1) if eq(t,z,2)==(0,0)]
 assert len(roots)==1
 trace=[{'bits':1,'T':str(roots[0][0]),'Z':str(roots[0][1])}]
 for k in range(1,N):
  t,z=roots[0]; m=1<<(k+1)
  roots=[(t+(dt<<k),z+(dz<<k)) for dt in (0,1) for dz in (0,1) if eq(t+(dt<<k),z+(dz<<k),m)==(0,0)]
  assert len(roots)==1,('not a unique lift',k,roots)
  trace.append({'bits':k+1,'T':str(roots[0][0]),'Z':str(roots[0][1])})
 return roots[0],Q0,Q1,trace

def run(P,out):
 started=time.time();base.B=base.bernoullis(max(256,P));mod=1<<P
 # Finite template's uniform conditions.
 qpar=2*P;budget=641-(2*(161+qpar)+1-1).bit_length()
 assert (1<<640)>2*(161+qpar) and P<=budget
 low,high,Q=split_residual(P)
 H0,H1=norm_affine(low,high,10202,15,178,P);N=P-179
 (tau,zeta),Q0,Q1,trace=lift_joint(H0,H1,N)
 # All lower residues have exactly one simple root. V is the lower prefix
 # divided by 2^153. Scalar integrality supplies the division globally.
 assert all(x%(1<<153)==0 for x in low)
 V=[x>>153 for x in low]
 Vmod=[x%2 for x in V]
 assert Vmod[1]==1 and all(x==0 for i,x in enumerate(Vmod) if i!=1)
 vr=[x for x in range(128) if base.ev(V,x,128)==0]
 assert vr==[90]
 # Cubic critical residues on its entire ball; use actual b*K = affine model.
 A0,A1=norm_affine(low,high,90,7,162,P)
 assert min(val(x,P-162) for x in A1)>=8
 DA0=base.deriv(A0);DA1=base.deriv(A1)
 assert all(x%512==0 for x in DA1)
 droots=[y for y in range(512) if base.ev(DA0,y,512)==0]
 residues=sorted({y%256 for y in droots})
 assert residues==[79,221],residues
 assert val(base.ev(A0,221,1<<16),16)==2
 assert all(x%8==0 for x in A1)
 # A restricted integral cubic is Lipschitz: at 221+256Z its value
 # is constant modulo 8, so this whole critical branch cannot vanish.
 # Verify a second independent joint lift by Newton's 2x2 Jacobian update.
 t=z=0
 for k in range(N):
  mk=1<<k; nxt=mk<<1
  f=(base.ev(H0,z,nxt)+t*base.ev(H1,z,nxt))%nxt
  q=(base.ev(Q0,z,nxt)+t*base.ev(Q1,z,nxt))%nxt
  if k:
   assert f%mk==0 and q%mk==0
  # Jacobian mod 2 is [[1,0],[0,1]] under checked conditions.
  dt=(f//mk)&1;dz=(q//mk)&1
  t+=dt*mk;z+=dz*mk
 assert (t,z)==(tau,zeta)
 result={
  'status':'finite certificate passed','claim_scope':'finite coefficient certificate for actual terminal-161 r=(17659+2^18*T)*2^640-161; not universal Euler simplicity',
  'global_precision':P,'finite_template_precision_budget':budget,'computed_packet_max':Q,'parity_packet_cutoff':qpar,
  'deep_content':178,'joint_precision':N,'excluded_initial_parameter_interval':[0,str(tau)],
  'candidate_T_residue':str(tau),'candidate_Z_residue':str(zeta),'candidate_T_bitlength':tau.bit_length(),
  'H0':list(map(str,H0)),'H1':list(map(str,H1)),'Q0':list(map(str,Q0)),'Q1':list(map(str,Q1)),
  'lower_root_mod128':vr,'cubic_critical_residues_mod256':residues,'other_branch_value_valuation':2,
  'cubic_H0':list(map(str,A0)),'cubic_H1':list(map(str,A1)),
  'lower_V_mod128':list(map(lambda a:str(a%128),V)),
  'joint_lift_trace':trace,
  'source_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  'python':platform.python_version(),'seconds':time.time()-started,
  'nonclaims':['No Lean compilation','Not an exact analytic interpolation of the undepleted parameter family',
   'No exact singular Euler input identified by a modular candidate',
   'Inherited Bernoulli and source arithmetic shared with prior release']}
 out=Path(out);out.parent.mkdir(exist_ok=True,parents=True)
 if out.exists(): raise FileExistsError(out)
 out.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['H0','H1','Q0','Q1','joint_lift_trace','lower_V_mod128','cubic_H0','cubic_H1']},indent=2),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--precision',type=int,default=272);ap.add_argument('--out',type=str,required=True)
 ns=ap.parse_args();run(ns.precision,ns.out)
