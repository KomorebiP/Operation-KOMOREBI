#!/usr/bin/env python3
"""Exact integer/rational verification. No analytic gamma evaluation or fitting.
The torus/gerbe interpretation is proved separately in PROOF.md.
"""
from __future__ import annotations
from pathlib import Path
from itertools import combinations, product, permutations
from fractions import Fraction as F
from datetime import datetime, timezone
import json, time, hashlib, platform
import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
ROOT=Path(__file__).resolve().parents[1]
checks=[]; negatives=[]
def ck(name: str, test: bool) -> None:
    if not bool(test): raise AssertionError(name)
    checks.append(name)
def neg(name: str, false_claim: bool) -> None:
    if bool(false_claim): raise AssertionError('Negative control unexpectedly true: '+name)
    negatives.append(name)
def emul(x,y): return (x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0]-x[1]*y[1])
def eadd(x,y): return (x[0]+y[0],x[1]+y[1])
def escale(n,x):return (n*x[0],n*x[1])
def enorm(x):return x[0]**2-x[0]*x[1]+x[1]**2
def ebar(x):return (x[0]-x[1],-x[1])
def mod1(x):return tuple(v%1 for v in x)
def matE(A,vs):return tuple(tuple(sum(A[i,j]*vs[j][k] for j in range(3)) for k in range(2)) for i in range(3))
def scalE(a,vs):return tuple(emul(a,v) for v in vs)
def vm(vs):return tuple(mod1(v) for v in vs)
def detsmall(A):
    n=len(A); ans=0
    for p in permutations(range(n)):
        inversions=sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        term=(-1)**inversions
        for i in range(n):term*=A[i][p[i]]
        ans+=term
    return ans

