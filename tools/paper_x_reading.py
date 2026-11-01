"""Source-bound Paper X chapters, current contract and dated continuations."""
import hashlib
import html
import json
from pathlib import Path
import re

WORK='paper-x'
BASE='papers/paper-x/current/manuscript/'
MAIN=BASE+'Paper_X_Block27_Amended.tex'
BIB=BASE+'references.tex'
CONTINUATION=BASE+'residue_continuation_body.tex'
PREFIX='read/paper-x/'
BIB_RECORD='documents/paper-x-bibliography.json'
INPUTS=['reading_contract.tex','historical_checkpoint_frontmatter.tex',
        'residue_continuation_body.tex','conditional_completion.tex','references.tex']
CHAPTERS=json.loads(Path(__file__).with_name('paper_x_sections.json').read_text(encoding='utf-8'))
BOOK=dict(work=WORK,label='Paper X',base=BASE,main=MAIN,bib=BIB,inline_bibliography=True,
    index=PREFIX+'index.html',bib_page=PREFIX+'references.html',
    title='Universal Residual Seeds',chapters=CHAPTERS,main_chapters=15,
    custom_reader='paper_x',number_floats=True,statement_navigation=True,
    required_macros=['Ocal','F','Z','Q','Compat','Forest','Sys'],
    require_table_reading_aids=True,
    reading_introduction='Read all 15 main sections, the algorithms and reproducibility appendices, '
        'the retained historical checkpoints and residue-counting continuation, and the final '
        'conditional occupied-system completion. The thirty-page visual atlas remains in the PDF.')
BOOK['table_reading_aids']={
    ('reading_contract.tex','L10'):dict(caption='Routes through the complete reading edition',
        headers=['Read for','Follow this route'],row_header_column=0),
    ('Paper_X_Block27_Amended.tex','L1896'):dict(
        headers=['Certificate','Result'],row_header_column=0),
    ('Paper_X_Block27_Amended.tex','L1921'):dict(caption='Retained main-manuscript claim ledger',
        headers=['Statement','Status','Scope or boundary'],row_header_column=0),
}


def mask(text):return ''.join('\n' if c=='\n' else ' ' for c in text)


def normalize(source):
    """Translate only reviewed layout and declaration syntax; keep line anchors."""
    from readable_chapters import clean_tex,group
    text=clean_tex(source);count=text.count('\n')
    text=re.sub(r'\\input\{(?:'+ '|'.join(re.escape(p) for p in INPUTS)+r')\}',lambda m:mask(m[0]),text)
    while match:=re.search(r'\\providecommand\{',text):
        _,end=group(text,match.end()-1)
        if text[end:end+1]=='[':_,end=group(text,end,'[',']')
        _,stop=group(text,end)
        text=text[:match.start()]+mask(text[match.start():stop])+text[stop:]
    text=re.sub(r'\\fbox\{\\begin\{minipage\}\{0\.94\\linewidth\}(.*?)\\end\{minipage\}\}',
        lambda m:r'\begin{readerroadmap}[title={Historical checkpoint scope}]'+m[1]+r'\end{readerroadmap}',text,flags=re.S)
    text=text.replace(r'\begin{tabularx}{\linewidth}',r'\begin{tabularx}{\textwidth}')
    text=re.sub(r'\\(?:phantomsection|newblock|smallskip|newpage)\b',lambda m:mask(m[0]),text)
    text=text.replace(r'\begin{equation}',r'\[').replace(r'\end{equation}',r'\]')
    while match:=re.search(r'\{\\em\b',text):
        body,end=group(text,match.start())
        text=text[:match.start()]+r'\emph{'+body[len(r'\em'):]+'}'+text[end:]
    if text.count('\n')!=count:raise ValueError('Paper X translation moved source lines')
    return text


def source_math(source,spec):
    from readable_chapters import chapter_text,original_math
    return original_math(normalize(chapter_text(source,spec)))


def source_macros(main,continuation):
    from readable_chapters import manuscript_macros
    return manuscript_macros(main+'\n'+continuation,BOOK['required_macros'])


def source_specs(load):
    """Require the complete current manuscript and all five authored inputs."""
    from readable_chapters import clean_tex
    main=load(MAIN);body=clean_tex(main).split(r'\begin{document}',1)[1]
    if re.findall(r'\\input\{([^{}]+)\}',body)!=INPUTS:
        raise ValueError('Review Paper X manuscript input order')
    selected={s['source'] for s in CHAPTERS}
    if selected!={MAIN,*[BASE+p for p in INPUTS if BASE+p!=BIB]}:
        raise ValueError('Review Paper X manuscript input coverage')
    if [s['source'] for s in CHAPTERS if s['source']!=MAIN]!=[BASE+p for p in INPUTS if BASE+p!=BIB]:
        raise ValueError('Review Paper X included chapter order')
    for path in selected:
        specs=[s for s in CHAPTERS if s['source']==path]
        lines=load(path).splitlines()
        if path==MAIN:
            if lines[specs[0]['start_line']-1]!=r'\begin{document}' or lines[specs[-1]['end_line']-1]!=r'\end{document}':
                raise ValueError('Review Paper X opening or ending boundary')
        elif 'start_line' not in specs[0]:continue
        elif specs[0]['start_line']!=1 or specs[-1]['end_line']!=len(lines):
            raise ValueError('Review Paper X source range coverage')
        for a,b in zip(specs,specs[1:]):
            if a['end_line']+1!=b['start_line']:raise ValueError('Paper X source ranges have a gap or overlap')
    return CHAPTERS


