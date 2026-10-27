#!/usr/bin/env python3
"""Exact rational order-49 divisor on the unique order-eligible q=83 orbit.
Cantor composition plus reduction in the phi basis. The separate checker
uses interpolation, Gaussian inversion, a different field basis and ladder.
"""
import json,math,argparse
from pathlib import Path
q=83
# field in phi basis; phi^2=phi+1
N=q*q

def add(x,y):return (x%q+y%q)%q+q*((x//q+y//q)%q)
def neg(x):return (-x%q)%q+q*((-(x//q))%q)
def sub(x,y):return add(x,neg(y))
def mul(x,y):
 a,b=x%q,x//q;c,d=y%q,y//q
 return (a*c+b*d)%q+q*((a*d+b*c+b*d)%q)
def pw(x,n):
 y=1
 while n:
  if n&1:y=mul(y,x)
  x=mul(x,x);n//=2
 return y
def inv(x):
 if not x:raise ZeroDivisionError
 return pw(x,N-2)
def tr(a):
 while len(a)>1 and a[-1]==0:a.pop()
 return a

def pa(a,b):return tr([add(a[i] if i<len(a) else 0,b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))])
def pn(a):return [neg(x) for x in a]
def ps(a,b):return pa(a,pn(b))
def pm(a,b):
 c=[0]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]=add(c[i+j],mul(x,y))
 return tr(c)
def scale(a,t):return tr([mul(x,t) for x in a])
def divmodp(a,b):
 if b==[0]:raise ZeroDivisionError
 a=a[:];r=[0]*max(1,len(a)-len(b)+1);il=inv(b[-1])
 while a!=[0] and len(a)>=len(b):
  j=len(a)-len(b);v=mul(a[-1],il);r[j]=add(r[j],v)
  for i,x in enumerate(b):a[i+j]=sub(a[i+j],mul(v,x))
  tr(a)
 return tr(r),a
def quo(a,b):
 x,r=divmodp(a,b);assert r==[0],(a,b,r);return x
def mod(a,b):return divmodp(a,b)[1]
def mon(a):return scale(a,inv(a[-1]))
def gcdex(a,b):
 r0,r1=a[:],b[:];s0,s1=[1],[0];t0,t1=[0],[1]
 while r1!=[0]:
  u,r2=divmodp(r0,r1);r0,r1=r1,r2;s0,s1=s1,ps(s0,pm(u,s1));t0,t1=t1,ps(t0,pm(u,t1))
 c=inv(r0[-1]);return scale(r0,c),scale(s0,c),scale(t0,c)
def ev(a,x):
 y=0
 for c in a[::-1]:y=add(mul(y,x),c)
 return y
# x=5+1/t, z=v/t^3 gives F(t)=delta*t^6*f(5+1/t)
old=[5*30*30%q,12,0,10*30%q,0,0,1]
f=[0]*7
for i,a in enumerate(old):
 for j in range(i+1):f[6-j]=add(f[6-j],a*math.comb(i,j)*pow(5,i-j,q)%q)
delta=9+q*((-3)%q)
f=scale(tr(f),delta)
assert len(f)==6
ID=([1],[0])
def valid(D):
 u,v=D
 assert u[-1]==1
 assert (len(v)<len(u)) if u!=[1] else (v==[0])
 assert mod(ps(f,pm(v,v)),u)==[0]
def red(u,v):
 u=mon(u);v=mod(v,u)
 while len(u)>3:
  u=mon(quo(ps(f,pm(v,v)),u));v=mod(pn(v),u)
 if u==[1]:v=[0]
 D=(u,v);valid(D);return D
def plus(D,E):
 if D==ID:return E
 if E==ID:return D
 u1,v1=D;u2,v2=E
 d1,e1,e2=gcdex(u1,u2)
 d,c1,c2=gcdex(d1,pa(v1,v2))
 s1,s2,s3=pm(c1,e1),pm(c1,e2),c2
 u=quo(pm(u1,u2),pm(d,d))
 v=quo(pa(pa(pm(pm(s1,u1),v2),pm(pm(s2,u2),v1)),pm(s3,pa(pm(v1,v2),f))),d)
 return red(u,mod(v,u))
def times(D,n):
 E=ID
 while n:
  if n&1:E=plus(E,D)
  D=plus(D,D);n//=2
 return E

_raw_plus=plus
TRACE=[]
def plus(D,E):
    R=_raw_plus(D,E)
    TRACE.append({'left':[D[0],D[1]],'right':[E[0],E[1]],'result':[R[0],R[1]]})
    return R

def run():
    TRACE.clear()
    assert gcdex(f,[mul(i%q,f[i]) for i in range(1,len(f))])[0]==[1]
    D=([neg(83),1],[4189]);valid(D)
    order=45724644;cofactor=19044
    assert order==7**4*cofactor and cofactor%7
    E=times(D,cofactor)
    E7=times(E,7);E49=times(E,49);DN=times(D,order)
    assert E7!=ID and E49==ID and DN==ID
    assert E7==([446,4060,1],[5496,3078])
    roots={mul(y,y):y for y in range(N)}
    ncurve=1+sum((1 if ev(f,x)==0 else 2) for x in range(N) if ev(f,x) in roots)
    assert ncurve==6634
    phi_symbol=pw(83,(N-1)//7)
    assert phi_symbol!=1 and pw(3,(N-1)//7)==1 and pw(neg(1)+0,(N-1)//7)==1
    sqrt5=add(neg(1),mul(2,83))
    assert pw(sqrt5,(N-1)//7)==1
    return {'schema':'beal.block63.jacobian83.v1','status':'PASS_ORDER_49_WITNESS',
       'field':'F83[phi]/(phi^2-phi-1); encode a+b*phi as a+83*b',
       'even_curve_coefficients':old,'delta':delta,'odd_change':'x=5+1/t, z=y/t^3',
       'odd_curve_coefficients':f,'odd_curve_points':ncurve,'jacobian_order':order,
       'cofactor':cofactor,'D':D,'E':E,'E7':E7,'E49':E49,'D_times_order':DN,
       'phi_seventh_symbol':phi_symbol,'sqrt5_seventh_symbol':1,'three_seventh_symbol':1,
       'operation_count':len(TRACE),'addition_transcript':TRACE,
       'finite_conclusion':'This finite Jacobian does not have all 7^4 geometric 7-torsion points rational.',
       'nonclaims':['Not a Beal counterexample','No full group decomposition asserted',
                    'No independent analytical or Galois proof from this computation']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=run();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(d['status'],d['E'],d['E7'],'operations',d['operation_count'])
if __name__=='__main__':main()
