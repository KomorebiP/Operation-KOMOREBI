"""Source coverage, exact mathematical presentation, proofs and reader routes."""
import hashlib
import json
from pathlib import Path
import posixpath
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

import readable_chapters as reading
from physics_reading import WORK, ROOT as SOURCE_ROOT, MAIN, MACROS, BOOK, DATA, CHAPTERS, source_specs, source_math, normalize
from build_reader_site import Site
from reader_documents import ReadingDocuments, source_lines
from check_reader_site import Page, check_readable_chapter

ROOT = Path(__file__).resolve().parents[1]


def reader_fixture(output):
    site = SimpleNamespace(root=ROOT, output=output, revision='physics-conversion-test',
        search=[], cache=None, assessments={}, editorial_editions={})
    for name in ('rel', 'write', 'page', 'read_source'):
        setattr(site, name, lambda *args, _name=name, **kwargs: getattr(Site, _name)(site, *args, **kwargs))
    reader = ReadingDocuments.__new__(ReadingDocuments)
    reader.site = site
    reader.owned, reader.records, reader.images, reader.inclusions = {}, {}, {}, {}
    reader.learning = {'learning_topics': []}
    reader.claims_by_module, reader.claims_by_source = {}, {}
    reader.manuscript_roots = {WORK: MAIN}
    receipt = json.loads((ROOT/'manifests/source-imports'/f'{WORK}.json').read_bytes())
    for entry in receipt['files']:
        path = SOURCE_ROOT+entry['path']
        reader.owned[path] = dict(entry, repository_path=path, work=WORK)
    reader.add(SOURCE_ROOT+'Komorebi_Physics.pdf', 'Complete Physics book (572 pages)')
    with patch.object(reading, 'BOOKS', {WORK: BOOK}):
        reading.prepare(reader)
    return reader


