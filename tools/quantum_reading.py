"""Source-bound arithmetic, symmetry, catalytic and circuit chapters of Quantum and Circuits.

Print wrappers are translated explicitly. The retained source lines, QA labels,
proof endings, mathematical expression order and original figures stay bound
to their recorded edition. This module performs no mathematical review.
"""
import hashlib
import json
from pathlib import Path
import re

WORK='monographs-quantum-and-circuits'
BASE='monographs/quantum-and-circuits/volume/'
MAIN=BASE+'volume.tex'
PREFIX='read/'+WORK+'/'
DATA=json.loads(Path(__file__).with_name('quantum_sections.json').read_text(encoding='utf-8'))
CHAPTERS=DATA['chapters']
BOOK=dict(work=WORK,label='Quantum and Circuits',title='Quantum and Circuits: Arithmetic, symmetry, and catalysis',
    base=BASE,main=MAIN,bib=BASE+'generated/references.tex',inline_bibliography=True,
    index=PREFIX+'index.html',bib_page=PREFIX+'references.html',chapters=CHAPTERS,
    custom_reader='quantum',partial=False,main_chapters=21,required_macros=[],
    reader_controls=True,statement_navigation=True,numbered_bibliography=True,
    contents_anchors=['source-continuations'],reading_guide=PREFIX+'start.html',
    visual_guide_index=PREFIX+'visual-guides.html',
    bibliography_introduction='These collected entries accompany all four mathematical treatments, in their original order and numbering.',
    figure_receipts='assets/figures/quantum-arithmetic/figures.json',
    table_reading_aids={(t['source'].removeprefix(BASE),t['id']):t['aid'] for t in DATA['tables']},
    require_table_reading_aids=True,contents_groups=DATA['groups'],
    reading_introduction='Read the complete volume: chapters 1–21, appendices A–F, the volume guide, glossary, and collected references. '
        'The formal guides retain their declaration types, proof boundaries, evidence ledgers, and reproduction commands.',
    reading_note='This HTML edition preserves the authored wording, mathematics, captions, and recorded limits of the 344-page volume. '
        'Verification statements describe the retained edition and its records. This presentation adds no proof review or Lean execution.',
    continuation_sources=[])


def mask(text):return ''.join('\n' if c=='\n' else ' ' for c in text)


def rewrite(text,name,count,convert):
    from readable_chapters import group
    pos=0
    while match:=re.search(r'\\'+re.escape(name)+r'\b',text[pos:]):
        start=pos+match.start();end=pos+match.end();args=[]
        for _ in range(count):
            while end<len(text) and text[end].isspace():end+=1
            value,end=group(text,end);args.append(value)
        replacement=convert(*args)
        padding=text[start:end].count('\n')-replacement.count('\n')
        if padding<0:raise ValueError('Quantum print wrapper moved source lines: '+name)
        replacement+='\n'*padding
        text=text[:start]+replacement+text[end:];pos=start+len(replacement)
    return text


