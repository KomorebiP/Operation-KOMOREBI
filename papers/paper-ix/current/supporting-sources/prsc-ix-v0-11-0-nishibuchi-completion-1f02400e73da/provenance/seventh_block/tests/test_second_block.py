"""Second-block scope, preservation and exact arithmetic checks."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify
import second_regressions as reg

class SecondBlockTests(unittest.TestCase):
    def test_coverage_gate_passes(self):
        counts=verify.validate_coverage(verify.source_inventory())
        self.assertEqual((counts['lean_checked'],counts['pending_lean']),(23,1))
    def test_only_three_more_manuscript_items(self):
        first=json.loads((ROOT/'provenance/first_block/coverage.json').read_text())
        now=json.loads((ROOT/'provenance/second_block/coverage.json').read_text())
        old={e['id'] for e in first['entries'] if e['status']=='LEAN_CHECKED'}
        new={e['id'] for e in now['entries'] if e['status']=='LEAN_CHECKED'}
        self.assertEqual(new-old,{'4.1','4.2','4.3'})
    def test_upstream_sources_unchanged(self):
        pairs=json.loads((ROOT/'provenance/upstream_sources.json').read_text())
        self.assertEqual(len(pairs),31)
        for path,digest in pairs.items(): self.assertEqual(verify.sha(ROOT/path),digest)
    def test_stale_counts_fail(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);c=json.loads((ROOT/'coverage.json').read_text());c['counts']['lean_checked']=7
            (p/'coverage.json').write_text(json.dumps(c))
            with patch.object(verify,'ROOT',p), self.assertRaisesRegex(ValueError,'Stale coverage'):
                verify.validate_coverage(json.loads((ROOT/'inventory.json').read_text()))
    def test_unresolved_target_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);c=json.loads((ROOT/'coverage.json').read_text());c['entries'][0]['targets']=['Missing.theorem']
            (p/'coverage.json').write_text(json.dumps(c))
            with patch.object(verify,'ROOT',p), self.assertRaisesRegex(ValueError,'Missing coverage'):
                verify.validate_coverage(json.loads((ROOT/'inventory.json').read_text()))
    def test_integral_euler_anchors(self):
        self.assertEqual(reg.euler_numbers(8),[1,0,-1,0,5,0,-61,0,1385])
    def test_composite_odd_length(self):
        e=reg.euler_numbers(12);b=reg.signed_inverse(e)
        self.assertEqual(reg.truncated(9,6,6,b),e[12])
    def test_even_length_rejected(self):
        with self.assertRaises(ValueError): reg.truncated(2,0,0,[1])
    def test_full_depth_endpoint(self):
        e=reg.euler_numbers(8);b=reg.signed_inverse(e)
        self.assertEqual(reg.truncated(5,4,100,b),1385)
    def test_sharp_precision(self):
        e=reg.euler_numbers(8);b=reg.signed_inverse(e)
        error=1385-reg.truncated(5,4,2,b)
        self.assertEqual(error,-2731000000)
        self.assertEqual(error%5**6,0);self.assertNotEqual(error%5**7,0)
    def test_zero_reciprocal_rejected(self):
        with self.assertRaises(ValueError): reg.reciprocal([reg.Q(0)])
    def test_new_audit_count(self):
        old=json.loads((ROOT/'provenance/first_block/inventory.json').read_text());new=json.loads((ROOT/'provenance/second_block/inventory.json').read_text())
        self.assertEqual(new['theorem_count']-old['theorem_count'],74)
        self.assertEqual(new['definition_count']-old['definition_count'],15)

if __name__=='__main__': unittest.main(verbosity=2)
