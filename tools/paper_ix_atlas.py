"""Complete source-bound HTML edition of Paper IX's 23 visual sections."""
import ast
import html
import json
from pathlib import Path
import posixpath
import re
from types import SimpleNamespace

from paper_ix_reading import BOOK,prepare_book,mask
from readable_chapters import (HEADINGS,PANELS,KIND_NAMES,clean_tex,group,original_math,
    expand_math,passage_links,reading_options,render_table)
from worked_visual_atlas import AtlasChapter
from reader_atlas import digest
from reader_documents import png_dimensions
from reading_navigation import navigation,outline,resources
from paper_ix_atlas_descriptions import DESCRIPTIONS,data_tables

BASE='papers/paper-ix/current/'
SPEC=json.loads(Path(__file__).with_name('paper_ix_atlas_sources.json').read_text(encoding='utf-8'))
SOURCE=BASE+'sources/visual.tex'
BODY=BASE+'sources/visual_body.tex'
WORKED=BASE+'sources/worked_atlas.tex'
INCLUSION=BASE+'sources/generated/worked_newton_values.tex'
GENERATOR=BASE+'sources/generate_figures.py'
EXACT=BASE+'figures/exact_figure_data.json'
WORKED_DATA=BASE+'verification/2026-10-20/finite/runs/worked_examples/result.json'
INDEX='read/paper-ix/atlas/index.html'
REPORT='documents/paper-ix-atlas.json'
RECEIPTS='assets/atlas/paper-ix/figures.json'

REFERENCES=[
 ['def:arith-euler','prop:arith-denominator'],['thm:arith-nishibuchi'],['cor:all-dyadic-final'],
 ['thm:all-prime-power-transfer'],['cor:final-euler-congruence','thm:four-factorial-bound'],
 ['thm:two-exact-power-orders','thm:four-factorial-bound'],['thm:zero-one-exact-mixed'],
 ['thm:rank-four-exact-periods'],['thm:rank-four-exact-periods','cor:arith-least-period'],
 ['cor:four-exact-images'],['cor:four-exact-images','thm:arith-isometry'],
 ['prop:two-four-eight-isometry-table','thm:lower-half-all-dyadic-isometry'],
 ['thm:four-taylor-radii'],['sec:verification'],['sec:open','sec:final-original-congruence'],
 ['def:arith-euler','thm:triangular-foundation'],['ex:arith-normalization-loss'],
 ['thm:all-prime-power-transfer'],['thm:zero-one-exact-mixed','lem:arith-newton-period'],
 ['thm:smooth-tower','thm:smooth-padic-root'],
 ['thm:finite-polynomial-obstruction','rem:singular-tower-boundary'],['thm:common-correction'],
 ['thm:weighted-lifting','thm:coefficient-motion']]

TABLE_AIDS={
 29:dict(caption='Rows, degrees and addresses',headers=['Symbol','Meaning','At rank four'],row_header_column=0),
 66:dict(caption='Branches of the original conjecture',headers=['Prime branch',r'Allowed $m$',r'$q$','Row step for the original shift'],row_header_column=0),
 252:dict(caption='Mixed-step equality criterion',headers=['Order parity','Number of even steps','Conclusion'],row_header_column=0),
 436:dict(caption='Exact upper-half counterexamples',headers=[r'$(N,j)$',r'$v_2(C(1)-C(0))$','Step-two prediction','Actual step-two valuation'],row_header_column=0),
 494:dict(caption='Evidence and its recorded scope',headers=['Evidence','What it establishes','Scope of the final release'],row_header_column=0),
 564:dict(caption='Completed statements and remaining boundaries',headers=['Statement','Final status'],row_header_column=0),
}


def section_url(number):return 'read/paper-ix/atlas/s'+str(number).zfill(2)+'.html'


