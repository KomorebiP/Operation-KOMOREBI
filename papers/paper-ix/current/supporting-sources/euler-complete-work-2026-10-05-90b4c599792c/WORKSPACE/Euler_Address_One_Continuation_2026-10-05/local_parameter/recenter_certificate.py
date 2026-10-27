#!/usr/bin/env python3
"""Finite Euler parameter recentering certificate, standard library only."""
from pathlib import Path
import sys,json,time,hashlib,argparse,math
HERE=Path(__file__).resolve().parent
SRC=HERE.parent/'recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate'
sys.path.insert(0,str(SRC))
import fast_parameter_certificate as old
base=old.base

def run(P,out,input_path=None):
 start=time.time()
 prior=json.loads(Path(input_path or SRC/'fast_certificate_629.json').read_text())
 oldN=prior['joint_precision']; tc=int(prior['candidate_T_residue']); zc=int(prior['candidate_Z_residue'])
 Bc=17659+(1<<18)*tc; s=18+oldN; r=Bc*(1<<640)-161; Qpar=2*P
 budget=641+s-(2*(161+Qpar)).bit_length()
 assert P<=budget and (1<<640)>2*(161+Qpar)
 assert 2*r-1>P
 base.B=base.bernoullis(max(256,P));base.twoB=old.fast_twoB
 M=1<<P;mu=-154
 bound=(r.bit_count()-1)//3
 costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range(bound+1)]
 assert min(costs)==mu and max(q for q,c in enumerate(costs) if c==mu)==161
 Q=(P+r.bit_count()+mu-2)//3
 gam=base.gamma(r,mu,P,Q);src=list(base.source(P))
 assert all(old.slow.val(v,P)>=i for i,v in enumerate(src))
 lo,hi=old.local_split(P,10202,15,gam,src)
 # B G_B = B L_center + B_center U_center, for B == B_center mod2^s.
 raw0=[(17659*l+Bc*u)%M for l,u in zip(lo,hi)]
 raw1=[((1<<18)*l)%M for l in lo]
 assert all(v%(1<<178)==0 for v in raw0+raw1)
 H0=[v>>178 for v in raw0];H1=[v>>178 for v in raw1]
 N=P-179
 (tau,zeta),Q0,Q1,trace=old.slow.lift_joint(H0,H1,N)
 assert tau%(1<<oldN)==tc and zeta%(1<<oldN)==zc
 # Independent elimination of parameter, lifting univariate critical equation.
 def tm(z,m):return (-base.ev(H0,z,m)*pow(base.ev(H1,z,m),-1,m))%m
 def em(z,m):return (base.ev(Q0,z,m)+tm(z,m)*base.ev(Q1,z,m))%m
 zs=[z for z in (0,1) if em(z,2)==0];assert len(zs)==1
 for k in range(1,N):
  m=1<<(k+1);roots=[z for z in (zs[0],zs[0]+(1<<k)) if em(z,m)==0]
  assert len(roots)==1;zs=roots
 assert (tm(zs[0],1<<N),zs[0])==(tau,zeta)
 # Whole retained T interval has the genuine terminal label, by global carry cutoff.
 # B<2^(18+N+1), hence s2(r)<=637+18+N+1.
 maxpop=637+18+N+1; globalcut=(maxpop-1)//3
 assert globalcut<(1<<640)
 localcost=[3*q+2-(160-q).bit_count() for q in range(161)]
 assert min(localcost)==-1 and [q for q,v in enumerate(localcost) if v==-1]==[1]
 assert -154==3*161+1-638
 # Future upper carries are impossible in this interval: all relevant q<2^640.
 outdata={
  'status':'passed','global_precision':P,'finite_template_precision_budget':budget,
  'joint_precision':N,'prior_joint_precision':oldN,'center_B':str(Bc),
  'center_T':str(tc),'B_cylinder_depth':s,'computed_packet_max':Q,
  'parity_packet_cutoff':Qpar,'candidate_T_residue':str(tau),
  'candidate_Z_residue':str(zeta),'candidate_T_bitlength':tau.bit_length(),
  'excluded_initial_parameter_interval':[0,str(tau)],
  'certificate_interval_terminal_cutoff':globalcut,
  'H0':list(map(str,H0)),'H1':list(map(str,H1)),
  'Q0':list(map(str,Q0)),'Q1':list(map(str,Q1)),
  'joint_lift_trace':trace,'independent_elimination':'passed',
  'prior_candidate_lifts':'passed','elapsed_seconds':time.time()-start,
  'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  'inherited_source_sha256':hashlib.sha256((SRC/'fast_parameter_certificate.py').read_bytes()).hexdigest(),
  'scope':'Uniform finite affine Euler template only on T=center_T mod2^prior_joint_precision. Outside cylinder use prior certificate.',
  'nonclaims':['No universal Euler simplicity','No exact critical Euler input inferred','No all-precision analytic interpolation','No Lean build']}
 Path(out).write_text(json.dumps(outdata,indent=2)+'\n')
 print(json.dumps({k:v for k,v in outdata.items() if k not in ['H0','H1','Q0','Q1','joint_lift_trace']},indent=2),flush=True)

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--precision',type=int,default=1096);a.add_argument('--out',required=True);a.add_argument('--input');n=a.parse_args();run(n.precision,n.out,n.input)
