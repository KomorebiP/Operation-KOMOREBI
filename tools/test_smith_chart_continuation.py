"""Failure, source-fidelity and link checks for the Smith/RLC continuation."""
from pathlib import Path
import hashlib
import json
import posixpath
import re
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from urllib.parse import unquote, urlsplit

import smith_chart_continuation as continuation

ROOT = Path(__file__).resolve().parents[1]


class TestSite:
    revision = 'a' * 40
    root = ROOT

    def __init__(self, output):
        self.output = Path(output)
        self.search = []
        self.pages = {}

    def rel(self, target, page):
        return posixpath.relpath(target, posixpath.dirname(page))

    def page(self, page, title, body, source):
        self.pages[page] = body
        target = self.output / page
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding='utf-8')


class SmithContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.files = continuation.load(ROOT)

    def test_authored_inventory_and_current_claim_distinctions(self):
        self.assertEqual(len(self.manifest['archives']), 5)
        self.assertEqual(len(self.manifest['chapters']), 6)
        hub = (ROOT / continuation.BASE / 'READING.md').read_text(encoding='utf-8')
        for token in ('reactive minimum is exactly six', 'at most four', 'positive real Laplace samples',
                      'independent or formal audit', 'eleven standard-library tasks', 'same component variables'):
            self.assertIn(token, hub)
        for members in self.files.values():
            self.assertFalse(any(name.lower().endswith('.pdf') for name in members))

    def test_archive_and_chapter_tampering_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / continuation.BASE, root / continuation.BASE)
            manifest_path = root / continuation.BASE / 'manifest.json'
            manifest = json.loads(manifest_path.read_bytes())
            manifest['chapters'][0]['source_sha256'] = '0' * 64
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'chapter checksum mismatch'):
                continuation.load(root)
            shutil.copyfile(ROOT / continuation.BASE / 'manifest.json', manifest_path)
            archive = root / continuation.BASE / 'archives' / next(iter(manifest['archives']))
            archive.write_bytes(archive.read_bytes() + b'tampered')
            with self.assertRaisesRegex(ValueError, 'archive checksum mismatch'):
                continuation.load(root)

    def test_all_mathematical_spans_survive_source_rendering(self):
        site = TestSite(Path('.'))
        spans = 0
        for chapter in self.manifest['chapters']:
            original = continuation.render(self.files[chapter['archive']][chapter['member']].decode('utf-8'))
            actual = continuation.chapter_body(site, self.manifest, self.files, chapter)
            pattern = r'<(?:span|div) class="arithmatex"[^>]*>(.*?)</(?:span|div)>'
            expected = re.findall(pattern, original, re.S)
            self.assertEqual(expected, re.findall(pattern, actual, re.S), chapter['slug'])
            spans += len(expected)
            self.assertEqual(len(re.findall('<h1\\b', actual)), 1)
            self.assertIn(chapter['status'], actual)
            self.assertIn('Original Markdown', actual)
            self.assertIn('no outside peer review or Lean proof', actual)
        self.assertGreater(spans, 150)

    def test_published_sources_match_archive_bytes_and_every_chapter_link_resolves(self):
        with tempfile.TemporaryDirectory() as directory:
            site = TestSite(directory)
            continuation.publish(site)
            self.assertEqual(len(site.pages), 7)
            self.assertEqual(len(site.search), 7)
            for archive, members in self.files.items():
                prefix = site.output / continuation.source_directory(self.manifest, archive)
                for member, raw in members.items():
                    self.assertEqual((prefix / member).read_bytes(), raw)
            shared = {'read/smith-chart/research.html', 'smith-chart.html', 'collection/demonstrations/SMITH_CHART.html', 'assets/smith-research.css'}
            for page, body in site.pages.items():
                ids = re.findall(r'\bid="([^"]+)"', body)
                self.assertEqual(len(ids), len(set(ids)), page)
                for target in re.findall(r'(?:href|src)="([^"]+)"', body):
                    parts = urlsplit(target)
                    if parts.scheme or parts.netloc:
                        continue
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(page), unquote(parts.path))) if parts.path else page
                    self.assertTrue(resolved in shared or (site.output / resolved).is_file(), (page, target))
                    if parts.fragment and resolved in site.pages:
                        self.assertIn('id="' + unquote(parts.fragment) + '"', site.pages[resolved], (page, target))

    def test_unresolved_source_link_is_an_error(self):
        chapter = self.manifest['chapters'][0]
        files = {name: dict(members) for name, members in self.files.items()}
        files[chapter['archive']][chapter['member']] += b'\n[Missing](missing.md)\n'
        with self.assertRaisesRegex(ValueError, 'Unresolved Smith continuation source link'):
            continuation.chapter_body(TestSite(Path('.')), self.manifest, files, chapter)

    def test_fresh_replay_is_scoped_and_preserves_inherited_sources(self):
        report = json.loads((ROOT / continuation.BASE / 'verification/portable-windows/summary.json').read_bytes())
        self.assertEqual(report['tasks'], 11)
        self.assertEqual(report['passed'], 11)
        self.assertTrue(report['all_original_sources_unchanged'])
        self.assertTrue(all(row['standard_library_only'] and row['source_unchanged'] for row in report['results']))
        for row in report['results']:
            self.assertTrue((ROOT / continuation.BASE / 'verification/portable-windows' / row['log']).is_file())


if __name__ == '__main__':
    unittest.main()
