"""Browse retained Lean sources for works with an existing HTML reading edition.

Declaration lists are lexical navigation aids, never compiler or coverage results.
Source bytes and ownership still pass through ReadingDocuments and its receipts.
"""
import hashlib
import html
import json
from pathlib import PurePosixPath
import posixpath
import re


EXCLUDED = {'.lake', '.git', 'build', 'node_modules', '__pycache__'}
DECLARATION = re.compile(
    r'^\s*(?:@\[(?:[^\[\]]|\[[^\[\]]*\])*\]\s*)*'
    r'(?:(?:private|protected|noncomputable|unsafe|partial)\s+)*'
    r'(theorem|lemma|def|abbrev|structure|class|inductive|axiom|constant|instance)'
    r'\s+(«[^»\n]+»|[\w\u0080-\uffff][\w\u0080-\uffff.\'!?]*)', re.M)
KEYWORDS = set(('import namespace section end open export variable variables universe universes '
                'structure class inductive coinductive def abbrev theorem lemma example axiom constant '
                'instance where by fun let have show from match with if then else do return '
                'noncomputable private protected unsafe partial mutual deriving forall exists '
                'in include omit set_option attribute syntax macro macro_rules elab scoped local '
                'infix infixl infixr prefix postfix notation termination_by decreasing_by').split())
TACTICS = set(('simp simpa rw rfl exact apply intro intros constructor cases rcases obtain '
              'induction ext refine specialize calc assumption trivial decide norm_num aesop '
              'change convert unfold dsimp congr omega linarith nlinarith ring field_simp '
              'subst revert generalize first all_goals any_goals repeat try done').split())
WORD = re.compile(r'[\w][\w.\'!?]*')
CHARACTER = re.compile(r"'(?:\\(?:u\{[0-9a-fA-F]+\}|.)|[^'\\])'")


def directory(work):
    return 'lean/'+work+'/index.html'


def quantity(count, label):
    return str(count)+' '+label+('' if count == 1 else 's')


def short_title(title):
    return re.sub(r'^Paper [IVX]+:\s*', '', title)


def source_root(reader, work):
    paths = [posixpath.dirname(r['repository_path']) for r in reader.lean_works[work]]
    return posixpath.commonpath(paths)+'/'


def paired_route(site, page):
    from urllib.parse import quote
    return '<a data-side-reader-link href="'+site.rel('side-by-side.html',page)+'?left='+quote(page,safe='')+'">Read side by side</a>'


def source_heading(reader, record, page):
    from readable_chapters import BOOKS
    site, work, e = reader.site, record['work'], html.escape
    book = BOOKS[work]
    name = PurePosixPath(record['repository_path']).name
    return ('<nav class="breadcrumbs" aria-label="Document navigation"><a href="'+site.rel('collection/works/'+work+'.html',page)+'">'+
            e(book['label'])+'</a><span aria-hidden="true">/</span><a href="'+site.rel(directory(work),page)+'">Lean files</a></nav>'
            '<header class="document-heading lean-source-heading"><p class="eyebrow">'+e(book['label'])+' · Lean source</p>'
            '<h1>'+e(name)+'</h1></header>')


def selected_paths(component, owned):
    """Expand only explicit Lean selections inside their receipt-owned component."""
    from build_reader_site import safe_path
    prefix = safe_path(component['destination'])+'/'
    selections = [safe_path(r['path'].rstrip('/'))+('/' if r['path'].endswith('/') else '')
                  for r in component['resources'] if r['kind'] == 'lean']
    for path, record in sorted(owned.items()):
        if record['work'] != component['id'] or not path.startswith(prefix):
            continue
        relative = safe_path(path[len(prefix):])
        if (not relative.endswith('.lean') or PurePosixPath(relative).name == 'lakefile.lean'
                or EXCLUDED.intersection(PurePosixPath(relative).parts)):
            continue
        if any(relative == p or p.endswith('/') and relative.startswith(p) for p in selections):
            yield path


def prepare(reader):
    from readable_chapters import BOOKS
    reader.lean_works = {}
    for component in reader.site.registry['components']:
        work = component['id']
        if work not in BOOKS:
            continue
        records = [reader.add(path) for path in selected_paths(component, reader.owned)]
        records = [r for r in records if r]
        if records:
            reader.lean_works[work] = records


