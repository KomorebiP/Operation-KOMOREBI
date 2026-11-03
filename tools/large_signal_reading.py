"""Source-bound reading edition of the corrected Large Signal Model body.

The retained editable source is Markdown with literal TeX mathematics. Only
its reviewed presentation syntax is translated into the existing reader.
The original publication includes additional registers and a glossary in PDF.
"""
import hashlib
import html
import json
from pathlib import Path
import re

WORK = 'monographs-large-signal-model'
BASE = 'monographs/large-signal-model/Monograph/source/'
MAIN = BASE + 'FOUNDATIONS.md'
COVERAGE = 'monographs/large-signal-model/Lean/COVERAGE.md'
SCOPE_PAGE = 'read/' + WORK + '/formal-scope.html'
RESOURCES = [
    (COVERAGE,'Read the proposition coverage map'),
    ('monographs/large-signal-model/Lean/LEAN_GUIDE.md','Read the Lean companion guide'),
    ('monographs/large-signal-model/Lean/CURRENT_STATUS.json','Inspect the accepted verification summary'),
    ('monographs/large-signal-model/Reference_Laboratory/REPLAY_README.md','Reference laboratory replay instructions')]
DATA = json.loads(Path(__file__).with_name('large_signal_sections.json').read_text(encoding='utf-8'))
CHAPTERS = DATA['chapters']
BOOK = dict(work=WORK, label='Large Signal Model', base=BASE, main=MAIN,
    bib=MAIN, index='read/' + WORK + '/index.html',
    bib_page='read/' + WORK + '/references.html', chapters=CHAPTERS,
    title='Realization, refinement, and predictive closure', main_chapters=100,
    custom_reader='large_signal', required_macros=[], statement_navigation=True,
    lean_reader_paths=('Lean/KomorebiLSM.lean', 'Lean/KomorebiLSM/'),
    lean_reader_note='This inspector shows the 254 mathematical modules and their root import file. '
        'The full retained project, including rejection controls and test sources, remains available '
        'in the source downloads and through the work overview.',
    reading_guide='read/' + WORK + '/start.html',
    reading_guide_description='A first pass through the mathematics, the recorded Lean scope, or the software.',
    figure_receipts='assets/figures/large-signal-model/figures.json',
    figure_source_root='monographs/large-signal-model/Monograph/',
    reading_introduction='Read the corrected mathematical body: 100 sections in '
        'eight parts, with all 87 numbered propositions and their written proofs. '
        'Follow exact realization through predictive closure, learning, and '
        'certified probability domains.',
    reading_note='This edition preserves the corrected editable mathematical body, '
        'its two figures, references, and source-line links. The full 174-page '
        'publication retains its additional glossary and formal registers in PDF. '
        'The theoretical atlas is available as a separate PDF. Recorded Lean '
        'mappings retain their stated assumptions; this conversion adds no proof '
        'audit, Lean execution, or empirical validation.')
BOOK['contents_groups'] = [dict(start=CHAPTERS[0]['url'],title='Orientation'),
    dict(start=CHAPTERS[1]['url'],title='Part I. Realization and predictive closure'),
    *[dict(start=c['url'],title=c['title']) for c in CHAPTERS if c['kind']=='part']]
BOOK['footer_index_only'] = True

# Longest delimiter first. Math contents are never passed to prose rewriting.
MATH = re.compile(r'\$\$(.*?)\$\$|(?<!\\)\$([^$\n]*?)(?<!\\)\$', re.S)


def source_math(source, spec):
    from readable_chapters import chapter_text
    return [next(v for v in match.groups() if v is not None)
            for match in MATH.finditer(chapter_text(source, spec))]


