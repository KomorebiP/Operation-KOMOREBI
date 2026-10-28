"""Publish receipt-bound papers and source texts inside the reading site."""
import hashlib
import html
import json
from pathlib import PurePosixPath
import posixpath
import re
from urllib.parse import quote, unquote, urlsplit

TEXT_SUFFIXES = {'.md', '.tex', '.txt', '.json', '.lean', '.py', '.bib', '.c', '.h'}


def page_path(work, path):
    name = re.sub(r'[^a-z0-9]+', '-', PurePosixPath(path).stem.lower()).strip('-')[:70] or 'document'
    identity = hashlib.sha256(path.encode()).hexdigest()[:12]
    return 'read/'+work+'/'+name+'-'+identity+'.html'


def tex_includes(text, path, owned):
    """Resolve explicit local TeX inputs. Never execute TeX or expand macros."""
    result = []
    clean = re.sub(r'(?<!\\)%[^\n]*', '', text)
    for kind, names in re.findall(r'\\(input|include|bibliography|addbibresource)\s*(?:\[[^\]]*\])?\{([^{}]+)\}', clean):
        for name in names.split(','):
            name = name.strip()
            if not name or '\\' in name or '#' in name:
                continue
            suffix = '.bib' if kind in {'bibliography', 'addbibresource'} else '.tex'
            if not PurePosixPath(name).suffix:
                name += suffix
            candidate = posixpath.normpath(posixpath.join(posixpath.dirname(path), name))
            if candidate in owned:
                result.append(candidate)
    return sorted(set(result))


def source_lines(text):
    return '<pre class="source-lines" tabindex="0" aria-label="Source text with linked line numbers"><code>'+''.join(
        '<span class="source-line" id="L'+str(n)+'"><a class="line-number" href="#L'+str(n)+'" aria-label="Line '+str(n)+'">'+str(n)+'</a> '+html.escape(line)+'\n</span>'
        for n, line in enumerate(text.splitlines(), 1))+'</code></pre>'


