"""Check the published recovery page and independently verify its exact model."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlsplit

from audit_recovery_lab import audit
from build_reader_site import Site
from check_reader_site import Page, check_search_targets
from recovery_lab import build


class RecoveryLaboratoryTests(unittest.TestCase):
    def test_exact_model_against_independent_minor_and_fraction_oracle(self):
        report = audit()
        self.assertEqual(report['status'], 'passed')
        self.assertEqual(report['cases'], 1604)
        self.assertGreater(report['recovery_rules'], 0)
        self.assertGreater(report['obstruction_witnesses'], 0)

    def test_published_page_has_labels_search_and_versioned_assets(self):
        with tempfile.TemporaryDirectory() as output:
            site = Site.__new__(Site)
            site.root = Path(__file__).resolve().parents[1]
            site.output = Path(output)
            site.search = []
            build(site)
            source = (site.output/'recovery-lab.html').read_text(encoding='utf-8')
            page = Page(source)
            self.assertEqual((page.h1, page.main, page.navigation), (1, 1, 1))
            self.assertTrue(page.skip and page.title)
            self.assertNotIn('data-side-reader-link', source)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            for control in page.inputs:
                self.assertTrue(control.get('id') in page.labels or control.get('aria-label'), control)
            check_search_targets(site.search, {'recovery-lab.html': page})
            script = (site.output/'assets/recovery-lab.js').read_text(encoding='utf-8')
            model = (site.root/'website/assets/recovery-lab-core.mjs').read_bytes()
            self.assertIn("'./recovery-lab-core.mjs?v="+hashlib.sha256(model).hexdigest()[:12]+"'", script)
            self.assertIn('assets/recovery-lab.js?v='+hashlib.sha256(script.encode()).hexdigest()[:12], page.links)
            for target in page.links:
                path = urlsplit(target).path
                if path.startswith(('assets/recovery-', 'assets/interactive-')):
                    self.assertTrue((site.root/'website'/path).is_file(), target)
            self.assertIn('recovery-lab.html', source)


if __name__ == '__main__':
    unittest.main()
