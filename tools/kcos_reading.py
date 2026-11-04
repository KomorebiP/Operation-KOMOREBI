"""Receipt-bound full K-COS reading conversion.

Integration contract (the shared renderer is maintained separately):
* prepare_book(reader, BOOK) returns ordinary Chapter tuples for render_book.
* source_math(raw, spec, source_texts) takes the book's receipt-loaded
  source_texts dictionary (including the three nested inputs), or a callable.
* source_macros(style_text) returns the eight literal manuscript math macros.
* expanded nodes carry source/line/end_line and source_spans; use
  node.get('source', spec['source']) for source links and retain those fields
  in reports. imported-source node IDs have a stable file-name prefix.
* The references chapter is already at BOOK['bib_page']; skip the separate
  render_bibliography call and additional bibliography nav item when
  bibliography_in_chapters is true.
No manuscript text, computational claim, or formal coverage is extended.
"""
import hashlib
import re
from collections import Counter
from pathlib import PurePosixPath

WORK = 'monographs-cos-method'
BASE = 'monographs/cos-method/book/'
MAIN = BASE + 'K_COS_Monograph.tex'
STYLE = BASE + 'monograph.sty'
FRONT = BASE + 'frontmatter.tex'
BIB = BASE + 'references.tex'
INDEX = 'read/' + WORK + '/index.html'
BIB_PAGE = 'read/' + WORK + '/references.html'

CHAPTER_DATA = [
    ('01_gaussian', 'Gaussian quadratic forms'),
    ('02_streaming', 'Exact streamed representations'),
    ('03_phases', 'Polyphase propagation and scheduling'),
    ('04_range', 'Range cores and low-rank interfaces'),
    ('05_spectrum', 'Spectral uncertainty and exact completion'),
    ('06_packets', 'Exponential tilting and spectral packets'),
    ('07_inversion', 'COS inversion and the analytic error budget'),
    ('08_adaptive', 'Adaptive evaluation and numerical interfaces'),
    ('09_intervals', 'Directed probability enclosures'),
    ('10_accuracy', 'Accuracy-driven certification'),
    ('11_evidence', 'Numerical evidence and applications'),
    ('12_synthesis', 'Composition, scope, and contribution'),
    ('A_atlas', 'Visual studies'),
    ('B_lean', 'Formalization and theorem correspondence'),
    ('C_reproduction', 'Computation and reproducibility'),
    ('D_glossary', 'Glossary and notation'),
]
PART_DATA = [
    (14, 'Gaussian quadratic forms', 'part-1-gaussian-quadratic-forms', 0),
    (16, 'Structured operators and spectral recovery', 'part-2-structured-operators', 1),
    (22, 'The K-COS method', 'part-3-kcos-method', 5),
    (26, 'Certified numerical computation', 'part-4-certified-computation', 8),
]
INPUTS = {
    BASE + 'chapters/06_packets.tex': ['worked_packet_table.tex'],
    BASE + 'chapters/09_intervals.tex': ['worked_enclosure_result.tex'],
    BASE + 'chapters/C_reproduction.tex': ['replay_results.tex'],
}


def _spec(source, title, slug, **other):
    return dict(work=WORK, source=source, title=title,
                url=INDEX.replace('index.html', slug + '.html'), **other)


CHAPTERS = [
    _spec(FRONT, title, slug, start_line=start, end_line=end, kind='frontmatter')
    for start, end, title, slug in [
        (1, 14, 'Preface', 'preface'),
        (15, 34, 'How to read this book', 'how-to-read'),
        (35, 58, 'Notation and conventions', 'notation'),
    ]
]
for _i, (_stem, _title) in enumerate(CHAPTER_DATA):
    for _part, (_line, _part_title, _slug, _before) in enumerate(PART_DATA, 1):
        if _i == _before:
            CHAPTERS.append(_spec(MAIN, _part_title, _slug, start_line=_line,
                                  end_line=_line, kind='part', printed_part=_part))
    CHAPTERS.append(_spec(BASE + 'chapters/' + _stem + '.tex', _title,
                          _stem.replace('_', '-').lower(), kind='chapter',
                          printed_chapter=str(_i + 1) if _i < 12 else 'ABCD'[_i - 12]))
