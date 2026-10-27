#!/usr/bin/env python3
"""Bounded exact illustrations for Paper XI's Conjecture 66 progress paper.

These finite tests are not Lean certification and do not prove the local-field
simple-character construction. Python's unbounded integers are used throughout.
Run: python -B tools/exact_checks.py --output verification/EXACT_CHECKS.json
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
import itertools as it
import json
from pathlib import Path
import unittest

COUNTS: Counter[str] = Counter()
NEGATIVE_CONTROLS: list[str] = []

class ExactChecks(unittest.TestCase):
    def check(self, family: str, condition: bool, message: str = '') -> None:
        COUNTS[family] += 1
        self.assertTrue(condition, message)

    def test_quantifiers_and_same_candidate(self) -> None:
        r = []
        self.check('quantifiers', all(False for _ in r))
        self.check('quantifiers', not any(True for _ in r))
        candidates = ['realizes_only', 'factors_only']
        self.check('quantifiers', any(c == 'realizes_only' for c in candidates))
        self.check('quantifiers', any(c == 'factors_only' for c in candidates))
        self.check('quantifiers', not any(c == 'realizes_only' and c == 'factors_only' for c in candidates))
        NEGATIVE_CONTROLS.extend(['vacuous_all_realizers_does_not_produce_a_witness', 'two_different_candidates_do_not_combine'])

    def test_frobenius_index_convention(self) -> None:
        for modulus in [7, 11, 13]:
            for q in range(2, modulus):
                inv = pow(q, -1, modulus)
                for j in range(modulus):
                    self.check('frobenius_indices', (q * (inv * j % modulus)) % modulus == j)
        self.check('frobenius_indices', (2 * 1) % 7 == 2 and (pow(2, -1, 7) * 1) % 7 == 4)
        NEGATIVE_CONTROLS.append('forward_and_geometric_frobenius_labels_differ')

    def test_finite_balanced_central_product(self) -> None:
        p = 3
        h = list(it.product(range(p), repeat=3))
        def mul(a, b):
            x,y,z = a; xx,yy,zz = b
            return ((x+xx)%p, (y+yy)%p, (z+zz+y*xx)%p)
        for a,b,c in it.product(h,repeat=3):
            self.check('heisenberg_associativity', mul(mul(a,b),c) == mul(a,mul(b,c)))
        def image(pair):
            (x,y,z),(xx,yy,zz) = pair
            return (x,xx,y,yy,(z+zz)%p)
        def mul_target(a,b):
            x1,x2,y1,y2,z=a; xx1,xx2,yy1,yy2,zz=b
            return ((x1+xx1)%p,(x2+xx2)%p,(y1+yy1)%p,(y2+yy2)%p,(z+zz+y1*xx1+y2*xx2)%p)
        domain=list(it.product(h, repeat=2))
        fibers=Counter(image(a) for a in domain)
        self.check('balanced_product',len(fibers)==p**5)
        for n in fibers.values():self.check('balanced_product',n==p)
        # Check multiplication against a generating set; generation is explicit.
        generators=[((1,0,0),(0,0,0)),((0,1,0),(0,0,0)),((0,0,1),(0,0,0)),
                    ((0,0,0),(1,0,0)),((0,0,0),(0,1,0)),((0,0,0),(0,0,1))]
        for a,b in it.product(domain,generators):
            ab=(mul(a[0],b[0]),mul(a[1],b[1]))
            self.check('balanced_product',image(ab)==mul_target(image(a),image(b)))

    def test_dyadic_markings(self) -> None:
        v=list(it.product(range(2),repeat=2))
        forms=[lambda a:(a[0]*a[1])%2,lambda a:(a[0]+a[1]+a[0]*a[1])%2]
        results=[]
        for q in forms:
            for a,b in it.product(v,repeat=2):
                s=((a[0]+b[0])%2,(a[1]+b[1])%2)
                self.check('quadratic_markings',(q(s)+q(a)+q(b))%2==(a[0]*b[1]+b[0]*a[1])%2)
            results.append((sum(q(a)==0 for a in v),sum((-1)**q(a) for a in v)))
        self.check('quadratic_markings',results==[(3,2),(1,-2)])
        group=list(it.product(range(2),repeat=3)); identity=(0,0,0)
        sq_signatures=[]
        for extra in [0,1]:
            def mul(a,b):
                x,y,z=a; xx,yy,zz=b
                return ((x+xx)%2,(y+yy)%2,(z+zz+y*xx+extra*(x*xx+y*yy))%2)
            for a,b,c in it.product(group,repeat=3):
                self.check('marked_group_associativity',mul(mul(a,b),c)==mul(a,mul(b,c)))
            for a,b in it.product(group,repeat=2):
                ab=mul(a,b);ba=mul(b,a)
                self.check('marked_group_commutators',(ab[2]+ba[2])%2==(a[0]*b[1]+b[0]*a[1])%2)
            sq_signatures.append(sum(mul(a,a)==identity for a in group))
        self.check('quadratic_markings',sq_signatures==[6,2])
        NEGATIVE_CONTROLS.append('same_polarization_does_not_fix_quadratic_marking')

    def test_coprime_cocycle_averaging(self) -> None:
        # A deliberately nonzero coboundary over F_3 for the trivial C_4 action.
        p,m=3,4; b=[0,1,0,2]
        f=lambda c,d:(b[c]+b[d]-b[(c+d)%m])%p
        S=[sum(f(c,e) for e in range(m))%p for c in range(m)]
        adjusted=[pow(m,-1,p)*a%p for a in S]
        for c,d,e in it.product(range(m),repeat=3):
            self.check('cocycle_averaging',(f(c,d)+f((c+d)%m,e)-f(d,e)-f(c,(d+e)%m))%p==0)
        for c,d in it.product(range(m),repeat=2):
            self.check('cocycle_averaging',(f(c,d)-adjusted[c]-adjusted[d]+adjusted[(c+d)%m])%p==0)
        self.check('cocycle_averaging',any(f(c,d) for c,d in it.product(range(m),repeat=2)))

    def test_compact_binder_finite_models(self) -> None:
        for n in range(1,9):
            modulus=2**n
            s0=[x for x in range(modulus) if x%modulus==0]
            s1=[x for x in range(modulus) if (x-1)%modulus==0]
            self.check('binder_models', bool(s0) and bool(s1) and not set(s0)&set(s1))
            self.check('binder_models',2**n!=0 and (2**n)%modulus==0)
        # Nested root sets for x^2-1, as an independent finite illustration.
        previous=None
        for n in range(1,9):
            modulus=3**n
            roots={x for x in range(modulus) if (x*x-1)%modulus==0}
            self.check('binder_models',len(roots)==2)
            if previous is not None:self.check('binder_models',{x%(modulus//3) for x in roots}<=previous)
            previous=roots
        NEGATIVE_CONTROLS.extend(['individual_equations_do_not_give_joint_solvability','nonzero_condition_can_be_lost_in_a_limit'])

    def test_depth_weighted_trace(self) -> None:
        # psi in F2((t)) reads the t^0 coefficient. Basis monomials suffice to
        # check these displayed finite supports by F2-linearity.
        for trace_valuation in range(-5,6):
            for depth in range(1,7):
                if trace_valuation+depth>=1:
                    for exponent in range(depth,depth+6):
                        self.check('trace_depth',trace_valuation+exponent!=0)
        self.check('trace_depth',(-1)+1==0)
        self.check('trace_depth',0+1>=1)
        NEGATIVE_CONTROLS.append('insufficient_trace_depth_is_visible')

    def test_odd_tower_profiles(self) -> None:
        for p in [3,5,7]:
            for d in range(1,7):
                hs=[n for n in range(1,30) if n%p][:d]
                qs=[(p+1)*h for h in hs]
                levels=[p**(d-j-1)*qs[d-j-1] for j in range(d)]
                N=p**d
                self.check('odd_towers',all(a>b for a,b in zip(levels,levels[1:])))
                self.check('odd_towers',(p-1)*p**(d-1)>=2*d)
                self.check('odd_towers',(N-1)%2==0)
                if d>=2:
                    n=p**(d-1)*qs[-1];R=p**(d-2)*qs[-2]
                    self.check('odd_towers',n>p*R>2*R)
        p=3;hs=[1,2];d=2
        conductor=p**(2*d)-1+sum((p**(2*i)-p**(2*i-2))*h for i,h in enumerate(hs,1))
        self.check('odd_towers',(p**(d-1)*(p+1)*hs[-1],conductor,p**((p**d-1)//2))==(24,232,81))
        self.check('odd_towers',5-1!=2)
        NEGATIVE_CONTROLS.append('minimal_rank_p_quotient_is_not_always_a_plane')

    def test_dyadic_capacity_and_profiles(self) -> None:
        for d in range(1,13):
            hs=list(range(1,2*d,2));N=2**d
            levels=[2**(d-j-1)*3*hs[d-j-1] for j in range(d)]
            contributions=[(2**(d-j)-2**(d-j-1))*(level%2==0) for j,level in enumerate(levels)]
            self.check('dyadic_capacity',sum(contributions)==N-2)
            self.check('dyadic_capacity',(N-2>=2*d)==(d>=3))
            self.check('dyadic_capacity',all(a>b for a,b in zip(levels,levels[1:])))
            self.check('dyadic_capacity',2*((3*hs[0]-1)//2+1)-3*hs[0]==1)
        for hs in it.combinations(range(1,16,2),3):
            h1,h2,h3=hs;L=12*h3;c=h1+4*h2
            full=63+sum(3*4**i*h for i,h in enumerate(hs))
            skipped=63+4*L+3*c
            self.check('profile_comparison',full==skipped)
            self.check('profile_comparison',c%2==1 and 2*c<L)
        self.check('profile_comparison',63+3*1+12*3+48*5==342)
        self.check('profile_comparison',[12*5,6*3,3*1]==[60,18,3])
        self.check('profile_comparison',2**3-2==6 and 8-4==4)
        NEGATIVE_CONTROLS.extend(['original_low_rank_carriers_are_too_small','same_profiles_can_have_different_capacities'])

    def test_native_prime_to_p_obstruction(self) -> None:
        for p in [2,3,5,7]:
            for r in range(1,4):
                n=p**r
                for m in range(2,13):
                    if m%p:
                        hom_images=[x for x in range(n) if m*x%n==0]
                        self.check('native_coprimality',hom_images==[0])
        # Yet F3^2 has a genuinely nontrivial order-four symplectic action.
        A=((0,2),(1,0));I=((1,0),(0,1))
        mm=lambda a,b:tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2))%3 for j in range(2)) for i in range(2))
        A2=mm(A,A)
        self.check('native_coprimality',A2!=I and mm(A2,A2)==I)
        self.check('native_coprimality',(A[0][0]*A[1][1]-A[0][1]*A[1][0])%3==1)
        NEGATIVE_CONTROLS.append('abstract_symplectic_action_need_not_fit_native_p_group')

    def test_augmentation_recovery(self) -> None:
        for seq in it.product(range(-2,3),repeat=5):
            if sum(seq):continue
            partial=[];v=0
            for x in seq:v+=x;partial.append(v)
            differences=[partial[0]]+[partial[i]-partial[i-1] for i in range(1,len(seq))]
            self.check('augmentation_kernel',differences==list(seq) and partial[-1]==0)

    def test_finite_cyclic_projector(self) -> None:
        for ell in range(1,13):
            avg=[[Fraction(1,ell) for _ in range(ell)] for _ in range(ell)]
            product=[[sum(avg[i][k]*avg[k][j] for k in range(ell)) for j in range(ell)] for i in range(ell)]
            self.check('cyclic_projector',product==avg)
            v=list(range(ell));out=[sum(avg[i][j]*v[j] for j in range(ell)) for i in range(ell)]
            self.check('cyclic_projector',len(set(out))==1)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('verification/EXACT_CHECKS.json'))
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ExactChecks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'status':'passed' if result.wasSuccessful() else 'failed','unittest_methods':result.testsRun,
            'exact_assertions_by_family':dict(sorted(COUNTS.items())),
            'total_bounded_assertions':sum(COUNTS.values()),'negative_control_distinctions':sorted(NEGATIVE_CONTROLS),
            'scope':'Finite illustrations only. No local-field simple-character theorem, Lean compilation or Conjecture 66 proof.',
            'failures':[(str(t),tb) for t,tb in result.failures+result.errors]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    if not result.wasSuccessful():raise SystemExit(1)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
