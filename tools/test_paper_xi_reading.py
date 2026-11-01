"""Preserve Paper XI's complete written scope, mathematics and source routes."""
import hashlib
import html
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
from paper_xi_reading import BOOK,CHAPTERS,MAIN,BASE,BIB,AUX,CONCORDANCE,normalize,source_math,source_specs,verify_bibliography
from reader_documents import ReadingDocuments,source_lines

ROOT=Path(__file__).resolve().parents[1]


def reader_fixture(output):
    site=SimpleNamespace(root=ROOT,output=output,revision='paper-xi-conversion-test',
        search=[],cache=None,assessments={},editorial_editions={})
    site.rel=lambda target,page:Site.rel(site,target,page)
    site.write=lambda path,text:Site.write(site,path,text)
    site.page=lambda path,title,body,source=None:Site.page(site,path,title,body,source)
    site.read_source=lambda entry:Site.read_source(site,entry)
    reader=ReadingDocuments.__new__(ReadingDocuments);reader.site=site
    receipt=json.loads((ROOT/'manifests/source-imports/paper-xi.json').read_bytes())
    reader.owned={'papers/paper-xi/current/'+e['path']:
        dict(e,repository_path='papers/paper-xi/current/'+e['path'],work='paper-xi') for e in receipt['files']}
    reader.records={};reader.images={};reader.inclusions={};reader.learning={'learning_topics':[]}
    reader.manuscript_roots={'paper-xi':MAIN};reader.claims_by_module={};reader.claims_by_source={}
    for row in json.loads((ROOT/'manifests/claim-navigation.json').read_bytes())['records']:
        if row['statement_path'].startswith(BASE):
            reader.claims_by_source.setdefault(row['statement_path'],[]).append(row)
    reader.add(MAIN)
    reader.add('papers/paper-xi/current/publication/pdfs/Paper_XI_Traditional_v1.1.0.pdf','Read PDF')
    with patch.object(reading,'BOOKS',{'paper-xi':BOOK}):reading.prepare(reader)
    return reader


class PaperXIReadingTests(unittest.TestCase):
    def test_complete_sources_numbering_and_literal_derivations(self):
        load=lambda path:(ROOT/path).read_text(encoding='utf-8-sig')
        self.assertEqual(source_specs(load),CHAPTERS)
        for source in {s['source'] for s in CHAPTERS}:
            specs=[s for s in CHAPTERS if s['source']==source];text=load(source)
            expected=text.split(r'\begin{document}',1)[1] if source==MAIN else text
            self.assertEqual([m for spec in specs for m in source_math(text,spec)],source_math(expected,{}),source)
        with tempfile.TemporaryDirectory() as folder:
            reader=reader_fixture(Path(folder));chapters=reader.readable_books['paper-xi']['chapters']
            nodes=[n for _,_,c in chapters for n in c.nodes]
            self.assertEqual(sum(n['kind']=='proof' for n in nodes),68)
            self.assertEqual(sum(n['kind']=='figure' for n in nodes),16)
            self.assertEqual([n['number'] for n in nodes if n['kind']=='section' and n['number']],
                [str(i) for i in range(1,20)]+list('ABCDEFGHIJKLMNO'))
            printed=dict(re.findall(r'\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}',load(AUX)))
            for node in nodes:
                if node['kind'] not in reading.NUMBERED|set(reading.HEADINGS)|{'figure','table'}:continue
                for label in node['labels']:
                    if label in printed:self.assertEqual(node['number'],printed[label],label)
            conjecture=next(n for n in nodes if 'conj:arithmetic_realization' in n['labels'])
            self.assertEqual((conjecture['kind'],conjecture['number']),('conjecture','66'))
            bib_numbers=dict(re.findall(r'\\bibcite\{([^{}]+)\}\{([^{}]+)\}',load(AUX)))
            self.assertEqual({r['key']:str(i) for i,r in enumerate(reader.readable_books['paper-xi']['references'],1)},bib_numbers)
            for spec,raw,chapter in chapters:
                selected=reading.chapter_text(raw.decode('utf-8-sig'),spec)
                literal=re.findall(r'\\begin\{Verbatim\}\[[^\n]*\](.*?)\\end\{Verbatim\}',selected,re.S)
                self.assertEqual(re.findall(r'\\begin\{verbatim\}(.*?)\\end\{verbatim\}',chapter.text,re.S),literal,spec['url'])

    def test_equations_proof_links_figures_tables_and_companions(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()),images=list(reader.images.values()))
            with patch.object(reading,'CHAPTERS',CHAPTERS),patch.object(reading,'BOOKS',{'paper-xi':BOOK}):
                count=check_readable_chapter(output,documents,pages)
            self.assertEqual(count,1030)
            reports=json.loads((output/'documents/readable-chapters.json').read_bytes())
            self.assertEqual(len(reports),38)
            self.assertEqual(sum(n['kind'] in {'tabular','longtable'} for r in reports for n in r['nodes']),5)
            for spec in CHAPTERS:
                page=pages[spec['url']];markup=(output/spec['url']).read_text(encoding='utf-8')
                self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
                self.assertEqual(len(page.ids),len(set(page.ids)))
                self.assertNotIn('komorebi.invalid',markup)
                for link in page.links:
                    p=urlsplit(link)
                    if p.scheme or p.netloc:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(spec['url']),unquote(p.path))) if p.path else spec['url']
                    if target in pages and p.fragment and not p.query:self.assertIn(unquote(p.fragment),pages[target].ids,(spec['url'],link))
            self.assertEqual(len(reader.images),16)
            for image in reader.images.values():
                self.assertEqual(hashlib.sha256((output/image['file_url']).read_bytes()).hexdigest(),image['sha256'])
            self.assertEqual(verify_bibliography(output,documents,pages)['entries'],29)
            self.assertIn('#page=6',(output/'read/paper-xi/reading-routes.html').read_text(encoding='utf-8'))
            for spec,raw,chapter in reader.readable_books['paper-xi']['chapters']:
                markup=(output/spec['url']).read_text(encoding='utf-8')
                actual=[html.unescape(t) for t in re.findall(r'<pre[^>]*><code>(.*?)</code></pre>',markup,re.S)]
                self.assertEqual(actual,[t.strip('\n') for t in re.findall(r'\\begin\{verbatim\}(.*?)\\end\{verbatim\}',chapter.text,re.S)])
                if actual:self.assertIn('aria-label="Original literal derivation"',markup)

    def test_changed_inputs_and_literal_control(self):
        def changed(path):
            text=(ROOT/path).read_text(encoding='utf-8-sig')
            return text.replace(r'\input{appendices/odd_tower}',r'\input{unreviewed}') if path==MAIN else text
        with self.assertRaisesRegex(ValueError,'manuscript input order'):source_specs(changed)
        text='\\begin{Verbatim}[fontsize=\\small,breaklines=true,breakanywhere=true]\n100% literal $x$ \\textless \\input{reader_route}\n\\end{Verbatim}'
        converted=normalize(text)
        self.assertEqual(converted.count('\n'),text.count('\n'))
        self.assertEqual(reading.original_math(converted),[])
        self.assertIn('100% literal $x$ \\textless \\input{reader_route}',converted)




def publish_fixture(output):
    reader=reader_fixture(output)
    with patch.object(reading,'BOOKS',{'paper-xi':BOOK}):reading.render(reader)
    for record in reader.records.values():
        raw=reader.site.read_source(record);dest=output/record['file_url']
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        if record['format']=='source':
            reader.site.page(record['url'],record['title'],'<h1>'+record['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader


if __name__=='__main__':unittest.main()
