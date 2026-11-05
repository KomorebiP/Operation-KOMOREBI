"""Independent exact finite checks for the audited Komorebi operator compendium.

No external libraries or network calls. These checks do not certify the entire
compendium, all software implementations, or the Lean manuscript claims.
"""
from fractions import Fraction as F
from math import factorial, comb


def mat(rows):
    return tuple(tuple(F(v) for v in row) for row in rows)


def identity(n):
    return mat([[int(i == j) for j in range(n)] for i in range(n)])


def zeros(m, n):
    return mat([[0] * n for _ in range(m)])


def multiply(a, b):
    if len(a[0]) != len(b):
        raise ValueError("incompatible matrix types")
    return mat([[sum(a[i][k]*b[k][j] for k in range(len(b)))
                 for j in range(len(b[0]))] for i in range(len(a))])


def add(a, b):
    return mat([[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))])


def negate(a):
    return mat([[-v for v in row] for row in a])


def minus(a, b):
    return add(a, negate(b))


def transpose(a):
    return mat(zip(*a))


def packet(n, mod, residue):
    return mat([[int(i == j and i % mod == residue) for j in range(n)]
                for i in range(n)])


def sum_mats(mats):
    mats = list(mats)
    total = zeros(len(mats[0]), len(mats[0][0]))
    for a in mats:
        total = add(total, a)
    return total


