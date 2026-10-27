#!/usr/bin/env python3
"""Assemble the release manuscript and its source concordance. No Lean execution."""
from pathlib import Path
import csv, json, re, hashlib

HERE = Path(__file__).resolve().parent
UPSTREAM = HERE.parent/'formal'
INDEX = list(csv.DictReader((UPSTREAM/'DECLARATION_INDEX_v0.16.0.csv').open()))
DECLS = {r['name']:r for r in INDEX}
PREFIX = 'Komorebi.SufficientResolution.'
claims, parts = [], []

def prose_hypotheses(s):
    """Escape the prose synopsis without changing its quantitative meaning."""
    replacements={'δ':r'\(\delta\)','λ':r'\(\lambda\)','τ':r'\(\tau\)',
                  'σ':r'\(\sigma\)','α':r'\(\alpha\)',
                  '→':r'\(\to\)','≤':r'\(\le\)','≥':r'\(\ge\)',
                  '⊥':r'\(\perp\)','∈':r'\(\in\)','‖':r'\(\Vert\)',
                  '²':r'\({}^2\)','′':r'\({}^{\prime}\)','−':'-'}
    result=[]
    for c in s:
        if c in replacements: result.append(replacements[c])
        elif c in '_%&#{}': result.append('\\'+c)
        elif c=='^': result.append(r'\textasciicircum{}')
        else: result.append(c)
    return ''.join(result).replace(r'\)\(', '').replace('/',r'/\allowbreak ')

PRINTED_SETUPS={
 2:r'Commutative-ring modules; linear $C:X\to Z$, $R:Z\to X$ with $CR=I_Z$; arbitrary endomorphisms $S,T,U$ of $X$.',
 3:r'Commutative-ring modules and a linear presentation $G\xrightarrow{A}V\xrightarrow{\delta}W$ with $\delta A=0$; a compatible vector $v\in\ker\delta$.',
 4:r'Commutative-ring modules; a linear observation $O:X\to Y$ and an arbitrary family of allowed endomorphisms $T_i:X\to X$; every finite chronological word is included.',
 16:r'Bounded maps on the normed spaces of SR-14; $\nn{T_i}\le1$ for every true operation; $\nn{U_i}\le1$ in the nonexpansive case or a common $0\le b<1$ with $\nn{U_i}\le b$ in the contractive case; $\nn{qT_i-U_iq}\le\epsilon$ and $\nn{O-Vq}\le\eta$ with $\epsilon,\eta\ge0$.',
 22:r'Real Banach spaces $X,Z$; bounded autonomous real generators $L,A$ and bounded representation/readouts $q,O,V$; real rates $a,b$ of either sign; $t\ge0$ and $M_L,M_A,\epsilon,\eta\ge0$. For every $s\ge0$, $\nn{e^{sL}}\le M_Le^{as}$ and $\nn{e^{sA}}\le M_Ae^{bs}$; also $\nn{qL-Aq}\le\epsilon$ and $\nn{O-Vq}\le\eta$.',
 47:r'Known bounded $A:G\to V$ between real Hilbert spaces and a fixed true source $g$; a valid pointwise allowance $\nn{Ag-v}\le\eta$. Accepted-source consistency uses a fixed $\tau\ge1$ and genuine bounds $\nn{Ag-v_i}\le\eta_i$ with $\eta_i\to0$. Total selector existence additionally requires $\eta>0$ and $\tau>1$.'
}

def section(title, text):
    parts.append('\\section{'+title+'}\n'+text+'\n')

def prose(text):
    parts.append(text+'\n')

def claim(i, title, hypotheses, anchors, statement, proof, dependencies=()):
    cid=f'SR-{i:02d}'
    resolved=[]
    for a in anchors.split(';'):
        a=a.strip()
        if not a: continue
        name=PREFIX+a
        if name not in DECLS:
            candidates=[n for n in DECLS if n.endswith('.'+a)]
            if len(candidates)!=1: raise ValueError(f'{cid}: unknown or ambiguous {name}: {candidates}')
            name=candidates[0]
        d=DECLS[name]
        resolved.append({'name':name,'file':d['file'],'kind':d['kind'],
                         'source_sha256':hashlib.sha256((UPSTREAM/d['file']).read_bytes()).hexdigest()})
    claims.append({'claim_id':cid,'title':title,'block':(i-1)//4+1,
                   'hypotheses':hypotheses,'domain':hypotheses.split(';')[0],
                   'hypotheses_tex':PRINTED_SETUPS.get(i,prose_hypotheses(hypotheses)),
                   'document_label':cid,'status':'proved_under_printed_hypotheses',
                   'evidence':'existing_Lean_declarations_and_reconstructed_prose_proof',
                   'dependencies':list(dependencies),'anchors':resolved,
                   'statement_tex':statement,'proof_tex':proof})
    parts.append('\\par{\\small\\textbf{Hypotheses.} '+claims[-1]['hypotheses_tex']+'}\\par\n')
    parts.append('\\begin{theorem}['+cid+'\\quad '+title+']\\label{'+cid+'}\n'+statement+
                 '\n\\end{theorem}\n\\begin{proof}\n'+proof+'\n\\end{proof}\n')
    parts.append('\\src{'+('; '.join(a['name'].removeprefix(PREFIX) for a in resolved))+'}\n')

PREAMBLE=r'''\documentclass[11pt]{article}
\usepackage[letterpaper,margin=0.88in,headheight=15pt]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amsthm,amssymb,mathtools}
\IfFileExists{newtxtext.sty}{\usepackage{newtxtext,newtxmath}}{\usepackage{lmodern}}
\usepackage{microtype,booktabs,longtable,tabularx,array,enumitem,xcolor,fancyhdr,titlesec,xurl}
\usepackage{hyperref}
\definecolor{Navy}{HTML}{17324D}
\definecolor{Teal}{HTML}{2F7A78}
\hypersetup{colorlinks=true,linkcolor=Navy,urlcolor=Teal,pdfauthor={Komorebi P.},
pdftitle={Sufficient Resolution: Exact Reduction, Hidden Memory, and Certified Reconstruction}}
\setlength{\parindent}{0pt}\setlength{\parskip}{4.2pt}
\setlist{itemsep=2pt,topsep=3pt,leftmargin=1.7em}
\allowdisplaybreaks
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\textsc{Sufficient Resolution}}
\fancyhead[R]{\small Komorebi P.}\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries\color{Navy}}{\thesection}{0.7em}{}
\titleformat{\subsection}{\large\bfseries\color{Navy}}{\thesubsection}{0.6em}{}
\newtheorem{theorem}{Theorem}[section]
\theoremstyle{definition}\newtheorem{definition}[theorem]{Definition}
\newtheorem{example}[theorem]{Example}
\theoremstyle{remark}\newtheorem{remark}[theorem]{Remark}
\DeclareMathOperator{\Ran}{Ran}\DeclareMathOperator{\dist}{dist}
\DeclareMathOperator{\End}{End}\DeclareMathOperator{\id}{id}
\DeclareMathOperator{\spanof}{span}\DeclareMathOperator{\cl}{cl}
\newcommand{\RR}{\mathbb R}\newcommand{\QQ}{\mathbb Q}
\newcommand{\nn}[1]{\left\lVert #1\right\rVert}
\newcommand{\ip}[2]{\left\langle #1,#2\right\rangle}
\newcommand{\src}[1]{\par{\small\color{Teal}\textit{Formal source:} \path{#1}.}\par}
\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}
\vspace*{0.9in}
{\color{Teal}\large\textsc{Komorebi\quad Realization Calculus}\par}
\vspace{0.35in}
{\color{Navy}\Huge\bfseries Sufficient Resolution\par}
\vspace{0.22in}
{\LARGE Exact Reduction, Hidden Memory,\\[5pt] and Certified Reconstruction\par}
\vspace{0.55in}
{\Large Komorebi P.\par}
\vspace{0.14in}
{\large Final edition\quad October 6, 2026\par}
\vfill
\begin{minipage}{0.92\textwidth}
\textbf{Reading set.} This traditional paper is accompanied by a visual guide,
a Lean guide, and the complete source ZIP. The ZIP includes the \texttt{.md}
files, editable manuscript sources, Lean sources, Python implementations,
example data, and verification records.\par
\medskip
\textbf{Scope.} Exact linear representation and behavioral reduction;
bounded discrete and continuous dynamics; real Hilbert reconstruction and
regularization; certified discrepancy rules; and calibration-based operator
allowances. Truth allowances and feasibility assumptions are stated explicitly.
\end{minipage}
\end{titlepage}
\hypersetup{pageanchor=true}
\pagenumbering{arabic}
\begin{abstract}
A representation is sufficient relative to an observation and a family of
permitted continuations. This paper develops that principle through exact
analysis and synthesis, hidden-return defects, behavioral quotients, finite
certificates, quantitative approximation, and certified inverse problems.
Split compression fails to preserve composition by an explicit hidden excursion;
for finite-dimensional hidden state, finitely many feedback moments decide
all-depth closure. Behavioral reduction retains precisely the distinctions that
some permitted future observation can detect. In real Hilbert settings,
compatibility, realizability, and source identifiability produce separate
obstructions and conditioning requirements. Canonical reconstruction,
Tikhonov regularization, discrepancy selection, inexact solves, changing
operators, and redundant calibration frames are assembled into a common chain
of contracts. Classical linear algebra and analysis provide the foundations.
The contribution of the assembled calculus is the explicit relation between
these contracts, their reusable certificates, and their sharp boundaries.
The paper consolidates sixteen development blocks and maps its principal
claims to existing Lean declarations. Finite rational implementations are
companion evidence and are not asserted to be formally verified.
\end{abstract}
\tableofcontents\newpage
'''

section('The problem and its mathematical contracts',r'''
Sufficiency depends on what a representation must support. A compression that
preserves today's observation can lose a distinction needed after a later
operation. A coordinate enlargement can be redundant yet exact. A compatible
local datum can still fail to have a global source. A small fitting residual
can coexist with large source error. These are distinct phenomena with
different mathematical witnesses.

The paper follows two connected lines. The first is the reduction of known
linear dynamics relative to declared observations. The second is the
reconstruction of a source from bounded linear data with explicit error
allowances. The first yields an exact semantic state quotient. The second yields
metric reconstruction and stability contracts. The present formalization does
not yet identify every behaviorally minimal state with a stably recoverable
target in an inverse problem. That bridge is an open extension, stated in the
final section.

\subsection{Conventions and domains}
Operator multiplication applies the right factor first: $STx=S(Tx)$.
A word $w=[i_1,\ldots,i_n]$ is chronological, so
$T_w=T_{i_n}\cdots T_{i_1}$; $T_\varnothing=I$. Concatenating $u$ then $v$
gives $T_{u\mathbin{+\!+}v}=T_vT_u$. Empty sums are zero and empty products are one.
All equalities of operators are equalities on the entire stated domain.

The exact redundant-coordinate theory works for modules over a semiring.
Subtraction and compression defects use modules over a commutative ring.
Dimension and annihilating-polynomial arguments use a field. Norm estimates
use bounded linear maps on normed spaces. Continuous flow results use bounded,
time-independent real generators on Banach spaces. Reconstruction and
regularization use real Hilbert spaces unless a weaker projection hypothesis
is printed explicitly. These changes of domain are part of the contracts.

For a subspace $L$ admitting orthogonal projection, $P_L$ denotes that actual
projection. On a Hilbert space, closed subspaces admit it. The notation
$\dist(v,L)=\inf_{\ell\in L}\nn{v-\ell}$ always refers to the actual subspace,
not a replacement chosen to make a theorem true. Closure is written $\cl L$.

\subsection{How to read the formal evidence}
The stable identifiers SR-01 through SR-64 label consolidated theorem groups.
They are editorial units, with hypotheses and proofs printed here. A separate
CSV/JSON concordance records their exact source declarations and source hashes.
Several formal lemmas can support one printed theorem, and one source lemma
can serve more than one explanatory purpose. The source inventory contains
998 theorem/lemma declarations in 93 production modules, including helper
lemmas and examples. It is not a count of independent new mathematical results.

The arguments below reconstruct the mathematics of the supplied Lean sources.
Classical inputs such as Cayley--Hamilton, orthogonal projection, the open
mapping theorem, Lax--Milgram, and the intermediate value theorem enter through
the source's Mathlib dependencies. This paper does not assert a new historical
priority assessment for those inputs. The Lean guide records exactly which
compilations and kernel replays are archived or freshly performed during this
release. Python certificates are tested implementations of mathematical
contracts; their parsers and algorithms are not Lean-verified.
''')

section('Exact coordinates, compression, and behavioral state',r'''
The first contract supplies two maps rather than identifying a coordinate
space with the object by convention. Let $a_X:X\to V_X$ and $s_X:V_X\to X$
be linear with $s_Xa_X=I_X$. The ambient space $V_X$ may have redundant
coordinates. Define $E_X=a_Xs_X$. For another such resolution of $Y$, put
\[
\mathcal K(T)=a_YTs_X,\qquad \mathcal D(K)=s_YKa_X.
\]
We call a proposed coordinate operator compatible when $E_YKE_X=K$.
''')
claim(1,'Exact redundant representation',
      'Semiring modules; supplied linear analysis/synthesis pairs with s_X a_X=I and s_Y a_Y=I.',
      'Resolution.projector_idempotent;Resolution.fixed_iff_realizable;Resolution.compatible_iff_existsUnique;Resolution.encode_comp;Resolution.encode_id',r'''
$E_X^2=E_X$, and $E_Xv=v$ exactly when $v\in\Ran a_X$. Moreover
\[
\mathcal D\mathcal K(T)=T,\qquad
\mathcal K\mathcal D(K)=E_YKE_X.
\]
Consequently a compatible $K$ is the encoding of a unique map $T:X\to Y$.
Encoding preserves composition. Its identity on resolved coordinates is $E_X$.
''',r'''
The splitting gives $E_X^2=a_X(s_Xa_X)s_X=a_Xs_X$. If $E_Xv=v$, then
$v=a_X(s_Xv)$; conversely $E_Xa_Xx=a_Xx$. Substituting the definitions yields
\[
s_Y(a_YTs_X)a_X=T,\qquad
a_Y(s_YKa_X)s_X=E_YKE_X.
\]
For compatible $K$, take $T=\mathcal D(K)$. If another $T'$ encodes to $K$,
decoding proves $T'=\mathcal D(K)$. Finally, an intermediate resolution of $Y$
has $s_Ya_Y=I_Y$, so
$\mathcal K(S)\mathcal K(T)=a_ZS(s_Ya_Y)Ts_X=a_ZSTs_X$.
Encoding $I_X$ gives $a_Xs_X=E_X$, which acts as identity on compatible kernels.
No inverse on all of $V_X$ has been assumed.
''')
prose(r'''
\begin{example}[Redundant coordinates]
For $X=\RR$ and $V_X=\RR^2$, take $a(x)=(x,x)$ and
$s(u,v)=(u+v)/2$. Then $E(u,v)=((u+v)/2,(u+v)/2)$.
The encoded scalar transformation $x\mapsto cx$ has matrix
$\frac c2\bigl(\begin{smallmatrix}1&1\\1&1\end{smallmatrix}\bigr)$.
Its redundant coordinate identity is $E$, while the ambient identity matrix
also acts on an unrealizable anti-diagonal sector. The distinction is exact.
\end{example}
''')

