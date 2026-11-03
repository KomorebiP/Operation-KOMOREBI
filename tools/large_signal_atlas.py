"""Source-bound HTML atlas and reading aids for the Large Signal Model."""
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import posixpath
import re

from large_signal_reading import WORK, BOOK, SCOPE_PAGE
from large_signal_atlas_descriptions import FIGURES, QUESTIONS
from readable_chapters import Chapter, group, original_math, manuscript_macros, PANELS, HEADINGS

BASE = 'monographs/large-signal-model/Visual_Companion/'
SOURCE = BASE + 'atlas.tex'
PDF = BASE + 'build/Realization_Calculus_Large_Signal_Model_Theoretical_Atlas.pdf'
PROOF_MAP = BASE + 'PROOF_MAP.json'
FIGURE_MAP = BASE + 'FIGURES.json'
EXACT_EXAMPLE = BASE + 'figures/exact_example.json'
INDEX = 'read/' + WORK + '/atlas/index.html'
REPORT = 'documents/' + WORK + '-atlas.json'
RECEIPTS = 'assets/atlas/' + WORK + '/figures.json'
SPEC_FILE = Path(__file__).with_name('large_signal_atlas_sources.json')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def specs(source):
    """Read the retained plate metadata and keep absolute source line anchors."""
    starts = list(re.finditer(r'\\plate\{', source))
    if len(starts) != 17:
        raise ValueError('Review the changed LSM atlas plate inventory')
    first = source.index('An observation, its archive, a predictive summary')
    result = [dict(number=0, title='Four contracts, one model', subtitle='Orientation',
        locator='', line=source.count('\n', 0, first)+1,
        end_line=source.count('\n', 0, starts[0].start()),
        url=posixpath.dirname(INDEX)+'/orientation.html',
        body='\n'*source.count('\n', 0, first)+source[first:starts[0].start()])]
    for i, match in enumerate(starts, 1):
        end = match.end()-1
        values = []
        for _ in range(4):
            value, end = group(source, end)
            values.append(value)
        number, title, subtitle, locator = values
        if number != str(i):
            raise ValueError('Review changed LSM atlas numbering')
        stop = starts[i].start() if i < len(starts) else source.index(r'\end{document}')
        result.append(dict(number=i, title=title, subtitle=subtitle, locator=locator,
            line=source.count('\n', 0, match.start())+1,
            end_line=source.count('\n', 0, stop),
            url=posixpath.dirname(INDEX)+'/v'+str(i).zfill(2)+'.html',
            body='\n'*source.count('\n', 0, end)+source[end:stop]))
    return result


def normalize(text):
    """Adapt only the atlas's declared print wrappers; preserve all math/lines."""
    def mask(match):
        return ''.join('\n' if c == '\n' else ' ' for c in match[0])
    text = re.sub(r'\\diagram(?:\[[^\]]+\])?\{([^{}]+)\}',
        lambda m:r'\begin{figure}\includegraphics[width=\linewidth]{'+m[1]+r'.pdf}\end{figure}', text)
    for command, title in [('claim','The mathematical point'), ('boundary','Scope'), ('nav','Formal route')]:
        while (match := re.search(r'\\'+command+r'\{', text)):
            value, end = group(text, match.end()-1)
            text = text[:match.start()]+r'\begin{readerroadmap}[title={'+title+'}]'+value+r'\end{readerroadmap}'+text[end:]
    text = re.sub(r'\{\\small\b', mask, text)
    text = re.sub(r'\\(?:par|noindent|small)\b|\\vspace\{[^{}]+\}', mask, text)
    text = text.replace(r'\end{tabular}}',r'\end{tabular} ')
    text = text.replace(r'\\[5pt]', r'\\'+' '*5)
    text = text.replace(r'\LaTeX{}','LaTeX')
    return text


def chapter_for(spec, macros):
    chapter = Chapter(normalize(spec['body']), macros, check_refs=False)
    chapter.url = spec['url']
    return chapter


