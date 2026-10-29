"""Publish source-preserving HTML reading chapters with explicit syntax coverage.

Unknown prose commands or environments stop the build. Mathematics remains TeX
for MathJax, expanding literal manuscript macros and supported math wrappers.
This is presentation tooling, not a mathematical review or a general TeX engine.
"""
import hashlib
import html
import json
import re
import posixpath
import unicodedata

BASE = 'papers/paper-ii/current/editable/traditional/'
SOURCE = BASE+'chapters/02_coordinates.tex'
MAIN = BASE+'Paper_II_Traditional_Final.tex'
BIB = BASE+'Paper_II_Traditional_Final.bbl'
BIB_SOURCE = BASE+'references.bib'
PAGE = 'read/paper-ii/refinement-and-residue-coordinates.html'
TITLE = 'Paper II: Refinement and residue coordinates'
INDEX = 'read/paper-ii/index.html'
BIB_PAGE = 'read/paper-ii/references.html'
CHAPTERS = [
    ('chapters/01_orientation.tex','orientation','Orientation'),
    ('chapters/02_coordinates.tex','refinement-and-residue-coordinates','Refinement and residue coordinates'),
    ('chapters/03_weighted.tex','weighted-transfer','Weighted transfer'),
    ('chapters/04_arithmetic.tex','integral-separation','Integral separation and Smith congruences'),
    ('chapters/05_defects.tex','refinement-defects','Linear refinement defects'),
    ('chapters/06_models.tex','models-and-algorithms','Worked models, tables and algorithms'),
    ('chapters/07_scope.tex','edition-and-proof-scope','Edition and proof scope'),
    ('generated/current_scope.tex','current-verification-scope','Current verification snapshot'),
]
CHAPTERS = [dict(source=BASE+p,url='read/paper-ii/'+slug+'.html',title=title,work='paper-ii') for p,slug,title in CHAPTERS]
BOOKS = {'paper-ii':dict(work='paper-ii',label='Paper II',base=BASE,main=MAIN,bib=BIB_SOURCE,index=INDEX,bib_page=BIB_PAGE,
                       title='Refinement, weighted transfer and integral separation',chapters=CHAPTERS[:],main_chapters=7)}
THIRD_BASE = 'papers/paper-iii/current/manuscript/'
THIRD_CHAPTERS = [
    ('01_finite_coordinates.tex','finite-coordinates','Finite coordinates and typed transfer'),
    ('02_connections_obstructions.tex','connections-and-obstructions','Connections and obstruction witnesses'),
    ('03_nonlinear_coordinates.tex','nonlinear-coordinates','Nonlinear packet coordinates'),
    ('04_correction_transport.tex','correction-and-transport','Correction, lifting and smooth transport'),
]
THIRD_CHAPTERS = [dict(source=THIRD_BASE+'chapters/'+p,url='read/paper-iii/'+slug+'.html',title=t,work='paper-iii') for p,slug,t in THIRD_CHAPTERS]
BOOKS['paper-iii']=dict(work='paper-iii',label='Paper III',base=THIRD_BASE,main=THIRD_BASE+'Paper_III_Traditional_Final.tex',
                       bib=THIRD_BASE+'references.bib',index='read/paper-iii/index.html',bib_page='read/paper-iii/references.html',
                       title='Typed transfer, nonlinear packets and obstruction theory',chapters=THIRD_CHAPTERS,main_chapters=4)
CHAPTERS += THIRD_CHAPTERS
FIRST_BASE = 'papers/paper-i/current/editable/traditional/'
FIRST_CHAPTERS = [
    ('01_orientation.tex', 'orientation', "Reader’s orientation"),
    ('02_foundations.tex', 'foundations-and-seed-rank', 'Foundations and seed rank'),
    ('03_packets_and_graphs.tex', 'packets-and-transfer-graphs', 'Packets and transfer graphs'),
    ('04_transport.tex', 'transport-and-realization', 'Transport and realization'),
    ('05_worked_models.tex', 'worked-models', 'Worked models and calculations'),
    ('06_reference.tex', 'reference-and-concordance', 'Notation, concordance and references'),
]
FIRST_CHAPTERS = [dict(source=FIRST_BASE+p, url='read/paper-i/'+slug+'.html', title=t, work='paper-i')
                  for p, slug, t in FIRST_CHAPTERS]
BOOKS = {'paper-i': dict(work='paper-i', label='Paper I', base=FIRST_BASE,
                        main=FIRST_BASE+'Paper_I_Monograph.tex', bib=FIRST_BASE+'06_reference.tex',
                        inline_bibliography=True, index='read/paper-i/index.html',
                        bib_page='read/paper-i/references.html',
                        title='Typed operator systems, seed rank and exact packet coordinates',
                        chapters=FIRST_CHAPTERS, main_chapters=6, chapter_prefix='',
                        diagram_guide='collection/PAPER_I_DIAGRAMS.html',
                        figure_descriptions='website/paper-i-figure-descriptions.json',
                        pdf_inputs={'visual_atlas.tex': 'Read the 22-plate visual atlas in the PDF'}), **BOOKS}
CHAPTERS = FIRST_CHAPTERS + CHAPTERS
FOURTH_BASE = 'papers/paper-iv/current/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/'
FOURTH_MAIN = FOURTH_BASE+'Paper_IV_Traditional_Final.tex'
# Inclusive, contiguous source ranges. Boundaries are checked before conversion;
# padding retains the manuscript's original line numbers on every chapter page.
FOURTH_SECTIONS = [
    (170, 'orientation', 'Orientation and formal scope'),
    (211, 'introduction', 'Introduction'),
    (268, 'construction-map', 'A map of the construction'),
    (324, 'cyclic-projection', 'Cyclic projection of analytic functions'),
    (430, 'transfer-exponential', 'The transfer exponential basis'),
    (577, 'signed-sections', 'Signed cyclic sections and the distinguished denominator'),
    (750, 'finite-algebra', 'A finite algebra and matrix model'),
    (917, 'reciprocal-powers', 'Reciprocal powers and parameter polynomials'),
    (1217, 'logarithmic-derivatives', 'Logarithmic derivatives and Riccati equations'),
    (1351, 'appell-systems', 'Residue-section reciprocals and Appell systems'),
    (1607, 'theta-polynomials', 'Scaled reciprocal coupling and theta polynomials'),
    (1708, 'zero-geometry', 'Growth and the geometry of the large zeros'),
    (2260, 'products-and-moments', 'Hadamard products and zero power sums'),
    (2588, 'coefficient-asymptotics', 'Coefficient asymptotics from the nearest zeros'),
    (2712, 'zero-zeta', 'Zero zeta functions'),
    (2946, 'scope-boundaries', 'Scope boundaries and further questions'),
    (2974, 'formalization-ledger', 'Formalization ledger for version 1.0.0'),
    (3087, 'conclusion', 'Conclusion'),
    (3109, 'visual-atlas', 'Visual atlas'),
]
FOURTH_CHAPTERS = [dict(source=FOURTH_MAIN, url='read/paper-iv/'+slug+'.html', title=title, work='paper-iv',
                        start_line=start, end_line=FOURTH_SECTIONS[i+1][0]-1 if i+1<len(FOURTH_SECTIONS) else 3123)
                   for i,(start,slug,title) in enumerate(FOURTH_SECTIONS)]
BOOKS['paper-iv'] = dict(work='paper-iv', label='Paper IV', base=FOURTH_BASE, main=FOURTH_MAIN,
                        bib=FOURTH_BASE+'references.bib', index='read/paper-iv/index.html',
                        bib_page='read/paper-iv/references.html',
                        title='Cyclic analytic functions, reciprocal families, and spectral zero data',
                        chapters=FOURTH_CHAPTERS, main_chapters=17, monolithic=True,
                        atlas_index='read/paper-iv/atlas/index.html',
                        html_inputs={'atlas-pages': dict(url='read/paper-iv/atlas/index.html',title='Explore the 26 atlas plates in HTML',note='')})
