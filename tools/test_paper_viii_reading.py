"""Check the complete Paper VIII conversion against the retained manuscript."""
import hashlib
import json
from pathlib import Path
import posixpath
import re
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

import readable_chapters as chapters
from build_reader_site import Site
from check_reader_site import Page, check_readable_chapter
from paper_viii_reading import BOOK, CHAPTERS, MAIN
from reader_documents import ReadingDocuments, source_lines

ROOT=Path(__file__).resolve().parents[1]


def reader_fixture(output):
    site=SimpleNamespace(root=ROOT,output=output,revision='paper-viii-conversion-test',
        search=[],cache=None,assessments={},editorial_editions={})
    site.rel=lambda target,page:Site.rel(site,target,page)
    site.write=lambda path,text:Site.write(site,path,text)
    site.page=lambda path,title,body,source=None:Site.page(site,path,title,body,source)
    site.read_source=lambda entry:Site.read_source(site,entry)
    reader=ReadingDocuments.__new__(ReadingDocuments)
    reader.site=site
    receipt=json.loads((ROOT/'manifests/source-imports/paper-viii.json').read_bytes())
    reader.owned={'papers/paper-viii/current/'+entry['path']:
        dict(entry,repository_path='papers/paper-viii/current/'+entry['path'],work='paper-viii')
        for entry in receipt['files']}
    reader.records={};reader.images={};reader.inclusions={}
    reader.learning={'learning_topics':[]}
    reader.manuscript_roots={'paper-viii':MAIN}
    reader.claims_by_module={};reader.claims_by_source={}
    claims=json.loads((ROOT/'manifests/claim-navigation.json').read_bytes())['records']
    for row in claims:
        if row['statement_path'].startswith(BOOK['base']):
            reader.claims_by_source.setdefault(row['statement_path'],[]).append(row)
    reader.add(MAIN)
    reader.add('papers/paper-viii/current/papers/Paper_VIII_Traditional_Final.pdf','Read PDF')
    with patch.object(chapters,'BOOKS',{'paper-viii':BOOK}):
        chapters.prepare(reader)
    return reader


