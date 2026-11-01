"""Preserve Paper XII's complete written scope, mathematics and source routes."""
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
from paper_xii_reading import BOOK,CHAPTERS,MAIN,BASE,BIB,normalize,source_math,source_specs,verify_bibliography
from reader_documents import ReadingDocuments,source_lines

ROOT=Path(__file__).resolve().parents[1]


def reader_fixture(output):
    site=SimpleNamespace(root=ROOT,output=output,revision='paper-xii-conversion-test',
        search=[],cache=None,assessments={},editorial_editions={})
    site.rel=lambda target,page:Site.rel(site,target,page)
    site.write=lambda path,text:Site.write(site,path,text)
    site.page=lambda path,title,body,source=None:Site.page(site,path,title,body,source)
    site.read_source=lambda entry:Site.read_source(site,entry)
    reader=ReadingDocuments.__new__(ReadingDocuments);reader.site=site
    receipt=json.loads((ROOT/'manifests/source-imports/paper-xii.json').read_bytes())
    reader.owned={'papers/paper-xii/current/'+e['path']:
        dict(e,repository_path='papers/paper-xii/current/'+e['path'],work='paper-xii') for e in receipt['files']}
    reader.records={};reader.images={};reader.inclusions={};reader.learning={'learning_topics':[]}
    reader.manuscript_roots={'paper-xii':MAIN};reader.claims_by_module={};reader.claims_by_source={}
    for row in json.loads((ROOT/'manifests/claim-navigation.json').read_bytes())['records']:
        if row['statement_path'].startswith(BASE):
            reader.claims_by_source.setdefault(row['statement_path'],[]).append(row)
    reader.add(MAIN)
    reader.add('papers/paper-xii/current/core/publication/pdfs/Paper_XII_Traditional_v1.0.0.pdf','Read PDF')
    with patch.object(reading,'BOOKS',{'paper-xii':BOOK}):reading.prepare(reader)
    return reader


def publish_fixture(output):
    reader=reader_fixture(output)
    with patch.object(reading,'BOOKS',{'paper-xii':BOOK}):reading.render(reader)
    for record in reader.records.values():
        raw=reader.site.read_source(record);dest=output/record['file_url']
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        if record['format']=='source':
            reader.site.page(record['url'],record['title'],'<h1>'+record['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader


class PaperXIIReadingTests(unittest.TestCase):
    def test_complete_sources_numbering_and_recorded_boundaries(self):
        load=lambda path:(ROOT/path).read_text(encoding='utf-8-sig')
        self.assertEqual(source_specs(load),CHAPTERS)
        for source in {s['source'] for s in CHAPTERS}:
            text=load(source);selected=[s for s in CHAPTERS if s['source']==source]
            expected=text.split(r'\begin{document}',1)[1] if source==MAIN else text
            self.assertEqual([m for s in selected for m in source_math(text,s)],reading.original_math(expected),source)
        with tempfile.TemporaryDirectory() as folder:
            reader=reader_fixture(Path(folder));nodes=[n for _,_,c in reader.readable_books['paper-xii']['chapters'] for n in c.nodes]
            self.assertEqual(sum(n['kind']=='proof' for n in nodes),52)
            self.assertEqual(sum(n['kind'] in reading.NUMBERED for n in nodes),82)
            self.assertEqual(sum(n['kind']=='figure' for n in nodes),18)
            self.assertEqual([n['number'] for n in nodes if n['kind']=='section' and n['number']],[str(i) for i in range(1,14)])
            labels={label:n for n in nodes for label in n['labels']}
            self.assertEqual(labels['thm:five_gate_completion']['number'],'12.6')
            self.assertEqual(labels['thm:simultaneous_companion_completion']['number'],'10.5')

    def test_math_proofs_figures_tables_bibliography_and_companions(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()),images=list(reader.images.values()))
            with patch.object(reading,'CHAPTERS',CHAPTERS),patch.object(reading,'BOOKS',{'paper-xii':BOOK}):
                count=check_readable_chapter(output,documents,pages)
            self.assertEqual(count,873)
            reports=json.loads((output/'documents/readable-chapters.json').read_bytes())
            self.assertEqual(len(reports),16)
            self.assertEqual(sum(n['kind'] in {'table','tabular'} for r in reports for n in r['nodes']),2)
            for spec in CHAPTERS:
                page=pages[spec['url']];markup=(output/spec['url']).read_text(encoding='utf-8')
                self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
                self.assertEqual(len(page.ids),len(set(page.ids)))
                self.assertNotIn('p12-route:',markup)
                self.assertNotIn('texorpdfstring',markup)
                for link in page.links:
                    p=urlsplit(link)
                    if p.scheme or p.netloc:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(spec['url']),unquote(p.path))) if p.path else spec['url']
                    if target in pages and p.fragment and not p.query:self.assertIn(unquote(p.fragment),pages[target].ids,(spec['url'],link))
            for source,rows in reader.claims_by_source.items():
                for row in rows:
                    if not row['proof_line']:continue
                    spec=next(s for s in CHAPTERS if s['source']==source and s.get('start_line',1)<=row['statement_line']<=s.get('end_line',10**9))
                    self.assertIn('#L'+str(row['proof_line']),pages[spec['url']].links)
                    self.assertIn('#L'+str(row['statement_line']),pages[spec['url']].links)
            self.assertEqual(len(reader.images),18)
            for image in reader.images.values():
                self.assertEqual(hashlib.sha256((output/image['file_url']).read_bytes()).hexdigest(),image['sha256'])
            self.assertEqual(verify_bibliography(output,documents,pages)['entries'],27)
            self.assertIn('#page=4',(output/'read/paper-xii/reading-map.html').read_text(encoding='utf-8'))
            self.assertIn('compatible Hecke point',(output/'read/paper-xii/reading-map.html').read_text(encoding='utf-8'))

    def test_changed_inputs_and_pdf_heading_control(self):
        def changed(path):
            text=(ROOT/path).read_text(encoding='utf-8-sig')
            return text.replace(r'\input{reading_route.tex}',r'\input{unreviewed}') if path==MAIN else text
        with self.assertRaisesRegex(ValueError,'manuscript input order'):source_specs(changed)
        text='\\section{Ring \\texorpdfstring{\\(R\\cong\\TT\\)}{R equals T}}\n'
        converted=normalize(text)
        self.assertEqual(converted.count('\n'),text.count('\n'))
        self.assertEqual(reading.original_math(converted),[r'R\cong\TT'])
        with self.assertRaisesRegex(ValueError,'Unsupported prose command'):
            reading.Chapter('',{}).paragraphs(r'Kept text. \unreviewedcommand{must remain}')


if __name__=='__main__':unittest.main()
