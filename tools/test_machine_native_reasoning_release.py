"""A synchronized release must bind its PDF, source, web text and old edition."""
from io import BytesIO
import hashlib,json,tempfile,unittest,zipfile
from pathlib import Path
from machine_native_reasoning_release import load,verify,MANIFEST,PDF_SHA256,SOURCE_SHA256,HISTORICAL_BOOK,HISTORICAL_RECORD
from machine_native_reasoning_expanded import artifact_bytes,publish,RECORD,BOOK
from test_machine_native_reasoning_expanded import fixture
from check_reader_site import Page
ROOT=Path(__file__).resolve().parents[1]

class SynchronizedMNRTests(unittest.TestCase):
    def test_source_is_bound_to_pdf_and_rebuilt_inputs(self):
        data=load(ROOT);raw=artifact_bytes(ROOT,data['assets']['source'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(),SOURCE_SHA256)
        with zipfile.ZipFile(BytesIO(raw)) as z:
            edition=json.loads(z.read('EDITION.json'));rebuild=json.loads(z.read('provenance/CLEAN_REBUILD.json'))
            self.assertEqual(edition['pdf_sha256'],PDF_SHA256)
            self.assertEqual(edition['version'],'1.0.0')
            web=json.loads((ROOT/data['html_manifest']).read_bytes())
            self.assertEqual(len(web['sources']),13)
            for source in web['sources']:
                raw=z.read(source['path'].removeprefix('source/'))
                self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sha256'])
                self.assertEqual((ROOT/source['repository_path']).read_bytes(),raw)
            self.assertTrue(rebuild['all_page_text_geometry_and_pixels_equal_36dpi'])
            for name,digest in rebuild['build_input_sha256'].items():self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),digest,name)
            review=json.loads(z.read('provenance/BRIDGE_SELF_REVIEW.json'))
            self.assertFalse(review['independent']);self.assertEqual(len(review['claims']),7)
    def test_published_readers_retain_both_editions(self):
        with tempfile.TemporaryDirectory() as tmp:
            site=fixture(tmp,True);publish(site);result=verify(tmp)
            self.assertTrue(result['historical_edition_preserved'])
            record=json.loads((Path(tmp)/RECORD).read_bytes());old=json.loads((Path(tmp)/HISTORICAL_RECORD).read_bytes())
            self.assertEqual(record['version'],'1.0.0');self.assertNotEqual(old['pdf_sha256'],record['pdf_sha256'])
            for path in [BOOK,HISTORICAL_BOOK]:
                markup=(Path(tmp)/path).read_text(encoding='utf-8');parsed=Page(markup)
                self.assertEqual(parsed.h1,1);self.assertEqual(parsed.main,1)
                self.assertTrue(any(url.endswith('/'+path) for url in parsed.canonicals),path)
            self.assertIn('mnr-reconstructed-2026-11-04.json',(Path(tmp)/HISTORICAL_BOOK).read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
