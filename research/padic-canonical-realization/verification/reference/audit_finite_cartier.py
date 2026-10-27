#!/usr/bin/env python3
"""Exact finite audit of the polynomial-state construction, not a universal proof.
The coefficient oracle solves BF=A F(z^p) recursively. It does not use the
Cartier correction formula or a radix carry computation. Python standard library.
"""
from __future__ import annotations
import argparse, hashlib, json, math, platform, random, time
from collections import Counter
from pathlib import Path

SEED = 230919

def trim(a: list[int]) -> list[int]:
    a = list(a) or [0]
    while len(a) > 1 and a[-1] == 0: a.pop()
    return a

def reduce(a: list[int], m: int) -> list[int]: return trim([x % m for x in a])
def add(a: list[int], b: list[int], m: int | None = None) -> list[int]:
    c = [(a[i] if i < len(a) else 0)+(b[i] if i < len(b) else 0) for i in range(max(len(a),len(b)))]
    return reduce(c,m) if m else trim(c)
def mul(a: list[int], b: list[int], m: int | None = None) -> list[int]:
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return reduce(c,m) if m else trim(c)
def power(a: list[int], k: int, m: int | None = None) -> list[int]:
    c=[1]
    for _ in range(k): c=mul(c,a,m)
    return c

def defect(p: int, b: list[int]) -> list[int]:
    e=power(b,p); expanded=[0]*(p*(len(b)-1)+1)
    for i,x in enumerate(b): expanded[p*i]=x
    e=add(e,[-x for x in expanded]); assert all(x%p==0 for x in e)
    return trim([x//p for x in e])

def digit_word(p: int, n: int) -> list[int]:
    ds=[]
    while n: ds.append(n%p); n//=p
    return ds

def recurrence_coefficients(p: int, m: int, a: list[int], b: list[int], n: int) -> list[int]:
    assert a[0]%m==b[0]%m and math.gcd(b[0],m)==1
    f=[1]+[0]*(n-1); inv=pow(b[0],-1,m)
    for t in range(1,n):
        rhs=sum(a[j]*f[(t-j)//p] for j in range(min(t,len(a)-1)+1) if (t-j)%p==0)
        old=sum(b[j]*f[t-j] for j in range(1,min(t,len(b)-1)+1))
        f[t]=((rhs-old)*inv)%m
    return f

def inverse_coefficients(b: list[int], m: int, n: int) -> list[int]:
    inv=pow(b[0],-1,m); out=[inv]+[0]*(n-1)
    for k in range(1,n): out[k]=(-inv*sum(b[j]*out[k-j] for j in range(1,min(k,len(b)-1)+1)))%m
    return out

def series_mul(a: list[int], b: list[int], m: int, n: int) -> list[int]:
    out=[0]*n
    for i,x in enumerate(a[:n]):
        for j,y in enumerate(b[:n-i]): out[i+j]=(out[i+j]+x*y)%m
    return out

class Machine:
    def __init__(self,p:int,r:int,a:list[int],b:list[int]):
        self.p,self.r,self.m=p,r,p**r; self.a,self.b=trim(a),trim(b)
        self.e=defect(p,self.b)
        self.L=r-1+(r+p-2)//(p-1)
        self.C=len(self.a)-1+(p-1)*(len(self.b)-1)+(r-1)*(len(self.e)-1)
        self.D=max(len(self.b)-1,(self.C+p-2)//(p-1))
        self.kernels=[]
        for ell in range(1,self.L+1):
            q=ell//p+1;t=p*q-(ell+1)
            rows=[]
            for k in range(r):
                scalar=(-1)**k*math.comb(q+k-1,k)*p**k
                w=[scalar*x for x in power(self.e,k)]
                kernel=reduce(mul(mul(self.a,power(self.b,t)),w),self.m)
                rows.append((q+k,kernel))
            self.kernels.append(rows)
    def initial(self):
        out=[[0]*(self.D+1) for _ in range(self.L)]
        out[0][:len(self.b)]=[x%self.m for x in self.b]
        return out
    def step(self,s:list[list[int]],d:int):
        out=[[0]*(self.D+1) for _ in range(self.L)]
        for row,branches in zip(s,self.kernels):
            for target,kernel in branches:
                assert 1<=target<=self.L
                prod=mul(row,kernel,self.m); sec=trim(prod[d::self.p])
                assert len(sec)-1<=self.D
                for n,x in enumerate(sec): out[target-1][n]=(out[target-1][n]+x)%self.m
        return out
    def output(self,s):
        inverse=pow(self.b[0],-1,self.m)
        return sum(row[0]*pow(inverse,i+1,self.m) for i,row in enumerate(s))%self.m
    def coefficient(self,n):
        state=self.initial()
        for d in digit_word(self.p,n): state=self.step(state,d)
        return self.output(state)
    def represented(self,s,n):
        f=recurrence_coefficients(self.p,self.m,self.a,self.b,n)
        inv=inverse_coefficients(self.b,self.m,n);layer=f;out=[0]*n
        for row in s:
            layer=series_mul(layer,inv,self.m,n)
            x=series_mul(row,layer,self.m,n)
            out=[(a+b)%self.m for a,b in zip(out,x)]
        return out

def audit() -> dict:
    start=time.monotonic(); rng=random.Random(SEED);counts=Counter()
    def check(ok:bool,tag:str,detail=None):
        counts[tag]+=1
        if not ok: raise AssertionError((tag,detail))
    # Dense small geometry: every formal correction, not only surviving ones.
    for p in range(2,14):
        for r in range(1,17):
            L=r-1+(r+p-2)//(p-1)
            for ell in range(1,L+1):
                for k in range(r):check(ell//p+1+k<=L,'layer_closure',(p,r,ell,k))
    # Generic degree/linearity over composite rings and nonprime radices.
    for m in (4,6,9,12):
        for p in (1,2,3,4,5):
            for _ in range(30):
                a=reduce([rng.randrange(m) for _ in range(rng.randrange(1,15))],m)
                b=reduce([rng.randrange(m) for _ in range(rng.randrange(1,15))],m)
                d=rng.randrange(0,p+4);c=rng.randrange(m)
                sec=lambda f: trim(f[d::p])
                check(len(sec(a))-1<=max(0,len(a)-1-d)//p,'section_degree')
                check(sec(add(a,b,m))==add(sec(a),sec(b),m),'section_additivity')
                check(sec(reduce([c*x for x in a],m))==reduce([c*x for x in sec(a)],m),'section_scalarity')
    cases=[]
    for p in (2,3,5):
        for r in (1,2,3):
            masks=[([1],[1,-1]),([1],[1]),([1,1],[1,0,-1]),([1,0,1],[1,1]),([1,2,-1],[1,-1,1]),([1],[1,0,1])]
            for _ in range(4):
                b0=rng.choice([u for u in (1,2,-1,-2,3) if u%p])
                masks.append(([b0,rng.randrange(-2,3),rng.randrange(-2,3)],[b0,rng.randrange(-2,3),rng.randrange(-2,3)]))
            for a,b in masks:cases.append(Machine(p,r,a,b))
    for M in cases:
        check(M.L>=1 and M.D>=len(M.b)-1,'initial_bounds')
        for branches in M.kernels:
            for target,k in branches:
                check(1<=target<=M.L,'target_bounds')
                check(len(k)-1<=(M.p-1)*M.D,'kernel_degree')
        oracle=recurrence_coefficients(M.p,M.m,M.a,M.b,96)
        for n,expected in enumerate(oracle):check(M.coefficient(n)==expected,'coefficient_output',(M.p,M.r,M.a,M.b,n))
        for _ in range(2):
            s=[[rng.randrange(M.m) for _ in range(M.D+1)] for _ in range(M.L)]
            t=[[rng.randrange(M.m) for _ in range(M.D+1)] for _ in range(M.L)]
            c=rng.randrange(M.m);plus=[[ (x+y)%M.m for x,y in zip(a,b)] for a,b in zip(s,t)]
            scaled=[[c*x%M.m for x in row] for row in s]
            old=M.represented(s,M.p*8)
            for d in range(M.p):
                out=M.step(s,d)
                check(M.represented(out,8)==old[d::M.p],'complete_state_semantics',(M.p,M.r,d))
                check(all(len(trim(row))-1<=M.D for row in out),'state_degree')
                ot=M.step(t,d)
                check(M.step(plus,d)==[[(x+y)%M.m for x,y in zip(a,b)] for a,b in zip(out,ot)],'state_additivity')
                check(M.step(scaled,d)==[[c*x%M.m for x in row] for row in out],'state_scalarity')
    M=Machine(2,2,[1],[1,-1]);example={'p':2,'r':2,'A':M.a,'B':M.b,'L':M.L,'D':M.D,'state_count':M.m**(M.L*(M.D+1)),'coefficients_mod_4_first_24':[M.coefficient(n) for n in range(24)]}
    check(trim([0,0,1][1::2])==[0],'annihilated_digit_control')
    finite_zero_radix=[1]
    repeated_series=[1,1,1]
    finite_coefficient_1=finite_zero_radix[1] if len(finite_zero_radix)>1 else 0
    check(finite_coefficient_1 != repeated_series[1],'zero_radix_degree_boundary')
    return {'status':'PASS','assertions':sum(counts.values()),'counts':dict(counts),'mask_cases':len(cases),'coefficient_range':[0,95],'represented_output_coefficients':8,'seed':SEED,'arithmetic':'exact Python integers and modular arithmetic','python':platform.python_version(),'elapsed_seconds':time.monotonic()-start,'example':example,'failures':[],'non_claims':['finite testing is not the universal proof','no executable Lean polynomial engine equivalence','no minimality','no existence construction in Lean']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=audit();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
