"""Source-bound reading editions of the retained Physics verification companions."""
import hashlib
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import posixpath
import re

WORK='monographs-physics'
BASE='monographs/physics/source/monographs/'
SCOPE='monographs/physics/book/verification_scope.pdf'
INDEX='read/'+WORK+'/verification/index.html'
REPORT='documents/physics-verification-companions.json'
SPEC_FILE=Path(__file__).with_name('physics_companion_sources.json')


def digest(raw):return hashlib.sha256(raw).hexdigest()
def metadata():return json.loads(SPEC_FILE.read_bytes())
def compact(text):return ' '.join(text.split())


def presentation_table(node):
    """Remove print row spacing while retaining every mathematical token."""
    from readable_chapters import MATH_PATTERN,original_math
    raw=node['body'];parts=[];position=0
    strip=lambda text:re.sub(r'(?<=\\\\)\[[0-9.]+(?:pt|em|ex)\]','',text)
    for match in MATH_PATTERN.finditer(raw):
        parts.extend([strip(raw[position:match.start()]),match[0]])
        position=match.end()
    parts.append(strip(raw[position:]));body=''.join(parts)
    assert original_math(body)==original_math(raw),'Table presentation changed mathematics'
    return dict(node,body=body)


def normalize(raw):
    from physics_reading import mask,normalize as common
    from foundational_reading import rewrite
    text=re.sub(r'\\(?:begin|end)\{quote\}|\\small\b|\\input\{[^{}]+\}',lambda m:mask(m[0]),raw)
    text=re.sub(r'\\begin\{Verbatim\}(?:\[[^\]]+\])?',lambda m:r'\begin{verbatim}'+('\n'*m[0].count('\n')),text)
    text=text.replace(r'\end{Verbatim}',r'\end{verbatim}')
    text=rewrite(text,'mbox',1,lambda content:content)
    return common(text)


def source_specs(load):
    from readable_chapters import clean_tex,group,navigation_title,chapter_text,original_math
    data=metadata()
    for path,sha in data['inputs'].items():
        if digest(load(path).encode())!=sha:raise ValueError('Review changed Physics companion source: '+path)
    for companion in data['companions']:
        main=load(companion['main'])
        if re.findall(r'\\input\{([^{}]+)\}',main)!=['preamble.tex',companion['body'].removeprefix(BASE)]:
            raise ValueError('Review Physics companion input order')
        body=clean_tex(main.split(r'\begin{document}',1)[1].split(r'\end{document}',1)[0])
        if re.sub(r'\\KomorebiCover\b|\\clearpage\b|\\input\{[^{}]+\}','',body).strip():
            raise ValueError('Unselected Physics companion main-file prose')
        expected_inputs=[fragment['source'].removeprefix(BASE) for fragment in companion['fragments'] if fragment['source']!=companion['body']]
        if re.findall(r'\\input\{([^{}]+)\}',load(companion['body']))!=expected_inputs:
            raise ValueError('Review Physics companion nested input order')
        selected=[]
        for fragment in companion['fragments']:
            raw=load(fragment['source']);selected.append(chapter_text(raw,fragment))
            pages=[p for p in data['pages'] if p.get('fragment')==fragment['id']]
            text=chapter_text(raw,fragment)
            headings=list(re.finditer(r'^\\section\{',text,re.M))
            if len(pages)!=len(headings) or pages[0]['start_line']!=fragment['start_line'] or pages[-1]['end_line']!=fragment['end_line']:
                raise ValueError('Incomplete Physics companion source ranges')
            for i,page in enumerate(pages):
                title,_=group(text,headings[i].end()-1)
                if page['title']!=navigation_title(title):raise ValueError('Review Physics companion heading identity')
                if i and (pages[i-1]['end_line']+1!=page['start_line'] or page['start_line']!=text.count('\n',0,headings[i].start())+1):
                    raise ValueError('Physics companion ranges have a gap or overlap')
        expanded=load(companion['body'])
        for child in expected_inputs:expanded=expanded.replace(r'\input{'+child+'}',load(BASE+child))
        if compact(normalize(''.join(selected)))!=compact(normalize(expanded)):
            raise ValueError('Incomplete Physics companion inclusion coverage')
        if [m for p in data['pages'] if p['companion']==companion['id'] for m in original_math(chapter_text(load(p['source']),p))]!=original_math(expanded):
            raise ValueError('Incomplete Physics companion mathematical sequence')
    return data


