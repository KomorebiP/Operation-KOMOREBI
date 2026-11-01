"""Complete source-bound Paper IX reading route, including dated appendices."""
import html
import hashlib
import json
from pathlib import Path
import re
import posixpath

WORK='paper-ix'
BASE='papers/paper-ix/current/sources/main/'
MAIN=BASE+'Paper_IX_Traditional_Final.tex'
PREFIX='read/paper-ix/'
AUX='papers/paper-ix/current/publication/build/Paper_IX_Euler_Main_Final/Paper_IX_Euler_Main_Final.aux'
HISTORICAL_BIB=BASE+'historical_references.tex'
BIB_RECORD='documents/paper-ix-bibliography.json'
CHAPTERS=json.loads(Path(__file__).with_name('paper_ix_sections.json').read_text(encoding='utf-8'))
BOOK=dict(work=WORK,label='Paper IX',base=BASE,main=MAIN,bib=MAIN,inline_bibliography=True,
    index=PREFIX+'index.html',bib_page=PREFIX+'references.html',title='Euler Congruences',
    chapters=CHAPTERS,main_chapters=13,custom_reader='paper_ix',number_floats=True,
    required_macros={'N','Z','Q','F','Zp','Qp'},statement_navigation=True,
    require_table_reading_aids=True,table_reading_aids={},
    reading_introduction='Read the complete arithmetic and strengthening chapters, the lifting and analytic '
        'development, and all five mathematical appendices. Historical checkpoints retain their dated scope. '
        'The worked visual atlas remains in the complete PDF.')
_table_path=Path(__file__).with_name('paper_ix_tables.json')
if _table_path.is_file():
    BOOK['table_reading_aids']={(r['source'].removeprefix(BASE),r['id']):
        {k:v for k,v in r.items() if k not in {'source','id'}} for r in json.loads(_table_path.read_text(encoding='utf-8'))}


def register(books,chapters):
    books[WORK]=BOOK
    chapters.extend(CHAPTERS)


def mask(text): return ''.join('\n' if c=='\n' else ' ' for c in text)


def normalize(source):
    """Translate reviewed print/Pandoc wrappers without moving source lines."""
    from readable_chapters import clean_tex,group
    text=clean_tex(source)
    count=text.count('\n')
    position=0
    while match:=re.search(r'\\hypertarget\{',text[position:]):
        start=position+match.start(); _,end=group(text,start+len(r'\hypertarget'))
        body,stop=group(text,end)
        text=text[:start]+mask(text[start:end+1])+body+' '+text[stop:]
        position=start
    text=re.sub(r'\\def\\labelenumi\{\\arabic\{enumi\}\.\}',lambda m:mask(m[0]),text)
    text=re.sub(r'\\(?:tightlist|relax|smallskip|bigskip|protect|leavevmode|ignorespaces|unskip|footnotesize|allowbreak)\b',lambda m:mask(m[0]),text)
    while match:=re.search(r'\\pageheading\{',text):
        title,end=group(text,match.end()-1);subtitle,stop=group(text,end)
        original=text[match.start():stop]
        replacement=r'\subsubsection*{'+title+'} '+subtitle
        replacement+='\n'*(original.count('\n')-replacement.count('\n'))
        text=text[:match.start()]+replacement+text[stop:]
    text=text.replace(',height=3.15in,keepaspectratio','')
    for spacing in ('0pt','2pt','3pt','4pt'):
        text=text.replace(r'\\['+spacing+']',r'\\')
    text=text.replace(r'\begin{tabularx}{\linewidth}',r'\begin{tabularx}{\textwidth}')
    text=re.sub(r'\\begin\{minipage\}\[b\]\{\\linewidth\}|\\end\{minipage\}|\\noalign\{\}',lambda m:mask(m[0]),text)
    for name,inner in [('equation',None),('equation*',None),('align','aligned'),('gather','gathered')]:
        text=text.replace(r'\begin{'+name+'}',r'\['+(r'\begin{'+inner+'}' if inner else ''))
        text=text.replace(r'\end{'+name+'}',(r'\end{'+inner+'}' if inner else '')+r'\]')
    if text.count('\n')!=count:raise ValueError('Paper IX translation moved source lines')
    return text


def source_math(source,spec):
    from readable_chapters import chapter_text,original_math
    return original_math(normalize(chapter_text(source,spec)))