def publish_fixture(output):
    reader = reader_fixture(output)
    with patch.object(reading, 'BOOKS', {WORK: BOOK}):
        reading.render(reader)
    for record in reader.records.values():
        raw = reader.site.read_source(record)
        target = output/record['file_url']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        if record['format'] == 'source':
            reader.site.page(record['url'], record['title'], '<h1>'+record['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader


class PhysicsReadingTests(unittest.TestCase):
    def test_lean_inspector_uses_the_complete_continuum_project(self):
        from lean_execution import collect
        # Paper V supplies the shared runner's explicitly labelled fallback.
        books = {WORK: BOOK, 'paper-v': reading.BOOKS['paper-v']}
        with patch.object(reading, 'BOOKS', books):
            _, catalog = collect(ROOT, 'physics-conversion-test')
        project = SOURCE_ROOT+'formal/continuum'
        sources = [row for row in catalog['sources'] if row['work'] == WORK]
        self.assertTrue(sources)
        self.assertTrue(all(row['path'].startswith(project+'/KomorebiPhysics/') for row in sources))
        self.assertEqual({row['project'] for row in sources}, {project})
        for name in ('lean-toolchain', 'lake-manifest.json'):
            self.assertIn(project+'/'+name, catalog['projects'][project]['files'])

    def test_sources_are_complete_in_order_and_fail_closed(self):
        load = lambda path: (ROOT/path).read_text(encoding='utf-8-sig')
        self.assertEqual(source_specs(load), CHAPTERS)
        self.assertEqual(len(CHAPTERS), 55)
        self.assertEqual(sum(spec['treatment']=='dirac' for spec in CHAPTERS), 28)
        self.assertEqual(sum(spec['treatment']=='generator' for spec in CHAPTERS), 8)
        for path in DATA['source_sha256']:
            with self.assertRaisesRegex(ValueError, 'changed Physics source'):
                source_specs(lambda p: load(p)+('changed' if p == path else ''))
        for spec in CHAPTERS:
            selected = reading.chapter_text(load(spec['source']), spec)
            self.assertEqual(normalize(selected).count('\n'), selected.count('\n'))
            # Independently mask only numbered display wrappers. No prose or
            # figure translation is used in this mathematical-token comparison.
            math_only = selected.replace(r'\begin{equation}', r'\[').replace(r'\end{equation}', r'\]')
            math_only = math_only.replace(r'\begin{align}', r'\begin{align*}').replace(r'\end{align}', r'\end{align*}')
            self.assertEqual(reading.original_math(math_only), source_math(load(spec['source']), spec))
        # A changed selection must never silently omit or repeat source text.
        altered = [dict(spec) for spec in CHAPTERS]
        altered[1]['start_line'] += 1
        with patch('physics_reading.CHAPTERS', altered), self.assertRaisesRegex(ValueError, 'gap or overlap'):
            source_specs(load)
        reordered = CHAPTERS[19:] + CHAPTERS[:19]
        with patch('physics_reading.CHAPTERS', reordered), self.assertRaisesRegex(ValueError, 'reading order'):
            source_specs(load)

    def test_publication_equations_numbering_figures_proofs_and_routes(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            reader = publish_fixture(output)
            pages = {path.relative_to(output).as_posix(): Page(path.read_text(encoding='utf-8')) for path in output.rglob('*.html')}
            documents = dict(files=list(reader.records.values()), images=list(reader.images.values()))
            with patch.object(reading, 'BOOKS', {WORK: BOOK}), patch.object(reading, 'CHAPTERS', CHAPTERS):
                count = check_readable_chapter(output, documents, pages)
            self.assertEqual(count, 1429)
            book = reader.readable_books[WORK]
            nodes = [node for _, _, chapter in book['chapters'] for node in chapter.nodes]
            for treatment, sections, proofs, figure_numbers in [('foundations', 16, 15, list(map(str, range(1, 11)))),
                    ('dirac', 25, 18, ['']*6), ('generator', 7, 10, ['1','2'])]:
                selected = [n for s, _, c in book['chapters'] if s['treatment']==treatment for n in c.nodes]
                self.assertEqual([n['number'] for n in selected if n['kind']=='section' and n['number']], list(map(str, range(1, sections+1))))
                self.assertEqual(sum(n['kind']=='proof' for n in selected), proofs)
                self.assertEqual([n['number'] for n in selected if n['kind']=='figure'], figure_numbers)
            self.assertEqual([n['number'] for n in nodes if n['number'].startswith('PH')], ['PH'+str(i).zfill(2) for i in range(1, 13)])
            for title, number in [('Self-adjoint maximal multiplier', '17.1'),
                                  ('Weighted domain and mass independence', '19.1'),
                                  ('Physical torus Hamiltonian', '21.1')]:
                self.assertEqual(next(n['number'] for n in nodes if n['title']==title), number)
            proofs = sum(n['kind']=='proof' for n in nodes)
            self.assertEqual(proofs, 43)
            self.assertEqual(proofs, sum(len(c.proof_pairs) for _, _, c in book['chapters']))
            self.assertEqual(book['chapters'][0][2].equation_numbers['f:atlas-relations'], '1')
            self.assertEqual(book['chapters'][0][2].labels['f:parseval']['number'], '1.2')
            self.assertEqual(len(reader.images), 18)
            self.assertEqual(len(book['references']), 6)
            generator = [c for s, _, c in book['chapters'] if s['treatment']=='generator']
            self.assertEqual(generator[0].labels['thm:generator']['number'], '2.3')
            self.assertEqual(generator[0].equation_numbers['eq:space'], '1')
            self.assertEqual(generator[0].equation_numbers['eq:prop_rate'], '16')
            self.assertEqual(generator[0].macros['pp']['body'], r'\left\lVert#1\right\rVert')
            self.assertNotIn('pp', book['chapters'][0][2].macros)
            for spec in CHAPTERS:
                page = pages[spec['url']]
                self.assertEqual((page.h1, page.main, page.images_without_alt), (1, 1, 0))
                self.assertEqual(len(page.ids), len(set(page.ids)))
                markup = (output/spec['url']).read_text(encoding='utf-8')
                self.assertIn('reading-text-size', markup)
                self.assertNotRegex(markup, r'\\(?:foundationfigure|atlasfigure|sourcepointer|endhead|addcontentsline|needspace|hypertarget)')
            refs = (output/CHAPTERS[18]['url']).read_text(encoding='utf-8')
            for label in ['P1', 'P4', 'C1', 'C3']:
                self.assertIn('['+label+']', refs)
            dirac_refs = (output/BOOK['bib_page']).read_text(encoding='utf-8')
            self.assertIn('Seydaoğlu', dirac_refs)
            self.assertIn('Schrödinger', dirac_refs)
            for entry in book['references']:
                self.assertIn('ref-'+entry['key'], pages[BOOK['bib_page']].ids)
            index = (output/BOOK['index']).read_text(encoding='utf-8')
            self.assertIn('opening HTML installments', index)
            self.assertIn('572-page', index)
            self.assertIn('adds no proof audit', index)
            destinations = [int(urlsplit(link).fragment.removeprefix('page=')) for link in pages[BOOK['index']].links
                            if urlsplit(link).fragment.startswith('page=')]
            self.assertEqual(destinations, [row['index_start']+1 for row in book['full_book']])
            self.assertEqual(len(destinations), 21)
            from statement_navigation import check_directory
            directory = reading.statement_directory_url(BOOK)
            result = check_directory((output/directory).read_text(encoding='utf-8'),
                [(s['url'], (output/s['url']).read_text(encoding='utf-8')) for s in CHAPTERS], directory)
            self.assertEqual(result['proof_links'], proofs)
            targets = set(pages) | {record['url'] for record in reader.records.values()}
            for name, page in pages.items():
                for link in page.links:
                    parts = urlsplit(link)
                    if parts.scheme or parts.netloc:
                        continue
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parts.path))) if parts.path else name
                    if target.startswith('read/'+WORK+'/'):
                        self.assertIn(target, targets, (name, link))
                    if target in pages and parts.fragment and not parts.query:
                        self.assertIn(unquote(parts.fragment), pages[target].ids, (name, link))
            for record in reader.images.values():
                self.assertEqual(record['source_sha256'], hashlib.sha256((ROOT/record['source']).read_bytes()).hexdigest())
                if '/generator/' in record['source']:
                    self.assertEqual((output/record['file_url']).read_bytes(), (ROOT/record['source']).read_bytes())


if __name__ == '__main__':
    unittest.main()