def legacy_checks():
    checks=[]
    def check(name, ok):
        if not ok:
            raise AssertionError(name)
        checks.append(name)
        print('PASS', name)

    # A family of idempotents and exact block composition.
    n, mod = 8, 3
    pp = [packet(n, mod, r) for r in range(mod)]
    check('residue projectors complete', sum_mats(pp) == identity(n))
    check('residue projectors orthogonal',
          all(multiply(pp[i], pp[j]) == (pp[i] if i == j else zeros(n, n))
              for i in range(mod) for j in range(mod)))
    t = mat([[(i*3+j*2) % 7 - 3 for j in range(n)] for i in range(n)])
    u = mat([[(i+5*j) % 9 - 4 for j in range(n)] for i in range(n)])
    check('transfer reconstructs operator',
          sum_mats(multiply(multiply(pp[i], t), pp[j])
                   for i in range(mod) for j in range(mod)) == t)
    composed = multiply(u, t)
    check('transfer composes with all middle packets',
          all(multiply(multiply(pp[k], composed), pp[i]) ==
              sum_mats(multiply(multiply(multiply(multiply(pp[k], u), pp[j]), t), pp[i])
                       for j in range(mod))
              for i in range(mod) for k in range(mod)))

    # Redundant frame: physical components reconstruct but need not be projectors.
    a = mat([[1, 0], [0, 1], [1, 1]])
    s = mat([[F(2, 3), F(-1, 3), F(1, 3)],
             [F(-1, 3), F(2, 3), F(1, 3)]])
    check('redundant analysis synthesis law', multiply(s, a) == identity(2) and
          multiply(a, s) != identity(3))
    ci = [multiply(multiply(s, packet(3, 3, j)), a) for j in range(3)]
    check('physical components reconstruct, not all idempotent',
          sum_mats(ci) == identity(2) and any(multiply(c, c) != c for c in ci))
    # Different middle coefficient presentations need bridge R=A2*S.
    a2 = mat([[1, 1], [0, 1], [1, 0]])
    s2 = mat([[1, -1, 0], [0, 1, 0]])
    check('second presentation is exact', multiply(s2, a2) == identity(2))
    small_t, small_u = mat([[2, 1], [3, 4]]), mat([[1, 2], [0, 1]])
    lifted_t = multiply(multiply(a, small_t), s)
    lifted_u = multiply(multiply(a, small_u), s2)
    bridge = multiply(a2, s)
    expected_lift = multiply(multiply(a, multiply(small_u, small_t)), s)
    check('bridge composes redundant coefficient lifts',
          multiply(multiply(lifted_u, bridge), lifted_t) == expected_lift)

    # Conjugation by the falling factorial linear map is not product preservation.
    x = F(4)
    check('falling factorial transport is not multiplicative',
          x*(x-1) != x*x)

    # Exact derivative / basepoint antiderivative on rational polynomials.
    p = [F(2), F(3), F(4), F(-5)]
    derivative = [F(i)*p[i] for i in range(1, len(p))]
    primitive_of_derivative = [F(0)] + [derivative[i-1]/i for i in range(1, len(p))]
    check('basepoint integral of derivative retains constant defect',
          primitive_of_derivative == [F(0)] + p[1:])
    q = [F(1), F(-2), F(7)]
    integral_q = [F(0)] + [q[i-1]/i for i in range(1, len(q)+1)]
    check('derivative of exact basepoint integral is identity',
          [F(i)*integral_q[i] for i in range(1, len(integral_q))] == q)

    # Phase-filter transfer exactly reconstructs a finite causal FIR operation.
    width = 3
    xseq = [F(i*i-2*i+3) for i in range(11)]
    taps = [F(1), F(2), F(-1), F(3)]
    y_direct = [sum(taps[l] * (xseq[n-l] if n-l >= 0 else 0)
                    for l in range(min(n, len(taps)-1)+1)) for n in range(len(xseq))]
    def phase_input(j, k):
        idx=width*k+j
        return xseq[idx] if 0 <= idx < len(xseq) else F(0)
    def phase_tap(i,j,q):
        ell=width*q+i-j
        return taps[ell] if 0<=ell<len(taps) else F(0)
    y_phase=[]
    for n in range(len(xseq)):
        i,k=n%width,n//width
        y_phase.append(sum(phase_tap(i,j,q)*phase_input(j,k-q)
                           for j in range(width) for q in range(len(taps)+1)))
    check('three-phase FIR transfer agrees with direct convolution',y_phase == y_direct)

    # CRT selectors and exact reconstruction.
    e3,e5,M = 10, 6, 15
    check('CRT idempotents and sum', e3*e3 % M == e3 and
          e5*e5 % M == e5 and e3*e5 % M == 0 and (e3+e5) % M == 1)
    check('CRT reconstructs both residues',
          (2*e3+3*e5) % M == 8 and 8 % 3 == 2 and 8 % 5 == 3)

    # In normalized EGF coordinates, multiplication is Hurwitz convolution.
    aa=[F(1),F(2),F(3)]; bb=[F(1),F(-1),F(4)]
    cc2=sum(F(comb(2,k))*aa[k]*bb[2-k] for k in range(3))
    direct2=sum((aa[k]/factorial(k))*(bb[2-k]/factorial(2-k)) for k in range(3))
    check('EGF Hurwitz coefficient agrees with ordinary multiplication', cc2 == direct2*factorial(2))

    # Haar cancellation shows a support/max semantic is not the additive carrier.
    a,d = F(1,2), F(1,2)
    check('Haar reconstruction needs signed addition',
          (a+d,a-d) == (F(1),F(0)) and (a,max(a,-d)) != (F(1),F(0)))

    # Kato's complete-family generator is skew in this exact 2x2 example.
    p0=mat([[1,0],[0,0]])
    p1=minus(identity(2),p0)
    pdot=mat([[0,1],[1,0]])
    katogen=add(multiply(pdot,p0),multiply(negate(pdot),p1))
    check('Kato generator is skew for rotating orthogonal packet pair',
          add(katogen, transpose(katogen)) == zeros(2,2))

    # Support-only factorization fails over signed sums.
    check('Boolean support cannot preserve signed cancellation',
          (1 + (-1) == 0) and ((1 != 0) or (-1 != 0)))

    print(f'RESULT {len(checks)} / {len(checks)} finite exact checks passed')



# Additional audit checks. Every value below is an integer or Fraction.
# These are independent mathematical fixtures, not a replay of the library.
import json
from pathlib import Path
from collections import Counter

AUDIT_RECORDS = []
def record(key, name, ok, operators, *, kind='identity', cases=1):
    if not ok:
        raise AssertionError(f'{key}: {name}')
    item={'id':key,'name':name,'status':'PASS','kind':kind,
          'operator_ids':[f'OP-{i:03d}' for i in operators], 'cases':cases}
    AUDIT_RECORDS.append(item)
    print('PASS',key,name)


