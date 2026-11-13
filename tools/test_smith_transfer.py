"""Bind structural transfer and physical-state certificates to actual sources."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/smith-chart/unified'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class SmithPhysicalTransferTests(unittest.TestCase):
    def test_fresh_record_and_scoped_review_match_sources(self):
        m=json.loads((AREA/'verification/current-exact-011/manifest.json').read_bytes())
        self.assertEqual((m['schema_version'],m['run']['status']),(2,'completed'))
        for row in m['input_artifacts']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'],row['path'])
            self.assertEqual(row['sha256'],row['sha256_after'])
        for row in m['outputs']:self.assertEqual(digest(ROOT/row['path']),row['sha256'])
        review=json.loads((AREA/'PHASE8_REVIEW.json').read_bytes())
        for p,h in review['source_sha256'].items():self.assertEqual(digest(AREA/p),h,p)
        self.assertEqual(review['parent_program_verdict'],'incomplete')
        self.assertEqual(review['current_scope']['global_structural_margin'],'10^(-10^45)')
        self.assertTrue(review['current_scope']['practical_global_margin_open'])
        self.assertFalse(review['current_scope']['new_independent_review'])
        state=json.loads((AREA/'STATE.json').read_bytes())
        self.assertEqual(state['formal_scope']['theorems'],41)
        self.assertEqual(state['mixed_representatives']['remaining'],796)
        self.assertIn('011',state['current_evidence']['portable_exact_suite'])
    def test_exact_controls_and_independent_physical_consumer(self):
        reports=[]
        for name in ('check_backbone_transfer.py','lossless_separator.py','check_transfer_consumer.py'):
            run=subprocess.run([sys.executable,'-B','-S',str(AREA/'solver'/name)],capture_output=True,text=True,check=True,timeout=90)
            report=json.loads(run.stdout);self.assertEqual(report['status'],'PASS');reports.append(report)
        self.assertEqual(reports[0]['feature_corner_graphs'],32)
        self.assertEqual(reports[0]['dense_R_slots'],45)
        self.assertEqual(reports[2]['driven_certificate_strict_margin'],'1/400')
        self.assertEqual(reports[2]['consumer_corruptions_rejected'],5)
        self.assertEqual(reports[2]['generic_interpolation_rank_controls'],2)
    def test_source_bound_desktop_and_mobile_pipeline_figure(self):
        spec=importlib.util.spec_from_file_location('transfer_figure',AREA/'figures/generate_global_transfer.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for mobile in (False,True):
            p=AREA/('figures/global-transfer'+('.mobile' if mobile else '')+'.svg')
            self.assertEqual(p.read_text(encoding='utf-8'),module.build(mobile))
            self.assertIn('10⁴⁵',module.build(mobile));self.assertIn('9',module.build(mobile))

if __name__=='__main__':unittest.main()