def scope_pages(raw,data):
    """Authenticate the full PDF transcription, including its printed exponent."""
    from pypdf import PdfReader
    if digest(raw)!=data['scope_sha256']:raise ValueError('Review changed Physics verification scope PDF')
    pdf=PdfReader(io.BytesIO(raw))
    if len(pdf.pages)!=3:raise ValueError('Review Physics scope page count')
    for source,page in zip(pdf.pages,data['scope_pages'],strict=True):
        extracted=compact(source.extract_text()).removeprefix('VERIFICATION AND SOURCES ')
        # PDF text extraction flattens this printed superscript. Its position
        # was checked against the rendered original before transcription.
        extracted=extracted.replace('2.63 × 1020','2.63 × 10²⁰')
        expected=compact(page['title']+' '+' '.join(s['title']+' '+s['text'] for s in page['sections']))
        if extracted!=expected:raise ValueError('Review Physics scope transcription: page '+str(page['pdf_page']))
    return data['scope_pages']


def config():
    data=metadata()
    return dict(work=WORK,label='Physics verification',overview_label='Physics',title='Physics verification and formalization companions',index=INDEX,
        chapters=data['scope_pages']+data['pages'],contents_groups=[dict(start=data['scope_pages'][0]['url'],title='Verification scope and sources')]+[
            dict(start=next(p['url'] for p in data['pages'] if p['companion']==c['id']),title=c['title']) for c in data['companions']],
        menu_title='Contents',index_title='All verification pages',footer_index_only=True,compact_chrome=True)


def prepare(reader,book):
    from readable_chapters import Chapter,chapter_text
    from physics_reading import source_macros
    def load(path):
        record=reader.add(path)
        if not record:raise ValueError('Missing retained Physics companion source: '+path)
        return reader.site.read_source(record).decode('utf-8-sig')
    data=source_specs(load)
    scopes=scope_pages(reader.site.read_source(reader.add(SCOPE)),data)
    chapters=[];labels={};state={};previous=None
    for spec in data['pages']:
        if spec['companion']!=previous:state={};previous=spec['companion']
        chapter=Chapter(normalize(chapter_text(load(spec['source']),spec)),source_macros(load),state=state,check_refs=False)
        chapter.url,chapter.base,chapter.source=spec['url'],BASE,spec['source']
        for key,node in chapter.labels.items():
            if key in labels:raise ValueError('Repeated Physics companion label: '+key)
            labels[key]=dict(node,url=chapter.url,reference_label=node['number'] or node['title'])
        state={key:getattr(chapter,key) for key in ['section','appendix','part','subsection','subsubsection','counter','section_prefix','figure','table','number_floats']}
        chapters.append((spec,chapter))
    for _,chapter in chapters:chapter.labels=labels;chapter.validate_references()
    book['verification_companions']=dict(data=data,scopes=scopes,chapters=chapters)