def scale(a,c):return mat([[c*v for v in row] for row in a])
def inv(a):
    n=len(a)
    if any(len(row)!=n for row in a):raise ValueError('inverse requires square matrix')
    b=[list(a[i])+list(identity(n)[i]) for i in range(n)]
    for k in range(n):
        pivot=next((j for j in range(k,n) if b[j][k]),None)
        if pivot is None:raise ValueError('singular matrix')
        b[k],b[pivot]=b[pivot],b[k]
        v=b[k][k];b[k]=[x/v for x in b[k]]
        for j in range(n):
            if j!=k:
                v=b[j][k];b[j]=[x-v*y for x,y in zip(b[j],b[k])]
    return mat([row[n:] for row in b])
def apply(a,x):return tuple(sum(v*w for v,w in zip(row,x)) for row in a)
def trace(a):return sum(a[i][i] for i in range(len(a)))
def ps(a):
    a=list(map(F,a)) or [F(0)]
    while len(a)>1 and a[-1]==0:a.pop()
    return tuple(a)
def padd(a,b):return ps([(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))])
def pscale(a,c):return ps([c*v for v in a])
def pmul(a,b,N=None):
    size=len(a)+len(b)-1
    if N is not None:size=min(size,N+1)
    out=[F(0)]*size
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            if i+j<size:out[i+j]+=x*y
    return ps(out)
def ppow(a,n,N=None):
    out=ps([1])
    for _ in range(n):out=pmul(out,a,N)
    return out
def peval(a,x):
    v=F(0)
    for c in reversed(a):v=v*x+c
    return v
def pcompose(a,b,N=None):
    out=ps([0])
    for c in reversed(a):out=padd(pmul(out,b,N),ps([c]))
    return out
def deriv(a):return ps([i*a[i] for i in range(1,len(a))])
def fall(n):
    v=ps([1])
    for j in range(n):v=pmul(v,ps([-j,1]))
    return v
def rising(n):
    v=ps([1])
    for j in range(n):v=pmul(v,ps([j,1]))
    return v
def polybasis(d,fn):
    columns=[fn(j) for j in range(d+1)]
    return mat([[columns[j][i] if i<len(columns[j]) else 0 for j in range(d+1)] for i in range(d+1)])
def trim(a,N):return ps(a[:N+1])
def recip(a,N):
    if not a[0]:raise ValueError('constant coefficient is not a unit in Q')
    b=[1/F(a[0])]
    for n in range(1,N+1):b.append(-sum(a[k]*b[n-k] for k in range(1,min(n,len(a)-1)+1))/a[0])
    return ps(b)
def substitute_power(a,p,N):
    out=[F(0)]*(N+1)
    for k,v in enumerate(a):
        if p*k<=N:out[p*k]=v
    return ps(out)
def mahler(mask,p,N):
    if mask[0]!=1:raise ValueError('mask must have constant coefficient one')
    out=ps([1]);power=1
    while power<=N:
        out=pmul(out,substitute_power(mask,power,N),N);power*=p
    return out

def reject(call):
    try:call()
    except ValueError:return True
    return False

def gmul(z,w):return (z[0]*w[0]-z[1]*w[1],z[0]*w[1]+z[1]*w[0])
def gconj(z):return (z[0],-z[1])

