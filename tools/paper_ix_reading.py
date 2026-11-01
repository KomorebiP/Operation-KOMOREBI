"""Opening HTML chapters of Paper IX, with explicit source-only continuations."""
import re

BASE = 'papers/paper-ix/current/sources/main/'
MAIN = BASE+'Paper_IX_Traditional_Final.tex'
CHAPTERS = [
    dict(source=BASE+'parts/00_scope.tex',url='read/paper-ix/scope-and-conventions.html',
         title='Scope and conventions',work='paper-ix'),
    dict(source=BASE+'parts/10_foundations.tex',url='read/paper-ix/arithmetic-packets.html',
         title='Arithmetic packets and coefficient transport',work='paper-ix'),
]
CONTINUATIONS = [
    (BASE+'parts/20_arithmetic.tex','Euler packets and arithmetic congruences'),
    (BASE+'../strengthening.tex','Factorial strengthening and sharp dyadic geometry'),
    (BASE+'parts/30_lifting.tex','Lifting and polynomial deformation'),
    (BASE+'parts/40_regularity.tex','Analytic regularity of the local solution map'),
    (BASE+'parts/50_open_questions.tex','Open questions and further directions'),
    (BASE+'parts/60_verification.tex','Verification record and formal scope'),
]
# Resolve only these authored forward references, checking their exact headings.
SOURCE_REFERENCES = [
    ('sec:regularity',BASE+'parts/40_regularity.tex','section','Analytic regularity of the local solution map'),
    ('sec:open',BASE+'parts/50_open_questions.tex','section','Open questions and further directions'),
    ('subsec:native133',BASE+'parts/50_open_questions.tex','subsection','Native 13.3: finite compatibility, completion, and descent'),
    ('subsec:historical-scope',BASE+'parts/50_open_questions.tex','subsection','Historical material and interface work'),
]


def register(books,chapters):
    import posixpath
    books['paper-ix']=dict(work='paper-ix',label='Paper IX',base=BASE,main=MAIN,
        bib=MAIN,bibliography_source_only=True,index='read/paper-ix/index.html',
        bib_page='read/paper-ix/references.html',title='Euler congruences',
        chapters=CHAPTERS,main_chapters=2,partial=True,chapter_prefix='parts/',
        required_macros={'N','Z','Q','F','Zp','Qp'},source_references=SOURCE_REFERENCES,
        continuation_sources=[(posixpath.normpath(path),title) for path,title in CONTINUATIONS],
        reading_introduction='Begin with the two opening chapters in HTML. Later chapters and appendices remain available in the complete PDF and linked manuscript sources.')
    chapters.extend(CHAPTERS)


def source_references(reader,config):
    """Bind forward links to original source headings without inventing numbering."""
    from readable_chapters import clean_tex
    for path,_ in config['continuation_sources']:
        if not reader.add(path): raise ValueError('Missing Paper IX continuation source: '+path)
    result={}
    for key,path,kind,title in config['source_references']:
        record=reader.add(path)
        text=clean_tex(reader.site.read_source(record).decode('utf-8-sig'))
        pattern=r'\\'+kind+r'\{'+re.escape(title)+r'\}\s*\\label\{'+re.escape(key)+r'\}'
        match=re.search(pattern,text)
        if not match: raise ValueError('Review Paper IX forward reference: '+key)
        result[key]=dict(kind=kind,number='',title=title,
                        reference_label=title+' (source)',url=record['url'],
                        id='L'+str(text.count('\n',0,match.start())+1))
    return result