def article(reader,data,spec,chapter):
    from readable_chapters import HEADINGS,PANELS,render_table,passage_links
    body='<article id="chapter-text" class="readable-chapter" aria-label="Original Physics companion text">'
    for node in chapter.nodes:
        kind=node['kind'];ident=node['id']
        links='<a href="#'+ident+'">Permalink</a> · <a href="'+reader.resolve(spec['source'],spec['url'],'L'+str(node['line']))+'">Source line '+str(node['line'])+'</a>'
        if kind in HEADINGS:
            level=str(HEADINGS[kind])
            body+='<h'+level+' id="'+ident+'">'+chapter.inline(node['title'])+'</h'+level+'>'+passage_links(links)
        elif kind in {'longtable','tabular','table','tabularx'}:
            aid=next(a for a in data['table_aids'] if a['source']==spec['source'] and a['id']==ident)
            body+='<section id="'+ident+'">'+render_table(presentation_table(node),chapter,aid)+passage_links(links)+'</section>'
        elif kind in {'lstlisting','verbatim'}:
            content=re.sub(r'^\[[^\]]+\]','',node['body']).strip('\n')
            body+='<section id="'+ident+'"><pre tabindex="0" aria-label="Original inspection and reproduction commands"><code>'+html.escape(content)+'</code></pre>'+passage_links(links)+'</section>'
        elif kind=='text' or kind in PANELS:
            body+='<section id="'+ident+'" class="reading-block '+kind+'">'
            if kind in PANELS:body+='<h3>'+chapter.inline(node['title'] or PANELS[kind])+'</h3>'
            body+=chapter.paragraphs(node['body'])+passage_links(links)+'</section>'
        else:raise ValueError('Unsupported Physics companion block: '+kind)
    return body+'</article>'


def article_identity(markup):
    """Compare served and built article structure, text, and literal commands."""
    class Content(HTMLParser):
        def __init__(self):super().__init__();self.active=False;self.pre=False;self.events=[]
        def handle_starttag(self,tag,attrs):
            if tag=='article' and dict(attrs).get('id')=='chapter-text':self.active=True
            if self.active:self.events.append(('start',tag,sorted(attrs)))
            if self.active and tag=='pre':self.pre=True
        def handle_endtag(self,tag):
            if self.active:self.events.append(('end',tag))
            if tag=='pre':self.pre=False
            if tag=='article':self.active=False
        def handle_data(self,text):
            if self.active and (self.pre or text.strip()):self.events.append(('text',text if self.pre else compact(text)))
    content=Content();content.feed(markup)
    return digest(json.dumps(content.events,ensure_ascii=False).encode())


