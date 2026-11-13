"""Source-bound Physics foundations, Dirac, generator, gauge, gravity, adic, fiber, and cosmology treatments.

The treatments, visual atlases, verification scope and companions have separate
HTML sequences. Publication adds no proof review, experiment, or Lean execution.
"""
import hashlib
import html
import json
from pathlib import Path
import re

WORK = 'monographs-physics'
ROOT = 'monographs/physics/'
BASE = ROOT + 'source/monographs/'
MAIN = BASE + 'Physics_Foundations_Monograph.tex'
DIRAC_MAIN = BASE + 'Physics_Dirac_Monograph.tex'
DIRAC_FINITE = BASE + 'chapters/finite_core.tex'
GENERATOR_BASE = ROOT + 'source/generator/'
GENERATOR_MAIN = GENERATOR_BASE + 'Block50_Spectral_Generator_Bridge.tex'
MACROS = BASE + 'preamble.tex'
PAGE_MAP = ROOT + 'book/book_manifest.json'
ASSEMBLY = ROOT + 'book/assembly_validation.json'
PREFIX = 'read/' + WORK + '/'
DATA = json.loads(Path(__file__).with_name('physics_sections.json').read_text(encoding='utf-8'))
CHAPTERS = DATA['chapters']
BOOK = dict(work=WORK, label='Physics', title='Physics: Resolution, dynamics, and constrained geometry',
    base=BASE, main=MAIN, macro_source=MACROS, bib=BASE+'references.tex',
    index=PREFIX+'index.html', bib_page=PREFIX+'dirac-sources-and-further-reading.html', chapters=CHAPTERS,
    custom_reader='physics', partial=False, main_chapters=len(CHAPTERS),
    atlas_index=PREFIX+'atlas/index.html',
    verification_index=PREFIX+'verification/index.html',
    atlas_link_text='Explore 60 original plates across 72 atlas pages',
    atlas_note='Five complete visual atlases, with authored explanations and source links.',
    statement_scope='in the Physics treatments',
    bibliography_in_chapters=True, numbered_bibliography=True, required_macros=[], statement_navigation=True,
    lean_reader_paths=['formal/continuum/KomorebiPhysics/'],
    reader_controls=True, number_floats=True, show_figure_numbers=True,
    contents_groups=DATA['groups'],
    figure_receipts='assets/figures/physics-foundations/figures.json',
    table_reading_aids={('foundations/orientation.tex', 'L25'): dict(
        caption='Physics conventions', headers=['Convention', 'Meaning'], row_header_column=0),
        ('chapters/orientation.tex', 'L23'): dict(caption='Objects in the Dirac construction',
            headers=['Object', 'Meaning in this volume'], row_header_column=0),
        ('chapters/finite_core.tex', 'L821'): dict(caption='Exact three-mode momenta',
            headers=['Mode', r'\(p(n)\)', r'\(q_h(n)\)'], row_header_column=0),
        ('chapters/finite_core.tex', 'L838'): dict(caption='Exact three-mode shell energies',
            headers=['Mode', r'\(E_n\)', r'\(E_{h,n}\)'], row_header_column=0),
        ('chapters/boundary.tex', 'L8'): dict(caption='The completed operator construction',
            headers=['Construction', 'Mathematical role'], row_header_column=0),
        (GENERATOR_MAIN, 'L268'): dict(caption='Generator, resolvent, and evolution limits',
            headers=[r'\textbf{Statement}', r'\textbf{Input}', r'\textbf{Conclusion}'], row_header_column=0),
        ('gauge/orientation.tex', 'L21'): dict(caption='Gauge transport conventions',
            headers=['Convention', 'Meaning'], row_header_column=0),
        ('gravity/orientation.tex', 'L21'): dict(caption='Gravity conventions and evidence',
            headers=['Convention', 'Meaning'], row_header_column=0),
        ('gravity/strong_fields.tex', 'L317'): dict(caption='Recorded electrovac state errors',
            headers=[r'$N$',r'$\norm{\delta R}_\infty$',r'$\norm{\delta\Lambda}_\infty$',
                r'$\norm{\delta P_\Lambda}_\infty$',r'$\norm{\delta P_R}_\infty$'],row_header_column=0),
        ('gravity/strong_fields.tex', 'L514'): dict(caption='Archived scalar marginal-sphere events',
            headers=[r'$N_r$',r'$h$',r'$t_H$',r'$r_H$',r'$\Delta M/M_0$'],row_header_column=0),
        ('gravity/strong_fields.tex', 'L557'): dict(caption='Recorded scalar constraint and flux residuals',
            headers=['Diagnostic','Relative residual'],row_header_column=0),
        ('adic/orientation.tex', 'L20'): dict(caption='Adic refinement conventions',
            headers=['Convention','Meaning'],row_header_column=0),
        ('adic/finite.tex', 'L835'): dict(caption='Per-leaf and collective coupling choices',
            headers=['Per-leaf choice',r'$\alpha$',r'$|G_{p,w}|$',r'$|G_{p,w}|^2$'],row_header_column=0)},
    require_table_reading_aids=True,
    reading_introduction='Read the complete foundations, continuum Dirac, spectral generator, gauge, gravity, adic, covariant fiber and cosmology treatments. '
        'Begin with packets, currents, open dynamics, refinement and operator domains; '
        'continue through PH01–PH12, the exact three-mode example, Fourier completion '
        'and the self-adjoint Hamiltonian on the three-torus, then its strong generator, resolvent limits '
        'and quantitative evolution estimates. Continue to endpoint covariance, finite matter–field dynamics, '
        'ordered holonomy and geometric refinement, then constrained geometry, regular canonical reduction '
        'and spherical strong-field models. Arithmetic refinement follows through normalized Haar packets, '
        'spectral elimination and compatible Hilbert-space limits. The covariant fiber model follows through '
        'stress exchange, canonical closure, production and ultraviolet bounds, including its failed benchmark '
        'energy test and the computational evidence appendix. Cosmology continues from a prescribed distribution '
        'through background and perturbation geometry, kinetic transport, CMB, nonlinear structure, baryonic '
        'response and linked rejection tests. One hundred four original figures accompany the text.',
    reading_note='These HTML reading sequences accompany the 572-page Physics book. '
        'The foundations, continuum Dirac, spectral generator, gauge, gravity, adic, covariant fiber and cosmology treatments are complete here; '
        'all five visual atlases, the verification scope and five formalization and verification companions '
        'are also available in HTML. Authored wording, equations and numbered statements '
        'are preserved. This reading edition adds no proof audit, scientific run or Lean execution.')
