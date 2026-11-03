"""Source-bound HTML edition of the Machine-Native Reasoning reviewed core.

Only printer-oriented TeX wrappers are adapted. Mathematical expressions,
source lines, authored titles, labels and printed statement numbers remain
bound to the retained manuscript. This conversion adds no proof review or
Lean execution, and does not enlarge the selected reviewed core's scope.
"""
import hashlib
import html
import re

WORK = 'monographs-machine-native-reasoning'
COMPONENT = 'monographs/machine-native-reasoning/'
BASE = COMPONENT + 'reader/source/'
MAIN = BASE + 'book.tex'
MAP = COMPONENT + 'THEOREM_MAP.json'
INDEX = 'read/' + WORK + '/index.html'
SCOPE_PAGE = 'read/' + WORK + '/formal-scope.html'
SOURCE_SHA256 = 'c2ef44767a242021cc573bbba7bb0c95df74a704c99cf992d2eff0a396838593'

# One contiguous retained source range per authored chapter. The printed cover
# is available in the unchanged PDF; the reading body begins with its preface.
MARKERS = [
    (64, 'The shape of the argument', 'shape-of-the-argument', None),
    (87, 'What the review label means', 'review-label', None),
    (100, 'From evidence to a reusable state', 'evidence-and-reusable-state', 1),
    (176, 'Operations must survive their representations', 'operations-and-representations', 2),
    (307, 'Memory that remains open to correction', 'memory-and-correction', 3),
    (523, 'From corrected records to decisions and explanations', 'decisions-and-explanations', 4),
    (591, 'One investigation, one resource budget', 'inquiry-and-resources', 5),
    (738, 'Improving discovery without changing its meaning', 'discovery-and-meaning', 6),
    (803, 'What remains valid after a revision', 'revision-and-validity', 7),
    (869, 'Shared work and maintained obligations', 'shared-work-and-obligations', 8),
    (939, 'One continuous chain, with no hidden promotion', 'continuous-chain', 9),
    (979, 'Result and source map', 'result-and-source-map', None),
    (1014, 'Reading sources and review boundaries', 'reading-sources-and-boundaries', None),
]
CHAPTERS = [dict(work=WORK, source=MAIN, url=INDEX.replace('index.html', slug + '.html'),
    title=('Chapter '+str(number)+'. '+title if number else title), start_line=start,
    end_line=MARKERS[i+1][0]-1 if i+1<len(MARKERS) else 1045,
    chapter_number=number, kind='chapter', figure_roots=[''])
    for i,(start,title,slug,number) in enumerate(MARKERS)]
BOOK = dict(work=WORK, label='Machine-Native Reasoning', base=BASE, main=MAIN,
    bib=MAIN, index=INDEX, bib_page='read/' + WORK + '/references.html',
    title='Evidence, methods, and accountable revision',
    chapters=CHAPTERS, main_chapters=9, custom_reader='machine_native_reasoning',
    required_macros={'TV', 'im', 'Span', 'Pow'}, statement_navigation=True,
    lean_reader_paths=('MachineTheory.lean', 'MachineTheory/'),
    lean_reader_note='This inspector contains the current MachineTheory root import and its '
        '78 mathematical modules. Historical sources and recorded checks keep their '
        'own provenance in the retained package.',
    lean_runtime_note='The accepted project pins Lean 4.34.0-rc2. The browser checker '
        'uses Lean 4.33.0 as a separate experiment, with some required imports unavailable. '
        'Reproduce the recorded environment '
        'with the retained compiler and dependency instructions.',
    lean_runtime_guide=COMPONENT+'release/RUNTIME_REPRODUCTION.md',
    reading_guide='read/' + WORK + '/start.html',
    reading_guide_description='Follow the sensor example, study the selected results, or inspect their recorded formal scope.',
    figure_receipts='assets/figures/machine-native-reasoning/figures.json',
    figure_source_root=BASE,
    footer_index_only=True,
    bibliography_introduction='These source descriptions are retained from the reader’s '
        '“Reading sources and review boundaries” chapter. Their selection does not '
        'admit every result in the source works.',
    reading_introduction='Read the Reviewed Mathematical Core: nine chapters connecting '
        'accessible evidence, reusable states, correction, inquiry, and revision. '
        'The two opening sections and both source and review registers are included.',
    reading_note='This HTML edition preserves the reviewed-core manuscript, its 27 '
        'selected mathematical results, 27 written proofs, 12 counterexamples, six '
        'figures, and source-line links. The formal correspondence describes only '
        'those selected results. The wider research continuation has its own scope. '
        'This conversion adds no proof review, Lean execution, or empirical validation.')
