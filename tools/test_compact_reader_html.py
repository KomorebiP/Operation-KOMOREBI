"""Check that publication compaction preserves HTML semantics and retained bytes."""
from pathlib import Path
import tempfile
import unittest

from compact_reader_html import PageTokens, compact_html, compact_tree


class CompactReaderTests(unittest.TestCase):
    def test_tags_attributes_entities_and_source_text_round_trip(self):
        text = ('<!doctype html><html lang="en"><head><title>A &amp; B</title></head>'
                '<body><svg viewBox="0 0 5 5"><path fill="none" d="M0 0L5 5"/></svg>'
                '<a href="path#L2" title="x href=\'y\'" data-value="&quot;&amp;&#39;">α</a>'
                '<pre class="source-lines"><code>\t"quoted" \'x\' &lt;tag&gt;\n</code></pre>'
                '<!-- retained comment --></body></html>')
        result = compact_html(text)
        self.assertLess(len(result), len(text))
        self.assertEqual(PageTokens(text).tokens, PageTokens(result).tokens)
        self.assertIn('viewBox="0 0 5 5"', result)
        self.assertIn('title="x href=\'y\'"', result)
        self.assertIn('\t"quoted" \'x\' &lt;tag&gt;\n', result)
        self.assertEqual(compact_html(result), result)

    def test_scripts_and_attribute_like_strings_are_not_rewritten(self):
        text = ('<script type="application/json">{"markup":"<a class=\"x\">"}</script>'
                '<style>.x::before{content:\'href="a"\'}</style>')
        result = compact_html(text)
        self.assertEqual(PageTokens(text).tokens, PageTokens(result).tokens)
        self.assertIn('{"markup":"<a class=\"x\">"}', result)
        self.assertIn('content:\'href="a"\'', result)

    def test_self_closing_values_keep_their_original_meaning(self):
        for text in ('<input value="x"/>', '<input value="x" />',
                     '<br class="x"/>', '<a data-x="x=y" href="/a?x=y&amp;z=2">x</a>'):
            self.assertEqual(PageTokens(text).tokens, PageTokens(compact_html(text)).tokens)

    def test_multiline_attributes_unicode_and_crlf_positions(self):
        text = '<html lang="en">\r\n<a\r\n id="α" class="x"\n href="/a#b">β</a></html>'
        result = compact_html(text)
        self.assertEqual(PageTokens(text).tokens, PageTokens(result).tokens)
        self.assertIn('id="α" class=x', result)
        self.assertEqual(result.count('\r\n'), text.count('\r\n'))

    def test_only_generated_pages_are_compacted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = ['index.html', 'read/work/source.html', 'assets/vendor/viewer.html',
                     'documents/files/hash/original.html', 'downloads/original.html']
            raw = b'<p class="example">same text</p>'
            for relative in paths:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            result = compact_tree(root)
            self.assertEqual(result, dict(files=2, saved_bytes=4, parsed_contents_preserved=True))
            for relative in paths[2:]:
                self.assertEqual((root / relative).read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
