#!/usr/bin/env python3
"""Check the finite arithmetic in docs/examples with exact rational values.

This checks the displayed constructions and their exercise answers.
It does not validate all tutorial prose, prove general research claims, run
Lean or exercise the production libraries.
"""
from fractions import Fraction as F
from itertools import combinations


def matrix(*rows):
    return tuple(tuple(F(x) for x in row) for row in rows)


def eye(n):
    return matrix(*[[int(i == j) for j in range(n)] for i in range(n)])


def transpose(a):
    return tuple(zip(*a))


def mul(a, b):
    assert a and b and len(a[0]) == len(b)
    return tuple(tuple(sum(x*y for x, y in zip(row, col))
                       for col in transpose(b)) for row in a)


def apply(a, x):
    assert len(a[0]) == len(x)
    return tuple(sum(c*v for c, v in zip(row, x)) for row in a)


def add(*arrays):
    return tuple(tuple(sum(a[i][j] for a in arrays)
                       for j in range(len(arrays[0][0])))
                 for i in range(len(arrays[0])))


def scale(c, a):
    return tuple(tuple(c*x for x in row) for row in a)


def selector(n, i):
    return matrix(*[[int(r == c == i) for c in range(n)] for r in range(n)])


def vector_sum(*vectors):
    return tuple(map(sum, zip(*vectors)))


def squared_norm(x, weights=None):
    return sum(w*v*v for w, v in zip(weights or [1]*len(x), x))


def packets():
    zero=matrix([0,0],[0,0])
    families=[(selector(2,0),selector(2,1)),
              (matrix([1,-1],[0,0]),matrix([0,1],[0,1]))]
    for p,q in families:
        assert mul(p,p)==p and mul(q,q)==q
        assert mul(p,q)==mul(q,p)==zero and add(p,q)==eye(2)
    p,q=families[0]
    assert (apply(p,(2,3)),apply(q,(2,3)))==((2,0),(0,3))
    assert (apply(p,(4,-1)),apply(q,(4,-1)))==((4,0),(0,-1))
    p,q=families[1]
    assert (apply(p,(2,3)),apply(q,(2,3)))==((-1,0),(3,3))
    assert sum(a*b for a,b in zip(apply(p,(2,3)),apply(q,(2,3))))==-3
    assert (apply(p,(4,-1)),apply(q,(4,-1)))==((5,0),(-1,-1))


def seeds():
    n=matrix([0,1],[0,0])
    assert mul(n,n)==matrix([0,0],[0,0])
    assert apply(n,(0,1))==(1,0) and apply(n,(1,0))==(0,0)
    assert apply(add(scale(3,eye(2)),scale(2,n)),(0,1))==(2,3)
    # Check the exercise's determinant on explicit illustrative seeds.
    # The tutorial's algebraic determinant calculation gives the general rule.
    for a,b in [(0,1),(2,3),(4,0),(-2,F(1,2))]:
        v=(F(a),F(b));nv=apply(n,v)
        assert v[0]*nv[1]-v[1]*nv[0]==-F(b)**2


def coordinates():
    c=matrix([1,F(1,2)],[0,1])
    inverse=matrix([1,F(-1,2)],[0,1])
    d=matrix([2,0],[0,1])
    dy=mul(mul(c,d),inverse)
    assert mul(c,inverse)==mul(inverse,c)==eye(2)
    assert dy==matrix([2,F(-1,2)],[0,1])
    assert mul(dy,c)==mul(c,d)
    for x,y,result in [((2,3),(F(7,2),3),(F(11,2),3)),
                       ((1,2),(2,2),(3,2))]:
        assert apply(c,x)==y and apply(inverse,y)==x
        assert apply(dy,y)==apply(c,apply(d,x))==result


