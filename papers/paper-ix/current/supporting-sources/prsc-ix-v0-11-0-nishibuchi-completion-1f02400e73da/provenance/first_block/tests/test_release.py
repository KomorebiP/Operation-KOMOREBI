"""Regression tests for source census, trust checks, process cleanup and arithmetic helpers."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
import check_low_memory
import regressions

class ReleaseTests(unittest.TestCase):
    def test_inventory_matches_sources(self):
        self.assertEqual(verify.source_inventory(),json.loads((ROOT/'inventory.json').read_text()))
    def test_inventory_counts(self):
        x=verify.source_inventory();self.assertEqual((len(x['modules']),x['theorem_count'],x['definition_count']),(8,89,22))
    def test_nested_comments_are_removed(self):
        text='a /- sorry /- axiom -/ admit -/ b'
        stripped=verify.stripped_source(text)
        self.assertEqual(stripped.split(),['a','b'])
        self.assertEqual(len(stripped),len(text))
    def test_strings_and_line_comments_are_removed(self):
        x=verify.stripped_source('"sorry" -- axiom\ntheorem valid : True := by trivial')
        self.assertIsNone(verify.FORBIDDEN.search(x));self.assertIn('theorem valid',x)
    def test_unterminated_comments_fail(self):
        with self.assertRaises(ValueError): verify.stripped_source('/- never closed')
    def test_active_holes_detected(self):
        self.assertIsNotNone(verify.FORBIDDEN.search(verify.stripped_source('theorem bad : False := by sorry')))
    def test_trust_bypass_detected(self):
        self.assertIsNotNone(verify.FORBIDDEN.search('set_option debug.skipKernelTC true'))
    def test_valid_audit_with_wrapping(self):
        x=verify.parse_audits("'X' depends on axioms: [propext,\n Classical.choice]\n'Y' does not depend on any axioms",{'X','Y'})
        self.assertEqual(x['Y'],[])
    def test_admitted_axiom_rejected(self):
        with self.assertRaises(ValueError): verify.parse_audits("'X' depends on axioms: [sorryAx]",{'X'})
    def test_missing_audit_rejected(self):
        with self.assertRaises(ValueError): verify.parse_audits('',{'X'})
    def test_duplicate_audit_rejected(self):
        with self.assertRaises(ValueError): verify.parse_audits("'X' depends on axioms: []\n'X' depends on axioms: []",{'X'})
    def test_import_failure_not_valid_negative(self):
        self.assertFalse(verify.control_passed(1,"error: unknown module prefix 'Missing'",'false_equality'))
    def test_timeout_not_valid_negative(self):
        self.assertFalse(verify.control_passed(124,'error: unsolved goals','false_equality'))
    def test_success_not_valid_negative(self):
        self.assertFalse(verify.control_passed(0,'error: unsolved goals','false_equality'))
    def test_process_timeout_raises(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            check_low_memory.run_with_timeout([sys.executable,'-c','import time;time.sleep(10)'],timeout=.1,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    def test_normalization_witness(self):
        a=regressions.euler(6,3,2);self.assertEqual(a[2]-a[1],regressions.Q(64,455))
    def test_coverage_counts(self):
        x=json.loads((ROOT/'coverage.json').read_text())
        self.assertEqual(sum(e['status']=='LEAN_CHECKED' for e in x['entries']),7)
        self.assertEqual(sum(e['status']=='PENDING_LEAN' for e in x['entries']),17)
        self.assertEqual(sum(e['status']=='CLASSICAL_INPUT' for e in x['entries']),3)
        self.assertEqual(sum(e['status']=='CONJECTURAL' for e in x['entries']),2)
    def test_coverage_targets_resolve(self):
        x=verify.source_inventory()
        names={d['name'] for m in x['modules'] for d in m['declarations']}
        for e in json.loads((ROOT/'coverage.json').read_text())['entries']:
            if e['status']=='LEAN_CHECKED': self.assertTrue(e['targets'])
            else: self.assertFalse(e['targets'])
            self.assertTrue(set(e['targets'])<=names)
    def test_baseline_pdf_hash(self):
        x=json.loads((ROOT/'coverage.json').read_text())
        self.assertEqual(verify.sha(ROOT/x['source_pdf']),x['source_sha256'])
    def test_zero_diagonal_rejected(self):
        with self.assertRaises(ValueError): regressions.triangular([[0]],[1])
    def test_finite_valuation_zero_rejected(self):
        with self.assertRaises(ValueError): regressions.vp(regressions.Q(0),3)

if __name__=='__main__': unittest.main(verbosity=2)