def source_specs(load):
    """Require the complete authored input graph, with only the atlas in PDF."""
    from readable_chapters import clean_tex,chapter_text
    seen=[]
    def visit(path):
        if path in seen:raise ValueError('Repeated Paper IX manuscript input: '+path)
        seen.append(path)
        text=clean_tex(load(path))
        if path==MAIN:text=text.split(r'\begin{document}',1)[1]
        for name in re.findall(r'\\input\{([^{}]+)\}',text):
            target=posixpath.normpath(BASE+name+('' if name.endswith('.tex') else '.tex'))
            if target=='papers/paper-ix/current/sources/worked_atlas.tex':continue
            visit(target)
    visit(MAIN)
    selected=list(dict.fromkeys(s['source'] for s in CHAPTERS))
    if selected!=[p for p in seen if p!=HISTORICAL_BIB]:
        raise ValueError('Review Paper IX manuscript input order or coverage')
    main=load(MAIN).splitlines()
    if main[CHAPTERS[0]['start_line']-1]!=r'\begin{document}':
        raise ValueError('Review Paper IX opening source boundary')
    for path in selected:
        specs=[s for s in CHAPTERS if s['source']==path]
        if path==MAIN or 'start_line' not in specs[0]:continue
        if specs[0]['start_line']!=1 or specs[-1]['end_line']!=len(load(path).splitlines()):
            raise ValueError('Review incomplete Paper IX source ranges: '+path)
        for a,b in zip(specs,specs[1:]):
            if a['end_line']+1!=b['start_line']:raise ValueError('Paper IX source ranges have a gap or overlap')
    return CHAPTERS


def references(load):
    from readable_chapters import manuscript_bibliography
    main=load(MAIN)
    current=manuscript_bibliography(main)
    for entry in current:
        entry['source']=MAIN
        entry['body']=entry['body'].replace(r'\input{historical_references.tex}','')
    historical=load(HISTORICAL_BIB)
    markers=list(re.finditer(r'\\bibitem\{([^{}]+)\}',historical))
    recovered=[dict(key=m[1],line=historical.count('\n',0,m.start())+1,source=HISTORICAL_BIB,
        body=historical[m.end():markers[i+1].start() if i+1<len(markers) else len(historical)].strip())
        for i,m in enumerate(markers)]
    result=current+recovered
    if len(result)!=27 or len({r['key'] for r in result})!=27:
        raise ValueError('Review the Paper IX bibliography inventory')
    return result


def prepare_book(reader,config):
    import readable_chapters as reading
    def load(path):
        record=reader.add(path)
        if not record:raise ValueError('Missing receipt-bound Paper IX source: '+path)
        return reader.site.read_source(record).decode('utf-8-sig')
    main=load(MAIN)
    source_specs(load)
    macros=reading.manuscript_macros(main,config['required_macros'])
    refs=references(load)
    printed=dict(re.findall(r'\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}',load(AUX)))
    chapters=[];labels={};state={'number_floats':True}
    for spec in config['chapters']:
        raw=reader.site.read_source(reader.add(spec['source']))
        text=reading.chapter_text(raw.decode('utf-8-sig'),spec)
        if spec.get('heading'):
            kind,title=spec['heading']
            if not re.search(r'\\'+kind+r'\*?\{'+re.escape(title)+r'\}',text):
                raise ValueError('Review Paper IX chapter boundary: '+spec['title'])
        state.update(spec.get('numbering_state',{}))
        chapter=reading.Chapter(normalize(text),macros,state=state,check_refs=False)
        chapter.source=spec['source'];chapter.table_config=config
        chapter.allow_prose_groups=True
        chapter.equation_numbers={key:number for key,number in printed.items()
                                  if re.search(r'(?:^|:)eq:',key) and not key.endswith('@cref')}
        chapter.table_aids_used=set();chapter.nested_tables=[]
        chapter.url=spec['url'];chapter.base=BASE;chapter.bibliography_url=config['bib_page']
        for key,node in chapter.labels.items():
            if key in labels:raise ValueError('Repeated Paper IX source label: '+key)
            node['url']=chapter.url
            reference=dict(node)
            if key in printed:
                equation=bool(re.search(r'(?:^|:)eq:',key))
                reference['plain_reference_label']='('+printed[key]+')' if equation else printed[key]
                if equation:reference.update(kind='equation',number=printed[key])
            labels[key]=reference
        state={key:getattr(chapter,key) for key in ('section','appendix','part','subsection','subsubsection',
            'counter','section_prefix','figure','table','number_floats')}
        chapters.append((spec,raw,chapter))
    for spec,raw,chapter in chapters:
        chapter.labels=labels;chapter.validate_references()
        chapter.citations={r['key']:(r['key'],chapter.relative(config['bib_page'])+'#ref-'+r['key']) for r in refs}
        nodes={n['line']:n for n in chapter.nodes}
        for row in reading.chapter_claims(reader,spec):
            if row['statement_line'] not in nodes:raise ValueError('Missing Paper IX statement')
            if row['proof_line'] and nodes.get(row['proof_line'],{}).get('kind')!='proof':
                raise ValueError('Missing Paper IX proof')
    return dict(config=config,chapters=chapters,references=refs,macros=macros,main=main)