def transfer():
    p=[selector(2,i) for i in range(2)]
    t=matrix([1,2],[3,4]);u=matrix([0,1],[1,0])
    blocks=[mul(mul(p[j],t),p[i]) for j in range(2) for i in range(2)]
    assert blocks==[matrix([1,0],[0,0]),matrix([0,2],[0,0]),
                    matrix([0,0],[3,0]),matrix([0,0],[0,4])]
    assert add(*blocks)==t
    assert [apply(b,(2,3)) for b in blocks]==[(2,0),(6,0),(0,6),(0,12)]
    assert apply(t,(2,3))==(8,18)
    assert mul(u,t)==matrix([3,4],[1,2])
    assert apply(mul(u,t),(2,3))==apply(u,apply(t,(2,3)))==(18,8)
    for k in range(2):
        for i in range(2):
            assert mul(mul(p[k],mul(u,t)),p[i])==add(*[
                mul(mul(mul(p[k],u),p[j]),mul(mul(p[j],t),p[i]))
                for j in range(2)])
    assert [apply(b,(1,-1)) for b in blocks]==[(1,0),(-2,0),(0,3),(0,-4)]
    assert apply(t,(1,-1))==(-1,-1)


def refinement():
    x=tuple(range(1,9))
    select=lambda m,r: tuple(v if i%m==r else 0 for i,v in enumerate(x))
    coarse=[select(2,r) for r in range(2)]
    fine=[select(4,r) for r in range(4)]
    assert [x[r::2] for r in range(2)]==[(1,3,5,7),(2,4,6,8)]
    assert [x[r::4] for r in range(4)]==[(1,5),(2,6),(3,7),(4,8)]
    assert vector_sum(fine[0],fine[2])==coarse[0]
    assert vector_sum(fine[1],fine[3])==coarse[1]
    assert vector_sum(*fine)==vector_sum(*coarse)==x
    retained=vector_sum(fine[0],fine[1],fine[3])
    assert retained==(1,2,0,4,5,6,0,8)
    residual=tuple(a-b for a,b in zip(x,retained))
    assert residual==(0,0,3,0,0,0,7,0) and squared_norm(residual)==58
    assert coarse[0]==(1,0,3,0,5,0,7,0) and squared_norm(coarse[1])==120


def redundant_coordinates():
    a=matrix([1,0],[0,1],[1,1])
    s=scale(F(1,3),matrix([2,-1,1],[-1,2,1]))
    assert mul(s,a)==eye(2)
    x=(2,3)
    assert apply(a,x)==(2,3,5) and apply(s,apply(a,x))==x
    c=[mul(mul(s,selector(3,i)),a) for i in range(3)]
    assert c==[scale(F(1,3),matrix([2,0],[-1,0])),
               scale(F(1,3),matrix([0,-1],[0,2])),
               scale(F(1,3),matrix([1,1],[1,1]))]
    assert [apply(ci,x) for ci in c]==[(F(4,3),F(-2,3)),(-1,2),(F(5,3),F(5,3))]
    assert add(*c)==eye(2) and vector_sum(*(apply(ci,x) for ci in c))==x
    assert mul(c[0],c[0])==scale(F(2,3),c[0])!=c[0]
    assert mul(a,s)==scale(F(1,3),matrix([2,-1,1],[-1,2,1],[1,1,2]))
    assert apply(mul(a,s),(0,0,1))==(F(1,3),F(1,3),F(2,3))
    assert apply(a,(1,-1))==(1,-1,0)
    assert [apply(ci,(1,-1)) for ci in c]==[
        (F(2,3),F(-1,3)),(F(1,3),F(-2,3)),(0,0)]


def obstructions():
    r=matrix([1,1]);f=matrix([1,0]);h=matrix([2,2])
    u=(1,0);v=(0,1)
    assert apply(r,u)==apply(r,v)==(1,)
    assert apply(f,u)==(1,) and apply(f,v)==(0,)
    assert apply(r,(1,-1))==(0,) and apply(f,(1,-1))==(1,)
    assert mul(matrix([2]),r)==h
    assert sum((1,1))==sum((2,0))==2 and 1*1!=2*0


