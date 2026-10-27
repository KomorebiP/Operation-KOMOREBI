#!/usr/bin/env python3
"""Reconcile three paper branches and receive the operator section migrated from IV."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parent
core=(R/'source/formal_core.tex').read_text();status=(R/'source/lean_status.tex').read_text();ext=(R/'source/strengthened.tex').read_text();old=(R/'source/earlier_annals.tex').read_text();migration=(R/'source/paper_iv_operator_substitution.tex').read_text();changes=[]
def edit(t,a,b,reason,part,kind='editorial'):
 assert t.count(a)==1,(part,a,t.count(a));changes.append(dict(part=part,kind=kind,old=a,new=b,reason=reason));return t.replace(a,b)
def ce(a,b,reason,kind='editorial'):
 global core;core=edit(core,a,b,reason,'I',kind)
def ee(a,b,reason,kind='mathematical-scope-repair'):
 global ext;ext=edit(ext,a,b,reason,'II',kind)
ce('are summable.  If the tower has a uniform gap $m>0$, it is enough that $\\sum_\\ell\\norm{D_\\ell}<\\infty$.  On every bounded time interval, the corresponding fractional-semigroup defects are summable as well.','have summable operator norms. If the tower has a uniform gap $m>0$, it is enough that $\\sum_\\ell\\norm{D_\\ell}<\\infty$. On every bounded time interval, the series of corresponding fractional-semigroup defect norms converges uniformly. The maps may have different domain and codomain spaces; no operator sum across unrelated spaces is asserted.','Disambiguate varying-space summability, matching RectangularTowers formal contract.','mathematical-scope-clarification')
ce('The complete release passes','The September 6 release records the following automated-test result:','Date the retained numerical certificate locally.')
ce('Five checked Lean blocks cover all 33 theorem-like results in Appendix~\\ref{sec:lean-status}.','The inherited September 6 release records five checked Lean blocks covering all 33 scoped theorem-like results in Appendix~\\ref{sec:lean-status}.','Date inherited formal evidence.')
status=edit(status,'The full\nbuild and namespace audit pass with Lean 4.34.0-rc2 and pinned mathlib.','The September 6 release records a successful full\nbuild and namespace audit with Lean 4.34.0-rc2 and pinned mathlib.','Date inherited compiler execution.','I appendix')
status=edit(status,'The full pinned build, project-wide axiom audit, all 54 companion tests and six\nverifier controls pass.','The September 6 release records that the full pinned build, project-wide axiom audit, all 54 companion tests and six\nverifier controls passed. No fresh Lean build is asserted for this October edition.','Separate historical compiler/test evidence from current checks.','I appendix')
status=edit(status,'not a rerun in this\nblock.','not a rerun in that September 6\nblock. The September 12 visual release subsequently records a numerical replay; current October checks are reported separately in the final package.','Attribute numerical history precisely.','I appendix')
# Audit corrections to the broader branch are explicit and reproducible.
ee('Assume \\(x_Q(0)=0\\). The following conditions are equivalent.','Assume \\(x_Q(0)=0\\) and \\(d=\\dim X_Q<\\infty\\). The following conditions are equivalent.','Finite Cayley--Hamilton moment criterion requires a finite hidden space.')
ee('If\n\\[\n\\norm{\\e^{tA_{QQ}}}\n\\leq\nM\\e^{-\\gamma t},\n\\]\nthen','If, for constants \\(M\\geq0\\) and \\(\\gamma>0\\),\n\\[\n\\norm{\\e^{tA_{QQ}}}\n\\leq\nM\\e^{-\\gamma t},\n\\]\nthen','Positive decay rate required for the L1 bound.')
# Additional exact audit edits are read from a small checked local ledger.
for x in json.loads((R/'additional_edits.json').read_text()) if (R/'additional_edits.json').exists() else []:
 if x['part']=='II':ee(x['old'],x['new'],x['reason'],x.get('kind','mathematical-scope-repair'))
 elif x['part']=='III':old=edit(old,x['old'],x['new'],x['reason'],'III',x.get('kind','mathematical-scope-repair'))
 elif x['part']=='IV migration':migration=edit(migration,x['old'],x['new'],x['reason'],'IV migration',x.get('kind','mathematical-scope-repair'))
# Corrected branches remain inspectable before typesetting and locator changes.
for name,t in [('core_corrected.tex',core),('lean_status_corrected.tex',status),('extension_corrected.tex',ext),('earlier_corrected.tex',old),('migration_corrected.tex',migration)]: (R/name).write_text(t)
core=core.replace('\\input{lean_status.tex}',status)
preamble=core.split('\\begin{document}',1)[0]
preamble=preamble.replace('\\documentclass[11pt]{article}','\\documentclass[11pt,a4paper]{article}')
preamble=preamble.replace('\\usepackage[margin=0.90in]{geometry}',r'\usepackage[a4paper,margin=23mm,includeheadfoot,headheight=15pt,headsep=15pt,footskip=22pt]{geometry}'+'\n'+r'\usepackage{setspace,titlesec,etoolbox,tocloft,bookmark}')
preamble=preamble.replace('\\graphicspath{{figures/}}','\\graphicspath{{core_figures/}}')
preamble=preamble.replace('\\fancyhead[L]{Projector-Resolved Seed Calculus VI}\n\\fancyhead[R]{Komorebi P.}\n\\fancyfoot[C]{\\thepage}\n\\setlength{\\headheight}{14pt}',r'''\fancyhead[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}KOMOREBI MATHEMATICS / PAPER VI}
\fancyhead[R]{\sffamily\fontsize{8}{10}\selectfont\color{muted}TRADITIONAL PAPER}
\fancyfoot[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}Transfer semigroups and memory}
\fancyfoot[R]{\sffamily\small\color{accent}\thepage}''')
preamble+='\n'+r'''\definecolor{accent}{HTML}{137668}
\definecolor{muted}{HTML}{536568}
\hypersetup{linkcolor=accent,citecolor=accent,urlcolor=accent,pdftitle={Komorebi Paper VI: Transfer Semigroups and Memory},pdfauthor={Komorebi P.}}
\frenchspacing\clubpenalty=10000\widowpenalty=10000\raggedbottom
\titleformat{\section}{\sffamily\bfseries\large\color{accent}}{\thesection}{.7em}{}
\titleformat{\subsection}{\sffamily\bfseries\normalsize}{\thesubsection}{.7em}{}
\titlespacing*{\section}{0pt}{1.4\baselineskip}{.55\baselineskip}
\pretocmd{\section}{\Needspace{7\baselineskip}}{}{}
\pretocmd{\subsection}{\Needspace{5\baselineskip}}{}{}
\setstretch{1.045}\setlength{\parskip}{.3em}\setlength{\parindent}{1.35em}
\setlength{\emergencystretch}{3em}
\setlength{\cftsecnumwidth}{2.5em}
\setlength{\cftsubsecindent}{2.5em}
\setlength{\cftsubsecnumwidth}{3.4em}
\newtheorem{standardfact}[theorem]{Standard Fact}
\crefname{standardfact}{standard fact}{standard facts}
\crefname{classical}{classical input}{classical inputs}
\crefname{boundary}{boundary}{boundaries}
\crefname{certificate}{numerical certificate}{numerical certificates}
\newcommand{\Dfun}{\mathsf D}
\newcommand{\Sfun}{\mathsf S}
'''
for src in [ext,old]:
 for line in src.split('\\begin{document}',1)[0].splitlines():
  if line.startswith('\\newcommand'):
   name=re.match(r'\\newcommand\{(\\[^}]+)\}',line)[1]
   if not re.search(r'\\newcommand\{'+re.escape(name)+r'\}',preamble):preamble+=line+'\n'
# Source labels are namespaced; invisible anchors make every unlabeled record navigable.
anchors=[]
def namespace(t,prefix):
 def refs(m):return m[1]+'{'+','.join(prefix+':'+x for x in m[2].split(','))+'}'
 return re.sub(r'(\\(?:label|ref|pageref|eqref|cref|Cref))\{([^}]+)\}',refs,t)
def anchor(t,prefix):
 n=0
 def rec(m):
  nonlocal n;n+=1
  label=f'{prefix}:record:{n:03}'
  anchors.append(dict(label=label,part=prefix,type='record',ordinal=n));return m.group()+'\\label{'+label+'}'
 t=re.sub(r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|remark|boundary|standardfact|classical|conjecture|certificate|construction)\}(?:\[[\s\S]*?\])?',rec,t)
 n=0
 def sec(m):
  nonlocal n;n+=1;label=f'{prefix}:section:{n:02}';anchors.append(dict(label=label,part=prefix,type='section',ordinal=n,title_tex=m[1]));return m.group()+'\\label{'+label+'}'
 return re.sub(r'\\section\{([^{}]*)\}',sec,t)
corebody=core.split('\\begin{document}',1)[1].rsplit('\\end{document}',1)[0].replace('\\maketitle','',1)
corebody=corebody.replace('\\tableofcontents\n\\begingroup\n\\small\n\\listoffigures\n\\listoftables\n\\endgroup\n\\clearpage','',1)
extbody=ext.split('\\begin{document}',1)[1].rsplit('\\end{document}',1)[0].replace('\\maketitle\n\\thispagestyle{plain}','',1)
extbody=extbody.replace('\\bibliographystyle{aomalpha}\n\\bibliography{PSC_Paper_VI_Strengthened_Annals_Edition}','')
corebody=anchor(namespace(corebody,'core'),'core');extbody=anchor(namespace(extbody,'extended'),'extended')
# The earlier human edition contains results whose hypotheses or conclusions are
# distinct from both later branches. Preserve complete statements and proofs.
selected=[]
def extract(label,proof=True):
 i=old.index('\\label{'+label+'}');start=old.rfind('\\begin{',0,i)
 if proof:end=old.index('\\end{proof}',i)+len('\\end{proof}')
 else:
  env=re.match(r'\\begin\{([^}]+)\}',old[start:])[1];end=old.index('\\end{'+env+'}',i)+len('\\end{'+env+'}')
 selected.append(label);return old[start:end]+'\n\n'
def records(labels):return ''.join(extract(x) for x in labels)
supp=r'''\section{Transfer paths and product-topology limits}
Let $T(t)$ be an arbitrary strongly continuous semigroup on a complex Banach space $X$, with generator $A$, and suppose $\norm{T(t)}\leq M e^{\omega t}$ for $M\geq1$ and $\omega\in\mathbb R$. Let $(P_\alpha)_{\alpha\in I_0}$ be a finite family of bounded pairwise orthogonal idempotents summing to $I$, and put $T_{\beta\alpha}(t)=P_\beta T(t)P_\alpha$. The generator need not be bounded. In the following resolvent statement the integral is strong: apply the integrand to each $x\in X$ and take its Bochner integral in $X$. It is not asserted to be a Bochner integral in the operator-norm space $\mathcal B(X)$. The general Laplace formula is \cite[Chapter II, Theorem 1.10]{EngelNagel2000}.
'''+records(['thm:packet_convolution','prop:packet_resolvent'])+r'''
For the path-order statement, now assume $A$ is bounded as in Part II. A directed edge from $\alpha$ to $\beta$ means that $P_\beta A P_\alpha$ is nonzero, with $\alpha\ne\beta$; a packet always has the length-zero path to itself.
'''+records(['cor:minimum_transfer_order'])+r'''
Let $C_j:X_{j+1}\to X_j$ be bounded linear maps, and put $C_{\ell,m}=C_\ell\cdots C_{m-1}$ for $\ell<m$, with $C_{j,j}=I$. No common ambient space is assumed.
'''+records(['thm:multilevel_telescoping','cor:summable_defects'])+extract('def:projective_limit',False)+records(['thm:projective_limit_semigroup','cor:projective_generators'])+r'''
The product topology used here differs from the bounded inverse-limit norm of Part II. No uniform boundedness of coordinate generators is required by the coordinatewise statement.
\section{Reversible coarse dynamics}
Let $Q$ be a finite Markov generator acting on column probability vectors, let $(B_a)$ be a partition into nonempty blocks, and let $C_{ai}=\one_{i\in B_a}$. Strong lumpability means $CQ=\overline Q C$ for a coarse Markov generator. For observables, the backward generator is $Q^T$; weighted $L^2$ inner products use the stated stationary probability.
'''+records(['thm:reversibility_descends','cor:coarse_dirichlet_form'])+r'''
\section{Prior-restricted sufficiency and filtering}
Let $L$ be a strictly positive finite likelihood and let $\Bcal_L(p)=L\odot p/\ip{L}{p}$ for a probability vector $p$. Fix probability vectors $r^{(a)}$ supported on $B_a$, and restrict the priors to $p_i=q_a r_i^{(a)}$ for $i\in B_a$, with $q$ a coarse probability vector.
'''+records(['prop:relative_sufficiency','lem:normalization_bound'])+r'''
For an arbitrary prior $p$, put $q=Cp$ and $Z(p,L)=\ip{L}{p}$. Define $\ell_a(p)=\sum_{i\in B_a}L_ip_i/q_a$ when $q_a>0$; choose any positive value when $q_a=0$. Only the product $q_a\ell_a(p)$ enters the formulas.
'''+records(['thm:information_loss','cor:bayes_oscillation'])+r'''
Along the Bayesian flow $p_i(t)=e^{tg_i}p_i(0)/\sum_j e^{tg_j}p_j(0)$, the following statement holds for every real observable $h$.
'''+records(['cor:bayesian_covariance'])+r'''
For stochastic matrices $K,\overline K$ and positive likelihoods $L_y,\overline L_y$, put $\Phi_y=\Bcal_{L_y}\circ K$ and $\overline\Phi_y=\Bcal_{\overline L_y}\circ\overline K$.
'''+records(['thm:exact_coarse_filter','thm:filter_defect'])+r'''
\section{Fractional modes and killed transfer}
For the one-dimensional Dirichlet difference operator, let $h=1/M$ with an integer $M\geq2$, let $1\leq k\leq M-1$, and set $\lambda_{k,h}=4h^{-2}\sin^2(k\pi h/2)$. The retained explicit coefficient below is valid for every discrete mode.
'''+records(['cor:fractional_low_mode_dispersion'])+r'''

Let $Q$ and $\overline Q$ be finite Markov generators in the column convention. All times in this section satisfy $t\geq0$.
'''+records(['thm:feynman_kac_potential_bound','thm:coarse_feynman_kac'])+r'''
\section{Memory compression, rational realization, and phase-type consequences}
Fix $T>0$. For the next estimate let $A$ be a bounded operator on a Banach space $X$, let $\Kcal,\widetilde\Kcal\in L^1((0,T),\mathcal B(X))$, and let $f$ be continuous. Take continuously differentiable solutions of the displayed equations. This direct bounded-generator estimate retains a sharper exponential constant than the general mild-semigroup estimate in Part II.
'''+records(['thm:memory_compression_stability'])+r'''

For the exact closure criterion of Part II, allowing an arbitrary bounded local generator $B$ does not enlarge the class: differentiating $P e^{tA}P=e^{tB}P$ at $t=0$ forces $B=A_{PP}$ on the retained space. Thus its zero-memory criterion excludes every alternative bounded local generator.

A finite auxiliary realization of a matrix kernel means $\Kcal(t)=B e^{tD}C$, with finite matrices of compatible sizes. Laplace transforms are taken in a right half-plane of absolute convergence. The rational characterization concerns continuous kernels of exponential order, so uniqueness of the ordinary Laplace transform applies.
'''+records(['thm:rational_memory_realization','cor:exponential_sum_memory'])+r'''
For the survival consequences, $A$ is a finite Metzler matrix with nonpositive column sums and spectrum in the open left half-plane, $p_0$ is a probability vector, $S(t)=\one^T e^{tA}p_0$, and $f(t)=-S'(t)$. The one-phase model has $\lambda>0$. The survival Laplace identity of Part II also holds for every complex $s$ with $\operatorname{Re}s\geq0$: stability gives absolute convergence of $\int_0^\infty e^{-st}e^{tA}\,dt=(sI-A)^{-1}$, and multiplying by the exit row and $p_0$ gives the same transform.
'''+records(['cor:phase_type_rationality','cor:one_phase_model'])+r'''
\section{Earlier exact examples}
These five short examples are retained from the earlier human edition. Their numerical parameters are independent of the later visual guide's worked models.
'''+''.join(extract(x,False) for x in ['ex:two_packet_transfer','ex:four_state_lumping','ex:bayes_information_loss','ex:one_hidden_mode','ex:two_phase_survival'])
# All external references from the selected earlier material have explicit current destinations.
refmap=json.loads((R/'EARLIER_RESULT_DESTINATIONS.json').read_text())
def supp_refs(m):
 vals=[]
 for v in m[2].split(','):
  if v in selected:vals.append('earlier:'+v)
  else:
   assert v in refmap,(m.group(),v);vals.append(refmap[v]['final_label'])
 return m[1]+'{'+','.join(vals)+'}'
supp=re.sub(r'(\\(?:ref|pageref|eqref|cref|Cref))\{([^}]+)\}',supp_refs,supp)
supp=re.sub(r'\\label\{([^}]+)\}',lambda m:'\\label{earlier:'+m[1]+'}',supp)
supp=anchor(supp,'earlier')
# Literal migrated section, with its scalar input defined locally.
migration=edit(migration,'The scalar identities have a direct functional calculus form.  This section records only the basic consequence and does not develop an operator resolvent theory.',r'''This section receives the operator-substitution result deliberately moved out of Paper IV. Fix an integer $N\geq1$ and the entire scalar function
\[
\Dfun_N(z)=\sum_{m=0}^{\infty}\frac{(-1)^m z^{Nm}}{(Nm)!}.
\]
More generally, the result applies to any specified holomorphic scalar function that is nonzero on the declared domain. On a simply connected zero-free domain $U$, choose $g=\log\Dfun_N$ once and define $\Sfun_N^{(r)}(z)=\exp(-r g(z))$ for complex $r$. The bounded Banach-space result below uses classical holomorphic functional calculus; it is separate from the finite canonical-jet calculus formalized in Part I.''','Supply scalar family, fixed branch, and explicit migrated scope locally.','IV migration','local-setup')
(R/'migration_corrected.tex').write_text(migration)
migration=namespace(migration,'migration');migration=anchor(migration,'migration')
cover=r'''\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}\thispagestyle{empty}
\vspace*{13mm}
{\sffamily\bfseries\color{accent}\large KOMOREBI MATHEMATICS\quad /\quad PAPER VI\par}
\vspace{12mm}
{\sffamily\bfseries\fontsize{29}{34}\selectfont Transfer Semigroups\\and Memory\par}
\vspace{8mm}
{\sffamily\fontsize{18}{23}\selectfont Probabilistic Refinement, Fractional Operators,\\and Exact Hidden-State Elimination\par}
\vspace{12mm}{\large Komorebi P.\par}
\vspace{5mm}{\sffamily\color{muted}Traditional final edition\quad\textbullet\quad 5 October 2026\par}
\vfill
\noindent\begin{minipage}{.94\linewidth}
\textbf{Part I.} The complete released 33-result formal core, including nonnormal memory and canonical finite holomorphic naturality.

\medskip
\textbf{Part II.} The complete strengthened mathematical development: bounded refinement towers, Bayesian information, Hermite transfer, quantitative memory compression, and competing risks.

\medskip
\textbf{Part III.} Distinct retained results from the earlier human edition, exact examples, and the bounded-operator reciprocal calculus received from Paper IV.
\end{minipage}
\vspace{13mm}\end{titlepage}
\hypersetup{pageanchor=true}
\section*{Reading this edition}\addcontentsline{toc}{section}{Reading this edition}
Paper VI has several substantial source branches. This edition preserves the latest formal-core manuscript in Part I and the complete strengthened standalone manuscript in Part II. Part III retains twenty-four earlier results with distinct statements or hypotheses, five exact examples, and the holomorphic operator-substitution section migrated from Paper IV. Overlap is intentional and is not a claim of independent novelty for each proof environment.

The formal denominator is exactly the thirty-three scoped results of Part I. The inherited September 6, 2026 release records 341 explicit Lean theorem declarations across 47 proof modules and an audit of 782 namespace declarations. These are different units. No fresh Lean compilation was available for this October edition, and the formal count does not automatically include Parts II or III. The Lean guide gives the exact targets and specialization boundaries.

Part I includes three explicitly open conjectures. Part II supplies bounded or finite theorems for several related questions; it does not settle arbitrary continuum limits, unbounded-generator convergence, general statistical sufficiency, or globally optimal nonnormal model reduction. The reader should keep each result's declared space, topology, positivity, and stability hypotheses. Part I's mass-only Bayesian commutation criterion assumes at least two coarse blocks; Part II's stronger sufficiency convention also preserves within-block conditionals, so its one-block case still requires a constant likelihood.

The current checks, historical compiler evidence, and numerical regressions are recorded separately in the accompanying package. Finite checks and illustrations have bounded scopes. They do not replace proofs. The September 12 worked visual appendix, its exact models, and additional guides to the strengthened and retained material are supplied in the visual companion.

Read Part I for the common operator language and the exact released formal contract. Read Part II for bounded Banach-space development and the broader probabilistic and analytical realizations. Read Part III for product-topology limits, reversible coarse dynamics, prior-restricted and coarse filtering, killed-transfer perturbations, rational realization, and the transferred operator reciprocal family. Section numbers in Part II have prefix E; those in Part III have prefix R. Original labels and statement locations are mapped in the editable sources.

The final mathematical audit makes explicit the hypotheses needed for contour winding, positive memory decay, finite moment closure, and eventual absorption. It also clarifies summability across varying spaces. Every substantive change is recorded against preserved sources. Historical source test counts retain their historical dates.
\clearpage
\tableofcontents
\clearpage
\listoffigures
\listoftables
\clearpage
\part*{Part I\quad The released formal core}\addcontentsline{toc}{part}{Part I: The released formal core}
\begin{center}\large Projector-Resolved Seed Calculus VI\par\normalsize Transfer Semigroups: Stochastic, Bayesian, Fractional, and PDE Realizations\end{center}
'''
def sep(part,title,prefix):return '\n'+r'\clearpage'+'\n'+r'\part*{Part '+part+r'\quad '+title+r'}\addcontentsline{toc}{part}{Part '+part+': '+title+'}\n'+r'\setcounter{section}{0}\setcounter{figure}{0}\setcounter{table}{0}'+'\n'+r'\renewcommand{\thesection}{'+prefix+r'\arabic{section}}'+'\n'+r'\renewcommand{\theHsection}{'+prefix+r'.\arabic{section}}'+'\n'+r'\renewcommand{\thefigure}{'+prefix+r'\arabic{figure}}'+'\n'+r'\renewcommand{\theHfigure}{'+prefix+r'.\arabic{figure}}'+'\n'+r'\renewcommand{\thetable}{'+prefix+r'\arabic{table}}'+'\n'+r'\renewcommand{\theHtable}{'+prefix+r'.\arabic{table}}'+'\n'
final=preamble+cover+corebody+sep('II','Extended mathematical development','E')+r'\graphicspath{{extension_figures/}}'+extbody+sep('III','Retained results and operator calculus','R')+supp+migration+'\n'+r'\clearpage\bibliographystyle{alpha}\bibliography{references}'+'\n'+r'\end{document}'+'\n'
(R/'Paper_VI_Traditional_Final.tex').write_text(final)
(R/'references.bib').write_text((R/'source/strengthened.bib').read_text()+'\n'+(R/'source/migration.bib').read_text())
(R/'EDITORIAL_CHANGES.json').write_text(json.dumps(dict(changes=changes,invisible_locator_labels=anchors,selected_earlier_labels=selected),indent=2)+'\n')
print('Assembled',len(final),'characters;',len(changes),'changes;',len(selected),'retained earlier records')
