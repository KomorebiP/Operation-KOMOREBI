"""One canonical Smith/RLC reader with exact source and legacy-route bindings."""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit
import zipfile

PAGE = 'read/smith-chart/research.html'
BASE = 'research/smith-chart/unified'
TITLE = 'Smith chart and minimum reactive RLC synthesis'
ALIASES = {'read/smith-chart/continuation.html': 'current-results',
    **{'read/smith-chart/'+slug+'.html': slug for slug in ('exact-six','composition','families','obstruction','quantitative-transfer','effective-margin')},
    'collection/demonstrations/SMITH_CHART.html': 'companion-guide',
    'collection/demonstrations/SMITH_FIRST_ORDER_RL.html': 'one-inductor',
    'collection/demonstrations/SMITH_SINGULAR_COMPLETION.html': 'singular-completion'}
NEW_CHAPTERS = {'deterministic-family':'DETERMINISTIC_FAMILY.md', 'compact-model-audit':'COMPACT_MODEL_AUDIT.md'}
TAG_PREFIXES = {'exact-six':'S','composition':'C','families':'F','obstruction':'O',
    'quantitative-transfer':'Q','effective-margin':'M','deterministic-family':'D',
    'compact-model-audit':'A','one-inductor':'R','singular-completion':'P','companion-guide':'G',
    'low-order-synthesis':'L','formal-graph-core':'V','typed-margins':'T','component-tolerances':'E'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_target(path, fragment=''):
    if path in ALIASES:
        anchor = ALIASES[path]
        return PAGE,anchor+('--'+fragment if fragment and anchor!='current-results' else '')
    return path,fragment


def namespace(content, slug):
    """Retain source mathematics; namespace anchors and explicit equation labels."""
    identifiers = set(re.findall(r'\bid="([^"]+)"',content))
    content = re.sub(r'\bid="([^"]+)"',lambda m:'id="'+slug+'--'+m[1]+'"',content)
    content = re.sub(r'href="#([^"]+)"',lambda m:'href="#'+slug+'--'+m[1]+'"' if unquote(m[1]) in identifiers else m[0],content)
    # A single book needs unique equation labels across formerly separate notes.
    content = re.sub(r'\\tag\{([^}]+)\}',lambda m:r'\tag{'+TAG_PREFIXES.get(slug,slug)+'.'+m[1]+'}',content)
    labels = set(re.findall(r'\\label\{([^}]+)\}',content))
    for label in labels:
        for command in ('label','ref','eqref'):
            content = content.replace('\\'+command+'{'+label+'}','\\'+command+'{'+slug+':'+label+'}')
    # The chapter's first heading is the public anchor, with subordinate levels below it.
    content = re.sub(r'<(/?)h([2-5])([^>]*)>',lambda m:
        '<'+m[1]+'h'+str(int(m[2])+1)+m[3]+'>',content)
    first = re.search(r'<h1\b[^>]*>(.*?)</h1>',content,re.S)
    if not first:
        raise ValueError('Missing source chapter title: '+slug)
    original_id = re.search(r'\bid="([^"]+)"',first[0])
    alias = '<span id="'+original_id[1]+'"></span>' if original_id else ''
    content = content[:first.start()]+alias+'<h2 id="'+slug+'">'+first[1]+'</h2>'+content[first.end():]
    return content


def source_markdown(site, path, slug, append_paths=()):
    from build_reader_site import Rewriter
    from smith_chart_continuation import render
    text = (site.root/path).read_text(encoding='utf-8')
    for extra in append_paths:
        addition = (site.root/extra).read_text(encoding='utf-8')
        text += '\n\n' + re.sub(r'^# ', '## ', addition, count=1)
    rewrite = Rewriter(lambda target,image:site.resolve('collection',path,PAGE,target,image))
    rewrite.feed(render(text))
    content = re.sub(r'<p>(?:<strong>)?Author:.*?</p>','', ''.join(rewrite.out),count=1,flags=re.S)
    return namespace(content,slug)


def chapter(site, manifest, files, entry):
    from smith_chart_continuation import chapter_body
    value = chapter_body(site,manifest,files,entry)
    value = value.split('<article class="manuscript">',1)[1].split('</article>',1)[0]
    value = re.sub(r'<aside class="research-update".*?</aside>','',value,flags=re.S)
    value = re.sub(r'<nav\b.*?</nav>','',value,flags=re.S)
    value = re.sub(r'<details class="page-contents">.*?</details>','',value,flags=re.S)
    # Chapter resources are consolidated once in the source ledger below.
    value = re.sub(r'<p>(?:<strong>)?Author:.*?</p>','',value,count=1,flags=re.S)
    if entry['slug']=='quantitative-transfer':
        before = 'That base margin has NOT been computed here. Any routine accepting a numerical value for it treats that value as an external premise. Test values are hypothetical arithmetic inputs, not certified Hughes margins.'
        after = 'This chapter proves finite transfer for any valid base margin. The effective-margin section supplies the explicit written bound, and the following audit checks its reduction and external theorem hypotheses. Hypothetical test values remain distinct from that proof.'
        if value.count(before)!=1:
            raise ValueError('Quantitative status reconciliation source changed')
        value = value.replace(before,after)
        value = value.replace('Its numerical value remains uncomputed.',
            'The effective-margin section supplies its explicit written value.')
        value = value.replace('It is not evidence that a numerical value for Delta_H has been computed.',
            'The effective-margin section supplies that value by a written theorem application; arithmetic tests alone do not prove it.')
        value = value.replace('The new hard computational obligation is a positive rational Delta_H together with an independently replayable all-topology seven-sample separation proof',
            'An explicit written Delta_H is now supplied. A compact independently replayable all-topology seven-sample separation proof remains a computational obligation')
    value = re.sub(r'<p><a href="[^"]+">Open the circuit diagram at full size</a></p>','',value)
    value = namespace(value,entry['slug'])
    return '<section class="book-chapter" data-source-chapter="'+entry['slug']+'">'+value+'</section>'


def local_routes(content):
    """Point current reading links directly into the canonical article."""
    def link(match):
        value = html.unescape(match[1])
        parts = urlsplit(value)
        if parts.scheme and not (parts.netloc.lower()=='komorebip.github.io' and parts.path.startswith('/Operation-KOMOREBI/')):
            return match[0]
        target = unquote(parts.path)
        if parts.scheme:
            target = target[len('/Operation-KOMOREBI/'):]
        elif target:
            target = posixpath.normpath(posixpath.join(posixpath.dirname(PAGE),target))
        else:
            return match[0]
        if target in ALIASES:
            slug = ALIASES[target]
            fragment = slug + ('--'+parts.fragment if parts.fragment and slug!='current-results' else '')
            return 'href="#'+fragment+'"'
        if target==PAGE:
            return 'href="#'+(parts.fragment or 'current-results')+'"'
        return match[0]
    return re.sub(r'href="([^"]+)"',link,content)


def diagrams(content, site):
    def figure(match):
        attrs = match[1]
        src = re.search(r'src="([^"]+)"',attrs)[1]
        alt = re.search(r'alt="([^"]*)"',attrs)
        label = ('Certified six-reactive circuit' if '/figures/topology.' in src else
                 'One-inductor circuit' if 'smith-first-order-rl.svg' in src else
                 'Two-packet feasibility boundary' if 'smith-two-packet-feasibility.svg' in src else 'Mathematical diagram')
        if src.endswith('/figures/topology.png'):
            src = src[:-4]+'.svg'
            attrs = re.sub(r'src="[^"]+"','src="'+src+'"',attrs)
        picture = '<img'+attrs+'>'
        responsive = next((name for name in ('stable-energy','balanced-resonance') if src.endswith('/figures/'+name+'.svg')),None)
        if responsive:
            mobile = site.resolve('collection',BASE+'/README.md',PAGE,'figures/'+responsive+'.mobile.svg',True)
            picture = '<picture><source media="(max-width: 600px)" srcset="'+mobile+'">'+picture+'</picture>'
        return ('<figure class="research-figure book-figure"><div class="figure-heading"><span>'+label+'</span>'
            '<a href="'+src+'">Source diagram</a></div>'+picture+'<div class="figure-actions">'
            '<button class="figure-open" type="button">Open diagram</button></div>'
            '<figcaption>'+ (alt[1] if alt else label)+'</figcaption></figure>')
    return re.sub(r'<p>\s*<img([^>]+)>\s*</p>',figure,content)


def build(site):
    from smith_chart_research import historical_body
    from smith_chart_continuation import load, render
    manifest,files = load(site.root)
    body = historical_body(site.root,site.revision)
    match = re.search(r'(<article class="manuscript" id="manuscript">)(.*?)(</article>)',body,re.S)
    if not match:
        raise ValueError('Missing historical article boundary')
    original = match[2]
    positions = list(re.finditer(r'<h2 id="([^"]+)">.*?</h2>',original,re.S))
    sections = {p[1]:original[p.start():positions[i+1].start() if i+1<len(positions) else len(original)] for i,p in enumerate(positions)}
    history_ids = {'current-result','exactly-six-reactive-elements-with-an-ideal-reciprocal-combiner',
        'transformer-free-synthesis-a-precise-decision-theorem-and-a-topology-obstruction','six-state-invariants',
        'pole-pair-extraction','second-pole-pair-extraction','four-anchor-continuation','certified-cubic-extraction',
        'seven-reactive-exact','verification-register-and-reproducible-records','what-has-been-settled-and-what-remains-open',
        'sources-and-provenance','suggested-reading-routes'}
    current = render((site.root/BASE/'OVERVIEW.md').read_text(encoding='utf-8'))
    current = re.sub(r'<table>.*?</table>',lambda m:
        '<div class="table-wrap" tabindex="0" role="region" aria-label="Scrollable current-results table">'+m[0]+'</div>',current,flags=re.S)
    current = current.replace('<h1 id="current-results-and-reading-route">','<h2 id="current-results">',1).replace('</h1>','</h2>',1)
    current = '<span id="current-result"></span>'+current
    assembled = [current]
    for identifier in [p[1] for p in positions if p[1] not in history_ids]:
        assembled.append(sections[identifier])
        if identifier=='passive-completion-from-incomplete-packets':
            assembled.append(source_markdown(site,'docs/demonstrations/SMITH_SINGULAR_COMPLETION.md','singular-completion'))
        if identifier=='exact-order-proliferation-under-cyclic-filtering':
            for slug in ('exact-six','composition'):
                assembled.append(chapter(site,manifest,files,next(c for c in manifest['chapters'] if c['slug']==slug)))
            assembled.append(source_markdown(site,BASE+'/LOW_ORDER_SYNTHESIS.md','low-order-synthesis'))
            assembled.append(chapter(site,manifest,files,next(c for c in manifest['chapters'] if c['slug']=='families')))
            assembled.append(source_markdown(site,BASE+'/DETERMINISTIC_FAMILY.md','deterministic-family'))
            for slug in ('obstruction','quantitative-transfer','effective-margin'):
                assembled.append(chapter(site,manifest,files,next(c for c in manifest['chapters'] if c['slug']==slug)))
            assembled.append(source_markdown(site,BASE+'/COMPACT_MODEL_AUDIT.md','compact-model-audit'))
            assembled.append(source_markdown(site,BASE+'/FORMAL_CORE.md','formal-graph-core',
                (BASE+'/FORMAL_PROGRESS.md',)))
            typed = source_markdown(site,BASE+'/BALANCED_RESONANCE.md','typed-margins',
                (BASE+'/GLOBAL_TYPED_MARGINS.md',BASE+'/STABLE_ENERGY.md',BASE+'/TYPED_MARGINS.md',BASE+'/TWO_REACTIVE_MARGIN.md',BASE+'/COEFFICIENT_ROUTES.md'))
            marker = '<h3 id="typed-margins--usable-pure-type-margins-and-a-smaller-mixed-search">'
            if typed.count(marker)!=1:
                raise ValueError('Missing retained typed-margin checkpoint anchor')
            split = typed.index(marker)
            typed = typed[:split]+'<details class="book-history"><summary>Earlier margin checkpoints and derivations</summary><p>The following status counts describe their original checkpoints. The current whole one-kind margins and 796 remaining balanced placements are stated above.</p>'+typed[split:]+'</details>'
            assembled.append(typed)
            assembled.append(source_markdown(site,BASE+'/TOLERANCE.md','component-tolerances',
                (BASE+'/MIXED_LOSS_TOLERANCE.md',)))
        if identifier=='arbitrary-order-separation':
            assembled.append(source_markdown(site,'docs/demonstrations/SMITH_FIRST_ORDER_RL.md','one-inductor'))
    reference = source_markdown(site,'docs/demonstrations/SMITH_CHART.md','companion-guide')
    assembled.append('<h2 id="laboratory-reference">Laboratory reference and selected Lean statements</h2>'
        '<details class="book-reference"><summary>Open the complete companion reference</summary>'+reference+'</details>')
    old = ''.join(sections[p[1]] for p in positions if p[1] in history_ids)
    old = old.replace('id="current-result"','id="historical-current-result"',1)
    old = re.sub(r'<aside class="research-update" data-edition-addition="exact-six-closure">.*?</aside>','',old,flags=re.S)
    assembled.append('<h2 id="historical-synthesis">Research history and superseded checkpoints</h2>'
        '<details class="book-history"><summary>Open the historical constructions, searches and status registers</summary>'
        '<p class="book-history-notice">These are the retained earlier checkpoints. Their six-versus-seven '
        'questions and earlier status tables describe that stage of the work. The current exact minimum '
        'for the original target is six, proved by the later eight-node witness above.</p>'+old+'</details>')
    assembled.append('<h2 id="source-ledger">Sources, checks and remaining work</h2>'
        '<p>The current written arguments have project self-review, and forty-one selected finite-graph, '
        'elimination, loss and shape statements have kernel replay. Complete formal compactification and transfer, independent peer review, '
        'a useful margin for the remaining mixed RLC models, arbitrary-target practical minimum synthesis, '
        'higher-target resistor minima, broader parasitic models and physical measurements remain open. '
        'The two-reactive separator, two series margins and dedicated-series-loss tolerance theorem close explicit subclasses. '
        'Physical graph and endpoint arguments now exclude every three-reactive mixed class and the '
        'four-reactive one-L/one-C classes with explicit tiny margins. Coverage is 1,334 of 2,130; '
        'the 796 balanced two-L/two-C placements remain. The exact internal-mode stratum and a certified '
        'detuning/opening-budget neighborhood are now separated too; a uniform near-mode transfer and '
        'regular balanced separator remain. All new comparisons use positive-real Laplace samples.</p>'
        '<p><a href="../../downloads/smith-rlc-current-source.zip">Download the complete current source and checks</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/tree/'+site.revision+'/'+BASE+'">'
        'Proof, computation and source-binding records</a>. The original checkpoint ZIPs and earlier Lean receipts '
        'are retained unchanged in that source package.</p>')
    article = local_routes(diagrams(''.join(assembled),site))
    article = article.replace('This note does not resolve the transformer-free six-reactive-element question.',
        'This auxiliary circuit is separate from the exact six-reactive closure in this reading.')
    body = body[:match.start(2)]+article+body[match.end(2):]
    cover = ('<section class="cover"><p class="kicker">Komorebi P. · Research reading</p>'
        '<h1 id="smith-chart-through-exact-packets-passivity-and-reconstruction">'+TITLE+'</h1>'
        '<p class="subtitle">Exact packets, passive completion, physical circuits and their verification.</p>'
        '<p class="author-line">Komorebi P. · Updated 12 November 2026</p>'
        '<nav class="quick-nav" aria-label="Start reading"><a href="#current-results">Current results</a>'
        '<a href="#exact-six">Exact-six circuit</a><a href="#low-order-synthesis">Certified synthesis</a>'
        '<a href="#formal-graph-core">Formal assurance</a></nav></section>')
    body = re.sub(r'<section class="cover">.*?</section>',lambda m:cover,body,count=1,flags=re.S)
    body = re.sub(r'<aside class="research-notice".*?</aside>',
        '<aside class="research-notice"><p><strong>Exact circuits and explicit limits.</strong> '
        'The original degree-six target has reactive minimum six. Exact construction now covers first-order '
        'targets, the RC/RL classes and specified higher-degree families. Selected graph and margin lemmas '
        'have Lean proofs; the complete universal proof chain and general mixed-RLC solver remain open.</p>'
        '<nav class="research-actions" aria-label="Reading resources"><a class="research-download" '
        'href="../../downloads/smith-rlc-current-source.zip">Download current source<span>Proofs, certificates and checks</span></a>'
        '<a href="../../smith-chart.html">Open the laboratory</a>'
        '<span class="research-print"><button type="button" id="print-reading">Print reading</button></span></nav></aside>',body,count=1,flags=re.S)
    links = re.findall(r'<h2\b[^>]*id="([^"]+)"[^>]*>(.*?)</h2>',article,re.S)
    toc = ('<details id="contents" class="contents" open><summary>Contents</summary><p class="contents-title">'
        'Smith chart and RLC synthesis</p><div class="toc-links">'+''.join('<a href="#'+identifier+'">'+
        re.sub('<[^>]+>','',title)+'</a>' for identifier,title in links)+'</div><div class="toc-progress">'
        'Reading progress<progress id="reading-progress" max="100" value="0" aria-label="Reading progress"></progress></div></details>')
    contents = re.search(r'<details\b[^>]*\bid="contents"[^>]*>',body)
    if not contents:
        raise ValueError('Missing consolidated contents boundary')
    start = contents.start()
    end = body.index('<article class="manuscript"',start)
    body = body[:start]+toc+body[end:]
    body = re.sub(r'<footer class="end-note">.*?</footer>',
        '<footer class="end-note">Komorebi P. · Current proofs and historical sources are distinguished '
        'in the reading. Analytic tolerance bounds concern the stated ideal models; physical validation '
        'and historical priority remain separate.</footer>',body,flags=re.S)
    return body


def publish_redirect(site, page, anchor):
    target = site.rel(PAGE,page)+'#'+anchor
    script = site.rel('assets/smith-book-redirect.js',page)
    body = ('<h1>Smith chart research reading</h1><p>This material is part of the consolidated reading.</p>'
        '<p><a id="smith-book-destination" href="'+target+'">Continue to this section in the complete reading</a></p>'
        '<script defer src="'+script+'" data-book-target="'+target+'" data-book-prefix="'+anchor+'"></script>')
    site.page(page,'Smith chart research reading',body)
    file = site.output/page
    value = file.read_text(encoding='utf-8').replace('</head>',
        '<noscript><meta http-equiv="refresh" content="0;url='+target+'"></noscript></head>',1)
    file.write_text(value,encoding='utf-8',newline='\n')


def publish_sources(site):
    """One downloadable current source package; full literature PDFs stay local."""
    source_files = []
    for directory in (site.root/BASE,site.root/'research/smith-chart/continuation',
                      site.root/'research/smith-chart/formal',site.root/'research/smith-chart/completion-formal',
                      site.root/'research/smith-chart/computations',site.root/'research/smith-chart/edition',
                      site.root/'formal/smith-chart-v0.1.0'):
        source_files += [p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    source_files += [site.root/'research/smith-chart/SmithChart_Complete.zip']
    source_files += [site.root/'docs/demonstrations'/ (name+'.md') for name in ('SMITH_CHART','SMITH_FIRST_ORDER_RL','SMITH_SINGULAR_COMPLETION')]
    source_files += [site.root/'docs/demonstrations/figures'/name for name in ('smith-first-order-rl.svg','smith-two-packet-feasibility.svg')]
    source_files += [site.root/'tools'/name for name in ('smith_chart_unified.py','smith_chart_continuation.py','smith_chart_research.py')]
    target = site.output/'downloads/smith-rlc-current-source.zip'
    target.parent.mkdir(parents=True,exist_ok=True)
    hashes = {}
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        def put(name,raw):
            info = zipfile.ZipInfo(name,date_time=(2026,11,12,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644<<16
            archive.writestr(info,raw)
            hashes[name] = sha(raw)
        for path in sorted(set(source_files)):
            name = path.relative_to(site.root).as_posix()
            raw = path.read_bytes()
            put(name,raw)
        put('replay.py',b'from pathlib import Path\nimport runpy\nrunpy.run_path(str(Path(__file__).resolve().parent/"research/smith-chart/unified/replay_current.py"), run_name="__main__")\n')
        put('START_HERE.md',b'# Smith / RLC current source\n\nAuthor: Komorebi P.\n\nRun `python -B replay.py` from this directory. Read `research/smith-chart/unified/README.md` for scope and individual commands. The package preserves repository-relative source paths. Full third-party PDFs and toolchain runtimes are not bundled.\n')
        info = zipfile.ZipInfo('SOURCE_HASHES.json',date_time=(2026,11,12,0,0,0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644<<16
        archive.writestr(info,json.dumps(hashes,indent=2)+'\n')
    site.write('documents/smith-rlc/current-source.json',json.dumps({'revision':site.revision,
        'archive':'downloads/smith-rlc-current-source.zip','sha256':sha(target.read_bytes()),
        'files':len(hashes),'scope':'Authored source and retained evidence; no third-party full-text PDFs'},indent=2)+'\n')
