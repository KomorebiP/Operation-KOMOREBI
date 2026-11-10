"""Test the public page and independently check the finite mathematical model."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from audit_special_functions_lab import audit
from build_reader_site import Site
from check_reader_site import Page, check_search_targets
from special_functions_lab import build


class SpecialFunctionsLaboratoryTests(unittest.TestCase):
    def test_exact_browser_model_against_dense_fraction_oracle(self):
        result=audit()
        self.assertEqual(result['status'],'passed')
        self.assertEqual(result['parameter_cases'],85)
        self.assertGreater(result['assertions'],2000)

    def test_page_labels_bounds_sources_and_versioned_assets(self):
        with tempfile.TemporaryDirectory() as output:
            site=Site.__new__(Site)
            site.root=Path(__file__).resolve().parents[1]
            site.output=Path(output);site.search=[]
            build(site)
            source=(site.output/'special-functions-lab.html').read_text(encoding='utf-8')
            page=Page(source)
            self.assertEqual((page.h1,page.main,page.navigation),(1,1,1))
            self.assertTrue(page.skip and page.title)
            self.assertEqual(len(page.ids),len(set(page.ids)))
            for control in page.inputs:
                self.assertTrue(control.get('id') in page.labels or control.get('aria-label'),control)
            check_search_targets(site.search,{'special-functions-lab.html':page})
            script=(site.output/'assets/special-functions-lab.js').read_text(encoding='utf-8')
            core=(site.root/'website/assets/special-functions-lab-core.mjs').read_bytes()
            self.assertIn("'./special-functions-lab-core.mjs?v="+hashlib.sha256(core).hexdigest()[:12]+"'",script)
            self.assertIn('assets/special-functions-lab.js?v='+hashlib.sha256(script.encode()).hexdigest()[:12],page.links)
            self.assertIn('additional floating-point roundoff',source)
            self.assertIn('read/monographs-special-functions/coupled-contractions.html',page.links)
            self.assertIn('aria-describedby="sf-plot-description"',source)
            self.assertIn('sf-terms',page.ids)
            self.assertEqual(source.count('class="sf-equations arithmatex"'),3)


if __name__=='__main__':
    unittest.main()
