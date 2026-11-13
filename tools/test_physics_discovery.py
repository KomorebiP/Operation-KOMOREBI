"""Physics reading coverage and complete-volume discovery boundaries."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from check_reader_site import Page
from physics_discovery import counts,destination,verify,REPORT,GUIDE
from physics_reading import BOOK,PAGE_MAP,WORK
from test_physics_reading import ROOT,publish_fixture


class PhysicsDiscoveryTests(unittest.TestCase):
    def test_every_assembled_entry_has_an_html_destination(self):
        manifest=json.loads((ROOT/PAGE_MAP).read_bytes())
        self.assertEqual(counts(),dict(treatments=160,visual=72,verification=73,plates=60,total=305))
        self.assertFalse(BOOK['partial'])
        self.assertEqual(BOOK['main_chapters'],160)
        self.assertEqual(len(manifest),21)
        self.assertEqual({row['part'] for row in manifest},set('I II III IV V VI'.split()))
        self.assertEqual(len({(row['part'],destination(row)['url']) for row in manifest}),21)
        with self.assertRaisesRegex(ValueError,'Unmapped Physics book entry'):
            destination(dict(stem='Unreviewed_New_Chapter',part='VI'))

    def test_publication_inventory_and_missing_continuation_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()),source_revision=reader.site.revision)
            self.assertEqual(verify(output,documents,pages),dict(entries=21,pages=305,math_expressions=7571))
            report=json.loads((output/REPORT).read_bytes());report['entries'][0]['pdf_page']+=1
            (output/REPORT).write_text(json.dumps(report),encoding='utf-8')
            with self.assertRaises(AssertionError):verify(output,documents,pages)
            report['entries'][0]['pdf_page']-=1;(output/REPORT).write_text(json.dumps(report),encoding='utf-8')
            row=report['entries'][0];target=row['html'].removeprefix('read/monographs-physics/')
            pages[BOOK['index']].links=[p for p in pages[BOOK['index']].links if p!=target]
            with self.assertRaises(AssertionError):verify(output,documents,pages)
            library=(output/'read/index.html').read_text(encoding='utf-8')
            self.assertIn('305 reading pages: 160 treatments, 72 visual studies and 73 verification pages',library)
            self.assertIn('Verification and sources',library)
            self.assertNotIn('opening selection',library)

    def test_physics_paths_link_all_formats_and_preserve_other_guides(self):
        from test_reading_paths import fixture
        from reading_paths import guide_model,eligible_books
        reader=fixture(Path('unused'))
        components=reader.site.registry['components']
        with patch.dict(BOOK,partial=True):
            previous={c['id']:guide_model(reader,c) for c in components if c['id'] in eligible_books()}
        current={c['id']:guide_model(reader,c) for c in components if c['id'] in eligible_books()}
        self.assertEqual({k:v for k,v in current.items() if k!=WORK},previous)
        model=current[WORK];self.assertEqual(model['url'],GUIDE)
        targets={s['url'] for path in model['paths'] for s in path['steps']}
        self.assertTrue({BOOK['index'],BOOK['atlas_index'],BOOK['verification_index']}<=targets)
        from physics_companions import metadata
        data=metadata()
        for c in data['companions']:
            self.assertIn(next(p['url'] for p in data['pages'] if p['companion']==c['id']),targets)
        self.assertEqual(model['scope'],reader.site.assessments[WORK]['scope'])
        from reader_documents import ReadingDocuments
        self.assertIn(WORK,ReadingDocuments.document_works(reader,'collection','docs/PHYSICS_COLLECTION.md'))


if __name__=='__main__':unittest.main()
