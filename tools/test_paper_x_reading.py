"""Preserve Paper X's complete written scope, mathematics and source routes."""
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
from paper_x_reading import BOOK,CHAPTERS,MAIN,BASE,BIB,normalize,source_math,source_specs,verify_bibliography
from reader_documents import ReadingDocuments,source_lines

ROOT=Path(__file__).resolve().parents[1]


def reader_fixture(output):
    site=SimpleNamespace(root=ROOT,output=output,revision='paper-x-conversion-test',
        search=[],cache=None,assessments={},editorial_editions={})
    site.rel=lambda target,page:Site.rel(site,target,page)
    site.write=lambda path,text:Site.write(site,path,text)
    site.page=lambda path,title,body,source=None:Site.page(site,path,title,body,source)
    site.read_source=lambda entry:Site.read_source(site,entry)
    reader=ReadingDocuments.__new__(ReadingDocuments);reader.site=site
    receipt=json.loads((ROOT/'manifests/source-imports/paper-x.json').read_bytes())
    reader.owned={'papers/paper-x/current/'+e['path']:
        dict(e,repository_path='papers/paper-x/current/'+e['path'],work='paper-x') for e in receipt['files']}
    reader.records={};reader.images={};reader.inclusions={};reader.learning={'learning_topics':[]}
    reader.manuscript_roots={'paper-x':MAIN};reader.claims_by_module={};reader.claims_by_source={}
    for row in json.loads((ROOT/'manifests/claim-navigation.json').read_bytes())['records']:
        if row['statement_path'].startswith(BASE):
            reader.claims_by_source.setdefault(row['statement_path'],[]).append(row)
    reader.add(MAIN)
    for name,title in [('Traditional','Read PDF'),('Visual_Guide','Visual guide (PDF)'),('Lean_Guide','Lean guide (PDF)')]:
        reader.add('papers/paper-x/current/publication/pdfs/Paper_X_'+name+'_Final.pdf',title)
    with patch.object(reading,'BOOKS',{'paper-x':BOOK}):reading.prepare(reader)
    return reader


def publish_fixture(output):
    reader=reader_fixture(output)
    with patch.object(reading,'BOOKS',{'paper-x':BOOK}):reading.render(reader)
    for record in reader.records.values():
        raw=reader.site.read_source(record);dest=output/record['file_url']
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        if record['format']=='source':
            reader.site.page(record['url'],record['title'],'<h1>'+record['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader


class PaperXReadingTests(unittest.TestCase):
    def test_complete_authored_ranges_and_numbering(self):
        load=lambda path:(ROOT/path).read_text(encoding='utf-8-sig')
        self.assertEqual(source_specs(load),CHAPTERS)
        for source in {s['source'] for s in CHAPTERS}:
            specs=[s for s in CHAPTERS if s['source']==source]
            text=load(source)
            expected=text.split(r'\begin{document}',1)[1] if source==MAIN else text
            self.assertEqual([m for spec in specs for m in source_math(text,spec)],source_math(expected,{}),source)
        with tempfile.TemporaryDirectory() as folder:
            reader=reader_fixture(Path(folder));chapters=reader.readable_books['paper-x']['chapters']
            nodes=[n for _,_,c in chapters for n in c.nodes]
            self.assertEqual([n['number'] for n in nodes if n['kind']=='section' and n['number']],
                [str(i) for i in range(1,16)]+list('ABCDE'))
            self.assertEqual(sum(n['kind']=='proof' for n in nodes),16)
            self.assertEqual(sum(n['kind']=='figure' for n in nodes),16)
            self.assertEqual(sum(n['kind']=='numericalcertificate' for n in nodes),4)
            for source,rows in reader.claims_by_source.items():
                for row in rows:
                    targets=[n for spec,_,c in chapters if spec['source']==source for n in c.nodes]
                    node=next(n for n in targets if n['line']==row['statement_line'])
                    label=row['labels'][0]
                    expected=label.removeprefix('px:') if label.startswith('px:') else {'prop:residue-count':'C.1','prop:norm-character':'C.2'}[label]
                    self.assertEqual(node['number'],expected)

    def test_equations_links_figures_tables_and_bibliography(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()),images=list(reader.images.values()))
            with patch.object(reading,'CHAPTERS',CHAPTERS),patch.object(reading,'BOOKS',{'paper-x':BOOK}):
                count=check_readable_chapter(output,documents,pages)
            self.assertEqual(count,1080)
            reports=json.loads((output/'documents/readable-chapters.json').read_bytes())
            self.assertEqual(len(reports),30)
            self.assertEqual(sum(n['kind'] in {'table','longtable','tabularx'} for r in reports for n in r['nodes']),3)
            for spec in CHAPTERS:
                page=pages[spec['url']]
                self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
                self.assertEqual(len(page.ids),len(set(page.ids)))
                for link in page.links:
                    p=urlsplit(link)
                    if p.scheme or p.netloc:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(spec['url']),unquote(p.path))) if p.path else spec['url']
                    if target in pages and p.fragment:self.assertIn(unquote(p.fragment),pages[target].ids,(spec['url'],link))
            self.assertEqual(len(reader.images),16)
            for image in reader.images.values():
                self.assertEqual(hashlib.sha256((output/image['file_url']).read_bytes()).hexdigest(),image['sha256'])
            for source,rows in reader.claims_by_source.items():
                for row in rows:
                    if not row['proof_line']:continue
                    spec=next(s for s in CHAPTERS if s['source']==source and s.get('start_line',1)<=row['statement_line']<=s.get('end_line',10**9))
                    self.assertIn('#L'+str(row['proof_line']),pages[spec['url']].links)
                    self.assertIn('#L'+str(row['statement_line']),pages[spec['url']].links)
            self.assertEqual(verify_bibliography(output,documents,pages)['entries'],23)
            continuation=(output/'read/paper-x/residue-counting.html').read_text(encoding='utf-8')
            self.assertIn('class="equation-number">(1)',continuation)
            self.assertIn('class="equation-number">(2)',continuation)
            self.assertIn('a separate nonzero premise',(output/'read/paper-x/reading-contract.html').read_text(encoding='utf-8'))
            self.assertIn('It does not identify those two objects',(output/'read/paper-x/reading-contract.html').read_text(encoding='utf-8'))

    def test_changed_inputs_and_unknown_syntax_are_rejected(self):
        def load(path):
            text=(ROOT/path).read_text(encoding='utf-8-sig')
            return text.replace(r'\input{conditional_completion.tex}',r'\input{unreviewed.tex}') if path==MAIN else text
        with self.assertRaisesRegex(ValueError,'manuscript input order'):source_specs(load)
        with self.assertRaisesRegex(ValueError,'Unsupported prose command'):
            reading.Chapter('',{}).paragraphs(r'Kept text. \unreviewedcommand{must remain}')
        text='\\fbox{\\begin{minipage}{0.94\\linewidth}\nHistorical $x$.\n\\end{minipage}}'
        self.assertEqual(normalize(text).count('\n'),text.count('\n'))
        self.assertEqual(reading.original_math(normalize(text)),['x'])
        chapter=reading.Chapter('',{})
        markup=chapter.paragraphs('Before $a$.\\paragraph{Step $b$.}After $c$.')
        self.assertIn('<h5>',markup)
        self.assertEqual(chapter.math,['a','b','c'])


if __name__=='__main__':unittest.main()