CHAPTERS.append(_spec(BIB, 'Sources and further reading', 'references', kind='bibliography'))

BOOK = dict(
    work=WORK, label='The K-COS Method', base=BASE, main=MAIN, macro_source=STYLE,
    bib=BIB, inline_bibliography=True, bibliography_in_chapters=True,
    index=INDEX, bib_page=BIB_PAGE, chapters=CHAPTERS, main_chapters=12,
    title='Structured Gaussian Quadratic Forms, Spectral Compression, and Certified Extreme-Tail Evaluation',
    custom_reader='kcos', figure_directory='figures_production',
    visual_guide_index=INDEX.replace('index.html', 'a-atlas.html'),
    contents_groups=[
        dict(start=CHAPTERS[0]['url'], title='Introduction'),
        *[dict(start=chapter['url'], title=chapter['title'])
          for chapter in CHAPTERS if chapter['kind'] == 'part'],
        dict(start=INDEX.replace('index.html', 'a-atlas.html'), title='Appendices'),
    ],
    number_floats=True, show_figure_numbers=True, show_table_numbers=True, numbered_bibliography=True,
    statement_navigation=True, required_macros={'E', 'Var', 'R', 'C', 'Pp', 'eps', 'ii', 'phit'},
    reading_introduction='Read the complete monograph, including its preface, four parts, twelve chapters, visual studies, formalization correspondence, reproducibility records, glossary, and references.',
    reading_note='The reading edition preserves the manuscript wording, mathematical expressions, all fifty original figures, and the stated limits of the numerical and formal results.',
)


def _mask(text):
    return ''.join('\n' if c == '\n' else ' ' for c in text)


def _rewrite(text, command, arguments, render):
    """Translate a declared print command without changing its source lines."""
    from readable_chapters import group
    position = 0
    pattern = re.compile(r'\\' + command + r'\b')
    while (match := pattern.search(text, position)):
        end = match.end()
        values = []
        for _ in range(arguments):
            while end < len(text) and text[end].isspace():
                end += 1
            value, end = group(text, end)
            values.append(value)
        replacement = render(*values)
        missing = text[match.start():end].count('\n') - replacement.count('\n')
        if missing < 0:
            raise ValueError('K-COS command translation introduced source lines: ' + command)
        replacement += '\n' * missing
        text = text[:match.start()] + replacement + text[end:]
        position = match.start() + len(replacement)
    return text


def _literal_parts(text):
    return re.split(r'(\\begin\{(?:lstlisting|verbatim)\}(?:\[[^\]\n]*\])?.*?\\end\{(?:lstlisting|verbatim)\})', text, flags=re.S)


def math_environments(text):
    """Present numbered displays using the reader's supported math delimiters.

    The equation body, labels, spacing, and align rows remain literal. The
    printed numbers are bound separately from the authored TeX environments.
    """
    parts = _literal_parts(text)
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].replace(r'\begin{equation}', r'\[').replace(r'\end{equation}', r'\]')
        parts[i] = parts[i].replace(r'\begin{align}', r'\begin{align*}').replace(r'\end{align}', r'\end{align*}')
    return ''.join(parts)


def source_macros(style_text):
    """Read the eight mathematical commands from the retained .sty file."""
    from readable_chapters import group
    result = {}
    for name in ('R', 'C', 'Pp', 'eps', 'ii', 'phit'):
        match = re.search(r'\\newcommand\{\\' + name + r'\}', style_text)
        if not match:
            raise ValueError('Missing K-COS math macro: ' + name)
        value, _ = group(style_text, match.end())
        if '#' in value:
            raise ValueError('Changed K-COS math macro arity: ' + name)
        result[name] = value
    for name in ('E', 'Var'):
        match = re.search(r'\\DeclareMathOperator\{\\' + name + r'\}', style_text)
        if not match:
            raise ValueError('Missing K-COS math operator: ' + name)
        value, _ = group(style_text, match.end())
        result[name] = r'\operatorname{' + value + '}'
    return result


