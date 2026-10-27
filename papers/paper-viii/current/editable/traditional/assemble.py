#!/usr/bin/env python3
"""Editorial assembly. Raw inputs remain read-only; build.py is portable."""
from pathlib import Path
import re, json, shutil, hashlib, difflib

ROOT=Path(__file__).resolve().parent
SRC=ROOT.parent/'source'
S=SRC/'strengthened/PSC_Paper_VIII_Strengthened_Annals_Edition_Package'
C=SRC/'complete/Paper_VIII_Complete_v0.6.0_With_Visual_Appendix'
MAIN=S/'PSC_Paper_VIII_Strengthened_Annals_Edition.tex'
NOTES=C/'original_snapshot/notes'
for d in ['parts','figures','evidence']:(ROOT/d).mkdir(parents=True,exist_ok=True)
for p in (S/'figures').glob('*.pdf'):shutil.copy2(p,ROOT/'figures'/p.name)
shutil.copy2(S/'PSC_Paper_VIII_Strengthened_Annals_Edition.bib',ROOT/'references.bib')
bib=(ROOT/'references.bib').read_text()
bib=bib.replace('title        = {CUDA Programming Guide}', 'title        = {CUDA C++ Programming Guide}')
bib=bib.replace('note         = {Version consulted May 2026}', 'note         = {Archive version 12.8.1, Section 3.2.8.7 (CUDA Graphs), accessed 6 October 2026},\n  url          = {https://docs.nvidia.com/cuda/archive/12.8.1/cuda-c-programming-guide/index.html#cuda-graphs}')
bib=bib.replace('  year         = {2026},\n  note         = {Archive version', '  note         = {Archive version')
(ROOT/'references.bib').write_text(bib)

changes=[];records=[];proofs=[];sections=[];supplements=[]
raw=MAIN.read_text();body=raw[raw.index(r'\section{Introduction}'):raw.index(r'\bibliographystyle')]
def fix(before,after,reason):
 global body
 count=body.count(before)
 if count!=1:raise RuntimeError(f'Anchor {count}: {reason}')
 body=body.replace(before,after)
 changes.append(dict(before=before,after=after,reason=reason))

