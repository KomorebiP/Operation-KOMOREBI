"""Source-bound edition of all 47 Paper XI lessons and the opening reader routes."""
import ast
import html
import json
from pathlib import Path
import posixpath
import re
from types import SimpleNamespace

from paper_xi_reading import BOOK,prepare_book,companion_routes,CONCORDANCE,mask
from readable_chapters import (HEADINGS,PANELS,KIND_NAMES,clean_tex,group,original_math,
    expand_math,manuscript_macros,passage_links,reading_options,render_table)
from worked_visual_atlas import AtlasChapter
from reader_atlas import digest
from reader_documents import png_dimensions
from reading_navigation import atlas_config,navigation,outline,resources,visual_title,visual_backlink,visual_position, visual_search_terms, visual_search_preview
from paper_ix_atlas import render_figure
from paper_xi_atlas_descriptions import DESCRIPTIONS,data_tables

BASE='papers/paper-xi/current/publication/source/visual_guide/'
SOURCE=BASE+'Paper_XI_Visual_Guide_Final.tex'
ROUTE=BASE+'reader_route.tex'
GENERATOR=BASE+'generate_figures.py'
DATA=BASE+'figures/figure_data.json'
SPEC=json.loads(Path(__file__).with_name('paper_xi_atlas_sources.json').read_bytes())
INDEX='read/paper-xi/atlas/index.html'
REPORT='documents/paper-xi-atlas.json'
RECEIPTS='assets/atlas/paper-xi/figures.json'


def section_url(number):return 'read/paper-xi/atlas/l'+str(number).zfill(2)+'.html'


def sections(read):
    text=read(SOURCE).decode('utf-8-sig')
    if re.findall(r'\\input\{([^{}]+)\}',text)!=['reader_route']:raise ValueError('Review Paper XI visual input graph')
    starts=list(re.finditer(r'^\\lesson\{',text,re.M));result=[]
    if len(starts)!=47:raise ValueError('Review Paper XI lesson inventory')
    for i,match in enumerate(starts):
        end=match.end()-1;values=[]
        for _ in range(3):value,end=group(text,end);values.append(value)
        stop=starts[i+1].start() if i+1<len(starts) else text.index(r'\end{document}',end)
        category,title,locator=values
        record=dict(number=i+1,category=category,title=title,locator=locator,source=SOURCE,
            start_line=text.count('\n',0,match.start())+1,end_line=text.count('\n',0,stop),
            figures=re.findall(r'\\plate\{([^{}]+)\}',text[end:stop]))
        if record!=SPEC['sections'][i]:raise ValueError('Changed Paper XI lesson boundary')
        result.append(dict(record,body='\n'*text.count('\n',0,end)+text[end:stop],url=section_url(i+1)))
    if sorted(n for row in result for n in row['figures'])!=sorted(SPEC['figures']):raise ValueError('Changed Paper XI figure inventory')
    return result


def opening(read):
    text=read(SOURCE).decode('utf-8-sig');start=text.index(r'\KomorebiOpeningNote{',text.index(r'\begin{document}'))
    end=text.index(r'\input{reader_route}',start)
    raw='\n'*text.count('\n',0,start)+text[start:end]
    route=read(ROUTE).decode('utf-8-sig')
    return [(dict(number=0,source=SOURCE,url=INDEX,title='Opening orientation'),raw),
        (dict(number=0,source=ROUTE,url=INDEX,title='Reader routes and corrections'),route)]


def normalize(text):
    count=text.count('\n')
    while match:=re.search(r'\\plate\{',text):
        name,end=group(text,match.end()-1);caption,stop=group(text,end)
        text=text[:match.start()]+r'\begin{figure}'+name+r'\end{figure}\begin{readerroadmap}[title={Original figure caption}]'+caption+r'\end{readerroadmap}'+'\n'*text[match.start():stop].count('\n')+text[stop:]
    for name,title in [('takeaway','Reading the diagram'),('boundary','Scope')]:
        while match:=re.search(r'\\'+name+r'\{',text):
            value,end=group(text,match.end()-1)
            text=text[:match.start()]+r'\begin{readerroadmap}[title={'+title+'}]'+value+r'\end{readerroadmap}'+text[end:]
    text=re.sub(r'\\phantomsection\b|\\vfill\b',lambda m:mask(m[0]),text)
    text=re.sub(r'\\\\\[(?:5|9)pt\]',lambda m:r'\\'+' '*(len(m[0])-2),text)
    result=clean_tex(text)
    if result.count('\n')!=count:raise ValueError('Paper XI visual translation moved source lines')
    return result


