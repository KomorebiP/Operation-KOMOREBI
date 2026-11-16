"""Finite evidence identity, outward web bounds, replay and reader integration."""
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from chemistry_responses_data import build as data_build,DATA,VERIFY,replay
from chemistry_responses import build
from test_computational_chemistry import fixture_site
from check_reader_site import Page,check_search_targets

ROOT=Path(__file__).resolve().parents[1]

class ChemistryResponsesTests(unittest.TestCase):
    def test_fixtures_reproduce_and_round_outward(self):
        data=data_build();self.assertEqual((ROOT/DATA).read_bytes(),(json.dumps(data,separators=(',',':'))+'\n').encode())
        raw=json.loads((ROOT/VERIFY/'responses-001/results/curves.json').read_bytes())['points']
        for public,source in zip(data['points'],raw):
            self.assertEqual(public['center'],source['response_center'])
            self.assertGreaterEqual(F(public['radius']),F(source['radius_rational_upper']))
            self.assertLess(F(public['radius'])-F(source['radius_rational_upper']),F(1,10**18))
        reduced=json.loads((ROOT/VERIFY/'reduction-001/results/curves.json').read_bytes())['points']
        red={(x['ionic_energy'],x['eta']):x for x in reduced if x['source']=='stored-removal'}
        for public,source in zip(data['points'],raw):
            r=red[public['energy'],public['eta']]
            lower=max(F(0),abs(F(public['center']['imaginary'])-F(r['response_center']['imaginary']))-F(source['radius_rational_upper'])-F(r['reduced_model_radius_rational_upper']))
            self.assertLessEqual(F(public['imaginary_discrepancy_lower']),lower)
            self.assertLess(lower-F(public['imaginary_discrepancy_lower']),F(1,10**18))
        useful=[p for p in data['points'] if p['actions']==128 and p['eta']=='1/10']
        self.assertEqual(len(useful),41);self.assertTrue(all(F(p['radius'])<F(4,10**9) for p in useful))
        self.assertTrue(all(F(p['imaginary_discrepancy_lower'])>0 for p in useful))

    def test_replay_is_deterministic_and_complete(self):
        raw=replay();self.assertEqual(raw,replay())
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            package=json.loads(z.read('PACKAGE.json'))
            self.assertEqual(len(z.namelist()),len(set(z.namelist())))
            for item in package['files']:
                self.assertNotIn('..',Path(item['path']).parts)
                self.assertEqual(hashlib.sha256(z.read(item['path'])).hexdigest(),item['sha256'])
            for name in ['reduction-001','kernel-001','responses-001']:
                record=json.loads(z.read((VERIFY/name/'manifest.json').as_posix()))
                self.assertEqual(record['run']['status'],'completed')
                for item in record['input_artifacts']+record['outputs']:self.assertEqual(hashlib.sha256(z.read(item['path'])).hexdigest(),item['sha256'])

    def test_reader_preserves_static_results_and_bound_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            site=fixture_site(Path(directory));result=build(site)
            self.assertEqual(result['samples'],984)
            body=(site.output/'chemistry-responses.html').read_text(encoding='utf-8');page=Page(body)
            check_search_targets(site.search,{'chemistry-responses.html':page})
            for phrase in ['37.506%','52,920','conditional','without JavaScript','Scan and certificates','Three reduced-model actions','73 small-model columns']:
                self.assertIn(phrase,body)
            self.assertIn(hashlib.sha256((ROOT/DATA).read_bytes()).hexdigest(),body)
            self.assertEqual((site.output/'assets/chemistry/responses-v1.json').read_bytes(),(ROOT/DATA).read_bytes())
            self.assertEqual(hashlib.sha256((site.output/'assets/chemistry/stage15-replay.zip').read_bytes()).hexdigest(),result['replay_sha256'])

    def test_chemistry_and_home_entry_points(self):
        from home_page import home_page
        from computational_chemistry import publish
        from chemistry_lab import build as lab
        self.assertIn('chemistry-responses.html',home_page())
        with tempfile.TemporaryDirectory() as directory:
            site=fixture_site(Path(directory));publish(site);lab(site);site.markdown_pages()
            for path in ['chemistry-lab.html','collection/COMPUTATIONAL_CHEMISTRY.html','read/computational-chemistry/three-queries.html']:
                self.assertIn('chemistry-responses.html',(site.output/path).read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
