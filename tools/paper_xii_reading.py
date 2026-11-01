"""Source-bound Paper XII monograph, reading map and revision record."""
import hashlib
import html
import json
from pathlib import Path
import re

WORK='paper-xii'
ROOT='papers/paper-xii/current/core/'
BASE=ROOT+'publication/source/traditional/'
MAIN=BASE+'Paper_XII_Traditional_Final.tex'
BIB=BASE+'Paper_XII_Traditional_Final.bbl'
BIB_SOURCE=BASE+'Paper_XII_Traditional_Final.bib'
CONCORDANCE=ROOT+'READING_CONCORDANCE.md'
PREFIX='read/paper-xii/'
BIB_RECORD='documents/paper-xii-bibliography.json'
CHAPTERS=json.loads(Path(__file__).with_name('paper_xii_sections.json').read_text(encoding='utf-8'))
BOOK=dict(work=WORK,label='Paper XII',base=BASE,main=MAIN,bib=BIB,inline_bibliography=True,
    index=PREFIX+'index.html',bib_page=PREFIX+'references.html',chapters=CHAPTERS,
    title='Patching Support, Hecke Packets, and Conditional Automorphic Completion',main_chapters=13,
    custom_reader='paper_xii',number_floats=True,statement_navigation=True,
    figure_receipts='assets/figures/paper-xii/figures.json',
    required_macros=['OO','FF','QQ','ZZ','TT','Spec','Supp','wideotimes'],
    require_table_reading_aids=True,
    reading_introduction='Read all 13 main sections, the reading map and the complete verification '
        'and revision record. The algebraic results retain their supplied arithmetic hypotheses '
        'and conditional conclusions. The visual and Lean companions remain available in PDF.')
BOOK['table_reading_aids']={
    ('reading_route.tex','L7'):dict(caption='Reading routes through the three companions',
        headers=['Topic','Main statement','Visual','Lean section'],row_header_column=0),
    ('Paper_XII_Traditional_Final.tex','L1775'):dict(
        headers=['Proved in this article','Not proved in this article'],row_header_column=0),
}


def mask(text):return ''.join('\n' if c=='\n' else ' ' for c in text)


def normalize(source):
    """Translate reviewed print controls without moving source-line anchors."""
    from readable_chapters import clean_tex,group
    text=clean_tex(source);count=text.count('\n')
    text=re.sub(r'\\input\{reading_route\.tex\}|\\bibliography\{Paper_XII_Traditional_Final\}',lambda m:mask(m[0]),text)
    text=re.sub(r'\\makeatletter\\@setabstract\\makeatother|\\thispagestyle\{plain\}',lambda m:mask(m[0]),text)
    text=re.sub(r'\\pdfbookmark\[0\]\{Reading map and evidence boundary\}\{release-map\}',lambda m:mask(m[0]),text)
    while match:=re.search(r'\\texorpdfstring\{',text):
        value,end=group(text,match.end()-1);_,stop=group(text,end)
        text=text[:match.start()]+mask(text[match.start():match.end()])+value+mask(text[end-1:stop])+text[stop:]
    text=text.replace(r'\bysame','—').replace(r'\textendash','–')
    if text.count('\n')!=count:raise ValueError('Paper XII translation moved source lines')
    return text


def source_math(source,spec):
    from readable_chapters import chapter_text,original_math
    return original_math(normalize(chapter_text(source,spec)))


def source_specs(load):
    from readable_chapters import clean_tex
    body=clean_tex(load(MAIN)).split(r'\begin{document}',1)[1]
    if re.findall(r'\\input\{([^{}]+)\}',body)!=['reading_route.tex']:raise ValueError('Review Paper XII manuscript input order')
    if re.findall(r'\\bibliography\{([^{}]+)\}',body)!=['Paper_XII_Traditional_Final']:raise ValueError('Review Paper XII bibliography route')
    if {s['source'] for s in CHAPTERS}!={MAIN,BASE+'reading_route.tex'}:raise ValueError('Review Paper XII source coverage')
    specs=[s for s in CHAPTERS if s['source']==MAIN];lines=load(MAIN).splitlines()
    if lines[specs[0]['start_line']-1]!=r'\begin{document}' or lines[specs[-1]['end_line']-1]!=r'\end{document}':raise ValueError('Review Paper XII document boundaries')
    for a,b in zip(specs,specs[1:]):
        if a['end_line']+1!=b['start_line']:raise ValueError('Paper XII source ranges have a gap or overlap')
    return CHAPTERS


def companion_routes(load):
    routes={}
    for match in re.finditer(r'^\| ([^|]+) \| [^|]+ \| (Paper_XII_[^| ]+\.pdf) / (\d+) \|',load(CONCORDANCE),re.M):
        routes['p12-route:'+match[1]]=(ROOT+'publication/pdfs/'+match[2],int(match[3]))
    if len(routes)!=94:raise ValueError('Review Paper XII companion concordance')
    return routes