claim(2,'Hidden-return defect and coherence',
      'Commutative-ring modules; C:X→Z, R:Z→X linear with CR=I; arbitrary endomorphisms S,T,U.',
      'SplitCompression.defect_factorization;SplitCompression.defect_coherence;SplitCompression.defect_then',r'''
Set $P=RC$, $Q=I-P$, $\Phi(T)=CTR$, and
$\Delta(S,T)=\Phi(ST)-\Phi(S)\Phi(T)$. Then
\[
\Delta(S,T)=CSQTR,
\]
and associativity gives
\[
\Delta(S,T)\Phi(U)+\Delta(ST,U)
=\Phi(S)\Delta(T,U)+\Delta(S,TU).
\]
For two successive split compressions,
\[
\Delta_{21}(S,T)=\Phi_2(\Delta_1(S,T))
+\Delta_2(\Phi_1(S),\Phi_1(T)).
\]
''',r'''
Insert $I=P+Q$ between $S$ and $T$:
$CSTR=CS(P+Q)TR=(CSR)(CTR)+CSQTR$. This proves the factorization.
Expanding either side of the coherence identity cancels the terms
$\Phi(S)\Phi(T)\Phi(U)$ and leaves
$\Phi(STU)-\Phi(S)\Phi(TU)$ together with the same compensating term.
For the two-stage formula, add and subtract
$\Phi_2(\Phi_1(S)\Phi_1(T))$ in the composite defect. Linearity of $\Phi_2$
identifies the first difference with $\Phi_2(\Delta_1(S,T))$; the second is
the second-stage defect. Thus a later representation transports the earlier
error and can introduce another one. It does not remove the first term by definition.
''',('SR-01',))
claim(3,'Actual globalization obstruction',
      'Commutative-ring modules; linear G→A V→δ W with δA=0; compatible vector v∈kerδ.',
      'Globalization.obstructionClass_zero_iff;Globalization.all_obstructions_zero_iff_exact;Globalization.unique_realization_of_zero;PresentationMap.obstructionMap_compose;PresentationMap.reflects_zero_obstruction',r'''
For $\delta A=0$, define $K=\ker\delta$, $R=\Ran A\subseteq K$, and
$\mathcal H=K/R$. A compatible $v$ has class zero exactly when $v=Ag$
for some $g$. All classes vanish exactly when $R=K$. If $A$ is injective,
a zero class has a unique source.

Commuting presentation maps $LA=A'F$ and $\delta'L=M\delta$ induce a map
$\overline L:\mathcal H\to\mathcal H'$ by $[v]\mapsto[Lv]$.
These maps compose and preserve zero classes. Reflection of zero follows
when $\overline L$ is injective.
''',r'''
The chain condition puts the actual range of $A$ inside $K$. The zero class
criterion for a quotient is membership in the submodule divided out, giving
$[v]=0\iff v\in R\iff\exists g,Ag=v$. Every compatible class is zero exactly
when $K\subseteq R$; the reverse inclusion is already known. Injectivity of
$A$ gives uniqueness of any preimage.

For transport, if $v\in K$, then $\delta'Lv=M\delta v=0$.
If $v=Ag$, then $Lv=A'Fg$ lies in $R'$. Hence $L$ descends to the actual
quotients. Evaluating on representatives proves the composition law.
A linear map sends zero to zero. If its induced quotient map is injective,
$\overline L[v]=0=\overline L[0]$ implies $[v]=0$.
The commuting squares alone provide no such injectivity and do not assert
that either obstruction quotient vanishes.
''')
claim(4,'The all-future invisible quotient',
      'Commutative-ring modules; arbitrary allowed linear endomorphisms T_i and observation O; all finite chronological words.',
      'Behavioral.invisible_invariant;Behavioral.invariant_submodule_le_invisible;Behavioral.all_future_observations_preserved;Behavioral.quotient_eq_iff_same_future;Behavioral.exact_model_kernel_le',r'''
Let $N=\bigcap_w\ker(OT_w)$. It is the largest submodule contained in
$\ker O$ and invariant under every $T_i$. The operations and observation
descend to $X/N$, preserving every future observation. In particular,
\[
[x]=[y]\iff OT_wx=OT_wy\quad\text{for every finite word }w.
\]
If $q:X\to Z$ satisfies $qT_i=U_iq$ and $Vq=O$, then $\ker q\subseteq N$.
''',r'''
An intersection of kernels is a submodule. If $x\in N$, then
$OT_wT_ix=OT_{i::w}x=0$, so $T_ix\in N$. If an invariant submodule
$L\subseteq\ker O$ contains $x$, induction on word length gives $T_wx\in L$;
therefore $x\in N$. This establishes maximality.

Invariance defines quotient operations $[x]\mapsto[T_ix]$; containment in
$\ker O$ defines $[x]\mapsto Ox$. Induction gives their all-word fidelity.
Equality $[x]=[y]$ means $x-y\in N$, which is precisely equality of the
displayed observations by linearity. In an exact competing model, induction
gives $qT_w=U_wq$ and hence $OT_w=VU_wq$. If $qx=0$, every future observation
of $x$ is zero. Thus a competing model can retain extra distinctions, but
cannot erase any distinction visible to the specified future task.
''')

section('Discrete hidden memory and finite closure',r'''
Let $V$ be visible state and $H$ hidden state. Over a commutative ring, specify
four maps and form the actual full dynamics
\[
T(y,z)=(Ay+Bz,Gy+Dz).
\]
Put $C(y,z)=y$, $Ry=(y,0)$, $E_n=CT^nR$, and $M_k=BD^kG$.
The return $M_k$ contains entry into $H$, $k$ hidden transitions, and return
to $V$. Its first effect occurs after $k+2$ full transitions.
''')
claim(5,'Exact hidden elimination',
      'Commutative-ring modules; actual powers of T(y,z)=(Ay+Bz,Gy+Dz); arbitrary initial y_0,z_0.',
      'BlockDynamics.hidden_elimination;BlockDynamics.discrete_memory_equation;BlockDynamics.prepared_recurrence',r'''
For the trajectory $(y_n,z_n)=T^n(y_0,z_0)$,
\[
z_n=D^nz_0+\sum_{j=0}^{n-1}D^{n-1-j}Gy_j,
\]
and
\[
y_{n+1}=Ay_n+BD^nz_0+\sum_{j=0}^{n-1}M_{n-1-j}y_j.
\]
Prepared evolution ($z_0=0$) satisfies
$E_0=I$, $E_1=A$, and
\[
E_{n+1}=AE_n+\sum_{j=0}^{n-1}M_{n-1-j}E_j.
\]
''',r'''
At $n=0$, the first formula is $z_0=z_0$ with an empty sum. If it holds at
$n$, the actual recurrence $z_{n+1}=Gy_n+Dz_n$ gives the same formula at
$n+1$ after distributing $D$ and appending the newest forcing term.
Substituting this expression into $y_{n+1}=Ay_n+Bz_n$ proves the visible
memory equation. For a prepared input $y_0$, each $y_j$ equals $E_jy_0$.
The pointwise memory equation is therefore an operator identity because it
holds for every $y_0$. The equations are derived from powers of $T$; the
trajectory recurrence is not an extra certificate assumption.
''')
claim(6,'Prepared closure and the first return',
      'Same block dynamics; no finite-dimensional or orthogonality assumption.',
      'BlockDynamics.prepared_powers_iff_memory_zero;BlockDynamics.prepared_semigroup_iff_memory_zero;BlockDynamics.first_return_discrepancy;BlockDynamics.prepared_prefix_iff_memory_prefix;BlockDynamics.all_state_closure_iff_B_zero',r'''
The following conditions are equivalent:
\[
E_n=A^n\ (\forall n),\qquad M_k=0\ (\forall k),\qquad
E_{m+n}=E_mE_n\ (\forall m,n).
\]
More precisely,
\[
E_n=A^n\ (n\le N+1)\iff M_k=0\ (k<N).
\]
If $M_j=0$ for $j<k$, then $E_{k+2}-A^{k+2}=M_k$.
Closure for every initial hidden state is equivalent to $B=0$.
''',r'''
If all memory maps vanish, the recurrence in SR-05 reduces to
$E_{n+1}=AE_n$, proving $E_n=A^n$ by induction. Conversely, suppose exact
powers hold. Induct on $k$. In the recurrence for $E_{k+2}$, every term
except $M_kE_0$ involves a previously vanishing memory map. Thus
$E_{k+2}=AE_{k+1}+M_k$, forcing $M_k=0$.
The same induction restricted to $k<N$ proves the finite-prefix equivalence
and, before setting the last term to zero, the first-return identity.

Exact powers imply the semigroup law. The law conversely gives
$E_{n+1}=E_nE_1=E_nA$, so it implies exact powers. For arbitrary hidden
initialization, evaluating closure at $n=1$, $y_0=0$ gives $Bz_0=0$ for
every $z_0$, hence $B=0$. That condition also suffices directly from the
visible recurrence. Vanishing $BD^kG$ imposes a weaker prepared-state requirement.
''',('SR-05',))
claim(7,'Finite all-depth closure certificate',
      'Field modules; supplied monic annihilating polynomial p(D)=0, or finite-dimensional hidden H with d=dim H.',
      'BlockDynamics.memory_zero_of_annihilator;BlockDynamics.prepared_powers_iff_finrank_memory;BlockDynamics.prepared_powers_iff_finite_horizon;BlockDynamics.nonclosure_has_finite_feedback_witness',r'''
If a monic polynomial $p$ annihilates $D$, vanishing of $M_k$ for
$k<\deg p$ implies vanishing for all $k$. If $\dim H=d<\infty$, then
\[
E_n=A^n\ (\forall n)
\iff M_k=0\ (0\le k<d)
\iff E_n=A^n\ (0\le n\le d+1).
\]
The visible space need not be finite-dimensional. The case $d=0$ is included.
''',r'''
Divide $X^n$ by the monic $p$ to obtain a remainder $q_n$ of degree below
$\deg p$. Evaluation at $D$ gives $D^n=q_n(D)$ because $p(D)=0$.
Writing $q_n(D)$ as a finite linear combination of the powers $D^k$ below
$\deg p$ shows $BD^nG=0$. For finite-dimensional $H$, Cayley--Hamilton
provides the monic characteristic polynomial of $D$ with degree $d$.
SR-06 then yields both displayed equivalences. In dimension zero,
all maps through $H$ vanish and the empty list of memory tests is sufficient.
If exact closure fails, the contrapositive gives a nonzero memory map with
index below $d$. These tests concern complete linear maps, not sampled state
vectors or approximate floating-point agreement.
''',('SR-06',))
claim(8,'Canonical hidden state of a split compression',
      'Commutative-ring split C,R with CR=I; hidden H=ker C; finite-H corollary over a field.',
      'SplitCompression.block_synthesis_analysis;SplitCompression.block_analysis_synthesis;SplitCompression.block_powers_eq;SplitCompression.exact_powers_iff_canonical_memory_zero;SplitCompression.exact_powers_iff_canonical_finite_horizon',r'''
For $C:X\to Z$, $R:Z\to X$, $CR=I$, let $Q=I-RC$ and $H=\ker C$.
The maps
\[
x\longmapsto(Cx,Qx),\qquad (y,z)\longmapsto Ry+z
\]
are inverse linear maps between $X$ and $Z\times H$.
An endomorphism $T$ is conjugate to block dynamics with
\[
A=CTR,\quad B=CT\iota_H,\quad G=QTR,\quad D=QT\iota_H.
\]
Their prepared maps equal $CT^nR$. Hence exact compressed powers are
equivalent to zero canonical memory. If $\dim\ker C=d$, complete compressed
map tests through $d+1$ decide all depths.
''',r'''
$CQ=C-CRC=0$, so $Qx$ belongs to $H$. Synthesis after analysis gives
$RCx+Qx=x$. Conversely, for $z\in\ker C$, one has $C(Ry+z)=y$ and
$Q(Ry+z)=z$, using $QR=0$ and $Qz=z$. Conjugating $T$ by these inverse maps
gives the four displayed blocks; in the hidden blocks, $Q$ supplies the
required codomain. Induction transports powers under conjugacy.
The lift of $y$ is $(y,0)$ in these coordinates, so the prepared visible
map is precisely $CT^nR$. Apply SR-06 and SR-07. The construction uses the
actual discarded subspace and imposes no orthogonality on the chosen splitting.
''',('SR-06','SR-07'))
prose(r'''
\begin{example}[Delayed return and disconnected return]
On $\QQ^3$, set $T(y,z_1,z_2)=(z_1,z_2,y)$ and retain $y$.
Then $A=0$, $M_0=0$, $M_1=I$, and $E_1=E_2=0$ while $E_3=I$.
Two shallow exact checks cannot certify all depths without the dimension budget.
For another system, let $A=D=I$, $B(z_1,z_2)=z_1$, and $G(y)=(0,y)$.
Both couplings are nonzero but every $BD^kG$ vanishes. Prepared closure is exact,
while an arbitrary hidden initial first coordinate affects the next visible state.
\end{example}
''')

