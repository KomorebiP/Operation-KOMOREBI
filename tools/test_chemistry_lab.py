"""Check lab source identity, exact fixture regeneration, and reader routes."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from chemistry_lab import build
from chemistry_lab_data import build as build_data, DATA
from test_computational_chemistry import fixture_site
from check_reader_site import Page,check_search_targets

ROOT=Path(__file__).resolve().parents[1]


class ChemistryLabTests(unittest.TestCase):
    def test_completed_finite_run_still_matches_current_inputs_and_outputs(self):
        record=json.loads((ROOT/'verification/chemistry-lab/run-002/manifest.json').read_bytes())
        self.assertEqual(record['run']['status'],'completed')
        for item in record['input_artifacts']:
            self.assertEqual(item['sha256'],item['sha256_after'])
            self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),item['sha256'])
        for item in record['outputs']:
            self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),item['sha256'])

    def test_exact_fixtures_regenerate_and_match_the_sealed_decoder(self):
        expected=(json.dumps(build_data(),separators=(',',':'))+'\n').encode()
        self.assertEqual((ROOT/DATA).read_bytes(),expected)
        data=json.loads(expected)
        self.assertEqual([s['rank'] for s in data['stages']][-1],21)
        self.assertEqual(len(data['samples']),5)

    def test_lab_build_retains_static_content_and_hash_binds_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            site=fixture_site(Path(directory)); result=build(site)
            self.assertEqual(result['examples'],5)
            body=(site.output/'chemistry-lab.html').read_text(encoding='utf-8')
            self.assertIn('Why does the third action matter?',body)
            self.assertIn('without JavaScript',body)
            self.assertIn('finite-basis approximation error',body)
            self.assertIn(hashlib.sha256((ROOT/DATA).read_bytes()).hexdigest(),body)
            self.assertIn('data-probes="3"',body)
            page=Page(body)
            check_search_targets(site.search,{'chemistry-lab.html':page})
            script=(site.output/'assets/chemistry-lab.js').read_text(encoding='utf-8')
            self.assertIn('chemistry-lab-core.mjs?v=',script)
            self.assertEqual((site.output/'assets/chemistry/lab-v1.json').read_bytes(),(ROOT/DATA).read_bytes())

    def test_reader_and_home_link_to_the_experiment(self):
        from home_page import home_page
        from computational_chemistry import publish
        self.assertIn('chemistry-lab.html',home_page())
        with tempfile.TemporaryDirectory() as directory:
            site=fixture_site(Path(directory)); publish(site);site.markdown_pages()
            for path in ['collection/COMPUTATIONAL_CHEMISTRY.html','read/computational-chemistry/three-queries.html']:
                self.assertIn('chemistry-lab.html',(site.output/path).read_text(encoding='utf-8'))


if __name__=='__main__': unittest.main()
