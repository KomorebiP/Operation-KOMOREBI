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
    allowed=set('a p div span h1 h2 h3 h4 h5 h6 ul ol li dl dt dd pre code blockquote strong em b i s del table thead tbody tr th td br hr img sup sub details summary kbd abbr'.split())
    void={'br','hr','img'}
    attrs={'id','class','title','href','src','alt','colspan','rowspan','scope','start','open','aria-label','role','tabindex'}
    def __init__(self, resolve):
        super().__init__(convert_charrefs=False)
        self.resolve=resolve
        self.out=[]
        self.blocked=0
        self.tables=0
        self.ids=set()
        self.heading_stack=[]
        self.h1_count=0
    def handle_starttag(self,tag,attrs):
        if tag in {'script','style','iframe','object','form'}:
            self.blocked+=1
            return
        if self.blocked or tag not in self.allowed:return
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
            self.out.append('<div class="table-scroll" role="region" aria-label="Scrollable table '+str(self.tables)+'" tabindex="0">')
        if tag=='th' and 'scope' not in dict(attrs):values.append(' scope="col"')
        self.out.append('<'+tag+''.join(values)+'>')
    def handle_endtag(self,tag):
        if tag in {'script','style','iframe','object','form'}:
            self.blocked=max(0,self.blocked-1)
            return
        if not self.blocked and tag in self.allowed and tag not in self.void:
            if re.fullmatch(r'h[1-6]',tag) and self.heading_stack:
                tag=self.heading_stack.pop()
            self.out.append('</'+tag+'>')
            if tag=='table':self.out.append('</div>')
    def handle_data(self,data):
        if not self.blocked:self.out.append(data)
    def handle_entityref(self,name):
        if not self.blocked:self.out.append('&'+name+';')
    def handle_charref(self,name):
        if not self.blocked:self.out.append('&#'+name+';')


class Site:
    def __init__(self,root,math_root,poly_root,output,revision,source_cache=None,mathjax_root=None,pdfjs_root=None):
        self.root=root
        self.roots={'collection':root,'math':math_root,'polyphase':poly_root}
        self.output=output
        self.revision=revision
        self.cache=source_cache
        self.mathjax_root=mathjax_root
        self.pdfjs_root=pdfjs_root
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
        root=self.rel('index.html',path)
        nav=[('Reading routes','collection/READING_ROUTES.html'),('Works','works.html'),('Papers and PDFs','documents.html'),('Examples','collection/HAND_WORKED_EXAMPLES.html'),('Software','software.html'),('Glossary','collection/GLOSSARY.html'),('Claims','claims.html'),('Downloads','downloads.html')]
        nav_html=''.join('<a href="'+self.rel(p,path)+'"'+(' aria-current="page"' if p==path else '')+'>'+t+'</a>' for t,p in nav)
        source_html=('<a href="'+esc(source,quote=True)+'">Source on GitHub</a> · ') if source else ''
        doc='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Read Komorebi papers, follow recorded proofs and run finite mathematical examples.">