section('Finite behavioral models and minimality',r'''
Now work over a field and, for dimension statements, assume $\dim X<\infty$.
The allowed operations need not commute. Define
\[
N_r=\bigcap_{|w|\le r}\ker(OT_w),\qquad k=\dim\ker O.
\]
A finite horizon means bounded word length. It gives a finite enumeration of
constraints only when the operation alphabet is finite.
''')
claim(9,'Exact horizon and plateau certificate',
      'Finite-dimensional X over a field; arbitrary alphabet; all bounded-length words including empty word.',
      'FiniteHorizon.visibleKernel_succ;FiniteHorizon.visibleKernel_eq_invisible_of_plateau;FiniteHorizon.visibleKernel_stabilizes;FiniteHorizon.same_future_iff_bounded',r'''
$N_0=\ker O$ and
\[
N_{r+1}=\ker O\cap\bigcap_i T_i^{-1}N_r\subseteq N_r.
\]
One plateau $N_{r+1}=N_r$ implies $N_r=N$. In all cases $N_k=N$.
Thus equality of future observations through word length $k$ is equivalent
to equality for every finite word.
''',r'''
The empty word enforces $Ox=0$. A nonempty word $i::w$ of length at most
$r+1$ enforces $OT_wT_ix=0$, yielding the recursion. At a plateau, that
recursion shows $N_r$ is invariant under every $T_i$ and lies in $\ker O$.
By SR-04, $N_r\subseteq N$, while $N\subseteq N_r$ always holds.

Before reaching $N$, each successive inclusion must be strict, since an
equality would already certify the final subspace. Every strict inclusion
reduces dimension by at least one. Starting from dimension $k$ allows at
most $k$ such reductions; if $N_k$ has dimension zero it is already $N$,
and otherwise an earlier plateau has occurred. Applying the kernel identity
to $x-y$ proves the all-future comparison. No word-order commutativity is used.
''',('SR-04',))
claim(10,'Minimum exact state dimension',
      'Finite-dimensional X over a field; exact linear competitor q with qT_i=U_iq and Vq=O; finite Z only for final ambient comparison.',
      'BehavioralMinimality.quotient_is_observable;BehavioralMinimality.imageComparison;BehavioralMinimality.finrank_state_le_image;BehavioralMinimality.image_dimension_minimal_iff;BehavioralMinimality.minimalImageEquiv',r'''
The model $X/N$ is observable. Every exact competitor induces a unique
surjection $\Ran q\to X/N$, taking $qx$ to $[x]$. Therefore
\[
\dim(X/N)\le\dim\Ran q,
\]
with equality exactly when $\ker q=N$. In that case
$\Ran q\cong X/N$. If $Z$ is finite-dimensional, also
$\dim\Ran q\le\dim Z$. Surjectivity of $q$ onto $Z$ is not required.
''',r'''
If $qx=qy$, SR-04 gives $x-y\in N$, so $qx\mapsto[x]$ is well-defined.
It is linear and surjective because every class has a representative $x$.
Its values on the actual range force uniqueness.
Rank-nullity gives $\dim\Ran q=\dim X-\dim\ker q$ and
$\dim(X/N)=\dim X-\dim N$. Since $\ker q\subseteq N$, this proves the
inequality. Equality of dimensions forces equality of the nested finite-dimensional
subspaces; conversely their equality makes the comparison injective and hence
an equivalence. In the quotient model, an invisible class $[x]$ has every
$OT_wx=0$, so $x\in N$ and $[x]=0$. This establishes observability.
Unused coordinates in $Z$ do not change the reachable-image comparison.
''',('SR-04',))
claim(11,'Realizable finite observation tables',
      'Finite-dimensional X over a field; finite operation alphabet; k=dim ker O; target Y can be infinite-dimensional.',
      'FiniteObservableModel.mem_wordsUpTo;FiniteObservableModel.ker_complete_observation;FiniteObservableModel.observableEquiv;FiniteObservableModel.coordinate_all_future_fidelity;FiniteObservableModel.coordinate_dimension_le_exact_model',r'''
Let $H_kx=(OT_wx)_{|w|\le k}$ and $Z_k=\Ran H_k$. Then
$\ker H_k=N$ and $X/N\cong Z_k$. The formulas
\[
U_i(H_kx)=H_kT_ix,\qquad V(H_kx)=Ox
\]
define actual linear maps on $Z_k$ and preserve every finite future word.
This model has minimum exact dimension.
''',r'''
The recursively enumerated words are exactly those of length at most $k$.
SR-09 identifies the kernel of their combined observation map with $N$.
The first isomorphism theorem gives $X/N\cong\Ran H_k$. If $H_kx=H_ky$,
then $x-y\in N$; its invariance gives $H_kT_ix=H_kT_iy$, and
$N\subseteq\ker O$ gives $Ox=Oy$. Hence the displayed operations and readout
are well-defined on realizable tables. Induction proves
$U_wH_kx=H_kT_wx$ and $VU_wH_kx=OT_wx$ for words of any length.
Apply SR-10 to get minimality. An arbitrary table in the ambient coordinate
product need not be realizable and is not part of this constructed state space.
''',('SR-09','SR-10'))
claim(12,'Finite minimality certificate',
      'Field modules, not necessarily finite-dimensional; finite operation alphabet and finite horizon observation map H_r; actual maps q=F H_r, qT_i=U_iq, Vq=O.',
      'FiniteCertificate.certificate_kernel_eq;FiniteCertificate.certificate_same_future_iff;FiniteCertificate.certificateEquiv;FiniteCertificate.certificateEquiv_dynamics;FiniteCertificate.certificateEquiv_observation',r'''
For a finite operation alphabet, suppose a proposed representation satisfies
\[
q=F H_r,\qquad qT_i=U_iq,\qquad Vq=O.
\]
Then $\ker q=N$, regardless of whether $r$ reaches the a priori horizon.
If $q$ is surjective, it gives an equivalence $Z\cong X/N$ preserving
the observation and intertwining every operation. Without surjectivity,
the equivalence applies to $\Ran q$.
''',r'''
If $x\in N$, then every coordinate of $H_rx$ is zero, so $qx=FH_rx=0$.
This gives $N\subseteq\ker q$. Exact intertwining and output give the reverse
inclusion by SR-04. The equality makes $qx\mapsto[x]$ injective on the range
and surjective onto the quotient. Its inverse is the corresponding quotient
map induced by $q$. Evaluating both sides on $qx$ proves that the equivalence
intertwines $U_i$ with the quotient operations and preserves the readout.
The certificate has two roles: generation by observations prevents retention
of invisible distinctions, while exact dynamics and output prevent loss of
future-visible distinctions. Finite dimension is needed to guarantee that
such a certificate can be found at a bounded depth, not for its soundness.
''',('SR-04','SR-10'))
prose(r'''
\begin{example}[A noncommuting minimal model]
On $\QQ^3$, let $O(x,y,h)=x$,
$T_A(x,y,h)=(y,0,h)$, and $T_B(x,y,h)=(0,x,h)$.
The two operations do not commute: on $(1,0,0)$ their two compositions
give $(1,0,0)$ and $(0,0,0)$. The map $q(x,y,h)=(x,y)$ is generated by
$O$ and $OT_A$, intertwines both operations, and factors $O$.
It therefore has a depth-one certificate. The hidden coordinate $h$ is
invisible to every future word, and the minimum exact state dimension is two.
The current observation alone has dimension one and misses the distinction
between $(0,1,0)$ and zero, which one application of $T_A$ reveals.
\end{example}
''')
section('Quantitative discrete sufficiency',r'''
Let $q:X\to Z$ be a proposed representation, with true operations $T_i$,
reduced operations $U_i$, and readouts $O:X\to Y$, $V:Z\to Y$.
Define the step and word defects
\[
\delta_i=qT_i-U_iq,\qquad E_w=qT_w-U_wq.
\]
Algebraic identities require only the stated commutative-ring structure.
Quantitative estimates below use continuous linear maps over a nontrivially
normed field and their whole-map operator norms.
''')
claim(13,'Exact word-defect transport',
      'Commutative-ring modules; arbitrary chronological words and linear operations/representation/readouts.',
      'ApproximateAlgebra.wordDefect_cons;ApproximateAlgebra.wordDefect_append;ApproximateAlgebra.wordDefect_eq_sum;ApproximateAlgebra.output_defect_decomposition',r'''
One has $E_\varnothing=0$,
\[
E_{i::w}=E_wT_i+U_w\delta_i,\qquad
E_{u\mathbin{+\!+}v}=E_vT_u+U_vE_u.
\]
For $w=[i_1,\ldots,i_n]$ this yields
\[
E_w=\sum_{j=1}^n
U_{[i_{j+1},\ldots,i_n]}\delta_{i_j}T_{[i_1,\ldots,i_{j-1}]}.
\]
The output defect is $(O-Vq)T_w+VE_w$.
''',r'''
The recursive identity follows by adding and subtracting $U_wqT_i$ in
$qT_wT_i-U_wU_iq$. For concatenation, add and subtract $U_vqT_u$;
chronological order gives $T_{u\mathbin{+\!+}v}=T_vT_u$ and the analogous
identity for $U$. Inducting on the word expands one term per letter:
each step defect is transported by its true prefix and reduced suffix.
The empty word contributes no terms. Finally
$OT_w-VU_wq=(O-Vq)T_w+V(qT_w-U_wq)$.
Neither output mismatch nor accumulated dynamics mismatch is discarded.
''')
claim(14,'Heterogeneous operator budgets',
      'Normed spaces over nontrivially normed field; bounded maps; nonnegative letter bounds a_i,b_i,epsilon_i and eta≥‖O−Vq‖.',
      'ApproximateBounds.norm_wordError_le_budget;ApproximateBounds.budget_append;ApproximateBounds.norm_outputError_le;ApproximateBounds.norm_state_error_le',r'''
Suppose $\nn{T_i}\le a_i$, $\nn{U_i}\le b_i$, $\nn{\delta_i}\le\epsilon_i$.
Let $A_w,B_w$ be the products of the respective letter bounds and define
\[
D_\varnothing=0,\qquad D_{i::w}=D_wa_i+B_w\epsilon_i.
\]
Then $\nn{T_w}\le A_w$, $\nn{U_w}\le B_w$, $\nn{E_w}\le D_w$, and
\[
D_{u\mathbin{+\!+}v}=D_vA_u+B_vD_u.
\]
If $\nn{O-Vq}\le\eta$, then
\[
\nn{OT_w-VU_wq}\le\eta A_w+\nn V D_w.
\]
For arbitrary initial $x\in X$, $z\in Z$,
$\nn{qT_wx-U_wz}\le D_w\nn x+B_w\nn{qx-z}$.
''',r'''
Induction and submultiplicativity bound the two word operators by the
products. Apply the triangle inequality and submultiplicativity to the
first identity in SR-13 to obtain exactly the recursion for $D_w$.
Induction on $u$ proves the displayed scalar concatenation identity; it
tracks the same algebra as the exact defect identity, with nonnegative
factors preventing an inequality reversal. The output bound follows from
its exact decomposition in SR-13. For initialization, write
$qT_wx-U_wz=E_wx+U_w(qx-z)$ and bound both terms. These are operator budgets;
agreement on a finite set of sample vectors does not supply them.
''',('SR-13',))
claim(15,'Two-rate response and equal-rate limit',
      'Uniform nonnegative whole-map bounds a,b,epsilon; all finite words with length n; eta bound on output mismatch.',
      'ScalarBudgets.response_eq_sum;ScalarBudgets.response_mul_sub;ScalarBudgets.response_of_ne;ScalarBudgets.response_same_succ;StableApproximation.norm_wordError_uniform;StableApproximation.norm_outputError_uniform',r'''
For $H_0(a,b)=0$ and
$H_{n+1}(a,b)=aH_n(a,b)+b^n$,
\[
H_n(a,b)=\sum_{j=0}^{n-1}a^jb^{n-1-j},\qquad
(a-b)H_n=a^n-b^n.
\]
If $a\ne b$, $H_n=(a^n-b^n)/(a-b)$; for equal rates,
$H_{n+1}(a,a)=(n+1)a^n$. Uniform step bounds give
\[
\nn{E_w}\le\epsilon H_n(a,b),\qquad
\nn{OT_w-VU_wq}\le\eta a^n+\nn V\epsilon H_n(a,b).
\]
''',r'''
Induction proves the finite-sum formula: multiplying the old sum by $a$
and adjoining $b^n$ generates every term of the new sum. Multiplication
by $a-b$ telescopes, leaving $a^n-b^n$. Division is used only when the
rates are distinct. If they coincide, all $n+1$ terms of $H_{n+1}$ equal
$a^n$, including the zero-rate boundary with the usual $a^0=1$.
For uniform bounds, the heterogeneous budget becomes
$D_{i::w}=aD_w+b^{|w|}\epsilon$, so induction gives
$D_w=\epsilon H_{|w|}(a,b)$. Apply SR-14. The empty word has zero dynamics
defect and is handled by $H_0=0$, with no negative exponent required.
''',('SR-14',))
claim(16,'Nonexpansive and contractive continuations',
      'All true operation norms≤1; reduced operation norms≤1 or common b with 0≤b<1; uniform step/readout defect bounds.',
      'StableApproximation.norm_wordError_nonexpansive;StableApproximation.norm_outputError_nonexpansive;StableApproximation.norm_wordError_contractive;StableApproximation.norm_output_initial_contractive',r'''
If both families are nonexpansive, $\nn{E_w}\le n\epsilon$ and the output
defect is at most $\eta+\nn V n\epsilon$.
If the reduced family has a common bound $0\le b<1$, then
\[
\nn{E_w}\le\frac\epsilon{1-b},\qquad
\nn{OT_w-VU_wq}\le\eta+\nn V\frac\epsilon{1-b}.
\]
For arbitrary reduced initialization,
\[
\nn{OT_wx-VU_wz}
\le\left(\eta+\nn V\frac\epsilon{1-b}\right)\nn x
+\nn V b^n\nn{qx-z}.
\]
''',r'''
For $a=b=1$, the response sum has $n$ unit terms. For $a=1$ and $b<1$,
it is $1+b+\cdots+b^{n-1}\le1/(1-b)$. SR-15 gives the operator estimates.
For initialization, add $VU_w(qx-z)$ to the operator output error
applied to $x$, and use $\nn{U_w}\le b^n$.
The common bound concerns every allowed operation in the chosen norm.
Individual spectral radii do not imply a common product bound for a
noncommuting family. The nonexpansive estimate is an upper bound and does
not state that every such system accumulates error linearly.
''',('SR-15',))

