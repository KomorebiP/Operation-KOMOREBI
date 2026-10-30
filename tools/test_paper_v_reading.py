"""Whole-manuscript conversion checks for Paper V and its PDF figure assets."""
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
from paper_v_chapters import BOOK,CHAPTERS,MAIN
from reader_documents import ReadingDocuments, source_lines
from reader_figure_assets import prepare as prepare_figures

ROOT=Path(__file__).resolve().parents[1]

def reader_fixture(output):
    """Use real source receipts and production rendering with one selected book."""
    site=SimpleNamespace(root=ROOT,output=output,revision='paper-v-conversion-test',
                         search=[],cache=None,assessments={},editorial_editions={})
    site.rel=lambda target,page:Site.rel(site,target,page)
    site.write=lambda path,text:Site.write(site,path,text)
    site.page=lambda path,title,body,source=None:Site.page(site,path,title,body,source)
    site.read_source=lambda entry:Site.read_source(site,entry)
    reader=ReadingDocuments.__new__(ReadingDocuments)
    reader.site=site
    receipt=json.loads((ROOT/'manifests/source-imports/paper-v.json').read_bytes())
    reader.owned={('papers/paper-v/current/'+entry['path']):
                  dict(entry,repository_path='papers/paper-v/current/'+entry['path'],work='paper-v')
                  for entry in receipt['files']}
    reader.records={};reader.images={};reader.inclusions={}
    reader.learning={'learning_topics':[]}
    reader.manuscript_roots={'paper-v':MAIN}
    reader.claims_by_module={}
    claims=json.loads((ROOT/'manifests/claim-navigation.json').read_bytes())['records']
    reader.claims_by_source={MAIN:[row for row in claims if row['statement_path']==MAIN]}
    reader.add(MAIN)
    reader.add('papers/paper-v/current/papers/Paper_V_Traditional_Final.pdf','Read PDF')
    with patch.object(chapters,'BOOKS',{'paper-v':BOOK}):
        chapters.prepare(reader)
    return reader

