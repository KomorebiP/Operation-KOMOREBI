"""Presentation of the volume guide, appendices and back matter, without replay."""
import re

BASE='monographs/quantum-and-circuits/volume/'
MAIN=BASE+'volume.tex'
PREAMBLE=BASE+'preamble.tex'
ARITHMETIC=BASE+'generated/q_lean.tex'
SYMMETRY=BASE+'generated/s_appendix.tex'
CATALYTIC=BASE+'generated/g_appendix.tex'
CIRCUIT=BASE+'generated/c_lean.tex'
COVERAGE=BASE+'generated/c_supplement.tex'
VERIFICATION=BASE+'verification_status.tex'
GLOSSARY=BASE+'generated/glossary.tex'
NOTES=BASE+'generated/source_notes.tex'
SOURCES={MAIN,ARITHMETIC,SYMMETRY,CATALYTIC,CIRCUIT,COVERAGE,VERIFICATION,GLOSSARY,NOTES}
CODE=re.compile(r'\\begin\{(lstlisting|verbatim|Verbatim)\}(?:\[([^\]\n]*)\])?(.*?)\\end\{\1\}',re.S)
EVIDENCE_NOTE='Verification statements describe the retained edition and its recorded evidence. This HTML presentation adds no Lean execution or proof review.'


def normalize(raw,source):
    """Translate print infrastructure outside literal code; retain every line."""
    from readable_chapters import clean_tex,group
    from quantum_reading import mask,rewrite
    def prose(text):
        # Each register heading and its source/block/axiom metadata stay tied
        # to the original line; they are not additional numbered theorems.
        text=re.sub(r'\{\\small\\bfseries (L\d{3})\\enspace\\texttt\{([^{}]+)\}\\par\}',
            lambda m:r'\paragraph*{'+m[1]+' '+m[2].replace(r'\_','_')+'}',text)
        for match in reversed(list(re.finditer(r'\{\\(?:small|footnotesize)\b',text))):
            body,end=group(text,match.start())
            if body.startswith(r'\footnotesize\raggedright\textbf{Source.}'):
                body=body.replace(r'\par',r'\newline')
            text=text[:match.start()]+' '+body+' '+text[end:]
        text=clean_tex(text)
        text=rewrite(text,'hypertarget',2,lambda key,body:body)
        text=rewrite(text,'texttt',1,lambda body:
            r'\code{'+group(body,len(r'\detokenize'))[0]+'}' if body.startswith(r'\detokenize{') else r'\texttt{'+body.replace(r'\ ',' ')+'}')
        text=rewrite(text,'pagehead',2,lambda title,subtitle:r'\section*{'+title+r'}\textbf{'+subtitle+'}')
        text=rewrite(text,'resultrow',4,lambda key,title,scope,unused:
            r'\ref{'+key+'} & '+title+' & '+scope+r' & \pdfpage{'+key+r'}\\')
        text=re.sub(r'\\begin\{statusbox\}\{([^{}]+)\}',lambda m:r'\begin{interpretation}[title={'+m[1]+'}]',text)
        text=text.replace(r'\end{statusbox}',r'\end{interpretation}')
        text=re.sub(r'\\chapter\*?\{',r'\\section*{',text)
        text=re.sub(r'\\begin\{minipage\}(?:\[b\])?\{\\(?:line|text)width\}|\\end\{minipage\}',lambda m:mask(m[0]),text)
        text=re.sub(r'\\(?:footnotesize|bfseries|nopagebreak|raggedleft|enspace)\b|\\noalign\{\}|\\endlastfoot\b',lambda m:mask(m[0]),text)
        text=text.replace(r'\begin{longtable}[]',r'\begin{longtable}')
        if source==CIRCUIT:
            text=re.sub(r'\\subsection\*\{((?:Gates|CutComparison|Examples|Degree|MultiplicativeDegree|SafeDegree|AffineOutput|DegreeChecks): \d+ declarations)\}',r'\\section*{\1}',text)
            text=rewrite(text,'lstset',1,lambda value:mask(value))
        if source in {ARITHMETIC,COVERAGE,VERIFICATION}:
            text=re.sub(r'\\endhead\b',lambda m:mask(m[0]),text)
        if source==SYMMETRY or source==GLOSSARY:
            from quantum_symmetry import normalize as symmetry
            text=symmetry(text)
        if source==CATALYTIC:
            from quantum_catalytic import normalize as catalytic
            text=catalytic(text)
        if source==MAIN:
            text=re.sub(r'\\input\{(?:preamble\.tex|generated/[sgc]_macros\.tex)\}',lambda m:mask(m[0]),text)
            text=rewrite(text,'VolumePart',3,lambda title,intro,entries:r'\section*{'+title+'}'+intro+r'\begin{itemize}'+entries+r'\end{itemize}')
            text=rewrite(text,'VolumePartEntry',2,lambda number,title:r'\item \volumechapter{'+number+'}')
            text=text.replace(r'\VolumeVisualInput{',r'\input{')
            text=re.sub(r'\\(?:VolumeCover|frontmatter|mainmatter|appendix|backmatter)\b',lambda m:mask(m[0]),text)
            text=rewrite(text,'renewcommand',2,lambda name,value:mask(name+value))
            text=re.sub(r'\\begin\{description\}\[style=nextline\]|\\end\{description\}',lambda m:mask(m[0]),text)
            text=re.sub(r'\\item\[([^\]]+)\]',lambda m:r'\paragraph*{'+m[1]+'}',text)
        return text
    parts=[];position=0
    for match in CODE.finditer(raw):
        parts.append(prose(raw[position:match.start()]))
        options=match[2] or '';caption=''
        if options:
            expected=re.fullmatch(r'style=(?:pythonstyle|cppstyle)(?:,caption=\{([^{}]+)\})?',options)
            if match[1]=='Verbatim':
                if options not in {r'breaklines=true,breakanywhere=true,fontsize=\footnotesize,samepage=true',r'breaklines=true,breakanywhere=true,fontsize=\footnotesize',r'breaklines=true,fontsize=\footnotesize'}:
                    raise ValueError('Review arithmetic literal-code options')
            elif not expected:raise ValueError('Review companion listing options: '+options)
            if expected and expected[1]:caption=r'\paragraph*{'+expected[1]+'}'
        # The bodies, including Lean Unicode and literal backslashes, are copied.
        parts.append(caption+r'\begin{lstlisting}'+match[3]+r'\end{lstlisting}')
        position=match.end()
    parts.append(prose(raw[position:]));text=''.join(parts)
    if text.count('\n')!=raw.count('\n'):raise ValueError('Companion translation moved source lines: '+source)
    return text