BOOK['contents_groups'] = [dict(start=CHAPTERS[0]['url'],title='Orientation'),
    dict(start=CHAPTERS[2]['url'],title='Reviewed mathematical core'),
    dict(start=CHAPTERS[11]['url'],title='Sources and review boundaries')]


def source_specs(load):
    """Reject changed source identity or chapter boundaries before conversion."""
    main = load(MAIN)
    if hashlib.sha256(main.encode('utf-8')).hexdigest() != SOURCE_SHA256:
        raise ValueError('Review changed Machine-Native Reasoning manuscript source')
    lines = main.splitlines()
    if len(lines) != 1045 or lines[-1] != r'\end{document}':
        raise ValueError('Machine-Native Reasoning document boundaries changed')
    expected = [(start,title) for start,title,_,_ in MARKERS]
    actual = [(i+1,m[1]) for i,line in enumerate(lines)
              if (m := re.match(r'\\chapter\*?\{([^{}]+)\}',line))]
    if actual != expected:
        raise ValueError('Machine-Native Reasoning chapter order changed')
    if CHAPTERS[0]['start_line'] != 64 or CHAPTERS[-1]['end_line'] != len(lines):
        raise ValueError('Machine-Native Reasoning reading span changed')
    for prior,current in zip(CHAPTERS,CHAPTERS[1:]):
        if prior['end_line']+1 != current['start_line']:
            raise ValueError('Machine-Native Reasoning reading ranges overlap or omit lines')
    return CHAPTERS


def source_math(main, spec):
    from readable_chapters import chapter_text, original_math
    return original_math(chapter_text(main,spec))


def _mask(text):
    return ''.join('\n' if c == '\n' else ' ' for c in text)


def _rewrite(text, name, change):
    """Replace one prose macro, retaining exactly its authored line count."""
    from readable_chapters import group
    pattern = re.compile(r'\\' + re.escape(name) + r'\b')
    position = 0
    while match := pattern.search(text,position):
        start = match.end()
        while start < len(text) and text[start].isspace():
            start += 1
        value,end = group(text,start)
        old = text[match.start():end]
        new = change(value)
        missing = old.count('\n') - new.count('\n')
        if missing < 0:
            raise ValueError('Machine-Native Reasoning normalization shifts source lines')
        new += '\n' * missing
        text = text[:match.start()] + new + text[end:]
        position = match.start() + len(new)
    return text


def normalize(source):
    """Translate book headings and the three authored prose-only macros."""
    from readable_chapters import clean_tex
    text = clean_tex(source)
    count = source.count('\n')
    # Do all heading levels in a single pass so a transformed chapter is not
    # transformed a second time. The two backmatter chapters are unnumbered in
    # the printed book even though their TeX commands lack an asterisk.
    def heading(match):
        kind,star,title = match.groups()
        if kind == 'chapter' and title in {'Result and source map', 'Reading sources and review boundaries'}:
            star = '*'
        return '\\' + {'chapter':'section','section':'subsection','subsection':'subsubsection'}[kind] + star + '{' + title + '}'
    text = re.sub(r'\\(chapter|section|subsection)(\*?)\{([^{}]+)\}',heading,text)
    for name,label in [('source','Source relationship.'),('boundary','Boundary.')]:
        text = _rewrite(text,name,lambda body,label=label:r'\textit{' + label + '} ' + body)
    text = _rewrite(text,'question',lambda body:r'\paragraph*{' + body + '}')
    text = re.sub(r'\\(?:frontmatter|mainmatter|backmatter|footnotesize)\b',lambda m:_mask(m[0]),text)
    text = re.sub(r'\\(?:begin|end)\{samepage\}',lambda m:_mask(m[0]),text)
    text = text.replace(r'\begin{description}[style=nextline]',r'\begin{description}')
    text = re.sub(r'\\begin\{figure\}\[ht\]',r'\\begin{figure}',text)
    if text.count('\n') != count:
        raise ValueError('Machine-Native Reasoning normalization shifts source lines')
    return text


