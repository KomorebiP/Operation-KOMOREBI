"""Keep the new evidence, reader source and completion status consistent."""
from pathlib import Path
import hashlib,json,subprocess,sys,unittest

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/smith-chart/unified'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class SmithCoefficientRouteTests(unittest.TestCase):
    def test_fresh_evidence_and_review_bind_maintained_sources(self):
        directory=AREA/'verification/current-exact-006'
        m=json.loads((directory/'manifest.json').read_bytes())
        self.assertEqual((m['schema_version'],m['run']['status']),(2,'completed'))
        for row in m['input_artifacts']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'],row['path'])
            self.assertEqual(row['sha256'],row['sha256_after'])
        for row in m['outputs']:self.assertEqual(digest(ROOT/row['path']),row['sha256'])
        review=json.loads((AREA/'PHASE4_REVIEW.json').read_bytes())
        for name,h in review['source_sha256'].items():self.assertEqual(digest(AREA/name),h,name)
        self.assertEqual(review['unchanged_scope']['remaining_mixed_representatives'],1992)

    def test_new_physical_controls_reproduce_retained_observations(self):
        old=json.loads((AREA/'verification/current-exact-006/stdout.txt').read_bytes())['checks'][1]['report']
        run=subprocess.run([sys.executable,'-B','-S',str(AREA/'solver/check_coefficient_routes.py')],
          capture_output=True,text=True,check=True,timeout=90)
        self.assertEqual(json.loads(run.stdout),old)
        self.assertEqual(old['universal_templates']['boundary_lifts_checked'],2130)
        self.assertEqual(old['single_kind_minima']['physical_minimum_controls'],24)
        self.assertEqual(len(old['passive_transfer_counterexamples']),9)
        self.assertEqual([r['reflection_margin'] for r in old['series_margins']['certificate']['certificates']],['1/2000','1/500000'])

    def test_replay_reaches_new_checks_and_scope_stays_explicit(self):
        replay=(AREA/'replay_current.py').read_text(encoding='utf-8')
        self.assertIn('solver/check_current_routes.py',replay)
        state=json.loads((AREA/'STATE.json').read_bytes())
        self.assertEqual(state['current_phase'],'coefficient-fiber-and-series-001')
        self.assertEqual(state['formal_scope']['theorems'],41)
        self.assertEqual(state['mixed_representatives']['remaining'],1992)
        self.assertFalse(state['new_lean_claim'])
        self.assertEqual(len(state['remaining_work']),6)
        self.assertIn('COEFFICIENT_ROUTES.md',(ROOT/'tools/smith_chart_unified.py').read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
