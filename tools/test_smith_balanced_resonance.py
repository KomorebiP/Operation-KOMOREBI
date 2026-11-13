"""Keep balanced-mode claims, fresh evidence and coherent reader delivery bound."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/smith-chart/unified'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class SmithBalancedResonanceTests(unittest.TestCase):
    def test_exact_record_and_proof_review_bind_the_maintained_sources(self):
        d=AREA/'verification/current-exact-009';m=json.loads((d/'manifest.json').read_bytes())
        self.assertEqual((m['schema_version'],m['run']['status']),(2,'completed'))
        for row in m['input_artifacts']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'],row['path'])
            self.assertEqual(row['sha256'],row['sha256_after'])
        for row in m['outputs']:self.assertEqual(digest(ROOT/row['path']),row['sha256'])
        review=json.loads((AREA/'PHASE6_REVIEW.json').read_bytes())
        for name,h in review['source_sha256'].items():self.assertEqual(digest(AREA/name),h,name)
        self.assertEqual(review['overall_verdict'],'incomplete, with the smallest missing implication')
        self.assertEqual(review['current_scope']['newly_covered_whole_representatives'],0)

    def test_new_physical_controls_reproduce_the_fresh_observation(self):
        old=json.loads((AREA/'verification/current-exact-009/stdout.txt').read_bytes())['checks'][1]['report']
        run=subprocess.run([sys.executable,'-B','-S',str(AREA/'solver/check_balanced_resonance.py')],capture_output=True,text=True,check=True,timeout=150)
        self.assertEqual(json.loads(run.stdout),old)
        self.assertEqual((old['support_inventory']['unlabelled_colored_types'],old['support_inventory']['labeled_controls']),(8,37))
        self.assertEqual((old['mode_face']['physical_mode_graphs'],old['mode_face']['basis_modes_checked']),(88,96))
        self.assertEqual(old['mode_face']['independent_positive_real_phasor_comparisons'],616)
        self.assertEqual(old['near_mode_comparison']['near_mode_strict_margin'],'3/40')
        self.assertEqual(old['near_mode_comparison']['relative_response_bound'],'1/198')
        self.assertEqual(old['portable_consumer'],{'example_produced':1,'example_consumed':1,'corrupted_output_rejected':1})

    def test_status_and_portable_entry_keep_the_open_global_obligation(self):
        state=json.loads((AREA/'STATE.json').read_bytes())
        self.assertEqual(state['current_phase'],'global-transfer-and-joint-minima-001')
        self.assertEqual(state['mixed_representatives']['remaining'],796)
        self.assertEqual(state['formal_scope']['theorems'],41)
        self.assertTrue(state['new_analytic_robustness_claim'])
        self.assertFalse(state['new_lean_claim']);self.assertFalse(state['new_hardware_claim'])
        self.assertIn('011',state['current_evidence']['portable_exact_suite'])
        self.assertIn('solver/check_current_transfer.py',(AREA/'replay_current.py').read_text())
        wrapper=(AREA/'solver/check_current_resonance.py').read_text()
        self.assertIn('check_current_global.py',wrapper)
        self.assertIn('check_balanced_resonance.py',wrapper)
        self.assertIn('uniform',(AREA/'CONTINUATION.md').read_text())

    def test_vector_geometry_sources_and_current_chapter_are_retained(self):
        spec=importlib.util.spec_from_file_location('balanced_mode_figure',AREA/'figures/generate_balanced_resonance.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for mobile in (False,True):
            path=AREA/('figures/balanced-resonance'+('.mobile' if mobile else '')+'.svg')
            self.assertEqual(path.read_text(encoding='utf-8'),module.build(mobile))
            self.assertIn('796',module.build(mobile));self.assertIn('Positive-real',module.build(mobile))
        source=(ROOT/'tools/smith_chart_unified.py').read_text()
        self.assertIn('BALANCED_RESONANCE.md',source)
        self.assertIn('GLOBAL_TYPED_MARGINS.md',source)
        self.assertIn('Earlier margin checkpoints and derivations',source)

if __name__=='__main__':unittest.main()