def references(main):
    """Read the ten authored source descriptions, preserving their source lines."""
    match = re.search(r'\\begin\{description\}\[style=nextline\](.*?)\\end\{description\}',main,re.S)
    if not match:
        raise ValueError('Missing Machine-Native Reasoning source descriptions')
    items = list(re.finditer(r'\\item\[([^\]]+)\]',match[1]))
    if len(items) != 10 or match[1][:items[0].start()].strip():
        raise ValueError('Review Machine-Native Reasoning source descriptions')
    return [dict(key=item[1],line=main.count('\n',0,match.start(1)+item.start())+1,
        body=match[1][item.end():items[i+1].start() if i+1<len(items) else len(match[1])].strip())
        for i,item in enumerate(items)]


def prepare_book(reader,config):
    import readable_chapters as reading
    import json
    def load(path):
        record = reader.add(path)
        if not record:
            raise ValueError('Missing receipt-bound Machine-Native Reasoning source: '+path)
        return reader.site.read_source(record).decode('utf-8-sig')
    source_specs(load)
    main = load(MAIN)
    if not reader.add(config['lean_runtime_guide'],'Portable runtime reproduction'):
        raise ValueError('Missing Machine-Native Reasoning runtime reproduction guide')
    mapping = json.loads(load(MAP))
    if len(mapping) != 27 or len({r['label'] for r in mapping}) != 27:
        raise ValueError('Review Machine-Native Reasoning selected-result map')
    recorded = {r['label']:r for r in mapping}
    macros = reading.manuscript_macros(main,config['required_macros'])
    raw = reader.site.read_source(reader.records[MAIN])
    chapters,labels,seen = [],{},set()
    state = {}
    for spec in config['chapters']:
        selected = reading.chapter_text(main,spec)
        formatted = normalize(selected)
        if reading.original_math(formatted) != source_math(main,spec):
            raise ValueError('Machine-Native Reasoning mathematical source changed during normalization')
        chapter = reading.Chapter(formatted,macros,state=state,check_refs=False)
        chapter.url,chapter.base,chapter.source = spec['url'],BASE,MAIN
        chapter.bibliography_url = config['bib_page']
        chapter.external_inputs = {'formal_correspondence.tex': dict(
            url=SCOPE_PAGE+'#formal-correspondence', title='Read the formal correspondence chapter', note='')}
        chapter.proof_pairs = {}
        pending = None
        for node in chapter.nodes:
            if node['kind'] in {'theorem','proposition','corollary'}:
                if pending is not None:
                    raise ValueError('Unpaired Machine-Native Reasoning selected result')
                if len(node['labels']) != 1 or node['labels'][0] not in recorded:
                    raise ValueError('Unmapped Machine-Native Reasoning selected result')
                label = node['labels'][0]
                row = recorded[label]
                if any(node[field] != row[field] for field in ('kind','number','title')):
                    raise ValueError('Machine-Native Reasoning printed statement differs: '+label)
                if label in seen:
                    raise ValueError('Repeated Machine-Native Reasoning selected result')
                seen.add(label)
                pending = node
                chapter.related_readings[node['id']] = [('Recorded Lean scope',SCOPE_PAGE+'#'+label.replace(':','-'))]
            elif node['kind'] == 'proof':
                if pending is None:
                    raise ValueError('Unpaired Machine-Native Reasoning written proof')
                chapter.proof_pairs[pending['id']] = node['id']
                pending = None
        if pending is not None:
            raise ValueError('Missing Machine-Native Reasoning written proof')
        for label,node in chapter.labels.items():
            if label in labels:
                raise ValueError('Repeated Machine-Native Reasoning source label: '+label)
            # The manuscript writes “Theorem~\\ref{...}”; the reference itself
            # must supply just the printed number, as TeX does.
            labels[label] = dict(node,url=spec['url'],reference_label=node['number'] or node['title'])
        state = {key:getattr(chapter,key) for key in ('section','appendix','part','subsection',
                 'subsubsection','counter','section_prefix','figure','table','number_floats')}
        chapters.append((spec,raw,chapter))
    if seen != set(recorded):
        raise ValueError('Incomplete Machine-Native Reasoning selected-result conversion')
    for _,_,chapter in chapters:
        chapter.labels = labels
        chapter.validate_references()
    from reader_figure_assets import prepare
    book = dict(config=config,chapters=chapters,references=references(main),macros=macros,
                main=main,figure_assets=prepare(reader,config,chapters))
    # The source-bound scope adapter registers its supporting records here;
    # publication happens only after all source pages have been prepared.
    from machine_native_reasoning_scope import prepare_scope
    prepare_scope(reader,book)
    return book


