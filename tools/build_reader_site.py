#!/usr/bin/env python3
"""Build the public reader site from maintained records and pinned library checkouts.

Requires Markdown and pymdown-extensions. Does not run scientific source code.
"""
from __future__ import annotations
import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import subprocess
from urllib.parse import quote, unquote, urlsplit
import zipfile

REPOSITORY = 'KomorebiP/Operation-KOMOREBI'
BASE_URL = 'https://KomorebiP.github.io/Operation-KOMOREBI/'
READ_KINDS = {'guide', 'pdf', 'visual', 'formal_guide', 'text', 'claims', 'lean_setup'}


def safe_path(value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError('Unsafe repository path: '+value)
    return p.as_posix()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def github(repo, revision, path, line=None):
    return 'https://github.com/'+repo+'/blob/'+revision+'/'+quote(path, safe='/')+('#L'+str(line) if line else '')


def slugify(value, separator):
    value = html.unescape(re.sub(r'<[^>]+>', '', value)).lower()
    return re.sub(r'[^\w\- ]', '', value).replace(' ', separator)


def math_fences(rendered):
    """Render GitHub math fences after Markdown has protected their TeX escapes."""
    return re.sub(r'<pre><code class="language-math">(.*?)</code></pre>',
                  lambda match: '<div class="arithmatex">\\['+match[1]+'\\]</div>',
                  rendered, flags=re.S)


def site_navigation(page):
    """Ordinary links with a progressively enhanced, nonmodal disclosure."""
    def link(title, target):
        current = ' aria-current="page"' if target == page else ''
        url = posixpath.relpath(target, posixpath.dirname(page) or '.')
        icon = ('<svg class="site-search-icon" viewBox="0 0 20 20" width="17" height="17" '
                'aria-hidden="true" focusable="false"><circle cx="8.5" cy="8.5" r="5.5"/>'
                '<path d="m12.5 12.5 4 4"/></svg>') if target == 'search.html' else ''
        return '<a href="'+html.escape(url, quote=True)+'"'+current+'>'+icon+html.escape(title)+'</a>'
    groups = [
        ('Read', [('Reading routes', 'collection/READING_ROUTES.html'),
                  ('Physics collection', 'collection/PHYSICS_COLLECTION.html'),
                  ('Special Functions', 'collection/SPECIAL_FUNCTIONS.html'),
                  ('Papers and PDFs', 'documents.html'),
                  ('Read side by side', 'side-by-side.html'),
                  ('Worked examples', 'collection/HAND_WORKED_EXAMPLES.html')]),
        ('Look up', [('Claims', 'claims.html'),
                     ('Notation', 'notation.html')]),
        ('Use', [('Signal laboratory', 'signal-lab.html'),
                 ('Interactive diagrams', 'interactive.html'),
                 ('Run Python', 'playground.html'), ('Software', 'software.html'),
                 ('Downloads', 'downloads.html'),
                 ('Accessibility', 'collection/ACCESSIBILITY.html')]),
    ]
    panel = ''.join('<div><p class="site-nav-label">'+title+'</p><ul>'+''.join(
        '<li>'+link(label, target)+'</li>' for label, target in links)+'</ul></div>'
        for title, links in groups)
    return ('<nav class="site-navigation" aria-label="Main navigation">'
            '<div class="site-navigation-bar"><div class="site-nav-links">'+link('Collection', 'works.html')+
            link('Glossary', 'collection/GLOSSARY.html')+link('About', 'collection/START_HERE.html')+
            '</div><div class="site-nav-tools">'+link('Search', 'search.html')+
            '<button id="site-menu-toggle" type="button" aria-expanded="true" '
            'aria-controls="site-menu-panel" hidden><svg class="site-browse-icon" viewBox="0 0 20 20" '
            'width="16" height="16" aria-hidden="true" focusable="false"><path '
            'd="M3 3h5v5H3zm9 0h5v5h-5zM3 12h5v5H3zm9 0h5v5h-5z"/></svg>'
            'Browse <span aria-hidden="true">▾</span></button></div></div>'
            '<div id="site-menu-panel" class="site-menu-panel">'+panel+'</div></nav>')


from home_page import home_page


def page_contents(content):
    """List section headings from the final sanitized HTML, preserving its IDs."""
    class Sections(HTMLParser):
        def __init__(self):
            super().__init__()
            self.sections = []
            self.heading = None
            self.anchor = None
        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            if tag == 'a' and values.get('id') and not values.get('href'):
                self.anchor = values['id']
            if tag == 'h2':
                # Explicit Markdown anchors may already own the heading's ID.
                self.heading = [values.get('id') or self.anchor, []]
                self.anchor = None
        def handle_data(self, data):
            if self.heading is not None:
                self.heading[1].append(data)
            elif data.strip():
                self.anchor = None
        def handle_endtag(self, tag):
            if tag == 'h2' and self.heading is not None:
                identifier, text = self.heading
                label = ' '.join(''.join(text).split())
                if identifier and label:
                    self.sections.append((identifier, label))
                self.heading = None
    parser = Sections()
    parser.feed(content)
    if len(parser.sections) < 4:
        return ''
    links = ''.join('<li><a href="#'+html.escape(quote(identifier), quote=True)+'">'+
                    html.escape(label)+'</a></li>' for identifier, label in parser.sections)
    return ('<details class="page-contents"><summary>On this page</summary>'
            '<nav aria-label="Sections on this page"><ul>'+links+'</ul></nav></details>')


def document_url(repo, path):
    prefix = {'collection':'collection', 'math':'math', 'polyphase':'polyphase'}[repo]
    if path == 'README.md':
        return prefix+'/index.html'
    if path.startswith('docs/'):
        path=path[5:]
    if path == 'index.md':
        path='guide.md'
    return prefix+'/'+str(PurePosixPath(path).with_suffix('.html'))


def selected_files(root, component):
    receipt=json.loads((root/('manifests/source-imports/'+component['id']+'.json')).read_bytes())
    by={x['path']:x for x in receipt['files']}
    paths={r['path'] for r in component['resources'] if r['kind'] in READ_KINDS and r['path'] in by}
    paths |= {p for p,v in by.items() if PurePosixPath(p).name.lower().startswith(('license','copying','notice')) and v['size']<200000}
    result=[]
    for p in sorted(paths):
        safe_path(p)
        entry=by[p]
        if entry['mode'] not in ('100644','100755'):
            raise ValueError('Reading bundle cannot contain a symlink: '+p)
        result.append({**entry,'repository_path':component['destination']+'/'+p})
    return result


from claim_navigation import validate_claims, render_claim_index


class Rewriter(HTMLParser):
    """Rewrite Markdown links and discard active content in source documents."""
    allowed=set('a p div span h1 h2 h3 h4 h5 h6 ul ol li dl dt dd pre code blockquote strong em b i s del table caption thead tbody tr th td br hr img figure figcaption sup sub details summary kbd abbr'.split())
    void={'br','hr','img'}
    attrs={'id','class','title','href','src','alt','colspan','rowspan','scope','start','open','aria-label','role','tabindex','width','height','loading'}
    def __init__(self, resolve):
        super().__init__(convert_charrefs=False)
        self.resolve=resolve
        self.out=[]
        self.blocked=0
        self.tables=0
        self.table_stack=[]
        self.ids=set()
        self.heading_stack=[]
        self.h1_count=0
    def handle_starttag(self,tag,attrs):
        if tag in {'script','style','iframe','object','form'}:
            self.blocked+=1
            return
        if self.blocked or tag not in self.allowed:return
        if tag in {'br','p','div'}:self._caption_text(' ')
        if re.fullmatch(r'h[1-6]',tag):
            rendered_tag='h2' if tag=='h1' and self.h1_count else tag
            if tag=='h1':self.h1_count+=1
            self.heading_stack.append(rendered_tag)
            tag=rendered_tag
        values=[]
        for key,value in attrs:
            if key not in self.attrs or value is None and key!='open':continue
            if key=='id':
                if value in self.ids:continue
                self.ids.add(value)
            if key in {'href','src'}:
                if urlsplit(value).scheme.lower() not in {'','http','https','mailto'}:continue
                value=self.resolve(value, key=='src')
            values.append(' '+key+('="'+html.escape(value,quote=True)+'"' if value is not None else ''))
        if tag=='table':
            self.tables+=1
            self.table_stack.append(dict(wrapper=len(self.out),caption=None,seen_caption=False))
            self.out.append('<div class="table-scroll" role="region" aria-label="Scrollable table '+str(self.tables)+'" tabindex="0">')
        elif tag=='caption' and self.table_stack and not self.table_stack[-1]['seen_caption']:
            self.table_stack[-1]['caption']=[]
            self.table_stack[-1]['seen_caption']=True
        if tag=='th' and 'scope' not in dict(attrs):values.append(' scope="col"')
        # Wide display math and code remain keyboard-scrollable without scripts.
        original = dict(attrs)
        if tag=='pre' or (tag=='div' and 'arithmatex' in original.get('class','').split()):
            defaults = {'tabindex':'0', 'role':'group', 'aria-label':
                        'Code example. Scroll horizontally if needed.' if tag=='pre' else
                        'Displayed equation. Scroll horizontally if needed.'}
            for key, value in defaults.items():
                if key not in original:values.append(' '+key+'="'+value+'"')
        self.out.append('<'+tag+''.join(values)+'>')
    def handle_endtag(self,tag):
        if tag in {'script','style','iframe','object','form'}:
            self.blocked=max(0,self.blocked-1)
            return
        if not self.blocked and tag in self.allowed and tag not in self.void:
            if tag in {'p','div'}:self._caption_text(' ')
            if re.fullmatch(r'h[1-6]',tag) and self.heading_stack:
                tag=self.heading_stack.pop()
            self.out.append('</'+tag+'>')
            if tag=='caption' and self.table_stack:
                table=self.table_stack[-1]
                if table['caption'] is not None:
                    name=' '.join(html.unescape(''.join(table['caption'])).split())
                    if name:
                        self.out[table['wrapper']]='<div class="table-scroll" role="region" aria-label="'+html.escape(name,quote=True)+'" tabindex="0">'
                    table['caption']=None
            if tag=='table':
                self.out.append('</div>')
                if self.table_stack:self.table_stack.pop()
    def _caption_text(self,text):
        if self.table_stack and self.table_stack[-1]['caption'] is not None:
            self.table_stack[-1]['caption'].append(text)
    def handle_data(self,data):
        if not self.blocked:
            self.out.append(data)
            self._caption_text(data)
    def handle_entityref(self,name):
        if not self.blocked:
            self.out.append('&'+name+';')
            self._caption_text('&'+name+';')
    def handle_charref(self,name):
        if not self.blocked:
            self.out.append('&#'+name+';')
            self._caption_text('&#'+name+';')


class Site:
    def __init__(self,root,math_root,poly_root,output,revision,source_cache=None,mathjax_root=None,pdfjs_root=None,python_root=None):
        self.root=root
        self.roots={'collection':root,'math':math_root,'polyphase':poly_root}
        self.output=output
        self.revision=revision
        self.cache=source_cache
        self.mathjax_root=mathjax_root
        self.pdfjs_root=pdfjs_root
        self.python_root=python_root
        self.registry=json.loads((root/'manifests/browse-resources.json').read_bytes())
        self.status=json.loads((root/'manifests/project-status.json').read_bytes())
        self.assessments={c['id']:c for c in self.status['components']}
        self.components={c['id']:c for c in json.loads((root/'manifests/source-components.json').read_bytes())['components']}
        self.libraries=json.loads((root/'manifests/reader-site-libraries.json').read_bytes())
        self.repos={'collection':REPOSITORY,'math':'KomorebiP/komorebi-math','polyphase':'KomorebiP/polyphase-float'}
        self.revisions={'collection':revision,**{k:v['revision'] for k,v in self.libraries.items()}}
        self.documents={}
        self.search=[]
        self.asset_count=0
        self.bundle_records=[]
        self.editorial_editions={}
        self.claims=validate_claims(root,{c['destination']+'/'+f['path'] for c in self.components.values() for f in json.loads((root/c['receipt']).read_bytes())['files']})
        from reader_documents import ReadingDocuments
        self.reader=ReadingDocuments(self)
    def write(self,path,text):
        target=self.output/safe_path(path)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(text,encoding='utf-8',newline='\n')
    def rel(self,target,page):
        return posixpath.relpath(target,posixpath.dirname(page) or '.')
    def page(self,path,title,body,source=None):
        esc=html.escape
        reading_page = 'data-reading-placement="top"' in body
        chapter_help_script=''
        if reading_page:
            from reading_navigation import chapter_layout
            work=re.search(r'data-reading-work="([a-z0-9-]+)"',body)
            if work and 'class="reading-outline"' in body:
                from reader_guidance import notation_help
                controls,dialog=notation_help(self,path,work[1])
                body=chapter_layout(body,controls)+dialog
                chapter_help_script=''.join('<script defer src="'+self.rel('assets/'+name,path)+'?v='+hashlib.sha256((self.root/'website/assets'/name).read_bytes()).hexdigest()[:12]+'"></script>' for name in ('notation-search.js','chapter-notation.js'))
            else:body=chapter_layout(body)
        work_page = path.startswith('collection/works/')
        if not work_page and 'data-side-reader-link' not in body and path not in {'side-by-side.html','index.html','404.html','interactive.html','signal-lab.html','works.html'}:
            pair=self.rel('side-by-side.html',path)+'?left='+quote(path,safe='')
            launch='<p class="side-launch"><a data-side-reader-link href="'+esc(pair,quote=True)+'">Read side by side</a></p>'
            body=re.sub(r'(</h1>)',lambda match:match[1]+launch,body,count=1)
        root=self.rel('index.html',path)
        nav_html=site_navigation(path)
        source_html=('<a href="'+esc(source,quote=True)+'">Source on GitHub</a>') if source else ''
        glossary_script=('<script defer src="'+self.rel('assets/glossary.js',path)+'?v='+hashlib.sha256((self.root/'website/assets/glossary.js').read_bytes()).hexdigest()[:12]+'"></script>') if path=='collection/GLOSSARY.html' else ''
        home_assets=''
        if path=='index.html':
            for name in ('home.css','home-slides.js'):
                url=self.rel('assets/'+name,path)+'?v='+hashlib.sha256((self.root/'website/assets'/name).read_bytes()).hexdigest()[:12]
                home_assets+=('<link rel="stylesheet" href="'+url+'">') if name.endswith('.css') else ('<script defer src="'+url+'"></script>')
        doc='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Read Komorebi papers, follow recorded proofs and run finite mathematical examples.">
<meta name="theme-color" content="#20583c">
<title>'''+esc(title)+''' · Komorebi</title><link rel="stylesheet" href="'''+self.rel('assets/reader.css',path)+'?v='+hashlib.sha256((self.root/'website/assets/reader.css').read_bytes()).hexdigest()[:12]+'''">
<link rel="stylesheet" href="'''+self.rel('assets/open-research.css',path)+'?v='+hashlib.sha256((self.root/'website/assets/open-research.css').read_bytes()).hexdigest()[:12]+'''">
<link rel="stylesheet" href="'''+self.rel('assets/side-reader.css',path)+'?v='+hashlib.sha256((self.root/'website/assets/side-reader.css').read_bytes()).hexdigest()[:12]+'''">
<script defer src="'''+self.rel('assets/mathjax-config.js',path)+'''"></script><script defer src="'''+self.rel('assets/mathjax/tex-svg-full.js',path)+'''"></script>
<script defer src="'''+self.rel('assets/reader.js',path)+'?v='+hashlib.sha256((self.root/'website/assets/reader.js').read_bytes()).hexdigest()[:12]+'''"></script>'''+glossary_script+chapter_help_script+home_assets+'''</head><body class="open-research'''+(' home-page' if path == 'index.html' else '')+(' reading-page' if reading_page else '')+(' work-page' if work_page else '')+'''">
<a class="skip-link" href="#main">Skip to main content</a><header class="site-header"><a class="brand" href="'''+root+'''"><span class="brand-wordmark">Komorebi<small>Mathematics · proofs · software</small></span></a>'''+nav_html+'''</header>
<main id="main" tabindex="-1">'''+body+'''</main><footer><div class="footer-inner"><nav class="footer-links" aria-label="Project information">'''+source_html+'''<a href="'''+self.rel('collection/PROJECT_STATEMENT.html',path)+'''">Project and authorship statement</a><a href="'''+self.rel('collection/ACCESSIBILITY.html',path)+'''">Accessibility and reporting problems</a></nav><a class="footer-github" href="https://github.com/'''+REPOSITORY+'''">Return to GitHub <span aria-hidden="true">↗</span></a></div></footer></body></html>'''
        self.write(path,doc)
    def collect_documents(self):
        maintained=set(self.status['maintained_documents'])
        maintained|={p.relative_to(self.root).as_posix() for p in (self.root/'docs').rglob('*.md') if p.is_file() and ('history' not in p.parts)}
        maintained|={'README.md','CITATION.md','CONTRIBUTING.md','LICENSE.md'}
        for path in sorted(maintained):
            if path.startswith('.github/'):continue
            if (self.root/path).is_file():self.documents[('collection',path)]=(self.root/path).read_text(encoding='utf-8')
        for key in ('math','polyphase'):
            root=self.roots[key]
            for p in sorted((root/'docs').rglob('*.md')):
                relative=p.relative_to(root).as_posix()
                if key=='polyphase' and ('history' in p.parts or re.search(r'0\.(?:1[0-9]|[0-9])(?:\.|\b)',p.name)):
                    continue
                self.documents[(key,relative)]=p.read_text(encoding='utf-8')
            for p in ('README.md','LICENSE.md','CONTRIBUTING.md','SUPPORT.md'):
                if (root/p).is_file():self.documents[(key,p)]=(root/p).read_text(encoding='utf-8')
    def resolve(self,repo,path,page,target,is_image=False):
        parts=urlsplit(html.unescape(target))
        if parts.scheme or parts.netloc:
            # Keep cross-repository documentation within the public reading site.
            for key,full in self.repos.items():
                for revision in ('main',self.revisions[key]):
                    prefix='https://github.com/'+full+'/blob/'+revision+'/'
                    if target.startswith(prefix):
                        relative=unquote(parts.path.split('/blob/'+revision+'/',1)[1])
                        if (key,relative) in self.documents:
                            return self.rel(document_url(key,relative),page)+('#'+parts.fragment if parts.fragment else '')
                        if key=='collection' and not is_image:
                            local=self.reader.resolve(relative,page,parts.fragment)
                            if local:return local
            base=urlsplit(BASE_URL)
            if parts.scheme in {'http','https'} and parts.netloc.lower()==base.netloc.lower() and parts.path.startswith(base.path):
                return self.rel(parts.path[len(base.path):] or 'index.html',page)+('?'+parts.query if parts.query else '')+('#'+parts.fragment if parts.fragment else '')
            return target
        resolved=posixpath.normpath(posixpath.join(posixpath.dirname(path),unquote(parts.path))) if parts.path else path
        if resolved.startswith('../') or resolved.startswith('/'):
            return github(self.repos[repo],self.revisions[repo],resolved.lstrip('/'))
        if (repo,resolved) in self.documents:
            return self.rel(document_url(repo,resolved),page)+('#'+parts.fragment if parts.fragment else '')
        if repo == 'collection':
            for edition in getattr(self,'editorial_editions',{}).values():
                if resolved == edition['pdf_source']:
                    return self.rel(edition['file_url'], page)+('#'+parts.fragment if parts.fragment else '')
        if repo=='collection' and resolved=='examples/komorebi_demonstrations.py':
            return self.rel('read/demonstrations.html',page)+('#'+parts.fragment if parts.fragment else '')
        if repo=='collection' and resolved=='examples/factorial_lanes.py':
            return self.rel('read/factorial-lanes.html',page)+('#'+parts.fragment if parts.fragment else '')
        if repo=='collection' and resolved=='examples/wavelet_polyphase.py':
            return self.rel('read/wavelet-polyphase.html',page)+('#'+parts.fragment if parts.fragment else '')
        if repo=='collection' and resolved=='examples/quantum_phase_measurement.py':
            return self.rel('read/quantum-phase-measurement.html',page)+('#'+parts.fragment if parts.fragment else '')
        if repo=='collection' and resolved=='examples/stirling_bell_fubini.py':
            return self.rel('read/stirling-bell-fubini.html',page)+('#'+parts.fragment if parts.fragment else '')
        if repo=='collection' and resolved=='examples/roots_unity_falling_factorial.py':
            return self.rel('read/roots-unity-falling-factorial.html',page)+('#'+parts.fragment if parts.fragment else '')
        if repo=='collection' and resolved=='examples/euler_packets.py':
            return self.rel('read/euler-packets.html',page)+('#'+parts.fragment if parts.fragment else '')
        if repo=='collection' and not is_image:
            reader_url=self.reader.resolve(resolved,page,parts.fragment)
            if reader_url:return reader_url
        if repo=='collection' and is_image:
            image_url=self.reader.image_url(resolved,page)
            if image_url:return image_url
        local=self.roots[repo]/resolved
        if is_image and local.is_file() and local.suffix.lower() in {'.svg','.png','.jpg','.jpeg','.webp','.gif'}:
            dest='assets/source/'+repo+'/'+resolved
            target_path=self.output/dest
            target_path.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(local,target_path)
            self.asset_count+=1
            return self.rel(dest,page)
        return github(self.repos[repo],self.revisions[repo],resolved)+('#'+parts.fragment if parts.fragment else '')
    def markdown_pages(self):
        import markdown
        for (repo,path),text in self.documents.items():
            page=document_url(repo,path)
            rendered=markdown.markdown(text,extensions=['tables','fenced_code','toc','pymdownx.arithmatex'],extension_configs={'toc':{'slugify':slugify},'pymdownx.arithmatex':{'generic':True}})
            rendered=math_fences(rendered)
            rewrite=Rewriter(lambda target,image:self.resolve(repo,path,page,target,image))
            rewrite.feed(rendered)
            title_match=re.search(r'^#\s+(.+)',text,re.M)
            title=title_match[1] if title_match else Path(path).stem
            section={'collection':'Collection','math':'Komorebi Math','polyphase':'Polyphase Float'}[repo]
            content=''.join(rewrite.out)
            if repo=='collection' and path=='docs/GLOSSARY.md':
                from glossary_reader import glossary_lookup, glossary_return_links
                glossary_config=json.loads((self.root/'manifests/reader-experience.json').read_bytes())
                content=glossary_return_links(content,glossary_config)
                lookup=glossary_lookup(glossary_config)
                content=re.sub(r'(</h1>)',lambda m:m[1]+lookup,content,count=1)
            is_euler = repo=='collection' and path=='docs/demonstrations/EULER_PACKETS.md'
            if is_euler:
                from euler_navigation import decorate
                content=decorate(content)
            elif repo=='collection' and path.startswith('docs/works/'):
                identifier=PurePosixPath(path).stem
                content=self.reader.work_overview(identifier,page,content)
                pdf=self.reader.primary_pdf(identifier)
                if pdf and not self.assessments[identifier].get('editorial_edition'):
                    link='<p><a href="'+self.rel(pdf['url'],page)+'">Read the written arguments in the PDF</a>. The manuscript source remains available below.</p>'
                    content=content.replace('<h2 id="written-proofs">Written proofs</h2>','<h2 id="written-proofs">Written proofs</h2>'+link)
            else:
                contents=page_contents(content)
                content=re.sub(r'(</h1>)',lambda m:m[1]+contents,content,count=1)
            article_class=' class="euler-example"' if is_euler else ''
            body='<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="'+self.rel('index.html',page)+'">Home</a> / <a href="'+self.rel(repo+'/index.html',page)+'">'+section+'</a></nav><article'+article_class+'>'+content+'</article>'
            self.page(page,title,body,github(self.repos[repo],self.revisions[repo],path))
            plain=re.sub(r'<[^>]+>',' ',rendered)
            plain=html.unescape(re.sub(r'\s+',' ',plain))
            self.search.append(dict(title=title,group=section,url=page,text=plain[:50000],work_ids=self.reader.document_works(repo,path)))
    def read_source(self,entry):
        path=entry['repository_path']
        candidates=[self.root/path]+([self.cache/'blobs'/entry['git_blob_sha1']] if self.cache else [])
        for file in candidates:
            if file.is_file():
                raw=file.read_bytes()
                if len(raw)!=entry['size'] or digest(raw)!=entry['sha256'] or blob(raw)!=entry['git_blob_sha1']:
                    raise ValueError('Source receipt mismatch: '+path)
                return raw
        raise FileNotFoundError('Source required for reading ZIP: '+path)
    def bundles(self):
        out=self.output/'downloads'
        out.mkdir(parents=True,exist_ok=True)
        for component in self.registry['components']:
            files=selected_files(self.root,component)
            identifier=component['id']
            record=dict(work=identifier,title=self.components[identifier]['title'],source_revision=self.revision,
                        scope='Selected reading files. Not a complete source or build archive.',files=files)
            archive=out/(identifier+'.zip')
            with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
                def put(path,raw):
                    info=zipfile.ZipInfo(path,date_time=(2026,10,28,0,0,0))
                    info.compress_type=zipfile.ZIP_DEFLATED
                    info.external_attr=0o100644<<16
                    z.writestr(info,raw)
                for entry in files:put('files/'+entry['path'],self.read_source(entry))
                put('CONTENTS.json',(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode())
                put('SHA256SUMS',(''.join(f['sha256']+'  files/'+f['path']+'\n' for f in files)).encode())
                overview=self.root/('docs/works/'+identifier+'.md')
                text=overview.read_text(encoding='utf-8')
                from navigation_links import inline_targets
                for target in set(inline_targets(text)):
                    if not urlsplit(target).scheme:
                        resolved=posixpath.normpath(posixpath.join('docs/works',target.split('#')[0])) if target.split('#')[0] else 'docs/works/'+identifier+'.md'
                        url=github(REPOSITORY,self.revision,resolved)+('#'+target.split('#',1)[1] if '#' in target else '')
                        text=text.replace(']('+target+')',']('+url+')')
                put('README.md',('# Reading selection\n\nThis ZIP contains selected reading files, not a complete software or Lean build.\n\nSource revision: '+self.revision+'\n\n'+text).encode())
                for name in ('LICENSE.md','CITATION.md','docs/PROJECT_STATEMENT.md'):
                    put('collection-notices/'+PurePosixPath(name).name,(self.root/name).read_bytes())
            record.update(url='downloads/'+identifier+'.zip',archive_bytes=archive.stat().st_size,archive_sha256=digest(archive.read_bytes()))
            self.bundle_records.append(record)
        self.write('downloads/index.json',json.dumps(self.bundle_records,ensure_ascii=False,indent=2)+'\n')
    def publish_editorial_editions(self):
        """Publish separately identified reading editions without replacing imports."""
        (self.output/'downloads').mkdir(parents=True,exist_ok=True)
        for work, assessment in self.assessments.items():
            edition = assessment.get('editorial_edition')
            if not edition:
                continue
            record = json.loads((self.root/safe_path(edition['build_record'])).read_bytes())
            for field in ('manuscript', 'latex', 'pdf'):
                path = safe_path(edition[field])
                if path != record[field] or digest((self.root/path).read_bytes()) != record[field+'_sha256']:
                    raise ValueError('Reading edition differs from its build record: '+path)
            source = (self.root/edition['manuscript']).read_text(encoding='utf-8')
            title = re.search(r'^#\s+(.+)', source, re.M)[1]
            raw = (self.root/edition['pdf']).read_bytes()
            dest = 'documents/files/'+blob(raw)+'/Machine_Native_Mathematics_Reading_Edition.pdf'
            target = self.output/dest
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            page = 'read/'+work+'/revised-reading-edition.html'
            original = self.reader.primary_pdf(work)
            if not original or original['sha256'] != record['original_pdf_sha256']:
                raise ValueError('Original edition identity differs: '+work)
            current = dict(work=work, title=title, url=page, file_url=dest,
                           pdf_source=edition['pdf'], pdf_sha256=record['pdf_sha256'],
                           manuscript_url=document_url('collection',edition['manuscript']),
                           manuscript_sha256=record['manuscript_sha256'],
                           original_pdf_sha256=record['original_pdf_sha256'], pages=record['pages'])
            archive_url='downloads/'+work+'-reading-edition.zip'
            source_paths=[edition['manuscript'], edition['latex'], edition['pdf'], edition['build_record'],
                          'publication/machine-native-mathematics/README.md',
                          'publication/machine-native-mathematics/EDITORIAL_REVIEW.md',
                          'tools/build_machine_native_essay.py','docs/PROJECT_STATEMENT.md','LICENSE.md']
            source_files=[]
            with zipfile.ZipFile(self.output/archive_url,'w',compression=zipfile.ZIP_DEFLATED) as bundle:
                for path in source_paths:
                    safe_path(path)
                    content=(self.root/path).read_bytes()
                    bundle.writestr(path,content)
                    source_files.append(dict(path=path,sha256=digest(content)))
            current.update(source_archive=archive_url,source_archive_sha256=digest((self.output/archive_url).read_bytes()),source_files=source_files)
            self.editorial_editions[work]=current
            viewer=self.reader.viewer_url(current,page)
            e=html.escape
            body=('<h1>'+e(title)+'</h1><p>Revised reading edition · 29 October 2026 · '+str(record['pages'])+' pages.</p>'
                  '<p><a class="button" href="'+self.rel(current['manuscript_url'],page)+'">Read as HTML</a> '
                  '<a href="'+self.rel(dest,page)+'" download>Download the monograph PDF</a> · '
                  '<a href="'+viewer+'">Expand PDF reader</a> · '
                  '<a href="'+self.rel(archive_url,page)+'">Download editable sources</a></p>'
                  '<p>This edition revises the prose and typesetting and makes local mathematical assumptions explicit. '
                  'The individual papers retain their own proof and verification records.</p>'
                  '<iframe class="pdf-reader" title="'+e(title,quote=True)+' — revised reading edition" src="'+viewer+'" allow="fullscreen"></iframe>'
                  '<p><a href="'+self.rel(original['url'],page)+'">Original PDF</a> · '
                  '<a href="'+self.rel('collection/components/MACHINE_NATIVE_MATHEMATICS.html',page)+'">Edition history and review scope</a></p>')
            self.page(page,title,body,github(REPOSITORY,self.revision,edition['manuscript']))
            self.search.append(dict(title=title+' / Revised reading edition',group='Collection',kind='Papers and source',work_ids=[work],url=page,text='Revised monograph PDF editable manuscript sources editorial reading edition machine native mathematics'))
        self.write('editorial-editions.json',json.dumps(list(self.editorial_editions.values()),ensure_ascii=False,indent=2)+'\n')

    def indexes(self):
        e=html.escape
        self.page('index.html','Explore the ideas. Follow the evidence.',home_page())
        from discipline_catalog import render_works_catalog, facet_records, page_navigation
        body = render_works_catalog(self.root, self.registry, self.components, self.assessments, self.status)
        self.page('works.html', 'Browse works', body)
        work_facets = facet_records(self.root, self.registry, self.assessments)
        self.write('work-facets.json', json.dumps(work_facets, ensure_ascii=False, sort_keys=True) + '\n')
        self.page('software.html','Software','<h1>Run a small calculation</h1><p><a class="button" href="playground.html#library">Try Komorebi Math in your browser</a></p><p>Start with the platform instructions and expected output. All software remains beta.</p><p><a class="button" href="collection/FIRST_RUN.html">First runs and expected output</a></p><div class="route-grid"><a class="route" href="math/index.html"><h2>Komorebi Math</h2><p>Python. Finite operators, coordinates, signals and arithmetic.</p></a><a class="route" href="polyphase/index.html"><h2>Polyphase Float</h2><p>C on the supported Linux baseline. Arbitrary-precision binary arithmetic.</p></a></div><p><a href="collection/LIBRARIES.html">Library checks and source revisions</a></p>')
        work_options=''.join('<option value="'+c['id']+'">'+e(self.components[c['id']]['title'])+'</option>' for c in self.registry['components'])

        facet_values = list(work_facets['works'].values())
        facet_dimensions = [
            ('discipline', 'Discipline', 'All disciplines',
             [(key, item['label']) for key, item in work_facets['disciplines'].items()]),
            ('stage', 'Completion stage', 'Any completion stage',
             [(key, item[0]) for key, item in self.status['labels']['stage'].items()
              if any(work['stage'] == key for work in facet_values)]),
            ('lean', 'Lean coverage', 'Any Lean coverage',
             [(key, item[0]) for key, item in self.status['labels']['lean'].items()
              if any(work['lean'] == key for work in facet_values)]),
            ('evidence', 'Evidence basis', 'Any evidence basis',
             [(key, item[0]) for key, item in self.status['labels']['confidence'].items()
              if any(work['evidence'] == key for work in facet_values)]),
        ]
        search_facets = ''.join(
            '<label for="search-'+key+'">'+e(title)+'</label><select id="search-'+key+'">'
            '<option value="">'+e(default)+'</option>'+
            ''.join('<option value="'+e(code)+'">'+e(label)+'</option>'
                    for code,label in options)+'</select>'
            for key,title,default,options in facet_dimensions)
        self.page('search.html','Search the collection','<h1>Search the collection</h1><p>Find a work, a claim, a written proof location, Lean guidance, code or a worked example. Choose one work to keep its related material together. Open a PDF and use its reader search to find words throughout that document. Discipline and evidence filters refer to associated works, not the proof status of each search hit. Unassociated pages are excluded when these filters are active.</p><form id="site-search" data-facets="work-facets.json?v='+e(self.revision)+'" data-index="search-index.json?v='+e(self.revision)+'"><label for="search-query">Word, symbol name or question</label><input id="search-query" type="search" name="q" autocomplete="off"><label for="search-group">Repository</label><select id="search-group"><option value="">All repositories</option><option>Collection</option><option>Komorebi Math</option><option>Polyphase Float</option></select><label for="search-work">Work</label><select id="search-work"><option value="">All works</option>'+work_options+'</select>'+search_facets+'<label for="search-kind">Result type</label><select id="search-kind"><option value="">All result types</option><option>Claims</option><option>Written proofs</option><option>Lean</option><option>Code</option><option>Glossary</option><option>Notation</option><option>Examples</option><option>Papers and source</option><option>Guides</option></select><label for="search-size">Results per page</label><select id="search-size" name="per_page"><option value="10">10</option><option value="20">20</option><option value="40" selected>40</option><option value="80">80</option></select><button type="submit">Search</button><button type="reset">Clear search</button></form><p id="search-status" role="status" aria-live="polite">Enter a search term.</p>'+page_navigation('search','top')+'<ol id="search-results"></ol>'+page_navigation('search','bottom')+'<noscript><p>Search needs JavaScript. You can still <a href="works.html">browse all works</a> and use the <a href="collection/GLOSSARY.html">glossary</a>.</p></noscript>')
        self.claim_index()
        self.reader.search_routes()
        learning=json.loads((self.root/'manifests/reader-experience.json').read_bytes())
        for term in learning['glossary']:
            self.search.append(dict(title=term['term'], group='Collection', kind='Glossary', url='collection/GLOSSARY.html#'+term['id'], text=term['term']+' '+term['definition']+' '+' '.join(term.get('related',[])),work_ids=sorted({w for t in learning.get('learning_topics',[]) if term['id'] in t['terms'] for w in t['works']})))
        for item in self.search:
            if 'kind' not in item:
                url=item['url']
                item['kind']=('Glossary' if '/GLOSSARY.' in url else 'Examples' if '/examples/' in url or '/demonstrations/' in url or '/HAND_WORKED_EXAMPLES.' in url or '/DEMONSTRATIONS.' in url else 'Papers and source' if url.startswith('read/') else 'Guides')
        self.write('search-index.json',json.dumps(self.search,ensure_ascii=False)+'\n')
        from download_selector import build as build_selector, interface as selector_interface
        build_selector(self)
        body='<link rel="stylesheet" href="assets/download-selector.css?v='+self.revision+'"><h1>Choose your downloads</h1><p>Build one ZIP from the files you want, or download a ready-made reading selection.</p><p><a href="#build-a-zip">Build your own ZIP</a> · <a href="#ready-made">Ready-made reading ZIPs</a> · <a href="collection/DOWNLOADS.html#obtain-a-full-component">Complete source downloads</a></p>'+selector_interface(self)
        body+='<h2 id="ready-made">Ready-made reading ZIPs</h2><p>One reading selection per work, with license notices and checksums. These are not complete Lean or software builds.</p><p><a href="downloads/index.json">All bundle contents and checksums (JSON)</a></p><div class="download-list">'
        for r in self.bundle_records:
            body+='<section id="'+r['work']+'"><h3>'+e(r['title'])+'</h3><p><a download href="'+r['url']+'">Download reading ZIP</a> · '+f'{r["archive_bytes"]/1048576:.1f}'+' MB · '+str(len(r['files']))+' selected files · <a href="downloads.html?work='+r['work']+'#build-a-zip">Choose files</a></p><details><summary>Contents and checksum</summary><ul>'+''.join('<li>'+e(x['path'])+'</li>' for x in r['files'])+'</ul><p>ZIP SHA-256: <code>'+r['archive_sha256']+'</code></p></details><p><a href="collection/works/'+r['work']+'.html">Work, limits and evidence</a></p></section>'
        self.page('downloads.html','Choose your downloads',body+'</div>')
        self.page('404.html','Page not found','<h1>This page could not be found</h1><p>Use the <a href="'+BASE_URL+'">Komorebi starting page</a>, <a href="'+BASE_URL+'search.html">search</a> or <a href="'+BASE_URL+'works.html">work index</a> to find the current page.</p>')
    def claim_index(self):
        render_claim_index(self)
    def demonstration_program(self):
        """Publish the teaching program as readable source and an exact download."""
        from reader_documents import source_lines
        path='examples/komorebi_demonstrations.py'
        raw=(self.root/path).read_bytes()
        text=raw.decode('utf-8')
        download='downloads/komorebi_demonstrations.py'
        (self.output/download).parent.mkdir(parents=True,exist_ok=True)
        (self.output/download).write_bytes(raw)
        record=dict(source=path,source_revision=self.revision,url=download,size=len(raw),sha256=digest(raw),
                    reader_url='read/demonstrations.html',scope='Three fixed exact teaching examples. No Lean execution or general theorem verification.')
        self.write('downloads/demonstration-source.json',json.dumps(record,indent=2)+'\n')
        body='<h1>Program for the three demonstrations</h1><p><a class="button" href="../playground.html">Run and edit these examples in your browser</a></p><p>Exact integer calculations using Python 3.10 or later and its standard library. The program checks reconstruction, refinement and a recovery witness.</p><nav class="document-routes" aria-label="Demonstration routes"><a href="../collection/DEMONSTRATIONS.html">Setup and scope</a><a href="../collection/demonstrations/PACKETS.html">Operator reconstruction</a><a href="../collection/demonstrations/REFINEMENT.html">Signal refinement</a><a href="../collection/demonstrations/RECOVERY.html">Recovery witness</a></nav><p><a class="button" download href="../'+download+'">Download Python program</a> <a href="../downloads/demonstration-source.json">Revision and checksum</a></p>'
        body+='<p>From the download folder, run <code>python -B komorebi_demonstrations.py all</code>. Each demonstration page provides its expected output and mathematical explanation.</p>'
        body+=source_lines(text)
        self.page('read/demonstrations.html','Program for the three demonstrations',body,github(REPOSITORY,self.revision,path))
        self.search.append(dict(title='Program for the three demonstrations',group='Collection',kind='Code',work_ids=['paper-i','paper-ii','paper-iii','paper-v','realization-boundaries'],url='read/demonstrations.html',text='Exact integer Python packet operator reconstruction residue refinement recovery obstruction witness standalone program'))
    def build(self):
        if self.output.exists() and any(self.output.iterdir()):
            raise ValueError('Use a new empty site output directory')
        self.output.mkdir(parents=True,exist_ok=True)
        self.collect_documents()
        self.reader.prepare()
        shutil.copytree(self.root/'website/assets',self.output/'assets',dirs_exist_ok=True)
        if not self.mathjax_root or not (self.mathjax_root/'a11y/explorer.js').is_file():
            raise ValueError('The complete pinned MathJax runtime is required')
        shutil.copytree(self.mathjax_root,self.output/'assets/mathjax')
        from fetch_pdf_runtime import verify as verify_pdf_runtime
        if not self.pdfjs_root:
            raise ValueError('The pinned PDF.js runtime is required')
        verify_pdf_runtime(self.pdfjs_root)
        shutil.copytree(self.pdfjs_root,self.output/'assets/pdfjs')
        self.publish_editorial_editions()
        from euler_case import publish as publish_euler_case
        publish_euler_case(self)
        from factorial_case import publish as publish_factorial_case
        publish_factorial_case(self)
        from wavelet_case import publish as publish_wavelet_case
        publish_wavelet_case(self)
        from quantum_case import publish as publish_quantum_case
        publish_quantum_case(self)
        from stirling_case import publish as publish_stirling_case
        publish_stirling_case(self)
        from roots_newton_case import publish as publish_roots_newton_case
        publish_roots_newton_case(self)
        self.markdown_pages()
        self.reader.render()
        self.bundles()
        self.reader.catalog()
        self.demonstration_program()
        from browser_python import build as build_python
        build_python(self,self.python_root)
        from notation_index import build as build_notation
        notation = build_notation(self)
        from interactive_diagrams import build as build_interactive_diagrams
        build_interactive_diagrams(self)
        from signal_lab import build as build_signal_lab
        build_signal_lab(self)
        self.indexes()
        from side_reader import build as build_side_reader
        side_reader = build_side_reader(self)
        self.write('.nojekyll','')
        result=dict(collection_revision=self.revision,library_revisions=self.revisions,html_guides=len(self.documents),works=len(self.registry['components']),claim_records=len(self.claims['records']),reading_bundles=len(self.bundle_records),bundle_bytes=sum(x['archive_bytes'] for x in self.bundle_records),new_proof_review=False,new_lean_execution=False)
        result.update(reading_documents=len(self.reader.records),pdfs=sum(r['format']=='pdf' for r in self.reader.records.values()))
        result['notation'] = notation
        result['side_reader'] = side_reader
        self.write('build-info.json',json.dumps(result,indent=2)+'\n')
        print(json.dumps(result))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--math-root',type=Path,required=True)
    p.add_argument('--polyphase-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--revision',required=True)
    p.add_argument('--source-cache',type=Path)
    p.add_argument('--mathjax-root',type=Path,required=True)
    p.add_argument('--pdfjs-root',type=Path,required=True)
    p.add_argument('--python-root',type=Path,required=True)
    args=p.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}',args.revision):p.error('A full collection commit is required')
    Site(args.root.resolve(),args.math_root.resolve(),args.polyphase_root.resolve(),args.output.resolve(),args.revision,args.source_cache,args.mathjax_root,args.pdfjs_root,args.python_root).build()


if __name__=='__main__':main()

