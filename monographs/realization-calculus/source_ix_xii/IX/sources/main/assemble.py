#!/usr/bin/env python3
from pathlib import Path
import re,json,hashlib,subprocess,argparse
W=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path,default=W.parent/'source/consolidated/PRSC_IX_Consolidated_Manuscript');args=ap.parse_args()
B=args.source_root.resolve()
CORE=B/'manuscript/consolidated'
(W/'parts').mkdir(exist_ok=True);(W/'evidence').mkdir(exist_ok=True)
sha=lambda t:hashlib.sha256(t if isinstance(t,bytes) else t.encode()).hexdigest()
manifest=[]
for p in sorted((CORE/'sections').glob('*.tex')):
 t=p.read_text();out=t
 if p.name=='20_arithmetic.tex':
  out=out.replace('The Bernoulli valuation theorem gives $v_2(B_{2m})=-1$.','The Bernoulli denominator theorem gives $v_2(B_{2m})=-1$ for $m>0$: its denominator contains each prime $q$ with $(q-1)\\mid 2m$ exactly once, including $2$\\cite{DLMF24}.')
  extra=r''' Indeed, put $E_c=tD+c$ and $C_p=pD^{p^2}-D^p$.
The commutator is $[B_p,E_c]=C_p$, and iteration gives
\[
 B_p^rE_cy=E_cB_p^ry+rC_pB_p^{r-1}y.
\]
For the inverse equation $E_cy=f$, induction on $r$ makes the
correction term Hurwitz-integral. Both operators preserve support in
degrees divisible by $p$. On that support the degree multiplier $d+c$
is a unit, so integrality of $E_cB_p^ry$ implies integrality of
$B_p^ry$. Thus the inverse preserves full flatness, as well as support.
'''
  out=out.replace('Flatness and support are preserved.  Since', 'Flatness and support are preserved.'+extra+' Since')
  extra2=r'''
Here is the coefficient extraction explicitly. If $a_d=d![t^d]F$,
then
\[
 d![t^d]B_p^kF=p^{-k}\Delta_{p(p-1)}^ka_{d+pk}.
\]
For $F=j!\mathcal P_{N,j}$ and $k\le mn$, take $d=mpn-pk$.
Support in multiples of $mp$ turns this into
$p^{-k}\Delta_h^kU_{N,j}(n)$, so flatness gives divisibility by $p^k$.
For $k>mn$, expand $\Delta_h^{k-mn}$ applied to
$\Delta_h^{mn}U_{N,j}(n)$; every shifted row is at least $n$, so
each summand is divisible by $p^{mn}$. Finally
$\Delta_{uh}=((I+\Delta_h)^u-I)$, whose $k$th power for $u>0$
is an integral combination of powers of $\Delta_h$ of order at least $k$.
The case $u=0$ gives zero for $k>0$, and order zero is the original
integral coefficient. This proves the bound for all $u$ and $k$.
'''
  out=out.replace('Finally $\\Delta_{uh}^kU_{N,j}',extra2+'Finally $\\Delta_{uh}^kU_{N,j}')
 if p.name=='50_open_questions.tex':
  out=out.replace('The original TeX, original figure-generation files, and complete\nhistorical experiment package were not recovered with that PDF.', 'The exact original TeX bytes, original figure-generation files, and complete\nhistorical experiment package were not recovered with that PDF.\nThe reconstructed Annals text is reproduced in Appendix~\\ref{app:recovered},\nwith its separate provenance and local qualifications.')
 if p.name=='30_lifting.tex':
  out=out.replace('[Simultaneous coefficient and parameter deformation]','[Joint coefficient and parameter deformation]')
  out=out.replace('\\label{thm:joint-deformation}\nLet','\\label{thm:joint-deformation}\\leavevmode\\par\nLet')
 if p.name=='60_verification.tex':
  old='A fresh request to the official arXiv endpoints was blocked\nby the retrieval tool, so this edition does not claim a new inspection of the\nprimary paper. This access failure affects fresh reauthentication of the\nexternal wording, not the recorded compiler acceptance of the unchanged\nformal sources. No broad literature or priority claim is made.'
  new='The earlier consolidation recorded a blocked request to the official arXiv endpoints.\nFor this final edition, the official unversioned PDF was freshly inspected;\nits internal version is v2, dated 1 June 2026. Definition 2.1 and Remark 2.3\n(printed page 3), Notation 3.2 (page 5), and Conjecture 3.9 (page 8)\nconfirm the parameter, index, degree-displacement and normalization match.\nRequests to the versioned PDF and HTML endpoints still failed.\nThis source check is distinct from the inherited compiler acceptance.\nNo broad literature or priority claim is made.'
  assert old in out;out=out.replace(old,new)
  out+=r'''
\subsection{Checks for this final edition}
The final review reconstructed the arguments in all 54 current written
proof blocks under their stated hypotheses. The two expanded paragraphs
in the all-address proof make the inverse-flatness commutator and the
coefficient-extraction saturation explicit. The recovered historical text
received five local repairs: integral observation vectors for matrix
congruences, positive precision for matrix amplification, integral Mahler
coefficients for the sparsification consequence, the corrected modulo-seven
example, and the even-subsequence range for source changes. Its remaining
historical and external-source evidence limits are retained in
Appendix~\ref{app:recovered}; preservation of its 82 proof bodies is not
a blanket formal certificate.

An independent Python gate using arbitrary-precision integers and
\texttt{fractions.Fraction} passed 116,492 deterministic assertions in nine
finite families: packet construction, foundational identities, divisor-branch
congruences, four-packet sharpness, classical truncations, polynomial digit
fibers, shared affine quotients, finite towers and charts, and weighted
deformation. Nineteen invalid strengthenings were rejected by concrete
controls. The exact ranges, coefficient domains, scripts and output hashes
are in the accompanying \nolinkurl{verification/computation} manifests.
These finite tests do not establish a universal theorem.

The unchanged early-row script separately reproduced 312 finite period
cases and its odd-prime row-zero boundary control. Other research-script
replays, unchanged baseline regression gates and recovered-text controls
are recorded separately in the same audit directory; their totals are
not added to the independent gate. Lean and Lake were unavailable in this
execution environment. No fresh compiler run, infinite $p$-adic computation,
analytic-continuation computation or hardware benchmark is asserted.
'''
 (W/'parts'/p.name).write_text(out)
 manifest.append({'role':'current core','source':str(p.relative_to(B)),'output':'parts/'+p.name,'source_sha256':sha(t),'output_sha256':sha(out),'proofs':len(re.findall(r'\\begin\{proof\}',t)),'modified':t!=out})
