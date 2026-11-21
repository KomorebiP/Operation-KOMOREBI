"""Exact standard-library replay of the sharp quadratic proof's algebraic leaves.

Sparse Laurent polynomials in n,z,w; no SymPy or discovery imports.
"""
import argparse,itertools,json,time
from fractions import Fraction as F
from math import comb,factorial
from pathlib import Path

ZERO={};ONE={(0,0,0):F(1)}
def mono(n=0,z=0,w=0,value=1):return {} if not value else {(n,z,w):F(value)}
def plus(*items):
    out={}
    for item in items:
        for key,value in item.items():out[key]=out.get(key,F(0))+value
    return {key:value for key,value in out.items() if value}
def scale(p,value):return {key:x*value for key,x in p.items() if x*value}
def minus(a,b):return plus(a,scale(b,-1))
def mul(a,b):
    out={}
    for i,x in a.items():
        for j,y in b.items():
            key=tuple(u+v for u,v in zip(i,j));out[key]=out.get(key,F(0))+x*y
    return {key:value for key,value in out.items() if value}
def power(p,k):
    out=ONE
    for _ in range(k):out=mul(out,p)
    return out
def diff(p,axis):
    out={}
    for key,value in p.items():
        if key[axis]:
            target=list(key);target[axis]-=1;out[tuple(target)]=value*key[axis]
    return out
def at_n(p,value):
    out={}
    for (i,j,k),x in p.items():out=plus(out,mono(0,j,k,x*value**i))
    return out
def divide_n(p,root):
    slices={}
    for (i,j,k),value in p.items():slices.setdefault((j,k),{})[i]=value
    out={}
    for (j,k),coeff in slices.items():
        degree=max(coeff);carry=coeff[degree]
        for i in range(degree-1,-1,-1):
            out=plus(out,mono(i,j,k,carry));carry=coeff.get(i,F(0))+root*carry
        assert not carry
    return out

n=mono(1);z=mono(z=1);w=mono(w=1)
def shift(k):return plus(n,scale(ONE,k))
def ell(k,i,j):
    return plus(mul(shift(k-3),shift(k-4)),
        scale(mul(mul(shift(k),shift(k-4)),mono(z=-2*i,w=-2*j)),-2),
        mul(mul(shift(k),shift(k-1)),mono(z=-4*i,w=-4*j)))
def coefficient_groups():
    D={};E={}
    for i,j in itertools.product((-1,1),repeat=2):
        D[i,j]=divide_n(minus(mul(mul(ell(0,i,0),mono(w=2*j)),ell(2,0,j)),
            mul(mul(mono(z=2*i),ell(2,i,0)),ell(0,0,j))),1)
        E[i,j]=divide_n(mul(mono(z=i,w=j),minus(
            mul(mul(ell(1,i,0),mono(w=2*j)),ell(3,0,j)),
            mul(mul(mono(z=2*i),ell(3,i,0)),ell(1,0,j)))),0)
    out={}
    for (i,j),d in D.items():
        for (k,l),e in E.items():out[i+k,j+l]=plus(out.get((i+k,j+l),{}),mul(d,e))
    assert len(out)==9 and all(max(key[0] for key in p)<=6 for p in out.values())
    return out