fix('The corpus contains 154 measured rows from sixteen suites.', 'The preserved corpus contains 154 recorded rows from sixteen suites. The timings are inherited observations; no GPU timing is rerun for this edition.', 'Empirical evidence is inherited.')
fix('The benchmark protocol therefore records case identity, output contract, timing scope, source precision, correctness reference, discovery time, compilation time, and reuse count.', 'The benchmark protocol therefore requires case identity, output contract, timing scope, source precision, correctness reference, discovery time, compilation time, and reuse count. The archived rows do not satisfy every field of this ideal contract: source-value hashes and explicit correctness-reference fields are absent; setup, discovery, and reuse metadata are sparse. Recorded ratios are consequently descriptive comparisons under their stated scopes, rather than full-provenance fair matches.', 'Protocol requirement separated from incomplete archived metadata.')
fix(r'Its evaluation is', r'Local blocks are identified with their ambient extensions by inclusion and projection. In particular, the notation $P_\beta AP_\alpha$ denotes either the ambient block or its restriction $X_\alpha\to X_\beta$ according to the displayed domain; $\iota_\beta B_{\beta\alpha}P_\alpha$ is the corresponding ambient extension. Its evaluation is', 'Local versus ambient packet block convention.')
fix(r'The coordinate projector onto \(X_\alpha\) is denoted by \(P_\alpha\).', r'The coordinate inclusion and projection are $\iota_\alpha:X_\alpha\to X$ and $\pi_\alpha:X\to X_\alpha$. The ambient coordinate projector is $P_\alpha=\iota_\alpha\pi_\alpha$.', 'Explicit local projection and ambient inclusion types.')
fix(r'$\iota_\beta B_{\beta\alpha}P_\alpha$ is the corresponding ambient extension.', r'$\iota_\beta B_{\beta\alpha}\pi_\alpha$ is the corresponding ambient extension.', 'Ambient extension uses the actual local-coordinate projection.')
fix(r'\iota_\beta B_{\beta\alpha}P_\alpha,', r'\iota_\beta B_{\beta\alpha}\pi_\alpha,', 'IR evaluation fully typed.')
fix(r'B_{\beta\alpha}=P_\beta AP_\alpha', r'B_{\beta\alpha}=\pi_\beta A\iota_\alpha', 'Exact-evaluation local blocks fully typed.')
fix(r'B_{\beta\alpha}P_\alpha Z.', r'\iota_\beta B_{\beta\alpha}\pi_\alpha Z.', 'Exact batch output includes actual codomain inclusion.')
fix('These counts describe a representation. They do not predict wall time without a memory and launch model.', 'These counts describe a declared event model for a representation. They do not predict wall time without a memory and launch model. A multiply--accumulate charges two scalar operations even for the first coefficient. Thin corrections accumulate into an already computed diagonal or sparse result. Index metadata, temporary workspace, launch overhead, discovery, transfer, and materialization are accounted for separately.', 'Model ledger: event counts and accumulation convention.')
fix(r'Suppose \(n\) is divided into equal diagonal packets of width \(b\).', r'Let $p\ge1$ and $b\ge1$ be integers and $n=pb$. Suppose $n$ is divided into $p$ equal diagonal packets of width $b$.', 'Equal-block ratio has positive denominator and nonzero dense work/storage.')
fix('The dense to block reduction factor is', r'The dense-to-block storage reduction factor is the following; the arithmetic reduction factor has the same value when $q\ge1$:', 'Zero right-hand-side count allowed for count formulas but excluded from arithmetic ratio.')
fix('For equal packets of width \\(b\\), both ideal dense reduction factors equal', r'For $n=pb$, with integers $p,b\ge1$, both ideal dense reduction factors equal', 'Positive reduction-factor denominator.')
fix('both ideal dense reduction factors equal', r'the ideal dense storage reduction factor is the following; the arithmetic reduction factor has the same value when $q\ge1$:', 'BDLR arithmetic reduction ratio excludes q=0.')
fix(r'The modeled arithmetic intensity is', r'When the modeled byte traffic is strictly positive, the modeled arithmetic intensity is', 'Positive byte denominator.')
fix(r'Suppose a device sustains at most \(P\) modeled operations per second and at most \(W\) bytes per second.', r'Suppose a device sustains at most $P>0$ modeled operations per second and at most $W>0$ bytes per second.', 'Positive operation/bandwidth capacities.')
fix('Equivalently, its work rate is at most', 'For positive elapsed time and positive byte traffic, its work rate is at most', 'Rate/intensity divisions have positive denominators.')
fix(r'Let a device have available memory \(M\) bytes and scalar size \(s\).', r'Let a device have available memory $M\ge0$ bytes and scalar size $s>0$, and let $n\ge0$.', 'Square-root capacity threshold domain.')
fix(r'Let \(p=n/b\) equal packets have width \(b\).', r'Let $p,b\ge1$ be integers, $n=pb$, and let $p=n/b$ equal packets have width $b$.', 'Banded count uses positive width, exact integer factorization, w<p.')
fix(r'Let \(c\in\CC^n\), with indices taken modulo \(n\), and define', r'Let $n\ge1$ be an integer and $c\in\CC^n$, with indices taken modulo $n$, and define', 'Positive Fourier order.')
fix(r'Let \(T\in\CC^{n\times n}\) be Toeplitz, with first column', r'Let $n\ge1$ be an integer and $T\in\CC^{n\times n}$ be Toeplitz, with first column', 'Positive Toeplitz order.')
fix(r'A product of \(k\) square factors of order \(d\), acting on a tensor with \(d^k\) entries, can be applied by \(k\) modewise contractions with modeled cost', r'For integers $k,d\ge0$, a product of $k$ square factors of order $d$, acting on a tensor with $d^k$ entries, can be applied by $k$ modewise contractions, reusing intermediate slices, with modeled cost', 'Tensor action/count boundary including empty tensor product.')
fix(r'For one mode, there are \(d^{k-1}\) fibers of length \(d\).', r'For $k=0$ there are no contractions and both modeled work and factor storage are zero. For $k\ge1$, one mode has $d^{k-1}$ fibers of length $d$.', 'Proof explicitly handles k=0 before k-1 expression.')
fix('be a singular value decomposition. Define', r'be an ordered thin singular value decomposition, with nonnegative nonincreasing singular values. For an integer $k\ge0$, retain $\min\{k,d\}$ columns, where $d$ is the number of supplied thin singular directions; tail singular values beyond $d$ are zero. Define', 'Ordered exact SVD equations and rank endpoint convention.')
fix('then its truncated singular value decomposition \\(M_k\\) is a best rank at most \\(k\\) approximation.', r'pad this finite sequence with zeros. For each integer $k\ge0$, its truncated singular value decomposition $M_k$ is a best rank-at-most-$k$ approximation.', 'Classical singular-tail formula includes all truncation endpoints.')
fix('They preserve the nonzero singular values and every unitarily invariant norm of the core.', 'They preserve the nonzero singular values and the spectral and Frobenius norms of the core. For every ambient rank-at-most-$k$ competitor $B$, its compression $Q_L^*BQ_R$ has rank at most $k$, and compression cannot increase either norm. Thus the core best-approximation inequality also lower-bounds the error of every ambient competitor.', 'Explicit arbitrary ambient competitor bridge and the two norms actually needed.')
fix('The number of sequential stages in the level schedule equals one plus the length of the longest directed path.', 'For a nonempty finite graph, the number of sequential stages in the level schedule equals one plus the length of the longest directed path. The empty graph has depth zero.', 'Empty DAG branch.')
fix('The largest level therefore counts the vertices on a longest path.', 'For a nonempty graph, the largest level therefore counts the vertices on a longest path. For an empty graph, no task is scheduled and the depth is zero.', 'Proof handles empty DAG.')
fix('is the sum over directed paths', 'is the sum over directed walks (vertices may repeat)', 'General powers enumerate walks, not only simple paths.')
fix('If there is no directed path from packet', 'Reachability here includes a zero-length path from a packet to itself. If there is no directed path from packet', 'Reflexive inverse support reachability.')
fix('A retained block \\((\\beta,\\alpha)\\) can be active only if it was already active in \\(A_{RR}\\), or if there is a directed walk from \\(\\alpha\\) through hidden packets to \\(\\beta\\).', 'A retained block $({\\beta},{\\alpha})$ can be active only if it was already active in $A_{RR}$, or if there is a directed walk from $\\alpha$ through hidden packets to $\\beta$. The internal hidden path may have length zero, so entrance and exit may use the same hidden packet.', 'Schur support includes zero-length internal hidden paths.')
fix('be Hermitian positive definite with positive block diagonal part \\(D\\).', 'act on a nonempty finite coordinate space and be Hermitian positive definite with positive definite block diagonal part $D$. Here $D^{-1/2}$ is the actual inverse of the positive square root of $D$.', 'Nonempty actual positive square-root condition-number model.')
fix(r'Let \(A\) and \(M\) be Hermitian positive definite, and set', r'Let $A$ and $M$ be Hermitian positive definite on a nonempty finite coordinate space, and set', 'Classical CG condition number defined on nonempty space.')
fix('The energy norm error of preconditioned conjugate gradient satisfies', 'In exact arithmetic, the energy norm error of preconditioned conjugate gradient satisfies', 'External CG convergence theorem uses exact arithmetic.')
fix('Under the standard floating point model, a computed matrix product may be written as an exact product with a dimension dependent backward perturbation. The perturbation constant is controlled by the unit roundoff and the inner dimension when overflow and underflow are excluded.', r'''For real $A\in\RR^{m\times p}$ and $B\in\RR^{p\times n}$, consider ordinary dot-product matrix multiplication in uniform precision with unit roundoff $u$, no overflow or underflow, and $pu<1$. Its computed output $\widehat C$ satisfies the componentwise forward-error bound
\[
|\widehat C-AB|\le\gamma_p|A||B|,
\qquad\gamma_p=\frac{pu}{1-pu}.
\]
Absolute values and the inequality are entrywise. Complex arithmetic, fused kernels, mixed accumulation, and tensor kernels require their own stated constants. This fact does not assert one common small input perturbation for every column, and an input-dependent rounded action is not automatically a fixed linear operator.''', 'False generic common input-backward perturbation replaced by standard classical real product forward bound; Higham--Mary primary §4(4.1).')
fix(r'Detailed forms and their hypotheses are given in \cite{Higham2002}. Packetwise use of this fact produces edge bounds \(\eps_e\) for \cref{thm:packet_error}.', r'Detailed forms and their hypotheses are given in \cite{Higham2002,HighamMary2021}. For a fixed computed matrix, the bound can certify its error matrix. A rounded application to varying inputs needs a separately justified uniform certificate before it can be used as one fixed operator error in \cref{thm:packet_error}.', 'Forward certificate versus fixed linear-operator modeling.')
fix(r'If each factor \(A_j\) is replaced by a packetwise approximation \(\widehat A_j\), then the final operator error is bounded by \cref{thm:product_chain_error}. Each \(\norm{E_j}\) may in turn be bounded by the packet certificate in \cref{thm:packet_error}.', r'''If each fixed linear factor $A_j$ is replaced by a fixed packetwise linear approximation $\widehat A_j$, write $E_j=\widehat A_j-A_j=\sum_e\Delta_{j,e}P_{\alpha(j,e)}$. A uniform certificate is
\[
\|E_j\|\le\delta_j:=\sum_e\|\Delta_{j,e}\|\,\|P_{\alpha(j,e)}\|.
\]
For orthogonal packet projectors, $\delta_j\le\sum_e\|\Delta_{j,e}\|$. The final operator error is bounded by \cref{thm:product_chain_error} with these uniform $\delta_j$. The corresponding vector error is this operator bound multiplied by the input norm.''', 'Vector-specific estimate replaced by uniform operator certificate in product chain.')
fix(r'Apply \cref{thm:packet_error} at every stage and substitute the resulting operator error bounds into \cref{thm:product_chain_error}.', r'Take the supremum over unit inputs in \cref{thm:packet_error}, using $\|P_{\alpha}x\|\le\|P_{\alpha}\|\|x\|$. Substitute the resulting uniform operator error bounds into \cref{thm:product_chain_error}; the action estimate follows from submultiplicativity.', 'Uniform-bound proof repairs source domain mismatch.')
fix(r'Let \(s_e>0\) be sensitivities and \(c_e>0\) be costs. Consider', r'Let $E$ be a finite nonempty edge set, let $s_e>0$ be sensitivities and $c_e>0$ be costs, and let $\tau>0$. Consider', 'Source amendment for unique continuous optimum.')
fix('Add upper bounds\n', 'Retain the finite nonempty edge set, strictly positive sensitivities and costs, and add strictly positive caps $m_e>0$ with upper bounds\n', 'Source amendment for clipped optimum.')
fix('The constraint determines \\(\\lambda\\). Strict convexity gives uniqueness of the minimizer.', 'For a strictly submaximal budget, once any coordinate is unsaturated, $\\phi$ is strictly decreasing, which gives a unique multiplier. At maximal budget the only feasible vector is $(m_e)_e$ and every $0<\\lambda\\le\\min_e c_e/(s_em_e)$ produces it. Thus the minimizing vector is unique at this endpoint while its multiplier need not be. Strict convexity gives uniqueness of the minimizer in every case.', 'Explicit endpoint multiplier distinction.')
fix('Suppose the keep score and split score at every internal node change by less than \\(g_v/2\\).', 'Suppose the solved keep score and split score at every internal node change in absolute value by less than $g_v/2$. These are scores after child subproblems have been solved, rather than unconstrained changes in raw local costs.', 'Stability concerns solved scores.')
fix('Suppose local costs change only inside the subtree rooted at \\(u\\).', 'Suppose local costs change only inside the subtree rooted at $u$, while ancestor and sibling local models are unchanged. Use correct cached sibling values from the old solve.', 'Cached local update assumes valid unaffected sibling caches.')
fix('The minimum possible number of sequential stages equals the number of vertices on a longest directed path.', 'For a nonempty finite graph, the minimum possible number of sequential stages equals the number of vertices on a longest directed path. The empty task graph has depth zero.', 'Unit-task schedule includes empty graph.')
fix('The topological level schedule in \\cref{thm:level_schedule} achieves exactly this depth.', 'The topological level schedule in \\cref{thm:level_schedule} achieves exactly this depth. With no tasks, the empty schedule has depth zero.', 'Empty task schedule proof.')
fix(r'Let \(t_b\) be the baseline time per use and \(t_c\) the candidate time per use.', r'Let $t_b,t_c\ge0$ be the baseline and candidate times per use and let $R\in\NN$ be a reuse count.', 'Physical timing/reuse model.')
fix(r'If graph capture costs \(c\), ordinary execution costs \(t_o\), and replay costs \(t_r<t_o\),', r'If graph capture costs $c\ge0$, ordinary execution costs $t_o\ge0$, and replay costs $0\le t_r<t_o$,', 'Nonnegative graph capture/time model.')
fix(r'Suppose a compressed representation costs \(t_c\) per downstream use, an explicit representation costs \(t_e\) per use, and one time materialization costs \(m\).', r'Suppose a compressed representation costs $t_c\ge0$ per downstream use, an explicit representation costs $t_e\ge0$ per use, and one time materialization costs $m\ge0$, with reuse count $R\in\NN$.', 'Nonnegative materialization cost and reuse count.')
fix('Materialization is profitable only when', 'Materialization is profitable exactly when', 'Full equivalence under explicit nonnegative model.')
fix('The full deterministic verifier performs \\(37392\\) checks in nine groups.', 'The strengthened release records a deterministic verifier with $37392$ checks in nine groups.', 'Historical verifier record, fresh evidence in separate guide.')
fix('The strengthened unit suite contains eleven passing tests. The original source suite contains twenty three passing tests', 'The strengthened release records eleven passing unit tests and twenty three passing original-source tests', 'Historical unit records explicitly inherited.')
fix('The mathematical interface is deliberately narrow.', 'The mathematical interface is deliberately narrow. This Python implementation is a numerical prototype, not extracted Lean code. Its stored-key support can retain zero-valued blocks, whereas the exact support graph uses nonzero blocks. Its reduced numerical QR is not the exact rank-compact range construction proved in Appendix F. Prototype tests and theorem proofs therefore have different targets.', 'Numerical prototype separated from exact support and compact range objects.')
# Evidence qualifiers: keep numerical values but do not overstate archived matching metadata.
body=body.replace('matched device resident dense GPU row','recorded device resident dense GPU row with the same recorded case, output, and timing scope')
body=body.replace('matched CPU dense row','recorded CPU dense row (resident CPU scope versus device-resident GPU scope)')
body=body.replace('matched dense GPU row','recorded dense GPU row (graph-replay scope versus device-resident scope)')
body=body.replace('The corpus retains methods that lost to their matched baselines.', 'The corpus retains methods that lost in the recorded baseline comparisons. These are descriptive ratios; scope and complete-metadata qualifications apply.')
body=body.replace('matched OpenBLAS dense multiplication','recorded OpenBLAS dense multiplication')
body=body.replace('matched baselines','recorded baselines')
body=body.replace('best matched gain','best recorded gain')
body=body.replace('The measured product rows show the cost of changing the output contract.', 'The historical product rows illustrate the cost of changing the output contract; compressed and materialized outputs are separate computations.')
needle=r'\subsection{Dense precision frontier}'
body=body.replace(needle,r'''The 154 archived rows contain recorded case identifiers, seeds, types, output contracts, and timing scopes. Source-value hashes and explicit correctness-reference fields are absent. Setup time, discovery time, and reuse count are nonnull in only two rows each; correctness errors are present in 149 rows. Equality of available metadata cannot establish the full fair-match relation in \cref{def:fair_match}. In particular, CPU-resident and GPU-device-resident scopes differ, and graph replay excludes capture while a device-resident baseline has a different raw scope. The two-stream example also compares wall time with a serial device-time scope. The values below are retained as historical observations with these limitations.

'''+needle)
changes.append(dict(reason='Empirical prose consistently says recorded/descriptive comparisons, retains every historical numeric value, and inserts precise archived-metadata/scope limits.'))
body=body.replace('The historical product rows illustrate the cost of changing the output contract; compressed and materialized outputs are separate computations.', 'The historical product rows illustrate the cost of changing the output contract; compressed and materialized outputs are separate computations. The GPU materialized BDLR rows at dimensions 512 and 1024 are sums of separately measured factor and expansion medians, as the raw notes state; they are not complete-workflow timing medians.')
changes.append(dict(reason='Historical GPU materialization rows identify sums of separate medians, rather than a complete-workflow timing median.'))
unanchored_final=body

