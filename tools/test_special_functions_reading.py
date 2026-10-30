"""Coverage and rejection controls for the Special Functions HTML edition."""
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from reader_documents import ReadingDocuments, source_lines
from special_functions_reading import (BASE, MAIN, WORK, CONFIG, INDEX, REPORT,
    SOURCE_TITLES, normalize, source_specs, prepare_book, render_book, verify, figure_path)
from readable_chapters import Chapter, original_math
from check_reader_site import Page

ROOT = Path(__file__).resolve().parents[1]


class SpecialFunctionsReadingTests(unittest.TestCase):
    def test_all_body_inputs_and_ten_appendices_are_selected(self):
        load=lambda path:(ROOT/path).read_text(encoding='utf-8-sig')
        specs=source_specs(load)
        self.assertEqual(len(specs),37)
        self.assertEqual(sum(s['title'].startswith('Appendix ') for s in specs),10)
        self.assertEqual({s['source'] for s in specs if s['source']!=MAIN and s['source']!=BASE+'monograph-design.tex'}, {BASE+p for p in SOURCE_TITLES})
        with self.assertRaisesRegex(ValueError,'coverage changed'):
            source_specs(lambda p:load(p).replace(r'\input{sections/spectral_continuation.tex}',''))

    def test_layout_translation_preserves_lines_and_rejects_new_prose(self):
        text=r'\hypertarget{key}{\section{Heading}\label{key}}'+'\n'+r'\claim{A result} $x^2+1$'
        converted=normalize(text)
        self.assertEqual(converted.count('\n'),text.count('\n'))
        self.assertEqual(original_math(converted),original_math(text))
        with self.assertRaisesRegex(ValueError,'Unsupported prose command'):
            Chapter('',{}).paragraphs(normalize(r'Kept. \unreviewed{must not disappear}'))

    def test_entire_render_and_independent_html_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)
            registry=json.loads((ROOT/'manifests/browse-resources.json').read_bytes())
            registry['components']=[c for c in registry['components'] if c['id']==WORK]
            site=SimpleNamespace(root=ROOT,output=output,registry=registry,claims={'works':[],'records':[],'sources':[]},search=[])
            def write(path,text):
                dest=output/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
            def read_source(record):
                raw=(ROOT/record['repository_path']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),record['sha256'])
                return raw
            import posixpath
            site.read_source=read_source;site.write=write
            site.rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page))
            site.page=lambda path,title,body:write(path,'<!doctype html><html lang="en"><title>'+title+'</title><main>'+body+'</main></html>')
            reader=ReadingDocuments(site)
            book=prepare_book(reader,dict(CONFIG));render_book(reader,book)
            for path,record in reader.records.items():
                raw=read_source(record)
                dest=output/record['file_url'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
                if path.endswith('.tex'):site.page(record['url'],record['title'],source_lines(raw.decode('utf-8-sig')))
            pages={}
            for path in output.rglob('*.html'):
                pages[path.relative_to(output).as_posix()]=Page(path.read_text(encoding='utf-8'))
            result=verify(output,dict(files=list(reader.records.values())),pages)
            self.assertEqual(result,dict(reading_sections=37,mathematical_expressions=2123))
            self.assertEqual(len(reader.images),32)
            self.assertIn('Appendix J.',(output/INDEX).read_text(encoding='utf-8'))
            chapter=next(p for p in output.rglob('dilation-full.html'))
            chapter.write_text(chapter.read_text(encoding='utf-8').replace('c_-','c_+',1),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'HTML math changed'):
                verify(output,dict(files=list(reader.records.values())),pages)
            entry=next(iter(reader.owned.values()))
            fake=SimpleNamespace(owned={BASE+'figures/missing.pdf':entry})
            with self.assertRaisesRegex(ValueError,'matching receipt-bound'):
                figure_path(fake,'figures/missing.pdf')


if __name__=='__main__':unittest.main()