def metadata():
    return json.loads(SPEC_FILE.read_text(encoding='utf-8'))


def validate_source(read):
    data = metadata()
    for path, sha in data['inputs'].items():
        if digest(read(path)) != sha:
            raise ValueError('Review changed LSM visual source: '+path)
    selected = specs(read(SOURCE).decode('utf-8-sig'))
    if [{k:v for k,v in p.items() if k!='body'} for p in selected] != data['pages']:
        raise ValueError('Review changed LSM visual ranges')
    return data, selected


def sequence():
    return [dict(url=p['url'], title=('Orientation: ' if p['number']==0 else str(p['number'])+'. ')+p['title'])
            for p in metadata()['pages']]


def config():
    return dict(work=WORK, label='Large Signal Model visual guide', overview_label='Large Signal Model',
        index=INDEX, chapters=sequence(), menu_title='Visual guide', index_title='All plates',
        footer_index_only=True)


def prepare(reader):
    if WORK not in getattr(reader, 'readable_books', {}):
        return
    for path in metadata()['inputs']:
        reader.add(path)
    read = lambda path:reader.site.read_source(reader.records[path])
    data, pages = validate_source(read)
    source = read(SOURCE).decode('utf-8-sig')
    macros = manuscript_macros(source, ['R','im','TV','diag'])
    chapters = [(p, read(SOURCE), chapter_for(p, macros)) for p in pages]
    if [m for p in pages for m in original_math(p['body'])] != original_math(source[source.index(r'\begin{document}'):]):
        raise ValueError('Incomplete LSM visual mathematical body')
    from reader_figure_assets import prepare as prepare_figures
    figure_config = dict(base=BASE, figure_source_root=BASE, figure_receipts=RECEIPTS)
    figures = prepare_figures(reader, figure_config, chapters)
    main = reader.readable_books[WORK]
    propositions = {int(n['number']):(chapter,n) for _,_,chapter in main['chapters']
                    for n in chapter.nodes if n['kind']=='proposition'}
    routes = {}
    proofmap = json.loads(read(PROOF_MAP))
    if proofmap['fresh_Lean_execution'] is not False or [p['plate'] for p in proofmap['plates']] != list(range(1,17)):
        raise ValueError('Review the changed LSM visual proof map')
    for plate in proofmap['plates']:
        selected = []
        for row in plate['propositions']:
            number = row['id']; scope = main['scopes'][number]
            if (row['title'],row['scope']) != (scope['title'],scope['scope']):
                raise ValueError('Stale LSM visual scope for P'+str(number))
            modules = []
            for module in row['modules']:
                if not re.fullmatch(r'KomorebiLSM/[A-Za-z0-9_/]+\.lean', module):
                    raise ValueError('Unexpected LSM module path')
                record = reader.add('monographs/large-signal-model/Lean/'+module)
                if not record:
                    raise ValueError('Missing mapped LSM module: '+module)
                modules.append(dict(path=record['repository_path'],url=record['url'],label=module))
            selected.append(dict(number=number,title=row['title'],statement=scope['statement_url'],
                proof=scope['proof_url'],scope=SCOPE_PAGE+'#p'+str(number),modules=modules))
            chapter, node = propositions[number]
            title = 'Visual guide: '+pages[plate['plate']]['title']
            chapter.related_readings.setdefault(node['id'], []).append((title,pages[plate['plate']]['url']))
        routes[plate['plate']] = selected
    reader.large_signal_atlas = dict(pages=pages,chapters=chapters,macros=macros,
        figures=figures,figure_config=figure_config,routes=routes,
        source_inputs=data['inputs'],module_links={PurePosixPath(m['path']).stem:m['url']
            for rows in routes.values() for r in rows for m in r['modules']})