# Full mathematical continuation notes, selecting the complete exposition before evidence maps.
notes=[('polynomial_lifting/POLYNOMIAL_LIFTING.md','Scope of the completed block'),('polynomial_counts/POLYNOMIAL_LIFT_COUNTS.md','Verification and boundaries'),('polynomial_towers/PADIC_TOWERS.md','Formalization and verification'),('polynomial_deformation/POLYNOMIAL_DEFORMATION.md','Formal'),('polynomial_charts/POLYNOMIAL_PARAMETER_CHARTS.md','Formal'),('polynomial_weighted/WEIGHTED_LIFTING.md','Formal statement map'),('polynomial_motion/FIRST_ORDER_ROOT_MOTION.md','Formal statement map'),('polynomial_prescribed/PRESCRIBED_PARAMETER_LIFTING.md','Formal'),('polynomial_parameter_towers/PRESCRIBED_PARAMETER_TOWERS.md','Formal interfaces'),('polynomial_joint_motion/JOINT_DEFORMATION.md','Formal interfaces and evidence'),('polynomial_regularity/ANALYTIC_REGULARITY.md','Formal')]
app_a=r'''\clearpage\appendix
\section{Detailed continuation derivations}\label{app:continuation}
The following mathematical release notes preserve the detailed arguments
behind the continuation. They are source-grounded exposition of the completed
blocks, and retain their original hypotheses. Source-declaration and build
inventories are supplied separately in the archive. References to earlier
blocks and then-pending work are dated checkpoint statements; current scope
is given in the main text.
'''
for i,(rel,stop) in enumerate(notes,1):
 p=B/rel;t=p.read_text();lines=t.splitlines(keepends=True)
 # Keep every mathematical paragraph; remove only the trailing source/evidence map if identified.
 end=len(lines)
 for n,line in enumerate(lines):
  if re.match(r'^## '+re.escape(stop),line):end=n;break
 selected=''.join(lines[:end])
 md=W/'parts'/f'continuation_{i:02}.md';md.write_text(selected)
 tex=subprocess.check_output(['pandoc',str(md),'-f','markdown+tex_math_dollars+tex_math_single_backslash','-t','latex','--shift-heading-level-by=1'],text=True)
 # Pandoc fragment headings labels are globally namespaced.
 tex=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:'\\mcode{'+m.group(1).replace('\\_','_')+'}',tex)
 if i==1:
  tex=tex.replace(r'''[u]=[v]\text{ in }\mathcal C_x
\iff
\exists y\equiv x\pmod{q^L}:\quad
F(y)\equiv0\pmod{q^{L+1}},\quad G(y)\equiv0\pmod{q^{L+1}}.''',r'''\begin{gathered}
[u]=[v]\text{ in }\mathcal C_x
\iff
\exists y\equiv x\pmod{q^L}:\\
F(y)\equiv0\pmod{q^{L+1}},\quad G(y)\equiv0\pmod{q^{L+1}}.
\end{gathered}''')
 tex=tex.replace('aeb72f1e9981b6d35b426b16dca7759be3e7ba06',r'\mcode{aeb72f1e9981b6d35b426b16dca7759be3e7ba06}') if '\\mcode{aeb72' not in tex else tex
 tex=re.sub(r'(?<=\\label\{)([^}]+)',lambda m:'cont'+str(i)+':'+m.group(1),tex)
 tex=re.sub(r'\\hypertarget\{([^}]+)\}',lambda m:'\\hypertarget{cont'+str(i)+':'+m.group(1)+'}',tex)
 out=W/'parts'/f'continuation_{i:02}.tex';out.write_text(tex)
 app_a+=r'\input{parts/'+out.name+'}\n'
 manifest.append({'role':'continuation derivation','source':rel,'output':'parts/'+out.name,'source_sha256':sha(t),'selected_source_lines':[1,end],'selected_sha256':sha(selected),'output_sha256':sha(tex),'selection':'full body before indicated trailing formal/evidence section'})
