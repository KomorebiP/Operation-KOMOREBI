#!/usr/bin/env python3
"""Small exact laboratory for Frobenius-compressed packet multiplication.

Requires sympy.  It verifies:
  * factor-degree dimension sum for X^(2^m)-X over F2;
  * exact carryless multiplication through irreducible CRT packets;
  * zero-aware discrete-log multiplication inside each field packet;
  * Teichmuller lifting and Frobenius equivariance in GR(2^s,m);
  * exact chunked integer multiplication by Galois-ring evaluation/interpolation.

This is a correctness laboratory, not a fast implementation.
"""
import math, random, functools, collections
import sympy as sp

x=sp.symbols('x')

def poly_to_int(poly):
    p=sp.Poly(poly,x,modulus=2); v=0
    for (e,),c in p.terms():
        if int(c)&1:v|=1<<e
    return v

def find_irred(m):
    for lo in range(1,1<<m,2):
        expr=x**m+sum(((lo>>i)&1)*x**i for i in range(m))
        if sp.Poly(expr,x,modulus=2).is_irreducible:return (1<<m)|lo
    raise RuntimeError

def factors_q(m):
    q=1<<m
    _,fs=sp.factor_list(sp.Poly(x**q-x,x,modulus=2),modulus=2)
    return sorted([sp.Poly(P,x,modulus=2) for P,e in fs for _ in range(e)], key=lambda P:(P.degree(),poly_to_int(P)))

def pmod(a,mod,d):
    while a.bit_length()-1>=d:a^=mod<<((a.bit_length()-1)-d)
    return a

def gfmul(a,b,m,mod):
    r=0; top=1<<m
    while b:
        if b&1:r^=a
        b>>=1;a<<=1
        if a&top:a^=mod
    return r&(top-1)

def gfpow(a,e,m,mod):
    r=1
    while e:
        if e&1:r=gfmul(r,a,m,mod)
        a=gfmul(a,a,m,mod);e>>=1
    return r

def prime_divs(n):
    out=[];p=2
    while p*p<=n:
        if n%p==0:
            out.append(p)
            while n%p==0:n//=p
        p+=1
    if n>1:out.append(n)
    return out

