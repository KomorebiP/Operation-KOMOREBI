"""All-residue specification, preservation, and verification-boundary tests.
These tests complement the actual Lean compiler and axiom audit; they are not proofs.
Author: Komorebi P.
"""
from pathlib import Path
from fractions import Fraction as Q
import copy,json,sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
import tenth_regressions as reg

class TenthBlockTests(unittest.TestCase):
    def test_cumulative_census(self):
        v=verify.source_inventory()
        self.assertEqual((len(v['modules']),v['theorem_count'],v['definition_count']),(70,753,148))
    def test_added_census(self):
        a=json.loads((ROOT/'provenance/v0.9.0/inventory.json').read_text());b=verify.source_inventory()
        self.assertEqual((len(b['modules'])-len(a['modules']),b['theorem_count']-a['theorem_count'],b['definition_count']-a['definition_count']),(13,123,20))
    def test_all_57_upstream_sources_unchanged(self):
        a=json.loads((ROOT/'provenance/v0.9.0/inventory.json').read_text())
        self.assertEqual(len(a['modules']),57)
        for m in a['modules']:self.assertEqual(verify.sha(ROOT/m['source']),m['sha256'])
    def test_only_last_named_item_promoted(self):
        a=json.loads((ROOT/'provenance/v0.9.0/coverage.json').read_text());b=json.loads((ROOT/'coverage.json').read_text())
        aa={e['id'] for e in a['entries'] if e['status']=='LEAN_CHECKED'}
        bb={e['id'] for e in b['entries'] if e['status']=='LEAN_CHECKED'}
        self.assertEqual(bb-aa,{'7.5'});self.assertEqual(len(bb),24)
    def test_conjectures_not_promoted(self):
        a=json.loads((ROOT/'coverage.json').read_text())
        self.assertEqual({e['id'] for e in a['entries'] if e['status']=='CONJECTURAL'},{'13.2','13.3'})
        self.assertEqual(sum(e['status']=='CLASSICAL_INPUT' for e in a['entries']),3)
    def test_global_signature_has_no_flatness_premise(self):
        s=(ROOT/'formalization/Theorem75.lean').read_text().split('theorem global_finite_difference',1)[1].split(':=',1)[0]
        self.assertIn('(hj : j<m*p)',s);self.assertNotIn('(hj : j<p)',s)
        self.assertNotIn('Flat',s);self.assertNotIn('Weighted',s);self.assertNotIn('flat',s)
        self.assertIn('(hm : m∣p-1)',s);self.assertIn('(hmpos : 0<m)',s)
        self.assertIn('Congruential.unnormalized',s);self.assertIn('Congruential.coeff',s)
    def test_prime_hypothesis_is_explicit(self):
        s=(ROOT/'formalization/Theorem75.lean').read_text()
        self.assertIn('variable (p : ℕ) [Fact p.Prime]',s)
    def test_normalization_loss_not_removed(self):
        s=(ROOT/'formalization/AllResidueEuler.lean').read_text()
        self.assertIn('padicValNat p j.factorial',s);self.assertIn('factorial_loss_transfer',s)
    def test_ideal_statement_uses_Zp(self):
        s=(ROOT/'formalization/AllResidueEuler.lean').read_text()
        self.assertIn('(p:ℤ_[p])^(min k (m*n)) ∣',s)
        self.assertIn('unnormalizedLift_coe',s)
    def test_actual_ratio_equation_not_assumed(self):
        s=(ROOT/'formalization/RatioRiccati.lean').read_text()
        sig=s.split('theorem ratio_riccati ',1)[1].split(':= by',1)[0]
        self.assertNotIn('Flat',sig);self.assertIn('ratioSeries',sig)
        self.assertIn('ratio_cleared N hN',s);self.assertIn('original_derivative',s)
    def test_picard_solution_flatness_is_conclusion(self):
        s=(ROOT/'formalization/RiccatiFlatPropagation.lean').read_text()
        sig=s.split('theorem riccati_solution_flat',1)[1].split(':= by',1)[0]
        self.assertIn('(hq : Flat p q)',sig);self.assertNotIn('(hy : Flat p y)',sig)
        self.assertIn('picard_matches',s);self.assertIn('B_iterate_prefix',s)
    def test_exp_log_is_actual_substitution(self):
        s=(ROOT/'formalization/WeightedDworkTransfer.lean').read_text()
        self.assertIn('f.subst (exp ℚ_[p]-1)',s);self.assertIn('subst_log_exp_sub_one',s)
        self.assertIn('derivative_subst',s)
    def test_conditional_criterion_cannot_replace_final_target(self):
        inv=verify.source_inventory();real=Path.read_text
        def changed(path,*a,**k):
            t=real(path,*a,**k)
            if path==ROOT/'coverage.json':
                c=json.loads(t);next(e for e in c['entries'] if e['id']=='7.5')['targets']=['KomorebiPaperIX.DworkCriterion.saturated_bound_of_flat'];return json.dumps(c)
            return t
        with patch.object(Path,'read_text',changed):
            with self.assertRaisesRegex(ValueError,'Missing unconditional'):verify.validate_coverage(inv)
    def test_explicit_failed_draft_is_retained(self):
        self.assertTrue((ROOT/'preserved_checkpoint/ThetaWeighted.lean').is_file())
        self.assertNotEqual(verify.sha(ROOT/'preserved_checkpoint/ThetaWeighted.lean'),verify.sha(ROOT/'formalization/ThetaWeighted.lean'))
    def test_singular_second_exact(self):
        cs=reg.coefficients(6,3,3);d=6*reg.difference(cs,1,2,1)
        self.assertEqual(d,Q(-1464768,8645));self.assertEqual(reg.valuation(d,3),2)
    def test_upper_regular_second_exact(self):
        cs=reg.coefficients(6,4,3);d=24*reg.difference(cs,1,2,1)
        self.assertEqual(d,Q(-102745512,2377375));self.assertEqual(reg.valuation(d,3),2)
    def test_reciprocal_matches_recurrence(self):
        self.assertEqual(reg.coefficients(10,7,4),reg.reciprocal_coefficients(10,7,4))
    def test_old_no_loss_stays_false(self):
        d=reg.difference(reg.coefficients(6,3,2),1,1,1)
        self.assertFalse(reg.precision(d,3,1));self.assertTrue(reg.precision(6*d,3,1))
    def test_invalid_parameters_rejected(self):
        for args in [(4,1,0),(3,0,0),(5,3,0),(3,2,6),(True,1,0)]:
            with self.assertRaises(ValueError):reg.parameters(*args)
    def test_zero_step_and_zero_valuation(self):
        self.assertEqual(reg.difference([Q(7)],0,5,0),0)
        self.assertIsNone(reg.valuation(0,3));self.assertTrue(reg.precision(0,3,10000))
    def test_incomplete_stencil_rejected(self):
        with self.assertRaises(ValueError):reg.difference([Q(1)],1,1,0)
    def test_composite_counterexample_really_false(self):self.assertEqual((2**81-2**9)%81,54)
    def test_theta_weighted_stability(self):
        f=[Q(1),Q(2),Q(-1),Q(1,3),Q(2,3)]
        self.assertTrue(reg.weighted(f,3));self.assertTrue(reg.weighted(reg.theta_defect(f,3),3))
    def test_picard_prefix_is_not_assumed(self):
        q=[Q(0),Q(2),Q(1,3),Q(-1),Q(4)]
        expected=reg.fixedpoint(q,2)
        for r in range(5):self.assertEqual(reg.picard(q,2,r)[:r+1],expected[:r+1])
    def test_new_negative_controls_registered(self):
        s=(ROOT/'scripts/verify.py').read_text()
        for n in ['false_global_extra_power','false_global_no_factorial_loss','false_composite_frobenius_square','false_centered_ratio_constant']:self.assertIn(n,s)
    def test_unknown_symbol_not_counted_as_negative(self):
        # Unknown imports already fail closed in the inherited checker.
        self.assertFalse(verify.control_passed(1,'error: unknown module Missing','false_global_extra_power'))

if __name__=='__main__':unittest.main(verbosity=2)
