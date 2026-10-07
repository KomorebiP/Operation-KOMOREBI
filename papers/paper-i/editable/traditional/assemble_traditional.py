from pathlib import Path
import re,shutil,json,hashlib
import argparse
parser=argparse.ArgumentParser(description="Reassemble the final traditional edition from preserved source snapshots.")
parser.add_argument('--source-collection',type=Path,help='Path to the collected Komorebi_Papers_I-XII_2026-10-05 tree')
parser.add_argument('--bundle-root',type=Path,help='Release bundle root containing source/')
args=parser.parse_args()
O=Path(__file__).resolve().parent
if args.source_collection:
 R=args.source_collection.resolve()
 old=R/'baseline/Komorebi_Complete/journal/updates/Paper_I_v1.3.1'
 source=next((R/'supplements/Paper_I/readable/PSC_I_FINAL_MACHINE_RELEASE_v1.0.0').rglob('PSC_I_authoritative_source.tex'))
 vis=R/'baseline/Komorebi_Complete/journal/core_papers/01_Paper_I/visual_appendix'
else:
 bundle=(args.bundle_root or O.parents[1]).resolve()
 old=bundle/'source/traditional_v1.3.1'
 source=next((bundle/'source/machine_v1.0.0').rglob('PSC_I_authoritative_source.tex'))
 vis=bundle/'source/visual_guide_original'
t=source.read_text(); base=(old/'paper/Projector_Resolved_Seed_Calculus_I.tex').read_text()
shutil.copytree(old/'paper/figures',O/'figures',dirs_exist_ok=True)
for sub,dest in [('graphics','visual_graphics'),('source','visual_model_sources'),('checks','visual_checks')]:shutil.copytree(vis/sub,O/dest,dirs_exist_ok=True)
checker=O/'visual_checks/verify_examples.py'
checker.write_text(checker.read_text().replace("ROOT/'source'", "ROOT/'visual_model_sources'").replace("ROOT/'source/models.py'", "ROOT/'visual_model_sources/models.py'").replace("ROOT/'checks/EXACT_CHECKS.json'", "ROOT/'visual_checks/EXACT_CHECKS.json'"))
generator=O/'visual_model_sources/generate_graphics.py'
generator.write_text(generator.read_text().replace("OUT=ROOT/'graphics'", "OUT=ROOT/'visual_graphics'"))
# Explicit audited hypothesis restorations, identical to machine v1.0.1.
fixes=[('Let $X$ be Hilbert, let the packet projectors be orthogonal, and put',r'Let $X$ be Hilbert, let the packet projectors be orthogonal, assume $X_\alpha\neq0$ for every $\alpha\in I$, and put'),('Assume the packet-resolved module is packet-propagating.  If $c_0$ denotes',r'Assume the packet-resolved module is packet-propagating and $X_\alpha\neq0$ for every $\alpha\in I$.  If $c_0$ denotes')]
for before,after in fixes:assert t.count(before)==1;t=t.replace(before,after)
t=t.replace(r'\usepackage{lmodern}',r'\usepackage{lmodern}')
t=t.replace(r'\usepackage[margin=0.98in]{geometry}',r'\usepackage[a4paper,margin=23mm,includeheadfoot,headheight=15pt,headsep=15pt,footskip=22pt]{geometry}')
t=t.replace(r'\usepackage{hyperref}',r'\PassOptionsToPackage{hyphens}{url}'+chr(10)+r'\usepackage{hyperref}')
t=t.replace(r'\usepackage{xcolor}',r'\usepackage[table]{xcolor}')
t=t.replace(r'\usepackage{makecell}',r'''\usepackage{makecell}
\usepackage{graphicx,tikz,titlesec,bookmark,caption,etoolbox,tocloft}
\setlength{\cftbeforesecskip}{4pt}
\usetikzlibrary{arrows.meta,decorations.pathreplacing,patterns,calc}
\graphicspath{{figures/}}
\definecolor{accent}{HTML}{137668}\definecolor{muted}{HTML}{536568}
\frenchspacing\emergencystretch=2em\clubpenalty=10000\widowpenalty=10000\raggedbottom
\titleformat{\section}{\sffamily\bfseries\large\color{accent}}{\thesection}{.7em}{}
\titleformat{\subsection}{\sffamily\bfseries\normalsize}{\thesubsection}{.7em}{}
\titlespacing*{\section}{0pt}{1.4\baselineskip}{.55\baselineskip}
\captionsetup{font=small,labelfont={sf,bf},labelsep=period}
\pretocmd{\section}{\Needspace{7\baselineskip}}{}{}
\pretocmd{\subsection}{\Needspace{5\baselineskip}}{}{}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcommand{\cA}{\mathcal A}\newcommand{\cB}{\mathcal B}\newcommand{\cP}{\mathcal P}
\newcommand{\R}{\mathbb R}\newcommand{\C}{\mathbb C}\newcommand{\Z}{\mathbb Z}\newcommand{\N}{\mathbb N}
\newcommand{\Spec}{\operatorname{Spec}}\newcommand{\rank}{\operatorname{rank}}\newcommand{\diag}{\operatorname{diag}}
\newcommand{\closure}[1]{\overline{#1}}
''')
t=t.replace(r'\crefname{theorem}',r'\theoremstyle{definition}\newtheorem{example}[theorem]{Example}'+'\n'+r'\newtheorem{construction}[theorem]{Construction}'+'\n'+r'\crefname{theorem}',1)
t=t.replace(r'\fancyhead[L]{PSC I: Expanded Foundation}',r'\fancyhead[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}KOMOREBI MATHEMATICS / PAPER I}')
t=t.replace(r'\fancyhead[R]{Komorebi P.}',r'\fancyhead[R]{\sffamily\fontsize{8}{10}\selectfont\color{muted}TRADITIONAL PAPER}')
t=t.replace(r'\fancyfoot[C]{\thepage}',r'\fancyfoot[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}Projector-resolved seed calculus}\fancyfoot[R]{\sffamily\small\color{accent}\thepage}')
for macro,repl in [('RecordID',r'\newcommand{\RecordID}[1]{\label{record:#1}}'),('Depends',r'\newcommand{\Depends}[1]{}'),('Exports',r'\newcommand{\Exports}[1]{}')]:
 t=re.sub(r'\\newcommand\{\\'+macro+r'\}\[1\]\{[^\n]*',lambda m:repl,t)
