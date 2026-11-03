"""Source fidelity and usable reading routes for Machine-Native Reasoning."""
import hashlib
import json
from contextlib import ExitStack
from pathlib import Path
import posixpath
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

import readable_chapters as reading
from machine_native_reasoning_reading import (WORK, MAIN, MAP, BOOK, CHAPTERS,
    SOURCE_SHA256, SCOPE_PAGE, normalize, source_specs, source_math)
from build_reader_site import Site
from check_reader_site import Page, check_readable_chapter
from reader_documents import ReadingDocuments
from reading_navigation import verify as verify_reading_navigation

ROOT = Path(__file__).resolve().parents[1]


def publish_fixture(output):
    """Publish the real edition and sources without building the whole site.

    Root can reuse this for visual inspection and an incremental size estimate.
    The same receipt-owned records and actual figure assets are used in CI.
    """
    output = Path(output)
    registry = json.loads((ROOT/'manifests/browse-resources.json').read_bytes())
    registry['components'] = [c for c in registry['components'] if c['id'] == WORK]
    status = json.loads((ROOT/'manifests/project-status.json').read_bytes())
    components = json.loads((ROOT/'manifests/source-components.json').read_bytes())['components']
    site = SimpleNamespace(root=ROOT, output=output, revision='machine-native-reasoning-reading-test',
        search=[], cache=None, editorial_editions={}, registry=registry, status=status,
        assessments={c['id']:c for c in status['components']},
        components={c['id']:c for c in components},
        repos={'collection':'KomorebiP/Operation-KOMOREBI'},
        revisions={'collection':'machine-native-reasoning-reading-test'},
        roots={'collection':ROOT}, documents={}, asset_count=0)
    for name in ('rel','write','page','read_source','resolve'):
        setattr(site,name,lambda *args,_name=name,**kwargs:getattr(Site,_name)(site,*args,**kwargs))
    reader = ReadingDocuments.__new__(ReadingDocuments)
    reader.site = site
    site.reader = reader
    reader.owned,reader.records,reader.images,reader.inclusions = {},{},{},{}
    reader.learning = {'learning_topics':[]}
    reader.claims_by_module,reader.claims_by_source = {},{}
    reader.manuscript_roots = {WORK:MAIN}
    receipt = json.loads((ROOT/('manifests/source-imports/'+WORK+'.json')).read_bytes())
    for entry in receipt['files']:
        path = receipt['destination']+'/'+entry['path']
        reader.owned[path] = dict(entry,repository_path=path,work=WORK)
    reader.add('monographs/machine-native-reasoning/reader/Machine_Native_Reasoning_Reviewed_Core.pdf','Reviewed Mathematical Core PDF')
    with ExitStack() as stack:
        # Use the production document publisher, including Markdown/PDF landing
        # pages and highlighted Lean sources. Only unrelated atlas publishers
        # are omitted from this one-work fixture.
        for module in ('reader_atlas','paper_i_atlas','core_worked_atlases',
                       'paper_viii_atlas','paper_ix_atlas','paper_x_atlas',
                       'paper_xi_atlas','paper_xii_atlas','paper_v_atlas',
                       'paper_vi_atlas','paper_vii_atlas','large_signal_atlas',
                       'core_visual_guides'):
            stack.enter_context(patch(module+'.render',return_value=None))
        stack.enter_context(patch.object(reading,'BOOKS',{WORK:BOOK}))
        stack.enter_context(patch.object(reading,'CHAPTERS',CHAPTERS))
        from lean_reader import prepare as prepare_lean
        prepare_lean(reader)
        reading.prepare(reader)
        prepared = set(reader.records)
        reader.render()
        from lean_reader import build as build_lean
        build_lean(reader)
        if set(reader.records) != prepared:
            raise AssertionError('All MNR records must be prepared before source pages are rendered')
    return reader


class MachineNativeReasoningReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = (ROOT/MAIN).read_text(encoding='utf-8')

    def test_complete_source_ranges_and_changed_source_rejection(self):
        load = lambda path:(ROOT/path).read_text(encoding='utf-8')
        self.assertEqual(source_specs(load),CHAPTERS)
        self.assertEqual(hashlib.sha256(self.main.encode()).hexdigest(),SOURCE_SHA256)
        self.assertEqual(len(CHAPTERS),13)
        self.assertEqual([c['chapter_number'] for c in CHAPTERS if c['chapter_number']],list(range(1,10)))
        self.assertTrue(all(c['title'].startswith('Chapter '+str(c['chapter_number'])+'. ')
                            for c in CHAPTERS if c['chapter_number']))
        self.assertEqual(CHAPTERS[0]['start_line'],64)
        self.assertEqual(CHAPTERS[-1]['end_line'],len(self.main.splitlines()))
        for prior,current in zip(CHAPTERS,CHAPTERS[1:]):
            self.assertEqual(prior['end_line']+1,current['start_line'])
        with self.assertRaisesRegex(ValueError,'Review changed Machine-Native Reasoning'):
            source_specs(lambda path:load(path)+'\nUnreviewed change.')

    def test_math_lines_printed_numbers_and_source_macros(self):
        macros = reading.manuscript_macros(self.main,BOOK['required_macros'])
        state,results,expressions = {},[],[]
        for spec in CHAPTERS:
            raw = reading.chapter_text(self.main,spec)
            text = normalize(raw)
            self.assertEqual(text.count('\n'),raw.count('\n'))
            self.assertEqual(reading.original_math(text),source_math(self.main,spec))
            expressions.extend(source_math(self.main,spec))
            self.assertNotRegex(text,r'\\(?:source|boundary|question)\{')
            chapter = reading.Chapter(text,macros,state=state,check_refs=False)
            state = {key:getattr(chapter,key) for key in ('section','appendix','part','subsection',
                     'subsubsection','counter','section_prefix','figure','table','number_floats')}
            results.extend(n for n in chapter.nodes if n['kind'] in {'theorem','proposition','corollary'})
        self.assertEqual(len(expressions),618)
        recorded = json.loads((ROOT/MAP).read_bytes())
        self.assertEqual([(n['labels'][0],n['kind'],n['number'],n['title']) for n in results],
                         [(n['label'],n['kind'],n['number'],n['title']) for n in recorded])
        self.assertEqual([n['line'] for n in results],[self.main.count('\n',0,m.start())+1
            for m in re.finditer(r'\\begin\{(?:theorem|proposition|corollary)\}',self.main)])
        self.assertEqual(normalize(r'\source{A $x$ source.}'),r'\textit{Source relationship.} A $x$ source.')
        self.assertEqual(normalize(r'\boundary{Only $x$.}'),r'\textit{Boundary.} Only $x$.')

    def test_real_publication_equations_proofs_figures_and_all_local_routes(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            reader = publish_fixture(output)
            pages = {p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            documents = dict(files=list(reader.records.values()))
            with patch.object(reading,'BOOKS',{WORK:BOOK}),patch.object(reading,'CHAPTERS',CHAPTERS):
                self.assertEqual(check_readable_chapter(output,documents,pages),618)
                self.assertEqual(verify_reading_navigation(output,pages,documents),
                    dict(editions=1,reading_pages=14,navigation_controls=28))
            book = reader.readable_books[WORK]
            nodes = [node for _,_,chapter in book['chapters'] for node in chapter.nodes]
            expected = {'theorem':16,'proposition':10,'corollary':1,'proof':27,
                        'counterexample':12,'figure':6,'tabular':4,'longtable':1}
            self.assertEqual({kind:sum(n['kind']==kind for n in nodes) for kind in expected},expected)
            self.assertEqual(sum(len(chapter.proof_pairs) for _,_,chapter in book['chapters']),27)
            self.assertEqual(len(book['references']),10)
            self.assertEqual(len(reader.images),6)
            self.assertEqual(len(reader.lean_works[WORK]),79)
            for record in reader.records.values():
                self.assertIn(record['url'],pages,record['repository_path'])
                if record.get('source_url'):
                    self.assertIn(record['source_url'],pages,record['repository_path'])
            finder = (output/'read'/WORK/'statements.html').read_text(encoding='utf-8')
            self.assertEqual(finder.count('data-statement-entry='),39)
            self.assertEqual(finder.count('class="statement-proof-link"'),27)
            for spec in CHAPTERS:
                page = pages[spec['url']]
                self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
                self.assertEqual(len(page.ids),len(set(page.ids)))
            scope = pages[SCOPE_PAGE]
            self.assertTrue({'r-'+entry['label'].split(':',1)[1] for entry in json.loads((ROOT/MAP).read_bytes())} <= set(scope.ids))
            self.assertIn('formal-correspondence',scope.ids)
            continuous = (output/CHAPTERS[10]['url']).read_text(encoding='utf-8')
            self.assertIn('formal-scope.html#formal-correspondence',continuous)
            self.assertIn('Read the formal correspondence chapter',continuous)
            # This checks the source fragments as well as all chapter, proof,
            # statement finder, bibliography and recorded-scope routes.
            for name,page in pages.items():
                for link in page.links:
                    parts = urlsplit(link)
                    if parts.scheme or parts.netloc:
                        continue
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(parts.path))) if parts.path else name
                    if target.startswith('read/'+WORK+'/'):
                        self.assertIn(target,pages,(name,link))
                    if target in pages and parts.fragment and not parts.query:
                        self.assertIn(unquote(parts.fragment),pages[target].ids,(name,link))
            index = (output/BOOK['index']).read_text(encoding='utf-8')
            self.assertIn('27 selected mathematical results',index)
            self.assertIn('no proof review, Lean execution, or empirical validation',index)
            start = (output/BOOK['reading_guide']).read_text(encoding='utf-8')
            lean = (output/'lean'/WORK/'index.html').read_text(encoding='utf-8')
            for text in (start,lean):
                self.assertIn('Lean 4.34.0-rc2',text)
                self.assertIn('Lean 4.33.0',text)
            self.assertIn('Read the portable reproduction instructions',start)


if __name__ == '__main__':
    unittest.main()
