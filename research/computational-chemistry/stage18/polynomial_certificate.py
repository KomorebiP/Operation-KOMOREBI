"""Exact local polynomial response enclosures from saved endpoint disks."""
from fractions import Fraction as F
from functools import lru_cache
from math import comb
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'stage17'))
from planner import sharp_radius
from interval_certificate import sqrt_upper

SCALE=10**18
def ceil(x):
    x=F(x);return F(-(-x.numerator*SCALE//x.denominator),SCALE)
def floor(x):
    x=F(x);return F(x.numerator*SCALE//x.denominator,SCALE)
def add(a,b):return tuple((a[i] if i<len(a) else F(0))+(b[i] if i<len(b) else F(0)) for i in range(max(len(a),len(b))))
def scale(a,s):return tuple(x*s for x in a)
def multiply(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return tuple(out)
def value(a,t):
    result=F(0)
    for x in reversed(a):result=result*t+x
    return result
def bernstein(a,n=None):
    n=len(a)-1 if n is None else n
    if n<len(a)-1:raise ValueError('Degree too small')
    return tuple(sum(a[j]*F(comb(k,j),comb(n,j)) for j in range(min(k,len(a)-1)+1)) for k in range(n+1))
def split(b):
    levels=[tuple(b)]
    while len(levels[-1])>1:levels.append(tuple((a+c)/2 for a,c in zip(levels[-1],levels[-1][1:])))
    return tuple(row[0] for row in levels),tuple(row[-1] for row in reversed(levels))
def leaves(b,depth=2):
    if depth==0:return [tuple(b)]
    left,right=split(b);return leaves(left,depth-1)+leaves(right,depth-1)
def bounds(a,n=None):
    controls=[x for part in leaves(bernstein(a,n)) for x in part]
    return min(controls),max(controls)

@lru_cache(maxsize=4096)
def geometry(nodes):
    nodes=tuple(map(F,nodes));m=len(nodes)
    if m not in [2,3,4] or len(set(nodes))!=m or F(0) not in nodes or F(1) not in nodes or any(0<x<1 for x in nodes):raise ValueError('Stencil must contain both cell ends and no interior node')
    cardinal=[];absolute=[];P=(F(1),)
    for x in nodes:P=multiply(P,(-x,F(1)))
    for j,x in enumerate(nodes):
        L=(F(1),);denominator=F(1)
        for k,y in enumerate(nodes):
            if k!=j:L=multiply(L,(-y,F(1)));denominator*=x-y
        L=scale(L,1/denominator);cardinal.append(L);absolute.append(scale(L,1 if value(L,F(1,2))>0 else -1))
    Pabs=scale(P,1 if value(P,F(1,2))>0 else -1)
    return tuple(cardinal),tuple(absolute),Pabs

def polynomials(points,indices,cell_index,C):
    a=F(points[cell_index]['energy']);h=F(points[cell_index+1]['energy'])-a
    cardinal,absolute,P=geometry(tuple((F(points[j]['energy'])-a)/h for j in indices))
    real=(F(0),);imag=(F(0),);radius=scale(P,C)
    for L,A,j in zip(cardinal,absolute,indices):
        real=add(real,scale(L,F(points[j]['center']['real'])));imag=add(imag,scale(L,F(points[j]['center']['imaginary'])));radius=add(radius,scale(A,F(points[j]['radius'])))
    return real,imag,radius

def candidate(points,indices,i):
    m=len(indices)
    if m not in [2,3,4] or i not in indices or i+1 not in indices or len(set(indices))!=m:raise ValueError('Two to four distinct nodes including both cell endpoints required')
    eta=F(points[i]['eta']);h=F(points[i+1]['energy'])-F(points[i]['energy'])
    if eta<=0 or h<=0 or any(F(points[j]['eta'])!=eta for j in indices):raise ValueError('Positive equal broadening and ordered energies required')
    U=[-F(points[j]['center']['imaginary'])+F(points[j]['radius']) for j in indices]
    if min(U)<0 or any(F(points[j]['radius'])<0 for j in indices):raise ValueError('Invalid endpoint disk')
    smallest=min(U[j]*U[k] for j in range(m) for k in range(j+1,m))
    C=ceil((h/eta)**m*sqrt_upper(smallest));real,imag,radius=polynomials(points,indices,i,C)
    if m==2:R=sharp_radius(points[i]['radius'],points[i+1]['radius'],C)
    else:R=bounds(radius,m)[1]
    return dict(stencil=list(indices),coefficient=str(C),uniform_radius=str(ceil(R)))

def choices(points,i,m):
    if m not in [2,3,4]:raise ValueError('Unsupported interpolation degree')
    return [candidate(points,list(range(start,start+m)),i) for start in range(max(0,i+2-m),min(i,len(points)-m)+1)]
def best(points,i,m):return min(choices(points,i,m),key=lambda x:(F(x['uniform_radius']),x['stencil']))
def evaluate(points,record,i,t):
    real,imag,radius=polynomials(points,record['stencil'],i,F(record['coefficient']))
    return dict(center=dict(real=str(value(real,t)),imaginary=str(value(imag,t))),radius=str(value(radius,t)))
def gap(full_points,reduced_points,full,reduced,i):
    _,fi,fr=polynomials(full_points,full['stencil'],i,F(full['coefficient']));_,ri,rr=polynomials(reduced_points,reduced['stencil'],i,F(reduced['coefficient']))
    D=add(scale(fi,-1),ri);R=add(fr,rr);n=max(len(D),len(R))-1
    lower=floor(bounds(add(D,scale(R,-1)),n)[0]);upper=ceil(bounds(add(D,R),n)[1])
    return dict(signed_lower=str(lower),signed_upper=str(upper),absolute_lower=str(max(F(0),lower,-upper)))

def cubic_envelope(b):
    """Cubic Bezier controls and a uniform exact outward padding."""
    n=len(b)-1
    if n<3:
        # Degree elevation preserves the polynomial.
        for degree in range(n+1,4):b=(b[0],)+tuple(F(k,degree)*b[k-1]+F(degree-k,degree)*b[k] for k in range(1,degree))+(b[-1],)
        n=3
    controls=(b[0],b[0]+F(n,3)*(b[1]-b[0]),b[-1]-F(n,3)*(b[-1]-b[-2]),b[-1])
    if n==3:return controls,F(0)
    if n!=4:raise ValueError('Display supports degrees at most four')
    elevated=tuple(sum(controls[k]*F(comb(3,k)*comb(n-3,j-k),comb(n,j)) for k in range(max(0,j-(n-3)),min(3,j)+1)) for j in range(n+1))
    error=tuple(x-y for x,y in zip(b,elevated));assert error[0]==error[1]==error[-2]==error[-1]==0
    return controls,abs(error[2])*F(3,8)