(W/'parts/70_continuation.tex').write_text(app_a)
# Native prose proofs retain all mathematical sections 2--4, including classical specialization.
p=B/'native/Native_Conjectures_Progress.md';t=p.read_text();start=t.index('## 2. ');end=t.index('## 5. ');selected=t[start:end]
md=W/'parts/native_progress.md';md.write_text(selected)
tex=subprocess.check_output(['pandoc',str(md),'-f','markdown+tex_math_dollars+tex_math_single_backslash','-t','latex'],text=True)
tex=re.sub(r'(?<=\\label\{)([^}]+)',lambda m:'native:'+m.group(1),tex);tex=re.sub(r'\\hypertarget\{([^}]+)\}',lambda m:'\\hypertarget{native:'+m.group(1)+'}',tex)
tex=r'''\clearpage\section{Restricted native progress and complete prose proofs}\label{app:native}
This appendix reproduces the mathematical parts of the 8 September 2026
native progress note. The polynomial obstruction, finite reconstruction,
rectangularity and topological arguments are prose proofs. The intrinsic
commutative-algebra obstruction is the stated classical Stacks specialization,
with its original source record and finiteness argument. None of these prose
arguments is promoted to a new Lean run or to a completion of unrestricted
Native 13.2 or 13.3.
'''+tex
(W/'parts/71_native.tex').write_text(tex)
manifest.append({'role':'native prose proofs','source':str(p.relative_to(B)),'output':'parts/71_native.tex','source_sha256':sha(t),'selected_source_lines':[t[:start].count('\n')+1,t[:end].count('\n')],'selected_sha256':sha(selected),'output_sha256':sha(tex)})
# Reconstructed historical Annals body: exact proofs retained, namespaced labels.
p=B/'strengthening/recovery/PSC_Paper_IX_Local_Polyphase_Annals_Edition.retrieved.tex';t=p.read_text();body=t[t.index('\\section{Introduction}'):t.index('\\bibliographystyle')]
missing=[]
def unavailable(m):
 fig=m.group(0);f=re.search(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',fig).group(1);missing.append(f)
 return re.sub(r'\\includegraphics(?:\[[^]]*\])?\{[^}]+\}',r'\\fbox{\\parbox{.87\\linewidth}{\\small Historical figure source unavailable. The retained caption below identifies the original illustration; no replacement image is supplied.}}',fig)
body=re.sub(r'\\begin\{figure\}(?:\[[^]]*\])?.*?\\end\{figure\}',unavailable,body,flags=re.S)
body=re.sub(r'\\(label|ref|eqref|cref|Cref)\{([^}]+)\}',lambda m:'\\'+m.group(1)+'{'+','.join('hist:'+x.strip() for x in m.group(2).split(','))+'}',body)
body=body.replace('\\subsection','\\subsubsection').replace('\\section','\\subsection')
for env in ['theorem','proposition','lemma','corollary','definition','example','remark','standardfact']:
 body=body.replace('\\begin{'+env+'}','\\begin{hist'+env+'}').replace('\\end{'+env+'}','\\end{hist'+env+'}')
# Every superseded full-difference-pending paragraph receives a local current-status notice.
paragraphs=body.split('\n\n'); pending=0
for i,par in enumerate(paragraphs):
 if ('difference' in par.lower() and any(x in par.lower() for x in ['remains open','remain outside','still requires','do not yet','not yet'])):
  paragraphs[i]=par+'\n\\par\\smallskip\\noindent\\textbf{Current status.} This dated statement is superseded for the stated divisor-branch family by Theorem~\\ref{thm:arith-divisor-difference}, with the $j!$ normalization and factorial valuation loss explicitly retained. It makes no claim for unrestricted families.\\par'
  pending+=1
body='\n\n'.join(paragraphs)
body=re.sub(r'\\\[.*?\\\]',lambda m:re.sub(r'\n\s*\n','\n',m.group(0)),body,flags=re.S)
body=body.replace('be a polynomial map. Suppose',r'be a polynomial map.\par\noindent\textbf{Editorial coefficient clarification.} Here polynomial means $F_i\in\Z_p[X_1,\ldots,X_d]$, not merely an integer-valued polynomial with coefficients in $\Q_p$. This makes the Jacobian and Taylor remainder integral and their reduction well typed.\par Suppose')
# Recovered historical statements omitted hypotheses essential to their claims.
historical_notes={
 'hist:thm:matrix_carmichael_mahler':r'\par\noindent\textbf{Editorial hypothesis correction.} The original displayed statement leaves the vectors untyped. Its integrality conclusion requires $v_0,w\in\Z_p^d$, $L\ge1$, and $H,j,n\in\N$ with $H>0$; the value at $Hx+j$ for $x\in\Z_p$ means the matrix-binomial interpolation. With $p=3$, $C=4$, $L=1$, $w=1$ and $v_0=1/3$, one has $\Delta_1a_0=1$, which is not in $3\Z_3$. The printed claim without these restrictions is therefore not an as-written certificate. The full original proof follows under the corrected hypotheses.\par\medskip',
 'hist:thm:finite_adelic_transfer':r'\par\noindent\textbf{Editorial hypothesis correction.} Read this statement with $v_0,w\in\Z^d$, $H>0$ and $j,n,r\in\N$, and positive integer $L_p$. These restrictions make the integral congruences and powers well typed. Allowing $v_0=1/3$ in the one-prime example above loses the advertised digit; invertibility of $C$ alone does not restore it. The original proof is retained under these hypotheses.\par\medskip',
 'hist:lem:matrix_power_amplification':r'\par\noindent\textbf{Editorial hypothesis correction.} Require $L\ge1$. At $L=0$ the standalone claim is false: for $p=3$, $d=1$ and $X=2=1+B$, one has $X^3-1=7\notin3\Z_3$. With $L\ge1$, every higher binomial term in the retained proof has the required valuation, including $p=2$.\par\medskip',
 'hist:thm:matrix_polyphase_precision':r'\par\noindent\textbf{Editorial hypothesis correction.} Require $L\ge1$, $C,B\in M_d(\Z_p)$, $v_0,w\in\Z_p^d$, $H>0$, and $a,j,n,r\in\N$. These are the hypotheses of the two corrected matrix statements used by the retained proof. Without integral observation vectors or positive $L$, the preceding counterexamples invalidate the claimed precision.\par\medskip',
 'hist:thm:prime_power_sparsification':r'\par\noindent\textbf{Editorial hypothesis correction.} The affine-kernel congruence below needs no change, but its consequence for transformed Mahler coefficients requires $c_r\in\Z_p$ for every $r$. Convergence of a $\Q_p$-valued Mahler expansion alone is insufficient. For $p=2$, $M=2$, $s=0$ and $f(x)=x/2$, one has $c_1=1/2$, $c_2=0$, while $g(q)=q$ has $d_1=1$; thus $d_1\not\equiv c_2\pmod2$. The coefficient consequence is read with integral original coefficients.\par\medskip',
 'hist:ex:compressed_mod_seven':r'\par\noindent\textbf{Editorial numerical correction.} The positive-index standard-window tail printed below is erroneous. The defining recurrence gives $e_1=-1\equiv6$, $e_2=5$ and $e_3=-61\equiv2\pmod7$, so the correct positive tail is $6,5,2,6,5,2,\ldots$. The period-three conclusion remains correct. The original line is retained only as a corrected historical record.\par\medskip',
 'hist:cor:local_source_change':r'\par\noindent\textbf{Editorial range correction.} This comparison holds for the even source subsequences, equivalently the evenized generating functions $H_p$. It does not identify their full odd-degree source values. For $p=3$, the original odd source has $A_{3,1}=S_1(3)=3$, whereas every odd dyadic source coefficient is zero; the even kernel $L_3K_2$ cannot change that odd coefficient. Read the coefficient consequence below only at even indices. The displayed identity $H_p=L_pK_\ell H_\ell$ and its proof remain valid.\par\medskip',
 'hist:thm:exact_dyadic_kernel_weight':r'\par\noindent\textbf{Editorial index conventions.} The standalone kernel valuation holds for all $r\ge1$. Its reconstruction-term formula requires even $n\ge0$ and $1\le r\le n/2$. In the following truncation formulas only terms with $r\le n/2$ occur; terms that would use $R_{n-2r}$ at a negative index are omitted. An empty tail is exactly zero, and the minimum over an empty set of term valuations is $+\infty$. These conventions include $M\ge n/2$.\par\medskip'
}
for label,note in historical_notes.items():
 assert ('\\label{'+label+'}') in body,label
 body=body.replace('\\label{'+label+'}', '\\label{'+label+'}\n'+note)
# actual correct current label determined below
body=body.replace('thm:arith-divisor-difference','thm:arith-divisor-base')
labels=re.findall(r'\\label\{([^}]+)\}',(W/'parts/20_arithmetic.tex').read_text()); assert 'thm:arith-divisor-base' in labels,labels
header=r'''\clearpage\section{Recovered historical local polyphase manuscript}\label{app:recovered}
This is the complete substantive body of the reconstructed Annals textual
copy, preserved to retain its derivations and original parameter ranges.
The recovered text is not certified as the exact original TeX bytes. Its
historical theorem headings distinguish these statements from the current
numbered core. Preservation is not a blanket proof audit or Lean certificate:
in particular the broader Amice analytic pullback and depleted branches,
finite-field modal minimality and unrestricted infinite polyphase claims
retain their historical evidence scope. The current formal statement map
records only the individually identified interfaces in the main text.

All 14 original figure inclusions refer to files absent from the recovered
source; their captions and labels are retained with an unavailable-source
notice. The historical bibliography file is also absent. Its citation keys
are preserved in the bibliography as unresolved source records, without
invented bibliographic entries. Superseded claims about the divisor-branch
finite-difference problem have local notices directing the reader to the
current theorem. The remaining higher kernel-valuation and unrestricted
local-to-global questions remain open in their stated scopes.

'''
(W/'parts/72_recovered.tex').write_text(header+body)
manifest.append({'role':'historical recovered full manuscript','source':str(p.relative_to(B)),'output':'parts/72_recovered.tex','source_sha256':sha(t),'output_sha256':sha(header+body),'proofs':len(re.findall(r'\\begin\{proof\}',t)),'figures_unavailable':missing,'local_superseded_status_notices':pending})
# Eleven complete dated supplements.
order=['First','Second','Third','Fourth','Fifth','Sixth','Seventh','Eighth','Singular_Amice','All_Residue_Completion']
paths=[B/'manuscript/baseline/docs'/('Paper_IX_'+x+('_Lean_Block' if x in order[:8] else '')+'_Supplement.tex') for x in order]
paths.append(B/'manuscript/baseline/docs/Nishibuchi_Conjecture_Completion.tex')
app_d=r'''\clearpage\section{Complete mathematical checkpoint supplements}\label{app:supplements}
These eleven supplements reproduce the complete mathematical bodies of their
successive checkpoints. The numerical inventories, coverage fractions and
then-pending statements belong to each original checkpoint. They are not
current total counts. In particular the later all-residue and Nishibuchi
completion supersede earlier pending labels. The final arithmetic and
polynomial scopes are the ones stated in the main text. All derivations,
examples, formal-interface explanations and original qualification paragraphs
remain available below.
'''
for i,p in enumerate(paths,1):
 t=p.read_text();body=t.split('\\begin{document}',1)[1].rsplit('\\end{document}',1)[0]
 # Remove standalone masthead only; full section body is retained.
 m=re.search(r'\\section\*',body);assert m,p;body=body[m.start():]
 body=body.replace('\\section*','\\subsubsection*')
 body=re.sub(r'\\(label|ref|eqref|cref|Cref)\{([^}]+)\}',lambda m:'\\'+m.group(1)+'{sup'+str(i)+':'+m.group(2)+'}',body)
 body=body.replace('\\newpage','\\par\\medskip')
 body=body.replace('\\input{verification_summary.tex}','\\input{parts/verification_summary.tex}')
 body=body.replace(r'p{.48\textwidth}p{.18\textwidth}rr',r'p{.48\textwidth}>{\raggedright\arraybackslash}p{.18\textwidth}rr')
 body=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:'\\mcode{'+m.group(1).replace('\\_','_')+'}',body)
 body=re.sub(r'\\(target|code)\{([^{}]*)\}',lambda m:'\\'+m.group(1)+'{'+m.group(2).replace('\\_','_')+'}',body)
 title=p.stem.replace('Paper_IX_','').replace('_',' ').replace('Nishibuchi Conjecture Completion','Nishibuchi conjecture completion')
 part=r'\clearpage\subsection{'+title+r'}\label{app:sup'+str(i)+'}\n'+r'\noindent\textbf{Checkpoint scope.} This complete source body retains the status of its dated original supplement. Earlier pending or partial-coverage labels are historical; the final core records their resolution.\par\medskip'+'\n'+body
 out=W/'parts'/f'supplement_{i:02}.tex';out.write_text(part);app_d+=r'\input{parts/'+out.name+'}\n'
 manifest.append({'role':'complete mathematical checkpoint supplement','source':str(p.relative_to(B)),'output':'parts/'+out.name,'source_sha256':sha(t),'output_sha256':sha(part),'proofs':len(re.findall(r'\\begin\{proof\}',t)),'body_preserved':'complete first-section-through-end body; only heading depth,label prefix,pagebreak conversion'})
