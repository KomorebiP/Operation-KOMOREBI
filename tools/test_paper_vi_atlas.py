"""Source correspondence and accessible-table checks for the opening atlas."""
import copy
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
import unittest

from paper_vi_atlas import (AtlasChapter, BOOK, DEFINITIONS, FIGURES, HTML_COUNT,
                            PDF, PDF_SHA256, RECEIPTS, SOURCE, TABLE_AIDS, plates)
from reader_atlas import atlas_tex, drawing_nodes, expected_math, render_drawing, transcript_order
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
        cls.macros = manuscript_macros((ROOT/BOOK['main']).read_text(encoding='utf-8-sig')+'\n'+
                                       (ROOT/DEFINITIONS).read_text(encoding='utf-8-sig'),
                                       BOOK['required_macros'])
        cls.receipts = json.loads((ROOT/'website'/RECEIPTS).read_bytes())
        cls.nodes = {name:drawing_nodes((ROOT/BOOK['base']/'visual_graphics'/(name+'.tex')).read_text(encoding='utf-8-sig'))
                     for name in FIGURES}

    def test_inventory_distinguishes_html_plates_from_pdf_continuations(self):
        self.assertEqual(len(self.selected),42)
        self.assertEqual([p['number'] for p in self.selected],list(range(1,43)))
        self.assertEqual(HTML_COUNT,6)
        self.assertTrue(all(p['url'].endswith('.html') for p in self.selected[:6]))
        self.assertTrue(all('/index.html#v' in p['url'] for p in self.selected[6:]))
        self.assertEqual(self.selected[1]['title'],'A dictionary with orientations')
        with self.assertRaisesRegex(ValueError,'numbering'):
            plates(self.source.replace(r'\vpage{3}',r'\vpage{30}',1))
        with self.assertRaisesRegex(ValueError,'preamble'):
            plates('Unreviewed prose.\n'+self.source)

    def test_all_drawing_labels_are_read_once_and_keep_their_math(self):
        self.assertEqual(sum(map(len,self.nodes.values())),138)
        reader = SimpleNamespace(site=SimpleNamespace(rel=lambda path,page:path),
                                 resolve=lambda path,page:'source.html')
        figures = {}
        for record in self.receipts['figures']:
            name = record['name']
            nodes = self.nodes[name]
            order = transcript_order(FIGURES[name],nodes)
            self.assertEqual(sorted(order),list(range(len(nodes))))
            width,height = png_dimensions((ROOT/'website'/record['image']).read_bytes())
            figure = dict(receipt=record,nodes=nodes,description=FIGURES[name],order=order,
                          width=width,height=height)
            figures[name] = figure
            chapter = AtlasChapter('',self.macros)
            chapter.url = 'read/paper-vi/atlas/v01.html'
            markup = render_drawing(figure,chapter,reader)
            self.assertEqual(chapter.math,[m for index in order for m in original_math(nodes[index]['text'])],name)
            self.assertEqual(markup.count('id="drawing-label-'),len(nodes),name)
            if name!='defect_budget':
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
                self.assertEqual(after.count('scope="row"'),4 if plate['number']==1 else 11)
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