CHAPTERS += FOURTH_CHAPTERS
BY_SOURCE = {c['source']:c for c in reversed(CHAPTERS)}
NUMBERED = {'definition', 'theorem', 'proposition', 'lemma', 'corollary', 'remark', 'example', 'standardfact', 'certificate','boundary','roadmap','construction','classicalinput'}
KIND_NAMES = {'standardfact':'Standard fact','certificate':'Numerical certificate','text':'Passage','roadmap':'Formalization target','classicalinput':'Classical input'}
HEADINGS = {'part':2,'section':2,'subsection':3,'subsubsection':4,'paragraph':5}
MATH_PATTERN = re.compile(r'(?<!\\)\$(.*?)(?<!\\)\$|\\\[(.*?)\\\]|(\\begin\{align\*\}.*?\\end\{align\*\})|\\\((.*?)\\\)',re.S)
PANELS = {'keyidea': 'The central idea', 'interpretation': 'How to read the result',
          'readerroadmap': 'Reader roadmap', 'microexample': 'Running example',
          'hypothesisguide': 'Why the hypotheses matter', 'sectionrecap': 'Section recap',
          'warningbox': 'Do not conflate'}
BLOCKS = NUMBERED | set(PANELS) | {'proof','figure','table','longtable','tabularx','lstlisting','thebibliography','conceptchain'}
MACROS = {'Pcal', 'Qcal', 'Rcal', 'Acal', 'Scal', 'cA', 'cS', 'End', 'id', 'bbk'}
# Search aliases describe notation, not new equivalences between mathematical claims.
SYMBOLS = {'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'rho': 'ρ', 'omega': 'ω',
           'eta': 'η', 'delta': 'δ', 'ell': 'ℓ', 'sum': 'sum', 'bigoplus': 'direct sum',
           'oplus': 'direct sum', 'subseteq': 'subset', 'in': 'in', 'longrightarrow': 'maps to',
           'to': 'maps to', 'leftarrow': 'from', 'circ': 'composition', 'equiv': 'congruent',
           'ne': 'not equal', 'le': 'less than or equal', 'leq': 'less than or equal',
           'geq': 'greater than or equal', 'pmod': 'modulo', 'bmod': 'modulo'}


def clean_tex(text):
    # Retain newlines for exact links to the unchanged source file.
    parts = re.split(r'(\\begin\{lstlisting\}.*?\\end\{lstlisting\})',text,flags=re.S)
    for i in range(0,len(parts),2):
        parts[i] = re.sub(r'(?<!\\)%[^\n]*', '', parts[i])
        parts[i] = re.sub(r'\\(?:Needspace|enlargethispage)\{[^{}]*\}',lambda m:' '*len(m[0]),parts[i])
        parts[i] = re.sub(r'\\phantomsection\b',lambda m:' '*len(m[0]),parts[i])
        parts[i] = re.sub(r'\\setlength\{\\(?:above|below)displayskip\}\{[^{}]*\}',lambda m:' '*len(m[0]),parts[i])
        parts[i] = re.sub(r'\\(?:clearpage|medskip|noindent|small|normalsize|begingroup|endgroup)\b',lambda m:' '*len(m[0]),parts[i])
    return ''.join(parts)


def presentation_tex(text):
    """Mask known print-only layout, preserving all source line numbers."""
    mask = lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0])
    text = re.sub(r'\\(?:begin|end)\{center\}|\\begin\{multicols\}\{2\}|\\end\{multicols\}', mask, text)
    text = re.sub(r'\\addcontentsline\{toc\}\{section\}\{[^{}]*\}', mask, text)
    text = re.sub(r'\\fontsize\{[\d.]+\}\{[\d.]+\}|\\setstretch\{[\d.]+\}|\\selectfont\b', mask, text)
    text = re.sub(r'\\setlength\{\\(?:parindent|parskip)\}\{[^{}]*\}', mask, text)
    text = re.sub(r'\\(?:begin|end)\{document\}|\\(?:KomorebiCover|tableofcontents|listoffigures)\b|\\pagenumbering\{arabic\}', mask, text)
    # This exact wrapper only changes spacing in the printed bibliography.
    text = re.sub(r'\\let\\prscbibliography\\thebibliography\s*\\renewcommand\{\\thebibliography\}\[1\]\{\\prscbibliography\{#1\}\\setlength\{\\itemsep\}\{0pt\}\\setlength\{\\parsep\}\{0pt\}\}', mask, text)
    text = re.sub(r'\\bibliographystyle\{alpha\}', mask, text)
    text = text.replace(r'\begin{abstract}', r'\begin{readerroadmap}[title={Abstract}]').replace(r'\end{abstract}', r'\end{readerroadmap}')
    while (match := re.search(r'\\KomorebiOpeningNote\{', text)):
        value,end = group(text, match.end()-1)
        text = text[:match.start()] + r'\begin{readerroadmap}[title={Reading orientation}]' + value + r'\end{readerroadmap}' + text[end:]
    while (match := re.search(r'\\modelfigure\{', text)):
        path,end = group(text, match.end()-1)
        caption,end = group(text, end)
        label,end = group(text, end)
        text = text[:match.start()] + r'\begin{figure}\centering\includegraphics[width=.98\linewidth]{' + path + r'.pdf}\caption{' + caption + r'}\label{' + label + r'}\end{figure}' + text[end:]
    # These macros are explicitly empty in the manuscript preamble.
    while (match := re.search(r'\\(?:Depends|Exports)\{', text)):
        _, end = group(text, match.end()-1)
        text = text[:match.start()] + ''.join('\n' if c=='\n' else ' ' for c in text[match.start():end]) + text[end:]
    text = re.sub(r'\\RecordID\{([^{}]+)\}', r'\\label{record:\1}', text)
    text = re.sub(r'''\{(\\['`"](?:\{[A-Za-z]\}|[A-Za-z]))\}''', lambda m:tex_accents(m[1]), text)
    while (match := re.search(r'\\ConceptChain\{', text)):
        value, end = group(text, match.end()-1)
        text = text[:match.start()] + r'\begin{conceptchain}' + value + r'\end{conceptchain}' + text[end:]
    return text


def original_math(text):
    text = re.sub(r'\\begin\{lstlisting\}.*?\\end\{lstlisting\}', '', clean_tex(text),flags=re.S)
    return [next(x for x in m.groups() if x is not None) for m in MATH_PATTERN.finditer(text)]


def tex_accents(text):
    accents={"'":'\u0301','`':'\u0300','"':'\u0308'}
    return re.sub(r'''\\(['`"])(?:\{([A-Za-z])\}|([A-Za-z]))''',lambda m:unicodedata.normalize('NFC',(m[2] or m[3])+accents[m[1]]),text)


def typography(text):
    text = tex_accents(text)
    return text.replace('``','“').replace("''",'”').replace('~','\u00a0')


def group(text, start, opening='{', closing='}'):
    if start >= len(text) or text[start] != opening:
        raise ValueError('Expected '+opening+' at '+str(start))
    depth = 1
    i = start+1
    while i < len(text):
        if text[i] == '\\':
            i += 2
            continue
        if text[i] == opening: depth += 1
        if text[i] == closing: depth -= 1
        if not depth: return text[start+1:i], i+1
        i += 1
    raise ValueError('Unclosed group')