section('Continuous flow and exact hidden memory',r'''
Let $L$ be a bounded real operator on a Banach space. Its flow is the actual
operator exponential $e^{tL}$. Boundedness allows differentiation of the
norm-convergent exponential series and integration of continuous operator
curves. Equalities in this section hold for all real $t$, using oriented
interval integrals when $t<0$.
''')
claim(17,'Actual flow and variation of constants',
      'Real Banach space; bounded autonomous D; continuous forcing f; differentiable actual z with z′=Dz+f at every real time.',
      'ContinuousFlow.hasDerivAt_flow;ContinuousFlow.flow_add;ContinuousFlow.variation_of_constants;ContinuousFlow.homogeneous_unique;ContinuousFlow.forced_unique',r'''
$\frac d{dt}e^{tD}=De^{tD}=e^{tD}D$,
$e^{(s+t)D}=e^{sD}e^{tD}$, and $e^{-tD}$ is the inverse flow.
Every actual curve satisfying $z'=Dz+f$ with continuous $f$ obeys
\[
z(t)=e^{tD}z(0)+\int_0^t e^{(t-s)D}f(s)\,ds.
\]
The initial value uniquely determines the homogeneous solution; two forced
solutions with the same forcing and initial value also agree.
''',r'''
Termwise differentiation of the exponential series gives both derivative
orders, since all powers of $D$ commute with $D$. The exponential addition
identity for commuting multiples of one bounded operator gives the flow law
and inverse. For fixed $t$, differentiate $e^{(t-s)D}z(s)$. The product rule
produces $-De^{(t-s)D}z(s)+e^{(t-s)D}(Dz(s)+f(s))$; commutation cancels
the generator terms. The remaining derivative is the continuous integrand
$e^{(t-s)D}f(s)$. The fundamental theorem of calculus on the oriented interval
gives the displayed identity. Setting $f=0$ yields the homogeneous formula.
Subtracting two forced solutions reduces uniqueness to that case.
The theorem starts from the differential equation, not from an assumed
integral representation.
''')
claim(18,'Power identities and exponential identities',
      'Bounded real generator algebras and bounded linear observation maps; norm-convergent exponentials; all real times or all natural powers.',
      'ContinuousFlow.mapped_flow_eq_iff_powers_eq;ContinuousFlow.sandwich_flow_zero_iff;ContinuousFlow.compressed_flow_iff_powers;ContinuousFlow.compressed_flow_defect',r'''
For bounded linear observation maps $K,J$ on bounded generator algebras,
\[
K(e^{tL})=J(e^{tD})\ (\forall t)
\iff K(L^n)=J(D^n)\ (\forall n).
\]
In particular, $Be^{tD}G=0$ for every $t$ exactly when $BD^nG=0$ for every $n$.
For $CR=I$, $A=CLR$, one has
\[
Ce^{tL}R=e^{tA}\ (\forall t)
\iff CL^nR=A^n\ (\forall n),
\]
and, with $Q=I-RC$,
\[
Ce^{(s+t)L}R-(Ce^{sL}R)(Ce^{tL}R)=Ce^{sL}Qe^{tL}R.
\]
''',r'''
The $n$th derivative at zero of $e^{tL}$ is $L^n$. Bounded linear maps
commute with these derivatives, so equality for all times implies equality
of every observed power. Conversely bounded linear maps commute with the
sum of the norm-convergent exponential series:
$K(e^{tL})=\sum_n(t^n/n!)K(L^n)$. Equality term by term gives equality of
the sums. Sandwiching and compression are bounded linear maps on the
corresponding operator spaces, so they give the specializations. For the
last identity, use the flow law and insert $I=RC+Q$ between the two flows.
The defect factorization itself does not need $CR=I$; that condition makes
$Q$ the discarded-state projector and ensures $E(0)=I$.
''',('SR-02','SR-17'))
claim(19,'Continuous hidden elimination',
      'Real Banach visible/hidden spaces; bounded autonomous blocks A,B,G,D; actual exponential full trajectory; arbitrary hidden initial state.',
      'ContinuousBlockDynamics.hasDerivAt_visible;ContinuousBlockDynamics.hidden_elimination;ContinuousBlockDynamics.continuous_memory_equation;ContinuousBlockDynamics.prepared_memory_equation',r'''
For $L(y,z)=(Ay+Bz,Gy+Dz)$ and
$(y(t),z(t))=e^{tL}(y_0,z_0)$,
\[
z(t)=e^{tD}z_0+\int_0^t e^{(t-s)D}Gy(s)\,ds.
\]
Writing $M(t)=Be^{tD}G$, the visible dynamics satisfy
\[
y'(t)=Ay(t)+Be^{tD}z_0+\int_0^t M(t-s)y(s)\,ds.
\]
Prepared initialization removes the term involving $z_0$.
''',r'''
Projecting the derivative of $e^{tL}$ onto the visible and hidden components
gives $y'=Ay+Bz$ and $z'=Gy+Dz$. The visible curve is continuous, so
$Gy$ is continuous forcing for the hidden equation. SR-17 yields the hidden
elimination formula. Bounded $B$ commutes with the interval integral,
giving the memory kernel in the visible equation. Taking $z_0=0$ removes
only the initialization term. No converse construction of a full trajectory
from an arbitrary Volterra solution is asserted here, and no unbounded
generator domain is present.
''',('SR-17',))
claim(20,'Continuous closure, finite moments, and jets',
      'Bounded real Banach block system; finite-dimensional hidden H only for finite certificates, or supplied monic annihilator.',
      'ContinuousBlockDynamics.prepared_exact_iff_memory_zero;ContinuousBlockDynamics.prepared_semigroup_iff_memory_zero;ContinuousBlockDynamics.prepared_exact_iff_finite_memory;ContinuousBlockDynamics.prepared_exact_iff_finite_derivatives;ContinuousBlockDynamics.first_return_derivative',r'''
Let $E(t)=Ce^{tL}R$. The following are equivalent:
\[
E(t)=e^{tA}\ (\forall t),\quad M(t)=0\ (\forall t),\quad
BD^kG=0\ (\forall k),\quad E(s+t)=E(s)E(t)\ (\forall s,t).
\]
If $\dim H=d$, each is equivalent to $BD^kG=0$ for $k<d$, or to
$E^{(n)}(0)=A^n$ for $n\le d+1$. If the first $k$ return moments vanish,
\[
E^{(k+2)}(0)-A^{k+2}=BD^kG.
\]
''',r'''
SR-18 converts prepared flow equality into prepared power equality and
memory flow vanishing into memory moment vanishing. SR-06 equates the
corresponding algebraic conditions, and SR-07 supplies the finite moment
criterion. Exact prepared flow gives its semigroup law. Conversely, if
$E$ is a semigroup, differentiating $E(s+t)=E(s)E(t)$ in $s$ at zero
gives $E'(t)=AE(t)$ because $E'(0)=CLR=A$ and $E(0)=I$.
The bounded-generator uniqueness theorem yields $E(t)=e^{tA}$.

Actual iterated derivatives of the exponential satisfy
$E^{(n)}(0)=CL^nR$. Applying the finite algebraic horizon and first-return
identity proves the jet statements. The leading Taylor coefficient has
the additional denominator $(k+2)!$; the derivative itself does not.
The visible Banach space can be infinite-dimensional. The finite tests
are whole-operator jet identities, not a finite list of sampled times.
''',('SR-06','SR-07','SR-18'))
prose(r'''
\begin{example}[A linear continuous memory kernel]
Take $V=\RR$, $H=\RR^2$, $A=0$, $B(z_1,z_2)=z_1$,
$G(y)=(0,y)$, and $D(z_1,z_2)=(z_2,0)$. Since $D^2=0$,
$e^{tD}(z_1,z_2)=(z_1+tz_2,z_2)$ and $M(t)=tI$.
The first two prepared jets agree with the reduced generator, while the
third derivative differs by $I$. Changing $D$ to zero leaves both boundary
couplings nonzero but makes the memory kernel identically zero.
Arbitrary hidden initialization still affects the visible initial derivative.
\end{example}
''')

section('Continuous approximate sufficiency',r'''
For bounded real generators $L$ on $X$ and $A$ on $Z$, and bounded $q:X\to Z$,
write $\delta=qL-Aq$ and $E(t)=qe^{tL}-e^{tA}q$.
Algebraic evolution identities hold for all real times. Norm bounds in this
section restrict to $t\ge0$, with growth assumptions on the nonnegative-time flows.
''')
claim(21,'Duhamel transport and composition',
      'Real Banach source/reduced spaces; bounded autonomous generators; bounded q and second representation p; all real times.',
      'ContinuousDefect.duhamel;ContinuousDefect.generatorDefect_zero_iff;ContinuousDefect.evolutionDefect_add;ContinuousDefect.generatorDefect_composite;ContinuousDefect.evolutionDefect_composite',r'''
One has the operator identity
\[
E(t)=\int_0^t e^{(t-s)A}\delta e^{sL}\,ds,
\]
and $\delta=0$ exactly when $E(t)=0$ for every $t$. Also
\[
E(s+t)=E(s)e^{tL}+e^{sA}E(t).
\]
For a second representation $p:Z\to W$ with generator $B$,
\[
\delta_{pq}=p\delta_q+\delta_pq,\qquad
E_{pq}(t)=pE_q(t)+E_p(t)q.
\]
''',r'''
Differentiate $F(s)=e^{(t-s)A}qe^{sL}$ using the product rule. Its derivative
is $e^{(t-s)A}(qL-Aq)e^{sL}$. Integrating from zero to $t$ gives
$F(t)-F(0)=E(t)$ and proves the formula. Zero generator defect therefore
forces zero evolution defect; differentiating $E$ at zero gives the
converse. The addition identity follows by adding and subtracting
$e^{sA}qe^{tL}$ and using the two flow laws.
For a composite representation, add and subtract $pAq$ in its generator
defect and $pe^{tA}q$ in its evolution defect. Both stages' contributions
remain explicit. Boundedness guarantees the continuous operator integrand.
''',('SR-17',))
claim(22,'Growth envelopes and scalar response',
      'Real Banach X,Z; bounded autonomous generators and representation/readouts; real rates a,b of either sign; t≥0; whole-flow bounds ‖e^{sL}‖≤M_L e^{as}, ‖e^{sA}‖≤M_A e^{bs} for every s≥0; nonnegative M_L,M_A,epsilon,eta and generator/readout defect bounds.',
      'ExponentialBudgets.response_of_ne;ExponentialBudgets.response_self;ContinuousApproximation.norm_evolution_le_response;ContinuousApproximation.norm_output_le_response',r'''
For $\nn\delta\le\epsilon$, put
\[
R(a,b,t)=\int_0^t e^{b(t-s)}e^{as}\,ds
=\begin{cases}(e^{at}-e^{bt})/(a-b),&a\ne b,\\ te^{at},&a=b.\end{cases}
\]
Then
\[
\nn{E(t)}\le M_LM_A\epsilon R(a,b,t).
\]
If $\nn{O-Vq}\le\eta$, the output defect $F(t)=Oe^{tL}-Ve^{tA}q$ obeys
\[
\nn{F(t)}\le\eta M_Le^{at}+\nn V M_LM_A\epsilon R(a,b,t).
\]
''',r'''
Apply the integral norm inequality and submultiplicativity to SR-21.
For $0\le s\le t$, the integrand norm is at most
$M_Ae^{b(t-s)}\epsilon M_Le^{as}$. Integration gives the first estimate.
Factoring $e^{bt}$ and integrating $e^{(a-b)s}$ gives the distinct-rate
formula; for equal rates the integrand is constant $e^{at}$.
The output decomposition is
$F(t)=(O-Vq)e^{tL}+VE(t)$, giving the stated bound.
The same argument works with continuous nonnegative envelope functions
$u,v$ on the interval, replacing the scalar response by
$\int_0^tv(t-s)u(s)\,ds$. In particular these assumptions concern actual
flow norms, not just eigenvalues of the generators.
''',('SR-21',))
claim(23,'Uniform continuous stability and initialization',
      'True flow bounded by M_L; reduced flow bounded by M_A exp(−rt), r>0, for t≥0; generator/readout allowances; arbitrary initial reduced z.',
      'ContinuousStability.norm_evolution_uniform;ContinuousStability.norm_output_uniform;ContinuousStability.norm_initialization_uniform;ContinuousStability.norm_composite_evolution',r'''
If $\nn{e^{tL}}\le M_L$ and $\nn{e^{tA}}\le M_Ae^{-rt}$ with $r>0$, then
\[
\nn{E(t)}\le\frac{M_LM_A\epsilon}{r},\qquad
\nn{F(t)}\le\eta M_L+\nn V\frac{M_LM_A\epsilon}{r}.
\]
For arbitrary $x,z$,
\begin{align*}
\nn{Oe^{tL}x-Ve^{tA}z}
&\le\left(\eta M_L+\nn V\frac{M_LM_A\epsilon}{r}\right)\nn x\\
&\quad+\nn V M_Ae^{-rt}\nn{qx-z}.
\end{align*}
Composition through a second representation propagates allowances with
its explicit map norm, as in SR-21.
''',r'''
Use SR-22 with $a=0$, $b=-r$. Its response equals
$(1-e^{-rt})/r\le1/r$ for $t\ge0$. This gives the evolution and output
operator bounds. The initialization error decomposes into $F(t)x$ plus
$Ve^{tA}(qx-z)$, which proves the displayed estimate. The first allowance
must be multiplied by $\nn x$ because it is an operator estimate.
For another representation $p$ with its own evolution defect, SR-21 gives
$\nn{E_{pq}(t)}\le\nn p\nn{E_q(t)}+\nn{E_p(t)}\nn q$.
This retains error introduced at both stages, rather than identifying
their budgets with a single unqualified small quantity.
''',('SR-21','SR-22'))
claim(24,'Sharp response and small-defect failure',
      'Actual real scalar bounded generators, q=I; t≥0; b≤a for equality and epsilon>0 for counterexample.',
      'ContinuousApproxExamples.scalar_response_sharp;ContinuousApproxExamples.unstable_generator_exact;ContinuousApproxExamples.unstable_error_exact;ContinuousApproxExamples.unstable_error_unbounded',r'''
For scalar generators $a\ge b$,
\[
|e^{at}-e^{bt}|=(a-b)R(a,b,t),
\]
so the response estimate is attained. For every $\epsilon>0$, choosing
$L=\epsilon I$, $A=0$, $q=I$ gives
\[
\nn\delta=\epsilon,\qquad \nn{E(t)}=e^{\epsilon t}-1\ge\epsilon t.
\]
Its evolution defect exceeds every fixed bound at some nonnegative time.
''',r'''
The scalar exponential is the actual flow by the homogeneous ODE uniqueness
theorem. For $a>b$, the response formula immediately gives the equality;
for $a=b$, both sides vanish. In the second example, the generator defect
is multiplication by $\epsilon$, while the evolution defect is multiplication
by $e^{\epsilon t}-1$. The elementary exponential inequality
$e^u\ge1+u$ for $u\ge0$ gives the lower bound. Taking $t$ sufficiently
large makes it exceed any prescribed real bound. Thus a small generator
defect alone does not supply uniform accuracy. The hypothesis of a bounded
true flow in SR-23 fails here.
''',('SR-22','SR-23'))

