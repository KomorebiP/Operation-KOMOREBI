"""Source fidelity and failure checks for the archived Smith chart reading."""
from pathlib import Path
from html.parser import HTMLParser
import re
import shutil
import tempfile
import unittest

import smith_chart_research as research

ROOT = Path(__file__).resolve().parents[1]
REVISION = 'a' * 40


def manuscript_text(source):
    class Extractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.inside = False
            self.parts = []
        def handle_starttag(self, tag, attrs):
            if tag == 'article' and dict(attrs).get('id') == 'manuscript':
                self.inside = True
        def handle_endtag(self, tag):
            if tag == 'article' and self.inside:
                self.inside = False
        def handle_data(self, data):
            if self.inside:
                self.parts.append(data)
    parser = Extractor()
    parser.feed(source)
    return ''.join(parser.parts)


class ResearchReadingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = research.archive_contents(ROOT)
        cls.original = cls.files[research.HTML_NAME].decode('utf-8').split('<main class="page">', 1)[1].split('</main>', 1)[0]
        cls.rendered = research.reading_body(ROOT, REVISION)

    def test_mathematical_text_figures_and_tables_survive(self):
        self.assertEqual(manuscript_text(self.original), manuscript_text(self.rendered))
        original_math = re.findall(r'<span class="math (?:inline|display)">.*?</span>', self.original, re.S)
        rendered_math = re.findall(r'<span class="math (?:inline|display) arithmatex">.*?</span>', self.rendered, re.S)
        self.assertEqual(len(original_math), 1668)
        self.assertEqual(original_math, [item.replace(' arithmatex"', '"', 1) for item in rendered_math])
        for tag in ('h1', 'h2', 'h3', 'figcaption', 'table'):
            original = re.findall(r'<'+tag+r'\b[^>]*>.*?</'+tag+r'>', self.original, re.S)
            rendered = re.findall(r'<'+tag+r'\b[^>]*>.*?</'+tag+r'>', self.rendered, re.S)
            # Tables and captions include math spans, whose only change is their renderer class.
            self.assertEqual(original, [x.replace(' arithmatex"', '"') for x in rendered], tag)
        self.assertEqual(self.rendered.count('class="research-figure"'), 42)
        self.assertEqual(len(re.findall(r'<table\b', self.rendered)), 23)
        self.assertNotIn('="data:', self.rendered)

    def test_every_internal_route_resolves(self):
        ids = set(re.findall(r'\bid="([^"]+)"', self.rendered))
        targets = re.findall(r'\bhref="#([^"]+)"', self.rendered)
        self.assertFalse(set(targets) - ids)
        self.assertIn('seven-reactive-exact', ids)
        self.assertIn('arbitrary-order-separation', ids)
        self.assertIn('verification-register-and-reproducible-records', ids)

    def test_source_links_are_revision_bound_and_claim_scope_is_visible(self):
        links = re.findall(r'(?:src|href)="(https://raw\.githubusercontent\.com/[^"]+)"', self.rendered)
        self.assertEqual(len(links), 45)  # 42 figures and three downloads
        self.assertTrue(all('/'+REVISION+'/' in link for link in links))
        self.assertIn(research.ARCHIVE_SHA256, self.rendered)
        self.assertIn('six-reactive realization using an ideal transformer', self.rendered)
        self.assertIn('transformer-free RLC-only realization with six reactive elements remains open', self.rendered)
        self.assertIn('not this entire draft', self.rendered)
        with self.assertRaises(ValueError):
            research.reading_body(ROOT, 'main')

    def test_tampered_figure_and_archive_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT/'research/smith-chart', root/'research/smith-chart')
            figure = next((root/'research/smith-chart/figures').glob('*'))
            figure.write_bytes(figure.read_bytes()+b'tampered')
            with self.assertRaisesRegex(ValueError, 'Published source differs'):
                research.archive_contents(root)
            shutil.copy2(ROOT/'research/smith-chart'/figure.relative_to(root/'research/smith-chart'), figure)
            archive = root/research.ARCHIVE
            archive.write_bytes(archive.read_bytes()+b'tampered')
            with self.assertRaisesRegex(ValueError, 'archive checksum mismatch'):
                research.archive_contents(root)


if __name__ == '__main__':
    unittest.main()