def declarations(text):
    """Ignore nested comments and string contents while preserving line positions."""
    clean = list(text)
    index, depth, string = 0, 0, False
    while index < len(text):
        pair = text[index:index+2]
        if depth:
            count = 2 if pair in {'/-', '-/'} else 1
            if pair == '/-': depth += 1
            elif pair == '-/': depth -= 1
        elif string:
            count = 2 if text[index] == '\\' and index+1 < len(text) else 1
            if text[index] == '"': string = False
        elif pair == '/-':
            depth, count = 1, 2
        elif pair == '--':
            end = text.find('\n', index)
            count = (len(text) if end < 0 else end)-index
        elif text[index] == '"':
            string, count = True, 1
        else:
            index += 1
            continue
        for pos in range(index, min(index+count, len(text))):
            if text[pos] != '\n': clean[pos] = ' '
        index += count
    masked = ''.join(clean)
    result = []
    for match in DECLARATION.finditer(masked):
        # Whitespace may include newlines before the actual declaration keyword.
        line = masked.count('\n', 0, match.start(1))+1
        if match[2] not in {'where', 'of', 'deriving'}:
            result.append(dict(kind=match[1], name=match[2], line=line))
    return result


def highlight_lines(text):
    """Color lexical tokens, preserving each original line as escaped HTML."""
    result, depth, string = [], 0, False
    for line in text.splitlines():
        pieces, index = [], 0
        while index < len(line):
            start, kind = index, None
            if depth or line.startswith('/-',index):
                kind = 'comment'
                if not depth: depth, index = 1, index+2
                while index < len(line) and depth:
                    pair = line[index:index+2]
                    if pair == '/-': depth, index = depth+1, index+2
                    elif pair == '-/': depth, index = depth-1, index+2
                    else: index += 1
            elif string or line[index] == '"':
                kind = 'string'
                if not string: string, index = True, index+1
                while index < len(line):
                    if line[index] == '\\': index = min(index+2,len(line))
                    elif line[index] == '"':
                        string, index = False, index+1
                        break
                    else: index += 1
            elif line.startswith('--',index):
                kind, index = 'comment', len(line)
            elif line[index] == '«' and '»' in line[index+1:]:
                index = line.index('»',index+1)+1
            elif (match := CHARACTER.match(line,index)):
                kind, index = 'string', match.end()
            elif (match := WORD.match(line,index)):
                word, index = match[0], match.end()
                kind = ('keyword' if word in KEYWORDS else 'tactic' if word in TACTICS else
                        'number' if re.fullmatch(r'\d+(?:\.\d+)?',word) else None)
            else:
                index += 1
            escaped = html.escape(line[start:index])
            pieces.append('<span class="lean-token-'+kind+'">'+escaped+'</span>' if kind else escaped)
        result.append(''.join(pieces))
    return result


def declaration_outline(entries):
    if not entries: return ''
    e = html.escape
    body = ('<aside class="lean-outline" aria-label="Declarations in this source file">'
            '<details class="lean-declarations" data-lean-outline><summary>Declarations in this file <span>'+str(len(entries))+
            '</span></summary><form class="lean-outline-filter" role="search" hidden>'
            '<label for="lean-declaration-query">Find a declaration</label><div>'
            '<input id="lean-declaration-query" type="search" autocomplete="off" placeholder="Name or kind…">'
            '<button type="reset">Clear</button></div></form>'
            '<p class="lean-declaration-count" role="status" aria-live="polite">'+quantity(len(entries),'declaration')+'</p><ul>')
    body += ''.join('<li data-lean-declaration="'+e(d['kind']+' '+d['name'],quote=True)+'"><a href="#L'+str(d['line'])+'" aria-label="'+e(d['kind']+' '+d['name']+', line '+str(d['line']),quote=True)+'">'
                    '<span class="lean-declaration-kind">'+e(d['kind'])+'</span><code>'+e(d['name'])+'</code>'
                    '<span class="lean-declaration-line">L'+str(d['line'])+'</span></a></li>' for d in entries)
    return body+'</ul><p class="lean-outline-note">Names from source text, not a compiler report. Anonymous and generated declarations may be omitted.</p></details></aside>'


def code_view(text, annotations=None):
    from reader_documents import source_lines
    entries = declarations(text)
    body = '<div class="lean-code-layout'+(' has-lean-outline' if entries else '')+'">'
    if entries: body += '<a class="lean-code-skip" href="#source-navigation">Skip declarations and read code</a>'
    body += declaration_outline(entries)
    return body+'<div class="lean-code-panel">'+source_lines(text,annotations,rendered_lines=highlight_lines(text))+'</div></div>'


def assets(site, page):
    result = ''
    for name in ('lean-reader.css', 'lean-reader.js'):
        version = hashlib.sha256((site.root/'website/assets'/name).read_bytes()).hexdigest()[:12]
        url = site.rel('assets/'+name, page)+'?v='+version
        result += ('<link rel="stylesheet" href="'+url+'">' if name.endswith('.css')
                   else '<script defer src="'+url+'"></script>')
    return result


