#!/usr/bin/env python3
"""Exact central-type scalar test on the actual eta of the cyclotomic fixture."""
import importlib.util,contextlib,io,pathlib,json,sys
p=pathlib.Path(__file__).with_name('self_twist113.py')
spec=importlib.util.spec_from_file_location('st',p);st=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(st)
for key in ['c','Q','z','o','I','ma','mn','ms','mm','mi','mp','sm','va','mt','Pi','B','g','gi','padic_log_mod7']:
 globals()[key]=getattr(st,key)
from functools import lru_cache
correction=int(sys.argv[1]) if len(sys.argv)>1 else 0
assert correction in (0,1,2)
chi_coeff=c.add(c.beta,c.scale(c.power(c.x,-8),correction))
@lru_cache(None)
def PP(r):return mp(Pi,r)
def D(a,b,c0):return ((c.scale(o,a),z,z),(z,c.scale(o,b),z),(z,z,c.scale(o,c0)))
u0=ma(I,mm(D(1,0,0),PP(5)))
u1=ma(I,mm(D(0,1,0),PP(5)))
def htheta(h):
 rem=ms(h,I);le=o;lm=I
 for j in range(1,6):
  opts=[]
  for a in range(3):
   res=ms(rem,sm(PP(j),c.scale(o,a)))
   if va(res)>=j+1:opts.append((a,res))
  if not opts:return None
  a,rem=opts[0];le=c.add(le,c.scale(c.power(c.x,j),a));lm=ma(lm,sm(PP(j),c.scale(o,a)))
 y=mm(mi(lm),h)
 if va(ms(y,I))<6:return None
 e=c.trace(c.mul(chi_coeff,padic_log_mod7(le)))/3+c.trace(mt(mm(B,ms(y,I))))/9
 return c.fractional_part_3(e)
def root(e):
 e=c.fractional_part_3(e)
 assert (3*e).denominator==1,(e,'not cubic')
 return c.power(c.zeta3,int(3*e))
X=((z,z,o),(o,z,z),(z,o,z))
Z=((o,z,z),(z,c.zeta3,z),(z,z,c.power(c.zeta3,2)))
sections=[(a,b,mm(mp(u0,a),mp(u1,b)),mm(mp(X,a),mp(Z,b))) for a in range(3) for b in range(3)]
@lru_cache(None)
def eta(j):
 candidates=[]
 for a,b,s,W in sections:
  h=mm(j,mi(s));e=htheta(h)
  if e is not None:candidates.append((a,b,sm(W,root(e))))
 assert len(candidates)==1,(len(candidates),va(ms(j,I)))
 return candidates[0][2]
# Validate actual generators and central commutator before using the model.
assert htheta(mp(u0,3))==0 and htheta(mp(u1,3))==0
comm=mm(mm(mm(u0,u1),mi(u0)),mi(u1));commphase=htheta(comm)
assert commphase==Q(2,3),commphase
assert mm(X,Z)==sm(mm(Z,X),root(commphase))
assert eta(u0)==X and eta(u1)==Z
Pii=mi(Pi)
A=eta(mm(mm(Pi,u0),Pii)); BB=eta(mm(mm(Pi,u1),Pii))
# Finite Heisenberg averaging produces a nonzero intertwiner S.
S=None
for r in range(3):
 for s in range(3):
  R=tuple(tuple(o if (i,j)==(r,s) else z for j in range(3)) for i in range(3))
  acc=sm(I,z)
  for a,b,_,W in sections:
   acc=ma(acc,mm(mm(mm(mp(A,a),mp(BB,b)),R),mi(W)))
  if acc!=sm(I,z):S=acc;break
 if S is not None:break
assert S is not None
assert mm(S,X)==mm(A,S) and mm(S,Z)==mm(BB,S)
Sinv=mi(S)
Ag=eta(mm(mm(gi,u0),g));Bg=eta(mm(mm(gi,u1),g))
def omega_on_j(j):
 # j lies in UA5 here; logdet higher terms are trivial under coefficient1/3.
 return root(c.trace(mt(sm(ms(j,I),c.scale(o,Q(1,3)))))/9)
w0=omega_on_j(u0);w1=omega_on_j(u1)
Ts=[]
for a,b,_,W in sections:
 if mm(mm(W,Ag),mi(W))==sm(X,w0) and mm(mm(W,Bg),mi(W))==sm(Z,w1):Ts.append((a,b,W))
assert len(Ts)==1,len(Ts)
a,b,T=Ts[0]
h=mm(mm(mm(gi,Pi),g),Pii)
Eh=eta(h)
Delta=mm(mm(mm(mm(T,Eh),S),mi(T)),Sinv)
assert Delta==sm(I,Delta[0][0]),'not scalar'
assert c.power(Delta[0][0],3)==o
unit_tests=[]
for r in range(1,7):
 ur=ma(I,PP(r)); ue=c.add(o,c.power(c.x,r))
 e=htheta(mm(mm(gi,ur),g))
 assert e is not None
 ratio=c.fractional_part_3(e-c.trace(c.mul(chi_coeff,padic_log_mod7(ue)))/3)
 assert ratio==0
 unit_tests.append(str(ratio))
result={'wild_unit_correction_coefficient':correction,'corrected_unit_generator_ratios':unit_tests,'commutator_phase_mod1':str(commphase),'generator_cubes_trivial':True,'omega_generator_values':{'u0':list(map(str,w0)),'u1':list(map(str,w1))},'eta_intertwiner_Weyl_label':[a,b],'g3_minus1_order':va(ms(mp(g,3),I)),'uniformizer_commutator_H_character':str(htheta(h)) if htheta(h) is not None else 'not in H1','remaining_scalar_coefficients':list(map(str,Delta[0][0])),'remaining_scalar_is_one':Delta==I,'all_assertions_pass':True,'scope':'Exact scalar for the actual eta and uniformizer action; full central-type consequence requires the group-generation and scalar-independence argument in ARITHMETIC113. Not AI occurrence.'}
print(json.dumps(result,indent=2))
