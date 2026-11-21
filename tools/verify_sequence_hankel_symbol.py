"""Exact universal product-polynomial certificate in Z[A,p,q,x,y]."""
import argparse,json,time
from pathlib import Path


def constant(n):return {(0,0,0,0,0):n} if n else {}
def variable(i):
    key=[0]*5;key[i]=1;return {tuple(key):1}
def add(a,b,scale=1):
    out=dict(a)
    for key,value in b.items():
        out[key]=out.get(key,0)+scale*value
        if not out[key]:out.pop(key)
    return out
def mul(a,b):
    out={}
    for left,x in a.items():
        for right,y in b.items():
            key=tuple(i+j for i,j in zip(left,right));out[key]=out.get(key,0)+x*y
    return {key:value for key,value in out.items() if value}
def power(a,n):
    out=constant(1)
    for _ in range(n):out=mul(out,a)
    return out
def scale(a,n):return {key:value*n for key,value in a.items() if value*n}


def monic_divide(poly,g,axis):
    remainder=dict(poly);quotient={}
    while True:
        keys=[key for key in remainder if key[axis]>=4]
        if not keys:break
        key=max(keys,key=lambda key:key[axis]);value=remainder[key]
        monomial=list(key);monomial[axis]-=4;term={tuple(monomial):value}
        quotient=add(quotient,term);remainder=add(remainder,mul(term,g),-1)
    return quotient,remainder


parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
args=parser.parse_args();started=time.perf_counter();A,p,q,x,y=[variable(i) for i in range(5)]
def g(t):return add(add(add(add(power(t,4),mul(p,power(t,3))),mul(q,power(t,2))),mul(mul(A,p),t)),power(A,2))
t=mul(x,y)
hd=add(power(add(add(power(t,2),mul(q,t)),power(A,2)),2),mul(mul(power(p,2),t),power(add(t,A),2)),-1)
qm=add(q,scale(A,2),-1)
hc=add(add(add(add(power(t,4),mul(qm,power(t,3)),-1),mul(add(mul(A,add(power(p,2),scale(q,2),-1)),scale(power(A,2),2)),power(t,2))),mul(mul(power(A,2),qm),t),-1),power(A,4))
h=mul(mul(add(t,A,-1),hd),hc)
U,remainder=monic_divide(h,g(x),3);V,remainder=monic_divide(remainder,g(y),4)
assert not remainder
assert add(mul(U,g(x)),mul(V,g(y)))==h
def serialized(poly):return [[*key,value] for key,value in sorted(poly.items())]
result={'outcome':'Universal polynomial ideal identity verified coefficient by coefficient',
    'ring':'Z[A,p,q,x,y]','identity':'h(x*y)=U*g(x)+V*g(y)',
    'g':'t^4+p*t^3+q*t^2+A*p*t+A^2','h':'(t-A)*((t^2+q*t+A^2)^2-p^2*t*(t+A)^2)*(t^4-(q-2A)t^3+(A(p^2-2q)+2A^2)t^2-A^2(q-2A)t+A^4)',
    'U_monomials':serialized(U),'V_monomials':serialized(V),'h_monomial_count':len(h),
    'consequence':'h(x*y)^7 is in (g(x)^4,g(y)^4) by the binomial expansion; no separability or generic-specialization hypothesis is needed',
    'elapsed_seconds':time.perf_counter()-started}
Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'outcome':result['outcome'],'U_terms':len(U),'V_terms':len(V),'h_terms':len(h),'elapsed_seconds':result['elapsed_seconds']}))