def prepare_book(reader,config):
    import readable_chapters as reading
    def load(path):
        record=reader.add(path)
        if not record:raise ValueError('Missing receipt-bound Paper X source: '+path)
        return reader.site.read_source(record).decode('utf-8-sig')
    source_specs(load)
    main=load(MAIN);macros=source_macros(main,load(CONTINUATION))
    refs=reading.manuscript_bibliography(load(BIB))
    if len(refs)!=23:raise ValueError('Review Paper X bibliography inventory')
    chapters=[];labels={};state={'number_floats':True}
    for spec in config['chapters']:
        raw=reader.site.read_source(reader.add(spec['source']))
        text=reading.chapter_text(raw.decode('utf-8-sig'),spec)
        if spec.get('heading'):
            kind,title=spec['heading']
            if not re.search(r'\\'+kind+r'\*?\{'+re.escape(title)+r'\}',text):
                raise ValueError('Review Paper X chapter boundary: '+spec['title'])
        chapter=reading.Chapter(normalize(text),macros,state=state,check_refs=False)
        chapter.allow_prose_groups=True
        chapter.equation_numbers={'eq:weighted-torsion':'1','eq:unit-witness':'2'}
        chapter.url=spec['url'];chapter.base=BASE;chapter.bibliography_url=config['bib_page']
        for key,node in chapter.labels.items():
            if key in labels:raise ValueError('Repeated Paper X source label: '+key)
            node['url']=chapter.url
            reference=dict(node)
            if key in chapter.equation_numbers:
                number=chapter.equation_numbers[key]
                reference.update(kind='equation',number=number,plain_reference_label='('+number+')')
            labels[key]=reference
        state={key:getattr(chapter,key) for key in ('section','appendix','part','subsection',
            'subsubsection','counter','section_prefix','figure','table','number_floats')}
        chapters.append((spec,raw,chapter))
    for spec,raw,chapter in chapters:
        chapter.labels=labels;chapter.validate_references()
        chapter.citations={r['key']:(r['key'],chapter.relative(config['bib_page'])+'#ref-'+r['key']) for r in refs}
        nodes={n['line']:n for n in chapter.nodes}
        for row in reading.chapter_claims(reader,spec):
            if row['statement_line'] not in nodes:raise ValueError('Missing Paper X statement')
            if row['proof_line'] and nodes.get(row['proof_line'],{}).get('kind')!='proof':
                raise ValueError('Missing Paper X proof')
    return dict(config=config,chapters=chapters,references=refs,macros=macros,main=main)


def render_bibliography(reader,book):
    from readable_chapters import Chapter,original_math
    from reading_navigation import navigation,resources,work_links
    config=book['config'];site=reader.site;page=config['bib_page']
    parser=Chapter('',book['macros']);parser.url=page;parser.allow_prose_groups=True
    body='<h1>Paper X bibliography</h1>'+navigation(config,page)+resources(work_links(reader,WORK,page))
    body+='<article id="chapter-text" class="reading-bibliography"><p>All 23 entries follow the retained current bibliography.</p>'
    for entry in book['references']:
        body+='<section id="ref-'+entry['key']+'"><h2>'+html.escape(entry['key'])+'</h2>'
        body+=parser.paragraphs(normalize(entry['body']))
        body+='<p><a href="'+reader.resolve(BIB,page,'L'+str(entry['line']))+'">Original bibliography entry</a></p></section>'
    body+='</article>'+navigation(config,page,'bottom')
    site.page(page,'Paper X bibliography',body)
    expected=original_math(normalize(reader.site.read_source(reader.records[BIB]).decode('utf-8-sig')))
    if parser.math!=expected:raise ValueError('Paper X bibliography math differs from its source')
    site.write(BIB_RECORD,json.dumps(dict(source=BIB,source_sha256=reader.records[BIB]['sha256'],
        references=[{k:e[k] for k in ('key','line')} for e in book['references']],math=expected,
        new_proof_review=False,new_lean_execution=False),ensure_ascii=False,indent=2)+'\n')
    site.search.append(dict(title='Paper X / Bibliography',group='Collection',kind='Papers and source',
        work_ids=[WORK],url=page,text=' '.join(e['key']+' '+e['body'] for e in book['references'])))


def verify_bibliography(root,documents,pages):
    from readable_chapters import expand_math,original_math,manuscript_bibliography
    sources={r['repository_path']:r for r in documents['files']}
    def load(path):return (root/sources[path]['file_url']).read_text(encoding='utf-8-sig')
    record=json.loads((root/BIB_RECORD).read_bytes());expected=original_math(normalize(load(BIB)))
    assert record['source']==BIB and record['source_sha256']==hashlib.sha256((root/sources[BIB]['file_url']).read_bytes()).hexdigest()
    assert record['math']==expected and not record['new_proof_review'] and not record['new_lean_execution']
    refs=manuscript_bibliography(load(BIB))
    assert record['references']==[{k:e[k] for k in ('key','line')} for e in refs]
    for entry in refs:assert 'ref-'+entry['key'] in pages[BOOK['bib_page']].ids
    markup=(root/BOOK['bib_page']).read_text(encoding='utf-8')
    actual=[html.unescape(x) for x in re.findall(r'<(?:span|div) class="arithmatex"[^>]*>(.*?)</(?:span|div)>',markup,re.S)]
    macros=source_macros(load(MAIN),load(CONTINUATION))
    assert actual==[r'\('+expand_math(x,macros)+r'\)' for x in expected]
    return dict(entries=len(refs),math_expressions=len(expected))
