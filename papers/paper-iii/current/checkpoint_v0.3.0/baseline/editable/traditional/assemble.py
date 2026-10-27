#!/usr/bin/env python3
"""Reproduce the historical Paper III integration in a separate archival directory.

The authored monograph master, chapters and current references are never
regenerated. Historical reproduction requires an explicit archival destination.
"""
from pathlib import Path
import argparse
import re
import json
import shutil


def main():
    source_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--historical-output', required=True, type=Path,
                        help='A named directory below source/historical_assembly/.')
    args = parser.parse_args()
    R = args.historical_output.expanduser().resolve()
    history = (source_root / 'source/historical_assembly').resolve()
    if R == history or not R.is_relative_to(history):
        parser.error('--historical-output must be a directory below ' + str(history))
    (R / 'source').mkdir(parents=True, exist_ok=True)
    for name in ('canonical.tex', 'expanded.tex', 'expanded.bib'):
        shutil.copy2(source_root / 'source' / name, R / 'source' / name)
    shutil.copytree(source_root / 'figures', R / 'figures', dirs_exist_ok=True)
    f = (R/'source/canonical.tex').read_text()
    e = (R/'source/expanded.tex').read_text()
    changes = []

    def replace(s, old, new, reason):
        assert old in s, old
        changes.append({'old': old, 'new': new, 'reason': reason})
        return s.replace(old, new)

    fb = f[f.index(r'\section{Purpose'):f.index(r'\begin{thebibliography}')]
    eb = e[e.index(r'\section{Introduction}'):e.index(r'\bibliographystyle')]
    math_changes = []
    def math_replace(s, old, new, reason, affected):
        assert old in s, old
        math_changes.append({'old':old,'new':new,'reason':reason,'affected':affected,'authorization':'Root-authorized local audit repair; original source preserved.'})
        return s.replace(old,new)

    eb = math_replace(eb, 'there is a bounded right inverse', 'there is a bounded linear right inverse', 'The operator norm estimates and the linear closed range argument require a linear right inverse.', ['thm:right_inverse_correction','cor:correction_stability'])
    eb = math_replace(eb, 'The class below is therefore finite whenever the two graded pieces have finite length, even if the completed problem is infinite.', 'The cokernel below has finite length whenever the target graded piece has finite length, even if the completed problem is infinite. Finite cardinality requires additional finiteness of the underlying graded pieces.', 'Finite length over an infinite field does not imply finite cardinality.', ['def:depth_obstruction','cor:finite_branch_count'])
    eb = math_replace(eb, 'Let $\\Lcal$ be complete and carry operations $\\ell_r$ that respect a finite abelian group grading.', 'Let $\\Lcal$ be complete and carry operations $\\ell_r$ that respect a finite abelian group grading. Assume the packet projectors are continuous for the topology in which the series below converges.', 'Completeness alone does not justify moving projectors through a convergent infinite sum.', ['prop:packet_l_infinity'])
    eb = math_replace(eb, 'Completeness permits the convergent sums to be projected term by term.', 'Continuity of the packet projectors permits the convergent sums to be projected term by term.', 'Use the explicit continuity hypothesis in the proof of passage to the limit.', ['prop:packet_l_infinity'])
    eb = math_replace(eb, r'\begin{corollary}[Tree pruning]\label{cor:tree_pruning}', r'''For an infinite tree expansion, each underlying tree's finite sum of packet decorations is kept grouped. The unlabelled tree majorant does not imply absolute convergence of the fully flattened family of decorations for arbitrary oblique projectors. Finite tree reconstruction and this grouped interpretation remain exact.

    \begin{corollary}[Tree pruning]\label{cor:tree_pruning}''', 'A bounded oblique packet system can produce decorations that do not tend to zero although the unlabelled tree series converges absolutely. No unconditional rearrangement is justified.', ['thm:packet_tree_reconstruction','cor:tree_pruning'])
    eb = math_replace(eb, 'Removing all such trees leaves the exact series unchanged.', 'Removing all such zero terms leaves every finite tree sum unchanged and therefore leaves the grouped infinite series unchanged.', 'Make the pruning statement use the grouping proved by finite reconstruction.', ['cor:tree_pruning'])
    eb = math_replace(eb, 'Split the variables and equations as', 'Let $U,V,Y_P,Y_Q$ be Banach spaces. On an open neighborhood of $(u_0,v_0)\\in U\\times V$, split the variables and equations as', 'State the ambient category required by the implicit function theorem.', ['sec:nonlinear_elimination','thm:exact_local_elimination','thm:schur_derivative','thm:schur_second_derivative','cor:reduced_packet_jets'])
    eb = math_replace(eb, "Assume $F$ is twice continuously Fr\\'echet differentiable near $(u_0,v_0)$ and", "Assume $F$ takes values in $Y_P\\times Y_Q$, is twice continuously Fr\\'echet differentiable near $(u_0,v_0)$, satisfies $F_Q(u_0,v_0)=0$, and", 'Without the zero basepoint hypothesis, derivative invertibility alone does not produce a zero graph through the declared basepoint.', ['sec:nonlinear_elimination','thm:exact_local_elimination','thm:schur_derivative','thm:schur_second_derivative','cor:reduced_packet_jets'])
    eb = math_replace(eb, 'is invertible.  The implicit function theorem gives a local map $v=\\varphi(u)$ with', 'is a Banach space isomorphism from $V$ to $Y_Q$. The implicit function theorem gives a local map $v=\\varphi(u)$, with $\\varphi(u_0)=v_0$, satisfying', 'Specify bounded invertibility and the basepoint of the implicit solution.', ['sec:nonlinear_elimination','thm:exact_local_elimination','thm:schur_derivative','thm:schur_second_derivative','cor:reduced_packet_jets'])
    eb = math_replace(eb, 'For a loop, this product is its holonomy.', 'For a loop, this product is its holonomy. In the based loop group, $\\gamma_2\\gamma_1$ means first traverse $\\gamma_1$ and then $\\gamma_2$, so $T_{\\gamma_2\\gamma_1}=T_{\\gamma_2}T_{\\gamma_1}$.', 'Declare the loop multiplication convention matching rightmost-first operator composition.', ['thm:gauge_classification'])
    eb = math_replace(eb, 'be a finite family of complete orthogonal packet systems that is continuously differentiable in operator norm.  Thus', 'be a finite family of complete orthogonal packet systems that is continuously differentiable in operator norm for $t\\in[0,T]$, where $T\\ge0$. Here every $P_\\alpha(t)$ is a bounded self-adjoint projection, so $P_\\alpha(t)^*=P_\\alpha(t)=P_\\alpha(t)^2$. Zero projections are permitted in this section and contribute zero to all generator sums. When $T=0$, every partition product is the empty product $I$. Thus', 'Self-adjointness is needed for skew-adjointness and unitarity; specify the interval and zero-object endpoint conventions.', ['sec:kato_transport','lem:packet_commutator','thm:kato_transport','cor:one_moving_subspace','prop:packet_direct_rotation','thm:direct_rotation_convergence','thm:sampled_transport_convergence'])
    eb = math_replace(eb, '\\begin{proof}\nSkew adjointness of $K(t)$ gives', '\\begin{proof}\nThe continuous bounded generator has an evolution inverse. Indeed, solve $\\dot V=-VK$ with $V(0)=I$. Differentiation gives $(VU)^{\\prime}=0$, hence $VU=I$. The product $W=UV$ satisfies $\\dot W=KW-WK$ and $W(0)=I$; uniqueness of this bounded linear equation gives $UV=I$. Thus $U$ is invertible.\n\nSkew adjointness of $K(t)$ gives', 'In infinite dimensions U*U=I establishes only an isometry; the bounded ODE provides the required two-sided inverse before unitarity is concluded.', ['thm:kato_transport'])
    eb = math_replace(eb, r'\max_{\alpha\in I}\|P_\alpha-Q_\alpha\|<1,', r'\max\bigl(\{0\}\cup\{\|P_\alpha-Q_\alpha\|:\alpha\in I\}\bigr)<1,', 'Use an empty-family maximum convention compatible with the zero Hilbert space.', ['prop:packet_direct_rotation'])
    eb = math_replace(eb, r'Put $\delta=\max_\alpha\|P_\alpha-Q_\alpha\|$.', r'Put $\delta=\max(\{0\}\cup\{\|P_\alpha-Q_\alpha\|:\alpha\in I\})$.', 'Match the empty-family convention in the proposition and its proof.', ['prop:packet_direct_rotation'])
    eb = math_replace(eb, 'If $P_\\alpha(0)=P_\\alpha(T)$ for every $\\alpha$, then $U(T)$ preserves every initial packet.', 'Assume the complete packet family is twice continuously differentiable in operator norm on $[0,T]$. If $P_\\alpha(0)=P_\\alpha(T)$ for every $\\alpha$, then $U(T)$ preserves every initial packet.', 'The two cited convergence theorems require C² packet paths and Lipschitz K; C² on the compact interval supplies both.', ['cor:continuous_holonomy'])
    # The module statement uses a kernel coset; affine-space terminology needs a field.
    old='form an affine space under $\\Ker\\overline L_m$'
    if old not in eb:
        old='form an affine space under $\\Ker\\overline L_m$.'
    if old in eb:
        eb = math_replace(eb, old, old.replace('an affine space under','a coset of'), 'The section allows general modules; the preceding lifting criterion gives a coset, not necessarily a vector-space affine space.', ['cor:unique_lift_branch'])
    else:
        start=eb.index(r'\label{cor:unique_lift_branch}')
        raise ValueError(eb[start:start+1600])

    fb = replace(fb, 'The completion denominator is the thirty theorem-like environments in the\npaper:', 'The completion denominator of the finite v1.0.1 contract is the thirty theorem-like environments in Part~I:', 'Restrict the inherited finite formalization count to its original scope.')
    fb = replace(fb, r'\section{Nonlinear operation trees: proved locality and scoped roadmap}', r'\section{Nonlinear operation trees: locality and the formalization frontier}', 'Explain the roadmap relative to formal coverage, while Part II contains written nonlinear results.')
    fb = replace(fb, r'\subsection{Typed colored extension (roadmap)}', r'\subsection{Typed colored extension beyond the finite contract}', 'Distinguish the finite formal boundary from the expanded mathematical development.')
    fb = replace(fb, r'\statusroadmap{No tree-level defect identity, higher-chain-rule theorem, or nonlinear norm bound is claimed here.}', r'\statusroadmap{Tree-level defect identities, higher chain rules, and nonlinear norm bounds are outside the finite Lean contract. Ordinary mathematical results in these directions appear in Part~II under their stated hypotheses.}', 'Prevent an inherited formal-scope statement from contradicting the expanded written proofs.')
    fb = replace(fb, 'This version does not prove convergence of an infinite tree series, existence\nof derivatives, a Banach-space Fa\\`a di Bruno theorem, a Baker--Campbell--Hausdorff\nexpansion, a continuum limit, or an identification of algebraic holonomy with\ncurvature of a smooth bundle.  It also does not derive a connection from\ndata, optimization, physics, or probability.', 'The finite formal contract does not include convergence of an infinite tree series, existence\nof derivatives, a Banach-space Fa\\`a di Bruno theorem, a Baker--Campbell--Hausdorff\nexpansion, a continuum limit, or an identification of algebraic holonomy with\ncurvature of a smooth bundle. Part~II supplies ordinary proofs for its explicit nonlinear and analytic statements. This edition does not derive a connection from\ndata, optimization, physics, or probability.', 'Localize exclusions to formal scope without deleting genuine exclusions.')
    fb = replace(fb, 'These facts define a clean boundary for the nonlinear program.  At the audited\nboundary,', 'These facts define the boundary of the finite formal contract.  At that\nboundary,', 'Connect the finite conclusion to the expanded second part.')
    fb = replace(fb, 'multilinear packet labelings, and Fa\\`a di Bruno expansions remain explicit\nfuture milestones rather than completed results.', 'multilinear packet labelings, and Fa\\`a di Bruno expansions remain\noutside this finite Lean contract. Part~II develops the corresponding ordinary mathematics, including packet jets, rooted tree expansions, and explicit nonlinear obstruction theorems.', 'Do not describe written expanded results as globally absent.')
    fb = replace(fb, r'\section{Conclusion}', r'\section{The finite contract and the nonlinear transition}', 'The finite conclusion is now a transition rather than the end of the edition.')
    fb = replace(fb, r'\section{Nonlinear operation trees: locality and the formalization frontier}', r'\clearpage\section{Nonlinear operation trees: locality and the formalization frontier}', 'Keep the section heading with its first subsection instead of leaving it alone at a page foot.')
    for old,new in [('The first part treats the local nonlinear calculus.','The first stage of Part~II treats the local nonlinear calculus.'),('The second part studies nonlinear iteration.','The next stage studies nonlinear iteration.'),('The third part concerns correction and obstruction.','The correction stage concerns correction and obstruction.'),('The final part studies elimination and gluing.','The final stage studies elimination and gluing.')]:
        eb=replace(eb,old,new,'Clarify narrative stages within Part II without confusing them with the edition\'s two numbered parts.')

    pre = r'''\documentclass[11pt,a4paper]{article}
    \usepackage[T1]{fontenc}\usepackage{lmodern}
    \usepackage[a4paper,margin=23mm,includeheadfoot,headheight=15pt,headsep=15pt,footskip=22pt]{geometry}
    \usepackage[nopatch=footnote]{microtype}
    \usepackage{amsmath,amssymb,amsthm,mathtools,amscd,aliascnt}
    \usepackage{booktabs,longtable,array,tabularx,enumitem,fancyhdr,graphicx}
    \usepackage[table]{xcolor}\usepackage{setspace,needspace,listings,caption,titlesec,etoolbox,bm,float}
    \usepackage{xurl}\usepackage{hyperref}\usepackage[nameinlink,noabbrev]{cleveref}\usepackage{bookmark}
    \definecolor{accent}{HTML}{137668}\definecolor{muted}{HTML}{536568}
    \definecolor{leanblue}{RGB}{20,72,135}\definecolor{roadmapgray}{RGB}{86,86,86}
    \frenchspacing\emergencystretch=3em\clubpenalty=10000\widowpenalty=10000\raggedbottom
    \titleformat{\section}{\sffamily\bfseries\large\color{accent}}{\thesection}{.7em}{}
    \titleformat{\subsection}{\sffamily\bfseries\normalsize}{\thesubsection}{.7em}{}
    \titlespacing*{\section}{0pt}{1.4\baselineskip}{.55\baselineskip}
    \captionsetup{font=small,labelfont={sf,bf},labelsep=period}
    \pretocmd{\section}{\Needspace{7\baselineskip}}{}{}\pretocmd{\subsection}{\Needspace{5\baselineskip}}{}{}
    \allowdisplaybreaks\setstretch{1.055}\setlength{\parskip}{.3em}\setlength{\parindent}{1.35em}
    \setlist[itemize]{topsep=.35em,itemsep=.15em,leftmargin=1.6em}\setlist[enumerate]{topsep=.35em,itemsep=.15em,leftmargin=1.8em}
    \graphicspath{{figures/}}
    \hypersetup{pdftitle={Projector-Resolved Seed Calculus III: Typed Transfer, Nonlinear Packets and Obstruction Theory},pdfauthor={Komorebi P.},colorlinks=true,linkcolor=accent,citecolor=accent,urlcolor=accent}
    \pagestyle{fancy}\fancyhf{}
    \fancyhead[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}KOMOREBI MATHEMATICS / PAPER III}
    \fancyhead[R]{\sffamily\fontsize{8}{10}\selectfont\color{muted}TRADITIONAL PAPER}
    \fancyfoot[L]{\sffamily\fontsize{8}{10}\selectfont\color{muted}Projector-resolved seed calculus}\fancyfoot[R]{\sffamily\small\color{accent}\thepage}
    \lstset{basicstyle=\ttfamily\footnotesize,breaklines=true,frame=single,showstringspaces=false,columns=fullflexible,keepspaces=true}
    \newtheorem{theorem}{Theorem}[section]
    '''
    for style, envs in [('plain',['proposition','lemma','corollary']),('definition',['definition','example','construction','standardfact']),('remark',['remark','boundary','roadmap'])]:
        pre += '\\theoremstyle{'+style+'}\n'
        for env in envs:
            name = {'standardfact':'Standard Fact','roadmap':'Formalization target'}.get(env,env.title())
            pre += '\\newaliascnt{'+env+'}{theorem}\n\\newtheorem{'+env+'}['+env+']{'+name+'}\n\\aliascntresetthe{'+env+'}\n'
            pre += '\\crefname{'+env+'}{'+name.lower()+'}{'+name.lower()+'s}\n'
    pre += '\\crefname{theorem}{theorem}{theorems}\n'
    # Identical repeated macro definitions are emitted only once.
    macros = {}
    for src in (f,e):
        for m in re.finditer(r'^\\newcommand\{(\\\w+)\}[^\n]*$',src, re.M):
            line=m.group()
            if line.endswith('%'): continue
            if m[1] in macros: assert macros[m[1]]==line, (m[1],line)
            macros[m[1]]=line
    pre += '\n'.join(macros.values())+'\n'
    pre += r'''
    \newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
    \newcolumntype{Y}{>{\raggedright\arraybackslash}X}
    \newcommand{\statusleanthree}[1]{\par\smallskip\noindent\begin{minipage}{\linewidth}{\color{leanblue}\textbf{Formal contract: Paper III v1.0.1.}}\par\begingroup\small\raggedright\leanname{#1}\par\endgroup\end{minipage}\par\smallskip}
    \newcommand{\statusleanprior}[1]{\par\smallskip\noindent\begin{minipage}{\linewidth}{\color{leanblue}\textbf{Inherited formal contract: Papers I--II.}}\par\begingroup\small\raggedright\leanname{#1}\par\endgroup\end{minipage}\par\smallskip}
    \newcommand{\statusroadmap}[1]{\par\smallskip\noindent{\color{roadmapgray}\textbf{Outside the finite formal contract.}}\ #1\par\smallskip}
    \begin{document}
    \begin{titlepage}\thispagestyle{empty}
    \vspace*{13mm}
    {\sffamily\bfseries\color{accent}\large KOMOREBI MATHEMATICS\quad /\quad PAPER III\par}
    \vspace{12mm}
    {\sffamily\bfseries\fontsize{29}{34}\selectfont Projector-Resolved\\Seed Calculus III\par}
    \vspace{8mm}
    {\sffamily\fontsize{18}{23}\selectfont Typed Transfer, Nonlinear Packets,\\and Obstruction Theory\par}
    \vspace{12mm}{\large Komorebi P.\par}
    \vspace{5mm}{\sffamily\color{muted}Traditional final edition\quad\textbullet\quad 5 October 2026\par}
    \vfill
    \noindent\begin{minipage}{.94\linewidth}
    \textbf{Reading route.} Typed edge words and exact coordinate transport lead to connection defects and packet obstruction witnesses. Nonlinear packet jets then lead to tree expansions, correction complexes, filtered lifting, elimination, and smooth transport.

    \medskip
    \textbf{Scope.} Part~I retains the finite v1.0.1 formal contract. Part~II gives the strengthened nonlinear and analytic development with ordinary proofs. Formal coverage stays attached to the exact released declarations and does not extend merely because both parts appear in one edition.
    \end{minipage}
    \vspace{13mm}
    \end{titlepage}
    \begin{abstract}
    Finite projector packets turn linear transfer into typed walks and arbitrary maps into exact coordinate representations. We separate canonical coordinate transport, which satisfies an exact cocycle law, from a chosen connection, whose failure to compose produces holonomy and packet obstruction witnesses. We then develop nonlinear packet jets and higher composition, convergent rooted tree expansions, graded operations, and nonlinear refinement defects. A specified correction map produces a canonical cokernel obstruction. Relative exact sequences, mapping cones, Hilbert splitting, nonlinear correction, and filtered lifting describe how these obstructions behave. Exact elimination produces Schur formulas, and finite transport reduces gluing to fundamental cycle holonomy. For smooth orthogonal packet families, direct packet rotations converge in operator norm to canonical unitary transport. The finite formal contract and the broader ordinary proof development are identified separately throughout.
    \end{abstract}
    \noindent This edition preserves both the finite release and the strengthened nonlinear manuscript. Its companions are a worked visual guide and a Lean guide. The released Lean evidence is inherited; this editorial build does not assert a new Lean execution.
    \tableofcontents\listoffigures\clearpage
    \part{Finite typed transfer and the formal contract}\label{part:finite}
    \noindent The finite release supplies the algebraic foundation and its declaration-level contract. In this part, ``roadmap'' and ``outside the contract'' refer to the finite Lean formalization, not to the absence of ordinary mathematical results in Part~II. The original thirty theorem-like statements and their proof bodies are retained. The source contract has 41 mapping rows, which include definitions and other interfaces and therefore are not the same count as theorem-like statements.

    \medskip\noindent The preserved v1.0.1 release records Lean v4.34.0-rc2 against Mathlib revision \leanname{aeb72f1e9981b6d35b426b16dca7759be3e7ba06} \cite{lean,mathlib}. The compiler and kernel-check descriptions in Part~I describe that inherited evidence. Current editorial checks of this edition are recorded separately in the companion verification files.
    '''
    transition = r'''
    \clearpage
    \part{Nonlinear packet calculus, obstruction complexes, and holonomy}\label{part:nonlinear}
    \noindent The strengthened development below moves from exact arbitrary-function coordinates to differentiable interactions, specified correction problems, and finite or smooth transport. Its ordinary proofs retain their own hypotheses. They are not asserted to belong to the finite Lean contract of Part~I.

    \medskip\noindent The notational change from \(\cA,\cS\) to \(\Acal,\Scal\) is typographical: both denote analysis and synthesis for the declared packet system. A connection is still additional data. Smooth canonical transport is constructed from a moving projector family, whereas the algebraic exact coordinate transport in Part~I compares fixed exact descriptions of one ambient object.
    '''
    bib = (R/'source/expanded.bib').read_text()+r'''
    @misc{paperI,author={Komorebi P.},title={Projector-Resolved Seed Calculus I: Typed Seeds, Operator Grammars, and Exact Reconstruction},year={2026},note={Version 1.2.1}}
    @misc{paperII,author={Komorebi P.},title={Projector-Resolved Seed Calculus II: Polyphase Refinement, Weighted Transfer, and Dyadic--Odd Resolution},year={2026},note={Version 1.2.1}}
    @incollection{lean,author={de Moura, Leonardo and Ullrich, Sebastian},title={The {Lean 4} Theorem Prover and Programming Language},booktitle={Automated Deduction -- CADE 28},series={Lecture Notes in Computer Science},volume={12699},pages={625--635},publisher={Springer},year={2021},doi={10.1007/978-3-030-79876-5_37}}
    @inproceedings{mathlib,author={{The mathlib Community}},title={The {Lean} mathematical library},booktitle={Proceedings of the 9th ACM SIGPLAN International Conference on Certified Programs and Proofs},pages={367--381},publisher={Association for Computing Machinery},year={2020},doi={10.1145/3372885.3373824}}
    '''
    (R/'references.bib').write_text(bib)
    (R/'Paper_III_Traditional_Final.tex').write_text(pre+fb+transition+eb+'\n\\begingroup\\small\\setstretch{1}\n\\bibliographystyle{plain}\n\\bibliography{references}\n\\endgroup\n\\end{document}\n')
    (R/'EDITORIAL_CHANGES.json').write_text(json.dumps({'routine_changes':['Integrated both source bodies in two connected parts without deduplicating proofs.','Unified typography, theorem counters, contents, bibliography and local figures.','Added scope introduction and transition distinguishing inherited finite formalization from strengthened ordinary proofs.','Changed status macros to formal-contract labels and identified inherited evidence.'],'exact_prose_changes':changes,'mathematical_changes':math_changes},indent=2)+'\n')
    print('Assembled Paper III:', len(pre+fb+transition+eb), 'characters')


if __name__ == '__main__':
    main()