a=t.index(r'\title{');b=t.index(r'\begin{abstract}',a)
t=t[:a]+r'''\begin{document}
\thispagestyle{empty}
\noindent{\sffamily\bfseries\small\color{accent}KOMOREBI MATHEMATICS}\par
\vspace{.6em}\noindent{\sffamily\small\color{muted}CORE SERIES I\hfill FINAL SERIES EDITION}\par
\vspace{.7em}\noindent{\color{accent}\rule{\textwidth}{1pt}}
\vspace{1.1em}\noindent{\sffamily\bfseries\fontsize{30}{34}\selectfont Projector-resolved\\seed calculus I\par}
\vspace{.7em}\noindent{\fontsize{17}{21}\selectfont\itshape Typed operator systems, seed rank,\\and exact packet coordinates\par}
\vspace{1em}\noindent{\sffamily\bfseries Komorebi P.}\par
\noindent{\sffamily\small\color{muted}5 October 2026}\par\vspace{1.3em}
'''+t[b:]
t=t.replace("This expanded edition preserves the formal symbolic core while adding a reader's guide, notation maps, proof roadmaps, running micro-examples, hypothesis commentary, section recaps, and a glossary of common confusions.  Detailed domain examples, historical priority analysis, numerical case studies, and full visual design remain separate later passes.","The presentation combines the complete symbolic foundation with worked quiver, coordinate-ring, matrix, and graph models, an analytic shift example, exact computational specifications, and a visual atlas. Stable statement identifiers connect the traditional argument to the machine-native companion. The separate Lean guide records precisely which statements and certificate scopes have kernel-checked counterparts.")
a=t.index('\\begin{center}\n\\begin{tabular}{@{}lr@{}}');b=t.index(r'\tableofcontents',a)
t=t[:a]+r'''\noindent\textbf{Companion volumes.} The Lean guide explains the formal development, its build procedure, theorem mapping, and the hypotheses of each verified contract. The machine-native paper exposes the stable records, dependencies, and executable evidence interfaces. The mathematics below retains the full scope of its stated classical inputs and written proofs.
\clearpage
'''+t[b:]
t=t.replace(r'\RecordID{PSC-I-D-COEFFICIENT-REGIME}',r'\RecordID{PSC-I-D-COEFFICIENT-REGIME}'+chr(10)+r'\paragraph{Empty-family conventions.} For finite families of nonnegative integers we use $\max\varnothing=0$. The height of an empty finite partially ordered set is $0$, as is the height of a nonempty poset with no strict comparable pair. Thus the height in the support-preorder theorem counts strict steps.')
# Move the status table off the cover and place it with the reading orientation.
a=t.index('\\begin{center}\n\\begin{tabularx}{0.96\\textwidth}{@{}lY@{}}');b=t.index('\\clearpage',a)
front_note=t[a:b];t=t[:a]+t[b:]
anchor="\\addcontentsline{toc}{section}{Reader's orientation}"
t=t.replace(anchor,anchor+'\n'+front_note,1)
t=t.replace(r'\tableofcontents',r'\begingroup\small\setstretch{1.0}\tableofcontents\endgroup',1)
t=t.replace('\\clearpage\n\n\\section{Coefficient conventions', '\\section{Coefficient conventions')
t=t.replace('The following small systems recur throughout the explanatory boxes.  They are not substitutes for the later full example pass.  They are local orientation devices.','The following small systems recur throughout the explanatory boxes. The worked models and visual atlas later develop these ideas in complete calculations.')
a=t.index('\\ConceptChain{\n\\(\n\\text{typed grammar}');b=t.index('\n\nThe words in this chain',a)
t=t[:a]+r'''\ConceptChain{\(\begin{gathered}
\text{typed grammar}\longrightarrow\text{realized algebra}\longrightarrow\text{seed hull}\\[.45em]
\longrightarrow\text{seed rank}\longrightarrow\text{packet coordinates}\\[.45em]
\longrightarrow\text{transfer blocks}\longrightarrow\text{functorial realization}.
\end{gathered}\)}'''+t[b:]
t=t.replace(r'\begin{definition}[Reserved example slots]',r'\begin{definition}[Worked realization interface]')
t=t.replace('The later example pass for Paper I is reserved for exactly four canonical realizations:','The foundational calculus is illustrated by four canonical algebraic realizations:')
t=t.replace('The bilateral shift belongs to Paper V, while computational orbit-hull and graph-rank algorithms belong to the verification supplement or Paper VIII.','The worked-model sections below instantiate these four interfaces. A bilateral-shift example records the analytic completion mechanism also used in Paper V. Computational specifications connect the proofs with the verification companion and are not premises of the foundational theorems.')
a=base.index(r'\section{A typed quiver model}');b=base.index(r'\section{Formal verification record}',a);models=base[a:b]
models=models.replace('prop:scalar-quotient-obstruction','prop:scalar-quotient')
models=models.replace('The kernel-checked general result\nstarts from an exact spectral certificate rather than deriving one from graph\nsymmetry.','The general result applies directly to a spectral certificate. For a symmetric real adjacency matrix, the classical spectral theorem supplies such data.')
models=models.replace('The all-field, kernel-checked certificate is instead combinatorial.','There is also an all-field combinatorial proof.')
models=models.replace('Their\nkernel-checked minimum finite seed numbers differ','Their\nminimum finite seed numbers differ')
models=models.replace('Representative computed checks from the journal-edition run.','Archived representative checks from the v1.3.1 journal-edition run. Fresh companion runs are reported separately in the release verification record.')
models=models.replace('The Lean component proves mathematical specifications for the following\nfinite constructions.  These statements establish termination and\ncorrectness at the level of subspaces, block tables, and exact certificates;\nthey do not assert code extraction or a particular backend\'s performance.','The following finite constructions state mathematical specifications for the companion. Their Lean counterparts and exact scope are listed in the separate guide. They do not assert code extraction or a particular backend\'s performance.')
t=t.replace(r'\section{Digestibility guide: common confusions and diagnostic questions}',models+'\n\\section{Reading guide: common confusions and diagnostic questions}')
# Remove a vacant orientation heading; move recaps before the next section they do not summarize.
t=t.replace(r'\subsection{The evaluation map and its universal quotient}'+chr(10)+chr(10),'')
t=re.sub(r'(\\section\{[^\n]+\}\s*)(\\begin\{sectionrecap\}[\s\S]*?\\end\{sectionrecap\})',lambda m:m.group(2)+'\n\n'+m.group(1),t)
t=t.replace(r'\section{Expanded notation and convention ledger}',r'\section{Notation and convention ledger}')
t=t.replace(r'\section{Symbolic completion statement}',r'\clearpage\section{Conclusions and further use}')
t=t.replace('Every target in the Phase 0 Paper I skeleton has now been resolved as follows:','The main structural conclusions can be collected in the following form:')
for oldlabel,anchor in [('fig:grammar',r'\section{Free presentations by seeds and relations}'),('fig:semisimple',r'\section{Single-operator modules over arbitrary fields}'),('fig:krylov',r'\section{Exact finite and countable packet coordinates}'),('fig:transfer-blocks',r'\section{Transfer graphs and directed packet generation}'),('fig:coordinate-transport',r'\section{Realization functors and semantic theorem transport}')]:
 fm=re.search(r'\\begin\{figure\}[\s\S]*?\\label\{'+re.escape(oldlabel)+r'\}[\s\S]*?\\end\{figure\}',base)
 if fm:value=fm.group(0);value=value[value.rfind('\\begin{figure}'):];t=t.replace(anchor,value+'\n\n'+anchor,1)