def sections(read):
    """Follow the actual standalone entrypoint, including its worked input."""
    wrapper=read(SOURCE).decode('utf-8-sig')
    if re.findall(r'\\input\{([^{}]+)\}',wrapper)!=['visual_body.tex','worked_atlas.tex']:
        raise ValueError('Review Paper IX visual input graph')
    result=[]
    for path,command,count in [(BODY,'section',15),(WORKED,'AtlasHead',8)]:
        text=read(path).decode('utf-8-sig');starts=list(re.finditer(r'\\'+command+r'\{',text))
        if len(starts)!=count:raise ValueError('Review Paper IX visual section inventory')
        for i,match in enumerate(starts):
            title,end=group(text,match.end()-1)
            if command=='AtlasHead':_,end=group(text,end)
            stop=starts[i+1].start() if i+1<len(starts) else len(text)
            number=len(result)+1;raw=text[end:stop]
            figures=re.findall(r'\\includegraphics\[[^\]]+\]\{\.\./figures/([^{}]+)\.pdf\}',raw)+['worked/'+name for name in re.findall(r'\\AtlasImage\{([^{}]+)\}',raw)]
            record=dict(number=number,title=title,source=path,start_line=text.count('\n',0,match.start())+1,
                end_line=text.count('\n',0,stop),figures=figures)
            if record!=SPEC['sections'][number-1]:raise ValueError('Changed Paper IX visual section boundary')
            result.append(dict(record,body='\n'*text.count('\n',0,end)+raw,url=section_url(number)))
    if sorted(name for row in result for name in row['figures'])!=sorted(SPEC['figures']):
        raise ValueError('Paper IX figure coverage changed')
    return result


def normalize(text):
    """Translate presentation wrappers while retaining every original source line."""
    count=text.count('\n')
    text=re.sub(r'\\begin\{figure\}\[ht\]|\\end\{figure\}|\\centering\b',lambda m:mask(m[0]),text)
    text=re.sub(r'\\includegraphics\[[^\]]+\]\{\.\./figures/([^{}]+)\.pdf\}',lambda m:r'\begin{figure}'+m[1]+r'\end{figure}',text)
    text=re.sub(r'\\AtlasImage\{([^{}]+)\}',lambda m:r'\begin{figure}worked/'+m[1]+r'\end{figure}',text)
    while match:=re.search(r'\\caption\{',text):
        value,end=group(text,match.end()-1)
        text=text[:match.start()]+r'\begin{readerroadmap}[title={Original figure caption}]'+value+r'\end{readerroadmap}'+text[end:]
    text=clean_tex(text)
    if text.count('\n')!=count:raise ValueError('Paper IX visual translation moved source lines')
    return text


def figure_math_labels(source,name):
    """Read literal Matplotlib math labels from the original Python AST; never run it."""
    if name.startswith('worked/'):return []
    sections_=list(re.finditer(r'^# \d\d\. ',source,re.M))
    end=re.search(r'^save\(fig,"'+re.escape(name)+r'"\)',source,re.M)
    if not end:raise ValueError('Missing original figure generator boundary')
    start=max(m.start() for m in sections_ if m.start()<end.start())
    first=source.count('\n',0,start)+1;last=source.count('\n',0,end.end())+1
    return [dict(line=node.lineno,text=node.value) for node in sorted(ast.walk(ast.parse(source)),key=lambda n:(getattr(n,'lineno',0),getattr(n,'col_offset',0)))
        if isinstance(node,ast.Constant) and isinstance(node.value,str) and '$' in node.value and first<=node.lineno<=last]


def reading_config(selected):
    return dict(work='paper-ix',label='Paper IX visual guide',overview_label='Paper IX',index=INDEX,
        chapters=[dict(url=r['url'],title=str(r['number'])+' · '+r['title']) for r in selected],
        menu_title='Visual sections',index_title='All 23 visual sections',
        contents_groups=[dict(start=section_url(1),title='Congruences and dyadic geometry'),dict(start=section_url(16),title='Worked arithmetic and lifting')])


def manuscript_book(read):
    """Reconstruct the manuscript's own normalization and printed label numbering."""
    reader=SimpleNamespace(records={},claims_by_source={},site=SimpleNamespace(read_source=lambda path:read(path)))
    reader.add=lambda path:reader.records.setdefault(path,path)
    return prepare_book(reader,BOOK)


def routes(book):
    labels=book['chapters'][0][2].labels
    result={}
    for number,keys in enumerate(REFERENCES,1):
        result[number]=[]
        for key in keys:
            if key not in labels:raise ValueError('Missing Paper IX manuscript label: '+key)
            node=labels[key];kind='Section' if node['kind'] in HEADINGS else KIND_NAMES.get(node['kind'],node['kind'].capitalize())
            result[number].append(dict(key=key,label=kind+' '+node['number'],number=node['number'],kind=node['kind'],title=node['title'],url=node['url']+'#'+node['id']))
    return result