def inline_prose(text, citations=True):
    """Translate only the literal Markdown inline syntax used in this body."""
    # Protect literal filenames and URLs from emphasis and prose-reference rules.
    literals = []
    def literal(match):
        value = match[1]
        literals.append((r'\url{' if value.startswith('https://') else r'\texttt{') + value + '}')
        return '\x00' + str(len(literals)-1) + '\x00'
    text = re.sub(r'`([^`\n]+)`', literal, text)
    text = re.sub(r'\*\*([^*\n]+)\*\*', lambda m: r'\textbf{' + m[1] + '}', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', lambda m: r'\emph{' + m[1] + '}', text)
    if citations:
        text = re.sub(r'(?<!\{)\[([KR]\d+[a-z]?)\]', lambda m: r'\cite{' + m[1] + '}', text)
    text = re.sub(r'\x00(\d+)\x00', lambda m: literals[int(m[1])], text)
    return text


def normalize(source):
    """Keep every source line and mathematical token while adapting wrappers."""
    pieces, end = [], 0
    for match in MATH.finditer(source):
        pieces.append(inline_prose(source[end:match.start()]))
        pieces.append((r'\[' + match[1] + r'\]') if match[1] is not None else match[0])
        end = match.end()
    pieces.append(inline_prose(source[end:]))
    text = ''.join(pieces)
    text = re.sub(r'^(#{1,3}) (.+)$',
        lambda m: '\\' + {1:'section', 2:'subsection', 3:'subsubsection'}[len(m[1])] + '*{' + m[2] + '}', text, flags=re.M)
    text = re.sub(r'^\\textbf\{Proposition (\d+)\. (.+?)\.\}',
        lambda m: r'\begin{proposition}[' + m[2] + r']\label{lsm-prop-' + m[1] + '}', text, flags=re.M)
    text = text.replace(r'\textbf{Proof.}', r'\end{proposition}\begin{proof}')
    text = text.replace(r'$\square$', r'$\square$\end{proof}')
    # The two finite numbered lists are semantic ordered lists, not prose numbers.
    text = re.sub(r'(?m)(^1\. [^\n]+\n(?:[2-9]\. [^\n]+\n?)+)',
        lambda m: r'\begin{enumerate}' + re.sub(r'(?m)^\d+\. ', r'\\item ', m[0]).rstrip('\n') + r'\end{enumerate}' + ('\n' if m[0].endswith('\n') else ''), text)
    # Original reference headings remain in the complete source-lineage chapter.
    text = re.sub(r'^\\textbf\{\[([KR]\d+[a-z]?)\]\}',
        lambda m: r'\paragraph*{[' + m[1] + ']}', text, flags=re.M)
    text = re.sub(r'\\newpage\b', lambda m: ' ' * len(m[0]), text)
    if text.count('\n') != source.count('\n'):
        raise ValueError('Large Signal Model translation moved source lines')
    return text


def source_specs(load):
    raw = load(MAIN)
    if hashlib.sha256(raw.encode()).hexdigest() != DATA['source_sha256']:
        raise ValueError('Review changed Large Signal Model source')
    lines = raw.splitlines()
    actual = [(i+1, line[2:]) for i, line in enumerate(lines) if line.startswith('# ')]
    if actual != [(c['start_line'], c['title']) for c in CHAPTERS]:
        raise ValueError('Review Large Signal Model chapter order')
    if CHAPTERS[0]['start_line'] != 1 or CHAPTERS[-1]['end_line'] != len(lines):
        raise ValueError('Incomplete Large Signal Model body')
    if any(a['end_line']+1 != b['start_line'] for a,b in zip(CHAPTERS, CHAPTERS[1:])):
        raise ValueError('Large Signal Model source ranges overlap or omit lines')
    numbers = re.findall(r'^\*\*Proposition (\d+)\.', raw, re.M)
    if numbers != list(map(str, range(1,88))) or raw.count('**Proof.**') != 87 or raw.count(r'$\square$') != 87:
        raise ValueError('Review Large Signal Model proposition and proof inventory')
    return CHAPTERS


def prepare_book(reader, config):
    import readable_chapters as reading
    def load(path):
        record = reader.add(path)
        if not record:
            raise ValueError('Missing receipt-bound Large Signal Model source: ' + path)
        return reader.site.read_source(record).decode('utf-8-sig')
    source_specs(load)
    main = load(MAIN)
    for path,title in RESOURCES:
        if not reader.add(path,title):
            raise ValueError('Missing Large Signal Model reading resource: '+path)
    coverage = load(COVERAGE)
    scopes = {int(m[1]): dict(line=i,title=m[2],scope=m[3])
              for i,line in enumerate(coverage.splitlines(),1)
              if (m := re.fullmatch(r'\| P(\d+): (.*?) \| complete \| (.*?) \|', line))}
    if set(scopes) != set(range(1,88)):
        raise ValueError('Review recorded Large Signal Model coverage rows')
    references = [dict(key=m[1], line=main.count('\n',0,m.start())+1,
                       body=inline_prose(m[2], citations=False))
                  for m in re.finditer(r'^\*\*\[([KR]\d+[a-z]?)\]\*\* (.+)$', main, re.M)]
    if len(references) != 28 or len({r['key'] for r in references}) != 28:
        raise ValueError('Review Large Signal Model bibliography')
    raw = reader.site.read_source(reader.records[MAIN])
    chapters, labels, count = [], {}, 0
    for spec in config['chapters']:
        text = reading.chapter_text(main, spec)
        chapter = reading.Chapter(normalize(text), {}, check_refs=False)
        chapter.url, chapter.base, chapter.source = spec['url'], BASE, MAIN
        chapter.bibliography_url = config['bib_page']
        chapter.proof_pairs = {}
        pending = None
        for node in chapter.nodes:
            if node['kind'] == 'proposition':
                count += 1
                node['number'] = str(count)
                node['url'] = spec['url']
                scope = scopes[count]
                if node['title'] != scope['title']:
                    raise ValueError('Large Signal Model recorded title differs at P' + str(count))
                chapter.related_readings[node['id']] = [('Recorded Lean scope',
                    SCOPE_PAGE + '#p' + str(count))]
                scope['statement_url'] = spec['url']+'#'+node['id']
                pending = node
            elif node['kind'] == 'proof':
                if pending is None:
                    raise ValueError('Unpaired Large Signal Model proof')
                chapter.proof_pairs[pending['id']] = node['id']
                scopes[int(pending['number'])]['proof_url'] = spec['url']+'#'+node['id']
                pending = None
        if pending is not None:
            raise ValueError('Missing Large Signal Model proof')
        for key, node in chapter.labels.items():
            if key in labels:
                raise ValueError('Repeated Large Signal Model label')
            labels[key] = dict(node, url=spec['url'])
        chapter.citations = {r['key']:(r['key'], chapter.relative(config['bib_page'])+'#ref-'+r['key']) for r in references}
        chapters.append((spec, raw, chapter))
    if count != 87:
        raise ValueError('Incomplete Large Signal Model proposition conversion')
    for _,_,chapter in chapters:
        chapter.labels = labels
        chapter.validate_references()
    from reader_figure_assets import prepare
    return dict(config=config, chapters=chapters, references=references, macros={},scopes=scopes,
        main=main, figure_assets=prepare(reader,config,chapters))


def publish_start(reader, book):
    """Connect the mathematical edition, recorded evidence and separate runtime."""
    site = reader.site
    page = BOOK['reading_guide']
    def link(title, target):
        return '<a href="'+html.escape(site.rel(target,page),quote=True)+'">'+html.escape(title)+'</a>'
    by_number = {int(m[1]):c for c in CHAPTERS if (m:=re.match(r'(\d+)\.',c['title']))}
    body = '<p class="eyebrow">Large Signal Model</p><h1>From an observation to a predictive state</h1>'
    body += '<p>An exact archive preserves an observation. A useful predictive state must also retain what the declared future questions need. Start with that distinction, then follow the construction and its evidence.</p>'
    body += '<p>'+link('Read the mathematical body',BOOK['index'])+' · '+link('Find a proposition or proof','read/'+WORK+'/statements.html')+'</p>'
    body += '<h2>A first reading path</h2><ol>'
    for n,label in [(1,'Distinguish observations, archives, and predictive states'),
                    (5,'See when a summary supports a reduced transition'),
                    (13,'Follow the complete small signal example'),
                    (18,'Identify a recurrence from observed outputs')]:
        body += '<li>'+link(label,by_number[n]['url'])+'</li>'
    body += '</ol><h2>Study the full construction</h2><p>Continue through learning and stability, controlled stochastic realization, certified probability domains, continuous observations, and robustness under data uncertainty. The contents group the 100 sections into eight parts.</p>'
    body += '<p>'+link('Open all chapters',BOOK['index'])+' · '+link('Try the Signal laboratory','signal-lab.html')+'</p>'
    body += '<h2>Inspect the recorded formal scope</h2><p>The retained coverage map records complete mappings for 87 registered proposition cores under explicit assumptions. Each HTML proposition links to its written proof and its recorded scope. The publication conversion adds no compiler run or mathematical review.</p>'
    body += '<p>'+link('Read the scope of each proposition',SCOPE_PAGE)+'</p><ul>'
    body += '<li>'+link('Inspect the mathematical Lean sources','lean/'+WORK+'/index.html')+'</li>'
    for path,title in RESOURCES[:3]:
        record=reader.records[path]
        body += '<li>'+link(title,record['url'])+'</li>'
    body += '<li><a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/monographs/large-signal-model/Lean/verification/current/report.json">Full accepted execution record on GitHub</a></li>'
    body += '</ul><h2>Explore the software and reference examples</h2><p>The PR-LASM software package has its own implementation and assessment record. Use its documentation for setup and runtime details; the mathematical coverage count does not establish empirical model performance.</p>'
    body += '<p>'+link('Open the PR-LASM software work page','collection/works/large-signal-model.html')+'</p>'
    record=reader.records[RESOURCES[-1][0]]
    body += '<p>'+link('Run the retained reference examples',record['url'])+'</p>'
    body += '<h2>Original publication and atlas</h2><p>The 174-page PDF retains the full publication layout, additional glossary, and formal registers. Its theoretical atlas remains a separate PDF.</p><p>'+link('Open publication and companion links','collection/works/'+WORK+'.html#read')+'</p>'
    site.page(page,'Start reading the Large Signal Model',body)
    site.search.append(dict(title='Large Signal Model / Start here',group='Collection',kind='Guides',
        work_ids=[WORK,'large-signal-model'],url=page,
        text='Large Signal Model PR-LASM realization predictive closure learning probability domains Lean coverage software reference laboratory'))
    publish_scopes(reader,book)


def publish_scopes(reader, book):
    """Present the retained coverage rows alongside their written passages."""
    site=reader.site
    def link(label,target):
        return '<a href="'+html.escape(site.rel(target,SCOPE_PAGE),quote=True)+'">'+html.escape(label)+'</a>'
    body='<p class="eyebrow">Large Signal Model · Retained formal evidence</p><h1>Propositions and their recorded Lean scope</h1>'
    body+='<p>These are the 87 complete mappings recorded in the retained coverage guide. Each scope statement keeps its original qualifications. Counts are not weighted by proof difficulty. This page reports existing evidence and adds no Lean execution or proof audit.</p>'
    body+='<p>'+link('Start here',BOOK['reading_guide'])+' · '+link('Find a written statement','read/'+WORK+'/statements.html')+'</p>'
    source=reader.records[COVERAGE]
    for number,scope in book['scopes'].items():
        body+='<section id="p'+str(number)+'"><h2>Proposition '+str(number)+': '+html.escape(scope['title'])+'</h2>'
        body+='<p>'+html.escape(scope['scope'])+'</p>'
        body+='<p>'+link('Written statement',scope['statement_url'])+' · '+link('Written proof',scope['proof_url'])+' · '+link('Retained coverage row',source['source_url']+'#L'+str(scope['line']))+'</p></section>'
    site.page(SCOPE_PAGE,'Large Signal Model recorded Lean scope',body)
    site.search.append(dict(title='Large Signal Model / Recorded Lean scope',group='Collection',kind='Guides',
        work_ids=[WORK],url=SCOPE_PAGE,text='87 registered propositions formal mapping assumptions scope '+
        ' '.join(scope['title']+' '+scope['scope'] for scope in book['scopes'].values())))
