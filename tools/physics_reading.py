"""Source-bound opening Physics installment: Projectors, Packets, and Transfer.

The full foundations treatment is included. Later treatments remain in the
complete PDF. Publication adds no proof review, experiment, or Lean execution.
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
MACROS = BASE + 'preamble.tex'
PAGE_MAP = ROOT + 'book/book_manifest.json'
ASSEMBLY = ROOT + 'book/assembly_validation.json'
PREFIX = 'read/' + WORK + '/'
DATA = json.loads(Path(__file__).with_name('physics_sections.json').read_text(encoding='utf-8'))
CHAPTERS = DATA['chapters']
BOOK = dict(work=WORK, label='Physics', title='Physics: Projectors, Packets, and Transfer',
    base=BASE, main=MAIN, macro_source=MACROS, bib=BASE+'foundations/references.tex',
    index=PREFIX+'index.html', bib_page=CHAPTERS[-1]['url'], chapters=CHAPTERS,
    custom_reader='physics', partial=True, main_chapters=16,
    bibliography_in_chapters=True, required_macros=[], statement_navigation=True,
    reader_controls=True, number_floats=True, show_figure_numbers=True,
    contents_groups=DATA['groups'],
    figure_receipts='assets/figures/physics-foundations/figures.json',
    table_reading_aids={('foundations/orientation.tex', 'L25'): dict(
        caption='Physics conventions', headers=['Convention', 'Meaning'], row_header_column=0)},
    require_table_reading_aids=True,
    reading_introduction='Begin with the complete foundations treatment: orthogonal packets, '
        'transfer currents, coarse balance, moving frames, mixed and open dynamics, '
        'refinement, positive effects, and the domains and limits of infinite systems. '
        'The original ten figures accompany the text.',
    reading_note='This is the opening HTML installment of the 572-page Physics book. '
        'The foundations treatment is complete here; the Dirac, generator, gauge, gravity, '
        'adic, matter and cosmology treatments, visual atlases and formal companions '
        'remain in the full PDF. Authored wording, equations and numbered statements '
        'are preserved. This reading edition adds no proof audit, scientific run or Lean execution.')


def mask(text):
    return ''.join('\n' if char == '\n' else ' ' for char in text)


def normalize(raw):
    """Translate only print wrappers, preserving source line positions."""
    from readable_chapters import clean_tex
    from foundational_reading import rewrite
    text = clean_tex(raw)
    lines = text.count('\n')
    text = re.sub(r'\\foundationfigure\[[^\]]+\]', r'\\foundationfigure', text)
    text = rewrite(text, 'foundationfigure', 2, lambda name, caption:
        r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{foundation_figures/'
        + name + r'.pdf}\caption{' + caption + r'}\end{figure}')
    text = rewrite(text, 'sourcepointer', 1, lambda prose: 'Source correspondence: ' + prose)
    text = re.sub(r'\\addcontentsline\{toc\}\{section\}\{[^{}]*\}|\\endhead\b',
                  lambda match: mask(match[0]), text)
    text = text.replace(r'\begin{equation}', r'\[').replace(r'\end{equation}', r'\]')
    text = text.replace(r'\begin{align}', r'\begin{align*}').replace(r'\end{align}', r'\end{align*}')
    # Keep the source's P1-P4 and C1-C3 bibliography labels visible.
    for prefix in ('P', 'C'):
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


def source_macros(load):
    from readable_chapters import manuscript_macros, group
    text = load(MACROS)
    macros = manuscript_macros(text, [])
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
    inputs = re.findall(r'\\input\{([^{}]+)\}', load(MAIN))
    if inputs != ['preamble.tex', *DATA['selected_inputs']]:
        raise ValueError('Review Physics foundations input order')
    for name in DATA['selected_inputs']:
        source = BASE + name
        specs = [spec for spec in CHAPTERS if spec['source'] == source]
        if specs[0]['start_line'] != 1 or specs[-1]['end_line'] != len(load(source).splitlines()):
            raise ValueError('Physics selection omits source boundaries')
        for left, right in zip(specs, specs[1:]):
            if left['end_line'] + 1 != right['start_line']:
                raise ValueError('Physics source ranges have a gap or overlap')
    return CHAPTERS


def source_math(raw, spec):
    from readable_chapters import original_math, chapter_text
    return original_math(normalize(chapter_text(raw, spec)))


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
    main = load(MAIN)
    macros = source_macros(load)
    chapters, labels, equations = [], {}, {}
    state = {'number_floats': True}
    equation_counter = 0  # The retained article uses one global equation counter.
    for spec in config['chapters']:
        raw = reader.site.read_source(reader.add(spec['source']))
        selected = reading.chapter_text(raw.decode('utf-8-sig'), spec)
        chapter = reading.Chapter(normalize(selected), macros, state=state, check_refs=False)
        chapter.url, chapter.base, chapter.source = spec['url'], BASE, spec['source']
        chapter.bibliography_url = config['bib_page']
        chapter.macro_source = MACROS
        chapter.table_config = config
        chapter.table_aids_used, chapter.nested_tables, chapter.proof_pairs = set(), [], {}
        for i, node in enumerate(chapter.nodes):
            if node['kind'] in reading.NUMBERED and i+1 < len(chapter.nodes) and chapter.nodes[i+1]['kind'] == 'proof':
                chapter.proof_pairs[node['id']] = chapter.nodes[i+1]['id']
        for key, node in chapter.labels.items():
            if key in labels:
                raise ValueError('Repeated Physics label: ' + key)
            node['url'] = chapter.url
            labels[key] = dict(node, reference_label=node['number'] or node['title'])
        for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', selected, re.S):
            rows = [match[2]] if match[1] == 'equation' else [row for row in reading.split_cells(match[2], r'\\') if row.strip()]
            for row in rows:
                if r'\notag' in row or r'\nonumber' in row:
                    continue
                equation_counter += 1
                for key in re.findall(r'\\label\{([^{}]+)\}', row):
                    equations[key] = str(equation_counter)
        state = {key: getattr(chapter, key) for key in (
            'section', 'appendix', 'part', 'subsection', 'subsubsection', 'counter',
            'section_prefix', 'figure', 'table', 'number_floats')}
        chapters.append((spec, raw, chapter))
    for key, number in equations.items():
        labels[key].update(reference_label=number, equation_number=number)
    for _, _, chapter in chapters:
        chapter.labels, chapter.equation_numbers = labels, equations
        chapter.validate_references()
    from reader_figure_assets import prepare
    return dict(config=config, chapters=chapters, references=[], macros=macros, main=main,
                full_book=manifest, figure_assets=prepare(reader, config, chapters))


def full_book_routes(reader, book, page):
    """Continue at the actual PDF page, including its unnumbered preliminaries."""
    pdf = reader.records.get(ROOT+'Komorebi_Physics.pdf')
    if not pdf:
        raise ValueError('Missing complete Physics PDF')
    if pdf['sha256'] != json.loads(reader.site.read_source(reader.records[ASSEMBLY]))['output_sha256']:
        raise ValueError('Physics page map is bound to a different PDF')
    body = ('<section aria-labelledby="source-continuations"><h2 id="source-continuations">Continue in the full Physics book</h2>'
        '<p>The complete 572-page PDF contains all six parts below. Each PDF link opens at '
        'the beginning of that treatment. The HTML installment above covers Projectors, Packets, and Transfer.</p>')
    part = None
    for row in book['full_book']:
        if part != row['part']:
            if part is not None:
                body += '</ul>'
            part = row['part']
            body += '<h3>Part '+part+': '+html.escape(row['part_title'])+'</h3><ul>'
        link = reader.viewer_url(pdf, page, 'page='+str(row['index_start']+1))
        body += '<li><a href="'+html.escape(link,quote=True)+'">'+html.escape(row['title'])+' (PDF)</a> — '+html.escape(row['deck'])+'</li>'
    return body+'</ul></section>'
