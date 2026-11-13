"""Exact source coverage, visual math, preserved main reader and directory routes."""
from pathlib import Path
import copy,hashlib,json,tempfile,unittest
from unittest.mock import patch
from physics_visual import metadata,source_specs,verify,REPORT,INDEX,BASE
from test_physics_reading import publish_fixture,ROOT
from check_reader_site import Page

class PhysicsVisualTests(unittest.TestCase):
    def test_visual_reading_controls_use_the_visual_sequence(self):
        from reader_display import edition
        from physics_reading import BOOK
        self.assertEqual(edition(INDEX)['index'],INDEX)
        self.assertEqual(len(edition(metadata()['pages'][0]['url'])['chapters']),72)
        self.assertIs(edition(BOOK['chapters'][0]['url']),BOOK)
        self.assertIsNone(edition('read/monographs-physics/atlas/unknown.html'))

    def test_source_order_ranges_and_macros_fail_closed(self):
        data=metadata();load=lambda p:(ROOT/p).read_text(encoding='utf-8-sig')
        self.assertEqual(source_specs(load),data)
        for path in data['inputs']:
            with self.assertRaisesRegex(ValueError,'changed Physics visual source'):
                source_specs(lambda p:load(p)+('changed' if p==path else ''))
        altered=copy.deepcopy(data);altered['pages'][1]['start_line']+=1
        with patch('physics_visual.metadata',return_value=altered),self.assertRaisesRegex(ValueError,'gap or overlap'):
            source_specs(load)
        main=data['atlases'][0]['main'];raw=load(main).replace(r'\end{document}','An omitted passage.\n'+r'\end{document}')
        altered=copy.deepcopy(data);altered['inputs'][main]=hashlib.sha256(raw.encode()).hexdigest()
        with patch('physics_visual.metadata',return_value=altered),self.assertRaisesRegex(ValueError,'Unselected Physics visual'):
            source_specs(lambda p:raw if p==main else load(p))

    def test_complete_publication_and_negative_controls(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            documents=dict(files=list(reader.records.values()),images=list(reader.images.values()),source_revision=reader.site.revision)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            self.assertEqual(verify(output,documents,pages),dict(atlases=5,pages=72,plates=60,math_expressions=718,source_inputs=11))
            report=json.loads((output/REPORT).read_bytes())
            self.assertEqual([sum(p['atlas']==a['id'] for p in report['html_pages']) for a in metadata()['atlases']],[14,14,14,15,15])
            old=json.loads((output/'documents/readable-chapters.json').read_bytes())
            self.assertEqual(len(old),160)
            self.assertEqual(sum(r['math_expressions'] for r in old),6320)
            self.assertEqual(len({r['image'] for r in report['figures'] if '/physics-visual-extra/' in r['image']}),17)
            self.assertEqual(sum('/physics-visual-extra/' not in r['image'] for r in report['figures']),43)
            # Alter published mathematics without touching its declaration.
            page=output/report['html_pages'][0]['url'];raw=page.read_text(encoding='utf-8')
            page.write_text(raw.replace(r'\operatorname{Re}',r'\operatorname{Im}',1),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'Changed Physics visual math'):verify(output,documents,pages)
            page.write_text(raw,encoding='utf-8')
            illustrated=output/report['html_pages'][1]['url'];original=illustrated.read_text(encoding='utf-8')
            illustrated.write_text(original.replace('01_packets.','02_corners.',1),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'Changed Physics visual figure'):verify(output,documents,pages)
            illustrated.write_text(original,encoding='utf-8')
            for title in ['Foundations','Dirac','Gauge','Gravity','Adic']:
                self.assertIn(title,(output/INDEX).read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
