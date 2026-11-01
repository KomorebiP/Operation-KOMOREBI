"""Complete source-bound Paper XI monograph and fifteen construction appendices."""
import hashlib
import html
import json
from pathlib import Path
import re

WORK='paper-xi'
ROOT='papers/paper-xi/current/'
BASE=ROOT+'publication/source/traditional/'
MAIN=BASE+'Paper_XI_Traditional_Final.tex'
BIB=ROOT+'verification/publication/traditional/Paper_XI_Traditional_Final.bbl'
BIB_SOURCE=BASE+'Paper_XI_Traditional_Final.bib'
AUX=ROOT+'verification/publication/traditional/Paper_XI_Traditional_Final.aux'
CONCORDANCE=ROOT+'READING_CONCORDANCE.md'
PREFIX='read/paper-xi/'
BIB_RECORD='documents/paper-xi-bibliography.json'
CHAPTERS=json.loads(Path(__file__).with_name('paper_xi_sections.json').read_text(encoding='utf-8'))
INPUTS=['reader_route']+['appendices/'+Path(s['source']).stem for s in CHAPTERS if '/appendices/' in s['source']]
BOOK=dict(work=WORK,label='Paper XI',base=BASE,main=MAIN,bib=BIB,inline_bibliography=True,
    index=PREFIX+'index.html',bib_page=PREFIX+'references.html',chapters=CHAPTERS,
    title='Tame and Wild Packet Geometry for Local Langlands',main_chapters=19,
    custom_reader='paper_xi',number_floats=True,statement_navigation=True,literal_derivations=True,
    figure_receipts='assets/figures/paper-xi/figures.json',
    required_macros=['CC','FF','ZZ','QQ','OO','GL','calH','one'],
    require_table_reading_aids=True,
    reading_introduction='Read all 19 main sections and all fifteen detailed construction appendices. '
        'The reader routes preserve the distinction between proved finite theory, restricted arithmetic '
        'constructions and the open Conjecture 66. The visual, Lean and research companions remain in PDF.')
BOOK['table_reading_aids']={
    ('reader_route.tex','L8'):dict(caption='Five readers with different jobs',headers=['Reader','Route and purpose'],row_header_column=0),
    ('reader_route.tex','L28'):dict(caption='Current scope and research routes',headers=['Question','Route beyond the core statement'],row_header_column=0),
    ('appendices/stabilizer_contract.tex','L215'):dict(caption='Three stabilizer-action contracts',headers=['Given contract','Exact remaining issue'],row_header_column=0),
    ('appendices/dyadic_synthesis.tex','L141'):dict(caption='Dyadic whole-profile capacity',headers=['Ambient rank','Host quotient dimension','Host Heisenberg carrier','Required source carrier','Outcome'],row_header_column=0),
    ('appendices/dyadic_capacity.tex','L53'):dict(caption='Exact dyadic capacity and low-rank limits',headers=['d','Ambient rank','Actual quotient dimension','eta dimension','Source carrier dimension','Capacity'],row_header_column=0),
}


def mask(text):return ''.join('\n' if c=='\n' else ' ' for c in text)


def normalize(source):
    """Keep literal derivations intact while translating reviewed Pandoc layout."""
    from readable_chapters import clean_tex,group
    count=source.count('\n')
    text=source.replace(r'\begin{Verbatim}[fontsize=\small,breaklines=true,breakanywhere=true]',r'\begin{verbatim}').replace(r'\end{Verbatim}',r'\end{verbatim}')
    parts=re.split(r'(\\begin\{verbatim\}.*?\\end\{verbatim\})',text,flags=re.S)
    for i in range(0,len(parts),2):
        text=clean_tex(parts[i])
        while match:=re.search(r'\\hypertarget\{',text):
            start=match.start();_,end=group(text,start+len(r'\hypertarget'));body,stop=group(text,end)
            text=text[:start]+mask(text[start:end+1])+body+' '+text[stop:]
        text=re.sub(r'\\input\{(?:'+ '|'.join(re.escape(p) for p in INPUTS)+r')\}',lambda m:mask(m[0]),text)
        text=re.sub(r'\\bibliography\{Paper_XI_Traditional_Final\}',lambda m:mask(m[0]),text)
        text=re.sub(r'\\special\{pdf:trailerid \[<[^>]+><[^>]+>\]\}',lambda m:mask(m[0]),text)
        text=re.sub(r'\\makeatletter\\@setabstract\\makeatother|\\thispagestyle\{plain\}|\\setcounter\{tocdepth\}\{1\}|\\renewcommand\{\\theconjecture\}\{66\}',lambda m:mask(m[0]),text)
        text=re.sub(r'\\def\\labelenumi\{\\arabic\{enumi\}\.\}',lambda m:mask(m[0]),text)
        text=re.sub(r'\\(?:tightlist|phantomsection)\b',lambda m:mask(m[0]),text)
        text=re.sub(r'\\begin\{minipage\}\[b\]\{\\linewidth\}|\\end\{minipage\}|\\noalign\{\}',lambda m:mask(m[0]),text)
        for spacing in ('7pt','8pt'):text=text.replace(r'\\['+spacing+']',r'\\')
        text=text.replace(r'\textless','<').replace(r'\textgreater','>').replace(r'\textbar','|').replace(r'\^{}','^')
        text=text.replace(r'\bysame','—')
        parts[i]=text
    result=''.join(parts)
    if result.count('\n')!=count:raise ValueError('Paper XI translation moved source lines')
    return result