<title>'''+esc(title)+''' · Komorebi</title><link rel="stylesheet" href="'''+self.rel('assets/reader.css',path)+'?v='+hashlib.sha256((self.root/'website/assets/reader.css').read_bytes()).hexdigest()[:12]+'''">
<script defer src="'''+self.rel('assets/mathjax-config.js',path)+'''"></script><script defer src="'''+self.rel('assets/mathjax/tex-svg-full.js',path)+'''"></script>
<script defer src="'''+self.rel('assets/reader.js',path)+'?v='+hashlib.sha256((self.root/'website/assets/reader.js').read_bytes()).hexdigest()[:12]+'''"></script></head><body>
<a class="skip-link" href="#main">Skip to main content</a><header class="site-header"><a class="brand" href="'''+root+'''">Komorebi<span>Mathematics · proofs · software</span></a><nav aria-label="Main navigation">'''+nav_html+'''<a href="'''+self.rel('search.html',path)+'''">Search</a></nav></header>
<main id="main" tabindex="-1">'''+body+'''</main><footer>'''+source_html+'''<a href="'''+self.rel('collection/PROJECT_STATEMENT.html',path)+'''">Project and authorship statement</a> · <a href="'''+self.rel('collection/ACCESSIBILITY.html',path)+'''">Accessibility and reporting problems</a><p>Work in progress. Completion, Lean coverage and confidence retain their recorded scope.</p></footer></body></html>'''
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
            if target.startswith(BASE_URL):return self.rel(target[len(BASE_URL):].split('#')[0] or 'index.html',page)+('#'+parts.fragment if parts.fragment else '')
            return target
        resolved=posixpath.normpath(posixpath.join(posixpath.dirname(path),unquote(parts.path))) if parts.path else path
        if resolved.startswith('../') or resolved.startswith('/'):
            return github(self.repos[repo],self.revisions[repo],resolved.lstrip('/'))
        if (repo,resolved) in self.documents:
            return self.rel(document_url(repo,resolved),page)+('#'+parts.fragment if parts.fragment else '')
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
            if repo=='collection' and path.startswith('docs/works/'):
                identifier=PurePosixPath(path).stem
                shortcut=self.reader.work_intro(identifier,page)
                content=re.sub(r'(</h1>)',lambda m:m[1]+shortcut,content,count=1)
                pdf=self.reader.primary_pdf(identifier)
                if pdf:
                    link='<p><a href="'+self.rel(pdf['url'],page)+'">Read the written arguments in the PDF</a>. The manuscript source remains available below.</p>'
                    content=content.replace('<h2 id="written-proofs">Written proofs</h2>','<h2 id="written-proofs">Written proofs</h2>'+link)
            body='<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="'+self.rel('index.html',page)+'">Home</a> / <a href="'+self.rel(repo+'/index.html',page)+'">'+section+'</a></nav><article>'+content+'</article>'
            self.page(page,title,body,github(self.repos[repo],self.revisions[repo],path))
            plain=re.sub(r'<[^>]+>',' ',rendered)
            plain=html.unescape(re.sub(r'\s+',' ',plain))
            self.search.append(dict(title=title,group=section,url=page,text=plain[:50000]))
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
    def indexes(self):
        e=html.escape
        route_links=[('New to Komorebi','Start with a small example and the vocabulary.','NEW_READER'),('Read the mathematics','Choose a work and keep its assumptions in view.','MATHEMATICS'),('Inspect a proof','Follow statements, formal sources and recorded evidence.','PROOF_REVIEW'),('Run the software','Choose an environment and compare expected output.','SOFTWARE')]
        cards=''.join('<a class="route" href="collection/routes/'+key+'.html"><h2>'+title+'</h2><p>'+desc+'</p><span>Open route →</span></a>' for title,desc,key in route_links)
        body='<section class="hero"><p class="eyebrow">Komorebi P. / A working research collection</p><h1>Find a way into<br>the mathematics.</h1><p class="lede">Read a paper, follow its proof, or run a small calculation. Choose your starting point and keep the work’s assumptions and evidence close at hand.</p><p><a class="button" href="works.html">Browse the works</a> <a href="search.html">Search the collection</a></p></section><section aria-label="Choose a reading route" class="route-grid">'+cards+'</section><section class="intro"><h2>Three repositories, one place to begin</h2><dl><dt><a href="collection/index.html">Operation KOMOREBI</a></dt><dd>Papers, books, research programs, formal sources and evidence.</dd><dt><a href="math/index.html">Komorebi Math</a></dt><dd>A Python library for finite mathematical constructions and inspectable certificates.</dd><dt><a href="polyphase/index.html">Polyphase Float</a></dt><dd>A C library for arbitrary-precision binary floating-point arithmetic.</dd></dl></section><aside class="notice"><h2>Read the status with the result</h2><p>The collection is a work in progress. Completion, Lean coverage and confidence are separate descriptions. Software is beta. A linked file is not evidence that every claim has been verified.</p><a href="collection/COMPLETION_STATUS.html">Understand the evidence labels</a></aside>'
        self.page('index.html','Read, inspect and run',body)
        body='<h1>Browse the works</h1><p>Each page brings together reading files, written proofs, Lean, code and the recorded limits. Incubator entries remain visible and labeled.</p><form class="filters" data-work-filter><label for="work-query">Find a title or subject</label><input id="work-query" name="q" type="search"><label for="work-group">Collection</label><select id="work-group"><option value="">All collections</option>'+''.join('<option value="'+g+'">'+t+'</option>' for g,t in [('papers','Core papers'),('monographs','Books and companion volumes'),('research','Research programs'),('packages','Software packages'),('experiments','Experiments')])+'</select><button type="reset">Clear filters</button></form><p id="work-count" role="status" aria-live="polite">'+str(len(self.registry['components']))+' works</p><div class="work-list">'
        for row in self.registry['components']:
            c=self.components[row['id']];s=self.assessments[row['id']]
            labels=self.status['labels']
            status=' · '.join(t+': '+labels[k][s[k]][0] for t,k in [('Completion','stage'),('Lean','lean'),('Confidence','confidence')])
            held=s.get('reader_listing',{}).get('placement')=='incubator'
            body+='<article class="work" data-group="'+c['group']+'" data-search="'+e((c['title']+' '+s.get('reader_summary',c['summary'])).lower(),quote=True)+'"><p class="eyebrow">'+e(c['group'])+(' · Incubator' if held else '')+'</p><h2><a href="collection/works/'+c['id']+'.html">'+e(c['title'])+'</a></h2><p>'+e(s.get('reader_summary',c['summary']))+'</p><p class="status">'+e(status)+'</p></article>'
        self.page('works.html','Browse works',body+'</div><noscript><p>All works are shown. Use your browser’s Find command to locate a title.</p></noscript>')
        self.page('software.html','Software','<h1>Run a small calculation</h1><p>Start with the platform instructions and expected output. All software remains beta.</p><p><a class="button" href="collection/FIRST_RUN.html">First runs and expected output</a></p><div class="route-grid"><a class="route" href="math/index.html"><h2>Komorebi Math</h2><p>Python. Finite operators, coordinates, signals and arithmetic.</p></a><a class="route" href="polyphase/index.html"><h2>Polyphase Float</h2><p>C on the supported Linux baseline. Arbitrary-precision binary arithmetic.</p></a></div><p><a href="collection/LIBRARIES.html">Library checks and source revisions</a></p>')
        self.page('search.html','Search the collection','<h1>Search the collection</h1><p>Search claims from all 12 core papers, glossary entries, worked examples, source texts and guides. Open a PDF and use its reader search to find words throughout that document.</p><form id="site-search" data-index="search-index.json"><label for="search-query">Word, symbol name or question</label><input id="search-query" type="search" name="q" autocomplete="off"><label for="search-group">Repository</label><select id="search-group"><option value="">All repositories</option><option>Collection</option><option>Komorebi Math</option><option>Polyphase Float</option></select><label for="search-kind">Result type</label><select id="search-kind"><option value="">All result types</option><option>Claims</option><option>Glossary</option><option>Examples</option><option>Papers and source</option><option>Guides</option></select><button type="submit">Search</button><button type="reset">Clear search</button></form><p id="search-status" role="status" aria-live="polite">Enter a search term.</p><ol id="search-results"></ol><button id="search-more" type="button" hidden>Show more results</button><noscript><p>Search needs JavaScript. You can still <a href="works.html">browse all works</a> and use the <a href="collection/GLOSSARY.html">glossary</a>.</p></noscript>')
        self.claim_index()
        learning=json.loads((self.root/'manifests/reader-experience.json').read_bytes())
        for term in learning['glossary']:
            self.search.append(dict(title=term['term'], group='Collection', kind='Glossary', url='collection/GLOSSARY.html#'+term['id'], text=term['term']+' '+term['definition']+' '+' '.join(term.get('related',[]))))
        for item in self.search:
            if 'kind' not in item:
                url=item['url']
                item['kind']=('Glossary' if '/GLOSSARY.' in url else 'Examples' if '/examples/' in url or '/HAND_WORKED_EXAMPLES.' in url else 'Papers and source' if url.startswith('read/') else 'Guides')
        self.write('search-index.json',json.dumps(self.search,ensure_ascii=False)+'\n')
        body='<h1>Download one work</h1><p>These ZIP files contain selected reading files and license notices, with source identities and SHA-256 checksums. They are not complete Lean or software builds. For those, use the <a href="collection/DOWNLOADS.html#obtain-a-full-component">component source instructions</a>.</p><p><a href="downloads/index.json">All bundle contents and checksums (JSON)</a></p><div class="download-list">'
        for r in self.bundle_records:
            body+='<section id="'+r['work']+'"><h2>'+e(r['title'])+'</h2><p><a download href="'+r['url']+'">Download reading ZIP</a> · '+f'{r["archive_bytes"]/1048576:.1f}'+' MB · '+str(len(r['files']))+' selected files</p><details><summary>Contents and checksum</summary><ul>'+''.join('<li>'+e(x['path'])+'</li>' for x in r['files'])+'</ul><p>ZIP SHA-256: <code>'+r['archive_sha256']+'</code></p></details><p><a href="collection/works/'+r['work']+'.html">Work, limits and evidence</a></p></section>'
        self.page('downloads.html','Download one work',body+'</div>')
        self.page('404.html','Page not found','<h1>This page could not be found</h1><p>Use the <a href="'+BASE_URL+'">Komorebi starting page</a>, <a href="'+BASE_URL+'search.html">search</a> or <a href="'+BASE_URL+'works.html">work index</a> to find the current page.</p>')
    def claim_index(self):
        render_claim_index(self)
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
        self.markdown_pages()
        self.reader.render()
        self.bundles()
        self.reader.catalog()
        self.indexes()
        self.write('.nojekyll','')
        result=dict(collection_revision=self.revision,library_revisions=self.revisions,html_guides=len(self.documents),works=len(self.registry['components']),claim_records=len(self.claims['records']),reading_bundles=len(self.bundle_records),bundle_bytes=sum(x['archive_bytes'] for x in self.bundle_records),new_proof_review=False,new_lean_execution=False)
        result.update(reading_documents=len(self.reader.records),pdfs=sum(r['format']=='pdf' for r in self.reader.records.values()))
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
    args=p.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}',args.revision):p.error('A full collection commit is required')
    Site(args.root.resolve(),args.math_root.resolve(),args.polyphase_root.resolve(),args.output.resolve(),args.revision,args.source_cache,args.mathjax_root,args.pdfjs_root).build()


if __name__=='__main__':main()