def manuscript_macros(main):
    result = {}
    for m in re.finditer(r'\\(newcommand|providecommand)\{\\([A-Za-z]+)\}', main):
        if m[2] in result or main[m.end():m.end()+1] != '{': continue
        value, _ = group(main, m.end())
        if '#' in value: raise ValueError('Argument macro is outside the reading pilot')
        result[m[2]] = value
    required = {'CC','Dfun','Thetafun','Pcal','id'} if r'\newcommand{\Dfun}' in main else {'Pcal', 'Qcal', 'Rcal', 'Scal', 'End', 'id', 'bbk'}
    if not required <= set(result):
        raise ValueError('Missing manuscript macro definitions')
    # Only the literal, one-argument math wrappers used by the reading editions.
    for name in ('cl', 'closure', 'norm', 'mat'):
        match = re.search(r'\\newcommand\{\\'+name+r'\}\[1\]', main)
        if match:
            value, _ = group(main, match.end())
            if re.search(r'#(?!1)', value): raise ValueError('Unsupported math macro argument')
            result[name] = dict(arguments=1, body=value)
    return result


def formal_note_labels(main):
    """Read scope labels from the retained manuscript's argument macros."""
    labels={}
    for name in ('statusleanthree','statusleanprior','statusroadmap'):
        match=re.search(r'\\newcommand\{\\'+name+r'\}\[1\]',main)
        if not match: continue
        body,_=group(main,match.end())
        label=re.search(r'\\textbf\{([^{}]+)\}',body)
        if not label: raise ValueError('Missing source scope label: '+name)
        labels[name]=typography(label[1]).replace('--','–')
    return labels


def expand_math(tex, macros):
    tex = re.sub(r'\\label\{[^{}]+\}', '',tex)
    tex = tex_accents(tex)
    if tex.startswith(r'\begin{align*}'):
        tex = tex.replace(r'\begin{align*}',r'\begin{aligned}',1).removesuffix(r'\end{align*}')+r'\end{aligned}'
    for _ in range(10):
        pieces=[]
        pos=0
        for match in re.finditer(r'\\\\|\\([A-Za-z]+)', tex):
            if match.start()<pos: continue
            pieces.append(tex[pos:match.start()])
            value=macros.get(match[1])
            pos=match.end()
            if isinstance(value, dict):
                while pos<len(tex) and tex[pos].isspace(): pos+=1
                if tex[pos:pos+1]!='{': raise ValueError('Math macro requires a braced argument: '+match[1])
                argument,pos=group(tex,pos)
                pieces.append('{'+value['body'].replace('#1',argument)+'}')
            else: pieces.append('{'+value+'}' if value is not None else match[0])
        pieces.append(tex[pos:])
        expanded=''.join(pieces)
        # unicode-math's upright alphabet has the same presentation here as
        # MathJax's supported upright command; retain the original in receipts.
        if expanded == tex: return re.sub(r'\\symup\b', r'\\mathrm', tex)
        tex = expanded
    raise ValueError('Recursive manuscript macro')


def plain_math(tex):
    names = []
    def replace(m):
        name = m[1]
        if name in SYMBOLS:
            names.append(name)
            return ' '+SYMBOLS[name]+' '
        return ' '+({'Pcal':'P','Qcal':'Q','Rcal':'R','Acal':'A','Scal':'S',
                     'cA':'A','cS':'S','bbk':'k','End':'End','id':'id'}.get(name, name))+' '
    text = re.sub(r'\\([A-Za-z]+)', replace, tex)
    return re.sub(r'\s+', ' ', re.sub(r'[{}_^\\]', ' ', text)).strip(), ' '.join(names)


