"""Saved reading is a page enhancement, never a change to source mathematics."""
from pathlib import Path
import posixpath
import tempfile
from types import SimpleNamespace
import unittest

from build_reader_site import Site, site_navigation
from check_reader_site import Page
from reading_list import build, enhance


class ReadingListTests(unittest.TestCase):
    def test_saving_preserves_the_article_and_nested_paths(self):
        site = SimpleNamespace(rel=lambda target, page: posixpath.relpath(target, posixpath.dirname(page)))
        article = '<article id="chapter-text"><h2 id="lemma">A &amp; B</h2><p>\\(x^2\\)</p></article>'
        rendered = enhance(site, 'read/paper-i/chapter.html', 'A "quoted" title', '<h1>Chapter</h1>'+article)
        self.assertIn(article, rendered)
        self.assertIn('href="../../reading-list.html"', rendered)
        self.assertIn('data-page-title="A &quot;quoted&quot; title"', rendered)
        self.assertIn('data-reading-save', rendered)
        self.assertIn('aria-pressed="false"', rendered)
        self.assertEqual(enhance(site, 'index.html', 'Home', '<h1>Home</h1>'), '<h1>Home</h1>')

    def test_the_site_template_publishes_the_list_and_progressive_controls(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Site.__new__(Site)
            site.root = Path(__file__).resolve().parents[1]
            site.output = Path(temporary)
            build(site)
            site.page('collection/works/test.html', 'A work', '<h1>A work</h1><article><h2 id="scope">Scope</h2></article>')
            site.page('index.html', 'Home', '<h1>Home</h1>')
            listing = (site.output/'reading-list.html').read_text(encoding='utf-8')
            work = (site.output/'collection/works/test.html').read_text(encoding='utf-8')
            home = (site.output/'index.html').read_text(encoding='utf-8')
            parsed = Page(listing)
            self.assertEqual((parsed.h1, parsed.main), (1, 1))
            self.assertIn('reading-list.js?v=', listing)
            self.assertIn('reading-list.css?v=', listing)
            self.assertIn('data-reading-list hidden', listing)
            self.assertIn('<noscript>', listing)
            self.assertNotIn('data-reading-save', listing)
            self.assertIn('data-reading-save', work)
            self.assertIn('../../assets/reading-list.js?v=', work)
            self.assertNotIn('assets/reading-list.js', home)
            self.assertIn('href="../../reading-list.html"', site_navigation('read/paper-i/chapter.html'))


if __name__ == '__main__':
    unittest.main()
