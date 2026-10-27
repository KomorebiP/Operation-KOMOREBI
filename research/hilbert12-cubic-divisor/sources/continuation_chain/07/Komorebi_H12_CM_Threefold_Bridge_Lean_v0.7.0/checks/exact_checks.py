#!/usr/bin/env python3
"""Exact Q/Eisenstein certificates; no gamma value is used or fitted.
The finite residue enumeration is deliberately bounded. Uniform statements
have the proofs in PROOF.md and the explicit Std-only Lean modules.
"""
from pathlib import Path
from datetime import datetime, timezone
import sympy as s
from sympy.matrices.normalforms import smith_normal_form
from fractions import Fraction as F
import json,time,itertools,platform,hashlib
ROOT=Path(__file__).resolve().parents[1]
r,w,z=s.symbols('r w z')
G=s.groebner([r**3-7,w*w+w+1],r,w,domain=s.QQ)
def red(f): return s.expand(G.reduce(s.expand(f))[1])
mons=[s.Integer(1),w,r,r*w,r*r,r*r*w]
def vec(f):
    q=red(f)
    return s.Matrix([q.coeff(r,i).coeff(w,j) for i in range(3) for j in range(2)])
def transform(f,rr,ww):return red(s.sympify(f).subs({r:rr,w:ww},simultaneous=True))
# Independent integer coefficient implementation.
def ea(x,y):return (x[0]+y[0],x[1]+y[1])
def em(x,y):return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]-x[1]*y[1])
def sc(n,x):return(n*x[0],n*x[1])
def rm(a,b):
    return (ea(em(a[0],b[0]),sc(7,ea(em(a[1],b[2]),em(a[2],b[1])))),
            ea(ea(em(a[0],b[1]),em(a[1],b[0])),sc(7,em(a[2],b[2]))),
            ea(ea(em(a[0],b[2]),em(a[1],b[1])),em(a[2],b[0])))
def poly(a):return sum((a[i][0]+w*a[i][1])*r**i for i in range(3))
def ev(a,k):return (a[0][0]+k*a[0][1])%7

