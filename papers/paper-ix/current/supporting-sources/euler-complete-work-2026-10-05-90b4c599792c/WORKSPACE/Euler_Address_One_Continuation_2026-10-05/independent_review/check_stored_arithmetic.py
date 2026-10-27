#!/usr/bin/env python3
"""Independent exact modular audit of the retained coefficient data; no author imports."""
from pathlib import Path
import hashlib,json,platform,time
started=time.time();ROOT=Path(__file__).resolve().parents[1]
paths=[ROOT/'local_parameter/recenter_1096.json',ROOT/'recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate/fast_certificate_629.json']
c,old=[json.loads(p.read_text()) for p in paths]
P=c['global_precision'];N=c['joint_precision'];M=1<<N
h0,h1,q0,q1=[list(map(int,c[k])) for k in ['H0','H1','Q0','Q1']]
ev=lambda a,x,m:sum(a_i*pow(x,i,m) for i,a_i in enumerate(a))%m
deriv=lambda a:[i*x for i,x in enumerate(a) if i]
d0,d1,dq0,dq1=map(deriv,[h0,h1,q0,q1])
assert P==1096 and N==P-179 and len(h0)==len(h1)==(P-1)//15+1==74
assert all(0<=a<2*M for a in h0+h1)
assert all(a%2==0 for a in d0+d1)
assert q0==[(a//2)%M for a in d0] and q1==[(a//2)%M for a in d1]
assert [a%2 for a in h0]==[1,0,1]+[0]*(len(h0)-3)
assert [a%2 for a in h1]==[1]+[0]*(len(h1)-1)
assert [a%2 for a in q0]==[0,1]+[0]*(len(q0)-2)
assert all(a%2==0 for a in q1)
# Starting residue from exhaustive mod-2 equations; then full-Jacobian Newton doubling.
roots=[(t,z) for t in [0,1] for z in [0,1] if (ev(h0,z,2)+t*ev(h1,z,2))%2==0 and (ev(q0,z,2)+t*ev(q1,z,2))%2==0]
assert roots==[(1,0)];t,z=roots[0];bits=1;doubling=[]
while bits<N:
 target=min(2*bits,N);m=1<<target
 f=(ev(h0,z,m)+t*ev(h1,z,m))%m;g=(ev(q0,z,m)+t*ev(q1,z,m))%m
 a=ev(h1,z,m);b=(ev(d0,z,m)+t*ev(d1,z,m))%m
 d=ev(q1,z,m);e=(ev(dq0,z,m)+t*ev(dq1,z,m))%m
 det=(a*e-b*d)%m;assert det%2==1;inv=pow(det,-1,m)
 dt=(-e*f+b*g)*inv%m;dz=(d*f-a*g)*inv%m
 t=(t+dt)%m;z=(z+dz)%m
 assert (ev(h0,z,m)+t*ev(h1,z,m))%m==0
 assert (ev(q0,z,m)+t*ev(q1,z,m))%m==0
 doubling.append(target);bits=target
assert (t,z)==(int(c['candidate_T_residue']),int(c['candidate_Z_residue']))
assert t.bit_length()==915 and 0<=t<M and 0<=z<M
assert t%(1<<450)==int(old['candidate_T_residue'])
assert z%(1<<450)==int(old['candidate_Z_residue'])
trace=c['joint_lift_trace'];assert len(trace)==N
for k,entry in enumerate(trace,1):
 m=1<<k;tk=int(entry['T']);zk=int(entry['Z'])
 assert entry['bits']==k and (tk,zk)==(t%m,z%m)
 assert (ev(h0,zk,m)+tk*ev(h1,zk,m))%m==0
 assert (ev(q0,zk,m)+tk*ev(q1,zk,m))%m==0
# Entire reduction includes newly added degrees, which must vanish at old precision.
for key,H in [('H0',h0),('H1',h1)]:
 oldH=list(map(int,old[key]));mod=1<<(old['global_precision']-178)
 assert [a%mod for a in H]==oldH+[0]*(len(H)-len(oldH))
Bc=17659+(1<<18)*int(old['candidate_T_residue']);r=(Bc<<640)-161
assert Bc==int(c['center_B']);assert c['B_cylinder_depth']==468
assert c['finite_template_precision_budget']==641+468-(2*(161+2*P)).bit_length()==1096
assert c['computed_packet_max']==(P+r.bit_count()-154-2)//3==603
assert 3*604+1-r.bit_count()+154>=P
assert 15*74>=P
report={'status':'passed','coefficient_domain':'exact integers modulo powers of two','python':platform.python_version(),'global_precision':P,'normalized_value_precision':P-178,'half_derivative_precision':N,'newton_precision_steps':doubling,'full_trace_prefixes_checked':N,'T_bitlength':t.bit_length(),'Z_bitlength':z.bit_length(),'prior_residue_precision':450,'complete_H_degree_cutoff':73,'first_omitted_degree_global_valuation':15*74,'packet_q_max':603,'first_omitted_packet_scalar_lower_bound':3*604+1-r.bit_count()+154,'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'seconds':time.time()-started,'nonclaims':['Does not independently establish source-to-Euler identification or uniform recentering theorem','Does not establish actual critical Euler zero']}
out=Path(__file__).with_suffix('.json');out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
