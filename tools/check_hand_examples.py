#!/usr/bin/env python3
"""Check the finite arithmetic in docs/examples with exact rational values.

This checks the displayed constructions and their exercise answers.
It does not validate all tutorial prose, prove general research claims, run
Lean or exercise the production libraries.
"""
from fractions import Fraction as F


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


def main():
    checks=(packets,seeds,coordinates,transfer,refinement,
            redundant_coordinates,obstructions,weighted_averages,binary_rounding,
            kernels,spectral_projectors,block_elimination,modular_reconstruction,
            haar_pairs,typed_paths)
    for check in checks:
        check()
    print(f'PASS: {len(checks)} hand-worked examples')


if __name__=='__main__':
    main()
