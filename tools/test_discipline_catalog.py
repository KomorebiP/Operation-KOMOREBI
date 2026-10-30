"""Regressions for the editorial discipline and evidence catalogue."""
import copy
import json
from pathlib import Path
import unittest

from discipline_catalog import load_catalog, facet_records, render_works_catalog


class DisciplineCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.registry = json.loads((cls.root/'manifests/browse-resources.json').read_text())
        cls.status = json.loads((cls.root/'manifests/project-status.json').read_text())
        cls.assessments = {c['id']: c for c in cls.status['components']}
        cls.components = {c['id']: c for c in json.loads(
            (cls.root/'manifests/source-components.json').read_text())['components']}

    def test_complete_disjoint_primary_disciplines(self):
        data, subjects = load_catalog(self.root, self.registry, self.assessments)
        self.assertEqual(len(subjects), len(self.registry['components']))
        self.assertEqual(len(subjects), 90)
        counts = {key: sum(item['primary'] == key for item in subjects.values())
                  for key in data['disciplines']}
        self.assertEqual(counts, {'math': 53, 'cs': 29, 'physics': 6, 'other': 2})
        self.assertEqual(subjects['paper-i']['primary'], 'math')
        self.assertEqual(subjects['monographs-large-signal-model']['primary'], 'cs')
        self.assertEqual(subjects['monographs-physics']['primary'], 'physics')
        self.assertEqual(subjects['komorebi-methodology']['primary'], 'other')

    def test_facets_copy_assessments_without_inference(self):
        facets = facet_records(self.root, self.registry, self.assessments)
        for id, item in facets['works'].items():
            source = self.assessments[id]
            self.assertEqual(item['stage'], source['stage'])
            self.assertEqual(item['lean'], source['lean'])
            self.assertEqual(item['evidence'], source['confidence'])
        self.assertEqual(facets['works']['paper-xi']['lean'], self.assessments['paper-xi']['lean'])

    def test_html_links_both_work_and_status(self):
        page = render_works_catalog(self.root, self.registry, self.components,
                                    self.assessments, self.status)
        self.assertEqual(page.count('class="catalog-item"'), 90)
        self.assertEqual(page.count('class="catalog-section"'), 4)
        self.assertIn('collection/works/paper-xi.html', page)
        self.assertIn('collection/STATUS_CATALOG.html#paper-xi', page)
        for key in ('catalog-discipline','catalog-stage','catalog-lean','catalog-evidence',
                    'catalog-query', 'catalog-group'):
            self.assertIn('id="' + key + '"', page)
        self.assertIn('a completed reading edition need not prove', page.lower())

    def test_reject_missing_or_duplicate_primary_assignment(self):
        data, _ = load_catalog(self.root, self.registry, self.assessments)
        bad = copy.deepcopy(self.registry)
        bad['components'].append({'id': 'unknown-work'})
        with self.assertRaisesRegex(ValueError, 'cover each indexed primary work'):
            # The fixture must not accidentally accept a new unclassified work.
            load_catalog(self.root, bad, self.assessments)


if __name__ == '__main__':
    unittest.main()