TABLE_AIDS = {
 0:dict(caption='Four contracts and the questions they answer',
        headers=['Contract','Defining identity','Question answered'],row_header_column=0),
 17:dict(caption='Routes from the atlas into the retained formal source',
         headers=['Plates','Proof route',r'Primary entry modules in \texttt{Lean/KomorebiLSM/}'],row_header_column=0),
}


def assets(site, page):
    result = ''
    for name in ['large-signal-atlas.css','large-signal-atlas.js']:
        url = site.rel('assets/'+name,page)+'?v='+digest((site.root/'website/assets'/name).read_bytes())[:12]
        result += '<link rel="stylesheet" href="'+url+'">' if name.endswith('.css') else '<script defer src="'+url+'"></script>'
    return result


def module_links(markup, atlas, site, page):
    def replace(match):
        target = atlas['module_links'].get(match[1].removesuffix('.lean'))
        return '<a href="'+site.rel(target,page)+'">'+match[0]+'</a>' if target else match[0]
    return re.sub(r'<code>([A-Za-z0-9_.]+)</code>', replace, markup)


def figure(reader, atlas, spec, node):
    from reader_figure_assets import image
    from reader_documents import png_dimensions
    name = re.search(r'\\includegraphics\[[^\]]+\]\{([^{}]+)\}',node['body'])[1]
    stem = PurePosixPath(name).stem
    source, target, sha = image(reader,atlas['figure_config'],{},atlas['figures'],name,spec['url'])
    receipt = atlas['figures'][source]
    width,height = png_dimensions((reader.site.root/'website'/receipt['image']).read_bytes())
    alt, description = FIGURES[stem]
    e = html.escape
    return ('<figure class="lsm-atlas-figure"><a href="'+target+'" aria-label="Open full-size diagram: '+e(alt,quote=True)+'">'
        '<img src="'+target+'" width="'+str(width)+'" height="'+str(height)+'" alt="'+e(alt,quote=True)+'" loading="lazy"></a>'
        '<figcaption>'+e(alt)+'</figcaption><details class="lsm-figure-description"><summary>Read the diagram in words</summary><p>'+e(description)+'</p></details>'
        '<p class="lsm-figure-links"><a href="'+target+'">Open full-size image</a> · <a href="'+reader.resolve(source,spec['url'])+'">Original vector diagram</a></p></figure>')


def proof_routes(reader, spec, atlas):
    site = reader.site; page = spec['url']; e = html.escape
    body = '<section class="lsm-proof-routes" id="proof-routes"><h2>Follow the proofs</h2>'
    rows = atlas['routes'].get(spec['number'], [])
    if not rows:
        body += '<p><a href="'+site.rel('read/'+WORK+'/statements.html',page)+'">Find any of the 87 statements and written proofs</a> · <a href="'+site.rel(SCOPE_PAGE,page)+'">Read the recorded scope</a></p>'
    else:
        body += '<ul>'
        for row in rows:
            body += '<li><a href="'+site.rel(row['statement'],page)+'">Proposition '+str(row['number'])+': '+e(row['title'])+'</a><span class="lsm-proof-actions">'
            body += '<a href="'+site.rel(row['proof'],page)+'">Written proof</a> · <a href="'+site.rel(row['scope'],page)+'">Recorded Lean scope</a></span></li>'
        body += '</ul>'
        modules = {m['path']:m for row in rows for m in row['modules']}
        body += '<details><summary>Inspect the mapped Lean modules</summary><ul>'+''.join(
            '<li><a href="'+site.rel(m['url'],page)+'"><code>'+e(m['label'])+'</code></a></li>' for m in modules.values())+'</ul></details>'
    return body+'</section>'