def visual_macros(read):
    # The retained guide uses unbraced command names; canonicalize only the parser input.
    text=re.sub(r'\\newcommand\\([A-Za-z]+)',r'\\newcommand{\\\1}',read(SOURCE).decode('utf-8-sig'))
    return manuscript_macros(text,['F','C','OO','GL','Sp','tr','Tr','Ind','cInd','Sw','Arf','rad','LLC'])


def figure_math_labels(source,name):
    tree=ast.parse(source);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    calls=sorted([n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='save'],key=lambda n:(n.lineno,n.col_offset))
    index=next(i for i,n in enumerate(calls) if len(n.args)==3 and isinstance(n.args[2],ast.Constant) and n.args[2].value==name)
    lower=(calls[index-1].end_lineno,calls[index-1].end_col_offset) if index else (main.lineno,0)
    upper=(calls[index].lineno,calls[index].col_offset)
    partial={id(n) for joined in ast.walk(main) if isinstance(joined,ast.JoinedStr) for n in ast.walk(joined)}
    return [dict(line=n.lineno,text=n.value) for n in sorted(ast.walk(main),key=lambda n:(getattr(n,'lineno',0),getattr(n,'col_offset',0)))
        if isinstance(n,ast.Constant) and isinstance(n.value,str) and '$' in n.value and id(n) not in partial and lower<(n.lineno,n.col_offset)<upper]


def reading_config(selected):
    return dict(atlas_config('paper-xi','Paper XI',INDEX,selected),
        index_title='All 47 visuals and opening routes',contents_groups=[
            dict(start=section_url(n),title=t) for n,t in [(1,'Finite tame coordinates'),(12,'Finite wild comparison'),(24,'Actual arithmetic construction'),(40,'Realization and comparison'),(46,'Evidence and sources')]])


def manuscript_book(read):
    root=Path(__file__).resolve().parents[1]
    reader=SimpleNamespace(records={},claims_by_source={},site=SimpleNamespace(root=root,read_source=lambda record:read(record['repository_path'])))
    reader.add=lambda path,*args:reader.records.setdefault(path,dict(repository_path=path))
    reader.resolve=lambda path,page,anchor=None:path+('#'+anchor if anchor else '')
    return prepare_book(reader,BOOK)


def routes(book):
    result={};chapters=book['chapters']
    for row in SPEC['sections']:
        targets=[]
        for key in SPEC['references'][str(row['number'])]:
            matches=[(c,n) for _,_,c in chapters for n in c.nodes if n['kind']=='section' and n['number']==key]
            if len(matches)!=1:raise ValueError('Changed Paper XI manuscript section '+key)
            chapter,node=matches[0]
            targets.append(dict(label=('Appendix ' if key.isalpha() else 'Section ')+key,title=node['title'],url=chapter.url+'#'+node['id']))
        result[row['number']]=targets
    return result


def figure_info(read,receipt):
    name=receipt['name'];alt,description=DESCRIPTIONS[name]
    return dict(receipt=receipt,alt=alt,description=description,
        math_labels=figure_math_labels(read(GENERATOR).decode('utf-8-sig'),name),tables=data_tables(name,json.loads(read(DATA))))


def load_figures(read,asset):
    for path,sha in SPEC['source_inputs'].items():
        if digest(read(path))!=sha:raise ValueError('Changed Paper XI visual dependency: '+path)
    if digest(read(SPEC['pdf']))!=SPEC['pdf_sha256']:raise ValueError('Changed Paper XI visual PDF')
    raw=asset(RECEIPTS)
    if digest(raw)!=SPEC['figure_receipts_sha256']:raise ValueError('Changed Paper XI drawing receipts')
    receipts=json.loads(raw)
    if (receipts['source_pdf'],receipts['source_pdf_sha256'])!=(SPEC['pdf'],SPEC['pdf_sha256']):raise ValueError('Changed Paper XI receipt PDF binding')
    figures={}
    for receipt in receipts['figures']:
        name=receipt['name'];binding=SPEC['figures'][name]
        if any(receipt[k]!=v for k,v in binding.items()):raise ValueError('Changed Paper XI vector source')
        raw=asset(receipt['image'])
        if receipt['image']!='assets/atlas/paper-xi/'+name+'.png' or digest(raw)!=receipt['image_sha256'] or list(png_dimensions(raw))!=receipt['dimensions']:raise ValueError('Changed Paper XI rendered figure')
        if digest(read(binding['source']))!=binding['source_sha256']:raise ValueError('Changed Paper XI retained figure')
        figures[name]=figure_info(read,receipt)
    if len(receipts['figures'])!=23 or set(figures)!=set(SPEC['figures']):raise ValueError('Incomplete Paper XI figures')
    return figures


