"""Keep lookup entries identical to the maintained reference and its anchors."""
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest

from glossary_reader import glossary_lookup, glossary_return_links, glossary_search_text
from reader_experience import glossary_prose, load, render_glossary


class PlainText(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.parts = []
        self.feed(source)

    def handle_data(self, text):
        self.parts.append(text)


class LookupHTML(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.entries = []
        self.links = []
        self.elements = {}
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.elements[attrs['id']] = attrs
        if 'data-glossary-entry' in attrs:
            self.entries.append(attrs)
        if tag == 'a':
            self.links.append(attrs['href'])


class GlossaryLookupTests(unittest.TestCase):
    def test_every_maintained_definition_has_its_original_anchor(self):
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root/'manifests/reader-experience.json').read_bytes())
        result = LookupHTML(glossary_lookup(config))
        terms = sorted(config['glossary'], key=lambda t: t['term'].casefold())
        self.assertEqual(len(result.entries), len(terms))
        self.assertEqual(result.links, ['#'+t['id'] for t in terms])
        for entry, term in zip(result.entries, terms):
            self.assertEqual(entry['data-term'], term['term'])
            self.assertEqual(entry['data-subject'], term['section'])
            self.assertIn(term['definition'], entry['data-search'])
            if term.get('note'):
                self.assertIn(term['note'], entry['data-search'])
            self.assertEqual(entry['data-aliases'].splitlines(), term.get('aliases', []))
            for alias in term.get('aliases', []):
                self.assertIn(alias, entry['data-search'])
            if term.get('example_text'):
                self.assertIn(term['example_text'], entry['data-search'])
            if term.get('quick_example'):
                self.assertIn(term['quick_example'], entry['data-search'])
            self.assertGreaterEqual(len(term['explanation']), 2, term['id'])
            for paragraph in term['explanation']:
                self.assertIn(paragraph, entry['data-search'])
            self.assertEqual(entry['data-search'], glossary_search_text(term))
        reference = render_glossary(config)
        self.assertEqual((root/'docs/GLOSSARY.md').read_text(encoding='utf-8'), reference)
        for term in terms:
            self.assertIn('<a id="'+term['id']+'"></a>', reference)
            self.assertIn(glossary_prose(term['definition']), reference)
            for paragraph in term['explanation']:
                self.assertIn(glossary_prose(paragraph), reference)
            if term.get('aliases'):
                self.assertIn('**Also called:** '+', '.join(term['aliases']), reference)
            if term.get('example_text'):
                self.assertIn('**In the worked example:** '+glossary_prose(term['example_text']), reference)
            if term.get('quick_example'):
                self.assertIn('**Quick example:** '+glossary_prose(term['quick_example']), reference)
        self.assertIn('hidden', result.elements['glossary-form'])
        self.assertIn('hidden', result.elements['glossary-matches'])
        self.assertEqual(result.elements['glossary-status']['role'], 'status')

    def test_reading_routes_and_letter_groups_link_to_existing_anchors(self):
        import re
        from navigation_links import anchors, inline_targets
        root = Path(__file__).resolve().parents[1]
        config = load(root)
        reference = render_glossary(config)
        identifiers = anchors(reference)
        local = [target[1:] for target in inline_targets(reference) if target.startswith('#')]
        self.assertTrue(set(local) <= identifiers)
        for step in config['glossary_start']:
            for key in step['terms']:
                self.assertIn(key, identifiers)
        for comparison in config['glossary_comparisons']:
            self.assertEqual(len(comparison['terms']), 2)
            self.assertTrue(set(comparison['terms']) <= identifiers)
        for route in config['glossary_routes']:
            self.assertIn('route-'+route['id'], identifiers)
            self.assertTrue(set(route['terms']) <= identifiers)
            self.assertIn(']('+route['reading']+')', reference)
            self.assertTrue((root/'docs'/route['reading']).is_file())
        index = reference.split('## Alphabetical index\n', 1)[1]
        self.assertEqual(set(re.findall(r'\]\(#([^)]*)\)', index)) - identifiers, set())
        for term in config['glossary']:
            self.assertEqual(index.count('](#'+term['id']+')'), 1)
            self.assertIn('id="index-'+term['term'][0].lower()+'"', index)

    def test_return_links_preserve_the_complete_rendered_reference(self):
        try:
            import markdown
        except ModuleNotFoundError:
            self.skipTest('Rendered glossary checks require the website Markdown dependency; the Reader website workflow installs it.')
        from build_reader_site import Rewriter, slugify
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root/'manifests/reader-experience.json').read_bytes())
        reference = render_glossary(config)
        rendered = markdown.markdown(reference, extensions=['tables', 'toc'], extension_configs={'toc':{'slugify':slugify}})
        rewrite = Rewriter(lambda target, image: target)
        rewrite.feed(rendered)
        original = ''.join(rewrite.out)
        import re
        for term in config['glossary']:
            marker = '<p><a id="'+term['id']+'"></a></p>'
            entry = original.split(marker, 1)[1]
            entry = re.split(r'<p><a id=|<h2\b', entry, maxsplit=1)[0]
            plain = ''.join(PlainText(entry).parts)
            for paragraph in term['explanation']:
                self.assertIn(paragraph, plain, (term['id'], 'Explanation changed in rendering'))
            for key in ('definition', 'quick_example', 'example_text', 'note'):
                if term.get(key):
                    self.assertIn(term[key], plain, (term['id'], key, 'Markdown changed the maintained text'))
        enhanced = glossary_return_links(original, config)
        return_link = '<p class="glossary-return"><a href="#glossary-lookup">Back to glossary lookup</a></p>'
        self.assertEqual(enhanced.count(return_link), len(config['glossary']))
        self.assertEqual(enhanced.replace(return_link, ''), original, 'Only return links are added to the full reference')
        with self.assertRaises(ValueError):
            glossary_return_links(original.replace('id="power-series"', 'id="missing"'), config)

    def test_untrusted_text_is_escaped_in_text_and_attributes(self):
        config = dict(glossary_sections=[dict(id='test',title='Test & examples')],
                      glossary=[dict(id='sample',term='A "term" <test>',section='test',
                                     definition='x < y & y > z',note='Read "carefully".',
                                     aliases=['<alias> & "name"'],example_text='<example> & "value"',
                                     quick_example='<quick> & "illustration"')])
        config['glossary'][0]['explanation'] = ['An <explanation> with A*A and [brackets].', 'Second paragraph.']
        markup = glossary_lookup(config)
        self.assertNotIn('<test>', markup)
        self.assertNotIn('<alias>', markup)
        self.assertNotIn('<example>', markup)
        self.assertNotIn('<quick>', markup)
        self.assertNotIn('<explanation>', markup)
        parsed = LookupHTML(markup)
        self.assertEqual(parsed.entries[0]['data-term'], config['glossary'][0]['term'])
        self.assertIn('x < y & y > z', parsed.entries[0]['data-search'])
        self.assertEqual(parsed.entries[0]['data-aliases'], '<alias> & "name"')
        self.assertIn('<example> & "value"', parsed.entries[0]['data-search'])
        self.assertIn('<quick> & "illustration"', parsed.entries[0]['data-search'])
        for paragraph in config['glossary'][0]['explanation']:
            self.assertIn(paragraph, parsed.entries[0]['data-search'])
        self.assertEqual(parsed.links, ['#sample'])


if __name__ == '__main__':
    unittest.main()
