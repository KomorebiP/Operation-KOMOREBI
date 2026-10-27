#!/usr/bin/env python3
"""Exact finite-field corroboration. No NumPy floating arithmetic and no sampling.
Compare actual localization images with the proved pivot/primary criteria.
Also enumerate actual dual-number matrix powers and kernel conjugations.
"""
from __future__ import annotations
import itertools, json, platform, hashlib, time
from pathlib import Path

def eye(n): return [[int(i == j) for j in range(n)] for i in range(n)]
def zero(n): return [[0]*n for _ in range(n)]
def add(A,B,p): return [[(a+b)%p for a,b in zip(r,s)] for r,s in zip(A,B)]
def neg(A,p): return [[-a%p for a in r] for r in A]
def sub(A,B,p): return add(A,neg(B,p),p)
def scale(c,A,p): return [[c*a%p for a in r] for r in A]
def mul(A,B,p): return [[sum(A[i][j]*B[j][h] for j in range(len(B)))%p for h in range(len(B[0]))] for i in range(len(A))]
def power(A,n,p):
    R=eye(len(A))
    while n:
        if n&1:R=mul(R,A,p)
        A=mul(A,A,p);n//=2
    return R
def norm(A,d,p):
    R=zero(len(A));P=eye(len(A))
    for _ in range(d):R=add(R,P,p);P=mul(P,A,p)
    return R
def rref(A,p):
    A=[r[:] for r in A];row=0;piv=[]
    if not A:return A,piv
    for col in range(len(A[0])):
        k=next((k for k in range(row,len(A)) if A[k][col]%p),None)
        if k is None:continue
        A[row],A[k]=A[k],A[row];inv=pow(A[row][col]%p,-1,p)
        A[row]=[(v*inv)%p for v in A[row]]
        for k in range(len(A)):
            if k!=row:
                c=A[k][col];A[k]=[(x-c*y)%p for x,y in zip(A[k],A[row])]
        piv.append(col);row+=1
        if row==len(A):break
    return A,piv
def rank(A,p):return len(rref(A,p)[1])
def inverse(A,p):
    n=len(A);R,piv=rref([A[i]+eye(n)[i] for i in range(n)],p)
    assert piv[:n]==list(range(n)), 'singular normalizer'
    return [r[n:] for r in R]
def transpose(A):return list(map(list,zip(*A)))
def nullspace(A,p):
    R,piv=rref(A,p);n=len(A[0]);ans=[]
    for j in range(n):
        if j not in piv:
            v=[0]*n;v[j]=1
            for i,c in enumerate(piv):v[c]=-R[i][j]%p
            ans.append(v)
    return ans
def annihilator(A,p):return nullspace(transpose(A),p)
def mv(A,v,p):return [sum(x*y for x,y in zip(r,v))%p for r in A]
def flatten(A):return tuple(v for r in A for v in r)
def unflatten(v,n):return [list(v[i*n:(i+1)*n]) for i in range(n)]
def ppart(d,p):
    assert d>0
    a=0
    while d%p==0:d//=p;a+=1
    return d,a

def localization_matrix(T,degrees,p):
    n=len(T);r=len(degrees);out=[[0]*(n*(r+1)) for _ in range(n*r)]
    for i,d in enumerate(degrees):
        S=norm(T,d,p);G=sub(eye(n),power(T,d,p),p)
        for j in range(n):
            out[i*n+j][:n]=S[j]
            out[i*n+j][(i+1)*n:(i+2)*n]=G[j]
    return out

def pivot_constraints(N,degrees,normalizers,p):
    n=len(N);r=len(degrees);parts=[ppart(d,p)[1] for d in degrees]
    j=min(range(r),key=lambda i:parts[i]);s=[p**a for a in parts]
    inv=[inverse(U,p) for U in normalizers];constraints=[]
    # e_j normalized must belong to im N^(s_j-1).
    for row in annihilator(power(N,s[j]-1,p),p):
        z=[0]*(n*r);z[j*n:(j+1)*n]=mv(transpose(inv[j]),row,p);constraints.append(z)
    for i in range(r):
        transfer=mul(power(N,s[i]-s[j],p),inv[j],p)
        for row in annihilator(power(N,s[i],p),p):
            z=[0]*(n*r)
            qi=mv(transpose(inv[i]),row,p);qj=mv(transpose(transfer),row,p)
            for h in range(n):
                z[i*n+h]=(z[i*n+h]+qi[h])%p
                z[j*n+h]=(z[j*n+h]-qj[h])%p
            constraints.append(z)
    return constraints

def check_equal_kernel_image(L,C,p):
    if C:
        assert not any(any(r) for r in mul(C,L,p)), 'predicted constraints miss actual image'
        c=rank(C,p)
    else:c=0
    assert rank(L,p)+c==len(L), 'predicted criterion has incorrect dimension'

