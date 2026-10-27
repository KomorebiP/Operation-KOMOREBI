#!/usr/bin/env python3
"""Fresh actual arithmetic reconstruction against recentered finite templates."""
from pathlib import Path
import json,time,hashlib,sys
import recenter_certificate as rec
old=rec.old;base=rec.base
started=time.time();checks=[]
c=json.loads((rec.HERE/'recenter_1096.json').read_text());P=c['global_precision'];N=c['joint_precision'];M=1<<P
B0=int(c['center_B']);T0=int(c['center_T']);h=c['prior_joint_precision'];s=c['B_cylinder_depth']
base.B=base.bernoullis(P);base.twoB=old.fast_twoB;source=list(base.source(P))
H0=list(map(int,c['H0']));H1=list(map(int,c['H1']))
for S in [0,1,3]:
 T=T0+(1<<h)*S;B=17659+(1<<18)*T;r=B*(1<<640)-161
 bound=(r.bit_count()-1)//3
 costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range(bound+1)]
 assert min(costs)==-154 and max(q for q,v in enumerate(costs) if v==-154)==161
 Q=(P+r.bit_count()-154-2)//3
 gam=base.gamma(r,-154,P,Q);lo,hi=old.local_split(P,10202,15,gam,source)
 actual=[(B*(l+u))%M for l,u in zip(lo,hi)]
 assert all(v%(1<<178)==0 for v in actual)
 m=1<<(P-178)
 actual=[v>>178 for v in actual]
 expected=[(a+T*b)%m for a,b in zip(H0,H1)]
 assert actual==expected
 checks.append({'type':'fresh_actual_coefficient_reconstruction','S':S,'packet_max':Q,'complete_local_coefficients':len(actual),'precision_after_content':P-178})
 # Exact finite factorial-unit congruence at all nonzero relevant offsets.
 K=641+s
 Qpar=2*P
 for d in range(-2*161+1,2*(Qpar-161)+1):
  if d:
   vd=base.v2(d)
   assert base.v2((1<<641)*B+d)==vd
   assert ((((1<<641)*B+d)>>vd)-(((1<<641)*B0+d)>>vd))%(1<<P)==0
 checks.append({'type':'all_relevant_factorial_offsets','S':S,'offset_count':2*Qpar-1,'precision':P})
 # Exact binomial differences at actual giant Bernoulli indices.
 n=2*(B0*(1<<640)-161);nn=2*r
 b0=bn=1
 for k in range(1,P+1):
  b0=b0*(n-k+1)//k;bn=bn*(nn-k+1)//k
  assert (bn-b0)%(1<<(K-(k.bit_length()-1)))==0
 checks.append({'type':'exact_giant_binomial_finite_lipschitz_bound','S':S,'k_max':P})
# Deliberately compare the old global base approximation at the new precision.
# It is a negative control, not a claimed valid template at P=1096.
r=(1<<640)-161;Q=(P+r.bit_count()-154-2)//3
gam=base.gamma(r,-154,P,Q);lo,hi=old.local_split(P,10202,15,gam,source)
oldmodel=[(B0*l+u)%M for l,u in zip(lo,hi)]
newmodel=[(((a+T0*b)%(1<<(P-178)))<<178) for a,b in zip(H0,H1)]
diffs=[(a-b)%M for a,b in zip(oldmodel,newmodel)]
minimum=min(base.v2(v,P) for v in diffs)
assert minimum<P
checks.append({'type':'negative_control_old_global_template_extrapolation','first_disagreement_global_valuation':minimum,'after_content_valuation':minimum-178,'status':'correctly rejected'})
out={'status':'passed','checks':checks,'seconds':time.time()-started,
     'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     'nonclaims':['Finite checks do not replace universal local-template proof','No Lean build']}
(rec.HERE/'RECENTER_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2),flush=True)
