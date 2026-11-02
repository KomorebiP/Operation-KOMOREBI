"""End-to-end source preservation for both foundational books."""
import json
from pathlib import Path
import posixpath
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import readable_chapters as reading
from foundational_reading import BOOKS,CHAPTERS,source_specs,source_math,normalize
from build_reader_site import Site
from reader_documents import ReadingDocuments,source_lines
from check_reader_site import Page,check_readable_chapter
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]

def reader_fixture(output):
    site=SimpleNamespace(root=ROOT,output=output,revision='foundational-conversion-test',search=[],cache=None,assessments={},editorial_editions={})
    for name in ('rel','write','page','read_source'):
        setattr(site,name,lambda *args,_name=name,**kwargs:getattr(Site,_name)(site,*args,**kwargs))
    reader=ReadingDocuments.__new__(ReadingDocuments);reader.site=site
    reader.owned={};reader.records={};reader.images={};reader.inclusions={}
    reader.learning={'learning_topics':[]};reader.claims_by_module={};reader.claims_by_source={}
    reader.manuscript_roots={work:c['main'] for work,c in BOOKS.items()}
    for work in BOOKS:
        receipt=json.loads((ROOT/f'manifests/source-imports/{work}.json').read_bytes())
        for e in receipt['files']:
            path='monographs/'+work+'/'+e['path']
            reader.owned[path]=dict(e,repository_path=path,work=work)
    with patch.object(reading,'BOOKS',BOOKS):reading.prepare(reader)
    return reader

def publish_fixture(output):
    reader=reader_fixture(output)
    with patch.object(reading,'BOOKS',BOOKS):reading.render(reader)
    for r in reader.records.values():
        raw=reader.site.read_source(r);dest=output/r['file_url'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        if r['format']=='source':reader.site.page(r['url'],r['title'],'<h1>'+r['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader

class FoundationalReadingTests(unittest.TestCase):
    def test_complete_retained_sources_and_fail_closed(self):
        load=lambda path:(ROOT/path).read_text(encoding='utf-8-sig')
        for config in BOOKS.values():
            self.assertEqual(source_specs(load,config),config['chapters'])
            for spec in config['chapters']:
                selected=reading.chapter_text(load(spec['source']),spec)
                self.assertEqual(reading.original_math(normalize(selected,config['work'])),source_math(load(spec['source']),spec))
            with self.assertRaisesRegex(ValueError,'changed foundational source'):
                source_specs(lambda path:load(path)+'unreviewed text',config)
        self.assertEqual(reading.original_math(r'row\\[3pt] next $x$'),['x'])

    def test_publication_math_links_and_structure(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            docs=dict(files=list(reader.records.values()),images=list(reader.images.values()))
            pdf_pages={r['url'] for r in reader.records.values() if r['format']=='pdf'}
            with patch.object(reading,'BOOKS',BOOKS),patch.object(reading,'CHAPTERS',CHAPTERS):
                count=check_readable_chapter(output,docs,pages)
            self.assertGreater(count,1500)
            reports=json.loads((output/'documents/readable-chapters.json').read_bytes())
            self.assertEqual(len(reports),len(CHAPTERS))
            for spec in CHAPTERS:
                page=pages[spec['url']]
                self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
                self.assertEqual(len(page.ids),len(set(page.ids)))
            for name,page in pages.items():
                for link in page.links:
                    parts=urlsplit(link)
                    if parts.scheme or parts.netloc:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(parts.path))) if parts.path else name
                    if any(target.startswith('read/'+work+'/') for work in BOOKS):
                        self.assertIn(target,set(pages)|pdf_pages,(name,link,'Missing book reading page'))
                    if target in pages and parts.fragment and not parts.query:
                        self.assertIn(unquote(parts.fragment),pages[target].ids,(name,link))
            nodes=[n for r in reports for n in r['nodes']]
            self.assertEqual(sum(n['kind']=='proof' for n in nodes),137)
            self.assertEqual(sum(n['kind']=='figure' for n in nodes),46)
            self.assertEqual(sum(len(c.proof_pairs) for b in reader.readable_books.values() for _,_,c in b['chapters']),137)
            from statement_navigation import check_directory
            for work,config in BOOKS.items():
                directory=reading.statement_directory_url(config)
                self.assertIn(directory,pages)
                chapters=[(s['url'],(output/s['url']).read_text(encoding='utf-8')) for s in config['chapters']]
                result=check_directory((output/directory).read_text(encoding='utf-8'),chapters,directory)
                self.assertEqual(result['proof_links'],92 if work=='komorebi-space' else 45)
            space=reader.readable_books['komorebi-space']['chapters'][0][2]
            self.assertEqual(space.labels['KS01']['number'],'1.3')
            self.assertEqual(space.labels['WR10']['number'],'30.1')
            self.assertEqual(space.equation_numbers['eq:ambient'],'1.1')
            for spec in CHAPTERS:
                markup=(output/spec['url']).read_text(encoding='utf-8')
                self.assertIn('reading-text-size',markup)
                self.assertIn('Switch work',markup)

if __name__=='__main__':unittest.main()
