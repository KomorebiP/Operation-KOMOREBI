"""Publish receipt-bound papers and source texts inside the reading site."""
import hashlib
import html
import json
from pathlib import PurePosixPath
import posixpath
import re
from urllib.parse import quote, unquote, urlsplit

TEXT_SUFFIXES = {'.md', '.tex', '.txt', '.json', '.lean', '.py', '.bib', '.bbl', '.c', '.h'}


def png_dimensions(raw):
    """Read the intrinsic size without decoding or changing a retained image."""
    if len(raw)<33 or raw[:16]!=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR':
        raise ValueError('A PNG image must have its complete IHDR header')
    width=int.from_bytes(raw[16:20],'big')
    height=int.from_bytes(raw[20:24],'big')
    if not 0<width<2**31 or not 0<height<2**31:
        raise ValueError('Invalid PNG image dimensions')
    return width,height


def page_path(work, path):
    name = re.sub(r'[^a-z0-9]+', '-', PurePosixPath(path).stem.lower()).strip('-')[:70] or 'document'
    identity = hashlib.sha256(path.encode()).hexdigest()[:12]
    return 'read/'+work+'/'+name+'-'+identity+'.html'


def tex_includes(text, path, owned, main_path=None):
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
            bases = [posixpath.dirname(main_path)] if main_path else []
            bases.append(posixpath.dirname(path))
            candidate = next((p for base in bases
                              if (p := posixpath.normpath(posixpath.join(base, name))) in owned), None)
            if candidate:
                result.append(candidate)
    return sorted(set(result))


def source_lines(text, annotations=None):
    annotations = annotations or {}
    lines = text.splitlines()
    navigation = '<div id="source-navigation" class="source-navigation"><p><a href="#source-end">Skip source text</a></p>'
    if lines:
        navigation += ('<form id="source-line-form" class="source-jump" hidden>'
                       '<label for="source-line-number">Line number (1–'+str(len(lines))+')</label>'
                       '<div><input id="source-line-number" name="line" type="number" min="1" max="'+str(len(lines))+'" step="1" required>'
                       '<button type="submit">Go to line</button></div>'
                       '<p class="status">Jump directly to a line, then copy its address from your browser.</p></form>')
    navigation += '</div>'
    return navigation+'<pre class="source-lines" tabindex="0" aria-label="Source text with linked line numbers"><code>'+''.join(
        '<span class="source-line" id="L'+str(n)+'">'+annotations.get(n, '')+'<a class="line-number" href="#L'+str(n)+'" aria-label="Line '+str(n)+'">'+str(n)+'</a> '+html.escape(line)+'\n</span>'
        for n, line in enumerate(lines, 1))+'</code></pre><p id="source-end" tabindex="-1"><a href="#source-navigation">Back to source controls</a></p>'


