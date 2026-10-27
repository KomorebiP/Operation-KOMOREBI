"""Exact reader regressions. Finite examples only, never a Lean replay."""
from __future__ import annotations
from fractions import Fraction
from itertools import product
from pathlib import Path
import sys, unittest, json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'inherited_baseline/original_companion'))
from projector_seed_residuals.residual import reconstruct_digits, compatible_residue_tower

class ReaderRegressions(unittest.TestCase):
    def test_01_canonical_towers_exhaustively(self):
        self.towers=0
        for p in (2,3,5,7):
            for n in range(p**4):
                tower=[n%p**m for m in range(1,5)]
                got=reconstruct_digits(tower,p);prev=0
                for m,x in enumerate(tower,1):
                    self.assertEqual(got[m-1],(x-prev)//p**(m-1))
                    self.assertEqual(got[m-1],(x//p**(m-1))%p)
                    self.assertTrue(0<=got[m-1]<p);prev=x
                self.assertEqual(sum(a*p**i for i,a in enumerate(got)),n)
                self.towers+=1
        self.assertEqual(self.towers,3123)

    def test_02_noncanonical_representatives(self):
        for p in (2,3,5,7):
            for n in range(p**3):
                original=[n%p**m for m in range(1,4)]
                expected=reconstruct_digits(original,p)
                for shift in (-3,-1,1,4):
                    altered=[x+shift*p**m for m,x in enumerate(original,1)]
                    self.assertEqual(reconstruct_digits(altered,p),expected)

    def test_03_old_display_is_not_integer_digit(self):
        self.assertEqual(reconstruct_digits([4,19],5),[4,3])
        self.assertNotEqual(Fraction(19,5),3)
        self.assertNotEqual(Fraction(19,5).denominator,1)

    def test_04_incompatible_tower_rejected(self):
        self.assertFalse(compatible_residue_tower([4,18],5))
        with self.assertRaises(ValueError):reconstruct_digits([4,18],5)

    def test_05_bad_base_rejected(self):
        for base in (-1,0,1):
            with self.assertRaises(ValueError):reconstruct_digits([0],base)

    def test_06_nonconvergence_despite_same_residue(self):
        seq=[0,3]*8
        self.assertEqual({x%3 for x in seq},{0})
        self.assertEqual({x%9 for x in seq},{0,3})

    def test_07_two_existentials_not_common_witness(self):
        A={0};B={1};self.assertTrue(A);self.assertTrue(B);self.assertFalse(A&B)

    def test_08_zero_selection_within_capacity(self):
        for c in product(range(4),repeat=3):
            m=(0,0,0);self.assertTrue(all(mi<=ci for mi,ci in zip(m,c)))
            self.assertEqual(sum(mi*d for mi,d in zip(m,(1,1,2))),0)

    def test_09_nonzero_dimension_has_nonzero_input(self):
        dims=(1,1,2)
        for m in product(range(4),repeat=3):
            self.assertEqual(sum(x*d for x,d in zip(m,dims))>0,any(m))

    def test_10_fixed_determinant_not_copy_closed(self):
        chi=-1
        self.assertEqual(chi*chi,1);self.assertNotEqual(chi*chi,chi)

    def test_11_pairwise_not_joint_occupancy(self):
        labels=[(0,0,0),(0,0,1),(0,1,0),(1,0,1),(1,1,0),(1,1,1)]
        target=(0,1,1)
        for inds in ((0,1),(0,2),(1,2)):
            self.assertTrue(any(all(x[i]==target[i] for i in inds) for x in labels))
        self.assertNotIn(target,labels)

    def test_12_exact_precision_loss(self):
        C=((1,1,2),(1,-1,0),(1,1,-1));v=(4,4,0)
        b=tuple(sum(x*y for x,y in zip(row,v)) for row in C)
        self.assertEqual(b,(8,0,8));self.assertTrue(any(x%8 for x in v))
        self.assertTrue(all(x%8==0 for x in b));self.assertTrue(any(x%16 for x in b))

    def test_13_singular_nodes_can_die(self):
        roots9=[x for x in range(9) if x*x%9==0]
        roots27=[x for x in range(27) if x*x%27==0]
        self.assertEqual(roots9,[0,3,6]);self.assertEqual(roots27,[0,9,18])
        self.assertEqual({x%9 for x in roots27},{0})

if __name__=='__main__':unittest.main(verbosity=2)