def register(t,part,source,section_prefix=''):
 counters={};position=0;out=[];last=None;proof_no=0
 envs='theorem|proposition|lemma|corollary|definition|example|standardfact|remark'
 pattern=re.compile(r'\\section\{([^{}]*)\}|\\subsection\{([^{}]*)\}|\\begin\{('+envs+r')\}(?:\[([^\]]*)\])?|\\begin\{proof\}(?:\[([^\]]*)\])?|\\end\{proof\}')
 for m in pattern.finditer(t):
  out.append(t[position:m.end()]);position=m.end()
  if m.group(1) or m.group(2):
   kind='section' if m.group(1) else 'subsection';i=sum(x['part']==part and x['kind']==kind for x in sections)+1
   lab=f'{part}:{kind}:{i:03}';out.append(r'\label{'+lab+'}')
   sections.append(dict(part=part,kind=kind,title=m.group(1) or m.group(2),label=lab,source=str(source.relative_to(SRC))))
  elif m.group(3):
   env=m.group(3);counters[env]=counters.get(env,0)+1;lab=f'{part}:{env}:{counters[env]:03}';last=lab
   original_labels=re.findall(r'\\label\{([^}]+)\}',t[m.end():m.end()+180])[:1]
   orig=list(re.finditer(r'\\begin\{'+env+r'\}',source.read_text()))[counters[env]-1]
   rec=dict(part=part,environment=env,title=m.group(4) or '',label=lab,original_labels=original_labels,source=str(source.relative_to(SRC)),source_line=source.read_text()[:orig.start()].count('\n')+1,proof_required=env in ['theorem','proposition','lemma','corollary'])
   records.append(rec);out.append(r'\label{'+lab+'}')
  elif m.group().startswith(r'\begin{proof}'):
   proof_no+=1;lab=f'{part}:proof:{proof_no:03}'
   out.append(r'\phantomsection\label{'+lab+'}')
   orig=list(re.finditer(r'\\begin\{proof\}',source.read_text()))[proof_no-1]
   proofs.append(dict(part=part,index=proof_no,label=lab,end_label=lab+':end',result_label=last,source=str(source.relative_to(SRC)),source_line=source.read_text()[:orig.start()].count('\n')+1))
  else:
   out[-1]=out[-1][:-len(r'\end{proof}')]+r'\phantomsection\label{'+f'{part}:proof:{proof_no:03}:end'+r'}\end{proof}'
 out.append(t[position:]);return ''.join(out)