class Chapter:
    def __init__(self, text, macros, section_offset=0, state=None, check_refs=True):
        self.text = presentation_tex(clean_tex(text))
        self.macros = macros
        self.formal_labels = {}
        self.external_inputs = {}
        self.command_links = {}
        self.related_readings = {}
        self.math = []
        self.labels = {}
        self.nodes = []
        self.references = []
        state = state or {}
        self.section = state.get('section',section_offset)
        self.part = state.get('part',0)
        self.appendix = state.get('appendix',False)
        self.subsection = self.subsubsection = self.counter = 0
        self.url = ''
        self.base = BASE
        self.parse()
        if check_refs: self.validate_references()

    def section_number(self):
        return chr(64+self.section) if self.appendix else str(self.section)

    def line(self, pos): return self.text.count('\n', 0, pos)+1

    def parse(self):
        text = self.text
        pos = 0
        while pos < len(text):
            if text[pos].isspace():
                pos += 1
                continue
            start = pos
            if text.startswith('\\appendix',pos):
                self.appendix=True
                self.section=self.subsection=self.subsubsection=self.counter=0
                pos += len('\\appendix')
                continue
            heading = re.match(r'\\(part|section|subsection|subsubsection|paragraph)(\*)?\{', text[pos:])
            env = re.match(r'\\begin\{([a-z]+)\}', text[pos:])
            if heading:
                title, pos = group(text, pos+heading.end()-1)
                if heading[2]: number=''
                elif heading[1]=='part':
                    self.part+=1
                    number='Part '+('I','II','III','IV','V','VI','VII','VIII','IX','X')[self.part-1]
                elif heading[1] == 'section':
                    self.section += 1
                    self.subsection = self.subsubsection = self.counter = 0
                    number = self.section_number()
                elif heading[1] == 'subsection':
                    self.subsection += 1
                    self.subsubsection=0
                    number = self.section_number()+'.'+str(self.subsection)
                elif heading[1] == 'subsubsection':
                    self.subsubsection += 1
                    number = self.section_number()+'.'+str(self.subsection)+'.'+str(self.subsubsection)
                else: number = ''
                node = dict(kind=heading[1], title=title, number=number, body='')
            elif env:
                kind = env[1]
                if kind not in BLOCKS | {'enumerate','itemize','description'}:
                    raise ValueError('Unsupported reading environment: '+kind)
                pos += env.end()
                title = ''
                if text[pos:pos+1] == '[': title, pos = group(text, pos, '[', ']')
                if kind in PANELS and title:
                    if not title.startswith('title={'): raise ValueError('Unsupported panel option: '+title)
                    title, option_end = group(title, len('title='))
                    if option_end != len('title={'+title+'}'): raise ValueError('Unsupported panel options')
                end_tag = '\\end{'+kind+'}'
                end = text.find(end_tag, pos)
                if end < 0: raise ValueError('Unclosed '+kind)
                body = text[pos:end]
                pos = end+len(end_tag)
                if kind in {'enumerate','itemize','description'}:
                    kind,body='text',text[start:pos]
                number = ''
                if kind in NUMBERED:
                    self.counter += 1
                    number = self.section_number()+'.'+str(self.counter)
                node = dict(kind=kind, title=title, number=number, body=body)
            else:
                match = re.search(r'\\(?:part|section|subsection|subsubsection|paragraph)\*?\{|\\appendix\b|\\begin\{(?:'+
                                  '|'.join(sorted(BLOCKS))+r')\}', text[pos:])
                pos = pos+match.start() if match else len(text)
                node = dict(kind='text', title='', number='', body=text[start:pos])
            # Labels immediately after headings belong to those headings.
            if heading:
                while (m := re.match(r'\s*\\label\{([^{}]+)\}', text[pos:])):
                    node['body'] += m[0]
                    pos += m.end()
            labels = re.findall(r'\\label\{([^{}]+)\}', node['body'])
            if node['kind']=='text' and not re.sub(r'\\label\{[^{}]+\}', '', node['body']).strip():
                if labels and not self.nodes: raise ValueError('Unattached manuscript label')
                for label in labels:
                    if label in self.labels: raise ValueError('Duplicate chapter label '+label)
                    self.nodes[-1]['labels'].append(label)
                    self.labels[label]=self.nodes[-1]
                continue
            line=self.line(start)
            on_line=sum(n['line']==line for n in self.nodes)
            identifier='L'+str(line)+('-'+str(on_line+1) if on_line else '')
            node.update(line=line, end_line=self.line(pos), id=identifier, labels=labels,section=self.section_number())
            for label in labels:
                if label in self.labels: raise ValueError('Duplicate chapter label '+label)
                self.labels[label] = node
            self.nodes.append(node)
    def validate_references(self):
        # Resolve the whole paper before rendering references between chapters.
        for node in self.nodes:
            for keys in re.findall(r'\\(?:c|C|eq)?ref\{([^{}]+)\}', node['body']):
                for key in keys.split(','):
                    if key not in self.labels: raise ValueError('Unresolved chapter reference: '+key)

    def inline(self, text):
        out = []
        pos = 0
        while pos < len(text):
            math = MATH_PATTERN.match(text,pos)
            if math:
                display = math[1] is None and math[4] is None
                tex = next(x for x in math.groups() if x is not None)
                self.math.append(tex)
                tag = 'div' if display else 'span'
                extra = ' tabindex="0" role="group" aria-label="Displayed equation. Scroll horizontally if needed."' if display else ''
                out.append('<'+tag+' class="arithmatex"'+extra+'>'+html.escape(
                    ('\\[' if display else '\\(')+expand_math(tex,self.macros)+('\\]' if display else '\\)'))+'</'+tag+'>')
                pos = math.end()
            elif text[pos]=='$':
                raise ValueError('Unclosed inline mathematics')
            elif text[pos] == '\\':
                if text[pos:pos+2] in {r'\_',r'\&',r'\%',r'\#',r'\$'}:
                    out.append(html.escape(text[pos+1]));pos+=2;continue
                accent = re.match(r'''\\['`"](?:\{[A-Za-z]\}|[A-Za-z])''',text[pos:])
                if accent:
                    out.append(html.escape(typography(accent[0]))); pos += accent.end(); continue
                m = re.match(r'\\([A-Za-z]+)', text[pos:])
                if not m: raise ValueError('Unsupported prose escape at '+text[pos:pos+40])
                name = m[1]
                pos += m.end()
                if name in {'S','textquotesingle'}:
                    out.append('§' if name=='S' else '’')
                    if text[pos:pos+1]==' ': pos+=1
                    continue
                if name=='newline':
                    out.append('<br>')
                    continue
                option = None
                if text[pos:pos+1]=='[': option,pos=group(text,pos,'[',']')
                if text[pos:pos+1]!='{': raise ValueError('Missing argument for '+name+' in '+repr(text[:200]))
                value, pos = group(text, pos)
                if name == 'label': continue
                if name in self.command_links:
                    if value not in self.command_links[name]: raise ValueError('Unresolved reading link: '+name+' '+value)
                    target,label=self.command_links[name][value]
                    out.append('<a href="'+html.escape(self.relative(target),quote=True)+'">'+html.escape(label)+'</a>')
                elif name in {'textbf','emph','textit','texttt','leanname','path','nolinkurl'}:
                    tag = {'textbf':'strong','texttt':'code','leanname':'code','path':'code','nolinkurl':'code'}.get(name,'em')
                    content=html.escape(value.replace(r'\_','_')) if tag=='code' else self.inline(value)
                    out.append('<'+tag+'>'+content+'</'+tag+'>')
                elif name in {'statusleanthree','statusleanprior','statusroadmap'}:
                    if name not in self.formal_labels: raise ValueError('Missing manuscript scope label: '+name)
                    label=html.escape(self.formal_labels[name])
                    content=self.inline(value) if name=='statusroadmap' else '<code>'+html.escape(value)+'</code>'
                    out.append('<span class="source-formal-note"><strong>'+label+'</strong> '+content+'</span>')
                elif name in {'cref','Cref','ref','eqref'}:
                    links = []
                    for key in value.split(','):
                        node = self.labels[key]
                        label = KIND_NAMES.get(node['kind'],node['kind'].capitalize())+' '+node['number']
                        url = self.relative(node.get('url',''))+'#'+node['id']
                        links.append('<a href="'+url+'" title="'+html.escape(typography(node['title']),quote=True)+'">'+label+'</a>')
                    out.append(', '.join(links))
                    self.references.extend(value.split(','))
                elif name == 'cite':
                    links = []
                    for key in value.split(','):
                        number, url = self.citations[key]
                        links.append('<a href="'+html.escape(url,quote=True)+'" aria-label="Reference '+str(number)+': '+html.escape(key,quote=True)+'">['+str(number)+']</a>')
                    out.append(', '.join(links))
                    if option: out.append(', '+self.inline(option))
                elif name == 'bibliography':
                    if value!='references' or not getattr(self,'bibliography_url',None): raise ValueError('Unsupported bibliography route')
                    out.append('<a href="'+html.escape(self.relative(self.bibliography_url),quote=True)+'">Read the bibliography</a>')
                elif name == 'input':
                    if value in self.external_inputs:
                        target=self.external_inputs[value]
                        out.append('<a class="included-reading" href="'+html.escape(self.relative(target['url']),quote=True)+'">'+html.escape(target['title'])+'</a>'+target.get('note',' (this atlas is not converted to HTML)'))
                        continue
                    path = posixpath.normpath(self.base+value)
                    target = BY_SOURCE.get(path)
                    if not target: raise ValueError('Unselected chapter input: '+path)
                    out.append('<a class="included-reading" href="'+self.relative(target['url'])+'">Read '+html.escape(target['title'].lower())+'</a>')
                elif name=='href':
                    label,pos=group(text,pos)
                    if not value.startswith(('https://','http://')): raise ValueError('Unsupported bibliography URL')
                    out.append('<a href="'+html.escape(value,quote=True)+'">'+self.inline(label)+'</a>')
                else: raise ValueError('Unsupported prose command: '+name)
            else:
                m = re.match(r'[^$\\]+', text[pos:])
                literal = m[0]
                if '$' in literal or '{' in literal or '}' in literal: raise ValueError('Unparsed prose or math grouping')
                out.append(html.escape(typography(re.sub(r'\s+', ' ', literal))))
                pos += len(literal)
        return ''.join(out)

    def relative(self,target):
        if not target or target==self.url: return ''
        return posixpath.relpath(target,posixpath.dirname(self.url) or '.')

    def paragraphs(self, text):
        # Separate paragraphs outside math. A display splits paragraph elements,
        # but its exact mathematical source is passed unchanged to inline().
        # Lists can occur inside statements. Keep them semantic and preserve order.
        description=re.search(r'\\begin\{description\}(?:\[([^\]]*)\])?(.*?)\\end\{description\}',text,re.S)
        if description:
            if description[1] not in (None, r'style=nextline,font=\normalfont\bfseries'):
                raise ValueError('Unsupported description options')
            items=re.split(r'\\item\[([^\]]+)\]',description[2])
            if items[0].strip() or len(items)%2!=1: raise ValueError('Unsupported description list')
            before=self.paragraphs(text[:description.start()])
            content=''.join('<dt>'+self.inline(items[i])+'</dt><dd>'+self.paragraphs(items[i+1].strip())+'</dd>' for i in range(1,len(items),2))
            return before+'<dl>'+content+'</dl>'+self.paragraphs(text[description.end():])
        listing = re.search(r'\\begin\{(enumerate|itemize)\}(?:\[([^\]]*)\])?(.*?)\\end\{\1\}',text,re.S)
        if listing:
            option=listing[2] or ''
            options={'':'',r'label=(\alph*)':'a',r'label=(\roman*)':'i',r'label=\textbf{S\arabic*.},leftmargin=3.2em':'S',
                     r'label=\textbf{I.\arabic*.},leftmargin=*,itemsep=0.3em,topsep=0.4em':'I'}
            if option not in options: raise ValueError('Unsupported list labels '+option)
            items=re.split(r'\\item\b',listing[3])
            if items[0].strip(): raise ValueError('Content before first list item')
            tag='ol' if listing[1]=='enumerate' else 'ul'
            attrs=(' class="seed-axioms"' if options[option]=='S' else (' class="paper-conclusions"' if options[option]=='I' else ' type="'+options[option]+'"')) if option else ''
            before=self.paragraphs(text[:listing.start()])
            content=''.join('<li>'+('<span class="conclusion-label">I.'+str(i)+'. </span>' if options[option]=='I' else '')+self.paragraphs(item.strip())+'</li>' for i,item in enumerate(items[1:],1))
            return before+'<'+tag+attrs+'>'+content+'</'+tag+'>'+self.paragraphs(text[listing.end():])
        chunks=[]
        pos=0
        for m in MATH_PATTERN.finditer(text):
            if m[1] is not None or m[4] is not None: continue
            chunks.extend([text[pos:m.start()],m[0]])
            pos=m.end()
        chunks.append(text[pos:])
        out = []
        for chunk in chunks:
            if chunk.startswith(('\\[',r'\begin{align*}')): out.append(self.inline(chunk))
            else:
                out.extend('<p>'+self.inline(p.strip())+'</p>' for p in re.split(r'\n\s*\n',chunk) if re.sub(r'\\label\{[^{}]*\}','',p).strip())
        return ''.join(out)

    def preview(self, text):
        """Return inert text/math pieces, keeping formulas intact at the excerpt boundary."""
        text = re.sub(r'\\label\{[^}]+\}', '', text).strip()
        def reference(match):
            return ', '.join(self.labels[key]['kind']+' '+self.labels[key]['number'] for key in match[1].split(','))
        text = re.sub(r'\\(?:c|C|eq)?ref\{([^}]+)\}', reference, text)
        text = re.sub(r'\\cite(?:\[([^\]]*)\])?\{([^}]+)\}',lambda m:', '.join('['+str(self.citations[k][0])+']' for k in m[2].split(','))+(', '+m[1] if m[1] else ''),text)
        while (note:=re.search(r'\\(statusleanthree|statusleanprior|statusroadmap)\{',text)):
            value,end=group(text,note.end()-1)
            if note[1] not in self.formal_labels: raise ValueError('Missing manuscript scope label: '+note[1])
            text=text[:note.start()]+self.formal_labels[note[1]]+' '+value+text[end:]
        text = re.sub(r'\\(?:textbf|emph|textit|texttt|leanname|path|nolinkurl)\{([^{}]*)\}',r'\1',text)
        text = text.replace(r'\textquotesingle ', '’').replace(r'\S','§')
        parts = []
        size = 0
        segments=[]
        position=0
        for match in MATH_PATTERN.finditer(text):
            segments.extend([(False,text[position:match.start()]),(True,next(g for g in match.groups() if g is not None))])
            position=match.end()
        segments.append((False,text[position:]))
        for math,part in segments:
            if not part: continue
            value = expand_math(part,self.macros) if math else typography(re.sub(r'\s+',' ',part))
            if math and size+len(value)>400: break
            if not math and size+len(value)>400: value=value[:max(0,400-size)].rsplit(' ',1)[0]+'…'
            parts.append(dict(type='math' if math else 'text',text=value))
            size += len(value)
            if size>=400 or value.endswith('…'): break
        return parts