def source_macros(load,source):
    from readable_chapters import manuscript_macros
    from quantum_symmetry import MACROS as S_MACROS,source_macros as symmetry
    from quantum_catalytic import MACROS as G_MACROS,source_macros as catalytic
    from quantum_circuits import MACROS as C_MACROS,source_macros as circuit
    if source in {SYMMETRY,GLOSSARY}:return S_MACROS,symmetry(load)
    if source==CATALYTIC:return G_MACROS,catalytic(load)
    if source in {CIRCUIT,COVERAGE}:
        macros=circuit(load,visual=source==CIRCUIT)
        macros.update({k:v for k,v in manuscript_macros(load(PREAMBLE),[]).items() if k in {'TC','Deg','x','xor'}})
        return C_MACROS,macros
    return PREAMBLE,manuscript_macros(load(PREAMBLE),[])


def bind_volume_routes(reader,chapters,config):
    """Use explicit input paths and the authored part-entry numbers as routes."""
    from readable_chapters import group,navigation_title
    volume=next(c for spec,_,c in chapters if spec['source']==MAIN)
    for spec,_,chapter in chapters:
        if spec['source']==MAIN:continue
        path=spec['source'].removeprefix(BASE)
        volume.external_inputs.setdefault(path,dict(url=spec['url'],title='Read '+spec['title'],note=''))
    volume.external_inputs['generated/references.tex']=dict(url=config['bib_page'],title='Read the collected references',note='')
    entries={}
    for match in re.finditer(r'\\VolumePartEntry\{([^{}]+)\}',volume.original_text):
        title,_=group(volume.original_text,match.end())
        number=match[1]
        spec=next(s for s,_,c in chapters if str(s.get('printed_chapter'))==number)
        entries[number]=(spec['url'],number+'. '+navigation_title(title))
    if set(entries)!={str(i) for i in range(1,22)}|set('ABCDEF'):
        raise ValueError('Review volume part-entry routes')
    volume.command_links['volumechapter']=entries


def bind_pdf_pages(reader,chapters,data):
    """Retain the result index's printed page column as links into the PDF."""
    import hashlib
    pdf=data['result_index_pdf'];record=reader.add(pdf['source'])
    if hashlib.sha256(reader.site.read_source(record)).hexdigest()!=pdf['sha256']:
        raise ValueError('Review result-index PDF identity')
    links={row['label']:(record['file_url']+'#page='+str(row['pdf_page']),str(row['printed_page'])) for row in pdf['rows']}
    for spec,_,chapter in chapters:
        if spec['source']==COVERAGE:chapter.command_links['pdfpage']=links