body=register(body,'main',MAIN)
(ROOT/'parts/01_manuscript.tex').write_text(body)
for i,name in enumerate(['First','Second','Third','Fourth','Fifth','Sixth'],1):
 p=NOTES/f'Paper_VIII_{name}_Lean_Block_Supplement.tex';s=p.read_text()
 start=s.index(r'\pageheading{1.')
 # Retain every body paragraph, including historical audit/failure records. The
 # cover and release summary are the only omitted matter, separately preserved.
 t=s[start:s.index(r'\end{document}')]
 t=re.sub(r'\\(?:newpage|clearpage)\s*','\n\n',t)
 t=t.replace(r'\section*{\color{ink}',r'\subsubsection{')
 t=re.sub(r'\\pageheading\{([^{\n]+)\}\{([^\n]+)\}',lambda m:r'\subsection{'+re.sub(r'^\d+\.\s*','',m.group(1))+r'}\textit{'+m.group(2)+r'}\par',t)
 title=['Exact semantics, support, and low-rank identities','Exact compilation, continuous precision, and explicit costs','Product chains, Krylov spaces, and integer budgets','Structured transforms and clipped precision','Constructed graph schedules, support, and preconditioning','Global small-core recompression from ordered thin SVD data'][i-1]
 lead=r'\clearpage\FloatBarrier\section{'+title+'}'+'\n'
 lead+=r'This chapter retains the substantive mathematical pages of verification block '+str(i)+r' (v0.'+str(i)+r'.0). Its dated audit and pending-status passages describe that historical checkpoint; the final status is 56 of 56 registered finite items under the recorded hypotheses. Later chapters supersede earlier pending statements. All compiler and regression counts in this chapter are inherited records, not fresh runs for this edition.\par'+'\n\n'
 t=register(lead+t,f'supp{i}',p)
 fn=f'02_supplement_{i:02}.tex';(ROOT/'parts'/fn).write_text(t)
 supplements.append(dict(source=str(p.relative_to(SRC)),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),retained_line_range=[s[:start].count('\n')+1,s[:s.index(r'\end{document}')].count('\n')+1],final_source='parts/'+fn,prefix=f'supp{i}',full_substantive_body_retained=True))

