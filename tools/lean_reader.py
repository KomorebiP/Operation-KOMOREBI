"""Browse retained Lean sources for works with an existing HTML reading edition.

Declaration lists are lexical navigation aids, never compiler or coverage results.
Source bytes and ownership still pass through ReadingDocuments and its receipts.
"""
import hashlib
import html
import json
from pathlib import PurePosixPath
import re


EXCLUDED = {'.lake', '.git', 'build', 'node_modules', '__pycache__'}
DECLARATION = re.compile(
    r'^\s*(?:@\[(?:[^\[\]]|\[[^\[\]]*\])*\]\s*)*'
    r'(?:(?:private|protected|noncomputable|unsafe|partial)\s+)*'
    r'(theorem|lemma|def|abbrev|structure|class|inductive|axiom|constant|instance)'
    r'\s+(«[^»\n]+»|[\w\u0080-\uffff][\w\u0080-\uffff.\'!?]*)', re.M)


def directory(work):
    return 'lean/'+work+'/index.html'


def quantity(count, label):
    return str(count)+' '+label+('' if count == 1 else 's')


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
    return ('<aside class="lean-scope" aria-label="Recorded Lean coverage"><p><strong>'+e(label)+
            '</strong> · '+e(description)+'</p><p>Browse the retained source. This viewer does not '
            'compile Lean or establish a correspondence with every statement in the paper.</p>'
            '<p><a href="'+coverage+'">Coverage and setup</a> · <a href="'+evidence+'">Recorded evidence</a></p></aside>')


def source_controls(reader, record, text, page):
    work = record['work']
    if work not in getattr(reader,'lean_works',{}):
        return ''
    e = html.escape
    body = assets(reader.site, page)+scope(reader, work, page)
    relative = record['repository_path'].removeprefix(reader.site.components[work]['destination']+'/')
    body += '<p class="lean-current-path"><code>'+e(relative)+'</code></p>'
    body += '<p><a class="button" href="'+reader.site.rel(directory(work), page)+'">Browse this work’s Lean files</a></p>'
    entries = declarations(text)
    if entries:
        body += ('<details class="lean-declarations"><summary>'+quantity(len(entries),'declaration location')+
                 '</summary><p>Names found in the source text; this is not a compiler report. '
                 'Anonymous and generated declarations may be omitted.</p><ul>')
        body += ''.join('<li><a href="#L'+str(d['line'])+'"><code>'+e(d['kind']+' '+d['name'])+
                        '</code></a><span>Line '+str(d['line'])+'</span></li>' for d in entries)
        body += '</ul></details>'
    return body


def build(reader):
    site, e = reader.site, html.escape
    catalog, total = [], 0
    for work, records in reader.lean_works.items():
        page = directory(work)
        title = site.components[work]['title']
        body = assets(site, page)+'<p class="eyebrow">Lean source inspector</p><h1>'+e(title)+'</h1>'
        body += '<nav class="document-routes" aria-label="Lean reading routes"><a href="'+site.rel('lean/index.html',page)+'">All included works</a>'
        body += '<a href="'+site.rel('collection/works/'+work+'.html',page)+'">Work overview</a>'
        from readable_chapters import BOOKS
        body += '<a href="'+site.rel(BOOKS[work]['index'],page)+'">Read the paper</a></nav>'+scope(reader,work,page)
        body += ('<p>'+quantity(len(records),'file')+' from this work’s selected Lean source directories. '
                 'Historical editions retain their original paths. Package caches and build files are omitted.</p>'
                 '<form class="lean-filter" role="search" hidden><label for="lean-query">Find a file or declaration</label>'
                 '<input id="lean-query" name="q" type="search" autocomplete="off" placeholder="File path, theorem, definition…">'
                 '<button type="reset">Clear</button></form><p class="lean-count" role="status" aria-live="polite">'+
                 quantity(len(records),'file')+'</p><ul class="lean-files">')
        file_entries = []
        prefix = site.components[work]['destination']+'/'
        for record in records:
            path = record['repository_path']
            raw = site.read_source(record)
            entries = declarations(raw.decode('utf-8-sig'))
            relative = path.removeprefix(prefix)
            search = relative+' '+' '.join(d['kind']+' '+d['name'] for d in entries)
            body += '<li data-lean-search="'+e(search,quote=True)+'"><a href="'+site.rel(record['url'],page)+'"><code>'+e(relative)+'</code></a>'
            body += '<span>'+quantity(len(raw.splitlines()),'line')+' · '+quantity(len(entries),'declaration location')+'</span></li>'
            file_entries.append(dict(path=path,url=record['url'],sha256=record['sha256'],declarations=entries))
        body += '</ul><noscript><p>The complete file list works without JavaScript. Use your browser’s Find command to search file paths.</p></noscript>'
        site.page(page,title+' / Inspect Lean',body)
        site.search.append(dict(title=title+' / Inspect Lean',group='Collection',kind='Lean',work_ids=[work],url=page,
                                text='Lean source inspector files declarations theorem definition '+title))
        catalog.append(dict(work=work,url=page,files=file_entries))
        total += len(records)
    body = assets(site,'lean/index.html')+'<p class="eyebrow">Read the formal source</p><h1>Inspect Lean</h1>'
    body += ('<p>Explore the Lean sources accompanying the papers and books already available as HTML reading editions. '
             'Open a work, find a file or declaration, and follow a line link into the original source.</p>'
             '<p>Coverage labels come from the existing evidence records. Browsing does not run Lean or change a work’s verification status.</p><ul class="lean-works">')
    for item in catalog:
        work = item['work']
        label = site.status['labels']['lean'][site.assessments[work]['lean']][0]
        body += '<li><a href="'+site.rel(item['url'],'lean/index.html')+'">'+e(site.components[work]['title'])+'</a><span>'+quantity(len(item['files']),'file')+' · '+e(label)+'</span></li>'
    body += '</ul>'
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