section('Orthogonal globalization and conditioning',r'''
Let $R\subseteq K$ be subspaces of a real inner-product space $V$, both admitting
orthogonal projections. Define the actual maps
\[
r(v)=P_Rv,\quad o(v)=(P_K-P_R)v,\quad i(v)=(I-P_K)v.
\]
They distinguish realized data, compatible obstruction, and incompatibility.
In a globalization presentation use $R=\Ran A$, $K=\ker\delta$ with $\delta A=0$.
''')
claim(25,'Unique three-component geometry',
      'Real inner-product V; nested subspaces R≤K both with orthogonal projections; arbitrary v and represented candidate u∈R.',
      'OrthogonalResolution.components_sum;OrthogonalResolution.unique_components;OrthogonalResolution.norm_sq_components;OrthogonalResolution.candidate_error_sq;OrthogonalResolution.infDist_sq_decomposition',r'''
The components lie in $R$, $K\cap R^\perp$, and $K^\perp$, respectively,
are pairwise orthogonal, and give the unique decomposition
$v=r(v)+o(v)+i(v)$. Furthermore,
\[
\nn v^2=\nn r^2+\nn o^2+\nn i^2,\qquad
\dist(v,R)^2=\nn o^2+\nn i^2.
\]
For any $u\in R$,
\[
\nn{v-u}^2=\dist(v,R)^2+\nn{r(v)-u}^2.
\]
Thus $r(v)$ is the unique nearest represented vector.
''',r'''
Nested projections satisfy $P_RP_K=P_R$. Hence
$P_Kv-P_Rv$ lies in $K$ and is orthogonal to $R$; the last component is
orthogonal to $K$. Their definitions sum to $v$ and yield pairwise
orthogonality. In any competing decomposition, projection onto $R$
selects its first term and projection onto $K$ selects the first two,
so all components are forced. Pythagoras gives the norm identities.
For $u\in R$, the residual $v-r(v)$ is orthogonal to $r(v)-u$,
so the candidate identity follows. It proves optimality and uniqueness,
and taking the infimum over actual $u\in R$ proves the distance formula.
Each component map is an orthogonal projection onto its displayed sector
and consequently is nonexpansive.
''')
claim(26,'Harmonic realization of the obstruction quotient',
      'Real linear presentation δA=0; projections on actual R=range A and K=kerδ; source G only needs real module structure.',
      'HilbertGlobalization.obstructionEquivHarmonic;HilbertGlobalization.class_zero_iff_component_zero;HilbertGlobalization.same_class_iff_same_harmonic;HilbertGlobalization.exists_best_global_image',r'''
The same quotient $\mathcal H=K/R$ from SR-03 is linearly equivalent to
$K\cap R^\perp$ by
\[
[v]\longmapsto v-P_Rv\quad(v\in K).
\]
It is inverse to the quotient map restricted to the harmonic subspace.
For compatible data, the class is zero exactly when $o(v)=0$; equality
of classes is equality of harmonic representatives. The best image $P_Rv$
has an actual source under $A$.
''',r'''
Adding a vector of $R$ leaves $v-P_Rv$ unchanged, so the map descends to
$K/R$. Its values lie in $K\cap R^\perp$ by SR-25. For harmonic $h$,
$P_Rh=0$, so its class maps back to $h$. For compatible $v$, the difference
$v-(v-P_Rv)=P_Rv$ lies in $R$, so the reverse roundtrip returns $[v]$.
The inverse laws prove the equivalence and both class criteria.
Since $P_Rv$ belongs to the actual range, some $g$ satisfies $Ag=P_Rv$.
This is image existence; uniqueness of $g$ requires the separate injectivity
condition in SR-03. No norm isometry is inferred from linear equivalence
alone; the metric statement is proved in SR-33.
''',('SR-03','SR-25'))
claim(27,'Residual bounds retain conditioning and obstruction',
      'Same projection presentation; bounded δ; sigma>0 with sigma‖x‖≤‖δx‖ on K⊥; arbitrary data.',
      'HilbertConditioning.inconsistency_residual;HilbertConditioning.inconsistency_le_residual;HilbertConditioning.conditioned_distance_sq;HilbertConditioning.obstruction_lower_bound;HilbertConditioning.compatible_distance',r'''
If $\sigma\nn x\le\nn{\delta x}$ for $x\in K^\perp$ and $\sigma>0$, then
\[
\delta i(v)=\delta v,\qquad
\nn{i(v)}\le\frac{\nn{\delta v}}\sigma,
\]
and
\[
\nn{o(v)}\le\dist(v,R),\qquad
\dist(v,R)^2\le\nn{o(v)}^2+\left(\frac{\nn{\delta v}}\sigma\right)^2.
\]
For compatible data, $\dist(v,R)=\nn{o(v)}$.
''',r'''
The component $P_Kv$ is in $\ker\delta$, so
$\delta(v-P_Kv)=\delta v$. Apply coercivity to $i(v)\in K^\perp$ and divide
by the positive $\sigma$. SR-25 gives the exact sum of two nonnegative
squares, proving both the lower bound and conditioned upper bound.
If $\delta v=0$, then $v\in K$ and $i(v)=0$, giving equality.
In particular, a compatibility residual bounds only inconsistency. A
residual-only global bound needs a vanished obstruction or exactness
$R=K$. The condition on $\sigma$ is independent of the size of a particular
measured residual and cannot be inferred from that measurement.
''',('SR-25',))
claim(28,'Finite conditioning and realizable enlargement',
      'Finite-dimensional real V for existence/characterization; fixed metric and K with projected R0≤R1≤K for refinement.',
      'HilbertConditioning.exists_coercivity_finite;FiniteGlobalization.finite_residual_bound_iff_exact;GlobalizationRefinement.obstruction_refinement_sq;GlobalizationRefinement.distance_refinement_sq;GlobalizationExamples.no_uniform_conditioning_over_scalar_family',r'''
In finite dimension some $\sigma>0$ satisfies SR-27. Under $\delta A=0$,
\[
\exists c>0\ \forall v:\dist(v,\Ran A)\le c\nn{\delta v}
\iff\Ran A=\ker\delta.
\]
For projected $R_0\subseteq R_1\subseteq K$ in a fixed metric, put
$g(v)=(P_{R_1}-P_{R_0})v$. Then
\[
\nn{o_0(v)}^2=\nn{o_1(v)}^2+\nn{g(v)}^2,
\quad
\dist(v,R_0)^2=\dist(v,R_1)^2+\nn{g(v)}^2.
\]
No uniform conditioning constant exists across all nonzero scalar compatibility maps.
''',r'''
Restrict $\delta$ to $K^\perp$. It is injective: a zero image lies in both
$K$ and $K^\perp$. A finite-dimensional injective linear map has a positive
lower norm bound, giving $\sigma$; the zero domain is harmless and permits
any positive choice. If the residual-only inequality holds, every $v\in K$
has zero distance to $\Ran A$. Finite-dimensional ranges are closed, so
$v\in\Ran A$. Conversely exactness removes $o(v)$ in SR-27.

Nested orthogonal projections split $o_0(v)=o_1(v)+g(v)$ into orthogonal
sectors, and the inconsistency component stays fixed. Pythagoras gives
both refinement identities. For the scalar family $\delta_s(x)=sx$, $s>0$,
take $R=0$ and $v=1$. The reconstruction distance is one and the residual
is $s$. For any proposed common $c$, choosing $s$ sufficiently small
violates $1\le cs$. The theorem guarantees a constant per presentation,
not a common constant across degenerating presentations.
''',('SR-25','SR-27'))
prose(r'''
\begin{example}[A complete error split]
For $A(g)=(g,0,0)$, $\delta(x,y,z)=2z$, and $v=(3,4,5)$,
the components are $(3,0,0)$, $(0,4,0)$, and $(0,0,5)$.
The squared reconstruction distance is $41=16+25$. The compatibility
residual has squared norm $100$, and $\sigma=2$ is sharp on $K^\perp$.
Thus the conditioned upper bound is attained: $16+100/4=41$.
\end{example}
''')

section('Canonical minimum-norm reconstruction',r'''
Let $A:G\to V$ be bounded between real Hilbert spaces, with actual closed
range $R=\Ran A$. Write $N_A=\ker A$ and $S=N_A^\perp$.
Closedness is a substantive hypothesis for a bounded exact inverse. It will
be removed for regularized recovery in the following sections.
''')
claim(29,'Constructed bounded canonical inverse',
      'Bounded real Hilbert operator A with actual closed range; core needs complete source/range and orthogonal projections.',
      'MinimumNormReconstruction.restrictionEquiv;MinimumNormReconstruction.image_comp_recover;MinimumNormReconstruction.recover_comp_image;MinimumNormReconstruction.recover_unique;ClosedRangeReconstruction.closedRecover',r'''
Restriction $A_S:S\to R$ is a bounded linear bijection with bounded inverse.
Define
\[
B=\iota_S A_S^{-1}P_R.
\]
Then $AB=P_R$, $BA=P_S$, $ABA=A$, and $BAB=B$.
Its two projections are symmetric, $\ker B=R^\perp$, and $\Ran B=S$.
The best-image identity $AB=P_R$ and the condition $\Ran B\subseteq S$
uniquely determine $B$.
''',r'''
The restriction is injective because $S\cap\ker A=0$. Every $Ag\in R$
equals $AP_Sg$, so it is surjective. Closed $R$ and closed $S$ are Banach
spaces; the bounded inverse theorem supplies $A_S^{-1}$ as an actual
continuous linear inverse. The definition then gives $AB=P_R$.
For $g$, $BAg$ is the unique element of $S$ with image $Ag$, namely
$P_Sg$. The two inverse identities imply the generalized inverse laws.
Orthogonal projections are symmetric, proving the symmetry conditions.
The definition and injectivity of $A_S^{-1}$ identify the kernel and range.
Finally, if $B'$ has the same best image and values in $S$, then
$B'v-Bv\in S\cap\ker A$ for each $v$, hence it is zero.
This construction is the classical Moore--Penrose inverse with the
actual range and source ambiguity retained.
''')
claim(30,'All least-squares sources and unique minimum norm',
      'Same real Hilbert closed-range constructor; arbitrary data v, candidate g and arbitrary deterministic noise e.',
      'MinimumNormOptimality.candidate_error_decomposition;MinimumNormOptimality.all_least_squares_sources;MinimumNormOptimality.unique_minimum_norm_least_squares;MinimumNormOptimality.exact_source_recovery_iff;MinimumNormOptimality.noisy_source_error_sq',r'''
For every source $g$,
\[
\nn{v-Ag}^2=\dist(v,R)^2+\nn{A(g-Bv)}^2.
\]
All least-squares minimizers are $Bv+k$ with $k\in\ker A$.
Among them $Bv$ is the unique minimum-norm source. Exact source recovery
$BAg=g$ holds exactly for $g\in S$. For data $Ag+e$,
\[
\nn{B(Ag+e)-g}^2=\nn{Be}^2+\nn{P_{N_A}g}^2.
\]
''',r'''
$ABv=P_Rv$, so SR-25's candidate identity with $u=Ag$ proves the first
formula. Equality to the minimum image error is equivalent to
$A(g-Bv)=0$, yielding exactly the affine family of minimizers.
Since $Bv\in S$ and $k\in N_A$, Pythagoras gives
$\nn{Bv+k}^2=\nn{Bv}^2+\nn k^2$. It proves minimum norm and uniqueness.
The identity $BA=P_S$ proves the exact recovery criterion.
For noisy data, linearity gives $B(Ag+e)-g=Be-P_{N_A}g$.
The first term belongs to $S$ and the second to $N_A$, so they are
orthogonal. This last identity does not assume a statistical noise model.
It shows explicitly which source content the operator cannot identify.
''',('SR-25','SR-29'))
claim(31,'Source conditioning and solver ambiguity',
      'Closed-range A; alpha>0 with alpha‖g‖≤‖Ag‖ on S; computed source h may contain a kernel component.',
      'SourceConditioning.exists_source_coercivity;SourceConditioning.recover_opNorm_bound;SourceConditioning.noisy_source_bound_sq;SourceConditioning.candidate_source_bound_sq;ReconstructionGlobalization.two_condition_reconstruction',r'''
Some $\alpha>0$ satisfies $\alpha\nn g\le\nn{Ag}$ on $S$, and any supplied
such constant gives $\nn B\le1/\alpha$. Therefore
\[
\nn{B(Ag+e)-g}^2\le(\nn e/\alpha)^2+\nn{P_{N_A}g}^2.
\]
For an arbitrary computed source $h$,
\[
\nn{h-Bv}^2
\le\left(\frac{\nn{Ah-P_Rv}}\alpha\right)^2+\nn{P_{N_A}h}^2.
\]
If also $\delta A=0$, a compatibility constant $\sigma$ bounds the local
error as in SR-27. The constants $\alpha$ and $\sigma$ have separate roles.
''',r'''
The bounded inverse on $S$ gives
$\nn g\le\nn B\nn{Ag}$. Taking, for example,
$\alpha=1/(\nn B+1)>0$ handles also the zero complement and proves
existence. For a supplied constant, apply it to $Bv\in S$:
$\alpha\nn{Bv}\le\nn{ABv}=\nn{P_Rv}\le\nn v$.
Take the operator norm and combine with SR-30 for the noisy bound.
For a computed $h$, split
$h-Bv=(P_Sh-Bv)+P_{N_A}h$ orthogonally. Coercivity bounds the first term
by $\nn{Ah-P_Rv}/\alpha$ because $AP_Sh=Ah$.
The compatibility operator bounds distance of local data to realizability;
the forward operator bounds source amplification. Neither condition
establishes the other. A small fit without control of the computed kernel
component does not certify the minimum-norm source.
''',('SR-27','SR-29','SR-30'))
claim(32,'Closed range is equivalent to bounded recovery',
      'Bounded A between real Hilbert spaces; actual range closedness; bounded recovery BA=P_S or off-kernel coercivity.',
      'ClosedRangeReconstruction.closed_range_iff_coercivity;ClosedRangeReconstruction.bounded_recovery_iff_closed_range;ClosedRangeReconstruction.nonclosed_no_bounded_recovery;ReconstructionExamples.no_uniform_source_conditioning',r'''
The following conditions are equivalent:
\[
\Ran A\text{ is closed};\qquad
\exists\alpha>0:\alpha\nn g\le\nn{Ag}\ (g\in S);
\qquad \exists B\text{ bounded}:BA=P_S.
\]
Thus a nonclosed range admits no bounded exact identifiable-source recovery.
Finite-dimensional source or target supplies closed range. There is no common
inverse-sensitivity constant across all nonzero real scalar forward maps.
''',r'''
Closed range gives the bounded constructor and coercivity by SR-29--SR-31.
Conversely suppose coercivity holds. If $Ag_n$ converges in $V$, replace
$g_n$ by $P_Sg_n$ without changing its image. Coercivity makes this source
sequence Cauchy. Completeness gives a limit $g\in S$, and continuity gives
the image limit $Ag\in\Ran A$. Hence the range is closed.
If bounded $B$ satisfies $BA=P_S$, then for $g\in S$,
$\nn g=\nn{BAg}\le\nn B\nn{Ag}$. The same positive choice
$1/(\nn B+1)$ gives coercivity. Finite-dimensional image subspaces are
closed in a normed space. Finally $A_cg=cg$, $c>0$, has canonical inverse
$B_cv=v/c$. At $v=c$, data tend to zero with $c$ while the recovered
source remains one, ruling out a common constant as $c\downarrow0$.
''',('SR-29','SR-31'))
prose(r'''
\begin{example}[Source and image are different optima]
Let $A(g_1,g_2)=(g_1+g_2,0,0)$ and $v=(3,4,5)$.
The best image is $(3,0,0)$, with the same squared local error $41$.
The minimum-norm source is $(3/2,3/2)$ of squared norm $9/2$.
The source $(3,0)$ gives the same best image but has squared norm $9$.
Their difference $(3/2,-3/2)$ is kernel ambiguity, not local obstruction.
\end{example}
''')

