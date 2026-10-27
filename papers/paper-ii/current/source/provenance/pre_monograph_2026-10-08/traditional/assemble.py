from pathlib import Path
import re,json,hashlib,shutil
R=Path(__file__).resolve().parent
P=R/'source'; P.mkdir(exist_ok=True); (R/'figures').mkdir(exist_ok=True)
OLD=R.parents[1]/'Paper_II/source'
if not (P/'canonical.tex').exists():
 shutil.copy2(OLD/'release_v1.2.1/paper/Projector_Resolved_Seed_Calculus_II.tex',P/'canonical.tex')
 shutil.copy2(OLD/'annals_expanded/PSC_Paper_II_Annals_Human_Edition.tex',P/'expanded.tex')
 shutil.copy2(OLD/'annals_expanded/PSC_Paper_II_Annals_Human_Edition.bib',P/'expanded.bib')
 for f in (OLD/'release_v1.2.1/paper/figures').glob('*.pdf'):shutil.copy2(f,R/'figures'/f.name)
C=(P/'canonical.tex').read_text(); E=(P/'expanded.tex').read_text(); changes=[]
def edit(text,old,new,reason):
 if old not in text:raise ValueError('patch not found '+old[:60])
 changes.append({'old':old,'new':new,'reason':reason,'new_lean_coverage':False})
 return text.replace(old,new)
def sec(t,title):
 st=t.index('\\section{'+title+'}'); en=t.find('\\section{',st+10)
 if en<0:en=len(t)
 return t[st:en]
def theorem(t,label):
 pos=t.index('\\label{'+label+'}');st=t.rfind('\\begin{',0,pos);env=re.match(r'\\begin\{([^}]+)\}',t[st:])[1]
 en=t.index('\\end{'+env+'}',pos)+len('\\end{'+env+'}')
 pm=re.match(r'\s*\\begin\{proof\}[\s\S]*?\\end\{proof\}',t[en:])
 if pm:en+=pm.end()
 return t[st:en]
