"""Full guide inventory, explicit current routes, and preservation of revised scope."""
import json
from pathlib import Path
import tempfile
import unittest
from test_core_worked_atlases import publish
from paper_xii_atlas import ATLAS,SPEC
from paper_xii_atlas_drawings import drawing_nodes

ROOT=Path(__file__).resolve().parents[1]


class PaperXIIAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.output=Path(cls.temp.name)
        cls.reader,cls.documents,cls.pages=publish('paper-xii',cls.output,ATLAS)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def verify(self):return ATLAS.verify(self.output,self.documents,self.pages)

    def test_all_plates_drawings_and_current_manuscript_routes(self):
        self.assertEqual(self.verify(),dict(total_plates=27,html_plates=27,drawings=23,transcribed_labels=335,math_expressions=752,return_links=53))
        self.assertEqual(len(ATLAS.TABLE_AIDS),15)
        for n in range(1,28):
            page=self.pages[ATLAS.plate_url(n)];self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0));self.assertEqual(len(page.ids),len(set(page.ids)))
            self.assertNotIn('p12-route:',(self.output/ATLAS.plate_url(n)).read_text(encoding='utf-8'))

    def test_inline_drawings_and_literal_loop_labels_are_complete(self):
        report=json.loads((self.output/ATLAS.REPORT).read_bytes())
        self.assertEqual({f['name'] for f in report['figures'].values() if f['source']==ATLAS.SOURCE},{'inline_nilpotent_slice','inline_packet_occupancy'})
        nodes=report['figures']['derived_fibers']['nodes']
        self.assertTrue(all(1<=n['line']<=17 for n in nodes))
        self.assertEqual(sum(n['text']=='$0$' for n in nodes),9)
        for n in [7,13]:self.assertEqual(sum('/atlas/' in im['src'] for im in self.pages[ATLAS.plate_url(n)].images),1)
        self.assertIn('retained_unused_artwork',report['edition_checks'])

    def test_missing_input_or_changed_literal_loop_fails_closed(self):
        def read(path):
            raw=(ROOT/path).read_bytes();return raw.replace(br'\input{source/pages.tex}',b'') if path==ATLAS.DEFINITIONS else raw
        with self.assertRaisesRegex(ValueError,'input graph'):ATLAS.read_plates(read)
        raw=(ROOT/(SPEC['drawing_base']+'derived_fibers.tex')).read_text(encoding='utf-8-sig')
        with self.assertRaisesRegex(ValueError,'literal label loop'):drawing_nodes(raw.replace('3/0','3/1'),'derived_fibers')

    def test_changed_equation_scope_table_and_reachable_target_are_rejected(self):
        for number,old,new in [(17,b'conditional',b'unconditional'),(26,b'<td>49</td>',b'<td>48</td>'),(25,b'm_1+m_2=5',b'm_1+m_2=6'),(7,b'>reduced slice<',b'>altered slice<')]:
            path=self.output/ATLAS.plate_url(number);raw=path.read_bytes();changed=raw.replace(old,new,1);self.assertNotEqual(changed,raw);path.write_bytes(changed)
            try:
                with self.assertRaises(AssertionError):self.verify()
            finally:path.write_bytes(raw)
        path=self.output/ATLAS.REPORT;raw=path.read_bytes();report=json.loads(raw);report['manuscript_references']['3']=report['manuscript_references']['25'];path.write_text(json.dumps(report),encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):self.verify()
        finally:path.write_bytes(raw)


if __name__=='__main__':unittest.main()
