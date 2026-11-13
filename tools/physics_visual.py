"""Source-preserving HTML for the five retained Physics visual atlases."""
import hashlib
import html
import json
from pathlib import Path
import posixpath
import re
from types import SimpleNamespace

WORK='monographs-physics'
BASE='monographs/physics/source/monographs/'
PDF='monographs/physics/Komorebi_Physics.pdf'
INDEX='read/'+WORK+'/atlas/index.html'
REPORT='documents/physics-visual-atlases.json'
RECEIPTS='assets/figures/physics-visual-extra/figures.json'
SPEC_FILE=Path(__file__).with_name('physics_visual_sources.json')


def digest(raw):return hashlib.sha256(raw).hexdigest()
def metadata():return json.loads(SPEC_FILE.read_bytes())


def normalize(raw, atlas):
    from physics_reading import mask,normalize as common
    from foundational_reading import rewrite
    text=re.sub(r'^\\renewcommand\{\\atlasfigure\}\[2\].*$',lambda m:mask(m[0]),raw,flags=re.M)
    text=re.sub(r'\\(?:begingroup|endgroup)\b',lambda m:mask(m[0]),text)
    text=rewrite(text,'atlasfigure',2,lambda name,caption:
        r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{'+atlas['figures']+'/'+name+r'.pdf}\caption{'+caption+r'}\end{figure}')
    text=text.replace(r'\begin{tabularx}{\linewidth}',r'\begin{tabularx}{\textwidth}')
    return common(text)


def source_specs(load):
    from readable_chapters import chapter_text,original_math,clean_tex,group,navigation_title
    data=metadata()
    for path,sha in data['inputs'].items():
        if digest(load(path).encode())!=sha:raise ValueError('Review changed Physics visual source: '+path)
    for atlas in data['atlases']:
        main=load(atlas['main'])
        if re.findall(r'\\input\{([^{}]+)\}',main)!=['preamble.tex',atlas['body'].removeprefix(BASE)]:
            raise ValueError('Review Physics visual input order')
        body=clean_tex(main.split(r'\begin{document}',1)[1].split(r'\end{document}',1)[0])
        if re.sub(r'\\KomorebiCover\b|\\clearpage\b|\\input\{[^{}]+\}','',body).strip():
            raise ValueError('Unselected Physics visual main-file prose')
        raw=load(atlas['body'])
        directory=re.findall(r'\\includegraphics\[[^\]]+\]\{([^{}]+)/#1\.pdf\}',raw)
        if directory!=[atlas['figures']]:raise ValueError('Review Physics visual figure macro')
        pages=[s for s in data['pages'] if s['atlas']==atlas['id']]
        headings=list(re.finditer(r'^\\section\{',raw,re.M))
        if len(pages)!=len(headings) or pages[0]['start_line']!=1 or pages[-1]['end_line']!=len(raw.splitlines()):
            raise ValueError('Incomplete Physics visual source ranges')
        for i,s in enumerate(pages):
            title,_=group(raw,headings[i].end()-1)
            if navigation_title(title)!=s['title']:raise ValueError('Review Physics visual heading identity')
            if i and (pages[i-1]['end_line']+1!=s['start_line'] or s['start_line']!=raw.count('\n',0,headings[i].start())+1):
                raise ValueError('Physics visual ranges have a gap or overlap')
        if [m for s in pages for m in original_math(chapter_text(raw,s))]!=original_math(raw):
            raise ValueError('Incomplete Physics visual mathematical sequence')
    return data


def config():
    data=metadata()
    return dict(work=WORK,label='Physics visual guide',overview_label='Physics',index=INDEX,
        chapters=data['pages'],contents_groups=[dict(start=next(p['url'] for p in data['pages'] if p['atlas']==a['id']),title=a['title']) for a in data['atlases']],
        menu_title='Visuals',index_title='All atlas pages',footer_index_only=True)


def prepare(reader,book):
    from readable_chapters import Chapter,chapter_text
    from physics_reading import source_macros
    def load(path):
        record=reader.add(path)
        if record is None:raise ValueError('Missing Physics visual source: '+path)
        return reader.site.read_source(record).decode('utf-8-sig')
    data=source_specs(load)
    atlases={a['id']:a for a in data['atlases']}
    chapters=[]
    for spec in data['pages']:
        chapter=Chapter(normalize(chapter_text(load(spec['source']),spec),atlases[spec['atlas']]),source_macros(load),check_refs=False)
        chapter.url,chapter.base,chapter.source=spec['url'],BASE,spec['source']
        chapter.validate_references()
        chapters.append((spec,b'',chapter))
    from reader_figure_assets import prepare as prepare_figures
    extra=json.loads((reader.site.root/'website'/RECEIPTS).read_bytes())['figures']
    selected={r['source'] for r in extra}
    filtered=[(s,raw,SimpleNamespace(nodes=[n for n in c.nodes if n['kind']=='figure' and BASE+re.search(r'\\includegraphics\[[^\]]+\]\{([^{}]+)\}',n['body'])[1] in selected])) for s,raw,c in chapters]
    figure_config=dict(base=BASE,figure_receipts=RECEIPTS)
    figures={**book['figure_assets'],**prepare_figures(reader,figure_config,filtered)}
    names=[BASE+re.search(r'\\includegraphics\[[^\]]+\]\{([^{}]+)\}',n['body'])[1] for _,_,c in chapters for n in c.nodes if n['kind']=='figure']
    if len(names)!=60 or len(set(names))!=60 or any(p not in figures for p in names):
        raise ValueError('Review Physics visual plate inventory')
    book['visual_atlases']=dict(data=data,chapters=chapters,figures={p:figures[p] for p in names},figure_config=figure_config)


def article(reader,atlas,spec,chapter):
    from readable_chapters import HEADINGS,PANELS,passage_links,render_table,group,plain_math
    from reader_figure_assets import image,dimensions
    page=spec['url'];site=reader.site;e=html.escape
    body='<article id="chapter-text" class="readable-chapter atlas-plate" aria-label="Original Physics atlas text">'
    for node in chapter.nodes:
        kind=node['kind'];ident=node['id']
        links='<a href="#'+ident+'">Permalink</a> · <a href="'+reader.resolve(spec['source'],page,'L'+str(node['line']))+'">Source line '+str(node['line'])+'</a>'
        if kind in HEADINGS:
            body+='<h2 id="'+ident+'">'+chapter.inline(node['title'])+'</h2>'+passage_links(links)
        elif kind=='figure':
            match=re.search(r'\\includegraphics\[[^\]]+\]\{([^{}]+)\}',node['body'])
            caption,_=group(node['body'],node['body'].index(r'\caption')+len(r'\caption'))
            source,target,sha=image(reader,atlas['figure_config'],spec,atlas['figures'],match[1],page)
            receipt=atlas['figures'][source];width,height=dimensions((site.root/'website'/receipt['image']).read_bytes(),receipt['image'])
            alt=plain_math(caption.replace('$',''))[0]
            body+='<figure id="'+ident+'"><a href="'+target+'" aria-label="Open full-size plate"><img src="'+target+'" width="'+str(width)+'" height="'+str(height)+'" alt="'+e(alt,quote=True)+'" loading="lazy"></a><figcaption>'+chapter.inline(caption)+'</figcaption><p><a href="'+target+'">Open full-size plate</a> · <a href="'+reader.resolve(source,page)+'">Original vector figure</a></p></figure>'+passage_links(links)
        elif kind in {'table','tabular','tabularx','longtable'}:
            aid=next(a for a in atlas['data']['table_aids'] if a['source']==spec['source'] and a['id']==ident)
            body+='<section id="'+ident+'">'+render_table(node,chapter,aid)+passage_links(links)+'</section>'
        elif kind in {'lstlisting','verbatim'}:
            content=node['body']
            if content.startswith('['):raise ValueError('Review Physics visual listing options')
            body+='<section id="'+ident+'"><pre tabindex="0" aria-label="Original reproduction commands"><code>'+e(content.strip('\n'))+'</code></pre>'+passage_links(links)+'</section>'
        elif kind=='text' or kind in PANELS:
            body+='<section id="'+ident+'" class="reading-block '+kind+'">'
            if kind in PANELS:body+='<h3>'+chapter.inline(node['title'] or PANELS[kind])+'</h3>'
            body+=chapter.paragraphs(node['body'])+passage_links(links)+'</section>'
        else:raise ValueError('Unsupported Physics visual block: '+kind)
    from readable_chapters import original_math,chapter_text
    raw=reader.site.read_source(reader.records[spec['source']]).decode('utf-8-sig')
    if chapter.math!=original_math(chapter_text(raw,spec)):raise ValueError('Physics visual mathematics changed')
    return body+'</article>'


def render(reader):
    from readable_chapters import reading_options,original_math,chapter_text
    from reading_navigation import navigation,resources,outline,contents_list
    book=getattr(reader,'readable_books',{}).get(WORK)
    if not book:return
    atlas=book['visual_atlases'];site=reader.site;e=html.escape;reports=[]
    grouped={a['id']:a for a in atlas['data']['atlases']}
    for spec,_,chapter in atlas['chapters']:
        page=spec['url'];group=grouped[spec['atlas']]
        body='<p class="eyebrow">Physics · '+e(group['title'])+'</p><h1>'+e(spec['title'])+'</h1>'+reader.work_routes(WORK,page)+navigation(config(),page)
        tools='<p><a href="'+reader.resolve(spec['source'],page,'L'+str(spec['start_line']))+'">Original atlas TeX</a> · <a href="'+site.rel(group['reading'],page)+'">Read the treatment</a></p>'
        tools+=reading_options('Show source lines and passage links. Authored atlas prose, equations and captions are retained.')
        toc='<nav aria-label="On this atlas page"><h2 id="contents">On this page</h2><ol>'+''.join('<li><a href="#'+n['id']+'">'+e(n['title'] or 'Original plate')+'</a></li>' for n in chapter.nodes if n['title'] or n['kind']=='figure')+'</ol></nav>'
        body+=resources(tools)+outline(toc)+article(reader,atlas,spec,chapter)+navigation(config(),page,'bottom')
        body+='<p><a href="'+site.rel(REPORT,page)+'">Source and conversion record</a></p>'
        site.page(page,group['title']+' / '+spec['title'],body)
        site.search.append(dict(title=group['title']+' / '+spec['title'],group='Collection',kind='Guides',visual_guide=True,work_ids=[WORK],url=page,text=' '.join(n['title']+' '+n['body'] for n in chapter.nodes)))
        reports.append(dict(url=page,source=spec['source'],source_sha256=atlas['data']['inputs'][spec['source']],start_line=spec['start_line'],end_line=spec['end_line'],atlas=spec['atlas'],math_expressions=len(chapter.math),math_sequence_sha256=digest(json.dumps(chapter.math,ensure_ascii=False).encode()),nodes=[{k:n[k] for k in ['kind','id','line','end_line']} for n in chapter.nodes]))
    body='<p class="eyebrow">Physics · Visual guides</p><h1>Physics visual atlases</h1><p>Five complete atlases, with 60 original plates and their authored explanations. Read the diagrams alongside selectable equations, source links and the corresponding treatments. The retained scope notes distinguish finite examples, analytic arguments and formal evidence.</p>'+reader.work_routes(WORK,INDEX)
    body+='<nav class="reading-contents-index" aria-label="Physics visual atlas pages"><h2>Choose an atlas or topic</h2>'+contents_list(config(),INDEX)+'</nav>'
    body+='<details class="reading-resources"><summary>Original atlases in the full Physics PDF</summary><ul>'
    for group in atlas['data']['atlases']:
        row=next(r for r in book['full_book'] if group['main'].endswith('/'+r['stem']+'.tex'))
        target=reader.viewer_url(reader.records[PDF],INDEX,'page='+str(row['index_start']+1))
        body+='<li><a href="'+e(target,quote=True)+'">'+e(group['title'])+' (PDF)</a></li>'
    body+='</ul></details>'
    body+='<p><a href="'+site.rel(REPORT,INDEX)+'">Source and conversion record</a> · <a href="'+site.rel(book['config']['index'],INDEX)+'">Read the Physics treatments</a></p>'
    site.page(INDEX,'Physics visual atlases',body)
    site.search.append(dict(title='Physics visual atlases',group='Collection',kind='Guides',visual_guide=True,work_ids=[WORK],url=INDEX,text='Foundations Dirac gauge gravity adic polyphase original diagrams equations scope'))
    report=dict(source_revision=site.revision,index=INDEX,source_inputs=atlas['data']['inputs'],html_pages=reports,original_plates=60,figures=list(atlas['figures'].values()),math_expressions=sum(r['math_expressions'] for r in reports),new_proof_review=False,new_lean_execution=False,original_figure_generators_executed=False)
    site.write(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def inventory(root,files):
    from physics_reading import BOOK
    records={r['repository_path']:r for r in files};pdf=records[PDF];data=metadata()
    receipt=json.loads((root/'website/assets/figures/physics-foundations/figures.json').read_bytes())['figures'][0]
    return dict(work=WORK,label='Physics',title='Physics visual atlases',number=None,short_title='Packets, free fields, gauge, gravity and refinement',summary='Five complete visual atlases: 60 original plates with orientation, explanations, scope and reproduction notes.',units=len(data['pages']),unit_kind='pages',source_unit_kind='illustrated and supporting pages',topics='physics packets Dirac gauge gravity adic polyphase refinement',preview=dict(image=receipt['image'],sha256=receipt['image_sha256'],width=receipt['width'],height=receipt['height']),manuscript=BOOK['index'],overview='collection/works/'+WORK+'.html',html_atlas=INDEX,visual_pdf=pdf['url'],pdf_source=PDF,pdf_sha256=pdf['sha256'],integrated_pdf=True,sequences=[dict(id=a['id'],title=a['title'],summary='Twelve original illustrated plates, with orientation and scope.',source=a['body'],source_sha256=data['inputs'][a['body']],pages=[dict(url=p['url'],title=p['title']) for p in data['pages'] if p['atlas']==a['id']]) for a in data['atlases']])


def verify(root,documents,pages):
    """Independently bind every displayed expression, figure and reading route."""
    from html.parser import HTMLParser
    from readable_chapters import original_math,chapter_text,expand_math,Chapter
    from physics_reading import source_macros
    from reading_navigation import Navigation,neighbours
    from check_reader_site import check_table_reading_aids
    from reader_figure_assets import dimensions
    from urllib.parse import urlsplit,unquote
    records={r['repository_path']:r for r in documents['files']}
    if PDF not in records:return dict(pages=0,plates=0,math_expressions=0)
    load=lambda p:(root/records[p]['file_url']).read_text(encoding='utf-8-sig')
    data=source_specs(load);report=json.loads((root/REPORT).read_bytes())
    assert report['source_inputs']==data['inputs'] and report['source_revision']==documents['source_revision']
    assert len(report['html_pages'])==72 and len(report['figures'])==60
    assert not any(report[k] for k in ['new_proof_review','new_lean_execution','original_figure_generators_executed'])
    class Math(HTMLParser):
        def __init__(self):super().__init__();self.article=False;self.depth=0;self.values=[];self.images=[]
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='article' and attrs.get('id')=='chapter-text':self.article=True
            if not self.article:return
            if tag=='img':self.images.append(attrs.get('src'))
            if self.depth:self.depth+=1
            elif 'arithmatex' in attrs.get('class','').split():self.depth=1;self.values.append('')
        def handle_endtag(self,tag):
            if self.depth:self.depth-=1
            if tag=='article':self.article=False
        def handle_data(self,value):
            if self.article and self.depth:self.values[-1]+=value
    macros=source_macros(load);count=0;plates=0
    for spec,row in zip(data['pages'],report['html_pages'],strict=True):
        for field in ['url','source','start_line','end_line','atlas']:assert row[field]==spec[field],field
        expected=original_math(chapter_text(load(spec['source']),spec))
        assert row['source_sha256']==data['inputs'][spec['source']]
        assert row['math_expressions']==len(expected) and row['math_sequence_sha256']==digest(json.dumps(expected,ensure_ascii=False).encode())
        markup=(root/spec['url']).read_text(encoding='utf-8');math=Math();math.feed(markup)
        assert [s[2:-2] for s in math.values]==[expand_math(s,macros) for s in expected],('Changed Physics visual math',spec['url'])
        assert (pages[spec['url']].h1,pages[spec['url']].main,pages[spec['url']].images_without_alt)==(1,1,0)
        atlas=next(a for a in data['atlases'] if a['id']==spec['atlas'])
        chapter=Chapter(normalize(chapter_text(load(spec['source']),spec),atlas),macros,check_refs=False)
        assert row['nodes']==[{k:n[k] for k in ['kind','id','line','end_line']} for n in chapter.nodes]
        image_sources=[BASE+re.search(r'\\includegraphics\[[^\]]+\]\{([^{}]+)\}',n['body'])[1] for n in chapter.nodes if n['kind']=='figure']
        figures={r['source']:r for r in report['figures']}
        assert math.images==[posixpath.relpath(figures[p]['image'],posixpath.dirname(spec['url'])) for p in image_sources],('Changed Physics visual figure',spec['url'])
        for n in row['nodes']:
            assert n['id'] in pages[spec['url']].ids
            assert 'L'+str(n['line']) in pages[records[spec['source']]['url']].ids
            plates+=n['kind']=='figure'
        aids={a['id']:a for a in data['table_aids'] if a['source']==spec['source'] and spec['start_line']<=int(a['id'][1:])<=spec['end_line']}
        check_table_reading_aids(markup,aids)
        nav=Navigation(markup);assert len(nav.controls)==2
        seq,position,previous,following=neighbours(config(),spec['url'])
        for control in nav.controls:
            assert control['attrs']['data-reading-position']==str(position+1)
            assert control['attrs']['data-reading-total']=='72'
            for direction,target in [('previous',previous),('next',following)]:
                links=[a for a in control['links'] if 'reading-'+direction in a.get('class','').split()]
                assert len(links)==1
                actual=posixpath.normpath(posixpath.join(posixpath.dirname(spec['url']),unquote(urlsplit(links[0]['href']).path)))
                assert actual==target['url']
        count+=len(expected)
    for row in report['figures']:
        assert digest((root/records[row['source']]['file_url']).read_bytes())==row['source_sha256']
        raw=(root/row['image']).read_bytes();assert digest(raw)==row['image_sha256']
        assert dimensions(raw,row['image'])==(row['width'],row['height'])
    assert count==report['math_expressions']==718 and plates==60
    return dict(atlases=5,pages=72,plates=60,math_expressions=count,source_inputs=len(data['inputs']))
