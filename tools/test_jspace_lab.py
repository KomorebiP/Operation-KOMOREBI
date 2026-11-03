import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from build_reader_site import Site, site_navigation
from check_reader_site import Page, check_search_targets
from jspace_lab import APP_URL, RECORD_URL, APP_SHA256, APP_SIZE, SOURCE, build, verify
from reading_list import saveable
from browse_navigation import Browser


class JSpacePublicationTests(unittest.TestCase):
    def site(self, output, root=None):
        site = Site.__new__(Site)
        site.root = root or Path(__file__).resolve().parents[1]
        site.output = Path(output)
        site.search = []
        site.cache = None
        site.revision = '0'*40
        return site

    def test_real_instrument_is_copied_exactly_and_entry_is_accessible(self):
        with tempfile.TemporaryDirectory() as output:
            site = self.site(output)
            build(site)
            raw = (site.output/APP_URL).read_bytes()
            self.assertEqual(raw, (site.root/SOURCE).read_bytes())
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (APP_SIZE, APP_SHA256))
            page = Page((site.output/'j-lab.html').read_text(encoding='utf-8'))
            self.assertEqual((page.h1, page.main, page.navigation), (1, 1, 1))
            self.assertTrue(page.skip and page.title)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            self.assertEqual(len(page.iframes), 1)
            self.assertTrue(page.iframes[0]['title'])
            self.assertNotIn('src', page.iframes[0])  # No model download before launch.
            for control in page.inputs:
                self.assertTrue(control.get('id') in page.labels or control.get('aria-label'))
            self.assertNotIn('data-side-reader-link', (site.output/'j-lab.html').read_text(encoding='utf-8'))
            check_search_targets(site.search, {'j-lab.html': page})
            self.assertIn(APP_URL, page.links)
            self.assertEqual(verify(site.output)['source'], SOURCE)

    def test_modified_active_content_cannot_be_exempted_from_site_checks(self):
        with tempfile.TemporaryDirectory() as output:
            site = self.site(output)
            build(site)
            target = site.output/APP_URL
            raw = target.read_bytes()
            target.write_bytes(raw.replace(b'<script>', b'<script >', 1))
            with self.assertRaisesRegex(ValueError, 'differs from the preserved edition'):
                verify(site.output)

    def test_source_record_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as output:
            site = self.site(output)
            build(site)
            record = site.output/RECORD_URL
            data = json.loads(record.read_bytes())
            data['source'] = 'different.html'
            record.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'source record differs'):
                verify(site.output)

    def test_changed_source_receipt_requires_an_explicit_edition_review(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as output:
            root = Path(root)
            receipt = root/'manifests/source-imports/experiments-jspace-causal-lab.json'
            receipt.parent.mkdir(parents=True)
            receipt.write_text(json.dumps({'files': [{'path': SOURCE.rsplit('/',1)[1], 'size': APP_SIZE, 'sha256': '0'*64}]}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Review the J-Space edition'):
                build(self.site(output, root))
            self.assertFalse((Path(output)/APP_URL).exists())

    def test_entry_has_plain_navigation_download_and_failure_recovery_routes(self):
        with tempfile.TemporaryDirectory() as output:
            site = self.site(output)
            build(site)
            source = (site.output/'j-lab.html').read_text(encoding='utf-8')
            self.assertIn('<noscript>', source)
            self.assertIn('download="Komorebi_JSpace_Causal_Lab_v1_4.html"', source)
            self.assertTrue(saveable('j-lab.html'))
            for path in ('j-lab.html', 'read/index.html', 'interactive.html'):
                self.assertIn('j-lab.html', site_navigation(path))

    def test_work_page_regeneration_retains_the_live_lab_route(self):
        root = Path(__file__).resolve().parents[1]
        state = json.loads((root/'manifests/source-components.json').read_bytes())
        status = json.loads((root/'manifests/project-status.json').read_bytes())
        browser = Browser(root, state, status)
        component = next(c for c in browser.components if c['id'] == 'experiments-jspace-causal-lab')
        self.assertIn('https://KomorebiP.github.io/Operation-KOMOREBI/j-lab.html', browser.work_page(component))


if __name__ == '__main__':
    unittest.main()