def scope(reader, work, page):
    assessment = reader.site.assessments[work]
    label, description = reader.site.status['labels']['lean'][assessment['lean']]
    e = html.escape
    coverage = reader.site.rel('collection/works/'+work+'.html', page)+'#lean'
    evidence = reader.site.rel('collection/works/'+work+'.html', page)+'#evidence'
    return ('<details class="lean-scope"><summary><span class="lean-badge">'+e(label)+
            '</span> <span class="lean-scope-label">Coverage and evidence</span></summary><div><p>'+e(description)+
            '</p><p>This viewer reads the retained source; it does not run Lean or assign new claim mappings.</p>'
            '<nav aria-label="Recorded Lean evidence"><a href="'+coverage+'">Coverage and setup</a>'
            '<a href="'+evidence+'">Recorded evidence</a></nav></div></details>')


def source_controls(reader, record, text, page):
    work = record['work']
    if work not in getattr(reader,'lean_works',{}):
        return ''
    e = html.escape
    site = reader.site
    body = assets(site, page)
    relative = record['repository_path'].removeprefix(reader.site.components[work]['destination']+'/')
    from readable_chapters import BOOKS
    from urllib.parse import quote
    body += '<nav class="lean-actions" aria-label="Lean source actions"><a href="'+site.rel(BOOKS[work]['index'],page)+'">Read the paper</a>'
    body += '<a href="'+quote(site.rel(record['file_url'],page),safe='/')+'" download>Download source</a>'+paired_route(site,page)+'</nav>'
    from browser_lean import action
    body += action(site,page,source=record['repository_path'])
    body += scope(reader, work, page)
    module = record['repository_path'].removeprefix(source_root(reader,work))
    body += '<p class="lean-current-path"><code>'+e(module)+'</code><span>'+quantity(len(text.splitlines()),'line')+'</span></p>'
    body += '<details class="lean-source-location"><summary>Original source path</summary><code>'+e(relative)+'</code></details>'
    return body


def build(reader):
    from readable_chapters import BOOKS
    site, e = reader.site, html.escape
    catalog, total = [], 0
    for work, records in reader.lean_works.items():
        page = directory(work)
        title = site.components[work]['title']
        book = BOOKS[work]
        body = assets(site, page)+'<section class="lean-browser"><nav class="breadcrumbs" aria-label="Lean navigation"><a href="'+site.rel('lean/index.html',page)+'">All Lean sources</a></nav>'
        body += '<header class="lean-heading"><p class="eyebrow">'+e(book['label'])+' · Lean sources</p><h1>'+e(short_title(title))+'</h1></header>'
        body += '<nav class="lean-actions" aria-label="Lean reading routes"><a class="button" href="'+site.rel(book['index'],page)+'">Read the paper</a>'
        body += '<a href="'+site.rel('collection/works/'+work+'.html',page)+'">Work overview</a>'+paired_route(site,page)+'</nav>'+scope(reader,work,page)
        from browser_lean import action
        body += action(site,page,work=work)
        common = source_root(reader,work)
        root_label = common.removeprefix(site.components[work]['destination']+'/') or './'
        body += ('<div class="lean-directory-heading"><h2>Source files <span>'+str(len(records))+'</span></h2>'
                 '<details class="lean-source-location"><summary>Source locations and editions</summary>'
                 '<p>Files are shown relative to <code>'+e(root_label)+'</code>.</p>'
                 '<p>Historical editions keep their original paths. Package caches and build files are omitted.</p></details></div>'
                 '<form class="lean-filter" role="search" hidden><label for="lean-query">Find a file or declaration</label><div>'
                 '<input id="lean-query" name="q" type="search" autocomplete="off" placeholder="File path, theorem, definition…">'
                 '<button type="reset">Clear</button></div></form><p class="lean-count" role="status" aria-live="polite">'+
                 quantity(len(records),'file')+'</p><ul class="lean-files">')
        file_entries = []
        prefix = site.components[work]['destination']+'/'
        for record in records:
            path = record['repository_path']
            raw = site.read_source(record)
            entries = declarations(raw.decode('utf-8-sig'))
            relative = path.removeprefix(prefix)
            module = path.removeprefix(common)
            folder = posixpath.dirname(module)
            search = relative+' '+' '.join(d['kind']+' '+d['name'] for d in entries)
            body += '<li data-lean-search="'+e(search,quote=True)+'"><div class="lean-file-name"><a href="'+site.rel(record['url'],page)+'" aria-label="'+e(module,quote=True)+'"><code>'+e(PurePosixPath(path).name)+'</code></a>'
            if folder: body += '<span class="lean-file-folder">'+e(folder)+'/</span>'
            body += '</div><span class="lean-file-meta">'+quantity(len(raw.splitlines()),'line')+' · '+quantity(len(entries),'declaration location')+'</span></li>'
            file_entries.append(dict(path=path,url=record['url'],sha256=record['sha256'],declarations=entries))
        body += '</ul><noscript><p>The complete file list works without JavaScript. Use your browser’s Find command to search file paths.</p></noscript></section>'
        site.page(page,title+' / Inspect Lean',body)
        site.search.append(dict(title=title+' / Inspect Lean',group='Collection',kind='Lean',work_ids=[work],url=page,
                                text='Lean source inspector files declarations theorem definition '+title))
        catalog.append(dict(work=work,url=page,files=file_entries))
        total += len(records)
    body = assets(site,'lean/index.html')+'<section class="lean-browser"><header class="lean-heading"><p class="eyebrow">The formal source</p><h1>Inspect Lean</h1>'
    body += '<p class="lean-lede">Read the code behind the papers. Find a file, explore its declarations, and link directly to the source.</p>'
    body += '<p class="lean-summary">'+quantity(len(catalog),'reading edition')+'<span aria-hidden="true"> · </span>'+quantity(total,'source file')+'</p></header>'
    body += '<nav class="lean-actions" aria-label="Lean library routes"><a href="'+site.rel('read/index.html','lean/index.html')+'">Reading library</a>'+paired_route(site,'lean/index.html')+'</nav>'
    body += '<p class="lean-library-note">Coverage labels describe the existing evidence. Browsing the source does not run Lean.</p>'
    body += '<p class="lean-playground-route"><a class="button" href="'+site.rel('lean/playground.html','lean/index.html')+'">Try a proof in Lean</a> <span>Interactive pilot · Paper XII</span></p>'
    for group,core in [('Core papers',True),('Books and monographs',False)]:
        selected = [item for item in catalog if bool(re.fullmatch(r'paper-[ivx]+',item['work'])) == core]
        if not selected: continue
        body += '<section class="lean-work-group"><h2>'+group+'</h2><ul class="lean-works">'
        for item in selected:
            work = item['work']
            label = site.status['labels']['lean'][site.assessments[work]['lean']][0]
            title = site.components[work]['title']
            book_label = BOOKS[work]['label']
            body += '<li><div><p class="lean-work-label">'+e(book_label)+'</p><a href="'+site.rel(item['url'],'lean/index.html')+'">'+e(short_title(title))+'</a><span class="lean-work-coverage">'+e(label)+'</span></div>'
            body += '<span class="lean-work-count">'+quantity(len(item['files']),'file')+'</span></li>'
        body += '</ul></section>'
    body += '</section>'
    site.page('lean/index.html','Inspect Lean',body)
    site.write('lean/index.json',json.dumps(dict(source_revision=site.revision,works=catalog,new_lean_execution=False),ensure_ascii=False,indent=2)+'\n')
    return dict(works=len(catalog),files=total,new_lean_execution=False)