def weighted_averages():
    e=matrix([F(1,4),F(3,4),0],[F(1,4),F(3,4),0],[0,0,1])
    weights=(1,3,2);w=matrix([1,0,0],[0,3,0],[0,0,2])
    x=(2,6,9);y=apply(e,x);r=tuple(a-b for a,b in zip(x,y))
    assert y==(5,5,9) and r==(-3,1,0)
    assert mul(e,e)==e and e!=transpose(e)
    assert mul(w,e)==mul(transpose(e),w)
    assert apply(e,(1,1,0))==(1,1,0) and apply(e,(0,0,1))==(0,0,1)
    assert r[0]+3*r[1]==0 and r[2]==0
    assert (squared_norm(x,weights),squared_norm(y,weights),squared_norm(r,weights))==(274,262,12)
    assert squared_norm(x,weights)==squared_norm(y,weights)+squared_norm(r,weights)
    equal=matrix([F(1,2),F(1,2),0],[F(1,2),F(1,2),0],[0,0,1])
    y=apply(equal,x);r=tuple(a-b for a,b in zip(x,y))
    assert y==(4,4,9) and r==(-2,2,0)
    assert (squared_norm(x),squared_norm(y),squared_norm(r))==(121,113,8)


def binary_rounding():
    def nearest_even_in_unit_binade(x, precision):
        assert 1<=x<=2 and precision>=2
        denominator=2**(precision-1)
        candidates=[(F(k,denominator),k) for k in range(denominator,2*denominator+1)]
        return min(candidates,key=lambda row:(abs(row[0]-x),row[1]%2))[0]
    assert [F(k,4) for k in range(4,8)]==[1,F(5,4),F(3,2),F(7,4)]
    x=F(13,8)
    assert x==1+F(1,2)+F(1,8)
    assert x-F(3,2)==F(7,4)-x==F(1,8)
    stored=nearest_even_in_unit_binade(x,3)
    assert stored==F(3,2) and stored-x==F(-1,8)
    assert nearest_even_in_unit_binade(x,4)==x
    assert nearest_even_in_unit_binade(F(11,8),3)-F(11,8)==F(1,8)
    denominator=F(1,10).denominator
    assert denominator==10 and denominator & (denominator-1)!=0
    assert F(5,4)-1==F(1,4) and 2*F(5,4)-2==F(1,2)


def kernels():
    t=matrix([1,1,0],[0,1,1])
    k=(-1,1,-1)
    assert apply(t,k)==(0,0)
    assert apply(t,(1,0,0))==(1,0) and apply(t,(0,0,1))==(0,1)
    for s in [0,1,2,F(-3,2)]:
        assert apply(t,(5-s,s,7-s))==(5,7)
        assert apply(t,(1-s,s,-1-s))==(1,-1)
    assert apply(t,(3,2,5))==(5,7)


def spectral_projectors():
    t=matrix([2,1],[0,3]);i=eye(2)
    p=add(scale(3,i),scale(-1,t));q=add(t,scale(-2,i))
    assert p==matrix([1,-1],[0,0]) and q==matrix([0,1],[0,1])
    assert apply(t,(1,0))==(2,0) and apply(t,(1,1))==(3,3)
    assert mul(p,p)==p and mul(q,q)==q
    assert mul(p,q)==mul(q,p)==matrix([0,0],[0,0])
    assert add(p,q)==i and add(scale(2,p),scale(3,q))==t
    assert add(mul(t,t),scale(-5,t),scale(6,i))==matrix([0,0],[0,0])
    assert mul(t,t)==matrix([4,5],[0,9])==add(scale(4,p),scale(9,q))
    assert apply(t,(2,3))==(7,9) and apply(mul(t,t),(2,3))==(23,27)