def source_math(source,spec):
    from readable_chapters import chapter_text,original_math
    return original_math(normalize(chapter_text(source,spec)))


def source_specs(load):
    from readable_chapters import clean_tex
    body=clean_tex(load(MAIN)).split(r'\begin{document}',1)[1]
    if re.findall(r'\\input\{([^{}]+)\}',body)!=INPUTS:raise ValueError('Review Paper XI manuscript input order')
    if re.findall(r'\\bibliography\{([^{}]+)\}',body)!=['Paper_XI_Traditional_Final']:raise ValueError('Review Paper XI bibliography route')
    if list(dict.fromkeys(s['source'] for s in CHAPTERS if s['source']!=MAIN))!=[BASE+p+'.tex' for p in INPUTS]:
        raise ValueError('Review Paper XI included chapter order')
    for path in {s['source'] for s in CHAPTERS}:
        specs=[s for s in CHAPTERS if s['source']==path];lines=load(path).splitlines()
        if path==MAIN:
            if lines[specs[0]['start_line']-1]!=r'\begin{document}' or lines[specs[-1]['end_line']-1]!=r'\end{document}':
                raise ValueError('Review Paper XI document boundaries')
        elif 'start_line' not in specs[0]:continue
        elif specs[0]['start_line']!=1 or specs[-1]['end_line']!=len(lines):raise ValueError('Review Paper XI source coverage')
        for a,b in zip(specs,specs[1:]):
            if a['end_line']+1!=b['start_line']:raise ValueError('Paper XI source ranges have a gap or overlap')
    return CHAPTERS


def companion_routes(load):
    routes={}
    for match in re.finditer(r'^\| `([^`]+)` \| \[[^\]]+\]\((publication/pdfs/[^)#]+)#page=(\d+)\)',load(CONCORDANCE),re.M):
        routes['https://komorebi.invalid/b07/'+match[1]]=(ROOT+match[2],int(match[3]))
    if len(routes)!=107:raise ValueError('Review Paper XI companion concordance')
    return routes


def prepare_book(reader,config):
    import readable_chapters as reading
    def load(path):
        record=reader.add(path)
        if not record:raise ValueError('Missing receipt-bound Paper XI source: '+path)
        return reader.site.read_source(record).decode('utf-8-sig')
    source_specs(load);main=load(MAIN)
    macros=reading.manuscript_macros(main,config['required_macros'])
    refs=reading.manuscript_bibliography(load(BIB));bib=reading.bibliography(load(BIB_SOURCE))
    if len(refs)!=29 or {r['key'] for r in refs}!={r['key'] for r in bib}:raise ValueError('Review Paper XI bibliography inventory')
    printed=dict(re.findall(r'\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}',load(AUX)))
    routes=companion_routes(load)
    titles={'Paper_XI_Traditional_v1.1.0.pdf':'Read PDF',
        'Paper_XI_Visual_Guide_v1.1.0.pdf':'Core visual guide (PDF)',
        'Paper_XI_Lean_Guide_v1.1.0.pdf':'Lean and evidence guide (PDF)',
        'Paper_XI_Conjecture66_Progress_v0.4.0.pdf':'Conjecture 66 progress paper (PDF)',
        'Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf':'Conjecture 66 visual atlas (PDF)'}
    for path in sorted({path for path,_ in routes.values()}):reader.add(path,titles[Path(path).name])
    chapters=[];labels={};state={'number_floats':True}
    for spec in config['chapters']:
        raw=reader.site.read_source(reader.add(spec['source']));text=reading.chapter_text(raw.decode('utf-8-sig'),spec)
        if spec.get('heading'):
            kind,title=spec['heading']
            if not re.search(r'\\'+kind+r'\*?\{'+re.escape(title)+r'\}',text):raise ValueError('Review Paper XI chapter boundary')
        chapter=reading.Chapter(normalize(text),macros,state=state,check_refs=False)
        chapter.allow_prose_groups=True
        chapter.literal_listing_label='Original literal derivation'
        chapter.url=spec['url'];chapter.base=BASE;chapter.bibliography_url=config['bib_page']
        hrefs=re.findall(r'\\href\{([^{}]+)\}',text)
        chapter.href_targets={url:reader.resolve(routes[url][0],chapter.url,'page='+str(routes[url][1]))
            for url in hrefs if url.startswith('https://komorebi.invalid/b07/')}
        for key,node in chapter.labels.items():
            if key in labels:raise ValueError('Repeated Paper XI source label: '+key)
            node['url']=chapter.url
            if key in printed and node['kind'] in reading.NUMBERED|set(reading.HEADINGS)|{'figure','table'}:node['number']=printed[key]
            labels[key]=dict(node)
        state={key:getattr(chapter,key) for key in ('section','appendix','part','subsection','subsubsection','counter','section_prefix','figure','table','number_floats')}
        chapters.append((spec,raw,chapter))
    for spec,raw,chapter in chapters:
        chapter.labels=labels;chapter.validate_references()
        chapter.citations={r['key']:(str(i),chapter.relative(config['bib_page'])+'#ref-'+r['key']) for i,r in enumerate(refs,1)}
        nodes={n['line']:n for n in chapter.nodes}
        for row in reading.chapter_claims(reader,spec):
            if row['statement_line'] not in nodes:raise ValueError('Missing Paper XI statement')
            if row['proof_line'] and nodes.get(row['proof_line'],{}).get('kind')!='proof':raise ValueError('Missing Paper XI proof')
    from reader_figure_assets import prepare
    return dict(config=config,chapters=chapters,references=refs,macros=macros,main=main,figure_assets=prepare(reader,config,chapters))


