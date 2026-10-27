"""Fifth-block finite arithmetic, scope and source-integrity tests. Author: Komorebi P."""
from fractions import Fraction as Q
from pathlib import Path
import json, sys, unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
import fifth_regressions as reg

class FifthBlockTests(unittest.TestCase):
    def test_three_new_items(self):
        a=json.loads((ROOT/'provenance/fourth_block/coverage.json').read_text())
        b=json.loads((ROOT/'coverage.json').read_text())
        old={e['id'] for e in a['entries'] if e['status']=='LEAN_CHECKED'}
        new={e['id'] for e in b['entries'] if e['status']=='LEAN_CHECKED'}
        self.assertEqual(new-old,{'6.2','8.3','10.1'})
        self.assertLessEqual(old,new)
    def test_cumulative_counts(self):
        x=verify.source_inventory()
        self.assertEqual((len(x['modules']),x['theorem_count'],x['definition_count']),(28,333,77))
    def test_new_census(self):
        a=json.loads((ROOT/'provenance/fourth_block/inventory.json').read_text())
        b=verify.source_inventory()
        self.assertEqual((len(b['modules'])-len(a['modules']),b['theorem_count']-a['theorem_count'],
                          b['definition_count']-a['definition_count']),(7,61,17))
    def test_all_21_upstream_proofs_preserved(self):
        a=json.loads((ROOT/'provenance/fourth_block/inventory.json').read_text())
        self.assertEqual(len(a['modules']),21)
        for m in a['modules']: self.assertEqual(verify.sha(ROOT/m['source']),m['sha256'])
    def test_four_remaining_items(self):
        a=json.loads((ROOT/'coverage.json').read_text())
        self.assertEqual({e['id'] for e in a['entries'] if e['status']=='PENDING_LEAN'},
                         {'7.5','8.5','9.1','9.2'})
    def test_conjectures_not_promoted(self):
        a=json.loads((ROOT/'coverage.json').read_text())
        self.assertEqual({e['id'] for e in a['entries'] if e['status']=='CONJECTURAL'},
                         {'13.2','13.3'})
    def test_rational_bridge_present(self):
        a=(ROOT/'formalization/WindowIndependence.lean').read_text()
        self.assertIn('theorem coeffPadic_coe',a)
        self.assertIn('theorem standard_window_integral',a)
        self.assertIn('Congruential.coeff (m*p) j n',a)
    def test_root_not_assumed(self):
        a=(ROOT/'formalization/FiniteUnits.lean').read_text()
        self.assertIn('a^(p^L)',a)
        self.assertIn('ZMod.pow_totient a',a)
        self.assertIn('theorem root_unique',a)
    def test_zero_precision_rejected(self):
        with self.assertRaises(ValueError): reg.prime_decomposition(3,0,1)
    def test_nonprime_rejected(self):
        for p in [0,1,4,9]:
            with self.assertRaises(ValueError): reg.prime_decomposition(p,2,1)
    def test_nonunit_rejected(self):
        for a in [0,3,9]:
            with self.assertRaises(ValueError): reg.prime_decomposition(3,2,a)
    def test_actual_lift_mod_nine(self):
        self.assertEqual(reg.prime_decomposition(3,2,2),(8,7))
        self.assertNotEqual(pow(2,2,9),1)
    def test_base_precision_principal_one(self):
        for a in range(1,7): self.assertEqual(reg.prime_decomposition(7,1,a),(a,1))
    def test_p_two_root_split(self):
        self.assertEqual(reg.prime_decomposition(2,3,3),(1,3))
    def test_loss_of_precision(self):
        w,v=reg.prime_decomposition(5,4,7)
        for k in range(1,5): self.assertEqual((w%5**k,v%5**k),reg.prime_decomposition(5,k,7))
    def test_multiplicativity(self):
        wa,va=reg.prime_decomposition(7,3,9);wb,vb=reg.prime_decomposition(7,3,11)
        self.assertEqual(reg.prime_decomposition(7,3,99),(wa*wb%343,va*vb%343))
    def test_dyadic_sign(self): self.assertEqual(reg.dyadic_decomposition(3,3),(7,5))
    def test_dyadic_sign_minimal_precision(self):
        self.assertEqual(reg.dyadic_decomposition(2,3),(3,1))
        with self.assertRaises(ValueError): reg.dyadic_decomposition(1,1)
    def test_even_dyadic_input_rejected(self):
        with self.assertRaises(ValueError): reg.dyadic_decomposition(5,2)
    def test_standard_window_all_addresses(self):
        expected=reg.reduced_inverse(5,2,7)
        for j in range(5):
            self.assertEqual([reg.reduce_rational(x,5) for x in reg.window_coefficients(5,2,j,7)],expected)
    def test_actual_rational_coefficients(self):
        self.assertEqual(reg.packet_coefficients(6,3,2),[Q(1),Q(-1,84),Q(703,5460)])
    def test_outside_window_no_fake_reduction(self):
        with self.assertRaises(ValueError): reg.reduce_rational(Q(-1,84),3)
        with self.assertRaises(ValueError): reg.window_coefficients(3,2,3,1)
    def test_zero_row(self):
        for j in range(5): self.assertEqual(reg.window_coefficients(5,2,j,0),[1])
    def test_crt_endpoints(self):
        self.assertEqual(reg.crt_address(0,1,0),(0,0))
        self.assertEqual(reg.crt_reconstruct(0,1,0,0),0)
        self.assertEqual(reg.crt_reconstruct(0,7,0,6),6)
        self.assertEqual(reg.crt_reconstruct(3,1,7,0),7)
    def test_crt_reconstructs(self):
        for r in range(60):
            addr=reg.crt_address(2,15,r); self.assertEqual(reg.crt_reconstruct(2,15,*addr),r)
    def test_noncoprime_rejected(self):
        with self.assertRaises(ValueError): reg.crt_address(2,6,0)
        self.assertEqual((0%2,0%2),(2%2,2%2));self.assertNotEqual(0%4,2%4)
    def test_noncanoical_labels_rejected(self):
        with self.assertRaises(ValueError): reg.crt_address(2,3,12)
        with self.assertRaises(ValueError): reg.crt_reconstruct(2,3,4,0)
    def test_wrong_type_rejected(self):
        with self.assertRaises(ValueError): reg.prime_decomposition(True,2,1)
    def test_17_control_sources_in_verifier(self):
        text=(ROOT/'scripts/verify.py').read_text()
        for name in ['false_unlifted_root','false_composite_fermat','false_dyadic_sign_collapse',
                     'false_outside_window_integrality','false_noncoprime_CRT']:
            self.assertIn(name,text)

if __name__=='__main__': unittest.main(verbosity=2)
