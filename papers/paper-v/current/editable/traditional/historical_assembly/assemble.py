#!/usr/bin/env python3
"""Portable faithful two-part assembly with an explicit change ledger."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parent
core=(R/'source/formal_core.tex').read_text(); ext=(R/'source/annals_extension.tex').read_text()
changes=[]
def edit(t,old,new,reason,part,kind='editorial',n=1):
 assert t.count(old)==n,(part,old,t.count(old),n)
 changes.append(dict(part=part,kind=kind,old=old,new=new,reason=reason,occurrences=n))
 return t.replace(old,new)
def ce(old,new,reason,kind='editorial',n=1):
 global core
 core=edit(core,old,new,reason,'I',kind,n)
def ee(old,new,reason,kind='mathematical-scope-repair',n=1):
 global ext
 ext=edit(ext,old,new,reason,'II',kind,n)
# Current edition and inherited-evidence language; mathematical core preserved.
ce('In the remaining case,  For any competing pruning','In the remaining case, for any competing pruning','Uniquely forced capitalization/punctuation in result14 proof.','routine-proof-prose')
ce('The revised edition integrates a Lean formalization','The preserved September 2026 release integrates a Lean formalization','Attribute inherited formal evidence to its release.')
ce('The numerical experiments have been rerun for this edition.','The September 2026 release records a rerun of the numerical experiments. The current final-edition checks are distinguished in the opening reading note.','Separate historical execution from current checks.')
ce('The original companion source has been recovered and rerun. Its 33 tests pass, and all 18 figure pairs and numerical tables have been regenerated.','The September 2026 release records recovery and rerunning of the original companion source: its 33 tests passed, and all 18 figure pairs and numerical tables were regenerated.','Date inherited test and numerical evidence.')
ce('This edition has twenty theorem-like statements:','The preserved Part I manuscript has twenty theorem-like statements:','Coverage denominator applies only to the formal core.')
ce('A fresh build and axiom audit accepted the project with warnings treated as errors.','The September 2026 release records a successful build and axiom audit with warnings treated as errors. No fresh Lean build is asserted for this October final edition.','Avoid presenting historical kernel evidence as current execution.')
ce('All scalar entries in the recovered numerical-results JSON reproduced exactly in this environment.','The September 2026 record states that all scalar entries in the recovered numerical-results JSON reproduced exactly in its environment.','Date inherited reproducibility wording.')
ce('In the present container, a disclosed runtime adapter was needed','In the September 2026 release environment, a disclosed runtime adapter was needed','Date the inherited runtime workaround.')
ce('only Paper V was freshly built for this edition.','only Paper V was freshly built for that September 2026 release. These historical cross-paper counts are not a current census of the October final companions.','Prevent stale cross-paper counts from being mistaken for current totals.')
ce('The finite theorem scope is complete in the stated sense: all twenty theorem-like statements have reviewed, accepted formal counterparts, and the numerical companion has been rerun.','The September 2026 finite theorem scope is complete in the stated sense: all twenty theorem-like statements have reviewed, accepted formal counterparts, and that release records a rerun of the numerical companion.','Restrict completion assertion to preserved core formal contract.')
ce('If a noise model supplies \\emph{all} local bounds simultaneously on one event of probability at least $1-\\delta$,','Assume the random node costs and the joint local-error event are measurable. If a noise model supplies \\emph{all} local bounds simultaneously on one event of probability at least $1-\\delta$,','Make ordinary-probability hypothesis explicit; existing Lean interface supplies outer-measure monotonicity.','mathematical-scope-repair')
ce('The joint local-error event is contained in the selector-preservation event, so monotonicity of probability proves the probabilistic assertion.','The finite deterministic comparisons defining the selector make its preservation event measurable when the random node costs are measurable. The joint local-error event is contained in the selector-preservation event, so monotonicity of probability proves the probabilistic assertion.','Connect measurable random costs to selector-preservation event before probability monotonicity.','mathematical-proof-clarification')
ce('\\subsection{Executed checks and numerical conventions}','\\subsection{September 2026 checks and numerical conventions}','Label historical test counts at the point of use.')
ce('the expanded PDF and its TeX are the current manuscript.','the expanded PDF and its TeX are the manuscript of that September 2026 release.','Avoid confusing the historical source PDF with the final reading edition.')
ce('From the release root, the combined verification entry point is:','From the preserved release root (\\texttt{source/complete/original\\_snapshot} in the final package), the combined verification entry point is:','Give the actual packaged working directory for the inherited verifier.')
# Documented Part II substantive audit repairs.
ee('a bounded approximation operator acting on the smooth part','a bounded linear approximation operator acting on the smooth part','Estimated-packet splitting requires linearity (audit A).')
ee('let \\(Q:X\\to X\\) be bounded.','let \\(Q:X\\to X\\) be bounded and linear.','Declare common bounded linear operator convention (audit A).')
ee('Let \\(f=s+j\\), let \\(\\widehat j\\) be an estimated packet, and define','Let \\(Q_m:X\\to X\\) be linear, let \\(f=s+j\\), let \\(\\widehat j\\) be an estimated packet, and define','Add missing linearity before using Q_m additivity (audit A).')
ee('If \\(Q_m\\) is bounded and','If \\(Q_m\\) is bounded and linear and','Propagate operator hypothesis to reconstruction after detection (audit A).')
ee('Let \\(Q_m\\) be uniformly bounded on \\(L^p\\), with','Let \\(Q_m\\) be linear and uniformly bounded on \\(L^p\\), with','Propagate linearity to estimated Gibbs bound (audit A).')
ee('Suppose every internal node has an analysis map \\(U_v\\) satisfying','Suppose every internal node has an analysis map \\(U_v\\) and constants \\(0\\leq A_v\\leq B_v<\\infty\\) satisfying','Nonnegative local bounds required by recursive multiplication (audit B).')
ee('In the Haar subsections the signal is defined on \\(\\RR\\), or a fixed extension beyond the endpoints of a finite observation interval has been chosen, so every displayed wavelet support is available.','In the Haar subsections the signal is defined on \\(\\RR\\). Here the step convention is \\(H_\\tau(t)=\\one_{[\\tau,\\infty)}(t)\\), whose restriction to \\((0,1)\\) agrees with the preceding interval step. A chosen extension beyond the observation interval must use this half-line step convention, and the smooth extension must satisfy the stated Lipschitz hypothesis on every displayed wavelet support.','Remove the artificial endpoint jump from Haar formulas (audit C).')
ee('If \\(\\Gamma\\) has a linear tube bound, then for \\(1\\leq p<\\infty\\),','If \\(\\Gamma\\) has a linear tube bound and \\(0<\\delta<\\delta_0\\) lies in its stated range, then for \\(1\\leq p<\\infty\\),','Restrict use of tube bound to its hypothesis range (audit D).')
ee('The finite \\(L^p\\) packet error converges to zero.','For the fixed finite jump model above, along grids satisfying the preceding sampling assumptions, the packet error converges to zero in probability in every finite \\(L^p\\) norm.','Specify probabilistic convergence and inherited sampling model (audit E,F).')
ee('Then \\(b_{h,\\delta}\\to0\\). Apply \\cref{thm:probability_recovery,cor:reconstruction_after_detection}.','For each fixed \\(\\delta>0\\), \\(b_{h,\\delta}\\to0\\). Apply \\cref{thm:probability_recovery,cor:reconstruction_after_detection}. For any error tolerance \\(\\epsilon>0\\), the high-probability bound is eventually smaller than \\(\\epsilon\\), so the limit superior of the probability that the packet error exceeds \\(\\epsilon\\) is at most \\(\\delta\\). Since \\(\\delta\\) is arbitrary, convergence is in probability.','Complete the explicitly stated convergence-in-probability argument (audit E).')
ee('where \\(s\\) is Lipschitz with constant \\(M\\). Suppose no jump lies at a sample point','where \\(s\\) is Lipschitz with constant \\(M\\), and \\(Q\\geq1\\) is finite with nonzero jump amplitudes. The zero-jump case requires no minimum-amplitude condition. Suppose no jump lies at a sample point','Make finite nonempty jump model explicit where a minimum amplitude is used (audit F).')
ee('Assume \\(h\\to0\\), \\(\\varepsilon_h\\to0\\), the number of jumps is fixed, and the jump amplitudes and minimum separation remain fixed.','Assume \\(h\\to0\\) along grids satisfying the preceding sampling assumptions, \\(\\varepsilon_h\\to0\\), the number of jumps is fixed, and the nonzero jump amplitudes and positive minimum separation remain fixed.','Keep consistency within the declared sampling hypotheses (audit F).')
ee('For every fixed \\(0<\\delta<1\\), all jump cells are recovered','For every fixed \\(0<\\delta<1\\), along grids satisfying the preceding sampling assumptions, all jump cells are recovered','Propagate admissible-grid condition to probability recovery sequence (audit F).')
ee('A minimizing pruning is recovered by retaining \\(v\\) when the first term is smaller and splitting it when the second term is smaller.','A minimizing pruning is recovered by retaining \\(v\\) when the first term is no larger than the second and splitting it otherwise.','Specify deterministic stop-on-ties policy (audit G).')
ee('This gives the recursion and the reconstruction rule.','This gives the recursion and the reconstruction rule. In an equality case both choices minimize, and the stated rule retains the node.','Check tie branch in best-basis proof (audit G).')
ee('Assume the optimal pruning for \\(c\\) is unique. Let \\(g>0\\) be the difference between its cost and the second smallest admissible cost.','Assume the optimal pruning \\(\\Lcal_*\\) for \\(c\\) is unique and at least one competing pruning exists. Define \\(g=\\min_{\\Lcal\\ne\\Lcal_*}(C(\\Lcal)-C(\\Lcal_*))>0\\).','Exclude empty competitor minimum and fix sign of optimality gap (audit G).')
ee('then the optimal pruning for \\(\\widetilde c\\) is the same.','then the optimal pruning for \\(\\widetilde c\\) is the same. If only one admissible pruning exists, it remains selected under every cost change without a gap condition.','State singleton case separately (audit G).')
ee('Suppose \\(R\\) independent observations are averaged at every sample location, with each individual noise variable centered and \\(\\sigma\\) sub Gaussian.','Suppose \\(R\\) observations are averaged at every sample location, with all noise variables independent across sites and repetitions and each centered and \\(\\sigma\\) sub Gaussian.','Make independence inheritance explicit (audit H).')
ee('The bank reconstructs every input with delay \\(d\\) exactly if and only if','The bank reconstructs every input with a delay of \\(d\\) coarse channel samples, equivalent to \\(Nd\\) original samples in the one dimensional \\(N\\)-phase convention, exactly if and only if','Align delay convention with corrected formal core (audit I).')
ee('At an isolated jump of size \\(a\\), ordinary Fourier partial sums','For a periodic piecewise \\(C^1\\) function with an isolated jump of size \\(a\\), ordinary Fourier partial sums','Supply sufficient regularity for imported Gibbs fact (audit J).')
ee('The difference \\(\\eta_{k+1}-\\eta_k\\) is sub Gaussian with variance proxy \\(2\\sigma^2\\), so','If \\(\\sigma=0\\), every centered zero-sub-Gaussian noise variable vanishes almost surely, and the noise-free deterministic conclusion applies. For \\(\\sigma>0\\), the difference \\(\\eta_{k+1}-\\eta_k\\) is sub Gaussian with variance proxy \\(2\\sigma^2\\), so','Handle degenerate variance before dividing by sigma squared (audit K).')
ee('With one observation at each grid point and fixed noise scale, the maximum noise contrast grows slowly with \\(n\\). Consistency therefore requires decreasing noise, repeated measurements, or a multiscale averaging rule. The theorem states this limitation explicitly.','The displayed uniform noise certificate scales as \\(\\sigma\\sqrt{\\log n}\\). At fixed positive \\(\\sigma\\), it does not imply consistency of this detector. Decreasing the noise scale or averaging repeated measurements gives sufficient regimes; other averaging schemes require their own analysis.','Distinguish a growing certificate from an unsupported universal claim about actual maxima (audit L).')
ee('When \\(G=\\ZZ^d\\), translation','For an integer \\(d\\geq1\\), when \\(G=\\ZZ^d\\), translation','Specify positive lattice dimension for proper c0 inclusion.')
ee('For \\(L=N\\ZZ\\), define','For \\(L=N\\ZZ\\) with \\(N\\geq1\\), first take \\(|z|=1\\). The assumption \\(h\\in\\ell^1(\\ZZ)\\) makes the following symbol series absolutely convergent. Define','State symbol domain for infinite convolution kernels.')
ee('If \\(\\bm X(z)\\) and \\(\\bm Y(z)\\) are the channel transforms, then','For \\(x\\in\\ell^1(\\ZZ)\\), the channel transforms converge absolutely on the unit circle and satisfy','Restrict literal transform sums to absolute convergence domain.')
ee('This is the classical polyphase matrix. It is the exact block matrix of the original convolution operator.','For \\(x\\in\\ell^2(\\ZZ)\\), the same identity holds almost everywhere in the \\(L^2\\) Fourier sense. For finite impulse-response kernels it also holds at nonzero \\(z\\) wherever the input channel transforms are weighted absolutely summable. This is the classical polyphase matrix. It is the exact block matrix of the original convolution operator.','Separate algebraic FIR, absolutely convergent transforms, and L2 Fourier statements.')
ee('For \\(\\theta=2\\pi/N\\), the map has order \\(N\\).','For an integer \\(N\\geq1\\) and \\(\\theta=2\\pi/N\\), the map has order \\(N\\).','Specify positive integer cyclic order.')
ee('When \\(\\theta=2\\pi/N\\), the \\(N\\)th power is the identity.','When \\(\\theta=2\\pi/N\\), the \\(N\\)th power is the identity. Conversely, if its \\(k\\)th power is the identity, conjugation by \\(C\\) and evaluation at \\(w=1/2\\) give \\(\\e^{2\\pi\\ii k/N}=1\\), so \\(N\\) divides \\(k\\). Hence the order is exactly \\(N\\).','Complete exact-order argument, beyond order dividing N.')
ee('\\bigl(s(t)-s(t+L/2)\\bigr)\\dd t.','\\overline{s(t)-s(t+L/2)}\\,\\dd t.','Match core convention: inner product conjugate-linear in the first argument.')
ee('Let \\(h\\in\\ell^1(\\ZZ^d)\\) and define','Let \\(h\\in\\ell^1(\\ZZ^d)\\) and \\(x\\in\\ell^p(\\ZZ^d)\\), with \\(1\\leq p\\leq\\infty\\), and define','State convolution input domain; bounded sequence makes ell1 convolution pointwise absolute.')
ee('and an integer \\(Q\\). The class','and an integer \\(Q\\geq0\\). The class','Permit empty trace-packet class and rule out negative packet count.')
ee('Let \\(H_\\tau=\\one_{[\\tau,1]}\\). For \\(1\\leq p<\\infty\\),','Let \\(0\\leq\\tau,\\widehat\\tau\\leq1\\) and \\(H_\\tau=\\one_{[\\tau,1]}\\). For \\(1\\leq p<\\infty\\),','Keep step location-error formula within declared observation interval.')
bib=(R/'source/annals.bib').read_text()
old='David Gottlieb and Chi Wai Shu';new='David Gottlieb and Chi-Wang Shu'
assert old in bib
(R/'references.bib').write_text(bib.replace(old,new))
changes.append(dict(part='II',kind='bibliographic',old=old,new=new,reason='Primary SIAM publisher metadata confirms Chi-Wang Shu, DOI10.1137/S0036144596301390.',occurrences=1))
# Store corrected branch sources for transparent proof comparison, before anchors/typesetting.
(R/'core_corrected.tex').write_text(core);(R/'extension_corrected.tex').write_text(ext)
# Main preamble adopts the final-series geometry and style.
preamble=core.split('\\begin{document}',1)[0]
preamble=preamble.replace('\\documentclass[11pt]{article}','\\documentclass[11pt,a4paper]{article}')
preamble=preamble.replace('\\usepackage[margin=0.90in]{geometry}',r'\usepackage[a4paper,margin=23mm,includeheadfoot,headheight=15pt,headsep=15pt,footskip=22pt]{geometry}'+'\n'+r'\usepackage{setspace,titlesec,etoolbox,tocloft}')
preamble=preamble.replace('\\usepackage{microtype}',r'\usepackage[nopatch=footnote]{microtype}')
preamble=preamble.replace('\\usepackage[nameinlink,noabbrev]{cleveref}',r'\usepackage[nameinlink,noabbrev]{cleveref}'+'\n'+r'\usepackage{bookmark}')
preamble=preamble.replace('\\graphicspath{{figures/}}','\\graphicspath{{core_figures/}}')
preamble=preamble.replace('\\fancyhead[L]{Projector-Resolved Seed Calculus V}\n\\fancyhead[R]{Komorebi P.}\n\\fancyfoot[C]{\\thepage}\n\\setlength{\\headheight}{14pt}',r'''\fancyhead[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}KOMOREBI MATHEMATICS / PAPER V}
\fancyhead[R]{\sffamily\fontsize{8}{10}\selectfont\color{muted}TRADITIONAL PAPER}
\fancyfoot[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}Multiresolution signal calculus}
\fancyfoot[R]{\sffamily\small\color{accent}\thepage}''')
preamble+='\n'+r'''\definecolor{accent}{HTML}{137668}
\definecolor{muted}{HTML}{536568}
\hypersetup{linkcolor=accent,citecolor=accent,urlcolor=accent}
\frenchspacing\clubpenalty=10000\widowpenalty=10000\raggedbottom
\titleformat{\section}{\sffamily\bfseries\large\color{accent}}{\thesection}{.7em}{}
\titleformat{\subsection}{\sffamily\bfseries\normalsize}{\thesubsection}{.7em}{}
\titlespacing*{\section}{0pt}{1.4\baselineskip}{.55\baselineskip}
\pretocmd{\section}{\Needspace{7\baselineskip}}{}{}
\pretocmd{\subsection}{\Needspace{5\baselineskip}}{}{}
\setstretch{1.055}\setlength{\parskip}{.3em}\setlength{\parindent}{1.35em}
\setlength{\emergencystretch}{3em}
\setlength{\cftsecnumwidth}{2.5em}
\setlength{\cftsubsecindent}{2.5em}
\setlength{\cftsubsecnumwidth}{3.4em}
\newtheorem{standardfact}[theorem]{Standard Fact}
\crefname{standardfact}{standard fact}{standard facts}
\crefname{classical}{classical input}{classical inputs}
\crefname{boundary}{boundary}{boundaries}
\crefname{certificate}{numerical certificate}{numerical certificates}
'''
# Preserve extension-only macros, skipping identical already-defined aliases.
for line in ext.split('\\begin{document}',1)[0].splitlines():
 if line.startswith('\\newcommand'):
  name=re.match(r'\\newcommand\{(\\[^}]+)\}',line)[1]
  if not re.search(r'\\newcommand\{'+re.escape(name)+r'\}',preamble):preamble+=line+'\n'
core_body=core.split('\\begin{document}',1)[1].rsplit('\\end{document}',1)[0]
core_body=core_body.replace('\\maketitle','',1)
core_body=core_body.replace('\\tableofcontents\n\\listoffigures\n\\listoftables\n\\clearpage','',1)
ext_body=ext.split('\\begin{document}',1)[1].rsplit('\\end{document}',1)[0]
ext_body=ext_body.replace('\\maketitle\n\\thispagestyle{plain}','',1)
ext_body=ext_body.replace('\\bibliographystyle{aomalpha}','\\bibliographystyle{alpha}').replace('\\bibliography{PSC_Paper_V_Annals_Human_Edition}','\\bibliography{references}')
# Inject invisible locator labels only where the source has none.
anchors=[]
record_re=r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|remark|boundary|standardfact|classical|conjecture|certificate)\}(?:\[[\s\S]*?\])?'
def anchor_body(t,part):
 n=0
 def record(m):
  nonlocal n;n+=1
  after=t[m.end():m.end()+180]
  if re.match(r'\s*\\label\{',after):return m.group()
  label=f'{part}:record:{n:02}'
  anchors.append({'label':label,'part':part,'type':'record','ordinal':n})
  return m.group()+'\\label{'+label+'}'
 t=re.sub(record_re,record,t)
 section_n=0
 def section(m):
  nonlocal section_n;section_n+=1
  label=f'{part}:section:{section_n:02}'
  anchors.append({'label':label,'part':part,'type':'section','ordinal':section_n,'title_tex':m[1]})
  return m.group()+'\\label{'+label+'}'
 t=re.sub(r'\\section\{([^{}]*)\}',section,t)
 return t
core_body=anchor_body(core_body,'core');ext_body=anchor_body(ext_body,'extension')
cover=r'''\begin{document}
\begin{titlepage}\thispagestyle{empty}
\vspace*{13mm}
{\sffamily\bfseries\color{accent}\large KOMOREBI MATHEMATICS\quad /\quad PAPER V\par}
\vspace{12mm}
{\sffamily\bfseries\fontsize{29}{34}\selectfont Multiresolution\\Signal Calculus\par}
\vspace{8mm}
{\sffamily\fontsize{18}{23}\selectfont Exact Coordinates, Singular Packets,\\and Stable Reconstruction\par}
\vspace{12mm}{\large Komorebi P.\par}
\vspace{5mm}{\sffamily\color{muted}Traditional final edition\quad\textbullet\quad 5 October 2026\par}
\vfill
\noindent\begin{minipage}{.94\linewidth}
\textbf{Part I.} The full twenty-result formal core: polyphase reconstruction, filter transfers, Hilbert packet operators, finite adaptive trees, edge error bounds, and Smith coordinates.

\medskip
\textbf{Part II.} The complete extended mathematical development: lattice coordinates, stable banks, singular packets, separated-jump recovery, geometric error bounds, and multiscale localization.

\medskip
\textbf{Companions.} A visual guide develops exact worked models. A Lean guide explains the released formal scope and its relation to both parts.
\end{minipage}
\vspace{13mm}\end{titlepage}
\section*{Reading this edition}\addcontentsline{toc}{section}{Reading this edition}
This edition brings together two substantial branches of Paper V without conflating their evidence. Part I preserves the later v1.1.0 manuscript, including its twenty scoped results and their twenty proofs. Part II preserves the broader standalone development, with sixty-three proofs, under section numbers prefixed by E. Their overlap is intentional: Part I is the exact released formal contract, while Part II develops more general mathematical statements. The combined eighty-three proof environments are not a count of eighty-three independent or novel results.

The inherited September 2026 release records 225 Lean theorem targets across 23 proof modules supporting all twenty Part I results. That formal coverage does not extend automatically to Part II. No fresh Lean compilation was possible for this final edition. Part II has been reviewed as mathematical prose; the audit repairs missing hypotheses, transform and inner-product conventions, degenerate cases, and several proof details. Original sources and an exact change ledger accompany this edition.

The current checks reran twenty exact-model tests containing 305,933 assertions and sixteen verifier controls. The extended finite suite passed 11,052 checks across thirteen groups. Fifty-two stored numerical metrics reproduced exactly, and eighteen core figure pairs were regenerated. These finite checks have separate scopes and are not universal proofs. The original pytest suites and the separate visual-guide SymPy checks were not rerun. Historical counts in Part I's reproducibility appendix retain their September 2026 provenance.

For a first reading, follow Part I Sections 1--7, then its adaptive-tree and Smith-coordinate sections. Continue with Part II Sections E2--E6 for lattice and operator generalizations, E7--E11 for singular packets and recovery, and E12--E14 for nonlinear and Cayley realizations. The original Part I numbering is retained so the formal scope map remains directly usable. Part II theorem numbers and every original source label are mapped in the companion files.

Part I's open edge-recovery conjectures remain visible in their source form. Part II supplies recovery theorems for a declared one-dimensional separated-jump class; it does not settle universal image segmentation, infinite-tree consistency, or the broad recovery conjectures. Existing numerical figures are retained with their stated finite interpretation.
\clearpage
\tableofcontents
\clearpage
\listoffigures
\listoftables
\clearpage
\part*{Part I\quad The released formal core}\addcontentsline{toc}{part}{Part I: The released formal core}
\begin{center}\large Projector-Resolved Seed Calculus V\par\normalsize Polyphase Signal Calculus: Exact Reconstruction, Edge Packets, Wavelets, and Smith Coordinates\end{center}
'''
separator=r'''\clearpage
\part*{Part II\quad Extended mathematical development}\addcontentsline{toc}{part}{Part II: Extended mathematical development}
\begin{center}\large Multiresolution Signal Calculus, Singular Packets, and Stable Reconstruction\end{center}
\noindent This part preserves the complete standalone mathematical branch, with the explicit audit repairs recorded in the accompanying source ledger. Its sixty-three proofs are prose proofs; no additional Lean coverage is asserted. Section and result numbers carry the prefix E to distinguish this scope from Part I.
\setcounter{section}{0}\setcounter{figure}{0}\setcounter{table}{0}
\renewcommand{\thesection}{E\arabic{section}}
\renewcommand{\theHsection}{extension.\arabic{section}}
\renewcommand{\thefigure}{E\arabic{figure}}
\renewcommand{\theHfigure}{extension.\arabic{figure}}
\renewcommand{\thetable}{E\arabic{table}}
\renewcommand{\theHtable}{extension.\arabic{table}}
\graphicspath{{extension_figures/}}
'''
final=preamble+cover+core_body+separator+ext_body+'\n\\end{document}\n'
(R/'Paper_V_Traditional_Final.tex').write_text(final)
(R/'EDITORIAL_CHANGES.json').write_text(json.dumps({'schema':'komorebi.paper_v.traditional_changes.v1','changes':changes,'invisible_locator_labels':anchors},indent=2)+'\n')
print(f'Assembled {len(final)} characters; {len(changes)} documented changes, {len(anchors)} locator anchors.')
