"""Dyadic formula, provenance and release-scope regressions. Author: Komorebi P."""
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
import third_regressions as reg

class ThirdBlockTests(unittest.TestCase):
    def test_exact_four_new_registered_items(self):
        old=json.loads((ROOT/'provenance/second_block/coverage.json').read_text())
        new=json.loads((ROOT/'provenance/third_block/coverage.json').read_text())
        oldids={e['id'] for e in old['entries'] if e['status']=='LEAN_CHECKED'}
        newids={e['id'] for e in new['entries'] if e['status']=='LEAN_CHECKED'}
        self.assertEqual(newids-oldids,{'5.1','5.2','5.3','5.4'})
        self.assertLessEqual(oldids,newids)
    def test_new_theorem_and_definition_census(self):
        old=json.loads((ROOT/'provenance/second_block/inventory.json').read_text())
        new=json.loads((ROOT/'provenance/third_block/inventory.json').read_text())
        self.assertEqual(new['theorem_count']-old['theorem_count'],56)
        self.assertEqual(new['definition_count']-old['definition_count'],16)
        self.assertEqual(len(new['modules'])-len(old['modules']),4)
    def test_all_thirteen_upstream_modules_preserved(self):
        old=json.loads((ROOT/'provenance/second_block/inventory.json').read_text())
        for entry in old['modules']:
            self.assertEqual(verify.sha(ROOT/entry['source']),entry['sha256'])
    def test_no_global_difference_promotion(self):
        c=json.loads((ROOT/'provenance/third_block/coverage.json').read_text())
        self.assertEqual(next(e for e in c['entries'] if e['id']=='7.5')['status'],'PENDING_LEAN')
        self.assertEqual(sum(e['status']=='CONJECTURAL' for e in c['entries']),2)
    def test_actual_padic_integer_statement(self):
        src=(ROOT/'formalization/DyadicReconstruction.lean').read_text()
        self.assertIn('(2:ℤ_[2])^(2*M+2) ∣ (eulerEven n : ℤ_[2]) - truncationPadic n M',src)
        self.assertIn('theorem normalized_error_integral',src)
    def test_removable_zero_cleared(self):
        src=(ROOT/'formalization/DyadicSeries.lean').read_text()
        self.assertIn('inverseSeries * sinhAt 1 ^ 2 = X^2',src)
        self.assertIn('theorem source_shift_identity',src)
    def test_beta_anchors(self):
        self.assertEqual(reg.betas(4),[Q(1),-Q(1,3),Q(1,15),-Q(2,189),Q(1,675)])
    def test_source_nonzero_units(self):
        for n in range(21): self.assertEqual(reg.v2(reg.source_even_degree(2*n)),0)
    def test_kernel_and_inverse_odd_denominators(self):
        for value in [reg.alpha(n) for n in range(21)]+reg.betas(20):
            self.assertEqual(value.denominator%2,1)
    def test_source_rejects_odd_and_negative_degrees(self):
        for n in [-2,-1,1,3,11]:
            with self.assertRaises(ValueError): reg.source_even_degree(n)
    def test_invalid_depth_and_short_coefficients(self):
        for row,depth,b in [(-1,0,[Q(1)]),(2,-1,reg.betas(2)),(2,2,[Q(1)])]:
            with self.assertRaises(ValueError): reg.truncation(row,depth,b)
    def test_zero_valuation_is_not_silently_zero(self):
        with self.assertRaises(ValueError): reg.v2(Q(0))
    def test_zero_row_and_full_retention(self):
        b=reg.betas(8)
        for n in range(9):
            self.assertEqual(reg.truncation(n,100,b),reg.euler_numbers(16)[2*n])
        self.assertEqual(reg.truncation(0,100,b),1)
    def test_manuscript_error_valuations(self):
        b=reg.betas(4)
        self.assertEqual(reg.v2(Q(1385)-reg.truncation(4,0,b)),5)
        self.assertEqual(reg.v2(Q(1385)-reg.truncation(4,3,b)),15)
    def test_excess_precision_detected(self):
        b=reg.betas(4);error=Q(1385)-reg.truncation(4,0,b)
        self.assertEqual((error/2**5).denominator%2,1)
        self.assertEqual((error/2**6).denominator%2,0)
    def test_bernoulli_formula_as_finite_mirror_only(self):
        from math import factorial
        b=reg.betas(12);br=reg.bernoulli_numbers(24)
        self.assertEqual(br[1],-Q(1,2))
        for m in range(1,13):
            self.assertEqual(b[m],-Q(2**(2*m)*(2*m-1),factorial(2*m))*br[2*m])

if __name__=='__main__': unittest.main(verbosity=2)
