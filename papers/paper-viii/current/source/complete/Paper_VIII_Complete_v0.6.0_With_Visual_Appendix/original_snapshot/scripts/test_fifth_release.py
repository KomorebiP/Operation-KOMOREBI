#!/usr/bin/env python3
"""Fifth-block compatibility contracts updated for the sixth release.
Original fixed-count version is preserved in verification/provenance. Author: Komorebi P.
"""
from pathlib import Path
from fractions import Fraction as F
import json
import re
import unittest
import verify
import run_fifth_regressions as mirror

ROOT=Path(__file__).resolve().parents[1]
NEW=('GraphSchedules','TriangularSolve','InverseSupport','SchurSupport',
     'BandedCount','DiscoveryCertificate','BlockJacobi')

class FifthReleaseTests(unittest.TestCase):
    def setUp(self):
        self.inventory=json.loads((ROOT/'verification/theorem_inventory.json').read_text())
        self.ledger=json.loads((ROOT/'verification/coverage_ledger.json').read_text())

    def test_inventory_names_unique(self):
        flat=[s for names in self.inventory.values() for s in names]
        self.assertEqual(len(flat),len(set(flat)))
        self.assertEqual(set(self.inventory),set(verify.MODULES))

    def test_counts_derive_from_sources(self):
        counts={}
        for m in verify.MODULES:
            s=verify.without_comments((ROOT/'formalization'/f'{m}.lean').read_text())
            counts[m]=len(re.findall(r'\btheorem\s+(\w+)',s))
        self.assertEqual(sum(counts.values()),392)
        self.assertEqual(sum(counts[m] for m in NEW),66)
        self.assertEqual(counts['QuantumPacketCore'],19)

    def test_exact_audit_coverage(self):
        for m in verify.MODULES:
            s=verify.without_comments((ROOT/'formalization'/f'{m}.lean').read_text())
            audits=re.findall(r'^#print axioms ([\w.]+)',s,re.M)
            self.assertEqual(len(audits),len(set(audits)))
            self.assertEqual(set(audits),set(self.inventory[m]))
            theorem_names=set(re.findall(r'\btheorem\s+(\w+)',s))
            self.assertEqual(theorem_names,{x.rsplit('.',1)[-1]
              for x in set(audits)-verify.CONSTRUCTIONS.get(m,set())})

    def test_construction_census(self):
        self.assertEqual(sum(map(len,verify.CONSTRUCTIONS.values())),66)
        for m,names in verify.CONSTRUCTIONS.items():
            self.assertLessEqual(names,set(self.inventory[m]))

    def test_local_import_order(self):
        built=set()
        for m in verify.MODULES:
            self.assertLessEqual(set(verify.dependency_sources(ROOT,m)),built)
            built.add(m)

    def test_coverage_ledger_counts(self):
        items=[r for r in self.ledger['records'] if r['proof']=='complete']
        self.assertEqual(len(items),56)
        self.assertEqual(sum(r['lean_status']=='checked' for r in items),56)
        self.assertEqual([r['number'] for r in items if r['lean_status']!='checked'],[])
        self.assertEqual(sum(r['proof']=='external' for r in self.ledger['records']),4)

    def test_coverage_targets_resolve(self):
        all_names={x for names in self.inventory.values() for x in names}
        for r in self.ledger['records']:
            if r['lean_status']=='checked':
                self.assertTrue(r.get('lean_theorems'),r['number'])
                self.assertLessEqual(set(r['lean_theorems']),all_names)

    def test_current_increment_not_stale(self):
        self.assertEqual(set(self.ledger['newly_checked_items']),
                         {'5.6'})
        self.assertEqual(self.ledger['new_theorem_declarations'],79)
        cg=next(r for r in self.ledger['records'] if r['number']=='7.5')
        self.assertEqual(cg['lean_status'],'external_input_not_independently_formalized')

    def test_mirror_empty_and_diamond(self):
        self.assertEqual(mirror.levels(0,set()),[])
        self.assertEqual(mirror.levels(4,{(0,1),(0,2),(1,3),(2,3)}),[1,2,2,3])

    def test_mirror_cycle_rejected(self):
        for n,edges in [(1,{(0,0)}),(2,{(0,1),(1,0)})]:
            with self.assertRaises(ValueError):mirror.levels(n,edges)

    def test_mirror_singular_inverse_rejected(self):
        with self.assertRaises(ValueError):mirror.inverse([[F(0)]])
        with self.assertRaises(ValueError):mirror.inverse([[F(1),F(2)]])

    def test_mirror_reflexive_reach_and_cancellation(self):
        self.assertEqual(mirror.closure(1,set()),[[True]])
        a=[[F(1),F(1),F(1)],[F(0),F(1),F(1)],[F(0),F(0),F(1)]]
        self.assertEqual(mirror.inverse(a)[0][2],0)
        self.assertTrue(mirror.closure(3,{(2,1),(1,0)})[2][0])

if __name__=='__main__':
    unittest.main(verbosity=2)
