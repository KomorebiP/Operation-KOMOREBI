#!/usr/bin/env python3
"""Independent, finite exact-arithmetic checks of the stated Paper IX objects.

This is a bounded consistency gate, not a substitute for any universal proof,
Lean compilation, completed p-adic root, or analytic theorem. No dependencies
outside Python's standard library. All deterministic input bounds are literal.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from math import comb, factorial, gcd, lcm
from pathlib import Path
import argparse
import json

COUNTS = Counter()
CONTROLS = []
GROUPS = {}

def check(group, assertion):
    if not assertion:
        raise AssertionError(f'Finite assertion failed in {group}, assertion {COUNTS[group]+1}')
    COUNTS[group] += 1

def control(name, false_assertion, witness):
    if false_assertion:
        raise AssertionError(f'Invalid strengthening survived: {name}')
    CONTROLS.append({'name': name, 'status': 'REJECTED', 'witness': witness})

def vp(p, x):
    x = Q(x)
    if x == 0:
        return None  # extended infinity, never the finite valuation zero
    a, b, v = abs(x.numerator), x.denominator, 0
    while a % p == 0:
        a //= p
        v += 1
    while b % p == 0:
        b //= p
        v -= 1
    return v

def precise(p, x, depth):
    v = vp(p, x)
    return v is None or v >= depth

def diff(a, n, h, k):
    return sum(((-1)**(k-i)*comb(k,i)*a[n+i*h] for i in range(k+1)), Q(0))

@lru_cache(None)
def packet(N, j, end):
    a = [Q(1)]
    for n in range(1, end+1):
        a.append(-sum((comb(N*n+j,N*q)*a[q] for q in range(n)), Q(0))/comb(N*n+j,N*n))
    return tuple(a)

def convolution(a,b,end,hurwitz=True):
    return [sum((Q(comb(n,r) if hurwitz else 1)*a[r]*b[n-r] for r in range(n+1)), Q(0)) for n in range(end+1)]

def inverse_series(a,end):
    if a[0] == 0:
        raise ValueError('constant coefficient must be nonzero')
    b = [1/Q(a[0])]
    for n in range(1,end+1):
        b.append(-sum((a[i]*b[n-i] for i in range(1,n+1)),Q(0))/a[0])
    return b

def foundations():
    g='foundation_identities'
    for N in range(1,7):
        for n in range(18):
            bits=[int(n%N==j) for j in range(N)]
            check(g,sum(bits)==1 and all(x*x==x for x in bits))
            for M in (N,2*N,3*N):
                check(g,all(bits[j]==sum(int(n%M==r) for r in range(M) if r%N==j) for j in range(N)))
    for aexp in range(5):
        for M in (1,3,5,7):
            for n in range(2**aexp*M+2):
                check(g,(n%(2**aexp*M)==0)==(n%2**aexp==0 and n%M==0))
    for case in range(8):
        a=[Q((n+case)**2-3*n, n%3+1) for n in range(25)]
        c=[diff(a,0,1,r) for r in range(25)]
        for n in range(15):
            check(g,sum(c[r]*comb(n,r) for r in range(n+1))==a[n])
            for s in range(5):
                check(g,diff(a,n,1,s)==sum(c[s+j]*comb(n,j) for j in range(n+1)))
        for h in range(5):
            for k in range(5):
                check(g,diff(a,0,h,k)==sum((-1)**(k-j)*comb(k,j)*a[j*h] for j in range(k+1)))
    for case in range(5):
        a=[Q(case+n*n) for n in range(24)]
        b=[Q((-1)**n*(n+1)) for n in range(24)]
        ab=convolution(a,b,23)
        for d in range(5):
            for n in range(12):
                rhs=sum(comb(d,r)*sum(comb(n,i)*a[i+r]*b[n-i+d-r] for i in range(n+1)) for r in range(d+1))
                check(g,ab[n+d]==rhs)
    for p in (2,3,5):
        for u,v in product(range(1,p),repeat=2):
            hs=[(2*pow(u,n,p)-pow(v,n,p))%p for n in range(32)]
            inv=[1]
            for n in range(1,32):inv.append((-sum(comb(n,r)*inv[r]*hs[n-r] for r in range(n)))%p)
            for n in range(25):
                check(g,sum(comb(n,r)*inv[r]*hs[n-r] for r in range(n+1))%p==int(n==0))
            for n in range(24):check(g,inv[n+p]==inv[n+1])
        for u in range(1,10):
            if u%p==0:continue
            a=[u**n for n in range(24)]
            for n in range(5):
                for k in range(4):
                    check(g,diff(a,n,p-1,k)==u**n*(u**(p-1)-1)**k)
                    check(g,precise(p,diff(a,n,p-1,k),k))
        for L in range(4):
            modulus=p**(L+1)
            for a in range(modulus):
                if gcd(a,p)!=1: continue
                omega=pow(a,p**L,modulus)
                principal=a*pow(omega,-1,modulus)%modulus
                check(g,(omega*principal)%modulus==a and pow(omega,p-1,modulus)==1%modulus and principal%p==1%p)
                candidates=[w for w in range(modulus) if pow(w,p-1,modulus)==1%modulus and w%p==a%p]
                check(g,candidates==[omega])
        for L in range(4):
            modulus=2**(L+2)
            for a in range(1,modulus,2):
                sign=1 if a%4==1 else -1
                check(g,(sign*a)%4==1 and (sign*(sign*a))%modulus==a)
    # Fibonacci recurrence derived from the observable, independently of packet construction.
    fib=[0,1]
    for n in range(180): fib.append(fib[-1]+fib[-2])
    for N in range(13):
        lucas=2 if N==0 else fib[N-1]+fib[N+1]
        for j in range(7):
            for k in range(10):
                check(g,fib[N*(k+2)+j]==lucas*fib[N*(k+1)+j]-(-1)**N*fib[N*k+j])
    # Empty state, empty polynomial vector and zero step are included elsewhere.
    for case in range(5):
        solved=[];clearing=1
        for n in range(13):
            diagonal=(-1)**n*(1+(n+case)%3)
            row=[(-1)**(n+q)*(n+2*q+case) for q in range(n)]+[diagonal]
            rhs=n*n-case
            solved.append((rhs-sum(row[q]*solved[q] for q in range(n)))/Q(diagonal))
            clearing*=diagonal
            check(g,sum(row[q]*solved[q] for q in range(n+1))==rhs and (clearing*solved[n]).denominator==1)
    for p in (2,3,5):
        for n in range(15):
            for L in range(9):
                terms=[comb(n,r)*(-1)**r*p**(2*r)*(n-r+1) for r in range(n+1)]
                check(g,(sum(terms)-sum(terms[r] for r in range(n+1) if 2*r<L))%p**L==0)
    control('factorial division unavailable in characteristic p',pow(factorial(3),1,3)!=0,{'p':3,'3_factorial_mod_p':0})
    control('finite samples force a universal tail',diff([Q(0)]*5+[Q(1)],0,1,5)==0,{'samples_at_0_through_4':'all zero','order_5_coefficient':1})
    GROUPS[g]={'domain':'exact rational coefficients and finite residue rings','bounds':'N=1..6, n<18; Mahler eight 25-sample families; Hurwitz five families,d<=4,n<12 plus finite-characteristic inverses p2,3,5,all nonzero u,v,n<=24; unit modes u1..9 coprime to p,n<=4,k<=3; unit coordinates p2,3,5,L<=3; Fibonacci N<=12,j<=6,k<10; five triangular systems rows0..12; filtration p2,3,5,n0..14,L0..8'}

def arithmetic():
    g='packet_construction'
    for N in range(1,9):
        for j in range(N):
            a=packet(N,j,16)
            denom=1
            # Independently invert the ordinary EGF source before factorial decoding.
            source=[Q(0)]*(N*16+1)
            for n in range(17): source[N*n]=Q(factorial(j),factorial(N*n+j))
            inv=inverse_series(source,N*16)
            for n in range(17):
                denom*=comb(N*n+j,N*n)
                check(g,sum(comb(N*n+j,N*q)*a[q] for q in range(n+1))==int(n==0))
                check(g,(denom*a[n]).denominator==1)
                check(g,inv[N*n]*factorial(N*n)==a[n])
            check(g,all(inv[d]==0 for d in range(len(inv)) if d%N))
    GROUPS[g]={'domain':'Fraction','bounds':'N=1..8, all j<N, rows0..16; reciprocal EGF degree<=128','independent_check':'ordinary power-series inversion versus cleared binomial recurrence'}
    g='divisor_congruences'
    tuples=[]
    for p in (2,3,5):
        for m in range(1,p):
            if (p-1)%m: continue
            N,h=m*p,(p-1)//m
            end=max(60,6+2*p*(p-1)//m)
            arrays=[packet(N,j,end) for j in range(N)]
            tuples.append([p,m,N])
            for j,a in enumerate(arrays):
                U=[factorial(j)*x for x in a]
                for n in range(7):
                    check(g,precise(p,U[n],0))
                    if j<p:
                        check(g,precise(p,a[n],0) and precise(p,a[n]-arrays[0][n],1))
                    for u in (0,1,2,p):
                        for k in range(3):
                            bound=min(k*(1+(vp(p,u) if u else 0)),m*n)
                            check(g,precise(p,diff(U,n,u*h,k),bound))
                            check(g,precise(p,diff(a,n,u*h,k),bound-vp(p,factorial(j))))
                for r in (1,2):
                    step=lcm(2,p-1)*p**(r-1)//m
                    for n in range(r,7):
                        check(g,precise(p,U[n+step]-U[n],r))
                for n in range(8):
                    for q in range(n+1):
                        if j<p:check(g,(comb(N*n+j,N*q)-comb(m*n,m*q))%p==0)
    GROUPS[g]={'domain':'Fraction with exact numerator/denominator valuations','families':tuples,'bounds':'all addresses j<N; n0..6, k0..2,u in{0,1,2,p}; Nishibuchi r1,2,n=r..6; Lucas n0..7','non_claim':'The starting-index and all-order theorem are not decided by this finite range.'}
    control('omit factorial normalization loss',precise(3,diff(packet(6,3,3),1,1,1),1),{'N':6,'j':3,'n':1,'difference':str(diff(packet(6,3,3),1,1,1)),'v3':vp(3,diff(packet(6,3,3),1,1,1))})
    control('odd divisor branch bound starts at row zero',precise(3,packet(6,0,1)[1]-1,1),{'N':6,'j':0,'row0_difference':str(packet(6,0,1)[1]-1),'v3':vp(3,packet(6,0,1)[1]-1)})
    g='four_packet_sharpness'
    c=[1,1,4,2];d=[1,1,5,3]
    prefix={0:{2:3},1:{2:3},2:{2:6,3:9,4:13,5:16,6:22},3:{2:8,3:8,4:15}}
    for j in range(4):
        a=packet(4,j,80);U=[factorial(j)*x for x in a]
        for k,val in prefix[j].items():check(g,vp(2,diff(a,0,1,k))==val)
        for n in range(9):
            for T in range(1,65):
                check(g,vp(2,a[n+T]-a[n])==vp(2,T)+c[j])
                check(g,vp(2,U[n+T]-U[n])==vp(2,T)+d[j])
        for n in range(7):
            for u in (0,1,2,4,8):
                for k in range(5):
                    check(g,precise(2,diff(a,n,u,k),k*(1+(vp(2,u) if u else 0))))
        for r in range(7):
            least=2**max(0,r-d[j])
            observed=[]
            for T in range(1,65):
                is_period=all(precise(2,U[n+T]-U[n],r) for n in range(9))
                check(g,is_period==(T%least==0))
                if is_period:observed.append(T)
            check(g,min(observed)==least)
        # normalized images are permutations at each tested finite depth.
        for L in range(1,6):
            vals=[]
            for n in range(2**L):
                z=(a[n]-1)/2**c[j]
                vals.append(z.numerator*pow(z.denominator,-1,2**L)%2**L)
            check(g,sorted(vals)==list(range(2**L)))
    GROUPS[g]={'domain':'Fraction; exact v2; unit-denominator residues','bounds':'j0..3,n0..8,T1..64; higher differences n0..6,k0..4,u0,1,2,4,8; periods r0..6; image bijections L1..5','non_claim':'Finite residue bijections do not construct an infinite p-adic isometry.'}
    control('all four normalized gains equal one',vp(2,packet(4,2,1)[1]-1)==1,{'j':2,'gain':4})
    control('allow T=0 in nonzero displacement',packet(4,0,0)[0]-packet(4,0,0)[0]!=0,{'T':0,'difference':0,'extended_valuation':'infinity'})

def classical():
    g='classical_truncations'
    end=24
    e=[Q(0)]*(2*end+1)
    for n,a in enumerate(packet(2,0,end)):e[2*n]=a
    gamma=[convolution(e,e,2*end)[2*m] for m in range(end+1)]
    kernel=[Q(2**(2*m+1),factorial(2*m+2)) for m in range(end+1)]
    beta=inverse_series(kernel,end)
    # Bernoulli numbers from an unrelated formal source (e^z-1)/z.
    B=[x*factorial(i) for i,x in enumerate(inverse_series([Q(1,factorial(i+1)) for i in range(2*end+1)],2*end))]
    A=[Q(3**(2*n+2)-1,4*(2*n+1)*(2*n+2)) for n in range(end+1)]
    for n in range(end+1):
        check(g,vp(2,A[n])==0 and precise(2,beta[n],0))
        check(g,packet(2,1,end)[n]==(2-2**(2*n))*B[2*n])
        summands=[beta[m]*2**(2*m)*Q(factorial(2*n),factorial(2*n-2*m))*A[n-m] for m in range(n+1)]
        check(g,sum(summands,Q(0))==e[2*n])
        for m in range(1,n+1):
            check(g,vp(2,summands[m])==4*m-1+vp(2,comb(2*n,2*m)))
        for M in range(end+2):
            error=e[2*n]-sum(summands[:min(M,n)+1],Q(0))
            check(g,precise(2,error,4*M+3))
            if M>=n:check(g,error==0)
            if n==M+1:check(g,vp(2,error)==4*M+3)
    for m in range(1,end+1):
        kappa=beta[m]*2**(2*m)*factorial(2*m)
        check(g,kappa==-2**(4*m)*(2*m-1)*B[2*m] and vp(2,kappa)==4*m-1)
    for p in (1,3,5,7,9):
        for n in range(15):
            terms=[comb(2*n,2*m)*gamma[m]*p**(2*m)*sum((-1)**a*(2*a+1)**(2*(n-m)) for a in range(p)) for m in range(n+1)]
            check(g,sum(terms,Q(0))==e[2*n])
            for M in range(16):
                err=e[2*n]-sum(terms[:min(M,n)+1],Q(0))
                check(g,err.denominator==1 and err.numerator%p**(2*M+2)==0)
    err=e[2]-A[1]
    control('uniform dyadic tail gains an extra digit',precise(2,err,4),{'M':0,'n':1,'error':str(err),'v2':vp(2,err),'guaranteed_depth':3})
    p=2;n=0
    control('odd reconstruction also holds for even source length',sum((-1)**a*(2*a+1)**(2*n) for a in range(p))==e[0],{'source_length':2,'n':0,'source_sum':0,'Euler':1})
    GROUPS[g]={'domain':'Fraction; exact integer divisibility','bounds':'classical rows0..24 and M0..25; first-omitted rows1..24; odd lengths1,3,5,7,9,rows0..14,M0..15','independent_check':'sech reciprocal versus dyadic inverse and Bernoulli reciprocal'}

# Polynomials are dictionaries exponent tuple -> integer coefficient. Evaluation
# and formal derivatives are independent explicit loops, with zero dimensions.
def peval(P,x):
    return sum(c*product_int(xi**ei for xi,ei in zip(x,e)) for e,c in P.items())

def product_int(xs):
    v=1
    for x in xs:v*=x
    return v

def jacobian(F,x):
    return [[sum(c*e[j]*product_int(xi**(ei-int(i==j)) for i,(xi,ei) in enumerate(zip(x,e))) for e,c in P.items() if e[j]) for j in range(len(x))] for P in F]

def feval(F,x):return tuple(peval(P,x) for P in F)
def mvec(A,u,q):return tuple(sum(a*b for a,b in zip(row,u))%q for row in A)
def addvec(a,b,q):return tuple((x+y)%q for x,y in zip(a,b))
def vectors(q,d):return list(product(range(q),repeat=d))

def rank_prime(A,p,d):
    rows=[[a%p for a in row] for row in A];r=0
    for col in range(d):
        pivot=next((i for i in range(r,len(rows)) if rows[i][col]),None)
        if pivot is None:continue
        rows[r],rows[pivot]=rows[pivot],rows[r]
        scale=pow(rows[r][col],-1,p)
        rows[r]=[(x*scale)%p for x in rows[r]]
        for i in range(len(rows)):
            if i!=r:
                scale=rows[i][col]
                rows[i]=[(a-scale*b)%p for a,b in zip(rows[i],rows[r])]
        r+=1
    return r

SYSTEMS=[
 ('empty_space_zero',0,[{():0}]),('empty_space_constant',0,[{():2}]),('empty_equations',2,[]),
 ('x',1,[{(1,):1}]),('square_minus_one',1,[{(2,):1,(0,):-1}]),
 ('square',1,[{(2,):1}]),('cube_minus_x',1,[{(3,):1,(1,):-1}]),
 ('nonunit_affine',1,[{(1,):2,(0,):-2}]),
 ('sum',2,[{(1,0):1,(0,1):1}]),('circle',2,[{(2,0):1,(0,2):1,(0,0):-1}]),
 ('graph',2,[{(2,0):1,(0,1):1}]),('hyperbola',2,[{(1,1):1,(0,0):-1}]),
 ('two_equations',2,[{(2,0):1,(0,0):-1},{(0,1):1,(1,0):-1}]),
 ('zero_equation_added',2,[{(1,0):1},{}]),
]

def polynomial_fibers():
    g='polynomial_digit_fibers'
    root_centers=0;digits=0
    for name,d,F in SYSTEMS:
        for q in (1,2,3,4):
            for L in (1,2):
                QL=q**L;target=q**(L+1);us=vectors(q,d)
                for x in vectors(QL,d):
                    fx=feval(F,x);J=jacobian(F,x)
                    # Taylor divisibility at every tested center, including nonroots.
                    for u in us:
                        y=tuple(a+QL*b for a,b in zip(x,u));fy=feval(F,y)
                        check(g,all((b-a-QL*sum(j*v for j,v in zip(row,u)))%(QL**2)==0 for a,b,row in zip(fx,fy,J)))
                    if any(v%QL for v in fx):continue
                    root_centers+=1
                    r=tuple(v//QL for v in fx)
                    image={mvec(J,u,q) for u in us}
                    zero=(0,)*len(F)
                    linear=[];actual=[]
                    for u in us:
                        y=tuple(a+QL*b for a,b in zip(x,u));fy=feval(F,y)
                        linear_ok=addvec(tuple(v%q for v in r),mvec(J,u,q),q)==zero
                        actual_ok=all(v%target==0 for v in fy)
                        check(g,linear_ok==actual_ok);digits+=1
                        if linear_ok:linear.append(u)
                        if actual_ok:actual.append(tuple(v%target for v in y))
                    check(g,bool(linear)==(tuple((-v)%q for v in r) in image))
                    check(g,len(set(actual))==len(linear))
                    kernel={u for u in us if mvec(J,u,q)==zero}
                    if linear:
                        shifts={tuple((a-b)%q for a,b in zip(u,linear[0])) for u in linear}
                        check(g,shifts==kernel and len(linear)==len(kernel))
                    if q in (2,3):
                        rank=rank_prime(J,q,d)
                        check(g,len(kernel)==q**(d-rank) and len(image)==q**rank)
                        check(g,(q**len(F))//len(image)==q**(len(F)-rank))
                    # Representative independence: a complete digit set of representatives.
                    for s in us:
                        xp=tuple(a+QL*b for a,b in zip(x,s));fxp=feval(F,xp)
                        Jp=jacobian(F,xp)
                        check(g,all((a-b)%q==0 for row,prow in zip(J,Jp) for a,b in zip(row,prow)))
                        check(g,all((b//QL-a//QL-j)%q==0 for a,b,j in zip(fx,fxp,mvec(J,s,q))))
                    if d==2:
                        solved=1;Jsol=[row[:1] for row in J];K=[row[1:] for row in J]
                        for v in range(q):
                            restricted=[u for u in linear if u[1]==v]
                            shifted=addvec(tuple(z%q for z in r),mvec(K,(v,),q),q)
                            solimage={mvec(Jsol,(u,),q) for u in range(q)}
                            check(g,bool(restricted)==(tuple((-z)%q for z in shifted) in solimage))
                            if q in (2,3) and restricted:check(g,len(restricted)==q**(1-rank_prime(Jsol,q,1)))
    GROUPS[g]={'domain':'exact integer polynomial evaluation and finite rings Z/qZ','systems':[s[0] for s in SYSTEMS],'bounds':'q1,2,3,4,L1,2; all canonical centers mod q^L and all correction digits; d0,1,2; e0,1,2','root_centers':root_centers,'correcting_digit_cases':digits,'non_claim':'Rank cardinality asserted only over q2,3, never composite4.'}
    F=[{(2,):1,(0,):-1}];x=(0,);q=2
    residual=feval(F,x)[0]
    linear=any((residual+jacobian(F,x)[0][0]*u)%q==0 for u in range(q))
    actual=any(peval(F[0],(u,))%q==0 for u in range(q))
    control('nonlinear depth zero obstruction',linear==actual,{'F':'X^2-1','q':2,'L':0,'x':0,'residual_class':1,'Jacobian':0,'root_mod2':1})
    # Check this control from actual evaluation, not only its prose witness.
    check(g,peval({(2,):1,(0,):-1},(1,))%2==0 and peval({(2,):1,(0,):-1},(0,))%2==1)
    control('full Jacobian surjectivity permits arbitrary prescribed parameter digit',any((0+2*1)%4==0 for _ in range(2)),{'F':'T','full_J':[0,1],'solved_J':[0],'p':2,'L':1,'v':1})
    control('rectangular surjectivity implies endpoint uniqueness',(0,0,0)==(0,2,0),{'F':'Y1','same_parameters':0,'roots_in_dyadic_ball':[[0,0,0],[0,2,0]]})
    control('prime-field rank counts apply to composite modulus',len([u for u in range(4) if 2*u%4==0])==1,{'q':4,'J':[2],'kernel':[0,2]})

def affine_shared():
    g='shared_affine_quotient'
    for q in (1,2,3,4,5):
        U=vectors(q,2)
        maps=[[[a,b]] for a in range(q) for b in range(q)]
        # All map pairs for q<=3; six deterministically chosen pairs for q4,5.
        pairs=list(product(maps,maps)) if q<=3 else [(maps[i],maps[-1-i]) for i in range(6)]
        for J,K in pairs:
            kerJ=[u for u in U if mvec(J,u,q)==(0,)]
            kerK=[u for u in U if mvec(K,u,q)==(0,)]
            killed={addvec(a,b,q) for a in kerJ for b in kerK}
            for u in U:
                for v in U:
                    equivalent=tuple((a-b)%q for a,b in zip(u,v)) in killed
                    common=any(mvec(J,w,q)==mvec(J,u,q) and mvec(K,w,q)==mvec(K,v,q) for w in U)
                    check(g,equivalent==common)
    # Affine L=0..2, arbitrary q positive including q=1.
    for q in (1,2,3,4):
        for L in range(3):
            for A,b in product(range(-2,3),repeat=2):
                for x in range(-3,4):
                    fx=A*x-b
                    if fx%q**L:continue
                    for u in range(q):
                        check(g,((A*(x+q**L*u)-b)%q**(L+1)==0)==((fx//q**L+A*u)%q==0))
    control('individually solvable corrections are always shared',any(w%2==0 and w%2==1 for w in range(2)),{'q':2,'J':1,'K':1,'required_digits':[0,1]})
    GROUPS[g]={'domain':'finite modules (Z/qZ)^2 plus exact integer affine evaluation','bounds':'q1..5; all one-row map pairs for q<=3, six pairs q4,5; all u,v; affine q1..4,L0..2,A,b=-2..2,x=-3..3','non_claim':'A finite quotient implementation does not establish unrestricted native descent.'}

def towers_charts():
    g='finite_towers_and_charts'
    for p in (2,3,5):
        # Start at (0,0), prescribe exact integer representatives of tau=p/(p+1).
        x=t=0;rows=[]
        for n in range(6):
            N=1+n;modulus=p**N
            nextmod=p**(N+1)
            tn=p*pow(p+1,-1,nextmod)%nextmod
            delta=(tn-t)//modulus
            check(g,(tn-t)%modulus==0)
            r=(x+x*x+t)//modulus
            corrections=[u for u in range(p) if (r+(1+2*x)*u+delta)%p==0]
            check(g,len(corrections)==1)
            xn=x+modulus*corrections[0]
            check(g,(xn+xn*xn+tn)%nextmod==0 and (xn-x)%modulus==0 and (1+2*xn)%p==1)
            rows.append([xn,tn,N+1]);x,t=xn,tn
        for a in range(len(rows)):
            for b in range(a,len(rows)):
                check(g,all((rows[b][i]-rows[a][i])%p**rows[a][2]==0 for i in (0,1)))
    # Nonlinear local square inverse, over two different primes and centers.
    for p,center,kind in ((2,0,'x+x2'),(3,1,'x2')):
        f=lambda x:x+x*x if kind=='x+x2' else x*x
        for N in range(1,5):
            mod=p**N
            xs=[x for x in range(mod) if x%p==center%p]
            images=[f(x)%mod for x in xs]
            check(g,len(set(images))==len(xs))
            check(g,set(images)=={y for y in range(mod) if (y-f(center))%p==0})
            for x in xs:
                for y in xs:
                    for r in range(N+1):
                        check(g,((x-y)%p**r==0)==((f(x)-f(y))%p**r==0))
    # Finite root chart for an approximate, not exact, dyadic center.
    for N in range(1,6):
        mod=2**N;ts=list(range(0,mod,2));chart={}
        for t in ts:
            roots=[x for x in range(0,mod,2) if (x+x*x+t-2)%mod==0]
            check(g,len(roots)==1);chart[t]=roots[0]
        for t in ts:
            for t2 in ts:
                for r in range(N+1):
                    check(g,((t-t2)%2**r==0)==(all((a-b)%2**r==0 for a,b in zip((chart[t],t),(chart[t2],t2)))))
    control('approximate center implies chart value equals center',any(x==0 for x in range(0,8,2) if (x+x*x-2)%8==0),{'F':'Y+Y^2+T-2','center':[0,0],'L':1,'roots_at_T0_mod8':[x for x in range(0,8,2) if (x+x*x-2)%8==0]})
    GROUPS[g]={'domain':'exact integer representatives; finite residue roots','bounds':'six compatible correcting stages for primes2,3,5; square inverse depths1..4; approximate-center root chart depths1..5','non_claim':'Finite towers do not compute their p-adic limits or establish continuity/analyticity of an infinite chart.'}

def weighted_motion():
    g='weighted_and_deformation'
    cases=0
    for p in (2,3):
        for s in range(3):
            for r in (2*s+1,2*s+2):
                N=max(r-s+2,2*s+3);mod=p**N
                for coeff in (1,-1):
                    roots=[x for x in range(0,mod,p**(s+1)) if (p**s*x+x*x+coeff*p**r)%mod==0]
                    check(g,len(roots)==p**s)
                    check(g,all(x%p**(r-s)==0 for x in roots))
                    check(g,all((x-roots[0])%p**(N-s)==0 for x in roots))
                    cases+=1
            for M in (2*s+1,2*s+2):
                E=2*M-3*s;N=E+s+1;mod=p**N
                roots=[x for x in range(0,mod,p**(s+1)) if (p**s*x+x*x+p**M*(1+x))%mod==0]
                check(g,len(roots)==p**s)
                check(g,all(x%p**(M-s)==0 and (x+p**(M-s))%p**E==0 for x in roots))
                cases+=1
        for s in (0,1):
            for M in (2*s+1,2*s+2):
                E=2*M-3*s;N=E+s+1;mod=p**N
                for v in (0,1,2):
                    t=p**M*v
                    roots=[y for y in range(0,mod,p**(s+1)) if (p**s*y+y*y+t+2*y*t+p**M*(1+y+t))%mod==0]
                    check(g,len(roots)==p**s)
                    check(g,all(y%p**(M-s)==0 and (y+p**(M-s)*(1+v))%p**E==0 for y in roots))
                    # Exact triangular inverse certificate for actual J=p^s, K=1.
                    A=[[1,-1],[0,p**s]];B=[[p**s,1],[0,1]]
                    check(g,all(sum(A[i][k]*B[k][j] for k in range(2))==p**s*int(i==j) and sum(B[i][k]*A[k][j] for k in range(2))==p**s*int(i==j) for i in range(2) for j in range(2)))
                    cases+=1
    control('weighted threshold r=2s suffices',any((x*x+3)%8==0 for x in range(8)),{'p':2,'F':'X^2+3','a':1,'s':1,'r':2,'roots_mod8':[]})
    control('weighted displacement always gains a digit',precise(2,-2**(3-1),3-1+1),{'p':2,'F':'2X+8','root':-4,'guaranteed_displacement_depth':2})
    control('omit joint parameter term',precise(2,-8-(-4),4),{'F':'Y+T','H':1,'p':2,'M':2,'v':1,'actual_y':-8,'incorrect_prediction':-4})
    control('reverse joint parameter sign',precise(2,-8-0,4),{'F':'Y+T','H':1,'p':2,'M':2,'v':1,'actual_y':-8,'incorrect_prediction':0})
    evenroots=[y for y in range(0,16,2) if (y+y*y+2)%16==0]
    check(g,len(evenroots)==1 and vp(2,evenroots[0]+2)==2)
    control('first-order error always gains a digit',precise(2,evenroots[0]+2,3),{'F':'Y+Y^2+T','p':2,'s':0,'M':1,'v':1,'root_mod16':evenroots[0],'error_depth':2})
    GROUPS[g]={'domain':'integer polynomial roots modulo explicitly chosen prime powers','parameter_cases':cases,'bounds':'p2,3;s0..2;r,M=2s+1,2s+2; joint s0,1,v0,1,2; N=max(r-s+2,2s+3) for lifting and N=(2M-3s)+s+1 for motion','finite_uniqueness_convention':'Nonunit Jacobian roots modulo p^N have p^s residue representatives in the ball; all agree modulo p^(N-s). This is not a claim of p^s distinct completed roots.','non_claim':'Integral-coefficient test families do not cover arbitrary p-adic coefficients; infinite root uniqueness and analytic regularity require their separate proofs.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    for fn in (foundations,arithmetic,classical,polynomial_fibers,affine_shared,towers_charts,weighted_motion):
        before=sum(COUNTS.values());fn()
        print(f'{fn.__name__}: {sum(COUNTS.values())-before} exact assertions; total controls {len(CONTROLS)}',flush=True)
    result={'status':'PASS','coefficient_domain':'Python arbitrary-precision int and fractions.Fraction; no floating-point arithmetic','assertions':dict(COUNTS),'total_exact_assertions':sum(COUNTS.values()),'negative_controls_rejected':len(CONTROLS),'controls':CONTROLS,'groups':GROUPS,'non_claims':['Universal theorem verification','Fresh Lean/Lake/SymPy/pytest execution','Infinite p-adic root construction','General analytic regularity or native descent','Hardware benchmark or timing claims']}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'total_exact_assertions':result['total_exact_assertions'],'negative_controls_rejected':len(CONTROLS)},sort_keys=True))

if __name__=='__main__':main()
