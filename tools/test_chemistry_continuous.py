from fractions import Fraction as F
import hashlib,io,json,tempfile,unittest,zipfile
from pathlib import Path
from unittest import mock
from chemistry_continuous_data import build,DATA,replay,VERIFY,ep,cell
from chemistry_responses import build as build_reader
from test_computational_chemistry import fixture_site
ROOT=Path(__file__).resolve().parents[1]
class ContinuousTests(unittest.TestCase):
    def test_public_coefficients_enclose_the_endpoint_inequalities(self):
        data=build();self.assertEqual((ROOT/DATA).read_bytes(),(json.dumps(data,separators=(',',':'))+'\n').encode());self.assertEqual(len(data['groups']),22)
        cells=0
        for c in data['groups']:
            self.assertEqual(len(c['cells']),len(c['points'])-1)
            for i,public in enumerate(c['cells']):
                for pts,key in [(c['points'],'coefficient'),(c['reduced_points'],'reduced_coefficient')]:
                    reference=cell(ep(pts[i]),ep(pts[i+1]));C=F(public[key]);self.assertGreaterEqual(C,reference['interpolation_coefficient']);self.assertLess(C-reference['interpolation_coefficient'],F(1,10**18))
                minimum=max(F(c['points'][i]['radius']),F(c['points'][i+1]['radius']))+F(public['coefficient'])/4
                self.assertGreaterEqual(F(public['uniform_radius']),minimum);cells+=1
        self.assertEqual(cells,1005)
        narrow=next(c for c in data['groups'] if c['order']==512);self.assertEqual(len(narrow['points']),166);self.assertLessEqual(F(narrow['maximum_radius']),F(1,10))
        broad=next(c for c in data['groups'] if c['eta']=='1/10' and c['order']==128);self.assertGreater(F(broad['whole_interval_gap']),F(2365,100000))
    def test_replay_has_all_active_and_historical_inputs(self):
        raw=replay()
        with mock.patch('zipfile.sys.platform','linux'):self.assertEqual(raw,replay())
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            p=json.loads(z.read('PACKAGE.json'));self.assertEqual(len(z.namelist()),len(set(z.namelist())))
            for item in p['files']:self.assertEqual(hashlib.sha256(z.read(item['path'])).hexdigest(),item['sha256'])
            for name in ['intervals-001','audit-003','narrow-003']:
                record=json.loads(z.read((VERIFY/name/'manifest.json').as_posix()));self.assertEqual(record['run']['status'],'completed')
                for item in record['input_artifacts']+record['outputs']:self.assertEqual(hashlib.sha256(z.read(item['path'])).hexdigest(),item['sha256'])
    def test_existing_reader_gets_static_continuous_results_and_a_proof_route(self):
        with tempfile.TemporaryDirectory() as directory:
            site=fixture_site(Path(directory));result=build_reader(site);self.assertEqual(result['continuous']['cells'],1005)
            html=(site.output/'chemistry-responses.html').read_text(encoding='utf-8')
            for phrase in ['id="cr-continuous"','166','0.02365','Download interval certificate','Download the continuous-response replay','125 additional energies']:self.assertIn(phrase,html)
            note=(site.output/'read/computational-chemistry/continuous.html').read_text(encoding='utf-8');self.assertIn('Hermiticity is essential',note);self.assertIn('512',note)
            self.assertEqual((site.output/'assets/chemistry/continuous-v1.json').read_bytes(),(ROOT/DATA).read_bytes())
            core=(site.output/'assets/chemistry-continuous-core.mjs').read_text();self.assertIn('chemistry-lab-core.mjs?v=',core)
if __name__=='__main__':unittest.main()
