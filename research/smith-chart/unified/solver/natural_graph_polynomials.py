"""Exact natural graph polynomials by bounded-degree interpolation.
Author: Komorebi P. Degree/nonnegativity/stability are written graph theorems.
"""
from fractions import Fraction as F


def determinant(A):
    n=len(A);rows=[list(a) for a in A];out=F(1)
    for j in range(n):
        pivot=next((k for k in range(j,n) if rows[k][j]),None)
        if pivot is None:return F(0)
        if pivot!=j:rows[j],rows[pivot]=rows[pivot],rows[j];out=-out
        value=rows[j][j];out*=value
        for k in range(j+1,n):
            ratio=rows[k][j]/value
            for col in range(j+1,n):rows[k][col]-=ratio*rows[j][col]
    return out


def laplacian(edges,s):
    reached={1}
    while True:
        more=reached|{v for _,u,v,_ in edges if u in reached}|{u for _,u,v,_ in edges if v in reached}
        if more==reached:break
        reached=more
    if 0 not in reached:raise ValueError('Open port has no connected natural pair')
    kept=[e for e in edges if e[1] in reached and e[2] in reached and e[1]!=e[2]]
    nodes=sorted(reached-{0});index={v:j for j,v in enumerate(nodes)}
    A=[[F(0) for _ in nodes] for _ in nodes]
    for kind,u,v,value in kept:
        value=F(value)
        if value<=0:raise ValueError('Positive physical values required')
        y=1/value if kind=='R' else s*value if kind=='C' else 1/(s*value) if kind=='L' else None
        if y is None:raise ValueError('Ordinary R/L/C required')
        for a,b in ((u,v),(v,u)):
            if a in index:
                A[index[a]][index[a]]+=y
                if b in index:A[index[a]][index[b]]-=y
    port=index[1];minor=[[v for k,v in enumerate(row) if k!=port] for j,row in enumerate(A) if j!=port]
    return A,minor,sum(k=='L' for k,_,_,_ in kept),sum(k!='R' for k,_,_,_ in kept)


def interpolate(values):
    n=len(values);out=[F(0)]*n
    for j,value in enumerate(values,1):
        poly=[F(1)];den=F(1)
        for k in range(1,n+1):
            if k==j:continue
            next_poly=[F(0)]*(len(poly)+1)
            for e,a in enumerate(poly):next_poly[e]-=k*a;next_poly[e+1]+=a
            poly=next_poly;den*=j-k
        for e,a in enumerate(poly):out[e]+=value*a/den
    return tuple(out)


def pair(edges):
    _,_,_,q=laplacian(edges,F(1));rawP=[];rawQ=[]
    for j in range(1,q+2):
        s=F(j);A,B,nL,_=laplacian(edges,s)
        rawP.append(s**nL*determinant(B));rawQ.append(s**nL*determinant(A))
    P=interpolate(rawP);Q=interpolate(rawQ);scale=sum(P)+sum(Q)
    assert scale>0 and min(P+Q)>=0
    return {'P':tuple(a/scale for a in P),'Q':tuple(a/scale for a in Q),'scale':scale,'degree_cap':q}


def value(poly,s):
    out=0
    for a in reversed(poly):out=out*s+a
    return out
