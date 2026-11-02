"""Exercise the complete Paper V atlas through production render and verification."""
import json
from pathlib import Path
import posixpath
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch

import paper_v_atlas as atlas
import readable_chapters as chapters
from check_reader_site import Page
from reader_documents import source_lines
from test_paper_v_reading import reader_fixture

ROOT=Path(__file__).resolve().parents[1]


def publish(output):
    reader=reader_fixture(output)
    reader.work_routes=lambda work,page:''
    atlas.prepare(reader)
    with patch.object(chapters,'BOOKS',{'paper-v':atlas.BOOK}):
        chapters.render(reader)
    atlas.render(reader)
    for record in list(reader.records.values()):
        raw=reader.site.read_source(record)
        target=output/record['file_url'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        if record['format']=='source':
            reader.site.page(record['url'],record['title'],'<h1>Source</h1>'+source_lines(raw.decode('utf-8-sig')))
    shutil.copytree(ROOT/'website/assets',output/'assets',dirs_exist_ok=True)
    documents=dict(source_revision=reader.site.revision,files=list(reader.records.values()))
    pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
    return reader,documents,pages


class PaperVAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.output=Path(cls.temp.name)
        cls.reader,cls.documents,cls.pages=publish(cls.output)
        cls.report=json.loads((cls.output/atlas.REPORT).read_bytes())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_full_edition_passes_production_verifier(self):
        result=atlas.verify(self.output,self.documents,self.pages)
        self.assertEqual(result['html_plates'],40)
        self.assertEqual(result['drawings'],37)
        self.assertEqual(result['transcribed_labels'],550)
        self.assertGreater(result['math_expressions'],900)
        self.assertGreater(result['return_links'],65)

    def test_every_plate_keeps_pdf_source_and_both_directions_of_manuscript_links(self):
        self.assertEqual(len(self.report['html_plates']),40)
        for number in range(1,41):
            page=atlas.plate_url(number)
            body=(self.output/page).read_text(encoding='utf-8')
            self.assertIn('page='+str(number+3),body)
            self.assertIn('Original atlas source',body)
            self.assertNotIn('<iframe',body)
            for label,target in self.report['manuscript_references'][str(number)]:
                chapter,anchor=target.split('#')
                self.assertIn(anchor,self.pages[chapter].ids)
                self.assertIn(posixpath.relpath(target,posixpath.dirname(page)),self.pages[page].links)
                self.assertIn(posixpath.relpath(page,posixpath.dirname(chapter)),self.pages[chapter].links)
        self.assertIn('atlas/index.html', (self.output/'read/paper-v/visual-atlas.html').read_text(encoding='utf-8'))

    def test_tables_and_labels_are_selectable_and_semantic(self):
        self.assertEqual(len(atlas.TABLE_AIDS),6)
        for number,anchor in atlas.TABLE_AIDS:
            body=(self.output/atlas.plate_url(number)).read_text(encoding='utf-8')
            self.assertIn('id="'+anchor+'"',body)
            self.assertIn('scope="col"',body)
            self.assertIn('scope="row"',body)
        self.assertEqual(sum(len(f['nodes']) for f in self.report['figures'].values()),550)
        for figure in self.report['figures'].values():
            self.assertEqual(sorted(figure['node_order']),list(range(len(figure['nodes']))))
            body=(self.output/atlas.plate_url(figure['plate'])).read_text(encoding='utf-8')
            self.assertEqual(body.count('id="drawing-label-'),len(figure['nodes']))

    def test_verifier_rejects_changed_rendered_math(self):
        path=self.output/atlas.plate_url(3)
        original=path.read_text(encoding='utf-8')
        changed,count=re.subn(r'(<(?:span|div) class="arithmatex">\\[\[(])',lambda m:m[0]+'0+',original,count=1)
        self.assertEqual(count,1)
        path.write_text(changed,encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):
                atlas.verify(self.output,self.documents,self.pages)
        finally:
            path.write_text(original,encoding='utf-8')

    def test_source_and_image_changes_require_review(self):
        source=(ROOT/atlas.SOURCE).read_text(encoding='utf-8-sig')
        with self.assertRaisesRegex(ValueError,'numbering'):
            atlas.plates(source.replace(r'\vpage{3}',r'\vpage{30}',1))
        with self.assertRaisesRegex(ValueError,'preamble'):
            atlas.plates('Unexpected source text\n'+source)
        from paper_v_atlas_drawings import drawing_nodes
        text=(ROOT/atlas.drawing_source('ext_frame')).read_text(encoding='utf-8-sig')
        with self.assertRaisesRegex(ValueError,'loop'):
            drawing_nodes(text.replace('9/{9/4}','10/{9/4}'))
        with self.assertRaisesRegex(ValueError,'transcript'):
            drawing_nodes(r'\node at (0,0) {$x$}; $y$')

    def test_changed_drawing_image_stops_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            reader=reader_fixture(Path(temporary))
            original=Path.read_bytes
            def changed(path):
                raw=original(path)
                return raw+b'changed' if path.name=='three_worlds.png' else raw
            with patch.object(Path,'read_bytes',changed):
                with self.assertRaisesRegex(ValueError,'changed Paper V drawing'):
                    atlas.prepare(reader)


if __name__=='__main__':
    unittest.main()