def render(reader):
    from readable_chapters import reading_options,original_math,chapter_text
    from reading_navigation import navigation,resources,outline,contents_list
    book=getattr(reader,'readable_books',{}).get(WORK)
    if not book:return
    edition=book['verification_companions'];data=edition['data'];site=reader.site;e=html.escape;reports=[]
    groups={c['id']:c for c in data['companions']}
    for spec,chapter in edition['chapters']:
        page=spec['url'];companion=groups[spec['companion']]
        body='<p class="eyebrow">Physics · '+e(companion['title'])+'</p><h1>'+e(spec['title'])+'</h1>'+reader.work_routes(WORK,page)+navigation(config(),page)
        tools='<p><a href="'+reader.resolve(spec['source'],page,'L'+str(spec['start_line']))+'">Original companion TeX</a> · <a href="'+site.rel(companion['reading'],page)+'">Read the treatment</a></p>'+reading_options('Show source lines and passage links. Evidence claims describe the retained source; this HTML publication adds no Lean execution or scientific run.')
        toc='<nav aria-label="On this verification page"><h2>On this page</h2><ol>'+''.join('<li><a href="#'+n['id']+'">'+e(n['title'])+'</a></li>' for n in chapter.nodes if n['title'])+'</ol></nav>'
        content=article(reader,data,spec,chapter)
        raw=reader.site.read_source(reader.records[spec['source']]).decode('utf-8-sig')
        if chapter.math!=original_math(chapter_text(raw,spec)):raise ValueError('Physics companion mathematics changed')
        body+=resources(tools)+outline(toc)+content+navigation(config(),page,'bottom')+'<p><a href="'+site.rel(REPORT,page)+'">Source and conversion record</a></p>'
        site.page(page,companion['title']+' / '+spec['title'],body)
        site.search.append(dict(title=companion['title']+' / '+spec['title'],group='Collection',kind='Papers and source',work_ids=[WORK],url=page,text=' '.join(n['title']+' '+n['body'] for n in chapter.nodes)))
        reports.append(dict(url=page,source=spec['source'],source_sha256=data['inputs'][spec['source']],companion=spec['companion'],start_line=spec['start_line'],end_line=spec['end_line'],article_sha256=article_identity(content),math_expressions=len(chapter.math),math_sequence_sha256=digest(json.dumps(chapter.math,ensure_ascii=False).encode()),nodes=[{k:n[k] for k in ['kind','id','line','end_line']} for n in chapter.nodes]))
    scope_reports=[]
    for spec in edition['scopes']:
        page=spec['url'];body='<p class="eyebrow">Physics · Verification and sources</p><h1>'+e(spec['title'])+'</h1>'+reader.work_routes(WORK,page)+navigation(config(),page)
        target=reader.viewer_url(reader.records[SCOPE],page,'page='+str(spec['pdf_page']))
        body+='<p class="reading-note">Reading transcription of the retained scope document. Phrases such as “current run” refer to its recorded publication checkpoint. <a href="'+e(target,quote=True)+'">Read the original PDF page</a>.</p>'
        content='<article id="chapter-text" class="readable-chapter" aria-label="Original verification scope text">'+''.join('<section id="scope-'+str(i)+'"><h2>'+e(s['title'])+'</h2><p>'+e(s['text']).replace('10²⁰','10<sup>20</sup>')+'</p></section>' for i,s in enumerate(spec['sections'],1))+'</article>'
        site.page(page,'Physics verification / '+spec['title'],body+content+navigation(config(),page,'bottom'))
        site.search.append(dict(title='Physics verification / '+spec['title'],group='Collection',kind='Papers and source',work_ids=[WORK],url=page,text=' '.join(s['title']+' '+s['text'] for s in spec['sections'])))
        scope_reports.append(dict(url=page,source=SCOPE,source_sha256=data['scope_sha256'],pdf_page=spec['pdf_page'],article_sha256=article_identity(content)))
    body='<p class="eyebrow">Physics · Verification and sources</p><h1>Verification and formalization companions</h1><p>Read the retained verification scope and all five companions. Follow the declarations, hypotheses, evidence records and remaining obligations alongside the mathematical treatments.</p>'+reader.work_routes(WORK,INDEX)
    body+='<p class="reading-note">These documents describe their archived publication checkpoints. Recorded compiler passes, source-identity audits and bounded computations retain their original scope. This HTML edition adds no proof audit, Lean execution or scientific computation.</p>'
    body+='<nav class="reading-contents-index" aria-label="Physics verification pages"><h2>Choose a companion or topic</h2>'+contents_list(config(),INDEX)+'</nav>'
    body+='<details class="reading-resources"><summary>Original companions in the full Physics PDF</summary><ul>'
    for companion in data['companions']:
        row=next(r for r in book['full_book'] if companion['main'].endswith('/'+r['stem']+'.tex'))
        target=reader.viewer_url(reader.records['monographs/physics/Komorebi_Physics.pdf'],INDEX,'page='+str(row['index_start']+1))
        body+='<li><a href="'+e(target,quote=True)+'">'+e(companion['title'])+' (PDF)</a></li>'
    body+='</ul></details><p><a href="'+site.rel(book['config']['index'],INDEX)+'">Read the Physics treatments</a> · <a href="'+site.rel(REPORT,INDEX)+'">Source and conversion record</a></p>'
    site.page(INDEX,'Physics verification and formalization companions',body)
    site.search.append(dict(title='Physics verification and formalization companions',group='Collection',kind='Papers and source',work_ids=[WORK],url=INDEX,text='Foundations Dirac gauge gravity adic verification Lean declarations evidence scope source provenance reproduction'))
    report=dict(source_revision=site.revision,index=INDEX,source_inputs=data['inputs'],html_pages=reports,scope_pages=scope_reports,scope_transcription='All three rendered PDF pages reviewed; multiplication sign and exponent transcribed as printed. PDF extraction is checked in full.',math_expressions=sum(r['math_expressions'] for r in reports),new_proof_review=False,new_lean_execution=False,scientific_computations_executed=False)
    site.write(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def verify(root,documents,pages):
    from readable_chapters import chapter_text,original_math,expand_math,Chapter
    from physics_reading import source_macros
    from reading_navigation import Navigation,neighbours
    from urllib.parse import urlsplit,unquote
    records={r['repository_path']:r for r in documents['files']}
    if 'monographs/physics/Komorebi_Physics.pdf' not in records:return dict(pages=0,math_expressions=0)
    load=lambda p:(root/records[p]['file_url']).read_text(encoding='utf-8-sig')
    data=source_specs(load);scope_pages((root/records[SCOPE]['file_url']).read_bytes(),data)
    report=json.loads((root/REPORT).read_bytes())
    assert report['source_revision']==documents['source_revision'] and report['source_inputs']==data['inputs']
    assert not any(report[k] for k in ['new_proof_review','new_lean_execution','scientific_computations_executed'])
    class Math(HTMLParser):
        def __init__(self):super().__init__();self.depth=0;self.values=[]
        def handle_starttag(self,tag,attrs):
            if self.depth:self.depth+=1
            elif 'arithmatex' in dict(attrs).get('class','').split():self.depth=1;self.values.append('')
        def handle_endtag(self,tag):
            if self.depth:self.depth-=1
        def handle_data(self,text):
            if self.depth:self.values[-1]+=text
    assert len(report['html_pages'])==len(data['pages']) and len(report['scope_pages'])==3
    macros=source_macros(load);count=0
    for spec,row in zip(data['pages']+data['scope_pages'],report['html_pages']+report['scope_pages'],strict=True):
        assert row['url']==spec['url'] and row['source_sha256']==(data['inputs'][spec['source']] if 'source' in spec else data['scope_sha256'])
        markup=(root/spec['url']).read_text(encoding='utf-8')
        assert row['article_sha256']==article_identity(markup),('Changed Physics companion article',spec['url'])
        assert (pages[spec['url']].h1,pages[spec['url']].main)==(1,1)
        if 'source' in spec:
            expected=original_math(chapter_text(load(spec['source']),spec));math=Math();math.feed(markup)
            assert [value[2:-2] for value in math.values]==[expand_math(value,macros) for value in expected],('Changed Physics companion math',spec['url'])
            assert row['math_expressions']==len(expected) and row['math_sequence_sha256']==digest(json.dumps(expected,ensure_ascii=False).encode())
            assert row['source']==spec['source'] and (row['start_line'],row['end_line'])==(spec['start_line'],spec['end_line'])
            chapter=Chapter(normalize(chapter_text(load(spec['source']),spec)),macros,check_refs=False)
            assert row['nodes']==[{k:n[k] for k in ['kind','id','line','end_line']} for n in chapter.nodes]
            for node in row['nodes']:
                assert node['id'] in pages[spec['url']].ids
                assert 'L'+str(node['line']) in pages[records[spec['source']]['url']].ids
            count+=len(expected)
        else:assert row['source']==SCOPE and row['pdf_page']==spec['pdf_page']
        nav=Navigation(markup);assert len(nav.controls)==2
        _,position,previous,following=neighbours(config(),spec['url'])
        for control in nav.controls:
            assert control['attrs']['data-reading-position']==str(position+1)
            assert control['attrs']['data-reading-total']==str(len(config()['chapters']))
            for direction,target in [('previous',previous),('next',following)]:
                links=[link for link in control['links'] if 'reading-'+direction in link.get('class','').split()]
                assert len(links)==1
                actual=posixpath.normpath(posixpath.join(posixpath.dirname(spec['url']),unquote(urlsplit(links[0]['href']).path)))
                assert actual==target['url']
    assert count==report['math_expressions']
    return dict(companions=5,pages=len(data['pages'])+3,scope_pages=3,math_expressions=count,source_inputs=len(data['inputs']))
