"""Check the published recovery page and independently verify its exact model."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit

from audit_recovery_lab import audit
from build_reader_site import Site
from check_reader_site import Page, check_search_targets
from recovery_lab import build


class RecoveryLaboratoryTests(unittest.TestCase):
    def test_scoped_line_endings_preserve_the_existing_euler_publication(self):
        root = Path(__file__).resolve().parents[1]
        record = json.loads((root/'manifests/euler-packets-worked-example-2026-10-29.json').read_bytes())
        entry = next(item for item in record['files'] if item['path'] == '.gitattributes')
        self.assertEqual(hashlib.sha256((root/'.gitattributes').read_bytes()).hexdigest(), entry['sha256'])
        paths = ['website/assets/recovery-lab-core.mjs', 'tools/audit_recovery_lab.py',
                 'verification/recovery-lab/run-2026-11-03/manifest.json']
        output = subprocess.check_output([shutil.which('git') or 'git', 'check-attr', 'text', 'eol', 'whitespace', '--', *paths],
                                         cwd=root, text=True, encoding='utf-8')
        attributes = {}
        for line in output.splitlines():
            path, attribute, value = line.split(': ', 2)
            attributes[path, attribute] = value
        for path in paths[:2]:
            self.assertEqual(attributes[path, 'text'], 'set')
            self.assertEqual(attributes[path, 'eol'], 'lf')
        self.assertEqual(attributes[paths[2], 'text'], 'unset')
        self.assertEqual(attributes[paths[2], 'eol'], 'unspecified')
        self.assertEqual(attributes[paths[2], 'whitespace'], 'unset')

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
            guidance = (site.output/'assets/recovery-lab-guidance.mjs').read_text(encoding='utf-8')
            self.assertIn("'./recovery-lab-guidance.mjs?v="+hashlib.sha256(guidance.encode()).hexdigest()[:12]+"'", script)
            self.assertIn("'./recovery-lab-core.mjs?v="+hashlib.sha256(model).hexdigest()[:12]+"'", guidance)
            for description in ('rl-motion-help', 'rl-fiber-description', 'rl-response-description'):
                self.assertIn(description, page.ids)
            self.assertIn('Read all nine graph samples as exact values', source)
            self.assertIn('aria-describedby="rl-response-description"', source)
            self.assertNotIn('id="rl-certificate" aria-live=', source)


if __name__ == '__main__':
    unittest.main()
