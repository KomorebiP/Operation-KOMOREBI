"""Seventh-block release contracts and independent finite tests. Author: Komorebi P."""
from fractions import Fraction as Q
from pathlib import Path
import json,sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
import seventh_regressions as reg

class SeventhBlockTests(unittest.TestCase):
    def test_exact_one_new_item(self):
        a=json.loads((ROOT/'provenance/sixth_block/coverage.json').read_text())
        b=json.loads((ROOT/'coverage.json').read_text())
        old={e['id'] for e in a['entries'] if e['status']=='LEAN_CHECKED'}
        new={e['id'] for e in b['entries'] if e['status']=='LEAN_CHECKED'}
        self.assertEqual(new-old,{'8.5'});self.assertLessEqual(old,new)
    def test_cumulative_census(self):
        x=verify.source_inventory()
        self.assertEqual((len(x['modules']),x['theorem_count'],x['definition_count']),(38,439,94))
    def test_new_census(self):
        a=json.loads((ROOT/'provenance/sixth_block/inventory.json').read_text());b=verify.source_inventory()
        self.assertEqual((len(b['modules'])-len(a['modules']),b['theorem_count']-a['theorem_count'],b['definition_count']-a['definition_count']),(7,57,10))
    def test_upstream_31_sources_preserved(self):
        x=json.loads((ROOT/'provenance/sixth_block/inventory.json').read_text())
        self.assertEqual(len(x['modules']),31)
        for m in x['modules']:self.assertEqual(verify.sha(ROOT/m['source']),m['sha256'])
    def test_only_global_bound_pending(self):
        c=json.loads((ROOT/'coverage.json').read_text())
        self.assertEqual({e['id'] for e in c['entries'] if e['status']=='PENDING_LEAN'},{'7.5'})
        self.assertEqual({e['id'] for e in c['entries'] if e['status']=='CONJECTURAL'},{'13.2','13.3'})
    def test_partial_targets_resolve_but_are_not_coverage(self):
        inv=verify.source_inventory();names={d['name'] for m in inv['modules'] for d in m['declarations']}
        e=next(e for e in json.loads((ROOT/'coverage.json').read_text())['entries'] if e['id']=='7.5')
        self.assertEqual(e['status'],'PENDING_LEAN');self.assertEqual(e['targets'],[])
        self.assertTrue(e['partial_targets']);self.assertLessEqual(set(e['partial_targets']),names)
    def test_period_has_no_global_estimate_import(self):
        m=next(m for m in verify.source_inventory()['modules'] if m['module']=='StandardWindowPeriod')
        self.assertEqual(m['imports'],['HurwitzInverse','WindowIndependence'])
        text=(ROOT/m['source']).read_text()
        self.assertIn('inverse_on_support',text);self.assertIn('inverse_prime_difference',text)
        signature=text.split('theorem uniform_standard_window_period',1)[1].split(':= by',1)[0]
        self.assertIn('(hn : 1≤n)',signature);self.assertIn('(hm : m ∣ p-1)',signature)
        self.assertNotIn('flat',signature);self.assertNotIn('precision',signature)
    def test_flatness_is_explicit_hypothesis(self):
        text=(ROOT/'formalization/DworkCriterion.lean').read_text()
        self.assertIn('(H : flat p (packed (m*p) e))',text)
        self.assertIn('defectIter p (p*(p-1))',text)
    def test_reuses_original_normalization(self):
        text=(ROOT/'formalization/GlobalEulerBoundary.lean').read_text()
        self.assertIn('Congruential.unnormalized N j',text)
        self.assertNotIn('def unnormalized',text)
    def test_source_actual_convolution(self):
        text=(ROOT/'formalization/HurwitzConvolution.lean').read_text()
        self.assertIn('n.choose',text);self.assertIn('prime_shift_convolution',text)
    def test_source_actual_reciprocal(self):
        text=(ROOT/'formalization/HurwitzInverse.lean').read_text()
        self.assertIn('Triangular.solve',text);self.assertIn('inverse_convolution',text)
        self.assertIn('convolution_left_eq_zero',text)
    def test_negative_controls_present(self):
        text=(ROOT/'scripts/verify.py').read_text()
        for tag in ['false_period_at_zero','false_nondivisor_period','false_period_mod_p_squared']:self.assertIn(tag,text)
    def test_prime_two(self):self.assertEqual(reg.period(2,1),1)
    def test_composite_rejected(self):
        with self.assertRaises(ValueError):reg.period(9,2)
    def test_nondivisor_rejected(self):
        with self.assertRaises(ValueError):reg.period(5,3)
    def test_zero_width_rejected(self):
        with self.assertRaises(ValueError):reg.period(5,0)
    def test_noncanonical_residue_rejected(self):
        with self.assertRaises(ValueError):reg.normalized_coefficients(6,6,1)
    def test_no_rational_field_reduction(self):
        with self.assertRaises(ValueError):reg.reduce_fraction(Q(1,3),3)
    def test_bad_reciprocal_constant_rejected(self):
        with self.assertRaises(ValueError):reg.reciprocal([0,1],3)
    def test_incomplete_stencil_rejected(self):
        with self.assertRaises(ValueError):reg.difference([1],1,1,0)
    def test_zero_order_difference(self):self.assertEqual(reg.difference([7],0,0,0),7)
    def test_p3_tail(self):self.assertEqual(reg.reduced(3,2,8),[1]+[2]*8)
    def test_p5_tail(self):
        e=reg.reduced(5,2,20)
        for n in range(1,19):self.assertEqual(e[n+2],e[n])
    def test_period_fails_at_zero(self):self.assertNotEqual(*reg.reduced(3,2,1))
    def test_nondivisor_counterexample(self):self.assertEqual(reg.reduced(5,3,3),[1,4,4,2])
    def test_no_automatic_extra_precision(self):
        cs=reg.normalized_coefficients(6,0,2)
        self.assertEqual(cs,[1,-1,923]);self.assertEqual(reg.valuation(cs[2]-cs[1],3),1)
    def test_zero_order_infinity(self):self.assertIsNone(reg.valuation(Q(0),3))
    def test_section_inverse_support(self):
        f=reg.reciprocal([int(i%2==0) for i in range(17)],5)
        self.assertEqual(f[::2],reg.reduced(5,2,8));self.assertEqual(f[1::2],[0]*8)
    def test_inverse_prime_shift(self):
        g=[1]+[2 if i%2 else 0 for i in range(1,30)];f=reg.reciprocal(g,3)
        for n in range(27):self.assertEqual(f[n+3],f[n+1])
    def test_missing_partial_target_rejected(self):
        inv=verify.source_inventory();real=Path.read_text
        def changed(path,*a,**k):
            text=real(path,*a,**k)
            if path==ROOT/'coverage.json':
                c=json.loads(text);next(e for e in c['entries'] if e['id']=='7.5')['partial_targets']=['KomorebiPaperIX.Missing'];return json.dumps(c)
            return text
        with patch.object(Path,'read_text',changed):
            with self.assertRaisesRegex(ValueError,'Missing partial'):verify.validate_coverage(inv)
    def test_false_completion_rejected(self):
        inv=verify.source_inventory();real=Path.read_text
        def changed(path,*a,**k):
            text=real(path,*a,**k)
            if path==ROOT/'coverage.json':
                c=json.loads(text);c['counts']['lean_checked']=24;return json.dumps(c)
            return text
        with patch.object(Path,'read_text',changed):
            with self.assertRaisesRegex(ValueError,'Stale coverage'):verify.validate_coverage(inv)

if __name__=='__main__':unittest.main(verbosity=2)
