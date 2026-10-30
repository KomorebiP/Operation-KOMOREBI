"""Source-bound HTML edition of the Special Functions monograph.

Only this book's explicit print wrappers are translated. Unknown syntax fails
closed in Chapter; formulas are compared in source order after every render.
"""
import hashlib
import html
import json
import posixpath
import re

WORK = 'monographs-special-functions'
BASE = 'monographs/special-functions/monograph/'
MAIN = BASE + 'main.tex'
INDEX = 'read/' + WORK + '/index.html'
REPORT = 'documents/special-functions-reading.json'
MAIN_TITLES = [
    ('reading-map', 'Reading map'),
    ('contracted-feedback', 'Contracted nonlinear feedback'),
    ('arithmetic-depth', 'Arithmetic at complex depth'),
    ('prime-sieves', 'Prime sieves and signed measures'),
    ('orbit-spectra', 'Spectral functions of zero orbits'),
    ('sequences-and-polyphase', 'Sequences, trees and polyphase'),
    ('coupled-contractions', 'Coupled contraction functions'),
    ('finite-observation', 'Limits of finite observation'),
    ('proofs', 'Proofs and mathematical evidence'),
    ('evidence', 'Evidence and limitations'),
]
SOURCE_TITLES = {
    'sections/dilation_growth.tex': 'Positive type and tap continuity',
    'sections/dilation_parameters.tex': 'Recovering dilation parameters',
    'sections/arithmetic_inverse.tex': 'Arithmetic inverse and character resolution',
    'sections/multi_prime.tex': 'Multiple-prime geometry',
    'sections/spectral_continuation.tex': 'Spectral continuation and regularized products',
    'sections/sequence_polyphase.tex': 'Exact sequences, trees and polyphase laws',
    'sections_v11/extension_overview.tex': 'The coupled family and its scope',
    'sections_v11/coupled_visual.tex': 'Coupled growth and inverse geometry',
    'sections_v11/resolution_visual.tex': 'The resolution atlas',
    'sections/proof_map.tex': 'The proof architecture',
    'sections/dilation_full.tex': 'Appendix A. Dilation type and continuity',
    'sections/arithmetic_full.tex': 'Appendix B. Arithmetic inverse and characters',
    'sections/sieve_full.tex': 'Appendix C. Multiple-prime geometry and detectors',
    'sections/spectral_full.tex': 'Appendix D. Orbit continuation and shifts',
    'sections/sequence_full.tex': 'Appendix E. Integer sequences and polyphase laws',
    'sections_v11/coupled_growth_full.tex': 'Appendix F. Coupled entire growth and type',
    'sections_v11/coupled_inverse_full.tex': 'Appendix G. Component reduction and exact inverse',
    'sections_v11/coupled_structure_full.tex': 'Appendix H. Constant linear operator structure',
    'sections_v11/resolution_full.tex': 'Appendix I. Quantitative resolution atlas',
    'sections_v11/coupled_lab_full.tex': 'Appendix J. Coupled exact laboratory',
    'proofread_verification.tex': 'Reading-edition verification record',
    'sections_v11/release_status.tex': 'Coupled-family release record',
    'sections/release_status.tex': 'Foundational release record',
    'evidence_notes.tex': 'Evidence notes and open questions',
    'notation.tex': 'Notation and glossary',
    'references.tex': 'References',
}
CONFIG = dict(work=WORK, label='Special Functions', base=BASE, main=MAIN,
              index=INDEX, title='Special Functions: Function families and their structure',
              main_chapters=7, chapters=[dict(url=INDEX.replace('index.html', 'reading-map.html'))],
              custom_reader=True)


def mask(text):
    return ''.join('\n' if c == '\n' else ' ' for c in text)


def rewrite_commands(text, name, count, convert, optional=False):
    from readable_chapters import group
    pattern = re.compile(r'\\' + re.escape(name) + r'\b')
    pos = 0
    while match := pattern.search(text, pos):
        end = match.end()
        if optional and text[end:end+1] == '[':
            _, end = group(text, end, '[', ']')
        args = []
        for _ in range(count):
            while end < len(text) and text[end].isspace(): end += 1
            value, end = group(text, end)
            args.append(value)
        replacement = convert(*args)
        # Preserve source lines even when print-only arguments contain newlines.
        missing = text[match.start():end].count('\n') - replacement.count('\n')
        if missing < 0: raise ValueError('Conversion added source lines: ' + name)
        replacement += '\n' * missing
        text = text[:match.start()] + replacement + text[end:]
        pos = match.start() + len(replacement)
    return text


