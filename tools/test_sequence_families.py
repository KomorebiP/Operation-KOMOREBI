import hashlib
import unittest
from pathlib import Path
from sequence_generalized import family_definitions, source_manifest, catalogue as family_catalogue, links_for
from sequence_library import library_entries
from sequence_atlas import catalogue


class GeneralizedFamiliesTests(unittest.TestCase):
    def test_sources_are_bound_to_maintained_passages(self):
        sources = source_manifest()['sources']
        self.assertEqual(len(sources), 11)
        for source in sources:
            text = Path(source['path']).read_text(encoding='utf-8')
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), source['normalized_sha256'])
            self.assertTrue(source['headings'])
            for heading in source['headings']:
                self.assertLessEqual(heading['line'], len(text.splitlines()))
        definitions = family_definitions()
        self.assertEqual(len(definitions), 22)
        self.assertEqual(sum(bool(f['engine']) for f in definitions), 10)
        self.assertTrue(all(f['source'].startswith('https://github.com/') and '#L' in f['source'] for f in definitions))

    def test_family_memberships_do_not_change_integer_records(self):
        entries = library_entries(catalogue())
        data = family_catalogue(entries)
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


if __name__ == '__main__':
    unittest.main()
