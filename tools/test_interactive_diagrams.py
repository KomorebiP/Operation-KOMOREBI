"""Exercise the new page through the shared renderer and access/link checker."""
from pathlib import Path
import hashlib
import tempfile
import unittest
from urllib.parse import urlsplit

from build_reader_site import Site
from check_reader_site import Page, check_search_targets
from interactive_diagrams import build


class InteractivePageTests(unittest.TestCase):
    def test_rendered_page_satisfies_reader_structure_and_control_labels(self):
        with tempfile.TemporaryDirectory() as output:
            site = Site.__new__(Site)
            site.root = Path(__file__).resolve().parents[1]
            site.output = Path(output)
            site.search = []
            build(site)
            page = Page((site.output/'interactive.html').read_text(encoding='utf-8'))
            self.assertEqual((page.h1, page.main, page.navigation), (1,1,1))
            self.assertTrue(page.skip and page.title)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            for control in page.inputs:
                self.assertTrue(control.get('id') in page.labels or control.get('aria-label'), control)
            check_search_targets(site.search, {'interactive.html':page})
            for target in page.links:
                path = urlsplit(target).path
                if path.startswith('assets/interactive-'):
                    self.assertTrue((site.root/'website'/path).is_file(), target)
            self.assertEqual({entry['url'] for entry in site.search},
                             {'interactive.html#packets','interactive.html#refinement','interactive.html#recovery','interactive.html#haar'})
            script = (site.output/'assets/interactive-diagrams.js').read_text(encoding='utf-8')
            for module in ('core', 'state'):
                filename = 'interactive-diagrams-'+module+'.mjs'
                version = hashlib.sha256((site.root/'website/assets'/filename).read_bytes()).hexdigest()[:12]
                self.assertIn("'./"+filename+"?v="+version+"'", script)
            expected = hashlib.sha256(script.encode('utf-8')).hexdigest()[:12]
            self.assertIn('assets/interactive-diagrams.js?v='+expected, page.links)


if __name__ == '__main__':
    unittest.main()