records=[]
for m in re.finditer(r'\\begin\{(theorem|proposition|lemma|corollary|definition|classicalinput|boundary|remark)\}(?:\[([^\n]*)\])?([\s\S]*?)\\end\{\1\}\s*\\RecordID\{([^}]+)\}',source.read_text()):
 label=re.search(r'\\label\{([^}]+)\}',m.group(3));records.append({'id':m.group(4),'kind':m.group(1),'title':m.group(2) or '', 'label':label.group(1) if label else None})
rows=[]
for item in records:
 if item['id']=='PSC-I-ALG-EXAMPLE-SLOTS':item['title']='Worked realization interface'
 label=item['label'];ref=('\\ref{'+label+'}') if label else '\\ref{record:'+item['id']+'}'
 rows.append('\\nolinkurl{'+item['id']+'} & '+ref+' & '+item['title']+r' \\')
concordance=r'''\clearpage\appendix
\section{Stable statement concordance}\label{app:stable-concordance}
These identifiers preserve the expanded foundation's 108-record namespace. The display numbers refer to this edition. They identify mathematical statements, not a count of Lean-verified theorems. The worked-model statements added after the foundation retain their source labels and are mapped separately by the Lean guide.
\small\begin{longtable}{@{}p{.44\textwidth}p{.07\textwidth}p{.41\textwidth}@{}}
\toprule Stable identifier & No. & Statement\\\midrule\endhead
'''+ '\n'.join(rows)+r'''
\bottomrule\end{longtable}\normalsize
\clearpage\section{Visual atlas}\label{app:visual-atlas}
The following twenty-two plates give exact finite models, explanatory diagrams, and one analytic density example. All graphics are generated from mathematical source. Cross-references are aligned with this edition. The atlas illustrates the proofs and hypotheses in the main text.

\medskip
\begin{longtable}{@{}p{.08\textwidth}p{.82\textwidth}@{}}
\toprule Plate & Route through the examples\\\midrule\endhead
1--2 & Fixed grammars, seed power, and the objects of the calculus.\\
3--4 & Two linked chains and a quotient proving the minimum seed count.\\
5--6 & Left-ideal relations and typed reachability with a missing direction.\\
7--8 & Oblique exact coordinates and complete transfer-block multiplication.\\
9--10 & Cancellation along paths and the algebra of admissible zero patterns.\\
11--12 & Coordinate transport, shared action, and independent control.\\
13--14 & Semisimple multiplicity budgets and primary extraction polynomials.\\
15--16 & Path endpoints and the cycle's two-dimensional quotient obstruction.\\
17 & A coordinate-ring relation as a two-packet product rule.\\
18--19 & Dense shift generation, residue coordinates, and address carry.\\
20--21 & Exact orbit-hull stabilization and all tensor cross terms.\\
22 & The scope of mathematical, formal, and computational evidence.\\
\bottomrule\end{longtable}

The seed examples can be read consecutively, while the packet and graph plates form independent entry points. The displayed matrices are exact. Numerical illustrations in the earlier figures retain their explicitly stated finite ranges. Every diagram is accompanied by the equation or obstruction it represents.
\begingroup\fontsize{10.2}{11.6}\selectfont\setstretch{1.0}\setlength{\parindent}{0pt}\setlength{\parskip}{2pt}\setlength{\abovedisplayskip}{7pt}\setlength{\belowdisplayskip}{7pt}\input{visual_atlas.tex}\endgroup
'''
visualmacros=r'''
\newcommand{\OO}{\mathcal O}\newcommand{\FF}{\mathbb F}\newcommand{\QQ}{\mathbb Q}\newcommand{\ZZ}{\mathbb Z}\newcommand{\RR}{\mathbb R}\newcommand{\CC}{\mathbb C}\newcommand{\kk}{\mathbb k}
\renewcommand{\AA}{\mathcal A}\newcommand{\BB}{\mathcal B}
\newcommand{\Fitt}{\operatorname{Fitt}}\newcommand{\Ann}{\operatorname{Ann}}\newcommand{\coker}{\operatorname{coker}}\newcommand{\Tr}{\operatorname{Tr}}
\newcommand{\whot}{\mathbin{\widehat\otimes}}\newcommand{\m}{\mathfrak m}\newcommand{\p}{\mathfrak p}
\newcommand{\head}[1]{\par\vspace{2pt}{\sffamily\bfseries\normalsize #1}\par\vspace{1pt}}
\newcommand{\atlasCaption}[1]{\par\noindent{\footnotesize\color{black!70}#1\par}}
\newtcolorbox{insight}{colback=black!3,colframe=accent,boxrule=0pt,leftrule=1.1pt,arc=0pt,left=10pt,right=10pt,top=5pt,bottom=5pt,before skip=6pt,after skip=5pt}
\newcommand{\takeaway}[1]{\begin{insight}\textbf{Read this as:}\ #1\end{insight}}
\newcommand{\vfig}[2][.92]{\par\begingroup\centering\resizebox{#1\linewidth}{!}{\input{visual_graphics/#2.tex}}\par\endgroup\vspace{2pt}}
\newcommand{\vpage}[4]{\clearpage\hypertarget{visual:#1}{}\pdfbookmark[2]{V#1. #2}{PIA.visual#1}{\sffamily\small\bfseries\color{accent}PLATE #1 / #3\par}\vspace{5pt}{\sffamily\bfseries\fontsize{22}{25}\selectfont #2\par}\vspace{5pt}{\sffamily\fontsize{8.7}{11}\selectfont\color{black!65}#4\par}\vspace{6pt}}
\newcommand{\pagerefV}[1]{\hyperlink{visual:#1}{Plate~#1}}
\newcommand{\norm}[1]{\left\lVert#1\right\rVert}\newcommand{\mat}[1]{\begin{pmatrix}#1\end{pmatrix}}
'''
t=t.replace(r'\begin{document}',visualmacros+'\n\\begin{document}',1)
bib=base[base.index(r'\begin{thebibliography}'):base.index(r'\end{thebibliography}')+len(r'\end{thebibliography}')]
t=t.replace(r'\end{document}',concordance+'\n\\clearpage\n'+bib+'\n\\end{document}')
vp=(vis/'source/pages.tex').read_text()
headers=[r'\cref{def:seed-rank,prop:acting-algebra-monotonicity,thm:exact-packet-coordinates}',r'\cref{def:typed-grammar,def:seed-system,def:seed-rank,def:packet-system,def:transfer-block}',r'\cref{thm:single-operator}; matrices over $\QQ$',r'\cref{prop:scalar-quotient,thm:single-operator}',r'\cref{thm:free-presentation,cor:one-seed-presentation,prop:two-sided-annihilator}',r'\cref{prop:typed-reachability,def:directed-seed-rank}',r'\cref{thm:exact-packet-coordinates,cor:adjoint-reversal}',r'\cref{thm:operator-reconstruction,thm:block-multiplication,cor:block-powers}',r'\cref{cor:block-powers,prop:reachability-obstruction}',r'\cref{thm:support-pattern}; all packet spaces nonzero',r'\cref{thm:coordinate-transport,cor:isomorphism-invariance,thm:naturality}',r'\cref{prop:shared-direct-sum,thm:independent-direct-sum}',r'\cref{thm:semisimple-seed-rank,cor:algebraically-closed-formula}',r'\cref{thm:single-operator,cor:invariant-factor-count}','Worked graph model: all-size endpoint Krylov proof','Worked graph model: complex minimum-seed proof for cycles','Worked coordinate-ring model: normal form and exact multiplication',r'\cref{prop:shift-seed,thm:completed-presentation}',r'\cref{thm:banach-packets}; residue packets',r'\cref{con:orbit-hull-algorithm}',r'\cref{prop:tensor-bound}; algebraic tensor products','Reading the theorem hypotheses and companion evidence']
updated=[]
for line in vp.splitlines():
 if line.startswith('\\vpage{'):
  pos=len('\\vpage');args=[]
  for k in range(4):
   assert line[pos]=='{';start=pos+1;depth=1;pos+=1
   while depth:
    if line[pos]=='{':depth+=1
    if line[pos]=='}':depth-=1
    pos+=1
   args.append(line[start:pos-1])
  args[3]='Main text: '+headers[int(args[0])-1];line='\\vpage'+''.join('{'+a+'}' for a in args)
 updated.append(line)