def verify(root, documents):
    """Check publication coverage, declaration locations and original source identities."""
    from html.parser import HTMLParser
    class SourceText(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.source = False
            self.spans = []
            self.lines = []
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'pre' and 'source-lines' in attrs.get('class','').split(): self.source = True
            if self.source and tag == 'span':
                self.spans.append('source-claim-links' in attrs.get('class','').split())
                if 'source-line' in attrs.get('class','').split(): self.lines.append('')
            if self.source and tag == 'a': self.spans.append('line-number' in attrs.get('class','').split())
        def handle_endtag(self, tag):
            if self.source and tag in {'span','a'} and self.spans: self.spans.pop()
            if tag == 'pre': self.source = False
        def handle_data(self, data):
            if self.source and self.lines and not any(self.spans): self.lines[-1] += data
    catalog = json.loads((root/'lean/index.json').read_bytes())
    records = {r['repository_path']:r for r in documents['files']}
    assert len(catalog['works']) == len({w['work'] for w in catalog['works']})
    assert catalog['source_revision'] == documents.get('source_revision',catalog['source_revision'])
    count = 0
    for work in catalog['works']:
        assert len(work['files']) == len({f['path'] for f in work['files']})
        listing = (root/work['url']).read_text(encoding='utf-8')
        from build_reader_site import Site
        for entry in work['files']:
            record = records[entry['path']]
            assert record['work'] == work['work'] and entry['sha256'] == record['sha256']
            raw = (root/record['file_url']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == entry['sha256']
            text = raw.decode('utf-8-sig')
            assert declarations(text) == entry['declarations']
            markup = (root/entry['url']).read_text(encoding='utf-8')
            parser = SourceText(); parser.feed(markup)
            assert [line.removeprefix(' ').removesuffix('\n') for line in parser.lines] == text.splitlines(), entry['path']
            assert Site.rel(None,entry['url'],work['url']) in listing
            for d in entry['declarations']:
                assert 'id="L'+str(d['line'])+'"' in markup
            count += 1
    assert not catalog['new_lean_execution']
    return dict(works=len(catalog['works']),files=count,new_lean_execution=False)
