"""Focused navigation and assurance-boundary checks; no Lean execution."""
import hashlib
import json
from pathlib import Path
import posixpath
import re
import unittest
from unittest.mock import patch

import machine_native_reasoning_scope as scope

ROOT = Path(__file__).resolve().parents[1]


class LocalSite:
    def __init__(self):
        self.root = ROOT
        self.overrides = {}
        self.pages = {}
        self.search = []

    def read_source(self, record):
        path = record['repository_path']
        return self.overrides.get(path, (ROOT/path).read_bytes())

    @staticmethod
    def rel(target, page):
        return posixpath.relpath(target, posixpath.dirname(page))

    def page(self, path, title, body):
        self.pages[path] = (title, body)


class LocalReader:
    def __init__(self):
        self.site = LocalSite()
        self.records = {}

    def add(self, path, title=None):
        if not (ROOT/path).is_file():
            return None
        if path not in self.records:
            raw = self.site.overrides.get(path, (ROOT/path).read_bytes())
            self.records[path] = dict(repository_path=path, title=title or path,
                url='source/'+path+'.html', sha256=hashlib.sha256(raw).hexdigest())
        return self.records[path]


def prepared_book(reader):
    import machine_native_reasoning_reading as reading
    # Figure generation has its own identity and rendering tests. These tests
    # exercise result/proof/declaration binding without rasterizing the PDFs.
    with patch('reader_figure_assets.prepare', return_value={}):
        return reading.prepare_book(reader, reading.BOOK)


class MachineNativeReasoningScopeTests(unittest.TestCase):
    def test_namespace_resolution_ignores_comments_and_prefixes(self):
        text = '''namespace A
/- namespace False
/- nested comment -/
end False -/
namespace B
noncomputable section
-- theorem fake : True := by trivial
 def label : String := "namespace False"
theorem ending : True := by trivial
endRank_should_not_pop_any_namespace
end
 theorem Factors.ending : True := by trivial
end B
end A
'''
        entries = scope.qualified_declarations(text)
        self.assertEqual([entry['qualified_name'] for entry in entries],
                         ['A.B.label', 'A.B.ending', 'A.B.Factors.ending'])
        self.assertEqual(entries[-1]['line'], 12)

    def test_current_registered_results_and_exact_lean_lines(self):
        reader = LocalReader()
        book = prepared_book(reader)
        data = scope.prepare_scope(reader, book)
        self.assertEqual(len(data['results']), 27)
        self.assertEqual(data['module_count'], 79)
        self.assertEqual(data['endpoint_count'], 174)
        self.assertEqual(sum(not item['lean_modules'] for item in data['results']), 9)
        for item in data['results']:
            self.assertRegex(item['statement_url'], r'\.html#L\d+')
            self.assertRegex(item['proof_url'], r'\.html#L\d+')
            self.assertTrue(item['endpoints'])
            for endpoint in item['endpoints']:
                line = (ROOT/endpoint['path']).read_text().splitlines()[endpoint['line']-1]
                self.assertRegex(line, r'\b(theorem|lemma|def|abbrev)\b')
                self.assertIn(endpoint['name'].split('.')[-1], line)

    def test_scope_preserves_authored_chapter_and_edition_boundaries(self):
        reader = LocalReader()
        book = prepared_book(reader)
        scope.publish_scope(reader, book)
        _, body = reader.site.pages[scope.PAGE]
        self.assertEqual(body.count('class="recorded-result-scope"'), 27)
        self.assertEqual(body.count('>Written statement</a>'), 27)
        self.assertEqual(body.count('>Written proof</a>'), 27)
        self.assertIn('source/formal_correspondence.tex.html', body)
        self.assertIn('A source correspondence is more specific than a shared theorem name.', body)
        self.assertIn('Earlier source-suite receipts retain their original provenance.', body)
        self.assertIn('41-page', body)
        self.assertIn('74-page', body)
        self.assertIn('older 23/27 map', body)
        self.assertIn('1,155-page', body)
        self.assertIn('no new Lean execution or mathematical review', body)
        self.assertNotIn('href="#r-occupancy"', body.split('id="formal-correspondence"',1)[1].split('</section>',1)[0])

    def test_unaccepted_record_fails_before_publishing(self):
        reader = LocalReader()
        admission = json.loads((ROOT/scope.ADMISSION).read_bytes())
        admission['status'] = 'FAIL'
        reader.site.overrides[scope.ADMISSION] = json.dumps(admission).encode()
        with self.assertRaisesRegex(ValueError, 'admission and publication binding'):
            prepared_book(reader)
        self.assertEqual(reader.site.pages, {})

    def test_missing_endpoint_and_written_proof_fail(self):
        reader = LocalReader()
        book = prepared_book(reader)
        book.pop('mnr_scope')
        mapping = json.loads((ROOT/scope.MAP).read_bytes())
        mapping[0]['lean_endpoints'][0] = 'Komorebi.MachineTheory.not_a_retained_declaration'
        reader.site.overrides[scope.MAP] = json.dumps(mapping).encode()
        with self.assertRaisesRegex(ValueError, 'Expected one.*Lean endpoint'):
            scope.prepare_scope(reader, book)
        reader.site.overrides.clear()
        selected = next(chapter for _,_,chapter in book['chapters'] if chapter.proof_pairs)
        selected.proof_pairs.clear()
        with self.assertRaisesRegex(ValueError, 'Missing paired.*written proof'):
            scope.prepare_scope(reader, book)

    def test_rendered_identity_cannot_drift_from_source_map(self):
        reader = LocalReader()
        book = prepared_book(reader)
        book.pop('mnr_scope')
        node = next(node for _,_,chapter in book['chapters'] for node in chapter.nodes
                    if 'r:factor' in node.get('labels', []))
        node['number'] = '99.1'
        with self.assertRaisesRegex(ValueError, 'statement identity changed'):
            scope.prepare_scope(reader, book)


if __name__ == '__main__':
    unittest.main()
