"""Guard the reconstructed edition and reconciled crosswalk against regressions."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

from build_reader_site import Site
from check_reader_site import Page
from reader_documents import ReadingDocuments, source_lines
import readable_chapters as chapters
import reader_atlas as atlas
from visual_guide_provenance import check, validate_file, IV_BASE, IV_PDF

ROOT=Path(__file__).resolve().parents[1]


class VisualProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.output=Path(cls.temp.name)
        site=SimpleNamespace(root=ROOT,output=cls.output,revision='visual-provenance-test',search=[],cache=None,assessments={},editorial_editions={})
        for name in ('rel','write','page','read_source'):
            setattr(site,name,lambda *args,_method=getattr(Site,name),**kwargs:_method(site,*args,**kwargs))
        reader=ReadingDocuments.__new__(ReadingDocuments);reader.site=site
        receipt=json.loads((ROOT/'manifests/source-imports/paper-iv.json').read_bytes())
        reader.owned={receipt['destination']+'/'+r['path']:dict(r,repository_path=receipt['destination']+'/'+r['path'],work='paper-iv') for r in receipt['files']}
        reader.records={};reader.images={};reader.inclusions={};reader.claims_by_module={};reader.claims_by_source={}
        reader.learning={'learning_topics':[]};reader.manuscript_roots={}
        reader.add(chapters.FOURTH_MAIN)
        reader.work_routes=lambda work,page:''
        with patch.object(chapters,'BOOKS',{'paper-iv':chapters.BOOKS['paper-iv']}):
            chapters.prepare(reader)
            atlas.prepare(reader)
            chapters.render(reader)
        atlas.render(reader)
        for record in reader.records.values():
            raw=site.read_source(record);target=cls.output/record['file_url'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            if record['format']=='source':site.page(record['url'],record['title'],'<h1>Source</h1>'+source_lines(raw.decode('utf-8-sig')))
        shutil.copytree(ROOT/'website/assets',cls.output/'assets',dirs_exist_ok=True)
        cls.reader=reader
        cls.documents=dict(files=list(reader.records.values()))
        cls.pages={p.relative_to(cls.output).as_posix():Page(p.read_text(encoding='utf-8')) for p in cls.output.rglob('*.html')}

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_current_sources_pass_production_math_and_route_verifier(self):
        result=atlas.verify(self.output,self.documents,self.pages)
        self.assertEqual((result['plates'],result['drawings']),(26,24))

    def test_online_guide_contains_the_later_pdf_corrections(self):
        tangent=(self.output/atlas.plate_url(12)).read_text(encoding='utf-8')
        evidence=(self.output/atlas.plate_url(26)).read_text(encoding='utf-8')
        self.assertIn('General complex powers retain the stated branch convention',tangent)
        self.assertNotIn('these meromorphic expressions have poles',tangent)
        self.assertIn('Current formal audit',evidence)
        self.assertIn('Historical certificates',evidence)
        self.assertIn('symbolic suites were hash-validated',evidence)
        pdf=self.reader.records[IV_PDF]
        self.assertIn('page=14',tangent)
        self.assertIn(pdf['git_blob_sha1'],tangent)

    def test_source_download_contains_every_reviewed_input_and_font(self):
        record=check(ROOT)
        archive=self.output/'downloads/paper-iv-visual-reconstructed-sources.zip'
        with zipfile.ZipFile(archive) as source:
            for item in record['works']['paper-iv']['published_files']:
                self.assertEqual(hashlib.sha256(source.read(item['path'][len(IV_BASE):])).hexdigest(),item['sha256'])
            for name in ('main.tex','pages.tex','build.py','fonts/P052-Roman.otf','fonts/latinmodern-math.otf','fonts/URW-FONT-LICENSE.txt'):
                self.assertIn(name,source.namelist())

    def test_reconciled_crosswalk_preserves_all_targets_and_original_records(self):
        record=check(ROOT)
        iv=record['works']['paper-iv'];viii=record['works']['paper-viii']
        self.assertEqual(iv['status'],'resolved-by-reconstructed-edition')
        self.assertEqual(viii['status'],'resolved-by-new-crosswalk-revision')
        self.assertEqual(viii['original_crosswalk']['sha256'],'99d61945f6b8c322c650f254195e595297d65800ec51a558304e29d6cc142f9b')

    def test_changed_source_bytes_are_rejected(self):
        item=check(ROOT)['works']['paper-iv']['source']
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);path=root/item['path'];path.parent.mkdir(parents=True)
            path.write_bytes((ROOT/item['path']).read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'identity changed'):validate_file(root,item)


if __name__=='__main__':unittest.main()