def readable_url(path, line=None):
    record = next((c for c in CHAPTERS if c['source']==path and (line is None or 'start_line' not in c or c['start_line']<=line<=c['end_line'])),None)
    return record['url']+('#L'+str(line) if line else '') if record else None


def chapter_text(text, spec):
    if 'start_line' not in spec: return text
    lines=text.splitlines(keepends=True)
    start,end=spec['start_line'],spec['end_line']
    if not 1<=start<=end<=len(lines): raise ValueError('Reading source range is invalid')
    return '\n'*(start-1)+''.join(lines[start-1:end])


def chapter_claims(reader, spec):
    return [row for row in reader.claims_by_source.get(spec['source'],[])
            if 'start_line' not in spec or spec['start_line']<=row['statement_line']<=spec['end_line']]


def validate_monolithic(main, config):
    specs=config['chapters']
    lines=main.splitlines()
    if lines[specs[0]['start_line']-1]!=r'\begin{document}' or lines[specs[-1]['end_line']-1]!=r'\end{document}':
        raise ValueError('Manuscript document boundaries changed')
    for i,spec in enumerate(specs):
        if i and specs[i-1]['end_line']+1!=spec['start_line']: raise ValueError('Reading ranges have a gap or overlap')
        text=chapter_text(main,spec)
        headings=re.findall(r'\\section\{([^{}]+)\}',text)
        if headings!=([spec['title']] if i else []): raise ValueError('Manuscript section order changed: '+spec['title'])
    if [m for s in specs for m in original_math(chapter_text(main,s))]!=original_math(main.split(r'\begin{document}',1)[1]):
        raise ValueError('Manuscript mathematics omitted by chapter ranges')


def bibliography(text):
    entries=[]
    pos=0
    while pos<len(text):
        if text[pos].isspace(): pos+=1; continue
        match=re.match(r'@([A-Za-z]+)\{([A-Za-z0-9_-]+),',text[pos:])
        if not match: raise ValueError('Unsupported bibliography syntax')
        start=pos
        pos+=match.end()
        fields={}
        while True:
            spacing=re.match(r'[\s,]*',text[pos:]); pos+=spacing.end()
            if text[pos:pos+1]=='}': pos+=1; break
            field=re.match(r'([A-Za-z]+)\s*=\s*',text[pos:])
            if not field: raise ValueError('Unsupported bibliography field')
            pos+=field.end()
            value,pos=group(text,pos)
            fields[field[1]]=value
        entries.append(dict(key=match[2],kind=match[1],line=text.count('\n',0,start)+1,fields=fields))
    return entries


def manuscript_bibliography(text):
    match=re.search(r'\\begin\{thebibliography\}\{[^{}]+\}(.*?)\\end\{thebibliography\}',text,re.S)
    if not match: raise ValueError('Missing manuscript bibliography')
    entries=list(re.finditer(r'\\bibitem\{([^{}]+)\}',match[1]))
    if not entries or match[1][:entries[0].start()].strip(): raise ValueError('Unsupported bibliography preamble')
    return [dict(key=entry[1], line=text.count('\n',0,match.start(1)+entry.start())+1,
                 body=match[1][entry.end():entries[i+1].start() if i+1<len(entries) else len(match[1])].strip())
            for i,entry in enumerate(entries)]


