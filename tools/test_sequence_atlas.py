"""Independent arithmetic oracles, snapshot coverage, and generated-page checks."""
from fractions import Fraction
import gzip
import hashlib
import json
from math import comb, factorial
from pathlib import Path
import tempfile
import unittest

from build_reader_site import Site
from check_reader_site import Page, check_search_targets
from sequence_atlas import ROOT, build, catalogue, reciprocal, terms
from update_sequence_atlas_oeis import compare


class SequenceAtlasTests(unittest.TestCase):
    def test_reciprocals_against_ordinary_rational_series(self):
        count = 16
        for N in range(2, 9):
            denominator = [Fraction((-1)**k, factorial(N*k)) for k in range(count)]
            inverse = [Fraction(1)]
            for n in range(1, count):
                inverse.append(-sum(denominator[k]*inverse[n-k] for k in range(1, n+1)))
            power = [Fraction(1)]+[Fraction(0)]*(count-1)
            for r in range(1, 4):
                power = [sum(power[k]*inverse[n-k] for k in range(n+1)) for n in range(count)]
                self.assertEqual([x*factorial(N*n) for n, x in enumerate(power)], list(reciprocal(N, r, count)), (N,r))
        self.assertEqual(reciprocal(2,1,6), (1,1,5,61,1385,50521))
        self.assertEqual(reciprocal(4,1,5), (1,1,69,33661,60376809))

    def test_counting_families_against_binomial_recurrences(self):
        bell, fubini = [1], [1]
        for n in range(1, 32):
            bell.append(sum(comb(n-1,k)*bell[k] for k in range(n)))
            fubini.append(sum(comb(n,k)*fubini[n-k] for k in range(1,n+1)))
        self.assertEqual(terms({'kind':'bell'},32), bell)
        self.assertEqual(terms({'kind':'fubini'},32), fubini)
        self.assertEqual(bell[:6], [1,1,2,5,15,52])
        self.assertEqual(fubini[:6], [1,1,3,13,75,541])

    def test_snapshot_scans_all_positions_and_records_finite_scope(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            with gzip.open(base/'stripped.gz','wt') as f:
                f.write('# fixture\nA000001 ,99,1,2,3,4,5,6,7,8,9,\nA000002 ,1,2,3,4,5,6,99,\nA000003 ,1,2,3,4,5,\n')
            with gzip.open(base/'names.gz','wt') as f:
                f.write('A000001 Fixture one\nA000002 Fixture two\n')
            report=compare(base/'stripped.gz',base/'names.gz',[{'id':'fixture','terms':list(map(str,range(1,10)))}])
            self.assertEqual(report['sequence_count'],3)
            self.assertEqual([(m['id'],m['position'],m['matched_terms']) for m in report['matches']['fixture']], [('A000001',1,9),('A000002',0,6)])
            self.assertEqual(report['matches']['fixture'][0]['name'],'Fixture one')

    def test_retained_snapshot_matches_current_catalogue(self):
        path=ROOT/'manifests/sequence-atlas-oeis.json'
        if not path.exists():
            self.skipTest('Bulk snapshot not supplied; UI labels it unavailable')
        report=json.loads(path.read_text(encoding='utf-8'))
        signature=hashlib.sha256(json.dumps([(e['id'],e['terms']) for e in catalogue()],separators=(',',':')).encode()).hexdigest()
        self.assertEqual(report['catalogue_terms_sha256'],signature)
        self.assertGreater(report['sequence_count'],100000)
        self.assertEqual(report['license'],'CC-BY-SA-4.0')

    def test_generated_catalogue_pages_and_exact_exports(self):
        with tempfile.TemporaryDirectory() as folder:
            site=Site.__new__(Site);site.root=ROOT;site.output=Path(folder);site.search=[]
            result=build(site)
            self.assertEqual(result['entries'],26)
            main=(site.output/'sequences.html').read_text(encoding='utf-8')
            self.assertIn('<noscript>',main)
            self.assertIn('CC BY-SA 4.0',main)
            self.assertNotIn('data-side-reader-link',main)
            for identifier in ('sa-query','sa-search-form','sa-results','sa-search-error','sa-previous-point','sa-next-window','sa-table-detail'):
                self.assertIn('id="'+identifier+'"',main)
            self.assertIn('role="search"',main)
            self.assertIn('value="mod-pairs"',main)
            pages={}
            for path in site.output.rglob('*.html'):
                source=path.read_text(encoding='utf-8');page=Page(source)
                self.assertEqual((page.h1,page.main),(1,1),str(path))
                self.assertEqual(len(page.ids),len(set(page.ids)))
                self.assertTrue(page.skip)
                for control in page.inputs:
                    self.assertTrue(control.get('id') in page.labels or control.get('aria-label'),control)
                pages[path.relative_to(site.output).as_posix()]=page
            check_search_targets(site.search,pages)
            data=json.loads((site.output/'assets/sequence-atlas-data.json').read_text(encoding='utf-8'))
            for entry in data['entries']:
                self.assertEqual(entry['terms'],list(map(str,terms(entry))))
                if entry['kind']=='euler':
                    self.assertEqual(entry['work_ids'],['paper-iv'])
                lines=(site.output/'sequences'/f"{entry['id']}.csv").read_text().splitlines()
                self.assertEqual(len(lines),65)
                self.assertEqual(lines[-1],f"63,{entry['terms'][63]}")
                indexed=(site.output/'sequences'/f"{entry['id']}.txt").read_text().splitlines()
                self.assertEqual(indexed[-1],f"63 {entry['terms'][63]}")
                self.assertEqual(len([line for line in indexed if not line.startswith('#')]),64)
                exported=json.loads((site.output/'sequences'/f"{entry['id']}.json").read_text(encoding='utf-8'))
                self.assertEqual(exported['terms'],entry['terms'])
                self.assertEqual(exported['oeis_reference']['license'],'CC-BY-SA-4.0')
                source=(site.output/'sequences'/f"{entry['id']}.html").read_text(encoding='utf-8')
                self.assertIn('Related entries',source)
                self.assertIn('data-save-sequence="'+entry['id']+'"',source)
                self.assertEqual('rel="prev"' in source,entry['id']!='KSEQ-000001')
                self.assertEqual('rel="next"' in source,entry['id']!='KSEQ-000026')
                if entry['source'].startswith('collection/'):
                    target=entry['source'].split('#')[0].replace('collection/','docs/').replace('.html','.md')
                    self.assertTrue((ROOT/target).is_file(),target)
            script=(site.output/'assets/sequence-atlas.js').read_text(encoding='utf-8')
            self.assertIn('./sequence-atlas-search.mjs?v=',script)
            self.assertIn('./sequence-atlas-saved.mjs?v=',script)
            self.assertIn('./sequence-atlas-saved.mjs?v=',(site.output/'assets/sequence-atlas-entry.js').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