def figure_info(read,receipt):
    name=receipt['name'];alt,description=DESCRIPTIONS[name]
    return dict(receipt=receipt,alt=alt,description=description,
        math_labels=figure_math_labels(read(GENERATOR).decode('utf-8-sig'),name),
        tables=data_tables(name,json.loads(read(EXACT)),json.loads(read(WORKED_DATA))))


def prepare(reader):
    for path in [*SPEC['source_inputs'],SPEC['pdf']]:reader.add(path)
    read=lambda path:reader.site.read_source(reader.records[path])
    for path,sha in SPEC['source_inputs'].items():
        if digest(read(path))!=sha:raise ValueError('Changed Paper IX visual dependency: '+path)
    if digest(read(SPEC['pdf']))!=SPEC['pdf_sha256']:raise ValueError('Changed Paper IX visual PDF')
    selected=sections(read);receipt_raw=(reader.site.root/'website'/RECEIPTS).read_bytes()
    if digest(receipt_raw)!=SPEC['figure_receipts_sha256']:raise ValueError('Changed Paper IX figure extraction receipt')
    receipts=json.loads(receipt_raw)
    if receipts['source_pdf']!=SPEC['pdf'] or receipts['source_pdf_sha256']!=SPEC['pdf_sha256']:
        raise ValueError('Paper IX figure receipts have a different visual PDF')
    figures={}
    for receipt in receipts['figures']:
        name=receipt['name'];binding=SPEC['figures'][name]
        if any(receipt[k]!=v for k,v in binding.items()):raise ValueError('Changed Paper IX figure source')
        reader.add(binding['source'])
        image=(reader.site.root/'website'/receipt['image']).read_bytes()
        if receipt['image']!='assets/atlas/paper-ix/'+name.replace('/','-')+'.png' or digest(image)!=receipt['image_sha256'] or digest(read(binding['source']))!=binding['source_sha256']:
            raise ValueError('Changed Paper IX original drawing')
        if list(png_dimensions(image))!=receipt['dimensions']:raise ValueError('Changed Paper IX image dimensions')
        figures[name]=figure_info(read,receipt)
    if len(receipts['figures'])!=20 or set(figures)!=set(SPEC['figures']):raise ValueError('Incomplete Paper IX figures')
    book=reader.readable_books['paper-ix'];targets=routes(book)
    by_url={chapter.url:chapter for _,_,chapter in book['chapters']}
    for row in selected:
        for target in targets[row['number']]:
            page,anchor=target['url'].split('#')
            by_url[page].related_readings.setdefault(anchor,[]).append(('Visual section '+str(row['number'])+': '+row['title'],row['url']))
    reader.paper_ix_atlas=dict(sections=selected,figures=figures,targets=targets,macros=book['macros'],
        inputs={'generated/worked_newton_values.tex':dict(source=INCLUSION,text=read(INCLUSION).decode('utf-8-sig'))})


def table_markup(table):
    e=html.escape
    body='<div class="table-scroll" tabindex="0" role="region" aria-label="'+e(table['caption'],quote=True)+'"><table><caption>'+e(table['caption'])+'</caption><thead><tr>'
    body+=''.join('<th scope="col">'+e(str(c))+'</th>' for c in table['headers'])+'</tr></thead><tbody>'
    for row in table['rows']:
        body+='<tr>'+''.join(('<th scope="row">' if i==0 else '<td>')+e(str(c))+('</th>' if i==0 else '</td>') for i,c in enumerate(row))+'</tr>'
    return body+'</tbody></table></div>'


def render_figure(figure,chapter,resolve,rel):
    e=html.escape;r=figure['receipt'];image=rel(r['image'],chapter.url)
    body='<figure class="atlas-drawing"><a href="'+image+'" aria-label="Open full-size figure: '+e(figure['alt'],quote=True)+'"><img src="'+image+'" width="'+str(r['dimensions'][0])+'" height="'+str(r['dimensions'][1])+'" alt="'+e(figure['alt'],quote=True)+'" loading="lazy"></a><figcaption>Original figure from the retained vector PDF.</figcaption></figure>'
    body+='<section aria-labelledby="figure-description"><h2 id="figure-description">Reading the figure</h2><p>'+e(figure['description'])+'</p>'
    if figure['math_labels']:
        body+='<h3>Mathematical labels</h3>'+''.join(chapter.paragraphs(label['text']) for label in figure['math_labels'])
    for table in figure['tables']:body+=table_markup(table)
    body+='<details><summary>Selectable labels from the original PDF</summary><p>Native PDF text retains the figure’s extraction order. Equations and data tables above provide the reading order.</p><pre class="figure-labels">'+e(r['native_text'])+'</pre></details>'
    body+='<p><a href="'+resolve(r['source'],chapter.url)+'">Original vector figure PDF</a> · <a href="'+image+'">Full-size image</a></p></section>'
    return body


