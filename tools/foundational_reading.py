"""Receipt-bound HTML editions of Komorebi Space and Realization Boundaries.

Only declared print wrappers are translated. Source ranges, include order,
equations, theorem numbering and figure receipts are checked independently.
"""
import hashlib
import json
from pathlib import Path
import re

DATA=json.loads(Path(__file__).with_name('foundational_sections.json').read_text(encoding='utf-8'))
BOOKS={}
CHAPTERS=[]
for work,entry in DATA.items():
    chapters=entry['chapters']
    config=dict(entry,work=work,chapters=chapters,custom_reader='foundational',
        index='read/'+work+'/index.html',bib_page='read/'+work+'/references.html',
        inline_bibliography=True,numbered_bibliography=True,number_floats=True,
        show_figure_numbers=True,statement_navigation=True,required_macros=[],reader_controls=True,
        figure_source_root=entry['base'] if work=='komorebi-space' else entry['base'].removesuffix('manuscript/'),
        table_reading_aids={(t['source'].removeprefix(entry['base']),t['id']):t['aid'] for t in entry.get('tables',[])},
        require_table_reading_aids=True,
        reading_introduction='Read the complete retained manuscript in its authored order, with proofs, diagrams, references and appendices. Choose a chapter below or start at the preface.',
        reading_note='The chapters retain the manuscript wording, hypotheses and recorded limits. The original PDF and companion files remain available above.')
    BOOKS[work]=config
    CHAPTERS.extend(chapters)


def mask(text):return ''.join('\n' if c=='\n' else ' ' for c in text)


def rewrite(text,name,count,convert):
    from readable_chapters import group
    position=0
    while match:=re.search(r'\\'+name+r'\b',text[position:]):
        start=position+match.start();end=position+match.end();args=[]
        for _ in range(count):
            while text[end].isspace():end+=1
            value,end=group(text,end);args.append(value)
        value=convert(*args)
        missing=text[start:end].count('\n')-value.count('\n')
        if missing<0:raise ValueError('Print wrapper added source lines: '+name)
        value+='\n'*missing
        text=text[:start]+value+text[end:];position=start+len(value)
    return text