def normalize(raw):
    """Translate known book layout without rewriting a mathematical expression."""
    from readable_chapters import clean_tex, group
    text = clean_tex(raw)
    text = re.sub(r'\\makeatletter.*?\\makeatother', lambda m: mask(m[0]), text, flags=re.S)
    text = rewrite_commands(text, 'hypertarget', 2, lambda key, body: body)
    text = rewrite_commands(text, 'chapter', 1, lambda title: r'\section*{' + title + '}', optional=True)
    text = rewrite_commands(text, 'FrontChapter', 1, lambda title: r'\section*{' + title + '}')
    text = rewrite_commands(text, 'pageheading', 2, lambda family, title: r'\subsection*{' + title + '}')
    text = rewrite_commands(text, 'claim', 1, lambda title: r'\paragraph*{' + title + '}')
    text = rewrite_commands(text, 'MonographPart', 3,
                            lambda number, title, subtitle: r'\section*{Part ' + number + ': ' + title + '} ' + subtitle)
    for command, directory in [('fig', 'figures'), ('smallfig', 'figures'), ('vfig', 'figures_v11')]:
        text = rewrite_commands(text, command, 2, lambda name, caption, directory=directory:
            r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{' + directory + '/' + name +
            r'.pdf}\caption{' + caption + r'}\label{fig:' + name + r'}\end{figure}', optional=True)
    text = re.sub(r'\\begin\{verbatim\}(.*?)\\end\{verbatim\}',
                  lambda m: r'\begin{lstlisting}' + m[1] + r'\end{lstlisting}', text, flags=re.S)
    text = re.sub(r'\\(?:begin|end)\{minipage\}(?:\[[bt]\])?(?:\{\\linewidth\})?', lambda m: mask(m[0]), text)
    text = re.sub(r'\\begin\{longtable\}\[\]', r'\\begin{longtable}', text)
    text = re.sub(r'\\begin\{tabular\}', r'\\begin{longtable}', text).replace(r'\end{tabular}', r'\end{longtable}')
    text = re.sub(r'\\noalign\{\}|\\(?:endhead|endlastfoot|raggedleft|tightlist|RCAppendixtrue|backmatter|mainmatter|appendix|endgroup)\b', lambda m: mask(m[0]), text)
    text = re.sub(r'\\renewcommand\{\\arraystretch\}\{[\d.]+\}|\\setlength\{\\(?:itemsep|parskip)\}\{[\d.]+pt\}', lambda m: mask(m[0]), text)
    text = re.sub(r'\\addtocontents\{toc\}\{\\protect\\newpage\}|\\def\\labelenumi\{\\arabic\{enumi\}\.\}', lambda m: mask(m[0]), text)
    text = re.sub(r'\\Needspace\{\d+\\baselineskip\}', lambda m: mask(m[0]), text)
    text = rewrite_commands(text, 'url', 1, lambda url: r'\href{' + url + '}{' + url.replace('_', r'\_') + '}')
    text = rewrite_commands(text, 'texorpdfstring', 2, lambda tex, plain: tex)
    text = text.replace(r'\textbackslash', 'backslash')
    text = re.sub(r'\\textbf\{(Proof\.|(?:Theorem|Lemma|Proposition|Corollary|Definition) [A-J]\.\d+\.|Zero-radius theorem\.)\}', r'\\paragraph*{\1}', text)
    text = re.sub(r'\\vspace\{7pt\}', lambda m: mask(m[0]), text)
    if text.count('\n') != raw.count('\n'): raise ValueError('Source line map changed')
    return text


def source_url(name):
    slug = name.removesuffix('.tex').replace('sections_v11/', 'coupled-').replace('sections/', '').replace('_', '-')
    return INDEX.replace('index.html', slug + '.html')


def figure_path(reader, name):
    """Use the retained PNG only when its companion PDF equals the book figure."""
    original = BASE + name
    for base in ('monographs/special-functions/research/', 'monographs/special-functions/coupled_atlas/'):
        pdf = base + name
        png = pdf.removesuffix('.pdf') + '.png'
        if png in reader.owned and pdf in reader.owned and original in reader.owned:
            if reader.owned[original]['sha256'] == reader.owned[pdf]['sha256']:
                return png
    raise ValueError('Missing matching receipt-bound figure preview: '+name)


def source_specs(load):
    """Walk every body input in authored order; reject changes to the selection."""
    from readable_chapters import clean_tex
    main = load(MAIN)
    heading = r'\\(?:chapter|FrontChapter)\{[^{}]+\}|\\MonographPart\{V\}'
    matches = list(re.finditer(heading, clean_tex(main)))
    if len(matches) != len(MAIN_TITLES): raise ValueError('Review Special Functions chapter boundaries')
    specs = []
    design = load(BASE+'monograph-design.tex')
    preface_start = design.index(r'\FrontChapter{Preface}')
    preface_end = design.index(r'\clearpage',preface_start)
    specs.append(dict(source=BASE+'monograph-design.tex',url=INDEX.replace('index.html','preface.html'),
                      title='Preface',start_line=design.count('\n',0,preface_start)+1,
                      end_line=design.count('\n',0,preface_end)+1,parent=INDEX))
    included = set()
    def include(name, parent):
        if name not in SOURCE_TITLES: raise ValueError('Unselected Special Functions input: ' + name)
        if name in included: raise ValueError('Repeated Special Functions body input: ' + name)
        included.add(name)
        spec = dict(source=BASE+name, url=source_url(name), title=SOURCE_TITLES[name], parent=parent)
        specs.append(spec)
        for child in re.findall(r'\\input\{([^{}]+)\}', clean_tex(load(spec['source']))): include(child, spec['url'])
    for i, (match, (slug, title)) in enumerate(zip(matches, MAIN_TITLES)):
        start = main.count('\n', 0, match.start()) + 1
        end = main.count('\n', 0, matches[i+1].start()) if i+1 < len(matches) else len(main.splitlines())-1
        spec = dict(source=MAIN, url=INDEX.replace('index.html', slug+'.html'), title=title,
                    start_line=start, end_line=end, parent=INDEX)
        specs.append(spec)
        fragment = '\n'.join(main.splitlines()[start-1:end])
        for name in re.findall(r'\\input\{([^{}]+)\}', clean_tex(fragment)): include(name, spec['url'])
    if included != set(SOURCE_TITLES): raise ValueError('Special Functions input coverage changed')
    return specs


def prepare_book(reader, config):
    from readable_chapters import Chapter, chapter_text, manuscript_macros, manuscript_bibliography
    def load(path):
        record = reader.add(path)
        if not record: raise ValueError('Missing receipt-bound Special Functions source: '+path)
        return reader.site.read_source(record).decode('utf-8-sig')
    main = load(MAIN)
    macros = manuscript_macros(main, {'dd', 'A', 'Z'})
    specs = source_specs(load)
    config['chapters'] = specs
    references = manuscript_bibliography(normalize(load(BASE+'references.tex')))
    labels, chapters = {}, []
    chapter_number = figure_number = 0
    # The front-matter bibliography patch is print infrastructure, not prose.
    for spec in specs:
        if spec['source']==MAIN:
            slug=spec['url'].rsplit('/',1)[-1].removesuffix('.html')
            chapter_number=[item[0] for item in MAIN_TITLES].index(slug)
            figure_number=0
        raw = load(spec['source'])
        selected = chapter_text(raw, spec)
        if spec['source'] == BASE+'references.tex':
            selected = re.sub(r'\\makeatletter.*?\\makeatother', lambda m: mask(m[0]), selected, flags=re.S)
        chapter = Chapter(normalize(selected), macros, check_refs=False)
        chapter.url, chapter.base = spec['url'], BASE
        chapter.citations = {entry['key']: (entry['key'], chapter.relative(source_url('references.tex'))+'#ref-'+entry['key']) for entry in references}
        chapter.external_inputs = {name: dict(url=source_url(name), title=SOURCE_TITLES[name], note='') for name in SOURCE_TITLES}
        for node in chapter.nodes:
            if node['kind']=='figure':
                figure_number+=1
                node['reference_label']=str(chapter_number)+'.'+str(figure_number)
        for key, node in chapter.labels.items():
            if key in labels: raise ValueError('Duplicate Special Functions label: '+key)
            node['url'] = chapter.url
            node.setdefault('reference_label', node['title'] or spec['title'])
            if key.startswith('ch:'):
                node['reference_label'] = str([slug for slug,title in MAIN_TITLES].index(spec['url'].rsplit('/',1)[-1].removesuffix('.html')))
            elif key.startswith('app:') and spec['title'].startswith('Appendix '):
                node['reference_label'] = spec['title'][9]
            labels[key] = node
        for node in chapter.nodes:
            if node['kind']=='figure':
                name = re.search(r'\\includegraphics\[[^]]+\]\{([^}]+)\}', node['body'])[1]
                figure_path(reader, name)
        chapters.append((spec, raw, chapter))
    for spec, raw, chapter in chapters:
        chapter.labels = labels
        chapter.validate_references()
    return dict(config=config, chapters=chapters, references=references, macros=macros, main=main)


def render_book(reader, book):
    from readable_chapters import (HEADINGS, chapter_text, original_math, render_table,
                                   group, passage_links, reading_options, typography, plain_math)
    site, reports = reader.site, []
    chapters = book['chapters']
    for index, (spec, raw, chapter) in enumerate(chapters):
        page = spec['url']
        def nav():
            routes = [('Chapter contents', INDEX)]
            if index: routes.insert(0, ('Previous: '+chapters[index-1][0]['title'], chapters[index-1][0]['url']))
            if index+1<len(chapters): routes.append(('Next: '+chapters[index+1][0]['title'], chapters[index+1][0]['url']))
            return '<nav class="document-routes" aria-label="Chapter navigation">'+''.join('<a href="'+site.rel(url,page)+'">'+html.escape(title)+'</a>' for title,url in routes)+'</nav>'
        body = '<p class="eyebrow">Special Functions · Reading edition</p><h1>'+html.escape(spec['title'])+'</h1>'+nav()
        body += reader.work_routes(WORK,page)
        body += '<p><a href="'+reader.resolve(spec['source'],page)+'">Original TeX with line links</a></p>'+reading_options()
        headings = [n for n in chapter.nodes if n['kind'] in HEADINGS]
        body += '<nav class="chapter-contents" aria-label="On this page"><h2>On this page</h2><ol>'+''.join('<li><a href="#'+n['id']+'">'+html.escape(typography(n['title']))+'</a></li>' for n in headings)+'</ol></nav>'
        body += '<article id="chapter-text" class="readable-chapter">'
        proof_targets = {}
        statement = None
        for n in headings:
            if re.match(r'(?:Theorem|Lemma|Proposition|Corollary|Zero-radius theorem)\b',n['title']): statement = n
            elif n['title']=='Proof.' and statement:
                proof_targets[statement['id']] = n['id']
                statement = None
        for node in chapter.nodes:
            kind = node['kind']
            links = '<a href="#'+node['id']+'">Permalink</a> · <a href="'+reader.resolve(spec['source'],page,'L'+str(node['line']))+'">Source line '+str(node['line'])+'</a>'
            if kind in HEADINGS:
                level = HEADINGS[kind]
                proof_link = '<a href="#'+proof_targets[node['id']]+'">Read proof</a>' if node['id'] in proof_targets else ''
                body += '<h'+str(level)+' id="'+node['id']+'">'+chapter.inline(node['title'])+'</h'+str(level)+'>'+passage_links(links,proof_link)
            elif kind=='figure':
                match = re.search(r'\\includegraphics\[[^]]+\]\{([^}]+)\}\\caption\{',node['body'])
                caption, _ = group(node['body'],match.end()-1)
                path = figure_path(reader, match[1])
                image = reader.image_url(path,page)
                dimensions = reader.images[path]
                alt = plain_math(caption.replace('$',''))[0]
                body += '<figure id="'+node['id']+'"><img src="'+image+'" width="'+str(dimensions['width'])+'" height="'+str(dimensions['height'])+'" alt="'+html.escape(alt,quote=True)+'" loading="lazy"><figcaption id="caption-'+node['id']+'">'+chapter.inline(caption)+'</figcaption>'+passage_links(links)+'</figure>'
            elif kind=='longtable':
                body += '<section id="'+node['id']+'">'+render_table(node,chapter)+passage_links(links)+'</section>'
            elif kind=='lstlisting':
                body += '<section id="'+node['id']+'"><pre tabindex="0" aria-label="Original code or recorded output"><code>'+html.escape(node['body'])+'</code></pre>'+passage_links(links)+'</section>'
            elif kind=='thebibliography':
                body += '<section id="'+node['id']+'">'
                for entry in book['references']:
                    body += '<section id="ref-'+entry['key']+'"><h3>'+html.escape(entry['key'])+'</h3>'+chapter.paragraphs(normalize(entry['body']))+'</section>'
                body += passage_links(links)+'</section>'
            elif kind=='text':
                body += '<section id="'+node['id']+'">'+chapter.paragraphs(node['body'])+passage_links(links)+'</section>'
            else: raise ValueError('Unsupported Special Functions block: '+kind)
            if kind not in {'figure','thebibliography','lstlisting'}:
                site.search.append(dict(title='Special Functions / '+spec['title'],group='Collection',kind='Papers and source',work_ids=[WORK],url=page+'#'+node['id'],text=re.sub(r'\s+',' ',node['title']+' '+node['body'])))
        body += '</article>'+nav()
        body += '<details class="document-provenance"><summary>Source and conversion record</summary><p>This HTML edition follows the retained manuscript. It adds no proof review or Lean coverage.</p><p><a href="'+site.rel(REPORT,page)+'">Source identities and equation checks</a></p></details>'
        # Ignore code literals, exactly as the shared parser does for listings.
        selected = re.sub(r'\\begin\{verbatim\}.*?\\end\{verbatim\}', lambda m: mask(m[0]), chapter_text(raw,spec), flags=re.S)
        expressions = original_math(selected)
        if chapter.math != expressions:
            first = next((i for i,(a,b) in enumerate(zip(chapter.math,expressions)) if a!=b),min(len(chapter.math),len(expressions)))
            raise ValueError('Special Functions mathematics differs: '+spec['source']+' at '+str(first)+' '+repr(chapter.math[first:first+1])+' != '+repr(expressions[first:first+1]))
        site.page(page, 'Special Functions: '+spec['title'], body)
        reports.append(dict(**spec,source_sha256=hashlib.sha256(reader.site.read_source(reader.records[spec['source']])).hexdigest(),math_expressions=len(expressions),math_sequence_sha256=hashlib.sha256(json.dumps(expressions,ensure_ascii=False).encode()).hexdigest(),macros=book['macros'],nodes=[{k:n[k] for k in ('id','line','end_line','kind')} for n in chapter.nodes],new_proof_review=False,new_lean_execution=False))
    site.write(REPORT,json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    body = '<p class="eyebrow">Read Special Functions</p><h1>Special Functions</h1><p class="lede">Function families and their structure</p><p>Read the seven main chapters, the ten proof appendices, and the notation, references and evidence notes. The HTML edition follows the retained monograph, with selectable equations, original figures, and links to the source of each passage.</p>'+reader.work_routes(WORK,INDEX)
    body += '<p><a class="button" href="reading-map.html">Start reading</a> <a href="'+site.rel(source_url('notation.tex'),INDEX)+'">Notation and glossary</a> · <a href="'+site.rel(source_url('references.tex'),INDEX)+'">References</a></p>'
    body += '<nav class="chapter-contents" aria-label="Special Functions contents"><h2>Contents</h2><ol>'
    for spec,raw,chapter in chapters:
        if spec['parent']==INDEX:
            body += '<li><a href="'+site.rel(spec['url'],INDEX)+'">'+html.escape(spec['title'])+'</a>'
            descendants = [s for s,_,_ in chapters if s['parent']!=INDEX and next((p['url'] for p,_,_ in chapters if p['url']==s['parent']),None)==spec['url']]
            if descendants:
                body += '<ul>'+''.join('<li><a href="'+site.rel(s['url'],INDEX)+'">'+html.escape(s['title'])+'</a></li>' for s in descendants)+'</ul>'
            body += '</li>'
    body += '</ol></nav><h2>Proof appendices</h2><ol>'+''.join('<li><a href="'+site.rel(s['url'],INDEX)+'">'+html.escape(s['title'])+'</a></li>' for s,_,_ in chapters if s['title'].startswith('Appendix '))+'</ol>'
    body += '<h2>Formal coverage and evidence</h2><p>The recorded formal companion covers 68 named declarations in a finite core and Block 1. The full analytic monograph is not formalized in Lean. The evidence notes distinguish analytic proofs, finite computations, classical inputs and open questions.</p><p><a href="'+site.rel('collection/works/'+WORK+'.html',INDEX)+'#lean">Lean sources and recorded scope</a> · <a href="'+site.rel(source_url('evidence_notes.tex'),INDEX)+'">Evidence notes and open questions</a></p>'
    pdfs = [r for r in reader.records.values() if r['work']==WORK and r['format']=='pdf']
    body += '<h2>PDF and companion volumes</h2><ul>'+''.join('<li><a href="'+site.rel(r['url'],INDEX)+'">'+html.escape(r['title'])+'</a></li>' for r in pdfs)+'</ul>'
    site.page(INDEX,'Read Special Functions',body)
    site.search.append(dict(title='Special Functions / Chapter contents',group='Collection',kind='Papers and source',work_ids=[WORK],url=INDEX,text='Special Functions contracted feedback arithmetic complex depth prime sieves spectral zeta sequences coupled growth resolution proof appendices glossary'))
    return []


def verify(root, documents, pages):
    """Independently re-read published sources and HTML, rejecting omissions."""
    from html.parser import HTMLParser
    from readable_chapters import chapter_text, original_math, expand_math, manuscript_macros
    from check_reader_site import check_png_image_sizes
    records = {r['repository_path']:r for r in documents['files']}
    def load(path):
        raw = (root/records[path]['file_url']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==records[path]['sha256'], ('Special Functions source identity',path)
        return raw.decode('utf-8-sig')
    specs = source_specs(load)
    reports = json.loads((root/REPORT).read_bytes())
    assert len(reports)==len(specs), 'Special Functions reading coverage changed'
    macros = manuscript_macros(load(MAIN), {'dd','A','Z'})
    class MathText(HTMLParser):
        def __init__(self):
            super().__init__();self.depth=0;self.expressions=[]
        def handle_starttag(self,tag,attrs):
            if self.depth:self.depth+=1
            elif 'arithmatex' in dict(attrs).get('class','').split():self.depth=1;self.expressions.append('')
        def handle_endtag(self,tag):
            if self.depth:self.depth-=1
        def handle_data(self,data):
            if self.depth:self.expressions[-1]+=data
    total = 0
    for spec,report in zip(specs,reports):
        assert all(report[k]==v for k,v in spec.items()), 'Special Functions source selection changed'
        raw = load(spec['source'])
        assert report['source_sha256']==records[spec['source']]['sha256']
        selected = re.sub(r'\\begin\{verbatim\}.*?\\end\{verbatim\}',lambda m:mask(m[0]),chapter_text(raw,spec),flags=re.S)
        expressions = original_math(selected)
        assert report['math_expressions']==len(expressions)
        assert report['math_sequence_sha256']==hashlib.sha256(json.dumps(expressions,ensure_ascii=False).encode()).hexdigest()
        assert report['macros']==macros
        assert not report['new_proof_review'] and not report['new_lean_execution']
        parsed = MathText();parsed.feed((root/spec['url']).read_text(encoding='utf-8'))
        assert [x[2:-2] for x in parsed.expressions]==[expand_math(x,macros) for x in expressions], ('Special Functions HTML math changed',spec['url'])
        check_png_image_sizes(root,spec['url'],pages[spec['url']].images)
        for node in report['nodes']:
            assert node['id'] in pages[spec['url']].ids
            assert 'L'+str(node['line']) in pages[records[spec['source']]['url']].ids
        total += len(expressions)
    return dict(reading_sections=len(specs),mathematical_expressions=total)