(W/'parts/73_supplements.tex').write_text(app_d)
(W/'parts/verification_summary.tex').write_bytes((B/'manuscript/baseline/docs/verification_summary.tex').read_bytes())
manifest.append({'role':'inherited supplemental verification summary','source':'manuscript/baseline/docs/verification_summary.tex','output':'parts/verification_summary.tex','source_sha256':sha((B/'manuscript/baseline/docs/verification_summary.tex').read_bytes()),'output_sha256':sha((W/'parts/verification_summary.tex').read_bytes()),'byte_identical':True})
# Root source and complete bibliography ledger.
main=(CORE/'Paper_IX_Consolidated.tex').read_text();main=main.replace('Consolidated Edition','Traditional Final Edition').replace('Consolidated edition','Traditional final edition').replace('Consolidated edition\\quad 8 September 2026','Final edition\\quad 6 October 2026').replace('8 September 2026','6 October 2026',1)
main=main.replace('\\usepackage{lmodern,microtype}','\\usepackage{lmodern,microtype,bm,graphicx}')
# Conventions needed only by retained supplements/history.
extra=r'''
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\passthrough}[1]{#1}
\newcommand{\mcode}[1]{\ifmmode\text{\nolinkurl{#1}}\else\nolinkurl{#1}\fi}
\definecolor{ink}{HTML}{20384B}
\newcommand{\ZZ}{\mathbb Z}\newcommand{\QQ}{\mathbb Q}\newcommand{\FF}{\mathbb F}\newcommand{\NN}{\mathbb N}
\newcommand{\Wp}{\mathcal W_p}\newcommand{\Hp}{\mathcal H(\Z_p)}
\newcommand{\ordp}{\operatorname{ord}_p}\newcommand{\ord}{\operatorname{ord}}
\newcommand{\coef}[2]{[#1^{#2}]}\newcommand{\target}[1]{{\footnotesize\nolinkurl{#1}}}
\newcommand{\pageheading}[2]{{\large\bfseries\color{ink}#1}\par{\small #2}\par\medskip}
\newcommand{\sech}{\operatorname{sech}}\newcommand{\fall}[2]{(#1)_{#2}}
\newcommand{\EE}{\mathcal E}\newcommand{\PP}{\mathcal P}\newcommand{\code}[1]{{\small\nolinkurl{#1}}}
\newcommand{\Hcal}{\mathcal H}\newcommand{\Ecal}{\mathcal E}\newcommand{\Ccal}{\mathcal C}\newcommand{\Pcal}{\mathcal P}\newcommand{\Scal}{\mathcal S}\newcommand{\Ocal}{\mathcal O}\newcommand{\Rcal}{\mathcal R}\newcommand{\Vcal}{\mathcal V}\newcommand{\Wcal}{\mathcal W}
\newcommand{\End}{\operatorname{End}}\newcommand{\Ker}{\operatorname{Ker}}\newcommand{\Res}{\operatorname{Res}}\newcommand{\vp}{v_p}\newcommand{\vTwo}{v_2}\newcommand{\sTwo}{s_2}\newcommand{\DeltaH}{\Delta_h}\newcommand{\abs}[1]{\left\lvert#1\right\rvert}\newcommand{\norm}[1]{\left\lVert#1\right\rVert}\newcommand{\one}{\bm 1}\newcommand{\starh}{\mathbin{\star}}\newcommand{\e}{\mathrm e}
'''
for env,title in [('theorem','Historical theorem'),('proposition','Historical proposition'),('lemma','Historical lemma'),('corollary','Historical corollary'),('definition','Historical definition'),('example','Historical example'),('remark','Historical remark'),('standardfact','Historical standard fact')]:
 extra+='\\newtheorem{hist'+env+'}[theorem]{'+title+'}\n'+'\\crefname{hist'+env+'}{historical '+env+'}{historical '+env+'s}\n'