def block_elimination():
    m=matrix([2,1],[3,4]);s=F(4)-3*F(1,2)
    assert s==F(5,2)
    assert mul(matrix([1,0],[F(3,2),1]),matrix([2,1],[0,s]))==m
    for f,g,u,v in [(5,11,F(9,5),F(7,5)),(3,5,F(7,5),F(1,5))]:
        assert (g-F(3,2)*f)/s==v and (f-v)/2==u
        assert apply(m,(u,v))==(f,g)
    assert m[0][0]*m[1][1]-m[0][1]*m[1][0]==2*s==5
    singular=matrix([2,1],[3,F(3,2)])
    assert apply(singular,(F(5,2),0))==apply(singular,(2,1))==(5,F(15,2))


def modular_reconstruction():
    assert (10%3,10%5)==(1,0) and (6%3,6%5)==(0,1)
    assert (2*10+3*6)%15==8 and (8%3,8%5)==(2,3)
    assert [x for x in range(15) if (x%3,x%5)==(2,3)]==[8]
    assert 10**2%15==10 and 6**2%15==6 and 10*6%15==0 and (10+6)%15==1
    assert [x for x in range(12) if (x%4,x%6)==(1,2)]==[]
    assert [x for x in range(12) if (x%4,x%6)==(1,1)]==[1]
    assert (10+4*6)%15==4 and (4%3,4%5)==(1,4)


def haar_pairs():
    h=scale(F(1,2),matrix([1,1],[1,-1]));inverse=scale(2,h)
    assert mul(h,inverse)==mul(inverse,h)==eye(2)
    assert mul(transpose(h),h)==scale(F(1,2),eye(2))
    for x,expected in [((2,6,10,14),(8,-4,-2,-2)),((1,3,5,7),(4,-2,-1,-1))]:
        a,d=apply(h,x[:2]);b,e=apply(h,x[2:])
        top,detail=apply(h,(a,b))
        assert (top,detail,d,e)==expected
        a2,b2=apply(inverse,(top,detail))
        assert apply(inverse,(a2,d))+apply(inverse,(b2,e))==x
        assert squared_norm(x)==4*(top*top+detail*detail)+2*(d*d+e*e)
    assert squared_norm((2,6,10,14))==336 and squared_norm((8,-4,-2,-2))==88
    assert squared_norm((4,4,12,12))==320 and squared_norm((-2,2,-2,2))==16
    assert squared_norm((1,3,5,7))==84


def typed_paths():
    a=matrix([1,1]);b=matrix([1],[0]);p=mul(b,a)
    assert mul(a,b)==eye(1) and p==matrix([1,1],[0,0])
    assert mul(p,p)==p and mul(a,p)==a
    assert apply(a,(2,3))==(5,) and apply(p,(2,3))==(5,0)
    d=matrix([2,0],[0,3])
    assert mul(d,p)==matrix([2,2],[0,0]) and mul(p,d)==matrix([2,3],[0,0])
    assert add(mul(d,p),scale(-1,mul(p,d)))==matrix([0,-1],[0,0])
    other=matrix([0],[1]);q=mul(other,a)
    assert mul(a,other)==eye(1) and mul(q,q)==q and q==matrix([0,0],[1,1])
    assert apply(q,(2,3))==(0,5)