def prepare(reader):
    """Bind selected books and resolve their references before writing pages."""
    reader.add(BIB,'Paper II historical bibliography output')
    reader.readable_books={}
    for work,config in BOOKS.items():
        reader.add(config['bib'],config['label']+' bibliography source')
        main=reader.site.read_source(reader.records[config['main']]).decode('utf-8-sig')
        if config.get('monolithic'): validate_monolithic(main,config)
        else:
            declared=re.findall(r'\\input\{('+re.escape(config.get('chapter_prefix','chapters/'))+r'[^}]+)\}',clean_tex(main).split(r'\begin{document}',1)[-1])
            if [config['base']+p for p in declared] != [c['source'] for c in config['chapters'][:config['main_chapters']]]:
                raise ValueError(config['label']+' chapter order changed. Review the readable edition.')
        macros=manuscript_macros(main)
        chapters=[]
        labels={}
        state={}
        for spec in config['chapters']:
            reader.add(spec['source'])
            raw=reader.site.read_source(reader.records[spec['source']])
            chapter=Chapter(chapter_text(raw.decode('utf-8-sig'),spec),macros,state=state,check_refs=False)
            chapter.formal_labels=formal_note_labels(main)
            chapter.url=spec['url']
            chapter.base=config['base']
            chapter.bibliography_url=config['bib_page']
            chapter.external_inputs={name:dict(url=reader.primary_pdf(work)['url'],title=title)
                                     for name,title in config.get('pdf_inputs',{}).items()}
            chapter.external_inputs.update(config.get('html_inputs',{}))
            for label,node in chapter.labels.items():
                if label in labels: raise ValueError('Duplicate book label '+label)
                node['url']=chapter.url
                labels[label]=node
            state={'section':chapter.section,'appendix':chapter.appendix,'part':chapter.part}
            chapters.append((spec,raw,chapter))
        bib_text=reader.site.read_source(reader.records[config['bib']]).decode('utf-8-sig')
        references=(manuscript_bibliography if config.get('inline_bibliography') else bibliography)(bib_text)
        for spec,raw,chapter in chapters:
            chapter.labels=labels
            chapter.validate_references()
            chapter.citations={r['key']:(r['key'],chapter.relative(config['bib_page'])+'#ref-'+r['key']) for r in references}
            nodes={n['line']:n for n in chapter.nodes}
            for row in chapter_claims(reader,spec):
                if row['statement_line'] not in nodes: raise ValueError('Claim does not have a rendered statement block')
                if row['proof_line'] and nodes.get(row['proof_line'],{}).get('kind')!='proof':
                    raise ValueError('Claim does not have its recorded rendered proof block')
        reader.readable_books[work]=dict(config=config,chapters=chapters,references=references,macros=macros,main=main)


def split_cells(text, separator):
    """Split table syntax only outside formulas and grouped command arguments."""
    result=[]
    start=pos=0
    while pos<len(text):
        match=MATH_PATTERN.match(text,pos)
        if match: pos=match.end(); continue
        if text[pos]=='{': _,pos=group(text,pos); continue
        if text.startswith(separator,pos):
            result.append(text[start:pos]); pos+=len(separator); start=pos; continue
        if text[pos]=='\\': pos+=2
        else: pos+=1
    result.append(text[start:])
    return result


def render_table(node,chapter):
    content=node['body'].strip()
    caption=''
    if node['kind']=='table':
        content=re.sub(r'^\\centering\s*','',content)
        if not content.startswith(r'\caption'): raise ValueError('Table caption is missing')
        caption,end=group(content,len(r'\caption'))
        content=content[end:].strip()
        content=re.sub(r'^\\label\{[^{}]+\}\s*','',content)
        start=re.match(r'\\begin\{(tabularx|tabular)\}',content)
        if not start: raise ValueError('Unsupported table environment')
        pos=start.end()
        if start[1]=='tabularx':
            width,pos=group(content,pos)
            if width!=r'\textwidth': raise ValueError('Unsupported table width')
        _,pos=group(content,pos)
        end_tag=r'\end{'+start[1]+'}'
        if not content.endswith(end_tag): raise ValueError('Unhandled table tail')
        content=content[pos:-len(end_tag)]
    else:
        _,pos=group(content,0)
        if node['kind']=='tabularx': _,pos=group(content,pos)
        content=content[pos:]
        if content.lstrip().startswith(r'\caption'):
            content=content.lstrip()
            caption,pos=group(content,len(r'\caption'))
            content=content[pos:]
            content=re.sub(r'^\s*\\label\{[^{}]+\}','',content).lstrip()
            if not content.startswith(r'\\'): raise ValueError('Missing caption row terminator')
            content=content[2:]
    # A print continuation header is not an additional data row.
    if r'\endfirsthead' in content:
        first,rest=content.split(r'\endfirsthead',1)
        repeated,tail=rest.split(r'\endhead',1)
        normalize=lambda t:re.sub(r'\s+','',t.replace(' (continued)',''))
        first_header=re.sub(r'^.*?\\toprule',r'\\toprule',first,flags=re.S)
        if normalize(first_header)!=normalize(repeated) or original_math(repeated):
            raise ValueError('Unsupported repeated table header')
        content=first+tail
    content=re.sub(r'\\(?:toprule|midrule|bottomrule|endfirsthead|endhead|addlinespace)\b','',content)
    rows=[split_cells(row,'&') for row in split_cells(content,r'\\') if row.strip()]
    if not rows or any(len(row)!=len(rows[0]) for row in rows): raise ValueError('Unexpected table column structure')
    body='<div class="table-scroll" tabindex="0" role="region" aria-label="'+html.escape(caption or 'Notation table',quote=True)+'"><table>'
    if caption: body+='<caption>'+chapter.inline(caption)+'</caption>'
    for index,row in enumerate(rows):
        if index==0: body+='<thead>'
        if index==1: body+='<tbody>'
        body+='<tr>'+''.join(('<th scope="col">' if index==0 else '<td>')+chapter.inline(cell.strip())+('</th>' if index==0 else '</td>') for cell in row)+'</tr>'
        if index==0: body+='</thead>'
    return body+('</tbody>' if len(rows)>1 else '')+'</table></div>'


def neighbour_links(spec):
    config=BOOKS[spec['work']]
    chapters=config['chapters']
    index=chapters.index(spec)
    routes=[]
    if index>0: routes.append(('Previous: '+chapters[index-1]['title'],chapters[index-1]['url']))
    routes.append(('All '+config['label']+' chapters',config['index']))
    if index+1<len(chapters): routes.append(('Next: '+chapters[index+1]['title'],chapters[index+1]['url']))
    return '<nav class="chapter-neighbours" aria-label="Neighbouring reading chapters">'+''.join(
        '<a href="'+posixpath.relpath(url,posixpath.dirname(spec['url']))+'">'+html.escape(title)+'</a>' for title,url in routes)+'</nav>'


