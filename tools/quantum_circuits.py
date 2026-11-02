"""Source-preserving presentation of circuit obstructions, chapters 13–21."""
import re

BASE='monographs/quantum-and-circuits/volume/'
SOURCE=BASE+'generated/c_main.tex'
VISUAL=BASE+'generated/c_visual.tex'
MACROS=BASE+'generated/c_macros.tex'
SUPPLEMENT=BASE+'generated/c_supplement.tex'
FIGURES='assets/figures/quantum-circuits/figures.json'


def normalize(raw):
    from readable_chapters import clean_tex
    from quantum_reading import mask,rewrite
    text=clean_tex(raw);lines=text.count('\n')
    text=text.replace(r'\chapter{',r'\section*{')
    # These are authored claim-group identifiers, not theorem counters.
    text=rewrite(text,'claim',1,lambda value:r'\textbf{CLAIM '+value+'}')
    text=re.sub(r'\\begin\{circuitscopebox\}\{([^{}]+)\}',
        lambda m:r'\begin{interpretation}[title={'+m[1]+'}]',text)
    text=text.replace(r'\end{circuitscopebox}',r'\end{interpretation}')
    text=text.replace(r'\begin{equation}',r'\[').replace(r'\end{equation}',r'\]')
    # This table has a single header, with no repeated continuation copy.
    text=re.sub(r'\\endhead\b|\\begin\{center\}|\\end\{center\}',lambda m:mask(m[0]),text)
    if text.count('\n')!=lines:raise ValueError('Circuit translation moved source lines')
    return text


def normalize_visual(raw):
    from readable_chapters import clean_tex
    from quantum_reading import mask,rewrite
    text=clean_tex(raw);lines=text.count('\n')
    text=rewrite(text,'guidepage',1,lambda title:r'\section*{'+title+'}')
    text=rewrite(text,'visualfigure',2,lambda name,caption:
        r'\begin{figure}\centering\includegraphics[width=.96\linewidth]{assets/c_'+name+r'.pdf}\caption{'+caption+r'}\end{figure}')
    text=rewrite(text,'evidence',1,lambda prose:r'\emph{'+prose+'}')
    # The print preamble explicitly suppresses sourcepath. Its literal content
    # stays available in the linked, immutable TeX rather than becoming prose.
    text=rewrite(text,'sourcepath',1,lambda prose:mask(prose))
    text=re.sub(r'\\begin\{(?:center|quote)\}|\\end\{(?:center|quote)\}|\\small\b',lambda m:mask(m[0]),text)
    # tabularx's X columns become flexible HTML columns; no cells are changed.
    text=text.replace(r'\begin{tabularx}{\textwidth}',r'\begin{tabular}').replace(r'\end{tabularx}',r'\end{tabular}')
    if text.count('\n')!=lines:raise ValueError('Circuit visual translation moved source lines')
    return text


def source_macros(load,visual=False):
    from readable_chapters import manuscript_macros
    source=load(MACROS)
    macros=manuscript_macros(source,[])
    # These two definitions are renewcommands in the retained local scope.
    if r'\renewcommand{\F}{\mathbb F_2}' not in source or r'\renewcommand{\B}{\{0,1\}}' not in source:
        raise ValueError('Review circuit field and Boolean conventions')
    macros.update(F=r'\mathbb F' if visual else r'\mathbb F_2',B=r'\{0,1\}')
    return macros


def bind_source_references(reader,load,labels):
    """Route the one cited unconverted appendix section to its retained lines."""
    text=load(SUPPLEMENT)
    headings=list(re.finditer(r'\\section\{([^{}]+)\}',text))
    match=re.search(r'\\label\{c:app:evidence\}',text)
    if not match:raise ValueError('Missing circuit evidence section')
    section=max((i,m) for i,m in enumerate(headings,1) if m.start()<match.start())
    number,heading=section
    if number!=4 or heading[1]!='Baseline domains reproduced by the full run':
        raise ValueError('Review circuit appendix reference')
    record=reader.add(SUPPLEMENT)
    labels['c:app:evidence']=dict(kind='heading',number='E.4',title=heading[1],
        reference_label='Section E.4 (manuscript source)',plain_reference_label='E.4',
        url=record['url'],id='L'+str(text.count('\n',0,heading.start())+1))