@functools.lru_cache(None)
def dlog_data(mod,d):
    if d==1:return ({1:0},[1])
    order=(1<<d)-1
    g=next(g for g in range(2,1<<d) if all(gfpow(g,order//p,d,mod)!=1 for p in prime_divs(order)))
    L={};E=[];z=1
    for e in range(order):L[z]=e;E.append(z);z=gfmul(z,g,d,mod)
    return L,E

def encode(v,mod,d):
    if not v:return 0
    return dlog_data(mod,d)[0][v]+1

def decode(c,mod,d):
    if not c:return 0
    return dlog_data(mod,d)[1][c-1]

def cmul(a,b,d):
    if not a or not b:return 0
    M=(1<<d)-1
    return ((a-1+b-1)%M)+1

def build_analysis(m):
    q=1<<m; rows=[]; packets=[];off=0
    for P in factors_q(m):
        mod=poly_to_int(P);d=P.degree();cols=[];r=1
        for _ in range(q):cols.append(r);r=pmod(r<<1,mod,d)
        for j in range(d):
            row=sum((1<<k) for k,c in enumerate(cols) if (c>>j)&1);rows.append(row)
        packets.append((off,d,mod));off+=d
    assert off==q
    return rows,packets

def apply(rows,v):
    return sum((1<<i) for i,r in enumerate(rows) if (r&v).bit_count()&1)

def invert(rows,n):
    A=[rows[i]|(1<<(n+i)) for i in range(n)];mask=(1<<n)-1
    for c in range(n):
        p=next(i for i in range(c,n) if (A[i]>>c)&1);A[c],A[p]=A[p],A[c]
        for i in range(n):
            if i!=c and ((A[i]>>c)&1):A[i]^=A[c]
    assert all((A[i]&mask)==(1<<i) for i in range(n))
    return [a>>n for a in A]

def packet_code(poly,packets):
    out=0
    for off,d,mod in packets:out|=encode(pmod(poly,mod,d),mod,d)<<off
    return out

def packet_mul(a,b,packets):
    out=0
    for off,d,mod in packets:
        mask=(1<<d)-1;out|=cmul((a>>off)&mask,(b>>off)&mask,d)<<off
    return out

def code_to_residue(code,packets):
    out=0
    for off,d,mod in packets:
        mask=(1<<d)-1;out|=decode((code>>off)&mask,mod,d)<<off
    return out

def clmul(a,b):
    r=0
    while a:
        if a&1:r^=b
        a>>=1;b<<=1
    return r

# Galois-ring routines

def gradd(a,b,M):return tuple((u+v)%M for u,v in zip(a,b))
def grsub(a,b,M):return tuple((u-v)%M for u,v in zip(a,b))
def grmul(a,b,f,M):
    m=len(f);t=[0]*(2*m-1)
    for i,u in enumerate(a):
        for j,v in enumerate(b):t[i+j]=(t[i+j]+u*v)%M
    for k in range(2*m-2,m-1,-1):
        c=t[k]%M
        for i,fi in enumerate(f):t[k-m+i]=(t[k-m+i]-c*fi)%M
    return tuple(t[:m])
def grpow(a,e,f,M):
    r=(1,)+(0,)*(len(f)-1)
    while e:
        if e&1:r=grmul(r,a,f,M)
        a=grmul(a,a,f,M);e>>=1
    return r
def scalar(c,m,M):return (c%M,)+(0,)*(m-1)
def teich(a,m,fint,s):
    M=1<<s;f=[(fint>>i)&1 for i in range(m)];z=tuple((a>>i)&1 for i in range(m));q=1<<m
    for _ in range(8):
        zn=grpow(z,q,f,M)
        if zn==z:return z
        z=zn
    raise RuntimeError
def rinv(a,fint,m,s):
    M=1<<s;f=[(fint>>i)&1 for i in range(m)];ar=sum((v&1)<<i for i,v in enumerate(a));y=tuple((gfpow(ar,(1<<m)-2,m,fint)>>i)&1 for i in range(m));two=scalar(2,m,M)
    for _ in range(5):y=grmul(y,grsub(two,grmul(a,y,f,M),M),f,M)
    return y
def vinv(points,fint,m,s):
    q=len(points);M=1<<s;f=[(fint>>i)&1 for i in range(m)];one=scalar(1,m,M);zero=scalar(0,m,M);A=[]
    for i,t in enumerate(points):
        p=one;row=[]
        for _ in range(q):row.append(p);p=grmul(p,t,f,M)
        row += [one if i==j else zero for j in range(q)];A.append(row)
    for c in range(q):
        p=next(i for i in range(c,q) if any(v&1 for v in A[i][c]));A[c],A[p]=A[p],A[c];iv=rinv(A[c][c],fint,m,s);A[c]=[grmul(v,iv,f,M) for v in A[c]]
        for i in range(q):
            if i==c:continue
            h=A[i][c]
            if any(h):A[i]=[grsub(A[i][j],grmul(h,A[c][j],f,M),M) for j in range(2*q)]
    return [r[q:] for r in A]
def evalbase(coeff,t,fint,m,s):
    M=1<<s;f=[(fint>>i)&1 for i in range(m)];r=scalar(0,m,M)
    for c in reversed(coeff):r=gradd(grmul(r,t,f,M),scalar(c,m,M),M)
    return r
def matvec(A,v,fint,m,s):
    M=1<<s;f=[(fint>>i)&1 for i in range(m)];out=[]
    for row in A:
        z=scalar(0,m,M)
        for a,b in zip(row,v):z=gradd(z,grmul(a,b,f,M),M)
        out.append(z)
    return out

def chunkmul(a,b,w,N):
    m=math.ceil(math.log2(2*N-1));q=1<<m;s=2*w+math.ceil(math.log2(N))+1;M=1<<s;fint=find_irred(m);f=[(fint>>i)&1 for i in range(m)];pts=[teich(t,m,fint,s) for t in range(q)];IV=vinv(pts,fint,m,s);mask=(1<<w)-1
    A=[(a>>(w*i))&mask for i in range(N)]+[0]*(q-N);B=[(b>>(w*i))&mask for i in range(N)]+[0]*(q-N)
    VA=[evalbase(A,t,fint,m,s) for t in pts];VB=[evalbase(B,t,fint,m,s) for t in pts];VC=[grmul(u,v,f,M) for u,v in zip(VA,VB)];C=matvec(IV,VC,fint,m,s)
    coeff=[]
    for k in range(2*N-1):
        assert all(z==0 for z in C[k][1:]);coeff.append(C[k][0])
    carry=0;out=0
    for k,c in enumerate(coeff):
        z=c+carry;out|=(z&mask)<<(w*k);carry=z>>w
    k=len(coeff)
    while carry:out|=(carry&mask)<<(w*k);carry>>=w;k+=1
    return out

def main():
    rng=random.Random(20260811)
    for m in range(1,7):
        q=1<<m;rows,p=build_analysis(m);iv=invert(rows,q)
        assert sum(d for _,d,_ in p)==q
        for _ in range(100):
            n=(q+1)//2;a=rng.randrange(1<<n);b=rng.randrange(1<<n);ca=packet_code(a,p);cb=packet_code(b,p);cc=packet_mul(ca,cb,p);c=apply(iv,code_to_residue(cc,p));assert c==clmul(a,b)
        print('PASS F2 nonlinear packets',m,q)
    for N in (2,3,4):
        for w in (1,2,3):
            for _ in range(15):
                a=rng.randrange(1<<(N*w));b=rng.randrange(1<<(N*w));assert chunkmul(a,b,w,N)==a*b
            print('PASS exact integer GR packets',N,w)
if __name__=='__main__':main()