section('Intrinsic metric obstruction and transport',r'''
Retain the globalization presentation $\delta A=0$, the actual projected
subspaces $R=\Ran A\subseteq K=\ker\delta$, and the same algebraic quotient
$\mathcal H=K/R$. Its seminorm is the quotient seminorm induced by the
ambient metric. We prove the harmonic equivalence respects that preexisting
seminorm, rather than defining a new norm to match its answer.
''')
claim(33,'Native quotient norm and isometry',
      'Real inner-product V; R=range A,K=kerδ both projected; δ bounded, δA=0; native quotient seminorm.',
      'MetricObstruction.quotientToHarmonic_norm;MetricObstruction.obstructionIsometry;MetricObstruction.norm_class_eq_infDist;MetricObstruction.distance_classes;MetricObstruction.quotient_inner_preserved',r'''
The equivalence $K/R\cong K\cap R^\perp$ in SR-26 is a linear isometry.
For compatible $v,w$,
\[
\nn{[v]}=\nn{o(v)}=\dist(v,R),\qquad
\dist([v],[w])=\dist(v-w,R).
\]
The quotient norm detects zero classes. Its standard quotient inner
product is preserved when the induced projection structure in $K$ is used.
''',r'''
Let $h$ be the harmonic representative of a class $z$. For any compatible
representative $v$ of $z$, its harmonic component is $h$, and the
nonexpansive harmonic projection gives $\nn h\le\nn v$.
Taking the infimum over representatives proves $\nn h\le\nn z$.
Conversely $h$ itself represents $z$, so the quotient map's norm bound
gives $\nn z\le\nn h$. This proves isometry against the existing quotient
seminorm. The compatible distance formula follows from SR-25, and
distances of classes follow by applying it to $v-w$.
Zero norm implies zero harmonic vector and hence zero class by the inverse
laws. Orthogonal projection onto $R$ restricts to $K$, constructing the
quotient inner-product structure there. A real linear isometry preserves
its inner product by the polarization identity.
''',('SR-25','SR-26'))
claim(34,'Minimum representatives and intrinsic class of data',
      'Same projected real presentation; arbitrary v for projected class c(v)=[P_Kv]; complete/closed source range only when canonical inverse B used.',
      'MetricRepresentatives.unique_minimum_representative;MetricRepresentatives.representative_error_energy;IntrinsicGlobalization.projectedClass_opNorm_le;IntrinsicGlobalization.intrinsic_distance_sq;IntrinsicGlobalization.realizable_iff_class_and_residual_zero;IntrinsicGlobalization.intrinsic_candidate_total_error',r'''
Every class $z$ has a unique compatible minimum-norm representative $s(z)$,
and every compatible representative $v$ satisfies
\[
\nn v^2=\nn z^2+\nn{v-s(z)}^2.
\]
For arbitrary data define $c(v)=[P_Kv]$. This is nonexpansive and
\[
\dist(v,R)^2=\nn{c(v)}^2+\nn{i(v)}^2.
\]
The datum is realizable exactly when both $c(v)=0$ and $\delta v=0$.
When the canonical inverse exists,
\[
\nn{v-Ag}^2=\nn{c(v)}^2+\nn{i(v)}^2+\nn{A(g-Bv)}^2.
\]
''',r'''
Take $s(z)$ to be its harmonic representative from SR-33. The difference
between any other compatible representative and $s(z)$ lies in $R$,
which is orthogonal to the harmonic sector. Pythagoras gives the first
formula, including unique attainment of the minimum.
The composition of $P_K$ and the quotient map is bounded by one; its
harmonic representative is $o(v)$. SR-25 and SR-33 give the intrinsic
distance identity. If both displayed tests vanish, then $v\in K$ and
its obstruction class is zero, so SR-03 supplies a source. Realizability
implies both tests directly. Finally combine the candidate identity
of SR-30 with the intrinsic distance split. The minimum representative
of an obstruction class belongs to local data space; it is a different
construction from the minimum-norm global source $Bv$.
''',('SR-03','SR-25','SR-30','SR-33'))
claim(35,'Bounded quotient transport and reflection',
      'Commuting linear presentation maps; whole local-map norm bound C≥0; reverse presentation with bound M>0 and induced left inverse for two-sided estimate.',
      'MetricObstructionTransport.obstructionMap_norm_le;MetricObstructionTransport.boundedObstructionMap_opNorm;MetricObstructionTransport.reverse_bound;MetricObstructionTransport.two_sided_bound',r'''
A presentation map with $\nn{Lv}\le C\nn v$ induces the same quotient map
as in SR-03, now satisfying
\[
\nn{\overline Lz}\le C\nn z.
\]
If a reverse presentation has bound $M>0$ and its quotient map is a left
inverse of $\overline L$, then
\[
\frac{\nn z}{M}\le\nn{\overline Lz}\le C\nn z.
\]
The corresponding class distances satisfy the same bounds.
''',r'''
For any representative $v$ of $z$, the quotient norm of $[Lv]$ is at most
$\nn{Lv}\le C\nn v$. Infimizing over representatives gives the upper bound
and supplies a bounded linear map with exactly the algebraic action of
SR-03. Alternatively, the minimum representative from SR-34 realizes the
infimum and yields it immediately. Apply the reverse bound to
$\overline Lz$: the left-inverse identity gives
$\nn z\le M\nn{\overline Lz}$. Division by positive $M$ proves the lower
bound. Apply the bounds to $z-w$ for distances. Forward boundedness alone
does not prove reflection; the reverse identity is genuine additional data.
''',('SR-03','SR-33','SR-34'))
claim(36,'Metric refinement and nonclosed boundary',
      'Projected nested R0≤R1≤K in fixed real metric for energy; arbitrary submodule R in real normed space for nonclosed seminorm boundary.',
      'MetricRefinement.refinementMap_surjective;MetricRefinement.refinementMap_norm_le;MetricRefinement.quotient_refinement_energy;QuotientMetricBoundaries.zero_norm_iff_closure;QuotientMetricBoundaries.nonclosed_nonzero_zero_norm;QuotientMetricBoundaries.norm_detects_zero_iff_closed',r'''
Range enlargement induces a surjective contraction $F:K/R_0\to K/R_1$.
For the old minimum representative $s_0(z)$,
\[
\nn z^2=\nn{Fz}^2+\nn{(P_{R_1}-P_{R_0})s_0(z)}^2.
\]
Without a closedness or projection hypothesis, a general quotient instead has
\[
\nn{[v]}=0\iff v\in\cl R,\qquad [v]=0\iff v\in R.
\]
Thus its seminorm detects zero exactly when $R$ is closed. Nonclosed range
can leave a nonzero class of zero seminorm.
''',r'''
The larger realization submodule contains the smaller, so the identity
on $K$ descends to a surjection of quotients. Every old representative is
a new representative, proving contraction by the quotient infimum.
For the energy identity apply the orthogonal refinement identity in
SR-28 to $s_0(z)$, whose old norm is $\nn z$. The new harmonic component
represents $Fz$ and has norm $\nn{Fz}$ by SR-33.

For any submodule, the native quotient seminorm equals distance to that
submodule. Zero distance is equivalent to membership in its closure by
the metric closure criterion; algebraic quotient zero remains actual
membership. If $R$ is nonclosed, choose $v\in\cl R\setminus R$.
Its class is nonzero with zero seminorm. Conversely closedness makes
zero distance imply membership. This is why the projection hypotheses
in the preceding metric theory cannot be discarded silently.
''',('SR-28','SR-33'))
prose(r'''
\begin{example}[A metric must survive its coordinate change]
For $K=\{(x,y,0)\}$ and $R=\spanof\{(1,0,0)\}$, take the compatible basis
$b_1=(1,0,0)$, $b_2=(1,2,0)$. Its Gram matrix is
$\bigl(\begin{smallmatrix}1&1\\1&5\end{smallmatrix}\bigr)$.
The vector $(3,4,0)$ has coordinates $(1,2)$; its harmonic representative
$(0,4,0)$ has coordinates $(-2,2)$ and squared norm $16$ in that Gram metric.
Computing with an untransported coordinate Euclidean metric would change
the problem. Redundant or nonorthogonal coordinates do not license such a change.
\end{example}
''')

section('Tikhonov construction, bias, and perturbation',r'''
Fix a bounded operator $A:G\to V$ between real Hilbert spaces, without
assuming closed range. For $\lambda>0$, put
\[
N_\lambda=A^*A+\lambda I,\qquad R_\lambda=N_\lambda^{-1},\qquad
B_\lambda=R_\lambda A^*.
\]
The inverse is constructed from coercivity. It is not supplied as a
certificate premise. Here $A^*$ is the actual Hilbert adjoint.
''')
claim(37,'Constructed normal inverse and energy',
      'Real Hilbert G,V; actual bounded A and lambda>0; no finite dimension or closed range.',
      'TikhonovConstruction.normalForm_coercive;TikhonovConstruction.normalEquiv_apply;TikhonovConstruction.normal_resolvent;TikhonovConstruction.resolvent_normal;TikhonovConstruction.normal_equation;TikhonovConstruction.solution_energy',r'''
$N_\lambda$ is a bounded bijection with bounded inverse $R_\lambda$.
For $x_\lambda=B_\lambda v$,
\[
N_\lambda x_\lambda=A^*v,\qquad
A^*(Ax_\lambda-v)+\lambda x_\lambda=0,
\]
and
\[
\nn{Ax_\lambda}^2+\lambda\nn{x_\lambda}^2
=\ip v{Ax_\lambda}.
\]
''',r'''
The bilinear form
$b(x,y)=\ip{Ax}{Ay}+\lambda\ip xy$ is bounded and satisfies
$b(x,x)\ge\lambda\nn x^2$. Lax--Milgram gives a continuous linear
equivalence from the source to itself under the Riesz identification.
The adjoint identity identifies its map with $A^*A+\lambda I$.
The two inverse laws give an actual resolvent. Applying one inverse law
to $A^*v$ yields the normal equation. Taking its inner product with
$x_\lambda$ and using $\ip{A^*v}{x_\lambda}=\ip v{Ax_\lambda}$ gives
the energy identity. Strictly positive $\lambda$ supplies coercivity
even if $A$ has a nontrivial kernel or a nonclosed range.
''')
claim(38,'Objective optimality and sharp fixed-parameter bounds',
      'Same real Hilbert bounded A with lambda>0; arbitrary source candidate x and data v; actual normal residual.',
      'TikhonovOptimality.objective_increment;TikhonovOptimality.unique_minimizer;TikhonovBounds.resolvent_opNorm_bound;TikhonovBounds.regularized_opNorm_bound;TikhonovBounds.approximate_solver_bound;TikhonovBounds.source_kernel_orthogonal',r'''
For $F_\lambda(v,x)=\nn{Ax-v}^2+\lambda\nn x^2$,
\[
F_\lambda(v,x)=F_\lambda(v,x_\lambda)
+\nn{A(x-x_\lambda)}^2+\lambda\nn{x-x_\lambda}^2.
\]
Thus $x_\lambda$ is the unique minimizer and lies in $(\ker A)^\perp$.
The whole-map bounds are
\[
\nn{R_\lambda}\le1/\lambda,\qquad
\nn{B_\lambda}\le\frac1{2\sqrt\lambda},\qquad
\nn{AB_\lambda v}\le\nn v,\quad\nn{AB_\lambda v-v}\le\nn v.
\]
For $r=N_\lambda x-A^*v$, one has
$x-x_\lambda=R_\lambda r$ and $\nn{x-x_\lambda}\le\nn r/\lambda$.
''',r'''
Expand both squared norms around $x_\lambda$. Their cross terms combine to
\[
2\ip{A^*(Ax_\lambda-v)+\lambda x_\lambda}{x-x_\lambda},
\]
which vanishes by SR-37. The remaining positive terms prove the increment
identity and uniqueness. Taking the normal equation against a kernel
vector $k$ yields $\lambda\ip{x_\lambda}k=0$, proving source orthogonality.

For $y=R_\lambda r$, its energy gives
$\lambda\nn y^2\le\ip ry\le\nn r\nn y$, hence the resolvent bound.
For $x_\lambda$, set $u=\nn{Ax_\lambda}$. The energy gives
$u^2+\lambda\nn{x_\lambda}^2\le\nn v\,u$.
Completing the square in $u$ yields
$4\lambda\nn{x_\lambda}^2\le\nn v^2$ and also $u\le\nn v$.
Comparing the minimum objective with $F_\lambda(v,0)=\nn v^2$ bounds the
fitting residual. Subtract the exact normal equation from the computed
one and apply the resolvent for the correction identity.
''',('SR-37',))
claim(39,'Bias, noise, and kernel content',
      'Same positive Tikhonov construction; arbitrary g,e; source-coercivity alpha>0 only for conditioned bound; g=A*Aw only for source-condition rate.',
      'TikhonovBias.filter_decomposition;TikhonovBias.noisy_source_error_squared;TikhonovBias.full_conditioned_error_squared;TikhonovBias.source_condition_bias_bound',r'''
Write $p=P_{(\ker A)^\perp}g$, $k=P_{\ker A}g$. Then
\[
B_\lambda Ag+\lambda R_\lambda g=g,
\quad B_\lambda(Ag+e)-g=-\lambda R_\lambda g+B_\lambda e,
\]
and
\[
\nn{B_\lambda(Ag+e)-g}^2
=\nn{-\lambda R_\lambda p+B_\lambda e}^2+\nn k^2.
\]
If $A$ has source coercivity $\alpha>0$, this is at most
\[
\left(\frac\lambda{\alpha^2+\lambda}\nn p
+\frac{\nn e}{2\sqrt\lambda}\right)^2+\nn k^2.
\]
For a supplied source condition $g=A^*Aw$,
$\nn{B_\lambda Ag-g}\le\lambda\nn w$ without requiring closed range.
''',r'''
The inverse identity $R_\lambda(A^*A+\lambda I)=I$ gives the filter
decomposition. Linearity adds the propagated noise. On $\ker A$,
$N_\lambda$ acts as $\lambda I$, so $\lambda R_\lambda k=k$.
The resolvent preserves the orthogonal complement: pairing its normal
equation with every kernel vector proves this directly. Thus the combined
identifiable error is orthogonal to $k$, giving the exact squared formula.
Bias and noise inside that first term need not be orthogonal to each other.

For $y=R_\lambda p\in(\ker A)^\perp$, source coercivity and its energy
give $(\alpha^2+\lambda)\nn y^2\le\nn p\nn y$.
Multiply by $\lambda$ and combine with the noise bound in SR-38.
For $g=A^*Aw$, the normal-range source filter is a contraction, so
$\nn{R_\lambda A^*Aw}\le\nn w$. Multiplication by $\lambda$ proves
the source-condition bias rate. The representation by $w$ is supplied;
no controlled $w$ is asserted for every identifiable source.
''',('SR-37','SR-38'))
claim(40,'Resolvent sensitivity and irreducible local error',
      'Real Hilbert bounded A,C; positive lambda,mu; actual closed range only for B=A-dagger and intrinsic globalization formulas.',
      'TikhonovPerturbation.resolvent_difference;TikhonovPerturbation.regularized_operator_difference_bound;TikhonovGlobalization.regularized_pseudoinverse_bias;TikhonovGlobalization.regularized_intrinsic_error',r'''
For two operators and parameters,
\[
R_{A,\lambda}-R_{C,\mu}
=R_{A,\lambda}(N_{C,\mu}-N_{A,\lambda})R_{C,\mu}.
\]
At fixed positive $\lambda$, with $\epsilon=\nn{A-C}$,
\[
\nn{B_{A,\lambda}-B_{C,\lambda}}
\le\frac\epsilon\lambda+
\frac{(\nn A+\nn C)\epsilon\nn C}{\lambda^2}.
\]
If $A$ has closed range and canonical inverse $B$, then
$B_\lambda v-Bv=-\lambda R_\lambda Bv$. For $\delta A=0$,
\[
\nn{v-AB_\lambda v}^2
=\nn{c(v)}^2+\nn{i(v)}^2+\nn{A(B_\lambda v-Bv)}^2.
\]
''',r'''
Multiply the difference of inverses on the left and right by their
normal operators, or insert their inverse laws, to obtain the resolvent
identity. SR-38 bounds its norm by
$\nn{N_{C,\mu}-N_{A,\lambda}}/(\lambda\mu)$.
At equal parameters,
$C^*C-A^*A=(C^*-A^*)C+A^*(C-A)$, whose norm is at most
$(\nn A+\nn C)\epsilon$. Splitting
$R_AA^*-R_CC^*=R_A(A^*-C^*)+(R_A-R_C)C^*$ proves the stated bound.
It permits rank changes and is not uniform as $\lambda$ vanishes.

Under closed range, $A^*$ ignores the part of data orthogonal to
$\Ran A$, so $B_\lambda v=B_\lambda ABv$. Apply the filter identity
to $Bv$ for its bias. The intrinsic candidate identity SR-34 with
$g=B_\lambda v$ yields the local error split. Regularization introduces
image bias while retaining the same obstruction and inconsistency.
''',('SR-29','SR-34','SR-38','SR-39'))
prose(r'''
\begin{example}[Exact scalar response and a two-coordinate example]
For $A_cx=cx$, $B_\lambda v=cv/(c^2+\lambda)$.
At $c>0$, $\lambda=c^2$, the value is $v/(2c)$, attaining the noise bound.
For $A(g_1,g_2)=(g_1+g_2,0,0)$, $v=(3,4,5)$, and $\lambda=1$,
the source is $(1,1)$. Its squared fit is $42=16+25+1$, separating
obstruction, inconsistency, and regularization image bias. Its objective
is $44$, whereas the unregularized source $(3/2,3/2)$ has penalized
objective $91/2$. Positive regularization solves its own stated objective.
\end{example}
''')