def chapter_for(row,macros,inputs):
    chapter=AtlasChapter(normalize(row['body']),macros)
    chapter.included_sources=inputs;chapter.url=row['url'];chapter.allow_prose_groups=True
    return chapter


def content(row,chapter,figures,resolve,rel):
    body=''
    for node in chapter.nodes:
        kind,identifier=node['kind'],node['id']
        links='<a href="#'+identifier+'">Permalink</a> · <a href="'+resolve(row['source'],chapter.url,'L'+str(node['line']))+'">Source line '+str(node['line'])+'</a>'
        if r'\input{' in node['body']:links+=' · <a href="'+resolve(INCLUSION,chapter.url)+'">Included exact Newton coefficients</a>'
        if kind=='figure':
            body+='<div id="'+identifier+'">'+render_figure(figures[node['body']],chapter,resolve,rel)+passage_links(links)+'</div>'
        elif kind in {'table','tabular','tabularx'}:
            if row['source']!=BODY or node['line'] not in TABLE_AIDS:raise ValueError('Review Paper IX visual source table')
            body+='<section id="'+identifier+'">'+render_table(node,chapter,TABLE_AIDS[node['line']])+passage_links(links)+'</section>'
        elif kind=='text' or kind in PANELS:
            body+='<section id="'+identifier+'" class="reading-block '+kind+'">'
            if kind in PANELS:body+='<h3>'+chapter.inline(node['title'] or PANELS[kind])+'</h3>'
            body+=chapter.paragraphs(node['body'])+passage_links(links)+'</section>'
        else:raise ValueError('Unsupported Paper IX visual block: '+kind)
    return body


def expected_math(row,figures,inputs):
    text=normalize(row['body'])
    for name,record in inputs.items():text=text.replace(r'\input{'+name+'}',record['text'])
    result=[];position=0
    for match in re.finditer(r'\\begin\{figure\}([^{}]+)\\end\{figure\}',text):
        result+=original_math(text[position:match.start()])
        result+=[m for label in figures[match[1]]['math_labels'] for m in original_math(label['text'])]
        position=match.end()
    return result+original_math(text[position:])


