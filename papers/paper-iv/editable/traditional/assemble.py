#!/usr/bin/env python3
"""Assemble the final traditional companion from the selected proofread manuscript.
No mathematics is deleted or merged from competing historical editions.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
s=(R/'source/proofread.tex').read_text()
changes=[]
def replace(old,new,reason,category='editorial'):
 global s
 assert old in s, old
 assert s.count(old)==1,(old,s.count(old))
 s=s.replace(old,new)
 changes.append({'category':category,'old':old,'new':new,'reason':reason})
replace(r'\documentclass[11pt]{article}',r'\documentclass[11pt,a4paper]{article}','Match the final companion series page format.')
replace(r'\usepackage[margin=0.92in]{geometry}',r'''\usepackage[a4paper,margin=23mm,includeheadfoot,headheight=15pt,headsep=15pt,footskip=22pt]{geometry}
\usepackage{setspace,needspace,titlesec,etoolbox}
\usepackage{bookmark}''','Use the established A4 final-edition layout.')
# bookmark must be loaded after hyperref.
s=s.replace('\\usepackage{bookmark}\n','')
s=s.replace('\\usepackage[nameinlink,noabbrev]{cleveref}', '\\usepackage[nameinlink,noabbrev]{cleveref}\n\\usepackage{bookmark}')
replace(r'\usepackage{microtype}',r'\usepackage[nopatch=footnote]{microtype}','Use the final series typesetting configuration.')
replace(r'\definecolor{leanblue}{RGB}{20,72,135}',r'''\definecolor{leanblue}{RGB}{20,72,135}
\definecolor{accent}{HTML}{137668}
\definecolor{muted}{HTML}{536568}
\frenchspacing\clubpenalty=10000\widowpenalty=10000\raggedbottom
\titleformat{\section}{\sffamily\bfseries\large\color{accent}}{\thesection}{.7em}{}
\titleformat{\subsection}{\sffamily\bfseries\normalsize}{\thesubsection}{.7em}{}
\titlespacing*{\section}{0pt}{1.4\baselineskip}{.55\baselineskip}
\pretocmd{\section}{\Needspace{7\baselineskip}}{}{}
\pretocmd{\subsection}{\Needspace{5\baselineskip}}{}{}
\setstretch{1.055}\setlength{\parskip}{.3em}\setlength{\parindent}{1.35em}''','Apply the existing final-edition typography without changing mathematical tokens.')
replace('Formal status: Lean-backed in Paper IV.','Released formal contract: Paper IV v1.0.0.','Distinguish inherited formal evidence from the present editorial build.')
replace('Formal status: inherited Lean-backed result.','Inherited formal contract: earlier papers.','Keep earlier-paper evidence distinct from the Paper IV release.')
replace(r'\date{Version 1.0.0 --- proofread draft --- September 5, 2026}',r'\date{Traditional final edition --- 5 October 2026}','Identify this as the final companion edition, not a new Lean release.')
replace('  linkcolor=black,\n  citecolor=black,\n  urlcolor=black','  linkcolor=accent,\n  citecolor=accent,\n  urlcolor=accent','Use consistent navigable accent links.')
old=r'''\fancyhead[L]{Projector-Resolved Seed Calculus IV}
\fancyhead[R]{Komorebi P.}
\fancyfoot[C]{\thepage}
\setlength{\headheight}{14pt}'''
new=r'''\fancyhead[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}KOMOREBI MATHEMATICS / PAPER IV}
\fancyhead[R]{\sffamily\fontsize{8}{10}\selectfont\color{muted}TRADITIONAL PAPER}
\fancyfoot[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}Projector-resolved seed calculus}
\fancyfoot[R]{\sffamily\small\color{accent}\thepage}'''
replace(old,new,'Use final series running headers and folios.')
replace('\\begin{document}\n\\maketitle',r'''\begin{document}
\begin{titlepage}\thispagestyle{empty}
\vspace*{13mm}
{\sffamily\bfseries\color{accent}\large KOMOREBI MATHEMATICS\quad /\quad PAPER IV\par}
\vspace{12mm}
{\sffamily\bfseries\fontsize{29}{34}\selectfont Projector-Resolved\\Seed Calculus IV\par}
\vspace{8mm}
{\sffamily\fontsize{18}{23}\selectfont Cyclic Analytic Functions,\\Reciprocal Families,\\and Spectral Zero Data\par}
\vspace{12mm}{\large Komorebi P.\par}
\vspace{5mm}{\sffamily\color{muted}Traditional final edition\quad\textbullet\quad 5 October 2026\par}
\vfill
\noindent\begin{minipage}{.94\linewidth}
\textbf{Reading route.} Cyclic projection turns the exponential into residue sections and a finite differential system. Reciprocal powers lead to coefficient polynomials, Appell families, and theta polynomials. The same denominator then connects zero geometry, canonical products, and spectral zero zeta functions.

\medskip
\textbf{Companions.} The visual guide supplies worked models and exact figures. The Lean guide follows the released declarations and explains their hypotheses and evidence. This traditional paper retains the full scoped manuscript and its proofs.
\end{minipage}
\vspace{13mm}
\end{titlepage}''','Introduce the complete traditional companion with a series title page.')
replace('The released Paper IV Lean contract covers all 68 theorem-like manuscript\nresults under their stated hypotheses.', 'The preserved Paper IV v1.0.0 release records full scoped Lean coverage of all\n68 theorem-like manuscript results under their stated hypotheses.', 'Attribute the coverage statement to its inherited release evidence.')
replace('The accompanying v1.0.0 theorem map\nand formalization ledger identify the declarations and their scopes.', 'The accompanying v1.0.0 theorem map\nand formalization ledger identify the declarations and their scopes. This\nfinal companion edition retains all 95 numbered records and all 68 proofs\nof the later proofread manuscript. It is an editorial edition, not a new\nLean release; no fresh Lean execution is asserted here.', 'State manuscript preservation and the current validation boundary explicitly.')
replace('The released Lean project uses Lean 4 v4.34.0-rc2 and Mathlib revision', 'The preserved v1.0.0 release was built with Lean 4 v4.34.0-rc2 and Mathlib revision', 'Identify the ledger as the historical release record.')
replace('The full namespace audit scans\n2234 declarations, including 1999 theorem declarations. A warning-fatal\nbuild and the supplied kernel audit allow only', 'The recorded namespace audit scanned\n2234 declarations, including 1999 theorem declarations. The historical warning-fatal\nbuild and supplied kernel audit allowed only', 'Use past tense for inherited build and kernel evidence.')
replace('The declaration-level theorem map is authoritative. All 68 theorem-like\nrecords have their full scoped statements covered: 68 full, zero partial,\nand zero unmapped.', 'The declaration-level theorem map is authoritative for the preserved\nv1.0.0 contract. Its release records full scoped coverage of all 68\ntheorem-like records: 68 full, zero partial, and zero unmapped.', 'Tie the coverage count to the recorded release contract, not new execution.')
(R/'Paper_IV_Traditional_Final.tex').write_text(s)
(R/'EDITORIAL_CHANGES.json').write_text(json.dumps({'scope':'Selected September 5 proofread manuscript; final companion edition dated October 5, 2026.','mathematical_token_changes':[],'changes':changes},indent=2)+'\n')
print('Wrote final traditional source:', len(s), 'characters')
