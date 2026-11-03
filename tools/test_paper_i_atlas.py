"""Complete Paper I atlas production rendering, source and manuscript routes."""
import json
from pathlib import Path
import posixpath
import re
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import paper_i_atlas as atlas
import readable_chapters as chapters
from build_reader_site import Site
from check_reader_site import Page
from reader_documents import ReadingDocuments,source_lines

ROOT=Path(__file__).resolve().parents[1]


def reader_fixture(output):
    site=SimpleNamespace(root=ROOT,output=output,revision='paper-i-atlas-test',
        search=[],cache=None,assessments={},editorial_editions={})
    site.rel=lambda target,page:Site.rel(site,target,page)
    site.write=lambda path,text:Site.write(site,path,text)
    site.page=lambda path,title,body,source=None:Site.page(site,path,title,body,source)
    site.read_source=lambda record:Site.read_source(site,record)
    reader=ReadingDocuments.__new__(ReadingDocuments);reader.site=site
    receipt=json.loads((ROOT/'manifests/source-imports/paper-i.json').read_bytes())
    reader.owned={('papers/paper-i/current/'+r['path']):dict(r,repository_path='papers/paper-i/current/'+r['path'],work='paper-i') for r in receipt['files']}
    reader.records={};reader.images={};reader.inclusions={};reader.claims_by_module={}
    reader.learning={'learning_topics':[]};reader.manuscript_roots={'paper-i':atlas.BOOK['main']}
    reader.claims_by_source={}
    for row in json.loads((ROOT/'manifests/claim-navigation.json').read_bytes())['records']:
        if row['statement_path'].startswith(atlas.BOOK['base']):
            reader.claims_by_source.setdefault(row['statement_path'],[]).append(row)
    reader.add(atlas.BOOK['main']);reader.add(atlas.PDF,'Read PDF')
    with patch.object(chapters,'BOOKS',{'paper-i':atlas.BOOK}):chapters.prepare(reader)
    return reader


def publish(output):
    reader=reader_fixture(output);reader.work_routes=lambda work,page:''
    atlas.prepare(reader)
    with patch.object(chapters,'BOOKS',{'paper-i':atlas.BOOK}):chapters.render(reader)
    atlas.render(reader)
    for record in list(reader.records.values()):
        raw=reader.site.read_source(record)
        target=output/record['file_url'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        if record['format']=='source':reader.site.page(record['url'],record['title'],'<h1>Source</h1>'+source_lines(raw.decode('utf-8-sig')))
    shutil.copytree(ROOT/'website/assets',output/'assets',dirs_exist_ok=True)
    documents=dict(source_revision=reader.site.revision,files=list(reader.records.values()))
    pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
    return reader,documents,pages


class PaperIAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.output=Path(cls.temp.name)
        cls.reader,cls.documents,cls.pages=publish(cls.output)
        cls.report=json.loads((cls.output/atlas.REPORT).read_bytes())

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_complete_edition_passes_production_verifier(self):
        result=atlas.verify(self.output,self.documents,self.pages)
        self.assertEqual(result['html_plates'],22)
        self.assertEqual(result['drawings'],20)
        self.assertEqual(result['transcribed_labels'],435)
        self.assertEqual(result['math_expressions'],699)

    def test_metadata_mathematics_and_theorem_labels_are_retained(self):
        for number in (3,6):
            body=(self.output/atlas.plate_url(number)).read_text(encoding='utf-8')
            metadata=body.split('<article id="chapter-text"',1)[0]
            self.assertIn('class="arithmatex"',metadata)
        for plate in self.reader.paper_i_atlas['plates']:
            body=(self.output/plate['url']).read_text(encoding='utf-8')
            self.assertNotIn(r'\cref{',body)
            self.assertIn('page='+str(plate['number']+82),body)
            for label,target in self.report['manuscript_references'][str(plate['number'])]:
                chapter,anchor=target.split('#')
                self.assertIn(anchor,self.pages[chapter].ids)
                self.assertIn(posixpath.relpath(target,posixpath.dirname(plate['url'])),self.pages[plate['url']].links)
                self.assertIn(posixpath.relpath(plate['url'],posixpath.dirname(chapter)),self.pages[chapter].links)

    def test_every_drawing_label_occurs_once_in_reading_order(self):
        for name,figure in self.report['figures'].items():
            self.assertEqual(sorted(figure['node_order']),list(range(len(figure['nodes']))),name)
            body=(self.output/atlas.plate_url(figure['plate'])).read_text(encoding='utf-8')
            self.assertEqual(body.count('id="drawing-label-'),len(figure['nodes']),name)
        for number,anchor in atlas.TABLE_AIDS:
            body=(self.output/atlas.plate_url(number)).read_text(encoding='utf-8')
            self.assertIn('id="'+anchor+'"',body)
            self.assertIn('scope="row"',body)
            self.assertIn('scope="col"',body)

    def test_changed_math_and_numbering_require_review(self):
        source=(ROOT/atlas.SOURCE).read_text(encoding='utf-8-sig')
        with self.assertRaisesRegex(ValueError,'numbering'):atlas.plates(source.replace(r'\vpage{3}',r'\vpage{30}',1))
        from paper_i_atlas_drawings import drawing_nodes
        with self.assertRaisesRegex(ValueError,'transcript'):
            drawing_nodes(r'\node at (0,0) {$x$}; $y$')
        path=self.output/atlas.plate_url(6);original=path.read_text(encoding='utf-8')
        changed,count=re.subn(r'(<(?:span|div) class="arithmatex">\\[\[(])',lambda m:m[0]+'0+',original,count=1)
        self.assertEqual(count,1);path.write_text(changed,encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):atlas.verify(self.output,self.documents,self.pages)
        finally:path.write_text(original,encoding='utf-8')

    def test_wrong_but_reachable_manuscript_target_is_rejected(self):
        path=self.output/atlas.REPORT;original=path.read_bytes()
        report=json.loads(original)
        report['manuscript_references']['3']=report['manuscript_references']['19']
        path.write_text(json.dumps(report),encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):atlas.verify(self.output,self.documents,self.pages)
        finally:path.write_bytes(original)


if __name__=='__main__':unittest.main()
