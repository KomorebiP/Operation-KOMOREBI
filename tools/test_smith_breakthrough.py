"""Validate the new physical controls, retained evidence and coherent status."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,unittest

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/smith-chart/unified'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class SmithBreakthroughTests(unittest.TestCase):
    def test_new_exact_physical_and_classification_controls(self):
        retained=json.loads((AREA/'verification/current-exact-005/stdout.txt').read_bytes())
        for script,index in (('check_loss_tolerance.py',1),('check_two_reactive_margin.py',2)):
            run=subprocess.run([sys.executable,'-B','-S',str(AREA/'solver'/script)],
              capture_output=True,text=True,check=True,timeout=60)
            self.assertEqual(json.loads(run.stdout),retained['checks'][index]['report'])
        loss,two=[r['report'] for r in retained['checks'][1:]]
        self.assertEqual((loss['physical_tolerance_corners'],loss['branch_mismatch_checks']),(1110,4686))
        self.assertEqual(two['nonregular_bridge_polynomials'],
          {'t':'8','K':'64','lambda1':'-32','lambda2':'-8','mu1':'64'})

    def test_new_observations_and_claims_remain_byte_bound(self):
        directory=AREA/'verification/current-exact-005'
        manifest=json.loads((directory/'manifest.json').read_bytes())
        self.assertEqual((manifest['schema_version'],manifest['run']['status']),(2,'completed'))
        for row in manifest['input_artifacts']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'])
            self.assertEqual(row['sha256'],row['sha256_after'])
        for row in manifest['outputs']:self.assertEqual(digest(ROOT/row['path']),row['sha256'])
        review=json.loads((AREA/'PHASE3_REVIEW.json').read_bytes())
        for name,h in review['source_sha256'].items():self.assertEqual(digest(AREA/name),h,name)

    def test_actual_kernel_receipt_and_false_controls(self):
        directory=AREA/'verification/phase3-loss-reduction-formal-001'
        r=json.loads((directory/'receipt.json').read_bytes())
        self.assertEqual((r['status'],r['new_theorem_axiom_audits'],r['total_selected_with_three_prior_receipts']),('PASS',16,41))
        self.assertEqual(r['input_sha256_before'],r['input_sha256_after'])
        for name,h in r['input_sha256_before'].items():self.assertEqual(digest(AREA/'formal'/name),h)
        self.assertEqual(digest(AREA/'verification/phase2-formal-001/receipt.json'),r['core_receipt_sha256'])
        for step in r['steps']:
            self.assertEqual(step['exit_code']==0,step['expected_success'])
            for stream in ('stdout','stderr'):
                self.assertEqual(digest(directory/(step['name']+'.'+stream+'.txt')),step[stream+'_sha256'])
        axioms=(directory/'axioms-loss-reduction.stdout.txt').read_text(encoding='utf-8')
        self.assertEqual(axioms.count('depends on axioms:'),16)
        self.assertNotIn('sorryAx',axioms)
        for names in re.findall(r'axioms:\s*\[([^]]*)\]',axioms):
            self.assertLessEqual(set(names.split(', ')),{'propext','Classical.choice','Quot.sound'})
        for name in ('wrong-mesh','wrong-disk'):
            self.assertIn('unsolved goals',(directory/(name+'.stdout.txt')).read_text(encoding='utf-8'))

    def test_single_live_status_agrees_with_scoped_progress(self):
        state=json.loads((AREA/'STATE.json').read_bytes())
        self.assertEqual(state['formal_scope']['theorems'],41)
        self.assertEqual(state['mixed_representatives'],{'population':2130,'excluded_union':138,
          'remaining':1992,'remaining_by_reactive_budget':{'2':0,'3':220,'4':1772}})
        self.assertEqual(len(state['remaining_work']),6)
        self.assertFalse(state['new_hardware_claim'])
        self.assertFalse(state['new_novelty_claim'])

if __name__=='__main__':unittest.main()
