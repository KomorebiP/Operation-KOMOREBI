"""Source order, proof routes, inline figures, and retained Part I bookmarks."""
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import paper_vii_reading as vii
import readable_chapters as chapters
from build_reader_site import Site
from check_reader_site import Page,check_readable_chapter
from reader_documents import ReadingDocuments,source_lines

ROOT=Path(__file__).resolve().parents[1]


def reader_fixture(output,prepare=True):
    site=SimpleNamespace(root=ROOT,output=output,revision='paper-vii-reader-test',
                         search=[],cache=None,assessments={},editorial_editions={})
    site.rel=lambda target,page:Site.rel(site,target,page)
    site.write=lambda path,text:Site.write(site,path,text)
    site.page=lambda path,title,body,source=None:Site.page(site,path,title,body,source)
    site.read_source=lambda entry:Site.read_source(site,entry)
    reader=ReadingDocuments.__new__(ReadingDocuments);reader.site=site
    receipt=json.loads((ROOT/'manifests/source-imports/paper-vii.json').read_bytes())
    reader.owned={('papers/paper-vii/current/'+r['path']):dict(r,repository_path='papers/paper-vii/current/'+r['path'],work='paper-vii') for r in receipt['files']}
    reader.records={};reader.images={};reader.inclusions={};reader.learning={'learning_topics':[]}
    reader.manuscript_roots={'paper-vii':vii.MAIN};reader.claims_by_module={}
    rows=json.loads((ROOT/'manifests/claim-navigation.json').read_bytes())['records']
    reader.claims_by_source={path:[r for r in rows if r['statement_path']==path] for path in {s['source'] for s in vii.CHAPTERS}}
    reader.add(vii.MAIN)
    reader.add('papers/paper-vii/current/papers/Paper_VII_Traditional_Final.pdf','Read PDF')
    if prepare:
        with patch.object(chapters,'BOOKS',{'paper-vii':vii.BOOK}):chapters.prepare(reader)
    return reader


def publish_fixture(output):
    reader=reader_fixture(output)
    with patch.object(chapters,'BOOKS',{'paper-vii':vii.BOOK}):chapters.render(reader)
    for record in list(reader.records.values()):
        raw=reader.site.read_source(record)
        target=output/record['file_url'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        if record['format']=='source':
            reader.site.page(record['url'],record['title'],'<h1>'+record['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader


class PaperVIIReadingTests(unittest.TestCase):
    def test_repeated_source_preparation_does_not_duplicate_figure_usage(self):
        with tempfile.TemporaryDirectory() as temp:
            reader=reader_fixture(Path(temp))
            with patch.object(chapters,'BOOKS',{'paper-vii':vii.BOOK}):chapters.prepare(reader)
            self.assertEqual(len(reader.paper_vii_figure_usage),38)
            self.assertEqual(len(reader.readable_books['paper-vii']['chapters']),25)

    def test_topic_split_preserves_every_original_node_number_and_math_expression(self):
        core=(ROOT/vii.CORE_SOURCE).read_text(encoding='utf-8-sig')
        vii.validate_core_ranges(core)
        original=vii.CHAPTERS[:2]+[dict(source=vii.BASE+'parts/'+name,part=part,reset_part=i in (0,1,2))
                                  for i,(name,slug,title,part) in enumerate(vii.PARTS)]
        macros=chapters.manuscript_macros((ROOT/vii.MAIN).read_text(encoding='utf-8-sig'))
        def parse(specs):
            state={};nodes=[];math=[]
            for spec in specs:
                if spec.get('reset_part'):state={}
                state.update(part=spec.get('part',0),part_numbering=True)
                raw=chapters.chapter_text((ROOT/spec['source']).read_text(encoding='utf-8-sig'),spec)
                parsed=chapters.Chapter(raw,macros,state=state,check_refs=False)
                nodes.extend((spec['source'],n['kind'],n['id'],n['number'],n['labels']) for n in parsed.nodes)
                math+=chapters.original_math(raw)
                state={k:getattr(parsed,k) for k in ('section','appendix','part','subsection','subsubsection','counter','section_prefix','figure','table','number_floats')}
            return nodes,math
        old_nodes,old_math=parse(original);new_nodes,new_math=parse(vii.CHAPTERS)
        self.assertEqual(new_nodes,old_nodes)
        self.assertEqual(new_math,old_math)
        self.assertEqual(len(new_math),1820)
        self.assertEqual(sum(n[1]=='proof' for n in new_nodes),107)
        self.assertEqual(len(vii.CORE_CHAPTERS),15)
        self.assertEqual(chapters.readable_url(vii.CORE_SOURCE,685),'read/paper-vii/measurements.html#L685')
        self.assertEqual(chapters.readable_url(vii.CORE_SOURCE,736),'read/paper-vii/quantum-channels.html#L736')
        self.assertEqual(chapters.readable_url(vii.CORE_SOURCE,822),'read/paper-vii/error-correction.html#L822')
        with self.assertRaisesRegex(ValueError,'heading'):
            vii.validate_core_ranges(core.replace(r'\subsection{Kraus transfer}',r'\subsection{Changed title}'))

    def test_rendered_figures_math_proof_links_and_old_part_bookmarks(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()),images=list(reader.images.values()))
            with patch.object(chapters,'CHAPTERS',vii.CHAPTERS),patch.object(chapters,'BOOKS',{'paper-vii':vii.BOOK}):
                self.assertEqual(check_readable_chapter(output,documents,pages),1820)
            self.assertEqual(vii.verify_site(output,pages,documents),dict(reading_pages=25,core_topic_pages=15,inline_figures=38,collected_part_pages=1))
            self.assertEqual(len(reader.images),38)
            for spec in vii.CORE_CHAPTERS:
                rows=chapters.chapter_claims(reader,spec)
                for row in rows:
                    if row['proof_line']:
                        page=pages[spec['url']]
                        self.assertIn('#L'+str(row['proof_line']),page.links)
                        self.assertIn('#L'+str(row['statement_line']),page.links)
            for item in reader.images.values():
                self.assertEqual(hashlib.sha256((output/item['file_url']).read_bytes()).hexdigest(),item['sha256'])
                self.assertEqual(reader.records[item['source']]['sha256'],item['source_sha256'])

    def test_pdf_and_image_hashes_and_descriptions_fail_closed(self):
        report=json.loads((ROOT/vii.FIGURE_MANIFEST).read_bytes())
        with tempfile.TemporaryDirectory() as temp:
            for key,value,message in [('source_sha256','0'*64,'PDF differs'),('image_sha256','0'*64,'image differs'),('alt','','description')]:
                changed=json.loads(json.dumps(report));changed['figures'][0][key]=value
                path=Path(temp)/'figures.json';path.write_text(json.dumps(changed),encoding='utf-8')
                reader=reader_fixture(Path(temp),prepare=False)
                with patch.object(vii,'FIGURE_MANIFEST',path),self.assertRaisesRegex(ValueError,message):
                    vii.assets(reader)


if __name__=='__main__':unittest.main()