body=E[E.index('\\section{Introduction}'):E.index('\\bibliographystyle')]
# Audited explicit hypotheses and boundary conventions; proof bodies are unchanged.
body=edit(body,'The operators $(P_{N,j})_{0\\leq j<N}$ form a packet system on $R[[z]]$:', 'For every commutative ring $R$, the operators $(P_{N,j})_{0\\leq j<N}$ satisfy the identities below.  If $R$ is nonzero, they form a packet system on $R[[z]]$:', 'Nonzero packet definition excludes the zero-ring carrier; displayed identities remain valid for all R.')
body=edit(body,'If $N$ divides $M$, then','Let $N,M$ be positive integers with $N$ dividing $M$, and let $0\\leq j<N$.  Then','Restore inherited positive-modulus domain.')
body=edit(body,'Thus the packet system modulo $M$ refines the packet system modulo $N$.','When $R$ is nonzero, the packet system modulo $M$ refines the packet system modulo $N$.','Propagate the nonzero-ring qualifier for packet-system terminology.')
body=edit(body,'A complete filtered algebra is a unital algebra $\\Bcal$ with a decreasing sequence','A complete filtered algebra is a unital algebra $\\Bcal$ with a decreasing sequence of two-sided ideals','Quotient rings and additive filtration limits require ideals.')
body=edit(body,'is invertible on every packet, and write','belongs to $\\Bcal$ and is invertible on every packet.  Assume that the assembled inverse\n\\[\nD^{-1}=\\sum_\\alpha D_\\alpha^{-1}P_\\alpha\\in\\Bcal=F^0\\Bcal,\n\\qquad D_\\alpha=P_\\alpha DP_\\alpha,\n\\]\nwhere each packet inverse is extended by zero to the other packets.  Let the edge set be finite, assume $w(e)\\geq1$ for every edge, and write','Packetwise ambient invertibility is insufficient: D=pI,N=-pI in B=Z_p gives T=0. Restore the preceding weighted-inverse hypotheses.')
body=edit(body,'with $d=\\infty$ when no path exists.  If','with $d=\\infty$ when no path exists.  Use the convention $F^\\infty\\Bcal=\\bigcap_{L\\geq0}F^L\\Bcal=0$.  If','Define the infinite filtration index used by the no-path endpoint.')
body=edit(body,'s_\\Lambda(\\Pcal)=\\max_\\alpha s_\\Lambda(E_\\alpha).','s_\\Lambda(\\Pcal)=\\max\\bigl(\\{0\\}\\cup\\{s_\\Lambda(E_\\alpha):\\alpha\\in I\\}\\bigr).','Empty packet family on zero vector space has separation weight zero.')
body=edit(body,'s_\\Lambda(\\Pcal)=a_r.','s_\\Lambda(\\Pcal)=\\max\\bigl(\\{0\\}\\cup\\{a_j:1\\leq j\\leq r\\}\\bigr).','Zero gluing module has no largest indexed Smith exponent; include zero.')
body=edit(body,'s_\\Lambda(\\Pcal)=\\max_ja_j.','s_\\Lambda(\\Pcal)=\\max\\bigl(\\{0\\}\\cup\\{a_j:1\\leq j\\leq r\\}\\bigr).','Same empty Smith decomposition convention.')
body=edit(body,'s_\\Lambda(\\Pcal)=a_n.','s_\\Lambda(\\Pcal)=\\max\\bigl(\\{0\\}\\cup\\{a_j:1\\leq j\\leq n\\}\\bigr).','Zero-dimensional inclusion matrix has no a_n; same zero convention.')
body=edit(body,'from $\\Lambda/\\pi^{m+s}\\Lambda$ to $V/\\pi^m\\Lambda$ is well defined.  If $d<s$, then for every $m\\geq0$','from $\\Lambda/\\pi^{m+s}\\Lambda$ to $V/\\pi^m\\Lambda$ is well defined.  Here $m$ is an integer.  If $d$ is an integer with $0\\leq d<s$, then for every integer $m\\geq0$','Necessity quantifies nonnegative precision depths; negative d invalidates x in lattice.')
body=edit(body,'Let $X_f$ and $X_c$ be vector spaces or Banach spaces, let\n\\[\nC:X_f\\longrightarrow X_c,\n\\]','Let $X_f$ and $X_c$ be vector spaces or Banach spaces over a common field, and let\n\\[\nC:X_f\\longrightarrow X_c\n\\]\nbe a linear map,','Linearity of C is consumed by all defect proofs.')
body=edit(body,'Let $T_f$ and $T_c$ be bounded operators on complex Banach spaces.  Let $h$ be holomorphic on a neighborhood of both spectra, and let $\\Gamma$ be a union of positively oriented contours surrounding both spectra inside that neighborhood.  Then','Let $X_f$ and $X_c$ be complex Banach spaces, and let $C:X_f\\to X_c$, $T_f$, and $T_c$ be bounded complex-linear maps.  Let $h$ be holomorphic on an open set $U$ containing both spectra.  Let $\\Gamma$ be an admissible finite rectifiable Cauchy cycle in $U$ and in both resolvent sets, with winding number one on the union of the spectra and zero outside $U$.  The length of a cycle counts multiplicities.  Then','Bounded linear C permits composition under integral; admissible winding excludes repeated nested positively oriented contours.')
body=edit(body,'For bounded operators and every real or complex $t$,','Let $C:X_f\\to X_c$, $T_f$, and $T_c$ be bounded linear maps between Banach spaces over a common field.  For real $t$, use real or complex spaces; for complex $t$, use complex spaces and complex-linear maps.  Then','All three maps must be bounded linear; complex parameter requires complex spaces.')
body=edit(body,'C_\\ell:X_{\\ell+1}\\longrightarrow X_\\ell\n\\]\nfor $0\\leq\\ell<L$,','C_\\ell:X_{\\ell+1}\\longrightarrow X_\\ell\n\\]\nbe linear maps for $0\\leq\\ell<L$,','Make multilevel linearity explicit.')
body=edit(body,'have resultant $\\pi^s$, but','have resultant $-\\pi^s$, up to the harmless choice of resultant order, but','Ordered Res(x,x-pi^s)=-pi^s; valuation unchanged.')
body=edit(body,'Its eigenvalue factors have resultant $\\pi^s$, and','Its eigenvalue factors have resultant equal to $\\pi^s$ up to a unit, and','Separate resultant sign from its valuation.')
# Shared canonical results are exact anchor aliases, never counted as new Lean rows.
aliases={'def:refinement-map':'def:refinement','thm:nested-refinement':'thm:children_transitivity','def:coordinate-refinement':'def:coordinate_change','prop:perfect-reconstruction':'thm:coordinate_coherence','thm:transfer-block-refinement':'thm:block_refinement','prop:residue-algebra':'prop:residue_algebra','thm:polyphase-refinement':'thm:residue_refinement','thm:dyadic-odd':'cor:dyadic_odd_coordinates','thm:power-defect':'thm:power_defect','thm:resolvent-defect':'thm:resolvent_defect'}
for old,new in aliases.items():body=body.replace('\\label{'+new+'}','\\label{'+new+'}\\label{'+old+'}')
# Insert additions at their mathematical positions. Shared proofs remain in the core.
naturality=C[C.index('These coordinate changes are coherent'):C.index('\\subsection{Operator blocks under refinement}')]
body=body.replace('\\subsection{Operator blocks across refinement}', '\\subsection{Typed coordinate naturality}\n'+naturality+'\n\\subsection{Operator blocks across refinement}')
# Canonical nested uniqueness, stated as explanation without new theorem numbering.
body=body.replace('\\subsection{Typed coordinate naturality}',r'''Every coarse packet is also uniquely reconstructed from its fine children.  If vectors $x_\beta\in Q_\beta X$ sum to a coarse packet $x$, applying $Q_\gamma$ recovers $x_\gamma=Q_\gamma x$.  This is the uniqueness clause of the canonical nested-refinement statement.

\subsection{Typed coordinate naturality}''')
fourier=C[C.index('\\subsection{Finite Fourier realization}'):C.index('\\subsection{Nested residue refinement}')]
fourier=fourier.replace('\\subsection{Finite Fourier realization}','\\subsection{Finite orthogonality certificates}')
body=body.replace('\\begin{theorem}[Character realization]',fourier+'\n\\subsection{The field specialization}\n\\begin{theorem}[Character realization]')
weighted=sec(C,'Weighted transfer words').replace('\\section{Weighted transfer words}','\\subsection{Finite quotient and normed-ring realizations}').replace('\\subsection{Filtered operator algebras}','\\subsubsection{Normalized edges and written-word convention}')
weighted=r'''\paragraph{Two compatible word conventions.} The path expansion above labels a word in chronological order and writes its operator product in reverse order, so the first edge acts first.  The following finite-word contract uses written multiplication order.  Reversing all word labels identifies the sums over all words; individual path labels must retain their stated convention.  The two conventions do not change a weight or an inverse.

'''+weighted
body=body.replace('\\section{Rational weighted transfer series}',weighted+'\n\\section{Rational weighted transfer series}')
zeta=sec(C,'Transfer-zeta functions').replace('\\section{Transfer-zeta functions}','\\subsection{Automatic finite-graph construction}')
body=body.replace('\\section{Rational spectral projectors and resultant bounds}',zeta+'\n\\section{Rational spectral projectors and resultant bounds}')
bezout=sec(C,'Integral spectral packets').replace('\\section{Integral spectral packets}','\\subsection{Evaluated certificates and explicit lattice action}').replace("\\subsection{B\\'ezout projectors}","\\subsubsection{Minimal evaluated B\\'ezout identities}").replace('\\subsection{Precision delay}','\\subsubsection{Certificate-level precision delay}')
body=body.replace('\\section{Exact lattice separation}',bezout+'\n\\section{Exact lattice separation}')
sign=sec(C,'The exceptional dyadic sign split').replace('\\section{The exceptional dyadic sign split}','\\subsection{The concrete rational sign matrix}').replace('\\subsection{Why coefficient packets remain available}','\\subsubsection{Why coefficient packets remain available}')
body=body.replace('\\section{Smith normal form and congruence lifting}',sign+'\n\\section{Smith normal form and congruence lifting}')
smith=sec(C,'Smith weights and multivariable lifting').replace('\\section{Smith weights and multivariable lifting}','\\subsection{Concrete diagonal fibres over integer quotients}')
smith=edit(smith,'p^s x=b\\pmod{p^L}\n\\quad\\Longleftrightarrow','\\bigl(\\exists x\\in\\mathbb Z/p^L\\mathbb Z:\\quad p^s x=b\\pmod{p^L}\\bigr)\n\\quad\\Longleftrightarrow','Restore uniquely forced existential quantifier in the displayed solvability equivalence.')
body=body.replace('\\section{Linear refinement defects}',smith+'\n\\section{Linear refinement defects}')
norm=theorem(C,'cor:defect-norm')
body=body.replace('\\begin{corollary}[Polynomial defect]',norm+'\n\n\\begin{corollary}[Polynomial defect]')
extra=C[C.index('For continuous linear maps, the same identity'):C.index('\\section{Worked realizations in the common operator language}')]
body=body.replace('\\begin{theorem}[Holomorphic functional calculus defect]', '\\subsection{One-sided inverse witnesses and operator-norm control}\n'+extra+'\n\\subsection{Analytic functional calculus}\n\\begin{theorem}[Holomorphic functional calculus defect]')
worked=sec(C,'Worked realizations in the common operator language')
num=sec(C,'Numerical certificates')
# Numerical results are retained as dated source evidence rather than new formal claims.
num=num.replace('\\section{Numerical certificates}', '\\section{Finite computational certificates}\nThe following results and tables are the recorded v1.2.1 finite implementation evidence.  They do not certify the expanded lattice or analytic statements in Lean.  Current reproduction outcomes are reported in the verification files accompanying this edition.\n')
body=body.replace('\\section{Scope and limits}',worked+'\n'+num+'\n\\section{Scope and limits}')
# Foundational pictures are retained alongside the existing exact prose.
for key,anchor in [('01_nested_dyadic_refinement','\\subsection{Operator blocks across refinement}'),('03_refinement_incidence','\\subsection{Common refinements}'),('02_crt_dyadic_odd_grid','\\section{Complete filtered transfer algebras}')]:
 pat=re.search(r'\\begin\{figure\}[\s\S]*?\\includegraphics[^\n]*\{'+key+r'\.pdf\}[\s\S]*?\\end\{figure\}',C)
 # restrict backwards to nearest figure beginning
 end=C.index('\\end{figure}',C.index('{'+key+'.pdf}'))+len('\\end{figure}')
 st=C.rfind('\\begin{figure}',0,C.index('{'+key+'.pdf}')); fig=C[st:end]
 body=body.replace(anchor,fig+'\n'+anchor,1)