def normalize(raw):
    """Translate only the retained arithmetic chapter's print syntax."""
    from readable_chapters import clean_tex,group
    text=clean_tex(raw);lines=text.count('\n')
    text=rewrite(text,'hypertarget',2,lambda key,body:body)
    text=rewrite(text,'lead',1,lambda prose:r'\emph{'+prose+'}')
    text=rewrite(text,'note',1,lambda prose:prose)
    text=rewrite(text,'fig',3,lambda name,width,caption:
        r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{assets/q_'+name+r'.pdf}\caption{'+caption+r'}\end{figure}')
    text=re.sub(r'\\addcontentsline\{toc\}\{section\}\{[^{}]*\}',lambda m:mask(m[0]),text)
    text=re.sub(r'\\begin\{center\}|\\end\{center\}|\\clearpage\b',lambda m:mask(m[0]),text)
    text=re.sub(r'\\begin\{minipage\}\[b\]\{\\linewidth\}\\centering|\\end\{minipage\}',lambda m:mask(m[0]),text)
    text=re.sub(r'\\noalign\{\}|\\(?:endhead|endlastfoot)\b',lambda m:mask(m[0]),text)
    text=text.replace(r'\begin{longtable}[]',r'\begin{longtable}')
    text=re.sub(r'\\def\\labelenumi\{\\arabic\{enumi\}\.\}',lambda m:mask(m[0]),text)
    # Pandoc's outer small-font group is print infrastructure around this table.
    text=re.sub(r'\{[ \t]*(?=\\begin\{longtable\})',lambda m:mask(m[0]),text)
    text=text.replace(r'\end{longtable}}',r'\end{longtable} ')
    text=re.sub(r'\\begin\{(?:tabular|longtable)\}.*?\\end\{(?:tabular|longtable)\}',
        lambda m:re.sub(r'\\\\\[\d+pt\]',lambda row:r'\\',m[0]),text,flags=re.S)
    position=0
    while match:=re.search(r'\\subsection\*\{Theorem (QA\d\d)\. ',text[position:]):
        start=position+match.start();brace=text.index('{',start)
        title,end=group(text,brace)
        statement_title=title.split('. ',1)[1]
        text=text[:start]+r'\begin{theorem}['+statement_title+']'+text[end:]
        position=start+len(r'\begin{theorem}['+statement_title+']')
    text=text.replace(r'\textbf{Proof.}',r'\end{theorem}\begin{proof}')
    text=text.replace(r'\(\square\)',r'\(\square\)\end{proof}')
    if text.count('\n')!=lines:raise ValueError('Quantum translation moved source lines')
    return text


def source_specs(load):
    for path,expected in DATA['source_sha256'].items():
        if hashlib.sha256(load(path).encode()).hexdigest()!=expected:
            raise ValueError('Review changed Quantum source: '+path)
    for source in DATA['selected_sources']:
        specs=[s for s in CHAPTERS if s['source']==source]
        if specs[0]['start_line']!=1 or specs[-1]['end_line']!=len(load(source).splitlines()):
            raise ValueError('Quantum selection omits source boundaries')
        for a,b in zip(specs,specs[1:]):
            if a['end_line']+1!=b['start_line']:raise ValueError('Quantum source ranges have a gap or overlap')
    return CHAPTERS


def source_math(raw,spec):
    from readable_chapters import original_math,chapter_text
    from quantum_symmetry import SOURCE,normalize as normalize_symmetry
    from quantum_catalytic import SOURCE as CATALYTIC,normalize as normalize_catalytic
    from quantum_circuits import SOURCE as CIRCUITS,VISUAL,normalize as normalize_circuits,normalize_visual
    from quantum_companions import SOURCES as COMPANIONS,normalize as normalize_companion
    if spec['source'] in COMPANIONS:return original_math(chapter_text(normalize_companion(raw,spec['source']),spec))
    normalizer={SOURCE:normalize_symmetry,CATALYTIC:normalize_catalytic,CIRCUITS:normalize_circuits,VISUAL:normalize_visual}.get(spec['source'],lambda text:text)
    return original_math(chapter_text(normalizer(raw),spec))


def source_macros(load,spec):
    from readable_chapters import manuscript_macros
    from quantum_symmetry import SOURCE,source_macros as symmetry_macros
    from quantum_catalytic import SOURCE as CATALYTIC,source_macros as catalytic_macros
    from quantum_circuits import SOURCE as CIRCUITS,VISUAL,source_macros as circuit_macros
    from quantum_companions import SOURCES as COMPANIONS,source_macros as companion_macros
    if spec['source'] in COMPANIONS:return companion_macros(load,spec['source'])[1]
    if spec['source'] in {CIRCUITS,VISUAL}:return circuit_macros(load,visual=spec['source']==VISUAL)
    if spec['source']==SOURCE:return symmetry_macros(load)
    if spec['source']==CATALYTIC:return catalytic_macros(load)
    return manuscript_macros(load(MAIN),[])


def prepare_book(reader,config):
    import readable_chapters as reading
    from quantum_symmetry import SOURCE as SYMMETRY,MACROS as SYMMETRY_MACROS,FIGURES,normalize as normalize_symmetry,number_chapter
    from quantum_catalytic import SOURCE as CATALYTIC,MACROS as CATALYTIC_MACROS,FIGURES as CATALYTIC_FIGURES,normalize as normalize_catalytic
    from quantum_circuits import SOURCE as CIRCUITS,VISUAL,MACROS as CIRCUIT_MACROS,FIGURES as CIRCUIT_FIGURES,normalize as normalize_circuits,normalize_visual
    from quantum_companions import SOURCES as COMPANIONS,ARITHMETIC as ARITHMETIC_GUIDE,CIRCUIT as CIRCUIT_GUIDE,normalize as normalize_companion,source_macros as companion_macros,bind_volume_routes,bind_pdf_pages
    treatments={CIRCUITS:(normalize_circuits,CIRCUIT_MACROS,None),VISUAL:(normalize_visual,CIRCUIT_MACROS,CIRCUIT_FIGURES),SYMMETRY:(normalize_symmetry,SYMMETRY_MACROS,FIGURES),CATALYTIC:(normalize_catalytic,CATALYTIC_MACROS,CATALYTIC_FIGURES)}
    def load(path):
        record=reader.add(path)
        if not record:raise ValueError('Missing retained Quantum source: '+path)
        return reader.site.read_source(record).decode('utf-8-sig')
    source_specs(load);main=load(MAIN);macros=reading.manuscript_macros(main,[])
    collected=reading.manuscript_bibliography(load(config['bib']))
    references=[r for r in collected if r['key'].startswith(('q:','s:','g:','c:'))]
    if [r['key'] for r in references]!=DATA['reference_keys']:raise ValueError('Review Quantum reference selection')
    if references!=collected[:len(references)]:raise ValueError('Review original Quantum citation numbering')
    for path,title in config['continuation_sources']:reader.add(path,title)
    for source in COMPANIONS:
        treatments[source]=(lambda raw,_source=source:normalize_companion(raw,_source),companion_macros(load,source)[0],None)
    chapters=[];labels={};state={};qa=[];current_source=None;printed_chapter=None;counters={};equations={}
    for spec in CHAPTERS:
        treatment=treatments.get(spec['source'])
        if treatment and spec['printed_chapter']!=printed_chapter:
            printed_chapter=spec['printed_chapter'];state={'section_prefix':str(printed_chapter)+'.'}
        elif not treatment and spec['source']!=current_source:
            current_source=spec['source']
            state={'section_prefix':str(DATA['selected_sources'].index(current_source)+1)+'.'}
        raw=reader.site.read_source(reader.add(spec['source']))
        selected=reading.chapter_text((treatment[0] if treatment else normalize)(raw.decode('utf-8-sig')),spec)
        chapter=reading.Chapter(selected,source_macros(load,spec),state=state,check_refs=False)
        chapter.url=spec['url'];chapter.base=BASE;chapter.allow_prose_groups=True
        chapter.bibliography_url=config['bib_page'];chapter.table_config=config;chapter.source=spec['source']
        chapter.table_aids_used=set();chapter.nested_tables=[];chapter.proof_pairs={}
        if treatment:
            chapter.original_text=reading.chapter_text(raw.decode('utf-8-sig'),spec)
            chapter.macro_source=treatment[1]
            number_chapter(chapter,spec,counters,equations)
            if spec['source']==VISUAL:
                # The print guide uses captioned images without float numbers.
                for node in chapter.nodes:
                    if node['kind']=='figure':node['number']=''
        for i,node in enumerate(chapter.nodes):
            if not treatment and node['kind']=='theorem':
                number='QA'+str(len(qa)+1).zfill(2);node['number']=number;qa.append(number)
                proof=chapter.nodes[i+1] if i+1<len(chapter.nodes) else None
                if not proof or proof['kind']!='proof':raise ValueError('Missing authored proof for '+number)
                chapter.proof_pairs[node['id']]=proof['id']
        for key,node in chapter.labels.items():
            if key in labels:raise ValueError('Repeated Quantum label: '+key)
            reference=node['number'] or node['title']
            if treatment and node['number']:
                kind='Table' if node['kind'] in {'longtable','tabular','table'} else reading.KIND_NAMES.get(node['kind'],node['kind'].capitalize())
                reference=kind+' '+node['number']
            node['url']=chapter.url
            labels[key]=dict(node,reference_label=reference,plain_reference_label=node['number'])
        state={k:getattr(chapter,k) for k in ('section','appendix','part','subsection','subsubsection','counter','section_prefix','figure','table','number_floats')}
        chapters.append((spec,raw,chapter))
    if qa!=['QA'+str(i).zfill(2) for i in range(1,21)]:raise ValueError('Review arithmetic statement inventory')
    bind_volume_routes(reader,chapters,config)
    bind_pdf_pages(reader,chapters,DATA)
    formal_types=[]
    for spec,_,chapter in chapters:
        if spec['source'] not in COMPANIONS:continue
        parent=spec['title'];current=None;records=0
        for node in chapter.nodes:
            if node['kind'] in reading.HEADINGS:
                parent=re.sub(r'\\(?:code|texttt)\{([^{}]+)\}',lambda m:m[1],reading.navigation_title(node['title']))
                node['toc_title']=parent;node['search_title']=parent
            if spec['source']==ARITHMETIC_GUIDE and node['kind']=='lstlisting':
                node['search_title']='Literal Lean source: '+parent+' (line '+str(node['line'])+')'
            if spec['source']==CIRCUIT_GUIDE:
                if node['kind']=='paragraph' and re.fullmatch(r'L\d{3} [A-Za-z0-9_]+',node['title']):current=node['title']
                if current and node['kind']=='lstlisting':
                    node['search_title']='Formal type '+current;formal_types.append(current.split()[0]);records+=1;current=None
        if records and records!=sum(n['kind']=='lstlisting' for n in chapter.nodes):raise ValueError('Review formal register code routes')
    if formal_types!=['L'+str(i).zfill(3) for i in range(1,116)]:raise ValueError('Review formal type inventory')
    # Chapter labels used by the coverage appendix denote chapters, while
    # their starred display headings remain unnumbered in the topic body.
    for spec,_,chapter in chapters:
        for key in chapter.labels:
            if key.startswith('c:ch:') or key=='c:app:index':
                number=str(spec['printed_chapter'])
                labels[key].update(reference_label='Chapter '+number,plain_reference_label=number)
    for label,number in equations.items():
        labels[label].update(reference_label='Equation ('+number+')',plain_reference_label=number,equation_number=number)
    from quantum_catalytic import bind_named_proofs
    bind_named_proofs(chapters,labels)
    for spec,raw,chapter in chapters:
        chapter.labels=labels;chapter.validate_references()
        chapter.equation_numbers=equations
        chapter.citations={r['key']:(str(i),chapter.relative(config['bib_page'])+'#ref-'+r['key']) for i,r in enumerate(references,1)}
    from reader_figure_assets import prepare
    figures=prepare(reader,config,[c for c in chapters if c[0]['source'] not in treatments])
    for source,treatment in treatments.items():
        if not treatment[2]:continue
        figures.update(prepare(reader,dict(config,figure_receipts=treatment[2]),[c for c in chapters if c[0]['source']==source]))
    return dict(config=config,chapters=chapters,references=references,macros=macros,main=main,
        figure_assets=figures)
