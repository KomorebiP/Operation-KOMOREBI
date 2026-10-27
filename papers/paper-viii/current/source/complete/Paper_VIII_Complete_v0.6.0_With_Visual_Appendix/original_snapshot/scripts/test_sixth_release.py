#!/usr/bin/env python3
"""Sixth-block source, audit, scope and mirror contracts. Author: Komorebi P."""
from pathlib import Path
import hashlib
import json
import re
import unittest
import numpy as np
import verify
import run_sixth_regressions as mirror
ROOT=Path(__file__).resolve().parents[1]
NS='KomorebiPaperVIII.SmallCore.'

class SixthReleaseTests(unittest.TestCase):
    def setUp(self):
        self.meta=json.loads((ROOT/'verification/sixth_module_inventory.json').read_text())
        self.inv=json.loads((ROOT/'verification/theorem_inventory.json').read_text())
        self.ledger=json.loads((ROOT/'verification/coverage_ledger.json').read_text())
    def test_exact_increment(self):
        self.assertEqual(self.meta['new_theorem_count'],79)
        self.assertEqual(len(self.meta['modules']),10)
        self.assertEqual(len(verify.MODULES),40)
        for m,c in self.meta['theorem_counts'].items():
            text=verify.without_comments((ROOT/'formalization'/f'{m}.lean').read_text())
            self.assertEqual(len(re.findall(r'\btheorem\s+\w+',text)),c)
    def test_upstream_inventory_unchanged(self):
        old=json.loads((ROOT/'verification/provenance/fifth_theorem_inventory.json').read_text())
        self.assertEqual(len(old),30)
        for m,v in old.items():self.assertEqual(v,self.inv[m])
    def test_theorem_coverage_completed(self):
        proved=[r for r in self.ledger['records'] if r['proof']=='complete']
        self.assertEqual(len(proved),56)
        self.assertTrue(all(r['lean_status']=='checked' for r in proved))
        self.assertEqual(self.ledger['fully_checked'],56)
        self.assertEqual(self.ledger['not_fully_checked'],0)
    def test_classical_boundary_not_erased(self):
        self.assertEqual(sum(r['proof']=='external' for r in self.ledger['records']),4)
        row=next(r for r in self.ledger['records'] if r['number']=='5.5')
        self.assertEqual(row['lean_status'],'external_input_with_checked_svd_data_specialization')
    def test_primary_target_audited(self):
        self.assertIn(NS+'small_core_optimal_recompression',self.inv['SmallCoreRecompression'])
        row=next(r for r in self.ledger['records'] if r['number']=='5.6')
        self.assertIn(NS+'small_core_optimal_recompression',row['lean_theorems'])
        self.assertIn('SVD existence/computation',row['formal_scope'])
    def test_svd_structure_has_no_optimality_field(self):
        text=verify.without_comments((ROOT/'formalization/SmallCoreRecompression.lean').read_text())
        body=text.split('structure OrderedThinSVD',1)[1].split('omit',1)[0]
        fields=re.findall(r'^  (\w+)\s*:',body,re.M)
        self.assertEqual(fields,['left','right','values','left_isometry','right_isometry',
                                 'nonnegative','sorted','reconstruction'])
        self.assertNotIn('BestRank',body)
    def test_lower_bounds_are_separate_targets(self):
        self.assertIn(NS+'diagonal_spectral_lower',self.inv['SpectralOptimality'])
        self.assertIn(NS+'diagonal_frobenius_lower',self.inv['FrobeniusOptimality'])
        self.assertIn(NS+'prefix_kernel_witness',self.inv['SpectralOptimality'])
        self.assertIn(NS+'kernel_rank_nullity',self.inv['KernelFrame'])
    def test_no_proof_bypass(self):
        for m in self.meta['modules']:
            text=verify.without_comments((ROOT/'formalization'/f'{m}.lean').read_text())
            self.assertIsNone(re.search(r'\b(sorry|admit|axiom|unsafe|native_decide|opaque|implemented_by)\b',text))
            self.assertNotIn('skipKernelTC',text)
    def test_all_new_constructions_audited(self):
        self.assertEqual(self.meta['new_construction_count'],30)
        for m,names in self.meta['constructions'].items():
            self.assertEqual(set(names),verify.CONSTRUCTIONS[m])
            self.assertLessEqual(set(names),set(self.inv[m]))
    def test_valid_diagonal_svd(self):
        mirror.validate_svd(np.diag([3.,1.]),np.eye(2),np.eye(2),np.array([3.,1.]))
    def test_empty_shapes(self):
        c=mirror.recompress(np.empty((0,3)),np.zeros((4,3)),2)
        self.assertEqual(c['b'].shape,(0,4))
        self.assertEqual(c['lk'].shape,(0,0))
    def test_zero_and_full_retention(self):
        l=np.diag([3.,1.]);r=np.eye(2)
        self.assertTrue(np.allclose(mirror.recompress(l,r,0)['b'],0))
        self.assertTrue(np.allclose(mirror.recompress(l,r,5)['b'],l))
    def test_invalid_assumptions_rejected(self):
        with self.assertRaises(ValueError):
            mirror.validate_svd(np.eye(2),2*np.eye(2),np.eye(2),np.ones(2))
        with self.assertRaises(ValueError):
            mirror.validate_svd(np.diag([1.,3.]),np.eye(2),np.eye(2),np.array([1.,3.]))
    def test_bad_inputs_rejected(self):
        for k in [-1,True,1.5]:
            with self.assertRaises(ValueError):mirror.recompress(np.eye(2),np.eye(2),k)
        with self.assertRaises(ValueError):mirror.matrix(np.array([[np.nan]]))

if __name__=='__main__':unittest.main(verbosity=2)