class ReadingDocuments:
    def __init__(self, site):
        self.site = site
        self.owned = {}
        self.records = {}
        self.inclusions = {}
        self.images = {}
        self.learning = json.loads((site.root/'manifests/reader-experience.json').read_bytes())
        self.claims_by_source = {}
        self.claims_by_module = {}
        self.manuscript_roots = {w['id']:w['entrypoint'] for w in site.claims.get('works', [])}
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
            self.claims_by_source.setdefault(row['statement_path'], []).append(row)
            self.add(row['statement_path'])
            for declaration in row['lean']:
                if declaration['path']:
                    self.add(declaration['path'])
                    mapped = self.claims_by_module.setdefault(declaration['path'], [])
                    if row not in mapped:
                        mapped.append(row)

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
        from notation_index import prepare_sources
        prepare_sources(self)
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
                work = self.records[path]['work']
                main = self.notation_roots.get(path) or self.manuscript_roots.get(work)
                # Use the main manuscript directory only for files in that same tree.
                if main and not path.startswith(posixpath.dirname(main)+'/'):
                    main = None
                included = tex_includes(text, path, self.owned, main)
                self.inclusions[path] = included
                for child in included:
                    self.add(child)
                    if main and path in self.notation_roots:
                        self.notation_roots.setdefault(child, main)
                done.add(path)
        from readable_chapters import prepare
        prepare(self)
        from reader_atlas import prepare as prepare_atlas
        prepare_atlas(self)
        from paper_vi_atlas import prepare as prepare_paper_vi_atlas
        prepare_paper_vi_atlas(self)
        from paper_vii_atlas import prepare as prepare_paper_vii_atlas
        prepare_paper_vii_atlas(self)

    def primary_pdf(self, work):
        candidates = [r for r in self.records.values() if r['work'] == work and r['format'] == 'pdf']
        preferred = next((r for r in candidates if r['title'] == 'Read PDF'), None)
        return preferred or (candidates[0] if len(candidates) == 1 else None)

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
        if PurePosixPath(path).suffix.lower()=='.png':
            width,height=png_dimensions(raw)
            self.images[path].update(width=width,height=height)
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

    def work_intro(self, work, page, collection_links=''):
        """One work toolbar; keep specialist destinations in a native disclosure."""
        targets = self.work_route_targets(work)
        primary = next((label for label in ('Revised edition', 'Read chapters', 'Read PDF')
                        if any(name == label for name, _ in targets)), None)
        prominent = {primary, 'Read PDF', 'Written proofs', 'Worked examples'}
        hub = 'collection/works/'+work+'.html'
        def link(label, url, main=False):
            target = '#'+url.split('#',1)[1] if url.startswith(hub+'#') else self.site.rel(url,page)
            title = {'Read chapters':'Read online', 'Revised edition':'Read revised edition'}.get(label,label)
            return '<a'+(' class="button"' if main else '')+' href="'+html.escape(target,quote=True)+'">'+html.escape(title)+'</a>'
        ordered = sorted(((label,url) for label,url in targets if label in prominent), key=lambda row: row[0] != primary)
        body = '<nav id="work-navigation" class="work-overview-nav" aria-label="Reading routes for this work">'
        body += ''.join(link(label,url,label==primary) for label,url in ordered)
        body += '<details class="work-more"><summary>More resources</summary><div class="work-more-links">'
        body += ''.join(link(label,url) for label,url in targets if label not in prominent and label!='Paper overview')
        body += link('All HTML reading editions','read/index.html')
        pair = self.site.rel('side-by-side.html',page)+'?left='+quote(page,safe='')
        body += '<a data-side-reader-link href="'+html.escape(pair,quote=True)+'">Read side by side</a>'
        body += collection_links+'</div></details></nav>'
        return body

    def work_overview(self, work, page, content):
        """Adapt repository Markdown navigation to the shared website toolbar."""
        context = re.search(r'<p>(<a href="[^"]+">Browse hub</a>.*?)</p>',content,re.S)
        collection_links = ''.join(re.findall(r'<a\b[^>]*>.*?</a>',context[1],re.S)) if context else ''
        if context: content=content[:context.start()]+content[context.end():]
        # Preserve the fragment on the replacement toolbar for existing return links.
        content=re.sub(r'<p><a id="work-navigation"></a></p>\s*<p>.*?</p>','',content,count=1,flags=re.S)
        content=re.sub(r'<p>Use the links below to read this work and its supporting files\..*?</p>','',content,count=1,flags=re.S)
        content=re.sub(r'(<p><strong>Completion:</strong>.*?</p>)\s*(<p>.*?</p>)',
                       lambda m:m[2].replace('<p>','<p class="work-summary">',1)+
                       m[1].replace('<p>','<p class="work-status">',1),content,count=1,flags=re.S)
        return re.sub(r'(</h1>)',lambda m:m[1]+self.work_intro(work,page,collection_links),content,count=1)

    def work_route_targets(self, work):
        hub = 'collection/works/'+work+'.html'
        pdf = self.primary_pdf(work)
        routes = [('Paper overview', hub)]
        edition = getattr(self.site,'assessments',{}).get(work,{}).get('editorial_edition')
        if edition:
            manuscript = 'collection/'+edition['manuscript'].removeprefix('docs/').removesuffix('.md')+'.html'
            routes += [('Revised edition',manuscript),('Monograph PDF','read/'+work+'/revised-reading-edition.html')]
        from readable_chapters import BOOKS
        if work in BOOKS:
            routes.append(('Read chapters', BOOKS[work]['index']))
            if BOOKS[work].get('atlas_index'):
                routes.append(('Visual atlas', BOOKS[work]['atlas_index']))
            if BOOKS[work].get('diagram_guide'):
                routes.append(('Diagram descriptions', BOOKS[work]['diagram_guide']))
        if pdf: routes.append(('Original PDF' if edition else 'Read PDF', pdf['url']))
        if work in self.manuscript_roots: routes.append(('Claims', 'claims.html#'+work))
        routes += [('Written proofs', hub+'#written-proofs'), ('Lean', hub+'#lean'), ('Code', hub+'#code')]
        if any(work in t['works'] for t in self.learning.get('learning_topics', [])):
            routes.append(('Worked examples', hub+'#worked-examples-for-this-work'))
        routes += [('Notation', 'notation/'+work+'.html'), ('Evidence', hub+'#evidence'), ('Search this work', 'search.html?work='+quote(work))]
        return routes

    def work_routes(self, work, page):
        return '<nav class="document-routes" aria-label="Reading routes for this work">'+''.join(
            '<a href="'+self.site.rel(url, page)+'">'+label+'</a>' for label, url in self.work_route_targets(work))+'</nav>'

    def source_annotations(self, path, page):
        from side_reader import pair_link
        result = {}
        for row in self.claims_by_source.get(path, []):
            claim = self.site.rel('claims.html', page)+'#'+row['id'].lower()
            for field, label in [('statement_line', 'Statement'), ('proof_line', 'Proof block')]:
                line = row[field]
                if not line: continue
                links = '<a href="'+claim+'">'+html.escape(row['title'])+'</a>'
                other = 'proof_line' if field == 'statement_line' else 'statement_line'
                if row[other]:
                    links += ' · <a href="#L'+str(row[other])+'">'+('Go to proof' if other=='proof_line' else 'Go to statement')+'</a>'
                    links += ' · '+pair_link(page+'#L'+str(row['statement_line']), page+'#L'+str(row['proof_line']), page)
                note = '<span class="source-claim-links" role="group" aria-label="Related claim"><span>'+label+': </span>'+links+'</span>'
                result[line] = result.get(line, '')+note
        return result

    def source_claims(self, path, page):
        from side_reader import pair_link
        from readable_chapters import readable_url
        rows = self.claims_by_source.get(path, [])
        module = False
        if not rows:
            rows = self.claims_by_module.get(path, [])
            module = True
        if not rows: return ''
        body = '<details class="source-claims"><summary>'+str(len(rows))+' '+('claims linked to this Lean module' if module else 'indexed statements in this file')+'</summary><ul>'
        for row in rows:
            body += '<li><a href="'+self.site.rel('claims.html', page)+'#'+row['id'].lower()+'">'+html.escape(row['title'])+'</a>'
            if not module:
                body += ' · <a href="#L'+str(row['statement_line'])+'">Statement</a>'
                if row['proof_line']: body += ' · <a href="#L'+str(row['proof_line'])+'">Proof block</a>'
            else:
                statement = readable_url(row['statement_path'], row['statement_line']) or self.resolve(row['statement_path'], 'side-by-side.html', 'L'+str(row['statement_line']))
                if statement:
                    body += ' · '+pair_link(statement, page, page, 'Read statement beside this module')
            body += '</li>'
        return body+'</ul><p>These links follow the claim index. They do not extend the recorded proof or Lean coverage.</p></details>'

    def search_kind(self, record):
        if record['repository_path'].endswith('.lean') or 'Lean guide' in record['title']:
            return 'Lean'
        if PurePosixPath(record['repository_path']).suffix in {'.py', '.c', '.h'}:
            return 'Code'
        return 'Papers and source'

    def document_works(self, repo, path):
        if repo != 'collection': return []
        editions=[work for work,assessment in getattr(self.site,'assessments',{}).items()
                  if assessment.get('editorial_edition',{}).get('manuscript')==path]
        if editions:return editions
        from reader_experience import GUIDED_DEMONSTRATIONS
        if path in GUIDED_DEMONSTRATIONS: return GUIDED_DEMONSTRATIONS[path][1][:]
        if path.startswith('docs/works/'):
            work = PurePosixPath(path).stem
            return [work] if work in self.site.components else []
        return sorted({work for t in self.learning.get('learning_topics', [])
                       if t['example'] == path for work in t['works']})

    def search_routes(self):
        """Index useful work sections even when no individual source is selected."""
        for component in self.site.registry['components']:
            work = component['id']
            title = self.site.components[work]['title']
            hub = 'collection/works/'+work+'.html'
            assessment = self.site.assessments[work]
            lean = self.site.status['labels']['lean'][assessment['lean']][0]
            routes = [
                ('Written proofs', 'Written proofs and source files', 'written-proofs', 'Written arguments and available manuscript files for '+title),
                ('Lean', 'Lean coverage and sources', 'lean', lean+'. '+assessment['scope']),
                ('Code', 'Code and run instructions', 'code', 'Available code, scripts and software instructions for '+title)]
            if any(work in t['works'] for t in self.learning.get('learning_topics', [])):
                routes.append(('Examples', 'Worked examples', 'worked-examples-for-this-work', 'Introductory calculations linked to '+title))
            for kind, label, fragment, text in routes:
                self.site.search.append(dict(title=title+' / '+label, group='Collection', kind=kind,
                                             work_ids=[work], url=hub+'#'+fragment, text=text))

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
            body += self.work_routes(work, page)
            body += self.source_claims(path, page)
            siblings = [r for r in self.records.values() if r['work'] == work and r['format'] == 'pdf' and r != record and not r.get('figure_source')]
            if record['format'] == 'pdf':
                if not raw.startswith(b'%PDF-'):
                    raise ValueError('Invalid PDF signature: '+path)
                viewer_url = e(self.viewer_url(record, page), quote=True)
                body += '<div class="document-actions"><a class="button" href="'+viewer_url+'">Expand reader</a><a href="'+file_url+'">Open PDF directly</a><a href="'+file_url+'" download>Download PDF</a></div>'
                body += '<p class="reader-help">Use the reader toolbar to search, choose a page, zoom or print. If the reader does not load, open or download the PDF directly.</p><iframe class="pdf-reader" src="'+viewer_url+'" title="'+e(title+' — '+record['title'], quote=True)+'" allow="fullscreen"></iframe><noscript><p>The embedded reader needs JavaScript. The direct PDF and download links above remain available.</p></noscript>'
                self.site.search.append(dict(title=title+' / '+record['title'], group='Collection', kind=self.search_kind(record), work_ids=[work], url=page,
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
                    from readable_chapters import readable_url
                    readable = readable_url(path)
                    if readable:
                        body += '<p><a class="button" href="'+self.site.rel(readable,page)+'">Read this chapter with formatted equations</a></p>'
                    body += source_lines(text, self.source_annotations(path, page))
                limit = 15000 if record['format'] == 'markdown' else 4000
                self.site.search.append(dict(title=title+' / '+record['title'], group='Collection', kind=self.search_kind(record), work_ids=[work], url=page, text=re.sub(r'\s+', ' ', text)[:limit]))
            if siblings:
                body += '<section><h2>Other PDFs for this work</h2><ul>'+''.join('<li><a href="'+self.site.rel(r['url'], page)+'">'+e(r['title'])+'</a></li>' for r in siblings)+'</ul></section>'
            body += '<details class="document-provenance"><summary>Original file and source record</summary><p>This copy matches the recorded source file. Its publication here does not change the work’s review status.</p><p>SHA-256: <code>'+record['sha256']+'</code></p><p><a href="'+github(self.site.repos['collection'], self.site.revision, path)+'">Original source on GitHub</a></p></details><p><a href="'+work_url+'">Back to '+e(title)+'</a></p>'
            self.site.page(page, title+' / '+record['title'], body, github(self.site.repos['collection'], self.site.revision, path))
        from readable_chapters import render
        render(self)
        from reader_atlas import render as render_atlas
        render_atlas(self)
        from paper_vi_atlas import render as render_paper_vi_atlas
        render_paper_vi_atlas(self)
        from paper_vii_atlas import render as render_paper_vii_atlas
        render_paper_vii_atlas(self)
        records = sorted(self.records.values(), key=lambda r: (r['work'], r['url']))
        self.site.write('documents/index.json', json.dumps(dict(source_revision=self.site.revision, files=records, images=list(self.images.values())), ensure_ascii=False, indent=2)+'\n')

    def catalog(self):
        e = html.escape
        pdfs = [r for r in self.records.values() if r['format'] == 'pdf' and not r.get('figure_source')]
        editions=list(getattr(self.site,'editorial_editions',{}).values())
        body = '<h1>Papers and PDFs</h1><p><a class="button" href="read/index.html">Read the HTML editions</a></p><p>HTML editions provide chapter navigation, selectable equations and links between statements and proofs. Other papers, visual guides and formal companions are available below as PDFs with search, page controls, zoom, printing and a direct download.</p><p><a href="works.html">Browse all works and their evidence</a> · <a href="collection/HAND_WORKED_EXAMPLES.html">Worked examples</a></p><label for="work-query">Find a work or document</label><input id="work-query" type="search" data-result-label="PDFs"><p id="work-count" role="status" aria-live="polite">'+str(len(pdfs)+len(editions))+' PDFs</p><div class="work-list">'
        for edition in editions:
            body+='<article class="work" data-search="'+e((edition['title']+' revised reading edition monograph').lower(),quote=True)+'"><p class="eyebrow">Revised reading edition</p><h2><a href="'+edition['url']+'">'+e(edition['title'])+'</a></h2><p>'+str(edition['pages'])+' pages · Editable sources and HTML reading version available.</p><p><a href="'+edition['manuscript_url']+'">Read as HTML</a> · <a href="collection/works/'+edition['work']+'.html">Work and evidence</a></p></article>'
        for r in sorted(pdfs, key=lambda r: (self.site.components[r['work']]['title'], r['title'])):
            title = self.site.components[r['work']]['title']
            body += '<article class="work" data-search="'+e((title+' '+r['title']+' '+r['path']).lower(), quote=True)+'"><p class="eyebrow">'+e(r['title'])+'</p><h2><a href="'+r['url']+'">'+e(title)+'</a></h2><p>'+e(PurePosixPath(r['path']).name)+' · '+f"{r['size']/1e6:.1f}"+' MB</p><p><a href="collection/works/'+r['work']+'.html">Work, proofs, Lean and code</a></p></article>'
        body += '</div><noscript><p>All PDFs are shown. Use your browser’s Find command to locate a title.</p></noscript>'
        self.site.page('documents.html', 'Papers and PDFs', body)