# Appendix contains substantive algorithm specifications, notation and dependencies.
appendix=C[C.index('\\section{Notation table}'):C.index('\\section{Reproducibility layout}')]
body+='\n\\appendix\n'+appendix
body+=r'''\section{Edition and proof scope}\label{sec:edition-scope}
The traditional article is a single topic-ordered edition.  The expanded ordinary-proof branch supplies the main narrative, including common refinements, complete filtered inversion, exact lattice gluing, rectangular Smith congruences, and analytic and multilevel defects.  The canonical v1.2.1 release supplies the explicitly certified specializations, finite graph construction, worked realizations, and three algorithm specifications.

The frozen Lean contract has 25 rows: 21 canonical numbered items, one Smith-phase identity, and three algorithm specifications.  A shared human theorem can serve more than one source address, and a contract row may use several Lean declarations.  These are distinct counting units.  In particular, the complete inverse-limit filtered theorem, general lattice gluing theorem, holomorphic and exponential calculus, and multilevel statements are ordinary written proofs here; the inherited 25-row contract does not automatically cover them.

The source statements have received only the recorded local hypothesis and endpoint repairs.  The original branch sources are preserved beside this editable edition.  The source crosswalk records original labels, final labels, display numbers, pages, and the relationship between the scopes.  The proof-preservation audit compares every inherited proof body.  No fresh Lean compiler replay is asserted by this article.

The standalone visual guide gives exact worked models.  The Lean guide explains declaration-level contracts, pins, and recorded build evidence.  Illustrations and finite tests support understanding and implementation checks; they do not replace universal proofs.
'''
# Combined bibliography from canonical generated bbl-style bibliography and Annals bib.
body=body.replace('\\section*{Use of language model tools}', '\\section*{Use of language model tools}\\addcontentsline{toc}{section}{Use of language model tools}')
# Shared references use canonical bibliography aliases to existing entries.
for old,new in {'serre1979':'Serre1979','lang2002':'Lang2002','stanley2012':'Stanley2012','vaidyanathan1993':'Vaidyanathan1993'}.items():
 body=re.sub(r'(?<=\{)'+old+r'(?=[,}])',new,body);body=body.replace(','+old,','+new)