def source_article(reader, atlas, spec, chapter):
    from readable_chapters import passage_links, render_table
    site = reader.site; page = spec['url']; e = html.escape
    body = '<article id="chapter-text" class="readable-chapter atlas-plate lsm-atlas-source" aria-label="Original atlas text">'
    for node in chapter.nodes:
        kind = node['kind']; identifier = node['id']
        links = '<a href="#'+identifier+'">Permalink</a> · <a href="'+reader.resolve(SOURCE,page,'L'+str(node['line']))+'">Source line '+str(node['line'])+'</a>'
        if kind == 'figure':
            body += '<section id="'+identifier+'">'+figure(reader,atlas,spec,node)+passage_links(links)+'</section>'
        elif kind in {'tabular','tabularx','table'}:
            body += '<section id="'+identifier+'">'+module_links(render_table(node,chapter,TABLE_AIDS[spec['number']]),atlas,site,page)+passage_links(links)+'</section>'
        elif kind == 'text' or kind in PANELS:
            extra = ' lsm-scope' if node['title']=='Scope' else ''
            body += '<section id="'+identifier+'" class="reading-block '+kind+extra+'">'
            if kind in PANELS:
                body += '<h2>'+chapter.inline(node['title'] or PANELS[kind])+'</h2>'
            body += module_links(chapter.paragraphs(node['body']),atlas,site,page)+passage_links(links)+'</section>'
        elif kind in HEADINGS:
            body += '<h2 id="'+identifier+'">'+chapter.inline(node['title'])+'</h2>'+passage_links(links)
        else:
            raise ValueError('Unsupported LSM visual block: '+kind)
    if chapter.math != original_math(spec['body']):
        raise ValueError('LSM visual mathematical sequence changed on '+str(spec['number']))
    return body+'</article>'