def normalize(source,work,macros=None):
    from readable_chapters import clean_tex
    text=math_environments(clean_tex(source));lines=text.count('\n')
    if work=='komorebi-space':
        text=rewrite(text,'partnote',2,lambda title,prose:r'\part{'+title+'} '+prose)
        text=rewrite(text,'chap',1,lambda title:r'\section{'+title+'}')
        text=rewrite(text,'source',1,lambda key:r'\label{src:'+key+'}')
        text=rewrite(text,'written',1,lambda value:'') # Explicitly empty in preamble.
        for command in ('plate','fixedplate'):
            text=rewrite(text,command,3,lambda name,caption,label:
                r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{'+name+r'.tex}\caption{'+caption+r'}\label{'+label+r'}\end{figure}')
        text=text.replace(r'\begin{insight}',r'\begin{interpretation}').replace(r'\end{insight}',r'\end{interpretation}')
        text=text.replace(r'\begin{scopebox}',r'\begin{warningbox}').replace(r'\end{scopebox}',r'\end{warningbox}')
    else:
        # Book chapters become top-level reader sections; lower headings retain
        # the printed chapter.section numbering and chapter-based theorem counter.
        text=re.sub(r'\\(chapter|section|subsection)(\*?)\{',lambda m:'\\'+{'chapter':'section','section':'subsection','subsection':'subsubsection'}[m[1]]+m[2]+'{',text)
        text=rewrite(text,'chapterintro',1,lambda prose:r'\emph{'+prose+'}')
        text=rewrite(text,'figfile',1,lambda name:name)
        text=text.replace(r'\begin{keybox}',r'\begin{keyidea}').replace(r'\end{keybox}',r'\end{keyidea}')
    text=re.sub(r'\\begin\{figure\}\[[^\]]+\]',r'\\begin{figure}',text)
    text=re.sub(r'\\includegraphics\[width=(?:[^\]]+)\]',r'\\includegraphics[width=.96\\linewidth]',text)
    text=re.sub(r'\\markboth\{[^{}]*\}\{[^{}]*\}|\\addcontentsline\{toc\}\{chapter\}\{[^{}]*\}',lambda m:mask(m[0]),text)
    text=re.sub(r'\\input\{verification_counts\}',lambda m:mask(m[0]),text)
    text=re.sub(r'\\(?:frontmatter|mainmatter|backmatter|tableofcontents|KomorebiCover)\b|\\pagenumbering\{[^{}]*\}|\\setlength\{\\parskip\}\{[^{}]*\}',lambda m:mask(m[0]),text)
    text=text.replace(r'\newline',' ')
    text=re.sub(r'\\begin\{(longtable|tabular|tabularx)\}.*?\\end\{\1\}',
        lambda m:re.sub(r'\\\\\[\d+pt\]',lambda n:r'\\',m[0]),text,flags=re.S)
    text=re.sub(r'\\begin\{tabularx\}\{\\linewidth\}',r'\\begin{tabularx}{\\textwidth}',text)
    text=re.sub(r'\\begin\{description\}\[style=nextline,leftmargin=0pt,labelindent=0pt,labelwidth=0pt,labelsep=0pt,itemindent=0pt,font=\\bfseries\\color\{Ink\},itemsep=9pt\]',r'\\begin{description}',text)
    # Printed page numbers become links to the same labelled passage.
    text=text.replace(r'p.~\pageref{',r'\passageref{')
    if macros:
        # Edition counts are authored prose macros; mathematical macros remain
        # literal until MathJax expansion so the expression record stays exact.
        for name,value in macros.items():
            if name.startswith('Edition') or name.endswith('Assertions'):
                if isinstance(value,str):
                    from readable_chapters import expand_math
                    text=re.sub(r'\\'+name+r'\b',lambda m:expand_math(value,macros),text)
    if text.count('\n')!=lines:raise ValueError('Source lines moved during book conversion')
    return text


def source_specs(load,config):
    entry=DATA[config['work']]
    for path,expected in entry['source_sha256'].items():
        raw=load(path)
        if hashlib.sha256(raw.encode()).hexdigest()!=expected:raise ValueError('Review changed foundational source: '+path)
    for path,expected in entry['input_order'].items():
        from readable_chapters import clean_tex
        if re.findall(r'\\input\{([^{}]+)\}',clean_tex(load(path)))!=expected:
            raise ValueError('Review foundational manuscript input order: '+path)
    return config['chapters']


def source_macros(load,config):
    from readable_chapters import manuscript_macros
    text='\n'.join(load(path) for path in config['macro_sources'])
    macros=manuscript_macros(text,[])
    # This one-argument wrapper is used only for literal Lean names in prose.
    macros.pop('code',None)
    return macros


def source_math(source,spec):
    from readable_chapters import chapter_text,original_math
    return original_math(math_environments(chapter_text(source,spec)))


def math_environments(text):
    """Preserve numbered display bodies while giving them reader delimiters."""
    return (text.replace(r'\begin{equation}',r'\[').replace(r'\end{equation}',r'\]')
        .replace(r'\begin{align}',r'\begin{align*}').replace(r'\end{align}',r'\end{align*}'))


def prepare_book(reader,config):
    import readable_chapters as reading
    def load(path):
        record=reader.add(path)
        if not record:raise ValueError('Missing retained book source: '+path)
        return reader.site.read_source(record).decode('utf-8-sig')
    source_specs(load,config);macros=source_macros(load,config)
    refs=reading.manuscript_bibliography(normalize(load(config['bib']),config['work'],macros))
    chapters=[];labels={};state={'number_floats':True};equations={};equation_counts={}
    for spec in config['chapters']:
        raw=reader.site.read_source(reader.add(spec['source']))
        selected=reading.chapter_text(raw.decode('utf-8-sig'),spec)
        if spec.get('appendix'):
            state.update(appendix=True,section=0,subsection=0,subsubsection=0,counter=0)
        chapter=reading.Chapter(normalize(selected,config['work'],macros),macros,state=state,check_refs=False)
        chapter.url=spec['url'];chapter.base=config['base'];chapter.allow_prose_groups=True
        chapter.bibliography_url=config['bib_page'];chapter.table_config=config;chapter.source=spec['source']
        chapter.table_aids_used=set();chapter.nested_tables=[]
        chapter.proof_pairs={}
        for a,b in zip(chapter.nodes,chapter.nodes[1:]):
            if a['kind'] in reading.NUMBERED and b['kind']=='proof':chapter.proof_pairs[a['id']]=b['id']
        for key,node in chapter.labels.items():
            if key in labels:raise ValueError('Repeated book label: '+key)
            node['url']=chapter.url;labels[key]=dict(node,reference_label=node['number'] or node['title'])
        # Number displayed equations exactly as the print counters do, including
        # multiple rows in align. The formula text remains unchanged.
        for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}',selected,re.S):
                line=selected.count('\n',0,match.start())+1
                node=next(n for n in reversed(chapter.nodes) if n['line']<=line)
                section=node['section'];counter=equation_counts.get(section,0)
                rows=re.split(r'\\\\(?:\[[^\]]*\])?',match[2]) if match[1]=='align' else [match[2]]
                for row in rows:
                    if r'\notag' in row or r'\nonumber' in row:continue
                    counter+=1
                    for key in re.findall(r'\\label\{([^{}]+)\}',row):
                        equations[key]=section+'.'+str(counter)
                equation_counts[section]=counter
        state={key:getattr(chapter,key) for key in ('section','appendix','part','subsection','subsubsection','counter','section_prefix','figure','table','number_floats')}
        chapters.append((spec,raw,chapter))
    for key,number in equations.items():
        labels[key]['reference_label']=number;labels[key]['equation_number']=number
    for spec,raw,chapter in chapters:
        chapter.labels=labels;chapter.equation_numbers=equations;chapter.validate_references()
        chapter.command_links['passageref']={key:(node['url']+'#'+node['id'],'Source passage') for key,node in labels.items()}
        chapter.citations={r['key']:(str(i),chapter.relative(config['bib_page'])+'#ref-'+r['key']) for i,r in enumerate(refs,1)}
    from reader_figure_assets import prepare
    figures=prepare(reader,config,chapters)
    return dict(config=config,chapters=chapters,references=refs,macros=macros,main=load(config['main']),figure_assets=figures)