BOOK['table_reading_aids'].update({(row['source'],row['id']):
    {key:value for key,value in row.items() if key not in {'source','id'}}
    for row in DATA['fiber_table_aids']+DATA['cosmology_table_aids']})
from physics_discovery import reading_summary
BOOK['reading_page_summary']=reading_summary()


def mask(text):
    return ''.join('\n' if char == '\n' else ' ' for char in text)


def finite_statements(text):
    """Expose the authored PH identifiers and literal proof boundaries."""
    from readable_chapters import group
    pattern = r'\\textbf\{(?:Proposition|Theorem|Example) PH\d\d \(|\\textbf\{Lemma \(finite Hermitian'
    for match in reversed(list(re.finditer(pattern, text))):
        heading, end = group(text, match.start()+len(r'\textbf'))
        numbered = re.fullmatch(r'(Proposition|Theorem|Example) (PH\d\d) \((.*)\)\.', heading, re.S)
        if numbered:
            kind, number, title = numbered.groups()
        else:
            kind, number, title = 'Lemma', '', 'finite Hermitian Duhamel estimate'
        kind = kind.lower()
        if number == 'PH10':
            boundary = text.index(r'\atlasfigure{06_packet_evolution}', end)
            text = text[:boundary]+r'\end{example}'+text[boundary:]
        else:
            proof = text.index(r'\emph{Proof.}', end)
            finish = text.index(r'\(\square\)', proof)+len(r'\(\square\)')
            text = text[:finish]+r'\end{proof}'+text[finish:]
            text = text[:proof]+r'\end{'+kind+r'}\begin{proof}'+text[proof+len(r'\emph{Proof.}'):]
        replacement = r'\begin{'+kind+'}['+title+']'
        replacement += '\n'*(text[match.start():end].count('\n')-replacement.count('\n'))
        text = text[:match.start()]+replacement+text[end:]
    return text


