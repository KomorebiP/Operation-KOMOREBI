from pathlib import Path
import hashlib
import tempfile
import unittest
from urllib.parse import urlsplit

from build_reader_site import Site
from check_reader_site import Page, check_search_targets
from signal_lab import build


class SignalLaboratoryTests(unittest.TestCase):
    def test_page_controls_search_and_versioned_model_are_published(self):
        with tempfile.TemporaryDirectory() as output:
            site = Site.__new__(Site)
            site.root = Path(__file__).resolve().parents[1]
            site.output = Path(output)
            site.search = []
            build(site)
            source = (site.output/'signal-lab.html').read_text(encoding='utf-8')
            page = Page(source)
            self.assertEqual((page.h1, page.main, page.navigation), (1, 1, 1))
            self.assertTrue(page.skip and page.title)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            for control in page.inputs:
                self.assertTrue(control.get('id') in page.labels or control.get('aria-label'), control)
            check_search_targets(site.search, {'signal-lab.html': page})
            self.assertNotIn('data-side-reader-link', source)
            for link in page.links:
                path = urlsplit(link).path
                if path.startswith(('assets/signal-lab', 'assets/interactive-diagrams')):
                    self.assertTrue((site.root/'website'/path).is_file(), link)
            script = (site.output/'assets/signal-lab.js').read_text(encoding='utf-8')
            model = site.root/'website/assets/signal-lab-core.mjs'
            version = hashlib.sha256(model.read_bytes()).hexdigest()[:12]
            self.assertIn("'./signal-lab-core.mjs?v="+version+"'", script)
            workspace = (site.output/'assets/signal-lab-workspace.mjs').read_text(encoding='utf-8')
            self.assertIn("'./signal-lab-core.mjs?v="+version+"'", workspace)
            self.assertIn("'./signal-lab-workspace.mjs?v="+hashlib.sha256(workspace.encode()).hexdigest()[:12]+"'", script)
            version = hashlib.sha256(script.encode()).hexdigest()[:12]
            self.assertIn('assets/signal-lab.js?v='+version, page.links)


if __name__ == '__main__':
    unittest.main()