vp='\n'.join(updated).replace(r'\captiontext',r'\atlasCaption');a=vp.index(r'\vpage{22}');last=vp[a:];last=last[:last.index('\n')]+r'''
The mathematical statements in the main text have explicit hypotheses and written proofs. The Lean guide separately identifies the checked declarations and certificate assumptions. The machine-native paper identifies the 108 stable foundation records and the checks executed on their structured representations. These are distinct forms of evidence.

{\small\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}p{.23\linewidth}Y>{\raggedright\arraybackslash}p{.25\linewidth}@{}}\toprule
\textbf{Topic} & \textbf{Mathematical content} & \textbf{What must be retained}\\\midrule
Presentations and hulls & Evaluation, module quotients, and generation under a fixed algebra. & The grammar must be fixed independently of the target.\\
Finite packets & Idempotence, annihilation, completeness and exact finite synthesis. & Orthogonality requires an additional hypothesis.\\
Semisimple formula & Division-ring multiplicities determine the minimal free cover. & The stated classical inputs and decomposition data.\\
Primary and graph formulas & Primary components and scalar quotients give sharp generator counts. & The coefficient field and multiplicity conventions.\\
Paths and cycles & All-size path and complex-cycle formulas have separate proofs. & Finite tests illustrate rather than prove all-size claims.\\
Coordinate algebra & Normal form, multiplication, packet identities and a unit seed. & Smooth projective geometry needs additional classical input.\\
Completion & Density and bounded extraction in the stated topology. & Infinite sequences are distinct from periodic finite arrays.\\\bottomrule\end{tabularx}}

\head{Evidence travels with the examples}
The release includes mathematical source, exact model definitions, deterministic graphics, Python checks, Lean source and theorem mapping, and the machine-native record archive. The visual models use integer, rational, symbolic, or explicitly analytic calculations. The separate verification record distinguishes fresh executions from archived evidence.

\takeaway{The pictures make the hypotheses visible. Read the traditional proof, the formal contract, and the executable record at their respective stated scopes.}
''';vp=vp[:a]+last
(O/'visual_atlas.tex').write_text(vp);(O/'Paper_I_Traditional_Final.tex').write_text(t)
(O/'stable_record_index.json').write_text(json.dumps(records,indent=2))
(O/'EDITORIAL_CHANGES.json').write_text(json.dumps({'base_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'core_records':len(records),'mathematical_token_changes':[{'before':a,'after':b} for a,b in fixes],'changes':['Publication typography and front matter','Removed historical future-pass prose','Updated reserved-example interface to actual worked models','Integrated corrected v1.3.1 worked models and specifications','Integrated all22visualplates with live cross-references','Detailed formal evidence moved to Lean companion','Printed stable-ID concordance']},indent=2))
print('WROTE',len(t),'characters',len(records),'records')
