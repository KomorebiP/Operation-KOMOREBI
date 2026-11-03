"""The full Paper X atlas must retain its scope contracts, labels and routes."""
import json
from pathlib import Path
import re
import tempfile
import unittest
from test_core_worked_atlases import publish
from paper_x_atlas import ATLAS,SPEC,opening_fragment
from worked_atlas_drawings import drawing_nodes

ROOT=Path(__file__).resolve().parents[1]


class PaperXAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.output=Path(cls.temp.name)
        cls.reader,cls.documents,cls.pages=publish('paper-x',cls.output,ATLAS)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def verify(self):return ATLAS.verify(self.output,self.documents,self.pages)

    def test_complete_edition_has_every_drawing_label_and_two_way_route(self):
        self.assertEqual(self.verify(),dict(total_plates=30,html_plates=30,drawings=29,transcribed_labels=754,math_expressions=969,return_links=50))
        for n in range(1,31):
            page=self.pages[ATLAS.plate_url(n)]
            self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
            self.assertEqual(len(page.ids),len(set(page.ids)))

    def test_opening_scope_contract_and_separate_outputs_are_retained(self):
        markup=(self.output/ATLAS.INDEX).read_text(encoding='utf-8')
        for text in ['The current reading contract','A checked scope and a later unpromoted scope',
                     '20/20 internal claims','19/20, no promoted endpoint','Zero multiplicity is allowed',
                     'Transported target family','Recovered carrier summand']:
            self.assertIn(text,markup)
        report=json.loads((self.output/ATLAS.REPORT).read_bytes())
        self.assertEqual(report['figures']['opening_contract']['pdf_page'],2)
        self.assertEqual(len(report['figures']['opening_contract']['nodes']),4)
        self.assertEqual(report['edition_checks']['pdf_page_offset'],3)
        self.assertFalse(any(report[k] for k in ('new_proof_review','new_lean_execution','new_mathematical_example_execution','new_tex_build')))

    def test_literal_word_node_is_not_treated_as_a_drawing_command(self):
        source=r'\node at (0,0) {Filled node: $+1$. Open node: $-1$.};'
        nodes=drawing_nodes(source)
        self.assertEqual(len(nodes),1);self.assertIn('Open node:',nodes[0]['text'])
        with self.assertRaisesRegex(ValueError,'drawing label'):
            drawing_nodes(source+r' node unsupported;')
        from readable_chapters import Chapter
        self.assertEqual(Chapter('',{}).inline(r'\textemdash'), '—')

    def test_adjacent_prose_is_excluded_by_original_pdf_object_extraction(self):
        self.assertEqual(SPEC['isolate_drawings'],{
            '11_chain_defect':dict(scale=1.18541,objects=104),
            '19_hypotheses':dict(scale=1.18541,objects=83),
            '22_norm_table':dict(scale=1.18541,objects=135)})
        report=json.loads((self.output/ATLAS.REPORT).read_bytes())
        for name,recipe in SPEC['isolate_drawings'].items():self.assertEqual(report['figures'][name]['isolated_drawing_objects'],recipe)

    def test_changed_equation_and_wrong_reachable_manuscript_target_are_rejected(self):
        path=self.output/ATLAS.plate_url(6);original=path.read_bytes()
        changed=original.replace(b'N(m)',b'N(m)+1',1);self.assertNotEqual(changed,original);path.write_bytes(changed)
        try:
            with self.assertRaises(AssertionError):self.verify()
        finally:path.write_bytes(original)
        path=self.output/ATLAS.REPORT;original=path.read_bytes();report=json.loads(original)
        report['manuscript_references']['6']=report['manuscript_references']['19'];path.write_text(json.dumps(report),encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):self.verify()
        finally:path.write_bytes(original)

    def test_omitting_opening_scope_or_changing_its_contract_is_rejected(self):
        path=self.output/ATLAS.INDEX;original=path.read_bytes()
        for changed in [original.replace(b'20/20 internal claims',b'20/20 unconditional claims',1),original.replace(b'A checked scope and a later unpromoted scope',b'Omitted scope notice',1)]:
            self.assertNotEqual(changed,original);path.write_bytes(changed)
            try:
                with self.assertRaises(AssertionError):self.verify()
            finally:path.write_bytes(original)
        source=(ROOT/ATLAS.DEFINITIONS).read_text(encoding='utf-8-sig')
        with self.assertRaisesRegex(ValueError,'opening scopes'):
            opening_fragment(source.replace('A checked scope and a later unpromoted scope','Changed heading',1))

    def test_conditional_ledger_wording_is_checked_even_without_equations(self):
        path=self.output/ATLAS.plate_url(30);original=path.read_bytes()
        changed=original.replace(b'amended conditional occupied-system assembly',b'unconditional occupied-system assembly',1)
        self.assertNotEqual(changed,original);path.write_bytes(changed)
        try:
            with self.assertRaises(AssertionError):self.verify()
        finally:path.write_bytes(original)


if __name__=='__main__':unittest.main()
