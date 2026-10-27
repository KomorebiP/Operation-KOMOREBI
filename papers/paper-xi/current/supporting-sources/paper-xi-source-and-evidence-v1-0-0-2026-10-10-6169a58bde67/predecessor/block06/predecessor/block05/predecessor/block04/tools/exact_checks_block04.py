#!/usr/bin/env python3
"""Exact finite controls for Paper XI Publication Block 04.

No floating point, local Langlands oracle, or theorem prover is used.
The tests validate the displayed finite models and algebraic identities only.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from math import gcd, prod
from pathlib import Path
import time
import unittest


def ceildiv(a: int, b: int) -> int:
    if b <= 0:
        raise ValueError('positive denominator required')
    return -((-a)//b)


def profile(b: list[int], levels: list[int]) -> dict[str, int]:
    if len(b) != len(levels)+1 or b[-1] != 1 or not levels:
        raise ValueError('profile must terminate at scalar grade 1')
    if any(x <= y for x,y in zip(b,b[1:])) or any(v <= 0 for v in levels):
        raise ValueError('strictly decreasing positive grade dimensions required')
    if any(x <= y for x,y in zip(levels,levels[1:])):
        raise ValueError('strictly decreasing positive levels required')
    delta=[x-y for x,y in zip(b,b[1:])]
    I=sum(t*ceildiv(v,2) for t,v in zip(delta,levels))-(b[0]-1)
    D=sum(t for t,v in zip(delta,levels) if v%2==0)
    sw_end=sum(t*v for t,v in zip(delta,levels))
    return dict(I=I,D=D,delta=sw_end,pair=b[0]**2-1+sw_end)


def polar(v: int, w: int, m: int) -> int:
    return sum(((v>>(2*i))&1)*((w>>(2*i+1))&1)+
               ((v>>(2*i+1))&1)*((w>>(2*i))&1) for i in range(m))%2


def quad(v: int, m: int, linear: int = 0) -> int:
    return (sum(((v>>(2*i))&1)*((v>>(2*i+1))&1) for i in range(m))
            + (v & linear).bit_count())%2


def gauss(m: int, linear: int) -> int:
    return sum(1-2*quad(v,m,linear) for v in range(1<<(2*m)))


def arf(m: int, linear: int) -> int:
    return int(gauss(m,linear)<0)


def dual_vector(linear: int, m: int) -> int:
    return sum(((linear>>(2*i))&1)<<(2*i+1) |
               ((linear>>(2*i+1))&1)<<(2*i) for i in range(m))


def transvection(v: int, a: int, m: int) -> int:
    return v ^ (a if polar(a,v,m) else 0)


def linmap(columns: tuple[int,...], v: int) -> int:
    r=0
    for i,c in enumerate(columns):
        if (v>>i)&1:r ^= c
    return r


def symplectic_frames(m: int, s: int):
    """Exhaustive labelled symplectic embeddings for small dimensions."""
    def rec(columns):
        if len(columns)==2*s:
            yield tuple(columns);return
        j=len(columns)
        for v in range(1,1<<(2*m)):
            if all(polar(v,w,m)==int(j%2==1 and i==j-1)
                   for i,w in enumerate(columns)):
                yield from rec(columns+[v])
    yield from rec([])


def ext_c(v: int,w: int,m: int,linear: int=0) -> int:
    # Normal order x_1 y_1 ... x_m y_m, with lift squares from linear.
    return (sum(((v>>(2*i+1))&1)*((w>>(2*i))&1) for i in range(m))
            + (v&w&linear).bit_count())%2


def ext_mul(g: tuple[int,int],h: tuple[int,int],m: int,linear: int=0):
    z,v=g;u,w=h
    return ((z+u+ext_c(v,w,m,linear))%2,v^w)


def gf_add(a: int,b: int) -> int:
    ans=0;t=1
    for _ in range(4):
        ans += ((a%3+b%3)%3)*t;a//=3;b//=3;t*=3
    return ans


def gf_neg(a: int) -> int:
    return gf_add(a,a)


def gf_mul(a: int,b: int) -> int:
    aa=[];bb=[]
    for _ in range(4):aa.append(a%3);bb.append(b%3);a//=3;b//=3
    c=[0]*7
    for i in range(4):
        for j in range(4):c[i+j]=(c[i+j]+aa[i]*bb[j])%3
    # z^4+z+2=0, so z^4=2z+1.
    for k in range(6,3,-1):
        c[k-4]=(c[k-4]+c[k])%3;c[k-3]=(c[k-3]+2*c[k])%3
    return sum(c[i]*3**i for i in range(4))


def gf_pow(a: int,n: int) -> int:
    r=1
    while n:
        if n&1:r=gf_mul(r,a)
        a=gf_mul(a,a);n//=2
    return r


class ConductorChecks(unittest.TestCase):
    def test_principal_order_grades(self):
        for n in range(1,25):
            for e in range(1,n+1):
                if n%e:continue
                d=n//e
                for k in range(-7,8):
                    blocks=sum(ceildiv(k+1+i-j,e)-ceildiv(k+i-j,e)
                               for i in range(e) for j in range(e))
                    self.assertEqual(blocks*d*d,n*n//e)

    def test_period_divisibility(self):
        for n in range(1,41):
            for w in range(1,81):
                for e in range(1,n+1):
                    if n%e==0:self.assertEqual((e*w)%n==0,e%(n//gcd(n,w))==0)
        self.assertEqual([(e,e*24//9) for e in (1,3,9) if e*24%9==0],[(3,8),(9,24)])

    def test_normalization_dimensions(self):
        a_rho,sw_rho,a_end,sw_end=33,24,232,152
        self.assertEqual(a_rho-9,sw_rho)
        self.assertEqual(a_end-(81-1),sw_end)
        self.assertEqual(a_end-81,151)
        self.assertNotEqual(a_end-81,sw_end)
        self.assertNotEqual(9*4//3,24)  # critical versus leading level

    def test_field81_and_projective_characters(self):
        self.assertTrue(all(gf_pow(a,80)==1 for a in range(1,81)))
        roots=[a for a in range(81) if gf_add(gf_pow(a,9),a)==0]
        self.assertEqual(len(roots),9)
        chars=[]
        for v in roots:
            row=tuple(gf_add(gf_mul(gf_pow(v,3),gf_pow(u,3)),gf_mul(v,u)) for u in roots)
            self.assertTrue(set(row)<=set(range(3)));chars.append(row)
        self.assertEqual(len(set(chars)),9)
        self.assertTrue(all(len(set(row))==3 for row in chars[1:]))

    def test_source_self_pair_breaks(self):
        counts=Counter(max(0 if x==0 else 1,0 if y==0 else 2)
                       for x,y in product(range(9),repeat=2))
        self.assertEqual(dict(counts),{0:1,1:8,2:72})
        sw=sum(h*c for h,c in counts.items())
        self.assertEqual(sw,152);self.assertEqual(81-1+sw,232)

    def test_rank_nine_volume_formula(self):
        for q in (3,9,27):
            vp=Fraction(1,prod(q**j-1 for j in range(1,10)))
            st=Fraction(prod(q**j-1 for j in range(1,9)),9)
            for c in (4,10):
                I=64+c;vj=(q-1)*vp/Fraction(q**I)
                degree=Fraction(q**4)/(9*vj)
                ratio=Fraction(q**9-1,q-1)*q**(I+4)
                self.assertEqual(degree/st,ratio)
                self.assertEqual(profile([9,3,1],[24,c])['pair'],224+2*c)
        self.assertEqual(profile([9,3,1],[24,4])['pair'],232)
        self.assertEqual(profile([9,3,1],[24,10])['pair'],244)

    def test_parity_cancellation_identity(self):
        for v in range(1,401):self.assertEqual(2*ceildiv(v,2)+int(v%2==0),v+1)
        for n in range(2,22):
            for mid in range(2,n):
                for hi,lo in combinations(range(1,15),2):
                    p=profile([n,mid,1],[lo,hi])
                    self.assertEqual(n-1+2*p['I']+p['D'],p['delta'])

    def test_dyadic_full_capacity(self):
        for d in range(1,13):
            h=list(range(1,2*d,2));n=2**d
            levels=[2**(d-j)*3*h[d-j] for j in range(1,d+1)]
            p=profile([2**(d-j) for j in range(d+1)],levels)
            self.assertEqual(p['D'],n-2)
            self.assertEqual(p['D']>=2*d,d>=3)
            self.assertEqual(p['pair'],n*n-1+sum(3*4**i*h[i] for i in range(d)))

    def test_rank_eight_same_invariant_distinct_capacity(self):
        good=profile([8,4,2,1],[60,18,3]);skip=profile([8,4,1],[60,13])
        self.assertEqual((good['pair'],skip['pair']),(342,342))
        self.assertEqual((good['I'],skip['I']),(133,134))
        self.assertEqual((good['D'],skip['D']),(6,4))
        for h1,h2,h3 in combinations(range(1,20,2),3):
            a=profile([8,4,2,1],[12*h3,6*h2,3*h1])
            b=profile([8,4,1],[12*h3,h1+4*h2])
            self.assertEqual(a['pair'],b['pair']);self.assertNotEqual(a['D'],b['D'])

    def test_descent_central_normalization(self):
        # Character groups of unramified degree-four and degree-three fibres.
        for m,n in ((4,9),(2,9),(5,8)):
            for r in range(m):self.assertEqual(len([a for a in range(m) if n*a%m==r]),1)
        self.assertEqual(len([a for a in range(3) if 9*a%3==0]),3)
        self.assertEqual(len([a for a in range(3) if 9*a%3==1]),0)


class MarkingChecks(unittest.TestCase):
    def test_quadratic_and_gauss_identities(self):
        for m in range(1,4):
            N=1<<(2*m)
            for l in range(N):
                self.assertEqual(abs(gauss(m,l)),2**m)
                self.assertEqual(arf(m,l),quad(dual_vector(l,m),m))
                for v in range(N):
                    for w in range(N):
                        self.assertEqual(quad(v^w,m,l)^quad(v,m,l)^quad(w,m,l),polar(v,w,m))

    def test_dihedral_quaternion_extensions(self):
        for l,orders in ((0,Counter({1:1,2:5,4:2})),(3,Counter({1:1,2:1,4:6}))):
            G=list(product(range(2),range(4)));found=Counter()
            for a in G:
                x=(0,0)
                for k in range(1,9):
                    x=ext_mul(x,a,1,l)
                    if x==(0,0):found[k]+=1;break
                self.assertEqual(ext_mul(a,a,1,l),(quad(a[1],1,l),0))
            self.assertEqual(found,orders)
            for a,b,c in product(G,repeat=3):
                self.assertEqual(ext_mul(ext_mul(a,b,1,l),c,1,l),ext_mul(a,ext_mul(b,c,1,l),1,l))
        self.assertEqual((gauss(1,0),gauss(1,3)),(2,-2))

    def test_equal_arf_does_not_fix_given_map(self):
        self.assertEqual(arf(1,0),arf(1,1))
        self.assertNotEqual(quad(1,1,0),quad(1,1,1))

    def test_full_section_has_extra_data(self):
        # Rephase only e+f. Squares and commutators survive, selected section does not.
        t=lambda v:int(v==3)
        for v in range(4):
            self.assertEqual(ext_c(v,v,1)^t(v)^t(v)^t(0),quad(v,1))
        self.assertNotEqual(ext_c(1,2,1),ext_c(1,2,1)^t(1)^t(2)^t(3))

    def test_all_rank_four_quadratic_embeddings(self):
        frames=list(symplectic_frames(2,2));self.assertEqual(len(frames),720)
        # Canonical forms suffice for the two types, all labelled symplectic maps checked.
        for ls,lt in product((0,3),repeat=2):
            good=[f for f in frames if all(quad(linmap(f,v),2,lt)==quad(v,2,ls) for v in range(16))]
            self.assertEqual(bool(good),ls==lt)
            self.assertEqual(len(good),{(0,0):72,(3,3):120}.get((ls,lt),0))

    def test_one_spare_plane_all_types(self):
        frames=list(symplectic_frames(2,1));self.assertEqual(len(frames),120)
        for ls,lt in product((0,3),repeat=2):
            self.assertTrue(any(all(quad(linmap(f,v),2,lt)==quad(v,1,ls) for v in range(4)) for f in frames))

    def test_arf_shift_and_transvection_repair(self):
        for m in range(1,4):
            N=1<<(2*m)
            for ls,lt in product(range(N),repeat=2):
                a=dual_vector(ls^lt,m)
                self.assertEqual(arf(m,ls)^arf(m,lt),quad(a,m,ls))
                if quad(a,m,ls)==0:
                    for v in range(N):
                        self.assertEqual(quad(transvection(v,a,m),m,lt),quad(v,m,ls))

    def test_transvection_preserves_fixed_subspace(self):
        m=3
        for a in range(64):
            for u in range(64):
                if polar(a,u,m)==0:self.assertEqual(transvection(u,a,m),u)
        for a,v,w in product(range(16),repeat=3):
            self.assertEqual(polar(transvection(v,a,2),transvection(w,a,2),2),polar(v,w,2))

    def test_odd_action_averaging_all_cocycles(self):
        # C3 on F2^2 by T(x,y)=(y,x+y), and its dual, represented directly.
        T=lambda v: ((v>>1)&1) | ((((v&1)^((v>>1)&1)))<<1)
        act=lambda g,v:v if g%3==0 else T(v) if g%3==1 else T(T(v))
        found=0
        for d1,d2 in product(range(4),repeat=2):
            d=(0,d1,d2)
            if not all(d[(g+h)%3]==(d[g]^act(g,d[h])) for g,h in product(range(3),repeat=2)):continue
            found+=1;u=d1^d2
            self.assertTrue(all(d[g]==(u^act(g,u)) for g in range(3)))
        self.assertEqual(found,4)

    def test_even_action_obstruction(self):
        # C2 with trivial action on a nonzero F2 coefficient group.
        d=(0,1)
        self.assertTrue(all(d[(g+h)%2]==(d[g]^d[h]) for g,h in product(range(2),repeat=2)))
        self.assertFalse(any(all(d[g]==(u^u) for g in range(2)) for u in range(2)))

    def test_equivariant_defect_repair(self):
        # C3 rotates three hyperbolic planes; defect vector is invariant and isotropic.
        m=3
        def C(v):return ((v<<2)&63)|(v>>4)
        a=1|4|16
        lt=2|8|32
        self.assertEqual(quad(a,m),0);self.assertEqual(C(a),a)
        for v in range(64):
            self.assertEqual(quad(transvection(v,a,m),m,lt),quad(v,m))
            self.assertEqual(C(transvection(v,a,m)),transvection(C(v),a,m))

    def test_rank_eight_arf_boundary_counts(self):
        # 36 versus 28 zeros on the six-dimensional quotient.
        self.assertEqual(sum(quad(v,3)==0 for v in range(64)),36)
        self.assertEqual(sum(quad(v,3,3)==0 for v in range(64)),28)
        self.assertEqual((gauss(3,0),gauss(3,3)),(8,-8))

    def test_arity_and_invalid_input_controls(self):
        with self.assertRaises(ValueError):profile([8,4,2],[60,18])
        with self.assertRaises(ValueError):profile([8,4,1],[3,13])
        with self.assertRaises(ValueError):ceildiv(3,0)


class RecordedResult(unittest.TextTestResult):
    def startTest(self,test):
        super().startTest(test);self.start=time.monotonic()
    def addSuccess(self,test):
        super().addSuccess(test);records.append({'test':test.id(),'status':'passed','seconds':round(time.monotonic()-self.start,4)})
    def addFailure(self,test,err):
        super().addFailure(test,err);records.append({'test':test.id(),'status':'failed'})
    def addError(self,test,err):
        super().addError(test,err);records.append({'test':test.id(),'status':'error'})
records=[]


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (ConductorChecks,MarkingChecks))
    result=unittest.TextTestRunner(verbosity=2,resultclass=RecordedResult).run(suite)
    report={'status':'passed' if result.wasSuccessful() else 'failed','test_methods':result.testsRun,'records':records,
            'scope':'Exact bounded algebra, selected conductor formulas, marked finite groups and action controls. Not arithmetic existence or H5. No Lean run.',
            'selected_cases':{'Sp4_all_labelled_frames':720,'rank_eight_good':profile([8,4,2,1],[60,18,3]),'rank_eight_skipped':profile([8,4,1],[60,13]),'rank_nine_pair_good':232,'rank_nine_pair_excluded':244}}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    return int(not result.wasSuccessful())
if __name__=='__main__':raise SystemExit(main())
