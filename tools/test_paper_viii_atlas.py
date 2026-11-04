"""Complete Paper VIII edition, split sources, literal loops and crosswalk audit."""
import json
from pathlib import Path
import re
import tempfile
import unittest
from paper_viii_atlas import ATLAS
from paper_viii_atlas_drawings import drawing_nodes
from test_core_worked_atlases import publish

ROOT=Path(__file__).resolve().parents[1]


class PaperVIIIAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.output=Path(cls.temp.name)
        cls.reader,cls.documents,cls.pages=publish('paper-viii',cls.output,ATLAS)
        cls.report=json.loads((cls.output/ATLAS.REPORT).read_bytes())

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_complete_edition_passes_production_verifier(self):
        self.assertEqual(ATLAS.verify(self.output,self.documents,self.pages),dict(total_plates=32,html_plates=32,drawings=30,transcribed_labels=711,math_expressions=830,return_links=84))

    def test_every_label_and_both_source_inputs_are_preserved(self):
        self.assertEqual(set(self.report['source_inputs']),set(ATLAS.SOURCES)|set(ATLAS.EXTRAS))
        for name,figure in self.report['figures'].items():
            body=(self.output/ATLAS.plate_url(figure['plate'])).read_text(encoding='utf-8')
            self.assertEqual(body.count('id="drawing-label-'),len(figure['nodes']),name)
            self.assertEqual(sorted(figure['node_order']),list(range(len(figure['nodes']))),name)
        for number in range(29,33):
            record=self.report['html_plates'][number-1]
            self.assertEqual(record['source'],ATLAS.SOURCES[1])
            body=(self.output/ATLAS.plate_url(number)).read_text(encoding='utf-8')
            self.assertIn('page='+str(number+2),body)
        for number,anchor in ATLAS.TABLE_AIDS:
            body=(self.output/ATLAS.plate_url(number)).read_text(encoding='utf-8')
            self.assertIn('id="'+anchor+'"',body);self.assertIn('scope="row"',body);self.assertIn('scope="col"',body)

    def test_literal_extension_loops_keep_values_and_original_node_lines(self):
        counts={'complex_core':10,'inverse_closure':12,'shared_family':11,'quantization':9}
        for name,count in counts.items():
            source=(ROOT/ATLAS.drawing_source(name)).read_text(encoding='utf-8-sig');nodes=drawing_nodes(source,name)
            self.assertEqual(len(nodes),count)
            for node in nodes:
                if node.get('loop_bindings'):self.assertIn(r'\node',source.splitlines()[node['line']-1])
        source=(ROOT/ATLAS.drawing_source('complex_core')).read_text(encoding='utf-8-sig')
        with self.assertRaisesRegex(ValueError,'inventory'):drawing_nodes(source.replace('6/0/2/0','6/0/2/1'),'complex_core')

    def test_current_pdf_checksum_and_printed_kind_are_explicit(self):
        checks=self.report['edition_checks']
        self.assertTrue(checks['crosswalk_pdf_checksum_current'])
        self.assertNotEqual(checks['inherited_crosswalk_pdf_sha256'],checks['retained_pdf_sha256'])
        self.assertEqual(len(checks['pdf_page_checks']),32)
        self.assertEqual(self.report['figures']['triangular']['isolated_drawing_objects']['objects'],48)
        body=(self.output/ATLAS.plate_url(18)).read_text(encoding='utf-8')
        self.assertIn('Classical input 7.5',body);self.assertIn('Standard fact 7.5',body)
        self.assertIn('revised crosswalk binds all 32 plates',body)
        self.assertNotIn('different PDF checksum',body)

    def test_changed_math_and_reachable_but_wrong_target_are_rejected(self):
        path=self.output/ATLAS.plate_url(29);original=path.read_bytes()
        text,count=re.subn(r'(<(?:span|div) class="arithmatex">\\[\[(])',lambda m:m[0]+'0+',original.decode(),count=1)
        self.assertEqual(count,1);path.write_text(text,encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):ATLAS.verify(self.output,self.documents,self.pages)
        finally:path.write_bytes(original)
        path=self.output/ATLAS.REPORT;original=path.read_bytes();report=json.loads(original)
        report['manuscript_references']['3']=report['manuscript_references']['30'];path.write_text(json.dumps(report),encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):ATLAS.verify(self.output,self.documents,self.pages)
        finally:path.write_bytes(original)

    def test_missing_second_source_and_forged_checksum_status_are_rejected(self):
        path=self.output/ATLAS.REPORT;original=path.read_bytes()
        for change in ('source','checksum'):
            report=json.loads(original)
            if change=='source':report['source_inputs'].pop(ATLAS.SOURCES[1])
            else:report['edition_checks']['crosswalk_pdf_checksum_current']=False
            path.write_text(json.dumps(report),encoding='utf-8')
            try:
                with self.assertRaises(AssertionError):ATLAS.verify(self.output,self.documents,self.pages)
            finally:path.write_bytes(original)


if __name__=='__main__':unittest.main()
