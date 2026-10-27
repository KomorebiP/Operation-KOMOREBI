"""Sixth-block specification and independent finite-regression tests. Author: Komorebi P."""
from fractions import Fraction as Q
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
import sixth_regressions as reg

class SixthBlockTests(unittest.TestCase):
    def test_exact_two_new_items(self):
        old=json.loads((ROOT/'provenance/fifth_block/coverage.json').read_text())
        new=json.loads((ROOT/'provenance/sixth_block/coverage.json').read_text())
        a={e['id'] for e in old['entries'] if e['status']=='LEAN_CHECKED'}
        b={e['id'] for e in new['entries'] if e['status']=='LEAN_CHECKED'}
        self.assertEqual(b-a,{'9.1','9.2'});self.assertLessEqual(a,b)
    def test_cumulative_census(self):
        x=json.loads((ROOT/'provenance/sixth_block/inventory.json').read_text())
        self.assertEqual((len(x['modules']),x['theorem_count'],x['definition_count']),(31,382,84))
    def test_new_census(self):
        a=json.loads((ROOT/'provenance/fifth_block/inventory.json').read_text());b=json.loads((ROOT/'provenance/sixth_block/inventory.json').read_text())
        self.assertEqual((len(b['modules'])-len(a['modules']),b['theorem_count']-a['theorem_count'],
                         b['definition_count']-a['definition_count']),(3,49,7))
    def test_upstream_28_sources_preserved(self):
        x=json.loads((ROOT/'provenance/fifth_block/inventory.json').read_text())
        self.assertEqual(len(x['modules']),28)
        for m in x['modules']:self.assertEqual(verify.sha(ROOT/m['source']),m['sha256'])
    def test_final_pair_not_promoted(self):
        x=json.loads((ROOT/'provenance/sixth_block/coverage.json').read_text())
        self.assertEqual({e['id'] for e in x['entries'] if e['status']=='PENDING_LEAN'},{'7.5','8.5'})
        self.assertEqual({e['id'] for e in x['entries'] if e['status']=='CONJECTURAL'},{'13.2','13.3'})
    def test_actual_matrix_and_charpoly(self):
        text=(ROOT/'formalization/CompanionPackets.lean').read_text()
        for token in ['(C ^ n) *ᵥ v','D.aeval_self_charpoly','packet_charpoly_recurrence','source_companion_jump']:
            self.assertIn(token,text)
    def test_actual_fibonacci_and_lucas(self):
        text=(ROOT/'formalization/FibonacciPackets.lean').read_text()
        for token in ['Nat.fib','| 0 => 2','| 1 => 1','trace_power_is_lucas','Matrix.det_pow']:
            self.assertIn(token,text)
    def test_new_negative_controls_present(self):
        text=(ROOT/'scripts/verify.py').read_text()
        for tag in ['false_fibonacci_sign','false_unjumped_matrix','false_jump_trace']:self.assertIn(tag,text)
    def test_empty_charpoly(self):self.assertEqual(reg.characteristic([]),[1])
    def test_nilpotent_charpoly(self):self.assertEqual(reg.characteristic([[0,1],[0,0]]),[0,0,1])
    def test_fibonacci_charpoly(self):self.assertEqual(reg.characteristic([[1,1],[1,0]]),[-1,-1,1])
    def test_jump_charpoly(self):self.assertEqual(reg.characteristic(reg.power([[1,1],[1,0]],3)),[-1,-4,1])
    def test_identity_not_minimal_order_two(self):
        self.assertEqual(reg.characteristic(reg.identity(2)),[1,-2,1])
        self.assertEqual(reg.apply(reg.identity(2),[1,0]),[1,0])
    def test_exact_example(self):self.assertEqual(reg.sampled_fib(3,2,5),[1,5,21,89,377,1597])
    def test_even_step_sign(self):
        self.assertEqual(reg.fib(5),3*reg.fib(3)-reg.fib(1))
        self.assertNotEqual(reg.fib(5),3*reg.fib(3)+reg.fib(1))
    def test_step_zero(self):self.assertEqual(reg.sampled_fib(0,7,5),[13]*6)
    def test_step_one(self):self.assertEqual(reg.sampled_fib(1,0,7),[0,1,1,2,3,5,8,13])
    def test_zero_initial_sample(self):self.assertEqual(reg.sampled_fib(3,0,3),[0,2,8,34])
    def test_noncanonical_offset_allowed(self):self.assertEqual(reg.sampled_fib(2,9,3),[34,89,233,610])
    def test_negative_step_rejected(self):
        with self.assertRaises(ValueError):reg.sampled_fib(-1,0,2)
    def test_negative_index_rejected(self):
        with self.assertRaises(ValueError):reg.fib(-1)
    def test_wrong_dimension_rejected(self):
        with self.assertRaises(ValueError):reg.apply([[1,2],[3,4]],[1])
    def test_inexact_matrix_rejected(self):
        with self.assertRaises(ValueError):reg.characteristic([[0.5]])
    def test_bool_index_rejected(self):
        with self.assertRaises(ValueError):reg.lucas(True)
    def test_singular_rational_case(self):
        x=reg.check_case([[Q(0),Q(1,3)],[Q(0),Q(0)]],[Q(0),Q(2,5)],2,0,None)
        self.assertEqual(x['recurrence_cases'],6)
    def test_composite_ring_case(self):
        x=reg.check_case([[2,1],[0,3]],[2,1],3,4,6)
        self.assertEqual(x['matrix_identity_cases'],1)
    def test_stale_coverage_is_rejected(self):
        from unittest.mock import patch
        inv=verify.source_inventory()
        real=Path.read_text
        def changed(path,*a,**k):
            text=real(path,*a,**k)
            if path==ROOT/'coverage.json':
                x=json.loads(text);x['counts']['lean_checked']=24;return json.dumps(x)
            return text
        with patch.object(Path,'read_text',changed):
            with self.assertRaisesRegex(ValueError,'Stale coverage'):verify.validate_coverage(inv)
    def test_missing_principal_target_rejected(self):
        from unittest.mock import patch
        inv=verify.source_inventory();real=Path.read_text
        def changed(path,*a,**k):
            text=real(path,*a,**k)
            if path==ROOT/'coverage.json':
                x=json.loads(text)
                next(e for e in x['entries'] if e['id']=='9.1')['targets']=['KomorebiPaperIX.NotPresent']
                return json.dumps(x)
            return text
        with patch.object(Path,'read_text',changed):
            with self.assertRaisesRegex(ValueError,'Missing coverage target'):verify.validate_coverage(inv)

if __name__=='__main__':unittest.main(verbosity=2)