section('Strong limits and the uniform boundary',r'''
The following limits fix one bounded $A$ between real Hilbert spaces.
Statements can be indexed by an arbitrary filter. When uniqueness of
limits or a converse is used, the filter is required to be nontrivial.
Closed range is unnecessary for strong convergence on each fixed source.
''')
claim(41,'Density and strong identifiable-source convergence',
      'Fixed bounded real Hilbert A; positive lambda_i→0 along a filter; arbitrary fixed g; nontrivial filter for exact-limit iff identifiability.',
      'TikhonovDensity.gram_range_closure;TikhonovDensity.source_approximation_bound;TikhonovConvergence.tendsto_source;TikhonovConvergence.exact_limit_iff_identifiable;TikhonovConvergence.tendsto_error_norm',r'''
One has $\cl\Ran(A^*A)=(\ker A)^\perp$, and for every $g,w$,
\[
\nn{B_\lambda Ag-g}\le\nn{g-A^*Aw}+\lambda\nn w.
\]
As $\lambda\downarrow0$,
\[
B_\lambda Ag\longrightarrow P_{(\ker A)^\perp}g,
\qquad \nn{B_\lambda Ag-g}\longrightarrow\nn{P_{\ker A}g}.
\]
For a nontrivial parameter filter, convergence to $g$ itself holds exactly
when $g\in(\ker A)^\perp$.
''',r'''
If $x$ is orthogonal to $\Ran(A^*A)$, pairing with $A^*Ax$ gives
$\nn{Ax}^2=0$. Conversely a kernel vector is orthogonal to every
$A^*Aw$ by the adjoint identity. Thus
$(\Ran(A^*A))^\perp=\ker A$, and taking orthogonal complements gives
the closure identity. Decompose the bias into the bias of
$g-A^*Aw$ and of $A^*Aw$. The first is bounded by its input norm because
$\lambda R_\lambda$ is contractive; the second is bounded by
$\lambda\nn w$ from SR-39.

For identifiable $p$, density lets us choose $w$ making the first term
arbitrarily small, independently of $\lambda$. Then let $\lambda$ tend
to zero to remove the second. For arbitrary $g$, $Ag=Ap$ with
$p=P_{(\ker A)^\perp}g$, yielding the claimed source limit.
Subtracting $g$ and taking norms gives the kernel-error limit.
Uniqueness of limits on a nontrivial filter gives the final equivalence.
''',('SR-39',))
claim(42,'Noise schedules and inexact strong limits',
      'Fixed real Hilbert bounded A; lambda_i>0→0; deterministic noise with ‖e_i‖/sqrt(lambda_i)→0; actual normal residual scale vanishes for computed sources.',
      'NoisyRegularization.noisy_source_tendsto;NoisyRegularization.noisy_inexact_solver_tendsto;NoisyRegularization.square_schedule_consistent',r'''
If $\lambda_i>0$ tends to zero and
$\nn{e_i}/\sqrt{\lambda_i}\to0$, then
\[
B_{\lambda_i}(Ag+e_i)\longrightarrow P_{(\ker A)^\perp}g.
\]
The same limit holds for computed $x_i$ when additionally
\[
\frac{\nn{(A^*A+\lambda_iI)x_i-A^*(Ag+e_i)}}{\lambda_i}\to0.
\]
For example, $\lambda_i=s_i^2$, $s_i>0\to0$, and $\nn{e_i}\le s_i^2$
give the exact-solve consistency condition.
''',r'''
The source difference between noisy and exact-data reconstruction is
$B_{\lambda_i}e_i$, whose norm is at most
$\nn{e_i}/(2\sqrt{\lambda_i})$ by SR-38. Combine its vanishing with
the exact-source limit in SR-41. For computed sources, the normal-residual
correction in SR-38 bounds their difference from the actual regularized
source by precisely the second displayed scale. The triangle inequality
then proves the same limit. In the square schedule, the noise ratio is
at most $s_i$, hence vanishes. These schedules are sufficient conditions;
they are not asserted necessary for every favorable operator or noise direction.
''',('SR-38','SR-41'))
claim(43,'Operator-norm convergence exactly at closed range',
      'Fixed real Hilbert bounded A; positive parameter family→0; nontrivial filter for iff; source conditioning alpha only for positive estimate.',
      'UniformRegularization.closed_range_of_approximate_recovery;UniformRegularization.nonclosed_sourceError_norm;UniformRegularization.conditioned_sourceError_norm;UniformRegularization.uniform_convergence_iff_closed_range',r'''
Let $E_\lambda=B_\lambda A-P_{(\ker A)^\perp}$. Always $\nn{E_\lambda}\le1$.
If $\Ran A$ is nonclosed, then $\nn{E_\lambda}=1$ for every positive parameter.
For a positive family tending to zero along a nontrivial filter,
\[
E_\lambda\to0\text{ in operator norm}\iff\Ran A\text{ is closed}.
\]
Under source coercivity $\alpha>0$,
$\nn{E_\lambda}\le\lambda/(\alpha^2+\lambda)$.
''',r'''
The projected bias bound from SR-39 gives the universal upper bound one.
Suppose any bounded $B'$ satisfies
$c=\nn{B'A-P_S}<1$, where $S=(\ker A)^\perp$.
For $x\in S$,
\[
\nn x\le\nn{x-B'Ax}+\nn{B'Ax}
\le c\nn x+\nn{B'}\nn{Ax}.
\]
Therefore $\alpha=(1-c)/(\nn{B'}+1)>0$ supplies off-kernel coercivity,
forcing closed range by SR-32. A nonclosed range thus cannot have
$\nn{E_\lambda}<1$, proving equality. For closed range, source coercivity
exists and the conditioned bias bound yields the displayed quantity tending
to zero. Conversely convergence to zero contradicts the constant norm one
on any nontrivial filter. Strong convergence in SR-41 remains valid in
the nonclosed case because it fixes a source before taking the limit.
''',('SR-32','SR-39','SR-41'))
claim(44,'Fitted-data limit and absent source limit',
      'Fixed real Hilbert bounded A; positive lambda_i→0; data noise→0 for fitted limit; nontrivial filter for impossible source limit.',
      'RegularizedDataLimit.fitted_adjoint_identity;RegularizedDataLimit.fitted_data_tendsto;RegularizedDataLimit.noisy_fitted_data_tendsto;RegularizedDataLimit.unrealizable_no_source_limit',r'''
For arbitrary data $v$,
\[
AB_\lambda^Av=B_\lambda^{A^*}A^*v
\longrightarrow P_{\cl\Ran A}v.
\]
Adding data noise $e_i\to0$ preserves this fitted-data limit.
If $v\in\cl\Ran A\setminus\Ran A$, fitted data converge to $v$ but the
corresponding reconstructed source family has no norm limit in $G$.
''',r'''
The identity
$(AA^*+\lambda I)A=A(A^*A+\lambda I)$ and uniqueness of the positive
normal inverse prove the dual formula. Apply SR-41 to the bounded
operator $A^*$ with source $v$. Its identifiable space is
$(\ker A^*)^\perp=\cl\Ran A$, yielding the fitted limit.
SR-38 shows $AB_\lambda$ is contractive, so changing data by $e_i$
changes the fitted value by at most $\nn{e_i}$.
If reconstructed sources converged in norm to some $g$, continuity of
$A$ would make their images converge to $Ag$. On a nontrivial filter,
the already established image limit $v$ would force $Ag=v$, contrary
to $v\notin\Ran A$. This proves absence of a source norm limit without
adding an unproved assertion that source norms diverge.
''',('SR-38','SR-41'))

section('Discrepancy selection and strong consistency',r'''
Still fix a known bounded $A$ between real Hilbert spaces. Define the actual
residual curve on positive parameters
$r_v(\lambda)=\nn{AB_\lambda v-v}$. Its parameter is mathematical data,
not an assumed noise estimate. Let $\eta$ be a justified true-data allowance
and $\tau>1$ a band multiplier. A total rule must include a small-data branch.
''')
claim(45,'Actual residual curve and unique interior root',
      'Real Hilbert bounded A; lambda>0; strict floor dist(v,range A)<rho<‖v‖ for existence; actual positive parameter only.',
      'DiscrepancyResidual.source_norm_antitone;DiscrepancyResidual.residual_strictMono;DiscrepancyResidual.residual_constant_of_adjoint_zero;DiscrepancyResidual.residual_difference_bound;DiscrepancySelection.exists_unique_parameter_of_distance',r'''
The residual is continuous and nondecreasing on positive parameters;
the source norm is nonincreasing. It is strictly increasing when $A^*v\ne0$,
and constant at $\nn v$ when $A^*v=0$.
For
\[
\dist(v,\Ran A)<\rho<\nn v,
\]
there is exactly one $\lambda>0$ with $r_v(\lambda)=\rho$.
The resulting exact real parameter is a noncomputable choice with a proved
specification.
''',r'''
Compare the minimum objectives at $0<\lambda<\mu$ using each minimizer
as a competitor for the other. Adding the two inequalities gives
$(\mu-\lambda)(\nn{x_\mu}^2-\nn{x_\lambda}^2)\le0$, so source norms
are antitone. Substitution back into the smaller-parameter comparison
shows residual monotonicity. If the two residuals were equal, both
norms and objective values would be equal, and unique minimization would
give $x_\lambda=x_\mu$. Subtracting their normal equations gives
$(\mu-\lambda)x_\lambda=0$, hence $x_\lambda=0$ and $A^*v=0$.
This proves strictness and the constant case.

The resolvent parameter identity gives, for $s,t\ge a>0$,
\[
|r_v(s)-r_v(t)|\le
\frac{\nn A\nn{A^*v}}{a^2}|s-t|,
\]
proving continuity on positive compact intervals. The strict floor permits
a comparator $g$ with $\nn{Ag-v}<\rho$; objective minimization at sufficiently
small positive $\lambda$ gives a lower residual bracket. For large
$\lambda$, $\nn{B_\lambda v}\le\nn{A^*v}/\lambda$, so the residual
approaches $\nn v>\rho$ and gives an upper bracket. The intermediate
value theorem provides a root; strictness gives uniqueness. The floor
condition itself excludes the constant orthogonal-data case.
''',('SR-37','SR-38','SR-40'))
claim(46,'Norm domination converts residual convergence to source convergence',
      'Fixed bounded real Hilbert A; p∈(ker A)⊥; family norm bounds ‖x_i‖≤‖p‖ and true residual ‖Ax_i−Ap‖→0.',
      'DiscrepancyConvergence.norm_domination_of_residual;DiscrepancyConvergence.source_distance_estimate;DiscrepancyConvergence.norm_control_residual_tendsto',r'''
If $\nn{Ag-v}\le r_v(\lambda)$, then $\nn{B_\lambda v}\le\nn g$.
For any $x,p,w$ with $\nn x\le\nn p$,
\[
\nn{x-p}^2\le4\nn p\nn{p-A^*w}+2\nn w\nn{Ax-Ap}.
\]
Consequently, for identifiable fixed $p$, the conditions
$\nn{x_i}\le\nn p$ and $\nn{Ax_i-Ap}\to0$ imply $x_i\to p$ strongly,
without assuming closed range.
''',r'''
Objective minimality gives
$r_v(\lambda)^2+\lambda\nn{B_\lambda v}^2
\le\nn{Ag-v}^2+\lambda\nn g^2$. The residual ordering and positive
$\lambda$ imply norm domination.
For the source estimate, expand $\nn{x-p}^2$ and use $\nn x\le\nn p$
to obtain $\nn{x-p}^2\le2\ip p{p-x}$.
Write $p=(p-A^*w)+A^*w$. The first pairing is at most
$\nn{p-A^*w}\nn{p-x}\le2\nn p\nn{p-A^*w}$; the adjoint identity bounds
the second by $\nn w\nn{Ap-Ax}$. This yields the displayed estimate.
For identifiable $p$, the density in SR-41 permits $w$ with
$p-A^*w$ arbitrarily small (take $w=A u$ from the normal range).
Fixing this $w$, the residual term tends to zero. An epsilon argument
then proves norm convergence. No common inverse bound is invoked.
''',('SR-37','SR-38','SR-41'))
claim(47,'Accepted bands and the total small-data rule',
      'Known bounded real Hilbert A; valid true noise ‖Ag−v_i‖≤eta_i→0; tau≥1 for acceptance consistency; eta>0,tau>1 for total selector existence.',
      'DiscrepancyRule.selectedSource_accepted;DiscrepancyRule.accepted_consistent;DiscrepancyRule.selectedSource_consistent;DiscrepancyRule.accepted_error_norm_limit;DiscrepancyRule.accepted_source_rate',r'''
Call $x$ accepted when either
\[
\nn v\le\tau\eta,\quad x=0,
\]
or $x=B_\lambda v$ for some $\lambda>0$ with
$\eta\le r_v(\lambda)\le\tau\eta$.
With a valid noise allowance, every accepted source satisfies
\[
\nn x\le\nn{P_{(\ker A)^\perp}g},\qquad
\nn{Ax-Ag}\le(\tau+1)\eta.
\]
For accepted families with $\eta_i\to0$,
\[
x_i\to P_{(\ker A)^\perp}g,
\qquad \nn{x_i-g}\to\nn{P_{\ker A}g}.
\]
With $\eta>0$, $\tau>1$, the total selector chooses zero on small data
and otherwise the root $r_v(\lambda)=\tau\eta$. If $g=A^*w$, accepted
sources obey $\nn{x-g}^2\le2\nn w(\tau+1)\eta$.
''',r'''
Let $p=P_{(\ker A)^\perp}g$, so $Ap=Ag$.
In the positive branch, $\nn{Ap-v}\le\eta\le r_v(\lambda)$ gives norm
domination by SR-46; the triangle inequality gives the true residual.
In the zero branch, norm domination is immediate and
$\nn{Ag}\le\nn{Ag-v}+\nn v\le(\tau+1)\eta$.
SR-46 now gives strong convergence to $p$, and continuity of the error
norm gives the kernel limit. For large data, feasibility supplies
$\dist(v,\Ran A)\le\eta<\tau\eta<\nn v$, so SR-45 provides the exact root.
For $g=A^*w$, the approximation term in SR-46 is zero, and the residual
bound proves the squared source-condition rate. General identifiable
sources have no asserted common rate. The rule controls actual Tikhonov
sources; numerical solve errors require the additional certificates below.
''',('SR-45','SR-46'))
claim(48,'Discrepancy endpoints and scalar formulas',
      'Known bounded real Hilbert A and positive lambda; real scalar identity case 0<rho<v.',
      'DiscrepancyBoundaries.no_parameter_above_data;DiscrepancyBoundaries.no_parameter_at_data_norm;DiscrepancyBoundaries.zero_residual_iff_zero_data;DiscrepancyBoundaries.identity_parameter_formula',r'''
No positive parameter has residual larger than $\nn v$.
When $A^*v\ne0$, none has residual equal to $\nn v$.
For every positive parameter, $r_v(\lambda)=0$ exactly when $v=0$.
For the real scalar identity model and $0<\rho<v$,
\[
\lambda=\frac\rho{v-\rho},\qquad B_\lambda v=v-\rho
\]
is the unique root at residual $\rho$.
''',r'''
The first assertion is the residual contraction in SR-38.
Equality at $\nn v$ would give
$F_\lambda(v,x_\lambda)\le F_\lambda(v,0)=\nn v^2$ while its fit term
already equals $\nn v^2$. Hence $x_\lambda=0$, forcing $A^*v=0$.
If the residual is zero, then $Ax_\lambda=v$, and the normal equation
reduces to $\lambda x_\lambda=0$. Thus $x_\lambda=0$ and $v=0$.
The converse is direct. For $A=I$, the normal equation gives
$B_\lambda v=v/(1+\lambda)$ and residual
$\lambda v/(1+\lambda)$ for $v>0$. Substitution proves the formula and
SR-45 supplies uniqueness. These endpoints explain the strict root
inequalities and the separate small-data branch.
''',('SR-38','SR-45'))

