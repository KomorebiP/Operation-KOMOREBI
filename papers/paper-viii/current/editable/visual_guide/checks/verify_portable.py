#!/usr/bin/env python3
"""Independent exact replay of displayed models; Python standard library only.

This is a second implementation, not a replacement for the saved SymPy suite.
Its matrices are constructed directly from the printed definitions. It checks
finite instances and negative controls; it neither establishes universal
optimality nor executes Lean or a numerical/GPU factorization.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import hashlib, json, platform
ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class G:
    """An exact element of Q(i)."""
    a: Q = Q(0)
    b: Q = Q(0)
    def __post_init__(self):
        object.__setattr__(self, 'a', Q(self.a))
        object.__setattr__(self, 'b', Q(self.b))
    @staticmethod
    def co(x): return x if isinstance(x, G) else G(x)
    def __eq__(self,x):
        if isinstance(x,(int,Q)):x=G(x)
        if not isinstance(x,G):return NotImplemented
        return self.a==x.a and self.b==x.b
    def __add__(self, x):
        x = G.co(x); return G(self.a+x.a, self.b+x.b)
    __radd__ = __add__
    def __neg__(self): return G(-self.a,-self.b)
    def __sub__(self,x): return self+-G.co(x)
    def __rsub__(self,x): return G.co(x)+-self
    def __mul__(self,x):
        x=G.co(x);return G(self.a*x.a-self.b*x.b,self.a*x.b+self.b*x.a)
    __rmul__=__mul__
    def __truediv__(self,x):
        x=G.co(x);d=x.a*x.a+x.b*x.b
        if not d:raise ZeroDivisionError('Gaussian rational division by zero')
        return self*G(x.a/d,-x.b/d)
    def __rtruediv__(self,x):return G.co(x)/self
    def __pow__(self,n):
        if n<0:return (G(1)/self)**(-n)
        v=G(1)
        for _ in range(n):v=v*self
        return v
    def conj(self):return G(self.a,-self.b)
    def abs2(self):return self.a*self.a+self.b*self.b
    def __str__(self):return f'{self.a}+({self.b})i'

def M(rows):return [[Q(x) if not isinstance(x,G) else x for x in r] for r in rows]
def Z(m,n=None):return M([[0]*(m if n is None else n) for _ in range(m)])
def I(n):return M([[int(i==j) for j in range(n)] for i in range(n)])
def T(A):return [list(r) for r in zip(*A)]
def H(A):return [[x.conj() if isinstance(x,G) else x for x in r] for r in T(A)]
def mul(A,B):
    assert len(A[0])==len(B)
    return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def add(A,B):return [[a+b for a,b in zip(ar,br)] for ar,br in zip(A,B)]
def scale(A,x):return [[x*a for a in r] for r in A]
def sub(A,B):return add(A,scale(B,-1))
def power(A,n):
    out=I(len(A))
    for _ in range(n):out=mul(out,A)
    return out
def diag(xs):return [[x if i==j else Q(0) for j in range(len(xs))] for i,x in enumerate(xs)]
def col(xs):return M([[x] for x in xs])
def concat(A,B):return [a+b for a,b in zip(A,B)]
def kron(A,B):return [[A[i][j]*B[k][l] for j in range(len(A[0])) for l in range(len(B[0]))] for i in range(len(A)) for k in range(len(B))]
def vec(A):return col([A[i][j] for j in range(len(A[0])) for i in range(len(A))])
def fro2(A):return sum(x.abs2() if isinstance(x,G) else x*x for row in A for x in row)
def inverse(A):
    n=len(A);B=concat(A,I(n))
    for c in range(n):
        pivot=next((i for i in range(c,n) if B[i][c]!=0),None)
        if pivot is None:raise ValueError('singular matrix')
        B[c],B[pivot]=B[pivot],B[c];v=B[c][c];B[c]=[x/v for x in B[c]]
        for i in range(n):
            if i!=c:
                v=B[i][c];B[i]=[x-v*y for x,y in zip(B[i],B[c])]
    return [r[n:] for r in B]
def determinant(A):
    n=len(A)
    if n==1:return A[0][0]
    return sum((-1)**j*A[0][j]*determinant([r[:j]+r[j+1:] for r in A[1:]]) for j in range(n))
def rank(A):
    B=[r[:] for r in A];r=0
    for c in range(len(A[0])):
        p=next((i for i in range(r,len(B)) if B[i][c]!=0),None)
        if p is None:continue
        B[r],B[p]=B[p],B[r];v=B[r][c];B[r]=[x/v for x in B[r]]
        for i in range(r+1,len(B)):
            v=B[i][c];B[i]=[x-v*y for x,y in zip(B[i],B[r])]
        r+=1
        if r==len(B):break
    return r
def circulant(xs):return M([[xs[(i-j)%len(xs)] for j in range(len(xs))] for i in range(len(xs))])
def walsh(n):
    if n<1 or n&(n-1):raise ValueError('power of two required')
    A=[[Q(1)]]
    while len(A)<n:A=concat(A,A)+concat(A,scale(A,-1))
    return A
def stages(xs):
    n=len(xs)
    if not n or n&(n-1):raise ValueError('power of two required')
    a=list(xs);out=[a[:]];h=1
    while h<n:
        for j in range(0,n,2*h):
            for k in range(j,j+h):p,q=a[k],a[k+h];a[k]=p+q;a[k+h]=p-q
        out.append(a[:]);h*=2
    return out

OPTIONS=(((0,7),(2,3),(4,1)),((0,6),(1,4),(3,1)),((0,9),(2,5),(5,1)))
@dataclass(frozen=True)
class Node:
    name:str
    cost:int
    error:int
    overhead:int=0
    children:tuple=()
def tree():return Node('r',1,6,1,(Node('a',3,2,0,(Node('a0',2,0),Node('a1',2,0))),Node('b',3,2,0,(Node('b0',2,0),Node('b1',3,0)))))
def prunings(n):
    out=[(n.cost,n.error,(n.name,))]
    if n.children:
        for parts in product(*(prunings(c) for c in n.children)):
            out.append((n.overhead+sum(p[0] for p in parts),sum(p[1] for p in parts),sum((p[2] for p in parts),())))
    return out
def lagrange(n,l):
    keep=(n.cost+l*n.error,(n.name,))
    if not n.children:return keep
    cs=[lagrange(c,l) for c in n.children]
    return min(keep,(n.overhead+sum(c[0] for c in cs),sum((c[1] for c in cs),())))
def budget(n):
    out={n.error:(n.cost,(n.name,))}
    if n.children:
        acc={0:(n.overhead,())}
        for c in n.children:
            nxt={}
            for w,(cost,labels) in acc.items():
                for z,(cc,ll) in budget(c).items():
                    v=(cost+cc,labels+ll)
                    if w+z not in nxt or v<nxt[w+z]:nxt[w+z]=v
            acc=nxt
        for w,v in acc.items():
            if w not in out or v<out[w]:out[w]=v
    return out
def values(n,l):
    out={n.name:lagrange(n,l)[0]}
    for c in n.children:out.update(values(c,l))
    return out
def changed(n,name,cost):return replace(n,cost=cost) if n.name==name else replace(n,children=tuple(changed(c,name,cost) for c in n.children))
def ceil(x):return -((-x.numerator)//x.denominator)
checks=[];controls=[]
def check(name,ok,pages):
    if not bool(ok):raise AssertionError(name)
    checks.append({'name':name,'visual_pages':pages,'passed':True})
def eq(name,a,b,pages):check(name,a==b,pages)
def reject(name,ok,pages):
    if bool(ok):raise AssertionError('Invalid control accepted: '+name)
    controls.append({'name':name,'visual_pages':pages,'rejected':True})

def main():
    # Printed six-dimensional input, with direct construction of every entry.
    D=M([[3 if i==j else int(i//2==j//2) for j in range(6)] for i in range(6)])
    u=col([1]*6);x=col([1,-1,2,0,-2,3]);A=add(D,mul(u,T(u)))
    Ps=[diag([int(j//2==i) for j in range(6)]) for i in range(3)]
    eq('projector partition',add(add(Ps[0],Ps[1]),Ps[2]),I(6),[2,3])
    for i,P in enumerate(Ps):
        eq(f'projector {i} idempotence',mul(P,P),P,[2])
        for j,R in enumerate(Ps):
            if i!=j:eq(f'projector {i},{j} annihilation',mul(P,R),Z(6),[2])
    full=Z(6)
    for P in Ps:
        for R in Ps:full=add(full,mul(mul(P,A),R))
    eq('full block reconstruction',full,A,[2,3]);eq('all 36 entries nonzero',sum(v!=0 for r in A for v in r),36,[3])
    eq('global contraction',mul(T(u),x),[[Q(3)]],[3]);eq('local vector',mul(D,x),col([2,-2,6,2,-3,7]),[3])
    y=mul(A,x);eq('factored application',add(mul(D,x),mul(u,mul(T(u),x))),y,[3]);eq('displayed result',y,col([5,1,9,5,0,10]),[3])
    eq('storage count',3*4+2*6,24,[4])
    for q in (1,2,4,8):eq(f'operation ratio q={q}',Q(72*q,48*q),Q(3,2),[4])
    for p in range(1,7):
        for w in range(p):eq(f'band count p={p},w={w}',sum(abs(i-j)<=w for i in range(p) for j in range(p)),p*(2*w+1)-w*(w+1),[4])
    # Gaussian-rational Fourier and explicitly complex tensor input.
    ii=G(0,1);F=[[ii**(-j*k)/2 for k in range(4)] for j in range(4)]
    c=col([2,1,0,-1]);C=circulant([2,1,0,-1]);lam=scale(mul(F,c),2);xc=col([1,2,-1,0])
    eq('Fourier isometry',mul(H(F),F),[[G(v) for v in r] for r in I(4)],[5])
    eq('Fourier multipliers',lam,col([G(2),G(2,-2),G(2),G(2,2)]),[5])
    decoded=mul(mul(H(F),diag([r[0] for r in lam])),F)
    eq('circulant reconstruction',decoded,[[G(v) for v in r] for r in C],[5]);eq('circulant output',mul(decoded,xc),col([G(0),G(6),G(0),G(-2)]),[5])
    reject('missing unitary convolution scale',mul(mul(H(F),diag([r[0] for r in mul(F,c)])),F)==decoded,[5])
    TT=M([[2,-1,5],[3,2,-1],[4,3,2]]);xt=col([1,2,-1]);Cg=circulant([2,3,4,0,5,-1])
    eq('padded Toeplitz output',mul(Cg,xt+col([0,0,0]))[:3],mul(TT,xt),[6]);eq('Toeplitz displayed vector',mul(TT,xt),col([-5,8,8]),[6])
    reject('unpadded circulant shortcut',mul(circulant([2,3,4]),xt)==mul(TT,xt),[6])
    KA=M([[1,ii],[2,-1]]);KB=M([[2,1],[0,3]]);XX=M([[1,2],[3,4]])
    expected=M([[G(5,8),2],[G(9,12),6]])
    eq('complex Kronecker coordinate output',mul(mul(KB,XX),T(KA)),expected,[7]);eq('column-major Kronecker identity',mul(kron(KA,KB),vec(XX)),vec(expected),[7])
    reject('adjoint replaces vectorization transpose',mul(mul(KB,XX),H(KA))==expected,[7])
    for n in (1,2,4,8,16):
        W=walsh(n);xs=col(range(1,n+1));ss=stages(list(range(1,n+1)))
        eq(f'Walsh orthogonality n={n}',mul(W,T(W)),scale(I(n),n),[8]);eq(f'Walsh stages n={n}',col(ss[-1]),mul(W,xs),[8])
        eq(f'Walsh operation count n={n}',n*(len(ss)-1),n*(n.bit_length()-1),[8])
    reject('unnormalized Walsh norm preservation',fro2(mul(walsh(8),col(range(1,9))))==fro2(col(range(1,9))),[8])
    DB=diag(range(1,7));ub=col([1,0,1,0,1,0]);vb=col([0,1,0,1,0,1]);B=add(DB,mul(ub,T(vb)))
    UC=concat(add(mul(D,ub),mul(u,mul(T(u),ub))),u);VC=concat(vb,mul(T(DB),u));AB=mul(A,B)
    eq('BDLR product cross term',add(mul(D,DB),mul(UC,T(VC))),AB,[9,27]);check('correction rank at most two',rank(sub(AB,mul(D,DB)))<=2,[9])
    shortcut=add(add(mul(D,DB),mul(mul(D,ub),T(vb))),mul(mul(u,T(u)),DB))
    reject('drop quadratic low-rank term',shortcut==AB,[9])
    invD=inverse(D);S=add(I(1),mul(mul(T(u),invD),u));WB=sub(invD,mul(mul(mul(mul(invD,u),inverse(S)),T(u)),invD))
    eq('Woodbury denominator',S,[[Q(5,2)]],[10]);eq('Woodbury left inverse',mul(WB,A),I(6),[10]);eq('Woodbury right inverse',mul(A,WB),I(6),[10])
    eq('determinant through small denominator',determinant(A),determinant(D)*determinant(S),[10]);reject('diagonal invertibility implies update invertibility',determinant(diag([0,1]))!=0,[10])
    QL=M([[Q(3,5),0],[Q(4,5),0],[0,1],[0,0]]);RL=M([[1,0,1],[0,1,0]]);RR=M([[3,0,2],[0,2,0],[1,0,-1]])
    L=mul(QL,RL);core=mul(RL,T(RR));ambient=mul(L,T(RR));Ak=mul(QL,M([[5,0,0],[0,0,0]]))
    eq('range isometry',mul(T(QL),QL),I(2),[11]);eq('actual rectangular core',core,M([[5,0,0],[0,2,0]]),[11]);eq('core ambient reconstruction',mul(QL,core),ambient,[11])
    eq('left range dimension',rank(L),2,[11]);eq('right range dimension',rank(RR),3,[11]);eq('core and ambient rank',rank(core),rank(ambient),[11]);eq('rank-one approximation',rank(Ak),1,[12])
    eq('rank-one squared Frobenius error',fro2(sub(ambient,Ak)),4,[12]);eq('residual Gram',mul(T(sub(ambient,Ak)),sub(ambient,Ak)),diag([0,4,0]),[12]);eq('rank-zero squared Frobenius error',fro2(ambient),29,[12])
    outside=Z(4,3);outside[3][2]=Q(1);eq('outside competitor compression',mul(T(QL),outside),Z(2,3),[12]);eq('outside competitor squared error',fro2(sub(ambient,outside)),30,[12])
    DD=diag([5,2,1]);KK=M([[0,0],[1,0],[0,1]]);eq('kernel weighted tail',fro2(mul(DD,KK)),5,[12]);eq('diagonal competitor kills kernel frame',mul(diag([4,0,0]),KK),Z(3,2),[12])
    ee=[Q(1,10),Q(1,5),Q(1,20)];pp=Q(1);hp=Q(1)
    for a,e in zip([2,3,4],ee):pp*=a;hp=a*hp+e
    eq('additive chain error',hp-pp,Q(41,20),[13]);eq('factor perturbation error',(2+ee[0])*(3+ee[1])*(4+ee[2])-24,Q(402,125),[13])
    reject('unweighted additive errors are final bound',hp-pp<=sum(ee),[13])
    K=Z(4)
    for i,j,z in [(1,0,1),(2,0,1),(3,1,1),(3,2,-1)]:K[i][j]=Q(z)
    eq('diamond cancellation',power(K,2),Z(4),[14,30]);support=M([[int(v!=0) for v in r] for r in K]);eq('two structural routes',power(support,2)[3][0],2,[14])
    edges=((0,2),(1,2),(1,3),(2,4),(3,4),(3,5),(4,6),(5,6));AD=scale(I(7),2)
    for a,z in edges:AD[z][a]=Q(-1)
    xd=mul(inverse(AD),col([1]*7));eq('DAG solve values',xd,col([Q(1,2),Q(1,2),1,Q(3,4),Q(11,8),Q(7,8),Q(13,8)]),[15]);eq('DAG solve residual',mul(AD,xd),col([1]*7),[15])
    done=set();levels=[]
    while len(done)<7:
        ready=[z for z in range(7) if z not in done and all(a in done for a,b in edges if b==z)]
        if not ready:raise AssertionError('DAG unexpectedly cyclic')
        levels.append(ready);done.update(ready)
    eq('DAG unit-duration stages',levels,[[0,1],[2,3],[4,5],[6]],[15]);eq('strict transfer nilpotent',power(sub(AD,scale(I(7),2)),4),Z(7),[15])
    for cancel in (False,True):
        off=Q(1,2) if cancel else Q(0);AS=M([[2,off,1],[off,2,1],[1,1,2]]);SC=M([[Q(3,2),off-Q(1,2)],[off-Q(1,2),Q(3,2)]])
        eq(f'Schur retained inverse cancel={cancel}',[r[:2] for r in inverse(AS)[:2]],inverse(SC),[16])
    vv=col([1,1]);eq('linked Krylov dimension',rank(concat(vv,mul(I(2),vv))),1,[17]);eq('distinct spectral Krylov dimension',rank(concat(vv,mul(diag([1,2]),vv))),2,[17]);reject('invariant packet inclusion always equality',rank(concat(vv,vv))==2,[17])
    PA=M([[4,1],[1,1]]);PB=diag([Q(1,2),1]);PN=mul(mul(PB,PA),PB)
    eq('preconditioned matrix',PN,M([[1,Q(1,2)],[Q(1,2),1]]),[18]);eq('preconditioned positive eigenvector',mul(PN,col([1,1])),col([Q(3,2),Q(3,2)]),[18]);eq('preconditioned negative eigenvector',mul(PN,col([1,-1])),col([Q(1,2),-Q(1,2)]),[18]);eq('condition number',Q(3,2)/Q(1,2),3,[18])
    ER=scale(sub(M([[1]*4 for _ in range(4)]),I(4)),Q(1,100));eq('discovery Frobenius square',fro2(ER),Q(3,2500),[19]);eq('coherent error eigenvector',mul(ER,col([1]*4)),col([Q(3,100)]*4),[19])
    for j in range(1,4):
        w=[0]*4;w[0]=1;w[j]=-1;eq(f'orthogonal error eigenvector {j}',mul(ER,col(w)),scale(col(w),-Q(1,100)),[19])
    reject('maximum block error bounds total operator error',Q(3,100)<=Q(1,100),[19])
    sens=[1,2,4];costs=[1,1,2];eps=[Q(1,4),Q(1,8),Q(1,8)]
    eq('continuous budget',sum(a*b for a,b in zip(sens,eps)),1,[20])
    for j in range(3):eq(f'continuous multiplier {j}',costs[j]/(eps[j]*sens[j]),4,[20])
    caps=[Q(1,10),Q(1,2),Q(1,2)];clip=[Q(1,10),Q(3,20),Q(3,20)];eq('clipped budget',sum(a*b for a,b in zip(sens,clip)),1,[20])
    for j in range(3):eq(f'clipped water filling {j}',min(caps[j],Q(costs[j])/(Q(10,3)*sens[j])),clip[j],[20])
    enum=[(sum(OPTIONS[i][a][0] for i,a in enumerate(sel)),sum(OPTIONS[i][a][1] for i,a in enumerate(sel)),sel) for sel in product(range(3),repeat=3)]
    tables=[{0:(0,())}]
    for opts in OPTIONS:
        nxt={}
        for w,(c,sel) in tables[-1].items():
            for k,(wk,ck) in enumerate(opts):
                cand=(c+ck,sel+(k,))
                if w+wk not in nxt or cand<nxt[w+wk]:nxt[w+wk]=cand
        tables.append(nxt)
    eq('precision assignment count',len(enum),27,[21])
    for b in range(13):
        opt=min(v for w,v in tables[-1].items() if w<=b);direct=min((c,sel) for w,c,sel in enum if w<=b)
        eq(f'precision optimum budget={b}',opt,direct,[21]);check(f'precision selector feasible budget={b}',sum(OPTIONS[i][a][0] for i,a in enumerate(opt[1]))<=b,[21])
    eq('precision displayed budget four',min(v for w,v in tables[-1].items() if w<=4),(14,(1,0,1)),[21])
    tr=tree();rows=prunings(tr);eq('all five tree prunings',[(c,e) for c,e,_ in rows],[(1,6),(7,4),(9,2),(8,2),(10,0)],[22])
    for l in (0,Q(1,2),1,Q(3,2),2,4):eq(f'penalty recurrence lambda={l}',lagrange(tr,l)[0],min(c+l*e for c,e,_ in rows),[22])
    bt=budget(tr)
    for b in range(7):eq(f'tree exact budget={b}',min(c for w,(c,_) in bt.items() if w<=b),min(c for c,e,_ in rows if e<=b),[22])
    eq('unsupported optimum budget two',min(c for c,e,_ in rows if e<=2),8,[22]);check('incompatible multiplier interval',Q(7,4)>1,[22])
    old=values(tr,2);new=values(changed(tr,'a0',3),2);eq('local update affected values',{k for k in old if old[k]!=new[k]},{'a0','a','r'},[23]);eq('local update root',new['r'],11,[23]);check('strict score stability',13-Q(7,5)>10+Q(7,5),[23]);reject('half-gap equality preserves strict ordering',13-Q(3,2)>10+Q(3,2),[23])
    for q,val in [(1,240),(4,672)]:eq(f'one-pass bytes q={q}',8*3*(4+2*q+4*q),val,[24])
    for r in range(1,12):eq(f'amortization R={r}',30+2*r<7*r,r>6,[25])
    eq('first strict improvement',min(r for r in range(1,20) if 30+2*r<7*r),7,[25]);reject('ceiling gives strict threshold at integral ratio',30+2*6<7*6,[25])
    eq('synthetic raw timing ratio',Q(12,2),6,[26]);eq('synthetic decoded timing ratio',Q(12,14),Q(6,7),[26]);reject('omit required decoding in explicit-output speedup',2+12<12,[26])
    eq('product thin contraction',mul(T(VC),x),col([2,13]),[27]);eq('product local contribution',mul(mul(D,DB),x),col([1,-5,18,6,-12,44]),[27]);eq('product correction',mul(UC,mul(T(VC),x)),col([25,21,25,21,25,21]),[27]);eq('dense independent product result',mul(AB,x),col([26,16,43,27,13,65]),[27])
    # New complex range example: every inner product uses conjugation.
    CQ=M([[Q(3,5),0],[G(0,Q(4,5)),0],[0,1]]);RQ=diag([G(1),ii]);CG=diag([5,2]);CA=mul(mul(CQ,CG),H(RQ));C1=mul(mul(CQ,diag([5,0])),H(RQ))
    eq('complex left isometry',mul(H(CQ),CQ),[[G(v) for v in r] for r in I(2)],[29]);eq('complex right isometry',mul(H(RQ),RQ),[[G(v) for v in r] for r in I(2)],[29]);eq('complex ambient matrix',CA,M([[G(3),G(0)],[G(0,4),G(0)],[G(0),G(0,-2)]]),[29]);eq('complex ambient Gram',mul(H(CA),CA),[[G(v) for v in r] for r in diag([25,4])],[29]);eq('complex rank-one error square',fro2(sub(CA,C1)),4,[29]);eq('complex residual Gram',mul(H(sub(CA,C1)),sub(CA,C1)),diag([0,4]),[29]);eq('complex rank-one output',rank(C1),1,[29]);reject('transpose isometry in complex core',mul(T(CQ),CQ)==I(2),[29])
    # Inverse computed by elimination, compared with the nilpotent formula.
    AI=add(I(4),K);inv=inverse(AI);eq('inverse nilpotent formula',inv,sub(I(4),K),[30]);eq('reachable but cancelled inverse entry',inv[3][0],0,[30])
    reach=[[i==j or K[i][j]!=0 for j in range(4)] for i in range(4)]
    for k in range(4):
        for i in range(4):
            for j in range(4):reach[i][j]=reach[i][j] or (reach[i][k] and reach[k][j])
    check('inverse outside closure is zero',all(inv[i][j]==0 for i in range(4) for j in range(4) if not reach[i][j]),[30]);check('closure contains cancelled transfer',reach[3][0],[30]);reject('reachability guarantees nonzero inverse',inv[3][0]!=0,[30])
    # Shared family: two admissible prunings, declared additive setup terms.
    for r in range(5):
        keep=4+2+7*r;split=2+8+2*r
        eq(f'shared family first reuse r={r}',split<keep,r>=1,[31])
    eq('shared family keep r2=3',4+2+3*7,27,[31]);eq('shared family split r2=3',2+8+3*2,16,[31])
    eq('isolated operator one preference',min((2,'keep'),(8,'split'))[1],'keep',[31]);eq('isolated operator two preference',min((7,'keep'),(2,'split'))[1],'split',[31])
    # Integerization is safe but may exclude real-feasible points.
    h=Q(1,10);errs=[Q(3,50),Q(2,25)];ws=[ceil(e/h) for e in errs]
    eq('ceiling weights',ws,[1,1],[21,32]);check('ceiling upper envelope',sum(errs)<=h*sum(ws),[21,32]);reject('floor rounding is conservative',sum(errs)<=h*sum(e//h for e in errs),[21,32]);eq('false floor certificate real sum',sum(errs),Q(7,50),[32])
    safe=[Q(3,50),Q(1,50)];check('real-feasible conservative rejection',sum(safe)<=h and sum(ceil(e/h) for e in safe)>1,[32]);eq('budget255 state count',255+1,256,[32]);eq('budget255 bit length',(255).bit_length(),8,[32]);eq('direct pair comparison bound',(255+1)**2,65536,[32])
    report={'status':'PASS','scope':'Finite displayed models only; independent exact stdlib replay. No universal theorem, Lean, numerical QR/SVD, CPU/GPU timing, or historical SymPy rerun.',
      'arithmetic_domains':['integers','fractions.Fraction: Q','G: Q(i)'],'positive_assertions':len(checks),'negative_controls_rejected':len(controls),'checks':checks,'invalid_controls':controls,
      'tested_bounds':{'band_packet_count':[1,6],'Walsh_dimensions':[1,2,4,8,16],'precision_assignments':27,'precision_budgets':[0,12],'tree_prunings':5,'tree_budgets':[0,6],'penalty_values':['0','1/2','1','3/2','2','4'],'reuse_counts':[1,11],'shared_second_operator_reuse':[0,4]},
      'covered_visual_pages':sorted({p for c in checks+controls for p in c['visual_pages']}),'python_version':platform.python_version(),
      'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'source_pages_sha256':hashlib.sha256((ROOT/'source/pages.tex').read_bytes()).hexdigest(),
      'extension_pages_sha256':hashlib.sha256((ROOT/'source/extended_pages.tex').read_bytes()).hexdigest(),
      'values':{'running_y':[str(r[0]) for r in y],'precision_budget4':[14,[1,0,1]],'tree_prunings':rows,'triangular_solution':[str(r[0]) for r in xd],'complex_core_matrix':[[str(v) for v in r] for r in CA]}}
    (ROOT/'checks/PORTABLE_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(checks)} exact positive assertions; {len(controls)} invalid controls rejected.')
if __name__=='__main__':main()
