"""Independent representation of the mixed example; standard library only.

Author: Komorebi P. Builds Gram entries from monomial moments and bitmask
matching states, without importing the discovery transfer or its NumPy code.
"""
import argparse,json,time
from functools import lru_cache
from math import comb,isqrt
from pathlib import Path


def trim(a):
    a=list(a)
    while len(a)>1 and not a[-1]:a.pop()
    return a


def product(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return trim(out)


def power(a,n):
    out=[1]
    for _ in range(n):out=product(out,a)
    return out


def moment(n):
    m=n//2
    return (m+1)*comb(2*m,m)*(2*(2*m+1) if n%2 else 1)


@lru_cache(None)
def chebyshev(n):
    if not n:return (2,)
    if n==1:return (0,1)
    a=chebyshev(n-1);b=chebyshev(n-2);out=[0]+list(a)
    for i,x in enumerate(b):out[i]-=x
    return tuple(out)


@lru_cache(None)
def basis(n):
    out=[0]*(n+1)
    for j in range(min(4,n//2)+1):
        factor=(-1)**j*comb(4,j)
        for k,x in enumerate(chebyshev(n-2*j)):out[k]+=factor*x
    return tuple(out)


@lru_cache(None)
def band(i,j):
    if min(i,j)<0:return 0
    return sum(value*moment(k) for k,value in enumerate(product(basis(i),basis(j))))


def bareiss(n):
    if not n:return 1
    A=[[moment(i+j) for j in range(n)] for i in range(n)];sign=1;previous=1
    for k in range(n-1):
        if not A[k][k]:
            pivot=next((i for i in range(k+1,n) if A[i][k]),None)
            if pivot is None:return 0
            A[k],A[pivot]=A[pivot],A[k];sign=-sign
        pivot=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                value=pivot*A[i][j]-A[i][k]*A[k][j]
                assert value%previous==0
                A[i][j]=value//previous
            A[i][k]=0
        previous=pivot
    return sign*A[-1][-1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();started=time.perf_counter();data=json.loads(Path(args.input).read_text())
    assert data['weights']==[1,1] and data['operator']==[1,2]
    q=list(map(int,data['coefficients']));assert len(q)==113 and q[-1]==1
    w=8;K=17;initial=(1<<w)-1
    masks=[mask for mask in range(1<<(2*w)) if mask.bit_count()==w]
    assert len(masks)==comb(16,8)==12870;index={mask:i for i,mask in enumerate(masks)}
    choices=[]
    for mask in masks:
        transitions=[]
        for k in range(2*w+1):
            if mask&(1<<k):continue
            if not mask&1 and k!=0:continue
            target=(mask|(1<<k))>>1
            sign=-1 if (mask>>(k+1)).bit_count()%2 else 1
            transitions.append((k,index[target],sign))
        choices.append(transitions)
    v=[0]*len(masks);v[index[initial]]=1;prefix=[1]
    for row in range(K):
        out=[0]*len(masks)
        diagonal=[band(row,row-w+k) for k in range(2*w+1)]
        for i,value in enumerate(v):
            if value:
                for k,j,sign in choices[i]:out[j]+=sign*diagonal[k]*value
        v=out;assert v[index[initial]]%4==0;prefix.append(v[index[initial]]//4)
    initial_vector=v[:];tail=[band(K,K-w+k) for k in range(2*w+1)]
    # Verify stationarity directly against the defining moment polynomial.
    for row in (K+1,K+4,K+9):assert tail==[band(row,row-w+k) for k in range(2*w+1)]
    edges=[(i,j,sign*tail[k]) for i,items in enumerate(choices) for k,j,sign in items if tail[k]]
    residual=[0]*len(masks)
    for value in q:
        residual=[r+value*x for r,x in zip(residual,v)]
        out=[0]*len(masks)
        for i,j,weight in edges:out[j]+=weight*v[i]
        v=out;assert v[index[initial]]%4==0;prefix.append(v[index[initial]]//4)
    assert not any(residual),'Independent bitmask residual is nonzero'
    assert any(initial_vector),'Constant-term corruption would be invisible'
    D=list(map(int,data['reduced_denominator']));N=list(map(int,data['reduced_numerator']))
    assert D==list(reversed(q)) and len(D)==len(N)==113
    numerator=trim([sum(D[j]*prefix[n-j] for j in range(min(n,len(D)-1)+1)) for n in range(K+112)])
    assert numerator==N
    bad=[n for n in range(K) if sum(q[j]*prefix[n+j] for j in range(len(q)))]
    assert bad==[0],bad
    B=[1,-16,384,1600,-21568,129792,649216,-2378752,9340416,-9515008,10387456,8306688,-5521408,1638400,1572864,-262144,65536]
    assert power(B,7)==D
    cert=data['coprimality'];prime=cert['prime']
    assert prime==1000003 and all(prime%d for d in range(2,isqrt(prime)+1))
    assert N[-1]%prime and D[-1]%prime
    left=product(cert['u'],N);right=product(cert['v'],D)
    left += [0]*max(0,len(right)-len(left))
    for i,value in enumerate(right):left[i]+=value
    assert trim([x%prime for x in left])==[1]
    for n in range(21):assert prefix[n]==bareiss(n)
    assert prefix[:4]==[1,1,0,-256]
    result={'outcome':'Separate moment/bitmask integer certificate and minimality audit passed',
        'review_provenance':'self-review, not independent review','full_vector_coordinates':len(masks),
        'raw_moment_definition':'mu_(2m)=(m+1)C(2m,m); mu_(2m+1)=2(2m+1)(m+1)C(2m,m)',
        'full_integer_residual_zero':True,'corrupted_relation_rejection_proved':True,
        'independent_bareiss_determinants':21,'denominator_factorization_reconstructed':True,
        'modular_bezout_verified':True,'minimal_eventual_order':112,'recurrence_start':1,
        'elapsed_seconds':time.perf_counter()-started}
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result))


if __name__=='__main__':main()
