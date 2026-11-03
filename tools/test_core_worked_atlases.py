"""Production source, formula and manuscript-route checks for Papers II/III."""
import json
from pathlib import Path
import re
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from core_worked_atlases import ATLASES
import readable_chapters as chapters
from build_reader_site import Site
from check_reader_site import Page
from reader_documents import ReadingDocuments,source_lines
from worked_atlas_drawings import drawing_nodes

ROOT=Path(__file__).resolve().parents[1]


def publish(work,output,atlas=None):
    atlas=atlas or ATLASES[work]
    site=SimpleNamespace(root=ROOT,output=output,revision='worked-atlas-test',search=[],cache=None,assessments={},editorial_editions={})
    for name in ('rel','write','page','read_source'):
        setattr(site,name,lambda *args,_method=getattr(Site,name),**kwargs:_method(site,*args,**kwargs))
    reader=ReadingDocuments.__new__(ReadingDocuments);reader.site=site
    receipt=json.loads((ROOT/('manifests/source-imports/'+work+'.json')).read_bytes())
    reader.owned={('papers/'+work+'/current/'+r['path']):dict(r,repository_path='papers/'+work+'/current/'+r['path'],work=work) for r in receipt['files']}
    reader.records={};reader.images={};reader.inclusions={};reader.claims_by_module={};reader.claims_by_source={}
    reader.learning={'learning_topics':[]};reader.manuscript_roots={work:atlas.BOOK['main']}
    for row in json.loads((ROOT/'manifests/claim-navigation.json').read_bytes())['records']:
        if row['statement_path'].startswith(atlas.BOOK['base']):reader.claims_by_source.setdefault(row['statement_path'],[]).append(row)
    reader.add(atlas.BOOK['main']);reader.add(atlas.PDF,'Read PDF')
    with patch.object(chapters,'BOOKS',{work:atlas.BOOK}):chapters.prepare(reader)
    reader.work_routes=lambda work,page:''
    atlas.prepare(reader)
    with patch.object(chapters,'BOOKS',{work:atlas.BOOK}):chapters.render(reader)
    atlas.render(reader)
    for record in list(reader.records.values()):
        raw=site.read_source(record);target=output/record['file_url'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        if record['format']=='source':site.page(record['url'],record['title'],'<h1>Source</h1>'+source_lines(raw.decode('utf-8-sig')))
    shutil.copytree(ROOT/'website/assets',output/'assets',dirs_exist_ok=True)
    documents=dict(source_revision=site.revision,files=list(reader.records.values()))
    pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
    return reader,documents,pages


class CoreWorkedAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.output=Path(cls.temp.name);cls.fixtures={}
        for work in ATLASES:cls.fixtures[work]=publish(work,cls.output)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_complete_editions_pass_production_verifier(self):
        for work,atlas in ATLASES.items():
            with self.subTest(work=work):
                _,documents,pages=self.fixtures[work]
                result=atlas.verify(self.output,documents,pages)
                self.assertEqual(result['html_plates'],24);self.assertEqual(result['drawings'],22)
                labels,math,links={'paper-ii':(754,1043,40),'paper-iii':(488,747,44)}[work]
                self.assertEqual((result['transcribed_labels'],result['math_expressions'],result['return_links']),(labels,math,links))

    def test_subject_search_titles_retain_original_pdf_label_searches(self):
        for work,atlas in ATLASES.items():
            reader,_,_=self.fixtures[work]
            entry=next(r for r in reader.site.search if r['url']==atlas.plate_url(3))
            self.assertTrue(entry['title'].startswith(atlas.label+' visual guide / '))
            self.assertNotIn('/ V3:',entry['title'])
            self.assertIn('Visual 3 V3',entry['text'])

    def test_every_label_and_source_table_is_present(self):
        for work,atlas in ATLASES.items():
            report=json.loads((self.output/atlas.REPORT).read_bytes())
            for name,figure in report['figures'].items():
                with self.subTest(work=work,drawing=name):
                    self.assertEqual(sorted(figure['node_order']),list(range(len(figure['nodes']))))
                    body=(self.output/atlas.plate_url(figure['plate'])).read_text(encoding='utf-8')
                    self.assertEqual(body.count('id="drawing-label-'),len(figure['nodes']))
            for number,anchor in atlas.TABLE_AIDS:
                body=(self.output/atlas.plate_url(number)).read_text(encoding='utf-8')
                self.assertIn('id="'+anchor+'"',body);self.assertIn('scope="row"',body);self.assertIn('scope="col"',body)

    def test_multiline_label_retains_both_formulas(self):
        from readable_chapters import original_math
        source=r'\node at (0,0) {\shortstack{$2E_+$ integral\\$E_+$ not integral}};'
        nodes=drawing_nodes(source)
        self.assertEqual([m for node in nodes for m in original_math(node['text'])],['2E_+','E_+'])
        self.assertNotIn(r'\shortstack',nodes[0]['text'])
        with self.assertRaisesRegex(ValueError,'transcript'):drawing_nodes(r'\node at (0,0) {$x$}; $y$')

    def test_current_scope_input_is_preserved(self):
        atlas=ATLASES['paper-ii'];body=(self.output/atlas.plate_url(24)).read_text(encoding='utf-8')
        self.assertIn('53 of 53 proof-level source records',body)
        self.assertIn('not counts of independent discoveries',body)

    def test_changed_formula_and_wrong_reachable_target_are_rejected(self):
        for work,atlas in ATLASES.items():
            _,documents,pages=self.fixtures[work]
            path=self.output/atlas.plate_url(3);original=path.read_bytes()
            changed,count=re.subn(r'(<(?:span|div) class="arithmatex">\\[\[(])',lambda m:m[0]+'0+',original.decode(),count=1)
            self.assertEqual(count,1);path.write_text(changed,encoding='utf-8')
            try:
                with self.assertRaises(AssertionError):atlas.verify(self.output,documents,pages)
            finally:path.write_bytes(original)
            path=self.output/atlas.REPORT;original=path.read_bytes();report=json.loads(original)
            report['manuscript_references']['3']=report['manuscript_references']['19'];path.write_text(json.dumps(report),encoding='utf-8')
            try:
                with self.assertRaises(AssertionError):atlas.verify(self.output,documents,pages)
            finally:path.write_bytes(original)

    def test_renumbered_plate_is_rejected(self):
        for atlas in ATLASES.values():
            source=(ROOT/atlas.SOURCE).read_text(encoding='utf-8-sig')
            with self.assertRaisesRegex(ValueError,'numbering'):atlas.plates(source.replace(r'\vpage{3}',r'\vpage{30}',1))

    def test_omitted_scope_input_is_rejected(self):
        atlas=ATLASES['paper-ii'];_,documents,pages=self.fixtures['paper-ii']
        path=self.output/atlas.REPORT;original=path.read_bytes();report=json.loads(original)
        report['included_sources']={};path.write_text(json.dumps(report),encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):atlas.verify(self.output,documents,pages)
        finally:path.write_bytes(original)


if __name__=='__main__':unittest.main()
