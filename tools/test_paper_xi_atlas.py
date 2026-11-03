"""Full lesson coverage, scope preservation, recorded data and two-way reading routes."""
import json
from pathlib import Path
import re
import tempfile
import unittest
from test_core_worked_atlases import publish
from paper_xi_atlas import ATLAS,SPEC,SOURCE,INDEX,REPORT,section_url,sections

ROOT=Path(__file__).resolve().parents[1]


class PaperXIAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.output=Path(cls.temp.name)
        cls.reader,cls.documents,cls.pages=publish('paper-xi',cls.output,ATLAS)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def verify(self):return ATLAS.verify(self.output,self.documents,self.pages)

    def test_complete_edition_and_return_routes(self):
        self.assertEqual(self.verify(),dict(total_sections=47,html_sections=47,drawings=23,source_tables=3,math_expressions=436,return_links=66,opening_routes=2))
        for n in range(1,48):
            page=self.pages[section_url(n)];self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0));self.assertEqual(len(page.ids),len(set(page.ids)))

    def test_opening_corrections_and_same_candidate_scope_survive(self):
        markup=(self.output/INDEX).read_text(encoding='utf-8')
        for phrase in ['Two visual routes, one claim map','Reading corrections without changing the contract','Theorem 16.2','not a claim that row 66','The equal-capacity example is conditional','No external peer review is claimed']:
            self.assertIn(phrase,markup)
        self.assertNotIn('komorebi.invalid',markup)
        self.assertEqual(len(self.pages[INDEX].ids),len(set(self.pages[INDEX].ids)))
        self.assertIn('H5 remains a conditional premise about the same independently constructed candidate',(self.output/section_url(44)).read_text(encoding='utf-8'))

    def test_recorded_tables_and_pdf_labels_are_selectable(self):
        record=json.loads((self.output/REPORT).read_bytes())
        self.assertTrue(all(f['receipt']['native_text'] for f in record['figures'].values()))
        capacity=record['figures']['18_capacity']['tables'][0]
        self.assertEqual(capacity['rows'][2],[3,8,6,6,8,8])
        self.assertEqual(capacity['rows'][4],[5,32,30,10,32768,32])
        self.assertIn('scope="row"',(self.output/section_url(31)).read_text(encoding='utf-8'))
        self.assertFalse(any(record[k] for k in ('new_proof_review','new_lean_execution','new_mathematical_example_execution','new_tex_build')))

    def test_omitted_scope_and_altered_table_fail_verification(self):
        for name,old,new in [(INDEX,b'The equal-capacity example is conditional',b'The equal-capacity example is unconditional'),(section_url(31),b'<td>32768</td>',b'<td>32767</td>'),(section_url(44),b'conditional premise',b'unconditional premise')]:
            path=self.output/name;raw=path.read_bytes();changed=raw.replace(old,new,1);self.assertNotEqual(raw,changed);path.write_bytes(changed)
            try:
                with self.assertRaises(AssertionError):self.verify()
            finally:path.write_bytes(raw)

    def test_wrong_reachable_target_and_missing_input_fail_verification(self):
        path=self.output/REPORT;raw=path.read_bytes();record=json.loads(raw);record['manuscript_references']['31']=record['manuscript_references']['3'];path.write_text(json.dumps(record),encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):self.verify()
        finally:path.write_bytes(raw)
        def read(path):
            raw=(ROOT/path).read_bytes();return raw.replace(br'\input{reader_route}',b'') if path==SOURCE else raw
        with self.assertRaisesRegex(ValueError,'input graph'):sections(read)


if __name__=='__main__':unittest.main()
