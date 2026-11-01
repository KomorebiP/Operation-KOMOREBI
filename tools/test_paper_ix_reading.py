"""Preservation and reading checks for the complete Paper IX edition."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import posixpath
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import unquote,urlsplit

import readable_chapters as reading
from build_reader_site import Site
from check_reader_site import Page,check_readable_chapter
from paper_ix_reading import BOOK,CHAPTERS,MAIN,BASE,AUX,normalize,source_math
from paper_ix_reading import verify_bibliography,source_specs
from reader_documents import ReadingDocuments,source_lines

ROOT=Path(__file__).resolve().parents[1]


def reader_fixture(output):
    site=SimpleNamespace(root=ROOT,output=output,revision='paper-ix-conversion-test',search=[],cache=None,
                         assessments={},editorial_editions={})
    site.rel=lambda target,page:Site.rel(site,target,page)
    site.write=lambda path,text:Site.write(site,path,text)
    site.page=lambda path,title,body,source=None:Site.page(site,path,title,body,source)
    site.read_source=lambda entry:Site.read_source(site,entry)
    reader=ReadingDocuments.__new__(ReadingDocuments);reader.site=site
    receipt=json.loads((ROOT/'manifests/source-imports/paper-ix.json').read_bytes())
    reader.owned={'papers/paper-ix/current/'+e['path']:dict(e,repository_path='papers/paper-ix/current/'+e['path'],work='paper-ix') for e in receipt['files']}
    reader.records={};reader.images={};reader.inclusions={};reader.learning={'learning_topics':[]}
    reader.manuscript_roots={'paper-ix':MAIN};reader.claims_by_module={};reader.claims_by_source={}
    for row in json.loads((ROOT/'manifests/claim-navigation.json').read_bytes())['records']:
        if row['statement_path'].startswith('papers/paper-ix/current/'):
            reader.claims_by_source.setdefault(row['statement_path'],[]).append(row)
    reader.add(MAIN)
    reader.add('papers/paper-ix/current/publication/pdfs/Paper_IX_Euler_Main_Final.pdf','Read PDF')
    with patch.object(reading,'BOOKS',{'paper-ix':BOOK}):reading.prepare(reader)
    return reader


def publish_fixture(output):
    reader=reader_fixture(output)
    with patch.object(reading,'BOOKS',{'paper-ix':BOOK}):reading.render(reader)
    for record in reader.records.values():
        raw=reader.site.read_source(record);dest=output/record['file_url']
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        if record['format']=='source':
            reader.site.page(record['url'],record['title'],'<h1>'+record['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader


class PaperIXReadingTests(unittest.TestCase):
    def test_printed_numbering_and_complete_source_ranges(self):
        with tempfile.TemporaryDirectory() as folder:
            reader=reader_fixture(Path(folder));book=reader.readable_books['paper-ix']
            printed=dict(re.findall(r'\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}',(ROOT/AUX).read_text(encoding='utf-8-sig')))
            for spec,raw,chapter in book['chapters']:
                for node in chapter.nodes:
                    if node['kind'] in reading.NUMBERED|{'figure','table'}:
                        for label in node['labels']:
                            if label in printed and not re.search(r'(?:^|:)eq:',label):
                                self.assertEqual(node['number'],printed[label],label)
            for source in {s['source'] for s in CHAPTERS if s['source']!=MAIN}:
                specs=[s for s in CHAPTERS if s['source']==source]
                text=(ROOT/source).read_text(encoding='utf-8-sig')
                if 'start_line' in specs[0]:
                    self.assertEqual(specs[0]['start_line'],1)
                    self.assertEqual(specs[-1]['end_line'],len(text.splitlines()))
                    for a,b in zip(specs,specs[1:]):self.assertEqual(a['end_line']+1,b['start_line'])
                self.assertEqual([m for s in specs for m in source_math(text,s)],source_math(text,{'source':source}))

    def test_whole_edition_equations_links_images_and_tables(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()),images=list(reader.images.values()))
            with patch.object(reading,'CHAPTERS',CHAPTERS),patch.object(reading,'BOOKS',{'paper-ix':BOOK}):
                count=check_readable_chapter(output,documents,pages)
            self.assertEqual(count,5252)
            reports=json.loads((output/'documents/readable-chapters.json').read_bytes())
            self.assertEqual(len(reports),56)
            self.assertEqual(sum(n['kind']=='proof' for r in reports for n in r['nodes']),153)
            self.assertEqual(sum(len(r.get('nested_tables',[]))+sum(n['kind'] in {'table','tabular','tabularx','longtable'} for n in r['nodes']) for r in reports),33)
            for spec in CHAPTERS:
                page=pages[spec['url']]
                self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
                self.assertEqual(len(page.ids),len(set(page.ids)))
                for link in page.links:
                    p=urlsplit(link)
                    if p.scheme or p.netloc:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(spec['url']),unquote(p.path))) if p.path else spec['url']
                    if target in pages and p.fragment:self.assertIn(unquote(p.fragment),pages[target].ids,(spec['url'],link))
            self.assertEqual(len(reader.images),14)
            self.assertEqual(len(reader.readable_books['paper-ix']['references']),27)
            self.assertEqual(verify_bibliography(output,documents,pages)['entries'],27)
            self.assertFalse(BOOK.get('partial',False))
            self.assertIn('class="equation-number"',(output/'read/paper-ix/euler-packets.html').read_text(encoding='utf-8'))

    def test_input_graph_and_unheaded_table_controls(self):
        def load(path):return (ROOT/path).read_text(encoding='utf-8-sig')
        self.assertEqual(source_specs(load),CHAPTERS)
        def changed(path):
            text=load(path)
            return text.replace('parts/20_arithmetic','parts/30_lifting') if path==MAIN else text
        with self.assertRaisesRegex(ValueError,'Repeated Paper IX manuscript input'):
            source_specs(changed)
        node=dict(kind='tabular',body=r'{ll}7.5 & Still pending\\8.5 & Later result')
        aid=dict(headers=['Item','Checkpoint scope'],source_first_row=['7.5','Still pending'],
                 caption='Historical pending items',row_header_column=0)
        chapter=reading.Chapter('',{})
        markup=reading.render_table(node,chapter,aid)
        self.assertIn('<th scope="row">7.5</th>',markup)
        self.assertIn('<th scope="col">Checkpoint scope</th>',markup)
        with self.assertRaisesRegex(ValueError,'unheaded source table'):
            reading.render_table(node,chapter,dict(aid,source_first_row=['Changed']))

    def test_layout_translation_preserves_lines_and_rejects_unknown_syntax(self):
        source='\\hypertarget{key}{%\n\\subsection{A heading}\\label{key}}\n\\begin{equation}\nx=y.\n\\end{equation}'
        converted=normalize(source)
        self.assertEqual(source.count('\n'),converted.count('\n'))
        self.assertIn(r'\label{key}',converted)
        self.assertEqual(reading.original_math(converted),['\nx=y.\n'])
        with self.assertRaisesRegex(ValueError,'Unsupported prose command'):
            reading.Chapter('',{}).paragraphs(r'Kept text. \unknowncommand{must not disappear}')


if __name__=='__main__':unittest.main()