def cyclic_reciprocals():
    b=[F(1)]
    for n in range(1,9):
        b.append(-b[n-1]-(b[n-2] if n>=2 else 0))
    assert b==[1,-1,0,1,-1,0,1,-1,0]
    def convolution(a,b):
        result=[F(0)]*(len(a)+len(b)-1)
        for i,x in enumerate(a):
            for j,y in enumerate(b):result[i+j]+=x*y
        return result
    for length in (6,9):
        product=convolution([1,1,1],b[:length])
        assert product==[1]+[0]*(length-1)+[-1,0]
    packets=[tuple(x if i%3==r else 0 for i,x in enumerate(b[:6])) for r in range(3)]
    assert packets==[(1,0,0,1,0,0),(0,-1,0,0,-1,0),(0,0,0,0,0,0)]
    assert vector_sum(*packets)==tuple(b[:6])
    # Exact arithmetic in Q[omega] with omega^2 + omega + 1 = 0.
    def multiply(x,y):
        a,b=x;c,d=y
        return (a*c-b*d,a*d+b*c-b*d)
    powers=[(1,0),(0,1),(-1,-1)]
    assert multiply(powers[1],powers[1])==powers[2]
    assert multiply(powers[2],powers[1])==powers[0]
    for n in range(9):
        for r in range(3):
            values=[powers[((n-r)*k)%3] for k in range(3)]
            assert (F(sum(v[0] for v in values),3),F(sum(v[1] for v in values),3))==(int(n%3==r),0)


