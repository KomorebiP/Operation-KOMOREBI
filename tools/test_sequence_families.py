import hashlib
from copy import deepcopy
from html import unescape
import json
import re
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from sequence_generalized import family_definitions, source_manifest, catalogue as family_catalogue, links_for, membership, build_pages
from sequence_archive_families import ARCHIVE_MEMBERSHIP, archive_parameters
from sequence_library import library_entries
from sequence_atlas import catalogue, reciprocal
from sequence_formula_catalogue import tangent

ROOT=Path(__file__).resolve().parents[1]


class GeneralizedFamiliesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries=library_entries(catalogue())
        cls.by_id={entry['id']:entry for entry in cls.entries}
        cls.data=family_catalogue(cls.entries)

    def test_sources_are_bound_to_maintained_passages(self):
        sources = source_manifest()['sources']
        self.assertEqual(len(sources), 12)
        for source in sources:
            text = (ROOT/source['path']).read_text(encoding='utf-8')
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), source['normalized_sha256'])
            self.assertTrue(source['headings'])
            for heading in source['headings']:
                self.assertLessEqual(heading['line'], len(text.splitlines()))
        definitions = family_definitions()
        self.assertEqual(len(definitions), 36)
        self.assertEqual(sum(bool(f['engine']) for f in definitions), 10)
        self.assertEqual(sum(f['family_type']=='analytic family' for f in definitions),12)
        self.assertEqual(sum(f['family_type']=='discrete construction' for f in definitions),13)
        self.assertEqual(sum(f['family_type']=='reference collection' for f in definitions),1)
        self.assertTrue(all(f['source'].startswith('https://github.com/') and '#L' in f['source'] for f in definitions))
        self.assertTrue(all('record_ids' not in family for family in definitions))

    def test_family_memberships_do_not_change_integer_records(self):
        entries = self.entries
        before=deepcopy(entries)
        data = family_catalogue(entries)
        self.assertEqual(entries,before)
        ids = {e['id'] for e in entries}
        self.assertEqual(len(data['relations']), 1231)
        for family in data['families']:
            self.assertLessEqual(set(family['record_ids']), ids)
        for edge in data['relations']:
            self.assertIn(edge['source'], ids)
            self.assertIn(edge['target'], ids)
        euler = next(e for e in entries if e['kind'] == 'euler' and e['collection'] == 'atlas')
        linked = links_for(euler)
        self.assertIn('GF-CONGRUENTIAL', linked)
        self.assertNotIn('GF-RECIPROCAL', linked)
        self.assertNotIn('generalized_family_ids', euler)

    def test_all_recovered_records_have_an_exactly_labeled_home(self):
        self.assertEqual(set(ARCHIVE_MEMBERSHIP),{f'KOM{n:03d}' for n in range(1,91)})
        self.assertEqual(self.data['archive_coverage'],dict(records=90,assigned=90))
        for identifier,family_id in ARCHIVE_MEMBERSHIP.items():
            with self.subTest(identifier=identifier):
                self.assertEqual(membership(self.by_id[identifier]),[family_id])
                family=next(f for f in self.data['families'] if f['id']==family_id)
                self.assertIn(identifier,family['record_ids'])
        # The weighted logarithmic normalization is not the tangent explorer's sequence.
        for n in range(29,36):
            self.assertEqual(membership(self.by_id[f'KOM{n:03d}']),['GF-BLOCK-LOGARITHMIC'])
        reference=next(f for f in self.data['families'] if f['id']=='GF-CLASSICAL-REFERENCES')
        self.assertEqual(reference['family_type'],'reference collection')
        self.assertIsNone(reference['engine'])

    def test_recovered_explorer_links_reproduce_the_same_reciprocal_values(self):
        for identifier,family_id in ARCHIVE_MEMBERSHIP.items():
            if family_id!='GF-RECIPROCAL':continue
            with self.subTest(identifier=identifier):
                entry=self.by_id[identifier]
                url=unescape(re.search(r'href="([^"]+)"',links_for(entry)).group(1))
                query=parse_qs(urlparse(url).query)
                params=json.loads(query['parameters'][0])
                self.assertEqual(query['family'],['GF-RECIPROCAL'])
                self.assertEqual({k:params[k] for k in ('N','r')},archive_parameters(identifier))
                self.assertEqual(list(map(str,reciprocal(params['N'],params['r'],8))),entry['terms'][:8])
        for identifier in ('KOM013','KOM014','KOM015','KOM016'):
            url=unescape(re.search(r'href="([^"]+)"',links_for(self.by_id[identifier])).group(1))
            params=json.loads(parse_qs(urlparse(url).query)['parameters'][0])
            self.assertEqual(params['k'],int(identifier[3:])-10)

    def test_logarithmic_shift_and_factor_match_the_preserved_coefficients(self):
        for N in range(2,9):
            entry=self.by_id[f'KOM{N+27:03d}']
            values=tangent(N,12)
            expected=['0']+[str(N*n*values[n-1]) for n in range(1,13)]
            self.assertEqual(entry['terms'][:13],expected)
            linked=links_for(entry)
            self.assertIn('#definition',linked)
            self.assertNotIn('#family-explorer',linked)
            self.assertNotIn('parameters=',linked)

    def test_static_family_pages_preserve_examples_and_reproduction_access(self):
        class Site:
            root=ROOT
            def __init__(self):self.pages={};self.files={};self.search=[]
            def write(self,path,text):self.files[path]=text
            def page(self,path,title,body):self.pages[path]=body
        site=Site()
        build_pages(site,self.data,lambda body,*args,**kwargs:body)
        self.assertEqual(len(site.pages),37)
        exported=json.loads(site.files['assets/sequence-generalized-data.json'])
        for family in exported['families']:
            body=site.pages[family['url']]
            self.assertIn('id="definition"',body)
            self.assertIn(family['source'].replace('&','&amp;'),body)
            for example in family['examples']:
                self.assertEqual(example['terms'],self.by_id[example['id']]['terms'][:8])
                self.assertTrue(all(isinstance(term,str) for term in example['terms']))
                self.assertIn('../'+example['url'],body)
            if family['engine']:
                self.assertIn('<noscript>',body)
                self.assertIn('id="family-explorer-controls"',body)
            elif family['paper']=='ARCHIVE':
                self.assertIn('sequence-archive-sources.zip',body)
                self.assertNotIn('id="family-explorer-controls"',body)
                self.assertNotIn('analytic continuation',body)
            for identifier in family['archive_record_ids']:
                self.assertIn('../sequence-archive/'+identifier+'.html',body)
        smith=site.pages['generalized-families/GF-SMITH-POLYNOMIALS.html']
        self.assertIn('flat j=n(n+1)/2+k',smith)
        self.assertIn('KOM084',smith)
        self.assertIn('All 90 recovered archive records',site.pages['generalized-families/index.html'])


if __name__ == '__main__':
    unittest.main()