with (ROOT/'references.bib').open('a') as f:
 f.write('''\n@misc{HighamMary2021,\n  author = {Higham, Nicholas J. and Mary, Theo},\n  title = {Mixed Precision Algorithms in Numerical Linear Algebra},\n  year = {2021},\n  note = {MIMS EPrint 2021.20, Sections 3--4; classical real dot-product forward-error model},\n  url = {https://eprints.maths.manchester.ac.uk/2841/1/paper_eprint.pdf}\n}\n''')
manifest=dict(source_manuscript=str(MAIN.relative_to(SRC)),source_sha256=hashlib.sha256(MAIN.read_bytes()).hexdigest(),result_records=records,proof_records=proofs,section_records=sections,supplement_crosswalk=supplements,corrections=changes,raw_source_modified=False)
(ROOT/'evidence/ASSEMBLY_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
ledger=['# Traditional edition correction and scope ledger','', 'The 45-page strengthened manuscript and all six substantive supplement bodies are retained. Raw recovered sources are unchanged.','', 'Source manuscript SHA-256: `'+manifest['source_sha256']+'`.','', '## Reasons for the final changes','', 'The list groups editorial purposes. The unified diff below compares the raw original body directly with the final body before navigation anchors, so its added lines are the actual final statements. Assembly steps retained in JSON are procedural records and can contain intermediate text.','']
for i,x in enumerate(changes,1):
 ledger.extend([f'{i}. {x["reason"]}'])
ledger.extend(['','## Exact original-to-final manuscript diff','','```diff'])
ledger.extend(difflib.unified_diff(raw[raw.index(r'\section{Introduction}'):raw.index(r'\bibliographystyle')].splitlines(),unanchored_final.splitlines(),fromfile='raw strengthened manuscript body',tofile='final traditional manuscript body',lineterm=''))
ledger.extend(['```','', 'Supplement bodies retain every substantive paragraph and display. Only cover/scope summaries and layout commands are omitted; dated pending/audit statements are retained with explicit historical-checkpoint prefaces. Bibliography updates pin the classical forward-error source and a stable official CUDA archive.'])
(ROOT/'evidence/CORRECTION_LEDGER.md').write_text('\n'.join(ledger)+'\n')
print(json.dumps(dict(records=len(records),proofs=len(proofs),supplements=len(supplements),changes=len(changes)),indent=2))
