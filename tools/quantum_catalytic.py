"""Source-bound presentation of catalytic gate-set distortion, chapters 8–12."""
import re

SOURCE='monographs/quantum-and-circuits/volume/generated/g_main.tex'
MACROS='monographs/quantum-and-circuits/volume/generated/g_macros.tex'
FIGURES='assets/figures/quantum-catalytic/figures.json'
PANELS={'provedbox':'Proved statement','computedbox':'Exact finite computation',
    'skeletonbox':'Research template','conjecturebox':'Conjectural frontier',
    'boundarybox':'Scope boundary'}


def numbered_gate_rows(body):
    """The one numbered align block contains six separate gate assignments."""
    from readable_chapters import split_cells
    rows=[row for row in split_cells(body,r'\\') if row.strip()]
    labels=[re.findall(r'\\label\{([^{}]+)\}',row) for row in rows]
    if labels!=[['g:gate:a'+str(i)] for i in range(1,7)] or any(row.count('&')!=1 for row in rows):
        raise ValueError('Review catalytic numbered gate alignment')
    return [row.replace('&','').strip('\n') for row in rows]


def normalize(raw):
    from readable_chapters import clean_tex,group
    from quantum_reading import mask,rewrite
    text=clean_tex(raw);lines=text.count('\n')
    text=re.sub(r'\\chapter\{',r'\\section*{',text)
    text=re.sub(r'\\index\{[^{}]*\}',lambda m:mask(m[0]),text)
    text=rewrite(text,'texorpdfstring',2,lambda printed,bookmark:printed)
    text=text.replace(r'label=\textup{(\roman*)}',r'label=(\roman*)')
    for name,title in PANELS.items():
        text=text.replace(r'\begin{'+name+'}',r'\begin{interpretation}[title={'+title+'}]')
        text=text.replace(r'\end{'+name+'}',r'\end{interpretation}')
    text=re.sub(r'\\begin\{(figure|table)\}\[[htbpH]+\]',r'\\begin{\1}',text)
    text=re.sub(r'\\begin\{center\}|\\end\{center\}|\\begin\{quote\}|\\end\{quote\}',lambda m:mask(m[0]),text)
    # Print scaling around the Green-signature table changes no table content.
    text=rewrite(text,'resizebox',3,lambda width,height,body:body)
    # Preserve the closing question, replacing its print-only frame by emphasis.
    text=rewrite(text,'fbox',1,lambda body:body)
    text=rewrite(text,'parbox',2,lambda width,body:r'\emph{'+body.replace(r'\centering','')+'}')
    # Keep authored code captions; the shared listing renderer retains code
    # verbatim and source anchors. Both wrappers stay on their original line.
    text=re.sub(r'\\begin\{lstlisting\}\[style=(?:pythonstyle|cppstyle),caption=\{([^{}]+)\}\]',
        lambda m:r'\paragraph*{'+m[1]+r'}\begin{lstlisting}',text)
    # Remove only the identical continuation header in the twenty-matrix table.
    def table(match):
        value=match[0]
        if r'\endfirsthead' not in value:return value
        first,rest=value.split(r'\endfirsthead',1);repeated,tail=rest.split(r'\endhead',1)
        if re.sub(r'\s+','',first[first.index(r'\toprule'):])!=re.sub(r'\s+','',repeated):
            raise ValueError('Review catalytic continuation header')
        return first+mask(r'\endfirsthead'+repeated+r'\endhead')+tail
    text=re.sub(r'\\begin\{longtable\}.*?\\end\{longtable\}',table,text,flags=re.S)
    # Six separately numbered equations become six displays, retaining each
    # assignment and label on its original line. Alignment & is print layout.
    def alignment(match):
        rows=numbered_gate_rows(match[1]);result=[];i=0
        for line in match[1].splitlines(keepends=True):
            if line.strip():
                result.append(r'\['+rows[i]+r'\]'+ ('\n' if line.endswith('\n') else ''));i+=1
            else:result.append(line)
        return mask(r'\begin{align}')+''.join(result)+mask(r'\end{align}')
    text=re.sub(r'\\begin\{align\}(.*?)\\end\{align\}',alignment,text,flags=re.S)
    text=text.replace(r'\begin{equation}',r'\[').replace(r'\end{equation}',r'\]')
    if text.count('\n')!=lines:raise ValueError('Catalytic translation moved source lines')
    return text


def source_macros(load):
    from readable_chapters import manuscript_macros,group
    source=load(MACROS);macros=manuscript_macros(source,[])
    expected={'ellBudget':1,'ellWeight':1,'tauGate':3,'ellExc':2,'ket':1,'bra':1,'braket':2}
    declarations=list(re.finditer(r'\\providecommand\{\\([A-Za-z]+)\}\[(\d+)\]',source))
    if {m[1]:int(m[2]) for m in declarations}!=expected:
        raise ValueError('Review catalytic argument macros')
    for match in declarations:
        body,_=group(source,match.end());arguments=int(match[2])
        if set(re.findall(r'#(\d)',body))!={str(i) for i in range(1,arguments+1)}:
            raise ValueError('Review catalytic macro parameters')
        macros[match[1]]=dict(arguments=arguments,body=body,token_arguments=True)
    return macros


def bind_named_proofs(chapters,labels):
    """Resolve only the eight explicit 'Proof of \\cref{...}' source titles."""
    from readable_chapters import NUMBERED
    by_url={spec['url']:chapter for spec,_,chapter in chapters};count=0
    for spec,_,chapter in chapters:
        if spec['source']!=SOURCE:continue
        chapter.proof_returns={}
        for node in chapter.nodes:
            if node['kind']!='proof' or not node['title']:continue
            match=re.fullmatch(r'Proof of \\cref\{(g:[^{}]+)\}',node['title'])
            if not match:raise ValueError('Review catalytic named proof title')
            statement=labels[match[1]];owner=by_url[statement['url']]
            if statement['kind'] not in NUMBERED or statement['id'] in owner.proof_pairs:
                raise ValueError('Ambiguous catalytic named proof')
            if not hasattr(owner,'proof_routes'):owner.proof_routes={}
            if statement['id'] in owner.proof_routes:raise ValueError('Duplicate catalytic named proof')
            owner.proof_routes[statement['id']]=chapter.url+'#'+node['id']
            chapter.proof_returns[node['id']]=owner.url+'#'+statement['id']
            node['display_title']=node['title']
            node['search_title']='Proof of '+statement['reference_label'];count+=1
    if count!=8:raise ValueError('Review catalytic named-proof inventory')