def source_specs(load):
    """Check the complete authored assembly before selecting reading passages."""
    from readable_chapters import group
    main = load(MAIN)
    expected = ['frontmatter'] + ['chapters/' + stem for stem, _ in CHAPTER_DATA] + ['references']
    actual = re.findall(r'\\input\{([^{}]+)\}', main)
    if actual != expected:
        raise ValueError('Review changed K-COS manuscript input order')
    if len(re.findall(r'\\monopart\{', main)) != 4:
        raise ValueError('Review changed K-COS part inventory')
    for line, title, _, _ in PART_DATA:
        content = main.splitlines()[line - 1]
        if not content.startswith(r'\monopart{'):
            raise ValueError('Review changed K-COS part boundary')
        _, pos = group(content, len(r'\monopart'))
        actual_title, _ = group(content, pos)
        if actual_title != title:
            raise ValueError('Review changed K-COS part title')
    front = load(FRONT)
    if len(front.splitlines()) != 58:
        raise ValueError('Review changed K-COS frontmatter ranges')
    for spec in CHAPTERS:
        if spec['kind'] == 'part':
            continue
        text = load(spec['source'])
        if spec['kind'] == 'frontmatter':
            text = text.splitlines()[spec['start_line'] - 1]
        match = re.search(r'\\chapter\*?\{', text)
        title = group(text, match.end() - 1)[0] if match else None
        if title != spec['title']:
            raise ValueError('Review changed K-COS chapter title: ' + spec['source'])
        actual_inputs = re.findall(r'\\input\{([^{}]+)\}', text)
        if actual_inputs != INPUTS.get(spec['source'], []):
            raise ValueError('Review changed K-COS nested inputs: ' + spec['source'])
    return CHAPTERS


def expand_source(raw, spec, source_texts):
    """Expand the three recorded inputs, retaining the origin of every line.

    Returns text and a one-based line map. A source_spans list uses the exact
    shape [{"source": repo_path, "line": first_line, "end_line": last_line}].
    Each span is inclusive and bound to the receipt record for that source.
    """
    from readable_chapters import chapter_text
    selected = chapter_text(raw, spec)
    lines, origins = [], []
    allowed = INPUTS.get(spec['source'], [])
    def get(path):
        value = source_texts(path) if callable(source_texts) else source_texts[path]
        return value.decode('utf-8-sig') if isinstance(value, bytes) else value
    for source_line, line in enumerate(selected.splitlines(keepends=True), 1):
        matches = list(re.finditer(r'\\input\{([^{}]+)\}', line))
        if not matches:
            lines.append(line)
            origins.append((spec['source'], source_line))
            continue
        if len(matches) != 1 or matches[0][1] not in allowed:
            raise ValueError('Unreviewed K-COS input expansion: ' + line.strip())
        match = matches[0]
        included_source = BASE + match[1]
        # Separate print wrappers from the included data. This also gives the
        # table and its captions a source anchor in the included record.
        prefix, suffix = line[:match.start()], line[match.end():]
        lines.append(prefix + '\n')
        origins.append((spec['source'], source_line))
        included = get(included_source)
        if re.search(r'\\input\{', included):
            raise ValueError('Unreviewed recursive K-COS input: ' + included_source)
        for included_line, value in enumerate(included.splitlines(keepends=True), 1):
            lines.append(value if value.endswith('\n') else value + '\n')
            origins.append((included_source, included_line))
        lines.append(suffix if suffix.endswith('\n') else suffix + '\n')
        origins.append((spec['source'], source_line))
    text = ''.join(lines)
    # Chapter.parse may assign the end boundary to the line after the source.
    origins.append(origins[-1] if origins else (spec['source'], 1))
    return text, origins


def source_math(raw, spec, source_texts=None):
    from readable_chapters import original_math
    if source_texts is None:
        source_texts = {}
    expanded, _ = expand_source(raw, spec, source_texts)
    return original_math(math_environments(expanded))


