"""Bind the new regular stratum/consumer evidence to the one maintained reader."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/smith-chart/unified'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class SmithRegularBalancedTests(unittest.TestCase):
    def test_fresh_record_and_separate_review_bind_actual_source(self):
        folder=AREA/'verification/current-exact-010';m=json.loads((folder/'manifest.json').read_bytes())
        self.assertEqual((m['schema_version'],m['run']['status']),(2,'completed'))
        for row in m['input_artifacts']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'],row['path'])
            self.assertEqual(row['sha256'],row['sha256_after'])
        for row in m['outputs']:self.assertEqual(digest(ROOT/row['path']),row['sha256'])
        review=json.loads((AREA/'PHASE7_REVIEW.json').read_bytes())
        for p,h in review['source_sha256'].items():self.assertEqual(digest(AREA/p),h,p)
        self.assertEqual(review['overall_verdict'],'incomplete, with the smallest missing implication')
        self.assertEqual(review['current_scope']['newly_covered_whole_representatives'],0)
        self.assertFalse(review['current_scope']['independent_review'])

    def test_controls_reproduce_the_recorded_observation(self):
        old=json.loads((AREA/'verification/current-exact-010/stdout.txt').read_bytes())['checks'][1]['report']
        run=subprocess.run([sys.executable,'-B','-S',str(AREA/'solver/check_regular_balanced.py')],capture_output=True,text=True,check=True,timeout=180)
        self.assertEqual(json.loads(run.stdout),old)
        self.assertEqual((old['support_inventory']['unlabelled_port_fixed_types'],old['orthogonal_support_enumerator']['port_fixed_labeled_multisets']),(18,34))
        self.assertEqual(old['orthogonal_support_enumerator']['ordered_edge_sequences_visited'],11633)
        self.assertEqual((old['physical_R_clouds']['physical_graphs'],old['physical_R_clouds']['independent_phasor_comparisons']),(48,384))
        self.assertEqual(old['scope_guards']['disconnected_cycle_graphs'],9)
        self.assertEqual(old['near_core_region']['unified_strict_margin'],'1/300')
        self.assertEqual(old['near_core_region']['all_component_corner_graphs'],128)
        self.assertEqual(old['portable_consumer']['invalid_domain_or_resource_cases_rejected'],19)
        self.assertTrue(old['portable_consumer']['negative_floor_remains_inconclusive'])

    def test_current_status_figure_and_portable_entry_are_coherent(self):
        state=json.loads((AREA/'STATE.json').read_bytes())
        self.assertEqual(state['current_phase'],'global-transfer-and-joint-minima-001')
        self.assertEqual(state['mixed_representatives']['remaining'],796)
        self.assertEqual(state['formal_scope']['theorems'],41)
        self.assertFalse(state['new_lean_claim']);self.assertFalse(state['new_hardware_claim'])
        self.assertIn('011',state['current_evidence']['portable_exact_suite'])
        self.assertIn('check_current_transfer.py',(AREA/'replay_current.py').read_text())
        self.assertIn('check_current_resonance.py',(AREA/'solver/check_current_regular.py').read_text())
        self.assertIn('REGULAR_BALANCED.md',(ROOT/'tools/smith_chart_unified.py').read_text())
        self.assertIn('disconnected',(AREA/'CONTINUATION.md').read_text().lower())
        spec=importlib.util.spec_from_file_location('regular_core_figure',AREA/'figures/generate_regular_balanced.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        example=json.loads((AREA/'solver/regular_core_example.json').read_bytes())
        self.assertEqual(module.FIGURE_GRAPHS['cyclic'],example['nominal'])
        for mobile in (False,True):
            p=AREA/('figures/regular-balanced'+('.mobile' if mobile else '')+'.svg')
            self.assertEqual(p.read_text(encoding='utf-8'),module.build(mobile))
            self.assertIn('1/300',module.build(mobile));self.assertIn('796',module.build(mobile))

if __name__=='__main__':unittest.main()