def normalize(raw, treatment=None, load=None):
    """Translate only print wrappers, preserving source line positions."""
    from readable_chapters import clean_tex
    from foundational_reading import rewrite
    text = clean_tex(raw)
    lines = text.count('\n')
    if treatment == 'cosmology':
        from physics_cosmology import normalize as cosmology_normalize
        text = cosmology_normalize(text, load)
    if r'\chapter{' in text or r'\PhysicsOpening{07 / Matter' in text or r'\section*{Bibliographic scope}' in text:
        from physics_fiber import normalize as fiber_normalize
        text = fiber_normalize(text)
    text = rewrite(text, 'PhysicsOpening', 3, lambda kicker, title, subtitle:
        r'\section*{'+title+r'}\textit{'+subtitle+r'}\par '+kicker+r'\par ')
    text = rewrite(text, 'hypertarget', 2, lambda target, body: body)
    text = finite_statements(text)
    text = re.sub(r'\\foundationfigure\[[^\]]+\]', r'\\foundationfigure', text)
    text = rewrite(text, 'foundationfigure', 2, lambda name, caption:
        r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{foundation_figures/'
        + name + r'.pdf}\caption{' + caption + r'}\end{figure}')
    text = re.sub(r'\\gaugefigure\[[^\]]+\]', r'\\gaugefigure', text)
    text = rewrite(text, 'gaugefigure', 2, lambda name, caption:
        r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{gauge_figures/'
        + name + r'.pdf}\caption{' + caption + r'}\end{figure}')
    text = re.sub(r'\\gravityfigure\[[^\]]+\]', r'\\gravityfigure', text)
    text = rewrite(text, 'gravityfigure', 2, lambda name, caption:
        r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{gravity_figures/'
        + name + r'.pdf}\caption{' + caption + r'}\end{figure}')
    text = re.sub(r'\\adicfigure\[[^\]]+\]', r'\\adicfigure', text)
    text = rewrite(text, 'adicfigure', 2, lambda name, caption:
        r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{adic_figures/'
        + name + r'.pdf}\caption{' + caption + r'}\end{figure}')
    text = re.sub(r'\\setlength\{\\cftbefore(?:sec|part)skip\}\{[^{}]*\}',
                  lambda match: mask(match[0]), text)
    text = rewrite(text, 'atlasfigure', 2, lambda name, caption:
        r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{figures/'
        + name + r'.pdf}\caption{' + caption + r'}\end{figure}')
    text = rewrite(text, 'sourcepointer', 1, lambda prose: 'Source correspondence: ' + prose)
    text = re.sub(r'\\addcontentsline\{toc\}\{(?:section|chapter)\}\{[^{}]*\}|\\endhead\b',
                  lambda match: mask(match[0]), text)
    text = re.sub(r'\\needspace\{[^{}]*\}|\\begin\{center\}|\\end\{center\}|'
                  r'\\renewcommand\{\\refname\}\{[^{}]*\}', lambda match: mask(match[0]), text)
    text = text.replace(r'\begin{equation}', r'\[').replace(r'\end{equation}', r'\]')
    text = text.replace(r'\begin{align}', r'\begin{align*}').replace(r'\end{align}', r'\end{align*}')
    # Keep the source's explicit project and context bibliography labels visible.
    for prefix in ('P', 'C', 'S'):
        pattern = r'\\begin\{enumerate\}\[label=\{\['+prefix+r'\\arabic\*\]\},leftmargin=2\.5em\](.*?)\\end\{enumerate\}'
        def references(match, prefix=prefix):
            count = 0
            def label(item):
                nonlocal count
                count += 1
                return r'\item ['+prefix+str(count)+']'
            return r'\begin{itemize}'+re.sub(r'\\item\b', label, match[1])+r'\end{itemize}'
        text = re.sub(pattern, references, text, flags=re.S)
    if text.count('\n') != lines:
        raise ValueError('Physics translation moved source lines')
    return text


def macro_source(spec):
    if spec.get('treatment') == 'cosmology':
        from physics_cosmology import MAIN as COSMOLOGY_MAIN
        return COSMOLOGY_MAIN
    if spec.get('treatment') == 'fiber':
        from physics_fiber import MAIN as FIBER_MAIN
        return FIBER_MAIN
    return GENERATOR_MAIN if spec['source'] == GENERATOR_MAIN else MACROS


def source_macros(load, spec=None):
    if spec and spec.get('treatment') == 'cosmology':
        from physics_cosmology import macros
        return macros(load)
    if spec and spec.get('treatment') == 'fiber':
        from physics_fiber import macros
        return macros(load)
    from readable_chapters import manuscript_macros, group
    text = load(macro_source(spec) if spec else MACROS)
    macros = manuscript_macros(text, [])
    if spec and spec['source'] == GENERATOR_MAIN:
        match = re.search(r'\\newcommand\{\\pp\}\[1\]', text)
        if not match:
            raise ValueError('Missing Physics generator norm macro')
        body, _ = group(text, match.end())
        macros['pp'] = dict(arguments=1, body=body, token_arguments=True)
        return macros
    match = re.search(r'\\providecommand\{\\inner\}\[2\]', text)
    if not match:
        raise ValueError('Missing Physics inner-product macro')
    body, _ = group(text, match.end())
    macros['inner'] = dict(arguments=2, body=body)
    return macros


def source_specs(load):
    for path, expected in DATA['source_sha256'].items():
        if hashlib.sha256(load(path).encode()).hexdigest() != expected:
            raise ValueError('Review changed Physics source: ' + path)
    expected_blocks = []
    for treatment in DATA['treatments']:
        inputs = re.findall(r'\\input\{([^{}]+)\}', load(treatment['main']))
        if inputs != [*treatment.get('layout_inputs', ['preamble.tex']), *treatment['inputs']]:
            raise ValueError('Review Physics treatment input order')
        sources = []
        def include(name, ancestors=()):
            if name in ancestors:
                raise ValueError('Repeated Physics nested input')
            source = BASE+name
            sources.append(source)
            raw = load(source)
            declared = re.findall(r'\\input\{([^{}]+)\}', raw)
            if declared != treatment.get('nested_inputs', {}).get(name, []):
                raise ValueError('Review Physics nested input order')
            if declared:
                # Separate reading pages can preserve inclusion order only when
                # the included member follows the parent's last prose passage.
                from readable_chapters import clean_tex
                if clean_tex(raw[raw.index(r'\input{'):]).strip() != ''.join(r'\input{'+p+'}' for p in declared):
                    raise ValueError('Review Physics nested input position')
            for child in declared:
                include(child, (*ancestors, name))
        if treatment.get('book_body'):
            if treatment['id']=='cosmology':
                from physics_cosmology import source_blocks
            else:
                from physics_fiber import source_blocks
            blocks = source_blocks(load, treatment)
            sources = [block[0] for block in blocks]
        elif treatment.get('standalone'):
            sources = [treatment['main']]
        else:
            for name in treatment['inputs']:
                include(name)
        if not treatment.get('book_body'):
            blocks = []
            for source in sources:
                raw = load(source)
                start, end = 1, len(raw.splitlines())
                if source == GENERATOR_MAIN:
                    start = raw.count('\n', 0, raw.index(r'\begin{document}'))+2
                    end = raw.count('\n', 0, raw.index(r'\end{document}'))
                blocks.append((source, start, end))
        expected_blocks.extend(blocks)
        if any(spec['treatment'] != treatment['id'] for spec in CHAPTERS
               if spec['source'] in sources):
            raise ValueError('Physics source belongs to the wrong treatment')
    actual_sources = [spec['source'] for i, spec in enumerate(CHAPTERS)
                      if i == 0 or spec['source'] != CHAPTERS[i-1]['source']]
    if actual_sources != [block[0] for block in expected_blocks]:
        raise ValueError('Physics reading order differs from the retained treatments')
    from itertools import groupby
    groups = [list(specs) for _, specs in groupby(CHAPTERS, key=lambda s:s['source'])]
    for (source, start, end), specs in zip(expected_blocks, groups):
        if specs[0]['start_line'] != start or specs[-1]['end_line'] != end:
            raise ValueError('Physics selection omits source boundaries')
        for left, right in zip(specs, specs[1:]):
            if left['end_line'] + 1 != right['start_line']:
                raise ValueError('Physics source ranges have a gap or overlap')
    return CHAPTERS


def source_math(raw, spec):
    from readable_chapters import original_math, chapter_text
    return original_math(normalize(chapter_text(raw, spec), spec.get('treatment')))


def prepare_book(reader, config):
    import readable_chapters as reading
    def load(path):
        record = reader.add(path)
        if not record:
            raise ValueError('Missing retained Physics source: ' + path)
        return reader.site.read_source(record).decode('utf-8-sig')
    source_specs(load)
    manifest = json.loads(load(PAGE_MAP))
    assembly = json.loads(load(ASSEMBLY))
    if assembly['page_count'] != 572 or len(manifest) != assembly['contents_entries']:
        raise ValueError('Review Physics full-book navigation')
    if any(not 0 <= row['index_start'] < 572 for row in manifest):
        raise ValueError('Physics PDF destination outside full book')
    from physics_discovery import destination
    for row in manifest:destination(row)
    main = load(MAIN)
    macros = source_macros(load)
    references = reading.manuscript_bibliography(load(config['bib']))
    for reference in references:
        reference['body'] = reading.tex_accents(reference['body'].replace(r'\u{g}', 'ğ'))
    chapters, labels, equations = [], {}, {}
    state = {'number_floats': True}
    equation_counter = 0  # The retained article uses one global equation counter.
    treatment = None
    for spec in config['chapters']:
        if spec['treatment'] != treatment:
            treatment = spec['treatment']
            state, equation_counter = {'number_floats': True}, 0
        if spec.get('book_chapter'):
            if spec.get('book_appendix') and not state.get('appendix'):
                state.update(appendix=True, section=0)
            state.update(figure=0, table=0)
            equation_counter = 0
        raw = reader.site.read_source(reader.add(spec['source']))
        selected = reading.chapter_text(raw.decode('utf-8-sig'), spec)
        chapter_macros = source_macros(load, spec)
        if treatment == 'cosmology':
            from physics_cosmology import make_chapter
            chapter = make_chapter(normalize(selected,treatment,load),chapter_macros,state)
        else:
            chapter = reading.Chapter(normalize(selected,treatment,load), chapter_macros, state=state, check_refs=False)
        chapter.url, chapter.base, chapter.source = spec['url'], BASE, spec['source']
        chapter.bibliography_url = config['bib_page']
        chapter.macro_source = macro_source(spec)
        chapter.table_config = config
        chapter.table_aids_used, chapter.nested_tables, chapter.proof_pairs = set(), [], {}
        if treatment == 'cosmology':
            from physics_cosmology import context_provenance
            context_provenance(chapter,selected)
        if treatment in {'fiber','cosmology'}:
            from physics_fiber import display_equation_numbers
            chapter.display_equation_numbers = display_equation_numbers(selected,chapter.section_number())
            for node in chapter.nodes:
                if node['kind'] in {'figure','longtable','table'} and node['number']:
                    node['number'] = chapter.section_number()+'.'+node['number']
        if spec['source'] == DIRAC_FINITE:
            records = {row['line']: row for row in DATA['dirac_statements']}
            for node in chapter.nodes:
                if node['kind'] not in reading.NUMBERED:
                    continue
                row = records.get(node['line'])
                if not row or (node['kind'], node['title']) != (row['kind'], row['title']):
                    raise ValueError('Review the authored PH statement identity')
                node['number'] = row['number']
        if treatment == 'dirac':
            for node in chapter.nodes:
                if node['kind'] == 'figure':
                    node['number'] = ''  # The retained atlasfigure macro has no float counter.
        for i, node in enumerate(chapter.nodes):
            if node['kind'] in reading.NUMBERED and i+1 < len(chapter.nodes) and chapter.nodes[i+1]['kind'] == 'proof':
                chapter.proof_pairs[node['id']] = chapter.nodes[i+1]['id']
        for key, node in chapter.labels.items():
            if key in labels:
                raise ValueError('Repeated Physics label: ' + key)
            node['url'] = chapter.url
            labels[key] = dict(node, reference_label=node['number'] or node['title'])
            if treatment in {'fiber','cosmology'}:
                kind = {'section':'Appendix' if chapter.appendix else 'Chapter','subsection':'Section','subsubsection':'Subsection'}.get(node['kind'],reading.KIND_NAMES.get(node['kind'],node['kind'].capitalize()))
                labels[key].update(reference_label=kind+' '+node['number'],plain_reference_label=node['number'],treatment=treatment)
                if treatment=='cosmology' and key.startswith('ch:'):
                    heading = next(n for n in chapter.nodes if n['kind']=='section')
                    labels[key].update(id=heading['id'],number=heading['number'],
                        reference_label='Chapter '+heading['number'],plain_reference_label=heading['number'])
        for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', selected, re.S):
            rows = [match[2]] if match[1] == 'equation' else [row for row in reading.split_cells(match[2], r'\\') if row.strip()]
            for row in rows:
                if r'\notag' in row or r'\nonumber' in row:
                    continue
                equation_counter += 1
                for key in re.findall(r'\\label\{([^{}]+)\}', row):
                    equations[key] = (chapter.section_number()+'.' if treatment in {'fiber','cosmology'} else '')+str(equation_counter)
        state = {key: getattr(chapter, key) for key in (
            'section', 'appendix', 'part', 'subsection', 'subsubsection', 'counter',
            'section_prefix', 'figure', 'table', 'number_floats')}
        chapters.append((spec, raw, chapter))
    for key, number in equations.items():
        labels[key].update(reference_label=number, equation_number=number)
        if labels[key].get('treatment') in {'fiber','cosmology'}:
            labels[key].update(reference_label='Equation ('+number+')',plain_reference_label=number)
    for _, _, chapter in chapters:
        chapter.labels, chapter.equation_numbers = labels, equations
        chapter.citations = {row['key']: (str(i), chapter.relative(config['bib_page'])+'#ref-'+row['key'])
                             for i, row in enumerate(references, 1)}
        chapter.validate_references()
    from reader_figure_assets import prepare
    figures = prepare(reader, config, [row for row in chapters if row[0]['treatment']=='foundations'])
    figures.update(prepare(reader, dict(config, figure_receipts='assets/figures/physics-dirac/figures.json'),
                           [row for row in chapters if row[0]['treatment']=='dirac']))
    figures.update(prepare(reader, dict(config, figure_source_root=GENERATOR_BASE,
        figure_receipts='assets/figures/physics-generator/figures.json'),
        [row for row in chapters if row[0]['treatment']=='generator']))
    figures.update(prepare(reader, dict(config, figure_receipts='assets/figures/physics-gauge/figures.json'),
        [row for row in chapters if row[0]['treatment']=='gauge']))
    figures.update(prepare(reader, dict(config, figure_receipts='assets/figures/physics-gravity/figures.json'),
        [row for row in chapters if row[0]['treatment']=='gravity']))
    figures.update(prepare(reader, dict(config, figure_receipts='assets/figures/physics-adic/figures.json'),
        [row for row in chapters if row[0]['treatment']=='adic']))
    from physics_fiber import BASE as FIBER_BASE
    figures.update(prepare(reader, dict(config, figure_source_root=FIBER_BASE,
        figure_receipts='assets/figures/physics-fiber/figures.json'),
        [row for row in chapters if row[0]['treatment']=='fiber']))
    from physics_cosmology import BASE as COSMOLOGY_BASE
    figures.update(prepare(reader, dict(config, figure_source_root=COSMOLOGY_BASE,
        figure_receipts='assets/figures/physics-cosmology/figures.json'),
        [row for row in chapters if row[0]['treatment']=='cosmology']))
    book=dict(config=config, chapters=chapters, references=references, macros=macros, main=main,
                full_book=manifest, figure_assets=figures)
    from physics_visual import prepare as prepare_visual
    prepare_visual(reader,book)
    from physics_companions import prepare as prepare_companions
    prepare_companions(reader,book)
    return book


def full_book_routes(reader, book, page):
    """Continue at the actual PDF page, including its unnumbered preliminaries."""
    pdf = reader.records.get(ROOT+'Komorebi_Physics.pdf')
    if not pdf:
        raise ValueError('Missing complete Physics PDF')
    if pdf['sha256'] != json.loads(reader.site.read_source(reader.records[ASSEMBLY]))['output_sha256']:
        raise ValueError('Physics page map is bound to a different PDF')
    body = ('<section aria-labelledby="source-continuations"><h2 id="source-continuations">Continue in the full Physics book</h2>'
        '<p>The complete 572-page PDF contains all six parts below. Each PDF link opens at '
        'the beginning of that treatment. The HTML installments above cover the complete foundations, '
        'continuum Dirac, spectral generator, gauge, gravity, adic, covariant fiber and cosmology treatments, '
        'including the fiber computational evidence appendix and the cosmology reproduction limits.</p>'
        '<p><a href="'+html.escape(reader.site.rel('read/monographs-physics/verification/index.html',page),quote=True)+'">Read the verification scope and formalization companions</a>.</p>')
    part = None
    for row in book['full_book']:
        if part != row['part']:
            if part is not None:
                body += '</ul>'
            part = row['part']
            body += '<h3>Part '+part+': '+html.escape(row['part_title'])+'</h3><ul>'
        link = reader.viewer_url(pdf, page, 'page='+str(row['index_start']+1))
        body += '<li><a href="'+html.escape(link,quote=True)+'">'+html.escape(row['title'])+' (PDF)</a> — '+html.escape(row['deck'])
        from physics_discovery import destination
        target=destination(row)
        body+=' · <a href="'+html.escape(reader.site.rel(target['url'],page),quote=True)+'">'+target['label']+'</a>'
        body += '</li>'
    return body+'</ul></section>'