def render_bibliography(reader,book):
    from readable_chapters import Chapter,original_math
    from reading_navigation import navigation,resources,work_links
    config=book['config'];site=reader.site;page=config['bib_page']
    parser=Chapter('',book['macros']);parser.url=page;parser.allow_prose_groups=True
    body='<h1>Paper XI bibliography</h1>'+navigation(config,page)+resources(work_links(reader,WORK,page))
    body+='<article id="chapter-text" class="reading-bibliography"><p>All 29 entries retain the published order and citation numbers. An em dash retains the bibliography’s repeated-author convention.</p>'
    for i,entry in enumerate(book['references'],1):
        body+='<section id="ref-'+entry['key']+'"><h2>['+str(i)+'] '+html.escape(entry['key'])+'</h2>'
        body+=parser.paragraphs(normalize(entry['body']))
        body+='<p><a href="'+reader.resolve(BIB,page,'L'+str(entry['line']))+'">Original bibliography entry</a></p></section>'
    body+='</article>'+navigation(config,page,'bottom');site.page(page,'Paper XI bibliography',body)
    expected=original_math(normalize(reader.site.read_source(reader.records[BIB]).decode('utf-8-sig')))
    if parser.math!=expected:raise ValueError('Paper XI bibliography math differs from its source')
    site.write(BIB_RECORD,json.dumps(dict(source=BIB,source_sha256=reader.records[BIB]['sha256'],references=[{k:e[k] for k in ('key','line')} for e in book['references']],math=expected,new_proof_review=False,new_lean_execution=False),ensure_ascii=False,indent=2)+'\n')
    site.search.append(dict(title='Paper XI / Bibliography',group='Collection',kind='Papers and source',work_ids=[WORK],url=page,text=' '.join(e['key']+' '+e['body'] for e in book['references'])))


def verify_bibliography(root,documents,pages):
    from readable_chapters import expand_math,original_math,manuscript_bibliography,manuscript_macros
    sources={r['repository_path']:r for r in documents['files']}
    def load(path):return (root/sources[path]['file_url']).read_text(encoding='utf-8-sig')
    record=json.loads((root/BIB_RECORD).read_bytes());expected=original_math(normalize(load(BIB)))
    assert record['source']==BIB and record['source_sha256']==hashlib.sha256((root/sources[BIB]['file_url']).read_bytes()).hexdigest()
    assert record['math']==expected and not record['new_proof_review'] and not record['new_lean_execution']
    refs=manuscript_bibliography(load(BIB));assert record['references']==[{k:e[k] for k in ('key','line')} for e in refs]
    for entry in refs:assert 'ref-'+entry['key'] in pages[BOOK['bib_page']].ids
    markup=(root/BOOK['bib_page']).read_text(encoding='utf-8')
    actual=[html.unescape(x) for x in re.findall(r'<(?:span|div) class="arithmatex"[^>]*>(.*?)</(?:span|div)>',markup,re.S)]
    macros=manuscript_macros(load(MAIN),BOOK['required_macros'])
    assert actual==[r'\('+expand_math(x,macros)+r'\)' for x in expected]
    return dict(entries=len(refs),math_expressions=len(expected))
