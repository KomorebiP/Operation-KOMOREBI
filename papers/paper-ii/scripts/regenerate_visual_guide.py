from pathlib import Path
import argparse, json, re, shutil, subprocess, hashlib

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description='Assemble the visual guide from preserved model sources and the final traditional crosswalk.')
parser.add_argument('--original', type=Path, default=ROOT.parent/'Paper_II/source/visual_appendix')
parser.add_argument('--traditional', type=Path, default=ROOT/'traditional')
parser.add_argument('--output', type=Path, default=ROOT/'visual_guide')
args=parser.parse_args()
SRC=args.original.resolve()
TRAD=args.traditional.resolve()
OUT=args.output.resolve()
OUT.mkdir(parents=True,exist_ok=True)
for name in ['source','graphics','checks']:
    shutil.copytree(SRC/name,OUT/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
cross=json.loads((TRAD/'canonical_label_to_final.json').read_text())
anchors={
1:['def:coordinate-refinement','thm:weighted-inverse','thm:precision-delay'],
2:['def:refinement-map','def:coordinate-refinement','def:separation-weight'],
3:['thm:nested-refinement','thm:polyphase-refinement'],
4:['def:coordinate-refinement','prop:perfect-reconstruction'],
5:['prop:perfect-reconstruction','thm:transfer-block-refinement'],
6:['prop:residue-algebra'],7:['thm:root-of-unity'],8:['thm:dyadic-odd'],
9:['thm:weighted-inverse','cor:finite-precision'],
10:['thm:weighted-inverse','cor:finite-precision'],
11:['thm:weighted-inverse','cor:finite-precision','alg:weighted-inverse'],
12:['thm:transfer-zeta'],13:['thm:transfer-zeta','cor:zeta-recurrence'],
14:['thm:bezout-projector','def:separation-weight'],15:['prop:dyadic-sign'],
16:['thm:precision-delay','prop:dyadic-sign'],17:['thm:smith-solve'],
18:['thm:smith-solve'],19:['thm:smith-solve'],20:['alg:residue'],
21:['sec:smith-realization','eq:smith-inversion'],
22:['thm:power-defect','cor:defect-norm'],23:['thm:resolvent-defect'],24:[]}
names={'def':'Definition','thm':'Theorem','prop':'Proposition','cor':'Corollary','sec':'Section','eq':'Equation','alg':'Algorithm'}
pages=(SRC/'source/pages.tex').read_text()
pat=re.compile(r'^\\vpage\{(\d+)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}$',re.M)
rows=[]
def header(m):
    n=int(m[1]); refs=[]; mapped=[]
    for key in anchors[n]:
        entry=cross[key]
        assert (entry['number'] or entry.get('locator_section')) and entry['page'], f'Missing final locator: {key}'
        prefix=entry['final_label'].split(':')[0]
        if key == 'eq:smith-inversion':
            refs.append(f"{entry['locator_text']} (p. {entry['page']})")
        elif key == 'sec:smith-realization' and 'eq:smith-inversion' in anchors[n]:
            pass
        else:
            refs.append(f"{names.get(prefix,'Item')} {entry['number']} (p. {entry['page']})")
        mapped.append({'canonical_label':key,**entry})
    ref='Traditional paper: '+ '; '.join(refs) if refs else 'Formal source: v1.2.1 / Lean component v1.1.1 / 25-row scoped contract'
    rows.append({'plate':n,'title_tex':m[2],'original_reference':m[4],'traditional_references':mapped})
    sub=m[3].replace('A WORKED VISUAL APPENDIX','A WORKED VISUAL GUIDE').replace('THIS APPENDIX','THIS GUIDE')
    return r'\vpage{'+str(n)+'}{'+m[2]+'}{'+sub+'}{'+ref+'}'
pages=pat.sub(header,pages)
assert len(rows)==24
pages=pages.replace('This appendix separates them','This guide separates them')
pages=pages.replace('Every small matrix in the appendix','Every small matrix in the guide')
pages=pages.replace('This appendix adds explanatory models','This guide adds explanatory models')
pages=pages.replace('Use the appendix to understand','Use the guide to understand')
old='The preserved Python suite was separately rerun in a copy: all 48 tests passed. Its thirteen original figure pairs and stored numerical records regenerated successfully. These executable checks are not a fresh Lean build. The original manuscript pages, theorem statements, source files, and all certificate boundaries remain unchanged.'
new='For this edition, the preserved Python suite was rerun in an isolated working directory: all 48 tests passed. All 118 exact visual checks passed, and all 22 regenerated vector plates matched their source bytes. Thirteen PDF/PNG figure pairs were regenerated and presence-checked; nine numerical summary rows passed the recorded comparison. These checks are not a fresh Lean build. The traditional companion integrates the expanded mathematics and records its local hypothesis corrections. The inherited 25-row formal contract retains its original scope.'
assert old in pages;pages=pages.replace(old,new)
(OUT/'source/pages_final.tex').write_text(pages)
(OUT/'VISUAL_CROSSWALK.json').write_text(json.dumps({'source':'Paper II visual appendix, 24 worked pages and 22 exact model figures','edition':'2026-10-05','traditional_source_sha256':hashlib.sha256((TRAD/'Paper_II_Traditional_Final.tex').read_bytes()).hexdigest(),'pages':rows},ensure_ascii=False,indent=2)+'\n')

t=(SRC/'appendix.tex').read_text().split(r'\begin{document}')[0]
t=t.replace('11pt,letterpaper','11pt,a4paper')
t=t.replace('left=.80in,right=.80in,top=.76in,bottom=.72in','left=20mm,right=20mm,top=18mm,bottom=17mm')
t=t.replace('Paper II: A Visual Appendix','Paper II: Visual Guide, Final Edition')
t=t.replace(r'\hypersetup{pageanchor=false}',r'\hypersetup{colorlinks=true,linkcolor=accent,urlcolor=accent,bookmarksopen=true}'+ '\n'+r'\definecolor{accent}{HTML}{137668}\definecolor{muted}{HTML}{536568}')
t=t.replace('VISUAL APPENDIX','VISUAL GUIDE')
t=t.replace("Reader's edition\\quad\\textbullet\\quad Formal source: v1.2.1",'Final companion edition\\quad\\textbullet\\quad 5 October 2026')
t=t.replace(r'\fancyfoot[R]{\sffamily\small V\,--\,\thepage}',r'\fancyfoot[R]{\sffamily\small\color{accent}\thepage}')
t=t.replace('colframe=black!55','colframe=accent').replace('colback=black!3','colback=accent!3')
a=t.index(r'\newif\ifstarted');b=t.index(r'\newcommand{\CC}',a)
t=t[:a]+r'''\newif\ifstarted\startedfalse
\newcommand{\vpage}[4]{\ifstarted\clearpage\else\startedtrue\fi
\pdfbookmark[1]{V#1. #2}{plate#1}\hypertarget{vpage#1}{}\label{visual:#1}
{\sffamily\fontsize{9}{11}\selectfont\bfseries\color{accent}V#1\quad /\quad #3\par}\vspace{5pt}
{\sffamily\bfseries\fontsize{21}{24}\selectfont #2\par}\vspace{5pt}
{\sffamily\fontsize{8.7}{11}\selectfont\color{muted} #4\par}\vspace{6pt}}
\newcommand{\pagerefV}[1]{\hyperlink{vpage#1}{V\,--\,#1}}

'''+t[b:]
front=r'''
\begin{document}
\begin{titlepage}
\thispagestyle{empty}
\vspace*{14mm}
{\sffamily\bfseries\small\color{accent}KOMOREBI MATHEMATICS / PAPER II}\par
\vspace{5mm}{\color{accent}\rule{\linewidth}{1pt}}\par
\vspace{12mm}
{\sffamily\bfseries\fontsize{32}{36}\selectfont Polyphase refinement\\and weighted resolution\par}
\vspace{9mm}
{\fontsize{23}{28}\selectfont\itshape The visual guide\par}
\vspace{8mm}
{\large Exact models for coordinates, inversion,\\arithmetic separation, and linear defects\par}
\vspace{15mm}
{\sffamily\bfseries Komorebi P.}\par
{\sffamily\small\color{muted}Final companion edition / 5 October 2026}\par
\vfill
{\Large\[P_{N,j}=\sum_{r=0}^{q-1}P_{qN,j+rN}.\]}
\begin{center}\small Finer addresses. The same reconstructible object.\end{center}
\vfill
\begin{minipage}{.96\linewidth}
Twenty-four worked pages and twenty-two exact model figures accompany the
traditional paper and its Lean guide. Integer, rational, modular and symbolic
calculations determine the figures. The preserved Python model sources and
their explicit finite verification ranges are included in the source package.
\end{minipage}
\end{titlepage}
\pdfbookmark[0]{Guide contents}{guidecontents}
{\sffamily\bfseries\Large\color{accent}A route through the examples}\par\medskip
The labels V--1 through V--24 identify worked pages independently of PDF
pagination. Each page names its corresponding statement in the final
traditional edition. The Lean guide provides the separate formal contract.
\medskip
\begin{multicols}{2}
'''
for row in rows:
    front+=r'{\small\noindent\hyperlink{vpage'+str(row['plate'])+'}{\\textbf{V--'+str(row['plate'])+'} '+row['title_tex']+r'}\par\smallskip}'+'\n'
front+=r'''
\end{multicols}
\medskip
\head{Three reading routes}
\textbf{Exact coordinates:} V--3 to V--8, followed by the finite filter in V--20.
\textbf{Precision and arithmetic:} V--9 to V--19.
\textbf{Realizations and defects:} V--20 to V--24.
\head{How to read an ordered product}
In a written matrix word $ab$, the rightmost map $b$ acts first. Directed
walks may instead be listed in chronological edge order, as in the traditional
paper's block-path formula. Follow the convention stated with the example.
\head{What the figures establish}
The models expose the mechanisms and their boundaries. Exact finite checks
validate the displayed instances. Universal statements keep the hypotheses
and proofs given in the traditional paper; Lean coverage is recorded by the
separate theorem map. No new kernel compilation is claimed here.
\clearpage
\pdfbookmark[0]{Worked visual guide}{workedguide}
\input{source/pages_final.tex}
\end{document}
'''
(OUT/'Paper_II_Visual_Guide_Final.tex').write_text(t+front)
for i in range(1,4):
    q=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','Paper_II_Visual_Guide_Final.tex'],cwd=OUT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (OUT/f'build_pass_{i}.txt').write_text(q.stdout)
    if q.returncode:raise SystemExit(f'LaTeX failed on pass {i}; see {OUT/f"build_pass_{i}.txt"}')
print(OUT/'Paper_II_Visual_Guide_Final.pdf')
