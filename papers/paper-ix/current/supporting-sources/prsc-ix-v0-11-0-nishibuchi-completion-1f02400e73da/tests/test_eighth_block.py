"""Eighth-block semantic and release contracts. Author: Komorebi P."""
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
import eighth_regressions as reg

class EighthBlockTests(unittest.TestCase):
    def test_exact_cumulative_inventory(self):
        x=json.loads((ROOT/'provenance/v0.8.0/inventory.json').read_text())
        self.assertEqual((len(x['modules']),x['theorem_count'],x['definition_count']),(47,526,107))
    def test_added_census(self):
        a=json.loads((ROOT/'provenance/seventh_block/inventory.json').read_text());b=json.loads((ROOT/'provenance/v0.8.0/inventory.json').read_text())
        self.assertEqual((len(b['modules'])-len(a['modules']),b['theorem_count']-a['theorem_count'],b['definition_count']-a['definition_count']),(9,87,13))
    def test_all_38_upstream_proofs_unchanged(self):
        a=json.loads((ROOT/'provenance/seventh_block/inventory.json').read_text())
        self.assertEqual(len(a['modules']),38)
        for m in a['modules']:self.assertEqual(verify.sha(ROOT/m['source']),m['sha256'])
    def test_no_full_coverage_promotion(self):
        a=json.loads((ROOT/'provenance/v0.8.0/coverage.json').read_text())
        self.assertEqual(a['counts']['lean_checked'],23)
        e=next(e for e in a['entries'] if e['id']=='7.5')
        self.assertEqual(e['status'],'PENDING_LEAN');self.assertFalse(e['targets'])
        self.assertIn('p<=j<mp',e['scope'])
    def test_actual_standard_window_signature(self):
        s=(ROOT/'formalization/StandardWindowDwork.lean').read_text()
        sig=s.split('theorem standard_window_global_bound',1)[1].split(':= by',1)[0]
        self.assertIn('(hj : j<p)',sig);self.assertIn('min k (m*n)',sig)
        self.assertIn('coeffPadic p m j hj',sig)
        self.assertNotIn('flat',sig);self.assertNotIn('precision',sig)
    def test_original_rational_sequence(self):
        s=(ROOT/'formalization/StandardWindowPrecision.lean').read_text()
        self.assertIn('Congruential.coeff (m*p) j',s)
        self.assertIn('Congruential.unnormalized (m*p) j',s)
        self.assertIn('lifted_difference_coe',s)
    def test_full_family_m1_is_explicit(self):
        s=(ROOT/'formalization/StandardWindowPrecision.lean').read_text()
        self.assertIn('theorem modulus_p_complete_family',s)
        self.assertIn('unnormalized_window_precision p 1',s)
    def test_actual_reciprocal_bridge(self):
        s=(ROOT/'formalization/StandardWindowDwork.lean').read_text()
        self.assertIn('Congruential.packet_times_kernel',s)
        self.assertIn('PowerSeries.eq_inv_iff_mul_eq_one',s)
        self.assertIn('kernel_encoding',s)
    def test_lattice_not_field_divisibility(self):
        s=(ROOT/'formalization/HurwitzDworkClosure.lean').read_text()
        self.assertIn('EGF.decode f n ∈ PadicInt.subring p',s)
        self.assertIn('(p:ℤ_[p])^s ∣ x',s)
        self.assertIn('integral_inverse',s)
    def test_product_contains_correction(self):
        s=(ROOT/'formalization/DworkAlgebra.lean').read_text()
        sig=s.split('theorem B_mul',1)[1].split(':= by',1)[0]
        self.assertIn('middle D p (p^2) f g - middle D p p f g',sig)
    def test_no_closure_hidden_in_definition(self):
        s=(ROOT/'formalization/DworkClosure.lean').read_text()
        definition=s.split('def flat',1)[1].split('@[simp]',1)[0]
        self.assertIn('∀ s, (B D p ^ s) f ∈ I',definition)
        self.assertNotIn('f*g',definition)
    def test_actual_euler_nonsingular_premise(self):
        s=(ROOT/'formalization/EulerDefect.lean').read_text()
        self.assertIn('(hc : ¬p∣c)',s)
        self.assertIn('iterated_commutator',s)
        self.assertIn('euler_pivot_unit',s)
    def test_new_negative_controls_registered(self):
        s=(ROOT/'scripts/verify.py').read_text()
        for tag in ['false_defect_derivation','false_window_extra_power','false_nonunit_euler_pivot','false_composite_binomial_divisibility']:self.assertIn(tag,s)
    def test_p3_j2_exact_row(self):
        self.assertEqual(reg.coefficients(6,2,3),[Q(1),Q(-1,28),Q(425,364),Q(-2039759,2660)])
    def test_p3_j2_sharp_difference(self):
        cs=reg.coefficients(6,2,3)
        d=reg.difference(lambda n:cs[n],1,2,1)
        self.assertEqual(d,Q(-949959,1235));self.assertEqual(reg.valuation(d,3),2)
        self.assertFalse(reg.precision(d,3,3))
    def test_bad_residue_normalization(self):
        self.assertEqual(reg.valuation(reg.coefficients(6,3,1)[1],3),-1)
    def test_cubic_defect(self):
        f=lambda d:Q(6 if d==3 else 0)
        self.assertEqual(reg.defect(f,3,1,0,True),-2)
    def test_integral_inverse_not_trivial(self):
        rec=reg.reciprocal([Q(1),Q(1)],30)
        self.assertEqual(rec,[Q((-1)**n*factorial(n)) for n in range(31)])
        self.assertTrue(reg.precision(reg.defect(lambda n:rec[n],3,3,0),3,3))
    def test_zero_has_infinite_precision(self):
        self.assertIsNone(reg.valuation(Q(0),5));self.assertTrue(reg.precision(0,5,1000))
    def test_p2_window(self):
        for j in [0,1]:
            cs=reg.coefficients(2,j,8)
            self.assertTrue(reg.precision(reg.difference(lambda n:cs[n],1,3,3),2,3))
    def test_zero_step(self):
        self.assertEqual(reg.difference(lambda n:n*n,0,5,4),0)
        self.assertEqual(reg.difference(lambda n:n*n,0,0,4),16)
    def test_bad_prime_input(self):
        for p in [0,1,4,9,True]:
            with self.assertRaises(ValueError):reg.prime(p)
    def test_invalid_index_input(self):
        with self.assertRaises(ValueError):reg.difference(lambda n:n,-1,2,0)
        with self.assertRaises(ValueError):reg.coefficients(3,3,2)
    def test_nonunit_pivot(self):self.assertEqual(reg.valuation(3,3),1)
    def test_premise_nondivisibility_not_vacuous(self):
        self.assertEqual(reg.valuation(4,3),0)
    def test_ordinary_and_hurwitz_products_differ(self):
        f=lambda d:Q(1 if d==1 else 0)
        self.assertEqual(reg.hurwitz(f,f,2),2)
    def test_negative_power_control_rejected_by_gate(self):
        self.assertTrue(verify.control_passed(1,'error: unsolved goals', 'false_window_extra_power'))
        self.assertFalse(verify.control_passed(124,'timed out', 'false_window_extra_power'))

if __name__=='__main__':unittest.main()
