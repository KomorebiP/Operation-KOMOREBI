"""Verify the new portable evidence and selected formal/source bindings."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,re,subprocess,sys,unittest,zipfile

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/smith-chart/unified'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class SystematicSmithTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result=subprocess.run([sys.executable,'-B','-S',str(AREA/'solver/check_phase2.py')],capture_output=True,text=True,check=True,timeout=180)
        cls.exact=json.loads(result.stdout)

    def test_physical_and_adversarial_controls(self):
        r=self.exact
        self.assertEqual(r['status'],'PASS')
        self.assertEqual((r['first_order_inputs'],r['first_order_certificates'],r['ideal_short_boundaries']),(600,576,24))
        self.assertEqual((r['cauer_certificates'],r['cauer_maximum_degree']),(52,15))
        self.assertEqual((r['independent_exact_phasor_samples'],r['power_identity_checks'],r['one_percent_tolerance_checks']),(4403,77,714))
        self.assertEqual(len(r['adversarial_controls']),16)
        self.assertEqual(r['Hughes_resistor_minimum']['lower_bound'],2)
        self.assertEqual(r['parallel_RLC_refutation']['canonical_mixed_representatives_excluded'],1)
        self.assertFalse(r['parallel_RLC_refutation']['all_remaining_mixed_representatives_excluded'])

    def test_original_hughes_witness_bytes(self):
        b=json.loads((AREA/'phase2-source-bindings.json').read_bytes())
        archive=AREA/'archives'/b['archive']
        self.assertEqual(digest(archive),b['archive_sha256'])
        with zipfile.ZipFile(archive) as z:raw=z.read(b['member'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(),b['member_sha256'])
        self.assertEqual(raw,(AREA/'solver/hughes_two_resistor.json').read_bytes())

    def test_formal_receipt_and_axiom_scope(self):
        directory=AREA/'verification/phase2-formal-001'
        r=json.loads((directory/'receipt.json').read_bytes())
        self.assertEqual(r['status'],'PASS')
        self.assertEqual(r['input_sha256_before'],r['input_sha256_after'])
        for name,h in r['input_sha256_before'].items():
            source=AREA/'formal'/name if name!='dependency-lock.json' else ROOT/'formal/smith-chart-v0.1.0/dependency-lock.json'
            self.assertEqual(digest(source),h,name)
        for step in r['steps']:
            for stream in ('stdout','stderr'):
                self.assertEqual(digest(directory/(step['name']+'.'+stream+'.txt')),step[stream+'_sha256'])
            self.assertEqual(step['exit_code']==0,step['expected_success'])
        axioms=(directory/'axioms.stdout.txt').read_text(encoding='utf-8')
        self.assertEqual(axioms.count('depends on axioms:'),17)
        self.assertNotIn('sorryAx',axioms)
        for line in axioms.splitlines():
            self.assertLessEqual(set(re.search(r'\[([^]]*)\]',line)[1].split(', ')),{'propext','Classical.choice','Quot.sound'})
        self.assertEqual((r['negative_controls'],r['positive_fixtures']),(2,1))
        for name in ('wrong-conservation','wrong-margin'):
            self.assertIn('unsolved goals', (directory/(name+'.stdout.txt')).read_text(encoding='utf-8'))

    def test_current_computation_observations_are_still_bound(self):
        d=AREA/'verification/current-exact-002'
        r=json.loads((d/'manifest.json').read_bytes())
        self.assertEqual(r['schema_version'],2)
        self.assertIn('SMITH_SYSTEMATIC_CLOSURE',r['claim_id'])
        # The installed runner's schema owns the field layout. Verify every
        # observed source hash and raw output without rerunning a manifest command.
        self.assertEqual(r['run']['status'],'completed')
        for row in r['input_artifacts']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'])
            self.assertEqual(row['sha256'],row['sha256_after'])
        for row in r['outputs']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'])
        observed=json.loads((d/'stdout.txt').read_text(encoding='utf-8'))
        self.assertEqual(observed['status'],'PASS')
        self.assertEqual(observed['checks'][1]['report'],self.exact)

    def test_self_review_and_optional_probe_provenance(self):
        review=json.loads((AREA/'PHASE2_REVIEW.json').read_bytes())
        for name,h in review['source_sha256'].items():
            self.assertEqual(digest(AREA/name),h,name)
        d=AREA/'verification/mixed-probe-003'
        manifest=json.loads((d/'manifest.json').read_bytes())
        self.assertEqual(manifest['run']['status'],'completed')
        for row in manifest['input_artifacts']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'])
            self.assertEqual(row['sha256'],row['sha256_after'])
        for row in manifest['outputs']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'])
        probe=json.loads((d/'results/summary.json').read_bytes())
        self.assertEqual((probe['canonical_population'],probe['processed']),(2130,62))
        self.assertEqual(probe['backend_files_sha256_before'],probe['backend_files_sha256_after'])
        self.assertTrue(probe['backend_files_sha256_before'])
        self.assertEqual(sum(probe['counts'].values()),62)
        self.assertTrue(any('UNKNOWN' in s for s in probe['non_claims']))

    def test_shunt_class_extension_and_formal_receipt(self):
        run=subprocess.run([sys.executable,'-B','-S',str(AREA/'solver/check_shunt_extension.py')],capture_output=True,text=True,check=True,timeout=60)
        report=json.loads(run.stdout)
        self.assertEqual((report['total_mixed_representatives_excluded'],report['remaining_mixed_representatives']),(60,2070))
        self.assertEqual(report['independent_physical_shapes'],36)
        d=AREA/'verification/current-exact-003'
        manifest=json.loads((d/'manifest.json').read_bytes())
        for row in manifest['input_artifacts']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'])
            self.assertEqual(row['sha256'],row['sha256_after'])
        for row in manifest['outputs']:self.assertEqual(digest(ROOT/row['path']),row['sha256'])
        self.assertEqual(json.loads((d/'stdout.txt').read_bytes())['checks'][1]['report'],report)
        d=AREA/'verification/phase2-shunt-formal-001'
        r=json.loads((d/'receipt.json').read_bytes())
        self.assertEqual((r['status'],r['total_selected_with_core']),('PASS',21))
        self.assertEqual(digest(AREA/'verification/phase2-formal-001/receipt.json'),r['core_receipt_sha256'])
        self.assertEqual(r['input_sha256_before'],r['input_sha256_after'])
        for name,h in r['input_sha256_before'].items():self.assertEqual(digest(AREA/'formal'/name),h)
        for step in r['steps']:
            self.assertEqual(step['exit_code']==0,step['expected_success'])
            for stream in ('stdout','stderr'):
                self.assertEqual(digest(d/(step['name']+'.'+stream+'.txt')),step[stream+'_sha256'])
        axioms=(d/'compile-shunt.stdout.txt').read_text(encoding='utf-8')
        self.assertEqual(axioms.count('depends on axioms:'),4)
        self.assertNotIn('sorryAx',axioms)
        for line in axioms.splitlines():
            self.assertLessEqual(set(re.search(r'\[([^]]*)\]',line)[1].split(', ')),{'propext','Classical.choice','Quot.sound'})
        self.assertIn('unsolved goals',(d/'wrong-shunt.stdout.txt').read_text(encoding='utf-8'))

    def test_complementary_capacitor_class_and_union(self):
        run=subprocess.run([sys.executable,'-B','-S',str(AREA/'solver/check_cap_shunt_extension.py')],capture_output=True,text=True,check=True,timeout=60)
        report=json.loads(run.stdout)
        self.assertEqual((report['total_mixed_representatives_excluded'],report['remaining_mixed_representatives']),(119,2011))
        self.assertEqual([r['excluded_union'] for r in report['coverage']],[7,26,86])
        self.assertEqual(report['independent_physical_shapes'],36)
        cert=json.loads((AREA/'solver/cap_shunt_rl_refutation.json').read_bytes())
        ys=[(1-F(g))/(1+F(g)) for g in cert['sample_gammas']]
        self.assertEqual(sum(w*y for w,y in zip((1,-6,15,-20,15,-6,1),ys)),F(-18225,9325316))
        d=AREA/'verification/current-exact-004'
        manifest=json.loads((d/'manifest.json').read_bytes())
        self.assertEqual(manifest['run']['status'],'completed')
        for row in manifest['input_artifacts']:
            self.assertEqual(digest(ROOT/row['path']),row['sha256'])
            self.assertEqual(row['sha256'],row['sha256_after'])
        for row in manifest['outputs']:self.assertEqual(digest(ROOT/row['path']),row['sha256'])
        self.assertEqual(json.loads((d/'stdout.txt').read_bytes())['checks'][1]['report'],report)
        d=AREA/'verification/phase2-cap-shunt-formal-001'
        r=json.loads((d/'receipt.json').read_bytes())
        self.assertEqual((r['status'],r['total_selected_with_earlier']),('PASS',25))
        for name,h in r['earlier_receipt_sha256'].items():self.assertEqual(digest(AREA/'verification'/name/'receipt.json'),h)
        self.assertEqual(r['input_sha256_before'],r['input_sha256_after'])
        for name,h in r['input_sha256_before'].items():
            source=ROOT/'formal/smith-chart-v0.1.0/dependency-lock.json' if name=='dependency-lock.json' else AREA/'formal'/name
            self.assertEqual(digest(source),h)
        for step in r['steps']:
            self.assertEqual(step['exit_code']==0,step['expected_success'])
            for stream in ('stdout','stderr'):self.assertEqual(digest(d/(step['name']+'.'+stream+'.txt')),step[stream+'_sha256'])
        axioms=(d/'compile-cap-shunt.stdout.txt').read_text(encoding='utf-8')
        self.assertEqual(axioms.count('depends on axioms:'),4)
        self.assertNotIn('sorryAx',axioms)
        for line in axioms.splitlines():
            self.assertLessEqual(set(re.search(r'\[([^]]*)\]',line)[1].split(', ')),{'propext','Classical.choice','Quot.sound'})
        self.assertIn('unsolved goals',(d/'wrong-cap-shunt.stdout.txt').read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