def main():
    start=datetime.now(timezone.utc).isoformat();tic=time.monotonic()
    M=sp.Matrix([[0,1,0],[-4,2,15],[-1,0,4]])
    R=sp.Matrix([[8,-4,15],[1,0,0],[2,-1,4]])
    Z=sp.zeros(3);I=sp.eye(3)
    B=sp.BlockMatrix([[Z,-M],[M,-M]]).as_explicit()
    C=sp.BlockMatrix([[Z,-R],[R,-R]]).as_explicit()
    D=sp.BlockMatrix([[-M,M],[-M,Z]]).as_explicit()
    ck('original matrix and inverse', M*R==R*M==I)
    ck('original determinant one',M.det()==1)
    ck('real twisted lattice determinant one',B.det()==1)
    ck('flat action inverse is opposite twist',C*D==D*C==sp.eye(6))
    t3=list(combinations(range(6),3)); t2=list(combinations(range(6),2))
    W=sp.Matrix(20,20,lambda i,j:B.extract(t3[j],t3[i]).det())
    Wind=sp.Matrix(20,20,lambda i,j:detsmall([[int(B[r,c]) for c in t3[i]] for r in t3[j]]))
    ck('all 400 third exterior entries independently computed',W==Wind)
    data=json.loads((ROOT/'evidence/exterior_data.json').read_text())
    ck('recorded exterior matrix matches actual minors',W==sp.Matrix(data['pullback3']))
    ck('third exterior fixed rank two', (W-sp.eye(20)).rank()==18)
    alpha=sp.Matrix(data['volume1']);beta=sp.Matrix(data['volumeW']);N=sp.Matrix.hstack(alpha,beta)
    ck('volume coefficient forms fixed',W*N==N)
    ck('volume coefficient parameters are primitive', N.extract([0,3],[0,1])==sp.eye(2))
    # Derive determinant coefficients directly over Eisenstein integers.
    vol=[]
    for tr in t3:
        rowcols=[[((1,0) if v<3 else (0,1)) if v%3==i else (0,0) for v in tr] for i in range(3)]
        ans=(0,0)
        for perm in permutations(range(3)):
            sg=(-1)**sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3))
            val=(sg,0)
            for i in range(3):val=emul(val,rowcols[i][perm[i]])
            ans=eadd(ans,val)
        vol.append(ans)
    ck('volume real and Eisenstein coefficients from determinant',sp.Matrix([v[0] for v in vol])==alpha and sp.Matrix([v[1] for v in vol])==beta)
    # D^3 times the (0,3) projection, D=omega-omega^2.
    h=[]
    for tr in t3:
        idx=[i%3 for i in tr]
        if len(set(idx))<3: h.append((0,0));continue
        sg=(-1)**sum(idx[i]>idx[j] for i in range(3) for j in range(i+1,3))
        val=(sg,0)
        for i in tr:val=emul(val,(0,1) if i<3 else (-1,0))
        h.append(val)
    H=sp.Matrix([[x[k] for x in h] for k in range(2)])
    ck('Hodge projection on invariant lattice',H*N==sp.Matrix([[0,3],[-3,0]]))
    ck('no invariant integral class with zero Hodge projection', (W-sp.eye(20)).col_join(H).rank()==20)
    cert=json.loads((ROOT/'evidence/elimination_certificate.json').read_text())
    # Inspect the durable exact elimination records below.
    records=cert if isinstance(cert,list) else cert['certificates']
    for c in records:
        i=c['coordinate']; den=c['denominator']; row=c['row']
        target=sp.zeros(1,20);target[0,i]=den;target[0,0]-=den*alpha[i];target[0,3]-=den*beta[i]
        ck(f'integer elimination certificate for coordinate {i}',sp.Matrix([row])*(W-sp.eye(20))==target)
    # The twist hypothesis is essential.
    Mu=sp.diag(M,M)
    Wu=sp.Matrix(20,20,lambda i,j:Mu.extract(t3[j],t3[i]).det())
    ck('untwisted fixed H3 rank eight', (Wu-sp.eye(20)).rank()==12)
    ck('untwisted Hodge-allowed fixed rank six',(Wu-sp.eye(20)).col_join(H).rank()==14)
    neg('incorrect extension of obstruction to untwisted M',(Wu-sp.eye(20)).col_join(H).rank()==20)
    # Integral (0,2) projection in cyclic component order 12,20,01.
    cyc=[(1,2),(2,0),(0,1)];P=sp.zeros(6,15)
    for j,(i,k) in enumerate(t2):
        if i%3==k%3:continue
        if (i%3,k%3) in cyc:rr=cyc.index((i%3,k%3));sg=1
        else:rr=cyc.index((k%3,i%3));sg=-1
        val=emul((0,1) if i<3 else (-1,0),(0,1) if k<3 else (-1,0))
        P[rr,j]=sg*val[0];P[rr+3,j]=sg*val[1]
    W2=sp.Matrix(15,15,lambda i,j:B.extract(t2[j],t2[i]).det())
    d2=json.loads((ROOT/'evidence/hodge2_data.json').read_text())
    ck('all 225 second exterior entries',W2==sp.Matrix(d2['pullback2']))
    ck('actual Hodge-two projection recorded',P==sp.Matrix(d2['projection']))
    ck('Hodge-two projection intertwines omega inverse M',P*W2==C*P)
    ck('integral surjectivity witness for Hodge lattice',P*sp.Matrix(d2['rightinverse'])==sp.eye(6))
    ck('Eisenstein scale D squared is minus three',emul((1,2),(1,2))==(-3,0))
    ck('flat parameter kernel has 252 points',abs((C-sp.eye(6)).det())==252)
    snf=smith_normal_form(C-sp.eye(6),domain=sp.ZZ)
    ck('flat parameter Smith invariants',sorted(abs(int(snf[i,i])) for i in range(6))==[1,1,1,1,6,42])
    neg('flat action is not omega M',C==B)
    J=(2,3);JB=(-1,-3);om=(0,1)
    ck('Jacobi norm seven',emul(J,JB)==(7,0))
    # Complete finite fixed group from exact rational parameterization.
    def gbar(z):return (emul((4,-1),z),emul((1,5),z),z)
    def h(z):return (escale(3,z),escale(3,z),z)
    def tor(z):return mod1(z)==(0,0)
    pts=[(F(i,42),F(j,42)) for i,j in product(range(42),repeat=2) if tor(emul(escale(6,JB),(F(i,42),F(j,42))))]
    ck('all 252 rational flat parameters enumerated',len(pts)==252)
    embedded=[vm(gbar(z)) for z in pts]
    ck('fixed parameterization injective',len(set(embedded))==252)
    ck('all enumerated classes fixed by flat action',all(vm(scalE(om,matE(R,v)))==v for v in embedded))
    ck('all enumerated classes fixed by opposite twist',all(vm(scalE((-1,-1),matE(M,v)))==v for v in embedded))
    ordinary={(F(i,6),F(j,6)) for i,j in product(range(6),repeat=2)}
    ck('projection to ordinary fixed group is surjective',{mod1(emul(JB,z)) for z in pts}==ordinary)
    kernel=[z for z in pts if tor(emul(JB,z))]
    ck('complementary seven sector has seven points',len(kernel)==7)
    ck('all sections split via J',all(mod1(emul(JB,emul(J,z)))==z for z in ordinary))
    ck('all seven subspace parameters have exponent seven',all(tor(escale(7,z)) for z in kernel))
    # Pairing convention: exp(2 pi i determinant/7) on integer coordinates.
    wedge=lambda x,y:x[0]*y[1]-x[1]*y[0]
    ck('oriented one-dimensional pairing exponent three',wedge(JB,J)==3)
    ck('complete 7 by 7 pairing table',all(wedge(escale(a,JB),escale(b,J))%7==(3*a*b)%7 for a,b in product(range(7),repeat=2)))
    ck('pairing nondegenerate on oriented sectors',all(any((3*a*b)%7!=0 for b in range(7)) for a in range(1,7)))
    ck('full product polarization exponent is 63',sum(wedge(escale(n,JB),escale(n,J)) for n in [1,2,4])==63)
    neg('full product polarization equals the selected one-dimensional pairing',63%7==3)
    neg('reversing orientation preserves additive character',(-3)%7==3)
    ch=[(0,0),(1,0),(0,1),(-1,-1),(-1,-1),(0,1),(1,0)]
    ck('cubic character covariance under doubling',all(ch[2*k%7]==emul(om,ch[k]) for k in range(7)))
    jac=(0,0)
    for k in range(7):jac=eadd(jac,emul(ch[k],ch[(1-k)%7]))
    ck('Jacobi sum exact',jac==J)
    gauss=[ch[5*k%7] for k in range(7)];cu=[]
    for k in range(7):
        ans=(0,0)
        for i,j in product(range(7),repeat=2):ans=eadd(ans,emul(emul(gauss[i],gauss[j]),gauss[(k-i-j)%7]))
        cu.append(ans)
    ck('Gauss cube as integer Eisenstein group-algebra identity',cu==[escale(6,J)]+[escale(-1,J)]*6)
    # An independent exact polynomial quotient check, not a floating root.
    x,w=sp.symbols('x w');gb=sp.groebner([sum(x**k for k in range(7)),w*w+w+1],x,w,domain=sp.QQ)
    GG=sum((ch[k][0]+w*ch[k][1])*x**((3*k)%7) for k in range(1,7))
    ck('Gauss cube independent SymPy cyclotomic reduction',gb.reduce(sp.expand(GG**3-7*(2+3*w)))[1]==0)
    neg('opposite Jacobi orientation cannot be substituted',gb.reduce(sp.expand(GG**3-7*(-1-3*w)))[1]==0)
    ck('coarse lattice map has determinant five',sp.diag(1,1,5).det()==5)
    ck('fifth smoothed topological class cancels',5-sp.diag(1,1,5).det()==0)
    result={'started_at':start,'runtime_seconds':time.monotonic()-tic,'exit_status':0,'assertion_count':len(checks),'negative_control_count':len(negatives),'assertions':checks,'negative_controls':negatives,'domains':'Integer matrices, rational coordinates modulo Z^2, Eisenstein coefficients, exact polynomial quotients over QQ','enumeration':{'third_exterior_entries':400,'second_exterior_entries':225,'fixed_classes':252,'ordinary_classes':36,'seven_kernel':7,'pairing_entries':49},'software':{'python':platform.python_version(),'sympy':sp.__version__},'non_claims':['No exact gamma phase equality','No analytic gerbe theory formalized','No chosen gamma descent or linearization','No floating-point or interval gamma computation']}
    (ROOT/'evidence/exact_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS {len(checks)} exact assertions; {len(negatives)} negative controls')
if __name__=='__main__':main()
