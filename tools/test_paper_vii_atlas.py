"""Retained-source correspondence for all 40 worked Paper VII plates."""
import copy
import hashlib
import json
from pathlib import Path
import posixpath
from types import SimpleNamespace
import unittest

import paper_vii_atlas as atlas
from readable_chapters import Chapter, manuscript_macros, original_math
from reader_atlas import transcript_order

ROOT=Path(__file__).resolve().parents[1]


class PaperVIIAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main=(ROOT/atlas.BOOK['main']).read_text(encoding='utf-8-sig')
        cls.source=(ROOT/atlas.SOURCE).read_text(encoding='utf-8-sig')
        cls.selected=atlas.plates(cls.source)
        macros=manuscript_macros(main)
        raw=(ROOT/atlas.BOOK['base']/'parts/02_strengthened.tex').read_bytes()
        chapter=Chapter(raw.decode('utf-8-sig'),macros,state={'part':2,'part_numbering':True},check_refs=False)
        chapter.url='read/paper-vii/effective-dynamics-and-towers.html'
        cls.pages={};cls.writes={}
        site=SimpleNamespace(root=ROOT,search=[],revision='test-revision',
            read_source=lambda record:(ROOT/record['repository_path']).read_bytes(),
            rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page)),
            page=lambda path,title,body:cls.pages.__setitem__(path,body),
            write=lambda path,value:cls.writes.__setitem__(path,value))
        records={}
        def add(path):
            records.setdefault(path,dict(repository_path=path,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()))
            return records[path]
        cls.reader=SimpleNamespace(site=site,records=records,add=add,
            readable_books={'paper-vii':dict(main=main,chapters=[({},raw,chapter)])},
            resolve=lambda path,page,anchor='':'source.html'+('#'+anchor if anchor else ''),
            work_routes=lambda work,page:'',viewer_url=lambda record,page,anchor='':'original.pdf#'+anchor)
        atlas.prepare(cls.reader)
        atlas.render(cls.reader)
        cls.report=json.loads(cls.writes[atlas.REPORT])

    def test_all_source_plates_drawings_and_math_are_rendered(self):
        self.assertEqual(len(self.selected),40)
        self.assertEqual(len(self.pages),41)
        self.assertEqual(len(self.report['figures']),38)
        self.assertEqual(sum(len(f['nodes']) for f in self.report['figures'].values()),547)
        self.assertEqual(sum(p['math_expressions'] for p in self.report['html_plates']),945)
        for plate in self.selected:
            text=self.pages[plate['url']]
            self.assertIn(plate['title'],text)
            self.assertIn('page='+str(plate['number']+117),text)
            self.assertNotIn('<iframe',text)
            self.assertTrue(self.report['manuscript_references'][str(plate['number'])])
        self.assertIn('Standard fact II.7.7',self.pages[atlas.plate_url(18)])

    def test_atlas_records_do_not_overwrite_another_edition(self):
        import paper_vi_atlas
        import reader_atlas
        self.assertEqual(len({atlas.REPORT,paper_vi_atlas.REPORT,reader_atlas.REPORT}),3)

    def test_finite_loop_values_and_matrix_rows_are_preserved(self):
        nodes=atlas.drawing_nodes((ROOT/atlas.drawing_source('defect')).read_text())
        self.assertEqual([n['text'] for n in nodes[:3]],['$9/10$','$1$','$11/10$'])
        nodes=atlas.drawing_nodes((ROOT/atlas.drawing_source('transfer_ground')).read_text())
        self.assertEqual([n['text'] for n in nodes[:3]],['$1$','$1/2$','$1/4$'])
        text=(ROOT/atlas.drawing_source('damping')).read_text()
        nodes=atlas.drawing_nodes(text)
        self.assertIn(r'coherence factor\newline $4/5$',[n['text'] for n in nodes])
        self.assertEqual(atlas.label_tex(r'$\mat{1&0\\0&1}$'),r'$\mat{1&0\\0&1}$')
        self.assertEqual([m for n in nodes for m in original_math(n['text'])],original_math(atlas.label_tex(text)))

    def test_every_original_label_is_transcribed_once(self):
        for name,figure in self.reader.paper_vii_atlas['figures'].items():
            self.assertEqual(sorted(figure['order']),list(range(len(figure['nodes']))),name)
            page=next(p for p in self.selected if r'\vfig{'+name+'}' in p['body'] or r'\xfig{'+name+'}' in p['body'])
            self.assertEqual(self.pages[page['url']].count('id="drawing-label-'),len(figure['nodes']),name)
        figure=self.reader.paper_vii_atlas['figures']['damping']
        bad=copy.deepcopy(figure['description'])
        bad['blocks'].append(dict(kind='text',nodes=[0]))
        with self.assertRaisesRegex(ValueError,'exactly once'):
            transcript_order(bad,figure['nodes'])

    def test_unreviewed_source_forms_stop_the_conversion(self):
        with self.assertRaisesRegex(ValueError,'preamble'):
            atlas.plates('New prose.\n'+self.source)
        with self.assertRaisesRegex(ValueError,'numbering'):
            atlas.plates(self.source.replace(r'\vpage{3}',r'\vpage{30}',1))
        with self.assertRaisesRegex(ValueError,'variables'):
            atlas.expand_drawing_loops(r'\foreach \other in {1,2,3} {\node at (0,0) {$1$};}')
        with self.assertRaisesRegex(ValueError,'outside'):
            atlas.drawing_nodes(r'\node at (0,0) {$1$}; $2$')

    def test_frozen_pdf_and_all_rendered_images_match_receipts(self):
        self.assertEqual(hashlib.sha256((ROOT/atlas.PDF).read_bytes()).hexdigest(),atlas.PDF_SHA256)
        for name,figure in self.reader.paper_vii_atlas['figures'].items():
            receipt=figure['receipt']
            self.assertEqual(hashlib.sha256((ROOT/receipt['source']).read_bytes()).hexdigest(),receipt['source_sha256'],name)
            self.assertEqual(hashlib.sha256((ROOT/'website'/receipt['image']).read_bytes()).hexdigest(),receipt['image_sha256'],name)


if __name__=='__main__':unittest.main()