def _prose_layout(text):
    """Remove only font, page, and running-header commands outside math."""
    from readable_chapters import MATH_PATTERN
    patterns = [
        r'\\(?:color|fontfamily|fontseries|fontshape)\{[^{}]*\}',
        r'\\fontsize\{[^{}]*\}\{[^{}]*\}',
        r'\\(?:vspace|hspace)\*?\{[^{}]*\}',
        r'\\markboth\{[^{}]*\}\{[^{}]*\}',
        r'\\renewcommand\{\\arraystretch\}\{[^{}]*\}',
        r'\\(?:displayface|selectfont|footnotesize|smallskip|bigskip|medskip|vfill|backmatter|protect)\b',
    ]
    chunks, position = [], 0
    for match in MATH_PATTERN.finditer(text):
        prose = text[position:match.start()]
        for pattern in patterns:
            prose = re.sub(pattern, lambda m: _mask(m[0]), prose)
        chunks.extend((prose, match[0]))
        position = match.end()
    prose = text[position:]
    for pattern in patterns:
        prose = re.sub(pattern, lambda m: _mask(m[0]), prose)
    chunks.append(prose)
    return ''.join(chunks)


def normalize(text, spec):
    """Translate print structure; exact mathematical sequences are checked."""
    from readable_chapters import clean_tex, group
    # The formal inventory's outer font group encloses a whole table.
    # Its braces are layout boundaries, not reading prose.
    match = re.search(r'\{\\small\s*(?=\\begin\{longtable\})', text)
    if match:
        body, end = group(text, match.start())
        text = text[:match.start()] + ' ' + body + ' ' + text[end:]
    original_lines = text.count('\n')
    text = math_environments(clean_tex(text))
    literal_parts = _literal_parts(text)
    for i in range(0, len(literal_parts), 2):
        part = literal_parts[i]
        # TeX book chapters occupy the reader's section level. Their sections
        # and subsections retain the printed chapter-prefixed numbers.
        names = {'chapter': 'section', 'section': 'subsection', 'subsection': 'subsubsection'}
        part = re.sub(r'\\(chapter|section|subsection)(\*?)(?=\{)',
                      lambda m: '\\' + names[m[1]] + ('*' if spec['kind'] == 'bibliography' and m[1] == 'chapter' else m[2]), part)
        part = _rewrite(part, 'monopart', 3,
                        lambda label, title, prose: r'\part{' + title + r'}\label{' + label + '} ' + prose)
        part = _rewrite(part, 'chapterlead', 1, lambda prose: prose)
        if spec.get('printed_chapter') == 'A':
            part = re.sub(r'\{\\displayface\\fontsize\{27\}\{30\}\\selectfont\\color\{ink\}([^{}]*?)\s+\}',
                          lambda m: r'\subsection*{' + m[1].rstrip() + '}', part)
        part = _rewrite(part, 'atlasheading', 3,
                        lambda number, theme, title: r'\subsection*{Study ' + number + ' / ' + theme + ': ' + title + '}')
        part = _rewrite(part, 'studyresult', 1,
                        lambda prose: r'\begin{readerroadmap}[title={Study result}]' + prose + r'\end{readerroadmap}')
        part = _rewrite(part, 'texorpdfstring', 2, lambda printed, bookmark: printed)
        part = _rewrite(part, 'decl', 1, lambda value: r'\nolinkurl{' + value + '}')
        part = re.sub(r'\\verb([|])([^|{}\n]*)\1', lambda m: r'\texttt{' + m[2] + '}', part)
        part = part.replace(r'\begin{enumerate}[label=\arabic*.]', r'\begin{enumerate}')
        part = part.replace(r'\begin{enumerate}[nosep,topsep=4pt]', r'\begin{enumerate}')
        part = part.replace(r'\begin{scopebox}', r'\begin{readerroadmap}[title={Scope}]').replace(r'\end{scopebox}', r'\end{readerroadmap}')
        part = part.replace(r'\begin{quote}', r'\begin{readerroadmap}[title={Guarantee boundary}]').replace(r'\end{quote}', r'\end{readerroadmap}')
        part = re.sub(r'\\begin\{(figure|table)\}\[[^\]\n]*\]', r'\\begin{\1}', part)
        # Atlas graphics are unnumbered in the manuscript. Their explanatory
        # captions stay as authored prose directly after each original image.
        part = re.sub(r'\\begin\{center\}(\s*\\includegraphics\[width=\\linewidth\]\{[^{}]+\}\s*)\\end\{center\}',
                      lambda m: r'\begin{figure}\centering' + m[1] + r'\caption{}\end{figure}', part)
        # Print-only bibliography heading replacement. Its seven entries stay
        # in the thebibliography node, on the one references reading page.
        part = part.replace(r'\patchcmd{\thebibliography}{\chapter*{\bibname}}{\section*{\bibname}}{}{}', '')
        part = part.replace(r'\patchcmd{\thebibliography}{\section*{\bibname}}{\subsection*{\bibname}}{}{}', '')
        part = _prose_layout(part)
        literal_parts[i] = part
    text = ''.join(literal_parts)
    if text.count('\n') != original_lines:
        raise ValueError('K-COS layout conversion moved source line boundaries')
    return text