def linear_sweep():
    counts={'prime_power_arbitrary_operator_cases':0,'mixed_primary_cases':0}
    for p in (2,3):
        # All 2x2 operators, including noninvertible ones: operator theorem allows them.
        for vals in itertools.product(range(p),repeat=4):
            T=unflatten(vals,2);N=sub(T,eye(2),p)
            for degrees in ((1,p),(p,p*p),(p*p,1,p),(p,p)):
                L=localization_matrix(T,degrees,p)
                C=pivot_constraints(N,degrees,[eye(2)]*len(degrees),p)
                check_equal_kernel_image(L,C,p);counts['prime_power_arbitrary_operator_cases']+=1
    for p in (2,3,5):
        for n in range(1,6):
            N=[[int(j==i+1) for j in range(n)] for i in range(n)]
            for lam in range(1,p):
                T=add(scale(lam,eye(n),p),N,p)
                families=((1,p),(p,p*p),(2,3),(p,2*p),(2,2*p,3),(p*p,p,1))
                for degrees in families:
                    L=localization_matrix(T,degrees,p)
                    if lam==1:
                        U=[power(norm(T,ppart(d,p)[0],p),p**ppart(d,p)[1],p) for d in degrees]
                        C=pivot_constraints(N,degrees,U,p)
                    else:
                        C=[]
                        for i,d in enumerate(degrees):
                            m,a=ppart(d,p);s=p**a;e=s if pow(lam,m,p)==1 else 0
                            for row in annihilator(power(N,e,p),p):
                                z=[0]*(n*len(degrees));z[i*n:(i+1)*n]=row;C.append(z)
                    check_equal_kernel_image(L,C,p);counts['mixed_primary_cases']+=1
    return counts

def dmul(X,Y,p):
    A,a=X;B,b=Y
    return mul(A,B,p),add(mul(A,b,p),mul(a,B,p),p)
def dpow(X,d,p):
    ans=(eye(len(X[0])),zero(len(X[0])))
    for _ in range(d):ans=dmul(ans,X,p)
    return ans

def genuine_matrix_test():
    p=3;n=2;F=[[1,1],[0,1]];vecs=list(itertools.product(range(p),repeat=4))
    # independent actual matrix conjugation action, column by column
    Finv=inverse(F,p);columns=[]
    for j in range(4):
        v=[0]*4;v[j]=1
        columns.append(flatten(mul(mul(F,unflatten(v,2),p),Finv,p)))
    T=transpose(columns);degrees=(1,3);predicted=set()
    for e0 in vecs:
        e1=mv(norm(T,3,p),e0,p);predicted.add(tuple(e0)+tuple(e1))
    actual=set();power_checks=0;conjugacy_checks=0
    for Xv in vecs:
        lift=(F,unflatten(Xv,2))
        options=[]
        for d in degrees:
            P=dpow(lift,d,p);power_checks+=1
            baseinv=inverse(power(F,d,p),p);local=set()
            for zv in vecs:
                z=unflatten(zv,2);U=(eye(2),z);Uinv=(eye(2),neg(z,p))
                Q=dmul(dmul(U,P,p),Uinv,p);conjugacy_checks+=1
                local.add(flatten(mul(Q[1],baseinv,p)))
            options.append(local)
        actual.update(a+b for a in options[0] for b in options[1])
    assert actual==predicted
    upper=(0,1,0,0);lower=(0,0,1,0);z=(0,0,0,0)
    assert z+upper not in actual and lower+upper in actual
    individual_sizes=[len({v[:4] for v in actual}),len({v[4:] for v in actual})]
    assert individual_sizes==[81,3] and len(actual)==81
    return {'field':3,'matrix_rank':2,'degrees':degrees,'actual_frobenius_lifts_enumerated':len(vecs),
       'matrix_power_evaluations':power_checks,'kernel_conjugation_evaluations':conjugacy_checks,
       'simultaneous_mismatch_image_size':len(actual),'individual_image_sizes':individual_sizes,
       'separately_attainable_pair_count':243,'compatible_example':list(lower+upper),
       'incompatible_example':list(z+upper)}

if __name__=='__main__':
    start=time.time();counts=linear_sweep();actual=genuine_matrix_test()
    result={'status':'PASS','scope':'exact finite tests only; general claims proved separately in Lean',
      'method':'integer modular Gaussian elimination; finite-subspace containment plus equal dimension; independent actual dual-number matrix powers and conjugations',
      'linear_counts':counts,'matrix_example':actual,'python':platform.python_version(),
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seconds':time.time()-start}
    out=Path(__file__).with_name('EXACT_CHECKS.json');out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
