"""Complete, source-bound HTML edition of The Komorebi Methodology."""
import hashlib
import json
from pathlib import Path
import re

WORK = 'komorebi-methodology'
BASE = 'monographs/' + WORK + '/'
MAIN = BASE + 'Komorebi_Methodology.tex'
ESSAY = BASE + 'essay.tex'
SOURCES = BASE + 'sources.tex'
DATA = json.loads(Path(__file__).with_name('methodology_sections.json').read_text(encoding='utf-8'))
CHAPTERS = DATA['chapters']
BOOK = dict(work=WORK, label='Komorebi Methodology', base=BASE, main=MAIN,
    bib=SOURCES, index='read/' + WORK + '/index.html',
    bib_page='read/' + WORK + '/references.html', chapters=CHAPTERS,
    title='Mathematical Discovery, Realization, and the Discipline of Proof',
    main_chapters=9, custom_reader='methodology', inline_bibliography=True,
    numbered_bibliography=True, number_floats=True, show_figure_numbers=True,
    required_macros=[], figure_receipts='assets/figures/' + WORK + '/figures.json',
    reading_introduction='Read the complete essay, from its preface and nine chapters '
        'to the closing reflection, source notes, and references. Equations and '
        'the three original diagrams appear alongside the text.',
    reading_note='The chapters preserve the retained manuscript and its evidence '
        'limits. The complete 28-page PDF and source package remain available. '
        'This HTML edition adds no formalization or mathematical proof audit.')


def mask(text):
    return ''.join('\n' if char == '\n' else ' ' for char in text)


def normalize(source):
    """Translate the declared print wrappers without moving source-line anchors."""
    from readable_chapters import clean_tex
    from foundational_reading import rewrite
    text = clean_tex(source)
    count = text.count('\n')
    text = rewrite(text, 'essaychapter', 1, lambda title: r'\section{' + title + '}')
    text = rewrite(text, 'sourceref', 1, lambda key: r'\cite{' + key + '}')
    text = rewrite(text, 'deck', 1, lambda prose: prose)
    text = text.replace(r'\begin{argumentbox}', r'\begin{keyidea}').replace(r'\end{argumentbox}', r'\end{keyidea}')
    text = re.sub(r'\\vspace\{\.6em\}|\\vfill\b', lambda m: mask(m[0]), text)
    text = re.sub(r'\\setlength\{\\itemsep\}\{8pt\}|\\renewcommand\{\\refname\}\{References\}', lambda m: mask(m[0]), text)
    # The printed article has secnumdepth=1, and a single global equation counter.
    text = re.sub(r'\\subsection(?!\*)\{', r'\\subsection*{', text)
    text = text.replace(r'\begin{equation}', r'\[').replace(r'\end{equation}', r'\]')
    text = re.sub(r'\\begin\{figure\}\[htbp\]', r'\\begin{figure}', text)
    text = re.sub(r'\\includegraphics\[width=(?:\.91)?\\linewidth\]', r'\\includegraphics[width=.96\\linewidth]', text)
    if text.count('\n') != count:
        raise ValueError('Methodology translation moved source lines')
    return text


def source_math(source, spec):
    from readable_chapters import chapter_text, original_math
    return original_math(normalize(chapter_text(source, spec)))


def source_specs(load):
    for path, expected in DATA['source_sha256'].items():
        if hashlib.sha256(load(path).encode()).hexdigest() != expected:
            raise ValueError('Review changed methodology source: ' + path)
    if re.findall(r'\\input\{([^{}]+)\}', load(MAIN)) != ['essay', 'sources']:
        raise ValueError('Review methodology input order')
    # All substantive text, including the preface scope note and source notes,
    # is covered exactly once. The print cover and automatic contents are omitted.
    expected = {MAIN: (113, 127), ESSAY: (1, 395), SOURCES: (1, 18)}
    for path, (start, end) in expected.items():
        selected = [spec for spec in CHAPTERS if spec['source'] == path]
        if selected[0]['start_line'] != start or selected[-1]['end_line'] != end:
            raise ValueError('Review methodology reading coverage')
        for left, right in zip(selected, selected[1:]):
            if left['end_line'] + 1 != right['start_line']:
                raise ValueError('Methodology source ranges overlap or omit text')
    return CHAPTERS


def prepare_book(reader, config):
    import readable_chapters as reading
    def load(path):
        record = reader.add(path)
        if not record:
            raise ValueError('Missing receipt-bound methodology source: ' + path)
        return reader.site.read_source(record).decode('utf-8-sig')
    source_specs(load)
    main = load(MAIN)
    macros = reading.manuscript_macros(main, [])
    references = reading.manuscript_bibliography(normalize(load(SOURCES)))
    if len(references) != 9:
        raise ValueError('Review methodology bibliography inventory')
    chapters, labels, equations = [], {}, {}
    state = {'number_floats': True}
    counter = 0
    for spec in config['chapters']:
        raw = reader.site.read_source(reader.add(spec['source']))
        text = reading.chapter_text(raw.decode('utf-8-sig'), spec)
        chapter = reading.Chapter(normalize(text), macros, state=state, check_refs=False)
        chapter.url = spec['url']
        chapter.base = BASE
        chapter.source = spec['source']
        chapter.bibliography_url = config['bib_page']
        for key, node in chapter.labels.items():
            if key in labels:
                raise ValueError('Repeated methodology label: ' + key)
            node['url'] = chapter.url
            labels[key] = dict(node, reference_label=node['number'] or node['title'])
        for match in re.finditer(r'\\begin\{equation\}(.*?)\\end\{equation\}', text, re.S):
            counter += 1
            for key in re.findall(r'\\label\{([^{}]+)\}', match[1]):
                equations[key] = str(counter)
        state = {key: getattr(chapter, key) for key in (
            'section', 'appendix', 'part', 'subsection', 'subsubsection', 'counter',
            'section_prefix', 'figure', 'table', 'number_floats')}
        chapters.append((spec, raw, chapter))
    for key, number in equations.items():
        labels[key]['reference_label'] = number
        labels[key]['equation_number'] = number
    for spec, raw, chapter in chapters:
        chapter.labels = labels
        chapter.equation_numbers = equations
        chapter.validate_references()
        chapter.citations = {entry['key']: (str(i), chapter.relative(config['bib_page']) + '#ref-' + entry['key'])
                              for i, entry in enumerate(references, 1)}
    from reader_figure_assets import prepare
    return dict(config=config, chapters=chapters, references=references, macros=macros,
                main=main, figure_assets=prepare(reader, config, chapters))
