"""Bind written scope, exact evidence, retained history and current delivery."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,unittest

ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/smith-chart/unified'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class SmithPhysicalConstraintTests(unittest.TestCase):
    def test_both_fresh_records_and_review_bind_actual_sources(self):
        for number in ('007','008'):
            d=AREA/('verification/current-exact-'+number);m=json.loads((d/'manifest.json').read_bytes())
            self.assertEqual((m['schema_version'],m['run']['status']),(2,'completed'))
            for row in m['input_artifacts']:
                self.assertEqual(digest(ROOT/row['path']),row['sha256'],row['path'])
                self.assertEqual(row['sha256'],row['sha256_after'])
            for row in m['outputs']:self.assertEqual(digest(ROOT/row['path']),row['sha256'])
        review=json.loads((AREA/'PHASE5_REVIEW.json').read_bytes())
        for name,h in review['source_sha256'].items():self.assertEqual(digest(AREA/name),h,name)
        self.assertEqual(review['overall_verdict'],'incomplete, with the smallest missing implication')
        self.assertEqual(review['current_scope']['remaining_balanced_classes'],796)

    def test_new_exact_results_replay_the_bound_observation(self):
        retained=json.loads((AREA/'verification/current-exact-008/stdout.txt').read_bytes())['checks'][1]['report']
        run=subprocess.run([sys.executable,'-B','-S',str(AREA/'solver/check_global_typed.py')],capture_output=True,text=True,check=True,timeout=90)
        self.assertEqual(json.loads(run.stdout),retained)
        self.assertEqual(retained['whole_skeleton_coverage']['newly_covered'],1196)
        self.assertEqual(retained['quartic_root_controls']['physical_quartics'],112)
        self.assertEqual(retained['one_C_endpoint_controls']['endpoint_trial_comparisons'],392)
        self.assertEqual([r['margin'] for r in retained['certificate']['whole_class_margins']],
          ['1/100000000000','1/1000000000000000000000000000000','1/10000000000000','1/10000000000000000000000000000000000000'])

    def test_current_source_reaches_global_and_unchanged_predecessor(self):
        state=json.loads((AREA/'STATE.json').read_bytes())
        self.assertEqual(state['current_phase'],'balanced-resonance-face-001')
        self.assertIn('009',state['current_evidence']['portable_exact_suite'])
        self.assertEqual(state['formal_scope']['theorems'],41)
        self.assertIn('solver/check_current_resonance.py',(AREA/'replay_current.py').read_text())
        wrapper=(AREA/'solver/check_current_global.py').read_text()
        self.assertIn('check_stable_energy.py',wrapper)
        self.assertIn('check_global_typed.py',wrapper)
        self.assertEqual(state['mixed_representatives']['remaining_by_reactive_budget'],{'2':0,'3':0,'4':796})
        self.assertFalse(state['new_lean_claim']);self.assertFalse(state['new_hardware_claim'])

    def test_vector_sources_are_deterministic_and_current_on_phone(self):
        spec=importlib.util.spec_from_file_location('physical_figure',AREA/'figures/generate_stable_energy.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for mobile in (False,True):
            path=AREA/('figures/stable-energy'+('.mobile' if mobile else '')+'.svg')
            self.assertEqual(path.read_text(encoding='utf-8'),module.build(mobile))
            self.assertIn('796',module.build(mobile));self.assertNotIn('1,992',module.build(mobile))
        source=(ROOT/'tools/smith_chart_unified.py').read_text()
        self.assertIn('GLOBAL_TYPED_MARGINS.md',source)
        self.assertIn('Earlier margin checkpoints and derivations',source)
        search=(ROOT/'tools/smith_chart_research.py').read_text()
        self.assertIn("100000 if slug=='typed-margins'",search)

if __name__=='__main__':unittest.main()
