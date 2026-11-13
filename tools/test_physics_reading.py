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
from check_reader_site import Page, check_readable_chapter, check_image_sources

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
        self.assertEqual(len(CHAPTERS), 160)
        self.assertEqual(sum(spec['treatment']=='dirac' for spec in CHAPTERS), 28)
        self.assertEqual(sum(spec['treatment']=='generator' for spec in CHAPTERS), 8)
        self.assertEqual(sum(spec['treatment']=='gauge' for spec in CHAPTERS), 21)
        self.assertEqual(sum(spec['treatment']=='gravity' for spec in CHAPTERS), 24)
        self.assertEqual(sum(spec['treatment']=='adic' for spec in CHAPTERS), 22)
        self.assertEqual(sum(spec['treatment']=='fiber' for spec in CHAPTERS), 11)
        self.assertEqual(sum(spec['treatment']=='cosmology' for spec in CHAPTERS),27)
        for path in DATA['source_sha256']:
            with self.assertRaisesRegex(ValueError, 'changed Physics source'):
                source_specs(lambda p: load(p)+('changed' if p == path else ''))
        for spec in CHAPTERS:
            selected = reading.chapter_text(load(spec['source']), spec)
            self.assertEqual(normalize(selected,spec['treatment'],load).count('\n'), selected.count('\n'))
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
        # The Adic context member is a retained inclusion at the end of its
        # references file, not a free-standing addition to the reading order.
        treatments = [dict(t) for t in DATA['treatments']]
        next(t for t in treatments if t['id']=='adic')['nested_inputs'] = {}
        with patch.dict(DATA, treatments=treatments), self.assertRaisesRegex(ValueError, 'nested input order'):
            source_specs(load)
        path = SOURCE_ROOT+'source/monographs/adic/references.tex'
        inclusion = r'\input{adic/primary_context.tex}'
        moved = inclusion+'\n'+load(path).replace(inclusion, '')
        hashes = dict(DATA['source_sha256'], **{path: hashlib.sha256(moved.encode()).hexdigest()})
        with patch.dict(DATA, source_sha256=hashes), self.assertRaisesRegex(ValueError, 'nested input position'):
            source_specs(lambda p: moved if p == path else load(p))
        from physics_fiber import MAIN as FIBER_MAIN, source_blocks
        fiber = next(t for t in DATA['treatments'] if t['id']=='fiber')
        omitted = load(FIBER_MAIN).replace(r'\input{source/02_covariant_eft}',
            'An additional passage must not be omitted.\n'+r'\input{source/02_covariant_eft}')
        with self.assertRaisesRegex(ValueError, 'main-file passage coverage'):
            source_blocks(lambda p: omitted if p==FIBER_MAIN else load(p),fiber)
        with self.assertRaisesRegex(ValueError, 'main-file passage coverage'):
            source_blocks(lambda p: load(p).replace(r'\appendix','') if p==FIBER_MAIN else load(p),fiber)
        from physics_cosmology import MAIN as COSMO_MAIN, BASE as COSMO_BASE, source_blocks, context
        cosmos = next(t for t in DATA['treatments'] if t['id']=='cosmology')
        for old,new,error in [(r'\input{chapters/02_scalar_perturbations}',
                'Unselected prose.\n'+r'\input{chapters/02_scalar_perturbations}','main-file passage coverage'),
                (r'\appendix','','appendix switch')]:
            with self.assertRaisesRegex(ValueError,error):
                source_blocks(lambda p:load(p).replace(old,new) if p==COSMO_MAIN else load(p),cosmos)
        nested = COSMO_BASE+'chapters/01_general_flrw_background.tex'
        with self.assertRaisesRegex(ValueError,'nested input order'):
            source_blocks(lambda p:load(p).replace('part_intros/part1','part_intros/part2') if p==nested else load(p),cosmos)
        with self.assertRaisesRegex(ValueError,'context inclusion'):
            context(load(COSMO_BASE+'part_intros/part1.tex')+'Additional prose.')
        with self.assertRaisesRegex(ValueError,'context inclusion'):
            context(r'\PhysicsContext{Title}{Unselected $x$.}')

    def test_publication_equations_numbering_figures_proofs_and_routes(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            reader = publish_fixture(output)
            pages = {path.relative_to(output).as_posix(): Page(path.read_text(encoding='utf-8')) for path in output.rglob('*.html')}
            documents = dict(files=list(reader.records.values()), images=list(reader.images.values()))
            check_image_sources(documents)
            with patch.object(reading, 'BOOKS', {WORK: BOOK}), patch.object(reading, 'CHAPTERS', CHAPTERS):
                count = check_readable_chapter(output, documents, pages)
            self.assertEqual(count, 6320)
            book = reader.readable_books[WORK]
            nodes = [node for _, _, chapter in book['chapters'] for node in chapter.nodes]
            for treatment, sections, proofs, figure_numbers in [('foundations', 16, 15, list(map(str, range(1, 11)))),
                    ('dirac', 25, 18, ['']*6), ('generator', 7, 10, ['1','2']),
                    ('gauge', 18, 13, list(map(str, range(1, 13)))),
                    ('gravity', 21, 20, list(map(str, range(1, 9)))),
                    ('adic', 18, 24, list(map(str, range(1, 8))))]:
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
            self.assertEqual(proofs, 119)
            self.assertEqual(proofs, sum(len(c.proof_pairs) for _, _, c in book['chapters']))
            self.assertEqual(book['chapters'][0][2].equation_numbers['f:atlas-relations'], '1')
            self.assertEqual(book['chapters'][0][2].labels['f:parseval']['number'], '1.2')
            self.assertEqual(sum(bool(r.get('source')) for r in reader.images.values()), 121)
            self.assertEqual(len(book['references']), 6)
            generator = [c for s, _, c in book['chapters'] if s['treatment']=='generator']
            self.assertEqual(generator[0].labels['thm:generator']['number'], '2.3')
            self.assertEqual(generator[0].equation_numbers['eq:space'], '1')
            self.assertEqual(generator[0].equation_numbers['eq:prop_rate'], '16')
            self.assertEqual(generator[0].macros['pp']['body'], r'\left\lVert#1\right\rVert')
            self.assertNotIn('pp', book['chapters'][0][2].macros)
            gauge = [c for s, _, c in book['chapters'] if s['treatment']=='gauge']
            for key, number in [('g:gauss','5.1'), ('g:patch-theorem','8.1'), ('g:constant-one','13.1')]:
                # Equation labels retain the equation counter as their reference
                # label, independently of the containing theorem's number.
                self.assertEqual(gauge[0].labels[key]['number'], number)
            self.assertEqual(gauge[0].equation_numbers['g:regular-bound'], '67')
            self.assertEqual(gauge[0].equation_numbers['g:dyadic-tail'], '68')
            gravity = [c for s, _, c in book['chapters'] if s['treatment']=='gravity']
            for title, number in [('Exact finite linearized closure','5.2'),
                    ('Transfer of a differential','7.2'),('Conditional boundary BFV construction','10.1'),
                    ('Charged mass coordinate','14.1'),('Exact triangular mass identity','14.2')]:
                self.assertEqual(next(n['number'] for c in gravity for n in c.nodes if n['title']==title),number)
            self.assertEqual(gravity[0].equation_numbers['c:strong:mass-identity'], '149')
            self.assertEqual(gravity[0].equation_numbers['c:strong:expansions'], '206')
            adic = [c for s, _, c in book['chapters'] if s['treatment']=='adic']
            for key, number in [('a-finite-unit-coordinates','1.1'),
                    ('a-finite-hamiltonian-classification','3.1'),('a-spectral-chebyshev-schur','8.2'),
                    ('a-limit-selfadjoint','13.1'),('a-limit-block-hamiltonian','14.1')]:
                self.assertEqual(adic[0].labels[key]['number'],number)
            for key, number in [('a-finite-hamiltonian-intertwine','25'),
                    ('a-spectral-companion-system','81'),('a-limit-block-domain','125')]:
                self.assertEqual(adic[0].equation_numbers[key],number)
            fiber = [c for s, _, c in book['chapters'] if s['treatment']=='fiber']
            fiber_nodes = [n for c in fiber for n in c.nodes]
            self.assertEqual([n['number'] for n in fiber_nodes if n['kind']=='section' and n['number']],
                ['1','2','3','4','5','6','7','A','B'])
            self.assertEqual([n['number'] for n in fiber_nodes if n['kind']=='figure'],['3.1','4.1','4.2','5.1','6.1','A.1'])
            self.assertEqual(sum(n['kind']=='proof' for n in fiber_nodes),14)
            self.assertEqual(next(n['number'] for n in fiber_nodes if n['kind']=='diagnostic'),'5.2')
            self.assertEqual(next(n['number'] for n in fiber_nodes if n['title']=='Failure of negligible backreaction'),'5.1')
            self.assertEqual(fiber[0].equation_numbers['eq:back-overdraw'],'5.6')
            self.assertEqual(fiber[0].labels['ch:canonical']['reference_label'],'Chapter 3')
            self.assertEqual(fiber[0].macros['BridgeOverdraw'],r'2.6272875374\times 10^{20}')
            self.assertEqual(fiber[0].macros['PB'],dict(arguments=2,body=r'\left\{#1,#2\right\}'))
            from physics_fiber import MAIN as FIBER_MAIN, BASE as FIBER_BASE, VALUES
            self.assertIn(VALUES,reader.records)
            expected_displays = {'1':4,'2':32,'3':16,'4':27,'5':30,'6':14}
            for spec,_,chapter in book['chapters']:
                if spec['treatment']!='fiber':continue
                native = [chapter.section_number()+'.'+str(i) for i in range(1,expected_displays.get(chapter.section_number(),0)+1)]
                self.assertEqual([v for values in chapter.display_equation_numbers.values() for v in values],native)
                markup = (output/spec['url']).read_text(encoding='utf-8')
                printed = re.findall(r'<span class="equation-number">(.*?)</span>',markup,re.S)
                self.assertEqual([n for span in printed for n in re.findall(r'\(([0-9AB]+\.[0-9]+)\)',span)],native)
            repeated = next(r for r in book['figure_assets'].values() if r['source']==FIBER_BASE+'figures/constraint_negative_controls.pdf')
            self.assertEqual(repeated['uses'],2)
            opening = (output/next(s['url'] for s in CHAPTERS if s['source']==FIBER_MAIN)).read_text(encoding='utf-8')
            self.assertIn('The controlling physical boundary',opening)
            self.assertIn('does not solve the coupled background and mode equations',opening)
            self.assertIn('conditional on the prescribed normalized distribution',opening)
            closing = (output/next(s['url'] for s in CHAPTERS if s['source']==FIBER_MAIN and s['title']=='Bibliographic scope')).read_text(encoding='utf-8')
            self.assertIn('No literature-priority or empirical-preference claim',closing)
            cosmos = [(s,c) for s,_,c in book['chapters'] if s['treatment']=='cosmology']
            self.assertEqual([n['number'] for _,c in cosmos for n in c.nodes if n['kind']=='section' and n['number']],
                [str(i) for i in range(1,22)]+['A','B','C'])
            self.assertEqual(sum(n['kind']=='proof' for _,c in cosmos for n in c.nodes),5)
            self.assertEqual(sum(n['kind']=='figure' for _,c in cosmos for n in c.nodes),54)
            self.assertEqual(len(DATA['cosmology_table_aids']),33)
            displays=[64,57,49,45,51,56,43,8,85,57,88,63,35,42,42,23,16,45,41,2,0]
            for spec,chapter in cosmos:
                number=chapter.section_number()
                native=[number+'.'+str(i) for i in range(1,displays[int(number)-1]+1)] if number.isdigit() and spec.get('book_chapter') else []
                self.assertEqual([v for values in chapter.display_equation_numbers.values() for v in values],native)
                markup=(output/spec['url']).read_text(encoding='utf-8')
                printed=re.findall(r'<span class="equation-number">(.*?)</span>',markup,re.S)
                self.assertEqual([v for span in printed for v in re.findall(r'\(([0-9ABC]+\.[0-9]+)\)',span)],native)
                for node in chapter.nodes:
                    for span in node.get('source_spans',[]):
                        from physics_cosmology import context
                        title,prose=context((ROOT/span['source']).read_text(encoding='utf-8'))
                        self.assertIn(chapter.inline(prose),markup)
                        self.assertIn('part'+span['source'].split('part')[-1]+', line 1',markup)
            labels=cosmos[0][1].labels
            for key,number in [('ch:hidden-detail-sector','8'),('ch:collisionless-boltzmann-observables','10'),
                    ('ch:subhalo-core-tidal-audit','19'),('thm:microcell-fof','16.2')]:
                self.assertEqual(labels[key]['number'],number)
            opening=(output/cosmos[0][0]['url']).read_text(encoding='utf-8')
            self.assertIn('The distribution is an input',opening)
            self.assertIn('not predictions of a demonstrated microscopic production process',opening)
            subhalo=next((output/s['url']).read_text(encoding='utf-8') for s,c in cosmos if s['source'].endswith('19_subhalo_core_tidal_audit.tex'))
            self.assertIn('0.943218',subhalo)
            self.assertEqual(cosmos[-1][1].macros['SCTBoundRatio'],'0.958333')
            self.assertNotIn(r'\SCTBoundMassZoom',subhalo)
            from check_reader_site import check_table_reading_aids
            units=next(a for a in DATA['cosmology_table_aids'] if a['source'].endswith('13_cmb_lensing_bmodes.tex') and a['id']=='L226')
            unit_page=next((output/s['url']).read_text(encoding='utf-8') for s,c in cosmos if s['source']==units['source'])
            with self.assertRaisesRegex(AssertionError,'Missing column headers'):
                check_table_reading_aids(unit_page.replace('scope="col"','',1),{units['id']:units})
            for spec in CHAPTERS:
                page = pages[spec['url']]
                self.assertEqual((page.h1, page.main, page.images_without_alt), (1, 1, 0))
                self.assertEqual(len(page.ids), len(set(page.ids)))
                markup = (output/spec['url']).read_text(encoding='utf-8')
                self.assertIn('reading-text-size', markup)
                self.assertNotRegex(markup, r'\\(?:foundationfigure|atlasfigure|gaugefigure|gravityfigure|adicfigure|sourcepointer|endhead|addcontentsline|needspace|hypertarget|cftbefore)')
            refs = (output/CHAPTERS[18]['url']).read_text(encoding='utf-8')
            for label in ['P1', 'P4', 'C1', 'C3']:
                self.assertIn('['+label+']', refs)
            gauge_refs = (output/next(s['url'] for s in CHAPTERS if s['source'].endswith('/gauge/references.tex'))).read_text(encoding='utf-8')
            for label in ['P1', 'P3', 'C1', 'C5']:
                self.assertIn('['+label+']', gauge_refs)
            gravity_refs = (output/next(s['url'] for s in CHAPTERS if s['source'].endswith('/gravity/references.tex'))).read_text(encoding='utf-8')
            for label in ['P1','P3','C1','C8']:
                self.assertIn('['+label+']',gravity_refs)
            self.assertIn('Painlevé',gravity_refs)
            adic_refs = (output/next(s['url'] for s in CHAPTERS if s['source'].endswith('/adic/references.tex'))).read_text(encoding='utf-8')
            adic_context = (output/next(s['url'] for s in CHAPTERS if s['source'].endswith('/adic/primary_context.tex'))).read_text(encoding='utf-8')
            for label in ['S1','S4']:
                self.assertIn('['+label+']',adic_refs)
            for label in ['C1','C5']:
                self.assertIn('['+label+']',adic_context)
            self.assertIn('adic-primary-context-and-scope-of-the-literature-check.html',adic_refs)
            self.assertIn('full PDF retrieval failed',adic_context)
            dirac_refs = (output/BOOK['bib_page']).read_text(encoding='utf-8')
            self.assertIn('Seydaoğlu', dirac_refs)
            self.assertIn('Schrödinger', dirac_refs)
            for entry in book['references']:
                self.assertIn('ref-'+entry['key'], pages[BOOK['bib_page']].ids)
            index = (output/BOOK['index']).read_text(encoding='utf-8')
            self.assertIn('HTML reading sequences', index)
            self.assertIn('60 original plates across 72 atlas pages',index)
            self.assertNotIn('26 atlas plates',index)
            self.assertIn('572-page', index)
            self.assertIn('adds no proof audit', index)
            destinations = [int(urlsplit(link).fragment.removeprefix('page=')) for link in pages[BOOK['index']].links
                            if urlsplit(link).fragment.startswith('page=')]
            self.assertEqual(destinations, [row['index_start']+1 for row in book['full_book']])
            self.assertEqual(len(destinations), 21)
            self.assertIn('fiber-computational-evidence-and-reproducibility.html',index)
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
                if not record.get('source'):
                    continue
                self.assertEqual(record['source_sha256'], hashlib.sha256((ROOT/record['source']).read_bytes()).hexdigest())
                if record['source'].endswith('.png'):
                    self.assertEqual((output/record['file_url']).read_bytes(), (ROOT/record['source']).read_bytes())


if __name__ == '__main__':
    unittest.main()