exec(compile((HERE/'advanced_claims.py').read_text(),str(HERE/'advanced_claims.py'),'exec'))

section('What the assembled calculus establishes',r'''
The results support a precise progression. Exact resolutions identify which
coordinate vectors and coordinate kernels describe actual objects and
operations. Split compression identifies the excursion through discarded
state that prevents preservation of composition. Memory maps characterize
prepared closure; finite hidden dimension turns their universal vanishing
into a finite whole-map certificate. Behavioral quotients retain exactly
the distinctions accessible to the declared future task. Normed defect
budgets determine how approximate representations propagate their errors.

In inverse problems, compatibility, realizability, and source identifiability
remain distinct. The local obstruction quotient measures compatible data
that have no global source. The compatibility residual measures the
inconsistent sector, with its own conditioning constant. A global source
has separate kernel ambiguity and inverse sensitivity. Regularization
controls an actual penalized objective. Its strong limits recover each
fixed identifiable source, while uniform source convergence requires
closed range. Discrepancy rules and calibrated changing models add
operational acceptance contracts whose true error allowances remain visible.

The common theme is that changing a representation changes the obligations
needed to use it. A certificate can discharge an obligation from concrete
maps and inequalities. A residual can expose the remaining defect.
An obstruction theorem can prove that an obligation is impossible under
the available structure. These outcomes have different mathematical meanings.

\subsection{Exact representation and information loss}
A redundant exact coordinate space need not lose any information about its
object, because synthesis after analysis is identity. Coarsening a packet
address family can also remain exact if the entire contents of the merged
packets are retained. Information loss is supplied by a separate map and
its kernel. In the behavioral setting, only the largest invariant invisible
subspace can be quotiented without changing any declared future observation.
In source reconstruction, the unavoidable ambiguity is the true forward
operator's kernel. Neither coordinate count nor packet count alone decides
sufficiency.

\subsection{Relations to established mathematics}
The mathematics deliberately uses established foundations. Split idempotents,
quotients, observability, block elimination, operator exponentials, orthogonal
geometry, Moore--Penrose inversion, Tikhonov regularization, and discrepancy
principles each contribute concrete constructions. The paper's organizing
claim is that their interfaces can be written together, with exact
transport, obstruction, approximation, and certificate obligations.
Historical novelty of each component is a separate question. The formal
inventory and finite test totals do not answer it.

\subsection{Open bridges and extensions}
The following problems specify further research beyond the printed contracts.

\begin{enumerate}
\item \textbf{Stable target-only recovery from behavioral minimality.}
The exact quotient $X/N$ preserves all specified future observations.
The Hilbert theory stably recovers an identifiable source under its
reconstruction or regularization assumptions. A general theorem connecting
these two constructions must identify a task target, its quotient metric,
the relevant forward map, and sufficient conditioning. It should recover
that target without requiring reconstruction of the full original source.
No such unrestricted bridge is asserted in this edition.
\item \textbf{Calibration truth allowances from individual samples.}
The calibration theorems start from the whole-operator inequality
$\nn{Y-AU}\le\eta_{\rm cal}$. Deriving it from individual noisy probes
requires a specified sample model, a justified aggregation bound, and
control of untested directions. A measured model fit supplies neither
the true operator nor that truth allowance by itself.
\item \textbf{Verified numerical procedures.}
The formalization proves the certificate contracts. The rational Python
implementations compute and check records under explicit input limits.
Their parsers, arithmetic helpers, row-space saturation, parameter
bracketing, and stopping procedures are not formally verified.
Verified extraction or an independent formal certificate importer would
add a new layer of assurance.
\item \textbf{Additional admissible categories.}
Minimum linear dimension does not establish a minimum positive,
stochastic, integral, geometric, or nonlinear realization. Bounded
autonomous generators do not settle unbounded-domain or time-dependent
flow problems. Such extensions must print the additional admissibility
and domain hypotheses rather than importing them through terminology.
\end{enumerate}
''')

section('Source distribution and verification boundaries',r'''
This edition contains a traditional paper, a visual guide, a Lean guide,
and a complete source ZIP. The \texttt{.md} files are included in that ZIP,
alongside editable \texttt{.tex}, the 93 production Lean modules, theorem
guides, exact Python companions, example data, source inventories, and
verification records. The original v0.16.0 archive is preserved separately
for provenance. Publication sources and reconciliation records are
additional files, not silent replacements of the mathematical source history.

The principal concordance uses SR-01 through SR-64 with explicit hypotheses,
dependencies, exact declaration names, and hashes of the source files read
for this assembly. These are consolidated theorem groups. The declaration
inventory comprises 998 theorem/lemma declarations and 1159 enumerated
named declarations in 93 production modules. Supporting identities,
classical specializations, definitions, and checked examples contribute
to these totals.

The archived v0.16.0 final verification includes two runs of the latest
block's 31-module project dependency closure and audits of its 52 new
named declarations. It does not record a fresh simultaneous compilation
of every one of the 93 modules at that final checkpoint. The complete
release verification record distinguishes archived Lean evidence,
fresh compilation if any, source inspections, finite Python replay,
document builds, and archive integrity. This manuscript makes no fresh
Lean compilation claim merely from the existence of those archives.

The exact-rational companions cover observation saturation, discrete
memory, quantitative budgets, orthogonal globalization, quotient metrics,
reconstruction, positive-parameter regularization, discrepancy,
inexact solves, changing operators, generalized feasibility, and calibration.
Their finite checks are implementation evidence in the tested dimensions
and inputs. They are not universal proofs and do not infer external truth
allowances. The current release's exact run ranges and counts belong in
its machine-readable verification records so that archived and fresh
results cannot be conflated.

\subsection{Rebuilding the reading set}
The supplied build scripts invoke pdfLaTeX three times for stable
cross-references and table-of-contents entries. This rebuild creates the
documents. It does not compile Lean, rerun scientific checks, infer a
noise allowance, or authenticate a physical calibration experiment.
Separate scripts and instructions address those activities.

The standalone Markdown manuscript preserves the same statements and
proofs for readers and tools that work directly with text. The concordance
CSV/JSON provides a structured route from a mathematical claim to its
formal declarations. The visual guide illustrates the same contracts
with exact vector figures and checked rational examples. The Lean guide
explains the production modules, the formal domains, and the evidence
needed to reproduce the recorded builds.
''')

parts.append(r'''\appendix
\section{Coverage of the sixteen development blocks}
The block numbers below preserve the development history; they are not
the section numbers of the reorganized paper. Each row identifies four
consolidated theorem groups and the principal mathematical contract.

\small
\begin{longtable}{@{}p{0.07\textwidth}p{0.19\textwidth}p{0.66\textwidth}@{}}
\toprule Block & Stable claims & Contract\\\midrule\endhead
1 & SR-01--SR-04 & Exact redundant representation; compression defects; actual globalization obstruction; behavioral quotient.\\
2 & SR-05--SR-08 & Discrete hidden elimination; closure equivalence; finite feedback certificate; canonical hidden-space construction.\\
3 & SR-09--SR-12 & Finite observation horizon; minimal image dimension; realizable observation tables; finite certificate soundness.\\
4 & SR-13--SR-16 & Exact word-defect transport; heterogeneous budgets; two-rate response; stable initialization bounds.\\
5 & SR-17--SR-20 & Actual bounded flows; powers-to-exponentials bridge; continuous memory; finite moment and jet certificates.\\
6 & SR-21--SR-24 & Duhamel defect transport; flow growth envelopes; uniform stability; scalar sharpness and instability boundary.\\
7 & SR-25--SR-28 & Unique orthogonal error split; harmonic obstruction; compatibility conditioning; finite exactness and refinement.\\
8 & SR-29--SR-32 & Constructed canonical inverse; minimum-norm source; source sensitivity; closed-range characterization.\\
9 & SR-33--SR-36 & Native quotient metric; minimum representatives; bounded obstruction transport; refinement and nonclosed seminorm boundary.\\
10 & SR-37--SR-40 & Coercive Tikhonov construction; objective optimality; bias/noise/kernel accounting; perturbation and globalization.\\
11 & SR-41--SR-44 & Normal-range density; strong source limits; noisy and inexact consistency; uniform boundary and fitted-data limits.\\
12 & SR-45--SR-48 & Actual residual curve; noncomputable root existence; norm-controlled strong consistency; accepted rule and endpoints.\\
13 & SR-49--SR-52 & Source/image solver scales; protected measurements; near-accepted consistency; squared certificate soundness.\\
14 & SR-53--SR-56 & Whole-operator uncertainty; model residual transport; changing-model consistency; operational certificates.\\
15 & SR-57--SR-60 & Candidate-dependent self-bounding; source-cap-free acceptance; feasibility-aware selection; inexact and impossible-model boundaries.\\
16 & SR-61--SR-64 & Redundant calibration frames; generated uncertainty and recovery; hierarchical/approximate frames; unseen-direction obstruction.\\
\bottomrule\end{longtable}\normalsize

\section{Principal dependency paths}
The exact-coordinate path is SR-01 to SR-02. The hidden-memory path is
SR-05 to SR-06 to SR-07, with SR-08 supplying the canonical bridge from an
arbitrary split compression. The behavioral path starts at SR-04 and
passes through SR-09--SR-12. Quantitative discrete transport is
SR-13--SR-16. Bounded analytic flow converts the algebraic memory path
through SR-17--SR-20 and provides approximate transport in SR-21--SR-24.

The globalization path begins with the actual quotient SR-03 and its
projected geometry SR-25--SR-28. Its intrinsic metric is proved in
SR-33--SR-36. Canonical source reconstruction SR-29--SR-32 needs the
additional source-space and closed-range hypotheses. Regularization
SR-37--SR-40 relaxes closed range at positive parameter. Density and
norm domination in SR-41 and SR-46 provide the common strong-consistency
engine for the discrepancy rules and changing-model extensions.

Calibration SR-61--SR-63 supplies operator-error allowances from its own
externally justified truth bounds and conditioning. The recovery chain
then uses generalized acceptance and explicit parameter feasibility.
The negative control SR-64 explains why source-direction coverage is
part of that contract.
\end{document}
''')

if len(claims)!=64 or [r['claim_id'] for r in claims]!=[f'SR-{i:02d}' for i in range(1,65)]:
    raise ValueError('Principal claim IDs are not contiguous in reading order')
for row in claims:
    for dep in row['dependencies']:
        if dep not in {r['claim_id'] for r in claims}: raise ValueError(f'Unknown dependency {dep}')

(HERE/'Sufficient_Resolution_Traditional.tex').write_text(PREAMBLE+'\n'.join(parts))
payload={'schema':'komorebi.claim_lean_concordance.v1','edition':'2026-10-06',
         'title':'Sufficient Resolution: Exact Reduction, Hidden Memory, and Certified Reconstruction',
         'source_inventory':'formal/DECLARATION_INDEX_v0.16.0.csv',
         'interpretation':'64 consolidated theorem groups, not independent novelty or source declaration counts',
         'claims':claims}
(HERE/'Claim_Lean_Concordance.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
fields=['claim_id','block','title','domain','hypotheses','status','evidence','document_label','dependencies','declarations','source_files','source_hashes']
with (HERE/'Claim_Lean_Concordance.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for row in claims:
        out={k:row[k] for k in fields if k in row}
        out.update(dependencies=';'.join(row['dependencies']),
                   declarations=';'.join(a['name'] for a in row['anchors']),
                   source_files=';'.join(dict.fromkeys(a['file'] for a in row['anchors'])),
                   source_hashes=';'.join(dict.fromkeys(a['source_sha256'] for a in row['anchors'])))
        w.writerow(out)
print(json.dumps({'claims':len(claims),'anchors':sum(len(r['anchors']) for r in claims),'tex':str(HERE/'Sufficient_Resolution_Traditional.tex')}))