def prepare(reader):
    for path in [*SPEC['source_inputs'],SPEC['pdf'],*(r['source'] for r in SPEC['figures'].values())]:reader.add(path)
    read=lambda path:reader.site.read_source(reader.records[path]);selected=sections(read)
    figures=load_figures(read,lambda path:(reader.site.root/'website'/path).read_bytes())
    book=reader.readable_books['paper-xi'];targets=routes(book);by_url={c.url:c for _,_,c in book['chapters']}
    for row in selected:
        for target in targets[row['number']]:
            page,anchor=target['url'].split('#');by_url[page].related_readings.setdefault(anchor,[]).append((visual_backlink(row),row['url']))
    reader.paper_xi_atlas=dict(sections=selected,figures=figures,targets=targets,macros=visual_macros(read))


def chapter_for(row,body,macros,read,resolve):
    chapter=AtlasChapter(normalize(body),macros);chapter.url=row['url'];chapter.included_sources={};chapter.allow_prose_groups=True
    chapter.href_targets={alias:resolve(path,row['url'],'page='+str(page)) for alias,(path,page) in companion_routes(lambda p:read(p).decode('utf-8-sig')).items()}
    return chapter


def content(row,chapter,figures,resolve,rel):
    body=''
    for node in chapter.nodes:
        kind,identifier=node['kind'],node['id']
        # The contents page combines two original files, whose line numbers can coincide.
        anchor=('opening-' if row['source']==SOURCE else 'route-')+identifier if row['number']==0 else identifier
        links='<a href="#'+anchor+'">Permalink</a> · <a href="'+resolve(row['source'],chapter.url,'L'+str(node['line']))+'">Original source line '+str(node['line'])+'</a>'
        if kind=='figure':body+='<div id="'+anchor+'">'+render_figure(figures[node['body']],chapter,resolve,rel)+passage_links(links)+'</div>'
        elif kind in HEADINGS:body+='<h2 id="'+anchor+'">'+chapter.inline(node['title'])+'</h2>'+passage_links(links)
        elif kind in {'table','tabular','tabularx'}:
            aid=dict(caption='Questions and companion reading routes',headers=['Start with the question','Continue to the linked reader'],row_header_column=0) if row['number']==0 else dict(caption='Retained sources for the complete arguments',headers=['Topic','Retained source anchor'],row_header_column=0)
            if row['number']==31:aid=dict(caption='Original-type quotient and carrier dimensions',headers=[r'$N$','host quotient','source quotient','host carrier','source carrier'],row_header_column=0)
            body+='<section id="'+anchor+'">'+render_table(node,chapter,aid)+passage_links(links)+'</section>'
        elif kind=='text' or kind in PANELS:
            body+='<section id="'+anchor+'" class="reading-block '+kind+'">'
            if kind in PANELS:body+='<h3>'+chapter.inline(node['title'] or PANELS[kind])+'</h3>'
            body+=chapter.paragraphs(node['body'])+passage_links(links)+'</section>'
        else:raise ValueError('Unsupported Paper XI visual block: '+kind)
    return body


def expected_math(body,figures):
    text=normalize(body);result=[];position=0
    for match in re.finditer(r'\\begin\{figure\}([^{}]+)\\end\{figure\}',text):
        result+=original_math(text[position:match.start()]);result+=[m for label in figures[match[1]]['math_labels'] for m in original_math(label['text'])];position=match.end()
    return result+original_math(text[position:])