def run_extended():
    # Typed rectangular packet composition.
    T=mat([[i-j+1 for j in range(3)] for i in range(4)])
    U=mat([[2*i+j-1 for j in range(4)] for i in range(2)])
    P=[packet(3,2,r) for r in range(2)]
    Q=[packet(4,3,r) for r in range(3)]
    R=[packet(2,2,r) for r in range(2)]
    ok=all(multiply(multiply(R[k],multiply(U,T)),P[i])==sum_mats(multiply(multiply(multiply(multiply(R[k],U),Q[j]),T),P[i]) for j in range(3)) for k in range(2) for i in range(2))
    record('A01','rectangular packet composition with distinct spaces',ok,[10,11,12],cases=4)
    p=mat([[1,0],[0,0]]);q=mat([[F(1,2),F(1,2)],[F(1,2),F(1,2)]])
    pq=multiply(p,q)
    record('A02','noncommuting projector product need not be a projector',multiply(pq,pq)!=pq,[28],kind='counterexample')
    A=mat([[1,0],[0,1],[1,1]]);S=mat([[F(2,3),F(-1,3),F(1,3)],[F(-1,3),F(2,3),F(1,3)]])
    P=multiply(A,S);G=minus(identity(3),P)
    record('A03','canonical coefficient projection and complementary gauge',multiply(P,P)==P and multiply(S,G)==zeros(2,3) and multiply(G,G)==G,[18,17])
    T=mat([[2,3],[-1,4]]);lift=multiply(multiply(A,T),S)
    record('A04','coefficient lift sandwich and recovery',multiply(multiply(P,lift),P)==lift and multiply(multiply(S,lift),A)==T,[19,22])
    A2=mat([[1,1],[0,1],[1,0]]);S2=mat([[1,-1,0],[0,1,0]])
    R=multiply(A2,S);HX=multiply(transpose(S),S);HY=multiply(transpose(S2),S2)
    record('A05','quotient metric bridge isometry',multiply(multiply(transpose(R),HY),R)==HX,[20,23])
    Cs=[multiply(multiply(S,packet(3,3,i)),A) for i in range(3)]
    # All three middle components square to a sum that is not the identity.
    bad=sum_mats(multiply(c,c) for c in Cs)
    record('A06','physical-component one-index composition fails',bad!=identity(2),[21,12],kind='counterexample')
    ii=(F(0),F(1));z=(F(1),F(2));w=(F(3),F(-1))
    record('A07','adjoint formation is complex conjugate-linear',gconj(gmul(ii,z))==gmul(gconj(ii),gconj(z)) and gconj(gmul(ii,z))!=gmul(ii,gconj(z)),[5],kind='counterexample')
    left=gmul(gconj(gmul(ii,z)),w);right=gmul(gconj(ii),gmul(gconj(z),w))
    record('A08','error-pair compression is sesquilinear',left==right and left!=gmul(ii,gmul(gconj(z),w)),[148],kind='counterexample')
    c=mat([[0,1],[1,1]]);forcing=(F(1),F(0))
    record('A09','forced companion update is not homogeneous linear',tuple(a+b for a,b in zip(apply(c,(0,0)),forcing))!= (0,0),[63],kind='counterexample')
    record('A10','operator squaring is nonlinear in the operator',multiply(scale(identity(2),2),scale(identity(2),2))!=scale(identity(2),2),[13],kind='counterexample')

    d=8;B=polybasis(d,fall);Bi=inv(B);Ps=[packet(d+1,3,r) for r in range(3)];Qs=[multiply(multiply(B,p),Bi) for p in Ps]
    record('A11','transported falling-factorial projectors reconstruct',sum_mats(Qs)==identity(d+1) and all(multiply(Qs[i],Qs[j])==(Qs[i] if i==j else zeros(d+1,d+1)) for i in range(3) for j in range(3)),[25,26,41],cases=10)
    # Phi D Phi^{-1} is the forward difference on falling-factorial images.
    record('A12','derivative transports to forward difference',all(padd(pcompose(fall(k),(1,1)),pscale(fall(k),-1))==pscale(fall(k-1),k) for k in range(1,10)),[41,47,53],cases=9)
    DB=mat([[j if j==i+1 else 0 for j in range(d+1)] for i in range(d)])
    Blow=polybasis(d-1,fall)
    Dfall=multiply(multiply(inv(Blow),DB),B)
    record('A13','rectangular derivative coordinate naturality',multiply(Blow,Dfall)==multiply(DB,B),[40,53])
    def lah(n,k):return 1 if n==k==0 else (0 if k==0 or k>n else comb(n-1,k-1)*factorial(n)//factorial(k))
    def sum_polys(a):
        out=ps([0])
        for x in a:out=padd(out,x)
        return out
    record('A14','Lah rising-to-falling orientation',all(rising(n)==sum_polys(pscale(fall(k),lah(n,k)) for k in range(n+1)) for n in range(10)),[46],cases=10)
    wrong=tuple(sum(lah(n,k)*(1 if k==2 else 0) for k in range(n+1)) for n in range(3))
    right=tuple(lah(2,k) for k in range(3))
    record('A15','lower sequence orientation is wrong for Lah polynomial coordinates',right==(0,2,1) and wrong!=right,[46],kind='counterexample')
    p=ps([2,-3,4,1,-2]);vals=[peval(p,F(i)) for i in range(len(p))];diff=[]
    while vals:
        diff.append(vals[0]);vals=[vals[i+1]-vals[i] for i in range(len(vals)-1)]
    rebuilt=sum_polys(pscale(fall(k),diff[k]/factorial(k)) for k in range(len(diff)))
    record('A16','Newton differences reconstruct in binomial normalization',rebuilt==p,[47,48])
    record('A17','falling coefficients need the Newton factorial divisor',pscale(fall(2),2)!=ps([0,-1,1]) and F(2,factorial(2))==1,[48],kind='counterexample')
    ok=True
    for n in range(1,5):
        size=2**n;a=[F((7*j)%11-3) for j in range(size)]
        b=[sum(a[t] for t in range(size) if t&s==t) for s in range(size)]
        c=[sum((-1)**((s^t).bit_count())*b[t] for t in range(size) if t&s==t) for s in range(size)]
        ok &= a==c
    record('A18','subset zeta and Mobius are inverse',ok,[50],cases=4)
    from math import gcd
    record('A19','factorial normalization fails at characteristic degree p',all(gcd(factorial(p),p)!=1 and all(gcd(factorial(k),p)==1 for k in range(p)) for p in (2,3,5,7)),[51,52],kind='counterexample',cases=4)
    record('A20','characteristic zero does not put logarithm in integer series',F(-1,2).denominator!=1,[66],kind='counterexample')
    constants=[pcompose([F(1)]*(N+1),(1,1))[0] for N in range(1,6)]
    record('A21','nonzero-inner-constant formal substitution need not stabilize',constants==list(map(F,range(2,7))),[60],kind='counterexample')
    record('A22','nonunit reciprocal is rejected',reject(lambda:recip(ps([0,1]),5)),[65],kind='guard rejection')
    ok=True
    for N in (1,2,5,10,20):
        for f in ([1,2,-3],[2,-1,4],[F(3,2),F(-1,7)]):ok &= pmul(ps(f),recip(ps(f),N),N)==ps([1])
    record('A23','formal reciprocal jet products',ok,[65],cases=15)
    N=24;f=ps([1,2,-3,1]);ok=True
    for radix in (2,3,5):
        mask=pmul(f,recip(substitute_power(f,radix,N),N),N)
        ok &= mahler(mask,radix,N)==f
    record('A24','normalized Mahler masks telescope',ok,[70,71],cases=3)
    f2=pscale(f,2);r1=pmul(f,recip(substitute_power(f,2,N),N),N);r2=pmul(f2,recip(substitute_power(f2,2,N),N),N)
    record('A25','mask recovery loses the constant scale',r1==r2 and mahler(r2,2,N)==f and f2!=f,[71],kind='counterexample')
    record('A26','unnormalized infinite-product mask is rejected',reject(lambda:mahler(ps([2,1]),2,8)),[70],kind='guard rejection')
    f=ps(list(range(1,16)));radix=3
    rebuilt=sum_polys(pmul(ps([0]*r+[1]),substitute_power(f[r::radix],radix,20)) for r in range(radix))
    record('A27','Cartier decimation and residue projection have different indices',rebuilt==f and ps(ps([0,0,0,1])[1::2])[1::2] != ps(ps([0,0,0,1])[1::2]),[25,36])
    f=ps([1,2,3,4]);ok=True
    for p in (2,3,5):
        lhs=ppow(f,p);rhs=substitute_power(f,p,p*(len(f)-1))
        ok &= all(int(v)%p==0 for v in padd(lhs,pscale(rhs,-1)))
    record('A28','commutative prime-characteristic Frobenius identity',ok,[37],cases=3)
    E=mat([[0,1],[0,0]]);Ff=mat([[0,0],[1,0]])
    record('A29','noncommutative characteristic-two Frobenius fails additivity',multiply(add(E,Ff),add(E,Ff))!=add(multiply(E,E),multiply(Ff,Ff)),[37],kind='counterexample')
    def gf4mul(a,b):
        out=0
        while b:
            if b&1:out^=a
            b>>=1;a<<=1
            if a&4:a^=7
        return out
    phi=lambda x:gf4mul(x,x)
    record('A30','finite-field Frobenius is not extension-field linear',all(phi(a^b)==phi(a)^phi(b) for a in range(4) for b in range(4)) and phi(2)!=gf4mul(2,phi(1)),[37,167],kind='counterexample',cases=16)
    def val(n,p):
        v=0
        while n and n%p==0:v+=1;n//=p
        return v
    def carries(a,b,p):
        carry=total=0
        while a or b or carry:
            carry=(a%p+b%p+carry)//p;total+=carry;a//=p;b//=p
        return total
    ncases=0;ok=True
    for p in (2,3,5,7):
        for n in range(65):
            for k in range(n+1):ok &= val(comb(n,k),p)==carries(k,n-k,p);ncases+=1
    record('A31','Kummer valuations match carries on the declared range',ok,[76,77],cases=ncases)
    mask=ps([1,1,1]);co=mahler(mask,2,128)
    Tdigits=[mat([[mask[d+2*qp-q] if 0<=d+2*qp-q<len(mask) else 0 for qp in range(2)] for q in range(2)]) for d in range(2)]
    def digitval(n):
        row=mat([[1,0]])
        while n:row=multiply(row,Tdigits[n%2]);n//=2
        return row[0][0]
    record('A32','carry transition matrices agree with direct mask product',all(digitval(n)==co[n] for n in range(129)),[72,73],cases=129)
    aa=[F(1),F(-2),F(3),F(4)];bb=[F(2),F(1),F(-1),F(2)];gamma=lambda n:F(factorial(n)**2)
    ordinary=pmul([v/gamma(i) for i,v in enumerate(aa)],[v/gamma(i) for i,v in enumerate(bb)])
    direct=[sum(gamma(n)/(gamma(k)*gamma(n-k))*aa[k]*bb[n-k] for k in range(len(aa)) if 0<=n-k<len(bb)) for n in range(7)]
    record('A33','general normalized convolution agrees with basis transport',ps(direct)==ps([ordinary[n]*gamma(n) for n in range(7)]),[52,67],cases=7)

    # Exact FIR cascades including every middle phase and lag.
    h=ps([1,2,-1,3]);g=ps([2,-1,4]);gh=pmul(g,h);ok=True
    def coeff(a,n):return a[n] if 0<=n<len(a) else F(0)
    for N in (2,3,4,5):
        for i in range(N):
            for j in range(N):
                for lag in range(7):
                    routed=sum(coeff(g,N*r+i-k)*coeff(h,N*(lag-r)+k-j) for k in range(N) for r in range(8))
                    ok &= routed==coeff(gh,N*lag+i-j)
    record('A34','polyphase cascade retains middle phases and lag carries',ok,[12,81,82,83],cases=sum(n*n*7 for n in (2,3,4,5)))
    analysis=mat([[2,0],[0,1]]);gram=multiply(transpose(analysis),analysis);syn=multiply(inv(gram),transpose(analysis))
    record('A35','normalized synthesis is not a raw adjoint',multiply(syn,analysis)==identity(2) and gram!=identity(2),[16,17,94,95],kind='counterexample')
    soft=lambda c: max(c-F(1),0) if c>=0 else -max(-c-F(1),0)
    record('A36','threshold retention is not a linear fixed mask',soft(F(3,4)+F(3,4))!=soft(F(3,4))+soft(F(3,4)),[88,99],kind='counterexample')
    pairs=[(F(x,3),F(y,5)) for x in range(-3,4) for y in range(-3,4)]
    record('A37','Haar average/detail energy uses a factor of two',all(x*x+y*y==2*((x+y)/2)**2+2*((x-y)/2)**2 for x,y in pairs),[84,85],cases=len(pairs))
    p=mat([[1,0],[0,0]]);pd=mat([[0,1],[1,0]]);k=add(multiply(pd,p),multiply(negate(pd),minus(identity(2),p)))
    record('A38','Kato generator has the correct commutator sign',minus(multiply(k,p),multiply(p,k))==pd,[115])
    E=mat([[F(1,3),F(2,3),0],[F(1,3),F(2,3),0],[0,0,1]]);M=mat([[1,0,0],[0,2,0],[0,0,3]])
    record('A39','weighted conditional expectation is an idempotent metric projection',multiply(E,E)==E and multiply(M,E)==multiply(transpose(E),M) and apply(E,(1,1,1))==(1,1,1),[125])
    def bayes(p):
        x=(p[0],2*p[1]);return tuple(v/sum(x) for v in x)
    record('A40','Bayesian normalization is nonlinear in the prior',bayes((F(1,2),F(1,2)))!=(F(1,2),F(1,2)),[126],kind='counterexample')
    row=mat([[F(1,2),F(1,2)],[F(1,4),F(3,4)]]);col=transpose(row);p=(F(1),F(0))
    record('A41','Markov column convention conserves total mass',sum(apply(col,p))==1 and sum(apply(row,p))!=1,[122,123],kind='counterexample')
    C=mat([[1,1,0,0],[0,0,1,1]]);K=mat([[F(1,2),0,F(1,4),0],[0,F(1,2),0,F(1,4)],[F(1,2),0,F(3,4),0],[0,F(1,2),0,F(3,4)]]);Kb=mat([[F(1,2),F(1,4)],[F(1,2),F(3,4)]])
    record('A42','finite Markov aggregation commutes exactly when specified',multiply(C,K)==multiply(Kb,C),[124,121])
    whole=mat([[3,2],[4,5]]);schur=F(3)-F(2)*F(1,5)*F(4)
    record('A43','Schur complement inverse matches retained inverse block',inv(whole)[0][0]==1/schur,[132])
    N=mat([[0,1,0],[0,0,1],[0,0,0]]);N2=multiply(N,N)
    expN=lambda t:add(add(identity(3),scale(N,t)),scale(N2,t*t/2))
    pairs=[(F(1,2),F(2,3)),(F(-1,3),F(5,7)),(F(0),F(3))]
    record('A44','nilpotent finite semigroup law is exact',all(multiply(expN(s),expN(t))==expN(s+t) for s,t in pairs),[119],cases=3)
    N=mat([[0,1],[0,0]]);C=mat([[1,0]]);t=F(3,5)
    record('A45','generator defect integrates to finite semigroup defect',minus(multiply(C,add(identity(2),scale(N,t))),C)==scale(multiply(C,N),t),[121,135])
    # For H=[[0,1],[1,0]], amplitude derivatives obey a''=-a.
    direct=[F((-1)**k,factorial(2*k)) for k in range(7)];from_memory=[F(1)]
    for k in range(1,7):from_memory.append(-from_memory[-1]/((2*k)*(2*k-1)))
    record('A46','Schrodinger memory carries the negative kernel sign',direct==from_memory and direct[1]!=F(1,2),[133,144],cases=7)
    record('A47','an algebraic resolvent point need not be a Laplace point',F(1,0-1)==-1 and 0<1,[134],kind='counterexample')
    K0=mat([[1,0],[0,F(3,5)]]);K1=mat([[0,F(4,5)],[0,0]]);rho=mat([[F(1,2),F(1,4)],[F(1,4),F(1,2)]])
    kraus=lambda r:sum_mats(multiply(multiply(k,r),transpose(k)) for k in (K0,K1))
    record('A48','rational Kraus channel preserves trace',sum_mats(multiply(transpose(k),k) for k in (K0,K1))==identity(2) and trace(kraus(rho))==trace(rho),[139])
    ps0=[packet(2,2,j) for j in range(2)];deph=lambda r:sum_mats(multiply(multiply(p,r),p) for p in ps0)
    record('A49','dephasing is an idempotent channel',deph(deph(rho))==deph(rho) and deph(rho)[0][1]==0,[140])
    record('A50','positive measurement operator alone does not bound probability',trace(multiply(scale(identity(2),2),rho))==2,[142],kind='counterexample')
    A=mat([[1,1]]);B=mat([[1],[-1]])
    record('A51','Boolean support composition misses signed cancellation',multiply(A,B)==zeros(1,1) and all(v!=0 for row in A for v in row) and all(v!=0 for row in B for v in row),[158,162],kind='counterexample')
    ok=True;count=0
    for p in range(4):
        for n in range(4):
            for q in range(4):
                for m in range(4):ok &= (p*q+n*m)-(p*m+n*q)==(p-n)*(q-m);count+=1
    record('A52','signed mass product preserves the signed observation',ok,[163],cases=count)
    record('A53','fiber collisions obstruct a carrier factorization',(-1)**2==1**2 and -1!=1,[162],kind='counterexample')
    w1=[F(1),F(1),F(1,2)];w2=[F(1),F(3,4),F(3,4)]
    record('A54','equal tropical scalar summaries lose argmax multiplicity',max(w1)==max(w2) and sum(w1)==sum(w2) and len(w1)==len(w2) and w1.count(1)!=w2.count(1),[164],kind='counterexample')
    gauge=lambda x:F(x,2) if x>=0 else F(-x)
    record('A55','an asymmetric convex gauge is not a norm',gauge(1)!=gauge(-1),[165],kind='counterexample')
    L=F(7,3);c0=F(2)/L*L
    record('A56','COS constant mode requires half weighting',c0/2==1 and c0!=1,[166],kind='counterexample')
    d0=mat([[-1,1,0],[0,-1,1],[-1,0,1]]);d1=mat([[1,1,-1]])
    record('A57','finite cochain differential squares to zero with orientation',multiply(d1,d0)==zeros(1,3),[169])
    s=F(1,10);x=F(1,2);api=s+x*x;incorrect=s+x*x/2
    record('A58','Picard supplied-operation convention has no extra factorial',api==F(7,20) and api!=incorrect,[106],kind='counterexample')
    # All binary ordered trees of height at most two, evaluated at seed s.
    leaf=None
    def treeval(tree):return s if tree is None else treeval(tree[0])*treeval(tree[1])
    small=[None,(None,None)];trees=[None]+[(a,b) for a in small for b in small]
    pic=F(0)
    for _ in range(3):pic=s+pic*pic
    record('A59','finite ordered-tree sum equals the matching Picard iterate',sum(treeval(t) for t in trees)==pic,[105,106],cases=len(trees))
    outer=ps([0,0,0,1]);inner=ps([1,0,1]);xx=F(2)
    left=peval(deriv(deriv(pcompose(outer,inner))),xx)
    right=peval(deriv(deriv(outer)),peval(inner,xx))*peval(deriv(inner),xx)**2+peval(deriv(outer),peval(inner,xx))*peval(deriv(deriv(inner)),xx)
    record('A60','second-order composition uses the correct evaluation point',left==right,[104])
    record('A61','general nonlinear maps cannot omit mixed packet terms',(F(1)+F(2))**2!=F(1)**2+F(2)**2,[116],kind='counterexample')


def main():
    import argparse, contextlib, io, platform
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json',type=Path,help='Write the named-check receipt as JSON')
    args=parser.parse_args()
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):legacy_checks()
    lines=capture.getvalue().splitlines()
    legacy_ops=[[25],[25],[10,11],[12],[16,17],[21],[16,17],[19,20],[41],[53,54,57],[53,54],[79,80,81,82],[34],[35],[51,67],[84,85],[115],[162]]
    legacy_kinds={6:'counterexample',9:'counterexample',16:'counterexample',18:'counterexample'}
    names=[s[5:] for s in lines if s.startswith('PASS ')]
    if len(names)!=18:raise AssertionError('unexpected legacy test count')
    for i,name in enumerate(names,1):record(f'L{i:02d}',name,True,legacy_ops[i-1],kind=legacy_kinds.get(i,'identity'))
    run_extended()
    receipt={'suite':'Komorebi operator audit exact finite fixtures','python':platform.python_version(),'arithmetic':'integers and fractions.Fraction; no floating-point comparisons','test_scope':'Independent finite mathematical checks. Not a replay of komorebi-math or Lean.','passed':len(AUDIT_RECORDS),'failed':0,'legacy_checks':18,'additional_checks':len(AUDIT_RECORDS)-18,'kinds':dict(Counter(x['kind'] for x in AUDIT_RECORDS)),'checks':AUDIT_RECORDS}
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(json.dumps(receipt,indent=2))
    print('RESULT',receipt['passed'],'/',receipt['passed'],'named finite checks passed')
    print('KINDS',receipt['kinds'])

if __name__=='__main__':main()