def poly_mul(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out
def poly_power(a,k):
    out=[1]
    for _ in range(k):out=poly_mul(out,a)
    return out
def determinant(matrix):
    if not matrix:return 1
    a=[row[:] for row in matrix];sign=previous=1;size=len(a)
    for k in range(size-1):
        if not a[k][k]:
            row=next((j for j in range(k+1,size) if a[j][k]),None)
            if row is None:return 0
            a[k],a[row]=a[row],a[k];sign=-sign
        pivot=a[k][k]
        for i in range(k+1,size):
            for j in range(k+1,size):
                value=pivot*a[i][j]-a[i][k]*a[k][j]
                if isinstance(value,int) and isinstance(previous,int):
                    assert value%previous==0;value//=previous
                else:value/=previous
                a[i][j]=value
            a[i][k]=0
        previous=pivot
    return sign*a[-1][-1]
def laurent_det(matrix):
    size=len(matrix);out={}
    for permutation in itertools.permutations(range(size)):
        inversions=sum(permutation[i]>permutation[j] for i in range(size) for j in range(i+1,size))
        term=ONE
        for i,j in enumerate(permutation):term=mul(term,matrix[i][j])
        out=plus(out,scale(term,(-1)**inversions))
    return out
def nu(k):
    if k%2:return F(0)
    m=k//2;return F(m*(m-1)*comb(2*m,m),12)
def inner(p,q):return sum((x*y*nu(i+j) for i,x in enumerate(p) for j,y in enumerate(q)),F(0))
def rodrigues(N):
    out=[F(1)];t=F(2*N-5,2)
    for k in range(N):
        derivative=[i*out[i] for i in range(1,len(out))]
        first=poly_mul([-4,0,1],derivative)
        second=[F(0)]+[2*(t-k)*x for x in out]
        out=[(first[i] if i<len(first) else 0)+(second[i] if i<len(second) else 0)
             for i in range(max(len(first),len(second)))]
    leading=F(factorial(2*N-5),factorial(N-5));assert out[-1]==leading
    return [x/leading for x in out]
def chebyshev(N):
    a,b=[F(2)],[F(0),F(1)]
    if not N:return a
    for _ in range(1,N):
        old=[0]+b;a+= [0]*(len(old)-len(a));a,b=b,[u-v for u,v in zip(old,a)]
    return b
def pn(N):
    d=(N-3)*(N-4);out=[F(0)]*(N+1)
    for size,factor in [(N,d),(N-2,-2*N*(N-4)),(N-4,N*(N-1))]:
        for i,value in enumerate(chebyshev(size)):out[i]+=value*F(factor,d)
    return out
def evaluate(p,x):
    out=F(0)
    for value in reversed(p):out=out*x+value
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    args=parser.parse_args();started=time.perf_counter();groups=coefficient_groups()
    r=plus(z,mono(z=-1));s=plus(w,mono(w=-1))
    b=scale(minus(minus(scale(ONE,8),power(r,2)),power(s,2)),F(1,2))
    c=scale(plus(mul(power(r,2),power(s,2)),scale(ONE,-16),scale(b,8)),F(1,12))
    factor=scale(mul(mul(r,s),power(minus(power(s,2),power(r,2)),2)),4608)
    def moment(k):
        if k%2:return {}
        m=k//2;return scale(plus(ONE,scale(b,m),scale(c,m*(m-1))),comb(2*m,m))
    for N in range(5):
        total={}
        for (i,j),p in groups.items():total=plus(total,mul(at_n(p,N),mono(z=i*N,w=j*N)))
        actual=scale(ONE,F(1,2)) if not N else laurent_det([[moment(i+j) for j in range(N)] for i in range(N)])
        assert scale(total,2**N)==mul(factor,actual),('early boundary',N)
    # ODE, with z**n factored out and all denominators cleared.
    L=ell(0,1,0);dx=minus(ONE,mono(z=-2));Lz=plus(diff(L,1),mul(mul(n,L),mono(z=-1)))
    Lzz=plus(diff(diff(L,1),1),scale(mul(mul(n,diff(L,1)),mono(z=-1)),2),
        mul(mul(mul(n,shift(-1)),L),mono(z=-2)))
    ode=minus(minus(mul(minus(power(r,2),scale(ONE,4)),minus(mul(Lzz,dx),mul(Lz,diff(dx,1)))),
        scale(mul(mul(r,Lz),power(dx,2)),3)),mul(mul(mul(n,shift(-4)),L),power(dx,3)))
    assert not ode
    def root_product(roots):
        values=[ONE]
        for root in roots:
            new=[{} for _ in range(len(values)+1)]
            for i,value in enumerate(values):new[i]=minus(new[i],mul(value,root));new[i+1]=plus(new[i+1],value)
            values=new
        return values
    p=plus(scale(ONE,-8),scale(b,8),scale(c,-24))
    q=plus(scale(ONE,24),scale(b,-32),scale(c,-96),scale(power(b,2),16))
    assert root_product([mono(z=i,w=j,value=2) for i in (-2,2) for j in (-2,2)])==[scale(ONE,16),scale(p,4),q,p,ONE]
    assert root_product([mono(z=i,value=2) for i in (-2,2)]+[mono(w=i,value=2) for i in (-2,2)])==[
        scale(ONE,16),plus(scale(b,16),scale(ONE,-32)),plus(scale(ONE,24),scale(b,-16),scale(c,48)),plus(scale(b,4),scale(ONE,-8)),ONE]
    for N in range(5,21):
        poly=rodrigues(N);assert poly==pn(N)
        for j in range(N):assert inner(poly,[0]*j+[1])==0
        assert inner(poly,poly)==F(2*N*(N-1),(N-3)*(N-4))
    assert determinant([[nu(i+j) for j in range(5)] for i in range(5)])==1
    transformed=0
    for z0,w0,a in [(F(2),F(3),F(1)),(F(3,2),F(5,2),F(-2))]:
        r0=z0+1/z0;s0=w0+1/w0;b0=a*(8-r0*r0-s0*s0)/2
        c0=(a*(r0*r0*s0*s0-16)+8*b0)/12
        def mu(k):
            if k%2:return F(0)
            m=k//2;return (a+b0*m+c0*m*(m-1))*comb(2*m,m)
        for N in range(5,13):
            H=F(2**(N-5)*(N-1)*(N-2)**2*(N-3)**2*(N-4),144)
            V=4*r0*s0*(s0*s0-r0*r0)**2
            transformed_value=a**N*H*determinant([[evaluate(pn(N+j),t) for j in range(4)] for t in [r0,-r0,s0,-s0]])/V
            assert transformed_value==determinant([[mu(i+j) for j in range(N)] for i in range(N)])
            transformed+=1
    cases=[(1,1,1),(2,-1,1),(0,0,1),(1,1,0),(2,0,0),(0,1,0),(0,0,0),(1,2,-1),(-1,2,1)]
    residues=0;direct_blocks=0;last=88
    for a,b,c in cases:
        def moment_integer(m):return (a+b*m+c*m*(m-1))*comb(2*m,m)
        blocks=[]
        for parity in (0,1):
            block=[determinant([[moment_integer(i+j+parity) for j in range(N)] for i in range(N)]) for N in range((last+1)//2+1)]
            blocks.append(block);direct_blocks+=len(block)
        W=[blocks[0][(N+1)//2]*blocks[1][N//2] for N in range(last+1)]
        p=-8*a+8*b-24*c;q=24*a*a-32*a*b-96*a*c+16*b*b
        g=[16*a**4,4*a*a*p,q,p,1]
        k=[16*a**4,16*a*a*(b-2*a),24*a*a-16*a*b+48*a*c,4*(b-2*a),1]
        gamma=poly_mul([-2*a,1],poly_mul(g,k));recurrence=poly_power(gamma,7)
        for N in range(1,last-63+1):
            assert sum(x*W[N+j] for j,x in enumerate(recurrence))==0,(a,b,c,N)
            residues+=1
        assert 2*sum(x*W[j] for j,x in enumerate(recurrence))==recurrence[0]
    report={'outcome':'Exact Laurent leaves and separate monomial determinant regressions passed',
        'review':'project self-review; independent implementation of the symbolic discovery, not independent review',
        'exponential_groups':len(groups),'maximum_coefficient_degree':6,'boundary_indices':[1,2,3,4],
        'formula_at_zero':'1/2','branch_ode':True,'quartic_root_factorizations':True,
        'rodrigues_and_orthogonality_indices':[5,20],'transformed_determinant_checks':transformed,
        'integer_parameter_cases':[list(row) for row in cases],'direct_monomial_blocks':direct_blocks,
        'recurrence_residues':residues,'recurrence_indices':[1,last-63],
        'all_zero_start_residues_match_exception':True,
        'scope':'Universal conclusion requires the written formal-moment, orthogonality, determinant and specialization proof. No all-parameter minimality or novelty claim.',
        'elapsed_seconds':time.perf_counter()-started}
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(report))

if __name__=='__main__':main()
