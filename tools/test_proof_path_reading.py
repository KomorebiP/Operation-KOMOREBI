"""Source-fidelity and parser regressions for the Proof Path Theory reader."""
import unittest
import hashlib
import json
import posixpath
import tempfile
from pathlib import Path
from types import SimpleNamespace

from proof_path_reading import (BOOK, CHAPTERS, MAIN, WORK, normalize, source_specs,
                                part_openings, prepare_book, source_math)
from readable_chapters import (Chapter, chapter_text, manuscript_macros,
                               original_math, render_book, expand_math)
from reader_documents import ReadingDocuments
from check_reader_site import Page


ROOT = Path(__file__).resolve().parents[1]


class ProofPathReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = (ROOT / MAIN).read_text(encoding="utf-8-sig")
        cls.macros = manuscript_macros(cls.main, BOOK["required_macros"])

    def test_all_sections_follow_retained_source(self):
        self.assertEqual(source_specs(lambda path: self.main), CHAPTERS)
        self.assertEqual(len(CHAPTERS), 40)
        self.assertEqual(sum(c["kind"] == "part" for c in CHAPTERS), 5)
        self.assertEqual(CHAPTERS[0]["title"], "Preface")
        self.assertEqual(CHAPTERS[-1]["title"], "A complete minimal proof-field record")
        self.assertEqual(len({c["url"] for c in CHAPTERS}), len(CHAPTERS))
        self.assertEqual(CHAPTERS[0]["start_line"], 187)

    def test_math_and_line_numbers_preserved_everywhere(self):
        state = {"number_floats": True}
        expressions = []
        nodes = []
        for spec in CHAPTERS:
            raw = chapter_text(self.main, spec)
            formatted = normalize(raw)
            self.assertEqual(formatted.count("\n"), raw.count("\n"), spec["title"])
            self.assertEqual(original_math(formatted), original_math(raw), spec["title"])
            chapter = Chapter(formatted, self.macros, state=state, check_refs=False)
            nodes.extend(chapter.nodes)
            expressions.extend(original_math(raw))
            state = {key: getattr(chapter, key)
                     for key in ("section", "appendix", "part", "subsection",
                                 "subsubsection", "counter", "section_prefix",
                                 "figure", "table", "number_floats")}
        self.assertGreater(len(expressions), 100)
        self.assertGreater(sum(n["kind"] == "proof" for n in nodes), 45)
        self.assertGreater(sum(n["kind"] == "figure" for n in nodes), 15)
        self.assertGreater(sum(n["kind"] == "lstlisting" for n in nodes), 8)
        self.assertGreater(sum(n["kind"] == "longtable" for n in nodes), 2)
        self.assertGreater(len(nodes), 150)

    def test_all_part_illustrations_have_receipted_png_source(self):
        for opening in part_openings(self.main).values():
            file = opening["image"].removesuffix('.pdf') + '.png'
            self.assertTrue((ROOT / "monographs/proof-path-theory/docs/figures" / file).is_file(), file)

    def test_part_macro_content_and_math_are_preserved(self):
        openings = part_openings(self.main)
        self.assertEqual(len(openings), 5)
        self.assertEqual(sum('The governing distinction' in o['text'] for o in openings.values()), 4)
        for spec in CHAPTERS:
            text = normalize(chapter_text(self.main, spec), openings)
            self.assertEqual(text.count('\n'), chapter_text(self.main, spec).count('\n'))
            self.assertEqual(original_math(text), source_math(self.main, spec))
        changed = self.main.replace(r'\vspace{4pt}{\sffamily\bfseries', r'\unreviewed{4pt}{\sffamily\bfseries', 1)
        with self.assertRaisesRegex(ValueError, 'part-opening prose'):
            part_openings(changed)

    def test_complete_render_retains_figures_references_and_equations(self):
        """Exercise published HTML, including macro captions absent from the body."""
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            registry = json.loads((ROOT/'manifests/browse-resources.json').read_bytes())
            registry['components'] = [c for c in registry['components'] if c['id'] == WORK]
            site = SimpleNamespace(root=ROOT, output=output, registry=registry,
                                   claims={'works': [], 'records': [], 'sources': []}, search=[])
            def write(path, text):
                target=output/path;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(text,encoding='utf-8')
            def read_source(record):
                raw=(ROOT/record['repository_path']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),record['sha256'])
                return raw
            site.write=write;site.read_source=read_source
            site.rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page))
            site.page=lambda path,title,body:write(path,'<!doctype html><html lang="en"><title>'+title+'</title><main>'+body+'</main></html>')
            reader=ReadingDocuments(site)
            book=prepare_book(reader,dict(BOOK))
            reports=render_book(reader,book)
            self.assertEqual(len(reports),40)
            self.assertEqual(sum(r['math_expressions'] for r in reports),1051)
            self.assertEqual(sum(n['kind']=='proof' for r in reports for n in r['nodes']),51)
            self.assertEqual(len(reader.images),25)
            figures=[n for _,_,chapter in book['chapters'] for n in chapter.nodes if n['kind']=='figure']
            self.assertEqual([n['number'] for n in figures],[str(i) for i in range(1,26)])
            from html.parser import HTMLParser
            class MathText(HTMLParser):
                def __init__(self, text):
                    super().__init__();self.depth=0;self.math=[];self.feed(text)
                def handle_starttag(self,tag,attrs):
                    if self.depth:self.depth+=1
                    elif 'arithmatex' in dict(attrs).get('class','').split():self.depth=1;self.math.append('')
                def handle_endtag(self,tag):
                    if self.depth:self.depth-=1
                def handle_data(self,data):
                    if self.depth:self.math[-1]+=data
            for spec,raw,chapter in book['chapters']:
                markup=(output/spec['url']).read_text(encoding='utf-8')
                parsed=Page(markup)
                self.assertEqual(len(parsed.ids),len(set(parsed.ids)),spec['title'])
                self.assertEqual([x[2:-2] for x in MathText(markup).math],
                                 [expand_math(x,chapter.macros) for x in source_math(self.main,spec)],spec['title'])
            part=(output/CHAPTERS[2]['url']).read_text(encoding='utf-8')
            self.assertIn('A declared proof field retains three different statuses.',part)
            self.assertIn('The governing distinction',part)
            self.assertIn('Figure 2.',part)
            intro=(output/'read/proof-path-theory/introduction.html').read_text(encoding='utf-8')
            self.assertIn('Figure 3.',intro)
            self.assertIn('>[2]</a>',intro)
            bridge=(output/'read/proof-path-theory/a-checked-realization-bridge-for-proof-fields.html').read_text(encoding='utf-8')
            self.assertIn('>(SC)</a>',bridge)
            self.assertNotRegex(bridge,r'Theorem[\s\xa0]+<a\b[^>]*>Theorem')
            self.assertNotRegex(bridge,r'Section[\s\xa0]+<a\b[^>]*>Section')
            references=(output/BOOK['bib_page']).read_text(encoding='utf-8')
            self.assertIn('[2] buss',references)

    def test_print_wrappers_removed_without_changing_prose(self):
        spec = next(c for c in CHAPTERS if c["kind"] == "part")
        text = normalize(chapter_text(self.main, spec))
        self.assertIn(r"\part{Proof fields and certificates}", text)
        self.assertNotIn(r"\monographpart", text)
        trace = next(c for c in CHAPTERS if c["title"] == "A checked realization bridge for proof fields")
        converted = normalize(chapter_text(self.main, trace))
        self.assertIn("Visual study 01", converted)
        self.assertIn("The bridge is a restriction map", converted)
        self.assertIn(r"\begin{readerroadmap}", converted)


if __name__ == "__main__":
    unittest.main()
