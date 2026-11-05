"""Catalog integrity, source binding, and the imported exact finite replay."""
from collections import Counter
import hashlib
import importlib
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

import operator_catalog as catalog

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'examples/operator_catalog'


class OperatorCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = catalog.load_catalog(ROOT)
        cls.entries = {row['id']: row for row in cls.data['operators']}
        cls.checks = {row['id']: row for row in cls.data['checks']}

    def test_stable_ids_source_pins_and_evidence_bindings(self):
        self.assertEqual(len(self.data['operators']), 205)
        self.assertEqual(set(self.entries), {f'OP-{n:03d}' for n in range(1, 206)})
        self.assertEqual([row['id'] for row in self.data['families']], list('ABCDEFGHIJKL'))
        self.assertEqual(len(self.data['relations']), 28)
        self.assertEqual({row['id'] for row in self.data['relations']},
                         {f'REL-{n:02d}' for n in range(1, 29)})
        expected_checks = {f'{prefix}{n:02d}' for prefix, count in [('L', 18), ('A', 61), ('R', 85)]
                           for n in range(1, count + 1)}
        self.assertEqual(len(self.data['checks']), 164)
        self.assertEqual(set(self.checks), expected_checks)
        families = {row['id']: row for row in self.data['families']}
        for family in families.values():
            self.assertTrue(family['path'].startswith('docs/operators/catalog/'))
            self.assertNotIn('..', Path(family['path']).parts)
            self.assertTrue(family['path'].endswith('.md'))
        for code, source in self.data['sources'].items():
            with self.subTest(source=code):
                repo = source['repository'].split('/')[-1]
                self.assertEqual(source['commit'], self.data['repository_pins'][repo])
                self.assertRegex(source['commit'], r'^[0-9a-f]{40}$')
                url = urlsplit(source['url'])
                self.assertEqual((url.scheme, url.netloc), ('https', 'github.com'))
                self.assertTrue(url.path.startswith('/' + source['repository'] + '/blob/' + source['commit'] + '/'))
                if source.get('blob_sha'):
                    self.assertRegex(source['blob_sha'], r'^[0-9a-f]{40}$')
        for row in self.entries.values():
            with self.subTest(entry=row['id']):
                self.assertIn(row['family_id'], families)
                self.assertTrue(row['section'].startswith(row['family_id'] + '.'))
                self.assertEqual(row['source_urls'], [self.data['sources'][code]['url'] for code in row['source_codes']])
                self.assertTrue(row['source_urls'])
                self.assertTrue(set(row['related_ids']) <= self.entries.keys())
                for check_id in row['check_ids']:
                    self.assertIn(row['id'], self.checks[check_id]['operator_ids'])
        for check in self.checks.values():
            for entry_id in check['operator_ids']:
                self.assertIn(check['id'], self.entries[entry_id]['check_ids'])
        for relation in self.data['relations']:
            self.assertTrue(set(relation['operator_ids']) <= self.entries.keys())
            self.assertTrue(set(relation['check_ids']) <= self.checks.keys())
            self.assertTrue(relation['assumptions'])

    def test_math_delimiters_and_tex_survive_json(self):
        for row in self.entries.values():
            with self.subTest(entry=row['id']):
                self.assertTrue(row['formula'].startswith('$') and row['formula'].endswith('$'))
                self.assertEqual(row['formula'].count('$'), 2)
                for key in ('formula', 'scope', 'review_note'):
                    text = row.get(key, '')
                    self.assertEqual(len(re.findall(r'(?<!\\)\$', text)) % 2, 0, key)
                    self.assertFalse(any(ord(char) < 32 for char in text), key)
        for row in self.data['relations']:
            self.assertNotIn('$', row['law_tex'])
            self.assertFalse(any(ord(char) < 32 for char in row['law_tex']))
            self.assertEqual(len(re.findall(r'(?<!\\)\$', row['assumptions'])) % 2, 0)
        # A single TeX slash must survive; the substack linebreak is intentionally double.
        self.assertIn(r'\Phi', self.entries['OP-173']['formula'])
        self.assertNotIn(r'\\Phi', self.entries['OP-173']['formula'])
        self.assertIn(r'\\a+b', self.entries['OP-030']['formula'])

    def test_generated_pages_links_and_unique_entry_anchors(self):
        documents = catalog.build_documents(self.data)
        anchors = {path: re.findall(r'<a id="([^"]+)"></a>', text) for path, text in documents.items()}
        all_entry_anchors = []
        for path, text in documents.items():
            with self.subTest(page=path):
                self.assertEqual((ROOT / path).read_text(encoding='utf-8'), text)
                self.assertEqual(len(anchors[path]), len(set(anchors[path])))
                all_entry_anchors.extend(anchor for anchor in anchors[path] if anchor.startswith('op-'))
                self.assertEqual(text.count('```') % 2, 0)
                prose = re.sub(r'```[\s\S]*?```', '', text)
                prose = re.sub(r'\$[^$]*\$', '', prose)
                for target in re.findall(r'\[[^\]]*\]\(([^)\s]+)\)', prose):
                    parsed = urlsplit(target)
                    if parsed.scheme:
                        continue
                    target_path = posixpath.normpath(posixpath.join(posixpath.dirname(path), parsed.path)) if parsed.path else path
                    self.assertTrue((ROOT / target_path).is_file(), (path, target))
                    if parsed.fragment and target_path in documents:
                        self.assertIn(parsed.fragment, anchors[target_path], (path, target))
        self.assertEqual(Counter(all_entry_anchors), Counter(identifier.lower() for identifier in self.entries))
        self.assertFalse(any(anchor.startswith('op-') for anchor in anchors[catalog.INDEX_PATH]))
        for row in self.entries.values():
            path, anchor = catalog.entry_path(row, self.data).split('#')
            self.assertIn(anchor, anchors[path])
            self.assertEqual(path, catalog.family_path(row['section'], self.data))

    def test_worked_routes_reach_real_calculations_from_their_relations_and_entries(self):
        catalog.validate_worked_routes(self.data, ROOT)
        documents = catalog.build_documents(self.data)
        relations = {row['id']: row for row in self.data['relations']}

        def section(text, identifier):
            start = text.index('<a id="' + identifier.lower() + '"></a>')
            end = text.find('\n<a id="', start + 1)
            return text[start:] if end < 0 else text[start:end]

        for route in catalog.WORKED_ROUTES:
            relation_link = catalog.link(route['title'], route['path'], catalog.RELATIONS_PATH)
            for identifier in route['relation_ids']:
                with self.subTest(route=route['path'], relation=identifier):
                    text = section(documents[catalog.RELATIONS_PATH], identifier)
                    self.assertEqual(text.count(relation_link), 1)
            associated = {identifier for relation in route['relation_ids']
                          for identifier in relations[relation]['operator_ids']}
            for entry in self.data['operators']:
                page = catalog.family_path(entry['section'], self.data)
                entry_link = catalog.link(route['title'], route['path'], page)
                text = section(documents[page], entry['id'])
                with self.subTest(route=route['path'], operator=entry['id']):
                    self.assertEqual(text.count(entry_link), int(entry['id'] in associated))
        self.assertIn(catalog.link('worked compositions', catalog.COMPOSITION_PATH, catalog.INDEX_PATH),
                      documents[catalog.INDEX_PATH])

    def test_worked_routes_reject_unknown_relations_and_stale_destinations(self):
        route = catalog.WORKED_ROUTES[0]
        cases = [
            ([dict(route, relation_ids=('REL-99',))], 'relation binding'),
            ([dict(route, path='docs/operators/MISSING_CALCULATION.md#missing')], 'Missing worked-calculation page'),
            ([dict(route, path=route['path'] + '-missing')], 'Missing worked-calculation anchor'),
            ([route, route], 'duplicate worked-calculation route'),
        ]
        for routes, message in cases:
            with self.subTest(message=message), patch.object(catalog, 'WORKED_ROUTES', routes):
                with self.assertRaisesRegex(ValueError, message):
                    catalog.validate_worked_routes(self.data, ROOT)

    def test_fresh_fixture_replay_matches_catalog(self):
        for name, digest in self.data['provenance']['fixture_replay']['input_sha256'].items():
            self.assertEqual(hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest(), digest)
        baseline = FIXTURES / 'Komorebi_Operator_Audit_Checks.py'
        self.assertEqual(hashlib.sha256(baseline.read_bytes()).hexdigest(),
                         self.data['provenance']['files'][baseline.name])
        with tempfile.TemporaryDirectory() as directory:
            receipt_path = Path(directory) / 'receipt.json'
            result = subprocess.run(
                [sys.executable, '-B', str(FIXTURES / 'Komorebi_Operator_Refined_Checks.py'),
                 '--json', str(receipt_path)], cwd=directory, text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            self.assertEqual(sorted(path.name for path in Path(directory).iterdir()), ['receipt.json'])
        self.assertTrue(receipt['baseline_replayed'])
        self.assertEqual((receipt['baseline_checks'], receipt['added_checks']), (79, 85))
        self.assertEqual((receipt['passed'], receipt['failed']), (164, 0))
        self.assertEqual(receipt['kinds'], {'identity': 93, 'counterexample': 59, 'guard rejection': 12})
        self.assertEqual(receipt['checks'], self.data['checks'])
        with patch.object(sys, 'path', [str(ROOT), *sys.path]):
            module = importlib.import_module('examples.operator_catalog.Komorebi_Operator_Refined_Checks')
        self.assertEqual(Path(module.prior.__file__).resolve(), baseline.resolve())
        self.assertEqual(module.RECORDS, [])  # Importing the module does not run the suite.

    def test_descent_requires_an_induced_map_not_an_arbitrary_candidate(self):
        # q=I and T=I preserve ker(q)={0}, but the supplied candidate bar(T)=0 fails.
        q = lambda value: value
        transform = lambda value: value
        wrong_candidate = lambda value: 0
        witness = lambda value: value
        self.assertEqual(transform(0), 0)
        self.assertNotEqual(wrong_candidate(q(1)), q(transform(1)))
        for value in (-2, 0, 1, 3):
            self.assertEqual(witness(q(value)), q(transform(value)))
        relation = next(row for row in self.data['relations'] if row['id'] == 'REL-09')
        self.assertIn(r'\exists!', relation['law_tex'])
        self.assertIn(r'\overline T:Y\to Y', relation['law_tex'])


if __name__ == '__main__':
    unittest.main()
