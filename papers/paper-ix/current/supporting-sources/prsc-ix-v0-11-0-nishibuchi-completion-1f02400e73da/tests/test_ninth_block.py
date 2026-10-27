"""Source, specification and exact finite regression contracts. Author: Komorebi P."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json,sys,unittest,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
import ninth_regressions as reg

class NinthBlockTests(unittest.TestCase):
    def test_cumulative_inventory(self):
        x=json.loads((ROOT/'provenance/v0.9.0/inventory.json').read_text())
        self.assertEqual((len(x['modules']),x['theorem_count'],x['definition_count']),(57,630,128))
    def test_added_inventory(self):
        a=json.loads((ROOT/'provenance/v0.8.0/inventory.json').read_text());b=json.loads((ROOT/'provenance/v0.9.0/inventory.json').read_text())
        self.assertEqual((len(b['modules'])-len(a['modules']),b['theorem_count']-a['theorem_count'],b['definition_count']-a['definition_count']),(10,104,21))
    def test_upstream_47_bytes_unchanged(self):
        a=json.loads((ROOT/'provenance/v0.8.0/inventory.json').read_text())
        self.assertEqual(len(a['modules']),47)
        for m in a['modules']:self.assertEqual(verify.sha(ROOT/m['source']),m['sha256'])
    def test_four_recovered_research_modules_unchanged(self):
        with zipfile.ZipFile(ROOT/'provenance/Paper_IX_Singular_Residue_Attempt.zip') as z:
            for m in ('CyclotomicFiltration','PrimeBlockPolynomial','CyclicAmiceCoefficients','BinomialLogSeries'):
                b=z.read('Paper_IX_Singular_Residue_Attempt/formalization/'+m+'.lean')
                self.assertEqual(b,(ROOT/'formalization'/f'{m}.lean').read_bytes())
    def test_no_global_promotion(self):
        c=json.loads((ROOT/'provenance/v0.9.0/coverage.json').read_text())
        self.assertEqual(c['counts']['lean_checked'],23)
        e=next(e for e in c['entries'] if e['id']=='7.5')
        self.assertEqual(e['status'],'PENDING_LEAN');self.assertFalse(e['targets'])
        self.assertIn('weighted Mahler pairing',e['scope'])
        self.assertIn('KomorebiPaperIX.SingularRatioAmice.paper_singular_amice_estimate',e['partial_targets'])
    def test_literal_weighted_ring(self):
        s=(ROOT/'formalization/WeightedAmice.lean').read_text()
        self.assertIn('PadicInt.subring p',s);self.assertIn('n/p',s)
    def test_actual_ratio_bridge_is_registered(self):
        x=verify.source_inventory();names={d['name'] for m in x['modules'] for d in m['declarations']}
        for n in ('ratio_cleared','ratio_pullback_cleared','ratio_pullback_formula','singular_rational_coefficient_bound'):
            self.assertIn('KomorebiPaperIX.SingularRatioAmice.'+n,names)
    def test_reciprocal_zero_constant_rejected(self):
        with self.assertRaises(ValueError):reg.reciprocal([Q(0),Q(1)],4)
    def test_nonprime_rejected(self):
        with self.assertRaises(ValueError):reg.vp(Q(1),4)
    def test_bad_singular_domain_rejected(self):
        for p,m,a in [(3,2,0),(5,3,1),(5,2,2),(9,2,1)]:
            with self.assertRaises(ValueError):reg.singular_case(p,m,a,10)
    def test_bad_section_label_rejected(self):
        with self.assertRaises(ValueError):reg.section_pullback(3,3,10)
    def test_ratio_zero_address_rejected(self):
        with self.assertRaises(ValueError):reg.ratio_t(6,0,6)
    def test_zero_valuation_infinite(self):self.assertIsNone(reg.vp(Q(0),3))
    def test_r3_constant_and_first_term(self):
        r=reg.compose_log_stirling(reg.ratio_t(6,3,6),6)
        self.assertEqual(r[0],3);self.assertEqual(r[1:6],[0]*5)
        self.assertEqual(r[6],Q(1,10080));self.assertEqual(reg.vp(r[6],3),-2)
    def test_singular_formula(self):self.assertEqual(reg.singular_case(3,2,1,12)['coefficient_checks'],13)
    def test_stirling_substitution_matches_direct(self):
        f=[Q(2),Q(-3),Q(1,7),Q(5)]
        self.assertEqual(reg.compose_log_stirling(f,9),reg.compose_log_direct(f,9))
    def test_section_can_have_denominators(self):
        q=reg.section_pullback(3,0,3)[3]
        self.assertEqual(q,Q(1,6));self.assertEqual(reg.vp(q,3),-1)
    def test_invalid_modulus_bound_fails(self):
        q=reg.section_pullback(4,1,9)[9]
        self.assertLess(reg.vp(q,3),-3)
    def test_weighted_not_unweighted(self):
        self.assertTrue(reg.weighted([Q(1),Q(0),Q(0),Q(1,3)],3))
        self.assertFalse(reg.weighted([Q(1,3)],3))
    def test_reciprocal_and_derivative(self):
        f=[Q(1),Q(0),Q(0),Q(1,3),Q(1)]
        b=reg.reciprocal(f,12)
        self.assertTrue(reg.weighted(b,3));self.assertEqual(reg.mul(f,b,12),[1]+[0]*12)
        self.assertTrue(reg.weighted(reg.euler_log(f,12),3))

if __name__=='__main__':unittest.main()