def prepare_book(reader,config):
    import readable_chapters as reading
    def load(path):
        record=reader.add(path)
        if not record:raise ValueError('Missing receipt-bound Paper XII source: '+path)
        return reader.site.read_source(record).decode('utf-8-sig')
    source_specs(load);main=load(MAIN);macros=reading.manuscript_macros(main,config['required_macros'])
    refs=reading.manuscript_bibliography(load(BIB));bib=reading.bibliography(load(BIB_SOURCE))
    if len(refs)!=27 or {r['key'] for r in refs}!={r['key'] for r in bib}:raise ValueError('Review Paper XII bibliography inventory')
    routes=companion_routes(load)
    titles={'Paper_XII_Traditional_v1.0.0.pdf':'Read PDF','Paper_XII_Visual_Guide_v1.0.0.pdf':'Visual guide (PDF)','Paper_XII_Lean_Guide_v1.0.0.pdf':'Lean and evidence guide (PDF)'}
    for path in sorted({path for path,_ in routes.values()}):reader.add(path,titles[Path(path).name])
    chapters=[];labels={};state={'number_floats':True}
    for spec in config['chapters']:
        raw=reader.site.read_source(reader.add(spec['source']));text=reading.chapter_text(raw.decode('utf-8-sig'),spec)
        chapter=reading.Chapter(normalize(text),macros,state=state,check_refs=False)
        chapter.allow_prose_groups=True;chapter.url=spec['url'];chapter.base=BASE;chapter.bibliography_url=config['bib_page']
        hrefs=re.findall(r'\\href\{([^{}]+)\}',text)
        chapter.href_targets={url:reader.resolve(routes[url][0],chapter.url,'page='+str(routes[url][1])) for url in hrefs if url.startswith('p12-route:')}
        for node in chapter.nodes:
            if node['kind']=='section' and node['number']=='7':node['toc_title']='Transport through an isomorphism R equals T'
        for key,node in chapter.labels.items():
            if key in labels:raise ValueError('Repeated Paper XII source label: '+key)
            node['url']=chapter.url;labels[key]=dict(node)
        state={key:getattr(chapter,key) for key in ('section','appendix','part','subsection','subsubsection','counter','section_prefix','figure','table','number_floats')}
        chapters.append((spec,raw,chapter))
    for spec,raw,chapter in chapters:
        chapter.labels=labels;chapter.validate_references()
        chapter.citations={r['key']:(str(i),chapter.relative(config['bib_page'])+'#ref-'+r['key']) for i,r in enumerate(refs,1)}
        nodes={n['line']:n for n in chapter.nodes}
        for row in reading.chapter_claims(reader,spec):
            if row['statement_line'] not in nodes:raise ValueError('Missing Paper XII statement')
            if row['proof_line'] and nodes.get(row['proof_line'],{}).get('kind')!='proof':raise ValueError('Missing Paper XII proof')
    from reader_figure_assets import prepare
    return dict(config=config,chapters=chapters,references=refs,macros=macros,main=main,figure_assets=prepare(reader,config,chapters))


def render_bibliography(reader,book):
    from readable_chapters import Chapter,original_math
    from reading_navigation import navigation,resources,work_links
    config=book['config'];site=reader.site;page=config['bib_page']
    parser=Chapter('',book['macros']);parser.url=page;parser.allow_prose_groups=True
    body='<h1>Paper XII bibliography</h1>'+navigation(config,page)+resources(work_links(reader,WORK,page))
    body+='<article id="chapter-text" class="reading-bibliography"><p>All 27 entries retain the published order and citation numbers.</p>'
    for i,entry in enumerate(book['references'],1):
        body+='<section id="ref-'+entry['key']+'"><h2>['+str(i)+'] '+html.escape(entry['key'])+'</h2>'
        body+=parser.paragraphs(normalize(entry['body']))
        body+='<p><a href="'+reader.resolve(BIB,page,'L'+str(entry['line']))+'">Original bibliography entry</a></p></section>'
    body+='</article>'+navigation(config,page,'bottom');site.page(page,'Paper XII bibliography',body)
    expected=original_math(normalize(reader.site.read_source(reader.records[BIB]).decode('utf-8-sig')))
    if parser.math!=expected:raise ValueError('Paper XII bibliography math differs from its source')
    site.write(BIB_RECORD,json.dumps(dict(source=BIB,source_sha256=reader.records[BIB]['sha256'],references=[{k:e[k] for k in ('key','line')} for e in book['references']],math=expected,new_proof_review=False,new_lean_execution=False),ensure_ascii=False,indent=2)+'\n')
    site.search.append(dict(title='Paper XII / Bibliography',group='Collection',kind='Papers and source',work_ids=[WORK],url=page,text=' '.join(e['key']+' '+e['body'] for e in book['references'])))


def verify_bibliography(root,documents,pages):
    from readable_chapters import expand_math,original_math,manuscript_bibliography,manuscript_macros
    sources={r['repository_path']:r for r in documents['files']}
    def load(path):return (root/sources[path]['file_url']).read_text(encoding='utf-8-sig')
    record=json.loads((root/BIB_RECORD).read_bytes());expected=original_math(normalize(load(BIB)))
    assert record['source']==BIB and record['source_sha256']==hashlib.sha256((root/sources[BIB]['file_url']).read_bytes()).hexdigest()
    assert record['math']==expected and not record['new_proof_review'] and not record['new_lean_execution']
    refs=manuscript_bibliography(load(BIB));assert record['references']==[{k:e[k] for k in ('key','line')} for e in refs]
    for entry in refs:assert 'ref-'+entry['key'] in pages[BOOK['bib_page']].ids
    markup=(root/BOOK['bib_page']).read_text(encoding='utf-8');actual=[html.unescape(x) for x in re.findall(r'<(?:span|div) class="arithmatex"[^>]*>(.*?)</(?:span|div)>',markup,re.S)]
    macros=manuscript_macros(load(MAIN),BOOK['required_macros']);assert actual==[r'\('+expand_math(x,macros)+r'\)' for x in expected]
    return dict(entries=len(refs),math_expressions=len(expected))
