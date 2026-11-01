"""Source correspondence and accessible-table checks for all 42 atlas plates."""
import copy
import hashlib
import json
import posixpath
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
import unittest

from paper_vi_atlas import (AtlasChapter, BOOK, DEFINITIONS, FIGURES, HTML_COUNT,
                            PDF, PDF_SHA256, RECEIPTS, SOURCE, TABLE_AIDS, plates,
                            atlas_macros,reading_aids,render_drawing,atlas_tex)
from reader_atlas import expected_math, transcript_order
from reader_drawing_transcripts import drawing_nodes
from readable_chapters import Chapter, chapter_text, manuscript_macros, original_math, render_table
from reader_documents import png_dimensions

ROOT = Path(__file__).resolve().parents[1]


class Cells(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.cells = []
        self.active = False
        self.feed(markup)
    def handle_starttag(self, tag, attrs):
        if tag in {'td','th'}:
            self.cells.append('')
            self.active = True
    def handle_endtag(self, tag):
        if tag in {'td','th'}:
            self.active = False
    def handle_data(self, data):
        if self.active:
            self.cells[-1] += data


class PaperVIAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT/SOURCE).read_text(encoding='utf-8-sig')
        cls.selected = plates(cls.source)
        cls.macros = atlas_macros((ROOT/BOOK['main']).read_text(encoding='utf-8-sig'),
                                 (ROOT/DEFINITIONS).read_text(encoding='utf-8-sig'))
        cls.receipts = json.loads((ROOT/'website'/RECEIPTS).read_bytes())
        cls.nodes = {name:drawing_nodes((ROOT/BOOK['base']/'visual_graphics'/(name+'.tex')).read_text(encoding='utf-8-sig'))
                     for name in FIGURES}
        main=(ROOT/BOOK['main']).read_text(encoding='utf-8-sig')
        state={'number_floats':True};chapters=[]
        for spec in BOOK['chapters']:
            if 'section_prefix' in spec:
                state.update(section=0,appendix=False,figure=0,table=0,section_prefix=spec['section_prefix'])
            chapter=Chapter(chapter_text(main,spec),cls.macros,state=state,check_refs=False)
            chapter.url=spec['url'];chapters.append((spec,main.encode(),chapter))
            state={key:getattr(chapter,key) for key in ('section','appendix','part','subsection','subsubsection','counter','section_prefix','figure','table','number_floats')}
        cls.pages={};cls.writes={};records={}
        def add(path):
            records.setdefault(path,dict(repository_path=path,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()))
            return records[path]
        site=SimpleNamespace(root=ROOT,revision='test-revision',search=[],
            read_source=lambda record:(ROOT/record['repository_path']).read_bytes(),
            rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page)),
            page=lambda path,title,body:cls.pages.__setitem__(path,body),
            write=lambda path,body:cls.writes.__setitem__(path,body))
        cls.reader=SimpleNamespace(site=site,records=records,add=add,
            readable_books={'paper-vi':dict(main=main,chapters=chapters)},
            resolve=lambda path,page,anchor='':'source.html'+('#'+anchor if anchor else ''),
            work_routes=lambda work,page:'',viewer_url=lambda record,page,anchor='':'original.pdf#'+anchor)
        from paper_vi_atlas import prepare,render
        prepare(cls.reader);render(cls.reader)
        cls.report=json.loads(cls.writes['documents/paper-vi-atlas.json'])

    def test_all_42_production_pages_keep_source_math_and_routes(self):
        self.assertEqual(len(self.pages),43)
        self.assertEqual(len(self.report['html_plates']),42)
        self.assertEqual(len(self.report['figures']),40)
        self.assertEqual(sum(p['math_expressions'] for p in self.report['html_plates']),931)
        self.assertEqual(sum(len(r) for r in self.report['manuscript_references'].values()),76)
        for plate in self.selected:
            body=self.pages[plate['url']]
            self.assertIn(plate['title'],body)
            self.assertIn('page='+str(plate['number']+2),body)
            self.assertNotIn('<iframe',body)
            self.assertEqual(bool(self.report['manuscript_references'][str(plate['number'])]),plate['number'] not in (28,42))
        self.assertIn('href="v42.html"',self.pages['read/paper-vi/atlas/index.html'])

    def test_inventory_includes_all_42_html_plates(self):
        self.assertEqual(len(self.selected),42)
        self.assertEqual([p['number'] for p in self.selected],list(range(1,43)))
        self.assertEqual(HTML_COUNT,42)
        self.assertTrue(all(p['url'].endswith('.html') for p in self.selected))
        self.assertEqual(self.selected[1]['title'],'A dictionary with orientations')
        with self.assertRaisesRegex(ValueError,'numbering'):
            plates(self.source.replace(r'\vpage{3}',r'\vpage{30}',1))
        with self.assertRaisesRegex(ValueError,'preamble'):
            plates('Unreviewed prose.\n'+self.source)

    def test_all_drawing_labels_are_read_once_and_keep_their_math(self):
        self.assertEqual(sum(map(len,self.nodes.values())),588)
        reader = SimpleNamespace(site=SimpleNamespace(rel=lambda path,page:path),
                                 resolve=lambda path,page:'source.html')
        figures = {}
        for record in self.receipts['figures']:
            name = record['name']
            nodes = self.nodes[name]
            source=(ROOT/record['source']).read_text(encoding='utf-8-sig')
            info=reading_aids(name,nodes,source)
            order = transcript_order(info,nodes)
            self.assertEqual(sorted(order),list(range(len(nodes))))
            width,height = png_dimensions((ROOT/'website'/record['image']).read_bytes())
            figure = dict(receipt=record,nodes=nodes,description=info,order=order,
                          width=width,height=height)
            figures[name] = figure
            chapter = AtlasChapter('',self.macros)
            chapter.url = 'read/paper-vi/atlas/v01.html'
            markup = render_drawing(figure,chapter,reader)
            self.assertEqual(chapter.math,[m for index in order for m in original_math(nodes[index]['text'])],name)
            self.assertEqual(markup.count('id="drawing-label-'),len(nodes),name)
            if name in {'three_views','clock','generator_modes','lumpability'}:
                self.assertIn('scope="col"',markup)
            self.assertNotIn('Drawing label 0',markup)
        for plate in self.selected[:HTML_COUNT]:
            expected = expected_math(plate,figures)
            source_count = len(original_math(plate['body']))
            names = [node['body'] for node in Chapter(atlas_tex(plate['body']),self.macros).nodes if node['kind']=='figure']
            self.assertEqual(len(expected),source_count+sum(len(original_math(n['text'])) for name in names for n in self.nodes[name]))

    def test_drawing_transcript_rejects_omitted_or_repeated_labels(self):
        bad = copy.deepcopy(FIGURES['clock'])
        bad['blocks'] = bad['blocks'][:-1]
        with self.assertRaisesRegex(ValueError,'exactly once'):
            transcript_order(bad,self.nodes['clock'])
        bad = copy.deepcopy(FIGURES['clock'])
        bad['blocks'].append(dict(kind='text',nodes=[0]))
        with self.assertRaisesRegex(ValueError,'exactly once'):
            transcript_order(bad,self.nodes['clock'])

    def test_authored_reference_tables_keep_all_cells_and_equations(self):
        found = set()
        for plate in self.selected[:HTML_COUNT]:
            parsed = Chapter(atlas_tex(plate['body']),self.macros)
            for node in parsed.nodes:
                if node['kind'] not in {'table','tabularx'}:
                    continue
                key = (plate['number'],node['id'])
                found.add(key)
                original,aided = AtlasChapter('',self.macros),AtlasChapter('',self.macros)
                for chapter in (original,aided):
                    chapter.url = plate['url']
                    chapter.command_links = {'pagerefV':{str(p['number']):(p['url'],'V'+str(p['number'])) for p in self.selected}}
                before = render_table(node,original)
                after = render_table(node,aided,TABLE_AIDS[key])
                self.assertEqual(Cells(before).cells,Cells(after).cells)
                self.assertEqual(original.math,aided.math)
                self.assertEqual(after.count('scope="row"'),{1:4,2:11,28:5}[plate['number']])
                self.assertIn('<caption>'+TABLE_AIDS[key]['caption']+'</caption>',after)
        self.assertEqual(found,set(TABLE_AIDS))

    def test_manuscript_table_headers_preserve_all_cells_and_equations(self):
        main=(ROOT/BOOK['main']).read_text(encoding='utf-8-sig')
        found=set()
        for spec in BOOK['chapters']:
            chapter=Chapter(chapter_text(main,spec),self.macros,check_refs=False)
            for node in chapter.nodes:
                if node['kind'] not in {'table','longtable','tabularx'}: continue
                found.add(node['id'])
                aid=BOOK['table_reading_aids'][node['id']]
                before,after=Chapter('',self.macros),Chapter('',self.macros)
                original=render_table(node,before)
                aided=render_table(node,after,aid)
                self.assertEqual(Cells(original).cells,Cells(aided).cells)
                self.assertEqual(before.math,after.math)
                self.assertEqual(aided.count('scope="row"'),aided.count('<tr>')-1)
                self.assertIn('<caption>',aided)
        self.assertEqual(found,set(BOOK['table_reading_aids']))
        self.assertEqual(len(found),5)

    def test_label_line_breaks_preserve_matrix_rows(self):
        chapter = AtlasChapter('',{})
        value = r'First\\Second $\begin{pmatrix}1&2\\3&4\end{pmatrix}$.'
        markup = chapter.inline(value)
        self.assertRegex(markup,r'First<br>\s*Second')
        self.assertEqual(chapter.math,[r'\begin{pmatrix}1&2\\3&4\end{pmatrix}'])

    def test_drawing_views_bind_the_pdf_tikz_and_png(self):
        self.assertEqual(self.receipts['source_pdf'],PDF)
        self.assertEqual(self.receipts['source_pdf_sha256'],PDF_SHA256)
        self.assertEqual({r['name'] for r in self.receipts['figures']},set(FIGURES))
        for record in self.receipts['figures']:
            self.assertEqual(hashlib.sha256((ROOT/record['source']).read_bytes()).hexdigest(),record['source_sha256'])
            raw = (ROOT/'website'/record['image']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),record['image_sha256'])
            x0,y0,x1,y1 = record['crop_pdf_points']
            self.assertTrue(0<=x0<x1<=612 and 0<=y0<y1<=792)
            self.assertEqual(png_dimensions(raw),((x1-x0)*3,(y1-y0)*3))
            self.assertEqual(record['pdf_page'],record['plate']+2)


if __name__ == '__main__':
    unittest.main()
