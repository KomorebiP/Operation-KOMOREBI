"""The expanded edition must publish the verified bytes without promoting scope."""
from copy import deepcopy
import hashlib,json,posixpath,re,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import unquote,urlsplit,parse_qs
from machine_native_reasoning_expanded import (PAGE,MANIFEST,RECORD,PDF_SHA256,SOURCE_SHA256,
    load_manifest,artifact_bytes,publish,verify,teaser)
from reader_documents import ReadingDocuments
from check_reader_site import Page
ROOT=Path(__file__).resolve().parents[1]

def fixture(output,full_chrome=False):
    from build_reader_site import Site
    site=SimpleNamespace(root=ROOT,output=Path(output),revision='expanded-mnr-preview',search=[],
      registry={'components':[]},assessments={},components={},documents={},reader=None)
    site.rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page) or '.')
    site.write=lambda path,text:((site.output/path).parent.mkdir(parents=True,exist_ok=True),(site.output/path).write_text(text,encoding='utf-8'))
    site.page=(lambda *args,**kwargs:Site.page(site,*args,**kwargs)) if full_chrome else lambda page,title,body,*args:site.write(page,'<html lang="en"><head><title>'+title+'</title></head><body><main id="main">'+body+'</main></body></html>')
    site.reader=SimpleNamespace(site=site)
    site.reader.viewer_url=lambda *args,**kwargs:ReadingDocuments.viewer_url(site.reader,*args,**kwargs)
    return site

class ExpandedMNRTests(unittest.TestCase):
    def test_all_chapters_and_verified_artifacts(self):
        data=load_manifest(ROOT)
        self.assertEqual([c['number'] for c in data['chapters']],list(range(1,98)))
        self.assertEqual(len({c['part'] for c in data['chapters']}),13)
        self.assertEqual(hashlib.sha256(artifact_bytes(ROOT,data['assets']['pdf'])).hexdigest(),PDF_SHA256)
        self.assertEqual(hashlib.sha256(artifact_bytes(ROOT,data['assets']['source'])).hexdigest(),SOURCE_SHA256)

    def test_part_integrity_and_escape_rejected(self):
        asset=deepcopy(load_manifest(ROOT)['assets']['pdf'])
        asset['parts'][0]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'part changed'):artifact_bytes(ROOT,asset)
        asset['parts'][0]['path']='../outside'
        with self.assertRaises(ValueError):artifact_bytes(ROOT,asset)

    def test_incomplete_chapter_manifest_rejected(self):
        data=load_manifest(ROOT);data['chapters'].pop()
        with patch('machine_native_reasoning_expanded.json.loads',return_value=data):
            with self.assertRaisesRegex(ValueError,'97 chapters'):load_manifest(ROOT)

    def test_pdf_reader_routes_and_downloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            site=fixture(tmp);record=publish(site)
            self.assertEqual(verify(tmp)['chapters'],97)
            markup=(Path(tmp)/PAGE).read_text(encoding='utf-8');page=Page(markup)
            self.assertEqual(len([x for x in page.ids if x.startswith('chapter-')]),97)
            self.assertEqual(len(set(page.ids)),len(page.ids))
            urls=[unquote(x) for x in page.links if 'viewer.html' in x]
            self.assertEqual(len(urls),98)
            for chapter in record['chapters']:
                self.assertTrue(any(x.endswith('#page='+str(chapter['physical_page'])) for x in urls))
            self.assertEqual(len(site.search),98)
            self.assertTrue(all(x['work_ids']==['research-machine-native-reasoning-wider'] for x in site.search))
            self.assertFalse(record['new_lean_execution']);self.assertFalse(record['new_proof_review'])
            self.assertIn('not an independent proof audit',markup)
            self.assertEqual(hashlib.sha256((Path(tmp)/record['source_archive']).read_bytes()).hexdigest(),SOURCE_SHA256)

    def test_core_link_remains_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            site=fixture(tmp)
            note=teaser(site,'read/monographs-machine-native-reasoning/start.html')
            self.assertIn('97-chapter',note)
            self.assertIn('separate from the accepted 27-result core',note)

if __name__=='__main__':unittest.main()