class ReadingDocuments:
    def __init__(self, site):
        self.site = site
        self.owned = {}
        self.records = {}
        self.inclusions = {}
        self.images = {}
        for component in site.registry['components']:
            receipt = json.loads((site.root/('manifests/source-imports/'+component['id']+'.json')).read_bytes())
            for f in receipt['files']:
                path = component['destination']+'/'+f['path']
                self.owned[path] = {**f, 'repository_path': path, 'work': component['id']}
            for resource in component['resources']:
                self.add(component['destination']+'/'+resource['path'], resource['label'])
        for source in site.claims.get('sources', []):
            self.add(source['path'])
        for row in site.claims['records']:
            self.add(row['statement_path'])
            for declaration in row['lean']:
                if declaration['path']:
                    self.add(declaration['path'])

    def add(self, path, label=None):
        if path in self.records:
            return self.records[path]
        entry = self.owned.get(path)
        suffix = PurePosixPath(path).suffix.lower()
        if not entry or entry['mode'] not in {'100644', '100755'}:
            return None
        if suffix != '.pdf' and (suffix not in TEXT_SUFFIXES or entry['size'] > 3*1024*1024):
            return None
        work = entry['work']
        record = {**entry, 'title': label or PurePosixPath(path).name,
                  'format': 'pdf' if suffix == '.pdf' else ('markdown' if suffix == '.md' else 'source'),
                  'url': page_path(work, path),
                  'file_url': 'documents/files/'+entry['git_blob_sha1']+'/'+PurePosixPath(path).name}
        if record['format'] == 'markdown':
            record['source_url'] = record['url'][:-5]+'-source.html'
        self.records[path] = record
        return record

    def prepare(self):
        # Include manuscript sections and explicit source passages linked from maintained guides.
        from navigation_links import inline_targets
        for (repo, path), text in self.site.documents.items():
            if repo != 'collection':
                continue
            for target in inline_targets(text):
                parts = urlsplit(target)
                if not parts.scheme and not parts.netloc:
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(parts.path)))
                    self.add(resolved)
        done = set()
        while True:
            pending = [p for p in self.records if p not in done and p.endswith('.tex')]
            if not pending:
                break
            for path in pending:
                text = self.site.read_source(self.records[path]).decode('utf-8-sig')
                included = tex_includes(text, path, self.owned)
                self.inclusions[path] = included
                for child in included:
                    self.add(child)
                done.add(path)

    def primary_pdf(self, work):
        return next((r for r in self.records.values() if r['work'] == work and r['format'] == 'pdf' and r['title'] == 'Read PDF'), None)

    def image_url(self, path, page):
        entry = self.owned.get(path)
        if not entry or entry['mode'] not in {'100644', '100755'} or PurePosixPath(path).suffix.lower() not in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}:
            return None
        raw = self.site.read_source(entry)
        dest = 'assets/source/collection/'+path
        target = self.site.output/dest
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        self.images[path] = {**entry, 'file_url': dest}
        return quote(self.site.rel(dest, page), safe='/')

    def resolve(self, path, page, fragment=''):
        record = self.records.get(path)
        if not record:
            return None
        if record['format'] == 'pdf' and fragment:
            return self.viewer_url(record, page, fragment)
        target = record['url']
        line = re.fullmatch(r'(L\d+)(?:-L\d+)?', fragment)
        if line:
            target = record.get('source_url', target)
            fragment = line[1]
        return self.site.rel(target, page)+('#'+fragment if fragment else '')

    def viewer_url(self, record, page, fragment=''):
        from fetch_pdf_runtime import RUNTIME_ID
        viewer = 'assets/pdfjs/web/viewer.html'
        return (self.site.rel(viewer, page)+'?file='+quote(self.site.rel(record['file_url'], viewer), safe='')+
                '&work='+quote(self.site.rel('collection/works/'+record['work']+'.html', viewer), safe='')+
                '&v='+RUNTIME_ID+
                ('#'+fragment if fragment else ''))

    def work_intro(self, work, page):
        pdf = self.primary_pdf(work)
        if not pdf:
            return ''
        return '<aside class="document-shortcut"><a class="button" href="'+self.site.rel(pdf['url'], page)+'">Read the paper here</a> <a href="'+self.site.rel('documents.html', page)+'">Browse papers and PDFs</a></aside>'

    def render(self):
        from build_reader_site import Rewriter, github, math_fences, slugify
        import markdown
        e = html.escape
        for path, record in sorted(self.records.items()):
            raw = self.site.read_source(record)
            page = record['url']
            target = self.site.output/record['file_url']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            work = record['work']
            work_url = self.site.rel('collection/works/'+work+'.html', page)
            title = self.site.components[work]['title']
            file_url = quote(self.site.rel(record['file_url'], page), safe='/')
            body = '<nav class="breadcrumbs" aria-label="Document navigation"><a href="'+work_url+'">'+e(title)+'</a> / <a href="'+self.site.rel('documents.html', page)+'">Papers and PDFs</a></nav>'
            body += '<header class="document-heading"><p class="eyebrow">'+e(record['title'])+'</p><h1>'+e(title)+'</h1><p class="document-filename">'+e(PurePosixPath(path).name)+'</p></header>'
            body += '<nav class="document-routes" aria-label="Related work"><a href="'+work_url+'#read">Reading files</a><a href="'+work_url+'#written-proofs">Written proofs</a><a href="'+work_url+'#lean">Lean coverage</a><a href="'+work_url+'#code">Code</a><a href="'+work_url+'#evidence">Evidence</a>'
            overview = self.site.root/('docs/works/'+work+'.md')
            if 'id="worked-examples-for-this-work"' in overview.read_text(encoding='utf-8') or '### Worked examples for this work' in overview.read_text(encoding='utf-8'):
                body += '<a href="'+work_url+'#worked-examples-for-this-work">Worked examples</a>'
            if work in {w['id'] for w in self.site.claims.get('works', [])}:
                body += '<a href="'+self.site.rel('claims.html', page)+'#'+work+'">Claim index</a>'
            body += '</nav>'
            siblings = [r for r in self.records.values() if r['work'] == work and r['format'] == 'pdf' and r != record]
            if record['format'] == 'pdf':
                if not raw.startswith(b'%PDF-'):
                    raise ValueError('Invalid PDF signature: '+path)
                viewer_url = e(self.viewer_url(record, page), quote=True)
                body += '<div class="document-actions"><a class="button" href="'+viewer_url+'">Expand reader</a><a href="'+file_url+'">Open PDF directly</a><a href="'+file_url+'" download>Download PDF</a></div>'
                body += '<p class="reader-help">Use the reader toolbar to search, choose a page, zoom or print. If the reader does not load, open or download the PDF directly.</p><iframe class="pdf-reader" src="'+viewer_url+'" title="'+e(title+' — '+record['title'], quote=True)+'" allow="fullscreen"></iframe><noscript><p>The embedded reader needs JavaScript. The direct PDF and download links above remain available.</p></noscript>'
                self.site.search.append(dict(title=title+' / '+record['title'], group='Collection', url=page,
                                             text=title+' '+record['title']+' '+PurePosixPath(path).name))
            else:
                text = raw.decode('utf-8-sig')
                body += '<p><a href="'+file_url+'" download>Download original file</a></p>'
                if record['format'] == 'markdown':
                    # Both pages share a directory, so their relative routes agree.
                    source_body = body+'<p><a href="'+self.site.rel(page, record['source_url'])+'">Read the formatted document</a></p>'+source_lines(text)
                    self.site.page(record['source_url'], title+' / Original Markdown', source_body,
                                   github(self.site.repos['collection'], self.site.revision, path))
                    body += '<p><a href="'+self.site.rel(record['source_url'], page)+'">Original Markdown with line links</a></p>'
                    rendered = markdown.markdown(text, extensions=['tables', 'fenced_code', 'toc', 'pymdownx.arithmatex'], extension_configs={'toc': {'slugify': slugify}, 'pymdownx.arithmatex': {'generic': True}})
                    rewrite = Rewriter(lambda target, image: self.site.resolve('collection', path, page, target, image))
                    rewrite.h1_count = 1
                    rewrite.feed(math_fences(rendered))
                    body += '<article class="edition-text">'+''.join(rewrite.out)+'</article>'
                else:
                    body += '<p>This is the original '+('TeX manuscript source. Use the paper’s PDF for typeset equations.' if path.endswith('.tex') else 'source text. Reading it does not run or verify the program.')+'</p>'
                    included = self.inclusions.get(path, [])
                    if included:
                        body += '<h2>Included manuscript sections</h2><ul>'+''.join('<li><a href="'+self.resolve(p, page)+'">'+e(PurePosixPath(p).name)+'</a></li>' for p in included)+'</ul>'
                    pdf = self.primary_pdf(work)
                    if pdf:
                        body += '<p><a class="button" href="'+self.site.rel(pdf['url'], page)+'">Read the typeset paper</a></p>'
                    body += source_lines(text)
                limit = 15000 if record['format'] == 'markdown' else 4000
                self.site.search.append(dict(title=title+' / '+record['title'], group='Collection', url=page, text=re.sub(r'\s+', ' ', text)[:limit]))
            if siblings:
                body += '<section><h2>Other PDFs for this work</h2><ul>'+''.join('<li><a href="'+self.site.rel(r['url'], page)+'">'+e(r['title'])+'</a></li>' for r in siblings)+'</ul></section>'
            body += '<details class="document-provenance"><summary>Original file and source record</summary><p>This copy matches the recorded source file. Its publication here does not change the work’s review status.</p><p>SHA-256: <code>'+record['sha256']+'</code></p><p><a href="'+github(self.site.repos['collection'], self.site.revision, path)+'">Original source on GitHub</a></p></details><p><a href="'+work_url+'">Back to '+e(title)+'</a></p>'
            self.site.page(page, title+' / '+record['title'], body, github(self.site.repos['collection'], self.site.revision, path))
        records = sorted(self.records.values(), key=lambda r: (r['work'], r['url']))
        self.site.write('documents/index.json', json.dumps(dict(source_revision=self.site.revision, files=records, images=list(self.images.values())), ensure_ascii=False, indent=2)+'\n')

    def catalog(self):
        e = html.escape
        pdfs = [r for r in self.records.values() if r['format'] == 'pdf']
        body = '<h1>Papers and PDFs</h1><p>Read the available papers, visual guides and formal companions here. Each reader includes search, page controls, zoom, printing and a direct download.</p><p><a href="works.html">Browse all works and their evidence</a> · <a href="collection/HAND_WORKED_EXAMPLES.html">Worked examples</a></p><label for="work-query">Find a work or document</label><input id="work-query" type="search" data-result-label="PDFs"><p id="work-count" role="status" aria-live="polite">'+str(len(pdfs))+' PDFs</p><div class="work-list">'
        for r in sorted(pdfs, key=lambda r: (self.site.components[r['work']]['title'], r['title'])):
            title = self.site.components[r['work']]['title']
            body += '<article class="work" data-search="'+e((title+' '+r['title']+' '+r['path']).lower(), quote=True)+'"><p class="eyebrow">'+e(r['title'])+'</p><h2><a href="'+r['url']+'">'+e(title)+'</a></h2><p>'+e(PurePosixPath(r['path']).name)+' · '+f"{r['size']/1e6:.1f}"+' MB</p><p><a href="collection/works/'+r['work']+'.html">Work, proofs, Lean and code</a></p></article>'
        body += '</div><noscript><p>All PDFs are shown. Use your browser’s Find command to locate a title.</p></noscript>'
        self.site.page('documents.html', 'Papers and PDFs', body)
