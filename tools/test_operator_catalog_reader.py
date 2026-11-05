"""Check source-bound search, stable destinations, and progressive catalog markup."""
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
import posixpath
from types import SimpleNamespace
import unittest

from operator_catalog import INDEX_PATH, RELATIONS_PATH, entry_path, load_catalog
from operator_catalog_reader import (
    inline_html, lookup_html, page_url, script_tag, search_entries, search_text, source_work_ids,
)

ROOT = Path(__file__).resolve().parents[1]


class CatalogHTML(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.entries = []
        self.links = []
        self.elements = {}
        self.labels = set()
        self.tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if 'id' in attrs:
            if attrs['id'] in self.elements:
                raise AssertionError('Duplicate HTML id: ' + attrs['id'])
            self.elements[attrs['id']] = attrs
        if 'data-operator-entry' in attrs:
            self.entries.append(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href'))
        if tag == 'label':
            self.labels.add(attrs['for'])


def minimal_site():
    return SimpleNamespace(
        root=ROOT, repos={'collection': 'KomorebiP/Operation-KOMOREBI'},
        components={'paper-i': {'destination': 'papers/paper-i'},
                    'paper-iii': {'destination': 'papers/paper-iii'}},
        reader=SimpleNamespace(document_works=lambda repo, path:
                               ['paper-i'] if path == 'docs/demonstrations/PACKETS.md' else []),
        rel=lambda target, page: posixpath.relpath(target, posixpath.dirname(page) or '.'))


class OperatorCatalogReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(ROOT)

    def test_lookup_preserves_every_entry_and_reaches_real_anchors(self):
        from navigation_links import anchors
        page = page_url(INDEX_PATH)
        parsed = CatalogHTML(lookup_html(self.catalog, page))
        entries = sorted(self.catalog['operators'], key=lambda row: (row['name'].casefold(), row['id']))
        self.assertEqual(len(parsed.entries), len(entries))
        self.assertEqual(len(parsed.links), len(entries))
        family_anchors = {family['path']: anchors((ROOT / family['path']).read_text(encoding='utf-8'))
                          for family in self.catalog['families']}
        for rendered, entry, target in zip(parsed.entries, entries, parsed.links):
            source, _, anchor = entry_path(entry, self.catalog).partition('#')
            self.assertIn(anchor, family_anchors[source])
            expected = posixpath.relpath(page_url(source), posixpath.dirname(page)) + '#' + anchor
            self.assertEqual(target, expected)
            self.assertEqual(rendered['data-operator-id'], entry['id'])
            self.assertEqual(rendered['data-family'], entry['family_id'])
            self.assertEqual(int(rendered['data-checks']), len(entry['check_ids']))
            self.assertEqual(rendered['data-search'], search_text(entry, self.catalog))
            self.assertEqual(rendered['id'], 'operator-result-' + entry['id'].lower())
        self.assertEqual(parsed.labels, {'operator-catalog-query', 'operator-catalog-family', 'operator-catalog-checks'})
        for identifier in ('operator-catalog-form', 'operator-catalog-matches', 'operator-catalog-status'):
            self.assertIn('hidden', parsed.elements[identifier])
        self.assertEqual(parsed.elements['operator-catalog-status']['role'], 'status')
        self.assertEqual(parsed.elements['operator-catalog-status']['aria-live'], 'polite')
        self.assertIn('noscript', parsed.tags)

    def test_search_links_have_the_recorded_scope_and_formula(self):
        records = search_entries(minimal_site(), self.catalog)
        self.assertEqual(len(records), len(self.catalog['operators']) + len(self.catalog['relations']))
        self.assertEqual(len({row['url'] for row in records}), len(records))
        for record, entry in zip(records, self.catalog['operators']):
            self.assertEqual(record['url'], page_url(entry_path(entry, self.catalog)))
            self.assertEqual(record['math_preview'], entry['formula'][1:-1])
            self.assertIn(entry['scope'], record['preview'])
            self.assertEqual(record['kind'], 'Guides')
            self.assertNotIn('Lean', record['kind'])
            for source in entry['source_codes']:
                self.assertIn(self.catalog['sources'][source]['title'], record['text'])

    def test_relation_search_reaches_each_law_without_inferred_work_attribution(self):
        from navigation_links import anchors
        records = [row for row in search_entries(minimal_site(), self.catalog)
                   if row['url'].startswith(page_url(RELATIONS_PATH) + '#')]
        self.assertEqual(len(records), len(self.catalog['relations']))
        destinations = anchors((ROOT / RELATIONS_PATH).read_text(encoding='utf-8'))
        for record, relation in zip(records, self.catalog['relations']):
            with self.subTest(relation=relation['id']):
                self.assertEqual(record['url'], page_url(RELATIONS_PATH + '#' + relation['id'].lower()))
                self.assertIn(relation['id'].lower(), destinations)
                self.assertEqual(record['title'], relation['id'] + ' · ' + relation['name'])
                self.assertEqual(record['math_preview'], relation['law_tex'])
                self.assertIn(relation['assumptions'], record['preview'])
                preview = ''.join('$' + part['text'] + '$' if part['type'] == 'math' else part['text']
                                  for part in record['preview_parts'])
                self.assertEqual(preview, record['preview'])
                self.assertEqual((record['group'], record['kind'], record['work_ids']),
                                 ('Collection', 'Guides', []))
                self.assertIn(relation['id'].replace('-', ''), record['text'])
                self.assertIn('REL' + str(int(relation['id'].split('-')[1])), record['text'])
                for identifier in relation['operator_ids'] + relation['check_ids']:
                    self.assertIn(identifier, record['text'])

    def test_work_filters_follow_sources_without_guessing_from_family_names(self):
        site = minimal_site()
        catalog = {'sources': {
            'paper': {'url': 'https://github.com/KomorebiP/Operation-KOMOREBI/blob/abc/papers/paper-iii/current/main.tex'},
            'demo': {'url': 'https://github.com/KomorebiP/Operation-KOMOREBI/blob/abc/docs/demonstrations/PACKETS.md'},
            'other_repo': {'url': 'https://github.com/KomorebiP/komorebi-math/blob/abc/papers/paper-i/main.tex'},
            'neighbor': {'url': 'https://github.com/KomorebiP/Operation-KOMOREBI/blob/abc/papers/paper-iii-extra/main.tex'},
            'traversal': {'url': 'https://github.com/KomorebiP/Operation-KOMOREBI/blob/abc/papers/paper-i/../other.tex'},
        }}
        self.assertEqual(source_work_ids(site, {'source_codes': ['paper', 'demo']}, catalog), ['paper-i', 'paper-iii'])
        self.assertEqual(source_work_ids(site, {'source_codes': ['other_repo', 'neighbor', 'traversal']}, catalog), [])

    def test_plain_text_and_inline_math_cannot_create_active_markup(self):
        catalog = deepcopy(self.catalog)
        catalog['operators'] = [catalog['operators'][0]]
        entry = catalog['operators'][0]
        entry['name'] = 'A "name" <img src=x onerror=alert(1)>'
        entry['scope'] = 'Require $x<y$ and <script>alert(1)</script> as literal text.'
        parsed = CatalogHTML(lookup_html(catalog, page_url(INDEX_PATH)))
        self.assertNotIn('img', parsed.tags)
        self.assertNotIn('script', parsed.tags)
        self.assertEqual(parsed.entries[0]['data-name'], entry['name'])
        self.assertIn(entry['scope'], parsed.entries[0]['data-search'])
        self.assertEqual(inline_html('$x<y$'), '<span class="arithmatex">\\(x&lt;y\\)</span>')

    def test_builder_retains_static_family_index_and_adds_entry_search(self):
        from build_reader_site import Site, document_url
        site = minimal_site()
        site.documents = {('collection', INDEX_PATH): (ROOT / INDEX_PATH).read_text(encoding='utf-8')}
        site.revisions = {'collection': 'a' * 40}
        site.search = []
        output = {}
        site.page = lambda path, title, body, source: output.update({path: body})

        def resolve(repo, path, page, target, image=False):
            source, marker, fragment = target.partition('#')
            if '://' in source:
                return target
            source = posixpath.normpath(posixpath.join(posixpath.dirname(path), source)) if source else path
            return site.rel(document_url(repo, source), page) + marker + fragment

        site.resolve = resolve
        Site.markdown_pages(site)
        parsed = CatalogHTML(output[page_url(INDEX_PATH)])
        self.assertIn('operator-catalog-lookup', parsed.elements)
        self.assertIn('browse-by-family', parsed.elements)
        self.assertIn('alphabetical-entry-index', parsed.elements)
        self.assertEqual(len(parsed.entries), len(self.catalog['operators']))
        self.assertEqual(len(site.search), len(self.catalog['operators']) + len(self.catalog['relations']) + 1)
        self.assertEqual(sum('#op-' in row['url'] for row in site.search), len(self.catalog['operators']))
        self.assertEqual(sum('#rel-' in row['url'] for row in site.search), len(self.catalog['relations']))

    def test_enhancement_script_is_only_loaded_on_the_index(self):
        site = minimal_site()
        script = script_tag(site, page_url(INDEX_PATH))
        self.assertRegex(script, r'../../../assets/operator-catalog\.js\?v=[0-9a-f]{12}')
        self.assertIn('defer', script)
        for page in ('index.html', 'collection/OPERATOR_AUDIT.html', 'collection/operators/catalog/A_STRUCTURAL.html'):
            self.assertEqual(script_tag(site, page), '')


if __name__ == '__main__':
    unittest.main()