def render(reader):
    atlas=reader.paper_xi_atlas;site=reader.site;selected=atlas['sections'];config=reading_config(selected);reports=[]
    read=lambda path:site.read_source(reader.records[path]);pdf=reader.records[SPEC['pdf']]
    for row in selected:
        page=row['url'];chapter=chapter_for(row,row['body'],atlas['macros'],read,reader.resolve)
        title=visual_title('Paper XI',row)
        body='<p class="eyebrow">'+visual_position('Paper XI',row['number'],47)+' · '+html.escape(row['category'])+'</p><h1>'+html.escape(row['title'])+'</h1>'+reader.work_routes('paper-xi',page)+navigation(config,page)
        body+='<nav class="document-routes" aria-label="Related manuscript passages">'+''.join('<a href="'+site.rel(t['url'],page)+'">'+html.escape(t['label']+': '+t['title'])+'</a>' for t in atlas['targets'][row['number']])+'</nav>'
        body+=resources('<p>Original source locator: '+chapter.inline(row['locator'])+'</p><p><a href="'+reader.viewer_url(pdf,page,'page='+str(row['number']+6))+'">This lesson in the original PDF</a></p>'+reading_options('Show passage permalinks and original source lines.'))
        body+='<article id="chapter-text" class="readable-chapter atlas-plate">'+content(row,chapter,atlas['figures'],reader.resolve,site.rel)+'</article>'+navigation(config,page,'bottom')
        expected=original_math(row['locator'])+expected_math(row['body'],atlas['figures'])
        if chapter.math!=expected:raise ValueError('Changed Paper XI lesson mathematics: '+str(row['number']))
        body+='<details class="document-provenance"><summary>Source and conversion record</summary><p>This edition preserves all 47 lessons, the opening orientation and both route sections. Figures are rendered from retained vector PDFs. Descriptions and recorded-data tables are reading aids. No mathematical generator, TeX build, proof audit or Lean replay was run for this conversion.</p><p><a href="'+site.rel(REPORT,page)+'">Source hashes and conversion checks</a></p></details>'
        site.page(page,title,body);site.search.append(dict(title=title,group='Collection',kind='Papers and source',visual_guide=True,work_ids=['paper-xi'],url=page,text=visual_search_terms(row)+' '+row['title']+' '+row['body'],**visual_search_preview(chapter,atlas['figures'])))
        reports.append(dict(number=row['number'],url=page,math=expected,source=row['source'],start_line=row['start_line'],end_line=row['end_line']))
    body='<p class="eyebrow">Paper XI visual guide</p><h1>Explore all 47 visuals</h1><p>Follow finite tame coordinates and finite wild comparison into the restricted arithmetic constructions, then the realization and comparison boundary. All 23 original vector figures have descriptions and selectable labels.</p>'+reader.work_routes('paper-xi',INDEX)
    for first,last,title in [(1,11,'Finite tame coordinates'),(12,23,'Finite wild comparison'),(24,39,'Actual arithmetic construction'),(40,45,'Realization and comparison'),(46,47,'Evidence and source map')]:
        body+='<section><h2>'+title+'</h2><ol start="'+str(first)+'">'+''.join('<li id="l'+str(r['number']).zfill(2)+'"><a href="'+site.rel(r['url'],INDEX)+'">'+html.escape(r['title'])+'</a></li>' for r in selected[first-1:last])+'</ol></section>'
    opening_math=[]
    body+='<article id="chapter-text" class="readable-chapter atlas-opening" aria-label="Original opening orientation and reader routes">'
    for row,raw in opening(read):
        chapter=chapter_for(row,raw,atlas['macros'],read,reader.resolve);body+=content(row,chapter,{},reader.resolve,site.rel)
        expected=original_math(normalize(raw))
        if chapter.math!=expected:raise ValueError('Changed Paper XI opening mathematics')
        opening_math+=expected
    body+='</article><p><a href="'+site.rel(REPORT,INDEX)+'">Conversion record</a></p>';site.page(INDEX,'Paper XI visual guide',body)
    record=dict(collection_revision=site.revision,source_inputs=SPEC['source_inputs'],source_pdf=SPEC['pdf'],source_pdf_sha256=SPEC['pdf_sha256'],index=INDEX,total_sections=47,html_sections=reports,opening_math=opening_math,figures=atlas['figures'],macros=atlas['macros'],manuscript_references=atlas['targets'],new_proof_review=False,new_lean_execution=False,new_mathematical_example_execution=False,new_tex_build=False)
    site.write(REPORT,json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    site.search.append(dict(title='Paper XI / Visual guide: 47 lessons and opening routes',group='Collection',kind='Papers and source',visual_guide=True,work_ids=['paper-xi'],url=INDEX,text=' '.join(r['title'] for r in selected)))


def verify(root,documents,pages):
    from check_reader_site import check_png_image_sizes
    from reading_navigation import Navigation,neighbours
    records={r['repository_path']:r for r in documents['files']};read=lambda path:(root/records[path]['file_url']).read_bytes()
    report=json.loads((root/REPORT).read_bytes());selected=sections(read);figures=load_figures(read,lambda path:(root/path).read_bytes());macros=visual_macros(read);targets=routes(manuscript_book(read))
    assert report['collection_revision']==documents['source_revision'] and report['source_inputs']==SPEC['source_inputs']
    assert (report['source_pdf'],report['source_pdf_sha256'],report['index'],report['total_sections'])==(SPEC['pdf'],SPEC['pdf_sha256'],INDEX,47)
    assert not any(report[k] for k in ('new_proof_review','new_lean_execution','new_mathematical_example_execution','new_tex_build'))
    assert report['figures']==json.loads(json.dumps(figures)) and report['macros']==macros and report['manuscript_references']=={str(k):v for k,v in targets.items()}
    rel=lambda path,page:posixpath.relpath(path,posixpath.dirname(page))
    from reader_documents import ReadingDocuments
    resolver=SimpleNamespace(records=records,site=SimpleNamespace(rel=rel))
    resolver.viewer_url=lambda *args:ReadingDocuments.viewer_url(resolver,*args)
    resolve=lambda path,page,anchor=None:ReadingDocuments.resolve(resolver,path,page,anchor or '')
    count=returns=0;config=reading_config(selected)
    for row,binding in zip(selected,report['html_sections'],strict=True):
        chapter=chapter_for(row,row['body'],macros,read,resolve);chapter.inline(row['locator'])
        markup=(root/row['url']).read_text(encoding='utf-8');assert content(row,chapter,figures,resolve,rel) in markup
        expected=original_math(row['locator'])+expected_math(row['body'],figures)
        assert chapter.math==expected
        assert binding==dict(number=row['number'],url=row['url'],math=expected,source=row['source'],start_line=row['start_line'],end_line=row['end_line'])
        actual=[html.unescape(x) for x in re.findall(r'<(?:span|div) class="arithmatex"[^>]*>(.*?)</(?:span|div)>',markup,re.S)]
        assert actual==[(r'\[' if t.startswith(r'\[') else r'\(')+expand_math(m,macros)+(r'\]' if t.startswith(r'\[') else r'\)') for t,m in zip(actual,expected,strict=True)]
        check_png_image_sizes(root,row['url'],pages[row['url']].images)
        for node in chapter.nodes:assert node['id'] in pages[row['url']].ids and 'L'+str(node['line']) in pages[records[row['source']]['url']].ids
        for target in targets[row['number']]:
            page,anchor=target['url'].split('#');assert anchor in pages[page].ids and rel(target['url'],row['url']) in pages[row['url']].links and rel(row['url'],page) in pages[page].links;returns+=1
        controls=Navigation(markup).controls;assert len(controls)==2
        _,position,previous,following=neighbours(config,row['url'])
        for control in controls:
            assert control['attrs']['data-reading-total']=='47' and control['attrs']['data-reading-position']==str(position+1)
            footer=control['attrs']['data-reading-placement']=='bottom'
            assert [a['href'] for a in control['links'] if 'data-reading-entry' in a]==([] if footer else [rel(r['url'],row['url']) for r in selected])
            if footer:assert [a['href'] for a in control['links'] if 'reading-menu-link' in a.get('class','').split()]==[rel(INDEX,row['url'])]
            for direction,target in [('previous',previous),('next',following)]:assert [a['href'] for a in control['links'] if 'reading-'+direction in a.get('class','').split()]==[rel(target['url'],row['url'])]
        count+=len(expected)
    opening_math=[];markup=(root/INDEX).read_text(encoding='utf-8')
    for row,raw in opening(read):
        chapter=chapter_for(row,raw,macros,read,resolve);assert content(row,chapter,{},resolve,rel) in markup;opening_math+=original_math(normalize(raw));assert chapter.math==original_math(normalize(raw))
    assert report['opening_math']==opening_math and all('l'+str(n).zfill(2) in pages[INDEX].ids for n in range(1,48))
    assert 'komorebi.invalid' not in markup
    return dict(total_sections=47,html_sections=47,drawings=23,source_tables=3,math_expressions=count+len(opening_math),return_links=returns,opening_routes=2)


ATLAS=SimpleNamespace(BOOK=BOOK,PDF=SPEC['pdf'],REPORT=REPORT,INDEX=INDEX,prepare=prepare,render=render,verify=verify)
