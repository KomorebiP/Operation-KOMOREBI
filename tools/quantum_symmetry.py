"""Presentation rules for the retained symmetry treatment (chapters 3–7)."""
import re

SOURCE='monographs/quantum-and-circuits/volume/generated/s_main.tex'
MACROS='monographs/quantum-and-circuits/volume/generated/s_macros.tex'
FIGURES='assets/figures/quantum-symmetry/figures.json'
PANELS={'provedbox':'Proved statement','recordbox':'Recorded computation',
    'derivedbox':'Derived theorem or corollary','frontierbox':'Open program or boundary',
    'scopebox':'Scope boundary'}


def normalize(raw):
    """Translate declared print syntax, retaining source lines and semantic math."""
    from readable_chapters import clean_tex,group
    from quantum_reading import mask
    text=raw;lines=text.count('\n')
    # The atlas priority list has a small-font outer group across block nodes.
    for match in reversed(list(re.finditer(r'\{\\small(?=\s*\\begin\{enumerate\})',text))):
        _,end=group(text,match.start())
        text=text[:match.start()]+' '+text[match.start()+1:end-1]+' '+text[end:]
    text=clean_tex(text)
    # Chapter titles remain in the text; the source-bound page groups supply
    # their printed chapter numbers and reset the counters at those boundaries.
    text=re.sub(r'\\chapter\{',r'\\section*{',text)
    text=re.sub(r'\\index\{[^{}]*\}',lambda m:mask(m[0]),text)
    text=text.replace(r'\begin{enumerate}[nosep,leftmargin=*,label=\arabic*.]',r'\begin{enumerate}')
    for name,title in PANELS.items():
        text=text.replace(r'\begin{'+name+'}',r'\begin{interpretation}[title={'+title+'}]')
        text=text.replace(r'\end{'+name+'}',r'\end{interpretation}')
    text=text.replace(r'\begin{equation}',r'\[').replace(r'\end{equation}',r'\]')
    text=re.sub(r'\\begin\{figure\}\[H\]',r'\\begin{figure}',text)
    # A longtable's identical continuation header is a print repetition, not
    # a second mathematical row. Verify it before masking its repeated copy.
    def table(match):
        value=match[0]
        first,rest=value.split(r'\endfirsthead',1)
        repeated,tail=rest.split(r'\endhead',1)
        header=first[first.index(r'\toprule'):]
        if re.sub(r'\s+','',header)!=re.sub(r'\s+','',repeated):
            raise ValueError('Review changed symmetry continuation header')
        return first+mask(r'\endfirsthead'+repeated+r'\endhead')+tail
    text=re.sub(r'\\begin\{longtable\}.*?\\end\{longtable\}',table,text,flags=re.S)
    if text.count('\n')!=lines:raise ValueError('Symmetry translation moved source lines')
    return text


def source_macros(load):
    from readable_chapters import manuscript_macros
    macros=manuscript_macros(load(MACROS),[])
    # TeX permits one token as well as a braced argument: \ket\psi and \ket0.
    for name in ('ket','bra'):macros[name]['token_arguments']=True
    return macros


def number_chapter(chapter,spec,counters,equations):
    """Use the book's chapter-shared theorem, equation and float counters."""
    from readable_chapters import NUMBERED
    number=spec['printed_chapter']
    chapter.show_figure_numbers=True
    counts=counters.setdefault(number,dict(statement=0,equation=0,figure=0,table=0))
    chapter.proof_pairs={}
    for i,node in enumerate(chapter.nodes):
        if node['kind'] in NUMBERED:
            counts['statement']+=1;node['number']=str(number)+'.'+str(counts['statement'])
            if i+1<len(chapter.nodes) and chapter.nodes[i+1]['kind']=='proof':
                chapter.proof_pairs[node['id']]=chapter.nodes[i+1]['id']
        if node['kind'] in {'figure','longtable'}:
            key='figure' if node['kind']=='figure' else 'table'
            counts[key]+=1;node['number']=str(number)+'.'+str(counts[key])
    # Equation wrappers were translated to display math for the shared reader.
    # Their labels still resolve to the original printed equation number.
    for match in re.finditer(r'\\begin\{equation\}(.*?)\\end\{equation\}',chapter.original_text,re.S):
        counts['equation']+=1
        for label in re.findall(r'\\label\{([^{}]+)\}',match[1]):
            equations[label]=str(number)+'.'+str(counts['equation'])