def render(reader):
    reports=[]
    for book in reader.readable_books.values():
        reports.extend(render_book(reader,book))
    reader.site.write('documents/readable-chapters.json',json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    render_reading_index(reader)


def render_reading_index(reader):
    site=reader.site
    page='read/index.html'
    body='<p class="eyebrow">HTML reading editions</p><h1>Read the papers online</h1><p>Read at your own pace with chapter contents, selectable equations, and direct links between statements, proofs and their sources. Start with Paper I for the foundations, or choose the paper you need.</p><div class="work-list">'
    for work,config in BOOKS.items():
        body+='<section class="work"><p class="eyebrow">'+config['label']+'</p><h2>'+html.escape(config['title'])+'</h2><p>'+str(config['main_chapters'])+' main chapters</p><nav aria-label="'+config['label']+' reading formats">'
        body+='<a class="button" href="'+site.rel(config['chapters'][0]['url'],page)+'">Start '+config['label']+'</a><a href="'+site.rel(config['index'],page)+'">Chapter contents</a>'
        pdf=reader.primary_pdf(work)
        if pdf: body+='<a href="'+site.rel(pdf['url'],page)+'">Read PDF</a>'
        body+='</nav></section>'
    body+='</div><h2>Reading options</h2><p>Use browser zoom to enlarge text. Wide equations and tables have separate areas that can be scrolled with the keyboard. MathJax provides equation exploration and assistive reading options through its context menu.</p><p>The HTML editions follow the retained manuscripts. <a href="'+site.rel('read/paper-iv/atlas/index.html',page)+'">Paper IV’s 26 atlas plates</a> also have HTML pages with drawings, descriptions and tables. Other visual atlases remain in the PDFs, and not every paper has an HTML edition yet. See <a href="'+site.rel('collection/ACCESSIBILITY.html',page)+'">accessibility and reading options</a> for current coverage and limitations.</p><p><a href="'+site.rel('documents.html',page)+'">Browse all papers and PDFs</a> · <a href="'+site.rel('collection/READING_ROUTES.html',page)+'">Choose a reading route</a></p>'
    site.page(page,'Read the papers online',body)
    site.search.append(dict(title='Read the papers online',group='Collection',kind='Guides',url=page,text='HTML reading editions '+' '.join(c['label'] for c in BOOKS.values())+' chapters equations proofs',work_ids=list(BOOKS)))


def passage_links(source_links, reading_links=''):
    """Keep proof/section navigation available when optional tools are hidden."""
    if reading_links:
        return '<p class="passage-links">'+reading_links+'<span class="passage-tools"> · '+source_links+'</span></p>'
    return '<p class="passage-links passage-tools">'+source_links+'</p>'


def related_reading_links(chapter, identifier):
    return ' · '.join('<a href="'+html.escape(chapter.relative(url),quote=True)+'">'+html.escape(label)+'</a>'
                      for label,url in chapter.related_readings.get(identifier,[]))


def reading_options(description=None):
    description=description or ('Show each passage’s permalink, source line, claim record '
                                'and related resources. Proof links, atlas links and chapter navigation are always available.')
    return ('<div class="reading-options" hidden><label for="show-passage-tools">'
            '<input id="show-passage-tools" type="checkbox" aria-controls="chapter-text" '
            'aria-describedby="reading-options-help">Show source and reference links</label>'
            '<p id="reading-options-help">'+html.escape(description)+'</p></div>'
            '<p><a href="#chapter-text">Skip contents and start reading</a></p>')


def render_book(reader,book):
    site=reader.site
    config=book['config']
    work=config['work']
    e=html.escape
    reports=[]
    descriptions=json.loads((site.root/config['figure_descriptions']).read_bytes()) if config.get('figure_descriptions') else {}
    described=set()
    for spec,raw,chapter in book['chapters']:
        source,page,title=spec['source'],spec['url'],config['label']+': '+spec['title']
        rows={r['statement_line']:r for r in chapter_claims(reader,spec)}
        proof_rows={r['proof_line']:r for r in rows.values() if r['proof_line']}
        headings=[n for n in chapter.nodes if n['kind'] in HEADINGS]
        toc='<nav class="chapter-contents" aria-label="Chapter contents"><h2 id="contents">Contents</h2><ol>'
        toc+=''.join('<li'+(' class="subsection-entry"' if n['kind']!='section' else '')+'><a href="#'+n['id']+'">'+e((n['number']+' '+typography(n['title'])).strip())+'</a></li>' for n in headings)
        if not headings: toc+='<li><a href="#L'+str(chapter.nodes[0]['line'])+'">'+e(spec['title'])+'</a></li>'
        toc+='</ol></nav>'
        body='<p class="eyebrow">Readable manuscript</p><h1>'+e(title)+'</h1>'
        body+='<p>The wording and mathematics follow the retained manuscript. This reading format does not add a proof review or extend Lean coverage.</p>'
        body+=reader.work_routes(work,page)+neighbour_links(spec)
        body+='<p><a href="'+reader.resolve(source,page)+'">Original TeX with line links</a> · <a href="'+site.rel(reader.records[source]['file_url'],page)+'" download>Download TeX</a></p>'+reading_options()+toc
        body+='<article id="chapter-text" class="readable-chapter" aria-label="'+e(title,quote=True)+'">'
        level=2
        for node in chapter.nodes:
            kind=node['kind']
            label=(node['number']+' '+node['title']).strip() if kind in HEADINGS else (KIND_NAMES.get(kind,kind.capitalize())+' '+node['number']+(': '+node['title'] if node['title'] else '')).strip()
            source_link=reader.resolve(source,page,'L'+str(node['line']))
            links='<a href="#'+node['id']+'">Permalink</a> · <a href="'+source_link+'">Source line '+str(node['line'])+'</a>'
            reading_links=related_reading_links(chapter,node['id'])
            if kind in HEADINGS:
                level=min(level+1,5) if kind=='paragraph' else HEADINGS[kind]
                body+='<h'+str(level)+' id="'+node['id']+'">'+e(node['number'])+' '+chapter.inline(node['title'])+'</h'+str(level)+'>'
                index=headings.index(node)
                section_links='<a href="#contents">Contents</a>'
                if index: section_links+=' · <a href="#'+headings[index-1]['id']+'">Previous section</a>'
                if index+1<len(headings): section_links+=' · <a href="#'+headings[index+1]['id']+'">Next section</a>'
                reading_links=' · '.join(filter(None,[section_links,reading_links]))
                body+=passage_links(links,reading_links)
            elif kind=='figure':
                match=re.match(r'\s*\\centering\s*\\includegraphics\[width=0?\.9[68]\\(?:textwidth|linewidth)\]\{([^}]+)\}\s*\\caption',node['body'])
                if not match: raise ValueError('Unsupported figure')
                caption,end=group(node['body'],match.end())
                if re.sub(r'\\label\{[^}]+\}','',node['body'][end:]).strip(): raise ValueError('Unhandled figure content')
                path=config['base']+'figures/'+match[1].removesuffix('.pdf')+'.png'
                image=reader.image_url(path,page)
                if not image: raise ValueError('Missing receipt-bound figure '+path)
                alt=plain_math(caption.replace('$',''))[0]
                description_link=''
                if config.get('figure_descriptions'):
                    name=posixpath.basename(path)
                    description=descriptions.get(name)
                    if not description or description['source_sha256']!=reader.images[path]['sha256']:
                        raise ValueError('Review the figure description for '+path)
                    described.add(name)
                    alt=description['alt']
                    description_link='<p><a href="'+site.rel(config['diagram_guide'],page)+'#'+description['anchor']+'">Text description of this figure</a></p>'
                body+='<figure id="'+node['id']+'"><img src="'+image+'" alt="'+e(alt,quote=True)+'" loading="lazy"><figcaption>'+chapter.inline(caption)+'</figcaption>'+description_link+passage_links(links)+'</figure>'
            elif kind in {'table','longtable','tabularx'}:
                body+='<section id="'+node['id']+'">'+render_table(node,chapter)+passage_links(links)+'</section>'
            elif kind=='conceptchain':
                body+='<section id="'+node['id']+'"><div class="table-scroll" tabindex="0" role="region" aria-label="Conceptual diagram. Scroll horizontally if needed.">'+chapter.paragraphs(node['body'])+'</div>'+passage_links(links)+'</section>'
            elif kind=='thebibliography':
                body+='<section id="'+node['id']+'"><h2>References</h2>'
                for entry in book['references']:
                    body+='<section id="ref-'+entry['key']+'"><h3>'+e(entry['key'])+'</h3>'+chapter.paragraphs(presentation_tex(entry['body']))+'</section>'
                body+=passage_links(links)+'</section>'
            elif kind=='lstlisting':
                body+='<section id="'+node['id']+'"><pre tabindex="0" aria-label="Original algorithm listing"><code>'+e(node['body'].strip('\n'))+'</code></pre>'+passage_links(links)+'</section>'
            else:
                row=rows.get(node['line']) or proof_rows.get(node['line'])
                if row:
                    links+=' · <a href="'+site.rel('claims.html',page)+'#'+row['id'].lower()+'">Claim record</a>'
                    other=row['statement_line'] if kind=='proof' else row['proof_line']
                    if other: reading_links=' · '.join(filter(None,['<a href="#L'+str(other)+'">'+('Back to statement' if kind=='proof' else 'Read proof')+'</a>',reading_links]))
                    hub=site.rel('collection/works/'+work+'.html',page)
                    links+=' · <a href="'+hub+'#lean">Lean coverage</a> · <a href="'+hub+'#code">Code</a> · <a href="'+hub+'#worked-examples-for-this-work">Worked examples</a>'
                body+='<section id="'+node['id']+'" class="reading-block '+kind+'">'
                if kind!='text':
                    if kind in PANELS: label=node['title'] or PANELS[kind]
                    if kind=='proof' and row:
                        statement=next(n for n in chapter.nodes if n['line']==row['statement_line'] and n['kind'] in NUMBERED)
                        label='Proof of '+KIND_NAMES.get(statement['kind'],statement['kind'].capitalize())+' '+statement['number']
                    heading_level=str(min(level+1,6))
                    body+='<h'+heading_level+'>'+chapter.inline(label)+'</h'+heading_level+'>'
                body+=chapter.paragraphs(node['body'])+passage_links(links,reading_links)+'</section>'
            if kind not in {'figure','thebibliography'}:
                plain,aliases=plain_math(re.sub(r'\\label\{[^}]+\}','',node['body']).replace('$',''))
                parent=next((n['title'] for n in reversed(headings) if n['line']<=node['line']),spec['title'])
                search_title=(parent+' / '+('Algorithm' if kind=='lstlisting' else 'Passage at line '+str(node['line']))) if kind in {'text','lstlisting'} else label
                item=dict(title=config['label']+' / '+typography(search_title),group='Collection',kind='Code' if kind=='lstlisting' else ('Written proofs' if kind=='proof' else 'Papers and source'),work_ids=[work],url=page+'#'+node['id'],text=parent+' '+plain+' '+aliases,preview=plain[:240] or label)
                # Preview prose only when it has no list/table/input syntax.
                snippet=re.split(r'\\\[|\\begin',node['body'],maxsplit=1)[0]
                snippet=re.sub(r'\\label\{[^}]+\}','',snippet).strip()
                if snippet and kind not in {'table','longtable','tabularx','lstlisting'} and r'\input' not in snippet:
                    item['preview_parts']=chapter.preview(snippet)
                math_preview=re.search(r'\\\[(.*?)\\\]',node['body'],re.S)
                if math_preview and len(math_preview[1])<650 and kind!='lstlisting': item['math_preview']=expand_math(math_preview[1],chapter.macros)
                site.search.append(item)
        body+='</article>'+neighbour_links(spec)+reader.work_routes(work,page)
        body+='<details class="document-provenance"><summary>Source and conversion record</summary><p>Source SHA-256: <code>'+reader.records[source]['sha256']+'</code></p><p>Unsupported prose commands stop the build. The mathematical expression sequence is checked against the source, with manuscript macros expanded for display.</p><p><a href="'+site.rel('documents/readable-chapters.json',page)+'">Conversion records</a></p></details>'
        site.page(page,title,body)
        expressions=original_math(chapter_text(raw.decode('utf-8-sig'),spec))
        if chapter.math!=expressions:
            difference=next((i for i,(a,b) in enumerate(zip(chapter.math,expressions)) if a!=b),min(len(chapter.math),len(expressions)))
            raise ValueError('Reading math differs at '+source+' expression '+str(difference)+' rendered '+str(chapter.math[difference:difference+1])+' original '+str(expressions[difference:difference+1]))
        report=dict(source=source,source_sha256=hashlib.sha256(raw).hexdigest(),url=page,math_expressions=len(expressions),math_sequence_sha256=hashlib.sha256(json.dumps(expressions,ensure_ascii=False).encode()).hexdigest(),references=len(chapter.references),labels=sum(len(n['labels']) for n in chapter.nodes),nodes=[{k:n[k] for k in ('kind','id','line','end_line','labels')} for n in chapter.nodes],macro_source=config['main'],macros=chapter.macros,new_proof_review=False,new_lean_execution=False)
        reports.append(report)
        if 'start_line' in spec: report.update(start_line=spec['start_line'],end_line=spec['end_line'])
        if source==SOURCE: site.write('documents/readable-paper-ii.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if described!=set(descriptions): raise ValueError('Unused figure descriptions for '+work)
    render_book_index(reader,book,reports)
    render_bibliography(reader,book)
    return reports


def render_book_index(reader,book,reports):
    site=reader.site
    config=book['config']
    page,work,label=config['index'],config['work'],config['label']
    body='<p class="eyebrow">Read '+label+'</p><h1>'+html.escape(config['title'])+'</h1><p>Read the '+str(config['main_chapters'])+' main manuscript chapters in order, or choose a topic below.</p>'+reader.work_routes(work,page)
    body+='<nav class="chapter-contents" aria-label="'+label+' chapters"><h2>Contents</h2><ol>'
    for spec,report in zip(config['chapters'],reports):
        body+='<li><a href="'+site.rel(spec['url'],page)+'">'+html.escape(spec['title'])+'</a></li>'
    body+='<li><a href="references.html">Bibliography</a></li></ol></nav>'
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',book['main'],re.S)
    if abstract:
        parser=Chapter('',book['macros'])
        body+='<section><h2>Abstract</h2>'+parser.paragraphs(abstract[1])+'</section>'
    body+='<h2>PDF and companion guides</h2><ul>'
    for record in reader.records.values():
        if record['work']==work and record['format']=='pdf':
            body+='<li><a href="'+site.rel(record['url'],page)+'">'+html.escape(record['title'])+'</a></li>'
    body+='</ul>'
    if config.get('html_inputs'):
        body+='<p><a href="'+site.rel(config['html_inputs']['atlas-pages']['url'],page)+'">Explore all 26 atlas plates in HTML</a>, with drawings, text descriptions, equations and tables.</p>'
    body+='<p>The original visual atlas remains available in the PDF and visual guide. The HTML chapters preserve the source wording, mathematical statements and recorded limits. They do not add a proof assessment.</p>'
    site.page(page,'Read '+label,body)
    site.search.append(dict(title=label+' / Read all chapters',group='Collection',kind='Papers and source',work_ids=[work],url=page,text=config['title']+' readable chapters '+ ' '.join(c['title'] for c in config['chapters'])))


def render_bibliography(reader,book):
    site=reader.site
    config=book['config']
    page,work,label=config['bib_page'],config['work'],config['label']
    body='<h1>'+label+' bibliography</h1>'+reader.work_routes(work,page)
    body+='<p>Entries follow the retained bibliography source. Citation keys keep references stable without relying on older generated bibliography numbering. These links do not establish what a cited source proves.</p>'
    for entry in book['references']:
        body+='<section id="ref-'+entry['key']+'"><h2>'+html.escape(entry['key'])+'</h2><dl>'
        if 'body' in entry:
            body+='</dl>'+Chapter('',book['macros']).paragraphs(presentation_tex(entry['body']))
        else:
            for field,value in entry['fields'].items():
                body+='<dt>'+html.escape(field.capitalize())+'</dt><dd>'+html.escape(typography(value).replace('{','').replace('}',''))+'</dd>'
            body+='</dl>'
        body+='<p><a href="'+reader.resolve(config['bib'],page,'L'+str(entry['line']))+'">Original bibliography entry</a> · <a href="#ref-'+entry['key']+'">Permalink</a></p></section>'
    site.page(page,label+' bibliography',body)
    site.search.append(dict(title=label+' / Bibliography',group='Collection',kind='Papers and source',work_ids=[work],url=page,text=' '.join(e['key']+' '+(e['body'] if 'body' in e else ' '.join(e['fields'].values())) for e in book['references'])))


def chapter_section(chapter,node):
    return node['section']
