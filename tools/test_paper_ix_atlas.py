"""Source coverage, equations, original figures and two-way routes for Paper IX."""
import json
from pathlib import Path
import re
import tempfile
import unittest

from test_core_worked_atlases import publish
from paper_ix_atlas import ATLAS,SPEC,sections,SOURCE,REPORT,section_url,RECEIPTS
from reading_navigation import Navigation
from check_reader_site import Page

ROOT=Path(__file__).resolve().parents[1]


class PaperIXAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.output=Path(cls.temp.name)
        cls.reader,cls.documents,cls.pages=publish('paper-ix',cls.output,ATLAS)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def verify(self):return ATLAS.verify(self.output,self.documents,self.pages)

    def test_full_edition_and_manuscript_return_routes(self):
        result=self.verify()
        self.assertEqual((result['html_sections'],result['drawings'],result['source_tables']),(23,20,6))
        self.assertEqual(result['math_expressions'],278)
        self.assertEqual(result['return_links'],35)
        for number in range(1,24):
            page=self.pages[section_url(number)]
            self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
            self.assertEqual(len(page.ids),len(set(page.ids)))

    def test_eight_worked_examples_and_generated_newton_input_are_included(self):
        report=json.loads((self.output/REPORT).read_bytes())
        self.assertEqual([r['number'] for r in report['html_sections']],[*range(1,24)])
        self.assertEqual(sum(len(s['figures']) for s in SPEC['sections'][15:]),8)
        body=(self.output/section_url(19)).read_text(encoding='utf-8')
        self.assertIn('60511872',body)
        self.assertIn('Included exact Newton coefficients',body)
        self.assertEqual(report['inherited_readme_inventory'],dict(sections=15,figures=12,current=False))
        self.assertFalse(any(report[k] for k in ('new_proof_review','new_lean_execution','new_mathematical_example_execution','new_tex_build')))

    def test_every_residue_and_native_label_is_selectable(self):
        report=json.loads((self.output/REPORT).read_bytes())
        tables=report['figures']['residue_permutations']['tables']
        self.assertEqual([len(t['rows']) for t in tables],[128,128,8,32])
        for number in (10,16,18,20):
            markup=(self.output/section_url(number)).read_text(encoding='utf-8')
            self.assertIn('scope="row"',markup);self.assertIn('scope="col"',markup)
        self.assertEqual(len(report['figures']),20)
        self.assertTrue(all(f['receipt']['native_text'] for f in report['figures'].values()))

    def test_changed_formula_omitted_prose_and_wrong_reachable_route_are_rejected(self):
        path=self.output/section_url(5);original=path.read_bytes()
        for changed in [original.replace(b'v_2(k!)',b'v_2(k!)+1',1),original.replace(b'This statement combines two different proved bounds',b'Altered statement combines two different proved bounds',1)]:
            self.assertNotEqual(changed,original);path.write_bytes(changed)
            try:
                with self.assertRaises(AssertionError):self.verify()
            finally:path.write_bytes(original)
        path=self.output/REPORT;original=path.read_bytes();report=json.loads(original)
        report['manuscript_references']['19']=report['manuscript_references']['20'];path.write_text(json.dumps(report),encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):self.verify()
        finally:path.write_bytes(original)

    def test_missing_appendix_input_fails_closed(self):
        read=lambda path:(ROOT/path).read_bytes()
        def omitted(path):
            raw=read(path)
            return raw.replace(br'\input{worked_atlas.tex}',b'') if path==SOURCE else raw
        with self.assertRaisesRegex(ValueError,'input graph'):sections(omitted)

    def test_altered_data_table_and_incomplete_jump_menu_are_rejected(self):
        path=self.output/section_url(20);original=path.read_bytes()
        changed=original.replace(b'<td>175</td>',b'<td>174</td>',1)
        self.assertNotEqual(changed,original);path.write_bytes(changed)
        try:
            with self.assertRaises(AssertionError):self.verify()
        finally:path.write_bytes(original)
        changed=re.sub(rb'(<a data-reading-entry="23"[^>]+href=")[^"]+',rb'\1s22.html',original,count=1)
        self.assertNotEqual(changed,original);path.write_bytes(changed)
        try:
            with self.assertRaises(AssertionError):self.verify()
        finally:path.write_bytes(original)


if __name__=='__main__':unittest.main()