def publish_start(reader,book):
    """Offer a concrete first path through the retained core and its evidence."""
    site = reader.site
    page = BOOK['reading_guide']
    def link(label,target):
        return '<a href="'+html.escape(site.rel(target,page),quote=True)+'">'+html.escape(label)+'</a>'
    body = '<p class="eyebrow">Machine-Native Reasoning · Reviewed Mathematical Core</p>'
    body += '<h1>From an observation to accountable revision</h1>'
    body += '<p>A sensor displays one bit under an unknown convention. Follow that small example through what a record determines, what a representation preserves, what correction requires, and which decisions and revisions the retained evidence supports.</p>'
    body += '<p>'+link('Read the reviewed core',INDEX)+' · '+link('Find a statement or written proof','read/'+WORK+'/statements.html')+'</p>'
    body += '<h2>A first reading path</h2><ol>'
    for index,label in [(2,'Begin with accessible evidence and a reusable state'),
                        (4,'See what memory must keep for later correction'),
                        (6,'Put one inquiry under an explicit resource budget'),
                        (8,'Track which results remain applicable after a revision')]:
        body += '<li>'+link(label,CHAPTERS[index]['url'])+'</li>'
    body += '</ol><h2>Know the scope of the edition</h2>'
    body += '<p>The retained reader develops 27 selected results with complete written proofs across nine chapters. Its 12 counterexamples keep the boundaries visible. The current MachineTheory companion contains a root import and 78 mathematical modules; the statement map identifies the modules and declarations attached to each selected result.</p>'
    body += '<p>'+link('Read what the review label means',CHAPTERS[1]['url'])+' · '+link('Inspect the recorded formal scope',SCOPE_PAGE)+' · '+link('Browse all current Lean files','lean/'+WORK+'/index.html')+'</p>'
    body += '<p>'+html.escape(BOOK['lean_runtime_note'])+' '+link('Read the portable reproduction instructions',reader.records[BOOK['lean_runtime_guide']]['url'])+'</p>'
    body += '<h2>Continue through the whole argument</h2><p>Read the chapters in order to connect representation, correction, decision, inquiry, discovery, revision, and shared obligations. The final source chapters retain the author’s source relationships and limits.</p>'
    body += '<p>'+link('Open the complete core contents',INDEX)+' · '+link('Read the result and source map',CHAPTERS[11]['url'])+'</p>'
    body += '<h2>Original publication and wider continuation</h2>'
    body += '<p>The original PDF retains the printed publication. The wider research continuation is a separate edition with its own evidence and review boundaries; the selected-core correspondence does not certify the wider manuscript.</p>'
    body += '<p>'+link('Open the reviewed-core publication and companion records','collection/works/'+WORK+'.html#read')+' · '+link('Open the wider continuation','collection/works/research-machine-native-reasoning-wider.html')+'</p>'
    body += '<p>This reading conversion reports retained evidence. It adds no proof review, Lean execution, or empirical validation.</p>'
    site.page(page,'Start reading Machine-Native Reasoning',body)
    site.search.append(dict(title='Machine-Native Reasoning / Start here',group='Collection',kind='Guides',
        work_ids=[WORK],url=page,text='Machine Native Reasoning reviewed mathematical core sensor evidence '
        'reusable state correction memory decisions inquiry discovery accountable revision formal scope Lean'))
    from machine_native_reasoning_scope import publish_scope
    publish_scope(reader,book)