def quantum_measurement():
    def z(a,b=0):return (F(a),F(b))
    def plus(a,b):return (a[0]+b[0],a[1]+b[1])
    def times(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
    def conj(a):return (a[0],-a[1])
    def abs2(a):return a[0]**2+a[1]**2
    def product(a,b):
        return tuple(tuple(plus(times(a[i][0],b[0][j]),times(a[i][1],b[1][j])) for j in range(2)) for i in range(2))
    psi=(z(F(3,5)),z(0,F(4,5)))
    rho=tuple(tuple(times(a,conj(b)) for b in psi) for a in psi)
    assert sum(abs2(a) for a in psi)==1
    assert rho==((z(F(9,25)),z(0,F(-12,25))),(z(0,F(12,25)),z(F(16,25))))
    assert product(rho,rho)==rho and plus(rho[0][0],rho[1][1])==z(1)
    assert tuple(tuple(conj(rho[j][i]) for j in range(2)) for i in range(2))==rho
    diagonal=((rho[0][0],z(0)),(z(0),rho[1][1]))
    squared=product(diagonal,diagonal)
    assert plus(squared[0][0],squared[1][1])==z(F(337,625))
    p=(((z(1),z(0)),(z(0),z(0))),((z(0),z(0)),(z(0),z(1))))
    parts=[product(product(q,rho),q) for q in p]
    assert tuple(tuple(plus(parts[0][i][j],parts[1][i][j]) for j in range(2)) for i in range(2))==diagonal
    u=((z(1),z(0)),(z(0),z(0,-1)))
    adjoint=tuple(tuple(conj(u[j][i]) for j in range(2)) for i in range(2))
    assert product(adjoint,u)==((z(1),z(0)),(z(0),z(1)))
    phi=(psi[0],times(z(0,-1),psi[1]))
    assert phi==(z(F(3,5)),z(F(4,5)))
    def hadamard_probabilities(v):
        return (abs2(plus(v[0],v[1]))/2,abs2(plus(v[0],(-v[1][0],-v[1][1])))/2)
    assert hadamard_probabilities(psi)==(F(1,2),F(1,2))
    assert hadamard_probabilities(phi)==(F(49,50),F(1,50))
    chi=(z(F(4,5)),z(F(3,5)))
    assert tuple(abs2(a) for a in chi)==(F(16,25),F(9,25))
    assert sum(abs2(a)**2 for a in chi)==F(337,625)
    assert hadamard_probabilities(chi)==(F(49,50),F(1,50))


def lift_branches():
    roots=lambda m:[x for x in range(m) if (x*x-1)%m==0]
    assert [roots(m) for m in (2,4,8,16,32)]==[[1],[1,3],[1,3,5,7],[1,7,9,15],[1,15,17,31]]
    children={r:[s for s in (r,r+8) if (s*s-1)%16==0] for r in roots(8)}
    assert children=={1:[1,9],3:[],5:[],7:[7,15]}
    assert 9**2%32==25**2%32==17
    path=(1,3,7,15)
    assert all(path[i+1]%(2**(i+1))==path[i] for i in range(3))
    for n in range(1,9):
        assert (2**n-1)**2-1==2**(2*n)-2**(n+1)
        assert ((2**n-1)**2-1)%(2**n)==0


def finite_frobenius():
    def multiply(x,y):
        a,b=x;c,d=y
        return ((a*c+3*b*d)%5,(a*d+b*c)%5)
    def power(x,n):
        result=(1,0)
        for _ in range(n):result=multiply(result,x)
        return result
    def reduced(a):return tuple(tuple(int(v)%5 for v in row) for row in a)
    assert {x*x%5 for x in range(5)}=={0,1,4}
    for a in range(5):
        for b in range(5):
            assert power((a,b),5)==(a,(-b)%5)
            assert power((a,b),25)==(a,b)
    alpha=(0,1);beta=(1,1);gamma=(2,1)
    assert power(alpha,5)==(0,4) and power(beta,2)==(4,2)
    assert power(beta,5)==(1,4) and multiply(beta,power(beta,5))==(3,0)
    assert multiply(beta,(2,3))==(1,0)
    assert power(gamma,5)==(2,4) and multiply(gamma,(2,4))==(1,0)
    c=matrix([1,0],[0,4]);m=matrix([1,3],[1,1])
    assert reduced(mul(c,c))==eye(2)
    assert reduced(mul(mul(c,m),c))==matrix([1,2],[4,1])
    assert (m[0][0]+m[1][1])%5==2 and (m[0][0]*m[1][1]-m[0][1]*m[1][0])%5==3


def support_multiplicity():
    j=matrix([0,0],[1,0]);p=selector(2,0)
    zero=matrix([0,0],[0,0])
    assert j!=zero and mul(j,j)==zero
    assert mul(p,p)==p and mul(p,j)==zero and mul(j,p)==j
    shift=matrix([0,0,0],[1,0,0],[0,1,0])
    assert mul(shift,shift)!=scale(0,eye(3))
    assert mul(mul(shift,shift),shift)==scale(0,eye(3))
    for value in (F(-2),F(-1,3),F(0),F(1,2),F(3)):
        assert (value==0)==(value**2==0)==(value**3==0)
        if value:assert value*(1/value)==value**2*(1/value**2)==1
    # Squaring a*I+b*J produces a^2*I+2ab*J, since J^2=0.
    for a,b in [(0,0),(1,0),(F(1,2),2),(1,3),(-2,F(1,3))]:
        element=add(scale(F(a),eye(2)),scale(F(b),j))
        assert mul(element,element)==add(scale(F(a)**2,eye(2)),scale(2*F(a)*F(b),j))


def proof_certificates():
    obligations=set('abcd')
    supplies=[set('ab'),set('bc'),set('cd'),set('ad')]
    def derived(chosen,available):
        # Singleton-premise rules, followed by the rule requiring all obligations.
        reached=set().union(*(available[i] for i in chosen))
        return reached|({'t'} if obligations<=reached else set())
    subsets=[frozenset(c) for n in range(5) for c in combinations(range(4),n)]
    valid=[s for s in subsets if 't' in derived(s,supplies)]
    best=min(map(len,valid))
    optima={s for s in valid if len(s)==best}
    assert best==2 and optima=={frozenset((0,2)),frozenset((1,3))}
    assert all(not any(t<s for t in valid) for s in optima)
    common=frozenset.intersection(*optima)
    assert not common and 't' not in derived(common,supplies)
    assert derived({0},supplies)==set('ab')
    for pair,missing in [((0,1),'d'),((0,3),'c'),((1,2),'a'),((2,3),'b')]:
        assert obligations-derived(pair,supplies)=={missing}
    extended=supplies+[obligations]
    for last_cost,minimum in [(3,2),(1,1)]:
        costs=[1,1,1,1,last_cost]
        actual=min(sum(costs[i] for i in chosen)
                   for n in range(6) for chosen in combinations(range(5),n)
                   if 't' in derived(chosen,extended))
        assert actual==minimum


def hidden_memory():
    t=matrix([1,1],[1,0]);power=eye(2);state=(F(1),F(0))
    visible=[];states=[]
    for n in range(6):
        states.append(state);visible.append(power[0][0])
        assert state==apply(power,(1,0))
        state=apply(t,state);power=mul(t,power)
    assert states==[(1,0),(1,1),(2,1),(3,2),(5,3),(8,5)]
    assert visible==[1,1,2,3,5,8]
    assert visible[2]!=visible[1]*visible[1]
    assert [F(1)*F(0)**k*F(1) for k in range(4)]==[1,0,0,0]
    assert all(states[n][1]==visible[n-1] for n in range(1,6))
    assert all(visible[n+1]==visible[n]+visible[n-1] for n in range(1,5))
    assert apply(t,(1,0))[0]==1 and apply(t,(1,1))[0]==2
    prepared=matrix([1,1],[0,0]);power=eye(2)
    for _ in range(6):
        assert apply(power,(1,0))==(1,0)
        power=mul(prepared,power)
    assert apply(prepared,(1,1))==(2,0)


def calibrated_continuation():
    e1,e2,e3=(1,0,0),(0,1,0),(0,0,1)
    t0=matrix([1,0,0],[0,0,0],[0,1,0])
    t1=matrix([1,0,1],[0,0,0],[0,1,0])
    for t in (t0,t1):
        assert apply(t,e1)==e1 and apply(t,e2)==e3
        assert apply(t,(2,-1,0))==(2,0,-1)
        assert apply(t,(1,1,0))==(1,0,1)
        assert t[2][0]==0 and t[2][1]==1  # U -> U requires the e2 coefficient to vanish.
        power=eye(3)
        for _ in range(6):
            assert apply(power,(2,0,0))==(2,0,0)
            power=mul(t,power)
    assert apply(mul(t0,t0),e2)==(0,0,0)
    assert apply(mul(t1,t1),e2)==e1
    assert apply(t0,(2,3,0))==(2,0,3)
    assert apply(mul(t0,t0),(2,3,0))==(2,0,0)


def contracted_feedback():
    def coefficients(q,r,count):
        values=[F(1)]
        for n in range(1,count):
            values.append(sum(q**(2*i+1)*r**(2*(n-1-i)+1)*values[i]*values[n-1-i]
                              for i in range(n))/(2*n+1))
        return values
    q,r=F(1,3),F(2,3)
    c=coefficients(q,r,4)
    assert c==[1,F(2,27),F(4,2187),F(232,11160261)]
    assert c[2]*(q*r**5+q**5*r)==F(136,1594323)
    assert c[1]**2*q**3*r**3==F(32,531441)
    assert sum(c[:3])==F(2353,2187)
    # Independently multiply the truncated polynomials and differentiate.
    polynomial=[F(0)]*8
    for i,v in enumerate(c):polynomial[2*i+1]=v
    product=[F(0)]*15
    for i,a in enumerate(polynomial):
        for j,b in enumerate(polynomial):product[i+j]+=a*q**i*b*r**j
    derivative=[(n+1)*polynomial[n+1] for n in range(7)]
    assert derivative==[product[n]+int(n==0) for n in range(7)]
    assert product[8]!=0  # A truncated polynomial is not the full solution.
    assert coefficients(F(1,2),F(1,2),3)==[1,F(1,12),F(1,480)]


def repair_menus():
    def rank(columns):
        a=[list(row) for row in zip(*columns)];pivot=0
        for j in range(len(columns)):
            i=next((i for i in range(pivot,len(a)) if a[i][j]),None)
            if i is None:continue
            a[pivot],a[i]=a[i],a[pivot]
            divisor=a[pivot][j];a[pivot]=[v/divisor for v in a[pivot]]
            for i in range(len(a)):
                if i!=pivot:
                    factor=a[i][j]
                    a[i]=[v-factor*w for v,w in zip(a[i],a[pivot])]
            pivot+=1
            if pivot==len(a):break
        return pivot
    d=tuple(map(F,(1,0,0)));target=tuple(map(F,(0,1,0)))
    menu=[tuple(map(F,row)) for row in ((0,1,1),(0,0,1),(0,1,0))]
    assert rank([d])==1 and rank([d,target])==2
    feasible=[]
    for n in range(4):
        for chosen in combinations(range(3),n):
            columns=[d]+[menu[i] for i in chosen]
            if rank(columns)==rank(columns+[target]):feasible.append(chosen)
    assert set(feasible)=={(2,),(0,1),(0,2),(1,2),(0,1,2)}
    costs=[1,1,3]
    assert min(sum(costs[i] for i in s) for s in feasible)==2
    assert vector_sum(menu[0],tuple(-v for v in menu[1]))==target
    assert vector_sum(menu[0],menu[1])==(0,1,2)
    witness=matrix([0,1,0])
    assert apply(witness,d)==apply(witness,menu[1])==(0,)
    assert apply(witness,target)==(1,)
    assert min(sum([1,1,1][i] for i in s) for s in feasible)==1


def gaussian_update():
    h=matrix([1,1]);p=eye(2);noise=eye(1);mean=(0,0);y=F(3)
    s=add(mul(mul(h,p),transpose(h)),noise)
    assert s==matrix([3])
    k=scale(F(1,3),mul(p,transpose(h)))
    assert k==matrix([F(1,3)],[F(1,3)])
    posterior_mean=apply(k,(y,))
    assert posterior_mean==(1,1)
    covariance=add(p,scale(-1,mul(mul(k,h),p)))
    assert covariance==matrix([F(2,3),F(-1,3)],[F(-1,3),F(2,3)])
    precision=add(eye(2),mul(transpose(h),h))
    assert precision==matrix([2,1],[1,2]) and mul(precision,covariance)==eye(2)
    assert apply(precision,posterior_mean)==apply(transpose(h),(y,))
    assert y*y-sum(a*b for a,b in zip(posterior_mean,apply(precision,posterior_mean)))==3
    assert apply(covariance,(1,1))==(F(1,3),F(1,3))
    assert apply(covariance,(1,-1))==(1,-1)
    def joseph(gain):
        residual_operator=add(eye(2),scale(-1,mul(gain,h)))
        return add(mul(mul(residual_operator,p),transpose(residual_operator)),mul(mul(gain,noise),transpose(gain)))
    assert joseph(k)==covariance
    b=matrix([F(1,4)],[F(1,4)])
    assert apply(b,(y,))==(F(3,4),F(3,4))
    assert joseph(b)==matrix([F(11,16),F(-5,16)],[F(-5,16),F(11,16)])
    assert add(mul(p,transpose(h)),scale(-1,mul(b,s)))==matrix([F(1,4)],[F(1,4)])
    assert joseph(b)!=add(p,scale(-1,mul(mul(b,h),p)))
    assert apply(k,(-y,))==(-1,-1) and joseph(k)==covariance


def main():
    checks=(packets,seeds,coordinates,transfer,refinement,
            redundant_coordinates,obstructions,weighted_averages,binary_rounding,
            kernels,spectral_projectors,block_elimination,modular_reconstruction,
            haar_pairs,typed_paths,cyclic_reciprocals,quantum_measurement,
            lift_branches,finite_frobenius,support_multiplicity,
            proof_certificates,hidden_memory,calibrated_continuation,
            contracted_feedback,repair_menus,gaussian_update)
    for check in checks:
        check()
    print(f'PASS: {len(checks)} hand-worked examples')


if __name__=='__main__':
    main()
