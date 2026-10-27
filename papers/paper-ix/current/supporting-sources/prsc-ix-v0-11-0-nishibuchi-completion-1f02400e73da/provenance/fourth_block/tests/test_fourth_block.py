"""Fourth-block semantic boundaries and release regressions. Author: Komorebi P."""
from fractions import Fraction as Q
from math import inf
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
import fourth_regressions as reg

class FourthBlockTests(unittest.TestCase):
    def test_exact_three_new_items(self):
        old=json.loads((ROOT/'provenance/third_block/coverage.json').read_text())
        new=json.loads((ROOT/'coverage.json').read_text())
        oldids={e['id'] for e in old['entries'] if e['status']=='LEAN_CHECKED'}
        newids={e['id'] for e in new['entries'] if e['status']=='LEAN_CHECKED'}
        self.assertEqual(newids-oldids,{'7.2','7.3','7.4'});self.assertLessEqual(oldids,newids)
    def test_added_census(self):
        old=json.loads((ROOT/'provenance/third_block/inventory.json').read_text());new=verify.source_inventory()
        self.assertEqual((new['theorem_count']-old['theorem_count'],new['definition_count']-old['definition_count'],len(new['modules'])-len(old['modules'])),(53,7,4))
    def test_all_seventeen_upstream_sources(self):
        old=json.loads((ROOT/'provenance/third_block/inventory.json').read_text())
        self.assertEqual(len(old['modules']),17)
        for m in old['modules']:self.assertEqual(verify.sha(ROOT/m['source']),m['sha256'])
    def test_precise_remaining_items(self):
        c=json.loads((ROOT/'coverage.json').read_text())
        self.assertEqual({e['id'] for e in c['entries'] if e['status']=='PENDING_LEAN'},
            {'6.2','7.5','8.3','8.5','9.1','9.2','10.1'})
    def test_zero_valuation_is_infinite(self):self.assertEqual(reg.valuation(0,3),inf)
    def test_nonprime_valuation_rejected(self):
        for p in [0,1,4,9]:
            with self.assertRaises(ValueError):reg.valuation(Q(1),p)
    def test_negative_indices_rejected(self):
        for args in [(-1,0,1),(0,-1,1),(0,0,-1)]:
            with self.assertRaises(ValueError):reg.difference(lambda n:n,*args)
    def test_empty_sample_rejected(self):
        with self.assertRaises(ValueError):reg.coefficients([])
    def test_square_coefficients(self):self.assertEqual(reg.coefficients([0,1,4,9]),[0,1,2,0])
    def test_square_interpolant(self):self.assertEqual(reg.eval_newton([0,1,2],7),49)
    def test_finite_sample_boundary(self):
        with self.assertRaises(ValueError):reg.sample_difference([0],0,1)
        self.assertNotEqual(reg.difference(lambda n:n,0,1),reg.difference(lambda n:0,0,1))
    def test_finite_stencil_endpoint(self):self.assertEqual(reg.sample_difference([0,1,4,9],1,2),2)
    def test_empty_binomial_expansion(self):self.assertEqual(reg.eval_newton([],17),0)
    def test_high_difference_zero(self):self.assertEqual(reg.difference(lambda n:reg.eval_newton([2,-3,7],n),4,3),0)
    def test_binomial_weight_improvement(self):
        c=[0,81,3,3,81]
        self.assertEqual(reg.weighted_bound(c,3,1,3),2)
        self.assertEqual(reg.difference(lambda n:reg.eval_newton(c,n),3,1),180)
        self.assertEqual(reg.valuation(180,3),2)
    def test_cancellation_zero_not_failure(self):
        c=[0,1,-1]
        self.assertEqual(reg.difference(lambda n:reg.eval_newton(c,n),1,1),0)
        self.assertEqual(reg.weighted_bound(c,1,1,3),0)
    def test_nonintegral_weights_rejected(self):
        with self.assertRaises(ValueError):reg.weighted_bound([Q(1,3)],0,0,3)
    def test_nonunit_mode_rejected(self):
        for u in [Q(0),Q(3),Q(1,3)]:
            with self.assertRaises(ValueError):reg.unit_mode(u,0,1,3)
    def test_sharp_unit_gain(self):
        self.assertEqual(reg.unit_mode(2,0,2,5),225)
        self.assertEqual(reg.valuation(225,5),2)
    def test_constant_unit_and_zero_step(self):
        self.assertEqual(reg.unit_mode(1,3,4,5),0)
        self.assertEqual(reg.unit_mode(2,3,4,5,0),0)
    def test_p_two_is_included(self):self.assertGreaterEqual(reg.valuation(reg.unit_mode(3,2,4,2),2),4)
    def test_zero_order_is_identity(self):self.assertEqual(reg.unit_mode(Q(2,3),4,0,5),Q(16,81))
    def test_stencil_condition_in_formal_source(self):
        s=(ROOT/'formalization/FiniteMahler.lean').read_text()
        self.assertIn('(hns : n+s ≤ N)',s)
        self.assertIn('theorem finite_sample_difference',s)
    def test_zero_safe_padic_definition(self):
        s=(ROOT/'formalization/PadicDifferenceBounds.lean').read_text()
        self.assertIn('if x = 0 then ⊤',s);self.assertIn('nat_le_order_iff',s)
    def test_unit_premise_not_silent(self):
        s=(ROOT/'formalization/UnitModeDifferences.lean').read_text()
        self.assertIn('(u : ℤ_[p]ˣ)',s);self.assertIn('PadicInt.ker_toZMod',s)

if __name__=='__main__':unittest.main(verbosity=2)