def render_bibliography(reader,book):
    from readable_chapters import Chapter,presentation_tex
    from reading_navigation import navigation,resources,work_links
    config=book['config'];site=reader.site;page=config['bib_page']
    parser=Chapter('',book['macros']);parser.url=page
    parser.allow_prose_groups=True
    parser.labels=book['chapters'][0][2].labels
    body='<h1>Paper IX bibliography</h1>'+navigation(config,page)+resources(work_links(reader,WORK,page))
    body+='<article id="chapter-text" class="reading-bibliography"><p>The five current and 22 recovered historical entries follow the retained edition.</p>'
    for entry in book['references']:
        body+='<section id="ref-'+entry['key']+'"><h2>'+html.escape(entry['key'])+'</h2>'
        body+=parser.paragraphs(presentation_tex(normalize(entry['body'])))
        body+='<p><a href="'+reader.resolve(entry['source'],page,'L'+str(entry['line']))+'">Original bibliography entry</a></p></section>'
    body+='</article>'+navigation(config,page,'bottom')
    site.page(page,'Paper IX bibliography',body)
    def load(path):return reader.site.read_source(reader.records[path]).decode('utf-8-sig')
    expected=bibliography_math(load)
    if parser.math!=expected:raise ValueError('Paper IX bibliography math differs from its sources')
    site.write(BIB_RECORD,json.dumps(dict(references=[{k:e[k] for k in ('key','source','line')} for e in book['references']],
        sources={p:reader.records[p]['sha256'] for p in (MAIN,HISTORICAL_BIB)},math=expected,
        new_proof_review=False,new_lean_execution=False),ensure_ascii=False,indent=2)+'\n')
    site.search.append(dict(title='Paper IX / Bibliography',group='Collection',kind='Papers and source',
        work_ids=[WORK],url=page,text=' '.join(e['key']+' '+e['body'] for e in book['references'])))


def bibliography_math(load):
    from readable_chapters import original_math
    main=load(MAIN).split(r'\begin{thebibliography}{99}',1)[1].split(r'\end{thebibliography}',1)[0]
    return original_math(normalize(main))+original_math(normalize(load(HISTORICAL_BIB)))


def verify_bibliography(root,documents,pages):
    from readable_chapters import expand_math,manuscript_macros
    sources={r['repository_path']:r for r in documents['files']}
    def load(path):return (root/sources[path]['file_url']).read_text(encoding='utf-8-sig')
    record=json.loads((root/BIB_RECORD).read_bytes())
    expected=bibliography_math(load)
    assert record['math']==expected
    for path,sha in record['sources'].items():
        assert hashlib.sha256((root/sources[path]['file_url']).read_bytes()).hexdigest()==sha
    refs=references(load)
    assert record['references']==[{k:e[k] for k in ('key','source','line')} for e in refs]
    for entry in refs:assert 'ref-'+entry['key'] in pages[BOOK['bib_page']].ids
    markup=(root/BOOK['bib_page']).read_text(encoding='utf-8')
    actual=[html.unescape(x) for x in re.findall(r'<(?:span|div) class="arithmatex"[^>]*>(.*?)</(?:span|div)>',markup,re.S)]
    macros=manuscript_macros(load(MAIN),BOOK['required_macros'])
    assert actual==[r'\('+expand_math(x,macros)+r'\)' for x in expected]
    return dict(entries=len(refs),math_expressions=len(expected))