bib=(P/'expanded.bib').read_text()+r'''
@misc{komorebi2026projectorI,author={Komorebi P.},title={Projector-Resolved Seed Calculus I: Typed Seeds, Operator Grammars, and Exact Reconstruction},year={2026},note={Version 1.2.1, manuscript and verification release}}
@inproceedings{demoura2015lean,author={de Moura, Leonardo and Kong, Soonho and Avigad, Jeremy and van Doorn, Floris and von Raumer, Jakob},title={The Lean Theorem Prover (System Description)},booktitle={Automated Deduction---CADE-25},year={2015},pages={378--388},doi={10.1007/978-3-319-21401-6_26}}
@inproceedings{mathlib2020,author={{The Mathlib Community}},title={The Lean Mathematical Library},booktitle={Proceedings of CPP},year={2020},pages={367--381},doi={10.1145/3372885.3373824}}
@book{pozar2012,author={Pozar, David M.},title={Microwave Engineering},edition={4},publisher={Wiley},year={2012}}
'''
(R/'references.bib').write_text(bib)
# Preserve all source macro definitions (same mathematics) under the article design.
macroE=E[E.index('\\newtheorem{theorem}'):E.index('\\title[')]
macroC=C[C.index('\\newcommand{\\Seed}'):C.index('\\lstset')]
macroC=macroC.replace('\\newcommand','\\providecommand')
# L/Y duplicated through shared macro block only once.
preamble=r'''\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[a4paper,margin=23mm,includeheadfoot,headheight=15pt,headsep=15pt,footskip=22pt]{geometry}
\usepackage[nopatch=footnote]{microtype}
\usepackage{amsmath,amssymb,amsthm,mathtools,aliascnt}
\usepackage{booktabs,longtable,array,tabularx,enumitem,fancyhdr,graphicx}
\usepackage[table]{xcolor}\usepackage{setspace,needspace,listings,caption,titlesec,etoolbox}
\PassOptionsToPackage{hyphens}{url}\usepackage{hyperref}\usepackage[nameinlink,noabbrev]{cleveref}\usepackage{bookmark}
\definecolor{accent}{HTML}{137668}\definecolor{muted}{HTML}{536568}
\frenchspacing\emergencystretch=3em\clubpenalty=10000\widowpenalty=10000\raggedbottom
\titleformat{\section}{\sffamily\bfseries\large\color{accent}}{\thesection}{.7em}{}
\titleformat{\subsection}{\sffamily\bfseries\normalsize}{\thesubsection}{.7em}{}
\titlespacing*{\section}{0pt}{1.4\baselineskip}{.55\baselineskip}
\captionsetup{font=small,labelfont={sf,bf},labelsep=period}
\pretocmd{\section}{\Needspace{7\baselineskip}}{}{}\pretocmd{\subsection}{\Needspace{5\baselineskip}}{}{}
\allowdisplaybreaks\setstretch{1.055}\setlength{\parskip}{.3em}\setlength{\parindent}{1.35em}
\setlist[itemize]{topsep=.35em,itemsep=.15em,leftmargin=1.6em}\setlist[enumerate]{topsep=.35em,itemsep=.15em,leftmargin=1.8em}
\graphicspath{{figures/}}
\hypersetup{pdftitle={Projector-Resolved Seed Calculus II: Refinement, Weighted Transfer and Integral Separation},pdfauthor={Komorebi P.},colorlinks=true,linkcolor=accent,citecolor=accent,urlcolor=accent}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}KOMOREBI MATHEMATICS / PAPER II}
\fancyhead[R]{\sffamily\fontsize{8}{10}\selectfont\color{muted}TRADITIONAL PAPER}
\fancyfoot[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}Projector-resolved seed calculus}\fancyfoot[R]{\sffamily\small\color{accent}\thepage}
\lstset{basicstyle=\ttfamily\footnotesize,breaklines=true,frame=single,showstringspaces=false,columns=fullflexible,keepspaces=true}
'''+macroE+macroC+r'''
\theoremstyle{definition}\newtheorem{construction}[theorem]{Construction}\newtheorem{certificate}[theorem]{Numerical Certificate}
\theoremstyle{remark}\newtheorem{boundary}[theorem]{Boundary}
\begin{document}
\begin{titlepage}\thispagestyle{empty}
\vspace*{13mm}
{\sffamily\bfseries\color{accent}\large KOMOREBI MATHEMATICS\quad /\quad PAPER II\par}
\vspace{12mm}
{\sffamily\bfseries\fontsize{29}{34}\selectfont Projector-Resolved\\Seed Calculus II\par}
\vspace{8mm}
{\sffamily\fontsize{18}{23}\selectfont Refinement Towers, Weighted Transfer,\\and Integral Separation of Operator Packets\par}
\vspace{12mm}{\large Komorebi P.\par}
\vspace{5mm}{\sffamily\color{muted}Traditional final edition\quad\textbullet\quad 5 October 2026\par}
\vfill
\noindent\begin{minipage}{.94\linewidth}
\textbf{Reading route.} Exact coordinates and residue selectors lead to weighted inversion and rational walk series.  Integral lattice gluing then gives exact separation weights and precision delays.  Smith congruences and typed defect formulas connect the algebra to finite computation and operator calculus.

\medskip
\textbf{Scope.} Full ordinary proofs and the revised 25-row formal contract are distinguished throughout.  The expanded analytic and lattice results retain their own hypotheses; inherited formal coverage does not expand merely because both presentations appear in this edition.
\end{minipage}
\vspace{13mm}
\end{titlepage}
\begin{abstract}
'''
abstract=re.search(r'\\begin\{abstract\}([\s\S]*?)\\end\{abstract\}',E)[1]
preamble+=abstract+r'''\end{abstract}
\noindent This edition integrates the expanded mathematical narrative with the canonical v1.2.1 certificate-level formulations.  It preserves the distinction between general written proofs, formal specifications, and finite computational examples.  A separate visual guide and a Lean guide provide worked models and the complete formal-contract crosswalk.
\tableofcontents\listoffigures\listoftables\clearpage
'''
final=preamble+body+r'\bibliographystyle{plain}\bibliography{references}'+'\n\\end{document}\n'
(R/'Paper_II_Traditional_Final.tex').write_text(final)
(R/'EDITORIAL_CHANGES.json').write_text(json.dumps({'schema':'komorebi.paper_ii.editorial.v1','author':'Komorebi P.','source_sources':['source/canonical.tex','source/expanded.tex'],'changes':changes,'proof_policy':'Inherited proof bodies retained where selected; local statement hypotheses corrected with explicit audit. No new Lean coverage.'},ensure_ascii=False,indent=2)+'\n')
required=['def:refinement-map','def:coordinate-refinement','thm:nested-refinement','prop:perfect-reconstruction','thm:transfer-block-refinement','prop:residue-algebra','thm:root-of-unity','thm:polyphase-refinement','thm:dyadic-odd','thm:weighted-inverse','cor:finite-precision','thm:transfer-zeta','cor:zeta-recurrence','thm:bezout-projector','def:separation-weight','thm:precision-delay','prop:dyadic-sign','thm:smith-solve','thm:power-defect','cor:defect-norm','thm:resolvent-defect','sec:smith-realization','eq:smith-inversion','alg:residue','alg:weighted-inverse','alg:path-zeta']
cross={k:{'final_label':aliases.get(k,k),'number':None,'page':None,'relation':'shared expanded statement; see scope notes' if k in aliases else 'canonical source retained in integrated topic'} for k in required}
cross['thm:nested-refinement']['relation']='Expanded parent-child/transitivity theorem plus adjacent unique child reconstruction paragraph and exact coordinate coherence; canonical uniqueness clause retained as explanation.'
for k,v in json.loads((R/'anchor_relations.json').read_text()).items(): cross[k]['relation']=v
(R/'canonical_label_to_final.json').write_text(json.dumps(cross,indent=2)+'\n')
print('Prepared final TeX',len(final),'bytes; edits',len(changes))