main=main.replace('\\begin{document}','\\usepackage[nameinlink,noabbrev]{cleveref}\n'+extra+'\n\\begin{document}')
main=main.replace('sections/','parts/')
main=main.replace('\\begin{thebibliography}{9}',r'''\clearpage
\input{parts/70_continuation}
\input{parts/71_native}
\input{parts/72_recovered}
\input{parts/73_supplements}
\clearpage
\begin{thebibliography}{99}''')
main=main.replace('\\bibitem{Mathlib}',r'''\bibitem{DLMF24}
NIST Digital Library of Mathematical Functions, \S24.10(i),
Eq.\ 24.10.1 (Bernoulli denominator theorem).
\url{https://dlmf.nist.gov/24.10.E1}. The official primary entry was inspected
for the positive even-index denominator specialization in this edition.

\bibitem{Mathlib}''')
keys=sorted({k.strip() for m in re.finditer(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}',t if False else (B/'strengthening/recovery/PSC_Paper_IX_Local_Polyphase_Annals_Edition.retrieved.tex').read_text()) for k in m.group(1).split(',')})
ledger='\n\\medskip\\noindent\\textbf{Recovered historical citation ledger.}\nThe following keys reproduce the callouts in Appendix~\\ref{app:recovered}.\nThe corresponding exact bibliography entries were absent from the recovered\narchive; a key is not an authenticated bibliographic record.\n'
for key in keys:ledger+='\\bibitem{'+key+'} Historical citation key \\nolinkurl{'+key+'}. Exact source entry unavailable in recovered bibliography.\n'
main=main.replace('\\end{thebibliography}',ledger+'\\end{thebibliography}')
main=main.replace('\\n\\usepackage','\n\\usepackage')
(W/'Paper_IX_Traditional_Final.tex').write_text(main)
(W/'evidence/ASSEMBLY_MANIFEST.json').write_text(json.dumps({'source_root':str(B),'parts':manifest,'historical_citation_keys':keys},indent=2)+'\n')
(W/'evidence/HISTORICAL_CORRECTION_NOTES.json').write_text(json.dumps({'role':'local repaired historical statements; raw body and original proof remain preserved','notes':historical_notes,'coefficient_typing_clarification':'F_i in Zp[X], not merely integer-valued Qp polynomial','superseded_full_difference_notices':pending,'math_audit_report':'../audit/math/MATH_AUDIT.json'},indent=2)+'\n')
print(json.dumps({'parts':len(manifest),'proofs_current':sum(x.get('proofs',0) for x in manifest if x['role']=='current core'),'proofs_historical':sum(x.get('proofs',0) for x in manifest if 'historical recovered' in x['role']),'supplements':len(paths),'missing_figures':len(missing),'citation_keys':len(keys)},indent=2))
