"""Keep lookup entries identical to the maintained reference and its anchors."""
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest

from glossary_reader import glossary_lookup, glossary_return_links
from reader_experience import render_glossary


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
        reference = render_glossary(config)
        self.assertEqual((root/'docs/GLOSSARY.md').read_text(encoding='utf-8'), reference)
        for term in terms:
            self.assertIn('<a id="'+term['id']+'"></a>', reference)
            self.assertIn(term['definition'], reference)
        import markdown
        from build_reader_site import Rewriter, slugify
        rendered = markdown.markdown(reference, extensions=['tables', 'toc'], extension_configs={'toc':{'slugify':slugify}})
        rewrite = Rewriter(lambda target, image: target)
        rewrite.feed(rendered)
        original = ''.join(rewrite.out)
        enhanced = glossary_return_links(original, config)
        return_link = '<p class="glossary-return"><a href="#glossary-lookup">Back to glossary lookup</a></p>'
        self.assertEqual(enhanced.count(return_link), len(terms))
        self.assertEqual(enhanced.replace(return_link, ''), original, 'Only return links are added to the full reference')
        with self.assertRaises(ValueError):
            glossary_return_links(original.replace('id="power-series"', 'id="missing"'), config)
        self.assertIn('hidden', result.elements['glossary-form'])
        self.assertIn('hidden', result.elements['glossary-matches'])
        self.assertEqual(result.elements['glossary-status']['role'], 'status')

    def test_untrusted_text_is_escaped_in_text_and_attributes(self):
        config = dict(glossary_sections=[dict(id='test',title='Test & examples')],
                      glossary=[dict(id='sample',term='A "term" <test>',section='test',
                                     definition='x < y & y > z',note='Read "carefully".')])
        markup = glossary_lookup(config)
        self.assertNotIn('<test>', markup)
        parsed = LookupHTML(markup)
        self.assertEqual(parsed.entries[0]['data-term'], config['glossary'][0]['term'])
        self.assertIn('x < y & y > z', parsed.entries[0]['data-search'])
        self.assertEqual(parsed.links, ['#sample'])


if __name__ == '__main__':
    unittest.main()