def publish_fixture(output):
    reader=reader_fixture(output)
    with patch.object(chapters,'BOOKS',{'paper-v':BOOK}):
        chapters.render(reader)
    # Copy the receipt-bound original files required by the verification pass.
    for record in reader.records.values():
        path=ROOT/record['repository_path']
        if not path.is_file(): continue
        raw=reader.site.read_source(record)
        target=output/record['file_url'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        if record['format']=='source':
            reader.site.page(record['url'],record['title'],'<h1>'+record['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader

class PaperVReadingTests(unittest.TestCase):
    def test_full_source_ranges_and_original_numbering(self):
        source=(ROOT/MAIN).read_text(encoding='utf-8-sig')
        chapters.validate_monolithic(source,BOOK)
        self.assertEqual(len(CHAPTERS),40)
        self.assertEqual(CHAPTERS[0]['start_line'],217)
        self.assertEqual(CHAPTERS[-1]['end_line'],3808)
        for a,b in zip(CHAPTERS,CHAPTERS[1:]):
            self.assertEqual(a['end_line']+1,b['start_line'])
        broken={**BOOK,'chapters':[dict(s) for s in CHAPTERS]}
        broken['chapters'][1]['start_line']+=1
        with self.assertRaisesRegex(ValueError,'gap or overlap'):
            chapters.validate_monolithic(source,broken)
        with self.assertRaisesRegex(ValueError,'section order changed'):
            chapters.validate_monolithic(source.replace(r'\section{Introduction}',r'\section{Changed introduction}'),BOOK)
        state={};parsed=[]
        macros=chapters.manuscript_macros(source,BOOK['macro_contract'])
        for spec in CHAPTERS:
            chapter=chapters.Chapter(chapters.chapter_text(source,spec),macros,state=state,check_refs=False)
            parsed+=chapter.nodes
            state=dict(section=chapter.section,appendix=chapter.appendix,part=chapter.part,section_prefix=chapter.section_prefix)
        numbers=[n['number'] for n in parsed if n['kind']=='section' and n['number']]
        self.assertEqual(numbers,[str(i) for i in range(1,18)]+list('ABCD')+['E'+str(i) for i in range(1,17)])
        self.assertEqual(sum(n['kind']=='proof' for n in parsed),83)
        self.assertEqual(sum(n['kind']=='figure' for n in parsed),35)
        self.assertEqual(sum(n['kind'] in {'table','longtable','tabular'} for n in parsed),10)
        aux=(ROOT/BOOK['base']/'Paper_V_Traditional_Final.aux').read_text(encoding='utf-8-sig')
        expected=dict(re.findall(r'\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}',aux))
        for node in parsed:
            if node['kind'] not in chapters.NUMBERED:continue
            for label in node['labels']:
                if label in expected:self.assertEqual(node['number'],expected[label],label)

    def test_whole_html_equation_sequence_and_every_statement_proof_route(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)
            reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8'))
                   for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()),images=list(reader.images.values()))
            with patch.object(chapters,'CHAPTERS',CHAPTERS),patch.object(chapters,'BOOKS',{'paper-v':BOOK}):
                count=check_readable_chapter(output,documents,pages)
            source=(ROOT/MAIN).read_text(encoding='utf-8-sig')
            self.assertEqual(count,len(chapters.original_math(source.split(r'\begin{document}',1)[1])))
            self.assertEqual(count,1219)
            proofs=[r for r in reader.claims_by_source[MAIN] if r['proof_line']]
            self.assertEqual(len(proofs),83)
            for row in proofs:
                statement=chapters.readable_url(MAIN,row['statement_line'])
                proof=chapters.readable_url(MAIN,row['proof_line'])
                self.assertIsNotNone(statement);self.assertIsNotNone(proof)
                statement_path,statement_id=statement.split('#')
                proof_path,proof_id=proof.split('#')
                self.assertIn('#'+proof_id,pages[statement_path].links)
                self.assertIn('#'+statement_id,pages[proof_path].links)
                self.assertIn(statement_id,pages[statement_path].ids)
                self.assertIn(proof_id,pages[proof_path].ids)
            for spec in CHAPTERS:
                page=pages[spec['url']]
                self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
                self.assertEqual(len(page.ids),len(set(page.ids)))
                for link in page.links:
                    parts=urlsplit(link)
                    if parts.scheme or parts.netloc:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(spec['url']),unquote(parts.path))) if parts.path else spec['url']
                    if target.startswith('read/paper-v/') and target in pages and parts.fragment:
                        self.assertIn(unquote(parts.fragment),pages[target].ids,(spec['url'],link))
            self.assertEqual(len(reader.images),35)
            for record in reader.records.values():
                if record.get('figure_source'):
                    self.assertNotIn(record['url'],pages['read/paper-v/index.html'].links)
            for image in reader.images.values():
                raw=(output/image['file_url']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),image['sha256'])
                self.assertEqual(reader.records[image['source']]['sha256'],image['source_sha256'])
            self.assertTrue(any(item['kind']=='Written proofs' for item in reader.site.search))
            formal=(output/'read/paper-v/formalization.html').read_text(encoding='utf-8')
            self.assertIn('September 2026',formal)
            self.assertIn('does not add a proof review',formal)
            self.assertIn('this atlas is not converted to HTML',(output/'read/paper-v/visual-atlas.html').read_text(encoding='utf-8'))

    def test_bold_tokens_and_spanning_table_cells_retain_math(self):
        source=(ROOT/MAIN).read_text(encoding='utf-8-sig')
        macros=chapters.manuscript_macros(source,BOOK['macro_contract'])
        self.assertIn(r'\boldsymbol{x}',chapters.expand_math(r'\bm x',macros))
        self.assertIn(r'\boldsymbol{\Gamma}',chapters.expand_math(r'\bm\Gamma',macros))
        self.assertIn(r'\boldsymbol{x+y}',chapters.expand_math(r'\bm{x+y}',macros))
        with self.assertRaises(ValueError):chapters.expand_math(r'\norm x',{'norm':dict(arguments=1,body='#1')})
        node=dict(kind='table',body=r'\caption{Record}\begin{tabular}{lll}Case&A&B\\one&\multicolumn{2}{c}{$x$}\\\end{tabular}\label{tab:record}')
        chapter=chapters.Chapter('',{})
        markup=chapters.render_table(node,chapter)
        self.assertIn('colspan="2"',markup)
        self.assertEqual(chapter.math,['x'])
        with self.assertRaises(ValueError):
            chapters.render_table(dict(node,body=node['body'].replace('{2}{c}','{3}{c}')),chapters.Chapter('',{}))
        with self.assertRaises(ValueError):
            chapters.render_table(dict(node,body=node['body']+'omitted prose'),chapters.Chapter('',{}))

    def test_figure_image_and_source_mismatches_are_rejected(self):
        raw=b'%PDF-1.7\nretained figure'
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);asset=root/'website/assets/figures/paper-v'
            asset.mkdir(parents=True)
            (asset/'plot.png').write_bytes(b'changed image')
            record=dict(source=BOOK['base']+'plot.pdf',source_sha256=hashlib.sha256(raw).hexdigest(),
                        image='assets/figures/paper-v/plot.png',image_sha256=hashlib.sha256(b'original image').hexdigest())
            (asset/'figures.json').write_text(json.dumps(dict(figures=[record])))
            site=SimpleNamespace(root=root,read_source=lambda entry:raw)
            reader=SimpleNamespace(site=site,add=lambda path:{'path':path})
            with self.assertRaisesRegex(ValueError,'image differs'):
                prepare_figures(reader,BOOK,[])
            record['source_sha256']='0'*64
            (asset/'figures.json').write_text(json.dumps(dict(figures=[record])))
            with self.assertRaisesRegex(ValueError,'source differs'):
                prepare_figures(reader,BOOK,[])

if __name__=='__main__':unittest.main()
