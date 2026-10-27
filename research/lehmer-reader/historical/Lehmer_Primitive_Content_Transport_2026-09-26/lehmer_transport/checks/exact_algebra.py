"""Small exact rational linear algebra and sparse polynomial ring in s2..s5."""
from fractions import Fraction as F
from math import gcd, lcm, prod


def rref(A):
    a=[[F(x) for x in row] for row in A]
    if not a:return a,[]
    r=0;piv=[]
    for j in range(len(a[0])):
        h=next((h for h in range(r,len(a)) if a[h][j]),None)
        if h is None:continue
        a[r],a[h]=a[h],a[r]
        v=a[r][j];a[r]=[x/v for x in a[r]]
        for h in range(len(a)):
            if h==r or not a[h][j]:continue
            v=a[h][j];a[h]=[x-v*y for x,y in zip(a[h],a[r])]
        piv.append(j);r+=1
        if r==len(a):break
    return a,piv


def rank(A):return len(rref(A)[1])


def nullspace(A):
    a,p=rref(A)
    if not a:return []
    n=len(a[0]);out=[]
    for j in range(n):
        if j in p:continue
        v=[F(0)]*n;v[j]=1
        for i,c in enumerate(p):v[c]=-a[i][j]
        out.append(v)
    return out


def solve(A,b):
    n=len(A[0]);rr,p=rref([list(row)+[y] for row,y in zip(A,b)])
    if n in p:raise ValueError('inconsistent exact linear system')
    x=[F(0)]*n
    for i,j in enumerate(p):x[j]=rr[i][-1]
    assert matvec(A,x)==list(b)
    return x


def matvec(A,x):return [sum(a*b for a,b in zip(row,x)) for row in A]
def transpose(A):return list(map(list,zip(*A)))
def matmul(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]


ZERO=(0,0,0,0)
def const(c):return {ZERO:F(c)} if c else {}
def var(i):return {tuple(int(j==i) for j in range(4)):F(1)}
def add(*polys):
    z={}
    for p in polys:
        for e,c in p.items():z[e]=z.get(e,0)+c
    return {e:c for e,c in z.items() if c}
def scale(p,a):return {e:c*a for e,c in p.items() if c*a}
def mul(a,b):
    z={}
    for e,c in a.items():
        for f,d in b.items():
            ef=tuple(x+y for x,y in zip(e,f));z[ef]=z.get(ef,0)+c*d
    return {e:c for e,c in z.items() if c}
def deriv(p,i):
    z={}
    for e,c in p.items():
        if e[i]:
            f=list(e);f[i]-=1;z[tuple(f)]=c*e[i]
    return z
def evaluate(p,values):return sum(c*prod(x**a for x,a in zip(values,e)) for e,c in p.items())
def exponents(d):
    for a in range(d//2+1):
        for b in range(d//3+1):
            for c in range(d//4+1):
                rem=d-2*a-3*b-4*c
                if rem>=0 and rem%5==0:yield (a,b,c,rem//5)
def integer_primitive(p):
    den=lcm(*(F(c).denominator for c in p.values()))
    ints={e:int(c*den) for e,c in p.items() if c}
    g=gcd(*ints.values())
    first=max(ints)
    if ints[first]<0:g=-g
    return {e:c//g for e,c in ints.items()}


S={0:const(5),1:{},2:var(0),3:var(1),4:var(2),5:var(3)}
E={1:{},2:scale(S[2],F(-1,2)),3:scale(S[3],F(1,3)),
   4:add(scale(mul(S[2],S[2]),F(1,8)),scale(S[4],F(-1,4))),
   5:add(scale(S[5],F(1,5)),scale(mul(S[2],S[3]),F(-1,6)))}
for k in range(6,9):S[k]=add(*(scale(mul(E[j],S[k-j]),(-1)**(j-1)) for j in range(1,6)))
DRIFT={m:add(scale(add(*(mul(S[a],S[m-2-a]) for a in range(m-1))),m),
             scale(S[m-2],F(-m*(m-1),5))) for m in range(2,6)}
METRIC={(m,n):scale(add(S[m+n-2],scale(mul(S[m-1],S[n-1]),F(-1,5))),m*n)
        for m in range(2,6) for n in range(2,6)}


def harmonic_operator(p):
    terms=[]
    for i,m in enumerate(range(2,6)):
        dp=deriv(p,i);terms.append(mul(dp,DRIFT[m]))
        for j,n in enumerate(range(2,6)):terms.append(mul(deriv(dp,j),METRIC[m,n]))
    return add(*terms)


def build_kernel(d,shell,weight):
    es=list(exponents(d));LP=[harmonic_operator({e:F(1)}) for e in es]
    rows=sorted(set(e for p in LP for e in p))
    A=[[p.get(e,F(0)) for p in LP] for e in rows]
    for n in range(1,(12+d)//12+1):
        pts=[(weight(v),[sum(x**k for x in v) for k in range(2,6)]) for v in shell(n)]
        A.append([sum(w*prod(x**a for x,a in zip(z,e)) for w,z in pts) for e in es])
    out=[]
    for v in nullspace(A):
        p=integer_primitive({e:c for e,c in zip(es,v) if c})
        assert not harmonic_operator(p)
        out.append({'degree':d,'terms':[[list(e),c] for e,c in sorted(p.items(),reverse=True)]})
    return out
