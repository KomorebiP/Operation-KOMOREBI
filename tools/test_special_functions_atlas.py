"""Full visual-source coverage, rendering and lossless-image rejection controls."""
import hashlib
import json
from pathlib import Path
import posixpath
import re
import tempfile
from types import SimpleNamespace
import unittest

from PIL import Image
from check_reader_site import Page
from reader_documents import ReadingDocuments, source_lines
from special_functions_atlas import (BASE, MAIN, PDF, WORK, INDEX, REPORT, RECEIPTS,
    COUNT, metadata, source_specs, expected_math, normalize_notes, prepare, render,
    verify, related_routes, inventory, sequence)
from readable_chapters import Chapter, original_math

ROOT=Path(__file__).resolve().parents[1]


def publish_fixture(output):
    registry=json.loads((ROOT/'manifests/browse-resources.json').read_bytes())
    registry['components']=[c for c in registry['components'] if c['id']==WORK]
    site=SimpleNamespace(root=ROOT,output=output,registry=registry,
        claims={'works':[],'records':[],'sources':[]},search=[],revision='test')
    def write(path,text):
        dest=output/path;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(text,encoding='utf-8')
    def read_source(record):
        raw=(ROOT/record['repository_path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=record['sha256']:
            raise ValueError('Changed source: '+record['repository_path'])
        return raw
    site.read_source=read_source;site.write=write
    site.rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page))
    site.page=lambda path,title,body:write(path,'<!doctype html><html lang="en"><title>'+title+'</title><main>'+body+'</main></html>')
    reader=ReadingDocuments(site)
    reader.readable_books={WORK:{}}
    prepare(reader);render(reader)
    for path,record in reader.records.items():
        raw=read_source(record)
        dest=output/record['file_url'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        if path.endswith('.tex'):
            site.page(record['url'],record['title'],source_lines(raw.decode('utf-8-sig')))
    return reader


class SpecialFunctionsAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temporary.cleanup)
        cls.output=Path(cls.temporary.name)
        cls.reader=publish_fixture(cls.output)
        cls.documents=dict(source_revision='test',files=list(cls.reader.records.values()),images=list(cls.reader.images.values()))
        cls.pages={p.relative_to(cls.output).as_posix():Page(p.read_text(encoding='utf-8')) for p in cls.output.rglob('*.html')}

    def test_complete_authored_lesson_inventory_and_mathematics(self):
        specs,sources=source_specs(lambda path:(ROOT/path).read_text(encoding='utf-8-sig'))
        self.assertEqual([p['number'] for p in specs if p['kind']=='lesson'],list(range(1,172)))
        self.assertEqual(len(specs),174)
        self.assertEqual(len(sources),18)
        self.assertEqual(sum(len(expected_math(p)) for p in specs),1494)
        for p in specs:
            if p['kind']=='notes':
                self.assertEqual(original_math(normalize_notes(p['body'])),original_math(p['body']))
        from special_functions_atlas import validate_source
        with self.assertRaisesRegex(ValueError,'Review changed Special Functions visual source'):
            validate_source(lambda p:(ROOT/p).read_bytes()+(b'\nchanged' if p==MAIN else b''))

    def test_every_lossless_image_has_identical_decoded_pixels(self):
        receipt=json.loads((ROOT/'website'/RECEIPTS).read_bytes())
        self.assertEqual(len(receipt['figures']),171)
        total=0
        for row in receipt['figures']:
            original=Image.open(ROOT/row['source']).convert('RGBA')
            converted=Image.open(ROOT/'website'/row['image']).convert('RGBA')
            self.assertEqual(original.size,converted.size,row['name'])
            self.assertEqual(original.tobytes(),converted.tobytes(),row['name'])
            self.assertEqual(hashlib.sha256(original.tobytes()).hexdigest(),row['rgba_sha256'])
            self.assertEqual(hashlib.sha256((ROOT/row['pdf_source']).read_bytes()).hexdigest(),row['pdf_sha256'])
            total+=(ROOT/'website'/row['image']).stat().st_size
        self.assertLess(total,6*1024*1024)

    def test_published_equations_images_navigation_and_directory(self):
        self.assertEqual(verify(self.output,self.documents,self.pages),
                         dict(lessons=171,figures=171,reading_pages=174,math_expressions=1494))
        visual=[row for row in self.reader.site.search if row.get('visual_guide')]
        self.assertEqual(len(visual),175)
        self.assertEqual({row['url'] for row in visual},{INDEX,*[p['url'] for p in sequence()]})
        self.assertEqual(len(self.reader.images),171)
        self.assertTrue(all(row['file_url'].endswith('.webp') for row in self.reader.images.values()))
        guide=inventory(ROOT,self.documents['files'])
        self.assertEqual(guide['units'],174)
        self.assertEqual(guide['html_atlas'],INDEX)
        for spec in sequence():
            markup=(self.output/spec['url']).read_text(encoding='utf-8')
            self.assertIn('data-reading-total="174"',markup)
            self.assertEqual(markup.count('class="reading-navigation"'),2)
            self.assertNotIn(r'\lesson{',markup)
            self.assertNotIn(r'\startvolume{',markup)
            from core_visual_guides import guide_choices
            for target in ['read/visual-guides.html','read/'+WORK+'/index.html',*[r[3] for r in guide_choices()]]:
                self.assertIn(posixpath.relpath(target,posixpath.dirname(spec['url'])),self.pages[spec['url']].links)

    def test_every_image_binds_a_published_source_and_original_receipt(self):
        files={row['repository_path']:row for row in self.documents['files']}
        receipt=json.loads((ROOT/'website'/RECEIPTS).read_bytes())
        figures={'website/'+row['image']:row for row in receipt['figures']}
        for image in self.documents['images']:
            self.assertIn(image['source'],files)
            self.assertEqual(image['source'],PDF)
            self.assertEqual(image['source_sha256'],files[image['source']]['sha256'])
            figure=figures[image['repository_path']]
            self.assertEqual(image['original_image_source'],figure['source'])
            self.assertEqual(image['original_image_source_sha256'],figure['source_sha256'])
            self.assertEqual(hashlib.sha256((ROOT/image['original_image_source']).read_bytes()).hexdigest(),
                             image['original_image_source_sha256'])
            self.assertNotIn(image['original_image_source'],files)

    def test_note_body_rejects_new_unsupported_markup(self):
        with self.assertRaisesRegex(ValueError,'Unsupported prose command'):
            Chapter('',{}).paragraphs(normalize_notes(r'A sentence. \unknownlayout{lost words}'))
        path=BASE+'foundations.tex'
        def load(source):
            text=(ROOT/source).read_text(encoding='utf-8-sig')
            return text+'\nMust be preserved.' if source==path else text
        with self.assertRaisesRegex(ValueError,'Unselected Special Functions visual tail'):
            source_specs(load)

    def test_topic_links_distinguish_paper_prefixes(self):
        self.assertTrue(related_routes({'tag':'PAPER I / 01'})[0][1].endswith('sequences-and-polyphase.html'))
        self.assertTrue(related_routes({'tag':'PAPER II / 01'})[0][1].endswith('arithmetic-depth.html'))
        self.assertTrue(related_routes({'tag':'PAPER III / 01'})[0][1].endswith('orbit-spectra.html'))
        self.assertTrue(related_routes({'tag':'PAPER IV / 01'})[0][1].endswith('index.html'))

    def test_changed_equation_is_rejected(self):
        path=self.output/INDEX.replace('index.html','l001.html');before=path.read_bytes()
        try:
            text=before.decode('utf-8')
            text,count=re.subn(r'(class="arithmatex"[^>]*>\\\[)',r'\g<1>1+',text,count=1)
            self.assertEqual(count,1);path.write_text(text,encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'HTML math changed'):
                verify(self.output,self.documents,self.pages)
        finally:path.write_bytes(before)

    def test_changed_image_is_rejected(self):
        record=json.loads((self.output/REPORT).read_bytes())['figures'][0]
        path=self.output/record['image'];before=path.read_bytes()
        try:
            path.write_bytes(before+b'changed')
            with self.assertRaisesRegex(AssertionError,'figure changed'):
                verify(self.output,self.documents,self.pages)
        finally:path.write_bytes(before)


if __name__=='__main__':unittest.main()