def _spans(origins, start, end):
    spans = []
    for source, line in origins[start - 1:min(end, len(origins))]:
        if spans and spans[-1]['source'] == source and line in (spans[-1]['end_line'], spans[-1]['end_line'] + 1):
            spans[-1]['end_line'] = line
        else:
            spans.append(dict(source=source, line=line, end_line=line))
    return spans


def bind_source_lines(chapter, spec, origins):
    """Bind stable reading anchors to each source, after input expansion."""
    counts = Counter()
    for node in chapter.nodes:
        spans = _spans(origins, node['line'], node['end_line'])
        first = spans[0]
        node.update(source=first['source'], line=first['line'], end_line=first['end_line'], source_spans=spans)
        prefix = '' if first['source'] == spec['source'] else PurePosixPath(first['source']).stem.replace('_', '-') + '-'
        key = prefix + 'L' + str(first['line'])
        counts[key] += 1
        node['id'] = key + ('-' + str(counts[key]) if counts[key] > 1 else '')


def equation_numbers(text, printed_chapter):
    """Read book-class equation counters from numbered TeX displays."""
    numbers, counter = {}, 0
    pattern = re.compile(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', re.S)
    for match in pattern.finditer(text):
        rows = re.split(r'\\\\(?:\[[^\]]*\])?', match[2]) if match[1] == 'align' else [match[2]]
        for row in rows:
            if not row.strip() or r'\notag' in row or r'\nonumber' in row:
                continue
            counter += 1
            for label in re.findall(r'\\label\{([^{}]+)\}', row):
                numbers[label] = str(printed_chapter) + '.' + str(counter)
    return numbers


def prepare_book(reader, config):
    from readable_chapters import Chapter, manuscript_bibliography, original_math, NUMBERED
    source_texts, source_bytes = {}, {}
    def load(path):
        if path not in source_texts:
            record = reader.add(path)
            if not record:
                raise ValueError('Missing receipt-bound K-COS source: ' + path)
            source_bytes[path] = reader.site.read_source(record)
            source_texts[path] = source_bytes[path].decode('utf-8-sig')
        return source_texts[path]
    source_specs(load)
    main, style = load(MAIN), load(STYLE)
    macros = source_macros(style)
    references = manuscript_bibliography(load(BIB))
    if len(references) != 7:
        raise ValueError('Review changed K-COS reference inventory')
    for names in INPUTS.values():
        for name in names:
            load(BASE + name)
    labels, chapters, equations = {}, [], {}
    for spec in CHAPTERS:
        raw = load(spec['source'])
        expanded, origins = expand_source(raw, spec, source_texts)
        formatted = normalize(expanded, spec)
        if source_math(raw, spec, source_texts) != original_math(formatted):
            raise ValueError('K-COS layout conversion changed mathematics in ' + spec['source'])
        printed = spec.get('printed_chapter')
        state = dict(number_floats=True)
        if printed:
            state.update(section=int(printed) - 1 if printed.isdigit() else ord(printed) - ord('A'), appendix=not printed.isdigit())
        if spec['kind'] == 'part':
            state['part'] = spec['printed_part'] - 1
        chapter = Chapter(formatted, macros, state=state, check_refs=False)
        chapter.url, chapter.base, chapter.source = spec['url'], BASE, spec['source']
        chapter.allow_prose_groups = True
        chapter.bibliography_url, chapter.macro_source = BIB_PAGE, STYLE
        chapter.table_config = config
        chapter.table_aids_used, chapter.nested_tables = set(), []
        chapter.proof_pairs = {}
        chapter.original_text = expanded
        bind_source_lines(chapter, spec, origins)
        figure, table = 0, 0
        study_title = spec['title']
        for i, node in enumerate(chapter.nodes):
            if printed == 'A' and node['kind'] == 'subsection':
                study_title = node['title']
            if node['kind'] == 'figure':
                if printed == 'A':
                    node['alt'] = study_title
                figure += 1
                node['number'] = '' if printed == 'A' else str(printed) + '.' + str(figure)
            elif node['kind'] in {'table', 'longtable'}:
                # The source uses tabular/longtable without captions; only
                # captioned floats advance LaTeX's table counter.
                if r'\caption' in node['body']:
                    table += 1
                    node['number'] = str(printed) + '.' + str(table)
                else:
                    node['number'] = ''
            elif node['kind'] in {'tabular', 'tabularx'}:
                node['number'] = ''
            if node['kind'] == 'proof':
                previous = next((item for item in reversed(chapter.nodes[:i]) if item['kind'] != 'text'), None)
                if previous and previous['kind'] in NUMBERED:
                    chapter.proof_pairs[previous['id']] = node['id']
        local_equations = equation_numbers(expanded, printed) if printed else {}
        for key, number in local_equations.items():
            if key in equations:
                raise ValueError('Repeated K-COS equation label: ' + key)
            equations[key] = number
        for key, node in chapter.labels.items():
            if key in labels:
                raise ValueError('Repeated K-COS source label: ' + key)
            node['url'] = chapter.url
            reference = node['number'] or node['title']
            if not reference and key in {'sec:gaussian-core', 'sec:packets', 'sec:final-5'}:
                # These authored labels follow a chapter lead before its first
                # section; LaTeX's current reference value is the chapter.
                reference = printed
            if not reference and key not in equations:
                raise ValueError('Review unnumbered K-COS reference target: ' + key)
            if key in equations:
                reference = equations[key]
            labels[key] = dict(node, reference_label=reference, plain_reference_label=reference)
            if key in equations:
                labels[key]['equation_number'] = equations[key]
        chapters.append((spec, source_bytes[spec['source']], chapter))
    counts = Counter(node['kind'] for _, _, chapter in chapters for node in chapter.nodes)
    expected = {'theorem': 35, 'corollary': 12, 'proposition': 6, 'lemma': 2, 'remark': 5, 'algorithm': 1, 'proof': 39, 'figure': 50}
    if any(counts[k] != count for k, count in expected.items()):
        raise ValueError('Review changed K-COS statement/proof/figure inventory: ' + repr(dict(counts)))
    for spec, _, chapter in chapters:
        chapter.labels = labels
        chapter.validate_references()
        chapter.equation_numbers = equations
        chapter.citations = {ref['key']: (str(i), chapter.relative(BIB_PAGE) + '#ref-' + ref['key']) for i, ref in enumerate(references, 1)}
    included_sources = []
    for source, names in INPUTS.items():
        for name in names:
            included = BASE + name
            line = next(i for i, text in enumerate(load(source).splitlines(), 1) if r'\input{' + name + '}' in text)
            included_sources.append(dict(source=included, source_sha256=hashlib.sha256(source_bytes[included]).hexdigest(), input_source=source, input_line=line))
    return dict(config=config, chapters=chapters, references=references, macros=macros,
                main=main, source_texts=source_texts, included_sources=included_sources)