def publish_fixture(output):
    reader=reader_fixture(output)
    with patch.object(chapters,'BOOKS',{'paper-viii':BOOK}):
        chapters.render(reader)
    for record in reader.records.values():
        raw=reader.site.read_source(record)
        target=output/record['file_url'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        if record['format']=='source':
            reader.site.page(record['url'],record['title'],
                '<h1>'+record['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader


class PaperVIIIReadingTests(unittest.TestCase):
    def test_complete_sources_and_printed_numbering(self):
        with tempfile.TemporaryDirectory() as folder:
            reader=reader_fixture(Path(folder))
            parsed=reader.readable_books['paper-viii']['chapters']
            self.assertEqual(len(parsed),23)
            for source in {s['source'] for s in CHAPTERS}:
                text=(ROOT/source).read_text(encoding='utf-8-sig')
                selected=[chapters.chapter_text(text,s) for s in CHAPTERS if s['source']==source]
                expected=text.split(r'\begin{document}',1)[-1] if source==MAIN else text
                self.assertEqual([m for t in selected for m in chapters.original_math(t)],
                                 chapters.original_math(expected),source)
                specs=[s for s in CHAPTERS if s['source']==source]
                if source.endswith('/parts/01_manuscript.tex'):
                    self.assertEqual(specs[0]['start_line'],1)
                    self.assertEqual(specs[-1]['end_line'],len(text.splitlines()))
                    for a,b in zip(specs,specs[1:]):self.assertEqual(a['end_line']+1,b['start_line'])
                    for spec in specs:
                        self.assertEqual(re.findall(r'\\section\{([^{}]+)\}',chapters.chapter_text(text,spec)),[spec['title']])
            nodes=[n for _,_,c in parsed for n in c.nodes]
            self.assertEqual(sum(n['kind']=='proof' for n in nodes),56)
            self.assertEqual(sum(n['kind']=='figure' for n in nodes),25)
            self.assertEqual(sum(n['kind'] in {'table','tabular'} for n in nodes),12)
            self.assertEqual([n['number'] for n in nodes if n['kind']=='section' and n['number']],
                             [str(i) for i in range(1,16)]+list('ABCDEF'))
            aux=(ROOT/BOOK['base']/'Paper_VIII_Traditional_Final.aux').read_text(encoding='utf-8-sig')
            printed=dict(re.findall(r'\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}',aux))
            for node in nodes:
                if node['kind'] not in chapters.NUMBERED|{'figure','table'}:continue
                for label in node['labels']:
                    if label in printed:self.assertEqual(node['number'],printed[label],label)

    def test_equations_proof_routes_figures_and_accessible_tables(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8'))
                   for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()),images=list(reader.images.values()))
            with patch.object(chapters,'CHAPTERS',CHAPTERS),patch.object(chapters,'BOOKS',{'paper-viii':BOOK}):
                count=check_readable_chapter(output,documents,pages)
            self.assertEqual(count,1192)
            for path,rows in reader.claims_by_source.items():
                for row in rows:
                    if not row['proof_line']:continue
                    statement=chapters.readable_url(path,row['statement_line'])
                    proof=chapters.readable_url(path,row['proof_line'])
                    self.assertIsNotNone(statement);self.assertIsNotNone(proof)
                    statement_path,statement_id=statement.split('#');proof_path,proof_id=proof.split('#')
                    self.assertIn('#'+proof_id,pages[statement_path].links)
                    self.assertIn('#'+statement_id,pages[proof_path].links)
            for spec in CHAPTERS:
                page=pages[spec['url']]
                self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
                self.assertEqual(len(page.ids),len(set(page.ids)))
                for link in page.links:
                    parts=urlsplit(link)
                    if parts.scheme or parts.netloc:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(spec['url']),unquote(parts.path))) if parts.path else spec['url']
                    if target in pages and parts.fragment:self.assertIn(unquote(parts.fragment),pages[target].ids,(spec['url'],link))
            self.assertEqual(len(reader.images),25)
            for image in reader.images.values():
                self.assertEqual(hashlib.sha256((output/image['file_url']).read_bytes()).hexdigest(),image['sha256'])
                self.assertEqual(reader.records[image['source']]['sha256'],image['source_sha256'])
            self.assertIn('The original visual atlas remains', (output/BOOK['index']).read_text(encoding='utf-8'))

    def test_grouped_headers_parallel_rows_and_literal_commands(self):
        source=ROOT/BOOK['base']/'monograph_examples.tex'
        chapter=chapters.Chapter(source.read_text(encoding='utf-8-sig'),{},check_refs=False)
        node=next(n for n in chapter.nodes if n['id']=='L85')
        aid=BOOK['table_reading_aids'][('monograph_examples.tex','L85')]
        markup=chapters.render_table(node,chapter,aid)
        self.assertEqual(markup.count('scope="colgroup"'),2)
        self.assertEqual(markup.count('scope="col"'),5)
        self.assertEqual(markup.count('scope="row"'),3)
        self.assertEqual(chapter.math,chapters.original_math(node['body']))
        with self.assertRaisesRegex(ValueError,'subordinate headers changed'):
            chapters.render_table(node,chapter,dict(aid,subheaders=['Changed']))
        parallel=next(n for n in chapter.nodes if n['id']=='L97')
        aid=BOOK['table_reading_aids'][('monograph_examples.tex','L97')]
        self.assertEqual(chapters.render_table(parallel,chapter,aid).count('scope="row"'),8)
        text='\\begin{verbatim}\n# literal $x$ and 100%\\n\\end{verbatim}'
        literal=chapters.Chapter(text,{})
        self.assertEqual(literal.nodes[0]['kind'],'verbatim')
        self.assertIn('100%',literal.nodes[0]['body'])
        self.assertEqual(chapters.original_math(text),[])


if __name__=='__main__':unittest.main()
