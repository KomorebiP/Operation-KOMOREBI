"""Exact finite fixtures for the refined Komorebi Operator Compendium.

Run: python Komorebi_Operator_Refined_Checks.py --json results.json
Requires only Python's standard library and the adjacent preserved
Komorebi_Operator_Audit_Checks.py. This is an independent mathematical
fixture suite, not a run of komorebi-math or Lean.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from collections import Counter
from math import factorial, comb
import argparse
import contextlib
import io
import json
import platform
import sys
import hashlib
if __package__:
    from . import Komorebi_Operator_Audit_Checks as prior
else:
    import Komorebi_Operator_Audit_Checks as prior

RECORDS: list[dict] = []

def rational(x):
    if isinstance(x, bool) or not isinstance(x, (int, F)):
        raise TypeError('exact fixture input must be an integer or Fraction')
    return F(x)

def mat(rows):
    a=tuple(tuple(rational(x) for x in row) for row in rows)
    if not a or not a[0] or any(len(row)!=len(a[0]) for row in a):
        raise ValueError('nonempty rectangular matrix required')
    return a

def shape(a): return (len(a),len(a[0]))
def eye(n):
    if n<1: raise ValueError('positive dimension required')
    return mat([[int(i==j) for j in range(n)] for i in range(n)])
def zero(m,n): return mat([[0]*n for _ in range(m)])
def tr(a): return mat(zip(*a))
def scale(a,c): return mat([[rational(c)*v for v in row] for row in a])
def add(a,b):
    if shape(a)!=shape(b): raise ValueError('matrix shape mismatch')
    return mat([[x+y for x,y in zip(ra,rb)] for ra,rb in zip(a,b)])
def sub(a,b): return add(a,scale(b,-1))
def mm(a,b):
    if len(a[0])!=len(b): raise ValueError('matrix product dimension mismatch')
    return mat([[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))])
def mv(a,x):
    x=tuple(map(rational,x))
    if len(a[0])!=len(x): raise ValueError('matrix vector dimension mismatch')
    return tuple(sum(v*w for v,w in zip(row,x)) for row in a)
def inv(a): return prior.inv(mat(a))
def trace(a):
    if len(a)!=len(a[0]): raise ValueError('trace requires square matrix')
    return sum(a[i][i] for i in range(len(a)))
def power(a,k):
    z=eye(len(a))
    for _ in range(k): z=mm(z,a)
    return z

def record(key,name,ok,ids,kind='identity',cases=1):
    if key in {r['id'] for r in RECORDS}: raise ValueError('duplicate check ID')
    if not ok: raise AssertionError(key+': '+name)
    RECORDS.append({'id':key,'name':name,'status':'PASS','kind':kind,
                    'operator_ids':[f'OP-{i:03d}' for i in ids],'cases':cases})
    print('PASS',key,name)

def rejects(fn, exc=ValueError):
    try: fn()
    except exc: return True
    return False

ps=prior.ps; padd=prior.padd; pmul=prior.pmul; pscale=prior.pscale
peval=prior.peval; deriv=prior.deriv; pcompose=prior.pcompose

def shift(p,t): return pcompose(p,ps([t,1]))
def delta(p): return padd(shift(p,1),pscale(p,-1))
def raising(p): return pmul(ps([0,1]),shift(p,-1))
def degree_op(p): return pmul(ps([0,1]),padd(p,pscale(shift(p,-1),-1)))
def fall(k):
    p=ps([1])
    for j in range(k):p=pmul(p,ps([-j,1]))
    return p

def phi(a):
    out=ps([0])
    for k,c in enumerate(a):out=padd(out,pscale(fall(k),c))
    return out

def unphi(p):
    work=list(ps(p)); out=[F(0)]*len(work)
    for k in range(len(work)-1,-1,-1):
        out[k]=work[k]; fk=fall(k)
        for j,c in enumerate(fk):work[j]-=out[k]*c
    if any(work):raise AssertionError('triangular inverse residual')
    return ps(out)

def qp(p,m,r):
    a=unphi(p)
    return phi([v if k%m==r else 0 for k,v in enumerate(a)])
def star(p,q):return phi(pmul(unphi(p),unphi(q)))
def trunc(p,n):return ps(p[:n+1])

def pcompose_trunc(f,g,n):
    ans=ps([0]);pw=ps([1])
    for c in f:
        ans=padd(ans,pscale(pw,c));pw=pmul(pw,g,n)
    return trunc(ans,n)

def revert(f,n):
    f=ps(f)
    if f[0]!=0 or len(f)<2 or f[1]==0:
        raise ValueError('composition inverse requires zero constant and a unit linear term')
    g=[F(0)]*(n+1)
    for k in range(1,n+1):
        cur=pcompose_trunc(f,ps(g),k)
        ck=cur[k] if len(cur)>k else F(0)
        g[k]=((1 if k==1 else 0)-ck)/f[1]
    return ps(g)

def pexp(u,n):
    if u[0]!=0:raise ValueError('zero-constant input required')
    ans=ps([1]);pw=ps([1])
    for k in range(1,n+1):
        pw=pmul(pw,u,n);ans=padd(ans,pscale(pw,F(1,factorial(k))))
    return trunc(ans,n)

def plog(f,n):
    if f[0]!=1:raise ValueError('normalized unit required')
    u=padd(f,ps([-1])); ans=ps([0]);pw=ps([1])
    for k in range(1,n+1):
        pw=pmul(pw,u,n);ans=padd(ans,pscale(pw,F((-1)**(k+1),k)))
    return trunc(ans,n)

def normalized_product(a,b,gamma):
    out=[]
    for n in range(len(a)+len(b)-1):
        out.append(sum(gamma[n]*a[k]*b[n-k]/(gamma[k]*gamma[n-k])
                       for k in range(len(a)) if 0<=n-k<len(b)))
    return ps(out)

def synth(initial,defects,c):
    if len(initial)!=len(c) or not c:raise ValueError('initial state dimension mismatch')
    out=list(map(rational,initial));d=len(c)
    for i,r in enumerate(defects):out.append(sum(c[j]*out[i+j] for j in range(d))+r)
    return tuple(out)
def defects(seq,c):
    d=len(c);return tuple(seq[i+d]-sum(c[j]*seq[i+j] for j in range(d)) for i in range(len(seq)-d))

def obs(A,C,m):
    return mat([row for k in range(m) for row in mm(C,power(A,k))])
def control(A,B,inputs):
    out=tuple(F(0) for _ in A)
    for u in inputs:out=tuple(x+y for x,y in zip(mv(A,out),mv(B,u)))
    return out

def rank(a):
    work=[list(row) for row in a];r=0
    for k in range(len(work[0])):
        j=next((i for i in range(r,len(work)) if work[i][k]),None)
        if j is None:continue
        work[r],work[j]=work[j],work[r];v=work[r][k];work[r]=[x/v for x in work[r]]
        for i in range(len(work)):
            if i!=r:
                v=work[i][k];work[i]=[x-v*y for x,y in zip(work[i],work[r])]
        r+=1
        if r==len(work):break
    return r

def recover(A,y):
    if rank(A)!=len(A[0]):raise ValueError('rank deficient observations')
    L=mm(inv(mm(tr(A),A)),tr(A));x=mv(L,y)
    if mv(A,x)!=tuple(y):raise ValueError('observations not in the stated image')
    return x

def adj(A,Qx,Qy):return mm(mm(inv(Qx),tr(A)),Qy)
def pull_metric(A,Q):return mm(mm(tr(A),Q),A)
def metric_prop(A,Q):return pull_metric(inv(A),Q)
def metric_def(A,Qx,Qy):return sub(pull_metric(A,Qy),Qx)
def hs(H,Q):
    e=sub(H,eye(len(H)))
    return trace(mm(mm(mm(inv(Q),tr(e)),Q),e))
def det2(A):return A[0][0]*A[1][1]-A[0][1]*A[1][0]

def atomic(p,nodes,weights):return sum(w*peval(p,x) for x,w in zip(nodes,weights))
def moment(k,a,b,rho=F(1)):return rho*(b**(k+1)-a**(k+1))/F(k+1)
def integral(p,a,b,rho=F(1)):return sum(c*moment(k,a,b,rho) for k,c in enumerate(p))
def moments(nodes,weights,d):return tuple(sum(w*x**k for x,w in zip(nodes,weights)) for k in range(d+1))

def filter_iir(x,b,a,pre_y=None,pre_x=None):
    if not a or a[0]==0:raise ValueError('nonzero leading denominator coefficient required')
    py=list(pre_y or []);px=list(pre_x or []);y=[]
    def xv(i):return x[i] if i>=0 else (px[i] if -i<=len(px) else F(0))
    def yv(i):return y[i] if i>=0 else (py[i] if -i<=len(py) else F(0))
    for n in range(len(x)):
        y.append((sum(b[k]*xv(n-k) for k in range(len(b)))-sum(a[k]*yv(n-k) for k in range(1,len(a))))/a[0])
    return tuple(y)

def run_extensions():
    # Coefficient gauge and typed transport.
    A=mat([[1,0],[0,1],[1,1]]);S=mat([[1,0,0],[0,1,0]])
    P=mm(A,S);G=sub(eye(3),P)
    record('R01','gauge complement is idempotent and synthesizes to zero',mm(G,G)==G and mm(S,G)==zero(2,3),[170,18,16,17])
    c=(F(2),F(-3),F(8))
    record('R02','coefficient gauge is generally oblique',G!=tr(G) and tuple(x+y for x,y in zip(mv(P,c),mv(G,c)))==c,[170,18],kind='counterexample')
    T=mat([[1,2],[-1,3],[2,0]]);Cx=mat([[1,1],[0,1]]);Cy=mat([[1,0,1],[0,2,0],[0,0,1]])
    Tn=mm(mm(Cy,T),inv(Cx));x=(F(2),F(-1))
    record('R03','two-endpoint transport preserves a rectangular action',mv(Tn,mv(Cx,x))==mv(Cy,mv(T,x)),[171,8,40])
    U=mat([[1,2,0],[-1,0,1]]);Cz=mat([[2,0],[0,1]]);Un=mm(mm(Cz,U),inv(Cy))
    record('R04','rectangular transports compose with the same middle chart',mm(Un,Tn)==mm(mm(Cz,mm(U,T)),inv(Cx)),[171,3,12])
    ell=mat([[1,-2,3]])
    record('R05','covector pullback needs no invertible map',mv(mm(ell,T),x)==mv(ell,mv(T,x)),[172,55,171])
    record('R06','contragredient coordinate storage preserves pairings',mm(mm(ell,inv(Cy)),Cy)==ell,[172,24])
    # Falling factorials and characteristic boundaries.
    polys=[ps([1,2,-1,3]),ps([0,0,0,0,1]),ps([F(2,3),F(-1,5),0,1])]
    record('R07','falling-factorial transport has an exact triangular inverse',all(unphi(phi(p))==p and phi(unphi(p))==p for p in polys),[41,42,43],cases=len(polys))
    tests=[]
    for p in polys:
        for m in (2,3,5):
            total=ps([0])
            for r in range(m):
                q=qp(p,m,r);total=padd(total,q)
                tests.append(qp(q,m,r)==q)
                tests.extend(qp(q,m,s)==ps([0]) for s in range(m) if s!=r)
            tests.append(total==p)
    record('R08','transported coefficient projectors are complete and orthogonal',all(tests),[173,9,25],cases=len(tests))
    p=ps([0,0,0,0,0,1]);vals=tuple(peval(qp(p,3,r),F(4)) for r in range(3))
    record('R09','degree labels cannot be replaced by ordinary-power labels',vals==(600,244,180) and vals!=(0,0,1024),[173,25,41],kind='counterexample')
    tests=[delta(qp(p,m,r))==qp(delta(p),m,(r-1)%m) for p in polys for m in (2,3) for r in range(m)]
    record('R10','forward differences shift the transported residue address',all(tests),[173,47,31],cases=len(tests))
    f,g,h=polys
    record('R11','transported product is associative and unital',star(star(f,g),h)==star(f,star(g,h)) and star(f,ps([1]))==f,[174])
    record('R12','finite differences obey Leibniz for the transported product',delta(star(f,g))==padd(star(delta(f),g),star(f,delta(g))),[174,47])
    xx=ps([0,1])
    record('R13','ordinary multiplication has a shifted rather than differential Leibniz rule',delta(pmul(xx,xx))!=padd(pmul(delta(xx),xx),pmul(xx,delta(xx))),[174,47],kind='counterexample')
    record('R14','raising advances the falling-factorial basis',all(raising(fall(k))==fall(k+1) for k in range(9)),[175,59],cases=9)
    record('R15','raising and difference have the polynomial Weyl commutator',all(padd(delta(raising(p)),pscale(raising(delta(p)),-1))==p for p in polys),[175,47,7],cases=len(polys))
    # Square truncation through degree d: the top basis vector cannot be raised.
    d=5;D=mat([[j if i==j-1 else 0 for j in range(d+1)] for i in range(d+1)])
    R=mat([[int(i==j+1) for j in range(d+1)] for i in range(d+1)])
    Ed=mat([[int(i==j==d) for j in range(d+1)] for i in range(d+1)])
    record('R16','a finite square Weyl representation retains a top-degree defect',sub(mm(D,R),mm(R,D))==sub(eye(d+1),scale(Ed,d+1)),[175,47],kind='counterexample')
    record('R17','backward difference realizes the falling-factorial degree operator',all(degree_op(fall(k))==pscale(fall(k),k) for k in range(9)),[176],cases=9)
    f3=fall(3)
    mod=lambda p: tuple(int(c)%3 for c in p)
    record('R18','finite characteristic preserves the integral basis but loses a spectral selector',any(mod(f3)) and not any(mod(degree_op(f3))) and qp(f3,2,0)==ps([0]) and qp(ps([1]),2,0)==ps([1]),[41,173,176,29],kind='counterexample')
    # Logarithm, exponential and reversion are different nonlinear operations.
    tests=[]
    for degree in range(1,9):
        phi0=ps([0,2,F(-1,3),F(2,5)]);psi=revert(phi0,degree)
        tests.append(pcompose_trunc(phi0,psi,degree)==ps([0,1]))
        tests.append(pcompose_trunc(psi,phi0,degree)==ps([0,1]))
    record('R19','formal compositional inversion works in both directions',all(tests),[177,60],cases=len(tests))
    record('R20','singular formal charts are rejected',rejects(lambda:revert(ps([0,0,1]),6)),[177],kind='guard rejection')
    u=ps([0,1,F(-2,3),F(1,5)])
    record('R21','formal exponential and logarithm invert after truncation',plog(pexp(u,9),9)==u and pexp(plog(padd(ps([1]),u),9),9)==padd(ps([1]),u),[203,66],cases=2)
    v=ps([0,F(1,2),1])
    record('R22','formal exponential converts commuting sums into products',pexp(padd(u,v),8)==pmul(pexp(u,8),pexp(v,8),8),[203,204])
    record('R23','formal exponential rejects an unhandled constant term',rejects(lambda:pexp(ps([1,1]),5)),[203],kind='guard rejection')
    aa=ps([1,2,3]);bb=ps([2,-1,1]);cc=ps([1,0,-2]);gam=[F(factorial(k)**2) for k in range(7)]
    prod=normalized_product(aa,bb,gam)
    ordinary=pmul(ps([a/gam[k] for k,a in enumerate(aa)]),ps([b/gam[k] for k,b in enumerate(bb)]))
    record('R24','normalized multiplication matches independent ordinary coefficients',ps([c/gam[k] for k,c in enumerate(prod)])==ordinary,[204,52,67])
    record('R25','general normalized multiplication is associative',normalized_product(normalized_product(aa,bb,gam),cc,gam)==normalized_product(aa,normalized_product(bb,cc,gam),gam),[204],cases=1)
    # Finite recurrence, observation and control.
    seq=tuple(F(k*k+(-1)**k,3) for k in range(12));coeff=(F(1),F(1));ds=defects(seq,coeff)
    record('R26','initial state plus defects reconstructs an arbitrary finite sequence',synth(seq[:2],ds,coeff)==seq,[178,63,64])
    record('R27','discarding recurrence defects changes a nonhomogeneous sequence',synth(seq[:2],[F(0)]*len(ds),coeff)!=seq,[178,64],kind='counterexample')
    A=mat([[0,1],[1,1]]);B=mat([[0],[1]]);C=mat([[1,0]]);O=obs(A,C,4);x=(F(3),F(-2))
    record('R28','observability recovers the initial state when full rank',rank(O)==2 and recover(O,mv(O,x))==x,[179,178])
    O_bad=obs(eye(2),C,5)
    record('R29','a longer observation list need not resolve a hidden state',rank(O_bad)==1 and mv(O_bad,(F(0),F(1)))==(F(0),)*5,[179],kind='counterexample')
    inputs=[(F(2),),(F(-1),),(F(3),)];terminal=control(A,B,inputs)
    expected=tuple(sum(mv(mm(power(A,2-j),B),inputs[j])[i] for j in range(3)) for i in range(2))
    record('R30','controllability uses chronological input powers',terminal==expected,[180,63])
    record('R31','reversing input order changes the terminal state',control(A,B,list(reversed(inputs)))!=terminal,[180],kind='counterexample')
    traceA=mat([[1,1],[1,-1],[2,0]]);m=(F(2),F(3));y=mv(traceA,m)
    record('R32','finite trace observation and reconstruction are inverse on the image',recover(traceA,y)==m,[181,182])
    record('R33','inconsistent overdetermined observations are rejected',rejects(lambda:recover(traceA,(F(5),F(-1),F(9)))),[182],kind='guard rejection')
    bad=mat([[1,1],[2,2]])
    record('R34','rank-deficient trace data cannot resolve all constituents',mv(bad,(F(1),F(0)))==mv(bad,(F(0),F(1))) and rejects(lambda:recover(bad,(F(1),F(2)))),[181,182],kind='counterexample')
    half=recover(mat([[1,1],[1,-1]]),(F(1),F(0)))
    record('R35','unique rational recovery is not an integral multiplicity certificate',half==(F(1,2),F(1,2)),[182],kind='counterexample')
    # Quotient observations and descended dynamics.
    s=lambda x:x[0]+x[1];t=lambda x:x[1]+x[2]
    z=(F(-1),F(1),F(-1))
    record('R36','joint query retains both observations but may keep a nonzero kernel',s(z)==t(z)==0 and z!=(F(0),)*3,[183],kind='counterexample')
    q=mat([[1,0]]);T=mat([[2,0],[3,4]]);Tb=mat([[2]])
    record('R37','kernel-preserving dynamics descends to the coarse state',mm(q,T)==mm(Tb,q),[184,15,124])
    Tbad=mat([[1,1],[0,1]]);x=(F(0),F(0));xp=(F(0),F(1))
    record('R38','equal present observations can have different future observations',mv(q,x)==mv(q,xp) and mv(mm(q,Tbad),x)!=mv(mm(q,Tbad),xp),[184,162],kind='counterexample')
    # Metric-aware finite transport.
    Qx=mat([[2,1],[1,2]]);Qy=mat([[3,0],[0,1]]);T=mat([[1,2],[0,1]]);Tsh=adj(T,Qx,Qy)
    record('R39','metric adjoint satisfies the exact pairing identity',mm(Qx,Tsh)==mm(tr(T),Qy) and Tsh!=tr(T),[185,5])
    record('R40','metric adjoints reverse composition',adj(mm(T,Tsh),Qy,Qy)==mm(adj(Tsh,Qy,Qx),adj(T,Qx,Qy)),[185,3])
    record('R41','a singular coefficient metric cannot be inverted as a positive metric',rejects(lambda:adj(T,mat([[1,0],[0,0]]),Qy)),[185,23],kind='guard rejection')
    Rx=mat([[2,1],[0,1]]);Ry=mat([[1,0],[1,2]]);Qx=mm(tr(Rx),Rx);Qy=mm(tr(Ry),Ry);W=mm(mm(Ry,T),inv(Rx))
    record('R42','whitening carries the metric quadratic form',mm(tr(W),W)==mm(mm(tr(inv(Rx)),pull_metric(T,Qy)),inv(Rx)),[186,185])
    Ox=mat([[F(3,5),F(-4,5)],[F(4,5),F(3,5)]]);Oy=mat([[0,-1],[1,0]])
    Wx=mm(mm(mm(Oy,Ry),T),inv(mm(Ox,Rx)))
    record('R43','changing metric factors changes only unitary coordinates',Wx==mm(mm(Oy,W),tr(Ox)),[186,187])
    # Exact diagonal condition numbers avoid any rounded singular-value computation.
    def Ddiag(v):return max(map(abs,v))/min(map(abs,v))
    a=(F(2),F(1,2));b=(F(1,2),F(2));ab=tuple(x*y for x,y in zip(a,b))
    record('R44','distortion is submultiplicative but not multiplicative',Ddiag(ab)==1 and Ddiag(a)*Ddiag(b)==16,[187],kind='counterexample')
    # The two individual rotations have square -I but their mixed word is hyperbolic.
    t=F(9);A=mat([[0,-1],[1,0]]);Bt=mat([[0,-t],[1/t,0]]);mixed=mm(A,Bt)
    Q=mat([[1/t,0],[0,1]])
    record('R45','individual finite-order generators can hide a mixed-word obstruction',mm(A,A)==scale(eye(2),-1) and mm(Bt,Bt)==scale(eye(2),-1) and mixed==mat([[-1/t,0],[0,-t]]),[187,189,191],kind='counterexample')
    # For anti-diagonal maps, generalized Gram eigenvalues are explicit rationals.
    ga=mm(inv(Q),pull_metric(A,Q));gb=mm(inv(Q),pull_metric(Bt,Q))
    record('R46','the source two-generator balancing metric has distortion nine',ga==mat([[t,0],[0,1/t]]) and gb==mat([[1/t,0],[0,t]]),[187,189])
    T1=mat([[-4]]);normalized=scale(T1,F(1,4))
    record('R47','determinant normalization fixes modulus rather than sign',normalized==mat([[-1]]) and abs(normalized[0][0])==1,[188],kind='counterexample')
    Qx=mat([[2,1],[1,3]]);T=mat([[1,2],[0,1]]);Qy=metric_prop(T,Qx)
    record('R48','edge metric propagation gives a vanishing isometry residual',metric_def(T,Qx,Qy)==zero(2,2),[189,191])
    U=mat([[2,0],[1,1]]);Qz=metric_prop(U,Qy)
    record('R49','metric propagation composes along a path',Qz==metric_prop(mm(U,T),Qx),[191,24])
    H=mat([[1,1],[0,1]]);g=mat([[2,1],[0,1]]);Hn=mm(mm(g,H),inv(g));Qn=metric_prop(g,Qx)
    record('R50','metric holonomy residual is coordinate invariant',hs(H,Qx)==hs(Hn,Qn),[190,24])
    record('R51','keeping the metric fixed breaks full-coordinate invariance',hs(H,Qx)!=hs(Hn,Qx),[190],kind='counterexample')
    # A unipotent invariant-metric equation forces the leading quadratic coefficient to zero.
    Qtest=mat([[2,3],[3,8]]);defect=metric_def(H,Qtest,Qtest)
    record('R52','the unipotent metric equation exposes the positive-metric obstruction',defect[0][1]==Qtest[0][0] and defect[0][0]==0,[189,191],kind='counterexample')
    Qx=mat([[2,1],[1,3]]);Qy=mat([[1,0],[0,2]]);Qz=mat([[3,1],[1,2]])
    eT=metric_def(T,Qx,Qy);eU=metric_def(U,Qy,Qz);eUT=metric_def(mm(U,T),Qx,Qz)
    record('R53','quadratic metric defects obey the exact pullback composition law',eUT==add(eT,pull_metric(T,eU)),[192,189,171])
    record('R54','plain addition is not the metric-defect composition law',eUT!=add(eT,eU),[192],kind='counterexample')
    # Finite integration and observation.
    nodes=(F(-1),F(0),F(2));weights=(F(1,2),F(2,3),F(3,4));p=ps([1,-2,3,1]);qpol=ps([2,0,-1]);mu=moments(nodes,weights,5)
    record('R55','atomic integration is linear in the integrand',atomic(padd(p,pscale(qpol,3)),nodes,weights)==atomic(p,nodes,weights)+3*atomic(qpol,nodes,weights),[193,197])
    record('R56','atomic moments reproduce independent point evaluation',atomic(p,nodes,weights)==sum(c*mu[k] for k,c in enumerate(p)),[194,193])
    B=mat([[1,0,0],[0,1,-1],[0,0,1]]);coeff=(F(2),F(3),F(-1));ell=mat([mu[:3]])
    record('R57','integration covectors carry the exact polynomial basis witness',mv(mm(ell,B),coeff)[0]==atomic(ps(mv(B,coeff)),nodes,weights),[194,172,40])
    fnodes=tuple(2*x-3 for x in nodes)
    record('R58','affine pushforward equals pullback of the integrand',atomic(p,fnodes,weights)==atomic(pcompose(p,ps([-3,2])),nodes,weights),[195,58,172])
    record('R59','noninjective finite pushforward preserves total mass',atomic(ps([1]),(F(0),)*3,weights)==sum(weights),[195,193])
    ny=(F(1),F(3));wy=(F(2),F(1,2));poly2={(0,0):F(1),(2,1):F(3),(1,2):F(-2)}
    direct=sum(wx*w0*sum(c*x**i*y**j for (i,j),c in poly2.items()) for x,wx in zip(nodes,weights) for y,w0 in zip(ny,wy))
    via_mom=sum(c*moments(nodes,weights,2)[i]*moments(ny,wy,2)[j] for (i,j),c in poly2.items())
    record('R60','finite product integration agrees with iterated moments',direct==via_mom,[196,194])
    # Correlated Bernoulli coordinates have E[XY]=1/2, not the independent 1/4.
    record('R61','product marginals cannot replace an arbitrary joint measure',F(1,2)!=F(1,2)*F(1,2),[196],kind='counterexample')
    sx=(F(0),F(1,2),F(1));sw=(F(1,6),F(4,6),F(1,6))
    good=[sum(w*x**k for x,w in zip(sx,sw))==F(1,k+1) for k in range(4)]
    record('R62','Simpson moments certify every cubic polynomial on the given interval',all(good),[197,198],cases=4)
    discrepancy=F(1,5)-sum(w*x**4 for x,w in zip(sx,sw))
    record('R63','exact rational quadrature is not exact integration at every degree',discrepancy==F(-1,120),[197,198],kind='counterexample')
    wbad=(F(2),F(-1));nbad=(F(0),F(1));square=ps([0,0,1])
    record('R64','a signed quadrature rule need not preserve positivity',atomic(square,nbad,wbad)==-1,[193,197],kind='counterexample')
    mres=tuple(moment(k,F(0),F(1))-sum(w*x**k for x,w in zip(sx,sw)) for k in range(5));p4=ps([1,-3,2,0,7])
    record('R65','quadrature residual is the coefficient pairing with moment discrepancies',integral(p4,F(0),F(1))-atomic(p4,sx,sw)==sum(c*mres[k] for k,c in enumerate(p4)),[198,194])
    family=[ps([1,2,3]),ps([-2,1,0,1]),ps([4,0,-1])];ws=[F(1,2),F(-2,3),F(3,4)];total=ps([0]);dtotal=ps([0])
    for w,f in zip(ws,family):total=padd(total,pscale(f,w));dtotal=padd(dtotal,pscale(deriv(f),w))
    record('R66','fixed-weight differentiation commutes with a finite weighted sum',deriv(total)==dtotal,[199,102,193])
    w=ps([0,1]);f=ps([0,0,1]);actual=deriv(pmul(w,f));naive=pmul(w,deriv(f))
    record('R67','moving weights contribute an additional derivative term',padd(actual,pscale(naive,-1))==pmul(deriv(w),f) and actual!=naive,[199],kind='counterexample')
    a=F(-1);b=F(2);rho=F(3,2);f=ps([1,2,-1]);g=ps([0,1,0,1]);boundary=rho*(peval(f,b)*peval(g,b)-peval(f,a)*peval(g,a))
    record('R68','integration by parts retains its bilinear endpoint term',integral(pmul(f,deriv(g)),a,b,rho)+integral(pmul(deriv(f),g),a,b,rho)==boundary,[200,53,56])
    p=ps([1,2,-1,3]);left=integral(pcompose(p,ps([1,-3])),F(0),F(2),F(2));right=integral(p,F(-5),F(1),F(2,3))
    record('R69','negative affine slope uses absolute density scaling',left==right,[201,195])
    record('R70','a constant affine map produces an atom rather than an infinite density',integral(pcompose(p,ps([2])),F(0),F(2),F(2))==4*peval(p,F(2)),[201,195],kind='counterexample')
    # Distinguished dual frame and finite recursive filter continuation.
    A=mat([[1,0],[0,1],[1,1]]);Sd=mm(inv(mm(tr(A),A)),tr(A));Pd=mm(A,Sd)
    record('R71','canonical dual synthesis is a left inverse with orthogonal coefficient projection',mm(Sd,A)==eye(2) and Pd==tr(Pd) and mm(Pd,Pd)==Pd,[202,17,18,94])
    record('R72','rank-deficient analysis cannot use the full-rank dual formula',rejects(lambda:inv(mm(tr(mat([[1,1],[2,2]])),mat([[1,1],[2,2]])))),[202],kind='guard rejection')
    a=(F(1),F(-1,2),F(1,4));b=(F(1),F(1,3));x=tuple(F(i-3,5) for i in range(10));z=tuple(F((-1)**i,7) for i in range(10))
    y=filter_iir(x,b,a);yz=filter_iir(z,b,a)
    record('R73','zero-state recursive filtering is linear',filter_iir(tuple(u+v for u,v in zip(x,z)),b,a)==tuple(u+v for u,v in zip(y,yz)),[205])
    cut=4;part1=filter_iir(x[:cut],b,a);part2=filter_iir(x[cut:],b,a,pre_y=part1[-2:],pre_x=x[cut-1:cut])
    record('R74','recursive filtering composes across chunks only with continuation state',part1+part2==y,[205,63])
    record('R75','dropping a filter continuation state changes the next chunk',filter_iir(x[cut:],b,a)!=part2,[205],kind='counterexample')
    record('R76','a nonzero fixed filter state gives an affine input map',filter_iir((F(0),)*5,b,a,pre_y=(F(0),F(1)))!=(F(0),)*5,[205,63],kind='counterexample')
    record('R77','recursive filter rejects a zero leading denominator',rejects(lambda:filter_iir(x,b,(F(0),F(1)))),[205],kind='guard rejection')
    # Refine previous weak witnesses with explicit identities and boundary guards.
    bayes=lambda v:(v[0]/(v[0]+2*v[1]),2*v[1]/(v[0]+2*v[1]))
    p0=(F(1),F(0));p1=(F(0),F(1));mid=(F(1,2),F(1,2))
    record('R78','Bayesian nonlinearity is witnessed against both endpoint images',bayes(mid)!=tuple((u+v)/2 for u,v in zip(bayes(p0),bayes(p1))),[126],kind='counterexample')
    record('R79','rational matrix fixtures reject ragged input',rejects(lambda:mat([[1,2],[3]])),[159],kind='guard rejection')
    record('R80','rational matrix fixtures reject mismatched addition',rejects(lambda:add(eye(2),eye(3))),[4,159],kind='guard rejection')
    record('R81','rational matrix fixtures reject truncated vector application',rejects(lambda:mv(eye(2),(F(1),))),[159],kind='guard rejection')
    record('R82','exact fixture inputs reject implicit floating-point conversion',rejects(lambda:mat([[0.1]]),TypeError),[159],kind='guard rejection')

    # Typed defects compose through the retained coarse dynamics.
    qx=mat([[1,0]]);qy=mat([[1,1]]);qz=mat([[0,1]])
    T=mat([[1,2],[0,1]]);U=mat([[2,0],[1,3]])
    bt=mat([[2]]);bu=mat([[3]])
    et=sub(mm(qy,T),mm(bt,qx));eu=sub(mm(qz,U),mm(bu,qy))
    eut=sub(mm(qz,mm(U,T)),mm(mm(bu,bt),qx))
    record('R83','typed coarse-map defects retain both intermediate contributions',eut==add(mm(eu,T),mm(bu,et)),[121,184,171])
    record('R84','coarse-map defects cannot be added without their transports',eut!=add(eu,et),[121,184],kind='counterexample')
    impulse=(F(1),)+(F(0),)*7
    unstable=filter_iir(impulse,(F(1),),(F(1),F(-2)))
    record('R85','finite recursive evaluation does not imply infinite-time stability',unstable==tuple(F(2**n) for n in range(8)),[205],kind='counterexample')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json',type=Path,help='Optionally save the named finite-check receipt')
    args=parser.parse_args()
    # Re-run the preserved suite, rather than merely importing its old receipt.
    stream=io.StringIO();oldargv=sys.argv
    try:
        sys.argv=[str(Path(prior.__file__))]
        prior.AUDIT_RECORDS.clear()
        with contextlib.redirect_stdout(stream):prior.main()
    finally:sys.argv=oldargv
    print(stream.getvalue(),end='')
    oldchecks=list(prior.AUDIT_RECORDS)
    if len(oldchecks)!=79:raise AssertionError('unexpected preserved suite count')
    run_extensions()
    allchecks=oldchecks+RECORDS
    if len({r['id'] for r in allchecks})!=len(allchecks):raise AssertionError('duplicate test identifiers')
    receipt={'suite':'Komorebi operator compendium refined exact finite fixtures',
        'arithmetic':'integers and fractions.Fraction; no floating-point comparisons',
        'python':platform.python_version(),'baseline_replayed':True,'baseline_checks':len(oldchecks),
        'added_checks':len(RECORDS),'passed':len(allchecks),'failed':0,
        'kinds':dict(Counter(r['kind'] for r in allchecks)),
        'scope':'Independent finite mathematical fixtures, not library execution or Lean verification.',
        'baseline_script_sha256':hashlib.sha256(Path(prior.__file__).read_bytes()).hexdigest(),
        'checks':allchecks}
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('RESULT',receipt['passed'],'/',receipt['passed'],'named finite checks passed')
    print('KINDS',receipt['kinds'])

if __name__=='__main__':main()