def render(reader):
    if not hasattr(reader, 'large_signal_atlas'):
        return
    from reading_navigation import navigation, outline, resources
    from readable_chapters import reading_options
    atlas = reader.large_signal_atlas; site = reader.site; e = html.escape
    reports = []
    for spec,raw,_ in atlas['chapters']:
        page = spec['url']; number = spec['number']; chapter = chapter_for(spec,atlas['macros'])
        label = 'Orientation' if number==0 else 'Plate '+str(number)+' of 17'
        body = assets(site,page)+'<p class="eyebrow">Large Signal Model · '+label+'</p><h1>'+e(spec['title'])+'</h1>'
        if number:
            body += '<p class="lsm-atlas-subtitle">'+e(spec['subtitle'])+'</p>'
            body += '<p class="lsm-reading-question"><strong>Question to keep in view.</strong> '+e(QUESTIONS[number])+'</p>'
        body += reader.work_routes(WORK,page)+navigation(config(),page)
        tools = '<p><a href="'+reader.viewer_url(reader.records[PDF],page,'page='+str(number+2))+'">Original PDF page</a> · <a href="'+reader.resolve(SOURCE,page,'L'+str(spec['line']))+'">Atlas source</a></p>'
        tools += reading_options('Show source lines and passage links. The original atlas text and equations are retained.')
        toc = '<nav aria-label="On this plate"><h2 id="contents">On this plate</h2><ul>'
        toc += ''.join('<li><a href="#'+n['id']+'">'+e('Diagram and description' if n['kind']=='figure' else n['title'])+'</a></li>' for n in chapter.nodes if n['kind']=='figure' or n['title'])
        toc += '<li><a href="#proof-routes">Follow the proofs</a></li>'
        if number==3:toc += '<li><a href="#closure-explorer">Try the exact comparison</a></li>'
        body += resources(tools)+outline(toc+'</ul></nav>')
        body += source_article(reader,atlas,spec,chapter)
        if number==3:
            from large_signal_explorer import markup
            body += markup()
        elif number in {4,9}:
            body += '<aside class="lsm-reading-question"><p><a href="v03.html#closure-explorer">Explore the same operator and its causal delay state</a>.</p></aside>'
        body += proof_routes(reader,spec,atlas)+navigation(config(),page,'bottom')
        body += '<details class="document-provenance"><summary>Source and reading aids</summary><p>The atlas text, mathematics, plate order, and original diagrams are retained. Questions, diagram descriptions, navigation, and the bounded comparison explorer are web reading aids. No original TeX build or Lean execution is added.</p><p><a href="'+site.rel(REPORT,page)+'">Source identities and conversion checks</a></p></details>'
        site.page(page,'Large Signal Model visual atlas / '+spec['title'],body)
        site.search.append(dict(title='Large Signal Model visual guide / '+spec['title'],group='Collection',kind='Guides',
            visual_guide=True,work_ids=[WORK],url=page,text=label+' '+spec['title']+' '+spec['subtitle']+' '+QUESTIONS.get(number,'Four contracts, one model')))
        reports.append(dict(number=number,url=page,source=SOURCE,start_line=spec['line'],end_line=spec['end_line'],
            math_expressions=len(chapter.math),math_sequence_sha256=digest(json.dumps(chapter.math,ensure_ascii=False).encode()),
            nodes=[dict(id=n['id'],line=n['line'],kind=n['kind']) for n in chapter.nodes]))
    publish_index(reader,atlas)
    report = dict(schema=1,source_inputs=atlas['source_inputs'],source_revision=site.revision,index=INDEX,
        original_plates=17,orientation_pages=1,html_pages=reports,figures=list(atlas['figures'].values()),
        proof_routes=atlas['routes'],math_expressions=194,new_tex_build=False,new_lean_execution=False,
        new_proof_review=False,original_figure_generator_executed=False,
        interactive_audit='verification/large-signal-atlas/run/manifest.json')
    site.write(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def publish_index(reader, atlas):
    site = reader.site; e = html.escape
    body = assets(site,INDEX)+'<div class="lsm-atlas-index"><p class="eyebrow">Large Signal Model · A theoretical atlas</p><h1>See what a predictive state must preserve</h1>'
    body += '<p class="lsm-atlas-lede">Seventeen visual plates connect realization, predictive closure, memory, and certified probability domains. Start with the four contracts, follow a short route, or choose a question below.</p>'
    body += reader.work_routes(WORK,INDEX)
    body += '<p class="lsm-atlas-start"><a class="button" href="orientation.html">Start with the four contracts</a><a href="v03.html#closure-explorer">Try two states with the same observation</a></p>'
    body += '<div class="lsm-atlas-paths" aria-label="Suggested reading paths">'
    for title,summary,numbers in [
        ('Build a predictive state','Begin with the obstruction, then add the observable directions needed for closure.',[3,4,9]),
        ('Understand lost paths and memory','Follow discarded contributions through composition, history, and error propagation.',[5,6,7,8]),
        ('Follow probability certificates','Move from behavior coordinates to domains, matrix witnesses, and statistical guarantees.',[10,11,12,13,14,15,16,17])]:
        body += '<section><h2>'+title+'</h2><p>'+summary+'</p><p>'+ ' · '.join('<a href="v'+str(n).zfill(2)+'.html">Plate '+str(n)+'</a>' for n in numbers)+'</p></section>'
    body += '</div><section class="lsm-atlas-chooser"><h2>Choose a plate</h2><form class="lsm-atlas-filter" role="search" hidden><label for="lsm-visual-query">Find a topic, question, or proposition</label><input id="lsm-visual-query" type="search" aria-controls="lsm-visual-list" placeholder="Closure, memory, P14, probability…"><button type="reset">Clear</button></form>'
    body += '<p id="lsm-visual-count" role="status" aria-live="polite">17 plates</p><ol id="lsm-visual-list" class="lsm-atlas-cards">'
    for p in atlas['pages'][1:]:
        n = p['number']; keywords = ' '.join('P'+str(r['number'])+' Proposition '+str(r['number']) for r in atlas['routes'].get(n,[]))
        body += '<li class="lsm-atlas-card" data-search="'+e(p['title']+' '+p['subtitle']+' '+QUESTIONS[n]+' '+keywords,quote=True)+'"><a href="'+site.rel(p['url'],INDEX)+'"><span class="eyebrow">Plate '+str(n)+' · '+e(p['locator'].replace('--','–'))+'</span><h3>'+e(p['title'])+'</h3><p>'+e(QUESTIONS[n])+'</p></a></li>'
    body += '</ol><p id="lsm-visual-empty" hidden>No plates match. Try another topic or clear the search.</p></section>'
    body += '<p class="lsm-atlas-boundary">This is a visual companion to the mathematical volume. Exact identities, geometric obstructions and worked rational examples connect the theory to its formal proofs. The source scope notes remain with every plate; the finite explorer illustrates the declared example.</p>'
    body += '<p><a href="'+reader.viewer_url(reader.records[PDF],INDEX)+'">Read the original 19-page PDF</a> · <a href="'+site.rel(REPORT,INDEX)+'">Conversion record</a> · <a href="'+reader.resolve(EXACT_EXAMPLE,INDEX)+'">Retained exact-example receipt</a></p></div>'
    site.page(INDEX,'Large Signal Model visual atlas',body)
    site.search.append(dict(title='Large Signal Model / Visual atlas',group='Collection',kind='Guides',visual_guide=True,
        work_ids=[WORK],url=INDEX,text='17 visual plates closure fibers delay memory probability certificates exact comparison explorer'))


def inventory(root, files):
    from reader_documents import png_dimensions
    records = {r['repository_path']:r for r in files}
    if PDF not in records:
        raise ValueError('Missing Large Signal Model visual PDF')
    receipts = json.loads((root/'website'/RECEIPTS).read_bytes())
    record = next(r for r in receipts['figures'] if r['image'].endswith('/00_architecture.png'))
    raw = (root/'website'/record['image']).read_bytes()
    if digest(raw) != record['image_sha256']:
        raise ValueError('Changed Large Signal Model visual preview')
    width,height = png_dimensions(raw)
    return dict(work=WORK,label='Large Signal Model',title=BOOK['title'],number=None,
        short_title='Predictive state, memory, and probability',
        summary='Seventeen plates and an orientation page, with original diagrams, proof routes, and an exact closure explorer.',
        units=18,unit_kind='pages',source_unit_kind='plates and orientation',
        topics='large signal model realization prediction closure fibers memory delay probability certificates',
        preview=dict(image=record['image'],sha256=record['image_sha256'],width=width,height=height),
        manuscript=BOOK['index'],overview='collection/works/'+WORK+'.html',html_atlas=INDEX,
        visual_pdf=records[PDF]['url'],pdf_source=PDF,pdf_sha256=records[PDF]['sha256'],integrated_pdf=False,
        sequences=[dict(id='theoretical-atlas',title='Theoretical atlas',summary='Orientation and the complete 17-plate sequence.',
            source=SOURCE,source_sha256=metadata()['inputs'][SOURCE],pages=sequence())])


def verify(root, documents, pages):
    """Authenticate inputs, every source expression, diagram, and proof route."""
    from html.parser import HTMLParser
    from readable_chapters import expand_math
    from reader_documents import png_dimensions
    class Math(HTMLParser):
        def __init__(self):
            super().__init__(); self.article = False; self.depth = 0; self.values = []
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag=='article' and attrs.get('id')=='chapter-text':self.article=True
            if not self.article:return
            if self.depth:self.depth+=1
            elif 'arithmatex' in attrs.get('class','').split():self.depth=1;self.values.append('')
        def handle_endtag(self, tag):
            if self.depth:self.depth-=1
            if tag=='article':self.article=False
        def handle_data(self, value):
            if self.article and self.depth:self.values[-1]+=value
    records = {r['repository_path']:r for r in documents['files']}
    read = lambda path:(root/records[path]['file_url']).read_bytes()
    data, selected = validate_source(read)
    report = json.loads((root/REPORT).read_bytes())
    assert report['source_inputs']==data['inputs'] and report['source_revision']==documents['source_revision']
    assert (report['original_plates'],report['orientation_pages'],report['index'])==(17,1,INDEX)
    assert len(report['html_pages'])==18 and len(report['figures'])==16
    original = json.loads((Path(__file__).resolve().parents[1]/'website'/RECEIPTS).read_bytes())
    assert report['figures']==original['figures']
    assert len({r['source'] for r in report['figures']})==16
    # Reconstruct the routes from the original map and independently published
    # main-volume node inventory; an omitted route must not pass vacuously.
    from large_signal_reading import MAIN
    nodes = json.loads((root/'documents/readable-chapters.json').read_bytes())
    statements = {}; proofs = {}
    for entry in nodes:
        if entry['source']!=MAIN:continue
        current = None
        for node in entry['nodes']:
            if node['kind']=='proposition':
                current=int(node['number']);statements[current]=entry['url']+'#'+node['id']
            elif node['kind']=='proof' and current is not None:
                proofs[current]=entry['url']+'#'+node['id'];current=None
    expected_routes = {}
    for plate in json.loads(read(PROOF_MAP))['plates']:
        expected_routes[str(plate['plate'])]=[dict(number=row['id'],title=row['title'],
            statement=statements[row['id']],proof=proofs[row['id']],scope=SCOPE_PAGE+'#p'+str(row['id']),
            modules=[dict(path='monographs/large-signal-model/Lean/'+module,
                url=records['monographs/large-signal-model/Lean/'+module]['url'],label=module) for module in row['modules']]) for row in plate['propositions']]
    assert report['proof_routes']==expected_routes
    macros = manuscript_macros(read(SOURCE).decode('utf-8-sig'),['R','im','TV','diag'])
    count = links = 0
    for spec, entry in zip(selected,report['html_pages'],strict=True):
        page = spec['url']; markup = (root/page).read_text(encoding='utf-8')
        assert (entry['number'],entry['url'],entry['source'],entry['start_line'],entry['end_line']) == (
            spec['number'],page,SOURCE,spec['line'],spec['end_line'])
        expected = original_math(spec['body'])
        assert entry['math_expressions']==len(expected)
        assert entry['math_sequence_sha256']==digest(json.dumps(expected,ensure_ascii=False).encode())
        rendered = Math(); rendered.feed(markup)
        assert [x[2:-2] for x in rendered.values]==[expand_math(x,macros) for x in expected], ('Changed LSM visual mathematics',page)
        assert (pages[page].h1,pages[page].main,pages[page].images_without_alt)==(1,1,0)
        assert len(pages[page].ids)==len(set(pages[page].ids))
        for node in entry['nodes']:
            assert node['id'] in pages[page].ids
            assert 'L'+str(node['line']) in pages[records[SOURCE]['url']].ids
        for route in report['proof_routes'].get(str(spec['number']),[]):
            for key in ['statement','proof','scope']:
                target,anchor = route[key].split('#')
                assert anchor in pages[target].ids
                assert posixpath.relpath(route[key],posixpath.dirname(page)) in pages[page].links
                links+=1
            target = route['statement'].split('#')[0]
            assert posixpath.relpath(page,posixpath.dirname(target)) in pages[target].links
            for module in route['modules']:
                assert module['url']==records[module['path']]['url']
                assert posixpath.relpath(module['url'],posixpath.dirname(page)) in pages[page].links
        count += len(expected)
    assert count==data['math_expressions']==194
    for record in report['figures']:
        raw = (root/record['image']).read_bytes()
        assert digest(raw)==record['image_sha256'] and digest(read(record['source']))==record['source_sha256']
        assert all(v>0 for v in png_dimensions(raw))
    for spec in selected:
        assert posixpath.relpath(spec['url'],posixpath.dirname(INDEX)) in pages[INDEX].links
    assert 'closure-explorer' in pages[selected[3]['url']].ids
    assert not report['new_tex_build'] and not report['new_lean_execution'] and not report['new_proof_review']
    return dict(plates=17,orientation_pages=1,diagrams=16,math_expressions=count,proof_route_links=links)