def render(reader):
    atlas=reader.paper_ix_atlas;site=reader.site;selected=atlas['sections'];config=reading_config(selected)
    pdf=reader.records[SPEC['pdf']];reports=[]
    for row in selected:
        number,page=row['number'],row['url'];chapter=chapter_for(row,atlas['macros'],atlas['inputs'])
        title='Paper IX visual guide / '+str(number)+': '+row['title']
        body='<p class="eyebrow">Paper IX visual guide · Section '+str(number)+' of 23</p><h1>'+html.escape(row['title'])+'</h1>'
        body+=reader.work_routes('paper-ix',page)+navigation(config,page)
        body+='<nav class="document-routes" aria-label="Related manuscript passages">'+''.join('<a href="'+site.rel(t['url'],page)+'">'+html.escape(t['label'])+'</a>' for t in atlas['targets'][number])+'</nav>'
        tools='<p><a href="'+reader.viewer_url(pdf,page,'page='+str(number+2))+'">Original section in the visual-guide PDF</a> · <a href="'+reader.resolve(row['source'],page,'L'+str(row['start_line']))+'">Original visual source</a></p>'
        body+=resources(tools+reading_options('Show each passage’s permalink and original source line.'))+'<p class="reading-start"><a href="#chapter-text">Start reading</a></p>'
        toc='<nav class="chapter-contents" aria-label="Section contents"><h2>On this page</h2><ul>'
        for node in chapter.nodes:
            label='Figure, description and selectable labels' if node['kind']=='figure' else 'Source table' if node['kind'] in {'table','tabular','tabularx'} else node['title'] or 'Passage at source line '+str(node['line'])
            toc+='<li><a href="#'+node['id']+'">'+html.escape(label)+'</a></li>'
        body+=outline(toc+'</ul></nav>')+'<article id="chapter-text" class="readable-chapter atlas-plate" aria-label="'+html.escape(title,quote=True)+'">'
        body+=content(row,chapter,atlas['figures'],reader.resolve,site.rel)+'</article>'+navigation(config,page,'bottom')
        body+='<details class="document-provenance"><summary>Source and conversion record</summary><p>The full edition has 23 sections and 20 figures, including eight worked examples. The older visual README describes 15 sections and 12 figures. Original wording, equations and finite-check scope are retained. Descriptions and data tables are reading aids. This conversion renders existing figure PDFs without rebuilding TeX, running the mathematical generators, auditing proofs or compiling Lean.</p><p><a href="'+site.rel(REPORT,page)+'">Source hashes and conversion checks</a></p></details>'
        expected=expected_math(row,atlas['figures'],atlas['inputs'])
        if chapter.math!=expected:raise ValueError('Paper IX visual mathematical sequence changed in section '+str(number))
        site.page(page,title,body)
        site.search.append(dict(title=title,group='Collection',kind='Papers and source',work_ids=['paper-ix'],url=page,text=row['title']+' '+row['body']))
        reports.append(dict(number=number,url=page,source=row['source'],start_line=row['start_line'],end_line=row['end_line'],math_expressions=len(expected),math_sequence_sha256=digest(json.dumps(expected,ensure_ascii=False).encode()),nodes=[{k:n[k] for k in ('kind','id','line','end_line')} for n in chapter.nodes]))
    record=dict(collection_revision=site.revision,source_inputs=SPEC['source_inputs'],source_pdf=SPEC['pdf'],source_pdf_sha256=SPEC['pdf_sha256'],
        index=INDEX,total_sections=23,html_sections=reports,figures=atlas['figures'],macros=atlas['macros'],manuscript_references=atlas['targets'],
        inherited_readme_inventory=dict(sections=15,figures=12,current=False),new_proof_review=False,new_lean_execution=False,new_mathematical_example_execution=False,new_tex_build=False)
    site.write(REPORT,json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    body='<p class="eyebrow">Paper IX · Euler Congruences</p><h1>Explore the 23 visual sections</h1><p>Read the complete guide to congruences and sharp dyadic geometry, followed by eight worked arithmetic and lifting examples. All 20 original figures have descriptions and selectable labels; recorded data are available in accessible tables.</p>'+reader.work_routes('paper-ix',INDEX)
    body+='<p>This guide explains the indexing, valuation gains, exact periods, and remaining boundaries through exact arithmetic and theorem-derived figures. The main paper supplies the proofs; the Lean companion supplies the formal source and evidence map.</p>'
    for first,last,heading in [(1,15,'Congruences and dyadic geometry'),(16,23,'Worked arithmetic and lifting')]:
        body+='<section><h2>'+heading+'</h2><ol start="'+str(first)+'">'
        for row in selected[first-1:last]:
            body+='<li id="s'+str(row['number']).zfill(2)+'"><a href="'+site.rel(row['url'],INDEX)+'">'+html.escape(row['title'])+'</a> · <a href="'+reader.viewer_url(pdf,INDEX,'page='+str(row['number']+2))+'">PDF section '+str(row['number'])+'</a></li>'
        body+='</ol></section>'
    body+='<p><a href="'+reader.resolve(SOURCE,INDEX)+'">Original visual entrypoint</a> · <a href="'+site.rel(REPORT,INDEX)+'">Conversion record</a></p>'
    site.page(INDEX,'Paper IX visual guide',body)
    site.search.append(dict(title='Paper IX / Visual guide: 23 sections',group='Collection',kind='Papers and source',work_ids=['paper-ix'],url=INDEX,text=' '.join(r['title'] for r in selected)))


def verify(root,documents,pages):
    from check_reader_site import check_png_image_sizes
    from reading_navigation import Navigation,neighbours
    report=json.loads((root/REPORT).read_bytes());records={r['repository_path']:r for r in documents['files']}
    read=lambda path:(root/records[path]['file_url']).read_bytes()
    assert report['source_inputs']==SPEC['source_inputs']
    for path,sha in SPEC['source_inputs'].items():assert digest(read(path))==sha
    assert report['collection_revision']==documents['source_revision']
    assert report['source_pdf']==SPEC['pdf'] and report['source_pdf_sha256']==digest(read(SPEC['pdf']))==SPEC['pdf_sha256']
    assert report['index']==INDEX and report['total_sections']==len(report['html_sections'])==23
    assert report['inherited_readme_inventory']==dict(sections=15,figures=12,current=False)
    assert not any(report[k] for k in ('new_proof_review','new_lean_execution','new_mathematical_example_execution','new_tex_build'))
    selected=sections(read);book=manuscript_book(read);targets=routes(book);macros=book['macros']
    assert report['macros']==macros
    assert report['manuscript_references']=={str(n):r for n,r in targets.items()}
    receipt_raw=(root/RECEIPTS).read_bytes();assert digest(receipt_raw)==SPEC['figure_receipts_sha256']
    receipts=json.loads(receipt_raw);figures={}
    assert (receipts['source_pdf'],receipts['source_pdf_sha256'])==(SPEC['pdf'],SPEC['pdf_sha256'])
    assert len(receipts['figures'])==20
    for receipt in receipts['figures']:
        name=receipt['name'];binding=SPEC['figures'][name]
        assert all(receipt[k]==v for k,v in binding.items())
        assert receipt['image']=='assets/atlas/paper-ix/'+name.replace('/','-')+'.png'
        assert digest(read(binding['source']))==binding['source_sha256']
        raw=(root/receipt['image']).read_bytes()
        assert digest(raw)==receipt['image_sha256'] and list(png_dimensions(raw))==receipt['dimensions']
        figures[name]=figure_info(read,receipt)
    # JSON-normalize tuples from projections before comparing saved records.
    assert report['figures']==json.loads(json.dumps(figures)) and set(figures)==set(SPEC['figures'])
    inputs={'generated/worked_newton_values.tex':dict(source=INCLUSION,text=read(INCLUSION).decode('utf-8-sig'))}
    config=reading_config(selected);count=returns=0
    def resolve(path,page,anchor=None):return posixpath.relpath(records[path]['url'],posixpath.dirname(page))+('#'+anchor if anchor else '')
    rel=lambda path,page:posixpath.relpath(path,posixpath.dirname(page))
    for row,binding in zip(selected,report['html_sections']):
        chapter=chapter_for(row,macros,inputs);markup=(root/row['url']).read_text(encoding='utf-8')
        expected_content=content(row,chapter,figures,resolve,rel)
        assert expected_content in markup,('Changed visual prose, figure transcript or source table',row['number'])
        expected=expected_math(row,figures,inputs);assert chapter.math==expected
        actual=[html.unescape(t) for t in re.findall(r'<(?:span|div) class="arithmatex"[^>]*>(.*?)</(?:span|div)>',markup,re.S)]
        assert actual==[(r'\[' if t.startswith(r'\[') else r'\(')+expand_math(m,macros)+(r'\]' if t.startswith(r'\[') else r'\)') for t,m in zip(actual,expected)] and len(actual)==len(expected)
        assert binding==dict(number=row['number'],url=row['url'],source=row['source'],start_line=row['start_line'],end_line=row['end_line'],math_expressions=len(expected),math_sequence_sha256=digest(json.dumps(expected,ensure_ascii=False).encode()),nodes=[{k:n[k] for k in ('kind','id','line','end_line')} for n in chapter.nodes])
        check_png_image_sizes(root,row['url'],pages[row['url']].images)
        for node in chapter.nodes:
            assert node['id'] in pages[row['url']].ids
            assert 'L'+str(node['line']) in pages[records[row['source']]['url']].ids
        for target in targets[row['number']]:
            page,anchor=target['url'].split('#');assert anchor in pages[page].ids
            assert rel(target['url'],row['url']) in pages[row['url']].links
            assert rel(row['url'],page) in pages[page].links
            returns+=1
        controls=Navigation(markup).controls;assert len(controls)==2
        _,position,previous,following=neighbours(config,row['url'])
        for control in controls:
            assert control['attrs']['data-reading-position']==str(position+1)
            assert control['attrs']['data-reading-total']=='23'
            assert [a['href'] for a in control['links'] if 'data-reading-entry' in a]==[rel(r['url'],row['url']) for r in selected]
            for direction,target in [('previous',previous),('next',following)]:
                assert [a['href'] for a in control['links'] if 'reading-'+direction in a.get('class','').split()]==[rel(target['url'],row['url'])]
        count+=len(expected)
    assert all('s'+str(n).zfill(2) in pages[INDEX].ids for n in range(1,24))
    return dict(total_sections=23,html_sections=23,drawings=20,source_tables=6,math_expressions=count,return_links=returns)


ATLAS=SimpleNamespace(BOOK=BOOK,PDF=SPEC['pdf'],REPORT=REPORT,INDEX=INDEX,prepare=prepare,render=render,verify=verify)