def main():
    tic=time.monotonic(); checks=[];neg=[]
    def ck(name,p):
        if not p:raise AssertionError(name)
        checks.append(name)
    def nc(name,p):
        if not p:raise AssertionError('negative control '+name)
        neg.append(name)
    b=w*w*r;bb=w*r
    S=s.Matrix.hstack(*[vec(transform(m,w*r,w)) for m in mons])
    K=s.Matrix.hstack(*[vec(transform(m,r,w*w)) for m in mons])
    R=s.Matrix.hstack(*[vec(r*m) for m in mons])
    U=[s.Matrix.hstack(*[vec((2-e)*m) for m in mons]) for e in [b,r,bb]]
    A=s.diag(1,7,1,1,1,1)
    span=s.Matrix.hstack(*[vec(f) for f in [1,b,b*b,bb,bb*bb]])
    ck('joined rational span has rank five',span.rank()==5)
    ck('real generator recovered',red(-b-bb)==r)
    ck('mixed product supplies seventh multiple of omega',red(b*bb**2)==7*w)
    ck('square real generator recovered',red(b*bb)==r*r)
    ck('twisted quadratic coefficient recovered',red(b*b)==w*r*r)
    ck('joined order index seven',abs(A.det())==7)
    ck('joined order Smith factors',list(smith_normal_form(A,domain=s.ZZ).diagonal())==[1,1,1,1,1,7])
    ck('conductor has index forty-nine',R.det()==49)
    ck('conductor is contained in joined order',all(q.q==1 for q in A.inv()*R))
    ck('rotation order three',S**3==s.eye(6))
    ck('conjugation order two',K**2==s.eye(6))
    ck('semilinear dihedral relation',K*S*K==S**2)
    nc('rotation is not conjugation-commuting',S*K!=K*S)
    ck('conjugate unit norm one',U[0]*U[1]*U[2]==s.eye(6))
    for i in range(3):
        ck(f'unit {i} determinant one',U[i].det()==1)
        ck(f'unit {i} preserves joined order',all(q.q==1 for q in A.inv()*U[i]*A))
        ck(f'unit rotation {i}',S*U[i]*S**2==U[(i+1)%3])
        ck(f'unit {i} defect action two',all(int(U[i][1,j]-(2 if j==1 else 0))%7==0 for j in range(6)))
    ck('complex conjugation exchanges the units',K*U[0]*K==U[2])
    J=2+3*w;Jb=-1-3*w
    ck('Jacobi pair adds to one',red(J+Jb)==1)
    ck('Jacobi norm seven',red(J*Jb)==7)
    ck('Jacobi exact idempotence defect minus seven',red(J*J-J)==-7)
    nc('Jacobi is not an idempotent in characteristic zero',red(J*J)!=red(J))
    ck('Jacobi two residue projectors',[int(J.subs(w,k))%7 for k in (2,4)]==[1,0])
    ck('conjugate Jacobi residues',[int(Jb.subs(w,k))%7 for k in (2,4)]==[0,1])
    nc('Jacobi is not in the joined order',int(vec(J)[1])%7!=0)
    chi=[0,1,w,w*w,w*w,w,1]
    ck('finite Jacobi sum has chosen orientation',red(sum(chi[a]*chi[(1-a)%7] for a in range(7)))==red(J))
    for a in range(1,7):ck(f'character multiplication by two {a}',red(chi[2*a%7]-w*chi[a])==0)
    gg=s.groebner([w*w+w+1,sum(z**i for i in range(7))],z,w,domain=s.QQ)
    gs=sum(chi[a]*z**(3*a%7) for a in range(1,7))
    ck('Gauss cubic agrees exactly',gg.reduce(s.expand(gs**3-7*J))[1]==0)
    # Exhaustive residue tests, recorded as whole finite assertions.
    residues=list(itertools.product(range(7),repeat=2))
    pairs={((a+2*b)%7,(a+4*b)%7) for a,b in residues}
    ck('two-branch residue map bijective in all 49 cases',len(pairs)==49)
    ck('diagonal pullback in all 49 cases',all(((a+2*b)%7==(a+4*b)%7)==(b==0) for a,b in residues))
    ck('universal residue conductor in all 49 times 49 cases',all(
        all(((em((a,b),(c,d))[1])%7==0) for c,d in residues)==(a==0 and b==0)
        for a,b in residues))
    test=[((a,b),(c,1-a),(b-c,2)) for a,b,c in itertools.product(range(-2,3),repeat=3)]
    basis=[tuple((int(i==j),0) for i in range(3)) for j in range(3)]+[tuple((0,int(i==j)) for i in range(3)) for j in range(3)]
    ck('independent coefficient multiplication all 36 basis pairs',all(s.expand(poly(rm(a,b)))==red(poly(a)*poly(b)) for a in basis for b in basis))
    ck('joined multiplication test in the declared 125-point family',all(rm(a,((0,7),(1,0),(0,1)))[0][1]%7==0 for a in test if a[0][1]%7==0))
    # Actual CM threefold matrices.
    T=s.Matrix([[0,0,7],[1,0,0],[0,1,0]])
    B=2*s.eye(3)-T
    M=s.Matrix([[0,1,0],[-4,2,15],[-1,0,4]])
    D=s.Matrix([[0,-2,15],[2,-1,0],[1,0,0]])
    ck('original unit determinant one',M.det()==1)
    ck('actual basis-change intertwines units',B*D==D*M)
    ck('basis-change determinant fifteen',D.det()==15)
    ck('ordinary fixed determinant six',(s.eye(3)-M).det()==6)
    ck('twisted fixed determinant six J',red((w*M-s.eye(3)).det())==red(6*J))
    ck('opposite twist determinant six conjugate J',red((w*w*M-s.eye(3)).det())==red(6*Jb))
    c=3+w
    ck('c is minus omega times J',red(c+w*J)==0)
    ck('c cubic difference six J',red(c**3-7)==red(6*J))
    vo=s.Matrix([3,3,1]);vt=s.Matrix([5+w,-4-5*w,1]);v7=s.Matrix([1,2,4])
    ck('original ordinary parameterization',(s.eye(3)-M)*vo==s.Matrix([0,-6,0]))
    ck('original twisted parameterization',all(red(x-y)==0 for x,y in zip((w*M-s.eye(3))*vt,[0,6*c,0])))
    ck('actual seven-line doubling carry',M*v7-2*v7==s.Matrix([0,56,7]))
    ck('actual seven-line twisted divisibility',all(red(x-J*y)==0 for x,y in zip((w*M-s.eye(3))*v7,[1+w,26+18*w,7+6*w])))
    ck('seven-line coordinate change',D*v7==s.Matrix([56,0,1]))
    nc('wrong twist does not fix the oriented seven point',any(red(x*Jb/7).as_poly(w).domain!=s.ZZ and any(k.q!=1 for k in s.Poly(red(x*Jb/7),w).all_coeffs()) for x in (w*w*M-s.eye(3))*v7))
    # Restriction of scalars gives exact finite fixed-group invariant factors.
    def realify(mat):
        out=s.zeros(2*mat.rows,2*mat.cols)
        for i in range(mat.rows):
            for j in range(mat.cols):
                x=red(mat[i,j]);a=x.coeff(w,0);b=x.coeff(w,1)
                out[2*i:2*i+2,2*j:2*j+2]=s.Matrix([[a,-b],[b,a-b]])
        return out
    so=smith_normal_form(realify(s.eye(3)-M),domain=s.ZZ)
    st=smith_normal_form(realify(w*M-s.eye(3)),domain=s.ZZ)
    ck('ordinary fixed group 6 by 6',[abs(int(x)) for x in so.diagonal()]==[1,1,1,1,6,6])
    ck('twisted fixed group 6 by 42',[abs(int(x)) for x in st.diagonal()]==[1,1,1,1,6,42])
    ck('twisted over ordinary degree ratio seven',abs(realify(w*M-s.eye(3)).det())==7*abs(realify(s.eye(3)-M).det()))
    jm=realify(s.Matrix([[J]]))
    ck('seventh kernel cyclic',[abs(int(x)) for x in smith_normal_form(jm,domain=s.ZZ).diagonal()]==[1,7])
    ck('CRT splitting has exact Bezout identity',7-6==1)
    ck('CRT splitting defect multiple 6J',red(s.Integer(7*7-7)/6-J*Jb)==0)
    P=s.Matrix([[0,-1],[1,-1]]);Kp=s.Matrix([[-1,0],[-1,1]])
    ck('unit character rotation coinvariants',[abs(int(x)) for x in smith_normal_form(P-s.eye(2),domain=s.ZZ).diagonal()]==[1,3])
    H=(P-s.eye(2)).row_join(Kp+s.eye(2))
    sh=smith_normal_form(H,domain=s.ZZ)
    ck('twisted reflection destroys coinvariants',[abs(int(sh[i,i])) for i in range(2)]==[1,1])
    # Exactly demonstrate the two nonzero multiplication-by-two orbits.
    ck('residue unit orbits',[[pow(2,k,7) for k in range(3)],[3*pow(2,k,7)%7 for k in range(3)]]==[[1,2,4],[3,6,5]])
    # Exact rational representatives on E_omega and E_omega^3.
    def tor(a):return (F(a[0])%1,F(a[1])%1)
    zero=(F(0),F(0));Jpair=(2,3);Jbarpair=(-1,-3)
    inv6J=(F(-1,42),F(-3,42)); invJ=(F(-1,7),F(-3,7))
    points252={tor(em((a,b),inv6J)) for a in range(42) for b in range(42)}
    points36={tor((F(a,6),F(b,6))) for a in range(6) for b in range(6)}
    points7={tor(sc(a,invJ)) for a in range(7)}
    tp=lambda z:(tor(em((5,1),z)),tor(em((-4,-5),z)),tor(z))
    op=lambda z:(tor(sc(3,z)),tor(sc(3,z)),tor(z))
    ip=lambda z:(tor(z),tor(sc(2,z)),tor(sc(4,z)))
    def mv(mat,v):return tuple(tor(tuple(sum(int(mat[i,j])*v[j][k] for j in range(3)) for k in range(2))) for i in range(3))
    def mscalar(a,v):return tuple(tor(em(a,x)) for x in v)
    def tadd(x,y):return tuple(tor(ea(a,b)) for a,b in zip(x,y))
    ck('enumerated exact 6J torsion has 252 elements',len(points252)==252)
    ck('all 252 original twisted points satisfy their equation',all(mscalar((0,1),mv(M,tp(z)))==tp(z) for z in points252))
    ck('all 36 ordinary points satisfy their equation',all(mv(M,op(z))==op(z) for z in points36))
    phi={z:tor(em(Jpair,z)) for z in points252}
    ck('fixed-point projection is onto the 36 ordinary parameters',set(phi.values())==points36)
    ck('each projection fiber has exactly seven points',all(sum(v==y for v in phi.values())==7 for y in points36))
    ck('kernel is the seven-point CM torsion group',{z for z,v in phi.items() if v==zero}==points7)
    ck('explicit conjugate-J section splits the projection',all(tor(em(Jpair,em(Jbarpair,y)))==y and tor(em(Jbarpair,y)) in points252 for y in points36))
    ck('seven and minus six split every twisted point',all(tadd(tp(tor(sc(7,z))),tp(tor(sc(-6,z))))==tp(z) for z in points252))
    ck('actual 1 2 4 seven-line equals the kernel subset',{ip(z) for z in points7}=={tp(z) for z in points7})
    ck('unit action on all seven points is doubling',all(mv(M,ip(z))==ip(tor(sc(2,z))) for z in points7))
    ck('first coordinate recovers the CM point',all(ip(z)[0]==z for z in points7))
    nc('opposite twist fails on all six nonzero oriented points',all(mscalar((-1,-1),mv(M,ip(z)))!=ip(z) for z in points7 if z!=zero))
    cb=lambda z:tor((z[0]-z[1],-z[1]))
    ck('complex conjugation sends every oriented point to opposite twist',all(mscalar((-1,-1),mv(M,ip(cb(z))))==ip(cb(z)) for z in points7))
    tt=-(b*b+2*b)/15
    bt=transform(tt,r,w*w)
    ck('cubic period polynomial exact',red(225*tt**3-42*tt+7)==0)
    ck('period recovers cubic generator',red((b-2)*(4-15*tt)+1)==0)
    ck('period and conjugate rational spans have rank five',s.Matrix.hstack(*[vec(v) for v in [1,tt,tt*tt,bt,bt*bt]]).rank()==5)
    data={'started_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':time.monotonic()-tic,
          'checks':checks,'negative_controls':neg,'assertion_count':len(checks),'negative_count':len(neg),
          'software':{'python':platform.python_version(),'sympy':s.__version__},'exit_status':0,
          'scope':'Exact algebra and explicitly bounded residue enumerations; no analytic reality or arithmetic gamma identity.',
          'matrices':{'sigma':S.tolist(),'kappa':K.tolist(),'unit0':U[0].tolist(),'basis_change':D.tolist(),'ordinary_snf':so.tolist(),'twisted_snf':st.tolist()}}
    (ROOT/'evidence/exact_results.json').write_text(json.dumps(data,indent=2,default=str)+'\n')
    print('PASS',len(checks),'exact assertions;',len(neg),'negative controls',round(data['runtime_seconds'],3),'s')
if __name__=='__main__':main()
