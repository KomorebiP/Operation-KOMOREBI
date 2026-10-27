#!/usr/bin/env python3
"""Exact test of a candidate cubic self-twist intertwiner, one actual example.
Imports the rational cyclotomic algebra, suppressing its separate result output.
"""
import importlib.util, contextlib, io, pathlib, json
from itertools import product
p=pathlib.Path(__file__).with_name('cyclotomic_check113.py')
spec=importlib.util.spec_from_file_location('cyclotomic',p)
c=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(c)
Q=c.Q; z=c.zero; o=c.one
I=tuple(tuple(o if i==j else z for j in range(3)) for i in range(3))
def ma(a,b): return tuple(tuple(c.add(a[i][j],b[i][j]) for j in range(3)) for i in range(3))
def mn(a):return tuple(tuple(c.neg(v) for v in r) for r in a)
def ms(a,b):return ma(a,mn(b))
def mm(a,b):return tuple(tuple(sumf(c.mul(a[i][k],b[k][j]) for k in range(3)) for j in range(3)) for i in range(3))
def sumf(vals):
 r=z
 for v in vals:r=c.add(r,v)
 return r
def sm(a,s):return tuple(tuple(c.mul(v,s) for v in r) for r in a)
def mi(a):
 m=[list(a[i])+list(I[i]) for i in range(3)]
 for i in range(3):
  k=next(k for k in range(i,3) if m[k][i]!=z);m[i],m[k]=m[k],m[i]
  t=c.inv(m[i][i]);m[i]=[c.mul(t,v) for v in m[i]]
  for k in range(3):
   if k!=i:
    t=m[k][i];m[k]=[c.sub(v,c.mul(t,w)) for v,w in zip(m[k],m[i])]
 return tuple(tuple(m[i][j+3] for j in range(3)) for i in range(3))
def mp(a,n):
 if n<0:return mp(mi(a),-n)
 r=I
 while n:
  if n&1:r=mm(r,a)
  a=mm(a,a);n//=2
 return r
def va(a):
 vals=[c.valuation(a[i][j])+i-j for i in range(3) for j in range(3) if a[i][j]!=z]
 return min(vals) if vals else 10**9
def mt(a):return sumf(a[i][i] for i in range(3))
Pi=((z,z,c.piF),(o,z,c.scale(o,-3)),(z,o,c.scale(o,-3)))
assert va(Pi)==1
assert mm(Pi,mi(Pi))==I
B=mp(Pi,-10)
C=sm(I,c.scale(o,Q(1,3)))
assert va(C)==-6

def poly_matrix(a):
 r=sm(I,z)
 for j,coef in enumerate(a):r=ma(r,sm(mp(Pi,j),c.scale(o,coef)))
 return r
assert poly_matrix(c.beta)==B

def padic_log_mod7(u):
 t=c.sub(u,o)
 if t==z:return z
 val=c.valuation(t); assert val>=1
 # For k>=27, k-6*v3(k)>=9, uniformly, hence terms vanish mod p_L^7.
 r=z; term=o
 for k in range(1,27):
  term=c.mul(term,t)
  r=c.add(r,c.scale(term,Q((-1)**(k+1),k)))
 return r

selected=[]
for dg in product(range(3),repeat=3):
 D=tuple(tuple(c.scale(o,dg[i]) if i==j else z for j in range(3)) for i in range(3))
 g=ma(I,mm(D,mp(Pi,4)))
 # Need g B g^-1 = B+C modulo P^-5, matching theta^(g^-1) at deep level.
 err=ms(ms(mm(mm(g,B),mi(g)),B),C)
 if va(err)>=-5:selected.append((dg,g,va(err)))
assert selected

dg,g,errval=selected[0]
gi=mi(g)
rows=[]
for r in range(1,7):
 ue=c.add(o,c.power(c.x,r)); u=ma(I,mp(Pi,r))
 # For theta^g(u)=theta(g^-1 u g), the beta parameter is g beta g^-1.
 h=mm(mm(gi,u),g)
 rem=ms(h,I); le=o; lm=I; digits=[];member=True
 for j in range(1,6):
  options=[]
  for a in range(3):
   res=ms(rem,sm(mp(Pi,j),c.scale(o,a)))
   if va(res)>=j+1:options.append((a,res))
  if not options:member=False;break
  a,rem=options[0];digits.append(a)
  le=c.add(le,c.scale(c.power(c.x,j),a));lm=ma(lm,sm(mp(Pi,j),c.scale(o,a)))
 row={'r':r,'in_H1':member,'L_representative_digits':digits}
 if member:
  y=mm(mi(lm),h)
  assert va(ms(y,I))>=6
  echi=c.trace(c.mul(c.beta,c.sub(padic_log_mod7(le),padic_log_mod7(ue))))/3
  ey=c.trace(mt(mm(B,ms(y,I))))/9
  row['theta_conjugate_ratio_exponent']=str(c.fractional_part_3(echi+ey))
 rows.append(row)
norm_checks=[c.fractional_part_3(c.trace(padic_log_mod7(c.add(o,c.power(c.x,r))))/9)==0 for r in (1,2,3)]
assert all(norm_checks)
assert all(row['in_H1'] and row.get('theta_conjugate_ratio_exponent')=='0' for row in rows)
assert len(selected)==3 and errval==-3
print(json.dumps({'norm_kernel_unit_generator_checks':norm_checks,'candidate_diagonal':dg,'stratum_error_valuation':errval,'all_deep_stratum_candidates':[list(v[0]) for v in selected], 'unit_generator_tests':rows,'scope':'Exact candidate intertwiner at six principal-unit generators and three norm-kernel generators; full simple-character consequence uses the ARITHMETIC113 reduction. Not a proof of AI occurrence.'},indent=2))
